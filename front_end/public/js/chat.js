/* Chat de NetBot: respuestas de ejemplo por palabra clave */

import { $, $$ } from './helpers.js';

const REPLIES = [
  {
    test: /\bhola\b|buenas|hey|qué tal/i,
    text: 'Hola. Soy NetBot, el asistente de esta guía. Pregúntame por redes, equipos o por dónde empezar con la CCNA.',
  },
  {
    test: /router/i,
    text: 'Un router conecta redes distintas y elige la mejor ruta para cada paquete mirando las direcciones IP y el estado de los enlaces.',
  },
  {
    test: /switch|conmutador/i,
    text: 'Un switch reparte el tráfico dentro de una misma red (LAN) usando las direcciones MAC de cada puerto.',
  },
  {
    test: /tipos? de red|lan|wan|man|pan\b/i,
    text: 'Hay cuatro grandes: LAN (local), WAN (amplia), MAN (metropolitana) y PAN (personal). En la sección Redes las comparo una a una.',
  },
  {
    test: /\bip\b|direccionamiento|subnet/i,
    text: 'La IP identifica a cada dispositivo dentro de la red. Sin ella, el router no sabría hacia dónde enviar el paquete.',
  },
  {
    test: /tcp|udp|protocolo/i,
    text: 'TCP entrega los datos en orden y confirma su llegada; UDP va más rápido pero sin confirmaciones. HTTP usa TCP.',
  },
  {
    test: /paquete|recorrido|ruta|salto/i,
    text: 'El paquete nace en el origen, sale por su router, salta de switch en switch y llega al router destino, que lo entrega. Está en la sección Redes.',
  },
  {
    test: /ccna|certificaci/i,
    text: 'La CCNA es la certificación base de Cisco: redes, direccionamiento, conmutación, enrutamiento y seguridad básica.',
  },
  {
    test: /cisco|1984|historia/i,
    text: 'Cisco nació en 1984 en San José, California. Su primer producto fue un router universitario; hoy fabrica routers, switches, wireless y seguridad.',
  },
  {
    test: /seguridad|firewall|vpn/i,
    text: 'La seguridad de red decide qué tráfico entra y qué se queda fuera: firewalls, VPN y segmentación trabajan sobre la misma infraestructura.',
  },
  {
    test: /compra|distribu|import|aduana|region/i,
    text: 'El equipo se cotiza con el canal oficial o distribuidores certificados, y viaja desde centros regionales hasta donde vaya a instalarse.',
  },
  {
    test: /gracias|genial|perfecto/i,
    text: 'Anotado. Si quieres, sigue explorando la guía con el botón «Explorar las redes».',
  },
];

const FALLBACK =
  'Puedo ayudarte con redes, equipos y esta guía. Prueba con «router», «IP», «tipos de red» o «CCNA».';

const WELCOME =
  'Hola, soy NetBot. Pregúntame sobre redes, equipos o el contenido de esta guía.';

export function initChat() {
  const log = $('#chatLog');
  const form = $('.chat-form');
  const input = $('#chatInput');
  if (!log || !form || !input) return;

  const addMessage = (text, who) => {
    const bubble = document.createElement('div');
    bubble.className = `msg msg-${who}`;
    bubble.textContent = text;
    log.appendChild(bubble);
    log.scrollTop = log.scrollHeight;
    return bubble;
  };

  const botReply = (question) => {
    const typing = document.createElement('div');
    typing.className = 'msg msg-bot msg-typing';
    typing.setAttribute('aria-label', 'NetBot está escribiendo');
    typing.innerHTML = '<i></i><i></i><i></i>';
    log.appendChild(typing);
    log.scrollTop = log.scrollHeight;

    const match = REPLIES.find((entry) => entry.test.test(question));
    const answer = match ? match.text : FALLBACK;

    window.setTimeout(() => {
      typing.remove();
      addMessage(answer, 'bot');
    }, 650);
  };

  const sendMessage = (text) => {
    const clean = text.trim();
    if (!clean) return;
    addMessage(clean, 'user');
    botReply(clean);
  };

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    sendMessage(input.value);
    input.value = '';
    input.focus();
  });

  $$('.chip').forEach((chip) => {
    chip.addEventListener('click', () => sendMessage(chip.textContent));
  });

  addMessage(WELCOME, 'bot');
}
