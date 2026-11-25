# ECOMEX Folien-Renderer

Kleiner HTTP-Dienst für die ECOMEX Content Factory. Er setzt die von den KI-Agenten gelieferten
Folieninhalte **deterministisch in den echten ECOMEX-Folienmaster** – als editierbare PowerPoint mit
nativen Formen, Tabellen und Sprechernotizen. Zusätzlich liest er Word/Excel/PDF/PPTX aus und
erzeugt eine PDF-Vorschau für die visuelle KI-Prüfung.

Kein KI-Aufruf, keine Datenbank, keine Datenhaltung: jede Anfrage wird im Speicher verarbeitet.

## Endpunkte

| Methode | Pfad | Zweck |
|---|---|---|
| GET | `/health` | Status, aktiver Master (ohne API-Key) |
| GET | `/katalog` | Layoutkatalog für die Agenten + Layoutnamen des Masters |
| POST | `/render?format=pptx` | Deck-JSON → PPTX |
| POST | `/render?format=pdf` | Deck-JSON → PDF-Vorschau (LibreOffice) |
| POST | `/render?format=report` | Deck-JSON → Prüfbericht (Textüberlauf, Pflichtfelder, Monotonie, Übung ohne Lösung …) |
| POST | `/extract` | Datei (multipart `file`) → Text mit Fundstellen (Seite/Folie/Abschnitt/Zeile) |
| POST | `/inspect` | Master-Layouts anzeigen und Zuordnung Katalog → Master prüfen (optional eigene Datei) |
| POST | `/finalisieren?version=…&pruefer=…` | Freigegebene PPTX: ENTWURF-Kennzeichnung entfernen, Version/Prüfer:in in Dateieigenschaften |

Alle Endpunkte außer `/health` verlangen den Header `X-API-Key` (= Umgebungsvariable `RENDERER_API_KEY`).

## Betrieb (für IT / go digital)

```bash
# 1. Master: docker-compose.yml bindet ../design/ECOMEX_Masterlayout_6.2.pptx direkt ein.
#    Neuer Master → Datei in design/ ablegen und den Pfad in docker-compose.yml anpassen.
# 2. Optional: Firmenschriften (TTF/OTF) nach fonts/ – sonst wird Open Sans verwendet
# 3. Bauen und starten (im selben Docker-Netz wie n8n)
export RENDERER_API_KEY="$(openssl rand -hex 24)"
docker compose up -d --build
# 4. Test
curl http://localhost:8080/health      # bzw. aus dem n8n-Container: http://ecomex-renderer:8080/health
```

- Ressourcen: ca. 1 GB RAM, 1 vCPU genügen. 55 Folien: PPTX ≈ 1 s, PDF-Vorschau ≈ 3 s.
- Den Port **nicht** öffentlich freigeben; n8n spricht den Dienst intern an.
- Alternativ als Azure Container App (Region West Europe) betreibbar; dann HTTPS + API-Key.
- Update des Masters: Datei austauschen, Container neu starten. Mit `POST /inspect` prüfen, welche
  Master-Layouts für Titel-, Kapitel- und Inhaltsfolien gewählt werden; bei Bedarf in
  `config/master_map.json` übersteuern, z. B. `{"default": "Nur Titel", "kapitel": "Kapiteltrenner"}`.
- Die n8n-Workflows funktionieren **auch ohne Renderer** (siehe `docs/04_Betrieb_mit_und_ohne_Renderer.md`);
  ECOMEX 0 prüft `/health` und wählt den Weg automatisch.
- Ohne Master-Datei nutzt der Dienst einen neutralen **Demo-Master** und meldet das
  im Prüfbericht.

## Wie der Renderer gestaltet

- Jede Folie nutzt ein Layout des Masters (Titel-Platzhalter, Logo, Hintergrund, Fußzeilen bleiben
  erhalten). Der Inhaltsbereich wird aus dem Titel-Platzhalter des Masters berechnet.
- Alle Farben sind **Theme-Farben** des Masters (accent1 … accent6, dk2); Schriften werden aus dem
  Theme geerbt. Ändert sich der Master, folgen alle neu gerenderten Decks.
- Textgrößen werden mit echten Schriftmetriken gewählt (größte passende Stufe, kein Wortbruch).
  Passt etwas nicht, wird es **nicht abgeschnitten**, sondern im Prüfbericht als `textueberlauf` gemeldet.
- 24 Layouts (siehe `app/catalog.json`): Tagestitel, Tagesablauf, Lernziele, Kapitel, Leitfrage,
  Kernaussage, Stichpunkte, Vergleich, Karten, Prozess, Tabelle, Zitat/Definition, Zahlen & Fakten,
  Praxisbeispiel, Prompt-Demo, Werkzeug-Anleitung, Bild + Text, Übung, Material, Musterlösung,
  Reflexion, Zusammenfassung, Quellen, Pause.

## Deck-JSON (Kurzform)

```json
{
  "meta": {"modul": "M02", "tag": "Tag 12", "thema": "…", "entwurf": true, "dateiname": "ECOMEX_M02_Tag12_ENTWURF"},
  "folien": [
    {"layout": "karten", "block": "Block 2",
     "felder": {"titel": "Vier typische Fehlerbilder", "karten": [{"ueberschrift": "…", "text": "…"}]},
     "notizen": "Sprechertext …", "quellen": ["…"], "review_hinweise": ["…"]}
  ]
}
```

Ein vollständiges Beispiel mit allen Layouts: `tests/sample_deck.json`
(`python tests/render_sample.py` erzeugt `tests/out/sample.pptx` und `sample.pdf`).

## Dateien

```
app/main.py        HTTP-Endpunkte
app/render.py      Deck → PPTX, PDF, Prüfbericht, Finalisierung
app/layouts.py     Gestaltung der 24 Layouts
app/pptxkit.py     Master/Theme lesen, Layoutwahl, native Formen
app/textfit.py     Textvermessung mit Schriftmetriken
app/extract.py     DOCX/XLSX/PPTX/PDF/TXT → Text mit Fundstellen
app/catalog.json   Layoutkatalog (Quelle für Agenten und Renderer)
config/            brand.json (ENTWURF-Label, Fußzeile), master_map.json
masters/           ecomex_master.pptx (hier ablegen), demo_master.pptx (automatisch)
```
