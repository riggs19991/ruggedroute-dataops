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
| 0 | Plan gate | Plan exists with the mandatory headings for its class (M: 4; W/L: 12; S/X inline: 2), parseable plan-meta, ≥1 `DoD-`, one valid brief per step, `max_tool_calls` per step, rollback command for R, baseline recorded; routing obeys ROUTING.md rules; M and W have one step; risk re-matched on every brief's paths; `red_ok_until` points forward | `SubagentStop` (`^(forge:)?forge-planner$`) + `forge-status plan` (+ `.forge/bin/forge-gate --plan` for the architect's own plans) | [G] |
| 1 | Plan-first / scope fence (main session) | No source `Edit\|Write\|NotebookEdit` without an open task; never for M/W/L; not before `plan.md` for S/X; not outside the declared `scope` for T/S/X; the Bash mutation heuristic under the same conditions; three same-rule denials in a turn → `continue: false` | `PreToolUse` | [G] tool edits; [G at close] shell writes (gate 8 backstop) |
| 2 | Scope fence (workers) | Edits only inside the brief's `allowed_paths`; existing tests only with `may_edit_tests`; protected / risk / mechanic-denied paths by tier; `.forge/**` never; the worker must be bound to a running, unbound brief of its own role | `PreToolUse` inside subagents (`agent_id`/`agent_type`) | [G] |
| 2b | Tool budget | Bash/Edit/Write denied once this agent's `bash\|edit` evidence rows reach `brief.max_tool_calls` ("write your HANDOFF with status BLOCKED") | `PreToolUse` | [G] |
| 2c | Read-only roles | `forge-scout`, `forge-verifier`, `forge-planner`: Bash allow-list (git read commands, `rg`, `grep`, `find`, `ls`, `cat`, `head`, `tail`, `wc`, `jq`, `pytest`, `python3 -m pytest\|unittest`, `.forge/bin/forge-check`, `.forge/bin/forge-gate`, `.forge/bin/forge-status get`, `binding.verify[].cmd` prefixes, `cd <dir> && <allowed>`); interpreter `-c`/`-e`, heredocs and redirects never; Edit/Write denied except the verifier's own memory directory (and the planner's `.forge/tasks/<id>/`) | `PreToolUse` (`Bash`, `Edit\|Write`) | [G] |
| 3 | Mechanical checks, exact exit codes | `forge-check` runs `binding.verify[]` (filtered by `when`; missing `exists` → `skipped`) ∪ brief `checks[]`, prints one `FORGE_CHECK name=… exit=…` line per command, writes the `checks/` record, runs the test ratchet against `plan-meta.test_baseline` | `.forge/bin/forge-check` | [G] |
| 4 | Evidence capture | Every Bash/Edit/Write tool event with `agent_id`, `kind`, success and failure, appended to `evidence.jsonl` | `PostToolUse` + `PostToolUseFailure` | [G] (Bash exit code inside `tool_response` is best-effort [U]; exact codes come from gate 3) |
| 5 | Handoff gate | Mandatory headings + JSON; `files_changed ⊆ allowed_paths`; this agent's source edits and the unit's tree changes ⊆ `files_changed`; checks run after the last source edit at exit 0; red-then-green for `tdd`; two-block cap → `UNVERIFIED`; commits and records on allow | `SubagentStop` (builders, mechanic), `onFailure: block` | [G] |
| 6 | Fresh-context verifier | Brief + DoD + committed range + report; re-runs `forge-check`; grades each `DoD-` id; scope check; ratchet; flags only gaps that affect correctness or the stated requirements; `env-cannot-run` tag | agent body + verdict gate | [G] shape, [I] judgment |
| 7 | Verdict gate | Every DoD id graded once with cmd + numeric exit; PASS only when everything passes; every cited cmd has a check record by this verifier (external criteria: a human attest record, else UNKNOWN); tags from the fixed list; runs `step-verdict` on allow | `SubagentStop` (`^(forge:)?forge-verifier$`), `onFailure: block` | [G] |
| 8 | Transition guard + scope backstop | `step-done` without PASS impossible; the step commit must descend from `.base-NN` and touch only `allowed_paths ∪ .forge/tasks/<id>/**`; `plan` with illegal routing impossible; `close` with a non-done step, an out-of-scope tree or out-of-scope commits impossible without `--accept-out-of-scope` + ruling | `.forge/bin/forge-status` | [G] |
| 9 | Spawn routing guard | `forge-*` spawns must match a pending step (or a pre-started retry) by agent/model/effort, alias-normalized; verifier only on a `reported` step with `verify_attempts < 2`; planner only in `phase: plan`; runs `step-start` / `step-verifying` on allow; `general-purpose` denied in settings; built-in spawns journaled as `builtin` | `PreToolUse` (`Agent`) + `permissions.deny` | [G] |
| 10 | Risk / human gate | `irreversible_commands` → `ask` for the main session in interactive mode; `deny` for subagents always and for the main session in driver mode (`forge-run` refuses the phase: `blocked`, `blocked_on: "human gate: <cmd>"`); `close --human-ack` for R | `PreToolUse` (`Bash`) + settings `ask` + `forge-run` + `forge-status` | [G interactive / blocked in driver] |
| 11 | Stop gate | STATUS reflects every mutation (`dirty-main`, `dirty-worker`, hand-edit sha); `?` chat-turn exemption; `stop_hook_active` honoured; 2-block soft cap then `stale-status`; fails open on crash | `Stop` | [G/cap] |
| 12 | Claims audit | `forge-status evidence` accepts only claims that point at a `checks/` record; `close` refuses a handoff whose *Done, with evidence* bullets lack a command, and a T `--one-line` without a passing check record | `.forge/bin/forge-status` | [G] |
| 13 | External verification path | `check: external` criteria pass only on a human `attest` record; `phase: awaiting_external` holds the task with the exact commands to run | `forge-status attest` + verdict gate | [G] |
| 14 | Policy-file lock | Model edits (main session and every subagent) to Forge-owned files (`install-manifest.json` list: scripts, schemas, templates, the `.forge/*.md` docs), `.claude/settings*.json`, `.forge/binding.json`, `.forge/STATUS.json`, `.forge/ledger.jsonl`, `.forge/history.jsonl` are denied; `ConfigChange` blocks a settings reload that drops or alters a Forge hook entry | `PreToolUse` + `ConfigChange` + settings `deny` | [G] (whether a ConfigChange block prevents the reload is [U]; `/forge-doctor` diffs settings either way) |
| 15 | System self-check | `/forge-doctor`: hooks alive, `python3` ≥ 3.9, `claude` ≥ 2.1.295, trust state, binding valid, STATUS valid, settings diff against `settings.forge.json`, executables, `.gitignore`, duplicate agents on the filesystem, FORGE.md pointer check; optional probes (`--probe-hooks`, `--driver`, `--probe-clear`, `--worktree`, `--probe-maxturns`, `--probe-coldstart`) | `.forge/bin/forge-doctor` | [G] |

