"""forge-check: run binding.verify[] and the brief's checks, write a checks/ record (MODULE-API §5).

Design §5.7 (record shape), §7 gate 3, §13.3 (`forge-check`). Pure standard library.

Command list = binding.verify[] filtered by `when` (`always` | `paths:<glob>` against the step's
changed set, `{layer}` substituted from the matched path; a missing `exists` path → skipped)
∪ the brief's `checks[]` ∪ the plan-meta DoD checks of the brief's `dod[]` ids (every DoD check for
the inline step `main`), deduplicated by cmd. `--cmd '<command>'` runs that one command instead.
Each command runs through `bash -c` from the repo root with a 20-minute cap.
"""
from __future__ import annotations

import os
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from . import common
from . import gates

CHECK_TIMEOUT_S = 20 * 60      # design §13.3: 20-minute cap per command
TAIL_LINES = 15                # design §13.3: last 15 lines kept in the record
_LAYER_RE = re.compile(r"(^|/)layers/([^/]+)/")


# --------------------------------------------------------------------------- #
# Baseline and ratchet (design §13.3, §5.3 test_baseline)
# --------------------------------------------------------------------------- #
def test_files(paths: common.Paths, binding: Dict[str, Any]) -> List[str]:
    """Repo-relative files on disk matching binding.test_globs (sorted; .git and .forge skipped)."""
    globs = [g for g in binding.get("test_globs", []) or [] if isinstance(g, str)]
    if not globs:
        return []
    out: List[str] = []
    for dirpath, dirnames, filenames in os.walk(paths.root):
        rel_dir = paths.rel(dirpath)
        if rel_dir == ".":
            rel_dir = ""
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "node_modules", "__pycache__")
                       and not (rel_dir == "" and d == ".forge")]
        for name in filenames:
            rel = f"{rel_dir}/{name}" if rel_dir else name
            if common.any_glob(rel, globs):
                out.append(rel)
    return sorted(out)


def count_tests(paths: common.Paths, files: List[str], pattern: str) -> int:
    """Sum of lines matching `pattern` (extended regex, like `grep -cE`) across `files`."""
    if not pattern:
        return 0
    rx = re.compile(pattern)
    n = 0
    for f in files:
        text = common.read_text(os.path.join(paths.root, f), default="") or ""
        n += sum(1 for line in text.splitlines() if rx.search(line))
    return n


def baseline(paths: common.Paths) -> Dict[str, Any]:
    """{"files": n_test_files, "tests": n_matches, "recorded_at"} for plan-meta.test_baseline."""
    binding = common.load_binding(paths)
    files = test_files(paths, binding)
    return {"files": len(files), "tests": count_tests(paths, files, binding.get("test_pattern") or ""),
            "recorded_at": common.now_iso()}


def _deleted_test_files(paths: common.Paths, binding: Dict[str, Any], task_id: str, step: str) -> List[str]:
    """Test files deleted in the working tree, plus those deleted between the step/task base and HEAD."""
    globs = [g for g in binding.get("test_globs", []) or [] if isinstance(g, str)]
    deleted: List[str] = []
    code, out = common.git(["status", "--porcelain", "--untracked-files=no"], paths.root)
    if code == 0:
        for line in out.splitlines():
            if len(line) >= 4 and "D" in line[:2]:
                p = line[3:].strip().strip('"')
                if common.any_glob(p, globs):
                    deleted.append(p)
    base = (common.read_text(paths.base_file(task_id, step)) or "").strip()
    if not base:
        st = gates.safe_status(paths)
        task = common.current_task(st) if st else None
        if task and task.get("id") == task_id and task.get("base"):
            base = str(task["base"])
    if base:
        code, out = common.git(["diff", "--name-only", "--diff-filter=D", f"{base}..HEAD"], paths.root)
        if code == 0:
            for p in out.splitlines():
                p = p.strip()
                if p and common.any_glob(p, globs):
                    deleted.append(p)
    return common.unique(deleted)


