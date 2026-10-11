#!/usr/bin/env bash
# hook_smoke.sh — replay one representative stdin per hook event against a throwaway repo.
#
# Builds a disposable git repo under ${TMPDIR:-/tmp}, copies forge/payload/.forge and dot-claude (as .claude) into it,
# writes a minimal binding.json, STATUS.json, plan.md and brief-01.md inline, then pipes one stdin JSON
# per event into .forge/bin/forge-hook and prints PASS/FAIL per event. Needs the real forgelib modules
# (common, gates, checks, status, hooks); the spawn-guard case FAILs honestly when status.py is absent.
#
#   bash forge/tests/hook_smoke.sh            # exit 0 when every event passed
#   KEEP=1 bash forge/tests/hook_smoke.sh     # keep the throwaway repo (path printed)
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
PAYLOAD=${PAYLOAD:-$HERE/../payload}
R=$(mktemp -d "${TMPDIR:-/tmp}/forge-hook-smoke.XXXXXX")
export CLAUDE_PROJECT_DIR="$R"
export CLAUDE_ENV_FILE="$R/.env-file"
PASS=0; FAIL=0

hk() { echo "$1" | "$R/.forge/bin/forge-hook" ${2:-}; }
report() {  # report <event> <ok 0|1> <detail>
  if [[ "$2" == 0 ]]; then PASS=$((PASS + 1)); printf 'PASS %-34s %s\n' "$1" "$3"; else FAIL=$((FAIL + 1)); printf 'FAIL %-34s %s\n' "$1" "$3"; fi
}
jget() { python3 -c 'import sys,json
d=sys.stdin.read().strip()
o=json.loads(d) if d else {}
cur=o
for k in sys.argv[1].split("."):
    cur=cur.get(k) if isinstance(cur,dict) else None
print("" if cur is None else cur)' "$1"; }

# ---- throwaway repo ------------------------------------------------------------------------------
cd "$R" || exit 2
git init -q . && git config user.email smoke@forge && git config user.name smoke && git config commit.gpgsign false
cp -R "$PAYLOAD/.forge" . && cp -R "$PAYLOAD/dot-claude" .claude
rm -rf .forge/bin/__pycache__ .forge/bin/forgelib/__pycache__
mkdir -p lib .forge/tasks/T-0001 .forge/lessons .forge/.runtime .claude/agent-memory
printf 'def add(a, b):\n    return a + b\n' > lib/foo.py
printf 'import unittest\nfrom foo import add\nclass T(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(1, 2), 3)\n' > lib/test_foo.py
printf '# lessons\n- smoke lesson\n' > .forge/lessons/INDEX.md
[[ -f .forge/ROLE-architect.md ]] || printf '# Role: Forge architect (smoke stand-in)\n' > .forge/ROLE-architect.md
printf '.forge/.runtime/\n.forge/incidents/\n__pycache__/\n' > .gitignore
cat > .forge/binding.json <<'EOF'
{"schema_version": 2, "project": "smoke", "stack": "python", "bootstrap": "true", "smoke": "true",
 "verify": [{"name": "lib-unit", "cmd": "cd lib && python3 -m unittest -q", "when": "always"}],
 "test_globs": ["lib/test_*.py"], "test_pattern": "^\\s*def test_",
 "protected_paths": [".github/workflows/*.yml"], "risk_paths": ["**/*upload*"], "important_paths": [],
 "mechanic_denied_paths": ["lib/route_common.py"], "risk_words": ["secret"],
 "irreversible_commands": ["git push *", "wrangler *"],
 "git": {"branch_per_task": false, "commit_prefix": "forge", "worktree_isolation": false},
 "budgets": {"T": 1, "S": 3, "M": 10, "M_chain": 12, "W": 25, "L_unit": 2, "X": 30, "risk_multiplier": 1.5},
 "routing": {"architect_effort": "medium", "m_builder": "opus-medium", "overrides": [], "measured": {}},
 "clear_policy": "phase", "auto_resume": true, "driver": {"max_turns": 120, "max_phases": 12}, "notes": []}
EOF
if [[ ! -f .claude/settings.forge.json ]]; then
cat > .claude/settings.forge.json <<'EOF'
{"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 15}]}],
           "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.forge/bin/forge-hook", "timeout": 15, "onFailure": "block"}]}]}}
