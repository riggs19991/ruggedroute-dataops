"""Tests for forgelib.gates / forge-gate (MODULE-API §4; design §5.5 handoff rules, §5.6 verdict rules, §7 gate 0)."""
import time
import unittest

import helpers
from helpers import LIB_UNIT, Repo, common, make_step, make_task


class GateTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = Repo.create()
        self.addCleanup(self.repo.cleanup)
        self.tid = "T-0001"

    def gate(self, *args, stdin=None):
        return self.repo.run_cli("forge-gate", *args, stdin=stdin)

    def assert_valid(self, result, hint=""):
        code, out, err = result
        self.assertEqual(code, 0, f"{hint}: defects={out!r} err={err!r}")
        self.assertEqual(out.strip(), "", f"{hint}: a valid artifact prints no defect lines")

    def assert_defect(self, result, hint="", mentions=None):
        code, out, err = result
        self.assertEqual(code, common.EXIT_DEFECTS, f"{hint}: expected exit 1, got {code}; out={out!r} err={err!r}")
        self.assertTrue(out.strip(), f"{hint}: one defect per line expected on stdout")
        if mentions:
            self.assertIn(mentions.lower(), out.lower(), f"{hint}: defect should mention {mentions!r}: {out!r}")


class PlanGateTests(GateTestCase):
    def test_valid_m_plan(self):
        self.repo.write_brief(self.tid)
        self.repo.write_plan(self.tid, "M")
        self.assert_valid(self.gate("--plan", self.tid))

    def test_missing_plan_is_a_defect(self):
        self.assert_defect(self.gate("--plan", self.tid), "no plan")

    def test_missing_mandatory_heading(self):
        self.repo.write_brief(self.tid)
        self.repo.write_plan(self.tid, "M", headings=["Steps", "Validation Criteria", "Routing"])   # no Rollback
        self.assert_defect(self.gate("--plan", self.tid), "no Rollback", mentions="Rollback")

    def test_wrong_schema(self):
        self.repo.write_brief(self.tid)
        self.repo.write_plan(self.tid, "M", extra_meta={"schema": "forge/plan/1"})
        self.assert_defect(self.gate("--plan", self.tid), "schema")

    def test_m_with_two_steps(self):
        self.repo.write_brief(self.tid, "01", allowed_paths=["lib/mod.py"])
        self.repo.write_brief(self.tid, "02", allowed_paths=["lib/util.py"])
        self.repo.write_plan(self.tid, "M", steps=[{"id": "01"}, {"id": "02"}])
        self.assert_defect(self.gate("--plan", self.tid), "M two steps")

    def test_missing_brief_and_mismatched_brief_step(self):
        self.repo.write_plan(self.tid, "M")
        self.assert_defect(self.gate("--plan", self.tid), "brief missing", mentions="brief")
        self.repo.write_brief(self.tid, "01", extra_meta={"step": "02"})
        self.assert_defect(self.gate("--plan", self.tid), "brief step mismatch")

    def test_empty_dod(self):
        self.repo.write_brief(self.tid)
        self.repo.write_plan(self.tid, "M", dod=[])
        self.assert_defect(self.gate("--plan", self.tid), "dod empty", mentions="dod")

    def test_inline_mode_with_steps_and_single_without(self):
        self.repo.write_brief(self.tid)
        self.repo.write_plan(self.tid, "M", mode="inline")
        self.assert_defect(self.gate("--plan", self.tid), "inline with steps")
        self.repo.write_plan(self.tid, "M", steps=[], mode="single")
        self.assert_defect(self.gate("--plan", self.tid), "single without steps")

    def test_red_ok_until_must_point_forward(self):
        for i, d in enumerate(("pkg1", "pkg2", "pkg3"), start=1):
            self.repo.write_brief(self.tid, f"0{i}", allowed_paths=[f"{d}/**"], checks=["true"])
        steps = [{"id": "01", "red_ok_until": "03"}, {"id": "02"}, {"id": "03"}]
        self.repo.write_plan(self.tid, "L", steps=steps)
        self.assert_valid(self.gate("--plan", self.tid), "L forward red_ok_until")
        steps = [{"id": "01"}, {"id": "02"}, {"id": "03", "red_ok_until": "01"}]
        self.repo.write_plan(self.tid, "L", steps=steps)
        self.assert_defect(self.gate("--plan", self.tid), "backwards red_ok_until", mentions="red_ok")

    def test_inline_plan_for_s(self):
        self.repo.write_plan(self.tid, "S", allowed_paths=["lib/mod.py"])
        self.assert_valid(self.gate("--plan", self.tid), "S inline")
        self.repo.write_plan(self.tid, "S", allowed_paths=["lib/mod.py"], headings=["Rollback"])
        self.assert_defect(self.gate("--plan", self.tid), "S missing Validation Criteria")

    def test_expected_fail_first_must_be_a_subset_of_checks(self):
        """Review #19: forge-check runs checks[] only, so a red/green pair can only exist for checks[] commands."""
        self.repo.write_brief(self.tid, checks=[LIB_UNIT], tdd=True, expected_fail_first=["pytest lib/test_new.py -q"])
        self.repo.write_plan(self.tid, "M")
        self.assert_defect(self.gate("--plan", self.tid), "expected_fail_first not in checks", mentions="pytest lib/test_new.py -q")
        self.repo.write_brief(self.tid, checks=[LIB_UNIT, "pytest lib/test_new.py -q"], tdd=True,
                              expected_fail_first=["pytest lib/test_new.py -q"])
        self.assert_valid(self.gate("--plan", self.tid), "subset")

    def test_usage(self):
        self.assertEqual(self.gate()[0], common.EXIT_USAGE)
        self.assertEqual(self.gate("--plan")[0], common.EXIT_USAGE)
        self.assertEqual(self.gate("--handoff", self.tid, "01")[0], common.EXIT_USAGE)   # neither --from-file nor --from-stdin
        # review #31: ids are validated before anything is read
        self.assertEqual(self.gate("--plan", "../../x")[0], common.EXIT_USAGE)
        self.assertEqual(self.gate("--handoff", self.tid, "../01", "--from-stdin", stdin="x")[0], common.EXIT_USAGE)
        self.assertEqual(self.gate("--verdict", "T-1", "01", "--from-stdin", stdin="x")[0], common.EXIT_USAGE)
        self.assertEqual(self.gate("--verdict", self.tid, "01", "--from-stdin", "--agent", "a/b", stdin="x")[0], common.EXIT_USAGE)


