# 10 — Art Direction & Cinematics

## Direction: a voxel world

From the brief: prioritise **creativity, scale and exciting environments** over
photorealism. Players should feel like they are inside an epic adventure.

**Style target:** a **voxel world** — everything is built from blocks. Castles,
forests, caves, lava, the sky towers, the characters, the flags. Blocky
silhouettes, bold flat colour, chunky readable shapes, lit with modern lighting.

Voxel does **not** mean 2011 rendering. The blocks are the *form language*, not
the fidelity ceiling. Dynamic light, volumetric dust, real shadows, glow and
depth-of-field all still apply — they just fall on cubes.

## Why voxel is the right choice, not just the cheap one

### 1. It solves the hardest problem in the project

[11 — Technical Architecture](11-technical-architecture.md) names the project's
defining risk: two full world transformations mid-match with no loading screen.

A voxel world makes that risk mostly **evaporate**:

| Transition | In a voxel world |
|---|---|
| **The Collapse** | The terrain genuinely shatters into thousands of falling blocks. The break is *the data structure doing what it naturally does.* |
| **The Underground** | Just more voxels below. Same world, same grid, deeper down — no second map to load, no handoff. |
| **The Ascent** | Blocks detach and re-stack upward into towers. The world rebuilds itself in place. |

This is the whole argument. In a conventional art pipeline the collapse is three
authored destruction set-pieces that must look identical on 16 clients. In a
voxel world it is one system that produces spectacle for free, and the acts stop
being separate maps that need swapping — **they are one continuous block world
you travel through vertically.** The brief's "it should feel like a continuation
of the same battle" becomes literally true rather than an illusion to maintain.

### 2. Readability at speed

Three worlds, four classes, two teams, constant transformation. Flat-coloured
cubes with hard edges are the most readable thing you can put on screen. A
10-year-old can tell friend from enemy from flag from hazard at a glance, in
daylight, in a dark cave, and against bright cloud.

### 3. Age-appropriate by construction

Blocky fantasy combat reads as adventure. There is no uncanny valley, no injury
detail, no realism to push it anywhere uncomfortable. The style does the
age-rating work for you.

### 4. Scale is cheap

The brief wants *massive*. Blocks let a small team build an enormous castle, an
underground city and a sky tower complex, because the vocabulary is a few hundred
block types instead of thousands of bespoke assets.

### 5. It ages out of the hardware race

Minecraft looks the same now as it did a decade ago and nobody minds. A stylised
voxel game shipped today still looks correct in 2035. Realism shipped today looks
dated in three years.

## The one hard rule: this is not a Minecraft skin

Voxel is a *form language*, like pixel art or cel shading — not Minecraft's
property. But the resemblance risk is real, and both for identity and for basic
legal hygiene:

- **No copied textures.** Every block texture is originally authored. Nothing
  traced, recoloured, or ripped.
- **No signature Minecraft content.** No creepers, no Steve, no crafting table,
  no distinctive mob designs.
- **Different grid feel.** Proposed below: a finer grid than Minecraft's, which
  changes the silhouette of everything immediately.
- **Different lighting identity.** Minecraft's look is flat and ambient.
  Flagbound's is dramatic and directional — hard shadows, strong coloured light,
  volumetric dust. Same cubes, unmistakably different game.
- **Different subject.** Minecraft is calm, solitary, creative. Flagbound is a
  loud 15-minute team war on a world that is falling apart. That contrast should
  be visible in the first screenshot.

**The test:** a player seeing one frame should think *"that's Flagbound"*, not
*"that's a Minecraft mod."*

## Grid and scale (proposed)

| Element | Size |
|---|---|
| **Structural block** | 0.5 m — walls, terrain, towers |
| **Detail voxel** | 0.125 m — props, weapons, armour trim, characters |
| **Player height** | ~2.5 structural blocks (1.25 m) — short and wide, see Characters |
| **Castle wall height** | 24–40 blocks (12–20 m) — must feel like a siege |
| **Sky tower height** | 200+ blocks |

