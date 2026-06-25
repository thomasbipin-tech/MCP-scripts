import { useState } from 'react'
import {
  Drum,
  Activity,
  Zap,
  Radio,
  Piano,
  Guitar,
  Music2,
  Waves,
  Volume2,
  VolumeX,
  Headphones,
  Trash2,
  Repeat,
  GripVertical,
} from 'lucide-react'
import { SEGMENT_COLORS } from '../lib/constants.js'

// Feature 3 — Interactive Layer System (Track Mixer). A draggable vertical
// stack of track lanes: neon border, instrument icon + name, breathing waveform
// block with section coloring, volume slider, mute/solo, FX toggles, loop
// badge, and delete.

const ICONS = { Drum, Activity, Zap, Radio, Piano, Guitar, Music2, Waves }
const ICON_FOR = {
  drums: Drum,
  bass: Activity,
  lead: Zap,
  synth: Radio,
  piano: Piano,
  guitar: Guitar,
  violin: Music2,
  pad: Waves,
}

function WaveformBlock({ track, playing, structure }) {
  const bars = track.pattern && track.pattern.length ? track.pattern : Array(8).fill('note')
  const totalUnits = structure.reduce((s, seg) => s + seg.bars * (seg.repeat || 1), 0) || 1
  return (
    <div style={{ position: 'relative', height: 40, borderRadius: 6, overflow: 'hidden', background: 'rgba(0,0,0,0.3)' }}>
      {/* Section color strip */}
      <div style={{ position: 'absolute', inset: 0, display: 'flex', opacity: 0.18 }}>
        {structure.map((seg, i) => (
          <div
            key={i}
            style={{ flex: seg.bars * (seg.repeat || 1), background: SEGMENT_COLORS[seg.type] || '#555' }}
          />
        ))}
      </div>
      {/* Breathing bars */}
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', gap: 2, padding: '0 6px' }}>
        {bars.map((step, i) => {
          const active = step && step !== ''
          const h = active ? 35 + ((i * 13) % 55) : 14
          return (
            <div
              key={i}
              style={{
                flex: 1,
                height: `${h}%`,
                borderRadius: 2,
                background: active ? track.color : 'rgba(255,255,255,0.12)',
                boxShadow: active && playing ? `0 0 6px ${track.color}` : 'none',
                transformOrigin: 'center',
                animation: playing && active ? `breathe ${0.6 + (i % 4) * 0.12}s ease-in-out infinite` : 'none',
              }}
            />
          )
        })}
      </div>
    </div>
  )
}

function FxToggle({ on, label, color, onClick }) {
  return (
    <button
      onClick={onClick}
      title={label}
      style={{
        fontFamily: 'var(--mono)',
        fontSize: 9,
        letterSpacing: '0.05em',
        padding: '3px 7px',
        borderRadius: 6,
        textTransform: 'uppercase',
        background: on ? `${color}28` : 'rgba(255,255,255,0.05)',
        border: `1px solid ${on ? color : 'var(--border)'}`,
        color: on ? color : 'var(--text-dim)',
        boxShadow: on ? `0 0 8px ${color}55` : 'none',
        transition: 'all 200ms ease',
      }}
    >
      {label}
    </button>
  )
}

