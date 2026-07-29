# 12 — Open Questions

Decisions this docket could not make on its own. Each needs an owner before
production. Grouped by how badly they block work.

## Blocking — needed before phase 1 of the build

### 1. Is the no-loading-screen transition achievable?

The entire concept rests on it. Two full world swaps mid-match with 16 players
and no loading screen is unproven at this scale.

- **Resolve by:** building the grey-box vertical slice
  ([11](11-technical-architecture.md), phase 1).
- **If the answer is no:** the fallback is a short, authored, *playable* fall
  sequence that masks a load. If even that fails, the three-act structure needs
  rethinking — better to learn that in week 4 than year 2.

### 2. Match size

[07](07-multiplayer-and-servers.md) proposes 8v8 on reasoning, not data. This
number drives map scale, server cost, bot count and the entire art budget, and
it is expensive to change late.

- **Resolve by:** playtesting 6v6, 8v8 and 12v12 in the grey-box slice.

### 3. Engine choice

Drives tooling, hiring and schedule.

- **Resolve by:** a technical spike on the transition problem in the two
  candidate engines.

## High priority — needed before the systems they touch

### 4. Legal and child-safety framework

The 10+ audience triggers COPPA, GDPR-K and equivalent regimes: age
verification, parental consent, data retention for moderation logs, and rules on
what a minor's account may display or share. [08](08-chat-and-moderation.md)
proposes sensible defaults but explicitly does not attempt the legal work.

- **Owner:** specialist legal counsel. **Must be settled before any beta.**

### 5. Do flags relocate in Act III, and where?

The brief says flags "may move to new locations."
[02](02-match-flow-and-world-phases.md) proposes symmetric relocation to each
team's sky tower, announced to both teams.

- **Alternatives:** flags stay with their existing carriers; flags move to a
  contested neutral position; only one flag relocates.
- **Resolve by:** playtesting Act III. The risk of the proposal is that it
  invalidates a defensive position a team spent five minutes earning.

### 6. Is there a revive/downed state?

[04](04-teamwork-scoring-and-strategies.md) scores revives conditionally. A
downed state would strongly reinforce the teamwork pillar but adds significant
combat complexity and lengthens fights.

- **Resolve by:** prototyping in phase 3.

### 7. F.C.S. — generative or fully authored?

Authored is safe, fast, testable and cheap. Generative answers the brief's
"players can ask questions" requirement more flexibly but adds latency, cost,
moderation surface and the risk of leaking information the player has not
earned.

- **Proposal on the table:** hybrid, per [11](11-technical-architecture.md).
- **Resolve by:** prototyping the question-answering path and measuring whether
  players actually ask open-ended questions or converge on a handful of intents.

### 8. Are unlockable abilities worth the balance risk?

[09](09-progression-and-rewards.md) resolves the brief's "new abilities" as
strict sidegrades. That is defensible but expensive — every new ability needs
full balance work against the starter kit forever.

- **Alternative:** cosmetics-only progression, with the ability roster fixed and
  free. Simpler, safer, and arguably a better fit for the fairness pillar.
- **Owner:** design lead.

## Medium priority

### 9. Platforms

Not specified in the brief. PC, console, mobile? Cross-play? This affects
control scheme, performance budget and the F.C.S. voice input design (push-to-
talk assumes a mic that mobile players may not want to use).

### 10. Are the four classes enough?

Four covers the strategy space in [04](04-teamwork-scoring-and-strategies.md)
cleanly. A fifth introduced later is a good live-ops beat, but only if the
counterplay matrix in [03](03-combat-and-classes.md) survives it.

### 11. Map variety

The brief describes one three-act sequence. Do all matches run the same three
worlds? Same worlds with varied layouts? Multiple act sequences that shuffle?

- **Consideration:** "every match tells a different story" is currently carried
  entirely by player action, not by map variation. That may be enough for
  launch; it is unlikely to be enough for year two.

### 12. Ranked / competitive mode

Not mentioned in the brief. Given the strategy focus and the 15-minute format,
there is an obvious competitive audience — but ranked play sharpens every
balance flaw and demands stricter matchmaking than the "under 30 seconds to a
match" priority in [07](07-multiplayer-and-servers.md) allows.

### 13. Spectating and replays

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
