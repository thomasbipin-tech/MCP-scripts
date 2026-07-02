/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['IBM Plex Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      colors: {
        signal: {
          DEFAULT: '#e5484d',
          50: '#fdecec',
          400: '#ef6f73',
          500: '#e5484d',
          600: '#c93a3f',
        },
      },
    },
  },
  plugins: [],
}
