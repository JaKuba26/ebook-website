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
