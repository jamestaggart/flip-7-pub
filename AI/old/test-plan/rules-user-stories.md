# Flip 7 Rules — User Stories for End-to-End Tests

Authority: [flip7-requirements.md](flip7-requirements.md) is the canonical behavioral spec;
each story below traces to a requirement ID (`FR-…`) there. This file is the executable test
backlog derived from those requirements.

Rules narrative: [AI/flip7-game-rules.md](AI/flip7-game-rules.md) and the official Flip 7 rulebook.
Deck authority: [AI/starting-documents/deck-composition-spec.md](AI/starting-documents/deck-composition-spec.md).

Each story is written Given / When / Then so it can be turned directly into a Playwright
end-to-end spec or a backend service/API test. The **Status** line records whether current
behaviour is believed correct (`PASS`), is a known deviation to fix (`BUG`), or is unverified
(`CHECK`). Stories marked `BUG` are the concrete "concerning things" and should be written as
failing tests first, then fixed.

---

## Deck composition

### US-R01 — Deck contains exactly the official 94 cards
- **Given** a new game is started
- **When** the deck is built
- **Then** it contains 94 cards: 79 number cards (0×1, and N copies of N for 1–12),
  6 modifiers (+2, +4, +6, +8, +10, x2 — one each), and 9 action cards
  (Freeze ×3, Flip Three ×3, Second Chance ×3).
- **Status:** PASS (fixed — `DECK_COMPOSITION` now matches the spec; `sum == 94` asserted).

### US-R02 — Every modifier value can appear
- **Given** repeated dealing/hitting across a full deck
- **When** cards are drawn
- **Then** +8 and +10 modifiers are reachable (they exist in the deck).
- **Status:** PASS (fixed — previously +8/+10 were absent).

### US-R03 — Action cards are common enough to appear in normal play
- **Given** a full game is played
- **When** players hit repeatedly
- **Then** Freeze, Flip Three, and Second Chance each appear multiple times (3 copies each).
- **Status:** PASS (fixed — previously only 1 copy of each existed).

---

## Hit, Stay, Bust

### US-R04 — Hitting draws exactly one card
- **Given** it is a player's turn and they are active
- **When** they Hit
- **Then** exactly one card is added to their line and play passes to the next active player.
- **Status:** PASS.

### US-R05 — Staying banks the current round score and ends the turn
- **Given** a player has a non-busted line
- **When** they Stay
- **Then** they become inactive, keep their current round score, and take no further cards
  this round.
- **Status:** PASS.

### US-R06 — Drawing a duplicate number busts the player
- **Given** a player already has a number card of value N in their line and no Second Chance
- **When** they draw a second card of value N
- **Then** they bust, score 0 for the round, and become inactive.
- **Status:** PASS.

### US-R07 — Modifiers and action cards can never cause a bust
- **Given** a player's line
- **When** they draw a modifier (+2…+10, x2) or an action card
- **Then** they never bust from it (only duplicate *number* cards bust).
- **Status:** PASS.

### US-R08 — Busted player displays as busted
- **Given** a player busts during the round
- **When** the board renders
- **Then** that player is shown as "Bust" (driven by `is_busted` from game state, not a heuristic).
- **Status:** PASS (fixed — `is_busted` now exposed in state and used by the UI).

### US-R09 — A player who stays with a zero score is not shown as busted
- **Given** a player stays holding only a `0` card (round score 0)
- **When** the board renders
- **Then** they are shown as stayed/inactive, not "Bust".
- **Status:** PASS (fixed — previous heuristic mislabelled this case).

---

## Flip 7 bonus

### US-R10 — Seven unique number cards ends the round with a +15 bonus
- **Given** a player has 6 unique number cards
- **When** they draw a 7th *unique number* card
- **Then** they score their number/modifier total plus 15, the round ends immediately,
  and remaining players do not take further turns.
- **Status:** PASS.

### US-R11 — Only number cards count toward Flip 7
- **Given** a player holds number cards plus modifiers/action cards
- **When** counting toward the 7-unique threshold
- **Then** modifiers and action cards do not count; only distinct number values do.
- **Status:** PASS.

### US-R12 — A `0` card counts as a unique number worth 0 points
- **Given** a player draws a `0`
- **Then** it counts as one of the seven unique numbers but adds 0 to the score.
- **Status:** PASS.

---

## Scoring order and modifiers

### US-R13 — x2 multiplies the number total before additive modifiers
- **Given** a line with number total S, an x2 card, and additive modifiers M
- **When** the round is scored
- **Then** score = (S × 2) + M (multiply first, then add).
- **Status:** PASS.

