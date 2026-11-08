# Memoria del proyecto NetAssist

Última actualización: 8 de noviembre de 2026.

Este documento conserva las decisiones de producto acordadas con el usuario. Es una referencia para continuar el proyecto; las fases siguientes describen trabajo previsto y no implican que esté implementado.

## Lo que se busca

Convertir NetAssist en una aplicación web para preparar, explicar y contrastar prácticas de configuración de redes. El usuario debe poder iniciar una tarea desde formularios, sin tener que escribir primero al chat.

La primera versión se concentra en un flujo completo de Cisco: separar Administración y Laboratorio mediante VLAN y puertos de acceso. Es preferible demostrar ese escenario con profundidad y evidencia de laboratorio antes de ampliar simultáneamente a OSPF, NAT y ambas marcas.

El prototipo actual incluye soporte conversacional para Cisco IOS y MikroTik RouterOS. Eso no significa que todos esos escenarios formen parte del primer generador estructurado.

## Valor de la IA y responsabilidad del código

La IA generativa transforma requisitos en una propuesta técnica, solicita datos faltantes, explica recomendaciones e interpreta evidencia. Debe responder en función del equipo, la versión, los requisitos y la documentación pertinentes al caso.

Las comprobaciones exactas corresponden a código convencional: por ejemplo, campos obligatorios, identificadores de VLAN distintos, asignaciones de puertos sin conflictos y comparación de datos extraídos de una salida con los requisitos. Los validadores deben tener un alcance explícito; superar una comprobación no demuestra por sí solo el funcionamiento completo de la red.

La aplicación debe distinguir entre:

- Datos incompletos: todavía falta información para preparar una propuesta pertinente.
- Propuesta generada: hay comandos de referencia y una explicación; todavía no se ha demostrado su funcionamiento.
- Comprobaciones automáticas realizadas: determinadas reglas exactas fueron evaluadas por código.
- Evidencia contrastada: una salida aportada permite sostener un hallazgo concreto.
- Pruebas de laboratorio realizadas: se documentan el escenario, la prueba y el resultado observado. No se debe dar este estado por supuesto a partir de los anteriores.

## Flujo de la primera versión

1. El usuario abre una práctica desde un formulario y describe la separación entre Administración y Laboratorio.
2. La aplicación solicita los datos que falten: equipo, modelo, versión, VLAN, puertos y conexiones relevantes.
3. Se produce una propuesta estructurada con requisitos, comandos por equipo, explicaciones, fuentes y pasos de comprobación.
4. El usuario revisa y aplica los comandos en el laboratorio externo.
5. El usuario ejecuta las comprobaciones y pega las salidas como evidencia en el caso.
6. La aplicación contrasta la evidencia con los requisitos y, al incorporar la fase de diagnóstico, propone el siguiente paso concreto sin repetir los ya realizados.

## Interfaz y chat contextual

- Pantalla de laboratorio con formularios, panel de resultados y una estética de redes.
- Resultados organizados en configuración, comprobaciones y fuentes.
- Chat flotante abajo a la derecha, minimizable y ampliable.
- El chat conoce el caso abierto: requisitos, equipo, versión, propuesta, comando que se está revisando, evidencia aportada y pasos realizados cuando estén disponibles.
- Debe permitir preguntas como «¿por qué este comando?» sobre la configuración que el usuario está revisando.
- El formulario permite iniciar y avanzar la tarea; el chat sirve de acompañamiento contextual.

## Relación con Cisco Packet Tracer

Nuestra aplicación se ejecuta en el navegador y Packet Tracer se utiliza como laboratorio externo. El chat pertenece a nuestra web.

Para la primera versión, el intercambio es manual: se copian los comandos desde la web a la CLI del equipo simulado y se pegan las salidas de vuelta en el caso. No se ha acordado una integración automática que controle Packet Tracer, lea archivos `.pkt` o observe su estado.

Las funciones y los comandos deben comprobarse en el modelo y la versión disponibles en la simulación. La aplicación solo puede conocer la evidencia que reciba; no debe afirmar que ha ejecutado o verificado comandos por generar una propuesta.

