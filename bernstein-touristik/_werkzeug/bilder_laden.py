#!/usr/bin/env python3
"""Lädt die Hotelfotos von der alten Website und speichert sie verkleinert als WebP.

Aufruf:  python3 bilder_laden.py [max_bilder_pro_hotel]
Ergebnis: ../img/hotels/<slug>/01.webp … (1200 px) und 01-klein.webp … (560 px, nur die ersten 5)
"""
import io
import json
import os
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, '..', 'img', 'hotels')
MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 12
AUSLASSEN = set(json.load(open(os.path.join(HIER, 'auslassen.json'))))


def laden(url):
    url = urllib.parse.quote(url, safe=":/%?=&")
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def speichern(job):
    slug, nr, url = job
    ordner = os.path.join(ZIEL, slug)
    gross = os.path.join(ordner, f'{nr:02d}.webp')
    klein = os.path.join(ordner, f'{nr:02d}-klein.webp')
    if os.path.exists(gross) and (nr > 5 or os.path.exists(klein)):
        return slug, nr, 'vorhanden', None
    try:
        im = Image.open(io.BytesIO(laden(url)))
        im = im.convert('RGB')
    except Exception as e:  # noqa: BLE001
        return slug, nr, 'FEHLER', str(e)
    os.makedirs(ordner, exist_ok=True)
    g = im.copy()
    g.thumbnail((1200, 1200), Image.LANCZOS)
    g.save(gross, 'WEBP', quality=72, method=5)
    if nr <= 5:
        k = im.copy()
        k.thumbnail((560, 560), Image.LANCZOS)
        k.save(klein, 'WEBP', quality=70, method=5)
    return slug, nr, 'ok', g.size


def main():
    hotels = json.load(open(os.path.join(HIER, 'hotels.json'), encoding='utf-8'))
    jobs = []
    for h in hotels:
        if h['slug'] in AUSLASSEN:
            continue
        for i, url in enumerate(h['bilder_quelle'][:MAX], 1):
            jobs.append((h['slug'], i, url))
    print(len(jobs), 'Bilder …')
    groessen = {}
    with ThreadPoolExecutor(8) as ex:
        for slug, nr, status, info in ex.map(speichern, jobs):
            if status == 'FEHLER':
                print('Fehler', slug, nr, info)
            elif isinstance(info, tuple):
                groessen[f'{slug}/{nr:02d}'] = info
    # Bildgrößen für width/height-Attribute merken
    pfad = os.path.join(HIER, 'bildgroessen.json')
    alt = json.load(open(pfad)) if os.path.exists(pfad) else {}
    alt.update({k: list(v) for k, v in groessen.items()})
    for k in list(alt):
        slug, nr = k.split('/')
        if not os.path.exists(os.path.join(ZIEL, slug, nr + '.webp')):
            del alt[k]
    json.dump(alt, open(pfad, 'w'), indent=0, sort_keys=True)
    print('fertig')


if __name__ == '__main__':
    main()