EOF
fi
cp .claude/settings.forge.json .claude/settings.json
python3 - "$R" <<'EOF'
import hashlib, json, os, sys, time
r = sys.argv[1]; now = int(time.time()); iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
scope = ["lib/foo.py", "lib/test_foo.py"]; check = "cd lib && python3 -m unittest -q"
step = {"id": "01", "title": "smoke step", "agent": "forge-builder", "model": "opus", "effort": "medium", "status": "pending",
        "attempts": 0, "from": None, "verify_attempts": 0, "started_at": None, "started_ts": None, "started_by": None,
        "agent_id": None, "base": None, "commit": None, "brief": ".forge/tasks/T-0001/brief-01.md", "report": None,
        "verdict": None, "red_ok_until": None, "allowed_paths": scope, "mechanical": False, "max_tool_calls": 60}
task = {"id": "T-0001", "title": "smoke task", "class": "M", "risk": "none", "size_source": "declared", "files": scope,
        "creates": [], "signals": {"files": 2, "dirs": 1, "importers": 0, "recent_cochanges": [], "tests_present": True,
                                   "risk_hits": [], "important_hits": []},
        "class_justification": "two declared files, one chain, tests present", "phase": "execute",
        "plan": ".forge/tasks/T-0001/plan.md", "plan_author": "architect", "branch": None, "scope": scope,
        "routing": {"mode": "single", "builder": {"agent": "forge-builder", "model": "opus", "effort": "medium"},
                    "verifier": {"agent": "forge-verifier", "model": "opus", "effort": "medium"}, "justification": "smoke"},
        "steps": [step], "escalation": {"step": None, "round": 0}, "next_action": "Dispatch forge-builder (opus/medium) on brief-01",
        "resume_hint": "smoke", "evidence_count": 0, "evidence": [], "blocked_on": None, "external": None,
        "budget": {"cap_usd": 10.0}, "opened_at": iso, "base": None}
st = {"schema_version": 2, "forge_version": "1.0.0", "project": "smoke", "updated_at": iso, "updated_ts": now,
      "updated_by": {"session_id": "cli", "cmd": "smoke"}, "context_state": "fresh", "task": task, "queue": [], "history": []}
p = os.path.join(r, ".forge", "STATUS.json"); json.dump(st, open(p, "w"), indent=2)
open(os.path.join(r, ".forge", ".runtime", "status.sha"), "w").write(hashlib.sha256(open(p, "rb").read()).hexdigest() + "\n")
pm = {"schema": "forge/plan/2", "task": "T-0001", "class": "M", "risk": "none", "chain": False,
      "routing": task["routing"], "steps": [{"id": "01", "title": "smoke step", "brief": "brief-01.md", "agent": "forge-builder",
      "model": "opus", "effort": "medium", "mechanical": False, "red_ok_until": None, "max_tool_calls": 60}],
      "dod": [{"id": "DoD-1", "criterion": "WHEN the suite runs THE SUITE SHALL exit 0", "check": check}],
      "rollback": "git revert <sha>", "test_baseline": {"files": 1, "tests": 1, "recorded_at": iso}, "needs_clarification": []}
with open(os.path.join(r, ".forge/tasks/T-0001/plan.md"), "w") as f:
    f.write("# Plan\n\n```json\n" + json.dumps(pm) + "\n```\n\n" + "".join(f"## {h}\nbody\n\n" for h in ("Steps", "Validation Criteria", "Routing", "Rollback")))
