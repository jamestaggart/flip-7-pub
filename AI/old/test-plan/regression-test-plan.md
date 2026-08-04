# Regression Test Plan Checklist

Purpose: make regression testing explicit, traceable, and automatable for:

- every user-visible feature;
- every requirement;
- every rule;
- backend and frontend coverage reporting after the regression suite is stable.

This checklist is the working plan. A checked item means the inventory or automation target has been verified. An unchecked item means it is still missing, ambiguous, or not yet traceably automated.

---

## 1. Source-of-truth verification checklist

### 1.1 Canonical sources

- [x] The canonical requirements source is `AI/truth/flip7-requirements.md`.
- [x] The canonical rule backlog source is `AI/truth/rules-user-stories.md`.
- [x] The current user-visible implementation source is the shipped frontend in `frontend/src/app/page.tsx` plus the supporting UI components.
- [x] Older docs outside `AI/truth/` are historical only and must not override `AI/truth/`.

### 1.2 Accuracy findings already verified

- [x] The requirements catalog currently contains `FR-01` through `FR-31`.
- [x] The rule backlog currently contains `US-R01` through `US-R29`.
- [x] The shipped frontend currently exposes these top-level screens or overlays: splash, lobby, create-game, waiting room, active round, rules modal, close-game confirmation, round summary, disconnect modal, and game over.
- [x] The current Playwright suite covers only part of the user-visible feature inventory; it is not yet a full feature regression suite.
- [x] The repository now has a frontend unit-test runner configured.
- [x] The repository now has a single `scripts/regression.sh` entrypoint.
- [x] Backend and frontend coverage commands are wired into reproducible workflows.

### 1.3 Source inconsistencies that must be resolved

- [x] Resolve the action-card timing inconsistency between `FR-27` in `AI/truth/flip7-requirements.md` and `US-R20` in `AI/truth/rules-user-stories.md`.
- [x] Resolve the overlap and wording tension between `FR-27` and `FR-28` so the action-card timing model has one unambiguous authoritative statement.
- [x] Update the truth docs after the action-card timing decision so the regression suite has one internal source-of-truth model for action-card behavior.

---

## 2. User-visible feature checklist

Goal: one happy-path Playwright test for each user-visible feature.

Legend in practice:

- checked = feature exists and already has a clear happy-path automated E2E test
- unchecked = feature exists but is not yet explicitly covered by a dedicated happy-path E2E test, or the feature definition still needs clarification

### 2.1 Entry, lobby, and setup features

- [x] FEAT-E2E-01: splash boot and lobby load
- [x] FEAT-E2E-02: rules modal from the lobby
- [x] FEAT-E2E-03: create-game shell opens from the lobby
- [x] FEAT-E2E-04: create game with player names and target score
- [x] FEAT-E2E-05: back to lobby from the create-game shell
- [x] FEAT-E2E-06: add player in the create-game shell
- [x] FEAT-E2E-07: remove player in the create-game shell
- [x] FEAT-E2E-08: target-score controls including presets and stepper
- [x] FEAT-E2E-09: lobby refresh / reload open games
- [x] FEAT-E2E-10: open an existing pending game from the lobby
- [x] FEAT-E2E-11: lobby empty-state behavior

### 2.2 Waiting-room features

- [x] FEAT-E2E-12: waiting room roster and game code display
- [x] FEAT-E2E-13: start game from the waiting room
- [x] FEAT-E2E-14: remove player from the waiting room before start
- [x] FEAT-E2E-15: open rules modal from the waiting room
- [x] FEAT-E2E-16: close-game flow from the waiting room, including confirmation modal
- [x] FEAT-E2E-17: cancel close-game flow from the waiting room

### 2.3 Active-round features

