import { useMemo, type MouseEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { renderMarkdown } from '../lib/markdown'

/** Renders sanitized markdown; internal links (/article/..., /category/...) navigate in-app. */
export function Markdown({ source, className = 'md' }: { source: string; className?: string }) {
  const html = useMemo(() => renderMarkdown(source), [source])
  const navigate = useNavigate()

  function onClick(e: MouseEvent<HTMLDivElement>) {
    const a = (e.target as HTMLElement).closest('a')
    if (!a) return
    const href = a.getAttribute('href') ?? ''
    if (href.startsWith('/') && !e.metaKey && !e.ctrlKey) {
      e.preventDefault()
      navigate(href)
    } else if (/^https?:/.test(href)) {
      a.setAttribute('target', '_blank')
      a.setAttribute('rel', 'noopener')
    }
  }

  return <div className={className} onClick={onClick} dangerouslySetInnerHTML={{ __html: html }} />
}
