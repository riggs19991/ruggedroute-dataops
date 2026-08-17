#!/usr/bin/env python3
"""D1b roads_tnm normalizer: TNM per-state FileGDB -> four whitelisted GeoJSONSeq files.

Source: USGS The National Map, National Transportation Dataset, per-state
FileGDB (Trans_RoadSegment + Trans_TrailSegment; EPSG:4269 measured lines).
Field names below are the PHYSICAL FGDB names, verified 2026-08-16 against
AK/DE/VT/WY on disk (identical schema) — never the MapServer aliases.

Output props are built FRESH from an explicit mapping (whitelist by
construction — parcels precedent); qa_roads_tnm.py re-verifies the same
whitelist on the files and on decoded tiles.

    class      interstate|us_hwy|state_hwy|local_conn|local|ramp|fourwd|closed|trail
    name       as published (optional)
    ref        'I-80;US-30', 'US-13 Bus', 'SR-89A', fallback 'FR-548.3' / 'CR-71' (optional)
    mtfcc      Census MTFCC verbatim, roads only (optional)
    source     originator code tiger|usfs|nps|akdot|other
    source_id  permanent_identifier, braces stripped, lower-cased
    miles      geodesic length (SHAPE_Length upstream is DEGREES); trails use lengthmiles

Classing is DESIGNATION-FIRST (layer.json 'classing'): riders read shields.
DE carries US-13 freeway rows at tnmfrc 1 with no interstate value; WY has
I-180 at tnmfrc 2 and 684 business-loop rows on tnmfrc 2/3 — a tnmfrc-first
rule mislabels all of them. tnmfrc only breaks ties.

Each feature also gets a per-feature `tippecanoe.minzoom` by class so the
low zooms carry a deterministic hierarchy (interstates z5 … local z10) instead
of the drop-densest lottery.

Input handling
--------------
--src PATH          the per-state zip (read IN PLACE via /vsizip/ — TX/CA
                    inflate ~2.9x, never unzip on a 14 GB runner) or a .gdb
                    dir; both layers are streamed through ogr2ogr.
--roads-src F.geojsonl / --trails-src F.geojsonl
                    already-EPSG:4326 GeoJSONSeq (tests, or a manual dump);
                    read directly, no GDAL needed.

Usage:
    normalize_roads_tnm.py --unit ID --src src/ID_1.zip --out build/
Writes build/{roads_hwy,roads_local,roads_4wd,trails_tnm}.geojsonl +
build/normalize_stats.json. Exits non-zero if zero roads were kept.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

WHITELIST = ("class", "name", "ref", "mtfcc", "source", "source_id", "miles")

CLASSES = ("interstate", "us_hwy", "state_hwy", "local_conn", "local",
           "ramp", "fourwd", "closed", "trail")

# class -> (source layer, per-feature minzoom). Contract with layer.json +
# both clients; the low-zoom hierarchy lives HERE, not in tippecanoe flags.
LAYER_OF = {
    "interstate": "roads_hwy", "us_hwy": "roads_hwy", "state_hwy": "roads_hwy", "ramp": "roads_hwy",
    "local_conn": "roads_local", "local": "roads_local",
    "fourwd": "roads_4wd", "closed": "roads_4wd",
    "trail": "trails_tnm",
}
MINZOOM = {
    "interstate": 5, "us_hwy": 6, "state_hwy": 7, "local_conn": 8,
    "fourwd": 9, "trail": 9, "ramp": 10, "local": 10, "closed": 10,
}
LAYERS = ("roads_hwy", "roads_local", "roads_4wd", "trails_tnm")

ROADS_LAYER = "Trans_RoadSegment"
TRAILS_LAYER = "Trans_TrailSegment"

# Verified originator vocabulary (roads: exactly these 5 nationally; trails
# have ~62 originators -> substring match, unknowns become 'other').
ORIGINATOR_SUBSTRINGS = (
    ("census bureau", "tiger"),
    ("forest service", "usfs"),
    ("national park service", "nps"),
    ("alaska dept", "akdot"),
)
KNOWN_MODIFIERS = {"bus": "Bus", "alt": "Alt", "byp": "Byp"}   # verified on 4 states
FUSED_MODIFIER = re.compile(r"^([A-Za-z]+)\.(\S+)$")            # 'Alt.10'
MAX_REF_PARTS = 4
MAX_NAME_LEN = 120


class Review:
    """Deduped review queue: one line per (field, value) with a running count."""

    def __init__(self) -> None:
        self.entries: dict[tuple[str, str], int] = {}

    def add(self, field: str, value) -> None:
        key = (field, "" if value is None else str(value)[:200])
        self.entries[key] = self.entries.get(key, 0) + 1

    def write(self, path: Path) -> None:
        with path.open("w", encoding="utf-8") as fh:
            for (field, value), n in sorted(self.entries.items()):
                fh.write(json.dumps({"field": field, "value": value, "count": n}) + "\n")


# ── value helpers ─────────────────────────────────────────────────────────────

def clean(value) -> str | None:
    """None for null-ish attribute values (None, '', 'null', '<Null>', whitespace)."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in ("null", "none", "<null>", "nan"):
        return None
    return text


