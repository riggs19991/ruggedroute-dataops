# Inline Plan: T-0007 — worker: add a real test for worker-tiles so the binding's worker verify entry can stop being a todo

```json
{
  "schema": "forge/plan/2",
  "task": "T-0007",
  "class": "S",
  "risk": "none",
  "chain": false,
  "routing": {
    "mode": "inline",
    "builder": null,
    "verifier": {
      "agent": "forge-verifier",
      "model": "sonnet",
      "effort": "medium"
    },
    "justification": "S: DoD-1 adds the first worker test (importers 0, no risk or important hits); the verifier runs because tests change"
  },
  "steps": [],
  "dod": [
    {
      "id": "DoD-1",
      "criterion": "WHEN `npm test` runs in worker-tiles THE SYSTEM SHALL execute a Node test suite against src/index.js and exit 0",
      "check": "cd worker-tiles && npm test"
    },
    {
      "id": "DoD-2",
      "criterion": "WHEN the suite runs THE SYSTEM SHALL cover the tile route, the TileJSON route, KV alias resolution, the edge-cache hit and alias-flip miss, the empty-tile 204, the missing-object 404, the unknown-path 404, the 405 and the OPTIONS CORS preflight (at least 9 passing tests)",
      "check": "cd worker-tiles && test \"$(node --test --test-reporter=tap 'test/**/*.test.js' 2>/dev/null | grep -c '^ok')\" -ge 9"
    },
    {
      "id": "DoD-3",
      "criterion": "WHEN the binding's test_globs are evaluated THE SYSTEM SHALL find the new test under worker-tiles/**/*.test.js and no file under worker-tiles/src or wrangler.toml changes",
      "check": "test -f worker-tiles/test/index.test.js && git diff --quiet HEAD -- worker-tiles/src worker-tiles/wrangler.toml"
    }
  ],
  "rollback": "git revert <sha> (one commit; no deploy, no protected path touched)",
  "test_baseline": {
    "files": 13,
    "tests": 129,
    "recorded_at": "2026-10-13T11:57:06Z"
  },
  "needs_clarification": [],
  "allowed_paths": [
    "worker-tiles/package.json",
    "worker-tiles/package-lock.json",
    "worker-tiles/test/index.test.js"
  ]
}
```

## Hypothesis / Objective
Give worker-tiles a real `npm test` (Node 22 built-in `node --test`, no new dependencies) that exercises `src/index.js` end to end
against an in-memory PMTiles v3 archive and fake R2 / KV / `caches.default` bindings, so the binding's `worker` verify entry can
replace `npx wrangler deploy --dry-run` with `cd worker-tiles && npm test` (binding.json is model-locked; that swap is a human edit).

## Validation Criteria
- DoD-1: `npm test` runs the suite and exits 0 — check: `cd worker-tiles && npm test`
- DoD-2: at least 9 passing tests covering every route and failure branch of the worker — check: `cd worker-tiles && test "$(node --test --test-reporter=tap 'test/**/*.test.js' 2>/dev/null | grep -c '^ok')" -ge 9`
- DoD-3: test lands under the binding's `worker-tiles/**/*.test.js` glob; protected src/ and wrangler.toml untouched — check: `test -f worker-tiles/test/index.test.js && git diff --quiet HEAD -- worker-tiles/src worker-tiles/wrangler.toml`

## Rollback
`git revert <sha>` of the single commit. Nothing is deployed and no protected path changes.
