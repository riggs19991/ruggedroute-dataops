# Upgrading the Forge

Design §8.2 (ownership), §10.3 (upgrade); installer contract: `docs/MODULE-API.md` §8.

## The ownership contract

Every file the Forge puts into a consumer repository has exactly one owner. **Ownership is the upgrade contract.**

| Owner | Files | On upgrade |
|---|---|---|
| **Forge-owned** | `.forge/FORGE.md`, `RUNBOOK.md`, `ROUTING.md`, `HOOKS.md`, `SCHEMAS.md`, `GATES.md`, `ROLE-architect.md`, `VERSION`; `.forge/bin/**`; `.forge/schemas/**`; `.forge/templates/**`; `.forge/install-manifest.json`; `.claude/agents/forge-*.md`; `.claude/skills/forge-*/`; `.claude/rules/forge-stack-*.md`; `.claude/settings.forge.json` | overwritten; a file whose sha256 differs from `install-manifest.json` (edited locally) is named in a warning: `--upgrade` backs it up to `.forge/incidents/upgrade-<ts>/` and replaces it, a plain install refuses it unless `--force` |
| **Merged** | `.claude/settings.json` | scalars from the fragment are written only when absent locally; a differing local scalar (`model`, `effortLevel`, `env.*`, …) is kept and printed as `settings: <key> local=… -> fragment=…`, and only `--force-settings` applies the fragment's value (`--force` never touches settings); arrays are unioned; hook entries whose `command` starts with `"$CLAUDE_PROJECT_DIR"/.forge/bin/` are replaced, every other entry is kept; `permissions.allow` gains one `Bash(<prefix> *)` per `binding.verify[].cmd`, `bootstrap` and `smoke` (the fragment itself carries no project-specific command rule) |
| **Merged** | `CLAUDE.md` | only the text between `<!-- forge:begin … -->` and `<!-- forge:end -->` is replaced |
| **Project-owned** | `.forge/binding.json`, `STATUS.json`, `ledger.jsonl`, `history.jsonl`, `queue.jsonl`, `CHANGELOG.md`, `COST-REPORT.md`, `tasks/**`, `lessons/**`, `decisions/**`, `archive/**`; `.claude/agent-memory/**`; `.claude/rules/project-*.md` | never touched, except by a migration on a schema MAJOR |
| **Local, gitignored** | `.forge/.runtime/`, `.forge/incidents/` | left alone |

The manifest doubles as the policy-lock list: no model may edit a Forge-owned file (GATES.md gate 14). Change Forge-owned files in
the Forge source repository and release them; change project-owned policy files (`binding.json`) by hand.

## Versioning (semver)

- **MAJOR** — a change to the STATUS, handoff, brief or binding schema (anything under `.forge/schemas/` that existing files must be
  migrated for). Ships a migration.
- **MINOR** — additive: a new agent, skill, hook registration, rule or template; a new routing default.
- **PATCH** — prompt or documentation text.

Agent and skill names are permanent (they appear in STATUS, ledgers and settings). The single version source is `forge/VERSION`; the
consumer copy is `.forge/VERSION`; a consumer may pin the version it expects in `binding.json` → `forge_pin`. Nothing auto-updates:
`/forge-doctor` warns when `.forge/VERSION` lags `forge_pin` or the Forge source checkout.

## Upgrade steps

1. Read the CHANGELOG entries between your `.forge/VERSION` and the target version. A MAJOR means a migration will rewrite project
   files; close or park the open task first (`/forge-close` or `/forge-close --partial`).
2. Dry run from the consumer repo root:
   ```bash
   bash <forge checkout>/install.sh --target . --upgrade --dry-run
   ```
   It lists the Forge-owned files it would overwrite, the ones that drifted from the manifest, the settings entries it would replace,
   and the migrations it would apply.
3. Resolve drift: for each locally edited Forge-owned file, either upstream the change to the Forge repo or accept the overwrite
   (`--upgrade` keeps a backup under `.forge/incidents/upgrade-<ts>/`). Never keep a local edit to a Forge-owned file; the next upgrade
   would replace it. Review the `settings: <key> local=… -> fragment=…` lines and pass `--force-settings` only if you want the
   fragment's values.
4. Run the upgrade (`--upgrade` without `--dry-run`). In order it: applies `migrations/` newer than `.forge/VERSION` (idempotent,
   only these may touch project-owned files), overwrites Forge-owned files, re-merges settings and the CLAUDE.md fragment, rewrites
   `install-manifest.json` and `.forge/VERSION`, prints the CHANGELOG delta and runs `.forge/bin/forge-doctor --report --no-probes`.
5. Verify in a session: `/forge-doctor`, then `.forge/bin/forge-doctor --probe-hooks`. Fix every FAIL (RUNBOOK.md §12).
6. Update `binding.json` → `forge_pin` if you pin, and commit everything as one commit (`forge: upgrade to vX.Y.Z`).

## Writing a migration (Forge maintainers)

- One file per schema bump in `forge/migrations/`, named `NNNN-<slug>`, applied in order, **idempotent** (running it twice is a no-op),
  touching only the project-owned files the schema change requires.
- Bump `schema_version` in the migrated files and in `forgelib` together; `forge-status validate` must pass afterwards.
- Add a CHANGELOG entry under a new MAJOR version that says what the migration changes.

## Downgrading

There is no downgrade command and no reverse migration. Revert the upgrade commit (or restore the files from git at the commit
before it).
