/**
 * Header: turns solid once the page scrolls, hides on scroll-down and returns
 * on scroll-up, switches to light-on-dark ink over .dark-island sections, and
 * drives the mobile menu (a native <dialog> — focus trap + Esc for free).
 */
export function initHeader(): void {
  const header = document.querySelector<HTMLElement>('.site-header')
  if (!header) return
  let lastY = window.scrollY
  let ticking = false

  const update = () => {
    ticking = false
    const y = window.scrollY
    header.classList.toggle('is-solid', y > 8)
    const focusInside = header.contains(document.activeElement)
    if (y > 160 && y > lastY + 4 && !focusInside) header.classList.add('is-hidden')
    else if (y < lastY - 4 || y < 160) header.classList.remove('is-hidden')
    lastY = y
  }
  window.addEventListener('scroll', () => {
    if (!ticking) { ticking = true; requestAnimationFrame(update) }
  }, { passive: true })
  header.addEventListener('focusin', () => header.classList.remove('is-hidden'))
  update()

  // Light ink while a dark island sits under the header band.
  const islands = document.querySelectorAll('.dark-island')
  if (islands.length && 'IntersectionObserver' in window) {
    const under = new Set<Element>()
    const band = () => `0px 0px -${Math.max(0, window.innerHeight - 68)}px 0px`
    let io: IntersectionObserver
    const observe = () => {
      io?.disconnect()
      under.clear()
      io = new IntersectionObserver((entries) => {
        entries.forEach((e) => (e.isIntersecting ? under.add(e.target) : under.delete(e.target)))
        header.classList.toggle('is-over-dark', under.size > 0)
      }, { rootMargin: band() })
      islands.forEach((el) => io.observe(el))
    }
    observe()
    let rt = 0
    window.addEventListener('resize', () => { clearTimeout(rt); rt = window.setTimeout(observe, 200) })
  }

  // Mobile menu
  const menu = document.getElementById('mobile-menu') as HTMLDialogElement | null
  const openers = document.querySelectorAll<HTMLElement>('[data-menu-open]')
  if (menu && typeof menu.showModal === 'function') {
    openers.forEach((b) => b.addEventListener('click', () => {
      menu.showModal()
      b.setAttribute('aria-expanded', 'true')
      window.__lenis?.stop()
    }))
    menu.addEventListener('close', () => {
      openers.forEach((b) => b.setAttribute('aria-expanded', 'false'))
      window.__lenis?.start()
    })
    menu.querySelectorAll('[data-menu-close], a').forEach((el) => el.addEventListener('click', () => menu.close()))
  }

  // Live Yerevan clock in the footer/menu (office hours are part of the promise).
  const clocks = document.querySelectorAll<HTMLElement>('[data-yerevan-time]')
  if (clocks.length) {
    const fmt = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Yerevan', hour: '2-digit', minute: '2-digit', weekday: 'short' })
    const tick = () => {
      const parts = Object.fromEntries(fmt.formatToParts(new Date()).map((p) => [p.type, p.value]))
      const h = Number(parts.hour)
      const open = !['Sat', 'Sun'].includes(parts.weekday) && h >= 9 && h < 18
      clocks.forEach((c) => { c.textContent = `${parts.hour}:${parts.minute} in Yerevan · ${open ? 'office open' : 'office closed — we reply next business day'}` })
    }
    tick()
    window.setInterval(tick, 30_000)
  }
}
