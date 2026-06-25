import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteSingleFile } from 'vite-plugin-singlefile'
import basicSsl from '@vitejs/plugin-basic-ssl'

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
    // basicSsl serves dev/preview over HTTPS with a self-signed cert. iOS Safari
    // only grants microphone access (voice + hum) on a secure origin, so this is
    // what makes those features work from an iPad over the LAN. Only applied when
    // serving — production builds don't need it.
    plugins: [react(), ...(command === 'serve' ? [basicSsl()] : [])],
    // host: true binds to 0.0.0.0 so other devices on your LAN (phone, iPad)
    // can reach the app at https://<your-laptop-ip>:5173
    server: { port: 5173, host: true },
    preview: { port: 5173, host: true },
  }
})
