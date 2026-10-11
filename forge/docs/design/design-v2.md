# The Forge — Design v2 (final build spec)

Version 1.0.0 of the Forge; design revision 2, 2026-10-11. Target runtime: Claude Code 2.1.296. This revision applies the 75 red-team findings against design v1 (§16 logs each one). Every mechanism cites `research-claude-code.md` (**RCC line n**), `requirements.md` (**REQ line n**) or `research-patterns.md` (**RP §n**). Facts observed in this sandbox but absent from the research files are labelled **[observed]** and carry a doctor probe.

Enforcement labels:
- **[G]** guaranteed: a hook, a setting, a script refusal or a process boundary verified in RCC/REQ decides it.
- **[G/cap]** guaranteed up to a documented platform ceiling (the 8-continuation Stop cap, RCC line 305).
- **[G at close]** not prevented mid-task but refused deterministically by `forge-status close`/`step-done`.
- **[I]** instructed: prompt or ritual text; nothing enforces it.
- **[U]** unverified against the research files; a fallback and a doctor probe are named.

Reading order for the builder: §13 is the build list (exact file contents); §3 and §5 are the contracts those files must satisfy; §7 lists every gate; §16 says which finding each rule answers. Conventions used everywhere in this document: every script path is written in full as `.forge/bin/<tool>` and is run from the repository root (the settings fragment keeps the Bash tool's working directory there, §13.4); there is no `bin/` shorthand.

---

## 1. Thesis

The Forge is a document-driven engineering team hosted inside Claude Code. Its durable state is plain files in the consumer repository (`.forge/STATUS.json`, one directory per task, lessons, decisions, an append-only ledger); its enforcement is twelve hook registrations backed by one dispatcher script and one state-machine CLI; its intelligence is a Fable 5.1 architect that plans, routes, audits and codes the hardest work itself, plus disposable fresh-context workers that implement and refute. Five findings carry the design:

1. **Plain project layout is the only form verified to load everywhere.** A plugin vendored under the project's `.claude/skills/forge/` did not load in a fresh headless session and loads only after workspace trust (REQ lines 63, 69); plain `.claude/agents`, `.claude/skills` and project `settings.json` hooks load even untrusted (REQ lines 64, 69, 74). The shipped form is plain layout expanded by an installer; the plugin manifest is a secondary user-level wrapper that self-silences inside a vendored repo.
2. **A rule that lives in a hook is a fact; a rule in a prompt is a request** (RP §4 rec. 5; REQ lines 71-75). Plan-first, scope fences, handoff shape, evidence capture, STATUS integrity, routing-at-spawn, tool budgets and the policy-file lock are hook-decided. What the platform cannot decide (`/clear` in interactive mode, RCC line 312; REQ line 42) is designed as the next-best enforcement and labelled [I]. v2 also closes the back doors v1 left open: shell writes, hand edits to the enforcement layer, and gates that depended on undocumented behaviour.
3. **Orchestration pays only for bulk, file-disjoint work; one dependent chain belongs in one context; the frontier model at low effort is often the cheapest solver per task** (REQ line 25; RP §3). v2 therefore runs trivial, small *and extreme* tasks inline in the architect (REQ line 6: Fable codes the extremely difficult tasks), medium and wide tasks in exactly one fresh-context builder with one verifier, and cheap workers only on plan-proven disjoint units. The bookkeeping that v1 charged to Fable turns is now done by zero-token hooks.
4. **Verification is evidence, not claims, and depends only on files the Forge writes itself.** Gates audit a hook-captured evidence log (documented `PostToolUse`/`PostToolUseFailure` fields, RCC lines 203-204), exact exit codes from `forge-check`, and git commits the gate itself made; never the transcript. A fresh-context verifier re-runs the checks (RP §4 rec. 2; REQ line 23). Work whose only real check is external (a scheduled workflow, an emulator) has a first-class human-attested evidence path instead of a dead end.
5. **Every harness component is a stale-able assumption and every cost figure is a hypothesis until the ledger measures it** (RP §1 managed-agents; RP §4 rec. 9). Clearing policy, routing thresholds, budgets and verifier tiers are data in a project-owned binding; cost rows are `measured` or `unknown`, never guessed; the system is versioned with a file-ownership upgrade contract.

What the operator gets: three daily commands (`/forge-task`, `/forge-next`, `/forge-close`), a status file that is always the truth, workers that cannot return without proof, a close ritual sized to the task, and an upgrade that never touches project-owned state.

---

## 2. Roles and agent roster

The **architect is the main session** (Fable 5.1; the settings fragment pins `model: fable` and the driver passes `--model fable`, §13.4, §13.3). It is never run as `claude --agent` because a custom agent's prompt replaces Claude Code's default system prompt (RCC line 95). Its role text is injected by a `SessionStart` hook (`additionalContext`, RCC line 265; re-run on `compact`, RCC line 416) only when the stdin has no `agent_type` (RCC line 200), so no worker inherits it. Workers are plain project agents in `.claude/agents/`; their `agent_type` in hook stdin equals the file's `name` (REQ line 73). v2 dispatches **every** worker through the `Agent` tool (`subagent_type`), the one path on which `agent_type == agent name` was verified; `context: fork` skills are not used anywhere because the `agent_type` a forked skill reports is undocumented (RCC lines 538-540; §16 #3, #40).

Eight agent files. Builder tiers are separate files because in-worker hooks see `agent_id`/`agent_type` (RCC line 194), never the model (no `$CLAUDE_MODEL`, RCC line 353). Opus and Fable share `forge-builder` (identical in-worker rules; the per-invocation `model` parameter, RCC line 125, selects). `forge-builder-wide` exists only because `maxTurns` is frontmatter-only (RCC line 38).

| Agent file (`name:`) | Purpose | Model / effort (frontmatter → allowed per-invocation overrides) | Tools and flags | Invoked when | Must never (enforcement) |
|---|---|---|---|---|---|
| **architect** (main session, no file) | Intake, classification, routing, brief dispatch, adjudication, inline T/S/X work (and small R work), STATUS ownership through `forge-status`, talking to the user | `fable`; project `effortLevel: medium` written by the installer from `binding.routing.architect_effort`; skills set `effort:` per ritual (§13.2) | all | every session | edit source while class ∈ {M,W,L} [G, PreToolUse Edit + Bash mutation guard]; edit `.forge/STATUS.json`, any Forge-owned file or `.claude/settings*.json` [G]; spawn a `forge-*` worker whose agent/model/effort disagree with the plan [G]; end a work turn without STATUS reflecting it [G/cap]; keep worker transcripts in its context [G by construction] |
| `forge-scout` | Cheap read-only survey; condenses large tool output to ≤1,200 tokens | `claude-haiku-5-5` / `medium` (never `low`, REQ line 24) | `Read, Grep, Glob, Bash`; `omitClaudeMd: true`; `maxTurns: 25` | architect or planner needs a survey that would flood context | write anything [G: no Edit/Write + Bash **allow-list**] |
| `forge-planner` | Fresh-context plan for M-large/W/L: the user's plan template fields (REQ line 20) plus a `plan-meta` JSON block; one brief per step | `claude-fable-5-1` / `high` → `effort: medium` for routine M (per-invocation) | `Read, Grep, Glob, Bash, Write`; `maxTurns: 30`; `experimental.cacheTtl: 1h` | `/forge-task` for class M-large/W/L via `Agent(subagent_type: "forge-planner")`; re-plan | write outside `.forge/tasks/<id>/` [G, fence]; shell writes [G, Bash allow-list]; return without a plan that passes the plan gate [G, SubagentStop] |
| `forge-builder` | Implements one brief in a fresh context (Opus or Fable tier) | `claude-opus-5-5` / `medium` → `model: fable`, `effort: low\|medium` | `Read, Edit, Write, Grep, Glob, Bash`; `maxTurns: 80`; `cacheTtl: 1h` | M (one step), R-overlay M/W/L units (`fable/low`), escalation from Sonnet | edit outside `allowed_paths` [G]; edit existing tests unless `may_edit_tests` [G]; protected paths unless `task.risk == "R"` [G]; `git push` [G]; exceed `brief.max_tool_calls` [G]; return without a validated handoff whose checks ran after the last source edit [G] |
| `forge-builder-wide` | Same contract, for one wide dependent chain (class W) | `claude-fable-5-1` / `low` → `effort: medium` on retry | same as builder; `maxTurns: 300` | W only | same as builder |
| `forge-builder-s` | Same contract on the Sonnet tier | `claude-sonnet-5-5` / `medium` (no model override; effort may be raised) | same as builder; `maxTurns: 60` | L units | all of the above, plus protected and `mechanic_denied_paths` always denied [G] |
| `forge-mechanic` | Mechanical edits with an exact spec | `claude-haiku-5-5` / `medium` | `Read, Edit, Write, Grep, Glob, Bash`; `omitClaudeMd: true`; `maxTurns: 40` | L units marked `mechanical: true` whose paths avoid `mechanic_denied_paths` | anything outside the manifest, protected, risk or mechanic-denied paths [G]; verifying [G, spawn guard] |
| `forge-verifier` | Fresh-context refutation of a committed diff against the brief's DoD; re-runs `forge-check`; returns a VERDICT | `claude-opus-5-5` / `medium` → `model: sonnet` (S, L units), `model: fable` (X, R, W, L spot-check) | `Read, Grep, Glob, Bash`; `memory: project` (which auto-enables Write/Edit, RCC line 116); `omitClaudeMd: true`; `maxTurns: 40`; `cacheTtl: 1h` | after every builder handoff for M/W/L; S when tests changed; X always | modify anything except `.claude/agent-memory/forge-verifier/**` [G: fence allow-list evaluated before the deny + Bash allow-list]; see the worker transcript [G by construction]; approve with FAIL or a required-criterion UNKNOWN [G, verdict gate] |
| `forge-librarian` | Doc garbage collection, lessons dedupe, ledger rollup, archive, MEMORY.md lint | `claude-sonnet-5-5` / `medium` | `Read, Grep, Glob, Bash, Edit, Write`; `omitClaudeMd: true`; `maxTurns: 60` | `/forge-gc` via `Agent(subagent_type: "forge-librarian")` | write outside `.forge/lessons/**`, `.forge/COST-REPORT.md`, `.forge/archive/**`, `.forge/decisions/**`, `CLAUDE.md`, `.claude/agent-memory/**` [G]; touch `binding.json`, `ledger.jsonl`, scripts, schemas [G] |

Roster notes:
- The Anthropic "run a real check before reporting done" paragraph (REQ line 24) lives in the bodies of `forge-builder-s` and `forge-mechanic` only, plus the Haiku "keep working until done" line in the mechanic.
- `memory: project` is set **only** on `forge-verifier` (calibration notes, capped at 60 lines by `/forge-gc`). Builders, the planner and the mechanic have no agent memory: their lessons travel in the handoff's *Failed approaches* and are promoted to `.forge/lessons/` at close (§16 #66). The verifier's memory directory is the only path its fence lets it write.
- `omitClaudeMd: true` (RCC line 44, v2.1.271+) on scout, mechanic, verifier and librarian; the brief carries everything a worker needs (§5.4), and path-scoped stack rules still load.
- `experimental.cacheTtl: "1h"` (RCC line 48) on planner, builders, mechanic and verifier, and `subagentPromptCacheTtl: "1h"` in settings (RCC line 949): `forge-check` runs can exceed the 5-minute default TTL.
- `maxTurns` is the backstop; the real per-brief ceiling is `brief-meta.max_tool_calls`, enforced by the `PreToolUse` hook from the evidence log (§7 gate 2b).
- No `Agent` in any worker's `tools`, so nesting is off for workers (RCC line 102). Built-in `Explore` and `Plan` remain available to the architect; `general-purpose` is denied in settings (`Agent(general-purpose)`, RCC line 87) and `env.CLAUDE_CODE_SUBAGENT_MODEL: "sonnet"` makes any remaining built-in run on Sonnet (RCC line 82; Explore uses the Opus alias under Fable regardless, RCC line 80). Every non-`forge-*` spawn is journaled as `agent: builtin` so unrouted work is visible in the ledger.
- Pinned full model IDs in frontmatter (RCC line 1319); per-invocation overrides use aliases (RCC line 125); the spawn guard normalizes both through one alias table before comparing (§13.3).

---

## 3. Lifecycle of one task, end to end

Worked example on the first consumer: **"nfs_trails: add golden-bbox count QA so the trail tileset can go live"** — the architect declares the edit set `qa/golden_counts.py`, `layers/nfs_trails/layer.json` and the new file `layers/nfs_trails/tests/test_golden.py`; one dependent chain; `layers/nfs_trails/` has no tests yet, so `tests_present=false` and the plan adds them as DoD-1; `qa/golden_counts.py` is not a risk path in the v2 binding (§5.2; §16 #33). Class **M**, M-small (3 files, 2 dirs, no risk) → the architect writes the plan and brief itself. Task id `T-0007`. The repo is on its working branch (`binding.git.branch_per_task: false`, §16 #38).

| # | Step | Who | Mechanism and label |
|---|---|---|---|
| 0 | **Session start.** `SessionStart` (source `startup`) runs `forge-hook` twice: (a) the digest handler writes `.forge/.runtime/session-id` (from stdin `session_id`, REQ line 69), `hooks-alive`, appends `export PATH="<root>/.forge/bin:$PATH"` to `$CLAUDE_ENV_FILE` (RCC line 349; a convenience, [U] for subagents), computes the INTERRUPTED banner from `steps[].started_by` **before** any STATUS write, then emits `additionalContext` = compact STATUS digest (≤3,000 chars, `[full: .forge/STATUS.json]`) + banner + newest handoff's *Remaining*/*Gotchas* + git state + lessons head + binding digest + VERSION drift (≤9,800 chars total); (b) the role handler emits the architect block when stdin has no `agent_type`. `sessionTitle: "forge idle"` or `"forge T-0007 execute"`. | hooks | [G] injection (RCC lines 265, 310; REQ line 69) |
| 1 | **Intake, one call.** User types `/forge-task nfs_trails: add golden-bbox count QA …`. The skill (effort `medium`) injects `forge-status get summary --lenient` (never fails) and tells the architect to run **one** command: `.forge/bin/forge-status open --title "…" --class M --risk none --files qa/golden_counts.py layers/nfs_trails/layer.json --creates layers/nfs_trails/tests/test_golden.py --why "3 declared files in 2 dirs, one dependent chain, no risk hits; nfs_trails has no tests so the plan adds them first"`. `open` allocates `T-0007`, creates `.forge/tasks/T-0007/`, computes **signals from the declared edit set** (size from `--files ∪ --creates`; advisory blast-radius signals `importers`, `recent_cochanges`, `risk_hits` from globs over the declared set *and* its importers) and applies the class rules: it refuses `T` with >2 declared files, `T/S` with any `risk_hits`, `M` with `files > 10 ∨ dirs > 3` (that is W), and records `size_source: declared`. Advisory signals only **raise** the verifier tier (§4.3 rule 11). The declared set becomes the inline `allowed_paths` for T/S/X and the scope ceiling for every class. | architect + script | [G] script refusal; the declaration is architect judgment [I] |
| 2 | **Plan-first fence.** From here any main-session `Edit\|Write\|NotebookEdit` to a path outside `.forge/tasks/<id>/**`, `.forge/lessons/**`, `.forge/decisions/**`, `.forge/CHANGELOG.md`, `CLAUDE.md`, `.gitignore` is denied while `task.class ∈ {M,W,L}` (those classes never implement in the architect) or while `task.plan` is null for S/X. Main-session Bash is held to the same line by the mutation guard (§13.3): write-shaped commands (`sed -i`, `tee`, `>`, heredocs, `python -c`, `rm`, `mv`, `cp`, `git checkout --`) are denied for M/W/L and when no task is open; `.forge/bin/*`, `git add/commit/status/log/diff/show`, and `binding.verify[]` commands are allowed. Three denials of the same rule in one turn return `continue: false` so the turn ends with one message instead of further Fable retries (RCC line 252; §16 #74). | `forge-hook pre-tool-use` | [G] for tool edits; [G at close] backstop for anything the heuristic misses (§7 gate 1) |
| 3 | **Plan.** M-small: the architect writes `.forge/tasks/T-0007/plan.md` (mandatory machine headings only: `plan-meta`, *Steps*, *Validation Criteria*, *Routing*, *Rollback*; the other user-template headings are optional for M) and `brief-01.md` from the templates, ~2K output tokens. M-large/W/L: the architect calls `Agent(subagent_type: "forge-planner", model: "fable", effort: "medium" (M) \| "high" (W, L), prompt: "Plan Forge task T-0007: read .forge/tasks/T-0007/signals.json, .forge/schemas/routing.json, .forge/binding.json, .forge/lessons/INDEX.md and the code; write plan.md and one brief per step; end with PLAN-FILE: …")`. The spawn guard allows the planner only while `phase == plan`. The **plan gate** (`SubagentStop` matcher `^(forge:)?forge-planner$`) blocks the return until `.forge/bin/forge-gate --plan T-0007` passes (the planner is told to run that same command before its final message, so a block is the exception, not the norm). | architect or planner + gate | [G] gate (REQ line 73 path); plan quality [I] |
| 4 | **Route.** `.forge/bin/forge-status plan T-0007 --from plan.md` imports steps and routing and validates the hard rules (§4.3): M has exactly one step; risk re-matched on every brief's `allowed_paths` (new or existing); risk → `forge-builder` with `fable/low` floor and Fable verifier; verifier tier ≥ builder tier; `parallel` only with ≥3 disjoint units **and** `binding.git.worktree_isolation == true` (else rewritten to `single`, journaled); `mechanical: true` refused on `mechanic_denied_paths`; `routing.overrides[].paths` applied. Phase → `execute`, `next_action: "Dispatch forge-builder (opus/medium) on brief-01"`. | script | [G] |
| 5 | **Dispatch, one call.** The architect calls `Agent(subagent_type: "forge-builder", model: "opus", effort: "medium", run_in_background: true, prompt: "Read .forge/tasks/T-0007/brief-01.md with the Read tool, then execute it. End with the HANDOFF in the brief's Output contract.")`. The **spawn guard** (`PreToolUse` matcher `Agent`) allows it only if a `pending` step has `agent/model/effort` equal (alias-normalized) to the call, and **on allow runs `.forge/bin/forge-status step-start T-0007 01` itself**: `running`, `attempts: 1`, `started_at`, `started_by: <session-id>`, `base: <git rev-parse HEAD>` written to `.forge/tasks/T-0007/.base-01`. For a retry (step `failed`) the guard requires the architect to have run `step-start --from failed\|clean` first (step `running`, `agent_id: null`). No architect bookkeeping call is needed. `SubagentStart` (matcher `forge-.*`) records `agent_id → agent_type` and injects a one-line format reminder only. | guard + script | [G] |
| 6 | **Bind worker to brief.** The builder's first tool call is `Read .forge/tasks/T-0007/brief-01.md`; `PostToolUse` (`Read`, or `Bash` whose command `cat`s/`sed -n`s a brief path) binds the agent **only** to a brief whose step is `running`, has `agent_id == null` and `owner_agent == role`; reading a sibling brief for context never rebinds. Until bound, every `Edit\|Write` by that agent is denied ("Read your brief with the Read tool first"). | `forge-hook` | [G] (fields RCC lines 194, 203) |
| 7 | **Execute inside the worker.** Scope fence: `Edit\|Write` outside `allowed_paths` denied; existing `test_globs` files denied unless `may_edit_tests` (new test files allowed); protected paths by tier; `.forge/**` denied except nothing (workers never write Forge state; hooks do); tool budget: once this `agent_id` has more `bash\|edit` rows in `evidence.jsonl` than `brief.max_tool_calls`, further Bash/Edit/Write are denied with "tool budget exhausted: write your HANDOFF with status BLOCKED". Bash guard for builders: `git push`, `git reset --hard`, `git clean`, `git checkout -- .`, `rm -rf` outside `/tmp`/scratchpad denied. Evidence: every `Bash`/`Edit`/`Write` appends a row keyed by `agent_id`; edit rows carry `kind: source\|meta` (`meta` for `.forge/**` and `.claude/agent-memory/**`). The builder runs `.forge/bin/forge-check T-0007 01 --expect-fail` after writing the new test (red), implements, then `.forge/bin/forge-check T-0007 01` (green; `layer-tests` fires because `layers/nfs_trails/tests` now exists, `lib-unit` always). Before its final message it runs `.forge/bin/forge-gate --handoff T-0007 01 --from-stdin <<'EOF' … EOF` (or writes the draft to the scratchpad and passes the path) to pre-validate. | hooks + scripts | [G] fences, budget and capture; red-then-green discipline [I], ordering [G] |
| 8 | **Handoff gate, which also records and commits.** The final message = four mandatory `## ` headings (*Where things stand · Done, with evidence · Remaining · Gotchas / do not touch*; the other seven headings are optional) + one fenced ```json `forge/handoff/1` block. `SubagentStop` (`^(forge:)?forge-(builder\|builder-wide\|builder-s\|mechanic)$`) validates (§5.5): JSON keys; `files_changed ⊆ allowed_paths`; every `kind: source` edit row of this agent ⊆ `files_changed`; every path in `git status --porcelain --untracked-files=all -- <allowed_paths>` ⊆ `files_changed`; for `DONE\|DONE_WITH_CONCERNS` every brief `checks[]` cmd has a `checks/01-*-<agent_id>.json` record at exit 0 (any exit when the plan marks the step `red_ok_until`) **newer than the agent's last `kind: source` edit row**; `tdd` → a non-zero record before a zero record. On allow it (a) persists `report-01.md/json`, (b) **commits** `git add -- <allowed_paths> .forge/tasks/T-0007/ && git commit -q -m "forge(T-0007/01): golden-bbox QA for nfs_trails [attempt 1]"` and writes the SHA into `report-01.json.commit`, (c) runs `.forge/bin/forge-status step-report T-0007 01` (`reported`, `next_action: "Dispatch forge-verifier (opus/medium) on step 01"`), (d) appends a ledger `attempt` row with `gate_blocks`. If (c) fails it touches `.runtime/dirty-worker` so the Stop gate insists the architect repair STATUS. After two blocks for one `agent_id` it allows and stamps `status: UNVERIFIED` (no commit); a `BLOCKED\|NEEDS_CONTEXT` handoff needs no check records and makes no commit. | gate | [G] (REQ line 73; RCC line 208) |
| 9 | **Verify.** On the completion notification (a later turn, RCC line 103) the architect's only call is `Agent(subagent_type: "forge-verifier", model: "opus", effort: "medium", prompt: "Verify .forge/tasks/T-0007/brief-01.md against the committed range $(cat .forge/tasks/T-0007/.base-01)..<commit> and report-01.md; run .forge/bin/forge-check T-0007 01 --ratchet yourself; grade every DoD id.")`. The spawn guard allows it because step 01 is `reported` and `verify_attempts < 2`; on allow it sets `verifying`. The verifier diffs **committed** work (`git diff <base>..<commit>`), re-runs checks (records keyed by its `agent_id`) and ends with a VERDICT. The **verdict gate** requires every brief `DoD-` id with `PASS\|FAIL\|UNKNOWN`, command + exit, a check record by this verifier per cited command (except `check: external` criteria, which need a human `attest` record), persists `verdict-01.md/json`, and runs `forge-status step-verdict T-0007 01`: PASS → `step-done` (records `commit`, verifies it descends from `.base-01` and touches only `allowed_paths ∪ .forge/tasks/T-0007/**`); FAIL → `step-fail` (`escalation.round += 1` unless every blocking finding is tagged `env-cannot-run`, which sets `phase: awaiting_external` instead). | guard + gate + script | [G] shape, evidence and transitions; judgment [I] |
| 10 | **Accept or escalate.** PASS needs nothing from the architect: STATUS already says `done` and `next_action: "/forge-close"`. FAIL → §4.3 ladder: round 1 resume the same builder via `SendMessage` with the blocking findings (RCC line 105; the builder's block counter is reset); round 2 `.forge/bin/forge-status step-start T-0007 01 --from failed\|clean` (mandatory choice: keep the failed tree and append the verdict to `brief-01.md §Known failed approaches`, or `recover` to the base) then a fresh worker one rung up; round 3 `ruling.md` then re-plan or `block`. A third verifier dispatch on one step without a ruling is refused by the spawn guard. | architect + script | [G] transitions; ladder [I] with script-enforced caps |
| 11 | **Close, sized to the class.** `/forge-close` (effort `low`): for M/W/L the architect writes `handoff.md` (four mandatory sections + JSON; optional sections as needed), promotes worker *Failed approaches* worth keeping into `.forge/lessons/<slug>.md`, writes an ADR only for a durable decision, then `.forge/bin/forge-status close T-0007 --handoff handoff.md` — it validates the handoff, refuses if a step is not `done`, refuses out-of-scope changes (§7 gate 1 backstop), appends the CHANGELOG line itself, writes the ledger `close` row (`cost_usd: null, cost_source: unknown` unless the operator passed `--cost`), commits `forge(T-0007): close`, sets `context_state` per `clear_policy`. For T: `close --one-line "<what> \| <check record>"` and nothing else. For S/X: handoff = JSON + *Where things stand · Done, with evidence · Remaining*. R: `--human-ack "<name> reviewed diff <sha>"` is mandatory after the skill prints `git diff --stat` and *Rollback*. The skill's last line is the CLEAR POINT. | skill + script | [G] validation; [I] the clear instruction |
| 12 | **Stop gate.** On every turn end: allow when no task is open or `phase ∈ {done, blocked, idle, awaiting_external}`; allow when `stop_hook_active` is true and the STATUS sha equals the sha recorded at the last block (never re-block on an unchanged state, RCC line 304); allow a `?` chat turn with no mutation; otherwise block while `.runtime/dirty-main` (a main-session source mutation newer than the last `forge-status` write) or `dirty-worker` exists, or the STATUS sha mismatches `.runtime/status.sha` (hand edit). Two consecutive blocks → allow with `systemMessage` + `stale-status` marker. The Stop hook has **no** `onFailure: block`: a crashed dispatcher fails open with a `systemMessage` "Forge Stop gate crashed: run /forge-doctor" and the STALE banner. No budget text is ever shown (§16 #60). | gate | [G/cap] (REQ line 72; RCC lines 301-305) |
| 13 | **Clear and resume.** Interactive: the human types `/clear forge-T-0007`. `SessionStart` (`clear`) injects the digest and, when `next_action` exists, `context_state == stale`, `binding.auto_resume` and no `.runtime/auto-resumed-<task>-<phase>` marker, emits `initialUserMessage` (plain text) and writes the marker; the hook then runs `forge-status fresh --no-stamp` (so `started_by` comparisons survive). Never on `compact`. Driver mode: `.forge/bin/forge-run` starts a new `claude -p` per phase; the clear is a process boundary. | hook / process | [G] injection; [U] `initialUserMessage` on `clear` (fallback `/forge-next`); [G] driver |
| 14 | **Next.** The resume turn reads STATUS and executes `next_action` (`/forge-next`, effort `low`, is the same thing typed by a human). | architect | [I] |

**Trivial path (class T).** `forge-status open --class T --files <≤2 paths> --why "…"` (one call) → inline edit (fence: only the declared files) → `.forge/bin/forge-check T-00NN main` → `.forge/bin/forge-status close T-00NN --one-line "<what> | <check file>"` (writes the history row and CHANGELOG line itself, commits). Two script calls plus the work. No plan, no planner, no verifier, no handoff.md.

**Small path (class S).** `open --class S` → the architect writes the inline plan section in `plan.md` (`plan-meta` with `mode: inline`, zero steps, DoD ids, `allowed_paths` = declared set) → `forge-status plan --from plan.md` (accepts `mode: inline` for S/X → `execute`) → implement inline → `forge-check` → if tests were added or changed, `Agent(subagent_type: "forge-verifier", model: "sonnet", effort: "medium", …)` (Opus when `importers ≥ 5`; §4.3 rule 11) → `close` with the short handoff.

**Medium path (class M).** Exactly one step, one fresh-context builder, one verifier. M-small (declared `files ≤ 5 ∧ dirs ≤ 2 ∧ risk none`): architect-written plan and brief. M-large: planner at `fable/medium`. Builder `opus/medium` by default; `fable/low` when `chain: true` (a shared module feeding several consumers inside one step) or when the ledger flip has been adopted by ADR. A multi-step M is refused by `forge-status plan`: merge into one brief or re-class as L.

**Wide path (class W).** One dependent chain too wide for M (>10 declared files or >3 dirs, no path-disjoint split): planner `fable/high`, builder `forge-builder-wide` (`fable/low`, `maxTurns: 300`, `max_tool_calls` from the plan, default 250), verifier `fable/medium`. Expected to cost about what solo Fable costs (§11) while adding a plan and a fresh verifier.

**Large path (class L).** The plan proves ≥3 units with pairwise-disjoint `allowed_paths`. Units run **sequentially by default** (fresh cheap context each: `forge-builder-s`, `forge-mechanic` when `mechanical: true` and no path intersects `mechanic_denied_paths`, `forge-builder` for an M-sized unit); `mode: parallel` is accepted only when `binding.git.worktree_isolation` is true, which the operator may set only after `/forge-doctor --worktree` passed (§6, §12.2). A shared prerequisite step may carry `red_ok_until: "<step id>"`, which lets its checks be red until that later step; the terminal step must be green on the full `forge-check`. Per-unit `forge-verifier sonnet/medium`; then one `forge-verifier fable/medium` spot-check of 20% of units (min 1) plus the full suite, which is the only full-suite result treated as authoritative.

**Extreme path (class X).** Novel, ambiguous, root-cause or outage work is **coded by the architect** (REQ line 6; RP §3: "for one dependent chain that fits one context, the frontier model alone … wins"; a plan for a root-cause debug cannot be written before the debug). `open --class X` → short plan section (hypothesis, DoD, rollback; `mode: inline`) → `/forge-investigate` (internal skill with `effort: medium`, so the investigation turn runs above the bookkeeping effort) → the architect investigates and fixes within the declared scope (the fence allows the declared files once `plan.md` exists; `forge-status scope add <path> --why` widens it with a journal line) → `Agent(subagent_type: "forge-verifier", model: "fable", effort: "medium")` is mandatory → close with the short handoff. Expected ~30% over solo Fable (§11), recorded `expected_premium: true`.

**Risk overlay (R).** Any `risk_hits ≠ ∅` on the declared set or on any brief's `allowed_paths` (including files that do not exist yet): the plan must contain *Rollback* with a concrete command; T/S-sized R work runs **inline in the architect** at `medium` effort with a mandatory `fable/medium` verifier; M/W/L R work uses `forge-builder` with `model: fable, effort: low` as the floor (RP implication 15: strongest model + explicit human gate), never `forge-builder-s`/`forge-mechanic`; `binding.irreversible_commands` return `permissionDecision: "ask"` in interactive sessions [G interactive]; in driver mode the Bash guard returns `deny` and `forge-run` refuses to start a phase whose brief contains an irreversible command, setting `phase: blocked`, `blocked_on: "human gate: <command>"` [G, blocked in driver]; `close` requires `--human-ack`.

---

## 4. Routing matrix

Routing is decided at intake (class) and plan time (per-step tier) from **structural signals over the declared edit set**, never from the executing model's self-assessed difficulty (RP §3). Effort is the first lever, model tier the second (RP §3 rec. 13). The matrix is data: defaults in `.forge/schemas/routing.json` (Forge-owned; what `forge-status` and the planner read) with the rationale in `.forge/ROUTING.md` (humans and the architect's occasional re-sweep); per-project overrides and measured flips in `.forge/binding.json`.

### 4.1 Signals (`forge-status open|signals`)

| Signal | Source | Used for |
|---|---|---|
| `files`, `dirs`, `creates` | the architect's `--files`/`--creates` declaration (`size_source: declared`) | size class; inline `allowed_paths` for T/S/X; scope ceiling for every class |
| `importers` | `git grep -l` of each declared module's import name (`≥4`-char identifier tokens), count only | advisory: `≥ 5` raises the verifier one tier (S: Sonnet → Opus; M: Opus → Fable when `≥ 10`) |
| `recent_cochanges` | `git log --name-only -20 -- <declared>` | advisory: files that usually change together but are not declared are listed in the plan's *Current State* prompt |
| `tests_present` | for every declared or created source path, a file matching `binding.test_globs` exists in that path's test location **or** the plan's first DoD adds one | whether cheap-first routing is **allowed** (rule 2) |
| `risk_hits` | (`declared ∪ creates ∪ every brief's allowed_paths`) ∩ `protected_paths ∪ risk_paths` via glob; title ∩ `risk_words` on `\b` word boundaries, case-sensitive for tokens ≤ 3 chars, minus each word's `not:` exclusions | R overlay |
| `important_hits` | declared ∩ `binding.important_paths` (LIVE layers, release paths) | raises the verifier to `fable` (rule 4) |
| `disjoint_units` | plan time, pairwise intersection of `steps[].allowed_paths` | whether L is **allowed** |
| `chain` | plan-meta flag: a shared module feeds several consumers inside the step | M → `fable/low` builder |
| `novelty`, `ambiguity` | architect judgment (mid-band only, RP §3); `needs_clarification` in the plan forces a user question | X; clarification turn |

Title-token grep is **never** used for size (it produced 15-57 candidate files for one-line fixes in this repo, §16 #23, #30).

### 4.2 The matrix

| Class | Definition (declared set) | Plan | Who builds (model/effort) | Mode | Verifier | Budget cap (USD) |
|---|---|---|---|---|---|---|
| **T** | ≤2 files, one-sentence diff, `risk_hits = ∅` | none; `--why ≥ 20` chars | architect inline (`fable`, session effort) | inline | none; `forge-check` record required at close | 1 |
| **S** | ≤3 files, ≤2 dirs, `tests_present` (or plan adds tests first), `risk_hits = ∅`, no novelty | inline plan section by the architect (`mode: inline`, zero steps) | architect inline | inline | `forge-verifier sonnet/medium` only if tests were added/changed (`opus` when `importers ≥ 5`); else `forge-check` | 3 |
| **M** | 3-10 files or ≤3 dirs, one dependent chain, clear after planning | M-small (`≤5 files ∧ ≤2 dirs ∧ risk none`): architect writes plan + brief; M-large: `forge-planner fable/medium` | **one** `forge-builder opus/medium` (`fable/low` when `chain` or `binding.routing.m_builder == "fable-low"`) | single, **exactly one step** | **one** `forge-verifier opus/medium` (`fable` when `important_hits` or `importers ≥ 10`) | 10 (12 chain) |
| **W** | one dependent chain, >10 files or >3 dirs, no disjoint split | `forge-planner fable/high` | `forge-builder-wide fable/low` (`medium` on retry) | single, one step | `forge-verifier fable/medium` | 25 |
| **L** | ≥3 units with pairwise-disjoint `allowed_paths` | `forge-planner fable/high` | per unit: `forge-builder-s sonnet/medium`; `forge-mechanic haiku/medium` when `mechanical ∧ ∉ mechanic_denied_paths`; `forge-builder opus/medium` for an M-sized unit; a shared prerequisite step may be `red_ok_until` | sequential; `parallel` only with proven worktrees | per unit `sonnet/medium`; then `fable/medium` spot-check (20%, min 1) + full suite | Σ unit budgets × 1.2 |
| **X** | novel, ambiguous, root-cause/outage, architecture change, or two prior escalations on one step | short inline plan section (hypothesis, DoD, rollback) by the architect | **architect inline** (`fable`, `medium` via `/forge-investigate`) | inline | `forge-verifier fable/medium`, mandatory | 30 |
| **R** overlay | `risk_hits ≠ ∅` (workflow YAML, R2 upload / KV alias flip code, licence/attribution fields, parcels attribute whitelist, secrets, deletions) | plan must have *Rollback* with a command | T/S-size: architect inline at `medium`; M/W/L: floor `forge-builder fable/low`; `forge-builder-s`/`forge-mechanic` forbidden | per base class | `forge-verifier fable/medium`; irreversible commands `ask` (interactive) / `deny` + blocked (driver); `close --human-ack` | base × 1.5 |

### 4.3 Rules encoded in `forge-status` (deterministic) and explained in ROUTING.md

1. **Don't over-orchestrate.** `mode: parallel` needs ≥3 pairwise-disjoint units **and** `binding.git.worktree_isolation == true`; otherwise `forge-status plan` rewrites to `single` and journals why. A shared dependency feeding several consumers is one M/W chain step (optionally `red_ok_until`), then L units for the dependants.
2. **Cheap-first only with a failure signal.** A tier below the class default (`sonnet` for an M-sized unit, `haiku` for a non-mechanical unit) is accepted only when `tests_present` holds for every path in the step. Otherwise start at the class's top rung (REQ line 25).
3. **Effort before model.** On FAIL, verdict tags `skipped-file`, `no-check-run`, `not-double-checked` → raise `effort` one level on the same model; otherwise change model (RP §3).
4. **Verifier tier ≥ builder tier; importance raises the verifier, not the builder.** `important_hits`, a user-stated "important", or `importers ≥ 10` → `fable` verifier.
5. **The mechanic never verifies, never touches risk, protected or `mechanic_denied_paths`**, and `forge-status plan` refuses `mechanical: true` for any step whose `allowed_paths` intersect them.
6. **Escalation ladder, capped.** Round 1: resume the same worker (`SendMessage`), block counter reset. Round 2: `step-start --from failed|clean` (mandatory on `attempts > 1`), fresh worker one rung up (`sonnet → opus → fable-low → fable-medium`), verdict appended to the brief. Round 3: `ruling.md` (`Decision — Why — Cost if wrong — Evidence`), then re-plan or `block`. `step-start` refuses `attempts > 3` without a ruling; `verify_attempts` is capped at 2 per step without a ruling.
7. **Environmental failures do not escalate.** A FAIL whose blocking findings are all tagged `env-cannot-run` sets `phase: awaiting_external` with `next_action` naming the exact local commands; no builder re-run, no round increment.
8. **Price the tail, don't hide it.** X, W and R rows carry `expected_premium: true`.
9. **Budgets are caps, not countdowns.** `binding.budgets.<class>` → `task.budget.cap_usd`. Driver mode enforces with `--max-budget-usd = cap × multiplier − Σ measured phase rows` (min 1), the execute phase of X/R/W may take up to 70% of it [G]. Interactive mode shows **no** spend to the model (RP §1: countdowns induce context anxiety); `/forge-gc` reports measured spend to the operator.
10. **Measure, don't assume.** Every `open|dispatch|attempt|verdict|close` writes a ledger row. `/forge-gc` computes cost per passed task, escalation rate and the `fable-low` vs `opus-medium` comparison **only over `cost_source: measured` rows** and reports the count of unmeasured rows beside them. Escalation rate > 40% proposes starting one rung higher; ≥10 measured rows showing the other M builder cheaper per passed task proposes a flip in either direction. Flips are ADRs.
11. **Advisory signals only raise tiers.** `importers`, `recent_cochanges`, `important_hits` never lower a class or a tier.
12. **Re-sweep per model generation** (RP §3): ROUTING.md carries the checklist; `forge-bench` runs it.

### 4.4 Consumer overrides (project-owned, `binding.json.routing`)

```json
"routing": {
  "architect_effort": "medium",
  "m_builder": "opus-medium",
  "overrides": [
    { "name": "ui-compose", "paths": ["app/src/main/java/**/ui/**/*.kt"], "builder": { "agent": "forge-builder", "model": "opus", "effort": "medium" }, "min_verifier": "opus" }
  ],
  "measured": { "note": "filled by /forge-gc from measured ledger rows only" }
}
```

`forge-status plan` applies an override to every step whose `allowed_paths` intersect its `paths` and refuses a lower tier.

---

## 5. Schemas

Design rule: **JSON for anything a hook or script reads or a model must not freely rewrite; Markdown for anything a human or the next role reads.** Machine fields never live in YAML frontmatter (bash + jq cannot parse YAML). Every Markdown artifact that carries machine fields opens with one fenced ```` ```json ```` block, extracted with `json_block` (§13.3) and validated with `jq -e`. Timestamps are stored twice where a script compares them: ISO-8601 `*_at` for humans and integer epoch `*_ts` for scripts (`jq 'fromdateiso8601'` / `now`; no `date -d`, §16 #19, #41). All schemas live in `.forge/schemas/*.json` (Forge-owned, jq assertion lists) and `SCHEMAS.md` documents them.

### 5.1 `.forge/STATUS.json` — single source of truth, written only by `.forge/bin/forge-status`

```json
{
  "schema_version": 2,
  "forge_version": "1.0.0",
  "project": "ruggedroute-dataops",
  "updated_at": "2026-10-11T18:42:10Z", "updated_ts": 1760208130,
  "updated_by": { "session_id": "7f2c…", "cmd": "forge-status step-report T-0007 01" },
  "context_state": "fresh",
  "task": {
    "id": "T-0007",
    "title": "nfs_trails: add golden-bbox count QA so the trail tileset can go live",
    "class": "M", "risk": "none", "size_source": "declared",
    "files": ["qa/golden_counts.py", "layers/nfs_trails/layer.json"],
    "creates": ["layers/nfs_trails/tests/test_golden.py"],
    "signals": { "files": 3, "dirs": 2, "importers": 3, "tests_present": false, "risk_hits": [], "important_hits": [] },
    "class_justification": "3 declared files in 2 dirs, one dependent chain, no risk hits; nfs_trails has no tests so the plan adds them first",
    "phase": "execute",
    "plan": ".forge/tasks/T-0007/plan.md", "plan_author": "architect",
    "branch": null,
    "scope": ["qa/golden_counts.py", "layers/nfs_trails/layer.json", "layers/nfs_trails/tests/**"],
    "routing": {
      "mode": "single",
      "builder":  { "agent": "forge-builder",  "model": "opus", "effort": "medium" },
      "verifier": { "agent": "forge-verifier", "model": "opus", "effort": "medium" },
      "justification": "M-small, chain=false, tests added as DoD-1 → opus/medium builder, opus/medium verifier"
    },
    "steps": [
      { "id": "01", "title": "golden-bbox QA for nfs_trails", "agent": "forge-builder", "model": "opus", "effort": "medium",
        "status": "reported", "attempts": 1, "from": null, "verify_attempts": 0,
        "started_at": "2026-10-11T18:30:00Z", "started_ts": 1760207400, "started_by": "7f2c…", "agent_id": "agent_7f3a",
        "base": "3e1f9c2…", "commit": "a91b0e4…", "brief": ".forge/tasks/T-0007/brief-01.md",
        "report": ".forge/tasks/T-0007/report-01.md", "verdict": null, "red_ok_until": null }
    ],
    "escalation": { "step": "01", "round": 0 },
    "next_action": "Dispatch forge-verifier (opus/medium) on step 01: brief-01.md, report-01.md, range 3e1f9c2..a91b0e4.",
    "resume_hint": "Step 01 is reported and committed (a91b0e4). If STATUS shows running with no report and started_by is another session, run .forge/bin/forge-status recover T-0007 01.",
    "evidence_count": 1,
    "evidence": [ { "claim": "lib unit suite green after step 01", "command": "cd lib && python3 -m unittest -v", "exit": 0, "when": "2026-10-11T18:40:02Z", "from": ".forge/tasks/T-0007/checks/01-1760208002-agent_7f3a.json" } ],
    "blocked_on": null, "external": null,
    "budget": { "cap_usd": 10.0 }
  },
  "queue":   [ { "id": "T-0008", "title": "roads_context: client layer manifest", "class_hint": "S" } ],
  "history": [ { "id": "T-0006", "title": "roads_tnm: parse go-pmtiles 1.31 bounds", "class": "S", "outcome": "done", "cost_usd": null, "cost_source": "unknown", "handoff": ".forge/tasks/T-0006/handoff.md" } ]
}
```

Enumerations: `context_state ∈ {fresh, stale}`; `class ∈ {T,S,M,W,L,X}`; `risk ∈ {none, R}`; `phase ∈ {idle, intake, plan, execute, verify, awaiting_external, close, done, blocked}`; `routing.mode ∈ {inline, single, parallel}`; `steps[].status ∈ {pending, running, reported, verifying, done, failed, blocked, awaiting_external}`; `steps[].from ∈ {null, failed, clean}`; `plan_author ∈ {architect, forge-planner}`. **Bounded**: `queue` ≤ 10 entries (the rest in `.forge/queue.jsonl`), `history` = last 5 rows (all rows in `.forge/history.jsonl`), `evidence` = newest 10 (count in `evidence_count`). There is no `spent_usd` in STATUS; spend lives in the ledger (§16 #59, #60).

**Transition table enforced by `forge-status` (refusals are exit 3 with one line on stderr):**

| Command | Precondition (refused otherwise) | Effect |
|---|---|---|
| `open --title --class C --risk R --files p… [--creates p…] --why "…" [--queue]` | `task == null` (or `--queue`); `why ≥ 20`; `C == T` ⇒ `files ≤ 2`; `C ∈ {T,S}` ⇒ `risk_hits = ∅`; `C == S` ⇒ `files ≤ 3 ∧ dirs ≤ 2`; `C == M` ⇒ `files ≤ 10 ∧ dirs ≤ 3`; `R == "R"` ⇔ `risk_hits ≠ ∅` unless `--force-risk`/`--accept-risk-none "<why>"` | `= new + signals + classify`: creates `.forge/tasks/T-NNNN/`, `signals.json`, sets `size_source: declared`, `scope`; T → `execute/inline`; S, X → `plan` (inline plan section required); M/W/L → `plan`; branch only if `git.branch_per_task` |
| `new`, `signals`, `classify` | the three components of `open`, same rules | for re-classification after a plan comes back `needs_clarification` |
| `plan --from plan.md` | `phase == plan`; plan-meta parses (`forge-gate --plan`); S/X ⇒ `mode: inline ∧ steps == []`; M ⇒ `steps.length == 1`; L ⇒ disjoint units; rules §4.3 (1, 2, 4, 5, 11, overrides); risk re-matched on every `allowed_paths` | imports `steps[]`, `routing`, `scope`; `phase: execute`; `needs_clarification ≠ []` ⇒ `phase: intake`, `next_action: "ask the user: …"` |
| `step-start ID [--from failed\|clean] [--agent <id>]` | step `pending`, or `failed` with `--from` given; `attempts < 3` or `ruling.md`; `mode: single` ⇒ no other step `running` | `running`, `attempts += 1`, `from`, `started_at/ts`, `started_by: <session>`, `agent_id: null` (or `--agent`), writes `.forge/tasks/<id>/.base-ID`; `--from clean` runs `recover` first; `--from failed` appends the last verdict to `brief-ID.md §Known failed approaches` |
| `step-report ID --report report-ID.json` | step `running`; report json valid | `reported` (or `blocked`/`needs_context` per `status`); records `commit`; `next_action` names the verifier |
| `step-verdict ID --verdict verdict-ID.json` | step `verifying`; verdict json valid | dispatches: PASS → `step-done`; FAIL (all tags `env-cannot-run`, or pending `external` criteria) → `step-external`; FAIL → `step-fail`; `verify_attempts += 1` |
| `step-done ID` | PASS verdict for this step; `commit` descends from `.base-ID`; `git diff --name-only base..commit ⊆ allowed_paths ∪ .forge/tasks/<id>/**`; T/S/X: `--no-verifier` (T/S only) + a `checks/` record with all exits 0 | `done`; L parallel: merges the unit branch into the main checkout (`--ff-only`, else `--no-ff`) |
| `step-fail ID` | FAIL verdict | `failed`, `escalation.round += 1`, ledger row |
| `step-external ID --needs "<cmds>"` | FAIL with only `env-cannot-run`/external pending | step and phase `awaiting_external`, `external: {step, criteria, needs}`, `next_action` names exactly what the human runs |
| `attest ID DoD-n --by human --evidence <url\|path> [--exit N]` | criterion exists with `check: external`; run by the operator (interactive) | writes `checks/ID-<ts>-human.json` `{source:"human", by, evidence, exit}`; when every pending external criterion is attested → step back to `reported`, `next_action: re-dispatch verifier` |
| `recover ID` | step `running`, `started_by != session` or `--force`, no report | saves `git diff -- <allowed_paths>` to `.forge/incidents/<ts>-<id>-ID.patch`, `git checkout -- <allowed_paths>` to `.base-ID`, `git clean -fd -- <new paths under allowed_paths>`, step `pending` |
| `evidence --claim --from-check f` | check file exists | appends `evidence[]`, `evidence_count` |
| `scope add <path> --why "…"` | class X or `--ruling` | widens `scope` (journaled) |
| `block --on "…"` / `unblock` | any | `phase: blocked` / previous phase |
| `close [--one-line "…"] [--handoff f] [--partial] [--cost usd] [--human-ack "…"] [--accept-out-of-scope "…"]` | every step `done` (or `--partial` + ruling); T ⇒ `--one-line` + a `checks/` record; S/X/M/W/L ⇒ handoff validates (§5.5, short form for S/X); R ⇒ `--human-ack`; **scope backstop**: `git status --porcelain` ∪ `git diff --name-only <task base>..HEAD` ⊆ `scope ∪ .forge/** ∪ CLAUDE.md ∪ .gitignore ∪ .claude/agent-memory/**` else refuse unless `--accept-out-of-scope` + ruling | appends CHANGELOG line, history row (file + last-5 in STATUS), ledger `close` row (`cost_usd: null, cost_source: unknown` unless `--cost`, then `operator`), commits `forge(<id>): close`, `context_state` per `clear_policy`, `task: null` unless queue non-empty |
| `stale` / `fresh [--no-stamp]` | any | flips `context_state`; `fresh` removes `auto-resumed-*`; `--no-stamp` leaves `updated_by` untouched |
| `validate [--restamp]` | — | exit 0/4; `--restamp` re-records the sha after a deliberate hand edit (journaled) |
| `get summary\|resume\|digest\|next_action\|<jq> [--lenient]` | — | read-only; `--lenient` always exits 0 and prints errors as text (for `!` injections) |
| `gate-block ID --agent <id> --gate <name>` | — | increments the block counter, ledger `gate_block` row |

Every write stamps `updated_at/ts`, `updated_by` (session id read from `.forge/.runtime/session-id`, fallback `cli`; §16 #7), rewrites the file atomically (`mv`), records `sha256` (via `sha256sum` or `shasum -a 256`) in `.forge/.runtime/status.sha`, and **removes `.runtime/dirty-main`** (a write to STATUS is what "recording the state" means). `step-report`/`step-fail`/`step-done`/`step-external` also remove `dirty-worker`.

### 5.2 `.forge/binding.json` — thin per-project binding (project-owned)

Worked value for ruggedroute-dataops. Facts verified against the repo on 2026-10-11: `worker-tiles/package.json` has **no** `scripts` key; only `layers/{lands,parcels,roads_tnm}/tests/` exist; the R2 upload and KV alias flip live inside `.github/workflows/*.yml` (no standalone upload scripts); `lib/route_common.py` is imported by 9 modules.

```json
{
  "schema_version": 2,
  "project": "ruggedroute-dataops",
  "stack": "python",
  "bootstrap": "python3 -m pip install -q pytest shapely",
  "verify": [
    { "name": "lib-unit",    "cmd": "cd lib && python3 -m unittest -v", "when": "always" },
    { "name": "layer-tests", "cmd": "pytest layers/{layer}/tests -q", "when": "paths:layers/{layer}/**", "exists": "layers/{layer}/tests", "vars": { "layer": "from-path" } },
    { "name": "worker",      "cmd": "cd worker-tiles && npx wrangler deploy --dry-run", "when": "paths:worker-tiles/**", "todo": "package.json has no test script; replace with a real test command when one exists" }
  ],
  "smoke": "python3 qa/golden_counts.py --help",
  "format": null,
  "test_globs": ["lib/test_*.py", "layers/*/tests/*.py", "worker-tiles/**/*.test.js"],
  "test_pattern": "^\\s*def test_",
  "protected_paths": [".github/workflows/*.yml", "worker-tiles/wrangler.toml", "worker-tiles/src/**"],
  "risk_paths": ["**/*upload*", "**/*alias*", "**/*kv*", "layers/parcels/**"],
  "important_paths": ["layers/mvum/**", "layers/lands/**"],
  "mechanic_denied_paths": ["lib/route_common.py", "lib/normalize_*.py", "layers/*/layer.json", "layers/mvum/**", "layers/lands/**"],
  "risk_words": [
    { "word": "ODbL" }, { "word": "owner", "not": ["ownership"] }, { "word": "alias" }, { "word": "R2" }, { "word": "KV" },
    { "word": "license" }, { "word": "attribution" }, { "word": "secret" }, { "word": "delete" }
  ],
  "irreversible_commands": ["wrangler *", "npx wrangler *", "gh workflow run *", "gh pr merge *", "git push *"],
  "git": { "branch_per_task": false, "commit_prefix": "forge", "worktree_isolation": false },
  "budgets": { "T": 1, "S": 3, "M": 10, "M_chain": 12, "W": 25, "L_unit": 2, "X": 30, "risk_multiplier": 1.5 },
  "routing": { "architect_effort": "medium", "m_builder": "opus-medium", "overrides": [], "measured": {} },
  "clear_policy": "phase",
  "auto_resume": true,
  "driver": { "max_turns": 120, "max_phases": 12 },
  "notes": [
    "Versioned uploads + KV alias flip; never overwrite a PMTiles object in place.",
    "Bulk downloads are the system of record; live ArcGIS is QA only.",
    "Normalizers are tolerant: bad rows go to the review queue, never raise.",
    "OSM-derived layers stay in separate tilesets (ODbL isolation).",
    "Owner names never enter tiles; parcels are geometry-only (apn/county/acres/st).",
    "mvum and lands are LIVE: changes there get a Fable verifier."
  ]
}
```

Semantics: `verify[].exists` — when the substituted path does not exist, `forge-check` records the command as `skipped` (not failed) and the planner is told to add a `tests_present=false` note; `verify[].todo` is printed by `/forge-doctor` as WARN. The installer emits a `verify` entry for `npm test` **only** when `jq -e .scripts.test package.json` succeeds (§16 #18). `clear_policy ∈ {phase, task, never}`. `git.branch_per_task` defaults to `false`: `.forge/` state and code then share one branch and "STATUS is the truth" holds across machines; with `true`, `close` additionally pushes the task branch behind `ask` and records `pushed` (§16 #38). `git.worktree_isolation` may only be flipped to `true` by the operator after `/forge-doctor --worktree` passed. `driver.permission_mode` is gone: `forge-run` always passes `--permission-prompts none` with explicit `--allowedTools` (§13.3).

### 5.3 `.forge/tasks/<id>/plan.md` — written by the architect (S, X, M-small) or `forge-planner` (M-large, W, L)

````markdown
# Execution Plan: T-0007 — nfs_trails golden-bbox QA

```json
{
  "schema": "forge/plan/2",
  "task": "T-0007", "class": "M", "risk": "none", "chain": false,
  "routing": {
    "mode": "single",
    "builder":  { "agent": "forge-builder",  "model": "opus", "effort": "medium" },
    "verifier": { "agent": "forge-verifier", "model": "opus", "effort": "medium" },
    "justification": "3 declared files, 2 dirs, one dependent chain, tests added first → M-small; chain=false → opus/medium"
  },
  "steps": [
    { "id": "01", "title": "golden-bbox QA for nfs_trails", "brief": "brief-01.md", "agent": "forge-builder", "model": "opus", "effort": "medium",
      "mechanical": false, "red_ok_until": null, "max_tool_calls": 60 }
  ],
  "dod": [
    { "id": "DoD-1", "criterion": "WHEN `pytest layers/nfs_trails/tests -q` runs THE SUITE SHALL exit 0 with at least 1 new golden-count test", "check": "pytest layers/nfs_trails/tests -q" },
    { "id": "DoD-2", "criterion": "WHEN the lib unit suite runs THE SUITE SHALL exit 0 (no regression)", "check": "cd lib && python3 -m unittest -v" },
    { "id": "DoD-3", "criterion": "WHEN `python3 qa/golden_counts.py --layer nfs_trails --fixture` runs THE SCRIPT SHALL report 3/3 regions within ±5%", "check": "python3 qa/golden_counts.py --layer nfs_trails --fixture" }
  ],
  "rollback": "git revert <step commit>; no external state is touched",
  "test_baseline": { "files": 11, "tests": 212, "recorded_at": "2026-10-11T18:12:00Z" },
  "needs_clarification": []
}
```

## Steps                      (one `### Step NN` per steps[] entry: File / Action / Details / Verify)
## Validation Criteria        (the DoD-n list in prose, same ids as plan-meta.dod)
## Routing                    (which signals fired; the justification in prose)
## Rollback
<!-- Optional for M; mandatory for W and L: -->
## Objective · ## Current State · ## Target State · ## Tech Stack Context · ## File Manifest · ## Dependency Order · ## Anti-Patterns — DO NOT · ## Escalation Points
````

A DoD criterion may carry `"check": "external", "external": {"what": "GitHub Actions run of quarterly-rec_pois.yml succeeds", "how": "gh workflow run quarterly-rec_pois.yml && gh run watch"}`; the verifier grades it only from a human `attest` record. Plan gate (`forge-gate --plan`, also run by `forge-status plan`): the four mandatory headings (M) or all twelve (W, L); `plan-meta` parses with `schema == "forge/plan/2"`; `dod[] ≥ 1` matching `^DoD-[0-9]+$`; one existing `brief-NN.md` per step whose `brief-meta.step` matches; `max_tool_calls` present per step; every `red_ok_until` names a later step. The planner writes only under `.forge/tasks/<id>/`.

### 5.4 `.forge/tasks/<id>/brief-NN.md` — self-contained worker brief

````markdown
# Brief T-0007/01 — golden-bbox QA for nfs_trails

```json
{
  "schema": "forge/brief/2",
  "task": "T-0007", "step": "01",
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

## Goal
## Context the worker needs      (paths, interfaces, invariants from README design rules, relevant lessons copied in)
## Definition of done            (DoD-n criteria verbatim)
## Out of scope / do not touch
## Known failed approaches       (from lessons; appended by step-start --from failed)
## Output contract
Your final message is the HANDOFF: these `## ` sections in this order — **Where things stand · Done, with evidence · Remaining · Gotchas / do not touch** (mandatory; write `none` rather than omit) and optionally Goal & scope · Decisions & rationale · Failed approaches — do not repeat · Files touched · Verification commands + expected output · Open questions · Bootstrap — followed by one fenced ```json block with schema forge/handoff/2. Run `.forge/bin/forge-check T-0007 01` after your last edit (and `--expect-fail` before implementing, since tdd is true). Pre-validate with `.forge/bin/forge-gate --handoff T-0007 01 --from-file <draft>`; a hook refuses your return until the same check passes. Run every command from the repository root.
````

The fence reads `allowed_paths`, `may_edit_tests`, `owner_agent`, `max_tool_calls`; the spawn guard reads `owner_agent/model/effort` (through STATUS); the handoff gate reads `checks`, `expected_fail_first`, `tdd`, `dod`, `red_ok`. The heading list is in the brief itself so a worker never has to read FORGE.md (§16 #72).

### 5.5 HANDOFF — the worker's final message (persisted to `report-NN.md` + `report-NN.json`); also the shape of the task-level `handoff.md`

Mandatory `## ` headings: **Where things stand · Done, with evidence · Remaining · Gotchas / do not touch**. Optional (M/W/L task handoffs should include them when they carry information): Goal & scope · Decisions & rationale · Failed approaches — do not repeat · Files touched · Verification commands + expected output · Open questions · Bootstrap. Then one fenced JSON block:

```json
{
  "schema": "forge/handoff/2",
  "task": "T-0007", "step": "01",
  "status": "DONE",
  "files_changed": ["qa/golden_counts.py", "layers/nfs_trails/layer.json", "layers/nfs_trails/tests/test_golden.py"],
  "checks_run": [
    { "cmd": "pytest layers/nfs_trails/tests -q", "exit": 1, "expected_fail": true },
    { "cmd": "pytest layers/nfs_trails/tests -q", "exit": 0 },
    { "cmd": "cd lib && python3 -m unittest -v", "exit": 0 },
    { "cmd": "python3 qa/golden_counts.py --layer nfs_trails --fixture", "exit": 0 }
  ],
  "not_verified": ["behaviour with an empty fixture directory"],
  "failed_approaches": ["Querying the live ArcGIS service for counts: throttled after 3 regions; switched to the bulk fixture"],
  "next_action": "none for this step",
  "commit": null
}
```

`status ∈ {DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED, UNVERIFIED}` (`UNVERIFIED` is stamped only by the gate after two blocks). **Gate rules** (`forge-gate --handoff`, identical in the hook): mandatory headings present; JSON parses with `schema`, `task`, `step`, `status`, `files_changed`, `checks_run`; `files_changed ⊆ allowed_paths`; `source_edits(agent_id) ⊆ files_changed` where `source_edits` = `kind: source` edit rows of this agent in `evidence.jsonl`; `tree_changed ⊆ files_changed` where `tree_changed` = `git status --porcelain --untracked-files=all -- <allowed_paths>` paths (so sibling units in a shared tree and pre-existing operator dirt outside the unit never fail a worker; new untracked files count; `.forge/**` and agent memory never count); for `DONE|DONE_WITH_CONCERNS`: every brief `checks[]` cmd has a `checks/<step>-*-<agent_id>.json` record with that cmd at exit 0 (any exit when `red_ok`) whose `ts` is **newer than this agent's last `kind: source` edit row**; `tdd` → each `expected_fail_first[]` cmd has a non-zero record earlier than a zero record. No hedge-word grep on prose (the prompt-level rule stays; §16 #57). On allow the hook commits (§3 step 8) and fills `commit`.

### 5.6 VERDICT — the verifier's final message (persisted to `verdict-NN.md` + `verdict-NN.json`)

Markdown: `## Verdict`, `## Criteria`, `## Scope check`, `## Blocking findings`, `## Deferred findings`, `## Confidence note`. JSON block:

```json
{
  "schema": "forge/verdict/2",
  "task": "T-0007", "step": "01", "range": "3e1f9c2..a91b0e4",
  "verdict": "PASS",
  "criteria": [
    { "id": "DoD-1", "result": "PASS", "cmd": "pytest layers/nfs_trails/tests -q", "exit": 0 },
    { "id": "DoD-2", "result": "PASS", "cmd": "cd lib && python3 -m unittest -v", "exit": 0 },
    { "id": "DoD-3", "result": "PASS", "cmd": "python3 qa/golden_counts.py --layer nfs_trails --fixture", "exit": 0 }
  ],
  "scope_check": "PASS", "ratchet": "PASS",
  "blocking_findings": [], "deferred_findings": ["no negative-longitude fixture"],
  "tags": []
}
```

Gate rules: every brief `DoD-` id appears exactly once with `result ∈ {PASS,FAIL,UNKNOWN}`, `cmd`, numeric `exit`; `verdict: PASS` ⇒ all `PASS` ∧ `scope_check == PASS` ∧ `ratchet == PASS` ∧ `blocking_findings == []`; every cited `cmd` has a `checks/<step>-*-<this agent_id>.json` record, except a criterion whose plan entry is `check: external`, which needs a `checks/<step>-*-human.json` attest record (else `UNKNOWN`); `tags[] ⊆ {skipped-file, no-check-run, not-double-checked, wrong-approach, scope-creep, test-weakened, env-cannot-run}`; `UNKNOWN` on a required criterion ⇒ `FAIL` for R tasks, `DONE_WITH_CONCERNS`-level otherwise; after 2 blocks allow with `verdict` rewritten to `UNKNOWN`. On allow the hook runs `forge-status step-verdict` (§5.1).

### 5.7 Evidence log, check records, attestations (hook- and script-written, committed)

`.forge/tasks/<id>/evidence.jsonl`, appended by `forge-hook` on `PostToolUse` (`Bash|Edit|Write|NotebookEdit`) and `PostToolUseFailure` (`Bash`):

```json
{"ts":1760208002,"agent_id":"agent_7f3a","agent_type":"forge-builder","event":"bash","ok":true,"exit":0,"cmd":".forge/bin/forge-check T-0007 01"}
{"ts":1760207990,"agent_id":"agent_7f3a","agent_type":"forge-builder","event":"edit","kind":"source","file":"qa/golden_counts.py"}
{"ts":1760207980,"agent_id":"main","agent_type":"main","event":"edit","kind":"meta","file":".forge/tasks/T-0007/plan.md"}
```

`kind: meta` for `.forge/**`, `.claude/agent-memory/**`, `CLAUDE.md`, `.gitignore`; everything else `source`. `exit` on bash rows is best-effort (`tool_response` shape undocumented, RCC line 203). **Exact exit codes come from `checks/`**, written by `forge-check`: `.forge/tasks/<id>/checks/<step>-<ts>-<agent_id|main|human>.json`:

```json
{"ts":1760208002,"agent_id":"agent_7f3a","session_id":"7f2c…","task":"T-0007","step":"01","expect_fail":false,
 "results":[{"name":"layer-tests","cmd":"pytest layers/nfs_trails/tests -q","exit":0,"dur_s":4.1,"tail":"12 passed in 4.1s"},
            {"name":"worker","cmd":"cd worker-tiles && npx wrangler deploy --dry-run","status":"skipped","why":"when: paths:worker-tiles/** did not match"}],
 "ratchet":{"baseline_tests":212,"now_tests":213,"deleted_test_files":[],"status":"PASS"}}
```

`agent_id` is stamped by the `PostToolUse(Bash)` hook (which has `agent_id` or, in the main session, `session_id` on stdin) onto the newest record created within 300 s with `agent_id == "unknown"`; a record stamped `main` carries the session id. Human attestations: `{"ts":…,"agent_id":"human","source":"human","by":"riggs","criterion":"DoD-4","evidence":"https://github.com/…/actions/runs/123","exit":0}`.

### 5.8 `.forge/ledger.jsonl` — append-only cost and routing record (committed)

```json
{"ts":"2026-10-11T18:42:10Z","task":"T-0007","step":"01","event":"dispatch","class":"M","agent":"forge-builder","model":"opus","effort":"medium","attempt":1,"escalated_from":null}
{"ts":"2026-10-11T18:58:00Z","task":"T-0007","step":"01","event":"attempt","status":"DONE","gate_blocks":0,"commit":"a91b0e4"}
{"ts":"2026-10-11T19:01:00Z","task":"T-0007","step":"01","event":"verdict","verdict":"PASS","verifier_model":"opus","tags":[],"gate_blocks":0}
{"ts":"2026-10-11T19:05:00Z","task":"T-0007","event":"close","class":"M","outcome":"done","cost_usd":null,"cost_source":"unknown","context_carried":false,"expected_premium":false,"escalations":0}
{"ts":"2026-10-12T02:10:00Z","task":"T-0009","event":"phase","phase":"execute","cost_usd":3.12,"cost_source":"measured","cache_read_share":0.71,"session_id":"c0ffee…"}
```

`cost_source ∈ {measured, operator, unknown}`: `measured` only when `forge-run` or `forge-bench` wrote the row from `total_cost_usd` (RCC line 1103, itself a client-side estimate); `operator` when a human passed `--cost` after reading `/usage` (a slash command the model cannot run, RCC line 374); `unknown` otherwise. `/forge-gc` thresholds use `measured` rows only. `context_carried: true` when the operator skipped the clear.

### 5.9 Lessons, decisions, rulings, history, journal

- `.forge/lessons/<slug>.md`: one lesson per file; line 1 is the summary; a bold first-line tag `type: feedback|project|reference`; `.forge/lessons/INDEX.md` one line per lesson, ≤200 lines, first 40 injected at SessionStart. Rule text in FORGE.md is the Fable memory guidance verbatim.
- `.forge/decisions/NNNN-<slug>.md`: Nygard ADR; numbers never reused; superseded, not deleted. `0001-adopt-forge.md` is written by the installer.
- `.forge/tasks/<id>/ruling.md`: `Decision — Why — Cost if wrong — Evidence considered`.
- `.forge/history.jsonl`, `.forge/queue.jsonl`: the unbounded tails of STATUS `history[]`/`queue[]`.
- `.forge/tasks/<id>/journal.md`: append-only hook log (dispatches, gate blocks with reasons, fence denials, stop blocks, recoveries, compactions, StopFailure, config-change blocks, builtin spawns).
- `.forge/CHANGELOG.md`: one line per closed task, appended by `forge-status close`.

---

## 6. Context-clearing mechanics

What the platform offers, verified: no hook output triggers `/clear` or `/compact` (RCC line 312; REQ line 42). Levers: `SessionStart` sources `startup|resume|clear|compact|fork` with `additionalContext` (≤10,000 chars per string) and `initialUserMessage` (RCC lines 143, 265, 310); `Stop`/`SubagentStop` blocking (RCC lines 156, 159, 301-305; REQ lines 72-73); `PreCompact` blocking (RCC lines 169, 423); disposable contexts via the `Agent` tool (RCC line 103); fresh processes via `claude -p` (RCC §8).

| Layer | Mechanism | Label |
|---|---|---|
| 1. Work never enters the architect's context (M/W/L) | Planning (M-large/W/L), implementation and verification run in `forge-*` subagents; only the final message returns (RCC line 103). The main-session fence makes inline implementation impossible for M/W/L. T/S/X run inline by design (§3), so for those classes the architect's context grows with the work, as the evidence says it should (REQ line 25). | [G] |
| 2. A phase cannot end without STATUS reflecting it | Stop gate (§3 step 12): blocks while `dirty-main` or `dirty-worker` exists or the STATUS sha mismatches; `dirty-main` is set by main-session source mutations (fence allow + `PostToolUse`) and cleared **only** by a writing `forge-status` command; `dirty-worker` is set by a SubagentStop gate whose own `forge-status` call failed and cleared by `step-report\|step-fail\|step-done\|step-external`. No per-prompt `turn` marker and no `rm -f dirty` on prompt submit, so the gate is independent of when a background completion arrives relative to the next prompt (§16 #2, #35). `stop_hook_active` honoured: never re-block on an unchanged sha. 2-block soft cap with `systemMessage` + STALE banner. Fail-open on crash. | [G/cap] |
| 3. The clear itself, interactive | `/forge-close` ends with the CLEAR POINT per `binding.clear_policy`; `forge-status close` sets `context_state: stale`; `UserPromptSubmit` injects a one-line non-blocking reminder while stale. No prompt lock. | [I] |
| 3b. The clear itself, unattended | `.forge/bin/forge-run`: one `claude -p … --model fable --effort <architect_effort> --permission-prompts none --allowedTools <explicit list> --max-budget-usd <remaining> --max-turns <n> --output-format json` per phase until `phase ∈ {done, blocked, awaiting_external}` or `max_phases`. Fresh context is a property of the OS process. Aborts (exit 6) when the JSON result's `permission_denials` is non-empty [observed field; doctor probe]. | [G] |
| 4. Re-injection on next start | `SessionStart` (`startup\|resume\|clear\|compact`): compact STATUS digest (≤3,000 chars, minified fields, last 5 history rows, newest 2 evidence rows, `[full: .forge/STATUS.json]`) → INTERRUPTED/STALE banner → newest handoff *Remaining* + *Gotchas* → `git status --short \| head -20` + `git log --oneline -5` → first 40 lines of `lessons/INDEX.md` → binding digest → VERSION drift; truncated in that order to fit 9,800 chars. `/forge-gc` warns when the STATUS digest exceeds 2,500 chars and fails when it exceeds 3,000. Second handler injects the architect role block when no `agent_type`. | [G] (REQ line 69; RCC lines 265, 310) |
| 5. Auto-resume after clear | On source `clear` only: `task.next_action` non-empty ∧ `context_state == stale` ∧ `binding.auto_resume` ∧ no `.runtime/auto-resumed-<task>-<phase>` → `initialUserMessage` (plain text) + marker; then `forge-status fresh --no-stamp`. Never on `compact` or `startup`. | [U] on `clear` (fallback `/forge-next`; `/forge-doctor --probe-clear` records the observed behaviour) |
| 6. Compaction inside a phase | `PreCompact` matcher `manual`: block while `dirty-main ∨ dirty-worker` with reason "checkpoint with .forge/bin/forge-status, then /compact"; never block `auto` (RCC line 423); no `onFailure: block` (fail open). `SessionStart` `compact` re-injects digest + role. CLAUDE.md carries the Fable six-item retention list [I]. | [G] block; [I] retention |
| 7. Resets as policy, not dogma | `binding.clear_policy: phase\|task\|never`; the ledger's `context_carried` flag lets `/forge-gc` show whether skipped clears cost anything (measured rows only). | [G] data |

Failure modes and mitigations:

| Failure | Detection | Response |
|---|---|---|
| Stop gate blocked 8× with no tool call | platform override (RCC line 305) | soft cap allows at 2; `stale-status` marker → banner; `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` is documented only as raising the cap (RCC line 305), so it is not set |
| Hooks not running (`--bare`, `disableAllHooks`, `--safe-mode`, untrusted plugin form) | `hooks-alive` missing/stale; `/forge-doctor` stream-json probe | `forge-run` aborts before spending (exit 4); doctor red |
| `jq` missing / dispatcher crash | `PreToolUse` and `SubagentStop` carry `onFailure: block` (fail closed: one denied call or one blocked return); `Stop`, `PreCompact`, injection hooks fail open with `systemMessage` | never an 8× Fable resend loop (§16 #14, #39) |
| Headless permission denial | `permission_denials` non-empty in `claude -p` JSON [observed] | `forge-run` exit 6, ledger row `denied_tools`; `/forge-doctor --driver` runs one trivial phase and asserts an empty array |
| Wrong model in driver/interactive | `/forge-doctor` asserts `modelUsage` names `claude-fable-*` [observed]; settings `model: fable` | FAIL line with remedy |
| `initialUserMessage` ignored on `clear` | nothing auto-submits | digest names `next_action`; operator types `/forge-next` |
| Operator never clears | `context_carried: true` on the next close row | correctness unaffected; cost visible only in measured rows |
| Session dies mid-step | `StopFailure` → `.forge/incidents/<ts>-stopfailure.json`; `SessionEnd` (timeout 5 s) → `last-session.json`; next SessionStart sees `started_by != session_id` and no report | banner + `resume_hint`; `recover` |
| Spawn allowed but the Agent call failed to start | step `running`, `agent_id: null`, no evidence rows after `started_ts` | banner; `step-start --from clean` or `recover` |
| Over-long injection | truncation in the documented order with `[truncated: read <path>]` | architect reads the file |
| Worktree-isolated worker | `CLAUDE_PROJECT_DIR` inside a worktree subagent is [U]; the hook resolves the main checkout from `git rev-parse --path-format=absolute --git-common-dir` for all `.forge/` writes regardless | `worktree_isolation` stays off until `/forge-doctor --worktree` shows the probe's HEAD equals the current HEAD and `.forge/` writes landed in the main checkout |
| Policy file edited mid-session | `ConfigChange` (matcher `project_settings\|local_settings`) compares hook entries with the fragment | blocks the reload (RCC line 163), journals; `/forge-doctor` diffs |

---

## 7. Verification and gates

Order of authority (RP §4 rec. 1): deterministic checks → hook-audited evidence → fresh-context verifier → architect adjudication → human gate. Prose is advisory; hooks and scripts are the law.

| # | Gate | What it checks | Enforced by | Label |
|---|---|---|---|---|
| 0 | **Plan gate** | Plan exists with the mandatory headings for its class, parseable `plan-meta`, ≥1 `DoD-`, one valid brief per step, `max_tool_calls` per step, rollback for R, baseline recorded; routing obeys §4.3; M has one step; risk re-matched on every brief's paths; `red_ok_until` points forward | `SubagentStop` (`^(forge:)?forge-planner$`) + `forge-status plan` (+ `forge-gate --plan` for the architect's own plans) | [G] |
| 1 | **Plan-first / scope fence (main session)** | No source `Edit\|Write\|NotebookEdit` without an open task, ever for M/W/L, before `plan.md` for S/X, outside the declared `scope` for T/S/X; Bash mutation heuristic under the same conditions; three same-rule denials in a turn → `continue: false` | `PreToolUse` | [G] tool edits; [G at close] shell writes (gate 8 backstop) |
| 2 | **Scope fence (workers)** | Edits only inside `allowed_paths`; existing tests only with `may_edit_tests`; protected/risk/mechanic-denied paths by tier; `.forge/**` never; must be bound to a running, unbound brief of its own role | `PreToolUse` inside subagents (`agent_id`/`agent_type`, RCC line 194) | [G] |
| 2b | **Tool budget** | Bash/Edit/Write denied once this agent's `bash\|edit` evidence rows exceed `brief.max_tool_calls` ("write your HANDOFF with status BLOCKED") | `PreToolUse` | [G] |
| 2c | **Read-only roles** | `forge-scout`, `forge-verifier`, `forge-planner`: Bash **allow-list** (`git log\|grep\|diff\|show\|status\|rev-parse\|ls-files`, `rg`, `grep`, `find`, `ls`, `cat`, `head`, `tail`, `wc`, `jq`, `pytest`, `python3 -m pytest\|unittest`, `.forge/bin/forge-check`, `.forge/bin/forge-gate`, `binding.verify[].cmd` prefixes, `cd <dir> && <allowed>`); interpreters with `-c`/`-e`, heredocs, redirects never allowed; Edit/Write denied except the verifier's own memory directory | `PreToolUse` (`Bash`, `Edit\|Write`) | [G] |
| 3 | **Mechanical checks with exact exit codes** | `forge-check` runs `binding.verify[]` (filtered by `when`, `exists` → `skipped`) ∪ brief `checks[]`, prints one `FORGE_CHECK name=… exit=…` line per command, writes the `checks/` record, runs the test ratchet vs `plan-meta.test_baseline` | script | [G] |
| 4 | **Evidence capture** | Every Bash/Edit/Write tool event with `agent_id`, `kind`, success and failure | `PostToolUse` + `PostToolUseFailure` | [G] |
| 5 | **Handoff gate** | §5.5: shape, agent-local scope evidence, checks after the last source edit, red-then-green, two-block cap → `UNVERIFIED`; commits and records on allow | `SubagentStop` (builders), `onFailure: block` | [G] |
| 6 | **Fresh-context verifier** | Brief + DoD + committed range + report; re-runs `forge-check`; grades each `DoD-` id; `scope_check`, `ratchet`; "flag only gaps that affect correctness or the stated requirements" (RP §4 rec. 7); `env-cannot-run` tag | agent body [I] + verdict gate [G] | [G] shape, [I] judgment |
| 7 | **Verdict gate** | §5.6 incl. DoD coverage, verifier-owned or human-attested check records; runs `step-verdict` on allow | `SubagentStop` (`^(forge:)?forge-verifier$`), `onFailure: block` | [G] |
| 8 | **Transition guard + scope backstop** | `step-done` without PASS impossible; commit must descend from the step base and touch only `allowed_paths ∪ .forge/tasks/<id>/**`; `plan` with illegal routing impossible; `close` with a non-done step, out-of-scope tree or committed changes impossible without `--accept-out-of-scope` + ruling | `forge-status` | [G] |
| 9 | **Spawn routing guard** | `forge-*` spawns must match a pending step (or a pre-started retry); verifier only on a `reported` step with `verify_attempts < 2`; planner only in `phase: plan`; alias-normalized; runs `step-start`/sets `verifying` on allow; `general-purpose` denied in settings; builtin spawns journaled | `PreToolUse` (`Agent`) + `permissions.deny` | [G] |
| 10 | **Risk / human gate** | `irreversible_commands` → `ask` for the main session in interactive mode; `deny` for subagents always and for the main session in driver mode (`forge-run` refuses the phase: `blocked`, `blocked_on: "human gate"`); `close --human-ack` for R | `PreToolUse` (`Bash`) + settings + `forge-run` + `forge-status` | [G interactive / blocked in driver] |
| 11 | **Stop gate** | STATUS reflects every mutation; chat exemption; `stop_hook_active`; 2-block soft cap; fail-open | `Stop` | [G/cap] |
| 12 | **Claims audit** | `forge-status evidence` accepts only claims pointing at a `checks/` record; `close` refuses a handoff whose *Done, with evidence* bullets lack a command, and a T `--one-line` without a check record | script | [G] |
| 13 | **External verification path** | `check: external` criteria pass only on a human `attest` record; `phase: awaiting_external` holds the task with the exact commands to run | `forge-status attest` + verdict gate | [G] |
| 14 | **Policy-file lock** | Model edits (main session and every subagent) to every path in `install-manifest.json`, `.claude/settings*.json`, `.forge/binding.json`, `.forge/schemas/**`, `.forge/ledger.jsonl`, `.forge/history.jsonl` denied ("Forge-owned or policy file: change it with install.sh or by hand"); `ConfigChange` blocks a reload that drops or alters a Forge hook entry; `/forge-doctor --disable-gate <name>` is the journaled bypass | `PreToolUse` + `ConfigChange` + settings `deny` | [G] |
| 15 | **System self-check** | `/forge-doctor`: hooks alive, `jq`, bash version (WARN < 4), CLI ≥ 2.1.295, trust state, binding valid, STATUS valid, settings diff, duplicate agents (filesystem), FORGE.md pointer check, optional model probes (`--driver`, `--probe-clear`, `--worktree`, `--probe-maxturns`) | script | [G] |

Definition of done is written **before code** as EARS-style criteria with a stated check (RP §4 rec. 3) and carried by id from plan → brief → verdict. Not used as gates, on purpose: `TaskCompleted`/`TeammateIdle` (teams experimental, interactive-only, RCC §9), `/goal` (optional, RUNBOOK), transcript grepping (undocumented), `context: fork` skills (undocumented `agent_type`), saved workflows in the core.

---

## 8. File layout

### 8.1 The Forge source repository (`forge/`, canonical; also a marketplace)

```text
forge/
├── VERSION                          # 1.0.0 (single source; plugin.json version generated from it)
├── CHANGELOG.md  README.md  install.sh
├── payload/                         # PRIMARY shipped form: copied verbatim into consumers
│   ├── .forge/
│   │   ├── FORGE.md  RUNBOOK.md  ROUTING.md  HOOKS.md  SCHEMAS.md  GATES.md  ROLE-architect.md  VERSION
│   │   ├── bin/forge-hook forge-status forge-check forge-gate forge-run forge-doctor forge-bench
│   │   ├── bin/lib/common.sh json.sh gates.sh glob.sh aliases.sh
│   │   ├── schemas/status.json binding.json plan.json brief.json handoff.json verdict.json routing.json ledger.json
│   │   └── templates/STATUS.json binding.json plan.md plan-inline.md brief.md handoff.md handoff-short.md verdict.md lesson.md adr.md ruling.md CLAUDE.fragment.md
│   ├── .claude/
│   │   ├── agents/forge-scout.md forge-planner.md forge-builder.md forge-builder-wide.md forge-builder-s.md forge-mechanic.md forge-verifier.md forge-librarian.md
│   │   ├── skills/forge-task/ forge-next/ forge-close/ forge-investigate/ forge-doctor/ forge-gc/   (SKILL.md each)
│   │   ├── rules/stacks/forge-stack-python.md forge-stack-kotlin-android.md forge-stack-web-ts.md forge-stack-unknown.md
│   │   └── settings.forge.json      # hooks + permissions + env + model + effortLevel fragment, merged by install.sh
├── plugin/                          # SECONDARY user-level form, GENERATED by `make plugin` (committed, CI-diffed)
│   ├── .claude-plugin/plugin.json  agents/  skills/  bin/  hooks/hooks.json
├── .claude-plugin/marketplace.json
├── migrations/0001-example.sh
├── evals/tasks/*.json  evals/README.md
├── tests/*.bats                     # hook, forge-status, forge-gate tests; tests/examples.bats re-runs every worked example in this document through `forge-status open` rules
├── docs/ARCHITECTURE.md UPGRADING.md DESIGN-RATIONALE.md adr/
└── .github/workflows/validate.yml   # shellcheck --shell=bash; bats on ubuntu AND macos (bash 3.2 syntax target); claude plugin validate --strict ./plugin; payload/plugin diff
```

`plugin/hooks/hooks.json` is generated from the same event map with every command `"${CLAUDE_PLUGIN_ROOT}"/bin/forge-hook --plugin`; the SubagentStop matchers are regexes that match both the bare and the `forge:`-prefixed agent ids (RCC lines 121, 139), and `forge-hook` strips a `forge:` prefix when resolving roles. `forge-hook --plugin` exits 0 immediately when `"$CLAUDE_PROJECT_DIR/.forge/VERSION"` exists, so a user-level install never double-fires inside a vendored repo. The plugin form needs workspace trust (REQ line 69) and is for developer machines only.

### 8.2 A consumer repo after `install.sh` (ruggedroute-dataops)

```text
ruggedroute-dataops/
├── CLAUDE.md                         # Forge fragment between <!-- forge:begin --> … <!-- forge:end -->
├── .claude/
│   ├── settings.json                 # merged: model, effortLevel, hooks, permissions, env, plansDirectory, subagentPromptCacheTtl, worktree
│   ├── agents/forge-*.md             # Forge-owned (8)
│   ├── skills/forge-*/SKILL.md       # Forge-owned (6)
│   ├── rules/forge-stack-python.md   # Forge-owned, path-scoped
│   ├── rules/project-*.md            # project-owned (optional)
│   └── agent-memory/forge-verifier/MEMORY.md   # project-owned, committed, ≤60 lines
├── .forge/
│   ├── FORGE.md RUNBOOK.md ROUTING.md HOOKS.md SCHEMAS.md GATES.md ROLE-architect.md VERSION   # Forge-owned
│   ├── bin/ schemas/ templates/      # Forge-owned
│   ├── install-manifest.json         # Forge-owned: sha256 of every Forge-owned file (also the policy-lock list)
│   ├── binding.json                  # project-owned, policy-locked (edit by hand / install.sh)
│   ├── STATUS.json ledger.jsonl history.jsonl queue.jsonl CHANGELOG.md COST-REPORT.md   # project-owned
│   ├── tasks/T-0007/{plan.md,brief-01.md,report-01.md,report-01.json,verdict-01.md,verdict-01.json,evidence.jsonl,checks/,journal.md,handoff.md,.base-01,ruling.md?}
│   ├── lessons/INDEX.md <slug>.md    # project-owned
│   ├── decisions/0001-adopt-forge.md # project-owned
│   ├── archive/                      # project-owned (GC moves old tasks here)
│   ├── incidents/                    # gitignored
│   └── .runtime/                     # gitignored: session-id hooks-alive dirty-main dirty-worker chat-turn stop-blocks last-block.sha status.sha stale-status denials agents/ auto-resumed-* last-session.json phase-costs.jsonl
├── .gitignore                        # += .forge/.runtime/ .forge/incidents/
└── lib/ layers/ qa/ worker-tiles/ .github/ … untouched
```

**Ownership is the upgrade contract.** Forge-owned files are overwritten on upgrade (three-way diff warning when the local sha differs from `install-manifest.json`); project-owned files are never touched except by an idempotent migration on a `schema_version` bump; `settings.json` is merged with `jq`, and only hook entries whose `command` starts with `"$CLAUDE_PROJECT_DIR"/.forge/bin/` are replaced. The manifest doubles as the policy-lock list for gate 14.

---

## 9. Documentation set

| File | Purpose | Reader | Updated when |
|---|---|---|---|
| `CLAUDE.md` fragment (6 lines) | Always-loaded pointer: Forge installed, STATUS is the truth, three commands, read FORGE.md | every session (workers with `omitClaudeMd` skip it) | install/upgrade |
| `.forge/FORGE.md` (≤120 lines) | **Entrypoint.** Bootstrap order; the three rituals and CLEAR POINT; evidence rule; handoff/verdict shapes; retention list; pointers | fresh session; humans | Forge upgrade |
| `.forge/ROLE-architect.md` | Architect role block, injected verbatim | main session; humans | Forge upgrade |
| `.forge/RUNBOOK.md` | Operate and troubleshoot: daily loop, driver mode, blocked/awaiting_external tasks, dead session recovery, stale STATUS, trust and permission prompts, `/effort medium` for X, raising the stop cap, `claude --debug`, upgrade | operator; architect when stuck | Forge upgrade; project appendix project-owned |
| `.forge/ROUTING.md` | §4 with rationale, signals, rules, ladder, re-sweep checklist | humans; architect re-sweep | Forge upgrade |
| `.forge/schemas/routing.json` | The matrix as data (~600 tokens): what `forge-status` and the planner read | scripts, planner | Forge upgrade |
| `.forge/HOOKS.md` | Per hook: event, matcher, stdin consumed, stdout, exit codes, `onFailure`, one `echo '{…}' \| .forge/bin/forge-hook` test line; the never-fail rule for `!` injections | maintainers, doctor | hook change |
| `.forge/SCHEMAS.md` + `schemas/*.json` | Every §5 schema with jq snippets | agents, scripts | schema change = MAJOR |
| `.forge/GATES.md` | Every gate, its label, the bypass (`/forge-doctor --disable-gate <name>`, journaled); the heuristic status of the Bash guards; "full-suite results are authoritative only from the final spot-check" for L | architect, humans | Forge upgrade |
| `.forge/STATUS.json` | Where we are | injected every start | every transition (gated) |
| `.forge/tasks/<id>/*` | Plan, briefs, reports, verdicts, evidence, checks, journal, handoff, ruling | next role; auditors | task lifecycle; immutable after close |
| `.forge/ledger.jsonl`, `COST-REPORT.md` | Routing/cost record (`measured`/`operator`/`unknown`) and its rollup | `/forge-gc`, operator | every transition; GC |
| `.forge/lessons/`, `decisions/`, `CHANGELOG.md`, `history.jsonl` | Memory surface, ADRs, lab notes, full history | SessionStart (INDEX head), planner, humans | close; GC |
| `.claude/agent-memory/forge-verifier/MEMORY.md` | Verifier calibration notes (≤60 lines, linted by GC for imperative text) | verifier | by the verifier |
| `.claude/rules/forge-stack-*.md` | Path-scoped stack rules (RCC lines 473-495) | whoever touches matching files | Forge upgrade |
| Forge repo `CHANGELOG.md`, `VERSION`, `docs/UPGRADING.md` | System versioning | operator before upgrading | each release |

**Cold-start acceptance test** (deterministic, run by `/forge-doctor` and `/forge-gc`): `forge-doctor --pointers` checks that every path FORGE.md names exists, that FORGE.md's bootstrap order equals the SessionStart digest order, and that the `/forge-*` commands it lists exist as skills. Optional model probe (`--probe-coldstart`): `claude -p "Read .forge/FORGE.md and state the next action in one line" --model haiku --settings '{"disableAllHooks":true}' --output-format json` must return `STATUS.task.next_action` — isolated from the hook so it measures the document, not the injection (§16 #49).

**Garbage collection** (`/forge-gc` → `Agent(subagent_type: "forge-librarian")`): contradiction scan between CLAUDE.md, FORGE.md, binding `notes` and lessons; lessons dedupe/delete-wrong with a replacement; INDEX ≤200 lines; archive tasks closed >60 days to `.forge/archive/`; verifier MEMORY.md ≤60 lines and no imperative sentences; STATUS digest size check; ledger rollup over measured rows with unmeasured counts; pointer check; VERSION drift report.

---

## 10. Install, bootstrap, upgrade

### 10.1 Install (one command, any repo)

```bash
curl -fsSL https://raw.githubusercontent.com/<owner>/forge/v1.0.0/install.sh | bash -s -- --tag v1.0.0
# or from a local clone:  bash ~/src/forge/install.sh --target . --tag v1.0.0 [--effort low|medium] [--no-model] [--with-bench]
```

`install.sh` (bash 3.2-compatible + jq + curl/tar or git; idempotent):
1. Fetches `payload/` at the tag (`git archive` over https or the release tarball; sha256 recorded). Refuses without `jq`; prints `brew install bash jq` / `apt install jq` remedies.
2. Copies Forge-owned files, `chmod +x .forge/bin/*`; refuses to overwrite a Forge-owned file whose sha differs from `install-manifest.json` unless `--force`.
3. Merges `.claude/settings.forge.json` into `.claude/settings.json` with `jq` (arrays union; Forge hook entries replaced by command-path prefix; non-Forge entries kept). Writes `model: "fable"` (unless `--no-model`), `effortLevel` from `--effort` or `binding.routing.architect_effort` (default `medium`), `plansDirectory`, `subagentPromptCacheTtl: "1h"`, `worktree.baseRef: "head"`, `env` (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "2"`, `CLAUDE_CODE_SUBAGENT_MODEL: "sonnet"`, `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR: "1"`), `permissions.allow` for `.forge/bin/*` and for each `binding.verify[].cmd` prefix, `permissions.deny` (`.env` reads, force pushes, `Agent(general-purpose)`, model edits to `.claude/settings.json`), `permissions.ask` (`git push *`, `gh pr merge *`, `gh workflow run *`, `wrangler *`, `npx wrangler *`). Prints the trust caveat: project `allow` rules apply only after the workspace trust dialog (RCC line 973), so an untrusted session prompts once per script call until trusted.
4. Appends the CLAUDE.md fragment between markers.
5. Stack detection → `binding.json`: `pyproject.toml|requirements*.txt|lib/*.py` → python verify commands (per-layer entries carry `exists`); `package.json` → `npm test` **only if** `jq -e .scripts.test` succeeds, else a `todo` entry; `build.gradle(.kts)` → `./gradlew :app:testDebugUnitTest`; none → `stack: "unknown"` and the first queued task is `T-0001 stack discovery`. Seeds `protected_paths` (CI, deploy configs), `risk_paths`, `important_paths` and `mechanic_denied_paths` from README hints (`LIVE`, "shared", "all … share") with `TODO` markers. Installs the matching `forge-stack-*.md` rule.
6. Writes idle `STATUS.json`, empty `ledger.jsonl`/`history.jsonl`/`queue.jsonl`, `CHANGELOG.md`, `lessons/INDEX.md`, `decisions/0001-adopt-forge.md`, `.forge/VERSION`, `install-manifest.json`; gitignores `.forge/.runtime/` and `.forge/incidents/`.
7. If `claude` is on PATH: `forge-doctor --report --no-probes`, then the hooks-alive probe; prints "Commit these files, then open Claude Code and run `/forge-task <first task>`."

Why not `extraKnownMarketplaces`/`enabledPlugins`: cloud sessions never add marketplaces and project-enabled external plugins are not fetched for collaborators (RCC lines 820, 835; REQ line 47); the in-repo plugin form needs trust (REQ line 69).

### 10.2 Bootstrap a fresh session

Nothing to run (§14). Local, cloud and headless sessions are identical because every piece is a plain project file or a project `settings.json` hook (REQ lines 64, 69, 74). On an untrusted cloud container the operator sees one permission tap per script call until trust is accepted; hooks fire regardless.

### 10.3 Upgrade

`bash install.sh --upgrade --tag v1.1.0 [--dry-run]`: reads `.forge/VERSION`; applies `migrations/` in order (idempotent; only a `schema_version` bump may touch project-owned files); overwrites Forge-owned files (three-way diff warning for locally modified ones); re-merges settings; rewrites `install-manifest.json` and `.forge/VERSION`; prints the CHANGELOG delta; runs `forge-doctor`. Semver: **MAJOR** = STATUS/handoff/brief/binding schema change; **MINOR** = additive agent/skill/hook/rule; **PATCH** = prompt or doc text. Agent and skill names are permanent. Nothing auto-updates (RCC line 866); `/forge-doctor` warns when `.forge/VERSION` lags `binding.forge_pin`.

### 10.4 The three consumer bindings (worked)

- **ruggedroute-dataops**: §5.2 verbatim.
- **RuggedRoute Android**: `verify: ["./gradlew :app:testDebugUnitTest", "./gradlew :app:compileDebugKotlin"]`, `smoke: "./gradlew :app:assembleDebug"`, `test_globs: ["app/src/test/**/*.kt"]`, `test_pattern: "^\\s*@Test"`, `protected_paths: ["app/google-services.json", "**/signing*", "app/src/main/res/values/tokens*.xml"]`, `risk_paths: ["**/firebase/**", "**/billing/**", "**/auth/**"]`, `mechanic_denied_paths: ["app/src/main/java/**/ui/**"]`, `irreversible_commands: ["./gradlew publish*", "./gradlew bundleRelease", "fastlane *"]`, `routing.overrides: [{"name":"ui-compose","paths":["app/src/main/java/**/ui/**/*.kt"],"builder":{"agent":"forge-builder","model":"opus","effort":"medium"},"min_verifier":"opus"}]`. UI criteria that need an emulator are planned as `check: external` with `how: "./gradlew connectedDebugAndroidTest on a local device"`; in a cloud container the verifier tags them `env-cannot-run`, the task parks in `awaiting_external`, and the operator attests from a local run (§16 #31, #64).
- **Millwright KB** (unknown stack): `stack: "unknown"`; every source path is S-gated until `T-0001 stack discovery` fills `verify[]`; the verifier refuses to PASS a criterion without a check command.

---

## 11. Cost model

Prices (REQ line 13): Fable $10/$50, Opus $4/$20, Sonnet $2/$10, Haiku $0.10/$0.50 per MTok in/out. **Method (§16 #51):** every row is `Σ(model calls × average context tokens) × input price + output tokens × output price`, because input is billed per call and every tool call resends the whole context. Two columns are shown with the **same assumption applied to both arms**: *list* (no cache) and *cached* (80% of input tokens are cache reads billed at 10% of the input price, i.e. effective input = 0.28 × list; requires the 1-hour subagent cache TTL the design sets, since a `forge-check` run longer than 5 minutes would otherwise expire the cache, §16 #61). The baseline is **one Fable session at `low` effort** doing the whole task in one growing context (REQ line 25). Call counts and contexts are planning assumptions; `forge-bench` and measured ledger rows replace them.

| Shape (ruggedroute-dataops) | Solo Fable `low` — list / cached | Forge v2 — composition — list / cached | Delta (cached) and reading |
|---|---|---|---|
| **T** README/config tweak | 4 calls × 25K + 2K out → **$1.10 / $0.38** | architect 6 × 28K + 3K (open, edit, check, close) → **$1.83 / $0.62** | +$0.24: the price of a status trail and a check record; two script calls, no handoff |
| **S** one-normalizer fix, tests exist | 8 × 35K + 8K → **$3.20 / $1.18** | architect 11 × 36K + 9K ($4.41 / $1.56) + Sonnet verifier 8 × 30K + 3K only when tests changed ($0.51 / $0.16) → **$4.92 / $1.72** | +$0.54: inline plan section, verifier, short handoff; S is a trail-and-verifier buy, not a saving |
| **M-small** 3 files, one chain | 20 × 50K + 35K → **$11.75 / $4.55** | architect 11 × 35K + 8K ($4.25 / $1.48) + Opus builder 30 × 45K + 30K ($6.00 / $2.11) + Opus verifier 12 × 35K + 5K ($1.78 / $0.57) → **$12.03 / $4.16**; with 25% expected escalation (Fable-low re-run $15.0 / $5.28 + re-verify) → **$16.2 / $5.6 expected** | parity to +23%: fresh verifier and clean architect context at roughly the solo price. The `chain` route (Fable-low builder) prices at $21 / $7.3 on the same token assumptions, so it is **not** the default; rule 10 flips it only on ≥10 measured rows |
| **M-large** planner fork | ~same as M-small solo or more | architect 9 × 35K + 5K ($3.40 / $1.13) + planner `fable/medium` 15 × 40K + 8K ($6.40 / $2.08) + builder + verifier ($7.78 / $2.68) → **$17.6 / $5.9** | +30%: the planner is the overhead; it is forked only above 5 files or 2 dirs |
| **W** 40-file token migration | 80 × 120K + 120K → **$102 / $32.9** | architect 12 × 35K + 6K ($4.50 / $1.48) + planner `fable/high` 25 × 50K + 12K ($13.1 / $4.1) + `forge-builder-wide` 80 × 100K + 100K ($85 / $27.4) + Fable verifier 15 × 50K + 6K ($7.8 / $2.4) → **$110 / $35.4** | +8%: a plan and a fresh verifier for the price of the handoff; `expected_premium: true` |
| **L** 6 disjoint per-layer units | 50 × 80K + 100K, two compactions → **$45 / $16.2** | architect 21 × 40K + 15K ($9.15 / $3.10) + planner `fable/high` ($13.1 / $4.1) + 6 Sonnet builders 25 × 35K + 12K ($11.2 / $3.66) + 6 Sonnet verifiers 10 × 30K + 3K ($3.8 / $1.2) + Fable spot-check ($7.8 / $2.4) + 20% retries ($3.0 / $1.0) → **$48 / $15.5** | parity (−4% cached, +7% list): the cheap tiers pay for the planner, spot-check and handoffs. The Forge wins outright only when the solo run would lose state across compactions and redo work, or when wall-clock matters (parallel with worktrees). The v1 claim of "~55% cheaper" is withdrawn |
| **X** root cause across the pipeline, inline | 50 × 80K + 50K → **$42.5 / $13.7** | architect inline 55 × 82K + 55K ($47.8 / $15.4) + Fable verifier ($7.8 / $2.4) → **$55.6 / $17.8** | +30% by design: the investigation is paid once (not three times as in v1), plus a fresh verifier; `expected_premium: true` |
| **R-small** workflow + upload change, inline | 10 × 35K + 10K → **$4.0 / $1.48** | architect at `medium` 12 × 40K + 12K ($5.4 / $1.94) + Fable verifier 10 × 35K + 4K ($3.7 / $1.18) + human ack → **$9.1 / $3.1** | ×2.1: the tail is priced, not hidden (RP §3 T2MO); strongest model + human review of the diff |
| **Driver mode**, per phase | — | bootstrap ~5 calls × 8K + 1K out → **+$0.45 / +$0.16 per phase**; a typical M is 3-4 phases | +$0.6 cached per M in exchange for measured cost rows and process-boundary clearing |

Fixed overhead: SessionStart digest ≤9,800 chars (~2.5K tokens) + role block (~1.2K) per start/clear/compaction; one-line prompt reminder per turn; hook scripts cost zero tokens. Compared with v1, each M step saves ~6 architect calls (signals, step-start, step-report, verifier bookkeeping, step-done, commit) ≈ $2.1 list / $0.6 cached, because hooks and `forge-status open` do them.

Where the run-time savings the user asked for come from, in order and honestly: (1) bookkeeping moved from Fable turns into zero-token hooks; (2) the architect runs at `medium` and the bookkeeping skills at `low` (§13.2) instead of Fable's default `high`; (3) the 1-hour cache TTL on every worker; (4) cheap tiers on plan-proven disjoint units; (5) no redo of work lost to dead sessions or compaction (`incidents/`, committed steps); (6) the close ritual sized to the class. Where the Forge costs more, by design: T/S (a trail and a verifier for a few tens of cents), X and R (fresh verification of the riskiest work).

**Measurement (core, always on):** every `close` row carries `cost_usd` + `cost_source ∈ {measured, operator, unknown}`; driver and bench rows are `measured` from `total_cost_usd` (RCC line 1103) and carry `cache_read_share`; interactive rows are `unknown` unless the operator passes `--cost` after reading `/usage`. **Measurement (optional add-on):** `forge-bench <taskset>` runs 20-50 real tasks twice (driver arm vs `claude -p --model fable --effort low --max-budget-usd <cap>`), reports pass rate beside cost per passed task by class, and the cache-read share so the 80% assumption above is checked. `/forge-gc` proposes threshold flips as ADRs only from measured rows.

---

## 12. Risks, unknowns, and conflict resolutions

### 12.1 Judge and red-team conflicts resolved by evidence

| Conflict | Resolution | Evidence |
|---|---|---|
| Architect role: unscoped rule vs `--agent` vs SessionStart block | SessionStart `additionalContext` gated on absent `agent_type`, re-run on `compact`; readable `.forge/ROLE-architect.md` | RCC lines 44, 95, 265, 416, 476 |
| One builder file vs tier-per-file | Four builder files (`forge-builder` Opus/Fable, `forge-builder-wide`, `forge-builder-s`, `forge-mechanic`) | hooks see `agent_type`, never the model (RCC line 194); `maxTurns` is frontmatter-only (RCC line 38) |
| Planner/verifier via `context: fork` skills vs the `Agent` tool | `Agent` tool only; no fork skills | `agent_type == name` verified only for Agent-tool spawns (REQ line 73); fork `agent_type` undocumented (RCC lines 538-540); no per-invocation model on fork skills (RCC line 536) |
| M as per-step workers vs one builder | Exactly one step, one builder, one verifier; multi-step is L | REQ line 25; Cognition (RP §2); gates are per step (§16 #63) |
| M default builder: Opus (v1) vs Fable-low (red team #55) | Opus/medium stays the default; accounting corrected; ledger flip symmetric | REQ line 6 (user intent: Opus for easier tasks); RP §3 matrix (Opus medium for well-specified multi-file work, Fable low "if measured cheaper"); §11 chain route prices higher on equal token assumptions |
| X in a planner+builder split vs inline | Inline in the architect with a fresh Fable verifier | REQ line 6; REQ line 25; RP §2 Cognition; RP §3 matrix hands Fable ambiguous/root-cause work |
| Evidence audit: transcript vs evidence.jsonl vs headings | evidence.jsonl for ordering + `forge-check` records for exit codes + git commits by the gate | transcript undocumented; `tool_response` exit undocumented (RCC line 203) |
| Verifier diff: working tree vs committed range | Handoff gate commits; verifier diffs `base..commit` | §16 #25, #37: uncommitted edits made the v1 diff empty and the recorded SHA wrong |
| Stop gate: `onFailure: block` vs fail-open | Fail-open on `Stop`/`PreCompact`; fail-closed on `PreToolUse`/`SubagentStop` | RCC line 305 8-cap × full-context resends (§16 #14, #39) |
| L parallel in a shared tree vs worktrees vs sequential | Sequential default; parallel only with proven worktrees; per-step bases; unit-scoped gates | RCC line 45 (worktree base), RCC line 95 (overwrites), §16 #8, #28, #53 |
| Budget visibility to the model | Removed from reminder and Stop; caps enforced out of band | RP §1/§2 context anxiety (§16 #60) |
| `permissionDecision: "ask"` as the driver's human gate | `deny` + `blocked` in driver; `ask` interactive only | RCC line 1070 (§16 #22) |
| Plugin vendored under project `.claude/skills/forge/` as primary | Plain layout primary; plugin wrapper user-level, self-silencing | REQ lines 63, 68, 69 |
| State on per-task branches | `branch_per_task: false` default | §16 #38 (cross-machine truth, merge conflicts) |

### 12.2 Unknowns and their fallbacks

1. **`initialUserMessage` on source `clear`** [U]: documented field (RCC line 265), not exercised for `clear`. Fallback `/forge-next`; `/forge-doctor --probe-clear`.
2. **`permission_denials` and `modelUsage` in `claude -p` JSON** [observed in this sandbox, not in RCC]: `forge-run` and the doctor read them defensively (`// empty`); absence is reported as WARN, never assumed as success.
3. **`tool_response` shape for Bash** [U]: exit code best-effort; exact codes from `forge-check`.
4. **Whether a non-zero Bash exit fires `PostToolUse` or `PostToolUseFailure`** [U]: both registered.
5. **`agent_type`/`agent_id` in `PreToolUse` stdin inside subagents**: documented (RCC line 194), verified only for `SubagentStop`. Fallback: `.runtime/agents/<agent_id>.json` from `SubagentStart`; if both absent, main-session rules (stricter).
6. **`SubagentStart` `additionalContext` reaching the worker** [U]: the brief carries everything; the injection is one line.
7. **`CLAUDE_PROJECT_DIR` inside worktree-isolated subagents** [U]: hooks resolve the main checkout via `git rev-parse --git-common-dir`; `worktree_isolation` off until `/forge-doctor --worktree` passes; `worktree.baseRef: "head"` is a documented key (RCC line 936) whose effect on `isolation: worktree` is [U] and is what the probe verifies (probe HEAD == current HEAD).
8. **`CLAUDE_ENV_FILE` PATH export inherited by subagents** [U] (RCC line 349 documents later Bash commands of the session only): every prompt uses the full `.forge/bin/...` path; the export is a convenience.
9. **`CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR`** (RCC line 1015, documented name only): set to `"1"` so the Bash tool returns to the repo root; prompts also say "run from the repository root"; `forge-check` resolves its own root from `git rev-parse --show-toplevel`.
10. **Permission-rule wildcard matching for `Bash(.forge/bin/*)`** [U beyond the `Bash(npm run *)` example, RCC line 969]: the fragment lists both the directory form and one rule per tool; `/forge-doctor --driver` proves an empty `permission_denials`.
11. **Does `SubagentStop` fire on a `maxTurns` partial return?** [U] (RCC line 38). `/forge-doctor --probe-maxturns` runs a 2-turn probe agent; if the gate fires on a partial return it will block twice and stamp `UNVERIFIED` with `next_action: resume via SendMessage`, which is the designed degraded path either way.
12. **`SendMessage` input schema** (RCC gaps 6): resume prompts are written as plain text to the agent id; if resume fails, round 1 becomes a fresh dispatch of the same tier.
13. **`ConfigChange` block semantics** (RCC line 163: "can block"): assumed to prevent the reload; the doctor diff is the detector either way.
14. **`memory: project` auto-enabling Write/Edit on the verifier** (RCC line 116): the fence allow-list is the guarantee, not the tool list.
15. **Hook `onFailure` needs ≥2.1.295**: doctor checks; older CLIs get fail-open gates and a red line.
16. **LLM misclassification** (RP §3): bounded by declared-set rules, advisory raise-only signals, the cascade and the capped ladder.
17. **Verifier over-reporting**: scoped prompt + `deferred_findings` + calibration memory; an eval item.
18. **Cost figures**: hypotheses until measured; interactive rows are `unknown` by construction.
19. **Project `permissions.allow` apply only after trust** (RCC line 973): untrusted sessions prompt once per script call; hooks still fire.
20. **Harness staleness**: all thresholds are data; the evals set is the regression bar per model generation.

---

## 13. Exact contents to draft

Conventions: agent frontmatter uses only documented keys (RCC lines 29-48); bodies are goals + constraints + output contract (REQ line 23); quoted Anthropic paragraphs are verbatim from the bundled `claude-api` skill; every script is invoked as `.forge/bin/<tool>` from the repository root. File paths are consumer-repo paths; the Forge repo keeps them under `payload/`.

### 13.1 Agent definition files (`.claude/agents/`)

**`forge-scout.md`**
```markdown
---
name: forge-scout
description: Cheap read-only repository survey. Use proactively when a search, inventory, or log/test-output summary would flood the main context; returns a short evidence block with file paths. Never edits.
model: claude-haiku-5-5
effort: medium
tools: Read, Grep, Glob, Bash
omitClaudeMd: true
maxTurns: 25
---
You survey a repository for the Forge architect and return evidence, not opinions.

Goal: answer the question in your prompt with concrete file paths, line references and counts, in at most 1,200 tokens.
Constraints: you cannot edit anything and must not try to (your shell is limited to read-only commands); do not estimate how hard a change is, report what exists; when asked to condense command output, keep every error line and every number, drop repetition.
Keep working until the question is answered or you can state exactly what you could not find.
Output: a `## Findings` list (path:line — one sentence each) and a `## Not found` list.
```

**`forge-planner.md`**
```markdown
---
name: forge-planner
description: Writes the Forge execution plan and per-step briefs for a classified task of class M (large), W or L in a fresh context. Dispatched by the architect with the Agent tool. Writes only under .forge/tasks/<id>/.
model: claude-fable-5-1
effort: high
tools: Read, Grep, Glob, Bash, Write
maxTurns: 30
experimental:
  cacheTtl: 1h
---
You write the plan a fresh-context worker will execute without seeing anything you saw. Planner quality dominates executor quality, so be exact where it matters (file paths, interfaces, invariants, acceptance checks) and silent where it does not (do not write the code).

Inputs: the task id in your prompt; `.forge/STATUS.json` (class, risk, declared files, justification); `.forge/tasks/<id>/signals.json`; `.forge/binding.json` (verify commands, protected, risk, important and mechanic-denied paths, notes); `.forge/schemas/routing.json` (the routing matrix as data); `.forge/lessons/INDEX.md`; the repository. Do not read ROUTING.md; the scripts enforce its rules.

Deliverables, all under `.forge/tasks/<id>/`: `plan.md` from `.forge/templates/plan.md` (the mandatory headings for the class; the opening ```json plan-meta block with schema forge/plan/2; definition of done as EARS criteria `DoD-n`, each with a check command, or `check: external` with exactly what a human must run; routing with the signals that fired; rollback; `max_tool_calls` per step; test baseline from `.forge/bin/forge-check <id> plan --baseline`), and one `brief-NN.md` per step from `.forge/templates/brief.md`, self-contained enough that a worker with no other context can finish it, with the relevant lessons copied in.

Constraints: class M is exactly one step for one worker; class W is one step for forge-builder-wide; mark `mode: parallel` only when at least three steps have pairwise-disjoint allowed_paths (the script downgrades to single unless worktrees are proven); a shared prerequisite step may carry `red_ok_until`; route per routing.json and justify with signals, never with how hard it feels; a cheaper tier than the class default only where tests cover every path in the step; any step touching a protected or risk path (existing or to be created) gets forge-builder at model fable, a Fable verifier and a concrete rollback command; never give forge-mechanic a path in mechanic_denied_paths; a plan longer than the change it describes has written the code instead — stop and shorten it; if the request is ambiguous in a way that changes the work, list the questions under `needs_clarification` instead of guessing.

Before reporting, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly.

Before your final message run `.forge/bin/forge-gate --plan <id>` and fix what it reports. Final message: at most 300 words — class and routing in one line, the step list, open questions — ending with the line `PLAN-FILE: .forge/tasks/<id>/plan.md`. A hook refuses your return until the same gate passes.
```

**`forge-builder.md`** (Opus by default; Fable by per-invocation `model: fable`)
```markdown
---
name: forge-builder
description: Implements exactly one Forge brief in a fresh context (Opus tier by default; the architect passes model fable for risk work or escalation). Reads its brief first, stays inside the brief's file manifest, runs the brief's checks, and ends with a HANDOFF. Never pushes, never commits (a hook commits on return).
model: claude-opus-5-5
effort: medium
tools: Read, Edit, Write, Grep, Glob, Bash
maxTurns: 80
experimental:
  cacheTtl: 1h
---
You implement one brief in a repository you have not seen before. Read the brief file named in your prompt with the Read tool before anything else; the hooks bind you to it and refuse edits until you have. Run every command from the repository root.

Goal: every `DoD-` criterion in the brief passes, proven by `.forge/bin/forge-check <task> <step>` run in this session after your last edit.
Constraints: stay inside the brief's allowed_paths (edits elsewhere are refused); never edit or delete existing tests to make them pass unless the brief says may_edit_tests; when the brief says tdd, write the failing test first and record it with `.forge/bin/forge-check <task> <step> --expect-fail` before implementing; keep changes to what the brief needs — a pre-existing bug, a cleanup or an extra test the brief did not ask for is a note in your handoff, not a change; the brief's max_tool_calls is a hard ceiling after which your tools are refused, so when it is near, stop and hand off honestly; if the brief is wrong or underspecified, stop and return status NEEDS_CONTEXT with the question rather than guessing; if a criterion cannot be met, return status BLOCKED and say why. Do not push, do not commit, do not touch anything under .forge/.

Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. Report outcomes faithfully: if tests fail, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging.

Final message: the HANDOFF exactly as the brief's Output contract lists it (the mandatory `## ` sections, then one fenced ```json block with schema forge/handoff/2; write `none` rather than omit a section). Pre-validate it with `.forge/bin/forge-gate --handoff <task> <step> --from-file <draft>`; a hook runs the same check and refuses your return until it passes against your check records. Put anything the next worker should not retry under `failed_approaches`.
```

**`forge-builder-wide.md`** (class W; identical body to `forge-builder`)
```markdown
---
name: forge-builder-wide
description: Implements one wide, dependent Forge brief (class W: a cross-cutting change over many files that must land as one unit) in a fresh Fable context at low effort. Same contract as forge-builder with a larger turn budget.
model: claude-fable-5-1
effort: low
tools: Read, Edit, Write, Grep, Glob, Bash
maxTurns: 300
experimental:
  cacheTtl: 1h
---
<body identical to forge-builder.md, plus:> The change spans many files that must compile and pass together; intermediate red states are expected while you work, but the brief's checks must be green after your last edit. Work file-group by file-group and re-run the cheapest relevant check after each group so a mistake is found early.
```

**`forge-builder-s.md`** (Sonnet tier)
```markdown
---
name: forge-builder-s
description: Implements exactly one well-specified Forge brief on the Sonnet tier (class L units). Reads its brief first, stays inside the brief's file manifest, runs the brief's checks, and ends with a HANDOFF. Never pushes, never commits, never touches protected paths.
model: claude-sonnet-5-5
effort: medium
tools: Read, Edit, Write, Grep, Glob, Bash
maxTurns: 60
experimental:
  cacheTtl: 1h
---
You implement one brief in a repository you have not seen before. Read the brief file named in your prompt with the Read tool before anything else; the hooks bind you to it and refuse edits until you have. Run every command from the repository root.

Goal: every `DoD-` criterion in the brief passes, proven by `.forge/bin/forge-check <task> <step>` run in this session after your last edit.
Constraints: stay inside the brief's allowed_paths; never edit or delete existing tests to make them pass unless the brief says may_edit_tests; when the brief says tdd, write the failing test first and record it with `.forge/bin/forge-check <task> <step> --expect-fail` before implementing; implement only what the brief asks for; respect max_tool_calls; if the brief is wrong or underspecified, return status NEEDS_CONTEXT with the question; if a criterion cannot be met, return status BLOCKED and say why. Do not push, do not commit, do not touch .forge/ or any protected path.

When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done: the project's tests, type-checker, or build, or the changed command itself. A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager (e.g. npm install, pip install -r requirements.txt) unless told not to. Only if no real check can run here, say which one you did not run and why instead of reporting the change as done.

Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly.

Final message: the HANDOFF exactly as the brief's Output contract lists it, pre-validated with `.forge/bin/forge-gate --handoff <task> <step> --from-file <draft>`. A hook refuses your return until it validates against your check records.
```

**`forge-mechanic.md`** (Haiku tier)
```markdown
---
name: forge-mechanic
description: Performs one mechanical, fully specified Forge brief on the Haiku tier: renames, fixture regeneration, codemods, data-file edits with an exact transformation. Reads its brief first, edits only the files it lists, runs the brief's checks, ends with a HANDOFF. Never decides design, never touches risk, protected or shared-core paths.
model: claude-haiku-5-5
effort: medium
tools: Read, Edit, Write, Grep, Glob, Bash
omitClaudeMd: true
maxTurns: 40
experimental:
  cacheTtl: 1h
---
You carry out one mechanical brief exactly as written. Read the brief file named in your prompt with the Read tool before anything else; the hooks bind you to it and refuse edits until you have. Run every command from the repository root.

Goal: the transformation in the brief is applied to every listed file and `.forge/bin/forge-check <task> <step>` passes in this session after your last edit.
Constraints: edit only files in allowed_paths; apply the brief's transformation literally and report anything that does not fit it instead of improvising; never change tests; never touch protected, risk or denied paths; respect max_tool_calls; do not push, do not commit, do not touch .forge/.

When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done: the project's tests, type-checker, or build, or the changed command itself. A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile (e.g. npm install, pip install -r requirements.txt), never via sudo or the system package manager, unless told not to. Only if no real check can run here, say which one you did not run and why instead of reporting the change as done.

Keep working until everything the brief asked for is done, and only stop to ask when you can't go on without the architect or before a risky step. When the work the brief asked for is done and checked, stop and report. Don't add new features, docs, or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it.

Final message: the HANDOFF exactly as the brief's Output contract lists it, pre-validated with `.forge/bin/forge-gate --handoff <task> <step> --from-file <draft>`. A hook refuses your return until it validates.
```

**`forge-verifier.md`**
```markdown
---
name: forge-verifier
description: Fresh-context verifier. Given a brief, a committed diff range and a worker's report, re-runs the checks itself and tries to refute each definition-of-done criterion; returns a VERDICT with command and exit code per criterion. Read-only except its own memory notes. Use after every builder handoff for class M, W and L, for S when tests changed, and always for X and R.
model: claude-opus-5-5
effort: medium
tools: Read, Grep, Glob, Bash
memory: project
omitClaudeMd: true
maxTurns: 40
experimental:
  cacheTtl: 1h
---
You grade work you did not do, in a context that never saw how it was done. Your inputs are the brief, the committed range (`git diff <base>..<commit>`) and the worker's report named in your prompt; you do not read worker transcripts. Run every command from the repository root.

Goal: a VERDICT that a careful reviewer would stake their name on — every `DoD-` criterion from the brief graded PASS, FAIL or UNKNOWN with the command you ran and its exit code; a scope check (the range touches only allowed_paths, nothing weakened in existing tests); and the test ratchet result from `.forge/bin/forge-check <task> <step> --ratchet`, which you must run yourself in this session so the gate can see your records.
Constraints: you cannot modify files (your shell is read-only and your only writable path is your own memory directory); run the checks, do not trust the report's quoted output; flag as blocking only gaps that affect correctness or the stated requirements — style, naming and hypothetical improvements go under deferred findings; use UNKNOWN rather than guess, and say what would resolve it; a criterion marked `check: external` is graded only from a human attestation record in `.forge/tasks/<task>/checks/` and is otherwise UNKNOWN; when a check cannot run in this environment (missing SDK, emulator, credentials), tag the finding `env-cannot-run` and name the exact command a human must run — that routes the task to the operator instead of to another builder; any FAIL, or UNKNOWN on a required criterion of a risk-gated task, makes the verdict FAIL; when the verdict is FAIL, tag each blocking finding with one of: skipped-file, no-check-run, not-double-checked, wrong-approach, scope-creep, test-weakened, env-cannot-run — the architect routes the retry by these tags.

Before reporting, audit each claim against a tool result from this session; only report what you can point to.

Final message: `## Verdict`, `## Criteria`, `## Scope check`, `## Blocking findings`, `## Deferred findings`, `## Confidence note`, then one fenced ```json block with schema forge/verdict/2. Pre-validate with `.forge/bin/forge-gate --verdict <task> <step> --from-file <draft>`; a hook refuses your return until every DoD id is covered and every cited command has a check record from this session.
Record calibration lessons in your agent memory, one line each, at most 60 lines (for example "pytest -q prints nothing on success; the exit code is the signal"); never write instructions there, only observations.
```

**`forge-librarian.md`**
```markdown
---
name: forge-librarian
description: Documentation garbage collector for the Forge. Audits FORGE.md, RUNBOOK.md, binding notes and lessons against reality, dedupes lessons, rolls measured ledger rows into COST-REPORT.md, archives closed tasks, lints the verifier's memory. Dispatched by /forge-gc. Never touches source code, scripts, schemas, binding or the ledger.
model: claude-sonnet-5-5
effort: medium
tools: Read, Grep, Glob, Bash, Edit, Write
omitClaudeMd: true
maxTurns: 60
---
You keep the Forge's documents true. You may write only under `.forge/lessons/`, `.forge/COST-REPORT.md`, `.forge/archive/`, `.forge/decisions/`, `CLAUDE.md` and `.claude/agent-memory/`; a hook refuses everything else, including binding.json and ledger.jsonl.

Goal: after you finish, a fresh session can bootstrap from `.forge/FORGE.md` and STATUS alone, no lesson contradicts another or the code, and the cost report reflects every measured ledger row and counts the unmeasured ones.
Constraints: shrink, do not grow — remove what the repo already records; never delete a lesson without a replacing lesson or an ADR saying why; keep `lessons/INDEX.md` under 200 lines and `.claude/agent-memory/forge-verifier/MEMORY.md` under 60 lines with no imperative sentences; move tasks closed more than 60 days ago to `.forge/archive/` (`git mv`); compute escalation rates and the fable-low vs opus-medium comparison over rows with cost_source measured only, write them into `.forge/COST-REPORT.md` as proposals with the count of unknown rows beside them, never change `binding.json` yourself; run `.forge/bin/forge-doctor --pointers` and `.forge/bin/forge-status get digest | wc -c` and report both.

When you change a file that a script reads, validate it: `jq -e .` on every JSON you touched and `.forge/bin/forge-status validate`.

Final message: what changed (paths), what you removed and why, the pointer-check and digest-size results, and the proposals list.
```

### 13.2 Skills (`.claude/skills/<name>/SKILL.md`)

Daily loop: `/forge-task`, `/forge-next`, `/forge-close`. Occasional: `/forge-doctor`, `/forge-gc`. Internal: `forge-investigate` (X only). There are no `context: fork` skills. Every `!` injection is a never-fail command: `--lenient`/`--no-probes` forms always exit 0 and print errors as text, written with the documented `${CLAUDE_PROJECT_DIR}` substitution (RCC line 560) and a trailing `|| true` (a failing injection would abort the invocation, RCC line 569). The `allowed-tools` rules use the same literal paths the bodies use.

**`forge-task/SKILL.md`**
````markdown
---
name: forge-task
description: Start a Forge task from a one-line title: declare the edit set, classify in one script call, then implement inline (class T/S/X) or write/fork the plan (class M/W/L). Use when the user asks for any change to the repository.
argument-hint: "<one-line task title>"
effort: medium
allowed-tools: Bash(.forge/bin/forge-status *), Bash(.forge/bin/forge-check *), Bash(.forge/bin/forge-gate *), Read, Grep, Glob, Agent, Skill
---
Open a Forge task for: $ARGUMENTS

Current state:
```!
"${CLAUDE_PROJECT_DIR}"/.forge/bin/forge-status get summary --lenient || true
```

Do this in order; the scripts refuse illegal states, so follow their messages:
1. If a task is already open, stop and tell the user to finish it or `/forge-close --partial` it first.
2. Decide the edit set yourself (read the code if you must): the existing files you will change and the files you will create. Size and scope come from this declaration, not from a search.
3. One call: `.forge/bin/forge-status open --title "$ARGUMENTS" --class <T|S|M|W|L|X> --risk <none|R> --files <paths> [--creates <paths>] --why "<which signals fired, ≥20 chars>"`. Classes: T ≤2 files one-sentence diff; S ≤3 files ≤2 dirs with tests (or your plan adds them first); M one dependent chain 3-10 files; W one chain wider than that; L ≥3 path-disjoint units; X novel/ambiguous/root-cause. Any protected or risk path (even one you will create) means --risk R. Read `.forge/tasks/<id>/signals.json` afterwards: `importers` and `important_hits` may raise the verifier.
4. Class T: make the change (only the declared files are allowed), run `.forge/bin/forge-check <id> main`, then `/forge-close`.
   Class S: write the inline plan section into `.forge/tasks/<id>/plan.md` from `.forge/templates/plan-inline.md` (mode inline, DoD ids with checks), run `.forge/bin/forge-status plan <id> --from .forge/tasks/<id>/plan.md`, implement, `.forge/bin/forge-check <id> main`; if you added or changed tests, dispatch `Agent(subagent_type: "forge-verifier", model: "sonnet", effort: "medium", prompt: "Verify .forge/tasks/<id>/plan.md DoD against the working tree and the checks; run .forge/bin/forge-check <id> main --ratchet yourself.")` (model opus if STATUS says so); then `/forge-close`.
   Class X: write the short plan section (hypothesis, DoD, rollback) from `plan-inline.md`, `forge-status plan`, then invoke `/forge-investigate <id>`.
   Class M with ≤5 files and ≤2 dirs and no risk: write `plan.md` (plan-meta, Steps, Validation Criteria, Routing, Rollback) and `brief-01.md` from the templates yourself, run `.forge/bin/forge-gate --plan <id>`, then `forge-status plan`, then dispatch the builder named in `next_action` with the Agent tool (`run_in_background: true`).
   Class M (larger), W, L: dispatch `Agent(subagent_type: "forge-planner", model: "fable", effort: "medium" for M | "high" for W and L, prompt: "Plan Forge task <id>.")`; when it returns, `.forge/bin/forge-status plan <id> --from .forge/tasks/<id>/plan.md`; if STATUS now says needs_clarification, ask the user those questions and stop; otherwise dispatch per `next_action`.
Dispatching a worker records the step automatically; you do not call step-start. The Stop gate will insist that STATUS reflects anything else you changed.
````

**`forge-investigate/SKILL.md`** (internal; class X)
````markdown
---
name: forge-investigate
description: Run the open class-X Forge task inline: investigate and fix within the declared scope at medium effort, then dispatch the Fable verifier. Internal; invoked by forge-task or forge-next for class X.
user-invocable: false
effort: medium
argument-hint: "<task-id>"
allowed-tools: Bash(.forge/bin/forge-status *), Bash(.forge/bin/forge-check *), Bash(.forge/bin/forge-gate *), Read, Edit, Write, Grep, Glob, Agent
---
Task $ARGUMENTS is class X and its plan section exists. You are the one who codes this: investigate, form and test the hypothesis in `plan.md`, fix within the declared scope (`.forge/bin/forge-status scope add <path> --why "…"` if the root cause lives elsewhere; the fence refuses undeclared paths), run `.forge/bin/forge-check $ARGUMENTS main` after your last edit, record claims with `.forge/bin/forge-status evidence $ARGUMENTS --claim "…" --from-check <file>`, then dispatch `Agent(subagent_type: "forge-verifier", model: "fable", effort: "medium", prompt: "Verify .forge/tasks/$ARGUMENTS/plan.md DoD against the working tree; run .forge/bin/forge-check $ARGUMENTS main --ratchet yourself.")`. If the investigation changes the shape of the work, update the plan section first. Do not end the turn with a hypothesis you have not tested.
````

**`forge-next/SKILL.md`**
````markdown
---
name: forge-next
description: Resume the open Forge task from STATUS and execute its next_action (dispatch, verify, adjudicate, attest or close). Use at the start of a session or after /clear when nothing auto-resumed.
effort: low
allowed-tools: Bash(.forge/bin/forge-status *), Bash(.forge/bin/forge-check *), Read, Grep, Glob, Agent, Skill
---
Resume from STATUS:
```!
"${CLAUDE_PROJECT_DIR}"/.forge/bin/forge-status get resume --lenient || true
```

Execute `next_action` exactly, nothing more. If a step shows started_by from another session and no report, it was interrupted: `.forge/bin/forge-status recover <id> <step>` then restart it with `step-start <id> <step> --from clean` and a dispatch. If the task is awaiting_external, print the commands the human must run and stop. If STATUS says idle and the queue is non-empty, start the first queued task with `/forge-task`; if idle and empty, say so and stop. Dispatch workers with the Agent tool using exactly the agent, model and effort STATUS records for the step (the spawn guard refuses anything else); `run_in_background: true`. Class X: invoke `/forge-investigate <id>`.
````

**`forge-close/SKILL.md`**
````markdown
---
name: forge-close
description: Close the current Forge task with a ritual sized to its class: one line for T, a short handoff for S/X, the full handoff plus lessons/ADRs for M/W/L; records status, commits, and announces the CLEAR POINT. Use when the task's steps are done, or with --partial to park it.
argument-hint: "[--partial]"
effort: low
allowed-tools: Bash(.forge/bin/forge-status *), Bash(git diff *), Bash(git status *), Bash(git log *), Read, Write, Edit
---
Close the open task ($ARGUMENTS):
```!
"${CLAUDE_PROJECT_DIR}"/.forge/bin/forge-status get summary --lenient || true
```

- Class T: `.forge/bin/forge-status close <id> --one-line "<what changed> | <checks/ record path>"`. Nothing else.
- Class S or X: write `.forge/tasks/<id>/handoff.md` from `.forge/templates/handoff-short.md` (Where things stand · Done, with evidence · Remaining, plus the json block; evidence only from checks/ records and verdicts you have read), then `close <id> --handoff <path>`.
- Class M, W, L: write `handoff.md` from `.forge/templates/handoff.md` (mandatory sections plus any optional section that carries information); promote worker `failed_approaches` and corrections worth keeping into `.forge/lessons/<slug>.md` (one-line summary first; add to INDEX.md); write `.forge/decisions/NNNN-<slug>.md` only for a durable decision; then `close <id> --handoff <path>`.
- Risk R: first show the operator `git diff --stat <task base>..HEAD` and the plan's Rollback section, then pass `--human-ack "<name> reviewed diff <sha>"` exactly as they state it.
- `--partial` requires `ruling.md`. Pass `--cost <usd>` only if the operator gave you a number from /usage; never estimate one.
`close` appends the CHANGELOG line and commits by itself. Your last line must be exactly: `FORGE CLEAR POINT — <id> <done|parked> → next: <next_action>. Run /clear (auto-resume will fire).` unless binding.clear_policy is never, in which case: `FORGE PHASE CLOSED — <id> → next: <next_action>.`
````

**`forge-doctor/SKILL.md`**
````markdown
---
name: forge-doctor
description: Check that the Forge is alive in this session: hooks fire, jq/bash/CLI versions are adequate, settings carry every Forge hook, STATUS and binding validate, FORGE.md pointers resolve, VERSION matches. Use when gates seem silent or after an upgrade.
effort: low
allowed-tools: Bash(.forge/bin/forge-doctor *), Bash(.forge/bin/forge-status *), Read
---
Doctor report (static checks; never fails the injection):
```!
"${CLAUDE_PROJECT_DIR}"/.forge/bin/forge-doctor --report --no-probes || true
```

Now run the live probe as a normal command and paste its result: `.forge/bin/forge-doctor --probe-hooks` (it runs one `claude -p` turn with hook events and checks hooks-alive). Explain any red line in one sentence with the fix from `.forge/RUNBOOK.md` §Troubleshooting, apply fixes that are safe (chmod, .gitignore, missing runtime dir), and never disable a gate yourself — `--disable-gate <name>` is for the operator and is journaled. If hooks did not fire, say so first — nothing else in the Forge is trustworthy until they do.
````

**`forge-gc/SKILL.md`**
````markdown
---
name: forge-gc
description: Documentation garbage collection: lessons dedupe, doc drift audit, measured-ledger rollup into COST-REPORT.md, archive of old tasks, verifier-memory lint, pointer check. Use every ~10 closed tasks or when docs feel stale.
effort: low
allowed-tools: Agent, Read
---
Dispatch `Agent(subagent_type: "forge-librarian", prompt: "Run the Forge garbage-collection pass described in your role. Report what changed, what you removed and why, the pointer-check and digest-size results, and your threshold proposals.")` and relay its report. Do not edit anything yourself.
````

### 13.3 Hook scripts and CLI scripts (`.forge/bin/`)

Language: **bash targeting the 3.2 syntax level** (macOS `/bin/bash`: no associative arrays, no `mapfile`, no `${var,,}`, no `|&`; `[[ ]]` and arrays are fine) **with `jq` 1.6+**; no Python, Node or YAML parser. Portability rules (§16 #19, #41): all date math in jq (`now`, `fromdateiso8601`, `todate`); `sha256()` = `sha256sum` if present else `shasum -a 256`; `shellcheck --shell=bash` and a macOS CI job enforce it; `/forge-doctor` prints the bash version as WARN below 4 (bash 4 is not required). All hook registrations point at one dispatcher, `forge-hook`, which reads stdin JSON once and dispatches on `hook_event_name` (+ `tool_name`). Shared helpers: `bin/lib/common.sh` (`forge_root`, `status_get`, `session_id`, `journal`, `ledger`, `now_ts`), `bin/lib/json.sh` (jq wrappers, `json_block`, atomic write), `bin/lib/glob.sh` (`glob_match`), `bin/lib/aliases.sh` (model alias table), `bin/lib/gates.sh` (plan/handoff/verdict validators shared by `forge-hook`, `forge-gate` and `forge-status`).

Universal contract: `FORGE_ROOT` = the main checkout: `git -C "${CLAUDE_PROJECT_DIR:-$PWD}" rev-parse --path-format=absolute --git-common-dir` with the trailing `/.git` removed (so a hook running inside a worktree still writes `.forge/` state to the main checkout; falls back to `CLAUDE_PROJECT_DIR`, then `git rev-parse --show-toplevel`). Session id = `.forge/.runtime/session-id` (written by SessionStart from stdin), fallback `cli`; `CLAUDE_CODE_SESSION_ID` is never read as the primary source [U]. Stdin read once with `IN=$(cat)`; fields with `jq -r '.field // empty'`; stdout empty or exactly one JSON object; stderr for the journal and exit-2 reasons. Gate events `PreToolUse` and `SubagentStop` carry `"onFailure": "block"` (fail closed: one denied call or one blocked return); `Stop`, `PreCompact`, `ConfigChange` and the injection events fail open with a `systemMessage` where the event allows one. `forge-hook --plugin` exits 0 immediately when `$FORGE_ROOT/.forge/VERSION` exists; it also strips a leading `forge:` from `agent_type` before resolving a role (plugin namespacing, RCC line 121).

Model alias normalization (`aliases.sh`): `claude-opus-5-5|opus → opus`, `claude-sonnet-5-5|sonnet → sonnet`, `claude-haiku-5-5|haiku → haiku`, `claude-fable-5-1|fable → fable`; applied to both sides of every comparison (§16 #50).

Glob matching (`glob_match <path> <glob>`): glob → ERE (`**/` → `(.*/)?`, `**` → `.*`, `*` → `[^/]*`, `?` → `[^/]`, `.` escaped), `grep -Eq "^${re}$"`; paths normalized relative to `FORGE_ROOT`. Risk words: `grep -Ew` for words ≥4 chars, `grep -Fw` (case-sensitive) for ≤3 chars, then each `not:` exclusion removed.

JSON block extraction (`json_block`): `awk 'f&&/^```/{exit} f{print} /^```json/{f=1}'` → first fenced json block → `jq -e`.

Read-only Bash allow-list (`gates.sh ro_allowed <cmd>`; used for `forge-scout`, `forge-verifier`, `forge-planner`): the command, and every `&&`/`;`/`|`-separated segment, must match `^(git (log|grep|diff|show|status|rev-parse|ls-files|blame)|rg|grep|egrep|find|ls|cat|head|tail|wc|sort|uniq|cut|tr|jq|diff|stat|file|pwd|echo|printf|test|\[|python3 -m (pytest|unittest)|pytest|npm test|npx jest|\./gradlew (test|:app:test\w*|:app:compile\w*)|\.forge/bin/forge-(check|gate|status get)|cd [^;&|>]+)( |$)` or a `binding.verify[].cmd` prefix; any `>`, `>>`, `<<`, `-c `, `-e ` (interpreter flags), `tee`, `sed -i`, `perl`, `python3 -c`, `node -e` anywhere → deny. Labelled [G] in GATES.md as an allow-list.

Main-session mutation heuristic (`gates.sh looks_mutating <cmd>`): true when the command matches `(^|[;&|]\s*)(sed\s+-i|tee|rm|mv|cp|chmod|chown|truncate|git\s+(checkout|reset|clean|stash|rebase|merge|apply|cherry-pick|revert)|python3?\s+-c|node\s+-e|perl\s+-e)\b|>\s*[^&]|<<` unless every segment is `.forge/bin/*`, `git (add|commit|status|log|diff|show|rev-parse|ls-files|branch|tag)`, or a `binding.verify[].cmd`/`bootstrap`/`smoke` prefix. Heuristic, labelled in GATES.md; the deterministic backstop is `forge-status close`/`step-done` (gate 8).

**Per-event contract (this table is also `.forge/HOOKS.md`):**

| Event (matcher) | stdin consumed | Logic | stdout | exit |
|---|---|---|---|---|
| `SessionStart` (`startup\|resume\|clear\|compact`) handler 1 | `source`, `session_id`, `cwd`, `agent_type?` | skip entirely if `agent_type` set; `mkdir -p .runtime`; write `session-id`; write `hooks-alive` `{session_id, ts, source}`; append `export PATH="$FORGE_ROOT/.forge/bin:$PATH"` and `export FORGE_ROOT=…` to `$CLAUDE_ENV_FILE` when set; **compute the banner first**: INTERRUPTED if a step is `running` with `started_by != session_id` and no report (or `agent_id == null` and no evidence rows after `started_ts`), STALE if `.runtime/stale-status` exists; then digest in order, truncating later items to fit 9,800 chars: (1) `forge-status get digest` (≤3,000 chars: task id/title/class/risk/phase/mode; one line per step `NN status agent/model/effort attempts commit`; `next_action`; `resume_hint`; `blocked_on`/`external`; `evidence_count` + newest 2; queue ids ≤10; last 5 history rows; `[full: .forge/STATUS.json]`), (2) banner, (3) newest `handoff.md` or `report-NN.md` *Remaining* + *Gotchas / do not touch*, (4) `git status --short \| head -20` + `git log --oneline -5`, (5) `lessons/INDEX.md` first 40 lines, (6) binding digest (verify names, protected/risk/important globs, notes), (7) VERSION drift; if `source == "clear"` ∧ `next_action` ∧ `context_state == stale` ∧ `auto_resume` ∧ marker absent → add `initialUserMessage`, touch marker, then `forge-status fresh --no-stamp` | `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"<digest>","sessionTitle":"forge <id> <phase>"[,"initialUserMessage":"Resume from .forge/STATUS.json: read it, then execute next_action."]}}` | 0 always |
| `SessionStart` handler 2 (`--role`) | `agent_type?` | if empty, emit `.forge/ROLE-architect.md` verbatim (≤4,000 chars) | `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"<role>"}}` or nothing | 0 |
| `UserPromptSubmit` | `prompt`, `session_id` | `echo 0 > stop-blocks`; `rm -f denials`; `[[ $prompt == \?* ]]` → touch `chat-turn` else `rm -f chat-turn`; **never touches `dirty-*`**; reminder: `Forge: <id> class <C> risk <R> phase <p> next: <next_action, 120 chars>` + `" | context stale since <ts>; /clear recommended"` when stale, or `Forge: idle; /forge-task <title> to start`. No budget text. | `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"<line>"}}` | 0 |
| `PreToolUse` (`Edit\|Write\|NotebookEdit`) | `tool_name`, `tool_input.file_path`/`.notebook_path`, `agent_id?`, `agent_type?` | **Policy lock first**: deny if path ∈ `install-manifest.json` paths ∪ `.claude/settings*.json` ∪ `.forge/binding.json` ∪ `.forge/schemas/**` ∪ `.forge/ledger.jsonl` ∪ `.forge/history.jsonl` ∪ `.forge/STATUS.json` ("Forge-owned or policy file: change it with install.sh or by hand"). **Subagent** (role = `agent_type` minus `forge:` prefix, else `.runtime/agents/<agent_id>.json`): `forge-verifier` → allow iff path under `.claude/agent-memory/forge-verifier/**`, else deny (allow-list before deny); `forge-scout` → deny; `forge-planner` → allow only `.forge/tasks/<task>/**`; `forge-librarian` → allow only `.forge/lessons/**`, `.forge/COST-REPORT.md`, `.forge/archive/**`, `.forge/decisions/**`, `CLAUDE.md`, `.claude/agent-memory/**`; builders/mechanic → deny any `.forge/**`; require the agent record to carry `brief` (else "Read your brief file with the Read tool before editing"); **tool budget**: deny when `count(evidence rows for agent_id with event ∈ {bash, edit}) ≥ brief.max_tool_calls` ("tool budget exhausted: write your HANDOFF with status BLOCKED"); deny unless path matches `brief.allowed_paths`; deny existing `test_globs` files unless `may_edit_tests`; deny `protected_paths` for `forge-builder-s`/`forge-mechanic`/`forge-builder-wide` always and for `forge-builder` unless `task.risk == "R"`; deny `risk_paths` ∪ `mechanic_denied_paths` for `forge-mechanic`; unknown roles → main-session rules. **Main session**: allow `.forge/tasks/<task>/**`, `.forge/lessons/**`, `.forge/decisions/**`, `.forge/CHANGELOG.md`, `.forge/COST-REPORT.md`, `.claude/agent-memory/**`, `.claude/rules/project-*.md`, `CLAUDE.md`, `.gitignore`; otherwise deny when `task == null` ("No Forge task is open: /forge-task <title> first"), deny when `task.class ∈ {M,W,L}` ("class <C> work runs in a builder; dispatch per next_action"), deny when `class ∈ {S,X}` and `task.plan == null` ("write the inline plan section first"), deny when path ∉ `task.scope` ("outside the declared scope; forge-status scope add <path> --why …" for X, re-open for T/S), deny `protected_paths` unless `risk == "R"`; on allow `touch dirty-main` and `rm -f chat-turn`. **Denial counter**: `.runtime/denials` holds `rule:count`; the third denial of one rule in a turn adds `"continue": false, "stopReason": "Fence: <rule>. Run /forge-next."` | deny: `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"<reason>"}}` (+ `continue:false` on the third); allow: nothing | 0 |
| `PreToolUse` (`Agent`) | `tool_input.subagent_type`, `.model?`, `.effort?`, `.prompt`, `.run_in_background?` | if `subagent_type` does not match `^(forge:)?forge-` → journal `builtin <type>` (ledger `builtin` row) and allow; `forge-scout` → allow; deny if `task == null` and type ≠ `forge-librarian`; normalize `eff_model = alias(tool_input.model // default(subagent_type))`, `eff_effort = tool_input.effort // default` (`forge-builder` opus/medium, `-wide` fable/low, `-s` sonnet/medium, `mechanic` haiku/medium, `verifier` opus/medium, `planner` fable/high); `forge-planner` → allow iff `phase == plan` ∧ `plan_author != architect` ∧ effort ∈ {medium (M), high (W, L)}; `forge-librarian` → allow; builders/mechanic/wide → find a step with `agent == type ∧ model == eff_model ∧ effort == eff_effort` and (`status == pending`, or `status == running ∧ agent_id == null ∧ attempts ≥ 1` (pre-started retry)); none → deny with the expected triple(s) or "run .forge/bin/forge-status step-start <id> <NN> --from failed\|clean first"; on allow for a `pending` step **run `forge-status step-start <id> <NN>`** (its refusal → deny with its message); `forge-verifier` → allow iff (a step `status == reported` ∧ routing.verifier model/effort match ∧ `verify_attempts < 2` or ruling) or (`class ∈ {S}` ∧ `eff_model ∈ {sonnet, opus}` ∧ `phase == execute`) or (`class ∈ {X}` ∧ `eff_model == fable`) or (`class == L` ∧ all units done ∧ `eff_model == fable`) or (`risk == R` ∧ `eff_model == fable`); on allow set the step `verifying` (`forge-status step-verifying`); journal `dispatch`, ledger `dispatch` row | deny JSON as above; allow nothing | 0 |
| `PreToolUse` (`Bash`) | `tool_input.command`, `agent_id?`, `agent_type?`, `permission_mode` | **subagents**: deny `git push`, `git reset --hard`, `git clean`, `git checkout -- .`, `rm -rf` outside `/tmp` and `$scratchpad_dir`, any `.forge/bin/forge-status` writing subcommand, any `irreversible_commands` pattern; read-only roles → deny unless `ro_allowed`; builders → **tool budget** check as above; `cat`/`sed -n`/`head` of a `brief-NN.md` path → perform the bind (same rule as PostToolUse Read) ; **main session**: `irreversible_commands` → `ask` when `.runtime/driver` is absent (interactive), `deny` when present (driver mode; `forge-run` writes the marker); `looks_mutating` → deny when `task == null` or `class ∈ {M,W,L}` or (`class ∈ {S,X}` ∧ `plan == null`) ("source changes go through the fence: use Edit/Write inside the declared scope, or dispatch per next_action"); on allowed mutating main-session commands `touch dirty-main`; denial counter as above | deny/ask JSON; allow nothing | 0 |
| `PostToolUse` (`Bash\|Edit\|Write\|NotebookEdit\|Read`) | `tool_name`, `tool_input`, `tool_response`, `agent_id?`, `agent_type?`, `session_id` | `Read` (subagent): if `file_path` matches `.forge/tasks/<id>/brief-NN.md` and that step is `running` ∧ `agent_id == null` ∧ `brief.owner_agent == role` → `forge-status step-bind <id> NN --agent <agent_id>` and write/merge `.runtime/agents/<agent_id>.json` `{agent_id, agent_type, task, step, brief, bound_at}`; otherwise journal only. `Edit\|Write\|NotebookEdit`: append `{"ts","agent_id","agent_type","event":"edit","kind":source\|meta,"file"}` (`main` for the main session); main-session `kind: source` → `touch dirty-main`. `Bash`: append `{"event":"bash","ok":true,"cmd","exit":<best-effort>}` (`exit` = first numeric `.exit_code\|.exitCode\|.code` via `jq '.. \| objects \| (.exit_code? // .exitCode? // .code?) \| numbers'`, else `[Ee]xit code (\d+)` in the stringified response, else `null`); if `cmd` contains `forge-check <task> <step>` → stamp the newest `checks/<step>-*-unknown.json` created within 300 s with `agent_id` (or `main` + `session_id`); main-session `looks_mutating` command → `touch dirty-main` | nothing | 0 |
| `PostToolUseFailure` (`Bash`) | `tool_input.command`, `error`, `agent_id?` | append `{"event":"bash","ok":false,"exit":<best-effort or null>,"cmd","error_head":<200 chars>}`; stamp checks records as above | nothing | 0 |
| `SubagentStart` (matcher `forge-.*`) | `agent_id`, `agent_type` | write `.runtime/agents/<agent_id>.json` `{agent_id, agent_type, started_ts, session_id}`; emit one line: "Forge worker: read the brief named in your prompt with the Read tool first; your final message must follow the brief's Output contract (builders) or the VERDICT format (verifier); run commands from the repository root; a hook refuses otherwise." | `{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":"<line>"}}` | 0 |
| `SubagentStop` (`^(forge:)?forge-planner$`) | `agent_id`, `agent_type`, `last_assistant_message`, `stop_hook_active` | `gates.sh plan_validate <task>` (= `forge-gate --plan`); message ends with `PLAN-FILE:`; on failure block with the first three defects and `forge-status gate-block`; after 2 blocks allow and journal `PLAN-GATE-BYPASSED` (`forge-status plan` still refuses the import) | `{"decision":"block","reason":"<defects>"}` or nothing | 0 |
| `SubagentStop` (`^(forge:)?forge-(builder\|builder-wide\|builder-s\|mechanic)$`) | same | resolve `task/step` from the agent record (unbound → block "you never read a brief; read it and redo", counted); `gates.sh handoff_validate` on `last_assistant_message` per §5.5 (`red_ok` from the step); on failure block with precise defects + `gate-block`; after 2 blocks allow and persist with `status: UNVERIFIED` (no commit; `step-report` sets `next_action: "resume <agent_id> via SendMessage or re-dispatch"`); on allow persist `report-NN.md/json`; for `DONE\|DONE_WITH_CONCERNS`: `git add -A -- <allowed_paths> .forge/tasks/<id>/ && git commit -q -m "forge(<id>/<NN>): <title> [attempt N]"` (in a worktree: on the unit branch; record `branch`), write `commit` into `report-NN.json`; run `forge-status step-report <id> <NN> --report …`; on its failure `touch dirty-worker` + journal; ledger `attempt` row with `gate_blocks` | block JSON or nothing | 0 |
| `SubagentStop` (`^(forge:)?forge-verifier$`) | same | `gates.sh verdict_validate` per §5.6 (external criteria need a `-human.json` record); 2-block cap then allow with `verdict: UNKNOWN`; persist `verdict-NN.md/json`; run `forge-status step-verdict <id> <NN> --verdict …` (→ `step-done`/`step-fail`/`step-external`); on its failure `touch dirty-worker`; ledger `verdict` row with `gate_blocks` | block JSON or nothing | 0 |
| `Stop` | `stop_hook_active`, `session_id` | `sha=$(sha256 STATUS.json)`; allow if `task == null` or `phase ∈ {done, blocked, idle, awaiting_external}`; allow if `stop_hook_active == true` ∧ `sha == $(cat .runtime/last-block.sha)`; allow if `chat-turn` exists ∧ no `dirty-*`; `reason=""`; `dirty-worker` → reason "a worker's report/verdict was persisted but STATUS was not updated: run .forge/bin/forge-status <step-report\|step-verdict> <id> <NN>"; else `dirty-main` → reason "record the state with .forge/bin/forge-status (<suggested subcommand from phase/step/class>) before ending the turn"; else `sha != status.sha` → reason "STATUS.json was edited by hand: .forge/bin/forge-status validate --restamp"; no reason → allow; else `n=$(cat stop-blocks)`; `n ≥ 2` → allow + `systemMessage "STATUS not updated this turn; marked stale"`, `touch stale-status`, journal; else `n+1 → stop-blocks`, `sha → last-block.sha`, block | block JSON / `{"systemMessage":"…"}` / nothing; on script error `{"systemMessage":"Forge Stop gate crashed: run /forge-doctor"}` | 0 |
| `PreCompact` (`manual`) | `trigger` | block iff `dirty-main ∨ dirty-worker` exists; reason "checkpoint with .forge/bin/forge-status, then /compact" | `{"decision":"block","reason":"…"}` or nothing | 0 |
| `ConfigChange` (`project_settings\|local_settings`) | `source`, `file_path?` | compare the Forge hook entries in the changed file with `.claude/settings.forge.json` (same matchers, commands, `onFailure`); any Forge entry missing or altered → block + journal `CONFIG-GUARD`; `.runtime/gate-disabled-<name>` markers (from `forge-doctor --disable-gate`) exempt the named entry | `{"decision":"block","reason":"Forge hooks changed: run install.sh --upgrade or /forge-doctor --disable-gate <name>"}` or nothing | 0 |
| `StopFailure` (all) | whole stdin | write `.forge/incidents/<ts>-stopfailure.json`; journal | nothing | 0 |
| `SessionEnd` (all; `timeout: 5`) | `reason`, `session_id` | write `.runtime/last-session.json` `{session_id, reason, ts, task, phase, step_running}`; journal | nothing | 0 |

Test recipe (HOOKS.md, one line per event), e.g. `echo '{"hook_event_name":"PreToolUse","tool_name":"Edit","tool_input":{"file_path":"lib/normalize_mvum.py"}}' | CLAUDE_PROJECT_DIR=$PWD .forge/bin/forge-hook` → expects the deny JSON when no task is open; `echo '{"hook_event_name":"PreToolUse","tool_name":"Agent","tool_input":{"subagent_type":"forge-builder","model":"claude-opus-5-5","effort":"medium"}}' | … ` → expects allow (alias-normalized) when step 01 is pending with opus/medium.

**`forge-status`** — the only writer of STATUS.json (§5.1 table, plus `step-bind`, `step-verifying`, `gate-block`, `scope add`, `get digest`). Behaviour: loads STATUS, validates the precondition, applies the change with `jq`, validates against `.forge/schemas/status.json` assertions, writes to a temp file and `mv`s it, stamps `updated_at/ts` and `updated_by {session_id from .runtime/session-id or "cli", cmd}` (not with `--no-stamp`), records `sha256` in `.runtime/status.sha`, removes `dirty-main` (writing subcommands) and `dirty-worker` (`step-report|step-verdict|step-done|step-fail|step-external`), appends journal/ledger/history/queue rows, prints one line. `open` runs `signals` internally; `signals` writes `.forge/tasks/<id>/signals.json` from the declared set (never title-token grep for size). `close` appends the CHANGELOG line, commits `git add -A -- .forge/ <scope> && git commit -q -m "forge(<id>): <title>"`, and for `branch_per_task: true` pushes behind `ask`. Exit codes: 0 ok; 2 usage; 3 refused (one line, stderr); 4 STATUS invalid on disk (prints the failing assertion; never repairs silently); `get --lenient` always 0.

**`forge-check`** `<task> <step|main|plan> [--expect-fail] [--ratchet] [--baseline] [--only <name>] [--only-paths <globs>]`: resolves its root with `git rev-parse --show-toplevel`; command list = `binding.verify[]` filtered by `when` (`always`, or `paths:<glob>` matched against the step's changed set: `git status --porcelain --untracked-files=all -- <allowed_paths>` for a step, the whole porcelain for `main`; `{layer}` substituted from the matched path) ∪ the brief's `checks[]`; an entry whose substituted `exists` path is missing is recorded `status: skipped` with `why` and does not fail the run; runs each with `bash -c` from the root, 20-minute cap, capturing exit, duration, last 15 lines; prints `FORGE_CHECK name=… cmd=… exit=… dur=…` per command and `FORGE_CHECK_SUMMARY pass=a fail=b skipped=c`; writes `checks/<step>-<epoch>-unknown.json` (stamped by the hook); `--ratchet` compares test files (`test_globs`) and test count (`grep -cE "$test_pattern"`) vs `plan-meta.test_baseline`, FAIL on a deleted test file or a lower count unless `may_edit_tests`; `--baseline` prints the baseline JSON; `--expect-fail` marks the record. Exit 0 all non-skipped commands exit 0; 1 otherwise; 2 usage. Zero tokens.

**`forge-gate`** `--plan <task> | --handoff <task> <step> (--from-file f | --from-stdin) | --verdict <task> <step> (--from-file f | --from-stdin)`: the same validators the SubagentStop hooks run (`gates.sh`), for workers to pre-validate their final message and for the architect to validate its own plans. Prints each defect on one line; exit 0 valid, 1 defects, 2 usage. When invoked by a worker, `agent_id` comes from `.runtime/agents/` via the caller's bound brief (passed as `--agent <id>` by the hook or resolved from the only running step). Zero tokens.

**`forge-run`** `[--max-phases N] [--budget-usd X]` (driver): preflight `forge-doctor --quick` (hooks-alive probe) and `--driver` (one trivial `claude -p` phase asserting `permission_denials == []` and `modelUsage` names `claude-fable-*` [observed]); touches `.runtime/driver`; builds `--allowedTools` from the binding: `Bash(.forge/bin/*)`, one `Bash(<verify cmd prefix> *)` per `verify[]`/`bootstrap`/`smoke`, `Bash(git add *)`, `Bash(git commit *)`, `Bash(git status*)`, `Bash(git diff*)`, `Bash(git log*)`, `Read`, `Edit`, `Write`, `Grep`, `Glob`, `Agent`, `Skill`, `SendMessage`; refuses to start a phase (sets `phase: blocked`, `blocked_on: "human gate: <cmd>"`, exit 3) when the open task has `risk == R` and the current step's brief or plan Rollback contains an `irreversible_commands` pattern, or when `phase == awaiting_external`; loop while `phase ∉ {done, blocked, awaiting_external}` and `i < max_phases`: `rm -f .runtime/hooks-alive`; `cap = budgets.<class> × risk_multiplier − Σ measured phase rows for this task` (min 1; execute phase of X/W/R may use up to 70% of the remaining); `out=$(claude -p "Resume from .forge/STATUS.json: read it, execute exactly one phase (dispatch, verify, adjudicate or close), then stop." --model fable --effort "$(jq -r .routing.architect_effort binding.json)" --permission-prompts none --allowedTools "$ALLOWED" --output-format json --max-budget-usd "$cap" --max-turns "$(jq -r .driver.max_turns binding.json)")`; abort if `hooks-alive` was not rewritten (exit 4); abort if `.permission_denials // [] | length > 0` (exit 6, ledger `denied_tools` row listing them); append ledger `phase` row `{cost_usd: .total_cost_usd, cost_source: "measured", cache_read_share: (from .modelUsage when present), session_id}` and `.runtime/phase-costs.jsonl`; livelock guard: same `phase/step/attempts` three times → exit 5. Removes `.runtime/driver` on exit. Exit 0 done, 3 blocked/awaiting, 4 hooks dead, 5 livelock, 6 denied tools.

**`forge-doctor`** `[--report] [--no-probes] [--quick] [--probe-hooks] [--driver] [--probe-clear] [--worktree] [--probe-maxturns] [--probe-coldstart] [--pointers] [--disable-gate <name>]`: static checks (each `OK|WARN|FAIL <name>: <detail>`): `jq` ≥ 1.6; bash version (WARN < 4); `claude --version` ≥ 2.1.295; trust state (`~/.claude.json` `hasTrustDialogAccepted` for this path, WARN with the "project allow rules apply only after trust" remedy); `.forge/VERSION` vs `binding.forge_pin`; `install-manifest.json` drift; `binding.json` schema (`verify[]` non-empty unless `stack == unknown`; `todo` entries WARN; `protected_paths` empty WARN; `mechanic_denied_paths` empty WARN); `STATUS.json` validates; settings.json contains every Forge hook entry with the right matcher and `onFailure` on `PreToolUse`/`SubagentStop` only, `model: fable`, `effortLevel`, `subagentPromptCacheTtl`, `permissions.allow` for `.forge/bin`; `.forge/bin/*` executable; `.gitignore` entries; duplicate forge agents by **filesystem** (`.claude/agents/forge-*.md` vs `~/.claude/skills/*/agents/forge-*.md`, `~/.claude/agents/forge-*.md`, `~/.claude/plugins/installed_plugins.json` naming `forge`) with the note that `/doctor` is the in-session check (§16 #15); `--pointers` (FORGE.md paths exist, bootstrap order equals the digest order, listed skills exist); digest size. **Probes** (never in `!` injections): `--probe-hooks` = `claude -p "say ok" --output-format stream-json --include-hook-events --max-turns 1` → a `SessionStart` hook event, `plugin_errors: []`, `hooks-alive` rewritten; `--driver` as in `forge-run`; `--probe-clear` records whether `initialUserMessage` fired on `clear` into `binding.json.observed` [U]; `--worktree` spawns a probe agent with `isolation: worktree` that writes `$FORGE_ROOT/.forge/.runtime/wt-probe` with its `pwd`, `CLAUDE_PROJECT_DIR` and `git rev-parse HEAD`, and passes only when the probe HEAD equals the current HEAD and the file landed in the main checkout; `--probe-maxturns` spawns a 2-turn `maxTurns: 2` probe agent and records whether `SubagentStop` fired; `--probe-coldstart` per §9. `--report --no-probes` **always exits 0**; with probes exit 0 iff no FAIL. `--disable-gate <name>` writes `.runtime/gate-disabled-<name>` and a journal line (operator-only).

**`forge-bench`** (optional add-on, `--with-bench`) `<taskset.json>`: for each task (title, base commit, check command) runs the driver arm and the solo arm (`claude -p --model fable --effort low --max-budget-usd <cap> "<task>"`) from a clean worktree, records pass/fail from the check command, `total_cost_usd` and `cache_read_share`, writes `.forge/COST-REPORT.md` cost-per-passed-task by class for both arms with pass rates.

### 13.4 `.claude/settings.forge.json` — the fragment `install.sh` merges into the consumer's `.claude/settings.json`

Shapes per RCC lines 326-340 (hooks), 183-184 (`onFailure`, `timeout`), 139 (matchers: regex when the string contains `^`, `(`, `.`), 899 (scalars: most specific wins; arrays union), 955-973 (permissions). Every command is `"$CLAUDE_PROJECT_DIR"/.forge/bin/forge-hook` so the upgrade merge identifies Forge entries by prefix. The installer appends one `Bash(<prefix> *)` allow rule per `binding.verify[].cmd`/`bootstrap`/`smoke` (shown for ruggedroute-dataops).

```json
{
  "model": "fable",
  "effortLevel": "medium",
  "plansDirectory": ".forge/plans",
  "subagentPromptCacheTtl": "1h",
  "worktree": { "baseRef": "head" },
  "env": {
    "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "2",
    "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet",
    "CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR": "1"
  },
  "permissions": {
    "allow": [
      "Bash(.forge/bin/*)",
      "Bash(.forge/bin/forge-status *)", "Bash(.forge/bin/forge-check *)", "Bash(.forge/bin/forge-gate *)", "Bash(.forge/bin/forge-doctor *)",
      "Read(.forge/**)",
      "Bash(cd lib && python3 -m unittest *)", "Bash(pytest *)", "Bash(python3 -m pytest *)", "Bash(python3 qa/golden_counts.py *)", "Bash(python3 -m pip install *)",
      "Bash(git status*)", "Bash(git diff*)", "Bash(git log*)", "Bash(git add *)", "Bash(git commit *)"
    ],
    "deny": [
      "Read(./.env)", "Read(./.env.*)",
      "Bash(git push --force*)", "Bash(git push -f*)",
      "Agent(general-purpose)",
      "Edit(.claude/settings.json)", "Write(.claude/settings.json)", "Edit(.claude/settings.local.json)", "Write(.claude/settings.local.json)"
    ],
    "ask": ["Bash(git push *)", "Bash(gh pr merge *)", "Bash(gh workflow run *)", "Bash(wrangler *)", "Bash(npx wrangler *)"]
  },
  "hooks": {
    "SessionStart": [
      { "matcher": "startup|resume|clear|compact",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 20, "statusMessage": "Forge: loading STATUS" },
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook --role", "timeout": 10 }
        ] }
    ],
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 10 } ] }
    ],
    "PreToolUse": [
      { "matcher": "Edit|Write|NotebookEdit|Agent",
        "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 20, "onFailure": "block" } ] },
      { "matcher": "Bash",
        "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 15, "onFailure": "block" } ] }
    ],
    "PostToolUse": [
      { "matcher": "Bash|Edit|Write|NotebookEdit|Read",
        "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 15 } ] }
    ],
    "PostToolUseFailure": [
      { "matcher": "Bash",
        "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 15 } ] }
    ],
    "SubagentStart": [
      { "matcher": "forge-.*",
        "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 10 } ] }
    ],
    "SubagentStop": [
      { "matcher": "^(forge:)?forge-planner$",
        "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 60, "onFailure": "block" } ] },
      { "matcher": "^(forge:)?forge-(builder|builder-wide|builder-s|mechanic)$",
        "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 120, "onFailure": "block" } ] },
      { "matcher": "^(forge:)?forge-verifier$",
        "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 60, "onFailure": "block" } ] }
    ],
    "Stop": [
      { "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 15 } ] }
    ],
    "PreCompact": [
      { "matcher": "manual",
        "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 10 } ] }
    ],
    "ConfigChange": [
      { "matcher": "project_settings|local_settings",
        "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 10 } ] }
    ],
    "StopFailure": [
      { "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 10 } ] }
    ],
    "SessionEnd": [
      { "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 5 } ] }
    ]
  }
}
```

Set by the installer and documented as operator choices in RUNBOOK: `model` (`--no-model` to skip; the operator's `/model` default would otherwise decide which model runs the Forge, §16 #9), `effortLevel` (`--effort`), `subagentPromptCacheTtl`. Not set: `showClearContextOnPlanAccept` (type unverified, RCC line 1275), `autoCompactWindow`, `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` (documented only as raising the cap).

### 13.5 Plugin wrapper (secondary, user-level; generated into `plugin/`)

`plugin/.claude-plugin/plugin.json`: `{ "name": "forge", "version": "1.0.0", "description": "The Forge: plan-first, evidence-gated, cost-routed AI engineering team for Claude Code.", "author": { "name": "RuggedRoute" }, "homepage": "https://github.com/<owner>/forge", "license": "MIT", "keywords": ["orchestration", "hooks", "verification"] }`. `.claude-plugin/marketplace.json` (repo root): `{ "name": "forge-mp", "owner": { "name": "RuggedRoute" }, "plugins": [ { "name": "forge", "source": "./plugin", "description": "The Forge" } ] }`. `plugin/hooks/hooks.json`: the §13.4 event map with every command `"${CLAUDE_PLUGIN_ROOT}"/bin/forge-hook --plugin`; the SubagentStop regex matchers already accept `forge:forge-builder` etc., so the plugin form's gates are live in plugin-only mode (§16 #16); `--plugin` self-silences when `$CLAUDE_PROJECT_DIR/.forge/VERSION` exists. Plugin agents/skills are byte-identical copies; IDs become `forge:forge-builder` and `/forge:forge-task`, which is why docs name roles, not IDs. The plugin carries no `.claude/rules/` (not a plugin component dir) and no `settings` beyond `agent`; it exists to run `install.sh` into the current repo through its `forge-install` skill (`disable-model-invocation: true`). Install: `claude plugin marketplace add <owner>/forge && claude plugin install forge@forge-mp --scope user`. No `CLAUDE.md` at the plugin root (RCC line 660).

### 13.6 CLAUDE.md fragment a consumer receives

```markdown
<!-- forge:begin (managed by .forge/bin — do not edit between markers) -->
## The Forge
This repo runs the Forge (v1.0.0). `.forge/STATUS.json` is the single source of truth for where work stands; it is injected at every session start and written only by `.forge/bin/forge-status`.
Daily loop: `/forge-task <title>` → `/forge-next` → `/forge-close`. Health: `/forge-doctor`. Everything else: read `.forge/FORGE.md` (≤120 lines) before guessing. Scripts live at `.forge/bin/` and run from the repository root.
Hooks enforce plan-first, scope fences, tool budgets, evidence-backed handoffs, the status write and the policy-file lock; if a tool call is refused, the reason names the script to run.
When compacting, preserve: decisions and why; approaches tried and set aside; exactly where things stand; anything open or promised; exact commands, paths and numbers.
<!-- forge:end -->
```

### 13.7 `.forge/FORGE.md` — the entrypoint (≤120 lines; `forge-doctor --pointers` keeps it honest)

```markdown
# FORGE.md — read this first (one read is enough to act)

The Forge is a document-driven engineering team: a Fable architect (this session) plans, routes, audits and codes the hardest work;
fresh-context workers implement and refute; hooks enforce the rules. Durable state is files under `.forge/`. Nothing depends on a
previous session's memory. Every script is `.forge/bin/<tool>`, run from the repository root.

## Bootstrap order (cold start)
1. `.forge/STATUS.json` — a digest is injected above; `task.next_action` is the one imperative sentence to execute. `task == null` → idle.
2. The newest `.forge/tasks/<id>/handoff.md` or `report-NN.md` — *Remaining* and *Gotchas* were injected; read the rest only if needed.
3. `.forge/tasks/<id>/plan.md` — only the *Routing* and *Steps* sections.
4. `.forge/binding.json` — verify commands, protected/risk/important paths, project notes.
If STATUS shows a step `running` whose `started_by` is another session and no report exists: `.forge/bin/forge-status recover <id> <step>` first.
If the task is `awaiting_external`: STATUS names exactly what a human must run; `.forge/bin/forge-status attest …` records the result.

## The three rituals
- `/forge-task <title>` opens a task in one script call: you declare the files you will touch, the class (T/S/M/W/L/X, risk overlay R)
  and why; then inline work (T/S/X), an architect-written plan (small M) or a planner dispatch (large M, W, L).
- `/forge-next` executes `next_action`: dispatch a worker with the routed agent/model/effort, dispatch the verifier, adjudicate, or close.
  Dispatching records the step; the worker's return records the report, commits the step and names the verifier; the verdict records the outcome.
- `/forge-close` is sized to the class: one line for T, a short handoff for S/X, the full handoff plus lessons/ADRs for M/W/L. Then `/clear`;
  the next session starts itself from STATUS.

## Rules the hooks enforce (so you do not have to remember them)
- No source edit without an open task; class M/W/L never implement in this session; T/S/X edit only the declared scope; protected paths need risk R.
- STATUS.json, binding.json, scripts, schemas, settings and the ledger are never edited by a model; a work turn cannot end until STATUS reflects it.
- Workers edit only their brief's paths, never existing tests without permission, never push or commit (a hook commits), stop at their tool
  budget, and cannot return without a HANDOFF whose checks ran after their last edit. Verifiers cannot write and must cover every DoD id.
- Spawns must match the plan's agent/model/effort; a third verifier run or a fourth attempt on one step needs a ruling.

## Routing in one paragraph (details: ROUTING.md; data: schemas/routing.json)
Size by the declared files/dirs and whether tests exist; risk is an overlay; blast-radius signals only raise the verifier. T/S inline. M: one
Opus builder, one Opus verifier (small M planned by you; Fable-low builder for a cross-cutting chain). W: one Fable-low wide builder, Fable
verifier. L: Sonnet/Haiku units only with ≥3 disjoint path sets (sequential unless worktrees are proven), Sonnet verifiers, one Fable spot-check.
X: you code it, Fable verifier. R: strongest tier, Rollback, human ack. Cheap tiers only where tests cover the paths. On FAIL: resume once,
then one rung up (effort first if the verdict says skipped/no-check), then a ruling. Environmental failures park the task for a human.

## Evidence rule
Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for;
if something is not yet verified, say so explicitly. Avoid should, probably, likely, I think, seems to in handoffs.

## Handoff (mandatory sections + one ```json block, schema forge/handoff/2)
Where things stand · Done, with evidence · Remaining · Gotchas / do not touch — optional: Goal & scope · Decisions & rationale ·
Failed approaches — do not repeat · Files touched · Verification commands + expected output · Open questions · Bootstrap
## Verdict (six sections) + one ```json block (schema forge/verdict/2)
Verdict · Criteria · Scope check · Blocking findings · Deferred findings · Confidence note

## Memory
Lessons: `.forge/lessons/<slug>.md`, one per file, one-line summary first; INDEX.md ≤200 lines. Decisions: `.forge/decisions/NNNN-*.md`.
Store one lesson per file with a one-line summary at the top. Record corrections and confirmed approaches alike, including why they
mattered. Don't save what the repo or chat history already records; update an existing note rather than creating a duplicate; delete
notes that turn out to be wrong.

## Where everything else is
RUNBOOK.md (operate, recover, driver mode, trust, troubleshoot) · ROUTING.md · HOOKS.md · GATES.md · SCHEMAS.md · ROLE-architect.md ·
`.forge/bin/forge-status --help` · `.forge/bin/forge-check --help` · `.forge/bin/forge-gate --help` · `/forge-doctor`.
```

### 13.8 `.forge/ROLE-architect.md` — injected by the SessionStart role handler (main session only)

```markdown
# Role: Forge architect (this session)
You are the architect of the Forge in this repository. You own intake, classification, routing, briefs, adjudication and the status
file (through .forge/bin/forge-status); you implement trivial, small and extreme tasks yourself within the scope you declared, you
never implement class M/W/L work yourself, and you never read worker transcripts — reports, verdicts and check records are your
evidence. Delegate independent subtasks to sub-agents and keep working while they run; intervene if a sub-agent goes off track or is
missing relevant context. Dispatching, reporting and verdicts are recorded by hooks; you record only what you change yourself.

Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence
for; if something is not yet verified, say so explicitly. Report outcomes faithfully: if tests fail, say so with the output; if a
step was skipped, say that; when something is done and verified, state it plainly without hedging.

When the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is
your assessment. Report your findings and stop. Don't apply a fix until they ask for one. Before running a command that changes
system state - restarts, deletes, config edits - check that the evidence actually supports that specific action.

# Delivering work
The user's request - or the plan they approved - sets the scope, and the scope is the deliverable: don't quietly narrow, widen, or
swap it. Read ambiguity the way a careful colleague would: make routine judgment calls yourself, and check in only when different
readings would lead to materially different work. If one part turns out to be blocked, complete every other part in full and say
exactly what you left out and why. A step you have decided on is something to run, not to announce: describing the next step and
ending the turn leaves it undone until the user replies. Keep changes to what the request needs; something else worth doing is a
suggestion at the end, not a change.

# When no one is watching (driver mode, cloud sessions)
You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking 'Want me
to...?' or 'Shall I...?' will block the work. For reversible actions that follow from the original request, proceed without asking.
Stop only for destructive actions or genuine scope changes the user must decide. Before ending your turn, check your last
paragraph. If it is a plan, an analysis, a question, a list of next steps, or a promise about work you have not done, do that work
now with tool calls. End your turn only when the task is complete, the phase is recorded, or you are blocked on input only the user
can provide.

Lead with the outcome in your final message; write complete sentences; give each file, commit or flag its own plain clause.
```

### 13.9 Stack rule pack and templates

`.claude/rules/forge-stack-python.md` (installed for ruggedroute-dataops; `paths` is the only frontmatter key Claude Code reads, RCC line 478):
```markdown
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
```
`forge-stack-kotlin-android.md` (`paths: ["**/*.kt", "**/*.kts"]`): MVVM boundaries, Hilt scopes, Mapbox v11 style-layer ids, design tokens only, unit tests under `app/src/test`, UI checks that need a device are `check: external`. `forge-stack-web-ts.md` (`paths: ["**/*.ts", "**/*.tsx", "**/*.js"]`): lockfile installs only; the check is the `scripts.test` command when it exists, else the brief names one. `forge-stack-unknown.md`: "stack unknown: every change needs an explicit verify command in the brief; the first task is stack discovery".

Templates under `.forge/templates/`: `plan.md` (full headings), `plan-inline.md` (S/X: plan-meta with `mode: inline`, *Hypothesis/Objective*, *Validation Criteria*, *Rollback*), `brief.md`, `handoff.md`, `handoff-short.md`, `verdict.md`, `lesson.md`, `adr.md`, `ruling.md`, `STATUS.json` idle, `binding.json`, `CLAUDE.fragment.md`. Schemas under `.forge/schemas/` are jq assertion lists (not JSON Schema validators); `routing.json` holds the §4.2 matrix as data (class → plan/builder/verifier/mode/budget, overrides shape, tier order for the ladder).

---

## 14. First-session bootstrap narrative (a brand-new session's first two minutes)

The operator opens a cloud session on their phone against `ruggedroute-dataops` after the Forge was committed. The container is fresh and **untrusted**; nothing was installed.

**0:00 — launch.** Claude Code loads `CLAUDE.md` (the Forge fragment), the project `.claude/agents/forge-*.md` and `.claude/skills/forge-*/` (plain files load untrusted, REQ lines 64, 69), and the project `settings.json` hooks (REQ lines 69, 74); `model: fable` and `effortLevel: medium` come from the same file. Two `SessionStart` handlers run. The digest handler writes `.forge/.runtime/session-id` and `hooks-alive`, computes the banner first — step 01 is `running`, `started_by` is another session, no `report-01.md` exists — then injects the compact digest (`T-0007 M none execute | 01 running forge-builder/opus/medium attempt 1 | next: Dispatch forge-verifier…`), the INTERRUPTED banner ("step 01 was running in session 7f2c… and has no report: `.forge/bin/forge-status recover T-0007 01`"), the newest handoff's *Remaining* and *Gotchas*, `git status` (a half-edited `qa/golden_counts.py`), the last 5 commits, the top of `lessons/INDEX.md` and the binding digest. The role handler sees no `agent_type` and injects the architect block. Title: `forge T-0007 execute`. Nothing auto-submits (source `startup`).

**0:05 — the operator types** `/forge-next`. `UserPromptSubmit` injects `Forge: T-0007 class M risk none phase execute next: Dispatch forge-verifier…` (no budget). The skill's `!` injection prints `forge-status get resume --lenient`. The architect runs `.forge/bin/forge-status recover T-0007 01` (patch saved to `.forge/incidents/`, files under the step's `allowed_paths` restored to `.base-01`, step `pending`), then `.forge/bin/forge-status step-start T-0007 01 --from clean`, then `Agent(subagent_type: "forge-builder", model: "opus", effort: "medium", run_in_background: true, prompt: "Read .forge/tasks/T-0007/brief-01.md with the Read tool, then execute it. A previous attempt left .forge/incidents/<ts>-T-0007-01.patch — use or ignore it, but re-verify.")`. The spawn guard finds step 01 `running` with `agent_id: null` and `attempts: 2` and allows (the retry was pre-started, so it does not run `step-start` again). Because this is an untrusted container, the two `forge-status` calls each cost the operator one permission tap (project `allow` rules apply only after trust, RCC line 973); the hooks ran regardless. The architect ends its turn with one sentence. The Stop gate finds no `dirty-*` marker (every mutation went through `forge-status`) and allows.

**0:40 — inside the builder** (invisible to the operator): `SubagentStart` records `agent_7f3a → forge-builder` and injects one line; the builder's `Read` of `brief-01.md` binds it to step 01 (`running`, unbound, owner matches); its edits to `qa/golden_counts.py` pass the fence, an attempted edit to `.github/workflows/weekly-motorized.yml` is denied ("protected path; not in allowed_paths"); it runs `.forge/bin/forge-check T-0007 01 --expect-fail` (red), implements, `.forge/bin/forge-check T-0007 01` (green; `layer-tests` now runs because `layers/nfs_trails/tests` exists; the record is stamped with its `agent_id`), pre-validates with `.forge/bin/forge-gate --handoff T-0007 01 --from-file …` and ends with the HANDOFF. The gate validates on the first try, commits `forge(T-0007/01): golden-bbox QA for nfs_trails [attempt 2]`, persists `report-01.md/json`, runs `step-report` (STATUS: `reported`, `next_action: Dispatch forge-verifier…`), writes the ledger `attempt` row.

**1:30 — the completion notification arrives** in the architect's next turn (RCC line 103). STATUS already says `reported`; the architect's only call is `Agent(subagent_type: "forge-verifier", model: "opus", effort: "medium", prompt: "Verify … range 3e1f9c2..a91b0e4 …")`; the guard allows (step `reported`, `verify_attempts: 0`) and sets `verifying`. The turn ends with nothing dirty. From the phone the operator sees two short messages, one per turn, each ending with what happens next; they never see test output.

**~2:00 onward.** The verifier diffs the committed range, re-runs the checks, returns PASS; the verdict gate runs `step-verdict` → `step-done` (commit `a91b0e4` verified against `.base-01` and `allowed_paths`), `next_action: "/forge-close"`. `/forge-close` writes `handoff.md` (four sections + JSON), promotes the builder's `failed_approaches` entry ("ArcGIS throttles live count queries; use the bulk fixture") to `.forge/lessons/arcgis-throttles-live-count-queries.md`, runs `close` (CHANGELOG line, history row, ledger `close` row with `cost_source: unknown`, commit, `context_state: stale`) and prints `FORGE CLEAR POINT — T-0007 done → next: T-0008 "roads_context: client layer manifest". Run /clear (auto-resume will fire).` The operator types `/clear`; `SessionStart` (`clear`) re-injects the digest and auto-submits "Resume from .forge/STATUS.json: read it, then execute next_action." (marker written; `fresh --no-stamp`). If auto-resume does not fire, the digest already names the next action and `/forge-next` is one tap away.

**Awaiting-external variant.** T-0012 adds `.github/workflows/quarterly-rec_pois.yml` (`--creates` makes it a risk hit → R; `DoD-4` is `check: external`). The Fable verifier grades DoD-1..3 PASS and DoD-4 UNKNOWN with `env-cannot-run`; `step-verdict` parks the task in `awaiting_external` with `next_action: "Run: gh workflow run quarterly-rec_pois.yml && gh run watch; then .forge/bin/forge-status attest T-0012 01 DoD-4 --by <you> --evidence <run url>"`. The operator runs it locally, attests, `/forge-next` re-dispatches the verifier, PASS, `/forge-close --human-ack "riggs reviewed diff <sha>"`.

**Idle variant.** With `task == null`, the digest says `idle; queue: T-0008 (S)`; the operator types `/forge-task …` and declares the files. **Doctor variant.** If the digest is missing, hooks are not running; `/forge-doctor` prints the static report and the operator runs the hooks probe; the RUNBOOK names the causes (`--bare`, `disableAllHooks`, missing `jq`, unexecutable scripts, untrusted plugin form).

---

## 15. Every fatal flaw the judges raised, and how v2 resolves it

| # | Flaw (proposal, judge) | v2 resolution | Where |
|---|---|---|---|
| 1 | Plugin vendored under project `.claude/skills/forge/` as the primary form; does not load untrusted | Plain project layout is the shipped form; the plugin wrapper is user-level, generated, self-silencing, with regex matchers so its gates are live | §1, §8, §10, §13.5 |
| 2 | Plan-first enforced only by the Stop gate | `PreToolUse` fence on edits **and** a Bash mutation guard in the main session; `close`/`step-done` scope backstop | §7 gates 1, 8; §13.3 |
| 3 | Evidence log assumes an exit code in `tool_response`; red runs never captured | Both events registered; exact codes from `forge-check` records; red-then-green on those records | §5.7, §7 gates 3-5 |
| 4 | Driver mode runs `claude -p --agent forge:<role>` | Never `--agent`; `--model fable --effort <architect_effort> --permission-prompts none --allowedTools …` with a plain resume prompt | §6 layer 3b, §13.3 `forge-run` |
| 5 | `initialUserMessage: "/forge-next"` relies on undocumented slash expansion; no loop guard | Plain text; `clear` only; per-task/phase marker; `auto_resume` knob; `fresh --no-stamp` | §6 layer 5 |
| 6 | "Pure bash + jq" but YAML must be parsed | Fenced JSON blocks everywhere a script reads; headings grep-checked | §5 |
| 7 | `agent: forge:planner` namespacing in skill frontmatter unverified | No `context: fork` skills at all; `Agent` tool dispatch only | §2, §13.2 |
| 8 | Architect role in an unscoped rule / CLAUDE.md leaks into workers | SessionStart role handler gated on absent `agent_type`; `omitClaudeMd` on cheap workers | §2, §13.8 |
| 9 | Scope fence cannot tell which step a parallel `agent_id` executes | Bind on first Read of a `running`, unbound brief of the agent's own role; unit-scoped gate checks | §3 step 6, §5.5 |
| 10 | Handoff gate greps the undocumented transcript | Gates depend only on `evidence.jsonl`, `checks/`, `git status`/commits the gate made | §5.5, §12.1 |
| 11 | SubagentStart cannot know the model to inject Sonnet/Haiku paragraphs | Tier-encoded builder files carry them; SubagentStart injects one line | §2, §13.1 |
| 12 | Weakest verification: presence + hedge grep; Stop gate fails open; S skips the verifier | Ordering after last source edit, exact exit codes, tdd, agent-local scope evidence, ratchet, DoD coverage, committed-range verification; Stop gate on `dirty-*` markers | §5.5-5.6, §7 |
| 13 | `rules/` inside the plugin is not a component dir | Stack rules installed by `install.sh` into `.claude/rules/` | §8, §13.9 |
| 14 | Every cost table rests on a different cache assumption | One explicit assumption applied to both arms; list and cached columns; `cost_source` honest | §11 |
| 15 | C0 trivial routed through ceremony | T = one `open`, one `check`, one `close --one-line`; S short handoff | §3 fast paths, §13.2 |
| 16 | Baseline "solo Fable at high" is a strawman | Baseline Fable `low`; bench solo arm identical; ledger flip symmetric and measured-only | §11, §4.3 rule 10 |
| 17 | Skills use `` !`bin/forge-new` `` relying on PATH; a failing injection aborts | `"${CLAUDE_PROJECT_DIR}"/.forge/bin/… --lenient \|\| true`; probes outside injections | §13.2 |
| 18 | `UserPromptSubmit` prompt lock with `onFailure: block` | No prompt lock; `onFailure: block` only on `PreToolUse`/`SubagentStop` | §6, §13.4 |
| 19 | Risk class forces Fable/high everywhere | R: inline Fable at `medium` for small work, `fable/low` builder floor for larger, Fable `medium` verifier, human ack | §4.2, §11 |
| 20 | Spawn guard denies built-ins; every denial wastes a Fable turn | Built-ins allowed and journaled (`general-purpose` denied in settings); denial counter ends the turn after three | §13.3 |
| 21 | M as per-step Sonnet builders | Exactly one step, one builder, one verifier | §4.2, §5.1 |
| 22 | Six-round escalation ladder | Three rounds; `step-start` and the spawn guard refuse beyond the caps; env failures do not escalate | §4.3 rules 6-7 |
| 23 | L triple review | Per-unit Sonnet verifier + one Fable spot-check + full suite | §4.2 |
| 24 | L fan-out via saved workflows | Background `Agent` spawns; sequential default; worktrees only when proven | §3 L path, §12.2 |
| 25 | `.status-written` marker never fires for Bash-written STATUS | Stop gate reads `dirty-*` markers and the sha `forge-status` records | §6 layer 2 |
| 26 | `git subtree add` of a remote subdirectory does not work | `git archive`/release tarball | §10.1 |
| 27 | Stop gate runs to the 8-cap | 2-block soft cap, `stop_hook_active` honoured, fail-open | §6 layer 2 |
| 28 | `watchPaths` on STATUS.json is inert overhead | Not used | §6 |
| 29 | Cache/90%-hit strawman cost model | §11 method | §11 |
| 30 | Verifier skipped for S with a test signal | Verifier when tests change; `forge-check` records at close otherwise; cheap-first needs `tests_present` | §4.2-4.3 |

Honest residuals (§12.2): the interactive `/clear` is instructed; `initialUserMessage` on `clear` is unverified; `permission_denials`/`modelUsage` are observed, not documented; `tool_response` exit codes are best-effort; the main-session Bash guard is a heuristic backed by a deterministic close-time check; worktree parallelism is off until proven; the 8-continuation cap and human hand-edits are detectable, not preventable.

---

## 16. Red-team findings log

Each v1 finding was checked against the research files before being applied. **Applied** = landed as proposed (possibly merged with a sibling finding); **Applied (partial)** = the defect is fixed but one proposed remedy was rejected, with the research line that contradicts it. No finding was rejected outright.

| # | Finding (short) | Decision | Where it landed |
|---|---|---|---|
| 1 | Headless `acceptEdits` cannot run scripts; prompts auto-denied | Applied (RCC lines 1070, 1263, 973 confirm) | §13.3 `forge-run` (`--allowedTools`, `--permission-prompts none`, exit 6 on `permission_denials` [observed]); §13.4 `permissions.allow`; `forge-doctor --driver`; R refusal in driver |
| 2 | Stop gate's `dirty`/`turn` never enforces recording a worker's return | Applied, merged with #35 | §6 layer 2; §13.3 UserPromptSubmit (no `rm dirty`, no `turn`), Stop (`dirty-main`/`dirty-worker`, cleared only by `forge-status`); gates run `forge-status` themselves |
| 3 | Plan gate keyed on `context: fork` `agent_type` (undocumented) | Applied | §2 (Agent-tool dispatch only); §13.2 (`forge-plan` deleted); `forge-task` dispatches `Agent(subagent_type: "forge-planner")` |
| 4 | No per-invocation model for a fork skill; S verifier always Opus | Applied | §13.2 `forge-task` S path (`Agent(... model: "sonnet")`); `forge-verify` deleted; §11 S row |
| 5 | `bin/` vs `.forge/bin/` path mismatch; nothing on PATH | Applied, merged with #26 | Convention paragraph in the preamble; every body/skill/brief uses `.forge/bin/…`; allow rules `Bash(.forge/bin/*)` + per tool; SessionStart PATH export [U]; `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` |
| 6 | `!` injections can fail/time out and abort skills | Applied, merged with #17, #48 | §13.2 (`--lenient`, `--no-probes`, `\|\| true`, probes as explicit steps); HOOKS.md rule |
| 7 | `$CLAUDE_SESSION_ID` is not an env var | Applied (RCC lines 344-353, 557 confirm; sandbox shows `CLAUDE_CODE_SESSION_ID`) | §13.3 universal contract (`.runtime/session-id` from SessionStart stdin); `steps[].started_by`; PostToolUse stamps `main` |
| 8 | L parallel in one tree: whole-tree diff equality fails | Applied, merged with #28, #53 | §3 L path (sequential default); §5.5 unit-scoped `tree_changed`; `.base-NN`; worktree probe; GATES.md note on full-suite authority |
| 9 | Driver never passes `--model`; account default model runs | Applied | §13.3 `forge-run --model fable --effort …`; §13.4 `model: fable`; doctor `modelUsage` assertion [observed] |
| 10 | Bash writes bypass plan-first/scope fences | Applied | §13.3 PreToolUse Bash `looks_mutating`; §5.1 `close`/`step-done` scope backstop; §7 gate 1 relabelled [G]/[G at close] |
| 11 | Verifier `memory: project` vs `disallowedTools` | Applied (option b′, merged with #66) | §2 roster; §13.1 `forge-verifier` (no `disallowedTools`; fence allows only its memory dir; rule order stated) |
| 12 | `classify` sends S to `execute` but S path needs `phase == plan` | Applied | §5.1 `open` (S, X → `plan`; `plan --from` accepts `mode: inline`) |
| 13 | `step-done` records the pre-step HEAD | Applied, merged with #37 | §3 step 8 (gate commits); §5.1 `step-done` verifies descent and pathspec |
| 14 | `stop_hook_active` not read; `onFailure: block` on Stop burns 8 resends | Applied (partial): `stop_hook_active` read and `onFailure` removed; **`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=2` rejected** because RCC line 305 documents the variable only as *raising* the cap | §13.3 Stop; §13.4; §6 failure table |
| 15 | `claude agents --json` lists sessions, not agent definitions | Applied (RCC line 1037 confirms) | §13.3 `forge-doctor` filesystem duplicate check |
| 16 | Plugin hooks use exact matchers that never match `forge:` ids | Applied (RCC lines 121, 139 confirm) | §13.4/§13.5 regex matchers `^(forge:)?…$`; `forge-hook` strips the prefix |
| 17 | `$CLAUDE_PROJECT_DIR` unbraced in skill `!` blocks | Applied | §13.2 (`"${CLAUDE_PROJECT_DIR}"`) |
| 18 | Binding wrong: `npm test` absent; `tests_present` false for the example | Applied (verified: no `scripts` key; only 3 layers have tests) | §5.2 (`worker` todo entry, `exists`); §4.1 `tests_present` definition; §3 example (`tests_present=false`, plan adds tests) |
| 19 | GNU-only `date -d`, bash 4 | Applied, merged with #41 | §5 (epoch fields), §13.3 (jq date math, `shasum` fallback, bash 3.2 syntax, macOS CI, doctor WARN) |
| 20 | `fresh` destroys the interrupted banner; `.gitignore` denied | Applied | §13.3 SessionStart (banner first, `fresh --no-stamp`), `steps[].started_by`; `.gitignore` in the idle allow-list |
| 21 | `/usage` cannot be read by the model; estimated rows feed thresholds | Applied, merged with #59 | §5.8 `cost_source ∈ {measured, operator, unknown}`; §4.3 rule 10 measured-only; §13.2 `forge-close` |
| 22 | `ask` in `-p` is not a human gate | Applied | §3 R overlay; §7 gate 10; §13.3 Bash guard (`deny` in driver) + `forge-run` refusal |
| 23 | Title-token grep forces one-liners into M | Applied (measured 10-22 files here) | §3 step 1 (`open --files/--creates`, `size_source: declared`); §4.1 advisory signals raise-only |
| 24 | Handoff equality fails on untracked files and meta edits | Applied, merged with #27, #53 | §5.5 gate rules (`source_edits ⊆ files_changed`, `tree_changed ⊆ files_changed`, `⊆ allowed_paths`; `.forge/**`/memory excluded) |
| 25 | Verifier diffs an empty committed range | Applied (option b) | §3 steps 8-9; §5.6 `range`; verifier body |
| 26 | `bin/forge-check` "No such file" | Applied (see #5) | everywhere |
| 27 | Memory edit newer than last check fails the gate | Applied | §5.7 `kind: source\|meta`; §5.5 "last `kind: source` edit row" |
| 28 | Shared `.base`, cross-contaminated diffs, unattributable commits in L | Applied (see #8) | §5.1 `.base-NN`; gate commits with pathspec; worktree protocol in §6 |
| 29 | No `permissions.allow`; `-p` cannot answer prompts | Applied (see #1) | §13.4; §10.1 trust caveat; §14 narrative |
| 30 | Greenfield files invisible to risk signals | Applied | §4.1 `risk_hits` over `creates` and every brief's `allowed_paths`; §5.1 `plan` re-match; planner body |
| 31 | No evidence path for external-only checks | Applied | §5.3 `check: external`; §5.1 `attest`, `step-external`, `phase: awaiting_external`; §7 gate 13; §10.4; §14 variant |
| 32 | Cross-cutting refactor has no viable route; `maxTurns` partial return unknown | Applied | §4.2 class **W** + `forge-builder-wide`; `red_ok_until`; `--probe-maxturns` [U] with the UNVERIFIED/resume degraded path |
| 33 | Worked example contradicts its own `risk_paths` | Applied | §5.2 (`qa/golden_counts.py` removed from `risk_paths`); `tests/examples.bats` |
| 34 | STATUS injection unbounded; 10,000-char cap truncates mid-JSON | Applied, merged with #71 | §5.1 bounded `queue`/`history`/`evidence`; `history.jsonl`; §6 layer 4 digest ≤3,000 chars |
| 35 | Background completion vs `rm -f dirty`; wake behaviour unlabelled | Applied (see #2) | §6 layer 2; §13.3 Stop; RCC line 103 cited in §3 step 9 |
| 36 | `layer-tests` fires on layers without `tests/` → exit 4 | Applied (verified) | §5.2 `exists`; §13.3 `forge-check` `skipped` |
| 37 | `step-done` wrong SHA (see #13) | Applied | §3 step 8; §5.1 |
| 38 | State on per-task branches breaks cross-machine truth | Applied | §5.2 `branch_per_task: false` default; `close` pushes behind `ask` when true |
| 39 | `onFailure: block` on Stop → 8× resends (see #14) | Applied | §13.4; §6 |
| 40 | Plan gate `agent_type` for fork undocumented (see #3) | Applied | §2; §12.1 |
| 41 | GNU userland assumptions (see #19) | Applied | §13.3 |
| 42 | `.claude/**` writable by the architect; no `ConfigChange`; MEMORY.md as injection vector | Applied, merged with #69 | §7 gate 14; §13.3 policy lock + `ConfigChange`; §13.4 `deny` on settings edits; GC lint of MEMORY.md |
| 43 | SubagentStart unmatched; binds to the first brief read; `cat` never binds | Applied | §13.4 matcher `forge-.*`; §3 step 6 bind rule (running ∧ unbound ∧ owner); Bash `cat`/`sed -n` bind |
| 44 | Round 2 tree state undefined; block counter not reset | Applied | §4.3 rule 6; §5.1 `step-start --from failed\|clean`; §3 step 10 |
| 45 | `risk_words` substring matches ("ownership") | Applied (verified against README) | §4.1; §5.2 `risk_words` objects with `not:`; §13.3 word-boundary matching |
| 46 | `routing.overrides` has no selector | Applied | §4.4 `paths` globs; §10.4 Android |
| 47 | T close ceremony exceeds the work | Applied, merged with #52 | §3 T path; §5.1 `close --one-line`; §13.2 `forge-close` |
| 48 | `$CLAUDE_PROJECT_DIR`/`CLAUDE_SESSION_ID` in injections and stamping | Applied (see #6, #7) | §13.2; §13.3 PostToolUse stamping |
| 49 | Cold-start test measures the hook, costs a Fable call | Applied | §9 (`--pointers` deterministic; optional Haiku probe with hooks disabled) |
| 50 | Spawn guard compares aliases to full IDs | Applied | §13.3 `aliases.sh` |
| 51 | Cost rows not derived from call counts; implicit cache credit | Applied | §11 method and every row; hooks run `step-start`/`step-report`/`step-verdict`; `open` folds signals; gate commits |
| 52 | T/S pay the full close ritual | Applied (see #47) | §3 T/S paths; `open` collapses new+signals+classify |
| 53 | L parallel gate guarantees blocks (see #8) | Applied | §5.5 agent-local scope; `.base-NN`; worktree protocol |
| 54 | X paid three times; contradicts "Fable codes the hardest" | Applied (REQ line 6, RP §2/§3 confirm) | §3 X path; §4.2 X row; `forge-investigate` skill; fence relaxed for X within scope |
| 55 | M chain-route accounting inconsistent; Fable-low should be default | Applied (partial): accounting corrected, ledger rule symmetric and measured-only, small-M plan written by the architect; **"default M builder = Fable-low" rejected**: REQ line 6 states the user's intent (Opus handles easier tasks) and RP §3's matrix row is "Opus 5.5 `medium` (or Fable `low` if measured cheaper)"; §11 prices the chain route at $7.3 vs $4.2 cached on equal token assumptions | §4.2 M; §4.3 rule 10; §11 M rows; §12.1 |
| 56 | Fable-high planner fork for every M | Applied | §4.2 M-small (architect plan) / M-large (`fable/medium`); §5.3 reduced mandatory headings for M |
| 57 | Gate contracts too strict; hedge grep on prose; blocks are full resends | Applied | §5.5 four mandatory headings, no hedge grep; `forge-gate` self-check; `gate_blocks` in ledger |
| 58 | `effortLevel` never written; bookkeeping at Fable `high` | Applied (RCC line 1025 confirms `high` default and skill `effort:`) | §10.1 installer writes `effortLevel`; §13.2 skill `effort:` keys; `routing.architect_effort` wired to installer and `forge-run` |
| 59 | Interactive cost numbers fabricated (see #21) | Applied | §5.8; §4.3 rule 10; no `spent_usd` in STATUS |
| 60 | Budget countdown induces context anxiety | Applied (RP §1/§2 confirm) | §13.3 UserPromptSubmit and Stop (no budget text); §4.3 rule 9 |
| 61 | No cache TTL; checks expire the 5-minute cache | Applied (RCC lines 48, 949) | §2 roster notes; §13.1 `experimental.cacheTtl`; §13.4 `subagentPromptCacheTtl`; §11 assumption |
| 62 | `maxTurns` is the only interactive runaway guard | Applied | §5.3/§5.4 `max_tool_calls`; §7 gate 2b; lowered `maxTurns` |
| 63 | M "one builder runs all steps" vs per-step gates | Applied | §4.2 M exactly one step; §5.1 `plan` refuses `steps > 1` for M |
| 64 | Verifier re-dispatch uncapped; env failures drive the ladder | Applied | §5.6 `env-cannot-run`; §5.1 `verify_attempts`, `step-external`; §4.3 rule 7; spawn guard cap |
| 65 | Built-in `general-purpose` unguarded on Fable | Applied (RCC lines 80, 82, 87) | §13.4 `env.CLAUDE_CODE_SUBAGENT_MODEL: sonnet`, `deny Agent(general-purpose)`; spawn guard journals builtins; Explore-on-Opus noted |
| 66 | Three overlapping memory surfaces | Applied | §2 roster notes (memory only on the verifier, ≤60 lines); lessons promoted at close |
| 67 | Haiku mechanic may edit shared core / LIVE manifests | Applied (README confirms shared normalizer core and LIVE layers) | §5.2 `mechanic_denied_paths`; §4.3 rule 5; installer seeding |
| 68 | Read-only roles have a denylist shell | Applied | §13.3 `ro_allowed` allow-list; §7 gate 2c |
| 69 | Enforcement layer writable by the agents it governs | Applied (see #42) | §7 gate 14; librarian allow-list |
| 70 | R overlay: Opus builder, human sees only the push | Applied (RP implication 15) | §3/§4.2 R (`fable/low` floor, inline Fable for small R, `--human-ack`); workflows already protected; §11 R row |
| 71 | Never-truncated STATUS grows without bound (see #34) | Applied | §5.1 bounds; §6 digest size check in GC |
| 72 | Workers re-read FORGE.md; CLAUDE.md loads into every worker | Applied (RCC line 44) | §5.4 headings in the brief; `omitClaudeMd` on scout/mechanic/verifier/librarian; one-line SubagentStart |
| 73 | Planner reads all of ROUTING.md | Applied | §4 (`schemas/routing.json`); planner body ("do not read ROUTING.md") |
| 74 | Main-session fence denials uncapped | Applied (RCC line 252 `continue`) | §13.3 denial counter → `continue: false` on the third |
| 75 | Driver splits the budget evenly per phase; bootstrap uncounted | Applied | §4.3 rule 9; §13.3 `forge-run` remaining-budget cap (70% for execute of X/W/R); §11 driver row |

Summary: 75 findings applied; 2 of them (#14, #55) with one proposed remedy each rejected on the research files' evidence, as stated in the table. The v1 cost claims for L ("~55% cheaper") and for T/S ("parity") are withdrawn and replaced by the derived rows in §11.
