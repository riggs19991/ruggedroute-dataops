#!/usr/bin/env python3
"""Stage 2 lands normalizer: PAD-US GDB -> land_fee.geojsonl + land_overlay.geojsonl.

Reads the PAD-US Fee layer (the flattened ownership base) and the Designation
layer (Wilderness / Wilderness Study Areas) from a PAD-US 4.x FileGDB and emits
the two normalized GeoJSONSeq files tiles.sh feeds to tippecanoe.

Schema contract (layer.json + the Android client's LandTileFeatureParser):
    land_fee:     {mgr, unit, access}   -- PVT/UNK dropped; access UK dropped
    land_overlay: {kind, name}          -- kind: wilderness | wsa

Design notes
------------
* ogr2ogr does the heavy lifting (GDB read, 4326 reproject, GeoJSONSeq
  streaming); this script streams line-by-line, so national runs stay flat on
  memory. -makevalid repairs the handful of self-intersections PAD-US ships.
* The Fee layer is already FLAT (non-overlapping by design) -- no carve is
  needed for the base-only build. When agency patches land (layer.json slots),
  the carve step runs base := base - patch_footprint before appending patches;
  translucent fills double-blend wherever polygons overlap, so precedence must
  be geometric, not paint-order.
* Proclamation is NEVER read (admin extents contain private land -- painting
  them is the classic trespass-liability bug).
* Designation polygons overlap Fee by design; they feed ONLY land_overlay.

Usage:
    normalize_lands.py --gdb PADUS4_1_StateUT.gdb --out build/
    normalize_lands.py --gdb national.gdb --fee-layer PADUS4_1Fee --out build/
Layer names are auto-detected when omitted (first layer matching Fee/Designation).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# ── Manager normalization ──────────────────────────────────────────────────────
# PAD-US Mang_Name (Agency Name domain, harvested from the 4.1 GDB domain table
# 2026-08-07) -> normalized rr mgr code. THE CONTRACT with the client color map
# (LayerRegistry.LANDS_FILL_COLORS) and label map (LandTileFeatureParser).
#
# PVT and UNK map to None = DROPPED: unshaded = private is the atlas convention,
# and absent polygons keep tiles small.
MGR_MAP: dict[str, str | None] = {
    # Federal
    "BLM": "BLM",
    "USFS": "USFS",
    "NPS": "NPS",
    "FWS": "FWS",
    "USBR": "BOR",
    "DOD": "DOD",
    "USACE": "FED_OTHER",   # Army Corps rec lands are public but are NOT Reclamation
    "DOE": "FED_OTHER",
    "NOAA": "FED_OTHER",
    "NRCS": "FED_OTHER",
    "ARS": "FED_OTHER",
    "BPA": "FED_OTHER",
    "BOEM": "FED_OTHER",
    "TVA": "FED_OTHER",
    "OTHF": "FED_OTHER",
    # Tribal
    "BIA": "TRIBAL",
    "TRIB": "TRIBAL",
    # State
    "SPR": "ST_PARK",
    "SFW": "ST_WILDLIFE",
    "SLB": "ST_TRUST",      # State Land Board = trust sections (UT SITLA et al.)
    "SDOL": "ST_TRUST",     # State Department of Land (AZ ASLD et al.)
    "SDC": "ST_OTHER",      # State Dept of Conservation
    "SDNR": "ST_OTHER",
    "OTHS": "ST_OTHER",
    # Local / regional
    "CITY": "LOCAL",
    "CNTY": "LOCAL",
    "REG": "LOCAL",
    "RWD": "LOCAL",
    "UNKL": "LOCAL",
    "JNT": "LOCAL",         # Joint city/county style holdings
    # NGO
    "NGO": "NGO",
    # Dropped
    "PVT": None,
    "UNK": None,
}

# PAD-US Pub_Access codes we carry; UK (unknown) is dropped -- never render an
# unknown as a confident access claim.
ACCESS_KEEP = {"OA", "RA", "XA"}

# Designation types that form the motorized-closure overlay.
OVERLAY_KIND = {"WA": "wilderness", "WSA": "wsa"}


def detect_layer(gdb: str, needle: str) -> str | None:
    """First layer in the GDB whose name contains needle (case-insensitive)."""
    out = subprocess.run(
        ["ogrinfo", "-so", "-q", gdb],
        capture_output=True, text=True, check=True,
    ).stdout
    for line in out.splitlines():
        # Listing shape varies by driver: OpenFileGDB prints
        # "Layer: PADUS4_1Fee_State_UT (Multi Polygon)", GPKG (used by the
        # test fixtures) prints "1: PADUS9_9Fee_State_XX (Multi Polygon)".
        line = line.strip()
        name = None
        if line.startswith("Layer:"):
            name = line.split("Layer:")[1].split("(")[0].strip()
        else:
            numbered = re.match(r"^\d+:\s+(.+?)(?:\s+\(|$)", line)
            if numbered:
                name = numbered.group(1).strip()
        if name and needle.lower() in name.lower():
            return name
    return None


def ogr_stream(gdb: str, layer: str, fields: list[str]) -> subprocess.Popen:
    """ogr2ogr GeoJSONSeq stream of layer, reprojected to EPSG:4326."""
    cmd = [
        "ogr2ogr",
        "-f", "GeoJSONSeq", "/vsistdout/",
        gdb, layer,
        "-t_srs", "EPSG:4326",
        "-makevalid",
        "-select", ",".join(fields),
        "-nlt", "PROMOTE_TO_MULTI",
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1)


def clean(value) -> str | None:
    """None for null-ish attribute values (None, '', 'null', whitespace)."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "null":
        return None
    return text


