"""
Frame-level simulated vehicle.

Where :mod:`vagtune.transport.fake` short-circuits a UDS request straight into a
:class:`~vagtune.transport.fake.SimulatedEcu` (no framing at all), this module puts
real CAN frames on a shared in-memory bus. Every simulated module is a
:class:`SimulatedNode` with its own thread, its own :class:`FakeCanTransport` and -
for UDS modules - its own ECU-side :class:`~vagtune.transport.isotp.SoftwareIsoTpLink`.
That means the tester's ISO-TP segmentation, flow control, STmin/block-size handling,
functional (0x7DF) addressing and multi-module concurrency are exercised offline
exactly as they would be on a car, through the same :class:`~vagtune.transport.router.CanRouter`
the hardware transports use.

Components:

* :class:`FakeCanBus` - the fabric. ``attach()`` creates a transport; ``publish()``
  delivers a frame to every *other* attached transport (a real CAN controller does
  not receive its own transmissions).
* :class:`FakeCanTransport` - a :class:`~vagtune.transport.base.RawCanTransport`
  with an ``inbox`` queue tests can inspect.
* :class:`SimulatedNode` / :class:`UdsNode` - a module on the bus. ``UdsNode`` wraps
  any object with ``handle(bytes) -> bytes | None`` (normally a ``SimulatedEcu``)
  behind software ISO-TP: it listens on its physical request id and the functional id,
  sends Flow Control for multi-frame requests and segments multi-frame responses.
* :class:`SimulatedVehicle` - a bus plus a set of nodes built from a named preset.
  Other slices add nodes to a preset through :meth:`SimulatedVehicle.register_preset_hook`
  without editing this file.
* :func:`get_default_vehicle` / :func:`reset_default_vehicle` - the process-global
  vehicle the ``fake`` transport kind attaches to.
"""

from __future__ import annotations

import dataclasses
import logging
import queue
import threading
import time
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional

from .base import CanFrame, RawCanTransport, TransportError, TransportNotOpen
from .fake import SimulatedEcu
from .isotp import IsoTpConfig, SoftwareIsoTpLink

log = logging.getLogger(__name__)

FUNCTIONAL_ID = 0x7DF
DEFAULT_PRESET = "demo"


# =============================================================================== bus

class FakeCanBus:
    """In-memory CAN fabric: every published frame reaches every other transport.

    ``latency`` (seconds) is an optional per-frame delay applied before delivery, for
    timing tests; it blocks the *sender* for that long, which is what a slow bus does.
    """

    def __init__(self, *, latency: float = 0.0) -> None:
        self.latency = latency
        self._lock = threading.Lock()
        self._transports: List["FakeCanTransport"] = []
        self.frames_published = 0

    def attach(self, name: str = "") -> "FakeCanTransport":
        """Create, register and open a new transport on this bus."""
        transport = FakeCanTransport(self, name=name)
        transport.open()
        return transport

    def _register(self, transport: "FakeCanTransport") -> None:
        with self._lock:
            if transport not in self._transports:
                self._transports.append(transport)

    def detach(self, transport: "FakeCanTransport") -> None:
        with self._lock:
            try:
                self._transports.remove(transport)
            except ValueError:
                pass

    @property
    def transports(self) -> List["FakeCanTransport"]:
        with self._lock:
            return list(self._transports)

    def publish(self, sender: "FakeCanTransport", frame: CanFrame) -> None:
        """Deliver ``frame`` to every attached transport except ``sender``."""
        if self.latency > 0:
            time.sleep(self.latency)
        with self._lock:
            targets = [t for t in self._transports if t is not sender]
            self.frames_published += 1
        # Stamp the receive time, like a controller would.
        delivered = dataclasses.replace(frame, timestamp=time.monotonic())
        for target in targets:
            target._deliver(delivered)