def to_int(value) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def parse_route(value, review: Review | None = None) -> list[tuple[str, str | None]]:
    """'Bus,13' -> [('13','Bus')]; '13,40' -> [('13',None),('40',None)];
    'Alt.10' -> [('10','Alt')]; '89A' -> [('89A',None)].

    Modifier tokens (no digit) PRECEDE their number — verified on AK/DE/VT/WY.
    Any alphabetic token outside the verified {Bus,Alt,Byp} vocabulary is still
    honoured as a modifier (title-cased) and logged to the review queue."""
    text = clean(value)
    if not text:
        return []
    out: list[tuple[str, str | None]] = []
    pending: str | None = None
    for tok in (t.strip() for t in text.split(",")):
        if not tok:
            continue
        m = FUSED_MODIFIER.match(tok)
        if m and not any(ch.isdigit() for ch in m.group(1)):
            out.append((m.group(2), _modifier(m.group(1), review)))
            pending = None
            continue
        if not any(ch.isdigit() for ch in tok):
            pending = _modifier(tok, review)
            continue
        out.append((tok, pending))
        pending = None
    if pending is not None and review is not None:
        review.add("route_modifier_dangling", text)
    return out


def _modifier(tok: str, review: Review | None) -> str:
    low = tok.lower().rstrip(".")
    if low in KNOWN_MODIFIERS:
        return KNOWN_MODIFIERS[low]
    if review is not None:
        review.add("route_modifier_unknown", tok)
    return tok.title()


def originator_code(value) -> str:
    text = (clean(value) or "").lower()
    for needle, code in ORIGINATOR_SUBSTRINGS:
        if needle in text:
            return code
    return "other"


def source_id(value) -> str | None:
    text = clean(value)
    if not text:
        return None
    return text.strip("{}").lower()


def haversine_miles(geometry: dict | None) -> float:
    """Geodesic-enough length of a (Multi)LineString in EPSG:4326, statute miles."""
    if not geometry:
        return 0.0
    gtype = geometry.get("type")
    coords = geometry.get("coordinates") or []
    if gtype == "LineString":
        lines = [coords]
    elif gtype == "MultiLineString":
        lines = coords
    else:
        return 0.0
    r_miles = 3958.7613
    total = 0.0
    for line in lines:
        for (lon1, lat1, *_), (lon2, lat2, *_) in zip(line, line[1:]):
            p1, p2 = math.radians(lat1), math.radians(lat2)
            dphi = p2 - p1
            dlmb = math.radians(lon2 - lon1)
            a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
            total += 2 * r_miles * math.asin(math.sqrt(a))
    return total


def round_miles(miles: float) -> float | None:
    if miles <= 0:
        return None
    return max(round(miles, 2), 0.01)


COORD_DECIMALS = 6   # 0.11 m — far below z14 tile resolution (~0.6 m); halves geojsonl bytes


def round_geometry(geometry: dict) -> dict:
    """Round every coordinate to COORD_DECIMALS (ogr2ogr emits 15 digits by default).
    Pure disk/pipe optimisation: TX/CA geojsonl must fit next to tippecanoe temp on a 14 GB runner."""
    def rnd(node):
        if isinstance(node, (int, float)):
            return round(node, COORD_DECIMALS)
        return [rnd(n) for n in node]
    return {"type": geometry.get("type"), "coordinates": rnd(geometry.get("coordinates") or [])}


# ── classing ──────────────────────────────────────────────────────────────────

