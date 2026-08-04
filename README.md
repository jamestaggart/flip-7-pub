# Flip 7

Flip 7 is a pass-and-play, turn-based card game built with Django REST Framework, PostgreSQL, Next.js, and Playwright.

Project status: active solo project, suitable for local development and testing.

## Quick start

From the repository root:

```bash
docker compose up -d --build
docker compose exec backend python manage.py migrate
```

Open:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/

## Self-hosting

The backend selects its environment via the `DJANGO_ENV` variable: `dev` (default) or `prod`. On startup it loads the matching `backend/.env.<DJANGO_ENV>` file if present. Real environment variables (for example those injected by Docker Compose or your host) always take precedence.

### Development

Local Docker development works out of the box — `DJANGO_ENV=dev` is set in `docker-compose.yml`, `DEBUG` is on, and all hosts/CORS origins are allowed. To customize, copy the example:

```bash
cp backend/.env.dev.example backend/.env.dev
```

### Production

Copy the production template and fill in real values before deploying:

```bash
cp backend/.env.prod.example backend/.env.prod
```

Then run the backend with `DJANGO_ENV=prod`. In production, `DEBUG` is off and you **must** set:

- `DJANGO_SECRET_KEY` — a strong, unique key (the app refuses to start without it)
- `DJANGO_ALLOWED_HOSTS` — comma-separated hostnames
- `CORS_ALLOWED_ORIGINS` — comma-separated allowed frontend origins
- `POSTGRES_PASSWORD` — a strong database password

Never commit a populated `.env.dev` or `.env.prod`; only the `*.example` templates are tracked.

## How to play

Core loop:

- Create or join a game
- Add players
- Start a round
- Take turns with Hit, Stay, Freeze, and Flip Three

## Testing

Run the full regression suite:

```bash
./scripts/regression.sh
```

Targeted test commands:

```bash
docker compose exec backend python manage.py test game.tests game.tests_coverage
cd frontend && npm run test:unit:functional
cd frontend && npx playwright test
```

## Documentation

- Development guide: [docs/development.md](docs/development.md)
- Architecture: [docs/architecture.md](docs/architecture.md)
- Database: [docs/database.md](docs/database.md)
- API: [docs/api.md](docs/api.md)
- Frontend walkthrough: [docs/frontend-walkthrough.md](docs/frontend-walkthrough.md)

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
