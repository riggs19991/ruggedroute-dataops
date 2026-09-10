import { Link } from 'react-router-dom'
import type { Article, SearchHit } from '../lib/types'
import { sanitizeInline } from '../lib/markdown'

type Item = Pick<Article, 'slug' | 'title' | 'summary' | 'kind' | 'tags' | 'manufacturer'> & {
  category_name?: string | null
  headline?: string
  status?: Article['status']
  upvotes?: number
  author_id?: string | null
}

export function ArticleCard({ item }: { item: Item | SearchHit }) {
  const categoryName = 'category_name' in item ? item.category_name : undefined
  const headline = 'headline' in item ? item.headline : undefined
  const status = 'status' in item ? item.status : undefined
  const upvotes = 'upvotes' in item ? item.upvotes ?? 0 : 0
  const community = 'author_id' in item && !!item.author_id
  return (
    <Link to={`/article/${item.slug}`} className="card result">
      <h3>{item.title}</h3>
      <div className="meta">
        <span className={`badge ${item.kind}`}>{item.kind}</span>
        {status && status !== 'published' && <span className={`badge ${status}`}>{status}</span>}
        {categoryName && <span>{categoryName}</span>}
        {item.manufacturer && <span>{item.manufacturer}</span>}
        {community && <span className="badge community">community</span>}
        {upvotes > 0 && <span className="votes">▲ {upvotes}</span>}
      </div>
      {headline
        ? <p className="snippet" dangerouslySetInnerHTML={{ __html: sanitizeInline(headline) }} />
        : item.summary && <p className="snippet">{item.summary}</p>}
    </Link>
  )
}
