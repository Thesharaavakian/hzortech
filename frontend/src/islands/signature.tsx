/**
 * Per-discipline "signature" — a small generative diagram unique to each of
 * the ten capability pages, built from the same visual language as the
 * system map (nodes, edges, the brand palette) rather than a stock icon.
 * Pure SVG + CSS animation (see .sig-* in islands.css) — cheap to mount,
 * respects prefers-reduced-motion via the .signature--still class.
 */
import { mountReact } from './shared'
import { reducedMotion } from '../core/prefs'
import type { MountFn } from '../core/islands'

type Props = { variant: string; name: string; layer: string }

const W = 400
const H = 400

function Assembly() {
  const cols = [80, 160, 240, 320]
  return (
    <g className="sig-assembly">
      {cols.map((x, i) => (
        <rect key={x} x={x - 24} y={310 - i * 8} width="48" height="36" rx="2" className="sig-block" style={{ animationDelay: `${i * 0.15}s` }} />
      ))}
      <rect x="56" y="70" width="288" height="150" rx="2" className="sig-frame" />
      <path d="M56 130h288M56 170h288M130 70v150M270 70v150" className="sig-grid-lines" />
    </g>
  )
}
function Tree() {
  return (
    <g className="sig-tree">
      <circle cx="200" cy="90" r="10" className="sig-node" />
      {[100, 200, 300].map((x, i) => (
        <g key={x}>
          <path d={`M200,100 L${x},190`} className="sig-branch" style={{ animationDelay: `${i * 0.1}s` }} />
          <circle cx={x} cy="190" r="8" className="sig-node" style={{ animationDelay: `${i * 0.1}s` }} />
          {[x - 40, x + 40].map((cx, j) => (
            <g key={cx}>
              <path d={`M${x},198 L${cx},290`} className="sig-branch" style={{ animationDelay: `${i * 0.1 + j * 0.08 + 0.15}s` }} />
              <circle cx={cx} cy="290" r="6" className="sig-node" style={{ animationDelay: `${i * 0.1 + j * 0.08 + 0.15}s` }} />
            </g>
          ))}
        </g>
      ))}
    </g>
  )
}
function Packets() {
  const rows = [130, 200, 270]
  return (
    <g className="sig-packets">
      <rect x="40" y="100" width="70" height="200" rx="3" className="sig-frame" />
      <rect x="290" y="100" width="70" height="200" rx="3" className="sig-frame" />
      {rows.map((y, i) => (
        <g key={y}>
          <path d={`M110,${y} H290`} className="sig-wire" />
          <rect x="103" y={y - 6} width="14" height="12" rx="2" className="sig-packet" style={{ animationDelay: `${i * 0.4}s` }} />
        </g>
      ))}
    </g>
  )
}
function Flow() {
  return (
    <g className="sig-flow">
      <circle cx="70" cy="200" r="16" className="sig-node" />
      <rect x="170" y="140" width="60" height="40" rx="4" className="sig-frame" />
      <rect x="170" y="220" width="60" height="40" rx="4" className="sig-frame" />
      <rect x="320" y="180" width="60" height="40" rx="4" className="sig-frame" />
      <path d="M86,200 C130,200 130,160 170,160" className="sig-branch" />
      <path d="M86,200 C130,200 130,240 170,240" className="sig-branch" style={{ animationDelay: '0.15s' }} />
      <path d="M230,160 C280,160 280,200 320,200" className="sig-branch" style={{ animationDelay: '0.3s' }} />
      <path d="M230,240 C280,240 280,200 320,200" className="sig-branch" style={{ animationDelay: '0.45s' }} />
    </g>
  )
}
function Mesh() {
  const pts = [[80, 120], [200, 80], [320, 130], [110, 240], [230, 210], [330, 270], [180, 320]]
  return (
    <g className="sig-mesh">
      {pts.map(([x1, y1], i) => pts.slice(i + 1).map(([x2, y2], j) => (
        Math.hypot(x1 - x2, y1 - y2) < 150 ? <path key={`${i}-${j}`} d={`M${x1},${y1} L${x2},${y2}`} className="sig-wire" /> : null
      )))}
      {pts.map(([x, y], i) => <circle key={i} cx={x} cy={y} r="7" className="sig-node" style={{ animationDelay: `${i * 0.08}s` }} />)}
    </g>
  )
}
function Pipeline() {
  const stages = ['BUILD', 'TEST', 'SCAN', 'SHIP']
  return (
    <g className="sig-pipeline">
      <path d="M40,200 H360" className="sig-wire" />
      {stages.map((s, i) => (
        <g key={s} transform={`translate(${70 + i * 90},200)`}>
          <rect x="-32" y="-24" width="64" height="48" rx="3" className="sig-frame sig-stage" style={{ animationDelay: `${i * 0.25}s` }} />
          <text x="0" y="4" textAnchor="middle" className="sig-label">{s}</text>
        </g>
      ))}
    </g>
  )
}
function Topology() {
  const ring = Array.from({ length: 6 }, (_, i) => {
    const a = (i / 6) * Math.PI * 2 - Math.PI / 2
    return [200 + Math.cos(a) * 110, 200 + Math.sin(a) * 110] as const
  })
  return (
    <g className="sig-topology">
      {ring.map(([x, y], i) => <path key={i} d={`M200,200 L${x},${y}`} className="sig-wire" />)}
      <circle cx="200" cy="200" r="20" className="sig-node sig-node--core" />
      {ring.map(([x, y], i) => <circle key={i} cx={x} cy={y} r="9" className="sig-node" style={{ animationDelay: `${i * 0.1}s` }} />)}
    </g>
  )
}
function Migration() {
  return (
    <g className="sig-migration">
      <rect x="40" y="160" width="90" height="80" rx="3" className="sig-frame" />
      <rect x="270" y="160" width="90" height="80" rx="3" className="sig-frame sig-frame--accent" />
      <path d="M140,200 H260" className="sig-wire" />
      <rect x="130" y="192" width="20" height="16" rx="2" className="sig-packet sig-packet--slide" />
    </g>
  )
}
function Scheduler() {
  const cells = Array.from({ length: 16 }, (_, i) => i)
  return (
    <g className="sig-scheduler">
      {cells.map((i) => {
        const x = 90 + (i % 4) * 60
        const y = 110 + Math.floor(i / 4) * 60
        return <rect key={i} x={x} y={y} width="44" height="44" rx="2" className="sig-cell" style={{ animationDelay: `${(i % 4) * 0.1 + Math.floor(i / 4) * 0.1}s` }} />
      })}
    </g>
  )
}
function Perimeter() {
  return (
    <g className="sig-perimeter">
      <rect x="70" y="70" width="260" height="260" rx="4" className="sig-frame sig-frame--dashed" />
      <path d="M200,120 L260,150 V210 C260,250 234,272 200,288 C166,272 140,250 140,210 V150 Z" className="sig-shield" />
      <path d="M172,206 L192,226 L232,182" className="sig-check" />
    </g>
  )
}

const VARIANTS: Record<string, () => React.ReactElement> = {
  assembly: Assembly, tree: Tree, packets: Packets, flow: Flow, mesh: Mesh,
  pipeline: Pipeline, topology: Topology, migration: Migration, scheduler: Scheduler, perimeter: Perimeter,
}

function Signature({ variant, layer }: Props) {
  const Comp = VARIANTS[variant] || Topology
  const still = reducedMotion()
  return (
    <svg className={`signature__svg sig--${layer}${still ? ' signature--still' : ''}`} viewBox={`0 0 ${W} ${H}`} role="img" aria-hidden="true">
      <Comp />
    </svg>
  )
}

export const mount: MountFn = (el, props) => mountReact(el, <Signature {...(props as unknown as Props)} />)
