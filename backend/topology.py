"""Topología visual acotada al caso VLAN; no controla Packet Tracer."""
import re
import unicodedata
from html import escape
from textwrap import wrap

from pydantic import BaseModel, Field, field_validator, model_validator

from .generator import generate, parse_ports


class TopologyGroup(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    vlan: int = Field(ge=2, le=1001)
    ports: list[str] = Field(min_length=1, max_length=32)

    @field_validator("ports")
    @classmethod
    def canonical_ports(cls, ports):
        return parse_ports(",".join(ports))


class Topology(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    model: str = Field(max_length=80)
    groups: list[TopologyGroup] = Field(min_length=2, max_length=2)

    @model_validator(mode="after")
    def distinct_assignments(self):
        ports = [port for group in self.groups for port in group.ports]
        if len(ports) > 32 or len(ports) != len(set(ports)):
            raise ValueError("La imagen admite hasta 32 puertos distintos.")
        if self.groups[0].vlan == self.groups[1].vlan:
            raise ValueError("Las VLAN deben ser distintas.")
        return self


def requests_topology(text):
    normalized = "".join(c for c in unicodedata.normalize("NFD", text.lower())
                         if unicodedata.category(c) != "Mn")
    subject = re.search(r"\b(topologia|diagrama|esquema)\b", normalized) or (
        re.search(r"\b(imagen|dibujo)\b", normalized)
        and re.search(r"\b(red|cisco|packet|switch|vlan)\b", normalized))
    action = re.search(r"\b(gener\w*|dibuj\w*|muestr\w*|mostrar\w*|ver|crea\w*|haz\w*|hacer\w*|quiero|necesito|imagen)\b", normalized)
    return bool(subject and action)


def build_topology(case):
    if case is None:
        return None, "Abre una práctica o carga un ejemplo y pídeme la topología. Usaré sus VLAN y puertos para dibujarla."
    reference = generate(case)
    if reference["errors"]:
        return None, "Antes de dibujar la topología, corrige estos datos: " + " ".join(reference["errors"])
    if any(not group["vlan"] or not group["ports"] for group in reference["groups"]):
        return None, "Completa las VLAN y los puertos de ambos grupos y pulsa Actualizar práctica. Después podré mostrarte la topología."
    if sum(len(group["ports"]) for group in reference["groups"]) > 32:
        return None, "Esta vista admite hasta 32 PC. Reduce la cantidad de puertos para dibujar el caso."
    topology = Topology(title=case.title, model=case.model,
                        groups=[TopologyGroup(name=g["name"], vlan=g["vlan"], ports=g["ports"])
                                for g in reference["groups"]])
    return topology, ("Aquí tienes la topología de tu práctica. Puedes ampliarla o descargarla. "
                      "Es una propuesta: no es un archivo .pkt ni una red verificada.")


def render_svg(topology):
    """Solo primitivas propias y texto escapado; nunca SVG aportado por el modelo."""
    total = sum(len(g.ports) for g in topology.groups)
    width = max(920, total * 180 + 100)
    unit = (width - 100) / total
    center = width / 2
    safe = lambda value: escape(str(value), quote=True)
    text = lambda x, y, value, size=17, color="#234352": (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="{color}">{safe(value)}</text>')
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="600" viewBox="0 0 {width} 600" role="img" font-family="Arial, sans-serif">',
             '<title>Topología propuesta para Packet Tracer</title>',
             f'<rect width="{width}" height="600" fill="#fff"/>',
             text(center, 36, topology.title, min(23, int((width-70)/(max(len(topology.title), 1)*.65)))),
             text(center, 64, "Un switch · Dos VLAN · Puertos de acceso", 15),
             f'<rect x="{center-145}" y="105" width="290" height="74" rx="13" fill="#183d4b"/>',
             text(center, 134, "SW1 · Cisco IOS", 19, "#fff"),
             text(center, 160, topology.model or "Modelo pendiente", 14, "#c9eee5")]
    index = 0
    for group_index, group in enumerate(topology.groups):
        count = len(group.ports)
        left = 40 + index * unit + group_index * 20
        panel_width = count * unit
        color = ["#087f73", "#2866ac"][group_index]
        background = ["#edf8f3", "#eff5fc"][group_index]
        parts.append(f'<rect x="{left}" y="270" width="{panel_width}" height="278" rx="16" fill="{background}"/>')
        for port in group.ports:
            x = left + (index - sum(len(g.ports) for g in topology.groups[:group_index]) + .5) * unit
            sx = center - 105 + (index + .5) * 210 / total
            short = port.replace("FastEthernet", "Fa").replace("GigabitEthernet", "Gi")
            parts.extend([f'<line x1="{sx}" y1="179" x2="{x}" y2="342" stroke="{color}" stroke-width="3"/>',
                          f'<rect x="{x-55}" y="307" width="110" height="26" rx="6" fill="{background}"/>',
                          text(x, 326, short, 16, color),
                          f'<rect x="{x-42}" y="346" width="84" height="53" rx="5" fill="#fff" stroke="{color}" stroke-width="3"/>',
                          f'<path d="M{x} 399 v13 m-25 0 h50" stroke="{color}" stroke-width="3" fill="none"/>',
                          text(x, 436, f"PC-{index+1}", 17)])
            index += 1
        for row, label in enumerate(wrap(f"{group.name} · VLAN {group.vlan}", width=max(18, int((panel_width-24)/9)))):
            parts.append(text(left + panel_width / 2, 465 + row * 18, label, 16, color))
    parts.extend([text(center, 578, "Cable de cobre directo · Esquema propuesto, pendiente de comprobar en Packet Tracer", 14), '</svg>'])
    return "".join(parts)
