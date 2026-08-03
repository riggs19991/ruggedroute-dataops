#!/usr/bin/env python3
"""Tests for the RoadCore (roads_context) normalizer."""
import os
import tempfile
import unittest

from _test_helpers import feature_line, out_props, read_jsonl, run_normalizer


def run(lines, td):
    return run_normalizer("normalize_roadcore.py",
                          ["--review-out", os.path.join(td, "rq.jsonl")], lines)


class HappyPath(unittest.TestCase):
    def test_full_feature(self):
        line = feature_line({
            "RTE_CN": "RC100", "ID": "9407A", "NAME": "SCHNEBLY HILL",
            "SYMBOL_CODE": "2", "SYMBOL_NAME": "Gravel Road",
            "SURFACE_TYPE": "AGG - CRUSHED AGGREGATE", "OPER_MAINT_LEVEL": "2 - HIGH CLEARANCE VEHICLES",
            "OBJECTIVE_MAINT_LEVEL": "3 - SUITABLE FOR PASSENGER CARS",
            "OPENFORUSETO": "ALL", "ROUTE_STATUS": "EX", "JURISDICTION": "FS - FOREST SERVICE",
            "GIS_MILES": 12.1, "FUNCTIONAL_CLASS": "L - LOCAL",
        })
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        p = out_props(proc)[0]
        self.assertEqual(p["source"], "usfs_roadcore")
        self.assertEqual(p["kind"], "road")
        self.assertEqual(p["source_id"], "RC100")
        self.assertEqual(p["route_no"], "9407A")
        self.assertEqual(p["maint_level"], "2 - HIGH CLEARANCE VEHICLES")
        self.assertEqual(p["objective_maint_level"], "3 - SUITABLE FOR PASSENGER CARS")
        self.assertEqual(p["surface"], "AGG - CRUSHED AGGREGATE")
        self.assertEqual(p["symbol"], "2")
        self.assertEqual(p["openforuseto"], "ALL")
        self.assertEqual(p["miles"], 12.1)
        self.assertEqual(rq, [])

    def test_designation_always_unassessed(self):
        # RoadCore is legality-agnostic — even when the data looks 'open'.
        line = feature_line({"RTE_CN": "RC1", "OPENFORUSETO": "PUBLIC",
                             "ROUTE_STATUS": "EX"})
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td)
        self.assertEqual(out_props(proc)[0]["designation"], "unassessed")


class Tolerance(unittest.TestCase):
    def test_missing_fields_and_garbage_never_crash(self):
        lines = [
            feature_line({}),
            "utter garbage {{{",
            feature_line({"ID": "125"}),  # missing rte_cn
        ]
        with tempfile.TemporaryDirectory() as td:
            proc = run(lines, td)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        props = out_props(proc)
        self.assertEqual(len(props), 2)  # garbage line dropped
        self.assertEqual(len(rq), 1)     # deduped: 2 occurrences of missing rte_cn
        self.assertEqual(rq[0]["field"], "rte_cn")
        self.assertEqual(rq[0]["count"], 2)
        self.assertIn("normalize_roadcore: 2 in, 2 out, 2 review-queue entries", proc.stderr)


if __name__ == "__main__":
    unittest.main()
