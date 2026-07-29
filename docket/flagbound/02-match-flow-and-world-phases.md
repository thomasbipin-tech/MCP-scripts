# 02 — Match Flow & World Phases

The signature of Flagbound. A match is not one map; it is one continuous battle
that passes through three worlds.

## Timeline (proposed)

The brief fixes the match at ~15 minutes and fixes the order of the three acts.
The split below is a proposal for playtesting.

| Time | Phase | What is happening |
|---|---|---|
| −0:45 → 0:00 | **Briefing** | Spawn-in, class select, F.C.S. objective brief |
| 0:00 → 5:00 | **Act I — Surface** | Open battlefield CTF |
| 5:00 → 6:00 | **Tremors** | Warning signals, first structural failures |
| 6:00 → 6:30 | **THE COLLAPSE** | Transition event — the world breaks |
| 6:30 → 10:30 | **Act II — Underground** | Hidden kingdom CTF |
| 10:30 → 11:15 | **Awakening** | Ancient technology activates, ruins begin to lift |
| 11:15 → 11:45 | **THE ASCENT** | Transition event — the world rises |
| 11:45 → 15:00 | **Act III — Sky** | Vertical sky-tower CTF, flags relocate |

**Design intent behind the shape:** each act is shorter than the last. Act I is
long enough to establish a plan, Act II long enough to break it, Act III short
enough that it is pure adrenaline.

## One world, three altitudes

The three acts are **not three maps**. They are three regions of a single
continuous vertical block world — surface at the top, the underground kingdom
several hundred metres below it, the sky towers built high above. The Collapse
drops players down through it; the Ascent lifts them up through it.

