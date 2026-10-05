"""VAG-specific knowledge: module addressing, DTCs, SA2 seed/key, ECU profiles."""

from __future__ import annotations

from .dtc import decode_dtc_number, describe_dtc
from .ecu import DtcEntry, EcuIdentity, VagEcuSession
from .modules import FUNCTIONAL_REQUEST_ID, MODULES, ModuleAddress
from .profiles import PROFILES, EcuProfile, FlashBlock, get_profile, guess_profile
from .sa2 import Sa2Error, Sa2Interpreter, make_seed_key_fn

__all__ = [
    "decode_dtc_number",
    "describe_dtc",
    "DtcEntry",
    "EcuIdentity",
    "VagEcuSession",
    "ModuleAddress",
    "MODULES",
    "FUNCTIONAL_REQUEST_ID",
    "EcuProfile",
    "FlashBlock",
    "PROFILES",
    "get_profile",
    "guess_profile",
    "Sa2Interpreter",
    "Sa2Error",
    "make_seed_key_fn",
]
