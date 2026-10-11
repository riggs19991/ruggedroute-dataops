# Forge evals

A small, real task set for measuring the Forge against a solo session, and the regression bar for the per-model-generation re-sweep
(`.forge/ROUTING.md` §Re-sweep checklist; design §4.3 rule 12, §11). Cost figures in the design are hypotheses until these runs
replace them.

## Task file format (`tasks/*.json`)

| Field | Meaning |
|---|---|
| `id` | stable identifier (also the file name) |
| `repo` | the consumer repository the task belongs to |
| `title` | the one-line task title, exactly what an operator would type after `/forge-task` |
| `class` | the expected Forge class (T/S/M/W/L/X); a run that opens the task in another class is reported, not failed |
| `base` | the commit the run starts from (a fresh local clone, `git clone --shared`, detached at this sha; each arm gets its own clone and its own `.forge/` state) |
| `check` | a shell command run from the repository root after the run; exit 0 = the task passed. It fails at `base` |
| `dod` | the definition of done in EARS form, for humans and for scoring partial runs |

## The set (ruggedroute-dataops)

| Task | Class | What it exercises |
|---|---|---|
| `t-readme-tweak` | T | the trivial path: one declared file, `forge-check main`, `close --one-line` |
| `s-normalizer-fix` | S | the small path: inline plan, a tolerant-normalizer fix with a new unit test, the Sonnet verifier because tests changed |
| `m-new-layer-qa` | M | the medium path (design §3 worked example): architect-written plan and brief, one Opus builder, one Opus verifier, tests added first (`tests_present=false`) |

Each `check` was confirmed to fail at `base` (9da9ae9). The M check needs `pytest` (`binding.bootstrap` installs it).

## Running

With the optional bench add-on installed (`install.sh --with-bench`):

```bash
.forge/bin/forge-bench forge/evals/tasks/ [--out .forge/COST-REPORT.md]                 # the whole set, files in name order
.forge/bin/forge-bench forge/evals/tasks/m-new-layer-qa.json [--arms driver,solo]    # one task file (a single JSON object)
```

`<taskset>` is a directory of task files, one task file, or a JSON list of tasks; `forge-bench` reads `title`, `base`, `check` and
`class` and ignores the other keys. `--dry-run` validates the set and prints the commands without spending.

`forge-bench` runs each task twice from a fresh clone at `base` — the driver arm (`/forge-task <title>` for intake, then `forge-run`) and the solo arm
(`claude -p --model fable --effort low --max-budget-usd <cap> "<title>"`) — records pass/fail from `check`, `total_cost_usd` and the
cache-read share, and writes cost per passed task by class for both arms with pass rates. Rows it writes to the ledger are
`cost_source: measured`.

Three tasks are a smoke set, not a benchmark. The design's measurement plan is 20-50 real tasks per run; add tasks here (one file
each, a `check` that fails at `base`) as real work closes, especially W, L, X and R shapes.
