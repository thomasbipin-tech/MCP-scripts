// The "AI music producer".
//
// interpretCommand() turns a natural-language command into a set of changes to
// merge into songState, plus a friendly message, a production tip, and a
// next-step suggestion — exactly the shape the spec asks for.
//
// By default it uses a fully-functional, offline rule-based interpreter so the
// whole app works end-to-end with zero setup. If a VITE_ANTHROPIC_API_KEY is
// provided, it instead routes the command through the real Claude API and falls
// back to the local interpreter on any failure.

import {
  INSTRUMENT_IDS,
  INSTRUMENTS,
  KEYS,
  GENRES,
  MOODS,
  NEON_COLORS,
  SEGMENT_TYPES,
  makeTrack,
  scaleNotes,
  rootChord,
} from './constants.js'

const API_KEY = import.meta.env?.VITE_ANTHROPIC_API_KEY || ''
const API_MODEL = import.meta.env?.VITE_ANTHROPIC_MODEL || 'claude-sonnet-4-6'

export const usingLiveAI = Boolean(API_KEY)

const NUMBER_WORDS = {
  one: 1,
  two: 2,
  three: 3,
  four: 4,
  five: 5,
  six: 6,
  seven: 7,
  eight: 8,
  nine: 9,
  ten: 10,
  twice: 2,
}

function parseNumber(text, fallback) {
  const digit = text.match(/\b(\d+)\b/)
  if (digit) return parseInt(digit[1], 10)
  for (const [word, n] of Object.entries(NUMBER_WORDS)) {
    if (new RegExp(`\\b${word}\\b`).test(text)) return n
  }
  return fallback
}

function pick(arr, seed = 0) {
  return arr[Math.abs(Math.floor(seed)) % arr.length]
}

const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n))

const TIPS = [
  'Leave space in the low end — sidechain the bass to the kick for punch.',
  'A little reverb on the snare glues a kit together; too much washes it out.',
  'Contrast verses and choruses in energy, not just volume.',
  'Pan layered instruments slightly apart so each has its own room.',
  'High-pass everything except kick and bass to clear up mud.',
  'Automate filter cutoff over a build to create tension before a drop.',
  'Keep your loudest element 6dB above the next — clarity beats loudness.',
  'A short slap delay on a lead widens it without muddying the mix.',
]

function tipFor(seed) {
  return TIPS[Math.abs(seed) % TIPS.length]
}

/** Find a track by spoken reference: "track 2", an instrument name, or selection. */
function resolveTrack(text, tracks, selectedTrackId) {
  const m = text.match(/track\s*(\d+)/)
  if (m) {
    const idx = parseInt(m[1], 10) - 1
    if (tracks[idx]) return tracks[idx]
  }
  for (const inst of INSTRUMENT_IDS) {
    if (new RegExp(`\\b${inst}s?\\b`).test(text)) {
      const found = tracks.find((t) => t.instrument === inst)
      if (found) return found
    }
  }
  for (const t of tracks) {
    if (text.includes(t.name.toLowerCase())) return t
  }
  if (selectedTrackId != null) return tracks.find((t) => t.id === selectedTrackId) || null
  return null
}

function detectInstrument(text) {
  for (const inst of INSTRUMENT_IDS) {
    if (new RegExp(`\\b${inst}s?\\b`).test(text)) return inst
  }
  if (/\bbeat|kick|percussion\b/.test(text)) return 'drums'
  if (/\bmelody|lead|hook\b/.test(text)) return 'lead'
  if (/\bpad|atmosphere|ambient\b/.test(text)) return 'pad'
  return null
}

const EFFECTS = ['reverb', 'delay', 'distortion']
function detectEffect(text) {
  return EFFECTS.find((fx) => text.includes(fx)) || null
}

/**
 * The local rule-based interpreter.
 * @returns {{changes:object, message:string, tip:string, nextSuggestion:string}}
 */