## Fases acordadas

| Fase | Trabajo principal | Cómo se comprueba que está terminada |
| --- | --- | --- |
| 1. Fortalecer la base | Delimitar el escenario, ampliar documentación y corregir el respaldo de proveedores y la reindexación. | Recupera fuentes pertinentes y conserva el servicio ante los fallos previstos. |
| 2. Crear la interfaz de laboratorio | Formularios, panel de resultados, estética de redes y chat flotante contextual. | Se puede iniciar una tarea sin escribir al chat. |
| 3. Implementar el generador | Primer escenario Cisco: VLAN y puertos de acceso, resultados estructurados y validadores. | Solicita los datos faltantes y una configuración de referencia funciona en laboratorio, con evidencia registrada. |
| 4. Implementar diagnóstico | Analizar salidas del mismo escenario y conservar los pasos realizados. | Cada hallazgo muestra su evidencia y propone una prueba concreta. |
| 5. Guardar casos e informes | SQLite para casos, recuperación de prácticas y exportación. | Se puede reabrir un caso con sus requisitos, resultados y evidencia. |
| 6. Preparar la demostración | Casos correctos, errores, datos incompletos y fallos de proveedor. | Se muestran resultados medidos y límites reales. |

Prioridad acordada: fases 1 a 3 como primera versión; fase 4 como siguiente incremento. El objetivo de la demostración inicial es un flujo de VLAN completo, explicado y contrastado en laboratorio.

## Estado conocido y referencias

- Existe un prototipo con frontend HTML/CSS/JavaScript, backend FastAPI, RAG local en ChromaDB y Gemini con respaldo a Groq. El historial conversacional del prototipo se conserva en el navegador.
- Se preparó un entorno local Python 3.11 y se comprobó la indexación y recuperación de los dos manuales incluidos. Esto no equivale a completar la fase 1 ni a demostrar una configuración de red en laboratorio.
- Se creó una referencia visual interactiva en [frontend/mockup.html](../frontend/mockup.html). Incluye formulario de VLAN, pestañas de configuración/comprobaciones/fuentes y chat ampliable.
- El mockup utiliza datos y respuestas de ejemplo. Sus interacciones sirven para revisar la propuesta de interfaz; no constituyen la implementación del generador o del diagnóstico.
- El usuario pidió el mockup como archivo HTML. Fue entregado en el repositorio y se dejó una copia local en Descargas.
- No se ha confirmado todavía una aprobación final del diseño ni una prueba de la configuración en Packet Tracer.
- La rama de trabajo creada a petición del usuario se llama exactamente `elliot`, desde `main`. Se eliminó la rama remota `codex/preparar-entorno-local` a petición del usuario.

## Restricción persistente de bases de datos

El usuario exige que las conexiones y migraciones del programa no interfieran con ninguna otra base de datos existente.

- La persistencia vectorial actual está en `backend/chroma_db`, dentro del repositorio, y utiliza la colección `manuales_netassist`.
- Antes de inicializar, migrar, reindexar o borrar datos, verificar el destino efectivo y que sea exclusivo de NetAssist. No asumir que un nombre o una variable de entorno garantiza aislamiento.
- La base SQLite de fase 5 está en `.data/netassist/cases.sqlite3`, dentro del proyecto y separada del almacenamiento interno de ChromaDB. No se admiten destinos externos.
- No reutilizar bases ajenas ni detener o reconfigurar sus servicios para ejecutar NetAssist.
- Durante la preparación local se detectó el puerto 5500 ocupado por un proceso `tnslsnr` de Oracle; se eligió el puerto 5501 para el frontend y se mantuvo ese servicio existente.

## Avance real de la fase 1 (8 de noviembre de 2026)

