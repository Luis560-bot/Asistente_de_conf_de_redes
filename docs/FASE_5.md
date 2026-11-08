# Fase 5: casos guardados e informes

La sección «Mis prácticas» permite guardar, listar las cien prácticas más
recientes, reabrirlas, actualizarlas e iniciar una práctica nueva. El guardado
es explícito: los cambios del formulario se aplican con Actualizar práctica,
y las salidas con Incorporar al caso. El botón Guardar práctica conserva ese
estado aplicado, hasta sesenta mensajes, las capturas y los resultados solicitados.
No existe guardado automático ni importación de archivos en esta fase.

Al reabrir se recuperan requisitos, evidencia, conversación y resultados de la
revisión guardada. Los resultados se calculan en el servidor al guardar según
los requisitos y capturas actuales; no se aceptan diagnósticos declarados por el
cliente. Si todavía no se había solicitado generación o diagnóstico, se conserva
ese estado. Los casos incompletos también se pueden guardar.

## Almacenamiento exclusivo

Destino fijo: `.data/netassist/cases.sqlite3`, dentro de la raíz efectiva del
proyecto. No se puede sustituir por una variable de entorno. Es independiente
de `backend/chroma_db` y no utiliza servicios de bases de datos externos.

Antes de abrir o crear la base se comprueba la resolución de los padres,
archivo y auxiliares SQLite: se rechazan redirecciones y archivos con varios
enlaces físicos. Se crea un archivo nuevo con apertura exclusiva. Para abrir
uno existente se exige `application_id=0x4E415343` y `user_version=1`; se rechaza
un archivo ajeno o una versión desconocida sin migrarlo ni reemplazarlo.
No hay migraciones de versiones anteriores ni borrado automático.
La verificación presupone un usuario local de confianza que no cambie rutas
mientras el servicio las abre. La carpeta de datos queda excluida de Git.

Cada escritura usa transacción y cada actualización exige el número de revisión
abierto. Un conflicto devuelve 409 y pide reabrir, en lugar de sobrescribir.
No se conserva un historial completo de revisiones: actualizar reemplaza la
versión anterior del caso. El historial de capturas dentro del caso sí se conserva.
No se implementaron cuentas ni permisos por usuario: el servicio es para uso
local, con API escuchando en 127.0.0.1. No publicarlo como servicio multiusuario.

## API y exportación

- `GET /casos`: identificadores, títulos, revisiones y fechas; máximo cien.
- `POST /casos`: `{case, messages, proposal_requested, diagnosis_requested}`.
- `GET /casos/{uuid}`: documento y metadatos guardados.
- `PUT /casos/{uuid}`: mismo cuerpo más `revision` obligatoria.
- `GET /casos/{uuid}/informe?formato=html|json`: descarga de la versión guardada.
  `revision` opcional permite rechazar una exportación si otra pestaña la actualizó.

El HTML es portátil, contiene requisitos, configuración, validaciones, límites,
fuentes, capturas, hallazgos, pasos y conversación; puede abrirse e imprimirse
desde un navegador. Todo texto aportado se escapa y no se incluyen scripts.
El JSON incluye el documento estructurado y metadatos. No se genera PDF en esta
fase. Exportar no incluye cambios que aún no se hayan guardado.

Los informes diferencian propuesta, evidencia aportada y contraste automático.
No marcan el laboratorio como verificado ni suponen resultados de ping.
La aceptación real de Packet Tracer de la fase 3 continúa pendiente.

## Comprobaciones

Las pruebas de persistencia usan bases reales en carpetas temporales bajo
`.cache` del proyecto, sin abrir otras bases del equipo. Cubren recuperación con
una instancia nueva, actualización, conflicto, UUID y revisión inválidos,
exportación, texto HTML escapado, base ajena sin modificar y rechazo de rutas
redirigidas. Si Windows impide crear un enlace simbólico, se simula la resolución
redirigida y se comprueba que no llega a crearse el archivo SQLite.
