# Brief T-0012/01 — parcels `use` bucket (land-use classification)

```json
{
  "schema": "forge/brief/2",
  "task": "T-0012",
  "step": "01",
  "owner_agent": "forge-builder",
  "model": "opus",
  "effort": "medium",
  "allowed_paths": [
    "layers/parcels/sources.json",
    "layers/parcels/fetch_parcels.sh",
    "layers/parcels/normalize_parcels.py",
    "layers/parcels/qa_parcels.py",
    "layers/parcels/layer.json",
    "layers/parcels/tests/test_use_adapters.py"
  ],
  "may_edit_tests": false,
  "tdd": false,
  "risk": "none",
  "expected_fail_first": [],
  "red_ok": false,
  "bootstrap": "Read this brief top to bottom, then layers/parcels/normalize_parcels.py (county tables + build_props + normalize + main), layers/parcels/tests/test_county_uniformity.py (importlib test pattern), layers/parcels/fetch_parcels.sh (rest-mode FIELDS snippet), layers/parcels/qa_parcels.py (WHITELIST + gates). Then implement sections 1-6 in order.",
  "max_tool_calls": 120,
  "dod": ["DoD-1", "DoD-2", "DoD-3"],
  "checks": [
    "pytest layers/parcels/tests/test_use_adapters.py -q",
    "pytest layers/parcels/tests -q"
  ]
}
```

## Goal
Ship one new whitelisted tile attribute `use` with a closed 7-value vocabulary, wired per-unit
through sources.json adapters, gated in QA, and documented in the layer contract — all tests
green via `.forge/bin/forge-check T-0012 01`.

## Context the worker needs
This repo builds the RuggedRoute parcel tileset (layers/parcels/: fetch → normalize → tiles →
qa, driven by sources.json per matrix unit). The owner-names-never-in-tiles WHITELIST in
normalize_parcels.py and qa_parcels.py is the licensing invariant — you are EXTENDING it by
exactly one key. The Android client already parses `use` (app repo USE_LABELS, 7 buckets) — the
vocabularies must match exactly. Every adapter below was specified by the architect from live
value harvests (2026-10-25: ArcGIS distinct-value queries, DBF reads, live-tile decodes) — do
not redesign them; implement as written. normalize_parcels.py already has the analogous
patterns: county tables + normalize_county (T-0009), acres_divisor plumbing, attr_present
null-rate stats; tests/test_county_uniformity.py shows the importlib test pattern.

One new whitelisted tile attribute `use` with a closed 7-value vocabulary:
`RES AG VAC COM IND FOREST GOV`. Seven states ship it in v1 — every adapter below is grounded
in live values harvested 2026-10-25 (service distinct-value queries, DBF reads, live tiles).
Unknown/unmapped values yield None and the attribute is OMITTED (never an "OTHER" bucket).

## allowed_paths
sources.json · fetch_parcels.sh · normalize_parcels.py · qa_parcels.py · layer.json ·
tests/test_use_adapters.py (new) — all under layers/parcels/.

## 1. normalize_parcels.py
Add near the county tables:

```python
USE_BUCKETS = frozenset({"RES", "AG", "VAC", "COM", "IND", "FOREST", "GOV"})

def _use_fl_dor(v):
    s = str(v).strip()
    if not s[:3].isdigit():
        return None
    n = int(s[:3])
    if n == 0: return "VAC"            # 000 vacant residential
    if 1 <= n <= 9: return "RES"
    if 10 <= n <= 39: return "COM"
    if 40 <= n <= 49: return "IND"
    if 54 <= n <= 58: return "FOREST"  # timberland band inside the ag range
    if 50 <= n <= 69: return "AG"
    if 70 <= n <= 89: return "GOV"     # institutional + governmental
    return None                        # 90-99 centrally assessed / misc

def _use_ma_dor(v):
    d = str(v).strip().lstrip("0")
    if len(d) < 3 or not d.isdigit():
        return None                    # '010C' style letter suffixes -> omit
    return {"1": "RES", "3": "COM", "4": "IND", "6": "FOREST",
            "7": "AG", "9": "GOV"}.get(d[0])   # 2xx open, 5xx personal, 8xx rec -> omit

def _use_in_dlgf(v):
    d = str(v).strip()
    if len(d) < 3 or not d.isdigit():
        return None
    return {"1": "AG", "3": "IND", "4": "COM", "5": "RES", "6": "GOV"}.get(d[0])

def _use_nj_modiv(v):
    c = str(v).strip().upper()
    if c == "1": return "VAC"
    if c in ("2", "4C"): return "RES"
    if c in ("3A", "3B"): return "AG"
    if c == "4A": return "COM"
    if c == "4B": return "IND"
    if c.startswith("15"): return "GOV"
    return None                        # 5A/5B/6x rail+utility -> omit

def _use_dc_class(v):
    c = str(v).strip().upper()
    if c in ("1", "1A", "1B"): return "RES"
    if c == "2": return "COM"
    if c in ("3", "4"): return "VAC"   # 4 = blighted vacant
    return None

def _use_wi_propclass(v):
    first = str(v).split(",")[0].strip().upper()
    return {"1": "RES", "2": "COM", "3": "IND", "4": "AG",
            "5": "VAC", "5M": "FOREST", "6": "FOREST"}.get(first)  # 7 'other' -> omit

def _use_mt_proptype(v):
    t = str(v).lower()
    if "vacant" in t: return "VAC"
    if "industrial" in t or "mining" in t or "gravel" in t or "oilfield" in t: return "IND"
    if "apartment" in t or "condominium" in t or "townhouse" in t or "mobile" in t: return "RES"
    if "exempt" in t or "tribal" in t or "centrally assessed" in t or "utility" in t: return "GOV"
    if "farm" in t or "agricultural" in t: return "AG"
    if "forest" in t or "timber" in t: return "FOREST"
    if "golf" in t: return "COM"
    return None                        # 'Improved Property' etc. are ambiguous -> omit

USE_ADAPTERS = {
    "fl_dor": _use_fl_dor, "ma_dor": _use_ma_dor, "in_dlgf": _use_in_dlgf,
    "nj_modiv": _use_nj_modiv, "dc_class": _use_dc_class,
    "wi_propclass": _use_wi_propclass, "mt_proptype": _use_mt_proptype,
}
```

