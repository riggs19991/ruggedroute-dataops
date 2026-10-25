# A brief checks[] entry must never invoke forge-check itself

forge-check plans verify[] ∪ checks[] ∪ DoD and runs each via bash -c with no self-invocation
guard, so a checks[] entry like `python .forge/bin/forge-check <task> <step>` recurses (238
nested processes observed on T-0012 before the builder killed the tree). Dedup is by exact
string within ONE process only. Authoring rule: checks[] lists leaf commands only; forge-check
is the RUNNER, named in prose/bootstrap, never in its own input. Upstream candidates:
plan_commands self-invocation guard + brief_validate flag (forgelib/checks.py).
Seen 2026-10-25, T-0012/01 (architect-authored brief). Cost: one builder NEEDS_CONTEXT round.