def classify(tnmfrc, mtfcc, interstate, us_route, state_route) -> str | None:
    """layer.json 'classing.rules_ordered' — first match wins; None = DROP."""
    frc = to_int(tnmfrc)
    if frc == 7:                       # ferry (mtfcc L4165)
        return None
    if frc == 5:
        return "ramp"
    if frc == 6:
        return "fourwd"
    if frc == 9:                       # domain code, zero rows anywhere today
        return "closed"
    if frc in (1, 2, 3, 8):
        i_parts = parse_route(interstate)
        if any(mod is None for _, mod in i_parts):
            return "interstate"        # mainline shield present
        if parse_route(us_route):
            return "us_hwy"
        if parse_route(state_route):
            return "state_hwy"
        if i_parts:
            return "state_hwy"         # interstate BUSINESS loop only ('Bus,25')
        if frc == 1:
            return "interstate"        # unsigned controlled-access
        if frc == 8:                   # tunnel inherits by mtfcc
            m = clean(mtfcc)
            if m == "S1100":
                return "interstate"
            if m == "S1200":
                return "local_conn"
            return "local"
        return "local_conn"            # tnmfrc 2/3 undesignated
    return "local"                     # 4, 99, NULL, anything else


def build_ref(cls: str, interstate, us_route, state_route,
              federal_lands_route, county_route, review: Review | None = None) -> str | None:
    parts: list[str] = []
    for prefix, value in (("I", interstate), ("US", us_route), ("SR", state_route)):
        for num, mod in parse_route(value, review):
            parts.append(f"{prefix}-{num}" + (f" {mod}" if mod else ""))
    seen: list[str] = []
    for p in parts:
        if p not in seen:
            seen.append(p)
    parts = seen[:MAX_REF_PARTS]
    if not parts and cls in ("fourwd", "local", "local_conn", "closed"):
        flr = clean(federal_lands_route)
        cr = clean(county_route)
        if flr:
            parts = [f"FR-{flr}"]
        elif cr:
            parts = [f"CR-{cr}"]
    return ";".join(parts) if parts else None


def name_of(*values) -> str | None:
    for v in values:
        text = clean(v)
        if text:
            return text[:MAX_NAME_LEN]
    return None


# ── per-feature builders (the enforcement points) ─────────────────────────────

def road_props(raw: dict, geometry: dict | None, review: Review) -> dict | None:
    """Fresh whitelisted props for a Trans_RoadSegment row (lower-cased keys), or None to drop."""
    cls = classify(raw.get("tnmfrc"), raw.get("mtfcc_code"), raw.get("interstate"),
                   raw.get("us_route"), raw.get("state_route"))
    if cls is None:
        return None
    props: dict = {"class": cls}
    name = name_of(raw.get("name"))
    if name:
        props["name"] = name
    ref = build_ref(cls, raw.get("interstate"), raw.get("us_route"), raw.get("state_route"),
                    raw.get("federal_lands_route"), raw.get("county_route"), review)
    if ref:
        props["ref"] = ref
    mtfcc = clean(raw.get("mtfcc_code"))
    if mtfcc:
        props["mtfcc"] = mtfcc
    src = originator_code(raw.get("source_originator"))
    if src == "other":
        review.add("road_originator_other", raw.get("source_originator"))
    props["source"] = src
    sid = source_id(raw.get("permanent_identifier"))
    if sid:
        props["source_id"] = sid
    else:
        review.add("permanent_identifier", "<missing>")
    miles = round_miles(haversine_miles(geometry))
    if miles is not None:
        props["miles"] = miles
    return props


def trail_props(raw: dict, geometry: dict | None, review: Review) -> dict | None:
    """Fresh whitelisted props for a Trans_TrailSegment row, or None to drop (snow/water)."""
    ttype = (clean(raw.get("trailtype")) or "").lower()
    if ttype in ("snow trail", "water trail"):
        return None
    props: dict = {"class": "trail"}
    name = name_of(raw.get("name"), raw.get("maplabel"))
    if name:
        props["name"] = name
    ref = clean(raw.get("trailnumber"))
    if ref:
        props["ref"] = ref[:40]
    props["source"] = originator_code(raw.get("sourceoriginator"))
    sid = source_id(raw.get("permanentidentifier"))
    if sid:
        props["source_id"] = sid
    else:
        review.add("permanentidentifier", "<missing>")
    miles = None
    try:
        lm = float(raw.get("lengthmiles"))
        if lm > 0:
            miles = round_miles(lm)
    except (TypeError, ValueError):
        pass
    if miles is None:
        miles = round_miles(haversine_miles(geometry))
    if miles is not None:
        props["miles"] = miles
    return props


# ── input plumbing ────────────────────────────────────────────────────────────

