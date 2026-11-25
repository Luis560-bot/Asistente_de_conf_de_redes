# NetAssist

Asistente educativo para prácticas de redes (**Cisco IOS** y **MikroTik RouterOS**). Usa FastAPI, recuperación local de manuales (RAG con ChromaDB), Gemini con respaldo en Groq y una interfaz web en HTML, CSS y JavaScript.

## Requisitos

- Python 3.11 o superior.
- Una clave de `GEMINI_API_KEY` o `GROQ_API_KEY`.
- Conexión a internet para instalar dependencias y descargar el modelo de embeddings la primera vez.

## Instalación y ejecución

Desde la carpeta raíz del proyecto:

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
copy .env.example .env
```

### macOS / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
```

Edita `.env` y agrega al menos una clave (`GEMINI_API_KEY` o `GROQ_API_KEY`).

### Iniciar el servidor

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

FastAPI sirve la API y la interfaz web en el mismo puerto:

- Aplicación: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Laboratorio directo: [http://127.0.0.1:8000/frontend/chat.html](http://127.0.0.1:8000/frontend/chat.html)
- Estado del servicio: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Documentación interactiva de la API: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Para detenerlo, pulsa `Ctrl+C`.

## Estructura

- `backend/` — API FastAPI, integración LLM/RAG, generación de configuraciones, diagnóstico de evidencias y topologías SVG.
- `frontend/` — Presentación, laboratorio de prácticas y chat contextual con Nexo.
- `docs/` — Manuales base indexados por el RAG.
- `.env.example` — Plantilla de variables de entorno.

Al iniciar se crean automáticamente el índice vectorial en `backend/chroma_db/` y la base local de prácticas en `.data/netassist/cases.sqlite3`.

## Notas

- Las respuestas, comandos y topologías generadas son orientativas: no ejecutan cambios en equipos reales ni reemplazan la verificación en laboratorio.
- No introduzcas contraseñas ni datos sensibles en el chat, las capturas o las prácticas guardadas.
