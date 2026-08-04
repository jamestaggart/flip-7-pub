# API Reference Examples (Live Responses)

These examples were captured from live calls against the local Docker backend.

Base URL: http://127.0.0.1:8000/api

## Create Player

Request:

```http
POST /api/players/
Content-Type: application/json

{"username":"api-doc-1785612878","display_name":"api-doc-1785612878"}
```

Response:

```json
{"id":43,"username":"api-doc-1785612878","display_name":"api-doc-1785612878","created_at":"2026-08-01T19:34:38.343700Z"}
```

## Create Game

Request:

```http
POST /api/games/create/
Content-Type: application/json

{"created_by":43}
```

Response:

```json
{"id":7,"game_code":"FLIP5945","status":"pending","started_at":null,"finished_at":null,"ruleset_version":"v1","created_at":"2026-08-01T19:34:38.469176Z","created_by":43}
```

## Start Round

Request:

```http
POST /api/games/7/start_round/
Content-Type: application/json
```

Response (truncated):

```json
{"round_id":1,"turn_id":1,"state":{"game_id":7,"game_code":"FLIP5945","status":"active","round_id":1,"current_turn":43}}
```

## Validate Rule Action

Request:

```http
POST /api/games/7/rules/validate/
Content-Type: application/json

{"action_type":"hit","player_id":43}
```

Response:

```json
{"valid":true,"reason":"Action is valid","round_id":1,"player_id":43}
```

## Calculate Round Score

Request:

```http
POST /api/games/7/rounds/1/score/calculate/
Content-Type: application/json

{"player_id":43}
```

Response:

```json
{"player_id":43,"number_subtotal":0,"multiplier":1,"modifier_total":0,"bonus_points":0,"unique_numbers":0,"final_score":0}
```

## Resolve Rule Action

Request:

```http
POST /api/games/7/rules/resolve/
Content-Type: application/json

{"action_type":"stay","payload":{"player_id":43}}
```

Response (truncated):

```json
{"game_id":7,"round_id":1,"action_type":"stay","actor_player_id":43,"outcome":{"round_ended":true,"message":"No active players remain"},"round_ended":true}
```

## Get Game Results

Request:

```http
GET /api/games/7/results/
```

Response:

```json
{"game_id":7,"status":"active","winner":{"player_id":43,"username":"api-doc-1785612878","seat_number":1,"total_score":0,"is_busted":false},"standings":[{"player_id":43,"username":"api-doc-1785612878","seat_number":1,"total_score":0,"is_busted":false}]}
```
