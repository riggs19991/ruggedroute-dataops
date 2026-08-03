#!/usr/bin/env python3
"""Corpus sweep: every real-world datesopen string harvested from live EDW
(fixtures/datesopen_corpus.json, 982 distinct values) must run through
parse_seasons with ZERO exceptions and reproduce the classified result, and
every parse_ok:false value must land in the review queue when run through the
actual MVUM normalizer CLI path (master plan §11 Stage 1 verification)."""
import json
import os
import tempfile
import unittest

from _test_helpers import FIXTURES, feature_line, run_normalizer, read_jsonl
from route_common import parse_seasons


def load_corpus():
    with open(FIXTURES / "datesopen_corpus.json", encoding="utf-8") as fh:
        return json.load(fh)


class CorpusSweep(unittest.TestCase):
    def test_no_crash_and_classification_matches_on_all_982(self):
        corpus = load_corpus()
        self.assertGreaterEqual(len(corpus["values"]), 900)
        for entry in corpus["values"]:
            value = entry["value"]
            try:
                windows, ok = parse_seasons(value)
            except Exception as e:  # pragma: no cover - the whole point
                self.fail(f"parse_seasons raised {type(e).__name__} on {value!r}: {e}")
            self.assertEqual(ok, entry["parse_ok"], f"parse_ok drifted for {value!r}")
            self.assertEqual(windows, entry["windows"], f"windows drifted for {value!r}")

    def test_all_failures_land_in_review_queue_via_mvum_cli(self):
        corpus = load_corpus()
        failures = [e["value"] for e in corpus["values"] if not e["parse_ok"]]
        self.assertTrue(failures, "corpus should contain known-bad values")
        lines = [
            feature_line({"RTE_CN": f"CORPUS{i}", "ID": str(i), "ATV": "Y",
                          "ATV_DATESOPEN": value})
            for i, value in enumerate(failures)
        ]
        with tempfile.TemporaryDirectory() as td:
            rq_path = os.path.join(td, "rq.jsonl")
            proc = run_normalizer("normalize_mvum.py",
                                  ["--kind", "trail", "--review-out", rq_path], lines)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            entries = read_jsonl(rq_path)
        queued = {e["value"] for e in entries if e["field"] == "atv_datesopen"}
        self.assertEqual(queued, set(failures))


if __name__ == "__main__":
    unittest.main()
