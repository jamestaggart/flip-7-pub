# Flip 7 — Bug Bash Tracker

Living list for the bug bash. Authority for correct behavior: [flip7-requirements.md](flip7-requirements.md).
New bugs found during the bash are appended here. Status: `OPEN` → `FIXED` (with verification) or `WONTFIX`.

Legend: **Sev** = Critical (breaks/strands game) · High (wrong outcome) · Med (UX/incorrect display) · Low (cosmetic).

| ID | Sev | Requirement | Summary | Status |
|----|-----|-------------|---------|--------|
| BB-01 | Critical | FR-26 | Flip Three: a bust during forced draws never advanced the turn *at all* and never finalized — stranding the game (worst when the target was the last active player or self-busted while an opponent stayed). | FIXED |
| BB-02 | High | FR-21, FR-27 | Action cards can't target self; frontend always targeted opponent, so a held Freeze/Flip Three was unusable once the opponent was inactive. | FIXED |
| BB-03 | High | FR-22 | "Only active player must target self" not enforced. | NOT A BUG — already enforced server-side (target must be active, so a lone active player can only pick themselves). |
| BB-04 | Med | FR-27 | Resolved action card was not discarded from the holder's line after use. | FIXED |
| BB-05 | Critical | FR-04 | Round cleanup only discarded Second Chance cards — all other line cards (numbers, modifiers) stayed in players' lines into the next round, so round 2+ started with stale cards that scored and caused false busts. No reshuffle when the deck emptied. | FIXED |
| BB-06 | Low | FR-28 | Action card dealt in the opening hand resolves when the player takes their turn rather than at the instant of the deal. | WONTFIX (by design) — resolving at deal time would auto-pick a target and violate FR-21 (holder must choose any active target). Resolving on the player's turn preserves that choice; no card is lost and no outcome is wrong. |
| BB-07 | Critical | FR-04, FR-30 | (Discovered while fixing BB-05) Player lines were never reset between rounds — same root cause as BB-05, fixed together by setting aside all line cards at round end. | FIXED |

## Notes / findings log

_(new bugs discovered while bashing get appended below and added to the table above)_

- **BB-01 fix:** the Flip Three bust branch returned immediately without creating a next turn or
  finalizing. Now: if no active players remain the round finalizes; otherwise the turn advances
  to the next active player. Regression tests: `test_flip_three_self_bust_advances_turn_to_opponent`,
  `test_flip_three_last_player_bust_finalizes_round`.
- **BB-04 fix:** added `discard_action_card_from_line`; `handle_freeze`/`handle_flip_three` now
  discard the played action card from the holder's line. Test: `test_freeze_discards_used_action_card_from_line`.
- **BB-05/BB-07 fix:** `finalize_round` now sets aside *all* line cards to the discard pile (not
  just Second Chance), so each round starts with empty lines; `draw_card_for_player` reshuffles
  the discard pile back into the deck when it is exhausted. Tests:
  `test_line_cleared_and_deck_persists_between_rounds`, `test_draw_reshuffles_discard_when_deck_empty`.
- **BB-02 fix (frontend):** action-card target now resolves to the opponent when active, otherwise
  to self; the target panel shows "(yourself)" when self-targeting. Server already permitted self-target.
- **BB-06 resolution:** kept by design. A Freeze/Flip Three dealt as an opening card is resolved by
  the holder on their turn (its action button appears), preserving the required target choice per
  FR-21. Auto-resolving at deal time would remove that choice, so it is intentionally not changed.
- Verification: 63 backend tests pass; frontend `npm run build` passes. **No open bugs.**
