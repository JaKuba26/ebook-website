#!/usr/bin/env python3
"""Erzeugt die übrigen Seiten der neuen Website und stellt alle Links um.

Aufruf:  python3 seiten_bauen.py [ordner-mit-alten-seiten]
  - orte/ (Übersicht), orte/<slug>/ (15 Orte), orte/sonderangebote/
  - kontakt/, vip/, bernstein-katalog/, karte/, suche/
  - impressum/, agb/, datenschutzerklaerung/ (Texte aus der alten Website,
    nur wenn der Ordner mit den alten Seiten angegeben ist)
  - zum Schluss: alle Links auf www.bernstein-touristik.de -> neue Seiten
"""
import html
import json
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from hotels_auslesen import ORTE  # noqa: E402
from hotels_bauen import (HANDGEBAUT, SLUG_NEU, WURZEL, anpassen, esc, karte,  # noqa: E402
                          preis_zahl, vorlage_teile)

ALT = 'https://www.bernstein-touristik.de'
CALL_FAB = '''<a class="call-fab" href="tel:+493048490070" aria-label="Jetzt anrufen: 030-484 900 70">
  <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/></svg>
</a>
'''

# Texte für Orte, die auf der alten Seite keinen Text hatten (bitte vom Kunden prüfen lassen)
ORT_TEXT_NEU = {
    'jershoeft': [
        'Jershöft (auf Polnisch: Jarosławiec) ist ein kleines, ruhiges Ostseebad in Westpommern zwischen Rügenwalde und Stolpmünde. '
        'Der Ort liegt auf einer Steilküste und ist bekannt für seinen Leuchtturm, von dem aus man weit über die Küste blickt.',
        'Breite, feinsandige Strände, Kiefernwälder und die frische, jodhaltige Meeresluft machen Jershöft zu einem idealen Ziel '
        'für alle, die Erholung abseits des Trubels suchen.',
    ],
    'ruegenwaldermuende': [
        'Rügenwaldermünde (auf Polnisch: Darłówko) ist der Badeort der Stadt Rügenwalde (Darłowo) an der Mündung der Wipper in die Ostsee. '
        'Der kleine Fischerhafen mit seinen Kuttern und die Fußgängerbrücke über die Hafeneinfahrt prägen das maritime Ortsbild.',
        'Zu beiden Seiten der Hafeneinfahrt laden lange Sandstrände zum Baden und Spazieren ein. Im nahen Rügenwalde lohnt sich '
        'ein Besuch der historischen Altstadt mit dem Schloss der Pommernherzöge.',
    ],
    'pommern-danzig': [
        'Die Region um Danzig (Gdańsk) verbindet Ostseeurlaub mit Kultur: Danzig mit seiner prachtvoll wiederaufgebauten Altstadt, '
        'das mondäne Seebad Zoppot (Sopot) mit seiner berühmten Seebrücke und Gdingen (Gdynia) bilden zusammen die „Dreistadt“.',
        'Elegante Kurhotels, breite Strände und die lebendige Promenade in Zoppot machen die Region zu einem besonderen Ziel – '
        'ideal für eine Kur- oder Wellnessreise mit Ausflügen in die Hansestadt Danzig.',
    ],
}


def rel(tiefe):
    return '../' * tiefe


def seite(titel, beschreibung, tiefe, inhalt, aktiv=None, robots=None, extra_body=''):
    """Komplette Seite mit Kopf und Fuß aus der Vorlage (Tiefe = Ordnerebenen unter der Wurzel)."""
    kopf, fuss = vorlage_teile()[:2]
    r = rel(tiefe)
    kopf = kopf.replace(' aria-current="page"', '')
    kopf = kopf.replace('href="#anfrage">Unverbindlich anfragen', 'href="tel:+493048490070">Kostenlos beraten lassen')
    kopf = kopf.replace('../../', '\0')
    fuss = fuss.replace('../../', '\0')
    # Links relativ zur Hotelseite (../ = hotels/) vorher absolut machen
    kopf = kopf.replace('href="../"', 'href="\0hotels/"')
    fuss = fuss.replace('href="../"', 'href="\0hotels/"')
    kopf = kopf.replace('\0', r)
    fuss = fuss.replace('\0', r)
    if aktiv:
        kopf = re.sub(r'(<li><a href="[^"]*")(>%s</a></li>)' % re.escape(aktiv), r'\1 aria-current="page"\2', kopf, count=1)
    head = f'''<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(titel)}</title>
  <meta name="description" content="{esc(beschreibung)}">
  {'<meta name="robots" content="' + robots + '">' if robots else ''}
  <meta name="theme-color" content="#13283b">
  <link rel="icon" href="{r}img/favicon.png">
  <link rel="preload" href="{r}fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{r}fonts/fraunces.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{r}css/style.css">
</head>
<body>

'''
    return head + kopf + '<main id="inhalt">\n' + inhalt + '\n</main>' + fuss + CALL_FAB + extra_body + \
        f'<script src="{r}js/main.js" defer></script>\n</body>\n</html>\n'


