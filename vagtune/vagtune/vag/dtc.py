"""
Diagnostic Trouble Code decoding.

Two jobs:

1. ``decode_dtc_number`` turns the 3-byte DTC an ECU returns into the familiar
   P/C/B/U alphanumeric code (ISO 15031-6 / SAE J2012 encoding of the first byte).

2. ``describe_dtc`` looks up a short human description. The generic (SAE) powertrain
   range is well standardized; manufacturer-specific codes are not, so the database
   here covers common generic codes plus a handful of VAG-relevant ones, and falls
   back to a category description for anything unknown.
"""

from __future__ import annotations

from typing import Dict

# First two bits of the first DTC byte select the system letter; next two bits are
# the first digit of the code.
_SYSTEM_LETTER = {0b00: "P", 0b01: "C", 0b10: "B", 0b11: "U"}


def decode_dtc_number(number: int) -> str:
    """Convert a 3-byte DTC (packed int, high byte first) to e.g. 'P0301'."""
    b0 = (number >> 16) & 0xFF
    b1 = (number >> 8) & 0xFF
    # b2 (number & 0xFF) is the failure-type/fault byte in the 3-byte format and is
    # not part of the 5-char code; it is surfaced separately via the status byte.
    letter = _SYSTEM_LETTER[(b0 >> 6) & 0x03]
    first_digit = (b0 >> 4) & 0x03
    second_digit = b0 & 0x0F
    third_digit = (b1 >> 4) & 0x0F
    fourth_digit = b1 & 0x0F
    return f"{letter}{first_digit}{second_digit:X}{third_digit:X}{fourth_digit:X}"


# Compact description table. Not exhaustive - extend as you catalogue codes from the
# cars you work on. Generic SAE codes first, then VAG-common ones.
_DTC_DB: Dict[str, str] = {
    # Fuel & air metering
    "P0101": "Mass or Volume Air Flow Circuit Range/Performance",
    "P0102": "Mass or Volume Air Flow Circuit Low Input",
    "P0106": "Manifold Absolute Pressure/Barometric Pressure Range/Performance",
    "P0111": "Intake Air Temperature Sensor Range/Performance",
    "P0112": "Intake Air Temperature Sensor Circuit Low",
    "P0113": "Intake Air Temperature Sensor Circuit High",
    "P0171": "System Too Lean (Bank 1)",
    "P0172": "System Too Rich (Bank 1)",
    # Boost / forced induction (very relevant to a tuned 2.0T)
    "P0234": "Turbocharger/Supercharger Overboost Condition",
    "P0299": "Turbocharger/Supercharger Underboost Condition",
    "P2563": "Turbocharger Boost Control Position Sensor Circuit Range/Performance",
    # Ignition / misfire
    "P0300": "Random/Multiple Cylinder Misfire Detected",
    "P0301": "Cylinder 1 Misfire Detected",
    "P0302": "Cylinder 2 Misfire Detected",
    "P0303": "Cylinder 3 Misfire Detected",
    "P0304": "Cylinder 4 Misfire Detected",
    # Knock / timing
    "P0324": "Knock Control System Error",
    "P0327": "Knock Sensor 1 Circuit Low",
    # Emissions components (will trip if you remove cats on an off-road car)
    "P0420": "Catalyst System Efficiency Below Threshold (Bank 1)",
    "P0421": "Warm Up Catalyst Efficiency Below Threshold (Bank 1)",
    "P0401": "Exhaust Gas Recirculation Flow Insufficient",
    "P2459": "Diesel Particulate Filter Regeneration Frequency",
    # Fuel system (HPFP common on direct-injection VAG)
    "P0087": "Fuel Rail/System Pressure Too Low",
    "P0089": "Fuel Pressure Regulator Performance",
    # Communication / gateway (U-codes)
    "U0100": "Lost Communication With ECM/PCM",
    "U0101": "Lost Communication With TCM",
    "U0121": "Lost Communication With ABS Control Module",
}

_CATEGORY = {
    "P0": "Generic powertrain (fuel, air, emissions, ignition, speed/idle)",
    "P1": "Manufacturer-specific powertrain",
    "P2": "Generic powertrain (injector, catalyst, auxiliary emissions)",
    "P3": "Generic/manufacturer powertrain (misfire, ignition)",
    "C0": "Generic chassis (ABS, traction, steering)",
    "C1": "Manufacturer-specific chassis",
    "B0": "Generic body (airbags, climate, lighting)",
    "B1": "Manufacturer-specific body",
    "U0": "Generic network/communication",
    "U1": "Manufacturer-specific network/communication",
}


def describe_dtc(code: str) -> str:
    if code in _DTC_DB:
        return _DTC_DB[code]
    prefix = code[:2]
    return _CATEGORY.get(prefix, "Unknown code category") + " (no specific description on file)"