function TrackLane({ track, index, playing, selected, structure, onSelect, onUpdate, onToggleEffect, onDelete, dnd }) {
  const Icon = ICON_FOR[track.instrument] || Radio
  const loops = track.loops || 1

  return (
    <div
      draggable
      onDragStart={() => dnd.setDragIndex(index)}
      onDragOver={(e) => e.preventDefault()}
      onDrop={() => dnd.onDrop(index)}
      onClick={() => onSelect(selected ? null : track.id)}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
        padding: 12,
        borderRadius: 12,
        cursor: 'pointer',
        background: 'rgba(10,10,16,0.55)',
        border: `1.5px solid ${selected ? track.color : track.color + '40'}`,
        boxShadow: selected ? `0 0 18px ${track.color}55` : 'none',
        opacity: dnd.dragIndex === index ? 0.4 : track.muted ? 0.6 : 1,
        transition: 'all 250ms ease',
      }}
      onMouseEnter={(e) => (e.currentTarget.style.boxShadow = `0 0 16px ${track.color}55`)}
      onMouseLeave={(e) => (e.currentTarget.style.boxShadow = selected ? `0 0 18px ${track.color}55` : 'none')}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <GripVertical size={15} style={{ color: 'var(--text-faint)', cursor: 'grab', flexShrink: 0 }} />
        <div
          style={{
            width: 30,
            height: 30,
            borderRadius: 8,
            display: 'grid',
            placeItems: 'center',
            background: `${track.color}22`,
            color: track.color,
            flexShrink: 0,
          }}
        >
          <Icon size={17} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13.5, fontWeight: 700, color: track.color }}>{track.name}</div>
          <div className="mono" style={{ fontSize: 9, color: 'var(--text-faint)', textTransform: 'uppercase' }}>
            {track.instrument}
          </div>
        </div>

        {/* Loop badge */}
        <button
          onClick={(e) => {
            e.stopPropagation()
            const nextLoops = loops >= 4 ? 1 : loops * 2
            onUpdate(track.id, { loops: nextLoops })
          }}
          title="Loop count"
          className="mono"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            fontSize: 10,
            padding: '3px 7px',
            borderRadius: 6,
            background: 'rgba(255,255,255,0.06)',
            border: '1px solid var(--border)',
            color: 'var(--text-dim)',
          }}
        >
          <Repeat size={11} /> x{loops}
        </button>

        <div style={{ display: 'flex', gap: 5 }} onClick={(e) => e.stopPropagation()}>
          <button
            onClick={() => onUpdate(track.id, { muted: !track.muted })}
            title="Mute"
            style={ctrlBtn(track.muted, '#ff6b85')}
          >
            {track.muted ? <VolumeX size={14} /> : <Volume2 size={14} />}
          </button>
          <button
            onClick={() => onUpdate(track.id, { solo: !track.solo })}
            title="Solo"
            style={ctrlBtn(track.solo, 'var(--neon-amber)')}
          >
            <Headphones size={14} />
          </button>
          <button onClick={() => onDelete(track.id)} title="Delete track" style={ctrlBtn(false, '#ff6b85')}>
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      <WaveformBlock track={track} playing={playing} structure={structure} />

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }} onClick={(e) => e.stopPropagation()}>
        <input
          type="range"
          min="0"
          max="100"
          value={track.volume}
          onChange={(e) => onUpdate(track.id, { volume: Number(e.target.value) })}
          style={{ flex: 1, '--thumb': track.color }}
          aria-label={`${track.name} volume`}
        />
        <span className="mono" style={{ fontSize: 10, color: 'var(--text-dim)', width: 26, textAlign: 'right' }}>
          {track.volume}
        </span>
        <div style={{ display: 'flex', gap: 4 }}>
          <FxToggle on={track.effects.reverb} label="Rev" color="var(--neon-blue)" onClick={() => onToggleEffect(track.id, 'reverb')} />
          <FxToggle on={track.effects.delay} label="Dly" color="var(--neon-green)" onClick={() => onToggleEffect(track.id, 'delay')} />
          <FxToggle on={track.effects.distortion} label="Dist" color="var(--neon-pink)" onClick={() => onToggleEffect(track.id, 'distortion')} />
        </div>
      </div>
    </div>
  )
}

export default function TrackMixer({ tracks, playing, structure, selectedTrackId, onSelect, onUpdate, onToggleEffect, onDelete, onReorder }) {
  const [dragIndex, setDragIndex] = useState(null)

  const onDrop = (index) => {
    if (dragIndex == null || dragIndex === index) return
    const next = [...tracks]
    const [moved] = next.splice(dragIndex, 1)
    next.splice(index, 0, moved)
    onReorder(next)
    setDragIndex(null)
  }

  return (
    <section className="glass" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="label">Tracks · {tracks.length}</span>
        <span className="mono" style={{ fontSize: 9, color: 'var(--text-faint)' }}>drag to reorder</span>
      </div>

      {tracks.length === 0 ? (
        <div style={{ padding: '28px 12px', textAlign: 'center', color: 'var(--text-faint)', fontSize: 13 }}>
          No tracks yet. Say “add a drum track”, hum a melody, or hit “Surprise me”.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {tracks.map((track, i) => (
            <TrackLane
              key={track.id}
              track={track}
              index={i}
              playing={playing}
              structure={structure}
              selected={selectedTrackId === track.id}
              onSelect={onSelect}
              onUpdate={onUpdate}
              onToggleEffect={onToggleEffect}
              onDelete={onDelete}
              dnd={{ dragIndex, setDragIndex, onDrop }}
            />
          ))}
        </div>
      )}
    </section>
  )
}

const ctrlBtn = (active, color) => ({
  width: 28,
  height: 28,
  borderRadius: 7,
  display: 'grid',
  placeItems: 'center',
  background: active ? `${color}22` : 'rgba(255,255,255,0.05)',
  border: `1px solid ${active ? color : 'var(--border)'}`,
  color: active ? color : 'var(--text-dim)',
  transition: 'all 200ms ease',
})
