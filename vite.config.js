import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
// On a production build (e.g. GitHub Pages project site) assets are served from
// /MCP-scripts/; in dev we stay at the root for a clean localhost URL.
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/MCP-scripts/' : '/',
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
  },
}))
