# Fase 4: diagnóstico de VLAN y puertos de acceso

La interfaz permite incorporar hasta doce capturas, cada una con su comando y
salida (máximo 8000 caracteres). Se conservan durante la pestaña y se pueden
retirar individualmente. Actualizar los requisitos reinicia las capturas y el
chat. Recargar también los borra; la persistencia corresponde a la fase 5.

«Analizar evidencia» llama a `POST /diagnosticar` con el mismo caso que
`/generar`, más `evidence_records: [{command, output}]`. La API funciona sin
proveedores ni índice RAG. El campo único anterior `evidence` se admite si no
hay registros. No se ejecutan comandos ni se modifica un equipo o base de datos.

## Contraste admitido

- `show vlan brief`: requiere cabecera VLAN/Name/Status/Ports y filas reconocibles.
  Compara el estado de las VLAN esperadas y los puertos presentes con sus VLAN.
  Admite continuación de puertos en líneas sangradas. No concluye que una VLAN
  o puerto ausente esté mal: la captura podría estar incompleta.
- `show interfaces <puerto> switchport`: requiere Name, Switchport,
  Administrative Mode y Access Mode VLAN sin duplicados y con el mismo puerto
  del comando. Compara Enabled, static access y el identificador VLAN esperado.
  Admite Fa/FastEthernet y Gi/GigabitEthernet. El modo operativo no se evalúa.

Cada hallazgo muestra campo, observado, esperado, coincidencia o discrepancia,
fragmento literal, número de captura y siguiente paso. Los datos del caso deben
superar las reglas de fase 3 antes del contraste.

Las capturas más recientes sustituyen las anteriores del mismo comando para el
contraste; el historial permanece visible. Una captura reciente inválida impide
reutilizar como actual una antigua correcta. Se proponen comandos pendientes,
sin repetir los reconocidos. Las discrepancias piden revisar el campo y aportar
una captura nueva después de corregirlo. El chat recibe registros y diagnóstico
calculado en el servidor, no resultados de contraste declarados por el cliente.

## Límites y evidencia de desarrollo

Salidas con errores CLI comunes, paginación, interfaz distinta, campos ambiguos o
formato no reconocido quedan sin contraste. Otros comandos, `show version`, ping,
direccionamiento, cableado y conectividad se conservan como evidencia manual,
sin interpretación automática en este incremento. Los comandos se escriben
completos, sin prompt (`Switch#`) ni abreviaturas de `show`.

Las capturas se suponen del único switch del caso y se ordenan por incorporación,
no por tiempo del dispositivo. No se autentican ni prueban el estado actual del
equipo. Resultados parciales pueden coincidir sin cubrir todos los requisitos.
`lab_verified` siempre permanece en false. No se afirma haber probado la red.

Las pruebas automatizadas usan capturas sintéticas para estados correctos,
discrepancias, continuaciones, errores, datos incompletos, reemplazo de capturas,
límites de la API, independencia del proveedor y contexto del chat. La aceptación
real en Packet Tracer de la fase 3 sigue pendiente; estas pruebas no la sustituyen.

Referencia de campos y comprobaciones: [Cisco Catalyst 2960, IOS 15.0(2)SE, VLAN](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst2960/software/release/15-0_2_se/configuration/guide/scg2960/swvlan.html).
