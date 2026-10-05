"""
KWP2000 (ISO 14230-3) service ids, VAG session ids, identification options and the
complete KWP negative-response-code table.

Everything here is copied from ``docs/PROTOCOL_FACTS.md`` §4 (ISO 14230-3 Table 4.3 /
Table 4.4 and the fetched VAG tools) and §7.5 / §7.10 for the VAG specifics:

* A KWP2000 message over TP 2.0 is ``SID [parameters...]`` - no format byte, no
  address bytes, no checksum (those exist only on K-line). The positive response SID
  is ``SID + 0x40``; a negative response is ``7F <request SID> <NRC>``.
* VAG opens every module with ``10 89`` ("standard diagnostic session", verified on
  every fetched tool and two real traces); the other session values below are listed
  for *recognition only* (seen in code / traces, not needed for diagnostics).
* ``1A <option>`` identification options as the fetched tools use them (``9B`` is the
  one everyone decodes; ``91`` is the fallback; ``9F`` is the gateway list).
* The NRC table is ISO 14230-3 Table 4.4 verbatim. The UDS-only codes PyVCDS carries
  (0x13, 0x14, 0x24, 0x25, 0x70, 0x73, 0x7E, 0x7F, 0x80) are deliberately **not**
  KWP2000 codes ("KWP2000 has no such thing, it can only ever send 0x11" for a wrong
  session) and are excluded; :func:`nrc_name` names them by their ISO range instead.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Dict, FrozenSet, Optional, Set

log = logging.getLogger(__name__)

# ------------------------------------------------------------------ UNVERIFIED warnings

_unverified_warned: Set[str] = set()
_unverified_lock = threading.Lock()


def warn_unverified(key: str, message: str) -> None:
    """Log ``UNVERIFIED mapping: <message>`` once per process for ``key``.

    The same helper as :func:`vagtune.vag.dtc.warn_unverified`, duplicated here
    because ``kwp`` sits below ``vag`` in the layer map and may not import it.
    """
    with _unverified_lock:
        if key in _unverified_warned:
            return
        _unverified_warned.add(key)
    log.warning("UNVERIFIED mapping: %s", message)


def _reset_unverified_warnings() -> None:   # tests only
    with _unverified_lock:
        _unverified_warned.clear()


# ------------------------------------------------------------------ message model

NEGATIVE_RESPONSE_SID = 0x7F
POSITIVE_RESPONSE_OFFSET = 0x40


def positive_sid(sid: int) -> int:
    """Request SID -> positive response SID (``SID + 0x40``, verified)."""
    return (sid + POSITIVE_RESPONSE_OFFSET) & 0xFF


# ------------------------------------------------------------------ service ids


class Service:
    """ISO 14230-3 service identifiers (Table 4.3 plus the ids the fetched VAG tools
    list: PyVCDS ``requests`` and pq-flasher ``SERVICE_TYPE``)."""

    START_DIAGNOSTIC_SESSION = 0x10
    ECU_RESET = 0x11
    READ_FREEZE_FRAME_DATA = 0x12
    READ_DIAGNOSTIC_TROUBLE_CODES = 0x13
    CLEAR_DIAGNOSTIC_INFORMATION = 0x14
    READ_STATUS_OF_DTC = 0x17
    READ_DTC_BY_STATUS = 0x18
    READ_ECU_IDENTIFICATION = 0x1A
    STOP_DIAGNOSTIC_SESSION = 0x20
    READ_DATA_BY_LOCAL_ID = 0x21
    READ_DATA_BY_COMMON_ID = 0x22
    READ_MEMORY_BY_ADDRESS = 0x23
    SET_DATA_RATES = 0x26
    SECURITY_ACCESS = 0x27
    DYNAMICALLY_DEFINE_LOCAL_ID = 0x2C
    WRITE_DATA_BY_COMMON_ID = 0x2E
    IO_CONTROL_BY_COMMON_ID = 0x2F
    IO_CONTROL_BY_LOCAL_ID = 0x30
    START_ROUTINE_BY_LOCAL_ID = 0x31
    STOP_ROUTINE_BY_LOCAL_ID = 0x32
    REQUEST_ROUTINE_RESULTS_BY_LOCAL_ID = 0x33
    REQUEST_DOWNLOAD = 0x34
    REQUEST_UPLOAD = 0x35
    TRANSFER_DATA = 0x36
    REQUEST_TRANSFER_EXIT = 0x37
    START_ROUTINE_BY_ADDRESS = 0x38
    STOP_ROUTINE_BY_ADDRESS = 0x39
    REQUEST_ROUTINE_RESULTS_BY_ADDRESS = 0x3A
    WRITE_DATA_BY_LOCAL_ID = 0x3B
    WRITE_MEMORY_BY_ADDRESS = 0x3D
    TESTER_PRESENT = 0x3E
    ESC_CODE = 0x80
    STOP_COMMUNICATION = 0x82


SERVICE_NAMES: Dict[int, str] = {
    0x10: "startDiagnosticSession",
    0x11: "ecuReset",
    0x12: "readFreezeFrameData",
    0x13: "readDiagnosticTroubleCodes",
    0x14: "clearDiagnosticInformation",
    0x17: "readStatusOfDiagnosticTroubleCodes",
    0x18: "readDiagnosticTroubleCodesByStatus",
    0x1A: "readEcuIdentification",
    0x20: "stopDiagnosticSession",
    0x21: "readDataByLocalIdentifier",
    0x22: "readDataByCommonIdentifier",
    0x23: "readMemoryByAddress",
    0x26: "setDataRates",
    0x27: "securityAccess",
    0x2C: "dynamicallyDefineLocalIdentifier",
    0x2E: "writeDataByCommonIdentifier",
    0x2F: "inputOutputControlByCommonIdentifier",
    0x30: "inputOutputControlByLocalIdentifier",
    0x31: "startRoutineByLocalIdentifier",
    0x32: "stopRoutineByLocalIdentifier",
    0x33: "requestRoutineResultsByLocalIdentifier",
    0x34: "requestDownload",
    0x35: "requestUpload",
    0x36: "transferData",
    0x37: "requestTransferExit",
    0x38: "startRoutineByAddress",
    0x39: "stopRoutineByAddress",
    0x3A: "requestRoutineResultsByAddress",
    0x3B: "writeDataByLocalIdentifier",
    0x3D: "writeMemoryByAddress",
    0x3E: "testerPresent",
    0x80: "escCode",
    0x82: "stopCommunication",
}


def service_name(sid: int) -> str:
    return SERVICE_NAMES.get(sid, f"service 0x{sid:02X}")


# Services that are reflashing / immobiliser material: listed so sniffed traffic can
# be named, never sent by this toolkit (PROTOCOL_FACTS scope note).
OUT_OF_SCOPE_SERVICES: FrozenSet[int] = frozenset({0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x3D})


# ------------------------------------------------------------------ sessions

#: ``10 89`` -> ``50 89``: VAG "standard diagnostic session". Verified on every fetched
#: tool (vag-blocks, PyVCDS, pq-flasher, teensy, DV, scirocco-dash, OpenHaldex,
#: speedPulserPro) and on two real traces (NefMoto engine, ICH EPS). Repeating it is
#: harmless (the EPS answered ``50 89`` twice).
SESSION_STANDARD_DIAGNOSTIC = 0x89

#: Seen in fetched code / traces; listed for recognition only. Nothing in this
#: toolkit sends them (programming and development sessions are out of scope).
SESSION_PROGRAMMING = 0x85          # pq-flasher SESSION_TYPE.PROGRAMMING, PyVCDS "PROG"
SESSION_ENGINEERING = 0x86          # pq-flasher ENGINEERING_MODE; ME7 "development"
SESSION_ME7_DEFAULT = 0x81          # me7-logger SessionDefault (ME7 stock session)


@dataclass(frozen=True)
class SessionInfo:
    value: int
    name: str
    used_by_toolkit: bool
    note: str


SESSIONS: Dict[int, SessionInfo] = {
    0x89: SessionInfo(0x89, "standardDiagnostic (VAG)", True,
                      "the only session this toolkit opens; verified on traces and every tool"),
    0x85: SessionInfo(0x85, "programming", False, "pq-flasher / PyVCDS; flashing - out of scope"),
    0x86: SessionInfo(0x86, "engineering / development", False,
                      "pq-flasher, NefMoto ME7 posts; refused on ME7.1.1 without level-1 access"),
    0x81: SessionInfo(0x81, "ME7 default", False, "me7-logger SessionDefault; recognition only"),
}

#: ``10 84 14`` is a two-parameter session kw1281-can-extension sends to a VDO cluster
#: before reading its EEPROM (immobiliser related, out of scope). Recognition only.
SESSION_REQUEST_IMMO_CLUSTER = bytes([0x10, 0x84, 0x14])


def session_name(value: int) -> str:
    info = SESSIONS.get(value)
    return info.name if info else f"session 0x{value:02X} (unknown)"


# ------------------------------------------------------------------ identification


@dataclass(frozen=True)
class IdentOption:
    option: int
    name: str
    users: str
    decoded: bool   # True when this toolkit has a byte-exact parser for the reply


#: ``1A <option>`` options as named by the fetched tools (PROTOCOL_FACTS §7.5).
IDENT_OPTIONS: Dict[int, IdentOption] = {
    0x86: IdentOption(0x86, "extended ident", "PyVCDS kwp_trace, PoloCornering, scirocco-dash", False),
    0x87: IdentOption(0x87, "probed (no decode)", "scirocco-dash ident_dump", False),
    0x88: IdentOption(0x88, "probed (no decode)", "scirocco-dash ident_dump", False),
    0x89: IdentOption(0x89, "probed (no decode)", "scirocco-dash ident_dump", False),
    0x8A: IdentOption(0x8A, "probed (no decode)", "scirocco-dash ident_dump", False),
    0x90: IdentOption(0x90, "ISO vehicleIdentificationNumber", "scirocco-dash (VIN first try)", False),
    0x91: IdentOption(0x91, "hardware number / VAG number (length-prefixed records)",
                      "vag-blocks, PyVCDS, DV, vag-diag-sim, scirocco-dash", True),
    0x92: IdentOption(0x92, "system supplier hardware id", "PyVCDS, bri3d", False),
    0x94: IdentOption(0x94, "system supplier software id", "PyVCDS, scirocco-dash", False),
    0x95: IdentOption(0x95, "probed (no decode)", "scirocco-dash", False),
    0x96: IdentOption(0x96, "probed (no decode)", "scirocco-dash", False),
    0x97: IdentOption(0x97, "probed (no decode)", "scirocco-dash", False),
    0x9A: IdentOption(0x9A, "long coding record (layout REPORTED)", "PyVCDS, vag-diag-sim, PoloCornering", True),
    0x9B: IdentOption(0x9B, "standard identification (part no, sw, coding, WSC, component)",
                      "everyone", True),
    0x9C: IdentOption(0x9C, "flash status", "PyVCDS, pq-flasher", False),
    0x9F: IdentOption(0x9F, "gateway installation list (layout REPORTED)", "vag-blocks, DV, PoloCornering", True),
}

IDENT_STANDARD = 0x9B
IDENT_HARDWARE_NUMBER = 0x91
IDENT_LONG_CODING = 0x9A
IDENT_INSTALLATION_LIST = 0x9F

#: Coding-type byte at offset 16 of the ``5A 9B`` record (DV comment, three real dumps).
CODING_TYPE_NONE = 0x00
CODING_TYPE_SHORT = 0x03
CODING_TYPE_LONG = 0x10
CODING_TYPE_NAMES: Dict[int, str] = {0x00: "no coding", 0x03: "short coding", 0x10: "long coding"}


# ------------------------------------------------------------------ fault codes

#: ``18 <status> <group hi> <group lo>``: VAG sends status 0x02 / group 0xFF00 first and
#: falls back to status 0x00 (PyVCDS, scirocco-dash, bri3d, NefMoto ME7 post).
DTC_GROUP_ALL = 0xFF00
DTC_STATUS_VAG = 0x02
DTC_STATUS_ALL = 0x00
#: DV ``readFaultCodes_getSupportedFaultCodes``; reply layout REPORTED (medium).
DTC_STATUS_SUPPORTED = 0x03

#: ``14 FF 00`` -> ``54 FF 00`` (DV emulator, bri3d, scirocco-dash).
CLEAR_GROUP_ALL = 0xFF00

#: KWP2000 fault status byte as VCDS prints it on TP 2.0 modules (verified from 21
#: real records): low nibble = elaboration code, bit 6 clear = intermittent.
DTC_STATUS_ELABORATION_MASK = 0x0F
DTC_STATUS_BIT4 = 0x10          # semantics REPORTED (DV forces it on)
DTC_STATUS_BIT5_STORED = 0x20   # set in every real record; "wasPresent" (bri3d) - REPORTED
DTC_STATUS_BIT6_PRESENT = 0x40  # clear <=> VCDS "Intermittent" (verified on 21 records)
DTC_STATUS_BIT7_MIL = 0x80      # bri3d "isCEL"; never seen on a KWP2000 record - REPORTED


# ------------------------------------------------------------------ routines (0x31)

#: ``31 B8 00 00`` -> ``71 B8`` + 16-bit function codes (real PQ35 engine, DV, VDS).
ROUTINE_FUNCTION_START = 0xB8
ROUTINE_FUNCTION_SELECT = 0xB9      # ``31 B9 01 03 <ch>`` (bri3d adaptation) - REPORTED model
ROUTINE_FUNCTION_READ = 0xBA        # ``31 BA 01 03`` - REPORTED model
ROUTINE_FUNCTION_SAVE = 0xBB        # ``31 BB 01 03 <value> <wsc6>`` - WRITE, never sent here
CAPABILITY_QUERY_FUNCTION = 0x0000


@dataclass(frozen=True)
class CapabilityCode:
    code: int
    name: str
    verified: bool
    source: str


#: 16-bit codes in the ``71 B8`` capability reply (DV responses.h documentation; the
#: real 1K0907115L engine advertised 0101 0103 0102 0106 0107 0108 010D 0118).
CAPABILITY_CODES: Dict[int, CapabilityCode] = {
    0x0000: CapabilityCode(0x0000, "no function supported", True, "DV responses.h"),
    0x0101: CapabilityCode(0x0101, "basic settings in KWP1281 mode", True, "DV responses.h; real engine"),
    0x0102: CapabilityCode(0x0102, "output tests with fixed sequence in KWP1281 mode", True,
                           "DV responses.h; real engine"),
    0x0103: CapabilityCode(0x0103, "adaptation", False,
                           "absent from DV's list; advertised by the real engine and used by bri3d as 01 03"),
    0x0104: CapabilityCode(0x0104, "20-bit coding possible", True, "DV responses.h"),
    0x0105: CapabilityCode(0x0105, "Coding-II possible (VCDS Login)", True, "DV responses.h"),
    0x0106: CapabilityCode(0x0106, "reading measuring blocks in KWP1281 mode", True, "DV responses.h; real engine"),
    0x0107: CapabilityCode(0x0107, "output tests with selective (non-fixed) sequence", True,
                           "DV responses.h; real engine"),
    0x0108: CapabilityCode(0x0108, "developer functions possible", True, "DV responses.h; real engine"),
    0x010D: CapabilityCode(0x010D, "immobilizer Gen4 supported", True, "DV responses.h; real engine"),
    0x0118: CapabilityCode(0x0118, "HEX-coded fault codes supported", True, "DV responses.h; real engine"),
}


def capability_name(code: int) -> str:
    """Human name of a ``71 B8`` capability code.

    Rows with ``verified=False`` are REPORTED meanings (today only 0x0103
    "adaptation": absent from DV's documented list, inferred from the real engine
    advertising it and bri3d's use of ``01 03`` as the adaptation function). Their
    text is suffixed ``(REPORTED)`` and warns once per process; it only ever labels
    output, nothing writes on the strength of it.
    """
    row = CAPABILITY_CODES.get(code)
    if row is None:
        return f"function 0x{code:04X} (not in table)"
    if row.verified:
        return row.name
    # UNVERIFIED: meaning of capability code 0x0103 (registry 7.10: not in DV's list; bri3d's 01 03).
    warn_unverified(f"capability-code:{code:04X}",
                    f"capability code {code:04X} shown as {row.name!r} is REPORTED ({row.source}); "
                    "confirm against the VCDS function list of a module that advertises it")
    return f"{row.name} (REPORTED)"


# ------------------------------------------------------------------ NRC table

NRC_GENERAL_REJECT = 0x10
NRC_SERVICE_NOT_SUPPORTED = 0x11
NRC_SUBFUNCTION_NOT_SUPPORTED = 0x12
NRC_BUSY_REPEAT_REQUEST = 0x21
NRC_CONDITIONS_NOT_CORRECT = 0x22
NRC_ROUTINE_NOT_COMPLETE = 0x23
NRC_REQUEST_OUT_OF_RANGE = 0x31
NRC_SECURITY_ACCESS_DENIED = 0x33
NRC_INVALID_KEY = 0x35
NRC_EXCEED_NUMBER_OF_ATTEMPTS = 0x36
NRC_REQUIRED_TIME_DELAY_NOT_EXPIRED = 0x37
NRC_RESPONSE_PENDING = 0x78

#: ISO 14230-3 Table 4.4, verbatim names (PROTOCOL_FACTS §4 item 7).
NRC_NAMES: Dict[int, str] = {
    0x10: "generalReject",
    0x11: "serviceNotSupported",
    0x12: "subFunctionNotSupported-invalidFormat",
    0x21: "busy-RepeatRequest",
    0x22: "conditionsNotCorrect or requestSequenceError",
    0x23: "routineNotComplete",
    0x31: "requestOutOfRange",
    0x33: "securityAccessDenied",
    0x35: "invalidKey",
    0x36: "exceedNumberOfAttempts",
    0x37: "requiredTimeDelayNotExpired",
    0x40: "downloadNotAccepted",
    0x41: "improperDownloadType",
    0x42: "can'tDownloadToSpecifiedAddress",
    0x43: "can'tDownloadNumberOfBytesRequested",
    0x50: "uploadNotAccepted",
    0x51: "improperUploadType",
    0x52: "can'tUploadFromSpecifiedAddress",
    0x53: "can'tUploadNumberOfBytesRequested",
    0x71: "transferSuspended",
    0x72: "transferAborted",
    0x74: "illegalAddressInBlockTransfer",
    0x75: "illegalByteCountInBlockTransfer",
    0x76: "illegalBlockTransferType",
    0x77: "blockTransferDataChecksumError",
    0x78: "reqCorrectlyRcvd-RspPending",
    0x79: "incorrectByteCountDuringBlockTransfer",
}

#: PyVCDS lists these too, but they are UDS (ISO 14229) codes, not KWP2000 ones; a
#: KWP module answers 0x11 for a wrong session. Kept only so a decoder can say so.
UDS_ONLY_NRCS: FrozenSet[int] = frozenset({0x13, 0x14, 0x24, 0x25, 0x70, 0x73, 0x7E, 0x7F, 0x80})

#: NRCs the client handles itself: keep waiting (0x78) or resend (0x21 / 0x23).
NRC_WAIT = frozenset({NRC_RESPONSE_PENDING})
NRC_RESEND = frozenset({NRC_BUSY_REPEAT_REQUEST, NRC_ROUTINE_NOT_COMPLETE})

#: "No such block / option / routine" family (PyVCDS maps 0x31 -> ENOENT, DV answers
#: ``7F 21 11`` for a block that does not exist).
NRC_NOT_HERE = frozenset({NRC_SERVICE_NOT_SUPPORTED, NRC_SUBFUNCTION_NOT_SUPPORTED, NRC_REQUEST_OUT_OF_RANGE})


def nrc_name(nrc: int) -> str:
    """Name for a KWP2000 NRC byte, or its ISO range when it has none."""
    name = NRC_NAMES.get(nrc)
    if name is not None:
        return name
    if 0x80 <= nrc <= 0xFF:          # ISO range wins over PyVCDS's 0x80 label
        return f"manufacturerSpecific(0x{nrc:02X})"
    if nrc in UDS_ONLY_NRCS:
        return f"notAKwp2000Code-UDSonly(0x{nrc:02X})"
    if nrc == 0x00:
        return "positiveResponse"
    return f"reservedByDocument(0x{nrc:02X})"


def is_negative_response(data: bytes) -> bool:
    return len(data) >= 3 and data[0] == NEGATIVE_RESPONSE_SID


def nrc_of(data: bytes) -> Optional[int]:
    """The NRC of a ``7F SID NRC`` message, or ``None`` for anything else."""
    return data[2] if is_negative_response(data) else None


__all__ = [
    "warn_unverified",
    "NEGATIVE_RESPONSE_SID", "POSITIVE_RESPONSE_OFFSET", "positive_sid",
    "Service", "SERVICE_NAMES", "service_name", "OUT_OF_SCOPE_SERVICES",
    "SESSION_STANDARD_DIAGNOSTIC", "SESSION_PROGRAMMING", "SESSION_ENGINEERING", "SESSION_ME7_DEFAULT",
    "SESSIONS", "SessionInfo", "session_name", "SESSION_REQUEST_IMMO_CLUSTER",
    "IdentOption", "IDENT_OPTIONS", "IDENT_STANDARD", "IDENT_HARDWARE_NUMBER", "IDENT_LONG_CODING",
    "IDENT_INSTALLATION_LIST", "CODING_TYPE_NONE", "CODING_TYPE_SHORT", "CODING_TYPE_LONG", "CODING_TYPE_NAMES",
    "DTC_GROUP_ALL", "DTC_STATUS_VAG", "DTC_STATUS_ALL", "DTC_STATUS_SUPPORTED", "CLEAR_GROUP_ALL",
    "DTC_STATUS_ELABORATION_MASK", "DTC_STATUS_BIT4", "DTC_STATUS_BIT5_STORED", "DTC_STATUS_BIT6_PRESENT",
    "DTC_STATUS_BIT7_MIL",
    "ROUTINE_FUNCTION_START", "ROUTINE_FUNCTION_SELECT", "ROUTINE_FUNCTION_READ", "ROUTINE_FUNCTION_SAVE",
    "CAPABILITY_QUERY_FUNCTION", "CapabilityCode", "CAPABILITY_CODES", "capability_name",
    "NRC_GENERAL_REJECT", "NRC_SERVICE_NOT_SUPPORTED", "NRC_SUBFUNCTION_NOT_SUPPORTED", "NRC_BUSY_REPEAT_REQUEST",
    "NRC_CONDITIONS_NOT_CORRECT", "NRC_ROUTINE_NOT_COMPLETE", "NRC_REQUEST_OUT_OF_RANGE",
    "NRC_SECURITY_ACCESS_DENIED", "NRC_INVALID_KEY", "NRC_EXCEED_NUMBER_OF_ATTEMPTS",
    "NRC_REQUIRED_TIME_DELAY_NOT_EXPIRED", "NRC_RESPONSE_PENDING", "NRC_NAMES", "UDS_ONLY_NRCS",
    "NRC_WAIT", "NRC_RESEND", "NRC_NOT_HERE", "nrc_name", "is_negative_response", "nrc_of",
]
