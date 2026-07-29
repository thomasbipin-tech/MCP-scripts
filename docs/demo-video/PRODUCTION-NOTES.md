# Netforge.ai demo video — production notes

**Current deliverable:** `netforge-demo-v3.mp4` — 1920×1080, 30 fps, H.264 high profile,
**2:46**, AAC stereo 48 kHz, `+faststart`.

| | | |
|---|---|---|
| v1 | 2:15 | silent, kinetic captions |
| v2 | 2:31 | Piper VO + score; invented logo fixed |
| **v3** | **2:46** | **Kokoro VO (warmer), verified pronunciation** |

## v3 — the voice

**Engine changed from Piper to [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)
(ONNX), voice `am_michael` at speed 1.06.** Piper's `en_US-ryan-high` read as obviously
synthetic. Kokoro is a materially better model — warmer tone, more natural prosody.
Still local, still no API key.

Kokoro reads more deliberately, which is why runtime went 2:31 → 2:46. That was a
deliberate trade: rushing the read to hit the old length is what makes TTS sound like
TTS. `VO_SPEED=1.12 python3 vo.py` tightens it to about 2:37 if you want the time back.

**Pick a different voice by ear:** `voice-options.m4a` (committed here) is the same two
sentences in six candidate voices, each announced by name — `am_michael`, `am_onyx`,
`am_eric`, `am_fenrir`, `bm_george`, `bm_lewis` (`am_*` American, `bm_*` British). To
switch: `VO_VOICE=am_onyx python3 vo.py && python3 music.py && node capture.js all`.

**What this still is not.** It is not the narrator from the NetBrain reference video —
that is a specific real person, and cloning an identifiable voice for another company's
marketing isn't something to do. If you want that register properly, a human read is
the answer, and the pipeline is built to take one (below).

### Pronunciation — one table, verified not guessed

v2 respelled acronyms by hand in a second copy of each line, and got some wrong. v3 has
a single `PRONOUNCE` table applied automatically to the scripted text, so there is no
duplicate string to drift. `python3 vo.py audit` prints each term's phonemes next to
what the synthesiser would do untreated:

| On screen | Untreated | Wrong how | Spoken as |
|---|---|---|---|
| `VLAN` | `vlˈæn` | one syllable, "vlan" | `vee-lan` → `vˈiːlˈæn` |
| `VLANs` | `vlˈæn` | plural silently dropped | `vee-lans` → `vˈiːlˈænz` |
| `CLI` | `klˈaɪ` | reads as "cly" | `C. L. I` → `sˈiːˈɛlˈaɪ` |
| `EVPN` | `ˈɛvpən` | reads as "evpen" | `E. V. P. N` → `ˈiːvˈiːpˈiːˈɛn` |
| `AVD` | `ˈævd` | reads as "avd" | `A. V. D` → `ˈeɪvˈiːdˈiː` |
| `Arista` | `ˈæɹɪstə` | "ARR-ista" | `uh-rista` → `ʌɹˈɪstə` |
| `Visio` | `vˈɪsɪˌoʊ` | "VIS-ee-oh" | `vizzy-oh` → `vˈɪziˈoʊ` |
| `BOM` | `bˈɑːm` | reads as "bahm" | `bill of materials` |

`BGP`, `IP`, `CVD`, `STP`, `PDF`, `VXLAN`, `AI` and `YAML` phonemise correctly untreated
and are pinned in the table anyway so a model change can't silently regress them.

Two bugs this caught, both now fixed:
- Respellings ending in `.` collided with the sentence's own period, merging
  "Production-ready CLI. AVD Ansible YAML" into one run-on. Trailing periods dropped —
  phonemes are identical without them.
- `A. V. D` style spellings must not use `ay`: `ay` phonemises to `ˈaɪ` ("eye"), so
  "ay vee dee" said *eye*-vee-dee. Period-separated letters give the correct `ˈeɪ`.

**Verified by read-back, not by assumption.** The synthesised audio is transcribed with
Whisper (`faster-whisper`, `small.en`) and checked for the real terms — the ASR hears
"VLAN", "VLANs", "BGP", "IP", "CLI", "AVD", "CVD", "YAML", "PDF", "Arista", "Azure",
"Terraform". ("Visio" comes back spelled "Vizio", which is the ASR spelling the correct
sound.) Re-run that check any time you change a voice or a line.

