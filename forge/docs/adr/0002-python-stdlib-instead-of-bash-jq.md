# 2. Implement the Forge scripts in Python 3 standard library instead of bash 3.2 + jq

Date: 2026-10-11

## Status
Accepted. Supersedes the implementation-language clause of design v2 §13.3.

## Context
Design v2 mandated bash at the 3.2 syntax level (macOS `/bin/bash`) with `jq` 1.6+ for every hook and CLI script, and no Python,
Node or YAML parser. The scripts that design describes are substantial: a state machine of about 25 subcommands (`forge-status`) with
preconditions, routing rules and atomic writes; three validators (plan, handoff, verdict) shared by hooks and a CLI; a hook
dispatcher covering every event; glob matching with `**` semantics; ISO/epoch time arithmetic; a check runner with a test ratchet.

Facts about the target machines:
- `python3` is present in every Claude Code cloud container.
- On macOS, `python3` ships with the Xcode command-line developer tools, which `git` itself requires, so any Mac that can run the
  Forge's git operations already has it.
- `jq` is **not** preinstalled on macOS; the design's installer had to refuse without it and print install remedies.
- bash 3.2 lacks associative arrays, `mapfile` and case conversion, which pushes logic into long jq programs that are hard to test.

## Decision
Write every Forge script in Python 3.9+ using only the standard library. Scripts in `.forge/bin/` are executable files with
`#!/usr/bin/env python3`; shared code lives in `.forge/bin/forgelib/` (`common`, `status`, `gates`, `checks`, `hooks`) behind the
contract in `docs/MODULE-API.md`. Data formats, file layout, exit codes, hook registrations and every behaviour of design v2 are
unchanged; only the implementation language and its helper layout (`forgelib/*.py` instead of `bin/lib/*.sh`) differ.
`forge/install.sh` remains a thin bash wrapper that checks for `python3` and runs `forge/installer.py`.

## Consequences
- `/forge-doctor` checks `python3 ≥ 3.9` (FAIL below) instead of the `jq` version and the bash-version WARN.
- The state machine and validators are ordinary, unit-testable Python; JSON handling, globbing and time arithmetic need no
  external tools, and the GNU-vs-BSD userland portability problems the design worked around disappear.
- Hook latency is unchanged in practice: each hook is one short-lived interpreter process, as each bash + jq hook was.
- Documentation written against the design's bash vocabulary (`gates.sh`, `jq -e`) is translated: validators are
  `forgelib.gates`, and JSON is validated with `python3 -m json.tool` or the Forge's own scripts.
- A machine without `python3` cannot run the Forge; such machines were already unable to run it without `jq`.
