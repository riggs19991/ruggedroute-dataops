#!/usr/bin/env bash
# D1b roads_tnm fetch: one matrix unit (USPS state code) per invocation.
#
# Every unit is the same adapter — ONE per-state FileGDB zip from the USGS TNM
# staged-products bucket (layers/roads_tnm/sources.json). Bulk downloads are the
# system of record (house rule); the zip is kept ZIPPED and read in place via
# /vsizip/ by normalize_roads_tnm.py (TX/CA zips are 750-800 MB and inflate
# ~2.9x — never unzip on a 14 GB runner). Zip magic is verified so an HTML
# error shell can never become a "tileset" (lands/parcels precedent).
#
# Usage: fetch_roads_tnm.sh <UNIT> <out_dir>      # e.g. fetch_roads_tnm.sh ID src
set -euo pipefail

UNIT="${1:?usage: fetch_roads_tnm.sh <UNIT> <out_dir>}"
OUT_DIR="${2:?out_dir required}"
mkdir -p "$OUT_DIR"

SOURCES="$(dirname "$0")/sources.json"
# Browser UA: prd-tnm S3 serves anonymously, but federal fronts have rejected
# default curl UAs before (ScienceBase, FDOR) — same string as parcels.
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

cfg() { # cfg <key> -> value or empty
  python3 - "$SOURCES" "$UNIT" "$1" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1], encoding="utf-8"))
unit = cfg.get(sys.argv[2])
if unit is None:
    sys.exit(f"unknown unit {sys.argv[2]!r} in {sys.argv[1]}")
v = unit.get(sys.argv[3], "")
print("" if v is None else v)
PY
}

URL="$(cfg url)"
EXPECTED_BYTES="$(cfg zip_bytes)"
[ -n "$URL" ] || { echo "no url for unit $UNIT" >&2; exit 1; }

tmp="$OUT_DIR/${UNIT}_1.dl"
echo "fetching $URL"
curl -fSL --retry 3 --retry-delay 10 -A "$UA" -o "$tmp" "$URL"

if ! head -c 4 "$tmp" | grep -q "PK"; then
  if [ "$(head -c 1 "$tmp")" = "<" ]; then
    echo "FETCH FAILED: $tmp is an HTML shell, not a zip" >&2
  else
    echo "FETCH FAILED: $tmp is not a zip (bad magic)" >&2
  fi
  head -c 300 "$tmp" >&2 || true
  exit 1
fi

out="$OUT_DIR/${UNIT}_1.zip"
mv "$tmp" "$out"
GOT="$(stat -c %s "$out" 2>/dev/null || stat -f %z "$out")"
ls -la "$out"

# Vintage drift is INFORMATIONAL: filenames are unversioned, so a refreshed
# upstream zip legitimately changes size. Only a tiny file is fatal.
if [ "$GOT" -lt 1000000 ]; then
  echo "FETCH FAILED: $out is ${GOT} bytes (< 1 MB) — not a state GDB" >&2; exit 1
fi
if [ -n "$EXPECTED_BYTES" ] && [ "$GOT" != "$EXPECTED_BYTES" ]; then
  echo "::notice::$UNIT zip is $GOT bytes vs sources.json $EXPECTED_BYTES — upstream vintage changed; refresh sources.json after this run"
fi
echo "done"
