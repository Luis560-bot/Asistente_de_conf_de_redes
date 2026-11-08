"""Prueba explícita con solicitudes reales a los proveedores configurados en .env."""
import asyncio
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import llm


async def check(name, function, key, model):
    if not key or not model:
        return name, model or "sin modelo", "Sin configurar", 0, "No se realizó llamada"
    start = time.perf_counter()
    try:
        reply = await asyncio.wait_for(function([{"role": "user", "content": "Responde únicamente: disponible"}], "Comprobación técnica breve de disponibilidad."), timeout=20)
        assert isinstance(reply, str) and reply.strip()
        status, detail = "Respondió", "Respuesta no vacía recibida; contenido omitido"
    except Exception as error:
        status = "No respondió correctamente"
        detail = type(error).__name__
        response = getattr(error, "response", None)
        if response is not None:
            detail += f" · HTTP {response.status_code}"
    return name, model, status, round((time.perf_counter() - start) * 1000, 2), detail


async def run():
    logging.disable(logging.CRITICAL)
    rows = await asyncio.gather(
        check("Gemini", llm._llamar_gemini, llm.GEMINI_API_KEY, llm.GEMINI_MODEL),
        check("Groq", llm._llamar_groq, llm.GROQ_API_KEY, llm.GROQ_MODEL))
    lines = ["# Comprobación real de proveedores", "", f"Ejecución UTC: {datetime.now(timezone.utc).isoformat()}", "", "Una solicitud directa por proveedor, ejecutadas en paralelo. Texto de prueba sintético; no se enviaron casos guardados. Límite total de 20 s por llamada; se conserva el timeout HTTP configurado en el cliente.", "", "| Proveedor | Modelo configurado | Resultado | Tiempo (ms) | Detalle |", "| --- | --- | --- | ---: | --- |"]
    lines += [f"| {name} | {model.replace('|', '/')} | {status} | {elapsed} | {detail} |" for name, model, status, elapsed, detail in rows]
    lines += ["", "Es una observación puntual de red, no garantiza disponibilidad futura. Estas llamadas no evalúan calidad técnica ni usan recuperación RAG. El respaldo y la caída de ambos se prueban por separado con errores simulados en RESULTADOS_DEMO.md. No se han realizado pruebas de configuración en Packet Tracer.", ""]
    (ROOT / "docs/PROVEEDORES_DEMO.md").write_text("\n".join(lines), encoding="utf-8")
    for name, _, status, elapsed, _ in rows:
        print(f"{name}: {status} ({elapsed} ms)")


if __name__ == "__main__":
    asyncio.run(run())
