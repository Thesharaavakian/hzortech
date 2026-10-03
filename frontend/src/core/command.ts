/** ⌘K / Ctrl+K opens the command menu; its chunk loads on first use only. */
let opener: Promise<(q?: string) => void> | null = null

const load = () => (opener ||= import('../islands/command-menu').then((m) => m.createCommandMenu()))

export function initCommand(): void {
  const open = () => load().then((fn) => fn())
  document.querySelectorAll('[data-command-open]').forEach((b) => b.addEventListener('click', open))
  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); open() }
    if (e.key === '/' && !(e.target as HTMLElement).closest('input, textarea, select, [contenteditable]')) { e.preventDefault(); open() }
  })
  // Warm the chunk when the pointer approaches a trigger.
  document.querySelectorAll('[data-command-open]').forEach((b) => b.addEventListener('pointerenter', () => { load() }, { once: true }))
}
