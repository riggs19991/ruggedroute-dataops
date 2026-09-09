// Fetch a list of chosen candidates. Usage: node scripts/photos/pick.mjs picks.json
// picks.json: [{ "cands": "path/to/key.json", "i": 3, "rel": "welding/smaw-arc", "crop": [x,y,w,h] }]
import { readFileSync } from 'node:fs'
import { fetchPhoto } from './fetch.mjs'
const picks = JSON.parse(readFileSync(process.argv[2], 'utf8'))
for (const p of picks) {
  const cand = JSON.parse(readFileSync(p.cands, 'utf8'))[p.i]
  try { const out = await fetchPhoto(cand, p.rel, { crop: p.crop }); console.log('ok', p.rel, '|', cand.license, '|', (cand.author || '').slice(0, 30)) }
  catch (e) { console.log('FAIL', p.rel, e.message) }
}
