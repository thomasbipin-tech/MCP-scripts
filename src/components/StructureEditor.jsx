import { useState } from 'react'
import { Plus, Minus, Clock, ChevronLeft, ChevronRight, Trash2 } from 'lucide-react'
import { SEGMENT_COLORS, SEGMENT_TYPES, estimateDuration, formatTime } from '../lib/constants.js'

// Song Structure Editor. Horizontal timeline of sections; tap a section to edit
// it (bars, repeat, move, delete) in the toolbar below, and add new sections.
// Everything is tap-based so it works on touch/iPad (drag reorder kept for
// desktop as a bonus).
export default function StructureEditor({
  songState,
  selectedSegment,
  onSelectSegment,
  onReorder,
  onRepeat,
  onAddSection,
  onDeleteSection,
  onChangeBars,
  onMoveSection,
  progress,
}) {
  const [dragIndex, setDragIndex] = useState(null)
  const [editIndex, setEditIndex] = useState(null)
  const structure = songState.structure || []

  const handleDrop = (index) => {
    if (dragIndex == null || dragIndex === index) return
    const next = [...structure]
    const [moved] = next.splice(dragIndex, 1)
    next.splice(index, 0, moved)
    onReorder(next)
    setDragIndex(null)
  }

  const selectBlock = (i, seg) => {
    setEditIndex(editIndex === i ? null : i)
    onSelectSegment(selectedSegment === seg.type ? null : seg.type)
  }

  const edit = editIndex != null ? structure[editIndex] : null

  return (
    <section className="glass" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="label">Song Structure</span>
        <span className="mono" style={{ fontSize: 11, color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: 6 }}>
          <Clock size={12} /> {formatTime(estimateDuration(songState))}
        </span>
      </div>

      <div style={{ position: 'relative', display: 'flex', gap: 6, height: 84, alignItems: 'stretch' }}>
        {structure.map((seg, i) => {
          const units = seg.bars * (seg.repeat || 1)
          const isEdit = editIndex === i
          const color = SEGMENT_COLORS[seg.type] || '#888'
          return (
            <div
              key={`${seg.type}-${i}`}
              draggable
              onDragStart={() => setDragIndex(i)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => handleDrop(i)}
              onClick={() => selectBlock(i, seg)}
              style={{
                flex: units,
                minWidth: 52,
                borderRadius: 10,
                padding: 10,
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                background: `linear-gradient(160deg, ${color}33, ${color}12)`,
                border: `1.5px solid ${isEdit ? color : color + '55'}`,
                boxShadow: isEdit ? `0 0 16px ${color}66` : 'none',
                transition: 'all 200ms ease',
                opacity: dragIndex === i ? 0.4 : 1,
              }}
            >
              <span className="mono" style={{ fontSize: 11, fontWeight: 700, color, textTransform: 'capitalize', letterSpacing: '0.04em' }}>
                {seg.type}
              </span>
              <span className="mono" style={{ fontSize: 9, color: 'var(--text-faint)' }}>
                {seg.bars}b ×{seg.repeat || 1}
              </span>
            </div>
          )
        })}

        {/* Playhead */}
        <div
          style={{
            position: 'absolute',
            top: -2,
            bottom: -2,
            left: `${progress * 100}%`,
            width: 2,
            background: '#fff',
            boxShadow: '0 0 10px #fff, 0 0 20px var(--neon-blue)',
            pointerEvents: 'none',
            transition: 'left 90ms linear',
            opacity: progress > 0 ? 1 : 0,
          }}
        >
          <div style={{ position: 'absolute', top: -5, left: -4, width: 10, height: 10, borderRadius: '50%', background: '#fff', boxShadow: '0 0 10px var(--neon-blue)' }} />
        </div>
      </div>

      {/* Edit toolbar for the selected section */}
      {edit && (
        <div
          style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', padding: 10, borderRadius: 10, background: 'rgba(10,10,16,0.55)', border: `1px solid ${SEGMENT_COLORS[edit.type] || '#888'}55` }}
        >
          <span className="mono" style={{ fontSize: 11, fontWeight: 700, color: SEGMENT_COLORS[edit.type], textTransform: 'capitalize' }}>
            {edit.type}
          </span>

          <Stepper label="bars" value={edit.bars} onDec={() => onChangeBars(editIndex, -1)} onInc={() => onChangeBars(editIndex, 1)} />
          <Stepper label="repeat" value={edit.repeat || 1} prefix="×" onDec={() => onRepeat(editIndex, -1)} onInc={() => onRepeat(editIndex, 1)} />

          <div style={{ display: 'flex', gap: 4, marginLeft: 'auto' }}>
            <button style={toolBtn} title="Move left" disabled={editIndex === 0} onClick={() => { onMoveSection(editIndex, -1); setEditIndex(Math.max(0, editIndex - 1)) }}>
              <ChevronLeft size={14} />
            </button>
            <button style={toolBtn} title="Move right" disabled={editIndex === structure.length - 1} onClick={() => { onMoveSection(editIndex, 1); setEditIndex(Math.min(structure.length - 1, editIndex + 1)) }}>
              <ChevronRight size={14} />
            </button>
            <button style={{ ...toolBtn, color: '#ff6b85' }} title="Delete section" onClick={() => { onDeleteSection(editIndex); setEditIndex(null) }}>
              <Trash2 size={14} />
            </button>
          </div>
        </div>
      )}

      {/* Add a section */}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
        <span className="mono" style={{ fontSize: 9, color: 'var(--text-faint)', textTransform: 'uppercase' }}>add</span>
        {SEGMENT_TYPES.map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => onAddSection(type)}
            className="mono"
            style={{
              fontSize: 10,
              padding: '4px 8px',
              borderRadius: 7,
              textTransform: 'capitalize',
              cursor: 'pointer',
              background: `${SEGMENT_COLORS[type] || '#888'}18`,
              border: `1px solid ${SEGMENT_COLORS[type] || '#888'}55`,
              color: SEGMENT_COLORS[type] || '#aaa',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 3,
            }}
          >
            <Plus size={10} /> {type}
          </button>
        ))}
      </div>

      <span className="mono" style={{ fontSize: 10, color: 'var(--text-faint)' }}>
        {selectedSegment ? (
          <>
            Editing <span style={{ color: SEGMENT_COLORS[selectedSegment] }}>{selectedSegment}</span> · voice/text commands target it too.
          </>
        ) : (
          'Tap a section to edit it · add new ones below'
        )}
      </span>
    </section>
  )
}

function Stepper({ label, value, prefix = '', onDec, onInc }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
      <span className="mono" style={{ fontSize: 9, color: 'var(--text-faint)', textTransform: 'uppercase' }}>{label}</span>
      <button style={toolBtn} onClick={onDec}><Minus size={12} /></button>
      <span className="mono" style={{ fontSize: 11, color: 'var(--text)', minWidth: 20, textAlign: 'center' }}>{prefix}{value}</span>
      <button style={toolBtn} onClick={onInc}><Plus size={12} /></button>
    </div>
  )
}

const toolBtn = {
  width: 26,
  height: 26,
  borderRadius: 7,
  display: 'grid',
  placeItems: 'center',
  background: 'rgba(255,255,255,0.06)',
  border: '1px solid var(--border)',
  color: 'var(--text)',
  cursor: 'pointer',
}
