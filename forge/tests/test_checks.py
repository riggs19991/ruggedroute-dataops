"""Tests for forgelib.checks / forge-check (MODULE-API §5; design §5.7 record shape, §7 gate 3)."""
import json
import os
import re
import unittest

import helpers
from helpers import LAYER_TESTS, LIB_UNIT, Repo, common, make_step, make_task


class CheckTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = Repo.create()
        self.addCleanup(self.repo.cleanup)
        self.tid = "T-0001"

    def check(self, *args):
        return self.repo.run_cli("forge-check", *args)

    def records(self, step=None):
        files = self.repo.check_files(self.tid)
        if step:
            files = [f for f in files if f.startswith(step + "-")]
        return [(f, self.repo.read_json(f".forge/tasks/{self.tid}/checks/{f}")) for f in files]

    def lines(self, out, prefix="FORGE_CHECK "):
        return [l for l in out.splitlines() if l.startswith(prefix)]

    def seed_T(self):
        self.repo.seed_status(task=make_task(self.tid, "T", "execute", scope=["lib/mod.py"], files=["lib/mod.py"], creates=[]))

    def seed_M(self, brief=None, plan=None, status_over=None):
        self.repo.write_brief(self.tid, "01", **(brief or {}))
        self.repo.write_plan(self.tid, "M", **(plan or {}))
        step = make_step("01", self.tid, status="running", attempts=1, started_by="cli",
                         started_at="2026-10-11T00:00:00Z", started_ts=1_760_000_000, base=self.repo.head())
        over = {"steps": [step]}
        over.update(status_over or {})
        self.repo.seed_status(task=make_task(self.tid, "M", "execute", **over))


