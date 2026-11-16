#!/usr/bin/env python3
"""Erzeugt aus hotels.json die Hotel-Detailseiten und die Hotelübersicht.

Aufruf:  python3 hotels_bauen.py
Vorlage für Kopf- und Fußbereich ist die handgebaute Seite
hotels/radisson-blu-resort-swinemuende/index.html.
"""
import html
import json
import os
import re

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.normpath(os.path.join(HIER, '..'))
HOTELS_DIR = os.path.join(WURZEL, 'hotels')
VORLAGE = os.path.join(HOTELS_DIR, 'radisson-blu-resort-swinemuende', 'index.html')
ALT = 'https://www.bernstein-touristik.de'

# Die handgebaute Radisson-Seite wird nicht überschrieben, steht aber in der Übersicht.
HANDGEBAUT = {
    'radisson-blu-resort-swinemuende': {
        'bild': '../img/hotels/radisson-blu/hotel-aussen-klein.jpg',
    },
}


def esc(s):
    return html.escape(s or '', quote=True)


def lade():
    hotels = json.load(open(os.path.join(HIER, 'hotels.json'), encoding='utf-8'))
    auslassen = set(json.load(open(os.path.join(HIER, 'auslassen.json'))))
    groessen = json.load(open(os.path.join(HIER, 'bildgroessen.json')))
    return hotels, auslassen, groessen


def vorlage_teile():
    s = open(VORLAGE, encoding='utf-8').read()
    kopf = s[s.index('<a class="skip"'):s.index('<main id="inhalt">')]
    fuss = s[s.index('</main>') + len('</main>'):s.index('<!-- Mobile Buchungsleiste -->')]
    lightbox = s[s.index('<!-- Bildergalerie (Lightbox) -->'):s.index('<script>')]
    anreise = s[s.index('<section class="block" id="anreise">'):s.index('<!-- Anfrage -->')]
    formular = s[s.index('<!-- Anfrage -->'):s.index('</article>')]
    seitenleiste = s[s.index('<!-- Seitenleiste -->'):s.index('<!-- Weitere Hotels -->')]
    # Radisson-spezifische Angaben aus der Anreise entfernen
    anreise = anreise.replace(
        'Strecke: Berlin – Stettin (Szczecin) – Swinemünde. Parkplatz am Hotel: 15 € pro Tag.',
        'Strecke: Berlin – Stettin (Szczecin) – polnische Ostseeküste. Parkmöglichkeiten siehe Buchungsoptionen.')
    return kopf, fuss, lightbox, anreise, formular, seitenleiste


def head(titel, beschreibung, tiefe='../../', robots=None):
    return f'''<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(titel)}</title>
  <meta name="description" content="{esc(beschreibung)}">
  {'<meta name="robots" content="' + robots + '">' if robots else ''}
  <meta name="theme-color" content="#13283b">
  <link rel="icon" href="{tiefe}img/favicon.png">
  <link rel="preload" href="{tiefe}fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{tiefe}fonts/fraunces.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{tiefe}css/style.css">
</head>
<body>

'''


