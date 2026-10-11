# Handoff {{task}} — {{title}}

<!-- Task-level handoff for class M, W and L (design §5.5; .forge/schemas/handoff.json). The four mandatory sections
     come first; write `none` rather than omit one. Keep an optional section only when it carries information.
     Every bullet under "Done, with evidence" names a command and a checks/ record or verdict file.
     Close with: .forge/bin/forge-status close {{task}} --handoff .forge/tasks/{{task}}/handoff.md -->

## Where things stand
{{one paragraph: what is true now}}

## Done, with evidence
- {{claim}} — `{{command}}` exit 0 (.forge/tasks/{{task}}/checks/<file>.json or verdict-NN.md)

## Remaining
none

## Gotchas / do not touch
none

## Goal & scope

## Decisions & rationale

## Failed approaches — do not repeat

## Files touched

## Verification commands + expected output

## Open questions

## Bootstrap

```json
{
  "schema": "forge/handoff/2",
  "task": "{{task}}",
  "step": "task",
  "status": "DONE",
  "files_changed": ["{{path}}"],
  "checks_run": [ { "cmd": "{{command}}", "exit": 0 } ],
  "not_verified": [],
  "failed_approaches": [],
  "next_action": "none",
  "commit": null
}
```
