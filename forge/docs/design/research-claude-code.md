
# Claude Code primitives reference (as of 2026-10-11)

Sources were fetched from `https://code.claude.com/docs/en/...`. The docs map is at `https://code.claude.com/docs/en/claude_code_docs_map.md`, and the full index is at `https://code.claude.com/docs/llms.txt`. The docs reference releases up to v2.1.296, and many features are gated by minimum versions, which I note where they appear. Pages I did not fetch are listed under "Gaps" at the end.

---

## 1. Subagents

**Sources:** `https://code.claude.com/docs/en/sub-agents`, `https://code.claude.com/docs/en/agent-sdk/typescript` (for the Agent tool input type)

### File locations and precedence

| Location | Scope | Priority |
|---|---|---|
| Managed settings | Organization | 1 (highest) |
| `--agents` CLI flag (JSON) | Current session | 2 |
| `.claude/agents/` | Current project | 3 |
| `~/.claude/agents/` | All projects | 4 |
| Plugin `agents/` directory | Where plugin is enabled | 5 (lowest) |

Files are scanned recursively, so subfolders are allowed. Identity comes from `name`, not the path. Duplicate names in one directory are not reliably resolved, and `/doctor` reports them.

### Frontmatter fields (`.claude/agents/*.md`)

The Markdown body becomes the system prompt. Only `name` and `description` are required. Field names are camelCase. Unrecognized fields are silently ignored.

| Field | Type / allowed values | Default and notes |
|---|---|---|
| `name` | string, required, max 256 chars | Cannot start with `-` or contain `:` (`:` is reserved for plugin IDs such as `my-plugin:reviewer`) |
| `description` | string, required | Tells Claude when to delegate |
| `tools` | comma-separated string or YAML list | Allowlist, e.g. `Read, Grep, Bash`. Preload skills with `skills`, not `Skill` |
| `disallowedTools` | same format as `tools` | Denylist, applied before `tools`. A specifier like `Bash(git push *)` removes the whole tool |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, a full model ID such as `claude-opus-5-5`, or `inherit` | See resolution order below |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max` | Available levels depend on the model. `CLAUDE_CODE_EFFORT_LEVEL` overrides it |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, `manual` (alias of `default`) | Ignored for plugin subagents. If the main session is in `bypassPermissions`, `acceptEdits`, or auto mode, that mode wins |
| `maxTurns` | number | On reaching it, output is returned marked partial and can be resumed |
| `skills` | list of skill names | Full skill content injected at startup (first 32 names). Skills with `disable-model-invocation: true` cannot be preloaded |
| `mcpServers` | list | Each entry is a server name string or an inline `name: {config}`. Ignored for plugin subagents |
| `hooks` | object (`PreToolUse`, `PostToolUse`, `Stop`, etc.) | Scoped to this subagent. Ignored for plugin subagents |
| `memory` | `user`, `project`, `local` | Enables persistent memory (see below) |
| `background` | boolean | `true` keeps it in the background even when Claude asks for foreground |
| `omitClaudeMd` | boolean | `true` skips user, project, and local CLAUDE.md. Requires v2.1.271+ |
| `isolation` | `worktree` only | Runs in a temporary git worktree branched from the default branch. Auto-cleaned if no changes |
| `color` | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` | UI color |
| `initialPrompt` | string | Auto-submitted first turn when run as the main session agent. Ignored for plugin subagents |
| `experimental` | map; `cacheTtl`: `5m` or `1h` | Subagent files only. Requires v2.1.248+ |

Minimal example, verbatim from the docs:

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

Persistent memory example, verbatim: `memory: user` in the frontmatter, with "update your agent memory" in the body.

### Model resolution

Order when `model` is omitted or set by Claude:
1. The per-invocation `model` parameter (Claude can pass this)
2. The definition's `model` frontmatter (`inherit` uses the main conversation's model)
3. `CLAUDE_CODE_SUBAGENT_MODEL`, if set
4. The main conversation's model

`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` makes the variable override the other sources. Note: the SDK's `AgentInput.model` type lists aliases only (`"sonnet" | "opus" | "haiku" | "fable"`). The frontmatter docs accept full IDs.

### Built-in subagent types

| Agent | Model | Tools | Notes |
|---|---|---|---|
| **Explore** | Main conversation's model. On Bedrock, Vertex, and Foundry it stays on the main model. With a subscription or Console account it uses the Opus alias when the main model is Fable | Read-only; Write and Edit denied | Skips CLAUDE.md and git status. Thoroughness set to quick, medium, or very thorough. Cannot be resumed |
| **Plan** | Inherits main model | Read-only; Write and Edit denied | Used during plan mode. Skips CLAUDE.md and git status. Cannot be resumed |
| **general-purpose** | `CLAUDE_CODE_SUBAGENT_MODEL` if set, else main model | All subagent-available tools | Multi-step work with exploration and changes |
| **claude** | Follows model order | All subagent-available tools | Catch-all; default for dispatched background sessions |
| **statusline-setup** | Sonnet | Not stated | Used by `/statusline` |
| **claude-code-guide** | Haiku | Not stated | Answers Claude Code feature questions |

Disable built-ins with `permissions.deny` entries such as `"Agent(Explore)"`, or with `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1` (v2.1.198+). `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1` removes all built-ins in non-interactive mode and the SDK. Deny the `Agent` tool to block all delegation.

### Invocation

1. Automatic delegation: Claude matches the task to each `description`. "Use proactively" helps.
2. Natural language: "Use the test-runner subagent to fix failing tests."
3. @-mention: `@"code-reviewer (agent)"`, or `@agent-<name>` (plugins: `@agent-my-plugin:code-reviewer`).
4. `/agents`: on v2.1.197 and earlier it opened a wizard. Current versions print a reminder to edit the files or ask Claude.
5. `--agent <name>` flag: runs the whole session as that subagent. Plugin agents: `claude --agent my-plugin:security-reviewer`. A custom subagent's prompt replaces the default system prompt unless empty.
6. `agent` setting in `.claude/settings.json`: `{ "agent": "code-reviewer" }`. The CLI flag overrides it.

Programmatic definitions (SDK `agents` option, or `--agents` JSON) use the same fields, with `prompt` as the body.

### Nesting, results, and resumption

