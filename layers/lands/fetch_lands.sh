#!/usr/bin/env bash
# Stage 2 lands fetch: PAD-US 4.1 from USGS ScienceBase.
#
# THE ENDPOINT THAT WORKS (verified 2026-08-07): ScienceBase file downloads
# stream from   https://www.sciencebase.gov/catalog/file/get/{item}?name={file}
# with a real browser User-Agent. The item JSON's own `url` and `downloadUri`
# fields both return the manager SPA HTML shell to curl -- do not use them.
# sciencebase.gov 403s non-browser UAs on some paths; always send UA.
#
# Usage:
#   fetch_lands.sh national <out_dir>        # PAD-US national GDB (~3 GB zip)
#   fetch_lands.sh state UT <out_dir>        # one state GDB (dev / matrix jobs)
set -euo pipefail

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
NATIONAL_ITEM="652d4fc5d34e44db0e2ee45e"   # PAD-US 4.1 national FGDB item
STATE_ITEM="6759abcfd34edfeb8710a004"      # PAD-US 4.1 state downloads item

MODE="${1:?usage: fetch_lands.sh national|state [STATE] <out_dir>}"

fetch_item_file() {
  local item="$1" name="$2" out="$3"
  echo "fetching $name from item $item"
  curl -sfL -A "$UA" -o "$out" \
    "https://www.sciencebase.gov/catalog/file/get/${item}?name=${name}"
  # An HTML shell instead of a zip means the endpoint shape regressed -- fail
  # loudly rather than shipping a 4 KB "tileset".
  file "$out" | grep -qi "zip" || { echo "FETCH FAILED: $out is not a zip" >&2; exit 1; }
}

# Find the (single) GDB zip filename on an item, robust to 4.2/5.0 renames.
item_gdb_filename() {
  local item="$1" pattern="$2"
  curl -sfL -A "$UA" "https://www.sciencebase.gov/catalog/item/${item}?format=json&fields=files" \
    | python3 -c "
import json, sys
d = json.load(sys.stdin)
names = [f['name'] for f in d.get('files', []) if '$pattern' in f['name'] and f['name'].endswith('.zip')]
if not names:
    sys.exit('no file matching $pattern on item $item')
print(names[0])
"
}

case "$MODE" in
  national)
    OUT_DIR="${2:?out_dir required}"; mkdir -p "$OUT_DIR"
    NAME="$(item_gdb_filename "$NATIONAL_ITEM" "GDB")"
    fetch_item_file "$NATIONAL_ITEM" "$NAME" "$OUT_DIR/padus_national_gdb.zip"
    ;;
  state)
    STATE="${2:?state code required}"; OUT_DIR="${3:?out_dir required}"; mkdir -p "$OUT_DIR"
    NAME="PADUS4_1_State_${STATE}_GDB_KMZ.zip"
    fetch_item_file "$STATE_ITEM" "$NAME" "$OUT_DIR/padus_${STATE}.zip"
    ;;
  *)
    echo "unknown mode: $MODE" >&2; exit 1;;
esac

echo "done"
