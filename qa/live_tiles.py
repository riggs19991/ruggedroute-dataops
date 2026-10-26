#!/usr/bin/env python3
"""Live worker probe (T-0008): decode real tiles per layer from
tiles.ruggedroutehq.com, gate the parcels contract at the serving edge, and
diff each layer's served version against the last recorded baseline.

Usage:
    python qa/live_tiles.py                     # probe every layer, diff baseline
    python qa/live_tiles.py --layers parcels    # subset
    python qa/live_tiles.py --update-baseline   # accept the current state

Exit codes: 0 all gates pass; 1 a gate failed (parcels whitelist / use
vocabulary / bare-code county, or an empty mandatory probe); 2 usage/env.

The parcels gates mirror layers/parcels/qa_parcels.py — this probe is the
post-publish backstop proving what the WORKER serves, not what CI built.
Baseline (qa/live_tiles.baseline.json) stores each layer's TileJSON hash and
probe feature counts; a changed hash means the alias flipped to a new version
object since the last accepted run.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
import urllib.request
from pathlib import Path

try:
    import mapbox_vector_tile
except ImportError:  # pragma: no cover
    sys.exit("pip install mapbox-vector-tile (CI installs it in every workflow)")

BASE = "https://tiles.ruggedroutehq.com"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 rr-live-tiles-qa"}
BASELINE = Path(__file__).parent / "live_tiles.baseline.json"

PARCELS_WHITELIST = {"apn", "county", "acres", "st", "use"}
USE_BUCKETS = {"RES", "AG", "VAC", "COM", "IND", "FOREST", "GOV"}

# layer -> (source_layer_expected_any, [(name, lat, lon, z)], mandatory)
# Anchors are stable, feature-dense spots; `mandatory` layers must decode at
# least one non-empty probe or the run fails.
PROBES: dict = {
    "mvum":          (["mvum_roads", "mvum_trails"],
                      [("Moab", 38.5725, -109.5498, 10)], True),
    "lands":         (["land_fee", "land_overlay"],
                      [("Moab", 38.5725, -109.5498, 10)], True),
    "blm_routes":    (["blm_routes"], [("Moab", 38.5725, -109.5498, 10)], False),
    "nps_roads":     (["nps_roads"], [("Yellowstone", 44.4605, -110.8281, 10)], False),
    "roads_context": (["roads_context"], [("Moab", 38.5725, -109.5498, 10)], False),
    "roads_tnm":     (["roads_hwy", "roads_local", "roads_4wd", "trails_tnm"],
                      [("Moab", 38.5725, -109.5498, 12)], True),
    "parcels":       (["parcels"],
                      [("Moab UT", 38.5725, -109.5498, 14),
                       ("Orlando FL", 28.5384, -81.3789, 13),
                       ("Madison WI", 43.0731, -89.4012, 13),
                       ("Helena MT", 46.5891, -112.0391, 13)], True),
}


def fetch(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def tile_xy(lat: float, lon: float, z: int) -> tuple[int, int]:
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n)
    return x, y


def decode(raw: bytes) -> dict:
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return mapbox_vector_tile.decode(raw)


def gate_parcels(features: list, where: str) -> list[str]:
    """The serving-edge mirror of qa_parcels.py Gates 1/3 + T-0009 county rule."""
    failures: list[str] = []
    bad_keys: set = set()
    bad_use: set = set()
    bad_county: set = set()
    for f in features:
        props = f.get("properties") or {}
        bad_keys |= set(props) - PARCELS_WHITELIST
        u = props.get("use")
        if u is not None and u not in USE_BUCKETS:
            bad_use.add(str(u))
        c = props.get("county")
        if c is not None and not any(ch.isalpha() for ch in str(c)):
            bad_county.add(str(c))
    if bad_keys:
        failures.append(f"{where}: non-whitelisted keys {sorted(bad_keys)}")
    if bad_use:
        failures.append(f"{where}: use vocabulary violation {sorted(bad_use)[:5]}")
    if bad_county:
        failures.append(f"{where}: bare-code county values {sorted(bad_county)[:5]}")
    return failures


def probe_layer(layer: str) -> tuple[dict, list[str]]:
    expected_layers, anchors, mandatory = PROBES[layer]
    failures: list[str] = []
    info: dict = {"tiles": {}}
    try:
        tj_raw = fetch(f"{BASE}/{layer}.json")
        tj = json.loads(tj_raw)
        info["tilejson_hash"] = hashlib.sha256(tj_raw).hexdigest()[:16]
        info["vector_layers"] = sorted(v["id"] for v in tj.get("vector_layers", []))
    except Exception as e:
        failures.append(f"{layer}: TileJSON fetch failed: {e}")
        return info, failures if mandatory else (info, [])

    decoded_any = False
    for name, lat, lon, z in anchors:
        x, y = tile_xy(lat, lon, z)
        where = f"{layer} {name} {z}/{x}/{y}"
        try:
            t = decode(fetch(f"{BASE}/{layer}/{z}/{x}/{y}.mvt"))
        except Exception as e:
            failures.append(f"{where}: fetch/decode failed: {e}")
            continue
        found = [sl for sl in expected_layers if sl in t]
        count = sum(len(t[sl]["features"]) for sl in found)
        info["tiles"][f"{name} {z}/{x}/{y}"] = count
        if count:
            decoded_any = True
        if layer == "parcels" and "parcels" in t:
            failures += gate_parcels(t["parcels"]["features"], where)
    if mandatory and not decoded_any:
        failures.append(f"{layer}: every mandatory probe tile was empty")
    return info, failures


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--layers", help="comma list; default = all")
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()
    layers = [l.strip() for l in args.layers.split(",")] if args.layers else list(PROBES)
    unknown = [l for l in layers if l not in PROBES]
    if unknown:
        sys.exit(f"unknown layer(s): {unknown} (choices: {sorted(PROBES)})")

    baseline = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    all_failures: list[str] = []
    state: dict = dict(baseline)
    for layer in layers:
        info, failures = probe_layer(layer)
        all_failures += failures
        prev = baseline.get(layer, {})
        drift = ""
        if prev.get("tilejson_hash") and info.get("tilejson_hash"):
            drift = ("  [version CHANGED since baseline]"
                     if prev["tilejson_hash"] != info["tilejson_hash"]
                     else "  [version unchanged]")
        counts = ", ".join(f"{k}={v}" for k, v in info.get("tiles", {}).items()) or "-"
        print(f"{layer:14s} {counts}{drift}")
        state[layer] = info

    if args.update_baseline:
        BASELINE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")
        print(f"baseline written: {BASELINE.name}")

    if all_failures:
        print("\nGATE FAILURES:")
        for f in all_failures:
            print(f"  FAIL {f}")
        sys.exit(1)
    print("\nall live-tile gates PASS")


if __name__ == "__main__":
    main()
