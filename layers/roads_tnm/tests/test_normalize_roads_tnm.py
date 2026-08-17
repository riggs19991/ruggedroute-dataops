"""D1b roads_tnm: classing rules, ref parser, whitelist-by-construction, QA gates.

Every rule below was verified against the TNM FGDB on disk (AK/DE/VT/WY,
2026-08-16); the tests pin the observed cases so a future 'tidy-up' cannot
silently flip e.g. DE's US-13 freeway rows back to 'interstate' or start
emitting an owner-style foreign key.
"""

import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from normalize_roads_tnm import (  # noqa: E402
    CLASSES, LAYER_OF, MINZOOM, WHITELIST, Review, build_ref, classify, clean,
    haversine_miles, originator_code, parse_route, resolve_src, road_props,
    round_miles, source_id, trail_props,
)
from qa_roads_tnm import (  # noqa: E402
    LAYER_CLASSES, WHITELIST as QA_WHITELIST, bbox_intersects, feature_bbox,
    gate_size_band, scan,
)

LINE = {"type": "MultiLineString",
        "coordinates": [[[-116.20, 44.30], [-116.19, 44.30]]]}   # ~0.5 mi E-W at 44.3N


# ── classing (layer.json rules_ordered) ──────────────────────────────────────

def test_ferry_dropped_before_anything_else():
    assert classify(7, "L4165", None, None, None) is None
    assert classify("7", "L4165", "95", None, None) is None   # even with a shield


def test_ramp_fourwd_closed_by_tnmfrc():
    assert classify(5, "S1630", None, None, None) == "ramp"
    assert classify(6, "S1500", None, None, None) == "fourwd"
    assert classify(6, None, None, None, None) == "fourwd"     # 8 NULL-mtfcc USFS rows nationally
    assert classify(9, "S1400", None, None, None) == "closed"  # forward-compat, 0 rows today


def test_designation_first_de_us13_freeway_is_us_hwy_not_interstate():
    # DE: tnmfrc 1 rows with only a us_route (US-13/202/301) — 53 rows on disk
    assert classify(1, "S1100", None, "13", None) == "us_hwy"
    # DE-1 / DE-141 freeways: tnmfrc 1 + state_route only (284 rows)
    assert classify(1, "S1100", None, None, "1") == "state_hwy"


def test_plain_interstate_wins_at_any_highway_tnmfrc():
    assert classify(1, "S1100", "95", None, None) == "interstate"
    assert classify(2, "S1200", "180", None, None) == "interstate"        # WY I-180 surface interstate
    assert classify(8, "S1100", "80", "30", None) == "interstate"         # WY Green River Tunnel
    assert classify(1, "S1100", "80", "30", "789") == "interstate"        # concurrency: I wins


def test_interstate_business_loop_is_state_hwy():
    # WY: 684 'Bus,25/80/90' rows on tnmfrc 2/3, none on tnmfrc 1
    assert classify(2, "S1200", "Bus,25", None, None) == "state_hwy"
    assert classify(3, "S1400", "Bus,25,Bus,90", None, None) == "state_hwy"
    # but a business loop alongside a US route -> us_hwy (US checked first)
    assert classify(2, "S1200", "Bus,25", "87", None) == "us_hwy"


def test_undesignated_highway_tnmfrc_falls_back_by_hierarchy():
    assert classify(1, "S1100", None, None, None) == "interstate"    # AK 35 / DE 13 unsigned freeways
    assert classify(2, "S1200", None, None, None) == "local_conn"    # AK 256
    assert classify(3, "S1400", None, None, None) == "local_conn"    # AK 2,067
    assert classify(8, "S1100", None, None, None) == "interstate"    # tunnel inherits by mtfcc
    assert classify(8, "S1200", None, None, None) == "local_conn"
    assert classify(8, "S1400", None, None, None) == "local"         # AK 'Whittier Access Road'


def test_local_is_the_default_and_never_promoted_by_route_fields():
    assert classify(4, "S1400", None, None, None) == "local"
    assert classify(4, "S1740", None, None, None) == "local"        # private road stays, mtfcc kept
    assert classify(4, "S1400", None, None, "27") == "local"        # DE 27 rows: NOT promoted (ref still set)
    assert classify(99, None, None, None, None) == "local"
    assert classify(None, None, None, None, None) == "local"
    assert classify("garbage", None, None, None, None) == "local"


def test_every_class_has_a_layer_and_a_minzoom():
    assert set(LAYER_OF) == set(CLASSES) == set(MINZOOM)
    assert MINZOOM["interstate"] < MINZOOM["us_hwy"] < MINZOOM["state_hwy"] < MINZOOM["local_conn"] < MINZOOM["local"]
    assert min(MINZOOM.values()) == 5     # tileset -Z5
    # qa's file->class contract must agree with the normalizer's routing
    for cls, layer in LAYER_OF.items():
        assert cls in LAYER_CLASSES[layer]


