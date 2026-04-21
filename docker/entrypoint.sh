#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  "$(dirname "${SQLITE_PATH:-/app/data/db.sqlite3}")" \
  "${DOCS_DIR:-/app/data/docs}" \
  "${VECTOR_DB_PATH:-/app/data/chroma_db}" \
  "${STATIC_ROOT:-/app/data/staticfiles}"

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

python manage.py migrate --noinput

exec uvicorn config.asgi:application \
  --host 0.0.0.0 \
  --proxy-headers \
  --port "${PORT:-8000}"
