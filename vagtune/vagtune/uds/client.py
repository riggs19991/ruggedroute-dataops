"""
ISO 14229-1 UDS client.

Sits on top of an :class:`~vagtune.transport.base.IsoTpLink` and speaks UDS to one
ECU. It implements the services this toolkit actually needs:

    0x10 DiagnosticSessionControl     0x2E WriteDataByIdentifier
    0x11 ECUReset                     0x2F InputOutputControlByID
    0x14 ClearDiagnosticInformation   0x31 RoutineControl
    0x19 ReadDTCInformation (01/02/03/04/06/0A/14 and the record-list group)
    0x22 ReadDataByIdentifier (single and multi-DID)
    0x23 ReadMemoryByAddress          0x34/0x35/0x36/0x37 download / upload
    0x27 SecurityAccess               0x3E TesterPresent
    0x28 CommunicationControl         0x85 ControlDTCSetting
    0x2C DynamicallyDefineDataIdentifier

Design notes:

* Every request waits for a matching positive response, transparently looping on
  NRC 0x78 (requestCorrectlyReceived-ResponsePending), which VAG ECUs emit a lot
  during flash operations; NRC 0x21 (busyRepeatRequest) resends the request.
* A background tester-present thread can keep a non-default session alive; the
  send lock makes keepalive and foreground requests mutually exclusive on the link.
* ``security_access`` is algorithm-agnostic: you pass a callable seed->key. The
  VAG SA2 implementation (:mod:`vagtune.vag.sa2`) provides that callable.
* DTC snapshot / extended-data parsing never guesses sizes (see :mod:`vagtune.uds.dtc`).
* Multi-DID reads need a size oracle because the response carries no per-DID length;
  DIDs without a known size are read one at a time.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from ..transport.base import IsoTpLink, TransportTimeout
from . import services as S
from . import dtc as D
from .exceptions import (
    NRC_REQUEST_OUT_OF_RANGE,
    NRC_SERVICE_NOT_SUPPORTED,
    NegativeResponse,
    UdsTimeout,
    UnexpectedResponse,
)

log = logging.getLogger(__name__)

SeedKeyFn = Callable[[int, bytes], bytes]  # (level, seed_bytes) -> key_bytes
SizeOracle = Union[Mapping[int, int], Callable[[int], Optional[int]], None]
ProgressFn = Callable[[int, int], None]


@dataclass
class UdsTiming:
    p2_timeout: float = 2.0          # normal response window
    p2_star_timeout: float = 5.0     # extended window after an 0x78 pending
    pending_limit: int = 30          # max consecutive 0x78 before giving up
    retry_on_busy: int = 2           # retries on NRC 0x21 busyRepeatRequest
    # How long a *suppressed-positive* request listens for a negative response before
    # it is taken as accepted. ISO 14229-1 §7.5.3: the suppressPosRspMsgIndicationBit
    # suppresses only the positive response; a server that refuses the request still
    # sends ``7F <SID> <NRC>`` within P2. The ECU-announced P2 (from the 0x10 reply)
    # widens this window when it is larger.
    suppressed_nrc_window: float = 0.1


@dataclass
class SessionTiming:
    """P2/P2* the ECU announced in its 0x10 response (ISO 14229 2013+ form).

    ``50 <session> <P2_hi> <P2_lo> <P2*_hi> <P2*_lo>``: P2 is in ms, P2* in 10 ms units
    (verified: udsoncan decodes ``a/1000`` and ``b*10/1000`` seconds).
    """
    session: int
    p2_ms: Optional[int] = None
    p2_star_ms: Optional[int] = None
    raw: bytes = b""

    @classmethod
    def from_response(cls, resp: bytes) -> "SessionTiming":
        session = resp[1] if len(resp) > 1 else 0
        record = resp[2:]
        if len(record) >= 4:
            return cls(session, int.from_bytes(record[0:2], "big"),
                       int.from_bytes(record[2:4], "big") * 10, record)
        return cls(session, None, None, record)


@dataclass
class DynamicDidEntry:
    """One source for a dynamically defined DID: a memory range (``address``/``size``)
    or a slice of another DID (``source_did``/``position``/``size``; position is 1-based
    per ISO)."""
    size: int
    address: Optional[int] = None
    source_did: Optional[int] = None
    position: int = 1


class UdsClient:
    def __init__(
        self,
        link: IsoTpLink,
        timing: Optional[UdsTiming] = None,
    ) -> None:
        self.link = link
        self.timing = timing or UdsTiming()
        self._send_lock = threading.RLock()
        self._tp_thread: Optional[_TesterPresentThread] = None
        self.last_session_timing: Optional[SessionTiming] = None

    # ================================================================= core I/O

    def request(
        self,
        payload: bytes,
        *,
        expect_response: bool = True,
        suppress_positive: bool = False,
    ) -> bytes:
        """Send one UDS request and return the response data (without the SID echo
        stripped). Raises NegativeResponse / UdsTimeout on failure.

        ``expect_response=False`` / ``suppress_positive=True`` is for requests sent
        with the suppressPosRspMsgIndicationBit (tester-present, ``85 82``...). The
        ECU stays silent **only when it accepts** the request: a refusal is still
        answered with ``7F <SID> <NRC>`` (ISO 14229-1 §7.5.3), so the client listens
        for one :attr:`UdsTiming.suppressed_nrc_window` (or the ECU-announced P2 if
        longer) and raises :class:`NegativeResponse` if one arrives. Silence within
        that window returns ``b""``. Nothing is ever reported as accepted on the
        strength of not having looked.
        """
        sid = payload[0]
        busy_retries = self.timing.retry_on_busy

        with self._send_lock:
            while True:
                self.link.flush_rx()
                self.link.send(payload)
                if not expect_response or suppress_positive:
                    try:
                        self._await_suppressed_nrc(sid)
                    except _BusyRepeat:
                        if busy_retries <= 0:
                            raise NegativeResponse(sid, 0x21)
                        busy_retries -= 1
                        time.sleep(0.05)
                        continue
                    return b""

                try:
                    response = self._await_response(sid)
                except _BusyRepeat:
                    if busy_retries <= 0:
                        raise NegativeResponse(sid, 0x21)
                    busy_retries -= 1
                    time.sleep(0.05)
                    continue
                return response

    def _suppressed_window(self) -> float:
        """Listening window for a negative response to a suppressed request: the
        configured window, widened to the ECU's announced P2, capped at P2 timeout."""
        window = self.timing.suppressed_nrc_window
        if self.last_session_timing is not None and self.last_session_timing.p2_ms:
            window = max(window, self.last_session_timing.p2_ms / 1000.0)
        return min(window, self.timing.p2_timeout)

    def _await_suppressed_nrc(self, request_sid: int) -> None:
        """After a suppressed-positive request: raise if the ECU refuses it.

        Reads the link for :meth:`_suppressed_window`; a ``7F <sid> <nrc>`` raises
        :class:`NegativeResponse` (0x78 extends the wait to P2*, 0x21 asks the caller
        to resend), responses for other services are ignored, and a positive
        response (an ECU that ignores the suppress bit) is accepted silently.
        """
        deadline = time.monotonic() + self._suppressed_window()
        pending_count = 0
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return
            data = self.link.recv(remaining)
            if not data:
                return
            if data[0] == (request_sid + S.POSITIVE_RESPONSE_OFFSET):
                log.debug("ECU answered a suppressed 0x%02X positively (suppress bit ignored)",
                          request_sid)
                return
            if data[0] != S.NEGATIVE_RESPONSE_SID or len(data) < 3 or data[1] != request_sid:
                continue
            nrc = data[2]
            if nrc == 0x78:
                pending_count += 1
                if pending_count > self.timing.pending_limit:
                    raise UdsTimeout(
                        f"service 0x{request_sid:02X} exceeded {self.timing.pending_limit} "
                        f"response-pending replies")
                deadline = time.monotonic() + self.timing.p2_star_timeout
                continue
            if nrc == 0x21:
                raise _BusyRepeat()
            raise NegativeResponse(request_sid, nrc)

    def _await_response(self, request_sid: int) -> bytes:
        """Read frames until a final (non-pending) response for ``request_sid``."""
        pending_count = 0
        timeout = self.timing.p2_timeout
        deadline = time.monotonic() + timeout

        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise UdsTimeout(f"no response to service 0x{request_sid:02X} within {timeout:.1f}s")

            data = self.link.recv(remaining)
            if data is None or len(data) == 0:
                raise UdsTimeout(f"no response to service 0x{request_sid:02X}")

            resp_sid = data[0]

            # Negative response?
            if resp_sid == S.NEGATIVE_RESPONSE_SID:
                if len(data) < 3:
                    raise UnexpectedResponse("malformed negative response (too short)")
                echoed_sid, nrc = data[1], data[2]
                if echoed_sid != request_sid:
                    # Response for a different service; keep waiting.
                    continue
                if nrc == 0x78:  # response pending
                    pending_count += 1
                    if pending_count > self.timing.pending_limit:
                        raise UdsTimeout(
                            f"service 0x{request_sid:02X} exceeded {self.timing.pending_limit} "
                            f"response-pending replies"
                        )
                    timeout = self.timing.p2_star_timeout
                    deadline = time.monotonic() + timeout
                    continue
                if nrc == 0x21:  # busyRepeatRequest -> let caller retry the whole request
                    raise _BusyRepeat()
                raise NegativeResponse(request_sid, nrc)

            # Positive response must be request SID + 0x40.
            if resp_sid == (request_sid + S.POSITIVE_RESPONSE_OFFSET):
                return data

            # Some other positive response (stray) - ignore and keep waiting.

    # ============================================================ UDS services

    def diagnostic_session_control(self, session: int) -> bytes:
        """0x10. Returns the raw session parameter record (P2/P2*); the decoded form is
        kept in :attr:`last_session_timing`."""
        resp = self.request(bytes([S.Service.DIAGNOSTIC_SESSION_CONTROL, session]))
        self.last_session_timing = SessionTiming.from_response(resp)
        return resp[2:]  # session parameter record (P2/P2* timing)

    def ecu_reset(self, reset_type: int = S.ResetType.HARD_RESET) -> Optional[int]:
        """0x11. Returns the powerDownTime byte when the ECU sends one (only for
        enableRapidPowerShutDown), else ``None``. After a hard reset the ECU is back in
        the default session and relocked."""
        resp = self.request(bytes([S.Service.ECU_RESET, reset_type]))
        if len(resp) < 2 or resp[1] != reset_type:
            raise UnexpectedResponse("ECUReset subfunction echo mismatch")
        return resp[2] if len(resp) > 2 else None

    def tester_present(self, suppress: bool = True) -> None:
        sub = 0x00 | (S.SUPPRESS_POSITIVE_RESPONSE if suppress else 0x00)
        self.request(bytes([S.Service.TESTER_PRESENT, sub]),
                     expect_response=not suppress, suppress_positive=suppress)

    # ------------------------------------------------------------- 0x22 / 0x2E

    def read_data_by_identifier(self, did: int) -> bytes:
        resp = self.request(bytes([S.Service.READ_DATA_BY_IDENTIFIER, (did >> 8) & 0xFF, did & 0xFF]))
        # resp = [0x62, did_hi, did_lo, <data...>]
        if len(resp) < 3 or ((resp[1] << 8) | resp[2]) != did:
            raise UnexpectedResponse(f"ReadDataByIdentifier echo mismatch for DID 0x{did:04X}")
        return resp[3:]

    def read_data_by_identifiers(
        self,
        dids: Sequence[int],
        *,
        size_of: SizeOracle = None,
        skip_unsupported: bool = False,
        max_per_request: int = 8,
    ) -> Dict[int, bytes]:
        """Multi-DID 0x22: ``22 <DID1> <DID2> ...`` -> ``62 <DID1> <data1> <DID2> <data2> ...``.

        The response has no per-DID length, so splitting it needs a *size oracle*
        (``size_of``: a mapping or a callable ``did -> length | None``). DIDs with a
        known size are requested together (``max_per_request`` at a time); DIDs with
        an unknown size fall back to single reads. If the ECU rejects a batch (NRC 0x14
        responseTooLong, 0x33 because one DID is secured, or anything else) the batch
        degrades to single reads so one refused DID never hides the others.

        A batch answer that does **not** carry every requested DID is never trusted:
        ISO 14229-1 lets a server answer a multi-DID request with only the DIDs it
        supports, and a wrong (stale / oversized) oracle entry produces exactly the
        same shape by swallowing the next DID's field into the previous one. Both
        cases degrade to single reads of the whole batch, which (a) surfaces the real
        NRC for a missing DID (raised, unless ``skip_unsupported`` and it is 0x31) and
        (b) yields the true length of every DID instead of a corrupted split.

        ``skip_unsupported=True`` drops DIDs answered with NRC 0x31 instead of raising.
        Returns ``{did: data}`` in request order for the DIDs that answered.
        """
        oracle = _oracle(size_of)
        known: List[int] = []
        unknown: List[int] = []
        for did in dids:
            (known if oracle(did) is not None else unknown).append(did)
        out: Dict[int, bytes] = {}

        for i in range(0, len(known), max(1, max_per_request)):
            batch = known[i:i + max_per_request]
            if len(batch) == 1:
                self._read_single_into(out, batch[0], skip_unsupported)
                continue
            try:
                got = self._read_batch(batch, oracle)
            except NegativeResponse as exc:
                log.debug("multi-DID read of %s refused (%s); falling back to single reads",
                          [f"0x{d:04X}" for d in batch], exc)
                for did in batch:
                    self._read_single_into(out, did, skip_unsupported)
                continue
            except UnexpectedResponse as exc:
                log.warning("multi-DID response could not be split (%s); falling back to "
                            "single reads", exc)
                for did in batch:
                    self._read_single_into(out, did, skip_unsupported)
                continue
            missing = [d for d in batch if d not in got]
            if missing:
                log.info("multi-DID response omitted %s (unsupported DID or wrong size oracle); "
                         "re-reading the batch one DID at a time",
                         [f"0x{d:04X}" for d in missing])
                for did in batch:
                    self._read_single_into(out, did, skip_unsupported)
                continue
            out.update(got)

        for did in unknown:
            self._read_single_into(out, did, skip_unsupported)
        # Preserve request order.
        return {did: out[did] for did in dids if did in out}

    def _read_single_into(self, out: Dict[int, bytes], did: int, skip_unsupported: bool) -> None:
        try:
            out[did] = self.read_data_by_identifier(did)
        except NegativeResponse as exc:
            if skip_unsupported and exc.nrc == NRC_REQUEST_OUT_OF_RANGE:
                log.debug("DID 0x%04X not supported", did)
                return
            raise

    def _read_batch(self, batch: Sequence[int], oracle: Callable[[int], Optional[int]]) -> Dict[int, bytes]:
        payload = bytearray([S.Service.READ_DATA_BY_IDENTIFIER])
        for did in batch:
            payload += bytes([(did >> 8) & 0xFF, did & 0xFF])
        resp = self.request(bytes(payload))
        wanted = set(batch)
        out: Dict[int, bytes] = {}
        p = 1
        while p < len(resp):
            if p + 2 > len(resp):
                raise UnexpectedResponse("multi-DID response ends inside a DID number")
            did = (resp[p] << 8) | resp[p + 1]
            if did not in wanted:
                raise UnexpectedResponse(
                    f"multi-DID response carries DID 0x{did:04X} that was not requested "
                    f"(size oracle wrong for an earlier DID?)")
            if did in out:
                raise UnexpectedResponse(
                    f"multi-DID response carries DID 0x{did:04X} twice "
                    f"(size oracle wrong for an earlier DID?)")
            size = oracle(did)
            assert size is not None
            if p + 2 + size > len(resp):
                raise UnexpectedResponse(
                    f"multi-DID response truncated inside DID 0x{did:04X} (expected {size} bytes)")
            out[did] = resp[p + 2:p + 2 + size]
            p += 2 + size
        return out

    def write_data_by_identifier(self, did: int, data: bytes) -> None:
        payload = bytes([S.Service.WRITE_DATA_BY_IDENTIFIER, (did >> 8) & 0xFF, did & 0xFF]) + data
        resp = self.request(payload)
        if len(resp) < 3 or ((resp[1] << 8) | resp[2]) != did:
            raise UnexpectedResponse(f"WriteDataByIdentifier echo mismatch for DID 0x{did:04X}")

    def scan_dids(
        self,
        start: int,
        stop: int,
        *,
        on_progress: Optional[Callable[[int, Optional[Union[bytes, NegativeResponse]]], None]] = None,
        stop_on_service_unsupported: bool = True,
    ) -> Dict[int, Union[bytes, NegativeResponse]]:
        """Probe every DID in ``range(start, stop)`` with a single 0x22 each.

        Classification (PROTOCOL_FACTS NRC semantics):

        * positive response -> ``result[did] = data``
        * NRC 0x31 requestOutOfRange -> the DID does not exist here; omitted
        * NRC 0x13 / 0x22 / 0x33 / 0x37 / 0x7E / 0x7F -> the DID exists but is refused
          (wrong session, locked, conditions, length); ``result[did]`` holds the
          :class:`NegativeResponse` so the caller can retry after login
        * NRC 0x11 serviceNotSupported -> the scan is pointless; raised (unless
          ``stop_on_service_unsupported=False``, then treated like 0x31)
        * any other NRC -> kept as the NegativeResponse (odd but informative)

        ``on_progress(did, outcome)`` is called per DID with ``None`` for an absent DID.
        A transport timeout propagates: an ECU normally answers every 0x22, so silence
        means it went away.
        """
        result: Dict[int, Union[bytes, NegativeResponse]] = {}
        for did in range(start, stop):
            outcome: Optional[Union[bytes, NegativeResponse]]
            try:
                outcome = self.read_data_by_identifier(did)
            except NegativeResponse as exc:
                if exc.nrc == NRC_REQUEST_OUT_OF_RANGE:
                    outcome = None
                elif exc.nrc == NRC_SERVICE_NOT_SUPPORTED and stop_on_service_unsupported:
                    raise
                elif exc.nrc == NRC_SERVICE_NOT_SUPPORTED:
                    outcome = None
                else:
                    outcome = exc
            if outcome is not None:
                result[did] = outcome
            if on_progress is not None:
                on_progress(did, outcome)
        return result

    # ------------------------------------------------------------- 0x23 / 0x14

    def read_memory_by_address(self, address: int, size: int,
                               addr_bytes: int = 4, size_bytes: int = 4) -> bytes:
        alfid = (size_bytes << 4) | addr_bytes
        payload = (bytes([S.Service.READ_MEMORY_BY_ADDRESS, alfid])
                   + address.to_bytes(addr_bytes, "big")
                   + size.to_bytes(size_bytes, "big"))
        resp = self.request(payload)
        return resp[1:]

    def clear_diagnostic_information(self, group: int = S.CLEAR_ALL_DTC_GROUPS) -> None:
        """0x14 with a 3-byte group; 0xFFFFFF clears everything (verified)."""
        payload = bytes([S.Service.CLEAR_DIAGNOSTIC_INFORMATION]) + group.to_bytes(3, "big")
        self.request(payload)

    # ------------------------------------------------------------- 0x19 ReadDTCInformation

    def read_dtc_by_status_mask(self, status_mask: int = 0xFF) -> List[Tuple[int, int]]:
        """Return a list of (dtc_number, status_byte). dtc_number is the 3-byte DTC
        packed into an int (high byte first). Kept for 0.1.0 callers; see
        :meth:`read_dtcs` for the dataclass form."""
        return [(d.dtc, d.status) for d in self.read_dtcs(status_mask)]

    def _read_dtc_info(self, subfunction: int, data: bytes = b"") -> bytes:
        return self.request(bytes([S.Service.READ_DTC_INFORMATION, subfunction]) + data)

    def read_dtc_count(self, status_mask: int = 0xFF) -> D.DtcCount:
        """0x19 0x01: number of DTCs matching the mask (+ availability mask, format)."""
        return D.parse_dtc_count(self._read_dtc_info(0x01, bytes([status_mask])))

    def read_dtcs(self, status_mask: int = 0xFF) -> List[D.UdsDtc]:
        """0x19 0x02 reportDTCByStatusMask; VCDS-style "all faults" is mask 0xFF."""
        _, dtcs = D.parse_dtc_records(self._read_dtc_info(0x02, bytes([status_mask])), 0x02)
        return dtcs

    def read_dtc_records(self, subfunction: int, data: bytes = b"") -> Tuple[int, List[D.UdsDtc]]:
        """Any subfunction of the "availability mask + 4-byte records" group
        (0x0A/0x0B/0x0C/0x0D/0x0E/0x0F/0x13/0x15/0x17)."""
        if subfunction not in S.DTC_RECORD_LIST_SUBFUNCTIONS:
            raise ValueError(f"0x19 subfunction 0x{subfunction:02X} is not a DTC record list")
        return D.parse_dtc_records(self._read_dtc_info(subfunction, data), subfunction)

    def read_supported_dtcs(self) -> List[D.UdsDtc]:
        """0x19 0x0A reportSupportedDTCs (no mask byte)."""
        return self.read_dtc_records(0x0A)[1]

    def read_dtc_snapshot_identification(self) -> List[Tuple[D.UdsDtc, int]]:
        """0x19 0x03: which DTCs have which snapshot record numbers."""
        return D.parse_snapshot_identification(self._read_dtc_info(0x03))

    def read_dtc_snapshot(self, dtc: int, record: int = 0xFF,
                          did_sizes: Optional[Mapping[int, int]] = None) -> D.DtcSnapshotReport:
        """0x19 0x04 reportDTCSnapshotRecordByDTCNumber (``record`` 0xFF = all).

        Snapshot DID payload lengths are not in the message: pass ``did_sizes`` from a
        label file / ODX / the simulator; unknown DIDs come back raw (never guessed).
        """
        payload = D.dtc_to_bytes(dtc) + bytes([record & 0xFF])
        return D.parse_snapshot_records(self._read_dtc_info(0x04, payload), did_sizes)

    def read_dtc_extended_data(self, dtc: int, record: int = 0xFF,
                               record_sizes: Optional[Mapping[int, int]] = None) -> D.DtcExtendedReport:
        """0x19 0x06 reportDTCExtendedDataRecordByDTCNumber (``record`` 0xFF = all).

        Record sizes are not in the message either; without ``record_sizes`` the whole
        tail is returned raw under the first record number.
        """
        payload = D.dtc_to_bytes(dtc) + bytes([record & 0xFF])
        return D.parse_extended_data(self._read_dtc_info(0x06, payload), record_sizes)

    def read_dtc_fault_detection_counters(self) -> List[D.UdsDtc]:
        """0x19 0x14: DTCs whose fault-maturing counter is non-zero ("almost failing")."""
        return D.parse_fault_detection_counters(self._read_dtc_info(0x14))

    # ------------------------------------------------------------- 0x31 RoutineControl

    def routine_control(self, routine_id: int,
                        control: int = S.RoutineControlType.START,
                        data: bytes = b"") -> bytes:
        """``31 <sub> <RID_hi> <RID_lo> [options]`` -> ``71 <sub> <RID> [status record]``;
        returns the status record."""
        payload = bytes([S.Service.ROUTINE_CONTROL, control,
                         (routine_id >> 8) & 0xFF, routine_id & 0xFF]) + data
        resp = self.request(payload)
        if len(resp) < 4 or resp[1] != control or ((resp[2] << 8) | resp[3]) != routine_id:
            raise UnexpectedResponse(f"RoutineControl echo mismatch for routine 0x{routine_id:04X}")
        return resp[4:]

    def routine_start(self, routine_id: int, data: bytes = b"") -> bytes:
        return self.routine_control(routine_id, S.RoutineControlType.START, data)

    def routine_stop(self, routine_id: int, data: bytes = b"") -> bytes:
        return self.routine_control(routine_id, S.RoutineControlType.STOP, data)

    def routine_results(self, routine_id: int, data: bytes = b"") -> bytes:
        return self.routine_control(routine_id, S.RoutineControlType.REQUEST_RESULTS, data)

    # ------------------------------------------------------------- 0x2F IO control

    def io_control_by_id(self, did: int, control_option: int, control_state: bytes = b"") -> bytes:
        """``2F <DID> <option> [state] [enable mask]`` -> ``6F <DID> <option> [status]``;
        returns the status/data bytes after the echo."""
        payload = bytes([S.Service.INPUT_OUTPUT_CONTROL,
                         (did >> 8) & 0xFF, did & 0xFF, control_option]) + control_state
        resp = self.request(payload)
        if len(resp) < 4 or ((resp[1] << 8) | resp[2]) != did or resp[3] != control_option:
            raise UnexpectedResponse(f"InputOutputControl echo mismatch for DID 0x{did:04X}")
        return resp[4:]

    def io_control(self, did: int, option: int = S.IoControlOption.SHORT_TERM_ADJUSTMENT,
                   data: bytes = b"") -> bytes:
        """Output test: ``2F <DID> 03 <value>`` drives an actuator (shortTermAdjustment);
        option 00 returns control, 01 resets to default, 02 freezes (verified)."""
        return self.io_control_by_id(did, option, data)

    def return_control(self, did: int) -> bytes:
        """``2F <DID> 00``: hand the output back to the ECU."""
        return self.io_control_by_id(did, S.IoControlOption.RETURN_CONTROL_TO_ECU)

    # ------------------------------------------------------------- 0x2C dynamic DIDs

    def dynamically_define_did_by_memory(self, dyn_did: int,
                                         entries: Sequence[Tuple[int, int]],
                                         *, addr_bytes: int = 4, size_bytes: int = 1) -> None:
        """``2C 02 <dynDID> <ALFID> (<address> <size>)*`` -> ``6C 02 <dynDID>``.

        ALFID high nibble = size byte count, low nibble = address byte count; the
        VW_Flash Simos logging capture uses ALFID 0x14 (4-byte address, 1-byte size)
        with entries like ``D0 01 B3 AA 01`` (reported/unverified reading of the capture,
        but it is plain ISO 14229 so the framing itself is standard).
        """
        if not entries:
            raise ValueError("at least one (address, size) entry is required")
        alfid = ((size_bytes & 0xF) << 4) | (addr_bytes & 0xF)
        payload = bytearray([S.Service.DYNAMICALLY_DEFINE_DATA_ID, S.DynamicDefineType.DEFINE_BY_MEMORY_ADDRESS,
                             (dyn_did >> 8) & 0xFF, dyn_did & 0xFF, alfid])
        for address, size in entries:
            payload += address.to_bytes(addr_bytes, "big") + size.to_bytes(size_bytes, "big")
        resp = self.request(bytes(payload))
        self._check_dyn_echo(resp, S.DynamicDefineType.DEFINE_BY_MEMORY_ADDRESS, dyn_did)

    def dynamically_define_did_by_identifier(self, dyn_did: int,
                                             entries: Sequence[Tuple[int, int, int]]) -> None:
        """``2C 01 <dynDID> (<sourceDID> <position> <size>)*``; position is 1-based."""
        if not entries:
            raise ValueError("at least one (source_did, position, size) entry is required")
        payload = bytearray([S.Service.DYNAMICALLY_DEFINE_DATA_ID, S.DynamicDefineType.DEFINE_BY_IDENTIFIER,
                             (dyn_did >> 8) & 0xFF, dyn_did & 0xFF])
        for source_did, position, size in entries:
            if not 1 <= position <= 0xFF or not 1 <= size <= 0xFF:
                raise ValueError("position and size must be 1..255")
            payload += bytes([(source_did >> 8) & 0xFF, source_did & 0xFF, position, size])
        resp = self.request(bytes(payload))
        self._check_dyn_echo(resp, S.DynamicDefineType.DEFINE_BY_IDENTIFIER, dyn_did)

    def clear_dynamic_did(self, dyn_did: Optional[int] = None) -> None:
        """``2C 03 <dynDID>`` (or ``2C 03`` alone to clear every dynamic DID)."""
        payload = bytes([S.Service.DYNAMICALLY_DEFINE_DATA_ID, S.DynamicDefineType.CLEAR])
        if dyn_did is not None:
            payload += bytes([(dyn_did >> 8) & 0xFF, dyn_did & 0xFF])
        resp = self.request(payload)
        if dyn_did is not None:
            self._check_dyn_echo(resp, S.DynamicDefineType.CLEAR, dyn_did)

    @staticmethod
    def _check_dyn_echo(resp: bytes, sub: int, dyn_did: int) -> None:
        if len(resp) < 4 or resp[1] != sub or ((resp[2] << 8) | resp[3]) != dyn_did:
            raise UnexpectedResponse(f"DynamicallyDefineDataIdentifier echo mismatch for 0x{dyn_did:04X}")

    # ------------------------------------------------------------- 0x28 / 0x85

    def communication_control(self, control: int, comm_type: int = S.COMM_NORMAL_MESSAGES,
                              node_id: Optional[int] = None) -> None:
        """``28 <controlType> <communicationType> [nodeId(2)]`` -> ``68 <controlType>``.

        ``28 03 01`` silences normal messages (what VW tools send before flashing),
        ``28 00 01`` re-enables them. The 2-byte nodeId is only valid for control types
        4/5 (2013+ standard).
        """
        if node_id is not None and control not in (
                S.CommunicationControlType.ENABLE_RX_AND_DISABLE_TX_WITH_ENHANCED_ADDRESS_INFORMATION,
                S.CommunicationControlType.ENABLE_RX_AND_TX_WITH_ENHANCED_ADDRESS_INFORMATION):
            raise ValueError("nodeId is only allowed with controlType 4 or 5")
        payload = bytes([S.Service.COMMUNICATION_CONTROL, control, comm_type & 0xFF])
        if node_id is not None:
            payload += node_id.to_bytes(2, "big")
        resp = self.request(payload)
        if len(resp) < 2 or resp[1] != control:
            raise UnexpectedResponse("CommunicationControl subfunction echo mismatch")

    def control_dtc_setting(self, on: bool, *, suppress: bool = False) -> None:
        """``85 01`` = ON, ``85 02`` = OFF (verified subfunctions).

        By default the request is sent without the suppress bit and the ``C5 <sub>``
        echo is validated, so a refusal (NRC 0x7F in the default session, 0x22 with
        the engine running) is raised and never mistaken for "logging is off" before
        an actuator test or a flash. ``suppress=True`` sets the suppress bit for bus
        quietness; the ECU then stays silent on success but still answers ``7F 85
        <NRC>`` on refusal, which :meth:`request` listens for and raises.
        """
        sub = S.DtcSettingType.ON if on else S.DtcSettingType.OFF
        if suppress:
            self.request(bytes([S.Service.CONTROL_DTC_SETTING, sub | S.SUPPRESS_POSITIVE_RESPONSE]),
                         expect_response=False, suppress_positive=True)
            return
        resp = self.request(bytes([S.Service.CONTROL_DTC_SETTING, sub]))
        if len(resp) < 2 or resp[1] != sub:
            raise UnexpectedResponse("ControlDTCSetting subfunction echo mismatch")

    # ------------------------------------------------------------- security access

    def security_access(self, level: int, seed_key_fn: SeedKeyFn) -> None:
        """Perform seed/key for the given security level (odd=requestSeed, even=sendKey).

        ``level`` is the requestSeed subfunction (e.g. 0x01, 0x03, 0x11 for VAG).
        The matching sendKey subfunction is ``level + 1``.
        """
        if level % 2 == 0:
            raise ValueError("security level must be the odd requestSeed subfunction")
        seed_resp = self.request(bytes([S.Service.SECURITY_ACCESS, level]))
        # seed_resp = [0x67, level, <seed...>]
        if len(seed_resp) < 2 or seed_resp[1] != level:
            raise UnexpectedResponse("SecurityAccess seed echo mismatch")
        seed = seed_resp[2:]
        if not seed:
            # A bare "67 <level>" is a truncated/malformed reply, not an unlock: the
            # all-zero-seed convention (ISO 14229-1 §9.4.2) needs a seed to be present.
            raise UnexpectedResponse(
                f"SecurityAccess seed response for level 0x{level:02X} carries no seed bytes")

        if all(b == 0 for b in seed):
            log.info("ECU returned all-zero seed for level 0x%02X (already unlocked)", level)
            return

        key = seed_key_fn(level, seed)
        send_sub = level + 1
        key_resp = self.request(bytes([S.Service.SECURITY_ACCESS, send_sub]) + key)
        if len(key_resp) < 2 or key_resp[1] != send_sub:
            raise UnexpectedResponse("SecurityAccess sendKey echo mismatch")
        log.info("security access level 0x%02X unlocked", level)

    # ------------------------------------------------------------- data transfer

    def request_upload(self, address: int, size: int,
                       data_format: int = 0x00,
                       addr_bytes: int = 4, size_bytes: int = 4) -> int:
        """RequestUpload (0x35). Returns the max block length the ECU will accept
        per TransferData (including the SID + sequence byte overhead)."""
        alfid = (size_bytes << 4) | addr_bytes
        payload = (bytes([S.Service.REQUEST_UPLOAD, data_format, alfid])
                   + address.to_bytes(addr_bytes, "big")
                   + size.to_bytes(size_bytes, "big"))
        resp = self.request(payload)
        # resp = [0x75, lengthFormatIdentifier, maxNumberOfBlockLength...]
        return self._parse_transfer_setup(resp, "RequestUpload")

    def request_download(self, address: int, size: int,
                        data_format: int = 0x00,
                        addr_bytes: int = 4, size_bytes: int = 4) -> int:
        """RequestDownload (0x34). Returns max block length per TransferData."""
        alfid = (size_bytes << 4) | addr_bytes
        payload = (bytes([S.Service.REQUEST_DOWNLOAD, data_format, alfid])
                   + address.to_bytes(addr_bytes, "big")
                   + size.to_bytes(size_bytes, "big"))
        resp = self.request(payload)
        return self._parse_transfer_setup(resp, "RequestDownload")

    @staticmethod
    def _parse_transfer_setup(resp: bytes, name: str) -> int:
        """``74/75 <lengthFormatIdentifier> <maxNumberOfBlockLength(lfid bytes)>`` ->
        maxNumberOfBlockLength. The high nibble of the lengthFormatIdentifier is the
        byte count of the following field (ISO 14229-1 §14.1.2 / §14.2.2); a missing
        or zero-length field, a truncated field, or a block length that cannot carry
        a single data byte (<= SID + sequence byte) is a :class:`UnexpectedResponse`,
        never an IndexError or a 1-byte-block transfer."""
        if len(resp) < 2:
            raise UnexpectedResponse(f"{name} response too short ({len(resp)} bytes)")
        lfid = (resp[1] >> 4) & 0x0F
        if lfid == 0:
            raise UnexpectedResponse(f"{name} response has a zero-length maxNumberOfBlockLength")
        if len(resp) < 2 + lfid:
            raise UnexpectedResponse(
                f"{name} response truncated: lengthFormatIdentifier announces {lfid} bytes, "
                f"{len(resp) - 2} present")
        max_block = int.from_bytes(resp[2:2 + lfid], "big")
        if max_block <= 2:
            raise UnexpectedResponse(
                f"{name}: maxNumberOfBlockLength {max_block} cannot carry data (SID + sequence "
                "byte already take 2)")
        return max_block

    def transfer_data_read(self, block_seq: int) -> bytes:
        """One TransferData (0x36) during an upload; returns the data block."""
        resp = self.request(bytes([S.Service.TRANSFER_DATA, block_seq & 0xFF]))
        if len(resp) < 2 or resp[1] != (block_seq & 0xFF):
            raise UnexpectedResponse(f"TransferData block sequence mismatch (expected {block_seq})")
        return resp[2:]

    def transfer_data_write(self, block_seq: int, data: bytes) -> bytes:
        """One TransferData (0x36) during a download; returns any parameter echo."""
        resp = self.request(bytes([S.Service.TRANSFER_DATA, block_seq & 0xFF]) + data)
        if len(resp) < 2 or resp[1] != (block_seq & 0xFF):
            raise UnexpectedResponse(f"TransferData block sequence mismatch (expected {block_seq})")
        return resp[2:]

    def request_transfer_exit(self, data: bytes = b"") -> bytes:
        resp = self.request(bytes([S.Service.REQUEST_TRANSFER_EXIT]) + data)
        return resp[1:]

    def upload(self, address: int, size: int,
               progress: Optional[ProgressFn] = None,
               addr_bytes: int = 4, size_bytes: int = 4) -> bytes:
        """High-level block read: RequestUpload -> loop TransferData -> TransferExit.

        Returns the concatenated memory image. ``progress(done, total)`` is called
        after each block if provided.
        """
        max_block = self.request_upload(address, size, addr_bytes=addr_bytes, size_bytes=size_bytes)
        # max_block includes the 2-byte (SID + seq) overhead of the response frame.
        chunk = max(1, max_block - 2)
        out = bytearray()
        seq = 1
        while len(out) < size:
            block = self.transfer_data_read(seq)
            if not block:
                break
            out.extend(block)
            seq = (seq + 1) & 0xFF
            if progress:
                progress(min(len(out), size), size)
        self.request_transfer_exit()
        return bytes(out[:size])

    def download(self, address: int, data: bytes,
                 progress: Optional[ProgressFn] = None,
                 addr_bytes: int = 4, size_bytes: int = 4,
                 data_format: int = 0x00) -> None:
        """High-level block write: RequestDownload -> TransferData writes -> TransferExit.

        The write-side mirror of :meth:`upload`; it only moves bytes. Erase routines,
        checksum routines, backups and identity checks belong to the caller
        (``flash/``) — this method never decides whether a write is safe.
        """
        size = len(data)
        max_block = self.request_download(address, size, data_format=data_format,
                                          addr_bytes=addr_bytes, size_bytes=size_bytes)
        chunk = max(1, max_block - 2)   # SID + sequence byte overhead
        seq = 1
        done = 0
        while done < size:
            block = data[done:done + chunk]
            self.transfer_data_write(seq, block)
            done += len(block)
            seq = (seq + 1) & 0xFF
            if progress:
                progress(done, size)
        self.request_transfer_exit()

    # ====================================================== tester-present keepalive

    def start_tester_present(self, interval: float = 2.0) -> None:
        """Start a background thread that sends suppressed TesterPresent periodically.

        VAG ECUs fall back to the default session (and relock security) after roughly
        5 s of silence (S3 timeout), so keep this running during long operations.
        """
        self.stop_tester_present()
        self._tp_thread = _TesterPresentThread(self, interval)
        self._tp_thread.start()

    def stop_tester_present(self) -> None:
        if self._tp_thread is not None:
            self._tp_thread.stop()
            self._tp_thread.join(timeout=2.0)
            self._tp_thread = None

    def close(self) -> None:
        self.stop_tester_present()
        self.link.close()

    def __enter__(self) -> "UdsClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def _oracle(size_of: SizeOracle) -> Callable[[int], Optional[int]]:
    if size_of is None:
        return lambda did: None
    if callable(size_of):
        return size_of
    mapping = size_of
    return lambda did: mapping.get(did)


class _BusyRepeat(Exception):
    """Internal signal: NRC 0x21, caller should resend the whole request."""


class _TesterPresentThread(threading.Thread):
    def __init__(self, client: UdsClient, interval: float) -> None:
        super().__init__(name="uds-tester-present", daemon=True)
        self.client = client
        self.interval = interval
        # NOTE: must not be named `_stop` - threading.Thread uses that name internally.
        self._halt = threading.Event()

    def run(self) -> None:
        while not self._halt.wait(self.interval):
            try:
                self.client.tester_present(suppress=True)
            except (TransportTimeout, UdsTimeout):
                log.debug("tester-present keepalive timed out (bus busy)")
            except NegativeResponse as exc:
                # The ECU refused the keepalive (now visible thanks to the suppressed-NRC
                # window); the session will time out on its own, which the next
                # foreground request reports as NRC 0x7F/0x33.
                log.debug("tester-present keepalive refused: %s", exc)
            except Exception as exc:  # pragma: no cover - keepalive must never crash app
                log.debug("tester-present keepalive error: %s", exc)

    def stop(self) -> None:
        self._halt.set()
