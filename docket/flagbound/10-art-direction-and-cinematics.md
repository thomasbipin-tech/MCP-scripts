# 10 — Art Direction & Cinematics

## Direction: a rounded block world

From the brief: prioritise **creativity, scale and exciting environments** over
photorealism. Players should feel like they are inside an epic adventure.

**Style target:** a **grid-built world drawn in soft rounded forms.** Green rolling
ground, grey stone walls and towers, trees with rounded canopies, a clear daylight
sky. Recognisable and readable — a classic battlefield — but every mass is a
softened, spherified form rather than a hard cube, and the figures are rounded
humanoids with big friendly eyes rather than armoured soldiers.

The result reads as familiar and welcoming rather than either harsh or abstract.

## The important distinction: grid underneath, rounded on top

The world is **simulated** as a grid of half-metre cells. That is what makes the
transitions work — see [11](11-technical-architecture.md#the-voxel-data-model).
What differs from a conventional block game is how those cells are **drawn**: each
renders as a spherified, smooth-shaded mass, oversized slightly so neighbours
interlock into one continuous surface.

So the technical argument for a grid world survives intact while the surface
treatment stays soft:

| Transition | Still works because |
|---|---|
| **The Collapse** | The terrain genuinely comes apart into its constituent cells. They tumble as rounded masses instead of cubes — the same system, softer forms. |
| **The Underground** | Just more cells below. Same world, same grid, deeper down — no second map to load, no handoff. |
| **The Ascent** | Cells detach and re-stack upward into towers. The world rebuilds itself in place. |

**This is the whole technical argument, and no styling choice changes it.** In a
conventional art pipeline the collapse is three authored destruction set-pieces
that must look identical on 16 clients. On a grid it is one system that produces
spectacle almost for free, and the acts stop being separate maps that need
swapping — they are one continuous world you travel through vertically. The
brief's *"it should feel like a continuation of the same battle"* becomes
literally true rather than an illusion to maintain.

## Why rounded, and why a familiar setting

### 1. Readable at a glance

Two teams, a flag, hazards, and a world that keeps changing. Soft masses in
naturalistic colours — green ground, grey stone, blue sky — give players an
instantly legible space, and saturated team colours pop cleanly against it.

### 2. Rounded is the differentiator

A grid world in cubes invites exactly one comparison, and it is not a flattering
one. Rounding every form breaks the resemblance immediately while keeping all the
benefits of a grid. See the rules below.

### 3. Age-appropriate by construction

Softened, wide-eyed figures in a bright landscape read as adventure. No uncanny
valley, no injury detail, no realism to push it anywhere uncomfortable.

### 4. Scale is cheap

Enormous environments come from a small vocabulary — a rounded mass, a sphere, a
palette per act. A small team can build a huge world.

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

## Keeping clear of the obvious comparison

A rounded grid world is not a cube world, but the family resemblance is worth
managing deliberately:

- **Rounded geometry, never cubes.** This is the primary differentiator and it is
  visible in every frame.
- **No copied textures.** Every surface is originally authored. Nothing traced,
  recoloured, or ripped.
- **No signature content of any other game.** No borrowed creatures, items, or
  crafting metaphors.
- **Different lighting identity.** Smooth normals, a warm key with a cool sky
  fill, and a subtle rim on every silhouette — soft and lit, not flat and ambient.
- **Different subject.** This is a 15-minute team match on a world that comes
  apart twice, not a calm solitary sandbox.

## The rendering signature

Three choices do most of the work, and all three are cheap:

- **Spherified geometry.** Every world cell is a subdivided cube pulled ~45%
  toward a sphere, with smooth normals, rendered slightly oversized so cells
  interlock into a continuous mass.
- **Two-tone lighting.** A warm key with a cool sky-coloured fill from the
  opposite side, so shadowed faces read as daylight-tinted rather than grey.
- **A subtle rim.** A restrained rim term traces silhouettes so characters and
  structures separate from the background. Kept low — pushed hard it turns
  dreamlike, which is not the target.

The sky is a gradient behind the scene, not geometry — cheaper and smoother than
any dome, and it cross-fades when the phase changes.

## Grid and scale (proposed)

| Element | Size |
|---|---|
| **World cell** | 0.5 m — terrain, structures, towers (drawn rounded, not cubic) |
| **Detail element** | 0.125 m — props, trim |
| **Player height** | ~1.75 m (3.5 cells) — rounded humanoid |
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

**Rounded humanoid figures.** Head, torso, two arms, two legs — the familiar,
instantly readable blocky silhouette — but every part is a softened spherified
form like the rest of the world, so nothing has a hard edge. Roughly **1.75 m**
(3.5 cells), with a head about as wide as the torso.

**Why humanoid rather than an abstract shape.** A humanoid reads its facing,
stance and motion at a glance, which matters in a game where knowing whether an
opponent is coming toward you or running away decides a fight. It also gives the
four classes far more silhouette range to work with than a single body shape can.

**Limbs swing from their joints.** Legs and arms pivot on a hip and shoulder as
the figure walks, with the arms counter-swinging. It costs almost nothing and it
is most of what makes a figure look alive rather than dragged along the ground.

**The face carries the likability.** Large eyes set proud of the head's front so
they read at third-person distance, faintly emissive so they stay visible in the
caverns, blinking on a loose timer, with a small mouth below. Friendlier than a
realistic figure without being childish.

The four classes must be identifiable **by silhouette alone**, because in a fight
that is all a player gets. Class reads through proportion and one accessory,
never through colour — colour belongs to the team:

| Class | Silhouette |
|---|---|
| **Guardian** | Broadest and heaviest, thick limbs, low stance, a shield slab on one arm. Reads as a wall. |
| **Swiftblade** | Slight and narrow, leaning forward, a trailing scarf. Reads as fast even standing still. |
| **Element Warrior** | Tall and upright, robed lower half, motes orbiting in the current element's colour, eyes tinted to match. Reads as dangerous at range. |
| **Shadow Runner** | Small and hooded, body darkened, eyes the only bright thing about it. Reads as *hard to see*, which is the point. |

**Team identity:** every character has its own colour, but one team's palette is
entirely **cool** and the other entirely **warm** — personality without costing
team readability. Warm-versus-cool also survives colour-blindness where
red-versus-green would not. On top of that, a floating team-coloured marker above
allies.

**On heads and skin:** the prototype tints heads with a lightened version of the
character's own colour, which sidesteps skin tone entirely and reads as a
costumed figure. A shipping game should instead offer proper character
customisation, including skin tone, as part of the cosmetic unlocks in
[09](09-progression-and-rewards.md) — a game for this audience needs players to
be able to make a character that looks like them.

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
