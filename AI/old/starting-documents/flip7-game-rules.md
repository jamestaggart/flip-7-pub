# Flip 7 Game Rules Reference

This document captures the rules from the supplied Flip 7 rules text in a structured, comprehensive format. It is designed to be used as a reference for implementation, database design, or game logic.

---

## 1. Game Overview

### 1.1 Game Name
- Flip 7
- Also referred to in the rules as a press-your-luck card game

### 1.2 Players
- Minimum players: 3
- Recommended players: 3+
- The rules mention that the game is intended for 3 or more players

### 1.3 Components
- 94-card deck
- Pen and paper for score tracking
- Optional printable scoresheets, scoring app, or video reference

### 1.4 Deck Composition
- The deck contains number cards, score modifier cards, and action cards
- The rules describe a special deck where the number cards include values from 0 through 12
- The number cards are used to build a player’s score line
- Action and modifier cards are used to affect the round, but do not count toward the 7-card bonus

### 1.5 Core Theme
- Players race to reach 200 points
- Players can choose to keep taking risks for more points or stop before busting
- The game is a press-your-luck style experience

---

## 2. Objective of the Game

### 2.1 Primary Goal
- Be the first player to score 200 points to win the game

### 2.2 How Players Score
- Players score points based on the total number value of the cards in front of them
- The more valuable a card is, the more copies of that card appear in the deck

### 2.3 Flip 7 Bonus
- If a player successfully flips 7 unique number cards into their line, they automatically end the round for everyone
- This also grants 15 bonus points

### 2.4 Bust Rule
- If a player ever draws a second card with the same number as one already in their line, they bust
- A busted player is out of the round and scores nothing for that round

### 2.5 Important Reminder
- Action cards and modifier cards do not count toward the seven-card bonus
- The only way to achieve the Flip 7 bonus is to have seven unique number cards face up in front of you

---

## 3. Setup

### 3.1 Preparation
- Have a pen and paper ready to track scores
- Shuffle the deck thoroughly
- Choose a player to be the Dealer for the round

### 3.2 Dealing the First Cards
- In turn order, the Dealer deals one card face up to each player, including themselves
- If an Action card is revealed during dealing, dealing pauses immediately so the Action card can be resolved
- After any Action cards are resolved, dealing resumes until every player has been dealt a card

### 3.3 Result of Initial Dealing
- Not every player will necessarily have a number card at this point
- Some players may have a number or modifier card, while others may have no cards at all
- Some players may end up with multiple cards depending on the Action cards revealed

### 3.4 Dealer’s Role After Dealing
- After the initial deal, the Dealer offers each player in turn the option to Hit or Stay

---

## 4. Turn Structure

### 4.1 Player Options
- On a turn, a player may choose to Hit or Stay
- Hit means the player takes another card
- Stay means the player exits the round and banks their points

### 4.2 Hit Action
- If a player Hits, they add cards to their row of number cards and place modifier cards above them as shown in the rules
- A player may Stay as long as they have a card in front of them

### 4.3 Active Player Definition
- An active player is any player who has not busted and has not chosen to Stay
- Action cards may be played on active players

### 4.4 If You Are the Only Active Player
- If you are the only active player in the round, any Action card that must be played must be applied to yourself

---

## 5. Number Cards

### 5.1 Number Card Values
- The number cards include values from 0 through 12
- The zero is a number card worth no points
- The zero still increases the chance of earning the 7-card bonus

### 5.2 Number Card Distribution
- The rules describe a descending frequency pattern for the number cards, with higher numbers appearing more often
- The card counts are used to reflect the relative value and frequency of each number

### 5.3 Busting on Duplicate Numbers
- If a player draws a second card with the same number as one already in their line, the player busts immediately
- Busting removes the player from the round and they score nothing for that round

### 5.4 Example
- Example score: 11 + 5 + 12 = 28 points
- With a +4 modifier: 32 points

---

## 6. Action Cards

### 6.1 General Rules for Action Cards
- Action cards can be played on any active player, including yourself
- They are placed above the player’s number cards

### 6.2 Freeze
- The player receiving a Freeze card banks all the points they have collected and is out of the round

### 6.3 Flip Three
- The player who receives a Flip Three card must accept the next three cards
- The cards are flipped one at a time
- The process stops if the player can Flip 7 number cards or the player busts
- The process continues until all three cards are drawn or until one of the stop conditions happens

### 6.4 Flip Three and Other Cards
- All number cards, action cards, and modifier cards count toward the three cards needed for the Flip Three effect
- If a Second Chance card is revealed during this process, it may be set aside and used later
- If another Flip Three or Freeze card is revealed during the process, they are resolved after all three cards are drawn, but only if the player has not already busted

---

## 7. Second Chance Card

### 7.1 General Rule
- The Second Chance card is kept by the player who receives it

