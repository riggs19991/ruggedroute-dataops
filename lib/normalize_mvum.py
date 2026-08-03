#!/usr/bin/env python3
"""MVUM normalizer: GeoJSONSeq on stdin -> normalized GeoJSONSeq on stdout.

Implements the normalized route schema from the master plan (§3). Tolerant by design:
any unparsable season string is preserved raw and logged to the review queue —
this process must NEVER crash on bad upstream data (documented USFS typos).

Usage:
  ogr2ogr -f GeoJSONSeq /vsistdout/ X.gdb LAYER -t_srs EPSG:4326 \
    | python3 lib/normalize_mvum.py --kind road --review-out review_queue_road.jsonl \
    > mvum_roads.geojsonl
"""
import argparse
import json
import re
import sys

# Vehicle-class columns (EDW MVUM schema; matched case-insensitively). Each pairs with
# a <col>_datesopen season string. Keys are our normalized flag names.
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
    "oper_maint_level": "maint_level",
    "trail_class": "trail_class",
}

DATE_RANGE = re.compile(r"(\d{1,2})\s*/\s*(\d{1,2})\s*(?:-|–|to|thru|through)\s*(\d{1,2})\s*/\s*(\d{1,2})", re.I)
YEARLONG = re.compile(r"year\s*-?\s*long|yearround|year\s*round|all\s*year|01/01\s*-\s*12/31", re.I)


def parse_seasons(text):
    """Return (seasons_list, ok). seasons_list = [{open,close}] mm/dd zero-padded.
    ok=False means text was non-empty but nothing parseable was found."""
    if not text or not str(text).strip():
        return [], True
    s = str(text).strip()
    if YEARLONG.search(s):
        return [{"open": "01/01", "close": "12/31"}], True
    out = []
    for m in DATE_RANGE.finditer(s):
        mo1, d1, mo2, d2 = (int(g) for g in m.groups())
        if 1 <= mo1 <= 12 and 1 <= d1 <= 31 and 1 <= mo2 <= 12 and 1 <= d2 <= 31:
            out.append({"open": f"{mo1:02d}/{d1:02d}", "close": f"{mo2:02d}/{d2:02d}"})
    return out, bool(out)


def truthy(v):
    """A vehicle class is allowed if its column is non-empty and not an explicit no."""
    if v is None:
        return False
    s = str(v).strip().lower()
    return s not in ("", "n", "no", "null", "none", "0")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["road", "trail"], required=True)
    ap.add_argument("--review-out", default="review_queue.jsonl")
    args = ap.parse_args()

    n_in = n_out = n_review = 0
    with open(args.review_out, "w", encoding="utf-8") as review:
        for line in sys.stdin:
            line = line.strip().rstrip(",")
            if not line or line in ("[", "]"):
                continue
            try:
                f = json.loads(line)
            except json.JSONDecodeError:
                continue
            if f.get("type") != "Feature":
                continue
            n_in += 1
            raw = {str(k).lower(): v for k, v in (f.get("properties") or {}).items()}
            props = {"kind": args.kind, "source": "usfs_mvum"}
            for src, dst in PASSTHROUGH.items():
                if raw.get(src) not in (None, ""):
                    props[dst] = raw[src]

            flags = {}
            seasons = []
            for flag, col in VEHICLE_COLS.items():
                allowed = truthy(raw.get(col))
                if allowed:
                    flags[flag] = 1
                stext = raw.get(col + "_datesopen")
                parsed, ok = parse_seasons(stext)
                if not ok:
                    n_review += 1
                    review.write(json.dumps({
                        "source_id": props.get("source_id"),
                        "route_no": props.get("route_no"),
                        "forest": props.get("forest"),
                        "field": col + "_datesopen",
                        "value": stext,
                    }) + "\n")
                for p in parsed:
                    seasons.append({"cls": flag, **p})
            if flags:
                props["vehicle_flags"] = json.dumps(flags, separators=(",", ":"))
            if seasons:
                props["seasons"] = json.dumps(seasons, separators=(",", ":"))

            if not props.get("source_id"):
                n_review += 1
                review.write(json.dumps({"error": "missing rte_cn", "route_no": props.get("route_no"),
                                         "name": props.get("name")}) + "\n")

            f["properties"] = props
            sys.stdout.write(json.dumps(f, separators=(",", ":")) + "\n")
            n_out += 1

    print(f"normalize_mvum[{args.kind}]: {n_in} in, {n_out} out, {n_review} review-queue entries",
          file=sys.stderr)


if __name__ == "__main__":
    main()
