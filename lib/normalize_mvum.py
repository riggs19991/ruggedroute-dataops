#!/usr/bin/env python3
"""MVUM normalizer: GeoJSONSeq on stdin -> normalized GeoJSONSeq on stdout.

Thin adapter over route_common (shared season parser / review queue / stream
helpers). The emitted feature schema is byte-identical to the Stage-0
standalone implementation — the live mvum tileset and the Android client
depend on it (see test_mvum_adapter.py golden fixtures).

Tolerant by design: any unparsable season string is preserved raw and logged
to the review queue — this process must NEVER crash on bad upstream data
(documented USFS typos).

Usage:
  ogr2ogr -f GeoJSONSeq /vsistdout/ X.gdb LAYER -t_srs EPSG:4326 \
    | python3 lib/normalize_mvum.py --kind road --review-out review_queue_road.jsonl \
        [--nfs-attrs nfs_attrs.json] \
    > mvum_roads.geojsonl

--nfs-attrs (optional): sidecar JSON {trail_cn: {surface, trail_class}} produced
by normalize_nfs_trails.py --attrs-out. For trail features whose source_id (a
CN) matches, missing surface/trail_class are filled in from the richer NFS
Trails dataset. Absent flag/file -> behavior identical to today.
"""
import argparse
import json
import sys

from route_common import (ReviewQueue, apply_passthrough, iter_features,
                          lower_props, parse_seasons, truthy, write_feature)

# Re-exported for existing tests/tools: parse_seasons and truthy are part of
# this module's public surface even though they live in route_common now.
__all__ = ["parse_seasons", "truthy", "VEHICLE_COLS", "PASSTHROUGH", "main"]

# Vehicle-class columns (EDW MVUM schema; matched case-insensitively). Each pairs with
# a season string column — usually <col>_datesopen. Keys are our normalized flag names.
VEHICLE_COLS = {
    "highway_legal": "passengervehicle",
    "high_clearance": "highclearancevehicle",
    "truck": "truck",
    "bus": "bus",
    "motorhome": "motorhome",
    "fourwd_gt50": "fourwd_gt50inches",
    "twowd_gt50": "twowd_gt50inches",
    "sxs_utv": "other_ohv_gt50inches",
    "atv_lt50": "atv",
    "moto": "motorcycle",
    "tracked_gt50": "tracked_ohv_gt50inches",
    "tracked_lt50": "tracked_ohv_lt50inches",
    "other_lt50": "other_ohv_lt50inches",
    "otherwheeled": "otherwheeled_ohv",
    "ebike1": "e_bike_class1",
    "ebike2": "e_bike_class2",
    "ebike3": "e_bike_class3",
}

# The real EDW data does NOT always name the season column <flag col>_datesopen:
# the gt50/lt50 columns DROP "inches" in their season variant, and the e-bike
# season columns are *_dur (verified against live EDW_MVUM_01 2026-08-03; see
# lib/fixtures/datesopen_corpus.json field_resolution). Without these fallbacks
# 9 of 17 vehicle classes silently lose ALL season data. First non-empty
# candidate wins; the documented name stays first for backward compatibility.
SEASON_FIELD_CANDIDATES = {
    "fourwd_gt50inches": ["fourwd_gt50inches_datesopen", "fourwd_gt50_datesopen"],
    "twowd_gt50inches": ["twowd_gt50inches_datesopen", "twowd_gt50_datesopen"],
    "other_ohv_gt50inches": ["other_ohv_gt50inches_datesopen", "other_ohv_gt50_datesopen"],
    "tracked_ohv_gt50inches": ["tracked_ohv_gt50inches_datesopen", "tracked_ohv_gt50_datesopen"],
    "tracked_ohv_lt50inches": ["tracked_ohv_lt50inches_datesopen", "tracked_ohv_lt50_datesopen"],
    "other_ohv_lt50inches": ["other_ohv_lt50inches_datesopen", "other_ohv_lt50_datesopen"],
    "e_bike_class1": ["e_bike_class1_datesopen", "e_bike_class1_dur"],
    "e_bike_class2": ["e_bike_class2_datesopen", "e_bike_class2_dur"],
    "e_bike_class3": ["e_bike_class3_datesopen", "e_bike_class3_dur"],
}

