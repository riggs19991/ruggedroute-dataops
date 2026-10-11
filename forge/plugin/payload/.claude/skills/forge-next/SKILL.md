---
name: forge-next
description: Resume the open Forge task from STATUS and execute its next_action (dispatch, verify, adjudicate, attest or close). Use at the start of a session or after /clear when nothing auto-resumed.
effort: low
allowed-tools: Bash(.forge/bin/forge-status *), Bash(.forge/bin/forge-check *), Read, Grep, Glob, Agent, Skill
---
Resume from STATUS:
```!
"${CLAUDE_PROJECT_DIR}"/.forge/bin/forge-status get resume --lenient || true
```

Execute `next_action` exactly, nothing more. If a step shows started_by from another session and no report, it was interrupted: `.forge/bin/forge-status recover <id> <step>` then restart it with `step-start <id> <step> --from clean` and a dispatch. If the task is awaiting_external, print the commands the human must run and stop. If STATUS says idle and the queue is non-empty, start the first queued task with `/forge-task`; if idle and empty, say so and stop. Dispatch workers with the Agent tool using exactly the agent, model and effort STATUS records for the step (the spawn guard refuses anything else); `run_in_background: true`. Class X: invoke `/forge-investigate <id>`.
