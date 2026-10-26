# Execution Plan: T-0012 — parcels land-use classification (`use` bucket)

```json
{
  "schema": "forge/plan/2",
  "task": "T-0012",
  "class": "M",
  "risk": "none",
  "chain": false,
  "routing": {
    "mode": "single",
    "builder": {
      "agent": "forge-builder",
      "model": "opus",
      "effort": "medium"
    },
    "verifier": {
      "agent": "forge-verifier",
      "model": "fable",
      "effort": "medium"
    },
    "justification": "small M (6 files, 1 dir) planned by the architect: every adapter is fully specified from this session's live value harvests, so one Opus builder implements mechanically; Fable verifier because the change extends the licensing-critical whitelist"
  },
  "steps": [
    {
      "id": "01",
      "title": "use adapters + whitelist + qa vocab gate + contract",
      "brief": "brief-01.md",
      "agent": "forge-builder",
      "model": "opus",
      "effort": "medium",
      "mechanical": false,
      "red_ok_until": null,
      "max_tool_calls": 120
    }
  ],
  "dod": [
    {
      "id": "DoD-1",
      "criterion": "WHEN the use adapters run on the harvested value tables THE SYSTEM SHALL bucket them exactly as brief-01 specifies (FL DOR_UC ranges incl 000->VAC and 054-058->FOREST; MA stripped-zero first digit; IN DLGF first digit; NJ PROP_CLASS map; DC CLASSTYPE map; WI first comma token; MT keyword table) and yield None for every unknown",
      "check": "pytest layers/parcels/tests/test_use_adapters.py -q"
    },
    {
      "id": "DoD-2",
      "criterion": "WHEN normalize runs THE SYSTEM SHALL emit use only from the unit's configured use_field/use_adapter, include 'use' in both WHITELIST tuples and in the null-rate stats, and fetch_parcels.sh rest mode SHALL request the use_field so MA's esridump actually fetches USE_CODE",
      "check": "pytest layers/parcels/tests -q && grep -q '\"use\"' layers/parcels/normalize_parcels.py && grep -q '\"use\"' layers/parcels/qa_parcels.py && grep -q 'use_field' layers/parcels/fetch_parcels.sh"
    },
    {
      "id": "DoD-3",
      "criterion": "WHEN qa_parcels gates a build THE SYSTEM SHALL fail it if any feature (geojsonl or decoded tile) carries a use value outside {RES,AG,VAC,COM,IND,FOREST,GOV}, and layer.json SHALL document the bucket vocabulary, the 7 covered states and the client-lockstep rule",
      "check": "pytest layers/parcels/tests/test_use_adapters.py -q && python -c \"import json; d=json.load(open('layers/parcels/layer.json')); s=json.dumps(d); assert 'FOREST' in s and 'use' in d['schema']['parcels']\""
    },
    {
      "id": "DoD-4",
      "criterion": "WHEN the 7-unit validation dispatch runs (FL_1 FL_2 MA IN NJ DC WI MT) THE SYSTEM SHALL pass every gate with use present at a plausible rate (null-rate printed per unit) and vocab-valid in decoded tiles",
      "check": "external",
      "external": {
        "what": "a green quarterly-parcels dispatch of the 7 use units with the new vocab gate active; per-unit use null-rates in the logs; spot tile decode showing bucket values",
        "how": "operator dispatches after merge, greps logs, decodes one FL/WI artifact tile, attests with the run url"
      }
    }
  ],
  "rollback": "path-scoped checkout of the five edited files + git rm of the new test file; tiles unaffected until a publish dispatch",
  "needs_clarification": [],
  "allowed_paths": [
    "layers/parcels/sources.json",
    "layers/parcels/fetch_parcels.sh",
    "layers/parcels/normalize_parcels.py",
    "layers/parcels/qa_parcels.py",
    "layers/parcels/layer.json",
    "layers/parcels/tests/test_use_adapters.py"
  ],
  "test_baseline": {
    "files": 15,
    "tests": 151,
    "recorded_at": "2026-10-25T22:36:50Z"
  }
}
```

## Routing
Small M planned by the architect (design fully specified in brief-01.md from this session's live
value harvests). One Opus forge-builder implements step 01; Fable forge-verifier grades it —
mandatory tier because the change extends the licensing-critical attribute whitelist.

## Steps
### Step 01 — use adapters + whitelist + qa vocab gate + contract
- Brief: `.forge/tasks/T-0012/brief-01.md` (complete design: adapter code, per-state wiring, harvested value tables, gate mechanics).
- Verify: `.forge/bin/forge-check T-0012 01`

## Validation Criteria
- DoD-1..3 run locally via the checks above (adapter tables, whitelist/stats/fetch plumbing, vocab gate + contract doc).
- DoD-4 external: the 7-unit validation dispatch after merge; operator attests.

## Rollback
Path-scoped checkout (see json). The live tileset changes only at the next publish dispatch.

## Post-verdict annotation (2026-10-26)
Shipped contract = 6 use states (FL MA IN DC WI MT): NJ was unwired mid-task when run 40243912707 proved the statewide gdb lacks PROP_CLASS (FGDB -select hard-fails). DoD-3/DoD-4 prose above predates that; the verifier graded against the current contract and PASSed (verdict-01.json).
