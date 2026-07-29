# 03 — Combat & Classes

## Philosophy

From the brief: combat focuses on **skill, movement, teamwork and strategy
rather than simple button pressing**. Players do not "tag" each other out — they
fight, in action-based battles inspired by fantasy adventure combat.

Three consequences for the design:

1. **Every attack is answerable.** Block, dodge, or reposition — there is always
   a defensive option, so losing a duel is a decision the player made, not dice.
2. **Movement is a weapon.** Sprint, jump, dodge and terrain use should decide
   more fights than raw damage output.
3. **Duels are winnable but slow enough to interrupt.** A 1v1 should last long
   enough that a teammate can arrive and change the outcome. This is what makes
   the teamwork pillar real instead of decorative.

## The verb set

Available to every class, regardless of build:

| Verb | Behaviour |
|---|---|
| **Attack** | Light/heavy variants; chains into short combos |
| **Block** | Directional guard; absorbs damage, drains stamina, breaks under heavy hits |
| **Dodge** | Short i-frame roll or dash; the primary skill expression |
| **Sprint** | Sustained speed at the cost of stamina; disabled while carrying a flag at full speed (*proposed:* carriers sprint at reduced speed) |
| **Jump** | Traversal and vertical mixups; essential in Act III |
| **Ability** | Class-defining, cooldown-gated — full roster in [13](13-abilities-and-skills.md) |
| **Ping / Callout** | Non-verbal team communication; always available, never moderated away |

## Health, defeat and respawn

- Players have health and stamina. Blocking and dodging cost stamina; running
  out leaves you vulnerable, which is what stops block-spam.
- Defeat is a **temporary elimination**, not a permanent one — respawn at your
  base after a timer (*proposed:* 8s in Act I/II, 8s in Act III including
  falls).
- A defeated flag carrier **drops the flag** where they fell. It can be picked up
  by either team; if untouched it returns to base after a timeout (*proposed:*
  20s).
- Respawn timers should not scale with match time. Late-match punishment
  snowballs, and the brief wants final moments to be close.

## The four classes

Each has a clear strength and a real weakness. From the brief: *no single play
style should dominate.*

### 🛡️ Guardian — defence

**Fantasy:** the wall. The reason your flag is still there.

- **Strengths:** shields, protection abilities for self and allies, powerful
  heavy attacks, highest effective health.
- **Weaknesses:** slowest movement, poor at chasing, weak at solo flag runs,
  vulnerable when isolated from the team.
- **Signature abilities (proposed):** deployable barrier that blocks projectiles;
  a taunt/shove that displaces attackers off objectives or off ledges; a damage
  reduction aura for nearby allies.
- **Phase notes:** dominant in Act II's tight tunnels where chokepoints matter;
  weakest in Act III where mobility rules.

### ⚔️ Swiftblade — speed & capture

**Fantasy:** the one who actually scores.

- **Strengths:** fastest movement, quick attack chains, the best flag carrier —
  suffers the smallest speed penalty while carrying.
- **Weaknesses:** lowest health, loses extended fights, dependent on escorts to
  survive the return trip.
- **Signature abilities (proposed):** a dash that closes or escapes gaps; a brief
  burst of carry speed; extra vertical mobility (wall-run or double jump).
- **Phase notes:** thrives on Act I's open ground and Act III's platform gaps;
  most exposed in Act II's dead ends.

### 🔥 Element Warrior — area control

**Fantasy:** the one who decides where the fight happens.

- **Strengths:** fire, ice, lightning and wind abilities; controls space, denies
  routes, hits groups.
- **Weaknesses:** long cooldowns, weak between abilities, poor sustained
  single-target damage, punished by a Shadow Runner who reaches them.
- **Signature abilities (proposed):** **Fire** — zone denial over time;
  **Ice** — slow/freeze a chokepoint; **Lightning** — burst damage that chains
  between clustered enemies; **Wind** — displacement, and the only ability that
  meaningfully manipulates Act III's air currents.
- **Phase notes:** strongest in Act II's chokepoints and Act III's ledges, where
  displacement is lethal.

### 🌑 Shadow Runner — stealth & disruption

**Fantasy:** the reason the enemy plan collapsed.

- **Strengths:** stealth, distractions, surprise attacks, route discovery,
  highest burst from an unseen opening.
- **Weaknesses:** fragile in a straight fight, stealth breaks on attacking, bad
  at holding ground, near-useless once spotted and focused.
- **Signature abilities (proposed):** temporary invisibility or camouflage; a
  decoy that draws bots and inattentive players; a mark that reveals enemy
  positions to the team; faster discovery of hidden underground routes.
- **Phase notes:** peak class in Act II — the hidden-route act is built for them;
  hardest in Act III's open sightlines with nowhere to hide.

## Counterplay matrix

Read as: *row class pressures column class.*

| | vs Guardian | vs Swiftblade | vs Element Warrior | vs Shadow Runner |
|---|---|---|---|---|
| **Guardian** | — | Strong (survives the burst) | Weak (zoned out) | Even |
| **Swiftblade** | Weak (can't break the wall) | — | Strong (closes the gap) | Even |
| **Element Warrior** | Strong (chip + zone) | Weak (out-paced) | — | Strong (area reveals stealth) |
| **Shadow Runner** | Strong (ignores the front line) | Even | Weak (caught by area effects) | — |

No class beats everything; every class has one matchup it dislikes. This
matrix is the balance target, not a measured result — it is what playtesting
should be checking.

## Team composition

*Proposed:* classes are **freely chosen, not restricted** — no hard limits on
how many of each a team can field. Instead:

- F.C.S. suggests filling gaps during class select ("no Guardian on this team —
  your flag will be exposed").
- Bots fill composition holes deliberately (see [06](06-ai-bots.md)).
- Contribution scoring rewards the roles a stack of one class cannot cover, so
  five Swiftblades lose on merit rather than by rule.

Players may **switch class on respawn**. Locking a class for 15 minutes across
three radically different worlds would fight the adaptation pillar.

## Combat readability (age 10+)

- Attacks telegraph with a visible wind-up.
- **Every class is identifiable by silhouette alone** — proportion and one
  accessory, never colour, since colour belongs to the team. In a fight at
  third-person distance, silhouette is all a player gets. See
  [10 — Characters](10-art-direction-and-cinematics.md#characters).
- Team colour is applied as **emissive** trim so it stays readable in Act I
  daylight, against Act II's glowing dark, and against Act III's bright cloud. Flat colour fails at
  least one of those three. The two team palettes are warm versus cool rather
  than red versus green, so they survive colour-blindness.
- Ability effects are stylised and bright — magic, not injury.
- Defeats are a knockdown followed by a burst of light. No gore.
- Screen-space damage indicators always show the direction of the attacker.
