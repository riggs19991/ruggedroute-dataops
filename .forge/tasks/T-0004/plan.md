# Inline Plan: T-0004 — parcels: restore the MN plan_parcels_open source URL and poll the ND hub export instead of failing on its first 400, then re-run the Q4 quarterly

```json
{
  "schema": "forge/plan/2",
  "task": "T-0004",
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
    "justification": "X: root cause of the failed Q4 scheduled run 37349704081, coded by the architect inline; the Fable verifier is mandatory; the R overlay applies because layers/parcels/** is a risk path, so the plan carries a rollback command and close needs a human acknowledgement"
  },
  "steps": [],
  "dod": [
    {
      "id": "DoD-1",
      "criterion": "WHEN the hub download/v1 job endpoint answers an HTTP error, a non-JSON body, a network error or a Pending/ExportingData status THE SYSTEM SHALL log the response and keep polling with a fixed interval until the job reports a resultUrl or the deadline passes, and exit non-zero only after the deadline",
      "check": "pytest layers/parcels/tests/test_fetch_helpers.py -q -k hub"
    },
    {
      "id": "DoD-2",
      "criterion": "WHEN sources.json is loaded THE MN unit SHALL be a hub-mode entry for layer 1 of hub item 69148d3959194a05a23964cc60f6517b on gis.data.mn.gov whose field mapping names only fields the live layer published on 2026-10-12 (state_pin, co_name, acres_poly) and none of the owner_* or tax_* columns",
      "check": "pytest layers/parcels/tests/test_fetch_helpers.py -q -k sources"
    },
    {
      "id": "DoD-3",
      "criterion": "WHEN the MN and ND hub download endpoints named in sources.json are probed THE SYSTEM SHALL receive a job envelope (a status or a resultUrl) from each",
      "check": "python3 layers/parcels/fetch_helpers.py probe \"https://gis.data.mn.gov/api/download/v1/items/69148d3959194a05a23964cc60f6517b/filegdb?redirect=false&layers=1\" && python3 layers/parcels/fetch_helpers.py probe \"https://gishubdata-ndgov.hub.arcgis.com/api/download/v1/items/ac6da1176038457db16e8debe3f1abaf/filegdb?redirect=false&layers=0\""
    },
    {
      "id": "DoD-4",
      "criterion": "WHEN the quarterly-parcels workflow is dispatched for the full matrix THE RUN SHALL succeed through merge-publish and the live TileJSON SHALL report a parcels object newer than parcels-20260811-1838",
      "check": "external",
      "external": {
        "what": "GitHub Actions run of quarterly-parcels.yml with no states input (full 26-unit matrix) succeeds, and https://tiles.ruggedroutehq.com/parcels.json reports a version newer than parcels-20260811-1838.pmtiles",
        "how": "gh workflow run quarterly-parcels.yml && gh run watch; then curl -s https://tiles.ruggedroutehq.com/parcels.json | jq -r .version"
      }
    }
  ],
  "rollback": "git revert --no-edit <task commit on this branch>; if the re-run published a bad tileset: npx wrangler kv key put --namespace-id f2f28315ee8f43fb8413d1bcddd20684 --remote layer-alias:parcels parcels-20260811-1838.pmtiles (the previous object is never overwritten, so the flip restores the Q3 tileset at once)",
  "test_baseline": {
    "files": 11,
    "tests": 119,
    "recorded_at": "2026-10-12T23:06:57Z"
  },
  "needs_clarification": [],
  "allowed_paths": [
    "layers/parcels/sources.json",
    "layers/parcels/fetch_helpers.py",
    "layers/parcels/tests/test_fetch_helpers.py"
  ]
}
```

## Hypothesis / Objective
The Q4 scheduled run 37349704081 (2026-10-05) lost two of 28 jobs, so merge-publish never ran and the live object is still parcels-20260811-1838. Both failures are upstream changes, not code regressions:
- MN (http mode): `resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_mngeo/plan_parcels_open/fgdb_plan_parcels_open.zip` answers 404 and the whole GDRS tree is gone; gisdata.mn.gov now redirects to the ArcGIS Hub site gis.data.mn.gov. The dataset is hub item `69148d3959194a05a23964cc60f6517b` (FeatureServer `us_mn_state_mngeo/plan_parcels_open`, layer 1 "Plan Parcels Open", 2,710,201 features on 2026-10-12, fields still `state_pin`, `co_name`, `acres_poly`; owner_* and tax_* columns present and stripped by the mapping + whitelist gate). The Hub download/v1 API serves an FGDB export, so MN becomes a hub-mode unit like VT and ME.
- ND (hub mode): the first poll of the job endpoint answered HTTP 400 and `fetch_helpers.hub()` raised immediately. Today the same endpoint answers 200 with status Pending/ExportingData, so the 400 was a transient hub state while the export was being regenerated. The poller must treat HTTP errors, non-JSON bodies and network errors as retryable until its deadline, and log the body so the next failure is diagnosable.
Hypothesis test: unit tests with an injected fetch function for the poller, plus a live `probe` mode run against both endpoints (DoD-3). The full re-run is a human-gated workflow dispatch (DoD-4, external).

## Validation Criteria
- DoD-1: the hub poller survives transient HTTP/network/JSON failures until its deadline — check: `pytest layers/parcels/tests/test_fetch_helpers.py -q -k hub`
- DoD-2: MN is a hub-mode entry for layer 1 of the new item with a mapping limited to live, non-owner fields — check: `pytest layers/parcels/tests/test_fetch_helpers.py -q -k sources`
- DoD-3: both hub endpoints answer with a job envelope — check: `python3 layers/parcels/fetch_helpers.py probe "<MN url>" && python3 layers/parcels/fetch_helpers.py probe "<ND url>"` (exact commands in the JSON block)
- DoD-4: the full quarterly re-run succeeds and the live parcels version advances — check: external (human attest after `gh workflow run quarterly-parcels.yml`)

## Rollback
`git revert --no-edit <task commit>` restores the previous sources.json and poller (MN then fails again on the dead URL, which is the pre-task state). If the re-run publishes a bad tileset, the alias flip is the rollback: `npx wrangler kv key put --namespace-id f2f28315ee8f43fb8413d1bcddd20684 --remote layer-alias:parcels parcels-20260811-1838.pmtiles`; versioned objects are never overwritten, so the Q3 tileset is intact.
