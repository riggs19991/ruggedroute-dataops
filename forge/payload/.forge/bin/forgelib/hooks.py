"""forgelib.hooks — the `forge-hook` dispatcher (MODULE-API §6; design §13.3, §3, §6, §7).

One executable (`.forge/bin/forge-hook`) serves every hook registration in
`.claude/settings.forge.json`. It reads stdin once, dispatches on `hook_event_name`
(+ `tool_name`), prints at most one JSON object and always exits 0.

Failure policy (design §6 layer 2, §13.3): a crash inside a `PreToolUse` or
`SubagentStop` handler becomes a deny / block naming the exception (fail closed);
every other event fails open with a `systemMessage`.

`forgelib.status` and `forgelib.gates` are imported lazily inside the handlers that
need them, and only through the functions MODULE-API §3-§5 define, so a broken sibling
module can break only the handlers that depend on it, never the whole dispatcher.
"""
from __future__ import annotations

import json
import os
import re
import traceback
from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import common

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
CHECK_STAMP_WINDOW_S = 300          # design §5.7: stamp `unknown` records created within 300 s
ROLE_MAX_CHARS = 4000               # design §13.3: ROLE-architect.md ≤ 4,000 chars
LESSONS_HEAD_LINES = 40             # design §6 layer 4: first 40 lines of lessons/INDEX.md
GIT_STATUS_LINES = 20               # design §6 layer 4: git status --short | head -20
GIT_LOG_LINES = 5                   # design §6 layer 4: git log --oneline -5
REMINDER_NEXT_CHARS = 120           # design §13.3 UserPromptSubmit: next_action cut at 120 chars
DENIAL_CAP = 3                      # design §3 step 2: the third same-rule denial in a turn ends it
PLAN_FILE_MARKER = "PLAN-FILE:"     # design §13.3: the planner's final message ends with it
RESUME_MESSAGE = "Resume from .forge/STATUS.json: read it, then execute next_action."
# Review-2 #3: the CLEAR POINT after `close` is idle (task null, context_state stale); a queued task resumes with this.
RESUME_IDLE_MESSAGE = "Resume from .forge/STATUS.json: start the first queued task with /forge-task"
WORKER_START_LINE = ("Forge worker: read the brief named in your prompt with the Read tool first; your final "
                     "message must follow the brief's Output contract (builders) or the VERDICT format "
                     "(verifier); run commands from the repository root; a hook refuses otherwise.")
STOP_ALLOW_PHASES = ("done", "blocked", "idle", "awaiting_external")   # design §3 step 12
# forge-status subcommands that only read STATUS (design §13.3 Bash row). A subagent's shell may run `get` only
# (review #6); `validate` without --restamp is a read for the main-session mutation guard.
STATUS_READ_SUBCOMMANDS = ("get", "validate")
# Main-session meta allow-list (design §13.3 Edit row): common.ARCHITECT_META_ALLOW plus agent memory
# and project-owned rule files.
MAIN_META_ALLOW = common.ARCHITECT_META_ALLOW + (".claude/agent-memory/",)
MAIN_META_GLOBS = (".claude/rules/project-*.md",)
LIBRARIAN_ALLOW = (".forge/lessons/", ".forge/COST-REPORT.md", ".forge/archive/", ".forge/decisions/",
                   "CLAUDE.md", ".claude/agent-memory/")
VERIFIER_MEMORY = ".claude/agent-memory/forge-verifier/"
# Directories a worker may `rm -r` under (design §3 step 7: /tmp and the scratchpad).
RM_SAFE_DIRS = ("/tmp",)
# Review #21: a spawn-guard dispatch marker (`.runtime/dispatched-<task>-<step>`) blocks a second builder for
# the same running-unbound step until the worker binds or the marker ages out.
DISPATCH_MARKER_TTL_S = 600
# Review #34: never store more than this many chars of a Bash command in evidence.
EVIDENCE_CMD_MAX_CHARS = 300
# Review #17: the sanctioned draft location for pre-validation (`forge-gate --from-file`), any forge-* subagent,
# bind-independent: `.forge/tasks/<id>/drafts/<agent_id>-*.md`.
_DRAFT_PATH_RE = re.compile(r"^\.forge/tasks/(T-\d{4,})/drafts/([^/]+?)-[^/]*\.md$")
_DRAFT_TOKEN_RE = re.compile(r"(^|/)\.forge/tasks/T-\d{4,}/drafts/[^/]+\.md$")
# Review #32: git subcommands a subagent may run (everything else is denied; name it in the HANDOFF).
GIT_WORKER_ALLOW = ("add", "commit", "status", "log", "diff", "show", "rev-parse", "ls-files", "blame", "grep",
                    "describe", "rev-list", "cat-file", "name-rev", "shortlog", "version", "help")
_GIT_GLOBAL_VALUE_OPTS = ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path")
# Review #6/#38: Forge scripts a subagent may never run, even through the exported PATH.
FORGE_DENIED_SCRIPTS = ("forge-doctor", "forge-run", "forge-bench", "forge-hook")
_FORGE_SCRIPT_RE = re.compile(r"^(\S*/)?\.forge/bin/(forge-[a-z-]+)$")
# A reference may sit inside a nested command string (`bash -c '… .forge/x'`) or a heredoc body, so the
# regexes accept any separator before the name, not only a path boundary.
_FORGE_REF_RE = re.compile(r"(^|[\s/'\"=(,;:])\.forge(/|$|[\s'\"),;:])")
_CLAUDE_REF_RE = re.compile(r"(^|[\s/'\"=(,;:])\.claude(/|$|[\s'\"),;:])")
_META_FILE_RE = re.compile(r"(^|[\s/'\"=(,;:])(CLAUDE\.md|\.gitignore)(?![A-Za-z0-9_])")
_BRIEF_TOKEN_RE = re.compile(r"(^|/)\.forge/tasks/T-\d{4,}/brief-\d{2}\.md$")
# Readers whose segment may name CLAUDE.md / .gitignore / .claude/** (a read, never a write).
META_READERS = ("cat", "head", "tail", "less", "more", "sed", "grep", "egrep", "rg", "wc", "diff", "stat", "file",
                "ls", "find", "git")
_SECRET_RE = re.compile(
    r"(?i)(authorization\s*[=:]\s*(?:bearer|basic|token)\s+|"
    r"(?:token|secret|password|passwd|api[_-]?key|authorization|bearer)\s*[=:]\s*|bearer\s+)(\S+)")
_SECRET_SHAPE_RE = re.compile(r"\b(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
                              r"sk-[A-Za-z0-9_-]{16,}|xox[baprs]-[A-Za-z0-9-]{10,})\b")
REDACTED = "[REDACTED]"

_BRIEF_PATH_RE = re.compile(r"\.forge/tasks/(T-\d{4,})/brief-(\d{2})\.md")
_BRIEF_READ_CMD_RE = re.compile(r"(^|[;&|]\s*)(cat|sed\s+-n|head|less)\s")
_FORGE_CHECK_RE = re.compile(r"forge-check\s+(T-\d{4,})\s+([A-Za-z0-9]+)")
_EXIT_TEXT_RE = re.compile(r"[Ee]xit code[: ]+(\d+)")
_FORGE_HOOK_CMD_RE = re.compile(r"forge-hook\b")


# --------------------------------------------------------------------------- #
# Redaction (review #34) and command tokenisation (reviews #6, #9, #32, #38)
# --------------------------------------------------------------------------- #
def redact(text: str) -> str:
    """Mask credential-shaped substrings (`token=…`, `Authorization: Bearer …`, AKIA…, ghp_…, sk-…)."""
    if not text:
        return text
    out = _SECRET_RE.sub(lambda m: m.group(1) + REDACTED, text)
    return _SECRET_SHAPE_RE.sub(REDACTED, out)


def _segments(cmd: str) -> List[str]:
    """&&, ||, ;, | AND newline-separated segments (a newline is a separator too; review #8)."""
    from . import gates
    out: List[str] = []
    for line in (cmd or "").splitlines():
        out.extend(gates.split_segments(line))
    return out


def _tokens(seg: str) -> List[str]:
    """shlex tokens of one segment (plain split on unbalanced quotes), leading VAR=value assignments dropped."""
    import shlex
    try:
        toks = shlex.split(seg, posix=True)
    except ValueError:
        toks = seg.split()
    while toks and "=" in toks[0] and not toks[0].startswith("-") and not toks[0].startswith(("/", ".", "~")):
        toks.pop(0)
    return toks


def _command_word(toks: List[str]) -> str:
    """Basename of the command word (after env assignments and a leading `sudo`/`command`/`exec`/`nice`)."""
    i = 0
    while i < len(toks) and os.path.basename(toks[i]) in ("sudo", "command", "exec", "nice", "env", "nohup", "time", "timeout"):
        i += 1
        # `timeout <n>` and `nice -n <n>` carry a value; skip numeric / dashed arguments
        while i < len(toks) and (toks[i].startswith("-") or re.match(r"^[0-9]+[smhd]?$", toks[i])):
            i += 1
    return os.path.basename(toks[i]) if i < len(toks) else ""


def _strip_redirect(tok: str) -> str:
    """`>file`, `>>file`, `2>file`, `<file` -> `file`."""
    return re.sub(r"^[0-9]?(>>|>|<)", "", tok)


def _git_subcommand(toks: List[str]) -> Optional[str]:
    """The git subcommand of a `git …` segment after its global options (-C dir, -c k=v, --git-dir …), else None."""
    if _command_word(toks) != "git":
        return None
    i = toks.index(next(t for t in toks if os.path.basename(t) == "git")) + 1
    while i < len(toks):
        t = toks[i]
        if t in _GIT_GLOBAL_VALUE_OPTS:
            i += 2
            continue
        if any(t.startswith(o + "=") for o in _GIT_GLOBAL_VALUE_OPTS) or t.startswith("-"):
            i += 1
            continue
        return t
    return ""


def _path_like(tok: str) -> bool:
    t = _strip_redirect(tok)
    if not t or t.startswith("-") or "://" in t:
        return False
    return t.startswith(("/", "./", "../", "~", ".forge", ".claude")) or "/" in t or t in ("CLAUDE.md", ".gitignore")


# --------------------------------------------------------------------------- #
# Context
# --------------------------------------------------------------------------- #
class Ctx:
    """Everything a handler needs, built once per invocation (MODULE-API §6).

    `role` is `common.agent_role(agent_type)` (plugin prefix stripped), falling back to the
    agent record when stdin carries `agent_id` without `agent_type`. `status` is None when
    STATUS.json is missing or invalid (`status_error` says why); `binding` is {} when absent."""

    def __init__(self, stdin: Dict[str, Any], flags: set):
        self.stdin = stdin
        self.flags = flags
        self.paths = common.Paths()
        self.event = str(stdin.get("hook_event_name") or "")
        self.tool_name = str(stdin.get("tool_name") or "")
        ti = stdin.get("tool_input")
        self.tool_input: Dict[str, Any] = ti if isinstance(ti, dict) else {}
        self.agent_id: Optional[str] = str(stdin["agent_id"]) if stdin.get("agent_id") else None
        self.agent_type: Optional[str] = str(stdin["agent_type"]) if stdin.get("agent_type") else None
        self.role: Optional[str] = common.agent_role(self.agent_type)
        if self.role is None and self.agent_id:
            rec = _agent_record(self, self.agent_id)
            self.role = common.agent_role(rec.get("agent_type"))
        self.is_subagent = bool(self.agent_id or self.agent_type)
        sid = stdin.get("session_id")
        self.session_id = str(sid) if sid else common.session_id(self.paths)
        self.status: Optional[Dict[str, Any]] = None
        self.status_error: Optional[str] = None
        self.reload_status()
        try:
            self.binding: Dict[str, Any] = common.load_binding(self.paths)
        except common.ForgeError:
            self.binding = {}

    def reload_status(self) -> None:
        """Re-read STATUS.json after a forge-status call."""
        try:
            self.status = common.load_status(self.paths)
            self.status_error = None
        except common.ForgeError as e:
            self.status = None
            self.status_error = str(e)

    @property
    def task(self) -> Optional[Dict[str, Any]]:
        return common.current_task(self.status) if self.status else None

    @property
    def task_id(self) -> Optional[str]:
        t = self.task
        return str(t["id"]) if t and t.get("id") else None


# --------------------------------------------------------------------------- #
# Output shapes (MODULE-API §6)
# --------------------------------------------------------------------------- #
def _context(event: str, text: str, **extra: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {"hookEventName": event, "additionalContext": text}
    out.update(extra)
    return {"hookSpecificOutput": out}


def _deny(reason: str) -> Dict[str, Any]:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def _ask(reason: str) -> Dict[str, Any]:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                   "permissionDecisionReason": reason}}


def _block(reason: str) -> Dict[str, Any]:
    return {"decision": "block", "reason": reason}


def _system(message: str) -> Dict[str, Any]:
    return {"systemMessage": message}


# --------------------------------------------------------------------------- #
# Runtime markers, journal, agent records
# --------------------------------------------------------------------------- #
def _marker(ctx: Ctx, name: str) -> bool:
    return common.exists(ctx.paths.rt(name))


def _touch(ctx: Ctx, name: str) -> None:
    common.touch(ctx.paths.rt(name))


def _rm(ctx: Ctx, name: str) -> None:
    common.rm(ctx.paths.rt(name))


def _read_marker(ctx: Ctx, name: str) -> str:
    return (common.read_text(ctx.paths.rt(name)) or "").strip()


