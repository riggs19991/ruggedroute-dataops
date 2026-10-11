# Build log — how the Forge v1.0.0 was made (2026-10-11)

A record of the process that produced this system, kept so a later session can judge what was
verified, what was assumed, and why the design looks the way it does. The design itself is in
`docs/design/design-v2.md`; the rationale in `docs/DESIGN-RATIONALE.md`; the decisions in `docs/adr/`.

## Sequence

| Phase | What ran | Output |
|---|---|---|
| Research | 2 background agents: a Claude Code 2.1.296 primitives reference (fetched docs; 85 KB) and an orchestration/handoff/routing/verification patterns report (Anthropic engineering posts, papers, community frameworks; 67 KB) | `docs/design/research-claude-code.md`, `docs/design/research-patterns.md` |
| Experiments | headless `claude -p` probes in throwaway repos | plain project skills/agents/hooks load untrusted; a plugin vendored in the repo loads only after workspace trust; `Stop` and `SubagentStop` gates block and re-prompt headlessly; only the plain repo-relative form of a skill's `!` injection passes headless permissions; nested `.claude/rules` in subdirectories are auto-loaded (hence `payload/dot-claude`); exports written to `CLAUDE_ENV_FILE` leak across sessions (hence no exports) |
| Design | 12-agent judge panel: 4 independent proposals (mechanism-, cost-, reliability-, longevity-first), 3 judges (feasibility, cost per completed task, operator experience), one synthesis, 3 red-team attacks (docs conformance, lifecycle simulation, cost), one revision applying 75 findings | `docs/design/design-v2.md` (1,421 lines, 16 sections) |
| Build | shared library and contract by the architect; 6 parallel implementers on disjoint files (state machine, gates and checks, hook dispatcher, ops and installer, text artifacts, tests) | `payload/`, `installer.py`, `tests/` (282 tests green on first integration) |
| Review 1 | 5 adversarial reviewers (contract, hooks under real stdin, lifecycle simulation, security, docs vs code); every finding refuted independently by 2 agents; 147 agents in total | 71 findings, 64 confirmed (10 fatal, 36 major, 18 minor) |
| Fix 1 | 5 owners by file; regression tests per finding | 371 tests, hook smoke 25/25 |
| Review 2 | 3 reviewers (fatal regressions, full class-M lifecycle through the hooks, docs vs code), 1 refuter each | 29 findings, 16 confirmed (none fatal) |
| Fix 2 | 3 owners | 392 tests, hook smoke 26/26 |
| Live runs | real headless sessions in throwaway clones (Haiku standing in for the architect; hooks, scripts and skills real) | `/forge-task` → open T → edit → `forge-check` → `/forge-close` → commit; 14 turns, about one cent, zero permission denials on the final run |
| Install | `installer.py` into this repository as the first consumer | `.forge/`, `.claude/`, `CLAUDE.md` fragment, manifest; doctor 0 FAIL |

## Deviations from the design, with reasons

- Python 3 standard library instead of bash 3.2 + jq for every script (ADR 0002): python3 is present in every Claude Code cloud container and ships with the macOS developer tools that git requires; jq is not preinstalled on macOS; a 25-subcommand state machine and three validators are far more reliable in Python.
- `payload/dot-claude/` instead of `payload/.claude/`: Claude Code auto-discovers nested `.claude/rules/*.md` and injected the payload's stack rules into the build session.
- No `export PATH`/`export FORGE_ROOT` at session start; `forge_root()` ignores a `FORGE_ROOT` that names another checkout.
- Skill `!` injections use the plain repo-relative command with no `|| true`.

## What remains unverified ([U] in the docs)

`initialUserMessage` on `/clear`; the `permission_denials` and `modelUsage` fields of the headless JSON result (observed, not documented); exact Bash exit codes in `tool_response` (the check records carry the authoritative ones); worktree-isolated parallelism (off until `/forge-doctor --worktree` passes); every cost figure until the ledger measures it.

## Known residuals (good first Forge tasks)

- The main-session Bash guard denies any mutating shell command while no task is open, even when every path it touches is outside the repository (for example `rm -rf /tmp/x`). Relaxing it for paths provably outside the repository would remove a false deny.
- The handoff gate's refusal text for a `tdd` step whose `--expect-fail` run came back green should name the honest exits (fix the test, or return `BLOCKED`).
- The draft-path regex captures an `agent_id` only up to its first hyphen; real ids are hex tokens without hyphens, so this is latent.
- `forge-bench` has run only against a fake `claude`; the first real benchmark will set the measured routing thresholds.