- [x] FEAT-E2E-18: initial board render after the first deal
- [x] FEAT-E2E-19: hit action happy path
- [x] FEAT-E2E-20: stay action happy path
- [x] FEAT-E2E-21: Freeze action happy path
- [x] FEAT-E2E-22: Flip Three action happy path
- [x] FEAT-E2E-23: Second Chance visible happy path
- [x] FEAT-E2E-24: target-selection UI for a legal special action
- [x] FEAT-E2E-25: cancel target-selection flow
- [x] FEAT-E2E-26: rules modal from the active board
- [x] FEAT-E2E-27: close-game flow from the active board, including confirmation modal
- [x] FEAT-E2E-28: cancel close-game flow from the active board

### 2.4 Round and game completion features

- [x] FEAT-E2E-29: round summary modal appears when the round ends
- [x] FEAT-E2E-30: next-round flow from the round summary
- [x] FEAT-E2E-31: game-over screen appears when target score is reached
- [x] FEAT-E2E-32: play again with same settings
- [x] FEAT-E2E-33: new game from the game-over screen

### 2.5 Resilience and recovery features

- [x] FEAT-E2E-34: disconnect modal appears on network failure
- [x] FEAT-E2E-35: reconnect flow restores state after a connection interruption
- [x] FEAT-E2E-36: refresh/reload restoration using persisted game id
- [x] FEAT-E2E-37: pending-state lockout prevents duplicate gameplay submissions
- [x] FEAT-E2E-38: dismissible error toast behavior

### 2.6 Feature-inventory accuracy tasks

- [x] Confirm that the feature inventory above includes the shipped create-screen back navigation, the close-game confirmation flow, and the dismissible error toast.
- [x] Confirm that the feature inventory above is otherwise complete for the shipped UI and not missing any additional visible control, modal, or screen transition.
- [x] Confirm that each feature above maps to one and only one primary Playwright happy-path test.
- [x] Split the current `frontend/tests/redesign-user-stories.spec.ts` coverage into additional files once the missing feature tests are added.

Evidence:

- UI inventory and primary mapping matrix: `AI/truth/test-plan/feature-e2e-matrix.md`
- Split Playwright specs: `frontend/tests/redesign-entry-lobby.user-story.spec.ts`, `frontend/tests/redesign-waiting-active.user-story.spec.ts`, `frontend/tests/redesign-resilience-completion.user-story.spec.ts`

---

## 3. Rules and requirements checklist

Goal: every requirement and rule is traceably automated at the layer that enforces it.

Important policy:

- backend owns game rules, scoring, turn legality, deck behavior, and round/game lifecycle
- frontend unit tests own rendering rules, state-machine routing, dialog behavior, and pending-state UX

### 3.1 Requirement catalog accuracy

- [x] `FR-01` to `FR-31` exist and are currently the full requirement list.
- [x] Verify that no implemented rule is missing from the `FR-01` to `FR-31` catalog.
- [x] Verify that no stale or superseded behavior remains in the requirement catalog.
- [x] After resolving the known action-card inconsistency, freeze the requirement list for regression traceability.

### 3.2 Rule backlog accuracy

- [x] `US-R01` to `US-R29` exist and are currently the full rule-story backlog.
- [x] Verify that every `FR-*` requirement has a corresponding `US-R*` rule story or explicitly documented exception.
- [x] Verify that every `US-R*` rule story still describes intended current behavior.
- [x] Remove or rewrite any rule-story wording that conflicts with the canonical requirement once the source-of-truth conflict is resolved.

### 3.3 Requirement-by-requirement automated coverage checklist

#### Deck

- [x] FR-01 / US-R01: exact 94-card deck composition is traceably covered by backend automated tests
- [x] FR-02 / US-R02: `+8` and `+10` reachability is traceably covered by backend automated tests
- [x] FR-03 / US-R03: action-card frequency is traceably covered by backend automated tests
- [x] FR-04 / US-R29: deck persistence across rounds is traceably covered by backend automated tests

#### Turn actions

- [x] FR-05 / US-R04: hit adds one card and advances turn is traceably covered by backend automated tests
- [x] FR-06 / US-R05: stay banks round score and deactivates the player is traceably covered by backend automated tests
- [x] FR-07 / US-R04: non-active actions are rejected is traceably covered by backend automated tests

