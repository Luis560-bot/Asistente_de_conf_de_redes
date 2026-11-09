# Memoria del proyecto NetAssist

Última actualización: 8 de noviembre de 2026.

Este documento conserva las decisiones de producto acordadas con el usuario. Es una referencia para continuar el proyecto; las fases siguientes describen trabajo previsto y no implican que esté implementado.

## Estado vigente para continuar

- Se prioriza una interfaz sencilla y con poco texto. Guardar y Vaciar están
  junto al formulario; Mis prácticas se abre desde la navegación izquierda.
- La configuración se solicita dentro de Nexo, en Configuración inicial →
  Preparar comandos. El panel conserva requisitos y comprobaciones. El bloque
  de comandos usa el generador validado por código y permite copiarlo.
- La versión de IOS se retiró del formulario y no es requisito para el caso
  básico de Packet Tracer. Se conserva como dato opcional compatible con casos
  antiguos. El modelo, las VLAN y los puertos siguen siendo necesarios.
- Nexo responde brevemente por defecto. Las sugerencias son opcionales y deben
  relacionarse con la pregunta respondida; solo se envían al pulsarlas. Enter
  envía el mensaje y Shift + Enter añade una línea.
- El chat admite adjuntar o pegar capturas PNG, JPG y WebP para interpretación
  visual con IA. No se incorporan automáticamente al contraste exacto de salidas.
  La implementación nueva necesita reiniciar la API local que ya estaba abierta.
- Nexo dibuja la topología del caso abierto, también en la demo: un switch,
  dos VLAN y hasta 32 PC. Es un SVG generado por código, no un archivo .pkt ni
  una generación libre de cualquier red. La aceptación real en Packet Tracer
  y las pruebas de conectividad siguen pendientes.
- La guía de inicio compartida usa frontend 5500 y API 8000, con dos terminales.
  El equipo original usa frontend 5501 porque 5500 pertenece a otro servicio.
  Las secciones históricas siguientes conservan la evolución y la evidencia;
  sus requisitos anteriores quedan sustituidos por estas decisiones vigentes.

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

## Credenciales en GitHub Secrets (8 de noviembre de 2026)

- Se crearon y confirmaron los secretos de repositorio `GEMINI_API_KEY` y
  `GROQ_API_KEY` en GitHub Actions, a petición del usuario. No se publicaron
  los valores ni el archivo `.env` en el historial del repositorio.
- El intento anterior de publicar `.env` fue rechazado por GitHub. Ese commit
  local se excluyó antes de publicar la fase 5. `.env` sigue local e ignorado.
- Los secretos de Actions no configuran por sí solos la aplicación local ni
  ejecutan pruebas: requieren un flujo que los consuma explícitamente.

## Fase 6: preparación de demostración (8 de noviembre de 2026)

- Se añadieron seis escenarios sintéticos cargables en la interfaz: correcto,
  modo/VLAN incorrectos, versión pendiente, conflicto de puertos, paginación y
  corrección mediante captura posterior. Abren una práctica nueva y usan los
  botones reales de generación y contraste, sin respuestas falsas del servicio.
- `scripts/validate_demo.py --with-tests` comprobó 10 recorridos de API y
  35 pruebas unitarias. Se midieron tiempos locales y se registraron límites
  en `docs/RESULTADOS_DEMO.md`. RAG y proveedores están simulados en esa ejecución;
  SQLite usa un directorio temporal exclusivo bajo `.cache`, sin tocar casos existentes.
- El guion de presentación y cómo reproducir las mediciones están en
  `docs/FASE_6.md`. Los estados de proveedor se inyectan solo en el evaluador,
  sin modificar el comportamiento de producción ni las credenciales.
- Se realizaron dos llamadas directas reales con texto sintético: Gemini
  respondió en aproximadamente 2,41 s y Groq en 1,22 s. El detalle puntual está en
  `docs/PROVEEDORES_DEMO.md`. No evalúan calidad técnica, RAG ni disponibilidad futura.
- La preparación de demostración de software queda implementada. No se ha
  ejecutado una práctica real en Packet Tracer: la aceptación de fase 3 y la
  demostración global de conectividad siguen abiertas hasta aportar esa evidencia.

