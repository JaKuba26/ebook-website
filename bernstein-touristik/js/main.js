// Bernstein Touristik – kleine Helfer für die Landingpage
(function () {
  // Mobiles Menü
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('hauptnav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('is-open', !open);
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        toggle.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
      }
    });
  }

  // Schatten unter der Kopfzeile beim Scrollen
  var header = document.getElementById('kopf');
  var onScroll = function () { header.classList.toggle('is-scrolled', window.scrollY > 10); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Hotel-Slider: Pfeile
  var slider = document.getElementById('hotel-slider');
  document.querySelectorAll('.slider-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var card = slider.querySelector('.hotel');
      var step = card ? card.getBoundingClientRect().width + 24 : 300;
      slider.scrollBy({ left: step * Number(btn.dataset.dir), behavior: 'smooth' });
    });
  });

  // Suche: gewählten Ort in den Suchbegriff übernehmen
  var form = document.querySelector('.search');
  if (form) {
    form.addEventListener('submit', function () {
      var ort = form.querySelector('select');
      var s = form.querySelector('input[name="s"]');
      s.value = [ort.value, s.value].filter(Boolean).join(' ').trim();
      ort.disabled = true;
    });
  }

  // Jahr im Footer
  var jahr = document.getElementById('jahr');
  if (jahr) jahr.textContent = new Date().getFullYear();
})();
