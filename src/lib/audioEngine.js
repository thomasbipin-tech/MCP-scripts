// Tone.js playback engine.
//
// Builds a per-track signal graph (instrument → distortion → delay → reverb →
// track volume → master volume → analyser → speakers), schedules the song from
// its structure, drives a looping playhead, and exposes a spectrum analyser.
//
// The engine keeps an internal copy of songState (set via setSongState) and
// reads it on every scheduler tick, so volume/mute/FX/key/tempo edits take
// effect live without rebuilding the graph.

import * as Tone from 'tone'
import { beatsPerBar, scaleNotes, rootChord } from './constants.js'

const STEPS_PER_BAR = 8 // eighth-note grid

function volToDb(pct) {
  if (pct <= 0) return -Infinity
  // 100 -> 0dB, 50 -> ~-9dB, near 0 -> very quiet.
  return 20 * Math.log10(pct / 100)
}

function makeInstrument(inst) {
  switch (inst) {
    case 'drums':
      return {
        kind: 'drums',
        kick: new Tone.MembraneSynth({
          pitchDecay: 0.04,
          octaves: 6,
          envelope: { attack: 0.001, decay: 0.4, sustain: 0 },
        }),
        snare: new Tone.MetalSynth({
          frequency: 200,
          envelope: { attack: 0.001, decay: 0.18, release: 0.02 },
          harmonicity: 5.1,
          modulationIndex: 32,
          resonance: 4000,
          octaves: 1.5,
        }),
        hat: new Tone.MetalSynth({
          frequency: 400,
          envelope: { attack: 0.001, decay: 0.05, release: 0.01 },
          harmonicity: 5.1,
          modulationIndex: 32,
          resonance: 6000,
          octaves: 1,
        }),
      }
    case 'bass':
      return {
        kind: 'mono',
        node: new Tone.Synth({
          oscillator: { type: 'square' },
          envelope: { attack: 0.02, decay: 0.2, sustain: 0.6, release: 0.4 },
        }),
      }
    case 'pad':
      return {
        kind: 'poly',
        node: new Tone.PolySynth(Tone.AMSynth, {
          harmonicity: 2,
          envelope: { attack: 0.6, decay: 0.4, sustain: 0.8, release: 2 },
          modulationEnvelope: { attack: 0.8, decay: 0.2, sustain: 0.6, release: 1.5 },
        }),
      }
    case 'piano':
      return {
        kind: 'poly',
        node: new Tone.PolySynth(Tone.Synth, {
          oscillator: { type: 'triangle' },
          envelope: { attack: 0.005, decay: 0.6, sustain: 0.1, release: 0.8 },
        }),
      }
    case 'guitar':
      return {
        kind: 'poly',
        node: new Tone.PolySynth(Tone.Synth, {
          oscillator: { type: 'sawtooth' },
          envelope: { attack: 0.005, decay: 0.3, sustain: 0.2, release: 0.5 },
        }),
      }
    case 'violin':
      return {
        kind: 'poly',
        node: new Tone.PolySynth(Tone.Synth, {
          oscillator: { type: 'sawtooth' },
          envelope: { attack: 0.3, decay: 0.1, sustain: 0.9, release: 0.6 },
        }),
      }
    case 'lead':
    case 'synth':
    default:
      return {
        kind: 'poly',
        node: new Tone.PolySynth(Tone.Synth, {
          oscillator: { type: 'sawtooth' },
          envelope: { attack: 0.01, decay: 0.2, sustain: 0.4, release: 0.4 },
        }),
      }
  }
}

function instrumentNodes(graph) {
  return graph.instrument.kind === 'drums'
    ? [graph.instrument.kick, graph.instrument.snare, graph.instrument.hat]
    : [graph.instrument.node]
}

export class AudioEngine {
  constructor() {
    this.ready = false
    this.graphs = new Map() // trackId -> { instrument, dist, delay, reverb, volume }
    this.songState = null
    this.loopId = null
    this.startOffset = 0 // Tone.Transport.seconds at which the current play began
    this.master = null
    this.analyser = null
    this.isPlaying = false
  }

  async init() {
    if (this.ready) return
    await Tone.start()
    this.master = new Tone.Volume(volToDb(80))
    this.analyser = new Tone.Analyser('fft', 64)
    this.master.connect(this.analyser)
    this.master.toDestination()
    Tone.Transport.bpm.value = 120
    this.ready = true
  }

  setMasterVolume(pct) {
    if (this.master) this.master.volume.rampTo(volToDb(pct), 0.05)
  }

  setBpm(bpm) {
    if (this.ready) Tone.Transport.bpm.rampTo(bpm, 0.1)
  }