def normalize_fee(gdb: str, layer: str, out_path: Path, stats: dict) -> None:
    """Fee polygons -> land_fee.geojsonl with {mgr, unit, access} props."""
    proc = ogr_stream(gdb, layer, ["Mang_Name", "Unit_Nm", "Pub_Access", "GIS_Acres"])
    kept = dropped = unmapped = 0
    with out_path.open("w", encoding="utf-8") as out:
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.strip().lstrip("\x1e")  # ogr GeoJSONSeq RS separators
            if not line:
                continue
            feature = json.loads(line)
            props = feature.get("properties") or {}
            raw_mgr = (clean(props.get("Mang_Name")) or "UNK").upper()
            if raw_mgr not in MGR_MAP:
                # Harvest-time unknown: keep the map honest -- route to
                # FED_OTHER only for *_F-looking codes would be a guess, so
                # count it, drop it, and let QA surface the gap loudly.
                unmapped += 1
                stats.setdefault("unmapped_codes", {}).setdefault(raw_mgr, 0)
                stats["unmapped_codes"][raw_mgr] += 1
                continue
            mgr = MGR_MAP[raw_mgr]
            if mgr is None:
                dropped += 1
                continue
            access = (clean(props.get("Pub_Access")) or "").upper()
            new_props = {"mgr": mgr}
            unit = clean(props.get("Unit_Nm"))
            if unit:
                new_props["unit"] = unit
            if access in ACCESS_KEEP:
                new_props["access"] = access
            acres = props.get("GIS_Acres")
            feature["properties"] = new_props
            out.write(json.dumps(feature, separators=(",", ":")) + "\n")
            kept += 1
            per = stats.setdefault("acres_by_mgr", {})
            try:
                per[mgr] = per.get(mgr, 0) + float(acres or 0)
            except (TypeError, ValueError):
                pass
    rc = proc.wait()
    if rc != 0:
        sys.exit(f"ogr2ogr failed on fee layer {layer} (rc={rc})")
    stats["fee_kept"] = kept
    stats["fee_dropped_private"] = dropped
    stats["fee_unmapped"] = unmapped


def normalize_dod_tribal_extents(gdb: str, layer: str, out_path: Path, stats: dict) -> None:
    """DOD + Tribal exterior extents from the PAD-US Combined layer.

    PAD-US 4.1 scripts DOD (via MIRTA) and Tribal (via Census AIANNH) into the
    Comb_DOD_Trib layer as Category='Proclamation' rows — they are ABSENT from
    the Fee layer entirely (verified on UT: Dugway/UTTR 1.45M ac + Uintah &
    Ouray/Navajo 5.76M ac live only there). Exterior extents are exactly what
    an onX-style map renders for these two classes (tribal interiors are
    checkerboarded — the client sheet carries the mandatory "exterior boundary
    only" caveat), so take Category='Proclamation' rows for Mang_Name in
    (DOD, TRIB, BIA) and NOTHING else: forest/park proclamations as ownership
    is the classic trespass-liability bug.

    APPENDS to land_fee.geojsonl — call after normalize_fee.
    """
    proc = ogr_stream(gdb, layer, ["Category", "Mang_Name", "Unit_Nm", "Pub_Access", "GIS_Acres"])
    counts: dict[str, int] = {}
    with out_path.open("a", encoding="utf-8") as out:
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.strip().lstrip("\x1e")
            if not line:
                continue
            feature = json.loads(line)
            props = feature.get("properties") or {}
            category = (clean(props.get("Category")) or "").lower()
            raw_mgr = (clean(props.get("Mang_Name")) or "").upper()
            if category != "proclamation" or raw_mgr not in ("DOD", "TRIB", "BIA"):
                continue
            mgr = "DOD" if raw_mgr == "DOD" else "TRIBAL"
            new_props = {"mgr": mgr}
            unit = clean(props.get("Unit_Nm"))
            if unit:
                new_props["unit"] = unit
            access = (clean(props.get("Pub_Access")) or "").upper()
            if access in ACCESS_KEEP:
                new_props["access"] = access
            feature["properties"] = new_props
            out.write(json.dumps(feature, separators=(",", ":")) + "\n")
            counts[mgr] = counts.get(mgr, 0) + 1
            per = stats.setdefault("acres_by_mgr", {})
            try:
                per[mgr] = per.get(mgr, 0) + float(props.get("GIS_Acres") or 0)
            except (TypeError, ValueError):
                pass
    rc = proc.wait()
    if rc != 0:
        sys.exit(f"ogr2ogr failed on combined layer {layer} (rc={rc})")
    stats["dod_tribal_extent_counts"] = counts


