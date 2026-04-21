# Plataforma Inteligente de Asistencia Académica para Estudiantes - Backend

Backend en Django para consultas académicas en lenguaje natural sobre documentos PDF oficiales. El servicio expone endpoints REST bajo `/api/`, usa SQLite para persistencia básica y ChromaDB para el índice vectorial del flujo RAG.

## Requisitos previos

- `Python 3.10` o `3.11` para desarrollo local
- `Git`
- `Podman` o `Docker` para correr el contenedor
- `cloudflared` si vas a publicar el backend mediante Cloudflare Tunnel
- Una API key de Groq en `LLM_API_KEY`

## Variables de entorno

1. Crea tu archivo local:

```bash
cp .env.template .env
```

2. Ajusta al menos estas variables:

- `SECRET_KEY`: clave secreta de Django.
- `LLM_API_KEY`: API key usada por `ChatGroq`.
- `ALLOWED_HOSTS`: hosts permitidos por Django, separados por comas.
- `CORS_ALLOWED_ORIGINS`: orígenes del frontend que pueden consumir la API.
- `CSRF_TRUSTED_ORIGINS`: hosts HTTPS confiables para admin y requests con sesión.
- `SQLITE_PATH`, `DOCS_DIR`, `VECTOR_DB_PATH`, `STATIC_ROOT`: rutas persistentes del contenedor. El `Dockerfile` ya apunta a `/app/data/...`.

Si vas a exponer la app con un dominio público, ese dominio debe estar en `ALLOWED_HOSTS` y normalmente también en `CSRF_TRUSTED_ORIGINS`.

## Flujo local con Python

```bash
git clone https://github.com/saaaan25/academic-assistant.git
cd academic-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
mkdir -p data/docs data/chroma_db data/staticfiles
python manage.py migrate
python manage.py runserver
```

Para cargar PDFs de prueba:

```bash
cp -n demo-data/docs/*.pdf data/docs/
python manage.py ingest_pdfs --docs-dir ./data/docs
```

La primera ingesta puede tardar porque descarga el modelo de embeddings si todavía no está en caché.

## Flujo con Podman o Docker

### 1. Preparar archivos persistentes

```bash
cp .env.template .env
mkdir -p data/docs data/chroma_db data/staticfiles
cp -n demo-data/docs/*.pdf data/docs/
```

El contenedor guarda estos datos en `./data`:

- `data/db.sqlite3`
- `data/docs/`
- `data/chroma_db/`
- `data/staticfiles/`

### 2. Construir la imagen

Con Podman:

```bash
podman build -t academic-assistant .
```

Con Docker:

```bash
docker build -t academic-assistant .
```

### 3. Levantar el backend

Con Podman:

```bash
podman run --name academic-assistant --rm \
  -p 8000:8000 \
  --env-file .env \
  -v "$PWD/data:/app/data:Z" \
  academic-assistant
```

Con Docker:

```bash
docker run --name academic-assistant --rm \
  -p 8000:8000 \
  --env-file .env \
  -v "$PWD/data:/app/data" \
  academic-assistant
```

Notas:

- El entrypoint crea directorios, ejecuta `python manage.py migrate --noinput` y luego inicia `uvicorn` en `0.0.0.0:8000`.
- Si tu entorno con Podman no usa SELinux, puedes quitar el sufijo `:Z` del volumen.
- El backend queda expuesto en `http://127.0.0.1:8000/`; los endpoints REST cuelgan de `/api/` y el admin de `/admin/`.

### 4. Ingerir PDFs dentro del contenedor

Con el contenedor ya ejecutándose:

Con Podman:

```bash
podman exec -it academic-assistant python manage.py ingest_pdfs
```

Con Docker:

```bash
docker exec -it academic-assistant python manage.py ingest_pdfs
```

El comando omite PDFs ya registrados en la base de datos y genera embeddings en `VECTOR_DB_PATH`.

## Flujo con Cloudflare Tunnel

La aplicación ya está preparada para correr detrás de proxy: el contenedor inicia `uvicorn` con `--proxy-headers` y Django usa `SECURE_PROXY_SSL_HEADER` y `USE_X_FORWARDED_HOST`.

### 1. Define el hostname público

Ejemplo:

- API pública: `api.tudominio.com`
- Frontend público: `https://smart-software.tudominio.com`

Antes de levantar el contenedor, actualiza `.env` con algo equivalente a:

```env
DEBUG=false
ALLOWED_HOSTS=127.0.0.1,localhost,api.tudominio.com,smart-software.tudominio.com
CORS_ALLOWED_ORIGINS=https://smart-software.tudominio.com
CSRF_TRUSTED_ORIGINS=https://api.tudominio.com,https://smart-software.tudominio.com
PORT=8000
```

### 2. Levanta el contenedor en localhost:8000

Usa cualquiera de los comandos de la sección anterior. Cloudflare Tunnel va a publicar ese puerto local.

### 3. Crear un túnel nombrado

```bash
cloudflared tunnel login
cloudflared tunnel create academic-assistant
cloudflared tunnel route dns academic-assistant api.tudominio.com
```

### 4. Crear la configuración de `cloudflared`

Archivo `~/.cloudflared/config.yml`:

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /home/<usuario>/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: api.tudominio.com
    service: http://localhost:8000
  - service: http_status:404
```

### 5. Ejecutar el túnel

```bash
cloudflared tunnel run academic-assistant
```

Con eso, el backend queda publicado en `https://api.tudominio.com/`.

### 6. Probar endpoints

- `https://api.tudominio.com/admin/`
- `https://api.tudominio.com/api/register/`
- `https://api.tudominio.com/api/chat-free/`
- `https://api.tudominio.com/api/login/`

## Túnel temporal para pruebas rápidas

Si solo quieres validar el backend sin crear un túnel nombrado:

```bash
cloudflared tunnel --url http://localhost:8000
```

Ese modo entrega un hostname temporal `*.trycloudflare.com`. Como cambia en cada ejecución, no es práctico para Django salvo que actualices `ALLOWED_HOSTS` cada vez y reinicies el contenedor.
