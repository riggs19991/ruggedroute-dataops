"""
SAE J1979 / ISO 15031-5 data tables: Mode 01/02 PIDs, bit/enumeration decodes,
supported-ID bitmaps, DTC bytes, Mode 06 OBDMID/TID/UASID tables, Mode 09 InfoTypes.

Everything in here is pure data + decoders (no I/O), so the client, the simulator,
the datalogger and the measuring-block mirror (UDS 0xF4xx DIDs) share one source.

Sources: the project's OBD-II fact sheet (ISO 15765-4:2005, ISO 15031-5:2006 incl.
Annexes A/B/D/E/G, the Wikipedia PID table and the dashlogic listing for PIDs above
0x5A). Rows the sheet lists as *Reported/unverified* are marked ``unverified=True``
and carry a ``# UNVERIFIED:`` comment; decoding one logs ``UNVERIFIED mapping: ...``
once per process via :func:`warn_unverified`.

Conventions:

* A decoder receives the data bytes that follow the echoed PID (``A, B, C, ...``) and
  returns a number, a string (enumerations), a ``set`` (support bitmaps) or a ``dict``
  (multi-value PIDs; keys only for sensors whose support bit is set).
* Decoders never round; the CLI formats.
* ``u16(A,B) = A*256+B``; ``s16`` is two's complement of that.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Set, Tuple

log = logging.getLogger(__name__)

Decoder = Callable[[bytes], Any]

# ---------------------------------------------------------------- unverified facts

_warned: Set[str] = set()


def warn_unverified(key: str, message: str) -> None:
    """Log ``UNVERIFIED mapping: <message>`` once per process for ``key``."""
    if key in _warned:
        return
    _warned.add(key)
    log.warning("UNVERIFIED mapping: %s", message)


def _reset_unverified_warnings() -> None:   # tests only
    _warned.clear()


# ---------------------------------------------------------------- byte helpers

def _u16(d: bytes, i: int = 0) -> int:
    return (d[i] << 8) | d[i + 1]


def _s16(d: bytes, i: int = 0) -> int:
    v = _u16(d, i)
    return v - 65536 if v > 32767 else v


def _u32(d: bytes, i: int = 0) -> int:
    return (d[i] << 24) | (d[i + 1] << 16) | (d[i + 2] << 8) | d[i + 3]


def _pct255(a: int) -> float:
    return a * 100 / 255


def _trim(a: int) -> float:
    """Fuel-trim style ``A*100/128-100`` (-100..99.2 %)."""
    return a * 100 / 128 - 100


def _bit(v: int, n: int) -> bool:
    return bool((v >> n) & 1)


# ======================================================================= bitmaps

#: PIDs (and OBDMIDs / TIDs / InfoTypes) that carry a "supported IDs" bitmap.
SUPPORT_BASES: Tuple[int, ...] = (0x00, 0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0, 0xE0)


def is_support_id(pid: int) -> bool:
    return pid in SUPPORT_BASES


def parse_supported(base: int, abcd: bytes) -> Set[int]:
    """Decode a 4-byte supported-ID bitmap whose Data A bit 7 means ``base + 1``.

    ISO 15031-5 Annex A: Data A bit 7 -> base+1 ... Data D bit 0 -> base+32
    (1 = supported). Worked example: ``BE1FA813`` at base 0 -> {01,03,04,05,06,07,
    0C,0D,0E,0F,10,11,13,15,1C,1F,20}.
    """
    if len(abcd) < 4:
        raise ValueError(f"supported-ID bitmap needs 4 bytes, got {len(abcd)}")
    bits = int.from_bytes(abcd[:4], "big")
    return {base + 32 - i for i in range(32) if (bits >> i) & 1}


def build_supported(base: int, ids: Sequence[int]) -> bytes:
    """Inverse of :func:`parse_supported` (used by the simulator)."""
    bits = 0
    for pid in ids:
        if base < pid <= base + 32:
            bits |= 1 << (32 - (pid - base))
    return bits.to_bytes(4, "big")


def next_support_id(base: int) -> Optional[int]:
    """The bitmap ID that covers the range after ``base`` (0x00 -> 0x20 ... 0xC0 -> 0xE0)."""
    nxt = base + 0x20
    return nxt if nxt in SUPPORT_BASES else None


# ========================================================================== DTCs

_DTC_LETTERS = "PCBU"


def decode_dtc(hi: int, lo: int) -> str:
    """Two DTC bytes -> ``P0143`` style code (ISO 15031-5 §7.3.1, W: ``C1 58`` -> U0158)."""
    return _DTC_LETTERS[hi >> 6] + str((hi >> 4) & 3) + f"{hi & 0xF:X}{lo:02X}"


def encode_dtc(code: str) -> bytes:
    """Inverse of :func:`decode_dtc` (``"P0143"`` -> ``01 43``)."""
    code = code.strip().upper()
    if len(code) != 5 or code[0] not in _DTC_LETTERS or code[1] not in "0123":
        raise ValueError(f"not a 5-character DTC: {code!r}")
    hi = (_DTC_LETTERS.index(code[0]) << 6) | (int(code[1]) << 4) | int(code[2], 16)
    lo = int(code[3:5], 16)
    return bytes([hi, lo])


def parse_dtc_list(payload: bytes) -> List[str]:
    """Parse the bytes after a ``43``/``47``/``4A`` SID: ``<#DTC> [hi lo]...``.

    ISO example ``06 01 43 01 96 02 34 02 CD 03 57 0A 24`` -> P0143, P0196, P0234,
    P02CD, P0357, P0A24. ``00 00`` pairs (K-line style filler) are skipped.
    """
    if not payload:
        return []
    n = payload[0]
    body = payload[1:1 + 2 * n]
    if len(body) < 2 * n:
        log.warning("DTC response announces %d codes but carries %d bytes", n, len(body))
    out: List[str] = []
    for i in range(0, len(body) - 1, 2):
        hi, lo = body[i], body[i + 1]
        if (hi, lo) != (0, 0):
            out.append(decode_dtc(hi, lo))
    return out


# ================================================================ enumerations

FUEL_SYSTEM_STATUS: Dict[int, str] = {
    0: "engine off (no status)",
    1: "open loop (conditions for closed loop not yet met)",
    2: "closed loop (oxygen sensor feedback)",
    4: "open loop (driving conditions: power enrichment / deceleration)",
    8: "open loop (system fault)",
    16: "closed loop with oxygen sensor fault",
}

SECONDARY_AIR_STATUS: Dict[int, str] = {
    1: "upstream of first catalytic converter",
    2: "downstream of first catalytic converter inlet",
    4: "atmosphere / off",
    8: "pump commanded on for diagnostics",   # W only; ISO5:2006 defines bits 0-2
}

# PID 1C. Values 1-13 and 17-35 per W (ISO5 Table B.23 for 1-11); 14-16 differ between
# ISO 15031-5:2006 (EURO IV B1 / EURO V B2 / EURO EEV C, later moved to PID 5F) and the
# current J1979-DA as reproduced by W. The W reading is used and flagged below.
OBD_STANDARDS: Dict[int, str] = {
    1: "OBD-II (CARB)", 2: "OBD (EPA)", 3: "OBD and OBD-II", 4: "OBD-I",
    5: "not OBD compliant", 6: "EOBD", 7: "EOBD and OBD-II", 8: "EOBD and OBD",
    9: "EOBD, OBD and OBD-II", 10: "JOBD", 11: "JOBD and OBD-II", 12: "JOBD and EOBD",
    13: "JOBD, EOBD and OBD-II",
    14: "OBD, EOBD and KOBD",              # UNVERIFIED: ISO5:2006 says EURO IV B1
    15: "OBD, OBD-II, EOBD and KOBD",      # UNVERIFIED: ISO5:2006 says EURO V B2
    16: "reserved",                        # UNVERIFIED: ISO5:2006 says EURO EEV C
    17: "EMD", 18: "EMD+", 19: "HD OBD-C", 20: "HD OBD", 21: "WWH OBD", 22: "reserved",
    23: "HD EOBD-I", 24: "HD EOBD-I N", 25: "HD EOBD-II", 26: "HD EOBD-II N", 27: "HD ZEV",
    28: "OBDBr-1", 29: "OBDBr-2", 30: "KOBD", 31: "IOBD I", 32: "IOBD II",
    33: "HD EOBD-IV (Heavy Duty Euro OBD Stage VI)", 34: "OBD, OBD-II and HD OBD", 35: "OBDBr-3",
}
_OBD_STANDARD_UNVERIFIED = {14, 15, 16}

FUEL_TYPES: Dict[int, str] = {
    0: "not available", 1: "gasoline", 2: "methanol", 3: "ethanol", 4: "diesel", 5: "LPG",
    6: "CNG", 7: "propane", 8: "electric", 9: "bifuel gasoline", 10: "bifuel methanol",
    11: "bifuel ethanol", 12: "bifuel LPG", 13: "bifuel CNG", 14: "bifuel propane",
    15: "bifuel electricity", 16: "bifuel electric and combustion", 17: "hybrid gasoline",
    18: "hybrid ethanol", 19: "hybrid diesel", 20: "hybrid electric",
    21: "hybrid electric and combustion", 22: "hybrid regenerative", 23: "bifuel diesel",
}

# PID 5F (DASH): the three values ISO5:2006 used to keep in PID 1C.
EMISSION_REQUIREMENTS: Dict[int, str] = {
    0x0E: "Heavy Duty Vehicles (EURO IV) B1",
    0x0F: "Heavy Duty Vehicles (EURO V) B2",
    0x10: "Heavy Duty Vehicles (EURO EEV) C",
}

_CONTROL_STATUS = {0: "reserved", 1: "open loop", 2: "closed loop", 3: "fault present"}
_MI_STATUS = {0: "off", 1: "on-demand", 2: "short", 3: "continuous", 0xE: "error", 0xF: "n/a"}
_DISPLAY_STRATEGY = {0: "nondiscriminatory", 1: "discriminatory", 3: "n/a"}
_INDUCEMENT_LEVEL = {0: "inactive", 1: "enabled", 2: "active", 3: "not supported"}


def decode_obd_standard(a: int) -> str:
    if 251 <= a <= 255:
        return "not available for assignment (SAE J1939 special meaning)"
    if a in _OBD_STANDARD_UNVERIFIED:
        warn_unverified("pid1c-14-16", f"PID 1C value {a} decoded per current J1979-DA (W); "
                                       "ISO 15031-5:2006 assigned EURO IV/V/EEV here")
    return OBD_STANDARDS.get(a, f"reserved ({a})")


def decode_fuel_system(a: int) -> str:
    if a in FUEL_SYSTEM_STATUS:
        return FUEL_SYSTEM_STATUS[a]
    return f"invalid (0x{a:02X})"


def decode_one_hot(table: Mapping[int, str], a: int) -> str:
    if a in table:
        return table[a]
    if a == 0:
        return "none"
    return f"invalid (0x{a:02X})"


# ======================================================== PID 01 / 41 readiness

#: Non-continuous monitor names, bit 0..7 of bytes C/D, per ignition type.
SPARK_MONITORS: Tuple[Optional[str], ...] = (
    "catalyst", "heated_catalyst", "evap", "secondary_air",
    "gpf_or_ac_refrigerant",      # W: gasoline particulate filter; ISO5:2006: A/C refrigerant
    "o2_sensor", "o2_heater", "egr_vvt",
)
COMPRESSION_MONITORS: Tuple[Optional[str], ...] = (
    "nmhc_catalyst", "nox_scr_aftertreatment", None, "boost_pressure",
    None, "exhaust_gas_sensor", "pm_filter", "egr_vvt",
)
CONTINUOUS_MONITORS: Tuple[str, ...] = ("misfire", "fuel_system", "components")

MONITOR_LABELS: Dict[str, str] = {
    "misfire": "Misfire", "fuel_system": "Fuel system", "components": "Comprehensive components",
    "catalyst": "Catalyst", "heated_catalyst": "Heated catalyst", "evap": "Evaporative system",
    "secondary_air": "Secondary air system", "gpf_or_ac_refrigerant": "GPF / A/C refrigerant",
    "o2_sensor": "Oxygen sensor", "o2_heater": "Oxygen sensor heater", "egr_vvt": "EGR / VVT system",
    "nmhc_catalyst": "NMHC catalyst", "nox_scr_aftertreatment": "NOx / SCR aftertreatment",
    "boost_pressure": "Boost pressure", "exhaust_gas_sensor": "Exhaust gas sensor",
    "pm_filter": "PM filter",
}


@dataclass(frozen=True)
class MonitorState:
    """One readiness monitor.

    For PID 01 ``available`` means "supported" and ``complete`` means "complete since
    DTCs cleared"; for PID 41 ``available`` means "enabled this monitoring cycle" and
    ``complete`` means "complete this monitoring cycle" (ISO 15031-5 Table B.46).
    """
    name: str
    available: bool
    complete: bool

    @property
    def label(self) -> str:
        return MONITOR_LABELS.get(self.name, self.name)


@dataclass(frozen=True)
class MonitorStatus:
    """Decoded PID 01 (since DTCs cleared) or PID 41 (this drive cycle)."""
    mil: bool
    dtc_count: int
    compression_ignition: bool
    continuous: Dict[str, MonitorState]
    non_continuous: Dict[str, MonitorState]
    this_cycle: bool = False
    raw: bytes = b""

    @property
    def ignition(self) -> str:
        return "compression" if self.compression_ignition else "spark"

    def all_monitors(self) -> List[MonitorState]:
        return list(self.continuous.values()) + list(self.non_continuous.values())

    def incomplete(self) -> List[str]:
        return [m.name for m in self.all_monitors() if m.available and not m.complete]

    @property
    def ready(self) -> bool:
        """True when every supported/enabled monitor reports complete."""
        return not self.incomplete()


def decode_monitor_status(data: bytes, *, this_cycle: bool = False,
                          compression_ignition: Optional[bool] = None) -> MonitorStatus:
    """Decode the 4 data bytes of PID 01 (or PID 41 with ``this_cycle=True``).

    Byte A: bit 7 MIL, bits 6..0 confirmed DTC count (PID 41: always 0).
    Byte B: bits 0-2 continuous monitors supported/enabled (misfire, fuel, components),
    bit 3 ignition type (0 spark, 1 compression), bits 4-6 "not complete" flags.
    Bytes C/D: availability / incompleteness of the non-continuous monitors; the bit
    meaning depends on the ignition type (:data:`SPARK_MONITORS` /
    :data:`COMPRESSION_MONITORS`). ``compression_ignition`` overrides byte B bit 3
    (useful for PID 41 on an ECU that does not repeat the flag there).
    """
    if len(data) < 4:
        raise ValueError(f"PID {'41' if this_cycle else '01'} needs 4 bytes, got {len(data)}")
    a, b, c, d = data[:4]
    ci = _bit(b, 3) if compression_ignition is None else bool(compression_ignition)
    continuous = {
        name: MonitorState(name, _bit(b, i), not _bit(b, i + 4))
        for i, name in enumerate(CONTINUOUS_MONITORS)
    }
    names = COMPRESSION_MONITORS if ci else SPARK_MONITORS
    non_continuous = {
        name: MonitorState(name, _bit(c, i), not _bit(d, i))
        for i, name in enumerate(names) if name is not None
    }
    return MonitorStatus(mil=_bit(a, 7), dtc_count=a & 0x7F, compression_ignition=ci,
                         continuous=continuous, non_continuous=non_continuous,
                         this_cycle=this_cycle, raw=bytes(data[:4]))


def encode_monitor_status(*, mil: bool, dtc_count: int, compression_ignition: bool,
                          supported: Mapping[str, bool], complete: Mapping[str, bool],
                          this_cycle: bool = False) -> bytes:
    """Inverse of :func:`decode_monitor_status` (simulator helper)."""
    a = 0 if this_cycle else ((0x80 if mil else 0) | (dtc_count & 0x7F))
    b = 0x08 if compression_ignition else 0
    for i, name in enumerate(CONTINUOUS_MONITORS):
        if supported.get(name, False):
            b |= 1 << i
            if not complete.get(name, True):
                b |= 1 << (i + 4)
    c = d = 0
    names = COMPRESSION_MONITORS if compression_ignition else SPARK_MONITORS
    for i, name in enumerate(names):
        if name is not None and supported.get(name, False):
            c |= 1 << i
            if not complete.get(name, True):
                d |= 1 << i
    return bytes([a, b, c, d])


# ===================================================================== scaling

@dataclass(frozen=True)
class ScalingOverrides:
    """ECU-reported scaling from PID 4F (Data A, equivalence ratio) and PID 50 (Data A, MAF).

    ISO 15031-5 Tables B.60/B.61: when PID 4F Data A != 0 the lambda scale for PIDs
    24-2B, 34-3B and 44 becomes ``A/65535`` per bit; when PID 50 Data A != 0 the MAF
    scale for PID 10 becomes ``A*10/65535`` g/s per bit. Bytes B/C/D of PID 4F are
    only *maxima* in the fetched text and are not applied (logged by the client).
    """
    pid4f_a: int = 0
    pid50_a: int = 0

    @property
    def lambda_scale(self) -> float:
        return self.pid4f_a / 65535 if self.pid4f_a else 2 / 65536

    @property
    def maf_scale(self) -> float:
        return self.pid50_a * 10 / 65535 if self.pid50_a else 0.01


DEFAULT_SCALING = ScalingOverrides()
LAMBDA_PIDS: frozenset = frozenset(range(0x24, 0x2C)) | frozenset(range(0x34, 0x3C)) | {0x44}


# ====================================================================== decoders

def _dec_o2_narrow(d: bytes) -> Dict[str, Any]:
    """PIDs 14-1B: A/200 V, B*100/128-100 % STFT (B == 0xFF: sensor not used in trim)."""
    return {"voltage": d[0] / 200, "stft": None if d[1] == 0xFF else _trim(d[1])}


def _dec_o2_lambda_voltage(scale: float) -> Decoder:
    def dec(d: bytes) -> Dict[str, float]:
        return {"lambda": _u16(d, 0) * scale, "voltage": _u16(d, 2) * 8 / 65536}
    return dec


def _dec_o2_lambda_current(scale: float) -> Decoder:
    def dec(d: bytes) -> Dict[str, float]:
        return {"lambda": _u16(d, 0) * scale, "current": _u16(d, 2) / 256 - 128}
    return dec


def _dec_lambda(scale: float) -> Decoder:
    return lambda d: _u16(d, 0) * scale


def _dec_maf(scale: float) -> Decoder:
    return lambda d: _u16(d, 0) * scale


def _dec_o2_present_2bank(d: bytes) -> Dict[str, bool]:
    names = ["B1S1", "B1S2", "B1S3", "B1S4", "B2S1", "B2S2", "B2S3", "B2S4"]
    return {n: _bit(d[0], i) for i, n in enumerate(names)}


def _dec_o2_present_4bank(d: bytes) -> Dict[str, bool]:
    names = ["B1S1", "B1S2", "B2S1", "B2S2", "B3S1", "B3S2", "B4S1", "B4S2"]
    return {n: _bit(d[0], i) for i, n in enumerate(names)}


def _dec_fuel_system(d: bytes) -> Dict[str, str]:
    return {"fuel_system_1": decode_fuel_system(d[0]), "fuel_system_2": decode_fuel_system(d[1])}


def _dec_pair_trim(label_a: str, label_b: str) -> Decoder:
    return lambda d: {label_a: _trim(d[0]), label_b: _trim(d[1])}


def _dec_4f(d: bytes) -> Dict[str, int]:
    return {"max_lambda": d[0], "max_o2_voltage": d[1], "max_o2_current": d[2], "max_map": d[3] * 10}


def _dec_50(d: bytes) -> Dict[str, int]:
    return {"max_maf": d[0] * 10}


def _dec_64(d: bytes) -> Dict[str, int]:
    keys = ["idle", "point1", "point2", "point3", "point4"]
    return {k: d[i] - 125 for i, k in enumerate(keys)}


def _dec_65(d: bytes) -> Dict[str, Any]:
    a, b = d[0], d[1]
    out: Dict[str, Any] = {}
    if _bit(a, 0):
        out["pto_active"] = _bit(b, 0)
    if _bit(a, 1):
        out["auto_trans_in_gear"] = _bit(b, 1)
    if _bit(a, 2):
        out["manual_trans_in_gear"] = _bit(b, 2)
    if _bit(a, 3):
        out["glow_plug_lamp_on"] = _bit(b, 3)
    return out


def _supported_u8(labels: Sequence[str], fn: Callable[[int], float]) -> Decoder:
    """A = support bits (bit i -> labels[i]); byte 1+i = value i."""
    def dec(d: bytes) -> Dict[str, float]:
        return {lab: fn(d[1 + i]) for i, lab in enumerate(labels) if _bit(d[0], i) and 1 + i < len(d)}
    return dec


def _supported_u16(labels: Sequence[str], fn: Callable[[int], float], *, signed: bool = False) -> Decoder:
    """A = support bits (bit i -> labels[i]); u16 at 1+2i = value i."""
    def dec(d: bytes) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for i, lab in enumerate(labels):
            off = 1 + 2 * i
            if _bit(d[0], i) and off + 1 < len(d):
                out[lab] = fn(_s16(d, off) if signed else _u16(d, off))
        return out
    return dec


def _supported_u32(labels: Sequence[str], fn: Callable[[int], float]) -> Decoder:
    def dec(d: bytes) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for i, lab in enumerate(labels):
            off = 1 + 4 * i
            if _bit(d[0], i) and off + 3 < len(d):
                out[lab] = fn(_u32(d, off))
        return out
    return dec


def _dec_68(d: bytes) -> Dict[str, float]:
    """PID 68: byte count differs between sources (W: 3 = 2 sensors; DASH: 7 = 6 sensors).

    Decoded by actual length: support bits A0..A5 map to B1S1, B1S2, B1S3, B2S1, B2S2,
    B2S3 (DASH order; W's two sensors are the first two), value ``X - 40`` °C.
    """
    # UNVERIFIED: response length of PID 68 (3 vs 7 bytes); decode whatever arrived.
    warn_unverified("pid68", "PID 68 byte count (3 per W vs 7 per dashlogic) is "
                             "unconfirmed; decoding by the length the ECU returned")
    labels = ["B1S1", "B1S2", "B1S3", "B2S1", "B2S2", "B2S3"]
    return {lab: d[1 + i] - 40 for i, lab in enumerate(labels) if 1 + i < len(d) and _bit(d[0], i)}


def _dec_69(d: bytes) -> Dict[str, float]:
    a = d[0]
    spec = [("commanded_egr_a", 1, lambda x: x / 2.55), ("actual_egr_a", 2, lambda x: x / 2.55),
            ("egr_error_a", 3, lambda x: x / 1.28 - 100), ("commanded_egr_b", 4, lambda x: x / 2.55),
            ("actual_egr_b", 5, lambda x: x / 2.55), ("egr_error_b", 6, lambda x: x / 1.28 - 100)]
    return {k: fn(d[i]) for bit, (k, i, fn) in enumerate(spec) if _bit(a, bit) and i < len(d)}


def _dec_6b(d: bytes) -> Dict[str, float]:
    """EGR temperature: A0..A3 1 °C sensors, A4..A7 the same sensors wide range (4 °C/bit)."""
    labels = ["egr_temp_a_b1s1", "egr_temp_c_b1s2", "egr_temp_b_b2s1", "egr_temp_d_b2s2"]
    out: Dict[str, float] = {}
    for i, lab in enumerate(labels):
        if 1 + i >= len(d):
            break
        if _bit(d[0], i):
            out[lab] = d[1 + i] - 40
        elif _bit(d[0], i + 4):
            out[lab] = d[1 + i] * 4 - 40
    return out


def _dec_6d(d: bytes) -> Dict[str, float]:
    a = d[0]
    out: Dict[str, float] = {}
    if _bit(a, 0): out["commanded_rail_pressure_a"] = _u16(d, 1) * 10
    if _bit(a, 1): out["rail_pressure_a"] = _u16(d, 3) * 10
    if _bit(a, 2): out["fuel_temperature_a"] = d[5] - 40
    if _bit(a, 3): out["commanded_rail_pressure_b"] = _u16(d, 6) * 10
    if _bit(a, 4): out["rail_pressure_b"] = _u16(d, 8) * 10
    if _bit(a, 5): out["fuel_temperature_b"] = d[10] - 40
    return out


def _dec_6f(d: bytes) -> Dict[str, float]:
    a = d[0]
    out: Dict[str, float] = {}
    if _bit(a, 0): out["compressor_inlet_a"] = d[1]
    elif _bit(a, 2): out["compressor_inlet_a"] = d[1] * 8
    if _bit(a, 1): out["compressor_inlet_b"] = d[2]
    elif _bit(a, 3): out["compressor_inlet_b"] = d[2] * 8
    return out


def _dec_70(d: bytes) -> Dict[str, Any]:
    a = d[0]
    out: Dict[str, Any] = {}
    if _bit(a, 0): out["commanded_boost_a"] = _u16(d, 1) / 32
    if _bit(a, 1): out["boost_a"] = _u16(d, 3) / 32
    if _bit(a, 3): out["commanded_boost_b"] = _u16(d, 5) / 32
    if _bit(a, 4): out["boost_b"] = _u16(d, 7) / 32
    if _bit(a, 2): out["control_status_a"] = _CONTROL_STATUS[d[9] & 3]
    if _bit(a, 5): out["control_status_b"] = _CONTROL_STATUS[(d[9] >> 2) & 3]
    return out


def _dec_71(d: bytes) -> Dict[str, Any]:
    a = d[0]
    out: Dict[str, Any] = {}
    if _bit(a, 0): out["commanded_vgt_a"] = d[1] / 2.55
    if _bit(a, 1): out["vgt_position_a"] = d[2] / 2.55
    if _bit(a, 3): out["commanded_vgt_b"] = d[3] / 2.55
    if _bit(a, 4): out["vgt_position_b"] = d[4] / 2.55
    if _bit(a, 2): out["control_status_a"] = _CONTROL_STATUS[d[5] & 3]
    if _bit(a, 5): out["control_status_b"] = _CONTROL_STATUS[(d[5] >> 2) & 3]
    return out


def _dec_75(d: bytes) -> Dict[str, float]:
    a = d[0]
    out: Dict[str, float] = {}
    if _bit(a, 0): out["compressor_inlet"] = d[1] - 40
    if _bit(a, 1): out["compressor_outlet"] = d[2] - 40
    if _bit(a, 2): out["turbine_inlet"] = _u16(d, 3) / 10 - 40
    if _bit(a, 3): out["turbine_outlet"] = _u16(d, 5) / 10 - 40
    return out


def _dec_7a(d: bytes) -> Dict[str, float]:
    a = d[0]
    out: Dict[str, float] = {}
    if _bit(a, 0): out["delta_pressure"] = _s16(d, 1) / 100
    if _bit(a, 1): out["inlet_pressure"] = _u16(d, 3) / 100
    if _bit(a, 2): out["outlet_pressure"] = _u16(d, 5) / 100
    return out


def _dec_nte(d: bytes) -> Dict[str, bool]:
    a = d[0]
    return {"inside_control_area": _bit(a, 0), "outside_control_area": _bit(a, 1),
            "inside_manufacturer_carve_out": _bit(a, 2), "nte_deficiency_active": _bit(a, 3)}


def _dec_aecd(first: int) -> Decoder:
    labels: List[str] = []
    for n in range(first, first + 5):
        labels += [f"aecd{n}_timer1", f"aecd{n}_timer2"]

    def dec(d: bytes) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for i, lab in enumerate(labels):
            off = 1 + 4 * i
            if _bit(d[0], i // 2) and off + 3 < len(d):
                out[lab] = _u32(d, off)
        return out
    return dec


def _dec_85(d: bytes) -> Dict[str, float]:
    a = d[0]
    out: Dict[str, float] = {}
    if _bit(a, 0): out["avg_reagent_consumption"] = _u16(d, 1) / 200
    if _bit(a, 1): out["avg_demanded_consumption"] = _u16(d, 3) / 200
    if _bit(a, 2): out["reagent_tank_level"] = d[5] / 2.55
    if _bit(a, 3): out["warning_mode_time"] = _u32(d, 6)
    return out


def _dec_88(d: bytes) -> Dict[str, Any]:
    a, b, c = d[0], d[1], d[2]

    def flags(n: int) -> Dict[str, bool]:
        return {"nox_too_high": _bit(n, 3), "reagent_consumption_deviation": _bit(n, 2),
                "incorrect_reagent": _bit(n, 1), "reagent_level_low": _bit(n, 0)}

    return {
        "inducement_active": _bit(a, 7), **flags(a),
        "history_10k": flags(b & 0xF), "history_20k": flags(b >> 4),
        "history_30k": flags(c & 0xF), "history_40k": flags(c >> 4),
        "km_active_current_10k": _u16(d, 3), "km_current_block": _u16(d, 5),
        "km_active_20k": _u16(d, 7), "km_active_30k": _u16(d, 9), "km_active_40k": _u16(d, 11),
    }


def _dec_8b(d: bytes) -> Dict[str, Any]:
    a, b = d[0], d[1]
    out: Dict[str, Any] = {}
    if _bit(a, 0): out["dpf_regen_in_progress"] = _bit(b, 0)
    if _bit(a, 1): out["dpf_regen_type"] = "active" if _bit(b, 1) else "passive"
    if _bit(a, 2): out["nox_adsorber_regen_in_progress"] = _bit(b, 2)
    if _bit(a, 3): out["nox_adsorber_desulfurization_in_progress"] = _bit(b, 3)
    if _bit(a, 4): out["normalized_trigger"] = d[2] / 2.55
    if _bit(a, 5): out["avg_time_between_regens"] = _u16(d, 3)
    if _bit(a, 6): out["avg_distance_between_regens"] = _u16(d, 5)
    return out


def _dec_wide_o2(sensors: Sequence[str]) -> Decoder:
    def dec(d: bytes) -> Dict[str, float]:
        a = d[0]
        out: Dict[str, float] = {}
        for i, s in enumerate(sensors):
            if _bit(a, i):
                out[f"concentration_{s}"] = _u16(d, 1 + 2 * i) * 0.001526
            if _bit(a, i + 4):
                out[f"lambda_{s}"] = _u16(d, 9 + 2 * i) * 0.000122
        return out
    return dec


def _dec_8f(d: bytes) -> Dict[str, Any]:
    a = d[0]
    out: Dict[str, Any] = {}
    if _bit(a, 0):
        out["b1s1_active"] = _bit(d[1], 0); out["b1s1_regenerating"] = _bit(d[1], 1)
    if _bit(a, 1): out["b1s1_normalized_output"] = _u16(d, 2) / 100
    if _bit(a, 2):
        out["b2s1_active"] = _bit(d[4], 0); out["b2s1_regenerating"] = _bit(d[4], 1)
    if _bit(a, 3): out["b2s1_normalized_output"] = _u16(d, 5) / 100
    return out


def _dec_90(d: bytes) -> Dict[str, Any]:
    a = d[0]
    return {"all_monitors_complete": not _bit(a, 6),
            "mi_status": _MI_STATUS.get((a >> 2) & 0xF, f"reserved ({(a >> 2) & 0xF})"),
            "display_strategy": _DISPLAY_STRATEGY.get(a & 3, f"reserved ({a & 3})"),
            "continuous_mi_hours": _u16(d, 1)}


def _dec_91(d: bytes) -> Dict[str, Any]:
    return {"ecu_mi_status": _MI_STATUS.get(d[0] & 0xF, f"reserved ({d[0] & 0xF})"),
            "continuous_mi_hours": _u16(d, 1), "highest_b1_counter_hours": _u16(d, 3)}


def _dec_92(d: bytes) -> Dict[str, bool]:
    labels = ["fuel_pressure_control_1", "injection_quantity_1", "injection_timing_1",
              "idle_fuel_balance_1", "fuel_pressure_control_2", "injection_quantity_2",
              "injection_timing_2", "idle_fuel_balance_2"]
    return {f"{lab}_closed_loop": _bit(d[1], i) for i, lab in enumerate(labels) if _bit(d[0], i)}


def _dec_94(d: bytes) -> Dict[str, Any]:
    a, b = d[0], d[1]
    out: Dict[str, Any] = {}
    if _bit(a, 0):
        out["warning_active"] = _bit(b, 0)
        out["level1"] = _INDUCEMENT_LEVEL[(b >> 1) & 3]
        out["level2"] = _INDUCEMENT_LEVEL[(b >> 3) & 3]
        out["level3"] = _INDUCEMENT_LEVEL[(b >> 5) & 3]
    counters = ["reagent_quality_hours", "reagent_consumption_hours", "dosing_activity_hours",
                "egr_valve_hours", "monitoring_system_hours"]
    for i, lab in enumerate(counters):
        if _bit(a, i + 1):
            out[lab] = _u16(d, 2 + 2 * i)
    return out


def _dec_c6(d: bytes) -> Dict[str, int]:
    return {"status": d[0], "removal_block_counter": _u16(d, 1),
            "liquid_reagent_failure_counter": _u16(d, 3), "monitoring_malfunction_counter": _u16(d, 5)}


def _raw(d: bytes) -> str:
    """No verified formula: return the hex bytes."""
    return d.hex(" ").upper()


# ===================================================================== PID table

@dataclass(frozen=True)
class PidDef:
    """One Mode 01/02 parameter.

    ``nbytes`` is the number of data bytes the ECU returns after the echoed PID; it is
    needed to walk multi-PID responses. ``None`` means "take whatever length arrived"
    (the ECU's ISO-TP length is the truth) and such a PID is always requested alone.
    ``units`` optionally maps keys of a dict result to their unit.
    """
    pid: int
    name: str
    nbytes: Optional[int]
    unit: str
    decoder: Decoder
    min: Optional[float] = None
    max: Optional[float] = None
    notes: str = ""
    units: Mapping[str, str] = field(default_factory=dict)
    unverified: bool = False

    def decode(self, data: bytes) -> Any:
        if self.nbytes is not None and len(data) < self.nbytes:
            raise ValueError(f"PID {self.pid:02X} ({self.name}) needs {self.nbytes} bytes, got {len(data)}")
        return self.decoder(data)


def _o2_name(i: int) -> str:
    bank, sensor = ("1", i + 1) if i < 4 else ("2", i - 3)
    return f"B{bank}S{sensor}"


def _build_table() -> Dict[int, PidDef]:
    rows: List[PidDef] = []
    P = rows.append

    for base in SUPPORT_BASES[:-1]:
        P(PidDef(base, f"PIDs supported {base + 1:02X}-{base + 0x20:02X}", 4, "",
                 (lambda b: (lambda d: parse_supported(b, d)))(base), notes="bitmap"))
    P(PidDef(0x01, "Monitor status since DTCs cleared", 4, "", decode_monitor_status))
    P(PidDef(0x02, "DTC that caused freeze frame", 2, "",
             lambda d: None if d[0] == 0 and d[1] == 0 else decode_dtc(d[0], d[1]),
             notes="Mode 02 only; 0000 = no freeze frame"))
    P(PidDef(0x03, "Fuel system status", 2, "", _dec_fuel_system))
    P(PidDef(0x04, "Calculated engine load", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x05, "Engine coolant temperature", 1, "°C", lambda d: d[0] - 40, -40, 215))
    P(PidDef(0x06, "Short term fuel trim bank 1", 1, "%", lambda d: _trim(d[0]), -100, 99.2))
    P(PidDef(0x07, "Long term fuel trim bank 1", 1, "%", lambda d: _trim(d[0]), -100, 99.2))
    P(PidDef(0x08, "Short term fuel trim bank 2", 1, "%", lambda d: _trim(d[0]), -100, 99.2))
    P(PidDef(0x09, "Long term fuel trim bank 2", 1, "%", lambda d: _trim(d[0]), -100, 99.2))
    P(PidDef(0x0A, "Fuel pressure (gauge)", 1, "kPa", lambda d: 3 * d[0], 0, 765))
    P(PidDef(0x0B, "Intake manifold absolute pressure", 1, "kPa", lambda d: d[0], 0, 255))
    P(PidDef(0x0C, "Engine speed", 2, "rpm", lambda d: _u16(d) / 4, 0, 16383.75))
    P(PidDef(0x0D, "Vehicle speed", 1, "km/h", lambda d: d[0], 0, 255))
    P(PidDef(0x0E, "Timing advance", 1, "° BTDC", lambda d: d[0] / 2 - 64, -64, 63.5))
    P(PidDef(0x0F, "Intake air temperature", 1, "°C", lambda d: d[0] - 40, -40, 215))
    P(PidDef(0x10, "MAF air flow rate", 2, "g/s", _dec_maf(DEFAULT_SCALING.maf_scale), 0, 655.35,
             notes="scale overridden by PID 50 Data A when non-zero"))
    P(PidDef(0x11, "Throttle position", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x12, "Commanded secondary air status", 1, "",
             lambda d: decode_one_hot(SECONDARY_AIR_STATUS, d[0])))
    P(PidDef(0x13, "O2 sensors present (2 banks)", 1, "", _dec_o2_present_2bank,
             notes="exclusive with PID 1D"))
    for i in range(8):
        P(PidDef(0x14 + i, f"O2 sensor {i + 1} ({_o2_name(i)}) voltage / STFT", 2, "", _dec_o2_narrow,
                 units={"voltage": "V", "stft": "%"}))
    P(PidDef(0x1C, "OBD standard this vehicle conforms to", 1, "", lambda d: decode_obd_standard(d[0]), 1, 250,
             notes="values 14-16 differ between ISO 15031-5:2006 and J1979-DA"))
    P(PidDef(0x1D, "O2 sensors present (4 banks)", 1, "", _dec_o2_present_4bank))
    P(PidDef(0x1E, "Auxiliary input status", 1, "", lambda d: {"pto_active": _bit(d[0], 0)}))
    P(PidDef(0x1F, "Run time since engine start", 2, "s", lambda d: _u16(d), 0, 65535))
    P(PidDef(0x21, "Distance traveled with MIL on", 2, "km", lambda d: _u16(d), 0, 65535))
    P(PidDef(0x22, "Fuel rail pressure (relative to manifold vacuum)", 2, "kPa", lambda d: _u16(d) * 0.079, 0, 5177.265))
    P(PidDef(0x23, "Fuel rail gauge pressure (diesel / GDI)", 2, "kPa", lambda d: _u16(d) * 10, 0, 655350))
    for i in range(8):
        P(PidDef(0x24 + i, f"O2 sensor {i + 1} ({_o2_name(i)}) lambda / voltage", 4, "",
                 _dec_o2_lambda_voltage(DEFAULT_SCALING.lambda_scale),
                 units={"lambda": "λ", "voltage": "V"}, notes="lambda scale overridden by PID 4F Data A"))
    P(PidDef(0x2C, "Commanded EGR", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x2D, "EGR error", 1, "%", lambda d: _trim(d[0]), -100, 99.2))
    P(PidDef(0x2E, "Commanded evaporative purge", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x2F, "Fuel tank level input", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x30, "Warm-ups since codes cleared", 1, "count", lambda d: d[0], 0, 255))
    P(PidDef(0x31, "Distance traveled since codes cleared", 2, "km", lambda d: _u16(d), 0, 65535))
    P(PidDef(0x32, "Evap system vapor pressure", 2, "Pa", lambda d: _s16(d) / 4, -8192, 8191.75))
    P(PidDef(0x33, "Absolute barometric pressure", 1, "kPa", lambda d: d[0], 0, 255))
    for i in range(8):
        P(PidDef(0x34 + i, f"O2 sensor {i + 1} ({_o2_name(i)}) lambda / current", 4, "",
                 _dec_o2_lambda_current(DEFAULT_SCALING.lambda_scale),
                 units={"lambda": "λ", "current": "mA"}, notes="lambda scale overridden by PID 4F Data A"))
    for pid, name in ((0x3C, "B1S1"), (0x3D, "B2S1"), (0x3E, "B1S2"), (0x3F, "B2S2")):
        P(PidDef(pid, f"Catalyst temperature {name}", 2, "°C", lambda d: _u16(d) / 10 - 40, -40, 6513.5))
    P(PidDef(0x41, "Monitor status this drive cycle", 4, "",
             lambda d: decode_monitor_status(d, this_cycle=True)))
    P(PidDef(0x42, "Control module voltage", 2, "V", lambda d: _u16(d) / 1000, 0, 65.535))
    P(PidDef(0x43, "Absolute load value", 2, "%", lambda d: _u16(d) * 100 / 255, 0, 25700))
    P(PidDef(0x44, "Commanded equivalence ratio (lambda)", 2, "λ", _dec_lambda(DEFAULT_SCALING.lambda_scale), 0, 2,
             notes="scale overridden by PID 4F Data A"))
    P(PidDef(0x45, "Relative throttle position", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x46, "Ambient air temperature", 1, "°C", lambda d: d[0] - 40, -40, 215))
    P(PidDef(0x47, "Absolute throttle position B", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x48, "Absolute throttle position C", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x49, "Accelerator pedal position D", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x4A, "Accelerator pedal position E", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x4B, "Accelerator pedal position F", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x4C, "Commanded throttle actuator", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x4D, "Time run with MIL on", 2, "min", lambda d: _u16(d), 0, 65535))
    P(PidDef(0x4E, "Time since trouble codes cleared", 2, "min", lambda d: _u16(d), 0, 65535))
    P(PidDef(0x4F, "Max values: lambda, O2 V, O2 mA, MAP (scaling info #1)", 4, "", _dec_4f,
             units={"max_lambda": "λ", "max_o2_voltage": "V", "max_o2_current": "mA", "max_map": "kPa"},
             notes="not for display; Data A rescales lambda PIDs"))
    P(PidDef(0x50, "Max MAF (scaling info #2)", 4, "", _dec_50, units={"max_maf": "g/s"},
             notes="not for display; Data A rescales PID 10"))
    P(PidDef(0x51, "Fuel type", 1, "", lambda d: FUEL_TYPES.get(d[0], f"reserved ({d[0]})")))
    P(PidDef(0x52, "Ethanol fuel", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x53, "Absolute evap system vapor pressure", 2, "kPa", lambda d: _u16(d) / 200, 0, 327.675))
    P(PidDef(0x54, "Evap system vapor pressure", 2, "Pa", lambda d: _s16(d), -32768, 32767,
             notes="exclusive with PID 32"))
    P(PidDef(0x55, "Short term secondary O2 trim banks 1/3", 2, "%", _dec_pair_trim("bank1", "bank3"), -100, 99.2))
    P(PidDef(0x56, "Long term secondary O2 trim banks 1/3", 2, "%", _dec_pair_trim("bank1", "bank3"), -100, 99.2))
    P(PidDef(0x57, "Short term secondary O2 trim banks 2/4", 2, "%", _dec_pair_trim("bank2", "bank4"), -100, 99.2))
    P(PidDef(0x58, "Long term secondary O2 trim banks 2/4", 2, "%", _dec_pair_trim("bank2", "bank4"), -100, 99.2))
    P(PidDef(0x59, "Fuel rail absolute pressure", 2, "kPa", lambda d: _u16(d) * 10, 0, 655350))
    P(PidDef(0x5A, "Relative accelerator pedal position", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x5B, "Hybrid battery pack remaining life", 1, "%", lambda d: _pct255(d[0]), 0, 100))
    P(PidDef(0x5C, "Engine oil temperature", 1, "°C", lambda d: d[0] - 40, -40, 210))
    P(PidDef(0x5D, "Fuel injection timing", 2, "°", lambda d: _u16(d) / 128 - 210, -210, 301.992))
    P(PidDef(0x5E, "Engine fuel rate", 2, "L/h", lambda d: _u16(d) / 20, 0, 3212.75))
    P(PidDef(0x5F, "Emission requirements vehicle is designed to", 1, "",
             lambda d: EMISSION_REQUIREMENTS.get(d[0], f"reserved (0x{d[0]:02X})")))
    P(PidDef(0x61, "Driver's demand engine percent torque", 1, "%", lambda d: d[0] - 125, -125, 130))
    P(PidDef(0x62, "Actual engine percent torque", 1, "%", lambda d: d[0] - 125, -125, 130))
    P(PidDef(0x63, "Engine reference torque", 2, "N·m", lambda d: _u16(d), 0, 65535))
    P(PidDef(0x64, "Engine percent torque data", 5, "%", _dec_64, -125, 130))
    P(PidDef(0x65, "Auxiliary input/output status", 2, "", _dec_65))
    P(PidDef(0x66, "Mass air flow sensor A/B", 5, "g/s",
             _supported_u16(["sensor_a", "sensor_b"], lambda v: v / 32), 0, 2047.96875))
    P(PidDef(0x67, "Engine coolant temperature sensors 1/2", 3, "°C",
             _supported_u8(["sensor_1", "sensor_2"], lambda v: v - 40), -40, 215))
    # UNVERIFIED: byte count 3 (W) vs 7 (DASH); decoded by actual length, requested alone.
    P(PidDef(0x68, "Intake air temperature sensors", None, "°C", _dec_68, -40, 215,
             notes="length unconfirmed (3 or 7 bytes); decoded by actual length", unverified=True))
    P(PidDef(0x69, "Commanded EGR and EGR error", 7, "%", _dec_69))
    P(PidDef(0x6A, "Commanded diesel intake air flow control / relative position", 5, "%",
             _supported_u8(["commanded_a", "relative_a", "commanded_b", "relative_b"], lambda v: v / 2.55)))
    P(PidDef(0x6B, "EGR temperature", 5, "°C", _dec_6b))
    P(PidDef(0x6C, "Commanded throttle actuator control / relative throttle position", 5, "%",
             _supported_u8(["commanded_a", "relative_a", "commanded_b", "relative_b"], lambda v: v / 2.55)))
    P(PidDef(0x6D, "Fuel pressure control system", 11, "", _dec_6d,
             units={"commanded_rail_pressure_a": "kPa", "rail_pressure_a": "kPa", "fuel_temperature_a": "°C",
                    "commanded_rail_pressure_b": "kPa", "rail_pressure_b": "kPa", "fuel_temperature_b": "°C"}))
    P(PidDef(0x6E, "Injection pressure control system", 9, "kPa",
             _supported_u16(["commanded_icp_a", "icp_a", "commanded_icp_b", "icp_b"], lambda v: v * 10)))
    P(PidDef(0x6F, "Turbocharger compressor inlet pressure", 3, "kPa", _dec_6f))
    P(PidDef(0x70, "Boost pressure control", 10, "kPa", _dec_70, 0, 2047.97))
    P(PidDef(0x71, "Variable geometry turbo control", 6, "%", _dec_71))
    P(PidDef(0x72, "Wastegate control", 5, "%",
             _supported_u8(["commanded_a", "position_a", "commanded_b", "position_b"], lambda v: v / 2.55)))
    P(PidDef(0x73, "Exhaust pressure", 5, "kPa", _supported_u16(["bank1", "bank2"], lambda v: v / 100)))
    P(PidDef(0x74, "Turbocharger RPM", 5, "rpm", _supported_u16(["turbo_a", "turbo_b"], lambda v: v * 10)))
    P(PidDef(0x75, "Turbocharger A temperature", 7, "°C", _dec_75))
    P(PidDef(0x76, "Turbocharger B temperature", 7, "°C", _dec_75))
    P(PidDef(0x77, "Charge air cooler temperature", 5, "°C",
             _supported_u8(["B1S1", "B1S2", "B2S1", "B2S2"], lambda v: v - 40)))
    P(PidDef(0x78, "Exhaust gas temperature bank 1", 9, "°C",
             _supported_u16(["S1", "S2", "S3", "S4"], lambda v: v / 10 - 40), -40, 6513.5))
    P(PidDef(0x79, "Exhaust gas temperature bank 2", 9, "°C",
             _supported_u16(["S1", "S2", "S3", "S4"], lambda v: v / 10 - 40), -40, 6513.5))
    P(PidDef(0x7A, "Diesel particulate filter bank 1", 7, "kPa", _dec_7a))
    P(PidDef(0x7B, "Diesel particulate filter bank 2", 7, "kPa", _dec_7a))
    P(PidDef(0x7C, "Diesel particulate filter temperature", 9, "°C",
             _supported_u16(["b1_inlet", "b1_outlet", "b2_inlet", "b2_outlet"], lambda v: v / 10 - 40)))
    P(PidDef(0x7D, "NOx NTE control area status", 1, "", _dec_nte))
    P(PidDef(0x7E, "PM NTE control area status", 1, "", _dec_nte))
    P(PidDef(0x7F, "Engine run time", 13, "s",
             _supported_u32(["total", "idle", "with_pto"], lambda v: v),
             notes="idle/PTO assignment follows the support-bit order (DASH captions all three 'total')"))
    P(PidDef(0x81, "Run time for EI-AECD #1-#5", 41, "s", _dec_aecd(1)))
    P(PidDef(0x82, "Run time for EI-AECD #6-#10", 41, "s", _dec_aecd(6)))
    P(PidDef(0x83, "NOx sensor", 9, "ppm", _supported_u16(["B1S1", "B1S2", "B2S1", "B2S2"], lambda v: v)))
    P(PidDef(0x84, "Manifold surface temperature", 1, "°C", lambda d: d[0] - 40))
    P(PidDef(0x85, "NOx reagent system", 10, "", _dec_85,
             units={"avg_reagent_consumption": "L/h", "avg_demanded_consumption": "L/h",
                    "reagent_tank_level": "%", "warning_mode_time": "s"}))
    P(PidDef(0x86, "Particulate matter sensor", 5, "mg/m³", _supported_u16(["B1S1", "B2S1"], lambda v: v / 80)))
    P(PidDef(0x87, "Intake manifold absolute pressure A/B", 5, "kPa",
             _supported_u16(["sensor_a", "sensor_b"], lambda v: v / 32)))
    P(PidDef(0x88, "SCR inducement system", 13, "km", _dec_88,
             notes="u16 km fields per pair (DASH prints the B/C pair for every field, a copy error)"))
    P(PidDef(0x89, "Run time for EI-AECD #11-#15", 41, "s", _dec_aecd(11)))
    P(PidDef(0x8A, "Run time for EI-AECD #16-#20", 41, "s", _dec_aecd(16)))
    P(PidDef(0x8B, "Diesel aftertreatment status", 7, "", _dec_8b,
             units={"normalized_trigger": "%", "avg_time_between_regens": "min",
                    "avg_distance_between_regens": "km"}))
    P(PidDef(0x8C, "O2 sensor (wide range) sensors 1/2", 17, "",
             _dec_wide_o2(["B1S1", "B1S2", "B2S1", "B2S2"]), notes="concentration % and lambda per sensor"))
    P(PidDef(0x8D, "Throttle position G", 1, "%", lambda d: d[0] / 2.55, 0, 100))
    P(PidDef(0x8E, "Engine friction percent torque", 1, "%", lambda d: d[0] - 125, -125, 130))
    P(PidDef(0x8F, "PM sensor bank 1 & 2", 7, "", _dec_8f,
             units={"b1s1_normalized_output": "%", "b2s1_normalized_output": "%"}))
    P(PidDef(0x90, "WWH-OBD vehicle OBD system information", 3, "", _dec_90,
             units={"continuous_mi_hours": "h"}))
    P(PidDef(0x91, "WWH-OBD ECU OBD system information", 5, "h", _dec_91))
    P(PidDef(0x92, "Fuel system control status (compression ignition)", 2, "", _dec_92))
    P(PidDef(0x93, "WWH-OBD vehicle OBD counters", 3, "h",
             _supported_u16(["cumulative_continuous_mi_hours"], lambda v: v)))
    P(PidDef(0x94, "NOx control driver inducement status/counters", 12, "h", _dec_94))
    P(PidDef(0x98, "Exhaust gas temperature bank 1 sensors 5-8", 9, "°C",
             _supported_u16(["S5", "S6", "S7", "S8"], lambda v: v / 10 - 40)))
    P(PidDef(0x99, "Exhaust gas temperature bank 2 sensors 5-8", 9, "°C",
             _supported_u16(["S5", "S6", "S7", "S8"], lambda v: v / 10 - 40)))
    P(PidDef(0x9A, "Hybrid/EV system data, battery, voltage", 6, "", _raw, notes="layout not published"))
    P(PidDef(0x9B, "Diesel exhaust fluid sensor data", 4, "%", lambda d: _pct255(d[3]), 0, 100,
             notes="only Data D (level %) is published"))
    P(PidDef(0x9C, "O2 sensor (wide range) sensors 3/4", 17, "",
             _dec_wide_o2(["B1S3", "B1S4", "B2S3", "B2S4"])))
    P(PidDef(0x9D, "Engine fuel rate", 4, "g/s", _raw, notes="formula not published; raw"))
    P(PidDef(0x9E, "Engine exhaust flow rate", 2, "kg/h", _raw, notes="formula not published; raw"))
    P(PidDef(0x9F, "Fuel system percentage use", 9, "", _raw, notes="layout not published"))
    P(PidDef(0xA1, "NOx sensor corrected data", 9, "ppm", _raw, notes="layout not published"))
    P(PidDef(0xA2, "Cylinder fuel rate", 2, "mg/stroke", lambda d: _u16(d) / 32, 0, 2047.97))
    P(PidDef(0xA3, "Evap system vapor pressure", 9, "Pa", _raw, notes="layout not published"))
    P(PidDef(0xA4, "Transmission actual gear", 4, "ratio",
             lambda d: {"gear_ratio": _u16(d, 2) / 1000} if _bit(d[0], 1) else {}, 0, 65.535))
    P(PidDef(0xA5, "Commanded diesel exhaust fluid dosing", 4, "%",
             lambda d: {"dosing": d[1] / 2} if _bit(d[0], 0) else {}, 0, 127.5))
    P(PidDef(0xA6, "Odometer", 4, "km", lambda d: _u32(d) / 10, 0, 429496729.5))
    P(PidDef(0xA7, "NOx sensor concentration sensors 3 and 4", 4, "", _raw, notes="layout not published"))
    P(PidDef(0xA8, "NOx sensor corrected concentration sensors 3 and 4", 4, "", _raw,
             notes="layout not published"))
    P(PidDef(0xA9, "ABS disable switch state", 4, "",
             lambda d: {"abs_disabled": _bit(d[1], 0)} if _bit(d[0], 0) else {}))
    P(PidDef(0xC3, "Fuel level input A/B", 2, "", _raw, notes="W marks its own row unreliable; raw"))
    P(PidDef(0xC4, "Exhaust particulate control system diagnostic time/count", 8, "", _raw,
             notes="W marks its own row unreliable; raw"))
    P(PidDef(0xC5, "Fuel pressure A and B", 4, "kPa", _raw, notes="no formula published; raw"))
    P(PidDef(0xC6, "Particulate control inducement", 7, "h", _dec_c6))
    P(PidDef(0xC7, "Distance since reflash or module replacement", 2, "km", _raw,
             notes="no formula published (presumably u16); raw"))
    P(PidDef(0xC8, "NCD and PCD warning lamp status", 1, "", _raw, notes="bit field not published; raw"))

    table: Dict[int, PidDef] = {}
    for row in rows:
        if row.pid in table:
            raise RuntimeError(f"duplicate PID 0x{row.pid:02X} in table")
        table[row.pid] = row
    return table


PIDS: Dict[int, PidDef] = _build_table()


def pid_def(pid: int) -> Optional[PidDef]:
    return PIDS.get(pid)


def pid_name(pid: int) -> str:
    d = PIDS.get(pid)
    return d.name if d else f"PID {pid:02X} (unknown)"


def pid_length(pid: int) -> Optional[int]:
    """Data byte count after the echoed PID, or ``None`` when unknown/variable."""
    d = PIDS.get(pid)
    return d.nbytes if d else None


def decode_pid(pid: int, data: bytes, scaling: ScalingOverrides = DEFAULT_SCALING) -> Any:
    """Decode ``data`` (bytes after the echoed PID) honouring the PID 4F/50 overrides."""
    d = PIDS.get(pid)
    if d is None:
        return _raw(data)
    if pid == 0x10 and scaling.pid50_a:
        return _dec_maf(scaling.maf_scale)(data)
    if pid in LAMBDA_PIDS and scaling.pid4f_a:
        if pid == 0x44:
            return _dec_lambda(scaling.lambda_scale)(data)
        if pid < 0x30:
            return _dec_o2_lambda_voltage(scaling.lambda_scale)(data)
        return _dec_o2_lambda_current(scaling.lambda_scale)(data)
    return d.decode(data)


def walk_records(payload: bytes, *, with_frame: bool = False) -> List[Tuple[int, Optional[int], bytes]]:
    """Split a multi-PID Mode 01 (``with_frame=False``) / Mode 02 (``True``) response body.

    ``payload`` is everything after the positive SID. Each record is ``[PID][frame#]
    [data...]`` and the data length comes from :data:`PIDS`; the walk stops (with a
    warning) at the first PID whose length is unknown, returning what was parsed plus
    that PID with the remainder of the payload as its data.

    The table is only a hypothesis about the ECU's byte counts: the caller must check
    that the records consume the payload exactly (``sum(hdr + len(data))``) and that
    the last record is not short, otherwise the reply is misaligned
    (``ObdClient._split_records`` does this and falls back to single-PID reads, where
    the ISO-TP payload length is the truth).
    """
    out: List[Tuple[int, Optional[int], bytes]] = []
    i = 0
    hdr = 2 if with_frame else 1
    while i + hdr <= len(payload):
        pid = payload[i]
        frame = payload[i + 1] if with_frame else None
        n = pid_length(pid)
        if n is None:
            rest = payload[i + hdr:]
            if i + hdr < len(payload) and len(payload) - (i + hdr) > 0:
                log.warning("PID %02X has no fixed length; taking the remaining %d byte(s) as its data",
                            pid, len(rest))
            out.append((pid, frame, bytes(rest)))
            break
        out.append((pid, frame, bytes(payload[i + hdr:i + hdr + n])))
        i += hdr + n
    return out


# ================================================================= Mode 06 tables

@dataclass(frozen=True)
class Uas:
    """One Unit and Scaling ID row: ``value = raw * scale + offset``.

    ``uasid`` is the row's own id; :attr:`signed` follows Annex E ($01-$7F unsigned,
    $80-$FE two's complement) and equals :func:`uas_signed`.
    """
    uasid: int
    scale: float
    offset: float
    unit: str
    note: str = ""

    @property
    def signed(self) -> bool:
        return uas_signed(self.uasid)


def _uas_rows() -> Dict[int, Uas]:
    r: Dict[int, Uas] = {}
    U = lambda i, s, u, o=0.0, n="": r.__setitem__(i, Uas(i, s, o, u, n))   # noqa: E731
    U(0x01, 1, "raw"); U(0x02, 0.1, "raw"); U(0x03, 0.01, "raw"); U(0x04, 0.001, "raw")
    U(0x05, 0.0000305, "raw"); U(0x06, 0.000305, "raw"); U(0x07, 0.25, "rpm"); U(0x08, 0.01, "km/h")
    U(0x09, 1, "km/h"); U(0x0A, 0.000122, "V"); U(0x0B, 0.001, "V"); U(0x0C, 0.01, "V")
    U(0x0D, 0.00390625, "mA"); U(0x0E, 0.001, "A"); U(0x0F, 0.01, "A"); U(0x10, 1, "ms")
    U(0x11, 0.1, "s"); U(0x12, 1, "s"); U(0x13, 1, "mΩ"); U(0x14, 1, "Ω"); U(0x15, 1, "kΩ")
    U(0x16, 0.1, "°C", -40.0); U(0x17, 0.01, "kPa"); U(0x18, 0.0117, "kPa"); U(0x19, 0.079, "kPa")
    U(0x1A, 1, "kPa"); U(0x1B, 10, "kPa"); U(0x1C, 0.01, "°"); U(0x1D, 0.5, "°"); U(0x1E, 0.0000305, "λ")
    U(0x1F, 0.05, "A/F"); U(0x20, 0.0039062, "ratio"); U(0x21, 0.001, "Hz"); U(0x22, 1, "Hz")
    U(0x23, 1, "kHz"); U(0x24, 1, "counts"); U(0x25, 1, "km"); U(0x26, 0.0001, "V/ms")
    U(0x27, 0.01, "g/s"); U(0x28, 1, "g/s"); U(0x29, 0.25, "Pa/s"); U(0x2A, 0.001, "kg/h")
    U(0x2B, 1, "switches"); U(0x2C, 0.01, "g/cyl"); U(0x2D, 0.01, "mg/stroke")
    U(0x2E, 1, "bool", 0.0, "state encoded (ISO5:2006 Table 170 labels it 'Percent'; treated as boolean)")
    U(0x2F, 0.01, "%"); U(0x30, 0.001526, "%"); U(0x31, 0.001, "L"); U(0x32, 0.0000305, "inch")
    U(0x33, 0.00024414, "λ"); U(0x34, 1, "min"); U(0x35, 0.01, "s"); U(0x36, 0.01, "g"); U(0x37, 0.1, "g")
    U(0x38, 1, "g"); U(0x39, 0.01, "%", -327.68)
    # Not in ISO 15031-5:2006 Annex E; python-OBD UAS_IDS, several confirmed by GM Mode 06 docs.
    U(0x3A, 0.001, "g", 0.0, "python-OBD/J1979-DA"); U(0x3B, 0.0001, "g", 0.0, "python-OBD/J1979-DA")
    U(0x3C, 0.1, "µs", 0.0, "python-OBD, GM"); U(0x3D, 0.01, "mA", 0.0, "python-OBD/J1979-DA")
    U(0x3E, 0.00006103516, "mm²", 0.0, "python-OBD/J1979-DA"); U(0x3F, 0.01, "L", 0.0, "python-OBD only")
    U(0x40, 1, "ppm", 0.0, "python-OBD/J1979-DA"); U(0x41, 0.01, "µA", 0.0, "python-OBD, GM")
    # Signed (two's complement) ids.
    U(0x81, 1, "raw"); U(0x82, 0.1, "raw"); U(0x83, 0.01, "raw"); U(0x84, 0.001, "raw")
    U(0x85, 0.0000305, "raw"); U(0x86, 0.000305, "raw"); U(0x87, 1, "ppm", 0.0, "python-OBD/J1979-DA")
    U(0x8A, 0.000122, "V"); U(0x8B, 0.001, "V"); U(0x8C, 0.01, "V"); U(0x8D, 0.00390625, "mA")
    U(0x8E, 0.001, "A"); U(0x8F, 1, "µs", 0.0, "GM Mode 06 docs"); U(0x90, 1, "ms"); U(0x96, 0.1, "°C")
    U(0x99, 0.1, "kPa", 0.0, "python-OBD/J1979-DA"); U(0x9C, 0.01, "°"); U(0x9D, 0.5, "°")
    U(0xA8, 1, "g/s"); U(0xA9, 0.25, "Pa/s"); U(0xAD, 0.01, "mg/stroke", 0.0, "python-OBD/J1979-DA")
    U(0xAE, 0.1, "mg/stroke", 0.0, "python-OBD/J1979-DA"); U(0xAF, 0.01, "%"); U(0xB0, 0.003052, "%")
    U(0xB1, 2, "mV/s"); U(0xFB, 10, "kPa", 0.0, "GM Mode 06 docs"); U(0xFC, 0.01, "kPa", 0.0, "python-OBD, GM")
    U(0xFD, 0.001, "kPa"); U(0xFE, 0.25, "Pa")
    return r


UASIDS: Dict[int, Uas] = _uas_rows()


def uas_signed(uasid: int) -> bool:
    """$01-$7F unsigned, $80-$FE signed two's complement (Annex E)."""
    return bool(uasid & 0x80)


def uas_raw(uasid: int, raw16: int) -> int:
    """Sign-extend ``raw16`` for signed UASIDs so comparisons use the real value."""
    if uas_signed(uasid) and raw16 > 0x7FFF:
        return raw16 - 0x10000
    return raw16


def uas_apply(uasid: int, raw16: int) -> Tuple[Any, str, bool]:
    """``(value, unit, known)``; unknown ids return the (sign-extended) raw value."""
    raw = uas_raw(uasid, raw16)
    u = UASIDS.get(uasid)
    if u is None:
        return raw, f"raw (UASID 0x{uasid:02X})", False
    if uasid == 0x2E:
        return bool(raw), u.unit, True
    return raw * u.scale + u.offset, u.unit, True


def _obdmid_names() -> Dict[int, str]:
    n: Dict[int, str] = {}
    o2 = [f"B{b}S{s}" for b in range(1, 5) for s in range(1, 5)]
    for base in SUPPORT_BASES:
        n[base] = f"OBDMIDs supported {base + 1:02X}-{base + 0x20:02X}"
    for i, s in enumerate(o2):
        n[0x01 + i] = f"Oxygen sensor monitor {s}"
        n[0x41 + i] = f"Oxygen sensor heater monitor {s}"
    for b in range(1, 5):
        n[0x20 + b] = f"Catalyst monitor bank {b}"
        n[0x30 + b] = f"EGR monitor bank {b}"
        n[0x34 + b] = f"VVT monitor bank {b}"          # reserved in ISO5:2006; later J1979 / python-OBD
        n[0x60 + b] = f"Heated catalyst monitor bank {b}"
        n[0x70 + b] = f"Secondary air monitor {b}"
        n[0x80 + b] = f"Fuel system monitor bank {b}"
    n.update({0x39: "EVAP monitor (cap off / 0.150\")", 0x3A: "EVAP monitor (0.090\")",
              0x3B: "EVAP monitor (0.040\")", 0x3C: "EVAP monitor (0.020\")", 0x3D: "Purge flow monitor",
              0x85: "Boost pressure control monitor bank 1", 0x86: "Boost pressure control monitor bank 2",
              0x90: "NOx adsorber monitor bank 1", 0x91: "NOx adsorber monitor bank 2",
              0x98: "NOx catalyst monitor bank 1", 0x99: "NOx catalyst monitor bank 2",
              0xA1: "Misfire monitor general data",
              0xB0: "PM filter monitor bank 1", 0xB1: "PM filter monitor bank 2"})
    for c in range(1, 13):
        n[0xA1 + c] = f"Misfire cylinder {c} data"
    return n


OBDMID_NAMES: Dict[int, str] = _obdmid_names()

TID_NAMES: Dict[int, str] = {
    0x01: "Rich-to-lean sensor threshold voltage", 0x02: "Lean-to-rich sensor threshold voltage",
    0x03: "Low sensor voltage for switch time calculation", 0x04: "High sensor voltage for switch time calculation",
    0x05: "Rich-to-lean sensor switch time", 0x06: "Lean-to-rich sensor switch time",
    0x07: "Minimum sensor voltage for test cycle", 0x08: "Maximum sensor voltage for test cycle",
    0x09: "Time between sensor transitions", 0x0A: "Sensor period",
    0x0B: "EWMA misfire counts for last ten driving cycles", 0x0C: "Misfire counts for last/current driving cycles",
}


def obdmid_name(mid: int) -> str:
    if mid in OBDMID_NAMES:
        return OBDMID_NAMES[mid]
    if 0xE1 <= mid <= 0xFF:
        return f"Manufacturer defined OBDMID {mid:02X}"
    return f"OBDMID {mid:02X} (reserved)"


def tid_name(tid: int) -> str:
    if tid in TID_NAMES:
        return TID_NAMES[tid]
    if 0x80 <= tid <= 0xFE:
        return f"Manufacturer defined TID {tid:02X}"
    return f"TID {tid:02X} (reserved)"


# ================================================================ Mode 09 tables

INFOTYPE_NAMES: Dict[int, str] = {
    0x00: "InfoTypes supported 01-20", 0x01: "VIN message count (K-line only)", 0x02: "VIN",
    0x03: "CALID message count (K-line only)", 0x04: "Calibration ID(s)",
    0x05: "CVN message count (K-line only)", 0x06: "Calibration verification number(s)",
    0x07: "IPT message count (K-line only)", 0x08: "In-use performance tracking (spark ignition)",
    0x09: "ECU name message count (K-line only)", 0x0A: "ECU name",
    0x0B: "In-use performance tracking (compression ignition)",
    0x0C: "Engine serial number (ESN)",            # UNVERIFIED: name only (J1979-DA, not fetched)
    0x0D: "Exhaust regulation / type approval number (EROTAN)",   # UNVERIFIED: name only
    0x20: "InfoTypes supported 21-40",
}
#: InfoTypes whose *names* are Reported only (J1979-DA not fetched; byte layouts unknown).
UNVERIFIED_INFOTYPES = frozenset({0x0C, 0x0D})


def infotype_name(infotype: int) -> str:
    """Display name of a Mode 09 InfoType.

    0x0C (ESN) and 0x0D (EROTAN) are named from secondary sources only (the J1979-DA
    text was not fetched); their first use logs an ``UNVERIFIED mapping`` warning and
    their payload is never decoded beyond raw hex. Unknown ids get ``InfoType xx``.
    """
    if infotype in UNVERIFIED_INFOTYPES:
        # UNVERIFIED: names from the W/J1979-DA summary; layouts unknown.
        warn_unverified("infotype-0c-0d", "InfoType 0C = 'Engine serial number (ESN)' and 0D = 'EROTAN' "
                                          "are names from J1979-DA summaries, not a fetched standard; "
                                          "payloads are shown raw")
    return INFOTYPE_NAMES.get(infotype, f"InfoType {infotype:02X}")

IPT_SPARK_NAMES: Tuple[str, ...] = (
    "OBDCOND", "IGNCYCCNTR", "CATCOMP1", "CATCOND1", "CATCOMP2", "CATCOND2", "O2SCOMP1", "O2SCOND1",
    "O2SCOMP2", "O2SCOND2", "EGRCOMP", "EGRCOND", "AIRCOMP", "AIRCOND", "EVAPCOMP", "EVAPCOND",
)
# UNVERIFIED: items 17-20 of the 20-item variant (W list; "4 or 5 messages").
IPT_SPARK_EXTRA_NAMES: Tuple[str, ...] = ("SO2SCOMP1", "SO2SCOND1", "SO2SCOMP2", "SO2SCOND2")
IPT_COMPRESSION_NAMES: Tuple[str, ...] = (
    "OBDCOND", "IGNCNTR", "HCCATCOMP", "HCCATCOND", "NCATCOMP", "NCATCOND", "NADSCOMP", "NADSCOND",
    "PMCOMP", "PMCOND", "EGSCOMP", "EGSCOND", "EGRCOMP", "EGRCOND", "BPCOMP", "BPCOND",
    "FUELCOMP", "FUELCOND",
)

ECU_ACRONYMS: Dict[str, str] = {
    "ABS": "Antilock brake system", "AFCM": "Alternative fuel control module",
    "AHCM": "Auxiliary heater control module", "BECM": "Battery energy control module",
    "BSCM": "Brake system control module", "CCM": "Chassis control module",
    "CTCM": "Coolant temperature control module", "DMCM": "Drive motor control module",
    "ECCI": "Emission critical control information", "ECM": "Engine control module",
    "FACM": "Fuel additive control module", "FICM": "Fuel injector control module",
    "FPCM": "Fuel pump control module", "FWDC": "Four wheel drive clutch control module",
    "GPCM": "Glow plug control module", "GSM": "Gear shift module", "HPCM": "Hybrid powertrain control module",
    "IPC": "Instrument panel cluster", "PCM": "Powertrain control module", "SGCM": "Starter/generator control module",
    "TACM": "Throttle actuator control module", "TCCM": "Transfer case control module",
    "TCM": "Transmission control module", "UDM": "Urea dosing control module",
}


def decode_vehicle_info(infotype: int, nodi: int, data: bytes) -> Any:
    """Decode the data items of a Mode 09 response (bytes after ``49 <infotype> <NODI>``).

    * 02 VIN: 17 ASCII characters (one ISO-TP message on CAN).
    * 04 CALID: NODI × 16 ASCII bytes, ``00`` padded at the end.
    * 06 CVN: NODI × 4 bytes, shown as 8 hex digits each.
    * 08 / 0B IPT: NODI × u16 big-endian, named per Annex G (08: 16 names, 0B: 18 names);
      extra items get positional names (08 items 17-20 are flagged unverified).
    * 0A ECUNAME: 4-byte acronym, ``-``, 15-byte text, ``00`` filled.
    * anything else: raw hex.
    """
    if infotype == 0x02:
        return data[:17].decode("ascii", "replace")
    if infotype == 0x04:
        return [data[16 * i:16 * i + 16].rstrip(b"\0").decode("ascii", "replace") for i in range(nodi)]
    if infotype == 0x06:
        return [data[4 * i:4 * i + 4].hex().upper() for i in range(nodi)]
    if infotype in (0x08, 0x0B):
        values = [_u16(data, 2 * i) for i in range(nodi) if 2 * i + 1 < len(data)]
        if infotype == 0x08:
            names: List[str] = list(IPT_SPARK_NAMES)
            if len(values) > len(names):
                # UNVERIFIED: the 20-item spark variant's extra names.
                warn_unverified("ipt08-extra", "InfoType 08 returned more than 16 items; items 17-20 "
                                               "named SO2SCOMP1/SO2SCOND1/SO2SCOMP2/SO2SCOND2 per W")
                names += list(IPT_SPARK_EXTRA_NAMES)
        else:
            names = list(IPT_COMPRESSION_NAMES)
        out: Dict[str, int] = {}
        for i, v in enumerate(values):
            out[names[i] if i < len(names) else f"item{i + 1}"] = v
        return out
    if infotype == 0x0A:
        acronym = data[:4].rstrip(b"\0").decode("ascii", "replace")
        text = data[5:20].rstrip(b"\0").decode("ascii", "replace")
        return f"{acronym}-{text}"
    return _raw(data)


def format_value(value: Any, unit: str = "", units: Optional[Mapping[str, str]] = None,
                 precision: int = 2) -> str:
    """Human formatting shared by the CLI and the datalogger (no rounding in decoders)."""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        text = f"{value:.{precision}f}".rstrip("0").rstrip(".") if isinstance(value, float) else str(value)
        return f"{text} {unit}".strip()
    if isinstance(value, (set, frozenset)):
        return ", ".join(f"{v:02X}" for v in sorted(value))
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            u = (units or {}).get(k, unit)
            parts.append(f"{k}={format_value(v, u, None, precision)}")
        return ", ".join(parts) if parts else "(no supported items)"
    if isinstance(value, list):
        return ", ".join(format_value(v, unit, units, precision) for v in value)
    if value is None:
        return "-"
    return str(value)
