"""Configuración central de NetAssist y lectura de variables de entorno."""

import os
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"
CHROMA_DIR = ROOT_DIR / "backend" / "chroma_db"

os.environ.setdefault("HF_HOME", str(ROOT_DIR / ".cache" / "huggingface"))

# Se carga únicamente el archivo .env del proyecto; las claves no se exponen al cliente.
load_dotenv(ROOT_DIR / ".env")


def _float_env(nombre: str, valor_predeterminado: float) -> float:
    """Lee un número decimal del entorno y falla con un mensaje claro si es inválido."""
    valor = os.getenv(nombre)
    if valor is None:
        return valor_predeterminado
    try:
        return float(valor)
    except ValueError as error:
        raise ValueError(f"La variable {nombre} debe ser un número decimal.") from error


def _int_env(nombre: str, valor_predeterminado: int) -> int:
    """Lee un entero del entorno y falla con un mensaje claro si es inválido."""
    valor = os.getenv(nombre)
    if valor is None:
        return valor_predeterminado
    try:
        return int(valor)
    except ValueError as error:
        raise ValueError(f"La variable {nombre} debe ser un número entero.") from error


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "").strip()
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5500").strip()


def frontend_origins(origin: str) -> list[str]:
    """Admite los dos nombres de loopback solo en el puerto configurado."""
    parsed = urlsplit(origin)
    origins = [origin]
    if (parsed.scheme in {"http", "https"}
            and parsed.hostname in {"localhost", "127.0.0.1"}
            and not parsed.username and not parsed.password
            and parsed.path in {"", "/"} and not parsed.query and not parsed.fragment):
        port = f":{parsed.port}" if parsed.port is not None else ""
        for host in ["localhost", "127.0.0.1"]:
            alias = f"{parsed.scheme}://{host}{port}"
            if alias not in origins:
                origins.append(alias)
    return origins


FRONTEND_ORIGINS = frontend_origins(FRONTEND_ORIGIN)
SUPPORT_CONTACT = os.getenv(
    "SUPPORT_CONTACT", "Contacta al docente o técnico responsable del laboratorio."
).strip()
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
).strip()
RAG_TOP_K = _int_env("RAG_TOP_K", 4)
RAG_DISTANCE_THRESHOLD = _float_env("RAG_DISTANCE_THRESHOLD", 0.65)
LLM_TIMEOUT_SECONDS = 15.0

if RAG_TOP_K < 1:
    raise ValueError("RAG_TOP_K debe ser mayor que cero.")
if not 0 <= RAG_DISTANCE_THRESHOLD <= 2:
    raise ValueError("RAG_DISTANCE_THRESHOLD debe estar entre 0 y 2.")
if not FRONTEND_ORIGIN:
    raise ValueError("FRONTEND_ORIGIN no puede estar vacío.")
