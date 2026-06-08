FROM docker.io/library/python:3.11-slim

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

# 1. Instalar dependencias del sistema esenciales (incluyendo libpq-dev por si usas postgres en producción)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# 2. Tu optimización genial para instalar Torch CPU y luego el resto
RUN grep -v '^torch==' requirements.txt > requirements.container.txt && \
    pip install --upgrade pip && \
    pip install --index-url https://download.pytorch.org/whl/cpu torch==2.4.0 && \
    pip install -r requirements.container.txt && \
    rm requirements.container.txt

COPY . .

# 3. Crear las carpetas de datos por si Django intenta escribir en ellas al iniciar
RUN mkdir -p /app/data/docs /app/data/chroma_db /app/data/staticfiles

EXPOSE 8000

# ◄--- AQUÍ ESTÁ EL CAMBIO CLAVE: Quitamos ENTRYPOINT y usamos CMD directo ---►
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT