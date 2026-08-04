# Flip 7 Game Design Document

## 1. Product Vision

Flip 7 is a fast, social, couch co-op turn-based card game designed for two players sitting side by side. The experience should feel easy to learn, lively to play, and tense when the decision to hit or stay becomes risky.

The game should preserve the core press-your-luck tension of the original rules while adapting it for a local, shared-screen experience that is intuitive and fun for casual play.

---

## 2. Core Design Goals

### 2.1 Primary Goals
- Create a local two-player couch co-op experience
- Keep the game simple enough to learn in under a minute
- Preserve the excitement of the original Flip 7 rules
- Make decisions feel meaningful and high-stakes
- Support quick rounds with easy reset and replay

### 2.2 Secondary Goals
- Make the game feel polished and visually clear on a couch setup
- Support shared-screen play without requiring a keyboard-heavy interface
- Keep the game accessible to players of different skill levels
- Allow future expansion with AI, online play, or more game modes

---

## 3. Target Experience

### 3.1 Player Feel
Players should feel:
- excited when they take risks
- tense when they are close to busting
- rewarded for smart timing and bold choices
- engaged by the opponent’s decisions and reactions

### 3.2 Session Feel
A typical session should feel:
- short and replayable
- social and interactive
- easy to start
- satisfying to finish

---

## 4. Core Gameplay Pillars

### 4.1 Couch Co-op Turn-Based Play
- The game is designed for two players sitting next to each other
- Players take turns making decisions in a shared physical space
- The game should feel natural to play with one device, one screen, and one set of controls

### 4.2 Press-Your-Luck Tension
- Players are encouraged to keep drawing cards to build a stronger score
- But every extra card increases the risk of busting
- The tension should come from choosing when to stop and bank points

### 4.3 Simple Rules, High Drama
- The rules should be easy to understand
- The game should avoid unnecessary complexity in the interface
- The emotional impact should come from the card outcomes, not from menu overload

---

## 5. Game Loop

### 5.1 Round Structure
1. The game starts a new round
2. Each player is dealt an initial set of cards
3. Players take turns deciding whether to Hit or Stay
4. Players may be affected by action cards and modifiers
5. The round ends when a player busts, a player reaches Flip 7, or no active players remain
6. Scores are calculated and added to the running total
7. A new round begins

### 5.2 Turn Flow
- Each turn is short and clear
- The active player sees their current hand and options
- The opponent can watch, react, and plan
- The game should make it obvious what the consequences of each choice are

---

## 6. Player Interaction Model

### 6.1 Local Two-Player Experience
- Two players share one screen
- Both players can play from the same device
- The game should feel like a living tabletop experience rather than a single-player puzzle

### 6.2 Shared Attention
- The UI should make it easy for both players to follow the game state
- Important information such as danger, score, remaining cards, and current turn should be visible at all times

### 6.3 Social Feel
- The game should encourage banter and reactions
- The design should support quick, friendly competition rather than complex strategy alone

---

## 7. Core Mechanics to Preserve

### 7.1 Number Cards
- Number cards form the core of the scoring system
- They determine the player’s current round score
- The risk of duplicate numbers creates the bust mechanic

### 7.2 Modifier Cards
- Modifier cards add excitement and scoring flexibility
- They should feel impactful without overwhelming the game

### 7.3 Action Cards
- Action cards should create memorable moments and shift the pace of the round
- They should not become too disruptive or slow the game down

### 7.4 Flip 7 Bonus
- The Flip 7 bonus is a defining feature of the experience
- It should feel like a powerful and rewarding achievement

---

## 8. Interface and UX Requirements

### 8.1 Screen Layout
The game should have:
- a clear player area for each player
- a visible current turn indicator
- a visible score tracker
- a card display area
- clear Hit and Stay buttons
- a simple round summary after each round

### 8.2 Readability
- Cards should be easy to distinguish
- Number cards, modifier cards, and action cards should have clear visual identity
- The current risk state should be obvious at a glance

### 8.3 Couch-Friendly Controls
- Large buttons and simple controls
- Minimal text entry
- Easy to play while sitting on a couch or using a TV display

---

## 9. Visual Style Direction

### 9.1 Tone
- Friendly
- Bright
- Slightly playful
- High-energy but readable

### 9.2 Visual Priorities
- Clear card states
- Strong contrast for values and types
- Comfortable spacing for shared-screen play
- A polished feel without becoming too busy

### 9.3 UI Principles
- Keep the game readable from a distance
- Use bold colors and high contrast for key actions
- Make the active player obvious

---

## 10. Game Flow Requirements

### 10.1 Fast Setup
- The game should be easy to start with minimal setup
- A new match should begin quickly

### 10.2 Short Rounds
- Rounds should be short enough to replay easily
- The game should support several rounds in one sitting

### 10.3 Clear Progression
- Players should know how close they are to winning
- Score totals should be visible at all times

---

## 11. Technical Direction

### 11.1 Platform Target
- Browser-based game
- HTML, CSS, and JavaScript
- Designed for local play on a desktop or large-screen device

### 11.2 Scope for Version 1
- Two-player local play
- Shared-screen UI
- Core card deck and mechanics
- Basic turn flow
- Score tracking
- Round results

### 11.3 Future Expansion Ideas
- Single-player AI mode
- Online multiplayer
- Sound effects and animations
- More card variants and custom rules
- Tournament mode

---

## 12. Success Criteria

The game is successful if:
- two players can pick it up quickly and start playing without confusion
- the tension between risk and reward feels strong
- the game is fun in a shared physical setting
- players want to play another round immediately

---

## 13. Open Design Questions

- Should the game be strictly competitive, or should players share a co-op goal?
- Should the game use a shared score target or individual score targets?
- Should the UI support turn-based play with a “pass device” mechanic for couch play?
- Should action cards be more dramatic or more streamlined for the first version?

---

## 14. Recommended First Version Scope

For the initial release, focus on:
- two-player local turn-based play
- the core number-card, modifier-card, and action-card flow
- clear score tracking
- simple hit/stay decisions
- visible round-end states
- polished but lightweight UI