# ── route parsing / ref ──────────────────────────────────────────────────────

def test_parse_route_verified_shapes():
    assert parse_route("Bus,13") == [("13", "Bus")]
    assert parse_route("13,40") == [("13", None), ("40", None)]
    assert parse_route("Bus,20,Bus,26,Bus,87") == [("20", "Bus"), ("26", "Bus"), ("87", "Bus")]
    assert parse_route("Alt,10,15") == [("10", "Alt"), ("15", None)]
    assert parse_route("Alt.10") == [("10", "Alt")]                # fused form, 45 WY rows
    assert parse_route("89A") == [("89A", None)]                   # letter suffix is part of the number
    assert parse_route(" 7Ro ") == [("7Ro", None)]
    assert parse_route(None) == [] and parse_route("") == [] and parse_route("<Null>") == []


def test_parse_route_unknown_modifier_still_honoured_and_reviewed():
    review = Review()
    assert parse_route("Loop,12", review) == [("12", "Loop")]
    assert parse_route("Spur,55", Review()) == [("55", "Spur")]      # ID pilot: 43 rows
    assert parse_route("bus,5", review) == [("5", "Bus")]           # case-insensitive verified vocab
    assert parse_route("13,Bus", review) == [("13", None)]          # dangling modifier ignored
    keys = {k[0] for k in review.entries}
    assert "route_modifier_unknown" in keys and "route_modifier_dangling" in keys


def test_build_ref_order_dedupe_cap_and_modifier_placement():
    assert build_ref("interstate", "80", "30", None, None, None) == "I-80;US-30"
    assert build_ref("us_hwy", None, "Bus,13", None, None, None) == "US-13 Bus"
    assert build_ref("state_hwy", None, None, "89A", None, None) == "SR-89A"
    assert build_ref("state_hwy", "Bus,25", None, None, None, None) == "I-25 Bus"
    assert build_ref("us_hwy", None, "14,16,20", None, None, None) == "US-14;US-16;US-20"
    assert build_ref("us_hwy", None, "13,13", None, None, None) == "US-13"          # dedupe
    assert build_ref("us_hwy", "80,80", "30,287,26,20", None, None, None).count(";") == 3  # capped at 4


def test_build_ref_fr_cr_fallback_only_for_context_classes():
    assert build_ref("local", None, None, None, "548.3", "71") == "FR-548.3"
    assert build_ref("fourwd", None, None, None, None, "7Ro") == "CR-7Ro"
    assert build_ref("local", None, None, None, None, None) is None
    # a signed road never gets the FR fallback
    assert build_ref("local", None, None, "27", "548.3", None) == "SR-27"
    # highway classes never fall back to FR/CR (interstate with only county_route is nonsense anyway)
    assert build_ref("interstate", None, None, None, "1", "2") is None


# ── value helpers ────────────────────────────────────────────────────────────

def test_originator_codes_verified_vocabulary():
    assert originator_code("U.S. Department of Commerce, U.S. Census Bureau, Geography Division") == "tiger"
    assert originator_code("U.S. Forest Service") == "usfs"
    assert originator_code("National Park Service") == "nps"
    assert originator_code("Alaska Dept. of Transportation") == "akdot"
    assert originator_code("Federal Highways Administration and/or howderfamily.com") == "other"
    assert originator_code(None) == "other"


def test_source_id_normalizes_braced_guids():
    assert source_id("{F47D15AA-9365-4693-A3C8-68A21E643D24}") == "f47d15aa-9365-4693-a3c8-68a21e643d24"
    assert source_id("f47d15aa-9365-4693-a3c8-68a21e643d24") == "f47d15aa-9365-4693-a3c8-68a21e643d24"
    assert source_id("  ") is None and source_id(None) is None


def test_haversine_and_rounding():
    m = haversine_miles(LINE)
    assert 0.48 < m < 0.51                       # 0.01° lon at 44.3N ≈ 0.495 mi
    assert haversine_miles({"type": "LineString", "coordinates": [[0, 0], [0, 1]]}) == pytest.approx(69.09, abs=0.1)
    assert haversine_miles(None) == 0.0 and haversine_miles({"type": "Point", "coordinates": [0, 0]}) == 0.0
    assert round_miles(0.001) == 0.01 and round_miles(0) is None and round_miles(12.3456) == 12.35


