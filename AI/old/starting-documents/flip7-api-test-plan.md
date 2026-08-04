# Flip 7 API Test Plan

This document defines a test plan for the Flip 7 API surface. Each endpoint is listed with the behaviors it should support and the game rules from the rules document that apply to it.

The goal is to make sure the API enforces the core rules of the game and that every important rule is covered by at least one test case.

---

## 1. Test Strategy

### 1.1 Scope
This plan covers:
- game creation and player joining
- round and turn flow
- card dealing and movement
- hit and stay decisions
- busting and Flip 7 completion
- action card effects
- modifier scoring
- round end and game end

### 1.2 Test Principles
Each endpoint should be tested for:
- happy path behavior
- invalid input handling
- rule enforcement
- state persistence
- side effects on related records
- round and game progression

---

## 2. Player Endpoints

### POST /players

#### Purpose
Create a new player profile.

#### Rules Covered
- Player identity and score tracking
- Each player must be able to participate in a game

#### Test Cases
- Create a player with valid data
- Reject a duplicate username if uniqueness is enforced
- Reject missing required fields
- Ensure the player record is stored correctly

---

### GET /players/{playerId}

#### Purpose
Retrieve a player’s profile.

#### Rules Covered
- Player identity and score history

#### Test Cases
- Return the correct player profile
- Return 404 for a non-existent player

---

## 3. Game Endpoints

### POST /games

#### Purpose
Create a new game session.

#### Rules Covered
- Game setup and round-based structure
- The game begins with a game session and players can be added

#### Test Cases
- Create a game with a valid creator
- Default status is set correctly
- Reject invalid creator input

---

### GET /games/{gameId}

#### Purpose
Retrieve game state.

#### Rules Covered
- Current game status and round progression

#### Test Cases
- Return the correct game metadata
- Return 404 for a missing game
- Report the current status accurately

---

### POST /games/{gameId}/players

#### Purpose
Add a player to a game.

#### Rules Covered
- Game setup
- A player must be associated with a specific game instance

#### Test Cases
- Add a player successfully
- Reject duplicate player-seat assignment
- Reject joining a finished game
- Ensure game_players records are created correctly

---

## 4. Round Endpoints

### POST /games/{gameId}/rounds

#### Purpose
Start a new round.

#### Rules Covered
- Round lifecycle
- Dealer rotation and round progression

#### Test Cases
- Create a round for an active game
- Increment round number correctly
- Reject creating a round for a finished game
- Initialize the round with the correct starting player

---

### GET /games/{gameId}/rounds/{roundId}

#### Purpose
Retrieve round details.

#### Rules Covered
- Current round state
- Active/inactive players

#### Test Cases
- Return the round metadata
- Include the current active players
- Return 404 for a missing round

---

## 5. Turn Endpoints

### POST /games/{gameId}/rounds/{roundId}/turns

#### Purpose
Start a new turn.

#### Rules Covered
- Turn structure
- The active player takes a turn in sequence

#### Test Cases
- Start a turn for the correct active player
- Reject starting a turn for a player who is already inactive
- Record the turn number correctly

---

### PATCH /games/{gameId}/rounds/{roundId}/turns/{turnId}

#### Purpose
End a turn.

#### Rules Covered
- Turn completion
- Result summary storage

#### Test Cases
- Mark a turn complete
- Store a result summary
- Reject ending a turn that has already been completed

---

## 6. Deck and Card Endpoints

### POST /games/{gameId}/decks

#### Purpose
Create a deck for a game.

#### Rules Covered
- Deck setup and card distribution

#### Test Cases
- Create a main deck successfully
- Reject invalid deck type
- Ensure deck is associated with the correct game

---

### POST /games/{gameId}/card-instances

#### Purpose
Create a physical card instance.

#### Rules Covered
- Card instances represent the actual cards in play

#### Test Cases
- Create a card instance from a card definition
- Associate it with the correct deck and game
- Reject invalid card definition input

---

### POST /games/{gameId}/card-locations

#### Purpose
Record the current location of a card.

#### Rules Covered
- Card placement in a hand, line, discard pile, play area, or removed state

#### Test Cases
- Move a card to a player’s line
- Move a card to the discard pile
- Update a card from face-down to face-up correctly
- Reject invalid zone types

---

### PATCH /games/{gameId}/card-locations/{cardInstanceId}

#### Purpose
Update a card’s location.

#### Rules Covered
- Card movement over time
- Cards can change zones as the round progresses

#### Test Cases
- Move a card to a new zone
- Update ownership correctly
- Update face-up state
- Reject a card update for a non-existent game card

---

## 7. Hit and Stay Endpoints

### POST /games/{gameId}/rounds/{roundId}/actions/hit

#### Purpose
Handle the Hit action.

#### Rules Covered
- Players may choose to Hit to receive another card
- If a player draws a card with the same number as one already in their line, they bust
- If a player reaches 7 unique number cards, the round ends immediately

#### Test Cases
- Draw a new card successfully
- Add the card to the player’s line
- Detect a duplicate number and mark the player as busted
- Detect a duplicate number with a Second Chance card and apply the rule correctly
- Detect that the player has reached 7 unique number cards and end the round
- Prevent a player from hitting if they are not active

---

### POST /games/{gameId}/rounds/{roundId}/actions/stay

#### Purpose
Handle the Stay action.

#### Rules Covered
- A player may Stay as long as they have a card in front of them
- Staying makes the player inactive for the round

