"""Unit + integration tests for the Stage 2 lands normalizer.

Unit tests pin the mapping contract (MGR_MAP ↔ client LandTileFeatureParser /
LayerRegistry.LANDS_FILL_COLORS). The integration test builds a tiny FileGDB-
shaped source (GeoPackage — same OGR path) end-to-end through normalize_lands
and asserts the emitted GeoJSONSeq contract.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from normalize_lands import (  # noqa: E402
    ACCESS_KEEP,
    MGR_MAP,
    OVERLAY_KIND,
    clean,
    detect_layer,
)

# Mirror of the Android contract (LayerRegistry.LANDS_FILL_COLORS keys +
# FED_OTHER handling). Change both sides together or neither.
CLIENT_MGR_CODES = {
    "BLM", "USFS", "NPS", "FWS", "BOR", "FED_OTHER", "TRIBAL", "DOD",
    "ST_PARK", "ST_WILDLIFE", "ST_TRUST", "ST_FOREST", "ST_OTHER", "LOCAL", "NGO",
}


class TestMgrMap:
    def test_private_and_unknown_are_dropped(self):
        assert MGR_MAP["PVT"] is None
        assert MGR_MAP["UNK"] is None

    def test_every_mapped_code_is_client_vocabulary(self):
        for padus_code, mgr in MGR_MAP.items():
            if mgr is not None:
                assert mgr in CLIENT_MGR_CODES, (
                    f"{padus_code} maps to {mgr}, unknown to the client contract"
                )

    def test_trust_boards_map_to_st_trust(self):
        # SLB = State Land Board (UT SITLA class), SDOL = State Dept of Land (AZ)
        assert MGR_MAP["SLB"] == "ST_TRUST"
        assert MGR_MAP["SDOL"] == "ST_TRUST"

    def test_army_corps_is_not_reclamation(self):
        # USACE rec lands are public federal but NOT Bureau of Reclamation --
        # mislabeling agencies is a trust-destroying bug in a land app.
        assert MGR_MAP["USACE"] == "FED_OTHER"
        assert MGR_MAP["USBR"] == "BOR"

    def test_tribal_codes_collapse_to_tribal(self):
        assert MGR_MAP["TRIB"] == "TRIBAL"
        assert MGR_MAP["BIA"] == "TRIBAL"

    def test_full_padus_domain_is_covered(self):
        # Complete Agency Name domain harvested from the 4.1 GDB domain table
        # (2026-08-07). A new PAD-US code lands in `unmapped` stats and fails
        # QA loudly -- this test documents today's full coverage.
        harvested = {
            "TVA", "BLM", "BOEM", "USBR", "FWS", "USFS", "DOD", "USACE", "DOE",
            "NPS", "NRCS", "ARS", "BIA", "NOAA", "BPA", "OTHF", "TRIB", "SPR",
            "SDC", "SLB", "SFW", "SDNR", "SDOL", "OTHS", "REG", "RWD", "CITY",
            "CNTY", "UNKL", "NGO", "PVT", "UNK", "JNT",
        }
        missing = harvested - set(MGR_MAP)
        assert not missing, f"harvested PAD-US codes missing from MGR_MAP: {missing}"


class TestSmallHelpers:
    def test_clean_drops_null_shapes(self):
        assert clean(None) is None
        assert clean("") is None
        assert clean("   ") is None
        assert clean("null") is None
        assert clean("NULL") is None
        assert clean(" Moab Field Office ") == "Moab Field Office"

    def test_access_keep_excludes_unknown(self):
        assert ACCESS_KEEP == {"OA", "RA", "XA"}  # UK stays out by contract

    def test_overlay_kinds(self):
        assert OVERLAY_KIND == {"WA": "wilderness", "WSA": "wsa"}


needs_gdal = pytest.mark.skipif(
    shutil.which("ogr2ogr") is None, reason="GDAL not installed"
)


@needs_gdal
class TestEndToEnd:
    @pytest.fixture()
    def source_gpkg(self, tmp_path: Path) -> Path:
        """Tiny PAD-US-shaped source: Fee + Designation + Comb layers."""
        def fc(features):
            return json.dumps({"type": "FeatureCollection", "features": features})

        def square(x, y, size=0.1):
            return {
                "type": "Polygon",
                "coordinates": [[[x, y], [x + size, y], [x + size, y + size], [x, y + size], [x, y]]],
            }

        fee = fc([
            {"type": "Feature", "properties": {
                "Mang_Name": "BLM", "Unit_Nm": "Test Field Office",
                "Pub_Access": "OA", "GIS_Acres": 100},
             "geometry": square(0, 0)},
            {"type": "Feature", "properties": {
                "Mang_Name": "SLB", "Unit_Nm": "Trust Section",
                "Pub_Access": "UK", "GIS_Acres": 40},
             "geometry": square(1, 0)},
            {"type": "Feature", "properties": {
                "Mang_Name": "PVT", "Unit_Nm": None,
                "Pub_Access": "XA", "GIS_Acres": 7},
             "geometry": square(2, 0)},
        ])
        designation = fc([
            {"type": "Feature", "properties": {"Des_Tp": "WA", "Unit_Nm": "Test Wilderness"},
             "geometry": square(0, 1)},
            {"type": "Feature", "properties": {"Des_Tp": "ACEC", "Unit_Nm": "Not An Overlay"},
             "geometry": square(1, 1)},
            {"type": "Feature", "properties": {"Des_Tp": "WSA", "Unit_Nm": None},
             "geometry": square(2, 1)},
        ])
        comb = fc([
            {"type": "Feature", "properties": {
                "Category": "Proclamation", "Mang_Name": "TRIB",
                "Unit_Nm": "Test Reservation", "Pub_Access": "UK", "GIS_Acres": 500},
             "geometry": square(0, 2)},
            {"type": "Feature", "properties": {
                "Category": "Proclamation", "Mang_Name": "USFS",
                "Unit_Nm": "Forest ADMIN EXTENT — never ownership",
                "Pub_Access": "OA", "GIS_Acres": 900},
             "geometry": square(1, 2)},
            {"type": "Feature", "properties": {
                "Category": "Fee", "Mang_Name": "DOD",
                "Unit_Nm": "Fee-category dupe — Fee layer's job, not ours",
                "Pub_Access": "XA", "GIS_Acres": 30},
             "geometry": square(2, 2)},
        ])

        gpkg = tmp_path / "padus_test.gpkg"
        for layer, payload in [
            ("PADUS9_9Fee_State_XX", fee),
            ("PADUS9_9Designation_State_XX", designation),
            ("PADUS9_9Comb_DOD_Trib_NGP_Fee_Desig_Ease_State_XX", comb),
        ]:
            src = tmp_path / f"{layer}.json"
            src.write_text(payload)
            subprocess.run(
                ["ogr2ogr", "-f", "GPKG", "-append", str(gpkg), str(src), "-nln", layer],
                check=True, capture_output=True,
            )
        return gpkg

    def _lines(self, path: Path) -> list[dict]:
        return [json.loads(l.strip().lstrip("\x1e"))
                for l in path.read_text().splitlines() if l.strip()]

    def test_full_run(self, source_gpkg: Path, tmp_path: Path):
        out = tmp_path / "build"
        script = Path(__file__).parent.parent / "normalize_lands.py"
        subprocess.run(
            [sys.executable, str(script), "--gdb", str(source_gpkg), "--out", str(out)],
            check=True, capture_output=True, text=True,
        )

        fee = self._lines(out / "land_fee.geojsonl")
        by_mgr = {f["properties"]["mgr"]: f["properties"] for f in fee}

        # PVT dropped; BLM + ST_TRUST + TRIBAL-extent kept; USFS admin extent
        # and Fee-category comb rows NEVER leak through the extents pass.
        assert set(by_mgr) == {"BLM", "ST_TRUST", "TRIBAL"}
        assert by_mgr["BLM"] == {"mgr": "BLM", "unit": "Test Field Office", "access": "OA"}
        assert "access" not in by_mgr["ST_TRUST"]          # UK dropped
        assert by_mgr["TRIBAL"]["unit"] == "Test Reservation"

        overlay = self._lines(out / "land_overlay.geojsonl")
        kinds = sorted(f["properties"]["kind"] for f in overlay)
        assert kinds == ["wilderness", "wsa"]              # ACEC excluded
        named = [f["properties"] for f in overlay if f["properties"]["kind"] == "wilderness"]
        assert named[0]["name"] == "Test Wilderness"

        stats = json.loads((out / "normalize_stats.json").read_text())
        assert stats["fee_kept"] == 2
        assert stats["fee_dropped_private"] == 1
        assert stats["fee_unmapped"] == 0
        assert stats["dod_tribal_extent_counts"] == {"TRIBAL": 1}
        assert stats["acres_by_mgr"]["TRIBAL"] == 500

    def test_detect_layer(self, source_gpkg: Path):
        assert "Fee" in detect_layer(str(source_gpkg), "Fee")
        assert detect_layer(str(source_gpkg), "Nonexistent") is None
