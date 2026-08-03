#!/usr/bin/env python3
"""NFS Trails normalizer: GeoJSONSeq on stdin -> normalized GeoJSONSeq on stdout.

Source: USFS Trans_Trail_NFS_Publish (EDW) — the full National Forest trail
system with per-mode managed-use columns. Stage 1 uses this two ways:
  1. A standalone nfs_trails tileset (no client layer yet — hiking overlay is a
     later stage).
  2. --attrs-out writes a compact sidecar JSON {trail_cn: {surface, trail_class}}
     that normalize_mvum.py --nfs-attrs joins onto MVUM trails (MVUM trail
     records often lack surface/trail_class).

Field names verified 2026-08-03 against
https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TrailNFSPublish_01/MapServer/0?f=json:
trail_cn (the stable CN key), trail_no, trail_name, trail_class, trail_surface,
terra_motorized / snow_motorized / water_motorized ('Y'/'N'/'N/A'), gis_miles,
and per-mode managed-use columns {mode}_managed which hold season-window
strings like "04/15-12/15" ("N/A" is the null sentinel — observed live).

Motorized-mode -> vehicle_flags mapping (motorized modes only; snowmobile,
snowcoach_snowcat and motor_watercraft have no slot in the 17-key
vehicle_flags vocabulary and are deliberately excluded — snow/water travel
modes are out of scope for the motorized road network):
  motorcycle_managed      -> moto
  atv_managed             -> atv_lt50
  fourwd_managed          -> fourwd_gt50
  e_bike_class1_managed   -> ebike1
  e_bike_class2_managed   -> ebike2
  e_bike_class3_managed   -> ebike3
A flag is set when its managed column carries a real value (not empty/N/A/'N');
the same string is parsed for season windows (failures -> review queue).

designation: 'open' when terra_motorized is affirmatively 'Y' (the trail is
managed for terra motorized use — same designation data that feeds MVUM),
otherwise 'unassessed'.

Usage:
  ogr2ogr -f GeoJSONSeq /vsistdout/ Trail.gdb LAYER -t_srs EPSG:4326 \
    | python3 lib/normalize_nfs_trails.py --review-out review_queue_nfs_trails.jsonl \
        [--attrs-out nfs_attrs.json] \
    > nfs_trails.geojsonl
"""
import argparse
import json
import sys

from route_common import ReviewQueue, apply_passthrough, iter_features, lower_props, \
    parse_seasons, truthy, write_feature

SOURCE = "usfs_nfs_trails"

# "N/A" is TrailNFSPublish's null sentinel (observed live 2026-08-03). The shared
# truthy() treats it as true (it is not an explicit no in MVUM-land), so managed
# columns get their own emptiness check here.
NA_SENTINELS = ("n/a", "na")

PASSTHROUGH = {
    # source col (lowercase) -> normalized name
    "trail_cn": "source_id",
    "trail_no": "route_no",
    "trail_name": "name",
    "trail_class": "trail_class",
    "trail_surface": "surface",
    "terra_motorized": "terra_motorized",
    "snow_motorized": "snow_motorized",
    "water_motorized": "water_motorized",
    "gis_miles": "miles",
}

MOTOR_MODES = {
    # vehicle_flags key -> managed-use season column (see module docstring)
    "moto": "motorcycle_managed",
    "atv_lt50": "atv_managed",
    "fourwd_gt50": "fourwd_managed",
    "ebike1": "e_bike_class1_managed",
    "ebike2": "e_bike_class2_managed",
    "ebike3": "e_bike_class3_managed",
}

YEARLONG_WINDOW = {"open": "01/01", "close": "12/31"}


def managed_value(raw, col):
    """Managed-use column value with the N/A sentinel collapsed to None."""
    v = raw.get(col)
    if v is None or str(v).strip().lower() in ("",) + NA_SENTINELS:
        return None
    return v


def normalize(feature, review):
    raw = lower_props(feature)
    props = {"kind": "trail", "source": SOURCE}
    terra = raw.get("terra_motorized")
    props["designation"] = "open" if str(terra).strip().lower() == "y" else "unassessed"
    apply_passthrough(props, raw, PASSTHROUGH)

    flags = {}
    seasons = []
    for flag, col in MOTOR_MODES.items():
        v = managed_value(raw, col)
        if v is None:
            continue
        if truthy(v):
            flags[flag] = 1
        parsed, ok = parse_seasons(v)
        if not ok:
            review.add(col, v, example=props.get("source_id"))
        for p in parsed:
            seasons.append({"cls": flag, **p})
    if flags:
        props["vehicle_flags"] = json.dumps(flags, separators=(",", ":"))
    if seasons:
        props["seasons"] = json.dumps(seasons, separators=(",", ":"))
        props["seasonal"] = "Yearlong" if all(
            {"open": s["open"], "close": s["close"]} == YEARLONG_WINDOW for s in seasons
        ) else "Seasonal"

    if not props.get("source_id"):
        review.add("trail_cn", "<missing>",
                   example={"route_no": props.get("route_no"), "name": props.get("name")})
    return props


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review-out", default="review_queue_nfs_trails.jsonl")
    ap.add_argument("--attrs-out", default=None,
                    help="also write a sidecar JSON {trail_cn: {surface, trail_class}} "
                         "for the MVUM enrichment join")
    args = ap.parse_args()

    attrs = {}
    n_in = n_out = 0
    with ReviewQueue(args.review_out) as review:
        for f in iter_features(sys.stdin):
            n_in += 1
            props = normalize(f, review)
            if args.attrs_out and props.get("source_id"):
                extra = {k: props[k] for k in ("surface", "trail_class") if props.get(k)}
                if extra:
                    attrs.setdefault(str(props["source_id"]), extra)
            write_feature(f, props)
            n_out += 1
        n_review = review.occurrences

    if args.attrs_out:
        with open(args.attrs_out, "w", encoding="utf-8") as fh:
            json.dump(attrs, fh, separators=(",", ":"))
        print(f"normalize_nfs_trails: wrote {len(attrs)} sidecar attr entries to {args.attrs_out}",
              file=sys.stderr)

    print(f"normalize_nfs_trails: {n_in} in, {n_out} out, {n_review} review-queue entries",
          file=sys.stderr)


if __name__ == "__main__":
    main()
