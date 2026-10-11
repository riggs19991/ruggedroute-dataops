# Requirements brief — AI Engineering Team system ("the Forge")

## What the user asked for (verbatim intent)
- An ecosystem of rules and processes, with hand-offs and AUTOMATIC CONTEXT CLEARING after a context/status update markdown file is written.
- Every piece of work starts with a very well thought-out plan.
- Routing by importance and model capability to save usage: Fable 5.1 (the master architect, this model) codes the extremely difficult tasks; Opus handles easier ones; Sonnet/Haiku used as the architect sees fit, or not at all.
- Reusable across projects: ruggedroute-dataops (this repo), the RuggedRoute Android app (Kotlin/Jetpack Compose/Mapbox/Firebase), "Millwright KB" (a knowledge base app), and future apps.
- Highly documented so it survives between sessions and can be "called upon" when working on other projects.
- "Monster team of AI engineers, most efficient and effective way possible." Not budget-light to build; the SYSTEM itself must save usage at run time.

## Hard facts established (Oct 2026)
- Claude Code 2.1.296 installed. Model aliases: fable, opus, sonnet, haiku (+ full ids). Effort: low|medium|high|xhigh|max. `--autocompact`, `--bg` background sessions, `claude agents`, `claude ultrareview`, `claude plugin validate <path>`.
- Pricing (per MTok in/out): Fable 5.1 $10/$50; Opus 5.5 $4/$20; Sonnet 5.5 $2/$10; Haiku 5.5 $0.10/$0.50 (≤100K prompt). Cache reads ~$0.20-0.25.
- Hook events present in binary: SessionStart, SessionEnd, UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, Notification, Stop, StopFailure, SubagentStart, SubagentStop, PreCompact, PostCompact, PermissionRequest, TeammateIdle, TaskCompleted, ConfigChange, Elicitation, ElicitationResult, WorktreeCreate, WorktreeRemove, InstructionsLoaded, FileChanged, CwdChanged.
- Hook outputs include: hookSpecificOutput.additionalContext, permissionDecision(+Reason), systemMessage, decision, updatedInput, suppressOriginalPrompt, blockingError, continue/stopReason. Stop hook input includes stop_hook_active + last_assistant_message.
- Saved workflows: `.claude/workflows/<name>.js` (Workflow tool `{name}`), plus `.claude/routines/`.
- Plugin layout (from `claude plugin init`): `.claude-plugin/plugin.json`, `skills/<name>/SKILL.md`, `agents/<name>.md`, `hooks/hooks.json` using `${CLAUDE_PLUGIN_ROOT}`. Auto-load dir: `~/.claude/skills/<name>/` as `<name>@skills-dir`.
- Agent frontmatter keys present: name, description, tools, disallowedTools, model, effort, permissionMode, maxTurns, memory, skills, hooks, mcpServers, isolation, background. `model: inherit` supported.
- Skill frontmatter keys: disable-model-invocation, user-invocable, allowed-tools, argument-hint, context, agent.
- The user already has a (dated, manual copy/paste) "dual-agent-orchestrator" skill with an Opus plan template (Objective, Current/Target state, File manifest, Dependency order, Steps w/ Verify, Validation criteria, Anti-patterns, Escalation points). Keep those fields; automate the handoff.

## Anthropic guidance that constrains the design (from the claude-api skill, Oct 2026)
- Fable 5.1: de-prescribe prompts (goals+constraints, not steps); fresh-context verifier sub-agents beat self-critique; use async sub-agents freely; give it a memory surface (one lesson per file); ground progress claims on tool evidence; "operating autonomously" + "Delivering work" blocks for long runs; explicit compaction-summary retention list.
- Opus 5.5: default effort medium — set explicitly; strong agentic coding. Sonnet 5.5: start medium for agentic coding; add the "run a real check before reporting done" paragraph. Haiku 5.5: high-volume checkable work only, not long agentic loops; "keep working until done" line at low effort.
- Cost evidence: orchestrator (frontier plans, cheap workers execute) pays ONLY when there is bulk, parallel, independent work; for one dependent chain that fits one context, the frontier model alone at lower effort wins. "Run cheap first, re-run failures at higher effort/model" holds pass rate at ~half cost when a failure signal (tests) exists. Price the tail: the hardest 10% decides the bill. Fable at low effort is often cheaper per solved task than Opus/Sonnet.

## Consumer-project facts (first consumer = this repo)
- ruggedroute-dataops: Python 3.11/3.12, GitHub Actions pipelines, tests via `cd lib && python3 -m unittest -v` and `pytest layers/<layer>/tests -q`; Cloudflare worker in worker-tiles/ (npm). Design rules in README (versioned uploads, bulk downloads system-of-record, tolerant normalizers, ODbL isolation, no owner names in tiles).
- Other consumers: RuggedRoute Android app (Kotlin, Compose, Mapbox v11, Firebase, Hilt, MVVM; AMP design tokens), Millwright KB (unknown stack), future apps.

