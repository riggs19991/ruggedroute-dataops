import { useRef } from 'react'
import { formatBytes } from '../lib/types'

const ACCEPT = 'image/*,application/pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.md'

/** Two ways in: the camera (phones) or the file chooser. Large photos are shrunk on upload. */
export function FilePicker({ files, onChange, label = 'Attachments' }: { files: File[]; onChange: (files: File[]) => void; label?: string }) {
  const camera = useRef<HTMLInputElement>(null)
  const chooser = useRef<HTMLInputElement>(null)
  const add = (list: FileList | null) => { if (list?.length) onChange([...files, ...Array.from(list)]) }
  return (
    <div className="field">
      <label>{label} <span className="muted">(photos, PDF, documents; 50 MB each)</span></label>
      <div className="btn-row">
        <button type="button" className="btn small" onClick={() => camera.current?.click()}>📷 Take a photo</button>
        <button type="button" className="btn small" onClick={() => chooser.current?.click()}>📎 Choose files</button>
      </div>
      <input ref={camera} type="file" accept="image/*" capture="environment" hidden onChange={(e) => { add(e.target.files); e.target.value = '' }} />
      <input ref={chooser} type="file" accept={ACCEPT} multiple hidden onChange={(e) => { add(e.target.files); e.target.value = '' }} />
      {files.length > 0 && (
        <ul className="picked-files">
          {files.map((f, i) => (
            <li key={i}><span className="name">{f.name}</span> <span className="size">{formatBytes(f.size)}</span> <button type="button" className="linklike" onClick={() => onChange(files.filter((_, k) => k !== i))}>remove</button></li>
          ))}
        </ul>
      )}
    </div>
  )
}
