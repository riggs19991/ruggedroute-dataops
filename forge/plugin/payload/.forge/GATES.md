# GATES.md — every Forge gate, what enforces it, and how sure we are

Source: design §7 (gate table), §5.5-5.6 (handoff and verdict rules), §13.3 (hook logic). Order of authority: deterministic
checks → hook-audited evidence → fresh-context verifier → architect adjudication → human gate. Prose is advisory; hooks and
scripts are the law.

## Labels

- **[G]** guaranteed: a hook, a setting, a script refusal or a process boundary decides it.
- **[G/cap]** guaranteed up to a documented platform ceiling (the 8-continuation Stop cap).
- **[G at close]** not prevented mid-task, but refused deterministically by `forge-status close` / `step-done`.
- **[I]** instructed: prompt or ritual text; nothing enforces it.
- **[U]** unverified against the research files; a fallback and a doctor probe are named.

## The gates

| # | Gate | What it checks | Enforced by | Label |
|---|---|---|---|---|
| 0 | Plan gate | Plan exists with the mandatory headings for its class (M: 4; W/L: 12; S/X inline: 2), parseable plan-meta, ≥1 `DoD-`, one valid brief per step, `max_tool_calls` per step, rollback command for R, baseline shape (`forge-status plan` records the real baseline at import when the template value is left); routing obeys ROUTING.md rules; M and W have one step; risk re-matched on every brief's paths; `red_ok_until` points forward | `SubagentStop` (`^(forge:)?forge-planner$`) + `forge-status plan` (+ `.forge/bin/forge-gate --plan` for the architect's own plans) | [G] |
| 1 | Plan-first / scope fence (main session) | No source `Edit\|Write\|NotebookEdit` without an open task; never for M/W/L; not before `plan.md` for S/X; not outside the declared `scope` for T/S/X; `.forge/tasks/<id>/` only for the open task; the Bash mutation heuristic under the same conditions; three same-rule denials in a turn → `continue: false`. Every session and role: a path that escapes the repository (lexically or through a symlink) is denied, and a symlink inside it is judged by its resolved target | `PreToolUse` | [G] tool edits; [G at close] shell writes (gate 8 backstop) |
| 2 | Scope fence (workers) | Edits only inside the brief's `allowed_paths` (plus the agent's own draft `.forge/tasks/<id>/drafts/<agent_id>-*.md`); existing tests only with `may_edit_tests`; protected / risk / mechanic-denied paths by tier; any other `.forge/**` never; the worker must be bound to a running, unbound brief of its own role; `isolation: worktree` spawns only when `binding.git.worktree_isolation` is true | `PreToolUse` inside subagents (`agent_id`/`agent_type`) | [G] |
| 2b | Tool budget | Bash/Edit/Write denied once this agent's tool calls (the larger of the hook-owned counter in `.forge/.runtime/agents/<agent_id>.json` and its `bash\|edit` evidence rows) reach `brief.max_tool_calls` ("write your HANDOFF with status BLOCKED") | `PreToolUse` | [G] |
| 2c | Read-only roles | `forge-scout`, `forge-verifier`, `forge-planner`: a Bash **allow-list** (every segment must be a listed command; §The Bash guards below) plus a **deny list** applied to the whole command: `$(…)`, backticks, `${`, `<(…)`/`>(…)`, output redirects (except `N>&M`, `N>/dev/null`), heredocs, `find -exec\|-execdir\|-ok\|-delete\|-fprint*`, `--output`, `sort -o`, `xargs`, `eval`, `tee`, `sed -i`, `perl`, interpreter `-c`/`-e`; Edit/Write denied except the verifier's memory directory, the planner's `.forge/tasks/<id>/` and each agent's own draft file | `PreToolUse` (`Bash`, `Edit\|Write`) | [G] for the listed constructs and unlisted command words; residual: allowed commands that run project code (test runners, verify commands) or carry a write flag the list does not know |
| 2d | Project-agent paths | A subagent outside the `forge-*` roles (a consumer's QA tester, a reviewer) may `Edit\|Write` a path under `binding.agent_paths` (project-owned globs, default `[]`) in any task state, and run a write-shaped shell command whose every target lies there; the policy lock, `protected_paths` and the outside-repository check still deny; its `irreversible_commands` are denied; everything outside the globs follows gate 1, with the globs named in the denial | `PreToolUse` (`Edit\|Write`, `Bash`) | [G] tool edits; shell writes by the gate-1 heuristic (targets read off the command line; a shape it cannot read falls back to gate 1) |
| 3 | Mechanical checks, exact exit codes | `forge-check` runs `binding.verify[]` (filtered by `when`; missing `exists` → `skipped`) ∪ brief `checks[]` ∪ the step's plan-meta DoD check commands (step `main`: every DoD check), prints one `FORGE_CHECK name=… exit=…` line per command, writes the `checks/` record, runs the test ratchet against `plan-meta.test_baseline` | `.forge/bin/forge-check` | [G] |
| 4 | Evidence capture | Every Bash/Edit/Write tool event with `agent_id`, `kind`, success and failure, appended to `evidence.jsonl` | `PostToolUse` + `PostToolUseFailure` | [G] (Bash exit code inside `tool_response` is best-effort [U]; exact codes come from gate 3) |
| 5 | Handoff gate | Mandatory headings + JSON; `files_changed ⊆ allowed_paths`; this agent's source edits and the unit's tree changes ⊆ `files_changed` (drafts excluded); checks run after the last source edit at exit 0; `tdd`: a failing record of each `expected_fail_first` cmd (by any agent, so a retry inherits attempt 1's red run) earlier than this agent's green record; two-block cap → `UNVERIFIED`; commits (drafts excluded) and records on allow; a resumed worker's non-handoff answer is journaled, never persisted over the report | `SubagentStop` (builders, mechanic), `onFailure: block` | [G] |
| 6 | Fresh-context verifier | Brief + DoD + committed range + report; re-runs `forge-check`; grades each `DoD-` id; scope check; ratchet; flags only gaps that affect correctness or the stated requirements; `env-cannot-run` tag | agent body + verdict gate | [G] shape, [I] judgment |
| 7 | Verdict gate | Every DoD id graded once with cmd + numeric exit; PASS only when everything passes; every cited cmd has a check record by this verifier (`forge-check <task> <step>` runs the step's DoD checks too; external criteria: a human attest record, else UNKNOWN); tags from the fixed list; runs `step-verdict` on allow (a numbered step → done / failed / external; step `main` → `task.inline_verdict`) | `SubagentStop` (`^(forge:)?forge-verifier$`), `onFailure: block` | [G] |
| 8 | Transition guard + scope backstop | `step-done` without PASS impossible; the step commit must descend from `.base-NN` and touch only `allowed_paths ∪ .forge/tasks/<id>/**`; `plan` with illegal routing impossible; `step-start` refused in phase `intake`; `close` with a non-done step, an out-of-scope tree or out-of-scope commits impossible without `--accept-out-of-scope` + ruling (files under `binding.agent_paths` never count); `close` of class X, or of class S that changed a `test_globs` file, impossible without a PASS verdict on step `main` (a FAIL/UNKNOWN on file always refuses; `--partial` excepted) | `.forge/bin/forge-status` | [G] |
| 9 | Spawn routing guard | `forge-*` worker spawns must match a pending step (or a retry pre-started with `step-start --from failed\|clean` and not yet dispatched) by agent/model/effort, alias-normalized; no builder or verifier in phase `intake`; verifier only on a `reported` step with `verify_attempts < 2` for the current attempt (`step-start` resets it), or inline per class; planner only in `phase: plan`; runs `step-start` / `step-verifying` on allow; **`forge-scout` and `forge-librarian` are exempt** (no step; any model/effort; the scout even with no task open); `general-purpose` denied in settings; built-in spawns journaled as `builtin` | `PreToolUse` (`Agent`) + `permissions.deny` | [G] |
| 10 | Risk / human gate | `irreversible_commands` → `ask` for the main session in interactive mode; `deny` for subagents always and for the main session in driver mode (`forge-run` refuses the phase: `blocked`, `blocked_on: "human gate: <cmd>"`); `close --human-ack` for R | `PreToolUse` (`Bash`) + settings `ask` + `forge-run` + `forge-status` | [G interactive / blocked in driver] |
| 11 | Stop gate | STATUS reflects every mutation (`dirty-main`, `dirty-worker`, hand-edit sha); `?` chat-turn exemption; `stop_hook_active` honoured; 2-block soft cap then `stale-status`; fails open on crash | `Stop` | [G/cap] |
| 12 | Claims audit | `forge-status evidence` accepts only claims that point at a `checks/` record; `close` refuses a handoff whose *Done, with evidence* bullets lack a command, and a T `--one-line` without a passing check record | `.forge/bin/forge-status` | [G] |
| 13 | External verification path | `check: external` criteria pass only on a human `attest` record; `phase: awaiting_external` holds the task with the exact commands to run | `forge-status attest` + verdict gate | [G] |
| 14 | Policy-file lock | Model edits (main session and every subagent) to Forge-owned files (`install-manifest.json` list: scripts, schemas, templates, the `.forge/*.md` docs), `.claude/settings*.json`, `.forge/binding.json`, `.forge/STATUS.json`, `.forge/ledger.jsonl`, `.forge/history.jsonl` are denied; `ConfigChange` blocks a settings reload that drops or alters a Forge hook entry | `PreToolUse` + `ConfigChange` + settings `deny` | [G] (whether a ConfigChange block prevents the reload is [U]; `/forge-doctor` diffs settings either way) |
| 15 | System self-check | `/forge-doctor`: `forge-root` (FAIL when `$FORGE_ROOT` names another repository), `python` ≥ 3.9, `claude-cli` ≥ 2.1.295, `trust`, `version`, `manifest`, `binding`, `status`, `settings-hooks` and `settings` against `settings.forge.json`, `bin` executables, `gitignore`, `duplicate-agents`, `hooks-alive`, `digest` size, `pointers` (FORGE.md); optional probes (`--probe-hooks`, `--driver`, `--probe-clear`, `--worktree`, `--probe-maxturns`, `--probe-coldstart`) | `.forge/bin/forge-doctor` | [G] |

Not used as gates, on purpose: `TaskCompleted`/`TeammateIdle` (teams are experimental and interactive-only), `/goal`, transcript
grepping (undocumented), `context: fork` skills (their `agent_type` is undocumented), saved workflows.

## The Bash guards are heuristics, backed by deterministic checks

Segments are split on `&&`, `||`, `;`, `|`, `|&`, newlines and a lone `&`, outside quotes (an unterminated quote splits
everywhere: fail closed).

- **Main session (gate 1):** `looks_mutating(cmd)` flags `sed -i`, `tee`, `rm`, `mv`, `cp`, `ln`, `chmod`, `chown`, `truncate`,
  `patch`, `dd`, `rsync`, `git checkout|reset|clean|stash|rebase|merge|apply|cherry-pick|revert|restore|switch|rm|mv|worktree|…`
  (after `-C <dir>`/`-c k=v`), `python3 -c`, `node -e`, `perl -e`, `sh -c`, output redirects and heredocs, unless every segment is
  `.forge/bin/*`, a read/commit git command, or a `binding.verify[]` / `bootstrap` / `smoke` prefix. A determined shell write can
  slip past a regex. The backstop is deterministic: `forge-status close` and `step-done` compare `git status --porcelain ∪
  git diff --name-only <base>..HEAD` with the declared scope and refuse anything outside it (gate 8). So: **[G] for tool edits,
  [G at close] for shell writes.**
- **Project agents (gate 2d, 1.0.1):** a command `looks_mutating` flags is allowed for a non-`forge-*` subagent when every write
  target lies under `binding.agent_paths`: redirect targets (`>`, `>>`, `&>`, `N>`; not `N>&M` or `/dev/null`) and the operands of
  `rm`, `rmdir`, `mv`, `cp` (destination), `mkdir`, `touch`, `tee`, `chmod`, `chown`, `truncate` and `sed -i`, flags and their values
  removed, `cd` tracked across segments, heredoc bodies dropped (a `<<<` here-string hides nothing). Every target is symlink-resolved,
  must stay inside the repository, must not be policy-locked or protected. `git`, `ln`, `patch`, `dd`, `rsync`, `pushd`, `cd -`, a
  dangling redirect and an interpreter fed a heredoc, `<` or `-c`/`-e` have unreadable targets: the plain gate-1 denial applies.
  **[G] for tool edits**; shell writes carry the same residual as gate 1 (a script the agent runs may write anywhere).
- **Read-only roles (gate 2c):** an **allow-list** plus a **deny list**. Allowed command words: `rg` (no `--pre`), `grep`, `egrep`, `fgrep`,
  `find`, `ls`, `cat`, `head`, `tail`, `wc`, `cut`, `tr`, `jq`, `diff`, `cmp`, `stat`, `file`, `pwd`, `echo`, `printf`, `test`, `[`,
  `true`, `false`, `which`, `basename`, `dirname`, `realpath`, `readlink`, `du`, `tree`, `nl`, `column`, `comm`, `paste`, `pytest`, `sort` (no `-o`), `uniq` (one input), `sed -n` (no `w`/`W`/`e`), `awk` (no `system`, redirect,
  pipe or program file), `cd <dir>`, read-only git subcommands (`log`, `diff`, `show`, `status`, `grep`, `blame`, `ls-files`,
  `rev-parse`, `stash list|show`, … without `--output`/`-O`), `python -m pytest|unittest|json.tool`, `npm test`, `npx jest`,
  `./gradlew test…`, `timeout <n> <allowed command>`, `binding.verify[].cmd` prefixes, and `.forge/bin/forge-check` (its `--cmd`
  must pass the same list), `.forge/bin/forge-gate`, `.forge/bin/forge-status get`. The deny list (gate 2c row) is applied to the
  whole command first. **[G]** for exactly those constructs: a command word not on the list is refused, and so is any denied
  construct anywhere. **Residual, not guaranteed:** a test runner or verify command executes project code, which can write
  anything; and an allowed word may have a write flag the deny list does not know (today: `tree -o <file>`, `file -C`). The handoff
  gate's `tree_changed` check and the step-done/close pathspec checks (gate 8) catch tree changes such a write leaves.
- **Workers (gate 2):** git is allow-listed by subcommand after its global options (`add`, `commit`, `status`, `log`, `diff`, `show`,
  `rev-parse`, `ls-files`, `blame`, `grep`, `describe`, `rev-list`, `cat-file`, `name-rev`, `shortlog`, `stash list|show`; `push`
  and everything else denied); `ln` denied; a segment naming `.forge/` is denied unless it runs `.forge/bin/forge-check`,
  `.forge/bin/forge-gate` (naming at most the agent's draft or brief) or `.forge/bin/forge-status get`, or reads the brief with
  `cat`/`sed -n`/`head`; `forge-doctor`, `forge-run`, `forge-bench`, `forge-hook` are never run by a subagent; a write to
  `CLAUDE.md`, `.gitignore` or `.claude/**` is denied (plain readers allowed); path arguments are judged by their symlink-resolved
  target; `rm -r` outside `/tmp`, `$TMPDIR` or the scratchpad, any writing `forge-status` subcommand and every
  `irreversible_commands` pattern are denied. The handoff gate's `tree_changed ⊆ files_changed` and the step-done pathspec check
  catch whatever a worker's shell changed inside the tree.

## Class L: which full-suite result counts

Per-unit verifiers run the unit's checks against the unit's committed range. In a shared tree a unit's checks may see sibling units'
work, and a parallel unit's suite run proves nothing about the merged result. **The full-suite result is authoritative only from the
final `forge-verifier fable/medium` spot-check**, which runs after every unit is done (design §3 L path, §4.2).

## Caps that turn into a decision

- Handoff, verdict and plan gates: two blocks for one `agent_id`, then allow — handoff stamped `UNVERIFIED` (no commit), verdict
  rewritten to `UNKNOWN`, plan journaled `PLAN-GATE-BYPASSED` (the import still refuses an invalid plan).
- Stop gate: two consecutive blocks, then allow with a `systemMessage` and the STALE banner at the next start.
- Fence: the third denial of one rule in one turn ends the turn (`continue: false`).
- Escalation: `step-start` refuses a fourth attempt on one step, and the spawn guard a third verifier run on one attempt, without
  `ruling.md` (`step-start` resets `verify_attempts`, so each attempt gets two verifier runs).

## The bypass (operator only, journaled)

A gate is never disabled by a model. The operator, when a gate is wrong and work must continue:

1. `.forge/bin/forge-doctor --disable-gate <name>` — writes `.forge/.runtime/gate-disabled-<name>` and a journal line. `<name>` is
   the hook event whose Forge entry will be changed (`PreToolUse`, `SubagentStop`, `Stop`, `PreCompact`, …) or `all`.
2. Edit `.claude/settings.json` by hand (remove or change that Forge hook entry). The ConfigChange guard lets an exempted event's
   entry change; every other Forge entry is still guarded.
3. Undo: re-run the Forge installer with `--upgrade` (it re-merges every Forge entry; UPGRADING.md in the Forge repo) and delete
   the marker. `.forge/.runtime/` is gitignored, so a
   bypass never travels to another machine.

Record why in `.forge/decisions/NNNN-<slug>.md` when a bypass lasts beyond one session.
