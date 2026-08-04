# Flip 7 API Design

This document outlines a practical API surface for implementing the Flip 7 game rules using the 4NF database schema. The APIs are organized around the core concepts in the game: players, games, rounds, turns, cards, deck state, scoring, and rule enforcement.

---

## 1. Design Principles

The API should:

- support local two-player couch play first
- enforce the game rules consistently
- keep the database as the source of truth
- separate state mutation from read-only queries
- make it easy to build a UI on top of the API

---

## 2. Core API Areas

### 2.1 Player APIs

#### Create Player
- POST /players
- Creates a new player account
- Input: username, displayName
- Returns: playerId

#### Get Player
- GET /players/{playerId}
- Returns player profile information

#### List Players
- GET /players
- Returns a list of players for selection or matchmaking

---

### 2.2 Game APIs

#### Create Game
- POST /games
- Creates a new game session
- Input: createdByPlayerId, rulesetVersion, status
- Returns: gameId

#### Get Game
- GET /games/{gameId}
- Returns game metadata and current state

#### List Games
- GET /games
- Returns games for a player or admin view

#### Join Game
- POST /games/{gameId}/players
- Adds a player to a game
- Input: playerId, seatNumber
- Returns: joined player association

#### Update Game Status
- PATCH /games/{gameId}
- Updates game status such as pending, active, finished, or abandoned

---

### 2.3 Round APIs

#### Create Round
- POST /games/{gameId}/rounds
- Starts a new round within a game
- Input: roundNumber
- Returns: roundId

#### Get Round
- GET /games/{gameId}/rounds/{roundId}
- Returns round info and current state

#### List Rounds
- GET /games/{gameId}/rounds
- Returns all rounds for the game

---

### 2.4 Turn APIs

#### Start Turn
- POST /games/{gameId}/rounds/{roundId}/turns
- Begins a new turn for the current active player
- Input: actingPlayerId, actionType
- Returns: turnId

#### Get Turn
- GET /games/{gameId}/rounds/{roundId}/turns/{turnId}
- Returns turn details and current state

#### End Turn
- PATCH /games/{gameId}/rounds/{roundId}/turns/{turnId}
- Marks the turn as completed
- Input: endedAt, resultSummary

---

### 2.5 Card and Deck APIs

#### Create Deck
- POST /games/{gameId}/decks
- Creates a deck for a game
- Input: deckName, deckType
- Returns: deckId

#### Get Deck
- GET /games/{gameId}/decks/{deckId}
- Returns deck metadata and current contents

#### Create Card Instance
- POST /games/{gameId}/card-instances
- Creates a physical card instance for the game
- Input: cardDefId, deckId
- Returns: cardInstanceId

#### Get Card Instance
- GET /games/{gameId}/card-instances/{cardInstanceId}
- Returns card definition and instance details

#### List Card Instances
- GET /games/{gameId}/card-instances
- Returns all card instances in the game

---

### 2.6 Card Location APIs

#### Move Card
- POST /games/{gameId}/card-locations
- Records where a card currently exists
- Input: cardInstanceId, zoneType, ownerPlayerId, positionInZone, isFaceUp
- Returns: created location record

#### Update Card Location
- PATCH /games/{gameId}/card-locations/{cardInstanceId}
- Updates the card’s current zone, owner, or visibility

#### Get Card Location
- GET /games/{gameId}/card-locations/{cardInstanceId}
- Returns the current placement of a specific card

#### List Player Cards
- GET /games/{gameId}/players/{playerId}/cards
- Returns all cards currently in that player’s line or hand

---

### 2.7 Action APIs

#### Apply Action Card
- POST /games/{gameId}/rounds/{roundId}/actions
- Records an action card effect
- Input: turnId, cardInstanceId, targetPlayerId, actionDetail
- Returns: turnActionId

#### Resolve Flip Three
- POST /games/{gameId}/rounds/{roundId}/actions/flip-three
- Handles the Flip Three mechanic
- Input: targetPlayerId, sourceCardInstanceId
- Returns: resolved action state

#### Apply Freeze
- POST /games/{gameId}/rounds/{roundId}/actions/freeze
- Applies Freeze to a player
- Input: targetPlayerId

