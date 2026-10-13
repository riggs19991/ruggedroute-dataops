// End-to-end tests for the rr-tiles worker (src/index.js) under Node's built-in test runner.
// No Cloudflare runtime: R2, KV and caches.default are replaced with in-memory fakes, and the
// PMTiles archive is built here, byte for byte, following the v3 spec with no compression.
import { test } from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

// ---------- PMTiles v3 archive builder (spec: https://github.com/protomaps/PMTiles/blob/main/spec/v3/spec.md)

function varint(n) {
  const out = [];
  while (n >= 0x80) {
    out.push((n & 0x7f) | 0x80);
    n = Math.floor(n / 128);
  }
  out.push(n);
  return out;
}

function rotate(n, x, y, rx, ry) {
  if (ry === 0) {
    if (rx !== 0) return [n - 1 - y, n - 1 - x];
    return [y, x];
  }
  return [x, y];
}

function zxyToTileId(z, x, y) {
  let acc = ((1 << z) * (1 << z) - 1) / 3;
  let a = z - 1;
  let [tx, ty] = [x, y];
  for (let s = 1 << a; s > 0; s >>= 1) {
    const rx = tx & s;
    const ry = ty & s;
    acc += ((3 * rx) ^ ry) * (1 << a);
    [tx, ty] = rotate(s, tx, ty, rx, ry);
    a--;
  }
  return acc;
}

function serializeDirectory(entries) {
  const bytes = [...varint(entries.length)];
  let last = 0;
  for (const e of entries) {
    bytes.push(...varint(e.tileId - last));
    last = e.tileId;
  }
  for (const e of entries) bytes.push(...varint(e.runLength));
  for (const e of entries) bytes.push(...varint(e.length));
  entries.forEach((e, i) => {
    const contiguous = i > 0 && e.offset === entries[i - 1].offset + entries[i - 1].length;
    bytes.push(...varint(contiguous ? 0 : e.offset + 1));
  });
  return Uint8Array.from(bytes);
}

/** Build a clustered, uncompressed PMTiles v3 archive holding the given MVT tiles. */
export function buildArchive({ tiles, metadata, minZoom, maxZoom, bounds }) {
  const sorted = tiles
    .map((t) => ({ ...t, tileId: zxyToTileId(t.z, t.x, t.y) }))
    .sort((a, b) => a.tileId - b.tileId);
  const entries = [];
  let offset = 0;
  for (const t of sorted) {
    entries.push({ tileId: t.tileId, offset, length: t.data.length, runLength: 1 });
    offset += t.data.length;
  }
  const rootDir = serializeDirectory(entries);
  const meta = new TextEncoder().encode(JSON.stringify(metadata));
  const tileData = new Uint8Array(offset);
  entries.forEach((e, i) => tileData.set(sorted[i].data, e.offset));

  const HEADER = 127;
  const rootOffset = HEADER;
  const metaOffset = rootOffset + rootDir.length;
  const tileOffset = metaOffset + meta.length;
  const buf = new Uint8Array(tileOffset + tileData.length);
  const v = new DataView(buf.buffer);
  buf.set(new TextEncoder().encode("PMTiles"), 0);
  v.setUint8(7, 3);
  const u64 = (at, n) => v.setBigUint64(at, BigInt(n), true);
  u64(8, rootOffset);
  u64(16, rootDir.length);
  u64(24, metaOffset);
  u64(32, meta.length);
  u64(40, 0); // leaf directories: none
  u64(48, 0);
  u64(56, tileOffset);
  u64(64, tileData.length);
  u64(72, entries.length); // addressed tiles
  u64(80, entries.length); // tile entries
  u64(88, entries.length); // tile contents
  v.setUint8(96, 1); // clustered
  v.setUint8(97, 1); // internal compression: none
  v.setUint8(98, 1); // tile compression: none
  v.setUint8(99, 1); // tile type: MVT
  v.setUint8(100, minZoom);
  v.setUint8(101, maxZoom);
  const e7 = (deg) => Math.round(deg * 1e7);
  v.setInt32(102, e7(bounds[0]), true);
  v.setInt32(106, e7(bounds[1]), true);
  v.setInt32(110, e7(bounds[2]), true);
  v.setInt32(114, e7(bounds[3]), true);
  v.setUint8(118, minZoom);
  v.setInt32(119, e7((bounds[0] + bounds[2]) / 2), true);
  v.setInt32(123, e7((bounds[1] + bounds[3]) / 2), true);
  buf.set(rootDir, rootOffset);
  buf.set(meta, metaOffset);
  buf.set(tileData, tileOffset);
  return buf;
}