def resolve_src(src: str) -> str:
    """OGR-openable path; zips go through /vsizip/ WITHOUT extraction."""
    if not src.lower().endswith(".zip"):
        return src
    names = zipfile.ZipFile(src).namelist()
    gdb_dirs = sorted({n.split(".gdb/")[0] + ".gdb" for n in names if ".gdb/" in n})
    posix = Path(src).as_posix()
    if gdb_dirs:
        return f"/vsizip/{posix}/{gdb_dirs[0]}"
    return f"/vsizip/{posix}"


def ogr_stream(ogr_src: str, layer: str, err_path: Path) -> subprocess.Popen:
    """ogr2ogr GeoJSONSeq stream. stderr goes to a FILE, never a pipe: a chatty
    driver (one warning per feature) fills a 64 KB stderr pipe while we are
    blocked reading stdout — classic two-pipe deadlock."""
    # COORDINATE_PRECISION=7 shrinks the pipe (default is 15 digits); the writer
    # rounds again to COORD_DECIMALS so the on-disk contract is one place.
    cmd = ["ogr2ogr", "-f", "GeoJSONSeq", "/vsistdout/", ogr_src, layer,
           "-t_srs", "EPSG:4326", "-dim", "XY", "-nlt", "PROMOTE_TO_MULTI",
           "-lco", "COORDINATE_PRECISION=7"]
    err_fh = err_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=err_fh,
                            text=True, encoding="utf-8", errors="replace", bufsize=1)
    proc._rr_err = (err_fh, err_path)  # type: ignore[attr-defined]
    return proc


def finish(proc: subprocess.Popen) -> tuple[int, str]:
    rc = proc.wait()
    err_fh, err_path = proc._rr_err  # type: ignore[attr-defined]
    err_fh.close()
    try:
        err = err_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        err = ""
    return rc, err


def iter_geojsonl(stream):
    for line in stream:
        line = line.strip().lstrip("\x1e").rstrip(",")
        if not line or line in ("[", "]"):
            continue
        try:
            feature = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(feature, dict) and feature.get("type") == "Feature":
            yield feature


def extract_gdb(zip_path: str, dest: Path) -> str:
    """Fallback only: unzip just the .gdb directory (runner GDAL refusing /vsizip/)."""
    with zipfile.ZipFile(zip_path) as zf:
        members = [n for n in zf.namelist() if ".gdb/" in n]
        zf.extractall(dest, members)
    hits = sorted(p for p in dest.rglob("*.gdb") if p.is_dir())
    if not hits:
        sys.exit(f"no .gdb directory inside {zip_path}")
    return str(hits[0])


# ── the loop ──────────────────────────────────────────────────────────────────

class Writer:
    def __init__(self, out_dir: Path):
        self.files = {layer: (out_dir / f"{layer}.geojsonl").open("w", encoding="utf-8")
                      for layer in LAYERS}
        self.counts = {layer: 0 for layer in LAYERS}
        self.by_class = {c: 0 for c in CLASSES}

    def write(self, feature: dict, props: dict) -> None:
        cls = props["class"]
        layer = LAYER_OF[cls]
        rec = {"type": "Feature",
               "tippecanoe": {"minzoom": MINZOOM[cls]},
               "properties": props,
               "geometry": round_geometry(feature["geometry"])}
        self.files[layer].write(json.dumps(rec, separators=(",", ":")) + "\n")
        self.counts[layer] += 1
        self.by_class[cls] += 1

    def close(self) -> None:
        for fh in self.files.values():
            fh.close()


def process(features, builder, writer: Writer, review: Review, stats: dict, key: str) -> None:
    n_in = kept = dropped_geom = dropped_rule = 0
    hist: dict[str, int] = {}
    for feature in features:
        n_in += 1
        geom = feature.get("geometry")
        if not geom or not geom.get("coordinates"):
            dropped_geom += 1
            continue
        raw = {str(k).lower(): v for k, v in (feature.get("properties") or {}).items()}
        if key == "roads":
            h = str(to_int(raw.get("tnmfrc")))
            hist[h] = hist.get(h, 0) + 1
        else:
            h = clean(raw.get("trailtype")) or "<null>"
            hist[h] = hist.get(h, 0) + 1
        props = builder(raw, geom, review)
        if props is None:
            dropped_rule += 1
            continue
        writer.write(feature, props)
        kept += 1
    stats[key] = {"in": n_in, "kept": kept, "dropped_empty_geometry": dropped_geom,
                  "dropped_by_rule": dropped_rule,
                  ("tnmfrc_hist" if key == "roads" else "trailtype_hist"): hist}


