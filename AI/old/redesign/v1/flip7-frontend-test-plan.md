# Flip 7 Frontend Test Plan

This document lists frontend tests for the Flip 7 game based on the user stories in the frontend design document. Each test is written to verify that the user-facing experience works correctly for a couch co-op, turn-based version of the game.

---

## 1. Test Strategy

### 1.1 Goal
Verify that the frontend supports the full gameplay experience from setup to victory while matching the game rules and API expectations.

### 1.2 Coverage Areas
- game setup and player entry
- turn flow and player actions
- card display and state updates
- action card resolution
- scoring and round progression
- game end and replay flow

---

## 2. Test Cases by User Story

### Redesign Flow Stories

#### US-20: Configure a match from the redesigned setup shell
- Given a player opens the app
- When they add a username, select the active player, set a target score, and create a game
- Then the setup panel updates the player list and the app transitions into the board experience

#### US-21: Follow the active game from a board-first experience
- Given a game is active
- When the user views the main board
- Then the hero metrics, turn banner, round status, deck count, and player panels are visible and up to date

#### US-22: Resolve turns from the shared action panel
- Given it is the active player’s turn
- When they choose Hit, Stay, Freeze Target, or Flip Three Target
- Then the action panel remains usable, the feedback banner updates, and the board reflects the outcome

#### US-23: Review round summaries and match results without losing context
- Given a round ends or the match is complete
- When the overlay appears
- Then the summary or winner details are shown and the user can continue to the next round, replay, or start a new game

### US-01: Start a New Game

#### Test: Start game from the home screen
- Given the player opens the app
- When they click “New Game”
- Then a new game session is created
- And the game screen is shown
- And the player is placed into the new game

#### Test: Show loading state while the game is being created
- Given the player clicks “New Game”
- When the API request is pending
- Then the UI shows a loading or busy state
- And the player is not left in a broken or empty screen

---

### US-02: Join a Game

#### Test: Join an existing game from a game code or selection screen
- Given a pending game exists
- When the player enters the correct game identifier
- Then the app calls the join-game API
- And the player is added to the game
- And the game screen appears

#### Test: Show error for an invalid game identifier
- Given a player enters an invalid or missing game code
- When they attempt to join
- Then the app shows an error message
- And the game is not entered

---

### US-03: Add Players to the Match

#### Test: Allow both players to be added before the match starts
- Given the game is in setup
- When both players are added
- Then the UI shows both players as ready or present
- And the game can begin

#### Test: Prevent starting the match with only one player
- Given only one player has been added
- When the user attempts to start the match
- Then the UI blocks the start
- And it explains that a second player is required

---

### US-04: See Whose Turn It Is

#### Test: Highlight the active player clearly
- Given the game has started
- When the turn changes
- Then the active player is visually highlighted
- And the turn indicator updates immediately

#### Test: Show the turn order clearly
- Given the game is in progress
- When the user views the screen
- Then the current turn and turn order are obvious

---

### US-05: Choose to Hit

#### Test: Hit button triggers a draw action
- Given it is the current player’s turn
- When the player clicks “Hit”
- Then the app calls the hit API
- And the drawn card is shown in the player’s display area

#### Test: Show the result of the hit immediately
- Given a hit action resolves
- When the API returns a result
- Then the UI updates the score or bust state appropriately
- And the next turn state is shown

#### Test: Prevent hitting when the player is inactive
- Given the player is not active for the round
- When they try to hit
- Then the action is blocked
- And the UI shows the player cannot act

---

### US-06: Choose to Stay

#### Test: Stay button makes the player inactive
- Given it is the current player’s turn
- When the player clicks “Stay”
- Then the player becomes inactive for the round
- And the UI updates the player’s state

#### Test: Move to the next active player after a stay
- Given a stay action is processed
- When the round continues
- Then the next active player becomes the current turn holder

---

### US-07: Understand Risk Before Acting

#### Test: Show current number-card value and risk state
- Given a player has collected cards
- When they view their board state
- Then the UI shows their current score line and any duplicate risk

#### Test: Warn the player if a duplicate number would bust them
- Given the player is about to draw a duplicate number
- When the next action is evaluated
- Then the UI makes it clear that this would cause a bust

---

### US-08: View My Cards

#### Test: Display the player’s cards in the player area
- Given a player has cards in front of them
- When the game screen is shown
- Then the cards appear in their assigned area

#### Test: Distinguish number, modifier, and action cards visually
- Given a player has different card types
- When the cards are displayed
- Then each type is visually represented clearly

---

### US-09: See the Current Card State

#### Test: Update card display after each move
- Given a player draws or resolves a card
- When the state updates
- Then the displayed cards change correctly