class FakeCanTransport(RawCanTransport):
    """A :class:`RawCanTransport` attached to a :class:`FakeCanBus`.

    ``inbox`` is the receive queue; tests may inspect or pre-load it directly.
    """

    def __init__(self, bus: FakeCanBus, name: str = "", *, bitrate: int = 500_000) -> None:
        super().__init__(bitrate=bitrate)
        self.bus = bus
        self.name = name or f"fake{id(self) & 0xFFFF:04x}"
        self.inbox: "queue.Queue[CanFrame]" = queue.Queue()
        self.tx_count = 0
        self.rx_count = 0

    def open(self) -> None:
        if self._open:
            return
        self.bus._register(self)
        self._open = True

    def close(self) -> None:
        if not self._open:
            return
        self.bus.detach(self)
        self._open = False
        self.flush_rx()

    def send(self, frame: CanFrame) -> None:
        if not self._open:
            raise TransportNotOpen(f"fake transport {self.name} is not open")
        self.tx_count += 1
        self.bus.publish(self, frame)

    def recv(self, timeout: float) -> Optional[CanFrame]:
        if not self._open:
            raise TransportNotOpen(f"fake transport {self.name} is not open")
        try:
            if timeout <= 0:
                return self.inbox.get_nowait()
            return self.inbox.get(timeout=timeout)
        except queue.Empty:
            return None

    def flush_rx(self) -> None:
        while True:
            try:
                self.inbox.get_nowait()
            except queue.Empty:
                return

    def _deliver(self, frame: CanFrame) -> None:
        self.rx_count += 1
        self.inbox.put(frame)

    def __repr__(self) -> str:
        return f"<FakeCanTransport {self.name} open={self._open} pending={self.inbox.qsize()}>"


# ============================================================================= nodes

class SimulatedNode(ABC):
    """A module on the simulated bus, driven by its own daemon thread.

    Subclasses implement :meth:`run`, which must return promptly once
    :attr:`should_stop` becomes true (poll with short timeouts, never block forever).
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    @property
    def running(self) -> bool:
        t = self._thread
        return t is not None and t.is_alive()

    @property
    def should_stop(self) -> bool:
        return self._stop_event.is_set()

    def start(self) -> None:
        """Start (or restart) the node's thread; :meth:`on_starting` runs first so a
        node re-acquires the resources :meth:`on_stopped` released."""
        if self.running:
            return
        self._stop_event.clear()
        self.on_starting()
        self._thread = threading.Thread(target=self._run_guarded,
                                        name=f"sim-node-{self.name}", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Signal the thread and join it (bounded); then release resources."""
        self._stop_event.set()
        t = self._thread
        if t is not None and t is not threading.current_thread():
            t.join(timeout=2.0)
            if t.is_alive():
                log.warning("simulated node %s did not stop within 2 s", self.name)
        self._thread = None
        self.on_stopped()

    def _run_guarded(self) -> None:
        try:
            self.run()
        except Exception:  # pragma: no cover - a node must report, never vanish silently
            log.exception("simulated node %s crashed", self.name)

    @abstractmethod
    def run(self) -> None:
        """Service the bus until :attr:`should_stop`."""

    def on_starting(self) -> None:
        """Hook called in :meth:`start` before the thread exists (re-open transports here)."""
        return None

    def on_stopped(self) -> None:
        """Hook called after the thread has been joined (release transports here)."""
        return None

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name} running={self.running}>"


