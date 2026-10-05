"""
Offline test harness: a fake ISO-TP link wired to a tiny simulated ECU.

This lets the entire UDS + VAG stack run on a laptop with no hardware. The
simulated ECU understands enough UDS to exercise the client: session control,
tester-present, read-data-by-identifier for the VAG identification DIDs, a
seed/key security handshake using the real SA2 interpreter, read DTCs, and a
minimal upload (read-memory / request-upload + transfer-data) so calibration
reads can be tested end to end.

It is deliberately not a faithful model of any real control unit - just a
predictable peer that speaks the same wire protocol.
"""

from __future__ import annotations

import logging
import queue
from typing import Callable, Dict, List, Optional, Tuple

from ..vag.sa2 import Sa2Interpreter
from .base import IsoTpLink

log = logging.getLogger(__name__)


class SimulatedEcu:
    """A scriptable UDS responder addressed at one pair of CAN IDs."""

    # A short, real SA2 script (from public SIMOS18 documentation) so the seed/key
    # path is exercised with genuine opcode semantics rather than a stub.
    DEFAULT_SA2 = bytes.fromhex(
        "6802814A10680493080820094A05872212195482499307122011824A058703112010824A0181494C"
    )

    def __init__(self) -> None:
        self.session = 0x01                       # default session
        self.security_unlocked = False
        self._pending_seed: Optional[int] = None
        self.sa2_script = self.DEFAULT_SA2
        # Fixed seed so tests are deterministic.
        self._seed_value = 0x1A2B3C4D

        # Identification DIDs (ISO 14229 / VAG) -> response bytes.
        self.identifiers: Dict[int, bytes] = {
            0xF190: b"WVWZZZAUZLW000001",            # VIN
            0xF187: b"8V0906259H",                    # VW spare part number
            0xF189: b"0001",                          # application software version
            0xF191: b"03C906016AB",                   # ECU hardware number
            0xF197: b"R4 2.0L TFSI",                  # system name / engine type
            0xF1A2: b"SC8_MQB_270",                   # ASAM/ODX file version
            0x0600: b"\x12\x34\x56\x78",              # example measurement block
        }

        # A couple of stored DTCs for readDTCInformation (status mask 0xFF).
        # Each entry is (3-byte DTC, status byte).
        self.dtcs: List[Tuple[bytes, int]] = [
            (b"\x01\x12\x00", 0x2F),  # P0112-ish
            (b"\x05\x61\x00", 0x09),
        ]

        # Memory is a set of regions, like a real ECU's address map:
        #   * a 64 KiB demo region at address 0 (simple tests, read-memory-by-address)
        #   * a 512 KiB "calibration" region at the SIMOS18.1 CAL block address, so
        #     the profile-driven read-cal flow hits the exact addresses a real car has.
        self.memory = bytes((i & 0xFF) for i in range(0x10000))
        self.cal_base = 0x80A8_0000
        self.cal_memory = bytes(((i * 7 + 3) & 0xFF) for i in range(0x8_0000))
        self.regions: List[Tuple[int, bytes]] = [
            (0x0, self.memory),
            (self.cal_base, self.cal_memory),
        ]
        self._upload_cursor = 0
        self._upload_remaining = 0
        self._upload_block_seq = 1

        self.custom_handlers: Dict[int, Callable[[bytes], bytes]] = {}

    def _slice(self, addr: int, size: int) -> bytes:
        """Return memory for [addr, addr+size) or raise requestOutOfRange."""
        for base, data in self.regions:
            if base <= addr and addr + size <= base + len(data):
                off = addr - base
                return data[off:off + size]
        raise _Nrc(0x31)

    # -- security ----------------------------------------------------------------

    def _seed(self) -> bytes:
        self._pending_seed = self._seed_value
        return self._seed_value.to_bytes(4, "big")

    def _expected_key(self) -> int:
        interp = Sa2Interpreter(self.sa2_script)
        return interp.compute_key(self._pending_seed)

    # -- request dispatch --------------------------------------------------------

    def handle(self, request: bytes) -> Optional[bytes]:
        """Map a UDS request to a response (or ``None`` to stay silent)."""
        if not request:
            return None
        sid = request[0]
        try:
            if sid == 0x10:    # DiagnosticSessionControl
                return self._svc_session(request)
            if sid == 0x3E:    # TesterPresent
                suppress = len(request) > 1 and (request[1] & 0x80)
                return None if suppress else bytes([0x7E, request[1] if len(request) > 1 else 0x00])
            if sid == 0x22:    # ReadDataByIdentifier
                return self._svc_read_did(request)
            if sid == 0x27:    # SecurityAccess
                return self._svc_security(request)
            if sid == 0x19:    # ReadDTCInformation
                return self._svc_read_dtc(request)
            if sid == 0x14:    # ClearDiagnosticInformation
                self.dtcs.clear()
                return bytes([0x54])
            if sid == 0x23:    # ReadMemoryByAddress
                return self._svc_read_memory(request)
            if sid == 0x35:    # RequestUpload
                return self._svc_request_upload(request)
            if sid == 0x36:    # TransferData
                return self._svc_transfer_data(request)
            if sid == 0x37:    # RequestTransferExit
                return bytes([0x77])
            if sid in self.custom_handlers:
                return self.custom_handlers[sid](request)
        except _Nrc as nrc:
            return bytes([0x7F, sid, nrc.code])
        return bytes([0x7F, sid, 0x11])  # serviceNotSupported

    def _svc_session(self, request: bytes) -> bytes:
        if len(request) < 2:
            raise _Nrc(0x13)
        self.session = request[1]
        # P2/P2* timing params (dummy but well-formed): 50ms, 5000ms.
        return bytes([0x50, request[1], 0x00, 0x32, 0x01, 0xF4])

    def _svc_read_did(self, request: bytes) -> bytes:
        if len(request) < 3:
            raise _Nrc(0x13)
        did = (request[1] << 8) | request[2]
        if did not in self.identifiers:
            raise _Nrc(0x31)  # requestOutOfRange
        value = self.identifiers[did]
        return bytes([0x62, request[1], request[2]]) + value

    def _svc_security(self, request: bytes) -> bytes:
        if len(request) < 2:
            raise _Nrc(0x13)
        sub = request[1]
        if sub % 2 == 1:          # requestSeed (odd subfunction)
            if self.security_unlocked:
                return bytes([0x67, sub, 0x00, 0x00, 0x00, 0x00])  # already unlocked -> zero seed
            return bytes([0x67, sub]) + self._seed()
        else:                      # sendKey (even subfunction)
            if self._pending_seed is None:
                raise _Nrc(0x24)  # requestSequenceError
            key = int.from_bytes(request[2:6], "big")
            if key == self._expected_key():
                self.security_unlocked = True
                self._pending_seed = None
                return bytes([0x67, sub])
            raise _Nrc(0x35)      # invalidKey

    def _svc_read_dtc(self, request: bytes) -> bytes:
        # Support subfunction 0x02 reportDTCByStatusMask.
        if len(request) < 3 or request[1] != 0x02:
            raise _Nrc(0x12)
        mask = request[2]
        body = bytearray([0x59, 0x02, 0xFF])  # echo availability mask
        for dtc, status in self.dtcs:
            if status & mask:
                body += dtc + bytes([status])
        return bytes(body)

    def _svc_read_memory(self, request: bytes) -> bytes:
        # Simplified addressAndLengthFormatIdentifier: 0x44 => 4-byte addr, 4-byte len.
        if len(request) < 2:
            raise _Nrc(0x13)
        alfid = request[1]
        addr_len = (alfid >> 4) & 0x0F
        size_len = alfid & 0x0F
        p = 2
        addr = int.from_bytes(request[p:p + addr_len], "big"); p += addr_len
        size = int.from_bytes(request[p:p + size_len], "big"); p += size_len
        return bytes([0x63]) + self._slice(addr, size)

    def _svc_request_upload(self, request: bytes) -> bytes:
        if not self.security_unlocked:
            raise _Nrc(0x33)  # securityAccessDenied
        # dataFormatIdentifier + addressAndLengthFormatIdentifier + addr + len
        if len(request) < 3:
            raise _Nrc(0x13)
        alfid = request[2]
        addr_len = (alfid >> 4) & 0x0F
        size_len = alfid & 0x0F
        p = 3
        addr = int.from_bytes(request[p:p + addr_len], "big"); p += addr_len
        size = int.from_bytes(request[p:p + size_len], "big"); p += size_len
        self._slice(addr, size)  # validates the range (raises 0x31 if bad)
        self._upload_cursor = addr
        self._upload_remaining = size
        self._upload_block_seq = 1
        # lengthFormatIdentifier = 2, then maxNumberOfBlockLength (0x0102 = 258 incl. SID+seq).
        return bytes([0x75, 0x20, 0x01, 0x02])

    def _svc_transfer_data(self, request: bytes) -> bytes:
        if len(request) < 2:
            raise _Nrc(0x13)
        seq = request[1]
        if seq != (self._upload_block_seq & 0xFF):
            raise _Nrc(0x73)  # wrongBlockSequenceCounter
        if self._upload_remaining <= 0:
            raise _Nrc(0x31)
        chunk_len = min(255, self._upload_remaining)
        chunk = self._slice(self._upload_cursor, chunk_len)
        self._upload_cursor += chunk_len
        self._upload_remaining -= chunk_len
        self._upload_block_seq = (self._upload_block_seq + 1) & 0xFF
        return bytes([0x76, seq]) + chunk


