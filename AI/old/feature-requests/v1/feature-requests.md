# Flip 7 — Feature Requests

New capabilities requested for the game, staged **before** the end-to-end test pass so the specs
can cover them. Authority for existing behavior: [flip7-requirements.md](flip7-requirements.md).
Each feature lists acceptance criteria as `US-F##` stories that will become Playwright/backend tests.

Status: `PROPOSED` (agreed, not built) → `BUILT` (implemented + verified).

---

## FEAT-01 — Close (delete) a game

**Status:** PROPOSED

**Request:** A player should be able to close a game they are in.

**Decisions:**
- **Who/when:** any player in the game may close it at any time (while `pending` or `active`).
- **Result:** closing **permanently deletes** the game and all associated data — no winner is
  declared and no results are kept.

**Current state:**
- No close/delete flow exists in the UI; "Leave game" is client-side navigation only.
- `Game.STATUS_CHOICES` includes `abandoned`, but it is never set and will remain unused.
- Backend: every game-child table (`GamePlayer`, `Deck`, `CardInstance`, `CardLocation`, `Round`,
  `Turn`, `GameResult`) has `on_delete=CASCADE` on its `game` FK, so a single delete cascades cleanly.

**Scope:**
- Backend: expose game deletion (e.g. `DELETE /api/games/{id}/`, already available via the
  `ModelViewSet`, or a `POST /api/games/{id}/close/` action) and confirm the cascade removes all
  rows. Return `204 No Content` on success.
- Frontend: a "Close game" control on the active/waiting screens, guarded by a confirm dialog
  ("This permanently deletes the game for everyone"). After success, return the user to the lobby/splash.
- Frontend resilience: if another participant closed the game, the next state fetch returns `404`;
  clients must handle it gracefully (surface a "This game was closed" message and return to lobby),
  not crash with a JSON/`Unexpected token` error.

**Acceptance criteria:**
- **US-F01** — Given a player is in a `pending` or `active` game, when they confirm "Close game",
  then the game and all its rows are deleted and they are returned to the lobby.
- **US-F02** — Given a game was closed by one player, when another participant's client next fetches
  state, then it receives a not-found result and shows a "game closed" message (no crash).
- **US-F03** — Given a closed (deleted) game id, when any game action or state endpoint is called
  for it, then the API responds with `404` and a consistent error body.
- **US-F04** — Closing requires explicit confirmation; cancelling the confirm leaves the game intact.

**Open questions:**
- Should closing be blocked once a game is already `finished` (nothing to close), or allowed as a
  way to delete history? (Assumed: allowed — delete is delete.)

---

## FEAT-02 — Support 2–30 players

**Status:** PROPOSED

**Request:** Support as many players as desired, up to 30 (not just 2).

**Decisions:**
- **Range:** minimum 2, maximum 30 players.
- **Lobby:** the create/lobby flow lets you add up to 30 players before the first round.
- **Timing:** players may only be added **before the first round starts**; no mid-game joins.

**Current state:**
- No maximum-player limit is enforced anywhere; seats only need to be unique and `> 0`
  (`GamePlayer` unique constraints on `(game, seat_number)` and `(game, player)`).
- `join` is rejected only when the game is `finished`; it is **not** rejected once play has started.
- The frontend create flow is hardcoded to exactly two players.
- Core round logic already generalizes to N players: dealing gives one card per player, turn order
  follows `seat_number`, and scoring / Flip 7 / Freeze / Flip Three are all per-player.
- Deck is 94 cards; dealing to 30 players uses 30 on the opening deal, and the discard reshuffle
  (FR-04) handles exhaustion during long rounds.

**Scope:**
- Backend:
  - Enforce **max 30** on `join` (and any create-time seat assignment); reject the 31st with a clear
    error code (e.g. `game_full`).
  - Reject `join` once the first round has started (status `active` or a round exists) with a clear
    error code (e.g. `game_already_started`).
  - Enforce **min 2** to start a round; reject `start_round` with fewer than 2 players.
- Frontend:
  - Lobby UI to add/name/remove players up to 30 and assign seats before starting.
  - Board rendering must scale from 2 to 30 players (scrollable/compact player list, turn indicator,
    current-turn highlight) instead of the fixed two-panel layout.
  - Action-card targeting must let the actor pick **any active player** from the full roster
    (extends the current opponent/self toggle) — see FR-21.

**Acceptance criteria:**
- **US-F05** — Given a new game, when the host adds players in the lobby, then they can add between
  2 and 30 players and start once at least 2 are present.
- **US-F06** — Given a game already has 30 players, when a 31st tries to join, then the API rejects it
  with `game_full` and the roster stays at 30.
- **US-F07** — Given a game with only 1 player, when the host tries to start a round, then it is
  rejected (minimum 2 players).
- **US-F08** — Given the first round has started, when a new player tries to join, then it is rejected
  with `game_already_started`.
- **US-F09** — Given a 3+ player game, when a player plays Freeze or Flip Three, then they can choose
  any active player (including themselves) as the target, and turn order continues by seat.
- **US-F10** — Given an N-player round, when the round is scored, then dealing, turn rotation, busts,
  Flip 7, and round/game-end all behave per the existing rules for every seat.

**Open questions:**
- Seat assignment: auto-assign next free seat, or let the host order players? (Assumed: auto-assign
  sequential seats in add order.)
- Display strategy for large rosters on mobile (e.g. collapse non-active players). To be settled in
  the frontend design.

---

## FEAT-03 — Stable player order (move the highlight, not the players)

**Status:** PROPOSED

**Request:** When it becomes a player's turn, don't reorder the player list — it's too jarring.
Keep everyone in a fixed position and just move the active highlight to whoever's turn it is.

**Current state:**
- The board sorts the current-turn player to the top on every turn (`orderedPlayers` in
  `renderBoard`, [frontend/src/app/page.tsx](frontend/src/app/page.tsx)), so panels jump around
  as turns change.

**Scope:**
- Frontend only: render players in a **stable order** (seat order) and drive the active state purely
  via the existing `isActive` highlight; remove the current-turn re-sort.

**Acceptance criteria:**
- **US-F11** — Given a multi-player game, when the turn passes from one player to the next, then the
  players stay in the same on-screen positions and only the active highlight moves.
- **US-F12** — Given a full round, when turns cycle through every player, then no player panel changes
  its vertical position at any point.

---

## FEAT-04 — Let players name their character

**Status:** PROPOSED

**Request:** Allow a player to name their character if they haven't already.

**Current state:**
- Players are identified by `username`; the `Player` model already has an unused `display_name`
  field. The create flow does not prompt for a friendly/character name.

**Scope:**
- Frontend: in the lobby (and/or first entry), let each player set a character/display name; if one
  is already set, don't prompt again. Show the character name on the board and in summaries.
- Backend: persist the name (reuse `Player.display_name`, or a per-game name if the same player
  should be able to differ between games — to confirm). Fall back to `username` when unset.

**Acceptance criteria:**
- **US-F13** — Given a player without a character name, when they join/create, then they are prompted
  to enter one and it is saved.
- **US-F14** — Given a player who already has a character name, when they play again, then they are not
  prompted again and their existing name is used.
- **US-F15** — Given a character name is set, when the board and round summaries render, then that name
  is displayed instead of the raw username.

**Open questions:**
- Is the character name global to the player (`Player.display_name`) or per-game? (Assumed: global,
  reused across games, editable.)

---

## Sequencing

These are `PROPOSED` only. Once agreed, implement backend enforcement + endpoints first (with tests),
then the frontend lobby/board scaling, then fold `US-F0x` into the end-to-end suite alongside the
`US-R##` rule stories.
