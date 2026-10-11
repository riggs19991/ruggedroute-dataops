"""Shared helpers for every Forge script. Standard library only.

Design contract (forge/docs/MODULE-API.md): this module owns
  * locating the repository root and the .forge/ tree (worktree-safe),
  * atomic JSON I/O and append-only JSONL,
  * glob matching with ** semantics, model alias normalisation,
  * the evidence log, ledger, journal and runtime markers,
  * small git / subprocess wrappers,
  * constants shared by status, gates, checks and hooks.
It never writes STATUS.json itself (that is forgelib.status).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple

FORGE_VERSION = "1.0.0"

# --------------------------------------------------------------------------- #
# Exit codes (same for every CLI)
# --------------------------------------------------------------------------- #
EXIT_OK = 0
EXIT_DEFECTS = 1      # forge-gate / forge-check: defects or failing checks
EXIT_USAGE = 2
EXIT_REFUSED = 3      # forge-status: precondition refused
EXIT_INVALID = 4      # STATUS.json invalid on disk / hooks not alive
EXIT_BLOCKED = 6      # forge-run: permission denials in headless phase


class ForgeError(Exception):
    """Raised by library code; CLIs print str(e) to stderr and exit with .code."""

    def __init__(self, message: str, code: int = EXIT_REFUSED):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- #
# Enumerations and constants (mirror .forge/schemas/*.json)
# --------------------------------------------------------------------------- #
CLASSES = ("T", "S", "M", "W", "L", "X")
RISKS = ("none", "R")
PHASES = ("idle", "intake", "plan", "execute", "verify", "awaiting_external", "close", "done", "blocked")
MODES = ("inline", "single", "parallel")
STEP_STATUSES = ("pending", "running", "reported", "verifying", "done", "failed", "blocked", "awaiting_external")
STEP_FROM = (None, "failed", "clean")
PLAN_AUTHORS = ("architect", "forge-planner")
CONTEXT_STATES = ("fresh", "stale")
HANDOFF_STATUSES = ("DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED", "UNVERIFIED")
VERDICTS = ("PASS", "FAIL", "UNKNOWN")
CRITERION_RESULTS = ("PASS", "FAIL", "UNKNOWN")
VERDICT_TAGS = ("skipped-file", "no-check-run", "not-double-checked", "wrong-approach",
                "scope-creep", "test-weakened", "env-cannot-run")
EFFORTS = ("low", "medium", "high", "xhigh", "max")
MODELS = ("haiku", "sonnet", "opus", "fable")
TIER_ORDER = {"haiku": 0, "sonnet": 1, "opus": 2, "fable": 3}
EFFORT_ORDER = {"low": 0, "medium": 1, "high": 2, "xhigh": 3, "max": 4}

HANDOFF_MANDATORY_HEADINGS = ("Where things stand", "Done, with evidence", "Remaining", "Gotchas / do not touch")
HANDOFF_OPTIONAL_HEADINGS = ("Goal & scope", "Decisions & rationale", "Failed approaches — do not repeat",
                             "Files touched", "Verification commands + expected output", "Open questions", "Bootstrap")
HANDOFF_SHORT_HEADINGS = ("Where things stand", "Done, with evidence", "Remaining")
VERDICT_HEADINGS = ("Verdict", "Criteria", "Scope check", "Blocking findings", "Deferred findings", "Confidence note")
PLAN_HEADINGS_M = ("Steps", "Validation Criteria", "Routing", "Rollback")
PLAN_HEADINGS_FULL = PLAN_HEADINGS_M + ("Objective", "Current State", "Target State", "Tech Stack Context",
                                        "File Manifest", "Dependency Order", "Anti-Patterns — DO NOT",
                                        "Escalation Points")
PLAN_HEADINGS_INLINE = ("Validation Criteria", "Rollback")   # S / X inline plan section

SCHEMA_PLAN = "forge/plan/2"
SCHEMA_BRIEF = "forge/brief/2"
SCHEMA_HANDOFF = "forge/handoff/2"
SCHEMA_VERDICT = "forge/verdict/2"

WORKER_ROLES = ("forge-builder", "forge-builder-wide", "forge-builder-s", "forge-mechanic")
READONLY_ROLES = ("forge-scout", "forge-verifier", "forge-planner")
ALL_ROLES = WORKER_ROLES + READONLY_ROLES + ("forge-librarian",)

# agent name -> (default model alias, default effort)
DEFAULT_AGENT_ROUTING: Dict[str, Tuple[str, str]] = {
    "forge-builder": ("opus", "medium"),
    "forge-builder-wide": ("fable", "low"),
    "forge-builder-s": ("sonnet", "medium"),
    "forge-mechanic": ("haiku", "medium"),
    "forge-verifier": ("opus", "medium"),
    "forge-planner": ("fable", "high"),
    "forge-scout": ("haiku", "medium"),
    "forge-librarian": ("sonnet", "medium"),
}

# Paths (relative to the repo root) that are "meta" edits, never "source" edits.
META_PREFIXES = (".forge/", ".claude/agent-memory/")
META_FILES = ("CLAUDE.md", ".gitignore")

# Paths the architect may edit while a task is open but before/without a plan (idle allow-list).
ARCHITECT_META_ALLOW = (".forge/tasks/", ".forge/lessons/", ".forge/decisions/", ".forge/CHANGELOG.md",
                        ".forge/COST-REPORT.md", "CLAUDE.md", ".gitignore")

# Policy-locked paths: never edited by a model through Edit/Write (gate 14).
POLICY_LOCK_PREFIXES = (".forge/bin/", ".forge/schemas/", ".forge/templates/", ".claude/settings")
POLICY_LOCK_FILES = (".forge/STATUS.json", ".forge/binding.json", ".forge/ledger.jsonl",
                     ".forge/history.jsonl", ".forge/queue.jsonl", ".forge/install-manifest.json",
                     ".forge/VERSION", ".forge/FORGE.md", ".forge/RUNBOOK.md", ".forge/ROUTING.md",
                     ".forge/HOOKS.md", ".forge/SCHEMAS.md", ".forge/GATES.md", ".forge/ROLE-architect.md")

MAX_ADDITIONAL_CONTEXT = 9800
MAX_DIGEST = 3000
STOP_SOFT_CAP = 2
GATE_BLOCK_CAP = 2
TOOL_BUDGET_DEFAULT = 60
WIDE_TOOL_BUDGET_DEFAULT = 250


# --------------------------------------------------------------------------- #
# Time
# --------------------------------------------------------------------------- #
def now_ts() -> int:
    return int(time.time())


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def iso_to_ts(s: str) -> int:
    s = s.replace("Z", "+00:00")
    return int(_dt.datetime.fromisoformat(s).timestamp())


# --------------------------------------------------------------------------- #
# Root discovery and paths
# --------------------------------------------------------------------------- #
def _git_out(args: List[str], cwd: Optional[str] = None) -> Optional[str]:
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def forge_root(start: Optional[str] = None) -> str:
    """The main checkout that owns .forge/ (worktree-safe).

    Order: $FORGE_ROOT if it has .forge/; git common dir of $CLAUDE_PROJECT_DIR or cwd
    (strip trailing /.git); git toplevel; walk up from start looking for .forge/;
    finally $CLAUDE_PROJECT_DIR or cwd.
    """
    env_root = os.environ.get("FORGE_ROOT")
    if env_root and os.path.isdir(os.path.join(env_root, ".forge")):
        return os.path.abspath(env_root)
    start = start or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    start = os.path.abspath(start)
    common = _git_out(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=start)
    if common:
        common = common.rstrip("/")
        cand = common[:-len("/.git")] if common.endswith("/.git") else os.path.dirname(common)
        if os.path.isdir(os.path.join(cand, ".forge")):
            return cand
    top = _git_out(["rev-parse", "--show-toplevel"], cwd=start)
    if top and os.path.isdir(os.path.join(top, ".forge")):
        return top
    cur = start
    while True:
        if os.path.isdir(os.path.join(cur, ".forge")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.environ.get("CLAUDE_PROJECT_DIR") or start


class Paths:
    """All Forge paths derived from one root. Attribute access returns absolute paths."""

    def __init__(self, root: Optional[str] = None):
        self.root = os.path.abspath(root or forge_root())
        self.forge = os.path.join(self.root, ".forge")
        self.bin = os.path.join(self.forge, "bin")
        self.status = os.path.join(self.forge, "STATUS.json")
        self.binding = os.path.join(self.forge, "binding.json")
        self.ledger = os.path.join(self.forge, "ledger.jsonl")
        self.history = os.path.join(self.forge, "history.jsonl")
        self.queue = os.path.join(self.forge, "queue.jsonl")
        self.changelog = os.path.join(self.forge, "CHANGELOG.md")
        self.cost_report = os.path.join(self.forge, "COST-REPORT.md")
        self.tasks = os.path.join(self.forge, "tasks")
        self.lessons = os.path.join(self.forge, "lessons")
        self.lessons_index = os.path.join(self.lessons, "INDEX.md")
        self.decisions = os.path.join(self.forge, "decisions")
        self.archive = os.path.join(self.forge, "archive")
        self.incidents = os.path.join(self.forge, "incidents")
        self.runtime = os.path.join(self.forge, ".runtime")
        self.schemas = os.path.join(self.forge, "schemas")
        self.templates = os.path.join(self.forge, "templates")
        self.version_file = os.path.join(self.forge, "VERSION")
        self.manifest = os.path.join(self.forge, "install-manifest.json")
        self.routing = os.path.join(self.schemas, "routing.json")
        self.forge_md = os.path.join(self.forge, "FORGE.md")
        self.role_md = os.path.join(self.forge, "ROLE-architect.md")
        self.claude_dir = os.path.join(self.root, ".claude")
        self.settings = os.path.join(self.claude_dir, "settings.json")
        self.settings_fragment = os.path.join(self.claude_dir, "settings.forge.json")
        self.agent_memory = os.path.join(self.claude_dir, "agent-memory")

    # task-scoped
    def task(self, task_id: str) -> str:
        return os.path.join(self.tasks, task_id)

    def task_file(self, task_id: str, name: str) -> str:
        return os.path.join(self.tasks, task_id, name)

    def checks_dir(self, task_id: str) -> str:
        return os.path.join(self.tasks, task_id, "checks")

    def evidence(self, task_id: str) -> str:
        return os.path.join(self.tasks, task_id, "evidence.jsonl")

    def journal_file(self, task_id: Optional[str]) -> str:
        if task_id:
            return os.path.join(self.tasks, task_id, "journal.md")
        return os.path.join(self.runtime, "journal.log")

    def base_file(self, task_id: str, step_id: str) -> str:
        return os.path.join(self.tasks, task_id, f".base-{step_id}")

    # runtime markers
    def rt(self, name: str) -> str:
        return os.path.join(self.runtime, name)

    def agent_record(self, agent_id: str) -> str:
        return os.path.join(self.runtime, "agents", f"{agent_id}.json")

    def rel(self, path: str) -> str:
        """Normalise any path to repo-relative POSIX form (no leading ./)."""
        p = path
        if not os.path.isabs(p):
            p = os.path.join(self.root, p)
        p = os.path.normpath(p)
        try:
            r = os.path.relpath(p, self.root)
        except ValueError:
            r = p
        r = r.replace(os.sep, "/")
        if r.startswith("./"):
            r = r[2:]
        return r


# --------------------------------------------------------------------------- #
# Files and JSON
# --------------------------------------------------------------------------- #
def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def read_text(path: str, default: Optional[str] = None) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return default


def write_text_atomic(path: str, text: str) -> None:
    ensure_dir(os.path.dirname(path) or ".")
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=os.path.dirname(path) or ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def read_json(path: str, default: Any = None) -> Any:
    text = read_text(path)
    if text is None:
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ForgeError(f"{path}: invalid JSON: {e}", EXIT_INVALID)


def dumps(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def write_json_atomic(path: str, obj: Any) -> None:
    write_text_atomic(path, dumps(obj))


def append_jsonl(path: str, row: Dict[str, Any]) -> None:
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    text = read_text(path)
    if not text:
        return rows
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def sha256_file(path: str) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return None


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def touch(path: str) -> None:
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "a", encoding="utf-8"):
        pass
    os.utime(path, None)


def rm(path: str) -> None:
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


def exists(path: str) -> bool:
    return os.path.exists(path)


def file_age_s(path: str) -> Optional[float]:
    try:
        return time.time() - os.path.getmtime(path)
    except OSError:
        return None


# --------------------------------------------------------------------------- #
# Loaders
# --------------------------------------------------------------------------- #
def load_status(paths: Paths) -> Dict[str, Any]:
    st = read_json(paths.status)
    if not isinstance(st, dict):
        raise ForgeError(f"{paths.status}: missing or not an object", EXIT_INVALID)
    return st


def load_binding(paths: Paths) -> Dict[str, Any]:
    b = read_json(paths.binding)
    if not isinstance(b, dict):
        raise ForgeError(f"{paths.binding}: missing or not an object", EXIT_INVALID)
    return b


def load_routing(paths: Paths) -> Dict[str, Any]:
    r = read_json(paths.routing)
    if not isinstance(r, dict):
        raise ForgeError(f"{paths.routing}: missing routing data", EXIT_INVALID)
    return r


def current_task(status: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    t = status.get("task")
    return t if isinstance(t, dict) else None


def find_step(task: Dict[str, Any], step_id: str) -> Optional[Dict[str, Any]]:
    for s in task.get("steps", []) or []:
        if s.get("id") == step_id:
            return s
    return None


# --------------------------------------------------------------------------- #
# Session, runtime markers, journal, ledger, evidence
# --------------------------------------------------------------------------- #
def session_id(paths: Paths) -> str:
    sid = read_text(paths.rt("session-id"))
    sid = (sid or "").strip()
    return sid or "cli"


def journal(paths: Paths, task_id: Optional[str], message: str) -> None:
    """Append one timestamped line to the task journal (or the runtime log when no task)."""
    path = paths.journal_file(task_id)
    ensure_dir(os.path.dirname(path))
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"- {now_iso()} {message}\n")


def ledger(paths: Paths, row: Dict[str, Any]) -> None:
    r = {"ts": now_iso()}
    r.update(row)
    append_jsonl(paths.ledger, r)


def evidence_append(paths: Paths, task_id: str, row: Dict[str, Any]) -> None:
    r = {"ts": now_ts()}
    r.update(row)
    append_jsonl(paths.evidence(task_id), r)


def evidence_rows(paths: Paths, task_id: str, agent_id: Optional[str] = None,
                  event: Optional[Iterable[str]] = None) -> List[Dict[str, Any]]:
    rows = read_jsonl(paths.evidence(task_id))
    if agent_id is not None:
        rows = [r for r in rows if r.get("agent_id") == agent_id]
    if event is not None:
        ev = set(event)
        rows = [r for r in rows if r.get("event") in ev]
    return rows


def edit_kind(paths: Paths, path: str) -> str:
    rel = paths.rel(path)
    if rel in META_FILES or any(rel.startswith(p) for p in META_PREFIXES):
        return "meta"
    return "source"


# --------------------------------------------------------------------------- #
# Globs, aliases, roles
# --------------------------------------------------------------------------- #
def glob_to_regex(glob: str) -> str:
    """Translate a Forge glob to an anchored regex.
    **/ -> (.*/)?   ** -> .*   * -> [^/]*   ? -> [^/]   . escaped.
    A glob without a slash and without ** matches a basename anywhere? No: Forge globs are
    repo-relative paths; a bare `file.py` matches only `file.py`. Use `**/file.py` for anywhere.
    """
    out = []
    i = 0
    g = glob.replace(os.sep, "/")
    if g.startswith("./"):
        g = g[2:]
    while i < len(g):
        c = g[i]
        if g.startswith("**/", i):
            out.append("(.*/)?")
            i += 3
            continue
        if g.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        if c == "*":
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        elif c in ".+()[]{}^$|\\":
            out.append("\\" + c)
        else:
            out.append(c)
        i += 1
    return "^" + "".join(out) + "$"


_GLOB_CACHE: Dict[str, "re.Pattern[str]"] = {}


def glob_match(path: str, glob: str) -> bool:
    """True when repo-relative `path` matches `glob`. A glob ending in '/' or naming a
    directory prefix (e.g. 'layers/mvum/**') also matches files below it."""
    p = path.replace(os.sep, "/")
    if p.startswith("./"):
        p = p[2:]
    g = glob
    if g.endswith("/"):
        g = g + "**"
    rx = _GLOB_CACHE.get(g)
    if rx is None:
        rx = re.compile(glob_to_regex(g))
        _GLOB_CACHE[g] = rx
    if rx.match(p):
        return True
    # a plain directory glob like "layers/mvum" should match "layers/mvum/x.py"
    if "*" not in g and "?" not in g and p.startswith(g.rstrip("/") + "/"):
        return True
    return False


def any_glob(path: str, globs: Iterable[str]) -> Optional[str]:
    for g in globs or []:
        if glob_match(path, g):
            return g
    return None


def alias_model(model: Optional[str]) -> Optional[str]:
    """Normalise a model id or alias to one of haiku|sonnet|opus|fable (else lowercased input)."""
    if not model:
        return None
    m = str(model).strip().lower()
    m = re.sub(r"\[1m\]$", "", m)
    for key in ("fable", "mythos", "opus", "sonnet", "haiku"):
        if key in m:
            return "fable" if key == "mythos" else key
    if m in ("best",):
        return "fable"
    if m in ("default",):
        return "opus"
    return m


def agent_role(agent_type: Optional[str]) -> Optional[str]:
    """Strip a plugin namespace ('forge:forge-builder' -> 'forge-builder')."""
    if not agent_type:
        return None
    a = str(agent_type)
    if ":" in a:
        a = a.rsplit(":", 1)[1]
    return a


def tier_gte(a: str, b: str) -> bool:
    return TIER_ORDER.get(alias_model(a) or "", -1) >= TIER_ORDER.get(alias_model(b) or "", -1)


def next_tier(model: str, effort: str) -> Tuple[str, str]:
    """One rung up the ladder: sonnet -> opus -> fable/low -> fable/medium (effort then model)."""
    m = alias_model(model) or "opus"
    if m == "fable":
        return "fable", "medium" if EFFORT_ORDER.get(effort, 0) < 1 else effort
    order = ["haiku", "sonnet", "opus", "fable"]
    nxt = order[min(order.index(m) + 1, len(order) - 1)]
    return nxt, "low" if nxt == "fable" else "medium"


# --------------------------------------------------------------------------- #
# Markdown helpers
# --------------------------------------------------------------------------- #
_FENCE_RE = re.compile(r"^```json\s*$")


def json_block(text: str) -> Optional[Dict[str, Any]]:
    """Return the first fenced ```json block in `text` parsed, or None."""
    lines = text.splitlines()
    buf: List[str] = []
    inside = False
    for line in lines:
        if not inside:
            if _FENCE_RE.match(line.strip()):
                inside = True
                buf = []
            continue
        if line.strip().startswith("```"):
            try:
                obj = json.loads("\n".join(buf))
            except json.JSONDecodeError:
                return None
            return obj if isinstance(obj, dict) else None
        buf.append(line)
    return None


