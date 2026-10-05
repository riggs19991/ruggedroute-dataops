"""
VAG Diagnostic Trouble Code knowledge: decoding, numbering, failure types, texts.

What a VAG module hands over and what VCDS shows for it:

* **UDS (ISO 14229) modules** (2012 Golf TDI engine, ABS, gateway, cluster...): a
  3-byte DTC = 2 SAE bytes + 1 failure-type byte (FTB) plus a status byte. VCDS
  prints two lines, ``000665 - Boost Pressure Regulation: Control Range Not Reached``
  and ``P0299 00 [096] - Control Range Not Reached``: the 6-digit number is the
  decimal value of the 2 SAE bytes, ``00`` the FTB, ``[096]`` the status byte in
  decimal (verified: uds_vag.md §E/§G/§H, dtc_db.md §B/§C).
* **KWP2000 / TP 2.0 modules** (every 2008 R32 module, the TDI's DSG/BCM/...): a
  2-byte fault number plus a third byte. Numbers 0x4000..0x7FFF are SAE codes in the
  "5-digit" packing (``16683 = P0299``: ``16384 + first_digit*1024 + decimal(last
  three)``); everything else is a factory-only number (``00287 ABS Wheel Speed Sensor
  Rear Right (G44)``) with no P-code. The 5-digit number *is* the raw 16-bit value
  (verified three independent ways, dtc_db.md §C).

Descriptions come from the packaged database ``vagtune/data/dtc_db.json`` (generic
SAE wording, VW/Ross-Tech wording, factory 5-digit codes, Ross-Tech fault-type
suffixes), loaded once and lazily. The FTB table and the KWP "elaboration" table are
in code below with per-row verification flags; decoding an unverified row logs
``UNVERIFIED mapping: ...`` once per process.
"""

from __future__ import annotations

import logging
import re
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Union

log = logging.getLogger(__name__)

# ----------------------------------------------------------------- warn-once helper

_warned: Set[str] = set()
_warned_lock = threading.Lock()


def warn_unverified(key: str, message: str) -> None:
    """Log ``UNVERIFIED mapping: <message>`` once per process for ``key``."""
    with _warned_lock:
        if key in _warned:
            return
        _warned.add(key)
    log.warning("UNVERIFIED mapping: %s", message)


def _reset_unverified_warnings() -> None:   # tests only
    with _warned_lock:
        _warned.clear()


# ----------------------------------------------------------------- SAE packing

# First two bits of the first DTC byte select the system letter; next two bits are
# the first digit of the code.
_SYSTEM_LETTER = {0b00: "P", 0b01: "C", 0b10: "B", 0b11: "U"}
_LETTERS = "PCBU"
_CODE_RE = re.compile(r"^[PCBU][0-3][0-9A-F]{3}$")


def decode_dtc_number(number: int) -> str:
    """Convert a 3-byte DTC (packed int, high byte first) to e.g. 'P0301'."""
    b0 = (number >> 16) & 0xFF
    b1 = (number >> 8) & 0xFF
    # b2 (number & 0xFF) is the failure-type byte in the 3-byte format and is not part
    # of the 5-char code; see decode_uds_dtc for the full decode.
    letter = _SYSTEM_LETTER[(b0 >> 6) & 0x03]
    first_digit = (b0 >> 4) & 0x03
    second_digit = b0 & 0x0F
    third_digit = (b1 >> 4) & 0x0F
    fourth_digit = b1 & 0x0F
    return f"{letter}{first_digit}{second_digit:X}{third_digit:X}{fourth_digit:X}"


def sae_code_from_bytes(b0: int, b1: int) -> str:
    """Two SAE bytes -> ``P0299`` (the OBD mode 03 / UDS packing, verified)."""
    return decode_dtc_number((b0 << 16) | (b1 << 8))


def sae_bytes_from_code(code: str) -> bytes:
    """Inverse: ``P0299`` -> ``02 99``."""
    code = code.strip().upper()
    if not _CODE_RE.match(code):
        raise ValueError(f"not a 5-character SAE code: {code!r}")
    hi = (_LETTERS.index(code[0]) << 6) | (int(code[1]) << 4) | int(code[2], 16)
    return bytes([hi, int(code[3:5], 16)])


# ----------------------------------------------------------------- VAG numbering

