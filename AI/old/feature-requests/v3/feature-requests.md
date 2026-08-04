# Flip 7 — Feature Requests & Fixes (truth)

Authoritative, agreed-upon changes staged **before** the end-to-end test pass so the specs can cover
them. Authority for existing behavior: [flip7-requirements.md](flip7-requirements.md) and
[rules-user-stories.md](rules-user-stories.md).

The first built set (FEAT-01…FEAT-04, US-F01…F15) is archived at
[../old/feature-requests/v1/feature-requests.md](../old/feature-requests/v1/feature-requests.md).
Numbering here continues from there.

Status legend: `PROPOSED` (agreed, not built) → `BUILT` (implemented + verified).

---

## FEAT-05 — Remove a player from an existing game

**Status:** PROPOSED

**Request:** Allow removing players — not just while first building the roster, but from a game that
already exists.

**Current state:**
- The **create** screen already lets you drop names before the game is created
  (`removePlayer`, down to `MIN_PLAYERS`, in `frontend/src/app/page.tsx`).
- Once the game exists there is **no** way to remove a player:
  - The **waiting room** (`renderWaiting`) only lists players with a "Ready" pill — no remove control.
  - There is no backend endpoint to detach a `GamePlayer`; `join` only ever adds
    (`get_or_create`) — see `backend/game/views.py`.
- Seats are unique per game and ordered by `seat_number`; gaps in the sequence are already harmless
  because turn order iterates existing seats in order.

**Decisions:**
- **Where/when:** removal is supported from the **waiting room** (game `pending`, first round not yet
  started). This is a single-device, pass-and-play flow, so **any player may remove any player**.
- **Floor:** you cannot remove below `MIN_PLAYERS` (2). Removing the second-to-last player is blocked
  with a clear message; to end a 2-player game entirely, use **Close game** (FEAT-01).
- **Identity:** removing a player detaches their `GamePlayer` membership from this game only; the
  `Player` record (and any `display_name`) is preserved for other/future games.

**Scope:**
- Backend:
  - Add a remove endpoint, e.g. `POST /api/games/{id}/remove_player/` (body `{ player_id }`) or
    `DELETE /api/games/{id}/players/{player_id}/`, returning the updated roster / `204`.
  - Reject removal once the first round has started (status `active` or a round exists) with a clear
    error code (e.g. `game_already_started`) — mirrors the join guard.
  - Reject removal that would drop the roster below 2 with a clear error code
    (e.g. `not_enough_players`).
  - Reject removing a player who is not in the game (`player_not_found`).
  - Leave the removed player's seat gap as-is (no re-packing required); the creator/host reference
    stays valid.
- Frontend:
  - A remove control (e.g. an "✕" per row) in the waiting-room roster, guarded so it is disabled/hidden
    when only 2 players remain.
  - After removal, refresh state so the roster and "Start game" enablement update.
  - Handle the `game_already_started` / `not_enough_players` errors with an inline message rather than
    a crash.

**Acceptance criteria:**
- **US-F16** — Given a `pending` game with 3+ players in the waiting room, when a player removes one,
  then that player is detached from the game, the roster shrinks by one, and play can still start.
- **US-F17** — Given a `pending` game with exactly 2 players, when a player attempts to remove one,
  then it is rejected (minimum 2 players) and the roster is unchanged; the user is pointed to
  "Close game" to end the game instead.
- **US-F18** — Given the first round has started, when a player attempts to remove someone, then it is
  rejected with `game_already_started` and the roster is unchanged.
- **US-F19** — Given a player removed from a game, when the roster is re-fetched, then the remaining
  seats keep their positions (gaps are tolerated) and the removed player is gone.
- **US-F20** — Given a removed player, when other games / the player list are inspected, then the
  `Player` record and its `display_name` are still intact (only the membership was removed).

**Open questions:**
- Mid-game removal (during an `active` round): if supported later, define what happens to the
  removed player's line cards (discard), turn (advance if it was theirs), and the round if removal
  drops active players below 2 (finalize). **Assumed out of scope for now** — removal is a
  waiting-room-only action; use Close game to end an in-progress match.

---

## FEAT-06 — Responsive UI for large rosters (up to 30 players)

**Status:** PROPOSED

**Request:** Adding up to 30 players should be handled responsively — the current UI feels flawed at
large player counts.

**Current state:**
- **Create screen** (`renderCreate`) stacks every name input vertically in a single `.stackGap`
  column. At 20–30 players this becomes a very long, cramped scroll with the "Start"/target controls
  pushed far below the fold, and each add appends `Player N` defaults one at a time.
- **Waiting room** (`renderWaiting`) renders one full-width `.rosterRow` per player — long scroll,
  no density options.
- **Board** (`renderBoard`) maps every player to a full-size `PlayerPanel` in a single-column
  `.playersStack` (`display:flex; flex-direction:column; gap`), so a 30-player round is an extremely
  long page; the active player can be far off-screen and there is no compact/overview mode.
- All three areas assume a small (≈2) player count from the original 2-player design.

**Decisions:**
- Layout must remain **mobile-first** and legible from 2 up to 30 players without horizontal overflow
  or clipped controls.
- The **active player** must always be discoverable (auto-scroll into view and/or a persistent
  turn indicator) even in a large roster.
- Primary actions (Start game, target score, Hit/Stay/action buttons) must stay reachable without
  scrolling past the entire roster.

