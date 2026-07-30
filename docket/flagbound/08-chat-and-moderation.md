# 08 — Chat & Moderation

## Requirement

The brief asks for a team communication system for coordinating strategy, and —
because the game targets a wide audience including players as young as 10 —
**strong moderation**, with automatic detection of inappropriate language,
bullying, harassment, threats and harmful behaviour, and real consequences
including temporary bans.

## Communication channels

| Channel | Scope | Moderated |
|---|---|---|
| **Team text chat** | Your team only | Yes — full filtering |
| **Pings / map markers** | Your team only | N/A — no free text |
| **Quick commands** | Your team only | N/A — fixed phrase set |
| **Bot callouts** | Your team only | N/A — pre-authored |
| **F.C.S.** | Private to the player | N/A — authored/templated |

**Design note:** there is deliberately **no all-chat between opposing teams**.
Cross-team chat is where the majority of harassment in competitive games
originates, and it buys almost nothing for a 15-minute objective game. Its
absence removes an entire category of abuse before moderation has to handle it.

### Quick commands

The pings-and-presets layer is the primary coordination tool, not a fallback.
It is instant, language-independent, and cannot be abused:

- "Attack the flag" / "Defend the base" / "Enemy here" / "Need help"
- "Follow me" / "Go now" / "Fall back" / "Nice one"
- Contextual pings on flags, routes, hazards and enemies

A player who never types a word should still be able to play the escort strategy
competently. That is the design target for this layer.

## Automated moderation

### Detection

Applied to all free-text chat, in real time, before the message is delivered:

- Profanity and slurs, including obfuscated spellings (leetspeak, spacing,
  substitution)
- Bullying and targeted personal attacks
- Harassment and threats
- Sexual content
- Self-harm content — routed to a support-resource response, **not** to a
  punishment
- Personal information sharing — addresses, phone numbers, external contact
  details, which is a child-safety concern as much as a civility one
- Scams and off-platform solicitation

### Enforcement ladder

Graduated, matching the brief's explicit examples (warnings and temporary chat
restrictions for minor issues; temporary bans such as a one-week suspension for
serious or repeated violations). *Proposed:*

| Tier | Trigger | Consequence |
|---|---|---|
| **0 — Blocked** | Message fails the filter | Message is not delivered; sender sees why |
| **1 — Warning** | First confirmed violation | On-screen warning explaining the rule |
| **2 — Chat mute** | Repeat minor violation | Text chat disabled 24h; pings still work |
| **3 — Extended mute** | Continued violations | Text chat disabled 7 days |
| **4 — Suspension** | Serious violation, or repeated tier-3 | 7-day account suspension |
| **5 — Permanent ban** | Severe violation, or repeated tier-4 | Permanent |

**Severe violations skip the ladder.** Threats of violence, sexual content
directed at a minor, and grooming behaviour go straight to tier 5 with a human
review and, where applicable, a report to the relevant authority.

### Principles

- **Violations decay.** A clean record for *proposed:* 90 days steps a player
  down one tier. The system is meant to correct behaviour, not to permanently
  mark a 10-year-old for one bad match.
- **Never mute the pings.** Chat restrictions never remove pings or quick
  commands. A muted player must still be able to play the team game — otherwise
  the punishment also punishes their four innocent teammates.
- **Explain every action.** Every enforcement tells the player what rule was
  broken and what happens next. Silent punishment teaches nothing.
- **Appeals exist.** Every tier 2+ action is appealable to human review. Filters
  produce false positives and the appeal path is what makes that survivable.
- **Humans review the top of the ladder.** Automation blocks and warns;
  suspensions and permanent bans get human eyes before or immediately after they
  land.

## Player-side tools

Moderation is not only automated — players need their own controls:

- **Report** a player, with a category, from the scoreboard or the chat log; the
  relevant chat context attaches automatically.
- **Block** — never matched into the same team again where possible, and their
  messages hidden.
- **Mute** an individual player or all chat.
- **Chat off entirely** — a supported, first-class configuration.

## Child-safety defaults

Given the 10+ audience, *proposed:* accounts flagged as belonging to minors
default to:

- Free-text chat **off**, pings and quick commands **on**
- Guardian-controlled opt-in to enable text chat
- Stricter filter thresholds that do not decay as quickly
- No display of any personal information in profiles

The full legal framework — COPPA, GDPR-K, age-verification and parental-consent
flows, data retention for moderation logs — is **out of scope for this docket**
and needs specialist review before launch. It is listed in
[12 — Open Questions](12-open-questions.md).

## Success measures

- Rate of reported messages per 1,000 sent, trending down
- False-positive rate on the filter (measured via appeal outcomes)
- Percentage of players who use pings — the health check for the language-free
  coordination layer
- Repeat-offence rate after a tier-1 warning; if warnings do not change
  behaviour, the ladder is wrong
