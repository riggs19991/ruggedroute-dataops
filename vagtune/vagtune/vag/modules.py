"""
VAG on-bus module addressing and identification data identifiers.

On the OBD2 diagnostic CAN bus (500 kbps), each control module answers at a fixed
pair of 11-bit CAN IDs: the tester sends to ``request_id`` and the module replies on
``response_id`` (response = request + 8 for the engine/transmission range).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ModuleAddress:
    name: str
    request_id: int
    response_id: int
    description: str = ""


# The modules you actually tune/diagnose first. (Diagnostic address -> CAN IDs.)
ENGINE = ModuleAddress("engine", 0x7E0, 0x7E8, "Engine control module (ECM/Motronic)")
TRANSMISSION = ModuleAddress("transmission", 0x7E1, 0x7E9, "DSG/automatic transmission control module")
ABS = ModuleAddress("abs", 0x713, 0x77D, "ABS/ESP brake electronics")
HALDEX = ModuleAddress("haldex", 0x70F, 0x779, "Haldex AWD coupling (4Motion)")
GATEWAY = ModuleAddress("gateway", 0x710, 0x77A, "CAN gateway (central electronics)")

MODULES: Dict[str, ModuleAddress] = {
    m.name: m for m in (ENGINE, TRANSMISSION, ABS, HALDEX, GATEWAY)
}

# Functional (broadcast) request ID: every module listens here; used for things like
# a broadcast TesterPresent. Physical addressing (above) is used for real work.
FUNCTIONAL_REQUEST_ID = 0x7DF


# ---- Identification DIDs (ISO 14229 0x22) commonly populated on VAG ECUs --------
@dataclass(frozen=True)
class IdentDid:
    did: int
    name: str
    decode: str = "ascii"  # "ascii" or "hex"


IDENT_DIDS = [
    IdentDid(0xF190, "VIN"),
    IdentDid(0xF187, "VW Spare Part Number"),
    IdentDid(0xF189, "VW Application Software Version"),
    IdentDid(0xF191, "VW ECU Hardware Number"),
    IdentDid(0xF1A3, "VW ECU Hardware Version"),
    IdentDid(0xF197, "VW System Name / Engine Type"),
    IdentDid(0xF1AD, "Engine Code Letters"),
    IdentDid(0xF17C, "VW FAZIT Identification String"),
    IdentDid(0xF18C, "ECU Serial Number"),
    IdentDid(0xF19E, "ASAM/ODX File Identifier"),
    IdentDid(0xF1A2, "ASAM/ODX File Version"),
    IdentDid(0xF1DF, "ECU Programming Information", decode="hex"),
    IdentDid(0xF1F4, "Boot Loader Identification"),
    IdentDid(0xF186, "Active Diagnostic Session", decode="hex"),
]


def decode_ident_value(did_def: IdentDid, raw: bytes) -> str:
    if did_def.decode == "hex":
        return raw.hex(" ").upper()
    # ASCII, trimming trailing NULs and padding spaces.
    text = raw.split(b"\x00", 1)[0].decode("latin-1", errors="replace").rstrip()
    return text or raw.hex(" ").upper()
