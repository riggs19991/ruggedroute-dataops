#!/usr/bin/env python3
"""0001-binding-agent-paths.py — Forge 1.0.1: add `"agent_paths": []` to an existing .forge/binding.json.

Additive and idempotent (migrations/README.md): when the key is absent it is inserted right after the
`mechanic_denied_paths` entry and every other byte of the file is kept; when it is present nothing changes.
If the file's layout defeats the textual insert (no `mechanic_denied_paths` line of its own), the binding is
re-serialised with indent 2 instead: same content, different formatting. Standard library only.
"""
import json
import os
import re
import sys

KEY = "agent_paths"
AFTER = "mechanic_denied_paths"
NAME = "0001-binding-agent-paths"


def value_end(text: str, start: int) -> int:
    """Index just past the JSON value that starts at text[start] (array, object, string or scalar)."""
    depth = 0
    i = start
    in_str = False
    while i < len(text):
        ch = text[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                in_str = False
                if depth == 0:
                    return i + 1
        elif ch == '"':
            in_str = True
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
            if depth == 0:
                return i + 1
            if depth < 0:
                return i
        elif depth == 0 and ch in ",\r\n}":
            return i
        i += 1
    return len(text)


def insert_key(text: str) -> str:
    m = re.search(r'^([ \t]*)"' + AFTER + r'"\s*:\s*', text, re.MULTILINE)
    if not m:
        raise ValueError(f"no {AFTER} line")
    end = value_end(text, m.end())
    nl = "\r\n" if "\r\n" in text else "\n"
    return text[:end] + "," + nl + m.group(1) + f'"{KEY}": []' + text[end:]


def main() -> int:
    target = os.environ.get("FORGE_TARGET") or os.getcwd()
    path = os.path.join(target, ".forge", "binding.json")
    if not os.path.isfile(path):
        print(f"{NAME}: {path} absent; nothing to migrate")
        return 0
    with open(path, "rb") as f:
        text = f.read().decode("utf-8-sig")
    try:
        binding = json.loads(text)
    except ValueError as e:
        print(f"{NAME}: {path} is not valid JSON ({e})", file=sys.stderr)
        return 1
    if not isinstance(binding, dict):
        print(f"{NAME}: {path} is not a JSON object", file=sys.stderr)
        return 1
    if KEY in binding:
        print(f"{NAME}: {KEY} already present; nothing to do")
        return 0
    try:
        new = insert_key(text)
        parsed = json.loads(new)
        if not isinstance(parsed, dict) or parsed.get(KEY) != [] or {k: v for k, v in parsed.items() if k != KEY} != binding:
            raise ValueError("textual insert changed the binding")
    except ValueError:
        binding[KEY] = []
        new = json.dumps(binding, indent=2, ensure_ascii=False) + "\n"
    tmp = path + ".forge-tmp"
    with open(tmp, "wb") as f:
        f.write(new.encode("utf-8"))
    os.replace(tmp, path)
    print(f"{NAME}: added {KEY}: [] to .forge/binding.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