class UdsNode(SimulatedNode):
    """A UDS module: ``ecu.handle(request) -> response | None`` behind software ISO-TP.

    The ECU-side link is ``SoftwareIsoTpLink(rx=request_id, tx=response_id,
    extra_rx_ids=[functional_id])``, so:

    * multi-frame *requests* are acknowledged with Flow Control and reassembled,
    * multi-frame *responses* are segmented and paced by the tester's Flow Control,
    * requests sent to the functional id (0x7DF) are answered on ``response_id`` just
      like physical ones (a module cannot tell, and does not care, which id a UDS
      request arrived on).

    Robustness: a handler exception is logged and answered with NRC 0x10
    (generalReject) so the tester gets a well-formed negative response instead of a
    timeout; transport errors during a transfer (sequence error, N_Cr timeout) are
    logged and the node keeps serving. ``stop()`` joins promptly because the thread
    polls ``link.recv`` with a short timeout, and detaches the node's transport from
    the bus; ``start()`` re-attaches it, so a vehicle can be stopped and started
    any number of times (``with vehicle:`` twice, an "ECU reset" feature).
    """

    POLL_TIMEOUT = 0.05

    def __init__(self, bus: FakeCanBus, ecu, *, request_id: int, response_id: int,
                 functional_id: Optional[int] = FUNCTIONAL_ID, name: str = "",
                 isotp_config: Optional[IsoTpConfig] = None) -> None:
        super().__init__(name or f"uds-{request_id:03X}")
        if not hasattr(ecu, "handle"):
            raise TypeError("ecu must expose handle(bytes) -> bytes | None")
        self.bus = bus
        self.ecu = ecu
        self.request_id = request_id
        self.response_id = response_id
        self.functional_id = functional_id
        self.transport = bus.attach(self.name)
        extra = [functional_id] if functional_id is not None else []
        self.link = SoftwareIsoTpLink(self.transport, tx_id=response_id, rx_id=request_id,
                                      extra_rx_ids=extra, config=isotp_config)
        self.requests_served = 0
        self.handler_errors = 0

    def run(self) -> None:
        while not self.should_stop:
            try:
                request = self.link.recv(self.POLL_TIMEOUT)
            except TransportNotOpen:
                if not self.should_stop:
                    log.warning("node %s: transport closed underneath it; node is dead until "
                                "start() is called again", self.name)
                break
            except TransportError as exc:
                log.warning("node %s: inbound transfer failed: %s", self.name, exc)
                continue
            if request is None:
                continue
            response = self._handle(request)
            if response is None:
                continue
            try:
                self.link.send(response)
            except TransportError as exc:
                log.warning("node %s: could not send response (%s)", self.name, exc)

    def _handle(self, request: bytes) -> Optional[bytes]:
        self.requests_served += 1
        try:
            return self.ecu.handle(request)
        except Exception:
            self.handler_errors += 1
            log.exception("node %s: handler raised on request %s; answering generalReject",
                          self.name, request.hex(" "))
            return bytes([0x7F, request[0], 0x10]) if request else None

    def on_starting(self) -> None:
        # stop() closed (and detached) the transport; put it back on the bus with a
        # clean receive state so a restarted node answers the first request it sees.
        if not self.transport.is_open:
            self.transport.open()
        self.link.flush_rx()

    def on_stopped(self) -> None:
        self.transport.close()


# =========================================================================== vehicle

PresetHook = Callable[["SimulatedVehicle"], None]


def _preset_demo(vehicle: "SimulatedVehicle") -> None:
    """The 0.1.0 SIMOS18.1 engine plus a gateway and an ABS module.

    All three are ``SimulatedEcu`` instances: identical wire behaviour, different
    identification strings and fault memories so a bus-wide scan has something to
    tell apart. Part numbers are demo values, not a claim about any real car.
    """
    engine = SimulatedEcu()
    vehicle.add_node(UdsNode(vehicle.bus, engine, request_id=0x7E0, response_id=0x7E8,
                             name="engine"))

    gateway = SimulatedEcu()
    gateway.identifiers = {
        0xF190: engine.identifiers[0xF190],
        0xF187: b"7N0907530C",
        0xF189: b"0432",
        0xF191: b"7N0907530C",
        0xF197: b"J533 Gateway",
        0xF18C: b"00000000000000",
    }
    gateway.dtcs = []
    vehicle.add_node(UdsNode(vehicle.bus, gateway, request_id=0x710, response_id=0x77A,
                             name="gateway"))

    abs_module = SimulatedEcu()
    abs_module.identifiers = {
        0xF190: engine.identifiers[0xF190],
        0xF187: b"1K0907379AC",
        0xF189: b"0101",
        0xF191: b"1K0907379AC",
        0xF197: b"ESP MK60EC1",
    }
    abs_module.dtcs = [(b"\x40\x35\x00", 0x28)]   # C0035 (chassis), stored + confirmed
    vehicle.add_node(UdsNode(vehicle.bus, abs_module, request_id=0x713, response_id=0x77D,
                             name="abs"))


def _preset_populated_by_hooks(vehicle: "SimulatedVehicle") -> None:
    """Base builder for the car presets: nodes come from registered preset hooks
    (UDS, KWP/TP 2.0 and OBD slices), so the base adds nothing."""
    return None


