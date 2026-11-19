---
document_id: ecomex.content_workflow
title: "ECOMEX | Modellunabhängiger Content-Produktionsworkflow"
version: "1.0.0"
status: "architecture_proposal"
last_reviewed: "2026-11-18"
language: "de-DE"
owner_role: "ECOMEX Content-Verantwortung / Weiterbildungsmanagement"
depends_on: ["curriculum.md", "didaktik.md", "design.md", "qa_rules.md"]
---

# Content Workflow: Produktion, Prüfschleifen und menschliche Freigaben

## 1. Zielbild

Eine **modell- und orchestratorunabhängige Content Engine** produziert aus einem freigegebenen Curriculum **fachlich belastbare, didaktisch durchdachte und editierbare Unterrichtsmaterialien** – insbesondere PowerPoint-Decks, Übungsmaterial, Musterlösungen und Dozentenunterlagen.

**Nicht das Ziel:** „Ein Prompt erstellt aus einem Stichwort 100 Folien und erklärt sie für perfekt.“

**Stattdessen:**

`Quellen → strukturierter Auftrag → fachliches Briefing → Lernreise → vollständig ausgearbeitete Inhalte → unabhängige QA → PPTX-Render → Bildprüfung → menschliche Freigabe → Veröffentlichung`

Jeder Schritt hat eigenständige Eingaben/Ergebnisse, maschinenlesbare Artefakte, eindeutige Versionsangaben und einen definierten Eskalationsweg. Die Architektur funktioniert:

- **manuell**, indem eine Person strukturierte Dateien nacheinander mit LLMs bearbeitet;
- **teilautomatisiert** mit Scripts und einem einzigen LLM;
- **multiagentisch** mit spezialisierten Modellen/Agenten;
- **orchestriert** z. B. durch n8n, Azure oder andere Workflow-Engines.

Kein Schritt darf ausschließlich durch eine geheime Konversationshistorie, einen speziellen Anbieter-Prompt oder ungesicherten Agentenspeicher definiert sein.

## 2. Aufgabenteilung: stabile Regeln vs. veränderbare Inhalte

| Schicht | Inhalt | Speicherprinzip | Änderungsfreigabe |
|---|---|---|---|
| **A – Normen** | diese fünf `.md`-Dateien; später genehmigtes Designmaster, Checklisten | versionskontrollierte Dateien | Weiterbildungsmanagement/Owner |
| **B – Curriculum** | Module, UE, Lernziele, Anschlusslogik, Scope-Grenzen | strukturierte Textdateien/YAML/JSON | Curriculum-Owner |
| **C – Wissensquellen** | interne Decks, PDFs, Lehrpläne, Handbücher, aktuelle externe Fachquellen | Originaldateien mit Metadaten und Zugriffskontrolle; optional Suchindex | Quellenverantwortliche |
| **D – Produktionsauftrag** | `ModuleBrief`, `DayBrief`, Unterrichtsdauer, konkrete Fall-/Materialvorgaben | pro Job versioniert | menschliches Gate G1 |
| **E – Zwischenprodukte** | `SourceBrief`, `SlidePlan`, `SlideSpecs`, Übungen, QA-Berichte | deterministische Dateien pro Modul/Tag | QA + spezifizierte Gates |
| **F – Releases** | freigegebenes PPTX/PDF, Workbook, Lösungen, Quellenmanifest | SharePoint/vereinbarte Ablage; immutable Release-Manifest | G5 / autorisierte Person |

**Kernregel:** Markdown ist ein **Regel- und Wissensformat**, keine Datenbank, kein dauerhafter LLM-Speicher und kein Git-Ersatz. Ein Vektorindex erleichtert Suche, ersetzt aber weder Versionierung noch die Verbindlichkeit freigegebener Dokumente.

## 3. Empfohlener Speicheraufbau – nicht vorgeschrieben

