import { useEffect, useRef, useState } from 'react'
import { Mic, Square, Play, Sparkles, Users, Sparkle, Radio } from 'lucide-react'
import { getEngine } from '../lib/audioEngine.js'
import { useClipRecorder } from '../hooks/useClipRecorder.js'

// Good Voice — record your full vocal with browser noise-suppression, then play
// it back through a "vibe" (Crystal Clear / Rockstar / On Stage) plus a
// simulated group of backing singers. One Play control; changing the vibe or
// singer count re-applies live.
const VIBES = [
  { id: 'clean', label: 'Crystal Clear', icon: Sparkle, desc: 'Clean, present, polished.' },
  { id: 'rockstar', label: 'Rockstar', icon: Sparkles, desc: 'Saturated, gritty, in-your-face.' },
  { id: 'stage', label: 'On Stage', icon: Radio, desc: 'Big arena reverb + echo.' },
]

export default function GoodVoicePage() {
  const engine = getEngine()
  const [clip, setClip] = useState(null)
  const [vibe, setVibe] = useState('clean')
  const [singers, setSingers] = useState(1)
  const [playing, setPlaying] = useState(false)
  const genRef = useRef(0)

  const recorder = useClipRecorder({
    constraints: { noiseSuppression: true, echoCancellation: true, autoGainControl: true },
    onClip: (c) => {
      genRef.current += 1
      engine.stopVocal()
      setClip(c)
      setPlaying(false)
    },
  })

  const play = async () => {
    if (!clip) return
    const my = (genRef.current += 1)
    setPlaying(true)
    await engine.playVocal(clip.url, { vibe, singers }, () => {
      if (genRef.current === my) setPlaying(false)
    })
  }

  const stop = () => {
    genRef.current += 1
    engine.stopVocal()
    setPlaying(false)
  }

  // Re-apply live when the vibe or singer count changes mid-playback.
  useEffect(() => {
    if (playing) play()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vibe, singers])

  // Stop audio when leaving the page.
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
      </div>
      <p style={{ color: 'var(--text-dim)', fontSize: 13.5, lineHeight: 1.6, margin: 0 }}>
        Record your whole song — background noise is cleaned up automatically. Pick a vibe and a crowd of backing
        singers, then press Play. <strong>Tip:</strong> use headphones so only your voice is recorded.
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
              : clip
                ? 'Re-record'
                : 'Tap to record your song'}
        </div>
        {recorder.error && <span className="mono" style={{ fontSize: 10, color: '#ff5252' }}>mic: {recorder.error}</span>}
      </div>

      {clip && (
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

          {/* Single play control */}
          <button className="btn" onClick={() => (playing ? stop() : play())} style={{ alignSelf: 'flex-start' }}>
            {playing ? <Square size={15} /> : <Play size={15} />}
            {playing ? 'Stop' : 'Play voice'}
          </button>

          <div className="mono" style={{ fontSize: 9.5, color: 'var(--text-faint)', lineHeight: 1.5 }}>
            Noise removal uses your browser's mic cleanup; the vibes are real audio effects. The backing singers are
            your own voice layered into a crowd (a simulated choir) — not separate real people.
          </div>
        </>
      )}
    </section>
  )
}
