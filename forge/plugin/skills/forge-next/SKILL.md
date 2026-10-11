---
name: forge-next
description: Resume the open Forge task from STATUS and execute its next_action (dispatch, verify, adjudicate, attest or close). Use at the start of a session or after /clear when nothing auto-resumed.
effort: low
allowed-tools: Bash(.forge/bin/forge-status *), Bash(.forge/bin/forge-check *), Read, Grep, Glob, Agent, Skill
---
Resume from STATUS:
```!
.forge/bin/forge-status get resume --lenient
```

Execute `next_action` exactly, nothing more. If a step shows started_by from another session and no report, it was interrupted: run `.forge/bin/forge-status recover <id> <step>` (it saves the step's tree to `.forge/incidents/`, restores the step's paths to its base and sets it `pending`), then dispatch the worker its `next_action` names — the spawn guard runs `step-start` itself (`step-start <id> <step> --from clean` first is accepted but optional). If a step is `blocked` (its worker returned NEEDS_CONTEXT or BLOCKED), read its report, then `step-start <id> <step> --from failed` (keep the tree) or `--from clean` and dispatch a fresh worker with the missing context in the prompt, or follow the other exits `next_action` names. If the task is awaiting_external, print the commands the human must run and stop. If STATUS says idle and the queue is non-empty, start the first queued task with `/forge-task`; if idle and empty, say so and stop. Dispatch workers with the Agent tool using exactly the agent, model and effort STATUS records for the step (the spawn guard refuses anything else); `run_in_background: true`. Class X: invoke `/forge-investigate <id>`.
