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
  var KLAPP_IDS = ['lage', 'zimmer', 'ausstattung', 'verpflegung', 'wellness', 'leistungen'];
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

  // Hol- und Bringdienst: Fahrpreis nach Postleitzahl (Katalog 2025, S. 7)
  var FAHRPREISE = [
    ['Berlin', '10-13,17', 99], ['', '01-02', 199], ['', '03,06', 179], ['', '04,08-09', 159], ['', '07', 189],
    ['', '14', 139], ['', '15', 189, 'Sa'], ['', '16', 129], ['', '18', 179], ['', '19', 189],
    ['', '20,22,28-29', 199], ['', '21', 189], ['', '23,27', 279], ['', '24-25', 329], ['', '26', 299],
    ['', '30-31,37-38', 199], ['', '32-33', 219], ['', '34-36', 209], ['', '39', 189], ['', '40,44-46', 249],
    ['', '41,47', 299], ['', '42', 239], ['', '48', 229], ['', '49', 199], ['', '50-51,63', 249],
    ['', '52-53,55', 299], ['', '54,66', 349], ['', '56', 279], ['', '57-58', 229], ['', '59', 199],
    ['', '60-61,64-65', 279], ['', '67-69', 319], ['', '70,72,75-76', 349], ['', '71,73', 299], ['', '74', 249],
    ['', '77,79', 399], ['', '78', 379], ['', '80-81', 279], ['', '82-83,87', 399], ['', '84-85', 339],
    ['', '86,89', 299], ['', '88', 349], ['', '90,92', 239], ['', '91', 279], ['', '93', 309],
    ['', '94', 229], ['', '95', 209], ['', '96-98', 199], ['', '99', 189]
  ];
  // Badeort-Zuschläge pro Person (Orte östlich von Kolberg); null = auf Anfrage
  var ZUSCHLAG = {
    'ostseebad-henkenhagen-ustronie-morskie': ['Henkenhagen', 25],
    'ostseebad-groess-moellen-mielno': ['Großmöllen', 79],
    'ruegenwaldermuende': ['Rügenwaldermünde', 129],
    'jershoeft': ['Jershöft', 149],
    'pommern-danzig': ['Danzig', 299],
    'ostseebad-stolpmuende-ustka': ['Stolpmünde', null]
  };
  var fahrpreis = function (plz) {
    var z = parseInt(plz.slice(0, 2), 10);
    for (var i = 0; i < FAHRPREISE.length; i++) {
      var teile = FAHRPREISE[i][1].split(',');
      for (var j = 0; j < teile.length; j++) {
        var g = teile[j].split('-'), von = parseInt(g[0], 10), bis = parseInt(g[1] || g[0], 10);
        if (z >= von && z <= bis) return { preis: FAHRPREISE[i][2], samstag: FAHRPREISE[i][3] === 'Sa' };
      }
    }
    return null;
  };
  var euro = function (n) { return n.toLocaleString('de-DE') + '\u00a0€'; };
  document.querySelectorAll('.plz-check').forEach(function (box) {
    var eingabe = box.querySelector('.plz-check__input');
    var ausgabe = box.querySelector('.plz-check__ergebnis');
    var ort = ZUSCHLAG[box.dataset.ort || ''];
    var tabelle = box.querySelector('.plz-tabelle');
    if (tabelle) {
      var html = '<table class="prices prices--compact"><thead><tr><th scope="col">PLZ beginnt mit</th><th scope="col">Preis p. P.</th></tr></thead><tbody>';
      FAHRPREISE.forEach(function (f) {
        html += '<tr><th scope="row">' + (f[0] ? f[0] + ' ' : '') + f[1].replace(/,/g, ', ').replace(/-/g, '–') + (f[3] ? '*' : '') + '</th><td>' + euro(f[2]) + '</td></tr>';
      });
      html += '</tbody></table><p class="note">* PLZ 15: Anreise und Abreise samstags.</p>';
      html += '<table class="prices prices--compact plz-tabelle__zuschlag"><thead><tr><th scope="col">Badeorte und Zuschläge</th><th scope="col">p. P.</th></tr></thead><tbody>';
      Object.keys(ZUSCHLAG).forEach(function (k) {
        if (ZUSCHLAG[k][1] !== null) html += '<tr><th scope="row">' + ZUSCHLAG[k][0] + '</th><td>' + euro(ZUSCHLAG[k][1]) + '</td></tr>';
      });
      html += '</tbody></table><p class="note">Zuschläge werden separat berechnet. Ohne Zuschlag: alle Orte von Swinemünde bis Kolberg.</p>';
      tabelle.innerHTML = html;
    }
    var zeigen = function () {
      var plz = eingabe.value.replace(/\D/g, '').slice(0, 5);
      if (eingabe.value !== plz) eingabe.value = plz;
      box.classList.remove('is-ok', 'is-fehler');
      if (plz.length < 2) { ausgabe.innerHTML = ''; return; }
      var t = fahrpreis(plz);
      if (!t) {
        box.classList.add('is-fehler');
        ausgabe.innerHTML = 'Für diese Postleitzahl haben wir keinen Festpreis – bitte rufen Sie uns an: <a href="tel:+493048490070">030-484 900 70</a>.';
        return;
      }
      box.classList.add('is-ok');
      var tage = t.samstag ? 'Abholung samstags · Rückfahrt samstags' : 'Abholung sonntags · Rückfahrt samstags';
      ausgabe.innerHTML = '<span class="plz-check__preis">' + euro(t.preis) + '<small> pro Person</small></span>' +
        '<span class="plz-check__detail">Hin- und Rückfahrt ab Ihrer Haustür · ' + tage + '</span>';
    };
    if (ort) {
      var hinweis = document.createElement('p');
      hinweis.className = 'plz-check__zuschlag';
      hinweis.innerHTML = '<strong>Badeort-Zuschlag ' + ort[0] + ':</strong> ' + (ort[1] !== null ? euro(ort[1]) + ' pro Person' : 'auf Anfrage') + ' – wird separat berechnet.';
      ausgabe.parentNode.insertBefore(hinweis, ausgabe.nextSibling);
    }
    eingabe.addEventListener('input', zeigen);
    zeigen();
  });

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
