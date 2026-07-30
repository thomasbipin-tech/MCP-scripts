# 10 — Art Direction & Cinematics

## Direction: cel-shaded anime characters in a vivid stylised world

From the brief: prioritise **creativity, scale and exciting environments** over
photorealism. Players should feel like they are inside an epic adventure.

**Style target, in two halves:**

- **Characters — anime.** Slim, tall, stylish figures with sharp silhouettes,
  dramatic spiky hair, oversized expressive eyes, and scarves and coats that
  trail behind them. Cel-shaded: hard-edged shadow terminators, ink-dark
  silhouette lines, hot rim light, and bright specular pops on hair and armour.
  They should look like characters from an action anime, not like soldiers.
- **World — stylised, vivid, large.** Saturated colour, bold readable silhouettes,
  exaggerated scale, spectacle over detail. The reference point for the *world* is
  a modern stylised battle-royale look: instantly legible, colourful, and
  cheerful, with the drama coming from scale and events rather than surface
  realism.

The combination is the pitch: **anime heroes doing impossible things on a
battlefield that keeps falling apart.**

## Two ways to ship anime characters

This is a real fork, and it should be decided deliberately rather than drifted
into.

### Route A — 3D cel-shaded models (the genre norm)

Sculpted, rigged characters with authored hair, cloth and a facial rig, lit by a
cel-shading pipeline.

- **Gives:** full freedom of camera angle, real 3D animation, correct occlusion,
  facing readable from any direction.
- **Costs:** character artists, riggers, animators, and a shading pipeline —
  ramp textures, a controllable terminator, an outline pass, per-material control.
  This is the largest budget line the art direction implies.

### Route B — authored 2D art on billboards (what the prototype uses)

Each character is a drawn illustration, rasterised to a texture and composited
into the 3D world facing the camera.

- **Gives:** *the truest anime line quality available*, because the art is
  literally drawn rather than approximated by a shader. Dramatically cheaper. One
  illustrator can produce a full roster.
- **Costs:** limited viewing angles (the prototype authors a front and a back view
  and mirrors for left/right), animation must be done as layered puppet motion or
  frames rather than skeletally, and **facing becomes a gameplay problem** — a
  billboard always faces you, so you cannot read which way an opponent is looking
  without an explicit cue.

**The prototype takes Route B deliberately.** It is the only route that produces
genuinely anime-looking figures without an art team, and it proves the direction
in a way a shader pass over primitives cannot. Earlier attempts to approximate
anime characters from procedural boxes were not close, and no amount of shading
fixed the underlying geometry.

**Recommendation:** Route A for a shipping product in this genre, because facing
and camera freedom matter in competitive play. Route B is worth keeping in mind
for a stylistically distinctive alternative, and it is far from a toy — several
shipped games use billboarded or 2D-composited characters to great effect. Tracked
as an open question in [12](12-open-questions.md).

## The rendering signature

Four choices carry the anime read. All are cheap, and the prototype implements
all four:

- **Hard-stepped light.** Three bands with sharp terminators instead of a smooth
  falloff. This one choice does more than the rest combined.
- **Ink silhouette.** Grazing-angle darkening toward near-black, so every figure
  is outlined against whatever is behind it. In production this becomes a proper
  outline pass; the prototype fakes it with a fresnel term, which is convincing
  in motion and cheap.
- **Hot rim light.** A bright, hard-edged rim tracing each silhouette — the
  signature of anime key art, and it also solves the gameplay problem of figures
  separating from a busy background.
- **Specular pops.** Tight highlights on hair and armour. Small, and they are what
  make a character look *drawn* rather than lit.

**Applied unevenly on purpose:** figures get the full treatment; terrain gets
about a third of it. Outlining every terrain cell would turn the ground into
visual noise — the same crowding mistake described below, arriving through the
shader instead of through props.

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
   central to how anime action feels: **hit-stop** — a few frames of freeze on a
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
| **Player height** | ~1.85 m — slim anime build, long-legged |
| **Arch / structure height** | 10–20 m — must still feel monumental |
| **Sky tower height** | 100 m+ |

## The three worlds

Each act must be recognisable from a single frame. The palettes are deliberately
opposed.

### Act I — The Surface

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

### Act II — The Caverns

- **Palette:** cool grey and near-black rock, lit by orange lava and pale cyan
  crystal — the darkest act, and the only one where light sources are objects
- **Forms:** rock columns, some crystal-tipped, for cover and grapple anchors;
  lava pools in the hollows; sparse stalactites out of the dark above
- **Light:** low ambient, emissive forms doing the work
- **Sound:** close and echoing, dripping, a deep hollow pulse

### Act III — The Sky Towers

- **Palette:** pale stone and gold against deep blue, bright cloud below
- **Forms:** colossal smooth towers, floating platforms, long thin bridges with
  nothing beneath them
- **Light:** full unfiltered sun above the cloud layer — the visual reward for ten
  minutes in the dark
- **Sound:** thin air, howling wind, the hum of ancient machinery

## Characters

**Anime figures.** Slim and tall — roughly **1.85 m**, long-legged, narrow through
the waist and shoulders, closer to seven heads tall than to a stocky game
silhouette. Nothing about the proportions is realistic; they are drawn
proportions, chosen to look striking in motion.

In the prototype these are **drawn illustrations** — SVG art rasterised to a
texture and billboarded into the 3D world — not geometry. That is what finally
made them read as anime.

The features that do the work, in order:

| Feature | Why it matters |
|---|---|
| **Hair** | The strongest anime signal available, and the fastest way to make a character recognisable at distance. Bold swept spikes with a designed shape, in a colour that reads as an accent. |
| **Eyes** | Oversized, tall, with a defined iris and a bright specular highlight. Set proud of the face so they read at third-person distance. Blinking on a loose timer. |
| **Trailing cloth** | A scarf or coat tail that swings against the stride. Cheap, and it is most of what makes a figure feel fast. |
| **Silhouette accessories** | One bold, class-defining shape per class — the thing you recognise before you recognise anything else. |
| **Pose and timing** | Snappy, exaggerated, strongly-posed animation. An anime character never moves smoothly through a transition; it snaps between readable shapes. |

The four classes must be identifiable **by silhouette alone**, because in a fight
that is all a player gets. Class reads through proportion and one accessory,
never through colour — colour belongs to the team:

| Class | Silhouette |
|---|---|
| **Guardian** | Heaviest build, broad shoulder plates, an oversized shield slung on one arm, a long coat. Reads as a wall. |
| **Swiftblade** | Slightest and fastest, hair swept hard back, a long trailing scarf, a blade held low. Reads as fast even standing still. |
| **Element Warrior** | Tall and upright, layered robes, motes orbiting in the current element's colour, eyes tinted to match. Reads as dangerous at range. |
| **Shadow Runner** | Hooded, hunched, darkened, eyes the only bright thing about it. Reads as *hard to see*, which is the point. |

**Team identity:** every character has its own colour, but one team's palette is
entirely **cool** and the other entirely **warm** — personality without costing
team readability. Warm-versus-cool also survives colour-blindness where
red-versus-green would not. Hair takes an accent colour drawn from the same
temperature, so a bright hairstyle never makes a player misread which side someone
is on. On top of that, a floating team-coloured marker above allies.

**Character customisation** is where the cosmetic economy in
[09](09-progression-and-rewards.md) earns its keep. An anime direction is a
natural fit for outfits, hairstyles, colours and accessories — and it must include
skin tone and body options, because an audience this age needs to be able to make
a character that looks like them.

**The player's own character** floats a spinning gold gem, so a player can always
find themselves in a crowd.

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
