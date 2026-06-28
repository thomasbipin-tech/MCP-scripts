import { useEffect } from 'react'
import { Mic, MicOff, Sparkles, Loader2 } from 'lucide-react'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition.js'

// Feature 1 — Voice Command System. A large central microphone button that
// listens via the Web Speech API, shows a live transcript, and routes the
// recognized command to the AI producer (with an "AI is thinking…" state).

export default function VoicePanel({ onCommand, thinking, liveAI }) {
  const { supported, listening, transcript, error, start, stop } = useSpeechRecognition({
    onResult: (text) => {
      stop()
      onCommand(text)
    },
  })

  // Auto-stop the mic visual once a command is dispatched.
  useEffect(() => {
    if (thinking && listening) stop()
  }, [thinking, listening, stop])

  const toggle = () => (listening ? stop() : start())

  return (
    <section className="glass" style={{ padding: 20, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, alignSelf: 'flex-start' }}>
        <span className="label">Voice Command</span>
        <span
          className="mono"
          style={{
            fontSize: 9,
            padding: '2px 7px',
            borderRadius: 99,
            background: liveAI ? 'rgba(43,166,64,0.12)' : 'rgba(62,166,255,0.1)',
            color: liveAI ? 'var(--neon-green)' : 'var(--neon-blue)',
            border: `1px solid ${liveAI ? 'rgba(43,166,64,0.3)' : 'rgba(62,166,255,0.25)'}`,
          }}
        >
          {liveAI ? 'LIVE AI' : 'AI: BUILT-IN'}
        </span>
      </div>

      <button
        onClick={toggle}
        disabled={!supported || thinking}
        aria-label={listening ? 'Stop listening' : 'Start voice command'}
        style={{
          width: 104,
          height: 104,
          borderRadius: '50%',
          display: 'grid',
          placeItems: 'center',
          background: listening
            ? 'radial-gradient(circle, rgba(255,0,0,0.35), rgba(255,0,0,0.08))'
            : 'radial-gradient(circle, rgba(62,166,255,0.22), rgba(62,166,255,0.1))',
          border: `2px solid ${listening ? '#ff0000' : 'rgba(62,166,255,0.5)'}`,
          color: listening ? '#ff5252' : 'var(--neon-blue)',
          animation: listening ? 'pulse-rec 1.4s infinite' : 'none',
          transition: 'all 300ms ease',
          opacity: !supported ? 0.45 : 1,
        }}
      >
        {thinking ? (
          <Loader2 size={38} className="spin" />
        ) : listening ? (
          <Mic size={40} />
        ) : supported ? (
          <Mic size={40} />
        ) : (
          <MicOff size={40} />
        )}
      </button>

      <div style={{ minHeight: 24, textAlign: 'center', maxWidth: 360 }}>
        {thinking ? (
          <span style={{ color: 'var(--neon-blue)', fontSize: 13, display: 'inline-flex', gap: 6, alignItems: 'center' }}>
            <Sparkles size={14} /> AI is thinking
            <span style={{ animation: 'thinking-dots 1.2s infinite' }}>.</span>
            <span style={{ animation: 'thinking-dots 1.2s infinite 0.2s' }}>.</span>
            <span style={{ animation: 'thinking-dots 1.2s infinite 0.4s' }}>.</span>
          </span>
        ) : transcript ? (
          <span style={{ fontSize: 14, color: 'var(--text)' }}>“{transcript}”</span>
        ) : (
          <span style={{ fontSize: 12.5, color: 'var(--text-faint)' }}>
            {supported
              ? listening
                ? 'Listening… say “add a bass track”'
                : 'Tap the mic and speak a command'
              : 'Voice input unsupported here — use the text box on the right'}
          </span>
        )}
      </div>

      {error && error !== 'no-speech' && (
        <span className="mono" style={{ fontSize: 10, color: '#ff5252' }}>
          mic: {error}
        </span>
      )}
    </section>
  )
}
