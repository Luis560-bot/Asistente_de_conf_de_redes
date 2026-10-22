'use client';

/* Barra superior: menú en móvil y sección activa según el scroll */

import { useEffect, useRef, useState } from 'react';

const SECTIONS = [
  { href: '#cisco', label: 'CISCO' },
  { href: '#redes', label: 'REDES' },
  { href: '#importancia', label: 'IMPORTANCIA' },
  { href: '#importacion', label: 'IMPORTACIÓN' },
];

export function Topbar() {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState('');
  const navRef = useRef<HTMLElement>(null);

  /* Sección visible según el scroll: misma franja que la versión original */
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          setActive(entry.target.id);
        }
      },
      { rootMargin: '-45% 0px -50% 0px' },
    );

    for (const { href } of SECTIONS) {
      const section = document.getElementById(href.slice(1));
      if (section) observer.observe(section);
    }

    return () => observer.disconnect();
  }, []);

  /* Cerrar el menú al pulsar fuera de la barra */
  useEffect(() => {
    if (!open) return;

    const onPointerDown = (event: PointerEvent) => {
      if (!navRef.current?.contains(event.target as Node)) setOpen(false);
    };

    document.addEventListener('pointerdown', onPointerDown);
    return () => document.removeEventListener('pointerdown', onPointerDown);
  }, [open]);

  return (
    <header className="topbar" ref={navRef}>
      <a className="brand" href="#inicio">
        <span className="brand-dot" aria-hidden="true"></span>
        CISCO / GUÍA DE REDES
      </a>

      <button
        className="nav-toggle"
        type="button"
        aria-expanded={open}
        aria-controls="nav-list"
        onClick={() => setOpen((value) => !value)}
      >
        MENÚ
      </button>

      <nav
        className={open ? 'nav-pill is-open' : 'nav-pill'}
        id="nav-list"
        aria-label="Secciones de la guía"
      >
        {SECTIONS.map(({ href, label }) => (
          <a
            key={href}
            href={href}
            className={active === href.slice(1) ? 'is-active' : undefined}
            onClick={() => setOpen(false)}
          >
            {label}
          </a>
        ))}
      </nav>
    </header>
  );
}
