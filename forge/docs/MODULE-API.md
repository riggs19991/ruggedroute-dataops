# Forge internal module API (build contract)

This document is the contract between the Forge's Python modules. Every module under
`payload/.forge/bin/forgelib/` and every CLI under `payload/.forge/bin/` is written against it.
Design authority: `forge/docs/design/design-v2.md` (§3 lifecycle, §5 schemas, §7 gates, §13.3 scripts).
When this file and the design disagree on a data shape, this file wins (it is what the code implements);
when it is silent, the design decides.

Runtime: Python 3.9+, standard library only. Scripts are executable files with
`#!/usr/bin/env python3`, invoked as `.forge/bin/<tool>` from the repository root. Each script begins with

```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forgelib import common
```

Exit codes (common.py): `0` ok · `1` defects / failing checks · `2` usage · `3` refused (precondition) ·
`4` STATUS invalid on disk or hooks not alive · `6` headless permission denial (forge-run).
Library code raises `common.ForgeError(message, code)`; CLIs catch it, print the message on stderr, exit `code`.

All paths handled by library code are **repo-relative POSIX** (`common.Paths.rel`). Timestamps: ISO-8601
`*_at` strings for humans and integer epoch `*_ts` for comparisons (`common.now_iso()`, `common.now_ts()`).

---

## 1. `forgelib.common` (written; do not change signatures)

See the module docstrings. Key items used by every other module:

| Item | Meaning |
|---|---|
| `Paths(root=None)` | `.root`, `.forge`, `.status`, `.binding`, `.ledger`, `.history`, `.queue`, `.changelog`, `.tasks`, `.lessons`, `.lessons_index`, `.decisions`, `.archive`, `.incidents`, `.runtime`, `.schemas`, `.templates`, `.routing`, `.settings`, `.agent_memory`; `task(id)`, `task_file(id, name)`, `checks_dir(id)`, `evidence(id)`, `journal_file(id|None)`, `base_file(id, step)`, `rt(name)` (runtime marker path), `agent_record(agent_id)`, `rel(path)` |
| `forge_root()` | main checkout owning `.forge/` (worktree-safe) |
| `read_json / write_json_atomic / append_jsonl / read_jsonl / read_text / write_text_atomic / sha256_file / touch / rm / exists` | I/O |
| `load_status / load_binding / load_routing / current_task / find_step` | loaders |
| `session_id(paths)` | from `.runtime/session-id`, else `"cli"` |
| `journal(paths, task_id, msg)` · `ledger(paths, row)` · `evidence_append(paths, task_id, row)` · `evidence_rows(paths, task_id, agent_id=None, event=None)` · `edit_kind(paths, path)` | logs |
| `glob_match(path, glob)` · `any_glob(path, globs)` · `alias_model(s)` · `agent_role(agent_type)` · `tier_gte(a,b)` · `next_tier(model, effort)` | matching |
| `json_block(text)` · `headings(text, level=2)` · `section(text, heading)` · `render_template(text, mapping)` · `truncate(text, n)` | markdown |
| `run(cmd, cwd, timeout)` → `(exit, output)` · `git(args, cwd)` · `git_head(cwd)` · `git_porcelain(cwd, pathspecs)` · `git_diff_names(cwd, base, head)` · `git_is_ancestor(cwd, a, b)` | processes |
| `read_stdin_json()` · `emit(obj)` · `eprint(...)` | hook I/O |
| `word_hits(title, risk_words)` · `next_task_id(paths)` · `dirs_of(paths)` · `unique(seq)` | misc |
| constants | `CLASSES, RISKS, PHASES, MODES, STEP_STATUSES, HANDOFF_STATUSES, VERDICTS, VERDICT_TAGS, EFFORTS, MODELS, TIER_ORDER, EFFORT_ORDER, HANDOFF_MANDATORY_HEADINGS, HANDOFF_SHORT_HEADINGS, VERDICT_HEADINGS, PLAN_HEADINGS_M, PLAN_HEADINGS_FULL, PLAN_HEADINGS_INLINE, SCHEMA_*, WORKER_ROLES, READONLY_ROLES, ALL_ROLES, DEFAULT_AGENT_ROUTING, META_PREFIXES, ARCHITECT_META_ALLOW, POLICY_LOCK_PREFIXES, POLICY_LOCK_FILES, MAX_ADDITIONAL_CONTEXT, MAX_DIGEST, STOP_SOFT_CAP, GATE_BLOCK_CAP, TOOL_BUDGET_DEFAULT, WIDE_TOOL_BUDGET_DEFAULT` |

