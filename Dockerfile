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

# 1. Instalar dependencias esenciales del sistema operativo (Linux)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 2. Instalar pip optimizado, forzar Torch para CPU (evita que explote la RAM de Railway) y el resto de librerías
RUN grep -v '^torch==' requirements.txt > requirements.container.txt && \
    pip install --upgrade pip && \
    pip install --index-url https://download.pytorch.org/whl/cpu torch==2.4.0 && \
    pip install -r requirements.container.txt && \
    rm requirements.container.txt

# 3. Copiar todo el código fuente de tu proyecto al contenedor
COPY . .

# 4. Asegurar que existan los directorios donde Django y Chroma guardarán los datos
RUN mkdir -p /app/data/docs /app/data/chroma_db /app/data/staticfiles

EXPOSE 8000

# 5. Pipeline secuencial de inicio: Migraciones -> Preparar carpetas -> Ingesta de PDFs -> Iniciar Gunicorn
CMD ["sh", "-c", "python manage.py migrate && mkdir -p ./data/docs && cp -n demo-data/docs/*.pdf ./data/docs/ && python manage.py ingest_pdfs --docs-dir ./data/docs && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT}"]