/**
 * ⌘K command menu. Loaded on first use (core/command.ts). Fetches the
 * search index once and keeps it for the session; a native <dialog> gives
 * us a focus trap and Esc-to-close for free.
 */
import { createRoot } from 'react-dom/client'
import { useEffect, useMemo, useRef, useState } from 'react'

type Item = { group: string; title: string; url: string; hint?: string; keywords?: string }

let cache: Item[] | null = null
async function loadIndex(): Promise<Item[]> {
  if (cache) return cache
  try {
    const res = await fetch('/api/v1/search-index/')
    const data = await res.json()
    cache = data.items as Item[]
  } catch {
    cache = []
  }
  return cache
}

function matches(item: Item, q: string) {
  const hay = `${item.title} ${item.hint || ''} ${item.keywords || ''}`.toLowerCase()
  return q.split(/\s+/).filter(Boolean).every((term) => hay.includes(term))
}

function Menu({ dialog, items }: { dialog: HTMLDialogElement; items: Item[] }) {
  const [query, setQuery] = useState('')
  const [index, setIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const results = useMemo(() => {
    const q = query.trim().toLowerCase()
    const filtered = q ? items.filter((i) => matches(i, q)) : items.slice(0, 8)
    const groups: Record<string, Item[]> = {}
    filtered.forEach((i) => { (groups[i.group] ||= []).push(i) })
    return groups
  }, [items, query])
  const flat = useMemo(() => Object.values(results).flat(), [results])

  // Reset the selection to the top whenever the query changes the result
  // set — this is "adjusting state during render" (React's own recommended
  // shape for this), not a side effect, so it runs synchronously before
  // paint instead of as an extra post-commit render via useEffect.
  const [queryAtLastReset, setQueryAtLastReset] = useState(query)
  if (query !== queryAtLastReset) {
    setQueryAtLastReset(query)
    setIndex(0)
  }

  useEffect(() => { inputRef.current?.focus() }, [])

  const go = (item: Item) => {
    dialog.close()
    if (item.url.startsWith('http') || item.url.startsWith('mailto:')) window.open(item.url, item.url.startsWith('mailto:') ? '_self' : '_blank', 'noopener')
    else window.location.href = item.url
  }

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setIndex((i) => Math.min(i + 1, flat.length - 1)) }
    if (e.key === 'ArrowUp') { e.preventDefault(); setIndex((i) => Math.max(i - 1, 0)) }
    if (e.key === 'Enter' && flat[index]) { e.preventDefault(); go(flat[index]) }
  }

  let cursor = -1
  return (
    <>
      <input ref={inputRef} className="cmdk__input" type="text" placeholder="Search pages, capabilities, work, journal…"
        aria-label="Search" role="combobox" aria-expanded="true" aria-controls="cmdk-list"
        value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={onKeyDown} />
      <ul className="cmdk__list" id="cmdk-list" role="listbox">
        {flat.length === 0 && <li className="cmdk__empty">No results for “{query}”.</li>}
        {Object.entries(results).map(([group, list]) => (
          <li key={group} role="presentation">
            <p className="cmdk__group">{group}</p>
            <ul role="group" aria-label={group} style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {list.map((item) => {
                cursor += 1
                const pos = cursor
                return (
                  <li key={item.url + item.title} role="option" aria-selected={pos === index}
                    className="cmdk__item" onMouseEnter={() => setIndex(pos)} onClick={() => go(item)}>
                    <span>{item.title}</span>
                    {item.hint && <small>{item.hint}</small>}
                  </li>
                )
              })}
            </ul>
          </li>
        ))}
      </ul>
      <div className="cmdk__foot">
        <span><kbd>↑↓</kbd> navigate</span>
        <span><kbd>↵</kbd> open</span>
        <span><kbd>esc</kbd> close</span>
      </div>
    </>
  )
}

export function createCommandMenu(): () => void {
  const dialog = document.createElement('dialog')
  dialog.className = 'cmdk'
  dialog.setAttribute('aria-label', 'Search')
  document.body.appendChild(dialog)
  const root = createRoot(dialog)
  let opened = false

  dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close() })
  dialog.addEventListener('close', () => { window.__lenis?.start() })

  return () => {
    if (!opened) {
      opened = true
      loadIndex().then((items) => root.render(<Menu dialog={dialog} items={items} />))
    }
    if (!dialog.open) { dialog.showModal(); window.__lenis?.stop() }
  }
}