def schreiben(pfad, text):
    voll = os.path.join(WURZEL, pfad)
    os.makedirs(os.path.dirname(voll), exist_ok=True)
    with open(voll, 'w', encoding='utf-8') as f:
        f.write(text)


def page_hero(titel, text, crumbs, eyebrow='', bild=None):
    stil = ''
    klasse = 'page-hero page-hero--bild' if bild else 'page-hero'
    bild_html = f'<img class="page-hero__bg" src="{bild}" alt="" width="1920" height="400" fetchpriority="high">' if bild else ''
    kr = ''.join(f'<a href="{u}">{esc(t)}</a><span aria-hidden="true">›</span>' for t, u in crumbs[:-1]) + \
        f'<span aria-current="page">{esc(crumbs[-1][0])}</span>'
    return f'''<section class="{klasse}"{stil}>
    {bild_html}
    <div class="wrap">
      <nav class="crumbs crumbs--light" aria-label="Brotkrümelnavigation">{kr}</nav>
      {f'<p class="eyebrow eyebrow--amber">{eyebrow}</p>' if eyebrow else ''}
      <h1>{titel}</h1>
      {f'<p>{text}</p>' if text else ''}
    </div>
  </section>'''


def kontakt_band(r):
    return f'''<section class="contact">
    <div class="wrap contact__inner">
      <div>
        <p class="eyebrow eyebrow--amber">Wir sind für Sie da</p>
        <h2>Lassen Sie sich kostenlos beraten</h2>
        <p>Unsere Urlaubsspezialisten kennen die Hotels persönlich und helfen Ihnen gerne bei der Auswahl – telefonisch oder in unserem Reisebüro in Berlin-Pankow.</p>
        <div class="contact__actions">
          <a class="btn btn--amber btn--lg" href="tel:+493048490070">030-484 900 70 anrufen</a>
          <a class="btn btn--ghost btn--lg" href="{r}kontakt/">Kontakt &amp; Anfahrt</a>
        </div>
      </div>
      <dl class="contact__card">
        <div><dt>Gratis-Hotline</dt><dd><a href="tel:+493048490070">030-484 900 70</a></dd></div>
        <div><dt>Öffnungszeiten</dt><dd>Mo.–Fr. 9–18 Uhr<br>Sa. 10–15 Uhr</dd></div>
        <div><dt>E-Mail</dt><dd><a href="mailto:info@bernstein-touristik.de">info@bernstein-touristik.de</a></dd></div>
      </dl>
    </div>
  </section>'''


# ---------------------------------------------------------------- Orte

