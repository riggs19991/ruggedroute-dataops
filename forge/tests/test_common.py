"""Tests for forgelib.common (MODULE-API §1). These must pass today: common.py is written."""
import json
import os
import subprocess
import tempfile
import unittest
from unittest import mock

import helpers
from helpers import common


class GlobTests(unittest.TestCase):
    def test_glob_to_regex_translation(self):
        # design §13.3: **/ -> (.*/)?, ** -> .*, * -> [^/]*, ? -> [^/], '.' escaped; anchored
        self.assertEqual(common.glob_to_regex("**/file.py"), r"^(.*/)?file\.py$")
        self.assertEqual(common.glob_to_regex("**"), "^.*$")
        self.assertEqual(common.glob_to_regex("a/**/b"), r"^a/(.*/)?b$")
        self.assertEqual(common.glob_to_regex("lib/*.py"), r"^lib/[^/]*\.py$")
        self.assertEqual(common.glob_to_regex("a?b"), "^a[^/]b$")
        self.assertEqual(common.glob_to_regex("./x.py"), r"^x\.py$")

    def test_glob_to_regex_escapes_regex_metacharacters(self):
        rx = common.glob_to_regex("a+b(c)[d]{e}^$|\\.py")
        for ch in "+()[]{}^$|\\":
            self.assertIn("\\" + ch, rx)
        self.assertTrue(common.glob_match("a+b(c)[d]{e}^$|\\.py", "a+b(c)[d]{e}^$|\\.py"))
        self.assertFalse(common.glob_match("aab.py", "a+b.py"))

    def test_double_star_matches_any_depth_including_root(self):
        self.assertTrue(common.glob_match("file.py", "**/file.py"))
        self.assertTrue(common.glob_match("a/b/file.py", "**/file.py"))
        self.assertTrue(common.glob_match("layers/mvum/a/b.py", "layers/mvum/**"))
        self.assertTrue(common.glob_match("x/upload_tool.py", "**/*upload*"))

    def test_single_star_does_not_cross_slash(self):
        self.assertTrue(common.glob_match("lib/x.py", "lib/*.py"))
        self.assertFalse(common.glob_match("lib/sub/x.py", "lib/*.py"))
        self.assertFalse(common.glob_match("axpy", "a.py"))  # '.' is literal

    def test_bare_filename_matches_only_at_root(self):
        self.assertTrue(common.glob_match("file.py", "file.py"))
        self.assertFalse(common.glob_match("dir/file.py", "file.py"))

    def test_directory_glob_matches_files_below_it(self):
        self.assertTrue(common.glob_match("layers/mvum/x.py", "layers/mvum"))
        self.assertTrue(common.glob_match("layers/mvum/x.py", "layers/mvum/"))
        self.assertFalse(common.glob_match("layers/mvumx/x.py", "layers/mvum"))

    def test_leading_dot_slash_normalised_on_both_sides(self):
        self.assertTrue(common.glob_match("./lib/x.py", "lib/x.py"))
        self.assertTrue(common.glob_match("lib/x.py", "./lib/x.py"))

    def test_question_mark(self):
        self.assertTrue(common.glob_match("lib/a1.py", "lib/a?.py"))
        self.assertFalse(common.glob_match("lib/a/.py", "lib/a?.py"))

    def test_any_glob_returns_matching_glob_or_none(self):
        self.assertEqual(common.any_glob("lib/x.py", ["qa/**", "lib/*.py"]), "lib/*.py")
        self.assertIsNone(common.any_glob("lib/x.py", ["qa/**"]))
        self.assertIsNone(common.any_glob("lib/x.py", []))
        self.assertIsNone(common.any_glob("lib/x.py", None))


