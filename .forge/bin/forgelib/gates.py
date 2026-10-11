"""Validators shared by forge-gate, the SubagentStop hooks and forge-status (MODULE-API §4).

Everything here is pure (reads files, runs read-only git) except persist_handoff and
persist_verdict, which write the report-NN / verdict-NN / handoff files.

Rules implemented:
  * plan gate          design §5.3, §7 gate 0, schemas/plan.json + schemas/brief.json
  * handoff gate       design §5.5, §7 gate 5, schemas/handoff.json
  * verdict gate       design §5.6, §7 gate 7, schemas/verdict.json
  * Bash heuristics    design §13.3: looks_mutating (main-session mutation heuristic),
                       ro_allowed (read-only allow-list), irreversible_match (binding patterns);
                       split_segments / mask_quotes are quote-aware and split on newlines too
  * helpers for hooks  commit_pathspecs / drafts_exclude_pathspec (step commit minus drafts),
                       verifier_agents / bound_agents (agent resolution), valid_component
"""
from __future__ import annotations

import glob as _glob
import os
import re
import shlex
from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import common

# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
_DOD_ID_RE = re.compile(r"^DoD-[0-9]+$")
_STEP_ID_RE = re.compile(r"^[0-9]{2}$")
_RECORD_RE = re.compile(r"^(?P<step>[^-]+)-(?P<ts>\d+)-(?P<agent>.+)\.json$")
# Paths that never count as tree changes for a worker (design §5.5).
_TREE_IGNORED_PREFIXES = (".forge/", ".claude/agent-memory/")
# Pre-validation drafts (review #17): `.forge/tasks/<id>/drafts/<agent_id>-*.md`, written by workers and
# verifiers for `forge-gate --from-file`; never a tree change, never committed (see commit_pathspecs).
_DRAFT_REL_RE = re.compile(r"^\.forge/tasks/[^/]+/drafts(/|$)")
# Path components that reach the filesystem (step ids, agent ids; review #31).
_PATH_COMPONENT_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
_TASK_ID_RE = re.compile(r"^T-[0-9]{4,}$")
# Test-file heuristic when binding.test_globs is empty (review #27).
_TEST_PATH_RE = re.compile(r"(^|/)(tests?|__tests__|spec)/|(^|/)test_[^/]*$|_tests?\.[A-Za-z0-9]+$|"
                           r"\.(test|spec)\.[A-Za-z0-9]+$|Tests?\.(kt|java|swift|cs|scala)$")

PLAN_REQUIRED = ("schema", "task", "class", "risk", "chain", "routing", "steps", "dod", "rollback",
                 "test_baseline", "needs_clarification")
PLAN_ROUTING_REQUIRED = ("mode", "builder", "verifier", "justification")
PLAN_STEP_REQUIRED = ("id", "title", "brief", "agent", "model", "effort", "mechanical", "red_ok_until",
                      "max_tool_calls")
BRIEF_REQUIRED = ("schema", "task", "step", "owner_agent", "model", "effort", "allowed_paths", "may_edit_tests",
                  "tdd", "checks", "expected_fail_first", "dod", "risk", "red_ok", "max_tool_calls", "bootstrap")
BRIEF_HEADINGS = ("Goal", "Context the worker needs", "Definition of done", "Out of scope / do not touch",
                  "Known failed approaches", "Output contract")
HANDOFF_REQUIRED = ("schema", "task", "step", "status", "files_changed", "checks_run")
VERDICT_REQUIRED = ("schema", "task", "step", "range", "verdict", "criteria", "scope_check", "ratchet",
                    "blocking_findings", "deferred_findings", "tags")
# A rollback for a risk task must name a command, not only prose (design §5.3 / schemas/plan.json).
_COMMAND_WORD_RE = re.compile(r"(`[^`]+`|\b(git|gh|wrangler|npx|npm|python3?|pytest|rm|mv|cp|kubectl|aws|gsutil|"
                              r"curl|make|docker|terraform|bash|sh)\b)")


def _heading_present(found: Iterable[str], wanted: str) -> bool:
    """A heading matches when it equals `wanted` or starts with it followed by a space or '('
    (templates carry trailing annotations such as '## Goal   (one line)')."""
    w = wanted.strip().lower()
    for h in found:
        hl = h.strip().lower()
        if hl == w or hl.startswith(w + " ") or hl.startswith(w + "("):
            return True
    return False


def missing_headings(text: str, required: Iterable[str]) -> List[str]:
    """Required level-2 headings absent from `text`."""
    found = common.headings(text, 2)
    return [h for h in required if not _heading_present(found, h)]


def _is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _is_str_list(v: Any) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def safe_status(paths: common.Paths) -> Optional[Dict[str, Any]]:
    """STATUS.json when present and valid, else None (validators never crash on its absence)."""
    try:
        return common.load_status(paths)
    except common.ForgeError:
        return None


# --------------------------------------------------------------------------- #
# Meta readers
# --------------------------------------------------------------------------- #
def plan_meta(paths: common.Paths, task_id: str) -> Optional[Dict[str, Any]]:
    """Parsed plan-meta (first ```json block of plan.md) or None."""
    text = common.read_text(paths.task_file(task_id, "plan.md"))
    if text is None:
        return None
    return common.json_block(text)


def brief_meta(paths: common.Paths, task_id: str, step_id: str) -> Optional[Dict[str, Any]]:
    """Parsed brief-meta (first ```json block of brief-<step>.md) or None."""
    text = common.read_text(paths.task_file(task_id, f"brief-{step_id}.md"))
    if text is None:
        return None
    return common.json_block(text)


def task_class(paths: common.Paths, task_id: str, meta: Optional[Dict[str, Any]]) -> Optional[str]:
    """Task class from plan-meta, else from STATUS."""
    if meta and meta.get("class") in common.CLASSES:
        return meta["class"]
    st = safe_status(paths)
    task = common.current_task(st) if st else None
    if task and task.get("id") == task_id:
        return task.get("class")
    return None


def _task_risk(paths: common.Paths, task_id: str, meta: Optional[Dict[str, Any]]) -> str:
    if meta and meta.get("risk") in common.RISKS:
        return meta["risk"]
    st = safe_status(paths)
    task = common.current_task(st) if st else None
    if task and task.get("id") == task_id and task.get("risk") in common.RISKS:
        return task["risk"]
    return "none"


