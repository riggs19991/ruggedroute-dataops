---
name: forge-gc
description: Documentation garbage collection: lessons dedupe, doc drift audit, measured-ledger rollup into COST-REPORT.md, archive of old tasks, verifier-memory lint, pointer check. Use every ~10 closed tasks or when docs feel stale.
effort: low
allowed-tools: Agent, Read
---
Dispatch `Agent(subagent_type: "forge-librarian", prompt: "Run the Forge garbage-collection pass described in your role. Report what changed, what you removed and why, the pointer-check and digest-size results, and your threshold proposals.")` and relay its report. Do not edit anything yourself.