def vag6_from_code(code: str) -> int:
    """UDS-era 6-digit number = decimal value of the 2 SAE bytes (P0299 -> 665, shown
    as ``000665``; verified against Ross-Tech titles)."""
    return int.from_bytes(sae_bytes_from_code(code), "big")


def code_from_vag6(number: int) -> str:
    if not 0 <= number <= 0xFFFF:
        raise ValueError("a 6-digit VAG number is a 16-bit value")
    return sae_code_from_bytes(number >> 8, number & 0xFF)


def vag5_from_code(code: str) -> Optional[int]:
    """KWP-era 5-digit factory number for an SAE code, or ``None`` when the code has
    hex letters in its last three characters (e.g. P17BF has no 5-digit number).

    ``N = 16384 + letter*4096 + first_digit*1024 + decimal(last three)`` with
    P=0, C=1, B=2, U=3 (verified for P and U against Ross-Tech / Bentley / vag-hub;
    the C/B extension follows the same bit layout, which KLineKWP1281Lib implements).
    """
    code = code.strip().upper()
    if not _CODE_RE.match(code) or not code[2:5].isdigit():
        return None
    return 0x4000 + _LETTERS.index(code[0]) * 4096 + int(code[1]) * 1024 + int(code[2:5], 10)


def legacy_number(code: str) -> Optional[int]:
    """Alias of :func:`vag5_from_code` (DESIGN_0.2 name)."""
    return vag5_from_code(code)


def code_from_vag5(number: int) -> Optional[str]:
    """5-digit factory number -> SAE code for 16384 <= N <= 32767 (last-three < 1000),
    else ``None`` (factory-only number)."""
    if not 0x4000 <= number <= 0x7FFF:
        return None
    n = number - 0x4000
    last3 = n % 1024
    if last3 > 999:
        return None
    return f"{_LETTERS[n // 4096]}{(n % 4096) // 1024}{last3:03d}"


def is_factory_only(number: int) -> bool:
    """True for KWP fault numbers that carry no SAE code (0..16383, >32767, or an
    invalid decimal field)."""
    return code_from_vag5(number) is None


# ----------------------------------------------------------------- failure type byte

@dataclass(frozen=True)
class FailureType:
    """One SAE J2012-DA / ISO 14229 Annex D failure-type byte row."""
    code: int
    text: str
    verified: bool
    source: str

    @property
    def unverified(self) -> bool:
        return not self.verified

    @property
    def category(self) -> str:
        return ftb_category(self.code)


# High-nibble category scheme (piembsystech, all 16 rows matched; secondary source).
FTB_CATEGORIES: Dict[int, str] = {
    0x0: "General Failure Information",
    0x1: "General Electrical Failures",
    0x2: "General Signal Failures",
    0x3: "FM/PWM Failures",
    0x4: "System Internal Failures",
    0x5: "System Programming Failures",
    0x6: "Algorithm-Based Failures",
    0x7: "Mechanical Failures",
    0x8: "Bus Signal/Message Failures",
    0x9: "Component Failures",
    0xA: "ISO/SAE reserved", 0xB: "ISO/SAE reserved", 0xC: "ISO/SAE reserved",
    0xD: "ISO/SAE reserved", 0xE: "ISO/SAE reserved",
    0xF: "Vehicle Manufacturer / System Supplier specific",
}


def ftb_category(ftb: int) -> str:
    return FTB_CATEGORIES.get((ftb >> 4) & 0xF, "unknown")


def _ft(code: int, text: str, verified: bool, source: str) -> Tuple[int, FailureType]:
    return code, FailureType(code, text, verified, source)


