import { useState } from 'react'
import { Layers, Sparkles, Loader2, Play } from 'lucide-react'
import { generateVariations } from '../lib/aiProducer.js'

// Super Generate: from the current song, produce 6 complete versions to browse.
// Tapping a version loads it into the studio.
export default function SuperGeneratePage({ songState, onApply }) {
  const [versions, setVersions] = useState([])
  const [busy, setBusy] = useState(false)

  const generate = async () => {
    setBusy(true)
    // A short beat so the "generating" state reads (and to feel deliberate).
    await new Promise((r) => setTimeout(r, 700))
    setVersions(generateVariations(songState, 6))
    setBusy(false)
  }

  return (
    <section className="glass page-pane" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Layers size={18} style={{ color: 'var(--neon-amber)' }} />
        <span style={{ fontSize: 17, fontWeight: 700 }}>Super Generate</span>
      </div>

      <p style={{ color: 'var(--text-dim)', fontSize: 13.5, lineHeight: 1.6, margin: 0 }}>
        Creates <strong>6 complete versions</strong> of your song — different moods, keys, tempos and
        instrument lineups. Tap any version to load it into the Studio.
      </p>

      <button className="btn" onClick={generate} disabled={busy} style={{ alignSelf: 'flex-start' }}>
        {busy ? <Loader2 size={15} className="spin" /> : <Sparkles size={15} />}
        {busy ? 'Generating…' : versions.length ? 'Regenerate 6 versions' : 'Generate 6 versions'}
      </button>

      <div className="version-grid">
        {versions.map((v) => (
          <button key={v.id} type="button" className="version-card" onClick={() => onApply(v.changes)}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
              <span style={{ fontSize: 14, fontWeight: 700, textTransform: 'capitalize' }}>{v.label}</span>
              <Play size={14} style={{ color: 'var(--neon-amber)', flexShrink: 0 }} />
            </div>
            <div className="mono" style={{ fontSize: 10, color: 'var(--text-dim)' }}>
              {v.key} · {v.bpm} BPM
            </div>
            <div className="mono" style={{ fontSize: 9.5, color: 'var(--text-faint)', textTransform: 'capitalize' }}>
              {v.instruments.join(' · ')}
            </div>
          </button>
        ))}
      </div>

      {!versions.length && !busy && (
        <div className="mono" style={{ fontSize: 10, color: 'var(--text-faint)' }}>
          Tip: set a genre/mood in the top bar first to steer the versions.
        </div>
      )}
    </section>
  )
}