```text
ecomex-content-engine/
├── governance/
│   ├── curriculum.md
│   ├── didaktik.md
│   ├── design.md
│   ├── qa_rules.md
│   └── content_workflow.md
├── references/
│   ├── source_manifest.json
│   └── approved_brand_master.pptx       # erst nach echter Freigabe
├── curriculum_data/
│   ├── modules/                        # M01–M12 briefs, YAML/JSON/MD
│   └── days/                           # Mxx-Dxx Briefs
├── cases/
│   └── <case_id>/                      # vollständig fiktive Testdaten + Musterlösungen
├── prompts/                            # knappe, modellneutral beschriebene Rollenaufträge
├── schemas/                            # JSON Schema o. ä.; Validierung nicht nur im Prompt
├── templates/                          # Renderer-Layouts und Komponenten
├── jobs/
│   └── <job_id>/
│       ├── input_manifest.json
│       ├── source_brief.md
│       ├── day_brief.json
│       ├── slide_plan.json
│       ├── slide_specs.json
│       ├── exercises/
│       ├── qa/
│       ├── render/
│       └── approval.json
└── releases/
    └── <curriculum_version>/<module_id>/<day_id>/<release_version>/
```

**Änderbar:** Ordnernamen, Git-Provider, RAG-Backend, LLM, Orchestrator und Renderbibliothek.  
**Stabil halten:** Dokumenttypen, Referenz-IDs, Pflichtfelder, QA-Regel-IDs, Entscheidungen und Freigabegates.

**Git** ist sinnvoll für die Versionierung von Regeln, Prompts, Schemas, Beispielquellen, Quelltext und Änderungsreviews. Große PPTX/PDF/Medien können je nach Infrastruktur in SharePoint/Objektspeicher liegen; Git muss **nicht** jedes Originaldeck beherbergen. Keine Zugangsdaten einchecken.

**Supabase/Postgres/RAG** ist **optional** für die Suche in vielen zugelassenen Materialien. Originalquellen und Autoritätsinformationen bleiben nachvollziehbar. n8n ist der **Orchestrator**, nicht automatisch das Fachmodell, die Quelle oder die zentrale Wahrheit. SharePoint kann als Freigabe-/Auslieferungsort dienen, sofern Berechtigungen und Zielpfade festgelegt sind.

## 4. Quellenaufnahme und Provenienz (Stage 0)

Bevor ein Agent Inhalte erstellt, werden Quellen systematisch erfasst.

**Eingang:** DOCX/PPTX/PDF/MD/Tabellen, Tooldokumentation und ggf. genehmigte externe Primärquellen.

**Aufgaben:**

1. Originaldatei unverändert aufbewahren; `source_id`, Dateiname, Version, Datum, Herkunft, Eigentum/Lizenz, Freigabestatus, Hash und Zugriffsrechte dokumentieren.
2. Struktur auslesen: Module, Tagesüberschriften, Tabellen, Stichpunkte, Übungen, Lösungen, Foliennotizen, Abbildungen, Quellenangaben, ggf. Screenshots.
3. Text **und visuelle Information** auswerten; eine reine PPTX-Textliste erfasst Diagrammaussagen und Layoutfehler nicht zuverlässig.
4. Bei unlesbaren Tabellen/Bildinhalten gezielte visuelle Sichtung statt Inhalte zu erraten.
5. Inhalte in kleine **inhaltliche Einheiten** gliedern (z. B. Abschnitt, Tabelle, Folienblock), aber Originalkontext und genaue Fundstelle erhalten.
6. Vertrauliche Daten vor externer Modellverarbeitung klassifizieren und gegebenenfalls anonymisieren/unternehmensintern verarbeiten.
7. Widersprüche nicht „zusammensynthetisieren“; separat im `source_conflicts`-Register erfassen.
8. Ursprung und epistemischen Status unterscheiden: `source_fact`, `derived`, `hypothesis`, `proposed_rule`, `example_fictional`, `unverified`.
9. Änderungen des Quellenbestands erkennen und gezielt betroffene Tages-/Modulbriefings als veraltet markieren.

**Beispiel:**

```json
{
  "source_id": "S04",
  "filename": "Ecomex Lehrplan Woche 1-4.docx",
  "source_type": "docx",
  "authority": "use_day_plan_working",
  "version_label": "2026-11 working copy",
  "hash_sha256": "<calculated_on_ingestion>",
  "access_class": "internal",
  "locator": "Tabelle: Tag 17",
  "claim_type": "source_fact",
  "verified_for_job": false,
  "conflicts_with": ["S03: week-2 JSON wording"]
}
```

In der realen Pipeline ist `hash_sha256` ein tatsächlich berechneter Hash, kein wörtlicher Platzhalter.