export function interpretLocal(command, songState, context = {}) {
  const text = String(command).toLowerCase().trim()
  const tracks = songState.tracks || []
  const seed = text.length + tracks.length

  const ok = (changes, message, nextSuggestion) => ({
    changes,
    message,
    tip: tipFor(seed),
    nextSuggestion,
  })

  if (!text) {
    return ok({}, "I didn't catch that — try a command like “add a bass track”.", 'Say “surprise me”.')
  }

  // ----- Surprise me / generate a song -----
  if (/surprise me|generate (a )?song|make me a song|starter song/.test(text)) {
    return generateSurpriseSong(songState)
  }

  // ----- Tempo -----
  if (/tempo|bpm|speed|fast|slow/.test(text)) {
    const explicit = text.match(/(\d{2,3})\s*(bpm)?/)
    let bpm = songState.bpm
    let how
    if (explicit && parseInt(explicit[1], 10) >= 40) {
      bpm = clamp(parseInt(explicit[1], 10), 40, 240)
      how = `set the tempo to ${bpm} BPM`
    } else if (/faster|speed up|quicker|heavier|energetic|harder/.test(text)) {
      bpm = clamp(songState.bpm + 12, 40, 240)
      how = `pushed the tempo up to ${bpm} BPM`
    } else if (/slower|slow down|softer|chill|relax|calm/.test(text)) {
      bpm = clamp(songState.bpm - 12, 40, 240)
      how = `eased the tempo down to ${bpm} BPM`
    }
    if (how) return ok({ bpm }, `I ${how}.`, 'Try “make it more energetic” or add another layer.')
  }

  // ----- Add a track -----
  if (/\badd|create|lay(er)? down|bring in|give me\b/.test(text) && !detectEffect(text)) {
    const inst = detectInstrument(text) || 'synth'
    const color = NEON_COLORS[tracks.length % NEON_COLORS.length]
    const newTrack = makeTrack({
      instrument: inst,
      color,
      notes: ['lead', 'synth', 'piano', 'guitar', 'violin', 'pad'].includes(inst)
        ? defaultMelody(songState, inst)
        : null,
    })
    return ok(
      { tracks: [...tracks, newTrack] },
      `Added a ${newTrack.name} track in ${songState.key}. It's lane ${tracks.length + 1}.`,
      'Assign it a melody by humming, or say “add reverb to ' + newTrack.name.toLowerCase() + '”.',
    )
  }

  // ----- Effects -----
  const fx = detectEffect(text)
  if (fx) {
    const target = resolveTrack(text, tracks, context.selectedTrackId)
    if (!target) {
      return ok({}, `Which track should I add ${fx} to? Try “add ${fx} to track 1”.`, 'Name a track or select one first.')
    }
    const remove = /remove|less|no |turn off|kill|drop the/.test(text)
    const nextTracks = tracks.map((t) =>
      t.id === target.id ? { ...t, effects: { ...t.effects, [fx]: !remove } } : t,
    )
    return ok(
      { tracks: nextTracks },
      `${remove ? 'Removed' : 'Added'} ${fx} ${remove ? 'from' : 'to'} ${target.name}.`,
      remove ? 'Try a different FX, or tweak the mix.' : `Blend it in — drop ${target.name}'s volume a touch so it sits back.`,
    )
  }

  // ----- Mute / Solo / Delete a track -----
  if (/mute|solo|delete|remove track|kill track/.test(text)) {
    const target = resolveTrack(text, tracks, context.selectedTrackId)
    if (!target) return ok({}, 'Tell me which track — e.g. “mute track 2”.', 'Reference a track number or name.')
    if (/delete|remove track|kill track/.test(text)) {
      return ok(
        { tracks: tracks.filter((t) => t.id !== target.id) },
        `Deleted ${target.name}.`,
        'Add a fresh layer whenever you’re ready.',
      )
    }
    const field = text.includes('solo') ? 'solo' : 'muted'
    const nextTracks = tracks.map((t) => (t.id === target.id ? { ...t, [field]: !t[field] } : t))
    return ok(
      { tracks: nextTracks },
      `${!target[field] ? (field === 'solo' ? 'Soloed' : 'Muted') : 'Un-' + field} ${target.name}.`,
      'Solo a track to dial in its tone, then un-solo to hear it in context.',
    )
  }

  // ----- Volume (louder / quieter, master or per-track) -----
  if (/louder|quieter|volume|turn up|turn down|boost|lower/.test(text)) {
    const target = resolveTrack(text, tracks, context.selectedTrackId)
    const up = /louder|turn up|boost|raise|more volume/.test(text)
    const delta = up ? 12 : -12
    if (target) {
      const nextTracks = tracks.map((t) =>
        t.id === target.id ? { ...t, volume: clamp(t.volume + delta, 0, 100) } : t,
      )
      return ok({ tracks: nextTracks }, `Turned ${target.name} ${up ? 'up' : 'down'}.`, 'Balance is everything — A/B against the other tracks.')
    }
    return ok(
      { masterVolume: clamp((songState.masterVolume ?? 80) + delta, 0, 100) },
      `Brought the master ${up ? 'up' : 'down'}.`,
      'Mix at a comfortable level — loud mixes trick your ears.',
    )
  }

  // ----- Repeat a section ("make the chorus repeat 4 times", "chorus x3") -----
  if (/repeat|times|loop|x\s*\d/.test(text)) {
    const seg = SEGMENT_TYPES.find((s) => text.includes(s)) || context.selectedSegment
    if (seg) {
      const n = clamp(parseNumber(text, 2), 1, 8)
      const structure = songState.structure.map((s) =>
        s.type === seg ? { ...s, repeat: n } : s,
      )
      return ok(
        { structure },
        `The ${seg} now repeats ${n}×.`,
        'A repeated chorus is your hook — make sure it earns the repeat.',
      )
    }
  }

  // ----- Fade out the ending -----
  if (/fade\s*out|fade the end|fade ending/.test(text)) {
    return ok(
      { fadeOut: true },
      'Added a fade-out across the outro — the master will ramp down to silence.',
      'Pair the fade with a filter sweep for a smoother exit.',
    )
  }
  if (/no fade|remove fade|hard ending|stop fade/.test(text)) {
    return ok({ fadeOut: false }, 'Removed the fade-out — the track now ends cold.', 'A hard ending hits harder on energetic tracks.')
  }

  // ----- Add a structure section -----
  for (const seg of SEGMENT_TYPES) {
    if (new RegExp(`add (a |an )?${seg}`).test(text)) {
      const bars = seg === 'intro' || seg === 'outro' ? 4 : 8
      const structure = [...songState.structure, { type: seg, bars, repeat: 1 }]
      return ok({ structure }, `Appended ${seg === 'intro' ? 'an' : 'a'} ${seg} (${bars} bars).`, 'Drag sections to reorder the arrangement.')
    }
  }

  // ----- Key -----
  if (/\bkey\b|major|minor/.test(text)) {
    const found = KEYS.find((k) => text.includes(k.toLowerCase()))
    if (found) return ok({ key: found }, `Switched to ${found}.`, 'New melodies will follow this key automatically.')
  }

  // ----- Genre -----
  const genre = GENRES.find((g) => text.includes(g))
  if (genre && /genre|style|make it|sound like/.test(text)) {
    return ok({ genre }, `Leaning into a ${genre} feel.`, `I'll bias suggestions toward ${genre}. Try “surprise me” for a ${genre} starter.`)
  }

  // ----- Mood / vibe ("heavier", "softer", "more energetic") -----
  const moodMap = {
    heavier: 'aggressive',
    harder: 'aggressive',
    aggressive: 'aggressive',
    softer: 'chill',
    chill: 'chill',
    calm: 'chill',
    relaxed: 'chill',
    dark: 'dark',
    moody: 'dark',
    euphoric: 'euphoric',
    uplifting: 'euphoric',
    energetic: 'energetic',
    dreamy: 'dreamy',
  }
  for (const [word, mood] of Object.entries(moodMap)) {
    if (text.includes(word)) {
      const changes = { mood }
      // Heavier => distortion on bass/drums + a tempo nudge.
      if (mood === 'aggressive') {
        changes.tracks = tracks.map((t) =>
          ['bass', 'drums', 'lead'].includes(t.instrument)
            ? { ...t, effects: { ...t.effects, distortion: true } }
            : t,
        )
        changes.bpm = clamp(songState.bpm + 8, 40, 240)
      } else if (mood === 'chill' || mood === 'dreamy') {
        changes.tracks = tracks.map((t) => ({ ...t, effects: { ...t.effects, reverb: true } }))
        changes.bpm = clamp(songState.bpm - 8, 40, 240)
      }
      return ok(changes, `Pushed the vibe toward ${mood}.`, 'Reinforce the mood with FX and arrangement, not just tempo.')
    }
  }

  // ----- Fallback -----
  return ok(
    {},
    `I heard “${command}”. I can add tracks, set tempo/key, add FX, repeat sections, change the mood, or fade the ending.`,
    'Try “add a bass track”, “speed up to 140 BPM”, or “make it heavier”.',
  )
}

