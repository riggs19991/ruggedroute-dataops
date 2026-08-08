#!/usr/bin/env python3
"""Harvest QA probe fixtures for the lands layer from the data itself.

Private-inholding probes: sample interior points of USFS PROCLAMATION polygons
(admin extents) that NO kept fee polygon covers — by construction these are the
private inholdings the ownership fill must leave unshaded ("5 known private
inholdings NOT green" acceptance gate). Points are emitted with expect:"none"
and become regression guards in qa_lands.py.

Manager probes: representative points of kept fee polygons for the codes under
test (ST_TRUST checkerboard sections, TRIBAL, BLM, USFS) — these prove the
mapping end-to-end through tiles.

Usage:
    harvest_probes.py --gdb <src.gdb> --build <build_dir> --out probes.json \
        [--inholdings 3] [--mgr ST_TRUST --mgr BLM ...]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from shapely.geometry import shape
from shapely.strtree import STRtree

sys.path.insert(0, str(Path(__file__).parent))
from normalize_lands import clean, detect_layer  # noqa: E402


def load_fee(build: Path):
    geoms, mgrs, units = [], [], []
    with (build / "land_fee.geojsonl").open() as f:
        for line in f:
            line = line.strip().lstrip("\x1e")
            if not line:
                continue
            feature = json.loads(line)
            geoms.append(shape(feature["geometry"]))
            mgrs.append(feature["properties"]["mgr"])
            units.append(feature["properties"].get("unit"))
    return geoms, mgrs, units


def proclamation_geoms(gdb: str):
    layer = detect_layer(gdb, "Proclamation")
    if not layer:
        return []
    proc = subprocess.Popen(
        ["ogr2ogr", "-f", "GeoJSONSeq", "/vsistdout/", gdb, layer,
         "-t_srs", "EPSG:4326", "-makevalid", "-select", "Unit_Nm",
         "-nlt", "PROMOTE_TO_MULTI"],
        stdout=subprocess.PIPE, text=True, bufsize=1,
    )
    out = []
    assert proc.stdout is not None
    for line in proc.stdout:
        line = line.strip().lstrip("\x1e")
        if not line:
            continue
        feature = json.loads(line)
        name = clean((feature.get("properties") or {}).get("Unit_Nm")) or "proclamation"
        out.append((shape(feature["geometry"]), name))
    proc.wait()
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gdb", required=True)
    parser.add_argument("--build", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--inholdings", type=int, default=3)
    parser.add_argument("--mgr", action="append", default=[])
    args = parser.parse_args()

    build = Path(args.build)
    geoms, mgrs, units = load_fee(build)
    tree = STRtree(geoms)
    probes: list[dict] = []

    def covered(point) -> list[int]:
        return [i for i in tree.query(point) if geoms[i].covers(point)]

    # ── Private inholdings: proclamation interior − fee coverage ──────────────
    found = 0
    for geom, name in proclamation_geoms(args.gdb):
        if found >= args.inholdings:
            break
        # Erode toward the interior so boundary slivers can't fake a hit, then
        # sample the largest uncovered pocket via a coarse interior grid.
        minx, miny, maxx, maxy = geom.bounds
        steps = 60
        from shapely.geometry import Point
        best = None
        for ix in range(1, steps):
            for iy in range(1, steps):
                point = Point(minx + (maxx - minx) * ix / steps,
                              miny + (maxy - miny) * iy / steps)
                if not geom.covers(point):
                    continue
                hits = covered(point)
                if not hits:
                    # require a real pocket: neighbors uncovered too
                    eps = (maxx - minx) / steps / 3
                    ring = [Point(point.x + dx, point.y + dy)
                            for dx in (-eps, eps) for dy in (-eps, eps)]
                    if all(not covered(p) for p in ring if geom.covers(p)):
                        best = point
                        break
            if best:
                break
        if best:
            probes.append({
                "label": f"inholding:{name}",
                "lon": round(best.x, 6), "lat": round(best.y, 6),
                "expect": "none",
            })
            found += 1

    # ── Manager probes from kept polygons ─────────────────────────────────────
    for want in args.mgr:
        for i, mgr in enumerate(mgrs):
            if mgr != want:
                continue
            point = geoms[i].representative_point()
            if [j for j in covered(point) if mgrs[j] == want]:
                probes.append({
                    "label": f"{want}:{units[i] or 'unit?'}",
                    "lon": round(point.x, 6), "lat": round(point.y, 6),
                    "expect": want,
                })
                break

    Path(args.out).write_text(json.dumps(probes, indent=2))
    print(json.dumps(probes, indent=2))
    if found < args.inholdings:
        print(f"WARNING: only {found}/{args.inholdings} inholding probes found",
              file=sys.stderr)


if __name__ == "__main__":
    main()