def orte_seiten(hotels):
    orte_daten = json.load(open(os.path.join(HIER, 'orte.json'), encoding='utf-8'))
    karten_orte = []
    for slug, (name, kurz) in ORTE.items():
        hs = [h for h in hotels if h['ort'] == slug]
        hs.sort(key=lambda x: (not x.get('sonderangebot'), preis_zahl(x['ab_preis']) or 9999))
        texte = [t for tag, t in orte_daten.get(slug, {}).get('text', []) if tag == 'p'] or ORT_TEXT_NEU.get(slug, [])
        preise = [preis_zahl(h['ab_preis']) for h in hs if preis_zahl(h['ab_preis'])]
        ab = f'{int(min(preise))}' if preise else ''
        karten_orte.append((slug, name, kurz, len(hs), ab, texte))
        r = '../../'
        andere = ''.join(f'<li><a href="../{s}/">{esc(k)}</a></li>' for s, (n, k) in ORTE.items() if s != slug)
        fakten = f'''<ul class="ort-facts">
          <li><strong>{len(hs)}</strong> {"Hotel" if len(hs) == 1 else "Hotels"}</li>
          {f'<li><strong>ab {ab} €</strong> pro Woche</li>' if ab else ''}
          <li><a class="link-arrow" href="{r}karte/">Auf der Karte ansehen</a></li>
        </ul>'''
        inhalt = page_hero(esc(name), '', [('Startseite', r), ('Orte', '../'), (name, '')],
                           eyebrow='Polnische Ostsee', bild=f'{r}img/orte/{slug}.webp') + f'''
  <section class="section section--tight">
    <div class="wrap ort-intro">
      <div class="lead">
        {"".join(f'<p>{esc(t)}</p>' for t in texte)}
      </div>
      {fakten}
    </div>
  </section>

  <section class="section section--sand" id="hotels">
    <div class="wrap">
      <div class="section__head">
        <div>
          <p class="eyebrow">Unsere Hotels</p>
          <h2>Hotels in {esc(kurz)}</h2>
        </div>
      </div>
      <div class="offers offers--4">
        {"".join(karte(h, GROESSEN, r, mit_ort=False) for h in hs)}
      </div>
    </div>
  </section>

  <section class="section section--tight">
    <div class="wrap">
      <h2 class="h3">Weitere Ostseebäder</h2>
      <ul class="chips">{andere}</ul>
    </div>
  </section>

  {kontakt_band(r)}'''
        schreiben(f'orte/{slug}/index.html', seite(
            f'{name} – Hotels & Kurreisen | Bernstein Touristik',
            (texte[0][:150].rsplit(' ', 1)[0] + ' …') if texte else f'Hotels und Kurreisen im {name}.',
            2, inhalt, aktiv='Orte'))

    # Übersicht aller Orte
    kacheln = ''.join(f'''<a class="ort-card" href="{slug}/">
          <img src="../img/orte/{slug}-klein.webp" alt="" loading="lazy" width="640" height="200">
          <div class="ort-card__body">
            <h2>{esc(name)}</h2>
            <p>{n} {"Hotel" if n == 1 else "Hotels"}{f" · ab {ab} € pro Woche" if ab else ""}</p>
          </div>
        </a>''' for slug, name, kurz, n, ab, t in karten_orte)
    inhalt = page_hero('Unsere Ostseebäder', 'Von Swinemünde an der deutschen Grenze bis nach Danzig – entdecken Sie die schönsten Kur- und Badeorte der polnischen Ostseeküste.',
                       [('Startseite', '../'), ('Orte', '')], eyebrow='Reiseziele') + f'''
  <section class="section section--tight">
    <div class="wrap">
      <figure class="places__map places__map--wide">
        <img src="../img/karte-ostsee.jpg" alt="Karte der polnischen Ostseeküste mit allen Bernstein-Reisezielen" loading="lazy" width="1200" height="498">
      </figure>
      <div class="ort-grid">
        {kacheln}
      </div>
    </div>
  </section>
  {kontakt_band('../')}'''
    schreiben('orte/index.html', seite('Unsere Ostseebäder | Bernstein Touristik',
                                       'Alle Reiseziele von Bernstein Touristik an der polnischen Ostsee: Swinemünde, Misdroy, Kolberg, Rewahl und viele mehr.',
                                       1, inhalt, aktiv='Orte'))

    # Sonderangebote
    sonder = [h for h in hotels if h.get('sonderangebot')]
    sonder.sort(key=lambda x: preis_zahl(x['ab_preis']) or 9999)
    inhalt = page_hero('Sonderangebote', 'Ausgewählte Hotels zu besonders günstigen Preisen – solange das Kontingent reicht.',
                       [('Startseite', '../../'), ('Orte', '../'), ('Sonderangebote', '')], eyebrow='Aktuell') + f'''
  <section class="section section--tight">
    <div class="wrap">
      <div class="offers">
        {"".join(karte(h, GROESSEN, '../../') for h in sonder)}
      </div>
    </div>
  </section>
  {kontakt_band('../../')}'''
    schreiben('orte/sonderangebote/index.html', seite('Sonderangebote | Bernstein Touristik',
                                                     'Aktuelle Sonderangebote von Bernstein Touristik an der polnischen Ostsee.',
                                                     2, inhalt, aktiv='Orte'))
    return len(karten_orte)


# ---------------------------------------------------------------- Formulare

def formular(name, r, felder_extra='', danke='danke/', knopf='Nachricht senden', hinweis=''):
    return f'''<form class="form" name="{name}" method="post" action="{r}{danke}" data-netlify="true" netlify-honeypot="website">
          <input type="hidden" name="form-name" value="{name}">
          <p class="hp"><label>Bitte leer lassen <input name="website"></label></p>
          <fieldset>
            <legend>Ihre Angaben</legend>
            <div class="form__grid">
              <label>Vor- und Nachname*<input name="name" autocomplete="name" required></label>
              <label>E-Mail*<input type="email" name="email" autocomplete="email" required></label>
              <label>Telefon<input type="tel" name="telefon" autocomplete="tel"></label>
            </div>
            {felder_extra}
            <label>Ihre Nachricht{'*' if not felder_extra else ''}<textarea name="nachricht" rows="5" {'required' if not felder_extra else ''}></textarea></label>
          </fieldset>
          <label class="consent"><input type="checkbox" name="datenschutz" required> <span>Ich bin damit einverstanden, dass meine Angaben zur Bearbeitung der Anfrage und für Rückfragen gespeichert werden. Die Daten werden nicht ohne Einwilligung an Dritte weitergegeben. Es gilt die <a href="{r}datenschutzerklaerung/">Datenschutzerklärung</a>.*</span></label>
          <button class="btn btn--amber btn--lg" type="submit">{knopf}</button>
          <p class="note">* Pflichtfelder.{(' ' + hinweis) if hinweis else ''}</p>
        </form>'''


