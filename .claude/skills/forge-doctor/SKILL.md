---
name: forge-doctor
description: "Check that the Forge is alive in this session: hooks fire, python/CLI versions are adequate, settings carry every Forge hook, STATUS and binding validate, FORGE.md pointers resolve, VERSION matches. Use when gates seem silent or after an upgrade."
effort: low
allowed-tools: Bash(.forge/bin/forge-doctor *), Bash(.forge/bin/forge-status *), Bash(mkdir -p .forge/.runtime), Read, Edit(/.gitignore)
---
Doctor report (static checks; never fails the injection):
```!
.forge/bin/forge-doctor --report --no-probes
```

Now run the live probe as a normal command and paste its result: `.forge/bin/forge-doctor --probe-hooks` (it runs one `claude -p` turn with hook events and checks hooks-alive). Explain any red line in one sentence with the fix from `.forge/RUNBOOK.md` §12 Troubleshooting (rows keyed by the line name). Two fixes you may apply yourself: a missing runtime dir (`mkdir -p .forge/.runtime`) and missing `.gitignore` lines (Edit `.gitignore`: add `.forge/.runtime/` and `.forge/incidents/`). Every other fix you print for the operator to run, including `chmod +x .forge/bin/*` for a red `bin` line (the main-session fence treats chmod as a source change and refuses it outside a task), and never disable a gate yourself — `--disable-gate <name>` is for the operator and is journaled. If hooks did not fire, say so first — nothing else in the Forge is trustworthy until they do.
