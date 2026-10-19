/* Barra superior: menú en móvil y sección activa según el scroll */

import { $, $$ } from './helpers.js';

export function initNav() {
  const navPill = $('.nav-pill');
  const navToggle = $('.nav-toggle');
  if (!navPill || !navToggle) return;

  const closeNav = () => {
    navPill.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
  };

  navToggle.addEventListener('click', () => {
    const open = navPill.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(open));
  });

  const navLinks = $$('.nav-pill a');
  const sectionByLink = new Map(
    navLinks.map((link) => [link.hash.slice(1), link]),
  );

  const activeObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        navLinks.forEach((link) => link.classList.remove('is-active'));
        const link = sectionByLink.get(entry.target.id);
        if (link) link.classList.add('is-active');
      });
    },
    { rootMargin: '-45% 0px -50% 0px' },
  );

  sectionByLink.forEach((_link, id) => {
    const section = document.getElementById(id);
    if (section) activeObserver.observe(section);
  });

  navLinks.forEach((link) => link.addEventListener('click', closeNav));

  document.addEventListener('click', (event) => {
    if (!navPill.classList.contains('is-open')) return;
    if (event.target.closest('.topbar')) return;
    closeNav();
  });
}
