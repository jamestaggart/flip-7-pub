# Flip 7 Manual Test Plan

This document provides a practical manual validation flow for the current project state.

## Redesign-specific user stories covered

The current redesign flow is covered by the following stories:
- US-20: Configure a match from the redesigned setup shell.
- US-21: Follow the active game from a board-first experience.
- US-22: Resolve turns from the shared action panel.
- US-23: Review round summaries and match results without losing context.

These stories are documented in [AI/flip7-frontend-design-document.md](AI/flip7-frontend-design-document.md) and [AI/flip7-frontend-test-plan.md](AI/flip7-frontend-test-plan.md).

## Purpose

Use this plan to verify that the game works end to end in the browser with the documented local environment.

Reference documents:

- [README.md](README.md)
- [AI/flip7-game-rules.md](AI/flip7-game-rules.md)
- [AI/flip7-frontend-design-document.md](AI/flip7-frontend-design-document.md)
- [AI/replay-reset-validation.md](AI/replay-reset-validation.md)

## Environment setup

Start from the project root.

1. Reset and start the stack:

```bash
docker compose down -v --remove-orphans
docker compose up -d --build
docker compose exec backend python manage.py migrate
```

2. Open the app:

- Frontend: http://localhost:3000
- API: http://localhost:8000

3. Optional confidence checks before manual testing:

```bash
ROOT_DIR="$(git rev-parse --show-toplevel)"
docker compose -f "$ROOT_DIR/docker-compose.yml" exec backend python manage.py test game.tests
curl -sf http://localhost:8000/api/players/ > /dev/null
curl -sf http://localhost:3000 > /dev/null
(cd "$ROOT_DIR/frontend" && node -e "const { chromium } = require('@playwright/test'); (async () => { const browser = await chromium.launch(); const page = await browser.newPage(); await page.goto('http://localhost:3000'); await page.getByText('Backend connected and ready').waitFor({ timeout: 30000 }); await browser.close(); })().catch((error) => { console.error(error); process.exit(1); });")
(cd "$ROOT_DIR/frontend" && PLAYWRIGHT_BASE_URL=http://localhost:3000 npx playwright test)
```

Important:

- The snippet above is safe to run from the project root or from a subdirectory such as `frontend`.
- The `node -e` step above opens a headless browser against `http://localhost:3000` and waits for the exact `Backend connected and ready` UI state before the suite starts.
- If you have just changed frontend config such as `next.config.js` or Playwright base URL settings, restart the frontend container before running the check: `docker compose up -d --build frontend`.
- If Playwright still fails immediately on `Player added`, the frontend on port `3000` is serving but has not successfully transitioned out of `Checking the backend...`.

## Test data guidance

- Use two fresh player names for each manual run.
- For fast validation, set a small target score such as `10` or `20`.
- For a normal gameplay feel, use the default target score of `200`.

## Core manual flow

### 1. Setup shell and lobby flow

Steps:

1. Open http://localhost:3000.
2. Enter a username in the setup panel.
3. Select the active player and set a target score.
4. Click Create game.

Expected results:

- The setup panel updates with the created player.
- The app transitions into the board-first experience.
- The hero panel, game status, and board shell are visible.

### 2. Board-first gameplay flow

Steps:

1. Create or join a game.
2. Start a round.
3. Observe the turn banner, player panels, and action panel.

Expected results:

- The current turn is clearly highlighted.
- Each player panel shows round score, total score, risk, and cards.
- The action panel presents Hit, Stay, Freeze Target, and Flip Three Target in the correct state.

### 3. Action feedback and turn changes

Steps:

1. Trigger a Hit action.
2. Observe the feedback banner and player state updates.
3. Trigger a Stay or another action as appropriate.

Expected results:

- The feedback banner updates with the result.
- The board state changes without losing context.
- The next turn is clear and legible.

### 4. Round summary and game-over overlays

Steps:

1. Continue the round until it ends.
2. Review the round-summary overlay.
3. Continue until the match reaches game over.

Expected results:

- The overlay explains the outcome and shows player results.
- The next-round, replay, and new-game actions are clear.
- The game-over overlay announces the winner and final standings.

### 5. Keyboard and accessibility pass

Steps:

1. Use Tab and Shift+Tab to navigate the setup, board, and overlay controls.
2. Press Escape to dismiss an overlay if applicable.

Expected results:

- Focus is visible and moves predictably.
- Dialog controls remain reachable.
- The board remains understandable when overlays are closed.

## Core manual flow

### 1. Home page loads

Steps:

1. Open `http://localhost:3000`.

Expected results:

- The page title `Flip 7` is visible.
- Backend connection status appears ready.
- No blocking error panel appears.

