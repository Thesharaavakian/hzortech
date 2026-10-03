import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

const src = (p: string) => fileURLToPath(new URL(`./src/${p}`, import.meta.url))

// Django serves the build from /static/dist/ (settings.STATICFILES_DIRS) and
// reads dist/.vite/manifest.json in the {% vite_entry %} template tag. During
// `npm run dev` the tag points at this dev server instead (VITE_DEV_SERVER).
export default defineConfig(({ command }) => ({
  base: command === 'serve' ? '/' : '/static/dist/',
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    manifest: true,
    target: 'es2022',
    sourcemap: false,
    assetsInlineLimit: 0,
    rollupOptions: {
      input: {
        main: src('main.ts'),
        article: src('entries/article.ts'),
      },
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    origin: 'http://localhost:5173',
    cors: true,
  },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.{ts,tsx}'],
  },
}))
