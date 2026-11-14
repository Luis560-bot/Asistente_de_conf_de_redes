"""Contraste conservador de salidas aportadas; nunca ejecuta comandos."""
import re
from .generator import generate, parse_ports, SOURCE


def command_key(command):
    command = " ".join(command.strip().lower().split())
    if command == "show vlan brief":
        return command
    match = re.fullmatch(r"show interfaces (\S+) switchport", command)
    if match:
        try:
            ports = parse_ports(match[1])
            if len(ports) == 1:
                return f"show interfaces {ports[0]} switchport"
        except ValueError:
            pass
    return None


def diagnose(case):
    proposal = generate(case)
    result = {"status": "insufficient", "findings": [], "steps": [], "next_steps": [],
              "lab_verified": False, "source": SOURCE,
              "limits": "Solo se contrastan filas y campos reconocidos de salidas pegadas. No se verifica su autenticidad, conectividad, cableado ni configuración actual del equipo."}
    if proposal["status"] != "proposed":
        result["requirements"] = proposal["missing"] + proposal["errors"]
        return result
    records = list(getattr(case, "evidence_records", []))
    # Compatibilidad con el campo único anterior; no duplicarlo si ya está registrado.
    if not records and case.evidence.strip():
        from types import SimpleNamespace
        records = [SimpleNamespace(command=case.review_command, output=case.evidence)]
    expected_ports = {p: g["vlan"] for g in proposal["groups"] for p in g["ports"]}
    latest = {}
    for index, record in enumerate(records):
        key = command_key(record.command)
        step = {"record": index + 1, "command": record.command, "recognized": False,
                "note": "Comando no admitido; conservado sin contraste automático."}
        result["steps"].append(step)
        if key:
            if key in latest:
                latest[key][2]["note"] = "Captura anterior conservada; sustituida para el contraste por otra más reciente del mismo comando."
            latest[key] = (index + 1, record.output, step)

    def finding(record, label, actual, expected, excerpt, matches, action):
        result["findings"].append(dict(record=record, label=label, actual=actual,
            expected=expected, evidence=excerpt, status="match" if matches else "mismatch", next_step=action))

    for key, (record, output, step) in latest.items():
        step["note"] = "Salida no reconocida, incompleta o con error; aporta una captura completa de este comando."
        # Errores y paginación impiden tratar una captura como comprobación realizada.
        if re.search(r"--More--|%\s*(?:Invalid|Error|Incomplete|Ambiguous)", output, re.I):
            continue
        if key == "show vlan brief":
            if not re.search(r"VLAN\s+Name\s+Status\s+Ports", output, re.I):
                continue
            rows, current = {}, None
            malformed = False
            for line in output.splitlines():
                match = re.fullmatch(r"\s*(\d+)\s+(\S+)\s+(active|suspended|act/unsup|act/lshut|sus/lshut)\s*(.*?)\s*", line, re.I)
                if match:
                    vlan = int(match[1])
                    if vlan in rows:
                        malformed = True
                    rows[vlan] = {"status": match[3].lower(), "ports": [], "lines": [line]}
                    current = rows[vlan]
                    tail = match[4]
                elif current is not None and re.match(r"\s+(?:Fa|Gi|FastEthernet|GigabitEthernet)\d", line, re.I):
                    tail = line.strip()
                    current["lines"].append(line)
                else:
                    current = None
                    continue
                if tail:
                    try:
                        current["ports"].extend(parse_ports(tail.rstrip(",").strip()))
                    except ValueError:
                        malformed = True
            if not rows or malformed:
                continue
            step["recognized"] = True
            step["note"] = "Filas presentes contrastadas; la ausencia de una fila o puerto no demuestra un fallo."
            for group in proposal["groups"]:
                row = rows.get(group["vlan"])
                if row:
                    matches = row["status"] == "active"
                    finding(record, f"Estado VLAN {group['vlan']}", row["status"], "active", "\n".join(row["lines"]), matches,
                            "Contrastar los puertos con show interfaces <puerto> switchport." if matches else "Revisar el estado de esta VLAN en el switch antes de repetir la captura.")
            for vlan, row in rows.items():
                for port in row["ports"]:
                    if port in expected_ports:
                        matches = vlan == expected_ports[port]
                        finding(record, f"Asignación {port}", str(vlan), str(expected_ports[port]), "\n".join(row["lines"]), matches,
                                f"Contrastar modo y VLAN con show interfaces {port} switchport." if matches else "Revisar la asignación de este puerto; después de corregirla, registrar una captura nueva.")
        else:
            port = key.split()[2]
            fields = {}
            for name in ["Name", "Switchport", "Administrative Mode", "Access Mode VLAN"]:
                matches = list(re.finditer(r"^\s*" + re.escape(name) + r":\s*([^\r\n]+)", output, re.M | re.I))
                if len(matches) == 1:
                    fields[name] = (matches[0][1].strip(), matches[0][0].strip())
            if len(fields) != 4 or port not in expected_ports:
                continue
            try:
                if parse_ports(fields["Name"][0]) != [port]:
                    continue
            except ValueError:
                continue
            vlan_match = re.fullmatch(r"(\d+)(?:\s+\([^\r\n]*\))?", fields["Access Mode VLAN"][0])
            if not vlan_match:
                continue
            step["recognized"] = True
            step["note"] = "Campos administrativos contrastados; no demuestra enlace operativo ni conectividad."
            for field, expected, matches in [
                ("Switchport", "Enabled", fields["Switchport"][0].lower() == "enabled"),
                ("Administrative Mode", "static access", fields["Administrative Mode"][0].lower() == "static access"),
                ("Access Mode VLAN", str(expected_ports[port]), int(vlan_match[1]) == expected_ports[port])]:
                finding(record, f"{port} · {field}", fields[field][0], expected, fields[field][1], matches,
                        "Completar las comprobaciones pendientes; después revisar IP y conectividad de los PC." if matches else "Revisar este campo en la configuración; tras corregirlo, registrar una nueva salida del puerto.")
    completed = {key for key, (_, _, step) in latest.items() if step["recognized"]}
    for item in result["findings"]:
        if item["status"] == "match":
            item["next_step"] = "Este campo coincide en la captura. Continúa con las próximas comprobaciones pendientes."
    for check in proposal["checks"]:
        key = command_key(check["command"])
        if key and key not in completed:
            result["next_steps"].append({"command": check["command"], "reason": "Aporta una salida completa para contrastar este paso."})
    if not result["next_steps"]:
        result["next_steps"].append({"command": "", "reason": "Las capturas admitidas ya se revisaron. Atiende las discrepancias indicadas; si no hay, registra IP, máscara y resultados de ping dentro de cada VLAN. El contraste de ping es manual."})
    if result["findings"]:
        result["status"] = "discrepancies" if any(f["status"] == "mismatch" for f in result["findings"]) else "compared"
    return result
