# Handoff T-0011 — Forge 1.0.1: binding.agent_paths for non-Forge agents + Git Bash on Windows (ADR 0002 upstream)

## Where things stand
Forge 1.0.1 is implemented and committed on branch forge-1.0.1-ci (implement commit ca30ded, on top of 0e12c5e). The source tree
under forge/ carries the agent_paths fences in hooks.py, the `_bash()` resolution in common.py, migration 0001, the version bump
to 1.0.1 everywhere, the docs, the regenerated forge/plugin and the new tests. forge-check passed 7/7 with 2 binding entries skipped
by their path filters (.forge/tasks/T-0011/checks/main-1792805131-main.json, ok=true) and the Fable verifier returned PASS on step main (.forge/tasks/T-0011/verdict-main.json). This repository's own installed Forge
under .forge/ is still 1.0.0 and the consumer installs are not yet upgraded.

## Done, with evidence
- DoD-1/DoD-2: agent_paths Edit/Write and Bash fences (10 AgentPaths tests) — `python3 -m unittest discover -s forge/tests -p test_hooks.py -k AgentPaths` exit 0 (.forge/tasks/T-0011/checks/main-1792805131-main.json)
- DoD-3: `_bash()` resolution order on win32, bare bash elsewhere — `python3 -m unittest discover -s forge/tests -p test_common.py -k bash` exit 0 (.forge/tasks/T-0011/checks/main-1792805131-main.json)
- DoD-4: migration 0001 adds `agent_paths: []` once, idempotently, recorded in the manifest — `python3 -m unittest discover -s forge/tests -p test_installer.py -k migration` exit 0 (.forge/tasks/T-0011/checks/main-1792805131-main.json)
- DoD-5: whole Forge suite green on Linux (410 tests) and forge/plugin in sync — `python3 -m unittest discover -s forge/tests && python3 forge/tools/make_plugin.py --check` exit 0 (.forge/tasks/T-0011/checks/main-1792805131-main.json)
- DoD-6: version 1.0.1 in forge/VERSION, payload VERSION, forgelib.common and CHANGELOG — `grep -qx 1.0.1 forge/VERSION && grep -qx 1.0.1 forge/payload/.forge/VERSION && grep -q 'FORGE_VERSION = "1.0.1"' forge/payload/.forge/bin/forgelib/common.py && grep -q '^## 1.0.1' forge/CHANGELOG.md` exit 0 (.forge/tasks/T-0011/checks/main-1792805131-main.json)
- DoD-7: agent_paths named in HOOKS.md, GATES.md, SCHEMAS.md, README.md, MODULE-API.md and the binding schema — `for f in forge/payload/.forge/HOOKS.md forge/payload/.forge/GATES.md forge/payload/.forge/SCHEMAS.md forge/README.md forge/docs/MODULE-API.md forge/payload/.forge/schemas/binding.json; do grep -q agent_paths "$f" || exit 1; done` exit 0 (.forge/tasks/T-0011/checks/main-1792805131-main.json)
- Binding lib-unit entry still green (68 tests) — `cd lib && python3 -m unittest -v` exit 0 (.forge/tasks/T-0011/checks/main-1792805131-main.json)
- Independent verification: PASS on step main — `.forge/bin/forge-check T-0011 main --ratchet` run by the forge-verifier (.forge/tasks/T-0011/verdict-main.json)

## Remaining
- Upgrade this repository's own installed Forge (.forge/ is 1.0.0, source tree is 1.0.1): `bash forge/install.sh --upgrade`, as a separate task.
- Upgrade the RuggedRoute install (`bash forge/install.sh --target <RuggedRoute> --upgrade`) and hand-edit its binding.json agent_paths.
- Fast-forward main to this branch and push it.

