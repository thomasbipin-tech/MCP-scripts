# 04 — Teamwork, Scoring & Strategies

## The core rule

From the brief: **a player who supports their team should be just as valuable as
a player who defeats many opponents.**

This is stated as a scoring requirement, not a sentiment. If the end-of-match
screen ranks players by eliminations, the pillar is dead no matter what the
design document says. So Flagbound scores **contribution**, and eliminations are
one input among many.

## Contribution scoring

Point values below are *proposed* starting numbers for tuning. What matters is
the ratio: a full defensive or support performance must be able to top the board
against a full offensive one.

### Objective

| Action | Points |
|---|---|
| Capture the enemy flag | 100 |
| Pick up the enemy flag | 20 |
| Return your own dropped flag | 40 |
| Carry the flag a sustained distance | 5 / segment |

### Defence

| Action | Points |
|---|---|
| Defeat an enemy carrying your flag | 60 |
| Defeat an enemy inside your base zone | 25 |
| Hold your base zone under contest | 5 / 10s |
| Intercept an enemy on a discovered route | 30 |

### Support

| Action | Points |
|---|---|
| Assist an ally's elimination | 20 |
| Escort the carrier (stay near them under fire) | 5 / 10s |
| Shield, heal or protect an ally from damage | 15 |
| Revive or rescue a downed ally *(if the revive system ships)* | 30 |
| Ping an enemy who is then engaged by a teammate | 10 |

### Exploration & information

| Action | Points |
|---|---|
| First discovery of a hidden route (per match) | 50 |
| Reveal a hidden area to the team | 25 |
| Scout an enemy position that leads to a team engagement | 15 |

### Combat

| Action | Points |
|---|---|
| Defeat an enemy | 25 |
| Defeat an enemy threatening your carrier | 40 |

Note the numbers: a straight elimination (25) is worth less than stopping an
enemy carrier (60) and half of an assist-plus-escort sequence. Killing is
useful. Killing *for a reason* is what scores.

## End-of-match presentation

The results screen shows **contribution**, broken into Objective / Defence /
Support / Exploration / Combat, so a player can see *how* they contributed. It
does **not** lead with a kill/death ratio.

*Proposed:* every match awards a small set of highlight badges that cover
different play styles, so the recognisable "best player" of a match can be the
person who never won a duel:

- **Flagbound** — most captures
- **Unbroken** — most successful base defences
- **Pathfinder** — most route discoveries
- **Shieldmate** — most time escorting the carrier
- **Turning Point** — the single highest-impact play of the match

## Team strategies

The brief names four. Each needs map affordances and F.C.S. support to be
genuinely viable — a strategy that is only viable on paper is a bug.

### 🛡️ Defensive — hold the base

Players stay near their own flag and repel attacks.

- **Wants:** Guardians, chokepoints, sightlines onto approaches.
- **Best phase:** Act II — tunnels are defensible.
- **Fails when:** the enemy finds an unwatched hidden route, or the phase
  transition moves the flag out from under the defence.
- **Counter:** split-push from two routes; force the defence to choose.

### ⚔️ Aggressive — rush the flag

Commit numbers to reaching the enemy flag fast and repeatedly.

- **Wants:** Swiftblades, open ground, early-match momentum.
- **Best phase:** Act I — long lanes, and the enemy has not settled yet.
- **Fails when:** the rush is repelled and the whole team is dead at once,
  leaving an empty base.
- **Counter:** a single Guardian holding the choke while the rest counter-attack.

### 🌑 Stealth — take the hidden path

Small groups move through secret routes and take the flag before contact.

- **Wants:** Shadow Runners, Act II's hidden network, patience.
- **Best phase:** Act II — the act is built for it.
- **Fails when:** the route is discovered and watched, or a tunnel collapses
  mid-run and strands the team.
- **Counter:** a defender assigned to sweep known routes; area abilities that
  reveal stealth.

### 🤝 Escort — protect the carrier

The team's job is to keep one player alive on the way home.

- **Wants:** mixed composition, Guardians on the flanks, Element Warriors
  denying the pursuit.
- **Best phase:** Act III — long, exposed, dangerous return trips.
- **Fails when:** the escort clumps up and eats one area ability.
- **Counter:** displacement — knock the carrier off a bridge instead of trying
  to out-damage the escort.

## How the game teaches strategy

Not with a tutorial wall. Through:

- **F.C.S.** naming what is happening ("they've pushed the same route three
  times — someone hold the east tunnel") — see [05](05-fcs-ai-assistant.md).
- **Bots** visibly executing strategies and calling them out in team chat — see
  [06](06-ai-bots.md).
- **Scoring** paying out for support play so players discover it is worth doing.
- **The match screen** showing which category earned the win.
