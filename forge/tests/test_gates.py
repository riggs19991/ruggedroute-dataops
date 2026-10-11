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

    def test_usage(self):
        self.assertEqual(self.gate()[0], common.EXIT_USAGE)
        self.assertEqual(self.gate("--plan")[0], common.EXIT_USAGE)
        self.assertEqual(self.gate("--handoff", self.tid, "01")[0], common.EXIT_USAGE)   # neither --from-file nor --from-stdin


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

    def test_tdd_needs_red_before_green(self):
        self.seed(tdd=True, expected_fail_first=[LIB_UNIT])
        now = int(time.time())
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now)
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        self.assert_defect(self.handoff(text), "green only", mentions="tdd")
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now - 20, expect_fail=True,
                                     results=[{"name": "lib-unit", "cmd": LIB_UNIT, "exit": 1, "dur_s": 0.1, "tail": "FAIL"}])
        self.assert_valid(self.handoff(text), "red then green")

    def test_tdd_green_before_red_is_not_enough(self):
        self.seed(tdd=True, expected_fail_first=[LIB_UNIT])
        now = int(time.time())
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now - 20)
        self.repo.write_check_record(self.tid, "01", self.AGENT, ts=now, expect_fail=True,
                                     results=[{"name": "lib-unit", "cmd": LIB_UNIT, "exit": 1, "dur_s": 0.1, "tail": "FAIL"}])
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        self.assert_defect(self.handoff(text), "red after green")

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


if __name__ == "__main__":
    unittest.main()
