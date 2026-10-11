"""Tests for forgelib.status / forge-status (MODULE-API §3; design §5.1 transition table, §4.3 rules).

Every test drives the real CLI (`.forge/bin/forge-status`) inside a throwaway repo. Where a
precondition needs state that only a long sequence of transitions would produce, the test seeds
STATUS.json directly (shape per MODULE-API §2.1) and restamps it.
"""
import hashlib
import json
import os
import unittest

import helpers
from helpers import LIB_UNIT, Repo, common, make_step, make_task


class StatusTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = Repo.create()
        self.addCleanup(self.repo.cleanup)

    # ------------------------------------------------------------------ helpers
    def open_m(self, title="lib: add extra helper and wire it into mod", files=("lib/mod.py", "lib/util.py"),
               creates=("lib/extra.py",), **kw):
        code, out, err = self.repo.open_task(title, "M", files, creates, **kw)
        self.assertEqual(code, 0, err)
        return self.repo.task()["id"]

    def plan_m(self, task_id, step=None, brief=None, **plan_kw):
        self.repo.write_brief(task_id, "01", **(brief or {}))
        rel = self.repo.write_plan(task_id, "M", steps=[step or {"id": "01"}], **plan_kw)
        return self.repo.forge_status("plan", task_id, "--from", rel)

    def assert_refused(self, result, hint=""):
        code, out, err = result
        self.assertEqual(code, common.EXIT_REFUSED, f"{hint}: expected exit 3, got {code}; out={out!r} err={err!r}")
        self.assertTrue(err.strip(), f"{hint}: a refusal must say why on stderr")
        self.assertEqual(len(err.strip().splitlines()), 1, f"{hint}: one-line refusal expected: {err!r}")

    def status_sha(self):
        with open(self.repo.path(".forge/STATUS.json"), "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()


class IdleAndValidationTests(StatusTestCase):
    def test_idle_status_validates(self):
        code, out, err = self.repo.forge_status("validate")
        self.assertEqual(code, 0, err)

    def test_corrupted_file_is_exit_4(self):
        self.repo.write(".forge/STATUS.json", "{not json at all")
        code, out, err = self.repo.forge_status("validate")
        self.assertEqual(code, common.EXIT_INVALID)
        self.assertTrue(err.strip())
        code, out, err = self.repo.forge_status("get", "digest")
        self.assertEqual(code, common.EXIT_INVALID)

    def test_schema_refusal_on_missing_key_and_bad_enum(self):
        st = helpers.idle_status()
        del st["queue"]
        self.repo.write_json(".forge/STATUS.json", st)
        self.assertEqual(self.repo.forge_status("validate")[0], common.EXIT_INVALID)
        st = helpers.idle_status()
        st["task"] = make_task(phase="flying")
        self.repo.write_json(".forge/STATUS.json", st)
        self.assertEqual(self.repo.forge_status("validate")[0], common.EXIT_INVALID)
        st["task"] = make_task(steps=[make_step(model="claude-opus-5-5")])   # full id, not an alias
        self.repo.write_json(".forge/STATUS.json", st)
        self.assertEqual(self.repo.forge_status("validate")[0], common.EXIT_INVALID)

    def test_open_refused_when_status_invalid(self):
        self.repo.write(".forge/STATUS.json", "{broken")
        code, out, err = self.repo.open_task("lib: tweak", "T", ["lib/mod.py"])
        self.assertEqual(code, common.EXIT_INVALID)

    def test_get_lenient_never_fails(self):
        self.repo.write(".forge/STATUS.json", "{broken")
        code, out, err = self.repo.forge_status("get", "digest", "--lenient")
        self.assertEqual(code, 0, err)
        self.assertTrue(out.strip())
        code, out, err = self.repo.forge_status("get", "summary", "--lenient")
        self.assertEqual(code, 0, err)

    def test_get_digest_idle(self):
        code, out, err = self.repo.forge_status("get", "digest")
        self.assertEqual(code, 0, err)
        self.assertLessEqual(len(out), common.MAX_DIGEST)
        self.assertIn("[full: .forge/STATUS.json]", out)

    def test_get_digest_bounded_with_a_large_task(self):
        steps = [make_step(f"0{i}", title="a long step title " * 10) for i in range(1, 7)]
        task = make_task(cls="L", steps=steps, routing={"mode": "single", "builder": {"agent": "forge-builder-s", "model": "sonnet", "effort": "medium"},
                                                        "verifier": {"agent": "forge-verifier", "model": "sonnet", "effort": "medium"}, "justification": "x" * 500},
                         title="t" * 300, next_action="n" * 600, resume_hint="r" * 2000,
                         evidence=[{"claim": "c" * 200, "command": LIB_UNIT, "exit": 0, "when": "2026-10-11T00:00:00Z", "from": "x"}] * 10,
                         evidence_count=10)
        hist = [{"id": f"T-00{i:02d}", "title": "h" * 100, "class": "S", "outcome": "done", "cost_usd": None,
                 "cost_source": "unknown", "handoff": None, "closed_at": "2026-10-11T00:00:00Z"} for i in range(1, 6)]
        queue = [{"id": f"T-01{i:02d}", "title": "q" * 100, "class_hint": "S"} for i in range(10)]
        self.repo.seed_status(task=task, queue=queue, history=hist)
        code, out, err = self.repo.forge_status("get", "digest")
        self.assertEqual(code, 0, err)
        self.assertLessEqual(len(out), common.MAX_DIGEST)
        self.assertIn("T-0001", out)
        self.assertIn("[full: .forge/STATUS.json]", out)
        self.assertIn("next:", out)

    def test_get_dotted_path_summary_and_next_action(self):
        self.repo.seed_status(task=make_task(next_action="Dispatch forge-builder (opus/medium) on brief-01"))
        code, out, err = self.repo.forge_status("get", "task.phase")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "execute")
        code, out, err = self.repo.forge_status("get", "next_action")
        self.assertEqual(out.strip(), "Dispatch forge-builder (opus/medium) on brief-01")
        code, out, err = self.repo.forge_status("get", "summary")
        self.assertEqual(code, 0, err)
        self.assertIn("Dispatch forge-builder", out)
        self.assertIn("T-0001", out)

    def test_usage_is_exit_2(self):
        self.assertEqual(self.repo.forge_status()[0], common.EXIT_USAGE)
        self.assertEqual(self.repo.forge_status("open", "--title", "x")[0], common.EXIT_USAGE)


