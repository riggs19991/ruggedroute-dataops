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


if __name__ == "__main__":
    unittest.main()