**The picture cuts to the audio.** The original 2:15 timings were written for a
face-led cut. Measured against real narration they overran by 4s and left the read
81% wall-to-wall — no breathing room. So scene durations are now *derived*:

```
scene duration = max(visual floor, intro pad + Σ(line duration + gap) + tail pad)
```

`vo.py` measures each rendered line, lays the lines out inside their scene, sizes the
scene to fit, and emits `timeline.json` (scene in/out points + caption cues) which
`scenes.html`, `music.py` and `capture.js` all consume. At v3's pace that lands at 2:46
with speech density 74% — 13 of 16 scenes are sized by their narration, 3 are still held
open by their visual floor. `vo.py` prints which is which, so a copy edit shows up as a
timing change rather than a rushed line.

Captions are now **one global track keyed to VO line starts**, not per-scene text, so a
caption cannot drift out of sync with what's being said.

The scenes the VO lengthened got extra motion rather than a longer freeze: the
fabric shot's zoom-to-fit and summary rows build progressively, the conflict ring
breathes, the AI Architect write-out is stretched, and the export fan's stagger is wider.

**Music.** Original score, synthesised from scratch in `music.py` — **no third-party
track, so nothing to license.** A minor, 100 BPM, structured to the cut: sparse low
drone under the problem, a drop at the turn (0:49) then a rising swell, a steady pulse
under the product act, a lift on the "0 conflicts" payoff, and a resolve under the end
card. It sidechain-ducks against the VO envelope (up to about −8 dB) so narration always
sits on top. Final mix is loudness-normalised to −16 LUFS, true peak −1.5 dBTP.

**Logo.** v1 used an invented "N" monogram. The real mark is now pulled from the
site's own `/icon.svg` (the `NetworkLogo.tsx` badge): a gradient circle
(`#0ea5e9` → `#0369a1`) with a ringed border and a five-node network glyph. It appears in
the topbar and on the end card. Nothing else in the video was invented — the palette,
sidebar metrics and vendor colours all come from the site's stylesheet.

## Structure

| | |
|---|---|
| 0:00–0:49 | The gap — hook, stale `.vsdx` vs live CLI, the rift opens |
| 0:49–1:02 | The turn — reframe, `From Sketch to Spine. Instantly Connected.` |
| 1:02–1:29 | **Design** — drag device, link ports, scale to leaf-spine fabric |
| 1:29–2:06 | **Validate** — checks stream, IP conflict caught, AI Architect, then green |
| 2:06–2:26 | **Ship** — export package, CLI, artefact fan, Cloud on Canvas → Terraform |
| 2:26–2:46 | Outcome + end card |

## Still outstanding

- **No faces** — left aside per your call. Insert points below; they still work.
- **The UI is a faithful re-creation, not a screen recording.** The build environment
  can't reach netforge.ai (egress policy) and the designer is behind sign-in. Swapping in
  real recordings for 1:02–2:26 remains the biggest available upgrade.

### Face insert points (~26s), if you revisit them

| Slot | TC | Replaces |
|---|---|---|
| 1 | 0:00–0:11 | Hook text card |
| 2 | 0:51–1:02 | Reframe text card |
| 3 | 2:26–2:36 | Outcome text card |

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
pip install imageio-ffmpeg kokoro-onnx scipy numpy faster-whisper
apt-get install -y espeak-ng     # phonemiser, also used by vo.py audit
npm i -g playwright && playwright install chromium
export NODE_PATH=$(npm root -g)
cd build

# model files (~338 MB, not committed)
mkdir -p kokoro && cd kokoro
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ..

python3 vo.py          # narration + timeline.json
python3 vo.py audit     # pronunciation table -> phonemes
python3 vo.py voices    # voice-options.wav for picking by ear
python3 music.py       # score, keyed to timeline.json
node capture.js all    # 4982 frames -> frames/       (~12 min)

ffmpeg -i vo.wav -i music.wav -filter_complex \
 "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=0.92[v];[1:a]aresample=48000[m];\
  [v][m]amix=inputs=2:normalize=0:duration=longest[mx];[mx]loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
 -map "[a]" -ar 48000 -ac 2 -c:a pcm_s16le audio.wav

ffmpeg -framerate 30 -i frames/%05d.png -i audio.wav \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -level 4.2 \
  -c:a aac -b:a 192k -movflags +faststart -shortest netforge-demo-v3.mp4
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