class _Nrc(Exception):
    def __init__(self, code: int) -> None:
        super().__init__(f"NRC 0x{code:02X}")
        self.code = code


class FakeIsoTpLink(IsoTpLink):
    """An ISO-TP link whose ``send`` is answered synchronously by a SimulatedEcu."""

    def __init__(self, tx_id: int, rx_id: int, ecu: SimulatedEcu) -> None:
        super().__init__(tx_id, rx_id)
        self.ecu = ecu
        self._inbox: "queue.Queue[bytes]" = queue.Queue()

    def send(self, payload: bytes) -> None:
        response = self.ecu.handle(payload)
        if response is not None:
            self._inbox.put(response)

    def recv(self, timeout: float) -> Optional[bytes]:
        try:
            return self._inbox.get(timeout=max(0.0, timeout))
        except queue.Empty:
            return None

    def flush_rx(self) -> None:
        while not self._inbox.empty():
            try:
                self._inbox.get_nowait()
            except queue.Empty:
                break

    def close(self) -> None:
        self.flush_rx()


def make_fake_pair(tx_id: int = 0x7E0, rx_id: int = 0x7E8) -> Tuple[FakeIsoTpLink, SimulatedEcu]:
    """Return (link, ecu) where the link's tester IDs match a VAG engine ECU."""
    ecu = SimulatedEcu()
    return FakeIsoTpLink(tx_id, rx_id, ecu), ecu
