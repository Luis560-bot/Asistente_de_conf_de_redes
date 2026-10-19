/* Punto de entrada: monta todos los módulos de la página */

import { initNav } from './nav.js';
import { initReveal } from './reveal.js';
import { initDrawer } from './drawer.js';
import { initChat } from './chat.js';

initNav();
initReveal();
initDrawer();
initChat();