def kontakt_seite():
    r = '../'
    maps = 'https://www.openstreetmap.org/search?query=Wollankstra%C3%9Fe%20127%2C%2013187%20Berlin'
    inhalt = page_hero('Kontakt &amp; Anfahrt', 'Wir beraten Sie gerne persönlich – am Telefon, per E-Mail oder in unserem Reisebüro in Berlin-Pankow.',
                       [('Startseite', r), ('Kontakt', '')], eyebrow='Wir sind für Sie da') + f'''
  <section class="section section--tight">
    <div class="wrap kontakt-grid">
      <div>
        <div class="kontakt-cards">
          <a class="kontakt-card" href="tel:+493048490070">
            <span class="perk__icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/></svg></span>
            <span><strong>030-484 900 70</strong>Gratis-Hotline · Mo.–Fr. 9–18 Uhr, Sa. 10–15 Uhr</span>
          </a>
          <a class="kontakt-card" href="mailto:info@bernstein-touristik.de">
            <span class="perk__icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"/></svg></span>
            <span><strong>info@bernstein-touristik.de</strong>Antwort in der Regel innerhalb von 24 Stunden</span>
          </a>
          <a class="kontakt-card" href="{maps}" target="_blank" rel="noopener">
            <span class="perk__icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z"/></svg></span>
            <span><strong>Wollankstraße 127, 13187 Berlin</strong>Reisebüro nahe Rathaus Pankow · Route planen ↗</span>
          </a>
        </div>
        <div class="block">
          <h2>Willkommen bei Bernstein Touristik</h2>
          <p>Neben der großen Vielfalt an Reisen und erstklassigem Service steht Bernstein Touristik für sehr gute Qualität zu Top-Preisen. Wir präsentieren Ihnen eine handverlesene Auswahl attraktiver Orte und Hotels, die Körper und Geist guttun.</p>
          <p>Unsere 3-, 4- und 5-Sterne-Hotels kennen wir persönlich. Besonders beliebt sind Kurreisen – das klare, gesunde Ostseeklima ist Balsam für Körper und Seele. Daneben laden wir Sie herzlich zu unseren weiteren Urlaubsangeboten ein.</p>
          <p><a class="link-arrow" href="{r}bernstein-katalog/">Katalog ansehen &amp; herunterladen</a></p>
        </div>
      </div>
      <div>
        <h2>Schreiben Sie uns</h2>
        {formular('kontakt', r)}
      </div>
    </div>
  </section>'''
    schreiben('kontakt/index.html', seite('Kontakt & Anfahrt | Bernstein Touristik',
                                          'Bernstein Touristik GmbH, Wollankstraße 127, 13187 Berlin. Gratis-Hotline 030-484 900 70, Mo.–Fr. 9–18 Uhr, Sa. 10–15 Uhr.',
                                          1, inhalt, aktiv='Kontakt'))


def vip_seite():
    r = '../'
    inhalt = page_hero('VIP-Gold-Mitgliedschaft', 'Für unsere treuen Stammgäste: Nach drei gebuchten Reisen erhalten Sie den VIP-Gold-Status mit exklusiven Vorteilen.',
                       [('Startseite', r), ('VIP-Gold', '')], eyebrow='Bernstein Club') + f'''
  <section class="section section--tight">
    <div class="wrap kontakt-grid">
      <div>
        <img class="vip-banner" src="{r}img/gold-member.jpg" alt="VIP Gold Mitgliedschaft" width="298" height="70">
        <h2>Ihre Vorteile</h2>
        <ul class="vip-list">
          <li><strong>50 €</strong><span>Willkommens-Gutschein</span></li>
          <li><strong>5 %</strong><span>Frühbucher-Rabatt</span></li>
          <li><strong>Exklusiv</strong><span>Sonderangebote nur für Clubmitglieder</span></li>
        </ul>
        <p>Werden Sie Clubmitglied mit VIP-Gold-Status, nachdem Sie insgesamt drei Reisen bei uns gebucht haben. Tragen Sie sich ein – wir prüfen gerne, ob Sie den Status bereits erhalten.</p>
      </div>
      <div>
        <h2>Status prüfen lassen</h2>
        {formular('vip', r, knopf='Status prüfen lassen')}
      </div>
    </div>
  </section>'''
    schreiben('vip/index.html', seite('VIP-Gold-Mitgliedschaft | Bernstein Touristik',
                                      'VIP-Gold-Status nach drei Reisen: 50 € Willkommens-Gutschein, 5 % Frühbucher-Rabatt und exklusive Sonderangebote.',
                                      1, inhalt))


