/**
 * Theme: follows the OS until the visitor chooses; the choice persists.
 * The pre-paint part lives inline in <head> (nonce'd) to avoid a flash.
 */
const KEY = 'hz-theme'

const effective = (): 'light' | 'dark' => {
  const set = document.documentElement.dataset.theme
  if (set === 'light' || set === 'dark') return set
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'
}

const sync = (btn: HTMLElement) => {
  const cur = effective()
  const next = cur === 'dark' ? 'light' : 'dark'
  const label = `Switch to ${next} theme`
  // Icon-only buttons get an accessible name; text buttons show it.
  if (btn.classList.contains('icon-btn')) { btn.setAttribute('aria-label', label); btn.setAttribute('title', label) }
  else btn.textContent = label
  btn.dataset.current = cur
  const meta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]:not([media])')
  if (meta) meta.content = cur === 'dark' ? '#0a0a0b' : '#f1eee8'
}

export function initTheme(): void {
  const buttons = document.querySelectorAll<HTMLElement>('[data-theme-toggle]')
  buttons.forEach((btn) => {
    sync(btn)
    btn.addEventListener('click', () => {
      const next = effective() === 'dark' ? 'light' : 'dark'
      document.documentElement.dataset.theme = next
      try { localStorage.setItem(KEY, next) } catch { /* storage may be blocked */ }
      buttons.forEach(sync)
      window.dispatchEvent(new CustomEvent('hz:theme', { detail: next }))
    })
  })
  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => {
    buttons.forEach(sync)
    window.dispatchEvent(new CustomEvent('hz:theme', { detail: effective() }))
  })
}

export const currentTheme = effective