def _journal(ctx: Ctx, message: str, task_id: Optional[str] = None) -> None:
    """One journal line in the task journal (or the runtime log when no task is open)."""
    who = ctx.agent_id or "main"
    if not os.path.isdir(ctx.paths.forge):
        return   # review #37: never create .forge/ in a repository that has no Forge install
    try:
        common.journal(ctx.paths, task_id or ctx.task_id, f"[{ctx.event}] {who}: {redact(message)}")
    except OSError:
        pass


def _agent_record(ctx: Ctx, agent_id: Optional[str]) -> Dict[str, Any]:
    """`.runtime/agents/<agent_id>.json` or {} (MODULE-API §2.10)."""
    if not agent_id:
        return {}
    try:
        rec = common.read_json(ctx.paths.agent_record(agent_id), default=None)
    except common.ForgeError:
        return {}
    return rec if isinstance(rec, dict) else {}


def _merge_agent_record(ctx: Ctx, agent_id: str, **fields: Any) -> Dict[str, Any]:
    rec = _agent_record(ctx, agent_id)
    rec.setdefault("agent_id", agent_id)
    rec.update(fields)
    common.write_json_atomic(ctx.paths.agent_record(agent_id), rec)
    return rec


# --------------------------------------------------------------------------- #
# forge-status bridge (MODULE-API §3; imported lazily)
# --------------------------------------------------------------------------- #
def _status_call(ctx: Ctx, method: str, *args: Any, **kwargs: Any) -> Tuple[bool, Any]:
    """Call `Status(paths).<method>(*args, **kwargs)`.

    Returns (True, result) or (False, one-line message): a ForgeError refusal, or the module
    being unavailable. STATUS is re-read afterwards so later rules see the new state."""
    try:
        from . import status as _status
        api = _status.Status(ctx.paths)
        result = getattr(api, method)(*args, **kwargs)
        ok, msg = True, result
    except common.ForgeError as e:
        ok, msg = False, str(e)
    except Exception as e:  # module missing or crashing: report, never raise into a gate
        ok, msg = False, f"forge-status {method} unavailable ({type(e).__name__}: {e})"
    ctx.reload_status()
    return ok, msg