  /** Create/update/dispose track graphs to match the current track list. */
  syncTracks(tracks) {
    if (!this.ready) return
    const seen = new Set()

    for (const track of tracks) {
      seen.add(track.id)
      let g = this.graphs.get(track.id)
      if (!g || g.instrumentId !== track.instrument) {
        if (g) this.disposeGraph(g)
        g = this.buildGraph(track)
        this.graphs.set(track.id, g)
      }
      this.applyTrackParams(g, track, tracks)
    }

    for (const [id, g] of this.graphs) {
      if (!seen.has(id)) {
        this.disposeGraph(g)
        this.graphs.delete(id)
      }
    }
  }

  buildGraph(track) {
    const instrument = makeInstrument(track.instrument)
    const dist = new Tone.Distortion(0.6)
    dist.wet.value = 0
    const delay = new Tone.FeedbackDelay('8n', 0.35)
    delay.wet.value = 0
    const reverb = new Tone.Reverb({ decay: 3, preDelay: 0.01 })
    reverb.wet.value = 0
    const volume = new Tone.Volume(volToDb(track.volume))

    instrumentNodes({ instrument }).forEach((n) => n.chain(dist, delay, reverb, volume))
    volume.connect(this.master)

    return { instrument, instrumentId: track.instrument, dist, delay, reverb, volume }
  }

  applyTrackParams(g, track, allTracks) {
    const anySolo = allTracks.some((t) => t.solo)
    const audible = !track.muted && (!anySolo || track.solo)
    g.volume.volume.rampTo(audible ? volToDb(track.volume) : -Infinity, 0.05)
    g.reverb.wet.rampTo(track.effects.reverb ? 0.45 : 0, 0.1)
    g.delay.wet.rampTo(track.effects.delay ? 0.3 : 0, 0.1)
    g.dist.wet.rampTo(track.effects.distortion ? 0.5 : 0, 0.1)
  }

  disposeGraph(g) {
    instrumentNodes(g).forEach((n) => n.dispose())
    g.dist.dispose()
    g.delay.dispose()
    g.reverb.dispose()
    g.volume.dispose()
  }

  setSongState(songState) {
    const prevBpm = this.songState?.bpm
    this.songState = songState
    if (this.ready) {
      if (prevBpm !== songState.bpm) this.setBpm(songState.bpm)
      this.setMasterVolume(songState.masterVolume ?? 80)
      this.syncTracks(songState.tracks)
    }
  }

  totalBars() {
    return (this.songState?.structure || []).reduce(
      (sum, s) => sum + (s.bars || 0) * (s.repeat || 1),
      0,
    )
  }

  /** Expanded section boundaries in bars: [{type, startBar, endBar}]. */
  sectionMap() {
    const map = []
    let bar = 0
    for (const s of this.songState?.structure || []) {
      const span = (s.bars || 0) * (s.repeat || 1)
      map.push({ type: s.type, startBar: bar, endBar: bar + span })
      bar += span
    }
    return map
  }

  sectionAt(bar) {
    return this.sectionMap().find((s) => bar >= s.startBar && bar < s.endBar)?.type || 'verse'
  }

  gate(inst, section) {
    if (section === 'intro') return inst !== 'lead'
    if (section === 'outro') return inst !== 'lead'
    return true
  }

  async play() {
    await this.init()
    this.syncTracks(this.songState.tracks)
    this.setBpm(this.songState.bpm)
    this.setMasterVolume(this.songState.masterVolume ?? 80)

    if (this.loopId == null) this.scheduleLoop()

    if (Tone.Transport.state !== 'started') {
      Tone.Transport.start()
    }
    this.isPlaying = true
  }

  scheduleLoop() {
    let step = 0
    this.loopId = Tone.Transport.scheduleRepeat((time) => {
      const total = this.totalBars() * STEPS_PER_BAR
      if (total <= 0) return
      const g = step % total
      const stepInBar = g % STEPS_PER_BAR
      const bar = Math.floor(g / STEPS_PER_BAR)
      const section = this.sectionAt(bar)
      this.triggerStep(stepInBar, bar, section, time)
      step++
    }, '8n')
  }

