#!/usr/bin/env python3
"""MVUM adapter regression tests.

The refactor onto route_common must keep the emitted schema BYTE-IDENTICAL for
existing attrs. Golden lineage:
- mvum_golden_{road,trail}_original.jsonl: captured from the Stage-0 standalone
  normalize_mvum.py over mvum_synthetic_{road,trail}_original.geojsonl — the
  frozen pre-change baseline (AdditiveMaintLevelTrailClass pins it).
- mvum_golden_{road,trail}.jsonl: regenerated after the intended ADDITIVE
  OPERATIONALMAINTLEVEL/TRAILCLASS passthrough change, over the extended
  synthetics; existing attrs are unchanged, only the new attrs were added.
Also covers the real-EDW season-field name variants and the optional
--nfs-attrs enrichment join."""
import json
import os
import tempfile
import unittest

from _test_helpers import FIXTURES, feature_line, out_props, run_normalizer


def read_lf(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read().replace("\r\n", "\n")


class GoldenByteIdentity(unittest.TestCase):
    def _check(self, kind):
        stdin_lines = read_lf(FIXTURES / f"mvum_synthetic_{kind}.geojsonl").splitlines()
        golden = read_lf(FIXTURES / f"mvum_golden_{kind}.jsonl")
        with tempfile.TemporaryDirectory() as td:
            proc = run_normalizer(
                "normalize_mvum.py",
                ["--kind", kind, "--review-out", os.path.join(td, "rq.jsonl")],
                stdin_lines)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, golden,
                         f"emitted {kind} schema drifted from the pre-refactor golden")

    def test_road_byte_identical(self):
        self._check("road")

    def test_trail_byte_identical(self):
        self._check("trail")

    def test_stderr_summary_format_kept(self):
        stdin_lines = read_lf(FIXTURES / "mvum_synthetic_road.geojsonl").splitlines()
        with tempfile.TemporaryDirectory() as td:
            proc = run_normalizer(
                "normalize_mvum.py",
                ["--kind", "road", "--review-out", os.path.join(td, "rq.jsonl")],
                stdin_lines)
        self.assertIn("normalize_mvum[road]: 4 in, 4 out, 3 review-queue entries",
                      proc.stderr)


