import { useRef, useState } from 'react'
import { Plus, Minus, Clock } from 'lucide-react'
import { SEGMENT_COLORS, estimateDuration, formatTime } from '../lib/constants.js'

// Feature 4 — Song Structure Editor. A horizontal timeline of draggable
// section blocks (Intro/Verse/Chorus/Bridge/Outro), click-to-select, a repeat
// badge with +/- controls, a duration estimate, and a moving playhead.

export default function StructureEditor({
  songState,
  selectedSegment,
  onSelectSegment,
  onReorder,
  onRepeat,
  progress,
}) {
  const [dragIndex, setDragIndex] = useState(null)
  const containerRef = useRef(null)
  const structure = songState.structure || []
  const totalUnits = structure.reduce((s, seg) => s + seg.bars * (seg.repeat || 1), 0) || 1

  const handleDrop = (index) => {
    if (dragIndex == null || dragIndex === index) return
    const next = [...structure]
    const [moved] = next.splice(dragIndex, 1)
    next.splice(index, 0, moved)
    onReorder(next)
    setDragIndex(null)
  }

  return (
    <section className="glass" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="label">Song Structure</span>
        <span className="mono" style={{ fontSize: 11, color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: 6 }}>
          <Clock size={12} /> {formatTime(estimateDuration(songState))}
        </span>
      </div>

      <div
        ref={containerRef}
        style={{ position: 'relative', display: 'flex', gap: 6, height: 92, alignItems: 'stretch' }}
      >
        {structure.map((seg, i) => {
          const units = seg.bars * (seg.repeat || 1)
          const isSel = selectedSegment === seg.type
          const color = SEGMENT_COLORS[seg.type] || '#888'
          return (
            <div
              key={`${seg.type}-${i}`}
              draggable
              onDragStart={() => setDragIndex(i)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => handleDrop(i)}
              onClick={() => onSelectSegment(isSel ? null : seg.type)}
              style={{
                flex: units,
                minWidth: 56,
                borderRadius: 10,
                padding: 10,
                cursor: 'pointer',
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                background: `linear-gradient(160deg, ${color}33, ${color}12)`,
                border: `1.5px solid ${isSel ? color : color + '55'}`,
                boxShadow: isSel ? `0 0 16px ${color}66` : 'none',
                transition: 'all 200ms ease',
                opacity: dragIndex === i ? 0.4 : 1,
              }}
            >
              <span
                className="mono"
                style={{ fontSize: 11, fontWeight: 700, color, textTransform: 'capitalize', letterSpacing: '0.04em' }}
              >
                {seg.type}
              </span>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <span className="mono" style={{ fontSize: 9, color: 'var(--text-faint)' }}>{seg.bars} bars</span>
                <div
                  style={{ display: 'flex', alignItems: 'center', gap: 3 }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    onClick={() => onRepeat(i, -1)}
                    style={iconBtn}
                    aria-label={`Decrease ${seg.type} repeat`}
                    disabled={(seg.repeat || 1) <= 1}
                  >
                    <Minus size={10} />
                  </button>
                  <span className="mono" style={{ fontSize: 11, color, minWidth: 18, textAlign: 'center' }}>
                    x{seg.repeat || 1}
                  </span>
                  <button onClick={() => onRepeat(i, 1)} style={iconBtn} aria-label={`Increase ${seg.type} repeat`}>
                    <Plus size={10} />
                  </button>
                </div>
              </div>
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
          <div
            style={{
              position: 'absolute',
              top: -5,
              left: -4,
              width: 10,
              height: 10,
              borderRadius: '50%',
              background: '#fff',
              boxShadow: '0 0 10px var(--neon-blue)',
            }}
          />
        </div>
      </div>

      <span className="mono" style={{ fontSize: 10, color: 'var(--text-faint)' }}>
        {selectedSegment ? (
          <>
            Selected: <span style={{ color: SEGMENT_COLORS[selectedSegment] }}>{selectedSegment}</span> — voice/text
            commands now target it.
          </>
        ) : (
          'Click a section to target it · drag to reorder'
        )}
      </span>
    </section>
  )
}

const iconBtn = {
  width: 18,
  height: 18,
  borderRadius: 5,
  display: 'grid',
  placeItems: 'center',
  background: 'rgba(255,255,255,0.08)',
  color: 'var(--text)',
}