#### Test Cases
- Mark the player as inactive when they stay
- Reject staying if the player has no cards in front of them
- Ensure the next active player becomes the current turn holder if applicable

---

## 8. Bust and Round-End Endpoints

### POST /games/{gameId}/rounds/{roundId}/actions/bust

#### Purpose
Mark a player as busted.

#### Rules Covered
- A busted player is out of the round and scores nothing for that round

#### Test Cases
- Bust a player successfully
- Ensure the player is removed from active play
- Ensure the player’s round score is set to zero or excluded from scoring
- Reject busting an already inactive player

---

### POST /games/{gameId}/rounds/{roundId}/actions/flip-seven

#### Purpose
Resolve the Flip 7 bonus.

#### Rules Covered
- A player with 7 unique number cards ends the round immediately
- The player gets 15 bonus points

#### Test Cases
- Award the Flip 7 bonus when the player has 7 unique number cards
- End the round immediately for everyone
- Reject the action if the player does not meet the condition

---

### POST /games/{gameId}/rounds/{roundId}/end-check

#### Purpose
Check whether the round should end.

#### Rules Covered
- Round ends when no active players remain or a player achieves Flip 7

#### Test Cases
- End the round when all players are inactive or busted
- End the round when Flip 7 is achieved
- Do not end the round while players remain active

---

## 9. Action Card Endpoints

### POST /games/{gameId}/rounds/{roundId}/actions

#### Purpose
Record an action card effect.

#### Rules Covered
- Action cards can be played on active players
- If the active player is the only player left, the card applies to themselves

#### Test Cases
- Apply Freeze to an active player
- Apply Flip Three to an active player
- Reject applying an action card to an inactive player
- If only one active player remains, apply the card to that player automatically

---

### POST /games/{gameId}/rounds/{roundId}/actions/freeze

#### Purpose
Apply the Freeze action.

#### Rules Covered
- Freeze banks the player’s points and removes them from the round

#### Test Cases
- Freeze a player successfully
- Ensure the frozen player is no longer active
- Ensure the player’s current points are banked correctly

---

### POST /games/{gameId}/rounds/{roundId}/actions/flip-three

#### Purpose
Handle the Flip Three action.

#### Rules Covered
- The next three cards are resolved one at a time
- The process stops if the player busts or reaches 7 unique numbers
- Action and modifier cards count toward the three-card process
- Second Chance may be set aside and used
- Another Flip Three or Freeze card is resolved after all three cards are drawn if the player has not busted

#### Test Cases
- Draw three cards in sequence
- Stop early if the player busts
- Stop early if the player reaches 7 unique numbers
- Count action and modifier cards toward the three-card process
- Resolve a nested Flip Three or Freeze card after the three-card sequence when applicable
- Apply Second Chance during the sequence if triggered

---

## 10. Second Chance Endpoints

### POST /games/{gameId}/rounds/{roundId}/actions/second-chance

#### Purpose
Manage the Second Chance card.

#### Rules Covered
- A player may only hold one Second Chance card at a time
- If the same number is drawn again, the Second Chance card and duplicate are discarded
- If another Second Chance is received, it may be passed to another active player
- All Second Chance cards are discarded at the end of the round

#### Test Cases
- Give a player a Second Chance card
- Discard both the Second Chance and the duplicate number card when a duplicate is drawn
- Reject giving a player a second Second Chance card while they already hold one
- Pass a new Second Chance card to another active player when applicable
- Clear all Second Chance cards at round end

---

## 11. Scoring Endpoints

### POST /games/{gameId}/rounds/{roundId}/score/calculate

#### Purpose
Calculate the round score for a player.

#### Rules Covered
- Number cards are added together
- x2 multiplier doubles the number card total
- Additional modifiers add points
- Flip 7 gives 15 bonus points

#### Test Cases
- Calculate a score from number cards only
- Apply a +4 modifier correctly
- Apply an x2 modifier correctly
- Apply both modifiers correctly in the correct order
- Add the 15-point Flip 7 bonus when applicable

---

### POST /games/{gameId}/rounds/{roundId}/score/apply

#### Purpose
Store the round score into cumulative totals.

#### Rules Covered
- Scores are carried forward across rounds

#### Test Cases
- Apply a round score to the player’s total
- Prevent double-counting a score if applied twice

---

### GET /games/{gameId}/results

#### Purpose
Return score results for the game.

#### Rules Covered
- End of game winner determination

#### Test Cases
- Return the highest score at game end
- Return tie information if relevant
- Report winner clearly when one player reaches 200 points

---

## 12. Rule Enforcement and Validation Tests

### Generic Validation Cases
For every mutation endpoint:
- reject invalid player IDs
- reject actions from inactive players
- reject actions during a finished game or round
- ensure state changes are persisted atomically
- ensure related tables are updated correctly

---

## 13. Recommended Test Cases by Priority

### High Priority
- hit causes bust correctly
- hit can trigger Flip 7
- stay makes a player inactive
- Freeze removes a player from the round
- Flip Three draws three cards and stops appropriately
- Second Chance prevents bust when a duplicate appears
- scoring adds modifiers and Flip 7 bonus correctly

### Medium Priority
- round end occurs when no active players remain
- reshuffle and dealer rotation behavior
- multi-turn progression across consecutive rounds

### Lower Priority
- edge cases around duplicate action cards
- tie handling at game end
- optional house-rule behavior