def test_clean():
    assert clean(" x ") == "x"
    for v in ("NULL", "<Null>", "", None, "none", "  "):
        assert clean(v) is None


# ── builders: whitelist by construction ──────────────────────────────────────

def test_road_props_is_fresh_and_whitelisted():
    raw = {"permanent_identifier": "{ABC-1}", "tnmfrc": 2, "mtfcc_code": "S1200",
           "name": "Banks Lowman Rd", "interstate": None, "us_route": None, "state_route": "55",
           "county_route": None, "federal_lands_route": None,
           "source_originator": "U.S. Forest Service", "source_datadesc": "USFS Roads 11/2019",
           "globalid": "{X}", "shape_length": 0.01, "stco_fipscode": "16015", "loaddate": "2026-01-01"}
    props = road_props(raw, LINE, Review())
    assert props == {"class": "state_hwy", "name": "Banks Lowman Rd", "ref": "SR-55", "mtfcc": "S1200",
                     "source": "usfs", "source_id": "abc-1", "miles": pytest.approx(0.5, abs=0.02)}
    assert set(props) <= set(WHITELIST) == QA_WHITELIST


def test_road_props_drops_ferry_and_reviews_unknown_originator():
    review = Review()
    assert road_props({"tnmfrc": 7, "permanent_identifier": "a"}, LINE, review) is None
    props = road_props({"tnmfrc": 4, "source_originator": "Somebody Else"}, LINE, review)
    assert props["source"] == "other" and "source_id" not in props
    keys = {k[0] for k in review.entries}
    assert {"road_originator_other", "permanent_identifier"} <= keys


def test_trail_props_rules():
    review = Review()
    assert trail_props({"trailtype": "Snow Trail", "permanentidentifier": "a"}, LINE, review) is None
    assert trail_props({"trailtype": "Water Trail", "permanentidentifier": "a"}, LINE, review) is None
    props = trail_props({"trailtype": "Terra Trail", "permanentidentifier": "{T-1}", "name": None,
                         "maplabel": "Blue Lake Tr", "trailnumber": "317722E", "lengthmiles": 2.345,
                         "sourceoriginator": "U.S. Forest Service", "hikerpedestrian": "Y",
                         "motorcycle": "Null"}, LINE, review)
    assert props == {"class": "trail", "name": "Blue Lake Tr", "ref": "317722E",
                     "source": "usfs", "source_id": "t-1", "miles": 2.35}
    # NULL trailtype is kept (no NULLs observed, but never drop the unknown); lengthmiles 0 -> computed
    props = trail_props({"trailtype": None, "permanentidentifier": "x", "lengthmiles": 0}, LINE, review)
    assert props["class"] == "trail" and 0.48 < props["miles"] < 0.51


def test_resolve_src_finds_gdb_inside_zip(tmp_path):
    z = tmp_path / "TRAN_Idaho_State_GDB.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("TRAN_Idaho_State_GDB.gdb/gdb", "x")
        zf.writestr("TRAN_Idaho_State_GDB.gdb/a00000001.gdbtable", "x")
        zf.writestr("TRAN_Idaho_State_GDB.xml", "x")
    assert resolve_src(str(z)) == f"/vsizip/{z.as_posix()}/TRAN_Idaho_State_GDB.gdb"
    assert resolve_src("src/state.gdb") == "src/state.gdb"


# ── end-to-end without GDAL: --roads-src / --trails-src ──────────────────────

def _write(path: Path, rows):
    with path.open("w", encoding="utf-8") as f:
        for props in rows:
            f.write(json.dumps({"type": "Feature", "geometry": LINE, "properties": props}) + "\n")


def _run_normalize(tmp_path: Path):
    roads = tmp_path / "roads.geojsonl"
    trails = tmp_path / "trails.geojsonl"
    _write(roads, [
        {"permanent_identifier": "r1", "tnmfrc": 1, "mtfcc_code": "S1100", "interstate": "84",
         "source_originator": "U.S. Department of Commerce, U.S. Census Bureau, Geography Division",
         "OWNER_NAME": "never"},
        {"permanent_identifier": "r2", "tnmfrc": 4, "mtfcc_code": "S1400", "name": "SAGEHEN",
         "source_originator": "U.S. Forest Service"},
        {"permanent_identifier": "r3", "tnmfrc": 6, "mtfcc_code": "S1500",
         "source_originator": "U.S. Forest Service", "federal_lands_route": "548.3"},
        {"permanent_identifier": "r4", "tnmfrc": 7, "mtfcc_code": "L4165",
         "source_originator": "Federal Highways Administration and/or howderfamily.com"},
        {"permanent_identifier": "r5", "tnmfrc": 3, "mtfcc_code": "S1200", "state_route": "55",
         "source_originator": "U.S. Department of Commerce, U.S. Census Bureau, Geography Division"},
    ])
    _write(trails, [
        {"permanentidentifier": "t1", "trailtype": "Terra Trail", "name": "Rim Tr", "lengthmiles": 1.5,
         "sourceoriginator": "State"},
        {"permanentidentifier": "t2", "trailtype": "Snow Trail", "name": "Groomed", "lengthmiles": 9},
    ])
    out = tmp_path / "build"
    script = Path(__file__).parent.parent / "normalize_roads_tnm.py"
    subprocess.run([sys.executable, str(script), "--unit", "ID",
                    "--roads-src", str(roads), "--trails-src", str(trails), "--out", str(out)],
                   check=True, capture_output=True, text=True)
    return out