### 7.2 How It Works
- If the player with a Second Chance card is dealt another card with the same number as one already in their line, the Second Chance card and the duplicate number card are both discarded

### 7.3 Limitation
- A player may only have one Second Chance card in front of them at a time

### 7.4 If Another Second Chance Is Drawn
- If a player is dealt another Second Chance card while they already have one, they must choose another active player to give the new Second Chance card to
- If there are no other active players, or everyone else already has one, the Second Chance card is discarded

### 7.5 End of Round Discard Rule
- All Second Chance cards are discarded at the end of the round even if they were never used
- This includes cases where the player who drew the card later received a Freeze card or successfully achieved the Flip 7 bonus

---

## 8. Modifier Cards

### 8.1 General Rule
- Modifier cards are not number cards
- Modifier cards do not count toward achieving a Flip 7 bonus
- You cannot bust on modifier cards

### 8.2 Ending a Turn with Only Modifier Cards
- A player may end their turn with just a modifier card and no number cards
- In that case, they still score the modifier value unless the modifier is an x2 card

### 8.3 Score Modifier Types
- +2 to +10 cards add the shown amount to the sum of the player’s number cards
- x2 cards double the score for all of the player’s number cards

### 8.4 Applying x2 Modifiers
- First, multiply the sum of the number cards by 2
- Then add any additional modifier cards

### 8.5 Example
- If a player has a number card total of 28 and a +4 modifier, the round score becomes 32
- If a player has a number card total and an x2 modifier, the number-card total is doubled before any additional modifier bonuses are applied

---

## 9. End of a Round

### 9.1 Round End Conditions
- A round continues until one of two end conditions is met:
  1. No active players remain because all players have either busted or chosen to Stay
  2. One player successfully flips 7 unique number cards and ends the round immediately

### 9.2 Marking Inactive Players
- To mark yourself as an inactive player, flip your cards over until the round is over

### 9.3 Scoring a Round
- Calculate scores as follows:
  1. Add the value of the number cards
  2. If the player has an x2 multiplier, double the score for the round
  3. Add any additional bonus points from modifier cards
  4. If the player achieved Flip 7 number cards, add 15 more points

### 9.4 Result of Flip 7
- If a player successfully flips 7 unique number cards, they end the round for everyone and score 15 bonus points

---

## 10. Starting the Next Round

### 10.1 Discarding Used Cards
- Set all cards from the round to the side
- Do not shuffle them back into the deck

### 10.2 Passing the Deck
- Pass the remaining cards in the deck to the left
- The player receiving the deck becomes the new Dealer

### 10.3 Reshuffling the Deck
- When the deck runs out, shuffle all the discarded cards to form a new deck

### 10.4 Mid-Round Reshuffle Rule
- If a reshuffle is needed mid-round, leave all cards in front of players where they are
- This remains true even if a player has busted and is out of the round

---

## 11. End of the Game

### 11.1 Winning Condition
- At the end of a round, when at least one player reaches 200 points, the player with the most points wins

### 11.2 Tie Handling
- The supplied rules do not define a separate tie-break rule
- A house rule may be needed if two or more players finish tied at 200 or above

---

## 12. Rule Notes and Clarifications

### 12.1 Action and Modifier Cards
- Action and modifier cards do not count toward the 7-card bonus
- Only seven unique number cards count toward the Flip 7 bonus

### 12.2 Card Count Awareness
- The rules emphasize keeping the card count in mind while playing
- The deck contains a large number of number cards as well as a smaller set of modifier and action cards

### 12.3 Special Handling of the Zero Card
- The zero card is treated as a number card worth zero points
- It still helps a player reach the 7-card bonus because it is a unique number card

---

## 13. Example Scenarios

### 13.1 Example Turn
- A player chooses to Hit and draws a number card
- If the number is already present in their line, they bust
- If the number is new, it remains in their line and the turn continues

### 13.2 Example Flip Three Resolution
- A player receives a Flip Three card
- The next three cards are drawn one at a time
- The process stops if the player busts or reaches 7 unique number cards

### 13.3 Example Scoring
- If a player has the number card total 11 + 5 + 12 = 28
- With a +4 modifier, the score becomes 32
- If the player also achieved Flip 7, they add 15 more points

---

## 14. Implementation Summary

### 14.1 Core Game State
- Players
- Current round
- Current turn order
- Each player’s line of cards
- Active/inactive status
- Current score totals
- Current deck and discard pile

### 14.2 Core Rules That Must Be Modeled
- Busting on duplicate numbers
- Flip 7 bonus and 15-point reward
- Action card resolution
- Modifier card scoring
- End of round after no active players or Flip 7
- Reshuffle and dealer rotation

---

## 15. Rule Inventory Checklist

- [x] Objective
- [x] Setup
- [x] Turn order
- [x] Card effects
- [x] Flip mechanics
- [x] Player interactions
- [x] Scoring
- [x] End condition
- [x] Edge cases
- [x] Examples
