# Flip 7 Completion Checklist

This is the working step-by-step checklist to reach full completion against all AI design and plan documents.

Related tracking:

- Blockers log: [AI/implementation-blockers.md](AI/implementation-blockers.md)

## How to use this checklist

- Mark each task complete by changing [ ] to [x].
- Do not mark a task complete until code is merged and tests pass.
- Keep tasks in order unless a dependency is explicitly independent.

## Phase 0: Environment and workflow baseline

- [x] Add root ignore rules for generated files and artifacts.
- [x] Confirm Docker services can run locally.
- [x] Confirm Playwright runs locally on host against Docker app on localhost.
- [x] Document local Docker plus Playwright workflow in README.
- [x] Add a single command script for bring-up, migrate, and test run.

## Phase 1: Database and data integrity completion

- [x] Create core models for players, games, rounds, turns, cards, and locations.
- [x] Create initial migration for core models.
- [x] Seed initial card definitions.
- [x] Align deck composition to full Flip 7 deck counts from game rules.
- [x] Add explicit game results and final ranking persistence model.
- [x] Add database constraints for card location consistency and uniqueness.
- [x] Add database constraints for seat ordering and per-game player integrity.
- [x] Add migration tests for schema assumptions.

## Phase 2: Backend rule engine completion

- [x] Implement create game, join game, start round, hit, stay, and state endpoints.
- [x] Implement base score calculation and round finalization flow.
- [x] Enforce acting player and turn ownership on hit and stay actions.
- [x] Enforce inactive and busted player action blocking.
- [x] Implement Freeze action effect end to end.
- [x] Implement Flip Three action effect end to end.
- [x] Implement Second Chance action effect end to end.
- [x] Implement action resolution payloads consistent with API design.
- [x] Ensure busted players always score zero for the round.
- [x] Ensure Flip 7 bonus behavior matches rules in all edge cases.
- [x] Add deterministic shuffling strategy and reproducible test mode.
- [x] Add robust serializer validation and consistent API error shapes.

## Phase 3: API contract completion

- [x] Audit every required endpoint from AI API design and map to implementation.
- [x] Add missing endpoints for scoring, results, and rules support.
- [x] Add endpoint-level permission and state validation checks.
- [x] Add API versioning strategy and response compatibility notes.
- [x] Generate API reference examples from real responses.

## Phase 4: Frontend gameplay completion

- [x] Implement basic setup flow for creating players and games.
- [x] Implement basic game state display and hit and stay controls.
- [x] Build dedicated main game board layout for two-player couch play.
- [x] Add clear active-player visual emphasis.
- [x] Add deck count and round state indicators.
- [x] Add per-player risk cues and duplicate danger messaging.
- [x] Add action card effect banners and resolution messages.
- [x] Add round summary overlay interaction and continue flow.
- [x] Add game over screen with winner, totals, and replay actions.
- [x] Add loading, empty, and recoverable error states for all async calls.
- [x] Improve styling and readability to match frontend design direction.

## Phase 5: Test plan completion

- [x] Keep Playwright smoke tests passing locally.
- [x] Implement full API test coverage from AI API test plan.
- [x] Implement frontend user-story Playwright tests from AI frontend test plan.
- [x] Add tests for all action cards and edge rule cases.
- [x] Add negative tests for invalid turns, invalid joins, and invalid state transitions.
- [x] Add regression tests for all bugs fixed during implementation.

## Phase 6: End-to-end hardening and release readiness

- [x] Run full backend plus frontend suite in CI-like clean environment.
- [x] Validate two-player complete game to win condition through UI only.
- [x] Validate replay and reset flows.
- [x] Add final README runbook with one clear start-to-finish demo path.
- [x] Add troubleshooting section for Docker, DB, and Playwright issues.

## Definition of done

All items below must be true:

- [x] Every required capability in AI design docs is implemented or explicitly deferred with rationale.
- [x] All API tests pass.
- [x] All Playwright tests pass.
- [x] A full two-player game to completion works from the frontend.
- [x] Project runs locally using documented Docker workflow.

## Current focus queue

Work these in order:

1. Enforce turn ownership and action validity in backend hit and stay actions.
2. Implement action card behavior in backend services and API.
3. Expand backend tests for full rules and edge cases.
4. Upgrade frontend board UX and action feedback.
5. Expand Playwright coverage to match user-story test plan.