---

## 2. Data shapes

### 2.1 `.forge/STATUS.json` (schema_version 2) — written only by `forgelib.status`

```json
{
  "schema_version": 2, "forge_version": "1.0.0", "project": "<name>",
  "updated_at": "...Z", "updated_ts": 0, "updated_by": {"session_id": "...", "cmd": "..."},
  "context_state": "fresh|stale",
  "task": null | {
    "id": "T-0007", "title": "...", "class": "T|S|M|W|L|X", "risk": "none|R", "size_source": "declared",
    "files": ["..."], "creates": ["..."],
    "signals": {"files": 3, "dirs": 2, "importers": 0, "recent_cochanges": [], "tests_present": true, "risk_hits": [], "important_hits": []},
    "class_justification": "...",
    "phase": "idle|intake|plan|execute|verify|awaiting_external|close|done|blocked",
    "plan": null | ".forge/tasks/T-0007/plan.md", "plan_author": null | "architect|forge-planner",
    "branch": null, "scope": ["..."],
    "routing": {"mode": "inline|single|parallel", "builder": null | {"agent","model","effort"}, "verifier": null | {"agent","model","effort"}, "justification": "..."},
    "steps": [ {"id": "01", "title": "...", "agent": "forge-builder", "model": "opus", "effort": "medium",
                "status": "pending|running|reported|verifying|done|failed|blocked|awaiting_external",
                "attempts": 0, "from": null|"failed"|"clean", "verify_attempts": 0,
                "started_at": null, "started_ts": null, "started_by": null, "agent_id": null,
                "base": null, "commit": null, "brief": ".forge/tasks/T-0007/brief-01.md",
                "report": null, "verdict": null, "red_ok_until": null, "allowed_paths": ["..."], "mechanical": false, "max_tool_calls": 60} ],
    "escalation": {"step": null, "round": 0},
    "next_action": "one imperative sentence", "resume_hint": "...",
    "evidence_count": 0, "evidence": [ {"claim","command","exit","when","from"} ],
    "blocked_on": null, "external": null | {"step": "01", "criteria": ["DoD-4"], "needs": "..."},
    "budget": {"cap_usd": 10.0},
    "opened_at": "...Z", "base": "<git sha at open or null>"
  },
  "queue": [ {"id": "T-0008", "title": "...", "class_hint": "S"} ],
  "history": [ {"id","title","class","outcome","cost_usd","cost_source","handoff","closed_at"} ]
}
```
Bounds: `queue` ≤ 10 (rest in `queue.jsonl`), `history` = last 5 (all rows in `history.jsonl`), `evidence` = newest 10.
Model fields hold **aliases** (`haiku|sonnet|opus|fable`), always normalised through `common.alias_model`.

### 2.2 `.forge/binding.json` (project-owned)

Keys used by code: `project, stack, bootstrap, verify[] {name, cmd, when: "always"|"paths:<glob>", exists?, vars?, todo?}, smoke, format, test_globs[], test_pattern, protected_paths[], risk_paths[], important_paths[], mechanic_denied_paths[], risk_words[] ({word, not?}|str), irreversible_commands[] (glob-like patterns matched against the command string; `*` = any chars), git {branch_per_task, commit_prefix, worktree_isolation}, budgets {T,S,M,M_chain,W,L_unit,X,risk_multiplier}, routing {architect_effort, m_builder: "opus-medium"|"fable-low", overrides[] {name, paths[], builder{agent,model,effort}, min_verifier}, measured{}}, clear_policy: "phase"|"task"|"never", auto_resume: bool, driver {max_turns, max_phases}, notes[]`.
`{layer}` in a verify `cmd`/`exists` is substituted from the first path component after `layers/` of a matching changed path (`vars: {"layer": "from-path"}`).