def ratchet_check(paths: common.Paths, binding: Dict[str, Any], task_id: str, step: str,
                  may_edit_tests: bool = False) -> Dict[str, Any]:
    """Compare test files and `grep -cE test_pattern` totals against plan-meta.test_baseline.

    FAIL on a deleted test file, fewer test files or a lower count unless `may_edit_tests`;
    UNKNOWN without a baseline (design §13.3)."""
    files = test_files(paths, binding)
    now_tests = count_tests(paths, files, binding.get("test_pattern") or "")
    deleted = _deleted_test_files(paths, binding, task_id, step)
    pm = gates.plan_meta(paths, task_id) or {}
    tb = pm.get("test_baseline")
    rec: Dict[str, Any] = {"baseline_tests": None, "baseline_files": None, "now_tests": now_tests,
                           "now_files": len(files), "deleted_test_files": deleted, "status": "UNKNOWN"}
    if not isinstance(tb, dict) or not isinstance(tb.get("tests"), int) or not isinstance(tb.get("files"), int):
        rec["why"] = "no test_baseline in plan-meta (forge-check <task> plan --baseline)"
        return rec
    rec["baseline_tests"] = tb["tests"]
    rec["baseline_files"] = tb["files"]
    regressed = bool(deleted) or now_tests < tb["tests"] or len(files) < tb["files"]
    if regressed and not may_edit_tests:
        rec["status"] = "FAIL"
    else:
        rec["status"] = "PASS"
        if regressed:
            rec["why"] = "tests shrank but the brief allows may_edit_tests"
    return rec


# --------------------------------------------------------------------------- #
# Command selection
# --------------------------------------------------------------------------- #
def _layer_of(path: str) -> Optional[str]:
    """First path component after `layers/` (binding §2.2 `{layer}` from-path)."""
    m = _LAYER_RE.search(path)
    return m.group(2) if m else None


def changed_set(paths: common.Paths, task_id: str, step: str, only_paths: Optional[List[str]] = None) -> List[str]:
    """The step's changed set: porcelain limited to the brief's allowed_paths for a step, the whole
    porcelain for main/plan. `only_paths` restricts it to those globs (literal paths are added so
    `paths:` rules fire even on a clean tree)."""
    if step in ("main", "plan"):
        changed = [paths.rel(p) for p in common.git_porcelain(paths.root, None, untracked=True)]
    else:
        bm = gates.brief_meta(paths, task_id, step) or {}
        allowed = [a for a in bm.get("allowed_paths") or [] if isinstance(a, str)]
        changed = gates.tree_changed(paths, allowed) if allowed else []
    changed = [p for p in changed if not p.startswith(".forge/")]
    if only_paths:
        changed = [p for p in changed if common.any_glob(p, only_paths)]
        changed += [g for g in only_paths if "*" not in g and "?" not in g]
    return common.unique(changed)


def _matches_when(when: str, changed: List[str]) -> Tuple[bool, List[Optional[str]]]:
    """(fires, layers): whether a `paths:<glob>` rule matches the changed set; `layers` lists the
    distinct `{layer}` values of matched paths (a single None when the glob has no placeholder)."""
    if when == "always":
        return True, [None]
    if not when.startswith("paths:"):
        return False, []
    glob = when[len("paths:"):].strip()
    match_glob = glob.replace("{layer}", "*")
    layers: List[Optional[str]] = []
    for p in changed:
        if not common.glob_match(p, match_glob):
            continue
        if "{layer}" in glob:
            layer = _layer_of(p)
            if layer and layer not in layers:
                layers.append(layer)
        elif None not in layers:
            layers.append(None)
    return bool(layers), layers


def _substitute(text: str, layer: Optional[str]) -> str:
    return text.replace("{layer}", layer) if layer else text