class RunTests(CheckTestCase):
    def test_main_step_runs_always_entries_and_writes_record(self):
        self.seed_T()
        code, out, err = self.check(self.tid, "main")
        self.assertEqual(code, 0, err + out)
        # the unmatched paths: entry is either filtered out (MODULE-API §5) or reported skipped (design §5.7)
        lines = [l for l in self.lines(out) if "exit=skipped" not in l]
        self.assertEqual(len(lines), 1, out)
        m = re.match(r"FORGE_CHECK name=lib-unit exit=0 dur=([0-9.]+)s cmd=(.*)$", lines[0])
        self.assertIsNotNone(m, lines[0])
        self.assertEqual(m.group(2), LIB_UNIT)
        summary = self.lines(out, "FORGE_CHECK_SUMMARY")
        self.assertEqual(len(summary), 1)
        self.assertIn("pass=1", summary[0])
        self.assertIn("fail=0", summary[0])
        self.assertIn("skipped=", summary[0])
        recs = self.records("main")
        self.assertEqual(len(recs), 1)
        name, rec = recs[0]
        self.assertRegex(name, r"^main-\d+-unknown\.json$")
        self.assertEqual(rec["agent_id"], "unknown")
        self.assertEqual(rec["task"], self.tid)
        self.assertEqual(rec["step"], "main")
        self.assertIs(rec["expect_fail"], False)
        self.assertIsInstance(rec["ts"], int)
        self.assertIn("session_id", rec)
        self.assertIs(rec["ok"], True)
        self.assertIsNone(rec["ratchet"])
        result = rec["results"][0]
        self.assertEqual(result["name"], "lib-unit")
        self.assertEqual(result["cmd"], LIB_UNIT)
        self.assertEqual(result["exit"], 0)
        self.assertIsInstance(result["dur_s"], (int, float))
        self.assertIn("tail", result)
        self.assertLessEqual(len(result["tail"].splitlines()), 15)

    def test_agent_flag_sets_agent_id_directly(self):
        self.seed_T()
        code, out, err = self.check(self.tid, "main", "--agent", "agent_x")
        self.assertEqual(code, 0, err)
        name, rec = self.records("main")[0]
        self.assertTrue(name.endswith("-agent_x.json"), name)
        self.assertEqual(rec["agent_id"], "agent_x")

    def test_skipped_entry_when_exists_path_is_missing(self):
        self.repo.write("layers/foo/x.py", "X = 1\n")
        self.repo.commit_all("fixture: layer foo")
        self.repo.write("layers/foo/x.py", "X = 2\n")   # changed under layers/foo, no tests dir
        self.repo.seed_status(task=make_task(self.tid, "T", "execute", scope=["layers/foo/x.py"], files=["layers/foo/x.py"], creates=[]))
        code, out, err = self.check(self.tid, "main")
        self.assertEqual(code, 0, err + out)
        skipped = [l for l in self.lines(out) if "name=layer-tests" in l]
        self.assertEqual(len(skipped), 1, out)
        self.assertIn("exit=skipped", skipped[0])
        self.assertIn("pass=1", self.lines(out, "FORGE_CHECK_SUMMARY")[0])
        self.assertIn("skipped=1", self.lines(out, "FORGE_CHECK_SUMMARY")[0])
        rec = self.records("main")[0][1]
        entry = [r for r in rec["results"] if r["name"] == "layer-tests"][0]
        self.assertEqual(entry["status"], "skipped")
        self.assertTrue(entry["why"])
        self.assertEqual(entry["cmd"], LAYER_TESTS.replace("{layer}", "foo"), "{layer} substituted from the changed path")
        self.assertIs(rec["ok"], True, "skipped never fails the run")

    def test_layer_entry_runs_when_tests_exist(self):
        self.repo.write("layers/foo/x.py", "X = 1\n")
        self.repo.write("layers/foo/tests/__init__.py", "")
        self.repo.write("layers/foo/tests/test_x.py", "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_x(self):\n        self.assertTrue(True)\n")
        self.repo.commit_all("fixture: layer foo with tests")
        self.repo.write("layers/foo/x.py", "X = 2\n")
        self.repo.seed_status(task=make_task(self.tid, "T", "execute", scope=["layers/foo/**"], files=["layers/foo/x.py"], creates=[]))
        code, out, err = self.check(self.tid, "main")
        self.assertEqual(code, 0, err + out)
        ran = [l for l in self.lines(out) if "name=layer-tests" in l]
        self.assertEqual(len(ran), 1, out)
        self.assertIn("exit=0", ran[0])
        self.assertIn("layers/foo/tests", ran[0])

    def test_paths_entry_absent_or_skipped_when_nothing_matches(self):
        self.seed_T()
        code, out, err = self.check(self.tid, "main")
        self.assertEqual(code, 0, err)
        rec = self.records("main")[0][1]
        ran = [r for r in rec["results"] if r["name"] == "layer-tests" and r.get("status") != "skipped"]
        self.assertEqual(ran, [], "a paths:<glob> entry never runs when no changed path matches")

    def test_failing_command_is_exit_1_and_ok_false(self):
        self.seed_M(brief={"checks": [LIB_UNIT, "false"]})
        code, out, err = self.check(self.tid, "01")
        self.assertEqual(code, common.EXIT_DEFECTS, out)
        fail = [l for l in self.lines(out) if "cmd=false" in l]
        self.assertEqual(len(fail), 1, out)
        self.assertIn("exit=1", fail[0])
        self.assertIn("fail=1", self.lines(out, "FORGE_CHECK_SUMMARY")[0])
        rec = self.records("01")[0][1]
        self.assertIs(rec["ok"], False)
        self.assertEqual(rec["step"], "01")

    def test_expect_fail_marks_the_record_but_ok_stays_honest(self):
        self.seed_M(brief={"checks": ["false"]})
        code, out, err = self.check(self.tid, "01", "--expect-fail")
        self.assertEqual(code, common.EXIT_DEFECTS)
        rec = self.records("01")[0][1]
        self.assertIs(rec["expect_fail"], True)
        self.assertIs(rec["ok"], False, "ok = every non-skipped result exited 0, regardless of expect_fail")

    def test_brief_checks_are_unioned_and_deduplicated(self):
        self.seed_M(brief={"checks": [LIB_UNIT, "python3 -c 'print(7)'"]})
        code, out, err = self.check(self.tid, "01")
        self.assertEqual(code, 0, err + out)
        cmds = [l.split("cmd=", 1)[1] for l in self.lines(out)]
        self.assertEqual(cmds.count(LIB_UNIT), 1, cmds)
        self.assertIn("python3 -c 'print(7)'", cmds)
        rec = self.records("01")[0][1]
        self.assertEqual(len([r for r in rec["results"] if r["cmd"] == LIB_UNIT]), 1)
        printed = [r for r in rec["results"] if r["cmd"] == "python3 -c 'print(7)'"][0]
        self.assertIn("7", printed["tail"])

    def test_brief_checks_run_even_when_a_verify_entry_is_skipped(self):
        self.repo.write("layers/foo/x.py", "X = 1\n")
        self.repo.commit_all("fixture: layer foo")
        self.repo.write("layers/foo/x.py", "X = 2\n")
        self.seed_M(brief={"allowed_paths": ["layers/foo/**"], "checks": ["true"]},
                    status_over={"steps": [make_step("01", self.tid, status="running", attempts=1, started_by="cli",
                                                     started_at="2026-10-11T00:00:00Z", started_ts=1_760_000_000,
                                                     allowed_paths=["layers/foo/**"])]})
        code, out, err = self.check(self.tid, "01")
        self.assertEqual(code, 0, err + out)
        self.assertTrue([l for l in self.lines(out) if "cmd=true" in l and "exit=0" in l], out)
        self.assertTrue([l for l in self.lines(out) if "name=layer-tests" in l and "exit=skipped" in l], out)

    def test_only_filters_by_name(self):
        self.seed_M(brief={"checks": ["python3 -c 'print(7)'"]})
        code, out, err = self.check(self.tid, "01", "--only", "lib-unit")
        self.assertEqual(code, 0, err + out)
        self.assertEqual(len(self.lines(out)), 1, out)
        self.assertIn("name=lib-unit", self.lines(out)[0])

    def test_step_changed_set_is_limited_to_allowed_paths(self):
        # layers/foo changes outside the step's allowed_paths do not trigger the layer entry
        self.repo.write("layers/foo/x.py", "X = 1\n")
        self.repo.commit_all("fixture: layer foo")
        self.repo.write("layers/foo/x.py", "X = 2\n")
        self.seed_M()
        code, out, err = self.check(self.tid, "01")
        self.assertEqual(code, 0, err + out)
        rec = self.records("01")[0][1]
        ran = [r for r in rec["results"] if r["name"] == "layer-tests" and r.get("status") != "skipped"]
        self.assertEqual(ran, [])

    def test_only_paths_overrides_the_changed_set(self):
        self.repo.write("layers/foo/x.py", "X = 1\n")
        self.repo.commit_all("fixture: layer foo")
        self.seed_M()
        code, out, err = self.check(self.tid, "01", "--only-paths", "layers/foo/**")
        self.assertEqual(code, 0, err + out)
        self.assertTrue([l for l in self.lines(out) if "name=layer-tests" in l], out)

    def test_usage_errors(self):
        self.assertEqual(self.check()[0], common.EXIT_USAGE)
        self.assertEqual(self.check(self.tid)[0], common.EXIT_USAGE)
        self.assertEqual(self.check(self.tid, "01", "--bogus")[0], common.EXIT_USAGE)
        self.assertEqual(self.check(self.tid, "01", "--cmd")[0], common.EXIT_USAGE)
        self.assertEqual(self.check(self.tid, "01", "--cmd", "")[0], common.EXIT_USAGE)
        self.assertEqual(self.check(self.tid, "01", "--cmd", "true", "--only", "lib-unit")[0], common.EXIT_USAGE)
        self.assertEqual(self.check(self.tid, "01", "--cmd", "true", "--baseline")[0], common.EXIT_USAGE)

    def test_ids_are_sanitised_before_anything_is_written(self):
        """Review #31: <step> and --agent are path components of the record file."""
        self.seed_T()
        before = helpers.tree_hashes(self.repo.path(".forge"))
        bad = [(self.tid, "../../../evil"), (self.tid, "main", "--agent", "../x"), (self.tid, "main", "--agent", "a/b"),
               (self.tid, "ma in"), (self.tid, "main", "--agent", "x" * 65), ("T-1", "main"), ("../T-0001", "main"),
               (self.tid, "main", "--agent", "human"), (self.tid, "..")]
        for args in bad:
            code, out, err = self.check(*args)
            self.assertEqual(code, common.EXIT_USAGE, (args, out, err))
            self.assertNotIn("FORGE_CHECK_RECORD", out)
        self.assertEqual(helpers.tree_hashes(self.repo.path(".forge")), before, "nothing written anywhere")
        from forgelib import checks
        with self.assertRaises(common.ForgeError) as cm:
            checks.run_checks(self.repo.paths, self.tid, "../x")
        self.assertEqual(cm.exception.code, common.EXIT_USAGE)
        with self.assertRaises(common.ForgeError):
            checks.run_checks(self.repo.paths, self.tid, "main", agent_id="../x")
        code, out, err = self.check(self.tid, "main", "--agent", "agent_b1.v2-x_y")
        self.assertEqual(code, 0, err)

    def test_cmd_runs_one_command_from_the_repo_root(self):
        """Review #20: `--cmd '<command>'` records a single command (verifier/builder convenience)."""
        self.seed_M(brief={"checks": [LIB_UNIT]})
        code, out, err = self.check(self.tid, "01", "--cmd", "pwd && echo marker-42")
        self.assertEqual(code, 0, err + out)
        self.assertEqual(len(self.lines(out)), 1, "exactly the one command, not the planned list")
        self.assertIn("name=cmd", self.lines(out)[0])
        self.assertIn("cmd=pwd && echo marker-42", self.lines(out)[0])
        name, rec = self.records("01")[0]
        self.assertEqual([r["cmd"] for r in rec["results"]], ["pwd && echo marker-42"])
        self.assertEqual(rec["results"][0]["name"], "cmd")
        self.assertEqual(rec["results"][0]["exit"], 0)
        tail = rec["results"][0]["tail"].splitlines()
        self.assertEqual(os.path.realpath(tail[0]), os.path.realpath(self.repo.root), "runs from the repo root")
        self.assertEqual(tail[-1], "marker-42")
        self.assertIs(rec["ok"], True)
        self.assertEqual(rec["step"], "01")
        code, out, err = self.check(self.tid, "01", "--cmd=false", "--expect-fail")
        self.assertEqual(code, common.EXIT_DEFECTS)
        rec = [r for _, r in self.records("01") if r["results"][0]["cmd"] == "false"][0]
        self.assertIs(rec["expect_fail"], True)
        self.assertIs(rec["ok"], False)
        code, out, err = self.check(self.tid, "main", "--cmd", "true", "--agent", "agent_v1")
        self.assertEqual(code, 0, err)
        self.assertTrue(self.records("main")[0][0].endswith("-agent_v1.json"))

    def test_step_run_includes_the_briefs_dod_checks(self):
        """Review #20: a numbered step's forge-check runs the plan-meta DoD checks of the brief's dod[] ids."""
        dod = [{"id": "DoD-1", "criterion": "WHEN a THE SYSTEM SHALL b", "check": LIB_UNIT},
               {"id": "DoD-2", "criterion": "WHEN c THE SYSTEM SHALL d", "check": "python3 -c 'print(42)'"},
               {"id": "DoD-3", "criterion": "WHEN e THE SYSTEM SHALL f", "check": "python3 -c 'print(99)'"},
               {"id": "DoD-4", "criterion": "WHEN g THE SYSTEM SHALL h", "check": "external", "external": {"what": "w", "how": "h"}}]
        self.seed_M(brief={"checks": [LIB_UNIT], "dod": ["DoD-1", "DoD-2", "DoD-4"]}, plan={"dod": dod})
        code, out, err = self.check(self.tid, "01")
        self.assertEqual(code, 0, err + out)
        rec = self.records("01")[0][1]
        names = [(r["name"], r["cmd"]) for r in rec["results"] if r.get("status") != "skipped"]
        self.assertIn(("dod:DoD-2", "python3 -c 'print(42)'"), names)
        self.assertEqual([c for _, c in names].count(LIB_UNIT), 1, "DoD-1's command is deduplicated against verify/checks")
        self.assertFalse([n for n, _ in names if n == "dod:DoD-3"], "DoD-3 is not this step's")
        self.assertFalse([n for n, _ in names if n == "dod:DoD-4"], "external checks never run")
        code, out, err = self.check(self.tid, "01", "--only", "lib-unit")
        self.assertEqual(len(self.lines(out)), 1, "--only <verify name> runs no DoD check")
        code, out, err = self.check(self.tid, "01", "--only", "dod")
        self.assertEqual([l for l in self.lines(out) if "name=dod:DoD-2" in l and "exit=0" in l] != [], True, out)
        self.assertFalse([l for l in self.lines(out) if "name=brief" in l], "--only dod runs no brief check")

    def test_tail_is_last_15_lines(self):
        self.seed_M(brief={"checks": ["seq 1 40"]})
        code, out, err = self.check(self.tid, "01")
        self.assertEqual(code, 0, err)
        rec = self.records("01")[0][1]
        tail = [r for r in rec["results"] if r["cmd"] == "seq 1 40"][0]["tail"].splitlines()
        self.assertEqual(len(tail), 15)
        self.assertEqual(tail[-1].strip(), "40")


