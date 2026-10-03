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

function initStack() {
  const cards = gsap.utils.toArray<HTMLElement>('[data-stack-card]')
  cards.forEach((card, i) => {
    const next = cards[i + 1]
    if (!next) return
    gsap.to(card.querySelector('[data-stack-inner]') || card, {
      scale: 0.94,
      opacity: 0.35,
      ease: 'none',
      scrollTrigger: { trigger: next, start: 'top bottom', end: 'top top+=96', scrub: true },
    })
  })
}
