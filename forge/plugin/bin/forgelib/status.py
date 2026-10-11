"""forgelib.status — the Forge state machine; the only writer of .forge/STATUS.json.

Contract: forge/docs/MODULE-API.md §3 (method signatures, data shapes, exit codes) and
forge/docs/design/design-v2.md §5.1 (transition table), §4.3 (routing rules), §4.1 (signals),
§6 (context clearing), §7 gates 8/12/13. Every public transition:

  * loads STATUS, checks its precondition and raises ForgeError(EXIT_REFUSED) with ONE line,
  * mutates the dict, journals one line (common.journal) and appends the design's ledger rows,
  * returns the new STATUS through save(), which validates against .forge/schemas/status.json,
    writes atomically, stamps updated_*, records .runtime/status.sha and clears dirty markers.

Standard library only (Python 3.9+).
"""
from __future__ import annotations

import glob as _glob
import json
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import common
from .common import ForgeError, EXIT_REFUSED, EXIT_INVALID, EXIT_USAGE

# Paths that never count as out-of-scope at close (design §5.1 close row; §7 gate 8).
CLOSE_ALWAYS_ALLOWED = (".forge/**", "CLAUDE.md", ".gitignore", ".claude/agent-memory/**")
# Verdict tags that raise effort instead of changing model (design §4.3 rule 3).
EFFORT_TAGS = ("skipped-file", "no-check-run", "not-double-checked")
# Design §4.3 rule 6: attempts per step without a ruling.md.
MAX_ATTEMPTS = 3
MAX_VERIFY_ATTEMPTS = 2
_TASK_ID_RE = re.compile(r"^T-[0-9]{4,}$")
_STEP_ID_RE = re.compile(r"^[0-9]{2}$")

Json = Dict[str, Any]


def idle_status(project: str) -> Json:
    """A valid idle STATUS (schema_version 2) for the installer and tests."""
    return {
        "schema_version": 2,
        "forge_version": common.FORGE_VERSION,
        "project": project,
        "updated_at": common.now_iso(),
        "updated_ts": common.now_ts(),
        "updated_by": {"session_id": "installer", "cmd": "idle_status"},
        "context_state": "fresh",
        "task": None,
        "queue": [],
        "history": [],
    }


def _short(sha: Optional[str]) -> str:
    return (sha or "")[:7] or "none"


def _basename(path: Optional[str]) -> str:
    return os.path.basename(path) if path else "none"


def _git_pathspecs(globs: Iterable[str]) -> List[str]:
    """Forge globs -> git pathspecs (git's default `*` already crosses `/`)."""
    out = []
    for g in globs:
        g = g.rstrip("/")
        out.append(g.replace("**/", "*").replace("**", "*"))
    return common.unique(out)


def _globs_intersect(a: Iterable[str], b: Iterable[str]) -> Optional[str]:
    """First path/glob of `a` that overlaps one of `b` (either side may be a glob)."""
    for x in a:
        for y in b:
            if x == y or common.glob_match(x, y) or common.glob_match(y, x):
                return x
    return None