class HandoffGateTests(GateTestCase):
    """design §5.5 rules, one by one. The step is running and bound to agent_b1."""

    AGENT = "agent_b1"
    ALLOWED = ["lib/mod.py", "lib/util.py", "lib/extra.py"]

    def seed(self, tdd=False, expected_fail_first=None, checks=None, red_ok_until=None, status_over=None):
        self.repo.write_brief(self.tid, "01", allowed_paths=self.ALLOWED, checks=checks, tdd=tdd,
                              expected_fail_first=expected_fail_first)
        self.repo.write_plan(self.tid, "M")
        step = make_step("01", self.tid, status="running", attempts=1, agent_id=self.AGENT, started_by="cli",
                         started_at="2026-10-11T00:00:00Z", started_ts=1_760_000_000, base=self.repo.head(),
                         red_ok_until=red_ok_until, allowed_paths=self.ALLOWED)
        self.repo.seed_status(task=make_task(self.tid, "M", "execute", steps=[step], **(status_over or {})))
        self.repo.bind_agent(self.AGENT, self.tid, "01")

    def handoff(self, text, *flags):
        return self.gate("--handoff", self.tid, "01", "--from-stdin", "--agent", self.AGENT, *flags, stdin=text)

    def test_valid_done_handoff(self):
        self.seed()
        now = int(time.time())
        self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", ts=now - 10, kind="source", file="lib/mod.py")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now)
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        self.assert_valid(self.handoff(text), "valid DONE")

    def test_missing_mandatory_heading(self):
        self.seed()
        self.repo.write_check_record(self.tid, "01", self.AGENT)
        text = self.repo.write_report_md(self.tid, "01", "DONE", [], headings=common.HANDOFF_SHORT_HEADINGS)
        self.assert_defect(self.handoff(text), "no Gotchas heading", mentions="Gotchas")

    def test_missing_or_invalid_json_block(self):
        self.seed()
        self.repo.write_check_record(self.tid, "01", self.AGENT)
        self.assert_defect(self.handoff(self.repo.write_report_md(self.tid, "01", json_obj=None)), "no json")
        bad = self.repo.handoff_json(self.tid, "01")
        bad["schema"] = "forge/handoff/1"
        self.assert_defect(self.handoff(self.repo.write_report_md(self.tid, "01", json_obj=bad)), "old schema")
        bad = self.repo.handoff_json(self.tid, "01")
        del bad["files_changed"]
        self.assert_defect(self.handoff(self.repo.write_report_md(self.tid, "01", json_obj=bad)), "no files_changed")
        bad = self.repo.handoff_json(self.tid, "01", status="FINISHED")
        self.assert_defect(self.handoff(self.repo.write_report_md(self.tid, "01", json_obj=bad)), "bad status")
        bad = self.repo.handoff_json(self.tid, "02")
        self.assert_defect(self.handoff(self.repo.write_report_md(self.tid, "01", json_obj=bad)), "wrong step")

    def test_files_changed_must_be_inside_allowed_paths(self):
        self.seed()
        self.repo.write_check_record(self.tid, "01", self.AGENT)
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py", "qa/other.py"])
        self.assert_defect(self.handoff(text), "outside allowed_paths", mentions="qa/other.py")

    def test_source_edits_must_be_declared(self):
        self.seed()
        now = int(time.time())
        self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", ts=now - 10, kind="source", file="lib/util.py")
        self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", ts=now - 9, kind="meta", file=".forge/tasks/T-0001/notes.md")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now)
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        self.assert_defect(self.handoff(text), "undeclared source edit", mentions="lib/util.py")
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py", "lib/util.py"])
        self.assert_valid(self.handoff(text), "meta edits never count")

    def test_other_agents_edits_do_not_count(self):
        self.seed()
        now = int(time.time())
        self.repo.add_evidence(self.tid, "agent_other", "forge-builder", "edit", ts=now - 10, kind="source", file="lib/util.py")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now)
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        self.assert_valid(self.handoff(text), "sibling agent's edit")

    def test_tree_changes_inside_allowed_paths_must_be_declared(self):
        self.seed()
        self.repo.write("lib/util.py", "def twice(x):\n    return x * 2\n")       # modified, tracked
        self.repo.write("lib/extra.py", "NEW = 1\n")                                # new, untracked
        self.repo.write("README.md", "# dirt outside the unit\n")                  # outside allowed_paths: ignored
        self.repo.write(".forge/tasks/T-0001/scratch.md", "meta\n")                # .forge/** never counts
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=int(time.time()) + 1)
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/util.py"])
        self.assert_defect(self.handoff(text), "untracked lib/extra.py undeclared", mentions="lib/extra.py")
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/util.py", "lib/extra.py"])
        self.assert_valid(self.handoff(text), "both declared; README.md and .forge/** ignored")

    def test_done_requires_a_green_record_newer_than_the_last_source_edit(self):
        self.seed()
        now = int(time.time())
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        self.assert_defect(self.handoff(text), "no record at all", mentions=LIB_UNIT.split()[0])
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now - 100)
        self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", ts=now - 10, kind="source", file="lib/mod.py")
        self.assert_defect(self.handoff(text), "record older than the last source edit")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now - 5,
                                     results=[{"name": "lib-unit", "cmd": LIB_UNIT, "exit": 1, "dur_s": 0.1, "tail": "FAIL"}])
        self.assert_defect(self.handoff(text), "newer but red")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now)
        self.assert_valid(self.handoff(text), "newer and green")

    def test_record_by_another_agent_does_not_count(self):
        self.seed()
        self.repo.write_check_record(self.tid, "01", "agent_other", ts=int(time.time()))
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        self.assert_defect(self.handoff(text), "record by another agent")

    def test_done_with_concerns_follows_the_same_evidence_rule(self):
        self.seed()
        text = self.repo.write_report_md(self.tid, "01", "DONE_WITH_CONCERNS", ["lib/mod.py"])
        self.assert_defect(self.handoff(text), "DONE_WITH_CONCERNS without record")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=int(time.time()))
        self.assert_valid(self.handoff(text), "DONE_WITH_CONCERNS with record")

    def test_blocked_and_needs_context_need_no_records(self):
        self.seed()
        for status in ("BLOCKED", "NEEDS_CONTEXT"):
            text = self.repo.write_report_md(self.tid, "01", status, ["lib/mod.py"])
            self.assert_valid(self.handoff(text), status)

    def test_red_ok_accepts_any_exit(self):
        self.seed(red_ok_until="02")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=int(time.time()),
                                     results=[{"name": "lib-unit", "cmd": LIB_UNIT, "exit": 1, "dur_s": 0.1, "tail": "FAIL"}])
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        self.assert_valid(self.handoff(text, "--red-ok"), "red_ok via flag")
        self.assert_valid(self.handoff(text), "red_ok from the step's red_ok_until")

    TDD_ALLOWED = ["lib/mod.py", "lib/util.py", "lib/extra.py", "lib/test_mod.py"]

    def seed_tdd(self, red_record_by=None, red_ts=None):
        """A tdd step whose worker wrote the test (evidence: a source edit of lib/test_mod.py)."""
        self.repo.write_brief(self.tid, "01", allowed_paths=self.TDD_ALLOWED, checks=[LIB_UNIT], tdd=True,
                              expected_fail_first=[LIB_UNIT], may_edit_tests=True)
        self.repo.write_plan(self.tid, "M")
        step = make_step("01", self.tid, status="running", attempts=1, agent_id=self.AGENT, started_by="cli",
                         started_at="2026-10-11T00:00:00Z", started_ts=1_760_000_000, base=self.repo.head(),
                         allowed_paths=self.TDD_ALLOWED)
        self.repo.seed_status(task=make_task(self.tid, "M", "execute", steps=[step]))
        self.repo.bind_agent(self.AGENT, self.tid, "01")
        now = int(time.time())
        self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", ts=now - 60, kind="source", file="lib/test_mod.py")
        if red_record_by:
            self.repo.write_check_record(self.tid, "01", red_record_by, ts=red_ts if red_ts is not None else now - 40,
                                         expect_fail=True,
                                         results=[{"name": "lib-unit", "cmd": LIB_UNIT, "exit": 1, "dur_s": 0.1, "tail": "FAIL"}])
        return now

    def test_tdd_needs_red_before_green(self):
        now = self.seed_tdd()
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now)
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py", "lib/test_mod.py"])
        self.assert_defect(self.handoff(text), "green only", mentions="tdd")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now - 20, expect_fail=True,
                                     results=[{"name": "lib-unit", "cmd": LIB_UNIT, "exit": 1, "dur_s": 0.1, "tail": "FAIL"}])
        self.assert_valid(self.handoff(text), "red then green")

    def test_tdd_green_before_red_is_not_enough(self):
        now = self.seed_tdd()
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now - 20)
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now, expect_fail=True,
                                     results=[{"name": "lib-unit", "cmd": LIB_UNIT, "exit": 1, "dur_s": 0.1, "tail": "FAIL"}])
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py", "lib/test_mod.py"])
        self.assert_defect(self.handoff(text), "red after green")

    def test_tdd_red_by_an_earlier_worker_counts_for_a_retry(self):
        """Review #27: a retry worker on an already-green tree inherits attempt 1's red record."""
        now = self.seed_tdd(red_record_by="agent_attempt1")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now)        # the retry's own green
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py", "lib/test_mod.py"])
        self.assert_valid(self.handoff(text), "another agent's red before this agent's green")
        # another agent's GREEN never substitutes for this agent's own green
        self.repo.rm(f".forge/tasks/{self.tid}/checks/01-{now}-{self.AGENT}.json")
        self.repo.write_check_record(self.tid, "01", "agent_attempt1", ts=now)
        self.assert_defect(self.handoff(text), "no green by this agent", mentions=LIB_UNIT.split()[0])

    def test_tdd_binds_only_a_worker_that_touched_a_test_file(self):
        """Review #27: a worker whose evidence shows no test-file edit has no red to show."""
        self.seed(tdd=True, expected_fail_first=[LIB_UNIT])
        now = int(time.time())
        self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", ts=now - 30, kind="source", file="lib/mod.py")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now)        # green only, no red anywhere
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        self.assert_valid(self.handoff(text), "no test file touched: tdd rule does not bind")
        self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", ts=now - 20, kind="source", file="lib/test_mod.py")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now + 1)
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py", "lib/test_mod.py"])
        code, out, err = self.handoff(text)
        self.assertEqual(code, common.EXIT_DEFECTS, out)
        self.assertIn("tdd", out)

    def test_touched_test_file_falls_back_to_a_path_heuristic(self):
        from forgelib import gates
        self.seed()
        self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", kind="source", file="lib/mod.py")
        self.assertFalse(gates.touched_test_file(self.repo.paths, self.tid, self.AGENT))
        self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", kind="source", file="lib/test_mod.py")
        self.assertTrue(gates.touched_test_file(self.repo.paths, self.tid, self.AGENT), "binding.test_globs match")
        binding = self.repo.read_json(".forge/binding.json")
        binding["test_globs"] = []
        self.repo.write_json(".forge/binding.json", binding)
        self.assertTrue(gates.touched_test_file(self.repo.paths, self.tid, self.AGENT), "heuristic: lib/test_mod.py")
        self.repo.rm(f".forge/tasks/{self.tid}/evidence.jsonl")
        for f in ("app/src/test/Foo.kt", "web/foo.spec.ts", "pkg/tests/x.py", "pkg/x_test.go"):
            self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", kind="source", file=f)
            self.assertTrue(gates.touched_test_file(self.repo.paths, self.tid, self.AGENT), f)
            self.repo.rm(f".forge/tasks/{self.tid}/evidence.jsonl")
        self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", kind="source", file="web/foo.ts")
        self.assertFalse(gates.touched_test_file(self.repo.paths, self.tid, self.AGENT))

    def test_every_brief_check_needs_a_record(self):
        self.seed(checks=[LIB_UNIT, "python3 -c 'print(1)'"])
        now = int(time.time())
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now)
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        self.assert_defect(self.handoff(text), "second check unrecorded", mentions="print(1)")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now + 1, results=[
            {"name": "lib-unit", "cmd": LIB_UNIT, "exit": 0, "dur_s": 0.1, "tail": "OK"},
            {"name": "brief-1", "cmd": "python3 -c 'print(1)'", "exit": 0, "dur_s": 0.1, "tail": "1"}])
        self.assert_valid(self.handoff(text), "both recorded")

    def test_from_file(self):
        self.seed()
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=int(time.time()))
        self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"], path="draft.md")
        self.assert_valid(self.gate("--handoff", self.tid, "01", "--from-file", "draft.md", "--agent", self.AGENT))

    def test_bound_agent_resolved_when_flag_absent(self):
        self.seed()
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        code, out, err = self.gate("--handoff", self.tid, "01", "--from-stdin", stdin=text)
        self.assertEqual(code, common.EXIT_DEFECTS, "the one bound agent's rules apply: no record -> defect")
        self.assertNotIn("WARN", err)

    def test_warn_when_no_agent_can_be_resolved(self):
        self.seed()
        self.repo.rm(f".forge/.runtime/agents/{self.AGENT}.json")
        self.repo.write_check_record(self.tid, "01", "agent_someone", ts=int(time.time()))
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        code, out, err = self.gate("--handoff", self.tid, "01", "--from-stdin", stdin=text)
        self.assertIn("WARN", err)
        self.assertEqual(code, 0, out)

    def test_drafts_are_never_tree_changes_and_never_committed(self):
        """Review #17: `.forge/tasks/<id>/drafts/**` is a pre-validation scratch area."""
        from forgelib import gates
        self.seed()
        self.repo.write("lib/util.py", "def twice(x):\n    return x * 2\n")
        self.repo.write(f".forge/tasks/{self.tid}/drafts/{self.AGENT}-handoff.md", "draft\n")
        self.repo.write(f".forge/tasks/{self.tid}/report-01.md", "report\n")
        wide = self.ALLOWED + [".forge/**"]
        self.assertEqual(gates.tree_changed(self.repo.paths, wide), ["lib/util.py"])
        self.assertTrue(gates.is_draft_path(f".forge/tasks/{self.tid}/drafts/x.md"))
        self.assertFalse(gates.is_draft_path(f".forge/tasks/{self.tid}/report-01.md"))
        specs = gates.commit_pathspecs(self.repo.paths, self.ALLOWED, self.tid)
        self.assertEqual(specs[0], "lib/util.py")
        self.assertIn(f".forge/tasks/{self.tid}/", specs)
        self.assertEqual(specs[-1], gates.drafts_exclude_pathspec(self.tid))
        code, out = self.repo.git("add", "-A", "--", *specs)
        self.assertEqual(code, 0, out)
        staged = self.repo.git("diff", "--cached", "--name-only")[1].split()
        self.assertIn("lib/util.py", staged)
        self.assertIn(f".forge/tasks/{self.tid}/report-01.md", staged)
        self.assertFalse([p for p in staged if "/drafts/" in p], staged)
        # the task-agnostic form (for close: `git add -A -- .forge/ <exclude>`)
        self.repo.git("reset", "-q")
        code, out = self.repo.git("add", "-A", "--", ".forge/", gates.drafts_exclude_pathspec())
        self.assertEqual(code, 0, out)
        staged = self.repo.git("diff", "--cached", "--name-only")[1].split()
        self.assertIn(f".forge/tasks/{self.tid}/report-01.md", staged)
        self.assertFalse([p for p in staged if "/drafts/" in p], staged)

    def test_task_level_handoff(self):
        self.seed()
        full = self.repo.write_report_md(self.tid, "task", "DONE", ["lib/mod.py"])
        self.assert_valid(self.gate("--handoff", self.tid, "task", "--from-stdin", "--task-level", stdin=full), "full task-level")
        short = self.repo.write_report_md(self.tid, "task", "DONE", ["lib/mod.py"], short=True)
        self.assert_defect(self.gate("--handoff", self.tid, "task", "--from-stdin", "--task-level", stdin=short), "M needs full form")
        self.assert_valid(self.gate("--handoff", self.tid, "task", "--from-stdin", "--task-level", "--short", stdin=short), "--short")
        wrong = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        self.assert_defect(self.gate("--handoff", self.tid, "task", "--from-stdin", "--task-level", stdin=wrong), "step must be task")


