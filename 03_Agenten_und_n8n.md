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

## Konkrete Reihenfolge der n8n-Workflows

1. `KB-01_source_register`: kontrollierter Quellenimport und Datenklassifizierung (noch kein KI-Agent).
2. `KB-02_search_test`: Fragen/Embeddings → Quellen, Fundstellen und Status zurückgeben, keine Schreibrechte.
3. `CP-01_storyboard`: zielgerichtete MDs + RAG → Entwurf → menschliche Freigabe.
4. `CP-02_content`: Content und Quellenbelege → strukturierte SlideSpecs.
5. `CP-03_design`: Layout-IDs/Mapping → Renderer oder bestehender geeigneter Connector.
6. `CP-04_qa_release`: Prüfläufe → Human Gate → SharePoint-Publikation.

**API-Rechte:** n8n-Agent-Tools nicht direkt mit dem breit berechtigten Supabase-Secret Key verbinden. Nur den Retrieval-Teil des Workflows mit den benötigten Suchfunktionen koppeln; Admin-Credential bleibt außerhalb der Agenten-Tool-Auswahl. Langfristig eigener Read-only-Endpoint.