class SimulatedVehicle:
    """A :class:`FakeCanBus` plus the nodes a named preset puts on it.

    ``PRESETS`` maps a preset name to its base builder; ``register_preset_hook`` lets
    other modules append nodes to a preset (or define a brand-new one) at import time.
    Hooks run after the base builder, in registration order, when the vehicle is
    constructed.
    """

    PRESETS: Dict[str, PresetHook] = {
        "demo": _preset_demo,
        "golf-tdi-2012": _preset_populated_by_hooks,
        "r32-2008": _preset_populated_by_hooks,
    }
    _PRESET_HOOKS: Dict[str, List[PresetHook]] = {}

    def __init__(self, preset: str = DEFAULT_PRESET) -> None:
        if preset not in self.PRESETS:
            raise KeyError(f"unknown vehicle preset {preset!r}; known: "
                           f"{', '.join(self.available_presets())}")
        self.preset = preset
        self.bus = FakeCanBus()
        self.nodes: List[SimulatedNode] = []
        self._started = False
        self._lock = threading.Lock()
        self.PRESETS[preset](self)
        for hook in list(self._PRESET_HOOKS.get(preset, ())):
            hook(self)

    # -- registry -------------------------------------------------------------------

    @classmethod
    def register_preset_hook(cls, preset: str, hook: PresetHook) -> None:
        """Append ``hook(vehicle)`` to ``preset``; creates the preset if it is new."""
        if not callable(hook):
            raise TypeError("hook must be callable")
        cls.PRESETS.setdefault(preset, _preset_populated_by_hooks)
        cls._PRESET_HOOKS.setdefault(preset, []).append(hook)

    @classmethod
    def available_presets(cls) -> List[str]:
        return sorted(cls.PRESETS)

    # -- nodes -------------------------------------------------------------------

    def add_node(self, node: SimulatedNode) -> None:
        with self._lock:
            if any(n.name == node.name for n in self.nodes):
                raise ValueError(f"vehicle {self.preset!r} already has a node named {node.name!r}")
            self.nodes.append(node)
            if self._started:
                node.start()

    def node(self, name: str) -> SimulatedNode:
        for n in self.nodes:
            if n.name == name:
                return n
        raise KeyError(f"no node named {name!r} in preset {self.preset!r}; "
                       f"have: {', '.join(n.name for n in self.nodes) or '(none)'}")

    def node_names(self) -> List[str]:
        return [n.name for n in self.nodes]

    # -- lifecycle ---------------------------------------------------------------

    @property
    def started(self) -> bool:
        return self._started

    def start(self) -> None:
        with self._lock:
            if self._started:
                return
            self._started = True
            for n in self.nodes:
                n.start()
        log.debug("simulated vehicle %r started with %d node(s)", self.preset, len(self.nodes))

    def stop(self) -> None:
        with self._lock:
            if not self._started:
                return
            self._started = False
            nodes = list(self.nodes)
        for n in nodes:
            n.stop()
        log.debug("simulated vehicle %r stopped", self.preset)

    def __enter__(self) -> "SimulatedVehicle":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.stop()

    def __repr__(self) -> str:
        return f"<SimulatedVehicle {self.preset} nodes={self.node_names()} started={self._started}>"


# ==================================================================== default vehicle

_default_lock = threading.Lock()
_default_vehicle: Optional[SimulatedVehicle] = None


def get_default_vehicle(preset: Optional[str] = None) -> SimulatedVehicle:
    """Return the process-global vehicle, building and starting it on first use.

    ``preset=None`` means "whatever is running" (or ``demo`` if nothing is). Asking
    for a different preset than the one running stops the old vehicle and builds the
    new one, so a CLI run with ``--vehicle`` always gets what it asked for.
    """
    global _default_vehicle
    with _default_lock:
        current = _default_vehicle
        if current is not None and preset is not None and current.preset != preset:
            current.stop()
            current = None
        if current is None:
            current = SimulatedVehicle(preset or DEFAULT_PRESET)
            _default_vehicle = current
        if not current.started:
            current.start()
        return current


def reset_default_vehicle() -> None:
    """Stop and forget the process-global vehicle (tests call this between cases)."""
    global _default_vehicle
    with _default_lock:
        current = _default_vehicle
        _default_vehicle = None
    if current is not None:
        current.stop()