- Se verificó además en navegador la carga de escenarios y los resultados
  correcto, discrepante y con versión pendiente; se mantuvo visible la
  identificación de datos sintéticos. No se guardaron estos escenarios en la
  base de casos durante esta comprobación.

## Identidad del chat: Nexo (8 de noviembre de 2026)

- El usuario pidió sustituir la apariencia genérica del chat por un personaje
  que salude al abrirlo. Se implementó Nexo, un robot de redes dibujado en SVG
  propio, con mano que saluda y ojos animados. No depende de recursos externos.
- El personaje aparece en el acceso flotante, la cabecera y la bienvenida del
  chat. El saludo contextual se presenta visualmente sin añadir turnos falsos
  al historial; reabrir no duplica la bienvenida ni borra la conversación.
- Dos preguntas rápidas rellenan el cuadro para que el usuario pueda editar
  y enviar. No se envían consultas al proveedor por abrir el chat o pulsarlas.
- El asistente se identifica como Nexo de NetAssist en sus instrucciones.
  Se conserva el chat contextual, minimizable y ampliable, abajo a la derecha.
- Se revisaron en navegador la vista de escritorio y móvil (390 px), el saludo,
  los accesos rápidos y la reapertura sin duplicados. Las animaciones respetan
  la preferencia de movimiento reducido. Se comprobó sintaxis JavaScript y SVG.

## Simplificación de prácticas (8 de noviembre de 2026)

- A petición del usuario, se prioriza una interfaz con menos texto y acciones
  junto a la tarea. Guardar práctica y Vaciar están en Prepara tu práctica.
- Mis prácticas presenta tarjetas de los casos guardados con una acción para
  abrirlos. Guardar incluye los campos actuales del formulario sin exigir
  Actualizar práctica antes; repetir el guardado actualiza el mismo caso.
- Vaciar limpia el caso en memoria, previa confirmación si hay datos, y conserva
  los registros guardados. Cambiar requisitos con chat o capturas pide confirmar
  el reinicio de ese contexto; guardar sin cambios conserva ese contenido.
- Ejemplos y exportación quedan en secciones desplegables. Se mantiene el
  almacenamiento exclusivo existente, sin migraciones ni cambios de backend.
- Comprobado en navegador: guardar un formulario incompleto, editar y volver a
  guardar sin duplicar la tarjeta, recargar, reabrir los datos editados y vaciar
  conservando las tarjetas. Se creó un caso identificado como prueba de interfaz
  con datos sintéticos. No se realizaron pruebas de red en Packet Tracer.

## Mis prácticas en la navegación lateral (8 de noviembre de 2026)

- El usuario pidió retirar Mis prácticas del contenido del laboratorio y acceder
  desde el menú izquierdo. Se implementaron vistas separadas de Laboratorio y
  Mis prácticas, con enlace activo y navegación por fragmento de URL.
- Cambiar entre vistas conserva el formulario y el caso en memoria. Las tarjetas
  guardadas se consultan en la biblioteca; abrir una regresa al laboratorio.
  Guardar y Vaciar permanecen junto al formulario. En móvil ambos accesos siguen
  disponibles en la navegación superior adaptable.
- Comprobado en navegador: ausencia del bloque en Laboratorio, apertura de la
  biblioteca desde el menú, carga de tarjetas y conservación de un borrador al
  regresar. Sintaxis JavaScript y formato del diff comprobados. Sin cambios de
  backend, almacenamiento ni pruebas de redes.

## Conexión local del navegador (8 de noviembre de 2026)

- Se reprodujo el error del chat al abrir el frontend en 127.0.0.1:5501:
  la petición previa de CORS devolvía HTTP 400, mientras localhost:5501
  devolvía HTTP 200. La configuración autorizaba solo este último origen.
- Se admiten ambos nombres de loopback para el esquema y puerto configurados.
  Otros puertos, hosts y esquemas siguen bloqueados; un origen externo
  configurado conserva exclusivamente su autorización explícita.
- Pasaron 37 pruebas automatizadas, incluidas dos nuevas de CORS. RAG y
  proveedores se simularon en las unitarias. Se reinició únicamente la API
  del proyecto, verificando antes sus rutas de almacenamiento exclusivo.