class VerdictGateTests(GateTestCase):
    """design §5.6 rules, one by one. The step is verifying; the verifier is agent_v1."""

    VERIFIER = "agent_v1"

    def seed(self, dod=None, brief_dod=("DoD-1",), step_status="verifying"):
        self.repo.write_brief(self.tid, "01", dod=list(brief_dod))
        self.repo.write_plan(self.tid, "M", dod=dod)
        commit = self.repo.head()
        step = make_step("01", self.tid, status=step_status, attempts=1, agent_id="agent_b1", started_by="cli",
                         started_at="2026-10-11T00:00:00Z", started_ts=1_760_000_000, base=commit, commit=commit)
        self.repo.seed_status(task=make_task(self.tid, "M", "execute", steps=[step]))
        self.repo.agent_record(self.VERIFIER, "forge-verifier", task=self.tid, step="01")

    def verdict(self, text):
        return self.gate("--verdict", self.tid, "01", "--from-stdin", "--agent", self.VERIFIER, stdin=text)

    def test_valid_pass(self):
        self.seed()
        self.repo.write_check_record(self.tid, "01", self.VERIFIER)
        self.assert_valid(self.verdict(self.repo.write_verdict_md(self.tid, "01")), "valid PASS")

    def test_headings_required(self):
        self.seed()
        self.repo.write_check_record(self.tid, "01", self.VERIFIER)
        text = self.repo.write_verdict_md(self.tid, "01", headings=common.VERDICT_HEADINGS[:-1])
        self.assert_defect(self.verdict(text), "no Confidence note", mentions="Confidence")

    def test_json_shape(self):
        self.seed()
        self.repo.write_check_record(self.tid, "01", self.VERIFIER)
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", json_obj=None)), "no json")
        bad = self.repo.verdict_json(self.tid, "01")
        bad["schema"] = "forge/verdict/1"
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", json_obj=bad)), "schema")
        bad = self.repo.verdict_json(self.tid, "01", verdict="MAYBE")
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", json_obj=bad)), "verdict enum")
        bad = self.repo.verdict_json(self.tid, "01")
        del bad["ratchet"]
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", json_obj=bad)), "missing ratchet")

    def test_every_dod_id_exactly_once(self):
        dod = [{"id": "DoD-1", "criterion": "WHEN a THE SYSTEM SHALL b", "check": LIB_UNIT},
               {"id": "DoD-2", "criterion": "WHEN c THE SYSTEM SHALL d", "check": "true"}]
        self.seed(dod=dod, brief_dod=("DoD-1", "DoD-2"))
        self.repo.write_check_record(self.tid, "01", self.VERIFIER, results=[
            {"name": "a", "cmd": LIB_UNIT, "exit": 0, "dur_s": 0.1, "tail": "OK"},
            {"name": "b", "cmd": "true", "exit": 0, "dur_s": 0.1, "tail": ""}])
        one = [{"id": "DoD-1", "result": "PASS", "cmd": LIB_UNIT, "exit": 0}]
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", criteria=one)), "DoD-2 missing", mentions="DoD-2")
        dup = one + one + [{"id": "DoD-2", "result": "PASS", "cmd": "true", "exit": 0}]
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", criteria=dup)), "DoD-1 twice")
        extra = one + [{"id": "DoD-2", "result": "PASS", "cmd": "true", "exit": 0}, {"id": "DoD-9", "result": "PASS", "cmd": "true", "exit": 0}]
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", criteria=extra)), "unknown DoD-9")
        both = one + [{"id": "DoD-2", "result": "PASS", "cmd": "true", "exit": 0}]
        self.assert_valid(self.verdict(self.repo.write_verdict_md(self.tid, "01", criteria=both)), "both once")

    def test_criterion_shape(self):
        self.seed()
        self.repo.write_check_record(self.tid, "01", self.VERIFIER)
        crit = [{"id": "DoD-1", "result": "PASS", "cmd": LIB_UNIT, "exit": "0"}]
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", criteria=crit)), "string exit")
        crit = [{"id": "DoD-1", "result": "OK", "cmd": LIB_UNIT, "exit": 0}]
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", criteria=crit)), "result enum")
        crit = [{"id": "DoD-1", "result": "PASS", "exit": 0}]
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", criteria=crit)), "no cmd")

    def test_pass_implies_everything_green(self):
        self.seed()
        self.repo.write_check_record(self.tid, "01", self.VERIFIER, results=[
            {"name": "a", "cmd": LIB_UNIT, "exit": 0, "dur_s": 0.1, "tail": "OK"},
            {"name": "a", "cmd": LIB_UNIT, "exit": 1, "dur_s": 0.1, "tail": "FAIL"}])
        failed = [{"id": "DoD-1", "result": "FAIL", "cmd": LIB_UNIT, "exit": 1}]
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", "PASS", criteria=failed)), "PASS with FAIL criterion")
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", "PASS", scope_check="FAIL")), "PASS with scope FAIL")
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", "PASS", ratchet="FAIL")), "PASS with ratchet FAIL")
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", "PASS", blocking=["x"])), "PASS with blocking")
        self.assert_valid(self.verdict(self.repo.write_verdict_md(self.tid, "01", "FAIL", criteria=failed, blocking=["suite red"])), "honest FAIL")

    def test_cited_command_needs_a_record_by_this_verifier(self):
        self.seed()
        text = self.repo.write_verdict_md(self.tid, "01")
        self.assert_defect(self.verdict(text), "no record")
        self.repo.write_check_record(self.tid, "01", "agent_b1")   # the builder's record is not the verifier's
        self.assert_defect(self.verdict(text), "builder's record")
        self.repo.write_check_record(self.tid, "01", self.VERIFIER)
        self.assert_valid(self.verdict(text), "verifier's record")

    def test_external_criterion_needs_a_human_record(self):
        dod = [{"id": "DoD-1", "criterion": "WHEN a THE SYSTEM SHALL b", "check": LIB_UNIT},
               {"id": "DoD-2", "criterion": "WHEN deployed THE SYSTEM SHALL serve", "check": "external",
                "external": {"what": "serves", "how": "curl"}}]
        self.seed(dod=dod, brief_dod=("DoD-1", "DoD-2"))
        self.repo.write_check_record(self.tid, "01", self.VERIFIER)
        crit = [{"id": "DoD-1", "result": "PASS", "cmd": LIB_UNIT, "exit": 0},
                {"id": "DoD-2", "result": "PASS", "cmd": "external", "exit": 0}]
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", "PASS", criteria=crit)), "external PASS without attest")
        unknown = [crit[0], {"id": "DoD-2", "result": "UNKNOWN", "cmd": "external", "exit": 0}]
        self.assert_valid(self.verdict(self.repo.write_verdict_md(self.tid, "01", "UNKNOWN", criteria=unknown)), "external UNKNOWN")
        self.repo.write_human_record(self.tid, "01", "DoD-2")
        self.assert_valid(self.verdict(self.repo.write_verdict_md(self.tid, "01", "PASS", criteria=crit)), "external attested")

    def test_tags_subset(self):
        self.seed()
        self.repo.write_check_record(self.tid, "01", self.VERIFIER)
        self.assert_defect(self.verdict(self.repo.write_verdict_md(self.tid, "01", tags=["made-up-tag"])), "unknown tag", mentions="made-up-tag")
        self.assert_valid(self.verdict(self.repo.write_verdict_md(self.tid, "01", tags=["not-double-checked"])), "known tag")

    def test_inline_task_uses_plan_dod_and_main_agent(self):
        self.repo.write_plan(self.tid, "S", allowed_paths=["lib/mod.py"])
        self.repo.seed_status(task=make_task(self.tid, "S", "execute", scope=["lib/mod.py"], files=["lib/mod.py"], creates=[]))
        text = self.repo.write_verdict_md(self.tid, "main", range_="worktree")
        code, out, err = self.gate("--verdict", self.tid, "main", "--from-stdin", "--agent", "agent_v1", stdin=text)
        self.assertEqual(code, common.EXIT_DEFECTS, "no record by the verifier yet")
        self.repo.write_check_record(self.tid, "main", "agent_v1")
        self.assert_valid(self.gate("--verdict", self.tid, "main", "--from-stdin", "--agent", "agent_v1", stdin=text), "inline PASS")

    def test_dod_check_outside_brief_checks_is_citable(self):
        """Review #20: a DoD command absent from checks[] gets a record from the verifier's own forge-check run
        (plan_commands runs the step's DoD checks) or from `forge-check --cmd`."""
        dod = [{"id": "DoD-1", "criterion": "WHEN a THE SYSTEM SHALL b", "check": LIB_UNIT},
               {"id": "DoD-2", "criterion": "WHEN c THE SYSTEM SHALL d", "check": "python3 -c 'print(42)'"}]
        self.seed(dod=dod, brief_dod=("DoD-1", "DoD-2"))
        crit = [{"id": "DoD-1", "result": "PASS", "cmd": LIB_UNIT, "exit": 0},
                {"id": "DoD-2", "result": "PASS", "cmd": "python3 -c 'print(42)'", "exit": 0}]
        text = self.repo.write_verdict_md(self.tid, "01", criteria=crit)
        code, out, err = self.repo.run_cli("forge-check", self.tid, "01", "--agent", self.VERIFIER)
        self.assertEqual(code, 0, err + out)
        self.assert_valid(self.verdict(text), "the verifier's forge-check run recorded the DoD command")
        for f in self.repo.check_files(self.tid):
            self.repo.rm(f".forge/tasks/{self.tid}/checks/{f}")
        code, out, err = self.repo.run_cli("forge-check", self.tid, "01", "--agent", self.VERIFIER, "--cmd", "python3 -c 'print(42)'")
        self.assertEqual(code, 0, err + out)
        self.assert_defect(self.verdict(text), "DoD-1 still unrecorded", mentions="DoD-1")
        code, out, err = self.repo.run_cli("forge-check", self.tid, "01", "--agent", self.VERIFIER, "--cmd", LIB_UNIT)
        self.assertEqual(code, 0, err + out)
        self.assert_valid(self.verdict(text), "both cited commands recorded with --cmd")


