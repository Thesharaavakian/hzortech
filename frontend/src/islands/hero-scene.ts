/**
 * Hero background: a real-time WebGL particle field that slowly assembles
 * into the HZORTECH mark and holds — reinforcing "forged, not assembled"
 * before the visitor has read a word. Desktop/fine-pointer only; everyone
 * else (including no-WebGL and reduced-motion) gets the static mark poster
 * underneath, which this canvas fades in on top of once it has a real frame.
 *
 * Loaded on idle (after first paint), never blocks LCP (the H1 text).
 */
import type { Cleanup, MountFn } from '../core/islands'
import { finePointer, lowPower, reducedMotion } from '../core/prefs'

async function build(canvas: HTMLCanvasElement): Promise<Cleanup> {
  const THREE = await import('three')

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: false, powerPreference: 'low-power' })
  const dpr = Math.min(window.devicePixelRatio || 1, lowPower() ? 1 : 1.75)
  renderer.setPixelRatio(dpr)

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100)
  camera.position.set(0, 0, 11)

  const COUNT = lowPower() ? 420 : 1400
  const positions = new Float32Array(COUNT * 3)
  const targets = new Float32Array(COUNT * 3)
  const colors = new Float32Array(COUNT * 3)
  const ember = new THREE.Color('#d9272e')
  const steel = new THREE.Color('#8c877f')

  // Target shape: a loose blade silhouette (two tapered triangles forming a
  // vertical sword-like form) sampled by rejection — echoes the mark without
  // reproducing its exact linework.
  const sampleTarget = () => {
    for (let tries = 0; tries < 400; tries++) {
      const x = (Math.random() - 0.5) * 3.2
      const y = (Math.random() - 0.5) * 7.5
      const halfWidth = y > 1.2
        ? Math.max(0.05, 0.55 - (y - 1.2) * 0.42) // blade taper
        : y > -2.6
          ? 0.75 - Math.abs(y - (-0.7)) * 0.06 // guard + grip band
          : Math.max(0, 0.9 + (y + 2.6) * 0.5) // pommel flare, closes below
      if (Math.abs(x) <= halfWidth) return [x, y, (Math.random() - 0.5) * 0.6]
    }
    return [0, 0, 0]
  }

  for (let i = 0; i < COUNT; i++) {
    const i3 = i * 3
    positions[i3] = (Math.random() - 0.5) * 16
    positions[i3 + 1] = (Math.random() - 0.5) * 10
    positions[i3 + 2] = (Math.random() - 0.5) * 8
    const [tx, ty, tz] = sampleTarget()
    targets[i3] = tx * 1.3; targets[i3 + 1] = ty * 1.05; targets[i3 + 2] = tz
    const c = Math.random() < 0.22 ? ember : steel
    colors[i3] = c.r; colors[i3 + 1] = c.g; colors[i3 + 2] = c.b
  }

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  const material = new THREE.PointsMaterial({ size: 0.052, vertexColors: true, transparent: true, opacity: 0.85, sizeAttenuation: true, depthWrite: false })
  const points = new THREE.Points(geometry, material)
  scene.add(points)

  const posAttr = geometry.getAttribute('position') as InstanceType<typeof THREE.BufferAttribute>
  let raf = 0
  let start = 0
  let visible = true
  const ASSEMBLE_MS = 3200

  const resize = () => {
    const { clientWidth: w, clientHeight: h } = canvas
    if (!w || !h) return
    renderer.setSize(w, h, false)
    camera.aspect = w / h
    camera.updateProjectionMatrix()
  }
  const ro = new ResizeObserver(resize)
  ro.observe(canvas)
  resize()

  let readyFired = false
  const tick = (t: number) => {
    raf = requestAnimationFrame(tick)
    if (!visible) return
    if (!start) start = t
    const elapsed = t - start
    const progress = Math.min(1, elapsed / ASSEMBLE_MS)
    const ease = 1 - (1 - progress) ** 3
    for (let i = 0; i < COUNT; i++) {
      const i3 = i * 3
      posAttr.array[i3] += (targets[i3] - posAttr.array[i3]) * ease * 0.06
      posAttr.array[i3 + 1] += (targets[i3 + 1] - posAttr.array[i3 + 1]) * ease * 0.06
      posAttr.array[i3 + 2] += (targets[i3 + 2] - posAttr.array[i3 + 2]) * ease * 0.06
    }
    posAttr.needsUpdate = true
    points.rotation.y = Math.sin(t * 0.00008) * 0.18
    renderer.render(scene, camera)
    if (!readyFired && elapsed > 120) { readyFired = true; canvas.classList.add('is-ready') }
  }
  raf = requestAnimationFrame(tick)

  const io = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting }, { threshold: 0.01 })
  io.observe(canvas)

  return () => {
    cancelAnimationFrame(raf)
    ro.disconnect()
    io.disconnect()
    geometry.dispose()
    material.dispose()
    renderer.dispose()
  }
}

export const mount: MountFn = (el) => {
  if (reducedMotion() || !finePointer()) return
  const canvas = document.createElement('canvas')
  canvas.className = 'hero__canvas'
  canvas.setAttribute('aria-hidden', 'true')
  el.appendChild(canvas)
  let cleanup: Cleanup | undefined
  build(canvas).then((c) => { cleanup = c }).catch(() => { canvas.remove() })
  return () => cleanup?.()
}