Half-metre blocks are the key decision. They are chunky enough to read as
unmistakably voxel, fine enough to build a convincing castle arch and a
recognisable character face, and immediately distinct from Minecraft's 1 m cubes.

## The three worlds in blocks

Each act must be recognisable from a single frame. The block palettes are
deliberately opposed.

### Act I — Surface

- **Blocks:** grass, dirt, cut stone, mossy stone, oak, thatch, banner cloth
- **Palette:** bright daylight — saturated greens, warm sandstone, hard blue sky
- **Silhouette:** two great block castles with crenellated walls, cubic
  watchtowers, a long plank bridge, forests of chunky cube-canopy trees
- **Light:** hard directional sun, long sharp-edged shadows, high visibility
- **Sound:** open air, wind through leaves, distant battle

### Act II — Underground

- **Blocks:** dark basalt, ancient carved brick, glowing crystal, obsidian,
  lava, wet cobble
- **Palette:** near-black rock cut by emissive orange and cyan — the darkest act,
  and the most colourful, because every light source is a glowing block
- **Silhouette:** a ruined block city in a vast cavern, lava channels, a river
  cavern, crystal clusters that light the routes
- **Light:** emissive blocks doing the work — glowing crystal, lava glow,
  torchlight. Darkness that genuinely hides a Shadow Runner
- **Sound:** close and echoing, dripping water, deep hollow ambience

### Act III — Sky

- **Blocks:** pale polished stone, gold-veined machinery, white cloud volumes,
  glass
- **Palette:** blinding brightness — white, pale gold, deep sky blue
- **Silhouette:** colossal block towers, thin floating platforms, long narrow
  bridges with nothing under them
- **Light:** full unfiltered sun above the cloud layer — the visual reward for
  ten minutes underground
- **Sound:** thin air, howling wind, the hum of ancient machinery

## Characters

**Rounded creatures, not humanoid warriors.** Short, wide, and built on an egg
profile — widest low through the middle, domed on top — with oversized eyes,
tiny stubby limbs, and one bright saturated colour each. Roughly **2.5 blocks
tall (1.25 m)**, so they read as small, chunky and appealing rather than as
soldiers.

They are still made of blocks like everything else, so they belong to the world.
The roundness comes from overlapping slabs on a tapered profile rather than from
leaving the voxel grid.

**Why this and not armoured humanoids.** The game is for ages 10 and up, and the
brief asks for an epic adventure rather than a war simulation. Appealing
characters do more for that than realistic ones, and they push the fantasy
combat further from anything uncomfortable. A knockdown between two round
wide-eyed creatures is unmistakably adventure. It also makes the game
screenshot-friendly, which serves the shareability goal directly.

**The face carries the likability.** Eyes are large, slightly proud of the body
surface, and faintly emissive so they still read in Act II's darkness. They
blink on a loose timer. A small mouth sits below. Characters bob and squash
slightly as they walk. None of this is expensive, and all of it is the difference
between a character and a shape.

The four classes must still be identifiable **by silhouette alone**, because in a
fight that is all a player gets. Class reads through proportion and one
accessory, never through colour — colour belongs to the team:

| Class | Silhouette |
|---|---|
| **Guardian** | The biggest and widest blob, low to the ground, heavy brow over the eyes, carrying a slab shield nearly as large as itself. Reads as a wall. |
| **Swiftblade** | The smallest and narrowest, leaning forward, with a trailing scarf. Reads as fast even standing still. |
| **Element Warrior** | Taller and rounder, with voxel motes orbiting it in the current element's colour and eyes tinted to match. Reads as dangerous at range. |
| **Shadow Runner** | Small and hooded, body blocks darkened, its eyes the only bright thing about it. Reads as *hard to see*, which is the point. |

**Team identity:** every character gets its own colour, but one team's palette is
entirely **cool** and the other entirely **warm** — personality without costing
team readability. On top of that, a strong emissive trim and a floating
team-coloured marker above allies.

Emissive is essential: a flat colour that reads in Act I daylight will vanish
against Act II lava and Act III cloud. Every team colour must be tested in all
three acts, and the two palettes must stay distinguishable for colour-blind
players — which is why the split is warm-versus-cool rather than red-versus-green.

