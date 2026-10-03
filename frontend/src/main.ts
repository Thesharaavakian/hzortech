import '@fontsource-variable/archivo/wdth.css'
import '@fontsource-variable/jetbrains-mono/wght.css'
import '@fontsource/noto-sans-armenian/armenian-800.css'
import './styles/main.css'

import { initTheme } from './core/theme'
import { initHeader } from './core/header'
import { initMotion } from './core/motion'
import { initIslands } from './core/islands'
import { initConsent } from './core/consent'
import { initCommand } from './core/command'

function boot() {
  document.documentElement.classList.add('motion-ready')
  initTheme()
  initHeader()
  initConsent()
  initCommand()
  initMotion()
  initIslands()
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true })
else boot()
