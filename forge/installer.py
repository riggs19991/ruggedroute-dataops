#!/usr/bin/env python3
"""installer.py — install or upgrade the Forge into a repository (design §10.1 steps 1-7, §10.3, §8.2; MODULE-API §8).

Usage:
  python3 forge/installer.py [--target DIR] [--source PAYLOAD] [--upgrade] [--force] [--dry-run]
                             [--effort low|medium] [--no-model] [--with-bench] [--binding FILE] [--project NAME]

Ownership is the upgrade contract (design §8.2):
  * Forge-owned files (everything shipped in the payload) are copied and listed with their sha256 in
    .forge/install-manifest.json. A Forge-owned file whose local sha differs from the manifest is refused unless
    --force (or, with --upgrade, overwritten after a backup to .forge/incidents/upgrade-<ts>/).
  * Project-owned files (binding.json, STATUS.json, ledgers, CHANGELOG, lessons, decisions) are written only when absent.
  * .claude/settings.json is merged: scalars set only when absent (unless --force), arrays unioned, Forge hook
    handlers (command containing /.forge/bin/forge-hook) replaced per event, every other hook handler kept.
  * CLAUDE.md gets the fragment between <!-- forge:begin --> and <!-- forge:end --> (inserted or replaced).
Idempotent: a second run reports "no changes". Python 3.9+, standard library only.
Exit codes: 0 ok · 1 a migration failed · 2 usage · 3 refused (conflict, wrong target, version mismatch).
"""
import argparse
import copy
import datetime
import glob
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SOURCE = os.path.join(HERE, "payload")
MIGRATIONS_DIR = os.path.join(HERE, "migrations")

EXIT_OK, EXIT_FAILED, EXIT_USAGE, EXIT_REFUSED = 0, 1, 2, 3
BEGIN_MARK = "<!-- forge:begin"
END_MARK = "<!-- forge:end -->"
GITIGNORE_LINES = (".forge/.runtime/", ".forge/incidents/", ".forge/**/__pycache__/")
FORGE_HOOK = "/.forge/bin/forge-hook"
# Paths under .forge/ that are project-owned even if a payload ever ships them (design §8.2).
PROJECT_OWNED = (".forge/binding.json", ".forge/STATUS.json", ".forge/ledger.jsonl", ".forge/history.jsonl",
                 ".forge/queue.jsonl", ".forge/CHANGELOG.md", ".forge/COST-REPORT.md", ".forge/install-manifest.json")
PROJECT_OWNED_DIRS = (".forge/lessons/", ".forge/decisions/", ".forge/tasks/", ".forge/archive/",
                      ".forge/incidents/", ".forge/.runtime/", ".claude/agent-memory/")
OPTIONAL_BIN = {".forge/bin/forge-bench": "--with-bench"}   # design §11 / §13.3: forge-bench is an add-on
STACKS = ("python", "kotlin-android", "web-ts", "unknown")
TRUST_CAVEAT = ("Note: project permissions.allow rules apply only after the workspace trust dialog is accepted; an "
                "untrusted session prompts once per script call until then. Hooks run regardless.")


class InstallError(Exception):
    """A refusal or failure: printed on stderr as one line; the process exits with .code."""

    def __init__(self, message: str, code: int = EXIT_REFUSED):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bytes(path: str) -> Optional[bytes]:
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None


def read_text(path: str) -> Optional[str]:
    data = read_bytes(path)
    return data.decode("utf-8") if data is not None else None