def run_layer(ogr_src: str, layer: str, builder, writer, review, stats, key,
              zip_path: str | None, out_dir: Path) -> None:
    err_path = out_dir / f"ogr2ogr_{key}.stderr"
    proc = ogr_stream(ogr_src, layer, err_path)
    assert proc.stdout is not None
    process(iter_geojsonl(proc.stdout), builder, writer, review, stats, key)
    rc, err = finish(proc)
    if rc != 0 or stats[key]["in"] == 0:
        # /vsizip/ refusal on the runner's GDAL is the one failure we can route
        # around: extract only the .gdb and retry once from disk. ONLY when
        # nothing streamed — a partial stream + crash must not be re-run (the
        # writer already holds the first pass; a retry would duplicate).
        if zip_path and ogr_src.startswith("/vsizip/") and stats[key]["in"] == 0:
            print(f"::warning::ogr2ogr rc={rc} in=0 on {ogr_src} — "
                  f"retrying from an extracted .gdb\n{err[-2000:]}", file=sys.stderr)
            tmp = Path(tempfile.mkdtemp(prefix="tnm_gdb_"))
            gdb = extract_gdb(zip_path, tmp)
            proc = ogr_stream(gdb, layer, err_path)
            process(iter_geojsonl(proc.stdout), builder, writer, review, stats, key)
            rc, err = finish(proc)
            shutil.rmtree(tmp, ignore_errors=True)
        if rc != 0:
            sys.exit(f"ogr2ogr failed on {ogr_src} {layer} (rc={rc})\n{err[-4000:]}")
    if err.strip():
        print(f"ogr2ogr {key} stderr ({len(err)} chars): {err[-800:]}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--unit", required=True, help="matrix unit (USPS state code)")
    parser.add_argument("--src", action="append", default=[],
                        help="per-state zip or .gdb (repeatable; both layers streamed via ogr2ogr)")
    parser.add_argument("--roads-src", action="append", default=[],
                        help="EPSG:4326 GeoJSONSeq of Trans_RoadSegment rows (no GDAL needed)")
    parser.add_argument("--trails-src", action="append", default=[],
                        help="EPSG:4326 GeoJSONSeq of Trans_TrailSegment rows (no GDAL needed)")
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--roads-layer", default=ROADS_LAYER)
    parser.add_argument("--trails-layer", default=TRAILS_LAYER)
    parser.add_argument("--review-out", default=None,
                        help="review queue path (default <out>/review_queue_roads_tnm.jsonl)")
    args = parser.parse_args()
    if not (args.src or args.roads_src or args.trails_src):
        parser.error("give --src (zip/gdb) or --roads-src/--trails-src (geojsonl)")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    review = Review()
    writer = Writer(out_dir)
    stats: dict = {"unit": args.unit, "sources": []}

    try:
        for src in args.src:
            ogr_src = resolve_src(src)
            stats["sources"].append(ogr_src)
            zip_path = src if src.lower().endswith(".zip") else None
            run_layer(ogr_src, args.roads_layer, road_props, writer, review, stats, "roads",
                      zip_path, out_dir)
            run_layer(ogr_src, args.trails_layer, trail_props, writer, review, stats, "trails",
                      zip_path, out_dir)
        for src in args.roads_src:
            stats["sources"].append(src)
            with open(src, encoding="utf-8") as fh:
                process(iter_geojsonl(fh), road_props, writer, review, stats, "roads")
        for src in args.trails_src:
            stats["sources"].append(src)
            with open(src, encoding="utf-8") as fh:
                process(iter_geojsonl(fh), trail_props, writer, review, stats, "trails")
    finally:
        writer.close()

    stats["kept_by_layer"] = writer.counts
    stats["kept_by_class"] = writer.by_class
    stats["kept"] = sum(writer.counts.values())
    stats["review_entries"] = len(review.entries)
    review.write(Path(args.review_out) if args.review_out else out_dir / "review_queue_roads_tnm.jsonl")
    (out_dir / "normalize_stats.json").write_text(json.dumps(stats, indent=2, sort_keys=True))
    print(json.dumps(stats, indent=2, sort_keys=True))
    if stats.get("roads", {}).get("kept", 0) == 0 and args.src:
        sys.exit("normalize produced 0 road features — refusing to continue")


if __name__ == "__main__":
    main()
