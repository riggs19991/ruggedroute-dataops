---
paths:
  - "**/*"
---
# Forge stack rules — stack unknown
- Stack unknown: every change needs an explicit verify command in the brief. The first task is the queued class-S task "stack discovery" (it gets its id when opened with `/forge-task`); it finds the project's real test commands, and the operator writes them into `verify[]` in `.forge/binding.json` (policy-locked: never edited by a model).
- The verifier does not PASS a criterion that has no check command.
- Run every command from the repository root.
