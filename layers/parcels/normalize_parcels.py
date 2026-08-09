#!/usr/bin/env python3
"""Stage 3 parcels normalizer: raw state source -> parcels.geojsonl (whitelisted).

THE INVARIANT (research 2026-08-09 §5/§6, master plan §7): owner names and
addresses NEVER enter tiles. This normalizer enforces it BY CONSTRUCTION — the
output properties dict is built fresh from an explicit three-field mapping
(apn/county/acres) plus the state code; nothing else can pass through, whatever
the source publishes. qa_parcels.py re-verifies the same whitelist on the
output file and on decoded tiles, so a regression here still cannot ship.

Input handling
--------------
--src accepts (repeatable, appended in order):
  *.geojsonl        esri2geojson --jsonlines output (already EPSG:4326)
  *.zip             routed through /vsizip/ WITHOUT extraction (MA's 6.3 GB
                    FGDB zip must never be unzipped on a 14 GB runner); the
                    inner .gdb directory or .shp is auto-located
  *.gdb / dir/file  any OGR-readable path, passed straight to ogr2ogr

ogr2ogr does the heavy lifting (driver detection, EPSG:4326 reproject,
-makevalid, GeoJSONSeq streaming); this script streams line-by-line so the
13M-parcel states stay flat on memory.

Usage:
    normalize_parcels.py --unit UT --src src/UT_1.zip --out build/
    normalize_parcels.py --unit TX_1 --src src/TX_1_raw.geojsonl --out build/
Field mapping comes from sources.json (next to this script) unless the
--apn-field/--county-field/--acres-field overrides are given.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

WHITELIST = ("apn", "county", "acres", "st")

# Substrings that mark a field mapping as forbidden no matter what a future
# sources.json says — a config typo must not be able to route an owner column
# into the apn/county slot. (APN fields legitimately named OWNER_* don't exist.)
FORBIDDEN_FIELD_SUBSTRINGS = ("owner", "own_", "name", "addr", "mail", "care_of", "taxpayer")


def clean(value) -> str | None:
    """None for null-ish attribute values (None, '', 'null', whitespace)."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in ("null", "none", "<null>"):
        return None
    return text


def check_mapping(mapping: dict[str, str | None]) -> None:
    for role, field in mapping.items():
        if not field:
            continue
        low = field.lower()
        for bad in FORBIDDEN_FIELD_SUBSTRINGS:
            # county fields are routinely called COUNTYNAME/CO_NAME — 'name' is
            # only forbidden for the apn slot, where an ID never contains it.
            if bad == "name" and role != "apn":
                continue
            if bad in low:
                sys.exit(f"REFUSING mapping {role}={field!r}: matches forbidden substring {bad!r} "
                         f"(owner/address data must never be selected)")


def resolve_src(src: str) -> str:
    """OGR-openable path for src; zips go through /vsizip/ without extraction."""
    if not src.lower().endswith(".zip"):
        return src
    names = zipfile.ZipFile(src).namelist()
    gdb_dirs = sorted({n.split(".gdb/")[0] + ".gdb" for n in names if ".gdb/" in n})
    posix = Path(src).as_posix()
    if gdb_dirs:
        return f"/vsizip/{posix}/{gdb_dirs[0]}"
    shps = sorted(n for n in names if n.lower().endswith(".shp"))
    if shps:
        return f"/vsizip/{posix}/{shps[0]}"
    return f"/vsizip/{posix}"


def pick_layer(ogr_src: str, hint: str | None) -> list[str]:
    """ogr2ogr layer args: explicit hint, else default (single-layer sources)."""
    return [hint] if hint else []


def build_props(raw: dict, mapping: dict[str, str | None], state: str,
                lower_index: dict[str, str] | None = None,
                acres_divisor: float = 1.0) -> dict:
    """Fresh whitelisted props dict — the enforcement point.

    lower_index maps lowercased source keys -> actual keys so a config written
    from REST metadata (PARCEL_ID) still matches a shapefile's truncated or
    recased header (parcel_id).

    acres_divisor converts non-acre source units (FL publishes LND_SQFOOT —
    square feet — so its sources.json entry carries acres_divisor 43560).
    """
    if lower_index is None:
        lower_index = {k.lower(): k for k in raw}
    out: dict = {"st": state}
    for role in ("apn", "county"):
        field = mapping.get(role)
        if not field:
            continue
        value = clean(raw.get(field, raw.get(lower_index.get(field.lower(), ""), None)))
        if value is not None:
            out[role] = value
    acres_field = mapping.get("acres")
    if acres_field:
        value = raw.get(acres_field, raw.get(lower_index.get(acres_field.lower(), ""), None))
        try:
            acres = round(float(value) / acres_divisor, 2)
            if acres > 0:
                out["acres"] = acres
        except (TypeError, ValueError, ZeroDivisionError):
            pass
    return out


