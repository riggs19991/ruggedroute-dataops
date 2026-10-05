#!/usr/bin/env python3
"""
Build ``vagtune/data/dtc_db.json`` from the research database.

Usage::

    python tools/build_dtc_db.py <research dtc_db.json> [<output path>]

The research file (assembled by the research build script from python-OBD, the
Wal33D generic database, the Bentley VW DTC table, Ross-Tech Wiki page headings,
vag-hub and a few verified forum/vendor pages) carries eight top-level keys. The
shipped file keeps what the runtime looks up and drops what is derivable or only
provenance:

* keep ``codes`` (code -> SAE/generic wording), ``vag_wording`` (code -> VW/VCDS
  wording), ``vag_5digit_only`` (factory 5-digit number -> text, KWP modules),
  ``vag_fault_variants`` (code -> fault-type suffixes seen on Ross-Tech),
* drop ``provenance`` (per-code source tag; the stats summary is enough) and
  ``vag_legacy`` (5-digit -> P-code; it is a pure formula, see ``vag/dtc.py``),
* fix python-OBD's ``lntake`` (lowercase L) typo,
* drop the 42 placeholder rows whose "description" is a reservation note
  (``^(Reserved|Undocumented)``), and the Ross-Tech joke text at 00543,
* add the handful of factory codes the verification pass confirmed by hand but the
  Ross-Tech crawl missed (listed in ``EXTRA_5DIGIT`` with their source).

The result is validated (shape, code grammar, sizes) and written compactly.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List

CODE_RE = re.compile(r"^[PCBU][0-9A-F]{4}$")
FIVE_RE = re.compile(r"^\d{5}$")
PLACEHOLDER_RE = re.compile(r"^(Reserved|Undocumented)", re.IGNORECASE)
MAX_TEXT = 120
TARGET_SIZE = 1_000_000   # bytes; the research file is 1.18 MB with provenance + legacy

# Factory 5-digit codes verified by the dtc_db.md verification pass (Ross-Tech pages /
# the KLineKWP1281Lib table quoted there) but absent from the research JSON.
EXTRA_5DIGIT: Dict[str, str] = {
    "00873": "Bass Speaker Rear Right (R17)",                  # Ross-Tech page 00873
    "00448": "Haldex Clutch Pump (V181)",                      # KLineKWP1281Lib 0x01C0
    "00286": "ABS Inlet/Outlet Valve; Rear Left (N139)",       # KLineKWP1281Lib
    "01313": "Data Bus for Powertrain in Emergency-Mode",      # KLineKWP1281Lib
    "01311": "Information Data Bus",                           # KLineKWP1281Lib
    "00543": "Maximum Engine Speed Exceeded",                  # joke suffix stripped (dtc_db.md §F)
}

# VW wording for codes the verification pass quoted verbatim from KLineKWP1281Lib's
# OBD table and that the research JSON lacks a VW wording for.
EXTRA_VAG_WORDING: Dict[str, str] = {
    "P0299": "Boost Pressure Regulation: Control Range Not Reached",
    "P0401": "EGR System: Insufficient Flow",
    "P0420": "Catalyst System; Bank 1: Efficiency Below Threshold",
    "P0671": "Cylinder 1 Glow Plug Circuit (Q10): Electrical Fault",
    "P0706": "Transmission Range Sensor (F125): Implausible Signal",
    "P0721": "Transmission Output Speed Sensor (G195): Implausible Signal",
    "P0730": "Gear Ratio Monitoring: Incorrect Gear Ratio",
    "P0731": "Gear 1: Incorrect Ratio",
    "P0736": "Reverse Gear: Incorrect Ratio",
    "P1750": "Supply Voltage: too Low",
    "P1757": "Supply Voltage: Open Circuit",
    "P1850": "Powertrain Data Bus: Missing Message from ECU",
    "P1866": "Powertrain Data Bus: Missing Messages",
    "P2002": "Particulate Trap Bank 1: Efficiency Below Threshold",
    "P2463": "Particle Filter: Excessive Soot Accumulation",
    "P3101": "Motor for Intake Manifold Flap (V157): Open or Short to Ground",
    "U0001": "Powertrain Databus: Unspecified Malfunction",
    "U0100": "No Communication with Engine Control Module (SAE ECM/PCM)",
    "U0121": "No Communication with ABS Brake Control Module",
    "U1100": "Component Protection: No Basic Setting",
    "U1101": "Component Protection: Active",
}

# UDS-era codes seen only as "CODE FTB - text" Ross-Tech headings (regex miss in the
# research crawl; quoted in dtc_db.md §A).
EXTRA_CODES: Dict[str, str] = {
    "C10E2": "Control Module for Electronic Parking Brake",
    "B1916": "Backup Battery",
}


def clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("lntake", "Intake")
    return text[:MAX_TEXT]


def build(source: Path) -> dict:
    src = json.loads(source.read_text(encoding="utf-8"))
    for key in ("codes", "vag_wording", "vag_5digit_only", "vag_fault_variants"):
        if key not in src:
            raise SystemExit(f"research file lacks key {key!r}")

    codes: Dict[str, str] = {}
    dropped_placeholders: List[str] = []
    for code, text in src["codes"].items():
        code = code.upper()
        if not CODE_RE.match(code):
            continue
        text = clean(text)
        if not text or PLACEHOLDER_RE.match(text):
            dropped_placeholders.append(code)
            continue
        codes[code] = text
    for code, text in EXTRA_CODES.items():
        codes.setdefault(code, text)

    vag_wording: Dict[str, str] = {}
    for code, text in src["vag_wording"].items():
        code = code.upper()
        text = clean(text)
        if CODE_RE.match(code) and text and not PLACEHOLDER_RE.match(text):
            vag_wording[code] = text
    for code, text in EXTRA_VAG_WORDING.items():
        vag_wording.setdefault(code, text)

    five: Dict[str, str] = {}
    for num, text in src["vag_5digit_only"].items():
        if FIVE_RE.match(num) and clean(text):
            five[num] = clean(text)
    for num, text in EXTRA_5DIGIT.items():
        five[num] = text   # verified replacements win (00543 joke text)

    variants: Dict[str, List[str]] = {}
    for key, items in src["vag_fault_variants"].items():
        key = key.upper()
        if not (CODE_RE.match(key) or FIVE_RE.match(key)):
            continue
        cleaned = [clean(v) for v in items if clean(v)]
        if cleaned:
            variants[key] = cleaned

    stats = {
        "codes": len(codes),
        "vag_wording": len(vag_wording),
        "vag_5digit_only": len(five),
        "vag_fault_variants": len(variants),
        "dropped_placeholders": len(dropped_placeholders),
        "by_prefix": _by_prefix(codes),
        "sources": (src.get("stats") or {}).get("by_source", {}),
    }
    notes = (
        "Generic SAE J2012 wording (codes) from python-OBD (GPL-2) and Wal33D/dtc-database "
        "(MIT) GENERIC rows; VAG P1xxx wording from the Bentley Publishers VW DTC table; "
        "VW/Ross-Tech wording (vag_wording) and KWP-era factory codes (vag_5digit_only) from "
        "Ross-Tech Wiki page headings; P173C/P17BF/P189C from forums.ross-tech.com and "
        "actronics.co.uk; gap-fill P1/P3 wording from vag-hub.com (machine translated). "
        "5-digit <-> P-code and 6-digit numbers are formulas (vagtune.vag.dtc). Built by "
        "tools/build_dtc_db.py from the research database; placeholder rows removed."
    )
    return {
        "source_notes": notes,
        "stats": stats,
        "codes": dict(sorted(codes.items())),
        "vag_wording": dict(sorted(vag_wording.items())),
        "vag_5digit_only": dict(sorted(five.items())),
        "vag_fault_variants": dict(sorted(variants.items())),
    }


def _by_prefix(codes: Dict[str, str]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for code in codes:
        out[code[:2]] = out.get(code[:2], 0) + 1
    return dict(sorted(out.items()))


def validate(db: dict) -> None:
    assert set(db) == {"source_notes", "stats", "codes", "vag_wording", "vag_5digit_only",
                       "vag_fault_variants"}, "unexpected top-level keys"
    assert all(CODE_RE.match(k) for k in db["codes"]), "bad code key"
    assert all(CODE_RE.match(k) for k in db["vag_wording"]), "bad vag_wording key"
    assert all(FIVE_RE.match(k) for k in db["vag_5digit_only"]), "bad 5-digit key"
    assert all(isinstance(v, str) and v for v in db["codes"].values())
    assert all(isinstance(v, list) and all(isinstance(s, str) for s in v)
               for v in db["vag_fault_variants"].values())
    assert not any(PLACEHOLDER_RE.match(v) for v in db["codes"].values()), "placeholder left"
    assert not any(PLACEHOLDER_RE.match(v) for v in db["vag_wording"].values()), "placeholder left"
    # Spot checks the verification pass pinned down.
    assert db["vag_wording"]["P0101"] == "Mass Air Flow Sensor (G70): Implausible Signal"
    assert db["codes"]["P17BF"].startswith("Hydraulic Pump System Overload Protection")
    assert db["vag_5digit_only"]["00287"] == "ABS Wheel Speed Sensor Rear Right (G44)"
    assert "lntake" not in json.dumps(db["codes"])


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    source = Path(argv[1])
    out = Path(argv[2]) if len(argv) > 2 else Path(__file__).resolve().parents[1] / "vagtune" / "data" / "dtc_db.json"
    db = build(source)
    validate(db)
    text = json.dumps(db, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    size = out.stat().st_size
    print(f"wrote {out} ({size} bytes; {db['stats']['codes']} codes, "
          f"{db['stats']['vag_wording']} VW wordings, {db['stats']['vag_5digit_only']} factory codes)")
    if size > TARGET_SIZE:
        print(f"WARNING: {size} bytes exceeds the {TARGET_SIZE} byte target")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
