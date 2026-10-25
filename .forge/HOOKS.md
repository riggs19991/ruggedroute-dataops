# HOOKS.md — every Forge hook, what it reads, what it does, how to test it

Source of truth: design §13.3 (per-event contract) and §13.4 (registrations); module contract: `forge/docs/MODULE-API.md` §6.
Every registration runs one dispatcher, `.forge/bin/forge-hook` (Python 3.9+, standard library only; ADR 0002), which reads the
hook's stdin JSON once, dispatches on `hook_event_name` (+ `tool_name`), prints **at most one JSON object** on stdout and
**always exits 0**. Logic lives in `.forge/bin/forgelib/hooks.py`; the validators it shares with `forge-gate` and `forge-status`
live in `.forge/bin/forgelib/gates.py`.

## Universal contract

- **Root.** The root is the main checkout that owns `.forge/`, derived from `$CLAUDE_PROJECT_DIR` (else the cwd) **first**:
  `git rev-parse --path-format=absolute --git-common-dir` (trailing `/.git` removed), else `git rev-parse --show-toplevel`, else a
  walk-up. A `$FORGE_ROOT` in the environment is honoured only when it names that same root; one naming another repository is
  ignored with a `forge: WARN ignoring FORGE_ROOT=…` line on stderr (and `/forge-doctor` FAILs `forge-root`). A hook running inside
  a linked worktree still writes `.forge/` state to the main checkout, and edited paths are made relative to the checkout that
  contains them. Every path a fence judges is symlink-resolved; a path that escapes the repository is denied.
- **Session id.** `.forge/.runtime/session-id` (written by SessionStart from stdin `session_id`), fallback `cli`.
  `CLAUDE_CODE_SESSION_ID` is never the primary source [U].
