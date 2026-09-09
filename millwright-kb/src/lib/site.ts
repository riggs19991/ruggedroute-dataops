// Site-wide constants. Change the donation link here (or set VITE_DONATE_URL at build time).
export const COMPANY = 'Addictive Media Productions LLC'
export const CONTACT_EMAIL = 'riggs1991@gmail.com'
export const COMPANY_LOCATION = 'Blanchard, Bonner County, Idaho, USA'
export const GOVERNING_LAW = 'the State of Idaho'
export const COPYRIGHT_YEAR = 2026
/** External donation page (Ko-fi, Stripe payment link, PayPal…). Empty = send people to /support. */
export const DONATE_URL: string = (import.meta.env.VITE_DONATE_URL as string | undefined) || 'https://buy.stripe.com/3cI14n5O17Hbfor2J29k400'
export const donateHref = DONATE_URL || '/support'

/** Short build id baked in at build time (commit SHA on CI). */
export const BUILD_ID = __BUILD_ID__
/** Figure and photo URLs carry the build id so the offline cache never serves a stale drawing. */
export function figureUrl(path: string): string {
  return /^\/(img|photos)\//.test(path) && !path.includes('?') ? `${path}?v=${BUILD_ID}` : path
}
