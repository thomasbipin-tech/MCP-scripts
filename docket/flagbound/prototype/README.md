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
| Rounded block world ([10](../10-art-direction-and-cinematics.md)) | Hand-written WebGL2 instanced renderer, two generated meshes: a spherified cube for the world and figures, and a smooth sphere for effects. Rolling green ground, a stone wall with two gaps, two towers, trees with rounded canopies, CSS-gradient sky per phase |
| Restraint in density ([10](../10-art-direction-and-cinematics.md#restraint-is-part-of-the-style)) | One wall, two towers, eighteen trees. An earlier pass added floating islands, drifting motes and dozens of spires and was judged too crowded — objectives disappeared into the noise |
| **Anime characters as drawn art** ([10](../10-art-direction-and-cinematics.md#two-ways-to-ship-anime-characters)) | Each figure is an SVG illustration — layered hair, big eyes with iris gradient and highlights, coat, belt, scarf — rasterised to a texture and billboarded into the 3D world. Ten characters, two views each (front / back), mirrored for left / right. Alpha-tested, so depth alone resolves them with no sorting |
| Cel shading ([10](../10-art-direction-and-cinematics.md#the-rendering-signature)) | Three hard-stepped light bands, fresnel ink silhouette, hot rim, specular pops — applied to the 3D world. The characters need none of it: they are already drawn |
| Soft lighting ([10](../10-art-direction-and-cinematics.md#the-rendering-signature)) | Warm key, cool sky-coloured fill, and a restrained rim term that separates silhouettes without turning dreamlike |
| Warm-vs-cool team palettes ([03](../03-combat-and-classes.md)) | Every character has its own hue; Azure hues all cool, Crimson all warm |
| Two teams, two flags, capture rules ([01](../01-game-overview.md)) | Azure vs Crimson, own flag must be home to score |
| **The Collapse** ([02](../02-match-flow-and-world-phases.md)) | Surface comes apart into its constituent cells at 60s; players fall into the caverns below |
| Carrier keeps the flag through a transition ([02](../02-match-flow-and-world-phases.md)) | Implemented — uncarried flags re-anchor to the new bases |
| Debris budget ([12](../12-open-questions.md), Q9) | Capped at 4,200 blocks, nearest-to-player prioritised |
| Debris is cosmetic, not authoritative ([11](../11-technical-architecture.md)) | Debris has no collision — it cannot be landed on |
| Third-person camera | Tries raising itself over an obstruction before pulling in, since a lifted view keeps the figure on screen where pulling in buries the camera in it. Falls back to pull-in, then to converging on the player. Your own figure is hidden when the camera ends up point-blank |
| Objective-aware bots ([06](../06-ai-bots.md)) | 4 per side: attack, escort the carrier, chase the enemy carrier, recover a dropped flag |
| F.C.S. callouts ([05](../05-fcs-ai-assistant.md)) | Text-only, priority-free, reacting to flag events and the collapse |
| Cells are 0.5 m ([10](../10-art-direction-and-cinematics.md)) | Characters stand 3.7 cells tall (~1.85 m) |

## What it does not implement

Named here so the prototype is not mistaken for the game:

- Online multiplayer — bots only, all local
- The four character classes — one generic loadout
- **Act III, the sky towers** — the prototype ends after the underground
- **Skeletal character animation.** The figures are static illustrations that bob
  and leave dash afterimages; they do not walk. Layered puppet animation or frame
  sets would fix this within the 2D route
- **Facing readability.** A billboard always faces you, so an opponent's facing is
  not readable from the sprite alone — a real gameplay problem with this route, and
  the reason [12](../12-open-questions.md) (Q4) recommends 3D models for shipping
- Hit-stop and impact frames, which is where most of the perceived punch would come from
- F.C.S. voice, and player questions to F.C.S.
- Chat, moderation, progression, matchmaking
- Cell breaking / placing (unresolved — [12](../12-open-questions.md), Q1)

Match length is compressed to 3 minutes with the collapse at 60s, so the
transition is reachable quickly. The docket specifies 15 minutes.

## Skills

Four are playable, bound to keys. The full roster — class signatures, ultimates,
and the ideas that were rejected — is in [13](../13-abilities-and-skills.md).

| Key | Skill | Behaviour | Cooldown |
|---|---|---|---|
| **Q** | Dash | Burst along your facing direction with brief invulnerability | 4s |
| **E** | Grapple | Raycasts along the view direction and reels you to whatever it strikes | 6.5s |
| **R** | Ground Slam | Comes down hard; shockwave knocks back and eliminates nearby enemies. Pressing it while standing leaps first, so the button never silently fails | 9s |
| **Space** (held, falling) | Glide | Clamps descent to a drift | — |

In the prototype all four are available to everyone. In the docket, dash and
glide are universal while grapple and slam are class signatures — the prototype
has no classes, so it hands out the whole kit.

Bots do not use skills. They fight and pursue objectives only, which is worth
knowing when judging how the abilities feel.

## Finding things

Two aids exist because the flag was genuinely hard to locate in testing:

- **Beacon** — a slim emissive column rises from each flag, visible over the wall
  from anywhere on the map. A carried flag keeps its beacon, so the carrier is
  always findable.
- **Objective tracker** — an on-screen tag naming the current objective and its
  distance in metres. It follows the flag while visible and pins to the screen
  edge with an arrow when it is not.

The player's own character floats a spinning gold diamond, so you can tell which
one is you.

## Verification

Smoke-tested headless in Chromium via Playwright: WebGL2 context creation, no
runtime errors across the phase transition, and `surface → collapse imminent →
underground` confirmed firing.

Camera shake is decayed unconditionally every frame, and anything that wants
shake raises a floor rather than owning the value. An earlier build decayed it
only after the collapse, so a ground slam on the surface left the screen shaking
until the world broke apart. Shake also respects `prefers-reduced-motion`, and
uses its own random source so visual jitter cannot perturb gameplay randomness.

One measurement worth recording, because it bears directly on
[12](../12-open-questions.md) Q9: under SwiftShader **software** rendering the
prototype runs at ~4 fps, and the frame-time budget is dominated by debris. On
GPU hardware it is smooth. This is exactly the min-spec sensitivity the docket
flags — the collapse's block count is the first thing to measure on the weakest
target device, not the last.
