# Implementation Blockers Checklist

This document tracks blockers discovered while executing the completion checklist.

## How to use

- Mark an item complete by changing `[ ]` to `[x]` once the blocker is actually removed.
- Keep the evidence, impact, and follow-up notes under each item current.
- Keep this file updated before checking off related items in [AI/completion-checklist.md](AI/completion-checklist.md).

## Core blockers

- [x] No open blockers currently tracked.

## Resolved blockers

### [x] B-001: Exact 94-card deck composition undefined

- Resolution:
  - Added project authority spec at [AI/deck-composition-spec.md](AI/deck-composition-spec.md).
  - Implemented composition in [backend/game/services.py](backend/game/services.py) via `DECK_COMPOSITION`.
  - Added deck-size regression test in [backend/game/tests.py](backend/game/tests.py).

### [x] B-002: Product direction conflict on minimum players

- Resolution:
  - Captured official project decisions in [AI/ruleset-deviations.md](AI/ruleset-deviations.md), including two-player support for this implementation.

### [x] B-003: Replay/reset behavior not formally specified

- Resolution:
  - Added spec in [AI/replay-reset-validation.md](AI/replay-reset-validation.md).
  - Added automated validation in [frontend/tests/replay-reset.spec.ts](frontend/tests/replay-reset.spec.ts).

### [x] B-005: Final ranking persistence model missing

- Resolution:
  - Added `GameResult` model and migration [backend/game/migrations/0003_gameresult_alter_gameplayer_unique_together_and_more.py](backend/game/migrations/0003_gameresult_alter_gameplayer_unique_together_and_more.py).
  - Persist rankings/results in round finalization logic in [backend/game/services.py](backend/game/services.py).
  - Results endpoint consumes persisted results in [backend/game/views.py](backend/game/views.py).

### [x] B-006: Missing strict DB constraints and migration tests

- Resolution:
  - Added DB constraints for seat integrity and card-location consistency in [backend/game/models.py](backend/game/models.py).
  - Added migration coverage via schema-integrity tests in [backend/game/tests.py](backend/game/tests.py).

### [x] R-001: Docker compose version key warning

- Resolution:
  - Removed obsolete `version` key from [docker-compose.yml](docker-compose.yml).

### [x] B-004: UI-only full game to win condition remained unstable in automation

- Resolution:
  - Added configurable target score support through backend and frontend flows.
  - Added a deterministic UI-only full-game validation in [frontend/tests/full-game.spec.ts](frontend/tests/full-game.spec.ts).
  - Verified the scenario passes locally in Playwright.

### [x] R-002: Frontend dependency security warnings

- Resolution:
  - Upgraded frontend framework/runtime dependencies to [frontend/package.json](frontend/package.json).
  - Added `postcss` and `sharp` overrides in [frontend/package.json](frontend/package.json).
  - Verified `npm audit --omit=dev` reports zero vulnerabilities.

## Suggested execution order

1. Return to the main completion checklist for any new work.
