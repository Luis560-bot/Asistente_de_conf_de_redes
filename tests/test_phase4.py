"""Capturas sintéticas: prueban el contraste, no un laboratorio real."""
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from backend import main
from backend.diagnostics import diagnose


BRIEF = """VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/1
10   ADMINISTRACION                   active    Fa0/1,
                                                Fa0/2
20   LABORATORIO                      active    Fa0/3
"""
PORT = """Name: Fa0/1
Switchport: Enabled
Administrative Mode: static access
Operational Mode: down
Access Mode VLAN: 10 (ADMINISTRACION)
"""


def case(records=()):
    return main.ContextoPractica(title="Prueba", model="2960", version="15.0", groups=[
        dict(name="Administración", vlan="10", ports="Fa0/1, Fa0/2"),
        dict(name="Laboratorio", vlan="20", ports="Fa0/3")],
        evidence_records=[dict(command=c, output=o) for c, o in records])


class Diagnostics(unittest.TestCase):
    def test_brief_wrap_and_citations(self):
        result = diagnose(case([("show vlan brief", BRIEF)]))
        self.assertEqual(result["status"], "compared")
        self.assertEqual(len(result["findings"]), 5)
        for finding in result["findings"]:
            self.assertEqual(finding["record"], 1)
            self.assertIn(finding["evidence"], BRIEF)
            self.assertTrue(finding["next_step"])
        self.assertNotIn("show vlan brief", [s["command"] for s in result["next_steps"]])
        self.assertFalse(result["lab_verified"])

    def test_wrong_vlan_and_mode(self):
        output = PORT.replace("static access", "trunk").replace("10 (ADMINISTRACION)", "20 (LABORATORIO)")
        result = diagnose(case([("show interfaces FastEthernet0/1 switchport", output)]))
        self.assertEqual(result["status"], "discrepancies")
        self.assertEqual(sum(f["status"] == "mismatch" for f in result["findings"]), 2)

    def test_missing_rows_are_unknown_not_failure(self):
        result = diagnose(case([("show vlan brief", BRIEF.split("10   ")[0])]))
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["status"], "insufficient")

    def test_truncated_error_and_wrong_interface(self):
        for output in [PORT + "--More--", PORT + "% Invalid input", PORT.replace("Name: Fa0/1", "Name: Fa0/2"), PORT.replace("Switchport: Enabled", "")]:
            with self.subTest(output=output):
                result = diagnose(case([("show interfaces Fa0/1 switchport", output)]))
                self.assertEqual(result["findings"], [])
                self.assertFalse(result["steps"][0]["recognized"])

    def test_latest_capture_wins_including_invalid(self):
        result = diagnose(case([("show interfaces Fa0/1 switchport", PORT),
                                ("SHOW INTERFACES FastEthernet0/1 SWITCHPORT", "incompleta")]))
        self.assertEqual(result["findings"], [])
        self.assertIn("sustituida", result["steps"][0]["note"])
        self.assertIn("show interfaces FastEthernet0/1 switchport", [s["command"] for s in result["next_steps"]])

    def test_latest_correction_removes_old_mismatch(self):
        result = diagnose(case([("show interfaces Fa0/1 switchport", PORT.replace("static access", "trunk")),
                                ("show interfaces Fa0/1 switchport", PORT)]))
        self.assertEqual(result["status"], "compared")
        self.assertTrue(all(f["record"] == 2 for f in result["findings"]))

    def test_unknown_command_and_incomplete_requirements(self):
        self.assertEqual(diagnose(case([("show running-config", PORT)]))["findings"], [])
        self.assertEqual(diagnose(case([("show interfaces Fa0/1,Gi0/2 switchport", PORT)]))["findings"], [])
        c = case(); c.version = ""
        self.assertTrue(diagnose(c)["requirements"])

    def test_api_without_rag_and_payload_limits(self):
        service = MagicMock(); service.initialize.side_effect = OSError("sin índice")
        with patch.object(main, "rag_service", service), patch.object(main, "llamar_llm", AsyncMock()) as model:
            with TestClient(main.app) as client:
                data = case([("show vlan brief", BRIEF)]).model_dump()
                self.assertEqual(client.post("/diagnosticar", json=data).json()["status"], "compared")
                data["evidence_records"] *= 13
                self.assertEqual(client.post("/diagnosticar", json=data).status_code, 422)
                model.assert_not_awaited()
                service.buscar.assert_not_called()

    def test_chat_receives_diagnosis_and_recorded_steps(self):
        service = MagicMock(); service.initialize.return_value = {}; service.buscar.return_value = []
        model = AsyncMock(return_value="Respuesta")
        with patch.object(main, "rag_service", service), patch.object(main, "llamar_llm", model):
            with TestClient(main.app) as client:
                response = client.post("/chat", json={"messages": [{"role": "user", "content": "¿Qué sigue?"}], "context": case([("show vlan brief", BRIEF)]).model_dump()})
                self.assertEqual(response.status_code, 200)
                content = model.await_args.args[0][-1]["content"]
                self.assertIn('"status": "compared"', content)
                self.assertIn("no repetir pasos reconocidos", content)