#### Test: Show cards for both players in the shared view
- Given the game is in progress
- When both players have cards in play
- Then each player’s card line is visible in the correct area

---

### US-10: See the Deck Status

#### Test: Display remaining deck count
- Given the game has started
- When the user views the game screen
- Then the remaining deck count is shown

#### Test: Update deck count after each draw
- Given a card is drawn
- When the action resolves
- Then the deck count decreases appropriately

---

### US-11: Resolve a Freeze Card

#### Test: Display Freeze effect clearly
- Given a Freeze card is applied
- When the effect resolves
- Then the UI shows the affected player is frozen or removed from play

#### Test: Show the reason for the round change
- Given a Freeze card affects a player
- When the player views the screen
- Then the effect explanation is visible in the action panel

---

### US-12: Resolve a Flip Three Card

#### Test: Show the Flip Three resolution flow
- Given a Flip Three card is applied
- When the three-card sequence begins
- Then the UI shows the sequence and progression clearly

#### Test: Stop the sequence when the player busts
- Given the player busts during the Flip Three sequence
- When the sequence resolves
- Then the UI stops the flow and shows the bust result

#### Test: Stop the sequence when the player reaches Flip 7
- Given the player gets 7 unique number cards during the sequence
- When the sequence resolves
- Then the UI ends the round and shows the Flip 7 result

---

### US-13: Use a Second Chance Card

#### Test: Show when Second Chance is active
- Given a player holds a Second Chance card
- When the game state is displayed
- Then the card is visible and marked as active

#### Test: Show that Second Chance prevented a bust
- Given a duplicate number would normally bust the player
- When the Second Chance card is used
- Then the UI shows that the duplicate was neutralized

---

### US-14: See My Current Round Score

#### Test: Display the current round score
- Given a player has accumulated cards and modifiers
- When the UI renders the game screen
- Then the round score is displayed accurately

#### Test: Update the round score after a new card is drawn
- Given a new card is resolved
- When the score changes
- Then the displayed round score updates

---

### US-15: See My Total Score Across Rounds

#### Test: Display cumulative scores after each round
- Given a round ends
- When the score summary is shown
- Then each player’s total score is updated correctly

#### Test: Show progress toward the 200-point goal
- Given a player is close to 200 points
- When the scoreboard is displayed
- Then the progress bar or score text reflects the current total

---

### US-16: See the Flip 7 Bonus

#### Test: Show the Flip 7 bonus when earned
- Given a player achieves 7 unique number cards
- When the round resolves
- Then the UI shows a Flip 7 bonus message and value

#### Test: Show the bonus in the score summary
- Given a round ends with Flip 7
- When the summary is shown
- Then the bonus points are included in the total

---

### US-17: See the Round End Reason

#### Test: Show why the round ended
- Given the round reaches an end condition
- When the summary is shown
- Then the reason is displayed clearly

#### Test: Show the correct end reason for no active players
- Given all players are inactive or busted
- When the round ends
- Then the UI states that no active players remain

---

### US-18: Start the Next Round

#### Test: Show a next-round prompt after round end
- Given a round has ended
- When the summary is visible
- Then the user sees a clear option to continue to the next round

#### Test: Continue smoothly to the next round
- Given the player clicks “Next Round”
- When the next round begins
- Then the scoreboard and turn state reset appropriately for the new round

---

### US-19: See Who Wins the Match

#### Test: Announce the match winner
- Given a player reaches 200 points or more at the end of a round
- When the game resolves
- Then the UI displays the winner and final totals

#### Test: Offer replay or new match options
- Given the match is over
- When the winner screen appears
- Then the user can choose to replay or start a new game

---

## 3. Cross-Cutting UI Tests

### Test: Handle API loading and failure states
- Given an API request is slow or fails
- When the frontend is loading game data
- Then the user receives a non-blocking error or retry option

### Test: Ensure the UI reflects backend state immediately
- Given the backend updates the game state
- When the frontend re-renders
- Then the visible state matches the real game state

### Test: Prevent duplicate interactions during processing
- Given a user double-clicks a button
- When the request is still processing
- Then the UI prevents duplicate submissions or disables the control

---

## 4. Recommended Test Tools

- Playwright for end-to-end browser testing
- Vitest or Jest for component-level tests
- Testing Library for DOM interaction and accessibility checks

---

## 5. Suggested Priorities

### Highest Priority
- turn flow
- hit/stay actions
- bust and Flip 7 outcomes
- score display
- round summary and game over flow

### Medium Priority
- action card resolution
- Second Chance handling
- deck count and state updates

### Lower Priority
- polish states and animations
- non-blocking error handling
