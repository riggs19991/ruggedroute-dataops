"""
KWP2000 (ISO 14230-3) client over any payload link (TP 2.0 channel, ISO-TP link or a
test double with ``send()`` / ``recv(timeout)`` / ``flush_rx()`` / ``close()``).

Protocol behaviour, all from ``docs/PROTOCOL_FACTS.md`` §4 (verified):

* a request is ``SID [params]`` with no framing; the positive answer starts with
  ``SID + 0x40``; a negative answer is ``7F <SID> <NRC>``;
* ``7F <SID> 78`` (responsePending) means *keep waiting, do not resend*; the wait
  becomes P2* and tester-present is not sent meanwhile (ISO 5.3.1.4.1);
* ``7F <SID> 21`` (busy-RepeatRequest) and ``7F <SID> 23`` (routineNotComplete) mean
  *resend the same request after a short delay*, bounded by ``retry_on_busy``;
* ``10 89`` opens the VAG standard diagnostic session and may be repeated; ``20``
  stops it; a bare ``3E`` is answered by ``7E``;
* ``1A <option>`` echoes the option; ``21 <group>`` echoes the group; ``18 02 FF 00``
  (fallback ``18 00 FF 00``) answers ``58 n`` + n x ``DTC_hi DTC_lo status``;
  ``14 FF 00`` answers ``54 FF 00``; ``23 addr(3) size`` answers ``63 data`` with no
  byte between the SID and the data (size 1..254).

The generic routine (``31``/``32``/``33``), ``3B`` and ``30`` framings are plain ISO
14230-3 services. Which local identifiers VAG tools use for coding, adaptation,
basic settings and output tests is *not* verified; those uses live in
:mod:`vagtune.vag.kwp_recipes` as documented byte models, never as functions here.

Matching replies to requests: a positive response is matched on ``SID + 0x40`` *and*,
for the services whose reply echoes the request parameter (``1A <option>``, ``21
<lid>``, ``10 <kind>``, ``31/32/33 <lid>``, ``3B``/``30 <lid>``), on that echoed
parameter, so a late ``61 02`` from a timed-out ``21 02`` is skipped while ``21 01``
waits for its ``61 01``. A negative response (``7F SID NRC``) carries no parameter
echo, so one that arrives during the wait is attributed to the current request -
nothing on the wire distinguishes a stale ``7F 21 31`` from a fresh one.

Keepalive: :meth:`KwpClient.start_tester_present` runs a daemon thread that sends a
bare ``3E`` every ``interval`` and shares the send lock with foreground traffic; its
wait is interruptible (``recv`` is polled in short slices while a halt flag is
clear), so :meth:`stop_tester_present` / :meth:`close` return with the thread gone and
the lock free even when the module has fallen silent.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..transport.base import TransportError, TransportTimeout
from . import services as S
from .exceptions import KwpError, KwpNegativeResponse, KwpTimeout, UnexpectedKwpResponse

log = logging.getLogger(__name__)


@dataclass
class KwpTiming:
    """Timeouts in seconds.

    ``p2`` is the normal response window (PyVCDS and scirocco-dash wait 1 s per
    request; PQ35 modules answer within ~10 ms); ``p2_star`` the window after a
    ``7F xx 78``; ``pending_limit`` bounds consecutive pending replies;
    ``retry_on_busy`` / ``busy_delay`` bound the resend loop for 0x21 / 0x23 (the
    project-wide policy is 200 ms, up to 5 times).
    """
    p2: float = 1.0
    p2_star: float = 5.0
    pending_limit: int = 30
    retry_on_busy: int = 5
    busy_delay: float = 0.2


class KwpClient:
    """One KWP2000 conversation with one module."""

    def __init__(self, link, timing: Optional[KwpTiming] = None) -> None:
        self.link = link
        self.timing = timing or KwpTiming()
        self._send_lock = threading.RLock()
        self._tp_thread: Optional[_TesterPresentThread] = None
        self.session: Optional[int] = None
        #: every (request, response) pair, newest last; ``raw()`` users read it back
        self.last_exchange: Optional[Tuple[bytes, bytes]] = None

    # ================================================================= core I/O

    def request(self, payload: bytes, *, timeout: Optional[float] = None,
                expect_response: bool = True, echo: Optional[bytes] = None,
                halt: Optional[threading.Event] = None) -> bytes:
        """Send ``payload`` and return the matching positive response (SID included).

        Handles the pending (0x78: wait) and busy (0x21 / 0x23: resend after
        ``busy_delay``) codes; any other NRC raises :class:`KwpNegativeResponse`.
        Replies for a different SID are logged and skipped (a late answer to an
        earlier request); with ``echo`` (the parameter bytes the positive reply must
        carry right after its SID, e.g. the group of ``21 <group>``) positive replies
        echoing something else are skipped too, and if nothing matching arrives in
        time the mismatched reply is reported as :class:`UnexpectedKwpResponse`
        instead of a bare timeout. ``halt`` (an Event) aborts the wait early with
        :class:`KwpTimeout`; the keepalive thread passes its own. ``expect_response=
        False`` returns ``b""`` right after sending (nothing in VAG's dialect needs
        it, but ``raw()`` callers may).
        """
        payload = bytes(payload)
        if not payload:
            raise ValueError("a KWP request needs at least the SID byte")
        sid = payload[0]
        echo = bytes(echo) if echo is not None else None
        busy_left = self.timing.retry_on_busy
        with self._send_lock:
            while True:
                if halt is not None and halt.is_set():
                    raise KwpTimeout(f"{S.service_name(sid)} aborted: halted before sending")
                self.link.flush_rx()
                self.link.send(payload)
                if not expect_response:
                    self.last_exchange = (payload, b"")
                    return b""
                try:
                    response = self._await_response(sid, timeout, echo=echo, halt=halt)
                except _Resend as again:
                    if busy_left <= 0:
                        raise KwpNegativeResponse(sid, again.nrc)
                    busy_left -= 1
                    log.debug("KWP 0x%02X: %s, resending in %.0f ms (%d left)", sid,
                              S.nrc_name(again.nrc), self.timing.busy_delay * 1000, busy_left)
                    time.sleep(self.timing.busy_delay)
                    continue
                self.last_exchange = (payload, response)
                return response

    def raw(self, payload: bytes, *, timeout: Optional[float] = None,
            raise_negative: bool = False) -> bytes:
        """Send arbitrary bytes and return the raw reply, negative responses included.

        Pending (0x78) and busy (0x21 / 0x23) replies are still handled (waited out /
        resent) so the caller sees the module's *final* answer; with
        ``raise_negative=False`` a final ``7F ..`` comes back as bytes instead of
        raising. This is the ``kwp raw --yes`` backend for the experiments in
        :mod:`vagtune.vag.kwp_recipes`.
        """
        try:
            return self.request(payload, timeout=timeout)
        except KwpNegativeResponse as exc:
            if raise_negative:
                raise
            reply = bytes([S.NEGATIVE_RESPONSE_SID, exc.sid, exc.nrc])
            self.last_exchange = (bytes(payload), reply)
            return reply

    #: longest single ``link.recv()`` call while a halt flag is being watched; the
    #: keepalive thread can therefore be stopped within this much plus the link's own
    #: reaction time, whatever P2/P2* say.
    HALT_POLL_SLICE = 0.05

    def _await_response(self, sid: int, timeout: Optional[float], *, echo: Optional[bytes] = None,
                        halt: Optional[threading.Event] = None) -> bytes:
        window = self.timing.p2 if timeout is None else timeout
        deadline = time.monotonic() + window
        pending = 0
        want = S.positive_sid(sid)
        mismatched: Optional[bytes] = None
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                if mismatched is not None:
                    raise UnexpectedKwpResponse(
                        f"{S.service_name(sid)} (0x{sid:02X}) echo mismatch: expected {echo.hex(' ')} "
                        f"after 0x{want:02X}, got {mismatched[:4].hex(' ')} and nothing else within {window:.1f} s")
                raise KwpTimeout(f"no response to {S.service_name(sid)} (0x{sid:02X}) within {window:.1f} s")
            if halt is not None:
                if halt.is_set():
                    raise KwpTimeout(f"{S.service_name(sid)} (0x{sid:02X}) wait aborted: keepalive halted")
                remaining = min(remaining, self.HALT_POLL_SLICE)
            try:
                data = self.link.recv(remaining)
            except TransportTimeout as exc:
                raise KwpTimeout(str(exc)) from exc
            if not data:
                if halt is not None:
                    continue            # a polling slice elapsed; the deadline decides above
                if mismatched is not None:
                    raise UnexpectedKwpResponse(
                        f"{S.service_name(sid)} (0x{sid:02X}) echo mismatch: expected {echo.hex(' ')} "
                        f"after 0x{want:02X}, got {mismatched[:4].hex(' ')} and nothing else within {window:.1f} s")
                raise KwpTimeout(f"no response to {S.service_name(sid)} (0x{sid:02X}) within {window:.1f} s")
            data = bytes(data)
            if data[0] == S.NEGATIVE_RESPONSE_SID:
                if len(data) < 3:
                    raise UnexpectedKwpResponse(f"malformed negative response {data.hex(' ')}")
                echoed, nrc = data[1], data[2]
                if echoed != sid:
                    log.debug("KWP: ignoring negative response for another service (%s)", data.hex(" "))
                    continue
                if nrc in S.NRC_WAIT:
                    pending += 1
                    if pending > self.timing.pending_limit:
                        raise KwpTimeout(f"{S.service_name(sid)} exceeded {self.timing.pending_limit} "
                                         "responsePending replies")
                    window = self.timing.p2_star
                    deadline = time.monotonic() + window
                    continue
                if nrc in S.NRC_RESEND:
                    raise _Resend(nrc)
                # A 7F carries no parameter echo: it is taken as the answer to this request.
                raise KwpNegativeResponse(sid, nrc)
            if data[0] == want:
                if echo is not None and data[1:1 + len(echo)] != echo:
                    log.debug("KWP: skipping 0x%02X reply echoing %s while waiting for %s (late answer "
                              "to an earlier request?)", want, data[1:1 + len(echo)].hex(" "), echo.hex(" "))
                    mismatched = data
                    continue
                return data
            log.debug("KWP: ignoring stray response %s while waiting for 0x%02X", data.hex(" "), want)

    # ================================================================= sessions

    def start_diagnostic_session(self, kind: int = S.SESSION_STANDARD_DIAGNOSTIC) -> bytes:
        """``10 <kind>`` -> ``50 <kind>``. ``0x89`` is the VAG standard diagnostic
        session (verified); repeating it is harmless. Returns the bytes after ``50``."""
        resp = self.request(bytes([S.Service.START_DIAGNOSTIC_SESSION, kind & 0xFF]), echo=bytes([kind & 0xFF]))
        if len(resp) < 2 or resp[1] != (kind & 0xFF):
            raise UnexpectedKwpResponse(f"startDiagnosticSession echo mismatch: {resp.hex(' ')}")
        self.session = kind & 0xFF
        return resp[2:]

    def stop_diagnostic_session(self) -> None:
        """``20`` -> ``60``; the default session stays active (ISO 6.2)."""
        self.request(bytes([S.Service.STOP_DIAGNOSTIC_SESSION]))
        self.session = None

    def tester_present(self, *, halt: Optional[threading.Event] = None) -> None:
        """Bare ``3E`` -> ``7E`` (VAG tools send no responseRequired byte). ``halt``
        makes the wait interruptible (used by the keepalive thread)."""
        resp = self.request(bytes([S.Service.TESTER_PRESENT]), halt=halt)
        if resp[0] != S.positive_sid(S.Service.TESTER_PRESENT):
            raise UnexpectedKwpResponse(f"testerPresent answered {resp.hex(' ')}")

    def stop_communication(self) -> None:
        """``82`` -> ``C2`` (pq-flasher / bri3d "log off"); not needed over TP 2.0,
        where ``A8`` closes the channel, but harmless."""
        self.request(bytes([S.Service.STOP_COMMUNICATION]))

    # ================================================================= reads

    def read_ecu_identification(self, option: int) -> bytes:
        """``1A <option>`` -> ``5A <option> <record...>``; returns the record bytes
        after the echoed option (a ``5A`` echoing another option is a late reply and
        is skipped). An unknown option is answered ``7F 1A 11`` by VAG modules, which
        surfaces as :class:`KwpNegativeResponse`."""
        resp = self.request(bytes([S.Service.READ_ECU_IDENTIFICATION, option & 0xFF]), echo=bytes([option & 0xFF]))
        if len(resp) < 2 or resp[1] != (option & 0xFF):
            raise UnexpectedKwpResponse(
                f"readEcuIdentification 0x{option:02X} echo mismatch: {resp[:4].hex(' ')}")
        return resp[2:]

    def read_data_by_local_id(self, lid: int) -> bytes:
        """``21 <lid>`` -> ``61 <lid> <record>``; returns the record (the measuring
        block fields for a VAG group number). A ``61`` echoing another group (the late
        answer of a timed-out poll) is skipped. ``7F 21 11`` / ``7F 21 31`` = no such
        group."""
        resp = self.request(bytes([S.Service.READ_DATA_BY_LOCAL_ID, lid & 0xFF]), echo=bytes([lid & 0xFF]))
        if len(resp) < 2 or resp[1] != (lid & 0xFF):
            raise UnexpectedKwpResponse(f"readDataByLocalIdentifier 0x{lid:02X} echo mismatch: {resp[:4].hex(' ')}")
        return resp[2:]

    def read_dtc_by_status(self, group: int = S.DTC_GROUP_ALL, status: int = S.DTC_STATUS_VAG, *,
                           fallback: bool = True, timeout: Optional[float] = None) -> List[Tuple[int, int]]:
        """``18 <status> <group16>`` -> ``58 n`` + n x ``DTC_hi DTC_lo status``.

        VAG tools send status 0x02 first and fall back to 0x00 when the module refuses
        the status value (``fallback=True`` does the same on NRC 0x12 / 0x31 / 0x22).
        Returns ``[(dtc16, status), ...]``; the 16-bit value *is* the VCDS 5-digit
        number (decimal rule for 0x4000..0x7FFF; see :mod:`vagtune.vag.kwp_session`).
        """
        payload = bytes([S.Service.READ_DTC_BY_STATUS, status & 0xFF, (group >> 8) & 0xFF, group & 0xFF])
        try:
            resp = self.request(payload, timeout=timeout if timeout is not None else max(self.timing.p2, 1.5))
        except KwpNegativeResponse as exc:
            if fallback and status != S.DTC_STATUS_ALL and exc.nrc in (
                    S.NRC_SUBFUNCTION_NOT_SUPPORTED, S.NRC_REQUEST_OUT_OF_RANGE, S.NRC_CONDITIONS_NOT_CORRECT):
                log.info("readDTCByStatus 0x%02X refused (%s); falling back to status 0x00", status, exc.nrc_name)
                return self.read_dtc_by_status(group, S.DTC_STATUS_ALL, fallback=False, timeout=timeout)
            raise
        return parse_dtc_list(resp)

    def read_memory_by_address(self, address: int, length: int, *, addr_bytes: int = 3) -> bytes:
        """``23 <addr(addr_bytes)> <size>`` -> ``63 <data>``; no byte between ``63``
        and the data (me7-logger, kw1281-can-extension; bri3d's skip is a bug).
        ``length`` 1..254 (ISO / me7-logger limit). Read-only probe."""
        if not 1 <= length <= 254:
            raise ValueError("readMemoryByAddress length must be 1..254")
        if addr_bytes not in (2, 3, 4):
            raise ValueError("addr_bytes must be 2, 3 or 4")
        if address < 0 or address >= (1 << (8 * addr_bytes)):
            raise ValueError(f"address 0x{address:X} does not fit in {addr_bytes} bytes")
        payload = bytes([S.Service.READ_MEMORY_BY_ADDRESS]) + address.to_bytes(addr_bytes, "big") + bytes([length])
        resp = self.request(payload)
        if len(resp) < 1 + length:
            raise UnexpectedKwpResponse(f"readMemoryByAddress returned {len(resp) - 1} of {length} bytes")
        return resp[1:1 + length]

    # ================================================================= routines / writes

    def start_routine_by_local_id(self, lid: int, data: bytes = b"") -> bytes:
        """``31 <lid> [params]`` -> ``71 <lid> [results]``; returns the results."""
        return self._routine(S.Service.START_ROUTINE_BY_LOCAL_ID, lid, data)

    def stop_routine_by_local_id(self, lid: int, data: bytes = b"") -> bytes:
        """``32 <lid> [params]`` -> ``72 <lid> [results]``."""
        return self._routine(S.Service.STOP_ROUTINE_BY_LOCAL_ID, lid, data)

    def request_routine_results_by_local_id(self, lid: int, data: bytes = b"") -> bytes:
        """``33 <lid> [params]`` -> ``73 <lid> [results]``."""
        return self._routine(S.Service.REQUEST_ROUTINE_RESULTS_BY_LOCAL_ID, lid, data)

    def _routine(self, sid: int, lid: int, data: bytes) -> bytes:
        resp = self.request(bytes([sid, lid & 0xFF]) + bytes(data), echo=bytes([lid & 0xFF]))
        if len(resp) < 2 or resp[1] != (lid & 0xFF):
            raise UnexpectedKwpResponse(f"{S.service_name(sid)} 0x{lid:02X} echo mismatch: {resp[:4].hex(' ')}")
        return resp[2:]

    def write_data_by_local_id(self, lid: int, data: bytes) -> bytes:
        """``3B <lid> <data>`` -> ``7B <lid> [...]`` (generic ISO framing). This
        *writes* to the module; which local ids VAG modules accept is unverified, so
        the VAG layer never calls it on its own - only ``kwp raw --yes`` style
        deliberate experiments do."""
        log.warning("KWP writeDataByLocalIdentifier 0x%02X (%d bytes) - a write to the module", lid, len(data))
        resp = self.request(bytes([S.Service.WRITE_DATA_BY_LOCAL_ID, lid & 0xFF]) + bytes(data),
                            echo=bytes([lid & 0xFF]))
        if len(resp) < 2 or resp[1] != (lid & 0xFF):
            raise UnexpectedKwpResponse(f"writeDataByLocalIdentifier 0x{lid:02X} echo mismatch")
        return resp[2:]

    def io_control_by_local_id(self, lid: int, data: bytes) -> bytes:
        """``30 <lid> <controlParameter...>`` -> ``70 <lid> [...]`` (generic ISO
        framing; drives an output, so treated like a write)."""
        log.warning("KWP inputOutputControlByLocalIdentifier 0x%02X %s - drives an output", lid, bytes(data).hex(" "))
        resp = self.request(bytes([S.Service.IO_CONTROL_BY_LOCAL_ID, lid & 0xFF]) + bytes(data),
                            echo=bytes([lid & 0xFF]))
        if len(resp) < 2 or resp[1] != (lid & 0xFF):
            raise UnexpectedKwpResponse(f"inputOutputControlByLocalIdentifier 0x{lid:02X} echo mismatch")
        return resp[2:]

    def clear_diagnostic_information(self, group: int = S.CLEAR_GROUP_ALL, *,
                                     timeout: Optional[float] = None) -> None:
        """``14 FF 00`` -> ``54 FF 00`` (the group bytes are echoed; verified). A bare
        ``54`` is accepted too (scirocco-dash does; the module has cleared its memory
        by then), a ``54`` echoing another group is not. Clears the fault memory,
        freeze frames and readiness. 3 s window by default (scirocco-dash)."""
        payload = bytes([S.Service.CLEAR_DIAGNOSTIC_INFORMATION, (group >> 8) & 0xFF, group & 0xFF])
        resp = self.request(payload, timeout=timeout if timeout is not None else max(self.timing.p2, 3.0))
        if len(resp) == 1:
            log.info("clearDiagnosticInformation answered with a bare 54 (no group echo)")
            return
        if resp[1:3] != payload[1:3]:
            raise UnexpectedKwpResponse(f"clearDiagnosticInformation echo mismatch: {resp.hex(' ')}")

    # ================================================================= keepalive

    def start_tester_present(self, interval: float = 1.0) -> None:
        """Send a bare ``3E`` every ``interval`` seconds from a daemon thread that
        shares the send lock with foreground requests (PyVCDS sends one every 1 s;
        whether the 0x89 session needs it next to TP 2.0 ``A3`` keepalives is an
        open question, so this is opt-in). A running keepalive is stopped first;
        there is never more than one thread per client."""
        self.stop_tester_present()
        if self._tp_thread is not None:      # still alive after the join: never spawn a second one
            raise KwpError("the previous tester-present thread has not stopped yet")
        self._tp_thread = _TesterPresentThread(self, interval)
        self._tp_thread.start()

    def keepalive_stop_timeout(self) -> float:
        """How long :meth:`stop_tester_present` waits for the thread: it is
        interruptible within :data:`HALT_POLL_SLICE`, so this is that slice plus one
        busy resend delay and a margin - independent of P2 / P2*."""
        return self.HALT_POLL_SLICE * 4 + self.timing.busy_delay + 0.5

    def stop_tester_present(self) -> None:
        """Halt the keepalive thread and join it. The thread's wait is polled in
        :data:`HALT_POLL_SLICE` steps, so it leaves ``request()`` (and releases the
        send lock) promptly even while the module is silent. Should the join still
        time out (a link whose ``recv`` ignores its timeout), the thread stays
        referenced - ``tester_present_running`` keeps reporting True and the next
        ``start_tester_present`` refuses to spawn a duplicate - and a warning is
        logged."""
        t = self._tp_thread
        if t is None:
            return
        t.halt()
        t.join(timeout=self.keepalive_stop_timeout())
        if t.is_alive():
            log.warning("KWP tester-present thread did not stop within %.1f s; the link's recv() ignores "
                        "its timeout - keeping the reference, no second thread will be started",
                        self.keepalive_stop_timeout())
            return
        self._tp_thread = None

    @property
    def tester_present_running(self) -> bool:
        t = self._tp_thread
        return t is not None and t.is_alive()

    def close(self) -> None:
        """Stop the keepalive (waiting for its thread) and close the link."""
        self.stop_tester_present()
        if self._tp_thread is not None:
            log.warning("closing the link underneath a tester-present thread that has not stopped")
        self.link.close()

    def __enter__(self) -> "KwpClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def parse_dtc_list(resp: bytes) -> List[Tuple[int, int]]:
    """``58 n`` + n x 3 bytes -> ``[(dtc16, status), ...]`` (verified layout: DV
    emulator, scirocco-dash, bri3d; PyVCDS's 2-byte stepping is wrong)."""
    if len(resp) < 2 or resp[0] != S.positive_sid(S.Service.READ_DTC_BY_STATUS):
        raise UnexpectedKwpResponse(f"not a readDTCByStatus reply: {resp[:4].hex(' ')}")
    count = resp[1]
    body = resp[2:]
    if len(body) < 3 * count:
        raise UnexpectedKwpResponse(f"readDTCByStatus announced {count} records but carried {len(body)} bytes")
    if len(body) > 3 * count:
        log.debug("readDTCByStatus reply carries %d trailing bytes after %d records", len(body) - 3 * count, count)
    return [((body[i] << 8) | body[i + 1], body[i + 2]) for i in range(0, 3 * count, 3)]


class _Resend(Exception):
    def __init__(self, nrc: int) -> None:
        super().__init__(f"resend (NRC 0x{nrc:02X})")
        self.nrc = nrc


class _TesterPresentThread(threading.Thread):
    def __init__(self, client: KwpClient, interval: float) -> None:
        super().__init__(name="kwp-tester-present", daemon=True)
        self.client = client
        self.interval = interval
        # Never name this `_stop`: threading.Thread uses that name internally.
        self._halt_event = threading.Event()
        self.sent = 0
        self.errors = 0

    def run(self) -> None:
        while not self._halt_event.wait(self.interval):
            try:
                self.client.tester_present(halt=self._halt_event)
                self.sent += 1
            except (KwpTimeout, TransportError, KwpNegativeResponse, UnexpectedKwpResponse) as exc:
                self.errors += 1
                log.debug("KWP tester-present keepalive failed: %s", exc)
            except Exception as exc:  # pragma: no cover - a keepalive must never kill the app
                self.errors += 1
                log.debug("KWP tester-present keepalive error: %s", exc)

    def halt(self) -> None:
        self._halt_event.set()


__all__ = ["KwpClient", "KwpTiming", "parse_dtc_list"]
