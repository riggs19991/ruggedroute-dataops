"""Stage 3 parcels: whitelist-by-construction + QA hard-gate tests.

The one invariant that matters: owner names/addresses can NEVER reach the
output, no matter what the source publishes or what sources.json says. These
tests attack it from three sides — the props builder, the field-mapping
validator, and the QA scanner that backstops both.
"""

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from normalize_parcels import build_props, check_mapping, clean, resolve_src  # noqa: E402
from qa_parcels import WHITELIST, gate_whitelist  # noqa: E402

MAPPING = {"apn": "PARCEL_ID", "county": "COUNTY_NM", "acres": "GIS_ACRES"}


def test_build_props_strips_everything_but_the_whitelist():
    raw = {
        "PARCEL_ID": "12-345-0067",
        "COUNTY_NM": "Mesa",
        "GIS_ACRES": "41.279",
        "OWNER_NAME": "JANE Q PUBLIC",          # must never survive
        "MAIL_ADDR": "123 Main St",              # must never survive
        "TOTAL_VALUE": 250000,
    }
    props = build_props(raw, MAPPING, "UT")
    assert props == {"st": "UT", "apn": "12-345-0067", "county": "Mesa", "acres": 41.28}
    assert set(props) <= WHITELIST


def test_build_props_case_insensitive_source_headers():
    # Shapefile headers get truncated/recased vs REST metadata
    raw = {"parcel_id": "99", "county_nm": "Iron", "gis_acres": 1}
    props = build_props(raw, MAPPING, "UT")
    assert props["apn"] == "99" and props["county"] == "Iron"


def test_build_props_missing_and_nullish_fields_omitted():
    props = build_props({"PARCEL_ID": " null ", "GIS_ACRES": "not-a-number"}, MAPPING, "MT")
    assert props == {"st": "MT"}
    assert build_props({}, {"apn": None, "county": None, "acres": None}, "TX") == {"st": "TX"}


def test_build_props_nonpositive_acres_dropped():
    assert "acres" not in build_props({"GIS_ACRES": 0}, MAPPING, "WI")
    assert "acres" not in build_props({"GIS_ACRES": -3}, MAPPING, "WI")


def test_build_props_acres_divisor_converts_sqft():
    # FL publishes LND_SQFOOT — sources.json carries acres_divisor 43560
    mapping = {"apn": "PARCEL_ID", "county": "CO_NO", "acres": "LND_SQFOOT"}
    props = build_props({"LND_SQFOOT": 87120}, mapping, "FL", acres_divisor=43560)
    assert props["acres"] == 2.0


def test_check_mapping_refuses_owner_and_address_fields():
    for field in ("OWNER_NAME", "OwnerAddr", "MAIL_CITY", "TAXPAYER_1", "own_full"):
        with pytest.raises(SystemExit):
            check_mapping({"apn": field, "county": None, "acres": None})


def test_check_mapping_allows_county_name_fields():
    # 'name' is only forbidden in the apn slot — COUNTYNAME is legitimate
    check_mapping({"apn": "PIN", "county": "COUNTYNAME", "acres": "DEED_ACRES"})
    with pytest.raises(SystemExit):
        check_mapping({"apn": "NAME_ID", "county": None, "acres": None})


def test_resolve_src_finds_gdb_inside_zip(tmp_path):
    z = tmp_path / "state.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("Parcels_2026.gdb/gdb", "x")
        zf.writestr("Parcels_2026.gdb/a00000001.gdbtable", "x")
        zf.writestr("readme.txt", "x")
    assert resolve_src(str(z)) == f"/vsizip/{z.as_posix()}/Parcels_2026.gdb"


def test_resolve_src_finds_shp_inside_zip(tmp_path):
    z = tmp_path / "state.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("parcels/MontanaParcels.shp", "x")
        zf.writestr("parcels/MontanaParcels.dbf", "x")
    assert resolve_src(str(z)) == f"/vsizip/{z.as_posix()}/parcels/MontanaParcels.shp"


def test_resolve_src_passthrough_for_non_zip():
    assert resolve_src("build/UT_raw.geojsonl") == "build/UT_raw.geojsonl"
    assert resolve_src("src/state.gdb") == "src/state.gdb"


def test_clean():
    assert clean("  x ") == "x"
    assert clean("NULL") is None and clean("") is None and clean(None) is None


# ── QA hard gate ───────────────────────────────────────────────────────────────

def _write_geojsonl(path: Path, features):
    with path.open("w", encoding="utf-8") as f:
        for props in features:
            f.write(json.dumps({
                "type": "Feature",
                "geometry": {"type": "MultiPolygon",
                             "coordinates": [[[[0, 0], [0, 1], [1, 1], [0, 0]]]]},
                "properties": props}) + "\n")


def test_gate_whitelist_passes_clean_output(tmp_path):
    p = tmp_path / "parcels.geojsonl"
    _write_geojsonl(p, [{"st": "UT", "apn": "1", "county": "Iron", "acres": 2.5},
                        {"st": "UT"}])
    failures, count = gate_whitelist(p)
    assert failures == [] and count == 2


def test_gate_whitelist_fails_on_smuggled_owner_key(tmp_path):
    p = tmp_path / "parcels.geojsonl"
    _write_geojsonl(p, [{"st": "UT", "apn": "1", "owner": "JANE Q PUBLIC"}])
    failures, _ = gate_whitelist(p)
    assert any("owner" in f for f in failures)


def test_gate_whitelist_fails_on_missing_st(tmp_path):
    p = tmp_path / "parcels.geojsonl"
    _write_geojsonl(p, [{"apn": "1"}])
    failures, _ = gate_whitelist(p)
    assert any("missing st" in f for f in failures)


# ── integration: full normalize through ogr2ogr (CI always has GDAL) ──────────

@pytest.mark.skipif(shutil.which("ogr2ogr") is None, reason="GDAL not installed")
def test_normalize_end_to_end_strips_owner_fields(tmp_path):
    src = tmp_path / "raw.geojsonl"
    _write_geojsonl(src, [
        {"PARCEL_ID": "A-1", "COUNTY_NM": "Mesa", "GIS_ACRES": 40,
         "OWNER_NAME": "JANE Q PUBLIC", "MAIL_ADDR": "123 Main St"},
        {"PARCEL_ID": "A-2", "COUNTY_NM": "Mesa", "GIS_ACRES": 0.4,
         "OWNER_NAME": "JOHN DOE"},
    ])
    out = tmp_path / "build"
    script = Path(__file__).parent.parent / "normalize_parcels.py"
    subprocess.run([sys.executable, str(script), "--unit", "UT",
                    "--src", str(src), "--out", str(out),
                    "--apn-field", "PARCEL_ID", "--county-field", "COUNTY_NM",
                    "--acres-field", "GIS_ACRES"],
                   check=True, capture_output=True, text=True)
    failures, count = gate_whitelist(out / "parcels.geojsonl")
    assert failures == [] and count == 2
    text = (out / "parcels.geojsonl").read_text()
    assert "JANE" not in text and "Main St" not in text and "OWNER" not in text
    stats = json.loads((out / "normalize_stats.json").read_text())
    assert stats["kept"] == 2