class OpenRulesTests(StatusTestCase):
    def test_T_with_more_than_two_files_refused(self):
        self.assert_refused(self.repo.open_task("lib: three files", "T", ["lib/mod.py", "lib/util.py", "lib/shared.py"]), "T>2")
        self.assertIsNone(self.repo.task())

    def test_S_with_risk_hit_refused(self):
        self.assert_refused(self.repo.open_task("rotate the secret key", "S", ["lib/mod.py"]), "S risk word")
        self.assert_refused(self.repo.open_task("lib: tidy uploads", "S", ["lib/mod.py"], ["lib/upload_tool.py"]), "S risk path")
        self.assert_refused(self.repo.open_task("lib: tidy", "T", ["lib/upload_tool.py"]), "T risk path")

    def test_S_size_limits(self):
        self.assert_refused(self.repo.open_task("lib: four files", "S", ["lib/mod.py", "lib/util.py", "lib/shared.py", "lib/x.py"]), "S>3")
        self.assert_refused(self.repo.open_task("three dirs", "S", ["lib/mod.py", "qa/x.py", "layers/y.py"]), "S dirs>2")

    def test_M_with_more_than_ten_files_refused(self):
        files = [f"lib/f{i}.py" for i in range(11)]
        self.assert_refused(self.repo.open_task("lib: eleven files", "M", files), "M>10")
        self.assertIsNone(self.repo.task())

    def test_M_with_more_than_three_dirs_refused(self):
        self.assert_refused(self.repo.open_task("four dirs", "M", ["a/x.py", "b/x.py", "c/x.py", "d/x.py"]), "M dirs>3")

    def test_why_shorter_than_20_chars_refused(self):
        self.assert_refused(self.repo.open_task("lib: tweak", "T", ["lib/mod.py"], why="too short"), "why<20")
        self.assertIsNone(self.repo.task())

    def test_risk_flag_must_agree_with_hits(self):
        # risk R with no hits refused unless --force-risk
        self.assert_refused(self.repo.open_task("lib: tweak", "M", ["lib/mod.py", "lib/util.py", "lib/shared.py"], risk="R"), "R without hits")
        code, out, err = self.repo.open_task("lib: tweak", "M", ["lib/mod.py", "lib/util.py", "lib/shared.py"], (), "R",
                                             "fixture: declared set is small and has no risk hits", "--force-risk")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.repo.task()["risk"], "R")
        self.assertIn("force-risk", self.repo.task()["class_justification"])

    def test_risk_none_with_hits_refused_unless_accepted(self):
        files = ["lib/mod.py", "lib/util.py", "lib/upload_tool.py"]
        self.assert_refused(self.repo.open_task("lib: uploads", "M", files), "none with hits")
        code, out, err = self.repo.open_task("lib: uploads", "M", files, (), "none",
                                             "fixture: declared set is small and has no risk hits",
                                             "--accept-risk-none", "upload_tool is a fixture, not the uploader")
        self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual(task["risk"], "none")
        self.assertTrue(task["signals"]["risk_hits"])
        self.assertIn("accept-risk-none", task["class_justification"])

    def test_second_open_refused_unless_queued(self):
        self.open_m()
        self.assert_refused(self.repo.open_task("another", "S", ["lib/util.py"]), "task already open")
        code, out, err = self.repo.open_task("queued one", "S", ["lib/util.py"], (), "none",
                                             "fixture: declared set is small and has no risk hits", "--queue")
        self.assertEqual(code, 0, err)
        st = self.repo.status()
        self.assertEqual(st["task"]["id"], "T-0001")
        self.assertEqual(len(st["queue"]), 1)
        q = st["queue"][0]
        self.assertEqual(q["id"], "T-0002")
        self.assertEqual(q["title"], "queued one")
        self.assertEqual(q["class_hint"], "S")

    def test_open_T_sets_inline_execute_and_scope(self):
        code, out, err = self.repo.open_task("lib: fix add", "T", ["lib/mod.py"])
        self.assertEqual(code, 0, err)
        self.assertTrue(out.startswith("T-0001"), out)
        self.assertIn("| next:", out)
        st = self.repo.status()
        task = st["task"]
        self.assertEqual(task["id"], "T-0001")
        self.assertEqual(task["class"], "T")
        self.assertEqual(task["phase"], "execute")
        self.assertEqual(task["routing"]["mode"], "inline")
        self.assertEqual(task["steps"], [])
        self.assertEqual(task["plan"], None)
        self.assertEqual(task["size_source"], "declared")
        self.assertEqual(task["scope"], ["lib/mod.py"])
        self.assertEqual(task["signals"]["files"], 1)
        self.assertEqual(task["signals"]["risk_hits"], [])
        self.assertEqual(task["budget"]["cap_usd"], 1)
        self.assertEqual(task["base"], self.repo.head())
        self.assertTrue(self.repo.exists(".forge/tasks/T-0001/signals.json"))
        self.assertIn("open", self.repo.ledger_events())
        self.assertEqual(st["updated_by"]["session_id"], "cli")
        self.assertIn("open", st["updated_by"]["cmd"])
        self.assertEqual(self.repo.read(self.repo.rt("status.sha")).strip(), self.status_sha())

    def test_open_M_goes_to_plan_phase(self):
        self.open_m()
        task = self.repo.task()
        self.assertEqual(task["phase"], "plan")
        self.assertEqual(task["signals"]["files"], 3)
        self.assertEqual(task["signals"]["dirs"], 1)
        self.assertEqual(task["budget"]["cap_usd"], 10)
        self.assertTrue(set(task["files"] + task["creates"]) <= set(task["scope"]))
        self.assertIn("plan", task["next_action"].lower())

    def test_open_removes_dirty_main_and_records_sha(self):
        self.repo.touch(self.repo.rt("dirty-main"))
        self.open_m()
        self.assertFalse(self.repo.exists(self.repo.rt("dirty-main")))
        self.assertEqual(self.repo.read(self.repo.rt("status.sha")).strip(), self.status_sha())


