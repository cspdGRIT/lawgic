#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"

# ── Postgres ────────────────────────────────────────────────────────────────
if ! pg_isready -q 2>/dev/null; then
  echo "Starting PostgreSQL..."
  brew services start postgresql@16
  sleep 2
fi

echo "Starting Lawgic backend on :8001..."
cd "$ROOT/backend"
# Override DATABASE_URL to always use Postgres (even if .env still has old SQLite value)
DATABASE_URL="postgresql+asyncpg://lawgic:lawgic_dev_pass@localhost:5432/lawgic" \
  .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend..."
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  curl -sf http://localhost:8001/health > /dev/null 2>&1 && break
  sleep 1
done

echo "Starting Lawgic frontend on :3001..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Lawgic running at http://localhost:3001"
echo "  API docs at    http://localhost:8001/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Demo login: demo@lawgic.in / password123"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
