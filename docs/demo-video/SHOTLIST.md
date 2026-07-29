# Netforge.ai — Shot List (v1)

Companion to `SCRIPT.md`. 24 shots · 2:15 · 1920×1080 · 30fps.

---

## 0. FRAMING LAW — the fix for the cropping problem

The last cut kept cropping into the Netforge.ai UI. That is now a hard rule, not a
preference. For every shot tagged **UI**:

1. **Full-bleed 1920×1080. The browser viewport fills the frame edge to edge.**
   No device mockup, no rounded laptop bezel, no floating "screenshot card" with a
   drop shadow, no 16:10 screen letterboxed inside a 16:9 frame.
2. **Never crop UI chrome.** The left sidebar, the top bar, the properties panel and
   the canvas all stay in frame simultaneously. If a detail is too small to read at
   full screen, the fix is a **callout ring + magnifier inset**, not a crop.
3. **Motion is push-in, capped at 8% scale, or cursor-led pan.** A push-in that would
   push any UI edge out of frame is over budget — reduce it. No whip-crops, no
   snap-zooms to a single button.
4. **Capture at 2× (3840×2160) and downscale to 1080p.** That's what buys legible
   6px label text without ever cropping in.
5. **Real cursor, real latency.** Keep the actual mouse movement and the real
   render delay. Cutting the wait out is what makes product video look fake.

Shots tagged **FACE** and **B-ROLL** may crop freely — that's where the visual
rhythm comes from, so the UI never has to supply it.

---

## 1. Shot list

Legend — **F** = face/human · **U** = product UI (framing law applies) · **B** = b-roll · **G** = graphic/kinetic

| # | TC | Dur | Type | What's on screen | Motion | On-screen text |
|---|---|---|---|---|---|---|
| 1 | 0:00 | 4s | **F** | Presenter, mid-shot, real workspace behind. Eye-line to lens. | Static, 35mm feel, shallow DOF | — |
| 2 | 0:04 | 4s | **F** | Same, slight reframe (second angle if you can film two) | Slow 3% push | — |
| 3 | 0:08 | 3s | **B** | Rack LEDs blinking in the dark, out of focus | Slow drift L→R | — |
| 4 | 0:11 | 5s | **B** | Hands on keyboard, terminal reflected in glasses | Static, tight | — |
| 5 | 0:16 | 4s | **B** | A stale Visio/PDF diagram on a second monitor, slightly yellowed | Slow push | `rev 4 — 11 months ago` |
| 6 | 0:20 | 4s | **U** | Raw CLI in a terminal, config being typed by hand | Cursor-led | — |
| 7 | 0:24 | 4s | **B** | Wall clock / phone showing 02:14. Screen glow on a tired face | Static | — |
| 8 | 0:28 | 8s | **G** | Split screen: static diagram (left) ✕ live CLI (right), a widening gap between them | Gap animates open | `the drawing` / `the network` |
| 9 | 0:36 | 8s | **B** | Maintenance-window tension: rollback doc, a second engineer on a call | Handheld, subtle | — |
| 10 | 0:44 | 2s | — | **BLACK. Full silence. Do not score.** | — | — |
| 11 | 0:46 | 6s | **F** | Presenter, closest framing of the video — this is the turn | Static | — |
| 12 | 0:52 | 4s | **G** | Title card dissolving into the product | Type animates in | `From Sketch to Spine.` `Instantly Connected.` |
| 13 | 0:56 | 7s | **U** | **Designer, full screen.** Empty canvas → device dragged from palette → dropped → snaps to grid | Cursor-led, zero scale change | — |
| 14 | 1:03 | 7s | **U** | **Full screen.** Port-to-port link drawn between two devices; properties panel opens on the right — *both panels stay in frame* | 4% push, centred | — |
| 15 | 1:10 | 6s | **U** | **Full screen.** Canvas zooms out to a full leaf-spine fabric. This shot has to feel like scale. | App's own zoom-out, frame static | `Arista AVD · VXLAN EVPN` |
| 16 | 1:16 | 6s | **U** | **Full screen.** Validation runs. Checks stream down the panel. | Static — let the app move | chips: `IOS-XE` `NX-OS` `EOS/AVD` `ArubaOS-CX` `PAN-OS` `EdgeConnect` |
| 17 | 1:22 | 5s | **U** | **Full screen.** An error state: an IP conflict flagged red on the canvas, device highlighted | Callout ring, **no crop** | `IP conflict · VLAN mismatch · BGP peer gap · STP` |
| 18 | 1:27 | 5s | **U** | **Full screen.** AI Network Architect panel writing its review; a SPOF called out | Magnifier inset over the finding | `AI Network Architect` |
| 19 | 1:32 | 6s | **U** | **Full screen.** Validation resolves green. **Hold ≥1.5s — this is the payoff frame.** | Static, then 2% push | `✓ 0 conflicts · 42 checks passed` |
| 20 | 1:38 | 7s | **U** | **Full screen.** Export dialog → generated CLI config scrolling, real syntax colour | Scroll at readable speed | — |
| 21 | 1:45 | 6s | **G** | Export artefacts fanning out: PDF, Visio, BOM, cable schedule, AVD YAML | Cards fan, staggered | `PDF` `VSDX` `XLSX` `CSV` `CLI` `YAML` |
| 22 | 1:51 | 7s | **U** | **Full screen.** Cloud on Canvas: live Azure subscription reverse-engineered onto the canvas → Terraform out | Cursor-led | `Azure → canvas → Terraform` |
| 23 | 1:58 | 9s | **F** | Presenter, warm, resolved. Mirrors shot 1's framing to close the loop. | Slow 3% pull-out | — |
| 24 | 2:07 | 8s | **G** | End card on brand background | Logo settles, CTA pulses once | `netforge.ai` · `Open Designer →` · `Free to start` |

**Face time: 31s across 5 shots (23%).** Enough to carry the story, not so much that it
becomes a talking-head video. All face shots sit at the act boundaries — open, turn,
close — which is exactly where the reference video puts its human moments.

---

## 2. What I need from you (blocks the build)

**A · Screen recordings — the highest-value item.** Shots 13–22, at **3840×2160**, browser
in fullscreen (F11, no tabs/bookmarks bar visible), 30fps, no cursor trails. One
continuous take per flow is better than clips:
- Designer: empty canvas → drag device → link ports → open properties → zoom to fabric
- Validation: run it, land on the IP-conflict error state, then resolve to green
- AI Network Architect: a real review with a real SPOF finding
- Export: dialog → CLI output scrolling → the artefact list
- Cloud on Canvas: Azure import → Terraform export

If recording those is a hassle, say so and I'll rebuild the screens in HTML from the
public site — uncropped and pixel-controlled either way, just not your live app.

**B · Face footage.** Shots 1, 2, 11, 23 (~31s). Phone in landscape is fine; window
light to one side, mic close. Record each alternate cold open from `SCRIPT.md`.

**C · B-roll.** Shots 3–9. Your own office/racks beat stock every time.

**D · Voice.** Read `SCRIPT.md` straight through in one take, then a second pass a
little slower. I'll cut the video to your audio, not the other way around.

**E · Brand.** Logo in SVG, the exact hex values, and your licensed music track — or
tell me to pull the palette off the live site.

---

## 3. 60-second social cutdown (free, from the same assets)

Shots **1 → 8 → 11 → 13 → 17 → 19 → 21 → 24**. Burned-in captions, first frame
readable muted, CTA on screen from 0:50. Vertical 9:16 variant means shots 13–22 get
a *safe-area pillarbox*, never a centre-crop — the framing law survives the reframe.
