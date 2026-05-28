#!/bin/bash
set -e

echo "Running Alembic migrations..."
uv run alembic upgrade head

echo "Seeding roles..."
uv run -m app.seeds.roles

echo "Seeding admin user..."
uv run -m app.seeds.admin

exec "$@"

echo "Starting Uvicorn..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload