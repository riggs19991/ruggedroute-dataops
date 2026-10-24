# Inline Plan: T-0011 — Forge 1.0.1: binding.agent_paths for non-Forge agents + Git Bash on Windows (ADR 0002 upstream)

```json
{
  "schema": "forge/plan/2",
  "task": "T-0011",
  "class": "X",
  "risk": "none",
  "chain": false,
  "routing": {
    "mode": "inline",
    "builder": null,
    "verifier": {
      "agent": "forge-verifier",
      "model": "fable",
      "effort": "medium"
    },
    "justification": "class X: a root-cause change to the hook fences and the check runner, implemented inline by the architect; the Fable verifier is mandatory and close needs its PASS on step main"
  },
  "steps": [],
  "dod": [
    {
      "id": "DoD-1",
      "criterion": "WHEN a non-Forge subagent edits a path matching binding.agent_paths with no task open THE SYSTEM SHALL allow the Edit/Write, deny paths outside the globs, and let the policy lock and protected_paths win",
      "check": "python3 -m unittest discover -s forge/tests -p test_hooks.py -k AgentPaths"
    },
    {
      "id": "DoD-2",
      "criterion": "WHEN such an agent runs a heredoc, redirect, mkdir or rm whose targets all lie under binding.agent_paths THE SYSTEM SHALL allow it while git push, binding irreversible patterns and writes outside the globs stay denied",
      "check": "python3 -m unittest discover -s forge/tests -p test_hooks.py -k AgentPaths"
    },
    {
      "id": "DoD-3",
      "criterion": "WHEN forgelib.common.run() spawns a shell on win32 THE SYSTEM SHALL prefer $FORGE_BASH, then Git Bash under Program Files, then a bare bash, and bash everywhere else",
      "check": "python3 -m unittest discover -s forge/tests -p test_common.py -k bash"
    },
    {
      "id": "DoD-4",
      "criterion": "WHEN installer.py --upgrade runs against a binding.json without agent_paths THE SYSTEM SHALL add the key with [] once, keep every other byte, stay idempotent and record migration 0001 in install-manifest.json",
      "check": "python3 -m unittest discover -s forge/tests -p test_installer.py -k migration"
    },
    {
      "id": "DoD-5",
      "criterion": "WHEN the release is built THE SYSTEM SHALL pass the whole Forge suite on Linux and ship forge/plugin exactly as tools/make_plugin.py generates it",
      "check": "python3 -m unittest discover -s forge/tests && python3 forge/tools/make_plugin.py --check"
    },
    {
      "id": "DoD-6",
      "criterion": "WHEN the version is read THE SYSTEM SHALL report 1.0.1 in forge/VERSION, the payload VERSION, forgelib.common and the CHANGELOG",
      "check": "grep -qx 1.0.1 forge/VERSION && grep -qx 1.0.1 forge/payload/.forge/VERSION && grep -q 'FORGE_VERSION = \"1.0.1\"' forge/payload/.forge/bin/forgelib/common.py && grep -q '^## 1.0.1' forge/CHANGELOG.md"
    },
    {
      "id": "DoD-7",
      "criterion": "WHEN an operator reads the shipped docs THE SYSTEM SHALL find agent_paths in HOOKS.md, GATES.md, SCHEMAS.md, README.md, MODULE-API.md and the binding schema",
      "check": "for f in forge/payload/.forge/HOOKS.md forge/payload/.forge/GATES.md forge/payload/.forge/SCHEMAS.md forge/README.md forge/docs/MODULE-API.md forge/payload/.forge/schemas/binding.json; do grep -q agent_paths \"$f\" || exit 1; done"
    }
  ],
  "rollback": "git revert <close sha>; no schema_version changes, and migration 0001 only adds agent_paths: [] to a consumer binding, which stays harmless after a revert",
  "test_baseline": {
    "files": 13,
    "tests": 129,
    "recorded_at": "2026-10-19T15:58:59Z"
  },
  "needs_clarification": [],
  "allowed_paths": [
    "forge/payload/.forge/bin/forgelib/hooks.py",
    "forge/payload/.forge/bin/forgelib/common.py",
    "forge/payload/.forge/bin/forgelib/status.py",
    "forge/payload/.forge/bin/forgelib/gates.py",
    "forge/payload/.forge/bin/forgelib/__init__.py",
    "forge/payload/.forge/bin/forge-doctor",
    "forge/payload/.forge/schemas/binding.json",
    "forge/payload/.forge/templates/binding.json",
    "forge/payload/.forge/templates/STATUS.json",
    "forge/payload/.forge/HOOKS.md",
    "forge/payload/.forge/GATES.md",
    "forge/payload/.forge/SCHEMAS.md",
    "forge/payload/.forge/RUNBOOK.md",
    "forge/payload/.forge/VERSION",
    "forge/VERSION",
    "forge/CHANGELOG.md",
    "forge/README.md",
    "forge/docs/MODULE-API.md",
    "forge/docs/UPGRADING.md",
    "forge/docs/BUILD-LOG.md",
    "forge/migrations/README.md",
    "forge/migrations/0001-binding-agent-paths.py",
    "forge/bindings/ruggedroute-android.json",
    "forge/bindings/ruggedroute-dataops.json",
    "forge/bindings/millwright-kb.json",
    "forge/tests/helpers.py",
    "forge/tests/test_hooks.py",
    "forge/tests/test_common.py",
    "forge/tests/test_installer.py",
    "forge/tests/test_status.py",
    "forge/tests/test_gates.py",
    "forge/tests/run_linux.sh",
    "forge/tools/make_plugin.py",
    "forge/installer.py",
    "forge/plugin/**"
  ]
}
```

