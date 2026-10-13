/**
 * Cursor-reactive micro-interactions: magnetic buttons and a subtle tilt on
 * glass surfaces. Fine-pointer + no-reduced-motion only — touch and
 * keyboard users get the plain, fully-functional element underneath, since
 * neither of these ever carries information, only feel.
 */
import { finePointer, reducedMotion } from './prefs'

const MAGNET_SELECTOR = '.btn--primary, .btn--large'
const TILT_SELECTOR = '.engagement, .svc-signature'

function initMagnetic() {
  document.querySelectorAll<HTMLElement>(MAGNET_SELECTOR).forEach((el) => {
    if (el.dataset.magnetBound) return
    el.dataset.magnetBound = 'true'
    let raf = 0
    const reset = () => {
      el.style.transform = ''
    }
    el.addEventListener('mousemove', (e) => {
      const r = el.getBoundingClientRect()
      const x = e.clientX - (r.left + r.width / 2)
      const y = e.clientY - (r.top + r.height / 2)
      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => {
        el.style.transform = `translate(${x * 0.18}px, ${y * 0.3}px)`
      })
    })
    el.addEventListener('mouseleave', () => {
      cancelAnimationFrame(raf)
      el.style.transition = 'transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)'
      reset()
      window.setTimeout(() => { el.style.transition = '' }, 500)
    })
  })
}

function initTilt() {
  document.querySelectorAll<HTMLElement>(TILT_SELECTOR).forEach((el) => {
    if (el.dataset.tiltBound) return
    el.dataset.tiltBound = 'true'
    el.style.transformStyle = 'preserve-3d'
    let raf = 0
    el.addEventListener('mousemove', (e) => {
      const r = el.getBoundingClientRect()
      const px = (e.clientX - r.left) / r.width - 0.5
      const py = (e.clientY - r.top) / r.height - 0.5
      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => {
        el.style.transform = `perspective(900px) rotateX(${(-py * 5).toFixed(2)}deg) rotateY(${(px * 5).toFixed(2)}deg)`
      })
    })
    el.addEventListener('mouseleave', () => {
      cancelAnimationFrame(raf)
      el.style.transition = 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)'
      el.style.transform = 'perspective(900px) rotateX(0deg) rotateY(0deg)'
      window.setTimeout(() => { el.style.transition = '' }, 600)
    })
  })
}

export function initInteractions(): void {
  if (reducedMotion() || !finePointer()) return
  initMagnetic()
  initTilt()
  // Islands (signature, etc.) mount after this runs — pick up any new
  // matching elements the same way motion.ts re-runs initStack().
  document.addEventListener('island:mounted', () => { initMagnetic(); initTilt() }, { passive: true })
}
