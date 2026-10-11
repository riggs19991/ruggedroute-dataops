# 1. Adopt the Forge

Date: 2026-10-11

## Status

Accepted

## Context

Work in this repository is done with Claude Code sessions whose context is lost between sessions. We want every
non-trivial change to start from a written plan, to be routed to a model and effort that fit its size and risk, to be
verified by a fresh context against stated criteria, and to leave a status file that the next session can resume from.

## Decision

Install the Forge v1.0.0 in plain project layout (`.forge/`, `.claude/agents/forge-*`, `.claude/skills/forge-*`,
hooks in `.claude/settings.json`). `.forge/STATUS.json` is the single source of truth and is written only by
`.forge/bin/forge-status`. The installer detected the stack as `python` and seeded `.forge/binding.json`, which is
project-owned and reviewed by hand.

## Consequences

Hooks refuse source edits without an open task, workers without evidence-backed handoffs, and turns that end without
recording state. Forge-owned files are replaced on upgrade; project-owned files (binding, STATUS, ledger, lessons,
decisions) are never overwritten. Costs are recorded in `.forge/ledger.jsonl` as measured only in driver/bench mode.
