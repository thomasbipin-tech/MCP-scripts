# Netforge.ai demo video — production notes

**Current deliverable:** `netforge-demo-v4.mp4` — 1920×1080, 30 fps, H.264 high profile,
**2:40**, AAC stereo 48 kHz, `+faststart`.

| | | |
|---|---|---|
| v1 | 2:15 | silent, kinetic captions |
| v2 | 2:31 | Piper VO + score; invented logo fixed |
| v3 | 2:46 | Kokoro VO; pronunciation by respelling |
| **v4** | **2:40** | **phoneme-level pronunciation, no subtitles, diff shot replaces the rift** |

## v4 — the voice

Voice is **`am_onyx`** (Kokoro-82M, ONNX) at speed 1.0 — the deepest and most measured of
the available voices, which is the closest legitimate answer to "documentary baritone".
Local, no API key.

**On matching a named narrator.** The ask was for a Peter Coyote–style voice. He is a
real, working narrator whose voice is his livelihood, and imitating or cloning a specific
identifiable performer for another company's marketing isn't something to do regardless
of the tool — same reason the NetBrain narrator is off the table. What *is* on the table
is choosing for the qualities: older, deeper, unhurried. That's what `am_onyx` was picked
for. For a real documentary read, hire a voice actor — the pipeline re-times itself
around a human take in three commands (see below).

`voice-options.m4a` has the same two sentences in six voices, each announcing itself, so
the choice can be made by ear rather than from my description: `am_michael`, `am_onyx`,
`am_eric`, `am_fenrir` (American), `bm_george`, `bm_lewis` (British). Swap with
`VO_VOICE=bm_george python3 vo.py && python3 music.py && node capture.js all`.

### Letter pacing — the real cause

The staccato acronyms were a **stress** problem, not a speed one. Spoken acronyms take
secondary stress on every letter but the last, and primary on the last: `BGP` is
`bˌiːdʒˌiːpˈiː`. v3 respelled them orthographically as `C. L. I`, which did two harmful
things — forced *primary* stress onto every letter, and put a sentence-ending period
between each one, so a prosodic break landed at every letter. That was the weird pacing.

v4 drops respellings and pins **phonemes** directly (`is_phonemes=True`), bypassing
espeak's guessing. That guessing was never dependable: `CLI` phonemises to `klˈaɪ`
("cly") in isolation but to letters mid-sentence, depending on surrounding text.

| Term | Native (bypassed) | Wrong how | Shipped phonemes |
|---|---|---|---|
| `VLAN` | `vlˈæn` | one syllable, "vlan" | `vˈiːlæn` |
| `VLANs` | `vlˈæn` | plural silently dropped | `vˈiːlænz` |
| `CLI` | `klˈaɪ` | "cly" | `sˌiːˌɛlˈaɪ` |
| `EVPN` | `ˈɛvpən` | "evpen" | `ˌiːvˌiːpˌiːˈɛn` |
| `AVD` | `ˈævd` | "avd" | `ˌeɪvˌiːdˈiː` |
| `VXLAN` | `vˌiːˈɛkslˈæn` | stress on the wrong letter | `vˌiːˌɛkslˈæn` |
| `Arista` | `ˈæɹɪstə` | "ARR-ista" | `əɹˈɪstə` |
| `Visio` | `vˈɪsɪˌoʊ` | "VIS-ee-oh" | `vˈɪzioʊ` |
| `BOM` | `bˈɑːm` | "bahm" | `bˈɪl ʌv mətˈɪɹiəlz` |

`BGP`, `CVD`, `STP`, `IP`, `PDF`, `AI` and `YAML` are correct natively, and are pinned to
their native strings anyway so a model or voice change can't silently regress them.

**A trap worth recording:** espeak puts the stress mark immediately before the *vowel*
(`ˌeɪvˌiːdˈiː`), not before the syllable as IPA convention suggests (`ˌeɪvˌiːˈdiː`).
Kokoro is trained on espeak's convention, so the textbook-correct form is wrong here — my
first pass rendered `AVD` as "Avi the" and stuttered `VXLAN` into a loop. `vo.py audit`
now flags stress marks sitting before consonants.

