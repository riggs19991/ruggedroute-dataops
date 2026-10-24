# Changelog

One line per closed Forge task, appended by `.forge/bin/forge-status close`.

- 2026-10-11 T-0001 [T] docs: add the Forge build log and link it from the Forge README — added forge/docs/BUILD-LOG.md (process record, deviations, unverified items, residuals) and linked it from forge/README.md | checks: lib-unit pass (done)
- 2026-10-11 T-0002 [T] release: merge the Forge to main, tag v1.0.0, install into RuggedRoute, RuggedRoutehq and plot-device — CHANGELOG release line; Forge installed into RuggedRoute and plot-device on branch forge/install; main fast-forwarded and tagged v1.0.0 | checks: lib-unit pass (done)
- 2026-10-11 T-0003 [T] fix: Paths.rel must relativise on real paths so macOS /var -> /private/var symlinked roots are inside the repo — Paths.rel relativises on resolved paths when the lexical prefix is a symlink (macOS /var -> /private/var); regression test added; installed copy and plugin mirror refreshed; 393 tests, smoke 26/26 | checks: lib-unit pass (done)
- 2026-10-13 T-0004 [X/R] parcels: restore the MN plan_parcels_open source URL and poll the ND hub export instead of failing on its first 400, then re-run the Q4 quarterly — handoff .forge/tasks/T-0004/handoff.md (done)
- 2026-10-13 T-0005 [T] docs: refresh the README layer status table from the live TileJSON versions and fix the broken master-plan pointer — README: six layer rows now say LIVE with cadence (roads_context, nfs_trails, blm_routes, nps_roads, parcels, roads_tnm), the dead master-plan pointer is replaced by an honest note, and a live-version hint points at the worker TileJSON | .forge/tasks/T-0005/checks/main-1791874790-unknown.json (done)
- 2026-10-13 T-0006 [X/R] ci: pin tippecanoe 2.79.0 in monthly-ownership.yml like the other three workflows — handoff .forge/tasks/T-0006/handoff.md (done)
- 2026-10-13 T-0007 [S] worker: add a real test for worker-tiles so the binding's worker verify entry can stop being a todo — handoff .forge/tasks/T-0007/handoff.md (done)
- 2026-10-24 T-0011 [X] Forge 1.0.1: binding.agent_paths for non-Forge agents + Git Bash on Windows (ADR 0002 upstream) — handoff .forge/tasks/T-0011/handoff.md (done)
