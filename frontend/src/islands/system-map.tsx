import { useEffect, useMemo, useRef, useState } from 'react'
import { mountReact } from './shared'
import { reducedMotion } from '../core/prefs'
import type { MountFn } from '../core/islands'

const VB_W = 1000
const VB_H = 620

type Node = { id: string; label: string; kind: 'actor' | 'node' | 'store' | 'guard' | 'ext'; layer: string; x: number; y: number; detail: string; service: string | null }
type Scenario = { label: string; summary: string; paths: string[][]; log: string[]; hostile?: string[] }
type Props = {
  nodes: Node[]
  edges: [string, string][]
  scenarios: Record<string, Scenario>
  layers: { key: string; name: string }[]
  services: Record<string, { name: string; url: string }>
}

function edgePath(a: Node, b: Node) {
  const midX = (a.x + b.x) / 2
  return `M${a.x},${a.y} C${midX},${a.y} ${midX},${b.y} ${b.x},${b.y}`
}

function pathEdgeSet(paths: string[][]): Set<string> {
  const set = new Set<string>()
  paths.forEach((p) => { for (let i = 0; i < p.length - 1; i++) set.add(`${p[i]}→${p[i + 1]}`) })
  return set
}
function pathNodeSet(paths: string[][]): Set<string> {
  const set = new Set<string>()
  paths.forEach((p) => p.forEach((n) => set.add(n)))
  return set
}

function SystemMap({ nodes, edges, scenarios, services }: Props) {
  const byId = useMemo(() => Object.fromEntries(nodes.map((n) => [n.id, n])), [nodes])
  const scenarioKeys = useMemo(() => Object.keys(scenarios), [scenarios])
  const [active, setActive] = useState<string>(scenarioKeys[0] || '')
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [visibleLog, setVisibleLog] = useState<number>(0)
  const reduced = useRef(reducedMotion())

  const scenario = scenarios[active]
  const activeEdges = useMemo(() => (scenario ? pathEdgeSet(scenario.paths) : new Set<string>()), [scenario])
  const activeNodes = useMemo(() => (scenario ? pathNodeSet(scenario.paths) : new Set<string>()), [scenario])
  const hostileNodes = useMemo(() => new Set(scenario?.hostile || []), [scenario])

  // The 0-reset when the scenario changes is "adjusting state during
  // render" (React's recommended shape for this, not a side effect); the
  // interval that then streams the log lines in IS a real side effect
  // (a subscription to a timer, an external system), so that part stays in
  // useEffect, started fresh from 0 every time `active` changes.
  const [activeAtLastReset, setActiveAtLastReset] = useState(active)
  if (active !== activeAtLastReset) {
    setActiveAtLastReset(active)
    setVisibleLog(0)
  }

  useEffect(() => {
    if (!scenario) return
    if (reduced.current) { setVisibleLog(scenario.log.length); return }
    let i = 0
    const id = window.setInterval(() => {
      i += 1
      setVisibleLog(i)
      if (i >= scenario.log.length) window.clearInterval(id)
    }, 550)
    return () => window.clearInterval(id)
  }, [active, scenario])

  const detail = selectedNode || (scenario ? byId[scenario.paths[0]?.[scenario.paths[0].length - 1]] : null)

  return (
    <div className="sysmap">
      <div>
        <div className="sysmap__scenarios" role="tablist" aria-label="Scenario">
          {scenarioKeys.map((key) => (
            <button key={key} type="button" role="tab" className="chip" aria-selected={active === key}
              data-active={active === key} onClick={() => { setActive(key); setSelectedNode(null) }}>
              {scenarios[key].label}
            </button>
          ))}
        </div>
        <div className="sysmap__svg-wrap">
          <div className="sysmap__stage" style={{ aspectRatio: `${VB_W} / ${VB_H}` }}>
            <svg className="sysmap__svg" viewBox={`0 0 ${VB_W} ${VB_H}`} role="img" aria-label="System architecture diagram" preserveAspectRatio="none">
              <g>
                {edges.map(([a, b]) => {
                  const from = byId[a]; const to = byId[b]
                  if (!from || !to) return null
                  const key = `${a}→${b}`
                  return <path key={key} className="sysmap__edge" data-active={activeEdges.has(key)} d={edgePath(from, to)} />
                })}
              </g>
            </svg>
            {nodes.map((n) => (
              <button
                key={n.id}
                type="button"
                className="sysmap__node-btn"
                data-layer={n.layer}
                data-active={activeNodes.has(n.id)}
                data-hostile={hostileNodes.has(n.id)}
                aria-pressed={selectedNode?.id === n.id}
                style={{ left: `${(n.x / VB_W) * 100}%`, top: `${(n.y / VB_H) * 100}%` }}
                onClick={() => setSelectedNode(n)}
              >
                {n.label}
              </button>
            ))}
          </div>
        </div>
        <div className="sysmap__legend">
          <span><span className="chip__dot layer-dot" data-layer="product" />Product</span>
          <span><span className="chip__dot layer-dot" data-layer="platform" />Platform</span>
          <span><span className="chip__dot layer-dot" data-layer="automation" />Automation</span>
          <span><span className="chip__dot layer-dot" data-layer="infrastructure" />Infrastructure</span>
          <span><span className="chip__dot layer-dot" data-layer="security" />Security</span>
        </div>
      </div>
      <aside className="sysmap__panel" aria-live="polite">
        {detail ? (
          <>
            <p className="t-mono">{detail.label}</p>
            <p className="t-body">{detail.detail}</p>
            {detail.service && services[detail.service] && (
              <a href={services[detail.service].url}>{services[detail.service].name}<svg width="14" height="14" aria-hidden="true"><use href="#i-arrow" /></svg></a>
            )}
          </>
        ) : (
          <p className="t-body">Select a part of the system, or run a scenario, to see how it works.</p>
        )}
        {scenario && (
          <>
            <p className="t-mono" style={{ marginTop: 8 }}>{scenario.summary}</p>
            <ol className="sysmap__log" role="list">
              {scenario.log.slice(0, visibleLog).map((line, i) => <li key={i}>{line}</li>)}
            </ol>
          </>
        )}
      </aside>
    </div>
  )
}

export const mount: MountFn = (el, props) => mountReact(el, <SystemMap {...(props as unknown as Props)} />)