### Priorität bei widersprüchlichen Quellen

1. **Explizite aktuelle menschliche Freigabe/Anweisung** für den betreffenden Job.
2. **Freigegebenes** Curriculum/Zertifizierungsdokument, falls verfügbar.
3. Ansonsten aktuelle, aber **noch vorläufige** 2027-Kursarchitektur S01/S02 und Stammdatenblatt S03 für Modul-/UE-Scope.
4. Der detaillierte USE-Lehrplan S04 für die Unterrichtsverteilung von Tagen 1–20; erkannte Konflikte zu S03 müssen als offen markiert bleiben.
5. Bestandsdecks S05–S07 als Material- und Ideenfundus **mit Prüfung**, nicht als neueste Wahrheit.
6. Pilot S08 nur für Analysen und Übernahme nach Review, **nicht als Master**.
7. Älterer Strategieentwurf S09 nur für historischen Kontext und Produktlogik; nicht zur stillen Überschreibung der neuen Modulmatrix.

Für rechtliche/technisch dynamische Sachverhalte gilt zusätzlich die **aktuell geprüfte Primärquelle**. Ein altes ECOMEX-Deck ersetzt diese nicht.

## 5. Wissenssuche (RAG) – wenn die Materialmenge wächst

**RAG-Muster:** Originale → strukturierte Extraktion → Chunk + `source_id`/Locator/Status → optional embeddings/Suche → gezielte Kontextauswahl → belegt formuliertes `SourceBrief`.

**Indexfelder (Minimum):**

`chunk_id`, `source_id`, `source_version`, `title`, `module_id`, `day_id`, `content_type`, `locator`, `body_text`, `access_class`, `authority`, `approved_status`, `valid_from`, `last_verified_at`, `hash`.

**Retrieval-Regeln:**

- Nur **zugelassene** Quellen des Jobs durchsuchen; Rechte pro Quelle prüfen.
- Retrieval zuerst nach Curriculum-/Status- und Modulmetadaten begrenzen, dann semantisch suchen.
- Genaues Quellenzitat/Locator zur Aussage zurückgeben.
- Bei Widerspruch beide Positionen zeigen und `needs_decision` erzeugen.
- Veraltete Versionsaussagen nicht ohne neue Prüfung als aktuell verwenden.
- Keine irrelevant langen Textmassen an jedes Modell senden. **Top-K** nach begründetem Bedarf; Wissensabruf pro Modul/Tag/Frage.
- Keine stillschweigende Vermischung vertraulicher interner Quellen mit öffentlichen/unkontrollierten Modellen.

**RAG ist keine Pflicht** für den ersten Tag. Mit neun lokalen Quellen und freigegebenen Briefings kann eine saubere Dateistruktur zunächst ausreichen. Supabase kann später als **Such- und Metadatenebene** hinzukommen; der verbindliche Curriculumstand bleibt separat versioniert.

## 6. Produktionspipeline: acht getrennte Stufen

### P0 – Auftrag und Eingaben validieren

**Input:** `job_id`, Modul/Tag, aktuelle fünf Regeldateien mit Versionen, Curriculumbrief, freigegebene Referenzen, verfügbare Tools/Designmaster, Outputziele.  
**Prüfen:** Pflichtdaten, Dateien, Berechtigungen, Versionsstände, Aufwand, Anzahl Tage, Zugriffsklasse.  
**Ergebnis:** `input_manifest.json` mit reproduzierbarem `job_id`.  
**Stoppen**, wenn Curriculum, Quellzugriff oder kritische Freigaben fehlen; keine Fakten erfinden.

### P1 – Fachliches Briefing / SourceBrief

**Rolle:** Fachredaktion + Recherche.  
**Input:** verifizierte Zielkompetenzen und relevante Quellen-Chunks.  
**Output:** `source_brief.md`, bestehend aus Fachbegriffen, korrekten Mechanismen, typischen Fehlannahmen, konkreten Quellen/Locators, offenen Fragen und bewusst ausgeschlossenen Themen.

Ergänzende Aktualitätsrecherche darf bei dynamischen Themen erfolgen, muss aber getrennt von der ECOMEX-Quellenaussage dokumentiert werden. Bei unklaren Fachclaims `needs_verification`, nicht „logisch klingt es“.

