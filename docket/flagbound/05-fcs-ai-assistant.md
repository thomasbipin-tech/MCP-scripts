# 05 — F.C.S. (Flagbound Command System)

Every player has a talking computer companion: a guide, strategist and mission
assistant that lives with them for the whole match.

## What F.C.S. is

A personal AI assistant with **voice and text** communication. It is not a
teammate and not a bot — it does not fight, does not carry the flag, and does not
occupy a team slot. It is the player's own channel of information.

## The prime directive

From the brief: **F.C.S. provides helpful suggestions but must not
automatically win the game for the player.**

Concretely, F.C.S. **may**:

- Explain objectives, controls, classes and phases
- Report what the player could reasonably observe or be told by a teammate
- Summarise team state, flag state and score
- Warn about world events it has advance knowledge of
- Suggest strategies, routes and role gaps
- Answer direct questions

F.C.S. **may not**:

- Wall-hack — reveal enemy positions the player's team has not detected
- Aim, move, dodge, or use abilities for the player
- Reveal undiscovered hidden routes before someone finds them
- Auto-execute anything; every suggestion needs a player to act on it

The line: **F.C.S. tells you what a very attentive teammate would tell you.** It
never tells you what only the server knows.

## Phases of assistance

### Before the match — the briefing

- Explains the objective and the win condition
- Introduces the battlefield and names the two bases
- Warns that the world will change twice, and roughly when
- Summarises the four classes and suggests one for the team's current gaps
- For new players: an extended version with control prompts

*Tone target:* mission briefing, not tutorial popup. The player should feel
deployed, not enrolled.

### During the match — live commentary

Continuous monitoring, surfaced as short callouts:

| Category | Example |
|---|---|
| **Enemy contact** | "Two enemies breaking through the west forest." |
| **Incoming attack** | "They're inside your base perimeter." |
| **Flag status** | "Our flag is taken. Carrier heading east." |
| **Team condition** | "You're the last one standing on defence." |
| **Battlefield change** | "Structural failure detected. Ninety seconds." |
| **Opportunity** | "Their base is undefended — go now." |

**Callout budget.** *Proposed:* no more than one voice line every 8 seconds,
with a priority queue — world events > flag events > threats > suggestions.
Silence has to be possible or the assistant becomes noise, and noise gets muted,
and a muted assistant helps nobody.

### Event reactions — the big moments

The brief calls these out specifically. F.C.S. is the voice of the world
changing:

| Event | F.C.S. behaviour |
|---|---|
| **Tremors begin** | Escalating warnings, countdown to collapse |
| **THE COLLAPSE** | Urgent alert, brace instruction, then orientation on landing |
| **Underground begins** | Announces the new environment, notes new route types |
| **Awakening** | Warns that ancient technology is activating |
| **THE ASCENT** | Announces the rise, warns about the edge |
| **Sky towers active** | Announces flag relocation and the new hazards |
| **Final 60 seconds** | Score state and what it will take to win |

These lines carry the cinematic weight of the transitions. They should be
written and performed as set pieces, not as generic UI barks.

## Player questions

The brief requires that players can ask F.C.S. questions. Supported intents:

| Question | Answer contains |
|---|---|
| "Where is the enemy flag?" | Current flag location *if known to the team*, and the nearest route |
| "What strategy should I use?" | A read of the current score, team composition and phase |
| "Where do teammates need help?" | The most contested friendly objective |
| "What class should I pick?" | The gap in the team's composition |
| "What's happening to the map?" | Time until the next transition and what it will do |
| "How am I doing?" | Contribution breakdown so far |
| "What does [class/ability] do?" | Plain explanation |

**Input:** voice (push-to-talk) or text. Voice-off is a first-class option — the
whole system must work with subtitles and text input for players who cannot or
do not want to use a microphone.

## Personality

*Proposed:* calm, competent, warm. A little dry. It has seen the battlefield
collapse before and it is not panicking, which lets the player not panic.

It should never be condescending to a struggling player, and never smug about a
losing score. For a 10-year-old having a bad match, F.C.S. is the thing that
keeps it fun.

## Accessibility

- Full subtitles for every voice line, on by default
- Volume and frequency sliders — including "critical events only"
- Colour-blind-safe indicators for every marker F.C.S. places
- Text-only mode with no functional loss

## Safety

- F.C.S. speech is authored/templated content, so it cannot produce unmoderated
  output.
- If free-form generation is used for player questions, responses must pass the
  same moderation filter as player chat (see [08](08-chat-and-moderation.md)),
  and must be constrained to game topics.
- F.C.S. never repeats player chat content, so it cannot become a laundering
  channel for abuse.
