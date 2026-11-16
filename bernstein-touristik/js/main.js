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

  // Suchseite: Hotels aus suche/hotels.json filtern
  var ergebnis = document.getElementById('suche-ergebnisse');
  if (ergebnis) {
    var params = new URLSearchParams(location.search);
    var formS = document.querySelector('.search--page');
    var q = (params.get('q') || params.get('s') || '').trim();
    var ortP = params.get('ort') || '';
    formS.q.value = q;
    formS.ort.value = ortP;
    var info = document.getElementById('suche-info');
    var escH = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var norm = function (t) { return t.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/ł/g, 'l'); };
    fetch('hotels.json').then(function (r) { return r.json(); }).then(function (alle) {
      var woerter = norm(q).split(/\s+/).filter(Boolean);
      var treffer = alle.filter(function (h) {
        if (ortP && h.o !== ortP) return false;
        var text = norm(h.n + ' ' + h.on + ' ' + h.t);
        return woerter.every(function (w) { return text.indexOf(w) !== -1; });
      });
      treffer.sort(function (a, b) {
        var an = woerter.length && woerter.every(function (w) { return norm(a.n).indexOf(w) !== -1; }) ? 0 : 1;
        var bn = woerter.length && woerter.every(function (w) { return norm(b.n).indexOf(w) !== -1; }) ? 0 : 1;
        return an - bn || (parseFloat(a.p) || 9999) - (parseFloat(b.p) || 9999);
      });
      info.textContent = treffer.length
        ? treffer.length + (treffer.length === 1 ? ' Hotel gefunden' : ' Hotels gefunden') + (q ? ' für „' + q + '“' : '')
        : 'Leider keine Treffer' + (q ? ' für „' + q + '“' : '') + '. Versuchen Sie einen anderen Begriff oder rufen Sie uns an: 030-484 900 70.';
      ergebnis.innerHTML = treffer.map(function (h) {
        var url = '../hotels/' + h.s + '/';
        return '<article class="offer"><a class="offer__media" href="' + url + '" tabindex="-1" aria-hidden="true"><img src="../' + h.b + '" alt="" loading="lazy" width="560" height="420">' +
          (h.so ? '<span class="badge">Sonderangebot</span>' : '') + '</a><div class="offer__body"><p class="offer__place">' + escH(h.on) + '</p>' +
          '<h3><a href="' + url + '">' + escH(h.n) + '</a> ' + (h.st ? '<span class="stars">' + '★'.repeat(h.st) + '</span>' : '') + '</h3>' +
          '<div class="offer__foot"><p class="price"><span>1 Woche schon ab</span><strong>' + escH(h.p) + ' €</strong><span>pro Person</span></p>' +
          '<a class="btn btn--navy" href="' + url + '">Ansehen</a></div></div></article>';
      }).join('');
    });
  }

  // Hotelkarte: Google Maps erst nach Klick laden (Datenschutz)
  var mapBox = document.querySelector('.map-consent');
  if (mapBox) {
    mapBox.querySelector('button').addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = mapBox.dataset.src;
      f.title = 'Hotelkarte (Google Maps)';
      f.loading = 'lazy';
      f.allowFullscreen = true;
      mapBox.innerHTML = '';
      mapBox.appendChild(f);
      mapBox.classList.add('is-loaded');
    });
  }

  // Hotelseite: lange Abschnitte einklappen ("Mehr anzeigen")
  var KLAPP_IDS = ['lage', 'zimmer', 'ausstattung', 'verpflegung', 'wellness', 'leistungen', 'anreise'];
  var GRENZE = 260;   // ab dieser Höhe (px) wird eingeklappt
  var SICHTBAR = 170; // so viel bleibt sichtbar
  var klappen = [];
  KLAPP_IDS.forEach(function (id) {
    var block = document.getElementById(id);
    if (!block || !block.classList.contains('block')) return;
    var titel = block.querySelector('h2');
    var box = document.createElement('div');
    box.className = 'klapp';
    box.id = id + '-inhalt';
    while (titel.nextSibling) box.appendChild(titel.nextSibling);
    block.appendChild(box);
    if (box.scrollHeight <= GRENZE) return;
    box.classList.add('is-zu');
    box.style.maxHeight = SICHTBAR + 'px';
    var knopf = document.createElement('button');
    knopf.type = 'button';
    knopf.className = 'klapp__btn';
    knopf.setAttribute('aria-expanded', 'false');
    knopf.setAttribute('aria-controls', box.id);
    knopf.innerHTML = '<span>Mehr anzeigen</span><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M7.4 8.6 12 13.2l4.6-4.6L18 10l-6 6-6-6z"/></svg>';
    block.appendChild(knopf);
    var setze = function (auf, scrollen) {
      knopf.setAttribute('aria-expanded', String(auf));
      knopf.querySelector('span').textContent = auf ? 'Weniger anzeigen' : 'Mehr anzeigen';
      box.classList.toggle('is-zu', !auf);
      box.style.maxHeight = (auf ? box.scrollHeight : SICHTBAR) + 'px';
      if (auf) setTimeout(function () { if (knopf.getAttribute('aria-expanded') === 'true') box.style.maxHeight = 'none'; }, 450);
      else if (scrollen && block.getBoundingClientRect().top < 0) block.scrollIntoView({ behavior: 'smooth' });
    };
    knopf.addEventListener('click', function () {
      var auf = knopf.getAttribute('aria-expanded') !== 'true';
      if (!auf && box.style.maxHeight === 'none') {
        // von "none" auf feste Höhe, damit die Animation läuft
        box.style.maxHeight = box.scrollHeight + 'px';
        box.offsetHeight; // eslint-disable-line no-unused-expressions
      }
      setze(auf, true);
    });
    klappen.push({ id: id, oeffnen: function () { if (knopf.getAttribute('aria-expanded') !== 'true') setze(true); } });
  });
  // Sprung über die Leiste (Lage, Zimmer …) klappt den Abschnitt auf
  var oeffneAnker = function () {
    var id = location.hash.slice(1);
    klappen.forEach(function (k) { if (k.id === id) k.oeffnen(); });
  };
  window.addEventListener('hashchange', oeffneAnker);
  document.querySelectorAll('.subnav a').forEach(function (a) {
    a.addEventListener('click', function () {
      var id = a.getAttribute('href').slice(1);
      klappen.forEach(function (k) { if (k.id === id) k.oeffnen(); });
    });
  });
  oeffneAnker();

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
      img.src = data.pfad + b[0] + (data.endung || '.jpg');
      img.alt = b[1];
      cap.textContent = b[1] + ' · ' + (idx + 1) + ' / ' + n;
      // nächstes Bild vorladen
      new Image().src = data.pfad + data.bilder[(idx + 1) % n][0] + (data.endung || '.jpg');
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

  // Hotelübersicht: nach Ort filtern (auch über #ort in der Adresse)
  var chips = document.querySelectorAll('.chip[data-filter]');
  if (chips.length) {
    var gruppen = document.querySelectorAll('.ort-gruppe');
    var filtern = function (ort, scroll) {
      chips.forEach(function (c) { c.classList.toggle('is-active', c.dataset.filter === ort); });
      gruppen.forEach(function (g) { g.hidden = !!ort && g.dataset.ort !== ort; });
      if (scroll) window.scrollTo({ top: document.querySelector('.hotel-groups').offsetTop - 160, behavior: 'smooth' });
    };
    chips.forEach(function (c) {
      c.addEventListener('click', function () {
        filtern(c.dataset.filter, true);
        history.replaceState(null, '', c.dataset.filter ? '#' + c.dataset.filter : location.pathname);
      });
    });
    var start = location.hash.slice(1);
    if (start && document.getElementById(start)) filtern(start, false);
  }

  // Jahr im Footer
  var jahr = document.getElementById('jahr');
  if (jahr) jahr.textContent = new Date().getFullYear();
})();
