import { useEffect, useRef, useState } from 'react'
import { Mic, Square, Play, Sparkles, Users, Sparkle, Radio, Trash2, Download, AudioLines } from 'lucide-react'
import { getEngine } from '../lib/audioEngine.js'
import { useClipRecorder } from '../hooks/useClipRecorder.js'

// Good Voice — a real recording booth (like Studio Real) with vocal polish.
// Record as many takes as you want with browser noise-suppression, keep them in
// a list (download / delete / play over the song), and play any take through a
// "vibe" (Crystal Clear / Rockstar / On Stage) plus a simulated group of
// backing singers.
const VIBES = [
  { id: 'clean', label: 'Crystal Clear', icon: Sparkle, desc: 'Clean, present, polished.' },
  { id: 'rockstar', label: 'Rockstar', icon: Sparkles, desc: 'Saturated, gritty, in-your-face.' },
  { id: 'stage', label: 'On Stage', icon: Radio, desc: 'Big arena reverb + echo.' },
]

export default function GoodVoicePage({ recordings, onAdd, onRemove, onTogglePlay }) {
  const engine = getEngine()
  const [vibe, setVibe] = useState('clean')
  const [singers, setSingers] = useState(1)
  const [activeId, setActiveId] = useState(null) // take currently playing through the vibe
  const genRef = useRef(0)

  const recorder = useClipRecorder({
    constraints: { noiseSuppression: true, echoCancellation: true, autoGainControl: true },
    onClip: (c) => {
      genRef.current += 1
      engine.stopVocal()
      setActiveId(null)
      onAdd?.(c)
    },
  })

  const play = async (rec) => {
    if (!rec) return
    const my = (genRef.current += 1)
    setActiveId(rec.id)
    await engine.playVocal(rec.url, { vibe, singers }, () => {
      if (genRef.current === my) setActiveId(null)
    })
  }

  const stop = () => {
    genRef.current += 1
    engine.stopVocal()
    setActiveId(null)
  }

  const activeRec = recordings.find((r) => r.id === activeId) || null

  // Re-apply live when the vibe or singer count changes mid-playback.
  useEffect(() => {
    if (activeRec) play(activeRec)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vibe, singers])

  // Stop vibe audio when leaving the page.
  useEffect(() => {
    return () => {
      genRef.current += 1
      engine.stopVocal()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <section className="glass page-pane" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Mic size={18} style={{ color: 'var(--neon-green)' }} />
        <span style={{ fontSize: 17, fontWeight: 700 }}>Good Voice</span>
        <span className="mono" style={{ fontSize: 9, color: 'var(--text-faint)', textTransform: 'uppercase' }}>recording booth</span>
      </div>
      <p style={{ color: 'var(--text-dim)', fontSize: 13.5, lineHeight: 1.6, margin: 0 }}>
        Record your song — background noise is cleaned up automatically. Keep as many takes as you like, then play any
        one through a vibe and a crowd of backing singers, or over your track. <strong>Tip:</strong> use headphones so
        only your voice is recorded.
      </p>

      {/* Record */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
        <button
          type="button"
          onClick={() => (recorder.recording ? recorder.stop() : recorder.start())}
          disabled={!recorder.supported}
          aria-label={recorder.recording ? 'Stop' : 'Record'}
          className={`rec-btn${recorder.recording ? ' active' : ''}`}
          style={{ width: 84, height: 84 }}
        >
          {recorder.recording ? <Square size={28} /> : <Mic size={32} />}
        </button>
        <div className="mono" style={{ fontSize: 11, color: recorder.recording ? '#ff5252' : 'var(--text-faint)' }}>
          {!recorder.supported
            ? 'Mic not available here'
            : recorder.recording
              ? `● REC  ${recorder.elapsed.toFixed(1)}s`
              : recordings.length
                ? 'Tap to record another take'
                : 'Tap to record your song'}
        </div>
        {recorder.error && recorder.error !== 'no-speech' && (
          <span className="mono" style={{ fontSize: 10, color: '#ff5252' }}>mic: {recorder.error}</span>
        )}
      </div>

      {recordings.length > 0 && (
        <>
          {/* Vibe */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <span className="label">Vibe</span>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {VIBES.map((v) => {
                const Icon = v.icon
                const on = vibe === v.id
                return (
                  <button
                    key={v.id}
                    type="button"
                    onClick={() => setVibe(v.id)}
                    title={v.desc}
                    style={{
                      flex: 1,
                      minWidth: 110,
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 4,
                      padding: 12,
                      borderRadius: 11,
                      cursor: 'pointer',
                      textAlign: 'left',
                      background: on ? 'rgba(43,166,64,0.1)' : 'rgba(255,255,255,0.04)',
                      border: `1px solid ${on ? 'var(--neon-green)' : 'var(--border)'}`,
                      color: on ? 'var(--neon-green)' : 'var(--text-dim)',
                    }}
                  >
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 700, fontSize: 13 }}>
                      <Icon size={15} /> {v.label}
                    </span>
                    <span className="mono" style={{ fontSize: 9.5, color: 'var(--text-faint)' }}>{v.desc}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Backing singers */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <span className="label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Users size={12} /> Backing singers · {singers === 1 ? 'just you' : `${singers} voices`}
            </span>
            <input type="range" min="1" max="500" step="1" value={singers} onChange={(e) => setSingers(Number(e.target.value))} />
          </div>

          {/* Takes list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <span className="label">Takes</span>
            {recordings.map((rec) => {
              const isPlaying = activeId === rec.id
              return (
                <div
                  key={rec.id}
                  style={{ padding: 12, borderRadius: 12, background: 'rgba(10,10,16,0.55)', border: `1px solid ${isPlaying ? 'var(--neon-green)' : 'var(--border)'}`, display: 'flex', flexDirection: 'column', gap: 10 }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <AudioLines size={15} style={{ color: 'var(--neon-green)' }} />
                    <span style={{ fontSize: 13.5, fontWeight: 700 }}>{rec.name}</span>
                    <span className="mono" style={{ fontSize: 10, color: 'var(--text-faint)' }}>{rec.duration.toFixed(1)}s</span>
                    <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
                      <a
                        href={rec.url}
                        download={`${rec.name}.webm`}
                        title="Download"
                        style={{ width: 30, height: 30, borderRadius: 7, display: 'grid', placeItems: 'center', border: '1px solid var(--border)', color: 'var(--text-dim)' }}
                      >
                        <Download size={14} />
                      </a>
                      <button
                        onClick={() => {
                          if (isPlaying) stop()
                          onRemove(rec.id)
                        }}
                        title="Delete"
                        style={{ width: 30, height: 30, borderRadius: 7, display: 'grid', placeItems: 'center', border: '1px solid var(--border)', background: 'transparent', color: '#ff5252', cursor: 'pointer' }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {/* Play through the vibe + backing singers */}
                    <button className="btn" onClick={() => (isPlaying ? stop() : play(rec))}>
                      {isPlaying ? <Square size={15} /> : <Play size={15} />}
                      {isPlaying ? 'Stop' : 'Play voice'}
                    </button>

                    {/* Play over the song, in sync (looped) */}
                    <button
                      type="button"
                      onClick={() => onTogglePlay(rec.id)}
                      className="mono"
                      style={{
                        fontSize: 11,
                        padding: '6px 10px',
                        borderRadius: 8,
                        cursor: 'pointer',
                        textTransform: 'uppercase',
                        letterSpacing: '0.04em',
                        background: rec.playWithSong ? 'rgba(43,166,64,0.12)' : 'rgba(255,255,255,0.05)',
                        border: `1px solid ${rec.playWithSong ? 'var(--neon-green)' : 'var(--border)'}`,
                        color: rec.playWithSong ? 'var(--neon-green)' : 'var(--text-dim)',
                      }}
                    >
                      {rec.playWithSong ? '● Plays with song' : 'Play with song'}
                    </button>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="mono" style={{ fontSize: 9.5, color: 'var(--text-faint)', lineHeight: 1.5 }}>
            Noise removal uses your browser's mic cleanup; the vibes are real audio effects. The backing singers are
            your own voice layered into a crowd (a simulated choir) — not separate real people. Takes are kept for this
            session — download any you want to keep.
          </div>
        </>
      )}
    </section>
  )
}
