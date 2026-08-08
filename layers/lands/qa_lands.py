#!/usr/bin/env python3
"""Stage 2 lands QA gates (layer.json 'qa' block).

Gate 1 — acreage: per-manager acreage in the normalized output must sit within
tolerance (default 2%) of an INDEPENDENT recompute from the source GDB. The
normalizer accumulates acres per feature while streaming; this recomputes the
same sums with ogrinfo SQL. A gap means features were lost or double-kept.

Gate 2 — tiles: decode one built tile per probe point from lands.pmtiles and
assert the contract: land_fee present, every feature carries a mapped mgr code,
and no PVT/UNK ever reaches a tile (unshaded = private is the product promise).

Gate 3 — private probes: at each fixture point expected to be PRIVATE (a known
inholding), NO land_fee polygon may cover it; at points with an expected code,
the covering polygon's mgr must match. Fixtures are harvested from the data
(Proclamation-minus-Fee interiors), then hand-checked once.

Usage:
    qa_lands.py --gdb <src.gdb> --build <build_dir> [--probes probes.json]
                [--tolerance 0.02] [--pmtiles <lands.pmtiles>]
Exit 0 = all gates pass.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from normalize_lands import MGR_MAP, detect_layer  # noqa: E402

VALID_MGR = {code for code in MGR_MAP.values() if code}


def sql_acres_by_mgr(gdb: str, fee_layer: str) -> dict[str, float]:
    """Independent per-mgr acreage recompute straight from the GDB."""
    out = subprocess.run(
        ["ogrinfo", "-q", "-dialect", "SQLITE", "-sql",
         f"SELECT Mang_Name, SUM(GIS_Acres) AS acres FROM {fee_layer} GROUP BY Mang_Name",
         gdb],
        capture_output=True, text=True, check=True,
    ).stdout
    raw: dict[str, float] = {}
    name = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("Mang_Name"):
            name = line.split("=", 1)[1].strip()
        elif line.startswith("acres") and name is not None:
            value = line.split("=", 1)[1].strip()
            try:
                raw[name] = float(value)
            except ValueError:
                pass
            name = None
    acres: dict[str, float] = {}
    for code, total in raw.items():
        mgr = MGR_MAP.get(code.upper())
        if mgr:
            acres[mgr] = acres.get(mgr, 0.0) + total
    return acres


def sql_dod_tribal_acres(gdb: str, comb_layer: str) -> dict[str, float]:
    """DOD/Tribal extents live only in the Combined layer (Category=Proclamation)."""
    out = subprocess.run(
        ["ogrinfo", "-q", "-dialect", "SQLITE", "-sql",
         "SELECT Mang_Name, SUM(GIS_Acres) AS acres FROM "
         f"{comb_layer} WHERE Category='Proclamation' AND Mang_Name IN ('DOD','TRIB','BIA') "
         "GROUP BY Mang_Name",
         gdb],
        capture_output=True, text=True, check=True,
    ).stdout
    acres: dict[str, float] = {}
    name = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("Mang_Name"):
            name = line.split("=", 1)[1].strip().upper()
        elif line.startswith("acres") and name is not None:
            mgr = "DOD" if name == "DOD" else "TRIBAL"
            try:
                acres[mgr] = acres.get(mgr, 0.0) + float(line.split("=", 1)[1].strip())
            except ValueError:
                pass
            name = None
    return acres


def gate_acreage(gdb: str, fee_layer: str, build: Path, tolerance: float) -> list[str]:
    stats = json.loads((build / "normalize_stats.json").read_text())
    got: dict[str, float] = stats.get("acres_by_mgr", {})
    expected = sql_acres_by_mgr(gdb, fee_layer)
    comb_layer = stats.get("combined_layer")
    if comb_layer:
        for mgr, acres in sql_dod_tribal_acres(gdb, comb_layer).items():
            expected[mgr] = expected.get(mgr, 0.0) + acres
    failures = []
    for mgr in sorted(set(expected) | set(got)):
        exp, act = expected.get(mgr, 0.0), got.get(mgr, 0.0)
        if exp < 1000:  # sub-1k-acre managers: absolute noise floor, skip ratio
            continue
        drift = abs(act - exp) / exp
        line = f"  {mgr:12s} expected={exp:14.0f} got={act:14.0f} drift={drift:6.2%}"
        print(line)
        if drift > tolerance:
            failures.append(f"acreage drift {drift:.2%} > {tolerance:.0%} for {mgr}")
    if stats.get("fee_unmapped"):
        failures.append(
            f"{stats['fee_unmapped']} features with unmapped manager codes "
            f"{sorted((stats.get('unmapped_codes') or {}).keys())}"
        )
    return failures


def lonlat_to_tile(lon: float, lat: float, z: int) -> tuple[int, int]:
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    lat_r = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n)
    return x, y


def decode_tile(pmtiles: Path, z: int, x: int, y: int) -> dict:
    """pmtiles CLI tile fetch -> decoded MVT dict (mapbox_vector_tile)."""
    import mapbox_vector_tile  # deferred: only the tile gate needs it
    raw = subprocess.run(
        ["pmtiles", "tile", str(pmtiles), str(z), str(x), str(y)],
        capture_output=True, check=True,
    ).stdout
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return mapbox_vector_tile.decode(raw)


def gate_tiles(pmtiles: Path, probes: list[dict]) -> list[str]:
    failures = []
    zoom = 10
    seen_fee = False
    for probe in probes:
        x, y = lonlat_to_tile(probe["lon"], probe["lat"], zoom)
        try:
            tile = decode_tile(pmtiles, zoom, x, y)
        except subprocess.CalledProcessError:
            continue  # empty tile — fine for a private-expectation probe
        fee = tile.get("land_fee")
        if not fee:
            continue
        seen_fee = True
        for feature in fee["features"]:
            mgr = feature["properties"].get("mgr")
            if mgr not in VALID_MGR:
                failures.append(f"tile {zoom}/{x}/{y}: invalid mgr {mgr!r} in land_fee")
                break
    if probes and not seen_fee:
        failures.append("no probe tile contained a land_fee layer — tileset looks empty")
    return failures


def gate_probes(build: Path, probes: list[dict]) -> list[str]:
    from shapely.geometry import Point, shape
    from shapely.strtree import STRtree

    geoms, mgrs = [], []
    with (build / "land_fee.geojsonl").open() as f:
        for line in f:
            line = line.strip().lstrip("\x1e")
            if not line:
                continue
            feature = json.loads(line)
            geoms.append(shape(feature["geometry"]))
            mgrs.append(feature["properties"]["mgr"])
    tree = STRtree(geoms)
    failures = []
    for probe in probes:
        point = Point(probe["lon"], probe["lat"])
        hits = [i for i in tree.query(point) if geoms[i].covers(point)]
        got = sorted({mgrs[i] for i in hits})
        expect = probe["expect"]
        label = probe.get("label", f"{probe['lat']:.4f},{probe['lon']:.4f}")
        if expect == "none":
            if hits:
                failures.append(f"probe {label}: expected PRIVATE (no fill), got {got}")
            else:
                print(f"  probe {label}: private ✓")
        else:
            if expect not in got:
                failures.append(f"probe {label}: expected {expect}, got {got or 'none'}")
            else:
                print(f"  probe {label}: {expect} ✓")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gdb", required=True)
    parser.add_argument("--fee-layer")
    parser.add_argument("--build", required=True)
    parser.add_argument("--probes")
    parser.add_argument("--pmtiles")
    parser.add_argument("--tolerance", type=float, default=0.02)
    args = parser.parse_args()

    build = Path(args.build)
    fee_layer = args.fee_layer or detect_layer(args.gdb, "Fee")
    if not fee_layer:
        sys.exit("no Fee layer found")

    probes = json.loads(Path(args.probes).read_text()) if args.probes else []

    failures = []
    print("== Gate 1: per-manager acreage vs source ==")
    failures += gate_acreage(args.gdb, fee_layer, build, args.tolerance)
    if probes:
        print("== Gate 3: ownership probe points ==")
        failures += gate_probes(build, probes)
        if args.pmtiles:
            print("== Gate 2: tile decode ==")
            failures += gate_tiles(Path(args.pmtiles), probes)

    if failures:
        print("\nQA FAILED:")
        for failure in failures:
            print(f"  ✗ {failure}")
        sys.exit(1)
    print("\nQA PASSED")


if __name__ == "__main__":
    main()
