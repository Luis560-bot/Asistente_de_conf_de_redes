"""Navegación integrada sin abrir índices, bases ni proveedores reales."""
import unittest
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from backend import main


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.targets = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.targets.append(value)


class Navigation(unittest.TestCase):
    def setUp(self):
        service = MagicMock()
        service.initialize.return_value = {"archivos": 0, "fragmentos": 0}
        self.enterContext(patch.object(main, "rag_service", service))
        self.client = self.enterContext(TestClient(main.app))

    def assert_local_targets_available(self, response):
        for target in Links(response.text).targets:
            if target.startswith("#") or urlsplit(target).scheme:
                continue
            with self.subTest(target=target):
                result = self.client.get(urljoin(str(response.url), target))
                self.assertEqual(result.status_code, 200)

    def test_presentation_entry_points_and_resources(self):
        for path in ["/", "/Presentacion"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.url.path, "/frontend/presentacion.html")
                self.assertIn('href="chat.html"', response.text)
                self.assert_local_targets_available(response)

    def test_presentation_opens_current_laboratory(self):
        response = self.client.get("/frontend/chat.html")
        self.assertEqual(response.status_code, 200)
        for element in ["case-form", "save-case", "attach-image", "chat-panel"]:
            self.assertIn(f'id="{element}"', response.text)
        self.assertIn('href="presentacion.html"', response.text)
        self.assert_local_targets_available(response)
        self.assertEqual(self.client.get("/health").status_code, 200)
