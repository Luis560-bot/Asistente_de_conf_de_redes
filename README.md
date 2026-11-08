# NetAssist

Prototipo educativo de asistente de soporte para MikroTik RouterOS y Cisco IOS. Usa FastAPI, recuperación local de manuales (RAG), Gemini con failover a Groq y una interfaz web en HTML, CSS y JavaScript sin frameworks.

La evolución acordada es una aplicación web de laboratorio con formularios y chat contextual, comenzando por Cisco, VLAN y puertos de acceso. El objetivo, las seis fases, las prioridades y las restricciones de aislamiento de bases de datos se conservan en la [memoria del proyecto](docs/MEMORIA_PROYECTO.md). El [mockup HTML](frontend/mockup.html) representa la propuesta de interfaz.

## Estructura

```text
netassist/
├── backend/
│   ├── main.py
│   ├── llm.py
│   ├── rag.py
│   ├── prompts.py
│   ├── config.py
│   ├── __init__.py
│   └── requirements.txt
├── docs/
│   ├── mikrotik_basico.txt
│   └── cisco_ios_basico.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── .env.example
├── .gitignore
└── README.md
```

## Requisitos previos

- Python 3.11 o superior.
- Acceso a Internet durante la instalación y la primera descarga del modelo de embeddings.
- Claves de Google AI Studio y Groq para obtener respuestas de LLM y habilitar el failover.

## Instalación y ejecución

1. Abre una terminal en la carpeta `netassist`.
2. Crea y activa un entorno virtual:

   **Windows PowerShell**
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS o Linux**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. Instala las dependencias del backend:

   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r backend/requirements.txt
   ```

4. Copia `.env.example` como `.env` y configura las claves, modelos y contacto humano:

   **Windows PowerShell**
   ```powershell
   Copy-Item .env.example .env
   ```

   **macOS o Linux**
   ```bash
   cp .env.example .env
   ```

   Completa `GEMINI_API_KEY` y `GEMINI_MODEL` para Gemini, y `GROQ_API_KEY` y `GROQ_MODEL` para Groq. NetAssist intenta primero Gemini y usa Groq ante errores o timeout. Si un proveedor no se configura, se intentará el otro. Obtén las claves en [Google AI Studio](https://aistudio.google.com/) y [Groq Console](https://console.groq.com/). Los nombres de modelo son configurables; usa modelos habilitados para tus cuentas y APIs.

5. Coloca manuales `.txt` o `.pdf` en `docs/`. El prototipo incluye dos TXT de ejemplo. Los PDFs se indexan usando el texto que pueda extraerse de sus páginas; documentos escaneados requieren OCR previo.
6. Inicia el backend desde la carpeta `netassist`:

   ```bash
   python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```

   Al primer inicio se descarga el modelo multilingüe de embeddings y se genera la base ChromaDB local en `backend/chroma_db/`. La inicialización puede tardar varios minutos. Comprueba el estado en `http://localhost:8000/health`.

7. En otra terminal, sirve el frontend en el origen permitido:

   **Windows PowerShell**
   ```powershell
   cd frontend
   py -3.11 -m http.server 5500
   ```

   **macOS o Linux**
   ```bash
   cd frontend
   python3 -m http.server 5500
   ```

8. Abre `http://localhost:5500` en el navegador. Si cambias el host o puerto del frontend, actualiza `FRONTEND_ORIGIN` en `.env` y reinicia el backend.

## Endpoints

- `POST /chat`: recibe `{ "messages": [{ "role": "user|assistant", "content": "..." }] }`, recupera hasta cuatro fragmentos relevantes y devuelve `{ "reply": "...", "contact": "..." }`.
- `POST /reindexar`: reconstruye el índice desde los documentos actuales de `docs/`.
- `POST /generar`: recibe los requisitos del caso, indica datos faltantes o errores y genera una propuesta Cisco VLAN/acceso independiente del proveedor. Ver [fase 3](docs/FASE_3.md).
- `POST /diagnosticar`: contrasta capturas de VLAN y switchport, cita evidencia y propone comprobaciones pendientes. Ver [fase 4](docs/FASE_4.md).
- `GET /health`: informa el estado de la API y del índice RAG.
- `GET /contacto`: devuelve el contacto de derivación configurado.
- `GET/POST /casos`, `GET/PUT /casos/{id}`: guardado y recuperación local con revisiones.
- `GET /casos/{id}/informe?formato=html|json`: exportación del caso guardado. Ver [fase 5](docs/FASE_5.md).

La interfaz conserva los cambios en memoria hasta pulsar **Guardar práctica**. Los casos guardados pueden reabrirse con requisitos, resultados, capturas y chat; recargar descarta los cambios sin guardar. Actualizar requisitos reinicia chat y evidencia en memoria. Se envían los últimos 40 mensajes y el contexto del caso en cada consulta. El historial del prototipo guardado en `localStorage` no se reutiliza. No ingreses contraseñas ni datos sensibles.

## RAG y relevancia

El backend acepta `.txt` y `.pdf`, divide el texto en fragmentos de 500 palabras con 50 palabras de solapamiento, genera embeddings localmente e indexa en ChromaDB. En cada turno consulta un máximo de cuatro fragmentos. `RAG_DISTANCE_THRESHOLD` configura el umbral de distancia coseno para tratar un resultado como relevante; ajústalo si el conjunto de manuales requiere otra calibración. Sin fragmentos relevantes, la instrucción del sistema impide inventar referencias.