## Non-negotiables for the design
1. Plan-first: no non-trivial work without a written plan file; the plan includes routing decisions with justification.
2. Explicit handoff documents between phases/agents with a fixed schema; status file is the single source of truth for "where are we".
3. Automatic context clearing after the status/handoff file is written — must be mechanically enforced (hooks), not just "remembered".
4. Routing matrix by difficulty/importance/blast-radius → model+effort, with the "don't over-orchestrate" rule and the cheap-first-escalate-on-failure rule built in.
5. Verification gates: fresh-context reviewers; definition-of-done; tests actually run; progress claims audited against evidence.
6. Portable: install into any repo with one command (plugin via marketplace or git), plus a thin per-project binding file. Zero dependency on this session's memory.
7. Self-documenting: a runbook, a decision log, a lessons/memory surface, and an entrypoint doc that lets a fresh session bootstrap in one read.
8. Versioned: the system itself has a version and a changelog.

## CRITICAL verified constraint on "automatic context clearing"
- research-claude-code.md §2: triggering `/clear` or `/compact` from a hook is NOT documented; no hook output field does it. Do not invent one.
- What IS mechanically available: (a) `SessionStart` with matcher `startup|resume|clear|compact` can inject up to 10,000 chars of `additionalContext` (e.g. the status/handoff file) on every fresh start and after every compaction; (b) `Stop`/`SubagentStop` hooks can BLOCK ending a turn (exit 2 or `decision:"block"` + reason) until a condition holds (e.g. status file updated this turn), guarded by `stop_hook_active` and an 8-continuation cap; (c) `PreCompact` can block compaction; `PostCompact` sees the summary; (d) disposable contexts via subagents (`Agent` tool / `.claude/agents`) and skills with `context: fork` — work done there never enters the orchestrator's context, only the returned handoff does; (e) `claude -p` / `claude --bg` / cloud `create_session` start genuinely fresh contexts for a phase; (f) `/clear [name]` and `/compact <focus>` are user/model-issued commands.
- Therefore "automatic context clearing after the status update" must be designed as: phase work in disposable contexts + a Stop-gate that refuses to end a phase until STATUS/handoff is written + SessionStart re-injection of the status file + an explicit, documented "end of phase" ritual (write handoff -> the orchestrator either returns from the fork or instructs `/clear`). Label honestly which parts are guaranteed vs instructed.

## CRITICAL verified constraint on portability (research-claude-code.md §6)
- Cloud sessions NEVER add `extraKnownMarketplaces`; external-source plugins enabled only in project settings are NOT fetched for collaborators (each person must `claude plugin install <name>@<marketplace> --scope project`).
- Reliable zero-install patterns: (a) a plugin directory committed INSIDE the consumer repo under `.claude/skills/<name>/` with `.claude-plugin/plugin.json` auto-loads as `<name>@skills-dir` in every session, local or cloud; (b) relative-path plugins inside the same marketplace repo load directly. So: the canonical system lives in one git repo (acts as marketplace + source of truth) AND is vendored into each consumer repo under `.claude/skills/forge/` via a one-command install/update script (git subtree or curl+tar), with a VERSION file to detect drift. Plugin subagents lose `hooks`, `mcpServers`, `permissionMode` — ship hooks at plugin level (`hooks/hooks.json`).
- Validate with `claude plugin validate --strict <path>`.

