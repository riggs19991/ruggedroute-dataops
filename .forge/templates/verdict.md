<!-- VERDICT (design §5.6; .forge/schemas/verdict.json). The verifier's final message: these six sections, then one
     fenced json block. Every DoD id from the brief (or plan-meta for inline tasks, step "main") appears exactly once
     with result, cmd and a numeric exit; every cited cmd has a checks/ record from this verifier's session.
     Pre-validate: write the draft to .forge/tasks/{{task}}/drafts/<your agent id>-verdict.md (Write tool; never committed), then
     .forge/bin/forge-gate --verdict {{task}} {{step}} --from-file <that path> --agent <your agent id>
     An inline verdict (step main) is recorded as STATUS task.inline_verdict; close needs it to be PASS for X, and for S
     when tests changed. -->

## Verdict
{{PASS | FAIL | UNKNOWN}} — {{one sentence}}

## Criteria
- DoD-1: {{PASS | FAIL | UNKNOWN}} — `{{command}}` exit {{n}}

## Scope check
{{PASS | FAIL}} — `git diff --name-only {{base}}..{{commit}}` ⊆ allowed_paths; no existing test weakened.

## Blocking findings
none

## Deferred findings
none

## Confidence note
{{what you could not check and what would resolve it}}

```json
{
  "schema": "forge/verdict/2",
  "task": "{{task}}",
  "step": "{{step}}",
  "range": "{{base}}..{{commit}}",
  "verdict": "PASS",
  "criteria": [ { "id": "DoD-1", "result": "PASS", "cmd": "{{command}}", "exit": 0 } ],
  "scope_check": "PASS",
  "ratchet": "PASS",
  "blocking_findings": [],
  "deferred_findings": [],
  "tags": []
}
```