- **Can subagents spawn subagents?** Yes, by default up to three layers below the main conversation. The `Agent` tool is removed at the depth limit. Set the limit with `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` (for example `"2"` in `settings.json` `env`; `1` disables nesting). Stop one subagent from spawning by omitting `Agent` from its `tools`. Concurrent limit: 20 by default (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`).
- **Results:** A subagent works in its own context and does not see your history. Its final report returns to the parent. Intermediate tool output stays out of the parent context. Background results arrive as a completion notification in a later turn. An API error returns partial output with a note.
- **Foreground vs background:** Foreground blocks and passes permission prompts through. Background runs concurrently, surfaces prompts in the main session (Esc denies one call), and gets a smaller tool set (Read, Grep, Glob, LSP, Bash, PowerShell, Edit, Write, NotebookEdit, WebFetch, WebSearch, TodoWrite, Skill, ToolSearch, EnterWorktree, ExitWorktree, Monitor, TaskStop, SendMessage, Artifact, SubagentHandback, plus MCP tools). Ctrl+B backgrounds a running task. `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` forces foreground.
- **Resuming:** Completed subagents return an agent ID. Claude resumes one with `SendMessage`, setting `to` to the agent ID or name. Resumed subagents keep full history. Transcripts live at `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl` and are deleted after `cleanupPeriodDays` (default 30).

### Persistent subagent memory

| `memory` value | Directory |
|---|---|
| `user` | `~/.claude/agent-memory/<agent-name>/` |
| `project` | `.claude/agent-memory/<agent-name>/` (shareable via version control; recommended default) |
| `local` | `.claude/agent-memory-local/<agent-name>/` (not checked in) |

- The system prompt includes the first 200 lines or 25KB of `MEMORY.md`.
- `Read`, `Write`, and `Edit` are enabled automatically.
- It is part of auto memory. If auto memory is disabled (`autoMemoryEnabled` or `CLAUDE_CODE_DISABLE_AUTO_MEMORY`), the `memory` field has no effect.

### Plugin subagent restrictions

`hooks`, `mcpServers`, `permissionMode`, and `initialPrompt` are ignored for plugin subagents. Workarounds: copy the file to `.claude/agents/` or `~/.claude/agents/`, or ship hooks in `hooks/hooks.json` and MCP servers in `.mcp.json`. A plugin agent at `agents/review/security.md` in plugin `my-plugin` becomes `my-plugin:review:security`.

### Agent tool input (SDK type `AgentInput`)

`description` and `prompt` are required. Optional: `subagent_type`, `model` (`sonnet|opus|haiku|fable`), `effort`, `run_in_background`, `name`, `isolation` (`worktree|remote`). The `team_name` and `mode` fields are deprecated and ignored. Source: `https://code.claude.com/docs/en/agent-sdk/typescript`.

### Forks

`/fork [prompt]` copies the conversation into a new background session. `/subtask <task>` spawns a forked subagent whose result returns to this conversation. Forks inherit the full conversation and system prompt. Subagents can use the Agent tool with `name` to become teammates (section 9).

---

## 2. Hooks

**Sources:** `https://code.claude.com/docs/en/hooks` (reference), `https://code.claude.com/docs/en/hooks-guide` (guide, not fetched)

### Events (33 total)

Matcher semantics: a matcher of `"*"`, `""`, or omitted matches everything. A string containing only letters, digits, `_`, `-`, spaces, `,`, and `|` is an exact match (`Edit|Write`). Anything else is an unanchored JavaScript regex (`^Notebook`, `mcp__memory__.*`). `FileChanged` and `StopFailure` accept only `|` as a separator.

| Event | Fires when | Matcher filters on | Can block? |
|---|---|---|---|
| `SessionStart` | Session begins or resumes | Source: `startup`, `resume`, `clear`, `compact`, `fork` | No |
| `Setup` | `--init-only`, or `--init`/`--maintenance` with `-p` | `init`, `maintenance` | No |
| `UserPromptSubmit` | Prompt submitted | None | Yes (ends turn) |
| `UserPromptExpansion` | A command expands into a prompt | Command name | Yes |
| `PreToolUse` | Before a tool call | Tool name (`Bash`, `Edit\|Write`, `mcp__.*`) | Yes (deny/ask/defer) |
| `PermissionRequest` | A permission decision is needed | Tool name | Allow/deny via decision object; exit 2 not honored |
| `PermissionDenied` | Auto mode denies a call | Tool name | No (can return `retry`) |
| `PostToolUse` | After a successful tool call | Tool name | Feedback only |
| `PostToolUseFailure` | After a failed tool call | Tool name | No |
| `PostToolBatch` | After a parallel tool batch, before next model call | None | Yes (stops loop) |
| `Notification` | Claude Code sends a notification | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog` | No |
| `MessageDisplay` | Assistant text is displayed | None | No |
| `SubagentStart` | Subagent spawned | Agent type | No |
| `SubagentStop` | Subagent finishes | Agent type | Yes |
| `TaskCreated` | Task created | None | Yes |
| `TaskCompleted` | Task marked completed | None | Yes |
| `Stop` | Claude finishes responding | None | Yes |
| `StopFailure` | Turn ends on API error | `rate_limit`, `overloaded`, `authentication_failed`, `billing_error`, `server_error`, `unknown` | No |
| `TeammateIdle` | Teammate about to go idle | None | Yes |
| `InstructionsLoaded` | CLAUDE.md or rules loaded | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` | No |
| `ConfigChange` | Config file changes mid-session | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` | Yes, except `policy_settings` |
| `CwdChanged` | Working directory changes | None | No |
| `DirectoryAdded` | Directory added via `/add-dir` or `register_repo_root` | `slash_command`, `register_repo_root` | No |
| `FileChanged` | Watched file changes on disk | Literal filenames (`.envrc\|.env`) | No |
| `WorktreeCreate` | Worktree being created | None | Non-zero exit fails creation |
| `WorktreeRemove` | Worktree removed | None | Non-zero exit fails if directory remains |
| `PreCompact` | Before compaction | `manual`, `auto` | Yes |
| `PostCompact` | After compaction | `manual`, `auto` | No |
| `PreModelSwitch` | Before a requested model switch applies (v2.1.251+) | Canonical model name, e.g. `claude-opus-5` | Yes |
| `PostModelSwitch` | After the model changes | Canonical model name | No |
| `Elicitation` | MCP server requests user input | MCP server name | Yes |
| `ElicitationResult` | After user answers an elicitation | MCP server name | Yes |
| `SessionEnd` | Session ends | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` | No (default timeout 1.5s) |

Hook handler `type` values: `command`, `http`, `mcp_tool`, `prompt`, `agent`. Not every event supports every type. `SessionStart` and `Setup` support only `command` and `mcp_tool`. Prompt and agent hooks are not supported on `PermissionRequest` or the events that support only command, http, and mcp_tool.

### Handler fields

| Type | Fields |
|---|---|
| All | `type` (required), `if` (permission-rule syntax such as `"Bash(git *)"`, tool events only), `timeout` (defaults: 600 for command/http/mcp_tool, 30 for prompt, 60 for agent), `statusMessage`, `once` (skill frontmatter only) |
| `command` | `command` (required), `args` (exec form, no shell), `async`, `asyncRewake`, `shell` (`bash` or `powershell`), `onFailure` (`continue` or `block`, v2.1.295+) |
| `http` | `url` (required), `headers` (supports `$VAR`), `allowedEnvVars`, `onFailure` |
| `mcp_tool` | `server` (required), `tool` (required), `input` (supports `${tool_input.file_path}`-style substitution) |
| `prompt` | `prompt` (required; `$ARGUMENTS` replaced with input JSON, or appended if absent), `model`, `continueOnBlock` |
| `agent` | Same as `prompt`, minus `continueOnBlock`. Experimental; spawns a subagent with up to 50 turns |

`"async": true` (command only) runs in the background. Async hooks cannot block. Their `additionalContext` and `systemMessage` are delivered on the next turn.

### Stdin JSON

Common fields: `session_id`, `transcript_path`, `cwd`, `permission_mode` (`default`, `plan`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`), `hook_event_name`. The overview also lists `prompt_id`, `scratchpad_dir`, and `effort` (object with `level`). Inside subagents, `agent_id` and `agent_type` appear.

Event-specific fields (as documented):

| Event | Fields |
|---|---|
| `SessionStart` | `source`; optional `model`, `agent_type`, `session_title` |
| `UserPromptSubmit` | `prompt`; optional `session_title` |
| `PreToolUse` | `tool_name`, `tool_input`, `tool_use_id`; `mcp_server` (`name`, `source`) for MCP tools |
| `PostToolUse` | `tool_name`, `tool_input`, `tool_response`, `tool_use_id`; optional `duration_ms` |
| `PostToolUseFailure` | `tool_name`, `tool_input`, `tool_use_id`, `error`; optional `is_interrupt`, `duration_ms` |
| `PermissionRequest` | `tool_name`, `tool_input`; optional `permission_suggestions`. No `tool_use_id` |
| `Notification` | `message`, `notification_type`; optional `title` |
| `SubagentStart` | `agent_id`, `agent_type` |
| `SubagentStop` | `stop_hook_active`, `agent_id`, `agent_type`, `agent_transcript_path`, `last_assistant_message`, `background_tasks`, `session_crons` |
| `Stop` | `stop_hook_active`, `last_assistant_message`, `background_tasks`, `session_crons` |
| `TaskCreated` / `TaskCompleted` | `task_id`, `task_subject`; optional `task_description`, `teammate_name`, `team_name` (deprecated), `agent_id` |
| `TeammateIdle` | `teammate_name`, `team_name` (deprecated), `agent_id` |
| `InstructionsLoaded` | `file_path`, `memory_type`, `load_reason`; optional `globs`, `trigger_file_path`, `parent_file_path` |
| `ConfigChange` | `source`; optional `file_path` |
| `Setup` | `trigger` (`init` or `maintenance`) |
| `PreCompact` | `trigger` (`manual`/`auto`), `custom_instructions` (`null` for auto or when no args) |
| `PostCompact` | `trigger`, `compact_summary` |
| `SessionEnd` | `reason` |
| `FileChanged` | `file_path`, `event` (`change`, `add`, `unlink`) |
| `WorktreeCreate` | `name` |
| `WorktreeRemove` | `worktree_path` |
| `PreModelSwitch` / `PostModelSwitch` | `from_model`, `to_model` |

Not captured from the docs I read: exact input for `CwdChanged`, `Elicitation`, `PermissionDenied`, `UserPromptExpansion`, `PostToolBatch`, `StopFailure`, `MessageDisplay`, and `DirectoryAdded`.

Example `PreToolUse` input, verbatim:

```json
{
  "session_id": "abc123",
  "cwd": "/home/user/my-project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test",
    "description": "Run test suite",
    "timeout": 120000,
    "run_in_background": false
  },
  "tool_use_id": "toolu_01ABC123..."
}
```

### Exit codes

- **0:** stdout parsed as JSON if it is a single object; otherwise plain text. Plain-text stdout enters Claude's context only for `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, and `PostModelSwitch`. Stderr is not shown to Claude.
- **2:** blocking error on events that can block. Stderr is the reason. Exit 2 blocks even if stdout says `"allow"`. Not honored on `PermissionRequest`. Ignored `hookSpecificOutput` on `Elicitation` and `ElicitationResult`.
- **Other non-zero:** non-blocking error; the action proceeds. Use `"onFailure": "block"` on `command` or `http` hooks to make failures block.

### Stdout JSON

Universal fields: `continue` (default `true`; `false` stops Claude after the hook), `stopReason` (shown when `continue` is false), `suppressOutput` (no effect), `systemMessage` (user-visible warning), `terminalSequence`.

Top-level: `decision` (only `"block"`) and `reason`.

`hookSpecificOutput` (requires `hookEventName`):

| Event | Output fields |
|---|---|
| `PreToolUse` | `permissionDecision` (`allow`, `deny`, `ask`, `defer`), `permissionDecisionReason`, `updatedInput`, `additionalContext`. Precedence when hooks disagree: deny > defer > ask > allow |
| `PermissionRequest` | `decision.behavior` (`allow`/`deny`), `decision.updatedInput`, `decision.updatedPermissions`, `decision.message`, `decision.interrupt` |
| `PostToolUse` | `updatedToolOutput`, `updatedMCPToolOutput`, `additionalContext`, `classifierContext` |
| `PermissionDenied` | `retry: true` (command hooks only) |
| `UserPromptSubmit` | `additionalContext`, `sessionTitle`, `suppressOriginalPrompt`. Cannot rewrite the prompt |
| `SessionStart` | `additionalContext`, `initialUserMessage`, `sessionTitle`, `watchPaths`, `reloadSkills` |
| `SubagentStart` | `additionalContext` |
| `Stop` / `SubagentStop` | top-level `decision: "block"` + `reason`, or `additionalContext` |
| `PreModelSwitch` | `permissionDecision` (`allow`/`deny`/`ask`), `permissionDecisionReason`; top-level `decision: "block"` cancels |
| `PostModelSwitch` | `additionalContext` |
| `WorktreeCreate` (HTTP) | `worktreePath`. For command hooks, print the path as the last stdout line |
| `Elicitation` / `ElicitationResult` | `action` (`accept`, `decline`, `cancel`), `content` |
| `MessageDisplay` | `displayContent` (display only) |
| `FileChanged` | `watchPaths` |

Decision control by event: top-level `decision`/`reason` for `UserPromptSubmit`, `UserPromptExpansion`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Stop`, `SubagentStop`, `ConfigChange`, `PreCompact`, `TaskCreated`. Exit code or `continue: false` for `TeammateIdle` and `TaskCompleted`. Context only for `SessionStart`, `SubagentStart`, `PostModelSwitch`. No decision control for `Setup`, `Notification`, `SessionEnd`, `PostCompact`, `InstructionsLoaded`, `StopFailure`, `CwdChanged`, `DirectoryAdded`, `FileChanged` (except `watchPaths`).

Example denial, verbatim:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Destructive command blocked by hook"
  }
}
```

Example `SessionStart` context output, verbatim:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Current branch: feat/auth-refactor\nUncommitted changes: src/auth.ts, src/login.tsx",
    "sessionTitle": "auth-refactor"
  }
}
```

### Stop-hook blocking and the loop guard

- `Stop` and `SubagentStop` can block with exit 2, or with top-level `decision: "block"` plus `reason`. `hookSpecificOutput.additionalContext` also continues the conversation.
- `stop_hook_active` is `true` when Claude is already continuing because a stop hook fired. Check it so a hook doesn't block on a condition that can never resolve.
- A cap of 8 consecutive continuations applies. After that Claude Code overrides the next block and ends the turn. The counter resets whenever Claude calls a tool. `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` raises the cap.
- Prompt hooks can return `{"ok": false, "reason": "...", "impossible": true}`. With `impossible: true`, Claude Code lets the turn end.

### Context injection and session control

- `additionalContext` is accepted on: `SessionStart`, `SubagentStart`, `UserPromptSubmit`, `UserPromptExpansion`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Stop`, `SubagentStop`, `PostModelSwitch`. Each string is capped at 10,000 characters and wrapped in a system reminder.
- To inject a file's contents, a hook script can read the file and emit it as `additionalContext`. The docs do not describe a dedicated file-injection field.
- **Triggering `/clear` or `/compact` from a hook is not documented.** I found no output field that does it. The closest levers are `PreCompact` (can block compaction), `PostCompact` (no control), and `SessionStart` with `compact` (re-injection).

