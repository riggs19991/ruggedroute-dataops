#!/usr/bin/env python3
"""make_plugin.py — generate forge/plugin/ (the secondary, user-level plugin form) from the payload (design §8.1, §13.5).

Usage: python3 forge/tools/make_plugin.py [--check]

Generated (plugin/ is never edited by hand; CI runs --check):
  .claude-plugin/plugin.json   version from forge/VERSION
  agents/, skills/             byte-identical copies of payload/dot-claude/agents and payload/dot-claude/skills
  skills/forge-install/        operator-only skill (disable-model-invocation: true) that runs install.sh here
  bin/                         copy of payload/.forge/bin (forge-hook and friends)
  hooks/hooks.json             settings.forge.json's hook map; every command "${CLAUDE_PLUGIN_ROOT}"/bin/forge-hook --plugin
  install.sh, installer.py, payload/, migrations/   so the forge-install skill works from the plugin cache alone
payload/dot-claude/ installs to <target>/.claude/ (installer.py); it is not named .claude so Claude Code never
auto-discovers the payload's rules and agents in a session working on the Forge source.
Exit codes: 0 written / up to date · 1 --check found differences · 2 the payload is incomplete.
"""
import argparse
import json
import os
import stat
import sys
from typing import Dict, List, Tuple

FORGE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAYLOAD = os.path.join(FORGE, "payload")
PAYLOAD_CLAUDE = os.path.join(PAYLOAD, "dot-claude")   # installs to <target>/.claude/
PLUGIN = os.path.join(FORGE, "plugin")
HOMEPAGE = "https://github.com/riggs19991/ruggedroute-dataops"
PLUGIN_HOOK = '"${CLAUDE_PLUGIN_ROOT}"/bin/forge-hook'
SKIP_DIRS = ("__pycache__", ".git")
SKIP_SUFFIXES = (".pyc", ".pyo")

FORGE_INSTALL_SKILL = """---
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
"""

Files = Dict[str, Tuple[bytes, int]]   # rel path -> (content, mode)


def read(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def mode_of(path: str) -> int:
    return 0o755 if os.stat(path).st_mode & stat.S_IXUSR else 0o644


def copy_tree(src_root: str, dest_prefix: str, files: Files) -> None:
    """Add every file under src_root (minus caches) at dest_prefix/<relative path>, keeping the exec bit."""
    for dirpath, dirnames, filenames in os.walk(src_root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.endswith(SKIP_SUFFIXES) or name == ".DS_Store":
                continue
            src = os.path.join(dirpath, name)
            rel = os.path.relpath(src, src_root).replace(os.sep, "/")
            files[f"{dest_prefix}/{rel}" if dest_prefix else rel] = (read(src), mode_of(src))


def plugin_hooks(fragment: Dict) -> Dict:
    """The fragment's hook map with every Forge command pointed at the plugin's forge-hook --plugin."""
    out: Dict = {}
    for event, groups in fragment.get("hooks", {}).items():
        new_groups = []
        for group in groups:
            g = dict(group)
            handlers = []
            for h in group.get("hooks", []):
                h = dict(h)
                flags = " --role" if "--role" in str(h.get("command", "")) else ""
                h["command"] = f"{PLUGIN_HOOK}{flags} --plugin"
                handlers.append(h)
            g["hooks"] = handlers
            new_groups.append(g)
        out[event] = new_groups
    return {"hooks": out}


def dumps(obj: Dict) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def expected_files() -> Files:
    """Every file plugin/ must contain, with its bytes and mode."""
    version = read(os.path.join(FORGE, "VERSION")).decode("utf-8").strip()
    fragment_path = os.path.join(PAYLOAD_CLAUDE, "settings.forge.json")
    for need in (fragment_path, os.path.join(PAYLOAD_CLAUDE, "agents"), os.path.join(PAYLOAD_CLAUDE, "skills"),
                 os.path.join(PAYLOAD, ".forge", "bin", "forge-hook")):
        if not os.path.exists(need):
            raise SystemExit(f"make_plugin.py: payload incomplete: {os.path.relpath(need, FORGE)} is missing")
    files: Files = {}
    files[".claude-plugin/plugin.json"] = (dumps({
        "name": "forge", "version": version,
        "description": "The Forge: plan-first, evidence-gated, cost-routed AI engineering team for Claude Code.",
        "author": {"name": "RuggedRoute"}, "homepage": HOMEPAGE, "license": "MIT",
        "keywords": ["orchestration", "hooks", "verification"]}), 0o644)
    copy_tree(os.path.join(PAYLOAD_CLAUDE, "agents"), "agents", files)
    copy_tree(os.path.join(PAYLOAD_CLAUDE, "skills"), "skills", files)
    files["skills/forge-install/SKILL.md"] = (FORGE_INSTALL_SKILL.encode("utf-8"), 0o644)
    copy_tree(os.path.join(PAYLOAD, ".forge", "bin"), "bin", files)
    files["hooks/hooks.json"] = (dumps(plugin_hooks(json.loads(read(fragment_path)))), 0o644)
    files["install.sh"] = (read(os.path.join(FORGE, "install.sh")), 0o755)
    files["installer.py"] = (read(os.path.join(FORGE, "installer.py")), 0o755)
    copy_tree(PAYLOAD, "payload", files)
    copy_tree(os.path.join(FORGE, "migrations"), "migrations", files)
    return files


def existing_files() -> List[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(PLUGIN):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, name), PLUGIN).replace(os.sep, "/"))
    return sorted(out)


def diff(files: Files) -> List[str]:
    """Human-readable differences between plugin/ and what it should be."""
    problems = []
    for rel, (data, mode) in sorted(files.items()):
        path = os.path.join(PLUGIN, rel)
        if not os.path.isfile(path):
            problems.append(f"missing  {rel}")
        elif read(path) != data:
            problems.append(f"differs  {rel}")
        elif mode_of(path) != mode:
            problems.append(f"mode     {rel}")
    for rel in existing_files():
        if rel not in files:
            problems.append(f"extra    {rel}")
    return problems


def write(files: Files) -> int:
    """Make plugin/ equal to `files`; returns the number of paths changed."""
    problems = diff(files)
    for rel, (data, mode) in files.items():
        path = os.path.join(PLUGIN, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.isfile(path) or read(path) != data:
            with open(path, "wb") as f:
                f.write(data)
        os.chmod(path, mode)
    for rel in existing_files():
        if rel not in files:
            os.unlink(os.path.join(PLUGIN, rel))
    for dirpath, _dirnames, _filenames in os.walk(PLUGIN, topdown=False):   # bottom-up: children first
        if dirpath != PLUGIN and not os.listdir(dirpath):
            os.rmdir(dirpath)
    return len(problems)


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="make_plugin.py", description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true", help="exit 1 when plugin/ is not what the payload generates")
    args = p.parse_args(argv)
    try:
        files = expected_files()
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2
    if args.check:
        problems = diff(files)
        for line in problems:
            print(line)
        print(f"make_plugin.py: plugin/ {'is up to date' if not problems else f'differs in {len(problems)} path(s); run python3 forge/tools/make_plugin.py'}")
        return 1 if problems else 0
    changed = write(files)
    print(f"make_plugin.py: plugin/ {'regenerated' if changed else 'already up to date'} ({len(files)} files, {changed} changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
