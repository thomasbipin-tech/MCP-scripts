import { useCallback, useRef, useState } from 'react'

// Captures microphone audio via MediaRecorder while sampling the live amplitude
// envelope with an AnalyserNode. On stop it returns a normalized waveform (for
// drawing) and a coarse pitch/loudness contour (used to shape the generated
// melody).

export function useHumRecorder() {
  const supported =
    typeof navigator !== 'undefined' && !!navigator.mediaDevices && !!window.MediaRecorder

  const [recording, setRecording] = useState(false)
  const [waveform, setWaveform] = useState([]) // 0..1 amplitude samples
  const [error, setError] = useState(null)
  const [level, setLevel] = useState(0) // live mic level 0..1

  const mediaRecorderRef = useRef(null)
  const streamRef = useRef(null)
  const audioCtxRef = useRef(null)
  const analyserRef = useRef(null)
  const rafRef = useRef(null)
  const samplesRef = useRef([])

  const sample = useCallback(() => {
    const analyser = analyserRef.current
    if (!analyser) return
    const buf = new Uint8Array(analyser.fftSize)
    analyser.getByteTimeDomainData(buf)
    let sum = 0
    for (let i = 0; i < buf.length; i++) {
      const v = (buf[i] - 128) / 128
      sum += v * v
    }
    const rms = Math.sqrt(sum / buf.length)
    samplesRef.current.push(rms)
    setLevel(Math.min(1, rms * 3))
    rafRef.current = requestAnimationFrame(sample)
  }, [])

  const start = useCallback(async () => {
    if (!supported || recording) return
    setError(null)
    setWaveform([])
    samplesRef.current = []
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const AudioCtx = window.AudioContext || window.webkitAudioContext
      const ctx = new AudioCtx()
      const src = ctx.createMediaStreamSource(stream)
      const analyser = ctx.createAnalyser()
      analyser.fftSize = 1024
      src.connect(analyser)
      audioCtxRef.current = ctx
      analyserRef.current = analyser

      const recorder = new MediaRecorder(stream)
      mediaRecorderRef.current = recorder
      recorder.start()

      setRecording(true)
      rafRef.current = requestAnimationFrame(sample)
    } catch (e) {
      setError(e.message || 'mic-error')
      setRecording(false)
    }
  }, [supported, recording, sample])

  const stop = useCallback(() => {
    return new Promise((resolve) => {
      if (!recording) {
        resolve({ waveform: [], contour: [] })
        return
      }
      const finish = () => {
        cancelAnimationFrame(rafRef.current)
        const raw = samplesRef.current
        // Downsample to a fixed-width waveform for display.
        const width = 64
        const wf = []
        const bucket = Math.max(1, Math.floor(raw.length / width))
        for (let i = 0; i < width; i++) {
          const slice = raw.slice(i * bucket, (i + 1) * bucket)
          const avg = slice.length ? slice.reduce((a, b) => a + b, 0) / slice.length : 0
          wf.push(Math.min(1, avg * 4))
        }
        setWaveform(wf)
        setRecording(false)
        setLevel(0)

        // Clean up audio resources.
        streamRef.current?.getTracks().forEach((t) => t.stop())
        audioCtxRef.current?.close().catch(() => {})
        streamRef.current = null
        audioCtxRef.current = null
        analyserRef.current = null

        resolve({ waveform: wf, contour: wf })
      }

      const recorder = mediaRecorderRef.current
      if (recorder && recorder.state !== 'inactive') {
        recorder.onstop = finish
        recorder.stop()
      } else {
        finish()
      }
    })
  }, [recording])

  return { supported, recording, waveform, level, error, start, stop }
}
