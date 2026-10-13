#!/usr/bin/env python3
"""T-0006 DoD checks, run from the repository root.

Default: DoD-1 — every `git clone` of felt/tippecanoe in monthly-ownership.yml carries
`--branch 2.79.0` and there are exactly two of them (build job + merge-publish job).
--yaml:  DoD-3 — monthly-ownership.yml and quarterly-parcels.yml parse as YAML, keep their
test/build/merge-publish jobs, and monthly-ownership's two install steps are still present.
Exit 0 when the criterion holds, non-zero with a FAIL line otherwise.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
MONTHLY = ROOT / ".github/workflows/monthly-ownership.yml"
PARCELS = ROOT / ".github/workflows/quarterly-parcels.yml"
TAG = "2.79.0"


def pins() -> None:
    text = MONTHLY.read_text(encoding="utf-8")
    clones = re.findall(r"git clone[^\n]*felt/tippecanoe\.git[^\n]*", text)
    unpinned = [c.strip() for c in clones if f"--branch {TAG}" not in c]
    if len(clones) != 2 or unpinned:
        sys.exit(f"FAIL: expected 2 clones pinned to {TAG} in {MONTHLY.name}; found {len(clones)}, unpinned: {unpinned}")
    print(f"OK: {len(clones)} tippecanoe clones in {MONTHLY.name}, all --branch {TAG}")


def structure() -> None:
    import yaml  # PyYAML; installed on the runner images and in this session

    for path in (MONTHLY, PARCELS):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        jobs = doc.get("jobs") or {}
        missing = {"test", "build", "merge-publish"} - set(jobs)
        if missing:
            sys.exit(f"FAIL: {path.name} lacks jobs {sorted(missing)}; has {sorted(jobs)}")
        steps = sum(len(j.get("steps") or []) for j in jobs.values())
        print(f"OK: {path.name} parses; jobs {sorted(jobs)}; {steps} steps")
    text = MONTHLY.read_text(encoding="utf-8")
    for name in ("Install GDAL + tippecanoe + pmtiles", "Install pmtiles + tile-join"):
        if name not in text:
            sys.exit(f"FAIL: install step {name!r} missing from {MONTHLY.name}")
    print("OK: both install steps present in monthly-ownership.yml")


if __name__ == "__main__":
    structure() if "--yaml" in sys.argv[1:] else pins()
