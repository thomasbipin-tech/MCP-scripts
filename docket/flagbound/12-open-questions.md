# 12 — Open Questions

Decisions this docket could not make on its own. Each needs an owner before
production. Grouped by how badly they block work.

## Resolved since v0.1

### ~~Is the no-loading-screen transition achievable?~~ — largely resolved

This was the docket's existential risk: two full world swaps mid-match with no
loading screen.

**The voxel art direction dissolved it.** There are no longer three maps to swap
between — there is one continuous vertical block world, and the transitions are
block operations within it
([11](11-technical-architecture.md#the-voxel-data-model)). What remains is a
*performance* question, not a feasibility one, and it is tracked as questions 10 and 11 below.

## Blocking — needed before phase 1 of the build

### 1. Can players break and place blocks?

**The biggest open design question in the docket, and it did not exist before the
art direction was settled.** A voxel world invites Minecraft's defining verb, and
the answer changes the whole game.

| Option | Consequence |
|---|---|
| **No block editing** | Simplest and safest. The world changes only through authored events. But players *will* try to dig, and a voxel world that refuses to be dug feels broken to anyone who has played Minecraft. |
| **Limited tactical editing** | *Proposed.* Guardians can place a small number of temporary blocks as cover; some soft block types (dirt, thatch, cracked stone) can be broken to open shortcuts; structural stone and base blocks are indestructible. Keeps map integrity while honouring the fantasy. |
| **Full Minecraft-style editing** | Most expressive, and almost certainly breaks the game — teams would wall their flag into an unreachable cube, or tunnel straight to the enemy base in minute one. Would need heavy rules to survive, at which point it is really option 2. |

- **Resolve by:** prototyping option 2 in phase 2 and testing whether a defended
  base is still attackable.
- **Note:** this interacts directly with the four strategies in
  [04](04-teamwork-scoring-and-strategies.md) — block-breaking is a *fifth*
  strategy (dig your own route) that the docket does not currently account for.

### 2. Match size

[07](07-multiplayer-and-servers.md) proposes 8v8 on reasoning, not data. This
number drives map scale, server cost, bot count and the entire art budget, and
it is expensive to change late.

- **Resolve by:** playtesting 6v6, 8v8 and 12v12 in the grey-box slice.

### 3. Engine choice — and voxel middleware vs. custom

Drives tooling, hiring and schedule. The voxel direction narrows it: no
commercial engine ships a production voxel terrain system, so the real question
is whether to extend existing voxel middleware or build the layer in-house
([11](11-technical-architecture.md#engine)).

- **Resolve by:** a technical spike building the phase-0 voxel foundation in the
  two most promising engine + middleware combinations.
- **Watch for:** middleware that handles static voxel worlds beautifully but
  cannot cope with mass runtime destruction. That is exactly the case Flagbound
  needs and exactly the case least likely to be well supported.

## High priority — needed before the systems they touch

### 4. Which route for anime characters — 3D models or 2D art?

[10](10-art-direction-and-cinematics.md#two-ways-to-ship-anime-characters) sets
out both. 3D cel-shaded rigged models are the genre norm and keep facing and
camera freedom intact; authored 2D art on billboards gives truer anime line
quality at a fraction of the cost, but limits angles and makes an opponent's
facing unreadable without an explicit cue.

- **The prototype uses 2D billboards**, because it is the only route that produces
  genuinely anime figures without an art team.
- **Resolve by:** deciding whether competitive facing-readability is negotiable.
  If it is not, Route A is required and should be budgeted early — it drives
  hiring.
- **Owner:** art director plus whoever owns the budget.

### 5. Legal and child-safety framework

The 10+ audience triggers COPPA, GDPR-K and equivalent regimes: age
verification, parental consent, data retention for moderation logs, and rules on
what a minor's account may display or share. [08](08-chat-and-moderation.md)
proposes sensible defaults but explicitly does not attempt the legal work.

- **Owner:** specialist legal counsel. **Must be settled before any beta.**

### 6. Do flags relocate in Act III, and where?

The brief says flags "may move to new locations."
[02](02-match-flow-and-world-phases.md) proposes symmetric relocation to each
team's sky tower, announced to both teams.

- **Alternatives:** flags stay with their existing carriers; flags move to a
  contested neutral position; only one flag relocates.
- **Resolve by:** playtesting Act III. The risk of the proposal is that it
  invalidates a defensive position a team spent five minutes earning.

### 7. Is there a revive/downed state?

[04](04-teamwork-scoring-and-strategies.md) scores revives conditionally. A
downed state would strongly reinforce the teamwork pillar but adds significant
combat complexity and lengthens fights.

- **Resolve by:** prototyping in phase 3.

### 8. F.C.S. — generative or fully authored?

Authored is safe, fast, testable and cheap. Generative answers the brief's
"players can ask questions" requirement more flexibly but adds latency, cost,
moderation surface and the risk of leaking information the player has not
earned.

- **Proposal on the table:** hybrid, per [11](11-technical-architecture.md).
- **Resolve by:** prototyping the question-answering path and measuring whether
  players actually ask open-ended questions or converge on a handful of intents.

### 9. Are unlockable abilities worth the balance risk?

[09](09-progression-and-rewards.md) resolves the brief's "new abilities" as
strict sidegrades. That is defensible but expensive — every new ability needs
full balance work against the starter kit forever.

- **Alternative:** cosmetics-only progression, with the ability roster fixed and
  free. Simpler, safer, and arguably a better fit for the fairness pillar.
- **Owner:** design lead.

### 10. What is the debris budget on minimum spec?

The collapse's impact scales with how many blocks visibly fall, and tens of
thousands of simulated cubes will not hold frame rate on low-end hardware
([11](11-technical-architecture.md#risk-2--physics-and-memory-cost-of-the-spectacle)).

- **Proposed:** 5,000 concurrent debris blocks, scaled down by graphics setting.
- **Must be measured on the lowest target spec before art production commits to
  a block count.** A collapse that only impresses on expensive hardware defeats
  the point of choosing a cheap-to-render style.

### 11. Does seeded client-side debris look identical enough?

The netcode plan replicates a region diff and lets each client simulate its own
debris from a shared seed
([11](11-technical-architecture.md#risk-1--replicating-mass-destruction-to-16-clients)).
In theory divergence is invisible because debris has no gameplay effect. In
practice, two players describing the same collapse differently would undercut the
shared-moment quality the brief is asking for.

- **Resolve by:** side-by-side capture of the same collapse on 16 clients in
  phase 1.

## Medium priority

### 12. Platforms

Not specified in the brief. PC, console, mobile? Cross-play? This affects
control scheme, performance budget and the F.C.S. voice input design (push-to-
talk assumes a mic that mobile players may not want to use).

### 13. Are the four classes enough?

Four covers the strategy space in [04](04-teamwork-scoring-and-strategies.md)
cleanly. A fifth introduced later is a good live-ops beat, but only if the
counterplay matrix in [03](03-combat-and-classes.md) survives it.

### 14. Map variety

The brief describes one three-act sequence. Do all matches run the same three
worlds? Same worlds with varied layouts? Multiple act sequences that shuffle?

- **Consideration:** "every match tells a different story" is currently carried
  entirely by player action, not by map variation. That may be enough for
  launch; it is unlikely to be enough for year two.

### 15. Ranked / competitive mode

Not mentioned in the brief. Given the strategy focus and the 15-minute format,
there is an obvious competitive audience — but ranked play sharpens every
balance flaw and demands stricter matchmaking than the "under 30 seconds to a
match" priority in [07](07-multiplayer-and-servers.md) allows.

### 16. Spectating and replays

[10](10-art-direction-and-cinematics.md) proposes automatic highlight capture.
Full spectating and replay would extend that, and would help the shareability
goal, but is not in the brief.

## Low priority — post-launch questions

- Custom/private matches for friend groups
- Community map or mode tools
- Seasonal live-ops structure
- Esports or organised competitive support
- Additional acts — a fourth world beyond the sky towers

## Numbers awaiting playtest data

Every value below is a *proposal* in this docket and should be treated as
provisional until measured:

| Value | Proposed | Source doc |
|---|---|---|
| Structural block size | 0.5 m | 10 |
| Detail voxel size | 0.125 m | 10 |
| Chunk size | 32³ blocks | 11 |
| Concurrent debris cap | 5,000 | 11 |
| Match length | 15 min (fixed by brief) | 02 |
| Act I / II / III split | 5 / 4 / 3.25 min | 02 |
| Team size | 8v8 | 07 |
| Respawn timer | 8s | 03 |
| Dropped flag return | 20s | 03 |
| F.C.S. callout floor | 1 per 8s | 05 |
| Bot chat rate limit | 1 per bot per 15s | 06 |
| Join-in-progress cutoff | 11:00 | 07 |
| Chat mute duration | 24h / 7d | 08 |
| Suspension length | 7 days (from brief) | 08 |
| Violation decay | 90 days clean | 08 |
| Contribution point values | see table | 04 |