# --------------------------------------------------------------------------- #
# Small helpers shared by handlers
# --------------------------------------------------------------------------- #
def _steps(task: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [s for s in (task or {}).get("steps", []) or [] if isinstance(s, dict)]


def _steps_with(task: Optional[Dict[str, Any]], *statuses: str) -> List[Dict[str, Any]]:
    return [s for s in _steps(task) if s.get("status") in statuses]


def _str_list(v: Any) -> List[str]:
    return [x for x in (v or []) if isinstance(x, str)] if isinstance(v, list) else []


def _verify_prefixes(ctx: Ctx) -> List[str]:
    """binding.verify[].cmd (used as prefixes by ro_allowed / looks_mutating)."""
    out = []
    for v in ctx.binding.get("verify", []) or []:
        if isinstance(v, dict) and isinstance(v.get("cmd"), str) and v["cmd"].strip():
            out.append(v["cmd"])
    return out


def _safe_prefixes(ctx: Ctx) -> List[str]:
    """verify[].cmd ∪ bootstrap ∪ smoke: commands exempt from the main-session mutation heuristic."""
    out = _verify_prefixes(ctx)
    for key in ("bootstrap", "smoke"):
        v = ctx.binding.get(key)
        if isinstance(v, str) and v.strip():
            out.append(v)
    return out


def _tool_calls(ctx: Ctx, task_id: str, agent_id: str) -> int:
    """Tool calls of this agent (design §7 gate 2b): the hook-owned counter in `.runtime/agents/<id>.json`
    (incremented by _record_bash/_record_edit; review #6), falling back to bash|edit evidence rows when the
    record is missing. The larger of the two wins, so a worker can never lower it by editing evidence."""
    rec = _agent_record(ctx, agent_id)
    counted = rec.get("tool_calls")
    rows = len(common.evidence_rows(ctx.paths, task_id, agent_id=agent_id, event=("bash", "edit")))
    if isinstance(counted, int) and not isinstance(counted, bool):
        return max(int(counted), rows)
    return rows


def _count_tool_call(ctx: Ctx) -> None:
    """Increment the hook-owned tool-call counter of a subagent (review #6)."""
    if not ctx.agent_id:
        return
    rec = _agent_record(ctx, ctx.agent_id)
    n = rec.get("tool_calls")
    n = int(n) if isinstance(n, int) and not isinstance(n, bool) else 0
    _merge_agent_record(ctx, ctx.agent_id, tool_calls=n + 1)


def _budget_cap(ctx: Ctx, brief: Optional[Dict[str, Any]]) -> int:
    """brief.max_tool_calls, else the role default."""
    if brief and isinstance(brief.get("max_tool_calls"), int) and not isinstance(brief.get("max_tool_calls"), bool):
        return int(brief["max_tool_calls"])
    return common.WIDE_TOOL_BUDGET_DEFAULT if ctx.role == "forge-builder-wide" else common.TOOL_BUDGET_DEFAULT


def _budget_exhausted(ctx: Ctx) -> Optional[str]:
    """Denial reason when this worker's tool budget is spent, else None (design §7 gate 2b)."""
    if not ctx.agent_id:
        return None
    rec = _agent_record(ctx, ctx.agent_id)
    task_id = rec.get("task") or ctx.task_id
    if not task_id:
        return None
    brief = None
    if rec.get("step"):
        from . import gates
        brief = gates.brief_meta(ctx.paths, str(task_id), str(rec["step"]))
    cap = _budget_cap(ctx, brief)
    used = _tool_calls(ctx, str(task_id), ctx.agent_id)
    if used >= cap:
        return f"tool budget exhausted ({used}/{cap} tool calls): write your HANDOFF with status BLOCKED"
    return None


def _evidence_task_id(ctx: Ctx) -> Optional[str]:
    """Task whose evidence.jsonl receives this event: the bound task for a worker, else the open task."""
    if ctx.is_subagent and ctx.agent_id:
        rec = _agent_record(ctx, ctx.agent_id)
        if rec.get("task"):
            return str(rec["task"])
    return ctx.task_id


def _count_denial(ctx: Ctx, rule: str) -> int:
    """Increment `.runtime/denials[rule]` for this turn and return the new count."""
    path = ctx.paths.rt("denials")
    try:
        counts = common.read_json(path, default={})
    except common.ForgeError:
        counts = {}
    if not isinstance(counts, dict):
        counts = {}
    counts[rule] = int(counts.get(rule, 0) or 0) + 1
    common.write_json_atomic(path, counts)
    return counts[rule]


def _fence_deny(ctx: Ctx, rule: str, reason: str) -> Dict[str, Any]:
    """Main-session denial with the per-turn counter (design §3 step 2, §16 #74).

    Subagent denials are not counted: a worker's turn is its whole life."""
    _journal(ctx, f"fence deny [{rule}]: {reason}")
    out = _deny(reason)
    if ctx.is_subagent:
        return out
    n = _count_denial(ctx, rule)
    if n >= DENIAL_CAP:
        out["continue"] = False
        out["stopReason"] = f"Fence: {rule}. Run /forge-next."
    return out


# --------------------------------------------------------------------------- #
# Policy lock (design §7 gate 14)
# --------------------------------------------------------------------------- #
def _manifest_paths(ctx: Ctx) -> List[str]:
    """Paths listed by install-manifest.json (any of the shapes an installer might write)."""
    try:
        m = common.read_json(ctx.paths.manifest, default=None)
    except common.ForgeError:
        return []
    files: Any = m.get("files", m) if isinstance(m, dict) else m
    out: List[str] = []
    if isinstance(files, dict):
        out = [str(k) for k in files.keys()]
    elif isinstance(files, list):
        for f in files:
            if isinstance(f, str):
                out.append(f)
            elif isinstance(f, dict) and f.get("path"):
                out.append(str(f["path"]))
    return [ctx.paths.rel(p) for p in out]


def _policy_locked(ctx: Ctx, rel: str) -> bool:
    if rel in common.POLICY_LOCK_FILES:
        return True
    if any(rel.startswith(p) for p in common.POLICY_LOCK_PREFIXES):
        return True
    return rel in _manifest_paths(ctx)


def _main_meta_allowed(ctx: Ctx, rel: str) -> Tuple[bool, Optional[str]]:
    """(allowed, deny reason) for the architect's always-editable meta paths (design §13.3 Edit row).

    `.forge/tasks/<id>/**` is allowed for the OPEN task only (review #49); another task's directory
    returns a deny reason. (False, None) means "not a meta path: apply the fence"."""
    if rel.startswith(".forge/tasks/"):
        tid = ctx.task_id
        if tid and rel.startswith(f".forge/tasks/{tid}/"):
            return True, None
        return False, f"{rel} is not under the open task's directory (.forge/tasks/{tid or '<none open>'}/): not the open task"
    for p in MAIN_META_ALLOW:
        if p.endswith("/"):
            if rel.startswith(p):
                return True, None
        elif rel == p:
            return True, None
    return common.any_glob(rel, MAIN_META_GLOBS) is not None, None


# --------------------------------------------------------------------------- #
# Brief binding (MODULE-API §2.11; design §3 step 6)
# --------------------------------------------------------------------------- #
def _maybe_bind(ctx: Ctx, rel: str) -> None:
    """Bind this worker to the brief at `rel` when the step is running, unbound and owned by its role."""
    m = _BRIEF_PATH_RE.search(rel)
    if not m or not ctx.agent_id:
        return
    task_id, step_id = m.group(1), m.group(2)
    task = ctx.task
    if not task or task.get("id") != task_id:
        _journal(ctx, f"read brief {rel} of a task that is not open; no bind", task_id)
        return
    step = common.find_step(task, step_id)
    if not step or step.get("status") != "running" or step.get("agent_id") is not None:
        _journal(ctx, f"read brief {rel}: step not running/unbound; no bind", task_id)
        return
    from . import gates
    bm = gates.brief_meta(ctx.paths, task_id, step_id) or {}
    if bm.get("owner_agent") != ctx.role:
        _journal(ctx, f"read brief {rel}: owner_agent {bm.get('owner_agent')!r} != {ctx.role!r}; no bind", task_id)
        return
    ok, msg = _status_call(ctx, "step_bind", task_id, step_id, ctx.agent_id)
    if not ok:
        _journal(ctx, f"step-bind {task_id}/{step_id} refused: {msg}", task_id)
        return
    _merge_agent_record(ctx, ctx.agent_id, agent_type=ctx.agent_type or ctx.role, task=task_id, step=step_id,
                        brief=rel, bound_at=common.now_iso())
    _rm(ctx, _dispatch_marker(task_id, step_id))   # review #21: the dispatched worker has arrived
    _journal(ctx, f"bound {ctx.agent_id} ({ctx.role}) to {task_id}/{step_id}", task_id)


def _dispatch_marker(task_id: str, step_id: str) -> str:
    return f"dispatched-{task_id}-{step_id}"


# --------------------------------------------------------------------------- #
# SessionStart (design §3 step 0, §6 layers 4-5, §13.3)
# --------------------------------------------------------------------------- #
def on_session_start(ctx: Ctx) -> Optional[Dict[str, Any]]:
    """Handler 1: session markers, env exports, banner, digest, auto-resume on `clear`."""
    if "role" in ctx.flags:
        return on_session_start_role(ctx)
    if ctx.agent_type:
        return None   # design §2: workers never receive the digest
    paths = ctx.paths
    source = str(ctx.stdin.get("source") or "startup")
    common.ensure_dir(paths.runtime)
    common.write_text_atomic(paths.rt("session-id"), ctx.session_id + "\n")
    common.write_json_atomic(paths.rt("hooks-alive"), {"session_id": ctx.session_id, "ts": common.now_ts(),
                                                      "source": source})
    _export_env(ctx)
    banner = _banner(ctx)          # design §3 step 0: computed before any STATUS write
    items = [
        (_digest(ctx), paths.rel(paths.status)),
        (banner, paths.rel(paths.status)),
        (_handoff_sections(ctx), None),
        (_git_state(ctx), None),
        (_lessons_head(ctx), paths.rel(paths.lessons_index)),
        (_binding_digest(ctx), paths.rel(paths.binding)),
        (_version_drift(ctx), paths.rel(paths.version_file)),
    ]
    text = _fit(items, common.MAX_ADDITIONAL_CONTEXT)
    extra: Dict[str, Any] = {"sessionTitle": _session_title(ctx)}
    if source == "clear":
        msg = _auto_resume(ctx)
        if msg:
            extra["initialUserMessage"] = msg
        elif ctx.status is not None and ctx.task is None and ctx.status.get("context_state") == "stale":
            # review #52: /clear after a close with an empty queue (or auto_resume off) resets the stale flag
            # without a message (RUNBOOK §6); a queued task resumed above (review-2 #3).
            ok, why = _status_call(ctx, "fresh", stamp=False)
            _journal(ctx, f"clear while idle and stale; fresh --no-stamp {'ok' if ok else 'failed: ' + str(why)}")
    _journal(ctx, f"session start ({source}) session {ctx.session_id}")
    return _context("SessionStart", text, **extra)


def on_session_start_role(ctx: Ctx) -> Optional[Dict[str, Any]]:
    """Handler 2 (`--role`): the architect role block, main session only (design §13.8)."""
    if ctx.agent_type:
        return None
    text = common.read_text(ctx.paths.role_md)
    if not text:
        _journal(ctx, f"{ctx.paths.rel(ctx.paths.role_md)} missing; no role block injected")
        return None
    return _context("SessionStart", common.truncate(text.strip(), ROLE_MAX_CHARS))


def _export_env(ctx: Ctx) -> None:
    """Writes nothing to CLAUDE_ENV_FILE: no PATH and no FORGE_ROOT export (MODULE-API §9.3; review #3, observed
    in the field). An export written to CLAUDE_ENV_FILE outlives the session that wrote it and leaks another
    checkout's .forge/bin and root into every later shell. Every prompt names scripts by their full .forge/bin/
    path, and forge_root() derives the root from CLAUDE_PROJECT_DIR/cwd first (a FORGE_ROOT naming a different
    repository is ignored with a WARN), so no export is needed. Kept as the one place that decision lives."""
    return


def _evidence_after(ctx: Ctx, task_id: str, ts: int) -> bool:
    rows = common.evidence_rows(ctx.paths, task_id)
    return any(isinstance(r.get("ts"), int) and r["ts"] > ts for r in rows)


def _banner(ctx: Ctx) -> str:
    """INTERRUPTED / STALE lines (design §3 step 0, §6 failure table)."""
    lines: List[str] = []
    task = ctx.task
    if task:
        tid = task.get("id")
        for s in _steps_with(task, "running"):
            sid, by, at = s.get("id"), s.get("started_by"), s.get("started_at")
            if not s.get("report") and by and by != ctx.session_id:
                lines.append(f"INTERRUPTED: step {sid} is running (started by session {by} at {at}) with no report. "
                             f"Follow resume_hint; `.forge/bin/forge-status recover {tid} {sid}` if that worker is gone.")
            elif s.get("agent_id") is None and not _evidence_after(ctx, str(tid), int(s.get("started_ts") or 0)):
                # Review-2 #9: name commands that work on a running step. step-start refuses a running step, and
                # plain recover refuses a step this session started (RUNBOOK §5 step 2: --force then).
                force = " --force" if by == ctx.session_id else ""
                lines.append(f"INTERRUPTED: step {sid} is running with no bound worker and no tool evidence since {at}; "
                             f"the Agent call may have failed. Run `.forge/bin/forge-status recover {tid} {sid}{force}` "
                             f"(it leaves the step pending), then re-dispatch per next_action (the dispatch runs "
                             f"step-start itself).")
    if _marker(ctx, "stale-status"):
        lines.append("STALE: a previous turn ended without STATUS.json being updated (.runtime/stale-status). "
                     "Verify STATUS against `git status` and the task directory before acting.")
    if ctx.status_error:
        lines.append(f"INVALID: {ctx.status_error}; run .forge/bin/forge-status validate")
    return "\n".join(lines)


def _digest(ctx: Ctx) -> str:
    """`forge-status get digest` (≤ MAX_DIGEST), falling back to a local rendering."""
    ok, text = _status_call(ctx, "get", "digest", lenient=True)
    if not ok or not isinstance(text, str) or not text.strip():
        text = _local_digest(ctx)
    return common.truncate(text.strip(), common.MAX_DIGEST)


def _local_digest(ctx: Ctx) -> str:
    """The MODULE-API §3 digest format rendered from STATUS directly (used when forgelib.status is unavailable)."""
    st = ctx.status
    if not st:
        return f"STATUS unavailable: {ctx.status_error or 'missing'}\n[full: .forge/STATUS.json]"
    task = common.current_task(st)
    lines: List[str] = []
    if task:
        lines.append(f'{task.get("id")} "{task.get("title", "")}" class {task.get("class")} risk {task.get("risk")} '
                     f'phase {task.get("phase")} mode {(task.get("routing") or {}).get("mode")}')
        for s in _steps(task):
            commit = (s.get("commit") or "")[:7] or "-"
            lines.append(f'{s.get("id")} {s.get("status")} {s.get("agent")}/{s.get("model")}/{s.get("effort")} '
                         f'attempts={s.get("attempts", 0)} commit={commit}')
        lines.append(f'next: {task.get("next_action") or "-"}')
        if task.get("resume_hint"):
            lines.append(f'resume_hint: {task["resume_hint"]}')
        if task.get("blocked_on"):
            lines.append(f'blocked_on: {task["blocked_on"]}')
        if task.get("external"):
            lines.append(f'external: {json.dumps(task["external"], ensure_ascii=False)}')
        ev = task.get("evidence") or []
        newest = "; ".join(f'{e.get("claim")} (exit {e.get("exit")})' for e in ev[-2:] if isinstance(e, dict))
        lines.append(f'evidence: {task.get("evidence_count", len(ev))}' + (f" (newest 2: {newest})" if newest else ""))
    else:
        lines.append("idle (no task open)")
    queue = [q.get("id") for q in st.get("queue", []) or [] if isinstance(q, dict)]
    if queue:
        lines.append("queue: " + " ".join(str(q) for q in queue[:10]))
    hist = [f'"{h.get("id")} {h.get("outcome")}"' for h in (st.get("history", []) or [])[-5:] if isinstance(h, dict)]
    if hist:
        lines.append("history: " + " ".join(hist))
    lines.append("[full: .forge/STATUS.json]")
    return "\n".join(lines)


def _newest_handoff_file(ctx: Ctx) -> Optional[str]:
    """Newest handoff.md / report-NN.md of the open task (else of the last closed task)."""
    task_dirs: List[str] = []
    if ctx.task_id:
        task_dirs.append(ctx.paths.task(ctx.task_id))
    for h in reversed((ctx.status or {}).get("history", []) or []):
        if isinstance(h, dict) and h.get("handoff"):
            task_dirs.append(os.path.dirname(os.path.join(ctx.paths.root, str(h["handoff"]))))
            break
    best: Optional[Tuple[float, str]] = None
    for d in task_dirs:
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if name == "handoff.md" or (name.startswith("report-") and name.endswith(".md")):
                p = os.path.join(d, name)
                try:
                    mt = os.path.getmtime(p)
                except OSError:
                    continue
                if best is None or mt > best[0]:
                    best = (mt, p)
        if best:
            break
    return best[1] if best else None


def _handoff_sections(ctx: Ctx) -> str:
    """*Remaining* and *Gotchas / do not touch* of the newest handoff (design §6 layer 4)."""
    path = _newest_handoff_file(ctx)
    if not path:
        return ""
    text = common.read_text(path) or ""
    out = [f"From {ctx.paths.rel(path)}:"]
    for h in ("Remaining", "Gotchas / do not touch"):
        body = common.section(text, h)
        if body:
            out.append(f"## {h}\n{body}")
    return "\n".join(out) if len(out) > 1 else ""


def _git_state(ctx: Ctx) -> str:
    code, out = common.git(["status", "--short"], ctx.paths.root)
    lines = out.splitlines()[:GIT_STATUS_LINES] if code == 0 else [f"(git status failed: {out.strip()[:120]})"]
    code2, log = common.git(["log", "--oneline", f"-{GIT_LOG_LINES}"], ctx.paths.root)
    log_lines = log.splitlines() if code2 == 0 else ["(no commits)"]
    return "git status --short:\n" + ("\n".join(lines) or "(clean)") + "\ngit log --oneline -5:\n" + "\n".join(log_lines)


def _lessons_head(ctx: Ctx) -> str:
    text = common.read_text(ctx.paths.lessons_index)
    if not text:
        return ""
    return "lessons/INDEX.md:\n" + "\n".join(text.splitlines()[:LESSONS_HEAD_LINES])


def _binding_digest(ctx: Ctx) -> str:
    b = ctx.binding
    if not b:
        return "binding: .forge/binding.json missing or invalid"
    names = [str(v.get("name")) for v in b.get("verify", []) or [] if isinstance(v, dict)]
    parts = [f"binding {b.get('project')!s} ({b.get('stack')}): verify={names}",
             f"protected={_str_list(b.get('protected_paths'))} risk={_str_list(b.get('risk_paths'))} "
             f"important={_str_list(b.get('important_paths'))}",
             f"clear_policy={b.get('clear_policy')} auto_resume={b.get('auto_resume')}"]
    notes = _str_list(b.get("notes"))
    if notes:
        parts.append("notes:\n" + "\n".join(f"- {n}" for n in notes))
    return "\n".join(parts)


def _version_drift(ctx: Ctx) -> str:
    installed = (common.read_text(ctx.paths.version_file) or "").strip()
    lines: List[str] = []
    if installed and installed != common.FORGE_VERSION:
        lines.append(f"VERSION drift: .forge/VERSION {installed} vs forgelib {common.FORGE_VERSION}")
    src = (common.read_text(os.path.join(ctx.paths.root, "forge", "VERSION")) or "").strip()
    if src and installed and src != installed:
        lines.append(f"VERSION drift: .forge/VERSION {installed} vs source tree forge/VERSION {src}; run install.sh --upgrade")
    pin = ctx.binding.get("forge_pin")
    if isinstance(pin, str) and installed and pin != installed:
        lines.append(f"VERSION drift: .forge/VERSION {installed} lags binding.forge_pin {pin}")
    return "\n".join(lines)


def _fit(items: List[Tuple[str, Optional[str]]], limit: int) -> str:
    """Join non-empty items with blank lines, truncating later items first to stay within `limit`
    (design §6 layer 4: "truncated in that order")."""
    out: List[str] = []
    used = 0
    for text, hint in items:
        if not text:
            continue
        sep = 2 if out else 0
        room = limit - used - sep
        if room <= 0:
            break
        if len(text) > room:
            marker = f"\n[truncated: read {hint}]" if hint else "\n[truncated]"
            text = common.truncate(text, room, marker) if room > len(marker) else ""
            if text:
                out.append(text)
            break
        out.append(text)
        used += len(text) + sep
    return "\n\n".join(out)


def _session_title(ctx: Ctx) -> str:
    task = ctx.task
    return f"forge {task.get('id')} {task.get('phase')}" if task else "forge idle"


def _auto_resume(ctx: Ctx) -> Optional[str]:
    """design §6 layer 5: initialUserMessage on `clear` only, once per task/phase.

    Review-2 #3: `close` sets `task: null` together with `context_state: stale`, so the CLEAR POINT the skills
    print arrives idle. Idle and stale with a non-empty queue resumes with RESUME_IDLE_MESSAGE under the marker
    `auto-resumed-idle-<queue[0].id>`; idle with an empty queue returns None (the caller runs `fresh --no-stamp`
    alone). A task with a next_action resumes as before under `auto-resumed-<task>-<phase>`."""
    st = ctx.status or {}
    if st.get("context_state") != "stale" or not ctx.binding.get("auto_resume"):
        return None
    task = ctx.task
    if task:
        if not task.get("next_action"):
            return None
        key, phase, message = str(task.get("id")), str(task.get("phase")), RESUME_MESSAGE
    else:
        queue = [q for q in st.get("queue") or [] if isinstance(q, dict)]
        if not queue:
            return None
        key, phase, message = "idle", str(queue[0].get("id") or "queue"), RESUME_IDLE_MESSAGE
    marker = f"auto-resumed-{key}-{phase}"
    if _marker(ctx, marker):
        return None
    # Marker first, then fresh (design §6 layer 5). `fresh` removes auto-resumed-* markers (§5.1), so
    # after a successful fresh the marker is gone and the `stale` condition alone prevents a re-fire;
    # when fresh fails the marker stays and stops an auto-resume loop.
    _touch(ctx, marker)
    ok, msg = _status_call(ctx, "fresh", stamp=False)
    _journal(ctx, f"auto-resume {key} {phase}; fresh --no-stamp {'ok' if ok else 'failed: ' + str(msg)}")
    return message


# --------------------------------------------------------------------------- #
# UserPromptSubmit (design §6 layer 3, §13.3)
# --------------------------------------------------------------------------- #
def on_user_prompt_submit(ctx: Ctx) -> Optional[Dict[str, Any]]:
    """Reset the per-turn counters, mark `?` chat turns, inject the one-line reminder."""
    common.ensure_dir(ctx.paths.runtime)
    common.write_text_atomic(ctx.paths.rt("stop-blocks"), "0\n")
    _rm(ctx, "denials")
    prompt = str(ctx.stdin.get("prompt") or "")
    if prompt.lstrip().startswith("?"):
        _touch(ctx, "chat-turn")
    else:
        _rm(ctx, "chat-turn")
    # design §6 layer 2: never touches dirty-* markers.
    return _context("UserPromptSubmit", _reminder(ctx))


def _reminder(ctx: Ctx) -> str:
    st = ctx.status
    if st is None:
        return f"Forge: STATUS.json unreadable ({ctx.status_error}); run .forge/bin/forge-status validate"
    task = common.current_task(st)
    if task:
        nxt = common.truncate(str(task.get("next_action") or "-").replace("\n", " "), REMINDER_NEXT_CHARS, "…")
        line = (f"Forge: {task.get('id')} class {task.get('class')} risk {task.get('risk')} phase {task.get('phase')} "
                f"next: {nxt}")
    else:
        line = "Forge: idle; /forge-task <title> to start"
    if st.get("context_state") == "stale":
        line += f" | context stale since {st.get('updated_at')}; /clear recommended"
    return line


# --------------------------------------------------------------------------- #
# PreToolUse (design §7 gates 1, 2, 2b, 2c, 9, 10, 14)
# --------------------------------------------------------------------------- #
def on_pre_tool_use(ctx: Ctx) -> Optional[Dict[str, Any]]:
    if ctx.tool_name in ("Edit", "Write", "NotebookEdit"):
        return _pre_edit(ctx)
    if ctx.tool_name == "Agent":
        return _pre_agent(ctx)
    if ctx.tool_name == "Bash":
        return _pre_bash(ctx)
    return None


def _edit_path(ctx: Ctx) -> Optional[str]:
    p = ctx.tool_input.get("file_path") or ctx.tool_input.get("notebook_path")
    return str(p) if p else None


def _pre_edit(ctx: Ctx) -> Optional[Dict[str, Any]]:
    path = _edit_path(ctx)
    if not path:
        return None
    # reviews #9/#10: judge the symlink-resolved path and refuse anything that escapes the repository.
    rel, ok, why = ctx.paths.safe_rel(path)
    if not ok:
        return _fence_deny(ctx, "outside-repo", f"{rel}: {why}")
    if why:
        _journal(ctx, f"edit {path} judged as {rel} ({why})")
    # design §7 gate 14: policy lock first, for every session.
    if _policy_locked(ctx, rel):
        return _fence_deny(ctx, "policy-lock", f"Forge-owned or policy file: change it with install.sh or by hand ({rel})")
    if ctx.is_subagent and ctx.role in common.ALL_ROLES:
        return _pre_edit_subagent(ctx, rel)
    return _pre_edit_main(ctx, rel)   # unknown roles follow the main-session rules


def _draft_allowed(ctx: Ctx, rel: str) -> bool:
    """review #17: `.forge/tasks/<id>/drafts/<agent_id>-*.md` of this agent's task (open task or the record's)."""
    m = _DRAFT_PATH_RE.match(rel)
    if not m or not ctx.agent_id or m.group(2) != ctx.agent_id:
        return False
    rec = _agent_record(ctx, ctx.agent_id)
    return m.group(1) in {str(rec.get("task") or ""), str(ctx.task_id or "")}


def _pre_edit_subagent(ctx: Ctx, rel: str) -> Optional[Dict[str, Any]]:
    """Worker scope fence (design §7 gate 2) and read-only roles (gate 2c)."""
    role = ctx.role
    if _draft_allowed(ctx, rel):
        return None
    if role == "forge-verifier":
        if rel.startswith(VERIFIER_MEMORY):
            return None
        return _deny(f"forge-verifier is read-only except {VERIFIER_MEMORY}**; it must not edit {rel}")
    if role == "forge-scout":
        return _deny("forge-scout is read-only: no Edit/Write")
    if role == "forge-planner":
        tid = ctx.task_id
        if tid and rel.startswith(f".forge/tasks/{tid}/"):
            return None
        return _deny(f"forge-planner writes only under .forge/tasks/{tid or '<task>'}/ (not {rel})")
    if role == "forge-librarian":
        if any(rel.startswith(p) if p.endswith("/") else rel == p for p in LIBRARIAN_ALLOW):
            return None
        return _deny(f"forge-librarian may write only lessons, COST-REPORT.md, archive, decisions, CLAUDE.md and agent memory (not {rel})")
    # Builders and the mechanic.
    if rel.startswith(".forge/"):
        return _deny(f"workers never write Forge state ({rel}); hooks record your work")
    rec = _agent_record(ctx, ctx.agent_id)
    if not rec.get("brief"):
        return _deny("Read your brief file with the Read tool before editing")
    task_id, step_id = str(rec.get("task")), str(rec.get("step"))
    from . import gates
    bm = gates.brief_meta(ctx.paths, task_id, step_id) or {}
    budget = _budget_exhausted(ctx)
    if budget:
        return _deny(budget)
    allowed = _str_list(bm.get("allowed_paths"))
    if common.any_glob(rel, allowed) is None:
        return _deny(f"{rel} is outside your brief's allowed_paths {allowed}; put it in the HANDOFF's Remaining instead")
    test_globs = _str_list(ctx.binding.get("test_globs"))
    if (common.any_glob(rel, test_globs) is not None and common.exists(os.path.join(ctx.paths.root, rel))
            and bm.get("may_edit_tests") is not True):
        return _deny(f"{rel} is an existing test file and the brief sets may_edit_tests: false (new test files are fine)")
    protected = _str_list(ctx.binding.get("protected_paths"))
    if common.any_glob(rel, protected) is not None:
        task = ctx.task
        risk = task.get("risk") if task else None
        if role != "forge-builder" or risk != "R":
            return _deny(f"{rel} is a protected path: only forge-builder on a risk R task may edit it")
    if role == "forge-mechanic":
        denied = _str_list(ctx.binding.get("risk_paths")) + _str_list(ctx.binding.get("mechanic_denied_paths"))
        if common.any_glob(rel, denied) is not None:
            return _deny(f"{rel} is a risk or mechanic-denied path: forge-mechanic never edits it")
    return None


def _main_fence_rule(ctx: Ctx) -> Optional[Tuple[str, str]]:
    """(rule, reason) when the main session may not mutate source now (design §7 gate 1), else None."""
    st = ctx.status
    if st is None:
        if common.exists(ctx.paths.status):
            return "status-invalid", f"STATUS.json unreadable ({ctx.status_error}); run .forge/bin/forge-status validate"
        return "no-task", "No Forge task is open: /forge-task <title> first"
    task = common.current_task(st)
    if task is None:
        return "no-task", "No Forge task is open: /forge-task <title> first"
    cls = task.get("class")
    if cls in ("M", "W", "L"):
        return "class-delegated", f"class {cls} work runs in a builder; dispatch per next_action: {task.get('next_action') or '-'}"
    if cls in ("S", "X") and not task.get("plan"):
        return "plan-first", (f"write the inline plan section first (.forge/tasks/{task.get('id')}/plan.md), then "
                              f".forge/bin/forge-status plan {task.get('id')} --from .forge/tasks/{task.get('id')}/plan.md")
    return None


def _pre_edit_main(ctx: Ctx, rel: str) -> Optional[Dict[str, Any]]:
    """Plan-first / scope fence for the architect (design §3 step 2, §7 gate 1)."""
    meta_ok, meta_why = _main_meta_allowed(ctx, rel)
    if meta_ok:
        return None
    if meta_why:
        return _fence_deny(ctx, "meta-task", meta_why)
    rule = _main_fence_rule(ctx)
    if rule:
        return _fence_deny(ctx, *rule)
    task = ctx.task or {}
    scope = _str_list(task.get("scope"))
    if common.any_glob(rel, scope) is None:
        if task.get("class") == "X":
            hint = f".forge/bin/forge-status scope add {ctx.task_id} {rel} --why \"...\" widens it"
        else:
            hint = "re-open the task with the right --files/--creates, or open a new one"
        return _fence_deny(ctx, "scope", f"{rel} is outside the declared scope {scope}; {hint}")
    protected = _str_list(ctx.binding.get("protected_paths"))
    if common.any_glob(rel, protected) is not None and task.get("risk") != "R":
        return _fence_deny(ctx, "protected", f"{rel} is a protected path; only a risk R task may edit it (--force-risk at open)")
    _touch(ctx, "dirty-main")   # design §6 layer 2: a source mutation STATUS has not recorded yet
    _rm(ctx, "chat-turn")
    return None


# ---- Agent spawn guard (design §7 gate 9) ---------------------------------- #
def _pre_agent(ctx: Ctx) -> Optional[Dict[str, Any]]:
    ti = ctx.tool_input
    sub = str(ti.get("subagent_type") or "")
    role_t = common.agent_role(sub) or ""
    task = ctx.task
    if str(ti.get("isolation") or "") == "worktree" and (ctx.binding.get("git") or {}).get("worktree_isolation") is not True:
        # review #16: tree_changed/_commit_step/recover are not worktree-aware until the probe proves the layout.
        return _deny("isolation: worktree is not enabled: binding.git.worktree_isolation is false. Run "
                     ".forge/bin/forge-doctor --worktree (/forge-doctor --worktree); the operator sets it to true "
                     "only after the probe passes. Spawn without isolation.")
    if not re.match(r"^(forge:)?forge-", sub):
        _journal(ctx, f"builtin spawn: {sub or 'general-purpose'}")
        common.ledger(ctx.paths, {"event": "builtin", "task": ctx.task_id, "agent": "builtin", "subagent_type": sub or None,
                                  "session_id": ctx.session_id})
        return None
    if role_t == "forge-scout":
        return None
    if task is None and role_t != "forge-librarian":
        return _deny("No Forge task is open: /forge-task <title> first (forge-* workers need an open task)")
    default = common.DEFAULT_AGENT_ROUTING.get(role_t, (None, None))
    eff_model = common.alias_model(ti.get("model") or default[0]) or ""
    eff_effort = str(ti.get("effort") or default[1] or "")
    if role_t == "forge-librarian":
        _record_dispatch(ctx, task, None, role_t, eff_model, eff_effort)
        return None
    if role_t == "forge-planner":
        return _spawn_planner(ctx, task or {}, role_t, eff_model, eff_effort)
    if role_t in common.WORKER_ROLES:
        return _spawn_worker(ctx, task or {}, role_t, eff_model, eff_effort)
    if role_t == "forge-verifier":
        return _spawn_verifier(ctx, task or {}, role_t, eff_model, eff_effort)
    return _deny(f"unknown Forge agent {sub!r}; the roster is {', '.join(common.ALL_ROLES)}")


def _last_dispatch(ctx: Ctx, task_id: str, step_id: Optional[str], agent: str) -> Optional[Dict[str, Any]]:
    """Newest ledger `dispatch` row for this task/step/agent."""
    rows = [r for r in common.read_jsonl(ctx.paths.ledger)
            if r.get("event") == "dispatch" and r.get("task") == task_id and r.get("step") == step_id
            and r.get("agent") == agent]
    return rows[-1] if rows else None


def _record_dispatch(ctx: Ctx, task: Optional[Dict[str, Any]], step: Optional[Dict[str, Any]], agent: str,
                     model: str, effort: str, via_status: bool = False) -> None:
    """Journal the dispatch; write the ledger `dispatch` row (design §5.8) unless a forge-status
    transition (`step_start` / `step_verifying`) already wrote it (`via_status`)."""
    tid = str(task.get("id")) if task else None
    sid = str(step.get("id")) if step else None
    if not via_status:
        common.ledger(ctx.paths, {"event": "dispatch", "task": tid, "step": sid, "class": (task or {}).get("class"),
                                  "agent": agent, "model": model, "effort": effort,
                                  "attempt": (step or {}).get("attempts"), "escalated_from": None,
                                  "session_id": ctx.session_id})
    _journal(ctx, f"dispatch {agent} {model}/{effort}" + (f" step {sid}" if sid else ""), tid)


def _spawn_planner(ctx: Ctx, task: Dict[str, Any], role_t: str, model: str, effort: str) -> Optional[Dict[str, Any]]:
    if task.get("phase") != "plan":
        return _deny(f"forge-planner spawns only in phase plan (phase is {task.get('phase')})")
    if task.get("plan_author") == "architect":
        return _deny("the architect already authored this plan; import it with .forge/bin/forge-status plan")
    cls = task.get("class")
    want = {"M": "medium", "W": "high", "L": "high"}.get(str(cls))
    if want is None:
        return _deny(f"class {cls} plans are written inline by the architect; no planner")
    if effort != want:
        return _deny(f"forge-planner effort must be {want} for class {cls} (got {effort})")
    if model != "fable":
        return _deny(f"forge-planner runs on fable (got {model})")
    _record_dispatch(ctx, task, None, role_t, model, effort)
    return None


def _spawn_worker(ctx: Ctx, task: Dict[str, Any], role_t: str, model: str, effort: str) -> Optional[Dict[str, Any]]:
    """A builder/mechanic spawn must match a pending step, or a pre-started retry (design §3 step 5)."""
    tid = str(task.get("id"))
    steps = _steps(task)
    if task.get("phase") == "intake":
        # review #4: a builder dispatched during intake flips the phase and strands the corrected plan.
        return _deny(f"{tid} is in phase intake: answer needs_clarification, then re-run "
                     f".forge/bin/forge-status plan {tid} --from .forge/tasks/{tid}/plan.md before dispatching")

    def dispatchable(s: Dict[str, Any]) -> bool:
        if s.get("status") == "pending":
            return True
        if not (s.get("status") == "running" and s.get("agent_id") is None and int(s.get("attempts") or 0) >= 1):
            return False
        return _pending_dispatch(ctx, tid, s) is None

    matches = [s for s in steps if dispatchable(s) and s.get("agent") == role_t
               and common.alias_model(s.get("model")) == model and s.get("effort") == effort]
    if not matches:
        expected = [f"{s.get('agent')} {common.alias_model(s.get('model'))}/{s.get('effort')} (step {s.get('id')}, {s.get('status')})"
                    for s in steps if dispatchable(s)]
        failed = [str(s.get("id")) for s in steps if s.get("status") == "failed"]
        running = [str(s.get("id")) for s in steps if s.get("status") == "running" and s.get("agent_id")]
        awaited = [(str(s.get("id")), _pending_dispatch(ctx, tid, s)) for s in steps
                   if s.get("status") == "running" and s.get("agent_id") is None and _pending_dispatch(ctx, tid, s)]
        if expected:
            reason = (f"spawn {role_t} {model}/{effort} matches no dispatchable step; expected one of: "
                      + "; ".join(expected))
        elif awaited:
            sid, who = awaited[0]
            reason = (f"step {sid} already dispatched to a worker that has not bound yet ({who}); wait for it to read "
                      f"its brief, or `.forge/bin/forge-status recover {tid} {sid} --force` if that Agent call failed")
        elif failed:
            reason = (f"step {', '.join(failed)} failed: run .forge/bin/forge-status step-start {tid} {failed[0]} "
                      f"--from failed|clean first")
        elif running:
            reason = f"step {', '.join(running)} is already running with a bound worker; wait for its handoff"
        else:
            reason = f"no pending step to dispatch; next_action: {task.get('next_action') or '-'}"
        return _deny(reason)
    step = matches[0]
    started = False
    if step.get("status") == "pending":
        ok, msg = _status_call(ctx, "step_start", tid, str(step.get("id")))
        if not ok:
            return _deny(f"forge-status step-start {tid} {step.get('id')} refused: {msg}")
        step = common.find_step(ctx.task or task, str(step.get("id"))) or step
        started = True
    # A pre-started retry was already recorded by the architect's own step-start.
    _record_dispatch(ctx, ctx.task or task, step, role_t, model, effort, via_status=True)
    # review #21: remember this dispatch until the worker binds (or the marker ages out / the attempt changes).
    common.write_json_atomic(ctx.paths.rt(_dispatch_marker(tid, str(step.get("id")))),
                             {"ts": common.now_ts(), "attempts": step.get("attempts"), "started_ts": step.get("started_ts"),
                              "agent": role_t, "session_id": ctx.session_id})
    _journal(ctx, f"spawn guard allowed {role_t} on step {step.get('id')} ({'started now' if started else 'pre-started'})", tid)
    return None


def _pending_dispatch(ctx: Ctx, task_id: str, step: Dict[str, Any]) -> Optional[str]:
    """Why a running-unbound step is already spoken for (review #21), else None.

    A fresh spawn-guard marker for this attempt (≤ DISPATCH_MARKER_TTL_S old), or an agent record of the step's
    role that started after this attempt began (bound to the step, or unbound and ≤ 10 min old)."""
    sid = str(step.get("id"))
    now = common.now_ts()
    try:
        marker = common.read_json(ctx.paths.rt(_dispatch_marker(task_id, sid)), default=None)
    except common.ForgeError:
        marker = None
    if isinstance(marker, dict) and marker.get("attempts") == step.get("attempts") \
            and marker.get("started_ts") == step.get("started_ts") and isinstance(marker.get("ts"), int) \
            and now - int(marker["ts"]) < DISPATCH_MARKER_TTL_S:
        return f"spawn guard dispatch at {marker['ts']}"
    agents_dir = os.path.join(ctx.paths.runtime, "agents")
    if not os.path.isdir(agents_dir):
        return None
    started_ts = int(step.get("started_ts") or 0)
    for name in sorted(os.listdir(agents_dir)):
        if not name.endswith(".json"):
            continue
        rec = _agent_record(ctx, name[:-5])
        if rec.get("task") != task_id or common.agent_role(rec.get("agent_type")) != step.get("agent"):
            continue
        rec_ts = rec.get("started_ts") if isinstance(rec.get("started_ts"), int) else 0
        if rec_ts < started_ts:
            continue   # a worker of an earlier attempt
        if rec.get("step") == sid:
            return f"agent record {rec.get('agent_id')} bound to step {sid}"
        if rec.get("step") is None and now - rec_ts < DISPATCH_MARKER_TTL_S:
            return f"agent record {rec.get('agent_id')} started {now - rec_ts}s ago"
    return None


def _spawn_verifier(ctx: Ctx, task: Dict[str, Any], role_t: str, model: str, effort: str) -> Optional[Dict[str, Any]]:
    """Verifier spawn rules (design §13.3 Agent row; §3 steps 9-10)."""
    tid = str(task.get("id"))
    cls, risk, phase = task.get("class"), task.get("risk"), task.get("phase")
    if phase == "intake":
        return _deny(f"{tid} is in phase intake: answer needs_clarification, then re-run "
                     f".forge/bin/forge-status plan {tid} --from .forge/tasks/{tid}/plan.md; nothing to verify yet")
    rv = (task.get("routing") or {}).get("verifier") or {}
    reasons: List[str] = []
    for s in _steps_with(task, "reported"):
        sid = str(s.get("id"))
        if rv.get("model") and common.alias_model(rv.get("model")) != model:
            reasons.append(f"step {sid}: routing.verifier is {common.alias_model(rv.get('model'))}/{rv.get('effort')} (got {model}/{effort})")
            continue
        if rv.get("effort") and rv.get("effort") != effort:
            reasons.append(f"step {sid}: routing.verifier effort is {rv.get('effort')} (got {effort})")
            continue
        if int(s.get("verify_attempts") or 0) >= 2 and not common.exists(ctx.paths.task_file(tid, "ruling.md")):
            reasons.append(f"step {sid}: verify_attempts is {s.get('verify_attempts')}; a third verifier needs ruling.md")
            continue
        ok, msg = _status_call(ctx, "step_verifying", tid, sid)
        if not ok:
            return _deny(f"forge-status step-verifying {tid} {sid} refused: {msg}")
        _record_dispatch(ctx, ctx.task or task, common.find_step(ctx.task or task, sid) or s, role_t, model, effort,
                         via_status=True)
        return None
    steps = _steps(task)
    inline_ok = (
        (cls == "S" and model in ("sonnet", "opus") and phase == "execute")
        or (cls == "X" and model == "fable")
        or (cls == "L" and steps and all(s.get("status") == "done" for s in steps) and model == "fable")
        or (risk == "R" and model == "fable")
    )
    if inline_ok:
        _record_dispatch(ctx, task, None, role_t, model, effort)
        return None
    if not reasons:
        reasons.append(f"no step is reported; class {cls} risk {risk} phase {phase} admits "
                       "S: sonnet|opus in execute · X: fable · L spot-check: fable after all units are done · R: fable")
    return _deny("forge-verifier spawn refused: " + "; ".join(reasons))


# ---- Bash guard (design §7 gates 1, 2b, 2c, 10) --------------------------- #
def _rm_target_abs(tok: str, root: str) -> str:
    """Normalised absolute form of an `rm` target: quotes stripped, `~` and `$VAR` expanded, `..` collapsed;
    a relative target is taken from the repository root (workers run commands from the root)."""
    t = os.path.expanduser(os.path.expandvars(tok.strip("'\"")))
    if not os.path.isabs(t):
        t = os.path.join(root, t)
    return os.path.normpath(t)


def _rm_recursive_outside(cmd: str, safe_dirs: List[str], root: str, repo_roots: Iterable[str] = ()) -> Optional[str]:
    """First target of a recursive `rm` that is not under a safe directory, else None.

    Review-2 #1: the containment test was lexical (`startswith`), so `/tmp/../home/...` passed. The target is now
    normalised (`_rm_target_abs`) and judged by its symlink-resolved path with the realpath + commonpath test
    `common._is_under` uses: `/tmp/../home` is `/home`, `<scratchpad>/../../x` leaves the scratchpad, and a link
    under /tmp pointing elsewhere is judged by where it points. The repository (`repo_roots`: root and a linked
    worktree) is never a safe target, nor is any directory that contains it (`rm -rf ../` from the root), even
    when the checkout itself lives under /tmp."""
    roots = [r for r in repo_roots if r]
    for seg in _segments(cmd):
        toks = _tokens(seg)
        if _command_word(toks) != "rm":
            continue
        i = next((k for k, t in enumerate(toks) if os.path.basename(t) == "rm"), None)
        if i is None:
            continue
        args = toks[i + 1:]
        flags = [t for t in args if t.startswith("-")]
        recursive = any(f == "--recursive" or (not f.startswith("--") and ("r" in f or "R" in f)) for f in flags)
        if not recursive:
            continue
        for t in args:
            if t.startswith("-"):
                continue
            target = _rm_target_abs(t, root)
            if any(common._is_under(target, r) or common._is_under(r, target) for r in roots):
                return t
            if not any(common._is_under(target, d) for d in safe_dirs if d):
                return t
    return None


def _status_write_subcommand(cmd: str) -> Optional[str]:
    """The forge-status subcommand in `cmd` when it writes STATUS (anything but get / validate)."""
    for seg in _segments(cmd):
        m = re.search(r"forge-status\b(.*)$", seg)
        if not m:
            continue
        rest = m.group(1).split()
        sub = next((t for t in rest if not t.startswith("-")), None)
        if sub is None or sub == "get":
            continue
        if sub == "validate" and "--restamp" not in rest:
            continue
        return sub
    return None


def _bash_paths(ctx: Ctx, cmd: str) -> List[Tuple[str, str, bool, str]]:
    """(token, rel, ok, why) via paths.safe_rel for every path-like token of every segment that lies inside the
    repository lexically (paths outside, such as /tmp, are not judged here; the `rm -r` rule covers them)."""
    out: List[Tuple[str, str, bool, str]] = []
    for seg in _segments(cmd):
        for tok in _tokens(seg):
            if not _path_like(tok):
                continue
            t = os.path.expanduser(os.path.expandvars(_strip_redirect(tok)))
            lexical = ctx.paths.rel(t)
            if os.path.isabs(lexical) or lexical == ".." or lexical.startswith("../"):
                continue
            rel, ok, why = ctx.paths.safe_rel(t)
            out.append((tok, rel, ok, why))
    return out


def _bash_symlink_policy(ctx: Ctx, cmd: str, mutating: bool, strict: bool) -> Optional[str]:
    """Deny reason when a path argument escapes the repository through a symlink (judged for write-shaped
    commands) or reaches Forge state / a policy-locked file through one (reviews #9/#10). `strict` (subagents)
    denies any link into .forge/, .claude/, CLAUDE.md or .gitignore; the main session denies a link into a
    policy-locked file for write-shaped commands."""
    for tok, rel, ok, why in _bash_paths(ctx, cmd):
        if not ok:
            if mutating:
                return f"{tok}: {why}"
            continue
        if not why:
            continue
        if strict and (rel.startswith((".forge/", ".claude/")) or rel in ("CLAUDE.md", ".gitignore")):
            return f"{tok} resolves to {rel} ({why}); subagents never touch Forge state or policy files"
        if mutating and _policy_locked(ctx, rel):
            return f"{tok} resolves to the Forge-owned or policy file {rel} ({why}); change it with install.sh or by hand"
    return None


def _pre_bash(ctx: Ctx) -> Optional[Dict[str, Any]]:
    cmd = str(ctx.tool_input.get("command") or "")
    if not cmd.strip():
        return None
    if ctx.is_subagent and ctx.role in common.ALL_ROLES:
        return _pre_bash_subagent(ctx, cmd)
    from . import gates
    mutating = gates.looks_mutating(cmd, _safe_prefixes(ctx))
    bad_link = _bash_symlink_policy(ctx, cmd, mutating=mutating, strict=False)
    if bad_link:
        return _fence_deny(ctx, "policy-lock", bad_link)
    # design §7 gate 10: irreversible commands ask (interactive) or are denied (driver mode).
    pat = gates.irreversible_match(cmd, _str_list(ctx.binding.get("irreversible_commands")))
    if pat:
        if _marker(ctx, "driver"):
            return _fence_deny(ctx, "irreversible", f"irreversible command (binding pattern {pat!r}) is denied in driver "
                                                    "mode: a human runs it; forge-run blocks the phase")
        _journal(ctx, f"irreversible command asks for confirmation ({pat!r}): {redact(cmd[:120])}")
        return _ask(f"irreversible command: matches binding.irreversible_commands pattern {pat!r}")
    if mutating:
        rule = _main_fence_rule(ctx)
        if rule:
            return _fence_deny(ctx, rule[0], "source changes go through the fence: use Edit/Write inside the declared "
                                              f"scope, or dispatch per next_action ({rule[1]})")
        _touch(ctx, "dirty-main")
        _rm(ctx, "chat-turn")
    return None


def _forge_segment_rule(toks: List[str]) -> Optional[str]:
    """Deny reason when a subagent segment touches `.forge/` outside the allow-list (review #6):
    `.forge/bin/forge-check …`, `.forge/bin/forge-gate …` (a draft under .forge/tasks/<id>/drafts/ may be named),
    `.forge/bin/forge-status get …`, or `cat|sed -n|head|less` of `.forge/tasks/<id>/brief-NN.md`. Also denies
    forge-doctor/forge-run/forge-bench/forge-hook however they are reached, and any interpreter run on a file
    under .forge/."""
    if not toks:
        return None
    word = _command_word(toks)
    if word in FORGE_DENIED_SCRIPTS:
        return f"subagents never run {word} (operator-only; it changes gates, state or sessions)"
    refs = [t for t in toks if _FORGE_REF_RE.search(_strip_redirect(t))]
    if not refs:
        return None
    head = next((t for t in toks if os.path.basename(t) == word), toks[0])
    m = _FORGE_SCRIPT_RE.match(head)
    if m:
        script = m.group(2)
        rest = [t for t in toks[toks.index(head) + 1:]]
        if script in ("forge-check", "forge-gate"):
            stray = [t for t in rest if _FORGE_REF_RE.search(_strip_redirect(t))
                     and not (_DRAFT_TOKEN_RE.search(t) or _BRIEF_TOKEN_RE.search(t))]
            if stray:
                return f"{script} may name only your draft or brief under .forge/tasks/<id>/ (not {stray[0]})"
            return None
        if script == "forge-status":
            sub = next((t for t in rest if not t.startswith("-")), None)
            stray = [t for t in rest if _FORGE_REF_RE.search(_strip_redirect(t))]
            if sub == "get" and not stray:
                return None
            return f"subagents may run forge-status get only (not forge-status {sub or ''}); hooks record your work"
        return f"subagents never run .forge/bin/{script}"
    if word in ("cat", "head", "less", "more") or (word == "sed" and len(toks) > 1 and toks[1].startswith("-n")):
        if all(_BRIEF_TOKEN_RE.search(t) for t in refs) and not any(_strip_redirect(t) != t for t in toks):
            return None
        return f"from the shell a subagent may read only its brief under .forge/tasks/<id>/ (not {refs[0]})"
    return (f"subagents never touch .forge/ from the shell ({refs[0]}); allowed: .forge/bin/forge-check, "
            f".forge/bin/forge-gate, .forge/bin/forge-status get, and cat/sed -n/head of your brief")


def _meta_segment_rule(toks: List[str]) -> Optional[str]:
    """Deny reason when a subagent segment writes CLAUDE.md, .gitignore or .claude/** (review #38): only a
    plain reader command (cat, head, grep, git diff …) with no redirect may name them."""
    refs = [t for t in toks if _META_FILE_RE.search(_strip_redirect(t)) or _CLAUDE_REF_RE.search(_strip_redirect(t))]
    if not refs:
        return None
    word = _command_word(toks)
    redirected = any(_strip_redirect(t) != t or t in (">", ">>", "<") for t in toks)
    writes = ((word == "sed" and any(t.startswith("-i") for t in toks))
              or (word == "find" and any(t in ("-delete", "-exec", "-execdir", "-ok", "-okdir") or t.startswith("-fprint") for t in toks))
              or (word == "git" and _git_subcommand(toks) not in ("diff", "log", "show", "status", "blame", "grep", "ls-files")))
    if word in META_READERS and not redirected and not writes:
        return None
    return (f"subagents never write CLAUDE.md, .gitignore or .claude/** from the shell ({refs[0]}); only the librarian "
            "edits CLAUDE.md and agent memory, with Edit/Write")


def _pre_bash_subagent(ctx: Ctx, cmd: str) -> Optional[Dict[str, Any]]:
    from . import gates
    role = ctx.role
    for seg in _segments(cmd):
        toks = _tokens(seg)
        if not toks:
            continue
        word = _command_word(toks)
        # review #32: git is allow-listed by subcommand after its global options (-C dir, -c k=v, …).
        git_sub = _git_subcommand(toks)
        if git_sub is not None:
            if git_sub == "push":
                return _deny("workers never git push")
            if git_sub == "stash":
                i = toks.index("stash")
                if i + 1 >= len(toks) or toks[i + 1] not in ("list", "show"):
                    return _deny("workers never git stash (that hides the operator's tree); name the operation in your HANDOFF")
            elif git_sub not in GIT_WORKER_ALLOW:
                return _deny(f"workers never run git {git_sub or '(no subcommand)'}; allowed: git "
                             f"{'|'.join(GIT_WORKER_ALLOW[:9])}, stash list; name anything else in your HANDOFF")
        if word == "ln":
            return _deny("workers never create links (ln): a link could route an edit around the fences (review #9)")
        why = _forge_segment_rule(toks)
        if why:
            return _deny(why)
        why = _meta_segment_rule(toks)
        if why:
            return _deny(why)
    # reviews #9/#10: path arguments are judged by their symlink-resolved target.
    bad_link = _bash_symlink_policy(ctx, cmd, mutating=gates.looks_mutating(cmd, _verify_prefixes(ctx)), strict=True)
    if bad_link:
        return _deny(bad_link)
    safe = list(RM_SAFE_DIRS) + [str(ctx.stdin.get("scratchpad_dir") or ""), os.environ.get("TMPDIR") or ""]
    bad = _rm_recursive_outside(cmd, safe, ctx.paths.root, (ctx.paths.root, ctx.paths.worktree_root or ""))
    if bad:
        return _deny(f"recursive rm outside /tmp, $TMPDIR or the scratchpad (or inside the repository) is denied ({bad})")
    sub = _status_write_subcommand(cmd)
    if sub:
        return _deny(f"workers never write STATUS (forge-status {sub}); hooks record dispatch, reports and verdicts")
    pat = gates.irreversible_match(cmd, _str_list(ctx.binding.get("irreversible_commands")))
    if pat:
        return _deny(f"irreversible command (binding pattern {pat!r}) is never run by a worker; name it in your HANDOFF")
    if role in common.READONLY_ROLES and not gates.ro_allowed(cmd, _verify_prefixes(ctx)):
        return _deny(f"{role} is read-only: the command is not on the Bash allow-list (git log/grep/diff/show, rg, grep, "
                     "find, ls, cat, head, tail, wc, jq, pytest, .forge/bin/forge-check|forge-gate, binding verify commands)")
    if role in common.WORKER_ROLES:
        budget = _budget_exhausted(ctx)
        if budget:
            return _deny(budget)
        # design §3 step 6: a brief read through the shell binds like a Read.
        if _BRIEF_READ_CMD_RE.search(cmd):
            m = _BRIEF_PATH_RE.search(cmd)
            if m:
                _maybe_bind(ctx, m.group(0))
    return None


# --------------------------------------------------------------------------- #
# PostToolUse / PostToolUseFailure (design §7 gate 4, §5.7)
# --------------------------------------------------------------------------- #
def on_post_tool_use(ctx: Ctx) -> Optional[Dict[str, Any]]:
    tool = ctx.tool_name
    if ctx.is_subagent:
        _reset_blocks_on_resume(ctx)   # review-2 #13: the bound worker is active again on a failed step
    if tool == "Read":
        if ctx.is_subagent:
            path = _edit_path(ctx)
            if path and _BRIEF_PATH_RE.search(ctx.paths.rel(path)):
                _maybe_bind(ctx, ctx.paths.rel(path))
        return None
    if tool in ("Edit", "Write", "NotebookEdit"):
        _record_edit(ctx)
        return None
    if tool == "Bash":
        _record_bash(ctx, ok=True)
        return None
    return None


def on_post_tool_use_failure(ctx: Ctx) -> Optional[Dict[str, Any]]:
    if ctx.is_subagent:
        _reset_blocks_on_resume(ctx)   # review-2 #13
    if ctx.tool_name == "Bash":
        _record_bash(ctx, ok=False)
    return None


def _record_edit(ctx: Ctx) -> None:
    path = _edit_path(ctx)
    if not path:
        return
    rel, _ok, _why = ctx.paths.safe_rel(path)   # the resolved target, so evidence names the real file (#9)
    kind = common.edit_kind(ctx.paths, rel)
    tid = _evidence_task_id(ctx)
    if ctx.is_subagent:
        _count_tool_call(ctx)   # review #6: the budget counter lives in the hook-owned agent record
    if tid:
        common.evidence_append(ctx.paths, tid, {"agent_id": ctx.agent_id or "main", "agent_type": ctx.role or "main",
                                                "event": "edit", "kind": kind, "file": rel})
    if not ctx.is_subagent and kind == "source":
        _touch(ctx, "dirty-main")


def _best_effort_exit(obj: Any) -> Optional[int]:
    """First numeric exit_code|exitCode|code anywhere in `obj`, else `[Ee]xit code N` in its text, else None."""
    def walk(o: Any) -> Optional[int]:
        if isinstance(o, dict):
            for k in ("exit_code", "exitCode", "code"):
                v = o.get(k)
                if isinstance(v, int) and not isinstance(v, bool):
                    return v
            for v in o.values():
                r = walk(v)
                if r is not None:
                    return r
        elif isinstance(o, list):
            for v in o:
                r = walk(v)
                if r is not None:
                    return r
        return None

    found = walk(obj)
    if found is not None:
        return found
    text = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, default=str)
    m = _EXIT_TEXT_RE.search(text or "")
    return int(m.group(1)) if m else None