class PlanRulesTests(StatusTestCase):
    def test_plan_refused_outside_plan_phase(self):
        self.repo.open_task("lib: fix add", "T", ["lib/mod.py"])
        self.repo.write_brief("T-0001")
        rel = self.repo.write_plan("T-0001", "M")
        self.assert_refused(self.repo.forge_status("plan", "T-0001", "--from", rel), "T has no plan phase")

    def test_M_plan_with_two_steps_refused(self):
        tid = self.open_m()
        self.repo.write_brief(tid, "01", allowed_paths=["lib/mod.py"])
        self.repo.write_brief(tid, "02", allowed_paths=["lib/util.py"])
        rel = self.repo.write_plan(tid, "M", steps=[{"id": "01"}, {"id": "02"}])
        self.assert_refused(self.repo.forge_status("plan", tid, "--from", rel), "M with 2 steps")
        self.assertEqual(self.repo.task()["phase"], "plan")
        self.assertEqual(self.repo.task()["steps"], [])

    def test_M_plan_happy_imports_routing(self):
        tid = self.open_m()
        code, out, err = self.plan_m(tid)
        self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual(task["phase"], "execute")
        self.assertEqual(task["plan"], f".forge/tasks/{tid}/plan.md")
        self.assertEqual(task["plan_author"], "architect")      # M-small: 3 files, 1 dir, no risk
        self.assertEqual(task["routing"]["mode"], "single")
        self.assertEqual(task["routing"]["builder"], {"agent": "forge-builder", "model": "opus", "effort": "medium"})
        self.assertEqual(task["routing"]["verifier"]["model"], "opus")
        self.assertEqual(len(task["steps"]), 1)
        step = task["steps"][0]
        self.assertEqual(step["status"], "pending")
        self.assertEqual(step["attempts"], 0)
        self.assertEqual(step["brief"], f".forge/tasks/{tid}/brief-01.md")
        self.assertEqual(step["allowed_paths"], ["lib/mod.py", "lib/util.py", "lib/extra.py"])
        self.assertEqual(step["max_tool_calls"], 60)
        self.assertIn("forge-builder", task["next_action"])
        self.assertIn("opus", task["next_action"])

    def test_S_inline_plan(self):
        code, out, err = self.repo.open_task("lib: small change", "S", ["lib/mod.py"])
        self.assertEqual(code, 0, err)
        self.assertEqual(self.repo.task()["phase"], "plan")
        self.assertIsNone(self.repo.task()["plan"])
        rel = self.repo.write_plan("T-0001", "S", allowed_paths=["lib/mod.py"])
        code, out, err = self.repo.forge_status("plan", "T-0001", "--from", rel)
        self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual(task["phase"], "execute")
        self.assertEqual(task["routing"]["mode"], "inline")
        self.assertEqual(task["steps"], [])
        self.assertIn("lib/mod.py", task["scope"])
        self.assertEqual(task["plan"], rel)

    def test_S_plan_with_a_step_refused(self):
        self.repo.open_task("lib: small change", "S", ["lib/mod.py"])
        self.repo.write_brief("T-0001", "01", allowed_paths=["lib/mod.py"])
        rel = self.repo.write_plan("T-0001", "S", steps=[{"id": "01"}], mode="single", allowed_paths=["lib/mod.py"])
        self.assert_refused(self.repo.forge_status("plan", "T-0001", "--from", rel), "S with steps")

    def test_needs_clarification_sets_intake(self):
        tid = self.open_m()
        code, out, err = self.plan_m(tid, needs_clarification=["which bucket receives the output?"])
        self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual(task["phase"], "intake")
        self.assertTrue(task["next_action"].lower().startswith("ask the user"), task["next_action"])

    def test_parallel_downgraded_to_single_without_worktree_isolation(self):
        for d in ("pkg1", "pkg2", "pkg3"):
            self.repo.write(f"{d}/m.py", "X = 1\n")
        self.repo.commit_all("fixture: three packages")
        code, out, err = self.repo.open_task("three independent packages", "L", ["pkg1/m.py", "pkg2/m.py", "pkg3/m.py"])
        self.assertEqual(code, 0, err)
        tid = self.repo.task()["id"]
        steps = []
        for i, d in enumerate(("pkg1", "pkg2", "pkg3"), start=1):
            self.repo.write_brief(tid, f"0{i}", allowed_paths=[f"{d}/**"], checks=["true"])
            steps.append({"id": f"0{i}", "title": f"unit {d}"})
        rel = self.repo.write_plan(tid, "L", steps=steps, mode="parallel")
        code, out, err = self.repo.forge_status("plan", tid, "--from", rel)
        self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual(task["routing"]["mode"], "single")
        self.assertEqual(len(task["steps"]), 3)
        self.assertIn("parallel", self.repo.journal(tid).lower())

    def test_L_with_fewer_than_three_steps_refused(self):
        for d in ("pkg1", "pkg2"):
            self.repo.write(f"{d}/m.py", "X = 1\n")
        self.repo.commit_all("fixture: two packages")
        self.repo.open_task("two packages", "L", ["pkg1/m.py", "pkg2/m.py"])
        tid = self.repo.task()["id"]
        self.repo.write_brief(tid, "01", allowed_paths=["pkg1/**"], checks=["true"])
        self.repo.write_brief(tid, "02", allowed_paths=["pkg2/**"], checks=["true"])
        rel = self.repo.write_plan(tid, "L", steps=[{"id": "01"}, {"id": "02"}])
        self.assert_refused(self.repo.forge_status("plan", tid, "--from", rel), "L<3 steps")

    def test_mechanical_on_mechanic_denied_paths_refused(self):
        for d in ("pkg1", "pkg2"):
            self.repo.write(f"{d}/m.py", "X = 1\n")
        self.repo.commit_all("fixture: packages")
        self.repo.open_task("packages plus shared", "L", ["pkg1/m.py", "pkg2/m.py", "lib/shared.py"])
        tid = self.repo.task()["id"]
        self.repo.write_brief(tid, "01", allowed_paths=["pkg1/**"], checks=["true"])
        self.repo.write_brief(tid, "02", allowed_paths=["pkg2/**"], checks=["true"])
        self.repo.write_brief(tid, "03", allowed_paths=["lib/shared.py"], checks=["true"], owner_agent="forge-mechanic",
                              model="haiku")
        steps = [{"id": "01"}, {"id": "02"},
                 {"id": "03", "agent": "forge-mechanic", "model": "haiku", "effort": "medium", "mechanical": True}]
        rel = self.repo.write_plan(tid, "L", steps=steps)
        self.assert_refused(self.repo.forge_status("plan", tid, "--from", rel), "mechanical on denied path")

    def test_cheaper_tier_requires_tests_present(self):
        # layers/foo has no tests: a sonnet builder for an M step is refused (design §4.3 rule 2)
        for n in ("a", "b", "c"):
            self.repo.write(f"layers/foo/{n}.py", "X = 1\n")
        self.repo.commit_all("fixture: layer without tests")
        code, out, err = self.repo.open_task("layers/foo: refactor", "M", ["layers/foo/a.py", "layers/foo/b.py", "layers/foo/c.py"])
        self.assertEqual(code, 0, err)
        tid = self.repo.task()["id"]
        self.assertFalse(self.repo.task()["signals"]["tests_present"])
        self.repo.write_brief(tid, "01", allowed_paths=["layers/foo/**"], checks=["true"], model="sonnet")
        rel = self.repo.write_plan(tid, "M", steps=[{"id": "01", "model": "sonnet"}])
        self.assert_refused(self.repo.forge_status("plan", tid, "--from", rel), "cheaper tier without tests")

    def test_cheaper_tier_accepted_with_tests_present(self):
        code, out, err = self.repo.open_task("lib: refactor three tested modules", "M", ["lib/mod.py", "lib/util.py", "lib/shared.py"])
        self.assertEqual(code, 0, err)
        tid = self.repo.task()["id"]
        self.assertTrue(self.repo.task()["signals"]["tests_present"])
        self.repo.write_brief(tid, "01", allowed_paths=["lib/mod.py", "lib/util.py", "lib/shared.py"], model="sonnet")
        rel = self.repo.write_plan(tid, "M", steps=[{"id": "01", "model": "sonnet"}])
        code, out, err = self.repo.forge_status("plan", tid, "--from", rel)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.repo.step()["model"], "sonnet")

    def test_risk_floors_builder_and_verifier(self):
        files = ["lib/mod.py", "lib/util.py"]
        code, out, err = self.repo.open_task("lib: tidy uploads", "M", files, ["lib/upload_tool.py"], "R")
        self.assertEqual(code, 0, err)
        tid = self.repo.task()["id"]
        self.assertEqual(self.repo.task()["risk"], "R")
        self.assertEqual(self.repo.task()["budget"]["cap_usd"], 15)   # 10 × risk_multiplier 1.5
        allowed = files + ["lib/upload_tool.py"]
        # forge-builder-s is forbidden under R
        self.repo.write_brief(tid, "01", allowed_paths=allowed, owner_agent="forge-builder-s", model="sonnet", risk="R")
        rel = self.repo.write_plan(tid, "M", risk="R", steps=[{"id": "01", "agent": "forge-builder-s", "model": "sonnet"}])
        self.assert_refused(self.repo.forge_status("plan", tid, "--from", rel), "builder-s under R")
        # forge-builder opus/medium is raised to the fable/low floor; verifier to fable/medium
        self.repo.write_brief(tid, "01", allowed_paths=allowed, risk="R")
        rel = self.repo.write_plan(tid, "M", risk="R", steps=[{"id": "01"}])
        code, out, err = self.repo.forge_status("plan", tid, "--from", rel)
        self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual((task["steps"][0]["model"], task["steps"][0]["effort"]), ("fable", "low"))
        self.assertEqual((task["routing"]["verifier"]["model"], task["routing"]["verifier"]["effort"]), ("fable", "medium"))

    def test_risk_rematched_on_brief_allowed_paths(self):
        # declared set has no hits, but the brief's allowed_paths reach a risk path: builder floor applies
        tid = self.open_m()
        self.repo.write_brief(tid, "01", allowed_paths=["lib/mod.py", "lib/util.py", "lib/extra.py", "secrets/**"])
        rel = self.repo.write_plan(tid, "M")
        code, out, err = self.repo.forge_status("plan", tid, "--from", rel)
        if code == 0:
            task = self.repo.task()
            self.assertEqual(task["risk"], "R")
            self.assertEqual(task["steps"][0]["model"], "fable")
        else:
            self.assert_refused((code, out, err), "risk re-match")

    def test_important_hits_raise_verifier_to_fable(self):
        self.repo.write("lib/live/a.py", "A = 1\n")
        self.repo.write("lib/live/b.py", "B = 1\n")
        self.repo.commit_all("fixture: live module")
        code, out, err = self.repo.open_task("lib/live: tune", "M", ["lib/live/a.py", "lib/live/b.py", "lib/mod.py"])
        self.assertEqual(code, 0, err)
        tid = self.repo.task()["id"]
        self.assertTrue(self.repo.task()["signals"]["important_hits"])
        self.repo.write_brief(tid, "01", allowed_paths=["lib/live/**", "lib/mod.py"])
        rel = self.repo.write_plan(tid, "M")
        code, out, err = self.repo.forge_status("plan", tid, "--from", rel)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.repo.task()["routing"]["verifier"]["model"], "fable")

    def test_verifier_tier_not_below_builder(self):
        tid = self.open_m()
        self.repo.write_brief(tid, "01", model="fable", effort="low")
        rel = self.repo.write_plan(tid, "M", steps=[{"id": "01", "model": "fable", "effort": "low"}],
                                   verifier={"agent": "forge-verifier", "model": "sonnet", "effort": "medium"})
        code, out, err = self.repo.forge_status("plan", tid, "--from", rel)
        if code == 0:
            task = self.repo.task()
            self.assertTrue(common.tier_gte(task["routing"]["verifier"]["model"], task["steps"][0]["model"]))
        else:
            self.assert_refused((code, out, err), "verifier below builder")

    def test_routing_override_applies_to_intersecting_step(self):
        binding = dict(helpers.BINDING)
        binding["routing"] = {"architect_effort": "medium", "m_builder": "opus-medium", "measured": {},
                              "overrides": [{"name": "lib", "paths": ["lib/**"],
                                             "builder": {"agent": "forge-builder", "model": "fable", "effort": "low"},
                                             "min_verifier": "fable"}]}
        self.repo.write_json(".forge/binding.json", binding)
        tid = self.open_m()
        # a plan below the override's tier is either raised to it or refused (design §4.4)
        code, out, err = self.plan_m(tid)
        if code != 0:
            self.assert_refused((code, out, err), "lower tier than override")
            code, out, err = self.plan_m(tid, step={"id": "01", "model": "fable", "effort": "low"},
                                         brief={"model": "fable", "effort": "low"})
            self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual((task["steps"][0]["model"], task["steps"][0]["effort"]), ("fable", "low"))
        self.assertEqual(task["routing"]["verifier"]["model"], "fable")

    def test_plan_refused_when_brief_missing(self):
        tid = self.open_m()
        rel = self.repo.write_plan(tid, "M")   # no brief-01.md
        self.assert_refused(self.repo.forge_status("plan", tid, "--from", rel), "missing brief")


