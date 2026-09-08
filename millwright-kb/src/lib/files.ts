import { supabase, FILES_BUCKET } from './supabase'
import type { FileRow } from './types'

export const MAX_FILE_BYTES = 50 * 1024 * 1024

function safeName(name: string): string {
  return name.replace(/[^A-Za-z0-9._-]+/g, '_').slice(0, 120)
}

const MAX_IMAGE_PX = 2000
const MAX_IMAGE_BYTES = 4 * 1024 * 1024

/**
 * Phone photos are 4-12 MB. Shrink big images (longest side 2,000 px, JPEG 0.85) on a canvas
 * before upload so they go quickly on mobile data. PDFs and documents pass through untouched;
 * anything the browser cannot decode (HEIC on some devices) also passes through.
 */
export async function prepareForUpload(file: File): Promise<File> {
  if (!file.type.startsWith('image/') || file.type === 'image/svg+xml' || file.type === 'image/gif') return file
  const bmp = await createImageBitmap(file).catch(() => null)
  if (!bmp) return file
  const big = Math.max(bmp.width, bmp.height)
  if (big <= MAX_IMAGE_PX && file.size <= MAX_IMAGE_BYTES) { bmp.close(); return file }
  const scale = Math.min(1, MAX_IMAGE_PX / big)
  const canvas = document.createElement('canvas')
  canvas.width = Math.round(bmp.width * scale); canvas.height = Math.round(bmp.height * scale)
  canvas.getContext('2d')!.drawImage(bmp, 0, 0, canvas.width, canvas.height)
  bmp.close()
  const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.85))
  if (!blob || blob.size >= file.size) return file
  const name = file.name.replace(/\.[^.]+$/, '') + '.jpg'
  return new File([blob], name, { type: 'image/jpeg', lastModified: file.lastModified })
}

/** Uploads to the user's own folder in the bucket (shrinking large photos first). Returns the storage path. */
export async function uploadFile(userId: string, original: File): Promise<Omit<FileRow, 'id' | 'created_at' | 'article_id' | 'group_post_id'>> {
  const file = await prepareForUpload(original)
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
