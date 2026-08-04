#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/4] Ensuring Docker services are running..."
docker compose up -d --build

echo "[2/4] Applying backend migrations..."
docker compose exec backend python manage.py migrate

echo "[3/4] Running backend tests with branch coverage..."
docker compose exec backend coverage run --branch manage.py test game.tests game.tests_coverage

echo "[4/4] Writing backend coverage reports..."
docker compose exec backend coverage report
docker compose exec backend coverage xml -o coverage/backend-coverage.xml
docker compose exec backend coverage html -d coverage/backend-htmlcov

echo "Backend coverage reports written to backend/coverage/."