### P2 – Modul-/Tagesbrief (DayBrief)

**Rolle:** Curriculum-/Didaktikplanung.  
**Input:** Mxx-Outcome, Schnittstelle zum Vor-/Folgemodul, Stunden-/Pausenrahmen, Zielgruppe und verfügbares Material.  
**Output:** `day_brief.json` mit konkret beobachtbaren Outcomes, Pflichtbegriffen, Fall, Voraussetzungen, Differenzierung, Scope-Grenzen, Nettozeiten, Tool-/Offline-Pfad und Tests.

**Gate G1:** menschliche Freigabe der Lernziele, wesentlichen Inhalte und Tagesrealität, bevor das Deck detailliert ausformuliert wird.

### P3 – Unterrichtsdramaturgie und SlidePlan

**Rolle:** Instructional Design (ggf. mit kritischem Zweitmodell).  
**Output:** `slide_plan.json` mit Unterrichtsblöcken, Zeit, Zielbezug, konkretem Visualtyp, vorbereiteter Interaktion, Lernprodukt, Übergängen und wiederkehrenden Referenzdaten.

**Verpflichtend:**
- klare Progression statt Themenliste;
- ein ausgearbeitetes Beispiel vor komplexer selbstständiger Übung;
- ausgewogene Lehr-/Übungszeit;
- keine unmotivierten Toolwechsel;
- Basis/Plus-Verzweigung für heterogene Gruppe;
- Lösung/Besprechung tatsächlich eingeplant;
- keine falsche Gleichsetzung von Folienanzahl und Unterrichtsminuten.

**Gate G2:** fachlich-didaktischer Storyboard-Review; große Fehlkonzepte hier ändern, nicht erst nach dem PowerPoint-Render.

### P4 – Vollständiger Content vor Folienproduktion

**Rollen:** Fachautor/Editor, Aufgabenautor, Prüfer.  
**Input:** genehmigter SlidePlan, SourceBrief, Falldaten.  
**Output:** vollständig befüllte `slide_specs.json`, Übungsdateien, Musterlösungen, optionaler Dozentenleitfaden.

Inhalt wird **zuerst geschrieben und überprüft**. Keine unfertigen Visual-Anweisungen, Pseudografiken, fehlenden Lösungen oder bloßen Definitionssammlungen an den Renderer durchreichen. Bei Änderungswunsch nur betroffene `slide_id` neu erzeugen.

### P5 – Unabhängige Content-QA

**Rollen:** faktenorientierter QA-Agent, Didaktik-QA, optional Human/SME.  
**Output:** strukturierter Bericht pro `qa_rules.md`-Regel, `PASS/FAIL/NOT_RUN`, Korrekturtickets mit Fundstellen.  
**Regel:** Kritische Fehler blockieren. Korrektur → gezielter Nachtest. Kein Qualitätsbeweis durch selbstvergebenen Score.

**Gate G3:** fachliche Freigabe der **vollständigen Unterrichtsinhalte** vor Renderung.

### P6 – Deterministisches Rendern und Render-QA

**Rolle:** PPTX-Renderer + geometrische/visuelle QA.  
**Input:** vollständige `SlideSpecs`, freigegebenes Masterlayout oder vorläufiges Token-Set, Assets mit Rechten.

**Output:** editierbare `.pptx`, `.pdf`, Einzelbilder/Contact Sheet, `render_qa.json`. Die `SlideSpec` bleibt die **inhaltliche Quelle**, nicht die gerenderte PNG-Datei.

**Checks:** Titel-/Box-Clipping, Überlagerung, Überläufe, Lesbarkeit, Farben, Datenbeispiele, Bildlizenzen, Textcode/Bildunterschiede, alle Folien gerendert.

**Gate G4:** Bildkontrolle der tatsächlichen Ausgabe. Automatische Geometriechecks sind hilfreich, ersetzen aber kein visuelles Review.

### P7 – Dozenten-/Owner-Review und Veröffentlichung

**Review:** Dozierende prüfen fachliche Anschlüsse, Tempo, realistische Aufgaben, nötige Live-Zugänge; Curriculum-Owner prüft Scope/Qualität; zuständige Person genehmigt das **konkrete** Release.

