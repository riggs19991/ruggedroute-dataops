"""
UDS (ISO 14229-1) service identifiers, subfunction constants and identifier catalogues.

Everything here is a plain constant table. Values marked *verified* come from
PROTOCOL_FACTS (uds_vag.md): the Wikipedia UDS service table, udsoncan's service
modules (re-read byte for byte), uds.readthedocs.io's DID/RID lists and the VW_Flash
``data_records`` table for the VAG-specific DIDs. The few VAG items whose *meaning*
is only reported (session 0x4F semantics, the 0xFF02 mirror-memory routine) carry an
``UNVERIFIED`` note; they are names, not behaviour, so no runtime warning fires here —
the code paths that *act* on them warn.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Dict, Optional

POSITIVE_RESPONSE_OFFSET = 0x40
NEGATIVE_RESPONSE_SID = 0x7F


class Service(IntEnum):
    """Request SIDs; the positive response SID is ``sid + 0x40`` (verified)."""
    DIAGNOSTIC_SESSION_CONTROL = 0x10
    ECU_RESET = 0x11
    CLEAR_DIAGNOSTIC_INFORMATION = 0x14
    READ_DTC_INFORMATION = 0x19
    READ_DATA_BY_IDENTIFIER = 0x22
    READ_MEMORY_BY_ADDRESS = 0x23
    READ_SCALING_DATA_BY_IDENTIFIER = 0x24
    SECURITY_ACCESS = 0x27
    COMMUNICATION_CONTROL = 0x28
    AUTHENTICATION = 0x29
    READ_DATA_BY_PERIODIC_ID = 0x2A
    DYNAMICALLY_DEFINE_DATA_ID = 0x2C
    WRITE_DATA_BY_IDENTIFIER = 0x2E
    INPUT_OUTPUT_CONTROL = 0x2F
    ROUTINE_CONTROL = 0x31
    REQUEST_DOWNLOAD = 0x34
    REQUEST_UPLOAD = 0x35
    TRANSFER_DATA = 0x36
    REQUEST_TRANSFER_EXIT = 0x37
    REQUEST_FILE_TRANSFER = 0x38
    WRITE_MEMORY_BY_ADDRESS = 0x3D
    TESTER_PRESENT = 0x3E
    ACCESS_TIMING_PARAMETER = 0x83
    SECURED_DATA_TRANSMISSION = 0x84
    CONTROL_DTC_SETTING = 0x85
    RESPONSE_ON_EVENT = 0x86
    LINK_CONTROL = 0x87


SERVICE_NAMES: Dict[int, str] = {
    0x10: "DiagnosticSessionControl", 0x11: "ECUReset", 0x14: "ClearDiagnosticInformation",
    0x19: "ReadDTCInformation", 0x22: "ReadDataByIdentifier", 0x23: "ReadMemoryByAddress",
    0x24: "ReadScalingDataByIdentifier", 0x27: "SecurityAccess", 0x28: "CommunicationControl",
    0x29: "Authentication", 0x2A: "ReadDataByPeriodicIdentifier",
    0x2C: "DynamicallyDefineDataIdentifier", 0x2E: "WriteDataByIdentifier",
    0x2F: "InputOutputControlByIdentifier", 0x31: "RoutineControl", 0x34: "RequestDownload",
    0x35: "RequestUpload", 0x36: "TransferData", 0x37: "RequestTransferExit",
    0x38: "RequestFileTransfer", 0x3D: "WriteMemoryByAddress", 0x3E: "TesterPresent",
    0x83: "AccessTimingParameter", 0x84: "SecuredDataTransmission", 0x85: "ControlDTCSetting",
    0x86: "ResponseOnEvent", 0x87: "LinkControl",
}


class Session(IntEnum):
    """DiagnosticSessionControl types (verified). ``VAG_4F`` is exercised by VW_Flash
    testdata (``10 4F`` -> ``50 4F``) so the byte is real on VAG; its semantics
    (EOL / another extended variant) are UNVERIFIED (uds_vag.md REPORTED)."""
    DEFAULT = 0x01
    PROGRAMMING = 0x02
    EXTENDED_DIAGNOSTIC = 0x03
    SAFETY_SYSTEM_DIAGNOSTIC = 0x04
    VAG_4F = 0x4F   # UNVERIFIED: semantics; the byte itself is verified present on VAG


SESSION_NAMES: Dict[int, str] = {
    0x01: "defaultSession", 0x02: "programmingSession", 0x03: "extendedDiagnosticSession",
    0x04: "safetySystemDiagnosticSession", 0x4F: "VAG session 0x4F (semantics unverified)",
}


class ResetType(IntEnum):
    """ECUReset subfunctions (verified)."""
    HARD_RESET = 0x01
    KEY_OFF_ON_RESET = 0x02
    SOFT_RESET = 0x03
    ENABLE_RAPID_POWER_SHUTDOWN = 0x04
    DISABLE_RAPID_POWER_SHUTDOWN = 0x05


class RoutineControlType(IntEnum):
    START = 0x01
    STOP = 0x02
    REQUEST_RESULTS = 0x03


# Routine-identifier ranges (uds.readthedocs.io rid.html, verified).
ROUTINE_ERASE_MEMORY = 0xFF00
ROUTINE_CHECK_PROGRAMMING_DEPENDENCIES = 0xFF01
ROUTINE_EXECUTE_SPL = 0xE200
ROUTINE_DEPLOY_LOOP = 0xE201
# UNVERIFIED: 0xFF02 "eraseMirrorMemoryDTCs" exists in some ISO editions; rid.html lists
# 0xFF02-0xFFFF as reserved. Kept as a name for callers that know their module.
ROUTINE_ERASE_MIRROR_MEMORY_DTCS_UNVERIFIED = 0xFF02

_ROUTINE_RANGES = (
    (0x0000, 0x00FF, "ISOSAEReserved"),
    (0x0100, 0x01FF, "TachographTestIds"),
    (0x0200, 0xDFFF, "VehicleManufacturerSpecific"),
    (0xE000, 0xE1FF, "OBDTestIds"),
    (0xE200, 0xE200, "ExecuteSPL"),
    (0xE201, 0xE201, "DeployLoopRoutineID"),
    (0xE202, 0xE2FF, "SafetySystemRoutineIDs"),
    (0xE300, 0xEFFF, "ISOSAEReserved"),
    (0xF000, 0xFEFF, "SystemSupplierSpecific"),
    (0xFF00, 0xFF00, "eraseMemory"),
    (0xFF01, 0xFF01, "checkProgrammingDependencies"),
    (0xFF02, 0xFFFF, "ISOSAEReserved"),
)


def routine_id_range(rid: int) -> str:
    """Name of the ISO range a routine identifier falls in."""
    for lo, hi, label in _ROUTINE_RANGES:
        if lo <= rid <= hi:
            return label
    return "unknown"


class DtcReportType(IntEnum):
    """ReadDTCInformation (0x19) subfunctions (udsoncan, verified)."""
    REPORT_NUMBER_BY_STATUS_MASK = 0x01
    REPORT_DTC_BY_STATUS_MASK = 0x02
    REPORT_DTC_SNAPSHOT_IDENTIFICATION = 0x03
    REPORT_DTC_SNAPSHOT_RECORD = 0x04            # by DTC number
    REPORT_DTC_SNAPSHOT_RECORD_BY_RECORD_NUMBER = 0x05
    REPORT_DTC_EXTENDED_DATA_RECORD = 0x06       # by DTC number
    REPORT_NUMBER_BY_SEVERITY_MASK = 0x07
    REPORT_DTC_BY_SEVERITY_MASK = 0x08
    REPORT_SEVERITY_INFORMATION_OF_DTC = 0x09
    REPORT_SUPPORTED_DTC = 0x0A
    REPORT_FIRST_TEST_FAILED_DTC = 0x0B
    REPORT_FIRST_CONFIRMED_DTC = 0x0C
    REPORT_MOST_RECENT_TEST_FAILED_DTC = 0x0D
    REPORT_MOST_RECENT_CONFIRMED_DTC = 0x0E
    REPORT_MIRROR_MEMORY_DTC_BY_STATUS_MASK = 0x0F
    REPORT_MIRROR_MEMORY_DTC_EXTENDED_DATA_RECORD = 0x10
    REPORT_NUMBER_OF_MIRROR_MEMORY_DTC_BY_STATUS_MASK = 0x11
    REPORT_NUMBER_OF_EMISSIONS_OBD_DTC_BY_STATUS_MASK = 0x12
    REPORT_EMISSIONS_OBD_DTC_BY_STATUS_MASK = 0x13
    REPORT_DTC_FAULT_DETECTION_COUNTER = 0x14
    REPORT_DTC_WITH_PERMANENT_STATUS = 0x15
    REPORT_DTC_EXT_DATA_RECORD_BY_RECORD_NUMBER = 0x16
    REPORT_USER_DEF_MEMORY_DTC_BY_STATUS_MASK = 0x17
    REPORT_USER_DEF_MEMORY_DTC_SNAPSHOT_RECORD = 0x18
    REPORT_USER_DEF_MEMORY_DTC_EXT_DATA_RECORD = 0x19
    REPORT_SUPPORTED_DTC_EXT_DATA_RECORD = 0x1A
    REPORT_WWH_OBD_DTC_BY_MASK_RECORD = 0x42
    REPORT_WWH_OBD_DTC_WITH_PERMANENT_STATUS = 0x55
    REPORT_DTC_INFORMATION_BY_DTC_READINESS_GROUP = 0x56


DTC_REPORT_NAMES: Dict[int, str] = {
    0x01: "reportNumberOfDTCByStatusMask", 0x02: "reportDTCByStatusMask",
    0x03: "reportDTCSnapshotIdentification", 0x04: "reportDTCSnapshotRecordByDTCNumber",
    0x05: "reportDTCSnapshotRecordByRecordNumber",
    0x06: "reportDTCExtendedDataRecordByDTCNumber", 0x07: "reportNumberOfDTCBySeverityMaskRecord",
    0x08: "reportDTCBySeverityMaskRecord", 0x09: "reportSeverityInformationOfDTC",
    0x0A: "reportSupportedDTCs", 0x0B: "reportFirstTestFailedDTC", 0x0C: "reportFirstConfirmedDTC",
    0x0D: "reportMostRecentTestFailedDTC", 0x0E: "reportMostRecentConfirmedDTC",
    0x0F: "reportMirrorMemoryDTCByStatusMask",
    0x10: "reportMirrorMemoryDTCExtendedDataRecordByDTCNumber",
    0x11: "reportNumberOfMirrorMemoryDTCByStatusMask",
    0x12: "reportNumberOfEmissionsRelatedOBDDTCByStatusMask",
    0x13: "reportEmissionsRelatedOBDDTCByStatusMask", 0x14: "reportDTCFaultDetectionCounter",
    0x15: "reportDTCWithPermanentStatus", 0x16: "reportDTCExtDataRecordByRecordNumber",
    0x17: "reportUserDefMemoryDTCByStatusMask", 0x18: "reportUserDefMemoryDTCSnapshotRecordByDTCNumber",
    0x19: "reportUserDefMemoryDTCExtDataRecordByDTCNumber", 0x1A: "reportSupportedDTCExtDataRecord",
    0x42: "reportWWHOBDDTCByMaskRecord", 0x55: "reportWWHOBDDTCWithPermanentStatus",
    0x56: "reportDTCInformationByDTCReadinessGroupIdentifier",
}

# Subfunctions whose response is "<availability mask> then 4-byte (DTC3 + status) records"
# (udsoncan parses all of these identically; verified).
DTC_RECORD_LIST_SUBFUNCTIONS = frozenset({0x02, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x13, 0x15, 0x17})


# DTC status bit masks (ISO 14229-1 Annex D, verified).
class DtcStatus(IntEnum):
    TEST_FAILED = 0x01
    TEST_FAILED_THIS_CYCLE = 0x02
    PENDING = 0x04
    CONFIRMED = 0x08
    TEST_NOT_COMPLETE_SINCE_CLEAR = 0x10
    TEST_FAILED_SINCE_CLEAR = 0x20
    TEST_NOT_COMPLETE_THIS_CYCLE = 0x40
    WARNING_INDICATOR_REQUESTED = 0x80


DTC_STATUS_NAMES: Dict[int, str] = {
    0x01: "testFailed", 0x02: "testFailedThisOperationCycle", 0x04: "pendingDTC",
    0x08: "confirmedDTC", 0x10: "testNotCompletedSinceLastClear", 0x20: "testFailedSinceLastClear",
    0x40: "testNotCompletedThisOperationCycle", 0x80: "warningIndicatorRequested",
}


class DtcFormat(IntEnum):
    """DTCFormatIdentifier in a ``59 01`` response (udsoncan dtc.py, verified)."""
    ISO15031_6 = 0x00            # == SAE_J2012_DA_DTCFormat_00
    ISO14229_1 = 0x01
    SAE_J1939_73 = 0x02
    ISO11992_4 = 0x03
    SAE_J2012_DA_DTCFormat_04 = 0x04


class DtcSeverity(IntEnum):
    """Severity byte bits (subfunctions 0x08/0x09); low 5 bits are the DTC class."""
    MAINTENANCE_ONLY = 0x20
    CHECK_AT_NEXT_EXIT = 0x40
    CHECK_IMMEDIATELY = 0x80


class FunctionalGroup(IntEnum):
    EMISSIONS_SYSTEM_GROUP = 0x33
    SAFETY_SYSTEM_GROUP = 0xD0
    VOBD_SYSTEM = 0xFE


CLEAR_ALL_DTC_GROUPS = 0xFFFFFF   # ClearDiagnosticInformation group "all" (verified)


class IoControlOption(IntEnum):
    """InputOutputControlByIdentifier controlOptionRecord first byte (verified)."""
    RETURN_CONTROL_TO_ECU = 0x00
    RESET_TO_DEFAULT = 0x01
    FREEZE_CURRENT_STATE = 0x02
    SHORT_TERM_ADJUSTMENT = 0x03


class CommunicationControlType(IntEnum):
    """CommunicationControl controlType (udsoncan, verified)."""
    ENABLE_RX_AND_TX = 0x00
    ENABLE_RX_AND_DISABLE_TX = 0x01
    DISABLE_RX_AND_ENABLE_TX = 0x02
    DISABLE_RX_AND_TX = 0x03
    ENABLE_RX_AND_DISABLE_TX_WITH_ENHANCED_ADDRESS_INFORMATION = 0x04
    ENABLE_RX_AND_TX_WITH_ENHANCED_ADDRESS_INFORMATION = 0x05


# communicationType byte = (message_type & 0x3) | ((subnet & 0xF) << 4)  (verified)
COMM_NORMAL_MESSAGES = 0x01
COMM_NETWORK_MANAGEMENT_MESSAGES = 0x02
COMM_SUBNET_THIS_NODE = 0x0
COMM_SUBNET_ALL = 0xF


def communication_type(*, normal: bool = True, network_management: bool = False,
                       subnet: int = COMM_SUBNET_THIS_NODE) -> int:
    """Build the communicationType byte: low 2 bits message class, high nibble subnet."""
    message_type = (COMM_NORMAL_MESSAGES if normal else 0) | \
                   (COMM_NETWORK_MANAGEMENT_MESSAGES if network_management else 0)
    if not message_type:
        raise ValueError("communicationType needs at least one message class")
    return (message_type & 0x3) | ((subnet & 0xF) << 4)


class DynamicDefineType(IntEnum):
    """DynamicallyDefineDataIdentifier subfunctions (udsoncan, verified)."""
    DEFINE_BY_IDENTIFIER = 0x01
    DEFINE_BY_MEMORY_ADDRESS = 0x02
    CLEAR = 0x03


DYNAMIC_DID_RANGE = range(0xF200, 0xF300)   # periodic / dynamically defined DIDs


class DtcSettingType(IntEnum):
    ON = 0x01
    OFF = 0x02


SUPPRESS_POSITIVE_RESPONSE = 0x80  # OR into a subfunction byte to suppress the positive ack

# Security access: odd subfunction = requestSeed, even = sendKey (verified).
SECURITY_LEVEL_VAG_LOGIN = 0x03   # UNVERIFIED: coding/adaptation login level (VW_Flash fake data uses 03/04)
SECURITY_LEVEL_VAG_FLASH = 0x11   # UNVERIFIED: recorded in CLAUDE.md, not in any fetched source


# ------------------------------------------------------------------ DID catalogue

# ISO 14229-1 identification DIDs 0xF180..0xF19F (uds.readthedocs.io did.html, verified).
ISO_DID_NAMES: Dict[int, str] = {
    0xF180: "bootSoftwareIdentification",
    0xF181: "applicationSoftwareIdentification",
    0xF182: "applicationDataIdentification",
    0xF183: "bootSoftwareFingerprint",
    0xF184: "applicationSoftwareFingerprint",
    0xF185: "applicationDataFingerprint",
    0xF186: "ActiveDiagnosticSession",
    0xF187: "vehicleManufacturerSparePartNumber",
    0xF188: "vehicleManufacturerECUSoftwareNumber",
    0xF189: "vehicleManufacturerECUSoftwareVersionNumber",
    0xF18A: "systemSupplierIdentifier",
    0xF18B: "ECUManufacturingDate",
    0xF18C: "ECUSerialNumber",
    0xF18D: "supportedFunctionalUnits",
    0xF18E: "vehicleManufacturerKitAssemblyPartNumber",
    0xF190: "VIN",
    0xF191: "vehicleManufacturerECUHardwareNumber",
    0xF192: "systemSupplierECUHardwareNumber",
    0xF193: "systemSupplierECUHardwareVersionNumber",
    0xF194: "systemSupplierECUSoftwareNumber",
    0xF195: "systemSupplierECUSoftwareVersionNumber",
    0xF197: "systemNameOrEngineType",
    0xF198: "repairShopCodeOrTesterSerialNumber",
    0xF199: "programmingDate",
    0xF19A: "calibrationRepairShopCodeOrCalibrationEquipmentSerialNumber",
    0xF19B: "calibrationDate",
    0xF19C: "calibrationEquipmentSoftwareNumber",
    0xF19D: "ECUInstallationDate",
    0xF19E: "ODXFileIdentifier",
    0xF19F: "EntityDataIdentifier",
}

# VAG-specific DIDs (VW_Flash lib/constants.py data_records, verified list; the
# *meaning* strings are VW_Flash's labels).
VAG_DID_NAMES: Dict[int, str] = {
    0x0405: "State Of Flash Memory",
    0x0407: "VW Logical Software Block Counter Of Programming Attempts",
    0x0408: "VW Logical Software Block Counter Of Successful Programming Attempts",
    0x0600: "VW Coding Value (long coding)",
    0x12FC: "VW DID 0x12FC (unlabeled in source)",
    0x12FF: "VW DID 0x12FF (unlabeled in source)",
    0x295A: "Vehicle Mileage",
    0x295B: "Control Module Mileage",
    0xEF90: "Immobilizer Status SHE",
    0xF15B: "Fingerprint and Programming Date",
    0xF17C: "VW FAZIT Identification String",
    0xF17E: "ECU Production Change Number",
    0xF187: "VW Spare Part Number",
    0xF189: "VW Application Software Version Number",
    0xF190: "VIN Vehicle Identification Number",
    0xF191: "VW ECU Hardware Number",
    0xF19E: "ASAM/ODX File Identifier",
    0xF1A2: "ASAM/ODX File Version",
    0xF1A3: "VW ECU Hardware Version Number",
    0xF1A5: "VW Coding Repair Shop Code Or Serial Number (Coding Fingerprint)",
    0xF1AA: "VW Workshop System Name",
    0xF1AB: "VW Logical Software Block Version",
    0xF1AD: "Engine Code Letters",
    0xF1DF: "ECU Programming Information",
    0xF1E0: "VW DID 0xF1E0 (unlabeled in source)",
    0xF1F1: "Tuning Protection SO2",
    0xF1F4: "Boot Loader Identification",
    0xF40D: "Vehicle Speed (OBD mirror PID 0D)",
    0xF442: "Control Module Voltage (OBD mirror PID 42)",
    0xF804: "Calibration ID",
    0xF806: "Calibration Verification Numbers",
    0xFD52: "VW DID 0xFD52 (unlabeled in source)",
    0xFD83: "VW DID 0xFD83 (unlabeled in source)",
    0xFDFA: "VW DID 0xFDFA (unlabeled in source)",
    0xFDFC: "VW DID 0xFDFC (unlabeled in source)",
}

# Known fixed sizes of VAG DIDs (from the captured VW_Flash responses, verified for the
# Simos18 capture; other modules may differ, so these are *hints* for the size oracle).
VAG_DID_SIZE_HINTS: Dict[int, int] = {
    0xF190: 17,   # VIN
    0xF1A5: 6,    # coding fingerprint
    0x0405: 1,    # state of flash memory
    0xF186: 1,    # active session
}

DID_COMMON_DECODE_ASCII = frozenset({
    0xF187, 0xF189, 0xF190, 0xF191, 0xF197, 0xF1A2, 0xF1A3, 0xF1AD, 0xF17C, 0xF19E,
    0xF1F4, 0xF18C, 0xF1AA, 0xF1AB, 0xF804, 0xF17E, 0xF18A, 0xF192, 0xF193, 0xF194, 0xF195,
    0xF180, 0xF181, 0xF182, 0xF188, 0xF19A, 0xF19C,
})

OBD_MIRROR_DID_RANGE = range(0xF400, 0xF600)   # OBDDataIdentifier range (did.html, verified)


def did_name(did: int) -> str:
    """Best name for a DID: VAG label, else ISO name, else its range."""
    if did in VAG_DID_NAMES:
        return VAG_DID_NAMES[did]
    if did in ISO_DID_NAMES:
        return ISO_DID_NAMES[did]
    if did in OBD_MIRROR_DID_RANGE:
        pid = obd_mirror_pid(did)
        return f"OBD mirror PID 0x{pid:02X}" if pid is not None else "OBD mirror (PID > 0xFF)"
    if did in DYNAMIC_DID_RANGE:
        return "dynamically defined / periodic DID"
    if 0xF180 <= did <= 0xF1FF:
        return "identification DID (unnamed)"
    return f"DID 0x{did:04X}"


def obd_mirror_pid(did: int) -> Optional[int]:
    """UDS 0xF4xx <-> J1979 mode 01 PID 0xxx (verified: 0xF40D speed, 0xF442 voltage).

    Only 0xF400..0xF4FF map onto the 8-bit mode-01 PID space; 0xF5xx belongs to the
    same OBD range but has no mode-01 PID number, so ``None`` is returned for it.
    """
    if 0xF400 <= did <= 0xF4FF:
        return did - 0xF400
    return None
