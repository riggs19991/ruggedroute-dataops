#!/usr/bin/env python3
"""NPS Public Roads normalizer: GeoJSONSeq on stdin -> normalized GeoJSONSeq on stdout.

Source: NPS_Public_Roads FeatureServer, layer 0 "Roads"
(https://mapservices.nps.gov/arcgis/rest/services/NationalDatasets/NPS_Public_Roads/FeatureServer/0).

Field names verified 2026-08-03 via ?f=json: OBJECTID, RDNAME, MAPLABEL,
RDSTATUS, RDCLASS, RDSURFACE, SEASONAL ("Yes"/"No"/"Unknown"), SEASDESC,
RDHICLEAR, RTENUMBER, RDMAINTAINER, UNITCODE, UNITNAME, OPENTOPUBLIC (null on
every live record today), ROUTEID, GEOMETRYID, FEATUREID.

designation: 'open' ONLY when OPENTOPUBLIC is an explicit yes — the dataset is
a road INVENTORY, not an OHV designation system, and 36 CFR 4.10 makes OHV
rules per-park. Everything else is 'unassessed'; we never fabricate legality.
(In practice OPENTOPUBLIC is null service-wide today, so expect 'unassessed'.)

source_id: GEOMETRYID (GUID, populated on every sampled record), falling back
to FEATUREID then OBJECTID. RDCLASS is kept as `road_class` (it is an
inventory class — Primary/Secondary/Local — not a trail_class). Values equal
to "Unknown" on road_class/surface/hiclear/seasonal are dropped rather than
baked into tiles. No miles field exists (Shape__Length is projected meters,
deliberately not mapped). SEASDESC free text goes through the shared season
parser; unparsable non-empty text lands in the review queue.

POLARITY TRAP (same as BLM GTLF limitation text): parse_seasons emits OPEN
windows, but SEASDESC is often CLOSURE-phrased ('Closed 11/15-05/15'), which
would invert legality if the date range shipped as an open window. SEASDESC
matching CLOSURE_HINT with no affirmative OPEN_HINT ('...closed in winter;
open 05/01-11/01' keeps its seasons) never emits a seasons attr — it goes to
the review queue (field seasdesc_closure) instead. The gate lives HERE in the
adapter — route_common.parse_seasons is byte-frozen.

Usage:
  esri2geojson --jsonlines <layer-url> - \
    | python3 lib/normalize_nps_roads.py --review-out review_queue_nps.jsonl \
    > nps_roads.geojsonl
"""
import argparse
import json
import re
import sys

from route_common import ReviewQueue, iter_features, lower_props, parse_seasons, write_feature

SOURCE = "nps_roads"

# Season-polarity gate (see the polarity-trap note in the module docstring):
# closure-phrased SEASDESC with no affirmative open language never becomes an
# OPEN season window. Word-boundary, case-insensitive.
CLOSURE_HINT = re.compile(r"\b(?:clos(?:ed|es|ing|ures?)|prohibit\w*)\b", re.I)
OPEN_HINT = re.compile(r"\b(?:open|opens|opened)\b", re.I)

PASSTHROUGH = {
    # source col (lowercase) -> normalized name; applied with Unknown-dropping below
    "rdname": "name",
    "rtenumber": "route_no",
    "rdclass": "road_class",
    "rdsurface": "surface",
    "rdstatus": "route_status",
    "rdhiclear": "hiclear",
    "rdmaintainer": "manager",
    "unitcode": "unit",
    "unitname": "unit_name",
}

DROP_UNKNOWN = {"road_class", "surface", "hiclear"}


def normalize(feature, review):
    raw = lower_props(feature)
    props = {"kind": "road", "source": SOURCE}

    source_id = raw.get("geometryid") or raw.get("featureid") or raw.get("objectid")
    if source_id not in (None, ""):
        props["source_id"] = str(source_id)

    otp = str(raw.get("opentopublic") or "").strip().lower()
    props["designation"] = "open" if otp in ("yes", "y", "true", "1") else "unassessed"

    for src, dst in PASSTHROUGH.items():
        v = raw.get(src)
        if v in (None, ""):
            continue
        if dst in DROP_UNKNOWN and str(v).strip().lower() == "unknown":
            continue
        props[dst] = v
    if not props.get("name"):
        label = str(raw.get("maplabel") or "").strip()
        if label:
            props["name"] = label

    seasonal = str(raw.get("seasonal") or "").strip().lower()
    if seasonal == "yes":
        props["seasonal"] = "Seasonal"
    elif seasonal == "no":
        props["seasonal"] = "Yearlong"

    seasdesc = raw.get("seasdesc")
    if seasdesc not in (None, ""):
        s = str(seasdesc)
        if CLOSURE_HINT.search(s) and not OPEN_HINT.search(s):
            # Closure-phrased with no affirmative open language: the date range
            # describes when the road is CLOSED — emitting it as an open window
            # would invert legality. Queue for human review instead.
            review.add("seasdesc_closure", seasdesc, example=props.get("source_id"))
        else:
            parsed, ok = parse_seasons(seasdesc)
            if ok and parsed:
                props["seasons"] = json.dumps([{"cls": "all", **p} for p in parsed],
                                              separators=(",", ":"))
            elif not ok:
                review.add("seasdesc", seasdesc, example=props.get("source_id"))

    if not props.get("source_id"):
        review.add("geometryid", "<missing>", example={"name": props.get("name")})
    return props


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review-out", default="review_queue_nps_roads.jsonl")
    args = ap.parse_args()

    n_in = n_out = 0
    with ReviewQueue(args.review_out) as review:
        for f in iter_features(sys.stdin):
            n_in += 1
            write_feature(f, normalize(f, review))
            n_out += 1
        n_review = review.occurrences

    print(f"normalize_nps_roads: {n_in} in, {n_out} out, {n_review} review-queue entries",
          file=sys.stderr)


if __name__ == "__main__":
    main()
