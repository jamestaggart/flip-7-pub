# Summary of the Frontend Redesign

This document consolidates the redesign direction for the Flip 7 frontend so implementation can proceed without waiting on missing design artifacts.

## Redesign scope

The redesign covers four required UI states:

1. Setup / pre-game
2. Active round
3. Round summary overlay
4. Game over overlay

The experience should remain gameplay-faithful and should not introduce rule changes. The visual redesign is for presentation, hierarchy, and feedback only.

## State flow

The implementation should follow this sequence:

1. Setup: create a game, choose starting player, set target score, and join or view existing games.
2. Game initialization: move into the active board state with the selected starting player.
3. Active turn: present the active player prominently, show scores, risk, cards, and primary actions.
4. Decision moment: make Hit and Stay primary, and surface Freeze and Flip Three only when available.
5. Action resolution: show feedback, update board state, and refresh risk/score cues.
6. Round summary: show each player’s result, earned score, and updated totals.
7. Next round: continue play with updated deck and round state.
8. Game completion: show winner, standings, and replay actions.

## Reference mapping

Use the design handoff package and the reference examples below as the implementation source of truth:

- Setup and lobby direction: [AI/design-handoff/assets/full-redesign-example/flip7-setup-and-lobby-assets.png](AI/design-handoff/assets/full-redesign-example/flip7-setup-and-lobby-assets.png)
- Core gameplay and player panels: [AI/design-handoff/assets/full-redesign-example/flip7-gameplay-ui-components.png](AI/design-handoff/assets/full-redesign-example/flip7-gameplay-ui-components.png)
- Controls and icons: [AI/design-handoff/assets/full-redesign-example/flip7-controls-and-icons.png](AI/design-handoff/assets/full-redesign-example/flip7-controls-and-icons.png)
- Card asset language: [AI/design-handoff/assets/full-redesign-example/flip7-card-asset-sheet.png](AI/design-handoff/assets/full-redesign-example/flip7-card-asset-sheet.png)
- Overlays and feedback states: [AI/design-handoff/assets/full-redesign-example/flip7-overlays-and-feedback.png](AI/design-handoff/assets/full-redesign-example/flip7-overlays-and-feedback.png)
- Full overview: [AI/design-handoff/assets/full-redesign-example/flip7-full-redesign-overview.png](AI/design-handoff/assets/full-redesign-example/flip7-full-redesign-overview.png)

## Implementation defaults

- Use the design tokens and component guidance in the handoff docs as the default starting point.
- Use temporary SVG or inline icon substitutes where final branded artwork is not yet available.
- Do not crop or repurpose the reference sheets as production UI elements.
- Keep the UI data-driven so player names, scores, cards, and round state come from existing game state rather than hard-coded values.

## Readiness note

The handoff package now provides enough direction to begin the redesign implementation. The remaining items are polish-level choices and acceptance refinements rather than blockers to starting the work.