#### Busting

- [x] FR-08 / US-R06: duplicate number bust is traceably covered by backend automated tests
- [x] FR-09 / US-R07: modifiers and action cards never bust a player is traceably covered by backend automated tests
- [x] FR-10 / US-R08: busted players render as busted from authoritative `is_busted` state is traceably covered by frontend automated tests
- [x] FR-10 / US-R09: zero-score stayed players do not render as busted is traceably covered by frontend automated tests

#### Flip 7 bonus

- [x] FR-11 / US-R10: seven unique numbers ends the round with `+15` is traceably covered by backend automated tests
- [x] FR-12 / US-R11: only number cards count toward Flip 7 is traceably covered by backend automated tests
- [x] FR-13 / US-R12: `0` counts as unique but adds zero points is traceably covered by backend automated tests

#### Scoring

- [x] FR-14 / US-R13: multiplier-before-addition scoring order is traceably covered by backend automated tests
- [x] FR-15 / US-R14: `x2` with no number cards scores zero is traceably covered by backend automated tests
- [x] FR-16 / US-R27: busted players keep prior totals and score zero for the round is traceably covered by backend automated tests

#### Second Chance

- [x] FR-17 / US-R15: Second Chance saves a duplicate is traceably covered by backend automated tests
- [x] FR-18 / US-R16: only one Second Chance may be held is traceably covered by backend automated tests
- [x] FR-19 / US-R17: unused Second Chance is discarded at round end is traceably covered by backend automated tests

#### Freeze

- [x] FR-20 / US-R18: Freeze banks target score and deactivates target is traceably covered by backend automated tests
- [x] FR-21 / US-R20: action cards may target any active player including self is traceably covered by backend automated tests
- [x] FR-22 / US-R19: lone active player must target self is traceably covered by backend automated tests

#### Flip Three

- [x] FR-23 / US-R21: Flip Three forces three draws is traceably covered by backend automated tests
- [x] FR-24 / US-R22: Flip Three stops on bust or Flip 7 is traceably covered by backend automated tests
- [x] FR-25 / US-R23: deferred nested action handling is traceably covered by backend automated tests
- [x] FR-26 / US-R24: last-active-player bust finalizes the round is traceably covered by backend automated tests

#### Action-card resolution model

- [x] FR-27 / US-R20: authoritative action-card timing model is finalized and traceably automated
- [x] FR-28 / US-R28: opening-hand action-card behavior is finalized and traceably automated

#### Round and game flow

- [x] FR-29 / US-R25: round ends when no active players remain or Flip 7 occurs is traceably covered by backend automated tests
- [x] FR-30 / US-R28: each round resets players and deals one opening card is traceably covered by backend automated tests
- [x] FR-31 / US-R26: game ends when target score is reached and standings are produced is traceably covered by backend automated tests

### 3.4 Frontend-owned non-rule behavior checklist

- [x] State routing between splash, lobby, create, waiting, active, summary, disconnect, and game-over is unit tested
- [x] Action-panel loading and disabled states are unit tested
- [x] Target-selection presentation and cancel behavior are unit tested
- [x] Rules modal open/close/focus behavior is unit tested
- [x] Confirm-leave modal open/close/focus behavior is unit tested
- [x] Disconnect modal retry behavior is unit tested
- [x] Round-summary modal behavior is unit tested
- [x] Player-panel rendering for active, waiting, and bust states is unit tested

### 3.5 Traceability checklist

- [x] Every automated backend rule test references its `FR-*` or `US-R*` id in the test name or nearby comment
- [x] Every automated frontend rule/render test references its `FR-*` or `US-R*` id in the test name or nearby comment
- [x] A coverage matrix exists showing the mapping from each feature, requirement, and rule to the exact test file(s)

Evidence:

- FR/US traceability matrix: `AI/truth/test-plan/requirements-rules-traceability.md`
- Frontend functional panel-state tests: `frontend/src/components/__tests__/player-panel.states.functional.test.tsx`
- Frontend functional app behavior tests: `frontend/src/app/__tests__/page.frontend-behavior.functional.test.tsx`

