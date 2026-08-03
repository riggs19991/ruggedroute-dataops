#!/usr/bin/env python3
"""BLM GTLF normalizer: GeoJSONSeq on stdin -> normalized GeoJSONSeq on stdout.

Source: BLM National Ground Transportation Linear Features, Public Display
service (gis.blm.gov .../transportation/BLM_Natl_GTLF_Public_Display/MapServer).
The workflow esridumps each motorized layer separately and pipes it through
this normalizer with per-layer hints:
  layer 0  Roads Managed for Public Motorized Use           --kind road  --designation-hint open
  layer 1  Roads Managed for Limited Public Motorized Use   --kind road  --designation-hint limited
  layer 2  Trails Managed for Public Motorized Use          --kind trail --designation-hint open
  layer 3  Trails Managed for Limited Public Motorized Use  --kind trail --designation-hint limited

Field names verified 2026-08-03 against .../MapServer/0?f=json:
GlobalID, OBJECTID, ROUTE_PRMRY_NM, PLAN_OHV_ROUTE_DSGNTN (observed values
"Open"/"Limited"), OHV_ROUTE_DSGNTN_LIM (e.g. "Limited by Other"),
OHV_DSGNTN_LIM_EXPLAIN (free text), PLAN_SEASON_RSTRCT_CODE ("YES"/"NO"),
OBSRVE_SRFCE_TYPE, GIS_MILES.

designation: explicit PLAN_OHV_ROUTE_DSGNTN wins when it maps cleanly to
open/limited/closed; missing or 'not assessed' falls back to the layer hint;
no hint -> 'unassessed'. Unrecognized designation strings go to the review
queue and also fall back to the hint.

source_id: GlobalID when present, else OBJECTID. OBJECTIDs are per-layer and
NOT stable across BLM republishes — the rte_cn-stability QA treats GTLF churn
as expected.

Season extraction: OHV_DSGNTN_LIM_EXPLAIN free text is run through the shared
season parser. Parsed windows -> seasons (cls "all" — the limitation applies
to the route, not a vehicle class). Non-empty unparsable text -> review queue
(deduped by (field, value) — identical boilerplate sentences repeat across
thousands of features and must not flood the artifact).

POLARITY TRAP (do not regress): parse_seasons emits OPEN windows, but live BLM
limitation text is overwhelmingly CLOSURE-phrased — 100/100 sampled date-bearing
OHV_DSGNTN_LIM_EXPLAIN values read like 'Closed 12/1- 4/15' or 'Closed 10/15 to
5/15', and 'Closed yearlong' would even parse to a full-year OPEN window via the
YEARLONG regex. Text matching CLOSURE_HINT therefore NEVER emits a seasons attr;
it goes to the review queue (field ohv_dsgntn_lim_explain_closure) instead. The
raw text still ships in limitation_text, and the seasonal attr (from
PLAN_SEASON_RSTRCT_CODE) is unaffected. The gate lives HERE in the adapter —
route_common.parse_seasons is byte-frozen (live MVUM tileset depends on it).

Usage:
  esri2geojson --jsonlines <layer-url> - \
    | python3 lib/normalize_gtlf.py --kind road --designation-hint open \
        --review-out review_queue_gtlf_0.jsonl > gtlf_0.geojsonl
"""
import argparse
import json
import re
import sys

from route_common import ReviewQueue, apply_passthrough, iter_features, lower_props, \
    parse_seasons, write_feature

SOURCE = "blm_gtlf"

# Closure-phrased limitation text must never become an OPEN season window (see
# the polarity-trap note in the module docstring). Word-boundary, case-insensitive;
# prohibit\w* covers prohibit/prohibits/prohibited/prohibition.
CLOSURE_HINT = re.compile(r"\b(?:clos(?:ed|es|ing|ures?)|prohibit\w*)\b", re.I)

PASSTHROUGH = {
    # source col (lowercase) -> normalized name
    "route_prmry_nm": "name",
    "obsrve_srfce_type": "surface",
    "ohv_route_dsgntn_lim": "limitation_type",
    "ohv_dsgntn_lim_explain": "limitation_text",
    "gis_miles": "miles",
}

DESIGNATION_MAP = {
    "open": "open",
    "limited": "limited",
    "closed": "closed",
}
UNASSESSED_VALUES = ("", "not assessed", "unassessed", "not evaluated", "unknown", "null", "<null>")


def pick_designation(raw_value, hint, review, source_id):
    s = "" if raw_value is None else str(raw_value).strip().lower()
    if s in DESIGNATION_MAP:
        return DESIGNATION_MAP[s]
    if s not in UNASSESSED_VALUES:
        review.add("plan_ohv_route_dsgntn", raw_value, example=source_id)
    return hint or "unassessed"


def normalize(feature, kind, hint, review):
    raw = lower_props(feature)
    source_id = raw.get("globalid") or raw.get("objectid")
    props = {"kind": kind, "source": SOURCE}
    if source_id not in (None, ""):
        props["source_id"] = str(source_id)
    props["designation"] = pick_designation(raw.get("plan_ohv_route_dsgntn"), hint,
                                            review, props.get("source_id"))
    apply_passthrough(props, raw, PASSTHROUGH)

    rstrct = str(raw.get("plan_season_rstrct_code") or "").strip().lower()
    if rstrct in ("yes", "y"):
        props["seasonal"] = "Seasonal"
    elif rstrct in ("no", "n"):
        props["seasonal"] = "Yearlong"

    lim_text = props.get("limitation_text")
    if lim_text:
        if CLOSURE_HINT.search(str(lim_text)):
            # Closure-phrased: any date range describes when the route is CLOSED,
            # so emitting it as an open window would invert legality. Queue for
            # human review instead (deduped, so boilerplate stays cheap).
            review.add("ohv_dsgntn_lim_explain_closure", lim_text,
                       example=props.get("source_id"))
        else:
            parsed, ok = parse_seasons(lim_text)
            if ok and parsed:
                props["seasons"] = json.dumps([{"cls": "all", **p} for p in parsed],
                                              separators=(",", ":"))
            elif not ok:
                review.add("ohv_dsgntn_lim_explain", lim_text, example=props.get("source_id"))

    if not props.get("source_id"):
        review.add("globalid", "<missing>", example={"name": props.get("name")})
    return props


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["road", "trail"], required=True)
    ap.add_argument("--designation-hint", choices=["open", "limited"], default=None,
                    help="fallback designation from which Public_Display layer this is")
    ap.add_argument("--review-out", default="review_queue_gtlf.jsonl")
    args = ap.parse_args()

    n_in = n_out = 0
    with ReviewQueue(args.review_out) as review:
        for f in iter_features(sys.stdin):
            n_in += 1
            write_feature(f, normalize(f, args.kind, args.designation_hint, review))
            n_out += 1
        n_review = review.occurrences

    print(f"normalize_gtlf[{args.kind}/{args.designation_hint}]: {n_in} in, {n_out} out, "
          f"{n_review} review-queue entries", file=sys.stderr)


if __name__ == "__main__":
    main()
