"""Clientes HTTP asíncronos para Claude y Gemini con failover automático."""

import logging
from urllib.parse import quote

import httpx

from .config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
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


def _validar_configuracion() -> None:
    """Comprueba que cada proveedor configurado tenga también su modelo."""
    if ANTHROPIC_API_KEY and not ANTHROPIC_MODEL:
        raise RuntimeError("ANTHROPIC_MODEL debe configurarse si se define ANTHROPIC_API_KEY.")
    if GEMINI_API_KEY and not GEMINI_MODEL:
        raise RuntimeError("GEMINI_MODEL debe configurarse si se define GEMINI_API_KEY.")


async def _llamar_claude(mensajes: list[dict[str, str]], system_prompt: str) -> str:
    """Envía el prompt de sistema separado, según el formato de Messages API."""
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("No está configurada ANTHROPIC_API_KEY.")
    if not ANTHROPIC_MODEL:
        raise RuntimeError("No está configurado ANTHROPIC_MODEL.")

    cuerpo = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1200,
        "system": system_prompt,
        "messages": mensajes,
    }
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT_SECONDS) as cliente:
        respuesta = await cliente.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=cuerpo,
        )
    respuesta.raise_for_status()
    datos = respuesta.json()
    contenido = datos.get("content", [])
    texto = "\n".join(
        bloque["text"]
        for bloque in contenido
        if bloque.get("type") == "text" and isinstance(bloque.get("text"), str)
    ).strip()
    if not texto:
        raise ValueError("Claude devolvió una respuesta sin texto.")
    return texto


async def _llamar_gemini(mensajes: list[dict[str, str]], system_prompt: str) -> str:
    """Convierte los roles a contents/model y envía systemInstruction separado."""
    if not GEMINI_API_KEY:
        raise RuntimeError("No está configurada GEMINI_API_KEY.")
    if not GEMINI_MODEL:
        raise RuntimeError("No está configurado GEMINI_MODEL.")

    contenido = [
        {
            "role": "model" if mensaje["role"] == "assistant" else "user",
            "parts": [{"text": mensaje["content"]}],
        }
        for mensaje in mensajes
    ]
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{quote(GEMINI_MODEL, safe='')}:generateContent"
    )
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT_SECONDS) as cliente:
        respuesta = await cliente.post(
            url,
            params={"key": GEMINI_API_KEY},
            headers={"content-type": "application/json"},
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
        if isinstance(parte.get("text"), str)
    ).strip()
    if not texto:
        raise ValueError("Gemini devolvió una respuesta sin texto.")
    return texto


async def llamar_llm(mensajes: list[dict[str, str]], contexto_rag: str) -> str:
    """Prueba Claude primero, pasa a Gemini ante un error y siempre devuelve texto."""
    _validar_configuracion()
    system_prompt = construir_prompt(contexto_rag, SUPPORT_CONTACT)

    try:
        return await _llamar_claude(mensajes, system_prompt)
    except (httpx.HTTPError, ValueError, RuntimeError) as error:
        logger.warning(
            "Claude no pudo responder; se intentará Gemini. Tipo de error: %s",
            type(error).__name__,
        )

    try:
        return await _llamar_gemini(mensajes, system_prompt)
    except (httpx.HTTPError, ValueError, RuntimeError) as error:
        logger.error(
            "Claude y Gemini no pudieron responder. Tipo de error: %s",
            type(error).__name__,
        )
        return MENSAJE_FALLBACK