## Hypothesis / Objective
Two root causes, one release. (1) `_pre_edit` sends every unknown role to the main-session rules, and `_pre_bash` sends
every unknown role through `looks_mutating` with the same `no-task` fence, so a consumer's own agent (RuggedRoute's
read-only QA tester, which writes `qa/reports/**` and `qa/scripts/**`) cannot write anything from a fresh session. A
project-owned binding key `agent_paths` (repo-relative globs, default `[]`) lets the two fences allow writes there for
any subagent whose `agent_type` is not a `forge-*` role, in every task state; the policy lock, the outside-repository
check and `protected_paths` still win; Forge roles and the main session are untouched. (2) `common.run()` spawns a bare
`bash`, which on Windows is the WSL stub in System32: RuggedRoute's ADR 0002 operator patch (`_bash()`: `$FORGE_BASH`, then
Git Bash under Program Files, else `bash`) ships upstream so an upgrade no longer reverts it. Tested by the Forge suite run natively on Linux (CI, or a cloud session; a Windows checkout cannot exec the shebang
scripts the tests spawn, so `forge/tests/run_linux.sh` runs them in a container there), plus grep checks on the version and the docs.

## Validation Criteria
- DoD-1: agent_paths Edit/Write fence (allow inside, deny outside, policy lock and protected_paths win) — check: `python3 -m unittest discover -s forge/tests -p test_hooks.py -k AgentPaths`
- DoD-2: agent_paths Bash fence (heredoc/redirect/mkdir/rm inside allowed; git push, irreversible patterns, outside denied) — check: the same command
- DoD-3: `_bash()` resolution order on win32, `bash` elsewhere — check: `python3 -m unittest discover -s forge/tests -p test_common.py -k bash`
- DoD-4: migration 0001 adds `agent_paths: []` once, idempotently, recorded in the manifest — check: `python3 -m unittest discover -s forge/tests -p test_installer.py -k migration`
- DoD-5: whole suite green on Linux; plugin/ in sync — check: `python3 -m unittest discover -s forge/tests && python3 forge/tools/make_plugin.py --check`
- DoD-6: version 1.0.1 everywhere — check: the grep chain in plan-meta
- DoD-7: docs name agent_paths — check: the grep loop in plan-meta

## Rollback
`git revert <close sha>` on main. No schema_version changes. Migration 0001 is additive (`agent_paths: []`) and idempotent;
a consumer that upgraded keeps a harmless extra key if the release is reverted.