**Gate G5:** `approval.json` mit Person/Rolle, Hash/Version, Datum und Entscheidungen. Erst dann SharePoint/Ablage veröffentlichen. Keine automatische Publikation ungeprüfter Dateien.

**Nach Veröffentlichung:** versionierte Änderungsanträge, wenn neue Tools/Fakten eintreffen oder Lehrfeedback eine Anpassung auslöst.

## 7. Standard-Datenverträge (anbieterneutral)

### Minimaler DayBrief

```json
{
  "job_id": "ecomex-m03-d17-v01",
  "curriculum_version": "1.0.0",
  "module_id": "M03",
  "day_id": "D17",
  "phase": "USE",
  "status": "DRAFT",
  "audience": {
    "description": "heterogene berufserfahrene Erwachsene",
    "prior_knowledge": ["Prompting", "Use Cases auf Einzelfallniveau"]
  },
  "learning_objectives": [
    {
      "id": "M03-D17-O1",
      "action": "JSON-Felder und -Werte erkennen und plausibilisieren",
      "evidence": "annotierte Ticket-Antwort mit zwei Prüffragen"
    }
  ],
  "in_scope": ["Formate", "Datenherkunft", "API-Grundverständnis"],
  "out_of_scope": ["HTTP-Clients programmieren"],
  "schedule": {
    "timezone": "Europe/Berlin",
    "net_minutes": null,
    "blocks": [],
    "breaks": []
  },
  "case_ids": ["support_ticket_fictional_01"],
  "required_sources": ["S01", "S02", "S03", "S04"],
  "tool_access": {"live": false, "offline_fallback": true},
  "design_version": "1.0.0",
  "approval_required": true
}
```

`net_minutes: null` ist **absichtlich noch nicht entschieden**, keine angenommene Unterrichtszeit. Der Job ist vor Planung zu vervollständigen und zu validieren.

### Minimaler SlideSpec

```json
{
  "slide_id": "M03-D17-S021",
  "order": 21,
  "block_id": "json-basics",
  "learning_objective_ids": ["M03-D17-O1"],
  "slide_type": "worked_example",
  "title": "Das Ticket enthält Felder – aber keinen Liefertermin",
  "key_message": "Strukturierte Daten enthalten nur, was tatsächlich erfasst ist.",
  "visible_content": [
    "{\"ticket_id\":\"T-8124\",\"status\":\"offen\"}",
    "Keine Lieferzusage aus diesen Feldern ableitbar."
  ],
  "visual_spec": {
    "type": "annotated_data",
    "editable_shapes_preferred": true,
    "renderer_instructions": "Feldname und Wert einzeln beschriften"
  },
  "source_refs": ["S04"],
  "case_ref": "support_ticket_fictional_01",
  "estimated_minutes": 5,
  "teacher_notes": null,
  "exercise_ref": null,
  "qa_status": "PENDING"
}
```

**Sichtbarkeitsregel:** `renderer_instructions`, interne Prompts, Quellen-Snippets, YAML-Metadaten und Kontrollmarker dürfen nicht in `visible_content` rutschen. Alle Source-/SlideSpecs werden mit Schema-Validatoren geprüft.

### Freigabeobjekt

```json
{
  "release_id": "M03-D17-1.0.0",
  "artifact_sha256": "<computed_hash>",
  "qa_report_id": "QA-M03-D17-01",
  "approved_by_role": "Weiterbildungsmanagement",
  "approved_by_person": null,
  "approved_at": null,
  "status": "PENDING",
  "notes": ""
}
```

Ein `PENDING` darf **keine Release-/SharePoint-Aktion** auslösen.

## 8. Rollenzuschnitt für Single-LLM und Multi-Agent-Systeme

Rollen beschreiben **Aufgaben**, nicht verpflichtend sieben kostenpflichtige Modelle.

| Rolle | Aufgabe | Qualitätsausgabe |
|---|---|---|
| **Coordinator** | Input prüfen, Stufen steuern, Wiederaufnahme/Fehlerzustände | Job-Manifest und Zustandslog |
| **Curriculum Reader** | Lernziele, Grenzen und Prioritäten aus den fünf Regeldateien lesen | Scope-/Conflict-Report |
| **Research / SME** | Quellenaussagen prüfen und technische Aussagen fachlich validieren | belegt referenziertes `SourceBrief` |
| **Instructional Designer** | Lernziele in Tagesdramaturgie und Aufgaben übersetzen | `DayBrief`/`SlidePlan` |
| **Content Writer** | jeden Folieninhalt, Beispiel und Übung vollständig ausarbeiten | `SlideSpecs` + Übungspaket |
| **Independent QA / Critic** | quellenbasiert unabhängig prüfen, Fehler verorten | regelbasierter QA-Bericht |
| **Renderer + Render QA** | freigegebene Specs in PPTX umsetzen und Bilder prüfen | editierbare Dateien + Sichtbericht |