PASSTHROUGH = {
    # source col (lowercase) -> normalized name
    "rte_cn": "source_id",
    "id": "route_no",
    "name": "name",
    "forestname": "forest",
    "districtname": "district",
    "surfacetype": "surface",
    "seasonal": "seasonal",
    "symbol": "symbol",
    "mvum_symbol_name": "symbol_name",
    "sbs_symbol_name": "symbol_name",
    "gis_miles": "miles",
    "routestatus": "route_status",
    "trailstatus": "route_status",
    "jurisdiction": "jurisdiction",
    # The real bulk GDB and live EDW spell these OPERATIONALMAINTLEVEL and
    # TRAILCLASS (verified 2026-08-03 against EDW_MVUM_01 layers 1/2). The
    # underscored keys never occur upstream today but are kept as harmless
    # future-proofing. ADDITIVE schema change only: inputs without the new
    # spellings emit byte-identical output (test_mvum_adapter.py).
    "oper_maint_level": "maint_level",
    "operationalmaintlevel": "maint_level",
    "trail_class": "trail_class",
    "trailclass": "trail_class",
}


def season_text(raw, col):
    """Season string for a vehicle-class column, trying the documented
    <col>_datesopen name first, then the real-world EDW variants."""
    for cand in ([col + "_datesopen"] + SEASON_FIELD_CANDIDATES.get(col, [])):
        v = raw.get(cand)
        if v not in (None, ""):
            return v
    return None


def load_nfs_attrs(path):
    """Tolerant sidecar load: missing/corrupt file -> warn + no enrichment."""
    if not path:
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("sidecar is not a JSON object")
        return data
    except (OSError, ValueError) as e:
        print(f"::warning::normalize_mvum: cannot load --nfs-attrs {path} ({e}); "
              "proceeding unenriched", file=sys.stderr)
        return {}


def normalize(feature, kind, review, nfs_attrs=None):
    """Build normalized properties for one feature (mutates + returns props)."""
    raw = lower_props(feature)
    props = {"kind": kind, "source": "usfs_mvum"}
    apply_passthrough(props, raw, PASSTHROUGH)

    # NFS Trails enrichment: trails only, fill MISSING attrs only.
    if kind == "trail" and nfs_attrs:
        extra = nfs_attrs.get(str(props.get("source_id")))
        if isinstance(extra, dict):
            for key in ("surface", "trail_class"):
                if key not in props and extra.get(key) not in (None, ""):
                    props[key] = extra[key]

    flags = {}
    seasons = []
    for flag, col in VEHICLE_COLS.items():
        if truthy(raw.get(col)):
            flags[flag] = 1
        stext = season_text(raw, col)
        parsed, ok = parse_seasons(stext)
        if not ok:
            review.add(col + "_datesopen", stext, example=props.get("source_id"))
        for p in parsed:
            seasons.append({"cls": flag, **p})
    if flags:
        props["vehicle_flags"] = json.dumps(flags, separators=(",", ":"))
    if seasons:
        props["seasons"] = json.dumps(seasons, separators=(",", ":"))

    if not props.get("source_id"):
        review.add("rte_cn", "<missing>",
                   example={"route_no": props.get("route_no"), "name": props.get("name")})
    return props


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["road", "trail"], required=True)
    ap.add_argument("--review-out", default="review_queue.jsonl")
    ap.add_argument("--nfs-attrs", default=None,
                    help="optional NFS Trails sidecar JSON for trail enrichment")
    args = ap.parse_args()

    nfs_attrs = load_nfs_attrs(args.nfs_attrs)
    n_in = n_out = 0
    with ReviewQueue(args.review_out) as review:
        for f in iter_features(sys.stdin):
            n_in += 1
            props = normalize(f, args.kind, review, nfs_attrs)
            write_feature(f, props)
            n_out += 1
        n_review = review.occurrences

    print(f"normalize_mvum[{args.kind}]: {n_in} in, {n_out} out, {n_review} review-queue entries",
          file=sys.stderr)


if __name__ == "__main__":
    main()
