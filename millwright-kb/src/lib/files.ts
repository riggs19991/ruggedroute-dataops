import { supabase, FILES_BUCKET } from './supabase'
import type { FileRow } from './types'

export const MAX_FILE_BYTES = 50 * 1024 * 1024

function safeName(name: string): string {
  return name.replace(/[^A-Za-z0-9._-]+/g, '_').slice(0, 120)
}

/** Uploads to the user's own folder in the bucket. Returns the storage path. */
export async function uploadFile(userId: string, file: File): Promise<Omit<FileRow, 'id' | 'created_at' | 'article_id' | 'group_post_id'>> {
  if (file.size > MAX_FILE_BYTES) throw new Error(`${file.name} is over the 50 MB limit`)
  const path = `${userId}/${crypto.randomUUID()}-${safeName(file.name)}`
  const { error } = await supabase.storage.from(FILES_BUCKET).upload(path, file, {
    contentType: file.type || 'application/octet-stream',
    upsert: false,
  })
  if (error) throw error
  return {
    uploader_id: userId,
    bucket: FILES_BUCKET,
    path,
    filename: file.name,
    mime_type: file.type || 'application/octet-stream',
    size_bytes: file.size,
  }
}

export async function signedUrl(path: string): Promise<string> {
  const { data, error } = await supabase.storage.from(FILES_BUCKET).createSignedUrl(path, 60 * 60)
  if (error) throw error
  return data.signedUrl
}

export async function deleteFile(row: FileRow): Promise<void> {
  await supabase.storage.from(FILES_BUCKET).remove([row.path])
  const { error } = await supabase.from('mw_files').delete().eq('id', row.id)
  if (error) throw error
}