  triggerStep(stepInBar, bar, section, time) {
    const ss = this.songState
    if (!ss) return
    const bpb = beatsPerBar(ss.timeSignature)
    const eighth = 60 / ss.bpm / 2

    // Master fade-out across the outro.
    if (ss.fadeOut && this.master) {
      const sm = this.sectionMap()
      const outro = sm.find((s) => s.type === 'outro')
      if (outro && bar >= outro.startBar) {
        const frac = (bar - outro.startBar) / Math.max(1, outro.endBar - outro.startBar)
        const target = volToDb((ss.masterVolume ?? 80) * (1 - frac))
        this.master.volume.rampTo(target, 0.2)
      } else if (stepInBar === 0 && bar === 0) {
        this.setMasterVolume(ss.masterVolume ?? 80)
      }
    }

    for (const track of ss.tracks) {
      const g = this.graphs.get(track.id)
      if (!g) continue
      if (!this.gate(track.instrument, section)) continue

      if (track.instrument === 'drums') {
        const hit = track.pattern?.[stepInBar % (track.pattern.length || 8)]
        try {
          if (hit === 'kick') g.instrument.kick.triggerAttackRelease('C1', '8n', time)
          else if (hit === 'snare') g.instrument.snare.triggerAttackRelease('16n', time)
          else if (hit === 'hat') g.instrument.hat.triggerAttackRelease('32n', time)
        } catch (_) {
          /* overlapping triggers can throw; ignore */
        }
        continue
      }

      // Melodic tracks.
      const dur = bpb >= 4 ? '8n' : '8n'
      try {
        if (Array.isArray(track.notes) && track.notes.length) {
          const hits = track.notes.filter((n) => (n.step ?? 0) % STEPS_PER_BAR === stepInBar)
          if (hits.length) {
            const node = g.instrument.node
            if (g.instrument.kind === 'poly') {
              node.triggerAttackRelease(
                hits.map((h) => h.note),
                hits[0].duration || dur,
                time,
              )
            } else {
              node.triggerAttackRelease(hits[0].note, hits[0].duration || dur, time)
            }
          }
        } else if (track.pattern?.[stepInBar]) {
          // No melody assigned: pulse the key root / chord.
          const node = g.instrument.node
          if (track.instrument === 'pad') {
            node.triggerAttackRelease(rootChord(ss.key, 3), '2n', time)
          } else if (track.instrument === 'bass') {
            node.triggerAttackRelease(scaleNotes(ss.key, 2, 1)[0], dur, time)
          } else if (g.instrument.kind === 'poly') {
            node.triggerAttackRelease(scaleNotes(ss.key, 4, 1)[0], dur, time)
          } else {
            node.triggerAttackRelease(scaleNotes(ss.key, 3, 1)[0], dur, time)
          }
        }
      } catch (_) {
        /* ignore overlapping voice errors */
      }
    }
  }

  pause() {
    if (this.ready && Tone.Transport.state === 'started') {
      Tone.Transport.pause()
      this.isPlaying = false
    }
  }

  stop() {
    if (this.ready) {
      Tone.Transport.stop()
      Tone.Transport.position = 0
      this.isPlaying = false
      this.setMasterVolume(this.songState?.masterVolume ?? 80)
    }
  }

  /** Playback progress 0..1 across the whole arrangement (loops). */
  getProgress() {
    if (!this.ready || !this.songState) return 0
    const totalSec = this.totalBars() * beatsPerBar(this.songState.timeSignature) * (60 / this.songState.bpm)
    if (totalSec <= 0) return 0
    return (Tone.Transport.seconds % totalSec) / totalSec
  }

  /** Normalized spectrum magnitudes (array of 0..1). */
  getSpectrum() {
    if (!this.analyser) return []
    const values = this.analyser.getValue() // dB, typically -100..0
    return Array.from(values, (v) => {
      const norm = (v + 100) / 100
      return Math.max(0, Math.min(1, norm))
    })
  }

  /** Preview a melody on a chosen instrument (used by the hum recorder). */
  async previewMelody(notes, instrument = 'lead') {
    await this.init()
    const inst = makeInstrument(instrument)
    const reverb = new Tone.Reverb({ decay: 2, wet: 0.3 })
    const out = new Tone.Volume(volToDb(85))
    instrumentNodes({ instrument: inst }).forEach((n) => n.chain(reverb, out))
    out.toDestination()

    const now = Tone.now() + 0.1
    const eighth = 60 / (this.songState?.bpm || 120) / 2
    notes.forEach((n) => {
      const t = now + (n.step ?? 0) * eighth
      const node = inst.kind === 'drums' ? inst.kick : inst.node
      try {
        node.triggerAttackRelease(n.note, n.duration || '8n', t)
      } catch (_) {
        /* ignore */
      }
    })

    const totalSec = (notes.length + 2) * eighth + 2.5
    setTimeout(() => {
      instrumentNodes({ instrument: inst }).forEach((nn) => nn.dispose())
      reverb.dispose()
      out.dispose()
    }, totalSec * 1000)
  }

  dispose() {
    if (this.loopId != null) Tone.Transport.clear(this.loopId)
    this.loopId = null
    for (const g of this.graphs.values()) this.disposeGraph(g)
    this.graphs.clear()
    if (this.analyser) this.analyser.dispose()
    if (this.master) this.master.dispose()
    this.ready = false
  }
}

let _engine = null
export function getEngine() {
  if (!_engine) _engine = new AudioEngine()
  return _engine
}
