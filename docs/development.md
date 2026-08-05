# Development guide

**One rule:** for local development you edit exactly one file, `.env.dev`. For production you edit
`.env.prod` instead — see [hosting.md](hosting.md).

## Quick start

From the project root:

```bash
make dev
```

That copies `.env.dev.example` to `.env.dev` on first run, builds the stack, applies migrations
automatically, and follows the logs. Defaults work out of the box; edit `.env.dev` only if you
want to change them.

Open the app at:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432

Stop the stack with `make down`; view logs with `make logs`.

## Environment configuration

Development configuration lives in a single root file, `.env.dev` (copied from
`.env.dev.example`). The dev stack ([docker-compose.dev.yml](../docker-compose.dev.yml)) reads it
via `--env-file .env.dev` and falls back to sane defaults, so the app runs even before you edit
it. In dev, `DEBUG` is on and all hosts/CORS origins are allowed. Only the `*.example` template is
tracked — never commit `.env.dev`.

## Running tests

### Functional, rule, and requirement test runs

Backend functional rule/requirement tests:

```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py test game.tests
```

Backend coverage-focused tests:

```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py test game.tests_coverage
```

Frontend functional tests:

```bash
cd frontend
npm run test:unit:functional
```

### Frontend build

```bash
cd frontend
npm run build
```

### End-to-end tests (Playwright)

Run the frontend tests locally from the host machine:

```bash
cd frontend
npm install
npx playwright test
```

The Playwright config defaults to http://127.0.0.1:3000.

### Coverage commands

Frontend coverage-only tests:

```bash
cd frontend
npm run test:unit:coverage-only
```

Frontend full unit coverage run (functional + coverage-focused):

```bash
cd frontend
npm run test:unit:coverage-all
```

Backend full coverage workflow (runs backend functional + coverage-focused tests and writes reports):

```bash
./scripts/backend-coverage.sh
```

Combined frontend/backend coverage summary and delta vs baseline:

```bash
./scripts/coverage-summary.sh
```

Optional: write the current run as a new baseline:

```bash
./scripts/coverage-summary.sh --write-baseline
```

### One-command local regression

Runs backend tests, frontend functional tests, and frontend E2E tests:

```bash
./scripts/regression.sh --down
```

## Useful commands

```bash
make down
docker compose -f docker-compose.dev.yml down -v --remove-orphans
```

## Troubleshooting

- If Docker is not running, start Docker Desktop and rerun the compose command.
- If the API reports missing tables or columns, run the migrate command again.
- If a port is already in use, stop the conflicting process or restart Docker Compose.