Plumbing:
- `WHITELIST` tuple gains `"use"` (order: apn, county, acres, st, use).
- `build_props(...)` gains `use_field=None, use_adapter=None`: after acres, read the raw value
  (same lower_index fallback as apn/county, through `clean()`), run the adapter, keep the result
  only if it is in `USE_BUCKETS`.
- `normalize(...)` passes them through; `attr_present` and the null-rate stats/print gain "use"
  (rate None when the unit configures no use_field — not 1.0; distinguish "not configured" from
  "configured but empty").
- `main()` reads `cfg.get("use_field")` / `cfg.get("use_adapter")`; unknown adapter name →
  `sys.exit` with a clear message. Run `check_mapping`-style forbidden-substring screening on
  use_field with the non-apn 'name' exemption (simplest: include it in the mapping dict passed to
  check_mapping under role "use" and keep the existing exemption condition `role != "apn"`), but
  do NOT let use_field join the county/apn extraction loop.

## 2. sources.json — add two keys per unit
FL_1, FL_2: `"use_field": "DOR_UC", "use_adapter": "fl_dor"`
MA: `"use_field": "USE_CODE", "use_adapter": "ma_dor"`
IN: `"use_field": "dlgf_prop_class_code", "use_adapter": "in_dlgf"`
NJ: `"use_field": "PROP_CLASS", "use_adapter": "nj_modiv"`
DC: `"use_field": "CLASSTYPE", "use_adapter": "dc_class"`
WI: `"use_field": "PROPCLASS", "use_adapter": "wi_propclass"`
MT: `"use_field": "PropType", "use_adapter": "mt_proptype"`
Append one sentence to each unit's notes naming the harvest basis (2026-10-25 probe). Do NOT
touch TX (STAT_LAND_ unpopulated in sampled counties), CT (municipal code soup), MD (DESCCIUSE
empty), VT (PROPTYPE is parcel-kind), HI (zoning-district, not assessment use) — record those
five exclusions in layer.json (see 4) so nobody re-adds them blind.

## 3. fetch_parcels.sh (rest mode only — MA is the only rest unit with a use_field)
The FIELDS python snippet currently joins `fields{}` values. Extend it to append
`cfg.get("use_field")` when set (dedup, keep order). Nothing else changes; http/hub/mirror
modes pass whole files to normalize.

## 4. qa_parcels.py
- `WHITELIST` gains `"use"`.
- New vocabulary gate wherever features are already iterated (Gate 1 full scan AND the Gate 3
  decoded-tile loop): any feature whose `use` value is not in
  `{"RES","AG","VAC","COM","IND","FOREST","GOV"}` is a FAILURE line
  (`use vocabulary violation: <value>`). Keep it one shared constant.

## 5. layer.json
- `schema.parcels` gains `"use": "normalized land-use bucket (string), optional — one of RES AG
  VAC COM IND FOREST GOV; v1 states FL MA IN NJ DC WI MT; adapters normalize assessment
  classes in the pipeline and the client maps buckets to labels (app USE_LABELS — change only
  in lockstep). Excluded after live probes 2026-10-25: TX (field unpopulated), CT (municipal
  code soup), MD (desc field empty), VT (field is parcel-kind), HI (zoning-district)."`
- `qa` section: note the vocabulary gate beside the whitelist gate.

## 6. tests/test_use_adapters.py (new; mirror test_county_uniformity.py's importlib pattern)
Pin with the HARVESTED values:
- fl_dor: "000"→VAC, "001"→RES, "0100"? no — FL codes are 3-char: "012"→COM, "048"→IND,
  "054"→FOREST, "060"→AG, "071"→GOV, "083"→GOV, "091"→None, ""→None, "XX"→None.
