// rr-tiles: serves self-hosted PMTiles layers from R2 as z/x/y vector/raster tiles.
// Routes:
//   GET /{layer}/{z}/{x}/{y}.mvt   -> tile
//   GET /{layer}.json              -> TileJSON
// Layer name resolves through KV alias `layer-alias:{layer}` -> versioned R2 key
// (falls back to `{layer}.pmtiles`). Versioned keys + alias flips prevent torn
// range reads during weekly republishes (master plan §5).
import { PMTiles } from "pmtiles";

class R2Source {
  constructor(bucket, key) {
    this.bucket = bucket;
    this.key = key;
  }
  getKey() {
    return this.key;
  }
  async getBytes(offset, length) {
    const obj = await this.bucket.get(this.key, { range: { offset, length } });
    if (obj === null) throw new Error(`R2 key not found: ${this.key}`);
    return { data: await obj.arrayBuffer() };
  }
}

const TILE_RE = /^\/([a-z0-9_-]+)\/(\d+)\/(\d+)\/(\d+)\.mvt$/;
const TILEJSON_RE = /^\/([a-z0-9_-]+)\.json$/;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
};

async function resolveKey(env, layer) {
  const alias = await env.ALIASES.get(`layer-alias:${layer}`);
  return alias || `${layer}.pmtiles`;
}

export default {
  async fetch(request, env, ctx) {
    if (request.method === "OPTIONS") return new Response(null, { headers: CORS });
    if (request.method !== "GET" && request.method !== "HEAD")
      return new Response("method not allowed", { status: 405 });

    const url = new URL(request.url);
    const tileMatch = TILE_RE.exec(url.pathname);
    const jsonMatch = tileMatch ? null : TILEJSON_RE.exec(url.pathname);
    if (!tileMatch && !jsonMatch) return new Response("not found", { status: 404, headers: CORS });

    const layer = (tileMatch || jsonMatch)[1];
    const key = await resolveKey(env, layer);

    // Cache key includes the resolved version so alias flips invalidate naturally.
    const cacheKey = new Request(`https://cache.internal/${key}${url.pathname}`);
    const cache = caches.default;
    const hit = await cache.match(cacheKey);
    if (hit) return hit;

    const pm = new PMTiles(new R2Source(env.BUCKET, key));
    let response;
    try {
      if (tileMatch) {
        const [, , z, x, y] = tileMatch;
        const tile = await pm.getZxy(Number(z), Number(x), Number(y));
        if (!tile || !tile.data || tile.data.byteLength === 0) {
          response = new Response(null, { status: 204, headers: CORS });
        } else {
          response = new Response(tile.data, {
            headers: {
              ...CORS,
              "Content-Type": "application/vnd.mapbox-vector-tile",
              "Cache-Control": "public, max-age=86400",
              "X-RR-Version": key,
            },
          });
        }
      } else {
        const header = await pm.getHeader();
        const meta = (await pm.getMetadata()) || {};
        const tilejson = {
          tilejson: "3.0.0",
          name: layer,
          tiles: [`${url.origin}/${layer}/{z}/{x}/{y}.mvt`],
          minzoom: header.minZoom,
          maxzoom: header.maxZoom,
          bounds: [header.minLon, header.minLat, header.maxLon, header.maxLat],
          vector_layers: meta.vector_layers || [],
          attribution: meta.attribution || "",
          version: key,
        };
        response = new Response(JSON.stringify(tilejson), {
          headers: { ...CORS, "Content-Type": "application/json", "Cache-Control": "public, max-age=3600" },
        });
      }
    } catch (e) {
      return new Response(`layer unavailable: ${e.message}`, { status: 404, headers: CORS });
    }

    ctx.waitUntil(cache.put(cacheKey, response.clone()));
    return response;
  },
};
