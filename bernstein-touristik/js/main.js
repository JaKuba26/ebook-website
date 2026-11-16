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

  // Hotelseite: mobile Buchungsleiste
  if (document.querySelector('.sticky-book')) document.body.classList.add('has-sticky-book');

  // Hotelseite: Unternavigation markiert den aktuellen Abschnitt
  var subLinks = document.querySelectorAll('.subnav a');
  if (subLinks.length && 'IntersectionObserver' in window) {
    var byId = {};
    subLinks.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        subLinks.forEach(function (a) { a.classList.remove('is-active'); });
        var a = byId[en.target.id];
        if (a) {
          a.classList.add('is-active');
          var nav = a.parentElement;
          nav.scrollTo({ left: a.offsetLeft - 16, behavior: 'smooth' });
        }
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    Object.keys(byId).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }

  // Hotelseite: Bildergalerie (Lightbox)
  var box = document.getElementById('lightbox');
  var data = window.GALERIE;
  if (box && data && typeof box.showModal === 'function') {
    var img = box.querySelector('img');
    var cap = box.querySelector('figcaption');
    var idx = 0;
    var n = data.bilder.length;
    var show = function (i) {
      idx = (i + n) % n;
      var b = data.bilder[idx];
      img.src = data.pfad + b[0] + '.jpg';
      img.alt = b[1];
      cap.textContent = b[1] + ' · ' + (idx + 1) + ' / ' + n;
      // nächstes Bild vorladen
      new Image().src = data.pfad + data.bilder[(idx + 1) % n][0] + '.jpg';
    };
    document.querySelectorAll('.gallery__item').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        show(Number(a.dataset.index) || 0);
        box.showModal();
      });
    });
    box.querySelector('.lightbox__prev, .lightbox__nav--prev').addEventListener('click', function () { show(idx - 1); });
    box.querySelector('.lightbox__nav--next').addEventListener('click', function () { show(idx + 1); });
    box.querySelector('.lightbox__close').addEventListener('click', function () { box.close(); });
    box.addEventListener('click', function (e) { if (e.target === box) box.close(); });
    box.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
    // Wischen auf dem Handy
    var x0 = null;
    box.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    box.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) show(idx + (dx < 0 ? 1 : -1));
      x0 = null;
    });
  }

  // Jahr im Footer
  var jahr = document.getElementById('jahr');
  if (jahr) jahr.textContent = new Date().getFullYear();
})();
