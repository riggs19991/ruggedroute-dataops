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
