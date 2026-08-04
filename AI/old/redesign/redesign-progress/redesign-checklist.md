# Frontend Redesign Checklist

This checklist tracks all work needed to implement the Flip 7 frontend redesign using the existing design handoff artifacts, including the full redesign examples and summary flow.

## 1) Alignment and planning

- [x] Confirm redesign scope matches four required states: setup, active round, round summary overlay, and game-over overlay.
- [x] Confirm no gameplay-rule changes are introduced by visual redesign.
- [x] Confirm implementation approach in frontend app (single page state shell vs modular route/state composition).
- [x] Confirm all handoff docs are the source of truth during implementation.
- [x] Create a state-to-reference mapping from `AI/design-handoff/summary-of-redesign.md` and `AI/design-handoff/assets/full-redesign-example/`.
- [x] Define milestone plan for implementation, QA, and polish.

## 2) Current UI audit

### Redesign user stories now captured
- [x] US-20: Configure a match from the redesigned setup shell.
- [x] US-21: Follow the active game from a board-first experience.
- [x] US-22: Resolve turns from the shared action panel.
- [x] US-23: Review round summaries and match results without losing context.

These stories are documented in `AI/flip7-frontend-design-document.md` and `AI/flip7-frontend-test-plan.md`.

- [x] Audit existing page structure and identify reusable pieces in `frontend/src/app/page.tsx`.
- [x] Inventory current UI elements that already satisfy handoff requirements.
- [x] Identify gaps between current UI and required screens/states.
- [x] Identify styling debt in `frontend/src/app/globals.css` that should be removed or refactored.
- [x] Build a reference matrix that maps current UI sections to the updated redesign examples.
- [ ] Capture before/after screenshots for comparison during redesign.

## 3) Design token and theme foundation

- [x] Implement design tokens from handoff (colors, spacing, radius, shadows, glow, risk colors).
- [x] Define semantic token layer (surface, text, status, risk, action, overlay).
- [x] Add typography system (display + body families, weights, scale).
- [x] Add responsive spacing and sizing scale for desktop/tablet/small screens.
- [ ] Add reduced-motion support tokens and media-query fallbacks.

## 4) App layout shell

- [x] Build top header area for title, status pills, round number, and deck count.
- [x] Build utility/setup region for player creation, active player selector, target score, and game create/join controls.
- [x] Build main board container as primary visual focus.
- [x] Build action region for turn controls and result banner.
- [x] Build overlay layer architecture for round summary and game-over dialogs.
- [x] Implement setup-to-main-board transition flow after create/join actions.

## 5) Setup/pre-game redesign

- [x] Redesign player creation area for pass-and-play clarity.
- [x] Redesign active-player selector for clear ownership and easy touch targets.
- [x] Redesign target score input and validation visuals.
- [x] Redesign create/join controls with clear hierarchy.
- [x] Redesign existing games list to support fast join and clean scanning.
- [x] Add empty/loading/error visual states for setup controls.

## 6) Active round redesign

- [x] Build two large player panels with clear active/inactive distinction.
- [x] Add strong current-turn visual highlight and transfer behavior.
- [x] Redesign score lines (round score + total score) for quick distance readability.
- [x] Surface target score, deck count, and round number in stable locations.
- [x] Implement a prominent turn banner that clearly states whose decision is next.
- [x] Redesign action/status banner for action outcomes and warnings.
- [x] Redesign action buttons for Hit, Stay, Freeze target, and Flip Three target.
- [x] Preserve action hierarchy: Hit and Stay as primary actions; action-card controls as secondary.
- [x] Ensure action availability states (enabled, disabled, pending) are obvious.

## 7) Player panel and card systems

- [x] Implement player panel content contract: name, turn state, round score, total score, risk, cards.
- [x] Implement card row layout for both players across breakpoints.
- [x] Add progress display for seven unique numbers per player.
- [x] Implement card-family visual differences: number, modifier, and action cards.
- [ ] Implement card-state visuals: default, emphasized, disabled, and recently-played feedback.
- [x] Ensure card text/icons remain legible at shared-screen distance.

