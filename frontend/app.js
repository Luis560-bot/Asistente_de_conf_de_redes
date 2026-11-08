"use strict";
const API_BASE = "http://localhost:8000";
const $ = (id) => document.getElementById(id);
let activeCase = null;
let savedCase = null;
let proposalSnapshot = null;
let diagnosisSnapshot = null;
let demoScenarios = [];
let history = [];
let supportContact = "Contacta al docente o técnico responsable del laboratorio.";
let busy = false;
const messagesElement = $("messages");
const inputElement = $("message-input");
const chatPanel = $("chat-panel");
const tabs = [...document.querySelectorAll('[role="tab"]')];

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, (character) => {
    const entities = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
    return entities[character];
  });
}

function renderMarkdown(text) {
  const bloquesCodigo = [];
  const conMarcadores = text.replace(/```([^\n`]*)\n?([\s\S]*?)```/g, (_, language, code) => {
    const index = bloquesCodigo.length;
    bloquesCodigo.push({ language: language.trim(), code: code.replace(/\n$/, "") });
    return `@@NETASSIST_CODE_${index}@@`;
  });
  const lineas = escapeHtml(conMarcadores).split(/\r?\n/);
  const resultado = [];
  let lista = null;

  const cerrarLista = () => {
    if (lista) {
      resultado.push(`</${lista}>`);
      lista = null;
    }
  };
  const inline = (line) =>
    line
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/`([^`]+)`/g, "<code>$1</code>");

  for (const linea of lineas) {
    const ulMatch = linea.match(/^\s*[-*]\s+(.+)$/);
    const olMatch = linea.match(/^\s*\d+[.)]\s+(.+)$/);
    if (ulMatch || olMatch) {
      const tipo = ulMatch ? "ul" : "ol";
      if (lista !== tipo) {
        cerrarLista();
        resultado.push(`<${tipo}>`);
        lista = tipo;
      }
      resultado.push(`<li>${inline((ulMatch || olMatch)[1])}</li>`);
      continue;
    }
    cerrarLista();
    if (!linea.trim()) continue;
    const marcador = linea.match(/^@@NETASSIST_CODE_(\d+)@@$/);
    if (marcador) {
      const bloque = bloquesCodigo[Number(marcador[1])];
      const codigoSeguro = escapeHtml(bloque.code);
      const idioma = bloque.language ? ` data-language="${escapeHtml(bloque.language)}"` : "";
      resultado.push(
        `<div class="code-block"${idioma}><button class="copy-button" type="button">Copiar</button><pre><code>${codigoSeguro}</code></pre></div>`
      );
    } else {
      resultado.push(`<p>${inline(linea)}</p>`);
    }
  }
  cerrarLista();
  return resultado.join("");
}


