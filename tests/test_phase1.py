import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from backend import llm
from backend.rag import RagService


class Providers(unittest.IsolatedAsyncioTestCase):
    async def test_primary_success(self):
        with patch.object(llm, '_llamar_gemini', AsyncMock(return_value='ok')), patch.object(llm, '_llamar_groq', AsyncMock()) as backup:
            self.assertEqual(await llm.llamar_llm([], ''), 'ok')
            backup.assert_not_called()

    async def test_primary_failures(self):
        for failure in (RuntimeError('sin modelo'), ValueError('vacío'), httpx.ReadTimeout('timeout'), TypeError('json inesperado')):
            with self.subTest(failure=type(failure).__name__), patch.object(llm, '_llamar_gemini', AsyncMock(side_effect=failure)), patch.object(llm, '_llamar_groq', AsyncMock(return_value='respaldo')):
                self.assertEqual(await llm.llamar_llm([], ''), 'respaldo')

    async def test_incomplete_primary_configuration(self):
        with patch.object(llm, 'GEMINI_API_KEY', 'prueba'), patch.object(llm, 'GEMINI_MODEL', ''), patch.object(llm, '_llamar_groq', AsyncMock(return_value='respaldo')):
            self.assertEqual(await llm.llamar_llm([], ''), 'respaldo')

    async def test_both_unavailable(self):
        with patch.object(llm, '_llamar_gemini', AsyncMock(side_effect=RuntimeError())), patch.object(llm, '_llamar_groq', AsyncMock(side_effect=ValueError())):
            self.assertEqual(await llm.llamar_llm([], ''), llm.MENSAJE_FALLBACK)


class Reindex(unittest.TestCase):
    def test_reject_external_storage_before_client(self):
        from pathlib import Path
        with patch('backend.rag.CHROMA_DIR', Path('C:/unrelated')), patch('backend.rag.chromadb.PersistentClient') as client:
            with self.assertRaises(RuntimeError):
                RagService().initialize()
            client.assert_not_called()

    def test_failed_read_keeps_active_collection(self):
        service = RagService()
        active = service.coleccion = MagicMock()
        service.modelo = MagicMock()
        service.cliente = MagicMock()
        with patch('backend.rag.SentenceTransformer'), patch('backend.rag._leer_archivo', side_effect=OSError('lectura')):
            with self.assertRaises(OSError):
                service.initialize()
        self.assertIs(service.coleccion, active)
        service.cliente.delete_collection.assert_not_called()

    def test_failed_write_only_removes_new_generation(self):
        service = RagService()
        active = service.coleccion = MagicMock()
        service.modelo = MagicMock()
        service.cliente = MagicMock()
        service.cliente.create_collection.return_value.add.side_effect = RuntimeError('escritura')
        with patch('backend.rag.SentenceTransformer'), patch('backend.rag._leer_archivo', return_value='VLAN'):
            with self.assertRaises(RuntimeError):
                service.initialize()
        self.assertIs(service.coleccion, active)
        deleted = service.cliente.delete_collection.call_args.args[0]
        self.assertTrue(deleted.startswith('manuales_netassist_'))


class ApiResilience(unittest.TestCase):
    def test_reindex_failure_keeps_chat_available(self):
        from backend import main
        from fastapi.testclient import TestClient
        service = MagicMock()
        service.initialize.side_effect = [{"archivos": 3, "fragmentos": 3}, OSError("fallo")]
        service.coleccion = MagicMock()
        service.buscar.return_value = []
        with patch.object(main, "rag_service", service), patch.object(main, "llamar_llm", AsyncMock(return_value="respuesta")):
            with TestClient(main.app) as client:
                self.assertEqual(client.post("/reindexar").status_code, 503)
                self.assertTrue(client.get("/health").json()["rag_ready"])
                reply = client.post("/chat", json={"messages": [{"role": "user", "content": "VLAN"}]})
                self.assertEqual(reply.json()["reply"], "respuesta")

    def test_startup_without_index_returns_contact(self):
        from backend import main
        from fastapi.testclient import TestClient
        service = MagicMock()
        service.coleccion = None
        service.resumen = {"archivos": 0, "fragmentos": 0}
        service.initialize.side_effect = OSError("sin índice")
        with patch.object(main, "rag_service", service):
            with TestClient(main.app) as client:
                self.assertFalse(client.get("/health").json()["rag_ready"])
                reply = client.post("/chat", json={"messages": [{"role": "user", "content": "VLAN"}]})
                self.assertEqual(reply.json()["reply"], main.MENSAJE_FALLBACK)


if __name__ == '__main__':
    unittest.main()
