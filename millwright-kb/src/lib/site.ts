// Site-wide constants. Change the donation link here (or set VITE_DONATE_URL at build time).
export const COMPANY = 'Addictive Media Productions LLC'
export const CONTACT_EMAIL = 'riggs1991@gmail.com'
export const COPYRIGHT_YEAR = 2026
/** External donation page (Ko-fi, Stripe payment link, PayPal…). Empty = send people to /support. */
export const DONATE_URL: string = (import.meta.env.VITE_DONATE_URL as string | undefined) ?? ''
export const donateHref = DONATE_URL || '/support'
