# Fase 6: demostración reproducible

## Preparación

Inicia NetAssist siguiendo README.md (API 8000, frontend 5501). No se requiere
una clave de IA para generar comandos, contrastar capturas o guardar casos.
El chat sí requiere proveedor y manuales disponibles. Usa un solo proceso de API.

En «Demostración guiada» elige uno de los seis escenarios y pulsa **Cargar
escenario**. Se abre como práctica nueva, sin guardado automático. Reemplazar
un caso abierto pide confirmar para evitar perder cambios. Los ejemplos están
en `frontend/demo-cases.json`; todos están identificados como sintéticos.

## Guion para presentar

| Escenario | Acción | Resultado que se debe mostrar |
| --- | --- | --- |
| VLAN y acceso correctos | Generar; ir a Comprobaciones y analizar | Comandos para dos VLAN; 18 campos/fila contrastados sin discrepancias. No se declara conectividad verificada. |
| Modo trunk y VLAN equivocada | Analizar evidencia | Fa0/1 muestra dos discrepancias y cita los campos Administrative Mode y Access Mode VLAN. |
| Falta la versión de IOS | Generar | Solicita versión; no entrega comandos de configuración. |
| Puerto asignado a dos grupos | Generar | Bloquea el conflicto entre Fa0/1 y FastEthernet0/1. |
| Salida incompleta o paginada | Analizar evidencia | Evidencia insuficiente, sin hallazgos inventados; show vlan brief sigue pendiente. |
| Corrección con captura posterior | Analizar y desplegar las capturas | Se conserva la captura antigua y se contrasta la más reciente; desaparecen las discrepancias corregidas. |

Con el caso correcto, guarda la práctica, recarga y reábrela desde «Mis
prácticas». Muestra requisitos, comandos, capturas y contraste recuperados.
Descarga HTML y JSON, explicando que corresponden a la revisión guardada.
Estos pasos pueden ejecutarse desde el formulario sin utilizar el chat.

Para explicar el papel de la IA, abre el chat y pregunta por qué se usa modo
access. Una respuesta depende de los manuales y del proveedor; el diagnóstico
exacto y el guardado son funciones de código. No uses respuestas de ejemplo
como prueba de disponibilidad real del chat.

## Mediciones y fallos controlados

Ejecuta desde la raíz:

```powershell
.\.venv\Scripts\python.exe scripts/validate_demo.py --with-tests
```

Evalúa las seis entradas mediante la API en proceso, un recorrido de SQLite y
exportación, y tres estados del chat: primario, timeout con respaldo, y caída
de ambos con derivación humana. El timeout se inyecta como excepción inmediata;
no representa esperar el timeout de red. Se simulan RAG, embeddings y llamadas
a proveedores, manteniendo el flujo real de respaldo. No usa claves ni red.

SQLite se crea en una carpeta temporal comprobada bajo `.cache`, independiente
de las prácticas guardadas y de ChromaDB. Se elimina solo esa carpeta temporal
al terminar. Se generan `.cache/demo-results.json` y
[RESULTADOS_DEMO.md](RESULTADOS_DEMO.md), con estado, alcance y tiempos locales.
Un fallo detiene la validación; no se genera un nuevo informe de éxito.

Para medir proveedores reales (envía dos consultas breves y puede consumir cuota):

```powershell
.\.venv\Scripts\python.exe scripts/check_live_providers.py
```

El resultado está en [PROVEEDORES_DEMO.md](PROVEEDORES_DEMO.md). No imprime ni
registra claves o contenido de respuestas; solo proveedor, modelo, duración y
estado. No confundir disponibilidad puntual con calidad técnica o respaldo real.
Las claves locales se leen de `.env`. Los GitHub Secrets del repositorio están
disponibles para Actions; no se descargan automáticamente al equipo.

## Límites que deben aparecer en la presentación

- Un solo switch Cisco IOS con dos VLAN y puertos de acceso. Sin trunks ni
  enrutamiento inter-VLAN en la propuesta de referencia.
- Los escenarios y sus salidas son sintéticos. La web no controla Packet Tracer.
- Coincidir con capturas no demuestra autenticidad, estado actual, cableado,
  direccionamiento o conectividad. Una fila ausente no se interpreta como fallo.
- La persistencia es local, sin cuentas ni autorización multiusuario. Los
  informes incluyen únicamente datos aplicados al caso y guardados.
- La aceptación real descrita en [FASE_3.md](FASE_3.md) sigue pendiente: registrar
  modelo/IOS reales, comandos aceptados, salidas de VLAN/switchport y ping.

La preparación de software de la demostración se comprueba con los resultados
adjuntos. El objetivo global de demostrar la red funcionando permanece abierto
hasta disponer de esa evidencia real de laboratorio.
