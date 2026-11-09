"""Imágenes del chat: contenido acotado y verificado, sin archivos ni nuevas bases."""
import base64
import binascii
from io import BytesIO
from typing import Literal

from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field, model_validator
from starlette.responses import JSONResponse

MAX_IMAGE_BYTES = 3 * 1024 * 1024
MAX_CHAT_IMAGES = 3
MAX_REQUEST_BYTES = 20 * 1024 * 1024


class ChatImage(BaseModel):
    mime_type: Literal["image/png", "image/jpeg", "image/webp"]
    data: str = Field(min_length=4, max_length=4 * ((MAX_IMAGE_BYTES + 2) // 3))
    name: str = Field(default="captura.png", min_length=1, max_length=120)

    @model_validator(mode="after")
    def verify_image(self):
        try:
            raw = base64.b64decode(self.data, validate=True)
            if not raw or len(raw) > MAX_IMAGE_BYTES:
                raise ValueError("La captura debe pesar como máximo 3 MB.")
            with Image.open(BytesIO(raw)) as image:
                expected = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}
                if expected.get(image.format) != self.mime_type:
                    raise ValueError("El formato de la captura no coincide con su contenido.")
                if image.width * image.height > 16_777_216 or max(image.size) > 8192:
                    raise ValueError("La captura supera las dimensiones admitidas (16 megapíxeles).")
                if getattr(image, "n_frames", 1) != 1:
                    raise ValueError("Adjunta una captura estática, sin animación.")
                image.verify()
            with Image.open(BytesIO(raw)) as image:
                image.load()
        except (binascii.Error, UnidentifiedImageError, OSError, SyntaxError,
                Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
            raise ValueError("La captura no contiene una imagen válida PNG, JPG o WebP.") from error
        return self


def check_image_count(messages):
    if sum(message.image is not None for message in messages) > MAX_CHAT_IMAGES:
        raise ValueError("Se admiten hasta 3 capturas por conversación. Limpia el chat para iniciar otra.")


class ChatBodyLimit:
    """Limita antes de decodificar JSON, también con solicitudes sin Content-Length."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if (scope["type"] != "http" or scope["method"] not in {"POST", "PUT"}
                or not (scope["path"] == "/chat" or scope["path"].startswith("/casos"))):
            return await self.app(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            size += len(message.get("body", b""))
            if size > MAX_REQUEST_BYTES:
                response = JSONResponse({"detail": "La solicitud supera 20 MB. Reduce las capturas."}, status_code=413)
                return await response(scope, receive, send)
            chunks.append(message.get("body", b""))
            if not message.get("more_body", False):
                break
        body = b"".join(chunks)
        delivered = False

        async def limited_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        await self.app(scope, limited_receive, send)
