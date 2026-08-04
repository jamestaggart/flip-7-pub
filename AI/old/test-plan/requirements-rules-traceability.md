# Requirements and Rules Traceability Matrix

Last updated: 2026-08-04

Purpose: map each FR/US pair to current automated test evidence and classify coverage status.

Status legend:
- Covered: behavior has direct automated evidence at the enforcing layer.
- Partial: some behavior is tested, but key requirement detail is not directly asserted.
- Missing: no direct automated evidence found yet.

## FR and US mapping coverage

| FR / US | Coverage | Current automated evidence |
|---|---|---|
| FR-01 / US-R01 | Covered | backend/game/tests.py: test_fr01_us_r01_deck_definition_counts_match_composition |
| FR-02 / US-R02 | Covered | backend/game/tests.py: test_fr02_us_r02_plus8_and_plus10_are_reachable_in_deck |
| FR-03 / US-R03 | Covered | backend/game/tests.py: test_fr03_us_r03_action_card_frequency_is_three_each |
| FR-04 / US-R29 | Covered | backend/game/tests.py: test_line_cleared_and_deck_persists_between_rounds; test_draw_reshuffles_discard_when_deck_empty |
| FR-05 / US-R04 | Covered | backend/game/tests.py: test_fr05_us_r04_hit_adds_one_card_and_advances_turn |
| FR-06 / US-R05 | Covered | backend/game/tests.py: test_fr06_us_r05_stay_banks_score_and_deactivates_player |
| FR-07 / US-R04 | Covered | backend/game/tests.py: test_hit_rejects_inactive_player; test_stay_rejects_inactive_player; test_hit_rejects_non_current_turn_player; test_stay_rejects_non_current_turn_player |
| FR-08 / US-R06 | Covered | backend/game/tests.py: test_busted_player_scores_zero_in_round_summary; test_flip_three_stops_early_when_target_busts |
| FR-09 / US-R07 | Covered | backend/game/tests.py: test_fr09_us_r07_modifier_draw_does_not_bust; test_fr09_us_r07_action_draw_does_not_bust |
| FR-10 / US-R08 | Covered | frontend/src/components/__tests__/player-panel.states.functional.test.tsx: renders Bust when is_busted is true |
| FR-10 / US-R09 | Covered | frontend/src/components/__tests__/player-panel.states.functional.test.tsx: does not render Bust for a stayed zero-score player |
| FR-11 / US-R10 | Covered | backend/game/tests.py: test_flip_seven_bonus_applies_only_to_round_winner; test_flip_seven_endpoint_awards_bonus_and_ends_round |
| FR-12 / US-R11 | Covered | backend/game/tests.py: test_fr12_us_r11_only_numbers_count_toward_flip7 |
| FR-13 / US-R12 | Covered | backend/game/tests.py: test_fr13_us_r12_zero_counts_as_unique_and_scores_zero |
| FR-14 / US-R13 | Covered | backend/game/tests.py: test_round_score_calculate_applies_modifiers_and_flip_seven_bonus |
| FR-15 / US-R14 | Covered | backend/game/tests.py: test_fr15_us_r14_x2_without_numbers_scores_zero |
| FR-16 / US-R27 | Covered | backend/game/tests.py: test_fr16_us_r27_bust_scores_zero_but_keeps_previous_total |
| FR-17 / US-R15 | Covered | backend/game/tests.py: test_hit_uses_second_chance_and_prevents_bust |
| FR-18 / US-R16 | Covered | backend/game/tests.py: test_flip_three_passes_extra_second_chance_to_active_player; test_fr18_us_r16_second_chance_discards_when_no_eligible_player |
| FR-19 / US-R17 | Covered | backend/game/tests.py: test_round_end_check_discards_second_chance_cards_when_round_ends |
| FR-20 / US-R18 | Covered | backend/game/tests.py: test_fr20_us_r18_freeze_banks_target_score_and_deactivates_target |
| FR-21 / US-R20 | Covered | backend/game/tests.py: test_fr21_us_r20_freeze_allows_self_target_when_active |
| FR-22 / US-R19 | Covered | backend/game/tests.py: test_fr22_us_r19_lone_active_player_must_target_self |
| FR-23 / US-R21 | Covered | backend/game/tests.py: test_flip_three_draws_up_to_three_cards_for_target |
| FR-24 / US-R22 | Covered | backend/game/tests.py: test_fr24_us_r22_flip_three_stops_when_target_hits_flip_seven; test_flip_three_stops_early_when_target_busts |
| FR-25 / US-R23 | Covered | backend/game/tests.py: test_flip_three_resolves_deferred_freeze_after_draw_sequence |
| FR-26 / US-R24 | Covered | backend/game/tests.py: test_flip_three_last_player_bust_finalizes_round |
| FR-27 / US-R20 | Covered | backend/game/tests.py: test_fr27_us_r20_hit_drawn_action_card_is_held_until_holder_turn_resolution |
| FR-28 / US-R28 | Covered | backend/game/tests.py: test_fr28_us_r28_opening_hand_action_card_is_held_until_resolved |
| FR-29 / US-R25 | Covered | backend/game/tests.py: test_round_end_check_endpoint_returns_status; test_round_end_check_returns_round_continues_when_active_players_remain; test_flip_seven_endpoint_awards_bonus_and_ends_round |
| FR-30 / US-R28 | Covered | backend/game/tests.py: test_start_round_endpoint_increments_round_number_and_sets_starting_player; test_line_cleared_and_deck_persists_between_rounds |
| FR-31 / US-R26 | Covered | backend/game/tests.py: test_finalize_round_marks_game_finished_on_cumulative_score; test_finalize_round_persists_rankings_in_game_results; test_results_endpoint_winner_is_highest_total_score |

## Notes

- Backend rule enforcement has broad coverage and now includes direct FR-05/06/27/28 assertions.
- Frontend rule/render assertions include FR-10 coverage, and frontend section 3.4 behavior coverage is now implemented in unit tests.
- This matrix is evidence only; remaining completeness work is tracked in the regression checklist.
