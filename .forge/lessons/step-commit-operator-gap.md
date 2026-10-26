# Operator-mode M/W steps deadlock at `verifying` with a null commit

The handoff gate's hook auto-commits a DONE worker step and records step.commit; with hooks
dormant (operator session), the architect commits by hand, step.commit stays null, and the
state machine wedges: step-report refuses status `verifying`, step-verdict's _step_done
refuses a null commit, recover refuses non-running, step-start refuses verifying. Seen on
T-0012/01 (2026-10-26). Workaround: ruling.md + close --partial with the verdict/attest files
as the durable record. Upstream fix: let step-report amend ONLY step.commit on a `verifying`
step whose commit is null (no state reset); forge/payload forgelib/status.py step_report.
