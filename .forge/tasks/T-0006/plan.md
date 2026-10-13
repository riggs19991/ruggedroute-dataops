# Inline Plan: T-0006 — ci: pin tippecanoe 2.79.0 in monthly-ownership.yml like the other three workflows

```json
{
  "schema": "forge/plan/2",
  "task": "T-0006",
  "class": "X",
  "risk": "R",
  "chain": false,
  "routing": {
    "mode": "inline",
    "builder": null,
    "verifier": {
      "agent": "forge-verifier",
      "model": "fable",
      "effort": "medium"
    },
    "justification": "Two-line pin in a protected workflow file plus a one-line comment fix in another: too small for a builder, but .github/workflows/*.yml is a protected path, so the R overlay applies (class X inline, Fable verifier mandatory, rollback command, human acknowledgement at close)"
  },
  "steps": [],
  "dod": [
    {
      "id": "DoD-1",
      "criterion": "WHEN monthly-ownership.yml installs tippecanoe in its build and merge-publish jobs THE WORKFLOW SHALL clone the 2.79.0 tag (the version the other three workflows pin) and no unpinned clone of felt/tippecanoe SHALL remain",
      "check": "python3 .forge/tasks/T-0006/check_pins.py"
    },
    {
      "id": "DoD-2",
      "criterion": "WHEN quarterly-parcels.yml's header describes the tippecanoe pin THE COMMENT SHALL no longer call monthly-ownership's clone a known to-do",
      "check": "grep -q 'PINNED at 2.79.0' .github/workflows/quarterly-parcels.yml && ! grep -qi 'known to-do' .github/workflows/quarterly-parcels.yml"
    },
    {
      "id": "DoD-3",
      "criterion": "WHEN both workflow files are parsed as YAML THEY SHALL load without error with their test, build and merge-publish jobs intact and monthly-ownership's two install steps still present",
      "check": "python3 .forge/tasks/T-0006/check_pins.py --yaml"
    }
  ],
  "rollback": "git revert --no-edit <task commit>; nothing external is touched (the next monthly-ownership run is the scheduled one on the 3rd, or a manual dispatch; the pinned clone is the same command weekly-motorized, quarterly-parcels and quarterly-roads already run)",
  "test_baseline": {
    "files": 12,
    "tests": 129,
    "recorded_at": "2026-10-13T07:01:26Z"
  },
  "needs_clarification": [],
  "allowed_paths": [
    ".github/workflows/monthly-ownership.yml",
    ".github/workflows/quarterly-parcels.yml"
  ]
}
```

## Hypothesis / Objective
monthly-ownership.yml builds tippecanoe from an unpinned `git clone --depth 1` of felt/tippecanoe in both its jobs (lines 79 and 115), so a lands build can silently pick up whatever tippecanoe's default branch holds that day, while weekly-motorized, quarterly-parcels and quarterly-roads pin tag 2.79.0 (quarterly-parcels.yml:12-13 calls the unpinned clone "a known to-do"). Objective: add `--branch 2.79.0` to both clone lines, the same tag the other workflows build and cache, and retire the "known to-do" wording in the parcels header. No cache idiom is adopted here: the pin is the correctness fix; the cache is a build-minute optimisation and would widen the diff in a protected file.

## Validation Criteria
- DoD-1: both tippecanoe clones in monthly-ownership.yml carry `--branch 2.79.0` and no unpinned clone remains — check: `python3 .forge/tasks/T-0006/check_pins.py`
- DoD-2: the parcels header no longer calls the monthly clone a known to-do — check: `grep -q 'PINNED at 2.79.0' .github/workflows/quarterly-parcels.yml && ! grep -qi 'known to-do' .github/workflows/quarterly-parcels.yml`
- DoD-3: both files parse as YAML with their jobs and install steps intact — check: `python3 .forge/tasks/T-0006/check_pins.py --yaml`

## Rollback
`git revert --no-edit <task commit>`. Nothing external changes until the next monthly-ownership run (scheduled the 3rd of each month, or a manual dispatch), and the pinned tag is the one already building weekly in the other three workflows (cache key tippecanoe-2.79.0), so the pin cannot introduce a version the pipeline has not run.
