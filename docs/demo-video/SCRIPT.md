# Netforge.ai — Demo Video Script (v1)

**Runtime target:** 2:15 · **Aspect:** 16:9, 1920×1080 · **VO:** ~340 words @ ~150 wpm

> **Timecodes below are the original plan, not the shipped cut.** Once real narration
> was measured, scene durations were derived from it and the runtime became **2:31** —
> see `PRODUCTION-NOTES.md`. The spoken lines live in `build/vo.py` and the authoritative
> in/out points live in `build/timeline.json`. This file remains the source for tone,
> structure and the claims audit.
**Tonal reference:** NetBrain, *"Powerful intent-based Change Management Automation"* —
structure and pacing only. No copied lines, footage, or music.

**The curiosity arc we're borrowing:** open on a problem the viewer has personally
been burned by → make the cost concrete → pose a "what if" that reframes the
category → prove it on screen, fast → land the outcome → CTA. The reference video
earns attention by *withholding the product for the first 40 seconds*. We do the
same. Netforge doesn't appear until 0:47.

---

## ACT 1 — THE GAP (0:00–0:44)

### 0:00–0:11 · Cold open — FACE
> **VO (to camera, unhurried):**
> "Every network change starts as a drawing.
> And every outage starts with the gap between that drawing — and what's actually
> on the box."

*Beat. Hold on the face for ~1s after the line before cutting.*

### 0:11–0:28 · The gap — FACE → B-ROLL
> **VO (over b-roll):**
> "So you design it in Visio. You build it by hand, box by box, in CLI.
> And somewhere between the two, a VLAN gets transposed. A BGP neighbour never
> comes up. A trunk goes out untagged.
> You find out at two in the morning, inside a maintenance window, with a rollback
> plan and no time left to use it."

### 0:28–0:44 · The cost
> **VO:**
> "The drawing wasn't wrong. It was just never connected to anything.
> Every diagram tool on the market gives you a picture of the network.
> Then it hands you a keyboard and wishes you luck."

*Hard cut to black. 0.4s of silence. This is the pivot beat — do not score over it.*

---

## ACT 2 — THE TURN (0:44–0:56)

### 0:44–0:56 · The reframe — FACE
> **VO:**
> "So what if the drawing *was* the source of truth?
> Not a picture of the network. The network itself."

**On-screen (kinetic, over black → dissolve into product):**
`From Sketch to Spine. Instantly Connected.`

---

## ACT 3 — THE PROOF (0:56–1:58)

Three movements, matching the site's own spine: **Design → Validate → Ship.**
Each one is a *full-screen, uncropped* product moment. See SHOTLIST.md for framing law.

### 0:56–1:16 · Design
> **VO:**
> "This is Netforge.ai. Drag a device onto the canvas. Connect the ports.
> Set your VLANs, your routing, your management.
> Scale the same canvas from a branch closet to a full Arista leaf-spine VXLAN
> EVPN fabric — without leaving the designer.
> Cisco. Arista. Aruba. Palo Alto. Silver Peak. One canvas."

**On-screen chips (lower third, sequential):** `IOS-XE` `NX-OS` `EOS / AVD` `ArubaOS-CX` `PAN-OS` `EdgeConnect`

### 1:16–1:38 · Validate — *the emotional centre of the video*
> **VO:**
> "And before anything ships — it gets checked.
> IP conflicts. VLAN mismatches. BGP peer gaps. Spanning-tree errors.
> Caught here, on the canvas, not out there in the maintenance window.
> Then the AI Network Architect reviews the whole design — single points of
> failure, CVD and AVD alignment — and tells you what to fix."

**On-screen (must land on the real validation result, held ≥1.5s):**
`✓ 0 conflicts · 42 checks passed`

### 1:38–1:58 · Ship
> **VO:**
> "Then the design ships itself.
> Production-ready CLI. AVD Ansible YAML. PDF design packages, Visio diagrams,
> Excel BOM, cable schedules — generated from the same canvas, so the documentation
> can't drift from the design.
> Reverse-engineer a live Azure subscription onto that canvas, and push it back as
> Terraform."

**On-screen export rail:** `PDF` `VSDX` `XLSX` `CSV` `CLI` `YAML` `TF`

---

## ACT 4 — LAND IT (1:58–2:15)

### 1:58–2:07 · Outcome — FACE
> **VO:**
> "Design, configure, validate, deploy. One tool. One source of truth.
> The drawing and the network — finally the same thing."

### 2:07–2:15 · CTA
> **VO:**
> "Netforge.ai. Open the designer, drag your first device.
> Free to start — no card."

**End card:** logo · `netforge.ai` · `Open Designer →`

---

## Alternate cold opens (pick one in the record session — cheap to try all three)

- **A (shipped above):** "Every network change starts as a drawing…"
- **B (sharper, more curiosity):** "There's a file on your laptop that says what your
  network is supposed to be. Nothing enforces it."
- **C (in-scene, most human):** *engineer mid-console, turns to camera* — "This diagram
  is four months old. Ask me how I know."

## Claims audit — every factual line above traces to netforge.ai's own copy

| Line | Source |
|---|---|
| Vendor list | Site FAQ: Cisco IOS-XE/NX-OS, Arista EOS + AVD, ArubaOS-CX, PAN-OS, EdgeConnect |
| "IP conflicts, VLAN mismatches, BGP peer gaps, STP errors" | Verbatim from the Validate section |
| "SPOFs, CVD/AVD alignment" | AI Network Architect feature card |
| `0 conflicts · 42 checks passed` | Site's own validation still |
| Export list | Full Export Suite card + `PDF/VSDX/XLSX/CSV/CLI/YAML` rail |
| Azure → Terraform | Cloud on Canvas card |
| "Free to start — no card" | FAQ: free tier, "without entering payment details" |

**Nothing in this script claims a metric the site doesn't already make.** If you want
a harder number in Act 4 — hours saved, change-failure rate — send me the figure and
where it came from, and I'll write it in. I won't invent one.
