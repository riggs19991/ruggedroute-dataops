"""Doc-consistency tests: the shipped docs, skills, agents and templates must describe what the
code does. Adopted from the post-review doc lint (review findings #24/#41, #56, #57, #58, #61, #63,
#64 and the frontmatter check). Run with: python3 -m unittest discover -s forge/tests
"""
import glob
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.abspath(os.path.join(HERE, ".."))
P = os.path.join(F, "payload")
sys.path.insert(0, os.path.join(P, ".forge", "bin"))
sys.dont_write_bytecode = True
from forgelib import common  # noqa: E402


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    """Very small YAML-subset parser for agent/skill/rule frontmatter: returns dict or raises."""
    if not text.startswith("---\n"):
        raise ValueError("no frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("unterminated frontmatter")
    block = text[4:end]
    out = {}
    key = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith(" ") or line.startswith("\t"):
            if key is None:
                raise ValueError(f"indented line without key: {line!r}")
            continue  # nested map / list item under key
        if ":" not in line:
            raise ValueError(f"bad line: {line!r}")
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val.startswith('"') and not val.endswith('"'):
            raise ValueError(f"unterminated quote in {key}")
        if val and not val.startswith(('"', "'", "[", "{")) and ": " in val:
            raise ValueError(f"unquoted ': ' in value of {key}: {val!r}")
        out[key] = val
    return out


OWNED_DOCS = (glob.glob(P + "/.forge/*.md") + glob.glob(P + "/.forge/templates/*")
              + glob.glob(P + "/dot-claude/agents/*.md") + glob.glob(P + "/dot-claude/skills/*/SKILL.md")
              + glob.glob(P + "/dot-claude/rules/*.md")
              + [F + "/docs/" + n for n in ("ARCHITECTURE.md", "UPGRADING.md", "DESIGN-RATIONALE.md")]
              + [F + "/evals/README.md"])


class DocConsistencyTests(unittest.TestCase):
    def test_payload_has_no_literal_dot_claude_dir(self):
        # Claude Code auto-discovers nested .claude/rules in subdirectories; the payload ships dot-claude.
        self.assertFalse(os.path.exists(P + "/.claude"), "payload/.claude must not exist (use dot-claude)")
        self.assertTrue(os.path.isdir(P + "/dot-claude/agents"))

    def test_frontmatter_is_well_formed(self):
        files = (glob.glob(P + "/dot-claude/agents/*.md") + glob.glob(P + "/dot-claude/skills/*/SKILL.md")
                 + glob.glob(P + "/dot-claude/rules/*.md"))
        self.assertTrue(files)
        for p in files:
            with self.subTest(file=os.path.basename(p)):
                fm = frontmatter(rd(p))
                if "/agents/" in p or "/skills/" in p:
                    self.assertIn("name", fm)
                    self.assertIn("description", fm)
                    self.assertTrue(fm["description"])
                if "/agents/" in p:
                    self.assertEqual(fm["name"], os.path.basename(p)[:-3])
                    self.assertIn("model", fm)
                    self.assertIn("effort", fm)
                if "/skills/" in p:
                    self.assertEqual(fm["name"], os.path.basename(os.path.dirname(p)))
                if "/rules/" in p:
                    self.assertIn("paths", fm)

    def test_scope_add_always_carries_task_id(self):
        for p in OWNED_DOCS:
            for m in re.finditer(r"scope add (\S+)", rd(p)):
                arg = m.group(1).strip("`")
                ok = arg in ("<id>", "<task>", "$ARGUMENTS", "{tid}", "{ctx.task_id}") or arg.startswith("T-") or arg.startswith("<id")
                self.assertTrue(ok, f"{os.path.basename(p)}: `scope add {arg}` lacks the task id")

    def test_runbook_troubleshooting_names_match_doctor(self):
        doc = rd(P + "/.forge/bin/forge-doctor")
        names = set(re.findall(r'rep\.(?:ok|warn|fail)\("([a-z0-9-]+)"', doc)) | set(re.findall(r'rep\.add\([^,]+, "([a-z0-9-]+)"', doc))
        rb = rd(P + "/.forge/RUNBOOK.md")
        self.assertIn("## 12.", rb)
        sec = rb[rb.index("## 12."):]
        rows = set(re.findall(r"^\| `([a-z0-9-]+)`", sec, re.M)) | set(re.findall(r"^\| `[a-z0-9-]+` / `([a-z0-9-]+)`", sec, re.M))
        self.assertTrue(names, "no doctor check names found")
        self.assertLessEqual(rows, names, f"RUNBOOK rows not printed by forge-doctor: {sorted(rows - names)}")
        self.assertLessEqual(names, rows, f"doctor names missing from RUNBOOK §12: {sorted(names - rows)}")

    def test_forge_md_within_cap_and_pointers_exist(self):
        text = rd(P + "/.forge/FORGE.md")
        self.assertLessEqual(len(text.splitlines()), 120)
        for name in re.findall(r"`\.forge/([A-Za-z-]+\.md)`", text):
            self.assertTrue(os.path.exists(P + "/.forge/" + name), f"FORGE.md names missing .forge/{name}")
        for skill in re.findall(r"`/forge-([a-z]+)`", text):
            self.assertTrue(os.path.isdir(P + f"/dot-claude/skills/forge-{skill}"), f"FORGE.md names missing skill forge-{skill}")

    def test_templates_json_blocks_parse_and_headings_match_constants(self):
        for name, headings in (("handoff.md", common.HANDOFF_MANDATORY_HEADINGS), ("handoff-short.md", common.HANDOFF_SHORT_HEADINGS),
                               ("verdict.md", common.VERDICT_HEADINGS), ("plan.md", common.PLAN_HEADINGS_M),
                               ("plan-inline.md", common.PLAN_HEADINGS_INLINE)):
            text = rd(P + "/.forge/templates/" + name)
            block = common.json_block(text)
            self.assertIsNotNone(block, f"{name}: json block missing or invalid")
            present = common.headings(text)
            for h in headings:
                self.assertIn(h, present, f"{name}: heading '{h}' missing")
        for name in ("STATUS.json", "binding.json"):
            json.loads(rd(P + "/.forge/templates/" + name).replace("{{project}}", "x").replace("{{version}}", "1"))

    def test_routing_json_modes_are_valid(self):
        r = json.loads(rd(P + "/.forge/schemas/routing.json"))
        for cls, spec in r["classes"].items():
            self.assertIn(spec["mode"], common.MODES, f"class {cls} mode {spec['mode']!r} is not a routing.mode")

    def test_close_skill_does_not_promise_auto_resume(self):
        text = rd(P + "/dot-claude/skills/forge-close/SKILL.md")
        self.assertNotIn("auto-resume will fire", text)

    def test_anthropic_paragraphs_verbatim(self):
        role = rd(P + "/.forge/ROLE-architect.md")
        self.assertIn("Before reporting progress, audit each claim against a tool result from this session.", role)
        self.assertIn("You are operating autonomously. The user is not watching in real time", role)
        builder = rd(P + "/dot-claude/agents/forge-builder-s.md")
        self.assertIn("run a real check that exercises the change before reporting it done", builder)


if __name__ == "__main__":
    unittest.main()
