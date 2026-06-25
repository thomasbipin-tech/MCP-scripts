import { Wand2, Loader2 } from 'lucide-react'
import { KEYS, TIME_SIGNATURES, GENRES, MOODS } from '../lib/constants.js'

// Feature 7 — Song Settings Panel. Key, time signature, genre and mood
// selectors (the AI uses genre/mood to bias suggestions) plus the "Surprise me"
// generator that builds a whole starter song.

function Field({ label, value, options, onChange, capitalize }) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <span className="label">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{ textTransform: capitalize ? 'capitalize' : 'none', minWidth: 96 }}
      >
        {options.map((o) => (
          <option key={o} value={o} style={{ textTransform: capitalize ? 'capitalize' : 'none' }}>
            {o}
          </option>
        ))}
      </select>
    </label>
  )
}

export default function SettingsBar({ songState, onChange, onSurprise, thinking }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 14, flexWrap: 'wrap' }}>
      <Field label="Key" value={songState.key} options={KEYS} onChange={(v) => onChange({ key: v })} />
      <Field
        label="Time"
        value={songState.timeSignature}
        options={TIME_SIGNATURES}
        onChange={(v) => onChange({ timeSignature: v })}
      />
      <Field
        label="Genre"
        value={songState.genre}
        options={GENRES}
        onChange={(v) => onChange({ genre: v })}
        capitalize
      />
      <Field
        label="Mood"
        value={songState.mood}
        options={MOODS}
        onChange={(v) => onChange({ mood: v })}
        capitalize
      />
      <button
        className="btn primary"
        onClick={onSurprise}
        disabled={thinking}
        style={{ height: 34 }}
      >
        {thinking ? <Loader2 size={15} className="spin" /> : <Wand2 size={15} />} Surprise me
      </button>
    </div>
  )
}
