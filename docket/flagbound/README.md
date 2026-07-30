# 🏴 Flagbound: The Shifting Battlefield — Design Docket

> **Status:** Design docket, plus a **playable prototype** in
> [`prototype/`](prototype/) — open `index.html` in any browser. The prototype
> covers Act I, the collapse and Act II; everything else here is specification.
> **Scope of this folder:** the full design specification for Flagbound. Nothing in
> here is wired into the AI Music Studio app that lives in the rest of this
> repository; this is a standalone dossier.

## At a glance

| Field | Value |
|---|---|
| **Title** | Flagbound: The Shifting Battlefield |
| **Genre** | Online multiplayer action strategy capture-the-flag |
| **Camera** | Third-person, with an optional first-person mode |
| **Match length** | ~15 minutes |
| **Players** | Real players, backfilled by intelligent AI bots |
| **Target audience** | Ages 10+ |
| **Art style** | Cel-shaded — square figures on a soft stylised battlefield that comes apart and rebuilds |
| **Main goal** | Steal the enemy flag and return it to your base while the battlefield transforms underneath you |

## The one-line pitch

Two teams fight for each other's flags on a battlefield that refuses to hold
still — it collapses into an underground kingdom, then launches into the sky —
so no strategy survives the whole match.

## Core features

- **Cel-shaded look** — hard shadow bands, ink silhouettes, rim light; square
  figures against a rounded world so players separate from terrain at a glance
- **Reboot pads** in opposite corners — dying costs you position, not just seconds
- **Disintegration on defeat** — no bodies, and it reads from across the map
- Dynamic transforming world (surface → underground → sky), three acts per match
- Skill-based action combat: attack, block, dodge, sprint, jump
- **Skills worth pressing** — dash, glide, grapple, ground slam, barriers, stealth,
  decoys, and ultimates that charge from *support* play as fast as from fighting
- Four classes — Guardian, Swiftblade, Element Warrior, Shadow Runner
- Teamwork-first scoring: support play is worth as much as eliminations
- **F.C.S.** — a talking AI companion that briefs, warns, and advises every player
- Objective-aware AI bots that fill empty slots and play like real teammates
- Concurrent multiplayer servers hosting many simultaneous matches
- Moderated team chat with graduated consequences
- Cosmetic-only progression — no purchasable competitive advantage

## Documents in this docket

| # | Document | Covers |
|---|---|---|
| 01 | [Game Overview](01-game-overview.md) | Pitch, pillars, audience, win conditions |
| 02 | [Match Flow & World Phases](02-match-flow-and-world-phases.md) | The 15-minute arc, the three acts, transition events |
| 03 | [Combat & Classes](03-combat-and-classes.md) | Verbs, damage model, the four classes, counterplay |
| 04 | [Teamwork, Scoring & Strategies](04-teamwork-scoring-and-strategies.md) | Contribution scoring, the four team strategies |
| 05 | [F.C.S. — Flagbound Command System](05-fcs-ai-assistant.md) | The AI companion: voice, text, triggers, guardrails |
| 06 | [AI Bots](06-ai-bots.md) | Bot behaviour, backfill rules, adaptation |
| 07 | [Multiplayer & Servers](07-multiplayer-and-servers.md) | Match hosting, matchmaking, concurrency |
| 08 | [Chat & Moderation](08-chat-and-moderation.md) | Communication tools and the safety ladder |
| 09 | [Progression & Rewards](09-progression-and-rewards.md) | Unlocks, fairness rules, what is never sold |
| 10 | [Art Direction & Cinematics](10-art-direction-and-cinematics.md) | Visual style, the shareable moments |
| 11 | [Technical Architecture](11-technical-architecture.md) | Proposed systems to build this — *inferred, not from brief* |
| 12 | [Open Questions](12-open-questions.md) | Decisions still owed before production |
| 13 | [Abilities & Skills](13-abilities-and-skills.md) | The full skill roster, ultimates, and what was rejected |

## How to read this docket

Documents **01–10** and **13** are a direct expansion of the source brief; every
design statement in them traces back to something the brief asked for. **Numbers are
proposals** where the brief did not give one — phase timings, cooldowns,
scoring values and suspension lengths are all marked as *proposed* and are meant
to be tuned in playtesting.

Document **11** is different: the brief describes an experience, not a stack, so
the architecture is an inference about how to deliver it. Treat it as a starting
proposal to argue with, not a decision.

Document **12** lists the questions this docket could not answer on its own.
