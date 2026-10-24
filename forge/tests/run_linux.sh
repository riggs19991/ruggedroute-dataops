#!/usr/bin/env bash
# run_linux.sh — run the Forge test suite (or any command) against this checkout's forge/ inside a Linux container.
#
# The suite spawns the .forge/bin shebang scripts, which Windows cannot exec, and an autocrlf checkout carries CRLF
# in its working tree. So the container copies forge/ out of a read-only mount of the repository, strips CR, puts
# back the exec bits git records, and runs the command from the copy's parent (so `forge/...` paths work as in CI).
#
#   bash forge/tests/run_linux.sh                                      # python3 -m unittest discover -s forge/tests
#   bash forge/tests/run_linux.sh python3 forge/tools/make_plugin.py --check
#   bash forge/tests/run_linux.sh bash forge/tests/hook_smoke.sh
#   FORGE_LINUX_IMAGE=python:3.9 bash forge/tests/run_linux.sh         # another image (needs git and python3)
# Exit code: the command's; 3 when docker is missing.
set -eu
REPO=$(cd "$(dirname "$0")/../.." && pwd)
IMAGE=${FORGE_LINUX_IMAGE:-python:3.12}
if [ $# -eq 0 ]; then set -- python3 -m unittest discover -s forge/tests; fi
command -v docker >/dev/null 2>&1 || { echo "run_linux.sh: docker not found" >&2; exit 3; }
HOST=$REPO
if command -v cygpath >/dev/null 2>&1; then HOST=$(cygpath -w "$REPO"); fi   # Git Bash: docker wants a Windows path
MSYS_NO_PATHCONV=1 docker run --rm -v "$HOST:/src:ro" -w /work "$IMAGE" bash -c '
  set -e
  cp -r /src/forge /work/forge
  find /work/forge -type f -exec sed -i "s/\r$//" {} +
  find /work/forge -type f -exec chmod 644 {} +
  git config --global --add safe.directory /src >/dev/null 2>&1 || true
  git -C /src ls-files -s -- forge 2>/dev/null | while read -r mode _hash _stage path; do
    if [ "$mode" = 100755 ] && [ -f "/work/$path" ]; then chmod 755 "/work/$path"; fi
  done
  chmod 755 /work/forge/install.sh /work/forge/installer.py /work/forge/tools/make_plugin.py /work/forge/tests/*.sh
  cd /work && exec "$@"' _ "$@"
