# Agenten-Architektur: Rollen, Inputs, Outputs und Rechte

**Nicht** jeder Prozessschritt benötigt ein eigenes kostenpflichtiges LLM. Starke Modelle für Planung/Review, günstigere für strukturierte Routineaufgaben. Entscheidend sind die einheitlichen Datenverträge.

## A. Retrieval / Research (wird bei Bedarf aufgerufen)

**Input:** Modul-/Tag-ID, konkrete Fragestellung, Quellzugriff, Versionen, Suchmodus.
**Tools:** Supabase/RAG + Web-Recherche/Primärquellenprüfung, wenn erlaubt.
**Output:** `source_brief.md` mit Zitaten, `source_id`, Fundstellen, Datum, Unsicherheiten, Grenzen.
**Grenze:** Retrieval ist keine Verifikation; ein externer Suchtreffer ist kein freigegebener Kursinhalt.

## B. Curriculum / Storyboard

**Input:** `curriculum.md`, `didaktik.md`, `content_workflow.md`, DayBrief, SourceBrief.
**Output:** beobachtbare Lernziele, Tagesagenda mit echten Unterrichtszeiten, Lernreise, Kern-/Plus-Pfad, Freigabe-Storyboard.
**Grenze:** keine Änderungen an Modulmatrix, UE, verbindlichen Lernzielen ohne Human Gate.

## C. Content Agent

**Input:** freigegebenes Storyboard + verifizierte Quellen + Pflicht-/Plus-Aufgabe + normative Dateien.
**Output:** vollständige `SlideSpecs`, Aufgabeninputs, Lösungen, Hinweise für kritische Dozenten.
**Grenze:** keine erfundenen Quellen, Leistungen oder Tools; keine automatische Publikation. KI darf recherchieren/entwerfen, Fakten bleiben nachweispflichtig.

## D. Design Agent

**Input:** fachlich freigegebene `SlideSpecs`, `design.md`, `slide_layouts_v3.json`, Markenmaster.
**Output:** Layout-IDs, Visuallogik, Platzhalterbelegung; niemals die fachliche Wahrheit der Texte verändern.
**Grenze:** unveränderte Schriftfamilien, CI-Farben, Logo-Position; keine erzwungene Master-Reihenfolge; reservierte Layouts für Übungen/Intro/Abschluss/Feedback beachten; flexible Beispielbeschriftungen.

## E. QA / Freigabe

**Input:** Inhalte + Quellen + Layoutmapping + tatsächlicher PPTX-/Bildrender.
**Output:** maschinenlesbare Befunde `PASS/FAIL/NOT_RUN`, Blocker und Korrekturtickets.
**Grenze:** kein „PASS“ ohne tatsächlich durchgeführte Prüfung. Menschen geben konkrete Version frei.

## Optionale KI-kuratierte Projektreise

`governance/optional_methods/ki_kuratierte_projektreise_repoabgleich_v0.2.md` nur bei explizitem, dokumentiertem Freigabeflag laden. Nicht zum Standard für alle Module machen. Eigenständige Entscheidungen, alternativer Lösungsweg und Transfer ohne Wizard müssen sichtbar bleiben.

## Konkrete n8n-Workflows

Umgesetzt in `workflows/` (ECOMEX 0–10); Einrichtung, Betrieb mit/ohne Renderer und Regeln für spätere Änderungen: `docs/04_Betrieb_mit_und_ohne_Renderer.md`.

| Ursprünglicher Plan | Umsetzung |
|---|---|
| `KB-01_source_register` | ECOMEX 5 (Einzeldatei) und ECOMEX 10 (Supabase-Ablage) |
| `KB-02_search_test` | Suche als fester Schritt in ECOMEX 3 (`ecomex_match_documents`) |
| `CP-01_storyboard` | ECOMEX 1 mit menschlicher Freigabe |
| `CP-02_content` | ECOMEX 3 (Recherche, Didaktik, Layout, QA, Revision) |
| `CP-03_design` | ECOMEX 2/4 → Renderer oder ECOMEX 8 (Claude-PPTX-Skill) |
| `CP-04_qa_release` | QA-Bericht in ECOMEX 2, Freigabe in ECOMEX 6 |

**API-Rechte:** n8n-Agent-Tools nicht direkt mit dem breit berechtigten Supabase-Secret Key verbinden. Nur den Retrieval-Teil des Workflows mit den benötigten Suchfunktionen koppeln; Admin-Credential bleibt außerhalb der Agenten-Tool-Auswahl. Langfristig eigener Read-only-Endpoint.