def headings(text: str, level: int = 2) -> List[str]:
    """All headings of exactly `level` (## by default), stripped."""
    prefix = "#" * level + " "
    out = []
    for line in text.splitlines():
        s = line.rstrip()
        if s.startswith(prefix) and not s.startswith("#" * (level + 1) + " "):
            out.append(s[len(prefix):].strip())
    return out


def section(text: str, heading: str, level: int = 2) -> str:
    """Body of the `## heading` section (until the next heading of the same or higher level)."""
    prefix = "#" * level + " "
    lines = text.splitlines()
    out: List[str] = []
    inside = False
    for line in lines:
        s = line.rstrip()
        if s.startswith("#"):
            m = re.match(r"^(#+)\s+(.*)$", s)
            if m:
                lvl = len(m.group(1))
                title = m.group(2).strip()
                if inside and lvl <= level:
                    break
                if lvl == level and title.lower() == heading.lower():
                    inside = True
                    continue
        if inside:
            out.append(line)
    return "\n".join(out).strip()


def render_template(text: str, mapping: Dict[str, Any]) -> str:
    """Replace {{key}} placeholders; unknown keys are left in place."""
    def repl(m: "re.Match[str]") -> str:
        k = m.group(1).strip()
        return str(mapping[k]) if k in mapping else m.group(0)
    return re.sub(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}", repl, text)


