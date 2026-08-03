#!/usr/bin/env python3
"""Season-parser test corpus, including known-typo strings from the wild (master plan §11
Stage 1 verification: 0 crashes, 100% of failures land in the review queue)."""
import unittest

from normalize_mvum import parse_seasons, truthy


class SeasonParser(unittest.TestCase):
    def test_simple_range(self):
        s, ok = parse_seasons("03/01 - 08/31")
        self.assertTrue(ok)
        self.assertEqual(s, [{"open": "03/01", "close": "08/31"}])

    def test_no_spaces_single_digits(self):
        s, ok = parse_seasons("3/1-8/31")
        self.assertTrue(ok)
        self.assertEqual(s, [{"open": "03/01", "close": "08/31"}])

    def test_multiple_ranges(self):
        s, ok = parse_seasons("05/16 - 09/14 09/15 - 12/01")
        self.assertTrue(ok)
        self.assertEqual(len(s), 2)

    def test_yearlong_variants(self):
        for t in ("yearlong", "Year-long", "YEAR ROUND", "all year", "01/01 - 12/31"):
            s, ok = parse_seasons(t)
            self.assertTrue(ok, t)
            self.assertEqual(s, [{"open": "01/01", "close": "12/31"}], t)

    def test_empty_is_ok(self):
        for t in (None, "", "   "):
            s, ok = parse_seasons(t)
            self.assertTrue(ok)
            self.assertEqual(s, [])

    def test_garbage_goes_to_review(self):
        for t in ("open when dry", "13/45 - 99/99", "call ranger district", "N/A"):
            s, ok = parse_seasons(t)
            self.assertFalse(ok, t)
            self.assertEqual(s, [], t)

    def test_dash_variants(self):
        s, ok = parse_seasons("04/15 to 11/30")
        self.assertTrue(ok)
        s2, ok2 = parse_seasons("04/15 thru 11/30")
        self.assertTrue(ok2)
        self.assertEqual(s, s2)

    def test_mixed_valid_and_garbage_extracts_valid(self):
        s, ok = parse_seasons("06/01 - 10/15 (weather permitting??)")
        self.assertTrue(ok)
        self.assertEqual(s, [{"open": "06/01", "close": "10/15"}])


class Truthy(unittest.TestCase):
    def test_values(self):
        self.assertTrue(truthy("Y"))
        self.assertTrue(truthy("open"))
        self.assertFalse(truthy(None))
        self.assertFalse(truthy(""))
        self.assertFalse(truthy("N"))
        self.assertFalse(truthy("null"))


if __name__ == "__main__":
    unittest.main()
