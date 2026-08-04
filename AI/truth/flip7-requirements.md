# Flip 7 — Game Requirements (Source of Truth)

**Status:** Canonical behavioral spec for the Flip 7 implementation. If code, tests, or other
docs disagree with this file, this file wins — update code/tests to match, or change this file
first (with rationale) if a rule is genuinely being revised.

**Companion docs (in this `truth/` folder):**
- [rules-user-stories.md](rules-user-stories.md) — executable Given/When/Then acceptance tests,
  each traced to a requirement ID below. This is the *test backlog*, not the authority.

**Upstream references:**
- Rules narrative: [AI/flip7-game-rules.md](AI/flip7-game-rules.md)
- Deck authority: [AI/starting-documents/deck-composition-spec.md](AI/starting-documents/deck-composition-spec.md)

**How to read this:** Each requirement has an ID (`FR-…`), the rule, the trace to a user story,
and a **Status**: `MET` (implemented + verified), `OPEN` (known gap/bug to fix), or
`CHECK` (needs verification during the bug bash).

**Architecture invariant:** the backend is authoritative for all game logic and scoring. The
frontend must render backend state and never recompute rules. Any place the UI derives rule
outcomes locally is a defect.

---

## 1. Deck

| ID | Requirement | Story | Status |
|----|-------------|-------|--------|
| FR-01 | The deck is exactly 94 cards: 79 number cards (one `0`, and N copies of N for 1–12), 6 modifiers (`+2 +4 +6 +8 +10 x2`, one each), 9 action cards (`Freeze`, `Flip Three`, `Second Chance`, three each). | US-R01 | MET |
| FR-02 | All modifier values, including `+8` and `+10`, are reachable in play. | US-R02 | MET |
| FR-03 | Action cards appear at their true frequency (3 of each), not rarer. | US-R03 | MET |
| FR-04 | Within a game, drawn/played cards are set aside; the deck persists across rounds and is only reshuffled when exhausted. It is **not** rebuilt fresh each round. | US-R29 | MET |

## 2. Turn actions: Hit / Stay

| ID | Requirement | Story | Status |
|----|-------------|-------|--------|
| FR-05 | On a turn, an active player may Hit (draw one card) or Stay. Hitting adds exactly one card and passes play to the next active player. | US-R04 | MET |
| FR-06 | Staying banks the player's current round score and makes them inactive for the rest of the round. | US-R05 | MET |
| FR-07 | Only active players may act; an action from a non-active player is rejected. | US-R04 | MET |

## 3. Busting

| ID | Requirement | Story | Status |
|----|-------------|-------|--------|
| FR-08 | Drawing a second number card of a value already in the line busts the player (unless saved by Second Chance): they score 0 for the round and become inactive. | US-R06 | MET |
| FR-09 | Modifiers and action cards can never cause a bust — only duplicate *number* cards can. | US-R07 | MET |
| FR-10 | Bust state is authoritative (`is_busted` in game state) and rendered as such by the UI — never inferred from score/card heuristics. | US-R08, US-R09 | MET |

## 4. Flip 7 bonus

| ID | Requirement | Story | Status |
|----|-------------|-------|--------|
| FR-11 | Collecting 7 unique *number* cards scores the normal total **plus 15** and ends the round immediately; remaining players take no further turns. | US-R10 | MET |
| FR-12 | Only distinct number values count toward the 7; modifiers and action cards never count. | US-R11 | MET |
| FR-13 | A `0` counts as one of the seven unique numbers but contributes 0 points. | US-R12 | MET |

## 5. Scoring

| ID | Requirement | Story | Status |
|----|-------------|-------|--------|
| FR-14 | Round score = (sum of number cards × product of any `x2` cards) + sum of additive modifiers. Multiplication is applied before addition. | US-R13 | MET |
| FR-15 | An `x2` (or any modifier) with no number cards scores 0. | US-R14 | MET |
| FR-16 | A busted player scores 0 for the round but retains their accumulated total. | US-R27 | MET |

## 6. Second Chance

| ID | Requirement | Story | Status |
|----|-------------|-------|--------|
| FR-17 | If a player holding Second Chance draws a duplicate number, the Second Chance and the duplicate are discarded and the player does not bust. | US-R15 | MET |
| FR-18 | A player may hold only one Second Chance at a time; a second is passed to another active player without one, or discarded if none qualify. | US-R16 | MET |
| FR-19 | Any unused Second Chance is discarded at the end of the round (never carried over or scored). | US-R17 | MET |

## 7. Freeze

| ID | Requirement | Story | Status |
|----|-------------|-------|--------|
| FR-20 | Freeze played on an active target banks the target's current round score and makes them inactive. | US-R18 | MET |
| FR-21 | An action card (Freeze / Flip Three) may target **any active player, including the player who holds it**. | US-R20 | MET |
| FR-22 | If the holder is the only remaining active player, the action card must be targeted on themselves. | US-R19 | MET |

## 8. Flip Three

| ID | Requirement | Story | Status |
|----|-------------|-------|--------|
| FR-23 | Flip Three forces the target to draw three cards in sequence. | US-R21 | MET |
| FR-24 | The forced sequence stops immediately on a bust or on reaching Flip 7, with the correct outcome. | US-R22 | MET |
| FR-25 | Freeze/Flip Three cards drawn during the sequence resolve *after* the three draws (deferred), with a recursion guard. | US-R23 | MET |
| FR-26 | If the Flip Three target is the last active player and busts during the forced draws, the round must finalize (no stranded/dead-end turn state). | US-R24 | MET |

## 9. Action-card resolution model

| ID | Requirement | Story | Status |
|----|-------------|-------|--------|
| FR-27 | Freeze and Flip Three are held in the player's line until that holder resolves them on a later turn; while held, they enable the corresponding action button when it is that holder's active turn. Once resolved, the used action card is discarded and never scored. | US-R20 | MET |
| FR-28 | An action card dealt in the opening hand follows the same holder-turn resolution model as any other held action card: it remains available to the holder, preserves the FR-21 target choice, and is never lost. | US-R28 | MET |

## 10. Round & game flow

| ID | Requirement | Story | Status |
|----|-------------|-------|--------|
| FR-29 | A round ends when no active players remain (all stayed, frozen, busted) or when Flip 7 is achieved; round scores then add to totals. | US-R25 | MET |
| FR-30 | Each new round resets every player to active/not-busted and deals one opening card each; the lowest seat acts first. | US-R28 | MET |
| FR-31 | The game ends when any player's cumulative total reaches the target score; final rankings are produced. | US-R26 | MET |

---

## Bug-bash focus list (all `OPEN` items)

**No open requirement-level inconsistencies remain inside this file.** Every requirement is `MET`
with backend coverage (63 tests) and should be re-verified end-to-end during the broader
regression work via [rules-user-stories.md](rules-user-stories.md).