def normalize_overlay(gdb: str, layer: str, out_path: Path, stats: dict) -> None:
    """Designation WA/WSA polygons -> land_overlay.geojsonl with {kind, name}."""
    proc = ogr_stream(gdb, layer, ["Des_Tp", "Unit_Nm"])
    counts: dict[str, int] = {}
    with out_path.open("w", encoding="utf-8") as out:
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.strip().lstrip("\x1e")
            if not line:
                continue
            feature = json.loads(line)
            props = feature.get("properties") or {}
            des_tp = (clean(props.get("Des_Tp")) or "").upper()
            kind = OVERLAY_KIND.get(des_tp)
            if kind is None:
                continue
            new_props = {"kind": kind}
            name = clean(props.get("Unit_Nm"))
            if name:
                new_props["name"] = name
            feature["properties"] = new_props
            out.write(json.dumps(feature, separators=(",", ":")) + "\n")
            counts[kind] = counts.get(kind, 0) + 1
    rc = proc.wait()
    if rc != 0:
        sys.exit(f"ogr2ogr failed on designation layer {layer} (rc={rc})")
    stats["overlay_counts"] = counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gdb", required=True, help="PAD-US 4.x FileGDB path")
    parser.add_argument("--fee-layer", help="Fee layer name (auto-detected when omitted)")
    parser.add_argument("--designation-layer", help="Designation layer name (auto-detected)")
    parser.add_argument("--out", required=True, help="output directory")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    fee_layer = args.fee_layer or detect_layer(args.gdb, "Fee")
    if not fee_layer:
        sys.exit("no Fee layer found in GDB -- pass --fee-layer")
    des_layer = args.designation_layer or detect_layer(args.gdb, "Designation")

    comb_layer = detect_layer(args.gdb, "Comb_DOD_Trib")

    stats: dict = {
        "gdb": args.gdb,
        "fee_layer": fee_layer,
        "designation_layer": des_layer,
        "combined_layer": comb_layer,
    }
    normalize_fee(args.gdb, fee_layer, out_dir / "land_fee.geojsonl", stats)
    if comb_layer:
        normalize_dod_tribal_extents(args.gdb, comb_layer, out_dir / "land_fee.geojsonl", stats)
    else:
        print("WARNING: no Comb_DOD_Trib layer found -- DOD/Tribal fills will be MISSING",
              file=sys.stderr)
    if des_layer:
        normalize_overlay(args.gdb, des_layer, out_dir / "land_overlay.geojsonl", stats)
    else:
        # Never silently skip the closure overlay -- an empty file keeps
        # tiles.sh honest and the log states why.
        (out_dir / "land_overlay.geojsonl").write_text("")
        print("WARNING: no Designation layer found -- land_overlay is EMPTY", file=sys.stderr)

    (out_dir / "normalize_stats.json").write_text(json.dumps(stats, indent=2, sort_keys=True))
    print(json.dumps(stats, indent=2, sort_keys=True))
    if stats.get("fee_unmapped"):
        # Loud but non-fatal: QA gates on it so CI fails visibly, while a local
        # dev run still produces inspectable output.
        print(f"WARNING: {stats['fee_unmapped']} features had UNMAPPED manager codes "
              f"{sorted((stats.get('unmapped_codes') or {}).keys())} -- extend MGR_MAP",
              file=sys.stderr)


if __name__ == "__main__":
    main()
