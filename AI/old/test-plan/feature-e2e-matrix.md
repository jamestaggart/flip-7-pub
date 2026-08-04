# Feature to E2E Primary Mapping

Last validated: 2026-08-03

Purpose: provide one designated primary Playwright happy-path test for each FEAT-E2E item and record the shipped UI-surface audit used to validate feature-inventory completeness.

Current spec files:
- frontend/tests/redesign-entry-lobby.user-story.spec.ts
- frontend/tests/redesign-waiting-active.user-story.spec.ts
- frontend/tests/redesign-resilience-completion.user-story.spec.ts

## UI surface audit (shipped)

Top-level screens found in frontend/src/app/page.tsx:
- splash
- lobby
- create
- waiting
- active
- game_over

Modal overlays found in frontend/src/components/modals.tsx:
- How to Play
- Close game?
- Connection lost
- Round Summary

Resilience and feedback surfaces found in frontend/src/app/page.tsx:
- dismissible error toast
- action status banner
- target-selection panel for Freeze and Flip Three

Audit conclusion:
- The current FEAT-E2E-01 through FEAT-E2E-38 inventory covers all shipped user-visible screens, modal overlays, and major control-driven transitions.
- No additional top-level screen, modal, or user-triggered transition was found outside the existing inventory.

## Primary mapping

| Feature ID | Feature | Primary Playwright test |
|---|---|---|
| FEAT-E2E-01 | splash boot and lobby load | Lobby and rules modal match the redesigned entry flow |
| FEAT-E2E-02 | rules modal from the lobby | Lobby and rules modal match the redesigned entry flow |
| FEAT-E2E-03 | create-game shell opens from the lobby | Create-game shell can return to the lobby |
| FEAT-E2E-04 | create game with player names and target score | Create game flow reaches the waiting room with the configured roster |
| FEAT-E2E-05 | back to lobby from the create-game shell | Create-game shell can return to the lobby |
| FEAT-E2E-06 | add player in the create-game shell | Create-game shell can add and remove a third player row |
| FEAT-E2E-07 | remove player in the create-game shell | Create-game shell can add and remove a third player row |
| FEAT-E2E-08 | target-score controls including presets and stepper | Create-game shell supports target-score stepper and presets |
| FEAT-E2E-09 | lobby refresh and reload open games | Lobby refresh shows a newly created pending game |
| FEAT-E2E-10 | open an existing pending game from the lobby | A low-target game can be opened from the lobby and finished through the redesigned game-over screen |
| FEAT-E2E-11 | lobby empty-state behavior | Lobby shows the designed empty state when no games are open |
| FEAT-E2E-12 | waiting room roster and game code display | Create game flow reaches the waiting room with the configured roster |
| FEAT-E2E-13 | start game from the waiting room | Starting the game shows the redesigned board, deck counter, and player panels |
| FEAT-E2E-14 | remove player from the waiting room before start | Waiting room can remove a player before the game starts |
| FEAT-E2E-15 | open rules modal from the waiting room | Waiting room opens the rules modal without leaving the game |
| FEAT-E2E-16 | close-game flow from the waiting room including confirmation | Waiting room close-game flow returns to the lobby after confirmation |
| FEAT-E2E-17 | cancel close-game flow from the waiting room | Waiting room close-game flow can be cancelled from the confirmation modal |
| FEAT-E2E-18 | initial board render after the first deal | Starting the game shows the redesigned board, deck counter, and player panels |
| FEAT-E2E-19 | hit action happy path | Hit advances the turn and updates the active player on the board |
| FEAT-E2E-20 | stay action happy path | Staying for the last two active players opens the round summary and next round flow |
| FEAT-E2E-21 | Freeze action happy path | Freeze action can target another active player and resolve cleanly |
| FEAT-E2E-22 | Flip Three action happy path | Flip Three action can target another player and resolve the forced draw sequence |
| FEAT-E2E-23 | Second Chance visible happy path | Second Chance visibly saves a duplicate draw without busting the player |
| FEAT-E2E-24 | target-selection UI for a legal special action | Freeze action shows target selection and cancel restores the action panel |
| FEAT-E2E-25 | cancel target-selection flow | Freeze action shows target selection and cancel restores the action panel |
| FEAT-E2E-26 | rules modal from the active board | Active board opens the rules modal without losing game context |
| FEAT-E2E-27 | close-game flow from the active board including confirmation | Active board close-game flow returns to the lobby after confirmation |
| FEAT-E2E-28 | cancel close-game flow from the active board | Active board close-game flow can be cancelled from the confirmation modal |
| FEAT-E2E-29 | round summary modal appears when the round ends | Staying for the last two active players opens the round summary and next round flow |
| FEAT-E2E-30 | next-round flow from the round summary | Staying for the last two active players opens the round summary and next round flow |
| FEAT-E2E-31 | game-over screen appears when target score is reached | A low-target game can be opened from the lobby and finished through the redesigned game-over screen |
| FEAT-E2E-32 | play again with same settings | A low-target game can be opened from the lobby and finished through the redesigned game-over screen |
| FEAT-E2E-33 | new game from the game-over screen | A low-target game can be opened from the lobby and finished through the redesigned game-over screen |
| FEAT-E2E-34 | disconnect modal appears on network failure | Network failure during an action shows the disconnect modal and reconnect restores play |
| FEAT-E2E-35 | reconnect flow restores state after interruption | Network failure during an action shows the disconnect modal and reconnect restores play |
| FEAT-E2E-36 | refresh and reload restoration using persisted game id | Reload restores the previously opened game using persisted game id |
| FEAT-E2E-37 | pending-state lockout prevents duplicate submissions | Pending action lockout prevents duplicate hit submissions |
| FEAT-E2E-38 | dismissible error toast behavior | A failed action shows a dismissible error toast |
