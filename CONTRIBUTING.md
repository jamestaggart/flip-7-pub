# Contributing

Thanks for contributing to Flip 7.

## Local setup

Start the development stack (creates `.env.dev` from the example on first run):

```bash
make dev
```

Open the app:
- http://localhost:3000

Migrations run automatically when the backend container starts. See
[docs/development.md](docs/development.md) for details.

## Test expectations for pull requests

Run these before opening a PR:

```bash
./scripts/regression.sh
```

If you only changed backend logic, at minimum run:

```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py test game.tests game.tests_coverage
```

If you only changed frontend logic, at minimum run:

```bash
cd frontend
npm run test:unit:functional
```

## Branch and PR guidance

- Keep changes focused and small.
- Use clear commit messages.
- Include what changed, why, and how you validated it.
- Link issues when relevant.

## Scope note

This is a solo-maintained game project. Reviews and responses are best effort.
