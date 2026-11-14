"""Carga de manuales, fragmentación, indexado y búsqueda semántica local."""

import logging
import json
from threading import RLock
from uuid import uuid4
from pathlib import Path
from typing import Any

import chromadb
from pypdf import PdfReader

from .config import (
    ROOT_DIR,
    CHROMA_DIR,
    DOCS_DIR,
    EMBEDDING_MODEL,
    RAG_DISTANCE_THRESHOLD,
    RAG_TOP_K,
)

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
COLLECTION_NAME = "manuales_netassist"
CHUNK_WORDS = 500
CHUNK_OVERLAP = 50


def fragmentar_texto(texto: str, tamano: int = CHUNK_WORDS, solapamiento: int = CHUNK_OVERLAP) -> list[str]:
    """Divide el texto por palabras y conserva un solapamiento entre fragmentos."""
    palabras = texto.split()
    if tamano <= 0 or solapamiento < 0 or solapamiento >= tamano:
        raise ValueError("El tamaño debe ser positivo y el solapamiento menor al tamaño.")
    paso = tamano - solapamiento
    return [
        " ".join(palabras[inicio : inicio + tamano])
        for inicio in range(0, len(palabras), paso)
        if palabras[inicio : inicio + tamano]
    ]


def _leer_archivo(ruta: Path) -> str:
    """Extrae texto de archivos PDF o TXT admitidos."""
    if ruta.suffix.lower() == ".txt":
        return ruta.read_text(encoding="utf-8", errors="replace")
    lector = PdfReader(str(ruta))
    paginas = [pagina.extract_text() or "" for pagina in lector.pages]
    return "\n".join(paginas)


class RagService:
    """Mantiene el modelo de embeddings y la colección local de ChromaDB."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._build_lock = RLock()
        self.modelo: SentenceTransformer | None = None
        self.cliente: Any | None = None
        self.coleccion: Any | None = None

    def initialize(self) -> dict[str, int]:
        """Construye una generación completa antes de publicar el nuevo índice."""
        with self._build_lock:
            return self._initialize()

    def _initialize(self) -> dict[str, int]:
        esperado = ROOT_DIR / "backend" / "chroma_db"
        if CHROMA_DIR.resolve() != esperado or any(
            (getattr(p.lstat(), "st_file_attributes", 0) & 0x400) or p.is_symlink()
            for p in (ROOT_DIR / "backend", CHROMA_DIR)
            if p.exists()
        ):
            raise RuntimeError("El almacenamiento debe ser exclusivo de backend/chroma_db de NetAssist.")
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        if self.cliente is None:
            self.cliente = chromadb.PersistentClient(path=str(CHROMA_DIR))
        manifest = CHROMA_DIR / "netassist_index.json"
        # Recuperar el último índice publicado incluso si falla la reconstrucción.
        if self.coleccion is None and manifest.exists():
            estado = json.loads(manifest.read_text(encoding="utf-8"))
            nombre = estado["collection"]
            if not nombre.startswith(COLLECTION_NAME + "_"):
                raise RuntimeError("Manifiesto de índice ajeno a NetAssist.")
            modelo = SentenceTransformer(estado["model"])
            coleccion = self.cliente.get_collection(nombre)
            with self._lock:
                self.modelo, self.coleccion = modelo, coleccion
                self.resumen = estado["summary"]
        modelo = SentenceTransformer(EMBEDDING_MODEL)
        archivos = sorted(r for r in DOCS_DIR.rglob("*")
                          if r.is_file() and r.suffix.lower() in {".txt", ".pdf"})
        documentos, metadatos, ids = [], [], []
        for archivo in archivos:
            for numero, fragmento in enumerate(fragmentar_texto(_leer_archivo(archivo))):
                documentos.append(fragmento)
                metadatos.append({"archivo": str(archivo.relative_to(DOCS_DIR)), "fragmento": numero + 1})
                ids.append(f"{archivo.relative_to(DOCS_DIR).as_posix()}-{numero}")
        if not documentos:
            raise ValueError("No hay documentación indexable; se conserva el índice anterior.")
        embeddings = modelo.encode(documentos, normalize_embeddings=True).tolist()
        nombre = COLLECTION_NAME + "_" + uuid4().hex
        nueva = self.cliente.create_collection(name=nombre, metadata={"hnsw:space": "cosine"})
        temporal = manifest.with_suffix(".tmp")
        try:
            for inicio in range(0, len(ids), 100):
                fin = inicio + 100
                nueva.add(ids=ids[inicio:fin], documents=documentos[inicio:fin],
                          metadatas=metadatos[inicio:fin], embeddings=embeddings[inicio:fin])
            if nueva.count() != len(documentos):
                raise RuntimeError("El índice construido está incompleto.")
            resumen = {"archivos": len(archivos), "fragmentos": len(documentos)}
            temporal.write_text(json.dumps({"collection": nombre, "model": EMBEDDING_MODEL,
                                           "summary": resumen}), encoding="utf-8")
            with self._lock:
                temporal.replace(manifest)
                self.modelo, self.coleccion, self.resumen = modelo, nueva, resumen
        except Exception:
            # Solo elimina la generación creada por este intento, nunca la activa.
            self.cliente.delete_collection(nombre)
            raise
        logger.info("Índice RAG publicado: %s", resumen)
        return resumen

    def buscar(self, consulta: str) -> list[dict[str, str | float]]:
        """Devuelve hasta cuatro fragmentos que superen el umbral de relevancia."""
        with self._lock:
            modelo, coleccion = self.modelo, self.coleccion
        if modelo is None or coleccion is None:
            raise RuntimeError("El servicio RAG no está inicializado.")
        if coleccion.count() == 0:
            return []

        embedding = modelo.encode([consulta], normalize_embeddings=True).tolist()
        resultados = coleccion.query(
            query_embeddings=embedding,
            n_results=min(RAG_TOP_K, coleccion.count()),
            include=["documents", "metadatas", "distances"],
        )
        documentos = resultados.get("documents", [[]])[0]
        metadatos = resultados.get("metadatas", [[]])[0]
        distancias = resultados.get("distances", [[]])[0]
        relevantes: list[dict[str, str | float]] = []

        for documento, metadata, distancia in zip(documentos, metadatos, distancias):
            if documento is None or distancia is None or distancia > RAG_DISTANCE_THRESHOLD:
                continue
            archivo = str((metadata or {}).get("archivo", "manual sin nombre"))
            relevantes.append(
                {"texto": str(documento), "archivo": archivo, "distancia": float(distancia)}
            )
        return relevantes


def formatear_contexto(fragmentos: list[dict[str, str | float]]) -> str:
    """Prepara fragmentos y referencias para incluirlos en el prompt."""
    if not fragmentos:
        return "No se encontraron fragmentos relevantes en los manuales disponibles."
    bloques = []
    for indice, fragmento in enumerate(fragmentos, start=1):
        bloques.append(
            f"[Fragmento {indice} | Fuente: {fragmento['archivo']}]\n{fragmento['texto']}"
        )
    return "\n\n".join(bloques)
