# 13 — Abilities & Skills

The skills players actually want to press. This document is the roster; the
class identities it serves are in [03](03-combat-and-classes.md).

## Rules every ability obeys

These are not style guidance. An ability that breaks one of them is cut,
regardless of how good it feels.

1. **Answerable.** Every ability has a counter — a dodge window, a cooldown to
   bait, a position to deny. Nothing is unconditionally correct to press.
2. **A sidegrade, never an upgrade.** Unlocked abilities are alternatives on an
   equal power budget, never stronger versions of the starter kit
   ([09](09-progression-and-rewards.md)). This is the fairness pillar and it is
   non-negotiable.
3. **No carrier may become uncatchable.** Any mobility skill that guarantees a
   flag run is broken. Carriers move slower and mobility skills are weaker while
   carrying.
4. **No base may become unreachable.** Barriers are temporary, breakable, or
   bypassable. A team must never be able to seal its flag away.
5. **Support skills earn as much as kill skills.** Shields, pulls and reveals all
   generate contribution ([04](04-teamwork-scoring-and-strategies.md)).
6. **Legible to a 10-year-old.** Loud wind-up, obvious effect, clear ownership.

## The universal kit

Available to every class, unlocked from the first match. These define how the
game *feels* to move in, so nobody is excluded from them.

| Skill | Key | What it does | Cooldown | Why it lands | Counterplay |
|---|---|---|---|---|---|
| **Dash** ✅ | Q | Burst along your facing direction, with brief invulnerability | 4s | The most reliably loved movement verb in any action game. Escape, engage, or cross a gap. | Short range; the i-frames are shorter than the animation, so a tracking attack still connects |
| **Glide** ✅ | Hold Space while falling | Slows your descent to a drift | — | Turns every fall into a decision. Essential in a game whose ground disappears twice. | No horizontal thrust; a gliding player is a slow, obvious target |

✅ = playable in the [prototype](prototype/).

**Why these two are universal and not class-locked:** the collapse and the ascent
drop every player into free-fall regardless of class. A player without a fall
answer would simply be punished for their class choice by a scripted event, which
is unfair in a way no balance pass can fix.

## Class signature skills

Three per class. The crowd-pleasers are distributed so that no single class holds
all the fun.

### 🛡️ Guardian — defence

| Skill | What it does | Cooldown | Why it lands | Counterplay |
|---|---|---|---|---|
| **Ground Slam** ✅ | Leap, then come down hard — a shockwave knocks nearby enemies back and out | 9s | Physical, loud, and clears a contested flag instantly. Pressing it while standing leaps first, so it never silently fails. | Long airborne wind-up telegraphs it; scatter and it hits nobody |
| **Bulwark** | Plant a temporary barrier that blocks movement and projectiles | 14s | Turning a corridor into a wall is the defensive fantasy | Breakable, timed, and can be walked around; wastes itself if placed early |
| **Chain Hook** | Fire a hook that drags one enemy toward you | 12s | Pulling an escaping carrier back into your team is the single most satisfying save in the game | Single target, slow projectile, and it puts the enemy *next to you* — a mistake against a Swiftblade |

### ⚔️ Swiftblade — speed & capture

| Skill | What it does | Cooldown | Why it lands | Counterplay |
|---|---|---|---|---|
| **Grapple Hook** ✅ | Fires at whatever you are looking at and reels you to it | 6.5s | Verticality on demand. Players will use it for fun long before they use it tactically. | Needs a surface, telegraphs your destination, and leaves you predictable mid-flight |
| **Wall Run** | Run along a vertical surface for a few seconds | 8s | Opens routes nobody is watching | Exposed the whole time, no attacking while running |
| **Afterimage** | Leave a marker; press again within 6s to snap back to it | 16s | Dive in, grab the flag, and rewind out — the highest-skill-ceiling skill in the roster | The marker is visible to enemies, so a good defender simply waits on it |

### 🔥 Element Warrior — area control

