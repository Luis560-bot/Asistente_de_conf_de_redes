# Comprobación real de proveedores

Ejecución UTC: 2026-11-08T21:22:43.494946+00:00

Una solicitud directa por proveedor, ejecutadas en paralelo. Texto de prueba sintético; no se enviaron casos guardados. Límite total de 20 s por llamada; se conserva el timeout HTTP configurado en el cliente.

| Proveedor | Modelo configurado | Resultado | Tiempo (ms) | Detalle |
| --- | --- | --- | ---: | --- |
| Gemini | gemini-3.1-flash-lite | Respondió | 2407.49 | Respuesta no vacía recibida; contenido omitido |
| Groq | openai/gpt-oss-20b | Respondió | 1224.46 | Respuesta no vacía recibida; contenido omitido |

Es una observación puntual de red, no garantiza disponibilidad futura. Estas llamadas no evalúan calidad técnica ni usan recuperación RAG. El respaldo y la caída de ambos se prueban por separado con errores simulados en RESULTADOS_DEMO.md. No se han realizado pruebas de configuración en Packet Tracer.
