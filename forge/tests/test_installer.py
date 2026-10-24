"""Tests for forge/installer.py (MODULE-API §8; design §10.1 steps 1-7, §8.2 ownership and settings merge)."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # also runnable as forge/tests/test_installer.py
import helpers  # noqa: E402
from helpers import FORGE_SRC, INSTALLER, PAYLOAD, PAYLOAD_CLAUDE, common, tree_hashes

INSTALL_SH = os.path.join(FORGE_SRC, "install.sh")
MAKE_PLUGIN = os.path.join(FORGE_SRC, "tools", "make_plugin.py")
FRAGMENT = os.path.join(PAYLOAD_CLAUDE, "settings.forge.json")
EVAL_TASKS = os.path.join(FORGE_SRC, "evals", "tasks")

NON_FORGE_HOOK = {"hooks": [{"type": "command", "command": "echo my-own-stop-hook"}]}


class InstallerTestCase(unittest.TestCase):
    def setUp(self):
        self.target = tempfile.mkdtemp(prefix="forge-install-")
        self.addCleanup(shutil.rmtree, self.target, True)
        self.git("init", "-q", ".")
        self.git("config", "user.name", "Forge Test")
        self.git("config", "user.email", "forge-test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.write("lib/mod.py", "def add(a, b):\n    return a + b\n")
        self.write("lib/test_mod.py", "import unittest\nfrom mod import add\n\n\nclass T(unittest.TestCase):\n"
                                      "    def test_add(self):\n        self.assertEqual(add(1, 2), 3)\n")
        self.write("CLAUDE.md", "# My project\n\nKeep this paragraph.\n")
        self.write(".claude/settings.json", json.dumps({"effortLevel": "high", "hooks": {"Stop": [NON_FORGE_HOOK]},
                                                        "permissions": {"allow": ["Bash(make *)"]}}, indent=2))
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "fixture")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.target, capture_output=True, text=True)

    def path(self, rel):
        return os.path.join(self.target, rel)

    def write(self, rel, text):
        p = self.path(rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)

    def read(self, rel):
        with open(self.path(rel), encoding="utf-8") as f:
            return f.read()

    def read_json(self, rel):
        return json.loads(self.read(rel))

    def install(self, *args, target=None):
        env = dict(os.environ)
        env.pop("FORGE_ROOT", None)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        r = subprocess.run([sys.executable, INSTALLER, "--target", target or self.target, "--source", PAYLOAD, *args],
                           cwd=self.target, env=env, capture_output=True, text=True, timeout=300)
        return r.returncode, r.stdout, r.stderr

    def forge_status(self, *args):
        env = dict(os.environ)
        env.pop("FORGE_ROOT", None)
        env["CLAUDE_PROJECT_DIR"] = self.target
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        r = subprocess.run([self.path(".forge/bin/forge-status"), *args], cwd=self.target, env=env, capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr


class FreshInstallTests(InstallerTestCase):
    def test_fresh_install_lays_out_a_consumer_repo(self):
        code, out, err = self.install("--project", "proj")
        self.assertEqual(code, 0, err + out)
        # Forge-owned files, executable scripts
        for rel in ("forge-status", "forge-check", "forge-gate", "forge-hook", "forge-doctor", "forge-run"):
            p = self.path(f".forge/bin/{rel}")
            self.assertTrue(os.path.exists(p), rel)
            self.assertTrue(os.access(p, os.X_OK), f"{rel} must be executable")
            with open(p, encoding="utf-8") as f:
                self.assertTrue(f.readline().startswith("#!/usr/bin/env python3"), rel)
        self.assertFalse(os.path.exists(self.path(".forge/bin/forge-bench")), "forge-bench only with --with-bench")
        self.assertTrue(os.path.exists(self.path(".forge/bin/forgelib/common.py")))
        self.assertTrue(os.path.exists(self.path(".forge/schemas/status.json")))
        self.assertTrue(os.path.exists(self.path(".forge/FORGE.md")))
        self.assertTrue(os.path.exists(self.path(".claude/agents/forge-builder.md")))
        self.assertTrue(os.path.exists(self.path(".claude/skills/forge-task/SKILL.md")))
        self.assertEqual(self.read(".forge/VERSION").strip(), helpers.common.read_text(os.path.join(helpers.FORGE_SRC, "VERSION")).strip())
        # project-owned state
        st = self.read_json(".forge/STATUS.json")
        self.assertEqual(st["schema_version"], 2)
        self.assertIsNone(st["task"])
        self.assertEqual(st["project"], "proj")
        code, out, err = self.forge_status("validate")
        self.assertEqual(code, 0, err)
        binding = self.read_json(".forge/binding.json")
        self.assertEqual(binding["stack"], "python")
        self.assertTrue(binding["verify"], "a python project gets a verify entry")
        self.assertEqual(binding["project"], "proj")
        for rel in (".forge/ledger.jsonl", ".forge/history.jsonl", ".forge/queue.jsonl"):
            self.assertTrue(os.path.exists(self.path(rel)), rel)
            self.assertEqual(self.read(rel), "")
        self.assertTrue(os.path.exists(self.path(".forge/CHANGELOG.md")))
        self.assertTrue(os.path.exists(self.path(".forge/lessons/INDEX.md")))
        self.assertTrue(os.path.exists(self.path(".forge/decisions/0001-adopt-forge.md")))
        gi = self.read(".gitignore").splitlines()
        self.assertIn(".forge/.runtime/", gi)
        self.assertIn(".forge/incidents/", gi)
        # manifest: sha256 per Forge-owned file, matching what is on disk
        manifest = self.read_json(".forge/install-manifest.json")
        self.assertIn(".forge/bin/forge-status", manifest["files"])
        self.assertIn(".forge/bin/forgelib/common.py", manifest["files"])
        self.assertNotIn(".forge/binding.json", manifest["files"], "project-owned files are not Forge-owned")
        self.assertNotIn(".forge/STATUS.json", manifest["files"])
        for rel, sha in manifest["files"].items():
            self.assertEqual(common.sha256_file(self.path(rel)), sha, rel)
        self.assertEqual(manifest["forge_version"], self.read(".forge/VERSION").strip())

    def test_settings_merge(self):
        code, out, err = self.install()
        self.assertEqual(code, 0, err + out)
        settings = self.read_json(".claude/settings.json")
        with open(FRAGMENT, encoding="utf-8") as f:
            fragment = json.load(f)
        # scalars: fragment wins only when absent locally
        self.assertEqual(settings["effortLevel"], "high")
        self.assertEqual(settings["model"], "fable")
        self.assertEqual(settings["subagentPromptCacheTtl"], fragment["subagentPromptCacheTtl"])
        # arrays: union
        allow = settings["permissions"]["allow"]
        self.assertIn("Bash(make *)", allow)
        self.assertIn("Bash(.forge/bin/*)", allow)
        for rule in fragment["permissions"]["deny"]:
            self.assertIn(rule, settings["permissions"]["deny"])
        # verify commands become Bash(<prefix> *) allow rules
        binding = self.read_json(".forge/binding.json")
        for entry in binding["verify"]:
            first = entry["cmd"].split()[0]
            self.assertTrue(any(r.startswith("Bash(") and first in r for r in allow), (entry["cmd"], allow))
        # hooks: every Forge entry present, the non-Forge Stop hook kept
        for event, entries in fragment["hooks"].items():
            self.assertIn(event, settings["hooks"], event)
            forge_cmds = sorted(h["command"] for e in entries for h in e["hooks"])
            local_cmds = sorted(h["command"] for e in settings["hooks"][event] for h in e["hooks"] if "/.forge/bin/forge-hook" in h["command"])
            self.assertEqual(local_cmds, forge_cmds, event)
        stop_cmds = [h["command"] for e in settings["hooks"]["Stop"] for h in e["hooks"]]
        self.assertIn("echo my-own-stop-hook", stop_cmds)
        # onFailure block only on the gate events
        for event, entries in settings["hooks"].items():
            for e in entries:
                for h in e["hooks"]:
                    if "/.forge/bin/forge-hook" in h["command"] and h.get("onFailure") == "block":
                        self.assertIn(event, ("PreToolUse", "SubagentStop"), event)

    def test_claude_md_fragment_inserted_once_and_content_kept(self):
        self.install()
        text = self.read("CLAUDE.md")
        self.assertIn("Keep this paragraph.", text)
        self.assertEqual(text.count("<!-- forge:begin"), 1)
        self.assertEqual(text.count("<!-- forge:end -->"), 1)
        self.assertIn(".forge/STATUS.json", text)
        self.install()
        text2 = self.read("CLAUDE.md")
        self.assertEqual(text2.count("<!-- forge:begin"), 1)
        self.assertEqual(text, text2)

    def test_stale_fragment_is_replaced_not_duplicated(self):
        self.write("CLAUDE.md", "# My project\n\n<!-- forge:begin (managed) -->\nold fragment text\n<!-- forge:end -->\n\nTrailing paragraph.\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "old fragment")
        code, out, err = self.install()
        self.assertEqual(code, 0, err)
        text = self.read("CLAUDE.md")
        self.assertNotIn("old fragment text", text)
        self.assertEqual(text.count("<!-- forge:begin"), 1)
        self.assertIn("Trailing paragraph.", text)
        self.assertIn("# My project", text)

    def test_idempotent_second_run_changes_nothing(self):
        code, out, err = self.install()
        self.assertEqual(code, 0, err + out)
        before = tree_hashes(self.target)
        code, out, err = self.install()
        self.assertEqual(code, 0, err + out)
        self.assertIn("no changes", out.lower())
        self.assertEqual(tree_hashes(self.target), before)

    def test_dry_run_writes_nothing(self):
        before = tree_hashes(self.target)
        code, out, err = self.install("--dry-run")
        self.assertEqual(code, 0, err + out)
        self.assertEqual(tree_hashes(self.target), before)
        self.assertFalse(os.path.exists(self.path(".forge")))
        self.assertIn(".forge/bin/forge-status", out)

    def test_no_model_and_effort_flags(self):
        self.write(".claude/settings.json", "{}")
        code, out, err = self.install("--no-model", "--effort", "low")
        self.assertEqual(code, 0, err)
        settings = self.read_json(".claude/settings.json")
        self.assertNotIn("model", settings)
        self.assertEqual(settings["effortLevel"], "low")

    def test_prepared_binding_is_installed_verbatim(self):
        prepared = os.path.join(self.target, "..", "prepared-binding.json")
        with open(prepared, "w", encoding="utf-8") as f:
            json.dump(helpers.BINDING, f)
        self.addCleanup(lambda: os.path.exists(prepared) and os.unlink(prepared))
        code, out, err = self.install("--binding", prepared)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.read_json(".forge/binding.json"), helpers.BINDING)
        allow = self.read_json(".claude/settings.json")["permissions"]["allow"]
        self.assertTrue(any("unittest" in r or "cd lib" in r for r in allow), allow)
        self.assertFalse(any("git push" in r for r in allow), "irreversible prefixes are never pre-approved")

    def test_existing_binding_is_never_touched(self):
        self.install()
        binding = self.read_json(".forge/binding.json")
        binding["notes"] = ["operator edited"]
        self.write(".forge/binding.json", json.dumps(binding))
        self.install()
        self.assertEqual(self.read_json(".forge/binding.json")["notes"], ["operator edited"])

    def test_with_bench(self):
        code, out, err = self.install("--with-bench")
        self.assertEqual(code, 0, err)
        self.assertTrue(os.path.exists(self.path(".forge/bin/forge-bench")))


class OwnershipTests(InstallerTestCase):
    def test_locally_modified_forge_file_refused_unless_forced(self):
        self.install()
        self.write(".forge/FORGE.md", "# hand-edited\n")
        code, out, err = self.install()
        self.assertEqual(code, 3, out + err)
        self.assertIn("FORGE.md", err + out)
        self.assertEqual(self.read(".forge/FORGE.md"), "# hand-edited\n", "a refusal writes nothing")
        code, out, err = self.install("--force")
        self.assertEqual(code, 0, err + out)
        self.assertNotEqual(self.read(".forge/FORGE.md"), "# hand-edited\n")
        manifest = self.read_json(".forge/install-manifest.json")
        self.assertEqual(common.sha256_file(self.path(".forge/FORGE.md")), manifest["files"][".forge/FORGE.md"])

    def test_force_never_overwrites_operator_settings_scalars(self):
        # review finding #35: --force (the remedy for a Forge-owned file conflict) must not touch settings scalars
        self.write(".claude/settings.json", json.dumps({
            "model": "opus", "effortLevel": "high", "plansDirectory": "plans",
            "env": {"CLAUDE_CODE_SUBAGENT_MODEL": "haiku"}}, indent=2))
        code, out, err = self.install()
        self.assertEqual(code, 0, err + out)
        self.write(".forge/FORGE.md", "# hand-edited\n")
        code, out, err = self.install("--force")
        self.assertEqual(code, 0, err + out)
        settings = self.read_json(".claude/settings.json")
        self.assertEqual(settings["model"], "opus")
        self.assertEqual(settings["effortLevel"], "high")
        self.assertEqual(settings["plansDirectory"], "plans")
        self.assertEqual(settings["env"]["CLAUDE_CODE_SUBAGENT_MODEL"], "haiku")
        self.assertNotEqual(self.read(".forge/FORGE.md"), "# hand-edited\n", "--force still overwrites Forge-owned files")
        # every kept difference is printed as settings: <key> local=<v> -> fragment=<w>
        for key in ("model", "effortLevel", "plansDirectory", "env.CLAUDE_CODE_SUBAGENT_MODEL"):
            self.assertRegex(out, rf"settings: {key}\s+local=.* -> fragment=", key)
        self.assertIn("--force-settings", out)

    def test_force_settings_applies_fragment_scalars(self):
        self.write(".claude/settings.json", json.dumps({"model": "opus", "plansDirectory": "plans"}, indent=2))
        code, out, err = self.install()
        self.assertEqual(code, 0, err + out)
        self.assertEqual(self.read_json(".claude/settings.json")["model"], "opus")
        code, out, err = self.install("--force-settings")
        self.assertEqual(code, 0, err + out)
        settings = self.read_json(".claude/settings.json")
        with open(FRAGMENT, encoding="utf-8") as f:
            fragment = json.load(f)
        self.assertEqual(settings["model"], fragment["model"])
        self.assertEqual(settings["plansDirectory"], fragment["plansDirectory"])
        self.assertRegex(out, r"settings: model\s+local=\"opus\" -> fragment=")

    def test_target_must_be_a_git_root(self):
        plain = tempfile.mkdtemp(prefix="forge-nogit-")
        self.addCleanup(shutil.rmtree, plain, True)
        code, out, err = self.install(target=plain)
        self.assertEqual(code, 3, out + err)
        self.assertTrue(err.strip())
        code, out, err = self.install(target=self.path("lib"))
        self.assertEqual(code, 3, out + err)

    def test_version_mismatch_needs_upgrade(self):
        self.install()
        self.write(".forge/VERSION", "0.9.0\n")
        code, out, err = self.install()
        self.assertEqual(code, 3, out + err)
        self.assertIn("--upgrade", err + out)

    def test_upgrade_backs_up_local_edits(self):
        self.install()
        self.write(".forge/VERSION", "0.9.0\n")
        self.write(".forge/FORGE.md", "# hand-edited\n")
        code, out, err = self.install("--upgrade")
        self.assertEqual(code, 0, err + out)
        self.assertEqual(self.read(".forge/VERSION").strip(), common.read_text(os.path.join(helpers.FORGE_SRC, "VERSION")).strip())
        self.assertNotEqual(self.read(".forge/FORGE.md"), "# hand-edited\n")
        incidents = self.path(".forge/incidents")
        backups = [d for d in os.listdir(incidents) if d.startswith("upgrade-")] if os.path.isdir(incidents) else []
        self.assertTrue(backups, "local edits are backed up under .forge/incidents/upgrade-<ts>/")
        self.assertTrue(os.path.exists(os.path.join(incidents, backups[0], ".forge", "FORGE.md")))


class PersistedOptionsTests(InstallerTestCase):
    """review-2 finding #12: --no-model / --effort are operator choices recorded in install-manifest.json "options"."""

    def test_no_model_and_effort_survive_reinstall_and_upgrade(self):
        self.write(".claude/settings.json", "{}")
        code, out, err = self.install("--no-model", "--effort", "low")
        self.assertEqual(code, 0, err + out)
        self.assertEqual(self.read_json(".forge/install-manifest.json")["options"], {"no_model": True, "effort": "low"})
        code, out, err = self.install()                      # plain re-install, no flags
        self.assertEqual(code, 0, err + out)
        self.assertNotIn("model", self.read_json(".claude/settings.json"))
        self.assertIn("no changes", out.lower())
        self.write(".forge/VERSION", "0.9.0\n")
        code, out, err = self.install("--upgrade")          # upgrade, no flags
        self.assertEqual(code, 0, err + out)
        settings = self.read_json(".claude/settings.json")
        self.assertNotIn("model", settings, "a recorded --no-model is honoured by --upgrade")
        self.assertEqual(settings["effortLevel"], "low")
        self.assertNotRegex(out, r"settings: effortLevel\s+local=")
        self.assertRegex(out, r"option\s+no_model\s+kept from install-manifest.json")
        self.assertEqual(self.read_json(".forge/install-manifest.json")["options"], {"no_model": True, "effort": "low"})

    def test_with_model_clears_and_effort_replaces_recorded_choice(self):
        self.write(".claude/settings.json", "{}")
        self.install("--no-model", "--effort", "low")
        code, out, err = self.install("--with-model", "--effort", "medium")
        self.assertEqual(code, 0, err + out)
        with open(FRAGMENT, encoding="utf-8") as f:
            fragment = json.load(f)
        settings = self.read_json(".claude/settings.json")
        self.assertEqual(settings.get("model"), fragment["model"])
        self.assertEqual(settings["effortLevel"], "medium")
        self.assertEqual(self.read_json(".forge/install-manifest.json")["options"], {"no_model": False, "effort": "medium"})
        code, out, err = self.install("--no-model", "--with-model")
        self.assertEqual(code, 2, out + err)

    def test_default_install_records_no_choices(self):
        code, out, err = self.install()
        self.assertEqual(code, 0, err + out)
        self.assertEqual(self.read_json(".forge/install-manifest.json")["options"], {"no_model": False, "effort": None})