def katalog_seite():
    r = '../'
    pdf = 'Bernstein-Katalog-2025.pdf'
    inhalt = page_hero('Unser Katalog', 'Alle Hotels, Kurangebote und Preise übersichtlich zum Blättern – online ansehen oder als PDF herunterladen.',
                       [('Startseite', r), ('Katalog', '')], eyebrow='Zum Blättern') + f'''
  <section class="section section--tight">
    <div class="wrap katalog">
      <a class="katalog__cover" href="{pdf}" target="_blank" rel="noopener">
        <img src="{r}img/katalog-2025.webp" alt="Blick in den Bernstein-Touristik-Katalog" width="600" height="843">
      </a>
      <div>
        <h2>Bernstein Katalog 2025</h2>
        <p>Auf 102 Seiten finden Sie unsere Hotels an der polnischen Ostsee mit Beschreibungen, Leistungen und Preisen. Gerne schicken wir Ihnen den Katalog auch kostenlos per Post – rufen Sie uns einfach an.</p>
        <div class="contact__actions">
          <a class="btn btn--amber btn--lg" href="{pdf}" target="_blank" rel="noopener">Katalog öffnen (PDF, 23 MB)</a>
          <a class="btn btn--outline btn--lg" href="#bestellen">Per Post bestellen</a>
        </div>
        <p class="note">Tipp: Aktuelle Preise finden Sie auch direkt auf den <a href="{r}hotels/">Hotelseiten</a>.</p>
      </div>
    </div>
  </section>

  <section class="section section--sand section--tight" id="bestellen">
    <div class="wrap kontakt-grid">
      <div>
        <p class="eyebrow">Kostenlos per Post</p>
        <h2>Katalog bestellen</h2>
        <p>Sie blättern lieber im gedruckten Katalog? Wir schicken ihn Ihnen kostenlos nach Hause. Einfach das Formular ausfüllen – oder anrufen: <a href="tel:+493048490070">030 48 49 00 70</a>.</p>
      </div>
      <form class="form" name="katalog-bestellung" method="post" action="{r}danke/" data-netlify="true" netlify-honeypot="website">
        <input type="hidden" name="form-name" value="katalog-bestellung">
        <p class="hp"><label>Bitte leer lassen <input name="website"></label></p>
        <fieldset>
          <legend>Versandadresse</legend>
          <label>Vor- und Nachname*<input name="name" autocomplete="name" required></label>
          <label>Straße und Hausnummer*<input name="strasse" autocomplete="street-address" required></label>
          <div class="form__grid">
            <label>Postleitzahl*<input name="plz" inputmode="numeric" autocomplete="postal-code" required></label>
            <label>Ort*<input name="ort" autocomplete="address-level2" required></label>
          </div>
          <label>E-Mail (für Rückfragen)<input type="email" name="email" autocomplete="email"></label>
        </fieldset>
        <label class="consent"><input type="checkbox" name="datenschutz" required> <span>Ich bin damit einverstanden, dass meine Angaben zum Versand des Katalogs gespeichert werden. Es gilt die <a href="{r}datenschutzerklaerung/">Datenschutzerklärung</a>.*</span></label>
        <button class="btn btn--amber btn--lg" type="submit">Katalog kostenlos bestellen</button>
      </form>
    </div>
  </section>
  {kontakt_band(r)}'''
    schreiben('bernstein-katalog/index.html', seite('Katalog | Bernstein Touristik',
                                                   'Der Bernstein-Touristik-Katalog mit allen Hotels an der polnischen Ostsee – online ansehen oder als PDF herunterladen.',
                                                   1, inhalt, aktiv='Katalog'))


def karte_seite():
    r = '../'
    embed = 'https://www.google.com/maps/d/embed?mid=14tEY2S4TSa5b-0uJMqxwRBTbKnLA3Y6R'
    orte = ''.join(f'<li><a href="{r}orte/{s}/">{esc(k)}</a></li>' for s, (n, k) in ORTE.items())
    inhalt = page_hero('Hotelkarte', 'Alle unsere Hotels an der polnischen Ostseeküste auf einen Blick.',
                       [('Startseite', r), ('Hotelkarte', '')], eyebrow='Übersicht') + f'''
  <section class="section section--tight">
    <div class="wrap">
      <div class="map-consent" data-src="{embed}">
        <img src="{r}img/karte-ostsee.jpg" alt="" width="1200" height="498">
        <div class="map-consent__box">
          <h2>Interaktive Karte laden</h2>
          <p>Die Karte wird von Google Maps bereitgestellt. Beim Laden werden Daten (u. a. Ihre IP-Adresse) an Google übertragen. Mehr dazu in unserer <a href="{r}datenschutzerklaerung/">Datenschutzerklärung</a>.</p>
          <button class="btn btn--amber" type="button">Karte anzeigen</button>
        </div>
      </div>
      <h2 class="h3" style="margin-top:40px">Hotels nach Ort</h2>
      <ul class="chips">{orte}</ul>
    </div>
  </section>'''
    schreiben('karte/index.html', seite('Hotelkarte | Bernstein Touristik',
                                        'Karte aller Bernstein-Touristik-Hotels an der polnischen Ostsee von Swinemünde bis Danzig.',
                                        1, inhalt, aktiv='Hotelkarte'))


