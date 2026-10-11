---
name: forge-gc
description: "Documentation garbage collection: lessons dedupe, doc drift audit, measured-ledger rollup into COST-REPORT.md, archive of old tasks, verifier-memory lint, pointer check. Use every ~10 closed tasks or when docs feel stale."
effort: low
allowed-tools: Agent, Read, Bash(.forge/bin/forge-doctor *)
---
Dispatch `Agent(subagent_type: "forge-librarian", prompt: "Run the Forge garbage-collection pass described in your role. Report what changed, what you removed and why, the pointer-check and digest-size results, and your threshold proposals.")` and relay its report. Then run `.forge/bin/forge-doctor --quick --pointers` yourself (subagents may not run the doctor) and add its `pointers` line. Archive moves and `binding.routing` flips are proposals for the operator; do not edit or move anything yourself.
