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

## Betrieb (für IT / Hetzner-Server)

Fertiges Image mit eingebautem ECOMEX-Master: `ghcr.io/ecomewb/ecomex-renderer` – gebaut und getestet von
GitHub Actions (`.github/workflows/renderer.yml`) bei jeder Änderung an `renderer/` oder am Master.
Schritt-für-Schritt-Anleitung: **`docs/05_Renderer_einrichten.md`**.

```bash
# auf dem Server, auf dem n8n läuft – Ordner mit docker-compose.yml und .env (aus .env.example)
docker compose pull && docker compose up -d
docker exec ecomex-renderer python tools/selbsttest.py      # → „ALLES IN ORDNUNG“
```

- Ressourcen: ca. 1 GB RAM, 1 vCPU genügen. 24 Folien: PPTX ≈ 1 s, PDF-Vorschau ≈ 5 s.
- Den Port **nicht** öffentlich freigeben; n8n spricht den Dienst intern an (`http://ecomex-renderer:8080`).
- Selbst bauen statt ziehen: im Repo-Hauptordner `docker build -f renderer/Dockerfile -t ghcr.io/ecomewb/ecomex-renderer:latest .`
- Neuer Master: Datei in `design/` ablegen und `MASTER_DATEI` im Dockerfile anpassen → GitHub baut ein neues Image →
  auf dem Server `docker compose pull && docker compose up -d`. Mit `POST /inspect` prüfen, welche
  Master-Layouts für Titel-, Kapitel- und Inhaltsfolien gewählt werden; bei Bedarf in
  `config/master_map.json` übersteuern, z. B. `{"default": "Nur Titel", "kapitel": "Kapiteltrenner"}`.
- Die n8n-Workflows funktionieren **auch ohne Renderer** (siehe `docs/04_Betrieb_mit_und_ohne_Renderer.md`);
  ECOMEX 0 prüft `/health` und wählt den Weg automatisch.
- Ohne Master-Datei nutzt der Dienst einen neutralen **Demo-Master** und meldet das im Prüfbericht
  und im Selbsttest.

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
