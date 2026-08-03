#!/usr/bin/env python3
"""Tests for the NPS Public Roads normalizer."""
import json
import os
import tempfile
import unittest

from _test_helpers import feature_line, out_props, read_jsonl, run_normalizer


def run(lines, td):
    return run_normalizer("normalize_nps_roads.py",
                          ["--review-out", os.path.join(td, "rq.jsonl")], lines)


class HappyPath(unittest.TestCase):
    def test_full_feature(self):
        line = feature_line({
            "GEOMETRYID": "{65263473-8D80-4501-BB14-3B3D3663909B}",
            "RDNAME": "Titus Canyon Road", "RTENUMBER": "TC1",
            "RDCLASS": "Secondary", "RDSURFACE": "Gravel", "RDSTATUS": "Existing",
            "RDHICLEAR": "Yes", "RDMAINTAINER": "National Park Service",
            "UNITCODE": "DEVA", "UNITNAME": "Death Valley National Park",
            "SEASONAL": "Yes", "SEASDESC": "Closed in summer; open 10/15-05/15",
            "OPENTOPUBLIC": None,
        })
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        p = out_props(proc)[0]
        self.assertEqual(p["source"], "nps_roads")
        self.assertEqual(p["kind"], "road")
        self.assertEqual(p["source_id"], "{65263473-8D80-4501-BB14-3B3D3663909B}")
        self.assertEqual(p["name"], "Titus Canyon Road")
        self.assertEqual(p["road_class"], "Secondary")
        self.assertEqual(p["surface"], "Gravel")
        self.assertEqual(p["hiclear"], "Yes")
        self.assertEqual(p["unit"], "DEVA")
        self.assertEqual(p["seasonal"], "Seasonal")
        self.assertEqual(json.loads(p["seasons"]),
                         [{"cls": "all", "open": "10/15", "close": "05/15"}])
        self.assertEqual(p["designation"], "unassessed")  # OPENTOPUBLIC null -> never fabricate
        self.assertEqual(rq, [])

    def test_explicit_opentopublic_yes(self):
        line = feature_line({"GEOMETRYID": "{G}", "OPENTOPUBLIC": "Yes"})
        with tempfile.TemporaryDirectory() as td:
            p = out_props(run([line], td))[0]
        self.assertEqual(p["designation"], "open")

    def test_seasonal_no_is_yearlong(self):
        line = feature_line({"GEOMETRYID": "{G}", "SEASONAL": "No"})
        with tempfile.TemporaryDirectory() as td:
            p = out_props(run([line], td))[0]
        self.assertEqual(p["seasonal"], "Yearlong")


class UnknownHandling(unittest.TestCase):
    def test_unknown_values_dropped(self):
        line = feature_line({"GEOMETRYID": "{G}", "RDCLASS": "Unknown",
                             "RDSURFACE": "Unknown", "RDHICLEAR": "Unknown",
                             "SEASONAL": "Unknown"})
        with tempfile.TemporaryDirectory() as td:
            p = out_props(run([line], td))[0]
        for absent in ("road_class", "surface", "hiclear", "seasonal"):
            self.assertNotIn(absent, p)

    def test_maplabel_fallback_and_blank_label(self):
        lines = [
            feature_line({"GEOMETRYID": "{A}", "MAPLABEL": "Essex Ct"}),
            feature_line({"GEOMETRYID": "{B}", "MAPLABEL": " "}),
        ]
        with tempfile.TemporaryDirectory() as td:
            props = out_props(run(lines, td))
        self.assertEqual(props[0]["name"], "Essex Ct")
        self.assertNotIn("name", props[1])


class Identity(unittest.TestCase):
    def test_id_fallback_chain(self):
        lines = [
            feature_line({"GEOMETRYID": "{G}", "FEATUREID": "F", "OBJECTID": 1}),
            feature_line({"FEATUREID": "F2", "OBJECTID": 2}),
            feature_line({"OBJECTID": 3}),
            feature_line({}),
        ]
        with tempfile.TemporaryDirectory() as td:
            proc = run(lines, td)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        props = out_props(proc)
        self.assertEqual(props[0]["source_id"], "{G}")
        self.assertEqual(props[1]["source_id"], "F2")
        self.assertEqual(props[2]["source_id"], "3")
        self.assertNotIn("source_id", props[3])
        self.assertEqual(rq[0]["field"], "geometryid")


class SeasonPolarity(unittest.TestCase):
    def test_closure_phrased_seasdesc_never_becomes_open_seasons(self):
        # Polarity trap (same as BLM GTLF): closure-phrased SEASDESC dates say
        # when the road is CLOSED — never ship them as an OPEN window.
        line = feature_line({"GEOMETRYID": "{P1}",
                             "SEASDESC": "Closed 11/15-05/15"})
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        self.assertNotIn("seasons", out_props(proc)[0])
        self.assertEqual(len(rq), 1)
        self.assertEqual(rq[0]["field"], "seasdesc_closure")
        self.assertEqual(rq[0]["value"], "Closed 11/15-05/15")
        self.assertEqual(rq[0]["examples"], ["{P1}"])

    def test_open_phrased_seasdesc_keeps_seasons(self):
        line = feature_line({"GEOMETRYID": "{P2}",
                             "SEASDESC": "Open 05/01-11/01"})
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        self.assertEqual(json.loads(out_props(proc)[0]["seasons"]),
                         [{"cls": "all", "open": "05/01", "close": "11/01"}])
        self.assertEqual(rq, [])

    def test_closure_wording_with_affirmative_open_keeps_seasons(self):
        # OPEN_HINT overrides CLOSURE_HINT: the date range is affirmatively open.
        line = feature_line({"GEOMETRYID": "{P3}",
                             "SEASDESC": "Closed in summer; open 10/15-05/15"})
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        self.assertEqual(json.loads(out_props(proc)[0]["seasons"]),
                         [{"cls": "all", "open": "10/15", "close": "05/15"}])
        self.assertEqual(rq, [])


class Tolerance(unittest.TestCase):
    def test_seasdesc_garbage_reviewed(self):
        line = feature_line({"GEOMETRYID": "{G}",
                             "SEASDESC": "Call the park for winter status"})
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        self.assertNotIn("seasons", out_props(proc)[0])
        self.assertEqual(len(rq), 1)
        self.assertEqual(rq[0]["field"], "seasdesc")
        self.assertEqual(rq[0]["examples"], ["{G}"])

    def test_garbage_stream_never_crashes(self):
        lines = ["]", "[", "not json", feature_line({"GEOMETRYID": "{G}"})]
        with tempfile.TemporaryDirectory() as td:
            proc = run(lines, td)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(out_props(proc)), 1)


if __name__ == "__main__":
    unittest.main()