| Skill | What it does | Cooldown | Why it lands | Counterplay |
|---|---|---|---|---|
| **Firewall** | A line of flame that denies ground over time | 11s | Deciding where the fight *cannot* happen | Does not block sight or projectiles; a Guardian simply walks through it |
| **Ice Wall** | Raises a wall of ice cells from the ground | 13s | Instant terrain authorship — a beloved trick in every game that has it | Breakable, and it blocks your own team too. Depends on the block-editing decision in [12](12-open-questions.md) (Q1) |
| **Updraft** | A column of wind that launches anyone in it upward | 10s | Launching a teammate onto an enemy tower is pure highlight material | Launches enemies too, and a launched player is helpless in the air |

### 🌑 Shadow Runner — stealth & disruption

| Skill | What it does | Cooldown | Why it lands | Counterplay |
|---|---|---|---|---|
| **Vanish** | Temporary invisibility; breaks on attacking or taking the flag | 15s | Walking past an entire defence is a story players retell | Faint shimmer at close range; area abilities reveal it; picking up the flag cancels it outright |
| **Decoy** | A copy of you that runs a route and draws attention | 12s | Watching a whole defence chase nothing is the best joke in the game | Bots learn to ignore repeated decoys; it deals no damage |
| **Mark** | Reveals enemy positions in an area to your whole team | 10s | Pure information — and it scores contribution, so support play is visibly rewarded | Reveals your own position when cast |

## Ultimates

*Proposed:* one per class, charged during the match — and here is the important
part:

> **Ultimates charge from contribution score, not from eliminations.**

Escorting a carrier, holding a base and returning a flag charge your ultimate
exactly as fast as fighting does. This makes the docket's central pillar —
*support is not second-class* ([04](04-teamwork-scoring-and-strategies.md)) —
something the player feels in their hands rather than reads on a results screen.

| Class | Ultimate | Effect |
|---|---|---|
| **Guardian** | **Bastion** | A large dome around your flag that blocks enemies for ~8s |
| **Swiftblade** | **Slipstream** | Your whole team gains large speed and full carry speed for ~6s — the escort payoff |
| **Element Warrior** | **Singularity** | Pulls every nearby enemy toward one point for ~2s |
| **Shadow Runner** | **Nightfall** | Your whole team turns briefly invisible — a coordinated push out of nowhere |

Every ultimate is **team-facing or area-facing, never a solo execute.** None of
them wins a fight alone; all of them make a *plan* work.

## Skills tuned per act

The three worlds change which skills matter, which is what keeps the adaptation
pillar alive across a match:

| Act | Skills that shine | Skills that struggle |
|---|---|---|
| **Dreamfield** (open ground) | Dash, Grapple, Firewall | Bulwark — too much open space to wall off |
| **The Deep** (tight routes) | Bulwark, Ice Wall, Vanish, Decoy | Glide, Updraft — low ceilings |
| **Sky Towers** (vertical) | Glide, Updraft, Grapple, Chain Hook | Vanish — nowhere to hide in open sky |

A player who never changes class still has a match that shifts under them,
because the same kit is strong, then awkward, then strong again.

## Deliberately rejected

Recorded so they do not get re-proposed:

| Idea | Why not |
|---|---|
| **Time stop / slow** | Cannot be reconciled with authoritative multiplayer, and a stopped clock breaks the phase timer the whole game is built on |
| **Free flight** | Destroys the sky act's tension and makes carriers uncatchable (rule 3) |
| **Teleport to own base** | An instant capture. Removes the entire return trip, which is where the game's best moments happen |
| **Team-wide revive** | Erases the cost of a lost fight and turns the last minute into a stalemate |
| **Permanent structures** | A team would seal its flag away (rule 4) |
| **Purchasable ability slots** | Violates the fairness pillar ([09](09-progression-and-rewards.md)) outright |

## What playtesting must check

- [ ] No ability has above-average pick rate *and* above-average win rate
- [ ] Every unlocked sidegrade sits within a few points of its starter equivalent
- [ ] No mobility skill lets a carrier outrun every counter
- [ ] Ultimate charge rates are genuinely equal between support and combat play —
      measured, not assumed
- [ ] A new player using only the universal kit can still win a match
