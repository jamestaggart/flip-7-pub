# Flip 7 Frontend Redesign Checklist (v2)

Source of truth for this redesign:

- Requirements: [flip7-frontend-product-requirements.md](flip7-frontend-product-requirements.md)
- Screen-by-screen design: [app_flow_and_redesign.png](app_flow_and_redesign.png)

Goal: rebuild the frontend as a **mobile-first, responsive, screen-by-screen flow** that presents existing backend state, exposes only backend-legal actions, and matches the redesign's atmosphere. No new game rules; the backend stays authoritative.

Target flow:

`SPLASH → LOBBY → CREATE / JOIN → WAITING → SET TARGET → GAMEPLAY → ROUND END → GAME OVER`
Modals: `RULES / HOW TO PLAY`, `HELP`, `CONFIRM LEAVE`, `DISCONNECT`.

Status legend: `[x]` done · `[~]` partial · `[ ]` not started.

---

## 0) API and backend mapping (do first)

Confirm each screen maps to a real endpoint before building it. Existing endpoints:

- [x] `POST /api/players/` — create player records for the two local names.
- [x] `POST /api/games/create/` — create game; accepts `created_by` and `target_score` (this is where **Set Target Score** is persisted).
- [x] `GET /api/games/` — lobby list of existing games.
- [x] `POST /api/games/{id}/join/` — join by `player_id` + `seat_number` (join is by game **id**, not game code).
- [x] `POST /api/games/{id}/start_round/` — begins a round, returns `{ round_id, turn_id, state }`.
- [x] `GET /api/games/{id}/state/` — authoritative board state (see shape below).
- [x] `POST /api/games/{id}/hit|stay|freeze|flip_three/` — turn actions by `player_id` (+ `target_player_id` for freeze/flip_three).
- [ ] `POST /api/games/{id}/rules/validate/` — check action legality without mutating. (not yet wired; legality derived from held cards)
- [x] `GET /api/games/{id}/results/` — winner + standings for Game Over.

Backend gaps decided:

- [x] **Join-by-code**: mapped lobby rows → id-based `Open` action (no code lookup).
- [x] **Waiting room / ready state**: derived from `game.status` + `players[]` length.
- [x] **Set Target Score as its own screen**: folded into the create step (stepper + presets).
- [x] **Play Again with same settings**: reuses `create` with the previous `target_score` + players.
- [x] **Splash/Lobby extras** (leaderboard, QR, modes) treated as **out of scope**.

`GET /state/` returns: `game_id, game_code, status, target_score, round_id, round_ended, active_player_count, deck_remaining, current_turn, players[]` where each player has `player_id, username, active, score (round), total_score, unique_numbers, cards[]`. Action responses include `bust`, `flip_seven`, `second_chance_used`, `round_ended`, `round_summary`.

---

## 1) Foundation and architecture

- [x] Define the frontend state machine: `splash, lobby, create, waiting, active, game_over` (+ overlays: round summary, rules, confirm leave, disconnect, target selection).
- [x] Build a single view-model that maps backend state → the shape in requirements §7.2 (adapt field names).
- [x] Centralize API calls in one client module with typed request/response helpers.
- [x] Add single-flight guards so every action submits exactly once (no duplicate create/join/hit).
- [x] Persist active `game_id` for refresh/reconnect recovery.
- [x] Derive available actions from backend state; never enable an action the backend hasn't confirmed legal.
- [x] Add a mobile-first responsive shell (320 / 768 / 1024 breakpoints) with stacked panels on small screens.

## 2) Design system and tokens

- [x] Implement the v2 palette (blue/yellow/coral/green/purple/ink/paper) as CSS tokens.
- [x] Add typography: Bungee for headings/buttons/scores, Inter for body and small text.
- [x] Define reusable button variants: primary, secondary, ghost, success, danger — with default/hover/focus/pressed/loading/disabled states.
- [x] Build the card-front visual system as code-driven components (no baked-in text).
- [x] Add the risk-meter component (segmented dots: green → yellow → red) using color **and** text.
- [x] Implement reduced-motion support at the token level.
- [~] High-contrast (AA) audit not yet formally verified.

## 3) Splash screen (1)

- [x] Full-bleed Flip 7 splash with logo and loading indicator.
- [x] Auto-advance to Lobby after load (~1.2s) or when initial data is ready.
- [x] Respect reduced-motion (no essential info conveyed only by animation).

## 4) Lobby / home hub (2)

- [x] Show logo, primary Create entry, and How to Play access.
- [x] List existing joinable games from `GET /api/games/` with loading, empty, and error states.
- [x] Route to Create Game and Open (join) an existing game.
- [x] Hide/omit unsupported hub features (leaderboard, currency).

## 5) Create game (3A)

- [x] Player 1 and Player 2 name fields with validation and clear labels.
- [x] Starting-player selector indicated by more than color alone (radio glyph + label).
- [x] Target-score input/stepper with presets (respect backend min/max).
- [x] Create button: disabled while invalid or pending; sends one `create` request.
- [x] On success, create/attach both players and transition to Waiting.
- [x] On failure, preserve entered values and show a retry path (toast).

## 6) Join game (3B)

- [x] Entry to open/join an existing game (lobby row → real game id per §0 decision).
- [x] Only enable Open on joinable games; lock the row while pending.
- [x] Success loads authoritative game state; failure keeps the lobby usable.

## 7) Waiting room (4)

- [x] Show game identity, joined players, and ready/waiting status derived from state.
- [x] Host can start the game (`start_round`) once conditions are met.
- [x] Leave action opens the Confirm Leave modal.

