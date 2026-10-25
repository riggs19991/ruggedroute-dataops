# SCHEMAS.md — every Forge data shape, with examples

Source: design §5; build contract: `forge/docs/MODULE-API.md` §2 (it wins on data shapes). The machine-readable assertion lists
live in `.forge/schemas/*.json` (Forge-owned; they are assertion lists read by the Python scripts, not JSON Schema validators).
A schema change is a MAJOR version (UPGRADING.md).

**Design rule.** JSON for anything a hook or script reads or a model must not freely rewrite; Markdown for anything a human or the
next role reads. Machine fields never live in YAML frontmatter. Every Markdown artifact that carries machine fields opens with
**one fenced ```` ```json ```` block** (the first one in the file is the one scripts read) plus fixed `## ` headings.
Timestamps a script compares are stored twice: ISO-8601 `*_at` for humans and integer epoch `*_ts` for scripts.
All model fields hold **aliases** (`haiku|sonnet|opus|fable`); agent frontmatter holds full ids and every comparison normalizes both.

| Artifact | Path | Schema id | Assertion list | Validated by |
|---|---|---|---|---|
| STATUS | `.forge/STATUS.json` | `schema_version: 2` | `.forge/schemas/status.json` | every `forge-status` write; `.forge/bin/forge-status validate` |
| Binding | `.forge/binding.json` | `schema_version: 2` | `.forge/schemas/binding.json` | `forge-status` on load; `/forge-doctor` |
| Plan | `.forge/tasks/<id>/plan.md` | `forge/plan/2` | `.forge/schemas/plan.json` | `.forge/bin/forge-gate --plan <id>`; `forge-status plan` |
| Brief | `.forge/tasks/<id>/brief-NN.md` | `forge/brief/2` | `.forge/schemas/brief.json` | the plan gate |
| Handoff | final message → `report-NN.md/json`; `handoff.md` | `forge/handoff/2` | `.forge/schemas/handoff.json` | `forge-gate --handoff`; SubagentStop; `forge-status close` |
| Verdict | final message → `verdict-NN.md/json` | `forge/verdict/2` | `.forge/schemas/verdict.json` | `forge-gate --verdict`; SubagentStop |
| Ledger | `.forge/ledger.jsonl` | `forge/ledger/2` | `.forge/schemas/ledger.json` | written only by scripts and hooks |
| Routing matrix | `.forge/schemas/routing.json` | `forge/routing/2` | (is itself the data) | read by `forge-status plan` and the planner |

## STATUS.json — the single source of truth (`.forge/schemas/status.json`)

