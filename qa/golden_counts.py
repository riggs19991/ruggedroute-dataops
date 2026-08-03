#!/usr/bin/env python3
"""Golden-bbox QA: normalized feature counts vs live ArcGIS queries (master plan
§11 verification). Every Stage-1 layer has a stable, feature-dense golden bbox
compared against the authoritative live service with a per-layer tolerance —
the bulk snapshot and the live service can be a few days apart, and live
map-services sometimes filter what the bulk GDB carries.

Degrades to a ::warning:: + skip when the live service errors (no SLA on any
of these endpoints); exits 1 on real drift so the workflow fails loudly.

CLI (new):    python3 qa/golden_counts.py --layer mvum --files roads.geojsonl trails.geojsonl
CLI (legacy): python3 qa/golden_counts.py --roads roads.geojsonl --trails trails.geojsonl
              (kept for compatibility; equivalent to --layer mvum)
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

UA = "RuggedRoute-dataops/1.0 (riggs1991@gmail.com)"

SEDONA = (-111.95, 34.70, -111.55, 35.05)      # Coconino NF — dense MVUM country, stable
MOAB = (-109.9, 38.4, -109.3, 38.8)            # BLM Moab field office — dense GTLF
DEATH_VALLEY = (-117.4, 36.2, -116.7, 37.0)    # biggest NPS backcountry road network

EDW = "https://apps.fs.usda.gov/arcx/rest/services/EDW"
BLM = "https://gis.blm.gov/arcgis/rest/services/transportation/BLM_Natl_GTLF_Public_Display/MapServer"
NPS = "https://mapservices.nps.gov/arcgis/rest/services/NationalDatasets/NPS_Public_Roads/FeatureServer"

# Per-layer config. checks are positional with --files: check[i] counts files[i]
# inside bbox and compares against the SUM of its live endpoints' counts.
LAYERS = {
    "mvum": {
        "bbox": SEDONA,
        "tolerance": 0.05,
        "checks": [
            {"name": "roads", "endpoints": [f"{EDW}/EDW_MVUM_01/MapServer/1/query"]},
            {"name": "trails", "endpoints": [f"{EDW}/EDW_MVUM_01/MapServer/2/query"]},
        ],
    },
    "roadcore": {
        "bbox": SEDONA,
        "tolerance": 0.10,
        "checks": [
            # The bulk Trans_RoadCore_FS GDB is the FULL existing-road inventory,
            # but the live companion service splits it: layer 0 = roads open to
            # motorized use, layer 1 = roads closed to motorized uses. Counting
            # layer 0 alone guarantees ~196% drift; summing both layers matches
            # the bulk (measured 2026-08-03, Sedona bbox: bulk 885 vs 0+1 sum
            # 893 -> 0.9% drift; national 368,040 vs 367,960). Mirrors the
            # blm_routes multi-endpoint pattern.
            # TODO: revisit the 10% tolerance after the first real bulk run.
            {"name": "roads",
             "endpoints": [f"{EDW}/EDW_RoadBasic_01/MapServer/{i}/query" for i in (0, 1)]},
        ],
    },
    "nfs_trails": {
        "bbox": SEDONA,
        "tolerance": 0.10,
        "checks": [
            {"name": "trails", "endpoints": [f"{EDW}/EDW_TrailNFSPublish_01/MapServer/0/query"]},
        ],
    },
    "blm_routes": {
        "bbox": MOAB,
        "tolerance": 0.10,
        "checks": [
            {"name": "routes", "endpoints": [f"{BLM}/{i}/query" for i in (0, 1, 2, 3)]},
        ],
    },
    "nps_roads": {
        "bbox": DEATH_VALLEY,
        "tolerance": 0.10,
        "checks": [
            {"name": "roads", "endpoints": [f"{NPS}/0/query"]},
        ],
    },
}


def live_count(endpoint, bbox):
    params = urllib.parse.urlencode({
        "geometry": ",".join(str(v) for v in bbox),
        "geometryType": "esriGeometryEnvelope",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "returnCountOnly": "true",
        "where": "1=1",
        "f": "json",
    })
    req = urllib.request.Request(f"{endpoint}?{params}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    if "count" not in body:  # ArcGIS reports errors with HTTP 200
        raise RuntimeError(f"no count in response: {body}")
    return body["count"]


def local_count(path, bbox):
    xmin, ymin, xmax, ymax = bbox
    n = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                f = json.loads(line)
            except json.JSONDecodeError:
                continue
            geom = (f.get("geometry") if isinstance(f, dict) else None) or {}
            coords = geom.get("coordinates") or []
            if geom.get("type") == "MultiLineString":
                pts = (p for part in coords for p in part)
            elif geom.get("type") == "LineString":
                pts = iter(coords)
            else:
                continue
            if any(xmin <= x <= xmax and ymin <= y <= ymax for x, y, *rest in pts):
                n += 1
    return n


def run_layer(layer, files):
    cfg = LAYERS[layer]
    checks = cfg["checks"]
    if len(files) != len(checks):
        print(f"::error::golden_counts[{layer}]: expected {len(checks)} file(s) "
              f"({', '.join(c['name'] for c in checks)}), got {len(files)}")
        return 1
    failures = 0
    for check, path in zip(checks, files):
        name = check["name"]
        try:
            live = sum(live_count(ep, cfg["bbox"]) for ep in check["endpoints"])
        except Exception as e:  # live service has no SLA — QA degrades to a warning
            print(f"::warning::golden_counts[{layer}/{name}]: live query failed ({e}); "
                  "skipping compare")
            continue
        local = local_count(path, cfg["bbox"])
        drift = abs(local - live) / max(live, 1)
        status = "OK" if drift <= cfg["tolerance"] else "FAIL"
        print(f"golden_counts[{layer}/{name}]: local={local} live={live} "
              f"drift={drift:.1%} tol={cfg['tolerance']:.0%} {status}")
        if drift > cfg["tolerance"]:
            failures += 1
    return 1 if failures else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", choices=sorted(LAYERS))
    ap.add_argument("--files", nargs="+", default=None,
                    help="normalized geojsonl file(s), positional per layer check")
    # Legacy Stage-0 CLI (equivalent to --layer mvum --files ROADS TRAILS)
    ap.add_argument("--roads", default=None)
    ap.add_argument("--trails", default=None)
    args = ap.parse_args()

    if args.layer:
        if not args.files:
            ap.error("--layer requires --files")
        sys.exit(run_layer(args.layer, args.files))
    if args.roads and args.trails:
        sys.exit(run_layer("mvum", [args.roads, args.trails]))
    ap.error("use --layer NAME --files F [F...] (or legacy --roads/--trails)")


if __name__ == "__main__":
    main()
