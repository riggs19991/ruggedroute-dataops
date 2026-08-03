# ruggedroute-dataops

The data platform for [RuggedRoute](https://ruggedroutehq.com)'s map: government open data →
normalized GeoJSON → vector tiles (PMTiles) → Cloudflare R2 → the app.

Master plan lives in the app repo: `docs/plans/2026-08-02-map-data-master-plan.md`.
Research archive (every source, endpoint, license, price — verified 2026-08-02):
`docs/research/2026-08-02-map-data-research.json`.

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

| Layer | Workflow | Status |
|---|---|---|
| `mvum` (USFS MVUM roads + trails, vehicle flags + season windows) | `weekly-motorized.yml` | Stage 0 proof-of-loop |
| roads_context (RoadCore), nfs_trails, blm_routes, lands, rec_pois, … | — | Stage 1+ per master plan §11 |

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