function appendMessage(role, content, persist = true) {
  const article = document.createElement("article");
  article.className = `message message-${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (role === "assistant") bubble.innerHTML = renderMarkdown(content);
  else { const p = document.createElement("p"); p.textContent = content; bubble.append(p); }
  const meta = document.createElement("span");
  meta.className = "message-meta";
  meta.textContent = role === "assistant" ? "Nexo · NetAssist" : "Tú";
  article.append(bubble, meta);
  messagesElement.append(article);
  messagesElement.scrollTop = messagesElement.scrollHeight;
  if (persist) history.push({role, content});
}
function welcome() {
  messagesElement.replaceChildren();
  const welcomeCard = document.createElement("article");
  welcomeCard.className = "nexo-welcome";
  welcomeCard.innerHTML = `<div class="nexo-welcome-art"><span class="nexo-orbit" aria-hidden="true"></span><img src="nexo.svg" alt="Nexo, un pequeño robot de redes que saluda" width="138" height="138"><span class="nexo-hello">¡Hola, colega!</span></div><p class="nexo-eyebrow">TU COMPAÑERO DE REDES</p><h3>¡Soy Nexo!</h3><p class="nexo-intro"></p><div class="nexo-prompts"><button type="button" data-nexo-prompt="¿Por dónde empiezo con esta práctica?">¿Por dónde empiezo? <span aria-hidden="true">↗</span></button><button type="button" data-nexo-prompt="Explícame por qué se usa modo access en los puertos de esta práctica.">Entender modo access <span aria-hidden="true">↗</span></button></div><p class="nexo-footnote">Tú haces la práctica. Yo te ayudo a entender cada paso.</p>`;
  welcomeCard.querySelector(".nexo-intro").textContent = activeCase
    ? `Ya tengo el contexto de «${activeCase.title}». Vamos paso a paso: podemos revisar tus VLAN, entender un comando o conversar sobre una salida.`
    : "Estoy aquí para ayudarte a entender tu red, un cable a la vez. Abre una práctica o cuéntame qué te gustaría aprender.";
  messagesElement.append(welcomeCard);
}

function openChat() {
  chatPanel.hidden = false;
  $("chat-launcher").hidden = true;
  $("chat-launcher").setAttribute("aria-expanded", "true");
  chatPanel.classList.remove("nexo-greeting");
  requestAnimationFrame(() => { if (!chatPanel.hidden) chatPanel.classList.add("nexo-greeting"); });
  inputElement.focus();
  if (history.length) messagesElement.scrollTop = messagesElement.scrollHeight;
  else messagesElement.scrollTop = 0;
}
function closeChat() {
  chatPanel.hidden = true;
  $("chat-launcher").hidden = false;
  $("chat-launcher").setAttribute("aria-expanded", "false");
  $("chat-launcher").focus();
}
$("chat-launcher").addEventListener("click", openChat);
$("minimize-chat").addEventListener("click", closeChat);
$("expand-chat").addEventListener("click", () => {
  const expanded = chatPanel.classList.toggle("expanded");
  $("expand-chat").setAttribute("aria-expanded", String(expanded));
  $("expand-chat").setAttribute("aria-label", expanded ? "Reducir chat" : "Ampliar chat");
});
chatPanel.addEventListener("keydown", (event) => { if (event.key === "Escape") closeChat(); });
$("ask-case-button").addEventListener("click", openChat);
$("new-chat-button").addEventListener("click", () => { if (!busy) { history = []; welcome(); inputElement.value = ""; inputElement.focus(); } });
function activateTab(tab, focus = false) {
  for (const item of tabs) {
    const selected = item === tab;
    item.setAttribute("aria-selected", String(selected));
    item.tabIndex = selected ? 0 : -1;
    $(item.getAttribute("aria-controls")).hidden = !selected;
  }
  if (focus) tab.focus();
}
tabs.forEach((tab, i) => {
  tab.addEventListener("click", () => activateTab(tab));
  tab.addEventListener("keydown", (event) => {
    let index;
    if (event.key === "ArrowRight") index = (i + 1) % tabs.length;
    if (event.key === "ArrowLeft") index = (i + tabs.length - 1) % tabs.length;
    if (event.key === "Home") index = 0;
    if (event.key === "End") index = tabs.length - 1;
    if (index !== undefined) { event.preventDefault(); activateTab(tabs[index], true); }
  });
});
function readCase() {
  const data = new FormData($("case-form"));
  const value = (key) => String(data.get(key) || "").trim();
  return {
    title: value("title"), model: value("model"), version: value("version"),
    connections: value("connections"), vendor: "Cisco IOS",
    groups: [
      {name: "Administración", vlan: value("adminVlan"), ports: value("adminPorts")},
      {name: "Laboratorio", vlan: value("labVlan"), ports: value("labPorts")}
    ], review_command: "", evidence: "", evidence_records: []
  };
}
function renderCase() {
  $("empty-case").hidden = true; $("case-content").hidden = false;
  $("case-heading").textContent = activeCase.title;
  $("chat-context").textContent = activeCase.title;
  $("launcher-context").textContent = activeCase.title;
  $("open-case-button").textContent = "Actualizar práctica ↗";
  const missing = [];
  if (!activeCase.model) missing.push("modelo del switch");
  if (!activeCase.version) missing.push("versión de IOS");
  for (const group of activeCase.groups) {
    if (!group.vlan) missing.push(`VLAN de ${group.name}`);
    if (!group.ports) missing.push(`puertos de ${group.name}`);
  }
  $("case-status").textContent = missing.length ? "Datos incompletos" : "Requisitos registrados";
  $("case-status").classList.add("open");
  const safe = escapeHtml;
  $("case-summary").className = "summary";
  $("case-summary").innerHTML = `<h3>Requisitos de la práctica</h3><dl><dt>Equipo</dt><dd>Cisco IOS · ${safe(activeCase.model || "Modelo pendiente")}</dd><dt>Versión</dt><dd>${safe(activeCase.version || "Pendiente de identificar")}</dd><dt>Conexiones</dt><dd>${safe(activeCase.connections || "Sin especificar")}</dd></dl><div class="group-summary">${activeCase.groups.map(g => `<div><h3>${safe(g.name)}</h3><p>VLAN ${safe(g.vlan || "pendiente")}</p><p>${safe(g.ports || "Puertos pendientes")}</p></div>`).join("")}</div>${missing.length ? `<p class="missing-list">Por completar: ${missing.map(safe).join(", ")}. Puedes registrar estos datos y consultar al asistente.</p>` : ""}`;
  for (const id of ["review-command", "evidence-input", "save-evidence-button", "diagnose-button"]) $(id).disabled = false;
  $("evidence-input").placeholder = "Pega aquí la salida que obtuviste en Packet Tracer…";
}
$("case-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (busy) return;
  const nextCase = readCase();
  if (!nextCase.title) { $("form-error").textContent = "Escribe un nombre para la práctica."; return; }
  $("form-error").textContent = "";
  // Una edición inicia una revisión del caso y descarta evidencia e historial antiguos.
  activeCase = nextCase; history = []; proposalSnapshot = null; diagnosisSnapshot = null;
  $("save-case").disabled = false;
  $("evidence-records").replaceChildren(); $("diagnosis-output").replaceChildren();
  $("proposal-output").replaceChildren(); $("proposal-checks").replaceChildren(); $("generation-status").textContent = "";
  $("review-command").value = ""; $("evidence-input").value = "";
  $("evidence-status").textContent = "No hay evidencia aportada.";
  renderCase(); welcome(); activateTab(tabs[0]);
  $("case-heading").setAttribute("tabindex", "-1"); $("case-heading").focus();
});
$("example-button").addEventListener("click", () => {
  const example = {"case-title":"Separar Administración y Laboratorio", "device-model":"Catalyst 2960", "ios-version":"", "admin-vlan":"10", "admin-ports":"Fa0/1, Fa0/2", "lab-vlan":"20", "lab-ports":"Fa0/3, Fa0/4", "connections":"Un switch con cuatro PC, dos por grupo. Confirmar el modelo y la versión en Packet Tracer."};
  for (const [id, value] of Object.entries(example)) $(id).value = value;
  $("case-title").focus();
});
$("save-evidence-button").addEventListener("click", () => {
  if (!activeCase || busy) return;
  const command = $("review-command").value.trim();
  const output = $("evidence-input").value.trim();
  if (!command || !output) { $("evidence-status").textContent = "Escribe el comando y pega su salida antes de incorporarlos."; return; }
  if (activeCase.evidence_records.length >= 12) { $("evidence-status").textContent = "Límite de 12 capturas por práctica. Retira una captura antes de añadir otra."; return; }
  activeCase.evidence_records.push({command, output});
  activeCase.review_command = command; activeCase.evidence = output;
  $("diagnosis-output").replaceChildren(); diagnosisSnapshot = null;
  renderEvidence();
  $("evidence-status").textContent = "Captura incorporada. Pulsa Analizar evidencia para actualizar el contraste.";
});
for (const id of ["review-command", "evidence-input"]) $(id).addEventListener("input", () => {
  $("evidence-status").textContent = "Hay cambios pendientes de incorporar al caso.";
});
function setBusy(value) {
  busy = value;
  for (const id of ["send-button", "new-chat-button", "open-case-button", "example-button", "generate-button", "diagnose-button"]) $(id).disabled = value;
  if (activeCase) $("save-evidence-button").disabled = value;
  for (const id of ["refresh-cases", "load-case", "new-case"]) $(id).disabled = value;
  $("save-case").disabled = value || !activeCase;
  for (const id of ["export-html", "export-json"]) $(id).disabled = value || !savedCase;
  $("load-demo").disabled = value || !demoScenarios.length;
  $("typing-indicator").hidden = !value;
}
$("chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const content = inputElement.value.trim();
  if (!content || busy) return;
  appendMessage("user", content); inputElement.value = ""; setBusy(true);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 45000);
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST", headers: {"Content-Type":"application/json"}, signal: controller.signal,
      body: JSON.stringify({messages: history.slice(-40), context: activeCase})
    });
    const data = await response.json();
    if (!response.ok || typeof data.reply !== "string" || !data.reply.trim()) throw new Error("Respuesta no disponible");
    if (typeof data.contact === "string" && data.contact.trim()) supportContact = data.contact;
    appendMessage("assistant", data.reply);
  } catch {
    appendMessage("assistant", `No pude obtener una respuesta. Puedes volver a intentarlo; tu práctica sigue abierta. Contacto: ${supportContact}`, false);
  } finally {
    clearTimeout(timer); setBusy(false);
    if (!chatPanel.hidden) inputElement.focus();
  }
});
document.addEventListener("click", async (event) => {
  const button = event.target.closest(".copy-button");
  if (!button) return;
  try {
    await navigator.clipboard.writeText(button.parentElement.querySelector("code").textContent);
    button.textContent = "Copiado";
  } catch { button.textContent = "Selecciona el texto"; }
  setTimeout(() => button.textContent = "Copiar", 1800);
});
async function loadService() {
  const status = $("service-status");
  try {
    const response = await fetch(`${API_BASE}/health`, {signal: AbortSignal.timeout(5000)});
    if (!response.ok) throw new Error();
    const data = await response.json();
    status.textContent = data.rag_ready ? "Servicio conectado" : "Manuales no disponibles";
    status.classList.toggle("online", Boolean(data.rag_ready));
    status.classList.toggle("offline", !data.rag_ready);
  } catch { status.textContent = "Servicio sin conexión"; status.classList.add("offline"); }
  try {
    const response = await fetch(`${API_BASE}/contacto`, {signal: AbortSignal.timeout(5000)});
    if (!response.ok) return;
    const data = await response.json();
    if (typeof data.contact === "string" && data.contact.trim()) supportContact = data.contact;
  } catch { /* Se conserva el contacto de ayuda local. */ }
}
$("contact-button").addEventListener("click", () => { $("contact-details").textContent = supportContact; $("contact-dialog").showModal(); });
for (const id of ["close-contact-button", "dialog-ok-button"]) $(id).addEventListener("click", () => $("contact-dialog").close());
$("service-status").addEventListener("click", loadService);
welcome(); loadService();

$("generate-button").addEventListener("click", async () => {
  if (!activeCase || busy) return;
  setBusy(true);
  $("generation-status").textContent = "Comprobando requisitos…";
  try {
    const response = await fetch(`${API_BASE}/generar`, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(activeCase), signal: AbortSignal.timeout(15000)
    });
    if (!response.ok) throw new Error();
    const proposal = await response.json();
    proposalSnapshot = proposal;
    renderProposal(proposal);
  } catch {
    $("generation-status").textContent = "No se pudo generar la propuesta. Revisa la conexión y vuelve a intentarlo.";
  } finally { setBusy(false); }
});

function renderEvidence() {
  $("evidence-records").innerHTML = `<h3>Pasos registrados (${activeCase.evidence_records.length}/12)</h3>` + activeCase.evidence_records.map((r, i) => `<details><summary>Captura ${i + 1}: ${escapeHtml(r.command)}</summary><pre>${escapeHtml(r.output)}</pre><button class="button secondary" type="button" data-remove-evidence="${i}">Retirar captura ${i + 1}</button></details>`).join("");
}
$("evidence-records").addEventListener("click", event => {
  const button = event.target.closest("[data-remove-evidence]");
  if (!button || busy || !activeCase) return;
  activeCase.evidence_records.splice(Number(button.dataset.removeEvidence), 1);
  const last = activeCase.evidence_records.at(-1);
  activeCase.review_command = last?.command || ""; activeCase.evidence = last?.output || "";
  $("diagnosis-output").replaceChildren(); diagnosisSnapshot = null; renderEvidence();
  $("evidence-status").textContent = "Captura retirada. Vuelve a analizar las restantes.";
});
$("diagnose-button").addEventListener("click", async () => {
  if (!activeCase || busy) return;
  setBusy(true);
  $("evidence-status").textContent = "Contrastando capturas…";
  try {
    const response = await fetch(`${API_BASE}/diagnosticar`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(activeCase), signal: AbortSignal.timeout(15000)});
    if (!response.ok) throw new Error();
    const data = await response.json();
    diagnosisSnapshot = data;
    renderDiagnosis(data);
  } catch { $("evidence-status").textContent = "No se pudo analizar la evidencia. Las capturas siguen en el caso; vuelve a intentarlo."; }
  finally { setBusy(false); }
});

function renderProposal(proposal) {
    const safe = escapeHtml;
    $("proposal-output").replaceChildren(); $("proposal-checks").replaceChildren();
    if (proposal.status !== "proposed") {
      $("case-status").textContent = proposal.errors.length ? "Requisitos por corregir" : "Datos incompletos";
      $("generation-status").textContent = [...proposal.missing.map(x => `Falta: ${x}.`), ...proposal.errors].join(" ");
      return;
    }
    $("case-status").textContent = "Propuesta generada";
    $("generation-status").textContent = "Comprobaciones de código superadas. Prueba en laboratorio pendiente.";
    $("proposal-output").innerHTML = `<h3>Configuración de referencia · un switch</h3><p>${safe(proposal.explanation)}</p>${renderMarkdown("```ios\n" + proposal.commands + "\n```")}<h3>Reglas comprobadas por código</h3><ul>${proposal.validations.map(x => `<li>${safe(x)}</li>`).join("")}</ul><h3>Antes de aplicar</h3><ul>${proposal.limitations.map(x => `<li>${safe(x)}</li>`).join("")}</ul><p>Después de revisar los resultados, guarda manualmente con <code>${safe(proposal.save_command)}</code>.</p><p>Fuente de la plantilla: <a href="${safe(proposal.sources[0].url)}" target="_blank" rel="noopener noreferrer">${safe(proposal.sources[0].title)}</a>. Comprueba su correspondencia con tu equipo.</p>`;
    $("proposal-checks").innerHTML = `<h3>Plan de comprobación · pendiente de ejecutar</h3><ul>${proposal.checks.map(x => `<li><code>${safe(x.command)}</code><p>${safe(x.expected)}</p></li>`).join("")}</ul><p>En los PC configura direcciones de una misma subred para cada grupo y subredes distintas entre grupos. Registra IP, máscara, origen, destino y resultado de ping: dentro de cada VLAN debe responder; entre VLAN no habrá comunicación sin enrutamiento. Un ping fallido por sí solo no demuestra aislamiento por VLAN.</p>`;
}

function renderDiagnosis(data) {
    const safe = escapeHtml;
    const labels = {compared: "Evidencia contrastada", discrepancies: "Discrepancias en la evidencia", insufficient: "Evidencia insuficiente"};
    $("diagnosis-output").innerHTML = `<h3>${labels[data.status]}</h3><p>${safe(data.limits)}</p>${data.requirements?.length ? `<p>Completa o corrige los requisitos: ${data.requirements.map(safe).join("; ")}</p>` : ""}<h3>Hallazgos</h3>${data.findings.length ? data.findings.map(f => `<article class="notice"><strong>${f.status === "match" ? "Coincide" : "Discrepancia"}: ${safe(f.label)}</strong><p>Observado: ${safe(f.actual)}. Esperado: ${safe(f.expected)}.</p><p>Captura ${f.record}:</p><pre>${safe(f.evidence)}</pre><p>Siguiente paso: ${safe(f.next_step)}</p></article>`).join("") : "<p>No hay campos suficientes para sostener un hallazgo.</p>"}<h3>Pasos revisados</h3><ul>${data.steps.map(s => `<li>Captura ${s.record} · ${safe(s.command)}: ${safe(s.note)}</li>`).join("")}</ul><h3>Próximas comprobaciones</h3><ul>${data.next_steps.map(s => `<li><code>${safe(s.command)}</code> ${safe(s.reason)}</li>`).join("")}</ul>`;
    $("evidence-status").textContent = "Contraste actualizado. No se han ejecutado comandos ni verificado la red.";
}

async function storageRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {...options, signal: AbortSignal.timeout(15000)}).catch(() => { throw new Error("No se pudo conectar con el almacenamiento. Revisa el servicio y vuelve a intentarlo."); });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(typeof data.detail === "string" ? data.detail : "No se pudo completar la operación. Revisa la conexión y vuelve a intentarlo.");
  }
  return response;
}
async function refreshCases() {
  const rows = await (await storageRequest("/casos")).json();
  $("saved-cases").replaceChildren(new Option("Selecciona una práctica", ""));
  for (const row of rows) $("saved-cases").add(new Option(`${row.title} · revisión ${row.revision}`, row.id));
  if (savedCase) $("saved-cases").value = savedCase.id;
  return rows;
}
$("refresh-cases").addEventListener("click", async () => {
  if (busy) return; setBusy(true);
  try { const rows = await refreshCases(); $("storage-status").textContent = `${rows.length} prácticas disponibles (se muestran las 100 más recientes).`; }
  catch (error) { $("storage-status").textContent = error.message; }
  finally { setBusy(false); }
});
$("save-case").addEventListener("click", async () => {
  if (!activeCase || busy) return; setBusy(true);
  try {
    const payload = {case: activeCase, messages: history.slice(-60), proposal_requested: proposalSnapshot !== null, diagnosis_requested: diagnosisSnapshot !== null, revision: savedCase?.revision || null};
    const response = await storageRequest(savedCase ? `/casos/${savedCase.id}` : "/casos", {method: savedCase ? "PUT" : "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
    savedCase = await response.json();
    $("storage-status").textContent = `Práctica guardada · revisión ${savedCase.revision}. Puedes reabrirla después de recargar. Solo se guardan los datos aplicados al caso.`;
    try { await refreshCases(); } catch { $("storage-status").textContent += " No se pudo actualizar la lista."; }
  } catch (error) { $("storage-status").textContent = error.message; }
  finally { setBusy(false); }
});
$("load-case").addEventListener("click", async () => {
  const id = $("saved-cases").value;
  if (!id || busy) return;
  if (activeCase && !confirm("Abrir otra práctica reemplaza el trabajo de esta pestaña que no hayas guardado. ¿Continuar?")) return;
  setBusy(true);
  try {
    const loaded = await (await storageRequest(`/casos/${id}`)).json();
    const doc = loaded.document;
    savedCase = loaded; activeCase = doc.case; history = doc.messages;
    proposalSnapshot = doc.proposal; diagnosisSnapshot = doc.diagnosis;
    const fields = {"case-title": activeCase.title, "device-model": activeCase.model, "ios-version": activeCase.version, "connections": activeCase.connections, "admin-vlan": activeCase.groups[0].vlan, "admin-ports": activeCase.groups[0].ports, "lab-vlan": activeCase.groups[1].vlan, "lab-ports": activeCase.groups[1].ports};
    for (const [id, value] of Object.entries(fields)) $(id).value = value;
    $("review-command").value = activeCase.review_command; $("evidence-input").value = activeCase.evidence;
    $("proposal-output").replaceChildren(); $("proposal-checks").replaceChildren(); $("generation-status").textContent = ""; $("diagnosis-output").replaceChildren();
    renderCase(); renderEvidence(); welcome();
    for (const message of history) appendMessage(message.role, message.content, false);
    if (proposalSnapshot) renderProposal(proposalSnapshot);
    if (diagnosisSnapshot) renderDiagnosis(diagnosisSnapshot);
    else $("evidence-status").textContent = "Capturas recuperadas; puedes analizarlas.";
    activateTab(tabs[0]);
    $("storage-status").textContent = `Práctica recuperada · revisión ${savedCase.revision}. Los resultados corresponden a esa revisión guardada.`;
  } catch (error) { $("storage-status").textContent = error.message; }
  finally { setBusy(false); }
});
$("new-case").addEventListener("click", () => {
  if (busy || (activeCase && !confirm("Iniciar otra práctica descarta los cambios de esta pestaña que no hayas guardado. ¿Continuar?"))) return;
  activeCase = null; savedCase = null; history = []; proposalSnapshot = null; diagnosisSnapshot = null;
  $("case-form").reset(); $("case-content").hidden = true; $("empty-case").hidden = false;
  $("case-heading").textContent = "Un espacio para construir"; $("case-status").textContent = "Sin práctica abierta";
  $("open-case-button").textContent = "Abrir práctica ↗";
  $("chat-context").textContent = "Sin práctica abierta"; $("launcher-context").textContent = "¿Vemos tu red juntos?";
  for (const id of ["proposal-checks", "diagnosis-output", "evidence-records"]) $(id).replaceChildren();
  for (const id of ["review-command", "evidence-input"]) { $(id).value = ""; $(id).disabled = true; }
  $("save-evidence-button").disabled = true; $("evidence-status").textContent = "No hay evidencia aportada.";
  $("storage-status").textContent = "Nueva práctica. Completa el formulario para abrirla.";
  welcome(); setBusy(false); $("diagnose-button").disabled = true; activateTab(tabs[0]);
});
for (const format of ["html", "json"]) $(`export-${format}`).addEventListener("click", async () => {
  if (!savedCase || busy) return; setBusy(true);
  try {
    const response = await storageRequest(`/casos/${savedCase.id}/informe?formato=${format}&revision=${savedCase.revision}`);
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement("a"); link.href = url; link.download = `netassist-${savedCase.id}.${format}`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    $("storage-status").textContent = `Informe de la revisión guardada ${savedCase.revision} descargado. Guarda primero si quieres incluir cambios posteriores.`;
  } catch (error) { $("storage-status").textContent = error.message; }
  finally { setBusy(false); }
});
refreshCases().then(rows => { $("storage-status").textContent = `${rows.length} prácticas guardadas. Guarda explícitamente los cambios que quieras conservar.`; }).catch(error => { $("storage-status").textContent = error.message; });

async function loadDemoScenarios() {
  try {
    const response = await fetch("demo-cases.json", {signal: AbortSignal.timeout(5000)});
    if (!response.ok) throw new Error();
    const data = await response.json(); demoScenarios = data.scenarios;
    $("demo-scenario").replaceChildren(...demoScenarios.map(item => new Option(item.label, item.id)));
    $("demo-scenario").disabled = false; $("load-demo").disabled = busy;
    $("demo-status").textContent = "Selecciona un escenario y cárgalo. No se guarda automáticamente.";
  } catch { $("demo-status").textContent = "No se pudieron cargar los escenarios. Recarga para volver a intentarlo."; }
}
$("load-demo").addEventListener("click", () => {
  if (busy) return;
  const scenario = demoScenarios.find(item => item.id === $("demo-scenario").value);
  if (!scenario) return;
  if (activeCase && !confirm("Cargar el ejemplo reemplaza el caso de esta pestaña. Guarda tus cambios antes de continuar. ¿Continuar?")) return;
  const data = scenario.case;
  const values = {"case-title":data.title, "device-model":data.model, "ios-version":data.version, "connections":data.connections, "admin-vlan":data.groups[0].vlan, "admin-ports":data.groups[0].ports, "lab-vlan":data.groups[1].vlan, "lab-ports":data.groups[1].ports};
  for (const [id, value] of Object.entries(values)) $(id).value = value;
  savedCase = null;
  $("case-form").requestSubmit();
  activeCase.evidence_records = structuredClone(data.evidence_records);
  const last = activeCase.evidence_records.at(-1);
  activeCase.review_command = last?.command || ""; activeCase.evidence = last?.output || "";
  $("review-command").value = activeCase.review_command; $("evidence-input").value = activeCase.evidence;
  renderEvidence();
  for (const id of ["export-html", "export-json"]) $(id).disabled = true;
  $("evidence-status").textContent = "Capturas sintéticas cargadas. Pulsa Analizar evidencia para contrastarlas.";
  $("storage-status").textContent = "Escenario de demostración abierto como práctica nueva, sin guardar.";
  $("demo-status").textContent = `Datos sintéticos: ${scenario.description} Continúa con Generar configuración y Analizar evidencia.`;
});
loadDemoScenarios();

messagesElement.addEventListener("click", event => {
  const button = event.target.closest("[data-nexo-prompt]");
  if (!button || busy) return;
  inputElement.value = button.dataset.nexoPrompt;
  inputElement.focus();
});
