# 10 — Art Direction & Cinematics

## Direction: a surreal world of soft rounded forms

From the brief: prioritise **creativity, scale and exciting environments** over
photorealism. Players should feel like they are inside an epic adventure.

**Style target:** a **dreamlike, surreal world built from soft rounded forms.**
Nothing is a sharp cube. Terrain is made of rounded, pebble-like masses that
interlock into rolling ground; structures are arches and rings rather than
crenellated walls; the sky is a deep violet-to-coral gradient; glowing orbs drift
above the battlefield. Characters are smooth, round, big-eyed creatures.

This is deliberately **not** a blocky Minecraft-style look, and not realism
either. It is closer to an illustrated dream than to either.

## The important distinction: grid underneath, rounded on top

The world is still **simulated** as a grid of half-metre cells. That is what makes
the transitions work — see [11](11-technical-architecture.md#the-voxel-data-model)
and the reasoning below. What changed is how those cells are **drawn**: each one
renders as a spherified, soft-shaded mass rather than a hard cube.

So the technical argument for a grid world survives intact while the aesthetic is
free to be anything:

| Transition | Still works because |
|---|---|
| **The Collapse** | The terrain genuinely comes apart into its constituent cells. They tumble as rounded masses instead of cubes — the same system, softer forms. |
| **The Underground** | Just more cells below. Same world, same grid, deeper down — no second map to load, no handoff. |
| **The Ascent** | Cells detach and re-stack upward into towers. The world rebuilds itself in place. |

**This is the whole technical argument, and it is unchanged by the style.** In a
conventional art pipeline the collapse is three authored destruction set-pieces
that must look identical on 16 clients. On a grid it is one system that produces
spectacle almost for free, and the acts stop being separate maps that need
swapping — they are one continuous world you travel through vertically. The
brief's *"it should feel like a continuation of the same battle"* becomes
literally true rather than an illusion to maintain.

## Why surreal and rounded

### 1. It is the strongest available answer to "epic adventure"

The brief does not ask for a war. It asks for an adventure with cinematic moments
worth sharing. A violet sky, floating islands and drifting lanterns deliver that
in the first second of the first screenshot. A grass-and-grey-stone battlefield
does not; it reads as generic.

### 2. Readability without harshness

Two teams, a flag, hazards, and a world that keeps changing. Soft forms with
strong rim lighting and saturated colour separate cleanly against every
background, and the palette per act is so distinct that a player always knows
where they are.

### 3. Age-appropriate by construction

Round, wide-eyed creatures in a dreamscape read as adventure. There is no uncanny
valley, no injury detail, no realism to push it anywhere uncomfortable. The style
does the age-rating work.

### 4. Scale is cheap

Enormous environments come from a small vocabulary — a rounded mass, a sphere, a
palette per act. A small team can build a huge world.

### 5. It is nobody else's look

The most common failure mode for a grid-based game is looking like a Minecraft
mod. Rounded surreal forms sidestep that entirely: there is no resemblance to
defend, no textures anyone could mistake for copied, and no legal exposure worth
worrying about. The style is the differentiator, not a liability.

## The rendering signature

Three choices do most of the work, and all three are cheap:

- **Spherified geometry.** Every world cell is a subdivided cube pulled ~45%
  toward a sphere, with smooth normals. Soft silhouettes, no hard edges.
  Cells render slightly oversized so they interlock into one continuous mass
  rather than reading as separate pebbles.
- **Rim light.** A coloured rim term — warm rose on the surface, violet in the
  deep — traces every silhouette. This is what makes the world look lit by the
  sky rather than by a lamp, and it is the single largest contributor to the
  dreamlike quality.
- **Two-tone lighting.** A warm key with a cool coloured fill from the opposite
  side, so shadowed faces read as tinted rather than grey. Nothing in the world
  is ever neutral-dark.

The sky is a gradient behind the scene, not geometry — cheaper and smoother than
any dome, and it cross-fades when the phase changes.

## Grid and scale (proposed)

| Element | Size |
|---|---|
| **World cell** | 0.5 m — terrain, structures, towers (drawn rounded, not cubic) |
| **Detail element** | 0.125 m — props, trim |
| **Player height** | ~1.25 m — short, wide and round; deliberately not humanoid |
| **Arch / structure height** | 10–20 m — must still feel monumental |
| **Sky tower height** | 100 m+ |

## The three worlds

Each act must be recognisable from a single frame. The palettes are deliberately
opposed, and each is dominated by colours the others do not use at all.

### Act I — The Dreamfield

- **Ground:** rolling, never flat — pale lilac at the crests, deeper violet in the
  hollows
- **Palette:** lilac, violet, indigo, with iridescent teal and coral accents
- **Sky:** deep violet at the zenith falling to coral and warm peach at the
  horizon
- **Forms:** two great arches spanning midfield instead of a castle wall; tall
  slender spires topped with glowing bulbs; floating islands with lanterns slung
  beneath them; drifting motes of light
- **Bases:** circular platforms ringed with pillars, open toward midfield, a
  glowing orb hanging above each flag
- **Light:** warm key, violet fill, rose rim
- **Sound:** open air, soft chimes, a distant low drone

### Act II — The Glowing Deep

- **Ground:** near-black indigo, rolling
- **Palette:** the darkest act and the most colourful, because every light source
  is an object — magenta and cyan bioluminescence, glowing violet pools
- **Forms:** enormous glowing caps on slender stalks; pools of light in the
  hollows; spires hanging out of the dark above
- **Light:** emissive forms doing the work; violet fill; violet rim
- **Sound:** close and echoing, dripping, a deep hollow pulse

### Act III — The Sky Towers

- **Palette:** blinding pale gold and white against deep blue, iridescent edges
- **Forms:** colossal smooth towers, floating platforms, long thin bridges with
  nothing beneath them
- **Light:** full unfiltered sun above the cloud layer — the visual reward for ten
  minutes in the dark
- **Sound:** thin air, howling wind, the hum of ancient machinery

## Characters

**Round creatures, not humanoid warriors.** A large egg-shaped body over a fuller
lower blob, oversized eyes standing proud of the surface, a small mouth, stubby
limbs, and a little antenna. Roughly **1.25 m tall** — short, wide and appealing
rather than soldierly. Built from smooth spheres, so they are the softest thing
on screen.

**Why this and not armoured humanoids.** The game is for ages 10 and up, and the
brief asks for an epic adventure rather than a war simulation. Appealing
characters serve that better than realistic ones, and they push the fantasy
combat further from anything uncomfortable. A knockdown between two round
wide-eyed creatures is unmistakably adventure. It also makes the game
screenshot-friendly, which serves the shareability goal directly.

**The face carries the likability.** Eyes are large, faintly emissive so they
still read in Act II's darkness, and they blink on a loose timer. Characters bob,
squash and stretch as they walk. None of this is expensive, and all of it is the
difference between a character and a shape.

The four classes must still be identifiable **by silhouette alone**, because in a
fight that is all a player gets. Class reads through proportion and one
accessory, never through colour — colour belongs to the team:

| Class | Silhouette |
|---|---|
| **Guardian** | The largest and widest, low and heavy, a broad shield nearly as big as itself. Reads as a wall. |
| **Swiftblade** | The smallest and narrowest, leaning forward, trailing a scarf. Reads as fast even standing still. |
| **Element Warrior** | Taller and rounder, motes orbiting it in the current element's colour, eyes tinted to match. Reads as dangerous at range. |
| **Shadow Runner** | Small and hooded, body darkened, its eyes the only bright thing about it. Reads as *hard to see*, which is the point. |

**Team identity:** every character has its own colour, but one team's palette is
entirely **cool** and the other entirely **warm** — personality without costing
team readability. Warm-versus-cool also survives colour-blindness, where
red-versus-green would not. On top of that, a floating team-coloured marker above
allies.

**The player's own character** floats a spinning gold gem with a soft halo, so a
player can always find themselves in a crowd.

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
3. **The break.** The ground comes apart into its constituent masses. Arches
   collapse. Spires topple. The floating islands lose their anchors and the
   lanterns fall with them — thousands of rounded forms and glowing orbs tumbling
   together into the dark.
4. **The fall.** The player falls *with* the wreckage of the field they were
   defending, the dreamfield receding into a bright hole above them.

The prototype confirms this reads beautifully: soft tumbling masses and drifting
lights against a violet void, rather than rubble.

### 2. The arrival in the deep

Landing: the cavern opens out and the scale of the glowing deep becomes visible.
Bioluminescent caps and pools placed to draw the eye across the space so the
player reads its size in one second. Debris from the surface lies scattered where
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
- Crisp, modern, softly-rounded UI against the dreamlike world — do **not** make
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