class Status:
    """State machine over .forge/STATUS.json (MODULE-API §3)."""

    def __init__(self, paths: common.Paths):
        self.paths = paths
        self._binding: Optional[Json] = None
        self._routing: Optional[Json] = None
        self._schema: Optional[Json] = None

    # ------------------------------------------------------------------ #
    # lazily loaded policy data
    # ------------------------------------------------------------------ #
    @property
    def binding(self) -> Json:
        if self._binding is None:
            self._binding = common.load_binding(self.paths)
        return self._binding

    @property
    def routing(self) -> Json:
        if self._routing is None:
            self._routing = common.load_routing(self.paths)
        return self._routing

    @property
    def schema(self) -> Json:
        """Assertion list from .forge/schemas/status.json (falls back to common constants)."""
        if self._schema is None:
            sch = common.read_json(os.path.join(self.paths.schemas, "status.json"), default=None)
            self._schema = sch if isinstance(sch, dict) else {}
        return self._schema

    def session(self) -> str:
        return common.session_id(self.paths)

    # ------------------------------------------------------------------ #
    # load / validate / save
    # ------------------------------------------------------------------ #
    def load(self) -> Json:
        """STATUS from disk; ForgeError(EXIT_INVALID) when missing or failing an assertion."""
        st = common.load_status(self.paths)
        defects = self.validate(st)
        if defects:
            raise ForgeError(f"{self.paths.rel(self.paths.status)} invalid: {defects[0]}", EXIT_INVALID)
        return st

    def validate(self, st: Json) -> List[str]:
        """Schema assertions (.forge/schemas/status.json): required keys, enums, bounds, invariants."""
        d: List[str] = []
        sch = self.schema
        enums = sch.get("enums", {})
        required = sch.get("required") or ["schema_version", "forge_version", "project", "updated_at",
                                           "updated_ts", "updated_by", "context_state", "task", "queue", "history"]
        for k in required:
            if k not in st:
                d.append(f"missing key {k}")
        if d:
            return d
        if st.get("schema_version") != 2:
            d.append(f"schema_version must be 2 (got {st.get('schema_version')!r})")
        if st.get("context_state") not in tuple(enums.get("context_state") or common.CONTEXT_STATES):
            d.append(f"context_state invalid: {st.get('context_state')!r}")
        if not isinstance(st.get("updated_by"), dict):
            d.append("updated_by must be an object")
        bounds = sch.get("bounds", {})
        for key, cap in (("queue", bounds.get("queue", 10)), ("history", bounds.get("history", 5))):
            v = st.get(key)
            if not isinstance(v, list):
                d.append(f"{key} must be a list")
            elif len(v) > cap:
                d.append(f"{key} exceeds {cap} entries")
        task = st.get("task")
        if task is None:
            return d
        if not isinstance(task, dict):
            return d + ["task must be null or an object"]
        task_required = sch.get("task_required") or [
            "id", "title", "class", "risk", "size_source", "files", "creates", "signals", "class_justification",
            "phase", "plan", "plan_author", "scope", "routing", "steps", "escalation", "next_action", "resume_hint",
            "evidence_count", "evidence", "blocked_on", "external", "budget"]
        for k in task_required:
            if k not in task:
                d.append(f"task missing key {k}")
        if d:
            return d
        if not _TASK_ID_RE.match(str(task.get("id", ""))):
            d.append(f"task.id invalid: {task.get('id')!r}")
        checks = (
            ("task.class", task.get("class"), common.CLASSES),
            ("task.risk", task.get("risk"), common.RISKS),
            ("task.phase", task.get("phase"), common.PHASES),
            ("task.routing.mode", (task.get("routing") or {}).get("mode"), common.MODES),
            ("task.plan_author", task.get("plan_author"), (None,) + common.PLAN_AUTHORS),
        )
        for name, value, default in checks:
            allowed = tuple(enums.get(name) or default)
            if value not in allowed:
                d.append(f"{name} invalid: {value!r}")
        if len(task.get("evidence") or []) > bounds.get("evidence", 10):
            d.append("task.evidence exceeds 10 entries")
        steps = task.get("steps")
        if not isinstance(steps, list):
            return d + ["task.steps must be a list"]
        step_required = sch.get("step_required") or ["id", "title", "agent", "model", "effort", "status",
                                                      "attempts", "from", "verify_attempts", "brief", "allowed_paths"]
        for s in steps:
            sid = s.get("id", "?") if isinstance(s, dict) else "?"
            if not isinstance(s, dict):
                d.append("step entries must be objects")
                continue
            for k in step_required:
                if k not in s:
                    d.append(f"step {sid} missing key {k}")
            for name, value, default in (("task.steps[].status", s.get("status"), common.STEP_STATUSES),
                                         ("task.steps[].from", s.get("from"), common.STEP_FROM),
                                         ("task.steps[].model", s.get("model"), common.MODELS),
                                         ("task.steps[].effort", s.get("effort"), common.EFFORTS)):
                if value not in tuple(enums.get(name) or default):
                    d.append(f"step {sid} {name.split('.')[-1]} invalid: {value!r}")
            if s.get("status") == "running" and not s.get("started_by"):
                d.append(f"step {sid} running without started_by")
            if s.get("status") == "done" and not s.get("commit") and not s.get("no_verifier"):
                d.append(f"step {sid} done without commit")
        # schema invariant "mode inline <=> steps == []", relaxed before the plan import (M/W/L open with
        # mode single and no steps until forge-status plan runs)
        mode = (task.get("routing") or {}).get("mode")
        if mode == "inline" and steps:
            d.append("routing.mode inline with steps")
        if not steps and mode != "inline" and task.get("phase") not in ("plan", "intake", "blocked", "idle"):
            d.append("steps empty but routing.mode is not inline after planning")
        if steps and task.get("class") in ("M", "W") and len(steps) != 1:
            d.append(f"class {task.get('class')} needs exactly one step (has {len(steps)})")
        if steps and task.get("class") == "L" and len(steps) < 3:
            d.append(f"class L needs >= 3 steps (has {len(steps)})")
        if task.get("phase") == "done" and any(s.get("status") != "done" for s in steps):
            d.append("phase done with a step not done")
        hits = (task.get("signals") or {}).get("risk_hits") or []
        just = str(task.get("class_justification") or "")
        forced = "force-risk" in just or "accept-risk-none" in just
        if not forced and (task.get("risk") == "R") != bool(hits):
            d.append("task.risk disagrees with signals.risk_hits (no --force-risk/--accept-risk-none recorded)")
        return d

    def save(self, st: Json, cmd: str, stamp: bool = True, clear_dirty: str = "main") -> None:
        """Validate, write atomically, stamp updated_*, record status.sha, clear dirty markers.

        design §5.1: a STATUS write is what "recording the state" means, so dirty-main goes;
        clear_dirty="worker" also removes dirty-worker (step-report/verdict/done/fail/external);
        "none" removes nothing (read-only re-stamps).
        """
        defects = self.validate(st)
        if defects:
            raise ForgeError(f"refusing to write an invalid STATUS: {defects[0]}", EXIT_INVALID)
        if stamp:
            st["updated_at"] = common.now_iso()
            st["updated_ts"] = common.now_ts()
            st["updated_by"] = {"session_id": self.session(), "cmd": f"forge-status {cmd}".strip()}
        common.write_json_atomic(self.paths.status, st)
        common.ensure_dir(self.paths.runtime)
        common.write_text_atomic(self.paths.rt("status.sha"), (common.sha256_file(self.paths.status) or "") + "\n")
        if clear_dirty in ("main", "worker"):
            common.rm(self.paths.rt("dirty-main"))
        if clear_dirty == "worker":
            common.rm(self.paths.rt("dirty-worker"))

    def restamp(self) -> None:
        """Re-record status.sha after a deliberate hand edit (journaled; STATUS must validate)."""
        st = self.load()
        common.ensure_dir(self.paths.runtime)
        common.write_text_atomic(self.paths.rt("status.sha"), (common.sha256_file(self.paths.status) or "") + "\n")
        task = common.current_task(st)
        common.journal(self.paths, task.get("id") if task else None,
                       f"restamp: status.sha re-recorded after a hand edit (session {self.session()})")

    # ------------------------------------------------------------------ #
    # small shared helpers
    # ------------------------------------------------------------------ #
    def _task(self, st: Json, task_id: str) -> Json:
        """The open task, which must carry `task_id`; refuses otherwise."""
        task = common.current_task(st)
        if task is None:
            raise ForgeError("no task is open", EXIT_REFUSED)
        if task_id and task.get("id") != task_id:
            raise ForgeError(f"open task is {task['id']}, not {task_id}", EXIT_REFUSED)
        return task

    def _step(self, task: Json, step_id: str) -> Json:
        step = common.find_step(task, step_id)
        if step is None:
            raise ForgeError(f"{task['id']} has no step {step_id}", EXIT_REFUSED)
        return step

    def _journal(self, task_id: Optional[str], msg: str) -> None:
        common.journal(self.paths, task_id, msg)

    def _ledger(self, row: Json) -> None:
        r = dict(row)
        r.setdefault("session_id", self.session())
        common.ledger(self.paths, r)

    def _has_ruling(self, task_id: str) -> bool:
        return common.exists(self.paths.task_file(task_id, "ruling.md"))

    def _verifier(self, task: Json) -> Tuple[str, str]:
        v = (task.get("routing") or {}).get("verifier") or {}
        model = common.alias_model(v.get("model")) or common.DEFAULT_AGENT_ROUTING["forge-verifier"][0]
        return model, v.get("effort") or common.DEFAULT_AGENT_ROUTING["forge-verifier"][1]

    def _dispatch_text(self, step: Json) -> str:
        return f"Dispatch {step['agent']} ({step['model']}/{step['effort']}) on {_basename(step.get('brief'))}"

    def _verify_text(self, task: Json, step: Json) -> str:
        vm, ve = self._verifier(task)
        return (f"Dispatch forge-verifier ({vm}/{ve}) on step {step['id']}: {_basename(step.get('brief'))}, "
                f"{_basename(step.get('report'))}, range {_short(step.get('base'))}..{_short(step.get('commit'))}")

    def _current_step(self, task: Json) -> Optional[Json]:
        esc = (task.get("escalation") or {}).get("step")
        if esc:
            s = common.find_step(task, esc)
            if s and s.get("status") != "done":
                return s
        for s in task.get("steps") or []:
            if s.get("status") != "done":
                return s
        return None

    def _idle_next(self, st: Json) -> str:
        queue = st.get("queue") or []
        if queue:
            return f"Run /forge-task \"{queue[0].get('title', '')}\" (queued {queue[0].get('id', '')})"
        return "Run /forge-task <title> to start"

    def one_line(self, st: Json) -> str:
        """`<task> <phase> <step?> <status?> | next: <next_action>` (MODULE-API §3 CLI output)."""
        task = common.current_task(st)
        if task is None:
            return f"idle | next: {self._idle_next(st)}"
        parts = [task["id"], task["phase"]]
        step = self._current_step(task)
        if step:
            parts += [step["id"], step["status"]]
        return " ".join(parts) + f" | next: {task.get('next_action') or ''}"

    def _default_next_action(self, task: Json) -> str:
        """Recompute next_action from the task shape (used by unblock and recover)."""
        cls, tid = task["class"], task["id"]
        if task["phase"] == "done":
            return "Run /forge-close"
        if not task.get("steps"):
            if cls == "T":
                return (f"Edit the declared files inline, run .forge/bin/forge-check {tid} main, "
                        f"then /forge-close")
            if task.get("plan") is None:
                return (f"Write the plan to .forge/tasks/{tid}/plan.md, then run "
                        f".forge/bin/forge-status plan {tid} --from .forge/tasks/{tid}/plan.md")
            if cls == "X":
                return f"Invoke /forge-investigate {tid}"
            vm, ve = self._verifier(task)
            return (f"Implement inline within scope, run .forge/bin/forge-check {tid} main, dispatch "
                    f"forge-verifier ({vm}/{ve}) if tests were added or changed, then /forge-close")
        step = self._current_step(task)
        if step is None:
            return "Run /forge-close"
        status = step["status"]
        if status == "pending":
            return self._dispatch_text(step)
        if status == "running":
            return f"Await {step['agent']} on step {step['id']} ({_basename(step.get('brief'))}); its handoff gate records the report"
        if status == "reported":
            return self._verify_text(task, step)
        if status == "verifying":
            return f"Await forge-verifier on step {step['id']}; its verdict gate records the verdict"
        if status == "failed":
            return (f"Run .forge/bin/forge-status step-start {tid} {step['id']} --from failed|clean, "
                    f"then {self._dispatch_text(step)}")
        if status == "awaiting_external":
            ext = task.get("external") or {}
            return f"Run: {ext.get('needs', '<external check>')}; then .forge/bin/forge-status attest {tid} {step['id']} <DoD-n> --by <you> --evidence <url|path>"
        return f"Read .forge/tasks/{tid}/{_basename(step.get('report'))} and decide: step-start --from failed|clean, scope add, or block --on"

    # ------------------------------------------------------------------ #
    # signals (design §4.1) and class constraints (design §5.1 open row)
    # ------------------------------------------------------------------ #
    def _test_files(self) -> List[str]:
        """Existing repo-relative files matching binding.test_globs."""
        out: List[str] = []
        for g in self.binding.get("test_globs") or []:
            for hit in _glob.glob(os.path.join(self.paths.root, g), recursive=True):
                if os.path.isfile(hit):
                    out.append(self.paths.rel(hit))
        return common.unique(out)

    def _importers(self, declared: List[str]) -> List[str]:
        """Files other than the declared set that import a declared .py module by its stem.

        design §4.1: `git grep -l` of each declared module's import name (>= 4-char identifier),
        counted only; advisory, never used for size.
        """
        found: List[str] = []
        declared_set = set(declared)
        for p in declared:
            if not p.endswith(".py"):
                continue
            stem = os.path.basename(p)[:-3]
            if len(stem) < 4 or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", stem):
                continue
            pattern = rf"(^|[^A-Za-z0-9_.])(import|from)\s+([A-Za-z0-9_]+\.)*{re.escape(stem)}([^A-Za-z0-9_]|$)"
            code, out = common.git(["grep", "-l", "-E", pattern, "--", "*.py"], self.paths.root)
            if code != 0:
                continue
            for line in out.splitlines():
                f = line.strip()
                if f and f not in declared_set:
                    found.append(f)
        return common.unique(found)

    def _cochanges(self, declared: List[str]) -> List[str]:
        """Files that changed in the last 20 commits touching the declared set but are not declared."""
        if not declared:
            return []
        code, out = common.git(["log", "--name-only", "--format=", "-20", "--"] + declared, self.paths.root)
        if code != 0:
            return []
        declared_set = set(declared)
        rows = [l.strip() for l in out.splitlines() if l.strip() and l.strip() not in declared_set]
        return common.unique(rows)[:20]

    def _tests_present(self, declared: List[str], created: List[str]) -> bool:
        """design §4.1: every declared/created source path has a test_globs file in its test location
        (an existing one, or one the declaration creates)."""
        globs = self.binding.get("test_globs") or []
        tests = set(self._test_files())
        tests.update(p for p in created if common.any_glob(p, globs))
        for p in declared:
            if common.any_glob(p, globs) or p.startswith(".forge/") or p.startswith(".claude/"):
                continue
            d = os.path.dirname(p)
            prefix = d + "/" if d and d != "." else ""
            if not any(t.startswith(prefix) for t in tests):
                return False
        return True

    def _risk_hits(self, title: str, paths_list: Iterable[str]) -> List[str]:
        """(paths ∩ protected_paths ∪ risk_paths) via glob, plus title ∩ risk_words (common.word_hits)."""
        b = self.binding
        globs = list(b.get("protected_paths") or []) + list(b.get("risk_paths") or [])
        hits: List[str] = []
        for p in paths_list:
            g = common.any_glob(p, globs)
            if g:
                hits.append(f"{p} ({g})")
        for w in common.word_hits(title or "", b.get("risk_words") or []):
            hits.append(f"title: {w}")
        return common.unique(hits)

    def _compute_signals(self, title: str, files: List[str], creates: List[str],
                         extra_paths: Iterable[str] = ()) -> Json:
        """Signals from the declared set (never title-token grep for size, design §4.1)."""
        declared = common.unique(list(files) + list(creates))
        all_paths = common.unique(declared + list(extra_paths))
        importers = self._importers(declared)
        important = [p for p in all_paths if common.any_glob(p, self.binding.get("important_paths") or [])]
        return {
            "files": len(declared),
            "dirs": len(common.dirs_of(declared)),
            "importers": len(importers),
            "importer_files": importers[:20],
            "recent_cochanges": self._cochanges(declared),
            "tests_present": self._tests_present(declared, list(creates)),
            "risk_hits": self._risk_hits(title, all_paths),
            "important_hits": important,
        }

    def _status_signals(self, sig: Json) -> Json:
        """The STATUS subset of signals.json (MODULE-API §2.1 shape)."""
        return {k: sig[k] for k in ("files", "dirs", "importers", "recent_cochanges",
                                    "tests_present", "risk_hits", "important_hits")}

    def _write_signals(self, task_id: str, title: str, declared: List[str], sig: Json) -> None:
        row = {"task": task_id, "title": title, "computed_at": common.now_iso(), "size_source": "declared",
               "declared": declared}
        row.update(sig)
        common.write_json_atomic(self.paths.task_file(task_id, "signals.json"), row)

    def _check_class(self, cls: str, risk: str, sig: Json, why: str, force_risk: bool,
                     accept_risk_none: Optional[str]) -> None:
        """design §5.1 open row / MODULE-API §3 open() constraints; raises on the first violation."""
        if cls not in common.CLASSES:
            raise ForgeError(f"class must be one of {'|'.join(common.CLASSES)}", EXIT_USAGE)
        if risk not in common.RISKS:
            raise ForgeError("risk must be none or R", EXIT_USAGE)
        if len((why or "").strip()) < 20:
            raise ForgeError("--why must be at least 20 characters (which signals fired)", EXIT_REFUSED)
        files, dirs, hits = sig["files"], sig["dirs"], sig["risk_hits"]
        if cls == "T" and files > 2:
            raise ForgeError(f"class T allows at most 2 declared files (got {files}); re-class as S or M", EXIT_REFUSED)
        if cls == "S" and (files > 3 or dirs > 2):
            raise ForgeError(f"class S allows at most 3 files in 2 dirs (got {files} files, {dirs} dirs); re-class as M", EXIT_REFUSED)
        if cls == "M" and (files > 10 or dirs > 3):
            raise ForgeError(f"class M allows at most 10 files in 3 dirs (got {files} files, {dirs} dirs); that is W", EXIT_REFUSED)
        if cls in ("T", "S") and hits and not accept_risk_none:
            raise ForgeError(f"class {cls} cannot carry risk hits ({', '.join(hits)}); re-class or --accept-risk-none \"<why>\"", EXIT_REFUSED)
        if risk == "R" and not hits and not force_risk:
            raise ForgeError("risk R declared but no risk hits on the declared set; pass --force-risk to insist", EXIT_REFUSED)
        if risk == "none" and hits and not accept_risk_none:
            raise ForgeError(f"risk hits on the declared set ({', '.join(hits)}): declare --risk R or --accept-risk-none \"<why>\"", EXIT_REFUSED)

    def _justification(self, why: str, force_risk: bool, accept_risk_none: Optional[str]) -> str:
        j = why.strip()
        if force_risk:
            j += " [--force-risk]"
        if accept_risk_none:
            j += f" [--accept-risk-none: {accept_risk_none.strip()}]"
        return j

    def _budget(self, cls: str, risk: str, steps: int = 0, chain: bool = False) -> Json:
        """binding.budgets.<class> (M_chain / L_unit × units × 1.2) × risk_multiplier (design §4.3 rule 9)."""
        b = self.binding.get("budgets") or {}
        if cls == "L":
            cap = float(b.get("L_unit", 2)) * max(steps, 3) * 1.2
        elif cls == "M" and chain:
            cap = float(b.get("M_chain", b.get("M", 10)))
        else:
            cap = float(b.get(cls, {"T": 1, "S": 3, "M": 10, "W": 25, "X": 30}.get(cls, 10)))
        if risk == "R":
            cap *= float(b.get("risk_multiplier", 1.5))
        return {"cap_usd": round(cap, 2)}

    def _m_small(self, sig: Json, risk: str) -> bool:
        small = ((self.routing.get("classes") or {}).get("M") or {}).get("small") or {}
        return (sig["files"] <= small.get("max_files", 5) and sig["dirs"] <= small.get("max_dirs", 2)
                and risk == small.get("risk", "none"))

    def _open_next_action(self, task: Json) -> Tuple[str, str]:
        """(next_action, resume_hint) right after open/classify (design §3 per-class paths)."""
        cls, tid = task["class"], task["id"]
        if cls == "T":
            return (f"Edit the declared files inline, run .forge/bin/forge-check {tid} main, then /forge-close",
                    f"Class T: only the declared files may change; close with --one-line \"<what> | <checks/ record>\".")
        plan_cmd = f".forge/bin/forge-status plan {tid} --from .forge/tasks/{tid}/plan.md"
        if cls in ("S", "X"):
            return (f"Write the inline plan section to .forge/tasks/{tid}/plan.md (mode inline, DoD ids, rollback), then run {plan_cmd}",
                    f"Class {cls} runs inline in the architect once the plan section exists.")
        if cls == "M" and self._m_small(task["signals"], task["risk"]):
            return (f"Write .forge/tasks/{tid}/plan.md and brief-01.md, run .forge/bin/forge-gate --plan {tid}, then {plan_cmd}",
                    "M-small: the architect writes the plan and the single brief itself.")
        effort = "medium" if cls == "M" else "high"
        return (f"Dispatch forge-planner (fable/{effort}) to plan {tid}, then run {plan_cmd}",
                f"Class {cls}: the planner writes plan.md and one brief per step under .forge/tasks/{tid}/.")

    # ------------------------------------------------------------------ #
    # open / signals / classify
    # ------------------------------------------------------------------ #
    def _push_queue(self, st: Json, entry: Json) -> None:
        """Bounded queue: STATUS holds <= 10 entries, the rest live in queue.jsonl."""
        if len(st.get("queue") or []) < (self.schema.get("bounds") or {}).get("queue", 10):
            st.setdefault("queue", []).append(entry)
        else:
            common.append_jsonl(self.paths.queue, entry)

    def _pop_queue(self, st: Json, index: int) -> None:
        st["queue"].pop(index)
        rest = common.read_jsonl(self.paths.queue)
        if rest:
            st["queue"].append(rest[0])
            common.write_text_atomic(self.paths.queue, "".join(
                json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rest[1:]))

    def open(self, title: str, cls: str, risk: str, files: Iterable[str], creates: Iterable[str] = (), why: str = "",
             queue: bool = False, force_risk: bool = False, accept_risk_none: Optional[str] = None) -> Json:
        """new + signals + classify in one call (design §5.1 open row)."""
        st = self.load()
        files = common.unique(self.paths.rel(p) for p in files)
        creates = common.unique(self.paths.rel(p) for p in creates)
        if not title.strip():
            raise ForgeError("--title is required", EXIT_USAGE)
        if not files and not creates:
            raise ForgeError("declare the edit set with --files and/or --creates", EXIT_USAGE)
        if queue:
            task_id = common.next_task_id(self.paths)
            common.ensure_dir(self.paths.task(task_id))
            common.write_json_atomic(self.paths.task_file(task_id, "queued.json"), {
                "id": task_id, "title": title, "class_hint": cls, "risk": risk, "files": files,
                "creates": creates, "why": why, "queued_at": common.now_iso()})
            self._push_queue(st, {"id": task_id, "title": title, "class_hint": cls})
            self._journal(task_id, f"queued: {title} (class hint {cls})")
            self.save(st, f"open --queue {task_id}")
            return st
        if common.current_task(st) is not None:
            raise ForgeError(f"task {st['task']['id']} is open: close it first (or use --queue)", EXIT_REFUSED)
        task_id = None
        for i, q in enumerate(st.get("queue") or []):
            if q.get("title") == title:
                task_id = q.get("id")
                self._pop_queue(st, i)
                break
        task_id = task_id or common.next_task_id(self.paths)
        sig = self._compute_signals(title, files, creates)
        self._check_class(cls, risk, sig, why, force_risk, accept_risk_none)
        common.ensure_dir(self.paths.task(task_id))
        common.rm(self.paths.task_file(task_id, "queued.json"))
        declared = common.unique(files + creates)
        mode = "inline" if cls in ("T", "S", "X") else "single"
        task: Json = {
            "id": task_id, "title": title, "class": cls, "risk": risk, "size_source": "declared",
            "files": files, "creates": creates, "signals": self._status_signals(sig),
            "class_justification": self._justification(why, force_risk, accept_risk_none),
            "phase": "execute" if cls == "T" else "plan",
            "plan": None, "plan_author": None, "branch": None,
            "scope": declared,
            "routing": {"mode": mode, "builder": None, "verifier": None,
                        "justification": "class T: inline, no plan, no verifier" if cls == "T"
                        else f"class {cls}: routing is fixed by forge-status plan"},
            "steps": [], "escalation": {"step": None, "round": 0},
            "next_action": "", "resume_hint": "",
            "evidence_count": 0, "evidence": [], "blocked_on": None, "external": None,
            "budget": self._budget(cls, risk), "opened_at": common.now_iso(),
            "base": common.git_head(self.paths.root),
        }
        if cls == "X":
            task["routing"]["verifier"] = {"agent": "forge-verifier", "model": "fable", "effort": "medium"}
        if cls == "S":
            model = "opus" if sig["importers"] >= 5 else "sonnet"
            task["routing"]["verifier"] = {"agent": "forge-verifier", "model": model, "effort": "medium"}
        if risk == "R":
            task["routing"]["verifier"] = {"agent": "forge-verifier", "model": "fable", "effort": "medium"}
        git_cfg = self.binding.get("git") or {}
        if git_cfg.get("branch_per_task"):
            branch = f"{git_cfg.get('commit_prefix', 'forge')}/{task_id}"
            code, out = common.git(["checkout", "-q", "-B", branch], self.paths.root)
            if code != 0:
                raise ForgeError(f"cannot create branch {branch}: {out.strip().splitlines()[-1] if out.strip() else code}", EXIT_REFUSED)
            task["branch"] = branch
        task["next_action"], task["resume_hint"] = self._open_next_action(task)
        st["task"] = task
        self._write_signals(task_id, title, declared, sig)
        self._journal(task_id, f"open: {title} | class {cls} risk {risk} files={sig['files']} dirs={sig['dirs']} "
                               f"importers={sig['importers']} tests_present={sig['tests_present']} "
                               f"risk_hits={sig['risk_hits']} important={sig['important_hits']}")
        self._ledger({"event": "open", "task": task_id, "class": cls, "risk": risk,
                      "expected_premium": cls in ("X", "W") or risk == "R", "cost_source": "unknown"})
        self.save(st, f"open {task_id}")
        return st

    def signals(self, task_id: str) -> Json:
        """Recompute signals.json from the declared set (plus every step's allowed_paths); returns them."""
        st = self.load()
        task = self._task(st, task_id)
        extra = [p for s in task.get("steps") or [] for p in s.get("allowed_paths") or []]
        sig = self._compute_signals(task["title"], task["files"], task["creates"], extra)
        task["signals"] = self._status_signals(sig)
        self._write_signals(task_id, task["title"], common.unique(task["files"] + task["creates"]), sig)
        self._journal(task_id, f"signals recomputed: {task['signals']}")
        self.save(st, f"signals {task_id}")
        return sig

    def classify(self, task_id: str, cls: str, risk: str, why: str, force_risk: bool = False,
                 accept_risk_none: Optional[str] = None) -> Json:
        """Re-classify an open, not-yet-planned task (after needs_clarification, design §5.1)."""
        st = self.load()
        task = self._task(st, task_id)
        if task.get("steps"):
            raise ForgeError(f"{task_id} already has imported steps; re-plan instead of re-classifying", EXIT_REFUSED)
        if task["phase"] not in ("plan", "intake", "execute"):
            raise ForgeError(f"{task_id} is in phase {task['phase']}; classify only before execution starts", EXIT_REFUSED)
        sig = self._compute_signals(task["title"], task["files"], task["creates"])
        self._check_class(cls, risk, sig, why, force_risk, accept_risk_none)
        old = f"{task['class']}/{task['risk']}"
        task.update({"class": cls, "risk": risk, "signals": self._status_signals(sig),
                     "class_justification": self._justification(why, force_risk, accept_risk_none),
                     "phase": "execute" if cls == "T" else "plan", "plan": None, "plan_author": None,
                     "budget": self._budget(cls, risk)})
        task["routing"] = {"mode": "inline" if cls in ("T", "S", "X") else "single", "builder": None,
                           "verifier": None, "justification": f"re-classified from {old}: {why.strip()}"}
        if cls == "X" or risk == "R":
            task["routing"]["verifier"] = {"agent": "forge-verifier", "model": "fable", "effort": "medium"}
        elif cls == "S":
            task["routing"]["verifier"] = {"agent": "forge-verifier", "model": "opus" if sig["importers"] >= 5 else "sonnet", "effort": "medium"}
        task["next_action"], task["resume_hint"] = self._open_next_action(task)
        self._write_signals(task_id, task["title"], common.unique(task["files"] + task["creates"]), sig)
        self._journal(task_id, f"classify: {old} -> {cls}/{risk}: {why.strip()}")
        self.save(st, f"classify {task_id}")
        return st

    # ------------------------------------------------------------------ #
    # plan import (design §5.1 plan row, §4.3 rules 1, 2, 4, 5, 11, overrides)
    # ------------------------------------------------------------------ #
    def _class_defaults(self, cls: str) -> Json:
        return (self.routing.get("classes") or {}).get(cls) or {}

    def _plan_author(self, task_id: str, cls: str, sig: Json, risk: str) -> str:
        """forge-planner when a planner agent record is bound to this task or the class needs one."""
        agents_dir = os.path.join(self.paths.runtime, "agents")
        if os.path.isdir(agents_dir):
            for name in os.listdir(agents_dir):
                rec = common.read_json(os.path.join(agents_dir, name), default=None)
                if isinstance(rec, dict) and rec.get("task") == task_id and \
                        common.agent_role(rec.get("agent_type")) == "forge-planner":
                    return "forge-planner"
        if cls in ("W", "L") or (cls == "M" and not self._m_small(sig, risk)):
            return "forge-planner"
        return "architect"

    def _load_brief(self, task_id: str, brief: str, step_id: str) -> Tuple[str, Json]:
        """(repo-relative brief path, brief-meta) for a plan step; refuses on any shape defect."""
        path = brief if ("/" in brief or os.path.isabs(brief)) else self.paths.task_file(task_id, brief)
        if not os.path.isabs(path):
            path = os.path.join(self.paths.root, path)
        text = common.read_text(path)
        if text is None:
            raise ForgeError(f"step {step_id}: brief {self.paths.rel(path)} does not exist", EXIT_REFUSED)
        meta = common.json_block(text)
        if not meta or meta.get("schema") != common.SCHEMA_BRIEF:
            raise ForgeError(f"step {step_id}: brief {self.paths.rel(path)} has no {common.SCHEMA_BRIEF} json block", EXIT_REFUSED)
        if meta.get("step") != step_id or meta.get("task") != task_id:
            raise ForgeError(f"step {step_id}: brief-meta task/step ({meta.get('task')}/{meta.get('step')}) do not match", EXIT_REFUSED)
        allowed = [self.paths.rel(p) for p in meta.get("allowed_paths") or [] if isinstance(p, str)]
        if not allowed:
            raise ForgeError(f"step {step_id}: brief allowed_paths is empty", EXIT_REFUSED)
        meta["allowed_paths"] = common.unique(allowed)
        return self.paths.rel(path), meta

    def _gate_plan(self, task_id: str) -> None:
        """forge-gate --plan through forgelib.gates when present (lazy import; absent = skip, journaled)."""
        try:
            from . import gates  # noqa: WPS433 (optional module, written separately)
        except ImportError:
            self._journal(task_id, "plan: forgelib.gates missing; plan gate skipped (structural checks only)")
            return
        defects = gates.plan_validate(self.paths, task_id)
        if defects:
            raise ForgeError(f"plan gate: {'; '.join(str(x) for x in defects[:3])}", EXIT_REFUSED)

    def _default_builder(self, cls: str, step: Json, chain: bool) -> Tuple[str, str, str]:
        """(agent, model, effort) the matrix starts at for this class/step (design §4.2)."""
        c = self._class_defaults(cls)
        if cls == "M":
            key = "builder_chain" if (chain or (self.binding.get("routing") or {}).get("m_builder") == "fable-low") else "builder"
            b = c.get(key) or {"agent": "forge-builder", "model": "opus", "effort": "medium"}
        elif cls == "W":
            b = c.get("builder") or {"agent": "forge-builder-wide", "model": "fable", "effort": "low"}
        elif cls == "L":
            if step.get("mechanical"):
                b = c.get("unit_builder_mechanical") or {"agent": "forge-mechanic", "model": "haiku", "effort": "medium"}
            elif step.get("agent") == "forge-builder":
                b = c.get("unit_builder_m_sized") or {"agent": "forge-builder", "model": "opus", "effort": "medium"}
            else:
                b = c.get("unit_builder") or {"agent": "forge-builder-s", "model": "sonnet", "effort": "medium"}
        else:
            b = {"agent": "forge-builder", "model": "opus", "effort": "medium"}
        return b["agent"], common.alias_model(b["model"]) or "opus", b.get("effort", "medium")

    def _route_step(self, task: Json, step: Json, chain: bool, notes: List[str]) -> None:
        """Builder-side rules for one step; mutates `step`, appends journal notes, refuses hard violations."""
        b = self.binding
        cls, risk, sid = task["class"], task["risk"], step["id"]
        allowed = step["allowed_paths"]
        denied = list(b.get("mechanic_denied_paths") or []) + list(b.get("protected_paths") or []) + list(b.get("risk_paths") or [])
        # design §4.3 rule 5: the mechanic never touches risk, protected or mechanic_denied paths
        if step.get("mechanical"):
            hit = _globs_intersect(allowed, denied)
            if hit:
                raise ForgeError(f"step {sid}: mechanical: true refused, {hit} intersects mechanic_denied/protected/risk paths", EXIT_REFUSED)
        if step["agent"] == "forge-mechanic" and not step.get("mechanical"):
            raise ForgeError(f"step {sid}: forge-mechanic requires mechanical: true", EXIT_REFUSED)
        # design §3 risk overlay: floor forge-builder fable/low; -s and mechanic forbidden
        if risk == "R":
            if step["agent"] in ("forge-builder-s", "forge-mechanic"):
                raise ForgeError(f"step {sid}: risk R forbids {step['agent']}; use forge-builder fable/low", EXIT_REFUSED)
            if not common.tier_gte(step["model"], "fable"):
                notes.append(f"step {sid}: risk R raised builder {step['model']}/{step['effort']} to fable/low")
                step["model"], step["effort"] = "fable", "low"
        # design §4.4 overrides: a lower tier than the override's builder is refused
        for ov in (b.get("routing") or {}).get("overrides") or []:
            if not _globs_intersect(allowed, ov.get("paths") or []):
                continue
            ob = ov.get("builder") or {}
            if ob.get("model") and not common.tier_gte(step["model"], ob["model"]):
                raise ForgeError(f"step {sid}: override {ov.get('name')} requires builder {ob.get('agent', step['agent'])} "
                                 f"{common.alias_model(ob['model'])}/{ob.get('effort', 'medium')} (plan has {step['model']}/{step['effort']})", EXIT_REFUSED)
            notes.append(f"step {sid}: override {ov.get('name')} applies")
        # design §4.3 rule 2: a tier below the class default only with tests_present
        d_agent, d_model, d_effort = self._default_builder(cls, step, chain)
        if not common.tier_gte(step["model"], d_model) and not (task.get("signals") or {}).get("tests_present"):
            raise ForgeError(f"step {sid}: builder {step['model']} is below the class default {d_model} and tests_present is false; "
                             f"start at {d_agent} {d_model}/{d_effort}", EXIT_REFUSED)
        if step["agent"] == "forge-builder-wide" and cls != "W":
            raise ForgeError(f"step {sid}: forge-builder-wide is for class W only", EXIT_REFUSED)

    def _route_verifier(self, task: Json, plan_verifier: Optional[Json], steps: List[Json],
                        notes: List[str]) -> Json:
        """Verifier tier >= builder tier; advisory signals and risk only raise it (rules 4, 11)."""
        cls, sig = task["class"], task.get("signals") or {}
        c = self._class_defaults(cls)
        default = c.get("verifier") or c.get("unit_verifier") or {"agent": "forge-verifier", "model": "opus", "effort": "medium"}
        v = {"agent": "forge-verifier",
             "model": common.alias_model((plan_verifier or {}).get("model") or default.get("model")) or "opus",
             "effort": (plan_verifier or {}).get("effort") or default.get("effort", "medium")}

        def raise_to(model: str, effort: str, why: str) -> None:
            if not common.tier_gte(v["model"], model):
                notes.append(f"verifier raised {v['model']}/{v['effort']} -> {model}/{effort}: {why}")
                v["model"], v["effort"] = model, effort
            elif v["model"] == model and common.EFFORT_ORDER.get(v["effort"], 0) < common.EFFORT_ORDER.get(effort, 0):
                v["effort"] = effort

        for s in steps:
            raise_to(s["model"], "medium", f"builder tier of step {s['id']}")
        raise_cfg = default.get("raise_to") or {}
        if cls == "S" and sig.get("importers", 0) >= raise_cfg.get("if_importers_gte", 5):
            raise_to("opus", "medium", f"importers={sig.get('importers')}")
        if cls == "M" and sig.get("importers", 0) >= raise_cfg.get("if_importers_gte", 10):
            raise_to("fable", "medium", f"importers={sig.get('importers')}")
        if sig.get("important_hits"):
            raise_to("fable", "medium", f"important_hits={sig['important_hits']}")
        if task["risk"] == "R" or cls in ("X", "W"):
            raise_to("fable", "medium", "risk R / class X / class W verifier")
        for ov in (self.binding.get("routing") or {}).get("overrides") or []:
            if ov.get("min_verifier") and any(_globs_intersect(s["allowed_paths"], ov.get("paths") or []) for s in steps):
                raise_to(common.alias_model(ov["min_verifier"]) or "opus", "medium", f"override {ov.get('name')} min_verifier")
        return v

    def plan(self, task_id: str, plan_path: str) -> Json:
        """Import plan-meta, apply the routing rules, phase execute (or intake on needs_clarification)."""
        st = self.load()
        task = self._task(st, task_id)
        cls = task["class"]
        if cls == "T":
            raise ForgeError("class T has no plan: edit inline, forge-check, then close --one-line", EXIT_REFUSED)
        if task["phase"] not in ("plan", "intake"):
            raise ForgeError(f"{task_id} is in phase {task['phase']}; plan import needs phase plan", EXIT_REFUSED)
        abs_plan = plan_path if os.path.isabs(plan_path) else os.path.join(self.paths.root, plan_path)
        text = common.read_text(abs_plan)
        if text is None:
            raise ForgeError(f"plan file {self.paths.rel(abs_plan)} does not exist", EXIT_REFUSED)
        meta = common.json_block(text)
        if not meta or meta.get("schema") != common.SCHEMA_PLAN:
            raise ForgeError(f"{self.paths.rel(abs_plan)}: first json block must be plan-meta ({common.SCHEMA_PLAN})", EXIT_REFUSED)
        if meta.get("task") != task_id:
            raise ForgeError(f"plan-meta.task is {meta.get('task')!r}, expected {task_id}", EXIT_REFUSED)
        if not isinstance(meta.get("dod"), list) or not meta["dod"]:
            raise ForgeError("plan-meta.dod must be a non-empty list", EXIT_REFUSED)
        self._gate_plan(task_id)
        routing_meta = meta.get("routing") or {}
        mode = routing_meta.get("mode")
        steps_meta = meta.get("steps") or []
        chain = bool(meta.get("chain"))
        notes: List[str] = []
        # class/step-count constraints (design §5.1 plan row)
        if cls in ("S", "X"):
            if mode != "inline" or steps_meta:
                raise ForgeError(f"class {cls} plans are inline: routing.mode inline and steps == []", EXIT_REFUSED)
        elif mode == "inline":
            raise ForgeError(f"class {cls} cannot use mode inline", EXIT_REFUSED)
        if cls in ("M", "W") and len(steps_meta) != 1:
            raise ForgeError(f"class {cls} needs exactly one step (plan has {len(steps_meta)}): merge into one brief or re-class as L", EXIT_REFUSED)
        if cls == "L" and len(steps_meta) < 3:
            raise ForgeError(f"class L needs >= 3 path-disjoint units (plan has {len(steps_meta)})", EXIT_REFUSED)
        if mode not in common.MODES:
            raise ForgeError(f"routing.mode must be one of {'|'.join(common.MODES)}", EXIT_REFUSED)
        # import steps with their brief-meta
        steps: List[Json] = []
        seen = set()
        for sm in steps_meta:
            sid = str(sm.get("id", ""))
            if not _STEP_ID_RE.match(sid) or sid in seen:
                raise ForgeError(f"step id {sid!r} must be a unique two-digit id", EXIT_REFUSED)
            seen.add(sid)
            brief_rel, bmeta = self._load_brief(task_id, str(sm.get("brief") or f"brief-{sid}.md"), sid)
            agent = common.agent_role(sm.get("agent") or bmeta.get("owner_agent"))
            if agent not in common.WORKER_ROLES:
                raise ForgeError(f"step {sid}: agent must be one of {'|'.join(common.WORKER_ROLES)}", EXIT_REFUSED)
            model = common.alias_model(sm.get("model") or bmeta.get("model"))
            effort = sm.get("effort") or bmeta.get("effort") or "medium"
            if model not in common.MODELS or effort not in common.EFFORTS:
                raise ForgeError(f"step {sid}: model/effort {model}/{effort} invalid", EXIT_REFUSED)
            default_budget = common.WIDE_TOOL_BUDGET_DEFAULT if agent == "forge-builder-wide" else common.TOOL_BUDGET_DEFAULT
            steps.append({
                "id": sid, "title": str(sm.get("title") or bmeta.get("title") or f"step {sid}"),
                "agent": agent, "model": model, "effort": effort,
                "status": "pending", "attempts": 0, "from": None, "verify_attempts": 0,
                "started_at": None, "started_ts": None, "started_by": None, "agent_id": None,
                "base": None, "commit": None, "brief": brief_rel, "report": None, "verdict": None,
                "red_ok_until": sm.get("red_ok_until"), "allowed_paths": bmeta["allowed_paths"],
                "mechanical": bool(sm.get("mechanical")),
                "max_tool_calls": int(sm.get("max_tool_calls") or bmeta.get("max_tool_calls") or default_budget),
                "gate_blocks": 0,
            })
        for s in steps:
            if s["red_ok_until"] and s["red_ok_until"] <= s["id"]:
                raise ForgeError(f"step {s['id']}: red_ok_until must name a later step", EXIT_REFUSED)
        # design §4.3 rule 1 / §5.1: L units must be pairwise disjoint; parallel needs worktree isolation too
        if cls == "L":
            for i, a in enumerate(steps):
                for b_ in steps[i + 1:]:
                    hit = _globs_intersect(a["allowed_paths"], b_["allowed_paths"])
                    if hit:
                        raise ForgeError(f"class L units are not path-disjoint: steps {a['id']} and {b_['id']} share {hit}", EXIT_REFUSED)
        if mode == "parallel":
            if len(steps) < 3 or not (self.binding.get("git") or {}).get("worktree_isolation"):
                notes.append("mode parallel rewritten to single: needs >= 3 disjoint units and binding.git.worktree_isolation (design §4.3 rule 1)")
                mode = "single"
        # inline plans: allowed_paths from plan-meta, else the declared set
        inline_allowed = [self.paths.rel(p) for p in meta.get("allowed_paths") or [] if isinstance(p, str)]
        all_paths = common.unique(task["files"] + task["creates"] + inline_allowed
                                  + [p for s in steps for p in s["allowed_paths"]])
        # risk re-matched over every allowed path (design §3 step 4)
        hits = self._risk_hits(task["title"], all_paths)
        task["signals"]["risk_hits"] = hits
        task["signals"]["important_hits"] = [p for p in all_paths if common.any_glob(p, self.binding.get("important_paths") or [])]
        if hits and task["risk"] == "none" and "accept-risk-none" not in task["class_justification"]:
            if cls == "S":
                raise ForgeError(f"class S cannot carry risk hits ({', '.join(hits)}); re-class or re-open with --accept-risk-none", EXIT_REFUSED)
            task["risk"] = "R"
            task["budget"] = self._budget(cls, "R", len(steps), chain)
            notes.append(f"risk re-matched on plan paths -> R: {', '.join(hits)}")
        if task["risk"] == "R" and not str(meta.get("rollback") or "").strip():
            raise ForgeError("risk R requires plan-meta.rollback with a concrete command", EXIT_REFUSED)
        for s in steps:
            self._route_step(task, s, chain, notes)
        verifier = self._route_verifier(task, routing_meta.get("verifier"), steps, notes)
        builder = None
        if steps:
            lead = steps[0]
            builder = {"agent": lead["agent"], "model": lead["model"], "effort": lead["effort"]}
        justification = str(routing_meta.get("justification") or "").strip()
        if notes:
            justification = (justification + " | " if justification else "") + "; ".join(notes)
        task["routing"] = {"mode": mode, "builder": builder, "verifier": verifier, "justification": justification}
        task["steps"] = steps
        task["plan"] = self.paths.rel(abs_plan)
        task["plan_author"] = self._plan_author(task_id, cls, task["signals"], task["risk"])
        task["scope"] = common.unique(task["files"] + task["creates"] + inline_allowed
                                      + [p for s in steps for p in s["allowed_paths"]])
        task["budget"] = self._budget(cls, task["risk"], len(steps), chain)
        task["escalation"] = {"step": steps[0]["id"] if steps else None, "round": 0}
        questions = [str(q) for q in meta.get("needs_clarification") or []]
        if questions:
            task["phase"] = "intake"
            task["next_action"] = "ask the user: " + " | ".join(questions)
            task["resume_hint"] = "The plan needs answers; re-run forge-status plan after updating plan.md (or classify to re-class)."
        else:
            task["phase"] = "execute"
            task["next_action"] = self._default_next_action(task)
            task["resume_hint"] = (f"Plan imported from {task['plan']} ({len(steps)} step(s), mode {mode}). "
                                   f"Dispatch exactly the agent/model/effort STATUS records; the spawn guard refuses anything else.")
        self._journal(task_id, f"plan imported: {task['plan']} mode={mode} steps={[s['id'] for s in steps]} "
                               f"builder={builder} verifier={verifier} phase={task['phase']}"
                               + (f" | {'; '.join(notes)}" if notes else ""))
        self.save(st, f"plan {task_id}")
        return st

    # ------------------------------------------------------------------ #
    # step transitions (design §5.1 step-* rows, §4.3 rule 6/7)
    # ------------------------------------------------------------------ #
    def _check_records(self, task_id: str, step_id: str) -> List[Json]:
        """Parsed checks/<step>-*.json records for a step, newest first."""
        cdir = self.paths.checks_dir(task_id)
        if not os.path.isdir(cdir):
            return []
        rows: List[Json] = []
        for name in sorted(os.listdir(cdir), reverse=True):
            if name.startswith(f"{step_id}-") and name.endswith(".json"):
                rec = common.read_json(os.path.join(cdir, name), default=None)
                if isinstance(rec, dict):
                    rec["_file"] = self.paths.rel(os.path.join(cdir, name))
                    rows.append(rec)
        return rows

    def _plan_meta(self, task: Json) -> Json:
        if not task.get("plan"):
            return {}
        text = common.read_text(os.path.join(self.paths.root, task["plan"])) or ""
        return common.json_block(text) or {}

    def _append_failed_approach(self, task_id: str, step: Json) -> None:
        """step-start --from failed: append the last verdict's blocking findings to the brief (§4.3 rule 6)."""
        vpath = self.paths.task_file(task_id, f"verdict-{step['id']}.json")
        verdict = common.read_json(vpath, default=None) if common.exists(vpath) else None
        if not isinstance(verdict, dict):
            return
        findings = verdict.get("blocking_findings") or []
        line = (f"- attempt {step['attempts']} verdict {verdict.get('verdict')} ({common.now_iso()}): "
                + ("; ".join(str(f) for f in findings) if findings else "no blocking findings recorded"))
        bpath = os.path.join(self.paths.root, step["brief"])
        text = common.read_text(bpath)
        if text is None:
            return
        lines = text.splitlines()
        heading = "## Known failed approaches"
        try:
            idx = next(i for i, l in enumerate(lines) if l.strip().lower() == heading.lower())
        except StopIteration:
            lines += ["", heading]
            idx = len(lines) - 1
        end = idx + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        lines.insert(end, line)
        common.write_text_atomic(bpath, "\n".join(lines) + "\n")

    def step_start(self, task_id: str, step_id: str, frm: Optional[str] = None, agent_id: Optional[str] = None) -> Json:
        """pending (or failed with --from) -> running; attempts += 1; writes .base-NN; ledger dispatch row."""
        st = self.load()
        task = self._task(st, task_id)
        step = self._step(task, step_id)
        if frm not in (None, "failed", "clean"):
            raise ForgeError("--from must be failed or clean", EXIT_USAGE)
        if step["status"] == "failed" and frm is None:
            raise ForgeError(f"step {step_id} is failed: pass --from failed (keep the tree) or --from clean (recover to base)", EXIT_REFUSED)
        if step["status"] not in ("pending", "failed"):
            raise ForgeError(f"step {step_id} is {step['status']}, not pending/failed", EXIT_REFUSED)
        if step["status"] == "pending" and frm is not None:
            raise ForgeError(f"step {step_id} is pending; --from {frm} applies to a failed step", EXIT_REFUSED)
        # design §4.3 rule 6: attempts capped at 3 without a ruling.md
        if step["attempts"] >= MAX_ATTEMPTS and not self._has_ruling(task_id):
            raise ForgeError(f"step {step_id} already has {step['attempts']} attempts: write .forge/tasks/{task_id}/ruling.md before another", EXIT_REFUSED)
        if task["routing"]["mode"] != "parallel":
            other = next((s for s in task["steps"] if s["id"] != step_id and s["status"] in ("running", "verifying")), None)
            if other:
                raise ForgeError(f"step {other['id']} is {other['status']}; mode {task['routing']['mode']} runs one step at a time", EXIT_REFUSED)
        if task["phase"] in ("blocked",):
            raise ForgeError(f"{task_id} is blocked ({task.get('blocked_on')}): unblock first", EXIT_REFUSED)
        prev = f"{step['model']}/{step['effort']}" if step["attempts"] else None
        if frm == "clean":
            self._recover_tree(task, step, "step-start --from clean")
        if frm == "failed":
            self._append_failed_approach(task_id, step)
        base = common.git_head(self.paths.root)
        step.update({"status": "running", "attempts": step["attempts"] + 1, "from": frm,
                     "started_at": common.now_iso(), "started_ts": common.now_ts(), "started_by": self.session(),
                     "agent_id": agent_id, "base": base, "commit": None, "report": None, "verdict": None,
                     "gate_blocks": 0})
        common.write_text_atomic(self.paths.base_file(task_id, step_id), (base or "") + "\n")
        task["phase"] = "execute"
        task["escalation"]["step"] = step_id
        task["external"] = None
        if frm:
            task["next_action"] = self._dispatch_text(step)
        else:
            task["next_action"] = self._default_next_action(task)
        task["resume_hint"] = (f"Step {step_id} attempt {step['attempts']} started by session {self.session()} at base {_short(base)}. "
                               f"If this session is gone and no report exists: .forge/bin/forge-status recover {task_id} {step_id}.")
        escalated_from = prev if (prev and prev != f"{step['model']}/{step['effort']}") else None
        self._journal(task_id, f"step-start {step_id}: attempt {step['attempts']} from={frm} base={_short(base)} agent_id={agent_id}")
        self._ledger({"event": "dispatch", "task": task_id, "step": step_id, "class": task["class"], "agent": step["agent"],
                      "model": step["model"], "effort": step["effort"], "attempt": step["attempts"],
                      "escalated_from": escalated_from})
        self.save(st, f"step-start {task_id} {step_id}")
        return st

    def step_bind(self, task_id: str, step_id: str, agent_id: str) -> Json:
        """Bind a worker to a running, unbound step (MODULE-API §2.11)."""
        st = self.load()
        task = self._task(st, task_id)
        step = self._step(task, step_id)
        if not agent_id:
            raise ForgeError("--agent is required", EXIT_USAGE)
        if step["status"] != "running":
            raise ForgeError(f"step {step_id} is {step['status']}, not running", EXIT_REFUSED)
        if step.get("agent_id") and step["agent_id"] != agent_id:
            raise ForgeError(f"step {step_id} is already bound to {step['agent_id']}", EXIT_REFUSED)
        step["agent_id"] = agent_id
        self._journal(task_id, f"step-bind {step_id}: agent {agent_id}")
        self.save(st, f"step-bind {task_id} {step_id}")
        return st

    def step_verifying(self, task_id: str, step_id: str, agent_id: Optional[str] = None) -> Json:
        """reported -> verifying on verifier dispatch; verify_attempts += 1, capped at 2 without a ruling."""
        st = self.load()
        task = self._task(st, task_id)
        step = self._step(task, step_id)
        if step["status"] not in ("reported", "verifying"):
            raise ForgeError(f"step {step_id} is {step['status']}; a verifier needs a reported step", EXIT_REFUSED)
        # design §4.3 rule 6: verify_attempts capped at 2 per step without a ruling
        if step["verify_attempts"] >= MAX_VERIFY_ATTEMPTS and not self._has_ruling(task_id):
            raise ForgeError(f"step {step_id} already had {step['verify_attempts']} verifier dispatches: write ruling.md first", EXIT_REFUSED)
        step["status"] = "verifying"
        step["verify_attempts"] += 1
        step["verifier_agent_id"] = agent_id
        task["phase"] = "verify"
        task["next_action"] = f"Await forge-verifier on step {step_id}; its verdict gate records the verdict"
        vm, ve = self._verifier(task)
        self._journal(task_id, f"step-verifying {step_id}: verifier dispatch {step['verify_attempts']} ({vm}/{ve}) agent_id={agent_id}")
        self._ledger({"event": "dispatch", "task": task_id, "step": step_id, "class": task["class"], "agent": "forge-verifier",
                      "model": vm, "effort": ve, "attempt": step["verify_attempts"], "escalated_from": None})
        self.save(st, f"step-verifying {task_id} {step_id}")
        return st

    def _read_report(self, task_id: str, step_id: str, path: str) -> Json:
        abs_path = path if os.path.isabs(path) else os.path.join(self.paths.root, path)
        rep = common.read_json(abs_path, default=None) if common.exists(abs_path) else None
        if not isinstance(rep, dict):
            raise ForgeError(f"report {self.paths.rel(abs_path)} missing or not a JSON object", EXIT_REFUSED)
        for k in ("schema", "task", "step", "status", "files_changed", "checks_run"):
            if k not in rep:
                raise ForgeError(f"report {self.paths.rel(abs_path)} lacks {k}", EXIT_REFUSED)
        if rep["schema"] != common.SCHEMA_HANDOFF or rep["task"] != task_id or str(rep["step"]) != step_id:
            raise ForgeError(f"report schema/task/step mismatch ({rep['schema']} {rep['task']}/{rep['step']})", EXIT_REFUSED)
        if rep["status"] not in common.HANDOFF_STATUSES:
            raise ForgeError(f"report status {rep['status']!r} not in {'|'.join(common.HANDOFF_STATUSES)}", EXIT_REFUSED)
        rep["_path"] = self.paths.rel(abs_path)
        return rep

    def step_report(self, task_id: str, step_id: str, report_json_path: str) -> Json:
        """running -> reported (DONE*), blocked (BLOCKED/NEEDS_CONTEXT) or failed (UNVERIFIED); ledger attempt row."""
        st = self.load()
        task = self._task(st, task_id)
        step = self._step(task, step_id)
        if step["status"] not in ("running", "blocked", "failed"):
            raise ForgeError(f"step {step_id} is {step['status']}: nothing to report", EXIT_REFUSED)
        rep = self._read_report(task_id, step_id, report_json_path)
        md = rep["_path"][:-5] + ".md" if rep["_path"].endswith(".json") else rep["_path"]
        step["report"] = md if common.exists(os.path.join(self.paths.root, md)) else rep["_path"]
        status = rep["status"]
        tid = task_id
        if status in ("DONE", "DONE_WITH_CONCERNS"):
            step["status"] = "reported"
            step["commit"] = rep.get("commit") or None
            task["phase"] = "execute"
            task["next_action"] = self._verify_text(task, step)
            task["resume_hint"] = (f"Step {step_id} is {status} and committed ({_short(step['commit'])}). "
                                   f"Dispatch the verifier named in next_action; the verdict gate records the outcome.")
        elif status == "UNVERIFIED":
            step["status"] = "failed"
            task["phase"] = "execute"
            task["next_action"] = (f"Step {step_id} UNVERIFIED (handoff gate bypassed): resume {step.get('agent_id') or 'the worker'} via SendMessage, "
                                   f"or run .forge/bin/forge-status step-start {tid} {step_id} --from failed|clean and re-dispatch")
            task["resume_hint"] = f"No commit was made for step {step_id}; its tree changes are uncommitted."
        else:  # BLOCKED | NEEDS_CONTEXT
            step["status"] = "blocked"
            task["phase"] = "execute"
            what = rep.get("next_action") or "see the report"
            task["next_action"] = (f"Step {step_id} {status} ({what}): read {_basename(step['report'])}, then resume "
                                   f"{step.get('agent_id') or 'the worker'} via SendMessage with the missing context, "
                                   f"run .forge/bin/forge-status step-start {tid} {step_id} --from failed|clean, scope add, or block --on")
            task["resume_hint"] = f"Worker on step {step_id} stopped with {status}."
        self._journal(task_id, f"step-report {step_id}: {status} commit={_short(step.get('commit'))} report={step['report']}")
        self._ledger({"event": "attempt", "task": task_id, "step": step_id, "class": task["class"], "agent": step["agent"],
                      "model": step["model"], "effort": step["effort"], "attempt": step["attempts"], "status": status,
                      "gate_blocks": step.get("gate_blocks", 0), "commit": step.get("commit")})
        self.save(st, f"step-report {task_id} {step_id}", clear_dirty="worker")
        return st

    def _read_verdict(self, task_id: str, step_id: str, path: str) -> Json:
        abs_path = path if os.path.isabs(path) else os.path.join(self.paths.root, path)
        v = common.read_json(abs_path, default=None) if common.exists(abs_path) else None
        if not isinstance(v, dict):
            raise ForgeError(f"verdict {self.paths.rel(abs_path)} missing or not a JSON object", EXIT_REFUSED)
        if v.get("schema") != common.SCHEMA_VERDICT or v.get("task") != task_id or str(v.get("step")) != step_id:
            raise ForgeError(f"verdict schema/task/step mismatch ({v.get('schema')} {v.get('task')}/{v.get('step')})", EXIT_REFUSED)
        if v.get("verdict") not in common.VERDICTS:
            raise ForgeError(f"verdict value {v.get('verdict')!r} not in {'|'.join(common.VERDICTS)}", EXIT_REFUSED)
        v["_path"] = self.paths.rel(abs_path)
        return v

    def _external_needs(self, task: Json, verdict: Json) -> Tuple[List[str], str]:
        """(pending external DoD ids, what the human runs) for a non-PASS verdict (design §4.3 rule 7, §7 gate 13)."""
        dod = {d.get("id"): d for d in self._plan_meta(task).get("dod") or [] if isinstance(d, dict)}
        pending, hows = [], []
        for c in verdict.get("criteria") or []:
            if c.get("result") == "PASS":
                continue
            entry = dod.get(c.get("id")) or {}
            # design §5.6: an external criterion is UNKNOWN until a human attests; FAIL means it was attested failing
            if entry.get("check") == "external" and c.get("result") == "UNKNOWN":
                pending.append(c.get("id"))
                how = (entry.get("external") or {}).get("how") or (entry.get("external") or {}).get("what")
                if how:
                    hows.append(str(how))
        return pending, "; ".join(common.unique(hows)) if hows else ""

    def step_verdict(self, task_id: str, step_id: str, verdict_json_path: str) -> Json:
        """verifying -> step_done (PASS) | step_external (env/external only) | step_fail; ledger verdict row."""
        st = self.load()
        task = self._task(st, task_id)
        step = self._step(task, step_id)
        if step["status"] != "verifying":
            raise ForgeError(f"step {step_id} is {step['status']}, not verifying", EXIT_REFUSED)
        v = self._read_verdict(task_id, step_id, verdict_json_path)
        md = v["_path"][:-5] + ".md" if v["_path"].endswith(".json") else v["_path"]
        step["verdict"] = md if common.exists(os.path.join(self.paths.root, md)) else v["_path"]
        tags = [t for t in v.get("tags") or [] if isinstance(t, str)]
        vm, _ = self._verifier(task)
        self._journal(task_id, f"step-verdict {step_id}: {v['verdict']} tags={tags} blocking={len(v.get('blocking_findings') or [])}")
        self._ledger({"event": "verdict", "task": task_id, "step": step_id, "class": task["class"], "verdict": v["verdict"],
                      "verifier_model": vm, "tags": tags, "gate_blocks": step.get("gate_blocks", 0),
                      "attempt": step["verify_attempts"]})
        if v["verdict"] == "PASS":
            self._step_done(task, step, no_verifier=False)
            self.save(st, f"step-verdict {task_id} {step_id}", clear_dirty="worker")
            return st
        pending, how = self._external_needs(task, v)
        non_pass = [c for c in v.get("criteria") or [] if c.get("result") != "PASS"]
        env_only = bool(tags) and all(t == "env-cannot-run" for t in tags)
        external_only = bool(pending) and len(pending) == len(non_pass)
        if env_only or external_only:
            needs = how or "; ".join(str(c.get("cmd") or c.get("id")) for c in non_pass) or "the environment-bound checks"
            self._step_external(task, step, needs, pending or [c.get("id") for c in non_pass], v)
        else:
            self._step_fail(task, step, v)
        self.save(st, f"step-verdict {task_id} {step_id}", clear_dirty="worker")
        return st

    def _step_done(self, task: Json, step: Json, no_verifier: bool) -> None:
        """Transition guard (design §7 gate 8): commit descends from base and touches only allowed paths."""
        task_id, sid = task["id"], step["id"]
        if no_verifier:
            if task["class"] not in ("T", "S"):
                raise ForgeError(f"--no-verifier is only for classes T and S (task is {task['class']})", EXIT_REFUSED)
            if not any(r.get("ok") is True for r in self._check_records(task_id, sid)):
                raise ForgeError(f"step {sid}: --no-verifier needs a checks/ record with ok: true", EXIT_REFUSED)
            step["no_verifier"] = True
        commit = step.get("commit")
        if not commit:
            raise ForgeError(f"step {sid} has no commit recorded (the handoff gate commits DONE work)", EXIT_REFUSED)
        base = step.get("base") or (common.read_text(self.paths.base_file(task_id, sid)) or "").strip()
        if not base:
            raise ForgeError(f"step {sid} has no base recorded (.base-{sid} missing)", EXIT_REFUSED)
        if not common.git_is_ancestor(self.paths.root, base, commit):
            raise ForgeError(f"step {sid}: commit {_short(commit)} does not descend from base {_short(base)}", EXIT_REFUSED)
        allowed = list(step["allowed_paths"]) + [f".forge/tasks/{task_id}/**"]
        for p in common.git_diff_names(self.paths.root, base, commit):
            if not common.any_glob(p, allowed):
                raise ForgeError(f"step {sid}: commit {_short(commit)} touches {p}, outside allowed_paths", EXIT_REFUSED)
        step["status"] = "done"
        if task["routing"]["mode"] == "parallel" and step.get("branch"):
            code, _ = common.git(["merge", "-q", "--ff-only", step["branch"]], self.paths.root)
            if code != 0:
                code, out = common.git(["merge", "-q", "--no-ff", "-m", f"forge({task_id}/{sid}): merge unit", step["branch"]], self.paths.root)
                if code != 0:
                    raise ForgeError(f"step {sid}: cannot merge unit branch {step['branch']}: {out.strip()[-200:]}", EXIT_REFUSED)
        if all(s["status"] == "done" for s in task["steps"]):
            task["phase"] = "done"
            task["next_action"] = "Run /forge-close"
            task["resume_hint"] = f"All steps of {task_id} are done and committed; close with the handoff sized to class {task['class']}."
            task["escalation"]["step"] = None
        else:
            task["phase"] = "execute"
            nxt = self._current_step(task)
            task["escalation"] = {"step": nxt["id"] if nxt else None, "round": 0}
            task["next_action"] = self._default_next_action(task)
            task["resume_hint"] = f"Step {sid} done ({_short(commit)}); continue with step {nxt['id'] if nxt else '?'}."
        self._journal(task_id, f"step-done {sid}: commit {_short(commit)} (base {_short(base)}) no_verifier={no_verifier}")
        self._ledger({"event": "step_done", "task": task_id, "step": sid, "class": task["class"], "agent": step["agent"],
                      "model": step["model"], "effort": step["effort"], "attempt": step["attempts"], "commit": commit})

    def step_done(self, task_id: str, step_id: str, no_verifier: bool = False) -> Json:
        """PASS verdict (or --no-verifier with a green checks/ record for T/S) -> done."""
        st = self.load()
        task = self._task(st, task_id)
        step = self._step(task, step_id)
        if step["status"] == "done":
            raise ForgeError(f"step {step_id} is already done", EXIT_REFUSED)
        if not no_verifier:
            vpath = self.paths.task_file(task_id, f"verdict-{step_id}.json")
            v = common.read_json(vpath, default=None) if common.exists(vpath) else None
            if not isinstance(v, dict) or v.get("verdict") != "PASS" or v.get("step") != step_id:
                raise ForgeError(f"step {step_id} has no PASS verdict (verdict-{step_id}.json)", EXIT_REFUSED)
            step["verdict"] = step.get("verdict") or self.paths.rel(vpath)
        self._step_done(task, step, no_verifier)
        self.save(st, f"step-done {task_id} {step_id}", clear_dirty="worker")
        return st

    def _ladder(self, step: Json, tags: List[str]) -> Tuple[str, str, str]:
        """design §4.3 rule 3/6: effort before model on skipped-file/no-check-run/not-double-checked; else one rung up."""
        model, effort = step["model"], step["effort"]
        if any(t in EFFORT_TAGS for t in tags):
            order = list(common.EFFORTS)
            effort = order[min(order.index(effort) + 1, order.index("high"))] if effort in order else "medium"
        else:
            model, effort = common.next_tier(model, effort)
        agent = step["agent"]
        if agent in ("forge-builder-s", "forge-mechanic") and model in ("opus", "fable"):
            agent = "forge-builder"
        return agent, model, effort

    def _step_fail(self, task: Json, step: Json, verdict: Json) -> None:
        """FAIL -> failed; escalation.round += 1; round 2 moves the step one rung up the ladder."""
        task_id, sid = task["id"], step["id"]
        tags = [t for t in verdict.get("tags") or [] if isinstance(t, str)]
        step["status"] = "failed"
        esc = task["escalation"]
        esc["round"] = (esc.get("round") or 0) + 1 if esc.get("step") == sid else 1
        esc["step"] = sid
        task["phase"] = "execute"
        rnd = esc["round"]
        vfile = _basename(step.get("verdict"))
        escalated = None
        if rnd == 1:
            task["next_action"] = (f"Resume {step.get('agent_id') or 'the builder'} via SendMessage with the blocking findings "
                                   f"from {vfile} (round 1; same worker)")
        elif rnd == 2:
            agent, model, effort = self._ladder(step, tags)
            if (model, effort) != (step["model"], step["effort"]):
                escalated = f"{step['model']}/{step['effort']}"
                step["agent"], step["model"], step["effort"] = agent, model, effort
                task["routing"]["builder"] = {"agent": agent, "model": model, "effort": effort}
                task["routing"]["verifier"] = self._route_verifier(task, task["routing"].get("verifier"), task["steps"], [])
            task["next_action"] = (f"Run .forge/bin/forge-status step-start {task_id} {sid} --from failed|clean, then "
                                   f"{self._dispatch_text(step)} (round 2; findings in {vfile})")
        else:
            task["next_action"] = (f"Write .forge/tasks/{task_id}/ruling.md (Decision — Why — Cost if wrong — Evidence), "
                                   f"then re-plan or run .forge/bin/forge-status block {task_id} --on \"...\" (round {rnd})")
        task["resume_hint"] = f"Step {sid} failed verification (round {rnd}, tags {tags})."
        self._journal(task_id, f"step-fail {sid}: round {rnd} tags={tags}" + (f" escalated from {escalated}" if escalated else ""))
        self._ledger({"event": "step_fail", "task": task_id, "step": sid, "class": task["class"], "agent": step["agent"],
                      "model": step["model"], "effort": step["effort"], "attempt": step["attempts"], "tags": tags,
                      "escalations": rnd, "escalated_from": escalated})

    def step_fail(self, task_id: str, step_id: str) -> Json:
        """A FAIL/UNKNOWN verdict file for this step -> failed (standalone form of the step-verdict branch)."""
        st = self.load()
        task = self._task(st, task_id)
        step = self._step(task, step_id)
        if step["status"] not in ("verifying", "reported", "running"):
            raise ForgeError(f"step {step_id} is {step['status']}; step-fail needs a verified step", EXIT_REFUSED)
        vpath = self.paths.task_file(task_id, f"verdict-{step_id}.json")
        v = common.read_json(vpath, default=None) if common.exists(vpath) else None
        if not isinstance(v, dict) or v.get("verdict") not in ("FAIL", "UNKNOWN"):
            raise ForgeError(f"step {step_id} has no FAIL verdict (verdict-{step_id}.json)", EXIT_REFUSED)
        step["verdict"] = step.get("verdict") or self.paths.rel(vpath)
        self._step_fail(task, step, v)
        self.save(st, f"step-fail {task_id} {step_id}", clear_dirty="worker")
        return st

    def _step_external(self, task: Json, step: Json, needs: str, criteria: List[str], verdict: Optional[Json]) -> None:
        task_id, sid = task["id"], step["id"]
        step["status"] = "awaiting_external"
        task["phase"] = "awaiting_external"
        task["external"] = {"step": sid, "criteria": [c for c in criteria if c], "needs": needs}
        crit = (criteria[0] if criteria else "<DoD-n>") or "<DoD-n>"
        task["next_action"] = (f"Run: {needs}; then .forge/bin/forge-status attest {task_id} {sid} {crit} "
                               f"--by <you> --evidence <url|path>")
        task["resume_hint"] = f"Step {sid} waits for an external check; no builder re-run and no escalation (design §4.3 rule 7)."
        self._journal(task_id, f"step-external {sid}: needs {needs!r} criteria={criteria}"
                               + (f" (verdict {verdict.get('verdict')})" if verdict else ""))

    def step_external(self, task_id: str, step_id: str, needs: str) -> Json:
        """Park a step on an environment-bound check the human must run."""
        st = self.load()
        task = self._task(st, task_id)
        step = self._step(task, step_id)
        if not (needs or "").strip():
            raise ForgeError("--needs must name the commands the human runs", EXIT_USAGE)
        if step["status"] not in ("verifying", "reported", "failed", "awaiting_external"):
            raise ForgeError(f"step {step_id} is {step['status']}; awaiting_external needs a verified or reported step", EXIT_REFUSED)
        pending = [d.get("id") for d in self._plan_meta(task).get("dod") or []
                   if isinstance(d, dict) and d.get("check") == "external"]
        self._step_external(task, step, needs.strip(), pending, None)
        self.save(st, f"step-external {task_id} {step_id}", clear_dirty="worker")
        return st

    def attest(self, task_id: str, step_id: str, criterion: str, by: str, evidence: str, exit_code: int = 0) -> Json:
        """Human attestation record for a check: external criterion (design §7 gate 13)."""
        st = self.load()
        task = self._task(st, task_id)
        step = self._step(task, step_id)
        dod = {d.get("id"): d for d in self._plan_meta(task).get("dod") or [] if isinstance(d, dict)}
        if criterion not in dod or dod[criterion].get("check") != "external":
            raise ForgeError(f"{criterion} is not a check: external criterion of {task_id}", EXIT_REFUSED)
        if not by or not evidence:
            raise ForgeError("--by and --evidence are required", EXIT_USAGE)
        ts = common.now_ts()
        rec = {"ts": ts, "agent_id": "human", "source": "human", "by": by, "criterion": criterion, "evidence": evidence,
               "exit": int(exit_code), "task": task_id, "step": step_id, "session_id": self.session()}
        common.write_json_atomic(os.path.join(self.paths.checks_dir(task_id), f"{step_id}-{ts}-human.json"), rec)
        attested = {r.get("criterion") for r in self._check_records(task_id, step_id) if r.get("source") == "human" and r.get("exit") == 0}
        ext = task.get("external") or {}
        if step["status"] == "awaiting_external" and ext.get("step") == step_id:
            left = [c for c in ext.get("criteria") or [] if c not in attested]
            if left:
                task["next_action"] = (f"Attest the remaining external criteria {', '.join(left)}: .forge/bin/forge-status attest "
                                       f"{task_id} {step_id} <DoD-n> --by <you> --evidence <url|path>")
            else:
                step["status"] = "reported"
                task["phase"] = "execute"
                task["external"] = None
                task["next_action"] = self._verify_text(task, step)
                task["resume_hint"] = f"Every external criterion of step {step_id} is attested; re-dispatch the verifier."
        self._journal(task_id, f"attest {step_id} {criterion} by {by} exit {exit_code}: {evidence}")
        self.save(st, f"attest {task_id} {step_id} {criterion}")
        return st

    def _recover_tree(self, task: Json, step: Json, reason: str) -> str:
        """Save the step's tree changes as a patch, restore allowed_paths to .base-NN, remove new files."""
        task_id, sid = task["id"], step["id"]
        base = (common.read_text(self.paths.base_file(task_id, sid)) or "").strip() or step.get("base") or common.git_head(self.paths.root)
        specs = _git_pathspecs(step["allowed_paths"])
        root = self.paths.root
        _, diff = common.git(["diff", base, "--"] + specs, root)
        untracked = [p for p in common.git_porcelain(root, specs) if p]
        _, untracked_out = common.git(["ls-files", "--others", "--exclude-standard", "--"] + specs, root)
        new_files = [l.strip() for l in untracked_out.splitlines() if l.strip()]
        common.ensure_dir(self.paths.incidents)
        patch = os.path.join(self.paths.incidents, f"{common.now_ts()}-{task_id}-{sid}.patch")
        header = f"# forge recover {task_id}/{sid}: {reason}; base {base}; untracked: {new_files}\n"
        common.write_text_atomic(patch, header + (diff or ""))
        # index back to base for these paths, then restore each changed file by name
        # (git ls-tree ignores glob pathspecs; git diff / ls-files honour them)
        common.git(["reset", "-q", base, "--"] + specs, root)
        _, changed_out = common.git(["diff", "--name-only", base, "--"] + specs, root)
        changed = common.unique([l.strip() for l in changed_out.splitlines() if l.strip()] + new_files + untracked)
        restore, remove = [], []
        for f in changed:
            code, _ = common.git(["cat-file", "-e", f"{base}:{f}"], root)
            (restore if code == 0 else remove).append(f)
        if restore:
            common.git(["checkout", "-q", base, "--"] + restore, root)
        for f in remove:
            common.rm(os.path.join(root, f))
        self._journal(task_id, f"recover {sid}: {reason}; {len(changed)} changed path(s) saved to {self.paths.rel(patch)}; tree reset to {_short(base)}")
        self._ledger({"event": "recover", "task": task_id, "step": sid, "class": task["class"], "commit": base})
        return self.paths.rel(patch)

    def recover(self, task_id: str, step_id: str, force: bool = False) -> Json:
        """Interrupted step (running, other session, no report) -> pending with its tree restored."""
        st = self.load()
        task = self._task(st, task_id)
        step = self._step(task, step_id)
        if step["status"] != "running":
            raise ForgeError(f"step {step_id} is {step['status']}, not running", EXIT_REFUSED)
        if step.get("started_by") == self.session() and not force:
            raise ForgeError(f"step {step_id} was started by this session; pass --force to recover anyway", EXIT_REFUSED)
        report_md = self.paths.task_file(task_id, f"report-{step_id}.md")
        report_is_new = common.exists(report_md) and int(os.path.getmtime(report_md)) > int(step.get("started_ts") or 0)
        if step.get("report") or report_is_new:
            raise ForgeError(f"step {step_id} has a report for this attempt; run step-report instead of recover", EXIT_REFUSED)
        patch = self._recover_tree(task, step, f"recover (started_by {step.get('started_by')}, session {self.session()})")
        step.update({"status": "pending", "agent_id": None, "started_at": None, "started_ts": None, "started_by": None,
                     "commit": None, "report": None})
        task["phase"] = "execute"
        task["next_action"] = f"{self._dispatch_text(step)} (step {step_id} recovered; previous tree saved to {patch})"
        task["resume_hint"] = f"Step {step_id} was recovered to base {_short(step.get('base'))}; the spawn guard re-runs step-start on dispatch."
        self.save(st, f"recover {task_id} {step_id}")
        return st

    # ------------------------------------------------------------------ #
    # evidence, scope, block (design §5.1 rows; §7 gate 12)
    # ------------------------------------------------------------------ #
    def evidence(self, task_id: str, claim: str, from_check: str) -> Json:
        """Record a claim that points at a checks/ record (gate 12: claims need a record)."""
        st = self.load()
        task = self._task(st, task_id)
        abs_path = from_check if os.path.isabs(from_check) else os.path.join(self.paths.root, from_check)
        if not common.exists(abs_path):
            abs_path = os.path.join(self.paths.checks_dir(task_id), os.path.basename(from_check))
        rec = common.read_json(abs_path, default=None) if common.exists(abs_path) else None
        if not isinstance(rec, dict) or "results" not in rec and rec.get("source") != "human":
            raise ForgeError(f"--from-check must name an existing checks/ record ({from_check})", EXIT_REFUSED)
        if not (claim or "").strip():
            raise ForgeError("--claim is required", EXIT_USAGE)
        results = [r for r in rec.get("results") or [] if isinstance(r, dict) and r.get("status") != "skipped"]
        command = "; ".join(str(r.get("cmd")) for r in results) if results else str(rec.get("evidence") or "")
        exits = [int(r.get("exit")) for r in results if isinstance(r.get("exit"), int)]
        exit_code = next((e for e in exits if e != 0), 0) if exits else int(rec.get("exit") or 0)
        row = {"claim": claim.strip(), "command": command, "exit": exit_code, "when": common.now_iso(),
               "from": self.paths.rel(abs_path)}
        task["evidence"] = (task.get("evidence") or [])[-((self.schema.get("bounds") or {}).get("evidence", 10) - 1):] + [row]
        task["evidence_count"] = int(task.get("evidence_count") or 0) + 1
        self._journal(task_id, f"evidence: {row['claim']} <- {row['from']} (exit {exit_code})")
        self.save(st, f"evidence {task_id}")
        return st

    def scope_add(self, task_id: str, path: str, why: str, ruling: bool = False) -> Json:
        """Widen scope (class X, or any class with --ruling backed by ruling.md); journaled, ledger scope_add."""
        st = self.load()
        task = self._task(st, task_id)
        if not (why or "").strip():
            raise ForgeError("--why is required", EXIT_USAGE)
        if task["class"] != "X":
            if not ruling:
                raise ForgeError(f"scope add is for class X; class {task['class']} needs --ruling (and ruling.md)", EXIT_REFUSED)
            if not self._has_ruling(task_id):
                raise ForgeError(f"--ruling given but .forge/tasks/{task_id}/ruling.md does not exist", EXIT_REFUSED)
        rel = self.paths.rel(path)
        if rel.startswith(".forge/"):
            raise ForgeError("scope never includes .forge/** (meta paths are always allowed)", EXIT_REFUSED)
        if rel not in task["scope"]:
            task["scope"].append(rel)
        self._journal(task_id, f"scope add {rel}: {why.strip()}" + (" [ruling]" if ruling else ""))
        self._ledger({"event": "scope_add", "task": task_id, "class": task["class"], "status": rel})
        if ruling:
            self._ledger({"event": "ruling", "task": task_id, "class": task["class"], "status": f"scope add {rel}"})
        self.save(st, f"scope add {task_id} {rel}")
        return st

    def block(self, on: str) -> Json:
        st = self.load()
        task = common.current_task(st)
        if task is None:
            raise ForgeError("no task is open", EXIT_REFUSED)
        if not (on or "").strip():
            raise ForgeError("--on is required", EXIT_USAGE)
        if task["phase"] != "blocked":
            task["phase_before_block"] = task["phase"]
        task["phase"] = "blocked"
        task["blocked_on"] = on.strip()
        task["next_action"] = f"Blocked on: {on.strip()}. Resolve it, then run .forge/bin/forge-status unblock"
        self._journal(task["id"], f"block: {on.strip()}")
        self._ledger({"event": "phase", "task": task["id"], "class": task["class"], "phase": "blocked", "status": on.strip(),
                      "cost_source": "unknown"})
        self.save(st, "block")
        return st

    def unblock(self) -> Json:
        st = self.load()
        task = common.current_task(st)
        if task is None or task["phase"] != "blocked":
            raise ForgeError("task is not blocked", EXIT_REFUSED)
        task["phase"] = task.pop("phase_before_block", None) or "execute"
        if task["phase"] == "blocked":
            task["phase"] = "execute"
        task["blocked_on"] = None
        task["next_action"] = self._default_next_action(task)
        self._journal(task["id"], f"unblock -> {task['phase']}")
        self.save(st, "unblock")
        return st

    # ------------------------------------------------------------------ #
    # close (design §5.1 close row; §7 gates 8 and 12)
    # ------------------------------------------------------------------ #
    def _validate_task_handoff(self, task: Json, handoff_path: str) -> Tuple[str, Json]:
        """(repo-relative path, parsed json) of a task-level handoff; refuses on the first defect."""
        abs_path = handoff_path if os.path.isabs(handoff_path) else os.path.join(self.paths.root, handoff_path)
        text = common.read_text(abs_path)
        if text is None:
            raise ForgeError(f"handoff {self.paths.rel(abs_path)} does not exist", EXIT_REFUSED)
        try:
            from . import gates  # lazy: status.py imports even when gates.py is missing
        except ImportError:
            raise ForgeError("gates module missing", EXIT_REFUSED)
        short = task["class"] in ("S", "X")
        defects, parsed = gates.handoff_validate(self.paths, task["id"], "task", text, task_level=True, short=short)
        if defects:
            raise ForgeError(f"handoff invalid: {defects[0]}", EXIT_REFUSED)
        parsed = parsed or common.json_block(text) or {}
        if parsed.get("task") != task["id"] or parsed.get("step") != "task":
            raise ForgeError(f"handoff json must carry task {task['id']} and step \"task\"", EXIT_REFUSED)
        # design §7 gate 12: every "Done, with evidence" bullet names a command or a record
        done = common.section(text, "Done, with evidence")
        for line in done.splitlines():
            s = line.strip()
            if s.startswith(("- ", "* ")) and s[2:].strip().lower() not in ("none", "none.") and \
                    not ("`" in s or "checks/" in s or "verdict-" in s or "report-" in s):
                raise ForgeError(f"handoff: 'Done, with evidence' bullet without a command or checks/ reference: {s[:80]}", EXIT_REFUSED)
        return self.paths.rel(abs_path), parsed

    def _changed_paths(self, task: Json) -> List[str]:
        """git status --porcelain ∪ git diff --name-only <task.base>..HEAD (design §5.1 scope backstop)."""
        root = self.paths.root
        changed = list(common.git_porcelain(root))
        base = task.get("base")
        if base and common.git_head(root) and common.git_is_ancestor(root, base, "HEAD"):
            changed += common.git_diff_names(root, base, "HEAD")
        return common.unique(changed)

    def close(self, task_id: str, one_line: Optional[str] = None, handoff: Optional[str] = None, partial: bool = False,
              cost: Optional[float] = None, human_ack: Optional[str] = None, accept_out_of_scope: Optional[str] = None,
              no_commit: bool = False) -> Json:
        """Close (or park with --partial) the open task: CHANGELOG, history, ledger close, commit, clear policy."""
        st = self.load()
        task = self._task(st, task_id)
        cls = task["class"]
        if partial and not self._has_ruling(task_id):
            raise ForgeError(f"--partial needs .forge/tasks/{task_id}/ruling.md", EXIT_REFUSED)
        not_done = [s["id"] for s in task["steps"] if s["status"] != "done"]
        if not_done and not partial:
            raise ForgeError(f"step(s) {', '.join(not_done)} not done; finish them or close --partial with ruling.md", EXIT_REFUSED)
        if task["phase"] == "blocked" and not partial:
            raise ForgeError(f"{task_id} is blocked ({task.get('blocked_on')}); unblock or close --partial", EXIT_REFUSED)
        handoff_rel: Optional[str] = None
        if cls == "T":
            if not (one_line or "").strip():
                raise ForgeError("class T closes with --one-line \"<what> | <checks/ record>\"", EXIT_REFUSED)
            if not any(r.get("ok") is True for r in self._check_records(task_id, "main")):
                raise ForgeError(f"class T needs a checks/main-*.json record with ok: true (run .forge/bin/forge-check {task_id} main)", EXIT_REFUSED)
        else:
            if not handoff:
                raise ForgeError(f"class {cls} closes with --handoff .forge/tasks/{task_id}/handoff.md", EXIT_REFUSED)
            handoff_rel, _ = self._validate_task_handoff(task, handoff)
        if task["risk"] == "R" and not (human_ack or "").strip():
            raise ForgeError("risk R closes only with --human-ack \"<name> reviewed diff <sha>\"", EXIT_REFUSED)
        allowed = list(task["scope"]) + [p for s in task["steps"] for p in s["allowed_paths"]] + list(CLOSE_ALWAYS_ALLOWED)
        out = [p for p in self._changed_paths(task) if not common.any_glob(p, allowed)]
        if out and not accept_out_of_scope:
            raise ForgeError(f"out-of-scope changes: {', '.join(out[:8])}; revert them or pass --accept-out-of-scope \"<why>\"", EXIT_REFUSED)
        outcome = "parked" if partial else "done"
        cost_source = "operator" if cost is not None else "unknown"
        closed_at = common.now_iso()
        title = task["title"]
        summary = (one_line or "").strip() or f"handoff {handoff_rel}"
        tag = cls + ("/R" if task["risk"] == "R" else "")
        common.ensure_dir(self.paths.forge)
        with open(self.paths.changelog, "a", encoding="utf-8") as f:
            f.write(f"- {closed_at[:10]} {task_id} [{tag}] {title} — {summary} ({outcome})\n")
        row = {"id": task_id, "title": title, "class": cls, "outcome": outcome, "cost_usd": cost,
               "cost_source": cost_source, "handoff": handoff_rel, "closed_at": closed_at}
        common.append_jsonl(self.paths.history, row)
        st["history"] = ((st.get("history") or []) + [row])[-((self.schema.get("bounds") or {}).get("history", 5)):]
        self._ledger({"event": "close", "task": task_id, "class": cls, "outcome": outcome, "cost_usd": cost,
                      "cost_source": cost_source, "context_carried": st.get("context_state") == "stale",
                      "expected_premium": cls in ("X", "W") or task["risk"] == "R",
                      "escalations": (task.get("escalation") or {}).get("round", 0),
                      "status": human_ack or None, "verdict": accept_out_of_scope or None})
        self._journal(task_id, f"close: {outcome} | {summary}" + (f" | human_ack: {human_ack}" if human_ack else "")
                      + (f" | out-of-scope accepted: {out} ({accept_out_of_scope})" if out else ""))
        policy = self.binding.get("clear_policy", "phase")
        if policy in ("phase", "task"):
            st["context_state"] = "stale"
        st["task"] = None
        self.save(st, f"close {task_id}")
        if not no_commit:
            self._commit_close(task, out if accept_out_of_scope else [], title)
        return st

    def _commit_close(self, task: Json, extra: List[str], title: str) -> None:
        """git add -A -- .forge/ <scope> && git commit -q -m "forge(<id>): close" (skipped when clean)."""
        root = self.paths.root
        pathspecs = [".forge/"]
        for p in self._changed_paths(task) + extra:
            if common.any_glob(p, list(task["scope"]) + [x for s in task["steps"] for x in s["allowed_paths"]]
                               + ["CLAUDE.md", ".gitignore", ".claude/agent-memory/**"]) and not p.startswith(".forge/"):
                pathspecs.append(p)
        def log(msg: str) -> None:
            self._journal(None, f"{task['id']} {msg}")  # runtime log: the task dir is already staged

        code, out = common.git(["add", "-A", "--"] + common.unique(pathspecs), root)
        if code != 0:
            log(f"close: git add failed: {out.strip()[-200:]}")
            return
        # runtime markers and incident patches never enter a commit, even when .gitignore lacks them
        common.git(["rm", "-r", "-q", "--cached", "--ignore-unmatch", "--", ".forge/.runtime", ".forge/incidents"], root)
        code, _ = common.git(["diff", "--cached", "--quiet"], root)
        if code == 0:
            log("close: nothing to commit")
            return
        prefix = (self.binding.get("git") or {}).get("commit_prefix", "forge")
        code, out = common.git(["commit", "-q", "-m", f"{prefix}({task['id']}): close — {title}"], root)
        if code != 0:
            log(f"close: git commit failed: {out.strip()[-200:]}")
            return
        log(f"close: committed {_short(common.git_head(root))}")
        if (self.binding.get("git") or {}).get("branch_per_task") and task.get("branch"):
            log(f"close: branch_per_task — push {task['branch']} yourself (interactive ask)")

    # ------------------------------------------------------------------ #
    # context state, gate blocks
    # ------------------------------------------------------------------ #
    def stale(self) -> Json:
        st = self.load()
        st["context_state"] = "stale"
        task = common.current_task(st)
        self._journal(task.get("id") if task else None, "context_state -> stale")
        self.save(st, "stale")
        return st

    def fresh(self, stamp: bool = True) -> Json:
        """context_state fresh; removes auto-resumed-* markers; --no-stamp keeps updated_by (design §6 layer 5)."""
        st = self.load()
        st["context_state"] = "fresh"
        if os.path.isdir(self.paths.runtime):
            for name in os.listdir(self.paths.runtime):
                if name.startswith("auto-resumed-"):
                    common.rm(self.paths.rt(name))
        task = common.current_task(st)
        self._journal(task.get("id") if task else None, f"context_state -> fresh (stamp={stamp})")
        self.save(st, "fresh", stamp=stamp, clear_dirty="none")
        return st

    def gate_block(self, task_id: str, agent_id: str, gate: str) -> Json:
        """Count a gate block for an agent (task.gate_blocks[agent_id], step.gate_blocks); ledger gate_block row."""
        st = self.load()
        task = self._task(st, task_id)
        if not agent_id or not gate:
            raise ForgeError("--agent and --gate are required", EXIT_USAGE)
        counts = task.setdefault("gate_blocks", {})
        counts[agent_id] = int(counts.get(agent_id) or 0) + 1
        step = next((s for s in task["steps"] if agent_id in (s.get("agent_id"), s.get("verifier_agent_id"))), None)
        if step is not None:
            step["gate_blocks"] = int(step.get("gate_blocks") or 0) + 1
        self._journal(task_id, f"gate-block {gate}: agent {agent_id} block #{counts[agent_id]}" + (f" (step {step['id']})" if step else ""))
        self._ledger({"event": "gate_block", "task": task_id, "step": step["id"] if step else None, "class": task["class"],
                      "agent": agent_id, "status": gate, "gate_blocks": counts[agent_id]})
        self.save(st, f"gate-block {task_id}", clear_dirty="none")
        return st

    # ------------------------------------------------------------------ #
    # read-only
    # ------------------------------------------------------------------ #
    def digest(self, st: Json) -> str:
        """Compact STATUS digest, <= MAX_DIGEST chars (MODULE-API §3 digest format)."""
        lines: List[str] = []
        task = common.current_task(st)
        if task is None:
            lines.append(f"idle (project {st.get('project')}) context {st.get('context_state')}")
            lines.append(f"next: {self._idle_next(st)}")
        else:
            lines.append(f"{task['id']} \"{common.truncate(task['title'], 120, '…')}\" class {task['class']} risk {task['risk']} "
                         f"phase {task['phase']} mode {task['routing']['mode']}")
            for s in task["steps"]:
                lines.append(f"{s['id']} {s['status']} {s['agent']}/{s['model']}/{s['effort']} attempts={s['attempts']} "
                             f"commit={_short(s.get('commit'))}")
            lines.append(f"next: {common.truncate(task.get('next_action') or '', 400, '…')}")
            if task.get("resume_hint"):
                lines.append(f"resume_hint: {common.truncate(task['resume_hint'], 300, '…')}")
            if task.get("blocked_on"):
                lines.append(f"blocked_on: {task['blocked_on']}")
            if task.get("external"):
                ext = task["external"]
                lines.append(f"external: step {ext.get('step')} criteria {','.join(ext.get('criteria') or [])} needs {ext.get('needs')}")
            newest = (task.get("evidence") or [])[-2:]
            ev = "; ".join(f"\"{common.truncate(e.get('claim', ''), 60, '…')}\" exit {e.get('exit')}" for e in reversed(newest))
            lines.append(f"evidence: {task.get('evidence_count', 0)}" + (f" (newest 2: {ev})" if ev else ""))
        queue = st.get("queue") or []
        if queue:
            lines.append("queue: " + " ".join(q.get("id", "?") for q in queue[:10]))
        history = st.get("history") or []
        if history:
            lines.append("history: " + ", ".join(f"{h.get('id')} {h.get('outcome')}" for h in history[-5:]))
        tail = "[full: .forge/STATUS.json]"
        body = "\n".join(lines)
        if len(body) + len(tail) + 1 > common.MAX_DIGEST:
            body = common.truncate(body, common.MAX_DIGEST - len(tail) - 1)
        return body + "\n" + tail

    def _newest_handoff(self, st: Json) -> Optional[str]:
        """Newest handoff.md / report-NN.md of the open task (or of the last closed one)."""
        task = common.current_task(st)
        ids = [task["id"]] if task else [h["id"] for h in reversed(st.get("history") or []) if h.get("id")][:1]
        for tid in ids:
            tdir = self.paths.task(tid)
            if not os.path.isdir(tdir):
                continue
            cands = [os.path.join(tdir, n) for n in os.listdir(tdir)
                     if n == "handoff.md" or (n.startswith("report-") and n.endswith(".md"))]
            if cands:
                return max(cands, key=os.path.getmtime)
        return None

    def get(self, what: str, lenient: bool = False) -> str:
        """summary | resume | digest | next_action | dotted.path (MODULE-API §3); --lenient never raises."""
        try:
            st = self.load()
        except ForgeError as e:
            if lenient:
                return f"STATUS unavailable: {e}"
            raise
        task = common.current_task(st)
        if what == "summary":
            return self.one_line(st)
        if what == "next_action":
            return task.get("next_action") if task else self._idle_next(st)
        if what == "digest":
            return self.digest(st)
        if what == "resume":
            text = self.digest(st)
            newest = self._newest_handoff(st)
            if newest:
                body = common.read_text(newest) or ""
                for heading in ("Remaining", "Gotchas / do not touch"):
                    sec = common.section(body, heading).split("\n```", 1)[0].strip()
                    if sec:
                        text += f"\n\n## {heading} ({self.paths.rel(newest)})\n{common.truncate(sec, 1500)}"
            return text
        cur: Any = st
        for part in what.split("."):
            if isinstance(cur, dict):
                cur = cur.get(part)
            elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
                cur = cur[int(part)]
            else:
                cur = None
            if cur is None:
                break
        if cur is None:
            return "null"
        if isinstance(cur, (dict, list)):
            return json.dumps(cur, ensure_ascii=False)
        if isinstance(cur, bool):
            return "true" if cur else "false"
        return str(cur)
