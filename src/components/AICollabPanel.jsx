import { useEffect, useRef, useState } from 'react'
import { Send, Lightbulb, ArrowRight, Bot, User, Sparkles } from 'lucide-react'

// Feature 5 — AI Collaboration Panel. The AI producer's chat log: every command
// and the AI's reply (what changed + a production tip + a next step), plus a
// text-input fallback. Has the spec's subtle scanline effect.

export default function AICollabPanel({ log, onCommand, thinking }) {
  const [text, setText] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [log, thinking])

  const submit = (e) => {
    e.preventDefault()
    const cmd = text.trim()
    if (!cmd || thinking) return
    onCommand(cmd)
    setText('')
  }

  return (
    <section
      className="glass scanlines"
      style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}
    >
      <div
        style={{
          padding: '14px 16px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          position: 'relative',
          zIndex: 2,
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 9,
            display: 'grid',
            placeItems: 'center',
            background: 'linear-gradient(135deg, var(--neon-blue), var(--neon-purple))',
            color: '#0a0a0f',
          }}
        >
          <Bot size={18} />
        </div>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700 }}>AI Producer</div>
          <div className="mono" style={{ fontSize: 9, color: 'var(--text-faint)', textTransform: 'uppercase' }}>
            your studio collaborator
          </div>
        </div>
      </div>

      <div
        ref={scrollRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: 16,
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
          position: 'relative',
          zIndex: 2,
        }}
      >
        {log.length === 0 && (
          <div style={{ color: 'var(--text-faint)', fontSize: 13, lineHeight: 1.6, marginTop: 8 }}>
            <Sparkles size={16} style={{ color: 'var(--neon-blue)' }} />
            <p style={{ marginTop: 8 }}>
              I'm your AI producer. Tell me what to build and I'll shape the track with you —
              adding layers, tweaking tempo, applying FX, and arranging sections.
            </p>
            <p style={{ marginTop: 10, color: 'var(--text-dim)' }}>Try:</p>
            <ul style={{ marginLeft: 16, marginTop: 4, color: 'var(--text-dim)' }}>
              <li>“add a drum track”</li>
              <li>“make the chorus repeat 4 times”</li>
              <li>“speed up tempo to 140 BPM”</li>
              <li>“make it heavier”</li>
            </ul>
          </div>
        )}

        {log.map((entry, i) =>
          entry.role === 'user' ? (
            <div key={i} className="fade-in" style={{ alignSelf: 'flex-end', maxWidth: '85%' }}>
              <div
                style={{
                  background: 'rgba(0,245,255,0.12)',
                  border: '1px solid rgba(0,245,255,0.28)',
                  borderRadius: '12px 12px 2px 12px',
                  padding: '8px 12px',
                  fontSize: 13,
                  display: 'flex',
                  gap: 8,
                  alignItems: 'center',
                }}
              >
                <User size={13} style={{ color: 'var(--neon-blue)', flexShrink: 0 }} />
                {entry.command}
              </div>
            </div>
          ) : (
            <div key={i} className="fade-in" style={{ alignSelf: 'flex-start', maxWidth: '92%' }}>
              <div
                style={{
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid var(--border)',
                  borderRadius: '12px 12px 12px 2px',
                  padding: '10px 12px',
                  fontSize: 13,
                  lineHeight: 1.5,
                }}
              >
                <div>{entry.message}</div>
                {entry.tip && (
                  <div
                    style={{
                      marginTop: 8,
                      paddingTop: 8,
                      borderTop: '1px solid var(--border)',
                      display: 'flex',
                      gap: 7,
                      color: 'var(--neon-amber)',
                      fontSize: 12,
                    }}
                  >
                    <Lightbulb size={13} style={{ flexShrink: 0, marginTop: 2 }} />
                    <span style={{ color: 'var(--text-dim)' }}>{entry.tip}</span>
                  </div>
                )}
                {entry.nextSuggestion && (
                  <div
                    style={{
                      marginTop: 6,
                      display: 'flex',
                      gap: 7,
                      color: 'var(--neon-green)',
                      fontSize: 12,
                    }}
                  >
                    <ArrowRight size={13} style={{ flexShrink: 0, marginTop: 2 }} />
                    <span style={{ color: 'var(--text-dim)' }}>{entry.nextSuggestion}</span>
                  </div>
                )}
              </div>
            </div>
          ),
        )}

        {thinking && (
          <div style={{ alignSelf: 'flex-start', display: 'flex', gap: 6, alignItems: 'center', color: 'var(--neon-blue)', fontSize: 13 }}>
            <Bot size={15} /> thinking
            <span style={{ animation: 'thinking-dots 1.2s infinite' }}>.</span>
            <span style={{ animation: 'thinking-dots 1.2s infinite 0.2s' }}>.</span>
            <span style={{ animation: 'thinking-dots 1.2s infinite 0.4s' }}>.</span>
          </div>
        )}
      </div>

      <form
        onSubmit={submit}
        style={{
          padding: 12,
          borderTop: '1px solid var(--border)',
          display: 'flex',
          gap: 8,
          position: 'relative',
          zIndex: 2,
        }}
      >
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type a command…"
          style={{
            flex: 1,
            background: 'rgba(0,0,0,0.3)',
            border: '1px solid var(--border)',
            borderRadius: 9,
            padding: '9px 12px',
            fontSize: 13,
            outline: 'none',
          }}
        />
        <button type="submit" className="btn primary" disabled={thinking || !text.trim()} aria-label="Send command">
          <Send size={15} />
        </button>
      </form>
    </section>
  )
}
