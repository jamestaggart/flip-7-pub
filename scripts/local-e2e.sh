#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

echo "[1/4] Starting Docker services..."
docker compose up -d --build

echo "[2/4] Applying backend migrations..."
docker compose exec backend python manage.py migrate

echo "[3/4] Installing frontend dependencies..."
cd frontend
npm install

echo "[4/4] Running Playwright tests locally..."
npx playwright test
