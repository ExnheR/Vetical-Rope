(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  const root = document.documentElement;
  const nav = $('#nav');
  const burger = $('.burger');
  const themeButton = $('#theme');

  if (burger && nav) {
    burger.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', String(open));
    });
  }

  $$('.mi > .tg').forEach(link => {
    link.addEventListener('click', event => {
      if (window.matchMedia('(max-width: 1340px)').matches) {
        event.preventDefault();
        const parent = link.closest('.mi');
        if (parent) parent.classList.toggle('open');
      } else if (link.getAttribute('href') === '#') {
        event.preventDefault();
      }
    });
  });

  if (themeButton) {
    themeButton.addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('vr_theme', next); } catch (error) {}
    });
  }

  // ===== Transición entre páginas (escalador descendiendo) =====
  // Flujo: clic -> capa + escalador (~1 s) -> navegar -> la página nueva muestra el logo y la capa se desvanece.
  const transition = $('#vr-trans');
  const reduceMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const DURATION = 1050;          // ms visibles antes de cargar la página destino
  let navigating = false;

  const resetTransition = () => {
    navigating = false;
    if (transition) transition.classList.remove('on', 'play');
  };

  // Llegada: la capa ya viene visible (clase vr-in puesta en <head>) y se desvanece.
  if (root.classList.contains('vr-in')) {
    const done = () => root.classList.add('vr-done');
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => setTimeout(done, 250));
    else setTimeout(done, 250);
    setTimeout(done, 1500);       // seguro adicional
  }

  const startTransition = go => {
    // Sin capa o con movimiento reducido: navegación normal e inmediata.
    if (!transition || reduceMotion()) { go(); return; }
    if (navigating) return;       // evita ejecuciones dobles
    navigating = true;
    try { sessionStorage.setItem('vr', String(Date.now())); } catch (error) {}
    transition.classList.add('on');
    void transition.offsetWidth;  // fuerza el reflujo para reiniciar las animaciones
    transition.classList.add('play');
    setTimeout(go, DURATION);
    // Si la navegación no ocurre (cancelada, error), nunca se bloquea la pantalla.
    setTimeout(resetTransition, DURATION + 3500);
  };

  const isInternalNavigation = (link, event) => {
    if (event.defaultPrevented || event.button !== 0) return false;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return false;
    const raw = link.getAttribute('href');
    if (!raw || raw.startsWith('#') || /^(mailto:|tel:|javascript:)/i.test(raw)) return false;
    if (link.hasAttribute('download') || link.dataset.noTransition !== undefined) return false;
    if (link.target && link.target !== '_self') return false;
    let url;
    try { url = new URL(link.href, window.location.href); } catch (error) { return false; }
    if (url.origin !== window.location.origin) return false;
    if (url.hash) return false;   // enlaces con ancla no se interceptan
    if (url.pathname === window.location.pathname && url.search === window.location.search) return false;
    return url.href;
  };

  document.addEventListener('click', event => {
    const link = event.target.closest ? event.target.closest('a[href]') : null;
    if (!link) return;
    const target = isInternalNavigation(link, event);
    if (!target) return;
    event.preventDefault();
    startTransition(() => { window.location.href = target; });
  });

  // Buscador del encabezado (GET): también cambia de página.
  $$('form.search').forEach(form => form.addEventListener('submit', event => {
    if (event.defaultPrevented || !transition || reduceMotion() || navigating) return;
    event.preventDefault();
    startTransition(() => form.submit());
  }));

  // Al volver con el botón "atrás" (bfcache) la capa no debe quedar visible.
  window.addEventListener('pageshow', event => {
    if (event.persisted) { resetTransition(); root.classList.add('vr-done'); }
  });

  // Carrusel de la página de inicio.
  const slides = $$('.slide');
  const dots = $$('.dots button');
  if (slides.length > 1) {
    let current = Math.max(0, slides.findIndex(slide => slide.classList.contains('on')));
    let timer;
    const show = index => {
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => slide.classList.toggle('on', i === current));
      dots.forEach((dot, i) => dot.classList.toggle('on', i === current));
    };
    dots.forEach((dot, i) => dot.addEventListener('click', () => { show(i); restart(); }));
    const restart = () => {
      window.clearInterval(timer);
      if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) timer = window.setInterval(() => show(current + 1), 6500);
    };
    restart();
  }

  // Búsqueda instantánea + filtros por categoría. Sin JavaScript, Flask hace el mismo filtrado.
  const search = $('#q');
  const list = $('#list');
  if (search && list) {
    const cards = $$('.card', list);
    const chips = $$('.chip[data-grupo]');
    const initialCat = list.dataset.initialCat || '';
    let group = list.dataset.initialGrupo || '';
    const norm = value => (value || '').toLocaleLowerCase('es').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    const update = () => {
      const query = norm(search.value.trim());
      let visible = 0;
      cards.forEach(card => {
        const text = norm(card.dataset.text);
        const ok = (!initialCat || card.dataset.cat === initialCat) &&
                   (!group || card.dataset.grupo === group) &&
                   (!query || text.includes(query));
        card.hidden = !ok;
        if (ok) visible++;
      });
      chips.forEach(chip => chip.classList.toggle('on', (chip.dataset.grupo || '') === group));
      const empty = $('#empty');
      if (empty) empty.hidden = visible > 0;
      const hidden = $('#g');
      if (hidden) hidden.value = group;
    };
    chips.forEach(chip => chip.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey) return;
      event.preventDefault();
      event.stopPropagation();    // el filtro es instantáneo: no cambia de página
      group = chip.dataset.grupo || '';
      update();
      try {
        const params = new URLSearchParams(window.location.search);
        if (group) params.set('grupo', group); else params.delete('grupo');
        history.replaceState(null, '', window.location.pathname + (params.toString() ? '?' + params : ''));
      } catch (error) {}
    }));
    search.addEventListener('input', update);
    const filterForm = $('#ff');
    if (filterForm) filterForm.addEventListener('submit', event => { event.preventDefault(); update(); });
    update();
  }

  // Carrito de cotización guardado en el navegador.
  const dataElement = $('#vr-data');
  const products = (() => {
    try { return JSON.parse(dataElement ? dataElement.textContent : '[]'); }
    catch (error) { return []; }
  })();
  const productMap = new Map(products.map(product => [String(product.id), product]));
  const cartPanel = $('#cart');
  const overlay = $('#cv');
  const cartList = $('#cl');
  const emptyMessage = $('#ce');
  const count = $('#cc');
  let cart = {};
  try { cart = JSON.parse(localStorage.getItem('vr_cart') || '{}') || {}; } catch (error) { cart = {}; }

  const saveCart = () => {
    try { localStorage.setItem('vr_cart', JSON.stringify(cart)); } catch (error) {}
  };
  const openCart = () => {
    if (!cartPanel || !overlay) return;
    cartPanel.classList.add('open');
    overlay.classList.add('open');
    cartPanel.setAttribute('aria-hidden', 'false');
    $('#cx')?.focus();
  };
  const closeCart = () => {
    if (!cartPanel || !overlay) return;
    cartPanel.classList.remove('open');
    overlay.classList.remove('open');
    cartPanel.setAttribute('aria-hidden', 'true');
  };
  const renderCart = () => {
    if (!cartList) return;
    cartList.innerHTML = '';
    let total = 0;
    Object.entries(cart).forEach(([id, quantity]) => {
      const product = productMap.get(String(id));
      const qty = Math.max(0, Number(quantity) || 0);
      if (!product || !qty) { delete cart[id]; return; }
      total += qty;
      const item = document.createElement('li');
      item.className = 'cart-item';
      const thumb = document.createElement('img');
      thumb.src = product.img || ''; thumb.alt = ''; thumb.loading = 'lazy';
      thumb.addEventListener('error', () => thumb.classList.add('fail'));
      const info = document.createElement('div');
      info.className = 'ci';
      const title = document.createElement('a');
      title.href = product.u || '#'; title.textContent = product.n;
      const controls = document.createElement('div');
      controls.className = 'q';
      const minus = document.createElement('button');
      minus.type = 'button'; minus.textContent = '−'; minus.setAttribute('aria-label', 'Quitar una unidad');
      const amount = document.createElement('span'); amount.textContent = String(qty);
      const plus = document.createElement('button');
      plus.type = 'button'; plus.textContent = '+'; plus.setAttribute('aria-label', 'Añadir una unidad');
      const remove = document.createElement('button');
      remove.type = 'button'; remove.className = 'rm'; remove.textContent = 'Eliminar';
      minus.addEventListener('click', () => { cart[id] = (Number(cart[id]) || 0) - 1; if (cart[id] <= 0) delete cart[id]; saveCart(); renderCart(); });
      plus.addEventListener('click', () => { cart[id] = (Number(cart[id]) || 0) + 1; saveCart(); renderCart(); });
      remove.addEventListener('click', () => { delete cart[id]; saveCart(); renderCart(); });
      controls.append(minus, amount, plus, remove);
      info.append(title, controls);
      item.append(thumb, info);
      cartList.append(item);
    });
    if (count) count.textContent = String(total);
    if (emptyMessage) emptyMessage.hidden = total > 0;
    saveCart();
  };

  $$('.add').forEach(button => {
    button.addEventListener('click', () => {
      const id = String(button.dataset.id || '');
      if (!productMap.has(id)) return;
      cart[id] = (Number(cart[id]) || 0) + 1;
      saveCart(); renderCart(); openCart();
    });
  });
  document.addEventListener('keydown', event => { if (event.key === 'Escape') closeCart(); });
  $('#cartbtn')?.addEventListener('click', openCart);
  $('#cx')?.addEventListener('click', closeCart);
  overlay?.addEventListener('click', closeCart);
  $('#cclr')?.addEventListener('click', () => { cart = {}; saveCart(); renderCart(); });
  window.addEventListener('storage', event => {
    if (event.key === 'vr_cart') {
      try { cart = JSON.parse(event.newValue || '{}') || {}; } catch (error) { cart = {}; }
      renderCart();
    }
  });
  renderCart();

  // Rellena el mensaje del formulario con los productos seleccionados.
  const contactForm = $('#cf');
  if (contactForm && new URLSearchParams(window.location.search).get('cart') === '1') {
    const message = $('textarea[name="mensaje"]', contactForm);
    if (message && !message.value.trim()) {
      const names = Object.entries(cart).map(([id, qty]) => {
        const product = productMap.get(String(id));
        return product ? `${product.n} (cantidad: ${qty})` : '';
      }).filter(Boolean);
      message.value = names.length ? `Solicito cotización para:\n${names.join('\n')}\nPor favor confirmar precios y disponibilidad.` : 'Quiero solicitar una cotización de productos. Por favor confirmar precios y disponibilidad.';
    }
  }

  // ===== Formulario de contacto: validación en el navegador (Flask vuelve a validar) =====
  if (contactForm) {
    const rules = {
      nombre: v => v.trim().length >= 2 ? '' : 'Escribe tu nombre.',
      correo: v => /^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(v.trim()) ? '' : 'Escribe un correo válido.',
      telefono: v => !v.trim() || /^[0-9+()\s-]{7,20}$/.test(v.trim()) ? '' : 'Revisa el número de teléfono.',
      asunto: v => v.trim().length >= 3 ? '' : 'Escribe un asunto.',
      mensaje: v => v.trim().length >= 10 ? '' : 'El mensaje debe tener al menos 10 caracteres.'
    };
    const check = field => {
      const rule = rules[field.name];
      if (!rule) return true;
      const message = rule(field.value);
      const slot = $(`.err[data-for="${field.name}"]`, contactForm);
      if (slot) slot.textContent = message;
      field.setAttribute('aria-invalid', message ? 'true' : 'false');
      return !message;
    };
    $$('input, textarea', contactForm).forEach(field => {
      field.addEventListener('blur', () => check(field));
      field.addEventListener('input', () => { if (field.getAttribute('aria-invalid') === 'true') check(field); });
    });
    contactForm.addEventListener('submit', event => {
      const invalid = $$('input[name], textarea[name]', contactForm).filter(field => !check(field));
      if (invalid.length) { event.preventDefault(); invalid[0].focus(); }
    });
  }
})();
