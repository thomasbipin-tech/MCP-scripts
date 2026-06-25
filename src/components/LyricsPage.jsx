import { useState } from 'react'
import { PenLine, Sparkles, Trash2, Loader2 } from 'lucide-react'
import { generateLyricsLocal } from '../lib/aiProducer.js'

// Lyrics AI page. Generates a structured lyric sheet from the song's mood and
// structure, fully editable. Lyrics live in songState, so they're preserved
// across page switches and covered by autosave.
export default function LyricsPage({ songState, onChange }) {
  const [theme, setTheme] = useState('')
  const [busy, setBusy] = useState(false)
  const lyrics = songState.lyrics || ''

  const generate = async () => {
    setBusy(true)
    // Small delay so the "writing…" state is visible.
    await new Promise((r) => setTimeout(r, 350))
    onChange(generateLyricsLocal(songState, theme))
    setBusy(false)
  }

  const chip = (text) => (
    <span
      className="mono"
      style={{
        fontSize: 9.5,
        padding: '2px 8px',
        borderRadius: 99,
        background: 'rgba(0,245,255,0.08)',
        border: '1px solid rgba(0,245,255,0.2)',
        color: 'var(--neon-blue)',
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
      }}
    >
      {text}
    </span>
  )

  return (
    <section className="glass page-pane" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <PenLine size={18} style={{ color: 'var(--neon-purple)' }} />
        <span style={{ fontSize: 17, fontWeight: 700 }}>Lyrics AI</span>
      </div>

      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {chip(songState.genre || 'genre')}
        {chip(songState.mood || 'mood')}
        {chip(songState.key || 'key')}
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <input
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
          placeholder="Theme — e.g. midnight drive, lost love, the city"
          onKeyDown={(e) => e.key === 'Enter' && generate()}
          style={{
            flex: 1,
            minWidth: 200,
            padding: '10px 12px',
            borderRadius: 10,
            background: 'var(--panel-solid)',
            border: '1px solid var(--border)',
            color: 'var(--text)',
            fontSize: 14,
          }}
        />
        <button className="btn" onClick={generate} disabled={busy} style={{ whiteSpace: 'nowrap' }}>
          {busy ? <Loader2 size={15} className="spin" /> : <Sparkles size={15} />}
          {busy ? 'Writing…' : 'Generate'}
        </button>
        <button
          className="btn"
          onClick={() => onChange('')}
          disabled={!lyrics}
          title="Clear lyrics"
          style={{ opacity: lyrics ? 1 : 0.4 }}
        >
          <Trash2 size={15} />
        </button>
      </div>

      <textarea
        value={lyrics}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Your lyrics appear here — generate a draft, then edit freely. Everything autosaves."
        spellCheck
        style={{
          flex: 1,
          minHeight: 240,
          resize: 'none',
          padding: 14,
          borderRadius: 12,
          background: 'var(--panel-solid)',
          border: '1px solid var(--border)',
          color: 'var(--text)',
          fontSize: 14.5,
          lineHeight: 1.6,
          fontFamily: 'inherit',
          whiteSpace: 'pre-wrap',
        }}
      />

      <div className="mono" style={{ fontSize: 10, color: 'var(--text-faint)' }}>
        Follows your song structure · saved automatically
      </div>
    </section>
  )
}