Written **only** by `.forge/bin/forge-status` (atomic replace; stamps `updated_at/ts`, `updated_by {session_id, cmd}`; records the
file's sha256 in `.forge/.runtime/status.sha`; clears `dirty-main`, and `dirty-worker` on step transitions). A hand edit is detected
by the Stop gate (sha mismatch); after a deliberate one run `.forge/bin/forge-status validate --restamp`.

```json
{
  "schema_version": 2, "forge_version": "1.0.1", "project": "ruggedroute-dataops",
  "updated_at": "2026-10-11T18:42:10Z", "updated_ts": 1760208130,
  "updated_by": { "session_id": "7f2c…", "cmd": "forge-status step-report T-0007 01" },
  "context_state": "fresh",
  "task": {
    "id": "T-0007", "title": "nfs_trails: add golden-bbox count QA so the trail tileset can go live",
    "class": "M", "risk": "none", "size_source": "declared",
    "files": ["qa/golden_counts.py", "layers/nfs_trails/layer.json"], "creates": ["layers/nfs_trails/tests/test_golden.py"],
    "signals": { "files": 3, "dirs": 2, "importers": 3, "recent_cochanges": [], "tests_present": false, "risk_hits": [], "important_hits": [] },
    "class_justification": "3 declared files in 2 dirs, one dependent chain, no risk hits; nfs_trails has no tests so the plan adds them first",
    "phase": "execute", "plan": ".forge/tasks/T-0007/plan.md", "plan_author": "architect", "branch": null,
    "scope": ["qa/golden_counts.py", "layers/nfs_trails/layer.json", "layers/nfs_trails/tests/**"],
    "routing": { "mode": "single",
      "builder": { "agent": "forge-builder", "model": "opus", "effort": "medium" },
      "verifier": { "agent": "forge-verifier", "model": "opus", "effort": "medium" },
      "justification": "M-small, chain=false, tests added as DoD-1 → opus/medium builder, opus/medium verifier" },
    "steps": [ { "id": "01", "title": "golden-bbox QA for nfs_trails", "agent": "forge-builder", "model": "opus", "effort": "medium",
      "status": "reported", "attempts": 1, "from": null, "verify_attempts": 0,
      "started_at": "2026-10-11T18:30:00Z", "started_ts": 1760207400, "started_by": "7f2c…", "agent_id": "agent_7f3a",
      "base": "3e1f9c2…", "commit": "a91b0e4…", "brief": ".forge/tasks/T-0007/brief-01.md", "report": ".forge/tasks/T-0007/report-01.md",
      "verdict": null, "red_ok_until": null, "allowed_paths": ["qa/golden_counts.py", "layers/nfs_trails/layer.json", "layers/nfs_trails/tests/**"],
      "mechanical": false, "max_tool_calls": 60 } ],
    "escalation": { "step": "01", "round": 0 },
    "next_action": "Dispatch forge-verifier (opus/medium) on step 01: brief-01.md, report-01.md, range 3e1f9c2..a91b0e4.",
    "resume_hint": "Step 01 is reported and committed (a91b0e4).",
    "evidence_count": 1,
    "evidence": [ { "claim": "lib unit suite green after step 01", "command": "cd lib && python3 -m unittest -v", "exit": 0,
                    "when": "2026-10-11T18:40:02Z", "from": ".forge/tasks/T-0007/checks/01-1760208002-agent_7f3a.json" } ],
    "blocked_on": null, "external": null, "budget": { "cap_usd": 10.0 },
    "opened_at": "2026-10-11T18:10:00Z", "base": "3e1f9c2…"
  },
  "queue": [ { "id": "T-0008", "title": "roads_context: client layer manifest", "class_hint": "S" } ],
  "history": [ { "id": "T-0006", "title": "roads_tnm: parse go-pmtiles 1.31 bounds", "class": "S", "outcome": "done",
                 "cost_usd": null, "cost_source": "unknown", "handoff": ".forge/tasks/T-0006/handoff.md", "closed_at": "2026-10-10T12:00:00Z" } ]
}
```

- Enumerations: `context_state ∈ {fresh, stale}`; `class ∈ {T,S,M,W,L,X}`; `risk ∈ {none, R}`;
  `phase ∈ {idle, intake, plan, execute, verify, awaiting_external, close, done, blocked}`; `routing.mode ∈ {inline, single, parallel}`;
  `steps[].status ∈ {pending, running, reported, verifying, done, failed, blocked, awaiting_external}`; `steps[].from ∈ {null, failed, clean}`;
  `plan_author ∈ {null, architect, forge-planner}`.
- Bounds: `queue` ≤ 10 (the rest in `.forge/queue.jsonl`), `history` = last 5 (every row in `.forge/history.jsonl`), `evidence` = newest 10
  (`evidence_count` holds the total). There is no spend field: spend lives in the ledger.
- Invariants: `routing.mode == inline ⇔ steps == []`; M and W have exactly one step once planned, L ≥ 3; a `running` step has
  `started_by`; a `done` step has `commit` and `verdict` (`step-done --no-verifier` exists for classes T and S only, which never have
  steps, so in practice every done step has a verdict; inline verification is `task.inline_verdict`, below); `risk == R ⇔
  signals.risk_hits ≠ ∅` unless the justification records `--force-risk` or `--accept-risk-none`.
- Inline verdict: `task.inline_verdict = {verdict, file, verifier_model, at, attempt, tags}` is written by
  `forge-status step-verdict <id> main --verdict .forge/tasks/<id>/verdict-main.json` (the verifier's SubagentStop gate runs it).
  PASS → `phase: done`, `next_action: Run /forge-close`; FAIL/UNKNOWN → `phase: execute` with the fix-and-re-verify action. `close`
  requires a PASS for class X always and for class S when a changed path matches `binding.test_globs`; a FAIL/UNKNOWN on file
  refuses every S/X close except `--partial`. `get digest`/`get resume` show it as `verdict (main): …`.
- Retry bookkeeping: every `step-start` sets `attempts += 1` and resets `verify_attempts` to 0 (the verifier cap of 2 is per
  attempt); `recover` keeps `attempts`, sets the step `pending` and stamps `recovered_at`, after which `step-start --from clean` is
  accepted (a no-op restore when the tree is already at base). `step-start` accepts `pending`, and `failed` or `blocked` with
  `--from failed|clean`; it is refused in phase `intake`.
- Idle form (what the installer writes; `.forge/templates/STATUS.json`): `"task": null, "queue": [], "history": []`. A queue entry
  may carry no `id` (the stack-unknown installer's "stack discovery" hint); ids are allocated over `tasks/`, `archive/`, history and
  every queued id, so a queued id never collides with a newly opened task.
- Read it without a model: `.forge/bin/forge-status get summary` · `get digest` · `get resume` · `get next_action` · `get task.phase`
  (any dotted path). Add `--lenient` to never exit non-zero.

Transitions (each refusal is exit 3 with one line on stderr; full table in design §5.1): `open` (alias `new`, which never queues) →
`plan` → `step-start` → (`step-bind`) → `step-report` → `step-verifying` → `step-verdict` → `step-done | step-fail | step-external` →
`close`; plus `attest`, `recover`, `evidence`, `scope add <id> <path> --why "…" [--ruling]`, `block --on "…"`/`unblock`,
`stale`/`fresh`, `validate [--restamp]`, `gate-block`. `open --files` paths must exist (new files go in `--creates`); a path that
escapes the repository is refused. Every subcommand except `get` prints one line: `<task> <phase> <step?> <status?> | next: …`.
Run `.forge/bin/forge-status --help` for the flags.

## binding.json — the thin per-project binding (`.forge/schemas/binding.json`)

Project-owned and policy-locked (edited by hand or by the installer, never by a model). Required keys: `schema_version, project, stack,
verify, test_globs, test_pattern, protected_paths, risk_paths, important_paths, mechanic_denied_paths, risk_words,
irreversible_commands, git, budgets, routing, clear_policy, auto_resume, driver`; optional `forge_pin, bootstrap, smoke, format, notes,
agent_paths` (1.0.1).

```json
{
  "schema_version": 2, "forge_pin": "1.0.1", "project": "ruggedroute-dataops", "stack": "python",
  "bootstrap": "python3 -m pip install -q pytest shapely",
  "verify": [
    { "name": "lib-unit",    "cmd": "cd lib && python3 -m unittest -v", "when": "always" },
    { "name": "layer-tests", "cmd": "pytest layers/{layer}/tests -q", "when": "paths:layers/{layer}/**", "exists": "layers/{layer}/tests", "vars": { "layer": "from-path" } },
    { "name": "worker",      "cmd": "cd worker-tiles && npx wrangler deploy --dry-run", "when": "paths:worker-tiles/**", "todo": "package.json has no test script" }
  ],
  "smoke": "python3 qa/golden_counts.py --help", "format": null,
  "test_globs": ["lib/test_*.py", "layers/*/tests/*.py", "worker-tiles/**/*.test.js"], "test_pattern": "^\\s*def test_",
  "protected_paths": [".github/workflows/*.yml", "worker-tiles/wrangler.toml", "worker-tiles/src/**"],
  "risk_paths": ["**/*upload*", "**/*alias*", "**/*kv*", "layers/parcels/**"],
  "important_paths": ["layers/mvum/**", "layers/lands/**"],
  "mechanic_denied_paths": ["lib/route_common.py", "lib/normalize_*.py", "layers/*/layer.json", "layers/mvum/**", "layers/lands/**"],
  "agent_paths": [],
  "risk_words": [ { "word": "owner", "not": ["ownership"] }, { "word": "R2" }, "license" ],
  "irreversible_commands": ["wrangler *", "npx wrangler *", "gh workflow run *", "gh pr merge *", "git push *"],
  "git": { "branch_per_task": false, "commit_prefix": "forge", "worktree_isolation": false },
  "budgets": { "T": 1, "S": 3, "M": 10, "M_chain": 12, "W": 25, "L_unit": 2, "X": 30, "risk_multiplier": 1.5 },
  "routing": { "architect_effort": "medium", "m_builder": "opus-medium", "overrides": [], "measured": {} },
  "clear_policy": "phase", "auto_resume": true, "driver": { "max_turns": 120, "max_phases": 12 },
  "notes": ["Versioned uploads + KV alias flip; never overwrite a PMTiles object in place."]
}
```

- `verify[].when`: `always` or `paths:<glob>` matched against the step's changed set. `{layer}` is substituted from the first path
  component after `layers/` of a matching changed path (`vars: {"layer": "from-path"}`). A missing `exists` path → the command is
  recorded `skipped`, not failed. `todo` entries print as WARN in `/forge-doctor`.
- Globs: repo-relative; `**/` = any directories, `**` = anything, `*` = within one path segment, `?` = one character; a directory
  glob such as `layers/mvum/**` matches every file below it.
- `agent_paths` (1.0.1; optional, default `[]`): repo-relative globs a **project agent** — any subagent whose `agent_type` is not a
  `forge-*` role, such as a consumer's QA tester — may write through Edit/Write and shell writes in any task state, no task open
  included. The policy lock, `protected_paths` and the outside-repository check still deny; Forge roles and the main session ignore
  the key; `forge-status close` never counts files under it as out of scope. Migration `0001` adds `"agent_paths": []` to an
  existing binding on upgrade; `/forge-doctor` FAILs a malformed value and WARNs when a glob reaches `.forge/`, `.claude/` or `**`.
- `risk_words`: a string or `{word, not: [...]}`. Words of ≥ 4 characters match case-insensitively on word boundaries, shorter ones
  case-sensitively; a `not` phrase present in the title cancels the hit.
- `irreversible_commands`: glob-like patterns matched against the whole command and each `&&`/`;`/`|` segment (`*` matches anything,
  spaces included).
- `clear_policy ∈ {phase, task, never}`; `routing.m_builder ∈ {opus-medium, fable-low}`; `routing.architect_effort ∈ {low, medium, high}`;
  `routing.overrides[]` = `{name, paths[], builder {agent, model, effort}, min_verifier}`; `git.worktree_isolation` may be set to
  `true` only after `.forge/bin/forge-doctor --worktree` passed.
- Invariants: `verify` non-empty unless `stack == "unknown"`; every `verify[].cmd` prefix appears in `settings.permissions.allow`
  (the installer adds it).

## Plan — `.forge/tasks/<id>/plan.md` (`.forge/schemas/plan.json`)

Templates: `.forge/templates/plan.md` (M/W/L) and `.forge/templates/plan-inline.md` (S/X). The first ```json block is **plan-meta**:

```json
{
  "schema": "forge/plan/2", "task": "T-0007", "class": "M", "risk": "none", "chain": false,
  "routing": { "mode": "single",
    "builder":  { "agent": "forge-builder",  "model": "opus", "effort": "medium" },
    "verifier": { "agent": "forge-verifier", "model": "opus", "effort": "medium" },
    "justification": "3 declared files, 2 dirs, one dependent chain, tests added first → M-small; chain=false → opus/medium" },
  "steps": [ { "id": "01", "title": "golden-bbox QA for nfs_trails", "brief": "brief-01.md", "agent": "forge-builder", "model": "opus",
               "effort": "medium", "mechanical": false, "red_ok_until": null, "max_tool_calls": 60 } ],
  "dod": [
    { "id": "DoD-1", "criterion": "WHEN `pytest layers/nfs_trails/tests -q` runs THE SUITE SHALL exit 0 with at least 1 new golden-count test", "check": "pytest layers/nfs_trails/tests -q" },
    { "id": "DoD-4", "criterion": "WHEN the quarterly workflow runs THE RUN SHALL succeed", "check": "external",
      "external": { "what": "GitHub Actions run of quarterly-rec_pois.yml succeeds", "how": "gh workflow run quarterly-rec_pois.yml && gh run watch" } }
  ],
  "rollback": "git revert <step commit>; no external state is touched",
  "test_baseline": { "files": 11, "tests": 212, "recorded_at": "2026-10-11T18:12:00Z" },
  "needs_clarification": []
}
```

- Required headings (level 2): **M** → Steps · Validation Criteria · Routing · Rollback. **W, L** → those four plus Objective · Current
  State · Target State · Tech Stack Context · File Manifest · Dependency Order · Anti-Patterns — DO NOT · Escalation Points.
  **S, X (inline)** → Validation Criteria · Rollback (the template adds *Hypothesis / Objective*).
- Rules: `mode: inline ⇔ steps == []` (S/X only) and inline plans carry `allowed_paths` (the declared set); M and W exactly one step;
  L ≥ 3 steps with pairwise-disjoint brief `allowed_paths`; every step has an existing brief whose `step` matches; `max_tool_calls`
  per step; `red_ok_until` names a later step; `dod` ids match `^DoD-[0-9]+$`, ≥ 1; risk R ⇒ `rollback` holds a concrete command;
  `needs_clarification ≠ []` ⇒ the import sets `phase: intake` and `next_action: "ask the user: …"` (no builder or verifier is
  dispatched in intake). A corrected plan may be imported again in `intake`, or in `execute` while every step is still `pending`
  with `attempts == 0` (the steps are replaced).
- The baseline comes from `.forge/bin/forge-check <id> plan --baseline`; when plan-meta still holds the template value
  (`recorded_at` 1970), `forge-status plan` records it at import and writes it back into `plan.md` (journaled).
- `check: external` criteria are graded only from a human `attest` record.

## Brief — `.forge/tasks/<id>/brief-NN.md` (`.forge/schemas/brief.json`)

Template: `.forge/templates/brief.md`. Self-contained: a worker sees nothing else. First ```json block = **brief-meta**:

```json
{
  "schema": "forge/brief/2", "task": "T-0007", "step": "01",
  "owner_agent": "forge-builder", "model": "opus", "effort": "medium",
  "allowed_paths": ["qa/golden_counts.py", "layers/nfs_trails/layer.json", "layers/nfs_trails/tests/**"],
  "may_edit_tests": false, "tdd": true,
  "checks": ["pytest layers/nfs_trails/tests -q", "cd lib && python3 -m unittest -v", "python3 qa/golden_counts.py --layer nfs_trails --fixture"],
  "expected_fail_first": ["pytest layers/nfs_trails/tests -q"],
  "dod": ["DoD-1", "DoD-2", "DoD-3"],
  "risk": "none", "red_ok": false, "max_tool_calls": 60,
  "bootstrap": "python3 -m pip install -q pytest shapely"
}
```

Headings: Goal · Context the worker needs · Definition of done · Out of scope / do not touch · Known failed approaches · Output contract.
Invariants: `owner_agent ∈ {forge-builder, forge-builder-wide, forge-builder-s, forge-mechanic}`; `model` is an alias;
`allowed_paths` non-empty (no path escaping the repository); `tdd ⇒ expected_fail_first` non-empty; `expected_fail_first ⊆ checks`;
`max_tool_calls ≥ 5`. `may_edit_tests: true` is needed whenever a DoD adds tests to an existing `test_globs` file (the fence refuses
every edit to an existing test file otherwise); the template defaults to `true` and its comment says when to set `false`. Readers: the fence (`allowed_paths`,
`may_edit_tests`, `owner_agent`, `max_tool_calls`), the handoff gate (`checks`, `expected_fail_first`, `tdd`, `dod`, `red_ok`),
`forge-check` (`checks`).

## Handoff — worker final message and task-level `handoff.md` (`.forge/schemas/handoff.json`)

Templates: `.forge/templates/handoff.md` (M/W/L task close) and `.forge/templates/handoff-short.md` (S/X task close). Workers write
the same shape as their final message; the gate persists it as `report-NN.md` + `report-NN.json`.

- Mandatory `## ` headings: **Where things stand · Done, with evidence · Remaining · Gotchas / do not touch** (write `none` rather than
  omit). Short form (S/X task handoffs): the first three. Optional: Goal & scope · Decisions & rationale · Failed approaches — do not
  repeat · Files touched · Verification commands + expected output · Open questions · Bootstrap.
- JSON block (`step` is `"task"` in a task-level `handoff.md`):

```json
{
  "schema": "forge/handoff/2", "task": "T-0007", "step": "01", "status": "DONE",
  "files_changed": ["qa/golden_counts.py", "layers/nfs_trails/layer.json", "layers/nfs_trails/tests/test_golden.py"],
  "checks_run": [
    { "cmd": "pytest layers/nfs_trails/tests -q", "exit": 1, "expected_fail": true },
    { "cmd": "pytest layers/nfs_trails/tests -q", "exit": 0 },
    { "cmd": "cd lib && python3 -m unittest -v", "exit": 0 }
  ],
  "not_verified": ["behaviour with an empty fixture directory"],
  "failed_approaches": ["Querying the live ArcGIS service for counts: throttled after 3 regions; switched to the bulk fixture"],
  "next_action": "none for this step",
  "commit": null
}
```

- `status ∈ {DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED, UNVERIFIED}`; `UNVERIFIED` is stamped only by the gate after two blocks.
- Gate rules (`.forge/bin/forge-gate --handoff <task> <step> --from-file <f>`, identical in the SubagentStop hook):
  `files_changed ⊆ allowed_paths`; every `kind: source` edit row of this agent ⊆ `files_changed`; every path in
  `git status --porcelain --untracked-files=all -- <allowed_paths>` ⊆ `files_changed`; for `DONE|DONE_WITH_CONCERNS` every brief
  `checks[]` cmd has a `checks/<step>-*-<agent_id>.json` record at exit 0 (any exit when `red_ok`) newer than the agent's last source
  edit; `tdd` ⇒ each `expected_fail_first[]` cmd has a non-zero record (by any agent: a retry inherits an earlier attempt's red run)
  earlier than this agent's zero record. `BLOCKED|NEEDS_CONTEXT` need no records (the step becomes `blocked`; `step-start --from
  failed` appends the report's `next_action` to the brief). Pre-validation drafts under `.forge/tasks/<id>/drafts/` never count as
  tree changes and are never committed.
  Task-level handoffs (`--task-level`) need the headings and a valid JSON block with `step == "task"` only.
- On allow the hook commits the unit and fills `commit` in `report-NN.json`.
- Pre-validation (workers and the verifier): write the draft to `.forge/tasks/<id>/drafts/<agent_id>-handoff.md` (or `-verdict.md`)
  with the Write tool — the one `.forge/` path a subagent may write — and run `.forge/bin/forge-gate --handoff|--verdict <id> <step>
  --from-file <draft> --agent <agent_id>`.

## Verdict — verifier final message (`.forge/schemas/verdict.json`)

Template: `.forge/templates/verdict.md`. Headings: Verdict · Criteria · Scope check · Blocking findings · Deferred findings ·
Confidence note. JSON block (`step` is `"main"` and `range` may be `"worktree"` for inline S/X tasks):

```json
{
  "schema": "forge/verdict/2", "task": "T-0007", "step": "01", "range": "3e1f9c2..a91b0e4", "verdict": "PASS",
  "criteria": [
    { "id": "DoD-1", "result": "PASS", "cmd": "pytest layers/nfs_trails/tests -q", "exit": 0 },
    { "id": "DoD-2", "result": "PASS", "cmd": "cd lib && python3 -m unittest -v", "exit": 0 }
  ],
  "scope_check": "PASS", "ratchet": "PASS",
  "blocking_findings": [], "deferred_findings": ["no negative-longitude fixture"], "tags": []
}
```

Gate rules: every brief DoD id exactly once with `result ∈ {PASS, FAIL, UNKNOWN}`, `cmd` and a numeric `exit`; `PASS` ⇒ all criteria
PASS ∧ `scope_check == PASS` ∧ `ratchet == PASS` ∧ no blocking findings; every cited cmd has a `checks/<step>-*-<verifier agent_id>.json`
record (`forge-check <id> <step>` runs the step's plan-meta DoD check commands as well as `verify[]` and brief `checks[]`, so the
verifier's own run records every criterion), except `check: external` criteria, which need a `checks/<step>-*-human.json` attest record (else `UNKNOWN`);
`tags ⊆ {skipped-file, no-check-run, not-double-checked, wrong-approach, scope-creep, test-weakened, env-cannot-run}`; UNKNOWN on a
required criterion ⇒ FAIL for risk R tasks; after two blocks the hook allows with the verdict rewritten to `UNKNOWN`.

## Evidence log, check records, attestations

`.forge/tasks/<id>/evidence.jsonl` — appended by `PostToolUse` / `PostToolUseFailure`:

```json
{"ts":1760208002,"agent_id":"agent_7f3a","agent_type":"forge-builder","event":"bash","ok":true,"exit":0,"cmd":".forge/bin/forge-check T-0007 01"}
{"ts":1760207990,"agent_id":"agent_7f3a","agent_type":"forge-builder","event":"edit","kind":"source","file":"qa/golden_counts.py"}
{"ts":1760207980,"agent_id":"main","agent_type":"main","event":"edit","kind":"meta","file":".forge/tasks/T-0007/plan.md"}
```

`kind: meta` for `.forge/**`, `.claude/agent-memory/**`, `CLAUDE.md`, `.gitignore`; everything else `source`. A Bash `cmd` (and
`error_head`, and a check record's `tail`) is stored with credential shapes redacted (`token=…`, `Authorization: Bearer …`, `AKIA…`,
`ghp_…`, `sk-…`), and the stored `cmd` is capped at 300 characters, because evidence is committed at close. Bash `exit` is best-effort
([U]); **exact exit codes come from check records**, `.forge/tasks/<id>/checks/<step>-<epoch>-<agent_id|main|human|unknown>.json`,
written by `.forge/bin/forge-check`:

```json
{"ts":1760208002,"agent_id":"agent_7f3a","session_id":"7f2c…","task":"T-0007","step":"01","expect_fail":false,
 "results":[{"name":"layer-tests","cmd":"pytest layers/nfs_trails/tests -q","exit":0,"dur_s":4.1,"tail":"12 passed in 4.1s"},
            {"name":"worker","cmd":"cd worker-tiles && npx wrangler deploy --dry-run","status":"skipped","why":"when: paths:worker-tiles/** did not match"}],
 "ratchet":{"baseline_tests":212,"now_tests":213,"deleted_test_files":[],"status":"PASS"},
 "ok":true}
```

`ok` = every non-skipped result exited 0. `forge-check` writes `agent_id: "unknown"`; the `PostToolUse(Bash)` hook re-stamps the newest
such record (≤ 300 s old, same task/step) with the caller's `agent_id` (or `main`). Human attestation
(`.forge/bin/forge-status attest <id> <step> DoD-n --by <name> --evidence <url|path> [--exit N]`):

```json
{"ts":1760300000,"agent_id":"human","source":"human","by":"riggs","criterion":"DoD-4","evidence":"https://github.com/…/actions/runs/123","exit":0,"task":"T-0012","step":"01"}
```

## Ledger — `.forge/ledger.jsonl` (`.forge/schemas/ledger.json`)

Append-only, committed; every row has `ts` and `event ∈ {open, dispatch, attempt, verdict, step_done, step_fail, close, phase,
gate_block, builtin, denied_tools, recover, scope_add, ruling}`.

```json
{"ts":"2026-10-11T18:42:10Z","task":"T-0007","step":"01","event":"dispatch","class":"M","agent":"forge-builder","model":"opus","effort":"medium","attempt":1,"escalated_from":null}
{"ts":"2026-10-11T18:58:00Z","task":"T-0007","step":"01","event":"attempt","status":"DONE","gate_blocks":0,"commit":"a91b0e4"}
{"ts":"2026-10-11T19:01:00Z","task":"T-0007","step":"01","event":"verdict","verdict":"PASS","verifier_model":"opus","tags":[],"gate_blocks":0}
{"ts":"2026-10-11T19:05:00Z","task":"T-0007","event":"close","class":"M","outcome":"done","cost_usd":null,"cost_source":"unknown","context_carried":false,"expected_premium":false,"escalations":0}
{"ts":"2026-10-12T02:10:00Z","task":"T-0009","event":"phase","phase":"execute","cost_usd":3.12,"cost_source":"measured","cache_read_share":0.71,"session_id":"c0ffee…"}
```

`cost_source`: `measured` only when `forge-run` or `forge-bench` wrote the row from `total_cost_usd`; `operator` when a human passed
`close --cost` after reading `/usage`; `unknown` otherwise. `/forge-gc` thresholds use measured rows only.
`context_carried: true` when the operator skipped the clear.

## Lessons, decisions, rulings, history, journal

- `.forge/lessons/<slug>.md` — one lesson per file; line 1 is the bold `type: feedback|project|reference` tag and the one-line summary
  (`.forge/templates/lesson.md`); `.forge/lessons/INDEX.md` one line per lesson, ≤ 200 lines; the first 40 lines are injected at start.
- `.forge/decisions/NNNN-<slug>.md` — Nygard ADR (`.forge/templates/adr.md`); numbers never reused; superseded, never deleted.
- `.forge/tasks/<id>/ruling.md` — Decision · Why · Cost if wrong · Evidence considered (`.forge/templates/ruling.md`).
- `.forge/tasks/<id>/drafts/<agent_id>-*.md` — pre-validation drafts written by subagents; excluded from step commits.
- `.forge/history.jsonl`, `.forge/queue.jsonl` — the unbounded tails of STATUS `history[]` / `queue[]`.
- `.forge/tasks/<id>/journal.md` — append-only hook log (dispatches, gate blocks with reasons, fence denials, stop blocks, recoveries,
  compactions, StopFailure, config-change blocks, builtin spawns). Without an open task: `.forge/.runtime/journal.log`.
- `.forge/CHANGELOG.md` — one line per closed task, appended by `forge-status close`.

## Runtime markers — `.forge/.runtime/` (gitignored)

`session-id` · `hooks-alive` (`{session_id, ts, source}`) · `dirty-main` · `dirty-worker` · `chat-turn` · `stop-blocks` (int) ·
`last-block.sha` · `status.sha` · `stale-status` · `denials` (`{rule: count}`) · `driver` · `auto-resumed-<task>-<phase>` ·
`dispatched-<task>-<step>` (spawn guard; removed when the worker binds) · `last-session.json` · `agents/<agent_id>.json`
(`{agent_id, agent_type, started_ts, session_id, task?, step?, brief?, bound_at?, verify_step?, tool_calls?}`; `tool_calls` is the
hook-owned tool-budget counter) · `gate-disabled-<name>` · `phase-costs.jsonl` · `driver-probe.json` (cached `forge-doctor --driver`
result) · `observed.json` (probe observations) · `journal.log`. SessionStart recreates the directory when it is missing.
