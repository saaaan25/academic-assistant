# Plataforma Inteligente de Asistencia Académica para Estudiantes - Backend

Este proyecto es una plataforma inteligente que permita a los estudiantes consultar y comprender procedimientos académicos e institucionales mediante preguntas en lenguaje natural, basada en documentos oficiales


## Requisitos Previos
Instalaciones necesarias:
* [Python 3.10 o superior](https://www.python.org/downloads/)
* [Git](https://git-scm.com/downloads)

---

## Instalación Local

### 1. Clonar el repositorio
```
git clone https://github.com/saaaan25/academic-assistant.git
cd academic-assistant
```

### 2. Crear entorno virtual y activarlo
```
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias
```
pip install -r requirements.txt
```

### 4. Configurar variables
Leer .env.template y completar según corresponda

### 5. Agregar documentos
Crear carpeta /data/docs en la raíz del proyecto y subir los .pdf oficiales

### 6. Inicializar base de datos
```
python manage.py migrate
```

### 7. Ejecutar servidor
```
python manage.py runserver
```

La app se está ejecutando en [http://127.0.0.1:8000/](http://127.0.0.1:8000/)