# Verified rows: present in both open-source tables the dtc_db sheet fetched
# (vinfast + neomotive, 31 rows, §G) and/or on autodtcs.com (uds_vag.md REPORTED->
# verified rows). Rows where those sources *conflict* are kept unverified:
#   0x1C/0x1D: autodtcs says "current below/above threshold", both other tables say
#              "voltage/current out of range" (and put current below/above at 0x18/0x19);
#   0x72: autodtcs "actuator stuck high" vs neomotive "actuator stuck open";
#   0x9D: autodtcs "over-temperature" vs neomotive 0x98 "component overtemperature".
# Everything else below the verified block is REPORTED (single source); neomotive's
# wording wins where the two differ (dtc_db.md REPORTED guidance).
FTB_TABLE: Dict[int, FailureType] = dict([
    _ft(0x00, "No Subtype Information", True, "vinfast+neomotive+autodtcs"),
    _ft(0x01, "General Electrical Failure", True, "vinfast+neomotive+rosstech C10E2 01"),
    _ft(0x02, "General Signal Failure", True, "vinfast+neomotive"),
    _ft(0x04, "System Internal Failure", True, "vinfast+neomotive+rosstech B1916 04"),
    _ft(0x07, "Mechanical Failure", True, "vinfast+neomotive"),
    _ft(0x11, "Circuit Short to Ground", True, "vinfast+neomotive+autodtcs"),
    _ft(0x12, "Circuit Short to Battery", True, "vinfast+neomotive+autodtcs"),
    _ft(0x13, "Circuit Open", True, "vinfast+neomotive+autodtcs"),
    _ft(0x14, "Circuit Short to Ground or Open", True, "vinfast+neomotive+autodtcs"),
    _ft(0x15, "Circuit Short to Battery or Open", True, "vinfast+neomotive+autodtcs"),
    _ft(0x16, "Circuit Voltage Below Threshold", True, "vinfast+neomotive+autodtcs"),
    _ft(0x17, "Circuit Voltage Above Threshold", True, "vinfast+neomotive+autodtcs"),
    _ft(0x18, "Circuit Current Below Threshold", True, "vinfast+neomotive"),
    _ft(0x19, "Circuit Current Above Threshold", True, "vinfast+neomotive"),
    _ft(0x1A, "Circuit Resistance Below Threshold", True, "vinfast+neomotive"),
    _ft(0x1B, "Circuit Resistance Above Threshold", True, "vinfast+neomotive"),
    _ft(0x1C, "Circuit Voltage Out of Range", False, "vinfast+neomotive; autodtcs conflicts"),
    _ft(0x1D, "Circuit Current Out of Range", False, "vinfast+neomotive; autodtcs conflicts"),
    _ft(0x29, "Signal Invalid", True, "vinfast+neomotive"),
    _ft(0x2F, "Signal Erratic", True, "vinfast+neomotive+autodtcs"),
    _ft(0x49, "Internal Electronic Failure", True, "vinfast+neomotive"),
    _ft(0x4A, "Incorrect Component Installed", True, "vinfast+neomotive"),
    _ft(0x54, "Missing Calibration", True, "vinfast+neomotive+rosstech C10E2 54"),
    _ft(0x62, "Signal Compare Failure", True, "vinfast+neomotive+autodtcs"),
    _ft(0x71, "Actuator Stuck", True, "vinfast+neomotive (autodtcs: stuck low)"),
    _ft(0x81, "Invalid Serial Data Received", True, "vinfast+neomotive"),
    _ft(0x83, "Value of Signal Protection Calculation Incorrect", True, "vinfast+neomotive"),
    _ft(0x87, "Missing Message", True, "vinfast+neomotive+autodtcs"),
    _ft(0x88, "Bus Off", True, "vinfast+neomotive"),
    _ft(0x92, "Performance or Incorrect Operation", True, "vinfast+neomotive"),
    _ft(0x96, "Component Internal Failure", True, "vinfast+neomotive+autodtcs"),
    # ---- REPORTED (single source or conflicting wording) ----
    _ft(0x03, "FM / PWM Failure", False, "vinfast"),
    _ft(0x05, "System Programming Failure", False, "neomotive"),
    _ft(0x08, "Bus Signal / Message Failure", False, "vinfast/neomotive wording differs"),
    _ft(0x09, "Component Internal Failure", False, "vinfast/neomotive wording differs"),
    _ft(0x1E, "Circuit Resistance Out of Range", False, "neomotive"),
    _ft(0x1F, "Circuit Intermittent", False, "neomotive"),
    _ft(0x21, "Signal Amplitude < Min", False, "vinfast/neomotive wording differs"),
    _ft(0x22, "Signal Amplitude > Max", False, "vinfast/neomotive wording differs"),
    _ft(0x23, "Signal Stuck Low", False, "neomotive"),
    _ft(0x24, "Signal Stuck High", False, "neomotive"),
    _ft(0x25, "Signal Shape / Waveform Failure", False, "neomotive"),
    _ft(0x26, "Signal Rate of Change Below Threshold", False, "neomotive"),
    _ft(0x27, "Signal Rate of Change Above Threshold", False, "neomotive"),
    _ft(0x28, "Signal Bias Level Out of Range", False, "neomotive"),
    _ft(0x31, "No Signal", False, "neomotive"),
    _ft(0x36, "Signal Frequency Too Low", False, "neomotive"),
    _ft(0x37, "Signal Frequency Too High", False, "neomotive"),
    _ft(0x38, "Signal Frequency Incorrect", False, "vinfast/neomotive wording differs"),
    _ft(0x41, "General Checksum Failure", False, "neomotive"),
    _ft(0x42, "General Memory Failure", False, "neomotive"),
    _ft(0x43, "Special Memory Failure", False, "neomotive"),
    _ft(0x44, "Data Memory Failure", False, "neomotive"),
    _ft(0x45, "Program Memory Failure", False, "neomotive"),
    _ft(0x46, "Calibration Memory Failure", False, "neomotive"),
    _ft(0x47, "Watchdog / Safety MCU Failure", False, "neomotive"),
    _ft(0x48, "Supervision Software Failure", False, "neomotive"),
    _ft(0x51, "Not Programmed", False, "neomotive"),
    _ft(0x52, "Not Activated", False, "neomotive"),
    _ft(0x53, "Deactivated", False, "neomotive"),
    _ft(0x55, "Not Configured", False, "vinfast/neomotive wording differs"),
    _ft(0x61, "Signal Calculation Failure", False, "neomotive"),
    _ft(0x63, "Circuit Protection Timeout", False, "neomotive"),
    _ft(0x64, "Signal Plausibility Failure", False, "neomotive"),
    _ft(0x65, "Signal Has Too Few Transitions", False, "neomotive"),
    _ft(0x66, "Signal Has Too Many Transitions", False, "neomotive"),
    _ft(0x67, "Signal Incorrect Event", False, "neomotive"),
    _ft(0x72, "Actuator Stuck Open", False, "neomotive; autodtcs says stuck high"),
    _ft(0x73, "Actuator Stuck Closed", False, "neomotive"),
    _ft(0x74, "Actuator Slipping", False, "neomotive"),
    _ft(0x75, "Emergency Position Not Reachable", False, "neomotive"),
    _ft(0x76, "Wrong Mounting Position", False, "neomotive"),
    _ft(0x77, "Commanded Position Not Reachable", False, "neomotive"),
    _ft(0x78, "Alignment / Adjustment Incorrect", False, "neomotive"),
    _ft(0x79, "Mechanical Linkage Failure", False, "neomotive"),
    _ft(0x7A, "Fluid Leak / Seal Failure", False, "neomotive"),
    _ft(0x82, "Alive Counter Incorrect", False, "vinfast/neomotive wording differs"),
    _ft(0x86, "Signal Invalid", False, "vinfast/neomotive wording differs"),
    _ft(0x89, "Signal Invalid / Invalid Serial Data", False, "vinfast"),
    _ft(0x91, "Parametric Parameter at Limit", False, "neomotive"),
    _ft(0x93, "No Operation", False, "neomotive"),
    _ft(0x94, "Unexpected Operation", False, "neomotive"),
    _ft(0x95, "Incorrect Assembly", False, "neomotive"),
    _ft(0x97, "Component Function Obstructed", False, "neomotive"),
    _ft(0x98, "Component Overtemperature", False, "neomotive"),
    _ft(0x9D, "Component or System Over-Temperature", False, "autodtcs; neomotive puts it at 0x98"),
])


