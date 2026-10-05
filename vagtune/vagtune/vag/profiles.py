"""
ECU family profiles.

A profile captures what the toolkit needs to know about a specific ECU hardware/
software family to read (and eventually write) its calibration: the diagnostic
module address, the SA2 security script, and the flash block map.

Only metadata lives here - no calibration maps (those come from per-ECU definition
files in :mod:`vagtune.calibration`). The SA2 script bytes shipped below are the
publicly documented scripts for these families; at runtime you can also extract the
script from the ECU's own ODX/FRF container and override it, which is the correct
approach for any ECU not listed here.

NOTE on legality/scope: these profiles describe how to communicate with and read an
ECU. This toolkit is intended for off-road / track-only vehicles. Writing
calibration that alters emissions behaviour on a street-registered vehicle is
regulated; see the project README.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .modules import ENGINE, TRANSMISSION, ModuleAddress


@dataclass(frozen=True)
class FlashBlock:
    """One addressable region of ECU flash."""
    index: int
    name: str
    start: int
    length: int

    @property
    def end(self) -> int:
        return self.start + self.length


@dataclass
class EcuProfile:
    key: str
    display_name: str
    module: ModuleAddress
    security_level: int                       # requestSeed subfunction for calibration access
    sa2_script: Optional[bytes]               # None => must be extracted from the ECU container
    blocks: List[FlashBlock] = field(default_factory=list)
    # DID whose value identifies this family (for auto-detect): (did, substring).
    identify_by: Tuple[int, bytes] = (0xF197, b"")
    notes: str = ""

    def block_by_name(self, name: str) -> Optional[FlashBlock]:
        for b in self.blocks:
            if b.name.lower() == name.lower():
                return b
        return None

    def calibration_block(self) -> Optional[FlashBlock]:
        return self.block_by_name("CAL")


# --- Bosch MED17.x (EA888 Gen1/Gen3 petrol: MK6 GTI/Golf R, 8P/8V A3, etc.) ------
# Block layout is a simplified, representative MED17.5 map. Real offsets vary by
# exact variant; auto-extract from the FRF/ODX for production use.
MED17_5 = EcuProfile(
    key="med17.5",
    display_name="Bosch MED17.5 (EA888 2.0T)",
    module=ENGINE,
    security_level=0x11,
    sa2_script=None,  # MED17 scripts differ per variant; extract from container.
    blocks=[
        FlashBlock(0, "CBOOT", 0x80_0000, 0x01_0000),
        FlashBlock(1, "ASW1", 0x82_0000, 0x0F_0000),
        FlashBlock(2, "ASW2", 0x90_0000, 0x10_0000),
        FlashBlock(3, "CAL", 0xA0_0000, 0x04_0000),
    ],
    identify_by=(0xF197, b""),
    notes="Petrol EA888. OBD read/write generally needs bench or a variant-specific flow.",
)

# --- Continental/Siemens SIMOS 18.1 (MQB EA888 Gen3: MK7 GTI/Golf R, 8V A3) ------
# Base addresses and the SA2 script here are the publicly documented SIMOS18 values.
SIMOS18_SA2 = bytes.fromhex(
    "6802814A10680493080820094A05872212195482499307122011824A058703112010824A0181494C"
)

SIMOS18_1 = EcuProfile(
    key="simos18.1",
    display_name="Continental SIMOS 18.1 (MQB 2.0T)",
    module=ENGINE,
    security_level=0x11,
    sa2_script=SIMOS18_SA2,
    blocks=[
        FlashBlock(0, "SBOOT", 0x8000_0000, 0x02_0000),
        FlashBlock(1, "CBOOT", 0x8002_0000, 0x02_0000),
        FlashBlock(2, "ASW1", 0x800C_0000, 0x1E_0000),
        FlashBlock(3, "ASW2", 0x802A_0000, 0x10_0000),
        FlashBlock(4, "ASW3", 0x803A_0000, 0x10_0000),
        FlashBlock(5, "CAL", 0x80A8_0000, 0x08_0000),
    ],
    identify_by=(0xF197, b""),
    notes="MQB petrol. OBD flash is well documented in the community; SFD not present.",
)

# --- Continental SIMOS 18.10 (MQB-Evo, ~2019+): adds SFD locking -----------------
SIMOS18_10 = EcuProfile(
    key="simos18.10",
    display_name="Continental SIMOS 18.10 (MQB-Evo 2.0T)",
    module=ENGINE,
    security_level=0x11,
    sa2_script=None,  # Extract per-ECU; also gated by SFD online auth on many cars.
    blocks=[
        FlashBlock(0, "SBOOT", 0x8000_0000, 0x02_0000),
        FlashBlock(1, "CBOOT", 0x8002_0000, 0x02_0000),
        FlashBlock(2, "ASW1", 0x800C_0000, 0x1E_0000),
        FlashBlock(3, "ASW2", 0x802A_0000, 0x10_0000),
        FlashBlock(4, "ASW3", 0x803A_0000, 0x10_0000),
        FlashBlock(5, "CAL", 0x80A8_0000, 0x08_0000),
    ],
    identify_by=(0xF197, b""),
    notes="MQB-Evo. SFD (Schutz Fahrzeugdiagnose) typically blocks write without online auth.",
)

# --- DSG: DQ250 (wet clutch) transmission, for completeness ----------------------
DQ250 = EcuProfile(
    key="dq250",
    display_name="DQ250 DSG (wet-clutch 6-speed)",
    module=TRANSMISSION,
    security_level=0x1B,
    sa2_script=None,
    blocks=[FlashBlock(0, "CAL", 0x0, 0x0)],  # placeholder; TCU map TBD
    notes="Transmission calibration; separate map set from the engine.",
)


PROFILES: Dict[str, EcuProfile] = {
    p.key: p for p in (MED17_5, SIMOS18_1, SIMOS18_10, DQ250)
}


def get_profile(key: str) -> EcuProfile:
    key = key.lower()
    if key not in PROFILES:
        raise KeyError(f"unknown ECU profile {key!r}; known: {', '.join(sorted(PROFILES))}")
    return PROFILES[key]


def guess_profile(system_name: str) -> Optional[EcuProfile]:
    """Heuristic match of an ECU's F197 'system name' string to a profile."""
    s = system_name.upper()
    if "SIMOS18.1" in s or "SC8" in s:
        return SIMOS18_1
    if "SIMOS18.10" in s or "SC9" in s:
        return SIMOS18_10
    if "MED17" in s:
        return MED17_5
    if "DQ250" in s:
        return DQ250
    return None
