#!/usr/bin/env python3
"""Golden-bbox QA: normalized feature counts vs a live EDW query (master plan Stage 0
verification: 'golden-bbox feature count matches live EDW +-0' — we allow a small tolerance
because the bulk snapshot and the live service can be a few days apart).

Exit 1 on failure so the workflow fails loudly.
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

# Sedona / Coconino NF — dense MVUM country, stable
BBOX = (-111.95, 34.70, -111.55, 35.05)  # xmin, ymin, xmax, ymax
EDW = "https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_MVUM_01/MapServer/{layer}/query"
TOLERANCE = 0.05  # 5%
UA = "RuggedRoute-dataops/1.0 (riggs1991@gmail.com)"


def live_count(layer):
    params = urllib.parse.urlencode({
        "geometry": ",".join(str(v) for v in BBOX),
        "geometryType": "esriGeometryEnvelope",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "returnCountOnly": "true",
        "where": "1=1",
        "f": "json",
    })
    req = urllib.request.Request(f"{EDW.format(layer=layer)}?{params}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["count"]


def local_count(path):
    xmin, ymin, xmax, ymax = BBOX
    n = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                f = json.loads(line)
            except json.JSONDecodeError:
                continue
            geom = f.get("geometry") or {}
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roads", required=True)
    ap.add_argument("--trails", required=True)
    args = ap.parse_args()

    failures = 0
    for name, layer, path in (("roads", 1, args.roads), ("trails", 2, args.trails)):
        try:
            live = live_count(layer)
        except Exception as e:  # live service has no SLA — QA degrades to a warning
            print(f"::warning::golden_counts[{name}]: live EDW query failed ({e}); skipping compare")
            continue
        local = local_count(path)
        drift = abs(local - live) / max(live, 1)
        status = "OK" if drift <= TOLERANCE else "FAIL"
        print(f"golden_counts[{name}]: local={local} live={live} drift={drift:.1%} {status}")
        if drift > TOLERANCE:
            failures += 1
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
