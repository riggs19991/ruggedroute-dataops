# Architecture

The Forge in one page. The build spec is `docs/design/design-v2.md`; the module contract is `docs/MODULE-API.md`. Section numbers
below (§n) refer to the design.

## The parts

| Part | Where (consumer repo) | Role |
|---|---|---|
| Architect | the main Claude Code session (Fable 5.1, `effortLevel` from the binding) | intake, classification, routing, briefs, adjudication; codes T/S/X work itself; never implements M/W/L |
| Workers | `.claude/agents/forge-*.md` (8 files; shipped as `payload/dot-claude/agents/`) | disposable fresh-context subagents dispatched with the `Agent` tool: planner, builders (Opus/Fable, wide Fable, Sonnet, Haiku mechanic), verifier, scout, librarian |
| Skills | `.claude/skills/forge-*/SKILL.md` (6) | the rituals: `/forge-task`, `/forge-next`, `/forge-close`, `/forge-doctor`, `/forge-gc`, internal `forge-investigate` |
| Hooks | `.claude/settings.json` (merged from `settings.forge.json`) → `.forge/bin/forge-hook` | twelve registrations, one dispatcher: injection, fences, evidence capture, gates, Stop gate, config guard |
| State machine | `.forge/bin/forge-status` → `.forge/STATUS.json` | the only writer of STATUS; refuses illegal transitions (exit 3) |
| Checks and validators | `.forge/bin/forge-check`, `.forge/bin/forge-gate` | exact exit codes into `checks/` records; plan / handoff / verdict validation shared with the hooks |
| Driver and probes | `.forge/bin/forge-run`, `forge-doctor`, `forge-bench` | unattended phases as separate processes; self-check; measured cost |
| Durable state | `.forge/` | STATUS, binding, tasks/, lessons/, decisions/, ledger, history, CHANGELOG — plain files, committed |

Every script is Python 3.9+ standard library (ADR 0002), invoked as `.forge/bin/<tool>` from the repository root. Library code lives
in `.forge/bin/forgelib/` (`common`, `status`, `gates`, `checks`, `hooks`).

## Task lifecycle

```text
 /forge-task "title"
      │  architect declares --files/--creates, class, risk, why
      ▼
 forge-status open ──────────────── refuses illegal class/size/risk (exit 3)
      │  T-NNNN, signals.json, scope
      ├── class T ──► edit inline (fence: declared files) ─► forge-check <id> main ─► close --one-line
      │
      ├── class S/X ─► plan-inline.md ─► forge-status plan ─► edit inline ─► forge-check main
      │                                   (X via /forge-investigate)      │
      │                                         verifier (S if tests changed; X always, Fable)
      │                                         [verdict gate → step-verdict main → task.inline_verdict]
      │                                                                   ▼
      │                                    close --handoff (short form; X, and S with changed tests, need PASS)
      │
      └── class M/W/L ─► plan.md + brief-NN.md (architect for small M; forge-planner otherwise)
                              │  [SubagentStop plan gate]
                              ▼
                        forge-status plan ── routes steps (§4.3 rules), phase execute
                              │
             ┌────────────────┴──── per step (M/W: one; L: ≥3, mode single = one at a time) ──────┐
             │ Agent(forge-builder…) ─[PreToolUse spawn guard: agent/model/effort match → step-start]
             │   worker Reads brief-NN.md ─[PostToolUse: bind agent_id to the step]
             │   edits inside allowed_paths ─[PreToolUse fence + tool budget; PostToolUse evidence rows]
             │   forge-check --expect-fail (red) … forge-check (green) → checks/ records
             │   final message = HANDOFF ─[SubagentStop handoff gate → commit → step-report]
             │ Agent(forge-verifier…) ─[spawn guard → step-verifying]
             │   git diff base..commit, re-run forge-check --ratchet
             │   final message = VERDICT ─[SubagentStop verdict gate → step-verdict]
             │        PASS → done │ FAIL → ladder (resume → one rung up → ruling) │ env-cannot-run → awaiting_external
             │        NEEDS_CONTEXT/BLOCKED → step blocked → step-start --from failed|clean + fresh worker
             └────────────────────────────────────────────────────────────────────────────────────┘
                              ▼
                        /forge-close: handoff.md, lessons, ADR if durable → forge-status close
                              │  scope backstop, CHANGELOG, history, ledger, commit, context_state stale
                              ▼
                        FORGE CLEAR POINT → /clear → SessionStart re-injects STATUS (+ auto-resume [U])
```