class AdditiveMaintLevelTrailClass(unittest.TestCase):
    """INTENDED ADDITIVE schema change: the bulk GDB and live EDW spell the
    maintenance-level and trail-class columns OPERATIONALMAINTLEVEL and
    TRAILCLASS (verified 2026-08-03 against EDW_MVUM_01 layers 1/2), so the
    PASSTHROUGH now maps those spellings to maint_level/trail_class alongside
    the never-occurring underscored ones. The extended synthetic fixtures +
    regenerated goldens cover the new attrs; these tests pin the invariant that
    inputs WITHOUT the new fields still emit output byte-identical to the
    pre-change goldens (mvum_golden_{road,trail}_original.jsonl)."""

    def _check_original_unchanged(self, kind):
        stdin_lines = read_lf(FIXTURES / f"mvum_synthetic_{kind}_original.geojsonl").splitlines()
        golden = read_lf(FIXTURES / f"mvum_golden_{kind}_original.jsonl")
        with tempfile.TemporaryDirectory() as td:
            proc = run_normalizer(
                "normalize_mvum.py",
                ["--kind", kind, "--review-out", os.path.join(td, "rq.jsonl")],
                stdin_lines)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, golden,
                         f"{kind} input WITHOUT the new fields must stay byte-identical "
                         "to the pre-change golden (existing attrs may never move)")

    def test_road_without_new_fields_byte_identical_to_original_golden(self):
        self._check_original_unchanged("road")

    def test_trail_without_new_fields_byte_identical_to_original_golden(self):
        self._check_original_unchanged("trail")

    def _props(self, kind, raw):
        with tempfile.TemporaryDirectory() as td:
            proc = run_normalizer(
                "normalize_mvum.py",
                ["--kind", kind, "--review-out", os.path.join(td, "rq.jsonl")],
                [feature_line(raw)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return out_props(proc)[0]

    def test_real_edw_operationalmaintlevel_maps(self):
        p = self._props("road", {"RTE_CN": "M1",
                                 "OPERATIONALMAINTLEVEL": "2 - HIGH CLEARANCE VEHICLES"})
        self.assertEqual(p["maint_level"], "2 - HIGH CLEARANCE VEHICLES")

    def test_real_edw_trailclass_maps(self):
        p = self._props("trail", {"RTE_CN": "M2", "TRAILCLASS": "4"})
        self.assertEqual(p["trail_class"], "4")


class SeasonFieldVariants(unittest.TestCase):
    """The bulk EDW data drops 'inches' in gt50/lt50 season columns and uses
    _dur for e-bikes (fixtures/datesopen_corpus.json field_resolution). Those
    variants must feed seasons instead of being silently dropped."""

    def _seasons(self, props):
        with tempfile.TemporaryDirectory() as td:
            proc = run_normalizer(
                "normalize_mvum.py",
                ["--kind", "road", "--review-out", os.path.join(td, "rq.jsonl")],
                [feature_line(props)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = out_props(proc)[0]
        return json.loads(out.get("seasons", "[]"))

    def test_real_edw_gt50_name(self):
        seasons = self._seasons({"RTE_CN": "X1", "FOURWD_GT50INCHES": "Y",
                                 "FOURWD_GT50_DATESOPEN": "03/15-12/15"})
        self.assertEqual(seasons, [{"cls": "fourwd_gt50", "open": "03/15", "close": "12/15"}])

    def test_real_edw_ebike_dur_name(self):
        seasons = self._seasons({"RTE_CN": "X2", "E_BIKE_CLASS1": "Y",
                                 "E_BIKE_CLASS1_DUR": "yearlong"})
        self.assertEqual(seasons, [{"cls": "ebike1", "open": "01/01", "close": "12/31"}])

    def test_documented_name_still_wins(self):
        seasons = self._seasons({"RTE_CN": "X3", "FOURWD_GT50INCHES": "Y",
                                 "FOURWD_GT50INCHES_DATESOPEN": "05/01-10/31",
                                 "FOURWD_GT50_DATESOPEN": "01/01-12/31"})
        self.assertEqual(seasons, [{"cls": "fourwd_gt50", "open": "05/01", "close": "10/31"}])


class NfsEnrichmentJoin(unittest.TestCase):
    TRAILS = [
        feature_line({"RTE_CN": "CN1", "ID": "1", "NAME": "BARE"}),               # gets both
        feature_line({"RTE_CN": "CN2", "ID": "2", "SURFACETYPE": "PAVED"}),        # keeps own surface
        feature_line({"RTE_CN": "CN3", "ID": "3"}),                                # no sidecar hit
    ]
    SIDECAR = {"CN1": {"surface": "NAT - NATIVE MATERIAL", "trail_class": "3"},
               "CN2": {"surface": "GRAVEL", "trail_class": "4"}}

    def _run(self, extra_args):
        with tempfile.TemporaryDirectory() as td:
            args = ["--kind", "trail", "--review-out", os.path.join(td, "rq.jsonl")]
            if extra_args:
                sidecar = os.path.join(td, "attrs.json")
                with open(sidecar, "w", encoding="utf-8") as fh:
                    json.dump(self.SIDECAR, fh)
                args += ["--nfs-attrs", sidecar]
            proc = run_normalizer("normalize_mvum.py", args, self.TRAILS)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc

    def test_fills_missing_attrs_only(self):
        props = out_props(self._run(True))
        self.assertEqual(props[0]["surface"], "NAT - NATIVE MATERIAL")
        self.assertEqual(props[0]["trail_class"], "3")
        self.assertEqual(props[1]["surface"], "PAVED")       # own value NOT overwritten
        self.assertEqual(props[1]["trail_class"], "4")       # missing one filled
        self.assertNotIn("surface", props[2])

    def test_absent_flag_is_identical_to_today(self):
        plain = self._run(False)
        self.assertNotIn("NAT - NATIVE MATERIAL", plain.stdout)

    def test_missing_sidecar_file_warns_and_proceeds(self):
        with tempfile.TemporaryDirectory() as td:
            proc = run_normalizer(
                "normalize_mvum.py",
                ["--kind", "trail", "--review-out", os.path.join(td, "rq.jsonl"),
                 "--nfs-attrs", os.path.join(td, "nope.json")],
                self.TRAILS)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("::warning::", proc.stderr)
        self.assertEqual(len(out_props(proc)), 3)

    def test_roads_never_enriched(self):
        with tempfile.TemporaryDirectory() as td:
            sidecar = os.path.join(td, "attrs.json")
            with open(sidecar, "w", encoding="utf-8") as fh:
                json.dump(self.SIDECAR, fh)
            proc = run_normalizer(
                "normalize_mvum.py",
                ["--kind", "road", "--review-out", os.path.join(td, "rq.jsonl"),
                 "--nfs-attrs", sidecar],
                self.TRAILS)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("surface", out_props(proc)[0])


if __name__ == "__main__":
    unittest.main()