class ChangelogDeltaTests(InstallerTestCase):
    """review-2 finding #11: --upgrade prints the forge/CHANGELOG.md sections between .forge/VERSION and the payload."""

    def load_installer(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("forge_installer_under_test", INSTALLER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_changelog_sections_selects_the_half_open_range(self):
        mod = self.load_installer()
        text = ("# Changelog\n\nintro\n\n## 1.2.0 — 2027-01-01\n\n- c\n\n## 1.1.0 — 2026-12-01\n\n- b\n\n"
                "## 1.0.0 — 2026-10-11\n\n- a\n\n## 0.9.0\n\n- z\n")
        self.assertEqual([v for v, _ in mod.changelog_sections(text, "1.0.0", "1.2.0")], ["1.2.0", "1.1.0"])
        self.assertEqual([v for v, _ in mod.changelog_sections(text, "0.9.0", "1.0.0")], ["1.0.0"])
        self.assertEqual(mod.changelog_sections(text, "1.2.0", "1.2.0"), [])
        body = dict(mod.changelog_sections(text, "1.0.0", "1.1.0"))["1.1.0"]
        self.assertIn("- b", body)
        self.assertNotIn("- a", body)
        self.assertNotIn("- c", body)

    def test_upgrade_and_dry_run_print_the_delta(self):
        self.install()
        self.write(".forge/VERSION", "0.9.0\n")
        version = common.read_text(os.path.join(helpers.FORGE_SRC, "VERSION")).strip()
        for args in (("--upgrade", "--dry-run"), ("--upgrade",)):
            code, out, err = self.install(*args)
            self.assertEqual(code, 0, err + out)
            self.assertIn(f"CHANGELOG 0.9.0 -> {version}", out, args)
            self.assertRegex(out, rf"(?m)^## {re.escape(version)}\b", args)

    def test_no_entries_message(self):
        self.install()
        code, out, err = self.install("--upgrade")
        self.assertEqual(code, 0, err + out)
        version = common.read_text(os.path.join(helpers.FORGE_SRC, "VERSION")).strip()
        self.assertIn(f"no CHANGELOG entries between {version} and {version}", out)
        code, out, err = self.install()
        self.assertNotIn("CHANGELOG", out, "a plain install prints no delta")


class GenericFragmentTests(InstallerTestCase):
    """review findings #36/#42/#50: the shipped fragment carries no project-specific command rule."""

    def test_fragment_has_no_project_specific_allow_rules(self):
        with open(FRAGMENT, encoding="utf-8") as f:
            fragment = json.load(f)
        for rule in fragment["permissions"]["allow"]:
            if not rule.startswith("Bash("):
                continue
            self.assertTrue(rule.startswith(("Bash(.forge/bin/", "Bash(git ")), f"project-specific rule in fragment: {rule}")
            for word in ("pip", "pytest", "unittest", "qa/", "golden", "lib", "npm", "gradle"):
                self.assertNotIn(word, rule, rule)

    def _bare_target(self):
        target = tempfile.mkdtemp(prefix="forge-bare-")
        self.addCleanup(shutil.rmtree, target, True)
        subprocess.run(["git", "init", "-q", target], check=True)
        return target

    def _allow(self, target):
        with open(os.path.join(target, ".claude", "settings.json"), encoding="utf-8") as f:
            return json.load(f)["permissions"]["allow"]

    def test_empty_verify_install_has_no_pip_or_test_runner_rules(self):
        target = self._bare_target()
        code, out, err = self.install(target=target)
        self.assertEqual(code, 0, err + out)
        with open(os.path.join(target, ".forge", "binding.json"), encoding="utf-8") as f:
            binding = json.load(f)
        self.assertEqual(binding["verify"], [])
        for rule in self._allow(target):
            for word in ("pip", "pytest", "unittest", "golden_counts"):
                self.assertNotIn(word, rule, rule)

    def test_pip_rule_only_when_bootstrap_uses_pip(self):
        target = self._bare_target()
        with open(os.path.join(target, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write("requests\n")
        code, out, err = self.install(target=target)
        self.assertEqual(code, 0, err + out)
        with open(os.path.join(target, ".forge", "binding.json"), encoding="utf-8") as f:
            self.assertIn("pip install", json.load(f)["bootstrap"])
        self.assertIn("Bash(python3 -m pip install *)", self._allow(target))
        # the fixture repo (lib/*.py, no requirements/pyproject) has no pip bootstrap, so no pip rule
        code, out, err = self.install()
        self.assertEqual(code, 0, err + out)
        self.assertIsNone(self.read_json(".forge/binding.json")["bootstrap"])
        self.assertFalse(any("pip" in r for r in self.read_json(".claude/settings.json")["permissions"]["allow"]))


class PayloadLayoutTests(InstallerTestCase):
    """The payload's .claude/ ships as dot-claude/ and installs to <target>/.claude/; plugin/ never drifts."""

    def test_payload_ships_dot_claude_not_dot_claude_dir(self):
        self.assertFalse(os.path.exists(os.path.join(PAYLOAD, ".claude")),
                         "payload/.claude would be auto-discovered by Claude Code in the Forge source repo")
        self.assertTrue(os.path.isfile(FRAGMENT))
        self.assertFalse(os.path.exists(os.path.join(FORGE_SRC, "plugin", "payload", ".claude")))

    def test_dot_claude_installs_to_target_dot_claude(self):
        code, out, err = self.install()
        self.assertEqual(code, 0, err + out)
        manifest = self.read_json(".forge/install-manifest.json")["files"]
        self.assertFalse([r for r in manifest if r.startswith("dot-claude")], "manifest paths are target-relative")
        self.assertIn(".claude/agents/forge-builder.md", manifest)
        self.assertIn(".claude/settings.forge.json", manifest)
        self.assertIn(".claude/rules/forge-stack-python.md", manifest)
        self.assertFalse(os.path.exists(self.path("dot-claude")))

    def test_plugin_matches_generator_output(self):
        # review findings #12/#60: plugin/ is generated; any drift from the payload fails the suite
        r = subprocess.run([sys.executable, MAKE_PLUGIN, "--check"], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class MigrationTests(InstallerTestCase):
    """1.0.1: migrations/0001-binding-agent-paths.py is additive, idempotent and keeps the file's other bytes."""
    MIGRATION = "0001-binding-agent-paths.py"

    def pre_1_0_1(self):
        """Shape a 1.0.0 install: binding without agent_paths, migration not recorded, old VERSION."""
        code, out, err = self.install()
        self.assertEqual(code, 0, err + out)
        text = self.read(".forge/binding.json")
        self.assertIn('"agent_paths": []', text, "a fresh binding carries the key from the template")
        self.write(".forge/binding.json", "\n".join(l for l in text.splitlines() if '"agent_paths"' not in l) + "\n")
        self.assertNotIn("agent_paths", self.read_json(".forge/binding.json"))
        manifest = self.read_json(".forge/install-manifest.json")
        self.assertIn(self.MIGRATION, manifest["migrations"], "a fresh install records every migration as applied")
        manifest["migrations"] = [m for m in manifest["migrations"] if m != self.MIGRATION]
        self.write(".forge/install-manifest.json", json.dumps(manifest, indent=2))
        self.write(".forge/VERSION", "1.0.0\n")

    def test_upgrade_migration_adds_agent_paths_once_and_keeps_formatting(self):
        self.pre_1_0_1()
        before = self.read(".forge/binding.json")
        code, out, err = self.install("--upgrade", "--dry-run")
        self.assertEqual(code, 0, err + out)
        self.assertIn(f"migrate  {self.MIGRATION}", out)
        self.assertEqual(self.read(".forge/binding.json"), before, "a dry run writes nothing")
        code, out, err = self.install("--upgrade")
        self.assertEqual(code, 0, err + out)
        after = self.read(".forge/binding.json")
        binding = json.loads(after)
        self.assertEqual(binding["agent_paths"], [])
        self.assertEqual({k: v for k, v in binding.items() if k != "agent_paths"}, json.loads(before))
        self.assertEqual(list(binding).index("agent_paths"), list(binding).index("mechanic_denied_paths") + 1)
        self.assertEqual(after.replace('  "agent_paths": [],\n', ""), before, "every other byte is kept")
        self.assertIn(self.MIGRATION, self.read_json(".forge/install-manifest.json")["migrations"])
        snapshot = tree_hashes(self.target)
        code, out, err = self.install("--upgrade")
        self.assertEqual(code, 0, err + out)
        self.assertNotIn("migrate", out, "an applied migration never runs twice")
        self.assertEqual(tree_hashes(self.target), snapshot, "idempotent: a second upgrade changes nothing")

    def test_migration_keeps_a_configured_key(self):
        self.pre_1_0_1()
        binding = self.read_json(".forge/binding.json")
        binding["agent_paths"] = ["qa/reports/**"]
        self.write(".forge/binding.json", json.dumps(binding, indent=2))
        code, out, err = self.install("--upgrade")
        self.assertEqual(code, 0, err + out)
        self.assertEqual(self.read_json(".forge/binding.json")["agent_paths"], ["qa/reports/**"])

    def test_migration_reserialises_a_one_line_binding(self):
        self.pre_1_0_1()
        self.write(".forge/binding.json", json.dumps(self.read_json(".forge/binding.json")))
        code, out, err = self.install("--upgrade")
        self.assertEqual(code, 0, err + out)
        binding = self.read_json(".forge/binding.json")
        self.assertEqual(binding["agent_paths"], [])
        self.assertEqual(list(binding).index("agent_paths"), len(binding) - 1, "the fallback appends the key")


class InstallShTests(InstallerTestCase):
    """review finding #43: the README one-liner and the doctor's remedy use flags install.sh accepts."""

    def sh(self, *args, env=None):
        e = dict(os.environ)
        e.pop("FORGE_ROOT", None)
        e["PYTHONDONTWRITEBYTECODE"] = "1"
        e.update(env or {})
        return subprocess.run(["bash", INSTALL_SH, *args], cwd=self.target, env=e, capture_output=True, text=True,
                              timeout=300)

    def test_repo_without_tag_is_usage_error(self):
        r = self.sh("--repo", "someone/forge", "--target", self.target, "--dry-run")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("--tag", r.stderr)

    def test_tag_alone_fetches_the_default_repo_forge_dir(self):
        # serve https://github.com/riggs19991/ruggedroute-dataops.git from a local bare repo (no network)
        mirror = tempfile.mkdtemp(prefix="forge-mirror-")
        self.addCleanup(shutil.rmtree, mirror, True)
        src = os.path.join(mirror, "src")
        shutil.copytree(FORGE_SRC, os.path.join(src, "forge"),
                        ignore=shutil.ignore_patterns("__pycache__", "plugin", "tests", "docs", "evals"))
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]
        for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "src"], ["tag", "v9.9.9"]):
            subprocess.run(git + cmd, cwd=src, check=True, capture_output=True)
        bare = os.path.join(mirror, "riggs19991", "ruggedroute-dataops.git")
        subprocess.run(["git", "clone", "-q", "--bare", src, bare], check=True, capture_output=True)
        env = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": f"url.{mirror}/.insteadOf",
               "GIT_CONFIG_VALUE_0": "https://github.com/"}
        r = self.sh("--tag", "v9.9.9", "--target", self.target, "--dry-run", env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("fetched riggs19991/ruggedroute-dataops@v9.9.9", r.stdout)
        self.assertIn("(dry run)", r.stdout)

    def test_readme_and_doctor_use_accepted_flags(self):
        readme = common.read_text(os.path.join(FORGE_SRC, "README.md"))
        for line in readme.splitlines():
            if "install.sh" in line and "--tag" in line and "bash -s" in line:
                self.assertIn("--target", line)
        doctor = common.read_text(os.path.join(PAYLOAD, ".forge", "bin", "forge-doctor"))
        self.assertNotIn("install.sh --upgrade --tag", doctor)
        self.assertIn("install.sh --tag v{pin}", doctor)


class DoctorTests(InstallerTestCase):
    """forge-doctor: FORGE_ROOT naming another repo FAILs (#3); --report runs the pointer check (#45)."""

    def doctor(self, *args, forge_root=None):
        env = dict(os.environ)
        env.pop("FORGE_ROOT", None)
        env["CLAUDE_PROJECT_DIR"] = self.target
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        if forge_root is not None:
            env["FORGE_ROOT"] = forge_root
        r = subprocess.run([self.path(".forge/bin/forge-doctor"), *args], cwd=self.target, env=env,
                           capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout, r.stderr

    def setUp(self):
        super().setUp()
        code, out, err = self.install()
        self.assertEqual(code, 0, err + out)

    def test_report_runs_pointer_check_by_default(self):
        code, out, err = self.doctor("--report", "--no-probes")
        self.assertEqual(code, 0, err)
        self.assertRegex(out, r"(?m)^(OK|WARN|FAIL) pointers: ")
        code, out, err = self.doctor("--quick")
        self.assertNotRegex(out, r"(?m)^\w+ pointers: ", "--quick stays minimal")

    def test_foreign_forge_root_fails(self):
        other = tempfile.mkdtemp(prefix="forge-other-")
        self.addCleanup(shutil.rmtree, other, True)
        subprocess.run(["git", "init", "-q", other], check=True)
        os.makedirs(os.path.join(other, ".forge"))
        code, out, err = self.doctor("--quick", forge_root=other)
        self.assertEqual(code, 1, out + err)
        self.assertRegex(out, r"(?m)^FAIL forge-root: FORGE_ROOT=.* names a different repository")
        code, out, err = self.doctor("--quick", forge_root=self.target)
        self.assertRegex(out, r"(?m)^OK forge-root: ")
        code, out, err = self.doctor("--quick")
        self.assertRegex(out, r"(?m)^OK forge-root: FORGE_ROOT unset")

    def test_installer_doctor_run_ignores_inherited_forge_root(self):
        other = tempfile.mkdtemp(prefix="forge-other-")
        self.addCleanup(shutil.rmtree, other, True)
        env = dict(os.environ, FORGE_ROOT=other, PYTHONDONTWRITEBYTECODE="1")
        self.write(".forge/VERSION", "0.0.1\n")
        r = subprocess.run([sys.executable, INSTALLER, "--target", self.target, "--source", PAYLOAD, "--upgrade"],
                           cwd=self.target, env=env, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertRegex(r.stdout, r"(?m)^OK forge-root: FORGE_ROOT unset")

    def test_malformed_agent_paths_fails_and_a_wide_one_warns(self):
        binding = self.read_json(".forge/binding.json")
        binding["agent_paths"] = "qa/**"
        self.write(".forge/binding.json", json.dumps(binding, indent=2))
        code, out, err = self.doctor("--report", "--no-probes")
        self.assertRegex(out, r"(?m)^FAIL binding: agent_paths is not a list")
        binding["agent_paths"] = [".forge/lessons/**"]
        self.write(".forge/binding.json", json.dumps(binding, indent=2))
        code, out, err = self.doctor("--report", "--no-probes")
        self.assertRegex(out, r"(?m)^WARN binding: agent_paths .* reaches Forge state")
        binding["agent_paths"] = ["qa/reports/**"]
        self.write(".forge/binding.json", json.dumps(binding, indent=2))
        code, out, err = self.doctor("--report", "--no-probes")
        self.assertNotRegex(out, r"(?m)^(WARN|FAIL) binding: agent_paths")


class BenchTasksetTests(InstallerTestCase):
    """review finding #44: forge-bench takes a list, one task object, or a directory of task files."""

    def bench(self, taskset):
        env = dict(os.environ)
        env.pop("FORGE_ROOT", None)
        env["CLAUDE_PROJECT_DIR"] = self.target
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        r = subprocess.run([self.path(".forge/bin/forge-bench"), taskset, "--dry-run", "--arms", "solo"],
                           cwd=self.target, env=env, capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout, r.stderr

    def setUp(self):
        super().setUp()
        code, out, err = self.install("--with-bench")
        self.assertEqual(code, 0, err + out)

    def test_single_task_file_directory_and_list(self):
        files = sorted(f for f in os.listdir(EVAL_TASKS) if f.endswith(".json"))
        self.assertTrue(files)
        code, out, err = self.bench(os.path.join(EVAL_TASKS, files[0]))
        self.assertEqual(code, 0, err)
        self.assertEqual(out.count("[dry-run] task"), 1)
        code, out, err = self.bench(EVAL_TASKS)
        self.assertEqual(code, 0, err)
        self.assertEqual(out.count("[dry-run] task"), len(files))
        listed = os.path.join(self.target, "..", os.path.basename(self.target) + "-taskset.json")
        self.addCleanup(lambda: os.path.exists(listed) and os.unlink(listed))
        with open(listed, "w", encoding="utf-8") as f:
            json.dump([json.loads(common.read_text(os.path.join(EVAL_TASKS, n))) for n in files], f)
        code, out, err = self.bench(listed)
        self.assertEqual(code, 0, err)
        self.assertEqual(out.count("[dry-run] task"), len(files))
        self.assertNotIn("FORGE_ROOT=", out, "the driver arm never exports FORGE_ROOT")

    def test_invalid_tasksets_are_usage_errors(self):
        empty = tempfile.mkdtemp(prefix="forge-empty-")
        self.addCleanup(shutil.rmtree, empty, True)
        code, out, err = self.bench(empty)
        self.assertEqual(code, 2, out + err)
        bad = os.path.join(empty, "bad.json")
        with open(bad, "w", encoding="utf-8") as f:
            json.dump({"title": "x"}, f)
        code, out, err = self.bench(bad)
        self.assertEqual(code, 2, out + err)
        self.assertIn("base", err)


if __name__ == "__main__":
    unittest.main()
