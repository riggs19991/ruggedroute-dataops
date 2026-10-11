"""Tests for forgelib.hooks / forge-hook (MODULE-API §6; design §13.3 per-event table, §6 context clearing, §7 gates)."""
import json
import os
import time
import unittest

import helpers
from helpers import LIB_UNIT, Repo, common, context, decision, make_step, make_task, post_tool, pre_tool, reason

SESSION = "sess-test"


class HookTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = Repo.create()
        self.addCleanup(self.repo.cleanup)
        self.tid = "T-0001"

    def hook(self, stdin, *flags, env=None):
        out = self.repo.hook(stdin, *flags, env=env)
        self.assertEqual(self.repo.last[0], 0, f"forge-hook must always exit 0: {self.repo.last}")
        return out

    def start_session(self, source="startup", session_id=SESSION):
        return self.hook({"hook_event_name": "SessionStart", "source": source, "session_id": session_id, "cwd": self.repo.root})

    def seed_T(self, **over):
        kw = {"scope": ["lib/mod.py"], "files": ["lib/mod.py"], "creates": []}
        kw.update(over)
        task = make_task(self.tid, "T", "execute", **kw)
        self.repo.seed_status(task=task)
        return task

    def seed_M(self, step_status="pending", brief=None, plan=None, **step_over):
        self.repo.write_brief(self.tid, "01", **(brief or {}))
        self.repo.write_plan(self.tid, "M", **(plan or {}))
        step = make_step("01", self.tid, status=step_status, **step_over)
        if step_status != "pending":
            step["started_by"] = step["started_by"] or SESSION
            step["attempts"] = max(1, step["attempts"])
            step["started_at"] = step["started_at"] or "2026-10-11T00:00:00Z"
            step["started_ts"] = step["started_ts"] or 1_760_000_000
            step["base"] = step["base"] or self.repo.head()
        task = make_task(self.tid, "M", "execute", steps=[step])
        self.repo.seed_status(task=task)
        return task

    def assert_deny(self, out, mentions=None, hint=""):
        self.assertEqual(decision(out), "deny", f"{hint}: expected deny, got {out}")
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PreToolUse")
        if mentions:
            self.assertIn(mentions.lower(), reason(out).lower(), f"{hint}: reason should mention {mentions!r}: {reason(out)!r}")

    def assert_allow(self, out, hint=""):
        self.assertNotEqual(decision(out), "deny", f"{hint}: expected allow, got {out}")
        self.assertNotEqual(decision(out), "ask", f"{hint}: expected allow, got {out}")
        self.assertNotEqual(out.get("decision"), "block", f"{hint}: {out}")


class DispatcherTests(HookTestCase):
    def test_garbage_stdin_exits_zero(self):
        code, out, err = self.repo.run_cli("forge-hook", stdin="not json")
        self.assertEqual(code, 0)
        code, out, err = self.repo.run_cli("forge-hook", stdin="")
        self.assertEqual(code, 0)
        code, out, err = self.repo.run_cli("forge-hook", stdin=json.dumps({"hook_event_name": "NoSuchEvent"}))
        self.assertEqual(code, 0)

    def test_plugin_flag_exits_at_once_when_version_exists(self):
        self.assertTrue(self.repo.exists(".forge/VERSION"))
        out = self.hook({"hook_event_name": "SessionStart", "source": "startup", "session_id": SESSION}, "--plugin")
        self.assertEqual(out, {})
        self.assertFalse(self.repo.exists(self.repo.rt("session-id")))

    def test_pre_tool_use_fails_closed_on_broken_status(self):
        self.repo.write(".forge/STATUS.json", "{broken")
        out = self.hook(pre_tool("Edit", {"file_path": "lib/mod.py"}))
        self.assert_deny(out, hint="broken STATUS")

    def test_stop_fails_open_on_broken_status(self):
        self.repo.write(".forge/STATUS.json", "{broken")
        out = self.hook({"hook_event_name": "Stop", "stop_hook_active": False, "session_id": SESSION})
        self.assertNotEqual(out.get("decision"), "block")

    def test_subagent_stop_fails_closed_on_broken_status(self):
        self.repo.write(".forge/STATUS.json", "{broken")
        out = self.hook({"hook_event_name": "SubagentStop", "agent_id": "agent_b1", "agent_type": "forge-builder",
                         "last_assistant_message": "done", "stop_hook_active": False, "session_id": SESSION})
        self.assertEqual(out.get("decision"), "block", out)