### Where hooks are configured

| Location | Scope | Shared? |
|---|---|---|
| `~/.claude/settings.json` | All projects | No |
| `.claude/settings.json` | Project | Yes, committed |
| `.claude/settings.local.json` | Project | No, gitignored |
| Managed policy settings | Organization | Yes (admin) |
| Plugin `hooks/hooks.json` (top-level `"hooks"` key) | When plugin enabled | Yes |
| Skill frontmatter `hooks:` | Rest of session once invoked | Yes |
| Subagent frontmatter `hooks:` | While subagent runs | Yes (not for plugin subagents) |

Settings shape, verbatim from the docs:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
      }]
    }]
  }
}
```

Other settings: `disableAllHooks: true` turns hooks off. `allowManagedHooksOnly` restricts hooks to managed sources. `allowedHttpHookUrls` and `httpHookAllowedEnvVars` govern HTTP hooks.

### Environment variables available to hook commands

- `CLAUDE_PROJECT_DIR`: project root where the session started
- `CLAUDE_PLUGIN_ROOT`: plugin installation directory (current version path)
- `CLAUDE_PLUGIN_DATA`: plugin persistent data directory (survives updates)
- `CLAUDE_ENV_FILE`: available to `SessionStart`. `export` lines written here apply to later Bash commands. `FileChanged` hooks can also use it. Cleared on `CwdChanged`
- `CLAUDE_EFFORT`: current effort level
- `CLAUDE_CODE_REMOTE`: `"true"` in remote web environments
- `CLAUDE_PLUGIN_OPTION_<KEY>`: plugin `userConfig` values
- No `$CLAUDE_MODEL` exists. Use `PostModelSwitch` to track model changes.

### Other hook notes

- `SessionEnd` default timeout is 1.5s. Raise it with a per-hook `timeout` (up to 60s) or `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`.
- `WorktreeRemove` needs a pairing `WorktreeCreate` hook, or Claude Code falls back to `git worktree remove --force`.
- `/hooks` opens the hook menu. `/debug` and `claude --debug` expose hook logs.

---

## 3. Context management

**Sources:** `https://code.claude.com/docs/en/context-window`, `https://code.claude.com/docs/en/commands`, `https://code.claude.com/docs/en/model-config`, `https://code.claude.com/docs/en/memory`

### Commands (exact names and aliases)

| Command | Behavior |
|---|---|
| `/clear [name]` | New conversation with empty context. Optional name labels the old one in `/resume`. Aliases `/reset`, `/new` |
| `/compact [instructions]` | Summarizes conversation to free context. Optional focus text, e.g. `/compact focus on the auth bug fix` |
| `/context [all]` | Colored grid of context usage. Lists loaded memory files under **Memory files**. Reports overflow warnings |
| `/usage` | Session cost, plan limits, and activity. `/cost` and `/stats` are aliases |
| `/rewind` | Rewind conversation and/or code, or **Summarize from here** / **Summarize up to here**. Aliases `/checkpoint`, `/undo`. Governed by `fileCheckpointingEnabled` (default `true`) |
| `/resume [session]` | Resume by ID or name, or open picker. Alias `/continue`. Background sessions appear marked `bg` |
| `/export [filename]` | Export conversation as plain text. With a filename, writes directly |
| `/branch [name]` | Branch the conversation at this point and switch into it |
| `/btw [question]` | Side question without adding to the conversation |
| `/memory` | Edit CLAUDE.md files, toggle auto memory, view auto memory |
| `/init` | Generate a CLAUDE.md. `CLAUDE_CODE_NEW_INIT=1` gives an interactive flow covering skills, hooks, and personal memory |

CLI equivalents: `claude -c` (continue), `claude -r <id|name>` (resume), `claude --fork-session`.

### Auto-compact and window sizes

- Claude Code compacts automatically as the conversation approaches the model's limit. Native-1M models compact at about 967K tokens.
- Configure with `autoCompactWindow` (settings, number from 100000 to 1000000 or `"auto"`), `/autocompact 500k` (saved under `modelSettings`), `claude --autocompact <value>` (one launch), or `CLAUDE_CODE_AUTO_COMPACT_WINDOW=<tokens>` (env, highest precedence). Accepted forms: `200000`, `500k`, `1M`, or `200` (thousands).
- `autoCompactEnabled` (boolean) toggles automatic compaction. The settings example also shows `"DISABLE_AUTO_COMPACT": "1"` in `env`.
- Gateways that enforce lower limits: set `CLAUDE_CODE_AUTO_COMPACT_WINDOW=200000`. For unrecognized model IDs, use `CLAUDE_CODE_MAX_CONTEXT_TOKENS`.

### Context window sizes

| Model | Window |
|---|---|
| Fable 5.1, Fable 5, Sonnet 5 and later, Haiku 5.5, Opus 4.7 and later | 1M by default, no suffix needed |
| Opus 4.6 and Sonnet 4.6 | 200K unless you use `[1m]` (`claude-opus-4-6[1m]`, `claude-sonnet-4-6[1m]`) |
| Other older models | 200K |

`CLAUDE_CODE_DISABLE_1M_CONTEXT=1` removes `[1m]` variants and treats native-1M models as 200K. Haiku 5.5 is 1M on the Anthropic API, with higher per-token cost above 100K.

### What survives compaction

| Mechanism | After compaction |
|---|---|
| System prompt and output style | Both still apply |
| Project-root CLAUDE.md and unscoped rules | Re-injected from disk |
| Auto memory | Re-injected from disk |
| Plan written in plan mode | Re-injected from disk |
| Rules with `paths:` frontmatter | Reloaded on demand |
| Nested CLAUDE.md in subdirectories | Reloaded on demand |
| Files Claude read or edited | Up to five re-read, most recent first. Files over 5,000 tokens come back as a path reference |
| Invoked skill bodies | Re-injected, capped at 5,000 tokens per skill and 25,000 total; oldest dropped first |
| Background commands and subagents | Keep running; Claude is told which are still running |
| Context hooks added earlier | Summarized with the rest |
| SessionStart hooks matching `compact` | Run; output added to the compacted context |

Path-scoped rules and nested CLAUDE.md load into history when triggered, so compaction summarizes them away. To persist a rule across compaction, remove its `paths:` frontmatter or move it to the project-root CLAUDE.md.

### Controlling compaction

- `/compact <focus>` steers the summary.
- `PreCompact` (matcher `manual` or `auto`) can block compaction with exit 2 or `decision: "block"`. Blocking automatic compaction proactively skips it. Blocking it in response to a context-limit error surfaces the error.
- `PostCompact` receives `compact_summary` and cannot affect the result.
- `SessionStart` with matcher `compact` re-injects context via `additionalContext`.
- **I found no settings key for custom compaction instructions.** The docs cover `/compact <focus>` and the hooks above. Whether CLAUDE.md content steers the summary is not documented.

### Auto memory

- **Location:** `~/.claude/projects/<project>/memory/`. `<project>` is derived from the git repository, so worktrees and subdirectories share one directory. Set `CLAUDE_CODE_PROJECT_DIR_NAME` (with `CLAUDE_CONFIG_DIR`) to override the name (v2.1.234+).
- **Override:** `autoMemoryDirectory` (absolute or `~/` path) in any settings scope. From project or local files it is honored only under the hooks trust rule.
- **Toggle:** `autoMemoryEnabled` (default `true`). `/memory` toggles it and saves to `~/.claude/settings.json`. `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` overrides for one session.
- **Structure:** `MEMORY.md` is the index, one line per memory. Topic files (`user_role.md`, `feedback_testing.md`, and so on) are read on demand. Each memory file has a `type` in frontmatter: `user`, `feedback`, `project`, or `reference`. A `modified` timestamp is added on write (v2.1.214+).
- **Loading:** the first 200 lines or 25KB of `MEMORY.md` load at session start. Over-limit writes succeed but return an error asking Claude to rewrite the index.
- **Subagents:** the main auto memory is not loaded into subagents. Forks inherit it. Subagents with `memory:` have their own directory.
- **Retention:** memory files are excluded from the `cleanupPeriodDays` sweep.
- **The `#` shortcut:** I did not find a `#`-prefix shortcut in the memory docs. Saving is done by asking Claude, or editing via `/memory`.

---

## 4. CLAUDE.md and rules

**Sources:** `https://code.claude.com/docs/en/memory`, `https://code.claude.com/docs/en/claude-directory`

### Locations and load order

| Scope | Location |
|---|---|
| Managed policy | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux/WSL: `/etc/claude-code/CLAUDE.md`; Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` |
| User | `~/.claude/CLAUDE.md` |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` (committed) |
| Local | `./CLAUDE.local.md` (gitignore it) |

- **Launch-time loading:** CLAUDE.md and CLAUDE.local.md from the working directory and every ancestor directory. Content is concatenated, not overridden, ordered from the filesystem root down. Within a directory, `CLAUDE.local.md` follows `CLAUDE.md`.
- **Lazy loading:** CLAUDE.md files in subdirectories load when Claude reads, writes, or edits a file in that subdirectory.
- **Additional directories:** `--add-dir` directories do not load CLAUDE.md unless `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` is set.
- **Exclusion:** `claudeMdExcludes` (array of absolute-path globs) in any settings layer. Arrays merge across layers.
- **Size:** target under 200 lines per file. The hard load limit is 4 MiB per CLAUDE.md. Block-level HTML comments are stripped before injection.

### Imports

- Syntax: `@path/to/import` anywhere in CLAUDE.md. Relative paths resolve from the importing file, not the working directory. Absolute paths are allowed.
- Maximum depth: four hops.
- Paths with spaces use backslashes: `@Design\ Docs/api-conventions.md`.
- Imports inside Markdown code spans or fenced code blocks are ignored. Wrap a path in backticks to mention it literally.
- External imports (resolving outside the working directory) trigger an approval dialog on first encounter in a project. User-scope files load without it.
- Imports do not reduce context cost, since imported files load at launch.

### AGENTS.md

Claude Code reads `AGENTS.md` and `.claude/AGENTS.md` in place of CLAUDE.md when no CLAUDE.md exists. It reads them from the working directory and its ancestors at launch, and from subdirectories lazily. It does not read `AGENTS.local.md`, `AGENTS.override.md`, or anything under `.agents/`.

### Rules (`.claude/rules/`)