def _record_bash(ctx: Ctx, ok: bool) -> None:
    cmd = str(ctx.tool_input.get("command") or "")
    source = ctx.stdin.get("tool_response") if ok else ctx.stdin.get("error")
    # review #34: evidence is committed at close; redact credential shapes and cap the stored command.
    stored = redact(cmd)
    if len(stored) > EVIDENCE_CMD_MAX_CHARS:
        stored = stored[:EVIDENCE_CMD_MAX_CHARS - 1] + "…"
    row: Dict[str, Any] = {"agent_id": ctx.agent_id or "main", "agent_type": ctx.role or "main", "event": "bash",
                           "ok": ok, "exit": _best_effort_exit(source), "cmd": stored}
    if not ok:
        err = source if isinstance(source, str) else json.dumps(source, ensure_ascii=False, default=str)
        row["error_head"] = redact((err or "")[:200])
    if ctx.is_subagent:
        _count_tool_call(ctx)   # review #6
    tid = _evidence_task_id(ctx)
    if tid:
        common.evidence_append(ctx.paths, tid, row)
    _stamp_checks(ctx, cmd)
    if not ctx.is_subagent:
        from . import gates
        if gates.looks_mutating(cmd, _safe_prefixes(ctx)):
            _touch(ctx, "dirty-main")


