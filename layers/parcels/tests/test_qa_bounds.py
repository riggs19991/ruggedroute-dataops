"""T-0010: the Gate-3 bounds parser must read go-pmtiles 1.31 `show` output.

The original regex expected the legacy `bounds: w,s,e,n` line; go-pmtiles 1.31
prints a parenthesised long/lat pair plus an `antimeridian_adjusted_bounds`
line, so the tile gate silently skipped on every unit from the first parcels
run. These are literal output forms (the 1.31 ones captured on roads_tnm pilot
run 31989953542).
"""

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

_QA = Path(__file__).resolve().parents[1] / "qa_parcels.py"
_spec = importlib.util.spec_from_file_location("qa_parcels_t0010", _QA)
qa = importlib.util.module_from_spec(_spec)
sys.modules["qa_parcels_t0010"] = qa
_spec.loader.exec_module(qa)

EXPECTED = (-117.239175, 41.988226, -111.043699, 49.000822)

V131_PAREN = (
    "tile type: mvt\n"
    "bounds: (long: -117.239175, lat: 41.988226) (long: -111.043699, lat: 49.000822)\n"
    "min zoom: 13\n"
)
# Distinct values on the antimeridian line so a regex-order swap fails the
# precedence test (verifier deferred finding 3, T-0010).
ANTIMERIDIAN_EXPECTED = (-117.0, 42.0, -111.5, 48.5)
V131_ANTIMERIDIAN = (
    V131_PAREN
    + "antimeridian_adjusted_bounds -117.0,42.0,-111.5,48.5\n"
)
LEGACY = "bounds: -117.239175,41.988226,-111.043699,49.000822\n"


def _bounds_for(output: str):
    fake = mock.Mock()
    fake.stdout = output
    with mock.patch.object(qa.subprocess, "run", return_value=fake):
        return qa.pmtiles_bounds(Path("ignored.pmtiles"))


class PmtilesBoundsTest(unittest.TestCase):
    def test_131_paren_pair_form(self):
        self.assertEqual(EXPECTED, _bounds_for(V131_PAREN))

    def test_131_antimeridian_line_wins(self):
        self.assertEqual(ANTIMERIDIAN_EXPECTED, _bounds_for(V131_ANTIMERIDIAN))

    def test_legacy_comma_form_still_parses(self):
        self.assertEqual(EXPECTED, _bounds_for(LEGACY))

    def test_garbage_returns_none_not_crash(self):
        self.assertIsNone(_bounds_for("pmtiles spec version: 3\n"))


if __name__ == "__main__":
    unittest.main()
