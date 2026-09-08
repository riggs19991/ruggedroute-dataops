export interface Profile {
  id: string
  display_name: string
  is_admin: boolean
  school: string
}

export interface Category {
  id: string
  slug: string
  name: string
  description: string
  icon: string
  sort_order: number
}

export type ArticleKind = 'procedure' | 'reference' | 'chart' | 'manual' | 'tip' | 'safety'
export type ArticleStatus = 'draft' | 'pending' | 'published' | 'rejected'

export const KINDS: { value: ArticleKind; label: string }[] = [
  { value: 'procedure', label: 'Procedure (step by step)' },
  { value: 'reference', label: 'Reference / explanation' },
  { value: 'chart', label: 'Chart / table' },
  { value: 'manual', label: 'Manufacturer manual' },
  { value: 'tip', label: 'Tip / shop trick' },
  { value: 'safety', label: 'Safety' },
]

export interface Article {
  id: string
  slug: string
  title: string
  summary: string
  body: string
  kind: ArticleKind
  category_id: string | null
  tags: string[]
  manufacturer: string
  model_numbers: string[]
  source: string
  author_id: string | null
  status: ArticleStatus
  review_note: string
  group_id: string | null
  view_count: number
  upvotes: number
  created_at: string
  updated_at: string
  category?: Category | null
  author?: Pick<Profile, 'display_name'> | null
}

export interface SearchHit {
  id: string
  slug: string
  title: string
  summary: string
  kind: ArticleKind
  tags: string[]
  manufacturer: string
  category_slug: string | null
  category_name: string | null
  rank: number
  headline: string
  upvotes: number
}

export interface FileRow {
  id: string
  article_id: string | null
  group_post_id: string | null
  uploader_id: string | null
  bucket: string
  path: string
  filename: string
  mime_type: string
  size_bytes: number
  created_at: string
}

export interface Group {
  id: string
  name: string
  school: string
  teacher_id: string
  join_code: string
  term_start: string | null
  created_at: string
  teacher?: Pick<Profile, 'display_name'> | null
}

export interface GroupPost {
  id: string
  group_id: string
  week_number: number
  title: string
  body: string
  article_id: string | null
  posted_by: string | null
  pinned: boolean
  created_at: string
  article?: Pick<Article, 'slug' | 'title'> | null
  files?: FileRow[]
}

export function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`
  return `${(n / (1024 * 1024)).toFixed(1)} MB`
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

/** Week number of a term given its start date (1-based). Null if no start date. */
export function currentWeek(termStart: string | null): number | null {
  if (!termStart) return null
  const start = new Date(termStart + 'T00:00:00')
  const days = Math.floor((Date.now() - start.getTime()) / 86400000)
  return Math.max(1, Math.floor(days / 7) + 1)
}
