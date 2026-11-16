#!/usr/bin/env python3
"""Liest die Hotelseiten der alten Website (bernstein-touristik.de) aus und
speichert die Inhalte strukturiert in hotels.json.

Aufruf:  python3 hotels_auslesen.py <ordner-mit-hotel-html> <orte-hotels.json>

Die HTML-Dateien heißen wie der Hotel-Slug (z. B. hotel-henryk.html).
orte-hotels.json ordnet jedem Orts-Slug die Hotel-Slugs zu.
"""
import html
import json
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

ORTE = {
    # Orts-Slug der alten Seite: (Anzeigename, Kurzname)
    'ostseebad-swinemuende': ('Ostseebad Swinemünde', 'Swinemünde'),
    'ostseebad-heidebrink': ('Ostseebad Heidebrink', 'Heidebrink'),
    'ostseebad-misdroy': ('Ostseebad Misdroy', 'Misdroy'),
    'ostseebad-pobierowo': ('Ostseebad Poberow', 'Poberow'),
    'ostseebad-rewal': ('Ostseebad Rewahl', 'Rewahl'),
    'ostseebad-fischerkaten-pogorzelica': ('Ostseebad Fischerkaten', 'Fischerkaten'),
    'treptower-deep': ('Ostseebad Treptower Deep', 'Treptower Deep'),
    'ostseebad-gribow': ('Ostseebad Gribow', 'Gribow'),
    'ostseebad-kolberg': ('Ostseebad Kolberg', 'Kolberg'),
    'ostseebad-henkenhagen-ustronie-morskie': ('Ostseebad Henkenhagen / Ziegenberg', 'Henkenhagen'),
    'ostseebad-grossmoellen-mielno': ('Ostseebad Großmöllen', 'Großmöllen'),
    'jershoeft': ('Jershöft', 'Jershöft'),
    'ruegenwaldermuende': ('Rügenwaldermünde', 'Rügenwaldermünde'),
    'ostseebad-stolpmuende-ustka': ('Ostseebad Stolpmünde', 'Stolpmünde'),
    'pommern-danzig': ('Pommern & Danzig', 'Danzig'),
}

# Hotels, die auf keiner Orts-Seite stehen (Sonderangebote usw.)
ORT_NACHTRAG = {
    'sopotorium-medical-resort': 'pommern-danzig',
    'hotel-arka-medical-spa': 'ostseebad-kolberg',
    'hotel-bursztyn-sonderangebot': 'ostseebad-swinemuende',
    'hotel-nad-parseta-weihnachten-silvester': 'ostseebad-kolberg',
    'hotel-new-skanpol-weihnachten-silvester': 'ostseebad-kolberg',
}

MONATE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli',
          'August', 'September', 'Oktober', 'November', 'Dezember']

ABSCHNITTE = [
    # (Schlüssel, Überschrift, Muster für die alte Überschrift)
    ('lage', 'Lage', r'^LAGE'),
    ('zimmer', 'Zimmer', r'^(ZIMMER|APARTMENTS?|UNTERKUNFT)'),
    ('ausstattung', 'Ausstattung', r'^AUSSTATTUNG'),
    ('verpflegung', 'Verpflegung', r'^VERPFLEGUNG'),
    ('wellness', 'Wellness & Kur', r'^(WELLNESS|WELLENSS|KUR\b|KUR &|SPA$|SPA\b)'),
    ('inklusiv', 'Inklusivleistungen', r'INKLUSIVLEISTUNGEN'),
]