def describe_ftb(ftb: int) -> FailureType:
    """Failure-type byte -> row (a category-only row for unknown bytes).

    Decoding an unverified row logs ``UNVERIFIED mapping`` once per process.
    """
    row = FTB_TABLE.get(ftb)
    if row is None:
        row = FailureType(ftb, f"{ftb_category(ftb)} (subtype 0x{ftb:02X} not in table)",
                          False, "category scheme only")
    if not row.verified:
        warn_unverified(f"ftb:{ftb:02X}",
                        f"failure-type byte 0x{ftb:02X} = {row.text!r} ({row.source}); "
                        "confirm against SAE J2012-DA / ISO 14229 Annex D")
    return row


# ----------------------------------------------------------------- KWP elaboration byte

# KWP1281/KWP2000 fault "elaboration" byte (third byte of a KWP fault record), bit 7 =
# intermittent, low 7 bits index this table (KLineKWP1281Lib fault_code_elaboration_EN.h,
# 83 rows, fetched source; dtc_db.md §F). Whether the Mk5 R32's KWP2000-over-TP2.0 modules
# use this byte or an ISO 14230 status byte is an OPEN question -> decode warns once.
KWP_INTERMITTENT_BIT = 0x80
KWP_ELABORATION: Dict[int, str] = {
    0x00: "-", 0x01: "Signal Shorted to Plus", 0x02: "Signal Shorted to Ground",
    0x03: "No Signal", 0x04: "Mechanical Malfunction", 0x05: "Input Open",
    0x06: "Signal too High", 0x07: "Signal too Low", 0x08: "Control Limit Surpassed",
    0x09: "Adaptation Limit Surpassed", 0x0A: "Adaptation Limit Not Reached",
    0x0B: "Control Limit Not Reached", 0x0C: "Adaptation Limit (Mul) Exceeded",
    0x0D: "Adaptation Limit (Mul) Not Reached", 0x0E: "Adaptation Limit (Add) Exceeded",
    0x0F: "Adaptation Limit (Add) Not Reached", 0x10: "Signal Outside Specifications",
    0x11: "Control Difference", 0x12: "Upper Limit", 0x13: "Lower Limit",
    0x14: "Malfunction in Basic Setting", 0x15: "Front Pressure Build-up Time too Long",
    0x16: "Front Pressure Reducing Time too Long", 0x17: "Rear Pressure Build-up Time too Long",
    0x18: "Rear Pressure Reducing Time too Long", 0x19: "Unknown Switch Condition",
    0x1A: "Output Open", 0x1B: "Implausible Signal", 0x1C: "Short to Plus",
    0x1D: "Short to Ground", 0x1E: "Open or Short to Plus", 0x1F: "Open or Short to Ground",
    0x20: "Resistance Too High", 0x21: "Resistance Too Low", 0x22: "No Elaboration Available",
    0x23: "-", 0x24: "Open Circuit", 0x25: "Faulty",
    0x26: "Output won't Switch or Short to Plus", 0x27: "Output won't Switch or Short to Ground",
    0x28: "Short to Another Output", 0x29: "Blocked or No Voltage",
    0x2A: "Speed Deviation too High", 0x2B: "Closed", 0x2C: "Short Circuit", 0x2D: "Connector",
    0x2E: "Leaking", 0x2F: "No Communications or Incorrectly Connected", 0x30: "Supply voltage",
    0x31: "No Communications", 0x32: "Setting (Early) Not Reached", 0x33: "Setting (Late) Not Reached",
    0x34: "Supply Voltage Too High", 0x35: "Supply Voltage Too Low", 0x36: "Incorrectly Equipped",
    0x37: "Adaptation Not Successful", 0x38: "In Limp-Home Mode", 0x39: "Electric Circuit Failure",
    0x3A: "Can't Lock", 0x3B: "Can't Unlock", 0x3C: "Won't Safe", 0x3D: "Won't De-Safe",
    0x3E: "No or Incorrect Adjustment", 0x3F: "Temperature Shut-Down", 0x40: "Not Currently Testable",
    0x41: "Unauthorized", 0x42: "Not Matched", 0x43: "Set-Point Not Reached",
    0x44: "Cylinder 1", 0x45: "Cylinder 2", 0x46: "Cylinder 3", 0x47: "Cylinder 4",
    0x48: "Cylinder 5", 0x49: "Cylinder 6", 0x4A: "Cylinder 7", 0x4B: "Cylinder 8",
    0x4C: "Terminal 30 missing", 0x4D: "Internal Supply Voltage", 0x4E: "Missing Messages",
    0x4F: "Please Check Fault Codes", 0x50: "Single-Wire Operation", 0x51: "Open", 0x52: "Activated",
}


