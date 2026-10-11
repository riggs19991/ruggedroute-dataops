# ROUTING.md — who does the work, on which model, at which effort, and why

Source: design §4 (and §3 for the per-class paths, §11 for the cost reasoning). The matrix as data lives in
`.forge/schemas/routing.json` (Forge-owned): that is what `.forge/bin/forge-status` and `forge-planner` read. This file is the
rationale, for humans and for the architect's occasional re-sweep. Per-project overrides and measured flips live in
`.forge/binding.json` → `routing` (project-owned).

**The principle.** Routing is decided at intake (class) and at plan time (per-step tier) from **structural signals over the declared
edit set**, never from the executing model's own sense of how hard the work is. Effort is the first lever; model tier is the second.
Orchestration pays only for bulk, file-disjoint work; one dependent chain belongs in one context; the frontier model at low effort is
often the cheapest solver per task.

## Signals (`.forge/bin/forge-status open` computes them; `.forge/tasks/<id>/signals.json`)

| Signal | Source | Used for |
|---|---|---|
| `files`, `dirs`, `creates` | the architect's `--files` / `--creates` declaration (`size_source: declared`) | size class; inline `allowed_paths` for T/S/X; the scope ceiling for every class |
| `importers` | `git grep -l` of each declared module's import name, count only | advisory: ≥ 5 raises the S verifier Sonnet → Opus; ≥ 10 raises the M verifier Opus → Fable |
| `recent_cochanges` | `git log --name-only -20 -- <declared>` | advisory: files that usually change together but are not declared go into the plan's *Current State* |
| `tests_present` | for every declared or created source path, a `binding.test_globs` file exists where its tests live, or the plan's first DoD adds one | whether cheap-first routing is **allowed** (rule 2) |
| `risk_hits` | (declared ∪ creates ∪ every brief's `allowed_paths`) ∩ (`protected_paths` ∪ `risk_paths`), plus title ∩ `risk_words` | the R overlay |
| `important_hits` | declared ∩ `binding.important_paths` (LIVE layers, release paths) | raises the verifier to `fable` (rule 4) |
| `disjoint_units` | plan time: pairwise intersection of `steps[].allowed_paths` | whether L is **allowed** |
| `chain` | plan-meta flag: a shared module feeds several consumers inside the step | M → `fable/low` builder |
| `novelty`, `ambiguity` | architect judgment; `needs_clarification` in the plan forces a user question | class X; a clarification turn |

Title-token grep is **never** used for size: on this kind of repo it produced 15-57 candidate files for one-line fixes.

## The matrix

| Class | Definition (declared set) | Plan | Who builds (model/effort) | Mode | Verifier | Budget cap (USD) |
|---|---|---|---|---|---|---|
| **T** | ≤ 2 files, one-sentence diff, no risk hits | none; `--why` ≥ 20 chars | architect inline (`fable`, session effort) | inline | none; a passing `forge-check` record is required at close | 1 |
| **S** | ≤ 3 files, ≤ 2 dirs, tests present (or the plan adds them first), no risk hits, no novelty | inline plan section by the architect (`mode: inline`, zero steps) | architect inline | inline | `forge-verifier sonnet/medium` only if tests were added or changed (`opus` when `importers ≥ 5`); else `forge-check` | 3 |
| **M** | 3-10 files and ≤ 3 dirs, one dependent chain, clear after planning | M-small (≤ 5 files ∧ ≤ 2 dirs ∧ no risk): the architect writes plan + brief; M-large: `forge-planner fable/medium` | **one** `forge-builder opus/medium` (`fable/low` when `chain` or `binding.routing.m_builder == "fable-low"`) | single, **exactly one step** | **one** `forge-verifier opus/medium` (`fable` when `important_hits` or `importers ≥ 10`) | 10 (12 chain) |
| **W** | one dependent chain, > 10 files or > 3 dirs, no disjoint split | `forge-planner fable/high` | `forge-builder-wide fable/low` (`medium` on retry) | single, one step | `forge-verifier fable/medium` | 25 |
| **L** | ≥ 3 units with pairwise-disjoint `allowed_paths` | `forge-planner fable/high` | per unit: `forge-builder-s sonnet/medium`; `forge-mechanic haiku/medium` when `mechanical` and clear of `mechanic_denied_paths`; `forge-builder opus/medium` for an M-sized unit; a shared prerequisite may be `red_ok_until` | sequential; `parallel` only with proven worktrees | per unit `sonnet/medium`; then one `fable/medium` spot-check (20%, min 1) + the full suite | Σ unit budgets × 1.2 |
| **X** | novel, ambiguous, root-cause/outage, architecture change, or two prior escalations on one step | short inline plan section (hypothesis, DoD, rollback) | **architect inline** (`fable`, `medium` via `/forge-investigate`) | inline | `forge-verifier fable/medium`, mandatory | 30 |
| **R** overlay | any risk hit (workflow YAML, upload / alias-flip code, licence or attribution fields, secrets, deletions …) | plan must have *Rollback* with a command | T/S-sized: architect inline at `medium`; M/W/L: floor `forge-builder fable/low`; `forge-builder-s` / `forge-mechanic` forbidden | per base class | `forge-verifier fable/medium`; irreversible commands `ask` (interactive) / `deny` + blocked (driver); `close --human-ack` | base × 1.5 |

Why each row looks the way it does:
- **T, S, X run inline.** A trivial or small change costs less in one context than in any split; X (root cause, outage, novelty)
  cannot be planned before it is debugged, and the user's intent is that Fable codes the hardest work itself.
- **M is exactly one step, one builder, one verifier.** One dependent chain loses information at every handoff; gates are per step,
  so a multi-step M is either one brief or class L.
- **W exists because a wide chain is still a chain.** Splitting a cross-cutting change into "disjoint" units that are not disjoint
  produces merge-shaped bugs; one Fable-low context with a large turn budget and a plan costs about what a solo run costs.
- **L is the only place cheap tiers pay**, because the work is bulk and path-disjoint. The planner, per-unit verifiers and the Fable
  spot-check are what the cheap tiers buy.
- **R is an overlay, not a class**: the size decides the path; risk raises the floor, adds a rollback and a human acknowledgement.

## Rules encoded in `forge-status` (deterministic)

1. **Don't over-orchestrate.** `mode: parallel` needs ≥ 3 pairwise-disjoint units **and** `binding.git.worktree_isolation == true`;
   otherwise `forge-status plan` rewrites it to `single` and journals why. A shared dependency feeding several consumers is one M/W
   chain step (optionally `red_ok_until`), then L units for the dependants.
2. **Cheap-first only with a failure signal.** A tier below the class default (`sonnet` for an M-sized unit, `haiku` for a
   non-mechanical unit) is accepted only when `tests_present` holds for every path in the step; otherwise start at the class's top rung.
3. **Effort before model.** On FAIL, verdict tags `skipped-file`, `no-check-run`, `not-double-checked` → raise `effort` one level on
   the same model; any other tag → change model.
4. **Verifier tier ≥ builder tier; importance raises the verifier, not the builder.** `important_hits`, a user-stated "important", or
   `importers ≥ 10` → `fable` verifier.
5. **The mechanic never verifies and never touches risk, protected or `mechanic_denied_paths`**; `forge-status plan` refuses
   `mechanical: true` for a step whose `allowed_paths` intersect them.
6. **Escalation ladder, capped.** Round 1: resume the same worker (`SendMessage`) with the blocking findings; its block counter resets.
   Round 2: `.forge/bin/forge-status step-start <id> <NN> --from failed|clean` (mandatory once `attempts > 1`), then a fresh worker one
   rung up — `sonnet/medium → opus/medium → fable/low → fable/medium` — with the verdict appended to the brief's *Known failed
   approaches*. Round 3: `ruling.md` (Decision — Why — Cost if wrong — Evidence), then re-plan or `block`. `step-start` refuses
   `attempts > 3` without a ruling; `verify_attempts` is capped at 2 per step without a ruling.
7. **Environmental failures do not escalate.** A FAIL whose blocking findings are all tagged `env-cannot-run` sets
   `phase: awaiting_external` with `next_action` naming the exact local commands: no builder re-run, no round increment.
8. **Price the tail, don't hide it.** X, W and R rows carry `expected_premium: true` in the ledger.
9. **Budgets are caps, not countdowns.** `binding.budgets.<class>` → `task.budget.cap_usd`. Driver mode enforces it with
   `--max-budget-usd = cap × multiplier − Σ measured phase rows` (minimum 1; the execute phase of X/W/R may take up to 70%).
   Interactive mode shows **no** spend to the model (a countdown induces context anxiety); `/forge-gc` reports measured spend to the
   operator.
10. **Measure, don't assume.** Every open / dispatch / attempt / verdict / close writes a ledger row. `/forge-gc` computes cost per
    passed task, escalation rate and the `fable-low` vs `opus-medium` comparison **only over `cost_source: measured` rows** and reports
    the count of unmeasured rows beside them. Escalation rate > 40% proposes starting one rung higher; ≥ 10 measured rows showing the
    other M builder cheaper per passed task proposes a flip in either direction. Flips are ADRs, applied by the operator to
    `binding.routing`.
11. **Advisory signals only raise tiers.** `importers`, `recent_cochanges`, `important_hits` never lower a class or a tier.
12. **Re-sweep per model generation** (checklist below; `forge-bench` runs the measurement).

Spawns are checked at dispatch, not trusted: the `PreToolUse(Agent)` guard allows a `forge-*` worker only when a pending step names
the same agent, model and effort (aliases and full ids normalized to `haiku|sonnet|opus|fable`), GATES.md gate 9.

## Consumer overrides (`binding.json` → `routing`, project-owned)

```json
"routing": {
  "architect_effort": "medium",
  "m_builder": "opus-medium",
  "overrides": [
    { "name": "ui-compose", "paths": ["app/src/main/java/**/ui/**/*.kt"], "builder": { "agent": "forge-builder", "model": "opus", "effort": "medium" }, "min_verifier": "opus" }
  ],
  "measured": { "note": "filled by /forge-gc from measured ledger rows only" }
}
```

`forge-status plan` applies an override to every step whose `allowed_paths` intersect its `paths` and refuses a lower tier.
`architect_effort` is written by the installer into `settings.json` `effortLevel` and passed by `forge-run` as `--effort`.

## Re-sweep checklist (once per model generation, and whenever a ledger trend says so)

Thresholds and tiers are hypotheses about today's models. When a new model generation ships (or `/forge-gc` reports an escalation
rate above 40% for a tier):