def _stamp_checks(ctx: Ctx, cmd: str) -> None:
    """Rewrite the newest `checks/<step>-<ts>-unknown.json` (≤300 s old) with the real agent (design §5.7)."""
    m = _FORGE_CHECK_RE.search(cmd)
    if not m:
        return
    task_id, step = m.group(1), m.group(2)
    d = ctx.paths.checks_dir(task_id)
    if not os.path.isdir(d):
        return
    now = common.now_ts()
    rx = re.compile(rf"^{re.escape(step)}-(\d+)-unknown\.json$")
    newest: Optional[Tuple[int, str]] = None
    for name in os.listdir(d):
        mm = rx.match(name)
        if not mm:
            continue
        ts = int(mm.group(1))
        if now - ts > CHECK_STAMP_WINDOW_S:
            continue
        if newest is None or ts > newest[0]:
            newest = (ts, name)
    if newest is None:
        return
    old = os.path.join(d, newest[1])
    try:
        rec = common.read_json(old, default=None)
    except common.ForgeError:
        return
    if not isinstance(rec, dict):
        return
    agent = ctx.agent_id or "main"
    rec["agent_id"] = agent
    if agent == "main":
        rec["session_id"] = ctx.session_id
    for res in rec.get("results") or []:   # review #34: output tails are committed at close
        if isinstance(res, dict) and isinstance(res.get("tail"), str):
            res["tail"] = redact(res["tail"])
    new = os.path.join(d, f"{step}-{newest[0]}-{agent}.json")
    common.write_json_atomic(new, rec)
    if new != old:
        common.rm(old)
    _journal(ctx, f"stamped {ctx.paths.rel(new)}", task_id)


