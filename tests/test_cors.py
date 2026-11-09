"""Regresión de conexión desde los dos nombres locales del frontend."""
import unittest

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from backend.config import frontend_origins


class LocalOrigins(unittest.TestCase):
    def test_loopback_aliases_keep_configured_port(self):
        for host in ["localhost", "127.0.0.1"]:
            app = FastAPI()
            app.add_middleware(
                CORSMiddleware,
                allow_origins=frontend_origins(f"http://{host}:5501"),
                allow_methods=["POST"], allow_headers=["Content-Type"],
            )
            with TestClient(app) as client:
                for origin, expected in [
                    ("http://localhost:5501", 200),
                    ("http://127.0.0.1:5501", 200),
                    ("http://localhost:5500", 400),
                    ("http://127.0.0.1:5502", 400),
                    ("https://localhost:5501", 400),
                    ("http://localhost.ejemplo.com:5501", 400),
                    ("http://192.168.1.10:5501", 400),
                ]:
                    with self.subTest(host=host, origin=origin):
                        response = client.options("/chat", headers={
                            "Origin": origin,
                            "Access-Control-Request-Method": "POST",
                            "Access-Control-Request-Headers": "content-type",
                        })
                        self.assertEqual(response.status_code, expected)
                        self.assertEqual(response.headers.get("access-control-allow-origin"),
                                         origin if expected == 200 else None)

    def test_external_origin_does_not_add_local_aliases(self):
        origin = "https://netassist.ejemplo.com"
        self.assertEqual(frontend_origins(origin), [origin])
