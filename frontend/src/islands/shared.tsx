import { createRoot, type Root } from 'react-dom/client'
import type { Cleanup } from '../core/islands'

/** Mount a React tree into an island element and return a cleanup that
 * unmounts it. Shared so every island file stays a one-liner at the bottom. */
export function mountReact(el: HTMLElement, tree: React.ReactElement): Cleanup {
  const root: Root = createRoot(el)
  root.render(tree)
  return () => root.unmount()
}
