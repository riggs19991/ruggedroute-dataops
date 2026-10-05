"""
ISO 14229-1 UDS client.

Sits on top of an :class:`~vagtune.transport.base.IsoTpLink` and speaks UDS to one
ECU. It implements the services this toolkit actually needs:

    0x10 DiagnosticSessionControl     0x27 SecurityAccess
    0x11 ECUReset                     0x31 RoutineControl
    0x14 ClearDiagnosticInformation   0x34 RequestDownload
    0x19 ReadDTCInformation           0x35 RequestUpload
    0x22 ReadDataByIdentifier         0x36 TransferData
    0x23 ReadMemoryByAddress          0x37 RequestTransferExit
    0x2E WriteDataByIdentifier        0x3E TesterPresent
    0x2F InputOutputControlByID       0x85 ControlDTCSetting

Design notes:

* Every request waits for a matching positive response, transparently looping on
  NRC 0x78 (requestCorrectlyReceived-ResponsePending), which VAG ECUs emit a lot
  during flash operations.
* A background tester-present thread can keep a non-default session alive; the
  send lock makes keepalive and foreground requests mutually exclusive on the link.
* ``security_access`` is algorithm-agnostic: you pass a callable seed->key. The
  VAG SA2 implementation (:mod:`vagtune.vag.sa2`) provides that callable.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from ..transport.base import IsoTpLink, TransportTimeout
from . import services as S
from .exceptions import NegativeResponse, UdsTimeout, UnexpectedResponse

log = logging.getLogger(__name__)

SeedKeyFn = Callable[[int, bytes], bytes]  # (level, seed_bytes) -> key_bytes


@dataclass
class UdsTiming:
    p2_timeout: float = 2.0          # normal response window
    p2_star_timeout: float = 5.0     # extended window after an 0x78 pending
    pending_limit: int = 30          # max consecutive 0x78 before giving up
    retry_on_busy: int = 2           # retries on NRC 0x21 busyRepeatRequest


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

        ``expect_response=False`` is for suppressed-positive requests (e.g. a
        tester-present with the suppress bit set), where the ECU stays silent.
        """
        sid = payload[0]
        busy_retries = self.timing.retry_on_busy

        with self._send_lock:
            while True:
                self.link.flush_rx()
                self.link.send(payload)
                if not expect_response or suppress_positive:
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
        resp = self.request(bytes([S.Service.DIAGNOSTIC_SESSION_CONTROL, session]))
        return resp[2:]  # session parameter record (P2/P2* timing)

    def ecu_reset(self, reset_type: int = S.ResetType.HARD_RESET) -> None:
        self.request(bytes([S.Service.ECU_RESET, reset_type]))

    def tester_present(self, suppress: bool = True) -> None:
        sub = 0x00 | (S.SUPPRESS_POSITIVE_RESPONSE if suppress else 0x00)
        self.request(bytes([S.Service.TESTER_PRESENT, sub]),
                     expect_response=not suppress, suppress_positive=suppress)

    def read_data_by_identifier(self, did: int) -> bytes:
        resp = self.request(bytes([S.Service.READ_DATA_BY_IDENTIFIER, (did >> 8) & 0xFF, did & 0xFF]))
        # resp = [0x62, did_hi, did_lo, <data...>]
        if len(resp) < 3 or ((resp[1] << 8) | resp[2]) != did:
            raise UnexpectedResponse(f"ReadDataByIdentifier echo mismatch for DID 0x{did:04X}")
        return resp[3:]

    def write_data_by_identifier(self, did: int, data: bytes) -> None:
        payload = bytes([S.Service.WRITE_DATA_BY_IDENTIFIER, (did >> 8) & 0xFF, did & 0xFF]) + data
        self.request(payload)

    def read_memory_by_address(self, address: int, size: int,
                               addr_bytes: int = 4, size_bytes: int = 4) -> bytes:
        alfid = (size_bytes << 4) | addr_bytes
        payload = (bytes([S.Service.READ_MEMORY_BY_ADDRESS, alfid])
                   + address.to_bytes(addr_bytes, "big")
                   + size.to_bytes(size_bytes, "big"))
        resp = self.request(payload)
        return resp[1:]

    def clear_diagnostic_information(self, group: int = 0xFFFFFF) -> None:
        payload = bytes([S.Service.CLEAR_DIAGNOSTIC_INFORMATION]) + group.to_bytes(3, "big")
        self.request(payload)

    def read_dtc_by_status_mask(self, status_mask: int = 0xFF) -> List[Tuple[int, int]]:
        """Return a list of (dtc_number, status_byte). dtc_number is the 3-byte DTC
        packed into an int (high byte first)."""
        payload = bytes([S.Service.READ_DTC_INFORMATION,
                         S.DtcReportType.REPORT_DTC_BY_STATUS_MASK, status_mask])
        resp = self.request(payload)
        # resp = [0x59, 0x02, availabilityMask, (DTC[3] + status[1]) * n]
        body = resp[3:]
        out: List[Tuple[int, int]] = []
        for i in range(0, len(body) - 3, 4):
            dtc = (body[i] << 16) | (body[i + 1] << 8) | body[i + 2]
            out.append((dtc, body[i + 3]))
        return out

    def routine_control(self, routine_id: int,
                        control: int = S.RoutineControlType.START,
                        data: bytes = b"") -> bytes:
        payload = bytes([S.Service.ROUTINE_CONTROL, control,
                         (routine_id >> 8) & 0xFF, routine_id & 0xFF]) + data
        resp = self.request(payload)
        return resp[4:]

    def io_control_by_id(self, did: int, control_option: int, control_state: bytes = b"") -> bytes:
        payload = bytes([S.Service.INPUT_OUTPUT_CONTROL,
                         (did >> 8) & 0xFF, did & 0xFF, control_option]) + control_state
        resp = self.request(payload)
        return resp[4:]

    def control_dtc_setting(self, on: bool) -> None:
        sub = 0x01 if on else 0x02  # on / off
        self.request(bytes([S.Service.CONTROL_DTC_SETTING, sub | S.SUPPRESS_POSITIVE_RESPONSE]),
                     expect_response=False, suppress_positive=True)

    # ------------------------------------------------------------- security access

    def security_access(self, level: int, seed_key_fn: SeedKeyFn) -> None:
        """Perform seed/key for the given security level (odd=requestSeed, even=sendKey).

        ``level`` is the requestSeed subfunction (e.g. 0x01, 0x03, 0x11 for VAG).
        The matching sendKey subfunction is ``level + 1``.
        """
        seed_resp = self.request(bytes([S.Service.SECURITY_ACCESS, level]))
        # seed_resp = [0x67, level, <seed...>]
        if len(seed_resp) < 2 or seed_resp[1] != level:
            raise UnexpectedResponse("SecurityAccess seed echo mismatch")
        seed = seed_resp[2:]

        if all(b == 0 for b in seed):
            log.info("ECU returned all-zero seed for level 0x%02X (already unlocked)", level)
            return

        key = seed_key_fn(level, seed)
        send_sub = level + 1
        self.request(bytes([S.Service.SECURITY_ACCESS, send_sub]) + key)
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
        lfid = (resp[1] >> 4) & 0x0F
        max_block = int.from_bytes(resp[2:2 + lfid], "big")
        return max_block

    def request_download(self, address: int, size: int,
                        data_format: int = 0x00,
                        addr_bytes: int = 4, size_bytes: int = 4) -> int:
        """RequestDownload (0x34). Returns max block length per TransferData."""
        alfid = (size_bytes << 4) | addr_bytes
        payload = (bytes([S.Service.REQUEST_DOWNLOAD, data_format, alfid])
                   + address.to_bytes(addr_bytes, "big")
                   + size.to_bytes(size_bytes, "big"))
        resp = self.request(payload)
        lfid = (resp[1] >> 4) & 0x0F
        return int.from_bytes(resp[2:2 + lfid], "big")

    def transfer_data_read(self, block_seq: int) -> bytes:
        """One TransferData (0x36) during an upload; returns the data block."""
        resp = self.request(bytes([S.Service.TRANSFER_DATA, block_seq & 0xFF]))
        if len(resp) < 2 or resp[1] != (block_seq & 0xFF):
            raise UnexpectedResponse(f"TransferData block sequence mismatch (expected {block_seq})")
        return resp[2:]

    def transfer_data_write(self, block_seq: int, data: bytes) -> bytes:
        """One TransferData (0x36) during a download; returns any parameter echo."""
        resp = self.request(bytes([S.Service.TRANSFER_DATA, block_seq & 0xFF]) + data)
        return resp[2:]

    def request_transfer_exit(self, data: bytes = b"") -> bytes:
        resp = self.request(bytes([S.Service.REQUEST_TRANSFER_EXIT]) + data)
        return resp[1:]

    def upload(self, address: int, size: int,
               progress: Optional[Callable[[int, int], None]] = None,
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
            except Exception as exc:  # pragma: no cover - keepalive must never crash app
                log.debug("tester-present keepalive error: %s", exc)

    def stop(self) -> None:
        self._halt.set()
