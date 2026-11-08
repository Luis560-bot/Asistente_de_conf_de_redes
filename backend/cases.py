"""SQLite exclusivo de NetAssist. No admite destinos configurables externos."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from uuid import uuid4

APP_ID = 0x4E415343


class CaseStore:
    def __init__(self, project_root: Path):
        self.root = project_root.resolve()
        self.directory = self.root / ".data" / "netassist"
        self.path = self.directory / "cases.sqlite3"
        self.lock = RLock()

    def checked_path(self):
        # Verificar también padres existentes antes de crear carpetas o abrir SQLite.
        for path in [self.root / ".data", self.directory, self.path,
                     *[Path(str(self.path) + suffix) for suffix in ["-journal", "-wal", "-shm"]]]:
            if path.resolve() != path:
                raise RuntimeError("El almacenamiento de casos tiene una redirección no permitida.")
            if path.exists() and path.is_file() and path.stat().st_nlink > 1:
                raise RuntimeError("El archivo de casos no puede compartirse mediante enlaces físicos.")
        return self.path

    @contextmanager
    def connection(self):
        with self.lock:
            with self._connection() as conn:
                yield conn

    @contextmanager
    def _connection(self):
        path = self.checked_path()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.checked_path()
        # Crear exclusivamente; una base existente se abre en rw, nunca se reemplaza.
        try:
            with path.open("xb"):
                pass
            new = True
        except FileExistsError:
            new = False
        conn = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            app_id = conn.execute("PRAGMA application_id").fetchone()[0]
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if not new and (app_id != APP_ID or version != 1):
                raise RuntimeError("Archivo ajeno o versión de casos no admitida; no se modificó.")
            if new:
                with conn:
                    conn.execute("CREATE TABLE cases (id TEXT PRIMARY KEY, title TEXT NOT NULL, revision INTEGER NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, payload TEXT NOT NULL)")
                    conn.execute(f"PRAGMA application_id={APP_ID}")
                    conn.execute("PRAGMA user_version=1")
            yield conn
        finally:
            conn.close()

    def list(self):
        with self.connection() as conn:
            return [dict(row) for row in conn.execute("SELECT id,title,revision,created_at,updated_at FROM cases ORDER BY updated_at DESC LIMIT 100")]

    def get(self, case_id):
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
            if row is None:
                raise KeyError(case_id)
            result = dict(row)
            result["document"] = json.loads(result.pop("payload"))
            return result

    def save(self, document, case_id=None, revision=None):
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(document, ensure_ascii=False)
        with self.connection() as conn, conn:
            if case_id is None:
                case_id = str(uuid4())
                conn.execute("INSERT INTO cases VALUES (?,?,?,?,?,?)", (case_id, document["case"]["title"], 1, timestamp, timestamp, payload))
            else:
                cursor = conn.execute("UPDATE cases SET title=?,revision=revision+1,updated_at=?,payload=? WHERE id=? AND revision=?", (document["case"]["title"], timestamp, payload, case_id, revision))
                if cursor.rowcount != 1:
                    if conn.execute("SELECT 1 FROM cases WHERE id=?", (case_id,)).fetchone() is None:
                        raise KeyError(case_id)
                    raise ValueError("El caso cambió en otra pestaña. Reábrelo antes de guardar.")
            saved = dict(conn.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone())
            saved["document"] = json.loads(saved.pop("payload"))
        return saved


def html_report(saved):
    """Informe portátil sin scripts; escapa también las salidas y el chat."""
    from html import escape
    doc = saved["document"]
    title = escape(saved["title"])
    def safe(value):
        return escape(str(value))

    case = doc["case"]
    sections = [f"<h2>Requisitos</h2><p>Cisco IOS · {safe(case['model'])} · {safe(case['version'])}</p><p>{safe(case['connections'])}</p>",
                "<table><tr><th>Grupo</th><th>VLAN</th><th>Puertos</th></tr>" + "".join(
                    f"<tr><td>{safe(g['name'])}</td><td>{safe(g['vlan'])}</td><td>{safe(g['ports'])}</td></tr>" for g in case["groups"]) + "</table>"]
    proposal = doc["proposal"]
    sections.append("<h2>Propuesta de referencia</h2>")
    if proposal is None:
        sections.append("<p>No solicitada al guardar esta versión.</p>")
    else:
        sections.append(f"<p>Estado: {safe(proposal['status'])}. Pendiente de validación real en laboratorio.</p>")
        sections.append("<ul>" + "".join(f"<li>{safe(item)}</li>" for item in proposal.get("missing", []) + proposal.get("errors", []) + proposal.get("validations", [])) + "</ul>")
        sections.append(f"<p>{safe(proposal.get('explanation', ''))}</p><pre>{safe(proposal['commands'])}</pre>")
        sections.append("<ul>" + "".join(f"<li>{safe(item)}</li>" for item in proposal.get("limitations", [])) + "</ul>")
        sections.append("<h3>Comprobaciones propuestas</h3><ul>" + "".join(f"<li><code>{safe(c['command'])}</code>: {safe(c['expected'])}</li>" for c in proposal["checks"]) + "</ul>")
        sections.append("<h3>Fuentes de la plantilla</h3><ul>" + "".join(f"<li>{safe(s['title'])}: {safe(s['url'])}</li>" for s in proposal["sources"]) + "</ul>")
    sections.append("<h2>Evidencia aportada</h2>")
    records = case["evidence_records"] or ([{"command": case["review_command"], "output": case["evidence"]}] if case["evidence"] else [])
    for i, record in enumerate(records, 1):
        sections.append(f"<h3>Captura {i} · {safe(record['command'])}</h3><pre>{safe(record['output'])}</pre>")
    if not records:
        sections.append("<p>Sin capturas incorporadas.</p>")
    sections.append("<h2>Contraste de evidencia</h2>")
    diagnosis = doc["diagnosis"]
    if diagnosis is None:
        sections.append("<p>No solicitado al guardar esta versión.</p>")
    else:
        sections.append(f"<p>Estado: {safe(diagnosis['status'])}. {safe(diagnosis['limits'])}</p>")
        for finding in diagnosis["findings"]:
            sections.append(f"<h3>{safe(finding['label'])} · {safe(finding['status'])}</h3><p>Observado: {safe(finding['actual'])}. Esperado: {safe(finding['expected'])}. Captura {finding['record']}.</p><pre>{safe(finding['evidence'])}</pre><p>{safe(finding['next_step'])}</p>")
        sections.append("<h3>Pasos registrados</h3><ul>" + "".join(f"<li>Captura {s['record']} · {safe(s['command'])}: {safe(s['note'])}</li>" for s in diagnosis["steps"]) + "</ul>")
        sections.append("<h3>Próximas comprobaciones</h3><ul>" + "".join(f"<li>{safe(s['command'])}: {safe(s['reason'])}</li>" for s in diagnosis["next_steps"]) + "</ul>")
    sections.append("<h2>Conversación registrada</h2>" + "".join(f"<p><strong>{safe(m['role'])}</strong></p><pre>{safe(m['content'])}</pre>" for m in doc["messages"]))
    return ("<!doctype html><html lang='es'><meta charset='utf-8'>"
            f"<title>NetAssist · {title}</title><style>body{{font:16px system-ui;max-width:960px;margin:40px auto;padding:0 20px;color:#162c36}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f5f7;padding:16px}}h2{{margin-top:32px}}</style>"
            f"<h1>{title}</h1><p>NetAssist · revisión {saved['revision']} · {escape(saved['updated_at'])}</p>"
            "<p><strong>Una propuesta y un contraste de capturas no prueban el funcionamiento de la red.</strong> "
            "No se han ejecutado comandos desde NetAssist. Las salidas fueron aportadas por el usuario; la aceptación real en laboratorio no se da por supuesta.</p>"
            + "".join(sections) + "</html>")
