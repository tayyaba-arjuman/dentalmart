/* ============================================================
   DENTAL MART — static/js/script.js
   Shared JS: cart (localStorage), API helpers, UI helpers
   ============================================================ */

/* ── Products are injected by Flask into each template ─────────────────────
   Access via window.PRODUCTS set in each template's <script> block.       */

/* ══════════════════════════════════════════════════════════
   1. CART  (localStorage — works without server round-trip)
   ══════════════════════════════════════════════════════════ */
const Cart = {
  get()    { return JSON.parse(localStorage.getItem('dm_cart') || '[]'); },
  save(c)  { localStorage.setItem('dm_cart', JSON.stringify(c)); },

  add(id) {
    const cart     = this.get();
    const existing = cart.find(c => c.id === id);
    if (existing) existing.qty++;
    else cart.push({ id, qty: 1 });
    this.save(cart);
  },
  remove(id) { this.save(this.get().filter(c => c.id !== id)); },
  changeQty(id, delta) {
    const cart = this.get();
    const item = cart.find(c => c.id === id);
    if (!item) return;
    item.qty += delta;
    if (item.qty <= 0) this.save(cart.filter(c => c.id !== id));
    else this.save(cart);
  },
  clear() { localStorage.removeItem('dm_cart'); },

  totalItems() { return this.get().reduce((s, c) => s + c.qty, 0); },

  subtotal(products) {
    return this.get().reduce((s, c) => {
      const p = (products || window.PRODUCTS || []).find(p => p.id === c.id);
      return s + (p ? p.price * c.qty : 0);
    }, 0);
  },
  shipping(products) { return this.subtotal(products) >= 999 ? 0 : 80; },
  grandTotal(products) { return this.subtotal(products) + this.shipping(products); }
};

/* ══════════════════════════════════════════════════════════
   2. API HELPER
   ══════════════════════════════════════════════════════════ */
async function apiFetch(url, options = {}) {
  const defaults = {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
  };
  const res  = await fetch(url, { ...defaults, ...options });
  const data = await res.json();
  return data;
}

/* ══════════════════════════════════════════════════════════
   3. UI HELPERS
   ══════════════════════════════════════════════════════════ */
let _toastTimer;
function showToast(msg, isWarn = false) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.querySelector('.toast-msg').textContent = msg;
  el.classList.toggle('warn', isWarn);
  el.classList.add('show');
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => el.classList.remove('show'), 2600);
}

function show(id) { const e = document.getElementById(id); if (e) e.style.display = 'block'; }
function hide(id) { const e = document.getElementById(id); if (e) e.style.display = 'none'; }
function hideAll(ids) { ids.forEach(hide); }
function fmt(n) { return '₹' + Number(n).toLocaleString('en-IN'); }
function genOrderId() { return 'DM' + Date.now().toString().slice(-8); }

/* ══════════════════════════════════════════════════════════
   4. CART BADGE
   ══════════════════════════════════════════════════════════ */
function updateCartBadge() {
  const badge = document.getElementById('cartBadge');
  if (!badge) return;
  const n = Cart.totalItems();
  badge.textContent = n;
  badge.classList.toggle('visible', n > 0);
}

/* ══════════════════════════════════════════════════════════
   5. ADD-TO-CART HANDLER  (used on index + catalog)
   ══════════════════════════════════════════════════════════ */
function addToCartHandler(id) {
  /* Check if user is logged in via Flask session — the template sets window.LOGGED_IN */
  if (!window.LOGGED_IN) {
    showToast('🔐 Please login to add items to cart', true);
    setTimeout(() => window.location.href = '/login', 1200);
    return;
  }
  Cart.add(id);
  updateCartBadge();
  const p = (window.PRODUCTS || []).find(p => p.id === id);
  showToast('🛒 ' + (p ? p.name : 'Item') + ' added to cart');
  const btn = document.getElementById('addBtn-' + id);
  if (btn) { btn.textContent = '✓ Added'; btn.classList.add('added'); }
}

/* ══════════════════════════════════════════════════════════
   6. PRODUCT CARD BUILDER  (used on index + catalog pages)
   ══════════════════════════════════════════════════════════ */
function buildProductCard(p) {
  const inCart    = Cart.get().find(c => c.id === p.id);
  const badgeHtml = p.badge
    ? `<div class="product-badge ${p.badge_type || ''}">${p.badge}</div>` : '';

  /* image path using Flask static */
  const imgSrc = p.image
    ? `/static/images/${p.image}`
    : '/static/images/placeholder.jpg';

  return `
  <div class="product-card" id="card-${p.id}">
    <div class="product-img-wrap">
      <img src="${imgSrc}" alt="${p.name}"
           onerror="this.src='/static/images/placeholder.jpg'">
      ${badgeHtml}
    </div>
    <div class="product-body">
      <div class="product-category">${p.category}</div>
      <div class="product-name">${p.name}</div>
      <div class="product-desc">${p.desc}</div>
      <div class="product-footer">
        <div class="product-price">
          ${fmt(p.price)}<small>incl. tax</small>
        </div>
        <button class="add-cart-btn ${inCart ? 'added' : ''}"
                id="addBtn-${p.id}"
                onclick="addToCartHandler(${p.id})">
          ${inCart ? '✓ Added' : '+ Add'}
        </button>
      </div>
    </div>
  </div>`;
}

/* ══════════════════════════════════════════════════════════
   7. HAMBURGER MENU
   ══════════════════════════════════════════════════════════ */
function initHamburger() {
  const ham = document.getElementById('hamburger');
  const nl  = document.getElementById('navLinks');
  if (ham && nl) ham.addEventListener('click', () => nl.classList.toggle('mobile-open'));
}

/* ══════════════════════════════════════════════════════════
   8. LOGOUT
   ══════════════════════════════════════════════════════════ */
async function handleLogout() {
  if (!confirm('Log out of DentalMart?')) return;
  await apiFetch('/api/auth/logout', { method: 'POST' });
  window.location.href = '/';
}

/* ══════════════════════════════════════════════════════════
   9. INIT on every page
   ══════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  updateCartBadge();
  initHamburger();

  /* Logout button wiring */
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);
});
