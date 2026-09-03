# RuggedRoute — Session Workflow

How every Claude Code session on a RuggedRoute repo runs, from the first file read to the
handoff for the next agent. Written so another project's Claude can review it and adopt the
same structure. Everything here is taken from the files the agent actually reads and writes;
nothing is aspirational.

## The idea in one paragraph

Every session is a fresh agent with no memory of the last one. So the project, not the agent,
holds the memory: a stable rules file the agent reads first, a running state log the agent
reads second and writes last, and an index of the codebase so the agent never explores blind.
A session is one work chunk: read the baton, do the chunk, verify it honestly, record it,
commit and push, hand the baton back. Context carried past a finished chunk is waste.

## The files

| File | Role | Read by | Changes |
|---|---|---|---|
| `CLAUDE.md` | Read-me-first. Working rules, the per-task protocol, build constraints, authority. Claude Code loads it into context at session start. | The agent, every session, automatically | Rarely. History is kept out of it so the file stays stable for prompt caching. |
| `AGENTS.md` | The same rules for Codex or any other agent. A mirror of `CLAUDE.md`. | Non-Claude agents | Same cadence as `CLAUDE.md` |
| `TASK_STATE.md` | The baton. Reverse-chronological session log: what shipped, verified or not, dead ends, founder actions pending, NEXT. The single source of truth for project state. | The agent, first thing after the rules | Every session, at the end of each work chunk, and committed |
| `docs/CODEBASE_MAP.md` | The index. Route to Screen to ViewModel to Repository to backend path, a reverse index of backend paths, and a short narrative per subsystem. | The agent, by grep, only when it needs a location | In the same commit as any change to routes, screens, ViewModels, repositories, or backend paths |
| `PROMPT_GUIDE.md` | For the human. How to prompt so sessions stay cheap and verifiable, plus the shorthands the agent knows. | The founder | Rarely |
| `docs/plans/YYYY-MM-DD-<feature>.md` and `docs/superpowers/{specs,plans}/` | Dated design specs and implementation plans for big features. Written in one session, executed in another. | The agent executing the plan | New file per feature; a plan is never edited into a different plan |
| `.planning/` | Roadmap layer: `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `MILESTONES.md`, `phases/NN-slug/NN-MM-PLAN.md`, `codebase/*.md`, `research/*.md`, dated audits | The agent, when planning a phase or auditing | Per phase or milestone |
| `docs/PHASE*_FOUNDER_ACTIONS.md`, `docs/PHASE*_DEPLOY_NOTES.md` | Things only the human can do (rotate a key, deploy, back something up) and the order to do them in | The founder | Whenever a phase produces human-only steps |

Rule of thumb for what goes where: a rule that holds for months belongs in `CLAUDE.md`. A
fact about the last session belongs in `TASK_STATE.md`. Where something lives belongs in
`CODEBASE_MAP.md`. What we intend to build belongs in a dated plan. Nothing lives in two
places.

The data-pipeline repo (`ruggedroute-dataops`) runs the same loop with two substitutions,
described in its own section below.

## The session loop

```
boot ─► 0 environment ─► 1 read rules ─► 2 read baton ─► 3 lock target
                                                              │
        ┌─────────────────────────────────────────────────────┘
        ▼
4 orient via index ─► 5 ground truth ─► 6 plan ─► 7 execute ─► 8 verify
                                                     ▲             │
                                                     └── failed ───┘   two failures = stop and re-derive
        ┌──────────────────────────────────────────────────────────┘
        ▼
9 record in TASK_STATE.md ─► 10 diff, commit, push ─► 11 hand off
```

### 0. The environment boots

- On Claude Code on the web the session is a fresh clone in an ephemeral container, checked
  out on a designated `claude/<slug>` branch. Nothing survives the container except what is
  pushed. On the founder's machine it is the working tree, but the rest is identical.
- A SessionStart hook sets the git identity. A Stop hook refuses to end the turn while the
  tree has uncommitted, untracked, or unpushed changes. "Commit and push" is therefore the
  structural last step of every session, not a habit the agent has to remember.
- `CLAUDE.md` is injected into context automatically. The agent does not go looking for it;
  it is already there when the first message arrives.

### 1. Read the rules (`CLAUDE.md`)

What the agent takes from it before doing anything else:

- **Who decides.** "Founder is solo and non-technical; decisions are delegated. Act, don't
  ask." This sets the posture for the whole session: make routine calls, state assumptions,
  confirm only the irreversible.
- **Session start, and nothing more.** Two instructions: read `TASK_STATE.md`; grep
  `docs/CODEBASE_MAP.md` when a location is needed. Never re-derive project state from git
  history or by scanning the tree.
- **The non-negotiables.** Build constraints (pinned versions and the mistakes that waste a
  full build cycle), design-system tokens, the confirm-before list (deleting files,
  force-pushing, large refactors, any production deploy), and the staging rule: never
  `git add -A`, stage files by name, because personal and business docs live untracked at
  the repo root.
- **Token discipline.** Grep first, Read second. Never read a file over 400 lines end to end;
  the known giants are listed with their line counts. Batch every independent tool call into
  one message. Surgical edits over full rewrites. Subagents are research-only, one at a time,
  unless the founder says "rich research". Status updates are one sentence.
- **The think-first protocol and the operating doctrine.** Both are reproduced further down.
  They run inside every task.

### 2. Read the baton (`TASK_STATE.md`)

- Read the top entry; it is the most recent session. Its last bullet is `NEXT:`. If the
  founder gave no task, NEXT is the task.
- Scan the two or three entries below it for `AWAITING founder verify`, `NOT deployed`, and
  `FOUNDER ACTIONS PENDING`. These are open loops that decide what is safe to touch.
- Trust it. If the code disagrees with the log, that is a finding to record in the next
  entry, not a reason to rebuild the state from scratch.

### 3. Lock the target

- Restate the ask in one sentence: what changes, where, and what "done" looks like, including
  the verification bar (compile only, emulator screenshot, device install, deploy).
- If two readings exist, pick the likelier one, say which, and proceed. Never silently guess
  and never stall waiting for permission.

### 4. Orient through the index, not by exploring

- Grep `docs/CODEBASE_MAP.md` for the screen, route, repository, or backend path, then follow
  the row to the files.
- For a large file, grep for the symbol and Read with an offset and limit.
- One research subagent on a cheap model may locate things. All code is written in the main
  session.

### 5. Ground truth before code

- Never edit a file that was not Read this session. Never type a class name, signature, theme
  token, or API call from memory. Grep a real usage in this repo and copy its exact shape.
- Library calls: find how this codebase already calls them. With no example, check the pinned
  version in the version catalog first, because training data is stale for these versions.
- Keep three tiers of knowledge straight and know which one each fact is in: verified (read
  or ran this session), inferred (follows from something verified), recalled (training
  data). Code depends only on verified facts.

### 6. Plan at the right size

- Small task: the six-step protocol inline, no ceremony.
- Bug: follow the bad value upstream to where it is produced and fix it there. The
  explanation must account for all the evidence; one symptom that does not fit the theory
  means the theory is wrong.
- Big feature: plan in one session, execute in another. Session A writes
  `docs/plans/YYYY-MM-DD-<feature>.md` (goal, architecture, ordered tasks with checkboxes,
  verification per task) and asks the founder anything unclear. Session B starts clean with
  "Execute docs/plans/<feature>.md". A multi-session plan carries a short `RESUME-STATE.md`
  next to it: what is done, what remains, the exact task to start with.
- Roadmap-scale work uses `.planning/`: a phase directory holding numbered `PLAN.md` files
  whose frontmatter lists `depends_on`, `files_modified`, `requirements`, and `must_haves`
  (the truths the code must make true and the artifacts it must produce). `STATE.md` tracks
  the current milestone, phase, and plan.

### 7. Execute the smallest correct change

- The minimal diff that fully solves it. No drive-by refactors, no speculative abstraction,
  no "while I'm here". Match the surrounding file's idioms exactly.
- Mentally execute before writing: null or empty input, first and last item, offline,
  recomposition, configuration change, process death.
- Sweep the blast radius. After any rename or signature change, grep every call site and fix
  all of them in the same pass. Touched a data model? Check serialized names, the Room
  schema and migrations, Firestore field names, and the security rules.
- If routes, screens, ViewModels, repositories, or backend paths changed, update
  `docs/CODEBASE_MAP.md` in the same commit.

### 8. Verify before claiming

- Compile check after any multi-file or non-trivial change:

  ```
  ./gradlew :app:compileDebugKotlin 2>&1 | tail -15
  ```

  Run the unit suite when logic changed. A full `assembleDebug` only when an install follows.
- On failure, read the full error, go to the actual line, fix that specific thing. In
  Kotlin and Gradle output the first error is the real one; the rest are cascade.
- Two failed fixes on the same bug is a mandatory stop. Write the contradiction down ("X
  should imply Y, but I observe Z"), re-derive from raw evidence, and only then attempt a
  third fix. Or tell the founder a fresh session is the cheaper path.
- Report the tier reached and never a tier above it. The vocabulary is below.

### 9. Record in `TASK_STATE.md`

Prepend a new entry. Do not edit history except to close a loop the entry opened (for
example, `AWAITING founder verify` becomes `FOUNDER-VERIFIED`). The shape:

```markdown
## Session N (YYYY-MM-DD) — WHAT THIS CHUNK WAS (honest state qualifier)
- What shipped, in the verification vocabulary, with the commit hash. Decisions made and why.
- Dead ends ruled out, so the next agent does not walk them again. Corrections to earlier entries.
- Verification tier reached: compiles clean / tests green / emulator-verified / device-verified / deployed.
- FOUNDER ACTIONS PENDING: anything only the human can do, and the doc that gives the order.
- NEXT: the single most valuable next chunk, and what it is blocked on.
```

Conventions from the real file:

- Session numbers are sequential; same-day follow-ups get a letter (`22`, `22b`). The
  parenthetical in the heading is the honest state: "(compiles clean, NOT deployed)",
  "(authored + verified, NOT deployed)", "(all pushed)".
- Five lines or fewer per chunk. The future agent has none of this session's context, so
  write for them: decisions, dead ends, what is verified versus pending, what waits on the
  founder.
- Older long-form sections (phase ledgers, files-modified lists, incident notes) sit at the
  bottom and are left alone.
- Commit it. About one commit in six on the app repo touches `TASK_STATE.md`, many of them a
  pure `docs(state): ...` commit. The log is part of the deliverable, not private notes.

### 10. Diff, commit, push

- `git diff` before every commit, read as a reviewer: stray debug lines, unintended file
  touches, half-reverted experiments. The diff is the deliverable.
- Stage by name. Never `git add -A`.
- Message shape: `type(scope): outcome`, where the summary states what is now true, and
  `docs(state): ...` for a state-only commit. Illustrative:

  ```
  fix(map): selection card dismisses on empty-map tap
  docs(state): Session 23 log — selection pass compiles clean, NOT device-verified
  ```

  On the data repo the scope is the layer: `roads_tnm: parse go-pmtiles 1.31 bounds (tile
  gate was skipping), Spur modifier verified in ID pilot`.
- Push to the designated branch with `git push -u origin <branch>`. Retry network failures
  with backoff. Never push to a different branch.

### 11. Hand off

- One sentence to the founder: what shipped, which verification tier, and where the artifact
  is (an APK path, a workflow run, a commit).
- When the chunk is done, say so and recommend a fresh session. Context carried past a
  finished chunk is pure waste, and compaction loses the detail that then has to be
  rediscovered by re-reading files.
- List the founder actions that block the next step. Do not do them and do not report them
  as done.

## Verification vocabulary

The state log and the chat use these words, and each means exactly one thing.

| Word | Means |
|---|---|
| `authored` / `written` | Code or rules exist in the tree; nothing has been run |
| `compiles clean` | The compile check passed |
| `tests green` | The unit suite passed |
| `emulator-verified` | Seen working on an emulator, screenshot taken |
| `device-verified` / `FOUNDER-VERIFIED` | Seen working on the real phone, or confirmed by the founder |
| `DISTRIBUTED` / `installed` | The build is on the device or in App Distribution, not yet confirmed working |
| `AWAITING founder verify` | Shipped and waiting for a human look |
| `DEPLOYED` | Rules, functions, or tiles are live in production |
| `NOT deployed` | Deliberately held; the deploy order is written down |
| `LEARNED ON DEVICE` | A fact that only a real device revealed, recorded so nobody relearns it |
| `DEAD END` / `PIVOT` | An approach was tried and ruled out, with the reason |

"Compiled clean" is never reported as "verified working". If tests were not run, the entry
says "not run". Quote actual command output, never a paraphrase of what it probably said.

## Think-first protocol (runs inside every task)

Six steps, in order, from `CLAUDE.md`. Under time pressure this is the fast path; every
skipped step costs a compile cycle or a debugging session later.

1. **Lock the target.** One sentence: what changes, where, what done looks like.
2. **Ground truth before code.** Never trust memory for names, signatures, tokens, or
   versions. Grep a real usage and copy it.
3. **Diagnose cause, not symptom.** Follow the bad value upstream. The theory must fit all
   the evidence.
4. **Design the smallest correct change.** Minimal diff, matching idioms, mentally executed
   against the edge cases.
5. **Sweep the blast radius.** Every call site, every serialized name, every rule that
   references the changed thing.
6. **Verify before claiming.** Compile, read the real error, fix the real line, report the
   tier honestly.

The operating doctrine that governs judgment across a whole session:

- Keep the three knowledge tiers straight. Copy, never retype: version strings, field names,
  route constants, hex values, doc paths are transcribed from the file on screen.
- A familiar-looking symptom is a hypothesis, not a diagnosis. Demand this codebase's
  evidence before acting.
- Before deleting or "fixing" odd code, find out why it is odd (blame, call sites, the state
  log). It usually encodes a bug fix about to be reintroduced.
- Reproduce, or locate the mechanism in code, before fixing. Change one variable at a time.
- Memory of a file goes stale the moment it is edited, and after context compaction. Re-read
  the region before editing a file touched long ago in the session.
- Re-anchor on the original goal after every tangent. A compile error that interrupted a
  feature is a detour, not a new destination.
- Disagree with evidence, once and plainly, then defer to the founder's call.
- Act freely on the reversible (edits, branches, local experiments). Confirm the
  irreversible (deletes, force-pushes, deploys, migrations, anything user-visible in prod).
- Never fabricate verification. One invented "tests pass" destroys the trust that makes
  delegation work.
- Solve the asked problem at the asked scope. The powerful move is the surgical change plus
  a one-line note about what else was noticed, so the founder chooses whether to expand.

## The data-pipeline variant (`ruggedroute-dataops`)

The pipeline repo (government open data to normalized GeoJSON to PMTiles to Cloudflare R2)
runs the same loop with two substitutions.

- **The rules file is `README.md`.** It carries the architecture diagram, a "Design rules
  (from the master plan, do not violate)" list, the per-layer status table (stage, LIVE,
  pilot states), and the founder-only setup steps. The master plan and research archive it
  points to live in the app repo's `docs/` tree.
- **Memory is written into the artifacts instead of a state log.** Every GitHub Actions
  workflow opens with a comment block recording what was learned and why the file is shaped
  the way it is: which secrets idiom parses, which CLI flag silently no-ops, what a previous
  session cost. Each `layers/<layer>/layer.json` carries fields such as `notes`, `pilot`,
  and `phase2_backlog`. Docstrings cite the master-plan section they implement. Commit
  messages state the outcome and the verification. The next agent reads the file it is
  about to change and finds the history right there.

The verification ladder is different too. `cd lib && python3 -m unittest -v` gates every
workflow run. A new layer is dispatched first as a two- or three-state pilot that builds
artifacts only and can never flip the live alias. The pilot's QA stats (feature counts,
kilobytes per feature, golden-bbox drift against the live service) are read before the full
matrix is trusted. Publishing is always a versioned upload plus an alias flip, never an
overwrite in place.

## How the human drives (`PROMPT_GUIDE.md`, condensed)

The agent's loop only works when the sessions it runs in are shaped right. The founder-side
rules:

1. Open with the goal and what "done" looks like.
2. One work chunk per session; `/clear` between unrelated tasks. `TASK_STATE.md` is the
   baton between sessions.
3. State the verification bar explicitly, and only order the level you will actually look at.
4. Paste raw errors; do not describe them.
5. Name the screen or file if known; otherwise say exactly what you saw.
6. Batch related asks into one message.
7. For autonomous runs, rank the priorities and give stop conditions.
8. Two failed fixes on the same bug: stop, `/clear`, restate the problem with what the two
   failures taught.
9. Big feature: plan first, execute second, in separate sessions.
10. Demand evidence, not claims.

Shorthands the agent already knows: "update my phone", "check TASK_STATE", "rich research".

## Adopting this in another repo

The minimum set, in order of payoff:

1. **`CLAUDE.md`** with four sections: one line on what the project is and who decides;
   "Session start" pointing at the state log and the index; the non-negotiables (pinned
   versions, the confirm-before list, the staging rule); and the six-step protocol. Keep
   history out of it so it stays cache-stable. Mirror it as `AGENTS.md` if another agent
   will work the repo.
2. **`TASK_STATE.md`** seeded with one entry: the current state in the vocabulary above and
   a `NEXT:`. Rule: five lines per chunk, prepend, commit.
3. **`docs/CODEBASE_MAP.md`**, generated once by a full pass over every source file (screens,
   view models, repositories, backend paths) and then kept current in the same commit as
   any wiring change. Skip it until the tree is big enough that the agent starts exploring
   blind.
4. **`PROMPT_GUIDE.md`** for the human, adapted to the project's own verification ladder.
5. **`docs/plans/`** for dated plan docs, and `.planning/` only when working in phases
   against a roadmap.

Then run the loop once end to end and notice what the agent had to ask about or rediscover.
Whatever it asked belongs in `CLAUDE.md`. Whatever it rediscovered belongs in
`TASK_STATE.md` or the map.