This is a structural fact, not just a visual one, and it is what makes the
brief's requirement that the underground *"feel like a continuation of the same
battle"* literally true. See
[11 — The voxel data model](11-technical-architecture.md#the-voxel-data-model).

Consequence worth designing around: **debris from Act I stays visible in Act II.**
Players land amid the shattered blocks of the castle they were just defending.

## Rules that carry across phases

These make it feel like *one battle in a changing world*, not three maps.

- **Score persists.** Captures made in Act I count at the final whistle.
- **Teams persist.** No re-shuffling between phases.
- **Progression persists.** Ability cooldowns, contribution score, and any
  in-match unlocks carry over.
- **The carrier persists.** A player carrying the enemy flag when a transition
  fires **keeps it** through the transition. Flag position is re-anchored to the
  carrier's new location, not reset. This is the single most important rule in
  this document — resetting the flag on transition would make the last minute of
  each act meaningless.
- **Nobody dies to the transition.** Transitions never eliminate players. They
  relocate them. Falling during a collapse is choreography, not a death.

## Act I — The Surface Battlefield

**Fantasy:** a classic siege. Two great bases facing each other across contested
ground.

**Contents (from brief):** castles, walls, towers, bridges, forests, open combat
areas, two opposing bases.

**Role in the match:** establish the baseline. This is where players learn the
teams, pick their lanes, and form the plan that Act II will destroy.

**Layout principles:**

- Mirrored bases so neither side has a positional advantage.
- At least three viable approach routes per base — an open charge lane, a
  covered forest flank, and a high route across walls/towers — so all four
  classes have a preferred path.
- Bridges as natural chokepoints and natural highlight moments.
- Sightlines long enough to scout from, broken enough to move through.

## The Collapse (Act I → Act II)

The brief specifies the full sequence: ground shaking, warning signals,
structures collapsing, then the battlefield breaking apart and forcing players
underground.

**Staging:**

1. **Tremors (60s out).** Loose blocks rattle in place, dust lifts off surfaces,
   distant rumbling. F.C.S. warns. Combat continues normally — this is a
   countdown players can play around.
2. **Fracture lines (30s out).** Glowing seams trace the ground *along block
   boundaries*, so players can see exactly which blocks are about to go.
   Structures start shedding pieces.
3. **The break (0s).** The battlefield **shatters into its constituent blocks**.
   Castle walls come apart course by course, towers topple as stacks, and
   thousands of cubes tumble into the dark. Players fall with the wreckage.
4. **Landing.** Players land on stable underground blocks with a brief
   invulnerability window so the transition cannot be spawn-camped.

The voxel world does most of this work natively — see
[10](10-art-direction-and-cinematics.md) for why the block-based art direction
makes the collapse the cheapest spectacle in the game rather than the most
expensive.

**Playable falling:** players keep camera and limited air control during the
drop. It is a moment, not a cutscene. Nobody wants their best flag run
interrupted by a loading screen.

## Act II — The Underground Kingdom

**Fantasy:** you did not fall into a basement. You fell into a civilisation that
was down here the whole time.

**Contents (from brief):** ancient ruins, caves, tunnels, underground rivers,
lava areas, secret pathways, hidden routes.

**Role in the match:** break Act I's plan. The route that worked on the surface
does not exist here. Stealth and route-discovery become dominant.

**Interactive elements (from brief):**

| Element | Effect |
|---|---|
| **Collapsing tunnels** | Routes close permanently mid-act — the map keeps changing *inside* the act |
| **Moving platforms** | Timed traversal over rivers and lava; skill-gated shortcuts |
| **Environmental hazards** | Lava, currents, falling rock — damage and displacement, not instant death |
| **Hidden areas** | Reward exploration with shortcuts, vantage points, and cosmetic discoveries |

**The discovery rule:** a hidden route that leads near the enemy base must be
findable *during the match* by a player who explores, and must be counterable
once discovered. Secret does not mean unfair — every shortcut has a tell
(airflow, light, sound) that an alert defender can learn.

**Route discovery is scored.** Being the first player to find and use a hidden
path awards contribution — see [04](04-teamwork-scoring-and-strategies.md).

## The Ascent (Act II → Act III)

The brief: ancient technology activates, underground structures rise upward, the
battlefield transforms again.

**Staging:**

1. **Awakening.** Dormant machinery in the ruins lights up. Gold glyph-blocks
   ignite in sequence along the tunnel walls. Deep mechanical sound builds.
   F.C.S. calls it.
2. **Lift.** Blocks tear free of the cavern floor and **re-stack upward** into
   towers, the world assembling itself as it climbs. Players ride the rising
   structures — again, playable, not a cutscene.
3. **Arrival.** The structures lock into a floating configuration above the
   clouds. Sunlight after ten minutes underground: the visual payoff of the
   match.

## Act III — The Sky Towers

**Fantasy:** the endgame. Nothing below you.

**Contents (from brief):** giant towers, floating platforms, bridges, structures
high above the clouds — a vertical battlefield.

**New challenges (from brief):**

| Challenge | Effect |
|---|---|
| **Moving platforms** | Traversal windows open and close on a timer |
| **Wind currents** | Push players mid-air; can be ridden for distance or fought for control |
| **Changing gravity** | Zones with altered jump height and fall speed |
| **Falling hazards** | Debris from higher structures |
| **Unstable structures** | Platforms that degrade and drop after sustained use |

**Flag relocation.** The brief calls for flags to move to new locations in this
stage. *Proposed:* each flag re-anchors to its team's sky tower — a fixed,
visible, defensible point — and F.C.S. announces the new position for both
teams. Both flags relocate simultaneously and symmetrically. The point is to
force a new plan, not to hide the objective.

**Falling.** Falling off is a **respawn with a timer**, not an elimination —
proposed 8 seconds, respawning at the team tower. A dropped flag falls to the
nearest platform below and returns to base after a timeout if untouched. Sky
combat has to be worth attempting; instant-death falls would make everyone
turtle on solid ground.

**Why Act III is last:** vertical space plus wind plus moving platforms produces
the most chaotic, least predictable fights in the game. That is exactly what the
final four minutes of a 15-minute match should be.

## Transition safety checklist

Every transition must satisfy all of these:

- [ ] Warned by F.C.S. with enough lead time to reposition (≥45s)
- [ ] Telegraphed visually before it fires
- [ ] Playable throughout — no forced camera lock
- [ ] Non-lethal — relocates, never eliminates
- [ ] Carrier keeps the flag
- [ ] Landing zones are spread and briefly protected
- [ ] Score, cooldowns and team assignment all persist
