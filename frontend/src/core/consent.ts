/**
 * Consent: the Meta Pixel is the only non-essential cookie on the site, and
 * it is loaded ONLY after an explicit "Accept". Declining is one click and
 * equally prominent. The choice is remembered; "Cookie settings" in the
 * footer reopens the panel.
 */
const KEY = 'hz-consent'
type Choice = 'granted' | 'denied'

const read = (): Choice | null => {
  try { const v = localStorage.getItem(KEY); return v === 'granted' || v === 'denied' ? v : null } catch { return null }
}
const write = (v: Choice) => { try { localStorage.setItem(KEY, v) } catch { /* ignore */ } }

function loadPixel(id: string) {
  if (!id || window.fbq) return
  const fbq = function (...args: unknown[]) {
    if (fbq.callMethod) fbq.callMethod(...args)
    else fbq.queue!.push(args)
  } as NonNullable<Window['fbq']>
  fbq.queue = []
  fbq.push = fbq
  fbq.loaded = true
  fbq.version = '2.0'
  window.fbq = fbq
  if (!window._fbq) window._fbq = fbq
  const s = document.createElement('script')
  s.async = true
  s.src = 'https://connect.facebook.net/en_US/fbevents.js'
  document.head.appendChild(s)
  fbq('init', id)
  fbq('track', 'PageView')
}

export function initConsent(): void {
  const panel = document.getElementById('consent')
  const pixelId = document.querySelector<HTMLMetaElement>('meta[name="hz:pixel"]')?.content || ''
  const choice = read()
  if (choice === 'granted') loadPixel(pixelId)
  if (!panel) return
  const show = () => { panel.hidden = false }
  const hide = () => { panel.hidden = true }
  if (!choice) show()
  panel.querySelector('[data-consent="accept"]')?.addEventListener('click', () => { write('granted'); hide(); loadPixel(pixelId) })
  panel.querySelector('[data-consent="decline"]')?.addEventListener('click', () => { write('denied'); hide() })
  document.querySelectorAll('[data-consent-open]').forEach((b) => b.addEventListener('click', (e) => {
    e.preventDefault(); show(); (panel.querySelector('button') as HTMLButtonElement | null)?.focus()
  }))
}

/** Conversion event — only fires if the pixel was consented to and loaded. */
export const track = (event: string, data?: Record<string, unknown>) => { window.fbq?.('track', event, data) }
