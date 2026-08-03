#!/usr/bin/env python3
"""Tests for the shared normalizer plumbing (route_common)."""
import io
import json
import os
import tempfile
import unittest

from route_common import ReviewQueue, apply_passthrough, iter_features, parse_seasons, truthy


class ReviewQueueDedup(unittest.TestCase):
    def _write_and_read(self, fill):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "rq.jsonl")
            with ReviewQueue(path) as rq:
                fill(rq)
                occurrences = rq.occurrences
            with open(path, encoding="utf-8") as fh:
                entries = [json.loads(line) for line in fh if line.strip()]
            return entries, occurrences

    def test_flood_dedupes_to_one_entry(self):
        # GTLF free text repeats on thousands of features — must be ONE line.
        def fill(rq):
            for i in range(1000):
                rq.add("ohv_dsgntn_lim_explain", "Limited to designated routes.",
                       example=f"id-{i}")
        entries, occurrences = self._write_and_read(fill)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["count"], 1000)
        self.assertEqual(occurrences, 1000)
        self.assertEqual(len(entries[0]["examples"]), ReviewQueue.MAX_EXAMPLES)
        self.assertEqual(entries[0]["examples"], ["id-0", "id-1", "id-2"])

    def test_distinct_values_stay_distinct(self):
        def fill(rq):
            rq.add("f", "a"), rq.add("f", "b"), rq.add("g", "a")
        entries, occurrences = self._write_and_read(fill)
        self.assertEqual(len(entries), 3)
        self.assertEqual(occurrences, 3)

    def test_duplicate_examples_not_repeated(self):
        def fill(rq):
            for _ in range(5):
                rq.add("f", "v", example="same-id")
        entries, _ = self._write_and_read(fill)
        self.assertEqual(entries[0]["examples"], ["same-id"])

    def test_empty_queue_writes_empty_file(self):
        entries, occurrences = self._write_and_read(lambda rq: None)
        self.assertEqual(entries, [])
        self.assertEqual(occurrences, 0)

    def test_none_value_is_keyed(self):
        def fill(rq):
            rq.add("f", None), rq.add("f", None)
        entries, _ = self._write_and_read(fill)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["count"], 2)


class IterFeatures(unittest.TestCase):
    def test_tolerates_garbage(self):
        stream = io.StringIO("\n".join([
            '{"type":"Feature","properties":{"A":1},"geometry":null}',
            "not json at all",
            "[",
            "]",
            "",
            '{"type":"FeatureCollection","features":[]}',
            '42',
            '{"type":"Feature","properties":{},"geometry":null},',  # trailing comma
        ]))
        feats = list(iter_features(stream))
        self.assertEqual(len(feats), 2)
        self.assertEqual(feats[0]["properties"], {"A": 1})


class ApplyPassthrough(unittest.TestCase):
    def test_skips_empty(self):
        props = {}
        apply_passthrough(props, {"a": "x", "b": "", "c": None, "d": 0},
                          {"a": "A", "b": "B", "c": "C", "d": "D"})
        self.assertEqual(props, {"A": "x", "D": 0})


class SharedParsers(unittest.TestCase):
    def test_parse_seasons_reexported_semantics(self):
        s, ok = parse_seasons("03/15-12/15")
        self.assertTrue(ok)
        self.assertEqual(s, [{"open": "03/15", "close": "12/15"}])

    def test_truthy(self):
        self.assertTrue(truthy("Y"))
        self.assertFalse(truthy("no"))


if __name__ == "__main__":
    unittest.main()
