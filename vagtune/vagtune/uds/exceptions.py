"""
UDS (ISO 14229) exceptions and negative-response-code decoding.

A negative response is always three bytes on the wire: ``7F <echoed request SID>
<NRC>`` (verified: PROTOCOL_FACTS / uds_vag.md §A). The NRC table below is the
complete 0x10..0x94 list with the exact names from the facts (udsoncan
``ResponseCode.py``, re-read line for line); anything not in the table falls into one
of the ISO 14229 reserved / manufacturer-specific ranges, which :func:`nrc_name`
describes instead of printing a bare number.

Three codes get special handling by the client:

* ``0x78`` RequestCorrectlyReceived_ResponsePending: keep waiting (P2* window).
* ``0x21`` BusyRepeatRequest: resend the whole request after a short pause.
* ``0x14`` ResponseTooLong: the client must split a multi-DID read.
"""

from __future__ import annotations

from typing import Dict

# --------------------------------------------------------------------------- codes
# Exact names from the facts (udsoncan ResponseCode.py, verified).

NRC_GENERAL_REJECT = 0x10
NRC_SERVICE_NOT_SUPPORTED = 0x11
NRC_SUBFUNCTION_NOT_SUPPORTED = 0x12
NRC_INCORRECT_MESSAGE_LENGTH = 0x13
NRC_RESPONSE_TOO_LONG = 0x14
NRC_BUSY_REPEAT_REQUEST = 0x21
NRC_CONDITIONS_NOT_CORRECT = 0x22
NRC_REQUEST_SEQUENCE_ERROR = 0x24
NRC_REQUEST_OUT_OF_RANGE = 0x31
NRC_SECURITY_ACCESS_DENIED = 0x33
NRC_INVALID_KEY = 0x35
NRC_EXCEED_NUMBER_OF_ATTEMPTS = 0x36
NRC_REQUIRED_TIME_DELAY_NOT_EXPIRED = 0x37
NRC_RESPONSE_PENDING = 0x78
NRC_SUBFUNCTION_NOT_SUPPORTED_IN_SESSION = 0x7E
NRC_SERVICE_NOT_SUPPORTED_IN_SESSION = 0x7F

# Exact spelling of the facts (udsoncan ResponseCode.py). ``NRC_NAMES`` below is the same
# table in ISO 14229 lowerCamel spelling (the form the rest of the project prints).
NRC_NAMES_UDSONCAN: Dict[int, str] = {
    0x10: "GeneralReject",
    0x11: "ServiceNotSupported",
    0x12: "SubFunctionNotSupported",
    0x13: "IncorrectMessageLengthOrInvalidFormat",
    0x14: "ResponseTooLong",
    0x21: "BusyRepeatRequest",
    0x22: "ConditionsNotCorrect",
    0x24: "RequestSequenceError",
    0x25: "NoResponseFromSubnetComponent",
    0x26: "FailurePreventsExecutionOfRequestedAction",
    0x31: "RequestOutOfRange",
    0x33: "SecurityAccessDenied",
    0x34: "AuthenticationRequired",
    0x35: "InvalidKey",
    0x36: "ExceedNumberOfAttempts",
    0x37: "RequiredTimeDelayNotExpired",
    0x38: "SecureDataTransmissionRequired",
    0x39: "SecureDataTransmissionNotAllowed",
    0x3A: "SecureDataVerificationFailed",
    0x50: "CertificateVerificationFailed_InvalidTimePeriod",
    0x51: "CertificateVerificationFailed_InvalidSignature",
    0x52: "CertificateVerificationFailed_InvalidChainOfTrust",
    0x53: "CertificateVerificationFailed_InvalidType",
    0x54: "CertificateVerificationFailed_InvalidFormat",
    0x55: "CertificateVerificationFailed_InvalidContent",
    0x56: "CertificateVerificationFailed_InvalidScope",
    0x57: "CertificateVerificationFailed_InvalidCertificate",   # ISO note: revoked cert
    0x58: "OwnershipVerificationFailed",
    0x59: "ChallengeCalculationFailed",
    0x5A: "SettingAccessRightsFailed",
    0x5B: "SessionKeyCreationDerivationFailed",
    0x5C: "ConfigurationDataUsageFailed",
    0x5D: "DeAuthenticationFailed",
    0x70: "UploadDownloadNotAccepted",
    0x71: "TransferDataSuspended",
    0x72: "GeneralProgrammingFailure",
    0x73: "WrongBlockSequenceCounter",
    0x78: "RequestCorrectlyReceived_ResponsePending",
    0x7E: "SubFunctionNotSupportedInActiveSession",
    0x7F: "ServiceNotSupportedInActiveSession",
    0x81: "RpmTooHigh",
    0x82: "RpmTooLow",
    0x83: "EngineIsRunning",
    0x84: "EngineIsNotRunning",
    0x85: "EngineRunTimeTooLow",
    0x86: "TemperatureTooHigh",
    0x87: "TemperatureTooLow",
    0x88: "VehicleSpeedTooHigh",
    0x89: "VehicleSpeedTooLow",
    0x8A: "ThrottlePedalTooHigh",
    0x8B: "ThrottlePedalTooLow",
    0x8C: "TransmissionRangeNotInNeutral",
    0x8D: "TransmissionRangeNotInGear",
    0x8F: "BrakeSwitchNotClosed",
    0x90: "ShifterLeverNotInPark",
    0x91: "TorqueConverterClutchLocked",
    0x92: "VoltageTooHigh",
    0x93: "VoltageTooLow",
    0x94: "ResourceTemporarilyNotAvailable",
}

