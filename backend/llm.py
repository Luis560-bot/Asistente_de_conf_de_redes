"""Clientes HTTP asíncronos para Gemini y Groq con failover automático."""

import logging
from urllib.parse import quote

import httpx

from .config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_VISION_MODEL,
    LLM_TIMEOUT_SECONDS,
    SUPPORT_CONTACT,
)
from .prompts import construir_prompt

logger = logging.getLogger(__name__)
MENSAJE_FALLBACK = (
    "Lo siento, no pude obtener una respuesta del asistente en este momento. "
    "Por favor, inténtalo de nuevo más tarde o contacta al docente o técnico: "
    f"{SUPPORT_CONTACT}"
)
MENSAJE_IMAGEN_NO_DISPONIBLE = (
    "No pude analizar la captura porque el servicio de visión no respondió. "
    "Vuelve a intentarlo; la imagen sigue disponible para reenviarla."
)


async def _llamar_gemini(mensajes: list[dict], system_prompt: str) -> str:
    """Convierte los roles a contents/model y envía systemInstruction separado."""
    if not GEMINI_API_KEY:
        raise RuntimeError("No está configurada GEMINI_API_KEY.")
    if not GEMINI_MODEL:
        raise RuntimeError("No está configurado GEMINI_MODEL.")

    contenido = []
    for mensaje in mensajes:
        parts = [{"text": mensaje["content"]}]
        if mensaje.get("image"):
            image = mensaje["image"]
            parts.append({"inlineData": {"mimeType": image["mime_type"], "data": image["data"]}})
        contenido.append({"role": "model" if mensaje["role"] == "assistant" else "user", "parts": parts})
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{quote(GEMINI_MODEL, safe='')}:generateContent"
    )
    async with httpx.AsyncClient(timeout=25.0 if any(m.get("image") for m in mensajes) else LLM_TIMEOUT_SECONDS) as cliente:
        respuesta = await cliente.post(
            url,
            headers={"content-type": "application/json", "x-goog-api-key": GEMINI_API_KEY},
            json={
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "contents": contenido,
                "generationConfig": {"maxOutputTokens": 1200},
            },
        )
    respuesta.raise_for_status()
    datos = respuesta.json()
    candidatos = datos.get("candidates", [])
    partes = (
        candidatos[0].get("content", {}).get("parts", [])
        if candidatos and isinstance(candidatos[0], dict)
        else []
    )
    texto = "\n".join(
        parte["text"]
        for parte in partes
        if isinstance(parte, dict) and isinstance(parte.get("text"), str)
    ).strip()
    if not texto:
        raise ValueError("Gemini devolvió una respuesta sin texto.")
    return texto


async def _llamar_groq(mensajes: list[dict], system_prompt: str) -> str:
    """Envía el historial a Groq mediante su endpoint compatible con OpenAI."""
    if not GROQ_API_KEY:
        raise RuntimeError("No está configurada GROQ_API_KEY.")
    visual = any(mensaje.get("image") for mensaje in mensajes)
    model = GROQ_VISION_MODEL if visual else GROQ_MODEL
    if not model:
        raise RuntimeError("No está configurado GROQ_MODEL.")
    messages = []
    for mensaje in mensajes:
        content = mensaje["content"]
        if mensaje.get("image"):
            image = mensaje["image"]
            content = [{"type": "text", "text": content},
                       {"type": "image_url", "image_url": {
                           "url": f"data:{image['mime_type']};base64,{image['data']}"}}]
        messages.append({"role": mensaje["role"], "content": content})
    cuerpo = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}, *messages],
        "max_tokens": 1200,
    }
    async with httpx.AsyncClient(timeout=25.0 if visual else LLM_TIMEOUT_SECONDS) as cliente:
        respuesta = await cliente.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "content-type": "application/json",
            },
            json=cuerpo,
        )
    respuesta.raise_for_status()
    datos = respuesta.json()
    elecciones = datos.get("choices", [])
    mensaje = (
        elecciones[0].get("message", {})
        if elecciones and isinstance(elecciones[0], dict)
        else {}
    )
    texto = mensaje.get("content", "")
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Groq devolvió una respuesta sin texto.")
    return texto.strip()


async def llamar_llm(mensajes: list[dict], contexto_rag: str) -> str:
    """Prueba Gemini primero, pasa a Groq ante un error y siempre devuelve texto."""
    system_prompt = construir_prompt(contexto_rag, SUPPORT_CONTACT)

    try:
        return await _llamar_gemini(mensajes, system_prompt)
    except (httpx.HTTPError, ValueError, RuntimeError, TypeError, KeyError, AttributeError) as error:
        logger.warning(
            "Gemini no pudo responder; se intentará Groq. Tipo de error: %s",
            type(error).__name__,
        )

    try:
        return await _llamar_groq(mensajes, system_prompt)
    except (httpx.HTTPError, ValueError, RuntimeError, TypeError, KeyError, AttributeError) as error:
        logger.error(
            "Gemini y Groq no pudieron responder. Tipo de error: %s",
            type(error).__name__,
        )
        return MENSAJE_IMAGEN_NO_DISPONIBLE if any(m.get("image") for m in mensajes) else MENSAJE_FALLBACK
