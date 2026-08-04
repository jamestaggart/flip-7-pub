# Component Specifications

## App shell

Landscape-first layout with a maximum content width around 1600 px. The board should occupy most of the viewport. Utility controls must not overpower gameplay.

## Header bar

Contains the Flip 7 title/logo, game status, round number, deck count, target score, and menu access. It remains visible during active play.

## Player panel

Required properties:

- `name`
- `isActive`
- `status`
- `roundScore`
- `totalScore`
- `riskLevel`
- `cards`
- `uniqueNumberCount`
- `message`

Active state uses a blue/cyan outline, glow, brighter header, and `Active Player` ribbon. Inactive state keeps full readability with reduced glow and contrast. Bust or duplicate danger uses red treatment.

Desktop target: two equal panels side by side. At narrow widths, stack panels while keeping the active panel first.

## Card component

Cards must be data-driven and render text/icons in code.

Variants:

- Number: cream base, blue details, large numeric value.
- Modifier positive: green base.
- Multiplier: gold/orange base.
- Modifier negative: red/orange base.
- Freeze: red or cool action treatment with snowflake.
- Flip Three: purple treatment with three-card icon.
- Second Chance: warm red treatment with heart icon.
- Card back: navy with gold ornament.

States: default, hover/focus, selected, disabled, duplicate danger, newly drawn. Maintain a consistent aspect ratio near 2.5:3.5.

## Risk meter

Three semantic states: low, medium, high. Include both color and text; never communicate risk through color alone. A duplicate already present should use an explicit warning message rather than only `high`.

## Action buttons

Primary actions:

- Hit: blue.
- Stay: green.
- Freeze Target: orange/red.
- Flip Three Target: purple.

Each button includes an icon, action label, and short explanatory label. Support default, hover/focus, pressed, disabled, and loading states.

## Status and result banners

Banner variants:

- Turn/information: blue.
- Success/stayed: green.
- Freeze/action: purple or blue.
- Warning/duplicate: orange-red.
- Bust/error: red.

Banners should contain one short headline and optional one-line explanation.

## Setup components

- Player-name text fields.
- Starting-player selector.
- Target-score stepper and presets.
- Create Game button.
- Existing-games list with Join state.
- Empty state.
- Backend/game status pills.

## Round summary modal

Shows one result card per player, round outcome, score earned, updated total, and one primary `Next Round` action. The background board remains recognizable but dimmed and noninteractive.

## Game over modal

Shows winner, standings, final totals, `Play Again`, and `New Game`. Celebration art must not reduce text readability.

## Accessibility

- Keyboard focus must be clearly visible.
- Buttons need accessible names and disabled explanations where useful.
- Dialog focus must be trapped and restored on close.
- Text contrast should meet WCAG AA where practical.
- Use `aria-live` for turn and action-result announcements without duplicating every visual update.
