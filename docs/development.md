# Development guide

## Quick start

From the project root:

```bash
docker compose up -d --build
```

Apply backend migrations:

```bash
docker compose exec backend python manage.py migrate
```

Open the app at:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- PostgreSQL: http://localhost:5432

## Environment configuration

The backend reads `DJANGO_ENV` to choose its environment: `dev` (default) or `prod`. On startup it loads `backend/.env.<DJANGO_ENV>` if present; real environment variables always win. Docker Compose sets `DJANGO_ENV=dev`, so local development needs no extra setup. Copy `backend/.env.dev.example` to `backend/.env.dev` to customize, or `backend/.env.prod.example` to `backend/.env.prod` for production. See the Self-hosting section in the root README for production requirements.

## Running tests

### Functional, rule, and requirement test runs

Backend functional rule/requirement tests:

```bash
docker compose exec backend python manage.py test game.tests
```

Backend coverage-focused tests:

```bash
docker compose exec backend python manage.py test game.tests_coverage
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
docker compose down
docker compose down -v --remove-orphans
```

## Troubleshooting

- If Docker is not running, start Docker Desktop and rerun the compose command.
- If the API reports missing tables or columns, run the migrate command again.
- If a port is already in use, stop the conflicting process or restart Docker Compose.