- Location: `.claude/rules/**/*.md` (recursive). User-level rules: `~/.claude/rules/`. User rules load before project rules.
- Rules without `paths:` load at launch, with the same priority as `.claude/CLAUDE.md`.
- Path-scoped rules load when Claude reads, writes, or edits a matching file (including `cat`/`head` of one file via Bash).
- Frontmatter: `paths` is the only field Claude Code reads. It accepts a YAML list or comma-separated string. Unparseable YAML is ignored and the rule loads unconditionally.

Verbatim example:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
- Include OpenAPI documentation comments
```

- Glob support: `**/*.ts`, `src/**/*`, `*.md`, and brace expansion (`src/**/*.{ts,tsx}`). The budget is 1,000 expanded patterns and 4 MiB per rule.
- Symlinks are supported. A symlink whose target is outside the working directory counts as an external import and needs approval. Circular symlinks are handled.
- `claudeMdExcludes` can exclude rules, including symlinked ones, by either path.
- Project rules are skipped if `project` is excluded from `--setting-sources`.

---

## 5. Skills

**Sources:** `https://code.claude.com/docs/en/skills`, `https://code.claude.com/docs/en/claude-directory`

### Locations and precedence

| Scope | Path |
|---|---|
| Enterprise (managed) | `.claude/skills/<name>/SKILL.md` in the managed settings directory (Linux example: `/etc/claude-code/.claude/skills/`) |
| Personal | `~/.claude/skills/<name>/SKILL.md` |
| Project | `.claude/skills/<name>/SKILL.md` |
| Nested | `<subdir>/.claude/skills/<name>/SKILL.md` (loads when Claude touches that subdirectory) |
| Additional directory | `.claude/skills/` inside a `--add-dir` directory (session only) |
| Plugin | `<plugin>/skills/<name>/SKILL.md`, invoked as `/plugin-name:skill-name` |

Precedence on name collisions: enterprise over personal, personal over project. A skill beats a `.claude/commands/` file with the same name. A custom skill replaces a bundled skill of the same name, but not its aliases. Plugin skills are namespaced and don't collide. Live edits to `SKILL.md` are picked up without restart. A newly created top-level skills directory needs `/reload-skills`.

Reserved names: `synced`, and `anthropic-skills` or anything prefixed `anthropic-skills:`.

### Frontmatter fields

Names are lowercase with hyphens, except `when_to_use`. Unknown fields are ignored. The frontmatter must start on line 1.

| Field | Default / values | Purpose |
|---|---|---|
| `name` | directory name | Command name |
| `description` | first non-empty body line if omitted | What it does and when to use it |
| `when_to_use` | none | Extra trigger context; appended to description in listing |
| `argument-hint` | none | Autocomplete hint, e.g. `[issue-number]` |
| `arguments` | none | Named positional args for `$name`; space-separated string or YAML list |
| `disable-model-invocation` | `false` | `true` blocks auto-invocation, subagent preloading, and scheduled-task runs |
| `user-invocable` | `true` | `false` hides it from the `/` menu; Claude can still invoke it |
| `allowed-tools` | none | Tools allowed without prompting during the invoking turn |
| `disallowed-tools` | none | Tools removed from the pool while the skill is active |
| `model` | session model | Model for the current turn; `inherit` keeps the active model |
| `effort` | session level | `low`, `medium`, `high`, `xhigh`, `max` |
| `context` | none | `fork` runs the skill as a subagent |
| `agent` | `general-purpose` | Subagent type for `context: fork`: `Explore`, `Plan`, `general-purpose`, or a custom agent |
| `background` | `true` | With `context: fork`; `false` waits for the result in the invoking turn (v2.1.218+) |
| `hooks` | none | Hooks registered on invocation and kept for the session |
| `paths` | none | Glob patterns limiting automatic activation; not allowed in command files |
| `shell` | `bash` | `bash` or `powershell` for injected commands |
| `metadata` | none | Free-form map; ignored by Claude Code |
| `license`, `compatibility` | none | Agent Skills spec fields; accepted, not acted on |

Portability: fields outside the Agent Skills spec (`argument-hint`, `context`, `hooks`, and others) cause a hard error when packaging for claude.ai or the Skills API. Only `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools` are portable.

### String substitutions

| Placeholder | Expands to |
|---|---|
| `$ARGUMENTS` | All arguments. If no placeholder receives them, `ARGUMENTS: <value>` is appended |
| `$ARGUMENTS[N]` | Argument at 0-based index N |
| `$N` | Shorthand for `$ARGUMENTS[N]` |
| `$name` | Named argument from `arguments`, by position |
| `${CLAUDE_SESSION_ID}` | Session ID |
| `${CLAUDE_EFFORT}` | Effort level |
| `${CLAUDE_SKILL_DIR}` | Directory containing this SKILL.md |
| `${CLAUDE_PROJECT_DIR}` | Project root |
| `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` | Plugin skills only |

Quote multi-word arguments. Escape a literal dollar sign with `\$1.00`. Substituted values are not re-expanded.

### Dynamic context injection

