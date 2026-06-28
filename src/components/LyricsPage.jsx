import { useState } from 'react'
import { PenLine, Sparkles, Trash2, Loader2, Upload } from 'lucide-react'
import { generateLyricsLocal } from '../lib/aiProducer.js'
import { GENRES, MOODS, KEYS } from '../lib/constants.js'

// Lyrics AI page. Title (woven into the lyrics), editable genre/mood/key, the
// instruments in use, a generate button + editable sheet, and a drop/choose box
// to base lyrics on a song file. Everything lives in songState, so it autosaves.

const selectStyle = {
  padding: '9px 10px',
  borderRadius: 9,
  background: 'var(--panel-solid)',
  border: '1px solid var(--border)',
  color: 'var(--text)',
  fontSize: 13,
  width: '100%',
  textTransform: 'capitalize',
}

function Field({ label, value, options, onChange }) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 5, flex: 1, minWidth: 120 }}>
      <span className="label">{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)} style={selectStyle}>
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  )
}

export default function LyricsPage({ songState, onChange, onSettings }) {
  const [title, setTitle] = useState('')
  const [busy, setBusy] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const lyrics = songState.lyrics || ''
  const instruments = [...new Set((songState.tracks || []).map((t) => t.instrument))]

  const generate = async (overrideTitle) => {
    const t = overrideTitle != null ? overrideTitle : title
    setBusy(true)
    await new Promise((r) => setTimeout(r, 320))
    onChange(generateLyricsLocal(songState, t))
    setBusy(false)
  }

  const useFile = (file) => {
    if (!file) return
    const name = file.name.replace(/\.[^/.]+$/, '').replace(/[_-]+/g, ' ').trim()
    setTitle(name)
    generate(name)
  }

  return (
    <section className="glass page-pane" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <PenLine size={18} style={{ color: 'var(--neon-purple)' }} />
        <span style={{ fontSize: 17, fontWeight: 700 }}>Lyrics AI</span>
      </div>

      {/* Title (woven into the lyrics) */}
      <label style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
        <span className="label">Title</span>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Song title — e.g. Midnight Drive, Golden Hour"
          onKeyDown={(e) => e.key === 'Enter' && generate()}
          style={{ ...selectStyle, textTransform: 'none' }}
        />
      </label>

      {/* Editable song settings (these change the song too) */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        <Field label="Genre" value={songState.genre} options={GENRES} onChange={(v) => onSettings({ genre: v })} />
        <Field label="Mood" value={songState.mood} options={MOODS} onChange={(v) => onSettings({ mood: v })} />
        <Field label="Key" value={songState.key} options={KEYS} onChange={(v) => onSettings({ key: v })} />
      </div>

      {/* Instruments in use (change them on the Instruments page) */}
      {instruments.length > 0 && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
          <span className="label">Instruments</span>
          {instruments.map((i) => (
            <span
              key={i}
              className="mono"
              style={{ fontSize: 9.5, padding: '2px 8px', borderRadius: 99, background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)', color: 'var(--text-dim)', textTransform: 'capitalize' }}
            >
              {i}
            </span>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <button className="btn" onClick={() => generate()} disabled={busy} style={{ whiteSpace: 'nowrap' }}>
          {busy ? <Loader2 size={15} className="spin" /> : <Sparkles size={15} />}
          {busy ? 'Writing…' : 'Generate'}
        </button>
        <button className="btn" onClick={() => onChange('')} disabled={!lyrics} title="Clear lyrics" style={{ opacity: lyrics ? 1 : 0.4 }}>
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
          minHeight: 200,
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

      {/* Drop / choose a song file to base lyrics on */}
      <label
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          useFile(e.dataTransfer.files?.[0])
        }}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 10,
          padding: '16px 14px',
          borderRadius: 12,
          border: `1.5px dashed ${dragOver ? 'var(--neon-purple)' : 'var(--border)'}`,
          background: dragOver ? 'rgba(62,166,255,0.08)' : 'rgba(255,255,255,0.02)',
          color: 'var(--text-dim)',
          fontSize: 13,
          cursor: 'pointer',
          textAlign: 'center',
        }}
      >
        <Upload size={16} style={{ flexShrink: 0 }} />
        <span>
          Drop or choose a song file → lyrics titled after it, matched to your genre &amp; mood.
        </span>
        <input type="file" accept="audio/*" hidden onChange={(e) => useFile(e.target.files?.[0])} />
      </label>
      <div className="mono" style={{ fontSize: 9.5, color: 'var(--text-faint)' }}>
        Note: the audio itself isn't transcribed — lyrics are written from the title, genre and mood.
      </div>
    </section>
  )
}
