import { useState } from 'react'
import { Wand2, Loader2, Play, Pause, Sparkles, PenLine, Mic, Layers } from 'lucide-react'

// Simple view — a friendly, stripped-down front end for people who just want to
// make a song without the full DAW. Describe a song or hit Surprise me, then one
// big Play button. Shortcut cards jump into the advanced pages when needed.
export default function SimpleStudio({ songState, playing, onPlay, onPause, onSurprise, onCommand, thinking, onOpenAdvanced }) {
  const [text, setText] = useState('')

  const create = () => {
    const t = text.trim()
    if (!t) return
    onCommand(t)
    setText('')
  }

  const shortcuts = [
    { icon: PenLine, label: 'Write lyrics', page: 'lyrics' },
    { icon: Mic, label: 'Edit voice', page: 'goodvoice' },
    { icon: Layers, label: 'More versions', page: 'super' },
  ]

  return (
    <div className="simple-wrap">
      <section className="glass" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20, alignItems: 'center', textAlign: 'center' }}>
        <div>
          <div style={{ fontSize: 22, fontWeight: 700 }}>Make a song</div>
          <div className="mono" style={{ fontSize: 12, color: 'var(--text-dim)', textTransform: 'capitalize', marginTop: 4 }}>
            {songState.genre} · {songState.mood} · {songState.key}
          </div>
        </div>

        {/* Big play button */}
        <button
          type="button"
          onClick={playing ? onPause : onPlay}
          className="btn primary"
          aria-label={playing ? 'Pause' : 'Play'}
          style={{ width: 110, height: 110, borderRadius: '50%', padding: 0, justifyContent: 'center' }}
        >
          {playing ? <Pause size={44} /> : <Play size={44} style={{ marginLeft: 6 }} />}
        </button>
        <div className="mono" style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: -8 }}>
          {playing ? 'Playing — tap to pause' : 'Tap to play your song'}
        </div>

        {/* Describe a song */}
        <div style={{ width: '100%', maxWidth: 520, display: 'flex', flexDirection: 'column', gap: 10 }}>
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && create()}
            placeholder="Describe your song… e.g. “upbeat summer pop with piano”"
            style={{
              padding: '14px 16px',
              borderRadius: 12,
              background: 'var(--panel-solid)',
              border: '1px solid var(--border)',
              color: 'var(--text)',
              fontSize: 15,
              fontFamily: 'inherit',
              textAlign: 'center',
            }}
          />
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button className="btn" onClick={create} disabled={thinking || !text.trim()} style={{ opacity: text.trim() ? 1 : 0.5 }}>
              {thinking ? <Loader2 size={15} className="spin" /> : <Wand2 size={15} />} Create
            </button>
            <button className="btn primary" onClick={onSurprise} disabled={thinking}>
              {thinking ? <Loader2 size={15} className="spin" /> : <Sparkles size={15} />} Surprise me
            </button>
          </div>
        </div>
      </section>

      {/* Quick shortcuts into the advanced pages */}
      <div className="simple-shortcuts">
        {shortcuts.map(({ icon: Icon, label, page }) => (
          <button key={page} type="button" className="glass simple-card" onClick={() => onOpenAdvanced(page)}>
            <Icon size={22} />
            <span>{label}</span>
          </button>
        ))}
      </div>

      <div className="mono" style={{ fontSize: 10.5, color: 'var(--text-faint)', textAlign: 'center' }}>
        Want the full studio? Tap <strong>Advanced</strong> at the top right.
      </div>
    </div>
  )
}