class AliasAndRoleTests(unittest.TestCase):
    def test_alias_model_normalises_full_ids(self):
        self.assertEqual(common.alias_model("claude-opus-5-5"), "opus")
        self.assertEqual(common.alias_model("claude-sonnet-4-5[1m]"), "sonnet")
        self.assertEqual(common.alias_model("claude-haiku-5-5"), "haiku")
        self.assertEqual(common.alias_model("claude-fable-5-1"), "fable")
        self.assertEqual(common.alias_model("Fable"), "fable")
        self.assertEqual(common.alias_model("  OPUS "), "opus")

    def test_alias_model_special_values(self):
        self.assertEqual(common.alias_model("mythos"), "fable")
        self.assertEqual(common.alias_model("best"), "fable")
        self.assertEqual(common.alias_model("default"), "opus")
        self.assertIsNone(common.alias_model(None))
        self.assertIsNone(common.alias_model(""))
        self.assertEqual(common.alias_model("gpt-9"), "gpt-9")  # unknown: lowercased input

    def test_agent_role_strips_plugin_namespace(self):
        self.assertEqual(common.agent_role("forge:forge-builder"), "forge-builder")
        self.assertEqual(common.agent_role("forge-builder"), "forge-builder")
        self.assertIsNone(common.agent_role(None))
        self.assertIsNone(common.agent_role(""))

    def test_tier_order(self):
        self.assertTrue(common.tier_gte("fable", "opus"))
        self.assertTrue(common.tier_gte("opus", "opus"))
        self.assertFalse(common.tier_gte("sonnet", "opus"))
        self.assertTrue(common.tier_gte("claude-opus-5-5", "sonnet"))  # alias-normalised both sides
        self.assertFalse(common.tier_gte("unknown-model", "haiku"))

    def test_next_tier_ladder(self):
        # design §4.3 rule 6: sonnet -> opus -> fable/low -> fable/medium
        self.assertEqual(common.next_tier("sonnet", "medium"), ("opus", "medium"))
        self.assertEqual(common.next_tier("opus", "medium"), ("fable", "low"))
        self.assertEqual(common.next_tier("fable", "low"), ("fable", "medium"))
        self.assertEqual(common.next_tier("fable", "high"), ("fable", "high"))
        self.assertEqual(common.next_tier("haiku", "medium"), ("sonnet", "medium"))


class MarkdownTests(unittest.TestCase):
    def test_json_block_returns_first_block(self):
        text = "intro\n```json\n{\"a\": 1}\n```\nmore\n```json\n{\"b\": 2}\n```\n"
        self.assertEqual(common.json_block(text), {"a": 1})

    def test_json_block_none_cases(self):
        self.assertIsNone(common.json_block("no fence here"))
        self.assertIsNone(common.json_block("```json\n[1, 2]\n```"))   # not an object
        self.assertIsNone(common.json_block("```json\n{not json}\n```"))
        self.assertIsNone(common.json_block("```json\n{\"unterminated\": 1}\n"))

    def test_json_block_tolerates_indent_and_trailing_space(self):
        text = "  ```json   \n  {\"a\": [1, 2]}\n  ```\n"
        self.assertEqual(common.json_block(text), {"a": [1, 2]})

    def test_headings_exact_level_only(self):
        text = "# Title\n## One\ntext\n### Sub\n## Two  \n#### Deep\n"
        self.assertEqual(common.headings(text), ["One", "Two"])
        self.assertEqual(common.headings(text, level=3), ["Sub"])
        self.assertEqual(common.headings(text, level=1), ["Title"])

    def test_section_body_until_same_or_higher_heading(self):
        text = "## Remaining\n- a\n### detail\n- b\n## Gotchas / do not touch\nnone\n# Top\nx\n"
        self.assertEqual(common.section(text, "Remaining"), "- a\n### detail\n- b")
        self.assertEqual(common.section(text, "gotchas / do not touch"), "none")   # case-insensitive
        self.assertEqual(common.section(text, "Missing"), "")

    def test_render_template_and_truncate(self):
        self.assertEqual(common.render_template("{{ a }}-{{b}}-{{c}}", {"a": 1, "b": "x"}), "1-x-{{c}}")
        self.assertEqual(common.truncate("abc", 10), "abc")
        out = common.truncate("x" * 100, 20)
        self.assertEqual(len(out), 20)
        self.assertTrue(out.endswith("[truncated]"))


