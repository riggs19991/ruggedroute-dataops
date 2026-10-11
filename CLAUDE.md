<!-- forge:begin (managed by .forge/bin — do not edit between markers) -->
## The Forge
This repo runs the Forge (v1.0.0). `.forge/STATUS.json` is the single source of truth for where work stands; it is injected at every session start and written only by `.forge/bin/forge-status`.
Daily loop: `/forge-task <title>` → `/forge-next` → `/forge-close`. Health: `/forge-doctor`. Everything else: read `.forge/FORGE.md` (≤120 lines) before guessing. Scripts live at `.forge/bin/` and run from the repository root.
Hooks enforce plan-first, scope fences, tool budgets, evidence-backed handoffs, the status write and the policy-file lock; if a tool call is refused, the reason names the script to run.
When compacting, preserve: decisions and why; approaches tried and set aside; exactly where things stand; anything open or promised; exact commands, paths and numbers.
<!-- forge:end -->