### 2.3 Plan file `.forge/tasks/<id>/plan.md`

First fenced ```json block = **plan-meta**:
```json
{"schema": "forge/plan/2", "task": "T-0007", "class": "M", "risk": "none", "chain": false,
 "routing": {"mode": "single|inline|parallel", "builder": {...}|null, "verifier": {...}|null, "justification": "..."},
 "steps": [ {"id": "01", "title": "...", "brief": "brief-01.md", "agent": "forge-builder", "model": "opus", "effort": "medium",
             "mechanical": false, "red_ok_until": null, "max_tool_calls": 60} ],
 "dod": [ {"id": "DoD-1", "criterion": "WHEN ... THE SYSTEM SHALL ...", "check": "<command>" | "external", "external": {"what","how"}?} ],
 "rollback": "...", "test_baseline": {"files": 0, "tests": 0, "recorded_at": "...Z"}, "needs_clarification": [],
 "allowed_paths": ["..."]   // inline plans (S/X) only: the declared set
}
```
Headings required (level 2): class M → `PLAN_HEADINGS_M`; W/L → `PLAN_HEADINGS_FULL`; S/X inline → `PLAN_HEADINGS_INLINE`.
`steps` must be `[]` for inline, exactly 1 for M and W, ≥ 3 for L (parallel needs pairwise-disjoint `allowed_paths` read from each brief).

### 2.4 Brief `.forge/tasks/<id>/brief-NN.md`

First fenced ```json block = **brief-meta**:
```json
{"schema": "forge/brief/2", "task": "T-0007", "step": "01", "owner_agent": "forge-builder", "model": "opus", "effort": "medium",
 "allowed_paths": ["..."], "may_edit_tests": false, "tdd": true, "checks": ["<cmd>", ...], "expected_fail_first": ["<cmd>"],
 "dod": ["DoD-1", "DoD-2"], "risk": "none", "red_ok": false, "max_tool_calls": 60, "bootstrap": "..."}
```
Required headings: `Goal`, `Context the worker needs`, `Definition of done`, `Out of scope / do not touch`, `Known failed approaches`, `Output contract`.

### 2.5 HANDOFF (worker final message; persisted as `report-NN.md` + `report-NN.json`; task-level `handoff.md`)

Mandatory `## ` headings: `HANDOFF_MANDATORY_HEADINGS` (short form for S/X task handoffs: `HANDOFF_SHORT_HEADINGS`). JSON block:
```json
{"schema": "forge/handoff/2", "task": "T-0007", "step": "01", "status": "DONE|DONE_WITH_CONCERNS|NEEDS_CONTEXT|BLOCKED|UNVERIFIED",
 "files_changed": ["..."], "checks_run": [{"cmd": "...", "exit": 0, "expected_fail": false}], "not_verified": [], "failed_approaches": [],
 "next_action": "...", "commit": null}
```
For a task-level `handoff.md`, `step` is `"task"`.

### 2.6 VERDICT (verifier final message; persisted as `verdict-NN.md` + `verdict-NN.json`)

Headings: `VERDICT_HEADINGS`. JSON block:
```json
{"schema": "forge/verdict/2", "task": "T-0007", "step": "01", "range": "<base>..<commit>", "verdict": "PASS|FAIL|UNKNOWN",
 "criteria": [{"id": "DoD-1", "result": "PASS|FAIL|UNKNOWN", "cmd": "...", "exit": 0}],
 "scope_check": "PASS|FAIL", "ratchet": "PASS|FAIL|UNKNOWN", "blocking_findings": ["..."], "deferred_findings": ["..."], "tags": []}
```
For inline tasks (S/X verifier on the working tree) `step` is `"main"` and `range` may be `"worktree"`.

### 2.7 Check record `.forge/tasks/<id>/checks/<step>-<epoch>-<agent_id|main|human|unknown>.json`