def describe_kwp_elaboration(byte: int) -> Tuple[str, bool]:
    """KWP third byte -> (text, intermittent). Warns once: the use of this table for
    KWP2000-over-TP2.0 modules is unverified (dtc_db.md OPEN QUESTION 2/3)."""
    warn_unverified("kwp-elaboration",
                    "KWP fault third byte decoded with the KWP1281 elaboration table "
                    "(bit 7 = intermittent); the Mk5 TP2.0 modules may send an ISO 14230 "
                    "status byte instead - confirm with a VCDS scan next to a raw trace")
    text = KWP_ELABORATION.get(byte & 0x7F, f"elaboration 0x{byte & 0x7F:02X} (not in table)")
    return text, bool(byte & KWP_INTERMITTENT_BIT)


# ----------------------------------------------------------------- description database

_PLACEHOLDER_RE = re.compile(r"^(Reserved|Undocumented)", re.IGNORECASE)


@dataclass
class DtcInfo:
    """Result of a database lookup."""
    code: str
    description: Optional[str]        # generic / SAE wording
    vag_wording: Optional[str]        # VW / Ross-Tech wording
    variants: List[str] = field(default_factory=list)

    def text(self, prefer_vag: bool = True) -> Optional[str]:
        if prefer_vag:
            return self.vag_wording or self.description
        return self.description or self.vag_wording

    @property
    def found(self) -> bool:
        return bool(self.description or self.vag_wording)


