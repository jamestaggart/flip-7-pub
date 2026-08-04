# Database Overview

The Flip 7 backend uses a normalized relational model to separate players, games, memberships, card definitions, per-game card instances, card locations, round history, turn history, and final standings.

## Entity relationship diagram

```mermaid
erDiagram
    Player ||--o{ Game : creates
    Player ||--o{ GamePlayer : joins
    Player ||--o{ Round : wins
    Player ||--o{ Turn : acts_in
    Player ||--o{ TurnAction : targets
    Player ||--o{ CardLocation : owns_line_card
    Player ||--o{ GameResult : finishes_with

    Game ||--o{ GamePlayer : has
    Game ||--o{ Deck : has
    Game ||--o{ CardInstance : contains
    Game ||--o{ CardLocation : tracks
    Game ||--o{ Round : has
    Game ||--o{ Turn : has
    Game ||--o{ GameResult : publishes

    CardDefinition ||--o{ CardInstance : instantiates
    Deck ||--o{ CardInstance : starts_in
    CardInstance ||--o{ CardLocation : located_as
    CardInstance ||--o{ TurnAction : referenced_by

    Round ||--o{ Turn : contains
    Turn ||--o{ TurnAction : records

    Player {
        bigint id PK
        string username UK
        string display_name
        datetime created_at
    }

    Game {
        bigint id PK
        string game_code UK
        string status
        bigint created_by_id FK
        int target_score
        string ruleset_version
        datetime started_at
        datetime finished_at
        datetime created_at
    }

    GamePlayer {
        bigint id PK
        bigint game_id FK
        bigint player_id FK
        int seat_number
        bool is_active
        bool is_busted
        int final_score
        int ranking
        datetime joined_at
    }

    CardDefinition {
        bigint id PK
        string card_name
        int value
        string effect_type
        string effect_payload
        bool is_special
    }

    Deck {
        bigint id PK
        bigint game_id FK
        string deck_name
        string deck_type
        datetime created_at
    }

    CardInstance {
        bigint id PK
        bigint card_definition_id FK
        bigint game_id FK
        bigint deck_id FK
        datetime created_at
    }

    CardLocation {
        bigint id PK
        bigint card_instance_id FK
        bigint game_id FK
        bigint owner_player_id FK
        string zone_type
        int position_in_zone
        bool is_face_up
        datetime moved_at
    }

    Round {
        bigint id PK
        bigint game_id FK
        int round_number
        bigint winner_player_id FK
        datetime started_at
        datetime ended_at
    }

    Turn {
        bigint id PK
        bigint game_id FK
        bigint round_id FK
        bigint acting_player_id FK
        int turn_number
        string action_type
        text result_summary
        datetime started_at
        datetime ended_at
    }

    TurnAction {
        bigint id PK
        bigint turn_id FK
        bigint card_instance_id FK
        bigint target_player_id FK
        text action_detail
        datetime created_at
    }

    GameResult {
        bigint id PK
        bigint game_id FK
        bigint player_id FK
        int score
        int ranking
        bool is_winner
        text notes
    }
```

## Model groups

### Identity and lobby

- `Player` stores reusable user identities.
- `Game` stores the lifecycle of a single multiplayer session.
- `GamePlayer` is the roster join table that assigns seat order and round-level active/busted flags.

### Cards and deck state

- `CardDefinition` describes the abstract card type such as `7`, `+4`, `Freeze`, or `Second Chance`.
- `CardInstance` materializes one concrete card inside one game deck.
- `Deck` groups instances for a game.
- `CardLocation` tracks where each instance currently is:
  - `deck`
  - `line`
  - `discard`

This split is what allows the backend to model a persistent shared deck across multiple rounds while preserving the official card frequencies.

### Round and turn history

- `Round` captures the start and end of each round and optionally the Flip 7 winner.
- `Turn` captures the acting player rotation for a round.
- `TurnAction` is available to record action-level detail, although the main gameplay flow currently relies more heavily on live state and service return payloads.

### Final standings

- `GameResult` stores final ranking rows for completed games.
- `GamePlayer.final_score` acts as the running total during the game.

## Constraints that matter

- A player can join a game only once.
- A seat number can be used only once per game.
- Seat numbers must be positive.
- Card locations only allow `deck`, `line`, or `discard`.
- `line` cards must belong to a player; `deck` and `discard` cards must not.
- One final result row exists per game/player pair.

## State reconstruction

The frontend board is not persisted as a separate read model. Instead, the backend rebuilds it from the relational model by combining:

- `Game`
- the latest `Round`
- the latest `Turn`
- `GamePlayer` rows ordered by seat
- each player's current `CardLocation` rows in the `line` zone
- computed round score and unique-number count

That reconstructed payload is exposed through the game state endpoint and treated as the canonical board state by the frontend.