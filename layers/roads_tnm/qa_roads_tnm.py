#!/usr/bin/env python3
"""D1b roads_tnm QA gates (layer.json 'qa' block).

Gate 1 — ATTRIBUTE WHITELIST + CONTRACT (hard): every feature in the four
geojsonl outputs carries ONLY keys ⊆ {class,name,ref,mtfcc,source,source_id,
miles}, class ∈ the enum AND belongs to the file it sits in, source ∈
{tiger,usfs,nps,akdot,other}, source_id present. One violation fails the build.

Gate 2 — SIZE BAND: kept ROAD features per zip-MB (sources.json zip_bytes).
Verified band 1,800 (AK, sparse) … 3,440 (DE, dense TIGER) → WARN outside
1,500-4,500; HARD FAIL below 300 (a broken read, not a vintage change).

Gate 3 — GOLDEN BBOX (units with sources.json golden_bbox): per-class-group
counts inside the bbox vs the live carto.nationalmap.gov transportation
MapServer, envelope-intersects semantics on both sides. Groups:
  hwyish = interstate+us_hwy+state_hwy+local_conn  vs  L29+L30+L31
  local vs L32 · ramp vs L33 · fourwd vs L35 · closed vs L36 · trail vs L37
Tolerance 30% (FGDB Feb-2026 vs MapServer Jul-2026 vintages differ; L37 live
still contains the snow/water trails we drop). Degrades to ::warning:: when the
service errors (house rule — no SLA on federal endpoints); drift beyond
tolerance fails.

Gate 4 — TILES: decode probe tiles at z10 + z14 across the archive bounds:
whitelist on every decoded feature; every non-empty layer must appear in at
least one probe (warn); a z6 probe containing roads_local features means the
per-feature minzoom was NOT honoured (warn — visual hierarchy, not correctness).

Calibration (non-fatal): KB/feature -> qa_stats.json. The ID+UT pilot reads
this to decide -z14 vs -z13 for the national run.

Usage:
    qa_roads_tnm.py --unit ID --build build/ [--pmtiles build/roads_tnm.pmtiles]
                    [--tolerance 0.30] [--skip-live]
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
import urllib.parse
import urllib.request
from pathlib import Path

WHITELIST = {"class", "name", "ref", "mtfcc", "source", "source_id", "miles"}
CLASSES = {"interstate", "us_hwy", "state_hwy", "local_conn", "local",
           "ramp", "fourwd", "closed", "trail"}
SOURCES = {"tiger", "usfs", "nps", "akdot", "other"}
LAYER_CLASSES = {
    "roads_hwy": {"interstate", "us_hwy", "state_hwy", "ramp"},
    "roads_local": {"local_conn", "local"},
    "roads_4wd": {"fourwd", "closed"},
    "trails_tnm": {"trail"},
}
ROAD_LAYERS = ("roads_hwy", "roads_local", "roads_4wd")

MAPSERVER = "https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
# our class group -> live layer ids summed
GOLDEN_GROUPS = {
    "hwyish": ({"interstate", "us_hwy", "state_hwy", "local_conn"}, (29, 30, 31)),
    "local": ({"local"}, (32,)),
    "ramp": ({"ramp"}, (33,)),
    "fourwd": ({"fourwd"}, (35,)),
    "closed": ({"closed"}, (36,)),
    "trail": ({"trail"}, (37,)),
}
GOLDEN_MIN_LIVE = 20   # below this a group is too small to judge drift


def sources_cfg(unit: str) -> dict:
    p = Path(__file__).parent / "sources.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8")).get(unit, {}) or {}


def iter_file(path: Path):
    if not path.exists():
        return
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip().lstrip("\x1e")
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                yield None


def feature_bbox(geometry: dict | None):
    if not geometry:
        return None
    coords = geometry.get("coordinates") or []
    if geometry.get("type") == "LineString":
        pts = coords
    elif geometry.get("type") == "MultiLineString":
        pts = [p for line in coords for p in line]
    else:
        return None
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def bbox_intersects(a, b) -> bool:
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


# ── Gate 1 + golden tallies in one pass ───────────────────────────────────────

def scan(build: Path, golden_bbox) -> tuple[list[str], dict]:
    failures: list[str] = []
    offenders: dict[str, int] = {}
    counts = {layer: 0 for layer in LAYER_CLASSES}
    by_class = {c: 0 for c in CLASSES}
    golden = {c: 0 for c in CLASSES}
    for layer, allowed in LAYER_CLASSES.items():
        for feature in iter_file(build / f"{layer}.geojsonl"):
            if feature is None:
                offenders["<unparsable line>"] = offenders.get("<unparsable line>", 0) + 1
                continue
            counts[layer] += 1
            props = feature.get("properties") or {}
            for key in props:
                if key not in WHITELIST:
                    offenders[f"key {key!r}"] = offenders.get(f"key {key!r}", 0) + 1
            cls = props.get("class")
            if cls not in CLASSES:
                offenders[f"class {cls!r}"] = offenders.get(f"class {cls!r}", 0) + 1
            elif cls not in allowed:
                k = f"class {cls!r} in {layer}"
                offenders[k] = offenders.get(k, 0) + 1
            else:
                by_class[cls] += 1
                if golden_bbox is not None:
                    fb = feature_bbox(feature.get("geometry"))
                    if fb and bbox_intersects(fb, golden_bbox):
                        golden[cls] += 1
            if props.get("source") not in SOURCES:
                k = f"source {props.get('source')!r}"
                offenders[k] = offenders.get(k, 0) + 1
            if not props.get("source_id"):
                offenders["<missing source_id>"] = offenders.get("<missing source_id>", 0) + 1
    for key, n in sorted(offenders.items()):
        failures.append(f"CONTRACT VIOLATION: {key} on {n} features")
    return failures, {"counts": counts, "by_class": by_class, "golden": golden}


# ── Gate 2 ────────────────────────────────────────────────────────────────────

def gate_size_band(cfg: dict, road_kept: int) -> list[str]:
    zip_bytes = cfg.get("zip_bytes")
    if not zip_bytes:
        print(f"  no zip_bytes in sources.json — size band skipped (roads kept={road_kept})")
        return []
    per_mb = road_kept / (zip_bytes / 1e6)
    print(f"  roads kept={road_kept} zip={zip_bytes / 1e6:.1f} MB -> {per_mb:.0f} features/zip-MB "
          f"(verified band 1,500-4,500)")
    if per_mb < 300:
        return [f"roads per zip-MB {per_mb:.0f} < 300 — looks like a broken read, not a vintage change"]
    if not 1500 <= per_mb <= 4500:
        print(f"  ::warning:: {per_mb:.0f} features/zip-MB outside the verified 1,500-4,500 band — eyeball the tileset")
    return []


# ── Gate 3 ────────────────────────────────────────────────────────────────────

def live_count(layer_id: int, bbox) -> int | None:
    params = {
        "where": "1=1",
        "geometry": ",".join(str(v) for v in bbox),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "returnCountOnly": "true",
        "f": "json",
    }
    url = f"{MAPSERVER}/{layer_id}/query?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8", "replace"))
    except Exception as exc:  # noqa: BLE001 — any live failure degrades to a warning
        print(f"  ::warning:: live count L{layer_id} failed: {exc}")
        return None
    if "count" not in body:
        print(f"  ::warning:: live count L{layer_id} returned no count: {str(body)[:200]}")
        return None
    return int(body["count"])


def gate_golden(cfg: dict, golden_by_class: dict, tolerance: float, skip_live: bool) -> tuple[list[str], dict]:
    bbox = cfg.get("golden_bbox")
    report: dict = {}
    if not bbox:
        print("  no golden_bbox for this unit — skipped")
        return [], report
    if skip_live:
        print("  --skip-live: golden gate skipped")
        return [], report
    failures: list[str] = []
    for group, (classes, layer_ids) in GOLDEN_GROUPS.items():
        ours = sum(golden_by_class[c] for c in classes)
        live_parts = [live_count(i, bbox) for i in layer_ids]
        if any(v is None for v in live_parts):
            report[group] = {"ours": ours, "live": None}
            continue
        live = sum(live_parts)  # type: ignore[arg-type]
        report[group] = {"ours": ours, "live": live}
        if live < GOLDEN_MIN_LIVE and ours < GOLDEN_MIN_LIVE:
            print(f"  {group:7s} ours={ours:6d} live={live:6d}  (too small to judge)")
            continue
        drift = abs(ours - live) / max(live, 1)
        flag = "OK" if drift <= tolerance else "DRIFT"
        print(f"  {group:7s} ours={ours:6d} live={live:6d} drift={drift:.1%} {flag}")
        if drift > tolerance:
            failures.append(f"golden {group}: ours={ours} live={live} drift {drift:.1%} > {tolerance:.0%}")
    return failures, report


# ── Gate 4 ────────────────────────────────────────────────────────────────────

def lonlat_to_tile(lon: float, lat: float, z: int) -> tuple[int, int]:
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    lat_r = math.radians(max(-85.05, min(85.05, lat)))
    y = int((1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n)
    return x, y


def pmtiles_bounds(pmtiles: Path):
    out = subprocess.run(["pmtiles", "show", str(pmtiles)],
                         capture_output=True, text=True, check=True).stdout
    # go-pmtiles 1.31 prints (verified pilot run 31989953542):
    #   bounds: (long: -117.239175, lat: 41.988226) (long: -111.043699, lat: 49.000822)
    #   antimeridian_adjusted_bounds -117.239175,41.988226,-111.043699,49.000822
    # (the plain "bounds: w,s,e,n" regex the parcels QA uses never matches — its
    # tile gate has always been silently skipped; fixed here, noted for parcels).
    num = r"(-?[\d.]+)"
    m = (re.search(rf"antimeridian_adjusted_bounds\s+{num},{num},{num},{num}", out)
         or re.search(rf"bounds:\s*\(long:\s*{num},\s*lat:\s*{num}\)\s*\(long:\s*{num},\s*lat:\s*{num}\)", out, re.I)
         or re.search(rf"bounds:\s*{num},\s*{num},\s*{num},\s*{num}", out, re.I))
    if not m:
        return None
    return tuple(float(g) for g in m.groups())


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


def gate_tiles(pmtiles: Path, nonempty_layers: set[str]) -> list[str]:
    bounds = pmtiles_bounds(pmtiles)
    if bounds is None:
        print("  ::warning:: could not parse bounds from `pmtiles show` — tile gate skipped")
        return []
    w, s, e, n = bounds
    probes = [(w + (e - w) * fx, s + (n - s) * fy)
              for fx, fy in ((0.5, 0.5), (0.25, 0.25), (0.75, 0.75), (0.25, 0.75), (0.75, 0.25),
                             (0.5, 0.25), (0.5, 0.75), (0.25, 0.5), (0.75, 0.5))]
    failures: list[str] = []
    seen_layers: set[str] = set()
    for z in (10, 14):
        for lon, lat in probes:
            x, y = lonlat_to_tile(lon, lat, z)
            tile = decode_tile(pmtiles, z, x, y)
            if not tile:
                continue
            for layer_name, layer in tile.items():
                if layer_name not in LAYER_CLASSES:
                    failures.append(f"tile {z}/{x}/{y}: unexpected source layer {layer_name!r}")
                    continue
                if layer.get("features"):
                    seen_layers.add(layer_name)
                for feature in layer["features"]:
                    bad = set(feature["properties"]) - WHITELIST
                    if bad:
                        failures.append(f"tile {z}/{x}/{y}/{layer_name}: non-whitelisted keys {sorted(bad)}")
                        break
    missing = nonempty_layers - seen_layers
    if missing:
        print(f"  ::warning:: layers never seen in probe tiles: {sorted(missing)} "
              f"(probes can land in empty country; contract enforced on the full geojsonl)")
    # per-feature minzoom honoured? z6 must not carry roads_local (local_conn is z8, local z10)
    z6_local = 0
    for lon, lat in probes[:5]:
        x, y = lonlat_to_tile(lon, lat, 6)
        tile = decode_tile(pmtiles, 6, x, y)
        if tile and tile.get("roads_local", {}).get("features"):
            z6_local += len(tile["roads_local"]["features"])
    if z6_local:
        print(f"  ::warning:: {z6_local} roads_local features in z6 probe tiles — per-feature "
              f"tippecanoe.minzoom NOT honoured; low-zoom hierarchy is drop-densest only")
    else:
        print("  z6 probes carry no roads_local features — per-feature minzoom honoured")
    print(f"  layers seen in probes: {sorted(seen_layers)}")
    return failures


def calibration(pmtiles: Path, kept: int, build: Path, extra: dict) -> None:
    size = pmtiles.stat().st_size
    kb_per = size / 1024 / max(kept, 1)
    print(f"  KB/feature = {kb_per:.3f} ({size / 1e6:.1f} MB / {kept} features)")
    (build / "qa_stats.json").write_text(json.dumps(
        {"kept": kept, "pmtiles_bytes": size, "kb_per_feature": round(kb_per, 4), **extra},
        indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--build", required=True)
    parser.add_argument("--pmtiles")
    parser.add_argument("--tolerance", type=float, default=0.30)
    parser.add_argument("--skip-live", action="store_true", help="skip the live MapServer golden gate")
    args = parser.parse_args()

    build = Path(args.build)
    cfg = sources_cfg(args.unit)
    failures: list[str] = []

    print("== Gate 1: attribute whitelist + contract ==")
    wl_failures, tallies = scan(build, cfg.get("golden_bbox"))
    failures += wl_failures
    kept = sum(tallies["counts"].values())
    road_kept = sum(tallies["counts"][layer] for layer in ROAD_LAYERS)
    print(f"  scanned {kept} features {tallies['counts']}: {'CLEAN' if not wl_failures else 'VIOLATIONS'}")
    print(f"  by class: {tallies['by_class']}")

    print("== Gate 2: size band vs zip ==")
    failures += gate_size_band(cfg, road_kept)

    print("== Gate 3: golden bbox vs live MapServer ==")
    golden_failures, golden_report = gate_golden(cfg, tallies["golden"], args.tolerance, args.skip_live)
    failures += golden_failures

    extra = {"kept_by_layer": tallies["counts"], "kept_by_class": tallies["by_class"],
             "golden": golden_report}
    if args.pmtiles:
        print("== Gate 4: tile decode ==")
        nonempty = {layer for layer, n in tallies["counts"].items() if n}
        failures += gate_tiles(Path(args.pmtiles), nonempty)
        calibration(Path(args.pmtiles), kept, build, extra)
    else:
        (build / "qa_stats.json").write_text(json.dumps({"kept": kept, **extra}, indent=2, sort_keys=True))

    if failures:
        print("\nQA FAILED:")
        for failure in failures:
            print(f"  ✗ {failure}")
        sys.exit(1)
    print("\nQA PASSED")


if __name__ == "__main__":
    main()
