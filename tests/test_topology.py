"""Diagrama del caso, contrato del chat y persistencia; sin proveedor real."""
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from backend import main
from backend.cases import CaseStore
from backend.topology import requests_topology


class TopologyChat(unittest.TestCase):
    def setUp(self):
        service = MagicMock()
        service.initialize.side_effect = OSError("RAG no disponible")
        self.enterContext(patch.object(main, "rag_service", service))
        self.model = self.enterContext(patch.object(main, "llamar_llm", AsyncMock()))
        self.client = self.enterContext(TestClient(main.app))

    def case(self):
        return {"title": "Caso <script>alert(1)</script>", "model": "2960", "version": "", "groups": [
            {"name": "Administración", "vlan": "10", "ports": "Fa0/1, Fa0/2"},
            {"name": "Laboratorio", "vlan": "20", "ports": "Fa0/3, Fa0/4"}]}

    def request(self, case):
        return self.client.post("/chat", json={"messages": [{"role": "user", "content":
            "Me puedes generar una imagen de la topología para Cisco Packet Tracer?"}], "context": case})

    def test_request_forms_and_conceptual_questions(self):
        for question in ["Genera la topologia", "Muéstrame un esquema de mi red", "Quiero ver mi topología", "Una imagen de mi Cisco Packet Tracer"]:
            self.assertTrue(requests_topology(question), question)
        for question in ["¿Qué es una topología?", "¿Puedes explicarme qué es una topología?", "Explícame el modo access", "Genera una imagen de un gato"]:
            self.assertFalse(requests_topology(question), question)

    def test_diagram_without_ios_version_rag_or_provider(self):
        response = self.request(self.case())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.model.assert_not_awaited()
        self.assertEqual(data["topology"]["groups"][0]["ports"], ["FastEthernet0/1", "FastEthernet0/2"])
        svg = ET.fromstring(data["topology_svg"])
        self.assertEqual(len(svg.findall("{http://www.w3.org/2000/svg}line")), 4)
        labels = " ".join(svg.itertext())
        for label in ["PC-1", "PC-4", "Fa0/1", "Fa0/4", "VLAN 10", "VLAN 20"]:
            self.assertIn(label, labels)
        self.assertNotIn("<script>", data["topology_svg"])
        self.assertIn("&lt;script&gt;", data["topology_svg"])
        self.assertIn("no es un archivo .pkt ni una red verificada", data["reply"])

    def test_missing_case_and_missing_ports_request_data(self):
        for case in [None, {**self.case(), "groups": [self.case()["groups"][0], {"name": "Laboratorio", "vlan": "20", "ports": ""}]}]:
            data = self.request(case).json()
            self.assertIsNone(data["topology"])
            self.assertIsNone(data["topology_svg"])
        self.model.assert_not_awaited()

    def test_conflicting_ports_do_not_produce_a_diagram(self):
        case = self.case()
        case["groups"][1]["ports"] = "FastEthernet0/1"
        data = self.request(case).json()
        self.assertIsNone(data["topology"])
        self.assertIn("ambos grupos", data["reply"])

    def test_image_survives_save_reopen_and_report(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / ".cache").resolve(), root / ".cache")
        (root / ".cache").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root / ".cache") as folder:
            with patch.object(main, "case_store", CaseStore(Path(folder))):
                data = self.request(self.case()).json()
                payload = {"case": self.case(), "messages": [{"role": "assistant", "content": data["reply"], "topology": data["topology"]}]}
                saved = self.client.post("/casos", json=payload)
                self.assertEqual(saved.status_code, 201)
                key = saved.json()["id"]
                reopened = self.client.get(f"/casos/{key}").json()
                topology = reopened["document"]["messages"][0]["topology"]
                image = self.client.post("/topologia/imagen", json=topology)
                self.assertEqual(image.status_code, 200)
                self.assertEqual(image.text, data["topology_svg"])
                report = self.client.get(f"/casos/{key}/informe").text
                self.assertIn("<svg", report)
                self.assertNotIn("<script>", report)

    def test_invalid_persisted_image_assignments_are_rejected(self):
        topology = self.request(self.case()).json()["topology"]
        topology["groups"][1]["ports"] = ["Fa0/1"]
        self.assertEqual(self.client.post("/topologia/imagen", json=topology).status_code, 422)
