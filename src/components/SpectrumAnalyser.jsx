import { useEffect, useRef } from 'react'

// Canvas spectrum analyser fed by the engine's AnalyserNode. Renders neon bars
// that react to the live audio; falls back to a calm idle shimmer when stopped.

export default function SpectrumAnalyser({ getSpectrum, playing, height = 56 }) {
  const canvasRef = useRef(null)
  const rafRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let t = 0

    const draw = () => {
      const dpr = window.devicePixelRatio || 1
      const w = canvas.clientWidth
      const h = canvas.clientHeight
      if (canvas.width !== w * dpr || canvas.height !== h * dpr) {
        canvas.width = w * dpr
        canvas.height = h * dpr
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, w, h)

      let spectrum = (playing && getSpectrum && getSpectrum()) || []
      const bars = 48
      if (!spectrum.length) {
        spectrum = Array.from({ length: bars }, (_, i) => 0.08 + 0.06 * Math.sin(t / 18 + i / 3))
      }
      const step = spectrum.length / bars
      const barW = w / bars

      for (let i = 0; i < bars; i++) {
        const v = spectrum[Math.floor(i * step)] ?? 0
        const bh = Math.max(2, v * h)
        const x = i * barW
        const hue = 180 + (i / bars) * 140 // cyan -> magenta
        const grad = ctx.createLinearGradient(0, h, 0, h - bh)
        grad.addColorStop(0, `hsla(${hue}, 100%, 60%, 0.95)`)
        grad.addColorStop(1, `hsla(${hue + 30}, 100%, 70%, 0.35)`)
        ctx.fillStyle = grad
        ctx.fillRect(x + barW * 0.15, h - bh, barW * 0.7, bh)
      }
      t++
      rafRef.current = requestAnimationFrame(draw)
    }
    draw()
    return () => cancelAnimationFrame(rafRef.current)
  }, [getSpectrum, playing])

  return (
    <canvas
      ref={canvasRef}
      style={{ width: '100%', height, display: 'block', borderRadius: 8 }}
      aria-hidden="true"
    />
  )
}
