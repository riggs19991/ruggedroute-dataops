#!/usr/bin/env python3
"""Stage 3 parcels normalizer: raw state source -> parcels.geojsonl (whitelisted).

THE INVARIANT (research 2026-08-09 §5/§6, master plan §7): owner names and
addresses NEVER enter tiles. This normalizer enforces it BY CONSTRUCTION — the
output properties dict is built fresh from an explicit three-field mapping
(apn/county/acres) plus the state code, plus (T-0012) an optional `use` bucket
that a named adapter derives from the unit's use_field — always one of the
closed 7-value USE_BUCKETS vocabulary, so no source text rides along. Nothing
else can pass through, whatever the source publishes. qa_parcels.py re-verifies
the same whitelist (and the use vocabulary) on the output file and on decoded
tiles, so a regression here still cannot ship.

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
--apn-field/--county-field/--acres-field overrides are given. The optional
use_field/use_adapter pair (T-0012) comes from sources.json only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

WHITELIST = ("apn", "county", "acres", "st", "use")

# Substrings that mark a field mapping as forbidden no matter what a future
# sources.json says — a config typo must not be able to route an owner column
# into the apn/county slot. (APN fields legitimately named OWNER_* don't exist.)
FORBIDDEN_FIELD_SUBSTRINGS = ("owner", "own_", "name", "addr", "mail", "care_of", "taxpayer")

# ── T-0009: county is a DISPLAY NAME or absent — bare codes never reach tiles ──
# Sources that publish only a numeric county code get a static translation
# table; numerics with no table entry are DROPPED. Name-carrying sources pass
# through untouched (MT CountyName, TX COUNTY, WI CONAME, ...).

# FDOR county number 11-77, alphabetical (FDOR NAL standard). Anchors verified
# against live tiles 2026-08-11: 58=Orange (Orlando), 23=Dade (shown as the
# county's current display name Miami-Dade).
FL_COUNTY_NAMES = {
    11: "Alachua", 12: "Baker", 13: "Bay", 14: "Bradford", 15: "Brevard", 16: "Broward",
    17: "Calhoun", 18: "Charlotte", 19: "Citrus", 20: "Clay", 21: "Collier", 22: "Columbia",
    23: "Miami-Dade", 24: "DeSoto", 25: "Dixie", 26: "Duval", 27: "Escambia", 28: "Flagler",
    29: "Franklin", 30: "Gadsden", 31: "Gilchrist", 32: "Glades", 33: "Gulf", 34: "Hamilton",
    35: "Hardee", 36: "Hendry", 37: "Hernando", 38: "Highlands", 39: "Hillsborough",
    40: "Holmes", 41: "Indian River", 42: "Jackson", 43: "Jefferson", 44: "Lafayette",
    45: "Lake", 46: "Lee", 47: "Leon", 48: "Levy", 49: "Liberty", 50: "Madison",
    51: "Manatee", 52: "Marion", 53: "Martin", 54: "Monroe", 55: "Nassau", 56: "Okaloosa",
    57: "Okeechobee", 58: "Orange", 59: "Osceola", 60: "Palm Beach", 61: "Pasco",
    62: "Pinellas", 63: "Polk", 64: "Putnam", 65: "St. Johns", 66: "St. Lucie",
    67: "Santa Rosa", 68: "Sarasota", 69: "Seminole", 70: "Sumter", 71: "Suwannee",
    72: "Taylor", 73: "Union", 74: "Volusia", 75: "Wakulla", 76: "Walton", 77: "Washington",
}

# VA locality FIPS → name, harvested 2026-10-25 from the Census codes2020
# national_county file (www2.census.gov/geo/docs/reference/codes2020/). VA's
# VGIN FGDB carries geometry+PARCELID+FIPS only, so this is the only name path.
VA_COUNTY_NAMES = {
    "51001": "Accomack County", "51003": "Albemarle County", "51005": "Alleghany County",
    "51007": "Amelia County", "51009": "Amherst County", "51011": "Appomattox County",
    "51013": "Arlington County", "51015": "Augusta County", "51017": "Bath County",
    "51019": "Bedford County", "51021": "Bland County", "51023": "Botetourt County",
    "51025": "Brunswick County", "51027": "Buchanan County", "51029": "Buckingham County",
    "51031": "Campbell County", "51033": "Caroline County", "51035": "Carroll County",
    "51036": "Charles City County", "51037": "Charlotte County", "51041": "Chesterfield County",
    "51043": "Clarke County", "51045": "Craig County", "51047": "Culpeper County",
    "51049": "Cumberland County", "51051": "Dickenson County", "51053": "Dinwiddie County",
    "51057": "Essex County", "51059": "Fairfax County", "51061": "Fauquier County",
    "51063": "Floyd County", "51065": "Fluvanna County", "51067": "Franklin County",
    "51069": "Frederick County", "51071": "Giles County", "51073": "Gloucester County",
    "51075": "Goochland County", "51077": "Grayson County", "51079": "Greene County",
    "51081": "Greensville County", "51083": "Halifax County", "51085": "Hanover County",
    "51087": "Henrico County", "51089": "Henry County", "51091": "Highland County",
    "51093": "Isle of Wight County", "51095": "James City County", "51097": "King and Queen County",
    "51099": "King George County", "51101": "King William County", "51103": "Lancaster County",
    "51105": "Lee County", "51107": "Loudoun County", "51109": "Louisa County",
    "51111": "Lunenburg County", "51113": "Madison County", "51115": "Mathews County",
    "51117": "Mecklenburg County", "51119": "Middlesex County", "51121": "Montgomery County",
    "51125": "Nelson County", "51127": "New Kent County", "51131": "Northampton County",
    "51133": "Northumberland County", "51135": "Nottoway County", "51137": "Orange County",
    "51139": "Page County", "51141": "Patrick County", "51143": "Pittsylvania County",
    "51145": "Powhatan County", "51147": "Prince Edward County", "51149": "Prince George County",
    "51153": "Prince William County", "51155": "Pulaski County", "51157": "Rappahannock County",
    "51159": "Richmond County", "51161": "Roanoke County", "51163": "Rockbridge County",
    "51165": "Rockingham County", "51167": "Russell County", "51169": "Scott County",
    "51171": "Shenandoah County", "51173": "Smyth County", "51175": "Southampton County",
    "51177": "Spotsylvania County", "51179": "Stafford County", "51181": "Surry County",
    "51183": "Sussex County", "51185": "Tazewell County", "51187": "Warren County",
    "51191": "Washington County", "51193": "Westmoreland County", "51195": "Wise County",
    "51197": "Wythe County", "51199": "York County", "51510": "Alexandria city",
    "51520": "Bristol city", "51530": "Buena Vista city", "51540": "Charlottesville city",
    "51550": "Chesapeake city", "51570": "Colonial Heights city", "51580": "Covington city",
    "51590": "Danville city", "51595": "Emporia city", "51600": "Fairfax city",
    "51610": "Falls Church city", "51620": "Franklin city", "51630": "Fredericksburg city",
    "51640": "Galax city", "51650": "Hampton city", "51660": "Harrisonburg city",
    "51670": "Hopewell city", "51678": "Lexington city", "51680": "Lynchburg city",
    "51683": "Manassas city", "51685": "Manassas Park city", "51690": "Martinsville city",
    "51700": "Newport News city", "51710": "Norfolk city", "51720": "Norton city",
    "51730": "Petersburg city", "51735": "Poquoson city", "51740": "Portsmouth city",
    "51750": "Radford city", "51760": "Richmond city", "51770": "Roanoke city",
    "51775": "Salem city", "51790": "Staunton city", "51800": "Suffolk city",
    "51810": "Virginia Beach city", "51820": "Waynesboro city", "51830": "Williamsburg city",
    "51840": "Winchester city",
}

# MD JURSCODE (MDP 4-letter jurisdiction codes). These are LETTER codes, so the
# table must be consulted before the letters-means-name passthrough. Anchors
# geo-verified on live tiles 2026-10-25: Rockville tile = MONT (Montgomery),
# Annapolis tile = ANNE (Anne Arundel).
MD_COUNTY_NAMES = {
    "ALLE": "Allegany",
    "ANNE": "Anne Arundel",
    "BACI": "Baltimore City",
    "BACO": "Baltimore",
    "CALV": "Calvert",
    "CARO": "Caroline",
    "CARR": "Carroll",
    "CECI": "Cecil",
    "CHAR": "Charles",
    "DORC": "Dorchester",
    "FRED": "Frederick",
    "GARR": "Garrett",
    "HARF": "Harford",
    "HOWA": "Howard",
    "KENT": "Kent",
    "MONT": "Montgomery",
    "PRIN": "Prince George's",
    "QUEE": "Queen Anne's",
    "SOME": "Somerset",
    "STMA": "St. Mary's",
    "TALB": "Talbot",
    "WASH": "Washington",
    "WICO": "Wicomico",
    "WORC": "Worcester",
}

# NH GRANIT CountyId 1-10, alphabetical. Anchors geo-verified on live tiles
# 2026-10-25: Concord = 7 (Merrimack), Nashua = 6 (Hillsborough).
NH_COUNTY_NAMES = {1: "Belknap", 2: "Carroll", 3: "Cheshire", 4: "Coos", 5: "Grafton", 6: "Hillsborough", 7: "Merrimack", 8: "Rockingham", 9: "Strafford", 10: "Sullivan"}

# IN county FIPS -> name, harvested 2026-10-25 from Census codes2020 (suffix
# "County" stripped — IN has no ambiguous city/county pairs, unlike VA).
# Anchor geo-verified on live tiles: Indianapolis tile = 18097 (Marion).
IN_COUNTY_NAMES = {
    "18001": "Adams",
    "18003": "Allen",
    "18005": "Bartholomew",
    "18007": "Benton",
    "18009": "Blackford",
    "18011": "Boone",
    "18013": "Brown",
    "18015": "Carroll",
    "18017": "Cass",
    "18019": "Clark",
    "18021": "Clay",
    "18023": "Clinton",
    "18025": "Crawford",
    "18027": "Daviess",
    "18029": "Dearborn",
    "18031": "Decatur",
    "18033": "DeKalb",
    "18035": "Delaware",
    "18037": "Dubois",
    "18039": "Elkhart",
    "18041": "Fayette",
    "18043": "Floyd",
    "18045": "Fountain",
    "18047": "Franklin",
    "18049": "Fulton",
    "18051": "Gibson",
    "18053": "Grant",
    "18055": "Greene",
    "18057": "Hamilton",
    "18059": "Hancock",
    "18061": "Harrison",
    "18063": "Hendricks",
    "18065": "Henry",
    "18067": "Howard",
    "18069": "Huntington",
    "18071": "Jackson",
    "18073": "Jasper",
    "18075": "Jay",
    "18077": "Jefferson",
    "18079": "Jennings",
    "18081": "Johnson",
    "18083": "Knox",
    "18085": "Kosciusko",
    "18087": "LaGrange",
    "18089": "Lake",
    "18091": "LaPorte",
    "18093": "Lawrence",
    "18095": "Madison",
    "18097": "Marion",
    "18099": "Marshall",
    "18101": "Martin",
    "18103": "Miami",
    "18105": "Monroe",
    "18107": "Montgomery",
    "18109": "Morgan",
    "18111": "Newton",
    "18113": "Noble",
    "18115": "Ohio",
    "18117": "Orange",
    "18119": "Owen",
    "18121": "Parke",
    "18123": "Perry",
    "18125": "Pike",
    "18127": "Porter",
    "18129": "Posey",
    "18131": "Pulaski",
    "18133": "Putnam",
    "18135": "Randolph",
    "18137": "Ripley",
    "18139": "Rush",
    "18141": "St. Joseph",
    "18143": "Scott",
    "18145": "Shelby",
    "18147": "Spencer",
    "18149": "Starke",
    "18151": "Steuben",
    "18153": "Sullivan",
    "18155": "Switzerland",
    "18157": "Tippecanoe",
    "18159": "Tipton",
    "18161": "Union",
    "18163": "Vanderburgh",
    "18165": "Vermillion",
    "18167": "Vigo",
    "18169": "Wabash",
    "18171": "Warren",
    "18173": "Warrick",
    "18175": "Washington",
    "18177": "Wayne",
    "18179": "Wells",
    "18181": "White",
    "18183": "Whitley",
}

COUNTY_CODE_TABLES: dict[str, dict] = {
    "FL": FL_COUNTY_NAMES,
    "VA": VA_COUNTY_NAMES,
    "MD": MD_COUNTY_NAMES,
    "NH": NH_COUNTY_NAMES,
    "IN": IN_COUNTY_NAMES,
}


def normalize_county(state: str, value: str | None) -> str | None:
    """Display name or None. Lookup order:
    1. The state's code table, keyed by the raw upper-cased token (MD's
       4-LETTER codes) or by integer / zero-padded-FIPS forms ('58.0', 51059).
    2. Letters present and no table hit -> already a name, pass through.
    3. Anything numeric left over is a bare code -> DROPPED, never shipped.
    Non-integral numerics ('58.9') and overflow-sized strings also drop."""
    if value is None:
        return None
    table = COUNTY_CODE_TABLES.get(state)
    token = value.strip()
    if table is not None:
        hit = table.get(token.upper())
        if hit:
            return hit
        try:
            f = float(token)
            if f.is_integer():
                code = int(f)
                hit = table.get(code) or table.get(f"{code:05d}")
                if hit:
                    return hit
        except (TypeError, ValueError, OverflowError):
            pass
    if any(ch.isalpha() for ch in token):
        # A table-state letter token that missed the table is suspect (an
        # unmapped MD-style code) only when it looks code-like; real names
        # carry lowercase or spaces. 2-5 upper-alnum chars in a table state
        # -> drop rather than ship a code as a name.
        if table is not None and token.isupper() and token.isalnum() and len(token) <= 5:
            return None
        return token
    return None


# ── T-0012: land use is a closed 7-bucket vocabulary or absent ───────────────
# One adapter per source classification scheme, each grounded in live value
# harvests (2026-10-25: ArcGIS distinct-value queries, DBF reads, live-tile
# decodes). sources.json wires a unit with use_field (the SOURCE column) +
# use_adapter (a USE_ADAPTERS key). Unknown/unmapped values return None and the
# attribute is OMITTED — there is no "OTHER" bucket, so the client never renders
# a meaningless label. The set must match the app's USE_LABELS exactly (change
# only in lockstep); qa_parcels.py gates the same vocabulary on output + tiles.
USE_BUCKETS = frozenset({"RES", "AG", "VAC", "COM", "IND", "FOREST", "GOV"})


def _use_fl_dor(v):
    s = str(v).strip()
    if not s[:3].isdigit():
        return None
    n = int(s[:3])
    if n == 0: return "VAC"            # 000 vacant residential
    if 1 <= n <= 9: return "RES"
    if 10 <= n <= 39: return "COM"
    if 40 <= n <= 49: return "IND"
    if 54 <= n <= 58: return "FOREST"  # timberland band inside the ag range
    if 50 <= n <= 69: return "AG"
    if 70 <= n <= 89: return "GOV"     # institutional + governmental
    return None                        # 90-99 centrally assessed / misc


def _use_ma_dor(v):
    d = str(v).strip().lstrip("0")
    if len(d) < 3 or not d.isdigit():
        return None                    # '010C' style letter suffixes -> omit
    return {"1": "RES", "3": "COM", "4": "IND", "6": "FOREST",
            "7": "AG", "9": "GOV"}.get(d[0])   # 2xx open, 5xx personal, 8xx rec -> omit


def _use_in_dlgf(v):
    d = str(v).strip()
    if len(d) < 3 or not d.isdigit():
        return None
    return {"1": "AG", "3": "IND", "4": "COM", "5": "RES", "6": "GOV"}.get(d[0])


def _use_nj_modiv(v):
    c = str(v).strip().upper()
    if c == "1": return "VAC"
    if c in ("2", "4C"): return "RES"
    if c in ("3A", "3B"): return "AG"
    if c == "4A": return "COM"
    if c == "4B": return "IND"
    if c.startswith("15"): return "GOV"
    return None                        # 5A/5B/6x rail+utility -> omit


def _use_dc_class(v):
    c = str(v).strip().upper()
    if c in ("1", "1A", "1B"): return "RES"
    if c == "2": return "COM"
    if c in ("3", "4"): return "VAC"   # 4 = blighted vacant
    return None


def _use_wi_propclass(v):
    first = str(v).split(",")[0].strip().upper()
    return {"1": "RES", "2": "COM", "3": "IND", "4": "AG",
            "5": "VAC", "5M": "FOREST", "6": "FOREST"}.get(first)  # 7 'other' -> omit


def _use_mt_proptype(v):
    t = str(v).lower()
    if "vacant" in t: return "VAC"
    if "industrial" in t or "mining" in t or "gravel" in t or "oilfield" in t: return "IND"
    if "apartment" in t or "condominium" in t or "townhouse" in t or "mobile" in t: return "RES"
    if "exempt" in t or "tribal" in t or "centrally assessed" in t or "utility" in t: return "GOV"
    if "farm" in t or "agricultural" in t: return "AG"
    if "forest" in t or "timber" in t: return "FOREST"
    if "golf" in t: return "COM"
    return None                        # 'Improved Property' etc. are ambiguous -> omit


USE_ADAPTERS = {
    "fl_dor": _use_fl_dor, "ma_dor": _use_ma_dor, "in_dlgf": _use_in_dlgf,
    "nj_modiv": _use_nj_modiv, "dc_class": _use_dc_class,
    "wi_propclass": _use_wi_propclass, "mt_proptype": _use_mt_proptype,
}


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
                acres_divisor: float = 1.0,
                use_field: str | None = None,
                use_adapter: str | None = None) -> dict:
    """Fresh whitelisted props dict — the enforcement point.

    lower_index maps lowercased source keys -> actual keys so a config written
    from REST metadata (PARCEL_ID) still matches a shapefile's truncated or
    recased header (parcel_id).

    acres_divisor converts non-acre source units (FL publishes LND_SQFOOT —
    square feet — so its sources.json entry carries acres_divisor 43560).

    use_field/use_adapter (T-0012, from sources.json): the source column holding
    the assessment class and the USE_ADAPTERS key that buckets it. Only a result
    inside USE_BUCKETS is kept — None, junk from a misbehaving adapter or an
    adapter error all omit the attribute; the raw value itself never ships.
    """
    if lower_index is None:
        lower_index = {k.lower(): k for k in raw}
    out: dict = {"st": state}
    for role in ("apn", "county"):
        field = mapping.get(role)
        if not field:
            continue
        value = clean(raw.get(field, raw.get(lower_index.get(field.lower(), ""), None)))
        if role == "county":
            value = normalize_county(state, value)
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
    if use_field and use_adapter:
        value = clean(raw.get(use_field, raw.get(lower_index.get(use_field.lower(), ""), None)))
        if value is not None:
            try:
                bucket = USE_ADAPTERS[use_adapter](value)
            except (TypeError, ValueError):  # tolerant: one odd code never kills a unit
                bucket = None
            if isinstance(bucket, str) and bucket in USE_BUCKETS:
                out["use"] = bucket
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
        # -select tolerance is FORMAT-DEPENDENT (learned on run 40243912707):
        # shapefiles warn-and-continue on unknown names, but FGDB sources HARD
        # FAIL ("Field 'X' not found in source layer" terminates translation).
        # That loudness is a feature — a renamed upstream column fails the unit
        # instead of shipping a silent all-null attribute — but it means every
        # -select name for a gdb unit is a live-verified contract, never a guess.
        cmd += ["-select", ",".join(fields)]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1)


def normalize(srcs: list[str], layer_hint: str | None, mapping: dict[str, str | None],
              state: str, out_path: Path, stats: dict,
              acres_divisor: float = 1.0,
              use_field: str | None = None,
              use_adapter: str | None = None) -> None:
    kept = dropped_geom = 0
    attr_present = {"apn": 0, "county": 0, "acres": 0, "use": 0}
    with out_path.open("w", encoding="utf-8") as out:
        for src in srcs:
            ogr_src = resolve_src(src)
            stats.setdefault("sources", []).append(ogr_src)
            fields = [f for f in mapping.values() if f]
            if use_field and use_field not in fields:
                # T-0012: -select must carry the use column too, or every
                # http/hub unit would ship use silently all-null.
                fields.append(use_field)
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
                props = build_props(raw, mapping, state, lower_index, acres_divisor,
                                    use_field=use_field, use_adapter=use_adapter)
                feature["properties"] = props
                for attr in ("apn", "county", "acres", "use"):
                    if attr in props:
                        attr_present[attr] += 1
                out.write(json.dumps(feature, separators=(",", ":")) + "\n")
                kept += 1
            rc = proc.wait()
            if rc != 0:
                sys.exit(f"ogr2ogr failed on {ogr_src} (rc={rc})")
    stats["kept"] = kept
    stats["dropped_empty_geometry"] = dropped_geom
    # T-0009: null-rate visibility — a renamed upstream field (WI V12→V13 etc.)
    # must show up as a number in the CI log, never as a silent all-null attr.
    # T-0012: use is None when the unit configures no use_field ("not
    # configured"), never 1.0 — 1.0 means configured-but-empty (renamed column
    # or dead adapter) and must read as a red flag.
    stats["attr_null_rates"] = {
        attr: (round(1.0 - attr_present[attr] / kept, 4)
               if kept and (attr != "use" or use_field) else None)
        for attr in ("apn", "county", "acres", "use")
    }
    print(f"  attr null rates (kept={kept}): " +
          ", ".join(f"{a}={stats['attr_null_rates'][a]}"
                    for a in ("apn", "county", "acres", "use")))


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
    # T-0012: optional land-use wiring (sources.json only). use_field gets the
    # same forbidden-substring screen under role "use" (so the non-apn 'name'
    # exemption applies) but stays out of mapping — it never joins the
    # apn/county extraction loop; build_props only ever emits its bucket.
    use_field = cfg.get("use_field") or None
    use_adapter = cfg.get("use_adapter") or None
    check_mapping({**mapping, "use": use_field})
    if bool(use_field) != bool(use_adapter):
        sys.exit(f"REFUSING use config for {args.unit}: use_field and use_adapter must be set "
                 f"together (use_field={use_field!r}, use_adapter={use_adapter!r})")
    if use_adapter and use_adapter not in USE_ADAPTERS:
        sys.exit(f"REFUSING use config for {args.unit}: unknown use_adapter {use_adapter!r} "
                 f"(known: {', '.join(sorted(USE_ADAPTERS))})")
    layer_hint = args.layer or cfg.get("layer") or None
    acres_divisor = float(cfg.get("acres_divisor") or 1.0)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    stats: dict = {"unit": args.unit, "st": state, "mapping": mapping}
    normalize(args.src, layer_hint, mapping, state, out_dir / "parcels.geojsonl", stats,
              acres_divisor, use_field=use_field, use_adapter=use_adapter)

    (out_dir / "normalize_stats.json").write_text(json.dumps(stats, indent=2, sort_keys=True))
    print(json.dumps(stats, indent=2, sort_keys=True))
    if stats["kept"] == 0:
        sys.exit("normalize produced 0 features — refusing to continue")


if __name__ == "__main__":
    main()