- Se delimitó el caso de referencia en `docs/FASE_1.md`: un switch Cisco y dos grupos con VLAN y puertos de acceso. Los valores y direcciones son ejemplos propuestos para la futura práctica, no requisitos confirmados del usuario.
- Se añadió `docs/cisco_vlan_acceso.txt`, síntesis con referencia oficial de Cisco, recuperable por el buscador. En dos consultas reales sobre asignación y comprobación de VLAN fue el primer resultado (distancias coseno aproximadas 0,370 y 0,382). Corpus: tres archivos, tres fragmentos.
- Se corrigió el respaldo de proveedores: una configuración incompleta del primario ya no impide intentar el secundario. Se cubrieron timeout, respuesta inválida y fallo de ambos con simulaciones; no se hicieron llamadas de validación a Gemini/Groq reales.
- La reindexación construye una colección nueva, verifica su tamaño y publica un manifiesto atómico. Conserva la activa ante fallos de lectura o escritura, permite recuperar la generación publicada tras un reinicio y no bloquea el bucle de solicitudes de la API.
- Se verifica la ruta efectiva antes de abrir ChromaDB; se rechazan enlaces/redirecciones fuera del directorio exclusivo. La caché del modelo usa por defecto `.cache/huggingface` del proyecto.
- Nueve pruebas automatizadas pasaron: respaldo, fallos de reindexación, rechazo de almacenamiento externo y disponibilidad/degradación de la API. No equivalen a una evaluación exhaustiva de relevancia ni a pruebas de redes.
- Límites de operación: un solo proceso de API por almacenamiento; se retienen generaciones anteriores sin limpieza automática. La migración inicial desde el índice heredado requiere una reconstrucción correcta para publicar el primer manifiesto.
- La base de la fase 1 está implementada y comprobada para los casos descritos. Sigue pendiente validar la configuración en Packet Tracer en la fase 3. El generador, la interfaz de laboratorio y el diagnóstico no se implementaron en esta fase.

## Cómo mantener esta memoria

Registrar cambios de alcance, nuevas decisiones y evidencia real de finalización cuando se acuerden o se obtengan. Mantener separados lo implementado, lo representado por el mockup y lo pendiente. No guardar claves, contraseñas ni otros secretos en esta documentación.

## Avance de fase 3: generador implementado (8 de noviembre de 2026)

- Se implementó `POST /generar` y el botón de generación en la interfaz real.
  Produce comandos de referencia para un switch Cisco IOS, dos VLAN y puertos
  de acceso, explicación, reglas comprobadas, fuentes y plan de comprobación.
- Las reglas y la plantilla son deterministas, independientes de RAG y de los
  proveedores. El chat recibe la misma propuesta calculada desde los requisitos
  y puede explicarla con IA. No se implementó generación libre de comandos por IA.
- Solicita datos faltantes y bloquea VLAN iguales o fuera de 2–1001, puertos
  duplicados o compartidos (incluidos alias), rangos y sintaxis no admitida.
  No se valida automáticamente la compatibilidad del modelo/IOS, la existencia
  física de interfaces ni la configuración previa. Esas revisiones son manuales.
- Se verificó en navegador que la versión faltante bloquea la generación y que,
  al completarla, aparecen comandos para VLAN 10 y 20 con cuatro puertos, reglas
  comprobadas y el estado explícito de laboratorio pendiente. El servicio del
  proyecto se reinició en 8000; frontend continúa en 5501.
- Se añadieron pruebas del generador y de su API sin RAG ni proveedor. Las
  pruebas unitarias usan una dependencia de embeddings simulada; no equivalen
  a pruebas de red. El servicio reiniciado sí cargó el índice real del proyecto.
- La práctica reproducible de aceptación está en `docs/FASE_3.md`.
  No se ejecutó en Packet Tracer ni se obtuvo evidencia real de conectividad.
  Por ello la fase 3 sigue abierta hasta completar esa aceptación. El análisis
  automático de salidas y la persistencia de casos siguen pendientes en fases 4 y 5.

## Fase 4: diagnóstico implementado (8 de noviembre de 2026)

- A petición del usuario se continúa con fase 4; la aceptación real en Packet
  Tracer de fase 3 sigue pendiente y no se considera completada por este avance.
- `POST /diagnosticar` contrasta por código `show vlan brief` y
  `show interfaces <puerto> switchport`. Cada hallazgo contiene observado,
  esperado, fragmento literal, número de captura y siguiente paso. Formatos no
  reconocidos y campos insuficientes no se dan por verificados; la ausencia de
  una fila o puerto no se interpreta como fallo.