## 8) Set target score (5)

- [x] Folded into create per §0.
- [x] Show recommended presets (200 / 300 / 500 / 750 / 1000) within backend constraints.
- [x] Confirm transitions into the waiting room, then gameplay.

## 9) Active round / your turn (6)

- [~] Persistent header: target score, deck count, menu/rules access. (round number `x/12` omitted — backend exposes no round index)
- [x] Turn banner names the active player and shows the backend action message.
- [x] Two player panels: name, turn/round status, round score, total score, risk level, cards, unique-number progress.
- [x] Active player unmistakable via ≥3 cues (label + glow/outline + pill + banner), not color alone.
- [x] Inactive panel stays fully readable, no active controls inside it.
- [x] Action panel: Hit, Stay, and Freeze/Flip Three only when legal, with concise labels.
- [~] Central tappable card / draw affordance — actions are in the action panel; no separate center draw pile yet.
- [x] `aria-live` announces turn changes and key results.

## 10) Turn actions and resolution

- [x] Hit: submit once, lock controls, render returned card/score/risk/next-turn from response (no prediction).
- [x] Stay: submit once; show banked/complete state from response; advance to next player or summary.
- [x] Target selection state for Freeze/Flip Three: confirm/cancel, sends one request.
- [~] Flip Three: settles to authoritative final state (no per-card reveal sequence animation yet).
- [x] Resolving state: lock controls, keep last board visible, replace atomically on response.
- [~] Stale-state resync path is basic (refetch on reconnect); no explicit 409 auto-resync loop yet.

## 11) Result feedback and outcomes

- [x] Card flip result (7): show drawn card (deal-in animation) and updated round score.
- [x] Bust (8): red bust treatment via banner + panel state.
- [x] Round end banked (9): "banked" celebration with the backend round score.
- [x] Second Chance: banner reflects the save from the backend result.
- [x] Flip 7: celebratory banner naming the outcome; values from backend.
- [x] Result banners follow the color hierarchy (info/success/action/warning/danger/celebrate).
- [x] Duplicate danger is an explicit warning strip + icon, separate from the risk meter.

## 12) Scoreboard / round summary (10 + Round Summary overlay)

- [x] One result card per player: round points, updated total, banked/no-points outcome.
- [x] Winner-of-round treatment when applicable.
- [x] Board dimmed and noninteractive; focus moved into the dialog.
- [x] Primary Next Round action submits once (`start_round`) and shows loading; dialog persists until the new round loads.
- [x] If backend reports game completion, route to Game Over instead of a new round.

## 13) Game over (11 win / 12 loss + overlay)

- [x] Winner and final standings from `GET /results/`.
- [x] Show final totals vs target score.
- [x] New Game returns to a clean setup state.
- [x] Play Again with same settings re-creates with prior settings, one request.
- [~] Distinct win/loss celebratory treatment is minimal (no confetti yet).

## 14) Modals

- [x] Rules / How to Play: Hit, Stay, duplicates/bust, Flip 7, Freeze, Flip Three, Second Chance summaries.
- [x] Confirm Leave: warn about losing progress; Cancel / Leave.
- [x] Disconnect / reconnect: non-disruptive messaging; refetch authoritative state on reconnect.
- [x] Only one primary modal at a time; trap and restore focus; Escape closes dismissible dialogs.

## 15) Accessibility

- [x] Dialogs trap focus and restore on close.
- [x] Risk, status, and turn never communicated by color alone.
- [x] Large tap targets (≥44px) via button min-heights.
- [x] `prefers-reduced-motion` preserves information via immediate state changes.
- [~] Full keyboard-focus-visibility and AA contrast audit still pending.
- [~] Disabled controls do not yet always expose a reason.

## 16) Responsive behavior

- [x] Mobile (320px+): stacked panels, active player first, action panel near the active panel.
- [x] Tablet (768px+): wider screen container, larger type.
- [x] Desktop (1024px+): two-panel board row, capped max width.
- [~] Card-row overflow scroll/compress not yet stress-tested.

## 17) Motion and feedback

- [x] Button press: immediate scale feedback.
- [x] Card draw deal-in animation; banner/modal entrance animations.
- [~] Exact timing tuning (220–320ms draw, 180–250ms glow transfer) not yet calibrated.
- [x] Animations never block the authoritative state from applying.

## 18) Resilience and recovery

- [x] Distinct loading states for initial load, create, join, action, next round, replay.
- [x] Failed action keeps the last authoritative board and offers retry (toast) without unsafe replay.
- [~] Refresh/reconnect restores active game via persisted id; full overlay/scroll restoration untested.
- [~] Stale-state responses do not yet auto-trigger a guarded refresh loop.

## 19) Test and validation

- [ ] Update/replace Playwright specs to match new screens and selectors.
- [ ] Cover the full flow: splash → lobby → create → waiting → gameplay → round end → game over.
- [ ] Assert action legality, duplicate-submission protection, and overlay behavior.
- [ ] Keep tests resilient to parallel runs and existing lobby state.
- [x] Run backend `game.tests` in Docker after integration touches (passing).
- [ ] Run Playwright locally against the running stack after specs are updated.

---

## Definition of done

- [~] All 12 designed screens plus modals implemented and reachable in-flow (core flow done; a few §9/§11 flourishes pending).
- [x] Every action reflects backend authority; no client-side rule logic.
- [x] Mobile-first responsive across 320 / 768 / 1024.
- [~] Accessibility and reduced-motion requirements met (focus/motion done; AA + keyboard audit pending).
- [ ] Playwright suite passes locally against the Docker stack.
