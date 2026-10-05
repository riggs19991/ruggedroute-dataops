"""UDS (ISO 14229) exceptions and negative-response-code decoding."""

from __future__ import annotations


class UdsError(Exception):
    """Base class for UDS-layer failures."""


class UdsTimeout(UdsError):
    """No response arrived within the configured timeout."""


class UnexpectedResponse(UdsError):
    """A positive response arrived but its SID/echo did not match the request."""


# ISO 14229-1 Negative Response Codes (the common subset; others pass through by number).
NRC_NAMES = {
    0x10: "generalReject",
    0x11: "serviceNotSupported",
    0x12: "subFunctionNotSupported",
    0x13: "incorrectMessageLengthOrInvalidFormat",
    0x14: "responseTooLong",
    0x21: "busyRepeatRequest",
    0x22: "conditionsNotCorrect",
    0x24: "requestSequenceError",
    0x25: "noResponseFromSubnetComponent",
    0x26: "failurePreventsExecutionOfRequestedAction",
    0x31: "requestOutOfRange",
    0x33: "securityAccessDenied",
    0x34: "authenticationRequired",
    0x35: "invalidKey",
    0x36: "exceededNumberOfAttempts",
    0x37: "requiredTimeDelayNotExpired",
    0x38: "secureDataTransmissionRequired",
    0x39: "secureDataTransmissionNotAllowed",
    0x3A: "secureDataVerificationFailed",
    0x70: "uploadDownloadNotAccepted",
    0x71: "transferDataSuspended",
    0x72: "generalProgrammingFailure",
    0x73: "wrongBlockSequenceCounter",
    0x78: "requestCorrectlyReceived-ResponsePending",
    0x7E: "subFunctionNotSupportedInActiveSession",
    0x7F: "serviceNotSupportedInActiveSession",
    0x81: "rpmTooHigh",
    0x82: "rpmTooLow",
    0x83: "engineIsRunning",
    0x84: "engineIsNotRunning",
    0x85: "engineRunTimeTooLow",
    0x86: "temperatureTooHigh",
    0x87: "temperatureTooLow",
    0x92: "voltageTooHigh",
    0x93: "voltageTooLow",
}


class NegativeResponse(UdsError):
    """The ECU replied with a 0x7F negative response."""

    def __init__(self, request_sid: int, nrc: int) -> None:
        self.request_sid = request_sid
        self.nrc = nrc
        self.nrc_name = NRC_NAMES.get(nrc, f"0x{nrc:02X}")
        super().__init__(
            f"ECU rejected service 0x{request_sid:02X}: {self.nrc_name} (NRC 0x{nrc:02X})"
        )

    @property
    def is_response_pending(self) -> bool:
        return self.nrc == 0x78
