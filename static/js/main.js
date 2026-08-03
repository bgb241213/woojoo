/* ============================================================
   우주렌탈 — Common JS (redesign)
   ============================================================ */

/* ── Overlay nav: transparent → solid on scroll ───────────── */
(function () {
  const nav = document.getElementById('siteNav');
  if (!nav || !nav.classList.contains('site-nav--overlay')) return;
  const THRESHOLD = 80;
  function update() {
    nav.classList.toggle('is-stuck', window.scrollY > THRESHOLD);
  }
  update();
  window.addEventListener('scroll', update, { passive: true });
})();

/* ── Mobile slide-down menu ────────────────────────────────── */
(function () {
  const nav = document.getElementById('siteNav');
  const toggle = document.getElementById('navToggle');
  const menu = document.getElementById('navMobile');
  if (!toggle || !menu) return;
  toggle.addEventListener('click', function () {
    const open = menu.classList.toggle('is-open');
    // On the transparent (home) nav, turn the top bar solid while the menu is open.
    if (nav) nav.classList.toggle('is-menu-open', open);
  });
})();

/* ── Business hours ────────────────────────────────────────── */
/* 월–금 08:00–18:00 · 토·일 휴무 */
function woojooIsOpen(now) {
  now = now || new Date();
  const day = now.getDay();               // 0=Sun … 6=Sat
  if (day === 0 || day === 6) return false;
  const mins = now.getHours() * 60 + now.getMinutes();
  return mins >= 480 && mins < 1080;      // 08:00–18:00
}

/* ── Call modal (floating button + any [data-call-open]) ──── */
(function () {
  const modal = document.getElementById('callModal');
  if (!modal) return;
  const openPane = document.getElementById('callOpen');
  const closedPane = document.getElementById('callClosed');

  function openModal() {
    const isOpen = woojooIsOpen();
    openPane.classList.toggle('is-hidden', !isOpen);
    closedPane.classList.toggle('is-hidden', isOpen);
    modal.classList.add('is-open');
  }
  function closeModal() { modal.classList.remove('is-open'); }

  const fab = document.getElementById('callFab');
  if (fab) fab.addEventListener('click', openModal);
  document.querySelectorAll('[data-call-open]').forEach(function (el) {
    el.addEventListener('click', function (e) { e.preventDefault(); openModal(); });
  });
  modal.querySelectorAll('[data-call-close]').forEach(function (el) {
    el.addEventListener('click', closeModal);
  });
  modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });

  // Callback submission (closed-hours path)
  const submit = document.getElementById('cbSubmit');
  if (submit) {
    submit.addEventListener('click', function () {
      const phone = (document.getElementById('cbPhone').value || '').trim();
      const memo = (document.getElementById('cbMemo').value || '').trim();
      const privacy = document.getElementById('cbPrivacy');
      if (!phone) { document.getElementById('cbPhone').focus(); return; }
      if (privacy && !privacy.checked) { privacy.focus(); return; }
      submit.disabled = true;
      const csrf = (document.getElementById('callCsrf') || {}).value || '';
      fetch('/quote/callback/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
        body: JSON.stringify({ phone: phone, message: memo, privacy_agree: true }),
      })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d && d.success) {
            document.getElementById('callbackForm').classList.add('is-hidden');
            document.getElementById('callbackDone').classList.remove('is-hidden');
          } else {
            submit.disabled = false;
          }
        })
        .catch(function () { submit.disabled = false; });
    });
  }
})();

/* ── Touch swipe (photo carousels) ─────────────────────────── */
/* Binds left/right swipes on `el` without stealing vertical page scrolls.
   A swipe also swallows the click the browser fires afterwards, so tapping
   through to a lightbox stays a deliberate tap. */
function woojooSwipe(el, onPrev, onNext) {
  const MIN = 40;                       // px of travel before it counts
  let x0 = null, y0 = null, swiping = false;

  el.addEventListener('touchstart', function (e) {
    if (e.touches.length !== 1) { x0 = null; return; }
    x0 = e.touches[0].clientX;
    y0 = e.touches[0].clientY;
    swiping = false;
  }, { passive: true });

  el.addEventListener('touchmove', function (e) {
    if (x0 === null) return;
    const dx = e.touches[0].clientX - x0;
    const dy = e.touches[0].clientY - y0;
    if (!swiping && Math.abs(dx) > MIN && Math.abs(dx) > Math.abs(dy)) swiping = true;
    if (swiping && e.cancelable) e.preventDefault();
  }, { passive: false });

  el.addEventListener('touchend', function (e) {
    if (x0 !== null && swiping) {
      (e.changedTouches[0].clientX - x0 < 0 ? onNext : onPrev)();
      const swallow = function (ev) { ev.stopPropagation(); ev.preventDefault(); };
      el.addEventListener('click', swallow, true);
      setTimeout(function () { el.removeEventListener('click', swallow, true); }, 350);
    }
    x0 = y0 = null;
    swiping = false;
  });
}

/* ── Hide the floating call button over the footer ─────────── */
(function () {
  var fab = document.getElementById('callFab');
  var footer = document.querySelector('.site-footer');
  if (!fab || !footer || !('IntersectionObserver' in window)) return;
  new IntersectionObserver(function (entries) {
    fab.classList.toggle('is-tucked', entries[0].isIntersecting);
    /* the bottom strip is where the button sits — only tuck once the
       footer actually rises into it */
  }, { threshold: 0, rootMargin: '0px 0px -90px 0px' }).observe(footer);
})();
