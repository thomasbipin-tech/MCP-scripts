// Shared constants, music-theory helpers, and the default song state.

// Per-track accent colors — distinct but tuned to the YouTube-dark scheme.
export const NEON_COLORS = [
  '#ff0000', // red
  '#3ea6ff', // blue
  '#2ba640', // green
  '#ffb02e', // amber
  '#a05cff', // violet
  '#ff7626', // orange
]

export const INSTRUMENTS = [
  { id: 'drums', name: 'Drums', icon: 'Drum' },
  { id: 'bass', name: 'Bass', icon: 'Activity' },
  { id: 'lead', name: 'Lead', icon: 'Zap' },
  { id: 'synth', name: 'Synth', icon: 'Radio' },
  { id: 'piano', name: 'Piano', icon: 'Piano' },
  { id: 'guitar', name: 'Guitar', icon: 'Guitar' },
  { id: 'violin', name: 'Violin', icon: 'Music2' },
  { id: 'pad', name: 'Pad', icon: 'Waves' },
]

export const INSTRUMENT_IDS = INSTRUMENTS.map((i) => i.id)

export const SEGMENT_TYPES = ['intro', 'verse', 'chorus', 'bridge', 'outro']

export const SEGMENT_COLORS = {
  intro: '#54546a',
  verse: '#00f5ff',
  chorus: '#ff2d95',
  bridge: '#b14cff',
  outro: '#ffb700',
}

export const KEYS = [
  'C major',
  'G major',
  'D major',
  'A major',
  'E major',
  'F major',
  'A minor',
  'E minor',
  'D minor',
  'B minor',
  'C minor',
  'G minor',
]

export const TIME_SIGNATURES = ['4/4', '3/4', '6/8']

export const GENRES = [
  'electronic',
  'hip hop',
  'rock',
  'pop',
  'lo-fi',
  'cinematic',
  'house',
  'ambient',
  'trap',
]

export const MOODS = ['energetic', 'dark', 'euphoric', 'chill', 'aggressive', 'dreamy']

// ----- Music theory -----
const NOTE_INDEX = {
  C: 0,
  'C#': 1,
  D: 2,
  'D#': 3,
  E: 4,
  F: 5,
  'F#': 6,
  G: 7,
  'G#': 8,
  A: 9,
  'A#': 10,
  B: 11,
}
const INDEX_NOTE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

const MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11]
const MINOR_STEPS = [0, 2, 3, 5, 7, 8, 10]

/** Parse "C major" / "A minor" into { root: 'C', mode: 'major' }. */
export function parseKey(key) {
  const [root = 'C', mode = 'major'] = String(key).trim().split(/\s+/)
  return { root, mode: mode.toLowerCase() === 'minor' ? 'minor' : 'major' }
}

/** Return note names (with octaves) for a scale across a small range. */
export function scaleNotes(key, baseOctave = 4, count = 8) {
  const { root, mode } = parseKey(key)
  const rootIdx = NOTE_INDEX[root] ?? 0
  const steps = mode === 'minor' ? MINOR_STEPS : MAJOR_STEPS
  const notes = []
  for (let i = 0; i < count; i++) {
    const degree = i % steps.length
    const octaveBump = Math.floor(i / steps.length)
    const semis = rootIdx + steps[degree]
    const octave = baseOctave + octaveBump + Math.floor(semis / 12)
    notes.push(INDEX_NOTE[semis % 12] + octave)
  }
  return notes
}

/** Diatonic triad built on the scale root (root, third, fifth). */
export function rootChord(key, octave = 3) {
  const { root, mode } = parseKey(key)
  const rootIdx = NOTE_INDEX[root] ?? 0
  const steps = mode === 'minor' ? MINOR_STEPS : MAJOR_STEPS
  return [steps[0], steps[2], steps[4]].map((s) => {
    const semis = rootIdx + s
    return INDEX_NOTE[semis % 12] + (octave + Math.floor(semis / 12))
  })
}

export const DEFAULT_PATTERNS = {
  drums: ['kick', '', 'snare', '', 'kick', 'kick', 'snare', ''],
  bass: ['note', '', '', 'note', 'note', '', 'note', ''],
  default: ['note', '', 'note', '', 'note', '', 'note', ''],
}

let _id = 100
export const nextId = () => ++_id

export function makeTrack(partial = {}) {
  const instrument = partial.instrument || 'synth'
  const idx = INSTRUMENT_IDS.indexOf(instrument)
  return {
    id: partial.id ?? nextId(),
    name: partial.name || (INSTRUMENTS.find((i) => i.id === instrument)?.name ?? 'Track'),
    instrument,
    color: partial.color || NEON_COLORS[(idx < 0 ? 0 : idx) % NEON_COLORS.length],
    volume: partial.volume ?? 80,
    muted: partial.muted ?? false,
    solo: partial.solo ?? false,
    effects: {
      reverb: false,
      delay: false,
      distortion: false,
      ...(partial.effects || {}),
    },
    pattern: partial.pattern || DEFAULT_PATTERNS[instrument] || DEFAULT_PATTERNS.default,
    notes: partial.notes ?? null,
  }
}

export const DEFAULT_SONG_STATE = {
  bpm: 120,
  key: 'C major',
  timeSignature: '4/4',
  genre: 'electronic',
  mood: 'energetic',
  masterVolume: 80,
  structure: [
    { type: 'intro', bars: 4, repeat: 1 },
    { type: 'verse', bars: 8, repeat: 1 },
    { type: 'chorus', bars: 8, repeat: 3 },
    { type: 'outro', bars: 4, repeat: 1 },
  ],
  tracks: [
    makeTrack({
      id: 1,
      name: 'Drums',
      instrument: 'drums',
      color: '#00f5ff',
      volume: 80,
      pattern: ['kick', '', 'snare', '', 'kick', 'kick', 'snare', ''],
    }),
  ],
  lyrics: '',
}

/** Beats-per-bar from a time signature string. */
export function beatsPerBar(timeSignature) {
  const [num] = String(timeSignature).split('/').map(Number)
  return num || 4
}

/** Estimate total song duration (seconds) from structure + bpm. */
export function estimateDuration(songState) {
  const bpb = beatsPerBar(songState.timeSignature)
  const secPerBeat = 60 / (songState.bpm || 120)
  const totalBars = (songState.structure || []).reduce(
    (sum, s) => sum + (s.bars || 0) * (s.repeat || 1),
    0,
  )
  return totalBars * bpb * secPerBeat
}

export function formatTime(seconds) {
  if (!isFinite(seconds) || seconds < 0) seconds = 0
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
