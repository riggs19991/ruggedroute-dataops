# Handoff: T-0009 — county is a display name or absent

## Where things stand
Done, verifier PASS, plus a post-verdict round applying its deferred findings. Tiles now carry
county NAMES for FL VA MD NH IN (tables) and MT TX (source name columns); every untranslatable
code drops. Ships nationally with the land-use full dispatch.

## Done, with evidence
- normalize_county + FL/VA tables, MT CountyName + TX COUNTY remaps (checks/main-1792966483-forge-verifier.json:
  verifier red/green, 5/5 logic mutants killed, 43-case probe, full table cross-checks).
- Validation run 40236586600 all green (checks/main-1792966404-human.json: operator decoded
  FL Orlando 13/2244/3417 = 'Orange'×14,137, zero bare codes; MT Helena = 'Lewis and Clark';
  null rates FL_2 county 0.0077 == apn rate, MT 0.0).
- Post-verdict round (checks/main-1792967623-unknown.json: `python .forge/bin/forge-check T-0009 main`
  pass=3, suite 46+1skip): MD JURSCODE (24, geo-anchored MONT/ANNE on live tiles), NH CountyId
  1-10 alphabetical (geo-anchored Concord=7, Nashua=6), IN FIPS (92, Census codes2020, anchor
  Indianapolis 18097); table-first lookup (letter codes hit tables BEFORE the name passthrough;
  unmapped code-like tokens in table states drop); is_integer + OverflowError strictness; 8
  discriminating tests killing the verifier's M6/M7/M8 mutants; layer.json VA-suffix convention
  ("client must never append ' County'") + WI acres note.

## Remaining
- The combined land-use validation + full publish exercises all 7 table states end to end; T-0008's
  live_tiles.py probe then gates county name-likeness continuously (add that check there).
- DE county confirmed clean names at source; no table needed.

## Gotchas / do not touch
- VA names KEEP their 'County'/'city' suffixes on purpose (Fairfax County ≠ Fairfax city);
  all other states ship bare names. Documented in layer.json.
- MD codes are LETTERS — any new table state must rely on the table-first lookup order in
  normalize_county, never the letters-means-name heuristic alone.
- FDOR order files Miami-Dade as 'Dade' and 'St.' as 'Saint' (the order-property test encodes this).

```json
{"schema": "forge/handoff/2", "task": "T-0009", "step": "task", "status": "DONE",
 "summary": "county display-name contract: 5 code tables + 2 source remaps, geo-anchored, mutant-killing tests; verifier PASS; proven on run 40236586600",
 "files_changed": ["layers/parcels/normalize_parcels.py", "layers/parcels/sources.json",
                   "layers/parcels/layer.json", "layers/parcels/tests/test_county_uniformity.py"],
 "checks_run": [{"cmd": "python .forge/bin/forge-check T-0009 main", "exit": 0},
                {"cmd": "pytest layers/parcels/tests -q", "exit": 0}],
 "verdict": "PASS"}
```
