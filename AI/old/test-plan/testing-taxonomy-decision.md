# Testing Taxonomy Decision

Last updated: 2026-08-03

## Decision

We separate tests by intent to avoid mixing coverage work with requirement/rule/user-story validation.

This workflow assumes solo development with local regression and pre-deploy safeguards to prevent shipping code bugs.

1. End-to-end tests are user-story tests.
2. Existing requirement/rule behavior tests are functional tests.
3. Coverage tests are separate tests dedicated to branch/path completion and edge-case reachability.

## Naming convention

- User-story E2E tests: `*.user-story.spec.ts`
- Functional unit/integration tests: `*.functional.test.ts` and `*.functional.test.tsx`
- Coverage-focused tests: `*.coverage.test.ts` and `*.coverage.test.tsx`

## File organization

- E2E user-story tests remain under `frontend/tests/`.
- Functional frontend tests remain in feature/component test folders under `frontend/src/**/__tests__/`.
- Coverage-focused frontend tests should be placed in `frontend/src/coverage-tests/`.
- Backend functional rule/requirement tests remain in `backend/game/tests.py` (or split by domain later).
- Backend coverage-only tests should be isolated in a dedicated backend coverage test module.

## Traceability policy

- Requirement/rule traceability is documented by mapping matrix entries and nearby comments.
- Test names should describe behavior, not requirement IDs.
- Requirement IDs remain in documentation and optional comments when useful for audits.

## Initial renames applied

- `frontend/src/components/__tests__/player-panel.fr10.test.tsx` -> `frontend/src/components/__tests__/player-panel.states.functional.test.tsx`
- `frontend/src/app/__tests__/page.frontend-behavior.test.tsx` -> `frontend/src/app/__tests__/page.frontend-behavior.functional.test.tsx`
- `frontend/tests/redesign-entry-lobby.spec.ts` -> `frontend/tests/redesign-entry-lobby.user-story.spec.ts`
- `frontend/tests/redesign-waiting-active.spec.ts` -> `frontend/tests/redesign-waiting-active.user-story.spec.ts`
- `frontend/tests/redesign-resilience-completion.spec.ts` -> `frontend/tests/redesign-resilience-completion.user-story.spec.ts`

## Related plan

- Coverage implementation checklist: `AI/truth/test-plan/coverage-implementation-plan-checklist.md`

## Execution commands

- Frontend functional tests: `cd frontend && npm run test:unit:functional`
- Frontend coverage-only tests: `cd frontend && npm run test:unit:coverage-only`
- Frontend full coverage run (functional + coverage-only): `cd frontend && npm run test:unit:coverage-all`
- Backend functional tests: `docker compose exec backend python manage.py test game.tests`
- Backend coverage-only tests: `docker compose exec backend python manage.py test game.tests_coverage`
- Backend full coverage run (functional + coverage-only): `scripts/backend-coverage.sh`