def text(s):
    s = re.sub(r'(?i)<br\s*/?>', ' ', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def inline(s):
    """Erlaubt nur einfache Auszeichnung (fett, kursiv, Umbruch)."""
    s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', '', s)
    s = re.sub(r'(?i)<br\s*/?>', '<br>', s)
    s = re.sub(r'(?i)<(/?)(b|strong)(\s[^>]*)?>', r'<\1strong>', s)
    s = re.sub(r'(?i)<(/?)(i|em)(\s[^>]*)?>', r'<\1em>', s)
    s = re.sub(r'(?i)<(?!/?(strong|em|br)\b)[^>]+>', '', s)
    s = html.unescape(s).replace('\xa0', ' ')
    s = s.replace('&', '&amp;').replace('<strong>', '\0s').replace('</strong>', '\0/s') \
         .replace('<em>', '\0e').replace('</em>', '\0/e').replace('<br>', '\0b')
    s = s.replace('<', '&lt;').replace('>', '&gt;')
    s = s.replace('\0s', '<strong>').replace('\0/s', '</strong>').replace('\0e', '<em>') \
         .replace('\0/e', '</em>').replace('\0b', '<br>')
    s = re.sub(r'<strong>\s*</strong>|<em>\s*</em>', '', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'(\s*<br>\s*)+$', '', s)
    s = re.sub(r'^(\s*<br>\s*)+', '', s)
    s = re.sub(r'\s*,\s*,', ',', s)
    s = re.sub(r'\s+([,.:;])', r'\1', s)
    return s.strip()


def preis(s):
    """'1.008,00 €' -> '1.008 €'"""
    s = text(s).replace('€', '').strip()
    s = re.sub(r',00$', '', s)
    s = re.sub(r',-$', '', s)
    return (s + ' €') if re.search(r'\d', s) else ''


def zahl(p):
    try:
        return float(p.replace('€', '').replace('.', '').replace(',', '.').strip())
    except ValueError:
        return None


def tabelle_zeilen(t):
    zeilen = []
    for r in re.findall(r'(?is)<tr.*?</tr>', t):
        zellen = [text(c) for c in re.findall(r'(?is)<t[dh][^>]*>.*?</t[dh]>', r)]
        if any(zellen):
            zeilen.append(zellen)
    return zeilen


def preistabelle(block):
    """Liest die Preistabelle. Ergebnis: Titel, Nächte-Spalten, Zeilen."""
    titel = ''
    h = re.search(r'(?is)<h3[^>]*>(.*?)</h3>', block)
    if h:
        titel = text(h.group(1))
    t = re.search(r'(?is)<table.*?</table>', block)
    if not t:
        return None
    zeilen = tabelle_zeilen(t.group(0))
    naechte, daten = None, []
    for z in zeilen:
        erste = z[0] if z else ''
        if erste.startswith(('Termine', 'TERMINE')) and not titel:
            titel = ' '.join(x for x in z if x)
        if naechte is None and re.match(r'(?i)aufenthalt', erste):
            n = [re.sub(r'\D', '', c) for c in z[1:]]
            n = [x for x in n if x]
            if n:
                naechte = [int(x) for x in n]
            continue
        monat = next((m for m in MONATE if erste.lower().startswith(m.lower()[:3])), None)
        if naechte and monat:
            werte = [preis(c) for c in z[1:]][:len(naechte)]
            if any(werte):
                daten.append({'monat': erste, 'preise': werte})
    if not naechte or not daten:
        return None
    # Spalten aufsteigend nach Nächten sortieren (6, 7, 13, 14)
    ordnung = sorted(range(len(naechte)), key=lambda i: naechte[i])
    naechte = [naechte[i] for i in ordnung]
    for d in daten:
        p = d['preise'] + [''] * (len(ordnung) - len(d['preise']))
        d['preise'] = [p[i] for i in ordnung]
    jahr = re.findall(r'20\d\d(?:/20\d\d)?', titel)
    return {'titel': titel, 'jahr': jahr[0] if jahr else '', 'naechte': naechte, 'zeilen': daten}


def zusatz(block):
    t = re.search(r'(?is)<table.*?</table>', block)
    if not t:
        return []
    out = []
    for z in tabelle_zeilen(t.group(0)):
        z = [c for c in z if c]
        if len(z) >= 2:
            label = re.sub(r'\s*:\s*$', '', z[0])
            out.append([label, z[-1]])
        elif len(z) == 1:
            out.append([z[0], ''])
    return out


def bloecke(inhalt):
    """Zerlegt den Freitext in Absätze, Listen und Tabellen."""
    teile = re.findall(r'(?is)<(p|ul|ol|table|h[1-6])\b[^>]*>(.*?)</\1>', inhalt)
    out = []
    for tag, inner in teile:
        tag = tag.lower()
        if tag in ('ul', 'ol'):
            punkte = [inline(li) for li in re.findall(r'(?is)<li[^>]*>(.*?)</li>', inner)]
            punkte = [p for p in punkte if text(p)]
            if punkte:
                out.append({'typ': 'liste', 'punkte': punkte})
        elif tag == 'table':
            for z in tabelle_zeilen('<table>' + inner + '</table>'):
                t = ' '.join(c for c in z if c)
                if t:
                    out.append({'typ': 'hinweis', 'html': inline(t)})
        else:
            h = inline(inner)
            roh = text(inner)
            if not roh:
                continue
            nur_fett = re.fullmatch(r'\s*<strong>([^<]*)</strong>\s*', h)
            if tag.startswith('h') or (nur_fett and len(roh) <= 90) or (len(roh) <= 40 and abschnitt_von(roh)[0]):
                out.append({'typ': 'ueberschrift', 'text': roh})
                continue
            # "<strong>Lage</strong><br> Text …" -> Überschrift + Absatz
            vorne = re.match(r'\s*<strong>([^<]{2,45}?)(?:<br>)?\s*</strong>\s*(?:<br>\s*)?(.+)$', h, re.S)
            if vorne and abschnitt_von(vorne.group(1))[0]:
                out.append({'typ': 'ueberschrift', 'text': text(vorne.group(1))})
                h = vorne.group(2).strip()
                if not text(h):
                    continue
            # Mehrere Zeilen mit "<br>" -> einzelne Absätze
            out.append({'typ': 'absatz', 'html': h})
    return out


def abschnitt_von(ueberschrift):
    u = ueberschrift.upper().strip(' :')
    for key, titel, muster in ABSCHNITTE:
        if re.search(muster, u):
            return key, titel
    return None, None


def paket_titel(u):
    """'ZUBUCHUNG KURPAKET: 40,00€ PRO PERSON/PRO WOCHE' -> Titel + Preis."""
    roh = u.split('•')[0]
    p = re.search(r'(\d+(?:,\d\d)?)\s*€', roh)
    art = 'Wellnesspaket' if re.search(r'(?i)wellnes', roh) else 'Kurpaket'
    if re.search(r'(?i)mini', roh):
        art = 'Mini-' + art
    if re.search(r'(?i)deluxe', roh):
        art += ' Deluxe'
    betrag = re.sub(r',00$', '', p.group(1)) if p else ''
    extra = [x.strip() for x in u.split('•')[1:] if x.strip()]
    return art, betrag, extra


def strukturieren(bl):
    abschnitte, pakete, hinweise = [], [], []
    akt = None
    paket = None
    for b in bl:
        if b['typ'] == 'ueberschrift':
            u = b['text']
            if re.search(r'(?i)zubuch', u) or re.search(r'(?i)^\d+x\s+kuranwendungen', u):
                art, betrag, extra = paket_titel(u)
                paket = {'titel': art, 'preis': betrag, 'punkte': list(extra), 'text': u}
                pakete.append(paket)
                continue
            key, titel = abschnitt_von(u)
            paket = None
            if key == 'inklusiv':
                akt = {'key': 'inklusiv', 'titel': titel, 'bloecke': []}
                abschnitte.append(akt)
                continue
            if key:
                # gleiche Abschnitte zusammenführen
                vorhanden = next((a for a in abschnitte if a['key'] == key), None)
                if vorhanden:
                    akt = vorhanden
                else:
                    akt = {'key': key, 'titel': titel, 'bloecke': []}
                    abschnitte.append(akt)
                continue
            # Zwischenüberschrift innerhalb eines Abschnitts
            if akt is None:
                akt = {'key': 'allgemein', 'titel': 'Über das Hotel', 'bloecke': []}
                abschnitte.append(akt)
            akt['bloecke'].append({'typ': 'zwischen', 'text': u})
            continue
        if b['typ'] == 'hinweis':
            hinweise.append(b['html'])
            continue
        if b['typ'] == 'absatz' and text(b['html']).startswith('*'):
            hinweise.append(b['html'])
            continue
        if paket is not None:
            if b['typ'] == 'liste':
                for pu in b['punkte']:
                    (hinweise if text(pu).startswith('*') else paket['punkte']).append(pu)
            else:
                paket['punkte'].append(b['html'])
            continue
        if akt is None:
            akt = {'key': 'allgemein', 'titel': 'Über das Hotel', 'bloecke': []}
            abschnitte.append(akt)
        if b['typ'] == 'absatz' and b['html'].startswith('*'):
            hinweise.append(b['html'])
            continue
        akt['bloecke'].append(b)
    abschnitte = [a for a in abschnitte if a['bloecke']]
    return abschnitte, pakete, hinweise


def auslesen(pfad, slug):
    s = open(pfad, encoding='utf-8').read()
    titel_seite = text(re.search(r'(?is)<title>(.*?)</title>', s).group(1)).split(' – ')[0].split(' - Bernstein')[0]
    m = re.search(r'(?is)<main.*?</main>', s)
    s = m.group(0)
    name = text((re.search(r'(?is)<h1[^>]*>(.*?)</h1>', s) or re.search(r'(?is)<h2[^>]*>(.*?)</h2>', s)).group(1)) or titel_seite
    kopfbild = re.search(r'class="hotelheader[^"]*"[^>]*data-bg="([^"]+)"', s)
    sterne = 0
    st = re.search(r'(?is)<div class="sterne">(.*?)</div>', s)
    if st:
        # jedes Stern-Bild steht doppelt im HTML (data-src + noscript)
        sterne = len(re.findall(r'<img[^>]*star\.svg', re.sub(r'(?is)<noscript>.*?</noscript>', '', st.group(1))))
    bilder = []
    if kopfbild:
        bilder.append(kopfbild.group(1))
    for u in re.findall(r"<a href='(https://www\.bernstein-touristik\.de/wp-content/uploads/[^']+\.(?:jpe?g|png|webp))'", s, re.I):
        if u not in bilder:
            bilder.append(u)
    ab = re.search(r'schon ab.{0,300}?(\d[\d.]*)\s*€', s, re.S)
    ab_preis = ab.group(1) if ab else ''

    # Freitext: nach der Galerie bis zur Preistabelle
    start = s.rfind("</figure>") if "gallery-item" in s else -1
    if start < 0:
        start = s.find('panel-layout')
    ende = s.find('tabelle tabelle-1')
    if ende < 0:
        ende = s.find('class="reiseinfos"')
    if ende < 0:
        ende = len(s)
    inhalt = s[start:ende]
    inhalt = re.sub(r'(?is)<table[^>]*>\s*<tbody>\s*<tr>\s*<td[^>]*bgcolor="#0072bc".*?</table>', '', inhalt)
    abschnitte, pakete, hinweise = strukturieren(bloecke(inhalt))

    pt = re.search(r'(?is)tabelle-1">(.*?)</div>\s*<div class="width-50 tabelle tabelle-2', s) or \
        re.search(r'(?is)tabelle-1">(.*?)</table>', s)
    preise = preistabelle(pt.group(1) + ('</table>' if '</table>' not in pt.group(1) else '')) if pt else None
    zt = re.search(r'(?is)tabelle-2">(.*?)</table>', s)
    extras = zusatz(zt.group(1) + '</table>') if zt else []
    zt_titel = ''
    if zt:
        h = re.search(r'(?is)<h3[^>]*>(.*?)</h3>', zt.group(1))
        zt_titel = text(h.group(1)) if h else ''

    return {
        'slug': slug, 'name': name, 'sterne': sterne, 'ab_preis': ab_preis,
        'bilder_quelle': bilder, 'abschnitte': abschnitte, 'pakete': pakete,
        'hinweise': hinweise, 'preise': preise, 'extras': extras, 'extras_titel': zt_titel,
    }


def main():
    ordner, orte_json = sys.argv[1], sys.argv[2]
    orte = json.load(open(orte_json))
    # alte Orts-Slugs der WordPress-Seite -> neue Slugs
    for alt, neu in {'ostseebad-groess-moellen-mielno': 'ostseebad-grossmoellen-mielno'}.items():
        if alt in orte:
            orte[neu] = orte.pop(alt)
    hotel_ort = {}
    for o, hs in orte.items():
        if o in ORTE:
            for h in hs:
                hotel_ort.setdefault(h, o)
    hotel_ort.update({k: v for k, v in ORT_NACHTRAG.items() if k not in hotel_ort})
    sonder = set(orte.get('sonderangebote', []))
    hotels = []
    for f in sorted(os.listdir(ordner)):
        if not f.endswith('.html'):
            continue
        slug = f[:-5]
        h = auslesen(os.path.join(ordner, f), slug)
        ort = hotel_ort.get(slug)
        if not ort:
            # Sonderseiten (z. B. Weihnachten) -> Ort des Basis-Hotels
            basis = next((k for k in sorted(hotel_ort, key=len, reverse=True)
                          if slug.startswith(k.split('-weihnachten')[0]) or k.startswith(slug.split('-weihnachten')[0].split('-sonderangebot')[0])), None)
            ort = hotel_ort.get(basis) if basis else None
        h['ort'] = ort
        h['ort_name'], h['ort_kurz'] = ORTE.get(ort, ('Polnische Ostsee', 'Ostsee'))
        h['sonderangebot'] = slug in sonder or bool(re.search(r'weihnacht|silve|sonderangebot', slug))
        hotels.append(h)
    json.dump(hotels, open(os.path.join(HIER, 'hotels.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(hotels), 'Hotels gespeichert')


if __name__ == '__main__':
    main()