class BaselineAndRatchetTests(CheckTestCase):
    def test_baseline_prints_json_and_runs_nothing(self):
        self.seed_M()
        code, out, err = self.check(self.tid, "plan", "--baseline")
        self.assertEqual(code, 0, err + out)
        self.assertNotIn("FORGE_CHECK ", out)
        base = json.loads(out.strip().splitlines()[-1])
        self.assertEqual(base["files"], 3)      # lib/test_mod.py, lib/test_util.py, lib/test_shared.py
        self.assertEqual(base["tests"], 3)      # one `def test_` each
        self.assertTrue(base["recorded_at"].endswith("Z"))
        self.assertEqual(self.records(), [], "--baseline writes no record")

    def _ratchet_setup(self, may_edit_tests=False, baseline=None):
        base = baseline or {"files": 3, "tests": 3, "recorded_at": "2026-10-11T00:00:00Z"}
        self.seed_M(brief={"may_edit_tests": may_edit_tests, "allowed_paths": ["lib/**"]}, plan={"test_baseline": base})

    def test_ratchet_pass_when_nothing_lost(self):
        self._ratchet_setup()
        code, out, err = self.check(self.tid, "01", "--ratchet")
        self.assertEqual(code, 0, err + out)
        rec = self.records("01")[0][1]
        self.assertEqual(rec["ratchet"]["status"], "PASS")
        self.assertEqual(rec["ratchet"]["baseline_tests"], 3)
        self.assertEqual(rec["ratchet"]["now_tests"], 3)
        self.assertEqual(rec["ratchet"]["deleted_test_files"], [])

    def test_ratchet_fail_on_deleted_test_file(self):
        self._ratchet_setup()
        self.repo.rm("lib/test_util.py")
        code, out, err = self.check(self.tid, "01", "--ratchet")
        rec = self.records("01")[0][1]
        self.assertEqual(rec["ratchet"]["status"], "FAIL")
        self.assertIn("lib/test_util.py", rec["ratchet"]["deleted_test_files"])
        self.assertEqual(rec["ratchet"]["now_tests"], 2)
        self.assertTrue([l for l in out.splitlines() if "RATCHET" in l and "FAIL" in l], out)

    def test_ratchet_fail_on_lower_count(self):
        self._ratchet_setup()
        self.repo.write("lib/test_util.py", "import unittest\n")   # file kept, test removed
        code, out, err = self.check(self.tid, "01", "--ratchet")
        rec = self.records("01")[0][1]
        self.assertEqual(rec["ratchet"]["status"], "FAIL")
        self.assertEqual(rec["ratchet"]["now_tests"], 2)

    def test_ratchet_tolerates_may_edit_tests(self):
        self._ratchet_setup(may_edit_tests=True)
        self.repo.rm("lib/test_util.py")
        code, out, err = self.check(self.tid, "01", "--ratchet")
        rec = self.records("01")[0][1]
        self.assertNotEqual(rec["ratchet"]["status"], "FAIL")
        self.assertIn("lib/test_util.py", rec["ratchet"]["deleted_test_files"])

    def test_ratchet_unknown_without_baseline(self):
        self.seed_M(plan={"extra_meta": {"test_baseline": None}})
        code, out, err = self.check(self.tid, "01", "--ratchet")
        rec = self.records("01")[0][1]
        self.assertEqual(rec["ratchet"]["status"], "UNKNOWN")

    def test_ratchet_pass_when_tests_grow(self):
        self._ratchet_setup()
        self.repo.write("lib/test_more.py", "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_more(self):\n        pass\n")
        code, out, err = self.check(self.tid, "01", "--ratchet")
        rec = self.records("01")[0][1]
        self.assertEqual(rec["ratchet"]["status"], "PASS")
        self.assertEqual(rec["ratchet"]["now_tests"], 4)


