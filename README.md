# NetAssist

Prototipo educativo de asistente de soporte para MikroTik RouterOS y Cisco IOS. Usa FastAPI, recuperación local de manuales (RAG), Gemini con failover a Groq y una interfaz web en HTML, CSS y JavaScript sin frameworks.

La evolución acordada es una aplicación web de laboratorio con formularios y chat contextual, comenzando por Cisco, VLAN y puertos de acceso. El objetivo, las seis fases, las prioridades y las restricciones de aislamiento de bases de datos se conservan en la [memoria del proyecto](docs/MEMORIA_PROYECTO.md). El [mockup HTML](frontend/mockup.html) representa la propuesta de interfaz.

## Inicio rápido en este equipo (Windows / PowerShell)

La ruta del proyecto es `E:\INGENIERIA DE SISTEMAS\Inteligencia artificial\trabajo\Asistente_de_conf_de_redes`.
Con el entorno `.venv` y las dependencias ya instalados, abre **dos terminales**
y ejecuta cada bloque en su terminal. Si es la primera vez, prepara primero el
entorno siguiendo el paso 2 de la guía de Windows de abajo, desde esta ruta.

**Terminal 1 — backend (API, puerto 8000):**

```powershell
cd "E:\INGENIERIA DE SISTEMAS\Inteligencia artificial\trabajo\Asistente_de_conf_de_redes"
$env:FRONTEND_ORIGIN = "http://localhost:5501"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Espera a que aparezca `Application startup complete`. Comprueba el estado en
[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

**Terminal 2 — frontend (página web, puerto 5501):**

```powershell
cd "E:\INGENIERIA DE SISTEMAS\Inteligencia artificial\trabajo\Asistente_de_conf_de_redes"
.\.venv\Scripts\python.exe -m http.server 5501 --bind 127.0.0.1 --directory frontend
```

Abre **[http://localhost:5501/](http://localhost:5501/)** y pulsa **Ir al chat**
para entrar al laboratorio. Deja
ambas terminales abiertas. Para detenerlas, pulsa **Ctrl + C** en cada una.
Este equipo usa 5501 porque el puerto 5500 pertenece a otro servicio.
La guía siguiente usa una ruta de ejemplo en Descargas y el puerto 5500 para
otros equipos; adapta la ruta si guardaste el proyecto en otra carpeta.

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
│   ├── presentacion.html
│   ├── presentacion.css
│   ├── chat.html
│   ├── style.css
│   └── app.js
├── .env.example
├── .gitignore
└── README.md
```

## Inicio en Windows (PowerShell o terminal de VS Code)

