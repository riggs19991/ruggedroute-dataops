---
name: forge-doctor
description: Check that the Forge is alive in this session: hooks fire, python/CLI versions are adequate, settings carry every Forge hook, STATUS and binding validate, FORGE.md pointers resolve, VERSION matches. Use when gates seem silent or after an upgrade.
effort: low
allowed-tools: Bash(.forge/bin/forge-doctor *), Bash(.forge/bin/forge-status *), Read
---
Doctor report (static checks; never fails the injection):
```!
"${CLAUDE_PROJECT_DIR}"/.forge/bin/forge-doctor --report --no-probes || true
```

Now run the live probe as a normal command and paste its result: `.forge/bin/forge-doctor --probe-hooks` (it runs one `claude -p` turn with hook events and checks hooks-alive). Explain any red line in one sentence with the fix from `.forge/RUNBOOK.md` §Troubleshooting, apply fixes that are safe (chmod, .gitignore, missing runtime dir), and never disable a gate yourself — `--disable-gate <name>` is for the operator and is journaled. If hooks did not fire, say so first — nothing else in the Forge is trustworthy until they do.
