'use client';

/* NetBot: riel lateral, botón flotante, drawer con ciclo de foco y chat */

import { useEffect, useRef, useState } from 'react';

/* Respuestas de ejemplo por palabra clave (mock en cliente) */
const REPLIES: { test: RegExp; text: string }[] = [
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

const CHIPS = [
  '¿Qué es un router?',
  '¿Qué tipos de red existen?',
  '¿Cómo preparo la CCNA?',
];

const FOCUSABLE =
  'a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])';

type Message = { id: number; text: string; who: 'user' | 'bot' };

let nextId = 1;

function replyTo(question: string) {
  const match = REPLIES.find((entry) => entry.test.test(question));
  return match ? match.text : FALLBACK;
}

export function Netbot() {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState('');
  const [typing, setTyping] = useState(false);
  const [messages, setMessages] = useState<Message[]>(() => [
    { id: 0, text: WELCOME, who: 'bot' },
  ]);

  const drawerRef = useRef<HTMLElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const logRef = useRef<HTMLDivElement>(null);
  const lastFocused = useRef<HTMLElement | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  /* Guardar el foco de origen y llevarlo al botón de cierre al abrir */
  useEffect(() => {
    if (open) {
      lastFocused.current = document.activeElement as HTMLElement | null;
      closeRef.current?.focus();
      return;
    }

    if (lastFocused.current?.isConnected) lastFocused.current.focus();
  }, [open]);

  /* Cerrar con Escape y mantener el foco dentro del drawer con Tab */
  useEffect(() => {
    if (!open) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false);
        return;
      }

      if (event.key !== 'Tab') return;

      const drawer = drawerRef.current;
      if (!drawer) return;

      const focusables = Array.from(
        drawer.querySelectorAll<HTMLElement>(FOCUSABLE),
      ).filter((element) => element.offsetParent !== null);

      if (focusables.length === 0) return;

      const first = focusables[0];
      const last = focusables[focusables.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [open]);

  /* El log siempre anclado al final */
  useEffect(() => {
    const log = logRef.current;
    if (log) log.scrollTop = log.scrollHeight;
  }, [messages, typing]);

  const sendMessage = (text: string) => {
    const clean = text.trim();
    if (!clean) return;

    setMessages((previous) => [
      ...previous,
      { id: nextId++, text: clean, who: 'user' },
    ]);
    setTyping(true);

    window.setTimeout(() => {
      setTyping(false);
      setMessages((previous) => [
        ...previous,
        { id: nextId++, text: replyTo(clean), who: 'bot' },
      ]);
    }, 650);
  };

  return (
    <>
      <aside className="rail">
        <button
          className="rail-btn"
          type="button"
          aria-controls="netbot"
          aria-expanded={open}
          onClick={() => setOpen(true)}
        >
          <span className="rail-chevron" aria-hidden="true">
            ›
          </span>
          <span className="rail-text">ABRIR NETBOT</span>
          <span className="rail-dot" aria-hidden="true"></span>
        </button>
      </aside>

      <button
        className="fab"
        type="button"
        aria-controls="netbot"
        aria-expanded={open}
        onClick={() => setOpen(true)}
      >
        ABRIR NETBOT
        <span className="fab-dot" aria-hidden="true"></span>
      </button>

      <div className={open ? 'backdrop is-open' : 'backdrop'} aria-hidden="true" onClick={() => setOpen(false)}></div>

      <section
        className={open ? 'drawer is-open' : 'drawer'}
        id="netbot"
        ref={drawerRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="netbot-title"
        aria-hidden={!open}
        inert={!open}
      >
        <header className="drawer-head">
          <div className="drawer-id">
            <span className="drawer-name" id="netbot-title">
              NETBOT
            </span>
            <span className="drawer-status">
              <span className="status-dot" aria-hidden="true"></span>
              DISPONIBLE
            </span>
          </div>
          <button
            className="drawer-close"
            type="button"
            aria-label="Cerrar el chat"
            ref={closeRef}
            onClick={() => setOpen(false)}
          >
            ✕
          </button>
        </header>

        <div className="chat-log" id="chatLog" ref={logRef} role="log" aria-live="polite">
          {messages.map((message) => (
            <div key={message.id} className={`msg msg-${message.who}`}>
              {message.text}
            </div>
          ))}

          {typing && (
            <div
              className="msg msg-bot msg-typing"
              aria-label="NetBot está escribiendo"
            >
              <i></i>
              <i></i>
              <i></i>
            </div>
          )}
        </div>

        <div className="chips" role="group" aria-label="Preguntas rápidas">
          {CHIPS.map((chip) => (
            <button
              key={chip}
              className="chip"
              type="button"
              onClick={() => sendMessage(chip)}
            >
              {chip}
            </button>
          ))}
        </div>

        <form
          className="chat-form"
          autoComplete="off"
          onSubmit={(event) => {
            event.preventDefault();
            sendMessage(draft);
            setDraft('');
            inputRef.current?.focus();
          }}
        >
          <label className="sr-only" htmlFor="chatInput">
            Escribe tu pregunta
          </label>
          <input
            id="chatInput"
            name="mensaje"
            type="text"
            placeholder="Escribe tu pregunta sobre redes…"
            maxLength={300}
            value={draft}
            ref={inputRef}
            onChange={(event) => setDraft(event.target.value)}
          />
          <button className="chat-send" type="submit">
            Enviar
          </button>
        </form>
      </section>
    </>
  );
}
