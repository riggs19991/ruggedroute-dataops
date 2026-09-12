import { markSvg } from '../brand/mark.mjs'

/** The Millwright KB mark (see src/brand/mark.mjs). `field` is the colour behind it: it edges the wrench. */
export function Logo({ size = 36, field = 'var(--brand)' }: { size?: number; field?: string }) {
  return <span aria-hidden="true" style={{ display: 'block', flex: 'none', width: size, height: size }} dangerouslySetInnerHTML={{ __html: markSvg({ size, id: 'mark', navy: field }) }} />
}
