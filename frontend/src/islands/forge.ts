/**
 * "Forged, not assembled" — a scroll-scrubbed image-sequence film (canvas 2D
 * drawImage, not <video>: frame-accurate in both scroll directions in every
 * browser). Falls back to the server-rendered static vertical read (see
 * home.css) whenever motion isn't appropriate or frame 1 can't be fetched.
 *
 * Loading strategy: the pin/scrub is set up as soon as the FIRST frame is
 * ready — not after all ~145 — so a slow connection gets a fast, correct
 * pin instead of a long wait followed by a layout jump. The rest of the
 * sequence loads in the background; drawFrame() always has a frame to show
 * (it walks outward from the requested index to the nearest one that has
 * actually finished loading), so scrubbing ahead of the network never
 * throws or blanks the canvas — it just briefly reuses the last known frame.
 */
import type { Cleanup, MountFn } from '../core/islands'
import { gsap, ScrollTrigger } from '../core/motion'
import { isNarrow, reducedMotion } from '../core/prefs'

type Tier = { dir: string; count: number; width: number; height: number }
type Props = { base: string; desktop: Tier; mobile: Tier; chapters: number }

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.decoding = 'async'
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

async function build(el: HTMLElement, props: Props): Promise<Cleanup | void> {
  const section = el.closest<HTMLElement>('.forge')
  if (!section) return
  const tier = isNarrow() ? props.mobile : props.desktop
  const urlFor = (i: number) => `${props.base}${tier.dir}/${String(i + 1).padStart(4, '0')}.webp`

  const frames: (HTMLImageElement | undefined)[] = new Array(tier.count)
  try {
    frames[0] = await loadImage(urlFor(0))
  } catch {
    return // stay on the static fallback — nothing to scrub
  }

  const canvas = document.createElement('canvas')
  canvas.width = tier.width
  canvas.height = tier.height
  el.insertBefore(canvas, el.firstChild)
  const ctx = canvas.getContext('2d', { alpha: false })
  if (!ctx) return

  const nearestLoaded = (i: number) => {
    for (let r = 0; r < frames.length; r++) {
      if (frames[i - r]) return frames[i - r]
      if (frames[i + r]) return frames[i + r]
    }
    return undefined
  }
  const drawFrame = (i: number) => {
    const clamped = Math.max(0, Math.min(frames.length - 1, i))
    const frame = frames[clamped] || nearestLoaded(clamped)
    if (frame) ctx.drawImage(frame, 0, 0, tier.width, tier.height)
  }
  drawFrame(0)

  section.classList.add('is-scrubbing')
  const frameCounter = section.querySelector<HTMLElement>('[data-forge-frame]')
  const chapterEls = Array.from(section.querySelectorAll<HTMLElement>('[data-chapter]'))
  const obj = { f: 0 }
  let cancelled = false

  // The rest of the sequence (144 more requests, ~4 MB) only starts
  // downloading once the visitor is actually about to scrub it — not the
  // moment this island mounts ~800px out, which would tax everyone who
  // scrolls past without ever reaching this section.
  let bulkLoadStarted = false
  const startBulkLoad = () => {
    if (bulkLoadStarted) return
    bulkLoadStarted = true
    const CONCURRENCY = 6
    const indices = Array.from({ length: tier.count - 1 }, (_, i) => i + 1)
    ;(async () => {
      while (indices.length && !cancelled) {
        await Promise.all(indices.splice(0, CONCURRENCY).map(async (i) => {
          try { frames[i] = await loadImage(urlFor(i)) } catch { /* nearest-neighbour fallback stands in */ }
        }))
      }
    })()
  }

  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: section,
      start: 'top top',
      end: '+=320%',
      scrub: 0.4,
      pin: section.querySelector('.forge__pin'),
      anticipatePin: 1,
      onEnter: startBulkLoad,
      onEnterBack: startBulkLoad,
    },
  })
  tl.to(obj, {
    f: tier.count - 1,
    ease: 'none',
    duration: 1,
    onUpdate: () => {
      const i = Math.round(obj.f)
      drawFrame(i)
      if (frameCounter) frameCounter.textContent = String(i + 1).padStart(3, '0')
    },
  }, 0)

  // Chapter captions: evenly spaced across the scrub, each holding ~1/N.
  const n = Math.max(1, props.chapters)
  chapterEls.forEach((chEl, i) => {
    tl.to(chEl, { opacity: 1, duration: 0.001 }, i / n)
      .call(() => chapterEls.forEach((c, j) => c.classList.toggle('is-active', j === i)), undefined, i / n)
    if (i < n - 1) tl.to(chEl, { opacity: 0, duration: 0.001 }, (i + 1) / n - 0.001)
  })

  ScrollTrigger.refresh()

  // Pre-scrubbed into view at setup time (a deep link, a very short page) —
  // onEnter may already have fired by the time refresh() settles positions,
  // so check once more rather than depend on it alone.
  if ((tl.scrollTrigger?.progress ?? 0) > 0) startBulkLoad()

  return () => {
    cancelled = true
    tl.scrollTrigger?.kill()
    tl.kill()
    canvas.remove()
    section.classList.remove('is-scrubbing')
  }
}

export const mount: MountFn = (el, props) => {
  if (reducedMotion()) return
  let cleanup: Cleanup | void
  const p = build(el, props as unknown as Props).then((c) => { cleanup = c })
  return () => { p.then(() => cleanup?.()) }
}
