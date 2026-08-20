# v8 — re-grounded on the redesigned netforge.ai (2026-08-19)

The live site was redesigned; the whole video set re-grounds against it. Crawled the
homepage, /pricing, /trust, /tools, /templates, /docs (25 pages) and the release history
before touching anything. Facts below are the site's own.

## The redesign, as it affects the videos

- **Tagline replaced.** "From Sketch to Spine." is gone site-wide (zero hits in the HTML
  and every JS chunk). The hero H1 is **"The Drawing is the Source of Truth."** with the
  support line **"Draw the network once. Everything else is generated."** The videos open
  on the thesis line (gradient-filled, as the live hero renders it) and close on the
  support line -- it is also the headline of the site's own OG share card, and the
  catchier of the two, per client note.
- **Light theme by default.** `:root` is now the light palette; dark is opt-in. All
  product screens re-themed: bg #fff/#f5f5f7, text #1d1d1f/#6e6e73, accent **#0284c7**
  (dark-mode keeps #38bdf8 -- no longer used here), canvas #f9f9fb with #00000038 dots.
  Code surfaces stay dark by the site's own tokens (--nm-code-bg #0b1220) -- terminals,
  diff embeds and Terraform panes render as dark panels on the light page.
- **JetBrains Mono is gone.** The site self-hosts Inter only; mono is the system stack
  whose listed fallback "Liberation Mono" is installed in the render container, so
  renders stay deterministic.
- **Vendor palette:** Arista **#b4283c** (was #ed1c24), Palo Alto **#fa582d** (new),
  Azure #0078d4. Catalog groups are by vendor and now include SD-WAN, Lantronix, FRR,
  Nokia and Azure. The marketing strip is five vendors; Lantronix is framed as OOB
  console support.
- **Logo unchanged** -- live icon.svg is byte-identical to our embedded copy.
- **New icon system** (NfIcon): 24-unit grid, stroke currentColor, size-stepped weight
  (<=13px -> 2, <=16 -> 1.8, >16 -> 1.5), round caps, secondary detail strokes at 0.8x
  weight / 0.55 opacity, nodes as filled dots. The eight real glyphs (topology, config,
  validation, architect, fabric, export, cloud, blueprint) are adopted verbatim.

## Fact corrections carried into narration

- 30-office Enterprise WAN: **108 devices / 296 links** (was narrated as 70 devices).
- /tools: **21 tools in 6 groups**, incl. the new Routing & BGP group with Looking
  Glass. Only four tools are fully browser-local; Config Compare's own "nothing leaves
  your browser" claim is still true (confirmed on /trust) and stays.
- /templates: **28 reference designs / 8 categories**, incl. three new families (L2
  DCI, low-latency trading, AI/ML Clos) and nine Azure designs.
- Azure ships as **Terraform or Pulumi**, per project, choice locked after first apply.

## New feature coverage (walkthrough grew 36 -> 41 shots)

Azure Designer drawer * Terraform/Pulumi deploy with live preflight * Firewall Studio
with hit-count dead-rule detection * Firewall what-if * Looking Glass (BGP scorecard) *
Watchtower rebuilt to its real shape (HTTP/TCP/UDP/ping/DNS/keyword/change/heartbeat/
API + BGP monitors, status pages) * public blueprint pages with embeds + last-verified *
rack elevations with patch panels + fibre LIU priced in a PANELS BOM section * as-built
import got its own shot * per-collection Ansible host_vars in the deploy narration *
roadmap chapter rewritten from the August 2026 release notes * a free-vs-Enterprise beat
("everything that draws is free").

## Flag for the client

`/.well-known/security.txt` lists a second canonical domain, `rackloom.com`, referenced
nowhere else on the site. If a rebrand is in flight, say so before the next cut is
distributed; the end cards say netforge.ai.

## v8 — the three bookend bugs

Three cuts shipped or nearly shipped with the wrong first or last screen, all the same
shape: a timeline whose scene indices stopped meaning what the code assumed, after
screens were appended to the shared library.

| Where | What happened |
|---|---|
| `shorts.py` | kept its own `BRAND, ENDCARD = 32, 33`. Twelve screens were inserted ahead of the brand card, `series.py` moved to 36/37, this file did not. Every short rendered afterwards opened on Site Areas and closed on Console & OOB. |
| `vo.py` / `timeline.json` | emitted no `order` array, so the player fell back to identity mapping slot→scene. Fine while the library ended at the end card; once it grew, the master's last slot landed on the Blueprint wizard and the sign-off played over "Never face a blank canvas". |
| `watch_build.sh` | restarted stalls with a blanket `pkill -9 -x node`, which kills unrelated renders — the same class of bug as the old `pkill -f capture.js` matching the script's own command line. |

Fixes are structural, not careful-next-time: scene indices now have **one owner**
(`series.py`; `shorts.py` and `vo.py` read from it), timelines always carry an explicit
`order`, and the watchdog kills only the PID it launched.

**`verify_cuts.py` is the gate.** It runs against the *encoded* files, not the source,
because that is what reaches the client. Per cut it asserts: an explicit `order` exists,
the first shot is the brand card and the last is the end card, the runtime matches the
timeline, and no content screen repeats. Run it before any delivery:

```
python3 verify_cuts.py              # every cut with an encoded file
python3 verify_cuts.py walkthrough  # one
```

All three bugs would have been caught by it in under a minute. They were caught by eye
instead, after delivery.

## v8 — the shipped set

| Cut | Runtime |
|---|---|
| master demo | 2:32 |
| full walkthrough | 17:49 (44 shots) |
| episodes 1–10 | 2:03 – 3:32, 26.5 min total |
| shorts 1–5 | ~27s each |

58 distinct content screens across the ten episodes, none shared between any two.
Upload metadata for all 17 cuts is in `YOUTUBE.md`, generated from the timelines.

# Netforge.ai demo video — production notes

**Current deliverable:** `netforge-demo-v7.mp4` — 1920×1080, 30 fps, H.264 high profile,
**2:31**, AAC stereo 48 kHz, `+faststart`.

| | | |
|---|---|---|
| v1 | 2:15 | silent, kinetic captions |
| v2 | 2:31 | Piper VO + score; invented logo fixed |
| v3 | 2:46 | Kokoro VO; pronunciation by respelling |
| v4 | 2:40 | phoneme-level pronunciation; subtitles removed |
| v5 | 2:20 | act 1 recut; gap shown as a bridge; major-key reveal |
| v6 | 2:29 | client hook at 1.2x; screen-only validation result; Azure lead-in; end-card tagline |
| **v7** | **2:31** | **opens on the brand card; heading moved to slide 2** |

## v7 — opening brand card

The video now opens on the same card it ends on: logo, wordmark, and
**From Sketch to Spine.** — no URL, so the open reads as a title and the close as a CTA.
It holds silent for 2.7s, then cross-dissolves into the demo **on the hook's first word**.

That transition is pinned to the narration, not to a hardcoded time: scene 1 reads
`voSpan('01').s` from `timeline.json`, so re-recording or re-pacing the hook keeps the
dissolve on the word. A soft two-note chime sits under the logo, bookending the end-card
chime; the score then drops into act 1's A-minor drone.

**Heading placement.** "Designed once. Configured by hand." is invented copy — written
when the client hook replaced the old opening line, so the screen wouldn't just echo the
narration. It sat on slide 1, which read as unexplained; it now appears on **slide 2**,
where it frames the four disagreements rather than an empty pair of panes. Verified by
sampling the top band of the frame: brightness 0.16 on the brand card, 0.05 mid-dissolve,
0.41 on slide 1, 4.11 on slide 2.

**One collision fixed:** the config pane's text was lengthened in v6 to fill the longer
opening shot, which put it underneath the value chips in the comparison. The terminal now
recedes to 11% opacity in that scene — the chips carry the meaning there, the panes are
context.

## The voice

**`am_onyx`** (Kokoro-82M, ONNX) at speed 1.0 — the deepest and most measured of the
available voices, which is the closest legitimate answer to "documentary baritone".
Local, no API key.

**On matching a named narrator.** A Peter Coyote–style voice was requested. He is a real,
working narrator whose voice is his livelihood, and imitating or cloning a specific
identifiable performer for another company's marketing isn't something to do regardless of
the tool — same reason the NetBrain narrator is off the table. What *is* on the table is
choosing for the qualities: older, deeper, unhurried. That's what `am_onyx` was picked for.
For a real documentary read, hire a voice actor — the pipeline re-times itself around a
human take in three commands (see below).

`voice-options.m4a` has the same two sentences in six voices, each announcing itself, so
the choice can be made by ear rather than from my description: `am_michael`, `am_onyx`,
`am_eric`, `am_fenrir` (American), `bm_george`, `bm_lewis` (British). Swap with
`VO_VOICE=bm_george python3 vo.py && python3 music.py && node capture.js all`.

### Letter pacing — the real cause

The staccato acronyms were a **stress** problem, not a speed one. Spoken acronyms take
secondary stress on every letter but the last, and primary on the last: `BGP` is
`bˌiːdʒˌiːpˈiː`. v3 respelled them as `C. L. I`, which did two harmful things at once —
forced *primary* stress onto every letter, and put a sentence-ending period between each
one, so a prosodic break landed at every letter. That was the weird pacing.

v4 dropped respellings and pins **phonemes** directly (`is_phonemes=True`), bypassing
espeak's guessing. That guessing was never dependable: `CLI` phonemises to `klˈaɪ` ("cly")
in isolation but to letters mid-sentence, depending on surrounding text.

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

**The table was too short.** It covered the terms in the 2:31 master and nothing else, so
the longer cuts shipped with `WAN` read as the English word "wan" (pale), `SD-WAN` as a
mangled "sd-wan", `OSPF` as `ˈɑːspf`, `IPAM` as "ipp-am", `CIDR` as "sidder", `ACL` as
"ackle", `EOS` as "ee-ohz" and `AS` as the word "as". The table now carries every acronym
the narration actually uses (60+ entries — see `CLAUDE.md`), and `python3 vo.py coverage`
fails the build if a narration line introduces one that isn't pinned. Plurals need their
own entry (`VRF`/`VRFs`): without one the `s` is silently dropped.

Two matching bugs came out with it:

- **Matching was unbounded**, so a short term could fire inside a longer word — `IP`
  plucked out of `IPAM`. Terms are now matched on word boundaries.
- **Fragments were phonemised in isolation.** Splitting the line at each term and
  phonemising the pieces separately loses sentence context, and espeak then gives function
  words their citation form: *"a WAN overview"* came out as stressed "AY wan". `vo.py` now
  masks each term with an ordinary word, phonemises the whole line in one pass so the
  article correctly reduces to `ɐ`, and swaps the mask for the pinned phonemes.

**A trap worth recording:** espeak puts the stress mark immediately before the *vowel*
(`ˌeɪvˌiːdˈiː`), not before the syllable as IPA convention suggests (`ˌeɪvˌiːˈdiː`).
Kokoro is trained on espeak's convention, so the textbook-correct form is wrong here — the
first pass rendered `AVD` as "Avi the" and stuttered `VXLAN` into a loop. `vo.py audit`
now flags stress marks sitting before consonants.

All verified by read-back rather than assumption: synthesised lines and the final encoded
mix are transcribed with Whisper and checked for the real terms.

## v5 — act 1 recut

**The product now arrives at 0:36 instead of 0:59**, and runtime dropped 2:40 → 2:20. None
of that came from speeding up the read — the voice is unchanged. It came from cutting:

- **The standalone hook card is gone.** "Every network change starts as a drawing" is now
  the *title of the panes shot* rather than its own slide, removing ~10s that was showing
  one sentence on black.
- **Two narration lines cut as redundant.** "So you design it in Visio. You build it by
  hand, box by box, in CLI" — the two panes on screen already *are* that sentence, so the
  voice was narrating the picture. And "Every diagram tool on the market gives you a
  picture of the network, then hands you a keyboard and wishes you luck" — a good line, but
  the pivot ("it was just never connected to anything") makes the same point in half the
  time.
- **The `From Sketch to Spine. Instantly Connected.` card is gone**, as requested; the
  reframe hands straight off to the product, removing another ~3s of hold.

Act 1 went from four scenes to three (16 → 15 total). The beats — artefacts, disagreement,
pivot, reframe — are all still there.

## v5 — the gap, shown rather than drawn

The red crack was replaced in v4 by a standalone diff panel, but that lost what the crack
was at least gesturing at: *two artefacts with a space between them*. v5 keeps both halves.

Scenes 1 and 2 are now the **same two panes** — stale `.vsdx` left, live `running-config`
right. Scene 1 introduces them; scene 2 holds them in place, recedes their contents to 30%,
and brings forward four value pairs facing each other across the gap:

| Drawing (struck through) | Running config |
|---|---|
| `vlan 20 · VOICE` | `vlan 30 · VOICE` |
| `native vlan 1` | `native vlan 99` |
| `bgp as 65001` | `bgp as 65002` |
| `mtu 1500` | `mtu 9216` |

Each pair is joined by a dashed red link that **breaks in the middle**, with a ✕ at the
break — so the gap is literally the space between the two artefacts, and every break names
a specific disagreement. Footed with "4 differences · 11 months since the diagram was
touched". These are the values the narration is discussing, so picture and voice make the
same argument.

**Reveal order is pinned to the narration.** The running-config pane was appearing at 3.4s
while the opening line ran to 3.71s — before the sentence finished. Scene 1 now reads that
line's end from `timeline.json` (`voSpan('01')`) and brings the config pane in 0.35s after
it, so a re-recorded or re-paced line keeps the beat instead of needing a new hardcoded
number. Verified by sampling the pane region: mean brightness 0.00 at 3.5s, 2.84 at 4.3s,
7.11 at 5.5s.

## Config Compare — the colours are structural, not a git diff

The Config Compare screen was drawn as a source-control diff: red for the left pane, green
for the right, one colour per *side*. That is not what the product does, and the narration
already described the real thing. The screen now matches it:

| Colour | Means | Drawn as |
|---|---|---|
| green | identical once the ignore rules have been applied | `=` gutter, faint green row |
| yellow | the same line, edited | `~` gutter, changed words boxed **inside** the row |
| red | opening words have no counterpart on the other side | `×` gutter; the other pane shows a hatched stub |

Severity is a **separate axis** from colour: each differing line also carries a
major/minor badge, classified fail-closed, on whichever pane actually holds the line so it
is never printed twice. The footer carries the counts, the `block-aware sort` state, and
the two facts that matter commercially — it exports as a unified `.diff` or a standalone
HTML report, and nothing leaves the browser.

The classification lands ~0.35s after the text staggers in (rows hold at `saturate(.12)`
until then), so the colour reads as a verdict on lines you have already seen rather than
as decoration.

## v5 — the score lifts at the reveal

The line is now **"Introducing Netforge.ai"** (was "This is Netforge.ai"), and the music
lifts with it. Act 1 stays in A minor; at the reveal the score **modulates to the relative
major** and runs `C – G – Am – F`, with an ascending bell flourish on the entrance, a
brighter filter (pad 1500 → 2100 Hz, arp 3200 → 4200 Hz), act 1 pushed darker still (tilt
0.72 → 0.62) so the lift is felt, and the outro resolving in C major with an end-card chime
rather than trailing off in A minor.

Verified rather than assumed: an FFT of the product act shows the C root and E4 — the major
third — dominating the chord register, where act 1 has neither.

## Picture

**Subtitles removed** (v4). Every lower-third caption box is gone; the voiceover carries
the narration. What remains on screen is the panes-shot title, the reframe card, the
outcome card, the end card, the vendor chip rail, and the product UI's own labels — none of
it transcription. The cue track is still generated and `caption()` is a no-op, so captions
can be switched back on for a muted-social variant without redoing the work.

**The picture cuts to the audio.** The original 2:15 timings were written for a
face-led cut. Measured against real narration they overran by 4s and left the read
81% wall-to-wall — no breathing room. So scene durations are now *derived*:

```
scene duration = max(visual floor, intro pad + Σ(line duration + gap) + tail pad)
```

`vo.py` measures each rendered line, lays the lines out inside their scene, sizes the
scene to fit, and emits `timeline.json` (scene in/out points + caption cues) which
`scenes.html`, `music.py` and `capture.js` all consume. At v5's cut that lands at 2:20
with speech density 75%. `vo.py` prints which of the 15 scenes are sized by their narration
and which by their visual floor, so a copy edit surfaces as a timing change rather than a
rushed line — which is how the act-1 recut above was costed.

The scenes the VO lengthened got extra motion rather than a longer freeze: the
fabric shot's zoom-to-fit and summary rows build progressively, the conflict ring
breathes, the AI Architect write-out is stretched, and the export fan's stagger is wider.

**Music.** Original score, synthesised from scratch in `music.py` — **no third-party
track, so nothing to license.** A minor, 100 BPM, structured to the cut: sparse low
drone under the problem, a drop at the turn (0:27) then a rising swell, a steady pulse
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
| 0:00–0:03 | Brand card — logo + tagline |
| 0:03–0:29 | The gap — hook, stale `.vsdx` vs live CLI, the rift opens |
| 0:29–0:38 | The turn — reframe, `From Sketch to Spine. Instantly Connected.` |
| 0:38–1:07 | **Design** — drag device, link ports, scale to leaf-spine fabric |
| 1:07–1:42 | **Validate** — checks stream, IP conflict caught, AI Architect, then green |
| 1:42–1:59 | **Ship** — export package, CLI, artefact fan, Cloud on Canvas → Terraform |
| 1:59–2:20 | Outcome + end card |

## Still outstanding

- **No faces** — left aside per your call. Insert points below; they still work.
- **The UI is a faithful re-creation, not a screen recording.** The build environment
  can't reach netforge.ai (egress policy) and the designer is behind sign-in. Swapping in
  real recordings for 0:36–1:59 remains the biggest available upgrade.

### Face insert points (~26s), if you revisit them

| Slot | TC | Replaces |
|---|---|---|
| 1 | 0:00–0:15 | Panes shot (title + artefacts) |
| 2 | 0:27–0:36 | Reframe card |
| 3 | 1:59–2:10 | Outcome card |

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
node capture.js all    # 4539 frames -> frames/       (~11 min)

ffmpeg -i vo.wav -i music.wav -filter_complex \
 "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=0.92[v];[1:a]aresample=48000[m];\
  [v][m]amix=inputs=2:normalize=0:duration=longest[mx];[mx]loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
 -map "[a]" -ar 48000 -ac 2 -c:a pcm_s16le audio.wav

ffmpeg -framerate 30 -i frames/%05d.png -i audio.wav \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -level 4.2 \
  -c:a aac -b:a 192k -movflags +faststart -shortest netforge-demo-v5.mp4
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