class AgentResolutionTests(GateTestCase):
    """Reviews #13/#25: forge-gate without --agent resolves per mode and never to another agent's records."""

    def seed_step(self):
        self.repo.write_brief(self.tid, "01")
        self.repo.write_plan(self.tid, "M")
        commit = self.repo.head()
        step = make_step("01", self.tid, status="verifying", attempts=1, agent_id="agent_b1", started_by="cli",
                         started_at="2026-10-11T00:00:00Z", started_ts=1_760_000_000, base=commit, commit=commit)
        self.repo.seed_status(task=make_task(self.tid, "M", "execute", steps=[step]))
        self.repo.bind_agent("agent_b1", self.tid, "01")

    def test_verdict_never_resolves_to_the_builders_record(self):
        self.seed_step()
        self.repo.write_check_record(self.tid, "01", "agent_b1")            # only the builder ran checks
        text = self.repo.write_verdict_md(self.tid, "01")
        code, out, err = self.gate("--verdict", self.tid, "01", "--from-stdin", stdin=text)
        self.assertEqual(code, 0, "no verifier record at all: agent-scoped rules skipped, with a WARN")
        self.assertIn("WARN", err)
        self.repo.agent_record("agent_v1", "forge-verifier", task=self.tid, verify_step="01")
        code, out, err = self.gate("--verdict", self.tid, "01", "--from-stdin", stdin=text)
        self.assertEqual(code, common.EXIT_DEFECTS, "resolved to the verifier, which has no record: defect")
        self.assertIn("agent_v1", err)
        self.assertNotIn("WARN", err)
        self.assertIn("agent_v1", out)
        self.repo.write_check_record(self.tid, "01", "agent_v1")
        self.assert_valid(self.gate("--verdict", self.tid, "01", "--from-stdin", stdin=text), "verifier's own record")
        # two verifier records for the step: ambiguous -> WARN and skip
        self.repo.agent_record("agent_v2", "forge-verifier", task=self.tid, verify_step="01")
        code, out, err = self.gate("--verdict", self.tid, "01", "--from-stdin", stdin=text)
        self.assertEqual(code, 0)
        self.assertIn("WARN", err)

    def test_inline_verdict_resolves_to_the_verifier_of_main(self):
        self.repo.write_plan(self.tid, "S", allowed_paths=["lib/mod.py"])
        self.repo.seed_status(task=make_task(self.tid, "S", "execute", scope=["lib/mod.py"], files=["lib/mod.py"], creates=[]))
        self.repo.write_check_record(self.tid, "main", "main")              # the architect's own run
        text = self.repo.write_verdict_md(self.tid, "main", range_="worktree")
        code, out, err = self.gate("--verdict", self.tid, "main", "--from-stdin", stdin=text)
        self.assertEqual(code, 0, "no verifier record: skipped with WARN, never 'main'")
        self.assertIn("WARN", err)
        self.repo.agent_record("agent_v1", "forge-verifier", task=self.tid, verify_step="main")
        code, out, err = self.gate("--verdict", self.tid, "main", "--from-stdin", stdin=text)
        self.assertEqual(code, common.EXIT_DEFECTS, "the architect's record is not the verifier's")
        self.repo.write_check_record(self.tid, "main", "agent_v1")
        self.assert_valid(self.gate("--verdict", self.tid, "main", "--from-stdin", stdin=text), "verifier of main")

    def test_inline_handoff_uses_main_and_counts_unknown_records(self):
        """Review #13: a record written by forge-check outside a hook (stamped unknown) counts for step main."""
        self.repo.write_plan(self.tid, "S", allowed_paths=["lib/mod.py"])
        self.repo.seed_status(task=make_task(self.tid, "S", "execute", scope=["lib/mod.py"], files=["lib/mod.py"], creates=[]))
        text = self.repo.write_report_md(self.tid, "main", "DONE", ["lib/mod.py"])
        code, out, err = self.gate("--handoff", self.tid, "main", "--from-stdin", stdin=text)
        self.assertEqual(code, common.EXIT_DEFECTS, "no record yet")
        self.assertIn("by main", out)
        self.assertNotIn("WARN", err)
        self.repo.write_check_record(self.tid, "main", "unknown", ts=int(time.time()))
        self.assert_valid(self.gate("--handoff", self.tid, "main", "--from-stdin", stdin=text), "unknown counts as main")
        # but never for a numbered step
        from forgelib import gates
        self.repo.write_check_record(self.tid, "01", "unknown")
        self.assertEqual(gates.check_records(self.repo.paths, self.tid, "01", "main"), [])
        self.assertEqual(gates.check_records(self.repo.paths, self.tid, "main", "agent_v1"), [])

    def test_handoff_resolves_to_the_bound_worker_only(self):
        self.seed_step()
        self.repo.agent_record("agent_v1", "forge-verifier", task=self.tid, verify_step="01")
        self.repo.write_check_record(self.tid, "01", "agent_v1", ts=int(time.time()))
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        code, out, err = self.gate("--handoff", self.tid, "01", "--from-stdin", stdin=text)
        self.assertEqual(code, common.EXIT_DEFECTS, "the verifier's record is not the builder's")
        self.assertIn("agent_b1", err)
        self.assertNotIn("WARN", err)


