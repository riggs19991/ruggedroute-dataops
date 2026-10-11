# Handoff {{task}} — {{title}}

<!-- Short task-level handoff for class S and X (design §3, §5.5): three sections plus the json block.
     Evidence only from checks/ records and verdicts you have read.
     Close with: .forge/bin/forge-status close {{task}} --handoff .forge/tasks/{{task}}/handoff.md -->

## Where things stand
{{one paragraph: what is true now}}

## Done, with evidence
- {{claim}} — `{{command}}` exit 0 (.forge/tasks/{{task}}/checks/<file>.json)

## Remaining
none

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