- ma_dor: "0101"→RES, "013"→RES? NO — "013"→RES is wrong: '013'.lstrip('0')=='13' len<3 → None.
  Pin: "0101"→RES, "0300"→COM? '0300'→'300'→COM? first digit '3'→COM ✓, "0400"→IND,
  "0601"→FOREST, "0712"→AG, "0900"→GOV, "010C"→None, "0200"→None, "013"→None.
- in_dlgf: "100"→AG, "199"→AG, "300"→IND, "400"→COM, "500"→RES? (values harvested stop at 3xx
  in the first 40 — the standard runs to 6xx; pin "510"→RES, "600"→GOV, "000"→None, "068"→None.
- nj_modiv: "1"→VAC, "2"→RES, "3A"→AG, "3B"→AG, "4A"→COM, "4B"→IND, "4C"→RES, "15A"→GOV,
  "15F"→GOV, "5A"→None, "6A"→None.
- dc_class: "1A"→RES, "1B"→RES, "2"→COM, "3"→VAC, "4"→VAC, ""→None.
- wi_propclass: "1"→RES, "1,2,4"→RES (first token), "4,5"→AG, "5M"→FOREST, "6"→FOREST,
  "5"→VAC, "7"→None, "2"→COM.
- mt_proptype: "VAC_R - Vacant Land - Rural"→VAC, "Vacant Land"→VAC, "Industrial Property"→IND,
  "IR - Industrial Rural"→IND, "Gravel Pit"→IND, "Oilfield Improvements"→IND, "Apartment"→RES,
  "Condominium"→RES, "Townhouse"→RES, "Mobile/RV Parks"→RES, "Exempt Property"→GOV,
  "Tribal Property"→GOV, "CA - Centrally Assessed"→GOV, "Locally Assessed Utility"→GOV,
  "Golf Course"→COM, "Improved Property"→None, None-ish ""→None.
- Vocabulary completeness: USE_ADAPTERS outputs ⊆ USE_BUCKETS (exercise every adapter over its
  pinned inputs and assert the union of non-None results ⊆ the frozenset); USE_BUCKETS == the
  7-value set.
- build_props integration: FL props with DOR_UC "001" + use_field/use_adapter kwargs → props
  carry use "RES"; without use_field → no use key; adapter returning junk can't leak (monkeypatch
  an adapter to return "RANCH", assert omitted).
- Stats: configured-but-empty vs not-configured distinction (normalize stats test optional —
  the T-0009 stats test pattern is in test_county_uniformity.py if needed).

## Definition of done
The plan's DoD-1..3 (DoD-4 is external, not yours):
- DoD-1 `pytest layers/parcels/tests/test_use_adapters.py -q` green — every pinned value from
  §6 buckets exactly as specified, every unknown yields None.
- DoD-2 full suite green + `"use"` in BOTH WHITELIST tuples + `use_field` honored by
  fetch_parcels.sh rest mode + null-rate stats include use (None when unconfigured).
- DoD-3 qa vocabulary gate live in geojsonl scan AND tile decode; layer.json documents buckets,
  the 7 states, the client-lockstep rule and the 5 exclusions.
Run `.forge/bin/forge-check T-0012 01` after your last edit — it runs lib-unit, layer-tests
(the 46+1skip suite must stay green and grow by your new file) and the DoD commands.

## Out of scope / do not touch
- The publish/workflow path (.github/), worker-tiles/, every other layers/* directory.
- FORBIDDEN_FIELD_SUBSTRINGS, the county tables, and the existing Gate 1/3 mechanics beyond
  adding the use checks.
- Do NOT add use to TX/CT/MD/VT/HI (probe-excluded; record the exclusions in layer.json only).
- Existing tests (no may_edit_tests): test_normalize_parcels.py, test_county_uniformity.py,
  test_qa_bounds.py stay byte-identical.

## Known failed approaches
- Keyword adapters over CT State_Use_Description / MD DESCCIUSE: harvested values are municipal
  free-text or empty — unusable; that is why those states are excluded, not adapted.
- TX STAT_LAND_/LOC_LAND_U: present in the DBF schema but unpopulated in sampled counties
  (48261 all-empty, 48337 all-empty across 20k rows) — do not wire it.
- An "OTHER" bucket: rejected by design; unmapped values omit the attribute so the client never
  renders a meaningless label.

- attempt 1 NEEDS_CONTEXT (2026-10-25T23:08:36Z): no next_action recorded
## Output contract
HANDOFF with sections: Where things stand · Done, with evidence (every bullet's FIRST line
carries a `command` or checks/ reference) · Remaining · Gotchas / do not touch · one fenced
```json block, schema forge/handoff/2, step "01", status DONE|BLOCKED|NEEDS_CONTEXT,
files_changed, checks_run [{cmd, exit}], summary. Write the draft to
.forge/tasks/T-0012/drafts/<agent-id>-handoff.md and validate with
`python .forge/bin/forge-gate --handoff T-0012 01 --from-file <draft> --agent <agent-id>`.
Do not commit, push, or touch .forge/ outside your draft.
