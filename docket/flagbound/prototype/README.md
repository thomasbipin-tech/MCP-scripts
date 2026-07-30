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
| Rounded block world ([10](../10-art-direction-and-cinematics.md)) | Hand-written WebGL2 instanced renderer, two generated meshes: a flat-faced cube for the world and a sphere for atmosphere and effects. Rolling green ground, a stone wall with two gaps, two towers, trees with rounded canopies, CSS-gradient sky per phase |
| **Disintegration on defeat** ([10](../10-art-direction-and-cinematics.md#defeat-disintegration)) | 72 team-coloured motes sweeping upward from the feet on a staggered delay, plus one expanding white flash. No body left behind |
| **Reboot pads** ([03](../03-combat-and-classes.md#health-defeat-and-respawn)) | Two raised platforms in diagonally opposite corners, one per team, with a glowing core and a locator beam. You spawn at your base at match start but re-form here after every elimination |
| **Battlefield points of interest** ([10](../10-art-direction-and-cinematics.md#act-i--citadel)) | Three buildings with window gaps and pitched tile roofs, a pond with a sandy shore and plank bridge, four rock formations, a ruined midfield wall with two gaps, two towers, trees with bushes, clouds overhead, and fogged distant hills for a horizon |
| Restraint in density ([10](../10-art-direction-and-cinematics.md#restraint-is-part-of-the-style)) | One wall, two towers, eighteen trees. An earlier pass added floating islands, drifting motes and dozens of spires and was judged too crowded — objectives disappeared into the noise |
| **Square figures** ([10](../10-art-direction-and-cinematics.md#characters)) | Hard-edged cubes — head, torso, two arms, two legs, belt, square eyes — deliberately sharp against the soft rounded world so players separate from terrain at any distance |
| **Three-way colour split** | Skin-toned head, team-coloured outfit, dark trousers, plus a team band on the head. One saturated hue over a whole figure read as plastic |
| **Speed-driven gait** | ~1.3 stride cycles/sec at run speed (2.7 steps/sec), amplitude scaling with measured speed, body rising twice per cycle, a lean into the run, and legs shortening at the stride extremes so feet do not scrape. Measured, not eyeballed — an earlier build ran at 9.2 steps/sec |
| Cel shading ([10](../10-art-direction-and-cinematics.md#the-rendering-signature)) | Three hard-stepped light bands, fresnel ink silhouette, rim, specular pops — full strength on figures, a third on terrain so cells are not each outlined |
| Soft lighting ([10](../10-art-direction-and-cinematics.md#the-rendering-signature)) | Warm key, cool sky-coloured fill, and a restrained rim term that separates silhouettes without turning dreamlike |
| Warm-vs-cool team palettes ([03](../03-combat-and-classes.md)) | Every character has its own hue; Azure hues all cool, Crimson all warm |
| Two teams, two flags, capture rules ([01](../01-game-overview.md)) | Azure vs Crimson, own flag must be home to score |
| **The Collapse** ([02](../02-match-flow-and-world-phases.md)) | Surface comes apart into its constituent cells at 60s; players fall into the caverns below |
| Carrier keeps the flag through a transition ([02](../02-match-flow-and-world-phases.md)) | Implemented — uncarried flags re-anchor to the new bases |
| Debris budget ([12](../12-open-questions.md), Q9) | Capped at 4,200 blocks, nearest-to-player prioritised |
| Debris is cosmetic, not authoritative ([11](../11-technical-architecture.md)) | Debris has no collision — it cannot be landed on |
| Third-person camera | Tries raising itself over an obstruction before pulling in, since a lifted view keeps the figure on screen where pulling in buries the camera in it. Falls back to pull-in, then to converging on the player. Your own figure is hidden when the camera ends up point-blank |
| Two meshes | A spherified cube for the world and a plain cube for figures — the same instanced renderer, two geometries, which is what makes the soft-versus-sharp contrast possible |
| Objective-aware bots ([06](../06-ai-bots.md)) | 4 per side: attack, escort the carrier, chase the enemy carrier, recover a dropped flag |
| F.C.S. callouts ([05](../05-fcs-ai-assistant.md)) | Text-only, priority-free, reacting to flag events and the collapse |
| Cells are 0.5 m ([10](../10-art-direction-and-cinematics.md)) | Characters stand 3.7 cells tall (~1.85 m) |

## What it does not implement

Named here so the prototype is not mistaken for the game:

- Online multiplayer — bots only, all local
- The four character classes — one generic loadout
- **Act III, the sky towers** — the prototype ends after the underground
- Hit-stop and impact frames, which is where most of the perceived punch would come from
- F.C.S. voice, and player questions to F.C.S.
- Chat, moderation, progression, matchmaking
- Cell breaking / placing (unresolved — [12](../12-open-questions.md), Q1)

Match length is compressed to 3 minutes with the collapse at 60s, so the
transition is reachable quickly. The docket specifies 15 minutes.

## The start screen

A full front-end rather than a play button: wordmark and live-match clock, a hero
with **ENTER THE BATTLE**, the three-act phase bar, an F.C.S. panel, class
selection, and the active loadout.

- **Phase names** — Citadel, Underdeep, Skyforge — are used in-game too, so the
  HUD label matches the lobby.
- **F.C.S. panel** answers for real. *Flag status*, *Strategy* and *Team help*
  each return a different briefing line, as does *F.C.S. intel*.
- **Class selection is not cosmetic.** Each of the four paths changes movement
  speed, one ability cooldown, the flag-carry penalty, or dash invulnerability:

  | Path | Effect |
  |---|---|
  | **Guardian** | 0.86× speed, slam cooldown 0.65×, heaviest carry penalty |
  | **Swiftblade** | 1.20× speed, dash cooldown 0.65×, lightest carry penalty |
  | **Element** | Baseline speed, grapple cooldown 0.62× |
  | **Shadow** | 1.10× speed, dash invulnerability 2.6× |

  These are deliberately small stand-ins for the full kits in
  [13](../13-abilities-and-skills.md), which are not implemented.
- **Field pickups are labelled "not in this build"** on the screen itself. The
  Scout Knife is the only weapon; the pickup roster is design intent and the
  screen says so rather than implying otherwise.

## Health, shield and weapons

**100 health under 75 shield** — damage eats shield first, so a full target has
175 effective. Shield does not regenerate; it is a per-life resource that resets
on reboot. Health regrows slowly after four seconds out of combat.

| Weapon | Key | Damage | Hits to drop a full target | Notes |
|---|---|---|---|---|
| **Blade** | 1 | 35 | 5 | Melee, ~1.9 m reach, 0.42s between swings |
| **Rifle** | 2 | 75 | 3 | Hitscan out to 35 m, tracer, 0.8s between shots |
| **Rocket** | 3 | 150 | 2 | Travelling projectile, 3.5 m blast, 2.6s reload |

**Worth knowing:** with 75 shield on top of 100 health, a rocket no longer drops a
full-health target in one hit — 150 is less than 175, leaving 25 health. It is a
one-shot against anyone who has already lost their shield. If a guaranteed
one-shot is wanted, either the rocket needs 175+ or the shield needs to come down.

Damage falls off toward the edge of a blast, so a near miss wounds rather than
kills, and rockets do not hurt teammates.

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

## Spawn safety

Spawn points are **validated, not assumed**. `findSpawn` looks for ground near the
expected level, checks the whole player box clears, and requires at least two
free directions to walk in — retrying up to 80 candidates before widening the
search.

This came from a reported bug: players sometimes spawned inside a tree or
somewhere they could not move. Sampling 800 spawns of the old code found **26% of
base spawns and 13.5% of reboot spawns landed inside geometry.** Two authoring
mistakes caused it, and both are fixed at source rather than only being validated
around:

- A rock cluster was placed at `(30,12)` — two cells from Azure's base centre at
  `(29,10)`, so it sat inside the spawn ring. `rockCluster` now refuses to build
  inside any base or reboot pad.
- The reboot pad's glowing core is a solid cell at the pad centre, and the spawn
  ring started 1.2 cells out — close enough for the player box to overlap it.

After both fixes: **0 bad spawns in 2,000 samples** across base, reboot, surface
and underdeep.

## Where the prototype deviates from the docket

Deliberate, so the demo fits in a few minutes on modest hardware. Nothing here is
a proposed design change:

| Value | Docket | Prototype | Why |
|---|---|---|---|
| Map | — | 116 × 116 cells (58 m square) | Four times the earlier area |
| Match length | 15 min | 3 min | Reach the collapse quickly |
| Collapse at | 6:00 | 1:00 | Same |
| Respawn timer | 8s | 4s | Short match |
| Team size | 8v8 | 5v5 | Frame budget in a browser |
| Debris cap | 5,000 | 2,400 | Browser frame budget |
| Acts | Three | Two — Skyforge is not built | The ascent is not implemented |

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
