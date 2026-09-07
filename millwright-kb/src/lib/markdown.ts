import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({ gfm: true, breaks: false })

/** Markdown -> sanitized HTML. Safe to inject with dangerouslySetInnerHTML. */
export function renderMarkdown(md: string): string {
  const html = marked.parse(md ?? '', { async: false }) as string
  return DOMPurify.sanitize(html, { ADD_ATTR: ['target'] })
}

/** For search headlines that already contain <mark> tags from Postgres. */
export function sanitizeInline(html: string): string {
  return DOMPurify.sanitize(html ?? '', { ALLOWED_TAGS: ['mark', 'b', 'strong', 'em'] })
}