```json
{
  "schema": "forge/handoff/2",
  "task": "T-0011",
  "step": "task",
  "status": "DONE",
  "files_changed": [
    "forge/CHANGELOG.md",
    "forge/README.md",
    "forge/VERSION",
    "forge/bindings/millwright-kb.json",
    "forge/bindings/ruggedroute-android.json",
    "forge/bindings/ruggedroute-dataops.json",
    "forge/docs/MODULE-API.md",
    "forge/docs/UPGRADING.md",
    "forge/installer.py",
    "forge/migrations/0001-binding-agent-paths.py",
    "forge/migrations/README.md",
    "forge/payload/.forge/GATES.md",
    "forge/payload/.forge/HOOKS.md",
    "forge/payload/.forge/RUNBOOK.md",
    "forge/payload/.forge/SCHEMAS.md",
    "forge/payload/.forge/VERSION",
    "forge/payload/.forge/bin/forge-doctor",
    "forge/payload/.forge/bin/forgelib/__init__.py",
    "forge/payload/.forge/bin/forgelib/common.py",
    "forge/payload/.forge/bin/forgelib/hooks.py",
    "forge/payload/.forge/bin/forgelib/status.py",
    "forge/payload/.forge/schemas/binding.json",
    "forge/payload/.forge/templates/STATUS.json",
    "forge/payload/.forge/templates/binding.json",
    "forge/plugin/.claude-plugin/plugin.json",
    "forge/plugin/bin/forge-doctor",
    "forge/plugin/bin/forgelib/__init__.py",
    "forge/plugin/bin/forgelib/common.py",
    "forge/plugin/bin/forgelib/hooks.py",
    "forge/plugin/bin/forgelib/status.py",
    "forge/plugin/installer.py",
    "forge/plugin/migrations/0001-binding-agent-paths.py",
    "forge/plugin/migrations/README.md",
    "forge/plugin/payload/.forge/GATES.md",
    "forge/plugin/payload/.forge/HOOKS.md",
    "forge/plugin/payload/.forge/RUNBOOK.md",
    "forge/plugin/payload/.forge/SCHEMAS.md",
    "forge/plugin/payload/.forge/VERSION",
    "forge/plugin/payload/.forge/bin/forge-doctor",
    "forge/plugin/payload/.forge/bin/forgelib/__init__.py",
    "forge/plugin/payload/.forge/bin/forgelib/common.py",
    "forge/plugin/payload/.forge/bin/forgelib/hooks.py",
    "forge/plugin/payload/.forge/bin/forgelib/status.py",
    "forge/plugin/payload/.forge/schemas/binding.json",
    "forge/plugin/payload/.forge/templates/STATUS.json",
    "forge/plugin/payload/.forge/templates/binding.json",
    "forge/tests/run_linux.sh",
    "forge/tests/test_common.py",
    "forge/tests/test_hooks.py",
    "forge/tests/test_installer.py",
    "forge/tests/test_status.py",
    "forge/tools/make_plugin.py"
  ],
  "checks_run": [
    {
      "cmd": "cd lib && python3 -m unittest -v",
      "exit": 0
    },
    {
      "cmd": "python3 -m unittest discover -s forge/tests -p test_hooks.py -k AgentPaths",
      "exit": 0
    },
    {
      "cmd": "python3 -m unittest discover -s forge/tests -p test_common.py -k bash",
      "exit": 0
    },
    {
      "cmd": "python3 -m unittest discover -s forge/tests -p test_installer.py -k migration",
      "exit": 0
    },
    {
      "cmd": "python3 -m unittest discover -s forge/tests && python3 forge/tools/make_plugin.py --check",
      "exit": 0
    },
    {
      "cmd": "grep -qx 1.0.1 forge/VERSION && grep -qx 1.0.1 forge/payload/.forge/VERSION && grep -q 'FORGE_VERSION = \"1.0.1\"' forge/payload/.forge/bin/forgelib/common.py && grep -q '^## 1.0.1' forge/CHANGELOG.md",
      "exit": 0
    },
    {
      "cmd": "for f in forge/payload/.forge/HOOKS.md forge/payload/.forge/GATES.md forge/payload/.forge/SCHEMAS.md forge/README.md forge/docs/MODULE-API.md forge/payload/.forge/schemas/binding.json; do grep -q agent_paths \"$f\" || exit 1; done",
      "exit": 0
    }
  ],
  "not_verified": [
    "this repository's own installed Forge is still 1.0.0: upgrade it in a separate task",
    "the RuggedRoute upgrade (bash forge/install.sh --target <RuggedRoute> --upgrade) and the hand edit of its binding.json agent_paths"
  ],
  "failed_approaches": [],
  "next_action": "fast-forward main to this branch and push it; then upgrade the consumer installs",
  "commit": null
}
```
