/* ============================================================
   우주렌탈 — Common JS
   ============================================================ */

/* ── Navigation: transparent → scrolled ───────────────────── */
(function () {
  const navbar = document.querySelector('.navbar-main');
  if (!navbar) return;

  const SCROLL_THRESHOLD = 100;

  function updateNavbar() {
    if (window.scrollY > SCROLL_THRESHOLD) {
      navbar.classList.add('navbar-scrolled');
      navbar.classList.remove('navbar-transparent');
    } else {
      navbar.classList.remove('navbar-scrolled');
      navbar.classList.add('navbar-transparent');
    }
  }

  // Run on load
  updateNavbar();
  window.addEventListener('scroll', updateNavbar, { passive: true });
})();

/* ── AOS Init ──────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 600,
      easing: 'ease-out-cubic',
      once: true,
      offset: 60,
    });
  }
});
