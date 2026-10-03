/**
 * "This page, measured on your device" — an honest instrument, not a claim.
 * Everything shown is read from the real Navigation/Resource Timing APIs and
 * from the actual response headers of this document (re-fetched from cache),
 * for this visit, on this device. No fabricated numbers.
 */
import { useEffect, useState } from 'react'
import { mountReact } from './shared'
import type { MountFn } from '../core/islands'

type Metrics = {
  ttfb: number | null
  domReady: number | null
  loaded: number | null
  lcp: number | null
  transferKB: number | null
  requestCount: number | null
  headers: Record<string, string | null>
}

function useMetrics(): Metrics {
  const [m, setM] = useState<Metrics>({
    ttfb: null, domReady: null, loaded: null, lcp: null, transferKB: null, requestCount: null, headers: {},
  })

  useEffect(() => {
    let lcp: number | null = null
    let po: PerformanceObserver | null = null
    try {
      po = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const last = entries[entries.length - 1] as PerformanceEntry & { startTime: number }
        if (last) lcp = Math.round(last.startTime)
      })
      po.observe({ type: 'largest-contentful-paint', buffered: true })
    } catch { /* unsupported */ }

    const collect = async () => {
      const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[]
      const transferKB = Math.round(
        (resources.reduce((sum, r) => sum + (r.transferSize || 0), 0) + (nav?.transferSize || 0)) / 1024,
      )
      let headers: Record<string, string | null> = {}
      try {
        const res = await fetch(window.location.href, { method: 'GET', cache: 'force-cache' })
        headers = {
          'content-security-policy': res.headers.get('content-security-policy'),
          'strict-transport-security': res.headers.get('strict-transport-security'),
          'x-content-type-options': res.headers.get('x-content-type-options'),
          'x-frame-options': res.headers.get('x-frame-options'),
          'referrer-policy': res.headers.get('referrer-policy'),
        }
      } catch { /* offline */ }
      setM({
        ttfb: nav ? Math.round(nav.responseStart - nav.requestStart) : null,
        domReady: nav ? Math.round(nav.domContentLoadedEventEnd - nav.startTime) : null,
        loaded: nav ? Math.round(nav.loadEventEnd - nav.startTime) : null,
        lcp,
        transferKB,
        requestCount: resources.length + (nav ? 1 : 0),
        headers,
      })
    }
    if (document.readyState === 'complete') window.setTimeout(collect, 400)
    else window.addEventListener('load', () => window.setTimeout(collect, 400), { once: true })

    return () => po?.disconnect()
  }, [])

  return m
}

function Cell({ label, value, unit, good }: { label: string; value: number | null; unit: string; good?: boolean }) {
  return (
    <div className="meter-cell">
      <p className="meter-cell__label">{label}</p>
      <p className={`meter-cell__value${good === undefined ? '' : good ? ' is-good' : ' is-warn'}`}>
        {value === null ? '—' : value}<span className="meter-cell__unit">{value === null ? '' : unit}</span>
      </p>
    </div>
  )
}

function headerRow(label: string, value: string | null) {
  return (
    <div key={label}>
      <dt>{label}</dt>
      <dd>{value ? <code className="ok">{value.length > 70 ? `${value.slice(0, 70)}…` : value}</code> : <code className="warn">not sent on this response</code>}</dd>
    </div>
  )
}

function VisitMeter() {
  const m = useMetrics()
  return (
    <>
      <div className="meter-grid">
        <Cell label="Time to first byte" value={m.ttfb} unit="ms" good={m.ttfb !== null ? m.ttfb < 400 : undefined} />
        <Cell label="Largest contentful paint" value={m.lcp} unit="ms" good={m.lcp !== null ? m.lcp < 2500 : undefined} />
        <Cell label="Page fully loaded" value={m.loaded} unit="ms" good={m.loaded !== null ? m.loaded < 3500 : undefined} />
        <Cell label="Requests, this page" value={m.requestCount} unit="" />
        <Cell label="Transferred over the wire" value={m.transferKB} unit="KB" good={m.transferKB !== null ? m.transferKB < 1200 : undefined} />
      </div>
      <dl className="kv meter-list">
        {headerRow('Content-Security-Policy', m.headers['content-security-policy'] ?? null)}
        {headerRow('Strict-Transport-Security', m.headers['strict-transport-security'] ?? null)}
        {headerRow('X-Content-Type-Options', m.headers['x-content-type-options'] ?? null)}
        {headerRow('X-Frame-Options', m.headers['x-frame-options'] ?? null)}
        {headerRow('Referrer-Policy', m.headers['referrer-policy'] ?? null)}
      </dl>
      <p className="meter-note t-small">Measured live from this browser’s Navigation and Resource Timing APIs, and from this response’s own headers — not a canned number. LCP needs the full page to finish loading, so it appears last.</p>
    </>
  )
}

export const mount: MountFn = (el) => mountReact(el, <VisitMeter />)