**Modellwahl:** Ein leistungsfähigeres Modell dort, wo Fachurteil, Didaktik, Unklarheit und Widersprüche entscheidend sind; einfachere Modelle oder klassische Parser für standardisierte Extraktion, Formatierung und Routinechecks. PPTX-Layout und JSON-Prüfung soweit möglich **deterministisch im Code**, nicht durch Sprachmodell-„Selbstvertrauen“.

**Unabhängigkeit:** Die QA-Rolle erhält die Originalquellen/Anforderungen und das zu prüfende Ergebnis, nicht nur die Behauptung des Writer-Agenten, alles sei korrekt. Unterschiedliche Modelle können hilfreich sein, aber unabhängige Prüfung hängt vor allem an **eigener Evidenz und Tests**, nicht an Markenvielfalt.

## 9. Menschliche Freigaben: minimale, aber wirksame Beteiligung

Für hohe Qualität muss nicht jede einzelne Textfolie manuell bestätigt werden. Die **wenigen entscheidenden Kontrollstellen** bleiben jedoch menschlich:

| Wann | Entscheidung durch Menschen | Was automatisiert vorliegen muss |
|---|---|---|
| **Vor Modulproduktion (G0)** | aktuelle Modulmatrix, Scope, UE und Ziele | Conflict-Report, Architekturversion |
| **Vor Tagesproduktion (G1)** | Lernziele, Fall und Tagesrealität | DayBrief mit Quelle/Agenda/Fallback |
| **Vor Ausarbeitung (G2)** | Struktur, Erklärfolge, Übungsdichte und Materialbedarf | Storyboard/SlidePlan |
| **Vor Render (G3)** | fachlich/didaktisch tragfähiger Content | QA-Report, vollständige Beispiele/Lösungen |
| **Vor Publikation (G4/G5)** | tatsächliches Deck, Tempo, Branding, kritische Fachstellen | PPTX/PDF/Renderbilder und Review-Report |

Bei etablierten, unveränderten Tagesformaten können G1/G2 im Rahmen genehmigter Templates gemeinsam gebündelt werden. **Nicht** gebündelt werden dürfen fachkritische Punkte oder die finale Freigabe, nur um „vollautonom“ zu wirken.

**Feedback externer Dozierender:** strukturiert sammeln (`issue`, `slide_id`, `evidence`, `priority`, `proposed_change`), fachlich bewerten, Konflikte diskutieren und erst nach Owner-Entscheidungen für spätere Läufe übernehmen. Das schützt die Dramaturgie davor, durch einzelne ad-hoc-Verschiebungen auseinanderzufallen.

## 10. SharePoint-/Ablagelogik

**Vorschlag**, erst nach Zustimmung:

```text
/KI-Coach-Professional-2027/
  /M03_Digitale-Ablaeufe/
    /D17/
      /_review/
      /_release/
        M03_D17_v1.0.0.pptx
        M03_D17_v1.0.0.pdf
        M03_D17_Uebungen_v1.0.0.md
        M03_D17_Loesungen_v1.0.0.md
        M03_D17_Sources_v1.0.0.json
        M03_D17_ReleaseManifest_v1.0.0.json
```

- Automationszugang erhält nur die nötigen Berechtigungen.
- **Draft/Review** und **Release** sind strikt getrennt.
- Die Engine darf nicht still vorhandene freigegebene Dateien überschreiben.
- Veröffentlichung referenziert `artifact_hash`, Freigabe-ID und exakte Version.
- Rücknahme/Korrektur erfolgt als neues Release oder dokumentierter Widerruf, nicht als heimliche Umschreibung.
- Zielordner und Schreibrechte müssen durch die ECOMEX-Verantwortlichen freigegeben sein. Dieses Dokument behauptet **keine bestehende SharePoint-Verbindung**.

