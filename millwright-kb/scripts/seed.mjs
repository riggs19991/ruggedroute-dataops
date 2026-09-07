// Pushes content/ to the database through the token-gated mw_import_content RPC.
//   SEED_TOKEN=... node scripts/seed.mjs            (uses VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY from .env or env)
//   node scripts/seed.mjs --out payload.json         (just write the payload, e.g. to post with curl)
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'
import { loadContent, root } from './content.mjs'

function loadDotEnv() {
  const p = join(root, '.env')
  if (!existsSync(p)) return
  for (const line of readFileSync(p, 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/)
    if (m && !(m[1] in process.env)) process.env[m[1]] = m[2].replace(/^["']|["']$/g, '')
  }
}
loadDotEnv()

const payload = loadContent()
const outIdx = process.argv.indexOf('--out')
if (outIdx !== -1) {
  writeFileSync(process.argv[outIdx + 1], JSON.stringify({ payload, token: process.env.SEED_TOKEN ?? '' }))
  console.log(`wrote payload: ${payload.categories.length} categories, ${payload.articles.length} articles`)
  process.exit(0)
}

const url = process.env.VITE_SUPABASE_URL
const key = process.env.VITE_SUPABASE_ANON_KEY
const token = process.env.SEED_TOKEN
if (!url || !key || !token) {
  console.error('need VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY and SEED_TOKEN')
  process.exit(1)
}
const res = await fetch(`${url}/rest/v1/rpc/mw_import_content`, {
  method: 'POST',
  headers: { apikey: key, Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ payload, token }),
})
const text = await res.text()
if (!res.ok) { console.error(res.status, text); process.exit(1) }
console.log('imported', text)