class SessionStartTests(HookTestCase):
    def test_emits_digest_and_writes_markers(self):
        env_file = self.repo.path(".env-file")
        out = self.hook({"hook_event_name": "SessionStart", "source": "startup", "session_id": SESSION, "cwd": self.repo.root},
                        env={"CLAUDE_ENV_FILE": env_file})
        hso = out["hookSpecificOutput"]
        self.assertEqual(hso["hookEventName"], "SessionStart")
        ctx = hso["additionalContext"]
        self.assertIn("[full: .forge/STATUS.json]", ctx)
        self.assertLessEqual(len(ctx), common.MAX_ADDITIONAL_CONTEXT)
        self.assertIn("fixture lesson", ctx)                      # lessons/INDEX.md head
        self.assertIn("lib-unit", ctx)                            # binding digest: verify names
        self.assertEqual(self.repo.read(self.repo.rt("session-id")).strip(), SESSION)
        alive = self.repo.read_json(self.repo.rt("hooks-alive"))
        self.assertEqual(alive["session_id"], SESSION)
        self.assertEqual(alive["source"], "startup")
        self.assertIsInstance(alive["ts"], int)
        self.assertIn("forge idle", hso.get("sessionTitle", "forge idle"))
        env_text = self.repo.read(".env-file")
        self.assertIn("/.forge/bin", env_text)
        self.assertIn("export PATH=", env_text)
        self.assertNotIn("initialUserMessage", hso)

    def test_skipped_entirely_for_subagents(self):
        out = self.hook({"hook_event_name": "SessionStart", "source": "startup", "session_id": SESSION, "agent_type": "forge-builder"})
        self.assertEqual(out, {})
        self.assertFalse(self.repo.exists(self.repo.rt("session-id")))

    def test_title_and_digest_with_task(self):
        self.seed_M()
        out = self.start_session()
        hso = out["hookSpecificOutput"]
        self.assertIn(self.tid, hso["additionalContext"])
        self.assertIn("execute", hso["additionalContext"])
        self.assertEqual(hso.get("sessionTitle"), f"forge {self.tid} execute")

    def test_interrupted_banner(self):
        self.seed_M("running", started_by="another-session", agent_id="agent_gone")
        out = self.start_session()
        self.assertIn("INTERRUPTED", context(out))

    def test_stale_banner(self):
        self.seed_M()
        self.repo.touch(self.repo.rt("stale-status"))
        out = self.start_session()
        self.assertIn("STALE", context(out))

    def test_auto_resume_only_on_clear(self):
        self.seed_M()
        self.repo.forge_status("stale")
        before = self.repo.status()["updated_by"]
        out = self.start_session("compact")
        self.assertNotIn("initialUserMessage", out["hookSpecificOutput"], "never on compact")
        self.assertEqual(self.repo.status()["context_state"], "stale")
        out = self.start_session("clear")
        hso = out["hookSpecificOutput"]
        self.assertIn("initialUserMessage", hso)
        self.assertIn("next_action", hso["initialUserMessage"])
        st = self.repo.status()
        self.assertEqual(st["context_state"], "fresh", "the hook runs forge-status fresh --no-stamp")
        self.assertEqual(st["updated_by"], before, "fresh --no-stamp leaves updated_by untouched")
        self.assertIn("auto-resume", self.repo.journal(self.tid).lower())
        # a second clear without a new stale state never re-fires (design §6 layer 5: once per task/phase).
        # NOTE: §5.1 says `fresh` removes auto-resumed-* markers while §13.3 touches the marker right before
        # `fresh`; the observable guarantee tested here holds under either reading.
        out = self.start_session("clear")
        self.assertNotIn("initialUserMessage", out["hookSpecificOutput"])

    def test_no_auto_resume_when_binding_disables_it(self):
        binding = dict(helpers.BINDING)
        binding["auto_resume"] = False
        self.repo.write_json(".forge/binding.json", binding)
        self.seed_M()
        self.repo.forge_status("stale")
        out = self.start_session("clear")
        self.assertNotIn("initialUserMessage", out["hookSpecificOutput"])

    def test_handoff_sections_injected(self):
        self.seed_M("reported", commit=self.repo.head(), report=f".forge/tasks/{self.tid}/report-01.md")
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        text = text.replace("## Remaining\nnone", "## Remaining\n- the unusual remaining item")
        self.repo.write(f".forge/tasks/{self.tid}/report-01.md", text)
        out = self.start_session()
        self.assertIn("the unusual remaining item", context(out))

    def test_role_handler(self):
        out = self.hook({"hook_event_name": "SessionStart", "source": "startup", "session_id": SESSION}, "--role")
        ctx = context(out)
        self.assertIn("Role: Forge architect", ctx)
        self.assertLessEqual(len(ctx), 4000)
        out = self.hook({"hook_event_name": "SessionStart", "source": "startup", "session_id": SESSION, "agent_type": "forge-builder"}, "--role")
        self.assertEqual(out, {})


class UserPromptSubmitTests(HookTestCase):
    def ups(self, prompt="do the thing"):
        return self.hook({"hook_event_name": "UserPromptSubmit", "prompt": prompt, "session_id": SESSION})

    def test_idle_reminder(self):
        out = self.ups()
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
        self.assertIn("Forge: idle", context(out))
        self.assertIn("/forge-task", context(out))

    def test_task_reminder_and_stale_hint(self):
        self.seed_M()
        ctx = context(self.ups())
        self.assertIn(f"Forge: {self.tid}", ctx)
        self.assertIn("class M", ctx)
        self.assertIn("risk none", ctx)
        self.assertIn("phase execute", ctx)
        self.assertIn("next:", ctx)
        self.assertNotIn("/clear", ctx)
        self.repo.forge_status("stale")
        ctx = context(self.ups())
        self.assertIn("stale", ctx)
        self.assertIn("/clear", ctx)
        self.assertNotIn("$", ctx, "no budget text, ever (design §4.3 rule 9)")

    def test_markers(self):
        self.repo.write(self.repo.rt("stop-blocks"), "2\n")
        self.repo.write(self.repo.rt("denials"), json.dumps({"rule": 3}))
        self.repo.touch(self.repo.rt("dirty-main"))
        self.repo.touch(self.repo.rt("dirty-worker"))
        self.ups("? what does this do")
        self.assertEqual(self.repo.read(self.repo.rt("stop-blocks")).strip(), "0")
        self.assertFalse(self.repo.exists(self.repo.rt("denials")))
        self.assertTrue(self.repo.exists(self.repo.rt("chat-turn")))
        self.assertTrue(self.repo.exists(self.repo.rt("dirty-main")), "never touches dirty-*")
        self.assertTrue(self.repo.exists(self.repo.rt("dirty-worker")))
        self.ups("now change it")
        self.assertFalse(self.repo.exists(self.repo.rt("chat-turn")))


