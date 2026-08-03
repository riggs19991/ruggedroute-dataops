#!/usr/bin/env python3
"""Stable-key stability check (the orphan check): given the previous run's
source_id list and this run's normalized geojsonl, report how many ids
disappeared (present in run A, missing in run B) and how many are new.

Without --max-orphan-pct this is a SOFT gate: churn is expected on some
sources (GTLF OBJECTIDs are per-layer and unstable across BLM republishes),
so the exit code stays 0 and the workflow surfaces a ::warning:: instead of
failing. --max-orphan-pct makes it a hard gate; the workflow passes 5 for the
stable-key layers (mvum, roads_context, nfs_trails, nps_roads) and leaves
blm_routes soft. A baseline run (no --previous file) always exits 0 — the
check only becomes meaningful on the second run (2-build criterion).

Wiring: each layer job downloads the previous successful run's id-list
ARTIFACT (rtecn-ids-<layer>, retention 35 days, via the gh CLI), runs this
script, then uploads the fresh --ids-out list as the same-named artifact for
the next run. actions/cache is deliberately NOT used: its 7-day eviction sits
exactly on the weekly cron boundary, so the baseline never survived to the
next run and the gate never armed.

Usage:
  python3 qa/rte_cn_stability.py --layer mvum \
      --current mvum_roads.geojsonl mvum_trails.geojsonl \
      --previous prev_ids.txt --ids-out ids.txt
"""
import argparse
import json
import os
import sys


def collect_ids(paths):
    ids = set()
    total = 0
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    f = json.loads(line)
                except json.JSONDecodeError:
                    continue
                total += 1
                sid = (f.get("properties") or {}).get("source_id")
                if sid not in (None, ""):
                    ids.add(str(sid))
    return ids, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", required=True, help="label for log output")
    ap.add_argument("--current", nargs="+", required=True,
                    help="this run's normalized geojsonl file(s)")
    ap.add_argument("--previous", default=None,
                    help="previous run's id list (one id per line); missing file is fine")
    ap.add_argument("--ids-out", default=None,
                    help="write this run's sorted id list here (for the next run)")
    ap.add_argument("--max-orphan-pct", type=float, default=None,
                    help="hard-fail when orphaned/previous exceeds this percentage")
    args = ap.parse_args()

    current, total = collect_ids(args.current)
    print(f"rte_cn_stability[{args.layer}]: {total} features, {len(current)} distinct source_ids")

    if args.ids_out:
        with open(args.ids_out, "w", encoding="utf-8") as fh:
            for sid in sorted(current):
                fh.write(sid + "\n")

    if not args.previous or not os.path.exists(args.previous):
        print(f"::notice::rte_cn_stability[{args.layer}]: no previous id list — "
              "baseline run, nothing to compare (2-build criterion)")
        return 0

    with open(args.previous, encoding="utf-8") as fh:
        previous = {line.strip() for line in fh if line.strip()}
    orphans = previous - current
    added = current - previous
    pct = 100.0 * len(orphans) / max(len(previous), 1)
    print(f"rte_cn_stability[{args.layer}]: previous={len(previous)} current={len(current)} "
          f"orphaned={len(orphans)} ({pct:.2f}%) new={len(added)}")
    if orphans:
        sample = ", ".join(sorted(orphans)[:5])
        print(f"::warning::rte_cn_stability[{args.layer}]: {len(orphans)} source_ids from the "
              f"previous run are missing in this run ({pct:.2f}%) — e.g. {sample}")
    if args.max_orphan_pct is not None and pct > args.max_orphan_pct:
        print(f"::error::rte_cn_stability[{args.layer}]: orphan rate {pct:.2f}% exceeds "
              f"--max-orphan-pct {args.max_orphan_pct}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