## Casos de prueba QA

1. **Flujo ideal MikroTik:** pregunta por el estado de una interfaz y proporciona modelo/versión; la respuesta debe citar el manual y sugerir verificación con sintaxis RouterOS.
2. **Flujo ideal Cisco:** reporta conectividad fallida; la guía debe respetar el orden de capa física, IP y enrutamiento, usando los comandos de verificación del manual IOS.
3. **Memoria de la conversación:** ejecuta una verificación, envía su resultado y pregunta por el siguiente paso; el asistente no debe volver a proponer como pendiente el comando ya probado.
4. **Faltan datos del equipo:** pregunta por un cambio de configuración sin marca, modelo ni versión; NetAssist debe preguntar esos datos antes de proponer el cambio.
5. **Advertencia de riesgo:** consulta cómo reiniciar o cambiar acceso remoto; la respuesta debe advertir el riesgo antes del comando y recomendar respaldo.
6. **Derivación humana:** reporta una falla física o un caso que persiste tras varios intentos; la respuesta debe recomendar contacto y mostrar la información configurada.
7. **Failover con API primaria caída:** simula error o timeout de Gemini; la solicitud debe intentar Groq y responder sin revelar claves.
8. **Todas las APIs caídas / error de servicio:** simula fallos en Gemini y Groq o detén el backend; la interfaz debe mostrar un mensaje amable y una vía de contacto humano, sin quedarse en estado «escribiendo».

## Demostración (fase 6)

La sección **Demostración guiada** carga seis escenarios sintéticos: correcto,
puerto incorrecto, versión pendiente, conflicto de puertos, salida paginada y
corrección posterior. Usa los botones habituales para generar y analizar.
El guion, las mediciones y sus límites están en [docs/FASE_6.md](docs/FASE_6.md).

Validación reproducible sin red ni claves:

```powershell
.\.venv\Scripts\python.exe scripts/validate_demo.py --with-tests
```

Los [resultados medidos](docs/RESULTADOS_DEMO.md) distinguen simulaciones y
validación real, que sigue pendiente en Packet Tracer.

## Límites del prototipo

- Los manuales de ejemplo son referencias introductorias, no sustituyen la documentación oficial ni una validación en laboratorio.
- La búsqueda semántica y su umbral deben validarse con el corpus de la institución.
- No ejecutes comandos de cambio sin verificar modelo, versión, topología, permisos y respaldo.

## Base de la fase 1

El alcance, las fuentes y las limitaciones están en [docs/FASE_1.md](docs/FASE_1.md).
El corpus incluye una síntesis de VLAN/puertos de acceso basada en documentación oficial Cisco.
La caché del modelo queda por defecto en `.cache/huggingface` del proyecto.

La reindexación conserva el índice activo si falla y publica una generación nueva
solo al terminar. El manifiesto en `backend/chroma_db` permite recuperar la última
publicación después de reiniciar. Usa un único proceso de API por almacenamiento;
las generaciones previas se retienen sin limpieza automática.

Pruebas de respaldo, reindexación y degradación de API (sin llamadas a proveedores):

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Estas comprobaciones no demuestran funcionamiento en Packet Tracer. La práctica
y su evidencia corresponden a la fase 3.

## Interfaz de laboratorio (fase 2)

Abre el frontend y completa el nombre de la práctica. Puedes registrar modelo,
versión de IOS, VLAN y puertos después; el panel mostrará lo que falta. Pulsa
**Abrir práctica** para trabajar sin escribir primero al chat. **Completar con un
ejemplo** precarga un escenario ilustrativo que debes revisar.

- **Configuración:** resumen de requisitos y datos pendientes. Pulsa **Generar configuración** para obtener comandos, explicaciones, reglas comprobadas y límites. El modelo y la versión son obligatorios; su compatibilidad requiere revisión manual.
- **Comprobaciones:** incorpora una captura por comando y pulsa **Analizar evidencia**.
  Se contrastan `show vlan brief` y `show interfaces <puerto> switchport`; los
  hallazgos citan el fragmento y la captura. Conserva hasta 12 registros en la
  pestaña y usa el más reciente por comando. Esto no prueba conectividad.
- **Fuentes:** referencias disponibles para este escenario.
- **Tu asistente:** chat contextual, minimizable y ampliable, conectado a `/chat`.

Pulsa **Guardar práctica** para conservar el caso en SQLite y reabrirlo desde
**Mis prácticas**. Recargar descarta cambios sin guardar; actualizar requisitos
reinicia chat y evidencia en memoria. Consulta [fase 5](docs/FASE_5.md).
El indicador de conexión permite volver a comprobar el servicio al pulsarlo.

`POST /chat` admite un objeto `context` opcional con `title`, `vendor` (Cisco IOS),
`model`, `version`, `connections`, `groups` (dos objetos con `name`, `vlan`, `ports`),
`review_command` y `evidence`. Sus tamaños están limitados; los mensajes sin
contexto continúan admitidos.

Desde fase 4 se añade `evidence_records` (hasta 12 objetos `{command, output}`)
al contexto. El chat recibe el diagnóstico calculado y los pasos registrados.
Los registros permanecen en memoria hasta pulsar Guardar práctica; entonces se conservan con el caso.

En este equipo usa el puerto **5501** para el frontend y configura
`FRONTEND_ORIGIN=http://localhost:5501`; el puerto 5500 pertenece a otro servicio.
