# Flip 7 Frontend Design Document

This document describes the frontend experience for a couch co-op, turn-based Flip 7 game that uses the API design already defined for the game engine.

The frontend should make the game feel simple, social, and readable while still supporting the full rules of the card game.

---

## 1. Product Goals for the Frontend

The frontend should:

- let two players sit next to each other and play comfortably on one screen
- make the current game state easy to understand at a glance
- support the full game flow from setup through scoring and game end
- guide players through turns without requiring them to understand the backend rules
- make risky choices feel exciting and clear

---

## 2. Core User Experience

### 2.1 Primary Persona
- Two local players playing on one device or shared screen
- One player acts as the current player, while the other watches and reacts
- Players want a fast, friendly, low-friction experience

### 2.2 Experience Goals
- The game should feel intuitive within the first minute
- The active player should know exactly what choices they have
- The other player should understand the state of the round without confusion
- The game should feel social and playful, not overly technical

---

## 3. User Stories

### 3.0 Redesign Flow Stories

#### US-20: Configure a match from the redesigned setup shell
As a local host, I want to add players, choose the active player, and set the target score from the setup panel so I can start a match quickly.

Acceptance criteria:
- The setup shell shows a clear player entry field, active player selector, target score input, and create-game control.
- Adding a player updates the roster immediately and keeps the selected player in sync.
- Creating a game transitions the interface into the board-first experience with live game state.

#### US-21: Follow the active game from a board-first experience
As a player, I want the main board to show the current round, deck count, turn, and player state at a glance so I can understand the match without reading the API.

Acceptance criteria:
- The hero and board sections display the current status, round, target score, and deck count.
- Each player panel shows round score, total score, unique-number risk, cards, and active status.
- The current turn is visually distinct and the board updates after each action.

#### US-22: Resolve turns from the shared action panel
As a player, I want clear turn controls and visible feedback so I know what action I can take and what happened after I act.

Acceptance criteria:
- The turn controls present the available actions in a prominent panel with clear labels and helpers.
- Action results are announced in the feedback banner and reflected in the board state.
- The UI disables or re-enables controls appropriately while an action is processing.

#### US-23: Review round summaries and match results without losing context
As a player, I want round-summary and game-over overlays to explain the outcome and offer clear next steps so the flow feels continuous.

Acceptance criteria:
- A round-summary overlay shows the result for each player and a clear next-round action.
- A game-over overlay announces the winner, shows final standings, and offers replay or new-game options.
- The overlays trap focus, support keyboard dismissal, and restore the board context when closed.

### 3.1 Game Setup Stories

#### US-01: Start a New Game
As a player, I want to start a new game so I can begin a fresh match with another player.

Acceptance criteria:
- A user can tap or click “New Game”
- The app creates a new game session through the API
- The player is assigned as the creator of the game
- The game screen appears immediately

#### US-02: Join a Game
As a player, I want to join an existing game so I can play with someone already waiting.

Acceptance criteria:
- A player can enter a game code or select a pending game
- The app calls the join game API
- The UI updates to show that the player has joined

#### US-03: Add Players to the Match
As a host, I want to add another local player to the game so a two-player match can begin.

Acceptance criteria:
- The app shows a player setup step before the game starts
- Both players can be added successfully
- The game can begin once both players are present

---

### 3.2 Round and Turn Stories

#### US-04: See Whose Turn It Is
As a player, I want to clearly see whose turn it is so I know when I need to act.

Acceptance criteria:
- The active player is visually highlighted
- The current turn is displayed in a prominent area
- The UI updates when the turn changes

#### US-05: Choose to Hit
As a player, I want to choose Hit so I can draw another card and build my score.

Acceptance criteria:
- The player can press a “Hit” button on their turn
- The app calls the hit API endpoint
- The UI shows the drawn card and any resulting change in score or bust state

#### US-06: Choose to Stay
As a player, I want to choose Stay so I can stop taking risks and bank my points.

Acceptance criteria:
- The player can press a “Stay” button
- The app calls the stay API endpoint
- The player becomes inactive for the round
- The turn moves to the next active player or round end state

#### US-07: Understand Risk Before Acting
As a player, I want to understand how close I am to busting so I can make a smarter decision.

Acceptance criteria:
- The UI shows my current number-card values and duplicate risk
- The app clearly displays whether the next draw would bust me
- The player can see the state of their line before making a choice

---

### 3.3 Card and Deck Stories

#### US-08: View My Cards
As a player, I want to see the cards I have accumulated so I can understand my current position.

Acceptance criteria:
- The UI shows the player’s number cards, modifiers, and action cards
- Cards are displayed in a clear row or grouping
- The player can tell which cards are active in the current round

#### US-09: See the Current Card State
As a player, I want to see the current card state in the game so I know what happened during the round.

Acceptance criteria:
- The UI displays the cards in play for each player
- The game board updates after each action
- The player can distinguish between number cards, modifier cards, and action cards