- Inline: `` !`<command>` `` (the `!` must start a line or follow whitespace).
- Multi-line: a fenced block opened with ` ```! `.
- Output replaces the placeholder before Claude sees the skill. Failures abort the whole invocation. Default timeout is 2 minutes.
- `"disableSkillShellExecution": true` in settings replaces these with `[shell command execution disabled by policy]`. It does not apply to bundled or managed skills.

### `context: fork`

- The skill body becomes the subagent's task prompt. The subagent does not see your conversation history, so the instructions must be self-contained.
- Background by default (v2.1.218+). Set `background: false` to wait in the invoking turn.
- Results return as the subagent's summary. Edits made by a backgrounded fork are outside checkpoints, so `/rewind` won't undo them.
- Use it only for skills with explicit tasks. Reference-only guidance produces no useful output in a fork.

Example, verbatim from the docs:

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

### Relationship to `.claude/commands/*.md`

Commands are the older format and still work. A skill and a command with the same name both create `/name`, and the skill wins. Command files accept the same frontmatter except `name` and `paths`. Subdirectories are namespaced with colons: `.claude/commands/frontend/component.md` becomes `/frontend:component`. Prefer skills for new work.

### Invocation, budget, and supporting files

- Claude auto-loads a skill when its description matches, unless `disable-model-invocation: true`.
- Users invoke with `/skill-name` at the start of a message. Up to six skills can be chained, e.g. `/write-tests /fix-issue 123`.
- Listing budget: `description` and `when_to_use` combined are truncated at 1,536 characters. Settings `skillListingBudgetFraction` (default `0.01`) and `skillListingMaxDescChars` (default `1536`) tune it. `/skill-doctor` reports per-skill context cost and usage (v2.1.252+). `/skills` lists them.
- Progressive disclosure: keep `SKILL.md` under 500 lines and reference sibling files (`reference.md`, `examples.md`, `scripts/helper.py`). Use `${CLAUDE_SKILL_DIR}` in scripts.

### Disabling skills

```text
Skill                 # deny rule: disable all skills
Skill(commit)         # allow only a specific skill
Skill(deploy *)       # deny with args matching
```

`skillOverrides` in settings maps names to `"on"`, `"name-only"`, `"user-invocable-only"`, or `"off"`. Plugin skills are not affected by it.

Example `SKILL.md`, verbatim:

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
---

Deploy $ARGUMENTS to production:

1. Run the test suite
2. Build the application
3. Push to the deployment target
4. Verify the deployment succeeded
```

---

## 6. Plugins and marketplaces

**Sources:** `https://code.claude.com/docs/en/plugins/create`, `.../plugins/manifest-reference`, `.../plugins/marketplace-reference`, `.../plugins/install`, `.../plugins/loading`, `.../plugins/publish`

### Plugin directory layout

```text
deploy-tools/
├── .claude-plugin/
│   └── plugin.json          # the only file that goes in .claude-plugin/
├── skills/<name>/SKILL.md
├── commands/*.md            # legacy; prefer skills/
├── agents/*.md
├── hooks/hooks.json         # top-level "hooks" key wrapping the event map
├── monitors/monitors.json
├── output-styles/
├── themes/
├── workflows/*.js
├── bin/                     # added to Bash PATH while plugin is enabled
├── settings.json            # only "agent" and "subagentStatusLine" take effect
├── .mcp.json
└── .lsp.json
```

A `CLAUDE.md` at the plugin root is not loaded. Put instructions in a skill. `claude plugin validate` warns about it.

### `plugin.json`

Path: `.claude-plugin/plugin.json`. Optional. Without it, Claude Code loads components from the standard layout, and the name comes from the marketplace entry or directory name.

Verbatim minimal example from the create guide:

```json
{
  "name": "my-first-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

Key fields (full table at the manifest reference):

| Field | Type / notes |
|---|---|
| `name` | Required. Kebab-case, no spaces, `@`, or `:`. Every component is namespaced under it. Anthropic-reserved prefixes are rejected |
| `displayName` | UI label only |
| `version` | Pins the plugin until changed. Omit it to track commit SHAs (see Versions) |
| `description`, `author` (`name` required), `homepage` (must parse as URL), `repository`, `license` (SPDX), `keywords` | Metadata |
| `defaultEnabled` | Default `true` |
| `dependencies` | Array of `"name"`, `"name@marketplace"`, or `{name, marketplace, version}` |
| `skills` | Path or array. Adds to the default `skills/` scan. `"."` or `"./"` for the root |
| `commands` | Replaces default scan. Path, array, or object map with `source` or `content` per entry |
| `agents` | Replaces default scan. `.md` files only |
| `hooks` | Path, inline object, or array. Merges with `hooks/hooks.json` |
| `mcpServers` | Path, inline map, `.mcpb`/`.dxt` bundle, or array. Merges with `.mcp.json` |
| `lspServers` | Merges with `.lsp.json` |
| `outputStyles`, `workflows` | Replace default scans |
| `settings` | Only `agent` and `subagentStatusLine` take effect |
| `userConfig` | Prompted values: `type` (`string`, `number`, `boolean`, `directory`, `file`), `title`, `description`, `required`, `default`, `options`, `multiple`, `sensitive`, `min`, `max` |
| `channels` | Message channels bound to an MCP server |
| `experimental` | `themes`, `monitors`, `evals` (eval directory) |

Path rules: every component path starts with `./`. Paths must stay inside the plugin root and exist. `claude plugin validate` checks them.

Key replacement behavior: `commands`, `agents`, `outputStyles`, `workflows`, `experimental.themes`, `experimental.monitors` replace the default folder. `skills` adds to it. `hooks`, `mcpServers`, `lspServers` merge.

`${CLAUDE_PLUGIN_ROOT}` changes with each version, so store durable state in `${CLAUDE_PLUGIN_DATA}` (`~/.claude/plugins/data/<id>/`), which persists across updates. `${CLAUDE_PROJECT_DIR}` is also available.

Hook file example, verbatim (`hooks/hooks.json`):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/format.sh" }
        ]
      }
    ]
  }
}
```

Validation: `claude plugin validate <path>`, with `--strict` to fail on warnings. Use it in CI.

### `marketplace.json`

Path: `.claude-plugin/marketplace.json` at the marketplace root. The root is the directory that contains `.claude-plugin/`, and relative plugin sources resolve from it.

| Field | Notes |
|---|---|
| `name` | Required. Letters, digits, `.`, `_`, `-`. Reserved names apply (official names, `inline`, `builtin`, `skills-dir`, `synced`, `claudeai-*`, and others) |
| `owner` | Required; `name` required, `email` and `url` optional |
| `plugins` | Required array of entries |
| `description`, `version` | Optional; also under `metadata` |
| `metadata.pluginRoot` | Directory that bare source names resolve under (v2.1.239+) |
| `forceRemoveDeletedPlugins` | Uninstalls plugins removed from the catalog |
| `allowCrossMarketplaceDependenciesOn` | Marketplaces whose plugins can be dependencies |
| `renames` | Map of former name to current name, or `null` for removed |

Plugin entry fields: `name` (required), `source` (required), `description`, `version`, `category`, `tags`, `strict` (default `true`), `relevance`, `dependencies`, `defaultEnabled`, `displayName`, `metadata`, `headers`, `headersHelper`.

Minimal example from the publish guide, verbatim:

```json
{
  "name": "your-marketplace",
  "owner": { "name": "Your Name" },
  "plugins": [
    { "name": "deploy-helper", "source": "./" }
  ]
}
```

#### Plugin sources (`plugins[].source`)

| Type | Shape |
|---|---|
| Relative path | `"./plugins/formatter"` (must start with `./`; no `..`) |
| `github` | `{"source":"github","repo":"owner/repo","ref":"v2.0.0","sha":"<40-char>"}` |
| `url` | `{"source":"url","url":"https://...git","ref":"main"}` |
| `git-subdir` | `{"source":"git-subdir","url":"...","path":"tools/formatter"}` (sparse checkout) |
| `npm` | `{"source":"npm","package":"@org/pkg","version":"^2.0.0","registry":"https://..."}` (install scripts never run) |
| `archive` | `{"source":"archive","url":"https://...zip","sha256":"<64 hex>"}` (v2.1.224+) |
| `command` | `{"source":"command","command":"my-tool claude-plugin-path","timeout":120,"mode":"copy"\|"link"}` (v2.1.229+) |

`ref` and `sha`: `sha` is preferred when both are set.

#### Marketplace sources (for `extraKnownMarketplaces`, `strictKnownMarketplaces`, `blockedMarketplaces`)

| Type | Fields |
|---|---|
| `github` | `repo`, `ref`, `path`, `sparsePaths` (`owner/*` allowed only in policy lists, v2.1.223+) |
| `git` | `url`, `ref`, `path`, `sparsePaths` |
| `url` | `url`, `headers`, `headersHelper` (a direct link to a marketplace.json) |
| `file` | `path` to a marketplace.json |
| `directory` | `path` to a marketplace root |
| `settings` | `name`, `plugins` (inline catalog, no hosted file) |
| `npm` | Not produced by the CLI; not supported in `extraKnownMarketplaces` |
| `hostPattern`, `pathPattern`, `skills-dir` | Valid only in policy lists |

### Install and manage (commands)

Inside a session:
```text
/plugin marketplace add owner/repo
/plugin marketplace add ./my-marketplace
/plugin install commit-commands@claude-plugins-official
/plugin install deploy-helper --marketplace your-org/plugins     # add and install (v2.1.275+)
/plugin                          # opens the manager (Discover, Installed, Marketplaces, Errors)
/plugin enable|disable|uninstall <name>
/plugin marketplace list|update <name>|remove <name>
/reload-plugins [--force]
```

From the shell:
```bash
claude plugin marketplace add your-org/plugins
claude plugin install formatter@your-org --scope project
claude plugin install deploy-helper --marketplace your-org/plugins   # v2.1.292+
claude plugin update <plugin>@<marketplace>
claude plugin enable|disable <plugin>@<marketplace>
claude plugin uninstall <plugin>@<marketplace> --scope project
claude plugin list
claude plugin details <name>
claude plugin validate ./my-plugin [--strict]
claude plugin init <name>                        # scaffolds under ~/.claude/skills/
claude plugin tag [--push]                       # creates {name}--v{version} tag
claude plugin prune                              # removes auto-installed dependencies
```

Scopes: `user` (in `~/.claude/settings.json` `enabledPlugins`), `project` (`.claude/settings.json`, committed), `local` (`.claude/settings.local.json`).

Session-only loading: `claude --plugin-dir ./my-plugin` (repeatable; accepts `.zip`), `claude --plugin-url <zip-url>`, and env `CLAUDE_CODE_PLUGIN_DIRS` (absolute paths, v2.1.280+). These are `@inline` plugins.

### Repository-level portability: what auto-installs and what does not

This is the key point for a portable design. The docs describe the following behavior.

1. **Marketplace registration:** a repo's `.claude/settings.json` can declare `extraKnownMarketplaces`. These are honored only after the folder's workspace trust dialog is accepted. Cloud sessions never add them.

   ```json
   {
     "extraKnownMarketplaces": {
       "acme-tools": {
         "source": { "source": "github", "repo": "acme-corp/claude-plugins" },
         "autoUpdate": true
       }
     }
   }
   ```

2. **Enablement:** `enabledPlugins` maps `"plugin@marketplace": true|false`. Example from the docs: `"code-formatter@team-tools": true`.

3. **Fetching is restricted.** A plugin enabled only by `.claude/settings.json` (project scope) with an external source (github, git, url, npm, and so on) is not fetched on a collaborator's machine. The `/plugin` Errors tab shows `Plugin "<name>" is enabled in project settings but isn't installed here`. Each collaborator must run `claude plugin install <name>@<marketplace> --scope project` once. Fetching happens only when user, local (untracked), `--settings`, or managed settings also set it to `true`.

4. **Exception: relative-path plugins** inside the same marketplace repository load directly from the marketplace and need no install record. This is the most reliable repo-local pattern.

5. **Settings-sourced marketplaces** (`"source": {"source":"settings","name":...,"plugins":[...]}`) inline the catalog in settings. The plugin name must match the marketplace key, and each plugin still needs `enabledPlugins` and the install step if it is external.

6. The docs also mention seed directories for CI, which I did not verify in detail.

### Plugin loading, precedence, and conflicts

- Plugin ID format: `<name>@<origin>`. Origins: a marketplace name, `inline` (`--plugin-dir`), `skills-dir` (directory under `~/.claude/skills/` or project `.claude/skills/`), or `synced` (claude.ai).
- Settings sources for `enabledPlugins`, highest to lowest: managed, `--settings` flag, project local, project shared, user. A higher source that mentions an ID overrides lower ones.
- Name conflicts, highest to lowest: managed-locked ID; enabled `--plugin-dir`/`--plugin-url`/`CLAUDE_CODE_PLUGIN_DIRS`; installed marketplace plugin; skills-directory plugin; claude.ai-synced plugin.

### Cache and disk layout (under `~/.claude/plugins/`, override with `CLAUDE_CODE_PLUGIN_CACHE_DIR`)

| Path | Contents |
|---|---|
| `cache/<marketplace>/<plugin>/<version>/` | Installed copies. `${CLAUDE_PLUGIN_ROOT}` points here |
| `data/<plugin-id>/` | `${CLAUDE_PLUGIN_DATA}`. Deleted on uninstall from last scope unless kept |
| `marketplaces/<name>/` | Clone of a git/GitHub/URL marketplace |
| `installed_plugins.json` | Install records: `scope`, `installPath`, `version` |
| `known_marketplaces.json` | Fetched marketplaces: `source`, `installLocation`, `lastUpdated`, `autoUpdate` |
| `synced/`, `.trash/` | claude.ai sync |

Loaded in place (not copied): `--plugin-dir` and skills-directory plugins, and relative-path plugins from a marketplace added by local path. Everything else is copied into the cache.

### Versions and updates

- Version resolution: manifest `version` first, then the marketplace entry `version`. If neither is set: `github`, `url`, and `git-subdir` use the commit SHA (12 chars). `archive` uses SHA-256. Relative path in a git-hosted marketplace uses the commit SHA. Local directory that is not git, and `npm`, use `unknown`. `command` sources always derive the version from output.
- Pinning `"version": "1.0.0"` keeps users on the cached copy until you change it, even after new commits. Omitting it tracks commits.
- Auto-update defaults: on for official marketplaces (`claude-plugins-official` and others, except `knowledge-work-plugins` and `first-party-plugins`) and for claude.ai-added marketplaces. Off for all others. Override per marketplace with `autoUpdate` in settings, or with `/plugin` → Marketplaces. Turn off globally with `DISABLE_AUTOUPDATER=1` or `DISABLE_UPDATES=1`, or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` (`FORCE_AUTOUPDATE_PLUGINS=1` re-enables plugin updates).
- Auto-update runs after the first message, with a random delay of up to ten minutes. Running sessions keep the old version until `/reload-plugins`.
- Orphaned version directories are removed in a background sweep 14 days after an update or uninstall.

### Dependencies

- Plugin-to-plugin: `dependencies` in `plugin.json` or the marketplace entry. Installing a plugin installs and enables its dependencies. `claude plugin prune` removes auto-installed ones.
- Node.js: if a plugin contains `package.json` and a supported lockfile (`bun.lock`, or `npm-shrinkwrap.json`/`package-lock.json`), Claude Code installs dependencies into the cache copy with lifecycle scripts disabled and a 60-second timeout. Registry packages only.

### Publishing

- Own marketplace: a git repository with `.claude-plugin/marketplace.json`. Users run `claude plugin marketplace add your-org/your-marketplace`, then `claude plugin install deploy-helper@your-marketplace`.
- Anthropic's directory: submitted through `https://claude.ai/directory/manage` on a paid plan. Plugins reach Claude Code users as `<name>@synced`.
- Never rename a published plugin. Use the marketplace `renames` map if you must.

### Plugin evals (flag)

The manifest reference links to `https://code.claude.com/docs/en/plugin-evals`, which I did not fetch. The embedded reference in this session says `claude plugin eval` is generally available, that suites live in `evals/` by default, and that `experimental.evals` in `plugin.json` sets the directory. Verify the details before relying on them.

---

## 7. Settings

**Sources:** `https://code.claude.com/docs/en/settings`, `https://code.claude.com/docs/en/settings-reference`

### Precedence (highest first)

1. Managed settings (`managed-settings.json`, MDM, or the claude.ai console). Organization-enforced.
2. Command line (`claude --settings <file-or-json>`), this session only.
3. Project local: `.claude/settings.local.json` (gitignored).
4. Shared project: `.claude/settings.json` (committed).
5. User: `~/.claude/settings.json`.

Array settings such as `permissions.allow` combine across scopes. Scalar settings such as `model` use the most specific value. The managed file path on Linux is not stated in the pages I fetched. `/etc/claude-code/` is inferred from the CLAUDE.md and skills paths.

### Keys that matter for this design

| Key | Type / values | Notes |
|---|---|---|
| `model` | alias or full ID | `--model` and `ANTHROPIC_MODEL` override it |
| `effortLevel` | `low`, `medium`, `high`, `xhigh` | Not `max`, not `ultracode` |
| `availableModels` | array of aliases, families, or IDs | Enforced via managed settings. `enforceAvailableModels`, `deniedModels` (v2.1.283+) |
| `fallbackModel` | array (max three models) | Tried in order for overload and unavailability |
| `modelSettings` | object keyed by model name, with `effortLevel`, `maxEffortLevel`, `autoCompactWindow` | Written by `/effort` |
| `alwaysThinkingEnabled` | boolean | `false` disables extended thinking |
| `autoCompactEnabled`, `autoCompactWindow` | boolean; number or `"auto"` | See section 3 |
| `cleanupPeriodDays` | integer ≥ 1; default `30` | Transcript retention; `0` fails validation |
| `includeCoAuthoredBy` | boolean, default `true` | Deprecated. Use `attribution` |
| `attribution` | `{commit, pr, sessionUrl}` or `false` | Empty string hides a line. `false` requires v2.1.281+ |
| `permissions` | `allow`, `ask`, `deny`, `defaultMode`, `additionalDirectories`, `disableBypassPermissionsMode`, `disableAutoMode`, `blockReadsOutsideWorkingDirectories` | See below |
| `hooks` | object | Keyed by event; array of `{matcher, hooks}` groups |
| `disableAllHooks` | boolean | Also disables statusLine and file suggestion command |
| `allowManagedHooksOnly` | boolean (managed) | Only managed, SDK, and force-enabled plugin hooks run |
| `env` | object of string values | Applied to each session and subprocess. `""` cancels a shell export |
| `statusLine` | `{type:"command", command, padding?, refreshInterval?, hideVimModeIndicator?}` | Example below |
| `subagentStatusLine` | `{type:"command", command}` | Receives JSON with a `tasks` array |
| `outputStyle` | string | Built-in or custom style name |
| `agent` | string | Starts each session as that named subagent |
| `enabledPlugins` | `{"name@marketplace": true\|false}` | See section 6 |
| `extraKnownMarketplaces` | `{name: {source, autoUpdate?}}` | Alias `additionalMarketplaces` (v2.1.232+) |
| `strictKnownMarketplaces` / `blockedMarketplaces` | arrays of source objects (managed) | Allowlist and blocklist |
| `pluginConfigs` | `{"plugin@mp": {options}}` | User or managed scope |
| `skillOverrides` | `{name: "on"\|"name-only"\|"user-invocable-only"\|"off"}` | Not applied to plugin skills |
| `disableSkillShellExecution` | boolean | See section 5 |
| `disableBundledSkills` | boolean | |
| `autoMemoryEnabled`, `autoMemoryDirectory` | boolean (default `true`); path | See section 3 |
| `claudeMdExcludes` | array of globs | See section 4 |
| `plansDirectory` | string, relative to project root | Default `~/.claude/plans` |
| `fileCheckpointingEnabled` | boolean (default `true`) | Enables `/rewind` |
| `teammateMode` | `in-process` (default), `auto`, `tmux`, `iterm2` | See section 9 |
| `worktree` | `{baseRef: "fresh"\|"head", symlinkDirectories, sparsePaths, bgIsolation: "worktree"\|"none", location}` | |
| `sandbox` | `{enabled, filesystem: {allowWrite, denyWrite, denyRead, allowRead}, network: {allowedDomains, deniedDomains, ...}, excludedCommands, autoAllowBashIfSandboxed, ...}` | `enabled` defaults `false`. macOS, Linux, WSL2 |
| `spinnerVerbs` | `{mode: "append"\|"replace", verbs: [...]}` | |
| `spinnerTipsEnabled` | boolean (default `true`) | |
| `theme`, `editorMode`, `tui`, `viewMode`, `verbose` | various | UI |
| `autoUpdatesChannel` | `"latest"` (default) or `"stable"` | |
| `minimumVersion` | version string | Blocks downgrades |
| `apiKeyHelper`, `otelHeadersHelper`, `awsAuthRefresh` | command strings | Dynamic credentials |
| `forceLoginMethod` | `claudeai`, `console`, `gateway` | |
| `defaultShell` | `bash` or `powershell` | |
| `agentPushNotifEnabled`, `inputNeededNotifEnabled`, `preferredNotifChannel` | notification controls | |
| `disableRemoteControl`, `disableAgentView`, `crossSessionInbound` | controls | |
| `disableWorkflows`, `workflowSizeGuideline`, `ultracode` | workflow controls | `workflowSizeGuideline`: `unrestricted`, `small`, `medium` (default), `large` |
| `subagentPromptCacheTtl` | `5m` (default) or `1h` | Cache TTL for subagent and workflow requests |
| `skillListingBudgetFraction`, `skillListingMaxDescChars` | number; integer (default `1536`) | |
| `enableArtifact` | boolean | `false` turns off the Artifact tool |

Not verified: `companionMode`, which I did not find in the pages I read.

### `permissions`

```json
{
  "permissions": {
    "allow": ["Bash(npm run *)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(./.env)"],
    "defaultMode": "acceptEdits"
  }
}
```

- Evaluation: `deny` first, then `ask`, then `allow`. First match decides.
- Rule forms: `Tool` or `Tool(specifier)`. Examples: `Bash`, `Bash(npm run *)`, `Read(./.env)`, `Edit(/src/**)`, `WebFetch(domain:example.com)`, `WebSearch`, `Skill(deploy *)`, `Agent(Explore)`, `mcp__*`.
- `defaultMode` values: `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`, `manual` (alias of `default`). `auto` and `bypassPermissions` take effect only from user settings or managed settings, not from project or local files.
- `additionalDirectories`: extra paths for file access.
- `disableBypassPermissionsMode: "disable"` blocks bypass mode.
- Project `allow` rules apply only after the workspace trust dialog is accepted.

### `env`, `statusLine`, and attribution

```json
{
  "env": {
    "DISABLE_AUTO_COMPACT": "1",
    "ANTHROPIC_BASE_URL": "https://proxy.example.com"
  }
}
```

```json
{
  "statusLine": {
    "type": "command",
    "command": "jq -r '\"[\\(.model.display_name)] \\(.context_window.used_percentage // 0)% context\"'",
    "padding": 2
  }
}
```

```json
{
  "attribution": {
    "commit": "Generated with AI\n\nCo-Authored-By: AI <ai@example.com>",
    "pr": "",
    "sessionUrl": false
  }
}
```

### Environment variables you can set under `env` (documented in this session)

- Agent and subagent: `CLAUDE_CODE_SUBAGENT_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`, `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS`, `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS`
- Teams and workflows: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, `CLAUDE_CODE_DISABLE_WORKFLOWS`, `CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`, `CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`
- Tasks: `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` (opt in to Task tools), `CLAUDE_CODE_ENABLE_TASKS=0` (re-enable TodoWrite)
- Memory: `CLAUDE_CODE_DISABLE_AUTO_MEMORY`, `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD`
- Models and effort: `ANTHROPIC_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_FABLE_MODEL`, `ANTHROPIC_DEFAULT_MODEL` (v2.1.236+), `CLAUDE_CODE_EFFORT_LEVEL`, `CLAUDE_CODE_DISABLE_1M_CONTEXT`, `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `CLAUDE_CODE_MAX_CONTEXT_TOKENS`, `MAX_THINKING_TOKENS`
- Plugins: `CLAUDE_CODE_PLUGIN_DIRS`, `CLAUDE_CODE_PLUGIN_CACHE_DIR`, `CLAUDE_CODE_PLUGIN_PREFER_HTTPS`, `DISABLE_AUTOUPDATER`, `DISABLE_UPDATES`, `FORCE_AUTOUPDATE_PLUGINS`
- Hooks: `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`, `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`
- Misc: `CLAUDE_ENV_FILE`, `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR`, `CLAUDE_CODE_SIMPLE` (bare mode), `CLAUDE_CODE_SAFE_MODE`

Full list: `https://code.claude.com/docs/en/env-vars` (not fetched).

### Model selection and effort

**Aliases** (per model-config): `default` (account default; Opus 5.5 on most plans and the API), `best` (Fable where available, else Opus), `fable` (Fable 5.1), `sonnet` (Sonnet 5.5 on the API), `opus` (Opus 5.5 on the API), `haiku` (Haiku 5.5 on the API), `sonnet[1m]`, `opus[1m]`, `opusplan` (Opus in plan mode, Sonnet otherwise). Full IDs are accepted anywhere an alias is, including `claude-opus-5-5`, `claude-sonnet-5`, `claude-haiku-5-5`, `claude-fable-5-1`, `claude-opus-4-6`, and `claude-sonnet-4-6`.

**Setting the model** (in priority order): `/model <name>` or `/model` picker (`Enter` saves as default, `s` for session only); `claude --model`; `ANTHROPIC_MODEL`; the `model` setting; `ANTHROPIC_DEFAULT_MODEL`.

**Effort levels:** Opus 5.5, Sonnet 5.5, Haiku 5.5, Opus 5, Sonnet 5, Opus 4.8, Opus 4.7, and Fable support `low`, `medium`, `high`, `xhigh`, `max`. Opus 4.6 and Sonnet 4.6 support `low`, `medium`, `high`, `max`. Defaults: `high` on most models, `medium` on Opus 5.5, Sonnet 5.5, Haiku 5.5, and `xhigh` on Opus 4.7. Resolution: session override (`--effort`, `/effort`, `CLAUDE_CODE_EFFORT_LEVEL`) first, then `modelSettings` or `effortLevel`, then model default. Skill and subagent `effort:` override the session level while active.

**Ultracode:** a setting, not an effort level. `/effort ultracode`, `claude --effort ultracode` (starts at `xhigh`), or `"ultracode": true` in settings.

---

## 8. Headless and automation

**Sources:** `https://code.claude.com/docs/en/headless`, `https://code.claude.com/docs/en/cli-reference`, `https://code.claude.com/docs/en/agent-sdk/typescript`

### Subcommands (selected)

`claude` (interactive), `claude "query"`, `claude -p "query"`, `claude -c` / `claude -c -p`, `claude -r "<session>" "query"`, `claude update`, `claude agents [--json]`, `claude attach <id|name>`, `claude logs <id>`, `claude stop <id>`, `claude rm <id>`, `claude respawn <id>`, `claude mcp …`, `claude plugin …`, `claude auth login|logout|status`, `claude doctor` (read-only diagnostics), `claude setup-token`, `claude ultrareview [target] [--json]`, `claude auto-mode defaults|config|reset`, `claude purge [path]`.

### Flags for agent and automation work

| Flag | Notes |
|---|---|
| `-p`, `--print` | Non-interactive |
| `--output-format` | `text` (default), `json`, `stream-json` |
| `--input-format` | `text`, `stream-json` |
| `--include-partial-messages` | With `stream-json` |
| `--include-hook-events` | With `stream-json` |
| `--json-schema '<schema>'` | Validated output after the run. Result appears in `structured_output` |
| `--agent <name>` | Run the session as a named subagent |
| `--agents '<json>'` | Define subagents on the command line. With `-p`, can be a file path (v2.1.281+) |
| `--model <alias\|id>` | |
| `--effort <level>` | `low`, `medium`, `high`, `xhigh`, `max`, `ultracode` |
| `--permission-mode <mode>` | `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`, `manual` |
| `--allowedTools` / `--allowed-tools` | Pre-approves, e.g. `"Bash(git log *)" "Read"`. Space or comma separated |
| `--disallowedTools` | Removes tools from context (bare name) or denies matches (scoped) |
| `--tools` | Restricts built-in tools: `""`, `"default"`, or `"Bash,Edit,Read"` |
| `--max-turns <n>` | Print mode only; exits with error at the limit |
| `--max-budget-usd <amount>` | Stop when estimated API spend reaches it |
| `--resume` / `-r`, `--continue` / `-c`, `--fork-session`, `--session-id <uuid>`, `--name` / `-n` | Session control |
| `--no-session-persistence` | Sessions are not saved and can't be resumed |
| `--append-system-prompt`, `--append-system-prompt-file` | Adds to the default prompt |
| `--system-prompt`, `--system-prompt-file` | Replaces the default prompt |
| `--append-subagent-system-prompt(-file)` | Appends to every subagent's system prompt (`-p` only) |
| `--mcp-config <file-or-json>`, `--strict-mcp-config` | MCP servers |
| `--settings <file-or-json>`, `--setting-sources user,project,local` | Settings |
| `--add-dir <path>` | Grants file access. Does not load most `.claude/` config |
| `--plugin-dir <path>`, `--plugin-url <url>` | Session-only plugins |
| `--worktree` / `-w [name]`, `--tmux` | Runs in `<repo>/.claude/worktrees/<name>` |
| `--bare` | Skips hooks, skills, plugins, MCP, auto memory, and CLAUDE.md discovery. Needs `ANTHROPIC_API_KEY` |
| `--permission-prompts none` | Denies prompts instead of waiting (v2.1.259+) |
| `--init`, `--init-only`, `--maintenance` | Run Setup hooks |
| `--safe-mode` | Disables all customizations for troubleshooting |
| `--restricted` | Refuses command-running built-ins unless named in `--tools` |
| `--bg` / `--background`, `--exec` | Background session or PTY job |
| `--debug`, `--debug-file <path>`, `--verbose` | Debugging |
| `--dangerously-skip-permissions` | Equivalent to `--permission-mode bypassPermissions` |

### Examples (verbatim from the docs)

```bash
claude -p "Find and fix the bug in auth.py" --allowedTools "Read,Edit,Bash"

claude -p "Summarize this project" --output-format json

claude -p "Extract the main function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'

claude -p "Explain recursion" --output-format stream-json --verbose --include-partial-messages

session_id=$(claude -p "Start a review" --output-format json | jq -r '.session_id')
claude -p "Continue that review" --resume "$session_id"

claude -p "Run the test suite and fix any failures" --allowedTools "Bash,Read,Edit"

claude --bare -p "Summarize README.md" --allowedTools "Read"

claude -p "Update the dependency pins and run the tests" --permission-mode auto --permission-prompts none
```

### Output and behavior

- `json` output includes `result`, `session_id`, and `total_cost_usd` (a client-side estimate), plus `structured_output` when `--json-schema` is set.
- `stream-json` emits newline-delimited events. The last line is a `result` message. Subagent messages carry `parent_tool_use_id`. `system/init` lists `mcp_servers`, `plugins`, and `plugin_errors`. Use these to fail CI when a plugin or MCP server does not load.
- Exit codes: 0 on success, non-zero on failure. SIGTERM exits 143.
- `-p` waits for background subagents, workflows, Monitor watches, and self-paced loop wakeups, up to a 10-minute idle ceiling (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`).
- In `-p`, `/plugin` is unavailable, but `/reload-plugins`, `/config key=value`, `/model <arg>`, `/rename`, and skill commands work. `/workflows` and `/agents` do not.
- Bare mode (`--bare`) never reads OAuth credentials or the keychain. Use `ANTHROPIC_API_KEY` or `apiKeyHelper` in `--settings`.

### Agent SDK relationship

The Agent SDK packages the same harness: the agent loop, context management, sessions, hooks, subagents, permissions, MCP, and built-in tools. It is available as the CLI (`claude -p`), as the Python package `claude-agent-sdk`, and as the TypeScript package `@anthropic-ai/claude-agent-sdk`. The `query()` options relevant to this design include `agent`, `agents` (AgentDefinition), `plugins` (`[{type:"local", path}]`), `settingSources` (default: all sources), `settings`, `hooks`, `permissionMode`, `allowedTools`, `disallowedTools`, `canUseTool`, `skills`, `tools`, `additionalDirectories`, and `mcpServers`. The SDK is self-hosted. It is not the Claude API Tool Runner and not Managed Agents.

Example from the SDK reference, verbatim:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Review the open pull requests",
  options: {
    settingSources: ["project"],
    plugins: [{ type: "local", path: "./my-plugin" }],
    agents: {
      reviewer: {
        description: "Reviews code changes",
        prompt: "You are a careful code reviewer.",
        tools: ["Read", "Grep"],
        maxTurns: 10,
      },
    },
    permissionMode: "default",
    allowedTools: ["Read", "Grep"],
  },
})) {
  console.log(message);
}
```

---

## 9. Agent teams, workflows, and task tools

### Agent teams

**Sources:** `https://code.claude.com/docs/en/agent-teams`

- **Status:** experimental and disabled by default.
- **Enable:** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, in the shell or in `settings.json`:
  ```json
  { "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
  ```
- **Requires:** an interactive session. Teammates are not spawned in `-p` mode or Agent SDK runs.
- **Effect on subagents:** while enabled, a subagent that Claude launches with a `name` becomes a teammate. Set the variable to `0` to turn this off.
- **Display modes:** `in-process` (default; agent panel, Enter to view, Ctrl+T toggles the task list, `x` stops a teammate). `split panes` need tmux or iTerm2 with `it2`. Set `teammateMode` or `--teammate-mode auto|tmux|iterm2|in-process`.
- **Teammate vs subagent:**

  | | Subagents | Teammates |
  |---|---|---|
  | Context | Own window; result returns to caller | Own window; fully independent |
  | Communication | Return result to caller | Message each other directly |
  | Coordination | Main agent manages | Self-coordinate, shared task list |
  | Token cost | Lower | Higher (separate Claude instance each) |

- **Model picking for teammates:** spawn prompt model, then the definition's `model`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the lead's model.
- **Spawning from a definition:** name a subagent type in the spawn prompt. The definition's `tools`, `disallowedTools`, `model`, `effort`, and body apply. `skills` do not. `mcpServers` apply only to split-pane teammates.
- **Storage:** team config at `~/.claude/teams/{team-name}/config.json`. Mailboxes at `~/.claude/teams/{team-name}/inboxes/{agent-name}.json`. Tasks at `~/.claude/tasks/{team-name}/`. Team name is `session-` plus the first eight characters of the session ID. There is no project-level equivalent. `.claude/teams/teams.json` is treated as an ordinary file.
- **Hooks:** `TeammateIdle`, `TaskCreated`, and `TaskCompleted`. Exit 2 keeps the teammate working, prevents task creation, or prevents completion.
- **Limitations:** no session resumption for in-process teammates. One team per session. No nested teams. The lead is fixed. Split panes not supported in VS Code's terminal, Windows Terminal, or Ghostty.
- **Message delivery:** messages are delivered automatically. Recipients are told messages come from another Claude session, not from you. In auto mode, a classifier reviews each inter-agent message.

### Workflows (dynamic workflows)

**Sources:** `https://code.claude.com/docs/en/workflows`, `https://code.claude.com/docs/en/agent-sdk/typescript`

**What it is:** a JavaScript script that orchestrates many subagents. The runtime executes it in the background. Intermediate results stay in script variables, not Claude's context.

**Availability:** paid plans, Anthropic API, Bedrock, Agent Platform, and Foundry. On Pro, turn on from `/config`. Disable with `disableWorkflows: true` in settings, `CLAUDE_CODE_DISABLE_WORKFLOWS=1`, or the `/config` toggle.

**Saved workflow file:**

- Project: `.claude/workflows/<name>.js` (committed). Personal: `~/.claude/workflows/<name>.js`. Plugin: `workflows/` in the plugin root, namespaced as `/<plugin>:<name>`. Project overrides personal. Under a monorepo, the nearest `.claude/workflows/` wins.
- Structure: `export const meta = { name, description }` must be the first statement and a plain object literal. Then top-level `await` code.
- Verbatim example from the docs:

```javascript
export const meta = {
  name: 'audit-routes',
  description: 'Audit every route handler for missing auth checks',
}

const found = await agent('List every .ts file under src/routes/.', {
  schema: { type: 'object', required: ['files'], properties: { files: { type: 'array', items: { type: 'string' } } } },
})

const audits = await pipeline(found.files, file =>
  agent(`Audit ${file} for missing authentication checks.`, { label: file }),
)

return audits.filter(Boolean)
```

**Script API (from docs):** `agent(prompt, opts)` spawns one subagent (opts include `schema`, `label`, `stallMs`). `pipeline(items, fn)` runs one per item. `parallel(...)` runs tasks together and waits. `phase(title)` groups progress. `log(msg)` shows a message. The global `args` holds input passed at invocation. Constraints: no `import()`, `Date.now()`, `Math.random()`, or no-argument `new Date()` (these throw so relaunches repeat the same calls). An `agent()` call resolves to `null` if stopped or hit an unrecoverable error.

**Invocation:**

- As a command: `/<name>`, then `/reload-skills` after editing a file on disk.
- As the `Workflow` tool. Input (SDK `WorkflowInput`): `name` (built-in or saved workflow), `script` (inline string), `scriptPath` (takes precedence; needs `Read` tool), `args` (any JSON value, exposed as global `args`), `resumeFromRunId` (resume a run in the same session). `title` and `description` are ignored because the `meta` block sets them. Example input, verbatim:
  ```json
  { "name": "research", "args": { "question": "How does the cache invalidate?" } }
  ```
- Permission to run without a prompt in `-p` or SDK: allow rule `Workflow` (any workflow) or `Workflow(<name>)` (one saved workflow), or the other approval routes in the docs.

**Limits:** 16 concurrent agents by default (`CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`, 1 to 256). 4,096 items per `parallel()` or `pipeline()` call. 1,000 agents per run. No direct filesystem or shell access from the script itself.

**Management:** `/workflows` opens the progress view (keys: `p` pause or resume, `x` stop, `r` restart an agent, `s` save the script as a command, `f` filter). Resume within the same session replays completed agents from saved results.

**Size guideline:** `workflowSizeGuideline` (`unrestricted`, `small`, `medium` default, `large`).

**Bundled:** `/deep-research <question>`.

### Task tools

**Sources:** `https://code.claude.com/docs/en/tools-reference`, `https://code.claude.com/docs/en/agent-sdk/typescript`

| Tool | Input (SDK types) |
|---|---|
| `TaskCreate` | `subject` (required), `description` (required), `activeForm?`, `metadata?`. Returns the new ID |
| `TaskUpdate` | `taskId` (required), `status?` (`pending`, `in_progress`, `completed`, `deleted`), `subject?`, `description?`, `activeForm?`, `addBlocks?`, `addBlockedBy?`, `owner?`, `metadata?` |
| `TaskGet` | `taskId` (required). Returns null for unknown IDs |
| `TaskList` | No parameters. Snapshot of all tasks |
| `TaskOutput` | Deprecated in favor of `Read` on the task's output file |
| `TaskStop` | Stops a background task |
| `TodoWrite` | Replaced by the Task tools by default |

**Availability (important):** Task tools are provided by default only on Claude 3.x, Opus 4 through 4.7, Sonnet 4 through 4.6, and Haiku 4.5. On other models, including Haiku 5.5, Sonnet 5.5, and Opus 5.5, Claude Code omits them unless you opt in:
- `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` (provides the same tools on every model and provider)
- `claude --allowedTools TaskCreate` (naming one of the tools opts in)
- `claude --tools "...,TaskCreate,..."`
- SDK `allowedTools` or `tools`

Background sessions and cloud sessions provide the tools on every model. Subagents get the tools only when the parent session has them.

### SendMessage

`SendMessage` exists. It resumes a completed subagent (`to` set to agent ID or name), messages a teammate, and cross-session messaging. It does not need agent teams enabled. The full input schema (the name of the message parameter and any others) is not in the pages I fetched.

### Cross-session messaging

Documented at `https://code.claude.com/docs/en/cross-session-messaging` (not fetched). It covers sending messages between your own sessions. `/list-agents` (alias `/peers`) lists messageable subagents, teammates, and sessions. `crossSessionInbound` controls acceptance.

---

## 10. Task and plan features

**Sources:** `https://code.claude.com/docs/en/permission-modes`, `https://code.claude.com/docs/en/tools-reference`, `https://code.claude.com/docs/en/commands`

### Permission modes

| Mode | What runs without asking |
|---|---|
| `default` (config name for Manual) | Reads only |
| `acceptEdits` | Reads, file edits, and common filesystem commands (`mkdir`, `touch`, `mv`, `cp`) |
| `plan` | Reads and planning; edits blocked until a plan is approved |
| `auto` | Classifier reviews actions; routine prompts skipped. Requires supported models and plan; Team and Enterprise orgs can disable with `permissions.disableAutoMode: "disable"` in managed settings |
| `dontAsk` | Auto-denies anything that would prompt. Useful in CI |
| `bypassPermissions` | Runs everything. Requires `--allow-dangerously-skip-permissions` to start in it, or opt-in |

Set with `Shift+Tab` (cycle), `--permission-mode <mode>`, or `defaultMode` in settings. `claude --permission-mode plan` starts in plan mode. The startup mode can be `auto` on v2.1.283+ for interactive terminal and VS Code sessions.

### Plan mode

- **Enter:** `Shift+Tab`, `/plan [description]`, `claude --permission-mode plan`, or `"defaultMode": "plan"` in `.claude/settings.json`. The Claude tool is `EnterPlanMode` (no permission needed).
- **Behavior:** Claude reads, explores, and writes a plan but does not edit source. Shell commands during planning follow the classifier (auto mode) or prompts.
- **Exit:** `ExitPlanMode` presents the plan (needs approval). Options: **Yes, and use auto mode**, **Yes, manually approve edits**, **No, keep planning**. `Ctrl+G` opens the plan in your editor. `showClearContextOnPlanAccept` adds a clear-context option.
- **Plan files:** `~/.claude/plans/` by default. Override with `plansDirectory` (relative to project root).
- **Subagents:** the built-in `Plan` agent is read-only research during plan mode (section 1). Teammates spawned while the lead is in plan mode work read-only until their plan is approved.

### Built-in commands relevant to this design

Session and context: `/clear`, `/compact [focus]`, `/context`, `/usage` (`/cost`), `/rewind`, `/resume`, `/export`, `/branch`, `/fork`, `/subtask`, `/btw`, `/memory`, `/init`, `/doctor` (`/checkup`; `/doctor prompt-audit` v2.1.283+), `/skill-doctor` (v2.1.252+, requires feature-flag fetching)

Configuration: `/config [key=value]`, `/model [model]`, `/effort [level|auto|status|ultracode]`, `/permissions` (`/allowed-tools`), `/hooks`, `/agents`, `/skills`, `/reload-skills`, `/reload-plugins [--force]`, `/statusline`, `/plugin [subcommand]`, `/update-config [request]`, `/keybindings`, `/theme`, `/output-style [style]`, `/sandbox`, `/mcp`, `/add-dir <path>`, `/cd <path>`

Work and automation: `/plan`, `/loop [interval] [prompt]` (alias `/proactive`), `/goal [condition|clear]`, `/batch <instruction>`, `/workflows`, `/workflow-authoring`, `/tasks` (alias `/bashes`), `/deep-research`, `/code-review` (`/review`), `/simplify`, `/security-review`, `/debug`, `/verify`, `/run`, `/schedule` (`/routines`), `/list-agents` (`/peers`)

Not found in the command list: `/teams`. Team state is shown in the agent panel, and Ctrl+T toggles the task list.

Commands run in `-p` mode: skill commands and `/model <arg>`, `/effort <arg>`, `/config key=value`, `/rename`, `/output-style`, `/mcp` (text summary), `/reload-plugins`. Interactive-only commands such as `/login` are unavailable.

---

## Gaps and things I could not verify

1. **Hook events I could not fully schema:** `CwdChanged`, `Elicitation`, `ElicitationResult`, `PermissionDenied`, `UserPromptExpansion`, `PostToolBatch`, `StopFailure`, `MessageDisplay`, `DirectoryAdded` (input fields only partially captured).
2. **Triggering `/clear` or `/compact` from a hook:** not documented in any page I read.
3. **Custom compaction instructions via settings:** no key found. Whether CLAUDE.md steers the compaction summary is not documented.
4. **`#` shortcut for auto memory:** not found in the memory docs.
5. **`companionMode` setting:** not found.
6. **`SendMessage` input schema:** only `to` (agent ID or name) is documented. The message parameter name is not.
7. **Managed settings file path per OS:** the `managed-settings.json` location is not stated in the pages I read. `/etc/claude-code/` on Linux is inferred from the managed CLAUDE.md and skills paths.
8. **Task storage outside teams:** the team task directory `~/.claude/tasks/{team-name}/` is documented. The location for non-team sessions is not.
9. **Workflow `meta` keys:** only `name` and `description` appear in examples. The docs mention an optional `phases` list. Other keys are not documented in what I read.
10. **Pages referenced but not fetched:** `hooks-guide`, `checkpointing`, `sessions`, `env-vars`, `plugins/components`, `plugins/cli-reference`, `plugins/dependencies`, `plugins/create-marketplace`, `plugins/host-marketplace`, `plugins/org`, `plugin-evals`, `agents`, `cross-session-messaging`, `statusline`, `output-styles`, `scheduled-tasks`, `goal`, `interactive-mode`. Some claims above rely on summaries of other pages.
11. **Explore model:** the docs say Explore uses the main conversation's model, with an Opus alias exception for Fable on subscription and Console accounts. Verify this against your provider.
12. **Plugin eval:** the manifest reference links to `https://code.claude.com/docs/en/plugin-evals`. I did not fetch it. The embedded reference in this session is the only source I used for `claude plugin eval`.
13. **Haiku 5.5 and Task tools:** per the tools reference, Task tools are not provided by default on Haiku 5.5. Verify in your own session before relying on `TaskCreate`.

---

## Design implications for a portable repo-level system

- **Repo-committed plugin enablement does not install external plugins for collaborators.** Relative-path plugins inside the same marketplace repository load directly. External-source plugins need each collaborator to run `claude plugin install <name>@<marketplace> --scope project`. Put that step in your README or onboarding.
- **Plugin subagents lose hooks, MCP servers, `permissionMode`, and `initialPrompt`.** If your subagents need hooks, ship them in `hooks/hooks.json` at plugin level, or keep the subagent files in the project's `.claude/agents/`.
- **CLAUDE.md is advisory.** Enforce policy with `PreToolUse` hooks (exit 2 or `permissionDecision: "deny"`) and permission rules. Use `disableBypassPermissionsMode` and managed settings for org-level enforcement.
- **Persistence:** use `memory: project` for subagents that need to survive sessions. Keep `MEMORY.md` under 200 lines. Use `${CLAUDE_PLUGIN_DATA}` for plugin state that must survive updates, and never write state to `${CLAUDE_PLUGIN_ROOT}`.
- **Plugin names are permanent.** Use `renames` in the marketplace if you must rename.
- **Validate in CI:** `claude plugin validate --strict <path>`. Use `claude -p --output-format json` and check `plugin_errors` and `mcp_server_errors` in the `system/init` event to fail on load errors.
- **Model pinning:** pin full model IDs in subagent frontmatter (`claude-opus-5-5`, `claude-haiku-5-5`) for reproducibility, and set `CLAUDE_CODE_SUBAGENT_MODEL` for the default. Use `availableModels` in managed settings to restrict.
- **Task tools on current models:** if your workflow depends on `TaskCreate` and friends, opt in explicitly.
- **Workflows vs teams vs subagents:** use subagents for focused delegation, workflows for scripted fan-out with a single consolidated result, and teams only for cooperative work that needs peer messaging. Teams are experimental and have no in-process resumption.