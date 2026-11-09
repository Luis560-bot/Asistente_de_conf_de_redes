"""Configuración en Nexo y continuaciones asociadas a cada respuesta."""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from backend import main
from backend.chat_actions import requests_configuration, split_suggestion


class ChatActions(unittest.TestCase):
    def context(self):
        return {"title": "Prueba", "model": "2960", "groups": [
            {"name": "Administración", "vlan": "10", "ports": "Fa0/1"},
            {"name": "Laboratorio", "vlan": "20", "ports": "Fa0/2"}]}

    def test_config_uses_same_generator_without_provider_or_rag(self):
        service = MagicMock(); service.initialize.side_effect = OSError("sin RAG")
        with patch.object(main, "rag_service", service), patch.object(main, "llamar_llm", AsyncMock()) as model:
            with TestClient(main.app) as client:
                case = self.context()
                reference = client.post("/generar", json=case).json()
                data = client.post("/chat", json={"context": case, "messages": [{"role": "user", "content": "Dame la configuración inicial de esta práctica."}]}).json()
                self.assertEqual(data["proposal"], reference)
                self.assertIn("```ios\n" + reference["commands"] + "\n```", data["reply"])
                self.assertIn("compruebo", data["suggestions"][0])
                model.assert_not_awaited()
                service.buscar.assert_not_called()

    def test_missing_context_or_invalid_data_never_returns_commands(self):
        service = MagicMock()
        with patch.object(main, "rag_service", service), TestClient(main.app) as client:
            case = self.context(); case["groups"][1]["ports"] = "FastEthernet0/1"
            for context in [None, case, {**self.context(), "model": ""}]:
                data = client.post("/chat", json={"context": context, "messages": [{"role": "user", "content": "Genera la configuración"}]}).json()
                self.assertNotIn("```", data["reply"])
                self.assertFalse(data["suggestions"])

    def test_suggestion_remains_separate_and_matches_supplied_topic(self):
        service = MagicMock(); service.buscar.return_value = []
        for answer, question in [("Una VLAN separa grupos.", "¿Cómo asigno un puerto a esa VLAN?"),
                                 ("Para 800 hosts se necesitan 10 bits de host.", "¿Cómo calculo la máscara de esa subred?")]:
            with patch.object(main, "rag_service", service), patch.object(main, "llamar_llm", AsyncMock(return_value=answer + "\n\nSiguiente pregunta: " + question)):
                with TestClient(main.app) as client:
                    data = client.post("/chat", json={"messages": [{"role": "user", "content": "Explícame este concepto"}]}).json()
                    self.assertEqual(data["reply"], answer)
                    self.assertEqual(data["suggestions"], [question])

    def test_optional_suggestions_and_conceptual_config_questions(self):
        self.assertEqual(split_suggestion("Respuesta sin continuación."), ("Respuesta sin continuación.", []))
        self.assertEqual(split_suggestion("Error\nSiguiente pregunta: " + "x"*181), ("Error", []))
        self.assertFalse(requests_configuration("¿Qué significa esta configuración?"))
        self.assertFalse(requests_configuration("Explícame los comandos"))
