# Flip 7 Mock Requirements

This document defines the visual and product requirements for generating mock images of the Flip 7 interface.

## Purpose

Use this as a handoff brief for ChatGPT, image-generation tools, Figma AI, or a designer creating interface mockups.

The goal is not to produce implementation code. The goal is to produce clear, high-quality visuals for the game experience.

## Product summary

Flip 7 is a couch-friendly, turn-based card game for local play on a shared screen.

The interface should feel like:

- a modern tabletop game night
- warm, tactile, and easy to read from a distance
- slightly dramatic and game-like rather than dashboard-like
- intuitive for pass-and-play use

The experience should prioritize:

- current turn clarity
- score pressure and risk visibility
- quick comprehension of game state
- large, comfortable controls

## Core gameplay concept

Players take turns choosing `Hit` or `Stay`.

Gameplay rules reflected in the UI:

- Number cards build round score.
- Drawing a duplicate number causes a bust.
- Reaching seven unique numbers triggers a Flip 7 bonus and ends the round.
- Action cards include:
  - `Freeze`
  - `Flip Three`
  - `Second Chance`
- Players accumulate total score across rounds.
- The game ends when a player reaches the target score.
- The interface supports replaying rounds and starting a new game.

## Primary mockup goals

The mockups should show:

1. A strong main board layout.
2. A clear current-turn focus.
3. Distinct visual identity for cards and player states.
4. A setup flow that feels simple and understandable.
5. Clear overlays for end-of-round and end-of-game states.

## Required screens and states

### 1. Setup / pre-game state

Show:

- player creation area
- active player selector
- target score input
- create game control
- join existing game control
- existing games list

The setup area should be easy to understand without feeling like a generic admin form.

### 2. Active round state

Show:

- a main board as the primary focus
- two large player panels
- one player clearly highlighted as the current turn
- visible round score and total score for each player
- visible target score
- visible deck count
- visible round number
- action/status banner
- large action buttons:
  - `Hit`
  - `Stay`
  - `Freeze target`
  - `Flip Three target`
- visible card rows for both players

### 3. Round summary overlay

Show:

- modal or overlay treatment
- each player’s round result
- updated total scores
- a strong `Next Round` action

### 4. Game over overlay

Show:

- clear winner announcement
- standings / totals
- `New Game` control
- optional replay-related action

## Required interface elements

The mockups should include these visible elements somewhere in the design:

- game title
- backend/game status pills or status indicators
- round number
- deck count
- target score
- two player areas
- current-turn highlight
- score lines for each player
- risk label for each player
- card row for each player
- action result banner
- setup controls
- overlay/modal states

## Player panel requirements

Each player panel should visually communicate:

- player name
- whether it is their turn
- current round score
- total score
- risk level
- card collection
- active/inactive state

The active player panel should feel unmistakably highlighted.

## Card presentation requirements

Cards should be visually distinct by type.

At minimum, mockups should differentiate:

- number cards
- modifier cards
- action cards

Suggested styling direction:

- number cards: calm, cool, stable color family
- modifier cards: bright, energetic accent family
- action cards: warmer, punchier disruptive family

Cards should feel readable and game-like, not like plain text pills.

## Risk and tension communication

The interface should make the danger of pressing your luck visible.

Show cues for:

- low risk
- medium risk
- high risk
- duplicate-number danger
- action resolution impact

The player should be able to glance at the board and understand where the tension is.

## Layout guidance

Preferred structure:

- Top header:
  - title
  - game status
  - round number
  - deck count
- Side rail or upper utility area:
  - player setup
  - active player selector
  - target score
  - game creation/joining
- Main board center:
  - two player areas side by side
- Action panel:
  - current-turn controls
- Overlay layer:
  - round summary
  - game over

The board should feel like the primary object, not secondary to forms.

## Visual direction

The design should avoid looking like:

- a generic admin dashboard
- a basic white-page form app
- a flat prototype with no atmosphere

The design should feel more like:

- a digital tabletop
- a premium party/card game interface
- a living game board with focus and tension

Use:

- strong hierarchy
- large readable typography
- rich but controlled color
- layered surfaces
- clear contrast
- spacious layout

## Interaction style to suggest in mocks

Even though these are static mockups, they should imply:

- large couch-friendly buttons
- obvious next action
- simple turn flow
- minimal confusion about where to look next

## Tone and personality

The visual personality should be:

- playful but not childish
- polished but not sterile
- dramatic but not chaotic
- friendly for local shared-screen play

## Device context

Primary target:

- desktop or laptop in landscape orientation
- shared-screen / couch-play context

Secondary requirement:

- should still adapt reasonably to smaller screens

## Specific states to emphasize in visuals

Mockups should especially make these moments feel strong:

1. Starting a round
2. Being the active player
3. Deciding whether to hit or stay
4. Seeing a dangerous board state
5. Ending a round
6. Seeing the winner at game over

## Suggested prompt-ready summary

If you need a compact version for image generation:

"Design a modern digital tabletop interface for a two-player couch-friendly card game called Flip 7. The layout should feature a large central game board, two side-by-side player panels, a strong current-turn highlight, visible round and total scores, a target score, deck count, action banner, and large controls for Hit, Stay, Freeze target, and Flip Three target. Use visually distinct number cards, modifier cards, and action cards. The design should feel warm, tactile, premium, and easy to read from a distance, like a polished party card game rather than an admin dashboard. Include mockups for setup state, active round state, round summary overlay, and game over overlay."