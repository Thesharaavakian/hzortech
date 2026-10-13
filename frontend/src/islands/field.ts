/**
 * Field: a generative wireframe network rendered live on <canvas> — nodes
 * drift slowly and connect to their nearest neighbours, with the occasional
 * signal pulse travelling an edge. Replaces photographic (or AI-rendered)
 * hero imagery on secondary pages: this draws the same "system, not stock
 * photo" visual the home page's particle hero and the system-map/signature
 * islands already establish, so every hero on the site reads as one
 * consistent generative language instead of competing with it.
 *
 * Canvas2D, not WebGL — these heroes don't need a 3D scene, and staying off
 * Three.js keeps this off the critical path for ten service pages at once.
 * Reduced-motion and low-power visitors get a single static frame.
 */
import type { Cleanup, MountFn } from '../core/islands'
import { lowPower, reducedMotion } from '../core/prefs'

type Node = { x: number; y: number; vx: number; vy: number }
type Pulse = { from: number; to: number; t: number; speed: number }

function build(canvas: HTMLCanvasElement, static_: boolean): Cleanup {
  const ctx = canvas.getContext('2d')
  if (!ctx) return () => {}

  const steel = 'rgba(124, 147, 172, OPA)'
  const ember = 'rgba(255, 138, 0, OPA)'
  const NODE_COUNT = lowPower() ? 16 : 30
  const LINK_DIST = 0.32 // fraction of min(w, h)

  let w = 0, h = 0, dpr = 1
  const nodes: Node[] = Array.from({ length: NODE_COUNT }, () => ({
    x: Math.random(),
    y: Math.random(),
    vx: (Math.random() - 0.5) * 0.00006,
    vy: (Math.random() - 0.5) * 0.00006,
  }))
  const pulses: Pulse[] = []

  const resize = () => {
    const { clientWidth, clientHeight } = canvas
    if (!clientWidth || !clientHeight) return
    dpr = Math.min(window.devicePixelRatio || 1, lowPower() ? 1 : 1.75)
    w = clientWidth; h = clientHeight
    canvas.width = Math.round(w * dpr)
    canvas.height = Math.round(h * dpr)
  }
  const ro = new ResizeObserver(resize)
  ro.observe(canvas)
  resize()

  const draw = () => {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.clearRect(0, 0, w, h)

    const pts = nodes.map((n) => ({ x: n.x * w, y: n.y * h }))
    const minSide = Math.min(w, h)
    const links: [number, number, number][] = []
    for (let i = 0; i < pts.length; i++) {
      for (let j = i + 1; j < pts.length; j++) {
        const dx = pts[i].x - pts[j].x
        const dy = pts[i].y - pts[j].y
        const dist = Math.hypot(dx, dy)
        if (dist < minSide * LINK_DIST) links.push([i, j, dist])
      }
    }

    links.forEach(([i, j, dist]) => {
      const opacity = (1 - dist / (minSide * LINK_DIST)) * 0.22
      ctx.strokeStyle = steel.replace('OPA', opacity.toFixed(3))
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(pts[i].x, pts[i].y)
      ctx.lineTo(pts[j].x, pts[j].y)
      ctx.stroke()
    })

    pts.forEach((p) => {
      ctx.fillStyle = steel.replace('OPA', '0.55')
      ctx.beginPath()
      ctx.arc(p.x, p.y, 1.6, 0, Math.PI * 2)
      ctx.fill()
    })

    if (!static_) {
      pulses.forEach((pulse) => {
        const a = pts[pulse.from], b = pts[pulse.to]
        if (!a || !b) return
        const x = a.x + (b.x - a.x) * pulse.t
        const y = a.y + (b.y - a.y) * pulse.t
        const fade = Math.sin(pulse.t * Math.PI)
        ctx.fillStyle = ember.replace('OPA', (fade * 0.9).toFixed(3))
        ctx.beginPath()
        ctx.arc(x, y, 2.4, 0, Math.PI * 2)
        ctx.fill()
      })
    }
  }

  if (static_) { draw(); return () => ro.disconnect() }

  let raf = 0
  let visible = true
  let lastSpawn = 0
  const tick = (t: number) => {
    raf = requestAnimationFrame(tick)
    if (!visible) return
    nodes.forEach((n) => {
      n.x += n.vx; n.y += n.vy
      if (n.x < 0 || n.x > 1) n.vx *= -1
      if (n.y < 0 || n.y > 1) n.vy *= -1
      n.x = Math.min(1, Math.max(0, n.x))
      n.y = Math.min(1, Math.max(0, n.y))
    })
    for (let i = pulses.length - 1; i >= 0; i--) {
      pulses[i].t += pulses[i].speed
      if (pulses[i].t >= 1) pulses.splice(i, 1)
    }
    if (t - lastSpawn > 2600 && pulses.length < 2 && nodes.length > 1) {
      lastSpawn = t
      const from = Math.floor(Math.random() * nodes.length)
      let to = Math.floor(Math.random() * nodes.length)
      if (to === from) to = (to + 1) % nodes.length
      pulses.push({ from, to, t: 0, speed: 0.012 })
    }
    draw()
  }
  raf = requestAnimationFrame(tick)

  const io = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting }, { threshold: 0.01 })
  io.observe(canvas)

  return () => {
    cancelAnimationFrame(raf)
    ro.disconnect()
    io.disconnect()
  }
}

export const mount: MountFn = (el) => {
  const canvas = document.createElement('canvas')
  canvas.className = 'field__canvas'
  canvas.setAttribute('aria-hidden', 'true')
  el.appendChild(canvas)
  return build(canvas, reducedMotion())
}