def dumps(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def load_json_file(path: str, what: str) -> Any:
    text = read_text(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise InstallError(f"{what} ({path}) is not valid JSON: {e}")


def load_module(name: str, path: str) -> Any:
    """Import a payload script (no .py suffix) as a module."""
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def render(text: str, mapping: Dict[str, str]) -> str:
    """Replace {{key}} placeholders (same syntax as forgelib.common.render_template)."""
    return re.sub(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}", lambda m: mapping.get(m.group(1), m.group(0)), text)


# --------------------------------------------------------------------------- #
# The change set: every write goes through put(), which makes dry-run and idempotency trivial
# --------------------------------------------------------------------------- #
class Installer:
    """Computes and (unless dry-run) applies every change; counts them for the summary."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.target = os.path.abspath(args.target)
        self.source = os.path.abspath(args.source)
        self.dry = args.dry_run
        self.changes = 0
        self.warnings: List[str] = []
        self.version = (read_text(os.path.join(self.source, ".forge", "VERSION")) or "").strip()
        self.stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # ---- output and writes ------------------------------------------------ #
    def log(self, verb: str, rel: str, detail: str = "") -> None:
        prefix = "[dry-run] " if self.dry else ""
        print(f"  {prefix}{verb:<8} {rel}{('  ' + detail) if detail else ''}")

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        print(f"  WARN     {message}")

    def abs(self, rel: str) -> str:
        return os.path.join(self.target, rel)

    def put(self, rel: str, data: bytes, mode: Optional[int] = None, verb: Optional[str] = None) -> bool:
        """Write `data` to `rel` when it differs (or the mode differs); returns True when something changed."""
        path = self.abs(rel)
        cur = read_bytes(path)
        mode_ok = mode is None or (cur is not None and (os.stat(path).st_mode & 0o777) == mode)
        if cur == data and mode_ok:
            return False
        self.changes += 1
        self.log(verb or ("new" if cur is None else ("chmod" if cur == data else "update")), rel)
        if not self.dry:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if cur != data:
                tmp = f"{path}.forge-tmp"
                with open(tmp, "wb") as f:
                    f.write(data)
                os.replace(tmp, path)
            if mode is not None:
                os.chmod(path, mode)
        return True

    def put_text(self, rel: str, text: str, verb: Optional[str] = None) -> bool:
        return self.put(rel, text.encode("utf-8"), verb=verb)

    def seed(self, rel: str, text: str) -> None:
        """Project-owned file: written only when absent (design §8.2)."""
        if os.path.exists(self.abs(rel)):
            return
        self.put_text(rel, text, verb="new")

    def remove(self, rel: str) -> None:
        self.changes += 1
        self.log("remove", rel)
        if not self.dry:
            os.unlink(self.abs(rel))

    # ---- step 0: preconditions -------------------------------------------- #
    def preconditions(self) -> Optional[str]:
        """Validate source and target; returns the installed version (None on a fresh install)."""
        if not self.version:
            raise InstallError(f"--source {self.source} is not a Forge payload (no .forge/VERSION)", EXIT_USAGE)
        if not os.path.isdir(self.target):
            raise InstallError(f"--target {self.target} is not a directory", EXIT_USAGE)
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=self.target, capture_output=True, text=True)
        if r.returncode != 0:
            raise InstallError(f"{self.target} is not a git repository (git init first)")
        if os.path.realpath(r.stdout.strip()) != os.path.realpath(self.target):
            raise InstallError(f"--target must be the repository root ({r.stdout.strip()}), not a subdirectory")
        installed = (read_text(self.abs(".forge/VERSION")) or "").strip() or None
        if installed and installed != self.version and not self.args.upgrade:
            raise InstallError(f"Forge {installed} is installed and the payload is {self.version}: re-run with --upgrade")
        if self.args.upgrade and not installed:
            self.warn("--upgrade given but no .forge/VERSION exists: performing a fresh install")
        return installed

    # ---- step 2: Forge-owned files ---------------------------------------- #
    def payload_files(self, stack: str) -> List[Tuple[str, str]]:
        """(source path, target rel) of every Forge-owned payload file to install."""
        out: List[Tuple[str, str]] = []
        for top in (".forge", ".claude"):
            base = os.path.join(self.source, top)
            for dirpath, dirnames, filenames in os.walk(base):
                dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
                for name in sorted(filenames):
                    if name.endswith((".pyc", ".pyo")) or name == ".DS_Store":
                        continue
                    src = os.path.join(dirpath, name)
                    rel = os.path.relpath(src, self.source).replace(os.sep, "/")
                    rel = self.map_rule(rel, stack)
                    if rel is None or rel in PROJECT_OWNED or rel.startswith(PROJECT_OWNED_DIRS):
                        continue
                    if rel in OPTIONAL_BIN and not self.args.with_bench:
                        continue
                    out.append((src, rel))
        return out

    @staticmethod
    def map_rule(rel: str, stack: str) -> Optional[str]:
        """Stack rule packs: only the binding's stack is installed, flat under .claude/rules/ (design §8.2, §13.9)."""
        m = re.match(r"^\.claude/rules/(?:stacks/)?forge-stack-([\w-]+)\.md$", rel)
        if not m:
            return rel
        return f".claude/rules/forge-stack-{m.group(1)}.md" if m.group(1) == stack else None

    def plan_forge_owned(self, stack: str, old_manifest: Dict[str, str]) -> List[Tuple[str, bytes, Optional[str]]]:
        """design §10.1 step 2, first half: [(rel, data, how)] where how is None, "force" or "backup".
        Refuses (before anything is written) when a Forge-owned file was modified locally."""
        plan = []
        conflicts = []
        for src, rel in self.payload_files(stack):
            data = read_bytes(src) or b""
            want = sha256_bytes(data)
            cur = read_bytes(self.abs(rel))
            cur_sha = sha256_bytes(cur) if cur is not None else None
            old = old_manifest.get(rel)
            if cur_sha is None or cur_sha == want or (old is not None and cur_sha == old):
                plan.append((rel, data, None))
            elif self.args.force:
                plan.append((rel, data, "force"))
            elif self.args.upgrade and old is not None:
                plan.append((rel, data, "backup"))
            else:
                conflicts.append(rel)
        if conflicts:
            raise InstallError(f"{len(conflicts)} Forge-owned file(s) differ locally from the installed copy, e.g. "
                               f"{', '.join(conflicts[:3])}: re-run with --force to overwrite (or --upgrade for local "
                               f"edits to an installed Forge)")
        return plan

    def apply_forge_owned(self, plan: List[Tuple[str, bytes, Optional[str]]],
                          old_manifest: Dict[str, str]) -> Dict[str, str]:
        """design §10.1 step 2, second half: write, chmod +x .forge/bin/*, drop files no longer shipped;
        returns the new manifest {rel: sha256}."""
        manifest: Dict[str, str] = {}
        for rel, data, how in plan:
            if how == "backup" and not self.dry:
                backup = self.abs(f".forge/incidents/upgrade-{self.stamp}/{rel}")
                os.makedirs(os.path.dirname(backup), exist_ok=True)
                with open(backup, "wb") as f:
                    f.write(read_bytes(self.abs(rel)) or b"")
            if how:
                self.warn(f"{rel} was modified locally; overwritten ({'backup in .forge/incidents/upgrade-' + self.stamp if how == 'backup' else '--force'})")
            executable = rel.startswith(".forge/bin/") and rel.count("/") == 2
            mode = 0o755 if executable else None
            self.put(rel, data, mode=mode)
            manifest[rel] = sha256_bytes(data)
        for rel, old in sorted(old_manifest.items()):
            if rel in manifest or not os.path.exists(self.abs(rel)):
                continue
            if sha256_bytes(read_bytes(self.abs(rel)) or b"") == old:
                self.remove(rel)       # dropped from the payload and never edited locally
            else:
                self.warn(f"{rel} is no longer shipped but was edited locally; left in place")
        return manifest

    # ---- step 3: settings merge ------------------------------------------- #
    def merge_settings(self, binding: Dict[str, Any], forge_run: Any) -> None:
        fragment = load_json_file(os.path.join(self.source, ".claude", "settings.forge.json"), "settings fragment")
        if not isinstance(fragment, dict):
            raise InstallError("payload .claude/settings.forge.json is missing", EXIT_USAGE)
        fragment = copy.deepcopy(fragment)
        if self.args.no_model:
            fragment.pop("model", None)
        effort = self.args.effort or (binding.get("routing") or {}).get("architect_effort") or "medium"
        fragment["effortLevel"] = effort
        fragment.setdefault("permissions", {}).setdefault("allow", [])
        fragment["permissions"]["allow"] = fragment["permissions"]["allow"] + forge_run.permission_rules(binding)
        local = load_json_file(self.abs(".claude/settings.json"), ".claude/settings.json")
        local = local if isinstance(local, dict) else {}
        merged = merge_settings(local, fragment, self.args.force)
        if self.args.effort:
            merged["effortLevel"] = self.args.effort   # an explicit --effort is the operator's choice
        self.put_text(".claude/settings.json", dumps(merged), verb="merge" if local else "new")

    # ---- step 4: CLAUDE.md fragment ----------------------------------------- #
    def claude_md(self) -> None:
        tmpl = read_text(os.path.join(self.source, ".forge", "templates", "CLAUDE.fragment.md"))
        if tmpl is None:
            self.warn("payload templates/CLAUDE.fragment.md missing; using the built-in fragment (design §13.6)")
            tmpl = BUILTIN_CLAUDE_FRAGMENT
        frag = render(tmpl, {"version": self.version}).strip() + "\n"
        cur = read_text(self.abs("CLAUDE.md")) or ""
        pattern = re.compile(re.escape(BEGIN_MARK) + r".*?" + re.escape(END_MARK) + r"\n?", re.DOTALL)
        if pattern.search(cur):
            new = pattern.sub(lambda _m: frag, cur, count=1)
        else:
            new = (cur.rstrip("\n") + "\n\n" if cur.strip() else "") + frag
        self.put_text("CLAUDE.md", new, verb="merge" if cur else "new")

    # ---- step 5: binding --------------------------------------------------- #
    def binding(self, project: str) -> Tuple[Dict[str, Any], Optional[bytes]]:
        """(binding, bytes to write or None): the existing binding (never touched), --binding verbatim, or stack
        detection (design §10.1 step 5). Nothing is written here, so a later refusal leaves the target untouched."""
        rel = ".forge/binding.json"
        existing = load_json_file(self.abs(rel), rel)
        if isinstance(existing, dict):
            if self.args.binding:
                self.warn(f"{rel} exists (project-owned): --binding ignored")
            return existing, None
        if self.args.binding:
            data = read_bytes(self.args.binding)
            if data is None:
                raise InstallError(f"--binding {self.args.binding} does not exist", EXIT_USAGE)
            try:
                binding = json.loads(data.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                raise InstallError(f"--binding {self.args.binding} is not valid JSON: {e}", EXIT_USAGE)
            if not isinstance(binding, dict):
                raise InstallError(f"--binding {self.args.binding} is not a JSON object", EXIT_USAGE)
            return binding, data
        binding = detect_binding(self.target, self.source, project, self.version, self.args.effort)
        self.log("detect", rel, f"stack {binding['stack']}, {len(binding['verify'])} verify entries")
        return binding, dumps(binding).encode("utf-8")

    # ---- step 6: project-owned state ---------------------------------------- #
    def state(self, project: str, stack: str) -> None:
        if not os.path.exists(self.abs(".forge/STATUS.json")):
            status = idle_status(self.source, project, self.warn)
            if stack == "unknown":
                status["queue"] = [{"id": "T-0001", "title": "stack discovery: fill binding.verify[] with the project's "
                                    "real test commands", "class_hint": "S"}]
            self.put_text(".forge/STATUS.json", dumps(status), verb="new")
        for rel in (".forge/ledger.jsonl", ".forge/history.jsonl", ".forge/queue.jsonl"):
            self.seed(rel, "")
        self.seed(".forge/CHANGELOG.md", "# Changelog\n\nOne line per closed Forge task, appended by "
                                         "`.forge/bin/forge-status close`.\n\n")
        self.seed(".forge/lessons/INDEX.md", "# Lessons index\n\nOne line per lesson: `- [<slug>](<slug>.md) — "
                                             "<one-line summary>`. At most 200 lines; the first 40 are injected at "
                                             "session start.\n")
        today = datetime.date.today().isoformat()
        self.seed(".forge/decisions/0001-adopt-forge.md", ADR_0001.format(date=today, version=self.version, stack=stack))
        self.seed(".claude/agent-memory/forge-verifier/MEMORY.md",
                  "# forge-verifier calibration notes\n\nAt most 60 lines; facts about this repo's checks, not instructions.\n")
        gi_rel = ".gitignore"
        cur = read_text(self.abs(gi_rel)) or ""
        lines = [l.strip() for l in cur.splitlines()]
        missing = [l for l in GITIGNORE_LINES if l not in lines]
        if missing:
            new = (cur if cur.endswith("\n") or not cur else cur + "\n") + "# The Forge (runtime markers, incident dumps)\n" \
                  + "".join(l + "\n" for l in missing)
            self.put_text(gi_rel, new, verb="update" if cur else "new")

    # ---- migrations (design §10.3) ------------------------------------------ #
    def migrations(self, applied: List[str], installed: Optional[str]) -> List[str]:
        """Run migrations/NNNN-*.sh|.py not yet applied (upgrade only); a fresh install marks them all applied."""
        names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(MIGRATIONS_DIR, "[0-9][0-9][0-9][0-9]-*"))
                       if p.endswith((".sh", ".py")))
        if not installed:
            return names
        done = list(applied)
        for name in names:
            if name in done:
                continue
            self.changes += 1
            self.log("migrate", name)
            if not self.dry:
                interp = ["bash"] if name.endswith(".sh") else [sys.executable]
                env = dict(os.environ, FORGE_TARGET=self.target, FORGE_FROM_VERSION=installed, FORGE_TO_VERSION=self.version)
                r = subprocess.run(interp + [os.path.join(MIGRATIONS_DIR, name)], cwd=self.target, env=env)
                if r.returncode != 0:
                    raise InstallError(f"migration {name} exited {r.returncode}; nothing after it ran", EXIT_FAILED)
            done.append(name)
            if not self.dry:
                self.record_migrations(done)
        return done

    def record_migrations(self, done: List[str]) -> None:
        """Persist the applied list right away, so a later failure never re-runs a migration that succeeded."""
        path = self.abs(".forge/install-manifest.json")
        manifest = load_json_file(path, "install-manifest.json")
        if isinstance(manifest, dict):
            manifest["migrations"] = list(done)
            with open(path, "w", encoding="utf-8") as f:
                f.write(dumps(manifest))

    # ---- step 7: doctor ---------------------------------------------------- #
    def doctor(self) -> None:
        doctor = self.abs(".forge/bin/forge-doctor")
        if self.dry or not os.access(doctor, os.X_OK):
            return
        print("\nforge-doctor --report --no-probes:")
        env = dict(os.environ, FORGE_ROOT=self.target, PYTHONDONTWRITEBYTECODE="1")
        subprocess.run([doctor, "--report", "--no-probes"], cwd=self.target, env=env)

    # ---- orchestration ----------------------------------------------------- #
    def run(self) -> int:
        installed = self.preconditions()
        print(f"forge installer: {'upgrade ' + installed + ' -> ' if installed and installed != self.version else ''}"
              f"Forge {self.version} into {self.target}{' (dry run)' if self.dry else ''}")
        old = load_json_file(self.abs(".forge/install-manifest.json"), "install-manifest.json")
        old = old if isinstance(old, dict) else {}
        project = self.args.project or os.path.basename(self.target.rstrip(os.sep))
        old_files = old.get("files") if isinstance(old.get("files"), dict) else {}
        binding, binding_data = self.binding(project)
        stack = binding.get("stack") if binding.get("stack") in STACKS else "unknown"
        plan = self.plan_forge_owned(stack, old_files)          # refuses before any write
        applied = self.migrations(list(old.get("migrations") or []), installed)
        if binding_data is not None:
            self.put(".forge/binding.json", binding_data, verb="new")
        manifest_files = self.apply_forge_owned(plan, old_files)
        forge_run = load_module("forge_run", os.path.join(self.source, ".forge", "bin", "forge-run"))
        self.merge_settings(binding, forge_run)
        self.claude_md()
        self.state(binding.get("project") or project, stack)
        manifest = {"schema": "forge/manifest/1", "forge_version": self.version,
                    "files": dict(sorted(manifest_files.items())), "migrations": applied}
        self.put_text(".forge/install-manifest.json", dumps(manifest))
        if self.changes:
            print(f"forge installer: {self.changes} change(s){' would be made' if self.dry else ''}"
                  f"{', ' + str(len(self.warnings)) + ' warning(s)' if self.warnings else ''}")
        else:
            print("forge installer: no changes (already up to date)")
        self.doctor()
        if not self.dry and self.changes:
            print("\n" + TRUST_CAVEAT)
            print("Commit these files, then open Claude Code and run `/forge-task <first task>`.")
            print("Optional: .forge/bin/forge-doctor --probe-hooks (one cheap claude -p call) proves the hooks fire.")
        return EXIT_OK


# --------------------------------------------------------------------------- #
# Settings merge (design §8.2, §13.4)
# --------------------------------------------------------------------------- #
def is_forge_handler(handler: Any) -> bool:
    return isinstance(handler, dict) and FORGE_HOOK in str(handler.get("command") or "")


def merge_value(cur: Any, want: Any, force: bool) -> Any:
    """Objects merge per key; arrays union (local order first); scalars keep the local value unless --force."""
    if isinstance(cur, dict) and isinstance(want, dict):
        out = copy.deepcopy(cur)
        for k, v in want.items():
            out[k] = merge_value(cur[k], v, force) if k in cur else copy.deepcopy(v)
        return out
    if isinstance(cur, list) and isinstance(want, list):
        out = copy.deepcopy(cur)
        for item in want:
            if item not in out:
                out.append(copy.deepcopy(item))
        return out
    return copy.deepcopy(want) if force else cur


def merge_hooks(local: Dict[str, Any], fragment: Dict[str, Any]) -> Dict[str, Any]:
    """Drop every Forge handler from the local hooks (per event), keep the rest, append the fragment's groups."""
    out: Dict[str, Any] = {}
    for event, groups in (local or {}).items():
        kept = []
        for group in groups if isinstance(groups, list) else []:
            if not isinstance(group, dict):
                kept.append(group)
                continue
            handlers = [h for h in group.get("hooks") or [] if not is_forge_handler(h)]
            if handlers:
                g = copy.deepcopy(group)
                g["hooks"] = handlers
                kept.append(g)
        if kept:
            out[event] = kept
    for event, groups in fragment.items():
        out.setdefault(event, []).extend(copy.deepcopy(groups))
    return out


def merge_settings(local: Dict[str, Any], fragment: Dict[str, Any], force: bool) -> Dict[str, Any]:
    out = copy.deepcopy(local)
    for key, want in fragment.items():
        if key == "hooks":
            hooks = local.get("hooks")
            out["hooks"] = merge_hooks(hooks if isinstance(hooks, dict) else {}, want)
        elif key in local:
            out[key] = merge_value(local[key], want, force)
        else:
            out[key] = copy.deepcopy(want)
    return out


# --------------------------------------------------------------------------- #
# Stack detection (design §10.1 step 5, §5.2, §10.4)
# --------------------------------------------------------------------------- #
def _exists(target: str, *rels: str) -> bool:
    return any(os.path.exists(os.path.join(target, r)) for r in rels)


def _package_json(path: str) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(read_text(path) or "")
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _npm_entry(name: str, cmd: str, when: str, pkg: Dict[str, Any], where: str) -> Dict[str, Any]:
    """`npm test` only when scripts.test exists; otherwise the same entry marked todo (design §5.2, §16 #18)."""
    entry = {"name": name, "cmd": cmd, "when": when}
    if not (isinstance(pkg.get("scripts"), dict) and pkg["scripts"].get("test")):
        entry["todo"] = f"{where} has no scripts.test; replace with a real test command when one exists"
    return entry


def _python_verify(target: str) -> Tuple[List[Dict[str, Any]], List[str], Optional[str]]:
    verify: List[Dict[str, Any]] = []
    globs: List[str] = []
    if glob.glob(os.path.join(target, "lib", "*.py")):
        verify.append({"name": "lib-unit", "cmd": "cd lib && python3 -m unittest -v", "when": "always"})
        globs.append("lib/test_*.py")
    if os.path.isdir(os.path.join(target, "layers")):
        verify.append({"name": "layer-tests", "cmd": "pytest layers/{layer}/tests -q", "when": "paths:layers/{layer}/**",
                       "exists": "layers/{layer}/tests", "vars": {"layer": "from-path"}})
        globs.append("layers/*/tests/*.py")
    cfg_text = "".join(read_text(p) or "" for p in
                       [os.path.join(target, n) for n in ("pyproject.toml", "setup.cfg", "tox.ini", "pytest.ini")]
                       + glob.glob(os.path.join(target, "requirements*.txt")))
    uses_pytest = "pytest" in cfg_text or _exists(target, "conftest.py", "tests/conftest.py", "pytest.ini")
    if not verify:
        verify.append({"name": "unit", "cmd": "python3 -m pytest -q" if uses_pytest else "python3 -m unittest discover -v",
                       "when": "always"})
    globs += ["tests/**/test_*.py", "**/test_*.py"]
    if _exists(target, "requirements.txt"):
        bootstrap: Optional[str] = "python3 -m pip install -q -r requirements.txt"
    elif _exists(target, "pyproject.toml", "setup.py"):
        bootstrap = "python3 -m pip install -q -e ."
    elif any("pytest" in v["cmd"] for v in verify):
        bootstrap = "python3 -m pip install -q pytest"
    else:
        bootstrap = None
    return verify, globs, bootstrap


def detect_stack(target: str) -> str:
    """python (pyproject/setup/requirements/lib/*.py) > web-ts (root package.json) > kotlin-android (gradle) > unknown."""
    if _exists(target, "pyproject.toml", "setup.py") or glob.glob(os.path.join(target, "requirements*.txt")) \
            or glob.glob(os.path.join(target, "lib", "*.py")):
        return "python"
    if _exists(target, "package.json"):
        return "web-ts"
    if _exists(target, "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts", "gradlew"):
        return "kotlin-android"
    return "unknown"


def detect_binding(target: str, source: str, project: str, version: str, effort: Optional[str]) -> Dict[str, Any]:
    """A first binding.json from the payload template plus what the tree shows. Seeds carry TODO notes."""
    tmpl = read_text(os.path.join(source, ".forge", "templates", "binding.json"))
    binding = json.loads(render(tmpl, {"project": project, "version": version})) if tmpl else copy.deepcopy(BUILTIN_BINDING)
    binding["project"] = project
    binding["forge_pin"] = version
    stack = detect_stack(target)
    binding["stack"] = stack
    notes = [n for n in binding.get("notes") or [] if isinstance(n, str)]
    irreversible = list(binding.get("irreversible_commands") or [])
    if stack == "python":
        verify, globs, bootstrap = _python_verify(target)
        binding.update(verify=verify, test_globs=globs, bootstrap=bootstrap, test_pattern="^\\s*def test_")
    elif stack == "web-ts":
        pkg = _package_json(os.path.join(target, "package.json")) or {}
        binding.update(verify=[_npm_entry("npm-test", "npm test", "always", pkg, "package.json")],
                       bootstrap="npm ci" if _exists(target, "package-lock.json") else "npm install",
                       test_globs=["**/*.test.ts", "**/*.test.js", "**/*.spec.ts", "**/*.spec.js"],
                       test_pattern="^\\s*(it|test)\\(")
    elif stack == "kotlin-android":
        app = _exists(target, "app/build.gradle", "app/build.gradle.kts")
        binding.update(verify=[{"name": "unit", "cmd": "./gradlew :app:testDebugUnitTest" if app else "./gradlew test",
                                "when": "always"}],
                       bootstrap=None, test_globs=["app/src/test/**/*.kt", "**/src/test/**/*.kt"], test_pattern="^\\s*@Test")
        irreversible += ["./gradlew publish*", "./gradlew bundleRelease", "fastlane *"]
    else:
        binding.update(verify=[], bootstrap=None, test_globs=[])
        notes.insert(0, "TODO: stack unknown: the first queued task (T-0001 stack discovery) fills verify[].")
    if stack != "web-ts":   # a JS sub-project next to a python/kotlin root (e.g. worker-tiles/) gets its own entry
        for pj in sorted(glob.glob(os.path.join(target, "*", "package.json"))):
            sub = os.path.basename(os.path.dirname(pj))
            if sub == "node_modules":
                continue
            binding["verify"].append(_npm_entry(f"{sub}-test", f"cd {sub} && npm test", f"paths:{sub}/**",
                                                _package_json(pj) or {}, f"{sub}/package.json"))
            binding["test_globs"] += [f"{sub}/**/*.test.js", f"{sub}/**/*.test.ts"]
    protected = []
    if os.path.isdir(os.path.join(target, ".github", "workflows")):
        protected.append(".github/workflows/*.yml")
    wrangler = [os.path.relpath(p, target) for p in glob.glob(os.path.join(target, "**", "wrangler.toml"), recursive=True)
                if "node_modules" not in p]
    if wrangler:
        protected += sorted(p.replace(os.sep, "/") for p in wrangler)
        irreversible += ["wrangler *", "npx wrangler *"]
    if _exists(target, "app/google-services.json"):
        protected.append("app/google-services.json")
    binding["protected_paths"] = protected
    binding["mechanic_denied_paths"] = list(protected)
    binding["irreversible_commands"] = list(dict.fromkeys(irreversible))
    if effort:
        binding.setdefault("routing", {})["architect_effort"] = effort
    notes.append(f"Installer-detected stack: {stack}; review verify[], protected_paths, risk_paths, important_paths "
                 f"and mechanic_denied_paths (seeded, TODO).")
    binding["notes"] = notes
    return binding


def idle_status(source: str, project: str, warn: Any) -> Dict[str, Any]:
    """forgelib.status.idle_status from the payload; an inline MODULE-API §2.1 idle STATUS if that import fails."""
    bin_dir = os.path.join(source, ".forge", "bin")
    sys.path.insert(0, bin_dir)
    try:
        from forgelib.status import idle_status as _idle   # noqa: WPS433 — imported from the payload being installed
        return _idle(project)
    except Exception as e:  # noqa: BLE001 — any import failure falls back, loudly
        warn(f"cannot import forgelib.status.idle_status ({type(e).__name__}: {e}); writing a minimal idle STATUS")
        now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        version = (read_text(os.path.join(source, ".forge", "VERSION")) or "").strip()
        return {"schema_version": 2, "forge_version": version, "project": project,
                "updated_at": now.isoformat().replace("+00:00", "Z"), "updated_ts": int(now.timestamp()),
                "updated_by": {"session_id": "installer", "cmd": "installer.py"}, "context_state": "fresh",
                "task": None, "queue": [], "history": []}
    finally:
        sys.path.remove(bin_dir)


# --------------------------------------------------------------------------- #
# Built-in fallbacks (used only when the payload templates are missing)
# --------------------------------------------------------------------------- #
BUILTIN_CLAUDE_FRAGMENT = """<!-- forge:begin (managed by .forge/bin — do not edit between markers) -->
## The Forge
This repo runs the Forge (v{{version}}). `.forge/STATUS.json` is the single source of truth for where work stands; it is injected at every session start and written only by `.forge/bin/forge-status`.
Daily loop: `/forge-task <title>` → `/forge-next` → `/forge-close`. Health: `/forge-doctor`. Everything else: read `.forge/FORGE.md` (≤120 lines) before guessing. Scripts live at `.forge/bin/` and run from the repository root.
Hooks enforce plan-first, scope fences, tool budgets, evidence-backed handoffs, the status write and the policy-file lock; if a tool call is refused, the reason names the script to run.
When compacting, preserve: decisions and why; approaches tried and set aside; exactly where things stand; anything open or promised; exact commands, paths and numbers.
<!-- forge:end -->
"""

BUILTIN_BINDING: Dict[str, Any] = {
    "schema_version": 2, "forge_pin": "", "project": "", "stack": "unknown", "bootstrap": None, "verify": [],
    "smoke": None, "format": None, "test_globs": [], "test_pattern": "^\\s*def test_",
    "protected_paths": [], "risk_paths": ["**/*secret*", "**/.env*"], "important_paths": [], "mechanic_denied_paths": [],
    "risk_words": [{"word": "secret"}, {"word": "license"}, {"word": "attribution"}, {"word": "delete"}],
    "irreversible_commands": ["git push *", "gh workflow run *", "gh pr merge *"],
    "git": {"branch_per_task": False, "commit_prefix": "forge", "worktree_isolation": False},
    "budgets": {"T": 1, "S": 3, "M": 10, "M_chain": 12, "W": 25, "L_unit": 2, "X": 30, "risk_multiplier": 1.5},
    "routing": {"architect_effort": "medium", "m_builder": "opus-medium", "overrides": [], "measured": {}},
    "clear_policy": "phase", "auto_resume": True, "driver": {"max_turns": 120, "max_phases": 12},
    "notes": ["TODO: one note per design rule a worker must not violate (copied from the README)."],
}

ADR_0001 = """# 1. Adopt the Forge

Date: {date}

## Status

Accepted

## Context

Work in this repository is done with Claude Code sessions whose context is lost between sessions. We want every
non-trivial change to start from a written plan, to be routed to a model and effort that fit its size and risk, to be
verified by a fresh context against stated criteria, and to leave a status file that the next session can resume from.

## Decision

Install the Forge v{version} in plain project layout (`.forge/`, `.claude/agents/forge-*`, `.claude/skills/forge-*`,
hooks in `.claude/settings.json`). `.forge/STATUS.json` is the single source of truth and is written only by
`.forge/bin/forge-status`. The installer detected the stack as `{stack}` and seeded `.forge/binding.json`, which is
project-owned and reviewed by hand.

## Consequences

Hooks refuse source edits without an open task, workers without evidence-backed handoffs, and turns that end without
recording state. Forge-owned files are replaced on upgrade; project-owned files (binding, STATUS, ledger, lessons,
decisions) are never overwritten. Costs are recorded in `.forge/ledger.jsonl` as measured only in driver/bench mode.
"""


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="installer.py", description=__doc__.splitlines()[0])
    p.add_argument("--target", default=".", help="repository root to install into (default: current directory)")
    p.add_argument("--source", default=DEFAULT_SOURCE, help="payload directory (default: the payload next to this script)")
    p.add_argument("--upgrade", action="store_true", help="upgrade an installed Forge (runs migrations; backs up local edits)")
    p.add_argument("--force", action="store_true", help="overwrite locally modified Forge-owned files and settings scalars")
    p.add_argument("--dry-run", action="store_true", help="print every change; write nothing")
    p.add_argument("--effort", choices=("low", "medium"), default=None, help="effortLevel (default binding.routing.architect_effort)")
    p.add_argument("--no-model", action="store_true", help="do not set model: fable in settings.json")
    p.add_argument("--with-bench", action="store_true", help="also install .forge/bin/forge-bench")
    p.add_argument("--binding", default=None, help="prepared binding.json, installed verbatim when none exists")
    p.add_argument("--project", default=None, help="project name for a new binding/STATUS (default: target dir name)")
    args = p.parse_args(argv)
    sys.dont_write_bytecode = True   # imports from the payload must not leave __pycache__ in it
    try:
        return Installer(args).run()
    except InstallError as e:
        print(f"installer.py: {e}", file=sys.stderr)
        return e.code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