bm = {"schema": "forge/brief/2", "task": "T-0001", "step": "01", "owner_agent": "forge-builder", "model": "opus", "effort": "medium",
      "allowed_paths": scope, "may_edit_tests": False, "tdd": False, "checks": [check], "expected_fail_first": [], "dod": ["DoD-1"],
      "risk": "none", "red_ok": False, "max_tool_calls": 60, "bootstrap": "true"}
with open(os.path.join(r, ".forge/tasks/T-0001/brief-01.md"), "w") as f:
    f.write("# Brief\n\n```json\n" + json.dumps(bm) + "\n```\n\n" + "".join(f"## {h}\nbody\n\n" for h in
            ("Goal", "Context the worker needs", "Definition of done", "Out of scope / do not touch", "Known failed approaches", "Output contract")))
EOF
git add -A . >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1
echo "throwaway repo: $R"

# ---- one stdin per event -----------------------------------------------------------------------------
out=$(hk '{"hook_event_name":"SessionStart","source":"startup","session_id":"sess-smoke","cwd":"'"$R"'"}')
ctx=$(echo "$out" | jget hookSpecificOutput.additionalContext); title=$(echo "$out" | jget hookSpecificOutput.sessionTitle)
[[ -n "$ctx" && "$title" == "forge T-0001 execute" && -f .forge/.runtime/hooks-alive && "$(cat .forge/.runtime/session-id)" == "sess-smoke" && ! -s "$CLAUDE_ENV_FILE" ]]
report "SessionStart(startup)" $? "digest ${#ctx} chars, title '$title', hooks-alive + session-id, no env exports"

out=$(hk '{"hook_event_name":"SessionStart","source":"startup","session_id":"sess-smoke"}' --role)
[[ "$(echo "$out" | jget hookSpecificOutput.additionalContext)" == *"Role"* ]]
report "SessionStart(--role)" $? "role block injected"

out=$(hk '{"hook_event_name":"SessionStart","source":"startup","session_id":"sess-smoke","agent_type":"forge-builder"}' --role)
[[ -z "$out" ]]; report "SessionStart(--role, subagent)" $? "nothing emitted for a worker"

out=$(hk '{"hook_event_name":"UserPromptSubmit","prompt":"hello","session_id":"sess-smoke"}')
[[ "$(echo "$out" | jget hookSpecificOutput.additionalContext)" == Forge:\ T-0001* && "$(cat .forge/.runtime/stop-blocks)" == 0 ]]
report "UserPromptSubmit" $? "reminder line + stop-blocks reset"

out=$(hk '{"hook_event_name":"PreToolUse","tool_name":"Edit","tool_input":{"file_path":"lib/foo.py"},"session_id":"sess-smoke"}')
[[ "$(echo "$out" | jget hookSpecificOutput.permissionDecision)" == deny ]]
report "PreToolUse(Edit, main, class M)" $? "$(echo "$out" | jget hookSpecificOutput.permissionDecisionReason)"

out=$(hk '{"hook_event_name":"PreToolUse","tool_name":"Edit","tool_input":{"file_path":".forge/binding.json"},"session_id":"sess-smoke"}')
[[ "$(echo "$out" | jget hookSpecificOutput.permissionDecisionReason)" == *policy* ]]
report "PreToolUse(Edit, policy lock)" $? "binding.json denied"

out=$(hk '{"hook_event_name":"PreToolUse","tool_name":"Agent","tool_input":{"subagent_type":"forge-builder","model":"claude-opus-5-5","effort":"medium","prompt":"x"},"session_id":"sess-smoke"}')
status=$(python3 -c 'import json;print(json.load(open(".forge/STATUS.json"))["task"]["steps"][0]["status"])')
[[ -z "$out" && "$status" == running ]]
report "PreToolUse(Agent, spawn guard)" $? "allow + step-start -> step $status ${out:+(output: $out)}"

