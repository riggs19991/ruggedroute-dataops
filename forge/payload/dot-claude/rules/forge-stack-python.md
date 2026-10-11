---
paths:
  - "**/*.py"
---
# Forge stack rules — Python data pipelines
- Normalizers are tolerant: malformed upstream rows go to the review-queue artifact; never raise on bad data.
- Tests: `cd lib && python3 -m unittest -v` for lib/, `pytest layers/<layer>/tests -q` for a layer (only lands, parcels and roads_tnm have tests today; a layer without tests gets them as the first DoD); `pytest -q` prints nothing on success — the exit code is the signal.
- Fixtures over live services: never query ArcGIS/live endpoints in tests; use `lib/fixtures/`.
- Never conflate OSM-derived data into other tilesets; never let owner names reach tile attributes.
- Run every command from the repository root.
