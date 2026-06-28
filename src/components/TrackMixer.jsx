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
  Plus,
} from 'lucide-react'
import { SEGMENT_COLORS, scaleNotes } from '../lib/constants.js'

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

const STEPS = 8
const DRUM_CYCLE = ['', 'kick', 'snare', 'hat']
const DRUM_LABEL = { kick: 'K', snare: 'S', hat: 'H' }
const octaveFor = (inst) => (inst === 'bass' ? 2 : inst === 'pad' ? 3 : 4)

// Editable step grid. Tap cells to change what a track plays.
// Drums: each cell cycles Kick → Snare → Hat → off. Melodic: each cell toggles a
// note (on/off) at that step, pitched from the song's key.
function StepGrid({ track, songKey, onUpdate }) {
  const isDrums = track.instrument === 'drums'

  if (isDrums) {
    const pattern = Array.from({ length: STEPS }, (_, i) => track.pattern?.[i] || '')
    const tap = (i) => {
      const next = DRUM_CYCLE[(DRUM_CYCLE.indexOf(pattern[i]) + 1) % DRUM_CYCLE.length]
      const np = [...pattern]
      np[i] = next
      onUpdate(track.id, { pattern: np })
    }
    return (
      <div className="step-grid" onClick={(e) => e.stopPropagation()}>
        {pattern.map((v, i) => (
          <button
            key={i}
            type="button"
            className="step-cell"
            onClick={() => tap(i)}
            style={{
              background: v ? track.color : 'rgba(255,255,255,0.06)',
              color: v ? '#0a0a0f' : 'transparent',
              borderColor: v ? track.color : 'var(--border)',
            }}
            aria-label={`step ${i + 1}: ${v || 'off'}`}
          >
            {DRUM_LABEL[v] || ''}
          </button>
        ))}
      </div>
    )
  }

  const onAt = (i) => (track.notes || []).some((n) => (n.step ?? 0) % STEPS === i)
  const tap = (i) => {
    let notes = (track.notes || []).filter((n) => (n.step ?? 0) % STEPS !== i)
    if (!onAt(i)) {
      const scale = scaleNotes(songKey || 'C major', octaveFor(track.instrument), STEPS)
      notes = [...notes, { note: scale[i % scale.length], step: i, duration: '8n' }]
      notes.sort((a, b) => (a.step ?? 0) - (b.step ?? 0))
    }
    onUpdate(track.id, { notes })
  }
  return (
    <div className="step-grid" onClick={(e) => e.stopPropagation()}>
      {Array.from({ length: STEPS }, (_, i) => {
        const on = onAt(i)
        return (
          <button
            key={i}
            type="button"
            className="step-cell"
            onClick={() => tap(i)}
            style={{
              background: on ? track.color : 'rgba(255,255,255,0.06)',
              borderColor: on ? track.color : 'var(--border)',
            }}
            aria-label={`step ${i + 1}: ${on ? 'on' : 'off'}`}
          />
        )
      })}
    </div>
  )
}

// Place a track into specific song sections. No selection = plays everywhere.
function SectionChips({ track, structure, onUpdate }) {
  const types = [...new Set((structure || []).map((s) => s.type))]
  const active = track.sections || []
  const toggle = (t) => {
    const next = active.includes(t) ? active.filter((x) => x !== t) : [...active, t]
    onUpdate(track.id, { sections: next })
  }
  return (
    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', alignItems: 'center' }} onClick={(e) => e.stopPropagation()}>
      <span className="mono" style={{ fontSize: 9, color: 'var(--text-faint)', textTransform: 'uppercase' }}>
        plays in
      </span>
      {types.map((t) => {
        const explicit = active.includes(t)
        const color = SEGMENT_COLORS[t] || '#888'
        return (
          <button
            key={t}
            type="button"
            onClick={() => toggle(t)}
            className="mono"
            style={{
              fontSize: 9,
              padding: '3px 7px',
              borderRadius: 6,
              textTransform: 'capitalize',
              background: explicit ? `${color}28` : 'rgba(255,255,255,0.05)',
              border: `1px solid ${explicit ? color : 'var(--border)'}`,
              color: explicit ? color : 'var(--text-faint)',
              opacity: active.length === 0 ? 0.7 : 1,
            }}
          >
            {t}
          </button>
        )
      })}
      {active.length > 0 ? (
        <button
          type="button"
          onClick={() => onUpdate(track.id, { sections: [] })}
          className="mono"
          style={{ fontSize: 9, padding: '3px 6px', borderRadius: 6, background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-dim)' }}
        >
          all
        </button>
      ) : (
        <span className="mono" style={{ fontSize: 9, color: 'var(--text-faint)' }}>· everywhere</span>
      )}
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

function TrackLane({ track, index, playing, selected, structure, songKey, onSelect, onUpdate, onToggleEffect, onDelete, dnd }) {
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
            style={ctrlBtn(track.muted, '#ff5252')}
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
          <button onClick={() => onDelete(track.id)} title="Delete track" style={ctrlBtn(false, '#ff5252')}>
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      <StepGrid track={track} songKey={songKey} onUpdate={onUpdate} />
      <SectionChips track={track} structure={structure} onUpdate={onUpdate} />

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

export default function TrackMixer({ tracks, playing, structure, songKey, selectedTrackId, onSelect, onUpdate, onToggleEffect, onDelete, onReorder, onAddTrack }) {
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
        <button
          type="button"
          onClick={onAddTrack}
          className="mono"
          style={{
            fontSize: 10,
            padding: '5px 10px',
            borderRadius: 7,
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 4,
            background: 'rgba(62,166,255,0.1)',
            border: '1px solid rgba(62,166,255,0.3)',
            color: 'var(--neon-blue)',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
          }}
        >
          <Plus size={12} /> Add track
        </button>
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
              songKey={songKey}
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