def plain(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()


def als_liste(absatz_html):
    """Lange Aufzählungen mit Kommas als Liste darstellen."""
    t = korrektur(plain(absatz_html))
    # fehlende Kommas aus dem Originaltext
    t = re.sub(r'(Salzgrotte) (Arztkonsultation)', r'\1, \2', t)
    t = re.sub(r'(“) (Kinderspielplatz)', r'\1, \2', t)
    if t.count(',') < 5:
        return None
    t = re.sub(r'\s*\.\s*$', '', t)
    teile = [x.strip(' .;') for x in re.split(r',(?![^()]*\))', t)]
    teile = [x for x in teile if x]
    if len(teile) < 6:
        return None
    if sum(len(x) for x in teile) / len(teile) > 55 or max(len(x) for x in teile) > 140:
        return None
    # "Trocken-, Rotlicht- und Dampfsauna" wieder zusammenfügen
    zusammen = []
    for x in teile:
        if zusammen and zusammen[-1].endswith('-'):
            zusammen[-1] = zusammen[-1] + ', ' + x
        else:
            zusammen.append(x)
    teile = [re.sub(r'^(und|sowie)\s+', '', x.lstrip('-–• ').strip(), flags=re.I) for x in zusammen]
    teile = [korrektur(x) for x in teile if x]
    return [x[0].upper() + x[1:] if x else x for x in teile]


TIPPFEHLER = {
    'Artkonsultation': 'Arztkonsultation',
    'Jaccuzzi': 'Jacuzzi',
    'Wellenss': 'Wellness',
    'familengeführt': 'familiengeführt',
}


def korrektur(t):
    for alt, neu in TIPPFEHLER.items():
        t = t.replace(alt, neu)
    t = re.sub(r"(?:''|‘‘|’’|\"|“)([^'‘’\"“”]+?)(?:''|‘‘|’’|\"|”)", r'„\1“', t)
    return t


def bloecke_html(bloecke, key):
    out = []
    for b in bloecke:
        if b['typ'] == 'zwischen':
            out.append(f'<h3>{esc(b["text"].rstrip(":"))}</h3>')
        elif b['typ'] == 'liste':
            out.append('<ul class="checks">' + ''.join(f'<li>{p}</li>' for p in b['punkte']) + '</ul>')
        elif b['typ'] == 'absatz':
            liste = als_liste(b['html']) if key in ('ausstattung', 'wellness', 'zimmer', 'lage') else None
            if liste and key in ('ausstattung', 'wellness'):
                klasse = 'features features--small' if key == 'wellness' else 'features'
                out.append(f'<ul class="{klasse}">' + ''.join(f'<li>{esc(x)}</li>' for x in liste) + '</ul>')
            else:
                out.append(f'<p>{b["html"]}</p>')
    return '\n        '.join(out)


def tausender(p):
    """'1 008 €' -> '1.008 €'"""
    return re.sub(r'(\d)\s(\d{3})\b', r'\1.\2', p or '')


def preis_zahl(p):
    try:
        return float(re.sub(r'\s', '', p.replace('€', '').replace('.', '')).replace(',', '.'))
    except (ValueError, AttributeError):
        return None


def sterne_html(n):
    if not n:
        return ''
    return f'<span class="stars" aria-label="{n} Sterne">{"★" * n}</span>'


def tags(h):
    t = []
    alles = plain(json.dumps(h['abschnitte'], ensure_ascii=False)).lower()
    if h['sterne']:
        t.append(f'{h["sterne"]}-Sterne-Hotel')
    if h.get('sonderangebot'):
        t.append('Sonderangebot')
    if 'vollpension' in alles and 'halbpension' not in alles:
        t.append('Vollpension')
    elif 'halbpension' in alles or 'abendbuffet' in alles or 'abendessen' in alles:
        t.append('Halbpension')
    if re.search(r'hallenbad|schwimmbad|schwimmbecken|pool', alles):
        t.append('Schwimmbad')
    if re.search(r'kuranwendung|kurabteilung|kurreise|arztkonsultation|ärztlich', alles):
        t.append('Kuranwendungen')
    if 'sauna' in alles:
        t.append('Sauna')
    if re.search(r'direkt am strand|direkte strandlage|direkt an der promenade|direkt an der strandpromenade', alles):
        t.insert(0, 'Strandnah')
    return t[:6]


def galerie(h, groessen, tiefe='../../'):
    slug = h['slug']
    n = min(12, len(h['bilder_quelle']))
    nrs = [i for i in range(1, n + 1) if f'{slug}/{i:02d}' in groessen]
    if not nrs:
        return '', '[]'
    pfad = f'{tiefe}img/hotels/{slug}/'
    zeige = nrs[:5]
    teile = []
    for pos, nr in enumerate(zeige):
        w, hh = groessen[f'{slug}/{nr:02d}']
        alt = f'{h["name"]} – Foto {nr}'
        if pos == 0:
            teile.append(f'''<a class="gallery__item gallery__item--main" href="{pfad}{nr:02d}.webp" data-index="{pos}">
        <img src="{pfad}{nr:02d}.webp" alt="{esc(alt)}" width="{w}" height="{hh}" fetchpriority="high">
      </a>''')
        else:
            mehr = pos == len(zeige) - 1 and len(nrs) > 1
            zusatz = f'''
        <span class="gallery__count"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 4h7v7H4zm9 0h7v7h-7zM4 13h7v7H4zm9 0h7v7h-7z"/></svg>Alle {len(nrs)} Fotos</span>''' if mehr else ''
            teile.append(f'''<a class="gallery__item{' gallery__item--more' if mehr else ''}" href="{pfad}{nr:02d}.webp" data-index="{pos}"><img src="{pfad}{nr:02d}-klein.webp" alt="{esc(alt)}" loading="lazy" width="560" height="{round(560 * hh / w)}">{zusatz}</a>''')
    html_ = f'<div class="gallery gallery--{len(zeige)}" id="galerie">\n      ' + '\n      '.join(teile) + '\n    </div>'
    bilder = json.dumps([[f'{nr:02d}', f'{h["name"]} – Foto {nr}'] for nr in nrs], ensure_ascii=False)
    return html_, f"{{ pfad: '{pfad}', endung: '.webp', bilder: {bilder} }}"


def preise_html(h):
    p = h['preise']
    if not p:
        return f'''<section class="block" id="preise">
        <h2>Termine &amp; Preise</h2>
        <div class="on-request">
          <p><strong>Preise auf Anfrage.</strong> Die aktuellen Termine und Preise für {esc(h["name"])} nennen wir Ihnen gerne persönlich – telefonisch oder per Anfrageformular.</p>
          <p class="on-request__price">1 Woche schon ab <strong>{esc(h["ab_preis"])} €</strong> pro Person</p>
          <div class="contact__actions"><a class="btn btn--amber" href="#anfrage">Preis anfragen</a><a class="btn btn--outline" href="tel:+493048490070">030-484 900 70</a></div>
        </div>
      </section>'''
    titel = f'Termine &amp; Preise {esc(p["jahr"])}'.strip()
    kopf = ''.join(f'<th scope="col">{n} Nächte</th>' for n in p['naechte'])
    # günstigsten Monat markieren (nach der 7-Nächte-Spalte, sonst erste Spalte)
    spalte = p['naechte'].index(7) if 7 in p['naechte'] else 0
    werte = [preis_zahl(z['preise'][spalte]) if spalte < len(z['preise']) else None for z in p['zeilen']]
    gueltig = [w for w in werte if w]
    best = min(gueltig) if gueltig else None
    zeilen = []
    for z, w in zip(p['zeilen'], werte):
        ist_best = best is not None and w == best and werte.count(best) <= 2
        pill = ' <span class="pill">Günstig</span>' if ist_best else ''
        zellen = ''.join(f'<td>{esc(tausender(x)) or "–"}</td>' for x in z['preise'])
        zeilen.append(f'<tr{" class=\"is-best\"" if ist_best else ""}><th scope="row">{esc(z["monat"])}{pill}</th>{zellen}</tr>')
    extras = ''
    if h['extras']:
        eintraege = []
        for label, wert in h['extras']:
            if wert:
                eintraege.append(f'<div><dt>{esc(label)}</dt><dd>{esc(wert)}</dd></div>')
            else:
                eintraege.append(f'<div class="extras__note"><dt>{esc(label)}</dt><dd></dd></div>')
        extras = f'''
        <h3>Zusätzliche Buchungsoptionen</h3>
        <dl class="extras">
          {"".join(eintraege)}
        </dl>'''
    alt_hinweis = ''
    if p['jahr'] and re.match(r'20(1\d|2[0-5])$', p['jahr']):
        alt_hinweis = f'<p class="note"><strong>Hinweis:</strong> Diese Preise gelten für {esc(p["jahr"])}. Aktuelle Preise erfahren Sie gerne telefonisch oder per Anfrage.</p>'
    return f'''<section class="block" id="preise">
        <h2>{titel}</h2>
        <p>Pro Person im Doppelzimmer.</p>
        {alt_hinweis}
        <div class="table-wrap">
          <table class="prices">
            <thead><tr><th scope="col">Anreise im</th>{kopf}</tr></thead>
            <tbody>
              {"".join(zeilen)}
            </tbody>
          </table>
        </div>{extras}
      </section>'''


def leistungen_html(h):
    inkl = next((a for a in h['abschnitte'] if a['key'] == 'inklusiv'), None)
    if not inkl and not h['pakete']:
        return ''
    karten = []
    if inkl:
        inhalt = bloecke_html(inkl['bloecke'], 'inklusiv')
        karten.append(f'''<div class="package package--incl">
            <p class="package__label">Im Reisepreis enthalten</p>
            {inhalt}
          </div>''')
    for p in h['pakete']:
        preis = f'<p class="package__price"><strong>+{esc(p["preis"])} €</strong> p. P. / Woche</p>' if p['preis'] else ''
        punkte = ''.join(f'<li>{x}</li>' for x in p['punkte'])
        karten.append(f'''<div class="package">
            <p class="package__label">{esc(p["titel"])} zubuchbar</p>
            {preis}
            {'<ul>' + punkte + '</ul>' if punkte else '<p>' + esc(p['text']) + '</p>'}
          </div>''')
    hinweise = ''.join(f'<p class="note">{x}</p>' for x in h['hinweise'])
    spalten = 'packages' + (' packages--wide' if len(karten) <= 2 else '')
    return f'''<section class="block" id="leistungen">
        <h2>Ihre Leistungen</h2>
        <div class="{spalten}">
          {"".join(karten)}
        </div>
        {hinweise}
      </section>'''


def beschreibung(h):
    for a in h['abschnitte']:
        for b in a['bloecke']:
            if b['typ'] == 'absatz':
                t = plain(b['html'])
                if len(t) > 60:
                    return (t[:150].rsplit(' ', 1)[0] + ' …') if len(t) > 155 else t
    return f'{h["name"]} im {h["ort_name"]} – Urlaub an der polnischen Ostsee mit Bernstein Touristik.'


def karte(h, groessen, tiefe, mit_ort=True):
    slug = h['slug']
    if slug in HANDGEBAUT:
        bild = HANDGEBAUT[slug]['bild'].replace('../', tiefe, 1)
    elif f'{slug}/01' in groessen:
        bild = f'{tiefe}img/hotels/{slug}/01-klein.webp'
    else:
        bild = f'{tiefe}img/hero.jpg'
    sterne = sterne_html(h['sterne'])
    ort = f'<p class="offer__place">{esc(h["ort_name"])}</p>' if mit_ort else ''
    badge = '<span class="badge">Sonderangebot</span>' if h.get('sonderangebot') else ''
    return f'''<article class="offer" data-ort="{esc(h['ort'] or '')}">
          <a class="offer__media" href="{tiefe}hotels/{slug}/" tabindex="-1" aria-hidden="true"><img src="{bild}" alt="" loading="lazy" width="560" height="420">{badge}</a>
          <div class="offer__body">
            {ort}
            <h3><a href="{tiefe}hotels/{slug}/">{esc(h["name"])}</a> {sterne}</h3>
            <div class="offer__foot">
              <p class="price"><span>1 Woche schon ab</span><strong>{esc(h["ab_preis"])} €</strong><span>pro Person</span></p>
              <a class="btn btn--navy" href="{tiefe}hotels/{slug}/">Ansehen</a>
            </div>
          </div>
        </article>'''


def seite(h, alle, groessen, teile):
    kopf, fuss, lightbox, anreise, formular, seitenleiste = teile
    name = h['name']
    ort_url = f'{ALT}/orte/{h["ort"]}/' if h['ort'] else f'{ALT}/hotels/'
    gal_html, gal_js = galerie(h, groessen)
    ab = h['ab_preis']

    abschnitte = []
    intro = ''
    subnav = []
    for a in h['abschnitte']:
        if a['key'] == 'inklusiv':
            continue
        inhalt = bloecke_html(a['bloecke'], a['key'])
        if a['key'] == 'allgemein':
            intro = f'<div class="block block--intro lead">{inhalt}</div>'
            continue
        anker = {'wellness': 'wellness', 'lage': 'lage', 'zimmer': 'zimmer', 'ausstattung': 'ausstattung', 'verpflegung': 'verpflegung'}.get(a['key'], a['key'])
        subnav.append((anker, a['titel']))
        abschnitte.append(f'''<section class="block" id="{anker}">
        <h2>{esc(a["titel"])}</h2>
        {inhalt}
      </section>''')
    leistungen = leistungen_html(h)
    if leistungen:
        subnav.append(('leistungen', 'Leistungen'))
    subnav += [('preise', 'Preise'), ('anreise', 'Anreise'), ('anfrage', 'Anfrage')]

    tag_html = ''.join(f'<li>{esc(t)}</li>' for t in tags(h))
    sterne = sterne_html(h['sterne'])

    # Weitere Hotels im selben Ort
    gleiche = [x for x in alle if x['ort'] == h['ort'] and x['slug'] != h['slug']]
    gleiche.sort(key=lambda x: (not x.get('sonderangebot'), preis_zahl(x['ab_preis']) or 9999))
    weitere = ''
    if gleiche:
        weitere = f'''<section class="section section--sand">
    <div class="wrap">
      <div class="section__head">
        <div>
          <p class="eyebrow">Ebenfalls in {esc(h["ort_kurz"])}</p>
          <h2>Weitere Hotels</h2>
        </div>
        <a class="link-arrow" href="../../orte/{esc(h["ort"] or "")}/">Alle Hotels in {esc(h["ort_kurz"])}</a>
      </div>
      <div class="offers">
        {"".join(karte(x, groessen, '../../') for x in gleiche[:3])}
      </div>
    </div>
  </section>'''

    form = formular.replace('value="Radisson Blu Resort, Swinemünde"', f'value="{esc(name)}, {esc(h["ort_kurz"])}"')
    leiste = seitenleiste.replace('449 €', f'{esc(ab)} €').replace('7 Nächte · Halbpension · Doppelzimmer', 'pro Person · Doppelzimmer')
    kopf_ = kopf.replace(' aria-current="page"', '').replace('<li><a href="../">Hotels</a></li>', '<li><a href="../" aria-current="page">Hotels</a></li>')
    fuss_ = fuss

    return head(f'{name} – {h["ort_kurz"]} | Bernstein Touristik', beschreibung(h)) + kopf_ + f'''<main id="inhalt">

  <div class="wrap">
    <nav class="crumbs" aria-label="Brotkrümelnavigation">
      <a href="../../">Startseite</a>
      <span aria-hidden="true">›</span>
      <a href="../">Hotels</a>
      <span aria-hidden="true">›</span>
      <a href="../../orte/{esc(h["ort"] or "")}/">{esc(h["ort_name"])}</a>
      <span aria-hidden="true">›</span>
      <span aria-current="page">{esc(name)}</span>
    </nav>

    <div class="hotel-head">
      <div>
        <p class="hotel-head__place">
          <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z"/></svg>
          {esc(h["ort_name"])}
        </p>
        <h1>{esc(name)} {sterne}</h1>
        <ul class="tags">{tag_html}</ul>
      </div>
      <div class="hotel-head__price">
        <span>1 Woche schon ab</span>
        <strong>{esc(ab)} €</strong>
        <span>pro Person</span>
      </div>
    </div>

    {gal_html}
  </div>

  <div class="wrap hotel-layout">
    <article class="hotel-main">

      <nav class="subnav" aria-label="Inhalt dieser Seite">
        {"".join(f'<a href="#{a}">{esc(t)}</a>' for a, t in subnav)}
      </nav>

      {intro}

      {"".join(abschnitte)}

      {leistungen}

      {preise_html(h)}

      {anreise}
      {form}</article>

    {leiste}  </div>

  {weitere}

</main>''' + fuss_ + f'''<!-- Mobile Buchungsleiste -->
<div class="sticky-book">
  <div><span>ab</span> <strong>{esc(ab)} €</strong> <span>p. P./Woche</span></div>
  <a class="btn btn--amber" href="#anfrage">Anfragen</a>
</div>

{lightbox}<script>
  window.GALERIE = {gal_js};
</script>
<script src="../../js/main.js" defer></script>
</body>
</html>
'''


def uebersicht(alle, groessen, teile, radisson):
    kopf, fuss = teile[0], teile[1]
    liste = alle + [radisson]
    from hotels_auslesen import ORTE
    gruppen = []
    chips = ['<li><button class="chip is-active" data-filter="">Alle Orte</button></li>']
    for ort, (name, kurz) in ORTE.items():
        hs = [x for x in liste if x['ort'] == ort]
        if not hs:
            continue
        hs.sort(key=lambda x: (not x.get('sonderangebot'), preis_zahl(x['ab_preis']) or 9999))
        chips.append(f'<li><button class="chip" data-filter="{ort}">{esc(kurz)} <span>{len(hs)}</span></button></li>')
        gruppen.append(f'''<section class="ort-gruppe" id="{ort}" data-ort="{ort}">
        <div class="ort-gruppe__head"><h2>{esc(name)}</h2><span>{len(hs)} {"Hotel" if len(hs) == 1 else "Hotels"}</span></div>
        <div class="offers offers--4">
          {"".join(karte(x, groessen, '../', mit_ort=False) for x in hs)}
        </div>
      </section>''')
    kopf_ = kopf.replace(' aria-current="page"', '').replace('<li><a href="../">Hotels</a></li>', '<li><a href="./" aria-current="page">Hotels</a></li>')
    kopf_ = kopf_.replace('../../', '../')
    kopf_ = kopf_.replace('href="#anfrage">Unverbindlich anfragen', 'href="tel:+493048490070">Kostenlos beraten lassen')
    fuss_ = fuss.replace('<li><a href="../">Hotels</a></li>', '<li><a href="./">Hotels</a></li>').replace('../../', '../')
    anzahl = len(liste)
    return head('Unsere Hotels an der polnischen Ostsee | Bernstein Touristik',
                f'{anzahl} ausgewählte und getestete Hotels an der polnischen Ostsee – von Swinemünde bis Danzig. Kurreisen, Wellness und Kurztrips mit Bernstein Touristik.',
                '../') + kopf_ + f'''<main id="inhalt">
  <section class="page-hero">
    <div class="wrap">
      <nav class="crumbs crumbs--light" aria-label="Brotkrümelnavigation"><a href="../">Startseite</a><span aria-hidden="true">›</span><span aria-current="page">Hotels</span></nav>
      <p class="eyebrow eyebrow--amber">Ausgewählt &amp; getestet</p>
      <h1>Unsere Hotels an der polnischen Ostsee</h1>
      <p>{anzahl} Hotels in {len(gruppen)} Ostseebädern – vom kleinen Familienhotel bis zum 5-Sterne-Spa-Resort. Wählen Sie einen Ort oder stöbern Sie einfach.</p>
    </div>
  </section>

  <div class="filterbar">
    <div class="wrap">
      <ul class="chips chips--filter" aria-label="Nach Ort filtern">
        {"".join(chips)}
      </ul>
    </div>
  </div>

  <div class="wrap hotel-groups">
      {"".join(gruppen)}
  </div>
</main>''' + fuss_ + '''<a class="call-fab" href="tel:+493048490070" aria-label="Jetzt anrufen: 030-484 900 70">
  <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/></svg>
</a>
<script src="../js/main.js" defer></script>
</body>
</html>
'''


def main():
    import sys
    sys.path.insert(0, HIER)
    hotels, auslassen, groessen = lade()
    teile = vorlage_teile()
    radisson = next(h for h in hotels if h['slug'] == 'radisson-blu-resort-swinemuende')
    aktiv = [h for h in hotels if h['slug'] not in auslassen]
    for h in aktiv:
        ordner = os.path.join(HOTELS_DIR, h['slug'])
        os.makedirs(ordner, exist_ok=True)
        with open(os.path.join(ordner, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(seite(h, aktiv + [radisson], groessen, teile))
    with open(os.path.join(HOTELS_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(uebersicht(aktiv, groessen, teile, radisson))
    # Liste der neuen Seiten für die Verlinkung
    json.dump(sorted([h['slug'] for h in aktiv] + ['radisson-blu-resort-swinemuende']),
              open(os.path.join(HIER, 'seiten.json'), 'w'), indent=0)
    print(len(aktiv), 'Hotelseiten + Übersicht erzeugt')


if __name__ == '__main__':
    main()