**Scope (frontend only; no rule/back-end changes):**
- Create screen:
  - Make the player list a scrollable, capped-height region so the target-score and "Create" controls
    stay visible; keep "＋ Add player" and the count indicator pinned/visible.
  - Consider a responsive multi-column grid for name inputs on wider viewports; compact spacing at
    high counts.
  - Validate and surface the 2–30 range clearly (already enforced in logic — see FEAT-02).
- Waiting room:
  - Denser roster layout (e.g. responsive grid / smaller rows) that scales to 30 without a giant
    scroll; keep the remove control (FEAT-05) usable at density.
- Board:
  - Scale `.playersStack` to a responsive grid (multiple compact panels per row on wider screens),
    and/or add a **compact panel variant** for non-active players with the active player emphasized.
  - Keep the current-turn highlight (FEAT-03 stable order) and **auto-scroll the active panel into
    view** when the turn changes.
  - Keep the action bar and header stats reachable (e.g. sticky action panel) regardless of roster
    length.
- Purely presentational: no change to turn order, scoring, dealing, or any backend contract.

**Acceptance criteria:**
- **US-F21** — Given the create screen with 30 players added, when the screen renders on a mobile
  viewport, then all name inputs are reachable via a contained scroll and the target-score and Create
  controls remain visible/usable (no clipped or unreachable controls).
- **US-F22** — Given a 30-player game, when the board renders, then player panels lay out responsively
  (compact/grid) without horizontal overflow, and the layout is legible at 2, 8, and 30 players.
- **US-F23** — Given a large roster, when the turn passes to a player who is off-screen, then that
  player's panel is brought into view and clearly highlighted as active.
- **US-F24** — Given any roster size, when the board is shown, then the Hit/Stay/action controls stay
  reachable without scrolling past the entire player list.
- **US-F25** — Given the responsive changes, when a 2-player game is played, then it looks and behaves
  as before (no regression to the small-count experience).

**Open questions:**
- Exact density strategy for the board (multi-column grid vs. collapse non-active panels into a
  summary strip). To be settled in the frontend design; both must satisfy US-F22/US-F23.
- Whether the waiting room and board should share a single "compact player" component.

---

## Bug fixes

### BUG-01 — Turn jumps back to the first player after a bust (round not finished out)

**Status:** PROPOSED

**Report:** When a player busts, the turn goes back to the **first** player who had a turn instead of
continuing to the **next** player, so the remaining players never get their turn and the round doesn't
finish out.

**Reproduction:** In a game with **3 or more** players (seats 1..N), when the player at seat _k_
(where `1 < k < N`) busts, then instead of the turn passing to seat _k+1_, it passes back to seat 1
and the players after _k_ are skipped for that round. A 2-player game does not show the bug (the only
remaining player happens to be the correct "next" one).

**Root cause:**
- In `handle_hit` (bust branch) — and identically in `handle_stay` — the acting player is set
  `is_active = False` **before** `get_next_active_player(game, player)` is called
  (`backend/game/services.py`).
- `get_next_active_player` computes "next" from the list of **currently active** players:
  ```
  ordered = [p.player_id for p in get_active_players(game)]   # busted player already removed
  if current_player.id in ordered:                            # -> False after bust/stay
      ... next after current ...
  return active_players[0].player                             # falls through to the FIRST active seat
  ```
  Because the just-busted (or just-stayed) player is no longer in `active_players`, the
  `current_player.id in ordered` branch is skipped and the function returns `active_players[0]` —
  the **lowest-seat active player** — rather than the player after the current seat.
- The bug was masked in 2-player games and only surfaced once 3+ players were supported (FEAT-02).

**Scope (backend only):**
- Advance the turn based on the acting player's **seat position among all seats**, selecting the next
  **active** player whose seat is after the current player's seat and wrapping to the lowest active
  seat — regardless of whether the current player is still active. Apply the same correct advancement
  to bust (`handle_hit`), stay (`handle_stay`), and any other path that deactivates the current player
  before advancing (Freeze/Flip Three already target other players but should use the same helper).
- No change to scoring, dealing, Flip 7, or round-end conditions.

**Acceptance criteria:**
- **US-F26** — Given a 4-player round (seats 1–4) with everyone active, when the seat-2 player busts,
  then the turn passes to seat 3 (then seat 4, then back to seat 1), and every remaining active player
  takes their turn before the round ends.
- **US-F27** — Given a multi-player round, when a player **stays** (not busts), then the turn advances
  to the next active player by seat in the same correct order (no jump back to the first player).
- **US-F28** — Given the last remaining active player busts or stays, when there are no active players
  left, then the round finalizes correctly (unchanged behavior).
- **US-F29** — Given a 2-player game, when a player busts or stays, then turn behavior is unchanged
  (no regression).

**Regression test to add:** a backend test that runs a 3+ player round where a middle-seat player
busts and asserts the next turn's `acting_player` is the next seat (not seat 1), plus the same for a
stay.

---

## Sequencing

These are `PROPOSED` only. Suggested order once agreed:
1. **BUG-01** first — it's a correctness regression in multi-player rounds; fix in
   `backend/game/services.py` with a regression test.
2. **FEAT-05** backend endpoint + guards (with tests), then the waiting-room remove control.
3. **FEAT-06** responsive layout for create → waiting → board (frontend/CSS only), verifying the
   small 2-player experience is unchanged.
Then fold `US-F16`–`US-F29` into the end-to-end suite alongside the existing `US-F0x` / `US-R##`
stories.
