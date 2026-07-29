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

*Proposed:* an off-the-shelf engine with mature networking and large-world
streaming — Unreal or Unity — with a **custom voxel layer** on top.

The voxel art direction ([10](10-art-direction-and-cinematics.md)) changes this
calculation. Off-the-shelf engines do not ship a production-grade voxel terrain
system, so this is the one place a custom subsystem is unavoidable. Options, in
order of preference:

1. **Existing voxel plugin/middleware** on Unreal or Unity, extended. Fastest
   path; the risk is hitting the plugin's ceiling on the transitions and having
   to fork it anyway.
2. **Custom voxel layer** inside a commercial engine, using it for rendering,
   networking, audio and tooling. Most likely the correct answer.
3. **Fully custom engine.** Almost certainly wrong — it spends the budget on
   solved problems instead of on the world transformation and AI that actually
   differentiate the game.

The engine question should be settled by which combination the team can build the
phase-1 slice in fastest.

## The voxel data model

The single most important architectural decision in the project, because
everything else — transitions, netcode, bot navigation, memory — falls out of it.

*Proposed:* **one continuous vertical voxel world**, not three maps.

```
   ┌──────────────────────┐  y = +400   Act III   sky towers
   │      (open sky)       │
   ├──────────────────────┤  y =    0   Act I     surface battlefield
   │       (bedrock)       │
   ├──────────────────────┤  y = -300   Act II    underground kingdom
   └──────────────────────┘  y = -400
```

All three acts are regions of the **same block grid**, stacked vertically. This
is the payoff the art direction promised: there is no world swap, no second map
to load, no handoff to get wrong. The Collapse deletes and drops blocks between
y=0 and y=-300; the Ascent lifts blocks from y=-300 to y=+400. The brief's
requirement that the underground *"feel like a continuation of the same
battle"* stops being an illusion to maintain and becomes a fact about the data.

**Two distinct kinds of block, and the distinction is critical:**

| Kind | Authority | Count | Purpose |
|---|---|---|---|
| **World blocks** | Server-authoritative, in the grid | Millions | Collision, gameplay, structure |
| **Debris blocks** | Client-side visual only | Thousands, transient | The spectacle of the collapse |

A block that detaches during a transition is **removed from the authoritative
grid and spawned as client-side debris**. Debris has no gameplay effect — it
cannot block, damage, or be landed on. This is what makes the collapse
affordable: the server replicates *"these regions are now empty"*, not the
trajectory of 40,000 individual cubes.

## Chunking and streaming

- World divided into chunks (*proposed:* 32³ blocks) with per-chunk meshes
- Clients stream chunks by proximity plus phase relevance
- **Act III geometry does not exist until the Ascent builds it**, so it costs
  nothing to hold during Acts I and II
- Only Act I's surface region can be freed after the Collapse — *proposed:* keep
  it, since a visible ruined surface above the cavern is a strong visual and a
  cheap one once its collision is stripped

## The Phase Director

The system that owns the match's three acts and two transitions. Server-side,
authoritative, and the heart of the game.

**Responsibilities:**

- Owns the phase clock and broadcasts phase state to all clients
- Fires the warning cascade before each transition
- Executes the authoritative block operations for each transition
- Guarantees the carry-over rules from [02](02-match-flow-and-world-phases.md) —
  carriers keep flags, score persists, nobody dies to a transition
- Relocates players to valid landing positions and applies the spawn-protection
  window

**Proposed phase state machine:**

```
BRIEFING → ACT_I → TREMORS → COLLAPSE → ACT_II
         → AWAKENING → ASCENT → ACT_III → RESULTS
```

Each transition state has an entry gate (all clients confirmed at the correct
world version, or timed out to a safe fallback) and an exit gate (all players in
valid positions on solid blocks).

## Technical risks

Going voxel **retired the project's original defining risk** — two full world
swaps mid-match with no loading screen. There is now one continuous block world
and nothing to swap. That was the risk most likely to kill the concept, and the
art direction dissolved it.

Three real risks remain. None of them threatens the concept the way the original
one did, but all three need answers in phase 1.

### Risk 1 — Replicating mass destruction to 16 clients

