#!/bin/bash
set -e

# Set defaults if variables are unset
: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"

wait_for_db() {
  echo "Waiting for database at $POSTGRES_HOST:$POSTGRES_PORT..."
  until python3 -c "import socket; s = socket.socket(); s.settimeout(1); s.connect(('$POSTGRES_HOST', int('$POSTGRES_PORT')))" 2>/dev/null; do
    echo "Database is unavailable - sleeping..."
    sleep 1
  done
  echo "Database is up!"
}

wait_for_db

echo "Running migrations..."
uv run alembic upgrade head

echo "Starting application..."
exec uv run python run.py
