#!/usr/bin/env python3
"""Tests for the BLM GTLF normalizer (designation mapping + free-text season
extraction + review-queue dedup under boilerplate flooding)."""
import json
import os
import tempfile
import unittest

from _test_helpers import feature_line, out_props, read_jsonl, run_normalizer


def run(lines, td, kind="road", hint=None):
    args = ["--kind", kind, "--review-out", os.path.join(td, "rq.jsonl")]
    if hint:
        args += ["--designation-hint", hint]
    return run_normalizer("normalize_gtlf.py", args, lines)


class DesignationMapping(unittest.TestCase):
    def _designation(self, value, hint=None):
        line = feature_line({"GlobalID": "{ABC}", "PLAN_OHV_ROUTE_DSGNTN": value})
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td, hint=hint)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        return out_props(proc)[0]["designation"], rq

    def test_explicit_values_win(self):
        self.assertEqual(self._designation("Open", hint="limited")[0], "open")
        self.assertEqual(self._designation("Limited", hint="open")[0], "limited")
        self.assertEqual(self._designation("Closed", hint="open")[0], "closed")

    def test_not_assessed_falls_back_to_hint(self):
        self.assertEqual(self._designation("Not Assessed", hint="limited")[0], "limited")
        self.assertEqual(self._designation(None, hint="open")[0], "open")

    def test_missing_without_hint_is_unassessed(self):
        d, rq = self._designation(None)
        self.assertEqual(d, "unassessed")
        self.assertEqual(rq, [])

    def test_unrecognized_string_reviewed_and_hinted(self):
        d, rq = self._designation("Seasonally Gated??", hint="limited")
        self.assertEqual(d, "limited")
        self.assertEqual(len(rq), 1)
        self.assertEqual(rq[0]["field"], "plan_ohv_route_dsgntn")


class FreeTextSeasons(unittest.TestCase):
    def test_extractable_dates_become_seasons(self):
        line = feature_line({"GlobalID": "{S1}", "PLAN_OHV_ROUTE_DSGNTN": "Limited",
                             "OHV_DSGNTN_LIM_EXPLAIN": "Open to OHVs 04/01-11/30 only."})
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td, hint="limited")
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        p = out_props(proc)[0]
        self.assertEqual(json.loads(p["seasons"]),
                         [{"cls": "all", "open": "04/01", "close": "11/30"}])
        self.assertEqual(p["limitation_text"], "Open to OHVs 04/01-11/30 only.")
        self.assertEqual(rq, [])

    def test_closure_phrased_dates_never_become_open_seasons(self):
        # Polarity trap: live BLM limitation text is overwhelmingly
        # CLOSURE-phrased — its date range says when the route is CLOSED, so it
        # must never ship as an OPEN season window.
        line = feature_line({"GlobalID": "{C1}", "PLAN_OHV_ROUTE_DSGNTN": "Limited",
                             "OHV_DSGNTN_LIM_EXPLAIN": "Closed 12/1- 4/15"})
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td, hint="limited")
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        p = out_props(proc)[0]
        self.assertNotIn("seasons", p)
        self.assertEqual(p["limitation_text"], "Closed 12/1- 4/15")  # raw text still ships
        self.assertEqual(len(rq), 1)
        self.assertEqual(rq[0]["field"], "ohv_dsgntn_lim_explain_closure")
        self.assertEqual(rq[0]["value"], "Closed 12/1- 4/15")
        self.assertEqual(rq[0]["examples"], ["{C1}"])

    def test_closed_yearlong_never_becomes_full_year_open_window(self):
        # 'Closed yearlong' hits the YEARLONG regex and would emit a full-year
        # OPEN window without the closure gate.
        line = feature_line({"GlobalID": "{C2}",
                             "OHV_DSGNTN_LIM_EXPLAIN": "Closed yearlong"})
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td, hint="limited")
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        self.assertNotIn("seasons", out_props(proc)[0])
        self.assertEqual(rq[0]["field"], "ohv_dsgntn_lim_explain_closure")

    def test_boilerplate_flood_dedupes(self):
        text = "Limited to Designated Routes for Motorized and Mechanical Vehicles."
        lines = [feature_line({"GlobalID": f"{{G{i}}}", "PLAN_OHV_ROUTE_DSGNTN": "Limited",
                               "OHV_DSGNTN_LIM_EXPLAIN": text}) for i in range(50)]
        with tempfile.TemporaryDirectory() as td:
            proc = run(lines, td, hint="limited")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        self.assertEqual(len(rq), 1)
        self.assertEqual(rq[0]["count"], 50)
        self.assertLessEqual(len(rq[0]["examples"]), 3)
        self.assertIn("50 in, 50 out, 50 review-queue entries", proc.stderr)


class Identity(unittest.TestCase):
    def test_globalid_preferred_over_objectid(self):
        line = feature_line({"GlobalID": "{ABC-123}", "OBJECTID": 42})
        with tempfile.TemporaryDirectory() as td:
            p = out_props(run([line], td))[0]
        self.assertEqual(p["source_id"], "{ABC-123}")

    def test_objectid_fallback(self):
        line = feature_line({"OBJECTID": 42})
        with tempfile.TemporaryDirectory() as td:
            p = out_props(run([line], td))[0]
        self.assertEqual(p["source_id"], "42")

    def test_kind_and_passthrough(self):
        line = feature_line({"GlobalID": "{K}", "ROUTE_PRMRY_NM": "Gemini Bridges Rd",
                             "OBSRVE_SRFCE_TYPE": "Natural", "GIS_MILES": 13.4,
                             "OHV_ROUTE_DSGNTN_LIM": "Limited by Season",
                             "PLAN_SEASON_RSTRCT_CODE": "YES"})
        with tempfile.TemporaryDirectory() as td:
            p = out_props(run([line], td, kind="trail", hint="open"))[0]
        self.assertEqual(p["kind"], "trail")
        self.assertEqual(p["source"], "blm_gtlf")
        self.assertEqual(p["name"], "Gemini Bridges Rd")
        self.assertEqual(p["surface"], "Natural")
        self.assertEqual(p["miles"], 13.4)
        self.assertEqual(p["limitation_type"], "Limited by Season")
        self.assertEqual(p["seasonal"], "Seasonal")

    def test_season_rstrct_no_maps_yearlong(self):
        line = feature_line({"GlobalID": "{K2}", "PLAN_SEASON_RSTRCT_CODE": "NO"})
        with tempfile.TemporaryDirectory() as td:
            p = out_props(run([line], td))[0]
        self.assertEqual(p["seasonal"], "Yearlong")


class Tolerance(unittest.TestCase):
    def test_garbage_never_crashes(self):
        lines = ["{{{{", "", "null", feature_line({})]
        with tempfile.TemporaryDirectory() as td:
            proc = run(lines, td, hint="open")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        props = out_props(proc)
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0]["designation"], "open")  # hint applies
        self.assertEqual(rq[0]["field"], "globalid")       # missing id reviewed


if __name__ == "__main__":
    unittest.main()
