"""Persistencia real únicamente en directorios temporales exclusivos del proyecto."""
import json
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend import main
from backend.cases import CaseStore, APP_ID

ROOT = Path(__file__).resolve().parents[1]


class Cases(unittest.TestCase):
    def setUp(self):
        (ROOT / ".cache").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / ".cache")
        self.addCleanup(self.temp.cleanup)
        self.store = CaseStore(Path(self.temp.name))

    def payload(self):
        return {"case": {"title": "Caso <script>alert(1)</script>", "model": "2960", "version": "15.0", "groups": [
            {"name": "Administración", "vlan": "10", "ports": "Fa0/1"},
            {"name": "Laboratorio", "vlan": "20", "ports": "Fa0/2"}],
            "evidence_records": [{"command": "show interfaces Fa0/1 switchport", "output": "Name: Fa0/1\nSwitchport: Enabled\nAdministrative Mode: static access\nAccess Mode VLAN: 10 (ADMIN)"}]},
            "messages": [{"role": "user", "content": "¿Qué sigue?"}], "proposal_requested": True, "diagnosis_requested": True}

    def client(self):
        service = MagicMock(); service.initialize.return_value = {}
        self.enterContext(patch.object(main, "rag_service", service))
        self.enterContext(patch.object(main, "case_store", self.store))
        return self.enterContext(TestClient(main.app))

    def test_roundtrip_restart_update_and_reports(self):
        client = self.client()
        response = client.post("/casos", json=self.payload())
        self.assertEqual(response.status_code, 201)
        saved = response.json(); key = saved["id"]
        self.assertEqual(saved["revision"], 1)
        self.assertEqual(saved["document"]["diagnosis"]["status"], "compared")
        self.assertFalse(saved["document"]["proposal"]["lab_verified"])
        restarted = CaseStore(Path(self.temp.name))
        self.assertEqual(restarted.get(key), saved)
        self.assertEqual(client.get("/casos").json()[0]["id"], key)
        self.assertEqual(client.get(f"/casos/{key}").json(), saved)
        data = self.payload(); data["revision"] = 1; data["case"]["title"] = "Título editado"
        updated = client.put(f"/casos/{key}", json=data).json()
        self.assertEqual(updated["revision"], 2)
        self.assertEqual(client.put(f"/casos/{key}", json=data).status_code, 409)
        self.assertEqual(restarted.get(key)["title"], "Título editado")
        self.assertEqual(client.get(f"/casos/{key}/informe?formato=json").json(), updated)
        self.assertEqual(client.get(f"/casos/{key}/informe?revision=1").status_code, 409)
        html = client.get(f"/casos/{key}/informe")
        self.assertIn("attachment", html.headers["content-disposition"])
        self.assertIn("Título editado", html.text)

    def test_report_escapes_user_content_and_retains_evidence(self):
        client = self.client(); saved = client.post("/casos", json=self.payload()).json()
        report = client.get(f"/casos/{saved['id']}/informe").text
        self.assertNotIn("<script>", report)
        self.assertIn("&lt;script&gt;", report)
        self.assertIn("show interfaces Fa0/1 switchport", report)
        self.assertIn("¿Qué sigue?", report)

    def test_missing_case_bad_ids_and_revision(self):
        client = self.client()
        self.assertEqual(client.get("/casos/not-a-uuid").status_code, 422)
        self.assertEqual(client.get("/casos/00000000-0000-0000-0000-000000000000").status_code, 404)
        saved = client.post("/casos", json=self.payload()).json()
        self.assertEqual(client.put(f"/casos/{saved['id']}", json=self.payload()).status_code, 422)

    def test_foreign_database_is_unchanged(self):
        self.store.directory.mkdir(parents=True)
        with closing(sqlite3.connect(self.store.path)) as conn, conn:
            conn.execute("CREATE TABLE unrelated (value TEXT)")
            conn.execute("INSERT INTO unrelated VALUES ('preservar')")
        before = self.store.path.read_bytes()
        with self.assertRaises(RuntimeError):
            self.store.list()
        self.assertEqual(before, self.store.path.read_bytes())

    def test_redirect_is_rejected_before_writing(self):
        outside = Path(self.temp.name) / "outside"; outside.mkdir()
        try:
            (Path(self.temp.name) / ".data").symlink_to(outside, target_is_directory=True)
        except OSError:
            original = Path.resolve
            with patch.object(Path, "resolve", autospec=True, side_effect=lambda p: outside if p == self.store.directory else original(p)):
                with self.assertRaises(RuntimeError):
                    self.store.list()
            self.assertFalse(self.store.path.exists())
            return
        with self.assertRaises(RuntimeError):
            self.store.list()
        self.assertEqual(list(outside.iterdir()), [])

    def test_storage_failure_does_not_claim_success(self):
        client = self.client()
        with patch.object(self.store, "checked_path", side_effect=RuntimeError("no permitido")):
            self.assertEqual(client.post("/casos", json=self.payload()).status_code, 503)

    def test_incomplete_case_preserves_unrequested_results(self):
        client = self.client(); data = self.payload()
        data["case"]["version"] = ""
        data["proposal_requested"] = False; data["diagnosis_requested"] = False
        response = client.post("/casos", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()["document"]["proposal"])
        self.assertIsNone(response.json()["document"]["diagnosis"])

    def test_shared_hardlink_rejected(self):
        import os
        self.store.directory.mkdir(parents=True)
        original = Path(self.temp.name) / "another.sqlite3"
        original.write_bytes(b"do not modify")
        os.link(original, self.store.path)
        with self.assertRaises(RuntimeError):
            self.store.list()
        self.assertEqual(original.read_bytes(), b"do not modify")
