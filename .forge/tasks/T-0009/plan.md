# Inline Plan: T-0009 — county/acres uniformity across parcel units

```json
{
  "schema": "forge/plan/2",
  "task": "T-0009",
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
    "justification": "class X data-quality defect; architect codes inline grounded in live field probes (MT CountyName + TX COUNTY exist at source; FL CO_NO and VA FIPS need static tables harvested from FDOR order anchors and Census codes2020); Fable verifier mandatory"
  },
  "steps": [],
  "dod": [
    {
      "id": "DoD-1",
      "criterion": "WHEN normalize builds the county attribute THE SYSTEM SHALL emit a display NAME (FL CO_NO incl. float-strings like '58.0' via the FDOR table; VA FIPS via the Census-2020 table; passthrough for name-carrying sources) and SHALL OMIT the attribute for any untranslatable bare-numeric value — codes never reach tiles",
      "check": "pytest layers/parcels/tests/test_county_uniformity.py -q"
    },
    {
      "id": "DoD-2",
      "criterion": "WHEN a unit is fetched THE SYSTEM SHALL map county from the source's own name column where one exists (MT CountyName, TX COUNTY) per sources.json, and normalize SHALL print per-attribute null-rate stats (apn/county/acres) so silent field-name drift is visible in CI logs",
      "check": "pytest layers/parcels/tests -q"
    },
    {
      "id": "DoD-3",
      "criterion": "WHEN the next validation dispatch runs FL and MT units THE SYSTEM SHALL produce tiles whose county values are names (spot: Orlando tile county == 'Orange'), verified from the run artifacts or live tiles after publish",
      "check": "external",
      "external": {
        "what": "validation-run artifact or post-publish tile decode showing FL county='Orange' at the Orlando probe and MT county a name not a code",
        "how": "operator decodes the artifact/live tile after the combined land-use+T-0009 dispatch and attests with the run/tile evidence"
      }
    }
  ],
  "rollback": "path-scoped: git checkout <pre-commit> -- layers/parcels/normalize_parcels.py layers/parcels/sources.json layers/parcels/layer.json && git rm layers/parcels/tests/test_county_uniformity.py; tiles revert on the next scheduled quarterly run",
  "needs_clarification": [],
  "allowed_paths": [
    "layers/parcels/normalize_parcels.py",
    "layers/parcels/sources.json",
    "layers/parcels/layer.json",
    "layers/parcels/tests/test_county_uniformity.py"
  ],
  "test_baseline": {
    "files": 14,
    "tests": 133,
    "recorded_at": "2026-10-25T21:38:11Z"
  }
}
```

## Routing
Inline X. Ground truth from this session's live probes: MT service layer exposes CountyName
(COUNTYCD currently mapped); TX StratMap DBFs carry COUNTY names (FIPS currently mapped); FL is
CO_NO 11-77 (FDOR alphabetical, anchors 23=Miami-Dade and 58=Orange proven from the S42 Orlando
tile); VA source is geometry+FIPS only (per its own notes) → Census codes2020 table (133
localities, harvested this session: 51059=Fairfax County, 51760=Richmond city).

## Steps
1. sources.json: MT county COUNTYCD→CountyName; TX_1..3 county FIPS→COUNTY; notes updated.
2. normalize_parcels.py: COUNTY_NAMES tables (FL int-code, VA 5-digit FIPS) + county
   post-processing (float-string tolerant int parse → table; untranslatable numerics dropped;
   names passthrough) + per-attribute null-rate stat line.
3. layer.json: county schema text = display-name contract; acres reality note (absent
   UT/VA/ME; OH ~96% null at source).
4. tests/test_county_uniformity.py: FL '58.0'→Orange, FL 23→Miami-Dade, VA '51059'→Fairfax
   County, bare-code drop, name passthrough, null-rate stats shape.

## Validation Criteria
- DoD-1/DoD-2: the new test file + full parcels suite green via forge-check.
- DoD-3: external — attested from the combined validation dispatch artifacts (Orlando county
  probe) after this task and the land-use task land together.

## Rollback
Path-scoped checkout of the three edited files + rm of the new test file (see json). Never
revert commits (Forge payload precedent from T-0010).
