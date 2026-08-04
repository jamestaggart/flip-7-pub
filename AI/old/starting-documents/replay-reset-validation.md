# Replay and Reset Validation Spec

This document defines pass/fail criteria for replay and reset behavior.

## Scope

- Replay: start another round after a round ends.
- Reset: start a new game after finishing or abandoning current game flow.

## Replay acceptance criteria

1. From an active game, a round can be ended through normal actions.
2. Round summary is shown when available.
3. Selecting Next Round starts a fresh round on the same game.
4. Turn controls are available again after replay starts.

## Reset acceptance criteria

1. User can create a new game from UI flow without reloading the page.
2. New game has a different game code than the prior game.
3. New game state is loaded in the board and action banner.

## Recommended automated checks

- Playwright test: end round, click Next Round, assert round restarted.
- Playwright test: create game A, create game B, assert B code differs and state is bound to B.

## Notes

- Full game-to-200 automation is tracked separately and may require deterministic long-game mode.