def ogr_stream(ogr_src: str, layer_args: list[str], fields: list[str]) -> subprocess.Popen:
    cmd = [
        "ogr2ogr",
        "-f", "GeoJSONSeq", "/vsistdout/",
        ogr_src, *layer_args,
        "-t_srs", "EPSG:4326",
        "-makevalid",
        "-nlt", "PROMOTE_TO_MULTI",
    ]
    if fields:
        # ogr2ogr warns-and-continues on unknown -select names, which is the
        # tolerance we want across shapefile/GDB header drift.
        cmd += ["-select", ",".join(fields)]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1)


def normalize(srcs: list[str], layer_hint: str | None, mapping: dict[str, str | None],
              state: str, out_path: Path, stats: dict,
              acres_divisor: float = 1.0) -> None:
    kept = dropped_geom = 0
    with out_path.open("w", encoding="utf-8") as out:
        for src in srcs:
            ogr_src = resolve_src(src)
            stats.setdefault("sources", []).append(ogr_src)
            fields = [f for f in mapping.values() if f]
            proc = ogr_stream(ogr_src, pick_layer(ogr_src, layer_hint), fields)
            assert proc.stdout is not None
            lower_index: dict[str, str] | None = None
            for line in proc.stdout:
                line = line.strip().lstrip("\x1e")
                if not line:
                    continue
                try:
                    feature = json.loads(line)
                except json.JSONDecodeError:
                    continue  # tolerant: never crash on a bad upstream line
                geom = feature.get("geometry")
                if not geom or not geom.get("coordinates"):
                    dropped_geom += 1
                    continue
                raw = feature.get("properties") or {}
                if lower_index is None:
                    lower_index = {k.lower(): k for k in raw}
                feature["properties"] = build_props(raw, mapping, state, lower_index,
                                                    acres_divisor)
                out.write(json.dumps(feature, separators=(",", ":")) + "\n")
                kept += 1
            rc = proc.wait()
            if rc != 0:
                sys.exit(f"ogr2ogr failed on {ogr_src} (rc={rc})")
    stats["kept"] = kept
    stats["dropped_empty_geometry"] = dropped_geom


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", required=True, help="matrix unit (UT, TX_1, ...)")
    parser.add_argument("--src", action="append", required=True,
                        help="input path (repeatable; zip/gdb/geojsonl)")
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--layer", help="source layer name (FGDB with several layers)")
    parser.add_argument("--apn-field")
    parser.add_argument("--county-field")
    parser.add_argument("--acres-field")
    args = parser.parse_args()

    state = args.unit.split("_")[0]
    sources_path = Path(__file__).parent / "sources.json"
    cfg = {}
    if sources_path.exists():
        cfg = json.loads(sources_path.read_text(encoding="utf-8")).get(args.unit, {})
    cfg_fields = cfg.get("fields", {})
    mapping = {
        "apn": args.apn_field or cfg_fields.get("apn"),
        "county": args.county_field or cfg_fields.get("county"),
        "acres": args.acres_field or cfg_fields.get("acres"),
    }
    check_mapping(mapping)
    layer_hint = args.layer or cfg.get("layer") or None
    acres_divisor = float(cfg.get("acres_divisor") or 1.0)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    stats: dict = {"unit": args.unit, "st": state, "mapping": mapping}
    normalize(args.src, layer_hint, mapping, state, out_dir / "parcels.geojsonl", stats,
              acres_divisor)

    (out_dir / "normalize_stats.json").write_text(json.dumps(stats, indent=2, sort_keys=True))
    print(json.dumps(stats, indent=2, sort_keys=True))
    if stats["kept"] == 0:
        sys.exit("normalize produced 0 features — refusing to continue")


if __name__ == "__main__":
    main()
