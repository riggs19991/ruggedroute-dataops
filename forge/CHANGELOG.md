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