- Tras el reinicio, ambos orígenes devolvieron HTTP 200 en la petición previa.
  El índice real quedó listo (tres archivos y tres fragmentos). Una consulta
  HTTP real a /chat con contexto sintético devolvió respuesta de Nexo en 4,66 s
  y el encabezado correcto para 127.0.0.1:5501. Esto verifica transporte y
  disponibilidad puntual, no exactitud técnica ni configuración en laboratorio.

## Envío directo del chat (8 de noviembre de 2026)

- Por petición del usuario, las preguntas sugeridas ahora se envían al pulsarlas,
  sustituyendo el comportamiento anterior de rellenar el cuadro para editar.
- Enter envía el mensaje; Shift + Enter inserta una línea. La composición de
  caracteres no provoca envío. Se conserva el botón de envío y el bloqueo de
  envíos repetidos mientras hay una solicitud en curso; las sugerencias también
  se deshabilitan durante esa espera.
- Comprobado en navegador en 127.0.0.1:5501: envío de una sugerencia con un clic,
  respuesta real del asistente, salto de línea con Shift + Enter y envío del texto
  con Enter. Sintaxis JavaScript y formato del diff comprobados. Sin cambios de
  backend ni pruebas de configuración en laboratorio.

## Topología visual dentro de Nexo (8 de noviembre de 2026)

- El usuario aclaró que necesita solicitar la imagen dentro del chatbot de
  NetAssist, también durante la demo. No pidió una imagen suelta en este chat.
- Implementado: solicitudes como «Muéstrame una imagen de la topología de mi
  práctica» producen una imagen SVG en la conversación, con vista ampliada y
  enlace de descarga. Se añadió el acceso rápido Ver mi topología.
- El servidor reconoce peticiones visuales del escenario y construye el diagrama
  por código desde el caso abierto: un switch, dos VLAN y una PC por puerto,
  hasta 32 PC. No usa un modelo de imágenes ni inventa IP. Solicita VLAN/puertos
  faltantes y rechaza conflictos. Modelo e IOS pueden faltar para este dibujo;
  los requisitos del generador de comandos no cambian.
- La generación visual no necesita RAG ni un proveedor disponible. La IA sigue
  atendiendo el resto del chat. No se implementó generación libre de topologías
  nuevas desde descripciones, ni creación de .pkt o control de Packet Tracer.
- La imagen se reconstruye desde datos estructurados validados, guardados junto
  al mensaje. Se recupera al reabrir y se incluye en el informe HTML. No se
  almacena SVG arbitrario del cliente, ni se cambia el esquema de SQLite.
- Pasaron 43 pruebas automatizadas con dependencias de IA simuladas, incluidas
  seis de topología: contrato del chat, datos faltantes/conflictivos, escape de
  texto, recuperación e informe. Se comprobó sintaxis JavaScript y formato.
- En navegador se cargó la demo correcta y se generó la imagen real desde el
  botón de Nexo, con Fa0/1–Fa0/4 y VLAN 10/20, y se comprobó la vista ampliada.
  El enlace de descarga SVG se añadió; la herramienta del navegador agotó la
  espera del evento de descarga, por lo que esa descarga no se da por verificada
  de extremo a extremo. Sin pruebas de red ni nueva práctica guardada en la base
  real durante esta revisión. La API local quedó reiniciada con el índice real.

## Respuestas breves de Nexo (8 de noviembre de 2026)

- El usuario compartió una conversación con respuestas largas y pidió concisión
  y precisión. Se ajustaron las instrucciones para responder primero la pregunta,
  con 2–4 frases y un máximo orientativo de 90 palabras para dudas básicas.
- Se pide omitir presentaciones repetidas, cierres automáticos, límites y
  contactos innecesarios. Las definiciones no deben añadir configuraciones no
  solicitadas. Se mantiene el detalle necesario para comandos completos, riesgos
  pertinentes o explicaciones amplias pedidas por el usuario.
- También se redujo la respuesta fija que acompaña a la topología, sin repetir
  sus puertos y grupos en un párrafo. Se conserva el aviso de propuesta no verificada.
- Dos consultas reales al proveedor con el prompt nuevo y un historial previo
  produjeron respuestas de 47 y 39 palabras. Esto comprueba ejemplos puntuales;
  las instrucciones no constituyen un límite rígido garantizado por código ni
  una evaluación exhaustiva de exactitud. No se recortan respuestas a mitad.
