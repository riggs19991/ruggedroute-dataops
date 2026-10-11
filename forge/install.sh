#!/usr/bin/env bash
# install.sh — thin wrapper around installer.py (design §10.1; MODULE-API §8). bash 3.2 compatible.
#
#   bash install.sh [--target DIR] [installer options]                 # payload next to this script (local checkout / plugin)
#   bash install.sh --from ~/src/forge [--target DIR] [options]         # a local checkout (its forge/ or root)
#   curl -fsSL <raw url>/install.sh | bash -s -- --repo OWNER/REPO --tag v1.0.0 [--target DIR] [options]
#
# Installer options are passed through: --target --upgrade --force --dry-run --effort low|medium --no-model
# --with-bench --binding FILE --project NAME (see python3 installer.py --help).
# Exit codes: those of installer.py; 2 usage; 3 when python3 >= 3.9 or the payload cannot be found.
set -eu

usage() {
  sed -n '2,12p' "$0" 2>/dev/null | sed 's/^# \{0,1\}//'
}

FROM=""
REPO=""
TAG=""
PASS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --from) [ $# -ge 2 ] || { echo "install.sh: --from needs a directory" >&2; exit 2; }; FROM=$2; shift 2 ;;
    --repo) [ $# -ge 2 ] || { echo "install.sh: --repo needs OWNER/REPO" >&2; exit 2; }; REPO=$2; shift 2 ;;
    --tag)  [ $# -ge 2 ] || { echo "install.sh: --tag needs a tag" >&2; exit 2; }; TAG=$2; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) PASS+=("$1"); shift ;;
  esac
done

# 1. Python 3.9+ (the Forge scripts are standard-library Python).
if ! command -v python3 >/dev/null 2>&1; then
  echo "install.sh: python3 not found; install Python 3.9+ (macOS: brew install python; Debian/Ubuntu: apt install python3)" >&2
  exit 3
fi
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'; then
  echo "install.sh: $(python3 --version 2>&1) is too old; the Forge needs Python 3.9+" >&2
  exit 3
fi

# 2. Resolve the directory holding installer.py + payload/.
find_installer() {  # find_installer DIR -> prints the directory containing installer.py and payload/
  for cand in "$1" "$1/forge"; do
    if [ -f "$cand/installer.py" ] && [ -d "$cand/payload/.forge" ]; then
      (cd "$cand" && pwd)
      return 0
    fi
  done
  return 1
}

TMP=""
cleanup() { if [ -n "$TMP" ]; then rm -rf "$TMP"; fi; }
trap cleanup EXIT

SRC=""
if [ -n "$FROM" ]; then
  SRC=$(find_installer "$FROM") || { echo "install.sh: no installer.py + payload/ under $FROM (or $FROM/forge)" >&2; exit 3; }
elif [ -n "$REPO" ] || [ -n "$TAG" ]; then
  [ -n "$REPO" ] && [ -n "$TAG" ] || { echo "install.sh: --repo OWNER/REPO and --tag TAG go together" >&2; exit 2; }
  TMP=$(mktemp -d "${TMPDIR:-/tmp}/forge-install.XXXXXX")
  if command -v git >/dev/null 2>&1; then
    git clone --quiet --depth 1 --branch "$TAG" "https://github.com/$REPO.git" "$TMP/src" \
      || { echo "install.sh: cannot clone https://github.com/$REPO.git at $TAG" >&2; exit 3; }
    echo "install.sh: fetched $REPO@$TAG ($(git -C "$TMP/src" rev-parse --short HEAD))"
  elif command -v curl >/dev/null 2>&1 && command -v tar >/dev/null 2>&1; then
    mkdir -p "$TMP/src"
    curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/tags/$TAG" -o "$TMP/src.tar.gz" \
      || { echo "install.sh: cannot download $REPO@$TAG" >&2; exit 3; }
    tar -xzf "$TMP/src.tar.gz" -C "$TMP/src" --strip-components 1
    if command -v shasum >/dev/null 2>&1; then SUM=$(shasum -a 256 "$TMP/src.tar.gz" | cut -d' ' -f1); else SUM=$(sha256sum "$TMP/src.tar.gz" | cut -d' ' -f1); fi
    echo "install.sh: fetched $REPO@$TAG tarball sha256 $SUM"
  else
    echo "install.sh: need git, or curl and tar, to fetch $REPO@$TAG" >&2
    exit 3
  fi
  SRC=$(find_installer "$TMP/src") || { echo "install.sh: $REPO@$TAG has no installer.py + payload/ (root or forge/)" >&2; exit 3; }
else
  HERE=""
  if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
    HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
  fi
  if [ -n "$HERE" ]; then SRC=$(find_installer "$HERE") || SRC=""; fi
  if [ -z "$SRC" ]; then
    echo "install.sh: no local payload next to this script; pass --from DIR or --repo OWNER/REPO --tag TAG" >&2
    exit 3
  fi
fi

# 3. Run the installer (not exec: the trap must remove a fetched checkout afterwards).
set +e
python3 "$SRC/installer.py" ${PASS[@]+"${PASS[@]}"}
CODE=$?
set -e
exit $CODE
