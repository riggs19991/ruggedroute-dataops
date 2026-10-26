# Handoff: T-0012 — parcels land-use classification (`use` bucket)

## Where things stand
SHIPPED AND VERIFIED; parked --partial solely on the operator-mode step-commit gap (ruling.md).
The parcels pipeline now emits `use` (RES AG VAC COM IND FOREST GOV) for FL MA IN DC WI MT,
whitelisted and vocabulary-gated; NJ dropped with evidence (its gdb lacks PROP_CLASS). Code on
origin/main (b1436fc + 3832d02 + 45783cf). Next operator action: the full publish dispatch.

## Done, with evidence
- Builder step 01 DONE (checks/01-1792969801-forge-builder.json: `python .forge/bin/forge-check
  T-0012 01 --agent forge-builder` pass=5 fail=0; suite 91+1skip; 45 new tests).
- Verifier verdict PASS (verdict-01.json; draft gate-validated; 55 refutation probes; ratchet
  151→196 no losses; scope clean 9025dd9..45783cf).
- DoD-4 attested (checks/01-1792977179-human.json: runs 40243912707 + 40246926809 green across
  the 6 use states + NJ-unwired; FL Fort Myers + WI Madison tile decodes vocab-clean; use null
  rates FL_1 0.025 / WI 0.1189 / MA 0.0266).
- FDOR curl hardened `--retry-all-errors` (3832d02) after the FL_2 connection reset.

## Remaining
- Full 26-unit publish dispatch (operator; sanctioned by this task's DoD-4 follow-through).
- Upstream Forge fix for the step-commit operator gap (lessons/step-commit-operator-gap.md) —
  queue as the next task.
- Stale attr lists: README.md:42 (+ forge bindings notes) say apn/county/acres/st — follow-up T.
- Client lockstep: app USE_LABELS == these buckets (already shipped, app T-0011/T-0012).

## Gotchas / do not touch
- FGDB `-select` HARD-FAILS on unknown field names (shapefiles only warn) — every gdb-unit
  field is a live-verified contract (normalize_parcels.py comment, run 40243912707 NJ).
- NJ's use route is the MOD-IV composite SERVICE, never the statewide gdb.
- qa-side USE_BUCKETS is deliberately independent of normalize's copy.
- use null-rate semantics: None = unconfigured; 1.0 = configured-but-empty (red flag).

```json
{"schema": "forge/handoff/2", "task": "T-0012", "step": "task", "status": "DONE_WITH_CONCERNS",
 "summary": "land-use use bucket shipped for 6 states with whitelist+vocab gates, verifier PASS + attested validation runs; parked --partial only because operator-mode cannot record the step commit (ruling.md); full publish dispatch is the next operator action",
 "files_changed": ["layers/parcels/sources.json", "layers/parcels/fetch_parcels.sh",
                   "layers/parcels/normalize_parcels.py", "layers/parcels/qa_parcels.py",
                   "layers/parcels/layer.json", "layers/parcels/tests/test_use_adapters.py"],
 "checks_run": [{"cmd": "python .forge/bin/forge-check T-0012 01 --ratchet --agent forge-verifier", "exit": 0},
                {"cmd": "pytest layers/parcels/tests -q", "exit": 0}],
 "verdict": "PASS"}
```
