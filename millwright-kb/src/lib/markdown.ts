import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { figureUrl } from './site'

marked.setOptions({ gfm: true, breaks: false })
// Diagram and photo sources get the build id appended (see figureUrl), everything else is untouched.
marked.use({ renderer: { image({ href, title, text }) { const t = title ? ` title="${title.replace(/"/g, '&quot;')}"` : ''; return `<img src="${figureUrl(href)}" alt="${text.replace(/"/g, '&quot;')}"${t}>` } } })

/** Markdown -> sanitized HTML. Safe to inject with dangerouslySetInnerHTML. */
export function renderMarkdown(md: string): string {
  const html = marked.parse(md ?? '', { async: false }) as string
  return DOMPurify.sanitize(html, { ADD_ATTR: ['target'] })
}

/** For search headlines that already contain <mark> tags from Postgres. */
export function sanitizeInline(html: string): string {
  return DOMPurify.sanitize(html ?? '', { ALLOWED_TAGS: ['mark', 'b', 'strong', 'em'] })
}
