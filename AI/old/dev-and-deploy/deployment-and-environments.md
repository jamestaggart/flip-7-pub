# Flip 7 — Deployment & Environments (Source of Truth)

**Status:** Canonical spec for how this repo is configured, run, and deployed. If compose
files, env templates, scripts, or docs disagree with this file, this file wins — update them to
match, or change this file first (with rationale) if the model is genuinely being revised.

**Companion docs (to be produced from this spec):**
- `docs/hosting.md` — how to deploy to production (one page, copy-paste steps).
- `docs/development.md` — how to run the stack locally for development.

**Guiding principle:** There are exactly **two modes**, each driven by **one command** and
**one environment file**. No configuration lives in more than one place.

- `dev` → local development stack. You edit **one** file: `.env.dev`.
- `prod` → production-ready stack (HTTPS, hardened Django). You edit **one** file: `.env.prod`.

---

## 1. Problems with the current setup (what we are fixing)

Environment configuration is currently scattered across at least four locations, which is
error-prone and hard to explain:

| Location | Purpose today | Problem |
|----------|---------------|---------|
| `backend/.env.dev`, `backend/.env.prod` | Django reads `backend/.env.<DJANGO_ENV>` | Backend-only; duplicates DB creds; separate from compose. |
| root `.env` (via `.env.prod.example`) | Interpolation for `docker-compose.prod.yml` | A second prod file, overlapping the backend one. |
| Inline env in `docker-compose.yml` | Hardcodes `DJANGO_ENV=dev` + DB creds | Config baked into a tracked file; can't override cleanly. |
| `NEXT_PUBLIC_API_URL` in each compose file | Frontend API base URL | Set in two places; easy to forget in prod. |

Net effect: to configure prod you touch multiple files in multiple folders, and it is unclear
which one "wins". The goal is to collapse this to **one file per mode**.

---

## 2. Target model

### 2.1 One entry point, two modes

A single wrapper provides the two commands the user types. Implement as a `Makefile` at the repo
root (preferred — no new dependencies):

```bash
make dev     # build + start the development stack, then follow logs
make prod    # build + start the production stack in the background
make down    # stop whichever stack is running
make logs    # tail logs
```

Each target simply selects the right compose file and env file:

- `make dev`  → `docker compose --env-file .env.dev  -f docker-compose.dev.yml  up --build`
- `make prod` → `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build`

> Rationale: `--env-file` makes the chosen file the *single* source of interpolation values for
> that mode. The compose file maps those values to each service. There is no second env file.

### 2.2 One env file per mode (repo root)

Only two tracked templates exist, both at the repo root:

- `.env.dev.example`  → copied to `.env.dev`
- `.env.prod.example` → copied to `.env.prod`

Both `.env.dev` and `.env.prod` are git-ignored. The backend-level `backend/.env.*` files are
**removed** (see §4). All services read their configuration from the single root env file for
the active mode, injected by compose.

**`.env.prod` — the only file a deployer edits:**

```dotenv
# The one file you edit for production.
DOMAIN=example.com
DJANGO_SECRET_KEY=<generate: python3 -c "import secrets; print(secrets.token_urlsafe(64))">
POSTGRES_PASSWORD=<strong-random-password>
POSTGRES_DB=flip7
POSTGRES_USER=flip7
```

Everything else in prod is **derived** by `docker-compose.prod.yml`, so the deployer never sets
it by hand:

- `DJANGO_ENV=prod`
- `DJANGO_ALLOWED_HOSTS=${DOMAIN}`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://${DOMAIN}`
- `CORS_ALLOWED_ORIGINS=https://${DOMAIN}`
- `NEXT_PUBLIC_API_URL=https://${DOMAIN}`

**`.env.dev` — the only file a developer edits:**

