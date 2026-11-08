# Resultados medidos de la demostración

Ejecución UTC: 2026-11-08T21:24:07.663608+00:00

API en proceso; capturas, RAG y proveedores simulados; SQLite temporal real

| Escenario | Resultado | Tiempo local (ms) | Observación |
| --- | --- | ---: | --- |
| VLAN y acceso correctos | Correcto | 11.19 | generación=proposed; contraste=compared; hallazgos=18 |
| Modo trunk y VLAN equivocada | Correcto | 5.59 | generación=proposed; contraste=discrepancies; hallazgos=18 |
| Falta la versión de IOS | Correcto | 5.1 | generación=incomplete; contraste=insufficient; hallazgos=0 |
| Puerto asignado a dos grupos | Correcto | 5.91 | generación=invalid; contraste=insufficient; hallazgos=0 |
| Salida incompleta o paginada | Correcto | 4.29 | generación=proposed; contraste=insufficient; hallazgos=0 |
| Corrección con captura posterior | Correcto | 4.96 | generación=proposed; contraste=compared; hallazgos=18 |
| Guardar, reabrir y exportar | Correcto | 295.85 | SQLite temporal: recuperación, HTML, JSON, revisión 2 y conflicto 409 correctos |
| Proveedor primario simulado | Correcto | 6.36 | Resultado esperado; llamadas simuladas, no mide latencia ni disponibilidad del proveedor real |
| Timeout y respaldo simulados | Correcto | 6.59 | Resultado esperado; llamadas simuladas, no mide latencia ni disponibilidad del proveedor real |
| Caída de ambos proveedores simulada | Correcto | 5.52 | Resultado esperado; llamadas simuladas, no mide latencia ni disponibilidad del proveedor real |

Pruebas unitarias: 35; fallos: 0; errores: 0; omitidas: 0.

Los tiempos son de una ejecución local en proceso y no incluyen arranque, carga del modelo, navegador ni red. Los proveedores y sus errores están simulados; no son mediciones de disponibilidad real. Capturas sintéticas: no se ejecutó una práctica en Packet Tracer. La validación real de laboratorio sigue pendiente.