- La interfaz conserva hasta 12 capturas con comando y salida en memoria de la
  pestaña, permite retirarlas y usa la más reciente por comando. Los pasos
  reconocidos se excluyen de la lista de comandos pendientes. Tras corregir
  una discrepancia se solicita evidencia nueva. El chat recibe el contraste
  recalculado por el servidor junto a los pasos registrados.
- El diagnóstico funciona sin proveedores ni RAG. No ejecuta comandos, no
  verifica conectividad y no inicializa nuevas bases. Persistencia y exportación
  continúan pendientes en fase 5. Los detalles y límites están en `docs/FASE_4.md`.
- Las pruebas de desarrollo usan capturas sintéticas; no representan evidencia
  obtenida de un switch ni una práctica ejecutada en Packet Tracer.
- Pasaron 27 pruebas automatizadas (embeddings simulados en las unitarias),
  comprobación de sintaxis JavaScript y revisión de formato del diff. En la web
  se comprobó la detección de modo trunk/VLAN incorrecta, la incorporación de una
  captura corregida y el uso de esa nueva captura conservando la anterior. Las
  capturas utilizadas en navegador también eran sintéticas.

## Fase 5: guardado e informes (8 de noviembre de 2026)

- Se implementó SQLite exclusivo en `.data/netassist/cases.sqlite3`, separado
  de ChromaDB. La ruta es fija y se verifican padres, archivo y auxiliares antes
  de abrir. Se rechazan redirecciones, enlaces físicos compartidos y bases sin
  la identificación y versión propias de NetAssist. Los datos se excluyen de Git.
- La interfaz permite guardar explícitamente, listar, reabrir y actualizar casos
  con requisitos, capturas, conversación y resultados solicitados. Se pueden
  guardar datos incompletos. Los resultados se calculan en el servidor al guardar.
- Las revisiones evitan sobrescribir cambios de otra pestaña. No hay historial
  completo de versiones ni autosalvado; editar requisitos sigue reiniciando chat
  y evidencia del caso en memoria hasta que se guarde de nuevo.
- Se implementó exportación HTML y JSON de la versión guardada. El informe
  diferencia propuestas y contraste de capturas de la validación real en
  laboratorio, que continúa pendiente. No se genera PDF ni se importan archivos.
- Uso local, sin cuentas ni permisos multiusuario. El detalle está en
  `docs/FASE_5.md`. La preparación de la demostración sigue en fase 6.
- Se comprobó en navegador: guardar, recargar, reabrir requisitos/resultados y
  evidencia sintética, guardar una segunda revisión y descargar el informe HTML.
  Las pruebas unitarias usan SQLite real en carpetas temporales del proyecto y
  embeddings simulados; no constituyen pruebas de configuración de redes.
- Pasaron 35 pruebas automatizadas, la comprobación de sintaxis JavaScript y
  la revisión de formato del diff. La base real de casos quedó dentro de la ruta
  exclusiva indicada y contiene una práctica identificada como evidencia sintética.

## Comprobación posterior de proveedores

Se configuró localmente la credencial de Gemini aportada por el usuario, sin
incluirla en el repositorio. La llamada real a gemini-2.5-flash devolvió HTTP 404:
el servicio indicó que no estaba disponible para usuarios nuevos y sugirió
gemini-3.8-flash. Se dejó este último modelo configurado; dos intentos reales
agotaron el tiempo de espera (15 y 45 segundos). No se ha confirmado una respuesta
correcta ni la validez de la credencial. Groq continúa sin clave configurada.
Las pruebas simuladas previas no demuestran disponibilidad de estos servicios.

## Nuevas claves y pruebas reales (8 de noviembre de 2026)

El usuario proporcionó nuevas credenciales para ambos proveedores. Se guardaron
solo en `.env`, excluido de Git. No se registran secretos en esta memoria.
Ambos endpoints de listado de modelos devolvieron HTTP 200 con las nuevas claves.

