# 07 — Multiplayer & Servers

## Requirement

From the brief: the game supports multiplayer servers where **multiple matches
happen at the same time**, allowing players to enter different battles and join
available games. Human players are backfilled by bots so matches always feel
full.

## Match size

*Proposed:* **8v8**. The brief asks for a "large-scale" battlefield with two
bases, multiple routes and four distinct strategies.

Reasoning: below 6v6, splitting into attack and defence leaves both too thin for
the four strategies in [04](04-teamwork-scoring-and-strategies.md) to be
distinguishable. Above 12v12, the transition events become chaotic in a way that
loses the individual player's story. 8v8 lets a team run 3 attack / 3 defence /
2 flex and still have every role occupied.

This number should be validated in playtest and is the most likely thing in this
docket to change.

## Server model

*Proposed:* **authoritative dedicated servers**, one match instance per server
process, many instances per host.

Non-negotiable reasons for server authority here:

- Flag possession, captures and score must not be client-trusted.
- The phase transitions are global, timed world events — every client must agree
  on exactly when the ground breaks.
- Bot AI runs server-side so bots exist consistently for all players.
- Peer-hosted matches would hand one player the ability to stall a transition.

## Session lifecycle

```
Player queues
  → Matchmaker assigns to an instance (existing with space, or new)
  → Instance reserves slot, retires a bot if one holds it
  → Briefing phase (45s) — class select, F.C.S. brief
  → Match runs 15 min through three phases
  → Results, contribution breakdown, progression awards
  → Instance tears down or recycles to a fresh match
```

## Matchmaking

**Priorities, in order:**

1. **Speed to a match.** Bot backfill means a player never waits for a full
   lobby. Target queue time under 30 seconds.
2. **Region / latency.** Route to the nearest healthy region.
3. **Skill proximity.** Loose brackets — tight brackets fight priority 1.
4. **Human density.** Prefer instances with more humans when the other factors
   are equal, so bots dilute the experience as little as possible.

**Join-in-progress:** allowed, *proposed:* until the ~11-minute mark. Joining
during Act III with four minutes left and no idea what happened is a bad first
impression. Late joiners take a bot's slot and get an abbreviated F.C.S. catch-up
brief ("we're down one capture, our flag is safe, sky phase in 30 seconds").

## Concurrency

- Many independent match instances run simultaneously per region.
- A server browser / match list lets players see and join available battles —
  the brief's "enter different battles" requirement.
- Instances are isolated: one match's transition, load or crash cannot affect
  another.
- *Proposed:* instances scale elastically with regional queue depth, and idle
  instances are reclaimed.

## Netcode considerations

The phase transitions are the hard part of this game technically. Notes:

- **World state versioning.** Each phase is a distinct world; clients must
  confirm they are loaded and simulating the correct phase before the server
  hands them control.
- **Pre-streaming.** The next phase's geometry should stream in during the
  preceding act so a transition never becomes a loading screen. This is the
  single biggest technical risk in the project — see
  [11](11-technical-architecture.md).
- **Transition tolerance.** During a transition, treat the world as
  server-authoritative and reduce client prediction; a mispredicted collapse is
  far worse than a slightly floaty fall.
- **Reconnection.** A player who disconnects can rejoin the same instance and
  reclaim their slot from the bot that took it, for the remainder of the match.

## Fairness and integrity

- All gameplay-relevant state is server-authoritative.
- Server-side validation of movement and damage; no client-reported hits.
- Rate limits on chat, pings and F.C.S. queries.
- Leaver handling: bots backfill immediately; *proposed:* repeated early leaving
  carries a matchmaking cooldown, but a single disconnect is never punished —
  the audience includes kids on home Wi-Fi.
