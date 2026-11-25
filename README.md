# ECOMEX Content Factory – 0.3

**Zweck:** Sichere, nachvollziehbare Einrichtung von Git + Supabase als Basis für n8n-gesteuerte Content- und Designagenten – inklusive der einsatzfähigen n8n-Workflows und des optionalen Folien-Renderers.

## Zuerst lesen

1. `docs/01_Einrichtung_fuer_Einsteiger.md` – Schritt für Schritt ohne Terminal
2. `docs/02_Datenpflege_und_Qualitaet.md` – Pflege, Berechtigungen, Freigaben
3. `docs/03_Agenten_und_n8n.md` – Rollen und Datenflüsse
4. `docs/04_Betrieb_mit_und_ohne_Renderer.md` – n8n-Workflows einrichten, betreiben und später sicher ändern
   `docs/05_Renderer_einrichten.md` – Renderer neben n8n starten (für IT / go digital)
5. `database/001_create_kb.sql` + `003_content_factory_betrieb.sql` – Wissensbasis und Ablage-Import

## Ordner

| Ordner | Inhalt |
|---|---|
| `governance/` | Regelwerk (curriculum, didaktik, design, qa_rules, content_workflow) – wird von n8n live geladen |
| `design/` | Folienmaster 6.2 und Layoutbibliothek |
| `workflows/` | 12 n8n-Workflows zum Import (ECOMEX 0–11, ECOMEX 11 = Systemcheck) |
| `renderer/` | optionaler Folien-Renderer (Docker-Image `ghcr.io/ecomewb/ecomex-renderer`, gebaut von GitHub Actions); Layoutkatalog der Agenten in `renderer/app/catalog.json` |
| `database/` | SQL für Supabase |
| `tools/` | `pruefe_workflows.py` (Prüfer nach Änderungen in n8n), Generator, Ausdrucks- und Integrationstests |
| `docs/` | Anleitungen |

**Mit oder ohne Renderer:** ECOMEX 0 prüft bei jedem Lauf, ob der Renderer erreichbar ist. Ohne Renderer
liest n8n PDF/Excel/Markdown selbst, PPTX/Word/Scans über Azure Document Intelligence, und erzeugt die
PowerPoint über den Claude-PPTX-Skill (abschaltbar). Nach dem Import zuerst **ECOMEX 11 | Systemcheck** ausführen.

## Wichtig: Bestehende ECOMEX-Arbeit ist unverändert übernommen

Die fünf Dateien unter `governance/` stammen aus dem vorhandenen Wissensstand. **Es wurde kein Inhalt umgeschrieben**, es wird kein `working_draft` zu `approved` erklärt. Ergänzende KI-kuratierte Methode unter `optional_methods/` bleibt optional.

Der aktuelle Folienmaster `design/ECOMEX_Masterlayout_6.2.pptx` und die technische Layoutbibliothek werden als Designreferenz eingebunden. Die PPTX kann alternativ in SharePoint liegen und nur referenziert werden.

**Hinweis Layoutbibliothek:** Die Dateien `design/ECOMEX_*_v3.json` wurden aus Master 6.1 erzeugt. Master 6.2 enthält zusätzlich u. a. Frage 1–5 sowie Kapitel/Unterkapitel/Inhalt in Farbvarianten; die Bildfolien „05/06 · Bildfolie | Großmotiv“ aus 6.1 fehlen in 6.2. Der Katalog wird im nächsten Schritt an 6.2 angeglichen.

## Nicht enthalten

- Keine Credentials oder Schlüssel (werden in n8n bzw. `.env` gesetzt, nie im Repo).
- Fachquellen werden erst durch ECOMEX 10 (Ablage) bzw. ECOMEX 5 (Einzeldatei) indexiert; ein Import ist keine fachliche Freigabe.
- Keine offiziell geprüfte Datenschutz-/Rechtefreigabe (Formulare fragen die Freigabe für externe KI-Dienste ab).
- Layoutkatalog noch auf Basis der Renderer-Layouts; Angleichung an alle Master-6.2-Layouts und automatische Bildbeschaffung folgen.

## Ergebnis von Schritt 1

Nach Einrichtung kannst du (1) Normdateien versioniert bearbeiten, (2) Quellen in Supabase nachvollziehbar registrieren, (3) später gezielt durch RAG abrufen und (4) Content-/Designagenten über definierte Schnittstellen einsetzen.
