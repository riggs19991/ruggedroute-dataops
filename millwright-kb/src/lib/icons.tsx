// Stroke icon set (24 px grid) used across the UI, plus a map from category slug to icon.
// Drawn inline so they scale, recolour with currentColor and work offline.
import type { CSSProperties } from 'react'

type IconProps = { size?: number; className?: string; style?: CSSProperties; title?: string }

const PATHS: Record<string, string> = {
  search: '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  close: '<path d="M6 6l12 12M18 6L6 18"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"/>',
  moon: '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
  up: '<path d="M12 19V6M6 12l6-6 6 6"/>',
  bookmark: '<path d="M6 4h12v17l-6-4-6 4z"/>',
  print: '<path d="M7 8V4h10v4M5 8h14a2 2 0 0 1 2 2v6h-4v4H7v-4H3v-6a2 2 0 0 1 2-2z"/>',
  edit: '<path d="M4 20h4l11-11-4-4L4 16z"/>',
  trash: '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/>',
  download: '<path d="M12 4v11M7 10l5 5 5-5M4 20h16"/>',
  heart: '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
  chevron: '<path d="M9 6l6 6-6 6"/>',
  share: '<path d="M12 3v12M8 7l4-4 4 4M5 13v7h14v-7"/>',
  phone: '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  users: '<circle cx="9" cy="8" r="3.5"/><path d="M3 20c0-3.5 2.7-6 6-6s6 2.5 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M16.5 14c2.6 0 4.5 2 4.5 5"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',
  check: '<path d="M5 12l4 4L19 7"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
  list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
  // category icons
  flame: '<path d="M12 3c1 4 5 5.5 5 10a5 5 0 0 1-10 0c0-2 1-3.5 2.2-4.6C9.5 10.5 10.5 12 11.5 12 11.2 9 12 6 12 3z"/>',
  arc: '<path d="M4 20l6-6M8 10l6 6M12 6l6-2-2 6zM17 3l2 2"/>',
  cut: '<path d="M3 12h9M12 12l7-5M12 12l7 5M19 5l2 1M19 19l2-1"/>',
  target: '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="2.5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>',
  bearing: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.5"/><circle cx="12" cy="5.8" r="1.2"/><circle cx="12" cy="18.2" r="1.2"/><circle cx="5.8" cy="12" r="1.2"/><circle cx="18.2" cy="12" r="1.2"/>',
  belt: '<circle cx="7" cy="12" r="4"/><circle cx="17" cy="12" r="4"/><path d="M7 8h10M7 16h10"/>',
  hydraulic: '<rect x="3" y="8" width="13" height="8" rx="1.5"/><path d="M16 12h5M9 8v8"/>',
  hook: '<path d="M12 3v4a3 3 0 0 1-3 3v0a5 5 0 0 0 10 0v-1M10 3h4"/>',
  shield: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
  gear: '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
  ruler: '<rect x="3" y="8" width="18" height="8" rx="1"/><path d="M7 8v3M11 8v4M15 8v3M19 8v4"/>',
  book: '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5M8 3v16"/>',
  cap: '<path d="M3 9l9-4 9 4-9 4z"/><path d="M7 11v4c0 1.5 2.5 3 5 3s5-1.5 5-3v-4M21 9v5"/>',
  drop: '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
  wave: '<path d="M3 12h3l2-6 3 12 3-9 2 3h5"/>',
  clipboard: '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V2h6v2M9 12h6M9 16h4"/>',
  zap: '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
  wrench: '<path d="M14 6a4 4 0 0 0 5 5l-9 9-3-3 9-9a4 4 0 0 0-2-2z"/>',
  pump: '<circle cx="12" cy="12" r="8"/><path d="M12 7s3 3.5 3 5.5a3 3 0 0 1-6 0C9 10.5 12 7 12 7z"/>',
  block: '<path d="M3 20h18M5 20V10h14v10M9 10V6h6v4M12 6V3"/>',
  triangle: '<path d="M4 20L20 4v16zM8 20v-4M12 20v-8M16 20v-12"/>',
  rollers: '<circle cx="5" cy="14" r="2.5"/><circle cx="12" cy="14" r="2.5"/><circle cx="19" cy="14" r="2.5"/><path d="M3 9h18"/>',
  drill: '<path d="M4 12h9v4H4zM13 13h5M18 11v6M5 16v5M8 16v5"/>',
  bolt: '<path d="M12 2l7 4v8l-7 4-7-4V6z"/><circle cx="12" cy="10" r="3"/>',
  magnifier: '<circle cx="10" cy="10" r="6"/><path d="M14.5 14.5L20 20M8 10h4M10 8v4"/>',
  calc: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h2M12 11h2M16 11h.01M8 15h2M12 15h2M16 15h.01M8 18h6"/>',
  folder: '<path d="M3 6h6l2 2h10v11H3z"/>',
}

const CATEGORY_ICON: Record<string, string> = {
  welding: 'arc', 'cutting-gouging': 'cut', 'oxy-fuel': 'flame', alignment: 'target', bearings: 'bearing',
  'power-transmission': 'belt', gearboxes: 'gear', hydraulics: 'hydraulic', rigging: 'hook', safety: 'shield',
  study: 'cap', measurement: 'ruler', manuals: 'book', lubrication: 'drop', 'condition-monitoring': 'wave',
  'motors-electrical': 'zap', 'pumps-seals': 'pump', maintenance: 'clipboard', troubleshooting: 'magnifier',
  'shop-reference': 'calc', installation: 'block', 'layout-templates': 'triangle', conveyors: 'rollers',
  machining: 'drill', fasteners: 'bolt',
}

export function Icon({ name, size = 22, className, style, title }: IconProps & { name: string }) {
  const d = PATHS[name] ?? PATHS.folder
  return (
    <svg className={`ico${className ? ' ' + className : ''}`} width={size} height={size} viewBox="0 0 24 24" aria-hidden={title ? undefined : true} role={title ? 'img' : undefined} style={style} dangerouslySetInnerHTML={{ __html: (title ? `<title>${title}</title>` : '') + d }} />
  )
}

/** Icon for a category by slug; falls back to the generic folder icon. */
export function CategoryIcon({ slug, size = 22, className }: { slug: string; size?: number; className?: string }) {
  return <Icon name={CATEGORY_ICON[slug] ?? 'folder'} size={size} className={className} />
}

export function hasCategoryIcon(slug: string): boolean { return slug in CATEGORY_ICON }