```json
{"ts": 0, "agent_id": "unknown|main|<agent_id>|human", "session_id": "...", "task": "T-0007", "step": "01|main|plan",
 "expect_fail": false,
 "results": [{"name": "lib-unit", "cmd": "...", "exit": 0, "dur_s": 1.2, "tail": "...last 15 lines..."} | {"name","cmd","status":"skipped","why"}],
 "ratchet": {"baseline_tests": 212, "now_tests": 213, "deleted_test_files": [], "status": "PASS|FAIL|UNKNOWN"} | null,
 "ok": true}
```
`ok` = every non-skipped result exited 0 (regardless of `expect_fail`). A human attestation record is
`{"ts","agent_id":"human","source":"human","by","criterion":"DoD-4","evidence":"<url|path>","exit":0,"task","step"}`.
The file is first written with `agent_id: "unknown"` by `forge-check`; the `PostToolUse(Bash)` hook renames/rewrites the
newest such record (≤300 s old, same task/step) with the real `agent_id` (or `main`). `forge-check --agent <id>` sets it directly.

### 2.8 Evidence row `.forge/tasks/<id>/evidence.jsonl`

`{"ts", "agent_id": "main|<id>", "agent_type": "main|<role>", "event": "edit|bash", "kind": "source|meta" (edit), "file" (edit), "ok": bool (bash), "exit": int|null (bash), "cmd" (bash), "error_head"?}`

### 2.9 Ledger rows `.forge/ledger.jsonl` (append-only; `common.ledger` adds `ts`)

`event ∈ open | dispatch | attempt | verdict | step_done | step_fail | close | phase | gate_block | builtin | denied_tools | recover | scope_add | ruling`.
Fields per §5.8 of the design: `task, step?, class, agent, model, effort, attempt, escalated_from, status, gate_blocks, commit, verdict, verifier_model, tags, outcome, cost_usd, cost_source ("measured"|"operator"|"unknown"), context_carried, expected_premium, escalations, phase, cache_read_share, session_id`.

### 2.10 Runtime markers `.forge/.runtime/` (gitignored)

`session-id` (text) · `hooks-alive` (json `{session_id, ts, source}`) · `dirty-main` · `dirty-worker` · `chat-turn` · `stop-blocks` (int) · `last-block.sha` · `status.sha` · `stale-status` · `denials` (json `{rule: count}`) · `driver` · `auto-resumed-<task>-<phase>` · `last-session.json` · `agents/<agent_id>.json` (`{agent_id, agent_type, started_ts, session_id, task?, step?, brief?, bound_at?}`) · `gate-disabled-<name>` · `phase-costs.jsonl` · `journal.log`.

### 2.11 Agent record binding rule

A worker is **bound** to a step when `agents/<agent_id>.json` carries `task`, `step`, `brief`. Binding happens on the first
`Read` (or `Bash` `cat`/`sed -n`/`head` of) a brief path whose step is `running`, has `agent_id == null`, and whose
`owner_agent == role`. Binding runs `status.step_bind(task, step, agent_id)`.

---

## 3. `forgelib.status` — the state machine (`forge-status` CLI)

