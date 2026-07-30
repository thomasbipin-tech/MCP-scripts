# Netforge.ai — short-form set

Five shorts, all 1920×1080 / 30fps / H.264 + AAC.

**Every screen in these is new.** None of them reuse a shot from the master cut, and no
screen appears in more than one short — ten additional product surfaces were built for
this set. Verified programmatically: 10 content screens used, 10 unique, zero drawn from
the master's 14 scenes.

| # | File | Length | Angle | Screens (unique to it) |
|---|---|---|---|---|
| 1 | `netforge-s1-autopsy.mp4` | 0:26 | The 2 a.m. autopsy | **Config Compare** — intended vs running, side-by-side diff with +/− gutters → **Watchtower** — per-device drift monitoring, one device flipping to drift |
| 2 | `netforge-s2-in-2026.mp4` | 0:27 | In 2026 | **Templates gallery** — 9 reference designs with live mini-topologies → **Blueprint wizard** — multi-site scoping, counters ticking to 17 sites |
| 3 | `netforge-s3-weeks-to-hours.mp4` | 0:28 | Weeks to hours | **Multi-site WAN overview** — 6 site groups radiating from a WAN hub, one tab per site → **Addressing plan** — 14-row subnet table + CIDR aggregation panel |
| 4 | `netforge-s4-deploy-minute.mp4` | 0:25 | The deploy minute | **Publish preflight** — dry-run steps ticking green, rollback point → **Looking Glass** — 6-hop path trace lighting up with latencies |
| 5 | `netforge-s5-paperwork.mp4` | 0:26 | The paperwork | **Rack elevation + BOM** — 17U rack filling, 12-line bill of materials → **Free network tools** — the 19-tool suite by category |

**Uniformity.** Every short opens on the brand card (logo + *From Sketch to Spine.*) and
closes on the end card. Verified by pixel-sampling both: identical values across all five
files (15.9 open / 16.0 close).

**Pacing** is 1.10× against the master's 1.0×, tighter pads, same voice (`am_onyx`).

## The new screens are real features, not invented UI

Every surface maps to something netforge.ai actually ships — `/tools` and `/templates`
enumerate them, and the Blueprint wizard is described on the home page ("builds your whole
multi-site network — DCs, campuses, branches — one tab per site, wired through a WAN
overview"). The tool names in the tools grid are the site's own list: DNS Lookup, Ping,
Traceroute, Port Check, Speed Test, Config Compare, Subnet Calculator, IPv6 Tools, CIDR
Aggregator, My IP, IP Geolocation, MAC Lookup, DNS Propagation, WHOIS, RDAP, Email Auth,
SSL/TLS Check, HTTP Headers, Blacklist Check, Watchtower.

Where a screen needed data the site doesn't publish — part numbers, subnet allocations,
hop latencies — the values are plausible engineering placeholders, consistent with the
topology used everywhere else in the set. Nothing claims a metric the product doesn't.

**#5 is mine.** The four supplied angles are all about the config. Nobody budgets for the
paperwork — rack elevation, BOM, cable schedule — and it's the least glamorous, most
reliably painful part of a build, which makes it a good top-of-funnel piece with the free
tools as the CTA.

## How they're built

`shorts.py` defines each variant as a **scene order plus its own narration**;
`scenes.html` reads that order from the timeline. The ten new screens live in the same
scene library as the master's, so a sixth short — or a re-mix using different screens — is
a dozen lines.

```bash
python3 shorts.py            # VO + timeline_<slug>.json for all five
python3 shorts.py s1-autopsy # just one
python3 shorts.py --list     # show the plan without synthesising
./build_shorts.sh            # music, mix, render, encode -> netforge-<slug>.mp4
```

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
