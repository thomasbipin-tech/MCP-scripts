import { useState } from 'react'
import { Mic, Square, Play, Sparkles, Users, Sparkle, Radio } from 'lucide-react'
import { getEngine } from '../lib/audioEngine.js'
import { useClipRecorder } from '../hooks/useClipRecorder.js'

// Good Voice — record your full vocal with browser noise-suppression, then play
// it back through a "vibe" (Crystal Clear / Rockstar / On Stage) plus a
// simulated group of backing singers.
const VIBES = [
  { id: 'clean', label: 'Crystal Clear', icon: Sparkle, desc: 'Clean, present, polished.' },
  { id: 'rockstar', label: 'Rockstar', icon: Sparkles, desc: 'Saturated, punchy, in-your-face.' },
  { id: 'stage', label: 'On Stage', icon: Radio, desc: 'Big arena reverb + echo.' },
]

export default function GoodVoicePage() {
  const engine = getEngine()
  const [clip, setClip] = useState(null)
  const [vibe, setVibe] = useState('clean')
  const [singers, setSingers] = useState(1)
  const [playing, setPlaying] = useState(false)

  const recorder = useClipRecorder({
    constraints: { noiseSuppression: true, echoCancellation: true, autoGainControl: true },
    onClip: (c) => {
      setClip(c)
      setPlaying(false)
    },
  })

  const play = async () => {
    if (!clip) return
    setPlaying(true)
    await engine.playVocal(clip.url, { vibe, singers }, () => setPlaying(false))
  }
  const stop = () => {
    engine.stopVocal()
    setPlaying(false)
  }

  return (
    <section className="glass page-pane" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Mic size={18} style={{ color: 'var(--neon-green)' }} />
        <span style={{ fontSize: 17, fontWeight: 700 }}>Good Voice</span>
      </div>
      <p style={{ color: 'var(--text-dim)', fontSize: 13.5, lineHeight: 1.6, margin: 0 }}>
        Record your whole song with the mic — background noise is cleaned up automatically. Then pick a vibe and a
        crowd of backing singers. <strong>Tip:</strong> use headphones so only your voice is recorded.
      </p>

      {/* Record */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
        <button
          type="button"
          onClick={() => (recorder.recording ? recorder.stop() : recorder.start())}
          disabled={!recorder.supported}
          aria-label={recorder.recording ? 'Stop' : 'Record'}
          style={{
            width: 84,
            height: 84,
            borderRadius: '50%',
            display: 'grid',
            placeItems: 'center',
            cursor: recorder.supported ? 'pointer' : 'not-allowed',
            border: `2px solid ${recorder.recording ? '#ff2d5a' : 'rgba(57,255,20,0.5)'}`,
            background: recorder.recording
              ? `radial-gradient(circle, rgba(255,45,90,${0.25 + recorder.level * 0.5}), rgba(255,45,90,0.08))`
              : 'radial-gradient(circle, rgba(57,255,20,0.16), rgba(0,245,255,0.06))',
            color: recorder.recording ? '#ff6b85' : 'var(--neon-green)',
            opacity: recorder.supported ? 1 : 0.45,
          }}
        >
          {recorder.recording ? <Square size={28} /> : <Mic size={32} />}
        </button>
        <div className="mono" style={{ fontSize: 11, color: recorder.recording ? '#ff6b85' : 'var(--text-faint)' }}>
          {!recorder.supported
            ? 'Mic not available here'
            : recorder.recording
              ? `● REC  ${recorder.elapsed.toFixed(1)}s`
              : clip
                ? 'Re-record'
                : 'Tap to record your song'}
        </div>
        {recorder.error && <span className="mono" style={{ fontSize: 10, color: '#ff6b85' }}>mic: {recorder.error}</span>}
      </div>

      {clip && (
        <>
          <audio src={clip.url} controls style={{ width: '100%', height: 34 }} />

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
                      background: on ? 'rgba(57,255,20,0.1)' : 'rgba(255,255,255,0.04)',
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

          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn" onClick={play} disabled={playing}>
              <Play size={15} /> Play voice
            </button>
            <button className="btn" onClick={stop} disabled={!playing} style={{ opacity: playing ? 1 : 0.5 }}>
              <Square size={15} /> Stop
            </button>
          </div>

          <div className="mono" style={{ fontSize: 9.5, color: 'var(--text-faint)', lineHeight: 1.5 }}>
            Noise removal uses your browser's mic cleanup; the vibes are real audio effects. The backing singers are
            your own voice layered into a crowd (a simulated choir) — not separate real people. True multi-singer
            vocals need an AI voice model.
          </div>
        </>
      )}
    </section>
  )
}