class PreToolUseEditTests(HookTestCase):
    def edit(self, path, **kw):
        return self.hook(pre_tool("Edit", {"file_path": path}, **kw))

    def test_denied_without_task(self):
        out = self.edit("lib/mod.py")
        self.assert_deny(out, "/forge-task", "no task")
        self.assertFalse(self.repo.exists(self.repo.rt("dirty-main")))

    def test_write_and_notebook_edit_share_the_rule(self):
        self.assert_deny(self.hook(pre_tool("Write", {"file_path": "lib/new.py"})), hint="Write")
        self.assert_deny(self.hook(pre_tool("NotebookEdit", {"notebook_path": "lib/nb.ipynb"})), hint="NotebookEdit")

    def test_class_m_denied_in_main_session(self):
        self.seed_M()
        self.assert_deny(self.edit("lib/mod.py"), "class M", "M in main")
        self.assert_deny(self.edit(os.path.join(self.repo.root, "lib", "mod.py")), "class M", "absolute path")

    def test_meta_paths_allowed_in_main_session_even_for_m(self):
        self.seed_M()
        for p in (f".forge/tasks/{self.tid}/plan.md", ".forge/lessons/x.md", ".forge/decisions/0002-x.md",
                  ".forge/CHANGELOG.md", "CLAUDE.md", ".gitignore", ".claude/agent-memory/forge-verifier/MEMORY.md"):
            self.assert_allow(self.edit(p), p)
        self.assertFalse(self.repo.exists(self.repo.rt("dirty-main")), "meta edits are not source mutations")

    def test_t_allowed_inside_declared_scope_and_denied_outside(self):
        self.seed_T()
        self.repo.touch(self.repo.rt("chat-turn"))
        out = self.edit("lib/mod.py")
        self.assert_allow(out, "in scope")
        self.assertTrue(self.repo.exists(self.repo.rt("dirty-main")), "allowed source edit touches dirty-main")
        self.assertFalse(self.repo.exists(self.repo.rt("chat-turn")), "a mutation ends the chat exemption")
        self.assert_deny(self.edit("lib/util.py"), "scope", "outside scope")

    def test_s_requires_plan_first(self):
        task = make_task(self.tid, "S", "plan", scope=["lib/mod.py"], files=["lib/mod.py"], creates=[], plan=None, plan_author=None)
        self.repo.seed_status(task=task)
        self.assert_deny(self.edit("lib/mod.py"), "plan", "S before plan")
        self.repo.write_plan(self.tid, "S", allowed_paths=["lib/mod.py"])
        task = make_task(self.tid, "S", "execute", scope=["lib/mod.py"], files=["lib/mod.py"], creates=[])
        self.repo.seed_status(task=task)
        self.assert_allow(self.edit("lib/mod.py"), "S after plan")

    def test_protected_paths_denied_unless_risk(self):
        self.seed_T(scope=["lib/mod.py", ".github/workflows/ci.yml"])
        self.assert_deny(self.edit(".github/workflows/ci.yml"), hint="protected in main")

    def test_policy_lock(self):
        self.seed_T(scope=["lib/mod.py", ".forge/STATUS.json", ".forge/binding.json"])
        for p in (".forge/STATUS.json", ".forge/binding.json", ".claude/settings.json", ".claude/settings.local.json",
                  ".forge/schemas/status.json", ".forge/ledger.jsonl", ".forge/history.jsonl", ".forge/bin/forge-status"):
            self.assert_deny(self.edit(p), hint=p)
        # the lock applies to subagents too
        self.repo.bind_agent("agent_b1")
        self.assert_deny(self.edit(".forge/STATUS.json", agent_id="agent_b1", agent_type="forge-builder"), hint="subagent lock")

    def test_denial_counter_ends_the_turn_on_the_third_denial(self):
        self.hook({"hook_event_name": "UserPromptSubmit", "prompt": "go", "session_id": SESSION})
        first = self.edit("lib/mod.py")
        second = self.edit("lib/util.py")
        third = self.edit("lib/shared.py")
        self.assert_deny(first)
        self.assertNotIn("continue", first)
        self.assertNotIn("continue", second)
        self.assertIs(third.get("continue"), False, third)
        self.assertTrue(third.get("stopReason"))

    # ---- subagents (design §7 gate 2)
    def test_builder_must_be_bound_to_a_brief(self):
        self.seed_M("running", agent_id=None)
        self.repo.agent_record("agent_b1", "forge-builder")
        self.assert_deny(self.edit("lib/mod.py", agent_id="agent_b1", agent_type="forge-builder"), "brief", "unbound")

    def test_builder_scope_fence(self):
        self.seed_M("running", agent_id="agent_b1", brief={"allowed_paths": ["lib/**"]}, allowed_paths=["lib/**"])
        self.repo.bind_agent("agent_b1")
        kw = {"agent_id": "agent_b1", "agent_type": "forge:forge-builder"}   # plugin-namespaced type
        self.assert_allow(self.edit("lib/mod.py", **kw), "inside allowed_paths")
        self.assertFalse(self.repo.exists(self.repo.rt("dirty-main")), "worker edits never dirty the main session")
        self.assert_deny(self.edit("qa/x.py", **kw), hint="outside allowed_paths")
        self.assert_deny(self.edit(f".forge/tasks/{self.tid}/notes.md", **kw), hint="builders never write .forge/**")
        self.assert_deny(self.edit("lib/test_mod.py", **kw), hint="existing test without may_edit_tests")
        self.assert_allow(self.edit("lib/test_brand_new.py", **kw), "new test file")

    def test_builder_may_edit_tests(self):
        self.seed_M("running", agent_id="agent_b1", brief={"allowed_paths": ["lib/**"], "may_edit_tests": True}, allowed_paths=["lib/**"])
        self.repo.bind_agent("agent_b1")
        self.assert_allow(self.edit("lib/test_mod.py", agent_id="agent_b1", agent_type="forge-builder"), "may_edit_tests")

    def test_tool_budget(self):
        self.seed_M("running", agent_id="agent_b1", brief={"max_tool_calls": 5})
        self.repo.bind_agent("agent_b1")
        for i in range(5):
            self.repo.add_evidence(self.tid, "agent_b1", "forge-builder", "bash" if i % 2 else "edit", kind="source", file="lib/mod.py", cmd="ls")
        self.assert_deny(self.edit("lib/mod.py", agent_id="agent_b1", agent_type="forge-builder"), "budget", "budget exhausted")

    def test_read_only_roles(self):
        self.seed_M("verifying", agent_id="agent_b1", commit=self.repo.head())
        self.repo.agent_record("agent_v1", "forge-verifier", task=self.tid, step="01")
        self.repo.agent_record("agent_s1", "forge-scout")
        self.repo.agent_record("agent_p1", "forge-planner", task=self.tid)
        self.assert_allow(self.edit(".claude/agent-memory/forge-verifier/MEMORY.md", agent_id="agent_v1", agent_type="forge-verifier"), "verifier memory")
        self.assert_deny(self.edit("lib/mod.py", agent_id="agent_v1", agent_type="forge-verifier"), hint="verifier source")
        self.assert_deny(self.edit("lib/mod.py", agent_id="agent_s1", agent_type="forge-scout"), hint="scout")
        self.assert_deny(self.edit(".claude/agent-memory/forge-scout/x.md", agent_id="agent_s1", agent_type="forge-scout"), hint="scout memory")
        self.assert_allow(self.edit(f".forge/tasks/{self.tid}/plan.md", agent_id="agent_p1", agent_type="forge-planner"), "planner plan")
        self.assert_deny(self.edit("lib/mod.py", agent_id="agent_p1", agent_type="forge-planner"), hint="planner source")

    def test_protected_paths_by_tier(self):
        self.seed_M("running", agent_id="agent_b1", brief={"allowed_paths": ["lib/**", ".github/workflows/**"], "owner_agent": "forge-builder-s", "model": "sonnet"},
                    allowed_paths=["lib/**", ".github/workflows/**"], agent="forge-builder-s", model="sonnet")
        self.repo.bind_agent("agent_b1", agent_type="forge-builder-s")
        self.assert_deny(self.edit(".github/workflows/ci.yml", agent_id="agent_b1", agent_type="forge-builder-s"), hint="builder-s protected")
        self.assert_allow(self.edit("lib/mod.py", agent_id="agent_b1", agent_type="forge-builder-s"), "builder-s source")


