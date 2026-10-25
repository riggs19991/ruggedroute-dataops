# Handoff: T-0010 — parcels Gate 3 bounds parser (go-pmtiles 1.31)

## Where things stand
Done and verified PASS. The parcels tile gate (Gate 3: decode + in-tile whitelist) runs again in CI.

## Done, with evidence
- Ported the 3-pattern `pmtiles_bounds()` from roads_tnm into `layers/parcels/qa_parcels.py`
  (antimeridian_adjusted_bounds → 1.31 paren pair → legacy). Red check: the new tests fail 2/4
  against the pre-fix file (verifier re-ran it).
- `layers/parcels/tests/test_qa_bounds.py`: 4 tests incl. a precedence test with distinct
  antimeridian values (verifier deferred-3 applied post-verdict; forge-check re-run green,
  record main-1792964052-unknown.json: pass=3 fail=0).
- CI proof: DC validation run 40234246805 — "Gate 3: tile decode" with no bounds-skip warning,
  run success. Human attestation record main-1792963029-human.json, annotated with provenance
  (hand-written; attest CLI cannot address inline step main — see lessons/attest-inline-step-gap.md).
- Verifier verdict PASS (verdict-main.json; Opus forge-verifier, 24-case refutation probe + mutation
  test + ratchet 129→133).

## Remaining
- Deferred-5 (optional): tighten the `[\d.]+` number token in BOTH qa_parcels.py and
  qa_roads_tnm.py to `(-?\d+(?:\.\d+)?)` — unreachable from %f output, fails loudly today.
- Gate 3's first FULL-matrix exercise rides the next land-use/T-0009 validation dispatch.

## Gotchas / do not touch
- Commit eb882bc also carries the Forge 1.0.0→1.0.1 installed-payload upgrade (fixes
  forge-check's WSL-bash spawn on Windows). NEVER `git revert` that commit; the task rollback is
  path-scoped (plan.md ## Rollback).
- forge-check runs with hooks dormant in operator sessions → check records stamp `unknown/cli`.

```json
{"schema": "forge/handoff/2", "task": "T-0010", "step": "main", "status": "done",
 "summary": "Gate 3 tile-decode gate unskipped: 1.31 bounds parser ported, 4-test regression suite, CI-proven on DC run 40234246805, verifier PASS",
 "files": ["layers/parcels/qa_parcels.py", "layers/parcels/tests/test_qa_bounds.py"],
 "checks": ["main-1792964052-unknown.json", "main-1792963029-human.json"],
 "verdict": "PASS"}
```
