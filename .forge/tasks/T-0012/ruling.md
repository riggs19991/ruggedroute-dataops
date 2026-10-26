# Ruling: T-0012 closes --partial on a Forge state-machine gap, not on the work

The work is COMPLETE and VERIFIED: builder DONE handoff (gate-validated,
drafts/builder-handoff-01b.md, checks/01-1792969801-forge-builder.json pass=5), architect
re-checks (checks/01-1792972533), verifier verdict PASS with 55 refutation probes
(verdict-01.json, draft gate-validated), DoD-4 human attestation
(checks/01-1792977179-human.json; runs 40243912707 + 40246926809). Three commits pushed:
b1436fc, 3832d02, 45783cf.

Step 01 cannot transition to done: in operator mode (hooks dormant) the handoff gate's
auto-commit never runs, so step.commit is null; step-report refuses amendments at status
`verifying`, and `_step_done` hard-requires the commit. This is the state-machine twin of the
attest-inline-step gap (lessons/attest-inline-step-gap.md). Per RUNBOOK §gates ("when a gate
refuses something it should allow... record the case in lessons, and if work must continue,
use the journaled operator bypass"), the operator decision — under the founder's standing
delegation (CLAUDE.md: solo non-technical founder, decisions delegated) — is:

1. Park T-0012 with this ruling; the handoff, verdict and attestation FILES are the durable
   record of a fully-shipped task.
2. Proceed with the sanctioned DoD-4 follow-through (full publish dispatch) — the shipped
   code is on origin/main and triple-verified.
3. Queue the upstream Forge fix (step-report amend path for a verifying step with a null
   commit) as the next task; lesson filed at lessons/step-commit-operator-gap.md.

— riggs/operator-session, 2026-10-26