class PreToolUseAgentTests(HookTestCase):
    def spawn(self, subagent_type, model=None, effort=None, prompt="Read the brief and execute it."):
        ti = {"subagent_type": subagent_type, "prompt": prompt, "run_in_background": True}
        if model:
            ti["model"] = model
        if effort:
            ti["effort"] = effort
        return self.hook(pre_tool("Agent", ti))

    def test_builtin_spawn_allowed_and_journaled(self):
        self.seed_M()
        out = self.spawn("general-purpose", "sonnet", "low")
        self.assert_allow(out, "builtin")
        self.assertIn("builtin", self.repo.ledger_events())

    def test_scout_always_allowed(self):
        self.assert_allow(self.spawn("forge-scout"), "scout without task")

    def test_denied_without_task(self):
        self.assert_deny(self.spawn("forge-builder", "opus", "medium"), hint="no task")

    def test_matching_pending_step_is_allowed_and_started(self):
        self.start_session()
        self.seed_M()
        base = self.repo.head()
        out = self.spawn("forge-builder", "claude-opus-5-5", "medium")   # full id: alias-normalised
        self.assert_allow(out, "matching triple")
        step = self.repo.step()
        self.assertEqual(step["status"], "running")
        self.assertEqual(step["attempts"], 1)
        self.assertEqual(step["started_by"], SESSION)
        self.assertEqual(step["base"], base)
        self.assertIsNone(step["agent_id"])
        self.assertTrue(self.repo.exists(f".forge/tasks/{self.tid}/.base-01"))
        self.assertIn("dispatch", self.repo.ledger_events())

    def test_defaults_fill_model_and_effort(self):
        self.seed_M()
        self.assert_allow(self.spawn("forge-builder"), "forge-builder defaults to opus/medium")
        self.assertEqual(self.repo.step()["status"], "running")

    def test_mismatched_model_or_effort_denied(self):
        self.seed_M()
        out = self.spawn("forge-builder", "sonnet", "medium")
        self.assert_deny(out, "opus", "wrong model")
        self.assert_deny(self.spawn("forge-builder", "opus", "high"), "medium", "wrong effort")
        self.assert_deny(self.spawn("forge-builder-s", "sonnet", "medium"), hint="wrong agent")
        self.assertEqual(self.repo.step()["status"], "pending", "a denied spawn never starts the step")

    def test_running_step_with_agent_is_denied_and_failed_step_needs_step_start(self):
        self.seed_M("running", agent_id="agent_old")
        self.assert_deny(self.spawn("forge-builder", "opus", "medium"), hint="a bound worker is still running")
        self.seed_M("failed", agent_id="agent_old")
        self.assert_deny(self.spawn("forge-builder", "opus", "medium"), "step-start", "retry needs --from failed|clean")
        self.assertEqual(self.repo.step()["status"], "failed")

    def test_pre_started_retry_is_allowed_without_a_second_start(self):
        self.seed_M("running", agent_id=None, attempts=2)
        out = self.spawn("forge-builder", "opus", "medium")
        self.assert_allow(out, "pre-started retry")
        self.assertEqual(self.repo.step()["attempts"], 2)

    def test_verifier_only_on_a_reported_step(self):
        self.seed_M("reported", agent_id="agent_b1", commit=self.repo.head())
        self.assert_deny(self.spawn("forge-verifier", "sonnet", "medium"), hint="verifier below routing")
        out = self.spawn("forge-verifier", "opus", "medium")
        self.assert_allow(out, "verifier on reported")
        self.assertEqual(self.repo.step()["status"], "verifying")
        self.assertEqual(self.repo.ledger_events().count("dispatch"), 1)

    def test_verifier_denied_on_pending_or_after_two_rounds(self):
        self.seed_M()
        self.assert_deny(self.spawn("forge-verifier", "opus", "medium"), hint="pending")
        self.seed_M("reported", agent_id="agent_b1", commit=self.repo.head(), verify_attempts=2)
        self.assert_deny(self.spawn("forge-verifier", "opus", "medium"), hint="verify_attempts cap")
        self.repo.write(f".forge/tasks/{self.tid}/ruling.md", "Decision — verify again\nWhy — fixture\nCost if wrong — low\nEvidence considered — none\n")
        self.assert_allow(self.spawn("forge-verifier", "opus", "medium"), "ruling lifts the cap")

    def test_planner_only_in_plan_phase(self):
        task = make_task(self.tid, "M", "plan", steps=[], plan=None, plan_author=None,
                         routing={"mode": "single", "builder": None, "verifier": None, "justification": "fixture"})
        self.repo.seed_status(task=task)
        self.assert_deny(self.spawn("forge-planner", "fable", "high"), hint="M planner needs medium")
        self.assert_allow(self.spawn("forge-planner", "fable", "medium"), "planner in plan phase")
        self.seed_M()
        self.assert_deny(self.spawn("forge-planner", "fable", "medium"), hint="planner outside plan phase")

    def test_inline_verifier_for_s_and_x(self):
        self.repo.seed_status(task=make_task(self.tid, "S", "execute", scope=["lib/mod.py"], files=["lib/mod.py"], creates=[]))
        self.assert_allow(self.spawn("forge-verifier", "sonnet", "medium"), "S verifier")
        self.assert_deny(self.spawn("forge-verifier", "haiku", "medium"), hint="S verifier haiku")
        self.repo.seed_status(task=make_task(self.tid, "X", "execute", scope=["lib/mod.py"], files=["lib/mod.py"], creates=[]))
        self.assert_deny(self.spawn("forge-verifier", "opus", "medium"), hint="X verifier must be fable")
        self.assert_allow(self.spawn("forge-verifier", "fable", "medium"), "X verifier")


