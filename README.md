# 🎛️ AI Music Studio

A GarageBand-style, AI-powered DAW that runs entirely in the browser — voice
commands, hum-to-melody, layered tracks, a song-structure timeline, real Tone.js
playback, and an AI producer that responds to everything you do.

Built with **React + Vite**, **Tone.js**, and the native **Web Speech** /
**MediaRecorder** APIs.

![dark studio UI](https://img.shields.io/badge/aesthetic-neon%20studio-00f5ff) ![stack](https://img.shields.io/badge/react%20+%20vite%20+%20tone.js-12121a)

## Quick start

```bash
npm install
npm run dev      # http://localhost:5173
```

Build / preview a production bundle:

```bash
npm run build
npm run preview
```

> **Audio note:** browsers only start audio after a user gesture — click **Play**
> (or **Preview**) once and the engine spins up. Use Chrome/Edge for the full
> voice-command experience (Web Speech API). Everywhere else, type commands into
> the AI Producer panel — every feature still works.

### Use it from your phone or iPad (same Wi‑Fi)

`npm run dev` binds to your whole network (`host: true`) and serves over HTTPS
(self‑signed cert via `@vitejs/plugin-basic-ssl`). On another device, open the
**Network** URL Vite prints — `https://<your-laptop-ip>:5173`.

- The first visit shows a "Not Private" / certificate warning — tap through it
  (**Show Details → visit this website**) to trust the self‑signed cert.
- HTTPS is what lets iOS Safari grant **microphone** access, so the voice mic and
  hum recorder work on the iPad. (Over plain HTTP, iOS blocks the mic and only
  typed commands work.)
- If a device can't connect, allow port `5173` through your laptop's firewall and
  confirm both devices are on the same network.

## Features

| # | Feature | What it does |
|---|---------|--------------|
| 1 | **Voice Command System** | Big mic button (Web Speech API), live transcript, "AI is thinking…" state. Parses commands like *"add a drum track"*, *"speed up to 140 BPM"*, *"add reverb to track 2"*, *"make it heavier"*. |
| 2 | **Hum-to-Melody Recorder** | Record a hum (MediaRecorder), see its waveform, generate a key-aware note sequence, view it as a piano-roll strip, pick an instrument, and preview it with Tone.js. |
| 3 | **Interactive Layer System** | Draggable track lanes with neon borders, instrument icons, breathing waveform blocks, volume sliders, mute/solo, reverb/delay/distortion toggles, loop badges, and delete. |
| 4 | **Song Structure Editor** | Horizontal timeline of draggable Intro/Verse/Chorus/Bridge/Outro blocks, click-to-select, `x3` repeat badges with +/- controls, live duration estimate, and a moving playhead. |
| 5 | **AI Collaboration Panel** | Chat log of every change. After each command the AI replies with *what it changed*, a *production tip*, and a *next-step suggestion*. Text-input fallback included. |
| 6 | **Playback Engine (Tone.js)** | Play/Pause/Stop transport, BPM +/-, bouncing playhead, MembraneSynth/MetalSynth drums, square-wave bass, PolySynth lead, AMSynth pad with reverb, master volume knob, and a live spectrum analyser. |
| 7 | **Song Settings** | Key, time-signature, genre and mood selectors (the AI uses these to bias suggestions) and a **Surprise me** button that generates a full 4-track starter song. |

## How the "AI producer" works

Every voice/text command, plus the "Surprise me" and melody generators, runs
through `src/lib/aiProducer.js`.

- **Built-in mode (default).** A robust rule-based interpreter maps natural
  language onto changes to the central `songState`. No keys, no network — the
  whole app works offline, end to end.
- **Live Claude mode (optional).** Copy `.env.example` to `.env` and set
  `VITE_ANTHROPIC_API_KEY`. Commands are then sent to the real Claude API
  (`claude-sonnet-4-6` by default), and the app falls back to the built-in
  interpreter automatically if a request fails.

  ⚠️ A key placed in a Vite env var is bundled into client-side JS. Use a
  throwaway/scoped key for local experimentation only; for production, proxy the
  request through a backend.

The single source of truth is the `songState` object (see
`src/lib/constants.js`):

```js
{
  bpm: 120, key: "C major", timeSignature: "4/4",
  genre: "electronic", mood: "energetic", masterVolume: 80,
  structure: [ { type: "chorus", bars: 8, repeat: 3 }, … ],
  tracks:    [ { id, name, instrument, color, volume, muted, solo,
                 effects: { reverb, delay, distortion }, pattern, notes }, … ],
}
```

The interpreter returns `{ changes, message, tip, nextSuggestion }`; `changes`
is shallow-merged into `songState` (arrays like `tracks`/`structure` are
replaced wholesale).

## Project layout

```
src/
  App.jsx                  # orchestrator: owns songState, wires everything
  lib/
    constants.js           # song schema, palettes, music-theory helpers
    aiProducer.js          # command interpreter + surprise/melody generators
    audioEngine.js         # Tone.js graph, scheduler, analyser, playhead
  hooks/
    useSpeechRecognition.js
    useHumRecorder.js
  components/
    VoicePanel.jsx  HumRecorder.jsx  StructureEditor.jsx
    TrackMixer.jsx  AICollabPanel.jsx  Transport.jsx
    SettingsBar.jsx  SpectrumAnalyser.jsx
```

## Try this flow

1. Hit **Surprise me** for an instant 4-track song.
2. Press **Play** — watch the playhead ride the timeline and the spectrum react.
3. Type or say **"make the chorus repeat 4 times"**.
4. **Record Melody**, hum something, **Generate**, then **Add as Track**.
5. Say **"make it heavier"** and hear the distortion + tempo bump land.
