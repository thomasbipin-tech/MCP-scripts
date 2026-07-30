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

## What this actually costs to build

Stated plainly, because this is the most expensive art direction in the docket and
the requirement should not be discovered late:

| Need | Why |
|---|---|
| **Sculpted, rigged character models** | Anime figures live or die on face, hair and silhouette. These must be authored by character artists — they cannot be assembled from primitives. |
| **Hair as authored geometry** | Anime hair is a designed shape, not a simulation. Each character needs bespoke hair. |
| **Cloth or bone-driven cloth** | Trailing scarves and coats are half the appeal, and they must move. |
| **A facial rig** | Expression is the point of an anime character. At minimum: blink, eye direction, and a few emotive states. |
| **A cel-shading pipeline** | Ramp textures, a controllable terminator, an outline pass (inverted hull or post-process edge detect), and per-material control. Not a single shader. |
| **Skeletal animation** | A full locomotion set plus ability animations, and anime style demands *pose-driven* animation with strong silhouettes and snappy timing. |

**The prototype does not have any of this** and cannot. It approximates the
*look* — cel bands, ink edges, rim, spiky hair blocked out of primitives, big eyes
with highlights — to prove the direction reads. Actual character quality is an
art-staffing question, and it is the single largest budget line this direction
implies.

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

- **Ground:** gently rolling green, never billiard-flat, never mountainous
- **Palette:** grass green, earth brown, grey stone, timber
- **Sky:** clear daylight — pale at the horizon deepening to blue overhead
- **Forms:** a low stone wall across midfield with two gaps as chokepoints; two
  towers flanking them for height and as grapple anchors; trees with rounded
  canopies, spread thin
- **Bases:** circular timber platforms ringed by a low team-coloured wall, open
  toward midfield, a gold pedestal holding the flag
- **Light:** warm key, cool sky fill, subtle rim
- **Sound:** open air, wind, distant battle

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
