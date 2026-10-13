# Handoff T-0007 — worker: add a real test for worker-tiles so the binding's worker verify entry can stop being a todo

## Where things stand
worker-tiles now has a real `npm test`: `node --test "test/**/*.test.js"` runs `test/index.test.js`, which builds an uncompressed PMTiles v3 archive in memory, fakes the R2 bucket, the KV alias namespace and `caches.default`, and drives `src/index.js` through every route and failure branch (11 tests). No new dependency; `pmtiles` was already a runtime dependency and Node 22 ships the runner. Protected `src/**` and `wrangler.toml` are untouched. The verifier (sonnet/medium) returned PASS after re-running the checks and mutation-testing a scratch copy of the worker.

## Done, with evidence
- `npm test` passes in worker-tiles (11/11) — `cd worker-tiles && npm test` exit 0 (.forge/tasks/T-0007/checks/main-1791892651-unknown.json)
- At least 9 passing tests cover tile, TileJSON, alias, cache hit, alias-flip miss, 204, missing-object 404, unknown-path 404, 405 and OPTIONS — DoD-2 check exit 0 (.forge/tasks/T-0007/checks/main-1791892651-unknown.json)
- Test lands under the binding's `worker-tiles/**/*.test.js` glob; src/ and wrangler.toml unchanged — DoD-3 check exit 0 (.forge/tasks/T-0007/checks/main-1791892651-unknown.json)
- Existing verify entries still pass: lib-unit exit 0, worker `npx wrangler deploy --dry-run` exit 0 (same record)
- Verifier PASS, ratchet 129→129, no deletions (.forge/tasks/T-0007/verdict-main.md, checks/main-1791892668-unknown.json)

## Remaining
- Human edit (binding.json is model-locked): replace the `worker` verify entry's cmd `cd worker-tiles && npx wrangler deploy --dry-run` with `cd worker-tiles && npm test` and drop its `todo`; keep the dry-run as a second entry if the bundle check is still wanted.
- Optional: run `npm test` in `.github/workflows/deploy-worker.yml` before deploy (protected path, needs a risk R task).
- Deferred from the verdict: HEAD requests are untested.

```json
{
  "schema": "forge/handoff/2",
  "task": "T-0007",
  "step": "task",
  "status": "DONE",
  "files_changed": ["worker-tiles/package.json", "worker-tiles/test/index.test.js"],
  "checks_run": [
    { "cmd": "cd worker-tiles && npm test", "exit": 0 },
    { "cmd": "cd worker-tiles && test \"$(node --test --test-reporter=tap 'test/**/*.test.js' 2>/dev/null | grep -c '^ok')\" -ge 9", "exit": 0 },
    { "cmd": "test -f worker-tiles/test/index.test.js && git diff --quiet HEAD -- worker-tiles/src worker-tiles/wrangler.toml", "exit": 0 },
    { "cmd": "cd lib && python3 -m unittest -v", "exit": 0 },
    { "cmd": "cd worker-tiles && npx wrangler deploy --dry-run", "exit": 0 }
  ],
  "not_verified": [],
  "failed_approaches": ["`node --test test/` (a directory argument) is not accepted by Node 22: it tries to load `test` as a module; use the glob `test/**/*.test.js`"],
  "next_action": "none",
  "commit": null
}
```
