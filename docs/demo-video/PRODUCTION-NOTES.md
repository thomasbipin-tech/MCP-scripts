# Netforge.ai demo video — production notes

**Current deliverable:** `netforge-demo-v2.mp4` — 1920×1080, 30 fps, H.264 high profile,
**2:31**, AAC stereo 48 kHz, `+faststart`.

v2 adds narration and an original score, and fixes the logo. v1 (`netforge-demo-v1.mp4`,
2:15, silent) is kept for reference.

## Changes in v2

**1. Voiceover.** Narration is synthesised locally with [Piper](https://github.com/rhasspy/piper)
(`en_US-ryan-high`, `--length-scale 1.04`), so no API key or external service is involved.
`vo.py` holds the script, per-line acronym respellings, and the layout logic.

Acronyms are respelled for the synthesiser only — `CLI` → "C L I", `VXLAN EVPN` →
"V X LAN E V P N", `YAML` → "YAM'L" — while the printed line stays scripted English, so
audio and captions never diverge.

**This is TTS, not a human read.** It's clean and correctly paced, but a real voice
would still be better; the swap is a single command (below). Treat the VO as a solid
scratch track that happens to be good enough to ship.

**2. The picture now cuts to the audio.** The original 2:15 timings were written for a
face-led cut. Measured against real narration they overran by 4s and left the read
81% wall-to-wall — no breathing room. So scene durations are now *derived*:

```
scene duration = max(visual floor, intro pad + Σ(line duration + gap) + tail pad)
```

`vo.py` measures each rendered line, lays the lines out inside their scene, sizes the
scene to fit, and emits `timeline.json` (scene in/out points + caption cues) which
`scenes.html` and `capture.js` both consume. Runtime became 2:31 and speech density
dropped to 70%. Nine scenes are VO-driven; seven are still held open by their visual
floor. `vo.py` prints which is which.

Captions are now **one global track keyed to VO line starts**, not per-scene text, so a
caption cannot drift out of sync with what's being said.

Four scenes that the VO lengthened got extra motion rather than a longer freeze: the
fabric shot's zoom-to-fit and summary rows build progressively, the conflict ring
breathes, the AI Architect write-out is stretched, and the export fan's stagger is wider.

**3. Music.** Original score, synthesised from scratch in `music.py` — **no third-party
track, so nothing to license.** A minor, 100 BPM, structured to the cut: sparse low
drone under the problem, a drop at the turn (0:41) then a rising swell, a steady pulse
under the product act, a lift on the "0 conflicts" payoff, and a resolve under the end
card. It sidechain-ducks against the VO envelope (up to about −8 dB) so narration always
sits on top. Final mix is loudness-normalised to −16 LUFS, true peak −1.5 dBTP.

**4. Logo fixed.** v1 used an invented "N" monogram. The real mark is now pulled from the
site's own `/icon.svg` (the `NetworkLogo.tsx` badge): a gradient circle
(`#0ea5e9` → `#0369a1`) with a ringed border and a five-node network glyph. It appears in
the topbar and on the end card. Nothing else in the video was invented — the palette,
sidebar metrics and vendor colours all come from the site's stylesheet.

## Structure

| | |
|---|---|
| 0:00–0:41 | The gap — hook, stale `.vsdx` vs live CLI, the rift opens |
| 0:41–0:52 | The turn — reframe, `From Sketch to Spine. Instantly Connected.` |
| 0:52–1:17 | **Design** — drag device, link ports, scale to leaf-spine fabric |
| 1:17–1:49 | **Validate** — checks stream, IP conflict caught, AI Architect, then green |
| 1:49–2:12 | **Ship** — export package, CLI, artefact fan, Cloud on Canvas → Terraform |
| 2:12–2:31 | Outcome + end card |

## Still outstanding

- **No faces** — left aside per your call. Insert points below; they still work.
- **The UI is a faithful re-creation, not a screen recording.** The build environment
  can't reach netforge.ai (egress policy) and the designer is behind sign-in. Swapping in
  real recordings for 0:52–2:12 remains the biggest available upgrade.

### Face insert points (~26s), if you revisit them

| Slot | TC | Replaces |
|---|---|---|
| 1 | 0:00–0:10 | Hook text card |
| 2 | 0:43–0:52 | Reframe text card |
| 3 | 2:12–2:22 | Outcome text card |

Each is a self-contained kinetic-text beat, so footage drops in without re-timing
anything around it. The VO lines for these slots already exist and can be re-cut to a
human read.

## Framing law, as built

- Every UI scene renders the browser viewport **edge to edge at 1:1** — palette (272px),
  canvas and properties panel (600px) all fully in frame, every product frame.
- **Scale locked at 1.0 on UI scenes.** Even the 8% push-in the shot list allowed pushes
  UI edges out of frame, which is the exact problem being fixed. The only zoom is the
  app's own zoom-to-fit on the fabric shot.
- The IP-conflict shot uses a **callout ring plus a magnifier inset in empty canvas
  space** — never a crop, never over the validation panel.
- Vignette disabled on UI scenes; it was dimming the sidebars.
- Captured at **3840×2160 (DPR 2), downscaled to 1080p** — that's what makes 11px panel
  labels legible without cropping in.

## Rebuilding

```bash
pip install imageio-ffmpeg piper-tts scipy numpy
npm i -g playwright && playwright install chromium
export NODE_PATH=$(npm root -g)
cd build

# voice model (~116 MB, not committed)
mkdir -p voices && curl -L -o voices/en_US-ryan-high.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx
curl -L -o voices/en_US-ryan-high.onnx.json \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx.json

python3 vo.py          # narration + timeline.json  (vo.py skip = re-time without re-synth)
python3 music.py       # score, keyed to timeline.json
node capture.js all    # 4530 frames -> frames/       (~11 min)

ffmpeg -i vo.wav -i music.wav -filter_complex \
 "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=0.92[v];[1:a]aresample=48000[m];\
  [v][m]amix=inputs=2:normalize=0:duration=longest[mx];[mx]loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
 -map "[a]" -ar 48000 -ac 2 -c:a pcm_s16le audio.wav

ffmpeg -framerate 30 -i frames/%05d.png -i audio.wav \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -level 4.2 \
  -c:a aac -b:a 192k -movflags +faststart -shortest netforge-demo-v2.mp4
```

**Order matters:** `vo.py` writes `timeline.json`, which `music.py`, `scenes.html` and
`capture.js` all read. Change the script copy and everything downstream re-times itself.

`scenes.html` is a deterministic renderer — `window.seek(t)` paints the exact frame at
time `t`, with nothing driven by wall clock or CSS animation. Open it in a browser and
call `seek()` from the console to scrub.

### Swapping in a human voiceover

Record the lines in `vo.py` (`LINES`, in order), drop the wavs into `vo/` as `01.wav`…
`25.wav`, then:

```bash
python3 vo.py skip     # re-measures your takes, re-times scenes, rewrites timeline.json
python3 music.py       # re-key the score to the new timing
node capture.js all    # re-render the picture to your read
```

The retiming is automatic — that's the point of deriving the timeline from the audio.
