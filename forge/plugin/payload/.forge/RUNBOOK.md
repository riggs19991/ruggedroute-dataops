# RUNBOOK.md — operating and troubleshooting the Forge

For the operator, and for the architect when it is stuck. Every command runs from the repository root as `.forge/bin/<tool>`.
Background: FORGE.md (entrypoint), GATES.md (what is enforced), HOOKS.md (how), ROUTING.md (who does what), SCHEMAS.md (file shapes).
This file is Forge-owned and overwritten on upgrade: keep project-specific operating notes in `.forge/lessons/` (`type: project`)
or `binding.json` → `notes`.

## 1. The daily loop

1. Open Claude Code in the repo. SessionStart injects the STATUS digest, any INTERRUPTED/STALE banner, the newest handoff's
   *Remaining*/*Gotchas*, git state, the lessons index head and the binding digest. If you see no digest, hooks are not running:
   go to §10 first.
2. `/forge-task <one-line title>` — the architect declares the files it will touch, opens the task in one
   `.forge/bin/forge-status open …` call (class T/S/M/W/L/X, risk overlay R) and then works inline (T/S/X), writes the plan
   (small M) or dispatches the planner (large M, W, L).
3. `/forge-next` — executes STATUS `next_action`: dispatch the routed builder, dispatch the verifier, adjudicate a FAIL, or close.
   Background workers report back in a later turn; type `/forge-next` again (or let auto-resume do it) when one finishes.
4. `/forge-close` — the close ritual sized to the class. For risk R you will be shown `git diff --stat` and the plan's *Rollback*
   and asked for the acknowledgement text (`--human-ack "<name> reviewed diff <sha>"`).
5. When the skill prints `FORGE CLEAR POINT — …`, type `/clear`. The next session starts from STATUS and, with
   `binding.auto_resume`, submits "Resume from .forge/STATUS.json …" by itself ([U]: if nothing auto-submits, type `/forge-next`).

Prefix a message with `?` to chat without the Stop gate asking for a STATUS update (no mutation that turn).
Health: `/forge-doctor`. Every ~10 closed tasks: `/forge-gc`.

**Clearing is a policy, not a reflex.** `binding.clear_policy`: `phase` (clear at every CLEAR POINT, the default), `task` (clear between
tasks), `never` (the skill prints `FORGE PHASE CLOSED` instead). Skipping a clear never breaks correctness; the next close row records
`context_carried: true` so `/forge-gc` can show whether it cost anything.

## 2. Driver mode (unattended, one process per phase)

`.forge/bin/forge-run [--max-phases N] [--budget-usd X] [--dry-run]` runs one `claude -p "<resume prompt>"` per phase with
`--model fable --effort <binding.routing.architect_effort> --permission-prompts none --permission-mode acceptEdits
--allowedTools <list built from the binding> --output-format json --max-budget-usd <phase cap> --max-turns <binding.driver.max_turns>`
until the task is done, blocked or awaiting a human, or `--max-phases` (default `binding.driver.max_phases`, 12) is reached. The
clear is the process boundary, so it is guaranteed here. With no task open it prints that and exits 0 without a preflight.

- Preflight: `forge-doctor --quick` (static checks only, no `hooks-alive`), then a passing `forge-doctor --driver` probe for this
  `claude --version` — reused from `.forge/.runtime/driver-probe.json` for 24 h, otherwise run again. The probe is one trivial phase
  that must report an empty `permission_denials` and a Fable model in `modelUsage` (both fields observed, not documented [U]).
- While it runs, `.forge/.runtime/driver` exists: irreversible commands are **denied** (not asked), and a risk-R phase whose brief or
  rollback contains an `irreversible_commands` pattern is refused before it starts (`phase: blocked`, `blocked_on: "human gate: <cmd>"`).
- Every phase writes a `measured` ledger `phase` row from `total_cost_usd` and a line in `.forge/.runtime/phase-costs.jsonl`.
- Hooks are checked **after** each phase: SessionStart must have rewritten `.forge/.runtime/hooks-alive` during it.
- Exit codes: `0` done, idle, or `--max-phases` reached (STATUS names the next action) · `1` a `claude -p` phase produced no JSON
  result · `2` usage (bad flag value) · `3` refused: preflight FAIL, `blocked`, `awaiting_external`, or the R human gate · `4` STATUS
  invalid, or `hooks-alive` was not rewritten by the phase just run (that phase's cost is already spent; run
  `.forge/bin/forge-doctor --probe-hooks`) · `5` livelock (same phase/step/status/attempts three times) · `6` a tool was denied in
  headless mode (ledger `denied_tools` row names it; add the allow rule — §8 — and re-run).
- `--dry-run` runs the static preflight and prints the next phase's command, then exits 0 without spending.

## 3. Blocked tasks

`phase: blocked` with `blocked_on` set means the architect or a gate decided a human must act (a ruling, an irreversible command, a
missing credential). Read `blocked_on` in the digest (`.forge/bin/forge-status get task.blocked_on`), do what it says, then
`.forge/bin/forge-status unblock` and `/forge-next`. To block a task yourself: `.forge/bin/forge-status block --on "<what a human
must do>"` (no task id; it acts on the open task). To park a task deliberately: write `.forge/tasks/<id>/ruling.md` (template
`.forge/templates/ruling.md`) and `/forge-close --partial`; the next queued task becomes `queue[0]` and is never opened automatically.

A **step** in status `blocked` is different: its worker returned `NEEDS_CONTEXT` or `BLOCKED`. Read its `report-NN.md`, then either
`.forge/bin/forge-status step-start <id> <NN> --from failed` (keep the tree; the report's `next_action` is appended to the brief's
*Known failed approaches*) or `--from clean` (restore to base) and dispatch a fresh worker with the missing context in the prompt;
or widen the scope (`scope add <id> <path> --why "…"`, class X, else `--ruling`); or `block --on "…"`.

## 4. Awaiting external verification

A criterion planned as `check: external` (a scheduled workflow, an emulator, a device) or a verifier finding tagged `env-cannot-run`
parks the task in `phase: awaiting_external`. `next_action` names the exact commands, for example:

```bash
gh workflow run quarterly-rec_pois.yml && gh run watch
.forge/bin/forge-status attest T-0012 01 DoD-4 --by <you> --evidence <run url or log path> [--exit 0]
```

Run the check yourself (locally, where the environment exists), attest it, then `/forge-next` re-dispatches the verifier, which grades
the criterion from your attestation record. The Stop gate never blocks while a task waits for you.

## 5. Dead-session recovery

Symptoms: the digest shows an **INTERRUPTED** banner — a step is `running` with `started_by` from another session and no report, or a
spawn was allowed but no worker ever started (`agent_id: null`, no evidence rows).

1. `.forge/bin/forge-status recover <id> <step>` — saves `git diff -- <allowed_paths>` to `.forge/incidents/<ts>-<id>-<step>.patch`
   and copies every new or untracked file it is about to delete to `.forge/incidents/<ts>-<id>-<step>/<path>`, restores the step's
   paths to `.forge/tasks/<id>/.base-<step>`, removes the new files, and sets the step `pending` (its `attempts` are kept). When the
   tree is already at base it saves and removes nothing. Add `--force` when the interrupted step was started by this same session.
2. Dispatch the worker `next_action` names (`/forge-next` does it): the spawn guard runs `step-start` for the pending step.
   Running `.forge/bin/forge-status step-start <id> <step> --from clean` yourself first is also accepted after a `recover`
   (a no-op restore when nothing changed since); the guard then accepts the pre-started retry. Mention the incident patch in the
   prompt if it is worth a look.
   If the Agent call itself failed (the step is `running` with `agent_id: null` and no evidence), a second dispatch is refused for
   10 minutes while `.forge/.runtime/dispatched-<id>-<step>` exists; `recover <id> <step>` (`--force` when this session started
   the step) sets it `pending` again, and a pending step is dispatchable at once.
3. `StopFailure` writes `.forge/incidents/<ts>-stopfailure.json` and `SessionEnd` writes `.forge/.runtime/last-session.json`: read them
   to see what the dead session was doing.

Committed steps are never lost: a worker's step is committed by the handoff gate before STATUS records it.

## 6. Stale STATUS

- **"STATUS not updated this turn; marked stale"** — the Stop gate blocked twice (its soft cap) and let the turn end; the next start
  shows a STALE banner. Run the `forge-status` subcommand the block reason named (for example `step-report <id> <NN> --report …`, `step-verdict`,
  `evidence <id> --claim … --from-check …`, `scope add <id> <path> --why "…"`), then end a turn normally; the marker clears when a turn ends with STATUS in sync.
- **"STATUS.json was edited by hand"** — never edit it; if you did so deliberately, `.forge/bin/forge-status validate --restamp`
  (journaled). `.forge/bin/forge-status validate` exits 4 and prints the failing assertion when the file is invalid; restore it from
  git (`git show HEAD:.forge/STATUS.json`) rather than repairing it by hand.
- **`context_state: stale`** after a close is expected: it means "clear before the next phase". `UserPromptSubmit` reminds you once
  per prompt; `/clear` resets it (with or without an open task), as does `.forge/bin/forge-status fresh`.

## 7. Model and effort

- `--no-model` and `--effort` persist in `.forge/install-manifest.json` (`options`), so a later install or `--upgrade` keeps them
  without flags; `--with-model` undoes a saved `--no-model`.
- The installer writes `model: "fable"` (skip with `--no-model`) and `effortLevel` from `binding.routing.architect_effort` (default
  `medium`) into `.claude/settings.json`; `forge-run` passes the same effort. Workers' models and efforts come from their frontmatter and
  the per-dispatch parameters the spawn guard checks.
- **`/effort medium` for X.** Class X is coded by the architect. `/forge-investigate` runs at `effort: medium` by itself; if you work an X
  task without the skill and the session runs at `low`, type `/effort medium` first. The bookkeeping skills (`/forge-next`,
  `/forge-close`, `/forge-doctor`, `/forge-gc`) deliberately run at `low`.
- `subagentPromptCacheTtl: "1h"` and `experimental.cacheTtl: 1h` on workers keep the prompt cache alive across `forge-check` runs longer
  than five minutes.

## 8. Trust and permission prompts

- Plain project files (`.claude/agents`, `.claude/skills`, `.claude/rules`, project `settings.json` hooks) load even before the workspace
  trust dialog is accepted; hooks fire regardless.
- Project `permissions.allow` rules apply **only after trust**. In an untrusted session (a fresh cloud container) every
  `.forge/bin/...` call and every verify command asks once per call. Accept the trust dialog to stop that; `/forge-doctor` reports the
  trust state as WARN.
- The installer adds `Bash(.forge/bin/*)`, one rule per Forge tool, and one `Bash(<prefix> *)` rule per `binding.verify[].cmd`,
  `bootstrap` and `smoke` (derived from your binding; the shipped fragment carries no project-specific command rule). A new verify command needs its allow rule: re-run the installer, or add it to `.claude/settings.json` by hand.
- `permissions.ask` covers `git push *`, `gh pr merge *`, `gh workflow run *`, `wrangler *`, `npx wrangler *`;
  `permissions.deny` covers `.env` reads, force pushes, `Agent(general-purpose)` and model edits to `.claude/settings*.json`.

## 9. The Stop cap

Claude Code ends a turn anyway after 8 consecutive Stop-hook blocks without a tool call (the counter resets on any tool call).
The Forge never gets there: its Stop gate allows after **2** consecutive blocks with a `systemMessage` and the STALE marker (§6).
`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` is documented only as *raising* the platform cap, so the Forge does not set it and raising it changes
nothing for the Forge's own soft cap. The Stop hook has no `onFailure: block`: if the dispatcher crashes, the turn ends with
"Forge Stop gate crashed: run /forge-doctor".

## 10. Debugging hooks

- `.forge/bin/forge-doctor --probe-hooks` — one `claude -p` turn; passes when `.forge/.runtime/hooks-alive` was rewritten.
- `claude --debug` (or `/debug` in a session) shows hook logs: which hooks loaded, their stdin, stdout and exit. `/hooks` lists the
  loaded hook configuration.
- Replay one event by hand: HOOKS.md §One test line per event.
- The hook journal: `.forge/tasks/<id>/journal.md` (or `.forge/.runtime/journal.log` with no task open) records dispatches, denials,
  gate blocks with reasons, stop blocks and config-change blocks.
- Hooks do not run under `claude --bare`, `--safe-mode`, or with `disableAllHooks: true`; the Forge is then unenforced and
  `forge-run` refuses to continue (exit 4).

## 11. Upgrade

Upgrades come from the Forge source repository (its `docs/UPGRADING.md` has the full contract):

```bash
bash <forge checkout>/install.sh --target . --upgrade [--dry-run]
```

It applies migrations, overwrites Forge-owned files (a file you changed locally is backed up to
`.forge/incidents/upgrade-<ts>/` first and named in a warning — compare with `.forge/install-manifest.json`), re-merges settings
(only hook entries whose command starts with `"$CLAUDE_PROJECT_DIR"/.forge/bin/` are replaced; a local scalar such as `model` or
`effortLevel` that differs from the fragment is kept and printed as `settings: <key> local=… -> fragment=…`, and only
`--force-settings` applies the fragment's value — `--force` covers Forge-owned files only), rewrites `.forge/VERSION` and the manifest, and runs the doctor. Project-owned files (`binding.json`, `STATUS.json`,
ledger, history, tasks, lessons, decisions, CHANGELOG) are touched only by a migration on a schema MAJOR. Nothing auto-updates:
`/forge-doctor` warns when `.forge/VERSION` lags `binding.forge_pin`. Commit the result as one commit.

## 12. Troubleshooting (keyed by `/forge-doctor` line names)

`/forge-doctor` prints `OK|WARN|FAIL <name>: <detail>` and a closing count line. The static set runs every time (`--quick`, used by
`forge-run`, runs only `forge-root`, `python`, `binding`, `binding-todo`, `status`, `settings-hooks`, `settings`, `bin`,
`gitignore`); probe lines appear only when their flag is passed. Fixes by name:

| Name | Meaning | Fix |
|---|---|---|
| `forge-root` | FAIL: `$FORGE_ROOT` is exported and names a different repository than this checkout (a stale export from another session) | `unset FORGE_ROOT`, remove any `export FORGE_ROOT=` line from `$CLAUDE_ENV_FILE` or your shell profile, and start a new session |
| `python` | `python3` older than 3.9 | Install Python ≥ 3.9 (macOS: the Xcode command-line tools ship it); every Forge script needs it |
| `claude-cli` | `claude` older than 2.1.295 (FAIL), or absent / version unreadable (WARN) | Update Claude Code (`claude update`); older versions ignore `onFailure`, so gates fail open |
| `trust` | the workspace trust dialog has not been accepted, or `~/.claude.json` is unreadable (WARN) | Accept it once in an interactive session; until then allow rules do not apply and each script call asks (§8) |
| `version` | `.forge/VERSION` missing (FAIL), or it differs from the Forge source tree or `binding.forge_pin` (WARN) | Upgrade (§11) or update `forge_pin` deliberately |
| `manifest` | a Forge-owned file is missing or differs from `install-manifest.json` (WARN per file), or the manifest is missing | Someone edited a Forge-owned file; restore it with `--upgrade`, or upstream the change to the Forge repo |
| `binding` | `binding.json` missing/invalid, a required key missing, a bad enum or `verify[]` entry, a malformed `agent_paths`, empty `verify` for a known stack (FAIL); empty `protected_paths` or `mechanic_denied_paths`, or `agent_paths` reaching `.forge/`, `.claude/` or the whole tree (WARN) | Edit `binding.json` by hand (it is policy-locked against model edits); SCHEMAS.md §binding |
| `binding-todo` | a `verify[]` entry carries a `todo` note (WARN) | Replace it with a real command, then re-run the installer so its allow rule is added |
| `status` | `STATUS.json` fails validation (or `forgelib.status` cannot be imported) | `.forge/bin/forge-status validate` names the assertion; restore from git (§6) |
| `settings-hooks` | a Forge hook entry is missing from `.claude/settings.json`, its command or `onFailure` differs from `settings.forge.json`, or an `onFailure` sits on an event that must fail open; WARN when disabled with `--disable-gate` | Re-run the installer with `--upgrade`; if you removed an entry on purpose, see GATES.md §The bypass |
| `settings` | `settings.forge.json` or `settings.json` missing/invalid, or no `Bash(.forge/bin/*)` allow rule (FAIL); `model` not fable, `effortLevel` unset, `subagentPromptCacheTtl` not `1h`, or binding command allow rules missing (WARN) | Re-run the installer (`--upgrade`); add a missing rule by hand if you prefer (§8) |
| `bin` | `.forge/bin` missing, or a script in it is not executable | `chmod +x .forge/bin/*` — run it yourself: the main-session fence refuses chmod outside a task, so `/forge-doctor` only prints it |
| `gitignore` | `.gitignore` lacks `.forge/.runtime/` or `.forge/incidents/` (WARN) | Add both lines (safe; the doctor skill may do it) |
| `duplicate-agents` | `forge-*` agents also exist at user level, or a `forge` plugin is installed (WARN) | Remove the duplicates, or rely on the plugin's self-silencing; `/doctor` shows what the session loaded |
| `hooks-alive` | no SessionStart has been recorded here yet (WARN); OK shows the age of the last one | Start a session in this repo, or run `--probe-hooks` |
| `markers` | a `dirty-main`/`dirty-worker` marker exists with no open task or in a terminal phase, or a `dispatched-*` marker is older than 10 minutes (WARN) | Remove the named file(s) under `.forge/.runtime/` by hand in a shell outside a Forge worker, then start a new session; they only wedge the Stop/PreCompact gates. |
| `digest` | the STATUS digest exceeds 3,000 chars (FAIL; WARN above 2,500), or cannot be computed | Close or park the task; `/forge-gc` archives old tasks |
| `pointers` | a path or `/forge-*` skill named in FORGE.md does not exist (FAIL); FORGE.md over 120 lines or its bootstrap order changed (WARN) | Upgrade (Forge-owned files missing) or restore the file from git |
| `probe-hooks` (`--probe-hooks`) | `hooks-alive` was not rewritten in a real `claude -p` turn (FAIL); `plugin_errors` reported (WARN) | Check `claude --debug`; causes: `--bare`, `--safe-mode`, `disableAllHooks`, non-executable scripts, `python3` missing, a settings merge that dropped entries, the plugin form without trust |
| `driver` (`--driver`) | a trivial headless phase produced no JSON, had permission denials, or ran on a non-Fable model | Add the denied tool's allow rule; check `model` in settings and that `--model fable` is accepted |
| `probe-clear` (`--probe-clear`) | whether `initialUserMessage` auto-submits after `/clear` [U] (WARN when not observed) | Informational; when it does not, type `/forge-next` after each clear |
| `worktree` (`--worktree`) | a worktree-isolated probe did not see the current HEAD, was not isolated, or did not resolve the main checkout | Keep `git.worktree_isolation: false` (L units then run one after another; `isolation: worktree` spawns are refused) |
| `probe-maxturns` (`--probe-maxturns`) | whether SubagentStop fires on a `maxTurns` partial return [U] (WARN when not observed) | Informational; the handoff gate's two-block cap gives the same degraded path either way |
| `probe-coldstart` (`--probe-coldstart`) | a fresh Haiku session could not state `next_action` from FORGE.md with hooks disabled (WARN) | Fix FORGE.md pointers (upgrade) or STATUS `next_action` |
| `probes` / `probe` | probe flags ignored because of `--no-probes` (WARN); a probe could not start, e.g. `claude` not on PATH (FAIL) | Run the probe from a shell without `--no-probes`; install or expose the `claude` CLI |

When a gate refuses something it should allow, do not edit the gate: record the case in `.forge/lessons/`, and if work must continue,
use the journaled operator bypass in GATES.md.