```python
class Status:
    def __init__(self, paths: common.Paths): ...
    # loading / saving
    def load(self) -> dict                      # raises ForgeError(EXIT_INVALID) if missing/invalid
    def save(self, st: dict, cmd: str, stamp: bool = True, clear_dirty: str = "main") -> None
        # validates against schema assertions, atomic write, updated_at/ts/updated_by, writes .runtime/status.sha,
        # removes .runtime/dirty-main; clear_dirty="worker" also removes dirty-worker; "none" removes nothing
    def validate(self, st: dict) -> list[str]   # schema assertion defects (empty = valid)
    # transitions (each returns the new STATUS dict; each raises ForgeError(EXIT_REFUSED) with ONE line on refusal)
    def open(self, title, cls, risk, files, creates=(), why="", queue=False, force_risk=False, accept_risk_none=None) -> dict
    def signals(self, task_id) -> dict          # recompute signals.json from the declared set; returns signals
    def classify(self, task_id, cls, risk, why, force_risk=False, accept_risk_none=None) -> dict
    def plan(self, task_id, plan_path) -> dict  # imports plan-meta; applies routing rules; phase execute|intake
    def step_start(self, task_id, step_id, frm=None, agent_id=None) -> dict
    def step_bind(self, task_id, step_id, agent_id) -> dict
    def step_verifying(self, task_id, step_id, agent_id=None) -> dict
    def step_report(self, task_id, step_id, report_json_path) -> dict
    def step_verdict(self, task_id, step_id, verdict_json_path) -> dict   # dispatches to step_done/step_fail/step_external
    def step_done(self, task_id, step_id, no_verifier=False) -> dict
    def step_fail(self, task_id, step_id) -> dict
    def step_external(self, task_id, step_id, needs: str) -> dict
    def attest(self, task_id, step_id, criterion, by, evidence, exit_code=0) -> dict
    def recover(self, task_id, step_id, force=False) -> dict
    def evidence(self, task_id, claim, from_check) -> dict
    def scope_add(self, task_id, path, why, ruling=False) -> dict
    def block(self, on) -> dict
    def unblock(self) -> dict
    def close(self, task_id, one_line=None, handoff=None, partial=False, cost=None, human_ack=None,
              accept_out_of_scope=None, no_commit=False) -> dict
    def stale(self) -> dict
    def fresh(self, stamp=True) -> dict
    def gate_block(self, task_id, agent_id, gate) -> dict
    def restamp(self) -> None                   # re-record status.sha after a deliberate hand edit (journaled)
    # read-only
    def get(self, what: str, lenient: bool = False) -> str
        # what ∈ summary | resume | digest | next_action | <dotted.path like task.phase>
```

Rules implemented in `plan()` (design §4.3 and §5.1): class/step-count constraints; `mode: parallel` → `single` unless
`len(steps) ≥ 3`, pairwise-disjoint brief `allowed_paths`, and `binding.git.worktree_isolation`; risk re-matched over every
brief's `allowed_paths` (and `creates`); risk → builder floor `forge-builder fable/low` and verifier `fable/medium`,
`forge-builder-s`/`forge-mechanic` refused; `mechanical: true` refused when any allowed path matches
`mechanic_denied_paths`; verifier tier ≥ builder tier; `important_hits` or `importers ≥ 10` raise the verifier to `fable`;
`routing.overrides[]` applied to steps whose paths intersect; a cheaper tier than the class default only when
`tests_present`; `needs_clarification` non-empty → `phase: intake`, `next_action: "ask the user: ..."`.
`open()` constraints: `T` ⇒ `len(files) ≤ 2`; `T/S` ⇒ no risk hits (unless `accept_risk_none`); `S` ⇒ `files ≤ 3 ∧ dirs ≤ 2`;
`M` ⇒ `files ≤ 10 ∧ dirs ≤ 3`; `why ≥ 20 chars`; `risk == "R"` ⇔ `risk_hits ≠ ∅` unless forced.
Phases after `open`: `T` → `execute` (mode inline), `S/X/M/W/L` → `plan`. `T` and inline classes set `scope` = declared set.
`close()` preconditions (design §5.1 table): every step `done` (or `--partial` with `ruling.md`); T ⇒ `one_line` and ≥1 `checks/`
record with `ok: true` for step `main`; S/X ⇒ handoff validates in short form; M/W/L ⇒ full form; R ⇒ `human_ack`;
scope backstop: `git status --porcelain ∪ git diff --name-only <task.base>..HEAD` ⊆ `scope ∪ .forge/** ∪ CLAUDE.md ∪
.gitignore ∪ .claude/agent-memory/**` else refuse unless `accept_out_of_scope`. Effects: CHANGELOG line, history row
(file + last 5), ledger `close`, `git add -A -- .forge/ <scope> && git commit` (skipped with `no_commit` or when
nothing to commit), `context_state` per `clear_policy` (`phase|task` → `stale`; `never` → unchanged), `task: null`
(or next queued task promoted to `queue[0]` only; never auto-opened).