- Pasaron las seis pruebas de topología y la revisión de formato. No se amplió
  el alcance de las herramientas ni se hicieron pruebas de redes en laboratorio.
- Tras reiniciar la API exclusiva del proyecto, /health confirmó el índice real
  listo. Una petición real a /chat («¿Qué es una VLAN?») devolvió una respuesta
  de 44 palabras. La preferencia se aplica a las nuevas respuestas.

## Retirada de versión de IOS del formulario (8 de noviembre de 2026)

- El usuario pidió eliminar el campo Versión de IOS. Se retiró del formulario,
  del resumen visible y del informe HTML. El modelo queda en una sola fila.
- La versión deja de bloquear la generación y el diagnóstico del escenario
  básico Cisco VLAN/acceso. Modelo, VLAN y puertos siguen siendo necesarios.
  El chat no debe exigir IOS para esta práctica de Packet Tracer; puede pedirlo
  en otros escenarios si una incompatibilidad o sintaxis lo requiere.
- Se conserva el campo opcional de la API y la metadata de casos antiguos para
  mantener compatibilidad, sin migrar ni borrar datos. Las prácticas nuevas y
  los ejemplos no necesitan rellenarlo. La demo incompleta ahora omite el modelo.
- Se actualizaron instrucciones de uso y pruebas: 44 pruebas automatizadas y los
  seis escenarios de demo pasaron con proveedores simulados y almacenamiento de
  pruebas temporal exclusivo. Se comprobó sintaxis JavaScript y formato del diff.
- En navegador se verificó la ausencia del campo y la apertura de una práctica
  con requisitos completos usando modelo, VLAN y puertos, sin versión de IOS.
- Tras el reinicio de la API del proyecto, se comprobó en el navegador la
  generación de comandos para VLAN 10/20 y Fa0/1–Fa0/4 sin versión de IOS.
  El índice real quedó listo; no se ejecutaron esos comandos en Packet Tracer.

## Configuración en Nexo y preguntas relacionadas (8 de noviembre de 2026)

- El usuario pidió retirar Generar configuración del panel y colocar la acción
  dentro del chat. Se implementó un bloque permanente Configuración inicial con
  Preparar comandos en Nexo. Los comandos se entregan en un bloque con Copiar.
- La petición usa el generador existente por código y sus validaciones, sin
  depender del proveedor ni de RAG. Los requisitos siguen en el formulario; el
  panel conserva el resumen, estado y plan de comprobación. Los comandos y sus
  resultados solicitados se conservan al guardar/reabrir y en el informe.
- El usuario aclaró que las sugerencias deben relacionarse con la pregunta
  respondida. Se añadió una continuación opcional en un botón separado: el
  proveedor propone la pregunta según la consulta; no se agrega siempre una
  invitación genérica a configurar ni se afirma que la duda quedó resuelta.
- La topología puede ofrecer preparar los comandos de ese mismo caso; después
  de los comandos se ofrece comprobar los puertos y las VLAN. Las sugerencias
  se envían solo al pulsarlas, se ocultan al comenzar otra pregunta y se guardan
  con el mensaje. No hay consultas ni acciones automáticas por mostrarlas.
- Pasaron 48 pruebas automatizadas, incluyendo generación desde el chat sin
  proveedor, datos faltantes/conflictivos y separación de respuesta/sugerencia.
  En dos consultas reales, VLAN sugirió asignar un puerto y /24 sugirió asignar
  una IP en esa red. La pertinencia generativa es puntual, no está garantizada
  por esas pruebas. Sintaxis JavaScript y formato comprobados.
- Verificado en navegador: ya no hay botón Generar configuración en el panel;
  Preparar comandos en Nexo devuelve el bloque completo con Copiar y ofrece
  «¿Cómo compruebo que los puertos pertenecen a la VLAN correcta?». La API
  quedó reiniciada con el índice real y almacenamiento exclusivo del proyecto.

## Inicio para otros equipos y publicación (8 de noviembre de 2026)