class BashHeuristicTests(unittest.TestCase):
    """looks_mutating / ro_allowed live in gates.py (MODULE-API §6; design §13.3 regexes)."""

    def setUp(self):
        from forgelib import gates
        self.gates = gates

    def test_looks_mutating(self):
        yes = ["sed -i 's/a/b/' lib/mod.py", "echo x > lib/mod.py", "cat a | tee lib/mod.py", "rm lib/mod.py",
               "mv a b", "cp a b", "git checkout -- lib/mod.py", "git reset --hard", "python3 -c 'open(\"x\",\"w\")'",
               "node -e 'x'", "cat <<EOF > x\nhi\nEOF", "ls && rm -rf build", "chmod +x x"]
        for cmd in yes:
            self.assertTrue(self.gates.looks_mutating(cmd), cmd)
        no = ["git status", "git diff --stat", "git log --oneline -5", "ls -la", "cat lib/mod.py", "pytest -q",
              ".forge/bin/forge-status get digest", "git add -A && git commit -m x", "echo 2>&1 hi", "grep -rn foo lib"]
        for cmd in no:
            self.assertFalse(self.gates.looks_mutating(cmd), cmd)

    def test_ro_allowed(self):
        yes = ["git log --oneline", "git diff HEAD~1", "git show HEAD", "git status --short", "rg foo lib", "grep -rn foo lib",
               "find . -name '*.py'", "ls lib", "cat lib/mod.py", "head -20 lib/mod.py", "tail -5 x", "wc -l x", "jq . x.json",
               "pytest -q", "python3 -m pytest -q", "python3 -m unittest -v", "cd lib && python3 -m unittest -q",
               ".forge/bin/forge-check T-0001 01", ".forge/bin/forge-gate --plan T-0001", ".forge/bin/forge-status get digest",
               "git log | head -3", "cat x; wc -l x"]
        for cmd in yes:
            self.assertTrue(self.gates.ro_allowed(cmd), cmd)
        no = ["echo hi > f", "cat x >> y", "python3 -c 'print(1)'", "node -e 'x'", "sed -i 's/a/b/' x", "tee x",
              "perl -e 'x'", "rm -rf x", "git push origin main", ".forge/bin/forge-status step-done T-0001 01",
              "cat <<EOF\nx\nEOF", "git log && rm x", "ls | tee out"]
        for cmd in no:
            self.assertFalse(self.gates.ro_allowed(cmd), cmd)

    def test_ro_denies_substitution_find_actions_and_output_flags(self):
        """Review #7: every bypass of the allow-list, one by one."""
        no = ["cat $(rm -rf lib)", "cat `rm x`", "echo ${X:=$(rm x)}", "cat <(rm x)", "ls > >(cat)", "cat x | cat >(rm x)",
              "find . -name '*.py' -delete", "find . -exec rm {} \\;", "find . -execdir rm {} \\;", "find . -ok rm {} \\;",
              "find . -okdir rm {} \\;", "find . -name x -fprint lib/mod.py", "find . -fprintf lib/mod.py '%p'", "find . -fls out",
              "git diff --output=lib/mod.py HEAD~1", "git log --output lib/mod.py", "git log \"--output=lib/mod.py\"",
              "git grep -Orm foo", "git grep --open-files-in-pager=rm foo", "sort -o lib/mod.py x", "sort -olib/mod.py x",
              "uniq x lib/mod.py", "ls | xargs rm", "eval 'rm x'", "echo tee", "rg --pre rm foo", "rg --pre-glob '*' foo",
              "find . -name '*.py' \"-delete\"", "ls 1>lib/mod.py", "ls 2>lib/mod.py", "ls &>lib/mod.py", "ls >|lib/mod.py",
              "cat x > \"$f\"", "bash -c 'ls'", "sh -c ls", "git -c core.pager=rm log", "git --git-dir=.git log",
              "git branch -D main", "git stash drop", "GIT_PAGER=rm git log", "env rm x", "exec rm x", "(rm x)", "{ rm x; }",
              "timeout 5 rm x", "timeout 5 timeout 5 rm x", "cat x #; rm y\nrm z", "true &\nrm x", "cat 'x\nrm y"]
        for cmd in no:
            self.assertFalse(self.gates.ro_allowed(cmd), cmd)

    def test_ro_allows_common_read_only_forms(self):
        """Review #51: flags that are not interpreter flags, quoted '>' text, sed -n, awk, git -C, timeout, prefixes."""
        yes = ["grep -c foo lib/mod.py", "grep -e foo -e bar lib", "grep -o 'x' lib/mod.py", "wc -c x", "head -c 10 x",
               "git log --format='%h -> %s'", "grep -rn '=>' lib", "grep -rn \"a > b\" lib", "echo 'x > y'",
               "sed -n 1,5p lib/mod.py", "sed -n '/foo/,/bar/p' x", "sed -n 's/a/b/p' x", "sed -ne '1p' -e '$p' x",
               "sed -En '/x/p' errors.log", "awk '{print $1}' x", "awk -F: '$2 == 1' x", "awk -v n=1 'NR==n' x",
               "python -m pytest -q", "python3.12 -m unittest -q", "python3 -m json.tool x.json", "true", "false",
               "timeout 60 pytest -q", "timeout -k 5 60s python3 -m pytest -q", "timeout 10 .forge/bin/forge-check T-0001 01",
               '"$CLAUDE_PROJECT_DIR"/.forge/bin/forge-check T-0001 01', "$FORGE_ROOT/.forge/bin/forge-status get digest",
               "forge-check T-0001 01", "git -C lib log --oneline", "git --no-pager diff --stat", "git -C . rev-parse HEAD",
               "git stash list", "git describe --tags", "git ls-tree HEAD", "ls 2>/dev/null", "ls 2>&1 | head", "cat < x",
               "cd lib && python3 -m unittest -q | tail -5", "cd lib && python3 -m unittest -q 2>&1; git status",
               "which python3", "realpath lib", "du -sh lib", "cmp a b", "ls lib; true", "git log -5 --stat --no-color",
               ".forge/bin/forge-check T-0001 01 --cmd 'grep -c foo lib/mod.py'", ".forge/bin/forge-status get task.phase",
               ".forge/bin/forge-gate --verdict T-0001 01 --from-file .forge/tasks/T-0001/drafts/agent_v1-verdict.md --agent agent_v1",
               "npm test", "npx jest --ci", "./gradlew :app:testDebugUnitTest", "jq -r '.a | .b' x.json"]
        for cmd in yes:
            self.assertTrue(self.gates.ro_allowed(cmd), cmd)

    def test_ro_sed_and_awk_scripts_that_write_or_execute_are_denied(self):
        no = ["sed -n 'w out' x", "sed -n '1,5w lib/mod.py' x", "sed -n 's/a/b/w out' x", "sed -n 's/a/b/e' x",
              "sed -n '1e rm x' x", "sed -n '/a/{p;w out}' x", "sed -n -f script.sed x", "sed -n --in-place p x",
              "sed 1p x", "sed -i.bak -n p x", "sed -ne 'w out' x", "awk '{system(\"rm x\")}' x",
              "awk '{print > \"lib/mod.py\"}' x", "awk '{print | \"rm x\"}' x", "awk -f prog.awk x", "gawk -l ext 'x'",
              "awk '\"rm x\" | getline' x", "awk '@load \"x\"' x", "sed -n 'y/abc/xyz/' x | sort -o out",
              "awk -F: '$2 > 1' x"]   # a '>' inside an awk program is a redirect or a comparison: refused either way
        for cmd in no:
            self.assertFalse(self.gates.ro_allowed(cmd), cmd)

    def test_ro_prefix_does_not_bless_the_rest_of_the_command(self):
        """Review #7: a binding command prefix covers only its own segment; a redirect on it is still a write."""
        pre = [LIB_UNIT, "pytest -q"]
        self.assertTrue(self.gates.ro_allowed(LIB_UNIT, pre))
        self.assertTrue(self.gates.ro_allowed(LIB_UNIT + " -v", pre))
        self.assertTrue(self.gates.ro_allowed("pytest -q tests/x.py | tail -3", pre))
        self.assertFalse(self.gates.ro_allowed(LIB_UNIT + "; rm -rf lib", pre))
        self.assertFalse(self.gates.ro_allowed(LIB_UNIT + " > lib/mod.py", pre))
        self.assertFalse(self.gates.ro_allowed("pytest -q && rm x", pre))
        self.assertFalse(self.gates.ro_allowed("pytest-cov -q", pre), "prefix needs a word boundary")
        self.assertFalse(self.gates.ro_allowed(".forge/bin/forge-check T-0001 01 --cmd 'rm -rf lib'"), "--cmd is judged too")
        self.assertFalse(self.gates.ro_allowed(".forge/bin/forge-check T-0001 01 --cmd='echo x > lib/mod.py'"))
        self.assertTrue(self.gates.ro_allowed(".forge/bin/forge-check T-0001 01 --cmd 'pytest -q'", pre))

    def test_newline_and_ampersand_are_separators(self):
        """Review #8: a leading `true\\n` or `ls &` never hides the real command."""
        self.assertEqual(self.gates.split_segments("true\nrm -rf lib"), ["true", "rm -rf lib"])
        self.assertEqual(self.gates.split_segments("ls &\nrm x"), ["ls", "rm x"])
        self.assertEqual(self.gates.split_segments("ls & rm x"), ["ls", "rm x"])
        self.assertEqual(self.gates.split_segments("cat x 2>&1 | head"), ["cat x 2>&1", "head"])
        self.assertEqual(self.gates.split_segments("a |& b ; c && d || e"), ["a", "b", "c", "d", "e"])
        self.assertEqual(self.gates.split_segments("ls \\\n -la"), ["ls \\\n -la"], "backslash-newline continues the line")
        for cmd in ("true\nrm -rf lib", "ls &\nrm x", "ls & rm x", "git status\necho x > lib/mod.py", "true\n\nsed -i s/a/b/ x",
                    "git status\ngit -C . reset --hard", "ls\n  git checkout -- lib/mod.py", "echo \"$(rm -rf lib)\"",
                    "echo `rm x`", "ln -s a b", "git restore .", "bash -c 'rm x'"):
            self.assertTrue(self.gates.looks_mutating(cmd), cmd)
        self.assertEqual(self.gates.irreversible_match("true\ngit push origin main", ["git push *"]), "git push *")
        self.assertEqual(self.gates.irreversible_match("ls & git push origin main", ["git push *"]), "git push *")
        self.assertEqual(self.gates.irreversible_match(".forge/bin/forge-check T-0001 01 --cmd 'git push origin main'",
                                                       ["git push *"]), "git push *")
        self.assertIsNone(self.gates.irreversible_match("git log 'git push origin main'", ["git push *"]))

    def test_quoted_separators_and_redirects_are_text(self):
        """Review #18: the idle entry command with free text in --title/--why is one safe segment."""
        cmd = '.forge/bin/forge-status open --title "fix a; rm it > now" --class T --files lib/mod.py --why "because > y | z"'
        self.assertEqual(len(self.gates.split_segments(cmd)), 1)
        self.assertFalse(self.gates.looks_mutating(cmd), cmd)
        cmd = ".forge/bin/forge-status open --title 'a | b' --why 'x; mv y && rm z'"
        self.assertFalse(self.gates.looks_mutating(cmd), cmd)
        self.assertFalse(self.gates.looks_mutating("forge-status close T-0001 --one-line \"x | .forge/tasks/T-0001/checks/a.json\""))
        self.assertFalse(self.gates.looks_mutating("git commit -m 'fix: rm > cp; tee'"))
        self.assertFalse(self.gates.looks_mutating("echo \"a > b\""), "a quoted '>' is text")
        self.assertFalse(self.gates.looks_mutating("grep -rn 'rm -rf' lib"))
        # real separators next to quoted ones still count
        self.assertTrue(self.gates.looks_mutating('.forge/bin/forge-status get digest; rm "a; b"'))
        self.assertTrue(self.gates.looks_mutating("git status && echo 'x' > lib/mod.py"))
        # an unterminated quote falls back to splitting everywhere (fail closed)
        self.assertTrue(self.gates.looks_mutating(".forge/bin/forge-status open --title \"a; rm -rf lib"))
        self.assertFalse(self.gates.ro_allowed("grep 'x lib"))
        masked, balanced = self.gates.mask_quotes("a 'b;c' \"d|$(e)\" \\; f")
        self.assertEqual(masked, "a '___' \"__$(e)\" __ f", "quoted text masked; $( ) stays live")
        self.assertTrue(balanced)
        self.assertFalse(self.gates.mask_quotes("a 'b")[1])

    def test_prefixes_cover_only_their_own_segment_in_looks_mutating(self):
        pre = [LIB_UNIT, "pytest -q", "true"]
        self.assertFalse(self.gates.looks_mutating(LIB_UNIT, pre))
        self.assertFalse(self.gates.looks_mutating(LIB_UNIT + " && pytest -q", pre))
        self.assertFalse(self.gates.looks_mutating("pytest -q tests/x.py | tail -3", pre))
        self.assertTrue(self.gates.looks_mutating(LIB_UNIT + "; rm -rf lib", pre))
        self.assertTrue(self.gates.looks_mutating(LIB_UNIT + " > out.txt", pre))
        self.assertTrue(self.gates.looks_mutating("true\nrm -rf lib", pre))
        self.assertTrue(self.gates.looks_mutating("pytest -q && sed -i s/a/b/ x", pre))
        self.assertFalse(self.gates.looks_mutating("truncate -s 0 x", []) is False, "truncate is mutating")
        self.assertTrue(self.gates.looks_mutating(".forge/bin/forge-check T-0001 main --cmd 'rm -rf lib'"), "--cmd inner")
        self.assertFalse(self.gates.looks_mutating(".forge/bin/forge-check T-0001 main --cmd 'pytest -q'"))


if __name__ == "__main__":
    unittest.main()
