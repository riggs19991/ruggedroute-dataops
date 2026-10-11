---
name: forge-close
description: Close the current Forge task with a ritual sized to its class: one line for T, a short handoff for S/X, the full handoff plus lessons/ADRs for M/W/L; records status, commits, and announces the CLEAR POINT. Use when the task's steps are done, or with --partial to park it.
argument-hint: "[--partial]"
effort: low
allowed-tools: Bash(.forge/bin/forge-status *), Bash(git diff *), Bash(git status *), Bash(git log *), Read, Write, Edit
---
Close the open task ($ARGUMENTS):
```!
"${CLAUDE_PROJECT_DIR}"/.forge/bin/forge-status get summary --lenient || true
```

- Class T: `.forge/bin/forge-status close <id> --one-line "<what changed> | <checks/ record path>"`. Nothing else.
- Class S or X: write `.forge/tasks/<id>/handoff.md` from `.forge/templates/handoff-short.md` (Where things stand · Done, with evidence · Remaining, plus the json block; evidence only from checks/ records and verdicts you have read), then `close <id> --handoff <path>`.
- Class M, W, L: write `handoff.md` from `.forge/templates/handoff.md` (mandatory sections plus any optional section that carries information); promote worker `failed_approaches` and corrections worth keeping into `.forge/lessons/<slug>.md` (one-line summary first; add to INDEX.md); write `.forge/decisions/NNNN-<slug>.md` only for a durable decision; then `close <id> --handoff <path>`.
- Risk R: first show the operator `git diff --stat <task base>..HEAD` and the plan's Rollback section, then pass `--human-ack "<name> reviewed diff <sha>"` exactly as they state it.
- `--partial` requires `ruling.md`. Pass `--cost <usd>` only if the operator gave you a number from /usage; never estimate one.
`close` appends the CHANGELOG line and commits by itself. Your last line must be exactly: `FORGE CLEAR POINT — <id> <done|parked> → next: <next_action>. Run /clear (auto-resume will fire).` unless binding.clear_policy is never, in which case: `FORGE PHASE CLOSED — <id> → next: <next_action>.`