out=$(hk '{"hook_event_name":"PreToolUse","tool_name":"Agent","tool_input":{"subagent_type":"forge-builder","model":"opus","effort":"medium","prompt":"x"},"session_id":"sess-smoke"}')
[[ "$(echo "$out" | jget hookSpecificOutput.permissionDecision)" == deny ]]
report "PreToolUse(Agent, duplicate dispatch)" $? "review #21: $(echo "$out" | jget hookSpecificOutput.permissionDecisionReason | cut -c1-80)"

out=$(hk '{"hook_event_name":"PreToolUse","tool_name":"Agent","tool_input":{"subagent_type":"forge-scout","isolation":"worktree","prompt":"x"},"session_id":"sess-smoke"}')
[[ "$(echo "$out" | jget hookSpecificOutput.permissionDecision)" == deny ]]
report "PreToolUse(Agent, isolation worktree)" $? "review #16: $(echo "$out" | jget hookSpecificOutput.permissionDecisionReason | cut -c1-80)"

out=$(hk '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git push origin main"},"agent_id":"agent_s1","agent_type":"forge-builder"}')
[[ "$(echo "$out" | jget hookSpecificOutput.permissionDecision)" == deny ]]
report "PreToolUse(Bash, worker git push)" $? "$(echo "$out" | jget hookSpecificOutput.permissionDecisionReason)"

out=$(hk '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"echo x > .forge/tasks/T-0001/brief-01.md"},"agent_id":"agent_s1","agent_type":"forge-builder"}')
[[ "$(echo "$out" | jget hookSpecificOutput.permissionDecision)" == deny ]]
report "PreToolUse(Bash, worker .forge write)" $? "review #6: $(echo "$out" | jget hookSpecificOutput.permissionDecisionReason | cut -c1-80)"

out=$(hk '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git -C . reset --hard"},"agent_id":"agent_s1","agent_type":"forge-builder"}')
[[ "$(echo "$out" | jget hookSpecificOutput.permissionDecision)" == deny ]]
report "PreToolUse(Bash, worker git -C reset)" $? "review #32: $(echo "$out" | jget hookSpecificOutput.permissionDecisionReason | cut -c1-80)"

out=$(hk '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git push origin main"},"session_id":"sess-smoke"}')
[[ "$(echo "$out" | jget hookSpecificOutput.permissionDecision)" == ask ]]
report "PreToolUse(Bash, main irreversible)" $? "ask in interactive mode"

out=$(hk '{"hook_event_name":"SubagentStart","agent_id":"agent_s1","agent_type":"forge-builder","session_id":"sess-smoke"}')
[[ -n "$(echo "$out" | jget hookSpecificOutput.additionalContext)" && -f .forge/.runtime/agents/agent_s1.json ]]
report "SubagentStart" $? "one-line context + agents/agent_s1.json"

out=$(hk '{"hook_event_name":"PostToolUse","tool_name":"Read","tool_input":{"file_path":".forge/tasks/T-0001/brief-01.md"},"tool_response":{},"agent_id":"agent_s1","agent_type":"forge-builder"}')
bound=$(python3 -c 'import json;print(json.load(open(".forge/STATUS.json"))["task"]["steps"][0]["agent_id"])')
[[ -z "$out" && "$bound" == agent_s1 ]]
report "PostToolUse(Read, brief bind)" $? "step.agent_id=$bound"

out=$(hk '{"hook_event_name":"PostToolUse","tool_name":"Edit","tool_input":{"file_path":"lib/foo.py"},"tool_response":{},"agent_id":"agent_s1","agent_type":"forge-builder"}')
grep -q '"event":"edit".*"kind":"source".*"file":"lib/foo.py"' .forge/tasks/T-0001/evidence.jsonl
report "PostToolUse(Edit, evidence)" $? "$(tail -1 .forge/tasks/T-0001/evidence.jsonl)"

