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
      <div className="field-wrap">
        <input
          type="search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={big ? 'Search: 7018 amps, SKF 22220, belt tracking' : 'Search: shaft alignment, SKF 22220, 7018 amps'}
          aria-label="Search the knowledge base"
          autoFocus={autoFocus}
        />
      </div>
      <button type="submit" aria-label="Search">{big ? 'Search' : '🔍'}</button>
    </form>
  )
}