## 11. Testbarkeit, Fehlerbehandlung und Kostenkontrolle

### Reproduzierbare Jobs

`job_id = hash(curriculum_version, module_id, day_id, source_versions, source_hashes, prompt_versions, schema_versions, design_version, job_parameters)`

- Gleicher Input darf dasselbe bereits freigegebene Zwischenprodukt wiederverwenden.
- Jeder Zwischenschritt speichert Version, Modell/Toolkonfiguration, Zeit/Token/Kosten soweit verfügbar, Befunde und Ergebnisdatei.
- Nach Fehler auf Folie 21 darf die Engine **nur** diesen Inhaltsblock erneut bearbeiten; nicht alle anderen 40 Folien neu erfinden.
- Wiederholungsversuche begrenzen, danach eskalieren. Kein endloser Agenten-Auto-Fix-Loop.
- Kein `ready`-Status, wenn Dateien/Tests fehlen oder Toolaufrufe gescheitert sind.

### Token-/Kostenstrategie

1. Fünf Grundsatzdateien pro Job **gezielt lesen**; nachgelagerte Agenten bekommen nur die relevanten Regeln/Versionen plus einen kurzen Shared Contract.
2. Quelle bei Bedarf anhand spezifischer Frage/ID abrufen, nicht jedes Mal komplette Hunderte-Folien-Decks in den Modellkontext laden.
3. `DayBrief`, `SlidePlan` und `SlideSpecs` persistent speichern; Modellkontext ist kein Archiv.
4. Generierung in **kleinen kohärenten Blöcken** und mit stabilen IDs.
5. Bei fachlicher Korrektur nur den Abschnitt neu prüfen/rendern, dann abhängige Regressionstests ausführen.
6. Rechen- und Formatprüfungen nicht mit teuren LLM-Aufrufen nachstellen, wenn Python/JSON-Schema/Parser deterministisch liefern.
7. Stärkere Modelle für inhaltliche schwierige Punkte, kein pauschal maximales Modell für jede Layout-/Dateioperation.
8. QA-Reports konkret und knapp halten; Quellen nur im erforderlichen Umfang erneut mitschicken.

## 12. Aktualitätsprüfung und externe Fachreferenzen

**[REGEL] Vor jedem relevanten Kurs-Release prüfen, nicht „einmal im Jahr reicht“ behaupten.** Diese offiziellen Einstiegsquellen sind Beispiele, die während der Quellenrecherche am 18.11.2026 ermittelt wurden:

