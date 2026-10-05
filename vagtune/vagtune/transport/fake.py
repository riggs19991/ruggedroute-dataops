"""
Offline test harness: a fake ISO-TP link wired to a simulated ECU.

This lets the entire UDS + VAG stack run on a laptop with no hardware. The
simulated ECU understands enough UDS to exercise the client: session control (with
session-gated services and NRC 0x7F/0x7E), tester-present, single and multi-DID
ReadDataByIdentifier, a seed/key security handshake using the real SA2 interpreter
plus a VCDS-style 5-digit login level, ReadDTCInformation subfunctions
01/02/03/04/06/0A/14 with snapshot and extended-data records, coding write, IO
control, routines, ECU reset, communication control, DTC setting, dynamically
defined DIDs, and upload/download (read-memory / request-upload + transfer-data,
request-download + transfer-data) so calibration reads and flash flows can be tested
end to end.

It is deliberately not a faithful model of any real control unit - just a
predictable peer that speaks the same wire protocol. Where the *real* VAG behaviour
is unverified (the login key algorithm, the extended-data record layout, which
routine ids are basic settings) the simulator's choice is its own and is documented
as such; the client side flags those mappings UNVERIFIED.
"""

from __future__ import annotations

import logging
import queue
from dataclasses import dataclass, field
from typing import Callable, Dict, FrozenSet, List, Optional, Tuple

from ..vag.sa2 import Sa2Interpreter
from .base import IsoTpLink

log = logging.getLogger(__name__)


# ------------------------------------------------------------------ fault model

@dataclass
class SimulatedFault:
    """One stored DTC with the records a VAG module keeps for it.

    ``snapshots`` maps snapshot record number -> ``[(did, data), ...]`` (0x19 0x04),
    ``extended`` maps extended record number -> data (0x19 0x06), ``fault_counter``
    is the 0x19 0x14 maturing counter (0 for a confirmed fault, 1..126 while maturing).
    """
    dtc: bytes
    status: int
    snapshots: Dict[int, List[Tuple[int, bytes]]] = field(default_factory=dict)
    extended: Dict[int, bytes] = field(default_factory=dict)
    fault_counter: int = 0

    @classmethod
    def default(cls, dtc: bytes, status: int, *, mileage_km: int = 123456,
                priority: int = 2, frequency: int = 1, aging: int = 40,
                speed_kmh: int = 0, voltage_mv: int = 14200,
                stamp: Tuple[int, int, int, int, int] = (24, 7, 17, 10, 42)) -> "SimulatedFault":
        """A realistic record set: snapshot record 1 with three DIDs of known size
        (0xF40D speed 1 byte, 0xF442 module voltage 2 bytes, 0x295A mileage 3 bytes)
        and five extended records (priority, frequency, aging counter, mileage, time).

        The *extended record layout* is the simulator's own (the real per-module
        layout is unverified: PROTOCOL_FACTS lists only the VCDS field names); the
        snapshot DIDs are real OBD-mirror / VAG DIDs with their verified sizes.
        """
        if len(dtc) != 3:
            raise ValueError("a DTC is 3 bytes")
        snapshots = {
            1: [
                (0xF40D, bytes([speed_kmh & 0xFF])),
                (0xF442, voltage_mv.to_bytes(2, "big")),
                (0x295A, mileage_km.to_bytes(3, "big")),
            ],
        }
        extended = {
            1: bytes([priority & 0xFF]),
            2: bytes([frequency & 0xFF]),
            3: bytes([aging & 0xFF]),
            4: mileage_km.to_bytes(3, "big"),
            5: bytes(stamp),
        }
        return cls(bytes(dtc), status, snapshots, extended)


# Sizes the simulator uses; tests feed these to the client as its size oracle.
SIM_SNAPSHOT_DID_SIZES: Dict[int, int] = {0xF40D: 1, 0xF442: 2, 0x295A: 3}
SIM_EXTENDED_RECORD_SIZES: Dict[int, int] = {1: 1, 2: 1, 3: 1, 4: 3, 5: 5}


@dataclass
class SimulatedIoChannel:
    """An output the tester can drive with 0x2F (one DID = one actuator)."""
    name: str
    default: bytes
    state: bytes = b""
    controlled: bool = False
    frozen: bool = False

    def __post_init__(self) -> None:
        if not self.state:
            self.state = self.default


