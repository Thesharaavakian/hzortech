/** Environment + preference probes shared by every motion/WebGL module. */

const mq = (q: string) => (typeof window !== 'undefined' && window.matchMedia ? window.matchMedia(q) : null)

export const reducedMotion = (): boolean => !!mq('(prefers-reduced-motion: reduce)')?.matches
export const finePointer = (): boolean => !!mq('(hover: hover) and (pointer: fine)')?.matches
export const isNarrow = (): boolean => !!mq('(max-width: 899.98px)')?.matches

type NetInfo = { saveData?: boolean; effectiveType?: string }
type NavExtras = Navigator & { connection?: NetInfo; deviceMemory?: number }

/** True when we should start in the cheapest visual tier. */
export const lowPower = (): boolean => {
  const nav = navigator as NavExtras
  const conn = nav.connection
  if (conn?.saveData) return true
  if (conn?.effectiveType && /(^|-)2g$/.test(conn.effectiveType)) return true
  if (nav.deviceMemory !== undefined && nav.deviceMemory <= 4 && (navigator.hardwareConcurrency || 8) <= 4) return true
  return false
}

export const onReducedMotionChange = (cb: (reduced: boolean) => void): (() => void) => {
  const m = mq('(prefers-reduced-motion: reduce)')
  if (!m) return () => {}
  const h = (e: MediaQueryListEvent) => cb(e.matches)
  m.addEventListener('change', h)
  return () => m.removeEventListener('change', h)
}

export const cssVar = (name: string, el: Element = document.documentElement): string =>
  getComputedStyle(el).getPropertyValue(name).trim()
