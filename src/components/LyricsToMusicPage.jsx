import { useState } from 'react'
import { Wand2, Sparkles, Loader2, Play, Mic, Square } from 'lucide-react'
import { generateSongFromLyrics } from '../lib/aiProducer.js'
import { useClipRecorder } from '../hooks/useClipRecorder.js'

// Lyrics → Music: paste lyrics, get 3 song versions built to fit them.
// Structure is read from [Section] headers; mood is inferred from the words.
export default function LyricsToMusicPage({ songState, onApply, onRecord }) {
  const [lyrics, setLyrics] = useState(songState.lyrics || '')
  const [versions, setVersions] = useState([])
  const [busy, setBusy] = useState(false)
  const [voiceClip, setVoiceClip] = useState(null)
  const voice = useClipRecorder({
    maxMs: 15000,
    onClip: (clip) => {
      setVoiceClip(clip)
      onRecord?.(clip)
    },
  })

  const generate = async () => {
    if (!lyrics.trim()) return
    setBusy(true)
    await new Promise((r) => setTimeout(r, 700))
    setVersions(generateSongFromLyrics(lyrics, songState, 3))
    setBusy(false)
  }

  return (
    <section className="glass page-pane" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Wand2 size={18} style={{ color: 'var(--neon-pink)' }} />
        <span style={{ fontSize: 17, fontWeight: 700 }}>Lyrics → Music</span>
      </div>

      <p style={{ color: 'var(--text-dim)', fontSize: 13.5, lineHeight: 1.6, margin: 0 }}>
        Paste your lyrics and get <strong>3 song versions</strong> built to fit them — the structure follows your
        <span className="mono" style={{ color: 'var(--text)' }}> [Section] </span>
        headers and the vibe is read from the words. Tap a version to load it.
      </p>

      <textarea
        value={lyrics}
        onChange={(e) => setLyrics(e.target.value)}
        placeholder={'Paste lyrics here. Use headers like:\n[Verse]\n...\n[Chorus]\n...'}
        spellCheck
        style={{
          minHeight: 160,
          resize: 'vertical',
          padding: 14,
          borderRadius: 12,
          background: 'var(--panel-solid)',
          border: '1px solid var(--border)',
          color: 'var(--text)',
          fontSize: 14,
          lineHeight: 1.6,
          fontFamily: 'inherit',
          whiteSpace: 'pre-wrap',
        }}
      />

      <button className="btn" onClick={generate} disabled={busy || !lyrics.trim()} style={{ alignSelf: 'flex-start', opacity: lyrics.trim() ? 1 : 0.5 }}>
        {busy ? <Loader2 size={15} className="spin" /> : <Sparkles size={15} />}
        {busy ? 'Composing…' : versions.length ? 'Regenerate 3 versions' : 'Generate 3 versions'}
      </button>

      <div className="version-grid">
        {versions.map((v) => (
          <button key={v.id} type="button" className="version-card" onClick={() => onApply(v.changes)}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
              <span style={{ fontSize: 14, fontWeight: 700, textTransform: 'capitalize' }}>{v.label}</span>
              <Play size={14} style={{ color: 'var(--neon-pink)', flexShrink: 0 }} />
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

      <div className="mono" style={{ fontSize: 9.5, color: 'var(--text-faint)' }}>
        Note: this composes a backing arrangement that fits your lyrics — it doesn't sing them.
      </div>

      {/* 15-second voice take */}
      <div style={{ borderTop: '1px solid var(--border)', paddingTop: 14, display: 'flex', flexDirection: 'column', gap: 10 }}>
        <span className="label">Sing it · 15-second take</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            type="button"
            onClick={() => (voice.recording ? voice.stop() : voice.start())}
            disabled={!voice.supported}
            aria-label={voice.recording ? 'Stop' : 'Record 15 seconds'}
            style={{
              width: 54,
              height: 54,
              borderRadius: '50%',
              display: 'grid',
              placeItems: 'center',
              flexShrink: 0,
              cursor: voice.supported ? 'pointer' : 'not-allowed',
              border: `2px solid ${voice.recording ? '#ff2d5a' : 'rgba(255,45,149,0.5)'}`,
              background: voice.recording
                ? `radial-gradient(circle, rgba(255,45,90,${0.25 + voice.level * 0.5}), rgba(255,45,90,0.08))`
                : 'radial-gradient(circle, rgba(255,45,149,0.18), rgba(177,76,255,0.08))',
              color: voice.recording ? '#ff6b85' : 'var(--neon-pink)',
              opacity: voice.supported ? 1 : 0.45,
            }}
          >
            {voice.recording ? <Square size={18} /> : <Mic size={20} />}
          </button>
          <div style={{ fontSize: 12.5, color: 'var(--text-dim)' }}>
            {!voice.supported
              ? 'Mic not available here.'
              : voice.recording
                ? `Recording… ${voice.elapsed.toFixed(1)}s / 15s`
                : 'Record up to 15 seconds of you singing.'}
          </div>
        </div>
        {voiceClip && <audio src={voiceClip.url} controls style={{ width: '100%', height: 34 }} />}
        <div className="mono" style={{ fontSize: 9.5, color: 'var(--text-faint)', lineHeight: 1.5 }}>
          Saved to Studio Real — toggle “Play with song” there to hear it over the track. Making it
          actually sing your lyrics in your voice needs an AI voice model (coming later).
        </div>
      </div>
    </section>
  )
}