- **Roles.** `agent_type` with a leading `forge:` stripped (plugin namespacing); if absent, `.runtime/agents/<agent_id>.json`
  (written by SubagentStart); if both are absent, main-session rules apply (the stricter ones). A subagent whose role is not a `forge-*` one is a
  **project agent** (a consumer's own QA tester or reviewer): it follows the main-session rules, except that writes under
  `binding.agent_paths` are allowed in any task state (1.0.1; the policy lock, `protected_paths` and the outside-repository
  check still deny, and its `irreversible_commands` are denied rather than asked).
- **Fail closed / fail open.** `PreToolUse` and `SubagentStop` registrations carry `"onFailure": "block"`, and a crash inside the
  dispatcher turns into a deny (PreToolUse) or a block (SubagentStop) naming the exception: one denied call or one blocked return.
  `Stop`, `PreCompact`, `ConfigChange` and the injection events fail **open** with
  `{"systemMessage": "Forge hook crashed (<event>): run /forge-doctor"}` (Stop: `"Forge Stop gate crashed: run /forge-doctor"`), so a
  broken hook never makes Claude Code resend the full context eight times.
- **`--plugin`** (user-level plugin form only): prints nothing and writes nothing unless the resolved root carries a Forge install
  (`.forge/binding.json` or `.forge/STATUS.json`) **and** has no `.forge/VERSION` (the plain-layout install registers its own hooks).
  So the plugin never double-fires in a plain-install repo and is a complete no-op in a repository without the Forge.
- **`--role`**: runs the SessionStart role handler (second SessionStart registration).

## The never-fail rule for `!` injections

A skill's ```` ```! ```` block runs before the model sees the skill, and a failing injection aborts the invocation. Every Forge
injection therefore (1) uses a lenient form that always exits 0 and prints errors as text (`forge-status get … --lenient`,
`forge-doctor --report --no-probes`), and (2) is written as the plain repository-relative command, e.g.
`.forge/bin/forge-status get summary --lenient`, with no `${CLAUDE_PROJECT_DIR}` prefix and no `|| true` chaining. Verified on
2026-10-11 in a headless session: the injection is subject to permission rules, and only the plain form matches the allow rule
`Bash(.forge/bin/forge-status *)`; the quoted absolute form and any chained form were refused and the skill invocation produced
nothing. Probes that start `claude -p` (`--probe-hooks`, `--driver`, …) are **never** run from an injection; skills tell the model
to run them as normal commands. Any new skill must follow the same rules.

## Registrations (`.claude/settings.forge.json`, merged into `.claude/settings.json` by the installer)

Every command is `"$CLAUDE_PROJECT_DIR"/.forge/bin/forge-hook` (plus `--role` for the second SessionStart entry); the installer and
`/forge-doctor` identify Forge entries by that prefix.

| Event | Matcher | Timeout (s) | `onFailure` |
|---|---|---|---|
| SessionStart (digest) | `startup\|resume\|clear\|compact` | 20 | — (fail open) |
| SessionStart (`--role`) | `startup\|resume\|clear\|compact` | 10 | — |
| UserPromptSubmit | (all) | 10 | — |
| PreToolUse | `Edit\|Write\|NotebookEdit\|Agent` | 20 | `block` |
| PreToolUse | `Bash` | 15 | `block` |
| PostToolUse | `Bash\|Edit\|Write\|NotebookEdit\|Read` | 15 | — |
| PostToolUseFailure | `Bash` | 15 | — |
| SubagentStart | `forge-.*` | 10 | — |
| SubagentStop | `^(forge:)?forge-planner$` | 60 | `block` |
| SubagentStop | `^(forge:)?forge-(builder\|builder-wide\|builder-s\|mechanic)$` | 120 | `block` |
| SubagentStop | `^(forge:)?forge-verifier$` | 60 | `block` |
| Stop | (all) | 15 | — (fail open) |
| PreCompact | `manual` | 10 | — (fail open) |
| ConfigChange | `project_settings\|local_settings` | 10 | — (fail open) |
| StopFailure | (all) | 10 | — |
| SessionEnd | (all) | 5 | — |

`onFailure` needs Claude Code ≥ 2.1.295; `/forge-doctor` checks the version and that `onFailure` appears on PreToolUse and
SubagentStop entries only.

## Per-event contract

Exit code is 0 for every row. "Nothing" means empty stdout (allow / no-op).

| Event (matcher) | stdin consumed | Logic | stdout |
|---|---|---|---|
| SessionStart handler 1 | `source`, `session_id`, `cwd`, `agent_type?` | Skip entirely if `agent_type` is set. Create `.runtime/`; write `session-id` and `hooks-alive` `{session_id, ts, source}`. Writes nothing to `$CLAUDE_ENV_FILE` (no PATH or FORGE_ROOT export; MODULE-API §9.3: an export outlives the session that wrote it and leaks another checkout's scripts into later shells). **Compute the banner first**: INTERRUPTED if a step is `running` with `started_by != session_id` and no report (or `agent_id == null` and no evidence rows after `started_ts`: that form names `.forge/bin/forge-status recover <id> <NN>`, with `--force` when this session started the step, then "re-dispatch per next_action", since `step-start` refuses a running step and the dispatch runs `step-start` itself); STALE if `.runtime/stale-status` exists. Then the digest, in this order, truncating later items to fit 9,800 chars: (1) `forge-status get digest` (≤3,000 chars), (2) banner, (3) newest `handoff.md` or `report-NN.md` *Remaining* + *Gotchas / do not touch*, (4) `git status --short` (first 20 lines) + `git log --oneline -5`, (5) `lessons/INDEX.md` first 40 lines, (6) binding digest (verify names, protected/risk/important globs, notes), (7) VERSION drift. On `source == "clear"` ∧ `context_state == stale` ∧ `binding.auto_resume`: with a task open and a `next_action`, and no `.runtime/auto-resumed-<task>-<phase>` marker → `initialUserMessage` "Resume from .forge/STATUS.json: read it, then execute next_action."; with no task open (the CLEAR POINT after `close`, which nulls the task) and a non-empty queue, and no `.runtime/auto-resumed-idle-<queue[0].id>` marker → `initialUserMessage` "Resume from .forge/STATUS.json: start the first queued task with /forge-task"; either way write the marker, then `forge-status fresh --no-stamp`. On `clear` with no task open, `context_state == stale` and an empty queue (or `auto_resume` off): `forge-status fresh --no-stamp` alone. Never on `compact` or `startup`. | `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"<digest>","sessionTitle":"forge <id> <phase>"[,"initialUserMessage":"Resume from .forge/STATUS.json: …"]}}` |
| SessionStart handler 2 (`--role`) | `agent_type?` | If `agent_type` is empty, emit `.forge/ROLE-architect.md` verbatim (≤4,000 chars). | `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"<role>"}}` or nothing |
| UserPromptSubmit | `prompt`, `session_id` | Reset `stop-blocks` to 0; remove `denials`; prompt starting with `?` → touch `chat-turn`, else remove it; **never touches `dirty-*`**. Reminder: `Forge: <id> class <C> risk <R> phase <p> next: <next_action, 120 chars>` plus ` \| context stale since <ts>; /clear recommended` when stale, or `Forge: idle; /forge-task <title> to start`. No budget text, ever. | `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"<line>"}}` |
| PreToolUse (`Edit\|Write\|NotebookEdit`) | `tool_name`, `tool_input.file_path`/`.notebook_path`, `agent_id?`, `agent_type?` | **Policy lock first** (gate 14): deny paths in `install-manifest.json`, `.claude/settings*.json`, `.forge/binding.json`, `.forge/schemas/**`, `.forge/ledger.jsonl`, `.forge/history.jsonl`, `.forge/STATUS.json`. **Outside the repository** (lexically or through a symlink) → deny, every session. **Subagents**: first allow the agent's own pre-validation draft `.forge/tasks/<task>/drafts/<agent_id>-*.md` (never committed); `forge-verifier` → allow only `.claude/agent-memory/forge-verifier/**` (allow-list before deny); `forge-scout` → deny; `forge-planner` → allow only `.forge/tasks/<task>/**`; `forge-librarian` → allow only `.forge/lessons/**`, `.forge/COST-REPORT.md`, `.forge/archive/**`, `.forge/decisions/**`, `CLAUDE.md`, `.claude/agent-memory/**`; builders/mechanic → deny any `.forge/**`; require a bound brief ("Read your brief file with the Read tool before editing"); **tool budget**: deny once this agent's tool calls (hook-owned counter in its agent record, never below its `bash\|edit` evidence rows) ≥ `brief.max_tool_calls`; deny outside `brief.allowed_paths`; deny existing `test_globs` files unless `may_edit_tests`; deny `protected_paths` for `forge-builder-s`, `forge-mechanic`, `forge-builder-wide` always and for `forge-builder` unless `task.risk == "R"`; deny `risk_paths ∪ mechanic_denied_paths` for `forge-mechanic`; **project agents** (any other `agent_type`, 1.0.1): allow a path matching `binding.agent_paths` unless it is a `protected_paths` match; otherwise the main-session rules below, with the globs named in the denial. **Main session**: allow `.forge/tasks/<open task>/**` (another task's directory is denied), `.forge/lessons/**`, `.forge/decisions/**`, `.forge/CHANGELOG.md`, `.forge/COST-REPORT.md`, `.claude/agent-memory/**`, `.claude/rules/project-*.md`, `CLAUDE.md`, `.gitignore`; otherwise deny when no task is open, when class ∈ {M,W,L}, when class ∈ {S,X} and `task.plan == null`, when the path is outside `task.scope` (class X: the reason names `.forge/bin/forge-status scope add <id> <path> --why "…"`), and on `protected_paths` unless risk R; on allow touch `dirty-main` and remove `chat-turn`. **Denial counter**: `.runtime/denials` counts per rule; the third denial of one rule in a turn adds `"continue": false, "stopReason": "Fence: <rule>. Run /forge-next."`. | deny JSON (+ `continue:false` on the third); allow: nothing |
| PreToolUse (`Agent`) | `tool_input.subagent_type`, `.model?`, `.effort?`, `.prompt`, `.run_in_background?`, `.isolation?` | `isolation: worktree` while `binding.git.worktree_isolation` is not true → deny (run `.forge/bin/forge-doctor --worktree` first). Non-`forge-*` type → journal + ledger `builtin` row, allow. `forge-scout` → allow (no task needed). No open task and type ≠ `forge-librarian` → deny. Effective model/effort = alias of `tool_input.model` (else the agent default) / `tool_input.effort` (else default): builder opus/medium, wide fable/low, -s sonnet/medium, mechanic haiku/medium, verifier opus/medium, planner fable/high. `forge-planner` → allow iff `phase == plan` ∧ the architect is not the plan author ∧ effort medium (M) or high (W, L). `forge-librarian` → allow. Phase `intake` → deny builders and verifiers ("answer needs_clarification, then re-run forge-status plan"). Builders → a step with the same agent/model/effort that is `pending`, or `running` ∧ `agent_id == null` ∧ `attempts ≥ 1` (pre-started retry) with no live `.runtime/dispatched-<task>-<step>` marker; none → deny naming the expected triple or "run .forge/bin/forge-status step-start <id> <NN> --from failed\|clean first"; on allow for a pending step run `forge-status step-start` (its refusal becomes the deny); write the dispatch marker (cleared when the worker binds). `forge-verifier` → allow iff a step is `reported` with matching routing and `verify_attempts < 2` for the current attempt (`step-start` resets it; or a ruling), or S with sonnet/opus in `execute`, or X with fable, or L with all units done and fable, or risk R with fable; on allow run `forge-status step-verifying`. Journal and ledger `dispatch` row. | deny JSON; allow: nothing |
| PreToolUse (`Bash`) | `tool_input.command`, `agent_id?`, `agent_type?`, `permission_mode`, `scratchpad_dir?` | **Subagents** (per segment, quote-aware; GATES.md §The Bash guards): git only by an allow-listed subcommand (`push`, `reset`, `checkout`, `stash` other than `list\|show`, … denied); `ln` denied; `.forge/` named only by `forge-check`, `forge-gate` (draft or brief), `forge-status get`, or a `cat`/`sed -n`/`head` of the brief; `forge-doctor\|forge-run\|forge-bench\|forge-hook` denied; writes to `CLAUDE.md`, `.gitignore`, `.claude/**` denied; path arguments symlink-resolved; `rm -r` whose target (quotes stripped, `~` and `$VAR` expanded, `..` collapsed, relative to the repository root, then symlink-resolved) lies inside the repository or outside `/tmp`, `$TMPDIR` and the scratchpad is denied (so `/tmp/../<repo>` and `<scratchpad>/../../x` are denied), as is any writing `forge-status` subcommand and any `irreversible_commands` pattern; read-only roles → deny unless `ro_allowed`; builders → tool budget; `cat`/`sed -n`/`head` of a `brief-NN.md` → bind (same rule as PostToolUse Read). **Main session**: `irreversible_commands` → `ask` when `.runtime/driver` is absent (interactive), `deny` when present (driver mode); `looks_mutating` → deny when no task is open, class ∈ {M,W,L}, or class ∈ {S,X} without a plan; an allowed mutating command touches `dirty-main`; denial counter as above. **Project agents** (non-`forge-*` subagents, 1.0.1): `irreversible_commands` → deny; a `looks_mutating` command the fence would deny is allowed instead when every write target lies under `binding.agent_paths` — redirect targets and the operands of `rm|rmdir|mv|cp|mkdir|touch|tee|chmod|chown|truncate|sed -i`, `cd` tracked across segments, heredoc bodies ignored — and none is policy-locked, protected or outside the repository; git, `ln`, `patch`, `dd`, `rsync`, `cd -` and an interpreter fed a heredoc, `<` or `-c`/`-e` fall back to the fence (deny, globs named). | deny/ask JSON; allow: nothing |
| PostToolUse (`Bash\|Edit\|Write\|NotebookEdit\|Read`) | `tool_name`, `tool_input`, `tool_response`, `agent_id?`, `agent_type?`, `session_id` | `Read` (subagent) of `.forge/tasks/<id>/brief-NN.md` whose step is `running` ∧ unbound ∧ `owner_agent == role` → `forge-status step-bind` and merge `{task, step, brief, bound_at}` into `.runtime/agents/<agent_id>.json`; otherwise journal only. `Edit\|Write\|NotebookEdit` → evidence row `{event: edit, kind: source\|meta, file}` (`agent_id: main` in the main session); main-session `source` edit → touch `dirty-main`. `Bash` → evidence row `{event: bash, ok: true, cmd, exit}` (`cmd` credential-redacted and capped at 300 chars; exit best-effort from `tool_response`, else `null`, [U]); a subagent's Bash/Edit/Write also increments the `tool_calls` counter in its agent record; a command containing `forge-check <task> <step>` stamps the newest `checks/<step>-*-unknown.json` (≤300 s old) with the real `agent_id` (or `main`); main-session `looks_mutating` → touch `dirty-main`. | nothing |
| PostToolUseFailure (`Bash`) | `tool_input.command`, `error`, `agent_id?` | Evidence row `{event: bash, ok: false, exit, cmd, error_head: <200 chars>}`; stamp check records as above. | nothing |
| SubagentStart (`forge-.*`) | `agent_id`, `agent_type` | Write `.runtime/agents/<agent_id>.json` `{agent_id, agent_type, started_ts, session_id, task?, verify_step?}`; inject one line (reaching the worker is [U]; the brief carries everything). | `{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":"Forge worker: read the brief …"}}` |
| SubagentStop (planner) | `agent_id`, `agent_type`, `last_assistant_message`, `stop_hook_active` | `plan_validate` (= `forge-gate --plan`) and the message ends with `PLAN-FILE:`; on failure block with the first three defects + `forge-status gate-block`; after 2 blocks allow and journal `PLAN-GATE-BYPASSED` (`forge-status plan` still refuses the import). | `{"decision":"block","reason":"<defects>"}` or nothing |
| SubagentStop (builders, mechanic) | same | Resolve task/step from the agent record (unbound → block "you never read a brief", counted); `handoff_validate` on `last_assistant_message` (SCHEMAS.md §Handoff); on failure block with the defects + `gate-block`; after 2 blocks allow and persist with `status: UNVERIFIED` (no commit). A resumed worker's non-handoff answer on a step whose report is on file → journal only (nothing persisted). On allow: persist `report-NN.md/json` (a bypass stub never overwrites a recorded report: it goes to `report-NN.unverified.*`); for `DONE\|DONE_WITH_CONCERNS` run `git add -A -- <allowed_paths> .forge/tasks/<id>/ ':(exclude).forge/tasks/<id>/drafts' && git commit -q -m "forge(<id>/<NN>): <title> [attempt N]"` and record the sha; run `forge-status step-report`; if that fails touch `dirty-worker` + journal; ledger `attempt` row with `gate_blocks`. | block JSON or nothing |
| SubagentStop (verifier) | same | Skip (journal only) when the step is no longer `verifying` or this agent's inline verdict is already on file. `verdict_validate` (external criteria need a `-human.json` record); 2-block cap then allow with `verdict: UNKNOWN`; persist `verdict-NN.md/json`; run `forge-status step-verdict` (numbered step → done / fail / external; step `main` → `task.inline_verdict`, which `close` requires for X and for S with changed tests); on failure touch `dirty-worker`; ledger `verdict` row. | block JSON or nothing |
| Stop | `stop_hook_active`, `session_id` | Allow when no task is open or `phase ∈ {done, blocked, idle, awaiting_external}`; allow when `stop_hook_active` ∧ STATUS sha == `.runtime/last-block.sha`; allow a `chat-turn` with no `dirty-*`. Reason, first match: `dirty-worker` → "a worker's report/verdict was persisted but STATUS was not updated: run .forge/bin/forge-status <step-report\|step-verdict> <id> <NN>"; `dirty-main` → "record the state with .forge/bin/forge-status (<suggested subcommand>) before ending the turn", where the suggestion fits the first step that is not done (`running` → `step-report` or `recover`; `reported`/`verifying` → `step-verdict`; `failed` → `step-start --from failed\|clean`; `blocked` → `step-start --from failed\|clean` or `block --on`; `awaiting_external` → `attest`; `pending` → dispatch per next_action) and is `close` only when every step is done; sha ≠ `.runtime/status.sha` → "STATUS.json was edited by hand: .forge/bin/forge-status validate --restamp". No reason → allow. `stop-blocks ≥ 2` → allow with a `systemMessage`, touch `stale-status`, journal; else increment `stop-blocks`, record the sha in `last-block.sha`, block. | block JSON, `{"systemMessage":"…"}` or nothing |
| PreCompact (`manual`) | `trigger` | Block iff `dirty-main` or `dirty-worker` exists: "checkpoint with .forge/bin/forge-status, then /compact". `auto` compaction is never registered, so never blocked. | `{"decision":"block","reason":"…"}` or nothing |
| ConfigChange (`project_settings\|local_settings`) | `source`, `file_path?` | Compare the Forge hook entries in the changed file with `.claude/settings.forge.json` (matchers, commands, `onFailure`); a missing or altered Forge entry → block + journal `CONFIG-GUARD`, unless `.runtime/gate-disabled-<name>` exempts it. Whether a block prevents the reload is [U]; `/forge-doctor` diffs settings either way. | `{"decision":"block","reason":"Forge hooks changed: run install.sh --upgrade, or (operator only, from a shell) .forge/bin/forge-doctor --disable-gate <name> (…)"}` or nothing |
| StopFailure | whole stdin | Write `.forge/incidents/<ts>-stopfailure.json`; journal. | nothing |
| SessionEnd | `reason`, `session_id` | Write `.runtime/last-session.json` `{session_id, reason, ts, task, phase, step_running}`; journal. | nothing |

## One test line per event

Run from the repository root of a repo with the Forge installed and **no task open** (idle STATUS). Each line pipes a hand-written
stdin into the dispatcher exactly as Claude Code would; `echo $?` after any of them prints `0`.

SessionStart writes nothing to `$CLAUDE_ENV_FILE` (MODULE-API §9.3), so the lines are safe to run inside a live session. The
first line still unsets `FORGE_ROOT`: an old session's stale `FORGE_ROOT` naming another checkout is ignored with a WARN, and
`/forge-doctor` reports it as a FAIL `forge-root` line.

```bash
unset FORGE_ROOT
export CLAUDE_PROJECT_DIR=$PWD
# SessionStart → additionalContext with the digest ("idle (project …)", git state, binding digest); writes .forge/.runtime/hooks-alive
echo '{"hook_event_name":"SessionStart","source":"startup","session_id":"test-session","cwd":"'"$PWD"'"}' | .forge/bin/forge-hook
# SessionStart --role → additionalContext = .forge/ROLE-architect.md (nothing when agent_type is present)
echo '{"hook_event_name":"SessionStart","source":"startup","session_id":"test-session"}' | .forge/bin/forge-hook --role
# UserPromptSubmit → "Forge: idle; /forge-task <title> to start"
echo '{"hook_event_name":"UserPromptSubmit","prompt":"hello","session_id":"test-session"}' | .forge/bin/forge-hook
# PreToolUse Edit → deny "No Forge task is open: /forge-task <title> first"
echo '{"hook_event_name":"PreToolUse","tool_name":"Edit","tool_input":{"file_path":"lib/foo.py"},"session_id":"test-session"}' | .forge/bin/forge-hook
# PreToolUse Write on a policy file → deny "Forge-owned or policy file: change it with install.sh or by hand"
echo '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":".forge/STATUS.json"},"session_id":"test-session"}' | .forge/bin/forge-hook
# PreToolUse Agent → deny (no task open); with step 01 pending at opus/medium the same line is allowed (alias-normalized) and runs step-start
echo '{"hook_event_name":"PreToolUse","tool_name":"Agent","tool_input":{"subagent_type":"forge-builder","model":"claude-opus-5-5","effort":"medium","prompt":"x"},"session_id":"test-session"}' | .forge/bin/forge-hook
# PreToolUse Bash, mutating → deny "source changes go through the fence …"
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"sed -i s/a/b/ lib/foo.py"},"session_id":"test-session"}' | .forge/bin/forge-hook
# PreToolUse Bash, irreversible (binding pattern "git push *") → ask (interactive); deny when .forge/.runtime/driver exists
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git push origin main"},"session_id":"test-session"}' | .forge/bin/forge-hook
# PostToolUse → nothing on stdout (with a task open it appends an evidence row)
echo '{"hook_event_name":"PostToolUse","tool_name":"Bash","tool_input":{"command":"ls"},"tool_response":{"stdout":""},"session_id":"test-session"}' | .forge/bin/forge-hook
# PostToolUseFailure → nothing on stdout
echo '{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","tool_input":{"command":"false"},"error":"Exit code 1","session_id":"test-session"}' | .forge/bin/forge-hook
# SubagentStart → the one-line worker reminder; writes .forge/.runtime/agents/agent_t1.json
echo '{"hook_event_name":"SubagentStart","agent_id":"agent_t1","agent_type":"forge-builder","session_id":"test-session"}' | .forge/bin/forge-hook
# SubagentStop (builder, never read a brief) → block "Handoff gate (1/2): you never read a brief …"
echo '{"hook_event_name":"SubagentStop","agent_id":"agent_t1","agent_type":"forge-builder","last_assistant_message":"hi","stop_hook_active":false,"session_id":"test-session"}' | .forge/bin/forge-hook
# Stop → nothing (idle: allow)
echo '{"hook_event_name":"Stop","stop_hook_active":false,"session_id":"test-session"}' | .forge/bin/forge-hook
# PreCompact manual → nothing (no dirty marker); block JSON when .forge/.runtime/dirty-main exists
echo '{"hook_event_name":"PreCompact","trigger":"manual","session_id":"test-session"}' | .forge/bin/forge-hook
# ConfigChange → nothing when the Forge hook entries match settings.forge.json; block JSON when one was removed
echo '{"hook_event_name":"ConfigChange","source":"project_settings","file_path":"'"$PWD"'/.claude/settings.json","session_id":"test-session"}' | .forge/bin/forge-hook
# StopFailure → nothing; writes .forge/incidents/<ts>-stopfailure.json
echo '{"hook_event_name":"StopFailure","error":"overloaded","session_id":"test-session"}' | .forge/bin/forge-hook
# SessionEnd → nothing; writes .forge/.runtime/last-session.json
echo '{"hook_event_name":"SessionEnd","reason":"exit","session_id":"test-session"}' | .forge/bin/forge-hook
```

These lines run the dispatcher directly; they prove the scripts, not that Claude Code fires them. That is what
`.forge/bin/forge-doctor --probe-hooks` checks (one `claude -p` turn, then `.forge/.runtime/hooks-alive` must have been rewritten).
`claude --debug` and `/hooks` show what Claude Code actually loaded and ran (RUNBOOK.md §Debugging hooks).
