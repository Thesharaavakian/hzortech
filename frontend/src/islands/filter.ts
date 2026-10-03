/**
 * Progressive enhancement over the work index's plain ?layer= links: the
 * server-rendered filter already works with zero JS (a real navigation with
 * SSR-filtered results). Once this mounts, clicking a chip instead filters
 * the already-rendered cards in place and updates the URL via
 * history.pushState — instant, and back/forward still works.
 */
import type { MountFn } from '../core/islands'

export const mount: MountFn = (el) => {
  const list = document.querySelector<HTMLElement>('[data-filter-target]')
  if (!list) return
  const status = el.querySelector<HTMLElement>('[data-filter-status]')
  const chips = Array.from(el.querySelectorAll<HTMLAnchorElement>('.chip'))
  el.dataset.live = 'true'

  const apply = (layer: string, push: boolean) => {
    const cards = Array.from(list.querySelectorAll<HTMLElement>('[data-layers]'))
    let shown = 0
    cards.forEach((card) => {
      const match = !layer || (card.dataset.layers || '').split(' ').includes(layer)
      card.hidden = !match
      if (match) shown += 1
    })
    chips.forEach((c) => {
      const isActive = (c.dataset.filter || '') === layer
      c.classList.toggle('is-active', isActive)
      if (isActive) c.setAttribute('aria-current', 'true')
      else c.removeAttribute('aria-current')
    })
    if (status) status.textContent = `Showing ${shown} case ${shown === 1 ? 'study' : 'studies'}.`
    if (push) {
      const url = new URL(window.location.href)
      if (layer) url.searchParams.set('layer', layer)
      else url.searchParams.delete('layer')
      window.history.pushState({ layer }, '', url)
    }
  }

  chips.forEach((chip) => {
    chip.addEventListener('click', (e) => {
      e.preventDefault()
      apply(chip.dataset.filter || '', true)
    })
  })
  window.addEventListener('popstate', () => {
    apply(new URLSearchParams(window.location.search).get('layer') || '', false)
  })
}
