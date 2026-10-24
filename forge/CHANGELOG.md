# Changelog

All notable changes to the Forge. Versioning is semantic (docs/UPGRADING.md): MAJOR = a STATUS, handoff, brief or binding schema
change; MINOR = an additive agent, skill, hook or rule; PATCH = prompt or documentation text. Agent and skill names are permanent.

## 1.0.1 — 2026-10-19

Project-agent and Windows release. No `schema_version` change: the new binding key is optional with a default, so
1.0.0 bindings keep working, and migration `0001` adds it on upgrade.

- `binding.agent_paths` (project-owned, default `[]`): repo-relative globs a **project agent** — any subagent whose
  `agent_type` is not a `forge-*` role, such as RuggedRoute's read-only QA tester — may write in any task state, no task
  open included. `PreToolUse` Edit/Write allows a matching path; the Bash fence allows a write-shaped command whose
  every target (redirects, the operands of `rm|rmdir|mv|cp|mkdir|touch|tee|chmod|chown|truncate|sed -i`, `cd` tracked,
  heredoc bodies ignored) lies under the globs. The policy lock, `protected_paths` and the outside-repository check still
  deny; `irreversible_commands` are denied for such agents (the main session still asks); git, `ln`, `patch`, `dd`,
  `rsync` and an interpreter fed a heredoc or inline code fall back to the plain fence, which now names the globs.
  Forge roles and the main session are unchanged. `forge-status close` never counts files under `agent_paths` as out
  of scope. `/forge-doctor` FAILs a malformed key and WARNs when it reaches `.forge/`, `.claude/` or the whole tree.
  Documented in HOOKS.md (Roles, Edit and Bash rows), GATES.md (gate 2d), SCHEMAS.md, MODULE-API.md and the README;
  the template binding carries `"agent_paths": []`; worked bindings updated (RuggedRoute: `qa/reports/**`,
  `qa/scripts/**`, `qa/.auth/**`).
- Migration `0001-binding-agent-paths.py`: `install.sh --upgrade` inserts `"agent_paths": []` right after
  `mechanic_denied_paths` in an existing `.forge/binding.json` when absent, keeping every other byte; idempotent.
- Windows: `forgelib.common.run()` spawns `_bash()` — `$FORGE_BASH`, then `C:/Program Files/Git/bin/bash.exe`, then
  `C:/Program Files/Git/usr/bin/bash.exe`, else `bash` — so checks no longer hit the WSL stub (RuggedRoute ADR 0002
  upstreamed; the upgrade overwrites that local patch, which is no longer needed). `installer.py` runs `forge-doctor`
  through its own interpreter instead of the `#!` line.
- Tests: `forge/tests/run_linux.sh` runs the suite (or any command) against the checkout inside a `python:3.12`
  container, for Windows checkouts that cannot exec the shebang scripts; new tests cover the fences, `_bash()`, the
  migration, the close backstop and the doctor check.

## 1.0.0 — 2026-10-11

First release, built from design v2 (`docs/design/design-v2.md`). Released 2026-10-11: merged to `main` and tagged `v1.0.0`;
installed into ruggedroute-dataops (this repo), RuggedRoute (branch `forge/install`) and plot-device (branch `forge/install`).

- Plain-project-layout payload: 8 agents (`forge-scout`, `forge-planner`, `forge-builder`, `forge-builder-wide`, `forge-builder-s`,
  `forge-mechanic`, `forge-verifier`, `forge-librarian`), 6 skills (`/forge-task`, `/forge-next`, `/forge-close`, `/forge-doctor`,
  `/forge-gc`, internal `forge-investigate`), 4 path-scoped stack rules, and a settings fragment with twelve hook registrations.
- Scripts in Python 3.9+ standard library (ADR 0002): `forge-hook` (one dispatcher for every hook event), `forge-status` (the only
  writer of STATUS.json; the task state machine), `forge-check` (exact exit codes, test ratchet), `forge-gate` (plan / handoff / verdict
  validators), `forge-run` (driver mode), `forge-doctor` (self-check and probes), `forge-bench` (optional cost measurement).
- Task classes T/S/M/W/L/X with the risk overlay R; routing matrix as data in `.forge/schemas/routing.json`.
- Gates: plan gate, main-session and worker scope fences, tool budgets, read-only role allow-lists, handoff gate (checks after the last
  source edit, red-then-green), verdict gate, spawn routing guard, Stop gate with a 2-block soft cap, policy-file lock, external
  (human-attested) verification path.
- Schemas: STATUS v2, binding v2, `forge/plan/2`, `forge/brief/2`, `forge/handoff/2`, `forge/verdict/2`, `forge/ledger/2`.
- Documentation: FORGE.md entrypoint, RUNBOOK, ROUTING, HOOKS, SCHEMAS, GATES, ROLE-architect; ARCHITECTURE, UPGRADING,
  DESIGN-RATIONALE; ADRs 0001-0002; worked bindings for ruggedroute-dataops, ruggedroute-android and millwright-kb; an eval task set.
- Pre-release hardening from a 64-finding adversarial review (behaviour as shipped):
  - Fences judge the symlink-resolved path and deny anything outside the repository; `FORGE_ROOT` is no longer exported, and a stale
    one naming another repository is ignored (WARN) and reported by `/forge-doctor` (`forge-root`). The `--plugin` hook form is a
    no-op in repositories without a Forge install.
  - Read-only roles: the Bash allow-list also denies command/process substitution, `${`, `find -exec|-delete|-fprint*`, `--output`,
    `sort -o`, `xargs`, `eval`; segments split on newlines and `&` outside quotes. Workers: git by allow-listed subcommand, no `ln`,
    no `.forge/` access from the shell beyond `forge-check`, `forge-gate`, `forge-status get` and reading the brief; the tool-budget
    counter is hook-owned.
  - Pre-validation drafts have one sanctioned place, `.forge/tasks/<id>/drafts/<agent_id>-*.md` (never committed); the verifier
    agent gains `Write` for it.
  - Inline S/X verdicts are recorded as `task.inline_verdict` (`step-verdict <id> main`); `close` requires a PASS for X, and for S
    when tests changed.
  - `step-start` resets `verify_attempts` (two verifier runs per attempt), accepts `blocked` steps (NEEDS_CONTEXT/BLOCKED reports)
    with `--from failed|clean`, accepts `--from clean` after `recover`, and is refused in phase `intake`; `recover` copies untracked
    files to `.forge/incidents/` before removing them.
  - `forge-status plan` records `test_baseline` at import when the template value is left; `open --files` refuses missing paths;
    `new` is an alias of `open`; queued tasks may carry no id (stack discovery) and ids never collide with queued ones.
  - `forge-check <id> <step>` also runs the step's DoD check commands; the tdd rule accepts an earlier red record by any agent.
  - Brief template: `may_edit_tests` defaults to `true` (with a comment on when to set it false) and `expected_fail_first` must be a
    subset of `checks`. Routing: class L `mode` is `single` with `sequential_units: true`.
  - Installer: `--force` covers Forge-owned files only; settings scalars change only with `--force-settings`; the settings fragment
    no longer pre-approves project-specific commands.
  - Docs: RUNBOOK troubleshooting keyed by the doctor's real line names; driver exit codes and argv as implemented; `scope add`
    takes the task id; dead-session recovery is `recover`, then dispatch.
