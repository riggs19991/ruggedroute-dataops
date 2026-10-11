"""Validators shared by forge-gate, the SubagentStop hooks and forge-status (MODULE-API §4).

Everything here is pure (reads files, runs read-only git) except persist_handoff and
persist_verdict, which write the report-NN / verdict-NN / handoff files.

Rules implemented:
  * plan gate          design §5.3, §7 gate 0, schemas/plan.json + schemas/brief.json
  * handoff gate       design §5.5, §7 gate 5, schemas/handoff.json
  * verdict gate       design §5.6, §7 gate 7, schemas/verdict.json
  * Bash heuristics    design §13.3: looks_mutating (main-session mutation heuristic),
                       ro_allowed (read-only allow-list), irreversible_match (binding patterns)
"""
from __future__ import annotations

import glob as _glob
import os
import re
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

    Filtered by `agent_id` when given (record field, falling back to the filename suffix).
    Each returned dict gains `_file` (repo-relative path) for messages."""
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


def tree_changed(paths: common.Paths, allowed_paths: List[str]) -> List[str]:
    """`git status --porcelain --untracked-files=all -- <allowed_paths>` filtered to the globs.

    `.forge/**` and `.claude/agent-memory/**` never count (design §5.5)."""
    if not allowed_paths:
        return []
    out: List[str] = []
    for p in common.git_porcelain(paths.root, list(allowed_paths), untracked=True):
        rel = paths.rel(p)
        if rel.startswith(_TREE_IGNORED_PREFIXES):
            continue
        # git pathspecs match more loosely than Forge globs; keep only true glob matches.
        if common.any_glob(rel, allowed_paths) is None:
            continue
        out.append(rel)
    return common.unique(out)


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
    if ctx["tdd"]:
        for cmd in ctx["expected_fail_first"]:
            hits = _record_hits(records, cmd)
            reds = [h[0] for h in hits if h[1] != 0]
            greens = [h[0] for h in hits if h[1] == 0]
            # design §5.5: a non-zero (red) record strictly earlier than a zero (green) record.
            if not reds or not greens or min(reds) >= max(greens):
                defects.append(f"tdd: `{cmd}` needs a failing record (forge-check --expect-fail) earlier than a passing one")
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
            cmd = c.get("cmd") or ""
            if not cmd or not _record_hits(records, cmd):
                defects.append(f"{cid}: cmd `{cmd}` has no checks/ record by {agent_id}; "
                               f"run .forge/bin/forge-check {task_id} {step_id} yourself")
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
def bound_agents(paths: common.Paths, task_id: str, step_id: str) -> List[str]:
    """agent_ids whose .runtime/agents/<id>.json is bound to (task_id, step_id)."""
    out: List[str] = []
    for f in sorted(_glob.glob(os.path.join(paths.runtime, "agents", "*.json"))):
        try:
            rec = common.read_json(f)
        except common.ForgeError:
            continue
        if isinstance(rec, dict) and rec.get("task") == task_id and rec.get("step") == step_id and rec.get("agent_id"):
            out.append(str(rec["agent_id"]))
    return out


# --------------------------------------------------------------------------- #
# Bash heuristics (design §13.3)
# --------------------------------------------------------------------------- #
_SEGMENT_SPLIT_RE = re.compile(r"\s*(?:\|\||&&|;|\|)\s*")

# design §13.3 `looks_mutating`: write-shaped commands and redirects.
_MUTATING_RE = re.compile(
    r"(^|[;&|]\s*)(sed\s+-i|tee|rm|mv|cp|chmod|chown|truncate|"
    r"git\s+(checkout|reset|clean|stash|rebase|merge|apply|cherry-pick|revert)|"
    r"python3?\s+-c|node\s+-e|perl\s+-e)\b|>\s*[^&]|<<")
# Segments exempt from the heuristic: Forge scripts and bookkeeping git.
_SAFE_FORGE_RE = re.compile(r"^(\S*/)?\.forge/bin/\S+")
_SAFE_GIT_RE = re.compile(r"^git\s+(add|commit|status|log|diff|show|rev-parse|ls-files|branch|tag)\b")

# design §13.3 `ro_allowed`: the read-only allow-list, evaluated per segment.
_RO_ALLOW_RE = re.compile(
    r"^(git (log|grep|diff|show|status|rev-parse|ls-files|blame)|rg|grep|egrep|find|ls|cat|head|tail|wc|sort|uniq|"
    r"cut|tr|jq|diff|stat|file|pwd|echo|printf|test|\[|python3 -m (pytest|unittest)|pytest|npm test|npx jest|"
    r"\./gradlew (test|:app:test\w*|:app:compile\w*)|\.forge/bin/forge-(check|gate|status get)|cd [^;&|>]+)( |$)")
# Denied anywhere in a read-only command: redirects, heredocs, interpreter flags, in-place editors.
_RO_DENY_RE = re.compile(r"(>>|<<|(?<![0-9])>(?!&)|\s-c\s|\s-e\s|\btee\b|\bsed\s+-i\b|\bperl\b|\bpython3?\s+-c\b|\bnode\s+-e\b)")
# A redirect is denied unless it is a pure fd duplication such as 2>&1 or >&2.
_FD_DUP_RE = re.compile(r"[0-9]?>&[0-9]")


def split_segments(cmd: str) -> List[str]:
    """Non-empty segments of `cmd` split on &&, ||, ; and |."""
    return [s.strip() for s in _SEGMENT_SPLIT_RE.split(cmd.strip()) if s.strip()]


def _prefix_of(p: str) -> str:
    """A verify/bootstrap/smoke command used as a prefix: the text before any {placeholder}."""
    return p.split("{", 1)[0].rstrip()


def _starts_with_prefix(text: str, prefixes: Iterable[str]) -> bool:
    for p in prefixes or []:
        pre = _prefix_of(str(p))
        if pre and text.startswith(pre):
            return True
    return False


def looks_mutating(cmd: str, safe_prefixes: Iterable[str] = ()) -> bool:
    """Main-session mutation heuristic (design §13.3).

    True when `cmd` matches the write-shaped regex unless every segment is `.forge/bin/*`,
    bookkeeping git (`add|commit|status|log|diff|show|rev-parse|ls-files|branch|tag`) or starts
    with one of `safe_prefixes` (binding.verify[].cmd / bootstrap / smoke)."""
    c = (cmd or "").strip()
    if not c:
        return False
    if not _MUTATING_RE.search(c):
        return False
    if _starts_with_prefix(c, safe_prefixes):
        return False
    for seg in split_segments(c):
        if _SAFE_FORGE_RE.match(seg) or _SAFE_GIT_RE.match(seg) or _starts_with_prefix(seg, safe_prefixes):
            continue
        return True
    return False


def ro_allowed(cmd: str, extra_prefixes: Iterable[str] = ()) -> bool:
    """Read-only Bash allow-list for forge-scout / forge-verifier / forge-planner (design §13.3).

    Denies redirects (`>`, `>>`, `<<`; fd duplications like `2>&1` are allowed), interpreter flags
    (`-c `, `-e `), `tee`, `sed -i`, `perl`, `python3 -c`, `node -e` anywhere; then every &&/;/|
    segment must match the allow-list regex or start with one of `extra_prefixes`
    (binding.verify[].cmd prefixes). The whole command starting with a prefix is allowed too."""
    c = (cmd or "").strip()
    if not c:
        return False
    stripped = _FD_DUP_RE.sub("", c)
    if _RO_DENY_RE.search(stripped):
        return False
    if _starts_with_prefix(c, extra_prefixes):
        return True
    for seg in split_segments(c):
        if _RO_ALLOW_RE.match(seg) or _starts_with_prefix(seg, extra_prefixes):
            continue
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
    """The first binding.irreversible_commands pattern matching the whole command or any
    &&/;/| segment (MODULE-API §6), or None."""
    c = (cmd or "").strip()
    if not c:
        return None
    candidates = [c] + split_segments(c)
    for pat in patterns or []:
        rx = _irreversible_regex(str(pat).strip())
        for cand in candidates:
            if rx.match(cand):
                return str(pat)
    return None