def suche_seite(hotels):
    r = '../'
    index = []
    for h in hotels:
        if h['slug'] in HANDGEBAUT:
            bild = HANDGEBAUT[h['slug']]['bild'].replace('../', '', 1)
        elif f'{h["bild"]}/01' in GROESSEN:
            bild = f'img/hotels/{h["bild"]}/01-klein.webp'
        else:
            bild = 'img/hero.jpg'
        text = ' '.join(re.sub(r'<[^>]+>', ' ', json.dumps(a['bloecke'], ensure_ascii=False)) for a in h['abschnitte'])
        text = re.sub(r'[^\wäöüÄÖÜß ]+', ' ', html.unescape(text)).lower()
        index.append({'s': h['slug'], 'n': h['name'], 'o': h['ort'], 'on': h['ort_kurz'], 'p': h['ab_preis'],
                      'st': h['sterne'], 'b': bild, 'so': bool(h.get('sonderangebot')),
                      't': ' '.join(sorted(set(w for w in text.split() if len(w) > 3)))})
    schreiben('suche/hotels.json', json.dumps(index, ensure_ascii=False, separators=(',', ':')))
    optionen = ''.join(f'<option value="{s}">{esc(k)}</option>' for s, (n, k) in ORTE.items())
    inhalt = page_hero('Hotels suchen', '', [('Startseite', r), ('Suche', '')], eyebrow='Ihr Bernstein-Urlaub') + f'''
  <section class="section section--tight">
    <div class="wrap">
      <form class="search search--page" action="./" method="get" role="search">
        <label class="search__field">
          <span>Ostseebad</span>
          <select name="ort" aria-label="Ostseebad wählen"><option value="">Alle Ostseebäder</option>{optionen}</select>
        </label>
        <label class="search__field search__field--grow">
          <span>Hotel oder Stichwort</span>
          <input type="search" name="q" placeholder="z. B. Spa, Kur, Hallenbad, Radisson …">
        </label>
        <button class="btn btn--amber search__btn" type="submit">Suchen</button>
      </form>
      <p class="search-info" id="suche-info" aria-live="polite"></p>
      <div class="offers offers--4" id="suche-ergebnisse"></div>
    </div>
  </section>'''
    schreiben('suche/index.html', seite('Hotels suchen | Bernstein Touristik',
                                        'Finden Sie Ihr Hotel an der polnischen Ostsee – nach Ort, Name oder Ausstattung.',
                                        1, inhalt, robots='noindex'))


# ---------------------------------------------------------------- Rechtstexte

