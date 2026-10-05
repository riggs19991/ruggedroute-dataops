"""
High-level VAG ECU session.

Wraps a :class:`~vagtune.uds.client.UdsClient` with the VAG-specific flows you run
all the time: read the identification block, read/clear fault codes, unlock security
with the right SA2 script, and read a calibration block out of flash.

This is the object a GUI or the CLI drives. It owns the tester-present keepalive
during security-sensitive work.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from ..uds.client import UdsClient
from ..uds.exceptions import NegativeResponse
from ..uds.services import Session
from . import modules
from .dtc import decode_dtc_number, describe_dtc
from .profiles import EcuProfile, FlashBlock, guess_profile
from .sa2 import Sa2Interpreter, make_seed_key_fn

log = logging.getLogger(__name__)


@dataclass
class EcuIdentity:
    values: Dict[int, str]

    @property
    def vin(self) -> Optional[str]:
        return self.values.get(0xF190)

    @property
    def part_number(self) -> Optional[str]:
        return self.values.get(0xF187)

    @property
    def software_version(self) -> Optional[str]:
        return self.values.get(0xF189)

    @property
    def system_name(self) -> Optional[str]:
        return self.values.get(0xF197)

    def pretty(self) -> str:
        lines = []
        for did_def in modules.IDENT_DIDS:
            v = self.values.get(did_def.did)
            if v:
                lines.append(f"  {did_def.name:<32} {v}")
        return "\n".join(lines)


@dataclass
class DtcEntry:
    number: int
    status: int
    code: str
    description: str

    def __str__(self) -> str:
        return f"{self.code}  (0x{self.number:06X}, status 0x{self.status:02X})  {self.description}"


class VagEcuSession:
    def __init__(self, client: UdsClient, profile: Optional[EcuProfile] = None) -> None:
        self.client = client
        self.profile = profile

    # -- identification ----------------------------------------------------------

    def read_identity(self) -> EcuIdentity:
        values: Dict[int, str] = {}
        for did_def in modules.IDENT_DIDS:
            try:
                raw = self.client.read_data_by_identifier(did_def.did)
            except NegativeResponse as exc:
                log.debug("DID 0x%04X not available: %s", did_def.did, exc)
                continue
            values[did_def.did] = modules.decode_ident_value(did_def, raw)
        return EcuIdentity(values)

    def detect_profile(self, identity: Optional[EcuIdentity] = None) -> Optional[EcuProfile]:
        identity = identity or self.read_identity()
        name = identity.system_name or ""
        prof = guess_profile(name)
        if prof is not None:
            self.profile = prof
            log.info("detected ECU profile: %s", prof.display_name)
        else:
            log.info("could not auto-detect ECU profile from system name %r", name)
        return prof

    # -- fault codes -------------------------------------------------------------

    def read_dtcs(self, status_mask: int = 0xFF) -> List[DtcEntry]:
        raw = self.client.read_dtc_by_status_mask(status_mask)
        out: List[DtcEntry] = []
        for number, status in raw:
            code = decode_dtc_number(number)
            out.append(DtcEntry(number, status, code, describe_dtc(code)))
        return out

    def clear_dtcs(self, group: int = 0xFFFFFF) -> None:
        self.client.clear_diagnostic_information(group)

    # -- security ----------------------------------------------------------------

    def enter_extended_session(self) -> None:
        self.client.diagnostic_session_control(Session.EXTENDED_DIAGNOSTIC)

    def enter_programming_session(self) -> None:
        self.client.diagnostic_session_control(Session.PROGRAMMING)

    def unlock(self, sa2_script: Optional[bytes] = None, level: Optional[int] = None) -> None:
        """Unlock calibration security using an SA2 script.

        Resolution order for the script:
          1. explicit ``sa2_script`` argument,
          2. the active profile's ``sa2_script``.
        If neither is available, raises - you must supply or extract the script.
        """
        script = sa2_script
        if script is None and self.profile is not None:
            script = self.profile.sa2_script
        if script is None:
            raise ValueError(
                "No SA2 script available for this ECU. Supply sa2_script=... "
                "(extract it from the ECU's ODX/FRF container)."
            )

        sec_level = level if level is not None else (
            self.profile.security_level if self.profile else 0x11
        )
        self.client.security_access(sec_level, make_seed_key_fn(script))

    # -- calibration read --------------------------------------------------------

    def read_block(
        self,
        block: FlashBlock,
        progress: Optional[Callable[[int, int], None]] = None,
    ) -> bytes:
        """Read a flash block via UDS upload (RequestUpload + TransferData loop)."""
        log.info("reading block %s: 0x%X bytes at 0x%08X", block.name, block.length, block.start)
        return self.client.upload(block.start, block.length, progress=progress)

    def read_calibration(self, progress: Optional[Callable[[int, int], None]] = None) -> bytes:
        if self.profile is None:
            raise ValueError("No ECU profile set; call detect_profile() or pass one in.")
        cal = self.profile.calibration_block()
        if cal is None or cal.length == 0:
            raise ValueError(f"profile {self.profile.key} has no CAL block defined")
        return self.read_block(cal, progress=progress)

    # -- convenience -------------------------------------------------------------

    def full_report(self) -> str:
        identity = self.read_identity()
        lines = ["ECU Identification:", identity.pretty(), "", "Fault codes:"]
        try:
            dtcs = self.read_dtcs()
            if dtcs:
                lines += [f"  {d}" for d in dtcs]
            else:
                lines.append("  (none stored)")
        except NegativeResponse as exc:
            lines.append(f"  (could not read DTCs: {exc})")
        return "\n".join(lines)