class DtcDatabase:
    """The packaged ``dtc_db.json`` (codes, vag_wording, vag_5digit_only, vag_fault_variants)."""

    MAX_SIZE = 1_000_000

    def __init__(self, data: dict, *, size: int = 0) -> None:
        self.codes: Dict[str, str] = data.get("codes", {})
        self.vag_wording: Dict[str, str] = data.get("vag_wording", {})
        self.vag_5digit_only: Dict[str, str] = data.get("vag_5digit_only", {})
        self.vag_fault_variants: Dict[str, List[str]] = data.get("vag_fault_variants", {})
        self.stats: dict = data.get("stats", {})
        self.source_notes: str = data.get("source_notes", "")
        self.size = size
        if size > self.MAX_SIZE:
            log.warning("dtc_db.json is %d bytes (> %d target)", size, self.MAX_SIZE)
        # Defensive: the build script strips placeholders, but a hand-edited file might not.
        self.codes = {k: v for k, v in self.codes.items() if v and not _PLACEHOLDER_RE.match(v)}

    def __len__(self) -> int:
        return len(self.codes)

    def lookup(self, code: str) -> DtcInfo:
        code = code.strip().upper()
        return DtcInfo(code, self.codes.get(code), self.vag_wording.get(code),
                       list(self.vag_fault_variants.get(code, ())))

    def lookup_factory(self, number: int) -> Optional[str]:
        """Text for a factory-only KWP number (``00287`` style), or ``None``."""
        key = f"{number:05d}"
        text = self.vag_5digit_only.get(key)
        if text is None:
            return None
        return text

    def factory_variants(self, number: int) -> List[str]:
        return list(self.vag_fault_variants.get(f"{number:05d}", ()))


_db: Optional[DtcDatabase] = None
_db_lock = threading.Lock()
_db_failed = False


def load_db() -> Optional[DtcDatabase]:
    """Load the packaged database once (thread-safe). Returns ``None`` (after one
    warning) when the data file is missing, so decoding still works with the small
    built-in table."""
    global _db, _db_failed
    if _db is not None or _db_failed:
        return _db
    with _db_lock:
        if _db is not None or _db_failed:
            return _db
        try:
            from .. import data as _data
            raw = _data.read_json(_data.DTC_DB_FILENAME)
            size = _data.data_size(_data.DTC_DB_FILENAME)
            _db = DtcDatabase(raw, size=size)
            log.debug("loaded dtc_db.json: %d codes, %d bytes", len(_db), size)
        except (FileNotFoundError, OSError, ValueError) as exc:
            _db_failed = True
            log.warning("DTC database unavailable (%s); using the built-in mini table", exc)
    return _db


def _reset_db_cache() -> None:   # tests only
    global _db, _db_failed
    with _db_lock:
        _db = None
        _db_failed = False


def lookup(code: str, *, prefer_vag: bool = True) -> DtcInfo:
    """Description lookup for an SAE code. ``prefer_vag`` only affects
    :meth:`DtcInfo.text`; both wordings are returned."""
    db = load_db()
    if db is not None:
        return db.lookup(code)
    code = code.strip().upper()
    return DtcInfo(code, _FALLBACK_DB.get(code), None)


