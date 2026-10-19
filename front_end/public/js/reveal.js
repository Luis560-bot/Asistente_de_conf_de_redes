/* Revelado de bloques cuando entran en pantalla */

import { $$, prefersReducedMotion } from './helpers.js';

export function initReveal() {
  const reveals = $$('.reveal');
  if (reveals.length === 0) return;

  if (prefersReducedMotion()) {
    reveals.forEach((el) => el.classList.add('is-visible'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries, currentObserver) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        currentObserver.unobserve(entry.target);
      });
    },
    { threshold: 0.15 },
  );

  reveals.forEach((el) => observer.observe(el));
}