Not used as gates, on purpose: `TaskCompleted`/`TeammateIdle` (teams are experimental and interactive-only), `/goal`, transcript
grepping (undocumented), `context: fork` skills (their `agent_type` is undocumented), saved workflows.

## The Bash guards are heuristics, backed by deterministic checks

- **Main session (gate 1):** `looks_mutating(cmd)` flags `sed -i`, `tee`, `rm`, `mv`, `cp`, `chmod`, `chown`, `truncate`,
  `git checkout|reset|clean|stash|rebase|merge|apply|cherry-pick|revert`, `python3 -c`, `node -e`, `perl -e`, output redirects
  and heredocs, unless every `&&`/`;`/`|` segment is `.forge/bin/*`, a read/commit git command, or a `binding.verify[]` /
  `bootstrap` / `smoke` prefix. A determined shell write can slip past a regex. The backstop is deterministic: `forge-status close`
  and `step-done` compare `git status --porcelain ∪ git diff --name-only <base>..HEAD` with the declared scope and refuse anything
  outside it (gate 8). So: **[G] for tool edits, [G at close] for shell writes.**
- **Read-only roles (gate 2c):** an **allow-list**, not a deny-list: a command is refused unless every segment matches it, and any
  redirect, heredoc, `tee`, `sed -i`, `perl`, `python3 -c` or `node -e` anywhere refuses it. Labelled [G] as an allow-list; it can be
  too strict (a legitimate read command missing from the list is refused), never too loose by construction.
- **Workers (gate 2):** `git push`, `git reset --hard`, `git clean`, `git checkout -- .`, `rm -rf` outside `/tmp`/scratchpad and every
  `irreversible_commands` pattern are denied by pattern; the handoff gate's `tree_changed ⊆ files_changed` and the step-done pathspec
  check catch whatever a worker's shell changed inside the tree.

## Class L: which full-suite result counts

Per-unit verifiers run the unit's checks against the unit's committed range. In a shared tree a unit's checks may see sibling units'
work, and a parallel unit's suite run proves nothing about the merged result. **The full-suite result is authoritative only from the
final `forge-verifier fable/medium` spot-check**, which runs after every unit is done (design §3 L path, §4.2).

## Caps that turn into a decision

- Handoff, verdict and plan gates: two blocks for one `agent_id`, then allow — handoff stamped `UNVERIFIED` (no commit), verdict
  rewritten to `UNKNOWN`, plan journaled `PLAN-GATE-BYPASSED` (the import still refuses an invalid plan).
- Stop gate: two consecutive blocks, then allow with a `systemMessage` and the STALE banner at the next start.
- Fence: the third denial of one rule in one turn ends the turn (`continue: false`).
- Escalation: `step-start` refuses a fourth attempt and the spawn guard a third verifier run on one step without `ruling.md`.

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