def lookup_factory(number: int) -> Optional[str]:
    db = load_db()
    return db.lookup_factory(number) if db is not None else None


# Compact built-in table: only used when the packaged database cannot be loaded.
_FALLBACK_DB: Dict[str, str] = {
    "P0101": "Mass or Volume Air Flow Circuit Range/Performance",
    "P0102": "Mass or Volume Air Flow Circuit Low Input",
    "P0106": "Manifold Absolute Pressure/Barometric Pressure Range/Performance",
    "P0111": "Intake Air Temperature Sensor Range/Performance",
    "P0112": "Intake Air Temperature Sensor Circuit Low",
    "P0113": "Intake Air Temperature Sensor Circuit High",
    "P0171": "System Too Lean (Bank 1)",
    "P0172": "System Too Rich (Bank 1)",
    "P0234": "Turbocharger/Supercharger Overboost Condition",
    "P0299": "Turbocharger/Supercharger Underboost Condition",
    "P2563": "Turbocharger Boost Control Position Sensor Circuit Range/Performance",
    "P0300": "Random/Multiple Cylinder Misfire Detected",
    "P0301": "Cylinder 1 Misfire Detected",
    "P0302": "Cylinder 2 Misfire Detected",
    "P0303": "Cylinder 3 Misfire Detected",
    "P0304": "Cylinder 4 Misfire Detected",
    "P0324": "Knock Control System Error",
    "P0327": "Knock Sensor 1 Circuit Low",
    "P0420": "Catalyst System Efficiency Below Threshold (Bank 1)",
    "P0421": "Warm Up Catalyst Efficiency Below Threshold (Bank 1)",
    "P0401": "Exhaust Gas Recirculation Flow Insufficient",
    "P2459": "Diesel Particulate Filter Regeneration Frequency",
    "P0087": "Fuel Rail/System Pressure Too Low",
    "P0089": "Fuel Pressure Regulator Performance",
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


def describe_dtc(code: str, *, prefer_vag: bool = False) -> str:
    """Short text for an SAE code: the curated 0.1.0 table first (stable wording for
    the common codes), then the database (generic by default, VW wording with
    ``prefer_vag=True``), else a category description."""
    code = code.strip().upper()
    info = lookup(code)
    if prefer_vag and info.vag_wording:
        return info.vag_wording
    if code in _FALLBACK_DB:
        return _FALLBACK_DB[code]
    text = info.text(prefer_vag)
    if text:
        return text
    prefix = code[:2].upper()
    return _CATEGORY.get(prefix, "Unknown code category") + " (no specific description on file)"


# ----------------------------------------------------------------- VagDtc

@dataclass
class VagDtc:
    """A decoded fault the way VCDS would show it.

    ``sae_code`` is ``""`` for factory-only KWP numbers (then ``vag5`` names it);
    ``vag6`` is the 6-digit string for codes that have an SAE form; ``vag5`` the
    5-digit factory number or ``None`` for hex-letter codes; ``ftb`` is the UDS
    failure-type byte or, for KWP, the elaboration byte (bit 7 intermittent).
    """
    sae_code: str
    ftb: int
    ftb_text: str
    status: int
    status_text: str
    vag6: Optional[str]
    vag5: Optional[int]
    description: Optional[str]
    vag_wording: Optional[str]
    source: str                      # "uds" | "kwp"
    raw: bytes = b""
    ftb_verified: bool = True
    variants: List[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        """VW wording first (what VCDS prints), then generic, then a category."""
        if self.vag_wording:
            return self.vag_wording
        if self.description:
            return self.description
        if self.sae_code:
            return describe_dtc(self.sae_code)
        return "factory fault code (no description on file)"

    @property
    def number(self) -> int:
        """3-byte UDS number (``0x029900``) or the 16-bit KWP number for KWP faults."""
        return int.from_bytes(self.raw[:3] if self.source == "uds" else self.raw[:2], "big")

    @property
    def factory_number(self) -> Optional[str]:
        return f"{self.vag5:05d}" if self.vag5 is not None else None

    @property
    def is_factory_only(self) -> bool:
        return not self.sae_code

    @property
    def intermittent(self) -> bool:
        if self.source == "kwp":
            return bool(self.ftb & KWP_INTERMITTENT_BIT)
        return bool(self.status & 0x20) and not (self.status & 0x01)

    @property
    def active(self) -> bool:
        if self.source == "kwp":
            return not self.intermittent
        return bool(self.status & 0x01)

    def __str__(self) -> str:
        return vcds_style(self)


def _status_text_uds(status: int) -> str:
    from ..uds import services as S
    names = [name for bit, name in sorted(S.DTC_STATUS_NAMES.items()) if status & bit]
    return ", ".join(names) if names else "no status bits set"


def decode_uds_dtc(dtc: Union[bytes, int], status: int) -> VagDtc:
    """3-byte UDS DTC (bytes or packed int) + status byte -> :class:`VagDtc`."""
    raw = dtc.to_bytes(3, "big") if isinstance(dtc, int) else bytes(dtc)
    if len(raw) != 3:
        raise ValueError("a UDS DTC is 3 bytes")
    code = sae_code_from_bytes(raw[0], raw[1])
    ftb = describe_ftb(raw[2])
    info = lookup(code)
    return VagDtc(
        sae_code=code, ftb=raw[2], ftb_text=ftb.text, status=status,
        status_text=_status_text_uds(status),
        vag6=f"{int.from_bytes(raw[:2], 'big'):06d}", vag5=vag5_from_code(code),
        description=info.description, vag_wording=info.vag_wording, source="uds",
        raw=raw + bytes([status & 0xFF]), ftb_verified=ftb.verified, variants=info.variants,
    )


def decode_kwp_dtc(dtc: Union[bytes, int], status: int) -> VagDtc:
    """2-byte KWP fault number + third byte -> :class:`VagDtc`.

    Numbers 0x4000..0x7FFF decode to an SAE code (``0x4127 = 16679 = P0295``...);
    anything else is a factory-only number looked up in ``vag_5digit_only``. The third
    byte is decoded with the KWP1281 elaboration table (UNVERIFIED for TP2.0/KWP2000
    modules; warns once).
    """
    raw = dtc.to_bytes(2, "big") if isinstance(dtc, int) else bytes(dtc)
    if len(raw) != 2:
        raise ValueError("a KWP fault number is 2 bytes")
    number = int.from_bytes(raw, "big")
    elab_text, intermittent = describe_kwp_elaboration(status)
    status_text = elab_text + (" (intermittent)" if intermittent else "")
    code = code_from_vag5(number)
    if code is None:
        db = load_db()
        text = db.lookup_factory(number) if db is not None else None
        variants = db.factory_variants(number) if db is not None else []
        return VagDtc(sae_code="", ftb=status, ftb_text=elab_text, status=status,
                      status_text=status_text, vag6=None, vag5=number,
                      description=text, vag_wording=text, source="kwp",
                      raw=raw + bytes([status & 0xFF]), ftb_verified=False, variants=variants)
    info = lookup(code)
    return VagDtc(sae_code=code, ftb=status, ftb_text=elab_text, status=status,
                  status_text=status_text, vag6=f"{vag6_from_code(code):06d}", vag5=number,
                  description=info.description, vag_wording=info.vag_wording, source="kwp",
                  raw=raw + bytes([status & 0xFF]), ftb_verified=False, variants=info.variants)


def vcds_style(d: VagDtc) -> str:
    """One VCDS-like line.

    UDS: ``P0299 00 [096] - Boost Pressure Regulation: Control Range Not Reached``
    (code, FTB hex, status decimal in brackets, text).
    KWP: ``16683 - P0299 - <text> - Signal Outside Specifications - Intermittent`` or
    ``00287 - ABS Wheel Speed Sensor Rear Right (G44) - Signal Outside Specifications``.
    """
    if d.source == "uds":
        return f"{d.sae_code} {d.ftb:02X} [{d.status:03d}] - {d.text}"
    head = f"{d.vag5:05d}" if d.vag5 is not None else "?????"
    parts = [head]
    if d.sae_code:
        parts.append(d.sae_code)
    parts.append(d.text)
    if d.ftb_text and d.ftb_text != "-":
        parts.append(d.ftb_text)
    if d.intermittent:
        parts.append("Intermittent")
    return " - ".join(parts)
