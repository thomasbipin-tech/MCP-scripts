# 06 — AI Bots

## Purpose

From the brief: if there are not enough human players, intelligent AI bots
automatically fill empty team positions **so matches always feel active and
competitive**.

The bar is explicit: bots must **not simply walk around randomly**. They
understand objectives, defend flags, attack enemies, communicate strategies,
follow team plans, and react to changing environments.

## Backfill rules

- Bots fill empty slots at match start and when a player leaves mid-match.
- Both teams stay numerically equal at all times. A bot joins the short side
  immediately.
- If a human joins mid-match, they take over a bot's slot — the bot retires,
  and *proposed:* the human inherits the bot's position and class so the team
  shape is not disrupted mid-fight.
- Bots deliberately fill **composition gaps** (see
  [03](03-combat-and-classes.md)) — a team of four Swiftblades gets a Guardian
  bot, not a fifth Swiftblade.

## Behaviour requirements

### Objective awareness

Bots play capture-the-flag, not deathmatch. A bot must be able to:

- Decide between attacking, defending, escorting and intercepting based on
  current score, flag state and how many teammates are already doing each
- Break off from a winnable fight to chase an enemy carrier
- Escort a *human* carrier home rather than run its own flag attempt
- Return a dropped friendly flag instead of pursuing an elimination

**Bots should be biased toward support roles.** A bot that reliably escorts,
holds a lane and returns flags makes a human's match better. A bot that
out-fights everyone makes it worse.

### Role behaviour

| Role | What the bot does |
|---|---|
| **Defender** | Holds base zone, watches the most-used enemy approach, calls incoming |
| **Attacker** | Pushes toward the enemy flag, prefers routes with friendly presence |
| **Escort** | Stays within range of the friendly carrier, intercepts pursuit |
| **Interceptor** | Hunts the enemy carrier specifically |
| **Scout** | Probes routes, reports contacts, does not overcommit |

### Communication

Bots speak through the team communication system — the brief requires it. They
warn about enemy attacks, suggest routes, and coordinate attacks:

- "Enemies coming through the east bridge."
- "Their flag is unguarded — pushing now."
- "I'll hold the base, go."
- "Carrier's down near the river."
- "Collapse in thirty. Get off the walls."

**Constraints:** bot chat is templated and pre-authored, so it is inherently safe
and cannot be a moderation surface. It is rate-limited (*proposed:* max one line
per bot per 15s, and a team-wide cap) so a bot-heavy team does not spam the
channel. Bot lines are visually tagged as bot-authored — the player should never
be deceived about who they are talking to.

### Reacting to the changing environment

Bots must handle the phase transitions as first-class events:

- **Before a transition:** stop committing to long routes that are about to stop
  existing; move away from fracture lines.
- **On landing/arrival:** re-plan from scratch. Cached Act I routes are invalid
  in Act II.
- **In Act II:** use and defend hidden routes once the team has discovered them.
  *Bots do not know undiscovered secrets* — same rule as F.C.S. A bot may
  "discover" a route by exploring, on a delay that makes it look like
  exploration.
- **In Act III:** respect wind, gravity zones, moving-platform timings and
  ledges. A bot that walks off a sky bridge is the single most immersion-breaking
  failure available in this game.

### Adaptation

From the brief: *if the enemy team constantly attacks through one route, bots
should recognise this and adjust their defence.*

**Proposed mechanism — route pressure tracking.** The team AI keeps a rolling
count of enemy incursions per route over a sliding window. When one route's
share crosses a threshold, defensive bots reweight toward it and announce the
change ("they keep coming through the west — I'm moving there"). The signal
decays, so the enemy can bait the adjustment and then switch routes. That
counterplay is the point: adaptation the player can manipulate is more
interesting than adaptation they cannot see.

Other adaptations: switching to all-out attack when behind late; turtling when
ahead in the final minute; focusing a player who is repeatedly carrying.

## Difficulty

*Proposed:* bots scale to the lobby's average skill, tuned by **reaction time,
aim precision and decision quality** — never by giving bots extra health,
damage, or information the team has not earned. Stat-cheating bots are
detectable and resented; slower-thinking bots just feel like weaker players.

Floor and ceiling both matter. A bot in a beginner lobby must be beatable by a
10-year-old on their first match. A bot in a high lobby must not be free
contribution points.

## Failure modes to test for

- [ ] Bots bunching on one objective and leaving another empty
- [ ] Bots walking off sky ledges or into lava
- [ ] Bots pathing into collapsed/closed tunnels
- [ ] Bots ignoring a friendly carrier who needs escort
- [ ] Bot chat drowning out human chat
- [ ] Bots feeling stronger than humans (they should not)
- [ ] Bots stuck on geometry during or after a transition
- [ ] Bots continuing to use a route that closed mid-act
