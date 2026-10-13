# Handoff T-0006 — ci: pin tippecanoe 2.79.0 in monthly-ownership.yml like the other three workflows

## Where things stand
monthly-ownership.yml now clones felt/tippecanoe at tag 2.79.0 in both of its jobs (build matrix and merge-publish), the same tag weekly-motorized, quarterly-parcels and quarterly-roads build and cache (cache key tippecanoe-2.79.0, restored on every parcels job of run 38328659747), so a lands build can no longer pick up whatever tippecanoe's default branch holds on the 3rd of the month. The parcels header comment that called the unpinned clone "a known to-do" now says monthly-ownership pins the same tag with a plain clone. No cache idiom was added: the pin is the correctness fix and the cache would widen a protected-file diff. Nothing external changes until the next monthly-ownership run (scheduled 2026-11-03, or a manual dispatch).

## Done, with evidence
- Both tippecanoe clones in monthly-ownership.yml carry `--branch 2.79.0` and no unpinned clone remains — `python3 .forge/tasks/T-0006/check_pins.py` exit 0 (.forge/tasks/T-0006/checks/main-1791874911-unknown.json)
- The parcels header no longer calls the monthly clone a known to-do — `grep -q 'PINNED at 2.79.0' .github/workflows/quarterly-parcels.yml && ! grep -qi 'known to-do' .github/workflows/quarterly-parcels.yml` exit 0 (.forge/tasks/T-0006/checks/main-1791874911-unknown.json)
- Both workflow files parse as YAML with their test, build and merge-publish jobs and the two install steps intact — `python3 .forge/tasks/T-0006/check_pins.py --yaml` exit 0 (.forge/tasks/T-0006/checks/main-1791874911-unknown.json)
- lib suite unaffected — `cd lib && python3 -m unittest -v` exit 0 (.forge/tasks/T-0006/checks/main-1791874911-unknown.json)

## Remaining
none

## Gotchas / do not touch
- The pinned tag must stay equal across the four workflows: weekly-motorized and the two quarterlies pin via the cache idiom (`--branch 2.79.0` + cache key `tippecanoe-2.79.0`); bump all four together.
- The first monthly-ownership run on this pin is the scheduled 2026-11-03 run; it builds tippecanoe from source in every matrix job, as before (no cache), so expect the same runtime.

```json
{
  "schema": "forge/handoff/2",
  "task": "T-0006",
  "step": "task",
  "status": "DONE",
  "files_changed": [".github/workflows/monthly-ownership.yml", ".github/workflows/quarterly-parcels.yml"],
  "checks_run": [
    { "cmd": "python3 .forge/tasks/T-0006/check_pins.py", "exit": 0 },
    { "cmd": "grep -q 'PINNED at 2.79.0' .github/workflows/quarterly-parcels.yml && ! grep -qi 'known to-do' .github/workflows/quarterly-parcels.yml", "exit": 0 },
    { "cmd": "python3 .forge/tasks/T-0006/check_pins.py --yaml", "exit": 0 },
    { "cmd": "cd lib && python3 -m unittest -v", "exit": 0 }
  ],
  "not_verified": [],
  "failed_approaches": [],
  "next_action": "none",
  "commit": null
}
```
