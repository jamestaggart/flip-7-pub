# Flip 7 API Endpoint Audit

This document maps endpoints from the API design to the current implementation status.

## Coverage summary

- Implemented: core player, game, round, turn, card, action, scoring, and rules support endpoints.
- Partially implemented: endpoint path shapes differ from the design in some areas.
- Remaining: full nested path parity and complete action-card administration endpoints.

## Endpoint mapping

### Players

- Design: POST /players, GET /players/{playerId}, GET /players
- Implemented:
  - POST /api/players/
  - GET /api/players/{id}/
  - GET /api/players/
- Status: Implemented

### Games

- Design: POST /games, GET /games/{gameId}, GET /games, PATCH /games/{gameId}
- Implemented:
  - POST /api/games/create/ and POST /api/games/
  - GET /api/games/{id}/
  - GET /api/games/
  - PATCH /api/games/{id}/
- Status: Implemented (plus project-specific create shortcut)

### Join game

- Design: POST /games/{gameId}/players
- Implemented:
  - POST /api/games/{id}/join/
- Status: Implemented (path variant)

### Rounds

- Design: create/get/list round under game
- Implemented:
  - POST /api/games/{id}/start_round/
  - GET /api/rounds/{id}/
  - GET /api/rounds/
- Status: Implemented (path variant)

### Turns

- Design: start/get/end turn under round
- Implemented:
  - ModelViewSet CRUD at /api/turns/
  - Turn changes also produced by gameplay actions
- Status: Partially implemented (no strict nested path parity)

### Deck/cards/card locations

- Design: create/list/get and move/update location under game
- Implemented:
  - CRUD endpoints: /api/decks/, /api/card-instances/, /api/card-locations/
  - Player card state available in game state payload
- Status: Implemented (path variant)

### Action APIs

- Design: apply action card, flip-three, freeze, second-chance
- Implemented:
  - POST /api/games/{id}/freeze/
  - POST /api/games/{id}/flip_three/
  - POST /api/rounds/{id}/freeze/
  - POST /api/rounds/{id}/flip_three/
  - Second Chance logic integrated in hit/flip-three resolution
- Status: Implemented (second-chance as rule behavior rather than dedicated endpoint)

### Gameplay decision APIs

- Design: hit, stay, bust, flip-seven
- Implemented:
  - POST /api/games/{id}/hit/
  - POST /api/games/{id}/stay/
  - POST /api/rounds/{id}/actions/bust/
  - POST /api/rounds/{id}/actions/flip-seven/
- Status: Implemented

### Scoring APIs

- Design: calculate/apply/get results
- Implemented:
  - POST /api/games/{gameId}/rounds/{roundId}/score/calculate/
  - POST /api/games/{gameId}/rounds/{roundId}/score/apply/
  - GET /api/games/{id}/results/
- Status: Implemented

### Rule enforcement APIs

- Design: validate move, resolve turn effects, end-check
- Implemented:
  - POST /api/games/{id}/rules/validate/
  - POST /api/games/{id}/rules/resolve/
  - POST /api/games/{gameId}/rounds/{roundId}/end-check/
- Status: Implemented

## Notes

- Existing routes favor DRF ViewSet patterns plus explicit custom actions.
- The largest delta vs design is path naming style, not capability availability.
- Capabilities in this audit are validated by backend test suite and live endpoint calls.
