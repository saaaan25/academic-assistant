FROM docker.io/library/python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    DEBUG=false \
    ALLOWED_HOSTS=127.0.0.1,localhost \
    SQLITE_PATH=/app/data/db.sqlite3 \
    DOCS_DIR=/app/data/docs \
    VECTOR_DB_PATH=/app/data/chroma_db \
    STATIC_ROOT=/app/data/staticfiles

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN grep -v '^torch==' requirements.txt > requirements.container.txt && \
    pip install --upgrade pip && \
    pip install --index-url https://download.pytorch.org/whl/cpu torch==2.11.0 && \
    pip install -r requirements.container.txt && \
    rm requirements.container.txt

COPY . .

RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