def test_end_to_end_routes_classes_to_layers_with_minzoom(tmp_path):
    out = _run_normalize(tmp_path)
    stats = json.loads((out / "normalize_stats.json").read_text())
    # r5 (tnmfrc 3 + SR-55) is state_hwy — designation-first — so it lands in roads_hwy
    assert stats["kept_by_layer"] == {"roads_hwy": 2, "roads_local": 1, "roads_4wd": 1, "trails_tnm": 1}
    assert stats["roads"]["dropped_by_rule"] == 1 and stats["trails"]["dropped_by_rule"] == 1
    assert stats["roads"]["tnmfrc_hist"] == {"1": 1, "4": 1, "6": 1, "7": 1, "3": 1}
    hwy = [json.loads(l) for l in (out / "roads_hwy.geojsonl").read_text().splitlines()]
    assert hwy[0]["tippecanoe"] == {"minzoom": 5}
    assert hwy[0]["properties"] == {"class": "interstate", "ref": "I-84", "mtfcc": "S1100",
                                    "source": "tiger", "source_id": "r1", "miles": hwy[0]["properties"]["miles"]}
    fourwd = json.loads((out / "roads_4wd.geojsonl").read_text().splitlines()[0])
    assert fourwd["properties"]["ref"] == "FR-548.3" and fourwd["tippecanoe"]["minzoom"] == 9
    text = (out / "roads_hwy.geojsonl").read_text() + (out / "roads_local.geojsonl").read_text()
    assert "OWNER" not in text and "never" not in text
    assert (out / "review_queue_roads_tnm.jsonl").exists()


def test_qa_scan_passes_clean_output_and_tallies_golden(tmp_path):
    out = _run_normalize(tmp_path)
    failures, tallies = scan(out, [-116.45, 44.15, -115.95, 44.45])
    assert failures == []
    assert tallies["counts"]["roads_local"] == 1 and tallies["counts"]["roads_hwy"] == 2
    assert tallies["golden"]["interstate"] == 1 and tallies["golden"]["local"] == 1
    assert tallies["golden"]["state_hwy"] == 1
    assert scan(out, [-100, 30, -99, 31])[1]["golden"]["local"] == 0


def test_qa_scan_fails_on_foreign_key_wrong_layer_bad_source(tmp_path):
    build = tmp_path / "b"
    build.mkdir()
    for layer in LAYER_CLASSES:
        (build / f"{layer}.geojsonl").write_text("")
    _write(build / "roads_hwy.geojsonl", [
        {"class": "interstate", "source": "tiger", "source_id": "a", "owner": "JANE Q PUBLIC"},   # foreign key
        {"class": "local", "source": "tiger", "source_id": "b"},                                   # wrong file
        {"class": "ramp", "source": "esri", "source_id": "c"},                                     # bad source
        {"class": "ramp", "source": "tiger"},                                                      # missing id
    ])
    failures, _ = scan(build, None)
    joined = "\n".join(failures)
    for needle in ("key 'owner'", "class 'local' in roads_hwy", "source 'esri'", "missing source_id"):
        assert needle in joined


def test_size_band_hard_floor_only():
    assert gate_size_band({"zip_bytes": 100_000_000}, 20_000) != []      # 200/MB -> broken read
    assert gate_size_band({"zip_bytes": 100_000_000}, 100_000) == []     # 1,000/MB -> warn only
    assert gate_size_band({}, 5) == []                                    # no config -> skipped


def test_bbox_helpers():
    assert feature_bbox(LINE) == (-116.20, 44.30, -116.19, 44.30)
    assert bbox_intersects((0, 0, 1, 1), (1, 1, 2, 2))          # touching counts (envelope semantics)
    assert not bbox_intersects((0, 0, 1, 1), (1.1, 1.1, 2, 2))
    assert feature_bbox({"type": "Point", "coordinates": [0, 0]}) is None
