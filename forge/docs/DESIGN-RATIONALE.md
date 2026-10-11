# Design rationale

Why the Forge is built the way it is. The full argument, with a citation for every mechanism, is `docs/design/design-v2.md`;
the user's intent and the verified sandbox experiments are in `docs/design/requirements.md`; the platform facts are in
`docs/design/research-claude-code.md` (Claude Code 2.1.296) and the orchestration evidence in `docs/design/research-patterns.md`.

## The five theses (design §1)

1. **Plain project layout is the only form verified to load everywhere.** A plugin vendored under the project's
   `.claude/skills/forge/` did not load in a fresh headless session and loads only after workspace trust; plain `.claude/agents`,
   `.claude/skills` and project `settings.json` hooks load even untrusted. So the shipped form is plain layout expanded by an
   installer; the plugin manifest is a secondary user-level wrapper that silences itself inside a vendored repo.
2. **A rule that lives in a hook is a fact; a rule in a prompt is a request.** Plan-first, scope fences, handoff shape, evidence
   capture, STATUS integrity, routing at spawn, tool budgets and the policy-file lock are decided by hooks. What the platform cannot
   decide (`/clear` in interactive mode) is designed as the next-best enforcement and labelled [I]. Version 2 also closed the back
   doors of version 1: shell writes, hand edits to the enforcement layer, and gates that depended on undocumented behaviour.
3. **Orchestration pays only for bulk, file-disjoint work; one dependent chain belongs in one context; the frontier model at low
   effort is often the cheapest solver per task.** Trivial, small and extreme tasks run inline in the architect (Fable codes the
   hardest work, as the user asked); medium and wide tasks run in exactly one fresh-context builder with one verifier; cheap workers
   run only on plan-proven disjoint units. Bookkeeping moved from Fable turns into zero-token hooks.
4. **Verification is evidence, not claims, and depends only on files the Forge writes itself.** Gates audit a hook-captured
   evidence log, exact exit codes from `forge-check`, and git commits the gate itself made — never the transcript. A fresh-context
   verifier re-runs the checks. Work whose only real check is external (a scheduled workflow, an emulator) has a human-attested
   evidence path instead of a dead end.
5. **Every harness component is a stale-able assumption, and every cost figure is a hypothesis until the ledger measures it.**
   Clearing policy, routing thresholds, budgets and verifier tiers are data in a project-owned binding; cost rows are `measured`,
   `operator` or `unknown`, never guessed; the system is versioned with a file-ownership upgrade contract.

## How the design was reached

- **Research first.** Two research passes established what Claude Code 2.1.296 actually does (hook events and output fields, agent
  and skill frontmatter, settings, plugin loading) and what the published evidence says about orchestration cost. Behaviour that was
  only observed in the sandbox, not documented, is labelled **[observed]** and carries a doctor probe; behaviour that is neither is
  **[U]** with a named fallback.
- **Judge panel.** Competing proposals were scored by judges; design v2 §15 lists the 30 fatal flaws they raised (for example: a
  plugin form that does not load untrusted, plan-first enforced only at Stop, gates that grep the undocumented transcript, a Stop gate
  that runs into the 8-continuation cap) and where each one is resolved.
- **Red team.** 75 findings against design v1 were each checked against the research files before being applied (§16). All 75
  were applied; two only partially, with the rejected remedy and the contradicting evidence stated: #14 (setting
  `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=2` — the variable is documented only as raising the cap) and #55 (making Fable-low the default M
  builder — the user's intent is Opus for easier work, and the cost model prices the chain route higher on equal assumptions; the
  ledger flip is symmetric and measured-only instead).
- **Conflicts resolved by evidence** (§12.1): e.g. `Agent`-tool dispatch only (the `agent_type` of `context: fork` skills is
  undocumented); one builder per M task; the verifier grades a committed range, not the working tree; fail-open Stop vs fail-closed
  PreToolUse/SubagentStop; sequential L by default, parallel only with proven worktrees.
- **Implementation language** changed after the design: Python 3 standard library instead of bash 3.2 + jq (ADR 0002).

## The cost model (design §11) and its honesty caveats

Prices: Fable $10/$50, Opus $4/$20, Sonnet $2/$10, Haiku $0.10/$0.50 per million input/output tokens. Each row is
`Σ(calls × average context) × input price + output tokens × output price`, because every tool call resends the whole context. Two
columns apply **the same assumption to both arms**: *list* (no cache) and *cached* (80% of input tokens are cache reads at 10% of the
input price). The baseline is one Fable session at `low` effort doing the whole task in one growing context.

| Shape (ruggedroute-dataops) | Solo Fable low (list / cached) | Forge (list / cached) | Reading |
|---|---|---|---|
| T README/config tweak | $1.10 / $0.38 | $1.83 / $0.62 | +$0.24 cached: the price of a status trail and a check record |
| S one-normalizer fix | $3.20 / $1.18 | $4.92 / $1.72 | +$0.54: a trail-and-verifier buy, not a saving |
| M-small, 3 files, one chain | $11.75 / $4.55 | $12.03 / $4.16 ($16.2 / $5.6 with 25% expected escalation) | parity to +23% for a fresh verifier and a clean architect context |
| M-large (planner forked) | ≈ M-small solo | $17.6 / $5.9 | +30%: the planner is the overhead, so it is forked only above 5 files or 2 dirs |
| W, 40-file migration | $102 / $32.9 | $110 / $35.4 | +8%: a plan and a fresh verifier for the price of the handoff |
| L, 6 disjoint units | $45 / $16.2 | $48 / $15.5 | parity; wins outright only when a solo run would lose state across compactions or wall-clock matters |
| X root cause, inline | $42.5 / $13.7 | $55.6 / $17.8 | +30% by design: the investigation is paid once, plus a fresh verifier |
| R-small, workflow + upload | $4.0 / $1.48 | $9.1 / $3.1 | ×2.1: the tail is priced, not hidden |
| Driver mode, per phase | — | +$0.45 / +$0.16 | measured cost rows and process-boundary clearing |

Caveats, stated plainly:
- **These are planning hypotheses, not measurements.** Call counts and context sizes are assumptions; `forge-bench` and `measured`
  ledger rows replace them. Interactive close rows are `unknown` by construction (the model cannot read `/usage`).
- **The Forge is not cheaper per task in most rows.** Its savings come from (1) bookkeeping moved into zero-token hooks, (2) the
  architect at `medium` and bookkeeping skills at `low` instead of Fable's default `high`, (3) the 1-hour worker cache TTL, (4) cheap
  tiers on plan-proven disjoint units, (5) no redo of work lost to dead sessions or compaction, (6) a close ritual sized to the class.
  It costs more by design for T/S (a trail and a verifier, tens of cents) and X/R (fresh verification of the riskiest work).
- **Version 1's claims are withdrawn**: "L ~55% cheaper" and "T/S at parity" did not survive a consistent cache assumption.
- **The 80% cache-read share is itself an assumption**; `forge-bench` reports the observed share so it can be checked.
- `total_cost_usd` from `claude -p` is a client-side estimate.

## Pointers

- `docs/design/design-v2.md` — the build spec: lifecycle (§3), routing (§4), schemas (§5), context clearing (§6), gates (§7),
  layout (§8), docs (§9), install (§10), cost (§11), risks and unknowns (§12), exact file contents (§13), judges' flaws (§15),
  red-team log (§16).
- `docs/design/requirements.md` — the user's intent and the experiments that fixed the packaging decision.
- `docs/design/research-claude-code.md`, `docs/design/research-patterns.md` — the evidence base.
- `docs/adr/` — decisions about the Forge itself.