- EU-Kommission: [AI Act – regulatory framework](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) und [AI Act FAQ](https://digital-strategy.ec.europa.eu/en/faqs/navigating-ai-act). **Zeitliche Anwendbarkeit kann durch geltende Rechtsakte und Änderungen beeinflusst sein**; nicht aus einer isolierten alten Folie übernehmen.
- Offizielle [MCP-Spezifikation](https://modelcontextprotocol.io/specification) und projektspezifische Versions-/Änderungsdokumentation; Beispiele auf zur Kursumgebung passende Version prüfen.
- [n8n-Dokumentation](https://docs.n8n.io/) für aktuelle Nodes, Workflows, Credentials, Integrationen und Human-in-the-Loop.
- [Microsoft Learn – Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/) für Wissensquellen, Tools/Aktionen, Berechtigungen und aktuelle UI.
- [RFC 8259 (JSON)](https://www.rfc-editor.org/rfc/rfc8259), [RFC 4180 (CSV)](https://www.rfc-editor.org/rfc/rfc4180), jeweils passend zum konkreten Lehrinhalt.

**Nicht blind veralten lassen:** URL, Abrufdatum, Dokumentversion, tatsächlich geprüfte Passage und Konsequenz für den Unterricht im SourceManifest speichern. Regulierung wird von einer zuständigen Fachperson fachlich freigegeben. Das Dokument selbst enthält **keine** verbindlichen Rechtsfristen oder festen SaaS-Preise.

## 13. Konkreter Start mit den vorhandenen ECOMEX-Materialien

**Erster sinnvoller Produktionsdurchlauf: ein repräsentativer USE-Tag, nicht sofort 16 Wochen.**

1. Fünf Regeldateien in einen gemeinsamen versionierten Ordner legen.
2. Die neun vorliegenden Originalquellen mit `S01–S09` ins Manifest aufnehmen; Hash/Locator/Dateirechte und offenen Quellenkonflikt erfassen.
3. **Curriculum-Owner** entscheidet die relevanten offenen Punkte aus `curriculum.md` und gibt einen echten ECOMEX-PPTX-Master frei, sofern verfügbar.
4. Einen **einzelnen** fachlich begrenzten Tag auswählen. Der vorhandene Tag-17/18-Test darf als **Fehler- und Lernreferenz** genutzt werden, nicht als unkritischer Inhalts- oder Layoutgenerator.
5. `DayBrief` mit Lernzielen, Zeit und gewünschtem konkreten Ergebnis erstellen und abnehmen.
6. `SourceBrief` → `SlidePlan` → ausgearbeitete `SlideSpecs` inklusive Datensatz/Übung/Lösung erzeugen.
7. Fachliches und didaktisches Review **vor** der PPTX-Produktion durchführen.
8. Erst dann rendern, alle Folien als Bild prüfen, reparieren und ein Release durch Menschen freigeben.
9. Nach einem gelungenen Tag: zweiten Tag mit **gemeinsamen Fall-/Begriffskonventionen**, danach Wochenaudit und erst dann auf weitere Module skalieren.

**Definition von „gelungen“:** Lernende verstehen und können eine Aufgabe durchführen, eine kritische Lehrperson sieht einen belastbaren roten Faden, alle Pflichtbeispiele und Lösungen stimmen, und das PPTX ist visuell/technisch brauchbar. Nicht: „Workflow ist grün durchgelaufen“.

## 14. Offene Entscheidungen für ECOMEX

**Nicht automatisch beantworten:**

- Ist die Kursarchitektur S01–S04 schon freigegeben oder bleibt sie ein Zertifizierungsentwurf?
- Wer gibt welche Gates frei und wo werden Freigaben dokumentiert?
- Welche freigegebene ECOMEX-PPTX-Vorlage samt Logo/Fontlizenzen wird benutzt?
- Wie erfolgt die verbindliche Abstimmung zwischen S03 und S04 zum frühen Daten-/JSON-Umfang?
- Welche Ablage ist führend für Originale, `.md`-Normen und Releases (Git, SharePoint oder Kombination)?
- Dürfen interne Quellen an externe Modellanbieter verarbeitet werden; welche Zugriffsstufen gelten?
- Sollen Notizen in die PPTX, als separater Leitfaden oder gar nicht – je Tagesauftrag?
- Welcher Grad an autonomer Korrektur ist für die erste Pilotphase ausdrücklich erlaubt?
- Welcher konkrete SharePoint-Ordner und welches Servicekonto sollen nach Freigabe publizieren?
- Welche Unterrichtszeiten, UE-Verteilung und Lizenz-/Accountbedingungen gelten je Kohorte?

Bis zur Antwort werden die betroffenen Felder als `OPEN` bzw. `PENDING_APPROVAL` geführt.

## 15. Änderungs- und Versionsregeln

- **Patch** `1.0.1`: sprachliche Klarstellung, ohne veränderte normative Aussage.
- **Minor** `1.1.0`: neue rückwärtskompatible Regel, Quelle oder Prüfschritt.
- **Major** `2.0.0`: geänderte Bedeutung/Scope, veränderter Datenvertrag oder wesentliche Gateveränderung.
- `ChangeRequest` dokumentiert alte/neue Fassung, Grund, Quellen, betroffene Module/Tage, Verantwortliche und Freigabe.
- Nur menschlich freigegebene Normversionen dürfen als `"approved"` veröffentlicht werden.
- Ein laufender Job referenziert **feste Normversionen**; Änderungen während der Produktion erzeugen bewussten Rebuild/Review.

## 16. Changelog

| Version | Datum | Änderung |
|---|---|---|
| 1.0.0 | 2026-11-18 | Modellneutrale Pipeline mit Quellenhierarchie, RAG-Option, Dateiverträgen, QA-Gates, Git-/n8n-/SharePoint-Anknüpfung und begrenzten menschlichen Freigaben |

Quellenkürzel `S01–S09` in `curriculum.md`. QA-Regel-IDs und Gate-Definitionen in `qa_rules.md`.