class HappyPathMTests(StatusTestCase):
    """The class M lifecycle end to end (design §3 steps 1-11), asserting every side effect."""

    def test_m_lifecycle(self):
        repo = self.repo
        tid = self.open_m()
        code, out, err = self.plan_m(tid)
        self.assertEqual(code, 0, err)

        # --- step-start (design §3 step 5): running, attempts 1, started_by, base
        repo.touch(repo.rt("dirty-main"))
        base = repo.head()
        code, out, err = repo.forge_status("step-start", tid, "01")
        self.assertEqual(code, 0, err)
        step = repo.step()
        self.assertEqual(step["status"], "running")
        self.assertEqual(step["attempts"], 1)
        self.assertEqual(step["started_by"], "cli")
        self.assertIsInstance(step["started_ts"], int)
        self.assertTrue(step["started_at"].endswith("Z"))
        self.assertIsNone(step["agent_id"])
        self.assertEqual(step["base"], base)
        self.assertEqual(repo.read(f".forge/tasks/{tid}/.base-01").strip(), base)
        self.assertFalse(repo.exists(repo.rt("dirty-main")))
        self.assertTrue(out.startswith(tid), out)
        self.assertIn("running", out)

        # --- a second start of a running step is refused; so is step-report before a report exists
        self.assert_refused(repo.forge_status("step-start", tid, "01"), "already running")

        # --- step-bind (design §3 step 6)
        code, out, err = repo.forge_status("step-bind", tid, "01", "--agent", "agent_b1")
        self.assertEqual(code, 0, err)
        self.assertEqual(repo.step()["agent_id"], "agent_b1")

        # --- the worker's work, committed the way the handoff gate commits it (design §3 step 8)
        repo.write("lib/mod.py", "def add(a, b):\n    return a + b\n\n\ndef sub(a, b):\n    return a - b\n")
        repo.write("lib/extra.py", "def extra():\n    return 42\n")
        repo.git("add", "-A", "--", "lib/mod.py", "lib/extra.py", f".forge/tasks/{tid}/")
        code, out = repo.git("commit", "-q", "-m", f"forge({tid}/01): step 01 [attempt 1]")
        self.assertEqual(code, 0, out)
        commit = repo.head()
        report_json = repo.handoff_json(tid, "01", "DONE", ["lib/mod.py", "lib/extra.py"], commit=commit)
        repo.write_json(f".forge/tasks/{tid}/report-01.json", report_json)
        repo.write_report_md(tid, "01", "DONE", ["lib/mod.py", "lib/extra.py"], commit=commit,
                             path=f".forge/tasks/{tid}/report-01.md")

        # --- step-report: reported, commit recorded, dirty-worker removed, next names the verifier
        repo.touch(repo.rt("dirty-worker"))
        code, out, err = repo.forge_status("step-report", tid, "01", "--report", f".forge/tasks/{tid}/report-01.json")
        self.assertEqual(code, 0, err)
        step = repo.step()
        self.assertEqual(step["status"], "reported")
        self.assertEqual(step["commit"], commit)
        self.assertEqual(step["report"], f".forge/tasks/{tid}/report-01.md")
        self.assertIn("forge-verifier", repo.task()["next_action"])
        self.assertFalse(repo.exists(repo.rt("dirty-worker")))

        # --- step-done without a PASS verdict is impossible (gate 8)
        self.assert_refused(repo.forge_status("step-done", tid, "01"), "step-done without verdict")

        # --- step-verifying
        code, out, err = repo.forge_status("step-verifying", tid, "01", "--agent", "agent_v1")
        self.assertEqual(code, 0, err)
        self.assertEqual(repo.step()["status"], "verifying")

        # --- close with a non-done step is refused (design §5.1)
        repo.write_report_md(tid, "task", "DONE", ["lib/mod.py", "lib/extra.py"], commit=commit,
                             path=f".forge/tasks/{tid}/handoff.md")
        self.assert_refused(repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md"), "close with verifying step")

        # --- verdict PASS -> step-done (design §3 step 9)
        vj = repo.verdict_json(tid, "01", "PASS", range_=f"{base}..{commit}")
        repo.write_json(f".forge/tasks/{tid}/verdict-01.json", vj)
        repo.write_verdict_md(tid, "01", "PASS", range_=f"{base}..{commit}", path=f".forge/tasks/{tid}/verdict-01.md")
        repo.touch(repo.rt("dirty-worker"))
        code, out, err = repo.forge_status("step-verdict", tid, "01", "--verdict", f".forge/tasks/{tid}/verdict-01.json")
        self.assertEqual(code, 0, err)
        task = repo.task()
        step = task["steps"][0]
        self.assertEqual(step["status"], "done")
        self.assertEqual(step["verify_attempts"], 1)
        self.assertEqual(step["commit"], commit)
        self.assertTrue(step["verdict"])
        self.assertIn("forge-close", task["next_action"])
        self.assertIn(task["phase"], ("done", "close"))
        self.assertFalse(repo.exists(repo.rt("dirty-worker")))
        events = repo.ledger_events()
        self.assertIn("open", events)
        self.assertIn("step_done", events)

        # --- journal has one line per transition
        journal = repo.journal(tid)
        self.assertGreaterEqual(len([l for l in journal.splitlines() if l.strip()]), 4, journal)

        # --- close (design §3 step 11)
        repo.touch(repo.rt("dirty-main"))
        code, out, err = repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md")
        self.assertEqual(code, 0, err)
        st = repo.status()
        self.assertIsNone(st["task"])
        self.assertEqual(st["context_state"], "stale")           # clear_policy: phase
        self.assertEqual(len(st["history"]), 1)
        row = st["history"][0]
        for key in ("id", "title", "class", "outcome", "cost_usd", "cost_source", "handoff", "closed_at"):
            self.assertIn(key, row)
        self.assertEqual(row["id"], tid)
        self.assertEqual(row["class"], "M")
        self.assertEqual(row["outcome"], "done")
        self.assertIsNone(row["cost_usd"])
        self.assertEqual(row["cost_source"], "unknown")
        self.assertEqual(row["handoff"], f".forge/tasks/{tid}/handoff.md")
        hist_rows = repo.read_jsonl(".forge/history.jsonl")
        self.assertEqual([r["id"] for r in hist_rows], [tid])
        self.assertIn(tid, repo.read(".forge/CHANGELOG.md"))
        close_rows = [r for r in repo.ledger() if r.get("event") == "close"]
        self.assertEqual(len(close_rows), 1)
        self.assertEqual(close_rows[0]["task"], tid)
        self.assertEqual(close_rows[0]["cost_source"], "unknown")
        self.assertIsNone(close_rows[0]["cost_usd"])
        self.assertEqual(close_rows[0]["outcome"], "done")
        for r in repo.ledger():
            self.assertIn("ts", r)
            self.assertIn("event", r)
        self.assertIn(f"forge({tid})", repo.last_commit_message())
        self.assertEqual(repo.porcelain(), [], "close commits .forge/ and the scope")
        self.assertEqual(repo.read(repo.rt("status.sha")).strip(), self.status_sha())
        self.assertFalse(repo.exists(repo.rt("dirty-main")))
        self.assertTrue(out.startswith("idle") or "idle" in out or "| next:" in out, out)

    def test_close_with_cost_is_operator_sourced(self):
        tid = self.open_m()
        commit = self.repo.head()
        task = make_task(tid, "M", "done", steps=[make_step("01", tid, status="done", attempts=1, commit=commit, base=commit,
                                                              verdict=f".forge/tasks/{tid}/verdict-01.md", report=f".forge/tasks/{tid}/report-01.md")],
                         base=commit)
        self.repo.seed_status(task=task)
        self.repo.write_report_md(tid, "task", path=f".forge/tasks/{tid}/handoff.md")
        code, out, err = self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md", "--cost", "1.25")
        self.assertEqual(code, 0, err)
        row = [r for r in self.repo.ledger() if r.get("event") == "close"][-1]
        self.assertEqual(row["cost_source"], "operator")
        self.assertEqual(row["cost_usd"], 1.25)
        self.assertEqual(self.repo.status()["history"][-1]["cost_source"], "operator")

    def test_close_promotes_queue_head_only(self):
        tid = self.open_m()
        self.repo.open_task("queued", "S", ["lib/util.py"], (), "none", "fixture: declared set is small and has no risk hits", "--queue")
        commit = self.repo.head()
        task = make_task(tid, "M", "done", steps=[make_step("01", tid, status="done", attempts=1, commit=commit, base=commit,
                                                              verdict=f".forge/tasks/{tid}/verdict-01.md")], base=commit)
        st = self.repo.seed_status(task=task, queue=[{"id": "T-0002", "title": "queued", "class_hint": "S"}])
        self.repo.write_report_md(tid, "task", path=f".forge/tasks/{tid}/handoff.md")
        code, out, err = self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md")
        self.assertEqual(code, 0, err)
        st = self.repo.status()
        self.assertIsNone(st["task"], "a queued task is never auto-opened")
        self.assertEqual(st["queue"][0]["id"], "T-0002")


class RefusalTests(StatusTestCase):
    def _planned(self, **step_over):
        tid = self.open_m()
        code, out, err = self.plan_m(tid)
        self.assertEqual(code, 0, err)
        return tid

    def test_step_start_refused_after_three_attempts_without_ruling(self):
        tid = self._planned()
        task = make_task(tid, "M", "execute", steps=[make_step("01", tid, status="failed", attempts=4, base=self.repo.head())],
                         plan=f".forge/tasks/{tid}/plan.md", escalation={"step": "01", "round": 3})
        self.repo.seed_status(task=task)
        self.assert_refused(self.repo.forge_status("step-start", tid, "01", "--from", "failed"), "attempts>3")
        self.repo.write(f".forge/tasks/{tid}/ruling.md", "# Ruling\nDecision — retry once more\nWhy — flaky\nCost if wrong — low\nEvidence considered — verdicts\n")
        code, out, err = self.repo.forge_status("step-start", tid, "01", "--from", "failed")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.repo.step()["status"], "running")
        self.assertEqual(self.repo.step()["attempts"], 5)
        self.assertEqual(self.repo.step()["from"], "failed")

    def test_failed_step_needs_from(self):
        tid = self._planned()
        task = make_task(tid, "M", "execute", steps=[make_step("01", tid, status="failed", attempts=1, base=self.repo.head())],
                         plan=f".forge/tasks/{tid}/plan.md")
        self.repo.seed_status(task=task)
        self.assert_refused(self.repo.forge_status("step-start", tid, "01"), "failed without --from")
        code, out, err = self.repo.forge_status("step-start", tid, "01", "--from", "failed")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.repo.step()["attempts"], 2)
        # --from failed appends the last verdict to the brief's Known failed approaches section
        self.assertIn("Known failed approaches", self.repo.read(f".forge/tasks/{tid}/brief-01.md"))

    def test_close_with_non_done_step_refused(self):
        tid = self._planned()
        self.repo.write_report_md(tid, "task", path=f".forge/tasks/{tid}/handoff.md")
        self.assert_refused(self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md"), "close pending step")
        self.assertIsNotNone(self.repo.task())

    def test_step_done_without_pass_verdict_refused(self):
        tid = self._planned()
        commit = self.repo.head()
        task = make_task(tid, "M", "execute", steps=[make_step("01", tid, status="reported", attempts=1, commit=commit, base=commit)],
                         plan=f".forge/tasks/{tid}/plan.md")
        self.repo.seed_status(task=task)
        self.assert_refused(self.repo.forge_status("step-done", tid, "01"), "no verdict")
        self.assertEqual(self.repo.step()["status"], "reported")

    def test_step_verdict_fail_escalates(self):
        tid = self._planned()
        commit = self.repo.head()
        task = make_task(tid, "M", "execute", steps=[make_step("01", tid, status="reported", attempts=1, commit=commit, base=commit)],
                         plan=f".forge/tasks/{tid}/plan.md", escalation={"step": "01", "round": 0})
        self.repo.seed_status(task=task)
        code, out, err = self.repo.forge_status("step-verifying", tid, "01", "--agent", "agent_v1")
        self.assertEqual(code, 0, err)
        vj = self.repo.verdict_json(tid, "01", "FAIL", criteria=[{"id": "DoD-1", "result": "FAIL", "cmd": LIB_UNIT, "exit": 1}],
                                    blocking=["suite red"])
        self.repo.write_json(f".forge/tasks/{tid}/verdict-01.json", vj)
        self.repo.write_verdict_md(tid, "01", "FAIL", json_obj=vj, path=f".forge/tasks/{tid}/verdict-01.md")
        code, out, err = self.repo.forge_status("step-verdict", tid, "01", "--verdict", f".forge/tasks/{tid}/verdict-01.json")
        self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual(task["steps"][0]["status"], "failed")
        self.assertEqual(task["escalation"]["round"], 1)
        self.assertEqual(task["steps"][0]["verify_attempts"], 1)
        self.assertIn("step_fail", self.repo.ledger_events())

    def test_step_verdict_env_cannot_run_parks_on_external(self):
        tid = self._planned()
        commit = self.repo.head()
        task = make_task(tid, "M", "execute", steps=[make_step("01", tid, status="verifying", attempts=1, commit=commit, base=commit)],
                         plan=f".forge/tasks/{tid}/plan.md")
        self.repo.seed_status(task=task)
        vj = self.repo.verdict_json(tid, "01", "FAIL", criteria=[{"id": "DoD-1", "result": "UNKNOWN", "cmd": LIB_UNIT, "exit": 127}],
                                    blocking=["cannot run the suite here"], tags=["env-cannot-run"])
        self.repo.write_json(f".forge/tasks/{tid}/verdict-01.json", vj)
        code, out, err = self.repo.forge_status("step-verdict", tid, "01", "--verdict", f".forge/tasks/{tid}/verdict-01.json")
        self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual(task["phase"], "awaiting_external")
        self.assertEqual(task["steps"][0]["status"], "awaiting_external")
        self.assertEqual(task["escalation"]["round"], 0, "environmental failures do not escalate (design §4.3 rule 7)")
        self.assertIsNotNone(task["external"])
        self.assertEqual(task["external"]["step"], "01")

    def test_step_done_refuses_commit_outside_allowed_paths(self):
        tid = self._planned()
        base = self.repo.head()
        self.repo.write("README.md", "# touched outside the step\n")
        commit = self.repo.commit_all("out of scope")
        task = make_task(tid, "M", "execute", steps=[make_step("01", tid, status="verifying", attempts=1, commit=commit, base=base)],
                         plan=f".forge/tasks/{tid}/plan.md")
        self.repo.seed_status(task=task)
        vj = self.repo.verdict_json(tid, "01", "PASS", range_=f"{base}..{commit}")
        self.repo.write_json(f".forge/tasks/{tid}/verdict-01.json", vj)
        self.assert_refused(self.repo.forge_status("step-verdict", tid, "01", "--verdict", f".forge/tasks/{tid}/verdict-01.json"),
                            "commit touches README.md outside allowed_paths")

    def test_scope_add_only_for_X_or_with_ruling(self):
        tid = self._planned()
        self.assert_refused(self.repo.forge_status("scope", "add", tid, "lib/other.py", "--why", "needed for the fix"), "M scope add")
        self.repo.write(f".forge/tasks/{tid}/ruling.md", "Decision — widen scope\nWhy — fixture\nCost if wrong — low\nEvidence considered — none\n")
        code, out, err = self.repo.forge_status("scope", "add", tid, "lib/other.py", "--why", "needed for the fix", "--ruling")
        self.assertEqual(code, 0, err)
        self.assertIn("lib/other.py", self.repo.task()["scope"])
        self.assertIn("lib/other.py", self.repo.journal(tid))

    def test_scope_add_for_X(self):
        code, out, err = self.repo.open_task("root-cause the flaky add", "X", ["lib/mod.py"])
        self.assertEqual(code, 0, err)
        rel = self.repo.write_plan("T-0001", "X", allowed_paths=["lib/mod.py"])
        code, out, err = self.repo.forge_status("plan", "T-0001", "--from", rel)
        self.assertEqual(code, 0, err)
        code, out, err = self.repo.forge_status("scope", "add", "T-0001", "lib/util.py", "--why", "the bug crosses into util")
        self.assertEqual(code, 0, err)
        self.assertIn("lib/util.py", self.repo.task()["scope"])

    def test_evidence_requires_an_existing_check_record(self):
        tid = self._planned()
        self.assert_refused(self.repo.forge_status("evidence", tid, "--claim", "suite green", "--from-check", ".forge/tasks/nope.json"), "no record")
        rec = self.repo.write_check_record(tid, "01", "agent_b1")
        code, out, err = self.repo.forge_status("evidence", tid, "--claim", "suite green", "--from-check", rec)
        self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual(task["evidence_count"], 1)
        row = task["evidence"][0]
        self.assertEqual(row["claim"], "suite green")
        self.assertEqual(row["from"], rec)
        for key in ("command", "exit", "when"):
            self.assertIn(key, row)

    def test_evidence_list_is_bounded_to_ten(self):
        tid = self._planned()
        for i in range(12):
            rec = self.repo.write_check_record(tid, "01", "agent_b1", ts=1_700_000_000 + i)
            code, out, err = self.repo.forge_status("evidence", tid, "--claim", f"claim {i}", "--from-check", rec)
            self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual(task["evidence_count"], 12)
        self.assertEqual(len(task["evidence"]), 10)
        self.assertEqual(task["evidence"][-1]["claim"], "claim 11")

    def test_block_and_unblock(self):
        tid = self._planned()
        code, out, err = self.repo.forge_status("block", "--on", "waiting for credentials")
        self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual(task["phase"], "blocked")
        self.assertEqual(task["blocked_on"], "waiting for credentials")
        code, out, err = self.repo.forge_status("unblock")
        self.assertEqual(code, 0, err)
        task = self.repo.task()
        self.assertEqual(task["phase"], "execute")
        self.assertIsNone(task["blocked_on"])

    def test_stale_and_fresh(self):
        self._planned()
        code, out, err = self.repo.forge_status("stale")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.repo.status()["context_state"], "stale")
        self.repo.touch(self.repo.rt("auto-resumed-T-0001-execute"))
        before = self.repo.status()["updated_by"]
        code, out, err = self.repo.forge_status("fresh", "--no-stamp")
        self.assertEqual(code, 0, err)
        st = self.repo.status()
        self.assertEqual(st["context_state"], "fresh")
        self.assertEqual(st["updated_by"], before, "--no-stamp leaves updated_by untouched")
        self.assertFalse(self.repo.exists(self.repo.rt("auto-resumed-T-0001-execute")))
        self.repo.forge_status("stale")
        code, out, err = self.repo.forge_status("fresh")
        self.assertEqual(self.repo.status()["updated_by"]["cmd"].split()[-1], "fresh")

    def test_gate_block_counts_and_ledgers(self):
        tid = self._planned()
        code, out, err = self.repo.forge_status("gate-block", tid, "--agent", "agent_b1", "--gate", "handoff")
        self.assertEqual(code, 0, err)
        rows = [r for r in self.repo.ledger() if r.get("event") == "gate_block"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["task"], tid)

    def test_validate_restamp_after_hand_edit(self):
        self._planned()
        st = self.repo.status()
        st["task"]["resume_hint"] = "hand edited"
        self.repo.write_json(".forge/STATUS.json", st)
        self.assertNotEqual(self.repo.read(self.repo.rt("status.sha")).strip(), self.status_sha())
        code, out, err = self.repo.forge_status("validate", "--restamp")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.repo.read(self.repo.rt("status.sha")).strip(), self.status_sha())


