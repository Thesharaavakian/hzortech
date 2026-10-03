/**
 * Islands: server-rendered placeholders that upgrade to interactive
 * components. Each island module exports `mount(el, props) => cleanup`.
 * Chunks are only fetched when the island approaches the viewport (or on
 * idle / immediately, per data-island-load), so the core bundle stays small.
 *
 *   <div data-island="system-map" data-props="system-map-props">…fallback…</div>
 *   {{ props|json_script:"system-map-props" }}
 */
export type Cleanup = () => void
export type MountFn = (el: HTMLElement, props: Record<string, unknown>) => Cleanup | void | Promise<Cleanup | void>
type IslandModule = { mount: MountFn }

const registry: Record<string, () => Promise<IslandModule>> = {
  'hero-scene': () => import('../islands/hero-scene'),
  'system-map': () => import('../islands/system-map'),
  forge: () => import('../islands/forge'),
  intake: () => import('../islands/intake'),
  signature: () => import('../islands/signature'),
  architecture: () => import('../islands/architecture'),
  'visit-meter': () => import('../islands/visit-meter'),
  filter: () => import('../islands/filter'),
}

const mounted = new WeakSet<HTMLElement>()

function readProps(el: HTMLElement): Record<string, unknown> {
  const id = el.dataset.props
  if (!id) return {}
  const node = document.getElementById(id)
  if (!node?.textContent) return {}
  try { return JSON.parse(node.textContent) } catch { return {} }
}

async function mountIsland(el: HTMLElement) {
  if (mounted.has(el)) return
  mounted.add(el)
  const name = el.dataset.island || ''
  const loader = registry[name]
  if (!loader) { console.warn(`[islands] unknown island "${name}"`); return }
  try {
    const mod = await loader()
    await mod.mount(el, readProps(el))
    el.classList.add('is-mounted')
    el.dispatchEvent(new CustomEvent('island:mounted', { bubbles: true }))
  } catch (err) {
    // The server-rendered fallback stays in place — the page keeps working.
    el.classList.add('is-failed')
    console.error(`[islands] ${name} failed to mount`, err)
  }
}

const NEAR_PX = 800

/** True if el's box is within NEAR_PX of the viewport — same threshold the
 * IntersectionObserver below uses, kept as a plain geometry check too. */
function isNear(el: HTMLElement): boolean {
  const r = el.getBoundingClientRect()
  return r.bottom > -NEAR_PX && r.top < (window.innerHeight || document.documentElement.clientHeight) + NEAR_PX
}

export function initIslands(root: ParentNode = document): void {
  const els = Array.from(root.querySelectorAll<HTMLElement>('[data-island]'))
  const visible: HTMLElement[] = []
  els.forEach((el) => {
    const mode = el.dataset.islandLoad || 'visible'
    if (mode === 'eager') mountIsland(el)
    else if (mode === 'idle') {
      const ric = window.requestIdleCallback || ((cb: () => void) => window.setTimeout(cb, 200))
      window.addEventListener('load', () => ric(() => mountIsland(el)), { once: true })
      if (document.readyState === 'complete') ric(() => mountIsland(el))
    } else visible.push(el)
  })
  if (!visible.length) return

  // IntersectionObserver is the primary (cheapest) signal. A plain
  // rAF-throttled scroll/resize sweep runs alongside it rather than instead
  // of it — belt-and-braces against the rare case (older engines, an
  // observer that never gets a rendering-pipeline tick in an unusual host)
  // where IO silently never fires; mountIsland() is idempotent, so whichever
  // signal notices first wins and the other is a no-op.
  let pending = visible.slice()
  const sweep = () => {
    if (!pending.length) return
    pending = pending.filter((el) => {
      if (!isNear(el)) return true
      mountIsland(el)
      return false
    })
    if (!pending.length) {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
    }
  }
  let ticking = false
  const onScroll = () => {
    if (ticking) return
    ticking = true
    requestAnimationFrame(() => { ticking = false; sweep() })
  }
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onScroll, { passive: true })
  sweep() // covers anything already on screen at boot

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) { io.unobserve(e.target); mountIsland(e.target as HTMLElement) }
      })
    }, { rootMargin: `${NEAR_PX}px 0px ${NEAR_PX}px 0px` })
    visible.forEach((el) => io.observe(el))
  }

  // Last resort: neither of the above is tied to requestAnimationFrame alone
  // (IntersectionObserver isn't meant to be), but both are tied to the
  // rendering pipeline having a tick at all. setTimeout doesn't need one, so
  // it's the backstop that guarantees every island eventually mounts even
  // in a host that never gives the page a paint (a backgrounded/occluded
  // webview, some embedded contexts) — a few seconds of extra wait there
  // beats a fallback staying a fallback forever.
  window.setTimeout(() => pending.slice().forEach(mountIsland), 4000)
}
