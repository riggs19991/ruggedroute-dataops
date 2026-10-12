# Handoff T-0004 — parcels: restore the MN plan_parcels_open source URL and poll the ND hub export instead of failing on its first 400, then re-run the Q4 quarterly

## Where things stand
The two upstream breakages that failed the Q4 scheduled run 37349704081 (2026-10-05) are fixed in the working tree and committed on branch `ccr-7bd1d4c3-8ow8cs`: MN is a hub-mode unit on the gis.data.mn.gov ArcGIS Hub (FGDB export of layer 1 "Plan Parcels Open" of item 69148d3959194a05a23964cc60f6517b; the old GDRS bulk zip is gone), and `fetch_helpers.py`'s hub job poller now treats HTTP errors, network errors and non-JSON bodies as retryable until a 90-minute deadline, logging the response body each time (ND died on one HTTP 400 on its first poll). A `probe` CLI mode is the live source check. The Fable verifier graded DoD-1 to DoD-3 PASS with its own refutation runs (network-blocked pytest, end-to-end failure path through `fetch_parcels.sh`); DoD-4 is `check: external` and stays UNKNOWN until a human dispatches the full quarterly-parcels run and attests it, so the verdict on file is FAIL tagged `env-cannot-run`. The live parcels object is still parcels-20260811-1838 until that run publishes.

## Done, with evidence
- MN unit rewritten to the hub download/v1 FGDB export of layer 1 with the unchanged mapping (state_pin, co_name, acres_poly), no owner/tax field, count 2,710,201 — `pytest layers/parcels/tests/test_fetch_helpers.py -q -k sources` exit 0 (.forge/tasks/T-0004/checks/main-1791847167-unknown.json)
- Hub poller retries HTTP errors, network errors and non-JSON bodies (body logged) until the deadline and exits non-zero only after it; `hub()` and `probe()` covered by scripted fakes — `pytest layers/parcels/tests/test_fetch_helpers.py -q -k hub` exit 0 (.forge/tasks/T-0004/checks/main-1791847167-unknown.json)
- Both hub endpoints answer with a job envelope (MN Completed with resultUrl, ND ExportingData) — `python3 layers/parcels/fetch_helpers.py probe "https://gis.data.mn.gov/api/download/v1/items/69148d3959194a05a23964cc60f6517b/filegdb?redirect=false&layers=1" && python3 layers/parcels/fetch_helpers.py probe "https://gishubdata-ndgov.hub.arcgis.com/api/download/v1/items/ac6da1176038457db16e8debe3f1abaf/filegdb?redirect=false&layers=0"` exit 0 (.forge/tasks/T-0004/checks/main-1791847167-unknown.json)
- Whole parcels suite and lib suite green, ratchet 119 → 129 tests — `pytest layers/parcels/tests -q` exit 0 and `cd lib && python3 -m unittest -v` exit 0 (.forge/tasks/T-0004/checks/main-1791847167-unknown.json)

## Remaining
- DoD-4 (external): dispatch `quarterly-parcels.yml` with no `states` input (full 26-unit matrix, about 5 h), confirm `https://tiles.ruggedroutehq.com/parcels.json` reports a version newer than parcels-20260811-1838.pmtiles, then `.forge/bin/forge-status attest T-0004 main DoD-4 --by <name> --evidence <run url> --exit 0`, re-dispatch `forge-verifier fable/medium`, and close with `--human-ack`.

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
  "not_verified": ["DoD-4: full quarterly-parcels run and alias flip (external, human-gated)"],
  "failed_approaches": [],
  "next_action": "dispatch quarterly-parcels.yml (full matrix), attest DoD-4, re-dispatch forge-verifier fable/medium, close --human-ack",
  "commit": null
}
```