# --------------------------------------------------------------------------- #
# Plan gate (design §5.3, §7 gate 0)
# --------------------------------------------------------------------------- #
def brief_validate(paths: common.Paths, task_id: str, step_id: str) -> List[str]:
    """Defects of brief-<step>.md against schemas/brief.json (headings, keys, invariants)."""
    path = paths.task_file(task_id, f"brief-{step_id}.md")
    text = common.read_text(path)
    rel = paths.rel(path)
    if text is None:
        return [f"{rel}: missing"]
    defects: List[str] = []
    for h in missing_headings(text, BRIEF_HEADINGS):
        defects.append(f"{rel}: missing heading '## {h}'")
    meta = common.json_block(text)
    if meta is None:
        defects.append(f"{rel}: no parseable ```json brief-meta block")
        return defects
    for k in BRIEF_REQUIRED:
        if k not in meta:
            defects.append(f"{rel}: brief-meta missing key '{k}'")
    if meta.get("schema") != common.SCHEMA_BRIEF:
        defects.append(f"{rel}: brief-meta schema must be {common.SCHEMA_BRIEF}")
    if meta.get("task") != task_id:
        defects.append(f"{rel}: brief-meta task {meta.get('task')!r} != {task_id}")
    if meta.get("step") != step_id:
        defects.append(f"{rel}: brief-meta step {meta.get('step')!r} != {step_id}")
    if meta.get("owner_agent") not in common.WORKER_ROLES:
        defects.append(f"{rel}: owner_agent must be one of {'|'.join(common.WORKER_ROLES)}")
    if common.alias_model(meta.get("model")) not in common.MODELS:
        defects.append(f"{rel}: model must be an alias ({'|'.join(common.MODELS)})")
    if meta.get("effort") not in common.EFFORTS:
        defects.append(f"{rel}: effort must be one of {'|'.join(common.EFFORTS)}")
    if not _is_str_list(meta.get("allowed_paths")) or not meta.get("allowed_paths"):
        defects.append(f"{rel}: allowed_paths must be a non-empty list of globs")
    for k in ("checks", "expected_fail_first", "dod"):
        if k in meta and not _is_str_list(meta.get(k)):
            defects.append(f"{rel}: {k} must be a list of strings")
    if meta.get("tdd") is True and not meta.get("expected_fail_first"):
        defects.append(f"{rel}: tdd is true but expected_fail_first is empty")
    # review #19: forge-check runs checks[] only, so a red/green pair can exist only for commands in checks[].
    checks_list = meta.get("checks") if _is_str_list(meta.get("checks")) else []
    for cmd in (meta.get("expected_fail_first") if _is_str_list(meta.get("expected_fail_first")) else []):
        if cmd not in checks_list:
            defects.append(f"{rel}: expected_fail_first cmd `{cmd}` is not in checks[] (forge-check runs checks[] only; "
                           "add it to checks)")
    mtc = meta.get("max_tool_calls")
    if not _is_int(mtc) or mtc < 5:
        defects.append(f"{rel}: max_tool_calls must be an integer >= 5")
    return defects


def plan_validate(paths: common.Paths, task_id: str) -> List[str]:
    """Defects of plan.md (plan-meta, headings for the class, steps/briefs, DoD); [] = valid."""
    path = paths.task_file(task_id, "plan.md")
    rel = paths.rel(path)
    text = common.read_text(path)
    if text is None:
        return [f"{rel}: missing"]
    defects: List[str] = []
    meta = common.json_block(text)
    if meta is None:
        return [f"{rel}: no parseable ```json plan-meta block"]
    for k in PLAN_REQUIRED:
        if k not in meta:
            defects.append(f"plan-meta missing key '{k}'")
    if meta.get("schema") != common.SCHEMA_PLAN:
        defects.append(f"plan-meta schema must be {common.SCHEMA_PLAN}")
    if meta.get("task") != task_id:
        defects.append(f"plan-meta task {meta.get('task')!r} != {task_id}")
    cls = meta.get("class")
    if cls not in common.CLASSES:
        defects.append(f"plan-meta class must be one of {'|'.join(common.CLASSES)}")
    risk = meta.get("risk")
    if risk not in common.RISKS:
        defects.append("plan-meta risk must be none|R")
    if not isinstance(meta.get("chain"), bool):
        defects.append("plan-meta chain must be a boolean")

    # Headings by class (design §5.3: four for M, twelve for W/L, inline section for S/X).
    inline_class = cls in ("S", "X", "T")
    if cls == "M":
        required = common.PLAN_HEADINGS_M
    elif cls in ("W", "L"):
        required = common.PLAN_HEADINGS_FULL
    else:
        required = common.PLAN_HEADINGS_INLINE
    for h in missing_headings(text, required):
        defects.append(f"{rel}: missing heading '## {h}'")

    # Routing block.
    routing = meta.get("routing")
    mode = None
    if not isinstance(routing, dict):
        defects.append("plan-meta routing must be an object")
    else:
        for k in PLAN_ROUTING_REQUIRED:
            if k not in routing:
                defects.append(f"plan-meta routing missing key '{k}'")
        mode = routing.get("mode")
        if mode not in common.MODES:
            defects.append(f"plan-meta routing.mode must be one of {'|'.join(common.MODES)}")

    # Steps and their briefs (schemas/plan.json invariants).
    steps = meta.get("steps")
    if not isinstance(steps, list):
        defects.append("plan-meta steps must be a list")
        steps = []
    if mode == "inline" and steps:
        defects.append("routing.mode inline requires steps == []")
    if mode in ("single", "parallel") and not steps:
        defects.append(f"routing.mode {mode} requires at least one step")
    if cls in ("M", "W") and len(steps) != 1:
        defects.append(f"class {cls} requires exactly one step (found {len(steps)})")
    if cls == "L" and len(steps) < 3:
        defects.append(f"class L requires >= 3 steps (found {len(steps)})")
    if inline_class and steps:
        defects.append(f"class {cls} is inline and must declare steps == []")
    if inline_class and not _is_str_list(meta.get("allowed_paths")):
        defects.append("inline plan-meta must declare allowed_paths (list of globs)")
    step_ids = [s.get("id") for s in steps if isinstance(s, dict)]
    for idx, s in enumerate(steps):
        if not isinstance(s, dict):
            defects.append(f"steps[{idx}] must be an object")
            continue
        sid = s.get("id")
        label = f"step {sid or idx}"
        for k in PLAN_STEP_REQUIRED:
            if k not in s:
                defects.append(f"{label}: missing key '{k}'")
        if not isinstance(sid, str) or not _STEP_ID_RE.match(sid):
            defects.append(f"{label}: id must match ^[0-9]{{2}}$")
            continue
        if step_ids.count(sid) > 1:
            defects.append(f"{label}: duplicate step id")
        if not _is_int(s.get("max_tool_calls")) or s.get("max_tool_calls", 0) < 5:
            defects.append(f"{label}: max_tool_calls must be an integer >= 5")
        if s.get("agent") not in common.WORKER_ROLES:
            defects.append(f"{label}: agent must be one of {'|'.join(common.WORKER_ROLES)}")
        if common.alias_model(s.get("model")) not in common.MODELS:
            defects.append(f"{label}: model must be an alias")
        if s.get("effort") not in common.EFFORTS:
            defects.append(f"{label}: effort must be one of {'|'.join(common.EFFORTS)}")
        brief_name = s.get("brief")
        if brief_name != f"brief-{sid}.md":
            defects.append(f"{label}: brief must be 'brief-{sid}.md' (found {brief_name!r})")
        defects.extend(brief_validate(paths, task_id, sid))
        rou = s.get("red_ok_until")
        if rou is not None:
            # design §3 (L path): red_ok_until names a later step.
            if rou not in step_ids or step_ids.index(rou) <= idx:
                defects.append(f"{label}: red_ok_until {rou!r} must name a later step id")

    # Definition of done.
    dod = meta.get("dod")
    if not isinstance(dod, list) or not dod:
        defects.append("plan-meta dod must be a non-empty list")
        dod = []
    seen_ids: List[str] = []
    for idx, d in enumerate(dod):
        if not isinstance(d, dict):
            defects.append(f"dod[{idx}] must be an object")
            continue
        did = d.get("id")
        if not isinstance(did, str) or not _DOD_ID_RE.match(did):
            defects.append(f"dod[{idx}]: id must match ^DoD-[0-9]+$")
        elif did in seen_ids:
            defects.append(f"{did}: duplicate DoD id")
        else:
            seen_ids.append(did)
        if not isinstance(d.get("criterion"), str) or not d.get("criterion", "").strip():
            defects.append(f"dod[{idx}]: criterion must be a non-empty string")
        chk = d.get("check")
        if not isinstance(chk, str) or not chk.strip():
            defects.append(f"dod[{idx}]: check must be a command or 'external'")
        elif chk == "external":
            ext = d.get("external")
            if not isinstance(ext, dict) or not ext.get("what") or not ext.get("how"):
                defects.append(f"dod[{idx}]: check external needs external.what and external.how")
    # Every brief dod id must exist in the plan.
    for s in steps:
        if isinstance(s, dict) and isinstance(s.get("id"), str):
            bm = brief_meta(paths, task_id, s["id"])
            for did in (bm or {}).get("dod", []) or []:
                if did not in seen_ids:
                    defects.append(f"brief-{s['id']}.md: dod id {did!r} is not in plan-meta.dod")

    # Rollback and baseline.
    rb = meta.get("rollback")
    if not isinstance(rb, str) or not rb.strip():
        defects.append("plan-meta rollback must be a non-empty string")
    elif risk == "R" and not _COMMAND_WORD_RE.search(rb):
        defects.append("risk R: rollback must contain a concrete command")
    tb = meta.get("test_baseline")
    if not isinstance(tb, dict) or not _is_int(tb.get("files")) or not _is_int(tb.get("tests")):
        defects.append("plan-meta test_baseline must be {files: int, tests: int, recorded_at}; "
                       "record it with forge-check <task> plan --baseline")
    if not isinstance(meta.get("needs_clarification"), list):
        defects.append("plan-meta needs_clarification must be a list")
    return defects