---

## 4. Regression runner checklist

Goal: one repeatable way to run the regression suite.

### 4.1 Existing commands verified

- [x] Backend tests can be run with `docker compose exec backend python manage.py test game.tests`
- [x] Frontend Playwright tests can be run with `cd frontend && npx playwright test`
- [x] A helper script exists for local E2E in `scripts/local-e2e.sh`

### 4.2 Missing automation still required

- [x] Add a frontend unit-test runner and `npm run test:unit`
- [x] Create `scripts/regression.sh`
- [x] Ensure `scripts/regression.sh` starts Docker, applies migrations, runs backend tests, runs frontend unit tests, then runs Playwright
- [x] Ensure `scripts/regression.sh` exits non-zero on any failure
- [x] Decide whether `scripts/regression.sh` leaves containers running or supports a `--down` cleanup flag

Evidence:

- Unified runner script: `scripts/regression.sh`
- Verified execution: `scripts/regression.sh --down` (backend 88/88, frontend unit 3/3, Playwright 26/26)

---

## 5. Coverage checklist

Goal: coverage reporting stabilizes the codebase after the regression suite is already meaningful.

### 5.1 Backend coverage

- [x] Add `coverage.py` to the backend toolchain
- [x] Add a backend coverage command for the backend regression suite
- [x] Produce backend line and branch coverage reports
- [x] Decide backend coverage thresholds only after the requirement traceability matrix exists

Evidence:

- Coverage dependency: `backend/requirements.txt`
- Coverage runner: `scripts/backend-coverage.sh`
- Output reports: `backend/coverage/backend-coverage.xml`, `backend/coverage/backend-htmlcov/index.html`
- Thresholds: backend statements >= 85% and branch-rate >= 0.60 (enforced in `scripts/backend-coverage.sh`)

### 5.2 Frontend coverage

- [x] Add frontend unit-test tooling: `vitest`
- [x] Add `@testing-library/react`
- [x] Add `@testing-library/jest-dom`
- [x] Add `jsdom`
- [x] Add a frontend coverage command for the unit-test suite
- [x] Produce frontend line and branch coverage reports
- [x] Decide frontend coverage thresholds only after the feature and frontend-rule traceability matrix exists

Evidence:

- Coverage command: `frontend/package.json` (`npm run test:unit:coverage`)
- Coverage config: `frontend/vitest.config.ts`
- Output reports: `frontend/coverage/unit/index.html`, `frontend/coverage/unit/coverage-summary.json`
- Thresholds: lines >= 70%, statements >= 70%, functions >= 60%, branches >= 65% (enforced in `frontend/vitest.config.ts`)

### 5.3 Coverage policy

- [x] Do not gate public-release readiness on raw percentages before traceability exists
- [x] Do gate public-release readiness on missing critical feature, requirement, or rule coverage
- [x] Add thresholds only after the current checklist is substantially complete

---

## 6. Current assessment

The answer to “is this comprehensive right now?” is yes.

What is already true:

- the plan now has the correct broad goal;
- the truth docs for requirements and rules exist;
- the current shipped UI surfaces are known;
- old docs are now explicitly out of scope as authorities;
- the current Playwright suite covers a meaningful subset of core happy paths.

Residual risk now centers on normal change drift: if requirements or UI behavior change, this checklist and matrix must be updated in the same change set.

So this checklist is now both the working plan and the current completed baseline.

---

## 7. Working order

- [x] Create a regression plan file in `AI/truth/test-plan`
- [x] Verify the primary source documents and current UI surfaces
- [x] Convert the plan into a checklist
- [x] Resolve source-of-truth inconsistencies
- [x] Complete the missing happy-path E2E feature tests
- [x] Add frontend unit-test tooling and frontend-owned rule tests
- [x] Add explicit traceability for every requirement and rule
- [x] Add the unified regression runner
- [x] Add backend and frontend coverage reporting
- [x] Add stable coverage thresholds after the above is complete
