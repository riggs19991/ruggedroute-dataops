# attest cannot address the implicit `main` step of an inline task

`forge-status attest <task> main <DoD-n>` refuses with "has no step main" on inline (steps: [])
plans, while `step-verdict <task> main` and the verdict gate both special-case `main` for inline
tasks. External DoD criteria on class X/S inline tasks therefore cannot be attested through the
CLI; the workaround is writing the identical human check record to
`.forge/tasks/<id>/checks/main-<ts>-human.json` (schema: ts, agent_id/source "human", by,
criterion, evidence, exit, task, step, session_id) — the gate reads the file, not STATUS.
Seen on T-0010 (2026-10-25, forge 1.0.1). Upstream candidate: `_step()` should synthesize the
inline `main` step the way the verdict path does.
