"""
VAG application layer over a :class:`~vagtune.kwp.client.KwpClient`: identification,
fault codes, measuring blocks, the read-only probes - for every KWP2000/TP 2.0
module of the 2008 R32 and the 2012 Golf TDI.

Verified facts used (``docs/PROTOCOL_FACTS.md`` §7.5 / §7.7 / §7.8 / §7.10):

* ``5A 9B`` record, byte-exact: 0..10 part number (ASCII, space padded), 11 = 0x20,
  12..15 software version, 16 coding type (00 none / 03 short / 10 long), 17 = 0x00,
  18..19 short coding big-endian, 20..25 WSC/importer/equipment block, 26.. component
  text; ``5A 91`` = length-prefixed records until 0xFF (the length counts itself);
  fallback 9B -> 91; unknown options answer ``7F 1A 11``.
* ``18 02 FF 00`` (fallback ``18 00 FF 00``) -> ``58 n`` + n x ``DTC_hi DTC_lo status``;
  the 16-bit value is the VCDS 5-digit number (SAE codes 0x4000..0x7FFF by the
  decimal rule); status low nibble = the VCDS 3-digit elaboration, bit 6 clear =
  "Intermittent" (21 real records); ``14 FF 00`` -> ``54 FF 00``.
* ``21 <group>`` -> ``61 <group>`` + fields walked by formula id
  (:mod:`vagtune.vag.measuring_blocks`).
* ``31 B8 00 00`` -> ``71 B8`` + 16-bit capability codes (read-only).
* ``23 addr(3) size`` -> ``63 data`` (read-only RAM probe).

REPORTED facts (each ``# UNVERIFIED:`` in code, warns once, never drives a write):

* the 48-bit WSC/importer/equipment packing of bytes 20..25 (high);
* the ``5A 9A`` long-coding record layout (medium);
* status bit 7 = MIL (low-medium) - shown as ``MIL?``; bits 4/5 semantics (low);
* elaboration texts 002/003/005/006/009/015 (medium);
* the read-only adaptation probe ``31 B8 01 03`` / ``31 B9 01 03 <ch>`` / ``31 BA 01
  03`` / ``32 B8 01 03`` and the layout of its ``71 BA`` reply (medium / low);
* the ``1A 9F`` gateway installation-list layout from vag-blocks (medium);
* ``18 03 FF 00`` supported-codes read (medium, display only).

The owner-level **writes** (login, coding, adaptation save, basic settings, output
tests) are not implemented: the methods raise ``NotImplementedError`` and point to
:mod:`vagtune.vag.kwp_recipes`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ..kwp import services as S
from ..kwp.client import KwpClient
from ..kwp.exceptions import KwpNegativeResponse, UnexpectedKwpResponse
from . import dtc as vagdtc
from .dtc import warn_unverified
from .kwp_recipes import not_implemented
from .measuring_blocks import MeasuringValue, decode_group

log = logging.getLogger(__name__)


# ================================================================= identification

def unpack_wsc_block(block: bytes) -> Tuple[int, int, int]:
    """Bytes 20..25 of ``5A 9B`` -> ``(wsc, importer, equipment)``.

    UNVERIFIED (registry 7.5 REPORTED, high): ``v`` = 48-bit big-endian; ``wsc = v &
    0x1FFFF``, ``importer = (v >> 17) & 0x3FF``, ``equipment = v >> 27``. Reproduces
    the four samples (blafusel ``00 00 00 00 19 23`` -> 06435/000/00000, NefMoto
    ``00 06 46 22 04 F5`` -> 01269/785/00200, VDS -> 00191/264/15243, bri3d ->
    04148/552/00000) and Basano's decoder output, but no fetched source pairs the
    bytes with a VCDS "Shop #" line. Warns once.
    """
    # UNVERIFIED: WSC/importer/equipment packing (registry 7.5 Reported, high).
    if len(block) != 6:
        raise ValueError("the WSC block is 6 bytes")
    warn_unverified("wsc-packing",
                    "WSC/importer/equipment 48-bit packing (v & 0x1FFFF / v>>17 & 0x3FF / v>>27) is REPORTED "
                    "(high); compare 5A 9B bytes 20..25 with a VCDS 'Shop #' line to confirm")
    v = int.from_bytes(block, "big")
    return v & 0x1FFFF, (v >> 17) & 0x3FF, v >> 27


def parse_length_prefixed_records(payload: bytes) -> List[bytes]:
    """``5A 91`` / ``5A 9F`` body: ``len data... len data... FF`` where ``len`` counts
    itself (vag-blocks ``shortIdHandler``, PyVCDS, VDS sample ``0E "8P0907115B" 20 20
    20 FF``). Stops at 0xFF or at the end; a length that overruns the payload yields
    the truncated record."""
    out: List[bytes] = []
    i = 0
    while i < len(payload):
        length = payload[i]
        if length == 0xFF:
            break
        if length == 0:
            raise UnexpectedKwpResponse(f"zero-length record at offset {i} in {payload.hex(' ')}")
        out.append(bytes(payload[i + 1:i + length]))
        i += length
    return out


@dataclass
class LongCodingRecord:
    """``5A 9A`` body as REPORTED (one sniffed sample): ``[wsc6] [sw version 4 ASCII]
    [10] [len counting itself] [coding bytes] [FF]``."""
    raw: bytes
    wsc_block: bytes = b""
    software_version: str = ""
    coding_type: Optional[int] = None
    coding: bytes = b""
    parsed: bool = False
    unverified: bool = True


def parse_ident_9a(payload: bytes) -> LongCodingRecord:
    """Best-effort parse of the ``5A 9A`` body (layout UNVERIFIED, medium; warns once).
    The raw bytes are always kept."""
    # UNVERIFIED: 5A 9A long-coding record layout (registry 7.5 Reported, medium).
    warn_unverified("ident-9a-layout",
                    "1A 9A long-coding record parsed with the single-sample layout [wsc6][sw4][10][len][coding][FF] "
                    "(medium); confirm on the R32 engine / gateway against the VCDS coding value")
    rec = LongCodingRecord(bytes(payload))
    if len(payload) < 12:
        return rec
    rec.wsc_block = bytes(payload[0:6])
    rec.software_version = payload[6:10].decode("latin-1", errors="replace")
    rec.coding_type = payload[10]
    length = payload[11]
    if length >= 1 and 11 + length <= len(payload):
        rec.coding = bytes(payload[12:11 + length])
        rec.parsed = rec.coding_type == S.CODING_TYPE_LONG and rec.software_version.isdigit()
    return rec


@dataclass
class KwpIdentity:
    """What ``1A 9B`` (or the ``1A 91`` fallback) says about a module.

    Byte-exact fields are verified; ``wsc`` / ``importer`` / ``equipment`` come from
    the REPORTED 48-bit packing (``unverified_fields`` names them); ``long_coding``
    is filled only when the caller asked for ``1A 9A``. ``source`` is ``"9B"`` for a
    record of the verified layout, ``"9B-short"`` for a ``5A 9B`` body too short for
    it (kept as text, ``layout_ok=False``) and ``"91"`` when the identity comes from
    the ``1A 91`` fallback only.
    """
    part_number: str
    software_version: str
    coding_type: Optional[int]
    short_coding: Optional[int]
    wsc_block: bytes
    component: str
    raw_9b: bytes = b""
    raw_91_records: List[bytes] = field(default_factory=list)
    hardware_number: Optional[str] = None
    source: str = "9B"
    wsc: Optional[int] = None
    importer: Optional[int] = None
    equipment: Optional[int] = None
    long_coding: Optional[LongCodingRecord] = None
    unverified_fields: List[str] = field(default_factory=list)
    layout_ok: bool = True

    @property
    def coding_type_name(self) -> str:
        if self.coding_type is None:
            return "unknown"
        return S.CODING_TYPE_NAMES.get(self.coding_type, f"coding type 0x{self.coding_type:02X} (unknown)")

    @property
    def coding(self) -> Optional[bytes]:
        """The coding bytes: 2-byte short coding, the long coding when read, else None."""
        if self.coding_type == S.CODING_TYPE_SHORT and self.short_coding is not None:
            return self.short_coding.to_bytes(2, "big")
        if self.long_coding is not None and self.long_coding.coding:
            return self.long_coding.coding
        return None

    @property
    def coding_text(self) -> str:
        """VCDS style: ``0000178`` for short coding, hex for long coding."""
        if self.coding_type == S.CODING_TYPE_SHORT and self.short_coding is not None:
            return f"{self.short_coding:07d}"
        if self.long_coding is not None and self.long_coding.coding:
            return self.long_coding.coding.hex().upper()
        if self.coding_type == S.CODING_TYPE_LONG:
            return "(long coding: read with 1A 9A)"
        return "-"

    @property
    def component_line(self) -> str:
        """``R32-DQ-LEV2 G 1098`` - component text plus software version, as VCDS prints
        the "Component:" line."""
        return f"{self.component} {self.software_version}".strip()

    @property
    def shop_line(self) -> str:
        if self.wsc is None:
            return "WSC ????? ??? ?????"
        return f"WSC {self.wsc:05d} {self.importer:03d} {self.equipment:05d}"

    def identity_key(self) -> Dict[str, str]:
        """What a backup must match before any write: part number + software version."""
        return {"part_number": self.part_number, "software_version": self.software_version}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "part_number": self.part_number,
            "software_version": self.software_version,
            "component": self.component,
            "coding_type": self.coding_type,
            "coding_type_name": self.coding_type_name,
            "short_coding": self.short_coding,
            "coding": self.coding_text,
            "wsc_block": self.wsc_block.hex(),
            "wsc": self.wsc, "importer": self.importer, "equipment": self.equipment,
            "hardware_number": self.hardware_number,
            "source": self.source,
            "raw_9b": self.raw_9b.hex(),
            "raw_91": [r.hex() for r in self.raw_91_records],
            "long_coding": self.long_coding.raw.hex() if self.long_coding else None,
            "unverified_fields": list(self.unverified_fields),
        }

    def pretty(self) -> str:
        lines = [
            f"  Part No: {self.part_number}",
            f"  Component: {self.component_line}",
            f"  Coding: {self.coding_text} ({self.coding_type_name})",
            f"  Shop #: {self.shop_line}" + ("  [packing UNVERIFIED]" if self.wsc is not None else ""),
        ]
        if self.hardware_number:
            lines.append(f"  VAG Number (1A 91): {self.hardware_number}")
        if self.source == "91":
            lines.append("  (1A 9B refused or unusable; identity from the 1A 91 fallback)")
        elif self.source == "9B-short":
            lines.append("  (1A 9B record shorter than the verified layout; read as text, raw kept)")
        return "\n".join(lines)


def _short_record_identity(raw: bytes) -> KwpIdentity:
    """A ``5A 9B`` body shorter than the 16-byte prefix of the verified layout.

    Reported (registry 7.5, medium): a PQ35 ABS emulator answers ``1A 9B`` with
    just its part-number string ``1K0907379 0143`` (14 bytes). Such a record is
    read as whitespace-separated ASCII: the first token is the part number, a
    second token of four digits the software version; everything else stays in
    ``raw_9b``. ``layout_ok`` is False and ``source`` is ``"9B-short"``.
    """
    text = raw.decode("latin-1", errors="replace")
    tokens = text.split()
    part = tokens[0] if tokens else text.strip() or raw.hex()
    sw = tokens[1] if len(tokens) > 1 and len(tokens[1]) == 4 and tokens[1].isdigit() else ""
    log.info("5A 9B record is shorter than the verified layout (%d bytes): %s - kept as text %r",
             len(raw), raw.hex(" "), text)
    return KwpIdentity(part, sw, None, None, b"", "", raw_9b=raw, source="9B-short", layout_ok=False)


def parse_ident_9b(payload: bytes, *, decode_wsc: bool = True) -> KwpIdentity:
    """Byte-exact ``5A 9B`` body (offsets from the first byte after ``5A 9B``).

    Three real dumps fit this layout exactly (blafusel ME7, NefMoto 1K0907115L, VDS
    8P0907115AQ). A record shorter than 26 bytes still yields what it has
    (``layout_ok=False``); one shorter than the 16-byte part-number/version prefix
    is kept as ASCII text (``source="9B-short"``, see :func:`_short_record_identity`)
    rather than refused, because the registry's rule is to keep the raw bytes and
    flag the deviation; only an empty record raises :class:`UnexpectedKwpResponse`.
    The constant bytes at 11 and 17 are checked and logged, not enforced (the ESP32
    converter's own record follows them too).
    """
    raw = bytes(payload)
    if not raw:
        raise UnexpectedKwpResponse("5A 9B record is empty")
    if len(raw) < 16:
        return _short_record_identity(raw)
    part = raw[0:11].decode("latin-1", errors="replace").rstrip()
    sw = raw[12:16].decode("latin-1", errors="replace")
    layout_ok = raw[11] == 0x20 and len(raw) >= 26
    coding_type = raw[16] if len(raw) > 16 else None
    if len(raw) > 17 and raw[17] != 0x00:
        layout_ok = False
    short_coding = int.from_bytes(raw[18:20], "big") if len(raw) >= 20 else None
    wsc_block = bytes(raw[20:26]) if len(raw) >= 26 else b""
    component = raw[26:].decode("latin-1", errors="replace").rstrip() if len(raw) > 26 else ""
    if not layout_ok:
        log.debug("5A 9B record deviates from the verified layout: %s", raw.hex(" "))
    ident = KwpIdentity(part, sw, coding_type, short_coding, wsc_block, component, raw_9b=raw,
                        layout_ok=layout_ok)
    if coding_type == S.CODING_TYPE_NONE:
        ident.short_coding = None
    if decode_wsc and len(wsc_block) == 6:
        ident.wsc, ident.importer, ident.equipment = unpack_wsc_block(wsc_block)
        ident.unverified_fields += ["wsc", "importer", "equipment"]
    return ident


# ================================================================= fault codes

#: VCDS text for the low nibble of a KWP2000 status byte ("- NNN -" after the P-code).
#: Verified pairs come from four real Auto-Scans (21 KWP records); the rest are
#: REPORTED (medium) and warn once when used.
@dataclass(frozen=True)
class Elaboration:
    code: int
    text: str
    verified: bool


KWP2000_ELABORATION: Dict[int, Elaboration] = {
    0: Elaboration(0, "-", True),
    1: Elaboration(1, "Upper Limit Exceeded", True),
    2: Elaboration(2, "Lower Limit Exceeded", False),
    3: Elaboration(3, "Mechanical Malfunction", False),
    4: Elaboration(4, "No Signal/Communication", True),
    5: Elaboration(5, "No or Incorrect Basic Setting / Adaptation", False),
    6: Elaboration(6, "Short to Plus", False),
    7: Elaboration(7, "Short to Ground", True),
    8: Elaboration(8, "Implausible Signal", True),
    9: Elaboration(9, "Open or Short to Ground", False),
    10: Elaboration(10, "Open or Short to Plus", True),
    11: Elaboration(11, "Open Circuit", True),
    12: Elaboration(12, "Electrical Fault in Circuit", True),
    13: Elaboration(13, "Check DTC Memory", True),
    14: Elaboration(14, "Defective", True),
    15: Elaboration(15, "Unknown Switch Condition", False),
}

#: DV's KWP1281-elaboration (83-row table index) -> KWP2000 nibble map, inverted:
#: which 83-row rows collapse onto each nibble (informational only).
_DV_KWP1281_TO_NIBBLE: Dict[int, int] = {
    0x00: 0, 0x01: 6, 0x02: 7, 0x03: 4, 0x04: 3, 0x05: 0xB, 0x06: 1, 0x07: 2, 0x08: 1, 0x09: 1, 0x0A: 2,
    0x0B: 2, 0x0C: 1, 0x0D: 2, 0x0E: 1, 0x0F: 2, 0x10: 8, 0x11: 8, 0x12: 1, 0x13: 2, 0x14: 5,
    0x15: 0xE, 0x16: 0xE, 0x17: 0xE, 0x18: 0xE, 0x19: 8, 0x1A: 0xB, 0x1B: 8, 0x1C: 6, 0x1D: 7, 0x1E: 0xA,
    0x1F: 9, 0x20: 1, 0x21: 2, 0x22: 0, 0x23: 0, 0x24: 0xB, 0x25: 0xE, 0x26: 6, 0x27: 7, 0x28: 0xC,
    0x29: 4, 0x2A: 1, 0x2B: 0xE, 0x2C: 0xC, 0x2D: 3, 0x2E: 0xE, 0x2F: 4, 0x30: 8, 0x31: 4, 0x32: 3,
    0x33: 3, 0x34: 1, 0x35: 2, 0x36: 5, 0x37: 5, 0x38: 0xE, 0x39: 0xC, 0x3A: 3, 0x3B: 3, 0x3C: 0xE,
    0x3D: 0xE, 0x3E: 5, 0x3F: 1, 0x40: 0xF, 0x41: 0xF, 0x42: 0xF, 0x43: 3, 0x44: 0xE, 0x45: 0xE,
    0x46: 0xE, 0x47: 0xE, 0x48: 0xE, 0x49: 0xE, 0x4A: 0xE, 0x4B: 0xE, 0x4C: 0xC, 0x4D: 0xC, 0x4E: 4,
    0x4F: 0xD, 0x50: 0xC, 0x51: 0xB, 0x52: 0xB,
}


def kwp1281_rows_for_nibble(nibble: int) -> List[str]:
    """The KWP1281 83-row elaboration texts DV's converter maps onto ``nibble``."""
    return [vagdtc.KWP_ELABORATION[k] for k, v in _DV_KWP1281_TO_NIBBLE.items() if v == (nibble & 0xF)]


def describe_elaboration(status: int) -> Elaboration:
    row = KWP2000_ELABORATION[status & S.DTC_STATUS_ELABORATION_MASK]
    if not row.verified:
        warn_unverified(f"kwp-elaboration-nibble:{row.code}",
                        f"KWP2000 status elaboration {row.code:03d} = {row.text!r} is REPORTED (medium); "
                        "confirm with an Auto-Scan that prints it")
    return row


@dataclass
class KwpFault:
    """A KWP2000 fault as VCDS prints it (VagDtc-like).

    ``number`` is the raw 16-bit value = the VCDS 5-digit number; ``sae_code`` is set
    for 0x4000..0x7FFF (decimal rule), empty for factory-only numbers; ``status`` is
    the third byte: low nibble -> ``elaboration``, bit 6 clear -> ``intermittent``,
    bit 7 -> ``mil`` (REPORTED, shown as ``MIL?``).
    """
    number: int
    status: int
    sae_code: str
    description: str
    elaboration: int
    elaboration_text: str
    elaboration_verified: bool
    intermittent: bool
    mil: bool
    raw: bytes
    vag_wording: Optional[str] = None
    unverified_fields: List[str] = field(default_factory=list)

    @property
    def vag5(self) -> str:
        return f"{self.number:05d}"

    @property
    def factory_number(self) -> str:
        return self.vag5

    @property
    def vag6(self) -> Optional[str]:
        return f"{vagdtc.vag6_from_code(self.sae_code):06d}" if self.sae_code else None

    @property
    def is_factory_only(self) -> bool:
        return not self.sae_code

    @property
    def active(self) -> bool:
        return not self.intermittent

    @property
    def stored_bit(self) -> bool:
        return bool(self.status & S.DTC_STATUS_BIT5_STORED)

    @property
    def text(self) -> str:
        return self.vag_wording or self.description

    @property
    def status_text(self) -> str:
        parts = [f"{self.elaboration:03d} - {self.elaboration_text}"]
        if self.intermittent:
            parts.append("Intermittent")
        if self.mil:
            parts.append("MIL?")
        return " - ".join(parts)

    @property
    def status_bits(self) -> str:
        return format(self.status, "08b")

    def vcds_lines(self) -> List[str]:
        """Two lines like VCDS: ``16485 - Mass Air Flow Sensor (G70): Implausible Signal``
        and ``P0101 - 008 - Implausible Signal - Intermittent``."""
        first = f"{self.vag5} - {self.text}"
        tail = f"{self.elaboration:03d} - {self.elaboration_text}"
        if self.intermittent:
            tail += " - Intermittent"
        if self.mil:
            tail += " - MIL? (bit 7, unverified)"
        second = f"{self.sae_code} - {tail}" if self.sae_code else f"{tail}"
        return [first, second, f"Fault Status: {self.status_bits}"]

    def __str__(self) -> str:
        return " / ".join(self.vcds_lines()[:2])


def decode_kwp_fault(number: int, status: int) -> KwpFault:
    """2-byte KWP fault number + status byte -> :class:`KwpFault` (verified rules;
    REPORTED pieces flagged in ``unverified_fields`` and warned once)."""
    raw = number.to_bytes(2, "big") + bytes([status & 0xFF])
    elab = describe_elaboration(status)
    code = vagdtc.code_from_vag5(number) or ""
    unverified: List[str] = []
    if not elab.verified:
        unverified.append("elaboration_text")
    mil = bool(status & S.DTC_STATUS_BIT7_MIL)
    if mil:
        # UNVERIFIED: bit 7 = MIL on KWP2000 modules (registry 7.8 Reported, low-medium).
        warn_unverified("kwp-status-bit7-mil",
                        "KWP2000 fault status bit 7 interpreted as 'MIL on' (bri3d isCEL; never seen on a "
                        "KWP2000 record) - shown as 'MIL?'")
        unverified.append("mil")
    if code:
        info = vagdtc.lookup(code)
        description = vagdtc.describe_dtc(code)
        wording = info.vag_wording
    else:
        wording = vagdtc.lookup_factory(number)
        description = wording or f"factory fault code {number:05d} (no description on file)"
    return KwpFault(number, status & 0xFF, code, description, elab.code, elab.text, elab.verified,
                    not (status & S.DTC_STATUS_BIT6_PRESENT), mil, raw, vag_wording=wording,
                    unverified_fields=unverified)


# ================================================================= probes

@dataclass
class CapabilityList:
    """``71 B8`` + 16-bit codes (verified read-only query)."""
    raw: bytes
    codes: List[int]

    @property
    def names(self) -> List[str]:
        return [S.capability_name(c) for c in self.codes]

    def supports(self, code: int) -> bool:
        return code in self.codes

    def __str__(self) -> str:
        return ", ".join(f"{c:04X} {S.capability_name(c)}" for c in self.codes) or "(none)"


@dataclass
class AdaptationProbe:
    """Raw replies of the read-only adaptation probe plus a best-effort decode."""
    channel: int
    replies: Dict[str, bytes]
    value: Optional[int] = None
    echoed_channel: Optional[int] = None
    decoded: bool = False
    unverified: bool = True

    def __str__(self) -> str:
        val = f"value {self.value}" if self.value is not None else "value undecoded"
        return f"adaptation channel {self.channel:03d}: {val} [UNVERIFIED probe]; raw 71 BA: " \
               f"{self.replies.get('read', b'').hex(' ') or '-'}"


@dataclass
class GatewayEntry:
    """One 4-byte entry of the ``5A 9F`` list per vag-blocks: ``[moduleNumber,
    tp20Address, ?, flags]``; ``flags & 1`` = present, ``(flags & 0x1E) >> 1`` = status."""
    module_number: int
    tp20_address: int
    byte2: int
    flags: int

    @property
    def present(self) -> bool:
        return bool(self.flags & 0x01)

    @property
    def status(self) -> int:
        return (self.flags & 0x1E) >> 1

    def __str__(self) -> str:
        return (f"module {self.module_number:02X} at TP2.0 0x{self.tp20_address:02X} "
                f"flags {self.flags:02X} (present={self.present}, status={self.status})")


@dataclass
class GatewayInstallationList:
    raw: bytes
    records: List[bytes]
    entries: List[GatewayEntry]
    unverified: bool = True

    @property
    def usable(self) -> List[GatewayEntry]:
        """vag-blocks' filter: flags != 0 and address != 0x13 (phantom entries)."""
        return [e for e in self.entries if e.flags and e.tp20_address != 0x13]


def parse_installation_list(payload: bytes) -> GatewayInstallationList:
    """``5A 9F`` body per vag-blocks (UNVERIFIED layout, medium; warns once): two
    length-prefixed records; record 0 = 4-byte entries. The raw bytes are always kept;
    a malformed body yields an empty entry list, never an exception."""
    # UNVERIFIED: 1A 9F installation-list layout (registry 7.4 Reported, medium).
    warn_unverified("gateway-1a9f-layout",
                    "1A 9F gateway installation list parsed with vag-blocks' layout (two length-prefixed "
                    "records, 4-byte entries [module, tp20 address, ?, flags]) - medium; dump the raw reply")
    raw = bytes(payload)
    try:
        records = parse_length_prefixed_records(raw)
    except UnexpectedKwpResponse:
        records = []
    entries: List[GatewayEntry] = []
    if records:
        rec = records[0]
        for i in range(0, len(rec) - 3, 4):
            entries.append(GatewayEntry(rec[i], rec[i + 1], rec[i + 2], rec[i + 3]))
        if len(records) != 2:
            log.debug("1A 9F reply carries %d records (vag-blocks expects 2)", len(records))
    return GatewayInstallationList(raw, records, entries)


# ================================================================= session

class VagKwpSession:
    """VAG workflows over one KWP2000 client (one module).

    Everything here is read-only except :meth:`clear_dtcs`. The DESIGN-named write
    functions raise ``NotImplementedError`` (see :mod:`vagtune.vag.kwp_recipes`).
    """

    def __init__(self, client: KwpClient, *, module_name: str = "") -> None:
        self.client = client
        self.module_name = module_name
        self.identity: Optional[KwpIdentity] = None

    # -- session ---------------------------------------------------------------

    def open(self) -> None:
        """``10 89`` (repeatable). Measuring blocks usually work without it, but every
        fetched tool sends it first."""
        self.client.start_diagnostic_session(S.SESSION_STANDARD_DIAGNOSTIC)

    def close(self) -> None:
        self.client.close()

    # -- identification --------------------------------------------------------

    def read_identification(self, *, with_long_coding: bool = False,
                            with_hardware_number: bool = False) -> KwpIdentity:
        """``1A 9B`` parsed byte-exact; on a negative response *or* an unusable
        ``5A 9B`` body fall back to ``1A 91`` (PyVCDS / vag-blocks / scirocco-dash
        behaviour). A ``5A 9B`` body shorter than the verified layout (the PQ35 ABS
        emulator's bare ``1K0907379 0143``) is kept as text (``source="9B-short"``)
        and ``1A 91`` is read as well to fill ``hardware_number``; the module is only
        reported unidentifiable when both ``9B`` and ``91`` fail. ``with_long_coding``
        adds ``1A 9A`` for type-10 modules (layout UNVERIFIED); ``with_hardware_number``
        adds ``1A 91`` next to a good ``9B``."""
        raw_9b = b""
        ident: Optional[KwpIdentity] = None
        try:
            raw_9b = self.client.read_ecu_identification(S.IDENT_STANDARD)
            ident = parse_ident_9b(raw_9b)
        except KwpNegativeResponse as exc:
            log.info("1A 9B refused (%s); falling back to 1A 91", exc.nrc_name)
        except UnexpectedKwpResponse as exc:
            log.info("1A 9B answered an unusable record (%s; raw %s); falling back to 1A 91",
                     exc, raw_9b.hex(" ") or "-")
        if ident is None:
            ident = self._identity_from_91(raw_9b)
            with_hardware_number = False
        elif ident.source == "9B-short":
            with_hardware_number = True
        if with_hardware_number:
            try:
                records = parse_length_prefixed_records(
                    self.client.read_ecu_identification(S.IDENT_HARDWARE_NUMBER))
                ident.raw_91_records = records
                if records:
                    ident.hardware_number = records[0].decode("latin-1", errors="replace").rstrip()
            except (KwpNegativeResponse, UnexpectedKwpResponse) as exc:
                log.debug("1A 91 refused or unusable: %s", exc)
        if with_long_coding and ident.coding_type == S.CODING_TYPE_LONG:
            try:
                ident.long_coding = parse_ident_9a(self.client.read_ecu_identification(S.IDENT_LONG_CODING))
                ident.unverified_fields.append("long_coding")
            except KwpNegativeResponse as exc:
                log.info("1A 9A refused: %s", exc.nrc_name)
        self.identity = ident
        return ident

    def _identity_from_91(self, raw_9b: bytes) -> KwpIdentity:
        """The ``1A 91`` fallback identity (``source="91"``); raises
        :class:`UnexpectedKwpResponse` naming both failures when ``91`` yields no
        record either (a refusal propagates as :class:`KwpNegativeResponse`)."""
        records = parse_length_prefixed_records(self.client.read_ecu_identification(S.IDENT_HARDWARE_NUMBER))
        if not records:
            raise UnexpectedKwpResponse(
                f"1A 91 returned no records and 1A 9B was unusable (raw 9B: {raw_9b.hex(' ') or 'refused'})")
        part = records[0].decode("latin-1", errors="replace").rstrip()
        return KwpIdentity(part, "", None, None, b"", "", raw_9b=raw_9b, raw_91_records=records,
                           hardware_number=part, source="91", layout_ok=False)

    def read_ident_option(self, option: int) -> bytes:
        """Raw ``1A <option>`` body for the options nobody decodes (86/90/92/94/9C...)."""
        return self.client.read_ecu_identification(option)

    def read_coding(self) -> Dict[str, Any]:
        """Read-only coding view: short coding from ``5A 9B`` (verified) and the
        ``1A 9A`` record for long-coded modules (layout UNVERIFIED)."""
        ident = self.read_identification(with_long_coding=True)
        return {
            "coding_type": ident.coding_type_name,
            "short_coding": ident.short_coding,
            "coding": ident.coding_text,
            "long_coding_raw": ident.long_coding.raw.hex() if ident.long_coding else None,
            "long_coding_parsed": bool(ident.long_coding and ident.long_coding.parsed),
            "wsc": ident.shop_line,
        }

    # -- fault codes -----------------------------------------------------------

    def read_dtcs(self) -> List[KwpFault]:
        """``18 02 FF 00`` (fallback ``18 00 FF 00``) decoded VCDS-style."""
        return [decode_kwp_fault(n, s) for n, s in self.client.read_dtc_by_status()]

    def read_dtcs_raw(self) -> List[Tuple[int, int]]:
        return self.client.read_dtc_by_status()

    def read_supported_dtcs(self) -> List[Tuple[int, int]]:
        """``18 03 FF 00`` "supported codes" (VCDS function 18). UNVERIFIED (medium):
        DV defines the status value; the reply layout is assumed identical to ``58``.
        Display only."""
        # UNVERIFIED: 18 03 FF 00 supported-codes read (registry 7.8 Reported, medium).
        warn_unverified("kwp-18-03-supported",
                        "18 03 FF 00 'supported codes' read is REPORTED (medium); reply assumed in the 58 layout")
        return self.client.read_dtc_by_status(S.DTC_GROUP_ALL, S.DTC_STATUS_SUPPORTED, fallback=False)

    def clear_dtcs(self) -> None:
        """``14 FF 00`` -> ``54 FF 00``. Also discards freeze frames and readiness."""
        self.client.clear_diagnostic_information(S.CLEAR_GROUP_ALL)

    # -- measuring blocks ------------------------------------------------------

    def read_group_raw(self, group: int) -> bytes:
        return self.client.read_data_by_local_id(group)

    def read_group(self, group: int, *, variants: Optional[Dict[int, str]] = None,
                   second_half_is_group_plus_128: bool = False) -> List[MeasuringValue]:
        """``21 <group>`` decoded by formula id. ``7F 21 11/31`` (no such group)
        propagates as :class:`KwpNegativeResponse`."""
        return decode_group(self.read_group_raw(group), group=group, variants=variants,
                            second_half_is_group_plus_128=second_half_is_group_plus_128)

    def read_groups(self, groups: Iterable[int], *, skip_refused: bool = True,
                    **decode_kw) -> Dict[int, List[MeasuringValue]]:
        """Several groups; a refused group is skipped (logged) unless ``skip_refused``
        is False."""
        out: Dict[int, List[MeasuringValue]] = {}
        for g in groups:
            try:
                out[g] = self.read_group(g, **decode_kw)
            except KwpNegativeResponse as exc:
                if not skip_refused or not exc.is_not_supported:
                    raise
                log.info("group %03d refused: %s", g, exc.nrc_name)
        return out

    def scan_groups(self, groups: Iterable[int] = range(0, 256)) -> List[int]:
        """Which groups answer ``61`` (walks ``21 g``; returns the group numbers)."""
        found: List[int] = []
        for g in groups:
            try:
                self.read_group_raw(g)
                found.append(g)
            except KwpNegativeResponse as exc:
                if not exc.is_not_supported:
                    raise
        return found

    # -- memory ----------------------------------------------------------------

    def read_ram(self, address: int, length: int, *, addr_bytes: int = 3, chunk: int = 254) -> bytes:
        """Read-only ``23`` probe in chunks of at most 254 bytes (me7-logger limit).
        On ME7 a development session may be required (``7F 23 xx`` then)."""
        if length <= 0:
            raise ValueError("length must be positive")
        if not 1 <= chunk <= 254:
            raise ValueError("chunk must be 1..254")
        out = bytearray()
        pos = address
        while len(out) < length:
            n = min(chunk, length - len(out))
            out += self.client.read_memory_by_address(pos, n, addr_bytes=addr_bytes)
            pos += n
        return bytes(out)

    # -- routines (read-only) --------------------------------------------------

    def capability_query(self) -> CapabilityList:
        """``31 B8 00 00`` -> ``71 B8`` + 01xx pairs (verified on a real PQ35 engine)."""
        body = self.client.start_routine_by_local_id(S.ROUTINE_FUNCTION_START,
                                                     S.CAPABILITY_QUERY_FUNCTION.to_bytes(2, "big"))
        codes = [(body[i] << 8) | body[i + 1] for i in range(0, len(body) - 1, 2)]
        if len(body) % 2:
            log.debug("71 B8 capability reply has an odd trailing byte: %s", body.hex(" "))
        raw = bytes([S.positive_sid(S.Service.START_ROUTINE_BY_LOCAL_ID), S.ROUTINE_FUNCTION_START]) + body
        return CapabilityList(raw, codes)

    def read_adaptation_probe(self, channel: int, *, send_stop: bool = True) -> AdaptationProbe:
        """Read-only adaptation probe: ``31 B8 01 03`` / ``31 B9 01 03 <ch>`` /
        ``31 BA 01 03`` / ``32 B8 01 03``. Never sends ``31 BB`` (save).

        UNVERIFIED (registry 7.10 Reported): the 01xx function model is medium for
        adaptation (bri3d's one real sequence), the ``71 BA`` reply layout is low
        (assumed ``<channel> <value16>``). Warns once; returns every raw reply.
        """
        # UNVERIFIED: 31 B8/B9/BA 01 03 adaptation model + 71 BA layout (registry 7.10 Reported).
        if not 0 <= channel <= 255:
            raise ValueError("adaptation channel is 0..255")
        warn_unverified("kwp-adaptation-probe",
                        "adaptation read probe 31 B8 01 03 / 31 B9 01 03 <ch> / 31 BA 01 03 / 32 B8 01 03 follows "
                        "bri3d's sequence (medium); the 71 BA value layout is a guess (low) - confirm on the car")
        replies: Dict[str, bytes] = {}
        func = bytes([0x01, 0x03])
        replies["start"] = self.client.start_routine_by_local_id(S.ROUTINE_FUNCTION_START, func)
        try:
            replies["select"] = self.client.start_routine_by_local_id(S.ROUTINE_FUNCTION_SELECT, func + bytes([channel]))
            replies["read"] = self.client.start_routine_by_local_id(S.ROUTINE_FUNCTION_READ, func)
        finally:
            if send_stop:
                try:
                    replies["stop"] = self.client.stop_routine_by_local_id(S.ROUTINE_FUNCTION_START, func)
                except KwpNegativeResponse as exc:
                    log.info("32 B8 01 03 refused: %s", exc.nrc_name)
        probe = AdaptationProbe(channel, replies)
        body = replies.get("read", b"")
        # best effort: strip an echoed "01 03", then expect <channel> <value hi> <value lo>
        if body[:2] == func:
            body = body[2:]
        if len(body) >= 3 and body[0] == channel:
            probe.echoed_channel = body[0]
            probe.value = int.from_bytes(body[1:3], "big")
            probe.decoded = True
        elif len(body) == 2:
            probe.value = int.from_bytes(body, "big")
            probe.decoded = True
        return probe

    def read_adaptation(self, channel: int) -> AdaptationProbe:
        """Alias of :meth:`read_adaptation_probe` (DESIGN name)."""
        return self.read_adaptation_probe(channel)

    def gateway_installation_list(self) -> GatewayInstallationList:
        """``1A 9F`` on the gateway channel (vag-blocks sends it right after opening
        the channel to module 0x1F). Layout UNVERIFIED; the raw reply is always in
        the result."""
        body = self.client.read_ecu_identification(S.IDENT_INSTALLATION_LIST)
        return parse_installation_list(body)

    # -- writes: deliberately not implemented ----------------------------------

    def login(self, code: int, **_: Any) -> None:
        """Not implemented: see :mod:`vagtune.vag.kwp_recipes` (``login``)."""
        raise not_implemented("login")

    def write_coding(self, *_: Any, **__: Any) -> None:
        """Not implemented: see :mod:`vagtune.vag.kwp_recipes` (``coding-write-*``)."""
        raise not_implemented("write_coding")

    def write_adaptation(self, *_: Any, **__: Any) -> None:
        """Not implemented: see :mod:`vagtune.vag.kwp_recipes` (``adaptation-save``)."""
        raise not_implemented("write_adaptation")

    def basic_settings(self, *_: Any, **__: Any) -> None:
        """Not implemented: see :mod:`vagtune.vag.kwp_recipes` (``basic-settings-*``)."""
        raise not_implemented("basic_settings")

    def output_test(self, *_: Any, **__: Any) -> None:
        """Not implemented: see :mod:`vagtune.vag.kwp_recipes` (``output-test-*``)."""
        raise not_implemented("output_test")

    # -- convenience -----------------------------------------------------------

    def full_report(self, groups: Sequence[int] = ()) -> str:
        ident = self.read_identification()
        lines = [f"Module {self.module_name or '?'} (KWP2000)", ident.pretty(), "", "Fault codes:"]
        try:
            faults = self.read_dtcs()
            if faults:
                for f in faults:
                    lines += [f"  {line}" for line in f.vcds_lines()]
            else:
                lines.append("  No fault code found.")
        except KwpNegativeResponse as exc:
            lines.append(f"  (could not read DTCs: {exc})")
        for g in groups:
            try:
                lines.append(f"Group {g:03d}:")
                lines += [f"  {v}" for v in self.read_group(g)]
            except KwpNegativeResponse as exc:
                lines.append(f"  (refused: {exc.nrc_name})")
        return "\n".join(lines)


__all__ = [
    "KwpIdentity", "LongCodingRecord", "parse_ident_9b", "parse_ident_9a", "parse_length_prefixed_records",
    "unpack_wsc_block", "KwpFault", "decode_kwp_fault", "Elaboration", "KWP2000_ELABORATION",
    "describe_elaboration", "kwp1281_rows_for_nibble", "CapabilityList", "AdaptationProbe",
    "GatewayEntry", "GatewayInstallationList", "parse_installation_list", "VagKwpSession",
]