#### US-10: See the Deck Status
As a player, I want to know how many cards remain in the deck so I can judge the game’s pace.

Acceptance criteria:
- The UI displays the remaining deck size or a simple count
- The count updates after each draw and reshuffle

---

### 3.4 Action Card Stories

#### US-11: Resolve a Freeze Card
As a player, I want to understand when a Freeze card is applied so I know why the round changed.

Acceptance criteria:
- When Freeze is played, the UI shows the effect clearly
- The affected player is visually marked as frozen or removed from active play
- The next state of the round is displayed immediately

#### US-12: Resolve a Flip Three Card
As a player, I want to see the result of a Flip Three card so I understand what happened to my turn.

Acceptance criteria:
- The UI shows the three-card sequence as it resolves
- Each drawn card is shown one by one or as a summary
- The result is clear if the player busts or reaches Flip 7

#### US-13: Use a Second Chance Card
As a player, I want to know when a Second Chance card helps me so I can understand the round state.

Acceptance criteria:
- The UI shows when Second Chance is active
- If a duplicate number is drawn, the UI explains that the Second Chance prevented busting
- The effect is reflected in the player’s displayed cards

---

### 3.5 Scoring Stories

#### US-14: See My Current Round Score
As a player, I want to see my round score so I know whether to keep taking risks.

Acceptance criteria:
- The UI displays the current round score for each player
- The score updates after each card or modifier effect
- The UI shows whether the score includes modifiers or multipliers

#### US-15: See My Total Score Across Rounds
As a player, I want to see my cumulative score so I know how close I am to winning the game.

Acceptance criteria:
- The app shows each player’s total score across rounds
- The total updates after each round ends
- The UI shows the target win threshold of 200 points

#### US-16: See the Flip 7 Bonus
As a player, I want to know when I earned the Flip 7 bonus so I understand the reward for my play.

Acceptance criteria:
- The UI clearly indicates when a player achieved Flip 7
- The bonus value is displayed
- The round end state is shown immediately

---

### 3.6 End-of-Round and End-of-Game Stories

#### US-17: See the Round End Reason
As a player, I want to know why the round ended so I understand the outcome.

Acceptance criteria:
- The UI shows whether the round ended due to no active players or Flip 7
- The reason is displayed in an end-of-round summary

#### US-18: Start the Next Round
As a player, I want to begin the next round easily so the game continues smoothly.

Acceptance criteria:
- A “Next Round” button or automatic transition appears after scoring
- The next dealer and round state are displayed
- The game continues without needing to reload

#### US-19: See Who Wins the Match
As a player, I want to know who wins the game so I can celebrate or play again.

Acceptance criteria:
- The UI announces the winner when a player reaches 200 points
- The final score summary is shown
- A replay option is available

---

## 4. Screen Requirements

### 4.1 Main Game Screen
The main game screen should include:
- player one area
- player two area
- current turn indicator
- score summary
- action buttons for Hit and Stay
- round status message
- deck count and round state

### 4.2 Round Summary Overlay
After a round ends, the UI should show:
- the winning or busting player
- the round score breakdown
- the reason the round ended
- a button to continue to the next round

### 4.3 Game Over Screen
At the end of the match, the UI should show:
- winner name or player label
- final totals
- replay button
- new game button

---

## 5. Component Map

### 5.1 Core Components
- App shell
- Game setup screen
- Player card area
- Turn control panel
- Scoreboard
- Card display area
- Action result panel
- Round summary modal
- Game over screen

### 5.2 Stateful UI Pieces
- current turn
- active player status
- player hand / line cards
- round score breakdown
- deck count
- round outcome banner
- winner banner

---

## 6. API Mapping to Frontend Features

The frontend should consume the following API areas:

- player creation and lookup
- game creation and joining
- round and turn lifecycle
- card creation and movement
- hit and stay actions
- action card resolution
- score calculation and application
- game result retrieval

This ensures the frontend can reflect the full game rules without adding logic that should live in the backend.

---

## 7. Functional Requirements for the UI

### 7.1 Required Functionalities
- create a game
- join a game
- display the current player and turn state
- show cards in each player’s line
- allow hit/stay actions
- show bust and Flip 7 outcomes
- display action card effects
- show score changes and totals
- show round end and game end states

### 7.2 Non-Functional Requirements
- responsive enough for a TV or couch setup
- readable from a distance
- fast updates after each action
- clear visual distinction between card types
- minimal friction for local two-player use

---

## 8. MVP Scope

For the first version of the game, the frontend should support:
- two-player local play
- game creation and joining
- turn-based Hit/Stay flow
- card display for each player
- busting and Flip 7 outcomes
- modifier and action card effect display
- score tracking and round progression

---

## 9. Future Enhancements

Possible later additions:
- AI opponent mode
- online multiplayer
- animations for card draws and effects
- richer card art and visual polish
- sound effects and accessibility improvements
