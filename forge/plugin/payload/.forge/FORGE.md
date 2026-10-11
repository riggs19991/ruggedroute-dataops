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