Phase values: `idle → intake? → plan → execute → (verify) → awaiting_external? → close → done`, with `blocked` reachable from any
phase. Step values: `pending → running → reported → verifying → done | failed | awaiting_external | blocked`.

## Hook map

| When | Event (matcher) | What the Forge does | Fails |
|---|---|---|---|
| session start / `/clear` / compaction | SessionStart (`startup\|resume\|clear\|compact`) ×2 | writes session id and `hooks-alive`; injects the STATUS digest, banner, newest handoff tail, git state, lessons head, binding digest (≤ 9,800 chars); injects the architect role when there is no `agent_type`; auto-resume on `clear` | open |
| every prompt | UserPromptSubmit | one-line reminder of task/phase/next action; resets per-turn counters; `?` marks a chat turn | open |
| before Edit/Write/NotebookEdit | PreToolUse | policy lock; main-session plan-first and scope fence; worker fence, binding check, tool budget | **closed** |
| before Agent | PreToolUse | spawn routing guard; runs `step-start` / `step-verifying`; journals built-ins | **closed** |
| before Bash | PreToolUse | irreversible commands (`ask` / `deny` in driver); main-session mutation heuristic; worker and read-only allow-lists; tool budget | **closed** |
| after Bash/Edit/Write/Read | PostToolUse | evidence rows; brief binding on Read; stamps `checks/` records with `agent_id`; `dirty-main` | open |
| after a failed Bash | PostToolUseFailure | failure evidence row | open |
| worker starts | SubagentStart (`forge-.*`) | agent record; one-line format reminder | open |
| worker returns | SubagentStop (planner / builders / verifier) | plan gate; handoff gate + commit + `step-report`; verdict gate + `step-verdict`; two-block caps | **closed** |
| turn end | Stop | blocks while STATUS does not reflect the turn (`dirty-main`, `dirty-worker`, hand edit); 2-block soft cap | open |
| manual `/compact` | PreCompact (`manual`) | blocks while a dirty marker exists | open |
| settings reload | ConfigChange (`project_settings\|local_settings`) | blocks a reload that drops or alters a Forge hook entry | open |
| API failure / exit | StopFailure, SessionEnd | incident file; last-session record | open |

"Closed" = `onFailure: block` plus a deny/block on a dispatcher crash; "open" = a `systemMessage` on a crash. Details: `.forge/HOOKS.md`.

## Where truth lives

- **STATUS.json** — where work stands. Only `forge-status` writes it; the Stop gate compares its sha with the one `forge-status`
  recorded, so a hand edit is caught.
- **evidence.jsonl** — what each agent did (hook-written, keyed by `agent_id`).
- **checks/** — exact exit codes (script-written; re-stamped with the caller's `agent_id` by the hook).
- **git commits** — the handoff gate commits each step before STATUS records it; the verifier grades the committed range.
- **ledger.jsonl** — routing and cost, `measured` / `operator` / `unknown`, never guessed.

Gates read only these; never a transcript (design §1 thesis 4, §12.1).

## Context clearing

No hook can trigger `/clear`. The design composes: (1) M/W/L work never enters the architect's context (subagents return only their
final message); (2) the Stop gate refuses to end a turn until STATUS reflects it; (3) `/forge-close` ends at a CLEAR POINT and sets
`context_state: stale` (the clear itself is instructed, [I]); (3b) in driver mode `forge-run` starts a new process per phase
(guaranteed); (4) SessionStart re-injects the digest on every start, clear and compaction; (5) auto-resume on `clear` ([U], fallback
`/forge-next`); (6) manual compaction is blocked while state is dirty. Design §6.

## Installation forms

The shipped form is the plain project layout (`.claude/agents`, `.claude/skills`, `.claude/rules`, project `settings.json` hooks),
because it is the only form verified to load everywhere, including untrusted cloud sessions. A user-level plugin wrapper (`plugin/`)
is secondary: `forge-hook --plugin` does nothing inside a repo that has the plain install (`.forge/VERSION`) and nothing at all in a
repository without a Forge install (no `.forge/binding.json` or `STATUS.json`), so enabling it user-wide never fences unrelated
projects. In the Forge source tree the payload's `.claude/` ships as `payload/dot-claude/` (so Claude Code never loads it while you
work on the Forge itself); the installer copies it to the target's `.claude/`. Ownership of every file is the upgrade contract
(docs/UPGRADING.md).
