#!/usr/bin/env python3
"""Shared helpers for the normalizer test suite (not collected by unittest
discovery — the filename does not match test*.py)."""
import json
import subprocess
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent
FIXTURES = LIB / "fixtures"
GEOM = {"type": "LineString", "coordinates": [[-111.7, 34.8], [-111.6, 34.9]]}


def feature_line(props, geometry=None):
    """One compact GeoJSONSeq Feature line."""
    return json.dumps({"type": "Feature", "properties": props,
                       "geometry": geometry or GEOM}, separators=(",", ":"))


def run_normalizer(script, args, stdin_lines):
    """Run a lib/ normalizer CLI exactly as CI does (stdin -> stdout).

    Returns the CompletedProcess; universal-newlines mode so output uses \\n
    on every platform. Never check=True — tests assert on returncode."""
    return subprocess.run(
        [sys.executable, str(LIB / script)] + list(args),
        input="\n".join(stdin_lines) + "\n",
        capture_output=True, text=True, cwd=str(LIB))


def out_props(proc):
    """Parse normalizer stdout back into a list of properties dicts."""
    out = []
    for line in proc.stdout.splitlines():
        if line.strip():
            out.append(json.loads(line)["properties"])
    return out


def read_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]
