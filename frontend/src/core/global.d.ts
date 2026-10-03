import type Lenis from 'lenis'

declare global {
  interface Window {
    __lenis?: Lenis
    fbq?: ((...args: unknown[]) => void) & { callMethod?: (...a: unknown[]) => void; queue?: unknown[]; push?: unknown; loaded?: boolean; version?: string }
    _fbq?: unknown
    turnstile?: { render: (el: HTMLElement, opts: Record<string, unknown>) => string; reset: (id?: string) => void }
  }
}
export {}
