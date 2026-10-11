"""Tests for forge/installer.py (MODULE-API §8; design §10.1 steps 1-7, §8.2 ownership and settings merge)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import helpers
from helpers import INSTALLER, PAYLOAD, common, tree_hashes

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
        with open(os.path.join(PAYLOAD, ".claude", "settings.forge.json"), encoding="utf-8") as f:
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

    def test_force_overwrites_settings_scalars(self):
        self.install()
        self.assertEqual(self.read_json(".claude/settings.json")["effortLevel"], "high")
        code, out, err = self.install("--force")
        self.assertEqual(code, 0, err)
        self.assertNotEqual(self.read_json(".claude/settings.json")["effortLevel"], "high")

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


if __name__ == "__main__":
    unittest.main()
