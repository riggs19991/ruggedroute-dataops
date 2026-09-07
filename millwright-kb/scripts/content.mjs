// Loads content/categories.json and content/**/*.md into a plain payload
// { categories: [...], articles: [...] } used by seed.mjs and build-seed.mjs.
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import matter from 'gray-matter'

export const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const contentDir = join(root, 'content')

function walk(dir) {
  const files = []
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) files.push(...walk(p))
    else if (name.endsWith('.md')) files.push(p)
  }
  return files.sort()
}

export function loadContent() {
  const categories = JSON.parse(readFileSync(join(contentDir, 'categories.json'), 'utf8'))
  const slugs = new Set()
  const articles = []
  for (const file of walk(contentDir)) {
    const { data, content } = matter(readFileSync(file, 'utf8'))
    for (const k of ['title', 'slug', 'category']) if (!data[k]) throw new Error(`${file}: missing ${k}`)
    if (slugs.has(data.slug)) throw new Error(`duplicate slug ${data.slug}`)
    slugs.add(data.slug)
    if (!categories.find((c) => c.slug === data.category)) throw new Error(`${file}: unknown category ${data.category}`)
    articles.push({
      slug: data.slug,
      title: data.title,
      summary: data.summary ?? '',
      body: content.trim(),
      kind: data.kind ?? 'procedure',
      category: data.category,
      tags: data.tags ?? [],
      manufacturer: data.manufacturer ?? '',
      model_numbers: (data.model_numbers ?? []).map(String),
      source: data.source ?? '',
    })
  }
  return { categories, articles }
}