/** A short, key-aware default melody for a freshly added melodic track. */
function defaultMelody(songState, instrument) {
  const octave = instrument === 'bass' ? 2 : instrument === 'pad' ? 3 : 4
  const scale = scaleNotes(songState.key, octave, 8)
  const order = [0, 2, 4, 2, 5, 4, 2, 0]
  return order.map((i, idx) => ({ note: scale[i], step: idx, duration: '8n' }))
}

/**
 * Turn a hummed-melody description (and optional contour features) into a note
 * sequence in the current key. Used by the Hum-to-Melody recorder.
 */
export function generateMelodyFromHum(songState, instrument = 'lead', contour = []) {
  const octave = instrument === 'bass' ? 2 : 4
  const scale = scaleNotes(songState.key, octave, 8)
  const len = 8
  let degrees
  if (contour && contour.length >= len) {
    // Map a normalized 0..1 loudness/pitch contour onto scale degrees.
    const stepSize = Math.floor(contour.length / len)
    degrees = Array.from({ length: len }, (_, i) => {
      const v = contour[i * stepSize] ?? 0.5
      return clamp(Math.round(v * (scale.length - 1)), 0, scale.length - 1)
    })
  } else {
    degrees = [0, 2, 4, 5, 4, 2, 1, 0]
  }
  return degrees.map((d, idx) => ({ note: scale[d], step: idx, duration: '8n' }))
}