- Un amigo intentó abrir la raíz de la API en 127.0.0.1:8000 y recibió
  {"detail":"Not Found"}. También solicitó /frontend/presentacion.html desde
  un servidor que ya servía frontend. Los registros mostraban inicio completo
  de la API; esas rutas no corresponden a la página de NetAssist.
- Se actualizó README.md con instalación en Windows, ruta de Descargas adaptable
  al nombre real de la carpeta, entorno .venv sin activación, configuración local
  y dos terminales desde la raíz del repositorio. Incluye macOS/Linux y cómo
  volver a arrancar sin reinstalar dependencias.
- La página se abre en http://localhost:5500/; el estado de la API se consulta
  en http://127.0.0.1:8000/health. No se añade /frontend/presentacion.html.
  Para usar 5501 deben coincidir el puerto del servidor web y FRONTEND_ORIGIN.
  El frontend mantiene la API en 8000. No detener otros servicios para liberar
  puertos: usar una alternativa cuando corresponda.
- La guía aclara que cada equipo configura sus claves en .env; GitHub Secrets
  no las instala en los equipos de los compañeros. Los fallos de telemetría
  ChromaDB/PostHog observados no impidieron el inicio según los registros;
  no se corrigieron las dependencias de telemetría en este trabajo.
- Se comprobaron los enlaces locales del README, el archivo de entrada y la
  coincidencia con .env.example. No se ha confirmado que el amigo completara
  el arranque en su equipo. No se cambiaron servicios ni bases para esta guía.
- Publicado en origin/elliot a petición del usuario: 85c6726 (topologías,
  respuestas concisas y retirada de IOS), ebfd02f (configuración y sugerencias
  en el chat) y 602143f (guía de inicio y rutas). Tras publicar 602143f, Git
  indicó árbol limpio y coincidencia entre HEAD y origin/elliot.

## Capturas en Nexo y presentación (8 de noviembre de 2026)

- El usuario pidió admitir capturas de pantalla en el chatbot y retirar la
  etiqueta «Copiar y pegar» del diagrama de arquitectura de la presentación.
- Implementado: adjuntar con + o pegar con Ctrl+V, vista previa, retirada antes
  de enviar, consulta solo con imagen o con texto y recuperación del borrador
  ante fallos. Una imagen estática PNG/JPG/WebP por mensaje, 3 MB como máximo,
  hasta 3 imágenes por conversación y 16 megapíxeles. La API comprueba contenido,
  formato, tamaño y límites del cuerpo antes de aceptar los adjuntos.
- Gemini recibe imagen y texto; Groq usa GROQ_VISION_MODEL separado del modelo
  de texto, por defecto qwen/qwen3.8-27b, anunciado por la cuenta consultada.
  Ambos proveedores leyeron correctamente la captura de prueba en llamadas
  reales. Hubo un fallo HTTP inicial de Groq y un intento posterior correcto;
  no se da por garantizada su disponibilidad permanente.
- Las imágenes enviadas se guardan en el documento JSON del caso, se recuperan
  en la conversación y se incluyen en informes HTML y JSON. No se modificó el
  esquema de SQLite ni el almacenamiento de producción. La interpretación visual
  es orientativa, no crea evidencia textual verificada ni prueba conectividad.
- Pasaron 57 pruebas automatizadas con embeddings simulados, sintaxis JavaScript
  y revisión de formato. En navegador se comprobaron adjuntar, pegar, quitar,
  respuesta visual real, guardado/reapertura, límites de tipo y tamaño, vista
  móvil y conservación del adjunto al simular una caída de visión.
- La prueba de navegador usó una API aislada en 8001, RAG simulado e IA real.
  Su SQLite se verificó dentro de .cache/image-ui-test/.data/netassist, separado
  de la base de prácticas real. No hubo pruebas de laboratorio en Packet Tracer.
- La revisión automática bloqueó el reinicio de la API existente en 8000 sin
  dar un motivo específico. Quedó pendiente que el usuario reinicie su terminal
  de API y recargue el frontend. La página detecta servicios anteriores para
  impedir que una captura se envíe a un backend que solo entiende texto.
- Se entregan revisiones PPTX y PDF en output/presentacion con sufijo
  _actualizado, conservando las siete diapositivas y quitando la etiqueta
  señalada. La retirada del texto del PPT no crea integración con Packet Tracer.
