#!/usr/bin/env bash
# D1b roads_tnm tileset: four normalized GeoJSONSeq files -> roads_tnm.pmtiles.
#
# Usage: tiles.sh <build_dir>   (expects roads_hwy/roads_local/roads_4wd/trails_tnm .geojsonl)
#   MAXZOOM=13 tiles.sh build   # pilot knob: national size control (layer.json qa.calibration)
#
# Zoom contract (layer.json + both clients): z5-14, client overzooms past 14.
# The LOW-zoom hierarchy is NOT a flag here — every feature carries a
# tippecanoe.minzoom stamped by class in normalize_roads_tnm.py (interstate 5
# … local 10), so z5-9 tiles are small and deterministic. Flags per the line
# recipe (weekly-motorized idiom + tippecanoe 2.79.0 README, verified 2026-08-16):
#   --drop-densest-as-needed          urban z10-12 tiles overflow 500 KB; thin
#                                     the densest streets rather than fail
#   -pn / --no-simplification-of-shared-nodes
#                                     keep junction nodes under simplification so
#                                     the network stays connected (README: "use
#                                     this instead of --detect-shared-borders")
#   -P                                parallel read (line-delimited input
#                                     guaranteed by the normalizer)
set -euo pipefail

BUILD_DIR="${1:?usage: tiles.sh <build_dir>}"
MAXZOOM="${MAXZOOM:-14}"
cd "$BUILD_DIR"

test -s roads_hwy.geojsonl || test -s roads_local.geojsonl \
  || { echo "no road features (roads_hwy + roads_local both empty)" >&2; exit 1; }
# A unit may legitimately lack 4WD roads or trails (DC) — empty layer files are fine
touch roads_hwy.geojsonl roads_local.geojsonl roads_4wd.geojsonl trails_tnm.geojsonl

tippecanoe \
  -o roads_tnm.pmtiles \
  --force \
  -Z5 -z"$MAXZOOM" \
  -P \
  --drop-densest-as-needed \
  --no-simplification-of-shared-nodes \
  --attribution="USGS The National Map: National Transportation Dataset; U.S. Census Bureau – TIGER/Line; U.S. Forest Service" \
  --name="RuggedRoute roads_tnm (every road + terra trail, context only)" \
  -L roads_hwy:roads_hwy.geojsonl \
  -L roads_local:roads_local.geojsonl \
  -L roads_4wd:roads_4wd.geojsonl \
  -L trails_tnm:trails_tnm.geojsonl

# Same tolerance as lands/parcels tiles.sh: a tiny unit can lack a tile at the
# header MinZoom (DC has interstates, but keep the guard), which go-pmtiles
# >=1.31 flags. Per-unit archives are merge INPUTS only; the merged national
# archive is verified STRICTLY in merge-publish.
if ! pmtiles verify roads_tnm.pmtiles 2>&1 | tee verify.out; then
  if grep -q "does not match min tile z" verify.out; then
    echo "::warning::pmtiles verify: benign MinZoom-header/min-tile mismatch — tolerated for per-unit merge inputs; national archive is verified strictly"
  else
    echo "pmtiles verify failed" >&2
    exit 1
  fi
fi
ls -la roads_tnm.pmtiles
pmtiles show roads_tnm.pmtiles | head -30