# --------------------------------------------------------------------------- #
# SubagentStart (design §3 step 5)
# --------------------------------------------------------------------------- #
def on_subagent_start(ctx: Ctx) -> Optional[Dict[str, Any]]:
    if not ctx.agent_id:
        return None
    fields: Dict[str, Any] = {"agent_type": ctx.agent_type or ctx.role, "started_ts": common.now_ts(),
                              "session_id": ctx.session_id}
    task = ctx.task
    if task:
        fields["task"] = task.get("id")
        if ctx.role == "forge-verifier":
            # Verifiers never bind to a brief; remember the step they verify (never `step`, which means bound).
            verifying = _steps_with(task, "verifying")
            if len(verifying) == 1:
                fields["verify_step"] = verifying[0].get("id")
            elif not _steps(task):
                fields["verify_step"] = "main"
    _merge_agent_record(ctx, ctx.agent_id, **fields)
    _reset_blocks_on_resume(ctx)   # review-2 #13: a known agent_id bound to a failed step is being resumed
    _journal(ctx, f"subagent start {ctx.agent_type} {ctx.agent_id}")
    return _context("SubagentStart", WORKER_START_LINE)


# --------------------------------------------------------------------------- #
# SubagentStop gates (design §7 gates 0, 5, 7; §3 steps 3, 8, 9)
# --------------------------------------------------------------------------- #
def on_subagent_stop(ctx: Ctx) -> Optional[Dict[str, Any]]:
    text = str(ctx.stdin.get("last_assistant_message") or "")
    if ctx.role == "forge-planner":
        return _stop_planner(ctx, text)
    if ctx.role in common.WORKER_ROLES:
        return _stop_builder(ctx, text)
    if ctx.role == "forge-verifier":
        return _stop_verifier(ctx, text)
    return None


def _gate_blocks(ctx: Ctx) -> int:
    """Blocks so far for this agent (counted in .runtime/agents/<id>.json)."""
    return int(_agent_record(ctx, ctx.agent_id).get("blocks") or 0)


def _reset_blocks_on_resume(ctx: Ctx) -> None:
    """Review-2 #13 (design §3 step 10; ROUTING rule 6): a worker resumed at round 1 via SendMessage starts with a
    fresh gate-block budget. The resume is detected lazily, the first time the bound agent is seen again
    (SubagentStart for a known agent_id, a PostToolUse, or its next SubagentStop) while its step is `failed`.
    The reset happens once per attempt and escalation round (`blocks_reset` in the agent record), so a resumed
    worker that is blocked again is not reset again (the two-block cap still ends the loop)."""
    if not ctx.agent_id:
        return
    rec = _agent_record(ctx, ctx.agent_id)
    tid, sid = rec.get("task"), rec.get("step")
    if not (tid and sid):
        return
    task = ctx.task if ctx.task and ctx.task.get("id") == tid else None
    step = common.find_step(task, str(sid)) if task else None
    if not step or step.get("status") != "failed" or step.get("agent_id") != ctx.agent_id:
        return
    key = f"{step.get('attempts')}:{(task.get('escalation') or {}).get('round')}"
    if rec.get("blocks_reset") == key:
        return
    had = int(rec.get("blocks") or 0)
    _merge_agent_record(ctx, ctx.agent_id, blocks=0, blocks_reset=key)
    _journal(ctx, f"resume of {ctx.agent_id} on failed step {sid} detected; gate-block counter reset ({had} -> 0)", str(tid))


