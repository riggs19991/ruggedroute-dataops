#!/usr/bin/env python3
"""Shared plumbing for every Stage-1 route normalizer (master plan §3, §11).

All five federal sources (USFS MVUM, USFS RoadCore, USFS NFS Trails, BLM GTLF,
NPS Public Roads) flow through the helpers here so season parsing, tolerant
GeoJSONSeq streaming, and review-queue behavior stay identical across layers.

Design rules (do not violate):
- Normalizers NEVER crash on bad upstream data. Unparsable values are preserved
  raw and logged to the review queue.
- The review queue is DEDUPED by (field, value): GTLF free-text limitation
  strings repeat thousands of times and would otherwise flood the artifact.
- parse_seasons/truthy are byte-for-byte the Stage-0 MVUM implementations; the
  live mvum tileset and the Android client depend on their exact behavior.
"""
import json
import re
import sys

DATE_RANGE = re.compile(r"(\d{1,2})\s*/\s*(\d{1,2})\s*(?:-|–|to|thru|through)\s*(\d{1,2})\s*/\s*(\d{1,2})", re.I)
YEARLONG = re.compile(r"year\s*-?\s*long|yearround|year\s*round|all\s*year|01/01\s*-\s*12/31", re.I)


def parse_seasons(text):
    """Return (seasons_list, ok). seasons_list = [{open,close}] mm/dd zero-padded.
    ok=False means text was non-empty but nothing parseable was found."""
    if not text or not str(text).strip():
        return [], True
    s = str(text).strip()
    if YEARLONG.search(s):
        return [{"open": "01/01", "close": "12/31"}], True
    out = []
    for m in DATE_RANGE.finditer(s):
        mo1, d1, mo2, d2 = (int(g) for g in m.groups())
        if 1 <= mo1 <= 12 and 1 <= d1 <= 31 and 1 <= mo2 <= 12 and 1 <= d2 <= 31:
            out.append({"open": f"{mo1:02d}/{d1:02d}", "close": f"{mo2:02d}/{d2:02d}"})
    return out, bool(out)


def truthy(v):
    """A vehicle class is allowed if its column is non-empty and not an explicit no."""
    if v is None:
        return False
    s = str(v).strip().lower()
    return s not in ("", "n", "no", "null", "none", "0")


def iter_features(stream):
    """Yield Feature dicts from a GeoJSONSeq stream, tolerantly.

    Skips blank lines, stray brackets/commas (some tools emit a JSON array),
    unparsable lines, and any object that is not a Feature. Never raises on
    bad input — bad lines are simply dropped."""
    for line in stream:
        line = line.strip().rstrip(",")
        if not line or line in ("[", "]"):
            continue
        try:
            f = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(f, dict) or f.get("type") != "Feature":
            continue
        yield f


def lower_props(feature):
    """Lower-cased copy of a feature's properties (GDB/ArcGIS field case varies)."""
    return {str(k).lower(): v for k, v in (feature.get("properties") or {}).items()}


def apply_passthrough(props, raw, mapping):
    """Copy raw[src] -> props[dst] for every non-empty source column, in mapping order."""
    for src, dst in mapping.items():
        if raw.get(src) not in (None, ""):
            props[dst] = raw[src]


def write_feature(feature, props, out=None):
    """Replace the feature's properties and emit one compact GeoJSONSeq line."""
    feature["properties"] = props
    (out or sys.stdout).write(json.dumps(feature, separators=(",", ":")) + "\n")


class ReviewQueue:
    """Deduped review-queue writer (JSONL).

    Entries are keyed by (field, value); each carries a running `count` and up
    to MAX_EXAMPLES example source_ids so a single weird upstream string that
    appears on 40k features produces ONE line, not 40k. `occurrences` preserves
    the Stage-0 stderr-summary semantics (total add() calls, not unique lines).

    Use as a context manager; the file (possibly empty) is always written."""

    MAX_EXAMPLES = 3

    def __init__(self, path):
        self.path = path
        self.occurrences = 0
        self._entries = {}

    def add(self, field, value, example=None):
        self.occurrences += 1
        key = (str(field), "" if value is None else str(value))
        e = self._entries.setdefault(key, {"field": field, "value": value,
                                           "count": 0, "examples": []})
        e["count"] += 1
        if example is not None and example not in e["examples"] \
                and len(e["examples"]) < self.MAX_EXAMPLES:
            e["examples"].append(example)

    def write(self):
        with open(self.path, "w", encoding="utf-8") as fh:
            for key in sorted(self._entries):
                fh.write(json.dumps(self._entries[key], default=str) + "\n")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.write()
        return False
