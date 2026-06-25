import { Play, Pause, Square, Minus, Plus } from 'lucide-react'
import SpectrumAnalyser from './SpectrumAnalyser.jsx'
import { formatTime, estimateDuration } from '../lib/constants.js'

// Feature 6 — Playback Engine controls. Play/Pause/Stop transport, BPM with
// +/- (also voice-adjustable elsewhere), a master volume knob, the live
// spectrum analyser, and a position readout. The playhead itself rides the
// structure timeline above.

function Knob({ value, onChange, color = 'var(--neon-blue)' }) {
  const angle = -135 + (value / 100) * 270
  return (
    <div style={{ position: 'relative', width: 46, height: 46 }}>
      <div
        style={{
          width: 46,
          height: 46,
          borderRadius: '50%',
          background: `conic-gradient(from -135deg, ${color} ${(value / 100) * 270}deg, rgba(255,255,255,0.1) 0)`,
          padding: 4,
        }}
      >
        <div
          style={{
            width: '100%',
            height: '100%',
            borderRadius: '50%',
            background: '#0a0a0f',
            position: 'relative',
            border: '1px solid var(--border)',
          }}
        >
          <div
            style={{
              position: 'absolute',
              top: 4,
              left: '50%',
              width: 2,
              height: 12,
              background: color,
              borderRadius: 2,
              transformOrigin: '50% 17px',
              transform: `translateX(-50%) rotate(${angle}deg)`,
              boxShadow: `0 0 6px ${color}`,
            }}
          />
        </div>
      </div>
      <input
        type="range"
        min="0"
        max="100"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        aria-label="Master volume"
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          opacity: 0,
          cursor: 'ns-resize',
        }}
      />
    </div>
  )
}

export default function Transport({
  playing,
  onPlay,
  onPause,
  onStop,
  bpm,
  onBpmChange,
  masterVolume,
  onMasterChange,
  getSpectrum,
  progress,
  songState,
}) {
  const duration = estimateDuration(songState)
  return (
    <div
      className="glass"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 18,
        padding: '12px 18px',
        flexWrap: 'wrap',
      }}
    >
      {/* Transport buttons */}
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <button
          onClick={playing ? onPause : onPlay}
          className="btn primary"
          style={{ width: 46, height: 46, borderRadius: '50%', padding: 0, justifyContent: 'center' }}
          aria-label={playing ? 'Pause' : 'Play'}
        >
          {playing ? <Pause size={20} /> : <Play size={20} style={{ marginLeft: 2 }} />}
        </button>
        <button
          onClick={onStop}
          className="btn"
          style={{ width: 40, height: 40, borderRadius: '50%', padding: 0, justifyContent: 'center' }}
          aria-label="Stop"
        >
          <Square size={15} />
        </button>
      </div>

      {/* BPM */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span className="label">BPM</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <button onClick={() => onBpmChange(bpm - 1)} className="btn" style={miniBtn} aria-label="Decrease BPM">
            <Minus size={13} />
          </button>
          <span
            className="mono"
            style={{ fontSize: 20, fontWeight: 700, width: 48, textAlign: 'center', color: 'var(--neon-blue)' }}
          >
            {bpm}
          </span>
          <button onClick={() => onBpmChange(bpm + 1)} className="btn" style={miniBtn} aria-label="Increase BPM">
            <Plus size={13} />
          </button>
        </div>
      </div>

      {/* Time */}
      <span className="mono" style={{ fontSize: 13, color: 'var(--text-dim)' }}>
        {formatTime(progress * duration)} / {formatTime(duration)}
      </span>

      {/* Spectrum */}
      <div style={{ flex: 1, minWidth: 140 }}>
        <SpectrumAnalyser getSpectrum={getSpectrum} playing={playing} height={46} />
      </div>

      {/* Master volume knob */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
        <Knob value={masterVolume} onChange={onMasterChange} />
        <span className="label" style={{ fontSize: 8 }}>
          Master
        </span>
      </div>
    </div>
  )
}

const miniBtn = { width: 30, height: 30, borderRadius: 8, padding: 0, justifyContent: 'center' }
