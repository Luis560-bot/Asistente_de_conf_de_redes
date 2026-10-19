/* Utilidades compartidas entre módulos */

export const $ = (sel, root = document) => root.querySelector(sel);

export const $$ = (sel, root = document) =>
  Array.from(root.querySelectorAll(sel));

export const prefersReducedMotion = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;
