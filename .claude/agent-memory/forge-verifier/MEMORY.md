# forge-verifier calibration notes

At most 60 lines; facts about this repo's checks, not instructions.

- Inline X tasks may be uncommitted when verified: `git status --porcelain` against HEAD is the range; `git diff HEAD -- <paths>` shows the work.
- `forge-check <task> main --ratchet` prints one FORGE_CHECK line per check plus FORGE_CHECK_RATCHET and the record path; it takes ~5 s here and DoD-3 probes hit the live hubs through the proxy.
- forge-check records are stamped `agent_id: unknown` in this environment; `forge-gate --verdict ... --agent unknown` exits 0 against them.
- forge-gate accepts a non-git `range` string (used `2716eb9..worktree`) and a negative `exit` on an external UNKNOWN criterion.
- A pytest plugin on PYTHONPATH that overrides `socket.socket.__init__`/`getaddrinfo` (`-p blocksock`) is a cheap proof that a test file never touches the network.
- Older check records in `checks/` can show earlier failing runs of the same step; only the newest record from this session counts.
- quarterly-parcels.yml sets no `timeout-minutes`, so the 360-min GitHub default bounds per-unit fetch pollers.
- Hub `resultUrl` blobs refuse HEAD Content-Length and the remote closes ranged GETs through the proxy; inspecting an export zip without a full download is not feasible here.
- `.forge/tasks/<task>/drafts/` may not exist; the Write tool creates it.
- Replacing `socket.socket` itself with a function breaks pytest startup (ssl subclasses it via the anyio plugin); patching `socket.socket.connect`, `getaddrinfo`, `create_connection` and `urllib.request.urlopen` plus `-p no:anyio` works and counts attempts.
- forge-check's `layer-tests` stage matches paths against the worktree, so once the work is committed it skips; run `pytest layers/<layer>/tests -q` by hand on a clean tree.
- `forge-status attest <task> main <DoD>` refuses inline tasks ("has no step main", `Status.attest` -> `_step`); the gate still accepts a hand-written `main-<ts>-human.json` whose keys match `status.py:1593` (`gates.py:663` reads human records by criterion).
- `gh run view <id> --repo riggs19991/ruggedroute-dataops --json status,conclusion,headSha,jobs` works through the proxy and ties a run to the exact commit; `curl -s https://tiles.ruggedroutehq.com/parcels.json | jq -r .version` works too.
- Local `main` can lag `origin/main` in this checkout; `git merge-base --is-ancestor` settles whether it is behind or diverged.
- Hub ND export flips between ExportingData and Completed across runs; a probe's status is not stable evidence of anything beyond "answers an envelope".