class PreToolUseBashTests(HookTestCase):
    def bash(self, cmd, **kw):
        return self.hook(pre_tool("Bash", {"command": cmd}, **kw))

    def test_irreversible_asks_in_main_session_and_denies_in_driver(self):
        self.seed_T()
        out = self.bash("git push origin main")
        self.assertEqual(decision(out), "ask", out)
        self.assertEqual(decision(self.bash("cd worker && npx wrangler deploy")), "ask")
        self.assertEqual(decision(self.bash("ls && git push origin main")), "ask", "every segment is matched")
        self.repo.touch(self.repo.rt("driver"))
        self.assert_deny(self.bash("git push origin main"), hint="driver mode")

    def test_subagent_denials(self):
        self.seed_M("running", agent_id="agent_b1")
        self.repo.bind_agent("agent_b1")
        kw = {"agent_id": "agent_b1", "agent_type": "forge-builder"}
        for cmd in ("git push origin main", "git reset --hard HEAD~1", "git clean -fd", "git checkout -- .",
                    "rm -rf lib", f".forge/bin/forge-status step-done {self.tid} 01", "wrangler deploy"):
            self.assert_deny(self.bash(cmd, **kw), hint=cmd)
        for cmd in ("rm -rf /tmp/scratch", f".forge/bin/forge-check {self.tid} 01", f".forge/bin/forge-status get digest",
                    f".forge/bin/forge-gate --handoff {self.tid} 01 --from-file /tmp/d.md", LIB_UNIT, "git status"):
            self.assert_allow(self.bash(cmd, **kw), cmd)

    def test_subagent_tool_budget_applies_to_bash(self):
        self.seed_M("running", agent_id="agent_b1", brief={"max_tool_calls": 5})
        self.repo.bind_agent("agent_b1")
        for _ in range(5):
            self.repo.add_evidence(self.tid, "agent_b1", "forge-builder", "bash", ok=True, exit=0, cmd="ls")
        self.assert_deny(self.bash("ls", agent_id="agent_b1", agent_type="forge-builder"), "budget")

    def test_read_only_roles_allow_list(self):
        self.seed_M("verifying", agent_id="agent_b1", commit=self.repo.head())
        self.repo.agent_record("agent_v1", "forge-verifier", task=self.tid, step="01")
        kw = {"agent_id": "agent_v1", "agent_type": "forge-verifier"}
        for cmd in ("git log --oneline -5", "git diff HEAD~1..HEAD", "pytest -q", LIB_UNIT, f".forge/bin/forge-check {self.tid} 01 --ratchet",
                    "cat lib/mod.py | head -5"):
            self.assert_allow(self.bash(cmd, **kw), cmd)
        for cmd in ("echo hi > f", "python3 -c 'print(1)'", "sed -i 's/a/b/' lib/mod.py", "rm lib/mod.py", "cat <<EOF > x\nhi\nEOF"):
            self.assert_deny(self.bash(cmd, **kw), hint=cmd)

    def test_main_session_mutation_guard(self):
        self.assert_deny(self.bash("sed -i 's/a/b/' lib/mod.py"), hint="no task")
        self.assert_allow(self.bash("git status"), "git status always fine")
        self.seed_M()
        self.assert_deny(self.bash("echo x > lib/mod.py"), hint="M in main")
        self.assert_allow(self.bash(LIB_UNIT), "verify command")
        self.assert_allow(self.bash(f".forge/bin/forge-check {self.tid} 01"), "forge script")
        self.assert_allow(self.bash("git add -A && git commit -m x"), "git add/commit")
        self.seed_T()
        out = self.bash("sed -i 's/a/b/' lib/mod.py")
        self.assert_allow(out, "T mutating")
        self.assertTrue(self.repo.exists(self.repo.rt("dirty-main")))

    def test_s_before_plan_denies_mutation(self):
        task = make_task(self.tid, "S", "plan", scope=["lib/mod.py"], files=["lib/mod.py"], creates=[], plan=None, plan_author=None)
        self.repo.seed_status(task=task)
        self.assert_deny(self.bash("python3 -c 'open(\"lib/mod.py\",\"w\")'"), hint="S before plan")


class PostToolUseTests(HookTestCase):
    def test_main_edit_appends_source_row_and_touches_dirty_main(self):
        self.seed_T()
        out = self.hook(post_tool("Edit", {"file_path": "lib/mod.py"}))
        self.assertEqual(out, {})
        rows = self.repo.evidence(self.tid)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["agent_id"], "main")
        self.assertEqual(row["agent_type"], "main")
        self.assertEqual(row["event"], "edit")
        self.assertEqual(row["kind"], "source")
        self.assertEqual(row["file"], "lib/mod.py")
        self.assertIsInstance(row["ts"], int)
        self.assertTrue(self.repo.exists(self.repo.rt("dirty-main")))

    def test_meta_edit_is_meta_and_clean(self):
        self.seed_M()
        self.hook(post_tool("Write", {"file_path": f".forge/tasks/{self.tid}/plan.md"}))
        row = self.repo.evidence(self.tid)[0]
        self.assertEqual(row["kind"], "meta")
        self.assertFalse(self.repo.exists(self.repo.rt("dirty-main")))

    def test_subagent_edit_row_keyed_by_agent(self):
        self.seed_M("running", agent_id="agent_b1")
        self.hook(post_tool("Edit", {"file_path": os.path.join(self.repo.root, "lib/mod.py")}, agent_id="agent_b1", agent_type="forge:forge-builder"))
        row = self.repo.evidence(self.tid)[0]
        self.assertEqual(row["agent_id"], "agent_b1")
        self.assertEqual(row["agent_type"], "forge-builder")
        self.assertEqual(row["file"], "lib/mod.py")
        self.assertFalse(self.repo.exists(self.repo.rt("dirty-main")))

    def test_bash_row_with_best_effort_exit(self):
        self.seed_T()
        self.hook(post_tool("Bash", {"command": "ls lib"}, {"stdout": "mod.py", "exit_code": 0}))
        row = self.repo.evidence(self.tid)[0]
        self.assertEqual(row["event"], "bash")
        self.assertIs(row["ok"], True)
        self.assertEqual(row["exit"], 0)
        self.assertEqual(row["cmd"], "ls lib")
        self.assertFalse(self.repo.exists(self.repo.rt("dirty-main")), "a read-only command is not a mutation")
        self.hook(post_tool("Bash", {"command": "sed -i 's/a/b/' lib/mod.py"}, {"stdout": ""}))
        self.assertTrue(self.repo.exists(self.repo.rt("dirty-main")), "a mutating main-session command touches dirty-main")

    def test_bash_failure_row(self):
        self.seed_T()
        self.hook({"hook_event_name": "PostToolUseFailure", "tool_name": "Bash", "tool_input": {"command": "false"},
                   "error": "Exit code 1\nsomething went wrong " + "x" * 400, "session_id": SESSION})
        row = self.repo.evidence(self.tid)[0]
        self.assertEqual(row["event"], "bash")
        self.assertIs(row["ok"], False)
        self.assertEqual(row["cmd"], "false")
        self.assertIn(row["exit"], (1, None))
        self.assertLessEqual(len(row["error_head"]), 200)

    def test_forge_check_record_is_stamped_with_agent(self):
        self.seed_M("running", agent_id="agent_b1")
        self.repo.bind_agent("agent_b1")
        code, out, err = self.repo.run_cli("forge-check", self.tid, "01")
        self.assertEqual(code, 0, err)
        self.assertTrue([f for f in self.repo.check_files(self.tid) if f.endswith("-unknown.json")])
        self.hook(post_tool("Bash", {"command": f".forge/bin/forge-check {self.tid} 01"}, {"stdout": out, "exit_code": 0},
                            agent_id="agent_b1", agent_type="forge-builder"))
        files = self.repo.check_files(self.tid)
        self.assertFalse([f for f in files if f.endswith("-unknown.json")], files)
        stamped = [f for f in files if f.endswith("-agent_b1.json")]
        self.assertEqual(len(stamped), 1, files)
        rec = self.repo.read_json(f".forge/tasks/{self.tid}/checks/{stamped[0]}")
        self.assertEqual(rec["agent_id"], "agent_b1")

    def test_forge_check_record_stamped_main_with_session(self):
        self.start_session()
        self.seed_T()
        code, out, err = self.repo.run_cli("forge-check", self.tid, "main")
        self.assertEqual(code, 0, err)
        self.hook(post_tool("Bash", {"command": f".forge/bin/forge-check {self.tid} main"}, {"stdout": out, "exit_code": 0}))
        stamped = [f for f in self.repo.check_files(self.tid) if f.endswith("-main.json")]
        self.assertEqual(len(stamped), 1, self.repo.check_files(self.tid))
        rec = self.repo.read_json(f".forge/tasks/{self.tid}/checks/{stamped[0]}")
        self.assertEqual(rec["agent_id"], "main")
        self.assertEqual(rec["session_id"], SESSION)

    def test_read_of_own_brief_binds_the_worker(self):
        self.seed_M("running", agent_id=None)
        self.hook({"hook_event_name": "SubagentStart", "agent_id": "agent_b1", "agent_type": "forge-builder", "session_id": SESSION})
        out = self.hook(post_tool("Read", {"file_path": f".forge/tasks/{self.tid}/brief-01.md"}, {"content": "..."},
                                  agent_id="agent_b1", agent_type="forge-builder"))
        self.assertEqual(out, {})
        self.assertEqual(self.repo.step()["agent_id"], "agent_b1")
        rec = self.repo.read_json(".forge/.runtime/agents/agent_b1.json")
        self.assertEqual(rec["task"], self.tid)
        self.assertEqual(rec["step"], "01")
        self.assertEqual(rec["brief"], f".forge/tasks/{self.tid}/brief-01.md")
        self.assertIn("bound_at", rec)
        # bound: an edit inside allowed_paths is now allowed
        self.assert_allow(self.hook(pre_tool("Edit", {"file_path": "lib/mod.py"}, agent_id="agent_b1", agent_type="forge-builder")), "after bind")

    def test_read_never_rebinds_or_binds_the_wrong_role(self):
        self.seed_M("running", agent_id="agent_first")
        self.repo.agent_record("agent_b2", "forge-builder")
        self.hook(post_tool("Read", {"file_path": f".forge/tasks/{self.tid}/brief-01.md"}, {}, agent_id="agent_b2", agent_type="forge-builder"))
        self.assertEqual(self.repo.step()["agent_id"], "agent_first", "a bound step is never rebound")
        self.assertNotIn("brief", self.repo.read_json(".forge/.runtime/agents/agent_b2.json"))
        self.seed_M("running", agent_id=None)
        self.repo.agent_record("agent_m1", "forge-mechanic")
        self.hook(post_tool("Read", {"file_path": f".forge/tasks/{self.tid}/brief-01.md"}, {}, agent_id="agent_m1", agent_type="forge-mechanic"))
        self.assertIsNone(self.repo.step()["agent_id"], "owner_agent mismatch never binds")

    def test_bash_cat_of_brief_binds_too(self):
        self.seed_M("running", agent_id=None)
        self.repo.agent_record("agent_b1", "forge-builder")
        self.hook(pre_tool("Bash", {"command": f"cat .forge/tasks/{self.tid}/brief-01.md"}, agent_id="agent_b1", agent_type="forge-builder"))
        self.hook(post_tool("Bash", {"command": f"cat .forge/tasks/{self.tid}/brief-01.md"}, {"exit_code": 0}, agent_id="agent_b1", agent_type="forge-builder"))
        self.assertEqual(self.repo.step()["agent_id"], "agent_b1")