Forty thousand blocks falling at once cannot be replicated per-block. Bandwidth
does not allow it, and it does not need to.

**Mitigation — split authority from spectacle:**

- The server replicates a compact **region diff**: "blocks in this volume are now
  removed." Bounded, small, cheap.
- Each client spawns its own **debris** from that diff, driven by a
  **server-provided seed** so all 16 clients see a visually near-identical
  collapse without a byte of per-block traffic.
- Debris is cosmetic. Divergence between clients is invisible because debris
  never touches gameplay.
- Only **player positions and the authoritative grid** are synchronised.

The rule: *the collapse the players see is client-simulated; the collapse that
matters is a server region diff.*

### Risk 2 — Physics and memory cost of the spectacle

Tens of thousands of simultaneously simulated rigid bodies will not hold frame
rate on a mid-range machine, let alone a console.

**Mitigations:**

- Hard cap on live debris (*proposed:* 5,000 concurrent, LRU-retired) with
  density scaled by graphics settings — a low-end machine sees a thinner collapse,
  not a slower one
- Debris uses simplified non-interacting physics, not full rigid-body collision
- Aggressive lifetime culling: debris fades once it leaves view or lands
- Distant destruction plays as pre-baked chunk animation rather than per-block
  simulation

**This must be measured on the lowest target spec before art production commits
to a block count.** Getting this wrong is not a crash; it is a game that only
looks impressive on expensive hardware, which contradicts the whole point of
choosing a cheap-to-render art style.

### Risk 3 — Bot navigation on a world that keeps changing

Bots need to path through a voxel world that rearranges twice per match, plus
tunnels that collapse mid-act ([02](02-match-flow-and-world-phases.md)). A
conventional baked navmesh cannot survive that.

**Mitigation:** *proposed:* **voxel-native pathfinding** — path directly over the
block grid with a chunk-level coarse graph for long routes and block-level
detail locally. Chunks mark themselves dirty when their blocks change and only
those chunks re-cost. No global rebuild, so a tunnel collapsing at minute 8
invalidates a handful of chunks rather than the whole map.

This is also the cleanest way to satisfy the brief's requirement that bots
*"react to changing environments."*

### Still true: prototype the collapse first

Before combat, before classes, before art — build a grey-box slice of
surface → collapse → underground with 16 players and measure bandwidth, frame
time on minimum spec, and bot pathing across the transition. The concept risk is
gone; the *performance* risk is not, and it is far cheaper to learn in week 4
than in year 2.

## Bot AI

*Proposed:* a **utility-scored behaviour system** over a hierarchical task
layer — bots continuously score candidate roles (attack / defend / escort /
intercept / scout) against match state and switch when the winner changes by
more than a hysteresis margin. That margin is what stops the visible
role-flip-flopping that makes bots look broken.

- Runs server-side, one AI context per match instance
- **Voxel-native pathfinding** over the block grid, with per-chunk dirty-marking
  so changed blocks re-cost only their own chunks (see Risk 3 above)
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
| 0 | **Voxel foundation** — block grid, chunking, streaming, meshing, collision. Everything else sits on this. |
| 1 | **Collapse slice** — surface → collapse → underground, 16 players, untextured blocks. Measures bandwidth, min-spec frame time, bot pathing across the transition. |
| 2 | Core CTF loop — flags, capture, respawn, score, one class |
| 3 | All four classes and the combat verb set |
| 4 | Bot AI to the behavioural bar in [06](06-ai-bots.md), on voxel pathing |
| 5 | Act III and the ascent (block re-stacking) |
| 6 | F.C.S. event engine and callouts |
| 7 | Matchmaking, concurrency, server browser |
| 8 | Chat and the moderation pipeline |
| 9 | Progression, cosmetics, achievements |
| 10 | Art pass — block palettes, lighting, animation, audio, highlight capture |

Phases 0 and 1 are not prototypes to skip. Everything after them is
conventional-to-hard; the voxel foundation and the collapse are the parts nobody
has proof of yet.

**The good news about this ordering:** phase 0 is a well-understood problem with
prior art and available middleware, and phase 1 is now a *performance*
investigation rather than an existential one. Before the art direction was
settled, phase 1 could have ended the project. It no longer can.
