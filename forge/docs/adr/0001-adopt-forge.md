# 1. Adopt the Forge as the engineering workflow

Date: 2026-10-11

## Status
Accepted

## Context
Work across ruggedroute-dataops, the RuggedRoute Android app and Millwright KB is done with Claude Code sessions that lose state
between sessions, re-derive context at full price, mix planning with implementation in one growing context, and report progress
without evidence. The owner asked for an ecosystem of rules and processes: plan-first work, explicit handoffs, a status file that is
the single source of truth, automatic context clearing after the status is written, routing by importance and model capability to
save usage (Fable for the hardest work, Opus for easier work, Sonnet and Haiku where they fit), verification gates, portability across
projects with a thin per-project binding, self-documentation and versioning (`docs/design/requirements.md`).

Claude Code 2.1.296 offers the primitives to enforce most of this mechanically: project hooks that load even in untrusted sessions,
`SubagentStop`/`Stop` blocking, `SessionStart` injection, fresh-context subagents, and headless `claude -p` for process-level clearing.
It cannot trigger `/clear` from a hook.

## Decision
Adopt the Forge (design v2, `docs/design/design-v2.md`) as the workflow for every repository that installs it: a Fable architect in
the main session, eight `forge-*` worker agents dispatched with the `Agent` tool, six skills for the rituals, twelve hook
registrations backed by one dispatcher, and `.forge/` as the durable, committed state. Ship it as plain project files copied by an
installer, with a user-level plugin wrapper as a secondary form. Label every rule by how it is enforced ([G], [G/cap], [G at close],
[I], [U]) and measure cost rather than assume it.

## Consequences
- Every change goes through `/forge-task` → `/forge-next` → `/forge-close`; trivial changes pay two script calls, small ones a short
  handoff, larger ones a plan, a builder and a verifier.
- STATUS.json, binding.json, scripts, schemas and settings can no longer be edited by a model; operators edit the binding by hand and
  upgrade the Forge through its installer.
- The interactive `/clear` remains an instructed step; driver mode (`forge-run`) gives guaranteed clearing at the cost of one process
  per phase.
- Per-task cost is higher than a solo session for T/S/X/R work and roughly at parity for M/W/L in the planning model; the ledger, not
  this ADR, decides whether routing defaults change.
- Each consumer repo receives its own `.forge/decisions/0001-adopt-forge.md` from the installer.
