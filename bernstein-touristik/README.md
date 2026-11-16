# Bernstein Touristik – Relaunch (Entwurf)

Moderne Neugestaltung von bernstein-touristik.de. Schritt 1: Startseite.

- `index.html` – Landingpage (statisches HTML, kein Framework)
- `hotels/<slug>/index.html` – Hotel-Detailseiten (gleiche Adressen wie auf der alten Seite), Vorlage: Radisson Blu Resort
- `danke/` – Bestätigungsseite nach einer Buchungsanfrage
- `css/style.css`, `js/main.js`
- `img/` – Bilder von der bisherigen Website übernommen und fürs Web verkleinert
- `fonts/` – Inter + Fraunces lokal eingebunden (keine Google-Fonts-Verbindung → DSGVO)

Links auf Unterseiten (Hotels, Orte, Karte, Katalog, AGB, Impressum, Datenschutz)
zeigen vorerst auf die alte Website und werden ersetzt, sobald die neuen Unterseiten stehen.
Die Hotelsuche nutzt vorerst die WordPress-Suche der alten Seite.

Die Buchungsanfrage nutzt Netlify Forms (`data-netlify="true"`). Damit Anfragen ankommen,
muss in Netlify unter *Forms* die Formularerkennung (Form detection) eingeschaltet sein.

## Hotelseiten erzeugen (`_werkzeug/`)

Die Hotel-Detailseiten werden aus den Inhalten der alten Website generiert:

1. `hotels_auslesen.py <ordner-mit-html> <orte-hotels.json>` → `hotels.json`
   (Texte, Preistabellen, Zusatzoptionen, Pakete, Bild-Adressen, Ort)
2. `bilder_laden.py 12` → `img/hotels/<slug>/NN.webp` (max. 12 Fotos pro Hotel, verkleinert)
3. `hotels_bauen.py` → `hotels/<slug>/index.html` + Übersicht `hotels/index.html`

Kopf, Fuß, Anreise, Formular und Seitenleiste stammen aus der handgebauten Vorlage
`hotels/radisson-blu-resort-swinemuende/index.html` (wird selbst nicht überschrieben).
`auslassen.json` enthält Seiten, die nicht erzeugt werden (abgelaufene Weihnachtsangebote).
Wer Inhalte ändern will, ändert `hotels.json` und startet `hotels_bauen.py` neu.
