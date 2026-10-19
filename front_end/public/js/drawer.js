/* Drawer de NetBot: apertura, cierre y ciclo de foco */

import { $, $$ } from './helpers.js';

const FOCUSABLE =
  'a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])';

export function initDrawer() {
  const drawer = $('#netbot');
  const backdrop = $('.backdrop');
  const openers = $$('.rail-btn, .fab');
  const closeButton = $('.drawer-close');
  if (!drawer || !backdrop || !closeButton || openers.length === 0) return;

  let lastFocused = null;

  const openDrawer = () => {
    lastFocused = document.activeElement;
    drawer.classList.add('is-open');
    drawer.removeAttribute('inert');
    drawer.setAttribute('aria-hidden', 'false');
    backdrop.classList.add('is-open');
    openers.forEach((btn) => btn.setAttribute('aria-expanded', 'true'));
    closeButton.focus();
  };

  const closeDrawer = () => {
    drawer.classList.remove('is-open');
    drawer.setAttribute('inert', '');
    drawer.setAttribute('aria-hidden', 'true');
    backdrop.classList.remove('is-open');
    openers.forEach((btn) => btn.setAttribute('aria-expanded', 'false'));
    if (lastFocused && typeof lastFocused.focus === 'function') {
      lastFocused.focus();
    }
  };

  openers.forEach((btn) => btn.addEventListener('click', openDrawer));
  closeButton.addEventListener('click', closeDrawer);
  backdrop.addEventListener('click', closeDrawer);

  document.addEventListener('keydown', (event) => {
    if (!drawer.classList.contains('is-open')) return;

    if (event.key === 'Escape') {
      closeDrawer();
      return;
    }

    if (event.key !== 'Tab') return;

    const focusables = $$(FOCUSABLE, drawer).filter(
      (el) => el.offsetParent !== null,
    );
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
  });
}
