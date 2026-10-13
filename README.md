# ruggedroute-dataops

The data platform for [RuggedRoute](https://ruggedroutehq.com)'s map: government open data →
normalized GeoJSON → vector tiles (PMTiles) → Cloudflare R2 → the app.

Master plan: the 2026-08-02 map-data master plan and its research archive
(`docs/plans/2026-08-02-map-data-master-plan.md`, `docs/research/2026-08-02-map-data-research.json`)
are NOT in the app repo today — checked 2026-10-12, no `docs/plans/2026-08-02-*` on its master
branch. Until they are recovered, the per-layer `layers/{layer}/layer.json` manifests and the app
repo's `docs/OFFROAD_ROADMAP.md` are the references.

## Architecture

```
gov bulk downloads ──► GitHub Actions (this repo, scheduled)
                          ogr2ogr → lib/normalize_*.py → tippecanoe → .pmtiles
                          └► versioned upload to R2 (rr-tiles) + KV alias flip
Cloudflare Worker (worker-tiles/) ──► serves /{layer}/{z}/{x}/{y}.mvt + /{layer}.json
                                       from R2 via PMTiles range reads
Android app ──► Mapbox v11 VectorSource pointed at the Worker
```

Design rules (from the master plan — do not violate):
- **Versioned uploads + KV alias flip, never overwrite in place** (overwrites tear in-flight
  PMTiles range reads).
- Bulk downloads are the system of record; live ArcGIS queries are for spot-checks/QA only.
- Every normalizer is tolerant: bad upstream data goes to a review-queue artifact, never crashes.
- OSM-derived layers stay in **separate tilesets** (ODbL isolation). Never conflate into
  public-domain or proprietary tilesets.
- Owner names never enter tiles. (Parcels come later, geometry-only.)

## Layers

| Layer | Source | Workflow | Status |
|---|---|---|---|
| `mvum` (roads + trails, vehicle flags + season windows, NFS-attr enrichment) | USFS MVUM bulk GDBs | `weekly-motorized.yml` | **LIVE** (Stage 0 loop, Stage 1 enrichment) |
| `roads_context` (full road inventory, grey context — never green) | USFS RoadCore bulk GDB | `weekly-motorized.yml` | **LIVE** (weekly) |
| `nfs_trails` (trail system + managed-use seasons; feeds MVUM enrichment) | USFS Trans_Trail_NFS_Publish bulk GDB | `weekly-motorized.yml` | **LIVE** tileset (weekly); no client layer yet |
| `blm_routes` (OHV designation open/limited/closed + limitation text) | BLM GTLF Public Display 0-3 (esridump) | `weekly-motorized.yml` | **LIVE** (weekly) |
| `nps_roads` (park road inventory, seasonal + surface) | NPS Public Roads FeatureServer (esridump) | `weekly-motorized.yml` | **LIVE** (weekly) |
| `lands` (PAD-US ownership fill + wilderness/WSA overlay) | USGS PAD-US 4.1 state GDBs (ScienceBase) | `monthly-ownership.yml` | **LIVE** (Stage 2, national 195 MB) |
| `parcels` (private-parcel boundaries, GEOMETRY ONLY — apn/county/acres/st; QA hard-gates any other attribute) | ~25 clean-license state programs (research 2026-08-09, app repo `docs/research/2026-08-09-free-parcel-boundaries.md`) | `quarterly-parcels.yml` | **LIVE** (quarterly; 22 states + DC in 26 units; MN moved to the gis.data.mn.gov hub 2026-10-12) |
| `roads_tnm` (EVERY road class + terra trails on every acre, styled by class — grey context, never a legal designation; source layers roads_hwy/roads_local/roads_4wd/trails_tnm) | USGS TNM National Transportation Dataset per-state FGDBs (TIGER + USFS + NPS + AK DOT; public domain) | `quarterly-roads.yml` | **LIVE** (national since 2026-08-17; quarterly) |
| rec_pois, … | — | — | per master plan §11 |

Live versions come from the worker, not this table: `https://tiles.ruggedroutehq.com/{layer}.json` →
`version` (2026-10-13: the five weekly layers 20261005, lands 20261003, roads_tnm 20260817,
parcels 20261013).

All five normalizers share `lib/route_common.py` (season parser, tolerant GeoJSONSeq
streaming, deduped review queue). Per-layer manifests live in `layers/{layer}/layer.json`.
QA: `qa/golden_counts.py` (per-layer golden-bbox counts vs the live services) and
`qa/rte_cn_stability.py` (soft stable-key orphan check between consecutive runs).
The worker is layer-name-agnostic: a new tileset goes live purely by uploading
`{layer}-YYYYmmdd-HHMM.pmtiles` and flipping `layer-alias:{layer}` in KV.

## One-time setup (founder)

1. **Enable R2** on the Cloudflare account (Dashboard → R2 → accept terms). Then the
   `rr-tiles` bucket gets created (MCP/wrangler/dashboard — any).
2. **Repo secrets** (Settings → Secrets and variables → Actions):
   - `CLOUDFLARE_API_TOKEN` — custom token with Workers Scripts:Edit, Workers KV:Edit,
     Workers Routes:Edit (deploys the worker, flips KV aliases)
   - `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` — R2 API token
     (Dashboard → R2 → Manage API Tokens → Object Read & Write on rr-tiles)
3. **DNS**: add `tiles.ruggedroutehq.com` as a custom domain on the `rr-tiles` worker once
   deployed (Workers → rr-tiles → Settings → Domains). Until then it serves on workers.dev
   (fine for testing; **workers.dev never edge-caches** — do not ship the app against it).

Until secrets exist, workflows still run: they build the tiles and attach them as Actions
artifacts (plus the review queue) instead of uploading — so the pipeline is provable end-to-end
before any credentials are minted.

## KV

Namespace `rr-tile-aliases` (id `f2f28315ee8f43fb8413d1bcddd20684`), keys
`layer-alias:{layer}` → current versioned object key (e.g. `mvum-20260802.pmtiles`).
