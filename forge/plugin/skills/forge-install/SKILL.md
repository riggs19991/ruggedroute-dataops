---
name: forge-install
description: Install or upgrade the Forge (plain project layout) into the current repository by running the plugin's bundled install.sh. Operator-invoked only.
disable-model-invocation: true
argument-hint: "[--upgrade] [--dry-run] [--effort low|medium] [--no-model] [--with-bench] [--force] [--force-settings]"
---
# Install the Forge into this repository

Run exactly this from the repository root, passing the operator's arguments through unchanged:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/install.sh" --target "${CLAUDE_PROJECT_DIR}" $ARGUMENTS
```

Then report the installer's summary lines and the `forge-doctor` report verbatim, including every WARN and FAIL line.
Do not edit any file yourself. If the installer refuses (exit 3), quote its one-line reason and stop.

After a successful install, tell the operator to:
1. commit the new and changed files (`.forge/`, `.claude/`, `CLAUDE.md`, `.gitignore`);
2. start a new session, because project hooks, agents and skills load at session start;
3. keep this plugin for other repositories: inside a repository with `.forge/VERSION` its hooks stay silent (`--plugin`).
