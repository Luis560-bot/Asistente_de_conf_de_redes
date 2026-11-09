# Resultados medidos de la demostración

Ejecución UTC: 2026-11-09T03:52:28.315120+00:00

API en proceso; capturas, RAG y proveedores simulados; SQLite temporal real

| Escenario | Resultado | Tiempo local (ms) | Observación |
| --- | --- | ---: | --- |
| VLAN y acceso correctos | Correcto | 30.12 | generación=proposed; contraste=compared; hallazgos=18 |
| Modo trunk y VLAN equivocada | Correcto | 5.72 | generación=proposed; contraste=discrepancies; hallazgos=18 |
| Falta el modelo del switch | Correcto | 6.31 | generación=incomplete; contraste=insufficient; hallazgos=0 |
| Puerto asignado a dos grupos | Correcto | 5.19 | generación=invalid; contraste=insufficient; hallazgos=0 |
| Salida incompleta o paginada | Correcto | 4.25 | generación=proposed; contraste=insufficient; hallazgos=0 |
| Corrección con captura posterior | Correcto | 4.94 | generación=proposed; contraste=compared; hallazgos=18 |
| Guardar, reabrir y exportar | Correcto | 2009.93 | SQLite temporal: recuperación, HTML, JSON, revisión 2 y conflicto 409 correctos |
| Proveedor primario simulado | Correcto | 10.04 | Resultado esperado; llamadas simuladas, no mide latencia ni disponibilidad del proveedor real |
| Timeout y respaldo simulados | Correcto | 4.34 | Resultado esperado; llamadas simuladas, no mide latencia ni disponibilidad del proveedor real |
| Caída de ambos proveedores simulada | Correcto | 3.72 | Resultado esperado; llamadas simuladas, no mide latencia ni disponibilidad del proveedor real |

Pruebas unitarias: 59; fallos: 0; errores: 0; omitidas: 0.

Los tiempos son de una ejecución local en proceso y no incluyen arranque, carga del modelo, navegador ni red. Los proveedores y sus errores están simulados; no son mediciones de disponibilidad real. Capturas sintéticas: no se ejecutó una práctica en Packet Tracer. La validación real de laboratorio sigue pendiente.