// ---------- Cloudflare binding fakes

class FakeBucket {
  constructor(objects) {
    this.objects = objects; // key -> Uint8Array
    this.gets = []; // [key, offset, length]
  }
  async get(key, opts = {}) {
    const { offset = 0, length } = opts.range || {};
    this.gets.push([key, offset, length]);
    const obj = this.objects[key];
    if (!obj) return null;
    const slice = obj.slice(offset, length === undefined ? undefined : offset + length);
    return { arrayBuffer: async () => slice.buffer.slice(slice.byteOffset, slice.byteOffset + slice.byteLength) };
  }
}

class FakeKV {
  constructor(entries = {}) {
    this.entries = entries;
  }
  async get(key) {
    return key in this.entries ? this.entries[key] : null;
  }
}

class FakeCache {
  constructor() {
    this.store = new Map();
  }
  async match(req) {
    const hit = this.store.get(req.url);
    return hit ? hit.clone() : undefined;
  }
  async put(req, res) {
    this.store.set(req.url, res);
  }
}

function makeCtx() {
  const pending = [];
  return { waitUntil: (p) => pending.push(p), settle: () => Promise.all(pending) };
}

// ---------- Fixture

const TILE_BYTES = Uint8Array.from([0x1a, 0x05, 0x0a, 0x03, 0x6d, 0x76, 0x74]); // arbitrary MVT-ish payload
const OTHER_BYTES = Uint8Array.from([0x1a, 0x02, 0x0a, 0x00]);
const META = {
  vector_layers: [{ id: "roads", fields: { name: "String" } }],
  attribution: "© RuggedRoute test fixture",
};
const ARCHIVE = buildArchive({
  tiles: [
    { z: 2, x: 1, y: 1, data: TILE_BYTES },
    { z: 3, x: 5, y: 2, data: OTHER_BYTES },
  ],
  metadata: META,
  minZoom: 0,
  maxZoom: 8,
  bounds: [-104.05, 45.93, -96.55, 49.0],
});

function harness({ objects = { "roads.pmtiles": ARCHIVE }, aliases = {} } = {}) {
  const cache = new FakeCache();
  globalThis.caches = { default: cache };
  const env = { BUCKET: new FakeBucket(objects), ALIASES: new FakeKV(aliases) };
  const run = async (path, init) => {
    const ctx = makeCtx();
    const res = await worker.fetch(new Request(`https://tiles.example.test${path}`, init), env, ctx);
    await ctx.settle();
    return res;
  };
  return { env, cache, run };
}

// ---------- Tests

test("tile route serves the tile bytes with MVT headers and the resolved version", async () => {
  const { run } = harness();
  const res = await run("/roads/2/1/1.mvt");
  assert.equal(res.status, 200);
  assert.equal(res.headers.get("Content-Type"), "application/vnd.mapbox-vector-tile");
  assert.equal(res.headers.get("Cache-Control"), "public, max-age=86400");
  assert.equal(res.headers.get("Access-Control-Allow-Origin"), "*");
  assert.equal(res.headers.get("X-RR-Version"), "roads.pmtiles");
  assert.deepEqual(new Uint8Array(await res.arrayBuffer()), TILE_BYTES);
});

test("tile route distinguishes tiles by z/x/y", async () => {
  const { run } = harness();
  const res = await run("/roads/3/5/2.mvt");
  assert.equal(res.status, 200);
  assert.deepEqual(new Uint8Array(await res.arrayBuffer()), OTHER_BYTES);
});

test("a tile absent from the archive returns 204 with CORS and no body", async () => {
  const { run } = harness();
  const res = await run("/roads/2/0/0.mvt");
  assert.equal(res.status, 204);
  assert.equal(res.headers.get("Access-Control-Allow-Origin"), "*");
  assert.equal((await res.arrayBuffer()).byteLength, 0);
});

test("TileJSON route reports header bounds, zooms, metadata and the tile URL template", async () => {
  const { run } = harness();
  const res = await run("/roads.json");
  assert.equal(res.status, 200);
  assert.equal(res.headers.get("Content-Type"), "application/json");
  assert.equal(res.headers.get("Cache-Control"), "public, max-age=3600");
  const body = await res.json();
  assert.equal(body.tilejson, "3.0.0");
  assert.equal(body.name, "roads");
  assert.deepEqual(body.tiles, ["https://tiles.example.test/roads/{z}/{x}/{y}.mvt"]);
  assert.equal(body.minzoom, 0);
  assert.equal(body.maxzoom, 8);
  assert.deepEqual(body.bounds, [-104.05, 45.93, -96.55, 49]);
  assert.deepEqual(body.vector_layers, META.vector_layers);
  assert.equal(body.attribution, META.attribution);
  assert.equal(body.version, "roads.pmtiles");
});

