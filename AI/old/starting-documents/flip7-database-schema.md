# Flip 7 Database Schema (4NF)

This document defines a 4NF database schema for a Flip 7-style card game. The design is intentionally structured to eliminate repeating groups, avoid multi-valued facts, and keep each table focused on a single entity or relationship type.

This version assumes a turn-based card game with:

- multiple players
- a shared deck of cards
- player hands and in-play card lines
- a discard pile or play area
- turn-by-turn game history
- round-level and game-level scoring

This schema is explicitly written for Fourth Normal Form (4NF): each table stores one kind of fact, and each non-key attribute depends on the key, the whole key, and nothing but the key.

## 4NF Design Principles Used Here

- Each table represents one entity type or one relationship type
- No table stores repeating groups or multiple values in a single row
- Facts about cards, players, turns, and locations are stored in separate tables
- Card position and ownership are modeled as facts about a specific card instance rather than as repeated columns on player or game rows
- Turn actions are separated from turns so detailed event history remains atomic and queryable

---

## 1. Core entities

### Players
Represents a person or account who can join games.

| Column | Type | Notes |
|---|---|---|
| player_id | PK | Surrogate key |
| username | varchar(50) | Unique |
| display_name | varchar(100) | Optional |
| created_at | timestamp | |

### Games
Represents one match or session.

| Column | Type | Notes |
|---|---|---|
| game_id | PK | Surrogate key |
| game_code | varchar(20) | Optional short code |
| status | varchar(20) | pending, active, finished, abandoned |
| started_at | timestamp | |
| finished_at | timestamp | nullable |
| created_by_player_id | FK -> players.player_id | nullable |
| ruleset_version | varchar(50) | Optional |

### Game Players
Associates players with a specific game and tracks their seat or role.

| Column | Type | Notes |
|---|---|---|
| game_id | FK -> games.game_id | |
| player_id | FK -> players.player_id | |
| seat_number | int | 1-based seat |
| joined_at | timestamp | |
| is_active | boolean | |
| final_score | int | nullable |
| ranking | int | nullable |

Primary key: (game_id, player_id)

---

## 2. Card catalog and card instances

### Card Definitions
Stores the permanent definition of each card type.

| Column | Type | Notes |
|---|---|---|
| card_def_id | PK | Surrogate key |
| card_name | varchar(100) | |
| suit | varchar(20) | nullable |
| rank | varchar(20) | nullable |
| color | varchar(20) | nullable |
| value | int | optional numeric value |
| effect_type | varchar(50) | e.g. draw, flip, skip |
| effect_payload | text | nullable |
| is_special | boolean | |

### Decks
Represents a deck used in a game.

| Column | Type | Notes |
|---|---|---|
| deck_id | PK | Surrogate key |
| game_id | FK -> games.game_id | |
| deck_name | varchar(100) | e.g. main, discard, bonus |
| deck_type | varchar(20) | draw, discard, side, reserve |
| created_at | timestamp | |

### Card Instances
Represents one physical card copy in a game.

| Column | Type | Notes |
|---|---|---|
| card_instance_id | PK | Surrogate key |
| card_def_id | FK -> card_definitions.card_def_id | |
| game_id | FK -> games.game_id | |
| deck_id | FK -> decks.deck_id | nullable |
| created_at | timestamp | |

This separates the card type from the card copy. That is important because the same card definition can appear multiple times in a game.

---

## 3. Card location and state

### Card Locations
Tracks where each physical card currently is.

| Column | Type | Notes |
|---|---|---|
| card_instance_id | FK -> card_instances.card_instance_id | |
| game_id | FK -> games.game_id | |
| zone_type | varchar(30) | hand, deck, discard, play_area, table, removed |
| owner_player_id | FK -> players.player_id | nullable |
| position_in_zone | int | nullable |
| is_face_up | boolean | |
| moved_at | timestamp | |

Primary key: (card_instance_id, game_id)

Why this is 4NF-friendly:
- it does not store multiple card lists in one row
- it avoids repeating the same player/zone data across many columns
- each location fact is atomic and tied to one card instance
- each row represents one card-location fact rather than a combined record of multiple card states

---

## 4. Turn and action history

### Rounds
If the game is structured by rounds.

| Column | Type | Notes |
|---|---|---|
| round_id | PK | Surrogate key |
| game_id | FK -> games.game_id | |
| round_number | int | |
| started_at | timestamp | |
| ended_at | timestamp | nullable |
| winner_player_id | FK -> players.player_id | nullable |

### Turns
Represents a single turn in a game.

| Column | Type | Notes |
|---|---|---|
| turn_id | PK | Surrogate key |
| game_id | FK -> games.game_id | |
| round_id | FK -> rounds.round_id | nullable |
| turn_number | int | |
| acting_player_id | FK -> players.player_id | |
| started_at | timestamp | |
| ended_at | timestamp | nullable |
| action_type | varchar(50) | draw, play, discard, flip, pass |
| result_summary | text | nullable |

### Turn Actions
Stores the detailed action taken during a turn.

| Column | Type | Notes |
|---|---|---|
| turn_action_id | PK | Surrogate key |
| turn_id | FK -> turns.turn_id | |
| card_instance_id | FK -> card_instances.card_instance_id | nullable |
| target_player_id | FK -> players.player_id | nullable |
| action_detail | text | nullable |
| created_at | timestamp | |