class RecoverAndAttestTests(StatusTestCase):
    def _running(self, started_by="other-session"):
        tid = self.open_m()
        code, out, err = self.plan_m(tid)
        self.assertEqual(code, 0, err)
        base = self.repo.head()
        self.repo.write(f".forge/tasks/{tid}/.base-01", base + "\n")
        task = make_task(tid, "M", "execute", plan=f".forge/tasks/{tid}/plan.md",
                         steps=[make_step("01", tid, status="running", attempts=1, started_by=started_by,
                                          started_at="2026-10-11T00:00:00Z", started_ts=1_760_000_000, base=base)])
        self.repo.seed_status(task=task)
        return tid, base

    def test_recover_restores_tree_and_saves_patch(self):
        tid, base = self._running()
        original = self.repo.read("lib/mod.py")
        self.repo.write("lib/mod.py", original + "\n# half-written\n")
        self.repo.write("lib/extra.py", "partial = True\n")
        code, out, err = self.repo.forge_status("recover", tid, "01")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.repo.step()["status"], "pending")
        self.assertEqual(self.repo.read("lib/mod.py"), original)
        self.assertFalse(self.repo.exists("lib/extra.py"))
        incidents = os.listdir(self.repo.path(".forge/incidents")) if self.repo.exists(".forge/incidents") else []
        patches = [f for f in incidents if f.endswith(".patch") and tid in f and "01" in f]
        self.assertEqual(len(patches), 1, incidents)
        self.assertIn("half-written", self.repo.read(f".forge/incidents/{patches[0]}"))
        self.assertIn("recover", self.repo.ledger_events())

    def test_recover_refused_for_own_session_unless_forced(self):
        tid, base = self._running(started_by="cli")
        self.assert_refused(self.repo.forge_status("recover", tid, "01"), "own session")
        code, out, err = self.repo.forge_status("recover", tid, "01", "--force")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.repo.step()["status"], "pending")

    def test_recover_refused_when_step_not_running(self):
        tid = self.open_m()
        self.plan_m(tid)
        self.assert_refused(self.repo.forge_status("recover", tid, "01", "--force"), "pending step")

    def test_attest_external_criterion_returns_step_to_reported(self):
        tid = self.open_m()
        dod = [{"id": "DoD-1", "criterion": "WHEN the suite runs THE SYSTEM SHALL pass", "check": LIB_UNIT},
               {"id": "DoD-2", "criterion": "WHEN the workflow runs THE SYSTEM SHALL publish", "check": "external",
                "external": {"what": "a green run", "how": "gh run list"}}]
        self.repo.write_brief(tid, "01", dod=["DoD-1", "DoD-2"])
        rel = self.repo.write_plan(tid, "M", dod=dod)
        code, out, err = self.repo.forge_status("plan", tid, "--from", rel)
        self.assertEqual(code, 0, err)
        commit = self.repo.head()
        task = make_task(tid, "M", "awaiting_external", plan=rel,
                         steps=[make_step("01", tid, status="awaiting_external", attempts=1, commit=commit, base=commit, verify_attempts=1)],
                         external={"step": "01", "criteria": ["DoD-2"], "needs": "run the workflow and attest DoD-2"})
        self.repo.seed_status(task=task)
        self.assert_refused(self.repo.forge_status("attest", tid, "01", "DoD-1", "--by", "riggs", "--evidence", "x"), "DoD-1 is not external")
        self.assert_refused(self.repo.forge_status("attest", tid, "01", "DoD-9", "--by", "riggs", "--evidence", "x"), "unknown criterion")
        code, out, err = self.repo.forge_status("attest", tid, "01", "DoD-2", "--by", "riggs",
                                                "--evidence", "https://example.invalid/actions/runs/1")
        self.assertEqual(code, 0, err)
        human = [f for f in self.repo.check_files(tid) if f.endswith("-human.json")]
        self.assertEqual(len(human), 1)
        rec = self.repo.read_json(f".forge/tasks/{tid}/checks/{human[0]}")
        self.assertEqual(rec["agent_id"], "human")
        self.assertEqual(rec["source"], "human")
        self.assertEqual(rec["by"], "riggs")
        self.assertEqual(rec["criterion"], "DoD-2")
        self.assertEqual(rec["evidence"], "https://example.invalid/actions/runs/1")
        self.assertEqual(rec["exit"], 0)
        self.assertEqual(rec["task"], tid)
        self.assertEqual(rec["step"], "01")
        task = self.repo.task()
        self.assertEqual(task["steps"][0]["status"], "reported")
        self.assertIsNone(task["external"])
        self.assertNotEqual(task["phase"], "awaiting_external")
        self.assertIn("verifier", task["next_action"].lower())