CLI: `forge-status <subcommand> [args]` mirroring the methods; flags use `--kebab-case` (`--from`, `--one-line`, `--human-ack`,
`--accept-out-of-scope`, `--force-risk`, `--accept-risk-none`, `--no-stamp`, `--no-verifier`, `--restamp`, `--lenient`,
`--agent`, `--report`, `--verdict`, `--needs`, `--by`, `--evidence`, `--exit`, `--claim`, `--from-check`, `--why`, `--ruling`,
`--on`, `--partial`, `--cost`, `--handoff`, `--queue`, `--class`, `--risk`, `--files`, `--creates`, `--title`).
`get` prints text; every other subcommand prints one line (`<task> <phase> <step?> <status?> | next: <next_action>`).

Digest format (`get digest`, ≤ `MAX_DIGEST` chars): `T-0007 "title" class M risk none phase execute mode single` /
one line per step `NN status agent/model/effort attempts=N commit=<7>` / `next: ...` / `resume_hint: ...` /
`blocked_on`/`external` when set / `evidence: N (newest 2 ...)` / `queue: ids` / `history: last 5 "id outcome"` /
`[full: .forge/STATUS.json]`. `get resume` = digest + the newest handoff's *Remaining* and *Gotchas / do not touch* sections.
`get summary` = the one-line form + next_action. `get --lenient` never exits non-zero.

---

## 4. `forgelib.gates` — validators (`forge-gate` CLI)

```python
def plan_meta(paths, task_id) -> dict|None            # parsed plan-meta or None
def brief_meta(paths, task_id, step_id) -> dict|None
def plan_validate(paths, task_id) -> list[str]        # defects; [] = valid
def handoff_validate(paths, task_id, step_id, text, agent_id=None, red_ok=False, short=False, task_level=False) -> tuple[list[str], dict|None]
def verdict_validate(paths, task_id, step_id, text, agent_id=None) -> tuple[list[str], dict|None]
def check_records(paths, task_id, step_id, agent_id=None) -> list[dict]   # parsed checks/ records, newest first
def last_source_edit_ts(paths, task_id, agent_id) -> int|None
def tree_changed(paths, allowed_paths) -> list[str]   # git porcelain limited to allowed_paths, untracked included
def persist_handoff(paths, task_id, step_id, text, parsed) -> tuple[str, str]   # writes report-NN.md/json, returns paths
def persist_verdict(paths, task_id, step_id, text, parsed) -> tuple[str, str]
```
Handoff rules (design §5.5): mandatory headings; JSON parses with `schema == SCHEMA_HANDOFF`, `task`, `step`, `status`,
`files_changed`, `checks_run`; `files_changed ⊆ allowed_paths` (globs); `source_edits(agent_id) ⊆ files_changed`;
`tree_changed(allowed_paths) ⊆ files_changed`; for `DONE|DONE_WITH_CONCERNS`: every brief `checks[]` cmd has a record
`results[].cmd == cmd` with `exit == 0` (any exit when `red_ok`) by this `agent_id` whose `ts` ≥ last source-edit `ts`;
`tdd` → each `expected_fail_first[]` cmd has a non-zero record earlier than a zero record. `BLOCKED|NEEDS_CONTEXT` need
no check records. Task-level handoffs (`task_level=True`) skip the evidence/check rules and require headings only
(short or full) plus a valid JSON block with `step == "task"`.
Verdict rules (design §5.6): headings; every brief `dod[]` id appears exactly once with `result`, `cmd`, numeric `exit`;
`verdict == PASS` ⇒ all `PASS` ∧ `scope_check == PASS` ∧ `ratchet == PASS` ∧ `blocking_findings == []`; every cited
`cmd` has a check record by this verifier `agent_id` (except `check: external` criteria which need a `human` record
with that criterion; otherwise the criterion must be `UNKNOWN`); `tags ⊆ VERDICT_TAGS`.
For inline tasks (step `main`) the dod list comes from plan-meta and `allowed_paths` from `task.scope`.

