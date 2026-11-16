#!/bin/sh
# Baut alle generierten Seiten neu (Hotels, Orte, Kontakt, Suche, …).
# Optional: Ordner mit den alten Rechtsseiten (impressum.html, agb.html, datenschutzerklaerung.html)
cd "$(dirname "$0")" && python3 hotels_bauen.py && python3 seiten_bauen.py "$@"
