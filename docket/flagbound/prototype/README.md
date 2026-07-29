# Collapse Prototype

A playable demonstration of one idea from the docket: **a battlefield that
transforms mid-match.** Single self-contained HTML file, no build step, no
dependencies.

## Running it

Open `index.html` in any browser with WebGL2. That is the whole procedure — it
works straight off the filesystem (`file://`), no server required.

## What it implements

| From the docket | Here |
|---|---|
| Voxel world ([10](../10-art-direction-and-cinematics.md)) | Hand-written WebGL2 instanced-cube renderer, per-block edge outlines |
| Two teams, two flags, capture rules ([01](../01-game-overview.md)) | Azure vs Crimson, own flag must be home to score |
| **The Collapse** ([02](../02-match-flow-and-world-phases.md)) | Surface shatters into its constituent blocks at 60s; players fall into the underground kingdom |
| Carrier keeps the flag through a transition ([02](../02-match-flow-and-world-phases.md)) | Implemented — uncarried flags re-anchor to the new bases |
| Debris budget ([12](../12-open-questions.md), Q9) | Capped at 4,200 blocks, nearest-to-player prioritised |
| Debris is cosmetic, not authoritative ([11](../11-technical-architecture.md)) | Debris has no collision — it cannot be landed on |
| Objective-aware bots ([06](../06-ai-bots.md)) | 4 per side: attack, escort the carrier, chase the enemy carrier, recover a dropped flag |
| F.C.S. callouts ([05](../05-fcs-ai-assistant.md)) | Text-only, priority-free, reacting to flag events and the collapse |
| Blocks are 0.5 m ([10](../10-art-direction-and-cinematics.md)) | Player stands ~3.2 blocks tall |

## What it does not implement

Named here so the prototype is not mistaken for the game:

- Online multiplayer — bots only, all local
- The four character classes — one generic loadout
- **Act III, the sky towers** — the prototype ends after the underground
- F.C.S. voice, and player questions to F.C.S.
- Chat, moderation, progression, matchmaking
- Block breaking / placing (unresolved — [12](../12-open-questions.md), Q1)

Match length is compressed to 3 minutes with the collapse at 60s, so the
transition is reachable quickly. The docket specifies 15 minutes.

## Verification

Smoke-tested headless in Chromium via Playwright: WebGL2 context creation, no
runtime errors across the phase transition, and `surface → collapse imminent →
underground` confirmed firing.

One measurement worth recording, because it bears directly on
[12](../12-open-questions.md) Q9: under SwiftShader **software** rendering the
prototype runs at ~4 fps, and the frame-time budget is dominated by debris. On
GPU hardware it is smooth. This is exactly the min-spec sensitivity the docket
flags — the collapse's block count is the first thing to measure on the weakest
target device, not the last.