All of it verified by read-back rather than assumption: the synthesised lines and the
final encoded mix are transcribed with Whisper and checked for the real terms.

## v4 — picture changes

**Subtitles removed.** Every lower-third caption box is gone; the voiceover carries the
narration. What remains on screen is title cards (hook, reframe, `From Sketch to Spine`,
outcome, end card), the vendor chip rail, and the product UI's own labels — none of it
transcription. The hook card also went from two lines to one so it reads as a title
rather than a subtitle. The cue track is still generated and `caption()` is a no-op, so
captions can be switched back on for a muted-social variant without redoing the work.

**The red crack is gone.** It was decorative and said nothing. That shot is now a
concrete diff between the drawing and the running config, in the app's own row styling —
`vlan 20` vs `vlan 30`, `native vlan 1` vs `99`, `bgp as 65001` vs `65002`, `mtu 1500`
vs `9216` — footed with "4 differences · 11 months since the diagram was touched". It
makes the narration's point instead of gesturing at it. The act-1 vignette was eased
(`#000000d9` → `#000000ad`) so those rows read cleanly.

**The picture cuts to the audio.** The original 2:15 timings were written for a
face-led cut. Measured against real narration they overran by 4s and left the read
81% wall-to-wall — no breathing room. So scene durations are now *derived*:

```
scene duration = max(visual floor, intro pad + Σ(line duration + gap) + tail pad)
```

`vo.py` measures each rendered line, lays the lines out inside their scene, sizes the
scene to fit, and emits `timeline.json` (scene in/out points + caption cues) which
`scenes.html`, `music.py` and `capture.js` all consume. At v4's pace that lands at 2:40
with speech density 74%. `vo.py` prints which scenes are sized by their narration and
which by their visual floor, so a copy edit surfaces as a timing change rather than a
rushed line.

The scenes the VO lengthened got extra motion rather than a longer freeze: the
fabric shot's zoom-to-fit and summary rows build progressively, the conflict ring
breathes, the AI Architect write-out is stretched, and the export fan's stagger is wider.

**Music.** Original score, synthesised from scratch in `music.py` — **no third-party
track, so nothing to license.** A minor, 100 BPM, structured to the cut: sparse low
drone under the problem, a drop at the turn (0:45) then a rising swell, a steady pulse
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
| 0:00–0:47 | The gap — hook, stale `.vsdx` vs live CLI, the rift opens |
| 0:47–0:59 | The turn — reframe, `From Sketch to Spine. Instantly Connected.` |
| 0:59–1:25 | **Design** — drag device, link ports, scale to leaf-spine fabric |
| 1:25–1:59 | **Validate** — checks stream, IP conflict caught, AI Architect, then green |
| 1:59–2:19 | **Ship** — export package, CLI, artefact fan, Cloud on Canvas → Terraform |
| 2:19–2:40 | Outcome + end card |

## Still outstanding

- **No faces** — left aside per your call. Insert points below; they still work.
- **The UI is a faithful re-creation, not a screen recording.** The build environment
  can't reach netforge.ai (egress policy) and the designer is behind sign-in. Swapping in
  real recordings for 0:59–2:19 remains the biggest available upgrade.

### Face insert points (~26s), if you revisit them

| Slot | TC | Replaces |
|---|---|---|
| 1 | 0:00–0:10 | Hook title card |
| 2 | 0:49–0:59 | Reframe title card |
| 3 | 2:19–2:30 | Outcome title card |

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
node capture.js all    # 4816 frames -> frames/       (~11 min)

ffmpeg -i vo.wav -i music.wav -filter_complex \
 "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=0.92[v];[1:a]aresample=48000[m];\
  [v][m]amix=inputs=2:normalize=0:duration=longest[mx];[mx]loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
 -map "[a]" -ar 48000 -ac 2 -c:a pcm_s16le audio.wav

ffmpeg -framerate 30 -i frames/%05d.png -i audio.wav \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -level 4.2 \
  -c:a aac -b:a 192k -movflags +faststart -shortest netforge-demo-v4.mp4
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