#### Apply Second Chance
- POST /games/{gameId}/rounds/{roundId}/actions/second-chance
- Records a Second Chance card usage or assignment
- Input: playerId, targetPlayerId, cardInstanceId

---

### 2.8 Gameplay Decision APIs

#### Player Hits
- POST /games/{gameId}/rounds/{roundId}/actions/hit
- Executes a player choosing to Hit
- Input: playerId, turnId
- Returns: updated card state and next turn state

#### Player Stays
- POST /games/{gameId}/rounds/{roundId}/actions/stay
- Executes a player choosing to Stay
- Input: playerId, turnId
- Returns: updated active/inactive state

#### Bust Player
- POST /games/{gameId}/rounds/{roundId}/actions/bust
- Marks a player as busted for the round
- Input: playerId, reason

#### Achieve Flip 7
- POST /games/{gameId}/rounds/{roundId}/actions/flip-seven
- Ends the round immediately for the Flip 7 bonus
- Input: playerId

---

### 2.9 Scoring APIs

#### Calculate Round Score
- POST /games/{gameId}/rounds/{roundId}/score/calculate
- Calculates the score for a player’s current round line
- Input: playerId
- Returns: subtotal, modifier adjustments, bonus points, final score

#### Apply Round Score
- POST /games/{gameId}/rounds/{roundId}/score/apply
- Stores the round score into the player’s cumulative score
- Input: playerId, roundScore

#### Get Game Results
- GET /games/{gameId}/results
- Returns scores and winner information

---

### 2.10 Rule Enforcement APIs

#### Validate Move
- POST /games/{gameId}/rules/validate
- Checks whether a proposed move is legal
- Input: playerId, actionType, cardInstanceId, targetPlayerId
- Returns: valid or invalid with reason

#### Resolve Turn Effects
- POST /games/{gameId}/rules/resolve
- Applies the full rule engine to a turn action
- Input: turnId, actionType, payload
- Returns: updated game state

#### End Round If Needed
- POST /games/{gameId}/rounds/{roundId}/end-check
- Determines whether the round should end due to no active players or Flip 7

---

## 3. Suggested Request/Response Shape

### Example: Create Game
```json
POST /games
{
  "createdByPlayerId": 1,
  "rulesetVersion": "v1"
}
```

Response:
```json
{
  "gameId": 101,
  "status": "pending"
}
```

### Example: Hit Action
```json
POST /games/101/rounds/5/actions/hit
{
  "playerId": 1,
  "turnId": 42
}
```

Response:
```json
{
  "turnId": 42,
  "playerId": 1,
  "action": "hit",
  "drawnCardInstanceId": 88,
  "bust": false,
  "nextPlayerId": 2,
  "roundEnded": false
}
```

---

## 4. API Coverage Mapping to Rules

### Rule Coverage

- Setup and dealing: create game, join players, create deck, create card instances, move cards to player zones
- Hit / Stay: hit and stay endpoints
- Busting on duplicate numbers: validate move and bust endpoint
- Flip 7 bonus: achieve flip seven endpoint
- Action cards: apply action card endpoints for Freeze and Flip Three
- Second Chance: second chance endpoint
- Modifier card scoring: calculate round score endpoint
- End of round: end round check endpoint
- End of game: game results endpoint

---

## 5. Recommended API Grouping

A clean structure would be:

- /players
- /games
- /games/{gameId}/players
- /games/{gameId}/rounds
- /games/{gameId}/rounds/{roundId}/turns
- /games/{gameId}/decks
- /games/{gameId}/card-instances
- /games/{gameId}/card-locations
- /games/{gameId}/actions
- /games/{gameId}/score
- /games/{gameId}/rules

---

## 6. Implementation Notes

### Recommended approach
- Keep the game rules in a service layer rather than in the API handlers directly
- Use a rule engine or domain service to evaluate legal moves and resolve effects
- Store each event as data in the database so the game can be reconstructed later

### Recommended first version scope
- Two-player local play
- Hit and Stay actions
- Number card scoring
- Bust detection
- Flip 7 bonus
- Basic action card support
- Score accumulation
