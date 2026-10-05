"""
CAN frame router: one physical bus, many logical links.

Problem solved here: ISO-TP links, TP 2.0 channels, an OBD functional link and the
tester-present keepalive all need to *read* from the same CAN interface at the same
time. A link that calls ``transport.recv()`` directly steals frames meant for another
link. The :class:`CanRouter` owns the hardware transport, runs a single reader thread,
and fans every received frame out to each :class:`RouterEndpoint` whose predicate
matches. Endpoints look exactly like a :class:`~vagtune.transport.base.RawCanTransport`,
so ``SoftwareIsoTpLink(router.endpoint([rx_id]), tx_id, rx_id)`` works unchanged.

Behaviour:

* The reader thread is a daemon, started lazily by the first :meth:`CanRouter.endpoint`
  call and stopped by :meth:`CanRouter.close` (which also closes the transport).
* It polls ``transport.recv(poll_interval)`` (50 ms by default) so ``close()`` can stop
  it promptly without any transport-specific cancellation support.
* A frame may be delivered to several endpoints (a sniffer with ``accept=None`` sees
  everything). A frame that matches no endpoint increments ``stats["dropped_unmatched"]``.
* Endpoint queues are bounded. On overflow the *oldest* frame is dropped, the endpoint's
  ``dropped`` counter and ``stats["dropped_overflow"]`` increment, and the event is
  logged at debug level.
* ``send`` is serialised with a lock so the keepalive thread and foreground requests
  never interleave writes to the driver.
* The endpoint list may change while the reader runs: mutations happen under a lock and
  the reader iterates over a snapshot (copy-on-iterate).
* Closing an endpoint (or the router, or the :class:`~vagtune.transport.context.TransportContext`
  above it) wakes every thread blocked in that endpoint's ``recv()`` immediately with
  :class:`~vagtune.transport.base.TransportNotOpen`; a sniffer or a client waiting out
  P2* never sleeps on past the shutdown.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Callable, Deque, Dict, FrozenSet, Iterable, List, Optional, Sequence, Union

from .base import CanFrame, RawCanTransport, TransportError, TransportNotOpen

log = logging.getLogger(__name__)

AcceptSpec = Union[Iterable[int], Callable[[CanFrame], bool], None]


class CanRouter:
    """Owns one :class:`RawCanTransport` and multiplexes it to many endpoints.

    The transport is opened in the constructor if it is not already open (the router
    owns its lifecycle from here on; :meth:`close` closes it).
    """

    def __init__(self, transport: RawCanTransport, *, name: str = "",
                 poll_interval: float = 0.05) -> None:
        self._transport = transport
        self.name = name or type(transport).__name__
        self.poll_interval = poll_interval
        self._lock = threading.Lock()           # guards _endpoints / _closed / _thread
        self._send_lock = threading.Lock()      # serialises transport.send()
        self._endpoints: List["RouterEndpoint"] = []
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._closed = False
        self.stats: Dict[str, int] = {
            "rx_frames": 0,
            "tx_frames": 0,
            "dropped_unmatched": 0,
            "dropped_overflow": 0,
        }
        self.last_error: Optional[BaseException] = None
        if not self._transport.is_open:
            self._transport.open()

    # -- properties ----------------------------------------------------------------

    @property
    def transport(self) -> RawCanTransport:
        return self._transport

    @property
    def is_closed(self) -> bool:
        return self._closed

    @property
    def reader_alive(self) -> bool:
        t = self._thread
        return t is not None and t.is_alive()

    @property
    def endpoints(self) -> List["RouterEndpoint"]:
        with self._lock:
            return list(self._endpoints)

    # -- endpoints -----------------------------------------------------------------

    def endpoint(self, accept: AcceptSpec = None, *, name: str = "",
                 queue_size: int = 4096) -> "RouterEndpoint":
        """Subscribe a new endpoint and (lazily) start the reader thread.

        ``accept``:
            ``None``                 -> every frame (monitor / sniffer)
            iterable of ints         -> frames whose ``arbitration_id`` is in the set
            ``callable(frame)->bool``-> arbitrary predicate (runs on the reader thread;
                                        keep it cheap and exception-free)
        """
        with self._lock:
            if self._closed:
                raise TransportNotOpen(f"router {self.name} is closed")
            ep = RouterEndpoint(self, accept, name=name or f"ep{len(self._endpoints)}",
                                queue_size=queue_size)
            self._endpoints.append(ep)
            self._ensure_reader_locked()
        log.debug("router %s: endpoint %s subscribed (%s)", self.name, ep.name, ep.describe_accept())
        return ep

    def _unsubscribe(self, ep: "RouterEndpoint") -> None:
        with self._lock:
            try:
                self._endpoints.remove(ep)
            except ValueError:
                return
        log.debug("router %s: endpoint %s unsubscribed", self.name, ep.name)

    def _ensure_reader_locked(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._reader_loop,
                                        name=f"can-router-{self.name}", daemon=True)
        self._thread.start()

    # -- reader thread -------------------------------------------------------------

    def _reader_loop(self) -> None:
        log.debug("router %s: reader thread started", self.name)
        backoff = 0.0
        while not self._stop_event.is_set():
            try:
                frame = self._transport.recv(self.poll_interval)
            except TransportNotOpen:
                if not self._stop_event.is_set():
                    log.warning("router %s: transport closed underneath the reader", self.name)
                break
            except Exception as exc:  # a daemon reader must never die silently
                if self._stop_event.is_set():
                    break
                self.last_error = exc
                backoff = min(1.0, backoff + 0.05)
                log.error("router %s: receive error (%s: %s); retrying in %.2fs",
                          self.name, type(exc).__name__, exc, backoff)
                time.sleep(backoff)
                continue
            backoff = 0.0
            if frame is None:
                continue
            self._dispatch(frame)
        log.debug("router %s: reader thread stopped", self.name)

    def _dispatch(self, frame: CanFrame) -> None:
        self.stats["rx_frames"] += 1
        with self._lock:
            targets = list(self._endpoints)
        matched = False
        for ep in targets:
            try:
                if ep._matches(frame):
                    matched = True
                    ep._deliver(frame)
            except Exception as exc:  # a bad predicate must not kill the bus for everyone
                log.error("router %s: endpoint %s predicate raised %s: %s",
                          self.name, ep.name, type(exc).__name__, exc)
        if not matched:
            self.stats["dropped_unmatched"] += 1

    # -- transmit ------------------------------------------------------------------

    def send(self, frame: CanFrame) -> None:
        if self._closed:
            raise TransportNotOpen(f"router {self.name} is closed")
        with self._send_lock:
            self._transport.send(frame)
            self.stats["tx_frames"] += 1

    def send_many(self, frames: Sequence[CanFrame]) -> None:
        if self._closed:
            raise TransportNotOpen(f"router {self.name} is closed")
        if not frames:
            return
        with self._send_lock:
            self._transport.send_many(frames)
            self.stats["tx_frames"] += len(frames)

    # -- lifecycle -----------------------------------------------------------------

    def close(self) -> None:
        """Stop the reader thread, detach every endpoint and close the transport. Idempotent."""
        with self._lock:
            if self._closed:
                return
            self._closed = True
            thread = self._thread
            endpoints = list(self._endpoints)
            self._endpoints.clear()
        self._stop_event.set()
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=max(1.0, self.poll_interval * 4))
            if thread.is_alive():
                log.warning("router %s: reader thread did not stop in time", self.name)
        for ep in endpoints:
            ep._mark_detached()
        try:
            self._transport.close()
        except TransportError as exc:
            log.debug("router %s: transport close reported %s", self.name, exc)

    def __enter__(self) -> "CanRouter":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"<CanRouter {self.name} endpoints={len(self.endpoints)} stats={self.stats}>"


class RouterEndpoint(RawCanTransport):
    """A :class:`RawCanTransport` view onto a :class:`CanRouter`.

    ``send()`` goes to the router (and thus the shared hardware); ``recv()`` reads this
    endpoint's own bounded queue; ``flush_rx()`` clears that queue; ``set_accept_ids()``
    replaces the accept set atomically; ``close()`` unsubscribes from the router. ``open()``
    is a no-op because the router owns the real transport.
    """

    def __init__(self, router: CanRouter, accept: AcceptSpec, *, name: str = "",
                 queue_size: int = 4096) -> None:
        super().__init__(bitrate=router.transport.bitrate)
        if queue_size < 1:
            raise ValueError("queue_size must be >= 1")
        self.router = router
        self.name = name
        self.queue_size = queue_size
        # A deque guarded by a Condition rather than queue.Queue: close() must be able
        # to wake a consumer blocked in recv(), which a plain Queue cannot do.
        self._cond = threading.Condition()
        self._frames: Deque[CanFrame] = deque()
        self._accept_ids: Optional[FrozenSet[int]] = None
        self._accept_fn: Optional[Callable[[CanFrame], bool]] = None
        self._set_accept(accept)
        self.dropped = 0            # frames this endpoint lost to overflow
        self.received = 0           # frames delivered to this endpoint
        self._open = True

    # -- predicate -----------------------------------------------------------------

    def _set_accept(self, accept: AcceptSpec) -> None:
        if accept is None:
            self._accept_ids, self._accept_fn = None, None
        elif callable(accept):
            self._accept_ids, self._accept_fn = None, accept
        else:
            self._accept_ids, self._accept_fn = frozenset(int(i) for i in accept), None

    def _matches(self, frame: CanFrame) -> bool:
        ids = self._accept_ids
        if ids is not None:
            return frame.arbitration_id in ids
        fn = self._accept_fn
        if fn is not None:
            return bool(fn(frame))
        return True

    def describe_accept(self) -> str:
        if self._accept_ids is not None:
            return "ids=" + ",".join(f"0x{i:X}" for i in sorted(self._accept_ids))
        if self._accept_fn is not None:
            return f"predicate={getattr(self._accept_fn, '__name__', repr(self._accept_fn))}"
        return "monitor"

    @property
    def accept_ids(self) -> Optional[FrozenSet[int]]:
        """The id set this endpoint accepts, or ``None`` for predicate/monitor endpoints."""
        return self._accept_ids

    def set_accept_ids(self, arbitration_ids: Iterable[int]) -> None:
        """Replace the accept set. Frames already queued are kept; the reader thread sees
        the new set on its next frame (attribute assignment is atomic)."""
        self._accept_fn = None
        self._accept_ids = frozenset(int(i) for i in arbitration_ids)

    # -- delivery (reader thread) --------------------------------------------------

    def _deliver(self, frame: CanFrame) -> None:
        with self._cond:
            if len(self._frames) >= self.queue_size:
                # Drop the oldest frame to make room.
                self._frames.popleft()
                self.dropped += 1
                self.router.stats["dropped_overflow"] += 1
                log.debug("router %s: endpoint %s overflow, dropped oldest (total %d)",
                          self.router.name, self.name, self.dropped)
            self._frames.append(frame)
            self.received += 1
            self._cond.notify()

    def _mark_detached(self) -> None:
        """Router-side close: mark closed and wake blocked receivers (queued frames stay
        readable so a consumer can drain what arrived before the shutdown)."""
        with self._cond:
            self._open = False
            self._cond.notify_all()

    # -- RawCanTransport API -------------------------------------------------------

    def open(self) -> None:
        """No-op: the router owns the real transport. Re-opening a closed endpoint is not
        supported; create a new one with ``router.endpoint()``."""
        if not self._open:
            raise TransportNotOpen(f"endpoint {self.name} was closed; create a new endpoint")

    def close(self) -> None:
        with self._cond:
            if not self._open:
                return
            self._open = False
            self._frames.clear()
            self._cond.notify_all()
        self.router._unsubscribe(self)

    def send(self, frame: CanFrame) -> None:
        if not self._open:
            raise TransportNotOpen(f"endpoint {self.name} is closed")
        self.router.send(frame)

    def send_many(self, frames: Sequence[CanFrame]) -> None:
        if not self._open:
            raise TransportNotOpen(f"endpoint {self.name} is closed")
        self.router.send_many(frames)

    def recv(self, timeout: float) -> Optional[CanFrame]:
        """Return the next queued frame or ``None`` once ``timeout`` seconds elapse.

        A closed endpoint still drains whatever was queued before it closed, then
        raises :class:`TransportNotOpen` so a link does not spin on a dead endpoint.
        Closing the endpoint (or its router) from another thread wakes a blocked
        call at once; it then raises instead of sleeping out its timeout.
        """
        with self._cond:
            if timeout > 0 and not self._frames and self._open:
                self._cond.wait_for(lambda: bool(self._frames) or not self._open, timeout=timeout)
            if self._frames:
                return self._frames.popleft()
            if not self._open:
                raise TransportNotOpen(f"endpoint {self.name} is closed")
            return None

    def flush_rx(self) -> None:
        with self._cond:
            self._frames.clear()

    @property
    def pending(self) -> int:
        return len(self._frames)

    def __repr__(self) -> str:
        return f"<RouterEndpoint {self.name} {self.describe_accept()} pending={self.pending}>"