test("KV alias resolves the layer to a versioned R2 key", async () => {
  const { env, run } = harness({
    objects: { "roads-v20261013.pmtiles": ARCHIVE },
    aliases: { "layer-alias:roads": "roads-v20261013.pmtiles" },
  });
  const res = await run("/roads/2/1/1.mvt");
  assert.equal(res.status, 200);
  assert.equal(res.headers.get("X-RR-Version"), "roads-v20261013.pmtiles");
  assert.ok(env.BUCKET.gets.every(([key]) => key === "roads-v20261013.pmtiles"));
  const json = await run("/roads.json");
  assert.equal((await json.json()).version, "roads-v20261013.pmtiles");
});

test("second request is served from the edge cache without touching R2", async () => {
  const { env, cache, run } = harness();
  const first = await run("/roads/2/1/1.mvt");
  assert.equal(first.status, 200);
  assert.equal(cache.store.size, 1);
  const before = env.BUCKET.gets.length;
  assert.ok(before > 0);
  const second = await run("/roads/2/1/1.mvt");
  assert.equal(second.status, 200);
  assert.deepEqual(new Uint8Array(await second.arrayBuffer()), TILE_BYTES);
  assert.equal(env.BUCKET.gets.length, before, "cache hit must not read R2");
});

test("an alias flip changes the cache key, so the new version is fetched instead of the stale entry", async () => {
  const { env, cache, run } = harness({
    objects: { "roads-v1.pmtiles": ARCHIVE, "roads-v2.pmtiles": ARCHIVE },
    aliases: { "layer-alias:roads": "roads-v1.pmtiles" },
  });
  await run("/roads/2/1/1.mvt");
  env.ALIASES.entries["layer-alias:roads"] = "roads-v2.pmtiles";
  const before = env.BUCKET.gets.length;
  const res = await run("/roads/2/1/1.mvt");
  assert.equal(res.headers.get("X-RR-Version"), "roads-v2.pmtiles");
  assert.ok(env.BUCKET.gets.length > before, "new version must miss the cache and read R2");
  assert.ok(env.BUCKET.gets.slice(before).every(([key]) => key === "roads-v2.pmtiles"));
  assert.equal(cache.store.size, 2);
  assert.ok([...cache.store.keys()].some((k) => k.includes("roads-v1.pmtiles")));
  assert.ok([...cache.store.keys()].some((k) => k.includes("roads-v2.pmtiles")));
});

test("a layer whose R2 object is missing returns 404 'layer unavailable' with CORS", async () => {
  const { run } = harness({ objects: {} });
  const res = await run("/ghost/2/1/1.mvt");
  assert.equal(res.status, 404);
  assert.equal(res.headers.get("Access-Control-Allow-Origin"), "*");
  assert.match(await res.text(), /^layer unavailable: /);
});

test("paths that match neither route return 404", async () => {
  const { env, run } = harness();
  for (const path of ["/", "/roads", "/roads/2/1/1.png", "/Roads/2/1/1.mvt", "/roads/2/1.mvt", "/roads.json/extra"]) {
    const res = await run(path);
    assert.equal(res.status, 404, path);
    assert.equal(await res.text(), "not found", path);
  }
  assert.equal(env.BUCKET.gets.length, 0, "no R2 read for unroutable paths");
});

test("non-GET methods are rejected with 405", async () => {
  const { run } = harness();
  for (const method of ["POST", "PUT", "DELETE"]) {
    const res = await run("/roads/2/1/1.mvt", { method });
    assert.equal(res.status, 405, method);
  }
});

test("OPTIONS preflight answers with the CORS headers", async () => {
  const { run } = harness();
  const res = await run("/roads/2/1/1.mvt", { method: "OPTIONS" });
  assert.equal(res.status, 200);
  assert.equal(res.headers.get("Access-Control-Allow-Origin"), "*");
  assert.equal(res.headers.get("Access-Control-Allow-Methods"), "GET, HEAD, OPTIONS");
  assert.equal((await res.arrayBuffer()).byteLength, 0);
});