def truncate(text: str, limit: int, marker: str = "\n[truncated]") -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - len(marker))] + marker


# --------------------------------------------------------------------------- #
# Subprocess and git
# --------------------------------------------------------------------------- #
def run(cmd: str, cwd: Optional[str] = None, timeout: int = 1200,
        env: Optional[Dict[str, str]] = None) -> Tuple[int, str]:
    """Run `cmd` through bash from `cwd`; return (exit code, combined output)."""
    try:
        r = subprocess.run(["bash", "-lc", cmd] if False else ["bash", "-c", cmd], cwd=cwd,
                           capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") if isinstance(e.stdout, str) else ""
        return 124, out + f"\n[forge: timed out after {timeout}s]"
    except OSError as e:
        return 127, f"[forge: cannot run: {e}]"
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def git(args: List[str], cwd: str, timeout: int = 60) -> Tuple[int, str]:
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as e:
        return 127, str(e)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def git_head(cwd: str) -> Optional[str]:
    code, out = git(["rev-parse", "HEAD"], cwd)
    return out.strip() if code == 0 and out.strip() else None


def git_porcelain(cwd: str, pathspecs: Optional[List[str]] = None, untracked: bool = True) -> List[str]:
    """Repo-relative paths from `git status --porcelain` (optionally limited to pathspecs)."""
    args = ["status", "--porcelain", "--untracked-files=all" if untracked else "--untracked-files=no"]
    if pathspecs:
        args += ["--"] + list(pathspecs)
    code, out = git(args, cwd)
    if code != 0:
        return []
    paths: List[str] = []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        p = line[3:]
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        paths.append(p.strip().strip('"'))
    return paths


def git_diff_names(cwd: str, base: str, head: str = "HEAD") -> List[str]:
    code, out = git(["diff", "--name-only", f"{base}..{head}"], cwd)
    if code != 0:
        return []
    return [l.strip() for l in out.splitlines() if l.strip()]


def git_is_ancestor(cwd: str, ancestor: str, descendant: str) -> bool:
    code, _ = git(["merge-base", "--is-ancestor", ancestor, descendant], cwd)
    return code == 0


# --------------------------------------------------------------------------- #
# Hook I/O
# --------------------------------------------------------------------------- #
def read_stdin_json() -> Dict[str, Any]:
    try:
        data = sys.stdin.read()
    except Exception:
        return {}
    data = (data or "").strip()
    if not data:
        return {}
    try:
        obj = json.loads(data)
    except json.JSONDecodeError:
        return {}
    return obj if isinstance(obj, dict) else {}


def emit(obj: Optional[Dict[str, Any]]) -> None:
    """Print exactly one JSON object to stdout (or nothing)."""
    if obj:
        sys.stdout.write(json.dumps(obj, ensure_ascii=False))
        sys.stdout.flush()


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


# --------------------------------------------------------------------------- #
# Misc
# --------------------------------------------------------------------------- #
def dirs_of(paths_list: Iterable[str]) -> List[str]:
    return sorted({os.path.dirname(p) or "." for p in paths_list})


def unique(seq: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for s in seq:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def word_hits(title: str, risk_words: Iterable[Any]) -> List[str]:
    """Risk-word matches in a title. Words >= 4 chars match case-insensitively on word
    boundaries; shorter words match case-sensitively. Each entry may carry `not: [...]`
    exclusions (phrases that, when present, cancel the hit)."""
    hits: List[str] = []
    for entry in risk_words or []:
        if isinstance(entry, str):
            word, nots = entry, []
        else:
            word, nots = entry.get("word", ""), entry.get("not", []) or []
        if not word:
            continue
        flags = re.IGNORECASE if len(word) >= 4 else 0
        if re.search(r"\b" + re.escape(word) + r"\b", title, flags):
            cancelled = False
            for n in nots:
                if re.search(r"\b" + re.escape(n) + r"\b", title, re.IGNORECASE):
                    cancelled = True
                    break
            if not cancelled:
                hits.append(word)
    return hits


def next_task_id(paths: Paths) -> str:
    """Allocate the next T-NNNN from tasks/, archive/ and history."""
    n = 0
    for d in (paths.tasks, paths.archive):
        if os.path.isdir(d):
            for name in os.listdir(d):
                m = re.match(r"^T-(\d{4,})$", name)
                if m:
                    n = max(n, int(m.group(1)))
    for row in read_jsonl(paths.history):
        m = re.match(r"^T-(\d{4,})$", str(row.get("id", "")))
        if m:
            n = max(n, int(m.group(1)))
    return f"T-{n + 1:04d}"
