import { useCallback, useRef, useState } from 'react'

// Records real microphone audio into a playable clip. Unlike useHumRecorder
// (which only samples the amplitude envelope), this keeps the recorded audio and
// hands back a Blob + object URL on stop via the onClip callback. Optional maxMs
// auto-stops the take (used for the 15-second voice clip).
export function useClipRecorder({ maxMs, onClip } = {}) {
  const supported =
    typeof navigator !== 'undefined' && !!navigator.mediaDevices && !!window.MediaRecorder

  const [recording, setRecording] = useState(false)
  const [level, setLevel] = useState(0)
  const [elapsed, setElapsed] = useState(0)
  const [error, setError] = useState(null)

  const onClipRef = useRef(onClip)
  onClipRef.current = onClip

  const recorderRef = useRef(null)
  const streamRef = useRef(null)
  const ctxRef = useRef(null)
  const analyserRef = useRef(null)
  const rafRef = useRef(null)
  const chunksRef = useRef([])
  const samplesRef = useRef([])
  const startRef = useRef(0)
  const maxTimerRef = useRef(null)

  const tick = useCallback(() => {
    const analyser = analyserRef.current
    if (analyser) {
      const buf = new Uint8Array(analyser.fftSize)
      analyser.getByteTimeDomainData(buf)
      let sum = 0
      for (let i = 0; i < buf.length; i++) {
        const v = (buf[i] - 128) / 128
        sum += v * v
      }
      samplesRef.current.push(Math.sqrt(sum / buf.length))
      setLevel(Math.min(1, Math.sqrt(sum / buf.length) * 3))
    }
    setElapsed((performance.now() - startRef.current) / 1000)
    rafRef.current = requestAnimationFrame(tick)
  }, [])

  const stop = useCallback(() => {
    const recorder = recorderRef.current
    if (recorder && recorder.state === 'recording') recorder.stop()
  }, [])

  const start = useCallback(async () => {
    if (!supported || recording) return
    setError(null)
    chunksRef.current = []
    samplesRef.current = []
    setElapsed(0)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const AudioCtx = window.AudioContext || window.webkitAudioContext
      const ctx = new AudioCtx()
      const src = ctx.createMediaStreamSource(stream)
      const analyser = ctx.createAnalyser()
      analyser.fftSize = 1024
      src.connect(analyser)
      ctxRef.current = ctx
      analyserRef.current = analyser

      const recorder = new MediaRecorder(stream)
      recorderRef.current = recorder
      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size) chunksRef.current.push(e.data)
      }
      recorder.onstop = () => {
        cancelAnimationFrame(rafRef.current)
        clearTimeout(maxTimerRef.current)
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || 'audio/webm' })
        const url = URL.createObjectURL(blob)
        const duration = (performance.now() - startRef.current) / 1000

        const raw = samplesRef.current
        const width = 48
        const wf = []
        const bucket = Math.max(1, Math.floor(raw.length / width))
        for (let i = 0; i < width; i++) {
          const slice = raw.slice(i * bucket, (i + 1) * bucket)
          const avg = slice.length ? slice.reduce((a, b) => a + b, 0) / slice.length : 0
          wf.push(Math.min(1, avg * 4))
        }

        setRecording(false)
        setLevel(0)
        setElapsed(0)
        streamRef.current?.getTracks().forEach((t) => t.stop())
        ctxRef.current?.close().catch(() => {})
        streamRef.current = null
        ctxRef.current = null
        analyserRef.current = null

        onClipRef.current?.({ blob, url, duration, waveform: wf })
      }

      recorder.start()
      startRef.current = performance.now()
      setRecording(true)
      rafRef.current = requestAnimationFrame(tick)
      if (maxMs) maxTimerRef.current = setTimeout(stop, maxMs)
    } catch (e) {
      setError(e.message || 'mic-error')
      setRecording(false)
    }
  }, [supported, recording, tick, maxMs, stop])

  return { supported, recording, level, elapsed, error, start, stop }
}
