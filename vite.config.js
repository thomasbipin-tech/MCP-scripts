import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteSingleFile } from 'vite-plugin-singlefile'
import basicSsl from '@vitejs/plugin-basic-ssl'
import { VitePWA } from 'vite-plugin-pwa'

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
    plugins: [
      react(),
      ...(command === 'serve' ? [basicSsl()] : []),
      // Service worker so the installed (Add to Home Screen) app updates itself.
      // registerType 'autoUpdate' + skipWaiting/clientsClaim means a freshly
      // deployed version is picked up and the page reloads on next open — no
      // delete-and-reinstall, no manual cache clearing.
      VitePWA({
        registerType: 'autoUpdate',
        workbox: {
          cleanupOutdatedCaches: true,
          clientsClaim: true,
          skipWaiting: true,
        },
        manifest: {
          name: 'AI Music Studio',
          short_name: 'AI Music Studio',
          description: 'GarageBand style AI DAW — voice commands, hum-to-melody, and a real-time AI producer.',
          theme_color: '#12121a',
          background_color: '#12121a',
          display: 'standalone',
          icons: [{ src: 'favicon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' }],
        },
      }),
    ],
    // host: true binds to 0.0.0.0 so other devices on your LAN (phone, iPad)
    // can reach the app at https://<your-laptop-ip>:5173
    server: { port: 5173, host: true },
    preview: { port: 5173, host: true },
  }
})