## 8) Risk and tension communication

- [x] Define low/medium/high risk visual language.
- [ ] Add duplicate-number danger cues and urgency treatment.
- [x] Add action resolution impact cues in banner/panel areas.
- [x] Ensure duplicate danger uses explicit warning text, not color-only emphasis.
- [x] Ensure risk cues remain understandable for color-vision differences.

## 9) Overlay/dialog redesign

- [x] Build round summary overlay with per-player round result and updated totals.
- [ ] Include explicit round outcomes (stayed, busted, Flip 7) in round summary rows.
- [x] Build strong Next Round action emphasis in round summary overlay.
- [x] Build game-over overlay with winner callout and standings.
- [ ] Add both New Game and Play Again with Same Settings actions.
- [ ] Add celebration treatment (for example confetti/crown effects) while preserving text readability.
- [ ] Ensure overlays trap focus and preserve keyboard usability.

## 10) Interaction and motion

- [x] Implement turn-change transition (focus shift + glow transfer).
- [x] Implement result banner entrance/exit motion.
- [x] Implement modal entrance/exit motion.
- [ ] Implement card draw/play transition cues.
- [ ] Add score-change callouts for major point events (for example +50, +25, -30).
- [ ] Ensure feedback coverage for key events: card drawn, stayed, Freeze, Flip Three, Second Chance, duplicate warning, bust, Flip 7.
- [ ] Respect reduced-motion preferences for all animated elements.

## 11) Responsive and accessibility

- [x] Validate desktop landscape as primary experience.
- [x] Validate medium-screen behavior while retaining two-panel clarity.
- [x] Validate small-screen stacked layout with active player first.
- [x] Ensure all controls meet touch-target size guidance.
- [x] Verify color contrast and text readability at all key hierarchy levels.
- [x] Verify keyboard navigation and focus visibility across setup/board/overlays.
- [x] Verify semantic labels/roles for buttons, inputs, lists, and dialogs.

## 12) Integration with existing logic

- [x] Keep all UI state data-driven from existing frontend/backend game data.
- [x] Ensure no hard-coded names/scores/cards in rendered UI.
- [x] Verify create game, join game, hit, stay, freeze, and flip-three flows still operate correctly.
- [x] Verify target score flow and game-finish handling still work in redesigned UI.
- [ ] Verify Next Round behavior resets card areas, updates round/deck state, and assigns next active player.
- [ ] Verify replay/reset/new-game flows still work in redesigned UI.

## 13) Frontend test updates

- [ ] Update Playwright selectors to match redesigned semantic structure.
- [ ] Keep tests resilient to parallel runs and existing game list state.
- [ ] Add/adjust assertions for current-turn visibility and action availability.
- [ ] Add/adjust assertions for overlay states and key score/status content.
- [ ] Re-run full frontend Playwright suite locally.

## 14) Final QA and acceptance

- [x] Validate redesign against handoff acceptance criteria.
- [x] Validate all required interface elements are visible in at least one appropriate state.
- [x] Validate no regression in backend connectivity/loading behavior.
- [ ] Run backend API/game tests in Docker after integration touches.
- [x] Validate final implementation against the state loop in `AI/design-handoff/summary-of-redesign.md`.
- [x] Validate visual hierarchy against the full redesign examples in `AI/design-handoff/assets/full-redesign-example/`.
- [ ] Capture final implementation notes and any remaining polish backlog.

## Definition of done

- [x] Setup, active round, round summary, and game-over states are redesigned and complete.
- [x] UI is responsive, readable, and couch-friendly.
- [x] Accessibility and keyboard usability requirements are met.
- [ ] Playwright frontend suite passes.
- [x] Redesign is aligned with the design handoff package and mock requirements.
