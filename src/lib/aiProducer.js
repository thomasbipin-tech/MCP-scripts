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
// Abort a live request that takes too long so the UI never gets stuck
// "thinking" — on timeout we fall back to the offline interpreter.
const LIVE_TIMEOUT_MS = Number(import.meta.env?.VITE_ANTHROPIC_TIMEOUT_MS) || 20000

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

// ----- Lyrics generator (offline) -----
// Builds a coherent, rhyming lyric sheet from curated couplets: distinct verses,
// one repeating chorus hook (with the theme woven in), a contrasting bridge, and
// mood-aware intros/outros. Fully local — works with zero setup.
const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s)

// Rhyming couplets ({theme}/{Theme} are slotted with the user's theme).
const VERSE_COUPLETS = [
  ['I still feel {theme} like a fire in my chest', "Chasing every second, never stopping to rest"],
  ['Headlights on the highway, neon in the rain', '{Theme} is the only thing that keeps me sane'],
  ['We were young and restless, dancing in the dark', 'Every spark between us left a permanent mark'],
  ['Footsteps in the silence, echoes of your name', 'Nothing in the morning ever feels the same'],
  ['City lights are calling, pulling me away', 'But the thought of {theme} is begging me to stay'],
  ['Rivers of the moment carry us along', 'Turning every heartbeat into a song'],
  ['Hold me in the chaos, steady when I fall', "You're the quiet answer underneath it all"],
  ['Miles of empty asphalt stretching out ahead', 'Living for the words we left but never said'],
  ['Smoke against the streetlight, shadows on the wall', 'I would trade it all just to hear you call'],
  ['Clocks are turning slowly, hands that never stay', 'Holding onto {theme} before it fades away'],
]

const CHORUS_HOOKS = [
  ["So hold on to {theme}, don't let it go", "We're burning like the embers, stealing the show", 'Hold on to {theme}, we never fold', 'Out here in the moment, breaking the mold'],
  ['{Theme}, you are the reason I’m alive', "Every time I'm falling, you're the reason I survive", '{Theme}, take me higher tonight', "Everything feels right when you're holding me tight"],
  ['This is our {theme}, and we own the night', 'Hearts beating louder, chasing the light', "This is our {theme}, we'll never hide", 'Riding every wave with you right by my side'],
  ['Run with me through {theme} and flame', 'Scream it to the sky, we are not the same', 'Run with me, we’ll never be tame', 'Carving out forever, leaving our name'],
]

const BRIDGE_COUPLETS = [
  ['And when the lights go down', "I'll still be around"],
  ['Maybe we were never meant to stay', "But I'd do it all again the same way"],
  ['Tear it all apart', "You're still my beating heart"],
  ['Even in the silence', 'You are my defiance'],
]

const INTRO_LINES = {
  energetic: ['(Yeah... here we go)'],
  aggressive: ['(Let it burn...)'],
  chill: ['(Mmm... easy now)'],
  dark: ['(Cold... so cold...)'],
  euphoric: ['(Ooh-ooh, take me up)'],
  dreamy: ['(Drifting... {theme}...)'],
  default: ['(Ooh... {theme}...)'],
}

const OUTRO_LINES = {
  default: ['So hold on to {theme}...', '(Don’t let it fade away)'],
  dreamy: ['(Ooh, {theme}...)', 'Till the morning light'],
  dark: ['(Fading... fading...)', 'Let the shadows take it all'],
}

const DEFAULT_THEME = {
  energetic: 'tonight',
  aggressive: 'the fire',
  chill: 'the moment',
  dark: 'the shadows',
  euphoric: 'the high',
  dreamy: 'a dream',
}

