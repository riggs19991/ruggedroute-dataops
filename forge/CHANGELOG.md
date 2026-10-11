# Changelog

All notable changes to the Forge. Versioning is semantic (docs/UPGRADING.md): MAJOR = a STATUS, handoff, brief or binding schema
change; MINOR = an additive agent, skill, hook or rule; PATCH = prompt or documentation text. Agent and skill names are permanent.

## 1.0.0 — 2026-10-11

First release, built from design v2 (`docs/design/design-v2.md`).

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