**The player's own character** carries a distinct floating marker so a player can
always find themselves in a crowd. In the prototype this is a spinning gold
diamond overhead.

## Cinematic moments

The four moments the brief asks for, staged in blocks. This is where voxel stops
being a style choice and starts being the best decision in the docket.

### 1. The ground breaks apart

The most important visual in the game — it happens in every player's **first
match**, six minutes in, and it is the moment they realise Flagbound is not a
normal CTF game.

Voxel staging:

1. **Tremors.** Loose blocks rattle in place. Dust voxels lift off surfaces.
2. **Fracture.** Glowing seams trace *along block boundaries* across the
   battlefield — the crack is grid-aligned, so the world telegraphs exactly which
   blocks are about to go.
3. **The break.** The terrain **shatters into its constituent blocks.** Castle
   walls come apart course by course. Towers topple as stacks. Thousands of cubes
   tumble into the dark, tumbling individually, catching the light.
4. **The fall.** The player falls *with the blocks*, surrounded by the wreckage
   of the castle they were defending, the surface receding into a bright square
   hole above them.

No other art style gives you that shot this easily. The blocks are already
separate objects — you are not authoring a destruction sequence so much as
switching gravity on.

### 2. The underground reveal

Landing: the cavern opens out and the scale of the block city becomes visible for
the first time. Emissive crystal and lava placed to draw the eye across the space
so the player reads the size of it in one second. Surface blocks — grass, castle
stone — lie scattered in the ruins where they landed, which quietly says *this is
the same world, you just fell through it.*

### 3. The towers launch

Ancient machinery ignites. Gold glyph-blocks light up in sequence along the
ruins. Then the structures **re-stack upward** — blocks detaching from the cavern
floor and assembling into towers as they climb, the world rebuilding itself
around the player while they ride it. Breaking through the cloud layer into full
sunlight is the peak of the match's visual arc.

### 4. The final-second capture

Not authored geometry — an authored *response*. When a capture lands in the last
few seconds: time dilation, camera push, sound drop-out and swell, a burst of
team-coloured voxel particles from the flag, and an automatically saved highlight
clip.

## Shareability

*Proposed:* automatic highlight capture on a defined trigger set — final-30
captures, captures during a transition, successful long escort runs, and
first-discovery route runs. Clips short, auto-trimmed, exportable.

The collapse is inherently screenshot-bait. Lean into it: a free-camera photo
mode would cost little and generate a lot of the sharing the brief asks for.

## Interface

- Minimal HUD — health, stamina, ability cooldowns, flag status, timer, score
- Flag status always visible; it is the only thing that decides the match
- **A prominent phase timer** so transitions are anticipated, not ambushing
- F.C.S. callouts as unobtrusive lower-third text with subtitles
- Clean modern UI as a deliberate contrast to the blocky world — do **not** make
  the interface pixel-art too. Blocky world, crisp interface: that pairing is
  part of the visual identity, and it keeps small text legible for younger
  players.

## Audio

- **Music per act**, with the two transitions scored as the crescendos they are
- Layered adaptive score — intensity follows flag state and time remaining
- Three completely distinct sound beds; a player should know which act they are
  in with their eyes closed
- **Block audio is a signature.** Thousands of individual cubes striking stone
  during the collapse is a sound no other game has. Build the collapse mix around
  it rather than burying it under orchestral score.
- **F.C.S. always wins the mix.** If a collapse warning cannot be heard over the
  collapse, the warning is useless.
- Distinct loud identity for every hazard — lava, wind, unstable platforms,
  falling debris

## What voxel does *not* excuse

Being blocky is not permission to be ugly or cheap. The bar:

- Lighting is where the money goes. Bad lighting on good voxels looks like a
  student project; good lighting on simple voxels looks like a style.
- Silhouettes must be composed. A block castle can be majestic or it can be a box
  with holes, and the difference is entirely layout craft.
- Animation must have weight. Blocky characters need snappy, exaggerated,
  well-timed motion — stiff animation is the fastest way to look amateur.
- Particle and dust work carries every transition. Budget for it.