export function generateLyricsLocal(songState, theme = '') {
  const mood = songState.mood || 'default'
  const topic = String(theme || '').trim() || DEFAULT_THEME[mood] || 'tonight'
  const Topic = cap(topic)
  const fill = (line) => line.split('{theme}').join(topic).split('{Theme}').join(Topic)

  // Seeded RNG (varies a little each generate so "regenerate" gives fresh words).
  let seed = (topic.length * 7 + (songState.bpm || 120) + String(mood).length + (Math.floor(Date.now() / 1000) % 1000)) >>> 0
  const rnd = () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  }
  const pickFrom = (arr) => arr[Math.floor(rnd() * arr.length)]

  // One chorus, reused for every chorus section (like a real song).
  const chorus = pickFrom(CHORUS_HOOKS).map(fill)
  const bridge = pickFrom(BRIDGE_COUPLETS).map(fill)
  const intro = (INTRO_LINES[mood] || INTRO_LINES.default).map(fill)
  const outro = (OUTRO_LINES[mood] || OUTRO_LINES.default).map(fill)

  // Distinct verses: shuffle couplet indices, take two couplets per verse.
  const order = VERSE_COUPLETS.map((_, i) => i)
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1))
    ;[order[i], order[j]] = [order[j], order[i]]
  }
  let vptr = 0
  const nextVerse = () => {
    const a = VERSE_COUPLETS[order[vptr++ % order.length]]
    const b = VERSE_COUPLETS[order[vptr++ % order.length]]
    return [...a, ...b].map(fill)
  }

  const sections =
    songState.structure && songState.structure.length
      ? songState.structure
      : [{ type: 'verse', repeat: 1 }, { type: 'chorus', repeat: 1 }]

  const out = []
  sections.forEach((s) => {
    const label = cap(s.type) + (s.repeat > 1 ? ` (x${s.repeat})` : '')
    out.push(`[${label}]`)
    if (s.type === 'intro') out.push(...intro)
    else if (s.type === 'chorus') out.push(...chorus)
    else if (s.type === 'bridge') out.push(...bridge)
    else if (s.type === 'outro') out.push(...outro)
    else out.push(...nextVerse())
    out.push('')
  })
  return out.join('\n').trim()
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
    // Triad-leaning contour (root/third/fifth) so it stays consonant and hooky.
    degrees = [0, 2, 4, 2, 0, 4, 2, 0]
  }
  return degrees.map((d, idx) => ({ note: scale[d], step: idx, duration: '8n' }))
}

/** Generate a full 4-track starter song. */
export function generateSurpriseSong(songState) {
  const seed = (songState.genre || '').length + (songState.mood || '').length + Date.now() % 97
  const genre = pick(GENRES, seed)
  const mood = pick(MOODS, seed + 1)
  const key = pick(KEYS, seed + 2)
  const bpm = BPM_BY_GENRE[genre] || 120

  const tempState = { ...songState, key }
  // Genre-appropriate instrument lineups. Acoustic genres use the real sampled
  // instruments (piano/guitar/violin/bass/drums); electronic genres keep synths.
  const kit = GENRE_KIT[genre] || ['drums', 'bass', 'piano', 'guitar']
  const tracks = kit.map((inst, i) => buildKitTrack(inst, tempState, NEON_COLORS[i % NEON_COLORS.length], genre))

  const structure = [
    { type: 'intro', bars: 4, repeat: 1 },
    { type: 'verse', bars: 8, repeat: 2 },
    { type: 'chorus', bars: 8, repeat: 3 },
    { type: 'bridge', bars: 4, repeat: 1 },
    { type: 'outro', bars: 4, repeat: 1 },
  ]

  const lineup = tracks.map((t) => t.name.toLowerCase()).join(', ')
  return {
    changes: { genre, mood, key, bpm, tracks, structure, fadeOut: true },
    message: `Cooked up a ${mood} ${genre} starter in ${key} at ${bpm} BPM — ${lineup}.`,
    tip: 'Piano, guitar, bass, violin and drums use real instrument sounds; lead/synth/pad are electronic.',
    nextSuggestion: 'Hit play, tap the step grids to edit beats, or drop tracks into sections.',
  }
}

const GENRE_KIT = {
  'lo-fi': ['drums', 'bass', 'piano', 'guitar'],
  ambient: ['pad', 'piano', 'violin', 'bass'],
  'hip hop': ['drums', 'bass', 'piano', 'lead'],
  trap: ['drums', 'bass', 'lead', 'piano'],
  house: ['drums', 'bass', 'lead', 'pad'],
  electronic: ['drums', 'bass', 'lead', 'pad'],
  pop: ['drums', 'bass', 'piano', 'guitar'],
  rock: ['drums', 'bass', 'guitar', 'piano'],
  cinematic: ['drums', 'violin', 'piano', 'bass'],
}

