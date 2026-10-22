import { Reveal } from './components/reveal';

export default function Home() {
  return (
    <>
      <section className="hero" id="inicio" aria-labelledby="hero-title">
        <div className="hero-bg" aria-hidden="true">
          <span className="hero-grid"></span>
          <span className="trace trace-h1"></span>
          <span className="trace trace-v"></span>
          <span className="trace trace-h2"></span>
          <span className="packet"></span>
        </div>

        <div className="hero-inner">
          <div className="eyebrow-row">
            <span className="eyebrow">EST. 1984 · SAN JOSÉ, CALIFORNIA</span>
            <span className="tag">INFRAESTRUCTURA DIGITAL</span>
          </div>

          <h1 className="hero-title" id="hero-title">
            <span className="ht-line">Conecta el</span>
            <span className="ht-line accent">mundo.</span>
          </h1>

          <p className="hero-lede">
            Cisco construye la infraestructura sobre la que viaja internet:
            routers, switches, redes inalámbricas y seguridad. Aprende cómo
            funciona el mundo conectado.
          </p>

          <div className="hero-actions">
            <a className="btn-primary" href="#redes">
              Explorar las redes
              <span className="btn-arrow" aria-hidden="true">
                →
              </span>
            </a>
            <span className="status">
              <span className="status-dot" aria-hidden="true"></span>
              NetBot disponible
            </span>
          </div>

          <dl className="stats">
            <div className="stat">
              <dt>1984</dt>
              <dd>FUNDACIÓN</dd>
            </div>
            <div className="stat">
              <dt>+90</dt>
              <dd>PAÍSES</dd>
            </div>
            <div className="stat">
              <dt>CCNA</dt>
              <dd>CERTIFICACIÓN</dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="section" id="cisco" aria-labelledby="cisco-title">
        <Reveal>
          <div className="sec-head">
            <span className="sec-eyebrow">QUIÉN CONSTRUYE LA RED</span>
            <h2 className="sec-title" id="cisco-title">
              De un router en 1984 a la red que usas hoy.
            </h2>
            <p className="sec-lede">
              Cisco Systems nació en San José, California, de la mano de Leonard
              Bosack y Sandy Lerner. Su primer producto fue un router que
              conectaba redes distintas dentro de la universidad, y de ahí vino
              el nombre: San Francisco.
            </p>
          </div>
        </Reveal>

        <div className="split">
          <Reveal>
            <div className="split-copy">
              <p>
                Cuatro décadas después, esa misma idea sostiene datacenters,
                oficinas, campus y ciudades enteras: equipos que se ponen de
                acuerdo para mover datos sin que tú lo notes.
              </p>
              <p>
                Detrás de cada página que abres hay un router que elige la ruta,
                un switch que reparte el tráfico y una política de seguridad que
                decide qué entra y qué no.
              </p>
            </div>
          </Reveal>

          <Reveal>
            <ul className="list" aria-label="Líneas de producto">
              <li>
                <h3>Routers y switches</h3>
                <p>Conectan redes y deciden por dónde viaja cada paquete.</p>
              </li>
              <li>
                <h3>Redes inalámbricas</h3>
                <p>
                  Puntos de acceso y controladores WiFi para oficinas y campus.
                </p>
              </li>
              <li>
                <h3>Seguridad</h3>
                <p>Firewalls y VPN que bloquean lo ajeno antes de que entre.</p>
              </li>
              <li>
                <h3>Colaboración</h3>
                <p>Voz y vídeo viajando sobre la misma red de datos.</p>
              </li>
            </ul>
          </Reveal>
        </div>

        <Reveal>
          <ol className="timeline">
            <li>
              <span className="tl-year">1984</span>
              <span className="tl-label">FUNDACIÓN EN SAN JOSÉ</span>
            </li>
            <li>
              <span className="tl-year">1990</span>
              <span className="tl-label">SALIDA A BOLSA · NASDAQ: CSCO</span>
            </li>
            <li>
              <span className="tl-year">1998</span>
              <span className="tl-label">NACE LA CERTIFICACIÓN CCNA</span>
            </li>
          </ol>
        </Reveal>
      </section>

      <section className="section" id="redes" aria-labelledby="redes-title">
        <Reveal>
          <div className="sec-head">
            <span className="sec-eyebrow">CÓMO SE CONECTA TODO</span>
            <h2 className="sec-title" id="redes-title">Qué es una red</h2>
            <p className="sec-lede">
              Una red es dos o más equipos que intercambian datos siguiendo las
              mismas reglas, llamadas protocolos. Sin esas reglas, cada
              dispositivo hablaría por su cuenta y nadie entendería a nadie.
            </p>
          </div>
        </Reveal>

        <Reveal>
          <ul className="cards" aria-label="Tipos de red">
            <li className="card">
              <span className="card-eyebrow">ÁREA LOCAL</span>
              <h3>LAN</h3>
              <p>
                Casa, oficina o campus. Cobertura corta, alta velocidad, equipos
                propios.
              </p>
            </li>
            <li className="card">
              <span className="card-eyebrow">ÁREA AMPLIA</span>
              <h3>WAN</h3>
              <p>
                Conecta ciudades y países. Internet es la mayor WAN que existe.
              </p>
            </li>
            <li className="card">
              <span className="card-eyebrow">ÁREA METROPOLITANA</span>
              <h3>MAN</h3>
              <p>Une varias LAN dentro de una misma ciudad.</p>
            </li>
            <li className="card">
              <span className="card-eyebrow">RED PERSONAL</span>
              <h3>PAN</h3>
              <p>
                Teléfono, auriculares y reloj: tu propia burbuja de dispositivos.
              </p>
            </li>
          </ul>
        </Reveal>

        <Reveal>
          <div className="route">
            <span className="sec-eyebrow">RUTA DE LOS DATOS</span>
            <h3 className="route-title">El recorrido de un paquete</h3>
            <ol className="steps">
              <li>
                <span className="step-num">01</span>
                <span className="step-text">
                  El origen divide los datos en paquetes y les escribe su
                  dirección IP.
                </span>
              </li>
              <li>
                <span className="step-num">02</span>
                <span className="step-text">
                  El router de salida consulta su tabla de enrutamiento y elige
                  la ruta.
                </span>
              </li>
              <li>
                <span className="step-num">03</span>
                <span className="step-text">
                  Los switches de cada red local lo saltan de puerto en puerto
                  hasta el siguiente salto.
                </span>
              </li>
              <li>
                <span className="step-num">04</span>
                <span className="step-text">
                  El router destino lo entrega y el receptor vuelve a juntar los
                  datos en orden.
                </span>
              </li>
            </ol>
          </div>
        </Reveal>
      </section>

      <section
        className="section"
        id="importancia"
        aria-labelledby="importancia-title"
      >
        <Reveal>
          <div className="sec-head">
            <span className="sec-eyebrow">POR QUÉ IMPORTA</span>
            <h2 className="sec-title" id="importancia-title">
              Todo lo que importa viaja por aquí.
            </h2>
            <p className="sec-lede">
              Salud, comercio, educación y gobierno dependen de que la red esté
              ahí. Por eso se mide con números exigentes y se documenta su
              impacto.
            </p>
          </div>
        </Reveal>

        <Reveal>
          <dl className="figures">
            <div className="figure">
              <dt>+5.500 M</dt>
              <dd>PERSONAS CONECTADAS</dd>
            </div>
            <div className="figure">
              <dt>99,999 %</dt>
              <dd>DISPONIBILIDAD OBJETIVO</dd>
            </div>
            <div className="figure">
              <dt>5 min 15 s</dt>
              <dd>CAÍDA MÁXIMA AL AÑO</dd>
            </div>
          </dl>
        </Reveal>

        <Reveal>
          <ul className="domains" aria-label="Áreas que dependen de la red">
            <li>
              <h3>Comercio</h3>
              <p>Tiendas, pagos y almacenes no funcionan sin red.</p>
            </li>
            <li>
              <h3>Educación</h3>
              <p>Aulas, bibliotecas y exámenes viven dentro de ella.</p>
            </li>
            <li>
              <h3>Salud</h3>
              <p>Historias clínicas y telemedicina se mueven por la red.</p>
            </li>
            <li>
              <h3>Gobierno</h3>
              <p>Trámites y servicios públicos dependen de su disponibilidad.</p>
            </li>
          </ul>
        </Reveal>
      </section>

      <section
        className="section"
        id="importacion"
        aria-labelledby="importacion-title"
      >
        <Reveal>
          <div className="sec-head">
            <span className="sec-eyebrow">COMPRA Y DISTRIBUCIÓN</span>
            <h2 className="sec-title" id="importacion-title">
              Cómo se compran y cómo se distribuyen.
            </h2>
            <p className="sec-lede">
              El equipo de red no llega solo: alguien lo cotiza, lo compra y lo
              mueve hasta la región donde se va a instalar.
            </p>
          </div>
        </Reveal>

        <div className="cols2">
          <Reveal>
            <div className="col">
              <span className="col-head">CÓMO SE COMPRAN</span>
              <ul className="list">
                <li>
                  <h3>Canal oficial</h3>
                  <p>
                    Compra directa al fabricante o a distribuidores certificados.
                  </p>
                </li>
                <li>
                  <h3>Presupuesto y licencias</h3>
                  <p>Se cotiza por cantidad, modelo y licencias de software.</p>
                </li>
                <li>
                  <h3>Partner certificado</h3>
                  <p>Un integrador instala, configura y da soporte.</p>
                </li>
              </ul>
            </div>
          </Reveal>

          <Reveal>
            <div className="col">
              <span className="col-head">CÓMO SE DISTRIBUYEN</span>
              <ul className="list">
                <li>
                  <h3>Centros regionales</h3>
                  <p>El material sale de almacenes cercanos a cada mercado.</p>
                </li>
                <li>
                  <h3>Aduanas y plazos</h3>
                  <p>Importar equipo implica partidas, aranceles y tiempos.</p>
                </li>
                <li>
                  <h3>Cobertura</h3>
                  <p>Cisco entrega en más de 90 países.</p>
                </li>
              </ul>
            </div>
          </Reveal>
        </div>

        <Reveal>
          <ul className="regions" aria-label="Regiones de distribución">
            <li className="region">
              <span className="region-name">AMÉRICAS</span>
              <p>Norte, Centro y Sur.</p>
            </li>
            <li className="region">
              <span className="region-name">EMEA</span>
              <p>Europa, Oriente Medio y África.</p>
            </li>
            <li className="region">
              <span className="region-name">APJC</span>
              <p>Asia-Pacífico, Japón y China.</p>
            </li>
          </ul>
        </Reveal>
      </section>
    </>
  );
}