# --------------------------------------------------------------------------- #
# Evidence: check records, source edits, tree changes
# --------------------------------------------------------------------------- #
def check_records(paths: common.Paths, task_id: str, step_id: str,
                  agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Parsed checks/<step>-<epoch>-<agent>.json records, newest first.

    Filtered by `agent_id` when given (record field, falling back to the filename suffix). For the
    inline step `main` with `agent_id == "main"`, records still stamped `unknown` count too: they
    were written by `forge-check` outside a hook (an operator terminal), where only the architect
    runs (review #13). Each returned dict gains `_file` (repo-relative path) for messages."""
    d = paths.checks_dir(task_id)
    if not os.path.isdir(d):
        return []
    out: List[Tuple[int, str, Dict[str, Any]]] = []
    for name in os.listdir(d):
        m = _RECORD_RE.match(name)
        if not m or m.group("step") != step_id:
            continue
        try:
            rec = common.read_json(os.path.join(d, name))
        except common.ForgeError:
            continue
        if not isinstance(rec, dict):
            continue
        rec_agent = rec.get("agent_id") or m.group("agent")
        if agent_id is not None and rec_agent != agent_id:
            if not (agent_id == "main" and step_id == "main" and rec_agent == "unknown"):
                continue
        ts = rec.get("ts") if _is_int(rec.get("ts")) else int(m.group("ts"))
        rec["_file"] = paths.rel(os.path.join(d, name))
        out.append((ts, name, rec))
    out.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [r for _, _, r in out]


def last_source_edit_ts(paths: common.Paths, task_id: str, agent_id: Optional[str]) -> Optional[int]:
    """Epoch of the newest `kind: source` edit row for `agent_id` (all agents when None)."""
    rows = common.evidence_rows(paths, task_id, agent_id=agent_id, event=("edit",))
    ts = [r.get("ts") for r in rows if r.get("kind") == "source" and _is_int(r.get("ts"))]
    return max(ts) if ts else None


def source_edits(paths: common.Paths, task_id: str, agent_id: Optional[str]) -> List[str]:
    """Distinct files of `kind: source` edit rows for `agent_id` (all agents when None)."""
    rows = common.evidence_rows(paths, task_id, agent_id=agent_id, event=("edit",))
    return common.unique(paths.rel(r["file"]) for r in rows if r.get("kind") == "source" and r.get("file"))


def is_draft_path(rel: str) -> bool:
    """True for `.forge/tasks/<id>/drafts/**` (pre-validation drafts; review #17)."""
    return _DRAFT_REL_RE.match(rel.replace(os.sep, "/")) is not None


def tree_changed(paths: common.Paths, allowed_paths: List[str]) -> List[str]:
    """`git status --porcelain --untracked-files=all -- <allowed_paths>` filtered to the globs.

    `.forge/**` (drafts included) and `.claude/agent-memory/**` never count (design §5.5)."""
    if not allowed_paths:
        return []
    out: List[str] = []
    for p in common.git_porcelain(paths.root, list(allowed_paths), untracked=True):
        rel = paths.rel(p)
        if rel.startswith(_TREE_IGNORED_PREFIXES) or is_draft_path(rel):
            continue
        # git pathspecs match more loosely than Forge globs; keep only true glob matches.
        if common.any_glob(rel, allowed_paths) is None:
            continue
        out.append(rel)
    return common.unique(out)


def drafts_exclude_pathspec(task_id: Optional[str] = None) -> str:
    """A git pathspec that excludes pre-validation drafts from `git add` (review #17): one task's
    `.forge/tasks/<id>/drafts` when `task_id` is given, every task's otherwise."""
    if task_id:
        return f":(exclude).forge/tasks/{task_id}/drafts"
    return ":(exclude,glob).forge/tasks/*/drafts/**"


def commit_pathspecs(paths: common.Paths, allowed_paths: List[str], task_id: str) -> List[str]:
    """Pathspecs for the step commit (design §3 step 8): the unit's changed files under
    `allowed_paths`, the task directory, minus `.forge/tasks/<id>/drafts` (review #17).
    Use as `git add -A -- <pathspecs>`."""
    return tree_changed(paths, allowed_paths) + [f".forge/tasks/{task_id}/", drafts_exclude_pathspec(task_id)]


def touched_test_file(paths: common.Paths, task_id: str, agent_id: str) -> bool:
    """True when this agent's `kind: source` edit rows name a test file (binding.test_globs, else a
    path heuristic: tests/ dirs, test_*.py, *_test.*, *.test.*, *Test.kt …) (review #27)."""
    try:
        binding = common.load_binding(paths)
    except common.ForgeError:
        binding = {}
    globs = [g for g in binding.get("test_globs", []) or [] if isinstance(g, str)]
    for f in source_edits(paths, task_id, agent_id):
        if globs:
            if common.any_glob(f, globs):
                return True
        elif _TEST_PATH_RE.search(f):
            return True
    return False


def _record_hits(records: List[Dict[str, Any]], cmd: str) -> List[Tuple[int, int, str]]:
    """(ts, exit, file) for every non-skipped result with results[].cmd == cmd."""
    hits: List[Tuple[int, int, str]] = []
    for rec in records:
        ts = rec.get("ts")
        if not _is_int(ts):
            continue
        for res in rec.get("results", []) or []:
            if not isinstance(res, dict) or res.get("cmd") != cmd:
                continue
            if res.get("status") == "skipped" or not _is_int(res.get("exit")):
                continue
            hits.append((ts, res["exit"], rec.get("_file", "")))
    return hits


# --------------------------------------------------------------------------- #
# Step context: where allowed_paths / checks / dod come from
# --------------------------------------------------------------------------- #
def step_context(paths: common.Paths, task_id: str, step_id: str) -> Tuple[Dict[str, Any], List[str]]:
    """Gate inputs for a step: {allowed_paths, checks, expected_fail_first, tdd, dod, dod_checks, red_ok}.

    For an inline step (`main`) the DoD comes from plan-meta and allowed_paths from plan-meta /
    task.scope (MODULE-API §4); otherwise from the brief. Returns (context, defects)."""
    ctx: Dict[str, Any] = {"allowed_paths": [], "checks": [], "expected_fail_first": [], "tdd": False,
                           "dod": [], "dod_checks": {}, "red_ok": False, "may_edit_tests": False}
    pm = plan_meta(paths, task_id)
    for d in (pm or {}).get("dod", []) or []:
        if isinstance(d, dict) and isinstance(d.get("id"), str):
            ctx["dod_checks"][d["id"]] = d.get("check")
    if step_id == "main":
        allowed = (pm or {}).get("allowed_paths")
        if not _is_str_list(allowed) or not allowed:
            st = safe_status(paths)
            task = common.current_task(st) if st else None
            allowed = task.get("scope") if task and task.get("id") == task_id else None
        ctx["allowed_paths"] = list(allowed or [])
        ctx["dod"] = list(ctx["dod_checks"].keys())
        ctx["checks"] = common.unique(c for c in ctx["dod_checks"].values()
                                      if isinstance(c, str) and c and c != "external")
        if not ctx["allowed_paths"]:
            return ctx, [f"{task_id}: no allowed_paths for inline step main (plan-meta.allowed_paths or task.scope)"]
        return ctx, []
    bm = brief_meta(paths, task_id, step_id)
    if bm is None:
        return ctx, [f".forge/tasks/{task_id}/brief-{step_id}.md: missing or no brief-meta"]
    ctx["allowed_paths"] = list(bm.get("allowed_paths") or [])
    ctx["checks"] = [c for c in bm.get("checks") or [] if isinstance(c, str)]
    ctx["expected_fail_first"] = [c for c in bm.get("expected_fail_first") or [] if isinstance(c, str)]
    ctx["tdd"] = bm.get("tdd") is True
    ctx["dod"] = [d for d in bm.get("dod") or [] if isinstance(d, str)]
    ctx["red_ok"] = bm.get("red_ok") is True
    ctx["may_edit_tests"] = bm.get("may_edit_tests") is True
    return ctx, []


# --------------------------------------------------------------------------- #
# Handoff gate (design §5.5)
# --------------------------------------------------------------------------- #
def handoff_validate(paths: common.Paths, task_id: str, step_id: str, text: str, agent_id: Optional[str] = None,
                     red_ok: bool = False, short: bool = False,
                     task_level: bool = False) -> Tuple[List[str], Optional[Dict[str, Any]]]:
    """Validate a HANDOFF message. Returns (defects, parsed JSON block or None).

    agent_id None skips the agent-scoped rules (source edits; checks are then matched over
    records by any agent). `red_ok` lets check records pass at any exit (red_ok_until steps)."""
    defects: List[str] = []
    required_headings = common.HANDOFF_SHORT_HEADINGS if short else common.HANDOFF_MANDATORY_HEADINGS
    for h in missing_headings(text, required_headings):
        defects.append(f"missing heading '## {h}'")
    parsed = common.json_block(text)
    if parsed is None:
        defects.append(f"no parseable ```json block (schema {common.SCHEMA_HANDOFF})")
        return defects, None
    for k in HANDOFF_REQUIRED:
        if k not in parsed:
            defects.append(f"json missing key '{k}'")
    if parsed.get("schema") != common.SCHEMA_HANDOFF:
        defects.append(f"json schema must be {common.SCHEMA_HANDOFF}")
    if parsed.get("task") != task_id:
        defects.append(f"json task {parsed.get('task')!r} != {task_id}")
    status = parsed.get("status")
    if status not in common.HANDOFF_STATUSES:
        defects.append(f"json status must be one of {'|'.join(common.HANDOFF_STATUSES)}")
    files_changed = parsed.get("files_changed")
    if not _is_str_list(files_changed):
        defects.append("json files_changed must be a list of paths")
        files_changed = []
    checks_run = parsed.get("checks_run")
    if not isinstance(checks_run, list) or not all(isinstance(c, dict) for c in checks_run):
        defects.append("json checks_run must be a list of {cmd, exit, expected_fail?}")

    if task_level:
        # MODULE-API §4: task-level handoffs need headings + a valid block with step == "task".
        if parsed.get("step") != "task":
            defects.append("task-level handoff json step must be \"task\"")
        return defects, parsed

    if parsed.get("step") != step_id:
        defects.append(f"json step {parsed.get('step')!r} != {step_id}")
    ctx, ctx_defects = step_context(paths, task_id, step_id)
    if ctx_defects:
        defects.extend(ctx_defects)
        return defects, parsed
    allowed = ctx["allowed_paths"]
    red_ok = red_ok or ctx["red_ok"]

    # files_changed ⊆ allowed_paths (globs).
    files_changed = [paths.rel(f) for f in files_changed]
    for f in files_changed:
        if common.any_glob(f, allowed) is None:
            defects.append(f"files_changed: {f} is outside allowed_paths")
    # source_edits(agent_id) ⊆ files_changed.
    if agent_id is not None:
        for f in source_edits(paths, task_id, agent_id):
            if f not in files_changed:
                defects.append(f"evidence: {agent_id} edited {f} but files_changed omits it")
    # tree_changed(allowed_paths) ⊆ files_changed.
    for f in tree_changed(paths, allowed):
        if f not in files_changed:
            defects.append(f"git: {f} changed under allowed_paths but files_changed omits it")

    # BLOCKED | NEEDS_CONTEXT (and UNVERIFIED) need no check records.
    if status not in ("DONE", "DONE_WITH_CONCERNS"):
        return defects, parsed

    records = check_records(paths, task_id, step_id, agent_id)
    who = agent_id or "any agent"
    last_edit = last_source_edit_ts(paths, task_id, agent_id)
    for cmd in ctx["checks"]:
        hits = _record_hits(records, cmd)
        good = [h for h in hits if red_ok or h[1] == 0]
        if not good:
            if hits:
                defects.append(f"check `{cmd}`: newest record by {who} exited {hits[0][1]} ({hits[0][2]}); needs exit 0")
            else:
                defects.append(f"check `{cmd}`: no checks/ record by {who}; run .forge/bin/forge-check {task_id} {step_id}")
            continue
        # design §5.5: the passing record must be newer than this agent's last source edit.
        newest = max(good, key=lambda h: h[0])
        if last_edit is not None and newest[0] < last_edit:
            defects.append(f"check `{cmd}`: passing record ts={newest[0]} ({newest[2]}) is older than the last "
                           f"source edit ts={last_edit}; re-run .forge/bin/forge-check {task_id} {step_id}")
    if ctx["tdd"] and ctx["expected_fail_first"]:
        # design §5.5: a non-zero (red) record strictly earlier than a zero (green) record. The red
        # may be any agent's (a retry worker inherits attempt 1's red run); the green is this agent's.
        # The rule binds only an agent whose own evidence shows it created or modified a test file:
        # a retry worker on an already-green tree that wrote no test has no red to show (review #27).
        all_records = check_records(paths, task_id, step_id)
        binds = agent_id is None or touched_test_file(paths, task_id, agent_id)
        for cmd in ctx["expected_fail_first"]:
            reds = [h[0] for h in _record_hits(all_records, cmd) if h[1] != 0]
            greens = [h[0] for h in _record_hits(records, cmd) if h[1] == 0]
            if reds and greens and min(reds) < max(greens):
                continue
            if not binds:
                continue
            defects.append(f"tdd: `{cmd}` needs a failing record (forge-check --expect-fail, by any agent) earlier "
                           f"than a passing one by {who}")
    return defects, parsed


# --------------------------------------------------------------------------- #
# Verdict gate (design §5.6)
# --------------------------------------------------------------------------- #
def verdict_validate(paths: common.Paths, task_id: str, step_id: str, text: str,
                     agent_id: Optional[str] = None) -> Tuple[List[str], Optional[Dict[str, Any]]]:
    """Validate a VERDICT message. Returns (defects, parsed JSON block or None).

    agent_id None skips the "cited cmd has a record by this verifier" rule."""
    defects: List[str] = []
    for h in missing_headings(text, common.VERDICT_HEADINGS):
        defects.append(f"missing heading '## {h}'")
    parsed = common.json_block(text)
    if parsed is None:
        defects.append(f"no parseable ```json block (schema {common.SCHEMA_VERDICT})")
        return defects, None
    for k in VERDICT_REQUIRED:
        if k not in parsed:
            defects.append(f"json missing key '{k}'")
    if parsed.get("schema") != common.SCHEMA_VERDICT:
        defects.append(f"json schema must be {common.SCHEMA_VERDICT}")
    if parsed.get("task") != task_id:
        defects.append(f"json task {parsed.get('task')!r} != {task_id}")
    if parsed.get("step") != step_id:
        defects.append(f"json step {parsed.get('step')!r} != {step_id}")
    verdict = parsed.get("verdict")
    if verdict not in common.VERDICTS:
        defects.append(f"json verdict must be one of {'|'.join(common.VERDICTS)}")
    if parsed.get("scope_check") not in ("PASS", "FAIL"):
        defects.append("json scope_check must be PASS|FAIL")
    if parsed.get("ratchet") not in common.VERDICTS:
        defects.append("json ratchet must be PASS|FAIL|UNKNOWN")
    for k in ("blocking_findings", "deferred_findings"):
        if not _is_str_list(parsed.get(k)):
            defects.append(f"json {k} must be a list of strings")
    tags = parsed.get("tags")
    if not _is_str_list(tags):
        defects.append("json tags must be a list")
        tags = []
    for t in tags:
        if t not in common.VERDICT_TAGS:
            defects.append(f"json tags: unknown tag {t!r} (allowed: {', '.join(common.VERDICT_TAGS)})")

    ctx, ctx_defects = step_context(paths, task_id, step_id)
    if ctx_defects:
        defects.extend(ctx_defects)
        return defects, parsed
    dod_ids = ctx["dod"]
    dod_checks = ctx["dod_checks"]
    criteria = parsed.get("criteria")
    if not isinstance(criteria, list) or not all(isinstance(c, dict) for c in criteria):
        defects.append("json criteria must be a list of {id, result, cmd, exit}")
        return defects, parsed
    cited = [c.get("id") for c in criteria]
    for did in dod_ids:
        n = cited.count(did)
        if n != 1:
            defects.append(f"criteria: {did} must appear exactly once (found {n})")
    for c in criteria:
        if c.get("id") not in dod_ids:
            defects.append(f"criteria: {c.get('id')!r} is not a DoD id of this step")

    records = check_records(paths, task_id, step_id, agent_id) if agent_id is not None else []
    human = check_records(paths, task_id, step_id, "human")
    all_pass = True
    any_unknown = False
    for c in criteria:
        cid = c.get("id")
        result = c.get("result")
        if result not in common.CRITERION_RESULTS:
            defects.append(f"{cid}: result must be PASS|FAIL|UNKNOWN")
            all_pass = False
            continue
        if result != "PASS":
            all_pass = False
        if result == "UNKNOWN":
            any_unknown = True
        if not isinstance(c.get("cmd"), str):
            defects.append(f"{cid}: cmd must be a string")
        if not _is_int(c.get("exit")):
            defects.append(f"{cid}: exit must be numeric")
        if cid not in dod_ids:
            continue
        if dod_checks.get(cid) == "external":
            # design §5.6 / §7 gate 13: external criteria pass only on a human attest record.
            attested = [r for r in human if r.get("criterion") == cid]
            if not attested and result != "UNKNOWN":
                defects.append(f"{cid}: check is external and no human attest record exists; result must be UNKNOWN "
                               f"(or run .forge/bin/forge-status attest {task_id} {step_id} {cid} ...)")
            continue
        if agent_id is not None and result in ("PASS", "FAIL"):
            # review #20: the record may come from this verifier's own `forge-check <task> <step>` run (which
            # runs the step's DoD checks) or from `forge-check <task> <step> --cmd '<cmd>'`.
            cmd = c.get("cmd") or ""
            if not cmd or not _record_hits(records, cmd):
                defects.append(f"{cid}: cmd `{cmd}` has no checks/ record by {agent_id}; run .forge/bin/forge-check "
                               f"{task_id} {step_id} yourself (or forge-check {task_id} {step_id} --cmd '<that command>')")
    if verdict == "PASS":
        if not all_pass:
            defects.append("verdict PASS requires every criterion PASS")
        if parsed.get("scope_check") != "PASS":
            defects.append("verdict PASS requires scope_check PASS")
        if parsed.get("ratchet") != "PASS":
            defects.append("verdict PASS requires ratchet PASS")
        if parsed.get("blocking_findings"):
            defects.append("verdict PASS requires blocking_findings == []")
    # design §5.6: UNKNOWN on a required criterion ⇒ FAIL for risk R tasks.
    if any_unknown and verdict != "FAIL" and _task_risk(paths, task_id, plan_meta(paths, task_id)) == "R":
        defects.append("risk R: an UNKNOWN criterion requires verdict FAIL")
    return defects, parsed


# --------------------------------------------------------------------------- #
# Persistence (the only writers in this module)
# --------------------------------------------------------------------------- #
def persist_handoff(paths: common.Paths, task_id: str, step_id: str, text: str,
                    parsed: Dict[str, Any]) -> Tuple[str, str]:
    """Write report-<step>.md + report-<step>.json (handoff.md/json for step 'task').
    Returns repo-relative paths (md, json)."""
    stem = "handoff" if step_id == "task" else f"report-{step_id}"
    md = paths.task_file(task_id, f"{stem}.md")
    js = paths.task_file(task_id, f"{stem}.json")
    common.write_text_atomic(md, text if text.endswith("\n") else text + "\n")
    common.write_json_atomic(js, parsed)
    return paths.rel(md), paths.rel(js)


def persist_verdict(paths: common.Paths, task_id: str, step_id: str, text: str,
                    parsed: Dict[str, Any]) -> Tuple[str, str]:
    """Write verdict-<step>.md + verdict-<step>.json. Returns repo-relative paths (md, json)."""
    md = paths.task_file(task_id, f"verdict-{step_id}.md")
    js = paths.task_file(task_id, f"verdict-{step_id}.json")
    common.write_text_atomic(md, text if text.endswith("\n") else text + "\n")
    common.write_json_atomic(js, parsed)
    return paths.rel(md), paths.rel(js)


# --------------------------------------------------------------------------- #
# Agent resolution for the CLI (MODULE-API §4: "exactly one agent bound to that step")
# --------------------------------------------------------------------------- #
def _agent_records(paths: common.Paths) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for f in sorted(_glob.glob(os.path.join(paths.runtime, "agents", "*.json"))):
        try:
            rec = common.read_json(f)
        except common.ForgeError:
            continue
        if isinstance(rec, dict) and rec.get("agent_id"):
            out.append(rec)
    return out


def bound_agents(paths: common.Paths, task_id: str, step_id: str) -> List[str]:
    """agent_ids whose .runtime/agents/<id>.json is bound to (task_id, step_id): the workers
    (a verifier record carries `verify_step`, never `step`; see verifier_agents)."""
    return [str(r["agent_id"]) for r in _agent_records(paths)
            if r.get("task") == task_id and r.get("step") == step_id]


def verifier_agents(paths: common.Paths, task_id: str, step_id: str) -> List[str]:
    """agent_ids of forge-verifier records whose `verify_step` is (task_id, step_id) (review #25):
    the verdict gate resolves to the verifier's OWN records, never a builder's."""
    return [str(r["agent_id"]) for r in _agent_records(paths)
            if r.get("task") == task_id and r.get("verify_step") == step_id
            and common.agent_role(r.get("agent_type")) == "forge-verifier"]


def valid_task_id(task_id: str) -> bool:
    return _TASK_ID_RE.match(str(task_id or "")) is not None


def valid_component(value: str) -> bool:
    """A step or agent id safe as a path component: ^[A-Za-z0-9_.-]{1,64}$ and never `..` (review #31)."""
    v = str(value or "")
    return _PATH_COMPONENT_RE.match(v) is not None and ".." not in v


# --------------------------------------------------------------------------- #
# Bash heuristics (design §13.3; reviews #7, #8, #18, #51)
#
# Three views of one command:
#   * raw text          — command substitution ($( ), `…`, ${ }) and process substitution are
#                          denied wherever they appear, quoted or not (they execute);
#   * masked text       — every character inside '…' / "…" (and every backslash-escaped one)
#                          replaced by `_`, same length: separators and redirects are only real
#                          outside quotes, so `--why "fix; rm > x"` is one segment (review #18);
#   * shlex tokens      — flags such as --output, -delete or -exec are judged per token, so
#                          quoting them ("-delete") does not hide them.
# Segments split on &&, ||, ;, |, |&, a newline and a lone & (review #8).
# --------------------------------------------------------------------------- #
_FILL = "_"
_SEP_RE = re.compile(r"\|\||&&|;;?|\|&|\||\n|(?<![<>])&(?![&>])")
# Fallback for a command with an unterminated quote: split everywhere (fail closed).
_FALLBACK_SPLIT_RE = re.compile(r"\s*(?:\|\||&&|;|\||\n|&(?!&))\s*")
_SEP_CHARS = " \t\n;&|"

# design §13.3 `looks_mutating`: write-shaped commands and redirects. MULTILINE so a command
# word at the start of any line counts (review #8); `(` and a backtick anchor `$(rm …)`.
_MUTATING_RE = re.compile(
    r"(^\s*|[;&|(`]\s*)(sed\s+-i|tee|rm|mv|cp|ln|chmod|chown|truncate|patch|dd|rsync|"
    r"git\s+(?:(?:-C\s+\S+|--no-pager|-c\s+\S+)\s+)*"
    r"(checkout|reset|clean|stash|rebase|merge|apply|cherry-pick|revert|restore|switch|rm|mv|worktree|filter-branch|am|pull)|"
    r"python3?\s+-c|node\s+-e|perl\s+-e|(?:ba|da|z)?sh\s+-c)\b|>\s*[^&]|<<", re.MULTILINE)
# Redirects that write (fd duplications and `N>/dev/null` are not writes).
_REDIRECT_RE = re.compile(r">|<<")
_FD_DUP_RE = re.compile(r"[0-9]*>&[0-9-]")
_DEV_NULL_RE = re.compile(r"[0-9]*>\s*/dev/null")
# Segments exempt from the main-session heuristic: Forge scripts and bookkeeping git.
_SAFE_FORGE_RE = re.compile(r"^((\S*/)?\.forge/bin/forge-\S+|forge-(check|gate|status)\b)")
_SAFE_GIT_RE = re.compile(r"^git\s+(add|commit|status|log|diff|show|rev-parse|ls-files|branch|tag)\b")
_FORGE_BIN_WORD_RE = re.compile(r"^((\S*/)?\.forge/bin/)?(forge-(check|gate|status))$")

# Read-only roles, denied anywhere in the raw command (review #7): command/process substitution,
# parameter expansion, find's action predicates, output flags, xargs, eval, tee, in-place sed,
# perl, interpreter one-liners.
_RO_DENY_RE = re.compile(
    r"\$\(|`|\$\{|<\(|>\(|\s-(exec|execdir|ok|okdir|delete)\b|--output(=|\s|$)|"
    r"\bxargs\b|\beval\b|\btee\b|\bsed\s+-i\b|\bperl\b|\bpython3?\s+-c\b|\bnode\s+-e\b|\b(ba|da|z)?sh\s+-c\b")
# Read-only command words that take any arguments.
RO_SIMPLE_WORDS = frozenset((
    "rg", "grep", "egrep", "fgrep", "find", "ls", "cat", "head", "tail", "wc", "cut", "tr", "jq", "diff", "cmp",
    "stat", "file", "pwd", "echo", "printf", "test", "[", "true", "false", "which", "basename", "dirname",
    "realpath", "readlink", "du", "tree", "nl", "column", "comm", "paste", "pytest"))
# Read-only git subcommands (after `-C <dir>` / `--no-pager`); `stash` only with list|show.
GIT_RO_SUBCOMMANDS = frozenset((
    "log", "grep", "diff", "show", "status", "rev-parse", "ls-files", "blame", "describe", "shortlog", "ls-tree",
    "cat-file", "merge-base", "show-ref", "for-each-ref", "rev-list", "name-rev", "diff-tree", "diff-index",
    "check-ignore", "stash"))
_GIT_DENY_TOKEN_RE = re.compile(r"^(--output|-O|--open-files-in-pager|--ext-diff)")
_PYTHON_WORD_RE = re.compile(r"^python[0-9.]*$")
PYTHON_RO_MODULES = frozenset(("pytest", "unittest", "json.tool"))
_GRADLEW_TASK_RE = re.compile(r"^(test|:app:test\w*|:app:compile\w*)$")
_TIMEOUT_DURATION_RE = re.compile(r"^[0-9]+(\.[0-9]+)?[smhd]?$")
_FIND_DENY_TOKEN_RE = re.compile(r"^-(exec|execdir|ok|okdir|delete|fprint0?|fprintf|fls)\b")
_AWK_DENY_RE = re.compile(r"system\s*\(|>|\||getline|@load")
_AWK_DENY_OPT_RE = re.compile(r"^(-f|--file|-E|--exec|-l|--load|-i|--include)")
_SED_ADDR = r"(?:[0-9]+(?:~[0-9]+)?|\$|/(?:\\.|[^/\\])*/|\\(.)(?:\\.|(?!\1).)*\1)"
_SED_CMD_RE = re.compile(r"^\s*(?:" + _SED_ADDR + r"(?:\s*,\s*(?:" + _SED_ADDR + r"|[+~][0-9]+))?)?\s*(?:!\s*)*(?P<cmd>[A-Za-z=#:{}])(?P<rest>.*)$",
                         re.DOTALL)


def mask_quotes(cmd: str) -> Tuple[str, bool]:
    """(masked, balanced): `cmd` with every character inside single/double quotes, and every
    backslash-escaped character, replaced by `_` (same length). Command substitutions `$( … )`
    and `` ` … ` `` stay visible even inside double quotes because they execute. `balanced` is
    False on an unterminated quote, substitution or trailing backslash."""
    out: List[str] = []
    stack: List[List[Any]] = []    # frames: ["'"] | ['"'] | ["sub", depth] | ["bt"]
    esc = False
    i = 0
    n = len(cmd)
    while i < n:
        ch = cmd[i]
        top = stack[-1][0] if stack else None
        if esc:
            out.append(_FILL)
            esc = False
            i += 1
            continue
        if top == "'":
            out.append(ch if ch == "'" else _FILL)
            if ch == "'":
                stack.pop()
            i += 1
            continue
        if top == "bt":
            out.append(ch)
            if ch == "`":
                stack.pop()
            i += 1
            continue
        if top == '"':
            if ch == "\\":
                out.append(_FILL)
                esc = True
            elif ch == '"':
                out.append(ch)
                stack.pop()
            elif ch == "$" and cmd.startswith("$(", i):
                out.append("$(")
                stack.append(["sub", 0])
                i += 2
                continue
            elif ch == "`":
                out.append(ch)
                stack.append(["bt"])
            else:
                out.append(_FILL)
            i += 1
            continue
        # unquoted, or inside a $( … ) substitution: shell syntax is live
        if ch == "\\":
            out.append(_FILL)
            esc = True
        elif ch == "'":
            out.append(ch)
            stack.append(["'"])
        elif ch == '"':
            out.append(ch)
            stack.append(['"'])
        elif ch == "`":
            out.append(ch)
            stack.append(["bt"])
        elif ch == "$" and cmd.startswith("$(", i):
            out.append("$(")
            stack.append(["sub", 0])
            i += 2
            continue
        elif ch == "(" and top == "sub":
            out.append(ch)
            stack[-1][1] += 1
        elif ch == ")" and top == "sub":
            out.append(ch)
            if stack[-1][1] == 0:
                stack.pop()
            else:
                stack[-1][1] -= 1
        else:
            out.append(ch)
        i += 1
    return "".join(out), (not stack and not esc)


def _segment_spans(cmd: str) -> List[Tuple[int, int]]:
    masked, balanced = mask_quotes(cmd)
    rx = _SEP_RE if balanced else _FALLBACK_SPLIT_RE
    probe = masked if balanced else cmd
    spans: List[Tuple[int, int]] = []
    pos = 0
    for m in rx.finditer(probe):
        spans.append((pos, m.start()))
        pos = m.end()
    spans.append((pos, len(cmd)))
    return spans


def split_segments(cmd: str) -> List[str]:
    """Non-empty segments of `cmd` split on &&, ||, ;, |, |&, newlines and a lone & — outside
    quotes (a separator inside '…' or "…" is text). On an unterminated quote every separator
    splits, quoted or not (fail closed)."""
    c = cmd or ""
    out: List[str] = []
    for a, b in _segment_spans(c):
        s = c[a:b].strip()
        if s:
            out.append(s)
    return out


def _shlex(seg: str) -> Optional[List[str]]:
    """POSIX tokens of one segment, None when the quoting is unbalanced."""
    try:
        return shlex.split(seg, posix=True)
    except ValueError:
        return None


def _prefix_of(p: str) -> str:
    """A verify/bootstrap/smoke command used as a prefix: the text before any {placeholder}."""
    return p.split("{", 1)[0].rstrip()


def _prefix_pairs(prefixes: Iterable[str]) -> List[Tuple[str, bool]]:
    """(prefix text, open_ended) longest first; open_ended when the command carries a {placeholder}
    (then anything may follow), else the prefix must end at a word boundary."""
    pairs = set()
    for p in prefixes or []:
        p = str(p)
        pre = _prefix_of(p)
        if pre:
            pairs.add((pre, "{" in p))
    return sorted(pairs, key=lambda t: -len(t[0]))


def _match_prefix(text: str, pairs: List[Tuple[str, bool]]) -> Optional[str]:
    for pre, open_ended in pairs:
        if text.startswith(pre) and (open_ended or len(text) == len(pre) or text[len(pre)] in _SEP_CHARS):
            return pre
    return None


def _starts_with_prefix(text: str, prefixes: Iterable[str]) -> bool:
    return _match_prefix(text, _prefix_pairs(prefixes)) is not None


def _strip_prefixes(cmd: str, prefixes: Iterable[str]) -> Tuple[str, bool]:
    """Consume leading segments that are binding commands (verify[].cmd / bootstrap / smoke).

    Returns (remainder, consumed). A binding command may span segments (`cd lib && python3 -m
    unittest`), so the whole prefix text is consumed, then that segment's arguments; a redirect
    or heredoc on a prefixed command is left in the remainder so callers still see it. The
    remainder starts at the first segment that is not a binding command."""
    pairs = _prefix_pairs(prefixes)
    text = cmd
    consumed = False
    while text and pairs:
        pre = _match_prefix(text, pairs)
        if pre is None:
            break
        consumed = True
        after = text[len(pre):]
        masked, balanced = mask_quotes(after)
        if not balanced:
            return after, consumed
        m = _SEP_RE.search(masked)
        args_masked = masked[:m.start()] if m else masked
        if _REDIRECT_RE.search(args_masked):
            return after, consumed
        if not m:
            return "", consumed
        text = after[m.end():].lstrip()
    return text, consumed


def forge_check_inner_commands(cmd: str) -> List[str]:
    """The `--cmd <command>` values of every forge-check invocation in `cmd` (review #20): the
    inner command runs with the caller's role, so fences judge it like a command of its own."""
    out: List[str] = []
    for seg in split_segments(cmd):
        toks = _shlex(seg)
        if not toks:
            continue
        m = _FORGE_BIN_WORD_RE.match(toks[0])
        if not m or m.group(3) != "forge-check":
            continue
        for i, t in enumerate(toks[1:], start=1):
            if t == "--cmd" and i + 1 < len(toks):
                out.append(toks[i + 1])
            elif t.startswith("--cmd="):
                out.append(t[len("--cmd="):])
    return out


def looks_mutating(cmd: str, safe_prefixes: Iterable[str] = ()) -> bool:
    """Main-session mutation heuristic (design §13.3).

    True when `cmd` (minus leading binding commands) matches the write-shaped regex outside
    quotes, unless every remaining segment is `.forge/bin/*`, bookkeeping git
    (`add|commit|status|log|diff|show|rev-parse|ls-files|branch|tag`) or starts with one of
    `safe_prefixes` (binding.verify[].cmd / bootstrap / smoke). A `forge-check --cmd '<inner>'`
    is as mutating as its inner command."""
    c = (cmd or "").strip()
    if not c:
        return False
    if any(looks_mutating(inner, safe_prefixes) for inner in forge_check_inner_commands(c)):
        return True
    rest, _ = _strip_prefixes(c, safe_prefixes)
    rest = rest.strip()
    if not rest:
        return False
    masked, balanced = mask_quotes(rest)
    if not _MUTATING_RE.search(masked if balanced else rest):
        return False
    for seg in split_segments(rest):
        if _SAFE_FORGE_RE.match(seg) or _SAFE_GIT_RE.match(seg) or _starts_with_prefix(seg, safe_prefixes):
            continue
        return True
    return False


def _writes_through_redirect(masked: str) -> bool:
    m = _FD_DUP_RE.sub("", masked)
    m = _DEV_NULL_RE.sub("", m)
    return _REDIRECT_RE.search(m) is not None


def _sed_script_writes(script: str) -> bool:
    """True when a sed script carries a w/W/e command or an s///w, s///e flag (or cannot be parsed)."""
    for chunk in re.split(r"[;\n]", script):
        if not chunk.strip():
            continue
        m = _SED_CMD_RE.match(chunk)
        if not m:
            return True
        c = m.group("cmd")
        if c in ("w", "W", "e"):
            return True
        if c in ("s", "y"):
            body = m.group("rest")
            if not body:
                return True
            delim = body[0]
            parts = 0
            i = 1
            while i < len(body) and parts < 2:
                if body[i] == "\\":
                    i += 2
                    continue
                if body[i] == delim:
                    parts += 1
                i += 1
            if parts < 2:
                return True
            flags = body[i:]
            if c == "s" and re.search(r"[we]", flags):
                return True
    return False


def _sed_ok(args: List[str]) -> bool:
    """`sed -n` print-only (review #51): -n/--quiet required, no -i/-f, no w/W/e in the script."""
    quiet = False
    scripts: List[str] = []
    positional: List[str] = []
    i = 0
    while i < len(args):
        t = args[i]
        if t in ("-e", "--expression"):
            if i + 1 >= len(args):
                return False
            scripts.append(args[i + 1])
            i += 2
            continue
        if t.startswith("--expression="):
            scripts.append(t.split("=", 1)[1])
        elif t in ("-n", "--quiet", "--silent"):
            quiet = True
        elif t.startswith("--"):
            if t not in ("--posix", "--debug", "--regexp-extended", "--separate", "--null-data", "--unbuffered",
                         "--sandbox", "--"):
                return False
        elif t.startswith("-") and len(t) > 1:
            flags = t[1:]
            j = 0
            while j < len(flags):
                ch = flags[j]
                if ch == "n":
                    quiet = True
                elif ch in "Erzsu":
                    pass
                elif ch == "e":
                    tail = flags[j + 1:]
                    if tail:
                        scripts.append(tail)
                    else:
                        if i + 1 >= len(args):
                            return False
                        scripts.append(args[i + 1])
                        i += 1
                    break
                elif ch == "l":
                    if j + 1 >= len(flags):
                        i += 1
                    break
                else:
                    return False
                j += 1
        else:
            positional.append(t)
        i += 1
    if not quiet:
        return False
    if not scripts:
        if not positional:
            return False
        scripts = [positional[0]]
    return not any(_sed_script_writes(s) for s in scripts)


def _awk_ok(args: List[str]) -> bool:
    """awk without a program file, extension load, `system(`, redirect or pipe (review #51)."""
    for t in args:
        if _AWK_DENY_OPT_RE.match(t) or _AWK_DENY_RE.search(t):
            return False
    return True


def _git_ok(args: List[str]) -> bool:
    i = 0
    while i < len(args) and args[i].startswith("-"):
        if args[i] == "-C":
            i += 2
        elif args[i].startswith("-C") or args[i] in ("--no-pager", "-P"):
            i += 1
        else:
            return False
    if i >= len(args) or args[i] not in GIT_RO_SUBCOMMANDS:
        return False
    sub, rest = args[i], args[i + 1:]
    if any(_GIT_DENY_TOKEN_RE.match(t) for t in rest):
        return False
    if sub == "stash":
        return bool(rest) and rest[0] in ("list", "show")
    return True


def _unwrap_timeout(toks: List[str]) -> Optional[List[str]]:
    """`timeout [flags] <duration> <command…>` -> the command tokens; None when malformed."""
    i = 1
    while i < len(toks) and toks[i].startswith("-"):
        i += 2 if toks[i] in ("-k", "--kill-after", "-s", "--signal") else 1
    if i >= len(toks) or not _TIMEOUT_DURATION_RE.match(toks[i]):
        return None
    rest = toks[i + 1:]
    return rest or None


def _ro_tokens_allowed(toks: List[str], extra_prefixes: Iterable[str]) -> bool:
    if not toks:
        return False
    if toks[0] == "timeout":
        inner = _unwrap_timeout(toks)
        return inner is not None and inner[0] != "timeout" and _ro_tokens_allowed(inner, extra_prefixes)
    if _starts_with_prefix(" ".join(toks), extra_prefixes):
        return True
    word, args = toks[0], toks[1:]
    if any(_FIND_DENY_TOKEN_RE.match(t) or t.startswith("--output") for t in args):
        return False
    if word in RO_SIMPLE_WORDS:
        if word == "rg" and any(t.startswith("--pre") for t in args):
            return False
        return True
    if word == "sort":
        return not any(t.startswith("-o") for t in args)
    if word == "uniq":
        return len([t for t in args if not t.startswith("-")]) <= 1
    if word == "sed":
        return _sed_ok(args)
    if word in ("awk", "gawk", "mawk", "nawk"):
        return _awk_ok(args)
    if word == "cd":
        return len(args) <= 1
    if word == "git":
        return _git_ok(args)
    if _PYTHON_WORD_RE.match(word):
        return len(args) >= 2 and args[0] == "-m" and args[1] in PYTHON_RO_MODULES
    if word == "npm":
        return bool(args) and args[0] == "test"
    if word == "npx":
        return bool(args) and args[0] == "jest"
    if word == "./gradlew":
        return bool(args) and _GRADLEW_TASK_RE.match(args[0]) is not None
    m = _FORGE_BIN_WORD_RE.match(word)
    if m:
        script = m.group(3)
        if script == "forge-gate":
            return True
        if script == "forge-check":
            inner = [args[i + 1] for i, t in enumerate(args) if t == "--cmd" and i + 1 < len(args)]
            inner += [t[len("--cmd="):] for t in args if t.startswith("--cmd=")]
            return all(ro_allowed(c, extra_prefixes) for c in inner)
        first = next((t for t in args if not t.startswith("-")), None)
        return first == "get"
    return False


def ro_allowed(cmd: str, extra_prefixes: Iterable[str] = ()) -> bool:
    """Read-only Bash allow-list for forge-scout / forge-verifier / forge-planner (design §13.3).

    Denies, anywhere in the command: command substitution, `${`, process substitution, find's
    action predicates, `--output`, xargs, eval, tee, sed -i, perl, interpreter one-liners; any
    output redirect outside quotes except `N>&M` and `N>/dev/null`; heredocs. Then, after the
    leading `extra_prefixes` segments (binding.verify[].cmd), every segment must be an allowed
    command: the words in RO_SIMPLE_WORDS, `sort` without -o, `uniq` with one input, `sed -n`
    without w/W/e, awk without system/redirect/pipe/program file, `cd <dir>`, read-only git
    subcommands (after `-C <dir>`/`--no-pager`), `python -m pytest|unittest|json.tool`,
    `npm test`, `npx jest`, `./gradlew test…`, `timeout <n> <allowed>`, and the Forge scripts
    forge-check (its `--cmd` must pass this list too), forge-gate and forge-status get."""
    c = (cmd or "").strip()
    if not c:
        return False
    if _RO_DENY_RE.search(c):
        return False
    masked, balanced = mask_quotes(c)
    if not balanced or _writes_through_redirect(masked):
        return False
    rest, _ = _strip_prefixes(c, extra_prefixes)
    for seg in split_segments(rest):
        toks = _shlex(seg)
        if toks is None or not _ro_tokens_allowed(toks, extra_prefixes):
            return False
    return True


def _irreversible_regex(pattern: str) -> "re.Pattern[str]":
    """Glob-like pattern over a whole command: `*` matches anything (spaces and slashes included)."""
    out = []
    for ch in pattern:
        if ch == "*":
            out.append(".*")
        elif ch == "?":
            out.append(".")
        else:
            out.append(re.escape(ch))
    return re.compile("^" + "".join(out) + "$", re.DOTALL)


def irreversible_match(cmd: str, patterns: Iterable[str]) -> Optional[str]:
    """The first binding.irreversible_commands pattern matching the whole command, any segment
    (&&, ||, ;, |, newline, &) or a forge-check `--cmd` inner command (MODULE-API §6), or None."""
    c = (cmd or "").strip()
    if not c:
        return None
    candidates = [c] + split_segments(c)
    for inner in forge_check_inner_commands(c):
        candidates += [inner] + split_segments(inner)
    for pat in patterns or []:
        rx = _irreversible_regex(str(pat).strip())
        for cand in candidates:
            if rx.match(cand):
                return str(pat)
    return None