const BPM_BY_GENRE = {
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

/**
 * "Super Generate" — produce N complete song versions derived from the current
 * song. The first couple keep the current genre; the rest explore neighbours.
 * Each varies mood, key, tempo, instrument lineup and arrangement.
 */
export function generateVariations(songState, count = 6) {
  const baseGenre = songState.genre || 'pop'
  const others = GENRES.filter((g) => g !== baseGenre)
  const out = []
  for (let i = 0; i < count; i++) {
    const genre = i < 2 ? baseGenre : others[i % others.length] || baseGenre
    const seed = baseGenre.length + i * 23 + (Math.floor(Date.now() / 997) % 100)
    const mood = MOODS[(seed + i) % MOODS.length]
    const key = KEYS[(seed * 2 + i * 5) % KEYS.length]
    const bpm = clamp((BPM_BY_GENRE[genre] || 120) + ((i % 3) - 1) * 6, 60, 180)
    const tempState = { ...songState, key }
    const kit = GENRE_KIT[genre] || ['drums', 'bass', 'piano', 'guitar']
    const tracks = kit.map((inst, k) => buildKitTrack(inst, tempState, NEON_COLORS[k % NEON_COLORS.length], genre))
    const structure = [
      { type: 'intro', bars: 4, repeat: 1 },
      { type: 'verse', bars: 8, repeat: 1 + (i % 2) },
      { type: 'chorus', bars: 8, repeat: 2 + (i % 2) },
      { type: 'bridge', bars: 4, repeat: 1 },
      { type: 'outro', bars: 4, repeat: 1 },
    ]
    out.push({
      id: i,
      label: `${mood} ${genre}`,
      genre,
      mood,
      key,
      bpm,
      instruments: kit,
      changes: { genre, mood, key, bpm, tracks, structure, fadeOut: true },
    })
  }
  return out
}

// Genre-appropriate 8-step drum grooves (kick/snare/hat per eighth note).
const GENRE_GROOVES = {
  rock: ['kick', 'hat', 'snare', 'hat', 'kick', 'hat', 'snare', 'hat'],
  pop: ['kick', 'hat', 'snare', 'hat', 'kick', '', 'snare', 'hat'],
  'lo-fi': ['kick', '', 'snare', '', '', 'kick', 'snare', ''],
  'hip hop': ['kick', '', 'snare', '', '', 'kick', 'snare', ''],
  trap: ['kick', '', 'snare', 'hat', 'kick', 'kick', 'snare', 'hat'],
  house: ['kick', 'hat', 'kick', 'hat', 'kick', 'hat', 'kick', 'hat'],
  electronic: ['kick', 'hat', 'snare', 'hat', 'kick', 'hat', 'snare', 'hat'],
  ambient: ['kick', '', '', '', 'snare', '', '', ''],
  cinematic: ['kick', '', '', '', 'snare', '', '', 'kick'],
}

// Mix balance: keep drums/bass present, pads/leads back so it isn't muddy.
const TRACK_VOLUME = { drums: 86, bass: 82, pad: 58, lead: 70, synth: 70, piano: 76, guitar: 74, violin: 70 }

function buildKitTrack(inst, tempState, color, genre) {
  const volume = TRACK_VOLUME[inst] ?? 76
  if (inst === 'drums') {
    return makeTrack({ instrument: 'drums', color, volume, pattern: GENRE_GROOVES[genre] })
  }
  if (inst === 'bass') return makeTrack({ instrument: 'bass', color, volume, notes: bassLine(tempState) })
  if (inst === 'pad') {
    return makeTrack({
      instrument: 'pad',
      color,
      volume,
      effects: { reverb: true, delay: false, distortion: false },
      notes: padChord(tempState),
    })
  }
  return makeTrack({ instrument: inst, color, volume, notes: generateMelodyFromHum(tempState, 'lead') })
}

// ----- Lyrics → Music -----
// Infer a song from lyrics: structure from [Section] headers, mood from the
// words, then build a few arrangements that fit.
const MOOD_WORDS = {
  energetic: ['run', 'fire', 'alive', 'burn', 'tonight', 'wild', 'race', 'loud', 'electric', 'jump'],
  aggressive: ['break', 'war', 'rage', 'fight', 'savage', 'thunder', 'storm', 'blood', 'scream', 'iron'],
  chill: ['easy', 'slow', 'calm', 'golden', 'sunset', 'breeze', 'quiet', 'drift', 'smooth', 'haze'],
  dark: ['shadow', 'cold', 'alone', 'fade', 'empty', 'silence', 'ashes', 'grey', 'lost', 'hollow'],
  euphoric: ['love', 'sky', 'high', 'light', 'heart', 'forever', 'glow', 'rise', 'free', 'alive'],
  dreamy: ['dream', 'float', 'ocean', 'star', 'silver', 'distant', 'soft', 'echo', 'sleep', 'drift'],
}

const MOOD_GENRES = {
  energetic: ['pop', 'rock', 'house'],
  aggressive: ['rock', 'trap', 'electronic'],
  chill: ['lo-fi', 'pop', 'ambient'],
  dark: ['cinematic', 'trap', 'electronic'],
  euphoric: ['house', 'pop', 'cinematic'],
  dreamy: ['ambient', 'lo-fi', 'cinematic'],
}

function inferMood(text) {
  const t = String(text).toLowerCase()
  let best = null
  let bestScore = 0
  for (const [mood, words] of Object.entries(MOOD_WORDS)) {
    const score = words.reduce((n, w) => n + (t.includes(w) ? 1 : 0), 0)
    if (score > bestScore) {
      bestScore = score
      best = mood
    }
  }
  return bestScore > 0 ? best : null
}

function parseStructure(text) {
  const known = ['intro', 'verse', 'chorus', 'bridge', 'outro']
  const out = []
  for (const line of String(text).split('\n')) {
    const m = line.match(/^\s*\[([a-zA-Z]+)(?:[^\d]*?(\d+))?/)
    if (!m) continue
    const type = m[1].toLowerCase()
    if (!known.includes(type)) continue
    const repeat = m[2] ? clamp(parseInt(m[2], 10), 1, 8) : 1
    const bars = type === 'intro' || type === 'outro' || type === 'bridge' ? 4 : 8
    out.push({ type, bars, repeat })
  }
  if (out.length) return out
  return [
    { type: 'intro', bars: 4, repeat: 1 },
    { type: 'verse', bars: 8, repeat: 1 },
    { type: 'chorus', bars: 8, repeat: 2 },
    { type: 'verse', bars: 8, repeat: 1 },
    { type: 'chorus', bars: 8, repeat: 2 },
    { type: 'outro', bars: 4, repeat: 1 },
  ]
}

/** Build N complete songs that fit the given lyrics. */
export function generateSongFromLyrics(lyrics, songState, count = 3) {
  const text = String(lyrics || '')
  const mood = inferMood(text) || songState.mood || 'energetic'
  const genres = MOOD_GENRES[mood] || ['pop', 'rock', 'lo-fi']
  const out = []
  for (let i = 0; i < count; i++) {
    const genre = genres[i % genres.length]
    const seed = text.length + i * 31 + (Math.floor(Date.now() / 997) % 100)
    const key = KEYS[(seed + i * 7) % KEYS.length]
    const bpm = clamp((BPM_BY_GENRE[genre] || 120) + ((i % 3) - 1) * 4, 60, 180)
    const tempState = { ...songState, key, mood }
    const kit = GENRE_KIT[genre] || ['drums', 'bass', 'piano', 'guitar']
    const tracks = kit.map((inst, k) => buildKitTrack(inst, tempState, NEON_COLORS[k % NEON_COLORS.length], genre))
    const structure = parseStructure(text).map((s) => ({ ...s }))
    out.push({
      id: i,
      label: `${mood} ${genre}`,
      genre,
      mood,
      key,
      bpm,
      instruments: kit,
      changes: { genre, mood, key, bpm, tracks, structure, fadeOut: true, lyrics: text },
    })
  }
  return out
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

// The producer persona + output contract live in the system prompt (stable
// across requests, so it caches well and steers more reliably than burying the
// instructions in the user turn).
const LIVE_SYSTEM_PROMPT = `You are an expert music producer AI collaborating inside a GarageBand-style, browser-based DAW called AI Music Studio.

The app's single source of truth is "songState":
{ bpm, key, timeSignature, genre, mood, masterVolume, fadeOut,
  structure: [ { type, bars, repeat } ],
  tracks:    [ { id, name, instrument, color, volume (0-100), muted, solo,
                 effects: { reverb, delay, distortion }, pattern, notes } ] }

Interpret the user's natural-language command and decide what to change.

Respond with ONLY a single JSON object — no prose, no markdown fences — in this exact shape:
{
  "changes": { /* only the top-level songState fields to update. For "tracks" or "structure" return the COMPLETE new array. Omit anything you don't change. */ },
  "message": "Friendly, concise explanation of what you changed",
  "tip": "A short pro music-production tip",
  "nextSuggestion": "What the user should try next"
}`

async function interpretLive(command, songState, context) {
  const body = {
    model: API_MODEL,
    max_tokens: 1000,
    system: LIVE_SYSTEM_PROMPT,
    messages: [
      {
        role: 'user',
        content: `Current songState: ${JSON.stringify(songState)}
Selected segment: ${context.selectedSegment || 'none'}; selected track id: ${context.selectedTrackId ?? 'none'}.
Command: "${command}"`,
      },
    ],
  }

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), LIVE_TIMEOUT_MS)
  let response
  try {
    response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true',
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    })
  } finally {
    clearTimeout(timer)
  }

  if (!response.ok) throw new Error(`Anthropic API ${response.status}`)
  const data = await response.json()
  // A model may decline a request (HTTP 200 + stop_reason "refusal"); treat it
  // as a failure so the caller falls back to the offline interpreter.
  if (data.stop_reason === 'refusal') throw new Error('Anthropic API declined the request')
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
