# Changelog

One line per closed Forge task, appended by `.forge/bin/forge-status close`.

- 2026-10-11 T-0001 [T] docs: add the Forge build log and link it from the Forge README — added forge/docs/BUILD-LOG.md (process record, deviations, unverified items, residuals) and linked it from forge/README.md | checks: lib-unit pass (done)
- 2026-10-11 T-0002 [T] release: merge the Forge to main, tag v1.0.0, install into RuggedRoute, RuggedRoutehq and plot-device — CHANGELOG release line; Forge installed into RuggedRoute and plot-device on branch forge/install; main fast-forwarded and tagged v1.0.0 | checks: lib-unit pass (done)
- 2026-10-11 T-0003 [T] fix: Paths.rel must relativise on real paths so macOS /var -> /private/var symlinked roots are inside the repo — Paths.rel relativises on resolved paths when the lexical prefix is a symlink (macOS /var -> /private/var); regression test added; installed copy and plugin mirror refreshed; 393 tests, smoke 26/26 | checks: lib-unit pass (done)
