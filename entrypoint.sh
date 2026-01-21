#!/usr/bin/env bash
set -euo pipefail

DB_URL_SYNC="${DATABASE_URL_SYNC:-}"
if [[ -z "$DB_URL_SYNC" && -n "${DATABASE_URL:-}" ]]; then
  DB_URL_SYNC="${DATABASE_URL/asyncpg/psycopg2}"
fi

# psycopg2.connect expects a libpq URL without the SQLAlchemy driver suffix.
DB_URL_SYNC="${DB_URL_SYNC/postgresql+psycopg2/postgresql}"

if [[ -z "$DB_URL_SYNC" ]]; then
  echo "DATABASE_URL_SYNC is not set." >&2
  exit 1
fi

export DATABASE_URL_SYNC="$DB_URL_SYNC"

uv run alembic upgrade head

should_seed=$(uv run python - <<'PY'
import os
import psycopg2

url = os.environ.get("DATABASE_URL_SYNC")
if not url:
    raise SystemExit("DATABASE_URL_SYNC not set")

conn = psycopg2.connect(url)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM properties")
count = cur.fetchone()[0]
cur.close()
conn.close()

print("yes" if count == 0 else "no")
PY
)

if [[ "$should_seed" == "yes" ]]; then
  uv run python seed.py
fi

exec "$@"