def _count_block(ctx: Ctx, task_id: Optional[str], gate: str, reason: str) -> int:
    n = _gate_blocks(ctx) + 1
    if ctx.agent_id:
        _merge_agent_record(ctx, ctx.agent_id, blocks=n)
    if task_id:
        ok, msg = _status_call(ctx, "gate_block", task_id, ctx.agent_id, gate)
        if not ok:
            _journal(ctx, f"gate-block bookkeeping failed: {msg}", task_id)
    _journal(ctx, f"{gate} gate block {n}/{common.GATE_BLOCK_CAP}: {reason[:300]}", task_id)
    return n


def _stop_planner(ctx: Ctx, text: str) -> Optional[Dict[str, Any]]:
    """Plan gate (design §7 gate 0): `forge-gate --plan` + the PLAN-FILE line; two-block cap."""
    from . import gates
    rec = _agent_record(ctx, ctx.agent_id)
    tid = str(rec.get("task") or ctx.task_id or "")
    if not tid:
        return _block("no Forge task is open; nothing to plan")
    defects = gates.plan_validate(ctx.paths, tid)
    if PLAN_FILE_MARKER not in text:
        defects.append(f"the final message must end with a line '{PLAN_FILE_MARKER} .forge/tasks/{tid}/plan.md'")
    if not defects:
        _journal(ctx, "plan gate passed", tid)
        return None
    if _gate_blocks(ctx) >= common.GATE_BLOCK_CAP:
        _journal(ctx, f"PLAN-GATE-BYPASSED after {common.GATE_BLOCK_CAP} blocks; defects: " + " | ".join(defects[:3]), tid)
        return None   # forge-status plan still refuses the import (design §13.3)
    n = _count_block(ctx, tid, "plan", "; ".join(defects[:3]))
    return _block(f"Plan gate ({n}/{common.GATE_BLOCK_CAP}): fix these, run .forge/bin/forge-gate --plan {tid}, "
                  f"then end with '{PLAN_FILE_MARKER} .forge/tasks/{tid}/plan.md':\n- " + "\n- ".join(defects[:3]))


def _synth_handoff(task_id: str, step_id: str, parsed: Optional[Dict[str, Any]], defects: List[str]) -> Dict[str, Any]:
    """A handoff block stamped UNVERIFIED after the two-block cap (design §5.5)."""
    out: Dict[str, Any] = {"schema": common.SCHEMA_HANDOFF, "task": task_id, "step": step_id, "files_changed": [],
                           "checks_run": [], "not_verified": [], "failed_approaches": [], "next_action": "", "commit": None}
    if parsed:
        out.update(parsed)
    out["status"] = "UNVERIFIED"
    out["gate_defects"] = defects
    return out


def _commit_step(ctx: Ctx, task_id: str, step_id: str, title: str, attempt: int,
                 allowed_paths: List[str]) -> Tuple[Optional[str], str]:
    """`git add -A -- <changed files under allowed_paths> .forge/tasks/<id>/ && git commit` (design §3 step 8)."""
    from . import gates
    root = ctx.paths.root
    files = gates.tree_changed(ctx.paths, allowed_paths)
    # review #17: pre-validation drafts under .forge/tasks/<id>/drafts/ are scratch, never part of the step commit.
    pathspecs = files + [f".forge/tasks/{task_id}/", f":(exclude).forge/tasks/{task_id}/drafts"]
    code, out = common.git(["add", "-A", "--"] + pathspecs, root)
    if code != 0:
        return None, f"git add failed: {out.strip()[:200]}"
    prefix = str((ctx.binding.get("git") or {}).get("commit_prefix") or "forge")
    msg = f"{prefix}({task_id}/{step_id}): {title} [attempt {attempt}]"
    code, out = common.git(["commit", "-q", "-m", msg], root)
    if code != 0:
        return None, f"git commit made no commit: {out.strip()[:200]}"
    return common.git_head(root), "committed"


def _stop_builder(ctx: Ctx, text: str) -> Optional[Dict[str, Any]]:
    """Handoff gate (design §5.5, §7 gate 5): validate, persist, commit, step-report, ledger."""
    from . import gates
    rec = _agent_record(ctx, ctx.agent_id)
    tid, sid = rec.get("task"), rec.get("step")
    if not (rec.get("brief") and tid and sid):
        if _gate_blocks(ctx) >= common.GATE_BLOCK_CAP:
            _journal(ctx, "unbound worker allowed to stop after the block cap; nothing persisted")
            return None
        n = _count_block(ctx, ctx.task_id, "handoff", "worker never read a brief")
        return _block(f"Handoff gate ({n}/{common.GATE_BLOCK_CAP}): you never read a brief. Read "
                      f".forge/tasks/{ctx.task_id or '<task>'}/brief-NN.md with the Read tool, do the work, then redo your HANDOFF.")
    tid, sid = str(tid), str(sid)
    _reset_blocks_on_resume(ctx)   # review-2 #13: a resumed worker's handoff gate starts from a clean counter
    task = ctx.task if ctx.task and ctx.task.get("id") == tid else None
    step = common.find_step(task, sid) if task else None
    # review #14: a worker resumed (SendMessage) after its return was recorded answers in prose; its step is
    # reported/verifying/done and no transition is expected, so the gate neither validates nor persists.
    if step and step.get("status") not in ("running", "failed", "blocked"):
        _journal(ctx, f"non-handoff return on step {sid} ({step.get('status')}); nothing validated or persisted", tid)
        return None
    handoff_shaped = bool(common.json_block(text)) or any(
        gates._heading_present(common.headings(text), h) for h in common.HANDOFF_MANDATORY_HEADINGS)
    if step and step.get("report") and rec.get("handoff_persisted") and not handoff_shaped:
        # a resumed worker on a failed/blocked step answering a question: its earlier report stands.
        _journal(ctx, f"non-handoff return on step {sid} ({step.get('status')}, report {step.get('report')} on file); "
                      "nothing persisted", tid)
        return None
    red_ok = bool(step and step.get("red_ok_until"))
    defects, parsed = gates.handoff_validate(ctx.paths, tid, sid, text, agent_id=ctx.agent_id, red_ok=red_ok)
    blocks = _gate_blocks(ctx)
    if defects and blocks < common.GATE_BLOCK_CAP:
        n = _count_block(ctx, tid, "handoff", "; ".join(defects[:3]))
        return _block(f"Handoff gate ({n}/{common.GATE_BLOCK_CAP}) refused your return:\n- " + "\n- ".join(defects)
                      + f"\nFix, re-run .forge/bin/forge-check {tid} {sid} after your last edit, pre-validate with "
                        f".forge/bin/forge-gate --handoff {tid} {sid} --from-file .forge/tasks/{tid}/drafts/{ctx.agent_id}-handoff.md "
                        f"--agent {ctx.agent_id}, then redo the HANDOFF.")
    unverified = bool(defects)
    if unverified:
        parsed = _synth_handoff(tid, sid, parsed, defects)
        _journal(ctx, f"HANDOFF-GATE-BYPASSED after {blocks} blocks; stamped UNVERIFIED; defects: " + " | ".join(defects[:3]), tid)
        existing = str((step or {}).get("report") or "")
        if existing and common.exists(os.path.join(ctx.paths.root, existing)):
            # review #14: never overwrite this attempt's recorded report with the synthesized stub.
            stub_md = ctx.paths.task_file(tid, f"report-{sid}.unverified.md")
            stub_js = ctx.paths.task_file(tid, f"report-{sid}.unverified.json")
            common.write_text_atomic(stub_md, text if text.endswith("\n") else text + "\n")
            common.write_json_atomic(stub_js, parsed)
            _journal(ctx, f"UNVERIFIED stub written to {ctx.paths.rel(stub_js)}; {existing} left intact; no transition", tid)
            return None
    assert parsed is not None
    md, js = gates.persist_handoff(ctx.paths, tid, sid, text, parsed)
    _merge_agent_record(ctx, ctx.agent_id, handoff_persisted=js)
    commit: Optional[str] = None
    if not unverified and parsed.get("status") in ("DONE", "DONE_WITH_CONCERNS"):
        bm = gates.brief_meta(ctx.paths, tid, sid) or {}
        title = str((step or {}).get("title") or bm.get("step") or sid)
        attempt = int((step or {}).get("attempts") or 1)
        commit, why = _commit_step(ctx, tid, sid, title, attempt, _str_list(bm.get("allowed_paths")))
        parsed["commit"] = commit
        code, branch = common.git(["rev-parse", "--abbrev-ref", "HEAD"], ctx.paths.root)
        if code == 0 and branch.strip():
            parsed["branch"] = branch.strip()
        common.write_json_atomic(os.path.join(ctx.paths.root, js), parsed)
        _journal(ctx, f"handoff {parsed.get('status')} persisted {js}; {why}" + (f" {commit[:7]}" if commit else ""), tid)
    else:
        _journal(ctx, f"handoff {parsed.get('status')} persisted {js} (no commit)", tid)
    # step_report writes the ledger `attempt` row (with gate_blocks); on failure the architect's manual
    # step-report writes it, so the hook never duplicates it.
    ok, msg = _status_call(ctx, "step_report", tid, sid, js)
    if not ok:
        _touch(ctx, "dirty-worker")   # design §6 layer 2: the Stop gate insists on the repair
        _journal(ctx, f"forge-status step-report {tid} {sid} failed: {msg}; dirty-worker set", tid)
    return None


def _resolve_verify_step(ctx: Ctx, rec: Dict[str, Any], task: Optional[Dict[str, Any]], text: str) -> str:
    """The step a verifier graded: its record, else the one `verifying` step, else the JSON block, else `main`."""
    if rec.get("verify_step"):
        return str(rec["verify_step"])
    verifying = _steps_with(task, "verifying")
    if len(verifying) == 1:
        return str(verifying[0].get("id"))
    block = common.json_block(text) or {}
    sid = block.get("step")
    if isinstance(sid, str) and (sid == "main" or (task and common.find_step(task, sid))):
        return sid
    return "main"


