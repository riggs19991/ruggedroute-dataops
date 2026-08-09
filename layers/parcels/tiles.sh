#!/usr/bin/env bash
# Stage 3 parcels tileset: normalized GeoJSONSeq -> parcels.pmtiles (one layer).
#
# Usage: tiles.sh <build_dir>   (expects parcels.geojsonl)
#
# Zoom contract (research §5, client LayerRegistry PARCELS_SOURCE): z13-15,
# client overzooms past 15 (Mapbox v11 overzooms vector polygons natively;
# z16 nationwide is the 150 GB+ trap). Flags per the polygon recipe:
#   --detect-shared-borders       adjacent lot edges stay coincident under
#                                 simplification (no slivers between parcels)
#   --coalesce-smallest-as-needed merges, never drops, small lots when a tile
#                                 overflows (z13 town centers) — parcels must
#                                 not vanish
#   -P                            parallel read (line-delimited input
#                                 guaranteed by normalize_parcels.py)
set -euo pipefail

BUILD_DIR="${1:?usage: tiles.sh <build_dir>}"
cd "$BUILD_DIR"

test -s parcels.geojsonl || { echo "parcels.geojsonl missing/empty" >&2; exit 1; }

tippecanoe \
  -o parcels.pmtiles \
  --force \
  -Z13 -z15 \
  -P \
  --detect-shared-borders \
  --coalesce-smallest-as-needed \
  --attribution="State & county parcel records (open data)" \
  --name="RuggedRoute parcels (boundaries only)" \
  -L parcels:parcels.geojsonl

# Same tolerance as lands tiles.sh: a tiny unit can lack a tile at the header
# MinZoom, which go-pmtiles >=1.31 flags. Per-unit archives are merge INPUTS
# only; the merged national archive is verified STRICTLY in merge-publish.
if ! pmtiles verify parcels.pmtiles 2>&1 | tee verify.out; then
  if grep -q "does not match min tile z" verify.out; then
    echo "::warning::pmtiles verify: benign MinZoom-header/min-tile mismatch — tolerated for per-unit merge inputs; national archive is verified strictly"
  else
    echo "pmtiles verify failed" >&2
    exit 1
  fi
fi
ls -la parcels.pmtiles
