// Generates every diagram into public/img and prints a count. Usage: node scripts/diagrams/run.mjs [module ...]
import { readdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { registry } from './lib.mjs'
const here = dirname(fileURLToPath(import.meta.url))
const only = process.argv.slice(2)
const mods = readdirSync(here).filter((f) => f.endsWith('.mjs') && !['lib.mjs', 'run.mjs'].includes(f)).filter((f) => !only.length || only.includes(f.replace(/\.mjs$/, '')))
for (const m of mods) await import(join(here, m))
console.log(`generated ${registry.length} diagrams from ${mods.length} modules`)
