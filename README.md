# NetAssist

Prototipo educativo de un asistente de soporte para **MikroTik RouterOS** y
**Cisco IOS**. Usa FastAPI, recuperación local de manuales (RAG), Gemini con
respaldo en Groq y una interfaz web en HTML, CSS y JavaScript sin frameworks.

## Requisitos

- Python 3.11 o superior.
- Internet durante la instalación y la primera descarga del modelo de
  embeddings.
- Una clave de `GEMINI_API_KEY` o `GROQ_API_KEY` para las respuestas de IA.

## Inicio rápido en Windows

Todos los comandos deben ejecutarse desde la carpeta raíz del proyecto, la que
contiene `README.md`, `backend` y `frontend`.

### 1. Crear el entorno e instalar dependencias

```powershell
cd "$env:USERPROFILE\Downloads\Asistente_de_conf_de_redes"
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Si el proyecto está en otra carpeta, adapta el comando `cd`. No es necesario
activar el entorno virtual: la guía usa directamente su ejecutable.

### 2. Crear la configuración local

```powershell
if (-not (Test-Path -LiteralPath ".env")) {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
}
```

Edita `.env` y completa al menos una de estas claves:

```dotenv
GEMINI_API_KEY=
GROQ_API_KEY=
```

También puedes ajustar `GEMINI_MODEL`, `GROQ_MODEL`, `FRONTEND_ORIGIN`,
`SUPPORT_CONTACT`, `EMBEDDING_MODEL`, `RAG_TOP_K` y
`RAG_DISTANCE_THRESHOLD`. El archivo `.env` es local y no debe publicarse.

### 3. Iniciar la API

Abre una terminal y ejecuta:

```powershell
cd "$env:USERPROFILE\Downloads\Asistente_de_conf_de_redes"
$env:FRONTEND_ORIGIN = "http://localhost:5500"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Espera el mensaje `Application startup complete`. La primera ejecución puede
tardar mientras descarga y prepara el modelo. Comprueba el estado en
[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

### 4. Iniciar el frontend

Abre una segunda terminal:

```powershell
cd "$env:USERPROFILE\Downloads\Asistente_de_conf_de_redes"
.\.venv\Scripts\python.exe -m http.server 5500 --bind 127.0.0.1 --directory frontend
```

Abre [http://localhost:5500/](http://localhost:5500/) en el navegador y pulsa
**Ir al chat**. Para detener ambos servicios, pulsa `Ctrl+C` en sus terminales.

Si el puerto 5500 está ocupado, usa 5501 en ambos comandos y cambia
`FRONTEND_ORIGIN` a `http://localhost:5501`.

## Inicio en macOS o Linux

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
[ -f .env ] || cp .env.example .env
```

En una terminal inicia la API:

```bash
FRONTEND_ORIGIN=http://localhost:5500 .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

En otra inicia el frontend:

```bash
.venv/bin/python -m http.server 5500 --bind 127.0.0.1 --directory frontend
```

Después abre [http://localhost:5500/](http://localhost:5500/).

## Estructura

```text
Asistente_de_conf_de_redes/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── cases.py             # Persistencia e informes de prácticas
│   ├── chat_actions.py      # Acciones del chat
│   ├── chat_images.py       # Validación de imágenes
│   ├── config.py            # Configuración de entorno
│   ├── diagnostics.py       # Diagnóstico de evidencias
│   ├── generator.py         # Generación de configuraciones
│   ├── topology.py          # Topologías SVG
│   ├── llm.py               # Gemini y Groq
│   ├── rag.py               # Recuperación de manuales
│   ├── prompts.py
│   └── requirements.txt
├── docs/
│   ├── cisco_ios_basico.txt
│   └── mikrotik_basico.txt
├── frontend/
│   ├── index.html
│   ├── presentacion.html
│   ├── chat.html
│   ├── app.js
│   ├── style.css
│   └── presentacion.css
├── .env.example
├── .gitignore
└── README.md
```

Al iniciar la API se crea o reutiliza el índice local en `backend/chroma_db/`.
Las prácticas se guardan en `.data/netassist/cases.sqlite3`.

## Endpoints principales

- `GET /` y `GET /Presentacion`: presentación de la aplicación.
- `POST /chat`: consulta contextual al asistente.
- `POST /generar`: genera una propuesta de configuración Cisco VLAN/acceso.
- `POST /diagnosticar`: analiza evidencias de comandos Cisco.
- `POST /topologia/imagen`: genera la topología SVG de una práctica.
- `GET /health`: informa el estado de la API y del índice RAG.
- `GET /contacto`: devuelve el contacto de soporte configurado.
- `POST /reindexar`: reconstruye el índice desde `docs/`.
- `GET/POST /casos`: lista o guarda prácticas.
- `GET/PUT /casos/{id}`: consulta o actualiza una práctica.
- `GET /casos/{id}/informe?formato=html|json`: exporta una práctica.

## Uso del laboratorio

La interfaz permite:

- Crear una práctica con proveedor, modelo, VLAN y puertos.
- Conversar con Nexo usando el contexto de la práctica.
- Preparar comandos de configuración y copiar sus resultados.
- Registrar evidencias y analizarlas con `show vlan brief` y
  `show interfaces <puerto> switchport`.
- Adjuntar capturas PNG, JPG o WebP de hasta 3 MB.
- Generar y descargar una topología SVG.
- Guardar prácticas y exportarlas como HTML o JSON.

Las imágenes y las respuestas de IA son orientativas. No ejecutan comandos en
equipos reales, no crean archivos de Packet Tracer y no sustituyen la
documentación oficial ni una validación en laboratorio.

## Solución de problemas

| Mensaje | Solución |
| --- | --- |
| `No module named uvicorn` | Instala `backend\requirements.txt` usando `.\.venv\Scripts\python.exe`. |
| `No module named backend.cases` | Comprueba que exista `backend\cases.py` y que ejecutes Uvicorn desde la raíz del proyecto. |
| `No se encuentra .venv` | Repite el paso de creación del entorno desde la raíz. |
| `Address already in use` o error 10048 | Libera el puerto o usa 5501 para el frontend. |
| «Servicio sin conexión» | Mantén la API abierta, espera `Application startup complete` y revisa `/health`. |
| `Failed to send telemetry event` de ChromaDB | Si después aparece `Application startup complete`, el aviso no impidió iniciar la API. |

No introduzcas contraseñas ni otros datos sensibles en el chat, las capturas o
las prácticas guardadas.
