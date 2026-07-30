# Netforge.ai — short-form set

Five shorts, all 1920×1080 / 30fps / H.264 + AAC, all built from the same scene library
as the master cut (`netforge-demo-v7.mp4`).

| # | File | Length | Angle | Best for | Scene spine |
|---|---|---|---|---|---|
| 1 | `netforge-s1-2am.mp4` | 0:37 | The 2 a.m. autopsy | video / pitch opener | brand → drawing vs config → the 4 disagreements → validation → green → end |
| 2 | `netforge-s2-in-2026.mp4` | 0:32 | In 2026 | landing page, demo intro | brand → Visio + CLI → drag a device → export fan → end |
| 3 | `netforge-s3-weeks-to-hours.mp4` | 0:33 | Weeks to hours | sales deck, webinar | brand → leaf-spine fabric → validation → export fan → end |
| 4 | `netforge-s4-deploy-minute.mp4` | 0:31 | The deploy minute | social, founder-voice | brand → IP conflict caught → AI Architect → green → end |
| 5 | `netforge-s5-already-running.mp4` | 0:29 | The network you already have | cloud / hybrid, retargeting | brand → Azure on canvas → export fan → end |

**Uniformity.** Every short opens on the standalone brand card (logo + *From Sketch to
Spine.*) and closes on the end card, so the set reads as one family regardless of which
one someone sees first. Verified by pixel-sampling the centre of the first and last shots
across all five — identical brightness in every file.

**Pacing** is 1.10× against the master's 1.0×, with tighter pads (0.35s intro, 0.35s
between lines, 0.55s tail) and lower visual floors. Same voice throughout (`am_onyx`).

**#5 is mine** rather than one of your four angles. The four supplied hooks are all about
configs you're *about to write*; nothing covered the network you already have and never
documented, which is a different buyer (cloud/platform rather than campus/DC) and the one
place `Cloud on Canvas` is the hero. The other four follow your copy closely, tightened
for the shorter form.

## How they're built

No footage is duplicated. `shorts.py` defines each variant as a **scene order plus its own
narration**; `scenes.html` reads that order from the timeline and re-sequences the
master's shots. Adding a sixth short is a dozen lines, not a new render pipeline.

```bash
python3 shorts.py            # VO + timeline_<slug>.json for all five
python3 shorts.py s1-2am     # just one
python3 shorts.py --list     # show the plan without synthesising
./build_shorts.sh            # music, mix, render, encode -> netforge-<slug>.mp4
```

`build_shorts.sh` gives each variant its own port and frames directory, and deletes the
PNG frames after encoding (~500 MB per short otherwise).

## Pronunciation at higher speed — and why the checker is only a net

Faster narration reintroduced the compression bug from the master: at 1.10×, `VLAN`
(`vˈiːlæn`) squashes until it reads as "VLN" or "villain". At 1.00× it renders correctly
as "V-LAN".

`shorts.py` handles this two ways, and the split matters:

- **By rule.** `RISKY_ABOVE_1X = {'VLAN', 'VLANs'}` — any line containing these is
  synthesised at 1.0× regardless. Deterministic.
- **By read-back, as a net.** Every other line is transcribed with Whisper and checked for
  its technical terms; a failure re-cuts that line at 1.0×.

The read-back is deliberately *not* trusted as the primary mechanism, because **the ASR
oracle is unstable**: on byte-identical audio it returns different transcripts run to run,
and has dropped whole clauses. Synthesis is deterministic (verified — identical SHA-1
across repeated runs), so the flakiness is entirely in the checker. It therefore samples
each line twice and treats a miss in either pass as a failure.

Two further traps that cost time, recorded so they aren't rediscovered:

- **"Visio" comes back spelled "Vizio."** That's the *correct* pronunciation
  (VIZ-ee-oh) transcribed as the TV brand. Treating it as a failure slowed good lines
  down for nothing. `EXPECT` now lists acceptable read-back spellings per term.
- **"Netforge" is excluded from the check entirely** (`SKIP_VERIFY`). It's a coined word;
  ASR spells the correct sound (net-FORJ) as anything from "Netforge" to "Netforj" to
  "net forged", so read-back can't judge it. Its phonemes are pinned and already verified
  in the master.

Mixed audio is also a poor input for this check — with the music bed under it, ASR
rendered a correct "transposed VLAN / missing BGP neighbor" as "V-line / V-neighbor". The
per-line check runs on clean narration before mixing for that reason.

## Aspect ratio — why these are 16:9

Short-form usually implies 9:16, and these are not. Vertical forces one of two bad
outcomes with a product this dense:

- **Crop the UI** — the exact problem this project started with, and what the framing law
  in `SHOTLIST.md` exists to prevent.
- **Scale the UI to fit 1080 wide** — that's 56% of native, which takes 11px panel labels
  to ~6px. Legible in the editor, unreadable on a phone.

16:9 also plays natively on LinkedIn, X and YouTube, which is where a networking-tools
pitch mostly lands.

**If you do want vertical**, the honest version is a different layout rather than a
reframe: a 9:16 composition with the type and brand card full-bleed, and the product shown
as a *purpose-built vertical panel* — one column of the UI at native scale (say the
validation panel alone, or the canvas alone) instead of the whole three-pane app. That's
new scene code, not a re-render, and worth doing properly if vertical matters. Say the
word and I'll build the vertical layouts.