@dataclass
class SimulatedRoutine:
    """A 0x31 routine: ``requires_unlock``/``sessions`` gate it; ``start_result`` is the
    status record returned by startRoutine (empty = none, like the VW_Flash capture
    ``31 01 02 03`` -> ``71 01 02 03``)."""
    rid: int
    name: str
    sessions: FrozenSet[int] = frozenset({0x02, 0x03, 0x4F})
    requires_unlock: bool = False
    start_result: bytes = b""
    result: bytes = b"\x00"
    state: str = "idle"          # idle | running | done
    runs: int = 0
    on_start: Optional[Callable[["SimulatedEcu", bytes], bytes]] = None


# IO / routine ids the demo ECU exposes. These numbers are the simulator's own; real
# VAG actuator DIDs and basic-setting routine ids live in each module's ODX.
SIM_IO_DID_DEMO = 0x1100                 # "demo actuator: boost control valve duty"
SIM_ROUTINE_BASIC_SETTING_A = 0x0203     # the one RID literally in VW_Flash testdata
SIM_ROUTINE_BASIC_SETTING_B = 0x0A1F     # arbitrary second basic setting
SIM_ROUTINE_ERASE = 0xFF00               # eraseMemory (ISO)
SIM_ROUTINE_CHECK_DEPENDENCIES = 0xFF01  # checkProgrammingDependencies (ISO)

NON_DEFAULT_SESSIONS: FrozenSet[int] = frozenset({0x02, 0x03, 0x4F})
DEFAULT_SESSION_GATES: Dict[int, FrozenSet[int]] = {
    0x2E: NON_DEFAULT_SESSIONS,
    0x2F: NON_DEFAULT_SESSIONS,
    0x31: NON_DEFAULT_SESSIONS,
    0x2C: NON_DEFAULT_SESSIONS,
    0x28: NON_DEFAULT_SESSIONS,
    0x85: NON_DEFAULT_SESSIONS,
    0x3D: NON_DEFAULT_SESSIONS,
    0x34: frozenset({0x02}),
}


