---
paths:
  - "**/*"
---
# Forge stack rules — stack unknown
- Stack unknown: every change needs an explicit verify command in the brief; the first task is stack discovery (`T-0001 stack discovery`), which fills `verify[]` in `.forge/binding.json`.
- The verifier does not PASS a criterion that has no check command.
- Run every command from the repository root.