```dotenv
# The one file you edit for local development. Sensible defaults; change if you need to.
DJANGO_ENV=dev
POSTGRES_DB=flip7
POSTGRES_USER=flip7
POSTGRES_PASSWORD=flip7pass
# Frontend talks to the backend on localhost during development.
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Dev keeps working out of the box: `DEBUG` on, all hosts/CORS allowed, no secret key required.

### 2.3 Two compose files, clearly named

- `docker-compose.dev.yml` — development. Bind-mounts source for hot reload, runs
  `runserver` / `next dev`, exposes ports 8000 and 3000, `DJANGO_ENV=dev`. (This is today's
  `docker-compose.yml`, renamed, with inline env replaced by `${VAR}` from `.env.dev`.)
- `docker-compose.prod.yml` — production. No bind mounts; `gunicorn` + Next production build;
  Caddy reverse proxy with automatic HTTPS; `DJANGO_ENV=prod`; restart policies and healthchecks.

Neither compose file contains secrets or hardcoded credentials — every value comes from the
active `--env-file`.

### 2.4 Secret handling rules

- Secrets live **only** in `.env.dev` / `.env.prod` on the machine that runs the stack.
- Compose injects each variable into **only** the services that need it. The public-facing
  frontend container never receives database credentials or the Django secret key.
- Only `*.example` templates are committed. `.gitignore` already enforces
  `.env`, `.env.*`, with `!.env.*.example` unignored — keep that rule.

---

## 3. Command reference (target end state)

| Goal | Command |
|------|---------|
| Start developing | `cp .env.dev.example .env.dev` → edit → `make dev` |
| Deploy to production | `cp .env.prod.example .env.prod` → edit the 3 required values → `make prod` |
| Stop | `make down` |
| Logs | `make logs` |
| Run backend migrations (prod) | handled automatically by the backend entrypoint on start |
| Create admin user (prod) | `docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser` |

Acceptance: a fresh clone reaches a running dev stack after editing exactly one file
(`.env.dev`), and a running production site after editing exactly one file (`.env.prod`).

---

## 4. Migration & cleanup checklist

Ordered work to reach the target model:

- [x] Rename `docker-compose.yml` → `docker-compose.dev.yml`; replace inline env with
      `${VAR}` interpolation sourced from `.env.dev`.
- [x] Keep `docker-compose.prod.yml`; confirm every value comes from `.env.prod` or is derived
      from `DOMAIN`.
- [x] Create root `.env.dev.example` (dev defaults) and root `.env.prod.example` (three required
      values + DB name/user). Both minimal and heavily commented.
- [x] Delete `backend/.env.dev.example` and `backend/.env.prod.example`; the
      `backend/.env.<DJANGO_ENV>` loading path now reads the root `.env.<DJANGO_ENV>` as a
      no-op fallback (env vars injected by compose always win).
- [x] Add a root `Makefile` with `dev`, `prod`, `down`, `logs` targets as defined in §2.1.
- [x] Confirm `gunicorn` + `whitenoise` are in `backend/requirements.txt` and wired in settings
      (`WhiteNoiseMiddleware`, `STATIC_ROOT`, `STORAGES`) so prod serves static with `DEBUG=off`.
- [x] Update `README.md` Quick start / Self-hosting to point at `make dev` / `make prod` and the
      two root env files only.
- [x] Write `docs/hosting.md` and update `docs/development.md` (see §5).
- [x] Grep the repo for stray env references (`.env.dev`, `.env.prod`, `NEXT_PUBLIC_API_URL`,
      `DJANGO_ENV`) and ensure each points at the single-source model.

---

## 5. Required user-facing docs

Two short, standalone pages. Each must be runnable start-to-finish by copy-paste with no prior
context.

### 5.1 `docs/hosting.md` — "Host Flip 7 in production"

Must contain, in order:
1. Prerequisites: a VPS with Docker + Docker Compose, a domain name.
2. Point the domain: add a DNS **A record** for `DOMAIN` → the server IP.
3. Get the code: `git clone … && cd flip-7-pub`.
4. Configure the one file: `cp .env.prod.example .env.prod`, then set `DOMAIN`,
   `DJANGO_SECRET_KEY` (with the generator command), and `POSTGRES_PASSWORD`.
5. Launch: `make prod`.
6. Verify: open `https://DOMAIN`; HTTPS is issued automatically by Caddy.
7. Operate: update (`git pull && make prod`), logs (`make logs`), create admin user.
8. Troubleshooting: DNS not propagated, low-RAM build failures (use ≥2 GB or add swap).

### 5.2 `docs/development.md` — "Develop Flip 7 locally"

Must contain, in order:
1. Prerequisites: Docker + Docker Compose.
2. Configure: `cp .env.dev.example .env.dev` (defaults are fine; note what you may change).
3. Run: `make dev`.
4. URLs: frontend `http://localhost:3000`, API `http://localhost:8000/api/`.
5. Common tasks: migrations, backend tests, frontend unit tests, Playwright on the host.
6. Stop / reset: `make down`, and how to wipe volumes.

Both docs must state the single rule up top: **dev = edit `.env.dev`; prod = edit `.env.prod`;
nothing else.**

---

## 6. Acceptance criteria

The simplification is "done" when all of the following hold:

1. A new contributor runs `cp .env.dev.example .env.dev && make dev` and gets a working local
   stack without touching any other file.
2. A deployer runs `cp .env.prod.example .env.prod`, edits exactly three values, runs
   `make prod`, and reaches an HTTPS production site on their domain.
3. There is exactly one env file per mode, both at the repo root; no `backend/.env.*` remain.
4. No compose file contains a hardcoded secret or credential.
5. `docs/hosting.md` and `docs/development.md` each work end-to-end by copy-paste.
