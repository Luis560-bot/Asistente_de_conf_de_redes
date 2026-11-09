"""Adjuntos reales de imagen, contratos multimodales y persistencia aislada."""
import base64
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from PIL import Image
from fastapi.testclient import TestClient
from pydantic import ValidationError
from backend import main, llm
from backend.chat_images import ChatImage, ChatBodyLimit, MAX_REQUEST_BYTES
from backend.cases import CaseStore


def capture():
    data = BytesIO()
    Image.new("RGB", (120, 80), "white").save(data, format="PNG")
    return {"mime_type": "image/png", "data": base64.b64encode(data.getvalue()).decode(),
            "name": "captura <script>.png"}


class ChatImages(unittest.TestCase):
    def client(self, model=None, rag_error=False):
        service = MagicMock(); service.buscar.return_value = []
        if rag_error:
            service.initialize.side_effect = RuntimeError("sin índice")
        self.enterContext(patch.object(main, "rag_service", service))
        self.model = self.enterContext(patch.object(main, "llamar_llm", model or AsyncMock(return_value="Veo una captura.")))
        return self.enterContext(TestClient(main.app))

    def test_image_only_and_history_reach_model_even_without_manuals(self):
        client = self.client(rag_error=True)
        image = capture()
        response = client.post("/chat", json={"messages": [{"role": "user", "image": image}]})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["image_analyzed"])
        self.assertEqual(self.model.await_args.args[0][0]["image"], image)
        messages = [{"role": "user", "content": "Mira esta captura", "image": image},
                    {"role": "assistant", "content": "Veo una captura"},
                    {"role": "user", "content": "¿Qué puerto aparece?"}]
        response = client.post("/chat", json={"messages": messages})
        self.assertTrue(response.json()["image_analyzed"])
        self.assertEqual(self.model.await_args.args[0][0]["image"], image)

    def test_image_does_not_trigger_case_generator_instead_of_vision(self):
        client = self.client()
        for question in ["Dame la configuración de esta captura", "Muéstrame la topología de esta imagen"]:
            response = client.post("/chat", json={"messages": [{"role": "user", "content": question, "image": capture()}]})
            self.assertEqual(response.json()["reply"], "Veo una captura.")
        self.assertEqual(self.model.await_count, 2)

    def test_invalid_attachments_never_reach_provider_or_echo_base64(self):
        client = self.client()
        wrong = [dict(capture(), mime_type="image/svg+xml"), dict(capture(), mime_type="image/jpeg"),
                 dict(capture(), data="not base64"), dict(capture(), data=base64.b64encode(b"not a PNG").decode()),
                 dict(capture(), data="A" * (4 * 1024 * 1024 + 4))]
        for image in wrong:
            response = client.post("/chat", json={"messages": [{"role": "user", "content": "Revisa", "image": image}]})
            self.assertEqual(response.status_code, 422)
            self.assertNotIn('"input"', response.text)
        self.model.assert_not_awaited()

    def test_count_role_empty_and_dimensions_limits(self):
        client = self.client()
        for messages in [[{"role": "user", "image": capture()}] * 4,
                         [{"role": "assistant", "content": "texto", "image": capture()}, {"role": "user", "content": "hola"}],
                         [{"role": "user", "content": "  "}]]:
            self.assertEqual(client.post("/chat", json={"messages": messages}).status_code, 422)
        data = BytesIO(); Image.new("1", (8193, 1)).save(data, format="PNG")
        with self.assertRaises(ValidationError):
            ChatImage(**dict(capture(), data=base64.b64encode(data.getvalue()).decode()))
        self.model.assert_not_awaited()

    def test_failed_vision_is_explicit(self):
        client = self.client(AsyncMock(return_value=llm.MENSAJE_IMAGEN_NO_DISPONIBLE))
        response = client.post("/chat", json={"messages": [{"role": "user", "image": capture()}]})
        self.assertFalse(response.json()["image_analyzed"])
        self.assertFalse(response.json()["suggestions"])

    def test_saved_image_roundtrip_and_portable_report(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root / ".cache") as folder:
            store = CaseStore(Path(folder))
            self.assertTrue(store.checked_path().is_relative_to(root / ".cache"))
            self.enterContext(patch.object(main, "case_store", store))
            client = self.client()
            payload = {"case": {"title": "Captura de prueba", "groups": [{"name": "Admin"}, {"name": "Lab"}]},
                       "messages": [{"role": "user", "content": "¿Qué ves?", "image": capture()}]}
            saved = client.post("/casos", json=payload)
            self.assertEqual(saved.status_code, 201)
            key = saved.json()["id"]
            restored = client.get(f"/casos/{key}").json()["document"]
            self.assertEqual(restored["messages"][0]["image"], capture())
            report = client.get(f"/casos/{key}/informe").text
            self.assertIn("data:image/png;base64,", report)
            self.assertIn("&lt;script&gt;", report)
            self.assertNotIn("<script>", report)
            payload["messages"] *= 4
            self.assertEqual(client.post("/casos", json=payload).status_code, 422)


