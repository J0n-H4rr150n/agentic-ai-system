#!/usr/bin/env sh
set -e

# If DATABASE_URL is set, ensure DB is reachable and migrations are applied.
if [ -n "${DATABASE_URL:-}" ]; then
  echo "[entrypoint] DATABASE_URL set; waiting for Postgres..."
  python - <<'PY'
import os
import time
import sys
import psycopg

dsn = os.environ.get("DATABASE_URL", "")
# Alembic/SQLAlchemy DSN may include a driver prefix; psycopg wants plain postgresql://
if "+psycopg" in dsn:
    dsn = dsn.replace("+psycopg", "")

deadline = time.time() + 60
last_err = None
while time.time() < deadline:
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        print("[entrypoint] Postgres is reachable")
        sys.exit(0)
    except Exception as e:
        last_err = e
        time.sleep(1)

print(f"[entrypoint] Timed out waiting for Postgres: {last_err}")
sys.exit(1)
PY

  echo "[entrypoint] Running Alembic migrations..."
  alembic -c backend/alembic.ini upgrade head
fi

exec "$@"