### 2. Create players

Steps:

1. Enter a username.
2. Click `Add player`.
3. Repeat for a second player.

Expected results:

- `Player added` appears after each create.
- Both players appear in the Players list.
- The `Active player` selector contains both players.

### 3. Configure target score

Steps:

1. In `Target score`, enter a low number such as `10`.

Expected results:

- The field accepts the value.
- The created game should use this value for scoring progress.

### 4. Create a game

Steps:

1. Select player one in `Active player`.
2. Click `Create game`.

Expected results:

- A game code is shown in the action banner.
- `Main Board` becomes visible.
- The game appears in the Games list.
- The board displays round/game status information.

### 5. Join the game with player two

Steps:

1. Change `Active player` to player two.
2. In the created game row, click `Join`.

Expected results:

- `Joined game` appears.
- No duplicate membership or seat conflict error appears.
- The game remains selected and viewable.

### 6. Start a round

Steps:

1. In the created game row, click `Start round`.

Expected results:

- Round number appears.
- Deck count appears.
- A player area is highlighted as the current turn.
- Both players are displayed on the main board.

### 7. Take actions during a round

Steps:

1. Use `Hit` on the current turn.
2. Observe board updates.
3. Use `Stay` when appropriate.

Expected results:

- Action banner updates after each action.
- Cards appear in player rows.
- Risk and unique-number counts change appropriately.
- Current-turn highlight moves when turns advance.
- Invalid actions should not silently succeed.

### 8. End a round

Steps:

1. Continue actions until the round ends.

Expected results:

- `Round summary` overlay appears when the round ends.
- Each player’s round score and total are shown.
- Background controls are blocked while the overlay is open.

### 9. Start next round

Steps:

1. Click `Next Round` in the overlay.

Expected results:

- Overlay closes.
- A new round starts in the same game.
- Turn controls become available again.

### 10. Reach game over

Steps:

1. Continue playing rounds until a player reaches the configured target score.

Expected results:

- `Game over` overlay appears.
- Winner is shown.
- Standings are shown.
- Totals reflect the finished game state.

## Replay and reset checks

### 11. Replay flow

Steps:

1. End a round.
2. Click `Next Round` from the summary overlay.

Expected results:

- Same game continues.
- New round starts cleanly.
- Turn controls are usable.

### 12. Reset flow

Steps:

1. From the current app state, click `Create game` again.

Expected results:

- A new game is created without reloading the page.
- A different game code is shown.
- The board state switches to the newly created game.

## Action card checks

These do not all need to occur in one run, but should be manually observed across sessions if you want extra confidence.

### 13. Freeze

Expected results:

- Target player becomes inactive.
- The action resolves without breaking turn flow.

### 14. Flip Three

Expected results:

- Up to three cards resolve in sequence.
- The sequence stops early on bust or Flip 7.
- Deferred Freeze or nested Flip Three resolves correctly when applicable.

### 15. Second Chance

Expected results:

- A player can hold Second Chance.
- A duplicate number can be discarded along with Second Chance instead of causing bust.
- Second Chance cards are not left stuck in finished-round state.

## UI and usability checks

### 16. Board clarity

Expected results:

- Active player is visually obvious.
- Deck count is visible.
- Number, modifier, and action cards are visually distinct.
- Score lines are readable.

### 17. Loading and disabled states

Expected results:

- Buttons disable during requests.
- No duplicate requests are triggered from rapid clicking.

### 18. Error handling

Steps:

1. If an error occurs, observe the error panel.
2. Use `Retry` if relevant.

Expected results:

- Errors are visible and recoverable.
- Retry reloads data cleanly.

## Negative/manual sanity checks

### 19. Game creation without players

Expected results:

- `Create game` is disabled when there are no players.

### 20. Duplicate join attempt

Steps:

1. Try to join the same game again using the same selected player.

Expected results:

- No duplicate game membership is created.
- App remains stable.

### 21. Turn ownership sanity

Steps:

1. Change the `Active player` selector during a round.
2. Continue taking actions.

Expected results:

- Actions follow the board’s current turn logic.
- The dropdown does not override turn ownership incorrectly.

## Minimum release acceptance

A manual run is acceptable if all of the following are true:

1. Two players can be created.
2. A game can be created and joined.
3. A round can start.
4. Hit and Stay work.
5. Round summary appears.
6. Next Round works.
7. A player can reach the configured target score.
8. Game over appears with winner and standings.
9. New game works after game over.
10. No blocking UI errors occur during the flow.

## Notes

- Automated coverage already validates many backend rule and UI interaction details.
- This plan is intended to confirm the real browser experience and end-to-end flow manually.
