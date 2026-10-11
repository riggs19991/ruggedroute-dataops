---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
---
# Forge stack rules — web / TypeScript
- Lockfile installs only (`npm ci`, `pnpm install --frozen-lockfile`, `yarn install --frozen-lockfile`); never add or upgrade a dependency the brief did not ask for.
- The check is the `scripts.test` command in `package.json` when it exists; when it does not, the brief names the command that proves the change (a build, a type-check, a dry run).
- Run every command from the repository root.
