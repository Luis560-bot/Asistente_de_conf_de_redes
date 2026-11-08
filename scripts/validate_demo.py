"""Demostración reproducible sin red, credenciales ni acceso a bases existentes."""
import argparse
import json
import logging
import sys
import tempfile
import time
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# El arranque y las búsquedas RAG se simulan explícitamente en esta ejecución.
# Evita cargar PyTorch o descargar un modelo para evaluar reglas deterministas.
stub = types.ModuleType("sentence_transformers")
stub.SentenceTransformer = object
sys.modules["sentence_transformers"] = stub

import httpx
from fastapi.testclient import TestClient
from backend import main, llm
from backend.cases import CaseStore


def run(with_tests=False):
    logging.disable(logging.CRITICAL)
    cache = ROOT / ".cache"
    if cache.resolve() != cache:
        raise RuntimeError("La carpeta temporal debe pertenecer exclusivamente al proyecto.")
    cache.mkdir(exist_ok=True)
    fixture = json.loads((ROOT / "frontend/demo-cases.json").read_text(encoding="utf-8"))
    report = {"executed_at_utc": datetime.now(timezone.utc).isoformat(),
              "mode": "API en proceso; capturas, RAG y proveedores simulados; SQLite temporal real",
              "lab_verified": False, "results": []}

    def measure(name, operation):
        start = time.perf_counter()
        detail = operation()
        report["results"].append({"name": name, "passed": True, "milliseconds": round((time.perf_counter() - start) * 1000, 2), "detail": detail})

    with tempfile.TemporaryDirectory(prefix="demo-", dir=cache) as directory:
        service = MagicMock()
        service.initialize.return_value = {"archivos": 0, "fragmentos": 0}
        service.buscar.return_value = []
        with patch.object(main, "rag_service", service), patch.object(main, "case_store", CaseStore(Path(directory))), TestClient(main.app) as client:
            for scenario in fixture["scenarios"]:
                def operation(scenario=scenario):
                    gen_response = client.post("/generar", json=scenario["case"])
                    diag_response = client.post("/diagnosticar", json=scenario["case"])
                    assert gen_response.status_code == diag_response.status_code == 200
                    gen, diag = gen_response.json(), diag_response.json()
                    assert gen["status"] == scenario["expected"]["generation"], scenario["id"]
                    assert diag["status"] == scenario["expected"]["diagnosis"], scenario["id"]
                    assert not gen["lab_verified"] and not diag["lab_verified"]
                    if scenario["id"] in ["correct", "corrected"]:
                        assert len(diag["findings"]) == 18
                        assert all(not step["command"] for step in diag["next_steps"])
                    if scenario["id"] == "wrong":
                        assert sum(f["status"] == "mismatch" for f in diag["findings"]) == 2
                    if gen["status"] != "proposed":
                        assert not gen["commands"]
                    if scenario["id"] == "partial":
                        assert not diag["findings"]
                        assert any(s["command"] == "show vlan brief" for s in diag["next_steps"])
                    return f"generación={gen['status']}; contraste={diag['status']}; hallazgos={len(diag['findings'])}"
                measure(scenario["label"], operation)

            def persistence():
                body = {"case": fixture["scenarios"][0]["case"], "messages": [{"role": "user", "content": "¿Por qué modo access?"}], "proposal_requested": True, "diagnosis_requested": True}
                response = client.post("/casos", json=body)
                assert response.status_code == 201
                saved = response.json(); key = saved["id"]
                assert CaseStore(Path(directory)).get(key) == saved
                assert client.get(f"/casos/{key}").json() == saved
                assert client.get(f"/casos/{key}/informe?formato=json").json() == saved
                html = client.get(f"/casos/{key}/informe")
                assert html.status_code == 200 and "Fa0/1" in html.text
                body["revision"] = 1
                assert client.put(f"/casos/{key}", json=body).json()["revision"] == 2
                assert client.put(f"/casos/{key}", json=body).status_code == 409
                return "SQLite temporal: recuperación, HTML, JSON, revisión 2 y conflicto 409 correctos"
            measure("Guardar, reabrir y exportar", persistence)

            for mode in ["primary", "backup", "unavailable"]:
                def provider(mode=mode):
                    primary = AsyncMock(return_value="Primario simulado")
                    backup = AsyncMock(return_value="Respaldo simulado")
                    if mode != "primary":
                        primary.side_effect = httpx.ReadTimeout("timeout simulado")
                    if mode == "unavailable":
                        backup.side_effect = RuntimeError("caída simulada")
                    with patch.object(llm, "_llamar_gemini", primary), patch.object(llm, "_llamar_groq", backup):
                        response = client.post("/chat", json={"messages": [{"role": "user", "content": "Explica VLAN"}], "context": fixture["scenarios"][0]["case"]})
                    expected = {"primary": "Primario simulado", "backup": "Respaldo simulado", "unavailable": llm.MENSAJE_FALLBACK}[mode]
                    assert response.status_code == 200 and response.json()["reply"] == expected
                    assert primary.await_count == 1 and backup.await_count == (0 if mode == "primary" else 1)
                    return "Resultado esperado; llamadas simuladas, no mide latencia ni disponibilidad del proveedor real"
                measure({"primary": "Proveedor primario simulado", "backup": "Timeout y respaldo simulados", "unavailable": "Caída de ambos proveedores simulada"}[mode], provider)
    if with_tests:
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        report["unit_tests"] = {"run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}
        if not result.wasSuccessful():
            raise RuntimeError("Fallaron pruebas unitarias; no se publica un informe correcto.")
    output = cache / "demo-results.json"
    if output.resolve() != output:
        raise RuntimeError("Destino de resultados redirigido.")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Resultados medidos de la demostración", "", f"Ejecución UTC: {report['executed_at_utc']}", "", report["mode"], "", "| Escenario | Resultado | Tiempo local (ms) | Observación |", "| --- | --- | ---: | --- |"]
    lines += [f"| {r['name']} | Correcto | {r['milliseconds']} | {r['detail']} |" for r in report["results"]]
    if with_tests:
        lines += ["", f"Pruebas unitarias: {result.testsRun}; fallos: {len(result.failures)}; errores: {len(result.errors)}; omitidas: {len(result.skipped)}."]
    lines += ["", "Los tiempos son de una ejecución local en proceso y no incluyen arranque, carga del modelo, navegador ni red. Los proveedores y sus errores están simulados; no son mediciones de disponibilidad real. Capturas sintéticas: no se ejecutó una práctica en Packet Tracer. La validación real de laboratorio sigue pendiente.", ""]
    (ROOT / "docs/RESULTADOS_DEMO.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Demostración: {len(report['results'])}/{len(report['results'])} escenarios correctos. Informe: docs/RESULTADOS_DEMO.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-tests", action="store_true")
    run(parser.parse_args().with_tests)