This keeps turn history normalized and avoids overloading the turn table with many optional columns.

---

## 5. Optional scoring and outcomes

### Game Results
If you want to store final outcome explicitly.

| Column | Type | Notes |
|---|---|---|
| game_result_id | PK | Surrogate key |
| game_id | FK -> games.game_id | |
| player_id | FK -> players.player_id | |
| score | int | |
| is_winner | boolean | |
| notes | text | nullable |

---

## 6. Why This Schema Is 4NF

This schema is designed to be 4NF in the following ways:

- Player information is stored once in the players table and referenced by related tables
- Game membership is represented in a separate association table rather than by repeating player columns in the games table
- Card definitions are separated from card instances so the same card type can appear many times without duplication
- Each card’s state and location is recorded as a separate fact in card_locations rather than being embedded in player rows
- Turn history is split into turns and turn_actions so each action remains a distinct fact
- The design avoids storing multiple independent facts in one row or combining several different entities into a single table

## 7. Suggested relationship summary

A typical flow would be:

1. Create a game in games
2. Add players through game_players
3. Create a deck in decks
4. Create card instances in card_instances
5. Place cards in card_locations as the game progresses
6. Record each turn in turns and turn_actions
7. Record final scores in game_results

---

## 8. Example SQL DDL sketch

```sql
CREATE TABLE players (
  player_id BIGINT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE games (
  game_id BIGINT PRIMARY KEY,
  game_code VARCHAR(20) UNIQUE,
  status VARCHAR(20) NOT NULL,
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  created_by_player_id BIGINT REFERENCES players(player_id),
  ruleset_version VARCHAR(50)
);

CREATE TABLE game_players (
  game_id BIGINT NOT NULL REFERENCES games(game_id),
  player_id BIGINT NOT NULL REFERENCES players(player_id),
  seat_number INT NOT NULL,
  joined_at TIMESTAMP NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  final_score INT,
  ranking INT,
  PRIMARY KEY (game_id, player_id)
);

CREATE TABLE card_definitions (
  card_def_id BIGINT PRIMARY KEY,
  card_name VARCHAR(100) NOT NULL,
  suit VARCHAR(20),
  rank VARCHAR(20),
  color VARCHAR(20),
  value INT,
  effect_type VARCHAR(50),
  effect_payload TEXT,
  is_special BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE decks (
  deck_id BIGINT PRIMARY KEY,
  game_id BIGINT NOT NULL REFERENCES games(game_id),
  deck_name VARCHAR(100) NOT NULL,
  deck_type VARCHAR(20) NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE card_instances (
  card_instance_id BIGINT PRIMARY KEY,
  card_def_id BIGINT NOT NULL REFERENCES card_definitions(card_def_id),
  game_id BIGINT NOT NULL REFERENCES games(game_id),
  deck_id BIGINT REFERENCES decks(deck_id),
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE card_locations (
  card_instance_id BIGINT NOT NULL REFERENCES card_instances(card_instance_id),
  game_id BIGINT NOT NULL REFERENCES games(game_id),
  zone_type VARCHAR(30) NOT NULL,
  owner_player_id BIGINT REFERENCES players(player_id),
  position_in_zone INT,
  is_face_up BOOLEAN NOT NULL DEFAULT TRUE,
  moved_at TIMESTAMP NOT NULL,
  PRIMARY KEY (card_instance_id, game_id)
);

CREATE TABLE rounds (
  round_id BIGINT PRIMARY KEY,
  game_id BIGINT NOT NULL REFERENCES games(game_id),
  round_number INT NOT NULL,
  started_at TIMESTAMP NOT NULL,
  ended_at TIMESTAMP,
  winner_player_id BIGINT REFERENCES players(player_id)
);

CREATE TABLE turns (
  turn_id BIGINT PRIMARY KEY,
  game_id BIGINT NOT NULL REFERENCES games(game_id),
  round_id BIGINT REFERENCES rounds(round_id),
  turn_number INT NOT NULL,
  acting_player_id BIGINT NOT NULL REFERENCES players(player_id),
  started_at TIMESTAMP NOT NULL,
  ended_at TIMESTAMP,
  action_type VARCHAR(50) NOT NULL,
  result_summary TEXT
);

CREATE TABLE turn_actions (
  turn_action_id BIGINT PRIMARY KEY,
  turn_id BIGINT NOT NULL REFERENCES turns(turn_id),
  card_instance_id BIGINT REFERENCES card_instances(card_instance_id),
  target_player_id BIGINT REFERENCES players(player_id),
  action_detail TEXT,
  created_at TIMESTAMP NOT NULL
);
```

---

## 8. Why this is a good 4NF design

- Player data is stored once in players
- Game membership is stored once in game_players
- Card definitions are separate from card instances
- Card location is modeled as a relationship, not embedded in player rows
- Turn history is split into turn-level and action-level facts
- No table contains repeating groups or mixed facts about different entities

If you want, I can also turn this into:

- a Mermaid ER diagram
- a PostgreSQL schema file
- a SQLite schema file
- a more exact version tailored to your specific Flip 7 rules
