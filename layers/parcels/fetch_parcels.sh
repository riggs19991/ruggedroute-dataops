#!/usr/bin/env bash
# Stage 3 parcels fetch: one matrix unit (state or shard) per invocation.
#
# Reads layers/parcels/sources.json for the unit's adapter config:
#   mode http  — direct bulk download(s) (FGDB/SHP/GeoJSON zip or file). Bulk
#                downloads are the system of record (house rule); zip magic is
#                verified so an HTML error shell never becomes a "tileset".
#   mode rest  — esri2geojson --jsonlines paging of an ArcGIS layer (the
#                blm_routes/nps_roads precedent), fields-limited; shard units
#                add a `where` clause (FL_1/FL_2 split on the county field).
#   mode hub   — ArcGIS Hub download/v1 job API (VT, ME): redirect=false
#                returns a JSON envelope — poll until Completed, then stream
#                the ephemeral resultUrl (fetch_helpers.py hub).
#   mode tnris — TX StratMap: 254 per-county zips via the api.tnris.org
#                manifest; shards filter on the FIPS embedded in filenames
#                (fetch_helpers.py tnris, keys fips_min/fips_max).
#
# Usage: fetch_parcels.sh <UNIT> <out_dir>       # e.g. fetch_parcels.sh UT src
set -euo pipefail

UNIT="${1:?usage: fetch_parcels.sh <UNIT> <out_dir>}"
OUT_DIR="${2:?out_dir required}"
mkdir -p "$OUT_DIR"

SOURCES="$(dirname "$0")/sources.json"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

cfg() { # cfg <key> -> value or empty
  python3 - "$SOURCES" "$UNIT" "$1" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1], encoding="utf-8"))[sys.argv[2]]
v = cfg.get(sys.argv[3], "")
if isinstance(v, list):
    print("\n".join(v))
elif v is not None:
    print(v)
PY
}

MODE="$(cfg mode)"
WHERE="$(cfg where)"

case "$MODE" in
  http)
    i=0
    while IFS= read -r url; do
      [ -z "$url" ] && continue
      i=$((i+1))
      tmp="$OUT_DIR/${UNIT}_${i}.dl"
      echo "fetching $url"
      curl -fSL --retry 3 --retry-delay 5 -A "$UA" -o "$tmp" "$url"
      # Sniff the real type — hub API URLs don't end in an extension, and the
      # extension routes normalize_parcels.py (.zip -> /vsizip/, no extraction:
      # big FGDB zips must never be unzipped on a 14 GB runner).
      magic="$(head -c 1 "$tmp")"
      if head -c 4 "$tmp" | grep -q "PK"; then
        out="$OUT_DIR/${UNIT}_${i}.zip"
      elif [ "$magic" = "{" ] || [ "$magic" = "[" ]; then
        out="$OUT_DIR/${UNIT}_${i}.geojson"
      elif [ "$magic" = "<" ]; then
        # HTML error shell instead of data => fail loudly (lands precedent)
        echo "FETCH FAILED: $tmp looks like an HTML shell" >&2; exit 1
      else
        out="$OUT_DIR/${UNIT}_${i}.bin"
      fi
      mv "$tmp" "$out"
      ls -la "$out"
    done < <(cfg urls)
    ;;
  rest)
    URL="$(cfg urls | head -1)"
    # Request ONLY the mapped fields: full-attribute dumps of a 6M-parcel
    # shard are 15-25 GB of runner disk — geometry + 3 fields fits.
    FIELDS="$(python3 - "$SOURCES" "$UNIT" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1], encoding="utf-8"))[sys.argv[2]]
print(",".join(v for v in (cfg.get("fields") or {}).values() if v))
PY
)"
    echo "esridump $URL ${WHERE:+(where: $WHERE)} ${FIELDS:+(fields: $FIELDS)}"
    ARGS=(--jsonlines)
    [ -n "$FIELDS" ] && ARGS+=(-f "$FIELDS")
    [ -n "$WHERE" ] && ARGS+=(-p "where=$WHERE")
    esri2geojson "${ARGS[@]}" "$URL" "$OUT_DIR/${UNIT}_raw.geojsonl"
    wc -l "$OUT_DIR/${UNIT}_raw.geojsonl"
    ;;
  hub)
    URL="$(cfg urls | head -1)"
    python3 "$(dirname "$0")/fetch_helpers.py" hub "$URL" "$OUT_DIR/${UNIT}_1.zip"
    head -c 4 "$OUT_DIR/${UNIT}_1.zip" | grep -q "PK" || { echo "FETCH FAILED: not a zip" >&2; exit 1; }
    ;;
  tnris)
    URL="$(cfg urls | head -1)"
    FIPS_MIN="$(cfg fips_min)"; FIPS_MAX="$(cfg fips_max)"
    python3 "$(dirname "$0")/fetch_helpers.py" tnris "$URL" "$FIPS_MIN" "$FIPS_MAX" "$OUT_DIR"
    ;;
  *)
    echo "unknown mode '$MODE' for unit $UNIT" >&2; exit 1;;
esac

echo "done"
