import type { Metadata } from 'next';
import { Archivo, IBM_Plex_Mono, Inter } from 'next/font/google';

import { Netbot } from './components/netbot';
import { Topbar } from './components/topbar';
import './globals.css';

/* Archivo e Inter son variables; Plex Mono se usa solo en 500 y 600 */
const archivo = Archivo({
  subsets: ['latin'],
  weight: 'variable',
  display: 'swap',
  variable: '--font-display',
});

const inter = Inter({
  subsets: ['latin'],
  weight: 'variable',
  display: 'swap',
  variable: '--font-body',
});

const plexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['500', '600'],
  display: 'swap',
  variable: '--font-mono',
});

export const metadata: Metadata = {
  title: 'Cisco / Guía de Redes — Conecta el mundo',
  description:
    'Cisco construye la infraestructura sobre la que viaja internet: routers, switches, redes inalámbricas y seguridad. Aprende cómo funciona el mundo conectado.',
  icons: {
    icon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='9' fill='%232FA8EE'/%3E%3C/svg%3E",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="es"
      data-scroll-behavior="smooth"
      className={`${archivo.variable} ${inter.variable} ${plexMono.variable}`}
    >
      <body>
        {/* Las animaciones de entrada y el revelado en scroll están gateadas
            tras la clase .js: sin JS el contenido se ve entero, con JS se
            oculta hasta que toca. Va como primer nodo del body para que se
            ejecute antes de parsear (y por tanto pintar) el resto. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `document.documentElement.classList.add('js');`,
          }}
        />

        <a className="skip-link" href="#contenido">
          Saltar al contenido
        </a>

        <Topbar />

        <main id="contenido" tabIndex={-1}>
          {children}
        </main>

        <footer className="footer">
          <span className="footer-brand">
            <span className="brand-dot" aria-hidden="true"></span>
            CISCO / GUÍA DE REDES
          </span>
          <span className="footer-note">PROYECTO EDUCATIVO · GUÍA DE REDES</span>
          <span className="footer-note">NETBOT DISPONIBLE</span>
        </footer>

        <Netbot />
      </body>
    </html>
  );
}