def plan_commands(paths: common.Paths, binding: Dict[str, Any], task_id: str, step: str,
                  only: Optional[str] = None, only_paths: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Ordered list of {name, cmd, run: bool, why?} entries for this run (MODULE-API §5)."""
    changed = changed_set(paths, task_id, step, only_paths)
    entries: List[Dict[str, Any]] = []
    for v in binding.get("verify", []) or []:
        if not isinstance(v, dict) or not v.get("name") or not v.get("cmd"):
            continue
        name, when = str(v["name"]), str(v.get("when", "always"))
        if only is not None and name != only:
            continue
        fires, layers = _matches_when(when, changed)
        if not fires:
            entries.append({"name": name, "cmd": str(v["cmd"]), "run": False, "why": f"when: {when} did not match"})
            continue
        for layer in layers:
            cmd = _substitute(str(v["cmd"]), layer)
            ex = v.get("exists")
            if ex and not os.path.exists(os.path.join(paths.root, _substitute(str(ex), layer))):
                entries.append({"name": name, "cmd": cmd, "run": False,
                                "why": f"exists: {_substitute(str(ex), layer)} missing"})
                continue
            entries.append({"name": name, "cmd": cmd, "run": True})
    # Brief checks (plan-meta DoD checks for the inline step) run even when a verify entry is skipped.
    if only in (None, "brief", "dod"):
        running = {e["cmd"] for e in entries if e["run"]}
        if step == "main":
            pm = gates.plan_meta(paths, task_id) or {}
            for d in pm.get("dod", []) or []:
                c = d.get("check") if isinstance(d, dict) else None
                if isinstance(c, str) and c and c != "external" and c not in running:
                    entries.append({"name": f"brief:{d.get('id', 'dod')}", "cmd": c, "run": True})
                    running.add(c)
        elif step != "plan":
            bm = gates.brief_meta(paths, task_id, step) or {}
            if only in (None, "brief"):
                for c in bm.get("checks", []) or []:
                    if isinstance(c, str) and c and c not in running:
                        entries.append({"name": "brief", "cmd": c, "run": True})
                        running.add(c)
            # review #20: the step's DoD check commands (plan-meta dod[] entries named in the brief's dod[])
            # run too, so the verifier's own forge-check run records every criterion it must grade.
            wanted = {d for d in bm.get("dod", []) or [] if isinstance(d, str)}
            pm = gates.plan_meta(paths, task_id) or {}
            for d in pm.get("dod", []) or []:
                if not isinstance(d, dict) or d.get("id") not in wanted:
                    continue
                c = d.get("check")
                if isinstance(c, str) and c and c != "external" and c not in running:
                    entries.append({"name": f"dod:{d['id']}", "cmd": c, "run": True})
                    running.add(c)
    return entries


def record_is_passing(record: Any) -> bool:
    """True when a check record proves something passed: `ok` is true AND at least one non-skipped
    result exited 0. An empty record (verify[] empty, no brief checks) is `ok: true` by the §2.7
    definition but proves nothing; a T `--one-line` close must not accept it (review #59)."""
    if not isinstance(record, dict) or record.get("ok") is not True:
        return False
    for res in record.get("results", []) or []:
        if isinstance(res, dict) and res.get("status") != "skipped" and res.get("exit") == 0:
            return True
    return False


def validate_ids(task_id: str, step: str, agent_id: str) -> None:
    """Refuse ids that are not safe path components (review #31): a `..` or `/` in <step> or --agent
    would write the record outside checks/. Raises ForgeError(EXIT_USAGE)."""
    if not gates.valid_task_id(task_id):
        raise common.ForgeError(f"forge-check: task id {task_id!r} must match ^T-[0-9]{{4,}}$", common.EXIT_USAGE)
    if not gates.valid_component(step):
        raise common.ForgeError(f"forge-check: step {step!r} must match ^[A-Za-z0-9_.-]{{1,64}}$ (no '..')", common.EXIT_USAGE)
    if not gates.valid_component(agent_id):
        raise common.ForgeError(f"forge-check: agent id {agent_id!r} must match ^[A-Za-z0-9_.-]{{1,64}}$ (no '..')",
                                common.EXIT_USAGE)
    if agent_id == "human":
        raise common.ForgeError("forge-check: --agent human is reserved for forge-status attest", common.EXIT_USAGE)


# --------------------------------------------------------------------------- #
# Execution and record
# --------------------------------------------------------------------------- #
def _tail(text: str, n: int = TAIL_LINES) -> str:
    lines = text.rstrip("\n").splitlines()
    return "\n".join(lines[-n:])


def _say(line: str) -> None:
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def record_path(paths: common.Paths, task_id: str, step: str, ts: int, agent_id: str) -> str:
    return os.path.join(paths.checks_dir(task_id), f"{step}-{ts}-{agent_id}.json")


def run_checks(paths: common.Paths, task_id: str, step: str, expect_fail: bool = False, ratchet: bool = False,
               only: Optional[str] = None, only_paths: Optional[List[str]] = None,
               agent_id: str = "unknown", cmd: Optional[str] = None) -> Dict[str, Any]:
    """Run the step's commands, print FORGE_CHECK lines, write and return the record (§2.7).

    `cmd` runs that one command instead of the planned list (`forge-check --cmd`, review #20): a
    verifier or builder records a DoD command directly; it still runs from the repo root under the
    20-minute cap. `ok` = every non-skipped result exited 0 (regardless of expect_fail). The written
    file is reported in the returned dict under `_file` (repo-relative; not part of the on-disk record)."""
    validate_ids(task_id, step, agent_id)
    binding = common.load_binding(paths)
    if not os.path.isdir(paths.task(task_id)):
        raise common.ForgeError(f"{task_id}: no task directory {paths.rel(paths.task(task_id))}", common.EXIT_USAGE)
    if cmd is not None:
        if not str(cmd).strip():
            raise common.ForgeError("forge-check: --cmd needs a non-empty command", common.EXIT_USAGE)
        entries = [{"name": "cmd", "cmd": str(cmd), "run": True}]
    else:
        entries = plan_commands(paths, binding, task_id, step, only=only, only_paths=only_paths)
    results: List[Dict[str, Any]] = []
    n_pass = n_fail = n_skip = 0
    for e in entries:
        if not e["run"]:
            n_skip += 1
            results.append({"name": e["name"], "cmd": e["cmd"], "status": "skipped", "why": e["why"]})
            _say(f"FORGE_CHECK name={e['name']} exit=skipped dur=0.0s cmd={e['cmd']} why={e['why']}")
            continue
        t0 = time.monotonic()
        code, out = common.run(e["cmd"], cwd=paths.root, timeout=CHECK_TIMEOUT_S)
        dur = round(time.monotonic() - t0, 1)
        if code == 0:
            n_pass += 1
        else:
            n_fail += 1
        # review #34: tails are committed at close, so credential-shaped text is masked at write time
        results.append({"name": e["name"], "cmd": e["cmd"], "exit": code, "dur_s": dur, "tail": common.redact(_tail(out))})
        _say(f"FORGE_CHECK name={e['name']} exit={code} dur={dur}s cmd={e['cmd']}")
    rat = None
    if ratchet:
        may_edit = False
        if step not in ("main", "plan"):
            may_edit = (gates.brief_meta(paths, task_id, step) or {}).get("may_edit_tests") is True
        rat = ratchet_check(paths, binding, task_id, step, may_edit_tests=may_edit)
        _say(f"FORGE_CHECK_RATCHET status={rat['status']} baseline_tests={rat['baseline_tests']} "
             f"now_tests={rat['now_tests']} deleted={','.join(rat['deleted_test_files']) or '-'}")
    _say(f"FORGE_CHECK_SUMMARY pass={n_pass} fail={n_fail} skipped={n_skip}")
    if n_pass + n_fail == 0:
        common.eprint(f"forge-check: WARN no command ran for {task_id} {step} (verify[] empty or nothing matched): "
                      "this record proves nothing and is not a passing record; run forge-check --cmd '<command>'")

    ts = common.now_ts()
    # One record per second per agent: bump the epoch rather than overwrite a sibling record.
    while os.path.exists(record_path(paths, task_id, step, ts, agent_id)):
        ts += 1
    record: Dict[str, Any] = {"ts": ts, "agent_id": agent_id, "session_id": common.session_id(paths),
                              "task": task_id, "step": step, "expect_fail": bool(expect_fail),
                              "results": results, "ratchet": rat, "ok": n_fail == 0}
    path = record_path(paths, task_id, step, ts, agent_id)
    common.write_json_atomic(path, record)
    _say(f"FORGE_CHECK_RECORD {paths.rel(path)}")
    record["_file"] = paths.rel(path)
    return record
