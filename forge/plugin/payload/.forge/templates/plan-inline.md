# Inline Plan: {{task}} — {{title}}

<!-- Template for class S and X (design §3 small/extreme paths, §5.3). The architect implements inline, so mode is
     "inline" and steps is []. allowed_paths is the declared edit set (STATUS task.scope).
     Mandatory headings: Validation Criteria, Rollback. Replace every {{placeholder}}.
     Class X: set "class": "X" and the verifier to fable/medium (mandatory; close needs its PASS on step main).
     Class S: sonnet/medium (opus when importers >= 5), dispatched only if tests are added or changed; then close needs its PASS.
     test_baseline: leave the template value and `forge-status plan` records the real baseline at import.
     Validate with: .forge/bin/forge-gate --plan {{task}}   then import with: .forge/bin/forge-status plan {{task}} --from .forge/tasks/{{task}}/plan.md -->

```json
{
  "schema": "forge/plan/2",
  "task": "{{task}}",
  "class": "S",
  "risk": "none",
  "chain": false,
  "routing": {
    "mode": "inline",
    "builder": null,
    "verifier": { "agent": "forge-verifier", "model": "sonnet", "effort": "medium" },
    "justification": "{{S: tests exist or DoD-1 adds them; verifier only if tests change (opus when importers >= 5) | X: Fable verifier, mandatory}}"
  },
  "steps": [],
  "dod": [
    { "id": "DoD-1", "criterion": "WHEN {{trigger}} THE SYSTEM SHALL {{observable result}}", "check": "{{command that exits 0 when the criterion holds}}" }
  ],
  "rollback": "{{git revert <sha> — a concrete command for risk R}}",
  "test_baseline": { "files": 0, "tests": 0, "recorded_at": "1970-01-01T00:00:00Z" },
  "needs_clarification": [],
  "allowed_paths": ["{{declared path}}"]
}
```

## Hypothesis / Objective
<!-- S: the change in one or two sentences. X: the hypothesis to test first and how it will be tested. -->

## Validation Criteria
- DoD-1: {{criterion}} — check: `{{command}}`

## Rollback
<!-- How to undo the change; for risk R a concrete command. -->
