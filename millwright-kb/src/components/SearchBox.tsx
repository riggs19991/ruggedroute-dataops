import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

export function SearchBox({ big = false, autoFocus = false }: { big?: boolean; autoFocus?: boolean }) {
  const [params] = useSearchParams()
  const [q, setQ] = useState(params.get('q') ?? '')
  const navigate = useNavigate()

  useEffect(() => { setQ(params.get('q') ?? '') }, [params])

  function submit(e: FormEvent) {
    e.preventDefault()
    const query = q.trim()
    if (!query) return
    const cat = params.get('cat')
    navigate(`/search?q=${encodeURIComponent(query)}${cat ? `&cat=${encodeURIComponent(cat)}` : ''}`)
  }

  return (
    <form className={`searchbox${big ? ' big' : ''}`} onSubmit={submit} role="search">
      <input
        type="search"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search: shaft alignment, SKF taper bearing, Victor tip chart, TA4207H…"
        aria-label="Search the knowledge base"
        autoFocus={autoFocus}
      />
      <button type="submit">Search</button>
    </form>
  )
}
