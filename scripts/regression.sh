#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export COMPOSE_FILE=docker-compose.dev.yml
SHOULD_DOWN=false

for arg in "$@"; do
  case "$arg" in
    --down)
      SHOULD_DOWN=true
      ;;
    *)
      echo "Unknown argument: $arg"
      echo "Usage: scripts/regression.sh [--down]"
      exit 2
      ;;
  esac
done

cleanup() {
  if [[ "$SHOULD_DOWN" == "true" ]]; then
    echo "[cleanup] Stopping Docker services (--down)."
    docker compose down
  fi
}
trap cleanup EXIT

cd "$ROOT_DIR"

echo "[1/6] Starting Docker services..."
docker compose up -d --build

echo "[2/6] Applying backend migrations..."
docker compose exec backend python manage.py migrate

echo "[3/6] Running backend tests..."
docker compose exec backend python manage.py test game.tests

echo "[4/6] Installing frontend dependencies..."
cd frontend
npm install

echo "[5/6] Running frontend unit tests..."
npm run test:unit:functional

echo "[6/6] Running frontend Playwright tests on host..."
npx playwright test

echo "Regression suite complete."