class SubagentStartTests(HookTestCase):
    def test_record_and_reminder(self):
        out = self.hook({"hook_event_name": "SubagentStart", "agent_id": "agent_b1", "agent_type": "forge:forge-builder", "session_id": SESSION})
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SubagentStart")
        self.assertIn("brief", context(out).lower())
        rec = self.repo.read_json(".forge/.runtime/agents/agent_b1.json")
        self.assertEqual(rec["agent_id"], "agent_b1")
        self.assertEqual(common.agent_role(rec["agent_type"]), "forge-builder")
        self.assertIsInstance(rec["started_ts"], int)
        self.assertIn("session_id", rec)


class StopTests(HookTestCase):
    def stop(self, active=False):
        return self.hook({"hook_event_name": "Stop", "stop_hook_active": active, "session_id": SESSION})

    def status_sha(self):
        return common.sha256_file(self.repo.path(".forge/STATUS.json"))

    def test_allows_when_idle(self):
        self.repo.touch(self.repo.rt("dirty-main"))
        self.assertNotEqual(self.stop().get("decision"), "block")

    def test_allows_in_terminal_phases(self):
        for phase in ("done", "blocked", "awaiting_external"):
            self.seed_M("done", commit=self.repo.head(), verdict="v")
            st = self.repo.status()
            st["task"]["phase"] = phase
            self.repo.write_json(".forge/STATUS.json", st)
            self.repo.touch(self.repo.rt("dirty-main"))
            self.assertNotEqual(self.stop().get("decision"), "block", phase)

    def test_blocks_on_dirty_main_then_honours_stop_hook_active(self):
        self.start_session()
        self.seed_M()
        self.assertNotEqual(self.stop().get("decision"), "block", "clean state allows")
        self.repo.touch(self.repo.rt("dirty-main"))
        out = self.stop()
        self.assertEqual(out.get("decision"), "block", out)
        self.assertIn("forge-status", out["reason"])
        self.assertEqual(self.repo.read(self.repo.rt("stop-blocks")).strip(), "1")
        self.assertEqual(self.repo.read(self.repo.rt("last-block.sha")).strip(), self.status_sha())
        out = self.stop(active=True)
        self.assertNotEqual(out.get("decision"), "block", "never re-block on an unchanged STATUS")
        # the architect records the state: dirty-main is cleared by a writing forge-status command
        self.repo.forge_status("stale")
        self.assertFalse(self.repo.exists(self.repo.rt("dirty-main")))
        self.assertNotEqual(self.stop().get("decision"), "block")

    def test_dirty_worker_reason(self):
        self.seed_M("running", agent_id="agent_b1")
        self.repo.touch(self.repo.rt("dirty-worker"))
        out = self.stop()
        self.assertEqual(out.get("decision"), "block", out)
        self.assertTrue("step-report" in out["reason"] or "step-verdict" in out["reason"], out["reason"])

    def test_hand_edited_status_reason(self):
        self.seed_M()
        st = self.repo.status()
        st["task"]["resume_hint"] = "edited by hand"
        self.repo.write_json(".forge/STATUS.json", st)
        out = self.stop()
        self.assertEqual(out.get("decision"), "block", out)
        self.assertIn("restamp", out["reason"])

    def test_chat_turn_exemption(self):
        self.seed_M()
        st = self.repo.status()
        st["task"]["resume_hint"] = "edited by hand"
        self.repo.write_json(".forge/STATUS.json", st)
        self.repo.touch(self.repo.rt("chat-turn"))
        self.assertNotEqual(self.stop().get("decision"), "block", "a ? turn with no mutation is allowed")
        self.repo.touch(self.repo.rt("dirty-main"))
        self.assertEqual(self.stop().get("decision"), "block", "dirty-* overrides the chat exemption")

    def test_two_block_soft_cap(self):
        self.seed_M()
        self.hook({"hook_event_name": "UserPromptSubmit", "prompt": "go", "session_id": SESSION})
        self.repo.touch(self.repo.rt("dirty-main"))
        self.assertEqual(self.stop().get("decision"), "block")
        self.assertEqual(self.stop().get("decision"), "block")
        out = self.stop()
        self.assertNotEqual(out.get("decision"), "block", out)
        self.assertIn("systemMessage", out)
        self.assertIn("stale", out["systemMessage"].lower())
        self.assertTrue(self.repo.exists(self.repo.rt("stale-status")))
        self.assertIn("stop", self.repo.journal(self.tid).lower())

    def test_block_reason_never_shows_budget(self):
        self.seed_M()
        self.repo.touch(self.repo.rt("dirty-main"))
        out = self.stop()
        self.assertNotIn("$", out.get("reason", ""))
        self.assertNotIn("usd", out.get("reason", "").lower())


