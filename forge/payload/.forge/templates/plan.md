# Execution Plan: {{task}} — {{title}}

<!-- Template for class M, W and L (design §5.3). The first fenced json block is plan-meta (schema forge/plan/2,
     .forge/schemas/plan.json); scripts read only that block and the level-2 headings. Replace every {{placeholder}}.
     Mandatory headings: M → Steps, Validation Criteria, Routing, Rollback.
                         W and L → all twelve headings below.
     test_baseline: leave the template value (recorded_at 1970) and `forge-status plan` records the real baseline at import
     (or run .forge/bin/forge-check {{task}} plan --baseline and copy its numbers in).
     Validate with: .forge/bin/forge-gate --plan {{task}}   then import with: .forge/bin/forge-status plan {{task}} --from .forge/tasks/{{task}}/plan.md -->

```json
{
  "schema": "forge/plan/2",
  "task": "{{task}}",
  "class": "M",
  "risk": "none",
  "chain": false,
  "routing": {
    "mode": "single",
    "builder": { "agent": "forge-builder", "model": "opus", "effort": "medium" },
    "verifier": { "agent": "forge-verifier", "model": "opus", "effort": "medium" },
    "justification": "{{which signals fired: files, dirs, tests_present, importers, important_hits, risk_hits, chain}}"
  },
  "steps": [
    { "id": "01", "title": "{{step title}}", "brief": "brief-01.md", "agent": "forge-builder", "model": "opus", "effort": "medium",
      "mechanical": false, "red_ok_until": null, "max_tool_calls": 60 }
  ],
  "dod": [
    { "id": "DoD-1", "criterion": "WHEN {{trigger}} THE SYSTEM SHALL {{observable result}}", "check": "{{command that exits 0 when the criterion holds}}" },
    { "id": "DoD-2", "criterion": "WHEN {{an external run happens}} THE SYSTEM SHALL {{result}}", "check": "external",
      "external": { "what": "{{what a human observes}}", "how": "{{exact command the human runs}}" } }
  ],
  "rollback": "{{git revert <step commit>; plus any external state to restore — a concrete command for risk R}}",
  "test_baseline": { "files": 0, "tests": 0, "recorded_at": "1970-01-01T00:00:00Z" },
  "needs_clarification": []
}
```

## Steps
<!-- One `### Step NN — title` per steps[] entry, each with File / Action / Details / Verify. M and W: exactly one step. L: ≥3 steps with pairwise-disjoint allowed_paths (read from each brief). -->
### Step 01 — {{step title}}
- File: {{paths}}
- Action: {{create | modify}}
- Details: {{what changes and the invariants that must hold}}
- Verify: `.forge/bin/forge-check {{task}} 01`

## Validation Criteria
<!-- The DoD-n list in prose, same ids as plan-meta.dod. -->
- DoD-1: {{criterion}} — check: `{{command}}`

## Routing
<!-- Which signals fired and why this builder/verifier tier; cite .forge/tasks/{{task}}/signals.json. -->

## Rollback
<!-- How to undo the change; for risk R a concrete command (e.g. git revert <sha>). -->

## Objective

## Current State
<!-- Include signals.recent_cochanges files that usually change together but were not declared. -->

## Target State

## Tech Stack Context

## File Manifest

## Dependency Order

## Anti-Patterns — DO NOT

## Escalation Points
