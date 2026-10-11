---
name: forge-task
description: Start a Forge task from a one-line title: declare the edit set, classify in one script call, then implement inline (class T/S/X) or write/fork the plan (class M/W/L). Use when the user asks for any change to the repository.
argument-hint: "<one-line task title>"
effort: medium
allowed-tools: Bash(.forge/bin/forge-status *), Bash(.forge/bin/forge-check *), Bash(.forge/bin/forge-gate *), Read, Grep, Glob, Agent, Skill
---
Open a Forge task for: $ARGUMENTS

Current state:
```!
"${CLAUDE_PROJECT_DIR}"/.forge/bin/forge-status get summary --lenient || true
```

Do this in order; the scripts refuse illegal states, so follow their messages:
1. If a task is already open, stop and tell the user to finish it or `/forge-close --partial` it first.
2. Decide the edit set yourself (read the code if you must): the existing files you will change and the files you will create. Size and scope come from this declaration, not from a search.
3. One call: `.forge/bin/forge-status open --title "$ARGUMENTS" --class <T|S|M|W|L|X> --risk <none|R> --files <paths> [--creates <paths>] --why "<which signals fired, ≥20 chars>"`. Classes: T ≤2 files one-sentence diff; S ≤3 files ≤2 dirs with tests (or your plan adds them first); M one dependent chain 3-10 files; W one chain wider than that; L ≥3 path-disjoint units; X novel/ambiguous/root-cause. Any protected or risk path (even one you will create) means --risk R. Read `.forge/tasks/<id>/signals.json` afterwards: `importers` and `important_hits` may raise the verifier.
4. Class T: make the change (only the declared files are allowed), run `.forge/bin/forge-check <id> main`, then `/forge-close`.
   Class S: write the inline plan section into `.forge/tasks/<id>/plan.md` from `.forge/templates/plan-inline.md` (mode inline, DoD ids with checks), run `.forge/bin/forge-status plan <id> --from .forge/tasks/<id>/plan.md`, implement, `.forge/bin/forge-check <id> main`; if you added or changed tests, dispatch `Agent(subagent_type: "forge-verifier", model: "sonnet", effort: "medium", prompt: "Verify .forge/tasks/<id>/plan.md DoD against the working tree and the checks; run .forge/bin/forge-check <id> main --ratchet yourself.")` (model opus if STATUS says so); then `/forge-close`.
   Class X: write the short plan section (hypothesis, DoD, rollback) from `plan-inline.md`, `forge-status plan`, then invoke `/forge-investigate <id>`.
   Class M with ≤5 files and ≤2 dirs and no risk: write `plan.md` (plan-meta, Steps, Validation Criteria, Routing, Rollback) and `brief-01.md` from the templates yourself, run `.forge/bin/forge-gate --plan <id>`, then `forge-status plan`, then dispatch the builder named in `next_action` with the Agent tool (`run_in_background: true`).
   Class M (larger), W, L: dispatch `Agent(subagent_type: "forge-planner", model: "fable", effort: "medium" for M | "high" for W and L, prompt: "Plan Forge task <id>.")`; when it returns, `.forge/bin/forge-status plan <id> --from .forge/tasks/<id>/plan.md`; if STATUS now says needs_clarification, ask the user those questions and stop; otherwise dispatch per `next_action`.
Dispatching a worker records the step automatically; you do not call step-start. The Stop gate will insist that STATUS reflects anything else you changed.
