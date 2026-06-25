import { useCallback, useEffect, useRef, useState } from 'react'

// Thin wrapper around the Web Speech API (SpeechRecognition). Exposes a live
// transcript, listening state, and start/stop controls. Gracefully reports when
// the browser doesn't support it (e.g. Firefox) so the UI can fall back to text.

export function useSpeechRecognition({ onResult } = {}) {
  const SR =
    typeof window !== 'undefined'
      ? window.SpeechRecognition || window.webkitSpeechRecognition
      : null
  const supported = Boolean(SR)

  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState(null)
  const recognitionRef = useRef(null)
  const onResultRef = useRef(onResult)
  onResultRef.current = onResult

  useEffect(() => {
    if (!supported) return
    const recognition = new SR()
    recognition.continuous = false
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onresult = (event) => {
      let interim = ''
      let final = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const chunk = event.results[i][0].transcript
        if (event.results[i].isFinal) final += chunk
        else interim += chunk
      }
      setTranscript(final || interim)
      if (final && onResultRef.current) onResultRef.current(final.trim())
    }
    recognition.onerror = (e) => {
      setError(e.error || 'speech-error')
      setListening(false)
    }
    recognition.onend = () => setListening(false)

    recognitionRef.current = recognition
    return () => {
      try {
        recognition.abort()
      } catch (_) {
        /* noop */
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [supported])

  const start = useCallback(() => {
    if (!recognitionRef.current || listening) return
    setError(null)
    setTranscript('')
    try {
      recognitionRef.current.start()
      setListening(true)
    } catch (_) {
      // start() throws if already started; ignore.
    }
  }, [listening])

  const stop = useCallback(() => {
    if (!recognitionRef.current) return
    try {
      recognitionRef.current.stop()
    } catch (_) {
      /* noop */
    }
    setListening(false)
  }, [])

  return { supported, listening, transcript, error, start, stop, setTranscript }
}
