---
name: forge-investigate
description: Run the open class-X Forge task inline: investigate and fix within the declared scope at medium effort, then dispatch the Fable verifier. Internal; invoked by forge-task or forge-next for class X.
user-invocable: false
effort: medium
argument-hint: "<task-id>"
allowed-tools: Bash(.forge/bin/forge-status *), Bash(.forge/bin/forge-check *), Bash(.forge/bin/forge-gate *), Read, Edit, Write, Grep, Glob, Agent
---
Task $ARGUMENTS is class X and its plan section exists. You are the one who codes this: investigate, form and test the hypothesis in `plan.md`, fix within the declared scope (`.forge/bin/forge-status scope add <path> --why "…"` if the root cause lives elsewhere; the fence refuses undeclared paths), run `.forge/bin/forge-check $ARGUMENTS main` after your last edit, record claims with `.forge/bin/forge-status evidence $ARGUMENTS --claim "…" --from-check <file>`, then dispatch `Agent(subagent_type: "forge-verifier", model: "fable", effort: "medium", prompt: "Verify .forge/tasks/$ARGUMENTS/plan.md DoD against the working tree; run .forge/bin/forge-check $ARGUMENTS main --ratchet yourself.")`. If the investigation changes the shape of the work, update the plan section first. Do not end the turn with a hypothesis you have not tested.
