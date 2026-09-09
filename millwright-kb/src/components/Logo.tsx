// The Millwright KB mark: an eight-tooth gear with an open-end wrench inside, amber on navy.
function gearPath(cx: number, cy: number, ro: number, ri: number, teeth: number): string {
  const pts: string[] = []
  const n = teeth * 4
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2
    const r = i % 4 === 0 || i % 4 === 1 ? ro : ri
    pts.push(`${(cx + r * Math.cos(a)).toFixed(2)},${(cy + r * Math.sin(a)).toFixed(2)}`)
  }
  return 'M' + pts.join(' L') + ' Z'
}
export const GEAR_PATH = gearPath(24, 24, 22, 17, 8)

export function Logo({ size = 36, amber = '#f4a11d', inner = 'var(--brand)' }: { size?: number; amber?: string; inner?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" aria-hidden="true" style={{ display: 'block', flex: 'none' }}>
      <path d={GEAR_PATH} fill={amber} />
      <circle cx="24" cy="24" r="13" fill={inner} />
      <path d="M14 34 L25 23" stroke={amber} strokeWidth="5" strokeLinecap="round" fill="none" />
      <path d="M23 15 a7 7 0 1 1 10 10" stroke={amber} strokeWidth="4.5" strokeLinecap="round" fill="none" />
    </svg>
  )
}

/** Standalone SVG markup (for icon generation and the static logo file). */
export function logoSvg(size: number, { bg = '#0f1b2d', amber = '#f4a11d', pad = 0.11, rounded = 0 }: { bg?: string; amber?: string; pad?: number; rounded?: number } = {}): string {
  const s = size, inset = s * pad, scale = (s - inset * 2) / 48
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}" viewBox="0 0 ${s} ${s}">` +
    `<rect width="${s}" height="${s}" rx="${rounded}" fill="${bg}"/>` +
    `<g transform="translate(${inset} ${inset}) scale(${scale})"><path d="${GEAR_PATH}" fill="${amber}"/><circle cx="24" cy="24" r="13" fill="${bg}"/>` +
    `<path d="M14 34 L25 23" stroke="${amber}" stroke-width="5" stroke-linecap="round" fill="none"/><path d="M23 15 a7 7 0 1 1 10 10" stroke="${amber}" stroke-width="4.5" stroke-linecap="round" fill="none"/></g></svg>`
}
