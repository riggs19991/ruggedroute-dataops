# Inline Plan: T-0010 — parcels: port the go-pmtiles 1.31 bounds parser so the in-CI tile gate runs again

```json
{
  "schema": "forge/plan/2",
  "task": "T-0010",
  "class": "X",
  "risk": "none",
  "chain": false,
  "routing": {
    "mode": "inline",
    "builder": null,
    "verifier": {
      "agent": "forge-verifier",
      "model": "fable",
      "effort": "medium"
    },
    "justification": "class X root-cause fix, one function body ported from the sibling layer that already diagnosed and fixed the same break; architect codes inline, Fable verifier mandatory"
  },
  "steps": [],
  "dod": [
    {
      "id": "DoD-1",
      "criterion": "WHEN pmtiles_bounds() in layers/parcels/qa_parcels.py is given go-pmtiles 1.31 `show` output (the `bounds: (long: X, lat: Y) (long: X, lat: Y)` and `antimeridian_adjusted_bounds w,s,e,n` forms) THE SYSTEM SHALL return (w,s,e,n) instead of None, and SHALL still parse the legacy `bounds: w,s,e,n` form",
      "check": "pytest layers/parcels/tests/test_qa_bounds.py -q"
    },
    {
      "id": "DoD-2",
      "criterion": "WHEN the next quarterly-parcels CI run executes gate_tiles() THE SYSTEM SHALL decode probe tiles (no 'could not parse bounds' warning) and enforce the attribute whitelist inside decoded tiles",
      "check": "external",
      "external": {
        "what": "a quarterly-parcels validation dispatch (any unit) whose 'Tiles + QA' job log contains no 'could not parse bounds' warning and no 'no probe tile contained a parcels layer' for a mainland unit",
        "how": "operator dispatches the subset validation run planned for this session, greps the job log, then .forge/bin/forge-status attest T-0010 main DoD-2 --by riggs/operator --evidence <run url>"
      }
    }
  ],
  "rollback": "git revert the single commit; the gate returns to its previous skipped-with-warning behavior, which was the status quo",
  "needs_clarification": [],
  "allowed_paths": ["layers/parcels/qa_parcels.py", "layers/parcels/tests/test_qa_bounds.py"],
  "test_baseline": {
    "files": 13,
    "tests": 129,
    "recorded_at": "2026-10-25T21:06:09Z"
  }
}
```

## Routing
Inline (class X): the exact parser already exists in layers/roads_tnm/qa_roads_tnm.py:240-254 with a
comment documenting that the parcels copy never matches 1.31 output. Port the function body verbatim,
keeping the parcels type annotation.

## Steps
1. Replace the regex body of pmtiles_bounds() in layers/parcels/qa_parcels.py with the roads_tnm
   3-pattern version (antimeridian_adjusted_bounds, paren long/lat pair, legacy w,s,e,n).
2. Local check: run the new function body against the three documented output strings.
3. CI proof rides the next validation dispatch (shared with T-0009 + the land-use task).

## Validation Criteria
- DoD-1: the ported parser returns (w,s,e,n) for all three documented `pmtiles show` output forms
  (1.31 paren pair, antimeridian_adjusted_bounds line, legacy comma form) — proven by an inline
  python check against literal strings taken from the roads_tnm comment.
- DoD-2: the next quarterly-parcels validation dispatch logs NO "could not parse bounds" warning
  and the tile gate decodes probes (external evidence attached to that run id).

## Rollback
git revert the single commit. The gate returns to skipped-with-warning — exactly the pre-task
status quo; nothing downstream consumes gate_tiles() output beyond pass/fail.
