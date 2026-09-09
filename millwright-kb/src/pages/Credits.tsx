import { figureUrl } from '../lib/site'
import { useEffect, useState } from 'react'

type Credit = { title: string; author: string; license: string; licenseUrl: string; source: string; sourceUrl: string }

/** Attribution for every photograph used in the knowledge base (public/photos/credits.json). */
export function CreditsPage() {
  const [credits, setCredits] = useState<Record<string, Credit> | null>(null)
  useEffect(() => { fetch(figureUrl('/photos/credits.json')).then((r) => r.json()).then(setCredits).catch(() => setCredits({})) }, [])
  const entries = Object.entries(credits ?? {}).sort((a, b) => a[0].localeCompare(b[0]))
  return (
    <div className="md" style={{ maxWidth: 820 }}>
      <h1>Photo credits</h1>
      <p>The diagrams in this app are drawn for it. The photographs come from free-licensed sources (public domain, CC0, CC BY and CC BY-SA), and each is credited here and in its caption. Licence texts: <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">CC BY</a>, <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener noreferrer">CC BY-SA</a>. Photos have been cropped and resized.</p>
      {credits === null ? <p className="loading">Loading…</p> : entries.length === 0 ? <p className="muted">No photographs yet.</p> : (
        <ul>
          {entries.map(([file, c]) => (
            <li key={file}><a href={`/photos/${file}`} target="_blank" rel="noopener noreferrer">{c.title || file}</a> by {c.author || 'unknown'}, <a href={c.licenseUrl || '#'} target="_blank" rel="noopener noreferrer">{c.license}</a>, via <a href={c.sourceUrl} target="_blank" rel="noopener noreferrer">{c.source.replace(/^openverse:/, '')}</a></li>
          ))}
        </ul>
      )}
    </div>
  )
}
