# 10 — Art Direction & Cinematics

## Direction: a stylised battlefield with square figures

From the brief: prioritise **creativity, scale and exciting environments** over
photorealism. Players should feel like they are inside an epic adventure.

**Style target, in two halves that deliberately contrast:**

- **The world — soft, stylised, vivid.** A battle-royale landscape: rolling green
  hills, buildings with tile roofs, a pond and a bridge, rock formations, trees.
  Saturated colour, bold readable silhouettes, spectacle over detail. Built on a
  grid of half-metre cells drawn as **soft rounded masses**, so it comes apart
  convincingly when the battlefield transforms.
- **The figures — hard squares.** Blocky humanoids built from sharp-edged cubes:
  head, torso, two arms, two legs, limbs swinging from their joints. Simple,
  instantly readable, and cheap to produce in any quantity.

**The contrast is the point.** Sharp-edged figures against a soft rounded
landscape separate cleanly at every distance — the thing that matters most in a
game where you need to spot an opponent across a field. Nothing else on screen
has a hard edge, so a player reads as a player immediately.

## Directions explored and set aside

Recorded so they are not re-proposed, and because each taught something worth
keeping:

| Direction | Why it was set aside |
|---|---|
| **Blocky Minecraft-style world** | Invited an unflattering comparison and read as generic |
| **Surreal dreamscape** (violet sky, floating islands, glowing motes) | Judged *too crowded* — objectives were lost in the noise. Produced the density rule below, which still stands |
| **Round blob characters** | Read as stacked boxes, not as rounded creatures. Primitives cannot fake smooth organic form |
| **Cel-shaded anime characters** | The look needs *drawn* characters. Approximating anime from procedural boxes was not close, and no amount of shading fixed the geometry. Authored 2D art on billboards did work, and is a viable route if the direction is ever revisited — but it makes an opponent's facing unreadable, which is a real competitive cost |

**The general lesson, worth keeping:** a shader can change how geometry is *lit*,
never what it *is*. When a look was not achievable, the fix was always to change
the geometry or the source art, not to add another shading term.

## The rendering signature

Cel shading, which suits both halves of the direction:

- **Hard-stepped light.** Three bands with sharp terminators instead of a smooth
  falloff. Flat, poster-like, and it keeps the palette readable at distance.
- **Ink silhouette.** Grazing-angle darkening toward near-black, so figures are
  outlined against whatever is behind them. Applied fully to figures and at about
  a third strength to terrain — outlining every terrain cell turns the ground into
  noise.
- **Rim light.** A restrained rim tracing silhouettes, so a figure separates from
  a busy background.
- **Specular pops.** Tight highlights that keep surfaces from reading as flat
  colour.

## The world still sits on a grid