out=$(hk '{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","tool_input":{"command":"pytest x"},"error":"exit code 2: boom","agent_id":"agent_s1","agent_type":"forge-builder"}')
grep -q '"event":"bash","ok":false,"exit":2' .forge/tasks/T-0001/evidence.jsonl
report "PostToolUseFailure(Bash)" $? "$(tail -1 .forge/tasks/T-0001/evidence.jsonl)"

out=$(hk '{"hook_event_name":"SubagentStop","agent_id":"agent_s1","agent_type":"forge-builder","stop_hook_active":false,"last_assistant_message":"## Where things stand\nnot a handoff"}')
[[ "$(echo "$out" | jget decision)" == block ]]
report "SubagentStop(builder, handoff gate)" $? "blocked: $(echo "$out" | jget reason | head -2 | tr '\n' ' ')"

touch .forge/.runtime/dirty-main; echo 0 > .forge/.runtime/stop-blocks
out=$(hk '{"hook_event_name":"Stop","stop_hook_active":false,"session_id":"sess-smoke"}')
[[ "$(echo "$out" | jget decision)" == block ]]
report "Stop(dirty-main)" $? "$(echo "$out" | jget reason)"

out=$(hk '{"hook_event_name":"PreCompact","trigger":"manual"}')
[[ "$(echo "$out" | jget decision)" == block ]]
report "PreCompact(manual, dirty)" $? "$(echo "$out" | jget reason)"
rm -f .forge/.runtime/dirty-main

python3 - <<'EOF'
import json; p=".claude/settings.json"; s=json.load(open(p)); s["hooks"].pop("Stop", None); json.dump(s, open(p, "w"))
EOF
out=$(hk '{"hook_event_name":"ConfigChange","source":"project_settings","file_path":".claude/settings.json"}')
[[ "$(echo "$out" | jget decision)" == block ]]
report "ConfigChange(Forge hook dropped)" $? "$(echo "$out" | jget reason)"
cp .claude/settings.forge.json .claude/settings.json

out=$(hk '{"hook_event_name":"StopFailure","error":"rate_limit","session_id":"sess-smoke"}')
ls .forge/incidents/*-stopfailure.json >/dev/null 2>&1
report "StopFailure" $? "$(ls .forge/incidents 2>/dev/null | head -1)"

out=$(hk '{"hook_event_name":"SessionEnd","reason":"other","session_id":"sess-smoke"}')
[[ "$(jget session_id < .forge/.runtime/last-session.json)" == sess-smoke ]]
report "SessionEnd" $? "last-session.json written"

echo "not json" | "$R/.forge/bin/forge-hook" >/dev/null 2>&1
report "garbage stdin exits 0" $? "exit code $?"

# ---- --plugin in a repository without a Forge install: silent, writes nothing (reviews #1/#2/#37) ---------
F=$(mktemp -d "${TMPDIR:-/tmp}/forge-hook-smoke-foreign.XXXXXX")
git init -q "$F" && printf 'x = 1\n' > "$F/a.py"
out=$(cd "$F" && echo '{"hook_event_name":"PreToolUse","tool_name":"Edit","tool_input":{"file_path":"a.py"},"session_id":"s"}' \
      | CLAUDE_PROJECT_DIR="$F" FORGE_ROOT= "$R/.forge/bin/forge-hook" --plugin 2>/dev/null)
out2=$(cd "$F" && echo '{"hook_event_name":"SessionStart","source":"startup","session_id":"s"}' \
      | CLAUDE_PROJECT_DIR="$F" FORGE_ROOT= CLAUDE_ENV_FILE="$F/.env" "$R/.forge/bin/forge-hook" --plugin 2>/dev/null)
[[ -z "$out" && -z "$out2" && ! -e "$F/.forge" && ! -e "$F/.env" ]]
report "--plugin in a foreign repo" $? "no output, no .forge/ created"
rm -rf "$F"

echo
echo "hook_smoke: $PASS passed, $FAIL failed"
if [[ "${KEEP:-0}" == 1 ]]; then echo "kept $R"; else rm -rf "$R"; fi
[[ $FAIL == 0 ]]