def sauber(fragment):
    """Rechtstexte der alten Seite auf einfache Auszeichnung reduzieren."""
    s = re.sub(r'(?is)<(script|style|noscript|form|img|figure|iframe)[^>]*>.*?</\1>', '', fragment)
    s = re.sub(r'(?is)<img[^>]*>', '', s)
    s = re.sub(r'(?i)<h1\b[^>]*>', '<h2>', s).replace('</h1>', '</h2>')
    s = re.sub(r'(?i)<(/?)(h[5-6])\b[^>]*>', r'<\1h4>', s)

    def tag(m):
        schluss, name, attrs = m.group(1), m.group(2).lower(), m.group(3) or ''
        if name in ('b',):
            name = 'strong'
        if name in ('i',):
            name = 'em'
        if name not in ('h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'strong', 'em', 'br', 'a', 'table', 'tr', 'td', 'th', 'tbody', 'thead'):
            return ''
        if name == 'a' and not schluss:
            href = re.search(r'href="([^"]+)"', attrs)
            return f'<a href="{href.group(1)}">' if href else '<a>'
        return f'<{schluss}{name}>'
    s = re.sub(r'<(/?)([a-zA-Z0-9]+)([^>]*)>', tag, s)
    s = s.replace('\xa0', ' ').replace('&nbsp;', ' ')
    s = re.sub(r'<p>\s*</p>|<strong>\s*</strong>|<li>\s*</li>', '', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s.strip()


def rechtsseite(alter_ordner, datei, slug, titel, zusatz_vorne='', zusatz_hinten=''):
    s = open(os.path.join(alter_ordner, datei), encoding='utf-8').read()
    m = re.search(r'(?is)<main.*?</main>', s)
    s = m.group(0)
    s = re.sub(r'(?is)<div class="suche">.*?</section>\s*</div>\s*</div>\s*</div>', '', s, count=1)
    # nur den eigentlichen Inhaltsbereich
    inhalt = re.search(r'(?is)<div class="entry-content"[^>]*>(.*)</div>\s*</article>', s) or \
        re.search(r'(?is)<div class="inside-article"[^>]*>(.*)</div>\s*</article>', s)
    roh = inhalt.group(1) if inhalt else s
    text = sauber(roh)
    text = re.sub(r'(?is)^.*?Finden Sie Ihren Bernstein Urlaub.*?Suchen\s*', '', text)
    seite_html = page_hero(titel, '', [('Startseite', '../'), (titel, '')]) + f'''
  <section class="section section--tight">
    <div class="wrap legal">
      {zusatz_vorne}
      {text}
      {zusatz_hinten}
    </div>
  </section>'''
    schreiben(f'{slug}/index.html', seite(f'{titel} | Bernstein Touristik', f'{titel} der Bernstein Touristik GmbH, Berlin.', 1, seite_html))


DATENSCHUTZ_NEU = '''<div class="legal-draft">
        <p class="legal-draft__label">Entwurf – vor Veröffentlichung rechtlich prüfen lassen</p>
        <h2>Hinweise zur neuen Website</h2>
        <h3>Hosting</h3>
        <p>Diese Website wird bei Netlify, Inc. (San Francisco, USA) gehostet. Beim Aufruf der Website verarbeitet Netlify technisch notwendige Daten (u. a. IP-Adresse, Datum und Uhrzeit des Abrufs, aufgerufene Seite, Browsertyp), um die Website auszuliefern und vor Angriffen zu schützen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO.</p>
        <h3>Anfrage- und Kontaktformulare</h3>
        <p>Wenn Sie uns über ein Formular eine Anfrage senden, werden Ihre Angaben über den Formulardienst von Netlify an uns übermittelt und dort gespeichert, um Ihre Anfrage zu bearbeiten. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO (vorvertragliche Maßnahmen) bzw. Ihre Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO.</p>
        <h3>Keine Cookies, keine Tracking-Dienste</h3>
        <p>Diese Website setzt keine Cookies und verwendet keine Analyse- oder Werbedienste. Die Schriftarten sind lokal auf unserem Server eingebunden; es wird keine Verbindung zu Google Fonts aufgebaut.</p>
        <h3>Google Maps (Hotelkarte)</h3>
        <p>Auf der Seite „Hotelkarte“ können Sie eine Karte von Google Maps (Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland) laden. Die Karte wird erst nach Ihrem Klick geladen; erst dann werden Daten wie Ihre IP-Adresse an Google übertragen. Rechtsgrundlage ist Ihre Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO.</p>
        <h3>Externe Links</h3>
        <p>Beim Klick auf den Link „Route planen“ verlassen Sie unsere Website und gelangen zu OpenStreetMap. Für die dortige Datenverarbeitung ist der jeweilige Anbieter verantwortlich.</p>
      </div>'''


def rechtsseiten(alter_ordner):
    rechtsseite(alter_ordner, 'impressum.html', 'impressum', 'Impressum')
    rechtsseite(alter_ordner, 'agb.html', 'agb', 'Allgemeine Reisebedingungen (AGB)')
    rechtsseite(alter_ordner, 'datenschutzerklaerung.html', 'datenschutzerklaerung', 'Datenschutzerklärung',
                zusatz_vorne=DATENSCHUTZ_NEU)


# ---------------------------------------------------------------- Links umstellen

# Einheitliche Schreibweisen / Korrekturen aus der Korrekturliste (auf alle Seiten angewendet)
TEXT_ERSETZUNGEN = [
    ('030-484 900 70', '030 48 49 00 70'),
    ('030-48 49 00 70', '030 48 49 00 70'),
    ('Fax: +49 (0) 30 48 49 00 7 -29', 'Fax: 030 48 49 00 729'),
    ('Telefon (030) -484 9007-0', 'Telefon 030 48 49 00 70'),
    ('Telefax (030) -484 9007-29', 'Telefax 030 48 49 00 729'),
    ('© <span id="jahr">', '© 2016–<span id="jahr">'),
    ('Copyright 2016 Bernstein Touristik GmbH.', '© 2016–2026 Bernstein Touristik GmbH.'),
    ('Festpreise in € pro Person. Irrtümer vorbehalten. Abbildungen ähnlich.',
     'Preise ab, pro Person, freibleibend und vorbehaltlich Verfügbarkeit. Irrtümer vorbehalten. Abbildungen ähnlich.'),
    ('Preisgünstige Angebote mit Festpreisen pro Person', 'Preisgünstige Angebote mit transparenten Preisen pro Person'),
    ('30 Tage vor Reisebeginn kostenlos umbuchen', 'Umbuchung bis 30 Tage vor Reisebeginn gegen Gebühr'),
    ('Boziane Gniazdo (STORCHENNEST)', 'Bocianie Gniazdo (Storchennest)'),
    ('Boziane Gniazdo', 'Bocianie Gniazdo'),
    ('Hotel El Pak', 'Hotel El Park'),
    ('Radisson Blue', 'Radisson Blu'),
    ('Grossmöllen', 'Großmöllen'),
]


ZIELE = ['karte', 'bernstein-katalog', 'kontakt', 'impressum', 'agb', 'datenschutzerklaerung', 'vip']


def links_umstellen():
    """Ersetzt in allen Seiten die Links auf die alte Website durch die neuen Seiten."""
    geaendert = 0
    for wurzel, ordner, dateien in os.walk(WURZEL):
        if '_werkzeug' in wurzel:
            continue
        for d in dateien:
            if not d.endswith('.html'):
                continue
            pfad = os.path.join(wurzel, d)
            tiefe = os.path.relpath(wurzel, WURZEL).count(os.sep) + (0 if wurzel == WURZEL else 1)
            r = rel(tiefe) or ''
            s = open(pfad, encoding='utf-8').read()
            alt = s
            for a, b in TEXT_ERSETZUNGEN:
                s = s.replace(a, b)
            # umbenannte Hotel-Adressen
            for a, b in SLUG_NEU.items():
                if a != b:
                    # nur Seiten-Links, nicht die Bildordner (img/hotels/<alter-slug>/)
                    s = re.sub(r'(?<!img/)hotels/' + re.escape(a) + '/', f'hotels/{b}/', s)
            s = re.sub(re.escape(ALT) + r'/orte/([a-z0-9-]+)/', lambda m: f'{r}orte/{m.group(1)}/', s)
            for z in ZIELE:
                s = s.replace(f'{ALT}/{z}/', f'{r}{z}/')
            s = s.replace(f'{ALT}/hotels/', f'{r}hotels/')
            # Suchformular der Startseite -> eigene Suche
            s = s.replace(f'action="{ALT}/"', f'action="{r}suche/"')
            # Navigation: Anker -> eigene Seiten
            s = s.replace(f'<li><a href="{r}#orte">Orte</a></li>', f'<li><a href="{r}orte/">Orte</a></li>')
            s = s.replace(f'<li><a href="{r}#kontakt">Kontakt</a></li>', f'<li><a href="{r}kontakt/">Kontakt</a></li>')
            s = s.replace('<li><a href="#orte">Orte</a></li>', '<li><a href="orte/">Orte</a></li>')
            s = s.replace('<li><a href="#kontakt">Kontakt</a></li>', '<li><a href="kontakt/">Kontakt</a></li>')
            if s != alt:
                open(pfad, 'w', encoding='utf-8').write(s)
                geaendert += 1
    # Suchindex ebenfalls korrigieren
    pfad = os.path.join(WURZEL, 'suche', 'hotels.json')
    if os.path.exists(pfad):
        t = open(pfad, encoding='utf-8').read()
        for a, b in TEXT_ERSETZUNGEN:
            t = t.replace(a, b)
        open(pfad, 'w', encoding='utf-8').write(t)
    return geaendert


GROESSEN = {}


def main():
    global GROESSEN
    GROESSEN = json.load(open(os.path.join(HIER, 'bildgroessen.json')))
    hotels = json.load(open(os.path.join(HIER, 'hotels.json'), encoding='utf-8'))
    auslassen = set(json.load(open(os.path.join(HIER, 'auslassen.json')))) - set(HANDGEBAUT)
    hotels = anpassen([h for h in hotels if h['slug'] not in auslassen])
    n = orte_seiten(hotels)
    kontakt_seite()
    vip_seite()
    katalog_seite()
    karte_seite()
    suche_seite(hotels)
    if len(sys.argv) > 1:
        rechtsseiten(sys.argv[1])
    print(n, 'Orte + Übersicht, Sonderangebote, Kontakt, VIP, Katalog, Karte, Suche' + (', Rechtstexte' if len(sys.argv) > 1 else ''))
    print(links_umstellen(), 'Dateien mit umgestellten Links')


if __name__ == '__main__':
    main()
