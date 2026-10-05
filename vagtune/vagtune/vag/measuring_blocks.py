"""
KWP measuring blocks (``21 <group>`` -> ``61 <group>`` + fields): the VAG formula
table 0x01..0xB5 and a decoder that walks a reply *by formula id*.

Facts (``docs/PROTOCOL_FACTS.md`` §7.7, verified unless stated):

* a field is normally 3 bytes ``(formulaId, A, B)``; real PQ35 engine replies carry
  8 fields (26 bytes), not 4;
* variable-length fields: ``5F <len> <ASCII>`` and ``76 <len> <bytes>`` (the length
  byte counts only the data), ``3F`` = ASCII to the end of the message, ``A0`` = 5
  data bytes ``NW B C D E`` with the KLineKWP1281Lib layout;
* ``8B / 8C / 93`` (value through a 17-byte table) and ``8D`` (string list) need a
  KWP1281 group header that a KWP2000 ``61`` reply does not carry: returned raw with
  ``undecodable=True``;
* the consensus formula column (KLineKWP1281Lib + blafusel + the agreeing tools) is
  the primary table; where the fetched tools disagree (0x04, 0x08, 0x0E, 0x12, 0x14,
  0x19, 0x21, 0x27, 0x2D, 0x2E, 0x51, 0x5E) the other forms are kept as named
  *variants* (``FORMULA_VARIANTS``) that a caller can select; every variant is
  ``unverified=True`` and warns once when used (registry conflict C15);
* "8 fields = groups N and N+128" is REPORTED (medium): the second half is exposed
  raw and only labelled as group N+128 when the caller passes
  ``second_half_is_group_plus_128=True`` after checking it on the car.

Group *names* for the owner's modules are label data (Ross-Tech standardized
gasoline groups, the CJAA / DQ250 / Haldex rows of §9) in :data:`GROUP_LABELS`;
they never drive decoding.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from .dtc import warn_unverified

log = logging.getLogger(__name__)

Compute = Callable[[int, int], Any]


# ================================================================= helpers

def _s16(a: int, b: int) -> int:
    v = (a << 8) | b
    return v - 0x10000 if v & 0x8000 else v


def _s8(b: int) -> int:
    """The table's ``signed(B)``: ``B > 128 -> B - 256`` (KL / blafusel wording, kept
    literally; 128 itself is therefore +128)."""
    return b - 256 if b > 128 else b


def _u16(a: int, b: int) -> int:
    return (a << 8) | b


def _bits(a: int, b: int) -> str:
    return format(b & a, "08b")


# ================================================================= formula model

KIND_VALUE = "value"
KIND_TEXT = "text"
KIND_BITS = "bits"
KIND_TIME = "time"
KIND_DATE = "date"
KIND_TABLE_INDEX = "table-index"     # 0x25 / 0x7B: raw 16-bit index into a label-file text table
KIND_LENGTH_TEXT = "length-text"     # 0x5F
KIND_LENGTH_HEX = "length-hex"       # 0x76
KIND_REST_TEXT = "rest-text"         # 0x3F
KIND_VARIABLE_UNITS = "variable-units"  # 0xA0, 5 data bytes
KIND_UNDECODABLE = "undecodable"     # 0x8B/0x8C/0x93/0x8D (need a KWP1281 header), 0x6C..0x6E, 0x00


@dataclass(frozen=True)
class Formula:
    """One formula-id row. ``compute(A, B)`` returns the physical value (number or
    text); ``kind`` says how to present it; ``variant`` names the source form."""
    id: int
    unit: str
    kind: str
    compute: Optional[Compute]
    label: str
    source: str = "consensus (KL/BL + agreeing tools)"
    variant: str = "consensus"
    unverified: bool = False
    note: str = ""

    @property
    def fixed_size(self) -> Optional[int]:
        """Bytes the field occupies including the id (``None`` = variable)."""
        if self.kind in (KIND_LENGTH_TEXT, KIND_LENGTH_HEX, KIND_REST_TEXT):
            return None
        if self.kind == KIND_VARIABLE_UNITS:
            return 6
        return 3


def _f(fid: int, unit: str, compute: Optional[Compute], label: str, *, kind: str = KIND_VALUE,
       source: str = "consensus (KL/BL + agreeing tools)", note: str = "") -> Tuple[int, Formula]:
    return fid, Formula(fid, unit, kind, compute, label, source=source, note=note)


def _text_table_index(a: int, b: int) -> int:
    return _u16(a, b)


def _date_7f(a: int, b: int) -> str:
    # KL: 200000 + (B&0x7F)*100 + (((A&7)<<1)|(B>>7)) + ((A&0xF8)>>3)*0.01 -> yyyy.mm.dd
    year = 2000 + (b & 0x7F)
    month = ((a & 7) << 1) | (b >> 7)
    day = (a & 0xF8) >> 3
    return f"{year:04d}.{month:02d}.{day:02d}"


# ================================================================= the table
# id: consensus formula (unit) - PROTOCOL_FACTS §7.7 table 3.1, consensus column.

FORMULAS: Dict[int, Formula] = dict([
    _f(0x01, "rpm", lambda a, b: a * b * 0.2, "engine speed"),
    _f(0x02, "%", lambda a, b: a * b * 0.002, "load"),
    _f(0x03, "°", lambda a, b: a * b * 0.002, "throttle angle"),
    _f(0x04, "°", lambda a, b: (b - 127) * a * 0.01, "ignition timing (+ = ATDC, - = BTDC)",
       note="sign convention: B>127 -> ATDC positive, B<127 -> BTDC negative (VB/PY/B3/BL/SC)"),
    _f(0x05, "°C", lambda a, b: (b - 100) * a * 0.1, "temperature"),
    _f(0x06, "V", lambda a, b: a * b * 0.001, "voltage"),
    _f(0x07, "km/h", lambda a, b: a * b * 0.01, "speed"),
    _f(0x08, "", lambda a, b: a * b * 0.1, "scaled value (A*B*0.1)",
       note="VB/PY show the raw 16-bit value instead; see FORMULA_VARIANTS"),
    _f(0x09, "°", lambda a, b: (b - 127) * a * 0.02, "steering angle"),
    _f(0x0A, "", lambda a, b: "COLD" if b == 0 else "WARM", "cold/warm", kind=KIND_TEXT),
    _f(0x0B, "λ", lambda a, b: 1 + (b - 128) * a * 0.0001, "lambda factor"),
    _f(0x0C, "Ω", lambda a, b: a * b * 0.001, "resistance"),
    _f(0x0D, "mm", lambda a, b: (b - 127) * a * 0.001, "distance"),
    _f(0x0E, "bar", lambda a, b: a * b * 0.005, "pressure",
       note="OpenHaldex uses 0.01*A*(B-100) for Haldex oil pressure; see FORMULA_VARIANTS"),
    _f(0x0F, "ms", lambda a, b: a * b * 0.01, "time"),
    _f(0x10, "bits", _bits, "bit field (B & A, A = mask)", kind=KIND_BITS),
    _f(0x11, "", lambda a, b: chr(a) + chr(b), "two ASCII characters", kind=KIND_TEXT),
    _f(0x12, "mbar", lambda a, b: a * b * 0.04, "pressure", note="PyVCDS multiplies by 25 (bug)"),
    _f(0x13, "l", lambda a, b: a * b * 0.01, "volume"),
    _f(0x14, "%", lambda a, b: (b - 128) * a / 128, "lambda integrator / fuel trim",
       note="VB/PY use A*B/128-1; scirocco-dash A*(B-128)*0.01; see FORMULA_VARIANTS"),
    _f(0x15, "V", lambda a, b: a * b * 0.001, "voltage"),
    _f(0x16, "ms", lambda a, b: a * b * 0.001, "injection time"),
    _f(0x17, "%", lambda a, b: a * b / 256, "duty cycle"),
    _f(0x18, "A", lambda a, b: a * b * 0.001, "current"),
    _f(0x19, "g/s", lambda a, b: (256 * b + a) / 180, "air mass (MAF)",
       note="PyVCDS uses (100/A)*B; blafusel B*1.421+A/182; see FORMULA_VARIANTS"),
    _f(0x1A, "°C", lambda a, b: b - a, "temperature (B - A)"),
    _f(0x1B, "°", lambda a, b: (b - 128) * a * 0.01, "ignition angle"),
    _f(0x1C, "", lambda a, b: b - a, "difference (B - A)"),
    _f(0x1D, "", lambda a, b: "Map 1" if b < a else "Map 2", "map selector", kind=KIND_TEXT),
    _f(0x1E, "°KW", lambda a, b: b / 12 * a, "knock retard"),
    _f(0x1F, "°C", lambda a, b: b / 2560 * a, "temperature"),
    _f(0x20, "", lambda a, b: _s8(b), "signed byte (B)"),
    _f(0x21, "%", lambda a, b: 100 * b / a if a else 100 * b, "percentage (100*B/A)",
       note="OpenHaldex uses 0.01*A*B for Haldex clutch duty; see FORMULA_VARIANTS"),
    _f(0x22, "kW", lambda a, b: (b - 128) * a * 0.01, "power / knock retard"),
    _f(0x23, "l/h", lambda a, b: a * b / 100, "consumption"),
    _f(0x24, "km", lambda a, b: (a * 256 + b) * 10, "distance"),
    _f(0x25, "", _text_table_index, "text from label-file table (raw 16-bit index)", kind=KIND_TABLE_INDEX,
       note="VCDS resolves the text from the label file; 25 00 00 is the usual empty filler"),
    _f(0x26, "°KW", lambda a, b: (b - 128) * a * 0.001, "crank angle"),
    _f(0x27, "mg/stroke", lambda a, b: a * b / 256, "fuel mass per stroke",
       note="KL divides by 255; see FORMULA_VARIANTS"),
    _f(0x28, "A", lambda a, b: (a * 255 + b - 4000) * 0.1, "current", source="KL/BL"),
    _f(0x29, "Ah", lambda a, b: a * 255 + b, "charge", source="KL/BL"),
    _f(0x2A, "kW", lambda a, b: (a * 255 + b - 4000) * 0.1, "power", source="KL/BL"),
    _f(0x2B, "V", lambda a, b: (a * 255 + b) * 0.1, "voltage", source="KL/BL"),
    _f(0x2C, "h:m", lambda a, b: f"{a}:{b:02d}", "time of day (A:B)", kind=KIND_TIME, source="KL/BL"),
    _f(0x2D, "l/km", lambda a, b: a * b * 0.1, "consumption", source="KL",
       note="blafusel: 0.1*A*B/100 (x100 disagreement); see FORMULA_VARIANTS"),
    _f(0x2E, "°KW", lambda a, b: ((a * 256) + b - 32768) * 0.00275, "crank angle", source="KL",
       note="blafusel (A*B-3200)*0.0027 is probably garbled; see FORMULA_VARIANTS"),
    _f(0x2F, "ms", lambda a, b: (b - 128) * a, "time", source="KL/BL"),
    _f(0x30, "", lambda a, b: a * 255 + b, "value (A*255+B)", source="KL/BL"),
    _f(0x31, "mg/stroke", lambda a, b: a * b * 0.025, "air mass per stroke"),
    _f(0x32, "mbar", lambda a, b: (b - 128) * 100 / a if a else (b - 128) * 100 / 0.01, "pressure", source="KL/BL"),
    _f(0x33, "mg/stroke", lambda a, b: (b - 128) * a / 255, "fuel mass delta"),
    _f(0x34, "Nm", lambda a, b: (b - 50) * a * 0.02, "torque", source="KL/BL"),
    _f(0x35, "g/s", lambda a, b: ((b - 128) * 256 + a) / 180, "air mass (signed)", source="KL/BL"),
    _f(0x36, "", _u16, "count (A*256+B)"),
    _f(0x37, "s", lambda a, b: a * b / 200, "time"),
    _f(0x38, "", _u16, "WSC (bit 16 = 0)", source="KL/BL"),
    _f(0x39, "", lambda a, b: a * 256 + b + 65536, "WSC (bit 16 = 1)", source="KL/BL"),
    _f(0x3A, "/s", lambda a, b: _s8(b) * 1.023, "misfires per second", source="KL"),
    _f(0x3B, "", lambda a, b: (a * 256 + b) / 32768, "ratio", source="KL/BL"),
    _f(0x3C, "s", lambda a, b: (a * 256 + b) / 100, "time", source="KL/BL"),
    _f(0x3D, "", lambda a, b: (b - 128) / a if a else b - 128, "ratio", source="KL/BL"),
    _f(0x3E, "s", lambda a, b: a * b * 0.256, "time", source="KL/BL"),
    _f(0x3F, "", None, "ASCII text to the end of the message", kind=KIND_REST_TEXT, source="KL"),
    _f(0x40, "Ω", lambda a, b: a + b, "resistance (A+B)", source="KL/BL"),
    _f(0x41, "mm", lambda a, b: (b - 127) * a * 0.01, "distance", source="KL/BL"),
    _f(0x42, "V", lambda a, b: a * b / 512, "voltage", source="KL/BL"),
    _f(0x43, "°", lambda a, b: _s16(a, b) * 2.5, "steering angle", source="KL/BL"),
    _f(0x44, "°/s", lambda a, b: _s16(a, b) * 0.1358, "yaw rate", source="KL/BL"),
    _f(0x45, "bar", lambda a, b: _s16(a, b) * 0.3255, "pressure", source="KL/BL"),
    _f(0x46, "m/s²", lambda a, b: _s16(a, b) * 0.192, "acceleration", source="KL/BL"),
    _f(0x47, "cm", lambda a, b: a * b, "distance", source="KL only"),
    _f(0x48, "V", lambda a, b: (a * 255 + b * (211 - a)) / 4080, "voltage", source="KL only"),
    _f(0x49, "Ω", lambda a, b: a * b * 0.01, "resistance", source="KL only"),
    _f(0x4A, "months", lambda a, b: a * b * 0.1, "time", source="KL only"),
    _f(0x4B, "", _u16, "fault code number", source="KL only"),
    _f(0x4C, "kΩ", lambda a, b: a * 255 + b, "resistance", source="KL only"),
    _f(0x4D, "V", lambda a, b: (255 * a + b * 60) / 4080, "voltage", source="KL only"),
    _f(0x4E, "/s", lambda a, b: _s8(b) * 1.819, "misfires per second", source="KL only"),
    _f(0x4F, "", lambda a, b: b, "channel number", source="KL only"),
    _f(0x50, "kΩ", lambda a, b: (a * 256 + b) / 100, "resistance", source="KL only"),
    _f(0x51, "°", lambda a, b: _s16(a, b) * 0.04375, "steering angle",
       source="KL", note="vag-blocks / PyVCDS use (A*112000|11200 + B*436)/1000; see FORMULA_VARIANTS"),
    _f(0x52, "m/s²", lambda a, b: _s16(a, b) * 0.00981, "acceleration", source="KL only"),
    _f(0x53, "bar", lambda a, b: _s16(a, b) * 0.01, "pressure (absolute)", source="KL; SC fitted vs PID 23"),
    _f(0x54, "m/s²", lambda a, b: _s16(a, b) * 0.0973, "acceleration", source="KL only"),
    _f(0x55, "°/s", lambda a, b: _s16(a, b) * 0.002865, "turn rate", source="KL only"),
    _f(0x56, "A", lambda a, b: a * b * 0.1, "current", source="KL only"),
    _f(0x57, "°/s", lambda a, b: (b - 128) * a * 0.1, "turn rate", source="KL only"),
    _f(0x58, "kΩ", lambda a, b: a * b * 0.01, "resistance", source="KL only"),
    _f(0x59, "h", _u16, "operating hours", source="KL only"),
    _f(0x5A, "kg", lambda a, b: a * b * 0.1, "mass", source="KL only"),
    _f(0x5B, "°", lambda a, b: (b - 128) * a * 0.1, "steering angle", source="KL only"),
    _f(0x5C, "km", lambda a, b: a * b, "distance", source="KL only"),
    _f(0x5D, "Nm", lambda a, b: (b - 128) * a * 0.001, "torque", source="KL only"),
    _f(0x5E, "Nm", lambda a, b: (b - 128) * a * 0.1, "torque",
       source="KL + OpenHaldex (confirmed against VCDS)", note="vag-blocks' A*(B/50-1) is its own flagged guess"),
    _f(0x5F, "", None, "ASCII text with length byte", kind=KIND_LENGTH_TEXT, source="PY/KL/DV"),
    _f(0x60, "mbar", lambda a, b: a * b * 0.1, "pressure", source="KL + teensy + VDS group 115"),
    _f(0x61, "°C", lambda a, b: (b - a) * 5, "catalyst temperature", source="KL only"),
    _f(0x62, "imp/km", lambda a, b: a * b * 0.1, "impulses per km", source="KL only"),
    _f(0x63, "", _s16, "signed 16-bit", source="KL only"),
    _f(0x64, "bar", lambda a, b: a * b * 0.1, "pressure", source="KL only"),
    _f(0x65, "l/mm", lambda a, b: a * b * 0.001, "volume per mm", source="KL only"),
    _f(0x66, "mm", lambda a, b: a * b * 0.1, "fuel level", source="KL only"),
    _f(0x67, "V", lambda a, b: a + b * 0.05, "voltage", source="KL only"),
    _f(0x68, "ml", lambda a, b: (b - 128) * a * 0.2, "volume", source="KL only"),
    _f(0x69, "m", lambda a, b: (b - 128) * a * 0.01, "distance", source="KL only"),
    _f(0x6A, "km/h", lambda a, b: (b - 128) * a * 0.1, "speed (signed)", source="KL only"),
    _f(0x6B, "", lambda a, b: f"{a:02X}{b:02X}", "hex text", kind=KIND_TEXT, source="KL only"),
    _f(0x6C, "", None, "Environment (undecoded text)", kind=KIND_UNDECODABLE, source="KL only (listed, unknown)"),
    _f(0x6D, "", None, "N/A (undecoded)", kind=KIND_UNDECODABLE, source="KL only (listed, unknown)"),
    _f(0x6E, "", None, "Workshop (undecoded text)", kind=KIND_UNDECODABLE, source="KL only (listed, unknown)"),
    _f(0x6F, "km", lambda a, b: 0x6F0000 | (a << 8) | b, "distance (odd KL form)", source="KL only"),
    _f(0x70, "°", lambda a, b: (b - 128) * a * 0.001, "angle", source="KL only"),
    _f(0x71, "", lambda a, b: (b - 128) * a * 0.01, "signed scaled value", source="KL only; seen in real replies"),
    _f(0x72, "m", lambda a, b: (b - 128) * a, "altitude", source="KL only"),
    _f(0x73, "W", _s16, "power", source="KL only"),
    _f(0x74, "rpm", _s16, "speed (signed)", source="KL only"),
    _f(0x75, "°C", lambda a, b: (b - 64) * a * 0.01, "temperature", source="KL only"),
    _f(0x76, "", None, "hex bytes with length byte", kind=KIND_LENGTH_HEX, source="KL"),
    _f(0x77, "%", lambda a, b: a * b * 0.01, "percentage", source="KL only"),
    _f(0x78, "°", lambda a, b: a * b * 1.41, "angle", source="KL only"),
    _f(0x79, "", lambda a, b: ((b * 256) + a) * 0.5, "value", source="KL only"),
    _f(0x7A, "", lambda a, b: ((b * 256) + a - 32768) * 0.01, "value (signed)", source="KL only"),
    _f(0x7B, "", _text_table_index, "text from label-file table (raw 16-bit index)", kind=KIND_TABLE_INDEX,
       source="KL only"),
    _f(0x7C, "mA", lambda a, b: a * b * 0.1, "current", source="KL only"),
    _f(0x7D, "dB", lambda a, b: a - b, "attenuation", source="KL only"),
    _f(0x7E, "", lambda a, b: a * b * 0.1, "scaled value (teensy: grams)", source="KL + teensy"),
    _f(0x7F, "", _date_7f, "date", kind=KIND_DATE, source="KL only"),
    _f(0x80, "rpm", lambda a, b: a * b, "speed", source="KL only"),
    _f(0x81, "%", lambda a, b: a * b / 256, "percentage", source="KL only"),
    _f(0x82, "A", lambda a, b: a * b / 2560, "current", source="KL only"),
    _f(0x83, "°", lambda a, b: a * b * 0.5 - 30, "angle", source="KL only"),
    _f(0x84, "°", lambda a, b: a * b * 0.5, "angle", source="KL only"),
    _f(0x85, "V", lambda a, b: a * b / 256, "voltage", source="KL only"),
    _f(0x86, "km/h", lambda a, b: a * b, "speed", source="KL only"),
    _f(0x87, "", lambda a, b: a * b, "value (A*B)", source="KL only"),
    _f(0x88, "bits", _bits, "bit field (B & A)", kind=KIND_BITS, source="KL only"),
    _f(0x89, "ms", lambda a, b: a * b * 0.01, "time", source="KL only"),
    _f(0x8A, "V", lambda a, b: a * b * 0.001, "knock sensor voltage", source="KL only"),
    _f(0x8B, "rpm", None, "value through a module-supplied 17-byte table (KWP1281 header only)",
       kind=KIND_UNDECODABLE, source="KL only"),
    _f(0x8C, "°C", None, "value through a module-supplied 17-byte table (KWP1281 header only)",
       kind=KIND_UNDECODABLE, source="KL only"),
    _f(0x8D, "", None, "string from a module-supplied list (KWP1281 header only)",
       kind=KIND_UNDECODABLE, source="KL only"),
    _f(0x8E, "", lambda a, b: chr(a) + chr(b), "two ASCII characters", kind=KIND_TEXT, source="KL only"),
    _f(0x8F, "°", lambda a, b: (b - 128) * a * 0.01, "angle", source="KL only"),
    _f(0x90, "l/h", lambda a, b: a * b * 0.01, "consumption", source="KL only"),
    _f(0x91, "", lambda a, b: a * b * 0.01, "scaled value", source="KL only"),
    _f(0x92, "λ", lambda a, b: 1 + (b - 128) * a * 0.0001, "lambda", source="KL only"),
    _f(0x93, "%", None, "value through a module-supplied 17-byte table (KWP1281 header only)",
       kind=KIND_UNDECODABLE, source="KL only"),
    _f(0x94, "rpm", lambda a, b: (b - 128) * a * 0.25, "slip", source="KL only"),
    _f(0x95, "°C", lambda a, b: (b - 100) * a * 0.1, "temperature", source="KL only"),
    _f(0x96, "g/s", lambda a, b: (256 * b + a) / 180, "air mass", source="KL only"),
    _f(0x97, "kW", lambda a, b: (b - 128) * a * 0.01, "power", source="KL only"),
    _f(0x98, "mg/stroke", lambda a, b: a * b * 0.025, "mass per stroke", source="KL only"),
    _f(0x99, "mg/stroke", lambda a, b: (b - 128) * a / 255, "mass per stroke (signed)", source="KL only"),
    _f(0x9A, "°", lambda a, b: a * b, "angle", source="KL only"),
    _f(0x9B, "°", lambda a, b: a * b * 0.01 - 90, "angle", source="KL only"),
    _f(0x9C, "cm", _u16, "distance", source="KL only"),
    _f(0x9D, "cm", _s16, "distance (signed)", source="KL only"),
    _f(0x9E, "km/h", lambda a, b: (a * 256 + b) * 0.01, "speed", source="KL only"),
    _f(0x9F, "°C", lambda a, b: ((b - 127) * 256 + a) * 0.1, "temperature", source="KL only"),
    _f(0xA0, "", None, "value with variable units (5 data bytes)", kind=KIND_VARIABLE_UNITS, source="KL"),
    _f(0xA1, "bits", lambda a, b: f"{a:08b} {b:08b}", "two binary bytes", kind=KIND_BITS, source="KL only"),
    _f(0xA2, "°", lambda a, b: a * b * 0.448, "angle", source="KL only"),
    _f(0xA3, "hh:mm", lambda a, b: f"{a}:{b:02d}", "time of day", kind=KIND_TIME, source="KL only"),
    _f(0xA4, "%", lambda a, b: b if b <= 100 else (b - 100 if b <= 200 else b), "percentage", source="KL only"),
    _f(0xA5, "mA", lambda a, b: (b * 256) + a - 32768, "current", source="KL only"),
    _f(0xA6, "°/s", lambda a, b: _s16(a, b) * 2.5, "turn rate", source="KL only"),
    _f(0xA7, "mΩ", lambda a, b: a * b * 0.001, "resistance", source="KL only"),
    _f(0xA8, "%", lambda a, b: (256 * a + b) * 0.01, "percentage", source="KL only"),
    _f(0xA9, "mV", lambda a, b: a * b + 200, "Nernst voltage", source="KL only"),
    _f(0xAA, "g", lambda a, b: a * b / 2560, "mass (NH3)", source="KL only"),
    _f(0xAB, "g", lambda a, b: a * b / 2560, "mass (NOx)", source="KL only"),
    _f(0xAC, "mg/km", lambda a, b: a * b, "NOx per km", source="KL only"),
    _f(0xAD, "mg/s", lambda a, b: a * b * 0.1, "NOx mass flow", source="KL only"),
    _f(0xAE, "km", lambda a, b: a * b * 0.01, "distance (avg DEF)", source="KL only"),
    _f(0xAF, "bar", lambda a, b: a * b * 0.005, "pressure (DEF)", source="KL only"),
    _f(0xB0, "ppm", lambda a, b: a * b * 0.1, "NOx concentration", source="KL only"),
    _f(0xB1, "Nm", lambda a, b: (a - 128) * 256 + b, "torque", source="KL only"),
    _f(0xB2, "°/s", lambda a, b: ((a - 128) * 256 + b) * 6 / 51, "turn rate", source="KL only"),
    _f(0xB3, "", lambda a, b: (a * 256 + b) * 10, "value", source="KL only"),
    _f(0xB4, "kg/h", lambda a, b: a * b / 256, "mass flow", source="KL only"),
    _f(0xB5, "mg/s", lambda a, b: a * b * 0.001, "mass flow", source="KL only"),
])

#: Formula ids that are a plain 3-byte field but cannot be decoded as a value over
#: KWP2000 (no table / no meaning known). 0x00 is not a formula; a ``00 xx yy``
#: triplet is returned raw.
UNDECODABLE_IDS = frozenset(fid for fid, f in FORMULAS.items() if f.kind == KIND_UNDECODABLE) | {0x00}

LAST_VALID_FORMULA = 0xB5   # KL: "There are no valid formulas after B5"


def _v(fid: int, variant: str, unit: str, compute: Compute, label: str, source: str, note: str = "") -> Formula:
    return Formula(fid, unit, KIND_VALUE, compute, label, source=source, variant=variant,
                   unverified=True, note=note)


#: Named alternate forms for the disputed ids (registry conflict C15). Selecting one
#: marks the value ``unverified`` and warns once.
FORMULA_VARIANTS: Dict[int, Dict[str, Formula]] = {
    0x04: {"kl-btdc-positive": _v(0x04, "kl-btdc-positive", "°", lambda a, b: (b - 127) * a * -0.01,
                                  "ignition timing (BTDC positive)", "KLineKWP1281Lib")},
    0x08: {"vb-raw16": _v(0x08, "vb-raw16", "", _u16, "raw 16-bit ('Binary')", "vag-blocks / PyVCDS")},
    0x0E: {"openhaldex": _v(0x0E, "openhaldex", "bar", lambda a, b: 0.01 * a * (b - 100),
                            "Haldex oil pressure", "OpenHaldex-C6",
                            "a=27,b=200 -> 27 bar under both forms; a Haldex sample with B != 200 discriminates")},
    0x12: {"pyvcds-x25-bug": _v(0x12, "pyvcds-x25-bug", "mbar", lambda a, b: a * b * 25,
                                "pressure (PyVCDS multiplies instead of dividing)", "PyVCDS (bug)")},
    0x14: {"vb-py": _v(0x14, "vb-py", "%", lambda a, b: a * b / 128 - 1, "lambda integrator", "vag-blocks / PyVCDS"),
           "sc-fitted": _v(0x14, "sc-fitted", "%", lambda a, b: a * (b - 128) * 0.01, "fuel trim (fitted)",
                           "scirocco-dash")},
    0x19: {"pyvcds": _v(0x19, "pyvcds", "g/s", lambda a, b: (100 / a) * b if a else float("nan"), "air mass",
                        "PyVCDS"),
           "blafusel": _v(0x19, "blafusel", "g/s", lambda a, b: b * 1.421 + a / 182, "air mass",
                          "blafusel / scirocco-dash (verified at idle)")},
    0x21: {"openhaldex": _v(0x21, "openhaldex", "%", lambda a, b: 0.01 * a * b, "Haldex clutch duty", "OpenHaldex-C6",
                            "a=100,b=40 -> 40 % under both forms; a Haldex sample with A != 100 discriminates")},
    0x27: {"kl-255": _v(0x27, "kl-255", "mg/stroke", lambda a, b: a * b / 255, "fuel mass per stroke", "KLineKWP1281Lib")},
    0x2D: {"blafusel": _v(0x2D, "blafusel", "l/km", lambda a, b: 0.1 * a * b / 100, "consumption", "blafusel")},
    0x2E: {"blafusel": _v(0x2E, "blafusel", "°KW", lambda a, b: (a * b - 3200) * 0.0027, "crank angle",
                          "blafusel (likely garbled)")},
    0x51: {"vag-blocks": _v(0x51, "vag-blocks", "°", lambda a, b: (a * 112000 + b * 436) / 1000, "torsion",
                            "vag-blocks ('check formula')"),
           "pyvcds": _v(0x51, "pyvcds", "°", lambda a, b: (a * 11200 + b * 436) / 1000, "torsion", "PyVCDS")},
    0x5E: {"vag-blocks": _v(0x5E, "vag-blocks", "Nm", lambda a, b: a * (b / 50 - 1), "torque",
                            "vag-blocks ('check formula'), copied by PyVCDS / scirocco-dash")},
}

DISPUTED_IDS = frozenset(FORMULA_VARIANTS)


def formula(fid: int, variant: Optional[str] = None) -> Optional[Formula]:
    """The consensus row for ``fid`` (``None`` when the id is not in the table), or a
    named variant from :data:`FORMULA_VARIANTS` (``KeyError`` for an unknown name)."""
    if variant is None or variant == "consensus":
        return FORMULAS.get(fid)
    try:
        return FORMULA_VARIANTS[fid][variant]
    except KeyError:
        raise KeyError(f"formula 0x{fid:02X} has no variant {variant!r}; known: "
                       f"{sorted(FORMULA_VARIANTS.get(fid, {}))}") from None


# ================================================================= 0xA0 units

#: KL ``getMeasurementUnits``: ``E & 0x3F`` selects the base unit, ``E >> 6`` a prefix.
A0_UNIT_PREFIX = {0: "", 1: "k", 2: "m", 3: "u"}
A0_BASE_UNITS: Dict[int, str] = {
    0x01: "V", 0x02: "V/s", 0x03: "A", 0x04: "capacity", 0x05: "Ω", 0x06: "W", 0x07: "W/m²",
    0x08: "W/cm²", 0x09: "Wh", 0x0A: "Ws", 0x0B: "distance", 0x0C: "m/s", 0x0D: "acceleration",
    0x0E: "cm", 0x0F: "speed", 0x10: "volume", 0x11: "l/100km", 0x12: "fuel-level factor",
    0x13: "l/h", 0x14: "l/km", 0x15: "time", 0x16: "h", 0x17: "months", 0x18: "mass",
    0x19: "mass flow", 0x1A: "mg/stroke", 0x1B: "torque", 0x1C: "N", 0x1D: "pressure",
    0x1E: "angle", 0x1F: "°", 0x20: "temperature", 0x21: "°F", 0x22: "turn rate",
    0x23: "° ignition", 0x24: "rpm", 0x25: "%", 0x26: "correction", 0x27: "correction",
    0x28: "misfires", 0x29: "impulses", 0x2A: "dB",
}
A0_UNIT_IGNITION_ANGLE = 0x23


def decode_a0(nw: int, b: int, c: int, d: int, e: int) -> Tuple[float, str, str]:
    """KL's variable-units formula: ``(value, unit, text)``.

    ``WORD_BC = B<<8 | C``; bit 7 of D negates it unless the unit is the ignition
    angle (then it means BTDC); ``value = NW * WORD_BC * (D & 0x0F) * 10^-((D>>4)&7)``.
    """
    word = (b << 8) | c
    unit_code = e & 0x3F
    btdc = ""
    if d & 0x80:
        if unit_code == A0_UNIT_IGNITION_ANGLE:
            btdc = " BTDC"
        else:
            word = -word
    elif unit_code == A0_UNIT_IGNITION_ANGLE:
        btdc = " ATDC"
    dl = d & 0x0F
    dh = (d >> 4) & 7
    value = nw * word * dl * (10.0 ** -dh)
    unit = A0_UNIT_PREFIX[e >> 6] + A0_BASE_UNITS.get(unit_code, f"unit 0x{unit_code:02X}")
    return value, unit, f"{value:g} {unit}{btdc}".strip()


# ================================================================= values

@dataclass
class MeasuringValue:
    """One decoded field of a ``61 <group>`` reply.

    ``value`` is the physical number (or the text for text-like formulas), ``text`` a
    display string, ``raw`` the field bytes including the formula id. ``unverified``
    marks a variant formula or a label the facts only *report*; ``undecodable``
    marks fields whose meaning needs data the KWP2000 reply does not carry (the
    raw bytes are still here). ``group`` / ``field`` label the value as VCDS would
    (``field`` is 1-based; ``group`` is ``None`` for the raw second half of an 8-field
    reply unless the caller asserted the N+128 convention).
    """
    formula_id: int
    a: int
    b: int
    value: Any
    unit: str
    text: str
    raw: bytes
    unverified: bool = False
    undecodable: bool = False
    index: int = 0
    group: Optional[int] = None
    field: Optional[int] = None
    label: str = ""
    variant: str = "consensus"
    note: str = ""

    @property
    def decoded(self) -> bool:
        return not self.undecodable

    def __str__(self) -> str:
        where = ""
        if self.group is not None and self.field is not None:
            where = f"{self.group:03d}.{self.field} "
        elif self.field is not None:
            where = f"field {self.field} "
        flags = ""
        if self.undecodable:
            flags = " [raw]"
        elif self.unverified:
            flags = " [unverified]"
        return f"{where}{self.text}{flags}".strip()


def _fmt(value: Any, unit: str) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        s = f"{value:.3f}".rstrip("0").rstrip(".")
        if s in ("-0", ""):
            s = "0"
    else:
        s = str(value)
    return f"{s} {unit}".strip() if unit else s


def decode_field(fid: int, a: int, b: int, *, variant: Optional[str] = None) -> MeasuringValue:
    """Decode one 3-byte field ``(fid, A, B)`` with the consensus formula or a named
    variant (which is unverified and warns once)."""
    raw = bytes([fid, a, b])
    f = formula(fid, variant) if (variant and variant != "consensus") else FORMULAS.get(fid)
    if f is None or f.kind == KIND_UNDECODABLE or f.compute is None:
        label = f.label if f is not None else ("not a formula (0x00)" if fid == 0 else
                                               f"formula 0x{fid:02X} not in the table")
        return MeasuringValue(fid, a, b, _u16(a, b), "", f"raw {raw.hex(' ')}", raw,
                              unverified=True, undecodable=True, label=label,
                              note=f.note if f is not None else "")
    if f.unverified:
        warn_unverified(f"formula-variant:{fid:02X}:{f.variant}",
                        f"measuring-block formula 0x{fid:02X} decoded with the {f.variant!r} form "
                        f"({f.source}) instead of the consensus column; confirm against VCDS on the car")
    try:
        value = f.compute(a, b)
    except (ZeroDivisionError, ValueError, OverflowError) as exc:
        return MeasuringValue(fid, a, b, None, f.unit, f"undefined ({exc})", raw, unverified=f.unverified,
                              undecodable=True, label=f.label, variant=f.variant)
    if f.kind in (KIND_TEXT, KIND_TIME, KIND_DATE):
        text = str(value)
    elif f.kind == KIND_BITS:
        text = f"{value} (bits)" if " " not in str(value) else str(value)
    elif f.kind == KIND_TABLE_INDEX:
        text = f"text #{value} (label file)"
    else:
        text = _fmt(value, f.unit)
    return MeasuringValue(fid, a, b, value, f.unit, text, raw, unverified=f.unverified,
                          label=f.label, variant=f.variant, note=f.note)


def decode_group(data: bytes, *, group: Optional[int] = None,
                 variants: Optional[Mapping[int, str]] = None,
                 second_half_is_group_plus_128: bool = False) -> List[MeasuringValue]:
    """Decode the bytes after ``61 <group>`` into fields, walking by formula id.

    ``variants`` maps formula id -> variant name for the disputed ids. With 8 fields
    the second four are exposed raw-labelled (``group=None``, ``field`` 5..8); pass
    ``second_half_is_group_plus_128=True`` only after confirming on the car that
    ``21 <N+128>`` returns those same fields (REPORTED convention; warns once).
    A truncated trailing field is kept as an undecodable raw value, never dropped.
    """
    variants = variants or {}
    out: List[MeasuringValue] = []
    pos = 0
    n = len(data)
    while pos < n:
        fid = data[pos]
        f = FORMULAS.get(fid)
        kind = f.kind if f is not None else KIND_VALUE
        if kind == KIND_REST_TEXT:
            raw = bytes(data[pos:])
            text = raw[1:].decode("latin-1").rstrip()
            out.append(MeasuringValue(fid, 0, 0, text, "", text, raw, index=len(out), label=f.label))
            break
        if kind in (KIND_LENGTH_TEXT, KIND_LENGTH_HEX):
            if pos + 1 >= n:
                out.append(_truncated(fid, data[pos:], len(out)))
                break
            length = data[pos + 1]
            raw = bytes(data[pos:pos + 2 + length])
            body = raw[2:]
            truncated = len(body) < length
            if kind == KIND_LENGTH_TEXT:
                value: Any = body.decode("latin-1").rstrip()
                text = str(value)
            else:
                value = body
                text = body.hex(" ")
            out.append(MeasuringValue(fid, length, 0, value, "", text, raw, index=len(out), label=f.label,
                                      undecodable=truncated, unverified=truncated,
                                      note="truncated field" if truncated else ""))
            pos += 2 + length
            continue
        if kind == KIND_VARIABLE_UNITS:
            raw = bytes(data[pos:pos + 6])
            if len(raw) < 6:
                out.append(_truncated(fid, raw, len(out)))
                break
            nw, b, c, d, e = raw[1], raw[2], raw[3], raw[4], raw[5]
            value, unit, text = decode_a0(nw, b, c, d, e)
            out.append(MeasuringValue(fid, nw, b, value, unit, text, raw, index=len(out), label=f.label,
                                      note="5-byte variable-units field (KL layout)"))
            pos += 6
            continue
        raw = bytes(data[pos:pos + 3])
        if len(raw) < 3:
            out.append(_truncated(fid, raw, len(out)))
            break
        mv = decode_field(fid, raw[1], raw[2], variant=variants.get(fid))
        mv.index = len(out)
        out.append(mv)
        pos += 3
    _label_fields(out, group, second_half_is_group_plus_128)
    return out


def _truncated(fid: int, raw: bytes, index: int) -> MeasuringValue:
    return MeasuringValue(fid, raw[1] if len(raw) > 1 else 0, raw[2] if len(raw) > 2 else 0,
                          None, "", f"truncated {raw.hex(' ')}", bytes(raw), unverified=True,
                          undecodable=True, index=index, label="truncated field")


def _label_fields(values: List[MeasuringValue], group: Optional[int], second_half: bool) -> None:
    for i, mv in enumerate(values):
        mv.field = i + 1
        mv.group = group
    if len(values) == 8 and group is not None:
        for i, mv in enumerate(values[4:]):
            if second_half:
                mv.group = group + 128
                mv.field = i + 1
                mv.unverified = True
                mv.note = (mv.note + "; " if mv.note else "") + "labelled as group N+128 (REPORTED convention)"
            else:
                mv.group = None
                mv.field = i + 5
                mv.note = (mv.note + "; " if mv.note else "") + "second half of an 8-field reply (group unlabelled)"
        if second_half:
            warn_unverified("kwp-8-field-n-plus-128",
                            "fields 5..8 of an 8-field measuring-block reply labelled as group N+128 "
                            "(DV's statement, medium); confirm with `21 <N+128>` on the car")


def format_group(values: Sequence[MeasuringValue]) -> str:
    return "\n".join(f"  {v}" for v in values)


# ================================================================= OBD mirror (UDS)

def obd_mirror_did_decoder(did: int) -> Optional[Callable[[bytes], Any]]:
    """For a UDS OBD-mirror DID (``0xF400 + PID``) return a decoder ``bytes -> value``
    built from :mod:`vagtune.obd.pids`, else ``None`` (unknown PID, other DID, or the
    OBD package not importable). Imported lazily; ``vag`` may depend on ``obd``."""
    if not 0xF400 <= did <= 0xF4FF:
        return None
    pid = did - 0xF400
    try:
        from ..obd import pids as obd_pids
    except ImportError:
        return None
    pid_def = getattr(obd_pids, "pid_def", None)
    decode_pid = getattr(obd_pids, "decode_pid", None)
    if pid_def is None or decode_pid is None or pid_def(pid) is None:
        return None
    return lambda raw: decode_pid(pid, raw)


# ================================================================= label data

@dataclass(frozen=True)
class GroupLabel:
    group: int
    fields: Tuple[str, ...]
    verified: bool = True
    source: str = ""


def _g(group: int, *fields: str, verified: bool = True, source: str = "Ross-Tech standardized gasoline groups") -> GroupLabel:
    return GroupLabel(group, tuple(fields), verified, source)


#: Field names per module family (label data only; PROTOCOL_FACTS §7.7 3.2 and §9).
GROUP_LABELS: Dict[str, Dict[int, GroupLabel]] = {
    "me7-gasoline-standard": {g.group: g for g in [
        _g(0, "coolant temp", "load", "RPM", "throttle angle", "idle control", "idle learning",
           "lambda control B1", "lambda control B2", "lambda adaptation (add) B1", "lambda adaptation (add) B2"),
        _g(1, "RPM [1/min]", "coolant [°C]", "lambda control value B1 [%]", "lambda control value B2 [%]"),
        _g(2, "RPM", "load [%]", "mean injection time [ms]", "air mass [g/s]"),
        _g(3, "RPM", "air mass [g/s]", "throttle valve angle [%]", "ignition angle actual [°KW]"),
        _g(4, "RPM", "voltage [V]", "coolant [°C]", "intake air temp [°C]"),
        _g(5, "RPM", "load", "speed [km/h]", "operating condition"),
        _g(6, "RPM", "load", "intake air temp", "altitude correction [%]"),
        _g(10, "RPM", "load", "throttle angle", "ignition angle actual"),
        _g(11, "RPM", "coolant", "intake air temp", "ignition angle actual"),
        _g(14, "RPM", "load", "misfire counter", "misfire recognition"),
        _g(15, "misfires cyl 1", "misfires cyl 2", "misfires cyl 3", "recognition status"),
        _g(16, "misfires cyl 4", "misfires cyl 5", "misfires cyl 6", "recognition status"),
        _g(18, "lower RPM", "upper RPM", "lower load [%]", "upper load [%]"),
        _g(20, "retard cyl 1 [°KW]", "retard cyl 2", "retard cyl 3", "retard cyl 4"),
        _g(21, "retard cyl 5 [°KW]", "retard cyl 6", "retard cyl 7", "retard cyl 8"),
        _g(30, "O2 status B1S1", "O2 status B1S2", "O2 status B2S1", "O2 status B2S2"),
        _g(31, "O2 voltage B1S1 / lambda actual B1", "B1S2 / lambda specified B1", "B2S1 / lambda actual B2",
           "B2S2 / lambda specified B2"),
        _g(32, "lambda learning B1 idle [%]", "B1 partial load [%]", "B2 idle [%]", "B2 partial load [%]"),
        _g(33, "lambda control B1 [%]", "sensor voltage B1 [V]", "lambda control B2 [%]", "sensor voltage B2 [V]"),
        _g(50, "RPM actual", "RPM specified", "A/C request", "A/C compressor"),
        _g(53, "RPM actual", "RPM specified", "voltage", "generator load [%]"),
        _g(54, "RPM", "operating condition", "accelerator pedal sensor 1 [%]", "throttle angle [%]"),
        _g(60, "throttle pot 1 [%]", "throttle pot 2 [%]", "adaptation status counter", "ADP text"),
        _g(63, "pedal sensor 1", "learned kick-down point", "switch", "ADP result"),
        _g(66, "speed actual", "switch bits", "speed specified", "lever bits"),
        _g(70, "purge opening [%]", "lambda diag value", "idle diag value", "result"),
        _g(71, "reed contact", "DTC small-large leak", "test status", "result"),
        _g(77, "RPM", "engine air mass [g/s]", "SAI air mass [g/s]", "result"),
        _g(78, "RPM", "engine air mass [g/s]", "SAI air mass [g/s]", "result"),
        _g(80, "manufacturer code", "manufacturing date", "change status", "test stand / running no."),
        _g(81, "VIN", "serial no.", "type test number", ""),
        _g(82, "flash tool code", "flash date", "HW comp group+type", "SW comp group+type"),
        _g(90, "RPM", "exhaust cam duty [%]", "adjustment specified [°KW]", "actual [°KW]"),
        _g(91, "RPM", "intake cam B1 duty [%]", "specified [°KW]", "actual [°KW]"),
        _g(93, "phase intake B1 [°KW]", "intake B2", "exhaust B1", "exhaust B2"),
        _g(95, "RPM", "load", "coolant", "manifold change-over status"),
        _g(99, "RPM", "coolant", "lambda regulation [%]", "lambda regulation ON/OFF"),
        _g(100, "readiness bits", "coolant", "time since start", "OBD status bits"),
        _g(101, "RPM", "load", "mean injection time [ms]", "air mass [g/s]"),
        _g(112, "EGT B1 [°C]", "enrichment factor B1 [%]", "EGT B2 [°C]", "factor B2 [%]"),
        _g(113, "RPM", "load", "throttle angle", "air pressure [mbar]"),
        _g(115, "RPM", "load", "boost pressure specified [mbar]", "boost pressure actual [mbar]"),
        _g(120, "RPM", "specified torque ASR [Nm]", "engine torque [Nm]", "status"),
        _g(122, "RPM", "specified torque transmission [Nm]", "engine torque [Nm]", "intervention"),
        _g(125, "Transmission", "ABS", "Instrument cluster", "A/C"),
        _g(126, "ADR", "LWS", "Airbag", "Electrical wiring"),
        _g(127, "All wheel", "Level", "Steering wheel", ""),
        _g(134, "oil temp", "ambient", "IAT", "engine-out temp"),
        _g(208, "", "", "intake cam offset [°]", "", verified=True, source="TTF-CHAIN / RT-P0087 (field 3)"),
        _g(209, "", "", "exhaust cam offset [°]", "", verified=True, source="TTF-CHAIN / RT-P0087 (field 3)"),
    ]},
    "edc17-cjaa": {g.group: g for g in [
        _g(2, "", "", "", "coolant temperature", source="RT-DPF"),
        _g(11, "engine speed [/min]", "boost pressure specified [mbar]", "boost pressure actual [mbar]",
           "N75 duty [%]", source="VTX-CJAA-011 (2011 CJAA log)"),
        _g(20, "rail pressure (specified/actual order unverified)", "rail pressure", "", "",
           verified=False, source="MTD-38651 owner post"),
        _g(46, "", "coolant temperature", "", "", source="VWTT-NOX"),
        _g(86, "ready bits (1 = ready)", "ready bits", "ready bits", "ready bits", source="VWTSB-RDY"),
        _g(89, "not-ready bits (1 = not ready)", "not-ready bits", "not-ready bits", "not-ready bits", source="VWTSB-RDY"),
        _g(99, "", "EGT before turbo", "EGT before DPF", "EGT after DPF", source="RT-DPF"),
        _g(100, "exhaust temperature (regen > 575 °C)", "temperature (> 300 °C EGR monitor)", "", "",
           source="VWTSB-RDY / VWTSB-DPF"),
        _g(108, "DPF oil ash volume", "soot mass calculated [g]", "soot mass measured [g]", "",
           source="RT-DPF / TDIC-334430"),
        _g(240, "fuel consumption since last regen", "mileage since last regen [km]",
           "time since last regen", "", source="VWTSB-DPF / TDIC-334430"),
        _g(241, "DPF oil ash volume [ml]", "soot load calculated [g]", "soot load measured [g]", "",
           source="VWTSB-DPF / RT-DPF"),
    ]},
    "dq250-02e": {g.group: g for g in [
        _g(1, "brake light switch", "brake test switch", "shift-lock status", "speed [km/h]", source="VAS-PC list"),
        _g(2, "selector lever position", "plausibility-checked position", "selector error byte", "engaged gear",
           source="VAS-PC list"),
        _g(6, "selector lever position", "valve current clutch valve 1 [A]", "safety valve 1 [%]",
           "main pressure valve current [A]", source="AUDIF-DSG VCDS log"),
        _g(13, "solenoid current clutch valve 1 [A]", "safety valve 1 [%]", "solenoid valve 1 (N88) [%]",
           "solenoid valve 2 (N89) [%]", source="AUDIF-DSG VCDS log"),
        _g(19, "control module temp (G510) [°C]", "clutch oil temp (G509) [°C]", "transmission fluid (G93) [°C]",
           "idle info", source="Ross-Tech staff / VAS-PC list"),
        _g(67, "clutch adaption K1 [A]", "clutch adaption K2 [A]", "", "", source="VAS-PC list (SW >= 0800)"),
        _g(125, "engine", "ABS", "dash panel", "selector lever", source="VAS-PC list"),
    ]},
    "haldex-gen2": {g.group: g for g in [
        _g(1, "supply voltage", "oil temperature", "pump status", "clutch status", verified=False,
           source="memory (R-G2); OpenHaldex only confirms the group exists"),
        _g(2, "wheel speeds", "", "", "", verified=False, source="memory (R-G2)"),
        _g(125, "CAN participants", "", "", "", verified=False, source="memory (R-G2)"),
    ]},
}


def group_label(family: str, group: int) -> Optional[GroupLabel]:
    """Label row for ``group`` in ``family`` (``None`` when unknown); an unverified
    row warns once when handed out."""
    row = GROUP_LABELS.get(family, {}).get(group)
    if row is not None and not row.verified:
        warn_unverified(f"group-label:{family}:{group}",
                        f"group {group:03d} field names for {family} come from {row.source}; "
                        "confirm against the VCDS label file on the car")
    return row


__all__ = [
    "Formula", "FORMULAS", "FORMULA_VARIANTS", "DISPUTED_IDS", "UNDECODABLE_IDS", "LAST_VALID_FORMULA",
    "formula", "decode_field", "decode_group", "decode_a0", "format_group", "MeasuringValue",
    "obd_mirror_did_decoder", "GroupLabel", "GROUP_LABELS", "group_label",
    "KIND_VALUE", "KIND_TEXT", "KIND_BITS", "KIND_TIME", "KIND_DATE", "KIND_TABLE_INDEX",
    "KIND_LENGTH_TEXT", "KIND_LENGTH_HEX", "KIND_REST_TEXT", "KIND_VARIABLE_UNITS", "KIND_UNDECODABLE",
]
