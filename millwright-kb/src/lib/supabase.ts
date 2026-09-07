import { createClient } from '@supabase/supabase-js'

// Publishable (anon) keys are designed to ship in browser bundles; row-level security does
// the real access control. Override with VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY in .env
// to point the app at a different project.
const DEFAULT_URL = 'https://tzucpijgyjhpgwukjsau.supabase.co'
const DEFAULT_KEY = 'sb_publishable_qgSQd92ZSLnHIgGToevHuA_x8PVlxNP'

const url = (import.meta.env.VITE_SUPABASE_URL as string | undefined) || DEFAULT_URL
const key = (import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined) || DEFAULT_KEY

export const supabase = createClient(url, key)
export const FILES_BUCKET = 'mw-files'