class PassingRecordTests(CheckTestCase):
    """Review #59: an empty record is `ok: true` by definition but proves nothing."""

    def test_record_is_passing(self):
        from forgelib import checks
        green = {"name": "a", "cmd": "true", "exit": 0, "dur_s": 0.1, "tail": ""}
        red = {"name": "b", "cmd": "false", "exit": 1, "dur_s": 0.1, "tail": ""}
        skipped = {"name": "c", "cmd": "x", "status": "skipped", "why": "exists missing"}
        self.assertFalse(checks.record_is_passing({"ok": True, "results": []}), "empty")
        self.assertFalse(checks.record_is_passing({"ok": True, "results": [skipped]}), "skipped only")
        self.assertFalse(checks.record_is_passing({"ok": False, "results": [green, red]}), "ok false")
        self.assertFalse(checks.record_is_passing({"ok": "true", "results": [green]}), "ok must be the boolean")
        self.assertFalse(checks.record_is_passing(None))
        self.assertFalse(checks.record_is_passing({"results": [green]}), "no ok")
        self.assertTrue(checks.record_is_passing({"ok": True, "results": [skipped, green]}))
        self.assertTrue(checks.record_is_passing({"ok": True, "results": [green], "expect_fail": False}))

    def test_empty_verify_record_is_ok_but_not_passing_and_warns(self):
        binding = dict(helpers.BINDING)
        binding["verify"] = []
        self.repo.write_json(".forge/binding.json", binding)
        self.seed_T()
        code, out, err = self.check(self.tid, "main")
        self.assertEqual(code, 0, err)
        self.assertIn("pass=0 fail=0", out)
        self.assertIn("WARN", err)
        self.assertIn("not a passing record", err)
        from forgelib import checks
        rec = self.records("main")[0][1]
        self.assertIs(rec["ok"], True, "§2.7: ok = every non-skipped result exited 0 (vacuously)")
        self.assertFalse(checks.record_is_passing(rec))
        code, out, err = self.check(self.tid, "main", "--cmd", LIB_UNIT)
        self.assertEqual(code, 0, err)
        self.assertNotIn("WARN", err)
        self.assertTrue(checks.record_is_passing(self.records("main")[0][1]) or
                        checks.record_is_passing(self.records("main")[-1][1]), "--cmd gives a stack-unknown install a real record")


if __name__ == "__main__":
    unittest.main()
