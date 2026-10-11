# Brief {{task}}/{{step}} — {{title}}

<!-- Template (design §5.4). The first fenced json block is brief-meta (schema forge/brief/2, .forge/schemas/brief.json).
     The fence reads allowed_paths, may_edit_tests, owner_agent, max_tool_calls; the handoff gate reads checks,
     expected_fail_first, tdd, dod, red_ok. The brief must be self-contained: the worker sees nothing else. -->

```json
{
  "schema": "forge/brief/2",
  "task": "{{task}}",
  "step": "{{step}}",
  "owner_agent": "forge-builder",
  "model": "opus",
  "effort": "medium",
  "allowed_paths": ["{{path or glob}}"],
  "may_edit_tests": false,
  "tdd": true,
  "checks": ["{{command}}"],
  "expected_fail_first": ["{{command that fails before the change}}"],
  "dod": ["DoD-1"],
  "risk": "none",
  "red_ok": false,
  "max_tool_calls": 60,
  "bootstrap": "{{binding.bootstrap}}"
}
```

## Goal
{{one paragraph: the outcome, not the steps}}

## Context the worker needs
<!-- Paths, interfaces, invariants from the README design rules, relevant lessons copied in. -->

## Definition of done
<!-- DoD-n criteria verbatim from plan-meta.dod. -->
- DoD-1: {{criterion}} — check: `{{command}}`

## Out of scope / do not touch

## Known failed approaches
<!-- From lessons; `.forge/bin/forge-status step-start {{task}} {{step}} --from failed` appends the last verdict here. -->
none

## Output contract
Your final message is the HANDOFF: these `## ` sections in this order — **Where things stand · Done, with evidence · Remaining · Gotchas / do not touch** (mandatory; write `none` rather than omit) and optionally Goal & scope · Decisions & rationale · Failed approaches — do not repeat · Files touched · Verification commands + expected output · Open questions · Bootstrap — followed by one fenced ```json block with schema forge/handoff/2. Run `.forge/bin/forge-check {{task}} {{step}}` after your last edit (and `--expect-fail` before implementing, since tdd is true). Pre-validate with `.forge/bin/forge-gate --handoff {{task}} {{step}} --from-file <draft>`; a hook refuses your return until the same check passes. Run every command from the repository root.
