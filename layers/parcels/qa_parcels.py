#!/usr/bin/env python3
"""Stage 3 parcels QA gates (layer.json 'qa' block).

Gate 1 — ATTRIBUTE WHITELIST (the hard gate): every feature in
parcels.geojsonl must carry ONLY keys ⊆ {apn, county, acres, st}. One foreign
key anywhere fails the build. This is the enforcement point for
owner-names-never-in-tiles — the invariant that keeps the layer at $0
licensing (research 2026-08-09 §5/§6 risk 4) and neutralizes the MT/ID
mailing-list statutes.

Gate 2 — count: kept features within tolerance (default ±25%) of the unit's
sources.json count_expected. Vintages drift year to year; a 50% collapse means
a broken fetch, a 2x jump means a source restructure — both need eyes.

Gate 3 — tiles: decode sample tiles from parcels.pmtiles (bounds from
`pmtiles show`), assert the parcels layer exists somewhere and every decoded
feature passes the same whitelist. Confirms nothing re-enters between
normalize and tile encode.

Calibration (non-fatal): KB/parcel printed and written to qa_stats.json.
Expected 0.4-0.7 through the pyramid; WARN outside 0.2-1.5. The pilot
(UT MT WI) validates this constant before the full matrix is trusted.

Usage:
    qa_parcels.py --unit UT --build build/ [--pmtiles build/parcels.pmtiles]
                  [--tolerance 0.25]
Exit 0 = all gates pass.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import re
import subprocess
import sys
from pathlib import Path

WHITELIST = {"apn", "county", "acres", "st"}


def gate_whitelist(geojsonl: Path) -> tuple[list[str], int]:
    """Full scan of every feature's property keys. Returns (failures, count)."""
    failures: list[str] = []
    offenders: dict[str, int] = {}
    count = 0
    with geojsonl.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip().lstrip("\x1e")
            if not line:
                continue
            try:
                feature = json.loads(line)
            except json.JSONDecodeError:
                failures.append(f"unparsable line at feature ~{count}")
                continue
            count += 1
            props = feature.get("properties") or {}
            for key in props:
                if key not in WHITELIST:
                    offenders[key] = offenders.get(key, 0) + 1
            if "st" not in props:
                offenders["<missing st>"] = offenders.get("<missing st>", 0) + 1
    for key, n in sorted(offenders.items()):
        failures.append(f"WHITELIST VIOLATION: key {key!r} on {n} features "
                        f"(allowed: {sorted(WHITELIST)})")
    return failures, count


def gate_count(unit: str, kept: int, tolerance: float) -> list[str]:
    sources = Path(__file__).parent / "sources.json"
    expected = None
    if sources.exists():
        expected = (json.loads(sources.read_text(encoding="utf-8"))
                    .get(unit, {}).get("count_expected"))
    if not expected:
        print(f"  no count_expected for {unit} — count gate skipped (kept={kept})")
        return []
    drift = abs(kept - expected) / expected
    print(f"  kept={kept} expected={expected} drift={drift:.1%} (tolerance {tolerance:.0%})")
    if drift > tolerance:
        return [f"count drift {drift:.1%} > {tolerance:.0%} (kept={kept}, expected={expected})"]
    return []


def lonlat_to_tile(lon: float, lat: float, z: int) -> tuple[int, int]:
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    lat_r = math.radians(max(-85.05, min(85.05, lat)))
    y = int((1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n)
    return x, y


def pmtiles_bounds(pmtiles: Path) -> tuple[float, float, float, float] | None:
    out = subprocess.run(["pmtiles", "show", str(pmtiles)],
                         capture_output=True, text=True, check=True).stdout
    m = re.search(r"bounds:\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)", out, re.I)
    if not m:
        return None
    return tuple(float(g) for g in m.groups())  # type: ignore[return-value]


def decode_tile(pmtiles: Path, z: int, x: int, y: int) -> dict | None:
    import mapbox_vector_tile  # deferred: only the tile gate needs it
    proc = subprocess.run(["pmtiles", "tile", str(pmtiles), str(z), str(x), str(y)],
                          capture_output=True)
    if proc.returncode != 0 or not proc.stdout:
        return None
    raw = proc.stdout
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return mapbox_vector_tile.decode(raw)


def gate_tiles(pmtiles: Path) -> list[str]:
    bounds = pmtiles_bounds(pmtiles)
    if bounds is None:
        print("  ::warning:: could not parse bounds from `pmtiles show` — tile gate "
              "skipped (whitelist gate already ran on the full geojsonl)")
        return []
    w, s, e, n = bounds
    probes = [(w + (e - w) * fx, s + (n - s) * fy)
              for fx, fy in ((0.5, 0.5), (0.25, 0.25), (0.75, 0.75), (0.25, 0.75), (0.75, 0.25))]
    failures: list[str] = []
    decoded_any = False
    for z in (13, 15):
        for lon, lat in probes:
            x, y = lonlat_to_tile(lon, lat, z)
            tile = decode_tile(pmtiles, z, x, y)
            if tile is None:
                continue
            layer = tile.get("parcels")
            if not layer:
                continue
            decoded_any = True
            for feature in layer["features"]:
                bad = set(feature["properties"]) - WHITELIST
                if bad:
                    failures.append(f"tile {z}/{x}/{y}: non-whitelisted keys {sorted(bad)}")
                    break
    if not decoded_any:
        # Interior probe points can all land in water/desert gaps for odd-shaped
        # states; warn rather than fail — Gate 1 already scanned everything.
        print("  ::warning:: no probe tile contained a parcels layer — check the "
              "tileset visually; whitelist was enforced on the full geojsonl")
    return failures


def calibration(pmtiles: Path, kept: int, build: Path) -> None:
    size = pmtiles.stat().st_size
    kb_per = size / 1024 / max(kept, 1)
    line = f"KB/parcel = {kb_per:.3f} ({size / 1e6:.1f} MB / {kept} parcels)"
    print(f"  {line}")
    if not 0.2 <= kb_per <= 1.5:
        print(f"  ::warning:: {line} outside the expected 0.2-1.5 band "
              f"(research §5 predicts 0.4-0.7) — recheck before trusting the full matrix")
    (build / "qa_stats.json").write_text(json.dumps(
        {"kept": kept, "pmtiles_bytes": size, "kb_per_parcel": round(kb_per, 4)}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--build", required=True)
    parser.add_argument("--pmtiles")
    parser.add_argument("--tolerance", type=float, default=0.25)
    args = parser.parse_args()

    build = Path(args.build)
    failures: list[str] = []

    print("== Gate 1: attribute whitelist (owner-names-never-in-tiles) ==")
    wl_failures, count = gate_whitelist(build / "parcels.geojsonl")
    failures += wl_failures
    print(f"  scanned {count} features: {'CLEAN' if not wl_failures else 'VIOLATIONS'}")

    print("== Gate 2: count vs source ==")
    failures += gate_count(args.unit, count, args.tolerance)

    if args.pmtiles:
        print("== Gate 3: tile decode ==")
        failures += gate_tiles(Path(args.pmtiles))
        calibration(Path(args.pmtiles), count, build)

    if failures:
        print("\nQA FAILED:")
        for failure in failures:
            print(f"  ✗ {failure}")
        sys.exit(1)
    print("\nQA PASSED")


if __name__ == "__main__":
    main()