Unchanged and non-negotiable, because it is what makes the transitions work — see
[11](11-technical-architecture.md#the-voxel-data-model). Terrain is a grid of
half-metre cells drawn as soft rounded masses, so it genuinely comes apart into
its constituent pieces during the Collapse and re-stacks during the Ascent.

**Production note:** a shipping version would likely keep the *terrain* on the
destructible grid while building *structures* — towers, bridges, bases — from
authored meshes that shatter into pre-fractured pieces. That gets sculpted,
interesting architecture without giving up the destruction that the whole game
depends on. The grid is a simulation requirement, not an aesthetic one.

## Where the "wow" actually comes from

Not from surface detail. From four things, in rough order of impact:

1. **The transitions.** A battlefield coming apart under you is a bigger moment
   than any texture.
2. **Ability spectacle** ([13](13-abilities-and-skills.md)). Anime-scale effects:
   an afterimage trail on a dash, a hooked enemy dragged across the ground, an
   updraft launching a teammate onto a tower.
3. **Impact framing.** Two techniques worth budgeting for, both cheap and both
   central to how action games feel: **hit-stop** — a few frames of freeze on a
   heavy connect — and **impact frames**, a single high-contrast flash on the
   biggest hits. Nothing else buys as much perceived punch per unit of effort.
4. **Camera drama on ultimates.** A brief push-in and time dilation when an
   ultimate fires, then straight back to play.

## Restraint is part of the style

**Learned from playtesting, and worth stating as a rule:** an earlier pass filled
the surface with floating islands, drifting motes, glowing orbs and dozens of
spires. It was immediately judged *too crowded* — the objectives were lost in the
noise and the space stopped reading as a battlefield.

The correction, which the prototype now follows:

- **Open sightlines first.** A player must be able to see the enemy base
  direction, their own flag, and the approaching enemy from most of the map.
- **Few object types, well spread.** One wall, two towers, eighteen trees. Not a
  forest, not a sculpture garden.
- **Emissive is rationed.** Only things that *matter* glow — flags, beacons, the
  player's own marker, hazards. Decoration never glows.
- **Empty ground is a feature.** It is where fights happen and where a carrier
  gets caught. Filling it removes the game.

Density is a gameplay decision disguised as an art decision. Every prop added to
the middle of the map removes a sightline from a defender.

## Grid and scale (proposed)

| Element | Size |
|---|---|
| **World cell** | 0.5 m — terrain, structures, towers (drawn rounded, not cubic) |
| **Detail element** | 0.125 m — props, trim |
| **Player height** | ~1.85 m — blocky square figure |
| **Arch / structure height** | 10–20 m — must still feel monumental |
| **Sky tower height** | 100 m+ |

## The three worlds

Each act must be recognisable from a single frame. The palettes are deliberately
opposed.

### Act I — Citadel

- **Ground:** rolling green hills with real relief — enough to break sightlines
  and hide an approach, never so much that the space stops reading
- **Palette:** saturated grass green, earth brown, grey stone, timber, terracotta
  roof tile
- **Sky:** bright daylight, near-white at the horizon deepening to strong blue
  overhead, with puffy clouds
- **Points of interest** — the thing that makes a battle-royale landscape feel
  like a *place* rather than an arena. Each is a small fight venue with its own
  character:
  - **Buildings** with plaster or timber walls, window gaps, a doorway, and
    pitched tile roofs. Enterable, defensible, and worth fighting over.
  - **A pond** in a hollow with a sandy shore, crossed by a **plank bridge** —
    a natural chokepoint that also reads as scenery.
  - **Rock formations** for cover and elevation.
  - **A ruined stone wall** across midfield with two gaps, flanked by **towers**
    for height and as grapple anchors.
  - **Trees** with rounded canopies and bushes at their feet.
- **Horizon:** distant hills beyond the playable area, fogged for atmospheric
  perspective. Cheap, and it stops the world feeling like it ends at a boundary.
- **Bases:** circular timber platforms ringed by a low team-coloured wall, open
  toward midfield, a gold pedestal holding the flag
- **Light:** warm key, cool sky fill, subtle rim
- **Sound:** open air, wind, distant battle

**The POI rule, learned the hard way** (see *Restraint* below): points of interest
belong on the **flanks**, not in the central lanes. They should reward a player who
chooses to route through them, never block the sightline of a defender watching
the direct approach.

### Act II — Underdeep

- **Palette:** cool grey and near-black rock, lit by orange lava and pale cyan
  crystal — the darkest act, and the only one where light sources are objects
- **Forms:** rock columns, some crystal-tipped, for cover and grapple anchors;
  lava pools in the hollows; sparse stalactites out of the dark above
- **Light:** low ambient, emissive forms doing the work
- **Sound:** close and echoing, dripping, a deep hollow pulse

### Act III — Skyforge

- **Palette:** pale stone and gold against deep blue, bright cloud below
- **Forms:** colossal smooth towers, floating platforms, long thin bridges with
  nothing beneath them
- **Light:** full unfiltered sun above the cloud layer — the visual reward for ten
  minutes in the dark
- **Sound:** thin air, howling wind, the hum of ancient machinery

## Characters

**Square figures.** Hard-edged cubes: head, torso, two arms, two legs, plus a belt
and simple square eyes. Roughly 1.85 m.

**Colour is split three ways, not one hue per character.** A skin-toned head, a
team-coloured outfit on torso and arms, and dark neutral trousers. A single
saturated colour over a whole figure reads as plastic; splitting it gives value
contrast and lets the outfit carry team identity without the character looking
like a toy. A team-coloured band across the top of the head reinforces the read at
distance. Skin tones vary across the roster.

**The walk has to be right, and the numbers matter.** Limbs pivot at hip and
shoulder with arms counter-swinging against the legs, but three details do the
actual work:

- **Cadence.** *Proposed:* about **1.3 stride cycles per second at run speed**
  (~2.7 steps/sec). An early build ran at 9 steps/sec — the same animation, four
  times too fast, and it read as broken rather than quick. Stride rate should be
  driven by distance travelled, not by time, so it stays correct at every speed.
- **Amplitude scales with actual speed**, and a stationary figure eases back to a
  neutral stance instead of freezing mid-stride.
- **The body rises twice per cycle**, once per footfall, and the figure leans
  slightly into a run. Legs shorten a little at the extremes, which reads as a
  knee bend and stops the swinging foot scraping the ground.

**Why square, against a rounded world.** Contrast. The landscape is the only soft
thing on screen and the figures are the only hard-edged thing, so players separate
from terrain instantly at any distance. It also makes the roster trivially cheap
to extend — a new character is a palette, not an art commission.

The four classes must be identifiable **by silhouette alone**, because in a fight
that is all a player gets. Class reads through proportion and one accessory, never
through colour — colour belongs to the team:

| Class | Silhouette |
|---|---|
| **Guardian** | Broadest and heaviest, thick limbs, a shield slab on one arm. Reads as a wall. |
| **Swiftblade** | Narrowest and shortest, leaning forward, a trailing marker. Reads as fast even standing still. |
| **Element Warrior** | Tallest, with motes orbiting in the current element's colour and eyes tinted to match. Reads as dangerous at range. |
| **Shadow Runner** | Small and darkened, its eyes the only bright thing about it. Reads as *hard to see*, which is the point. |

**Team identity:** every character has its own colour, but one team's palette is
entirely **cool** and the other entirely **warm** — personality without costing
team readability, and warm-versus-cool survives colour-blindness where
red-versus-green would not.

**Character customisation** is where the cosmetic economy in
[09](09-progression-and-rewards.md) earns its keep. Square figures take colour,
pattern and accessory swaps cheaply, which suits a cosmetic-only economy well.

**The player's own character** floats a spinning gold gem, and is hidden entirely
when the camera ends up point-blank, as in any third-person game.

## Cinematic moments

The four moments the brief asks for.

### 1. The world breaks apart

The most important visual in the game — it happens in every player's **first
match**, six minutes in, and it is the moment they realise Flagbound is not a
normal capture-the-flag game.

Staging:

1. **Tremors.** Loose masses rattle in place. Motes scatter. Dust lifts.
2. **Fracture.** Glowing seams trace across the ground, so the world telegraphs
   exactly what is about to give way.
3. **The break.** The ground comes apart into its constituent masses. The wall comes down,
   towers topple, and thousands of rounded masses tumble into the dark together.
4. **The fall.** The player falls *with* the wreckage of the field they were
   defending, the surface receding into a bright hole above them.

The prototype confirms this reads well: soft tumbling masses rather than rubble.

### 2. The arrival underground

Landing: the cavern opens out and its scale becomes visible. Lava and crystal
placed to draw the eye across the space so the player reads its size in one
second. Debris from the surface lies scattered where
it fell, which quietly says *this is the same world, you just fell through it.*

### 3. The towers rise

Ancient machinery ignites. Light runs through the ruins in sequence. Then the
structures **re-stack upward**, assembling into towers as they climb, the world
rebuilding itself around the player as they ride it. Breaking through the cloud
layer into full sun is the peak of the match's visual arc.

### 4. The final-second capture

Not authored geometry — an authored *response*. When a capture lands in the last
few seconds: time dilation, camera push, sound drop-out and swell, a burst of
team-coloured light from the flag, and an automatically saved highlight clip.

## Defeat: disintegration

**When a player is defeated they disintegrate.** The figure comes apart into motes
that sweep upward from the feet, with a single bright flash at the moment of the
hit. Nothing is left behind.

This is not only an effect — it settles a design problem the docket has to answer
anyway. The brief targets ages 10 and up, and defeat has to be *legible and
satisfying* without a body on the ground:

- **No corpse, no gore, nothing to linger on.** The screen resolves itself.
- **It reads at distance.** A rising column of motes tells the whole team someone
  went down over there, which is real tactical information a ragdoll does not give.
- **It is team-coloured**, so you can tell at a glance whether you just lost a
  teammate or gained a kill.
- **It sweeps bottom-to-top rather than bursting**, which takes about a second and
  gives the moment weight — a burst reads as an accident, a sweep reads as an
  elimination.
- **It costs almost nothing.** A few dozen particles per defeat.

Implemented in the prototype. It also makes the temporary nature of elimination
obvious: the player dissolved, and will re-form at their base.

## Shareability

*Proposed:* automatic highlight capture on a defined trigger set — final-30
captures, captures during a transition, successful long escort runs, and
first-discovery route runs. Clips short, auto-trimmed, exportable.

The collapse is inherently screenshot-bait in this style. A free-camera photo
mode would cost little and generate much of the sharing the brief asks for.

## Interface

- Minimal HUD — health, stamina, ability cooldowns, flag status, timer, score
- Flag status always visible; it is the only thing that decides the match
- **A prominent phase timer** so transitions are anticipated, not ambushing
- **An objective tracker** naming the current objective and its distance, pinning
  to the screen edge with an arrow when off-view. Playtesting the prototype
  showed the flag is genuinely hard to find in a large open world without this.
- **A beacon** rising from each flag, visible over structures from anywhere on the
  map, retained while the flag is carried so the carrier stays findable
- F.C.S. callouts as unobtrusive lower-third text with subtitles
- Crisp, modern, softly-rounded UI against the world — do **not** make
  the interface pixel-art or blocky. Keeping small text legible matters more for
  younger players than stylistic consistency in the chrome.

## Audio

- **Music per act**, with the two transitions scored as the crescendos they are
- Layered adaptive score — intensity follows flag state and time remaining
- Three completely distinct sound beds; a player should know which act they are in
  with their eyes closed
- **The collapse has its own signature:** thousands of soft masses coming apart at
  once. Build the mix around it rather than burying it under orchestral score.
- **F.C.S. always wins the mix.** If a collapse warning cannot be heard over the
  collapse, the warning is useless.
- Distinct loud identity for every hazard

## What the style does not excuse

Soft and colourful is not permission to be vague:

- **Lighting is where the money goes.** The rim and fill terms are the look; get
  them wrong and it turns to mush.
- **Silhouettes must be composed.** A rounded arch can be monumental or it can be
  a lump, and the difference is entirely layout craft.
- **Animation must have weight.** Round characters need snappy, exaggerated,
  well-timed motion; floaty animation is the fastest way to look amateur.
- **Contrast must be maintained.** A world this saturated can lose its objectives
  in the noise. Flags, players and hazards need values that separate from the
  environment in all three acts, and this must be tested per act.
