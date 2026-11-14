"use strict";
const API_BASE = window.location.port === "8000" ? window.location.origin : "http://localhost:8000";
const $ = (id) => document.getElementById(id);
let activeCase = null;
let savedCase = null;
let proposalSnapshot = null;
let diagnosisSnapshot = null;
let history = [];
let supportContact = "Contacta al docente o técnico responsable del laboratorio.";
let busy = false;
let topologyUrls = [];
let pendingImage = null;
let imageReading = false;
let imageReadVersion = 0;
let chatImagesSupported = false;
const IMAGE_TYPES = ["image/png", "image/jpeg", "image/webp"];
const MAX_IMAGE_BYTES = 3 * 1024 * 1024;
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


function imageSource(image) {
  return image && IMAGE_TYPES.includes(image.mime_type) && typeof image.data === "string"
    && image.data.length <= 4 * MAX_IMAGE_BYTES / 3 && /^[A-Za-z0-9+/]+={0,2}$/.test(image.data)
    ? `data:${image.mime_type};base64,${image.data}` : "";
}
function imageStatus(message = "") {
  $("image-status").textContent = message; $("image-status").hidden = !message;
}
function renderPendingImage() {
  $("image-preview").hidden = !pendingImage;
  if (pendingImage) {
    $("pending-image").src = imageSource(pendingImage);
    $("image-name").textContent = pendingImage.name;
  } else {
    $("pending-image").removeAttribute("src"); $("image-name").textContent = "";
  }
}
function clearPendingImage() {
  imageReadVersion++; imageReading = false; pendingImage = null;
  $("chat-image").value = ""; renderPendingImage(); imageStatus();
}
async function attachImage(file) {
  if (busy || imageReading || !file) return;
  if (!IMAGE_TYPES.includes(file.type)) { imageStatus("Usa una captura PNG, JPG o WebP."); return; }
  if (!file.size || file.size > MAX_IMAGE_BYTES) { imageStatus("La captura debe pesar como máximo 3 MB."); return; }
  if (history.filter(message => message.image).length >= 3) {
    imageStatus("Ya hay 3 capturas en esta conversación. Limpia el chat para adjuntar otra."); return;
  }
  const version = ++imageReadVersion; imageReading = true; imageStatus("Preparando captura…");
  try {
    const source = await new Promise((resolve, reject) => {
      const reader = new FileReader(); reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error("No se pudo leer la captura.")); reader.readAsDataURL(file);
    });
    const image = new Image(); image.src = source; await image.decode();
    if (image.naturalWidth * image.naturalHeight > 16_777_216 || Math.max(image.naturalWidth, image.naturalHeight) > 8192) {
      throw new Error("Recorta la captura: el máximo es 16 megapíxeles.");
    }
    if (version !== imageReadVersion) return;
    pendingImage = {mime_type: file.type, name: (file.name || "captura.png").slice(0, 120), data: source.slice(source.indexOf(",") + 1)};
    renderPendingImage(); imageStatus(); inputElement.focus();
  } catch (error) {
    if (version === imageReadVersion) imageStatus(error.message || "La captura no es una imagen válida.");
  } finally { if (version === imageReadVersion) imageReading = false; }
}
$("attach-image").addEventListener("click", () => { if (!busy) $("chat-image").click(); });
$("chat-image").addEventListener("change", event => { attachImage(event.target.files[0]); event.target.value = ""; });
$("remove-image").addEventListener("click", () => { if (!busy) clearPendingImage(); });
chatPanel.addEventListener("paste", event => {
  const item = [...(event.clipboardData?.items || [])].find(item => item.type.startsWith("image/"));
  if (item) { event.preventDefault(); attachImage(item.getAsFile()); }
});