class CloseRulesTests(StatusTestCase):
    def test_T_close_needs_one_line_and_a_check_record(self):
        code, out, err = self.repo.open_task("lib: fix add docstring", "T", ["lib/mod.py"])
        self.assertEqual(code, 0, err)
        self.repo.write("lib/mod.py", '"""math"""\n\n\ndef add(a, b):\n    return a + b\n')
        self.assert_refused(self.repo.forge_status("close", "T-0001", "--one-line", "docstring | none"), "no check record")
        code, out, err = self.repo.run_cli("forge-check", "T-0001", "main")
        self.assertEqual(code, 0, err + out)
        self.assert_refused(self.repo.forge_status("close", "T-0001"), "no --one-line")
        code, out, err = self.repo.forge_status("close", "T-0001", "--one-line", "docstring added | checks/main")
        self.assertEqual(code, 0, err)
        st = self.repo.status()
        self.assertIsNone(st["task"])
        self.assertEqual(st["history"][0]["class"], "T")
        self.assertEqual(st["history"][0]["outcome"], "done")
        self.assertIn("T-0001", self.repo.read(".forge/CHANGELOG.md"))
        self.assertIn("forge(T-0001)", self.repo.last_commit_message())
        self.assertEqual(self.repo.porcelain(), [])

    def test_T_close_refused_when_check_record_failed(self):
        self.repo.open_task("lib: break then close", "T", ["lib/mod.py"])
        self.repo.write_check_record("T-0001", "main", "main", results=[{"name": "lib-unit", "cmd": LIB_UNIT, "exit": 1, "dur_s": 0.1, "tail": "FAILED"}])
        self.assert_refused(self.repo.forge_status("close", "T-0001", "--one-line", "x | y"), "failing record")

    def _done_m(self, risk="none"):
        tid = "T-0001"
        self.repo.open_task("lib: add extra helper", "M", ["lib/mod.py", "lib/util.py"], ["lib/extra.py"])
        base = self.repo.head()
        self.repo.write("lib/extra.py", "def extra():\n    return 42\n")
        self.repo.git("add", "--", "lib/extra.py")
        self.repo.git("commit", "-q", "-m", f"forge({tid}/01): step [attempt 1]")
        commit = self.repo.head()
        self.repo.write_verdict_md(tid, "01", path=f".forge/tasks/{tid}/verdict-01.md")
        task = make_task(tid, "M", "done", risk=risk, base=base,
                         steps=[make_step("01", tid, status="done", attempts=1, commit=commit, base=base,
                                          verdict=f".forge/tasks/{tid}/verdict-01.md", report=f".forge/tasks/{tid}/report-01.md")])
        if risk == "R":   # status.json invariant: risk R <=> signals.risk_hits non-empty
            task["signals"]["risk_hits"] = ["lib/upload_tool.py"]
        self.repo.seed_status(task=task)
        self.repo.write_report_md(tid, "task", "DONE", ["lib/extra.py"], path=f".forge/tasks/{tid}/handoff.md")
        return tid

    def test_close_scope_backstop(self):
        tid = self._done_m()
        self.repo.write("qa/stray.py", "# not in scope\n")
        self.assert_refused(self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md"), "stray file")
        self.assertIsNotNone(self.repo.task())
        self.repo.write(f".forge/tasks/{tid}/ruling.md", "Decision — accept stray\nWhy — fixture\nCost if wrong — low\nEvidence considered — none\n")
        code, out, err = self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md",
                                                "--accept-out-of-scope", "qa/stray.py is a fixture artefact")
        self.assertEqual(code, 0, err)
        self.assertIsNone(self.repo.task())

    def test_close_allows_forge_meta_changes(self):
        tid = self._done_m()
        self.repo.write(".forge/lessons/new-lesson.md", "**type: project** a lesson\n")
        self.repo.write("CLAUDE.md", "# project\n")
        self.repo.write(".claude/agent-memory/forge-verifier/MEMORY.md", "# notes\n- calibrated\n")
        code, out, err = self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md")
        self.assertEqual(code, 0, err)

    def test_close_R_needs_human_ack(self):
        tid = self._done_m(risk="R")
        self.assert_refused(self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md"), "R without ack")
        code, out, err = self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md",
                                                "--human-ack", "riggs reviewed diff")
        self.assertEqual(code, 0, err)
        self.assertIsNone(self.repo.task())

    def test_close_M_needs_full_form_handoff(self):
        tid = self._done_m()
        self.repo.write_report_md(tid, "task", "DONE", ["lib/extra.py"], short=True, path=f".forge/tasks/{tid}/handoff.md")
        self.assert_refused(self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md"), "short form for M")
        self.repo.write_report_md(tid, "task", "DONE", ["lib/extra.py"], json_obj=None, path=f".forge/tasks/{tid}/handoff.md")
        self.assert_refused(self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md"), "no json block")

    def test_close_no_commit(self):
        tid = self._done_m()
        head = self.repo.head()
        code, out, err = self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md", "--no-commit")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.repo.head(), head)
        self.assertIsNone(self.repo.task())

    def test_close_partial_needs_ruling(self):
        tid = "T-0001"
        self.repo.open_task("lib: add extra helper", "M", ["lib/mod.py", "lib/util.py"], ["lib/extra.py"])
        base = self.repo.head()
        task = make_task(tid, "M", "execute", base=base, steps=[make_step("01", tid, status="failed", attempts=2, base=base)])
        self.repo.seed_status(task=task)
        self.repo.write_report_md(tid, "task", "BLOCKED", [], path=f".forge/tasks/{tid}/handoff.md")
        self.assert_refused(self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md", "--partial"), "partial without ruling")
        self.repo.write(f".forge/tasks/{tid}/ruling.md", "Decision — park\nWhy — fixture\nCost if wrong — low\nEvidence considered — none\n")
        code, out, err = self.repo.forge_status("close", tid, "--handoff", f".forge/tasks/{tid}/handoff.md", "--partial")
        self.assertEqual(code, 0, err)
        self.assertNotEqual(self.repo.status()["history"][0]["outcome"], "done")


if __name__ == "__main__":
    unittest.main()
