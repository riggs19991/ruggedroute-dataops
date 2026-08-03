#!/usr/bin/env python3
"""Tests for the NFS Trails normalizer (tileset + MVUM-enrichment sidecar)."""
import json
import os
import tempfile
import unittest

from _test_helpers import feature_line, out_props, read_jsonl, run_normalizer


def run(lines, td, attrs_out=None):
    args = ["--review-out", os.path.join(td, "rq.jsonl")]
    if attrs_out:
        args += ["--attrs-out", attrs_out]
    return run_normalizer("normalize_nfs_trails.py", args, lines)


class HappyPath(unittest.TestCase):
    def test_motorized_trail(self):
        line = feature_line({
            "TRAIL_CN": "138153010602", "TRAIL_NO": "15EV67",
            "TRAIL_NAME": "DORRINGTON OHV", "TRAIL_CLASS": "3",
            "TRAIL_SURFACE": "NAT - NATIVE MATERIAL", "TERRA_MOTORIZED": "Y",
            "SNOW_MOTORIZED": "N/A", "GIS_MILES": 4.2,
            "MOTORCYCLE_MANAGED": "04/15-12/15", "ATV_MANAGED": "N/A",
            "FOURWD_MANAGED": None, "E_BIKE_CLASS1_MANAGED": "01/01-12/31",
        })
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        p = out_props(proc)[0]
        self.assertEqual(p["source"], "usfs_nfs_trails")
        self.assertEqual(p["kind"], "trail")
        self.assertEqual(p["source_id"], "138153010602")
        self.assertEqual(p["route_no"], "15EV67")
        self.assertEqual(p["designation"], "open")
        self.assertEqual(json.loads(p["vehicle_flags"]), {"moto": 1, "ebike1": 1})
        self.assertEqual(json.loads(p["seasons"]), [
            {"cls": "moto", "open": "04/15", "close": "12/15"},
            {"cls": "ebike1", "open": "01/01", "close": "12/31"},
        ])
        self.assertEqual(p["seasonal"], "Seasonal")
        self.assertEqual(p["terra_motorized"], "Y")
        self.assertEqual(rq, [])

    def test_yearlong_only_is_yearlong(self):
        line = feature_line({"TRAIL_CN": "C1", "TERRA_MOTORIZED": "Y",
                             "MOTORCYCLE_MANAGED": "01/01-12/31"})
        with tempfile.TemporaryDirectory() as td:
            p = out_props(run([line], td))[0]
        self.assertEqual(p["seasonal"], "Yearlong")

    def test_na_everywhere_is_quiet(self):
        # N/A sentinels must produce NO flags, NO seasons, NO review entries.
        line = feature_line({"TRAIL_CN": "C2", "TERRA_MOTORIZED": "N/A",
                             "MOTORCYCLE_MANAGED": "N/A", "ATV_MANAGED": "N/A",
                             "FOURWD_MANAGED": "N/A"})
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        p = out_props(proc)[0]
        self.assertEqual(p["designation"], "unassessed")
        self.assertNotIn("vehicle_flags", p)
        self.assertNotIn("seasons", p)
        self.assertEqual(rq, [])

    def test_unparsable_managed_value_goes_to_review(self):
        line = feature_line({"TRAIL_CN": "C3", "TERRA_MOTORIZED": "Y",
                             "MOTORCYCLE_MANAGED": "open when dry"})
        with tempfile.TemporaryDirectory() as td:
            proc = run([line], td)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        p = out_props(proc)[0]
        self.assertEqual(json.loads(p["vehicle_flags"]), {"moto": 1})  # flag still set
        self.assertNotIn("seasons", p)
        self.assertEqual(len(rq), 1)
        self.assertEqual(rq[0]["field"], "motorcycle_managed")
        self.assertEqual(rq[0]["value"], "open when dry")
        self.assertEqual(rq[0]["examples"], ["C3"])


class AttrsSidecar(unittest.TestCase):
    def test_sidecar_contents(self):
        lines = [
            feature_line({"TRAIL_CN": "CN1", "TRAIL_SURFACE": "NAT", "TRAIL_CLASS": "3"}),
            feature_line({"TRAIL_CN": "CN2", "TRAIL_CLASS": "4"}),   # surface missing
            feature_line({"TRAIL_CN": "CN3"}),                        # nothing to contribute
            feature_line({"TRAIL_SURFACE": "GRAVEL"}),                # no CN -> excluded
        ]
        with tempfile.TemporaryDirectory() as td:
            attrs_path = os.path.join(td, "attrs.json")
            proc = run(lines, td, attrs_out=attrs_path)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with open(attrs_path, encoding="utf-8") as fh:
                attrs = json.load(fh)
        self.assertEqual(attrs, {
            "CN1": {"surface": "NAT", "trail_class": "3"},
            "CN2": {"trail_class": "4"},
        })

    def test_first_segment_wins_on_duplicate_cn(self):
        lines = [
            feature_line({"TRAIL_CN": "CN1", "TRAIL_SURFACE": "NAT"}),
            feature_line({"TRAIL_CN": "CN1", "TRAIL_SURFACE": "PAVED"}),
        ]
        with tempfile.TemporaryDirectory() as td:
            attrs_path = os.path.join(td, "attrs.json")
            run(lines, td, attrs_out=attrs_path)
            with open(attrs_path, encoding="utf-8") as fh:
                attrs = json.load(fh)
        self.assertEqual(attrs["CN1"]["surface"], "NAT")


class Tolerance(unittest.TestCase):
    def test_garbage_and_missing_cn(self):
        lines = ["%%%% not json", feature_line({"TRAIL_NO": "X"})]
        with tempfile.TemporaryDirectory() as td:
            proc = run(lines, td)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rq = read_jsonl(os.path.join(td, "rq.jsonl"))
        self.assertEqual(len(out_props(proc)), 1)
        self.assertEqual(rq[0]["field"], "trail_cn")


if __name__ == "__main__":
    unittest.main()
