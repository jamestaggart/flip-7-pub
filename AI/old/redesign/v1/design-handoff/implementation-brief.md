# Implementation Brief

## Goal

Implement the Flip 7 redesign as a responsive, couch-friendly card-game interface using reusable components and the provided visual references.

## Scope

Build these states:

1. Setup / pre-game.
2. Active round.
3. Round summary overlay.
4. Game over overlay.

Also implement reusable visual states for active/inactive players, card families, risk levels, action availability, warnings, loading, and disabled controls.

## Architecture recommendation

Create a route or state-driven screen shell and a reusable component library. Keep presentation separate from game logic. Components should accept plain data and emit actions.

Suggested component tree:

```text
Flip7App
├── AppHeader
├── SetupScreen
│   ├── PlayerCreationForm
│   ├── StartingPlayerSelector
│   ├── TargetScoreControl
│   └── ExistingGameList
└── GameBoard
    ├── TurnBanner
    ├── PlayerPanel × 2
    │   ├── ScoreLine
    │   ├── RiskMeter
    │   └── CardRow
    ├── ActionPanel
    ├── ResultBanner
    ├── RoundSummaryDialog
    └── GameOverDialog
```

## State model

At minimum, model:

- game status
- round number
- deck count
- target score
- active player ID
- players and scores
- each player's cards and round state
- available actions
- current result/feedback message
- active overlay

## Responsive behavior

- Desktop: two player panels side by side.
- Medium: retain two columns when legible; reduce decorative spacing.
- Small: stack panels with the active player first and keep actions sticky or immediately adjacent.
- Do not reduce critical text below comfortable reading size.

## Implementation constraints

- No full-screen mockup used as a background.
- No cropped UI from asset sheets.
- No baked dynamic text.
- Avoid hard-coding player names or scores.
- Preserve semantic buttons and dialogs.
- Keep colors, spacing, and typography tokenized.

## Definition of done

The four required states are implemented, responsive, keyboard usable, data-driven, and visually comparable to the reference images. All acceptance criteria in `qa-acceptance-criteria.md` pass.
