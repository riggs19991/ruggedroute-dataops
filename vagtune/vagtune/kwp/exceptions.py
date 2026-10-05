"""
KWP2000 client exceptions.

A KWP negative response is ``7F <request SID> <NRC>`` (ISO 14230-3, verified in every
fetched implementation); :class:`KwpNegativeResponse` carries the three facts and the
ISO name of the code (:func:`vagtune.kwp.services.nrc_name`).
"""

from __future__ import annotations

from typing import Optional

from .services import NRC_NOT_HERE, NRC_RESPONSE_PENDING, NRC_RESEND, nrc_name, service_name


class KwpError(Exception):
    """Base class for KWP2000-layer failures."""


class KwpTimeout(KwpError):
    """No (final) response arrived within the P2 / P2* window."""


class UnexpectedKwpResponse(KwpError):
    """A positive response arrived but its SID / echo / length did not fit the request."""


class KwpNegativeResponse(KwpError):
    """The module answered ``7F <sid> <nrc>``."""

    def __init__(self, sid: int, nrc: int, nrc_name_: Optional[str] = None) -> None:
        self.sid = sid
        self.nrc = nrc
        self.nrc_name = nrc_name_ or nrc_name(nrc)
        super().__init__(
            f"module rejected {service_name(sid)} (0x{sid:02X}): {self.nrc_name} (NRC 0x{nrc:02X})")

    @property
    def is_response_pending(self) -> bool:
        return self.nrc == NRC_RESPONSE_PENDING

    @property
    def is_busy(self) -> bool:
        """0x21 busy-RepeatRequest / 0x23 routineNotComplete: the client resends."""
        return self.nrc in NRC_RESEND

    @property
    def is_not_supported(self) -> bool:
        """0x11 / 0x12 / 0x31: no such service, option, group or routine here."""
        return self.nrc in NRC_NOT_HERE


__all__ = ["KwpError", "KwpTimeout", "UnexpectedKwpResponse", "KwpNegativeResponse"]
