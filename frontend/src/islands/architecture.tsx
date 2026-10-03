/**
 * Case-study architecture diagram — same visual language as the homepage
 * system map (nodes positioned on a grid, edges between them) but static:
 * no scenarios, just "this is how it's put together."
 */
import { mountReact } from './shared'
import type { MountFn } from '../core/islands'

type Node = { id: string; label: string; layer: string; x: number; y: number; detail?: string }
type Props = { nodes: Node[]; edges: [string, string][]; title: string }

const VB_W = 1000
const VB_H = 560

function edgePath(a: Node, b: Node) {
  const midX = (a.x + b.x) / 2
  return `M${a.x},${a.y} C${midX},${a.y} ${midX},${b.y} ${b.x},${b.y}`
}

function Architecture({ nodes, edges, title }: Props) {
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]))
  return (
    <div className="arch__stage" style={{ aspectRatio: `${VB_W} / ${VB_H}`, position: 'relative' }}>
      <svg className="arch__svg" viewBox={`0 0 ${VB_W} ${VB_H}`} role="img" aria-label={title} style={{ position: 'absolute', inset: 0 }}>
        <g>{edges.map(([a, b]) => {
          const from = byId[a]; const to = byId[b]
          if (!from || !to) return null
          return <path key={`${a}-${b}`} className="arch__edge" d={edgePath(from, to)} />
        })}</g>
      </svg>
      {nodes.map((n) => (
        <div key={n.id} className="sysmap__node-btn" data-layer={n.layer} title={n.detail}
          style={{ position: 'absolute', left: `${(n.x / VB_W) * 100}%`, top: `${(n.y / VB_H) * 100}%`, transform: 'translate(-50%, -50%)', cursor: n.detail ? 'help' : 'default' }}>
          {n.label}
        </div>
      ))}
    </div>
  )
}

export const mount: MountFn = (el, props) => mountReact(el, <Architecture {...(props as unknown as Props)} />)