CLI: `forge-gate --plan <task>` · `forge-gate --handoff <task> <step> (--from-file f | --from-stdin) [--agent id] [--task-level] [--short]` ·
`forge-gate --verdict <task> <step> (--from-file f | --from-stdin) [--agent id]`. Prints one defect per line; exit 0/1/2.
When `--agent` is absent and exactly one `.runtime/agents/*.json` is bound to that step, use it; otherwise skip agent-scoped rules and print a WARN line on stderr.

---

## 5. `forgelib.checks` — `forge-check` CLI

```python
def baseline(paths) -> dict                 # {"files": n_test_files, "tests": n_matches, "recorded_at"}
def run_checks(paths, task_id, step, expect_fail=False, ratchet=False, only=None, only_paths=None, agent_id="unknown") -> dict  # record (also written)
```
CLI: `forge-check <task> <step|main|plan> [--expect-fail] [--ratchet] [--baseline] [--only <name>] [--only-paths <glob>...] [--agent <id>]`.
Command list = `binding.verify[]` filtered by `when` (`always` or `paths:<glob>` against the step's changed set:
`git status --porcelain -- <allowed_paths>` for a step, the whole porcelain for `main`; `{layer}` substituted) ∪ the brief's
`checks[]` (deduplicated by cmd; brief checks run even when a verify entry is skipped). `exists` missing → `skipped`.
Each command runs through `bash -c` from the repo root with a 20-minute cap; prints `FORGE_CHECK name=<n> exit=<e> dur=<s>s cmd=<cmd>`
per command and `FORGE_CHECK_SUMMARY pass=a fail=b skipped=c` at the end; writes the record (§2.7). `--ratchet` compares
`binding.test_globs` files and `grep -cE test_pattern` totals against `plan_meta.test_baseline` (FAIL on a deleted test file or
lower count unless the brief says `may_edit_tests`; `UNKNOWN` without a baseline). `--baseline` prints the baseline JSON and
exits 0 without running anything. Exit 0 when every non-skipped command exited 0, else 1; 2 usage. `step == plan` with
`--baseline` is how the planner records the baseline.

---

## 6. `forgelib.hooks` — `forge-hook` CLI (the dispatcher)

```python
def dispatch(stdin: dict, flags: set[str]) -> dict|None   # flags ⊆ {"role", "plugin"}; returns the stdout JSON or None
```
`forge-hook [--role] [--plugin]` reads stdin once, dispatches on `hook_event_name` (+ `tool_name`), prints at most one JSON
object, **always exits 0** (never 2); a crash is caught at the top level and, for `PreToolUse`/`SubagentStop`, turns into a
deny/block JSON naming the exception (fail closed), for everything else into `{"systemMessage": "Forge hook crashed (<event>): run /forge-doctor"}` (fail open).
`--plugin`: exit 0 immediately when `<root>/.forge/VERSION` exists. Every event handler is a function
`on_<event_snake>(ctx) -> dict|None` where `ctx` holds `paths, stdin, status, binding, session_id, role (agent_role of agent_type), agent_id, is_subagent`.
Implement exactly the per-event table in design §13.3 (events: SessionStart ×2 handlers, UserPromptSubmit, PreToolUse
Edit|Write|NotebookEdit, PreToolUse Agent, PreToolUse Bash, PostToolUse Bash|Edit|Write|NotebookEdit|Read, PostToolUseFailure Bash,
SubagentStart, SubagentStop planner/builders/verifier, Stop, PreCompact, ConfigChange, StopFailure, SessionEnd).
Output shapes: `{"hookSpecificOutput": {"hookEventName": "<Event>", "additionalContext": "..."}}`,
`{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny|ask|allow", "permissionDecisionReason": "..."}}`,
`{"decision": "block", "reason": "..."}`, `{"systemMessage": "..."}`, `{"continue": false, "stopReason": "..."}`.
Irreversible-command matching: `binding.irreversible_commands[]` patterns are matched against the command with `common.glob_match`
semantics applied to the whole string (`*` matches anything including spaces); also match each `&&`/`;`/`|` segment.
`looks_mutating(cmd)` and `ro_allowed(cmd)` live in `gates.py` (shared with doctor tests) with the regexes from design §13.3.

---

## 7. `forge-doctor`, `forge-run`, `forge-bench`

