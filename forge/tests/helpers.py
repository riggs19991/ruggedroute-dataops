"""Fixture builder for the Forge test suite.

Every test builds a throwaway git repository under a tempfile directory, copies the shipped
payload (`forge/payload/.forge` and `forge/payload/.claude`) into it and seeds a minimal
`binding.json` and an idle `STATUS.json` INLINE (MODULE-API §2.1/§2.2; never from templates).
The repo also holds a tiny Python project (`lib/mod.py`, `lib/util.py`, one passing test each)
so `binding.verify[]` commands really run.

Tests are written against the contract (MODULE-API.md, design §5.1 transition table,
§5.5/§5.6 gate rules, §13.3 hook table), never against an implementation.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
FORGE_SRC = os.path.abspath(os.path.join(HERE, ".."))
PAYLOAD = os.path.join(FORGE_SRC, "payload")
PAYLOAD_BIN = os.path.join(PAYLOAD, ".forge", "bin")
INSTALLER = os.path.join(FORGE_SRC, "installer.py")

sys.dont_write_bytecode = True   # never leave __pycache__ inside the shipped payload
if PAYLOAD_BIN not in sys.path:
    sys.path.insert(0, PAYLOAD_BIN)
from forgelib import common  # noqa: E402  (the one module that is guaranteed to exist)

# The verify command every fixture binding carries (MODULE-API §2.2 verify[] entry).
LIB_UNIT = "cd lib && python3 -m unittest -q"
LAYER_TESTS = "python3 -m unittest discover -s layers/{layer}/tests -q"

# Minimal binding per MODULE-API §2.2 (every key the code reads).
BINDING: Dict[str, Any] = {
    "schema_version": 2,
    "forge_pin": "1.0.0",
    "project": "fixture",
    "stack": "python",
    "bootstrap": "true",
    "verify": [
        {"name": "lib-unit", "cmd": LIB_UNIT, "when": "always"},
        {"name": "layer-tests", "cmd": LAYER_TESTS, "when": "paths:layers/{layer}/**",
         "exists": "layers/{layer}/tests", "vars": {"layer": "from-path"}},
    ],
    "smoke": None,
    "format": None,
    "test_globs": ["lib/test_*.py", "layers/*/tests/test_*.py"],
    "test_pattern": "^\\s*def test_",
    "protected_paths": [".github/workflows/*.yml"],
    "risk_paths": ["**/*upload*", "secrets/**"],
    "important_paths": ["lib/live/**"],
    "mechanic_denied_paths": ["lib/shared.py"],
    "risk_words": [{"word": "secret"}, {"word": "delete", "not": ["soft delete"]}, "KV"],
    "irreversible_commands": ["git push *", "wrangler *", "npx wrangler *"],
    "git": {"branch_per_task": False, "commit_prefix": "forge", "worktree_isolation": False},
    "budgets": {"T": 1, "S": 3, "M": 10, "M_chain": 12, "W": 25, "L_unit": 2, "X": 30, "risk_multiplier": 1.5},
    "routing": {"architect_effort": "medium", "m_builder": "opus-medium", "overrides": [], "measured": {}},
    "clear_policy": "phase",
    "auto_resume": True,
    "driver": {"max_turns": 120, "max_phases": 12},
    "notes": ["fixture note: never query live services in tests"],
}


def idle_status(project: str = "fixture") -> Dict[str, Any]:
    """An idle STATUS.json per MODULE-API §2.1 (schema_version 2, task null)."""
    return {
        "schema_version": 2, "forge_version": common.FORGE_VERSION, "project": project,
        "updated_at": "1970-01-01T00:00:00Z", "updated_ts": 0,
        "updated_by": {"session_id": "test", "cmd": "helpers.idle_status"},
        "context_state": "fresh", "task": None, "queue": [], "history": [],
    }


def make_step(step_id: str = "01", task_id: str = "T-0001", **over: Any) -> Dict[str, Any]:
    """One STATUS steps[] entry (MODULE-API §2.1) with every required field; `over` wins."""
    step = {
        "id": step_id, "title": f"step {step_id}", "agent": "forge-builder", "model": "opus", "effort": "medium",
        "status": "pending", "attempts": 0, "from": None, "verify_attempts": 0,
        "started_at": None, "started_ts": None, "started_by": None, "agent_id": None,
        "base": None, "commit": None, "brief": f".forge/tasks/{task_id}/brief-{step_id}.md",
        "report": None, "verdict": None, "red_ok_until": None,
        "allowed_paths": ["lib/mod.py", "lib/util.py", "lib/extra.py"], "mechanical": False, "max_tool_calls": 60,
    }
    step.update(over)
    return step


def make_task(task_id: str = "T-0001", cls: str = "M", phase: str = "execute", steps: Optional[List[Dict[str, Any]]] = None,
              **over: Any) -> Dict[str, Any]:
    """A STATUS task dict (MODULE-API §2.1) with every required field; `over` wins.

    Defaults describe a planned, single-mode class M task on lib/; pass steps=[] and
    routing mode inline for T/S/X.
    """
    inline = cls in ("T", "S", "X")
    if steps is None:
        steps = [] if inline else [make_step("01", task_id)]
    files = ["lib/mod.py", "lib/util.py"]
    creates = [] if cls == "T" else ["lib/extra.py"]
    task = {
        "id": task_id, "title": f"fixture task {task_id}", "class": cls, "risk": "none", "size_source": "declared",
        "files": files, "creates": creates,
        "signals": {"files": len(files) + len(creates), "dirs": 1, "importers": 0, "recent_cochanges": [],
                    "tests_present": True, "risk_hits": [], "important_hits": []},
        "class_justification": "fixture: seeded directly by the test helpers",
        "phase": phase,
        "plan": None if (cls == "T" or phase == "plan") else f".forge/tasks/{task_id}/plan.md",
        "plan_author": None if (cls == "T" or phase == "plan") else "architect",
        "branch": None,
        "scope": files + creates,
        "routing": {"mode": "inline" if inline else "single",
                    "builder": None if inline else {"agent": "forge-builder", "model": "opus", "effort": "medium"},
                    "verifier": None if cls == "T" else {"agent": "forge-verifier", "model": "opus", "effort": "medium"},
                    "justification": "fixture"},
        "steps": steps,
        "escalation": {"step": None, "round": 0},
        "next_action": "fixture next action", "resume_hint": "fixture resume hint",
        "evidence_count": 0, "evidence": [],
        "blocked_on": None, "external": None,
        "budget": {"cap_usd": float(BINDING["budgets"].get(cls, 10))},
        "opened_at": "2026-10-11T00:00:00Z", "base": None,
    }
    task.update(over)
    return task


def sha256_of(path: str) -> Optional[str]:
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def tree_hashes(root: str, skip_dirs: Iterable[str] = (".git", "__pycache__")) -> Dict[str, Optional[str]]:
    """{relative path: sha256} for every file under root (used by idempotency tests)."""
    out: Dict[str, Optional[str]] = {}
    skip = set(skip_dirs)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in filenames:
            p = os.path.join(dirpath, name)
            out[os.path.relpath(p, root)] = sha256_of(p)
    return out


class Repo:
    """A throwaway consumer repository with the Forge payload installed by copy.

    Use `Repo.create()` in setUp and `repo.cleanup()` in tearDown (or `addCleanup`).
    """

    def __init__(self, root: str):
        self.root = root
        self.paths = common.Paths(root)
        self.last: Tuple[int, str, str] = (0, "", "")   # last run_cli / hook result

    # ------------------------------------------------------------------ build
    @classmethod
    def create(cls, with_project: bool = True, commit: bool = True) -> "Repo":
        root = tempfile.mkdtemp(prefix="forge-test-")
        repo = cls(root)
        repo._git_init()
        shutil.copytree(os.path.join(PAYLOAD, ".forge"), repo.path(".forge"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(os.path.join(PAYLOAD, ".claude"), repo.path(".claude"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        # settings.json = the fragment (what the installer would merge into an empty file)
        shutil.copy(repo.path(".claude/settings.forge.json"), repo.path(".claude/settings.json"))
        repo.write(".gitignore", ".forge/.runtime/\n.forge/incidents/\n__pycache__/\n")
        repo.write_json(".forge/binding.json", BINDING)
        repo.write_json(".forge/STATUS.json", idle_status())
        for rel in (".forge/ledger.jsonl", ".forge/history.jsonl", ".forge/queue.jsonl"):
            repo.write(rel, "")
        repo.write(".forge/CHANGELOG.md", "# Changelog\n\n")
        repo.write(".forge/lessons/INDEX.md", "# Lessons index\n- fixture lesson: run commands from the root\n")
        os.makedirs(repo.path(".forge/.runtime"), exist_ok=True)
        os.makedirs(repo.path(".forge/tasks"), exist_ok=True)
        os.makedirs(repo.path(".claude/agent-memory/forge-verifier"), exist_ok=True)
        repo.write(".claude/agent-memory/forge-verifier/MEMORY.md", "# notes\n")
        if with_project:
            repo.write("lib/mod.py", "def add(a, b):\n    return a + b\n")
            repo.write("lib/util.py", "def twice(x):\n    return 2 * x\n")
            repo.write("lib/test_mod.py", "import unittest\nfrom mod import add\n\n\nclass T(unittest.TestCase):\n"
                                           "    def test_add(self):\n        self.assertEqual(add(1, 2), 3)\n")
            repo.write("lib/test_util.py", "import unittest\nfrom util import twice\n\n\nclass T(unittest.TestCase):\n"
                                            "    def test_twice(self):\n        self.assertEqual(twice(2), 4)\n")
            repo.write("lib/shared.py", "SHARED = 1\n")
            repo.write("lib/test_shared.py", "import unittest\nfrom shared import SHARED\n\n\nclass T(unittest.TestCase):\n"
                                              "    def test_shared(self):\n        self.assertEqual(SHARED, 1)\n")
            repo.write("README.md", "# fixture\n")
        if commit:
            repo.commit_all("fixture: initial")
        return repo

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def _git_init(self) -> None:
        self.git("init", "-q", ".")
        self.git("config", "user.name", "Forge Test")
        self.git("config", "user.email", "forge-test@example.invalid")
        self.git("config", "commit.gpgsign", "false")

    # ------------------------------------------------------------------ files
    def path(self, rel: str) -> str:
        return os.path.join(self.root, rel)

    def exists(self, rel: str) -> bool:
        return os.path.exists(self.path(rel))

    def read(self, rel: str) -> str:
        with open(self.path(rel), "r", encoding="utf-8") as f:
            return f.read()

    def write(self, rel: str, text: str) -> str:
        p = self.path(rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p

    def append(self, rel: str, text: str) -> None:
        with open(self.path(rel), "a", encoding="utf-8") as f:
            f.write(text)

    def read_json(self, rel: str) -> Any:
        return json.loads(self.read(rel))

    def write_json(self, rel: str, obj: Any) -> str:
        return self.write(rel, json.dumps(obj, indent=2) + "\n")

    def read_jsonl(self, rel: str) -> List[Dict[str, Any]]:
        if not self.exists(rel):
            return []
        rows = []
        for line in self.read(rel).splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def rm(self, rel: str) -> None:
        try:
            os.unlink(self.path(rel))
        except FileNotFoundError:
            pass

    def touch(self, rel: str) -> None:
        p = self.path(rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a", encoding="utf-8"):
            pass

    def rt(self, name: str) -> str:
        """Runtime marker path (relative)."""
        return f".forge/.runtime/{name}"

    def status(self) -> Dict[str, Any]:
        return self.read_json(".forge/STATUS.json")

    def task(self) -> Optional[Dict[str, Any]]:
        return self.status().get("task")

    def step(self, step_id: str = "01") -> Optional[Dict[str, Any]]:
        task = self.task()
        if not task:
            return None
        for s in task.get("steps") or []:
            if s.get("id") == step_id:
                return s
        return None

    def ledger(self) -> List[Dict[str, Any]]:
        return self.read_jsonl(".forge/ledger.jsonl")

    def ledger_events(self) -> List[str]:
        return [r.get("event") for r in self.ledger()]

    def journal(self, task_id: str) -> str:
        rel = f".forge/tasks/{task_id}/journal.md"
        return self.read(rel) if self.exists(rel) else ""

    def evidence(self, task_id: str) -> List[Dict[str, Any]]:
        return self.read_jsonl(f".forge/tasks/{task_id}/evidence.jsonl")

    def check_files(self, task_id: str) -> List[str]:
        d = self.path(f".forge/tasks/{task_id}/checks")
        if not os.path.isdir(d):
            return []
        return sorted(os.listdir(d))

    # ------------------------------------------------------------------ git
    def git(self, *args: str) -> Tuple[int, str]:
        r = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, timeout=60)
        return r.returncode, (r.stdout or "") + (r.stderr or "")

    def head(self) -> str:
        return self.git("rev-parse", "HEAD")[1].strip()

    def commit_all(self, msg: str) -> str:
        self.git("add", "-A")
        code, out = self.git("commit", "-q", "-m", msg)
        if code != 0:
            raise RuntimeError(f"git commit failed: {out}")
        return self.head()

    def porcelain(self) -> List[str]:
        return common.git_porcelain(self.root)

    def last_commit_message(self) -> str:
        return self.git("log", "-1", "--pretty=%s")[1].strip()

    # ------------------------------------------------------------------ processes
    def env(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Environment for a Forge process: CLAUDE_PROJECT_DIR set, no inherited FORGE_ROOT."""
        env = dict(os.environ)
        for k in ("FORGE_ROOT", "CLAUDE_ENV_FILE", "CLAUDE_CODE_SESSION_ID"):
            env.pop(k, None)
        env["CLAUDE_PROJECT_DIR"] = self.root
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        if extra:
            env.update(extra)
        return env

    def run_cli(self, name: str, *args: str, stdin: Optional[str] = None,
                env: Optional[Dict[str, str]] = None, timeout: int = 300) -> Tuple[int, str, str]:
        """Invoke <repo>/.forge/bin/<name> from the repo root; returns (exit, stdout, stderr)."""
        exe = self.path(f".forge/bin/{name}")
        r = subprocess.run([exe, *args], cwd=self.root, env=self.env(env), input=stdin,
                           capture_output=True, text=True, timeout=timeout)
        self.last = (r.returncode, r.stdout, r.stderr)
        return self.last

    def forge_status(self, *args: str) -> Tuple[int, str, str]:
        return self.run_cli("forge-status", *args)

    def hook(self, stdin: Dict[str, Any], *flags: str, env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Pipe `stdin` as JSON into forge-hook and return its parsed stdout JSON ({} when empty).

        The raw (exit, stdout, stderr) triple is kept in `self.last`.
        """
        code, out, err = self.run_cli("forge-hook", *flags, stdin=json.dumps(stdin), env=env)
        out = out.strip()
        if not out:
            return {}
        return json.loads(out)

    def installer(self, *args: str, target: Optional[str] = None) -> Tuple[int, str, str]:
        r = subprocess.run([sys.executable, INSTALLER, "--target", target or self.root, "--source", PAYLOAD, *args],
                           cwd=self.root, env=self.env(), capture_output=True, text=True, timeout=300)
        self.last = (r.returncode, r.stdout, r.stderr)
        return self.last

    # ------------------------------------------------------------------ STATUS seeding
    def seed_status(self, task: Optional[Dict[str, Any]] = None, queue: Sequence[Dict[str, Any]] = (),
                    history: Sequence[Dict[str, Any]] = (), context_state: str = "fresh", restamp: bool = True) -> Dict[str, Any]:
        """Write a STATUS.json directly (test seeding), then `validate --restamp` so status.sha matches.

        Returns the written dict. With restamp=False the file is left unstamped (hand-edit scenario).
        """
        st = idle_status()
        st["task"] = task
        st["queue"] = list(queue)
        st["history"] = list(history)
        st["context_state"] = context_state
        self.write_json(".forge/STATUS.json", st)
        if restamp:
            code, out, err = self.forge_status("validate", "--restamp")
            if code != 0:
                raise RuntimeError(f"seeded STATUS does not validate: {err or out}")
        return st

    def open_task(self, title: str, cls: str, files: Sequence[str], creates: Sequence[str] = (), risk: str = "none",
                  why: str = "fixture: declared set is small and has no risk hits", *extra: str) -> Tuple[int, str, str]:
        args = ["open", "--title", title, "--class", cls, "--risk", risk, "--why", why]
        if files:
            args += ["--files", *files]
        if creates:
            args += ["--creates", *creates]
        args += list(extra)
        return self.forge_status(*args)

    # ------------------------------------------------------------------ artifact writers
    def task_dir(self, task_id: str) -> str:
        d = self.path(f".forge/tasks/{task_id}")
        os.makedirs(d, exist_ok=True)
        return d

    def write_plan(self, task_id: str, cls: str = "M", steps: Optional[List[Dict[str, Any]]] = None,
                   dod: Optional[List[Dict[str, Any]]] = None, mode: Optional[str] = None, risk: str = "none",
                   chain: bool = False, rollback: str = "git revert HEAD", allowed_paths: Optional[List[str]] = None,
                   needs_clarification: Sequence[str] = (), test_baseline: Optional[Dict[str, Any]] = None,
                   builder: Any = "default", verifier: Any = "default", headings: Optional[Sequence[str]] = None,
                   extra_meta: Optional[Dict[str, Any]] = None, title: str = "fixture plan") -> str:
        """Write .forge/tasks/<id>/plan.md per MODULE-API §2.3; returns its repo-relative path.

        `steps` entries may be partial; defaults fill forge-builder opus/medium with brief-NN.md.
        `headings=None` picks the mandatory set for the class; pass a list to override.
        """
        inline = cls in ("S", "X")
        if steps is None:
            steps = [] if inline else [{"id": "01"}]
        full_steps = []
        for s in steps:
            d = {"id": "01", "title": "fixture step", "brief": None, "agent": "forge-builder", "model": "opus",
                 "effort": "medium", "mechanical": False, "red_ok_until": None, "max_tool_calls": 60}
            d.update(s)
            if d["brief"] is None:
                d["brief"] = f"brief-{d['id']}.md"
            full_steps.append(d)
        if mode is None:
            mode = "inline" if inline else "single"
        if builder == "default":
            builder = None if (mode == "inline" or not full_steps) else {
                "agent": full_steps[0]["agent"], "model": full_steps[0]["model"], "effort": full_steps[0]["effort"]}
        if verifier == "default":
            verifier = None if cls == "T" else {"agent": "forge-verifier", "model": "opus", "effort": "medium"}
        if dod is None:
            dod = [{"id": "DoD-1", "criterion": "WHEN the lib suite runs THE SYSTEM SHALL exit 0", "check": LIB_UNIT}]
        meta = {
            "schema": common.SCHEMA_PLAN, "task": task_id, "class": cls, "risk": risk, "chain": chain,
            "routing": {"mode": mode, "builder": builder, "verifier": verifier, "justification": "fixture routing"},
            "steps": full_steps, "dod": dod, "rollback": rollback,
            "test_baseline": test_baseline or {"files": 0, "tests": 0, "recorded_at": "1970-01-01T00:00:00Z"},
            "needs_clarification": list(needs_clarification),
        }
        if inline:
            meta["allowed_paths"] = list(allowed_paths or ["lib/mod.py", "lib/util.py"])
        elif allowed_paths is not None:
            meta["allowed_paths"] = list(allowed_paths)
        if extra_meta:
            meta.update(extra_meta)
        if headings is None:
            if cls == "M":
                headings = common.PLAN_HEADINGS_M
            elif cls in ("W", "L"):
                headings = common.PLAN_HEADINGS_FULL
            else:
                headings = common.PLAN_HEADINGS_INLINE
        lines = [f"# Execution Plan: {task_id} — {title}", "", "```json", json.dumps(meta, indent=2), "```", ""]
        for h in headings:
            lines.append(f"## {h}")
            if h == "Steps":
                for s in full_steps:
                    lines += [f"### Step {s['id']} — {s['title']}", f"- File: {', '.join(allowed_paths or ['lib/'])}",
                              "- Action: modify", "- Details: fixture", f"- Verify: `.forge/bin/forge-check {task_id} {s['id']}`"]
            elif h == "Validation Criteria":
                for d in dod:
                    lines.append(f"- {d['id']}: {d['criterion']} — check: `{d['check']}`")
            elif h == "Rollback":
                lines.append(rollback)
            else:
                lines.append(f"{h}: fixture text.")
            lines.append("")
        rel = f".forge/tasks/{task_id}/plan.md"
        self.write(rel, "\n".join(lines))
        return rel

    def write_brief(self, task_id: str, step_id: str = "01", allowed_paths: Optional[List[str]] = None,
                    checks: Optional[List[str]] = None, owner_agent: str = "forge-builder", model: str = "opus",
                    effort: str = "medium", tdd: bool = False, expected_fail_first: Optional[List[str]] = None,
                    may_edit_tests: bool = False, dod: Sequence[str] = ("DoD-1",), risk: str = "none",
                    red_ok: bool = False, max_tool_calls: int = 60, bootstrap: str = "true",
                    headings: Optional[Sequence[str]] = None, extra_meta: Optional[Dict[str, Any]] = None) -> str:
        """Write .forge/tasks/<id>/brief-NN.md per MODULE-API §2.4; returns its repo-relative path."""
        meta = {
            "schema": common.SCHEMA_BRIEF, "task": task_id, "step": step_id, "owner_agent": owner_agent,
            "model": model, "effort": effort,
            "allowed_paths": list(allowed_paths or ["lib/mod.py", "lib/util.py", "lib/extra.py"]),
            "may_edit_tests": may_edit_tests, "tdd": tdd, "checks": list(checks if checks is not None else [LIB_UNIT]),
            "expected_fail_first": list(expected_fail_first or []), "dod": list(dod), "risk": risk, "red_ok": red_ok,
            "max_tool_calls": max_tool_calls, "bootstrap": bootstrap,
        }
        if extra_meta:
            meta.update(extra_meta)
        if headings is None:
            headings = ("Goal", "Context the worker needs", "Definition of done", "Out of scope / do not touch",
                        "Known failed approaches", "Output contract")
        lines = [f"# Brief {task_id}/{step_id} — fixture", "", "```json", json.dumps(meta, indent=2), "```", ""]
        for h in headings:
            lines += [f"## {h}", f"{h}: fixture text.", ""]
        rel = f".forge/tasks/{task_id}/brief-{step_id}.md"
        self.write(rel, "\n".join(lines))
        return rel

    @staticmethod
    def handoff_json(task_id: str, step_id: str, status: str = "DONE", files_changed: Sequence[str] = (),
                     checks_run: Optional[List[Dict[str, Any]]] = None, commit: Optional[str] = None,
                     **over: Any) -> Dict[str, Any]:
        obj = {"schema": common.SCHEMA_HANDOFF, "task": task_id, "step": step_id, "status": status,
               "files_changed": list(files_changed),
               "checks_run": checks_run if checks_run is not None else [{"cmd": LIB_UNIT, "exit": 0, "expected_fail": False}],
               "not_verified": [], "failed_approaches": [], "next_action": "none", "commit": commit}
        obj.update(over)
        return obj

    def write_report_md(self, task_id: str, step_id: str = "01", status: str = "DONE", files_changed: Sequence[str] = (),
                        checks_run: Optional[List[Dict[str, Any]]] = None, commit: Optional[str] = None,
                        headings: Optional[Sequence[str]] = None, short: bool = False, json_obj: Any = "default",
                        path: Optional[str] = None, **over: Any) -> str:
        """Build a HANDOFF message (MODULE-API §2.5). Returns the text; also writes it to `path` when given.

        `json_obj=None` omits the JSON block; a dict replaces the default one.
        """
        if headings is None:
            headings = common.HANDOFF_SHORT_HEADINGS if short else common.HANDOFF_MANDATORY_HEADINGS
        lines = []
        for h in headings:
            body = "none" if h in ("Remaining", "Gotchas / do not touch") else f"{h}: fixture text."
            if h == "Done, with evidence":
                body = f"- lib suite green — `{LIB_UNIT}` exit 0 (.forge/tasks/{task_id}/checks/)"
            lines += [f"## {h}", body, ""]
        if json_obj == "default":
            json_obj = self.handoff_json(task_id, step_id, status, files_changed, checks_run, commit, **over)
        if json_obj is not None:
            lines += ["```json", json.dumps(json_obj, indent=2), "```", ""]
        text = "\n".join(lines)
        if path:
            self.write(path, text)
        return text

    @staticmethod
    def verdict_json(task_id: str, step_id: str, verdict: str = "PASS", criteria: Optional[List[Dict[str, Any]]] = None,
                     scope_check: str = "PASS", ratchet: str = "PASS", blocking: Sequence[str] = (),
                     deferred: Sequence[str] = (), tags: Sequence[str] = (), range_: str = "worktree",
                     **over: Any) -> Dict[str, Any]:
        obj = {"schema": common.SCHEMA_VERDICT, "task": task_id, "step": step_id, "range": range_, "verdict": verdict,
               "criteria": criteria if criteria is not None else [{"id": "DoD-1", "result": "PASS", "cmd": LIB_UNIT, "exit": 0}],
               "scope_check": scope_check, "ratchet": ratchet, "blocking_findings": list(blocking),
               "deferred_findings": list(deferred), "tags": list(tags)}
        obj.update(over)
        return obj

    def write_verdict_md(self, task_id: str, step_id: str = "01", verdict: str = "PASS",
                         criteria: Optional[List[Dict[str, Any]]] = None, scope_check: str = "PASS", ratchet: str = "PASS",
                         blocking: Sequence[str] = (), deferred: Sequence[str] = (), tags: Sequence[str] = (),
                         range_: str = "worktree", headings: Optional[Sequence[str]] = None, json_obj: Any = "default",
                         path: Optional[str] = None, **over: Any) -> str:
        """Build a VERDICT message (MODULE-API §2.6). Returns the text; also writes it to `path` when given."""
        if headings is None:
            headings = common.VERDICT_HEADINGS
        lines = []
        for h in headings:
            body = "none" if h in ("Blocking findings", "Deferred findings") else f"{verdict} — fixture {h.lower()}."
            lines += [f"## {h}", body, ""]
        if json_obj == "default":
            json_obj = self.verdict_json(task_id, step_id, verdict, criteria, scope_check, ratchet, blocking, deferred,
                                         tags, range_, **over)
        if json_obj is not None:
            lines += ["```json", json.dumps(json_obj, indent=2), "```", ""]
        text = "\n".join(lines)
        if path:
            self.write(path, text)
        return text

    def write_check_record(self, task_id: str, step_id: str = "01", agent_id: str = "unknown",
                           results: Optional[List[Dict[str, Any]]] = None, ts: Optional[int] = None,
                           expect_fail: bool = False, ratchet: Optional[Dict[str, Any]] = None, ok: Optional[bool] = None,
                           session_id: str = "cli") -> str:
        """Write a checks/<step>-<ts>-<agent>.json record (MODULE-API §2.7); returns its repo-relative path."""
        ts = int(ts if ts is not None else time.time())
        if results is None:
            results = [{"name": "lib-unit", "cmd": LIB_UNIT, "exit": 0, "dur_s": 0.1, "tail": "OK"}]
        if ok is None:
            ok = all(r.get("exit") == 0 for r in results if r.get("status") != "skipped")
        rec = {"ts": ts, "agent_id": agent_id, "session_id": session_id, "task": task_id, "step": step_id,
               "expect_fail": expect_fail, "results": results, "ratchet": ratchet, "ok": ok}
        rel = f".forge/tasks/{task_id}/checks/{step_id}-{ts}-{agent_id}.json"
        self.write_json(rel, rec)
        return rel

    def write_human_record(self, task_id: str, step_id: str, criterion: str, by: str = "riggs",
                           evidence: str = "https://example.invalid/run/1", exit_code: int = 0,
                           ts: Optional[int] = None) -> str:
        """A human attestation record (MODULE-API §2.7)."""
        ts = int(ts if ts is not None else time.time())
        rec = {"ts": ts, "agent_id": "human", "source": "human", "by": by, "criterion": criterion,
               "evidence": evidence, "exit": exit_code, "task": task_id, "step": step_id}
        rel = f".forge/tasks/{task_id}/checks/{step_id}-{ts}-human.json"
        self.write_json(rel, rec)
        return rel

    def add_evidence(self, task_id: str, agent_id: str = "main", agent_type: str = "main", event: str = "edit",
                     ts: Optional[int] = None, **fields: Any) -> Dict[str, Any]:
        """Append one evidence row (MODULE-API §2.8)."""
        row = {"ts": int(ts if ts is not None else time.time()), "agent_id": agent_id, "agent_type": agent_type,
               "event": event}
        row.update(fields)
        with open(self.write_path(f".forge/tasks/{task_id}/evidence.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        return row

    def write_path(self, rel: str) -> str:
        p = self.path(rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    def agent_record(self, agent_id: str, agent_type: str, **fields: Any) -> Dict[str, Any]:
        """Write .forge/.runtime/agents/<agent_id>.json (MODULE-API §2.10/§2.11)."""
        rec = {"agent_id": agent_id, "agent_type": agent_type, "started_ts": int(time.time()), "session_id": "sess-test"}
        rec.update(fields)
        self.write_json(f".forge/.runtime/agents/{agent_id}.json", rec)
        return rec

    def bind_agent(self, agent_id: str, task_id: str = "T-0001", step_id: str = "01",
                   agent_type: str = "forge-builder") -> Dict[str, Any]:
        """An agent record bound to a brief (MODULE-API §2.11)."""
        return self.agent_record(agent_id, agent_type, task=task_id, step=step_id,
                                 brief=f".forge/tasks/{task_id}/brief-{step_id}.md", bound_at=int(time.time()))


# ---------------------------------------------------------------------- hook stdin builders
def pre_tool(tool_name: str, tool_input: Dict[str, Any], agent_id: Optional[str] = None,
             agent_type: Optional[str] = None, session_id: str = "sess-test", **extra: Any) -> Dict[str, Any]:
    d: Dict[str, Any] = {"hook_event_name": "PreToolUse", "tool_name": tool_name, "tool_input": tool_input,
                         "session_id": session_id, "permission_mode": "default"}
    if agent_id:
        d["agent_id"] = agent_id
    if agent_type:
        d["agent_type"] = agent_type
    d.update(extra)
    return d


def post_tool(tool_name: str, tool_input: Dict[str, Any], tool_response: Any = None, agent_id: Optional[str] = None,
              agent_type: Optional[str] = None, session_id: str = "sess-test", **extra: Any) -> Dict[str, Any]:
    d: Dict[str, Any] = {"hook_event_name": "PostToolUse", "tool_name": tool_name, "tool_input": tool_input,
                         "tool_response": tool_response if tool_response is not None else {}, "session_id": session_id}
    if agent_id:
        d["agent_id"] = agent_id
    if agent_type:
        d["agent_type"] = agent_type
    d.update(extra)
    return d


def decision(out: Dict[str, Any]) -> Optional[str]:
    """permissionDecision from a PreToolUse hook output (None when the hook allowed silently)."""
    return (out.get("hookSpecificOutput") or {}).get("permissionDecision")


def reason(out: Dict[str, Any]) -> str:
    hso = out.get("hookSpecificOutput") or {}
    return str(hso.get("permissionDecisionReason") or out.get("reason") or out.get("stopReason") or "")


def context(out: Dict[str, Any]) -> str:
    return str((out.get("hookSpecificOutput") or {}).get("additionalContext") or "")
