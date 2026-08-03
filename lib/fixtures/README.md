# lib/fixtures

`datesopen_corpus.json` is a real-world corpus of every DISTINCT season string found in the
live USFS EDW MVUM service (`EDW_MVUM_01` MapServer, layer 1 roads + layer 2 trails) across
all 17 vehicle-class season fields, harvested 2026-08-03, with each value classified through
`lib/normalize_mvum.py`'s `parse_seasons` (`parse_ok` + parsed `windows`). The pipeline
builder and test suite consume it to prove the tolerant parser handles everything the
government actually publishes (982 distinct values; only 4 fail: `04/01-12/33`,
`05/01/-10/31`, `<Null>`, `open`). Note the service's real field names differ from the
documented schema — the `*_gt50inches_datesopen`/`*_lt50inches_datesopen` fields drop
"inches" (`fourwd_gt50_datesopen`, etc.) and the e-bike fields are `e_bike_classN_dur`, not
`_datesopen`; the fixture's `field_resolution` block records the mapping per layer.
Regenerate with `python lib/fixtures/harvest_datesopen.py` (sequential curl requests with a
polite User-Agent; takes a couple of minutes) whenever USFS refreshes MVUM data or the
parser changes, and update `generated` review expectations accordingly.

## MVUM golden fixtures

- `mvum_synthetic_{road,trail}_original.geojsonl` + `mvum_golden_{road,trail}_original.jsonl`
  — the FROZEN pre-change pair: goldens captured from the Stage-0 standalone
  `normalize_mvum.py`. `test_mvum_adapter.py::AdditiveMaintLevelTrailClass` runs the
  original synthetics through the current adapter and requires byte-identical output —
  existing attrs may never move. Do not edit these files.
- `mvum_synthetic_{road,trail}.geojsonl` + `mvum_golden_{road,trail}.jsonl` — the current
  pair, extended with the real bulk-GDB/EDW spellings `OPERATIONALMAINTLEVEL` and
  `TRAILCLASS` (an intended ADDITIVE schema change: `maint_level`/`trail_class` now reach
  the tiles); goldens regenerated with the fixed adapter.