## Verified primitives that the design SHOULD exploit (research-claude-code.md §1-§7)
- `SessionStart` stdout may carry `hookSpecificOutput.additionalContext` (≤10,000 chars), `initialUserMessage` (auto-submits a first turn), `sessionTitle`, `watchPaths`, `reloadSkills`. Matchers: `startup|resume|clear|compact|fork`. => after `/clear`, a hook can inject the status file AND auto-submit "resume from STATUS" so the next phase starts itself.
- `Stop` and `SubagentStop` can block (`decision:"block"` + `reason`); input has `stop_hook_active`, `last_assistant_message`, `agent_type`, `agent_transcript_path`. => a Stop gate can refuse to end a phase until the status/handoff file was updated this turn; a SubagentStop gate can refuse a worker's return until its final message contains a well-formed handoff block. 8-continuation cap; must check stop_hook_active.
- `UserPromptSubmit` can inject `additionalContext` per prompt (cheap, small reminders such as current phase + routing rule), `PreToolUse` can deny/allow/ask (e.g., deny Haiku-tier agents from editing risky paths; deny `git push` from workers), `TaskCompleted` can block completion (e.g., until tests ran), `PostToolUse` on `Edit|Write` can run formatters/tests.
- Agent frontmatter: `model` (alias or full id), `effort` (low..max), `tools`/`disallowedTools`, `memory: project` (persistent `.claude/agent-memory/<name>/MEMORY.md`, first 200 lines loaded), `maxTurns`, `background`, `isolation: worktree`, `omitClaudeMd`, `skills` (preload). Plugin agents ignore `hooks`, `mcpServers`, `permissionMode`, `initialPrompt` → put hooks in plugin `hooks/hooks.json`.
- Skills: `context: fork` + `agent:` run the skill body as a self-contained subagent task (disposable context); `disable-model-invocation`, `user-invocable`, `allowed-tools`, `argument-hint`, `$ARGUMENTS`, `!`cmd`` dynamic injection, `hooks:` in skill frontmatter (rest of session), `once`.
- Settings: `plansDirectory` (relative to project root), `agent` (start every session as a named agent), `effortLevel` (no `max`), `modelSettings`, `env.CLAUDE_CODE_SUBAGENT_MODEL`, `env.CLAUDE_CODE_ENABLE_TODO_TOOLS=1`, `attribution`, `permissions.deny/ask/allow` (`Agent(name)`, `Bash(git push *)`, `Edit(path)`), `autoCompactWindow`, `workflowSizeGuideline`.
- Saved workflows: `.claude/workflows/<name>.js` or plugin `workflows/` (namespaced `/<plugin>:<name>`), invoked as `/<name>` or the `Workflow` tool; intermediate results stay out of the main context.
- Subagents may nest 3 deep, 20 concurrent; background subagents return as notifications; completed subagents can be resumed with `SendMessage`; transcripts at `~/.claude/projects/{project}/{sessionId}/subagents/`.
- `claude --agent <name>`, `claude -p --output-format json`, `claude --bg`, `claude agents`, `claude ultrareview`, `claude plugin validate --strict`.

## VERIFIED BY EXPERIMENT in this sandbox (Claude Code 2.1.296, headless `claude -p`, fresh git repo)
- A plugin directory committed under the PROJECT's `.claude/skills/<plugin>/` (with `.claude-plugin/plugin.json`) did NOT load (no plugin, no skills, no agents, no hooks), with or without `enabledPlugins` in project settings.
- Plain project-level components DO load: `.claude/skills/<name>/SKILL.md` and `.claude/agents/<name>.md` appeared in the session's skill/agent lists.
- `claude --plugin-dir <path>` loads the plugin fully (skills namespaced `<plugin>:<skill>`, agents `<plugin>:<agent>`, hooks fire).
- A plugin directory under the USER's `~/.claude/skills/<plugin>/` loads fully as `<plugin>@skills-dir` (hooks fire).
- `claude plugin validate --strict` passes on a minimal manifest {name, version, description, author}.
=> Packaging decision: the SYSTEM MUST SHIP IN PLAIN PROJECT LAYOUT (`CLAUDE.md`, `.claude/settings.json` hooks, `.claude/skills/*`, `.claude/agents/*`, `.claude/rules/*`, `.claude/workflows/*.js`, plus a docs/ tree) so it works in cloud sessions with zero install. A plugin manifest may ADDITIONALLY wrap the same files for user-level install on a developer machine (`~/.claude/skills/forge/`) — optional, secondary. The installer for other repos is a script that copies/updates these plain files (vendoring) and records a VERSION.
- CORRECTION (further experiment): once the project has workspace trust (`hasTrustDialogAccepted: true` in `~/.claude.json` for that path), a plugin vendored under the PROJECT's `.claude/skills/<plugin>/` DOES load fully as `<plugin>@skills-dir` (skills, agents, hooks all active), with or without `enabledPlugins`. Plain project files and project `settings.json` hooks load even when the project is NOT yet trusted. Conclusion unchanged: plain project layout is the robust primary; an in-repo plugin wrapper is a valid secondary form that needs trust. SessionStart hook stdin observed: {cwd, hook_event_name, scratchpad_dir, session_id, source, transcript_path}.

## VERIFIED BY EXPERIMENT: hook gates work headlessly (Claude Code 2.1.296, `claude -p`, Haiku)
- Stop gate: a project-settings `Stop` hook returning `{"decision":"block","reason":"..."}` when STATUS.md is missing made the model write STATUS.md and stop on the next attempt; stdin showed `stop_hook_active:false` then `true`. Guarding on `stop_hook_active` prevented loops.
- SubagentStop gate: a `SubagentStop` hook blocking unless `last_assistant_message` contains `HANDOFF:` made a project agent (`.claude/agents/worker.md`, model haiku) rewrite its final message to include the handoff line; stdin carried `agent_id`, `agent_type` (= agent name), `last_assistant_message`, `stop_hook_active`.
- Hook scripts received `$CLAUDE_PROJECT_DIR` correctly from project `.claude/settings.json`.
=> The status-update gate and the handoff-format gate can be MECHANICALLY GUARANTEED. Design them as such.
