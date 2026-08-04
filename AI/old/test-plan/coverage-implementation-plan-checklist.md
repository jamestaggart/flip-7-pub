# Coverage Implementation Plan Checklist

Last updated: 2026-08-03

Purpose: reduce bug risk by combining strong functional, user-story, and coverage-focused tests, push coverage aggressively now, then maintain a high practical coverage level over time (not perfect 100% forever).

## 1. Test taxonomy and separation

- [x] E2E tests are labeled as user-story tests using file suffix `.user-story.spec.ts`.
- [x] Existing frontend unit tests are labeled as functional tests using file suffix `.functional.test.tsx`.
- [x] Coverage-focused tests are labeled with file suffix `.coverage.test.ts` or `.coverage.test.tsx`.
- [x] Coverage-focused tests are stored separately from functional tests.
- [x] Backend coverage-focused tests are separated from backend rule/requirement functional tests.

Implementation notes:
- User-story tests validate complete user flows and should remain stable and business-readable.
- Functional tests validate behavior, rules, and requirements directly.
- Coverage tests target difficult branches, guard clauses, and failure handling not naturally hit by user-story or functional suites.

## 2. Baseline and reporting

- [x] Backend coverage report is generated at `backend/coverage/backend-coverage.xml` and `backend/coverage/backend-htmlcov/index.html`.
- [x] Frontend coverage report is generated at `frontend/coverage/unit/coverage-summary.json` and `frontend/coverage/unit/index.html`.
- [x] Backend coverage reporting command exists in `scripts/backend-coverage.sh`.
- [x] Frontend coverage reporting command exists in `frontend/vitest.config.ts`.
- [x] Add a combined coverage summary script that prints backend + frontend deltas versus previous run.

## 3. Full-coverage implementation phases

### Phase A: keep taxonomy clean while adding coverage tests

- [x] Add dedicated frontend folder `frontend/src/coverage-tests` for `.coverage.test.ts(x)` files.
- [x] Add dedicated backend file/module for coverage-only tests (for example `backend/game/tests_coverage.py`).
- [x] Add scripts:
  - `npm run test:unit:functional`
  - `npm run test:unit:coverage-only`
  - `npm run test:unit:coverage-all`
- [x] Ensure local regression runs functional suites by default, with coverage-only suite opt-in or coverage-stage only.

### Phase B: close largest backend gaps first

Targets from current report:
- `game/serializers.py`
- `game/views.py`
- uncovered branches in `game/services.py`

Checklist:
- [x] Add coverage tests for serializer validation failures and edge payloads.
- [x] Add coverage tests for API error paths (400/404/409) and response contracts.
- [x] Add coverage tests for rare service branches and nested action edge cases.

### Phase C: close largest frontend gaps first

Targets from current report:
- `frontend/src/lib/api.ts`
- `frontend/src/lib/presentation.ts`
- specific uncovered branches in `frontend/src/app/page.tsx`

Checklist:
- [x] Add coverage tests for API client error normalization and transport failures.
- [x] Add coverage tests for presentation mapping helpers and tone/risk branch edges.
- [x] Add coverage tests for low-frequency page state transitions and guard branches.

### Phase D: full-coverage push now, high coverage later

- [ ] Keep adding coverage-focused tests until remaining uncovered paths are mostly non-critical edge paths.
- [ ] Re-run functional + coverage suites before each deploy and review failures and coverage deltas.
- [ ] If coverage drops in core gameplay or UI logic, add focused coverage tests before release.

### Phase E: approach practical full coverage

- [ ] Complete the current full-coverage push for core gameplay and UI modules.
- [ ] Define the long-term high-coverage maintenance band for solo development (high, not perfect).
- [ ] Allow documented exceptions for generated files, framework glue, and intentionally unreachable defensive code.
- [ ] Require explicit justification for every excluded line/branch.

## 4. Quality guardrails

- [ ] No coverage test should duplicate end-to-end user-story intent.
- [ ] No coverage test should replace a missing requirement/rule functional test.
- [ ] Keep traceability mapping focused on functional and user-story evidence; coverage tests are supplemental.
- [ ] Every new production branch should be accompanied by either functional coverage or coverage-focused evidence.
- [ ] Treat failing functional or user-story tests as release blockers.
- [ ] Treat unhandled-error paths in API/services/UI state transitions as mandatory coverage targets.

Current implementation evidence:
- Frontend coverage-only tests: `frontend/src/coverage-tests/api-client.coverage.test.ts`, `frontend/src/coverage-tests/presentation.coverage.test.ts`, `frontend/src/coverage-tests/page-state-guards.coverage.test.tsx`
- Backend coverage-only tests: `backend/game/tests_coverage.py`
- Coverage summary script and baseline: `scripts/coverage-summary.sh`, `AI/truth/test-plan/coverage-baseline.json`
- Functional vs coverage execution split: `frontend/package.json`, `frontend/vitest.config.ts`, `frontend/vitest.coverage-only.config.ts`, `frontend/vitest.coverage.config.ts`, `scripts/regression.sh`, `scripts/backend-coverage.sh`

## 5. Exit criteria for coverage program

- [ ] All checklist items in this file are complete.
- [ ] Coverage commands are stable and part of local regression and pre-deploy checks.
- [ ] Coverage exceptions are documented and approved.
- [ ] Test categories stay clearly separated (user-story, functional, coverage) by file naming and location.
- [ ] Regression and coverage runs are used as the final local go/no-go gate before deploy.
