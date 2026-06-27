import { Drum, Activity, Zap, Radio, Piano, Guitar, Music2, Waves, SlidersVertical } from 'lucide-react'
import { INSTRUMENTS } from '../lib/constants.js'

// Instruments & Sounds page: swap any track's instrument. "Real" = sampled
// acoustic instrument; "Synth" = electronic.
const ICON_FOR = { drums: Drum, bass: Activity, lead: Zap, synth: Radio, piano: Piano, guitar: Guitar, violin: Music2, pad: Waves }
const ACOUSTIC = new Set(['piano', 'guitar', 'bass', 'violin', 'drums'])

export default function InstrumentsPage({ songState, onChangeInstrument }) {
  const tracks = songState.tracks || []

  return (
    <section className="glass page-pane" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <SlidersVertical size={18} style={{ color: 'var(--neon-green)' }} />
        <span style={{ fontSize: 17, fontWeight: 700 }}>Instruments &amp; Sounds</span>
      </div>
      <p style={{ color: 'var(--text-dim)', fontSize: 13.5, lineHeight: 1.6, margin: 0 }}>
        Swap any track's instrument. <strong style={{ color: 'var(--neon-green)' }}>Real</strong> = sampled
        acoustic sound; <strong style={{ color: 'var(--neon-blue)' }}>Synth</strong> = electronic.
      </p>

      {tracks.length === 0 ? (
        <div style={{ padding: '28px 12px', textAlign: 'center', color: 'var(--text-faint)', fontSize: 13 }}>
          No tracks yet. Generate a song first (Surprise me or Super Generate).
        </div>
      ) : (
        tracks.map((track) => {
          const Cur = ICON_FOR[track.instrument] || Radio
          return (
            <div
              key={track.id}
              style={{ padding: 14, borderRadius: 12, background: 'rgba(10,10,16,0.55)', border: `1px solid ${track.color}40`, display: 'flex', flexDirection: 'column', gap: 10 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 28, height: 28, borderRadius: 8, display: 'grid', placeItems: 'center', background: `${track.color}22`, color: track.color }}>
                  <Cur size={16} />
                </div>
                <div style={{ fontSize: 14, fontWeight: 700, color: track.color }}>{track.name}</div>
              </div>

              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {INSTRUMENTS.map((inst) => {
                  const Icon = ICON_FOR[inst.id] || Radio
                  const active = track.instrument === inst.id
                  const real = ACOUSTIC.has(inst.id)
                  return (
                    <button
                      key={inst.id}
                      type="button"
                      onClick={() => onChangeInstrument(track.id, inst.id)}
                      title={`${inst.name} (${real ? 'real' : 'synth'})`}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                        padding: '7px 10px',
                        borderRadius: 9,
                        cursor: 'pointer',
                        fontSize: 12,
                        fontWeight: 600,
                        background: active ? `${track.color}22` : 'rgba(255,255,255,0.04)',
                        border: `1px solid ${active ? track.color : 'var(--border)'}`,
                        color: active ? track.color : 'var(--text-dim)',
                      }}
                    >
                      <Icon size={14} />
                      {inst.name}
                      <span
                        className="mono"
                        style={{
                          fontSize: 8,
                          padding: '1px 4px',
                          borderRadius: 4,
                          color: real ? 'var(--neon-green)' : 'var(--neon-blue)',
                          border: `1px solid ${real ? 'rgba(57,255,20,0.3)' : 'rgba(0,245,255,0.3)'}`,
                        }}
                      >
                        {real ? 'REAL' : 'SYN'}
                      </span>
                    </button>
                  )
                })}
              </div>
            </div>
          )
        })
      )}
    </section>
  )
}