def _synth_verdict(task_id: str, step_id: str, parsed: Optional[Dict[str, Any]], defects: List[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"schema": common.SCHEMA_VERDICT, "task": task_id, "step": step_id, "range": "unknown",
                           "criteria": [], "scope_check": "FAIL", "ratchet": "UNKNOWN", "blocking_findings": [],
                           "deferred_findings": [], "tags": []}
    if parsed:
        out.update(parsed)
    out["verdict"] = "UNKNOWN"
    out["gate_defects"] = defects
    return out


def _stop_verifier(ctx: Ctx, text: str) -> Optional[Dict[str, Any]]:
    """Verdict gate (design §5.6, §7 gate 7): validate, persist, step-verdict, ledger."""
    from . import gates
    rec = _agent_record(ctx, ctx.agent_id)
    tid = str(rec.get("task") or ctx.task_id or "")
    if not tid:
        return _block("no Forge task is open; nothing to verify")
    task = ctx.task if ctx.task and ctx.task.get("id") == tid else None
    sid = _resolve_verify_step(ctx, rec, task, text)
    step = common.find_step(task, sid) if task else None
    # review #14: a verifier resumed after its verdict was recorded (step no longer verifying, or this agent's
    # inline verdict already on file) answers in prose; nothing is validated, persisted or transitioned.
    if step is not None and step.get("status") != "verifying":
        _journal(ctx, f"non-verdict return on step {sid} ({step.get('status')}); nothing validated or persisted", tid)
        return None
    if step is None and rec.get("verdict_persisted"):
        _journal(ctx, f"non-verdict return: inline verdict {rec.get('verdict_persisted')} already on file; nothing persisted", tid)
        return None
    defects, parsed = gates.verdict_validate(ctx.paths, tid, sid, text, agent_id=ctx.agent_id)
    blocks = _gate_blocks(ctx)
    if defects and blocks < common.GATE_BLOCK_CAP:
        n = _count_block(ctx, tid, "verdict", "; ".join(defects[:3]))
        return _block(f"Verdict gate ({n}/{common.GATE_BLOCK_CAP}) refused your return:\n- " + "\n- ".join(defects)
                      + f"\nRun .forge/bin/forge-check {tid} {sid} yourself for every cited command, then redo the VERDICT.")
    if defects:
        parsed = _synth_verdict(tid, sid, parsed, defects)
        _journal(ctx, f"VERDICT-GATE-BYPASSED after {blocks} blocks; verdict rewritten UNKNOWN; defects: " + " | ".join(defects[:3]), tid)
    assert parsed is not None
    md, js = gates.persist_verdict(ctx.paths, tid, sid, text, parsed)
    _merge_agent_record(ctx, ctx.agent_id, verdict_persisted=js)
    if sid == "main" or not (task and common.find_step(task, sid)):
        # Inline tasks (S/X, or an L spot-check once every step is done): forge-status step-verdict
        # <id> main records task.inline_verdict, writes the ledger `verdict` row and sets the phase
        # (review #22). If that call fails, fall back to a journal line + ledger row and mark
        # dirty-worker so the Stop gate asks the architect to repair STATUS.
        ok, msg = _status_call(ctx, "step_verdict", tid, "main", js)
        if ok:
            _journal(ctx, f"inline verdict {parsed.get('verdict')} recorded from {js}", tid)
            return None
        _touch(ctx, "dirty-worker")
        _journal(ctx, f"forge-status step-verdict {tid} main failed: {msg}; dirty-worker set; verdict file {js}", tid)
        prev = _last_dispatch(ctx, tid, None, "forge-verifier") or {}
        common.ledger(ctx.paths, {"event": "verdict", "task": tid, "step": sid, "class": (task or {}).get("class"),
                                  "agent": "forge-verifier", "verdict": parsed.get("verdict"),
                                  "verifier_model": prev.get("model"), "tags": parsed.get("tags") or [],
                                  "gate_blocks": blocks, "session_id": ctx.session_id})
        return None
    # step_verdict writes the ledger `verdict` row itself.
    ok, msg = _status_call(ctx, "step_verdict", tid, sid, js)
    if not ok:
        _touch(ctx, "dirty-worker")
        _journal(ctx, f"forge-status step-verdict {tid} {sid} failed: {msg}; dirty-worker set", tid)
    else:
        _journal(ctx, f"verdict {parsed.get('verdict')} persisted {js}; step-verdict applied", tid)
    return None


# --------------------------------------------------------------------------- #
# Stop gate (design §3 step 12, §6 layer 2, §7 gate 11)
# --------------------------------------------------------------------------- #
def _suggest_subcommand(task: Dict[str, Any]) -> str:
    """The forge-status subcommand the Stop gate names for dirty-main: one that fits the first step that is not
    done (review-2 #15: `close` only when every step is done, since close refuses a blocked or external step)."""
    tid, phase = task.get("id"), task.get("phase")
    steps = _steps(task)
    if phase == "plan":
        return f"plan {tid} --from .forge/tasks/{tid}/plan.md"
    if phase == "intake":
        return f"classify {tid} --class <C> --risk <R> --why \"...\""
    if phase == "close":
        return f"close {tid} ..."
    if not steps:
        return f"evidence {tid} --claim \"...\" --from-check <checks/ record>, or close {tid}"
    for status, form in (("running", "step-report {tid} {sid} --report .forge/tasks/{tid}/report-{sid}.json (or recover {tid} {sid})"),
                         ("reported", "step-verdict {tid} {sid} --verdict .forge/tasks/{tid}/verdict-{sid}.json"),
                         ("verifying", "step-verdict {tid} {sid} --verdict .forge/tasks/{tid}/verdict-{sid}.json"),
                         ("failed", "step-start {tid} {sid} --from failed|clean"),
                         ("blocked", "step-start {tid} {sid} --from failed|clean, or block --on \"...\""),
                         ("awaiting_external", "attest {tid} {sid} <DoD-n> --by <you> --evidence <url|path>"),
                         ("pending", "dispatch step {sid} per next_action; the spawn guard runs step-start")):
        found = _steps_with(task, status)
        if found:
            return form.format(tid=tid, sid=found[0].get("id"))
    if all(s.get("status") == "done" for s in steps):
        return f"close {tid}"
    return f"evidence {tid} --claim \"...\" --from-check <checks/ record>"


def on_stop(ctx: Ctx) -> Optional[Dict[str, Any]]:
    paths = ctx.paths
    if ctx.status is None:
        return _system(f"Forge: STATUS.json unreadable ({ctx.status_error}); run .forge/bin/forge-status validate")
    task = ctx.task
    sha = common.sha256_file(paths.status) or ""
    if task is None or task.get("phase") in STOP_ALLOW_PHASES:
        # review #15: no transition can be owed while idle or in a terminal phase; a leaked marker would
        # otherwise block manual compaction for good (block/unblock/close never clear dirty-worker).
        for name in ("dirty-main", "dirty-worker", "stale-status"):
            if _marker(ctx, name):
                _rm(ctx, name)
                _journal(ctx, f"{name} cleared on stop ({'idle' if task is None else 'phase ' + str(task.get('phase'))})")
        return None
    if ctx.stdin.get("stop_hook_active") is True and sha == _read_marker(ctx, "last-block.sha"):
        return None   # RCC line 304: never re-block on an unchanged state
    dirty_main, dirty_worker = _marker(ctx, "dirty-main"), _marker(ctx, "dirty-worker")
    if _marker(ctx, "chat-turn") and not dirty_main and not dirty_worker:
        return None
    reason = None
    tid = task.get("id")
    if dirty_worker:
        pending = _steps_with(task, "running", "reported", "verifying")
        sid = pending[0].get("id") if pending else "<NN>"
        reason = (f"a worker's report/verdict was persisted but STATUS was not updated: run "
                  f".forge/bin/forge-status step-report|step-verdict {tid} {sid}")
    elif dirty_main:
        reason = f"record the state with .forge/bin/forge-status ({_suggest_subcommand(task)}) before ending the turn"
    else:
        recorded = _read_marker(ctx, "status.sha")
        if recorded and sha != recorded:
            reason = "STATUS.json was edited by hand: .forge/bin/forge-status validate --restamp"
    if not reason:
        _rm(ctx, "stale-status")   # STATUS reflects the turn again
        return None
    n = int(_read_marker(ctx, "stop-blocks") or 0)
    if n >= common.STOP_SOFT_CAP:
        _touch(ctx, "stale-status")
        _journal(ctx, f"stop gate soft cap reached ({n}); marked stale: {reason}")
        return _system("STATUS not updated this turn; marked stale")
    common.write_text_atomic(paths.rt("stop-blocks"), f"{n + 1}\n")
    common.write_text_atomic(paths.rt("last-block.sha"), sha + "\n")
    _journal(ctx, f"stop gate block {n + 1}: {reason}")
    return _block(reason)


# --------------------------------------------------------------------------- #
# PreCompact (design §6 layer 6)
# --------------------------------------------------------------------------- #
def on_pre_compact(ctx: Ctx) -> Optional[Dict[str, Any]]:
    if ctx.stdin.get("trigger") != "manual":
        return None   # RCC line 423: never block auto compaction
    task = ctx.task
    if task is None or task.get("phase") in STOP_ALLOW_PHASES:
        return None   # review #15: dirty markers mean nothing while idle or in a terminal phase
    if _marker(ctx, "dirty-main") or _marker(ctx, "dirty-worker"):
        _journal(ctx, "manual compaction blocked: dirty markers present")
        return _block("checkpoint with .forge/bin/forge-status, then /compact")
    return None


# --------------------------------------------------------------------------- #
# ConfigChange guard (design §7 gate 14)
# --------------------------------------------------------------------------- #
def _forge_hook_entries(settings: Dict[str, Any]) -> Dict[Tuple[str, str], Tuple[str, Optional[str]]]:
    """{(event, matcher): (normalised command, onFailure)} for every Forge hook entry in `settings`."""
    out: Dict[Tuple[str, str], Tuple[str, Optional[str]]] = {}
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return out
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            continue
        for g in groups:
            if not isinstance(g, dict):
                continue
            matcher = str(g.get("matcher") or "")
            for h in g.get("hooks", []) or []:
                if not isinstance(h, dict):
                    continue
                cmd = str(h.get("command") or "")
                if not _FORGE_HOOK_CMD_RE.search(cmd):
                    continue
                norm = " ".join(cmd.replace('"', "").replace("'", "").split())
                key = (str(event), matcher if "--role" not in norm else matcher + " --role")
                out[key] = (norm, h.get("onFailure"))
    return out


def on_config_change(ctx: Ctx) -> Optional[Dict[str, Any]]:
    source = str(ctx.stdin.get("source") or "")
    if source not in ("project_settings", "local_settings"):
        return None
    paths = ctx.paths
    changed = str(ctx.stdin.get("file_path") or "")
    if not changed:
        changed = paths.settings if source == "project_settings" else os.path.join(paths.claude_dir, "settings.local.json")
    fragment = common.read_json(paths.settings_fragment, default=None) if common.exists(paths.settings_fragment) else None
    if not isinstance(fragment, dict):
        return None   # nothing to compare against
    try:
        current = common.read_json(changed, default={})
    except common.ForgeError as e:
        if source == "project_settings":
            _journal(ctx, f"CONFIG-GUARD: {changed} unparseable: {e}")
            return _block(f"Forge hooks changed: {paths.rel(changed)} is not valid JSON ({e}); restore it or run install.sh --upgrade")
        return None
    want = _forge_hook_entries(fragment)
    have = _forge_hook_entries(current if isinstance(current, dict) else {})
    problems: List[str] = []
    for key, (cmd, on_failure) in want.items():
        event = key[0]
        if _marker(ctx, f"gate-disabled-{event}") or _marker(ctx, "gate-disabled-all"):
            continue
        got = have.get(key)
        if got is None:
            if source == "project_settings":
                problems.append(f"{event} [{key[1] or '*'}] missing")
            continue
        if got[0] != cmd or (got[1] or None) != (on_failure or None):
            problems.append(f"{event} [{key[1] or '*'}] altered")
    if not problems:
        return None
    _journal(ctx, "CONFIG-GUARD: " + "; ".join(problems))
    # review #62: the bypass is the operator's shell command, not the /forge-doctor skill (which never disables a gate).
    return _block("Forge hooks changed: run install.sh --upgrade, or (operator only, from a shell) "
                  "`.forge/bin/forge-doctor --disable-gate <name>` (" + "; ".join(problems) + ")")


# --------------------------------------------------------------------------- #
# StopFailure, SessionEnd (design §6 failure table)
# --------------------------------------------------------------------------- #
def on_stop_failure(ctx: Ctx) -> Optional[Dict[str, Any]]:
    ts = common.now_ts()
    path = os.path.join(ctx.paths.incidents, f"{ts}-stopfailure.json")
    common.write_json_atomic(path, ctx.stdin)
    _journal(ctx, f"StopFailure {ctx.stdin.get('error') or ctx.stdin.get('reason') or ''}: {ctx.paths.rel(path)}")
    return None


def on_session_end(ctx: Ctx) -> Optional[Dict[str, Any]]:
    task = ctx.task
    running = [s.get("id") for s in _steps_with(task, "running")]
    common.write_json_atomic(ctx.paths.rt("last-session.json"), {
        "session_id": ctx.session_id, "reason": ctx.stdin.get("reason"), "ts": common.now_ts(),
        "task": task.get("id") if task else None, "phase": task.get("phase") if task else None,
        "step_running": running[0] if running else None})
    _journal(ctx, f"session end ({ctx.stdin.get('reason')})")
    return None


# --------------------------------------------------------------------------- #
# Dispatch
# --------------------------------------------------------------------------- #
HANDLERS = {
    "SessionStart": on_session_start,
    "UserPromptSubmit": on_user_prompt_submit,
    "PreToolUse": on_pre_tool_use,
    "PostToolUse": on_post_tool_use,
    "PostToolUseFailure": on_post_tool_use_failure,
    "SubagentStart": on_subagent_start,
    "SubagentStop": on_subagent_stop,
    "Stop": on_stop,
    "PreCompact": on_pre_compact,
    "ConfigChange": on_config_change,
    "StopFailure": on_stop_failure,
    "SessionEnd": on_session_end,
}


def _crash_output(event: str, exc: BaseException) -> Dict[str, Any]:
    """Fail closed for the gate events, open with a systemMessage for the rest (MODULE-API §6)."""
    what = f"{type(exc).__name__}: {exc}"
    if event == "PreToolUse":
        return _deny(f"Forge hook crashed ({what}); run /forge-doctor")
    if event == "SubagentStop":
        return _block(f"Forge hook crashed ({what}); run /forge-doctor")
    if event == "Stop":
        return _system("Forge Stop gate crashed: run /forge-doctor")
    return _system(f"Forge hook crashed ({event or 'unknown event'}): run /forge-doctor")


def dispatch(stdin: Dict[str, Any], flags: set) -> Optional[Dict[str, Any]]:
    """Run the handler for `stdin.hook_event_name`; return the stdout JSON or None.

    flags ⊆ {"role", "plugin"}. `--plugin` returns None at once when `<root>/.forge/VERSION`
    exists (the plain-layout install owns the hooks; design §13.5) and, reviews #1/#2/#37, when the
    resolved root carries no Forge install at all (neither `.forge/binding.json` nor `.forge/STATUS.json`):
    a user-scope plugin must be a complete no-op in every other repository (no output, no files).
    Never raises."""
    event = str(stdin.get("hook_event_name") or "")
    try:
        if "plugin" in flags and not plugin_owns_hooks(common.Paths()):
            return None
        handler = HANDLERS.get(event)
        if handler is None:
            return None
        return handler(Ctx(stdin, flags))
    except Exception as exc:  # noqa: BLE001 — the dispatcher's contract is "never crash the hook"
        tb = traceback.format_exc()
        common.eprint(f"forge-hook: {event} handler crashed:\n{tb}")
        try:
            paths = common.Paths()
            if os.path.isdir(paths.forge):   # review #37: never create .forge/ as a side effect
                common.journal(paths, None, f"[{event}] CRASH {type(exc).__name__}: {exc}")
        except Exception:
            pass
        return _crash_output(event, exc)


def plugin_owns_hooks(paths: common.Paths) -> bool:
    """True when the plugin form must run the handlers: a Forge install (binding.json or STATUS.json) exists
    at the resolved root and `.forge/VERSION` does not (the plain layout registers its own hooks)."""
    if common.exists(paths.version_file):
        return False
    return common.exists(paths.binding) or common.exists(paths.status)
