# API Overview

The backend exposes a Django REST Framework API under `/api/`. The frontend uses a small subset of the available endpoints for normal gameplay, while several lower-level endpoints remain available for rule validation, scoring, and state inspection.

## Conventions

- Base path: `/api/`
- Transport: JSON over HTTP
- Success responses: standard JSON payloads
- Error responses: JSON object with `error`, `error_code`, and optional `details`

Example error shape:

```json
{
  "error": "Player is not active in this round",
  "error_code": "player_not_active",
  "details": {}
}
```

## Frontend-facing endpoints

These are the endpoints the current Next.js app uses directly.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/players/` | List players |
| `POST` | `/api/players/` | Create a player |
| `PATCH` | `/api/players/{playerId}/` | Update a player's display name |
| `GET` | `/api/games/` | List games |
| `POST` | `/api/games/create/` | Create a game and optionally auto-join the creator |
| `POST` | `/api/games/{gameId}/join/` | Join a game with a seat number |
| `POST` | `/api/games/{gameId}/remove_player/` | Remove a waiting-room player before the game starts |
| `POST` | `/api/games/{gameId}/start_round/` | Start the next round |
| `GET` | `/api/games/{gameId}/state/` | Fetch the canonical board state |
| `POST` | `/api/games/{gameId}/close/` | Delete a game |
| `GET` | `/api/games/{gameId}/results/` | Fetch final standings |
| `POST` | `/api/games/{gameId}/hit/` | Take a hit action |
| `POST` | `/api/games/{gameId}/stay/` | Take a stay action |
| `POST` | `/api/games/{gameId}/freeze/` | Resolve Freeze against an active target |
| `POST` | `/api/games/{gameId}/flip_three/` | Resolve Flip Three against an active target |

## Lower-level and support endpoints

These endpoints exist in the backend even though the current frontend does not rely on all of them.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/games/{gameId}/rules/validate/` | Validate whether a proposed action is legal |
| `POST` | `/api/games/{gameId}/rules/resolve/` | Resolve an action by generic action type |
| `POST` | `/api/games/{gameId}/rounds/{roundId}/score/calculate/` | Return a score breakdown for one player |
| `POST` | `/api/games/{gameId}/rounds/{roundId}/score/apply/` | Apply round score to the running total |
| `POST` | `/api/games/{gameId}/rounds/{roundId}/actions/bust/` | Force a bust state |
| `POST` | `/api/games/{gameId}/rounds/{roundId}/actions/flip-seven/` | Force Flip 7 round completion |
| `POST` | `/api/games/{gameId}/rounds/{roundId}/end-check/` | Ask the backend whether the round should finalize |
| `GET/POST/...` | `/api/game-players/`, `/api/card-definitions/`, `/api/decks/`, `/api/card-instances/`, `/api/card-locations/`, `/api/rounds/`, `/api/turns/`, `/api/turn-actions/` | CRUD endpoints exposed by DRF viewsets |

## Key payloads

### Player

```json
{
  "id": 12,
  "username": "alice",
  "display_name": "Alice"
}
```

### Game summary

```json
{
  "id": 8,
  "game_code": "FLIP4821",
  "status": "pending",
  "target_score": 200,
  "created_by": 12
}
```

### Canonical game state

This is the main read model used by the frontend.

```json
{
  "game_id": 8,
  "game_code": "FLIP4821",
  "status": "active",
  "target_score": 200,
  "round_id": 3,
  "round_ended": false,
  "active_player_count": 2,
  "deck_remaining": 87,
  "current_turn": 12,
  "players": [
    {
      "player_id": 12,
      "username": "alice",
      "display_name": "Alice",
      "active": true,
      "is_busted": false,
      "score": 11,
      "total_score": 54,
      "unique_numbers": 2,
      "cards": [
        {
          "card_name": "7",
          "value": 7,
          "effect_type": "number",
          "effect_payload": ""
        },
        {
          "card_name": "+4",
          "value": null,
          "effect_type": "modifier",
          "effect_payload": "+4"
        }
      ]
    }
  ]
}
```

### Action request

`hit` and `stay` require the acting player.

```json
{
  "player_id": 12
}
```

`freeze` and `flip_three` require both actor and target.

```json
{
  "player_id": 12,
  "target_player_id": 18
}
```

### Action response

Action responses include both the specific outcome and a rebuilt `state` payload so the UI can update immediately.

```json
{
  "game_id": 8,
  "round_id": 3,
  "action_type": "hit",
  "actor_player_id": 12,
  "next_turn_player_id": 18,
  "bust": false,
  "flip_seven": false,
  "score": 11,
  "state": {
    "game_id": 8,
    "status": "active"
  }
}
```

## Gameplay contract notes

- The backend enforces turn order.
- A player must be an active member of the game to act.
- Freeze and Flip Three targets must be active members of the same game.
- `stay` is rejected when the acting player has no line cards.
- Finished games reject new turn actions.
- Results are exposed separately through `/results/`, but action responses already carry the updated live state.

## Frontend integration notes

The current frontend wraps all API calls in `frontend/src/lib/api.ts` and normalizes network and non-JSON failures into user-facing errors. The intended pattern is:

1. Submit one action request.
2. Use the returned outcome for immediate messaging.
3. Refresh or trust the returned state to rerender the board.

That keeps rule interpretation on the backend and minimizes duplicated client logic.