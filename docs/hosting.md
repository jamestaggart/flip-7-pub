# Host Flip 7 in production

This is the complete, copy-paste path to run Flip 7 on your own server with your own domain and
automatic HTTPS. **You edit exactly one file: `.env.prod`.**

The production stack ([docker-compose.prod.yml](../docker-compose.prod.yml)) runs:

- PostgreSQL
- Django via `gunicorn` (with `whitenoise` serving admin static files)
- Next.js production build
- [Caddy](../Caddyfile) as a reverse proxy that obtains and renews HTTPS certificates for you

Everything is served on one domain: `/api`, `/admin`, and `/static` go to the backend; everything
else goes to the frontend.

## 1. Prerequisites

- A Linux VPS (2 GB RAM or more — the frontend build needs memory).
- A domain name you control.
- Docker, the Docker Compose plugin, git, and make on the server:

```bash
apt update && apt install -y docker.io docker-compose-v2 git make
systemctl enable --now docker
```

Open the web ports on the server firewall so Caddy can serve traffic and complete the HTTPS
certificate challenge:

```bash
ufw allow OpenSSH
ufw allow 80,443/tcp
ufw --force enable
```

> If your host has a network-level firewall (for example a DigitalOcean Cloud Firewall), allow
> inbound TCP 80 and 443 there as well.

## 2. Point your domain at the server

Add a DNS **A record** for your domain to the server's public IP address:

- `@`   → `YOUR_SERVER_IP`
- `www` → `YOUR_SERVER_IP` (optional)

DNS must resolve to the server **before** you launch (Step 5) — Caddy can only obtain the HTTPS
certificate once the domain points at this machine. DNS can take a few minutes to propagate;
check with `dig +short YOUR_DOMAIN`.

## 3. Get the code

Push all project files (including `docker-compose.prod.yml`, `Caddyfile`, `Makefile`, and the
`.env.*.example` templates) to your repository first, since the server deploys by cloning it:

```bash
git clone <your-repo-url> flip7 && cd flip7
```

## 4. Configure the one file

```bash
cp .env.prod.example .env.prod
```

Edit `.env.prod` and set the three required values:

- `DOMAIN` — your domain, no scheme and no trailing slash (e.g. `example.com`).
- `DJANGO_SECRET_KEY` — generate one with:

  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(64))"
  ```

- `POSTGRES_PASSWORD` — a strong, random password.

Everything else — allowed hosts, CORS, CSRF, HTTPS redirect, and the frontend's API URL — is
derived from `DOMAIN` automatically. You do not set them by hand.

## 5. Launch

```bash
make prod
```

This builds the images, runs database migrations automatically, and starts everything in the
background.

## 6. Verify

Open `https://YOUR_DOMAIN`. The site loads over HTTPS with a certificate Caddy obtained
automatically. The API is reachable at `https://YOUR_DOMAIN/api/`.

## 7. Operate

Update to the latest code:

```bash
git pull && make prod
```

Tail logs:

```bash
make prod-logs
```

Create a Django admin user (for `https://YOUR_DOMAIN/admin`):

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

Stop everything:

```bash
make down
```

## Troubleshooting

- **HTTPS certificate not issued:** confirm the DNS A record points at the server and has
  propagated (`dig YOUR_DOMAIN`). Caddy retries automatically; watch `make prod-logs`.
- **Frontend build fails / server runs out of memory:** use a server with at least 2 GB RAM, or
  add swap space.
- **Site returns a 400 (Bad Request):** make sure `DOMAIN` in `.env.prod` exactly matches the
  hostname you are visiting.

## Security notes

- Secrets live only in `.env.prod` on the server; it is git-ignored and must never be committed.
- Database credentials and the Django secret key are passed only to the services that need them,
  never to the public-facing frontend container.
- In production, `DEBUG` is off, HTTPS redirect and secure cookies are on, and the app refuses to
  start without `DJANGO_SECRET_KEY`.