- `llama-3.3-70b-versatile` devolvió HTTP 404 en Groq. Se seleccionó un modelo
  anunciado por esa cuenta: `openai/gpt-oss-20b`, que respondió correctamente
  en una prueba directa (aproximadamente 0,97 s).
- `gemini-3.8-flash` volvió a agotar 15 s. Se probó `gemini-3.1-flash-lite`,
  anunciado por el servicio, y respondió correctamente (aproximadamente 2,05 s).
- Los dos modelos que respondieron quedaron configurados en `.env`.
- En el flujo de NetAssist con instrucciones del sistema y contexto Cisco,
  Gemini produjo una respuesta real sin usar Groq. Al forzar una caída de Gemini,
  Groq produjo una respuesta real de respaldo (aproximadamente 0,70 s).
- La repetición mostró variabilidad: hubo respuestas de Gemini y un timeout real
  de Gemini seguido de respuesta correcta de Groq. Por tanto, se comprobó el
  respaldo tanto ante fallo simulado del primario como ante timeout real. Esto no
  garantiza disponibilidad permanente; Gemini presenta tiempos intermitentes.
- Se volvieron a ejecutar las nueve pruebas automatizadas y pasaron.

No se realizaron pruebas de configuración en Packet Tracer ni una prueba desde
la interfaz del navegador durante estas comprobaciones de proveedores.

## Fase 2 implementada: interfaz de laboratorio

- `frontend/index.html`, `style.css` y `app.js` ahora contienen la interfaz de
  laboratorio real: formulario Cisco, dos grupos VLAN, resumen de requisitos,
  datos pendientes y paneles de configuración, comprobaciones y fuentes.
- Se abre una práctica desde el formulario sin enviar mensajes al chat ni
  requerir conexión al proveedor. El ejemplo precarga datos ilustrativos, no
  crea resultados de laboratorio. Modelo, versión, VLAN y puertos pueden quedar
  pendientes; los validadores técnicos del generador siguen en la fase 3.
- Chat flotante minimizable y ampliable, con contexto del caso abierto. El
  backend acepta `context` opcional y acotado en `/chat`, añade los datos a la
  consulta del usuario e incluye el escenario Cisco en la recuperación RAG.
  La ruta anterior sin contexto sigue siendo compatible.
- El usuario puede registrar un comando y pegar evidencia manualmente. Solo se
  incorpora al contexto cuando pulsa «Incorporar al caso». No se analiza ni se
  marca la red como verificada por esa acción. Las fuentes del panel se presentan
  como referencias disponibles, no como citas efectivamente recuperadas.
- Se conserva la práctica y el chat en memoria de la pestaña; recargar los borra.
  Actualizar la práctica reinicia chat y evidencia para evitar arrastrar datos
  de otro escenario; esta consecuencia se indica junto al formulario. La
  persistencia de casos de la fase 5 sigue pendiente. El historial anterior de
  `localStorage` no se reutiliza en un caso nuevo.
- Se comprobaron en navegador: apertura de práctica sin chat, datos incompletos,
  pestañas y navegación con flechas, incorporación manual de evidencia de prueba,
  chat ampliado/minimizado y vista móvil (390 px) sin desbordamiento horizontal.
- Una consulta real desde la interfaz reconoció VLAN 10 para Administración y
  la versión de IOS pendiente usando los datos del formulario. También se observó
  el mensaje de error de conexión sin perder el caso abierto. El servicio local
  se dejó en frontend 5501 y backend 8000, sin usar el puerto 5500 de Oracle.
- Pasaron 11 pruebas unitarias (nueve existentes y dos nuevas para el contrato de
  contexto/evidencia y rechazo de evidencia demasiado extensa). En esta ejecución
  se simuló la dependencia de embeddings para no cargar PyTorch en las pruebas
  unitarias; la consulta del navegador sí utilizó el servicio RAG real.
- No se implementó el generador estructurado, el diagnóstico automático ni la
  persistencia en base de datos. No se realizaron pruebas de configuración en
  Packet Tracer. El mockup original sigue siendo una referencia independiente.
