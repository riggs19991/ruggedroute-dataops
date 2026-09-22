// Millwright KB Worker: static assets for the site plus the donation API used by the supporters
// wall. Everything under /api/* runs here (wrangler.toml run_worker_first); the rest is dist/.
import { checkDisplayName } from '../src/lib/moderation'
import { createCheckout, retrieveCheckout, type StripeEnv } from './stripe'

export interface Env extends StripeEnv {
  ASSETS: Fetcher
  SUPABASE_URL: string
  SUPABASE_ANON_KEY: string
  DONATION_TOKEN?: string
}

const MIN_CENTS = 100
const MAX_CENTS = 1_000_000
const ALLOWED_ORIGINS = ['https://localhost', 'capacitor://localhost', 'http://localhost']

function cors(req: Request): Record<string, string> {
  const origin = req.headers.get('Origin') || ''
  const self = new URL(req.url).origin
  const ok = origin === self || ALLOWED_ORIGINS.includes(origin) || /^http:\/\/localhost:\d+$/.test(origin)
  return ok ? { 'Access-Control-Allow-Origin': origin, 'Access-Control-Allow-Methods': 'GET,POST,OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', Vary: 'Origin' } : {}
}
const json = (req: Request, status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', ...cors(req) } })

async function rpc<T>(env: Env, fn: string, args: Record<string, unknown>): Promise<T> {
  const r = await fetch(`${env.SUPABASE_URL}/rest/v1/rpc/${fn}`, {
    method: 'POST',
    headers: { apikey: env.SUPABASE_ANON_KEY, Authorization: `Bearer ${env.SUPABASE_ANON_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  })
  const body = (await r.json()) as T & { message?: string }
  if (!r.ok) throw new Error(body?.message || `supabase ${r.status}`)
  return body
}

type Donation = { id: string; amount_cents: number; currency: string; display_mode: string; display_name: string; created_at: string }

async function readBody(req: Request): Promise<Record<string, unknown>> {
  try { const b = await req.json(); return b && typeof b === 'object' ? (b as Record<string, unknown>) : {} } catch { return {} }
}

async function handleApi(req: Request, env: Env, url: URL): Promise<Response> {
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(req) })
  const configured = !!(env.STRIPE_SECRET_KEY || env.STRIPE_MOCK) && !!env.DONATION_TOKEN

  if (url.pathname === '/api/donate/status' && req.method === 'GET') return json(req, 200, { configured })
  if (req.method !== 'POST') return json(req, 405, { error: 'method' })
  if (!configured) return json(req, 503, { error: 'not-configured' })
  const body = await readBody(req)

  if (url.pathname === '/api/donate/checkout') {
    const cents = Math.round(Number(body.amount_cents))
    if (!Number.isFinite(cents) || cents < MIN_CENTS || cents > MAX_CENTS) return json(req, 400, { error: 'amount' })
    try {
      const s = await createCheckout(env, cents, url.origin)
      return json(req, 200, { url: s.url, session_id: s.id })
    } catch (e) { return json(req, 502, { error: (e as Error).message }) }
  }

  if (url.pathname === '/api/donate/confirm') {
    const id = String(body.session_id || '')
    if (!id) return json(req, 400, { error: 'session' })
    try {
      const s = await retrieveCheckout(env, id)
      if (s.payment_status !== 'paid' || !s.amount_total) return json(req, 402, { error: 'unpaid' })
      const d = await rpc<Donation>(env, 'mw_record_donation', { p_token: env.DONATION_TOKEN, p_session: s.id, p_amount_cents: s.amount_total, p_currency: s.currency || 'usd' })
      return json(req, 200, d)
    } catch (e) { return json(req, 502, { error: (e as Error).message }) }
  }

  if (url.pathname === '/api/donate/display') {
    const id = String(body.session_id || '')
    const mode = String(body.mode || 'anonymous')
    if (!id) return json(req, 400, { error: 'session' })
    if (!['anonymous', 'name', 'business', 'profile'].includes(mode)) return json(req, 400, { error: 'mode' })
    let name = ''
    if (mode !== 'anonymous') {
      const check = checkDisplayName(String(body.name || ''))
      if (!check.ok) return json(req, 422, { error: 'name', reason: check.reason })
      name = check.label
    }
    try {
      const d = await rpc<Donation>(env, 'mw_set_donation_display', { p_token: env.DONATION_TOKEN, p_session: id, p_mode: mode, p_name: name })
      return json(req, 200, d)
    } catch (e) { return json(req, 502, { error: (e as Error).message }) }
  }

  return json(req, 404, { error: 'not-found' })
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url)
    if (url.pathname.startsWith('/api/')) return handleApi(req, env, url)
    return env.ASSETS.fetch(req)
  },
} satisfies ExportedHandler<Env>
