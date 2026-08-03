#!/usr/bin/env python3
"""Harvest a real-world corpus of MVUM season strings for parser hardening.

Queries the live USFS EDW MVUM service (layers 1=roads, 2=trails) for DISTINCT
values of every season field, classifies each through lib/normalize_mvum.py's
parse_seasons, and writes lib/fixtures/datesopen_corpus.json.

Live ArcGIS queries are QA-only per the master plan; this is a QA/fixture tool,
not part of the tile pipeline. Politeness: sequential requests via curl with
--retry 2 and a custom User-Agent identifying us.

Run:  python lib/fixtures/harvest_datesopen.py
"""
import json
import subprocess
import sys
import time
import urllib.parse
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # lib/
from normalize_mvum import parse_seasons  # noqa: E402

BASE = "https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_MVUM_01/MapServer"
LAYERS = {1: "roads", 2: "trails"}
USER_AGENT = "RuggedRoute-dataops/1.0 (riggs1991@gmail.com)"
PAUSE_S = 0.5  # between sequential requests

# The 17 season fields per the EDW MVUM schema docs. Actual service field names
# differ for some (no 'inches' in *_gt50/_lt50 datesopen names; e-bike uses _dur).
REQUESTED_FIELDS = [
    "passengervehicle_datesopen",
    "highclearancevehicle_datesopen",
    "truck_datesopen",
    "bus_datesopen",
    "motorhome_datesopen",
    "fourwd_gt50inches_datesopen",
    "twowd_gt50inches_datesopen",
    "tracked_ohv_gt50inches_datesopen",
    "tracked_ohv_lt50inches_datesopen",
    "other_ohv_gt50inches_datesopen",
    "other_ohv_lt50inches_datesopen",
    "atv_datesopen",
    "motorcycle_datesopen",
    "otherwheeled_ohv_datesopen",
    "e_bike_class1_datesopen",
    "e_bike_class2_datesopen",
    "e_bike_class3_datesopen",
]


def curl_json(url):
    """GET url via curl, return parsed JSON. Raises on transport/JSON failure."""
    proc = subprocess.run(
        ["curl", "-sS", "--fail", "--retry", "2", "--max-time", "60",
         "-A", USER_AGENT, url],
        capture_output=True, text=True, timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"curl exit {proc.returncode}: {proc.stderr.strip()[:200]}")
    return json.loads(proc.stdout)


def resolve_field(requested, actual_lower):
    """Map a requested season-field name to the service's actual field name."""
    candidates = [
        requested,
        requested.replace("gt50inches_datesopen", "gt50_datesopen")
                 .replace("lt50inches_datesopen", "lt50_datesopen"),
        requested.replace("_datesopen", "_dur"),  # e_bike_classN_dur
    ]
    for c in candidates:
        if c in actual_lower:
            return actual_lower[c]
    return None


def distinct_values(layer_id, field, failures):
    """Yield distinct values of one field, paginating if the server truncates."""
    values, offset = [], 0
    while True:
        params = {
            "where": "1=1",
            "outFields": field,
            "returnDistinctValues": "true",
            "returnGeometry": "false",
            "f": "json",
        }
        if offset:
            params["resultOffset"] = str(offset)
        url = f"{BASE}/{layer_id}/query?{urllib.parse.urlencode(params)}"
        try:
            data = curl_json(url)
        except Exception as e:  # tolerate per-field failure, record + continue
            failures.append({"layer": layer_id, "field": field, "error": str(e)})
            return values
        if "error" in data:
            failures.append({"layer": layer_id, "field": field, "error": data["error"]})
            return values
        feats = data.get("features", [])
        for feat in feats:
            attrs = feat.get("attributes", {})
            # attribute key case can differ from the requested name
            for v in attrs.values():
                values.append(v)
        if data.get("exceededTransferLimit") and feats:
            offset += len(feats)
            time.sleep(PAUSE_S)
            continue
        return values


def main():
    failures = []
    field_map = {}       # layer -> {requested: actual or None}
    corpus = {}          # value string -> set of "layer:field" provenance
    fields_queried = set()

    for layer_id in LAYERS:
        meta = curl_json(f"{BASE}/{layer_id}?f=json")
        actual_lower = {f["name"].lower(): f["name"] for f in meta.get("fields", [])}
        time.sleep(PAUSE_S)
        field_map[layer_id] = {}
        for requested in REQUESTED_FIELDS:
            actual = resolve_field(requested, actual_lower)
            field_map[layer_id][requested] = actual
            if actual is None:
                print(f"layer {layer_id}: SKIP {requested} (no matching field)",
                      file=sys.stderr)
                continue
            vals = distinct_values(layer_id, actual, failures)
            fields_queried.add(actual)
            n_new = 0
            for v in vals:
                if v is None or not str(v).strip():
                    continue
                s = str(v)
                if s not in corpus:
                    n_new += 1
                corpus.setdefault(s, set()).add(f"{layer_id}:{actual}")
            print(f"layer {layer_id}: {actual}: {len(vals)} distinct ({n_new} new)",
                  file=sys.stderr)
            time.sleep(PAUSE_S)

    entries = []
    for value in sorted(corpus):
        windows, ok = parse_seasons(value)
        entries.append({"value": value, "parse_ok": ok, "windows": windows})

    out = {
        "generated": date.today().isoformat(),
        "source": "EDW_MVUM_01 layers 1+2 distinct values",
        "fields_queried": sorted(fields_queried),
        "field_resolution": {
            str(layer_id): field_map[layer_id] for layer_id in sorted(field_map)
        },
        "query_failures": failures,
        "values": entries,
    }
    out_path = HERE / "datesopen_corpus.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    n_ok = sum(1 for e in entries if e["parse_ok"])
    print(f"wrote {out_path}: {len(entries)} distinct values, "
          f"{n_ok} parse_ok, {len(entries) - n_ok} failed, "
          f"{len(failures)} query failures", file=sys.stderr)


if __name__ == "__main__":
    main()
