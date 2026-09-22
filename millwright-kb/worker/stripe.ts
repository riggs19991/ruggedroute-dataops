// Minimal Stripe Checkout client for the Worker: plain fetch to the REST API, no SDK.
// STRIPE_MOCK=1 (wrangler dev) fakes a paid session so the flow can be exercised without an account.
export type Session = { id: string; url: string | null; payment_status: string; amount_total: number | null; currency: string | null; status: string | null }

export interface StripeEnv { STRIPE_SECRET_KEY?: string; STRIPE_MOCK?: string }

const API = 'https://api.stripe.com/v1'

async function call(env: StripeEnv, path: string, body?: URLSearchParams): Promise<Session> {
  const r = await fetch(API + path, {
    method: body ? 'POST' : 'GET',
    headers: { Authorization: 'Basic ' + btoa(env.STRIPE_SECRET_KEY + ':'), ...(body ? { 'Content-Type': 'application/x-www-form-urlencoded' } : {}) },
    body,
  })
  const json = (await r.json()) as Session & { error?: { message?: string } }
  if (!r.ok) throw new Error(json.error?.message || `stripe ${r.status}`)
  return json
}

export async function createCheckout(env: StripeEnv, amountCents: number, site: string): Promise<Session> {
  const success = `${site}/support/thanks?session_id={CHECKOUT_SESSION_ID}`
  if (env.STRIPE_MOCK) {
    const id = `cs_mock_${amountCents}_${crypto.randomUUID().slice(0, 8)}`
    return { id, url: success.replace('{CHECKOUT_SESSION_ID}', id), payment_status: 'paid', amount_total: amountCents, currency: 'usd', status: 'complete' }
  }
  const p = new URLSearchParams()
  p.set('mode', 'payment')
  p.set('submit_type', 'donate')
  p.set('success_url', success)
  p.set('cancel_url', `${site}/support`)
  p.set('line_items[0][quantity]', '1')
  p.set('line_items[0][price_data][currency]', 'usd')
  p.set('line_items[0][price_data][unit_amount]', String(amountCents))
  p.set('line_items[0][price_data][product_data][name]', 'Support Millwright KB')
  p.set('line_items[0][price_data][product_data][description]', 'A gift to keep the knowledge base free, ad-free and growing')
  p.set('metadata[source]', 'millwright-kb')
  return call(env, '/checkout/sessions', p)
}

export async function retrieveCheckout(env: StripeEnv, id: string): Promise<Session> {
  if (env.STRIPE_MOCK) {
    const m = /^cs_mock_(\d+)_/.exec(id)
    if (!m) throw new Error('unknown mock session')
    return { id, url: null, payment_status: 'paid', amount_total: Number(m[1]), currency: 'usd', status: 'complete' }
  }
  if (!/^cs_[A-Za-z0-9_]+$/.test(id)) throw new Error('bad session id')
  return call(env, `/checkout/sessions/${id}`)
}
