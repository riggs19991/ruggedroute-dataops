#!/usr/bin/env python3
"""RoadCore normalizer: GeoJSONSeq on stdin -> normalized GeoJSONSeq on stdout.

Source: USFS Trans_RoadCore_FS (EDW). This is the FULL National Forest road
inventory of all EXISTING roads (ROUTE_STATUS domain — decommissioned roads
are NOT included), administrative and closed roads included. It is
LEGALITY-AGNOSTIC: designation is 'unassessed' ALWAYS, and the client must
NEVER treat a roads_context feature as drivable. It exists purely as grey
context under the MVUM legality layer (master plan §6.1: roads_context renders
grey, never green).

Field names verified 2026-08-03 against the live companion service
https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_RoadBasic_01/MapServer/0?f=json:
rte_cn, id, name, symbol_code, symbol_name, jurisdiction, system, route_status,
oper_maint_level, objective_maint_level, functional_class, surface_type,
gis_miles, openforuseto, admin_org, managing_org.
(admin_org/managing_org are numeric org codes, not display names — deliberately
dropped to keep the huge tileset lean.)

Usage:
  ogr2ogr -f GeoJSONSeq /vsistdout/ RoadCore.gdb LAYER -t_srs EPSG:4326 \
    | python3 lib/normalize_roadcore.py --review-out review_queue_roadcore.jsonl \
    > roads_context.geojsonl
"""
import argparse
import sys

from route_common import ReviewQueue, apply_passthrough, iter_features, lower_props, write_feature

SOURCE = "usfs_roadcore"

PASSTHROUGH = {
    # source col (lowercase) -> normalized name
    "rte_cn": "source_id",
    "id": "route_no",
    "name": "name",
    "symbol_code": "symbol",
    "symbol_name": "symbol_name",
    "surface_type": "surface",
    "oper_maint_level": "maint_level",
    "objective_maint_level": "objective_maint_level",
    "openforuseto": "openforuseto",
    "route_status": "route_status",
    "jurisdiction": "jurisdiction",
    "gis_miles": "miles",
}


def normalize(feature, review):
    raw = lower_props(feature)
    # RoadCore is legality-agnostic: 'unassessed' ALWAYS (see module docstring).
    props = {"kind": "road", "source": SOURCE, "designation": "unassessed"}
    apply_passthrough(props, raw, PASSTHROUGH)
    if not props.get("source_id"):
        review.add("rte_cn", "<missing>",
                   example={"route_no": props.get("route_no"), "name": props.get("name")})
    return props


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review-out", default="review_queue_roadcore.jsonl")
    args = ap.parse_args()

    n_in = n_out = 0
    with ReviewQueue(args.review_out) as review:
        for f in iter_features(sys.stdin):
            n_in += 1
            write_feature(f, normalize(f, review))
            n_out += 1
        n_review = review.occurrences

    print(f"normalize_roadcore: {n_in} in, {n_out} out, {n_review} review-queue entries",
          file=sys.stderr)


if __name__ == "__main__":
    main()
