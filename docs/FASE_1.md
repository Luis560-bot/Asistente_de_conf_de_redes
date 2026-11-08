# Fase 1: base para la práctica Cisco

## Escenario delimitado

Un switch Cisco de capa 2 en Packet Tracer y cuatro PC: dos en Administración
(VLAN 10, puertos Fa0/1 y Fa0/2) y dos en Laboratorio (VLAN 20, Fa0/3 y Fa0/4).
Estos valores son un caso de referencia, no datos inferidos del usuario.
Registrar modelo y versión con `show version`, nombres reales de interfaces,
conexiones y direccionamiento antes de preparar cambios.

Direcciones de ejemplo propuestas para la práctica: Administración 192.0.2.10/24
y 192.0.2.11/24; Laboratorio 198.51.100.10/24 y 198.51.100.11/24.
No se necesita gateway para probar pares de la misma subred en este escenario.
No se incluyen trunks, enrutamiento entre VLAN, NAT, OSPF ni automatización de Packet Tracer.

## Evidencia que se recogerá en fase 3

- Modelo, IOS, diagrama y asignación de puertos confirmados.
- `show vlan brief`, estado físico y `show interfaces <puerto> switchport`.
- Ping entre los dos PC de cada grupo, con origen, destino y resultado.
- Intento entre grupos, anotando que su fallo por sí solo no prueba aislamiento:
  también puede deberse al direccionamiento, enlaces o ausencia de enrutamiento.

Nada de lo anterior ha sido ejecutado en laboratorio durante esta fase.

## Respaldo y reindexación

Cada proveedor valida su configuración durante su propio intento. Un fallo,
respuesta vacía, timeout o configuración incompleta permite probar el siguiente.
La última alternativa es el mensaje de contacto. Las pruebas usan respuestas
simuladas; no certifican cuotas, claves o disponibilidad de los servicios reales.

La reindexación publica una colección nueva solo después de cargarla completa y
escribir un manifiesto mediante reemplazo atómico. Si falla conserva la colección
activa; un reinicio puede recuperar la última generación publicada. Las generaciones
anteriores se conservan; no hay limpieza automática. Ejecutar un único proceso de
API por almacenamiento (sin múltiples workers). Cada arranque reconstruye el corpus.
La primera migración desde el índice original necesita una reconstrucción correcta
para crear el manifiesto; no interpreta silenciosamente índices heredados.

El destino permitido es exclusivamente `backend/chroma_db` de este repositorio;
se rechazan redirecciones por enlaces o junctions. Las pruebas de fallos no deben
usar bases externas. La documentación Markdown de planificación no se indexa.

## Fuente técnica

La síntesis indexable está en `cisco_vlan_acceso.txt` y enlaza la guía oficial
Cisco Catalyst 2960/2960-S, IOS 15.2(1)E. El manual básico anterior permanece
como material introductorio y no se considera prueba de laboratorio.
