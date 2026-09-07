import { useState } from 'react'
import { deleteFile, signedUrl } from '../lib/files'
import { formatBytes, type FileRow } from '../lib/types'

function icon(mime: string): string {
  if (mime.includes('pdf')) return '📄'
  if (mime.startsWith('image/')) return '🖼️'
  if (mime.startsWith('video/')) return '🎬'
  if (mime.includes('word') || mime.includes('document')) return '📝'
  if (mime.includes('sheet') || mime.includes('excel')) return '📊'
  return '📎'
}

export function FileList({ files, canDelete = false, onDeleted }: { files: FileRow[]; canDelete?: boolean; onDeleted?: (id: string) => void }) {
  const [busy, setBusy] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  if (!files.length) return null

  async function open(f: FileRow) {
    setBusy(f.id); setError(null)
    try {
      const url = await signedUrl(f.path)
      window.open(url, '_blank', 'noopener')
    } catch (e) {
      setError((e as Error).message || 'Could not open file. Are you signed in?')
    } finally { setBusy(null) }
  }

  async function remove(f: FileRow) {
    if (!confirm(`Delete ${f.filename}?`)) return
    setBusy(f.id)
    try { await deleteFile(f); onDeleted?.(f.id) } catch (e) { setError((e as Error).message) } finally { setBusy(null) }
  }

  return (
    <div className="files">
      <h3>Attachments</h3>
      {error && <div className="notice error">{error}</div>}
      {files.map((f) => (
        <div className="file-row" key={f.id}>
          <span>{icon(f.mime_type)}</span>
          <span className="name" title={f.filename}>{f.filename}</span>
          <span className="size">{formatBytes(f.size_bytes)}</span>
          <button type="button" className="btn small" disabled={busy === f.id} onClick={() => open(f)}>Open</button>
          {canDelete && <button type="button" className="btn small danger" disabled={busy === f.id} onClick={() => remove(f)}>Delete</button>}
        </div>
      ))}
      <p className="hint small muted">You need to be signed in to open attachments.</p>
    </div>
  )
}
