"""Generador acotado de referencia; no ejecuta ni verifica equipos."""
import re

SOURCE = "https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst2960/software/release/15-0_2_se/configuration/guide/scg2960/swvlan.html"


def parse_ports(value):
    """Lista explícita, sin rangos ni texto que pueda convertirse en comandos."""
    ports = []
    for token in value.split(","):
        match = re.fullmatch(r"\s*(Fa|FastEthernet|Gi|GigabitEthernet)(0|[1-9]\d?)/(0|[1-9]\d?)(?:/(0|[1-9]\d?))?\s*", token, re.I)
        if not match:
            raise ValueError("Usa puertos separados por comas, como Fa0/1, Fa0/2 o Gi1/0/1; sin rangos.")
        prefix = "FastEthernet" if match[1].lower().startswith("fa") else "GigabitEthernet"
        numbers = [part for part in match.groups()[1:] if part is not None]
        if int(numbers[-1]) == 0:
            raise ValueError("El número final del puerto debe ser mayor que cero.")
        port = prefix + "/".join(numbers)
        if port in ports:
            raise ValueError(f"Puerto repetido: {port}.")
        ports.append(port)
    return ports


def generate(case):
    missing, errors, groups = [], [], []
    for field, label in [("model", "modelo del switch")]:
        if not getattr(case, field).strip():
            missing.append(label)
    used = set()
    for index, group in enumerate(case.groups):
        label = group.name.strip() or f"Grupo {index + 1}"
        vlan, ports = None, []
        if not group.vlan.strip():
            missing.append(f"VLAN de {label}")
        elif not re.fullmatch(r"[0-9]+", group.vlan.strip()) or not 2 <= int(group.vlan) <= 1001:
            errors.append(f"{label}: usa una VLAN entre 2 y 1001 (alcance de esta práctica).")
        else:
            vlan = int(group.vlan)
        if not group.ports.strip():
            missing.append(f"puertos de {label}")
        else:
            try:
                ports = parse_ports(group.ports)
                overlap = used.intersection(ports)
                if overlap:
                    errors.append("Puertos asignados a ambos grupos: " + ", ".join(sorted(overlap)))
                used.update(ports)
            except ValueError as error:
                errors.append(f"{label}: {error}")
        groups.append({"name": label, "vlan": vlan, "ports": ports, "cli_name": ["ADMINISTRACION", "LABORATORIO"][index]})
    if groups[0]["vlan"] is not None and groups[0]["vlan"] == groups[1]["vlan"]:
        errors.append("Los grupos deben usar VLAN distintas.")
    result = {"status": "invalid" if errors else "incomplete" if missing else "proposed",
              "missing": missing, "errors": errors, "groups": groups, "commands": "", "checks": [],
              "sources": [{"title": "Cisco Catalyst 2960 · VLAN · IOS 15.0(2)SE", "url": SOURCE}],
              "lab_verified": False}
    if missing or errors:
        return result
    lines = ["enable", "configure terminal"]
    checks = [{"command": "show version", "expected": "Confirmar el modelo del switch antes de aplicar cambios."},
              {"command": "show vlan brief", "expected": "Ambas VLAN activas, con los puertos de cada grupo."}]
    for group in groups:
        lines += [f"vlan {group['vlan']}", f"name {group['cli_name']}", "exit"]
        for port in group["ports"]:
            lines += [f"interface {port}", "switchport mode access", f"switchport access vlan {group['vlan']}", "no shutdown", "exit"]
            checks.append({"command": f"show interfaces {port} switchport", "expected": f"Administrative Mode: static access; Access Mode VLAN: {group['vlan']}."})
    lines.append("end")
    result.update(commands="\n".join(lines), checks=checks,
                  validations=["Campos obligatorios completos", "VLAN entre 2 y 1001 y distintas", "Sintaxis de puertos válida, sin duplicados ni conflictos"],
                  explanation="Se crean dos VLAN y se asigna cada interfaz en modo access. Los nombres CLI son ADMINISTRACION y LABORATORIO. no shutdown habilita los puertos seleccionados. No se configura enrutamiento entre grupos.",
                  limitations=["Referencia para un switch Cisco IOS y PC conectadas directamente. Confirma que las interfaces existen y que no son enlaces troncales o de administración.",
                               "La compatibilidad del equipo no se valida automáticamente. Revisa la guía y la CLI de Packet Tracer.",
                               "Usa un laboratorio aislado con VLAN y puertos disponibles; no se inspecciona la configuración previa ni VTP.",
                               "Las comprobaciones de código no prueban conectividad. Configura las IP de los PC y registra las pruebas indicadas."],
                  save_command="copy running-config startup-config")
    return result
