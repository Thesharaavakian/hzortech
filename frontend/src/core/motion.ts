/**
 * Motion system.
 *
 * - Lenis smooth scroll on fine pointers only (touch keeps native momentum),
 *   driven by the GSAP ticker so ScrollTrigger and Lenis share one clock.
 * - Declarative hooks in the markup, so templates never ship inline JS:
 *     data-reveal[="fade"]      fade/rise in once when entering the viewport
 *     data-split                line-masked heading reveal (SplitText)
 *     data-scrub-words          word-by-word ink-in scrubbed by scroll
 *     data-parallax="0.15"      vertical parallax (fraction of element height)
 *     data-stack-card           sticky stacked cards: previous card recedes
 * - Nothing here runs under prefers-reduced-motion: content is simply shown.
 */
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { SplitText } from 'gsap/SplitText'
import Lenis from 'lenis'
import { finePointer, reducedMotion } from './prefs'

gsap.registerPlugin(ScrollTrigger, SplitText)

export { gsap, ScrollTrigger }

let started = false

export function initMotion(): void {
  const root = document.documentElement
  if (reducedMotion()) {
    root.classList.remove('js-motion')
    return
  }
  if (started) return
  started = true

  ScrollTrigger.config({ ignoreMobileResize: true })

  if (finePointer()) {
    const lenis = new Lenis({ lerp: 0.11, smoothWheel: true, anchors: { offset: -80 }, autoRaf: false })
    window.__lenis = lenis
    lenis.on('scroll', ScrollTrigger.update)
    gsap.ticker.add((t) => lenis.raf(t * 1000))
    gsap.ticker.lagSmoothing(0)
  }

  initReveals()
  document.fonts?.ready.then(() => {
    initSplits()
    initScrubWords()
    initParallax()
    initStack()
    ScrollTrigger.refresh()
  })
  window.addEventListener('load', () => ScrollTrigger.refresh(), { once: true })

  // Islands lazy-mount well after this runs (scroll-proximity gated, up to
  // several seconds out via islands.ts's own backstop) and several of them
  // change page height after mounting — forge's pin alone goes from a
  // content-sized block to a full 100svh pinned section. A plain
  // ScrollTrigger.refresh() is NOT enough to fix this: GSAP correctly
  // recalculates ScrollTrigger.maxScroll() and self-referencing triggers
  // (trigger: el, start: 'top 88%') after a refresh, but a trigger created
  // earlier with `trigger: someLaterSibling` keeps stale start/end pixel
  // values even across repeated forced refreshes once something ABOVE that
  // sibling has inserted a pin-spacer — confirmed by killing and recreating
  // the exact same tween/trigger after the fact, which reads the correct
  // (now forge-inclusive) position immediately. So initStack()'s own
  // triggers are killed and recreated (not just refreshed) whenever any
  // island mounts, since any of them can change layout below itself; it's
  // the one spot in this file using a *sibling* element as the trigger
  // reference, which is what's exposed to this GSAP behavior.
  document.addEventListener('island:mounted', () => {
    initStack()
    ScrollTrigger.refresh()
  }, { passive: true })
}

function revealOne(el: HTMLElement) {
  if (el.classList.contains('is-in')) return
  const group = el.closest('[data-reveal-group]')
  if (group) {
    const siblings = Array.from(group.querySelectorAll('[data-reveal]'))
    el.style.setProperty('--reveal-delay', `${Math.min(siblings.indexOf(el), 8) * 0.07}s`)
  }
  el.classList.add('is-in')
}

function initReveals() {
  const els = Array.from(document.querySelectorAll<HTMLElement>('[data-reveal]'))
  if (!els.length) return

  // The watchdog is registered FIRST and unconditionally, before touching
  // IntersectionObserver at all — `new IntersectionObserver()` throws
  // synchronously (a ReferenceError, not a gentle "unsupported") in any
  // environment that lacks it, which would otherwise abort this whole
  // function before the watchdog line is ever reached. Generous rootMargin
  // plus this watchdog also covers fast/jump scrolling (End key, scrollbar
  // drag, fast flicks can all skip an element's trigger frame) or an
  // observer that never gets a rendering-pipeline tick. Unlike the islands
  // (which have working fallback HTML either way), a data-reveal element
  // IS the content — there's nothing to fall back to.
  let unobserveAll = () => {}
  window.setTimeout(() => {
    els.forEach((el) => revealOne(el))
    unobserveAll()
  }, 2500)

  if (!('IntersectionObserver' in window)) {
    els.forEach(revealOne)
    return
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return
      revealOne(e.target as HTMLElement)
      io.unobserve(e.target)
    })
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.01 })
  els.forEach((el) => io.observe(el))
  unobserveAll = () => els.forEach((el) => io.unobserve(el))
}

function initSplits() {
  document.querySelectorAll<HTMLElement>('[data-split]').forEach((el) => {
    SplitText.create(el, {
      type: 'lines',
      mask: 'lines',
      linesClass: 'split-line',
      aria: 'auto',
      autoSplit: true,
      onSplit(self) {
        return gsap.from(self.lines, {
          yPercent: 108,
          duration: 1.1,
          ease: 'expo.out',
          stagger: 0.08,
          scrollTrigger: { trigger: el, start: 'top 88%', once: true },
        })
      },
    })
  })
}

function initScrubWords() {
  document.querySelectorAll<HTMLElement>('[data-scrub-words]').forEach((el) => {
    const split = SplitText.create(el, { type: 'words', aria: 'auto' })
    gsap.fromTo(split.words, { opacity: 0.16 }, {
      opacity: 1,
      ease: 'none',
      stagger: 0.12,
      scrollTrigger: { trigger: el, start: 'top 78%', end: 'bottom 42%', scrub: 0.6 },
    })
  })
}

function initParallax() {
  document.querySelectorAll<HTMLElement>('[data-parallax]').forEach((el) => {
    const amount = parseFloat(el.dataset.parallax || '0.15')
    gsap.fromTo(el, { yPercent: -amount * 50 }, {
      yPercent: amount * 50,
      ease: 'none',
      scrollTrigger: { trigger: el.parentElement || el, start: 'top bottom', end: 'bottom top', scrub: true },
    })
  })
}

let stackTriggers: ScrollTrigger[] = []

// Safe to call more than once: kills its own previous triggers first. It's
// re-run (not just covered by ScrollTrigger.refresh()) whenever an island
// mounts below it — see the 'island:mounted' listener in initMotion() for
// why a refresh alone doesn't correct these specific triggers' positions.
function initStack() {
  stackTriggers.forEach((t) => t.kill())
  stackTriggers = []
  const cards = gsap.utils.toArray<HTMLElement>('[data-stack-card]')
  cards.forEach((card, i) => {
    const next = cards[i + 1]
    if (!next) return
    // Fades fully to 0, not a dim-but-still-visible floor: the previous
    // card's own sticky dwell and the next card's entrance are tuned to
    // line up almost exactly, but not pixel-perfectly at every viewport
    // size — a non-zero opacity floor meant whatever sliver of mistiming
    // existed stayed permanently visible as two faded cards' content
    // overlapping (the "one thing hurting the other from showing" bug).
    // Reaching true 0 means any such sliver is invisible by construction.
    const tween = gsap.to(card.querySelector('[data-stack-inner]') || card, {
      scale: 0.94,
      opacity: 0,
      ease: 'none',
      scrollTrigger: { trigger: next, start: 'top bottom', end: 'top top+=140', scrub: true },
    })
    if (tween.scrollTrigger) stackTriggers.push(tween.scrollTrigger)
  })
}
