# Public Release and VPS Hosting Work Checklist

Purpose: track the remaining work needed to finish the redesigned frontend validation,
complete the missing human-facing documentation, prepare the repository for public release,
and make the project easy to run on a fixed-cost VPS with Docker Compose.

Current assessment: 2026-08-03

Status values:
- `TODO` — not started
- `IN PROGRESS` — active work underway
- `DONE` — completed and verified
- `BLOCKED` — cannot proceed until an external dependency is resolved

---

## 1. Frontend end-to-end coverage for current user stories

Status: `DONE`

- [x] Playwright is already wired into the frontend workspace.
- [x] A baseline E2E suite exists in `frontend/tests/`.
- [x] Replace or remove outdated Playwright coverage that still reflects the old design.
- [x] Reconcile the latest redesigned UI against the current source-of-truth user stories.
- [x] Rewrite the end-to-end suite around the latest revision instead of preserving obsolete tests.
- [x] Ensure the new user-story-focused Playwright specs pass reliably on the current frontend.
- [x] Confirm the final test set covers the high-value user journeys for the redesign.

Notes:
- Completed with a fresh redesign-focused Playwright suite in `frontend/tests/redesign-user-stories.spec.ts`.
- Coverage now validates the splash-to-lobby transition, rules modal, create-game flow, waiting room, active board, hit/stay turn flow, round summary, and game-over screen.
- `npx playwright test` passed on 2026-08-03.

Suggested detail docs:
- [public-release-work/frontend-e2e-refresh.md](public-release-work/frontend-e2e-refresh.md)

## 2. Human-readable system documentation

Status: `DONE`

- [x] A docs directory already exists.
- [x] A development guide already exists in `docs/development.md`.
- [x] Create high-level system architecture diagrams in Mermaid.
- [x] Create Mermaid database diagrams that reflect the implemented schema.
- [x] Add API documentation in the docs directory.
- [x] Add a frontend walkthrough document in the docs directory.
- [x] Keep documentation aligned with the current code, not the superseded design.

Notes:
- Completed with `docs/architecture.md`, `docs/database.md`, `docs/api.md`, `docs/frontend-walkthrough.md`, and `docs/README.md`.

Suggested detail docs:
- [public-release-work/documentation-plan.md](public-release-work/documentation-plan.md)

## 3. Public repository readiness

Status: `IN PROGRESS` (ready for solo-public switch once optional items are accepted)

- [x] Ignore rules already cover common local env files.
- [x] A sample environment file already exists at `backend/.env.example`.
- [x] Review the repository for secrets, private-only assumptions, and internal-only notes.
- [x] Remove, move, or rewrite anything that should not be published.
- [x] Make setup instructions safe and clear for public contributors.
- [x] Verify ignore rules, sample environment files, and documentation support public use.
- [x] Record a final public-release review pass before switching visibility.

Notes:
- The repo currently contains a checked-in `backend/.env` with development credentials and secret defaults that should be handled before going public.
- There are internal workflow documents such as `HUMANS.md` and the `AI/` working area that should be reviewed for public visibility decisions.

Update (2026-08-03 quick pass):
- `backend/.env` exists locally but is not tracked.
- `.env.example` uses placeholder values.
- Added `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue templates, and PR template.
- Updated root README with safer public onboarding and test commands.
- Internal docs were reviewed and intentionally kept public for project transparency.

Suggested detail docs:
- [public-release-work/public-readiness.md](public-release-work/public-readiness.md)

## 4. VPS hosting readiness with Docker Compose

Status: `IN PROGRESS`

- [x] A Docker Compose stack already exists.
- [x] The repo can already be started locally with Docker Compose for development.
- [ ] Define a production-oriented Docker Compose path suitable for a fixed-cost VPS.
- [ ] Separate local development behavior from simple server deployment behavior.
- [ ] Document required environment variables, volumes, networking, and startup steps.
- [ ] Ensure the stack can be brought up on a single machine such as DigitalOcean with minimal ops overhead.
- [ ] Add a deployment checklist for first-time provisioning, updates, and rollback basics.

Notes:
- The current Compose file is development-oriented: bind mounts, Django `runserver`, Next.js dev server, localhost API URL, and hardcoded database credentials.
- A production deployment path still needs to be designed and documented.

Suggested detail docs:
- [public-release-work/vps-hosting-plan.md](public-release-work/vps-hosting-plan.md)

---

## Exit criteria

- [x] The redesigned frontend user-story Playwright suite passes.
- [x] The docs directory contains current architecture, database, API, and frontend walkthrough docs.
- [x] The repository has been reviewed and is safe to make public for a solo project baseline.
- [ ] A VPS operator can deploy the stack with Docker Compose using documented steps.