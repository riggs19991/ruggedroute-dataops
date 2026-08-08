#!/usr/bin/env bash
# Stage 2 lands tileset: normalized GeoJSONSeq -> lands.pmtiles (two layers).
#
# Usage: tiles.sh <build_dir>   (expects land_fee.geojsonl + land_overlay.geojsonl)
#
# Zoom contract (client LayerRegistry LANDS_SOURCE): z0-12. Fills must render at
# continental zooms; polygons overzoom cleanly past 12 (renderer clips, no
# re-fetch). Flags follow the research-verified polygon recipe:
#   --detect-shared-borders      keeps adjacent ownership edges coincident under
#                                simplification (no slivers between BLM/USFS)
#   --coalesce-smallest-as-needed merges, never drops, small polygons when a
#                                tile overflows -- ownership must not vanish
#   -P                           parallel read (requires line-delimited input,
#                                which normalize_lands.py guarantees)
set -euo pipefail

BUILD_DIR="${1:?usage: tiles.sh <build_dir>}"
cd "$BUILD_DIR"

test -s land_fee.geojsonl || { echo "land_fee.geojsonl missing/empty" >&2; exit 1; }
touch land_overlay.geojsonl  # overlay may legitimately be empty (see normalize warning)

tippecanoe \
  -o lands.pmtiles \
  --force \
  -Z0 -z12 \
  -P \
  --detect-shared-borders \
  --coalesce-smallest-as-needed \
  --simplification=4 \
  --attribution="USGS PAD-US, BLM, USFS, Wilderness Connect" \
  --name="RuggedRoute lands (ownership + wilderness)" \
  -L land_fee:land_fee.geojsonl \
  -L land_overlay:land_overlay.geojsonl

# Verify, tolerating ONE benign case: a tiny state (RI) can produce no z0 tile
# under -Z0, so the header MinZoom=0 disagrees with the real min tile zoom and
# go-pmtiles >=1.31 fails verify ("header MinZoom=0 does not match min tile z").
# Per-state archives are merge INPUTS only — tile-join iterates present tiles —
# and the merged national archive (which is what ships) always has z0 tiles and
# is verified STRICTLY in the merge-publish job. Any other verify failure is fatal.
if ! pmtiles verify lands.pmtiles 2>&1 | tee verify.out; then
  if grep -q "does not match min tile z" verify.out; then
    echo "::warning::pmtiles verify: benign MinZoom-header/min-tile mismatch (tiny state at -Z0) — tolerated for per-state merge inputs; national archive is verified strictly"
  else
    echo "pmtiles verify failed" >&2
    exit 1
  fi
fi
ls -la lands.pmtiles
