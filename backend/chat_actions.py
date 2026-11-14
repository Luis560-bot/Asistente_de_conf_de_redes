"""Acciones del chat sobre el caso abierto y preguntas de continuación."""
import re
import unicodedata

from .generator import generate


def requests_configuration(text):
    text = "".join(c for c in unicodedata.normalize("NFD", text.lower())
                   if unicodedata.category(c) != "Mn")
    return bool(re.search(r"\b(configur\w*|comandos)\b", text)
                and re.search(r"\b(gener\w*|dame|muestr\w*|quiero|necesito|prepara\w*|ayuda\w*|configurar)\b", text)
                and not re.search(r"\b(explica\w*|que significa|que es|por que)\b", text))


def configuration_reply(case):
    if case is None:
        return "Abre una práctica o carga un ejemplo para preparar su configuración.", None, []
    proposal = generate(case)
    if proposal["status"] != "proposed":
        issues = [f"Falta {item}." for item in proposal["missing"]] + proposal["errors"]
        return " ".join(issues) + " Corrige el formulario y pulsa Actualizar práctica.", proposal, []
    return ("Configuración de referencia para tu switch:\n\n```ios\n" + proposal["commands"]
            + "\n```\n\nRevisa los puertos antes de aplicarla en Packet Tracer. La prueba de laboratorio sigue pendiente.",
            proposal, ["¿Cómo compruebo que los puertos pertenecen a la VLAN correcta?"])


def split_suggestion(reply):
    # El proveedor propone una continuación del tema; nunca se ejecuta sola.
    match = re.search(r"\n+Siguiente pregunta:\s*([^\n]+)\s*$", reply)
    if not match:
        return reply, []
    question = match[1].strip()
    answer = reply[:match.start()].strip()
    return (answer or reply), [question] if answer and 5 <= len(question) <= 180 else []