1. Update the pinned full model ids in `.claude/agents/forge-*.md` and the alias normalization in `forgelib/common.py` (a Forge
   release, not a project edit); confirm `claude --version` meets the doctor minimum.
2. Re-run the doctor probes that guard [U] behaviour: `.forge/bin/forge-doctor --probe-hooks`, `--driver`, `--probe-clear`,
   `--probe-maxturns`, `--worktree`; record what changed.
3. Run `.forge/bin/forge-bench <taskset.json>` on the eval set (`forge/evals/`) for both arms (driver vs solo Fable at `low`): pass rate
   and cost per passed task by class, plus the cache-read share (the cost model assumes 80%).
4. Per class, ask: does the class default still pass at the rate it did? Would one rung lower pass with tests present (rule 2)? Does the
   ladder still start at the right rung (escalation rate per tier)?
5. Compare the M builders (`opus-medium` vs `fable-low`) per passed task over measured rows only; propose a flip only with ≥ 10 rows.
6. Re-check efforts: the architect's `architect_effort`, the skills' `effort:` keys, and the agent frontmatter `effort`.
7. Re-check the class boundaries (T ≤ 2 files, S ≤ 3 files / ≤ 2 dirs, M ≤ 10 files / ≤ 3 dirs) against how often `open` was
   refused or a task was re-classed.
8. Write each change as an ADR in the Forge repo (`docs/adr/`) for defaults in `schemas/routing.json`, or in the consumer's
   `.forge/decisions/` for a `binding.routing` flip; ship defaults as a Forge MINOR release.