`forge-doctor [--report] [--no-probes] [--quick] [--probe-hooks] [--driver] [--probe-clear] [--worktree] [--probe-maxturns]
[--probe-coldstart] [--pointers] [--disable-gate <name>] [--json]`: static checks print `OK|WARN|FAIL <name>: <detail>` lines
and exit 0 when no FAIL (1 otherwise). Checks: python ≥ 3.9; `claude --version` ≥ 2.1.295 (WARN if `claude` absent);
trust state in `~/.claude.json` (`projects.<root>.hasTrustDialogAccepted`, WARN); `.forge/VERSION` vs `forge/VERSION` when the
source tree is present and vs `binding.forge_pin`; `install-manifest.json` drift (sha256 per file, WARN per drifted file);
binding schema; STATUS validates; settings.json contains every Forge hook entry from `settings.forge.json` (same matcher, command
prefix, `onFailure` only on PreToolUse/SubagentStop), `model`, `effortLevel`, `subagentPromptCacheTtl`, `permissions.allow` for
`.forge/bin`; `.forge/bin/*` executable; `.gitignore` has `.forge/.runtime/` and `.forge/incidents/`; duplicate `forge-*` agents on
the filesystem; `--pointers` (every path named in FORGE.md exists; listed `/forge-*` skills exist); digest size.
Probes (never from `!` injections): `--probe-hooks` runs `claude -p "say ok" --output-format stream-json --verbose --max-turns 1 --model haiku --permission-mode dontAsk`
and asserts `.runtime/hooks-alive` was rewritten; `--driver` runs one trivial `claude -p` phase with the driver's allowed tools and asserts
`permission_denials == []` and `modelUsage` names a fable model; `--probe-clear`, `--worktree`, `--probe-maxturns`, `--probe-coldstart` per design §12.2 (report what was observed; never assume).
`--disable-gate <name>` writes `.runtime/gate-disabled-<name>` and journals it.

`forge-run [--max-phases N] [--budget-usd X] [--dry-run]`: the driver loop from design §13.3 (`claude -p` per phase with
`--model fable --effort <binding.routing.architect_effort> --permission-prompts none --permission-mode acceptEdits --allowedTools ... --output-format json
--max-budget-usd <cap> --max-turns <n>`), parses `total_cost_usd`, `permission_denials`, `modelUsage`, writes `measured` ledger
`phase` rows and `.runtime/phase-costs.jsonl`, aborts with exit 6 on denials, exit 4 when hooks-alive was not rewritten, exit 3 on the
R human gate; touches/removes `.runtime/driver`.

`forge-bench <taskset.json> [--out .forge/COST-REPORT.md]`: optional; per task runs the driver arm and a solo arm in fresh
`git worktree`s, records pass/fail (the task's `check` command), `total_cost_usd`, `cache_read_share`; writes cost per passed task by class.

---

## 8. Settings fragment and installer

`payload/.claude/settings.forge.json` = design §13.4 verbatim with Python-invoked commands:
`"command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook"` (the scripts are executable Python files).
`forge/installer.py --target <dir> [--source <payload dir>] [--upgrade] [--force] [--dry-run] [--effort low|medium] [--no-model] [--with-bench]`
implements design §10.1 steps 1-7 (copy Forge-owned files with manifest; merge settings with the rules in §8.2 — scalars: fragment
wins only when absent locally unless `--force`; arrays: union; Forge hook entries identified by command prefix `"$CLAUDE_PROJECT_DIR"/.forge/bin/` are replaced,
non-Forge entries kept; `permissions.allow` gains `Bash(<prefix> *)` per `binding.verify[].cmd`; CLAUDE.md fragment between
`<!-- forge:begin -->`/`<!-- forge:end -->`; stack detection → `binding.json` only when absent; idle STATUS; empty jsonl files;
`lessons/INDEX.md`; `decisions/0001-adopt-forge.md`; `.gitignore` lines; `install-manifest.json`; `.forge/VERSION`).
`forge/install.sh` is a thin bash wrapper: checks `python3`, resolves the payload (local checkout or `git archive` of a tag), runs `installer.py`.