class SubagentStopBuilderTests(HookTestCase):
    AGENT = "agent_b1"

    def setUp(self):
        super().setUp()
        self.start_session()
        self.seed_M("running", agent_id=self.AGENT)
        self.repo.bind_agent(self.AGENT)

    def stop(self, message, agent_id=None, agent_type="forge-builder"):
        return self.hook({"hook_event_name": "SubagentStop", "agent_id": agent_id or self.AGENT, "agent_type": agent_type,
                          "last_assistant_message": message, "stop_hook_active": False, "session_id": SESSION})

    def do_work(self):
        now = int(time.time())
        self.repo.write("lib/mod.py", "def add(a, b):\n    return a + b\n\n\ndef sub(a, b):\n    return a - b\n")
        self.repo.add_evidence(self.tid, self.AGENT, "forge-builder", "edit", ts=now - 10, kind="source", file="lib/mod.py")
        self.repo.write_check_record(self.tid, self.AGENT and "01", self.AGENT, ts=now)

    def test_blocks_a_message_without_handoff_headings(self):
        out = self.stop("I changed lib/mod.py and all tests pass.")
        self.assertEqual(out.get("decision"), "block", out)
        self.assertTrue(out["reason"])
        self.assertIn("gate_block", self.repo.ledger_events())
        self.assertFalse(self.repo.exists(f".forge/tasks/{self.tid}/report-01.json"))
        self.assertEqual(self.repo.step()["status"], "running")

    def test_unbound_agent_is_blocked(self):
        self.repo.agent_record("agent_zz", "forge-builder")
        out = self.stop("## Where things stand\nx\n", agent_id="agent_zz")
        self.assertEqual(out.get("decision"), "block", out)
        self.assertIn("brief", out["reason"].lower())

    def test_valid_handoff_is_allowed_persisted_committed_and_reported(self):
        self.do_work()
        head_before = self.repo.head()
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py"])
        out = self.stop(text)
        self.assertNotEqual(out.get("decision"), "block", out)
        self.assertTrue(self.repo.exists(f".forge/tasks/{self.tid}/report-01.md"))
        rj = self.repo.read_json(f".forge/tasks/{self.tid}/report-01.json")
        self.assertEqual(rj["status"], "DONE")
        self.assertEqual(rj["files_changed"], ["lib/mod.py"])
        head = self.repo.head()
        self.assertNotEqual(head, head_before, "the gate commits the step")
        self.assertEqual(rj["commit"], head)
        self.assertIn(f"forge({self.tid}/01)", self.repo.last_commit_message())
        self.assertIn("[attempt 1]", self.repo.last_commit_message())
        committed = common.git_diff_names(self.repo.root, head_before, head)
        self.assertIn("lib/mod.py", committed)
        self.assertTrue(all(p == "lib/mod.py" or p.startswith(f".forge/tasks/{self.tid}/") for p in committed), committed)
        step = self.repo.step()
        self.assertEqual(step["status"], "reported")
        self.assertEqual(step["commit"], head)
        self.assertIn("forge-verifier", self.repo.task()["next_action"])
        attempts = [r for r in self.repo.ledger() if r.get("event") == "attempt"]
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]["gate_blocks"], 0)
        self.assertEqual(attempts[0]["status"], "DONE")
        self.assertFalse(self.repo.exists(self.repo.rt("dirty-worker")))

    def test_blocked_handoff_needs_no_records_and_makes_no_commit(self):
        head = self.repo.head()
        text = self.repo.write_report_md(self.tid, "01", "BLOCKED", [])
        out = self.stop(text)
        self.assertNotEqual(out.get("decision"), "block", out)
        self.assertEqual(self.repo.head(), head)
        self.assertEqual(self.repo.read_json(f".forge/tasks/{self.tid}/report-01.json")["status"], "BLOCKED")
        self.assertIn(self.repo.step()["status"], ("blocked", "reported"))

    def test_two_blocks_then_unverified(self):
        head = self.repo.head()
        bad = "## Where things stand\nno json here\n"
        self.assertEqual(self.stop(bad).get("decision"), "block")
        self.assertEqual(self.stop(bad).get("decision"), "block")
        out = self.stop(bad)
        self.assertNotEqual(out.get("decision"), "block", "after two blocks the gate allows")
        rj = self.repo.read_json(f".forge/tasks/{self.tid}/report-01.json")
        self.assertEqual(rj["status"], "UNVERIFIED")
        self.assertEqual(self.repo.head(), head, "no commit for an UNVERIFIED handoff")
        attempts = [r for r in self.repo.ledger() if r.get("event") == "attempt"]
        self.assertEqual(attempts[-1]["gate_blocks"], 2)

    def test_pre_validation_matches_the_gate(self):
        self.do_work()
        text = self.repo.write_report_md(self.tid, "01", "DONE", ["lib/mod.py", "lib/util.py"])   # util undeclared in tree? no: not changed; fine
        code, out, err = self.repo.run_cli("forge-gate", "--handoff", self.tid, "01", "--from-stdin", "--agent", self.AGENT, stdin=text)
        hook_out = self.stop(text)
        self.assertEqual(code == 0, hook_out.get("decision") != "block", (out, hook_out))


