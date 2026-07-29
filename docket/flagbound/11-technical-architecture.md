# 11 — Technical Architecture (Proposed)

> ⚠️ **This document is inference, not brief.** The source prompt describes an
> experience, not a technology stack. Everything here is a starting proposal to
> be argued with and replaced by whatever the actual team decides. Documents
> 01–10 are the requirements; this one is one possible answer.

## System map

```
┌─────────────────────────────────────────────────────────┐
│  CLIENT                                                  │
│  Rendering · Input · Prediction · UI/HUD · F.C.S. voice   │
└───────────────────────────┬─────────────────────────────┘
                            │ authoritative state
┌───────────────────────────┴─────────────────────────────┐
│  MATCH SERVER (one per match instance)                    │
│  Simulation · Combat · Flag state · Phase Director        │
│  Bot AI · F.C.S. event engine · Chat relay                │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────┐
│  PLATFORM SERVICES                                        │
│  Matchmaking · Accounts · Progression · Moderation ·      │
│  Telemetry · Highlight capture                            │
└─────────────────────────────────────────────────────────┘
```

## Engine

*Proposed:* an off-the-shelf engine with mature networking, large-world
streaming and destruction tooling — Unreal or Unity. The differentiator in
Flagbound is world transformation and AI behaviour, not renderer technology, so
building an engine would spend the budget in exactly the wrong place.

The engine question should be settled by which one the team can move fastest in.

## The Phase Director

The system that owns the match's three acts and two transitions. Server-side,
authoritative, and the heart of the game.

**Responsibilities:**

- Owns the phase clock and broadcasts phase state to all clients
- Fires the warning cascade before each transition
- Coordinates the transition: freeze-safe, relocate players, hand over the new
  world
- Guarantees the carry-over rules from [02](02-match-flow-and-world-phases.md) —
  carriers keep flags, score persists, nobody dies to a transition
- Verifies every client is loaded and simulating the new phase before returning
  control

**Proposed phase state machine:**

```
BRIEFING → ACT_I → TREMORS → COLLAPSE → ACT_II
         → AWAKENING → ASCENT → ACT_III → RESULTS
```

Each transition state has an entry gate (all clients confirmed ready or timed
out to a safe fallback) and an exit gate (all players relocated to valid
positions).

## The biggest technical risk

**Two full world swaps mid-match, live, with no loading screen.**

This is the project's defining engineering problem. If it is solved, the game
works; if the collapse becomes a 20-second loading screen, the central pillar
dies and no other system can compensate.

**Mitigations to plan for from day one:**

1. **Pre-stream aggressively.** Act II geometry loads during Act I; Act III
   during Act II. The transition should be a visibility and simulation handoff,
   not a load.
2. **Budget for three worlds resident at once.** Memory ceiling drives the
   fidelity budget for all three acts. Set this number before art production
   starts, not after.
3. **Prototype the collapse first.** Before combat, before classes, before art —
   build a grey-box vertical slice of surface → collapse → underground with 16
   players. If that does not hold, the design needs to change while it is still
   cheap to change.
4. **Design a graceful fallback.** If a client cannot complete the handoff in
   time, it needs a defined recovery — a short scripted fall sequence covering a
   forced load — rather than a desync or a drop.
5. **Choreograph, don't simulate.** The collapse and ascent should be authored
   destruction with physics flourish, not fully simulated physics. Sixteen
   clients must see the same collapse; only authored motion guarantees that.

## Bot AI

*Proposed:* a **utility-scored behaviour system** over a hierarchical task
layer — bots continuously score candidate roles (attack / defend / escort /
intercept / scout) against match state and switch when the winner changes by
more than a hysteresis margin. That margin is what stops the visible
role-flip-flopping that makes bots look broken.

- Runs server-side, one AI context per match instance
- Navigation meshes are **per-phase**, rebuilt on transition; runtime
  invalidation handles mid-act tunnel collapses
- Bots consume only information their team legitimately possesses — the same
  rule as F.C.S. (see [05](05-fcs-ai-assistant.md))
- Route-pressure tracking implements the brief's adaptation requirement (see
  [06](06-ai-bots.md))
- Performance ceiling: bot AI shares a server tick with 16 players' simulation,
  so the AI budget per instance must be fixed early

## F.C.S. implementation

*Proposed:* a **hybrid** — deterministic where it matters, generative where it
helps.

- **Event-driven callouts** (the bulk of it): an authored rule engine over match
  state, with a priority queue and rate limiting. Deterministic, testable,
  latency-free, and impossible to make say something inappropriate.
- **Player questions:** intent classification against a fixed set of supported
  queries, answered from match state. A language model is optional here, and if
  used it must be constrained to game topics, moderated on output, and never
  given information the player's team has not earned.
- **Voice:** pre-recorded lines for authored callouts (best quality, zero
  latency); synthesis only if the question-answering path needs it.

**Hard constraint:** F.C.S. must never gate gameplay on a network round-trip to
an AI service. A warning that arrives after the collapse is worse than no
warning.

## Moderation pipeline

- **Client-side pre-filter** — instant feedback on obvious violations, low cost
- **Server-side authoritative filter** — the real decision; nothing bypasses it
- **Escalation service** — pattern detection across matches, ladder-state
  tracking, decay
- **Human review queue** — for tier 4/5 and all appeals
- Moderation logs retained per policy, with retention rules that must be set by
  legal review given the under-13 audience

## Build order

A sequencing proposal that puts the risky things first:

| Phase | Deliverable |
|---|---|
| 1 | Grey-box vertical slice: surface → collapse → underground, 16 players, no art, no classes. **Proves or kills the concept.** |
| 2 | Core CTF loop — flags, capture, respawn, score, one class |
| 3 | All four classes and the combat verb set |
| 4 | Bot AI to the behavioural bar in [06](06-ai-bots.md) |
| 5 | Act III and the ascent transition |
| 6 | F.C.S. event engine and callouts |
| 7 | Matchmaking, concurrency, server browser |
| 8 | Chat and the moderation pipeline |
| 9 | Progression, cosmetics, achievements |
| 10 | Art production pass, cinematics, audio, highlight capture |

Phase 1 is not a prototype to skip. Everything else in this docket is
conventional-to-hard; phase 1 is the part nobody has proof of yet.
