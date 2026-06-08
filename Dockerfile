FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    DEBUG=true \
    ALLOWED_HOSTS=* \
    SQLITE_PATH=/app/data/db.sqlite3 \
    DOCS_DIR=/app/data/docs \
    VECTOR_DB_PATH=/app/data/chroma_db \
    STATIC_ROOT=/app/data/staticfiles

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/data/docs /app/data/chroma_db /app/data/staticfiles

EXPOSE 8000

CMD ["sh", "-c", "\
python -m pip list && \
python manage.py migrate && \
python manage.py ingest_pdfs --docs-dir ./data/docs && \
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} \
"]