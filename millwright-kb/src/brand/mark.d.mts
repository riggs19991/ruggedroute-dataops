export const MARK_VARIANT: string
export const NAVY: string
export const AMBER: string
export const STEEL: string
export type MarkOptions = { variant?: string; amber?: string; steel?: string; navy?: string; id?: string }
export function gearPath(cx: number, cy: number, ro: number, rr: number, n: number, tipHalf?: number, baseHalf?: number): string
export function markInner(opts?: MarkOptions): string
export function markSvg(opts?: MarkOptions & { size?: number }): string
