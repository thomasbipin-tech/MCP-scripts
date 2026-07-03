import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  // Relative base so the built site works under a GitHub Pages project subpath
  // (https://<user>.github.io/<repo>/) without hardcoding the repo name.
  base: './',
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
