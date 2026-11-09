# Fase 3: generador de VLAN y acceso

Implementado: `POST /generar`, generador reproducible de referencia para un
switch Cisco IOS y dos grupos; bloque Configuración inicial → Preparar comandos dentro de Nexo.
No necesita proveedores de IA ni RAG. La IA del chat explica la propuesta y
acompaña el caso; no decide las reglas exactas ni ejecuta la configuración.

Solicita modelo, VLAN y puertos faltantes. La versión de IOS no es obligatoria. Bloquea VLAN fuera de
2–1001 (límite deliberado del escenario), VLAN iguales, sintaxis de puertos
inválida y puertos duplicados, incluso entre abreviaturas y nombres completos.
Admite listas separadas por comas de Fa/FastEthernet y Gi/GigabitEthernet;
no admite rangos. El modelo, el inventario físico de interfaces, VTP y la
configuración previa requieren revisión manual. No interpreta automáticamente
el texto libre de conexiones ni extiende la propuesta a varios switches.

Los resultados contienen grupos normalizados, comandos, explicación, reglas
comprobadas, límites, fuente y comandos de comprobación con resultados esperados.
El chat recalcula esta misma referencia desde los requisitos del caso.
Los nombres CLI son ADMINISTRACION y LABORATORIO. El guardado persistente se
presenta separado para realizarlo después de revisar los resultados.

Fuente de la plantilla: [Cisco Catalyst 2960, IOS 15.0(2)SE: Configuring VLANs](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst2960/software/release/15-0_2_se/configuration/guide/scg2960/swvlan.html).
La fuente describe IOS real; su uso no demuestra compatibilidad con el simulador.

## Práctica de aceptación pendiente

1. En Packet Tracer crea un laboratorio nuevo con un 2960 y cuatro PC.
   Conecta PC-A1 y PC-A2 a Fa0/1 y Fa0/2; PC-L1 y PC-L2 a Fa0/3 y Fa0/4.
2. Obtén `show version`. Registra el modelo en el formulario,
   VLAN 10 y 20 y los puertos anteriores. Pide los comandos a Nexo y revísalos.
3. En el switch confirma que los puertos existen y están disponibles. Aplica la
   propuesta en la CLI. Registra cualquier comando rechazado y su mensaje.
4. Ejecuta `show vlan brief` y `show interfaces Fa0/1 switchport` (repite para
   los cuatro puertos). Pega las salidas en Comprobaciones con el comando;
   incorpóralas al caso. Este registro es manual y todavía no se contrasta por código.
5. Configura A1 192.168.10.11/24 y A2 192.168.10.12/24; L1
   192.168.20.11/24 y L2 192.168.20.12/24; sin gateway ni router.
6. Desde A1 prueba ping a A2 y desde L1 a L2: se espera respuesta después
   de la convergencia y resolución ARP. Registra origen, destino y resultado.
   Desde A1 a L1 se espera ausencia de conectividad sin enrutamiento. Ese fallo
   aislado no prueba que la asignación VLAN sea correcta: contrástalo con las salidas.
7. Tras revisar, ejecuta `copy running-config startup-config` y guarda el `.pkt`.

Todavía no se ha ejecutado esta práctica ni se dispone de evidencia real de red.
La fase 3 no se considera cerrada hasta completar esa aceptación. El diagnóstico
automático y la persistencia de casos continúan en sus fases posteriores.
