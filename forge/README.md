# The Forge

A document-driven AI engineering team that runs inside Claude Code. A Fable architect (your main session) plans, routes, audits and
codes the hardest work; disposable fresh-context workers (Opus, Sonnet, Haiku, Fable) implement and refute; hooks enforce the rules.
All durable state is plain files in the consumer repository — `.forge/STATUS.json`, one directory per task, lessons, decisions and
an append-only ledger — so nothing depends on any session's memory.

Version: see `VERSION` (1.0.0). Runtime: Claude Code ≥ 2.1.295, Python ≥ 3.9 (standard library only), git.

## What it gives you

- **Plan first.** No source edit without an open task; medium and larger work is planned before a builder starts.
- **Status is the truth.** `.forge/STATUS.json` is written only by `.forge/bin/forge-status`, injected at every session start, and a
  turn cannot end while it is out of date.
- **Evidence, not claims.** Workers cannot return without a handoff whose checks ran after their last edit; a fresh-context verifier
  re-runs them against the committed diff.
- **Cost-aware routing.** Trivial, small and extreme work stays inline in the architect; one dependent chain goes to one builder; cheap
  tiers only on plan-proven disjoint units; every cost row is measured or marked unknown.
- **Context clearing by construction.** Work runs in disposable contexts; each phase ends at a CLEAR POINT; the next session restarts
  itself from STATUS.

## The three rituals

| Command | What happens |
|---|---|
| `/forge-task <title>` | The architect declares the files it will touch and opens the task in one script call (class T/S/M/W/L/X, risk overlay R), then works inline or writes / dispatches the plan. |
| `/forge-next` | Executes STATUS `next_action`: dispatch the routed worker, dispatch the verifier, adjudicate, attest or close. |
| `/forge-close` | Closes with a ritual sized to the class (one line for T, a short handoff for S/X, a full handoff plus lessons for M/W/L), commits, and prints the CLEAR POINT. Then `/clear`. |

Occasionally: `/forge-doctor` (is the Forge alive here?) and `/forge-gc` (documentation garbage collection, cost rollup).

## Install into a repository

```bash
# from a checkout of the Forge source (this directory):
bash forge/install.sh --target /path/to/repo [--effort low|medium] [--no-model | --with-model] [--with-bench] [--dry-run]
# from another local checkout:
bash install.sh --from ~/src/ruggedroute-dataops --target /path/to/repo
# from a published tag (run inside the target repository):
curl -fsSL https://raw.githubusercontent.com/riggs19991/ruggedroute-dataops/v1.0.0/forge/install.sh | bash -s -- --tag v1.0.0 --target .
# a fork: add --repo <owner>/<repo> (the payload may sit at the repository root or under forge/)
```

`--tag` fetches that tag from `--repo`, which defaults to `riggs19991/ruggedroute-dataops` (the Forge lives under `forge/` there);
`--repo` without `--tag` is a usage error. Upgrade an installed Forge with the same command plus `--upgrade`; it prints the
`CHANGELOG.md` sections between the installed `.forge/VERSION` and the new version (also with `--dry-run`). `--no-model` and
`--effort` are recorded in `.forge/install-manifest.json` (`"options"`) and honoured by every later install or upgrade without the
flags; `--with-model` undoes a recorded `--no-model`, and a new `--effort` replaces the recorded one (docs/UPGRADING.md).

The installer copies the payload (`payload/.forge/` to `.forge/`, `payload/dot-claude/` to `.claude/`), merges
`.claude/settings.forge.json` into `.claude/settings.json`, appends the CLAUDE.md fragment, detects the stack and writes
`.forge/binding.json` (only when absent), an idle STATUS and the install manifest, then runs `.forge/bin/forge-doctor`.
The settings fragment is generic: `permissions.allow` gains one `Bash(<prefix> *)` rule per `binding.verify[].cmd`, `bootstrap`
and `smoke` (a pip rule only when the binding's bootstrap uses pip). Local settings scalars (`model`, `effortLevel`,
`plansDirectory`, `env.*`) are never overwritten: differences are printed as `settings: <key> local=… -> fragment=…`, and only
`--force-settings` applies them. `--force` overwrites locally edited Forge-owned files only. Commit the result, open Claude Code and run `/forge-task <first task>`. Worked bindings for the first three
consumers are in `bindings/`.

## Repository layout

```text
forge/
├── VERSION  CHANGELOG.md  README.md  install.sh  installer.py
├── payload/                       # copied verbatim into a consumer repo
│   ├── .forge/
│   │   ├── FORGE.md RUNBOOK.md ROUTING.md HOOKS.md SCHEMAS.md GATES.md ROLE-architect.md VERSION
│   │   ├── bin/                   # forge-hook forge-status forge-check forge-gate forge-run forge-doctor forge-bench + forgelib/
│   │   ├── schemas/               # assertion lists + routing.json (the routing matrix as data)
│   │   └── templates/             # STATUS, binding, plan, brief, handoff, verdict, lesson, ADR, ruling, CLAUDE.md fragment
│   └── dot-claude/                # installed as .claude/ (not named .claude here, so Claude Code never loads it from this tree)
│       ├── agents/                # 8 forge-* agents
│       ├── skills/                # 6 forge-* skills
│       ├── rules/                 # path-scoped stack rules
│       └── settings.forge.json    # hooks, permissions, env, model, effort fragment
├── bindings/                      # worked binding.json for ruggedroute-dataops, ruggedroute-android, millwright-kb
├── evals/                         # task set for forge-bench and the per-model-generation re-sweep
├── migrations/                    # idempotent upgrade steps (schema MAJOR only)
├── plugin/                        # secondary user-level plugin wrapper (generated by tools/make_plugin.py; CI runs --check)
├── tests/                         # hook smoke tests and script tests
└── docs/
    ├── ARCHITECTURE.md  UPGRADING.md  DESIGN-RATIONALE.md  MODULE-API.md
    ├── adr/                       # decisions about the Forge itself
    └── design/                    # design v2 (the build spec), requirements, research
```

## Documentation

- Start here inside a consumer repo: `.forge/FORGE.md` (≤ 120 lines; one read is enough to act).
- Operating and troubleshooting: `.forge/RUNBOOK.md`. Gates and their guarantees: `.forge/GATES.md`. Hooks: `.forge/HOOKS.md`.
  Data shapes: `.forge/SCHEMAS.md`. Routing rationale: `.forge/ROUTING.md`.
- How the system fits together: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Why it is built this way:
  [docs/DESIGN-RATIONALE.md](docs/DESIGN-RATIONALE.md). Upgrading: [docs/UPGRADING.md](docs/UPGRADING.md).
- Module contract for contributors: [docs/MODULE-API.md](docs/MODULE-API.md). The full build spec:
  [docs/design/design-v2.md](docs/design/design-v2.md).
