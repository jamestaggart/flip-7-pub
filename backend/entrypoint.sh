#!/usr/bin/env sh
# Waits for Postgres, applies migrations, then runs the container command.
set -e

DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"

echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
python - <<PY
import os, socket, time, sys

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            sys.exit(0)
    except OSError:
        time.sleep(1)
print("Postgres was not reachable in time", file=sys.stderr)
sys.exit(1)
PY

echo "Applying database migrations..."
python manage.py migrate --noinput

exec "$@"