/** Generate a full 4-track starter song. */
export function generateSurpriseSong(songState) {
  const seed = (songState.genre || '').length + (songState.mood || '').length + Date.now() % 97
  const genre = pick(GENRES, seed)
  const mood = pick(MOODS, seed + 1)
  const key = pick(KEYS, seed + 2)
  const bpmByGenre = {
    'lo-fi': 78,
    ambient: 70,
    'hip hop': 90,
    trap: 140,
    house: 124,
    electronic: 126,
    pop: 118,
    rock: 132,
    cinematic: 90,
  }
  const bpm = bpmByGenre[genre] || 120

  const tempState = { ...songState, key }
  const tracks = [
    makeTrack({ instrument: 'drums', color: NEON_COLORS[0] }),
    makeTrack({ instrument: 'bass', color: NEON_COLORS[1], notes: bassLine(tempState) }),
    makeTrack({
      instrument: 'lead',
      color: NEON_COLORS[2],
      notes: generateMelodyFromHum(tempState, 'lead'),
    }),
    makeTrack({
      instrument: 'pad',
      color: NEON_COLORS[3],
      effects: { reverb: true, delay: false, distortion: false },
      notes: padChord(tempState),
    }),
  ]
  const structure = [
    { type: 'intro', bars: 4, repeat: 1 },
    { type: 'verse', bars: 8, repeat: 2 },
    { type: 'chorus', bars: 8, repeat: 3 },
    { type: 'bridge', bars: 4, repeat: 1 },
    { type: 'outro', bars: 4, repeat: 1 },
  ]

  return {
    changes: { genre, mood, key, bpm, tracks, structure, fadeOut: true },
    message: `Cooked up a ${mood} ${genre} starter in ${key} at ${bpm} BPM — drums, bass, a lead hook, and a lush pad.`,
    tip: 'Start arrangements with drums + bass; melody and pads layer on top.',
    nextSuggestion: 'Hit play, then hum a new melody or say “make the chorus repeat 4 times”.',
  }
}

function bassLine(songState) {
  const scale = scaleNotes(songState.key, 2, 8)
  const order = [0, 0, 4, 0, 5, 0, 4, 2]
  return order.map((i, idx) => ({ note: scale[i], step: idx, duration: '8n' }))
}

function padChord(songState) {
  const chord = rootChord(songState.key, 3)
  return chord.map((note, idx) => ({ note, step: idx * 2, duration: '2n', chord: true }))
}

// ----- Optional live Claude API path -----
async function interpretLive(command, songState, context) {
  const userCommand = command
  const body = {
    model: API_MODEL,
    max_tokens: 1000,
    messages: [
      {
        role: 'user',
        content: `You are an expert music producer AI collaborating inside a GarageBand-style DAW.
Current song state: ${JSON.stringify(songState)}
Selected segment: ${context.selectedSegment || 'none'}; selected track id: ${context.selectedTrackId ?? 'none'}.
User command: "${userCommand}"

Respond ONLY with a single JSON object (no markdown fences):
{
  "changes": { ...top-level fields to update in songState; for "tracks" or "structure" return the COMPLETE new array... },
  "message": "Friendly explanation of what you changed",
  "tip": "A short pro music production tip",
  "nextSuggestion": "What the user should try next"
}`,
      },
    ],
  }

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': API_KEY,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify(body),
  })
  if (!response.ok) throw new Error(`Anthropic API ${response.status}`)
  const data = await response.json()
  const text = (data.content || []).map((c) => c.text || '').join('')
  const match = text.match(/\{[\s\S]*\}/)
  if (!match) throw new Error('No JSON in AI response')
  const parsed = JSON.parse(match[0])
  return {
    changes: parsed.changes || {},
    message: parsed.message || 'Done.',
    tip: parsed.tip || tipFor(text.length),
    nextSuggestion: parsed.nextSuggestion || 'Keep layering.',
  }
}

/**
 * Public entry point. Always resolves to a result object; never throws.
 */
export async function interpretCommand(command, songState, context = {}) {
  if (usingLiveAI) {
    try {
      return await interpretLive(command, songState, context)
    } catch (err) {
      const local = interpretLocal(command, songState, context)
      local.message = `(offline fallback) ${local.message}`
      return local
    }
  }
  // Tiny delay so the "AI is thinking…" animation is visible.
  await new Promise((r) => setTimeout(r, 420))
  return interpretLocal(command, songState, context)
}