class WordHitsTests(unittest.TestCase):
    def test_long_words_match_case_insensitively_on_word_boundaries(self):
        self.assertEqual(common.word_hits("Rotate the SECRET key", ["secret"]), ["secret"])
        self.assertEqual(common.word_hits("rotate secrets", ["secret"]), [])        # \b: plural does not hit
        self.assertEqual(common.word_hits("topsecret file", ["secret"]), [])

    def test_short_words_are_case_sensitive(self):
        self.assertEqual(common.word_hits("flip the KV alias", ["KV"]), ["KV"])
        self.assertEqual(common.word_hits("flip the kv alias", ["KV"]), [])

    def test_not_exclusions_cancel_a_hit(self):
        words = [{"word": "delete", "not": ["soft delete"]}]
        self.assertEqual(common.word_hits("delete the bucket", words), ["delete"])
        self.assertEqual(common.word_hits("soft delete of rows", words), [])

    def test_dict_entries_without_word_and_empty_list(self):
        self.assertEqual(common.word_hits("anything", [{"not": ["x"]}]), [])
        self.assertEqual(common.word_hits("anything", []), [])
        self.assertEqual(common.word_hits("anything", None), [])


class PathsAndRootTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="forge-common-")
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", self.tmp]))
        self.env_backup = {k: os.environ.get(k) for k in ("FORGE_ROOT", "CLAUDE_PROJECT_DIR")}
        for k in self.env_backup:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self.env_backup.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def _git(self, cwd, *args):
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)

    def _repo(self, name, with_forge=True):
        root = os.path.join(self.tmp, name)
        os.makedirs(root)
        self._git(root, "init", "-q", ".")
        self._git(root, "config", "user.email", "t@example.invalid")
        self._git(root, "config", "user.name", "t")
        self._git(root, "config", "commit.gpgsign", "false")
        if with_forge:
            os.makedirs(os.path.join(root, ".forge"))
            with open(os.path.join(root, ".forge", "x"), "w") as f:
                f.write("x")
        with open(os.path.join(root, "README"), "w") as f:
            f.write("r")
        self._git(root, "add", "-A")
        self._git(root, "commit", "-q", "-m", "init")
        return os.path.realpath(root)

    def test_forge_root_prefers_FORGE_ROOT_when_it_has_forge_dir(self):
        root = self._repo("a")
        other = self._repo("b")
        os.environ["FORGE_ROOT"] = root
        self.assertEqual(os.path.realpath(common.forge_root(other)), root)

    def test_forge_root_ignores_FORGE_ROOT_without_forge_dir(self):
        root = self._repo("a")
        bogus = os.path.join(self.tmp, "bogus")
        os.makedirs(bogus)
        os.environ["FORGE_ROOT"] = bogus
        self.assertEqual(os.path.realpath(common.forge_root(root)), root)

    def test_forge_root_from_subdirectory_via_git(self):
        root = self._repo("a")
        sub = os.path.join(root, "lib", "deep")
        os.makedirs(sub)
        self.assertEqual(os.path.realpath(common.forge_root(sub)), root)
        os.environ["CLAUDE_PROJECT_DIR"] = sub
        self.assertEqual(os.path.realpath(common.forge_root()), root)

    def test_forge_root_is_worktree_safe(self):
        root = self._repo("a")
        wt = os.path.join(self.tmp, "a-wt")
        r = self._git(root, "worktree", "add", "-q", wt, "-b", "probe")
        self.assertEqual(r.returncode, 0, r.stderr)
        # the worktree has no .forge/ of its own; the main checkout owns it
        self.assertEqual(os.path.realpath(common.forge_root(wt)), root)

    def test_forge_root_walks_up_without_git(self):
        root = os.path.join(self.tmp, "plain")
        os.makedirs(os.path.join(root, ".forge"))
        sub = os.path.join(root, "x", "y")
        os.makedirs(sub)
        self.assertEqual(os.path.realpath(common.forge_root(sub)), os.path.realpath(root))

    def test_forge_root_falls_back_to_start(self):
        bare = os.path.join(self.tmp, "nothing", "here")
        os.makedirs(bare)
        self.assertEqual(os.path.realpath(common.forge_root(bare)), os.path.realpath(bare))

    def test_paths_rel_normalises(self):
        p = common.Paths(self.tmp)
        self.assertEqual(p.rel(os.path.join(self.tmp, "lib", "x.py")), "lib/x.py")
        self.assertEqual(p.rel("./lib/x.py"), "lib/x.py")
        self.assertEqual(p.rel("lib//x.py"), "lib/x.py")
        self.assertEqual(p.rel(".forge/STATUS.json"), ".forge/STATUS.json")

    def test_paths_layout(self):
        p = common.Paths(self.tmp)
        self.assertEqual(p.status, os.path.join(self.tmp, ".forge", "STATUS.json"))
        self.assertEqual(p.task_file("T-0001", "plan.md"), os.path.join(self.tmp, ".forge", "tasks", "T-0001", "plan.md"))
        self.assertEqual(p.checks_dir("T-0001"), os.path.join(self.tmp, ".forge", "tasks", "T-0001", "checks"))
        self.assertEqual(p.base_file("T-0001", "01"), os.path.join(self.tmp, ".forge", "tasks", "T-0001", ".base-01"))
        self.assertEqual(p.rt("dirty-main"), os.path.join(self.tmp, ".forge", ".runtime", "dirty-main"))
        self.assertEqual(p.agent_record("a1"), os.path.join(self.tmp, ".forge", ".runtime", "agents", "a1.json"))
        self.assertEqual(p.journal_file(None), os.path.join(self.tmp, ".forge", ".runtime", "journal.log"))
        self.assertEqual(p.journal_file("T-0001"), os.path.join(self.tmp, ".forge", "tasks", "T-0001", "journal.md"))

    def test_edit_kind(self):
        p = common.Paths(self.tmp)
        self.assertEqual(common.edit_kind(p, ".forge/tasks/T-0001/plan.md"), "meta")
        self.assertEqual(common.edit_kind(p, ".claude/agent-memory/forge-verifier/MEMORY.md"), "meta")
        self.assertEqual(common.edit_kind(p, "CLAUDE.md"), "meta")
        self.assertEqual(common.edit_kind(p, ".gitignore"), "meta")
        self.assertEqual(common.edit_kind(p, "lib/mod.py"), "source")
        self.assertEqual(common.edit_kind(p, os.path.join(self.tmp, "lib", "mod.py")), "source")


class IoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="forge-io-")
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", self.tmp]))
        self.paths = common.Paths(self.tmp)

    def test_json_roundtrip_and_invalid_json_is_exit_4(self):
        p = os.path.join(self.tmp, "a", "b.json")
        common.write_json_atomic(p, {"x": [1, 2]})
        self.assertEqual(common.read_json(p), {"x": [1, 2]})
        self.assertIsNone(common.read_json(os.path.join(self.tmp, "missing.json")))
        self.assertEqual(common.read_json(os.path.join(self.tmp, "missing.json"), default=[]), [])
        with open(p, "w") as f:
            f.write("{nope")
        with self.assertRaises(common.ForgeError) as cm:
            common.read_json(p)
        self.assertEqual(cm.exception.code, common.EXIT_INVALID)

    def test_jsonl_append_and_read_skips_bad_lines(self):
        p = os.path.join(self.tmp, "rows.jsonl")
        common.append_jsonl(p, {"a": 1})
        common.append_jsonl(p, {"b": 2})
        with open(p, "a") as f:
            f.write("not json\n\n")
        self.assertEqual(common.read_jsonl(p), [{"a": 1}, {"b": 2}])
        self.assertEqual(common.read_jsonl(os.path.join(self.tmp, "none.jsonl")), [])

    def test_text_sha_touch_rm_exists(self):
        p = os.path.join(self.tmp, "t.txt")
        common.write_text_atomic(p, "hello")
        self.assertEqual(common.read_text(p), "hello")
        self.assertIsNone(common.read_text(p + ".missing"))
        self.assertEqual(common.read_text(p + ".missing", default=""), "")
        self.assertEqual(common.sha256_file(p), common.sha256_text("hello"))
        self.assertIsNone(common.sha256_file(p + ".missing"))
        common.touch(os.path.join(self.tmp, "m", "marker"))
        self.assertTrue(common.exists(os.path.join(self.tmp, "m", "marker")))
        common.rm(os.path.join(self.tmp, "m", "marker"))
        common.rm(os.path.join(self.tmp, "m", "marker"))   # idempotent
        self.assertFalse(common.exists(os.path.join(self.tmp, "m", "marker")))

    def test_loaders_raise_exit_4_when_missing(self):
        for fn in (common.load_status, common.load_binding, common.load_routing):
            with self.assertRaises(common.ForgeError) as cm:
                fn(self.paths)
            self.assertEqual(cm.exception.code, common.EXIT_INVALID)

    def test_current_task_and_find_step(self):
        self.assertIsNone(common.current_task({"task": None}))
        task = {"steps": [{"id": "01"}, {"id": "02"}]}
        self.assertEqual(common.current_task({"task": task}), task)
        self.assertEqual(common.find_step(task, "02"), {"id": "02"})
        self.assertIsNone(common.find_step(task, "03"))
        self.assertIsNone(common.find_step({}, "01"))

    def test_session_id_fallback_cli(self):
        self.assertEqual(common.session_id(self.paths), "cli")
        common.write_text_atomic(self.paths.rt("session-id"), "abc-123\n")
        self.assertEqual(common.session_id(self.paths), "abc-123")

    def test_journal_ledger_evidence(self):
        common.journal(self.paths, "T-0001", "hello journal")
        self.assertIn("hello journal", common.read_text(self.paths.journal_file("T-0001")))
        common.journal(self.paths, None, "runtime line")
        self.assertIn("runtime line", common.read_text(self.paths.journal_file(None)))
        common.ledger(self.paths, {"event": "open", "task": "T-0001"})
        rows = common.read_jsonl(self.paths.ledger)
        self.assertEqual(rows[0]["event"], "open")
        self.assertTrue(rows[0]["ts"].endswith("Z"))
        common.evidence_append(self.paths, "T-0001", {"agent_id": "a1", "event": "edit", "kind": "source", "file": "x"})
        common.evidence_append(self.paths, "T-0001", {"agent_id": "a2", "event": "bash", "ok": True})
        self.assertEqual(len(common.evidence_rows(self.paths, "T-0001")), 2)
        self.assertEqual(len(common.evidence_rows(self.paths, "T-0001", agent_id="a1")), 1)
        self.assertEqual(common.evidence_rows(self.paths, "T-0001", event=["bash"])[0]["agent_id"], "a2")
        self.assertIsInstance(common.evidence_rows(self.paths, "T-0001")[0]["ts"], int)

    def test_time_helpers(self):
        iso = common.now_iso()
        self.assertTrue(iso.endswith("Z"))
        self.assertAlmostEqual(common.iso_to_ts(iso), common.now_ts(), delta=5)
        self.assertEqual(common.iso_to_ts("1970-01-01T00:00:10Z"), 10)

    def test_run_and_git_helpers(self):
        code, out = common.run("echo hi; echo err 1>&2; exit 3", cwd=self.tmp)
        self.assertEqual(code, 3)
        self.assertIn("hi", out)
        self.assertIn("err", out)
        code, out = common.run("sleep 5", cwd=self.tmp, timeout=1)
        self.assertEqual(code, 124)
        self.assertIn("timed out", out)
        subprocess.run(["git", "init", "-q", "."], cwd=self.tmp, check=True)
        subprocess.run(["git", "config", "user.email", "t@example.invalid"], cwd=self.tmp, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=self.tmp, check=True)
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=self.tmp, check=True)
        self.assertIsNone(common.git_head(self.tmp))   # no commits yet
        common.write_text_atomic(os.path.join(self.tmp, "a.txt"), "a")
        self.assertEqual(common.git_porcelain(self.tmp), ["a.txt"])
        self.assertEqual(common.git_porcelain(self.tmp, untracked=False), [])
        subprocess.run(["git", "add", "-A"], cwd=self.tmp, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "one"], cwd=self.tmp, check=True)
        base = common.git_head(self.tmp)
        self.assertEqual(len(base), 40)
        common.write_text_atomic(os.path.join(self.tmp, "b.txt"), "b")
        subprocess.run(["git", "add", "-A"], cwd=self.tmp, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "two"], cwd=self.tmp, check=True)
        head = common.git_head(self.tmp)
        self.assertEqual(common.git_diff_names(self.tmp, base, head), ["b.txt"])
        self.assertTrue(common.git_is_ancestor(self.tmp, base, head))
        self.assertFalse(common.git_is_ancestor(self.tmp, head, base))
        self.assertEqual(common.git_porcelain(self.tmp, ["b.txt"]), [])

    def test_hook_io(self):
        with mock.patch("sys.stdin", new=__import__("io").StringIO('{"a": 1}')):
            self.assertEqual(common.read_stdin_json(), {"a": 1})
        with mock.patch("sys.stdin", new=__import__("io").StringIO("[1]")):
            self.assertEqual(common.read_stdin_json(), {})
        with mock.patch("sys.stdin", new=__import__("io").StringIO("")):
            self.assertEqual(common.read_stdin_json(), {})
        buf = __import__("io").StringIO()
        with mock.patch("sys.stdout", new=buf):
            common.emit(None)
            common.emit({})
            common.emit({"x": 1})
        self.assertEqual(json.loads(buf.getvalue()), {"x": 1})

    def test_dirs_of_and_unique(self):
        self.assertEqual(common.dirs_of(["lib/a.py", "lib/b.py", "qa/x.py", "root.py"]), [".", "lib", "qa"])
        self.assertEqual(common.unique(["a", "b", "a", "c", "b"]), ["a", "b", "c"])

    def test_forge_error_default_code(self):
        e = common.ForgeError("refused")
        self.assertEqual(e.code, common.EXIT_REFUSED)
        self.assertEqual(str(e), "refused")
        self.assertEqual(common.ForgeError("bad", common.EXIT_INVALID).code, 4)


class NextTaskIdTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="forge-ids-")
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", self.tmp]))
        self.paths = common.Paths(self.tmp)

    def test_first_id(self):
        self.assertEqual(common.next_task_id(self.paths), "T-0001")

    def test_max_over_tasks_archive_and_history(self):
        os.makedirs(os.path.join(self.paths.tasks, "T-0003"))
        os.makedirs(os.path.join(self.paths.tasks, "not-a-task"))
        self.assertEqual(common.next_task_id(self.paths), "T-0004")
        os.makedirs(os.path.join(self.paths.archive, "T-0010"))
        self.assertEqual(common.next_task_id(self.paths), "T-0011")
        common.append_jsonl(self.paths.history, {"id": "T-0020"})
        common.append_jsonl(self.paths.history, {"id": "garbage"})
        self.assertEqual(common.next_task_id(self.paths), "T-0021")

    def test_five_digit_ids(self):
        os.makedirs(os.path.join(self.paths.tasks, "T-10000"))
        self.assertEqual(common.next_task_id(self.paths), "T-10001")


class ConstantsTests(unittest.TestCase):
    def test_constants_mirror_schemas(self):
        schemas = os.path.join(helpers.PAYLOAD, ".forge", "schemas")

        def load(name):
            with open(os.path.join(schemas, name), encoding="utf-8") as f:
                return json.load(f)

        status = load("status.json")
        self.assertEqual(tuple(status["enums"]["task.phase"]), common.PHASES)
        self.assertEqual(tuple(status["enums"]["task.steps[].status"]), common.STEP_STATUSES)
        self.assertEqual(tuple(status["enums"]["task.class"]), common.CLASSES)
        handoff = load("handoff.json")
        self.assertEqual(tuple(handoff["mandatory_headings"]), common.HANDOFF_MANDATORY_HEADINGS)
        self.assertEqual(tuple(handoff["short_headings"]), common.HANDOFF_SHORT_HEADINGS)
        self.assertEqual(tuple(handoff["status"]), common.HANDOFF_STATUSES)
        verdict = load("verdict.json")
        self.assertEqual(tuple(verdict["headings"]), common.VERDICT_HEADINGS)
        self.assertEqual(tuple(verdict["tags"]), common.VERDICT_TAGS)
        plan = load("plan.json")
        self.assertEqual(tuple(plan["headings"]["M"]), common.PLAN_HEADINGS_M)
        self.assertEqual(tuple(plan["headings"]["W_L"]), common.PLAN_HEADINGS_FULL)
        self.assertEqual(tuple(plan["headings"]["S_X_inline"]), common.PLAN_HEADINGS_INLINE)
        self.assertEqual(common.MAX_DIGEST, 3000)
        self.assertEqual(common.MAX_ADDITIONAL_CONTEXT, 9800)


if __name__ == "__main__":
    unittest.main()
