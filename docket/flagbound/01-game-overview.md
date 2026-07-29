# 01 — Game Overview

## Pitch

Flagbound: The Shifting Battlefield is a large-scale, online multiplayer
third-person capture-the-flag game. Two teams defend their own flag while
infiltrating the enemy base to steal theirs and carry it home before the
15-minute timer expires.

What separates Flagbound from every other CTF game is that **the map does not
stay still**. A single match runs through three completely different worlds —
a surface battlefield, a hidden underground kingdom, and a sky-tower arena above
the clouds — and the transitions between them happen mid-fight, live, with
players inside them. Every match tells a different story because the ground
literally changes under the players' feet.

## Design pillars

Every feature in this docket should serve at least one of these. A feature that
serves none should be cut.

### 1. The world is a character

The battlefield is not a stage the fight happens on; it is a participant. It
warns, it breaks, it rises. Players should spend the match reacting to it, not
just to each other.

### 2. Adaptation beats memorisation

Map knowledge is valuable, but it expires twice per match. The player who
re-reads the situation fastest wins over the player who has memorised one route.

### 3. Support is not second-class

Escorting a carrier, holding a lane, spotting an ambush, and opening a route are
scored, celebrated, and rewarded on par with eliminations. A team of pure
fraggers should lose to a coordinated team.

### 4. Skill, not spending

Progression is cosmetic and achievement-based. A player on day one can beat a
veteran through better decisions. Nothing in the store touches combat power.

### 5. Safe for a wide audience

The game is built for ages 10 and up. Combat is fantasy-adventure action, not
gore, and communication is actively moderated. A competitive game can still be a
respectful one.

## Visual identity

Flagbound is a **rounded block world** — rolling green ground under a clear sky,
stone walls and towers, trees with rounded canopies, and round big-eyed creatures
rather than armoured soldiers. Familiar and readable, but every mass is a softened
form rather than a hard cube.

Underneath, the world is simulated as a **grid of half-metre cells**, and that is
the load-bearing decision: it is what lets the battlefield genuinely come apart
and re-stack, making the collapse and the ascent *natural* instead of the hardest
thing in the project to build. The grid is the simulation; the rounded look is how
it is drawn.

Full treatment in [10 — Art Direction](10-art-direction-and-cinematics.md).

## Audience

**Primary:** players aged 10+ who want a team game with real strategy and real
spectacle, but not a punishing simulation.

**What that implies for design:**

- Readability over realism — telegraphed attacks, loud visual warnings, clear
  team colours.
- Onboarding carried by F.C.S. (see [05](05-fcs-ai-assistant.md)) rather than by
  a wall of tutorial text.
- Short commitment: 15 minutes is one sitting, one story, one result.
- Violence styled as fantasy-adventure combat — impact, knockdowns and glowing
  ability effects, not injury detail.

## Core loop

```
Queue  →  Pre-match briefing (F.C.S.)  →  Pick class  →
  ACT I   Surface battlefield        (~6 min)   →  COLLAPSE  →
  ACT II  Underground kingdom        (~5 min)   →  ASCENT    →
  ACT III Sky towers                 (~4 min)   →
Match result  →  Contribution breakdown  →  Unlocks  →  Requeue
```

Detailed timings and transition mechanics live in
[02 — Match Flow & World Phases](02-match-flow-and-world-phases.md).

## Win conditions

Evaluated in order:

1. **Captures.** The team with more flag captures at the final whistle wins.
2. **Tiebreak — flag control.** If captures are level, the team holding the
   enemy flag at the whistle wins.
3. **Tiebreak — contribution.** If still level, the team with the higher total
   contribution score (see [04](04-teamwork-scoring-and-strategies.md)) wins.
4. **Draw.** If every tiebreak is level, the match is a draw.

*Proposed:* a capture in progress at the whistle resolves — if the carrier is
within their own base zone when time expires, the capture counts. This exists to
make the final seconds feel like the brief's "final-second flag capture" moment
rather than an anticlimax.

## What a match feels like

- **Minute 1.** F.C.S. briefs the objective. Teams split — some rush, some hold.
- **Minute 4.** First capture attempt. A carrier gets escorted halfway home and
  is dropped at the bridge.
- **Minute 6.** The ground shakes. F.C.S. calls the collapse. The battlefield
  comes apart into thousands of tumbling masses and everyone falls with it.
- **Minute 8.** Underground, standing in the wreckage of their own base. A
  Shadow Runner finds a route straight into the enemy base and the whole
  defensive plan is wrong.
- **Minute 11.** Ancient machinery activates. The ruins start re-stacking upward.
- **Minute 13.** Sky towers. Flags have relocated. Wind pushes a carrier off a
  bridge.
- **Minute 15.** A Swiftblade takes a suicidal shortcut across open sky with the
  flag and lands in the base as the clock hits zero.

That last minute is the clip players share. Every system in this docket exists
to make it happen more often.
