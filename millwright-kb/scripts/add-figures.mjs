// Inserts figure references from figures.json into the markdown articles (idempotent).
// figures.json: { "<slug>": [ { "img": "welding/x.svg", "alt": "...", "after": "## Heading" | "top" } ] }
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { globSync } from 'node:fs'
const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const manifest = JSON.parse(readFileSync(join(root, 'scripts', 'figures.json'), 'utf8'))
const credits = existsSync(join(root, 'public', 'photos', 'credits.json')) ? JSON.parse(readFileSync(join(root, 'public', 'photos', 'credits.json'), 'utf8')) : {}
const files = Object.fromEntries(globSync('content/*/*.md', { cwd: root }).map((f) => [f.replace(/^.*\//, '').replace(/\.md$/, ''), join(root, f)]))
let inserted = 0, skipped = 0, missing = []
for (const [slug, figs] of Object.entries(manifest)) {
  const file = files[slug]
  if (!file) { missing.push('article:' + slug); continue }
  let md = readFileSync(file, 'utf8')
  for (const f of figs) {
    const isPhoto = !!f.photo
    const src = isPhoto ? `/photos/${f.photo}` : `/img/${f.img}`
    if (!existsSync(join(root, 'public', isPhoto ? 'photos' : 'img', isPhoto ? f.photo : f.img))) { missing.push('image:' + (f.photo || f.img)); continue }
    const ref = `![${f.alt}](${src})`
    if (md.includes(`(${src})`)) { skipped++; continue }
    let cap = f.alt
    if (isPhoto) { const c = credits[f.photo]; if (!c) { missing.push('credit:' + f.photo); continue } cap = `${f.alt}. Photo: ${c.author || 'unknown'}, ${c.license}, via ${String(c.source).replace(/^openverse:/, '')}` }
    const block = `\n${ref}\n\n*${cap}*\n`
    const lines = md.split('\n')
    let idx = -1
    if (f.after === 'top' || !f.after) {
      // after the front matter and any leading blockquote/intro: before the first "## " heading
      idx = lines.findIndex((l, i) => i > 2 && l.startsWith('## '))
      if (idx === -1) idx = lines.length
      lines.splice(idx, 0, block)
    } else {
      const h = lines.findIndex((l) => l.trim().toLowerCase().startsWith(f.after.trim().toLowerCase()))
      if (h === -1) { missing.push(`heading:${slug}:${f.after}`); continue }
      // insert after the heading and its first paragraph/blockquote (so the figure follows the intro line)
      let j = h + 1
      while (j < lines.length && lines[j].trim() === '') j++
      if (j < lines.length && !lines[j].startsWith('|') && !lines[j].startsWith('#') && !/^\d+\./.test(lines[j]) && !lines[j].startsWith('- ') && !lines[j].startsWith('```')) {
        while (j < lines.length && lines[j].trim() !== '') j++
      } else j = h + 1
      lines.splice(j, 0, block)
    }
    md = lines.join('\n').replace(/\n{3,}/g, '\n\n')
    inserted++
  }
  writeFileSync(file, md)
}
console.log(`figures inserted: ${inserted}, already present: ${skipped}`)
if (missing.length) { console.log('MISSING:\n' + missing.join('\n')); process.exitCode = 1 }