### US-R14 — x2 with no number cards scores 0
- **Given** a line containing only an x2 card (no numbers)
- **When** scored
- **Then** the round score is 0.
- **Status:** PASS.

---

## Second Chance

### US-R15 — Second Chance saves a player from a duplicate
- **Given** a player holds a Second Chance and a number card of value N
- **When** they draw a duplicate N
- **Then** the Second Chance and the duplicate are discarded, the player does not bust,
  and play continues.
- **Status:** PASS.

### US-R16 — A player may hold only one Second Chance at a time
- **Given** a player already holds a Second Chance
- **When** they draw another Second Chance
- **Then** it is passed to another active player without one, or discarded if none qualify.
- **Status:** PASS.

### US-R17 — Unused Second Chance cards are discarded at round end
- **Given** the round ends with a player still holding a Second Chance
- **Then** it is discarded (not carried into the next round or counted for score).
- **Status:** PASS.

---

## Freeze

### US-R18 — Freeze banks the target's score and removes them from the round
- **Given** an active player targets another active player with Freeze
- **When** the Freeze resolves
- **Then** the target keeps their current round score and becomes inactive.
- **Status:** PASS.

### US-R19 — The only active player must target themselves with an action card
- **Given** a player is the last remaining active player and resolves a Freeze or Flip Three
- **When** choosing a target
- **Then** the only legal target is themselves.
- **Status:** MET — the only legal target is enforced server-side (the target must be active, so a
  lone active player can only choose themselves). Frontend now offers self as the target.

### US-R20 — Held action cards target any active player (incl. self) when resolved
- **Given** a player holds a Freeze or Flip Three card in their line
- **When** it is that holder's active turn and they resolve the action card
- **Then** they may choose any active player, including themselves, as the target,
  and the used action card is discarded after resolving.
- **Status:** PASS — self-target is allowed, the frontend presents active targets,
  and the used action card is discarded after resolving.

---

## Flip Three

### US-R21 — Flip Three forces the target to draw three cards
- **Given** a Flip Three is played on an active target
- **When** it resolves
- **Then** the target draws three cards in sequence.
- **Status:** PASS.

### US-R22 — Flip Three stops early on bust or Flip 7
- **Given** a target is drawing their three Flip Three cards
- **When** they bust on a duplicate, or reach 7 unique numbers
- **Then** the sequence stops immediately with the correct bust/Flip-7 outcome.
- **Status:** PASS (bust and Flip 7 both short-circuit the loop).

### US-R23 — Action cards drawn during Flip Three resolve after the three draws
- **Given** a Freeze or Flip Three is drawn among the three forced cards
- **When** the three-card sequence completes without a bust
- **Then** the drawn action(s) resolve afterward (deferred), with a recursion guard.
- **Status:** PASS.

### US-R24 — A Flip Three bust that empties the round must end the round
- **Given** the Flip Three target is the last active player
- **When** they bust during the forced draws
- **Then** the round is finalized (no dead-end turn state).
- **Status:** MET — the bust branch now finalizes the round when no active players remain and
  otherwise advances the turn to the next active player.

---

## Round and game flow

### US-R25 — A round ends when no active players remain
- **Given** all players have stayed, been frozen, or busted
- **Then** the round is finalized and per-player round scores are added to totals.
- **Status:** PASS.

### US-R26 — The game ends when a player reaches the target score
- **Given** end-of-round scoring
- **When** any player's cumulative total is at least the target score
- **Then** the game status becomes finished and final rankings are produced.
- **Status:** PASS.

### US-R27 — Busted players score 0 for the round but keep prior totals
- **Given** a player busts
- **When** the round is finalized
- **Then** they add 0 for that round and retain their accumulated total.
- **Status:** PASS.

### US-R28 — Each round deals one card to every player to start
- **Given** a new round starts
- **Then** every player is reset to active/not-busted and dealt one opening card, and the
  lowest seat acts first.
- **Status:** PASS — every player is reset and dealt one opening card, lowest seat first. An action
  card dealt in the opening hand remains held by the player and can be resolved on that holder's
  turn, preserving the target choice described in US-R20.

### US-R29 — Cards are not reshuffled every round
- **Given** a multi-round game
- **When** a new round begins
- **Then** played cards are set aside and the deck persists across rounds, reshuffling only when
  exhausted.
- **Status:** MET — `finalize_round` sets aside all line cards to the discard pile and
  `draw_card_for_player` reshuffles the discard back into the deck when it is exhausted.

---

## Priority for fixes (open items)

No open rule-story deviations are currently tracked in this file.