class SimulatedEcu:
    """A scriptable UDS responder addressed at one pair of CAN IDs."""

    # A short, real SA2 script (from public SIMOS18 documentation) so the seed/key
    # path is exercised with genuine opcode semantics rather than a stub.
    DEFAULT_SA2 = bytes.fromhex(
        "6802814A10680493080820094A05872212195482499307122011824A058703112010824A0181494C"
    )
    DEFAULT_LOGIN_CODE = 12233   # a VCDS-documented engine login (injector adaptation)
    DYNAMIC_DID_RANGE = range(0xF200, 0xF300)

    def __init__(self) -> None:
        self.session = 0x01                       # default session
        self.security_unlocked = False            # the SA2 (flash) level, kept for 0.1.0 callers
        self.unlocked_levels: set = set()
        self._pending_seed: Optional[int] = None
        self._pending_level: Optional[int] = None
        self.sa2_script = self.DEFAULT_SA2
        # Fixed seed so tests are deterministic.
        self._seed_value = 0x1A2B3C4D
        # VCDS-style 5-digit login: level 0x03 (requestSeed) / 0x04 (sendKey) on this
        # simulator. The *real* coding level and key derivation are unverified; the
        # client warns. ``login_levels`` lists the odd requestSeed subfunctions that
        # use the login code instead of the SA2 script.
        self.login_code = self.DEFAULT_LOGIN_CODE
        self.login_levels: set = {0x03}
        self.coding_level = 0x03
        self.login_attempts = 0
        self.max_login_attempts = 3

        # Identification DIDs (ISO 14229 / VAG) -> response bytes. The VAG-specific
        # values mirror the VW_Flash Simos18 capture (shape, not a claim about any car).
        self.identifiers: Dict[int, bytes] = {
            0xF190: b"WVWZZZAUZLW000001",            # VIN
            0xF187: b"8V0906259H",                    # VW spare part number
            0xF189: b"0001",                          # application software version
            0xF191: b"03C906016AB",                   # ECU hardware number
            0xF1A3: b"H31",                           # hardware version
            0xF197: b"R4 2.0L TFSI",                  # system name / engine type
            0xF1AD: b"DGUA",                          # engine code letters
            0xF17C: b"ZSC-86415.07.18784303 20",      # FAZIT
            0xF18C: b"00000000000000",                # serial
            0xF19E: b"EV_ECM18TFS0208V0906264L\x00",  # ODX id
            0xF1A2: b"SC8_MQB_270",                   # ASAM/ODX file version
            0xF1DF: b"\x01",                          # programming information
            0xF1F4: b"MDG1  CB.06.031.5 013.00     ",  # bootloader id
            0x0600: bytes.fromhex("09190012242600 0E3004".replace(" ", "")),  # long coding (10 bytes)
            0xF1A5: bytes.fromhex("000003781FD7"),    # coding fingerprint (WSC + serial)
            0x0405: b"\x00",                          # state of flash memory
            0x0407: b"\x02",                          # programming attempts
            0x0408: b"\x02",                          # successful programming attempts
            0x295A: (123456).to_bytes(3, "big"),      # vehicle mileage (km)
            0x295B: (123456).to_bytes(3, "big"),      # module mileage (km)
            0xF15B: bytes.fromhex("200717420420 42B13D00".replace(" ", "")) * 5,  # programming log
            0xF198: b"\x00\x00\x00\x00\x00",          # repair shop code / tester serial
            0xF199: b"\x20\x07\x17",                  # programming date (BCD)
            0xF40D: b"\x00",                          # OBD mirror: vehicle speed
            0xF442: (14200).to_bytes(2, "big"),       # OBD mirror: module voltage (mV)
        }
        # DIDs a tester may write with 0x2E once logged in (coding and workshop data).
        self.writable_dids: set = {0x0600, 0xF198, 0xF199, 0xF1A5}
        # DIDs that exist but answer securityAccessDenied until any level is unlocked
        # (what a DID scan must classify as "present, refused" rather than absent).
        self.identifiers[0x12FC] = b"\x00\x00\x00\x00"
        self.locked_dids: set = {0x12FC}

        # Stored faults. ``dtcs`` (list of (3-byte DTC, status)) is the 0.1.0 view;
        # ``fault_dtcs`` carries snapshots / extended data / maturing counters.
        self.fault_dtcs: List[SimulatedFault] = [
            SimulatedFault.default(b"\x01\x12\x00", 0x2F),   # P0112, FTB 00, active+confirmed
            SimulatedFault.default(b"\x05\x61\x00", 0x09, priority=3, frequency=4),
        ]
        # DTCs the module *can* report (0x19 0x0A) beyond the stored ones.
        self.supported_dtcs: List[bytes] = [b"\x02\x99\x00", b"\x01\x01\x00", b"\xC1\x00\x00"]
        # A maturing fault for 0x19 0x14 (not yet stored).
        self.fault_counters: Dict[bytes, int] = {b"\x02\x99\x00": 0x40}

        # Outputs for 0x2F and routines for 0x31.
        self.io_channels: Dict[int, SimulatedIoChannel] = {
            SIM_IO_DID_DEMO: SimulatedIoChannel("boost control valve duty", default=b"\x00"),
        }
        self.routines: Dict[int, SimulatedRoutine] = {
            SIM_ROUTINE_BASIC_SETTING_A: SimulatedRoutine(
                SIM_ROUTINE_BASIC_SETTING_A, "basic setting A (throttle adaptation)",
                result=b"\x01\x00\x64"),   # done, 100 %
            SIM_ROUTINE_BASIC_SETTING_B: SimulatedRoutine(
                SIM_ROUTINE_BASIC_SETTING_B, "basic setting B (DPF regeneration request)",
                requires_unlock=False, result=b"\x02"),
            SIM_ROUTINE_ERASE: SimulatedRoutine(
                SIM_ROUTINE_ERASE, "eraseMemory", sessions=frozenset({0x02}),
                requires_unlock=True, on_start=_erase_cal),
            SIM_ROUTINE_CHECK_DEPENDENCIES: SimulatedRoutine(
                SIM_ROUTINE_CHECK_DEPENDENCIES, "checkProgrammingDependencies",
                sessions=frozenset({0x02}), requires_unlock=True, start_result=b"\x00"),
        }
        self.comm_control: int = 0          # last 0x28 controlType
        self.dtc_setting_on: bool = True    # 0x85
        self.dynamic_dids: Dict[int, List[Tuple[str, int, int, int]]] = {}  # did -> entries
        self.session_gates: Dict[int, FrozenSet[int]] = dict(DEFAULT_SESSION_GATES)
        self.reset_count = 0
        self.last_reset_type: Optional[int] = None

        # Memory is a set of regions, like a real ECU's address map:
        #   * a 64 KiB demo region at address 0 (simple tests, read-memory-by-address)
        #   * a 512 KiB "calibration" region at the SIMOS18.1 CAL block address, so
        #     the profile-driven read-cal flow hits the exact addresses a real car has.
        #     It is a bytearray so a download (flash write) can land in it.
        self.memory = bytes((i & 0xFF) for i in range(0x10000))
        self.cal_base = 0x80A8_0000
        self.cal_memory = bytearray(((i * 7 + 3) & 0xFF) for i in range(0x8_0000))
        self.regions: List[Tuple[int, bytes]] = [
            (0x0, self.memory),
            (self.cal_base, self.cal_memory),
        ]
        self._transfer_mode: Optional[str] = None   # "upload" | "download"
        self._upload_cursor = 0
        self._upload_remaining = 0
        self._upload_block_seq = 1

        self.custom_handlers: Dict[int, Callable[[bytes], bytes]] = {}

    # -- 0.1.0 compatibility view of the fault memory ----------------------------

    @property
    def dtcs(self) -> List[Tuple[bytes, int]]:
        return [(f.dtc, f.status) for f in self.fault_dtcs]

    @dtcs.setter
    def dtcs(self, value: List[Tuple[bytes, int]]) -> None:
        self.fault_dtcs = [SimulatedFault.default(bytes(d), s) for d, s in value]

    def fault(self, dtc: bytes) -> Optional[SimulatedFault]:
        for f in self.fault_dtcs:
            if f.dtc == dtc:
                return f
        return None

    def did_sizes(self) -> Dict[int, int]:
        """Size oracle for the client's multi-DID reads (what a label file would give)."""
        sizes = {did: len(v) for did, v in self.identifiers.items()}
        sizes[0xF186] = 1
        for did, entries in self.dynamic_dids.items():
            sizes[did] = sum(e[3] for e in entries)
        return sizes

    # -- memory --------------------------------------------------------------------

    def _slice(self, addr: int, size: int) -> bytes:
        """Return memory for [addr, addr+size) or raise requestOutOfRange."""
        for base, data in self.regions:
            if base <= addr and addr + size <= base + len(data):
                off = addr - base
                return bytes(data[off:off + size])
        raise _Nrc(0x31)

    def _write(self, addr: int, chunk: bytes) -> None:
        for base, data in self.regions:
            if base <= addr and addr + len(chunk) <= base + len(data):
                if not isinstance(data, bytearray):
                    raise _Nrc(0x72)   # generalProgrammingFailure: region is read-only
                off = addr - base
                data[off:off + len(chunk)] = chunk
                return
        raise _Nrc(0x31)

    # -- security ----------------------------------------------------------------

    def _seed(self) -> bytes:
        self._pending_seed = self._seed_value
        return self._seed_value.to_bytes(4, "big")

    def _expected_key(self) -> int:
        interp = Sa2Interpreter(self.sa2_script)
        return interp.compute_key(self._pending_seed)

    @staticmethod
    def login_key(seed: bytes, code: int) -> bytes:
        """The simulator's seed -> key rule for the 5-digit login levels.

        This is NOT a claim about any real module (the real derivation is unverified,
        PROTOCOL_FACTS uds_vag.md §O / REPORTED); it only gives the client something
        deterministic to compute against. ``vagtune.vag.ecu.login_seed_key_fn``
        implements the same rule and is flagged UNVERIFIED there.
        """
        n = len(seed) or 4
        value = (int.from_bytes(seed, "big") + (code & 0xFFFF)) & ((1 << (8 * n)) - 1)
        return value.to_bytes(n, "big")

    def _relock(self) -> None:
        self.security_unlocked = False
        self.unlocked_levels.clear()
        self._pending_seed = None
        self._pending_level = None

    # -- request dispatch --------------------------------------------------------

    def handle(self, request: bytes) -> Optional[bytes]:
        """Map a UDS request to a response (or ``None`` to stay silent)."""
        if not request:
            return None
        sid = request[0]
        if sid in self.custom_handlers:
            return self.custom_handlers[sid](request)
        try:
            gate = self.session_gates.get(sid)
            if gate is not None and self.session not in gate:
                raise _Nrc(0x7F)   # serviceNotSupportedInActiveSession
            if sid == 0x10:    # DiagnosticSessionControl
                return self._svc_session(request)
            if sid == 0x11:    # ECUReset
                return self._svc_reset(request)
            if sid == 0x3E:    # TesterPresent
                suppress = len(request) > 1 and (request[1] & 0x80)
                return None if suppress else bytes([0x7E, request[1] if len(request) > 1 else 0x00])
            if sid == 0x22:    # ReadDataByIdentifier (single or multi)
                return self._svc_read_did(request)
            if sid == 0x2E:    # WriteDataByIdentifier
                return self._svc_write_did(request)
            if sid == 0x27:    # SecurityAccess
                return self._svc_security(request)
            if sid == 0x19:    # ReadDTCInformation
                return self._svc_read_dtc(request)
            if sid == 0x14:    # ClearDiagnosticInformation
                if len(request) != 4:
                    raise _Nrc(0x13)
                self.fault_dtcs.clear()
                return bytes([0x54])
            if sid == 0x23:    # ReadMemoryByAddress
                return self._svc_read_memory(request)
            if sid == 0x2F:    # InputOutputControlByIdentifier
                return self._svc_io_control(request)
            if sid == 0x31:    # RoutineControl
                return self._svc_routine(request)
            if sid == 0x28:    # CommunicationControl
                return self._svc_comm_control(request)
            if sid == 0x85:    # ControlDTCSetting
                return self._svc_dtc_setting(request)
            if sid == 0x2C:    # DynamicallyDefineDataIdentifier
                return self._svc_dynamic_did(request)
            if sid == 0x34:    # RequestDownload
                return self._svc_request_download(request)
            if sid == 0x35:    # RequestUpload
                return self._svc_request_upload(request)
            if sid == 0x36:    # TransferData
                return self._svc_transfer_data(request)
            if sid == 0x37:    # RequestTransferExit
                self._transfer_mode = None
                return bytes([0x77])
        except _Nrc as nrc:
            return bytes([0x7F, sid, nrc.code])
        return bytes([0x7F, sid, 0x11])  # serviceNotSupported

    # -- 0x10 / 0x11 -------------------------------------------------------------

    def _svc_session(self, request: bytes) -> Optional[bytes]:
        if len(request) < 2:
            raise _Nrc(0x13)
        sub = request[1]
        session = sub & 0x7F
        if session not in (0x01, 0x02, 0x03, 0x04, 0x4F):
            raise _Nrc(0x12)
        if session == 0x02 and self.session == 0x01:
            # VAG modules are put into programming via extended (VW_Flash: 10 03, 10 02).
            raise _Nrc(0x7E)   # subFunctionNotSupportedInActiveSession
        if session != self.session:
            self._relock()      # ISO 14229: a session transition resets security access
        self.session = session
        if sub & 0x80:
            return None
        # P2 (ms) and P2* (10 ms units), both 16-bit big-endian: 50 ms / 5000 ms.
        return bytes([0x50, session, 0x00, 0x32, 0x01, 0xF4])

    def _svc_reset(self, request: bytes) -> Optional[bytes]:
        if len(request) < 2:
            raise _Nrc(0x13)
        sub = request[1]
        kind = sub & 0x7F
        if kind not in (0x01, 0x02, 0x03, 0x04, 0x05):
            raise _Nrc(0x12)
        if kind in (0x04, 0x05) and self.session == 0x01:
            raise _Nrc(0x7E)
        self.reset_count += 1
        self.last_reset_type = kind
        if kind in (0x01, 0x02, 0x03):
            # Power cycle: default session, relocked, volatile state gone.
            self.session = 0x01
            self._relock()
            self.dynamic_dids.clear()
            self._transfer_mode = None
            for ch in self.io_channels.values():
                ch.state, ch.controlled, ch.frozen = ch.default, False, False
            for r in self.routines.values():
                r.state = "idle"
        if sub & 0x80:
            return None
        if kind == 0x04:
            return bytes([0x51, kind, 0x0A])   # powerDownTime 10 s
        return bytes([0x51, kind])

    # -- 0x22 / 0x2E -------------------------------------------------------------

    def _did_value(self, did: int) -> Optional[bytes]:
        if did == 0xF186:
            return bytes([self.session])
        if did in self.dynamic_dids:
            out = bytearray()
            for kind, a, b, size in self.dynamic_dids[did]:
                if kind == "mem":
                    out += self._slice(a, size)
                else:
                    src = self._did_value(a) or b""
                    out += src[b - 1:b - 1 + size]
            return bytes(out)
        return self.identifiers.get(did)

    def _svc_read_did(self, request: bytes) -> bytes:
        if len(request) < 3 or (len(request) - 1) % 2:
            raise _Nrc(0x13)
        dids = [(request[i] << 8) | request[i + 1] for i in range(1, len(request), 2)]
        body = bytearray([0x62])
        found = 0
        for did in dids:
            if did in self.locked_dids and not self.unlocked_levels:
                if len(dids) == 1:
                    raise _Nrc(0x33)   # securityAccessDenied: exists, but not for you yet
                continue
            value = self._did_value(did)
            if value is None:
                continue
            found += 1
            body += bytes([(did >> 8) & 0xFF, did & 0xFF]) + value
        if not found:
            raise _Nrc(0x31)  # requestOutOfRange: none of the DIDs exist here
        return bytes(body)

    def _svc_write_did(self, request: bytes) -> bytes:
        if len(request) < 4:
            raise _Nrc(0x13)
        did = (request[1] << 8) | request[2]
        data = request[3:]
        if did not in self.writable_dids or did not in self.identifiers:
            raise _Nrc(0x31)
        if did == 0x0600:
            if self.coding_level not in self.unlocked_levels:
                raise _Nrc(0x33)   # securityAccessDenied: login first
            if len(data) != len(self.identifiers[0x0600]):
                raise _Nrc(0x13)
        elif not self.unlocked_levels:
            raise _Nrc(0x33)
        self.identifiers[did] = bytes(data)
        return bytes([0x6E, request[1], request[2]])

    # -- 0x27 --------------------------------------------------------------------

    def _svc_security(self, request: bytes) -> bytes:
        if len(request) < 2:
            raise _Nrc(0x13)
        sub = request[1]
        level = sub if sub % 2 == 1 else sub - 1
        if sub % 2 == 1:          # requestSeed (odd subfunction)
            if level in self.unlocked_levels:
                return bytes([0x67, sub, 0x00, 0x00, 0x00, 0x00])  # already unlocked -> zero seed
            if level in self.login_levels and self.login_attempts >= self.max_login_attempts:
                raise _Nrc(0x37)  # requiredTimeDelayNotExpired (lockout)
            self._pending_level = level
            return bytes([0x67, sub]) + self._seed()
        # sendKey (even subfunction)
        if self._pending_seed is None or self._pending_level != level:
            raise _Nrc(0x24)  # requestSequenceError
        key = request[2:]
        if level in self.login_levels:
            expected = self.login_key(self._pending_seed.to_bytes(4, "big"), self.login_code)
            ok = key == expected
            if not ok:
                self.login_attempts += 1
        else:
            ok = len(key) == 4 and int.from_bytes(key, "big") == self._expected_key()
        if ok:
            self.unlocked_levels.add(level)
            if level not in self.login_levels:
                self.security_unlocked = True
            self._pending_seed = None
            self._pending_level = None
            return bytes([0x67, sub])
        self._pending_seed = None
        self._pending_level = None
        if level in self.login_levels and self.login_attempts >= self.max_login_attempts:
            raise _Nrc(0x36)  # exceedNumberOfAttempts
        raise _Nrc(0x35)      # invalidKey

    # -- 0x19 --------------------------------------------------------------------

    def _svc_read_dtc(self, request: bytes) -> bytes:
        if len(request) < 2:
            raise _Nrc(0x13)
        sub = request[1] & 0x7F
        if sub == 0x01:
            if len(request) < 3:
                raise _Nrc(0x13)
            count = sum(1 for f in self.fault_dtcs if f.status & request[2])
            return bytes([0x59, 0x01, 0xFF, 0x01]) + count.to_bytes(2, "big")
        if sub == 0x02:
            if len(request) < 3:
                raise _Nrc(0x13)
            mask = request[2]
            body = bytearray([0x59, 0x02, 0xFF])  # echo availability mask
            for f in self.fault_dtcs:
                if f.status & mask:
                    body += f.dtc + bytes([f.status])
            return bytes(body)
        if sub == 0x03:
            body = bytearray([0x59, 0x03])
            for f in self.fault_dtcs:
                for rec in sorted(f.snapshots):
                    body += f.dtc + bytes([rec])
            return bytes(body)
        if sub in (0x04, 0x06):
            if len(request) != 6:
                raise _Nrc(0x13)
            dtc, rec_no = request[2:5], request[5]
            f = self.fault(dtc)
            if f is None:
                raise _Nrc(0x31)
            body = bytearray([0x59, sub]) + f.dtc + bytes([f.status])
            if sub == 0x04:
                for rec in sorted(f.snapshots):
                    if rec_no in (0xFF, rec):
                        dids = f.snapshots[rec]
                        body += bytes([rec, len(dids)])
                        for did, value in dids:
                            body += bytes([(did >> 8) & 0xFF, did & 0xFF]) + value
            else:
                for rec in sorted(f.extended):
                    if rec_no in (0xFF, 0xFE, rec):
                        body += bytes([rec]) + f.extended[rec]
            return bytes(body)
        if sub == 0x0A:
            body = bytearray([0x59, 0x0A, 0xFF])
            seen = set()
            for f in self.fault_dtcs:
                body += f.dtc + bytes([f.status])
                seen.add(f.dtc)
            for dtc in self.supported_dtcs:
                if dtc not in seen:
                    body += dtc + bytes([0x50])   # never failed, test not completed
                    seen.add(dtc)
            return bytes(body)
        if sub == 0x14:
            body = bytearray([0x59, 0x14])
            for dtc, counter in self.fault_counters.items():
                body += dtc + bytes([counter & 0xFF])
            return bytes(body)
        raise _Nrc(0x12)

    # -- 0x23 --------------------------------------------------------------------

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

    # -- 0x2F --------------------------------------------------------------------

    def _svc_io_control(self, request: bytes) -> bytes:
        if len(request) < 4:
            raise _Nrc(0x13)
        did = (request[1] << 8) | request[2]
        option = request[3]
        state = request[4:]
        ch = self.io_channels.get(did)
        if ch is None or option > 0x03:
            raise _Nrc(0x31)
        if option == 0x00:        # returnControlToECU
            ch.state, ch.controlled, ch.frozen = ch.default, False, False
        elif option == 0x01:      # resetToDefault
            ch.state = ch.default
        elif option == 0x02:      # freezeCurrentState
            ch.frozen = True
        else:                     # shortTermAdjustment = the output test
            if len(state) != len(ch.default):
                raise _Nrc(0x13)
            ch.state, ch.controlled = bytes(state), True
        return bytes([0x6F, request[1], request[2], option]) + ch.state

    # -- 0x31 --------------------------------------------------------------------

    def _svc_routine(self, request: bytes) -> Optional[bytes]:
        if len(request) < 4:
            raise _Nrc(0x13)
        sub = request[1]
        control = sub & 0x7F
        rid = (request[2] << 8) | request[3]
        options = request[4:]
        if control not in (0x01, 0x02, 0x03):
            raise _Nrc(0x12)
        routine = self.routines.get(rid)
        if routine is None:
            raise _Nrc(0x31)
        if self.session not in routine.sessions:
            raise _Nrc(0x7E)
        if routine.requires_unlock and not self.unlocked_levels:
            raise _Nrc(0x33)
        head = bytes([0x71, control, request[2], request[3]])
        if control == 0x01:
            routine.state = "running"
            routine.runs += 1
            result = routine.on_start(self, options) if routine.on_start else routine.start_result
            if routine.on_start:
                routine.state = "done"
            return None if sub & 0x80 else head + result
        if control == 0x02:
            if routine.state != "running":
                raise _Nrc(0x24)
            routine.state = "done"
            return None if sub & 0x80 else head
        if routine.state == "idle":
            raise _Nrc(0x24)   # results before start
        return head + routine.result

    # -- 0x28 / 0x85 -------------------------------------------------------------

    def _svc_comm_control(self, request: bytes) -> Optional[bytes]:
        if len(request) < 3:
            raise _Nrc(0x13)
        sub = request[1]
        control = sub & 0x7F
        if control > 0x05:
            raise _Nrc(0x12)
        if control in (0x04, 0x05) and len(request) != 5:
            raise _Nrc(0x13)
        if control not in (0x04, 0x05) and len(request) != 3:
            raise _Nrc(0x13)
        self.comm_control = control
        return None if sub & 0x80 else bytes([0x68, control])

    def _svc_dtc_setting(self, request: bytes) -> Optional[bytes]:
        if len(request) < 2:
            raise _Nrc(0x13)
        sub = request[1]
        setting = sub & 0x7F
        if setting not in (0x01, 0x02):
            raise _Nrc(0x12)
        self.dtc_setting_on = setting == 0x01
        return None if sub & 0x80 else bytes([0xC5, setting])

    # -- 0x2C --------------------------------------------------------------------

    def _svc_dynamic_did(self, request: bytes) -> bytes:
        if len(request) < 2:
            raise _Nrc(0x13)
        sub = request[1] & 0x7F
        if sub == 0x03 and len(request) == 2:
            self.dynamic_dids.clear()
            return bytes([0x6C, 0x03])
        if len(request) < 4:
            raise _Nrc(0x13)
        dyn = (request[2] << 8) | request[3]
        if dyn not in self.DYNAMIC_DID_RANGE:
            raise _Nrc(0x31)
        if sub == 0x03:
            self.dynamic_dids.pop(dyn, None)
            return bytes([0x6C, 0x03, request[2], request[3]])
        entries: List[Tuple[str, int, int, int]] = []
        if sub == 0x02:
            if len(request) < 5:
                raise _Nrc(0x13)
            alfid = request[4]
            size_len, addr_len = (alfid >> 4) & 0xF, alfid & 0xF
            if not size_len or not addr_len:
                raise _Nrc(0x13)
            body = request[5:]
            step = addr_len + size_len
            if not body or len(body) % step:
                raise _Nrc(0x13)
            for i in range(0, len(body), step):
                addr = int.from_bytes(body[i:i + addr_len], "big")
                size = int.from_bytes(body[i + addr_len:i + step], "big")
                self._slice(addr, size)   # validates (0x31 when out of range)
                entries.append(("mem", addr, 0, size))
        elif sub == 0x01:
            body = request[4:]
            if not body or len(body) % 4:
                raise _Nrc(0x13)
            for i in range(0, len(body), 4):
                src = (body[i] << 8) | body[i + 1]
                position, size = body[i + 2], body[i + 3]
                value = self._did_value(src)
                if value is None or position < 1 or position - 1 + size > len(value):
                    raise _Nrc(0x31)
                entries.append(("did", src, position, size))
        else:
            raise _Nrc(0x12)
        self.dynamic_dids[dyn] = entries
        return bytes([0x6C, sub, request[2], request[3]])

    # -- 0x34 / 0x35 / 0x36 ------------------------------------------------------

    def _parse_transfer_request(self, request: bytes) -> Tuple[int, int]:
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
        return addr, size

    def _svc_request_upload(self, request: bytes) -> bytes:
        if not self.security_unlocked:
            raise _Nrc(0x33)  # securityAccessDenied
        addr, size = self._parse_transfer_request(request)
        self._transfer_mode = "upload"
        self._upload_cursor = addr
        self._upload_remaining = size
        self._upload_block_seq = 1
        # lengthFormatIdentifier = 2, then maxNumberOfBlockLength (0x0102 = 258 incl. SID+seq).
        return bytes([0x75, 0x20, 0x01, 0x02])

    def _svc_request_download(self, request: bytes) -> bytes:
        if not self.security_unlocked:
            raise _Nrc(0x33)
        addr, size = self._parse_transfer_request(request)
        self._transfer_mode = "download"
        self._upload_cursor = addr
        self._upload_remaining = size
        self._upload_block_seq = 1
        return bytes([0x74, 0x20, 0x01, 0x02])

    def _svc_transfer_data(self, request: bytes) -> bytes:
        if len(request) < 2:
            raise _Nrc(0x13)
        if self._transfer_mode is None:
            raise _Nrc(0x24)
        seq = request[1]
        if seq != (self._upload_block_seq & 0xFF):
            raise _Nrc(0x73)  # wrongBlockSequenceCounter
        if self._upload_remaining <= 0:
            raise _Nrc(0x31)
        if self._transfer_mode == "upload":
            chunk_len = min(255, self._upload_remaining)
            chunk = self._slice(self._upload_cursor, chunk_len)
        else:
            chunk = request[2:]
            if not chunk or len(chunk) > 256 or len(chunk) > self._upload_remaining:
                raise _Nrc(0x13)
            self._write(self._upload_cursor, chunk)
            chunk_len = len(chunk)
            chunk = b""
        self._upload_cursor += chunk_len
        self._upload_remaining -= chunk_len
        self._upload_block_seq = (self._upload_block_seq + 1) & 0xFF
        return bytes([0x76, seq]) + chunk


def _erase_cal(ecu: SimulatedEcu, options: bytes) -> bytes:
    """eraseMemory routine: blank the calibration region (0xFF) like a flash erase."""
    for i in range(len(ecu.cal_memory)):
        ecu.cal_memory[i] = 0xFF
    return b"\x00"


class _Nrc(Exception):
    def __init__(self, code: int) -> None:
        super().__init__(f"NRC 0x{code:02X}")
        self.code = code


class FakeIsoTpLink(IsoTpLink):
    """An ISO-TP link whose ``send`` is answered synchronously by a SimulatedEcu.

    ``sent`` records every payload handed to the ECU so tests can check framing
    byte for byte.
    """

    def __init__(self, tx_id: int, rx_id: int, ecu: SimulatedEcu) -> None:
        super().__init__(tx_id, rx_id)
        self.ecu = ecu
        self._inbox: "queue.Queue[bytes]" = queue.Queue()
        self.sent: List[bytes] = []

    def send(self, payload: bytes) -> None:
        self.sent.append(bytes(payload))
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
