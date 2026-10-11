# Brief {{task}}/{{step}} — {{title}}

<!-- Template (design §5.4). The first fenced json block is brief-meta (schema forge/brief/2, .forge/schemas/brief.json).
     The fence reads allowed_paths, may_edit_tests, owner_agent, max_tool_calls; the handoff gate reads checks,
     expected_fail_first, tdd, dod, red_ok. The brief must be self-contained: the worker sees nothing else.
     may_edit_tests (default true here): the fence refuses every edit to an EXISTING file matching binding.test_globs
     unless this is true, so keep it true whenever a DoD adds tests to an existing test module (lib/test_*.py style).
     Set it false only when every new test goes into a NEW file that allowed_paths covers; deleted or weakened tests
     are caught by the ratchet and the verifier's test-weakened tag either way.
     tdd: true means the worker writes the failing test first and records it with `forge-check <task> <step>
     --expect-fail`, then implements and records green. Every expected_fail_first command must also be in checks
     (forge-check runs checks only; the plan gate refuses otherwise). On a retry an earlier red record by any agent
     counts, so a worker never has to break a test to satisfy the rule. Set tdd false (and expected_fail_first [])
     only when no test can fail first: a pure refactor, a config or data edit, a mechanical rename. -->

```json
{
  "schema": "forge/brief/2",
  "task": "{{task}}",
  "step": "{{step}}",
  "owner_agent": "forge-builder",
  "model": "opus",
  "effort": "medium",
  "allowed_paths": ["{{path or glob}}"],
  "may_edit_tests": true,
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
Your final message is the HANDOFF: these `## ` sections in this order — **Where things stand · Done, with evidence · Remaining · Gotchas / do not touch** (mandatory; write `none` rather than omit) and optionally Goal & scope · Decisions & rationale · Failed approaches — do not repeat · Files touched · Verification commands + expected output · Open questions · Bootstrap — followed by one fenced ```json block with schema forge/handoff/2. Run `.forge/bin/forge-check {{task}} {{step}}` after your last edit (and `--expect-fail` before implementing, since tdd is true). Pre-validate: write the draft with the Write tool to `.forge/tasks/{{task}}/drafts/<your agent id>-handoff.md` (the sanctioned draft path; drafts are never committed) and run `.forge/bin/forge-gate --handoff {{task}} {{step}} --from-file <that path> --agent <your agent id>`; a hook refuses your return until the same check passes. Run every command from the repository root.
