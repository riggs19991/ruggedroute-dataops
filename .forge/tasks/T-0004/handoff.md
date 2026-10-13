# Handoff T-0004 — parcels: restore the MN plan_parcels_open source URL and poll the ND hub export instead of failing on its first 400, then re-run the Q4 quarterly

## Where things stand
The two upstream breakages that failed the Q4 scheduled run 37349704081 (2026-10-05) are fixed and on `main` (fast-forwarded from branch `ccr-7bd1d4c3-8ow8cs`): MN is a hub-mode unit on the gis.data.mn.gov ArcGIS Hub (FGDB export of layer 1 "Plan Parcels Open" of item 69148d3959194a05a23964cc60f6517b; the old GDRS bulk zip is gone), and `fetch_helpers.py`'s hub job poller now treats HTTP errors, network errors and non-JSON bodies as retryable until a 90-minute deadline, logging the response body each time (ND died on one HTTP 400 on its first poll). A `probe` CLI mode is the live source check. The Fable verifier graded DoD-1 to DoD-3 PASS with its own refutation runs (network-blocked pytest, end-to-end failure path through `fetch_parcels.sh`). DoD-4, the human-gated full re-run, was dispatched on 2026-10-13 00:43Z after the founder's "Go" (run 38328659747): all 26 units built green (MN in 13 min on the hub export, ND in 5 min, OH the long pole at 5 h 28 min), merge-publish uploaded parcels-20261013-0632.pmtiles and flipped `layer-alias:parcels` at 06:32Z, and https://tiles.ruggedroutehq.com/parcels.json reports that version with exactly the whitelisted fields (acres, apn, county, st). The attest record for DoD-4 cites that run.

## Done, with evidence
- MN unit rewritten to the hub download/v1 FGDB export of layer 1 with the unchanged mapping (state_pin, co_name, acres_poly), no owner/tax field, count 2,710,201 — `pytest layers/parcels/tests/test_fetch_helpers.py -q -k sources` exit 0 (.forge/tasks/T-0004/checks/main-1791847167-unknown.json)
- Hub poller retries HTTP errors, network errors and non-JSON bodies (body logged) until the deadline and exits non-zero only after it; `hub()` and `probe()` covered by scripted fakes — `pytest layers/parcels/tests/test_fetch_helpers.py -q -k hub` exit 0 (.forge/tasks/T-0004/checks/main-1791847167-unknown.json)
- Both hub endpoints answer with a job envelope (MN Completed with resultUrl, ND ExportingData) — `python3 layers/parcels/fetch_helpers.py probe "https://gis.data.mn.gov/api/download/v1/items/69148d3959194a05a23964cc60f6517b/filegdb?redirect=false&layers=1" && python3 layers/parcels/fetch_helpers.py probe "https://gishubdata-ndgov.hub.arcgis.com/api/download/v1/items/ac6da1176038457db16e8debe3f1abaf/filegdb?redirect=false&layers=0"` exit 0 (.forge/tasks/T-0004/checks/main-1791847167-unknown.json)
- Whole parcels suite and lib suite green, ratchet 119 → 129 tests — `pytest layers/parcels/tests -q` exit 0 and `cd lib && python3 -m unittest -v` exit 0 (.forge/tasks/T-0004/checks/main-1791847167-unknown.json)

- DoD-4 (external, attested): run https://github.com/riggs19991/ruggedroute-dataops/actions/runs/38328659747 succeeded through merge-publish and `curl -s https://tiles.ruggedroutehq.com/parcels.json | jq -r .version` prints parcels-20261013-0632.pmtiles (newer than parcels-20260811-1838) — attest record under .forge/tasks/T-0004/checks/

## Remaining
none

## Gotchas / do not touch
- The hub names an exported feature class after the service's internal table (the layer-0 export's class is `o5_plan_parcels_open_2`), never after the display name: do not add a `layer` hint to MN.
- The Forge hooks stopped firing in this session after the shell moved outside the repository (evidence rows 0, verdict recorded by hand with `forge-status step-verdict`); start a fresh session in the repo before relying on the gates again.
- `fetch_parcels.sh`'s header still lists hub mode as "(VT, ME)"; it is outside this task's scope.

```json
{
  "schema": "forge/handoff/2",
  "task": "T-0004",
  "step": "task",
  "status": "DONE",
  "files_changed": ["layers/parcels/sources.json", "layers/parcels/fetch_helpers.py", "layers/parcels/tests/test_fetch_helpers.py"],
  "checks_run": [
    { "cmd": "pytest layers/parcels/tests/test_fetch_helpers.py -q -k hub", "exit": 0 },
    { "cmd": "pytest layers/parcels/tests/test_fetch_helpers.py -q -k sources", "exit": 0 },
    { "cmd": "python3 layers/parcels/fetch_helpers.py probe \"https://gis.data.mn.gov/api/download/v1/items/69148d3959194a05a23964cc60f6517b/filegdb?redirect=false&layers=1\" && python3 layers/parcels/fetch_helpers.py probe \"https://gishubdata-ndgov.hub.arcgis.com/api/download/v1/items/ac6da1176038457db16e8debe3f1abaf/filegdb?redirect=false&layers=0\"", "exit": 0 },
    { "cmd": "pytest layers/parcels/tests -q", "exit": 0 },
    { "cmd": "cd lib && python3 -m unittest -v", "exit": 0 }
  ],
  "not_verified": [],
  "failed_approaches": [],
  "next_action": "none",
  "commit": null
}
```