**La aplicación se abre en [http://localhost:5500/](http://localhost:5500/).**
Necesitas dejar **dos terminales abiertas**: una para la API y otra para la página.

| Servicio | Dirección | Para qué sirve |
| --- | --- | --- |
| Página de NetAssist | [http://localhost:5500/](http://localhost:5500/) | Presentación; pulsa Ir al chat para abrir el laboratorio. |
| Estado de la API | [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) | Permite comprobar que el servicio está listo. |
| Documentación de la API | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Consulta técnica opcional. |

### 1. Ubícate en la carpeta del proyecto

Descarga y descomprime el repositorio, o clónalo. La carpeta raíz es la que contiene
**README.md**, **backend**, **frontend** y **.env.example**.

Los comandos siguientes suponen que lo guardaste en Descargas con el nombre
`Asistente_de_conf_de_redes`:

```powershell
cd "$env:USERPROFILE\Downloads\Asistente_de_conf_de_redes"
```

**Adapta esa ruta a tu equipo.** Si descargaste un ZIP de GitHub, la carpeta puede
llamarse `Asistente_de_conf_de_redes-main` o `Asistente_de_conf_de_redes-elliot`;
usa el nombre real. No ejecutes los comandos desde `backend` ni desde `frontend`:
las instrucciones de esta guía parten siempre de la raíz.

### 2. Prepara el entorno (solo la primera vez)

Instala Python 3.11 y verifica que está disponible:

```powershell
py -3.11 --version
```

Desde la raíz del proyecto, crea el entorno e instala sus dependencias:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

Usamos directamente el Python de `.venv`, por lo que **no necesitas activar el
entorno ni cambiar la política de ejecución de PowerShell**. Si ya tenías un
entorno llamado `venv`, estos comandos crean otro llamado `.venv` para esta guía.

Crea la configuración local si todavía no existe:

```powershell
if (-not (Test-Path -LiteralPath ".env")) {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
}
```

Abre `.env` y comprueba esta línea:

```dotenv
FRONTEND_ORIGIN=http://localhost:5500
```

Para las respuestas de IA de Nexo, configura `GEMINI_API_KEY` o `GROQ_API_KEY`
y el modelo correspondiente. Se intenta Gemini primero y Groq como respaldo.
Obtén tus claves en [Google AI Studio](https://aistudio.google.com/) y
[Groq Console](https://console.groq.com/). Los modelos deben estar habilitados
para tu cuenta. **Cada persona necesita sus claves locales:** `.env` no se sube
al repositorio y los secretos de GitHub Actions no configuran la aplicación en
el equipo de tus amigos.

Sin claves puedes probar formularios, preparar comandos del caso desde Nexo,
generar la topología, analizar evidencia y guardar prácticas. Las respuestas
conceptuales de IA necesitan un proveedor configurado y los manuales disponibles.

Necesitas Internet durante la instalación y la primera descarga del modelo de
embeddings. El proyecto ya incluye manuales de ejemplo; no necesitas añadir
archivos para empezar. Puedes incorporar otros `.txt` o `.pdf` en `docs/`;
los PDF escaneados requieren OCR previo.

### 3. Terminal 1: inicia la API

```powershell
cd "$env:USERPROFILE\Downloads\Asistente_de_conf_de_redes"
$env:FRONTEND_ORIGIN = "http://localhost:5500"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Espera a que aparezca **`Application startup complete`**. La primera carga puede
tardar varios minutos mientras se descarga y prepara el modelo. Deja esta
terminal abierta. El inicio crea o recupera el índice exclusivo del proyecto en
`backend/chroma_db/`; las prácticas se guardan en `.data/netassist/cases.sqlite3`.

Puedes comprobar el servicio en
[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health): debe mostrar
`"status":"ok"` y, cuando los manuales estén listos, `"rag_ready":true`.

### 4. Terminal 2: inicia la página

Abre **otra terminal** y ejecuta:

```powershell
cd "$env:USERPROFILE\Downloads\Asistente_de_conf_de_redes"
.\.venv\Scripts\python.exe -m http.server 5500 --bind 127.0.0.1 --directory frontend
```

Cuando aparezca `Serving HTTP`, abre **[http://localhost:5500/](http://localhost:5500/)**
en el navegador. También puedes usar [http://127.0.0.1:5500/](http://127.0.0.1:5500/).

**Escribe solo esa dirección:** no añadas `/frontend/` ni `/presentacion.html`.
El servidor ya sirve `frontend`: `index.html` abre la presentación. Pulsa
**Ir al chat** para abrir el laboratorio con Nexo, o entra directamente en
[http://localhost:5500/chat.html](http://localhost:5500/chat.html).

### Para volver a iniciar otro día

Repite únicamente los pasos **3 y 4**, en dos terminales. No necesitas reinstalar
las dependencias ni copiar `.env` cada vez. Para detener cada servicio, pulsa
**Ctrl + C** en su terminal. Guarda tu práctica antes de cerrar o recargar la web.

### Si aparece un error

| Lo que ves | Qué hacer |
| --- | --- |
| `{"detail":"Not Found"}` al abrir `127.0.0.1:8000/` | Una API antigua puede devolver ese error. Abre **http://localhost:5500/**. La versión actual también abre la presentación desde la raíz de la API. |
| Error 404 en `/frontend/presentacion.html` | Abre **http://localhost:5500/**. Esa ruta no corresponde al inicio de la aplicación. |
| `No module named uvicorn` | Instala las dependencias del paso 2 y usa `.\.venv\Scripts\python.exe`, como en los ejemplos. |
| No se encuentra `.venv`, `backend` o `frontend` | Revisa el `cd`: debes estar en la raíz real del proyecto, con el nombre correcto de la carpeta descomprimida. |
| Puerto ocupado / error 10048 | Puede haber otro servicio abierto. Si es otra instancia de NetAssist, usa esa instancia o detenla con Ctrl + C; si pertenece a otro programa, elige otro puerto. |
| «Servicio sin conexión» | Mantén la API abierta, espera el fin del inicio y comprueba `/health`. Usa el mismo puerto de frontend en la terminal y en `FRONTEND_ORIGIN`. |
| `Failed to send telemetry event ... capture()` | Es un fallo al enviar telemetría de ChromaDB. Si después aparece `Application startup complete`, ese mensaje no impidió iniciar la API. Comprueba `/health` para conocer el estado real. |
| Sigues viendo una interfaz anterior | Guarda primero y recarga con **Ctrl + F5**. |

**Si el puerto 5500 está ocupado**, usa 5501 en las dos terminales: en la primera
cambia `$env:FRONTEND_ORIGIN` a `http://localhost:5501` antes de iniciar la API;
en la segunda cambia `http.server 5500` a `http.server 5501`. Después abre
[http://localhost:5501/](http://localhost:5501/). Reinicia la API si ya estaba abierta.
El puerto 8000 de la API debe mantenerse porque el frontend lo utiliza.

### macOS o Linux

Desde la raíz, prepara el entorno una vez:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
[ -f .env ] || cp .env.example .env
```

Configura `.env` como se explica arriba. En una terminal, desde la raíz:

```bash
FRONTEND_ORIGIN=http://localhost:5500 .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

En otra terminal, también desde la raíz:

```bash
.venv/bin/python -m http.server 5500 --bind 127.0.0.1 --directory frontend
```

Abre [http://localhost:5500/](http://localhost:5500/) y deja ambos servicios abiertos.

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
4. **Faltan datos del equipo:** pregunta por un cambio de configuración sin marca ni modelo; NetAssist debe preguntar esos datos antes de proponer el cambio. La versión solo se pide cuando afecta a la sintaxis del escenario.
5. **Advertencia de riesgo:** consulta cómo reiniciar o cambiar acceso remoto; la respuesta debe advertir el riesgo antes del comando y recomendar respaldo.
6. **Derivación humana:** reporta una falla física o un caso que persiste tras varios intentos; la respuesta debe recomendar contacto y mostrar la información configurada.
7. **Failover con API primaria caída:** simula error o timeout de Gemini; la solicitud debe intentar Groq y responder sin revelar claves.
8. **Todas las APIs caídas / error de servicio:** simula fallos en Gemini y Groq o detén el backend; la interfaz debe mostrar un mensaje amable y una vía de contacto humano, sin quedarse en estado «escribiendo».

## Demostración (fase 6)

La sección **Demostración guiada** carga seis escenarios sintéticos: correcto,
puerto incorrecto, modelo pendiente, conflicto de puertos, salida paginada y
corrección posterior. Pide los comandos a Nexo y utiliza Analizar evidencia para el contraste.
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
VLAN y puertos después; el panel mostrará lo que falta. Pulsa
**Abrir práctica** para trabajar sin escribir primero al chat. **Completar con un
ejemplo** precarga un escenario ilustrativo que debes revisar.

- **Configuración:** resumen de requisitos y datos pendientes. Abre Nexo y pulsa **Preparar comandos** en el bloque **Configuración inicial**. Los comandos aparecen en el chat con botón Copiar; el panel conserva el resumen y el plan de comprobación. El modelo es obligatorio; no se solicita versión de IOS. La compatibilidad requiere revisión manual.
- **Comprobaciones:** incorpora una captura por comando y pulsa **Analizar evidencia**.
  Se contrastan `show vlan brief` y `show interfaces <puerto> switchport`; los
  hallazgos citan el fragmento y la captura. Conserva hasta 12 registros en la
  pestaña y usa el más reciente por comando. Esto no prueba conectividad.
- **Fuentes:** referencias disponibles para este escenario.
- **Tu asistente:** chat contextual, minimizable y ampliable, conectado a `/chat`.

Pulsa **Guardar práctica**, junto al formulario, para conservar los campos actuales
y el caso en SQLite. Reábrelo desde su tarjeta en **Mis prácticas**, en el menú izquierdo.
**Vaciar** limpia el formulario y mantiene las prácticas guardadas. Recargar descarta cambios sin guardar; actualizar requisitos
reinicia chat y evidencia en memoria. Consulta [fase 5](docs/FASE_5.md).
El indicador de conexión permite volver a comprobar el servicio al pulsarlo.

`POST /chat` admite un objeto `context` opcional con `title`, `vendor` (Cisco IOS),
`model`, `version`, `connections`, `groups` (dos objetos con `name`, `vlan`, `ports`),
`review_command` y `evidence`. Sus tamaños están limitados; los mensajes sin
contexto continúan admitidos.

Desde fase 4 se añade `evidence_records` (hasta 12 objetos `{command, output}`)
al contexto. El chat recibe el diagnóstico calculado y los pasos registrados.
Los registros permanecen en memoria hasta pulsar Guardar práctica; entonces se conservan con el caso.

En el equipo original de desarrollo se usa **5501** porque 5500 pertenece a
otro servicio. Esa es una situación local: en tu equipo puedes seguir esta guía
con **5500**, o elegir **5501** si 5500 está ocupado.
Para el puerto local configurado se admiten tanto `localhost` como `127.0.0.1`.

## Capturas de pantalla en Nexo

Pulsa **+** junto al mensaje para adjuntar una captura, o pégala con **Ctrl+V**
dentro del chat. Revisa la vista previa, escribe tu pregunta y envía. Puedes
quitarla antes de enviarla, o enviar solo la imagen para pedir una revisión.
Se admiten PNG, JPG y WebP estáticos de hasta **3 MB**, una imagen por mensaje
y hasta **3 capturas por conversación**. Usa Limpiar chat para iniciar otra.

Nexo envía la captura al proveedor de IA para interpretarla. Usa Gemini y,
si falla, `GROQ_VISION_MODEL` como respaldo (por defecto `qwen/qwen3.8-27b`,
que debe estar habilitado en la cuenta). Las consultas de texto mantienen
`GROQ_MODEL`. Si no hay servicio de visión, conserva el adjunto para reintentarlo.

Las capturas enviadas se conservan al **Guardar práctica**, se recuperan con
el chat y aparecen en los informes HTML y JSON. No se crean bases nuevas ni
se modifica el esquema de SQLite. Los adjuntos no enviados se descartan al
limpiar el chat o cambiar de práctica.

La lectura de una imagen es orientativa y puede omitir texto pequeño o borroso.
No alimenta automáticamente el diagnóstico exacto de Comprobaciones ni prueba
conectividad. El análisis por código sigue usando las salidas en texto.

Referencias de implementación: [imágenes en Gemini](https://ai.google.dev/gemini-api/docs/image-understanding)
y [visión en Groq](https://console.groq.com/docs/vision).

## Topología visual en el chat

Abre una práctica o carga un escenario de demostración y pide a Nexo
**«Muéstrame una imagen de la topología de mi práctica»**. También puedes
pulsar **Ver mi topología** en su bienvenida. La imagen muestra un switch,
una PC por puerto de acceso y los dos grupos VLAN del caso abierto.

Puedes ampliar y descargar la imagen SVG. Se conserva en la conversación
al guardar la práctica y se incluye en el informe HTML. El dibujo se genera
por código a partir de los datos del caso, sin un proveedor de imágenes ni
credenciales adicionales. Las consultas habituales siguen usando la IA del chat.

Alcance: un switch Cisco IOS, dos VLAN y hasta 32 PC conectadas directamente.
Solicita VLAN y puertos faltantes y rechaza asignaciones en conflicto; modelo e
IOS no son obligatorios para dibujar. No interpreta libremente inventarios desde
texto ni asigna direcciones IP. Es una propuesta visual: no crea un archivo `.pkt`,
no controla Packet Tracer y no demuestra conectividad.

Las sugerencias de continuación de Nexo aparecen como un botón opcional relacionado
con la pregunta recién respondida. No se envían automáticamente. Tras preparar
los comandos, la continuación propone comprobar esa configuración; las consultas
conceptuales usan una sugerencia del proveedor, que puede omitirse si no aporta.
