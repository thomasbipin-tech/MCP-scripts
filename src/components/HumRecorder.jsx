import { useState } from 'react'
import { Mic, Square, Wand2, Play, Plus, Loader2 } from 'lucide-react'
import { useHumRecorder } from '../hooks/useHumRecorder.js'
import { generateMelodyFromHum } from '../lib/aiProducer.js'
import { INSTRUMENTS } from '../lib/constants.js'

const NOTE_SEMI = { C: 0, 'C#': 1, D: 2, 'D#': 3, E: 4, F: 5, 'F#': 6, G: 7, 'G#': 8, A: 9, 'A#': 10, B: 11 }
function noteRank(note) {
  const m = String(note).match(/^([A-G]#?)(\d)$/)
  if (!m) return 0
  return (NOTE_SEMI[m[1]] ?? 0) + parseInt(m[2], 10) * 12
}

// Feature 2 — Hum-to-Melody Recorder. Capture a hum, draw its waveform, turn it
// into a note sequence in the current key, preview it on a chosen instrument,
// and drop it in as a new track.

export default function HumRecorder({ songState, onAddTrack, onPreview }) {
  const { supported, recording, waveform, level, error, start, stop } = useHumRecorder()
  const [notes, setNotes] = useState(null)
  const [contour, setContour] = useState([])
  const [instrument, setInstrument] = useState('lead')
  const [thinking, setThinking] = useState(false)

  const handleStop = async () => {
    const { contour: c } = await stop()
    setContour(c)
  }

  const generate = async () => {
    setThinking(true)
    // Brief async pause to surface the AI generation state.
    await new Promise((r) => setTimeout(r, 400))
    setNotes(generateMelodyFromHum(songState, instrument, contour))
    setThinking(false)
  }

  const ranks = notes ? notes.map((n) => noteRank(n.note)) : []
  const minR = ranks.length ? Math.min(...ranks) : 0
  const maxR = ranks.length ? Math.max(...ranks) : 1
  const span = Math.max(1, maxR - minR)

  return (
    <section className="glass" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="label">Hum → Melody</span>
        {recording && (
          <span className="mono" style={{ fontSize: 10, color: '#ff5252', display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#ff0000', animation: 'pulse-rec 1.2s infinite' }} />
            REC
          </span>
        )}
      </div>

      {/* Waveform display */}
      <div
        style={{
          height: 56,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          padding: '0 6px',
          background: 'rgba(0,0,0,0.25)',
          borderRadius: 8,
          border: '1px solid var(--border)',
        }}
      >
        {(recording ? Array.from({ length: 64 }, () => level) : waveform.length ? waveform : Array.from({ length: 64 }, () => 0.04)).map(
          (v, i) => (
            <div
              key={i}
              style={{
                flex: 1,
                height: `${Math.max(4, (recording ? Math.random() * v : v) * 100)}%`,
                background: recording ? '#ff5252' : 'var(--neon-blue)',
                borderRadius: 2,
                opacity: recording ? 0.9 : 0.8,
                transition: 'height 80ms linear',
              }}
            />
          ),
        )}
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {!recording ? (
          <button className="btn" onClick={start} disabled={!supported}>
            <Mic size={15} /> Record Melody
          </button>
        ) : (
          <button className="btn primary" onClick={handleStop}>
            <Square size={14} /> Stop
          </button>
        )}

        <select value={instrument} onChange={(e) => setInstrument(e.target.value)} aria-label="Instrument">
          {INSTRUMENTS.filter((i) => i.id !== 'drums').map((i) => (
            <option key={i.id} value={i.id}>
              {i.name}
            </option>
          ))}
        </select>

        <button className="btn" onClick={generate} disabled={recording || (!waveform.length && !contour.length)}>
          {thinking ? <Loader2 size={15} className="spin" /> : <Wand2 size={15} />} Generate
        </button>
      </div>

      {!supported && (
        <span className="mono" style={{ fontSize: 10, color: 'var(--text-faint)' }}>
          Mic recording unsupported — “Generate” still works with a default contour.
        </span>
      )}
      {error && (
        <span className="mono" style={{ fontSize: 10, color: '#ff5252' }}>
          {error}
        </span>
      )}

      {/* Piano-roll strip */}
      {notes && (
        <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div
            style={{
              position: 'relative',
              height: 72,
              background: 'rgba(0,0,0,0.3)',
              borderRadius: 8,
              border: '1px solid var(--border)',
              overflow: 'hidden',
            }}
          >
            {notes.map((n, i) => {
              const y = 1 - (noteRank(n.note) - minR) / span
              return (
                <div
                  key={i}
                  title={n.note}
                  style={{
                    position: 'absolute',
                    left: `${(n.step / notes.length) * 100}%`,
                    top: `${8 + y * 52}px`,
                    width: `${(1 / notes.length) * 100 - 1.5}%`,
                    height: 10,
                    background: 'var(--neon-green)',
                    boxShadow: '0 0 8px rgba(43,166,64,0.6)',
                    borderRadius: 3,
                  }}
                />
              )
            })}
          </div>
          <div className="mono" style={{ fontSize: 10, color: 'var(--text-dim)' }}>
            {notes.map((n) => n.note).join(' · ')}
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn" onClick={() => onPreview(notes, instrument)}>
              <Play size={14} /> Preview
            </button>
            <button
              className="btn primary"
              onClick={() => {
                onAddTrack(notes, instrument)
                setNotes(null)
              }}
            >
              <Plus size={15} /> Add as Track
            </button>
          </div>
        </div>
      )}
    </section>
  )
}