function appendMessage(role, content, persist = true, topology = null, svg = null, suggestions = [], image = null) {
  messagesElement.querySelectorAll(".chat-suggestions").forEach(item => item.remove());
  const article = document.createElement("article");
  article.className = `message message-${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (role === "assistant") bubble.innerHTML = renderMarkdown(content);
  else { const p = document.createElement("p"); p.textContent = content; bubble.append(p); }
  if (role === "user" && imageSource(image)) {
    const preview = document.createElement("img"); preview.className = "chat-image";
    preview.src = imageSource(image); preview.alt = image.name || "Captura enviada";
    bubble.append(preview);
  }
  const meta = document.createElement("span");
  meta.className = "message-meta";
  meta.textContent = role === "assistant" ? "Nexo · NetAssist" : "Tú";
  article.append(bubble, meta);
  messagesElement.append(article);
  if (role === "assistant" && topology) appendTopology(bubble, topology, svg);
  messagesElement.scrollTop = messagesElement.scrollHeight;
  if (role === "assistant" && suggestions.length) {
    const actions = document.createElement("div"); actions.className = "chat-suggestions";
    for (const question of suggestions.slice(0, 1)) {
      const button = document.createElement("button"); button.type = "button";
      button.textContent = question; button.dataset.nexoPrompt = question;
      actions.append(button);
    }
    bubble.append(actions);
    messagesElement.scrollTop = messagesElement.scrollHeight;
  }
  if (persist) history.push({role, content, ...(topology ? {topology} : {}), ...(suggestions.length ? {suggestions} : {}), ...(image ? {image} : {})});
}
async function appendTopology(bubble, topology, svg) {
  const figure = document.createElement("figure"); figure.className = "topology-figure";
  const status = document.createElement("figcaption"); status.textContent = "Preparando imagen…";
  figure.append(status); bubble.append(figure);
  try {
    if (!svg) {
      const response = await fetch(`${API_BASE}/topologia/imagen`, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify(topology), signal: AbortSignal.timeout(15000)
      });
      if (!response.ok) throw new Error("Imagen no disponible");
      svg = await response.text();
    }
    if (!figure.isConnected) return;
    const url = URL.createObjectURL(new Blob([svg], {type: "image/svg+xml"})); topologyUrls.push(url);
    const image = document.createElement("img"); image.src = url;
    image.alt = `Topología propuesta de ${topology.title}: un switch y dos grupos VLAN`;
    const enlarge = document.createElement("button"); enlarge.type = "button";
    enlarge.className = "topology-preview"; enlarge.setAttribute("aria-label", "Ampliar topología");
    enlarge.append(image);
    enlarge.addEventListener("click", () => {
      $("topology-image").src = url; $("topology-image").alt = image.alt;
      const count = topology.groups.reduce((total, group) => total + group.ports.length, 0);
      $("topology-image").style.minWidth = `${Math.max(720, count * 140)}px`;
      $("topology-download").href = url; $("topology-dialog").showModal();
    });
    const actions = document.createElement("div"); actions.className = "topology-actions";
    const view = document.createElement("button"); view.type = "button"; view.textContent = "Ampliar";
    view.className = "button secondary"; view.addEventListener("click", () => enlarge.click());
    const download = document.createElement("a"); download.href = url; download.download = "topologia-netassist.svg";
    download.className = "button secondary"; download.textContent = "Descargar imagen";
    actions.append(view, download);
    status.textContent = "Esquema propuesto · Pendiente de comprobar en Packet Tracer";
    figure.replaceChildren(enlarge, actions, status);
    messagesElement.scrollTop = messagesElement.scrollHeight;
  } catch {
    status.textContent = "No se pudo cargar la imagen. ";
    const retry = document.createElement("button"); retry.type = "button"; retry.textContent = "Reintentar";
    retry.addEventListener("click", () => { figure.remove(); appendTopology(bubble, topology); }); status.append(retry);
  }
}
$("close-topology").addEventListener("click", () => $("topology-dialog").close());
function welcome() {
  clearPendingImage();
  $("topology-dialog").close(); $("topology-image").removeAttribute("src");
  $("topology-download").removeAttribute("href");
  topologyUrls.forEach(url => URL.revokeObjectURL(url)); topologyUrls = [];
  messagesElement.replaceChildren();
  const welcomeCard = document.createElement("article");
  welcomeCard.className = "nexo-welcome";
  welcomeCard.innerHTML = `<div class="nexo-welcome-art"><span class="nexo-orbit" aria-hidden="true"></span><img src="nexo.svg" alt="Nexo, un pequeño robot de redes que saluda" width="138" height="138"><span class="nexo-hello">¡Hola, colega!</span></div><p class="nexo-eyebrow">TU COMPAÑERO DE REDES</p><h3>¡Soy Nexo!</h3><p class="nexo-intro"></p><div class="nexo-prompts"><button type="button" data-nexo-prompt="¿Por dónde empiezo con esta práctica?">¿Por dónde empiezo? <span aria-hidden="true">↗</span></button><button type="button" data-nexo-prompt="Explícame por qué se usa modo access en los puertos de esta práctica.">Entender modo access <span aria-hidden="true">↗</span></button><button type="button" data-nexo-prompt="Muéstrame una imagen de la topología de mi práctica para Packet Tracer.">Ver mi topología <span aria-hidden="true">↗</span></button></div><p class="nexo-footnote">Tú haces la práctica. Yo te ayudo a entender cada paso.</p>`;
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
    title: value("title"), model: value("model"), version: activeCase?.version || "",
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
  for (const group of activeCase.groups) {
    if (!group.vlan) missing.push(`VLAN de ${group.name}`);
    if (!group.ports) missing.push(`puertos de ${group.name}`);
  }
  $("case-status").textContent = missing.length ? "Datos incompletos" : "Requisitos registrados";
  $("case-status").classList.add("open");
  const safe = escapeHtml;
  $("case-summary").className = "summary";
  $("case-summary").innerHTML = `<h3>Requisitos de la práctica</h3><dl><dt>Equipo</dt><dd>Cisco IOS · ${safe(activeCase.model || "Modelo pendiente")}</dd><dt>Conexiones</dt><dd>${safe(activeCase.connections || "Sin especificar")}</dd></dl><div class="group-summary">${activeCase.groups.map(g => `<div><h3>${safe(g.name)}</h3><p>VLAN ${safe(g.vlan || "pendiente")}</p><p>${safe(g.ports || "Puertos pendientes")}</p></div>`).join("")}</div>${missing.length ? `<p class="missing-list">Por completar: ${missing.map(safe).join(", ")}. Puedes registrar estos datos y consultar al asistente.</p>` : ""}`;
  for (const id of ["review-command", "evidence-input", "save-evidence-button", "diagnose-button"]) $(id).disabled = false;
  $("evidence-input").placeholder = "Pega aquí la salida que obtuviste en Packet Tracer…";
}
function applyForm(focus = true) {
  if (busy || !$("case-form").reportValidity()) return false;
  const nextCase = readCase();
  if (!nextCase.title) { $("form-error").textContent = "Escribe un nombre para la práctica."; return false; }
  if (!requirementsChanged()) return true;
  if (activeCase && (history.length || activeCase.evidence_records.length) && !confirm("Cambiar el equipo o las VLAN reinicia la conversación y las capturas de esta práctica. ¿Aplicar los cambios?")) return false;
  $("form-error").textContent = "";
  // Una edición inicia una revisión del caso y descarta evidencia e historial antiguos.
  activeCase = nextCase; history = []; proposalSnapshot = null; diagnosisSnapshot = null;
  $("save-case").disabled = false;
  $("evidence-records").replaceChildren(); $("diagnosis-output").replaceChildren();
  $("proposal-checks").replaceChildren(); $("generation-status").textContent = "";
  $("review-command").value = ""; $("evidence-input").value = "";
  $("evidence-status").textContent = "No hay evidencia aportada.";
  renderCase(); welcome(); activateTab(tabs[0]);
  if (focus) { $("case-heading").setAttribute("tabindex", "-1"); $("case-heading").focus(); }
  return true;
}
function requirementsChanged() {
  const form = readCase();
  return !activeCase || ["title", "model", "connections", "vendor", "groups"].some(key => JSON.stringify(form[key]) !== JSON.stringify(activeCase[key]));
}
$("case-form").addEventListener("submit", event => { event.preventDefault(); applyForm(); });
$("case-form").addEventListener("input", () => { $("storage-status").textContent = "Cambios sin guardar"; });
$("example-button").addEventListener("click", () => {
  const example = {"case-title":"Separar Administración y Laboratorio", "device-model":"Catalyst 2960", "admin-vlan":"10", "admin-ports":"Fa0/1, Fa0/2", "lab-vlan":"20", "lab-ports":"Fa0/3, Fa0/4", "connections":"Un switch con cuatro PC, dos por grupo. Confirmar el modelo en Packet Tracer."};
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
  for (const id of ["send-button", "new-chat-button", "open-case-button", "example-button", "chat-config-button", "diagnose-button", "attach-image", "chat-image", "remove-image"]) $(id).disabled = value;
  if (activeCase) $("save-evidence-button").disabled = value;
  for (const id of ["refresh-cases", "new-case"]) $(id).disabled = value;
  $("save-case").disabled = value;
  for (const button of document.querySelectorAll("[data-open-case], [data-nexo-prompt]")) button.disabled = value;
  for (const id of ["export-html", "export-json"]) $(id).disabled = value || !savedCase;
  $("typing-indicator").hidden = !value;
}
inputElement.addEventListener("keydown", event => {
  if (event.key !== "Enter" || event.shiftKey || event.isComposing || event.keyCode === 229) return;
  event.preventDefault();
  if (!busy && !event.repeat) $("chat-form").requestSubmit();
});
$("chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const draft = inputElement.value.trim(), image = pendingImage;
  if ((!draft && !image) || busy || imageReading) return;
  const content = draft || "Revisa esta captura de mi práctica y explica lo que observas.";
  const previousHistory = history.slice();
  appendMessage("user", content, true, null, null, [], image);
  clearPendingImage(); inputElement.value = ""; setBusy(true);
  const controller = new AbortController();
  const visual = history.some(message => message.image);
  const timer = setTimeout(() => controller.abort(), visual ? 75000 : 45000);
  try {
    if (visual && !chatImagesSupported) {
      const health = await fetch(`${API_BASE}/health`, {signal: AbortSignal.timeout(5000)});
      chatImagesSupported = health.ok && (await health.json()).chat_images === true;
      if (!chatImagesSupported) throw new Error("El servicio abierto todavía no admite capturas. Reinicia la API de NetAssist para activar la actualización.");
    }
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST", headers: {"Content-Type":"application/json"}, signal: controller.signal,
      body: JSON.stringify({messages: history.slice(-40), context: activeCase})
    });
    const data = await response.json();
    if (!response.ok) {
      const detail = typeof data.detail === "string" ? data.detail : data.detail?.[0]?.msg;
      throw new Error(detail || "No se pudo enviar la consulta.");
    }
    if (data.image_analyzed === false) throw new Error("No se pudo analizar la captura. Vuelve a enviarla en unos instantes.");
    if (typeof data.reply !== "string" || !data.reply.trim()) throw new Error("Respuesta no disponible");
    if (typeof data.contact === "string" && data.contact.trim()) supportContact = data.contact;
    if (data.proposal) { proposalSnapshot = data.proposal; renderProposal(data.proposal); }
    appendMessage("assistant", data.reply, true, data.topology, data.topology_svg, data.suggestions || []);
  } catch (error) {
    history = previousHistory;
    if (!inputElement.value) inputElement.value = draft;
    pendingImage = image; renderPendingImage();
    const visualError = ["AbortError", "TimeoutError"].includes(error.name)
      ? "El análisis tardó demasiado. Tu captura está lista para reenviarla."
      : error.name === "TypeError" ? "No se pudo contactar con el servicio de imágenes. Puedes volver a enviar tu captura." : error.message;
    appendMessage("assistant", visual ? visualError
      : `No pude obtener una respuesta. Puedes volver a intentarlo; tu práctica sigue abierta. Contacto: ${supportContact}`, false);
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
    chatImagesSupported = data.chat_images === true;
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

$("chat-config-button").addEventListener("click", () => {
  if (busy) return;
  inputElement.value = "Dame la configuración inicial de esta práctica.";
  $("chat-form").requestSubmit();
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
    $("proposal-checks").replaceChildren();
    if (proposal.status !== "proposed") {
      $("case-status").textContent = proposal.errors.length ? "Requisitos por corregir" : "Datos incompletos";
      $("generation-status").textContent = [...proposal.missing.map(x => `Falta: ${x}.`), ...proposal.errors].join(" ");
      return;
    }
    $("case-status").textContent = "Propuesta generada";
    $("generation-status").textContent = "Comprobaciones de código superadas. Prueba en laboratorio pendiente.";

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
  $("saved-cases").replaceChildren();
  for (const row of rows) {
    const card = document.createElement("article"); card.className = "saved-case-card";
    const title = document.createElement("h3"); title.textContent = row.title;
    const date = document.createElement("p");
    date.textContent = `Guardada el ${new Date(row.updated_at).toLocaleDateString("es-PE")}`;
    const button = document.createElement("button"); button.type = "button";
    button.className = "button secondary"; button.textContent = "Abrir práctica";
    button.dataset.openCase = row.id; button.disabled = busy;
    card.append(title, date, button); $("saved-cases").append(card);
  }
  $("library-status").textContent = rows.length ? "" : "Aún no tienes prácticas guardadas. Crea una en Laboratorio y pulsa Guardar práctica.";
  return rows;
}
$("refresh-cases").addEventListener("click", async () => {
  if (busy) return; setBusy(true);
  try { await refreshCases(); }
  catch (error) { $("library-status").textContent = error.message; }
  finally { setBusy(false); }
});
$("save-case").addEventListener("click", async () => {
  if (!applyForm(false)) return; setBusy(true);
  try {
    const payload = {case: activeCase, messages: history.slice(-60), proposal_requested: proposalSnapshot !== null, diagnosis_requested: diagnosisSnapshot !== null, revision: savedCase?.revision || null};
    const response = await storageRequest(savedCase ? `/casos/${savedCase.id}` : "/casos", {method: savedCase ? "PUT" : "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
    savedCase = await response.json();
    $("storage-status").textContent = "Guardada en Mis prácticas.";
    try { await refreshCases(); } catch { $("storage-status").textContent += " No se pudo actualizar la lista."; }
  } catch (error) { $("storage-status").textContent = error.message; }
  finally { setBusy(false); }
});
$("saved-cases").addEventListener("click", async event => {
  const id = event.target.closest("[data-open-case]")?.dataset.openCase;
  if (!id || busy) return;
  if ((activeCase || $("case-title").value) && !confirm("Abrir otra práctica reemplaza el trabajo de esta pestaña que no hayas guardado. ¿Continuar?")) return;
  setBusy(true);
  try {
    const loaded = await (await storageRequest(`/casos/${id}`)).json();
    const doc = loaded.document;
    savedCase = loaded; activeCase = doc.case; history = doc.messages;
    proposalSnapshot = doc.proposal; diagnosisSnapshot = doc.diagnosis;
    const fields = {"case-title": activeCase.title, "device-model": activeCase.model, "connections": activeCase.connections, "admin-vlan": activeCase.groups[0].vlan, "admin-ports": activeCase.groups[0].ports, "lab-vlan": activeCase.groups[1].vlan, "lab-ports": activeCase.groups[1].ports};
    for (const [id, value] of Object.entries(fields)) $(id).value = value;
    $("review-command").value = activeCase.review_command; $("evidence-input").value = activeCase.evidence;
    $("proposal-checks").replaceChildren(); $("generation-status").textContent = ""; $("diagnosis-output").replaceChildren();
    renderCase(); renderEvidence(); welcome();
    for (const message of history) appendMessage(message.role, message.content, false, message.topology, null, message.suggestions || [], message.image);
    if (proposalSnapshot) {
      renderProposal(proposalSnapshot);
      if (proposalSnapshot.commands && !history.some(message => message.role === "assistant" && message.content.includes(proposalSnapshot.commands))) {
        appendMessage("assistant", "Configuración de la práctica guardada:\n\n```ios\n" + proposalSnapshot.commands + "\n```\nPendiente de comprobar en Packet Tracer.", false);
      }
    }
    if (diagnosisSnapshot) renderDiagnosis(diagnosisSnapshot);
    else $("evidence-status").textContent = "Capturas recuperadas; puedes analizarlas.";
    activateTab(tabs[0]);
    window.location.hash = "laboratorio";
    showView();
    $("setup-title").scrollIntoView({behavior: "smooth", block: "start"});
    $("case-title").focus({preventScroll: true});
    $("storage-status").textContent = "Práctica abierta. Puedes continuar donde la dejaste.";
  } catch (error) { $("library-status").textContent = error.message; }
  finally { setBusy(false); }
});
$("new-case").addEventListener("click", () => {
  if (busy || ((activeCase || [...$("case-form").querySelectorAll("input, textarea")].some(field => field.value)) && !confirm("¿Vaciar la práctica actual? Las prácticas guardadas se conservan en Mis prácticas."))) return;
  activeCase = null; savedCase = null; history = []; proposalSnapshot = null; diagnosisSnapshot = null;
  $("case-form").reset(); $("case-content").hidden = true; $("empty-case").hidden = false;
  $("case-heading").textContent = "Un espacio para construir"; $("case-status").textContent = "Sin práctica abierta";
  $("open-case-button").textContent = "Abrir práctica ↗";
  $("chat-context").textContent = "Sin práctica abierta"; $("launcher-context").textContent = "¿Vemos tu red juntos?";
  for (const id of ["proposal-checks", "diagnosis-output", "evidence-records"]) $(id).replaceChildren();
  for (const id of ["review-command", "evidence-input"]) { $(id).value = ""; $(id).disabled = true; }
  $("save-evidence-button").disabled = true; $("evidence-status").textContent = "No hay evidencia aportada.";
  $("storage-status").textContent = "Formulario vacío. Tus prácticas guardadas siguen en Mis prácticas.";
  $("generation-status").textContent = ""; $("form-error").textContent = ""; $("case-status").classList.remove("open");
  inputElement.value = ""; $("case-title").focus();
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
function showView() {
  const library = window.location.hash === "#mis-practicas";
  $("laboratorio").hidden = library;
  $("mis-practicas").hidden = !library;
  $("current-view-title").textContent = library ? "Mis prácticas" : "Laboratorio";
  document.title = `NetAssist | ${library ? "Mis prácticas" : "Laboratorio de redes"}`;
  for (const link of document.querySelectorAll(".side-navigation a")) {
    const selected = link.getAttribute("href") === (library ? "#mis-practicas" : "#laboratorio");
    link.classList.toggle("nav-active", selected);
    if (selected) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
}
function navigateView() {
  showView();
  if (!$("mis-practicas").hidden) {
    $("library-title").focus({preventScroll: true});
    $("library-status").textContent = "Cargando prácticas…";
    refreshCases().catch(error => { $("library-status").textContent = error.message; });
  }
}
window.addEventListener("hashchange", navigateView);
navigateView();



messagesElement.addEventListener("click", event => {
  const button = event.target.closest("[data-nexo-prompt]");
  if (!button || busy) return;
  inputElement.value = button.dataset.nexoPrompt;
  $("chat-form").requestSubmit();
});