NRC_NAMES: Dict[int, str] = {k: v[0].lower() + v[1:] for k, v in NRC_NAMES_UDSONCAN.items()}

# Alternate names for 0x38..0x40 when SecuredDataTransmission (0x84) is involved
# (udsoncan, verified). Context decides; ``nrc_name(nrc, secured=True)`` selects them.
NRC_NAMES_SECURED_DATA: Dict[int, str] = {
    0x38: "GeneralSecurityViolation",
    0x39: "SecuredModeRequested",
    0x3A: "InsufficientProtection",
    0x3B: "TerminationWithSignatureRequested",
    0x3C: "AccessDenied",
    0x3D: "VersionNotSupported",
    0x3E: "SecuredLinkNotSupported",
    0x3F: "CertificateNotAvailable",
    0x40: "AuditTrailInformationNotAvailable",
}

# ISO 14229 reserved / manufacturer ranges for codes that have no name above.
_NRC_RANGES = (
    (0x00, 0x00, "positiveResponse"),
    (0x01, 0x0F, "ISOSAEReserved"),
    (0x15, 0x20, "ISOSAEReserved"),
    (0x3B, 0x4F, "ISOSAEReserved"),
    (0x5E, 0x6F, "ISOSAEReserved"),
    (0x74, 0x77, "ISOSAEReserved"),
    (0x79, 0x7D, "ISOSAEReserved"),
    (0x80, 0x80, "ISOSAEReserved"),
    (0x95, 0xEF, "ISOSAEReserved"),
    (0xF0, 0xFE, "vehicleManufacturerSpecific"),
    (0xFF, 0xFF, "ISOSAEReserved"),
)


def nrc_name(nrc: int, *, secured: bool = False) -> str:
    """Name for an NRC byte, or its ISO range when it has no name.

    ``secured=True`` picks the SecuredDataTransmission aliases for 0x38..0x40.
    """
    if secured and nrc in NRC_NAMES_SECURED_DATA:
        return NRC_NAMES_SECURED_DATA[nrc]
    if nrc in NRC_NAMES:
        return NRC_NAMES[nrc]
    for lo, hi, label in _NRC_RANGES:
        if lo <= nrc <= hi:
            return f"{label}(0x{nrc:02X})"
    return f"0x{nrc:02X}"


# NRCs that mean "the thing you asked for exists, but you may not have it right now":
# used by DID scanning to tell a refused DID from an absent one (0x31).
NRC_EXISTS_BUT_REFUSED = frozenset({0x13, 0x22, 0x33, 0x37, 0x7E, 0x7F})


# ---------------------------------------------------------------------- exceptions

class UdsError(Exception):
    """Base class for UDS-layer failures."""


class UdsTimeout(UdsError):
    """No response arrived within the configured timeout."""


class UnexpectedResponse(UdsError):
    """A positive response arrived but its SID/echo did not match the request."""


class NegativeResponse(UdsError):
    """The ECU replied with a 0x7F negative response."""

    def __init__(self, request_sid: int, nrc: int) -> None:
        self.request_sid = request_sid
        self.nrc = nrc
        self.nrc_name = nrc_name(nrc)
        super().__init__(
            f"ECU rejected service 0x{request_sid:02X}: {self.nrc_name} (NRC 0x{nrc:02X})"
        )

    @property
    def is_response_pending(self) -> bool:
        return self.nrc == NRC_RESPONSE_PENDING

    @property
    def is_not_supported(self) -> bool:
        """0x11/0x12/0x31: the service, subfunction or identifier does not exist here."""
        return self.nrc in (NRC_SERVICE_NOT_SUPPORTED, NRC_SUBFUNCTION_NOT_SUPPORTED,
                            NRC_REQUEST_OUT_OF_RANGE)

    @property
    def is_refused(self) -> bool:
        """The request was understood but refused (session, security, conditions, length)."""
        return self.nrc in NRC_EXISTS_BUT_REFUSED

    @property
    def is_security_related(self) -> bool:
        return self.nrc in (NRC_SECURITY_ACCESS_DENIED, NRC_INVALID_KEY,
                            NRC_EXCEED_NUMBER_OF_ATTEMPTS, NRC_REQUIRED_TIME_DELAY_NOT_EXPIRED)
