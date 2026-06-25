import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteSingleFile } from 'vite-plugin-singlefile'

// https://vitejs.dev/config/
// - default build  → GitHub Pages project site (assets under /MCP-scripts/)
// - mode=singlefile → one self-contained index.html (open directly, no server)
// - dev            → root path for a clean localhost URL
export default defineConfig(({ command, mode }) => {
  if (mode === 'singlefile') {
    return {
      base: './',
      plugins: [react(), viteSingleFile()],
      build: { outDir: 'dist-single', assetsInlineLimit: 100000000 },
    }
  }
  return {
    base: command === 'build' ? '/MCP-scripts/' : '/',
    plugins: [react()],
    server: { port: 5173, host: true },
  }
})
