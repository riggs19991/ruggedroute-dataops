# Forge migrations

`forge/installer.py --upgrade` runs the scripts in this directory, in file-name order, against the consumer
repository (design §10.3). A fresh install records every existing migration as applied without running it,
because a fresh install is already at the current schema.

## Contract

- **Name**: `NNNN-<slug>.sh` (run with `bash`) or `NNNN-<slug>.py` (run with the installer's `python3`). Four
  digits, never reused, never renumbered. Anything else in this directory (this README) is ignored.
- **Working directory**: the consumer repository root. Environment: `FORGE_TARGET` (absolute repo root),
  `FORGE_FROM_VERSION` (the installed `.forge/VERSION` before the upgrade), `FORGE_TO_VERSION` (the payload's).
- **Idempotent**: running a migration twice must change nothing the second time. Check the state you are about
  to change before changing it (for example `schema_version` in the file you migrate).
- **Ownership**: only a migration that ships with a `schema_version` bump (a MAJOR release: STATUS, handoff,
  brief or binding schema) may touch project-owned files (`.forge/binding.json`, `.forge/STATUS.json`,
  `.forge/*.jsonl`, `.forge/lessons/`, `.forge/decisions/`, `.forge/tasks/`). Forge-owned files are replaced by
  the installer itself after the migrations ran; a migration never edits them.
- **Failure**: exit non-zero to stop the upgrade. Migrations that already succeeded stay recorded; nothing after
  the failing one runs; the installer exits 1 before copying any Forge-owned file.
- **Bookkeeping**: applied migration file names are recorded in `.forge/install-manifest.json` under
  `"migrations"` as soon as each one succeeds.
- **Standard library only**: Python 3.9+ or bash 3.2 syntax; no `jq` requirement.

## Writing one

```bash
#!/usr/bin/env bash
# 0002-binding-add-forge-pin.sh — example shape (not shipped)
set -eu
python3 - <<'PY'
import json, os
p = os.path.join(os.environ["FORGE_TARGET"], ".forge", "binding.json")
b = json.load(open(p))
if "forge_pin" not in b:                      # idempotent: only when missing
    b["forge_pin"] = os.environ["FORGE_TO_VERSION"]
    json.dump(b, open(p, "w"), indent=2)
PY
```

Test it with `python3 forge/installer.py --target <throwaway repo> --upgrade --dry-run` (prints `migrate <name>`),
then without `--dry-run`, then once more to confirm nothing changes.
