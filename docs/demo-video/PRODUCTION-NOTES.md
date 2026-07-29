# Netforge.ai demo video — v1 production notes

**Deliverable:** `netforge-demo-v1.mp4` — 1920×1080, 30 fps, H.264 (high profile),
2:15.00, 4.9 MB, `+faststart` (streams without a full download).

## What v1 is

A **product-led, silent cut with kinetic captions**. Every VO line from `SCRIPT.md`
appears as an on-screen caption, so the video plays correctly on muted autoplay feeds
(LinkedIn, X) as-is. The act structure is unchanged from the script: the product
doesn't appear until 0:47.

| | |
|---|---|
| 0:00–0:44 | The gap — hook, stale `.vsdx` vs live CLI, the rift opens |
| 0:44–0:56 | The turn — reframe line, `From Sketch to Spine. Instantly Connected.` |
| 0:56–1:16 | **Design** — drag device, link ports, properties, scale to leaf-spine fabric |
| 1:16–1:38 | **Validate** — 12 checks stream, IP conflict caught, AI Architect, then green |
| 1:38–1:58 | **Ship** — export package, CLI config, artefact fan, Cloud on Canvas → Terraform |
| 1:58–2:15 | Outcome + end card |

## What is *not* in v1, and why

- **No faces.** No footage was supplied, and generating a synthetic presenter for a real
  company's marketing isn't something to do silently. Insert points are below.
- **No voiceover.** No recording and no TTS key. `SCRIPT.md` is timecoded and ready to read.
- **No music.** No licensed track supplied. Nothing is scored, so a track can be laid
  under the whole cut without fighting existing audio.
- **The UI is a faithful re-creation, not a screen recording.** The browser in the build
  environment can't reach netforge.ai (egress policy), and the designer is behind sign-in.
  Palette, type and layout metrics are pulled from the live site's own stylesheet —
  `--nm-*` tokens, `--nm-sidebar-left: 272px`, `--nm-sidebar-right: 600px`,
  `--nm-topbar-height: 50px`, vendor colours (Cisco `#1ba0d7`, Arista `#ed1c24`,
  Aruba `#ff8300`, Silver Peak `#00adef`), Inter + JetBrains Mono.
  **Swapping in real screen recordings is the single biggest upgrade available.**

## Face insert points (~31s total)

Drop-in replacements — the surrounding cut needs no re-timing, since each of these
spans is a self-contained kinetic-text beat.

| Slot | TC | Dur | Replaces | Line |
|---|---|---|---|---|
| 1 | 0:00–0:11 | 11s | Hook text card | "Every network change starts as a drawing…" |
| 2 | 0:46–0:52 | 6s | Reframe text card | "So what if the drawing *was* the source of truth?" |
| 3 | 1:58–2:07 | 9s | Outcome text card | "Design, configure, validate, deploy…" |

Shoot landscape, window light to one side, mic close. Record all three cold-open
variants from `SCRIPT.md` — they're the cheapest quality win in the whole production.

## The framing law, as actually built

`SHOTLIST.md` §0 required full-bleed uncropped product shots. In the build:

- Every UI scene renders the browser viewport **edge to edge at exactly 1:1** — the
  left palette (272px), canvas, and right panel (600px) are all fully in frame in every
  product frame. No device mockup, no screenshot card, no letterbox.
- **Scale is locked at 1.0 for all UI scenes.** A push-in — even the 8% the shot list
  allowed — pushes UI edges out of frame, which is the exact complaint being fixed.
  The only zoom in the video is the *app's own* zoom-to-fit on the fabric shot (1:10),
  where canvas contents scale inside a static frame.
- The IP-conflict shot (1:22) uses a **callout ring plus a magnifier inset placed in
  empty canvas space**, never a crop, and never over the validation panel.
- The vignette is disabled on every UI scene — it was dimming the sidebars, which reads
  as the same "can't see the whole screen" problem.
- Frames are captured at **3840×2160 (DPR 2) and downscaled to 1080p**, which is what
  makes 11px panel labels legible without cropping in.

## Rebuilding

```bash
pip install imageio-ffmpeg            # full ffmpeg (H.264 + AAC)
npm i -g playwright && playwright install chromium
export NODE_PATH=$(npm root -g)

cd build
node capture.js probe 84 95 114       # single frames at given timecodes -> build/probe/
node capture.js all                   # all 4050 frames -> build/frames/  (~9 min)

ffmpeg -framerate 30 -i frames/%05d.png -c:v libx264 -preset slow -crf 17 \
  -pix_fmt yuv420p -movflags +faststart -profile:v high -level 4.2 netforge-demo-v1.mp4
```

`scenes.html` is a deterministic renderer: `window.seek(t)` paints the exact frame at
time `t`. Nothing is driven by wall clock or CSS animation, so captures are
reproducible and the timeline is scrubbable — open it in a browser and call `seek()`
from the console to preview any moment.

**Editing the cut:** each entry in the `SCENES` array is `{a, b, go(lt, d)}` — start
second, end second, and a render function receiving local time. Retiming a beat means
changing two numbers. Adding VO means cutting the picture to the audio and adjusting
those pairs.

## Adding voiceover later

```bash
ffmpeg -i netforge-demo-v1.mp4 -i vo.wav -c:v copy -c:a aac -b:a 192k \
  -shortest netforge-demo-v2.mp4
```

If the read runs long or short, adjust the scene boundaries in `scenes.html` and
re-render rather than time-stretching the audio.