class VisionProviders(unittest.IsolatedAsyncioTestCase):
    async def test_http_payloads_keep_images_and_use_separate_groq_model(self):
        calls = []
        async def handle(request):
            body = json.loads(request.content); calls.append(body)
            if "googleapis" in request.url.host:
                return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "lectura"}]}}]})
            return httpx.Response(200, json={"choices": [{"message": {"content": "lectura"}}]})
        original = httpx.AsyncClient
        def client(**kwargs):
            return original(transport=httpx.MockTransport(handle), **kwargs)
        messages = [{"role": "user", "content": "¿Qué ves?", "image": capture()}]
        with patch.object(llm, "GEMINI_API_KEY", "test"), patch.object(llm, "GEMINI_MODEL", "vision"), \
                patch.object(llm, "GROQ_API_KEY", "test"), patch.object(llm, "GROQ_MODEL", "text"), \
                patch.object(llm, "GROQ_VISION_MODEL", "vision-backup"), patch.object(llm.httpx, "AsyncClient", client):
            self.assertEqual(await llm._llamar_gemini(messages, "system"), "lectura")
            self.assertEqual(calls[-1]["contents"][0]["parts"][1]["inlineData"]["data"], capture()["data"])
            self.assertEqual(await llm._llamar_groq(messages, "system"), "lectura")
            self.assertEqual(calls[-1]["model"], "vision-backup")
            self.assertIn(capture()["data"], calls[-1]["messages"][1]["content"][1]["image_url"]["url"])
            await llm._llamar_groq([{"role": "user", "content": "hola"}], "system")
            self.assertEqual(calls[-1]["model"], "text")

    async def test_failover_keeps_image_and_does_not_claim_analysis(self):
        messages = [{"role": "user", "content": "Revisa", "image": capture()}]
        with patch.object(llm, "_llamar_gemini", AsyncMock(side_effect=RuntimeError())), \
                patch.object(llm, "_llamar_groq", AsyncMock(return_value="Veo la imagen")) as backup:
            self.assertEqual(await llm.llamar_llm(messages, ""), "Veo la imagen")
            self.assertEqual(backup.await_args.args[0][0]["image"], capture())
        with patch.object(llm, "_llamar_gemini", AsyncMock(side_effect=RuntimeError())), \
                patch.object(llm, "_llamar_groq", AsyncMock(side_effect=RuntimeError())):
            self.assertEqual(await llm.llamar_llm(messages, ""), llm.MENSAJE_IMAGEN_NO_DISPONIBLE)

    async def test_body_limit_rejects_chunked_before_application(self):
        app = AsyncMock(); send = AsyncMock()
        receive = AsyncMock(side_effect=[{"type": "http.request", "body": b"x" * MAX_REQUEST_BYTES, "more_body": True},
                                        {"type": "http.request", "body": b"x", "more_body": False}])
        await ChatBodyLimit(app)({"type": "http", "method": "POST", "path": "/chat"}, receive, send)
        app.assert_not_awaited()
        self.assertEqual(send.await_args_list[0].args[0]["status"], 413)