class SubagentStopVerifierTests(HookTestCase):
    VERIFIER = "agent_v1"

    def setUp(self):
        super().setUp()
        self.start_session()
        self.seed_M("verifying", agent_id="agent_b1", commit=self.repo.head())
        self.hook({"hook_event_name": "SubagentStart", "agent_id": self.VERIFIER, "agent_type": "forge-verifier", "session_id": SESSION})

    def stop(self, message):
        return self.hook({"hook_event_name": "SubagentStop", "agent_id": self.VERIFIER, "agent_type": "forge-verifier",
                          "last_assistant_message": message, "stop_hook_active": False, "session_id": SESSION})

    def test_blocks_invalid_verdict(self):
        out = self.stop("Looks good to me. PASS.")
        self.assertEqual(out.get("decision"), "block", out)
        self.assertEqual(self.repo.step()["status"], "verifying")

    def test_valid_pass_persists_and_completes_the_step(self):
        self.repo.write_check_record(self.tid, "01", self.VERIFIER)
        text = self.repo.write_verdict_md(self.tid, "01", "PASS")
        out = self.stop(text)
        self.assertNotEqual(out.get("decision"), "block", out)
        self.assertTrue(self.repo.exists(f".forge/tasks/{self.tid}/verdict-01.md"))
        vj = self.repo.read_json(f".forge/tasks/{self.tid}/verdict-01.json")
        self.assertEqual(vj["verdict"], "PASS")
        step = self.repo.step()
        self.assertEqual(step["status"], "done")
        self.assertTrue(step["verdict"])
        rows = [r for r in self.repo.ledger() if r.get("event") == "verdict"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["verdict"], "PASS")
        self.assertEqual(rows[0]["gate_blocks"], 0)
        self.assertFalse(self.repo.exists(self.repo.rt("dirty-worker")))

    def test_valid_fail_marks_the_step_failed(self):
        self.repo.write_check_record(self.tid, "01", self.VERIFIER, results=[{"name": "lib-unit", "cmd": LIB_UNIT, "exit": 1, "dur_s": 0.1, "tail": "FAIL"}])
        text = self.repo.write_verdict_md(self.tid, "01", "FAIL", criteria=[{"id": "DoD-1", "result": "FAIL", "cmd": LIB_UNIT, "exit": 1}],
                                          blocking=["suite red"], tags=["no-check-run"])
        out = self.stop(text)
        self.assertNotEqual(out.get("decision"), "block", out)
        self.assertEqual(self.repo.step()["status"], "failed")
        self.assertEqual(self.repo.task()["escalation"]["round"], 1)

    def test_two_blocks_then_unknown(self):
        bad = "## Verdict\nPASS\n"
        self.assertEqual(self.stop(bad).get("decision"), "block")
        self.assertEqual(self.stop(bad).get("decision"), "block")
        out = self.stop(bad)
        self.assertNotEqual(out.get("decision"), "block")
        vj = self.repo.read_json(f".forge/tasks/{self.tid}/verdict-01.json")
        self.assertEqual(vj["verdict"], "UNKNOWN")
        self.assertNotEqual(self.repo.step()["status"], "done")


class SubagentStopPlannerTests(HookTestCase):
    def setUp(self):
        super().setUp()
        task = make_task(self.tid, "M", "plan", steps=[], plan=None, plan_author=None,
                         routing={"mode": "single", "builder": None, "verifier": None, "justification": "fixture"})
        self.repo.seed_status(task=task)
        self.hook({"hook_event_name": "SubagentStart", "agent_id": "agent_p1", "agent_type": "forge-planner", "session_id": SESSION})

    def stop(self, message):
        return self.hook({"hook_event_name": "SubagentStop", "agent_id": "agent_p1", "agent_type": "forge:forge-planner",
                          "last_assistant_message": message, "stop_hook_active": False, "session_id": SESSION})

    def test_blocks_without_a_valid_plan(self):
        out = self.stop(f"Plan written.\nPLAN-FILE: .forge/tasks/{self.tid}/plan.md")
        self.assertEqual(out.get("decision"), "block", out)

    def test_blocks_without_plan_file_line(self):
        self.repo.write_brief(self.tid)
        self.repo.write_plan(self.tid, "M")
        out = self.stop("Plan written; see plan.md.")
        self.assertEqual(out.get("decision"), "block", out)
        self.assertIn("PLAN-FILE", out["reason"])

    def test_allows_a_valid_plan(self):
        self.repo.write_brief(self.tid)
        self.repo.write_plan(self.tid, "M")
        out = self.stop(f"Plan written.\nPLAN-FILE: .forge/tasks/{self.tid}/plan.md")
        self.assertNotEqual(out.get("decision"), "block", out)


class OtherEventTests(HookTestCase):
    def test_pre_compact_manual_blocks_only_when_dirty(self):
        self.seed_M()
        self.assertEqual(self.hook({"hook_event_name": "PreCompact", "trigger": "manual"}), {})
        self.repo.touch(self.repo.rt("dirty-main"))
        out = self.hook({"hook_event_name": "PreCompact", "trigger": "manual"})
        self.assertEqual(out.get("decision"), "block", out)
        self.assertIn("forge-status", out["reason"])
        self.assertEqual(self.hook({"hook_event_name": "PreCompact", "trigger": "auto"}), {}, "never block auto")

    def test_config_change_guards_forge_hooks(self):
        out = self.hook({"hook_event_name": "ConfigChange", "source": "project_settings", "file_path": ".claude/settings.json"})
        self.assertNotEqual(out.get("decision"), "block", "identical settings pass")
        settings = self.repo.read_json(".claude/settings.json")
        del settings["hooks"]["Stop"]
        self.repo.write_json(".claude/settings.json", settings)
        out = self.hook({"hook_event_name": "ConfigChange", "source": "project_settings", "file_path": ".claude/settings.json"})
        self.assertEqual(out.get("decision"), "block", out)
        self.assertIn("forge-doctor", out["reason"])
        self.repo.touch(self.repo.rt("gate-disabled-Stop"))
        out = self.hook({"hook_event_name": "ConfigChange", "source": "project_settings", "file_path": ".claude/settings.json"})
        self.assertNotEqual(out.get("decision"), "block", "a disabled gate exempts the entry")

    def test_config_change_keeps_non_forge_hooks_out_of_it(self):
        settings = self.repo.read_json(".claude/settings.json")
        settings["hooks"]["Stop"].append({"hooks": [{"type": "command", "command": "echo mine"}]})
        self.repo.write_json(".claude/settings.json", settings)
        out = self.hook({"hook_event_name": "ConfigChange", "source": "project_settings", "file_path": ".claude/settings.json"})
        self.assertNotEqual(out.get("decision"), "block", out)

    def test_stop_failure_writes_an_incident(self):
        self.seed_M()
        self.hook({"hook_event_name": "StopFailure", "error": "api timeout", "session_id": SESSION})
        files = os.listdir(self.repo.path(".forge/incidents"))
        self.assertTrue([f for f in files if f.endswith("-stopfailure.json")], files)
        self.assertIn("stopfailure", self.repo.journal(self.tid).lower())

    def test_session_end_writes_last_session(self):
        self.seed_M("running", agent_id="agent_b1")
        self.hook({"hook_event_name": "SessionEnd", "reason": "exit", "session_id": SESSION})
        rec = self.repo.read_json(self.repo.rt("last-session.json"))
        self.assertEqual(rec["session_id"], SESSION)
        self.assertEqual(rec["reason"], "exit")
        self.assertEqual(rec["task"], self.tid)
        self.assertEqual(rec["phase"], "execute")
        self.assertEqual(rec["step_running"], "01")
        self.assertIsInstance(rec["ts"], int)


if __name__ == "__main__":
    unittest.main()
