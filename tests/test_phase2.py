"""Contrato del chat contextual; sin proveedores ni almacenamiento real."""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from backend import main


class ContextualChat(unittest.TestCase):
    def test_generator_works_without_rag_or_provider(self):
        service = MagicMock()
        service.initialize.side_effect = OSError("sin índice")
        with patch.object(main, "rag_service", service), patch.object(main, "llamar_llm", AsyncMock()) as model:
            with TestClient(main.app) as client:
                context = self.context(); context.pop("version")
                response = client.post("/generar", json=context)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["status"], "proposed")
                self.assertFalse(response.json()["lab_verified"])
                model.assert_not_awaited()
                service.buscar.assert_not_called()

    def context(self):
        return {"title": "Separar grupos", "model": "2960", "version": "15.0",
                "groups": [{"name": "Administración", "vlan": "10", "ports": "Fa0/1"},
                           {"name": "Laboratorio", "vlan": "20", "ports": "Fa0/2"}],
                "review_command": "show vlan brief", "evidence": "10 ADMIN active Fa0/1"}

    def test_current_case_and_evidence_reach_model_and_retrieval(self):
        service = MagicMock()
        service.initialize.return_value = {"archivos": 3, "fragmentos": 3}
        service.buscar.return_value = []
        model = AsyncMock(return_value="Respuesta contextual")
        with patch.object(main, "rag_service", service), patch.object(main, "llamar_llm", model):
            with TestClient(main.app) as client:
                response = client.post("/chat", json={"messages": [{"role": "user", "content": "¿Por qué?"}], "context": self.context()})
                self.assertEqual(response.status_code, 200)
                messages, _ = model.await_args.args
                self.assertEqual(messages[-1]["role"], "user")
                for value in ["Separar grupos", "show vlan brief", "10 ADMIN active Fa0/1", "¿Por qué?"]:
                    self.assertIn(value, messages[-1]["content"])
                self.assertIn("no ha sido contrastada", messages[-1]["content"])
                self.assertIn("Cisco IOS VLAN", service.buscar.call_args.args[0])

    def test_oversized_evidence_is_rejected(self):
        service = MagicMock()
        service.initialize.return_value = {"archivos": 3, "fragmentos": 3}
        context = self.context()
        context["evidence"] = "x" * 8001
        with patch.object(main, "rag_service", service), patch.object(main, "llamar_llm", AsyncMock()) as model:
            with TestClient(main.app) as client:
                response = client.post("/chat", json={"messages": [{"role": "user", "content": "Hola"}], "context": context})
                self.assertEqual(response.status_code, 422)
                model.assert_not_awaited()
