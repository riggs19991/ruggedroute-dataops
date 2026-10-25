"""T-0009: county is a display name or absent — bare codes never reach tiles.

FL serves CO_NO as float-strings ('58.0'), VA serves bare FIPS; both translate
through static tables (FDOR order, anchors proven on live tiles 2026-08-11;
Census codes2020). Untranslatable numerics are dropped. Name-carrying sources
pass through.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

_NORM = Path(__file__).resolve().parents[1] / "normalize_parcels.py"
_spec = importlib.util.spec_from_file_location("normalize_parcels_t0009", _NORM)
norm = importlib.util.module_from_spec(_spec)
sys.modules["normalize_parcels_t0009"] = norm
_spec.loader.exec_module(norm)


class NormalizeCountyTest(unittest.TestCase):
    def test_fl_float_string_code_translates(self):
        self.assertEqual("Orange", norm.normalize_county("FL", "58.0"))

    def test_fl_int_code_translates(self):
        self.assertEqual("Miami-Dade", norm.normalize_county("FL", "23"))

    def test_fl_table_is_complete_11_to_77(self):
        self.assertEqual(set(range(11, 78)), set(norm.FL_COUNTY_NAMES))

    def test_va_fips_translates(self):
        self.assertEqual("Fairfax County", norm.normalize_county("VA", "51059"))
        self.assertEqual("Richmond city", norm.normalize_county("VA", "51760.0"))

    def test_va_table_has_all_133_localities(self):
        self.assertEqual(133, len(norm.VA_COUNTY_NAMES))

    def test_untranslatable_numeric_is_dropped(self):
        self.assertIsNone(norm.normalize_county("FL", "99"))
        self.assertIsNone(norm.normalize_county("VA", "51999"))
        # a state with no table never ships a numeric county
        self.assertIsNone(norm.normalize_county("OH", "12345"))

    def test_names_pass_through_untouched(self):
        self.assertEqual("Grand", norm.normalize_county("UT", "Grand"))
        self.assertEqual("Lewis and Clark", norm.normalize_county("MT", "Lewis and Clark"))
        self.assertEqual("St. Croix", norm.normalize_county("WI", "St. Croix"))

    def test_null_and_garbage_stay_none(self):
        self.assertIsNone(norm.normalize_county("FL", None))
        self.assertIsNone(norm.normalize_county("FL", "--"))

    def test_build_props_routes_county_through_translation(self):
        props = norm.build_props(
            {"PARCEL_ID": "X1", "CO_NO": "58.0", "LND_SQFOOT": "87120"},
            {"apn": "PARCEL_ID", "county": "CO_NO", "acres": "LND_SQFOOT"},
            "FL", acres_divisor=43560,
        )
        self.assertEqual({"st": "FL", "apn": "X1", "county": "Orange", "acres": 2.0}, props)

    def test_build_props_drops_untranslatable_code(self):
        props = norm.build_props(
            {"PARCELID": "Y2", "FIPS": "51999"},
            {"apn": "PARCELID", "county": "FIPS", "acres": None},
            "VA",
        )
        self.assertEqual({"st": "VA", "apn": "Y2"}, props)

    # ── T-0009 verifier round: discriminating pins ────────────────────────────

    def test_md_letter_codes_translate_and_unmapped_codes_drop(self):
        # MDP JURSCODE anchors geo-verified on live tiles (Rockville/Annapolis).
        self.assertEqual("Montgomery", norm.normalize_county("MD", "MONT"))
        self.assertEqual("Anne Arundel", norm.normalize_county("MD", "ANNE"))
        self.assertEqual(24, len(norm.MD_COUNTY_NAMES))
        # unmapped code-like token in a table state drops; a real name passes
        self.assertIsNone(norm.normalize_county("MD", "ZZZZ"))
        self.assertEqual("Baltimore City", norm.normalize_county("MD", "Baltimore City"))

    def test_nh_countyid_alphabetical(self):
        # Geo-verified: Concord=7 Merrimack, Nashua=6 Hillsborough.
        self.assertEqual("Merrimack", norm.normalize_county("NH", "7"))
        self.assertEqual("Hillsborough", norm.normalize_county("NH", "6"))
        self.assertEqual(10, len(norm.NH_COUNTY_NAMES))
        self.assertEqual(
            ["Belknap", "Carroll", "Cheshire", "Coos", "Grafton", "Hillsborough",
             "Merrimack", "Rockingham", "Strafford", "Sullivan"],
            [norm.NH_COUNTY_NAMES[i] for i in range(1, 11)],
        )

    def test_in_fips_translates(self):
        # Geo-verified: Indianapolis tile = 18097.
        self.assertEqual("Marion", norm.normalize_county("IN", "18097"))
        self.assertEqual(92, len(norm.IN_COUNTY_NAMES))

    def test_fl_table_is_alphabetical_in_fdor_order(self):
        # FDOR numbers are alphabetical with Miami-Dade filed as Dade and the
        # 'St.' names filed as Saint (so St. Johns/St. Lucie precede Santa Rosa).
        def fdor_key(code: int, name: str) -> str:
            if code == 23:
                return "dade"
            return name.lower().replace("st.", "saint").replace(" ", "")
        names = [fdor_key(c, norm.FL_COUNTY_NAMES[c]) for c in range(11, 78)]
        self.assertEqual(sorted(names), names)

    def test_va_spot_set(self):
        for fips, name in (("51059", "Fairfax County"), ("51600", "Fairfax city"),
                           ("51036", "Charles City County"), ("51760", "Richmond city"),
                           ("51159", "Richmond County")):
            self.assertEqual(name, norm.normalize_county("VA", fips))

    def test_non_integral_numeric_drops(self):
        self.assertIsNone(norm.normalize_county("FL", "58.9"))
        self.assertIsNone(norm.normalize_county("FL", "1" * 400))  # no OverflowError

    def test_sources_map_name_columns_for_mt_and_tx(self):
        import json
        src = json.loads((Path(__file__).resolve().parents[1] / "sources.json").read_text(encoding="utf-8"))
        self.assertEqual("CountyName", src["MT"]["fields"]["county"])
        for unit in ("TX_1", "TX_2", "TX_3"):
            self.assertEqual("COUNTY", src[unit]["fields"]["county"])

    def test_normalize_emits_attr_null_rate_stats(self):
        # Stubbed ogr2ogr stream: 3 features — full, county-less, bare-code county.
        import io as _io, json as _json, tempfile, unittest.mock as mock
        lines = [
            _json.dumps({"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 1]},
                         "properties": {"PARCEL_ID": "A", "CO_NO": "58", "LND_SQFOOT": "43560"}}),
            _json.dumps({"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 1]},
                         "properties": {"PARCEL_ID": "B"}}),
            _json.dumps({"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 1]},
                         "properties": {"PARCEL_ID": "C", "CO_NO": "99"}}),
        ]
        fake = mock.Mock()
        fake.stdout = _io.StringIO("\n".join(lines) + "\n")
        fake.wait = lambda: 0
        with mock.patch.object(norm, "ogr_stream", return_value=fake), \
             mock.patch.object(norm, "resolve_src", side_effect=lambda s: s):
            stats: dict = {}
            with tempfile.TemporaryDirectory() as td:
                norm.normalize(["fake.zip"], None,
                               {"apn": "PARCEL_ID", "county": "CO_NO", "acres": "LND_SQFOOT"},
                               "FL", Path(td) / "out.geojsonl", stats, acres_divisor=43560)
        self.assertEqual(3, stats["kept"])
        rates = stats["attr_null_rates"]
        self.assertEqual(0.0, rates["apn"])
        self.assertEqual(round(2 / 3, 4), rates["county"])  # B absent + C dropped code
        self.assertEqual(round(2 / 3, 4), rates["acres"])


if __name__ == "__main__":
    unittest.main()
