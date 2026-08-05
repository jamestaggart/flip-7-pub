# Flip 7

Flip 7 is a pass-and-play, turn-based card game built with Django REST Framework, PostgreSQL, Next.js, and Playwright.

Project status: active solo project, suitable for local development and testing.

## Quick start

There are exactly two modes, each one command and one env file:

- **Develop:** `make dev` (edit `.env.dev`) — see [docs/development.md](docs/development.md)
- **Host in production:** `make prod` (edit `.env.prod`) — see [docs/hosting.md](docs/hosting.md)

To start developing from a fresh clone:

```bash
make dev
```

Open:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/

## Self-hosting

The app runs as a production stack (Django via gunicorn, Next.js production build, and Caddy for
automatic HTTPS) with a single command. You edit **one** file, `.env.prod`, and set three values:

- `DOMAIN` — your domain (must have a DNS A record pointing at the server)
- `DJANGO_SECRET_KEY` — a strong, unique key (the app refuses to start without it)
- `POSTGRES_PASSWORD` — a strong database password

Everything else (allowed hosts, CORS, HTTPS redirect, the frontend API URL) is derived from
`DOMAIN` automatically. Then:

```bash
cp .env.prod.example .env.prod   # edit the three values above
make prod
```

See [docs/hosting.md](docs/hosting.md) for the full step-by-step. Only the `*.example` templates
are tracked; real `.env.dev` / `.env.prod` files are git-ignored and must never be committed.

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
docker compose -f docker-compose.dev.yml exec backend python manage.py test game.tests game.tests_coverage
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
