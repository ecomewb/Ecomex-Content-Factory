# 04 · n8n-Workflows: Einrichtung, Betrieb mit und ohne Renderer

Stand: Content Factory v0.2 · n8n ab 2.46 · Supabase-Projekt *Ecomex-Content-Factory*

Die Workflows funktionieren **mit und ohne Renderer**. Ob der Renderer läuft, prüft ECOMEX 0 bei jedem Lauf
(`GET /health`, 8 Sekunden). Ist er nicht erreichbar oder fällt er mitten im Lauf aus, nimmt jeder Workflow
automatisch den Ersatzweg. Niemand muss etwas umschalten.

## 1. Die Workflows

| Nr. | Workflow | Start | Aufgabe |
|---|---|---|---|
| 0 | Regelwerk & Katalog laden | wird aufgerufen | **Einziger Ort für Einstellungen**, Renderer-Check, Regeln + Layoutkatalog live aus GitHub |
| 1 | Neues Kursdeck (Start) | Formular | Storyboard erstellen/prüfen → Tage starten |
| 2 | Tag produzieren | wird aufgerufen | Blöcke → Deck → PPTX, QA-Bericht, Manuskript, Deckdaten |
| 3 | Block produzieren (Agenten) | wird aufgerufen | Recherche → Didaktik → Layout → QA → Revision |
| 4 | Deck überarbeiten | Formular | einen Block neu erzeugen oder nur neu rendern |
| 5 | Wissensbasis befüllen | Formular | eine Fachquelle in Supabase durchsuchbar machen |
| 6 | Freigabe & Ablage | Formular | geprüftes Deck freigeben (ENTWURF entfernen) |
| 7 | Text extrahieren | wird aufgerufen | Datei → Text mit Fundstellen (Renderer oder n8n) |
| 8 | PPTX ohne Renderer (Claude) | wird aufgerufen | Ersatz-PPTX über den Claude-PPTX-Skill |
| 9 | Master an Claude übergeben | Formular, einmalig | Folienmaster für Workflow 8 hochladen |
| 10 | Ablage einlesen (Supabase) | manuell / nachts | alle neuen Dateien aus dem Bucket in die Wissensbasis |

## 2. Was mit und ohne Renderer passiert

| Schritt | mit Renderer | ohne Renderer (automatisch) |
|---|---|---|
| Vorlage lesen (WF 1, 5, 10) | PDF, PPTX, Word, Excel, Markdown | PDF (je Seite), Excel/CSV, Markdown/Text. **PPTX/Word → bitte als PDF speichern** |
| PowerPoint erzeugen (WF 2, 4) | im ECOMEX-Originalmaster, deterministisch | über **ECOMEX 8**: Claude baut die PPTX mit dem PPTX-Skill, mit Master, wenn über ECOMEX 9 hinterlegt |
| PDF-Vorschau + visuelle KI-Prüfung | ja | nein – Folien in PowerPoint sichten |
| Automatische Layoutprüfung (Überläufe …) | ja | nein – QA-Bericht weist darauf hin |
| Folien-Manuskript (HTML), Deckdaten (JSON), QA-Bericht | ja | **ja** |
| Freigabe (WF 6) | ENTWURF wird entfernt, Version in die Datei | Datei kommt zurück; ENTWURF-Textfeld in PowerPoint löschen |
| Layoutkatalog | aus GitHub, Ersatz vom Renderer | aus GitHub (`renderer/app/catalog.json`) |

Ersatzweg ganz ohne PPTX: In ECOMEX 0 `pptx_ohne_renderer` auf `aus` setzen. Dann liefern WF 2 und 4
Manuskript, Deckdaten und QA-Bericht, aber keine PowerPoint (z. B. solange die Übermittlung an Anthropic
nicht freigegeben ist).

## 3. Einrichtung (einmalig)

1. **Datenbank:** `database/001_create_kb.sql` und `database/003_content_factory_betrieb.sql` im
   Supabase-SQL-Editor ausführen (bereits erledigt im Projekt *Ecomex-Content-Factory*; beide Skripte
   sind wiederholbar).
2. **Import:** in n8n alle Dateien aus `workflows/` importieren (*Workflows → Import from File*), in der
   Reihenfolge 0, 7, 8, 3, 2, 1, 4, 5, 6, 9, 10. Namen nicht ändern.
3. **Unterworkflows verknüpfen:** In jedem Node *Call '…'* bei *Workflow → From list* den gleichnamigen
   Workflow auswählen (14 Stellen; `python3 tools/pruefe_workflows.py` listet sie).
4. **Credentials** anlegen und in den markierten Nodes auswählen:

   | Credential | Typ in n8n | genutzt in |
   |---|---|---|
   | GitHub | GitHub API (Token mit Leserecht auf das Repo) | WF 0 |
   | Supabase | Supabase API (Projekt-URL + **secret/service_role key**) | WF 3, 5, 10 |
   | OpenAI | OpenAI | WF 3 (Recherche/QA-Modelle), WF 3, 5, 10 (Embeddings) |
   | Anthropic | Anthropic | WF 1, 3 (Agenten), WF 2 (visuelle Prüfung), WF 8, 9 (HTTP Request) |
   | ECOMEX Renderer | Header Auth, Name `X-API-Key`, Wert = `RENDERER_API_KEY` | WF 0, 2, 4, 6, 7 – auch anlegen, wenn der Renderer noch fehlt |
   | SharePoint, SMTP | optional, Nodes sind deaktiviert | WF 2, 6 |

   Die Agenten bekommen **kein** Datenbank-Werkzeug: Die Suche in der Wissensbasis ist ein fester
   Schritt in WF 3, den das Modell nicht steuern kann. Der Service-Key bleibt damit außerhalb der
   Agenten-Toolauswahl (vgl. docs/03).
5. **Einstellungen** in ECOMEX 0 › *Edit Fields* prüfen (siehe Abschnitt 4).
6. **Optional, für den Weg ohne Renderer:** ECOMEX 9 einmal mit dem Master ausführen
   (Freigabe-Häkchen erforderlich) und die angezeigte `file_id` in ECOMEX 0 › `claude_master_file_id` eintragen.
7. **Wissensbasis füllen:** ECOMEX 10 zuerst mit `probelauf: true` ausführen, Bericht prüfen, dann mit
   `probelauf: false`.
8. **Prüfen:** `python3 tools/pruefe_workflows.py workflows/*.json` → *0 Fehler*.

## 4. Einstellungen (ECOMEX 0 › Edit Fields)

| Feld | Standard | Bedeutung |
|---|---|---|
| `github_owner`, `github_repo`, `branch` | ecomewb / Ecomex-Content-Factory / main | Quelle der Regeln und des Katalogs |
| `regel_ordner` | governance | alle `.md` darin werden geladen; Pflicht: curriculum, didaktik, design, qa_rules, content_workflow |
| `katalog_pfad` | renderer/app/catalog.json | Layoutkatalog der Agenten (derselbe, den der Renderer nutzt) |
| `renderer_url` | http://ecomex-renderer:8080 | leer lassen = immer ohne Renderer |
| `supabase_url`, `supabase_bucket` | Projekt-URL / ecomex-sources | für Ablage-Upload und Import |
| `wissensbasis_referenzen` | true | Agenten nutzen auch Quellen mit Status *reference*; `false` = nur *approved* |
| `pptx_ohne_renderer` | claude | `claude` = Ersatz-PPTX über ECOMEX 8, `aus` = ohne PPTX |
| `claude_pptx_modell` | claude-sonnet-5-5 | Modell für ECOMEX 8 |
| `claude_master_file_id` | leer | aus ECOMEX 9; leer = Claude baut ohne Master in ECOMEX-Farben |
| `anthropic_version`, `code_execution_tool` | 2026-10-21 / code_execution_20260521 | API-Stand für den PPTX-Skill; nur bei API-Änderungen anpassen |

## 5. Wissensbasis (Supabase)

- **Tabellen:** `ecomex_sources` (eine Zeile pro Quelle), `ecomex_documents` (Abschnitte mit Embedding).
  `source_id` und `embedding_model` in `ecomex_documents` werden automatisch aus den Metadaten gebildet.
- **Embeddings:** nur `text-embedding-3-small` (1536 Dimensionen). Die Datenbank lehnt Abschnitte mit
  anderem oder fehlendem Modell ab (Migration 003), damit die Suche nie Äpfel mit Birnen vergleicht.
- **Suche:** `ecomex_match_documents` liefert nur *approved* und – solange erlaubt – *reference*;
  *restricted* nie.
- **Ablage-Inventar:** `ecomex_storage_inventory()` entscheidet für ECOMEX 10, was eingelesen wird:
  neue Dateien; PPTX/Word nur, wenn keine PDF-Fassung im selben Ordner liegt; Folienmaster und
  Storyboards nie; bereits eingelesene Dateien werden übersprungen. `ecomex_kb_status()` zeigt den Stand.
- **Große Dateien:** ECOMEX 10 überspringt Dateien über `max_mb` (Standard 60 MB) und listet sie im
  Bericht. Große PPTX (z. B. 100–400 MB durch Videos/Bilder) bitte als PDF exportieren und in denselben
  Ordner legen – dann wird automatisch die PDF genommen.
- **Duplikate:** ECOMEX 5 prüft die SHA-256-Prüfsumme und legt nichts doppelt an.

## 6. Später in n8n ändern – ohne etwas kaputt zu machen

Die Workflows dürfen in n8n weiterentwickelt werden. Diese Punkte halten das Zusammenspiel stabil:

1. **Node-Namen:** Ausdrücke greifen per Name auf andere Nodes zu (`$('Edit Fields1')`). Beim
   Umbenennen im Editor passt n8n die Verweise an; beim **Löschen und Neuanlegen** nicht. Danach immer
   den Prüfer laufen lassen.
2. **End-Nodes nicht entfernen:** Unterworkflows liefern das Ergebnis über ihren letzten Node –
   *No Operation, do nothing* in ECOMEX 0, 7 und 8. Neue Schritte **vor** diesem Node einfügen.
3. **Verträge zwischen den Workflows** (Felder, auf die sich andere verlassen):

   | Workflow | erwartet | liefert |
   |---|---|---|
   | ECOMEX 0 | beliebige Felder; `nur_konfig: true` = schnell | alle Eingangsfelder + `konfig` {…Einstellungen, `renderer_aktiv`, `renderer_status`}; ohne `nur_konfig` zusätzlich `regeln`, `regel_versionen`, `katalog` |
   | ECOMEX 7 | Datei im Binärfeld `datei`, `konfig` | `abschnitte[{fundstelle,text}]`, `text`, `zeichen`, `source_type` (pdf/pptx/docx/md/other), `hinweis`, `extraktion` |
   | ECOMEX 8 | `deck`, `konfig`, `design_regeln`, `katalog` | Binärfeld `pptx` (falls erzeugt), `pptx_quelle` (claude/keine), `hinweis`, `master_verwendet` |
   | ECOMEX 3 | `zeile`, `tagesuebersicht`, `regeln`, `katalog`, `konfig`, optional `revision` | `folien[]`, `qa`, `quellen` |

4. **Dateien weiterreichen:** *Edit Fields* entfernt Binärdaten, wenn *Include Other Input Fields* aus
   ist; *Crypto* (Hash einer Datei) gibt die Datei ebenfalls nicht weiter. Wo eine Datei hinter dem Node
   gebraucht wird, *Include Other Input Fields* einschalten bzw. die Datei aus einem früheren Node holen.
5. **Neue Einstellungen** nur in ECOMEX 0 › *Edit Fields* anlegen; sie sind dann überall als
   `$json.konfig.<name>` verfügbar.
6. **Prüfen nach jeder Änderung:** Workflows in n8n exportieren (*… → Download*) und
   `python3 tools/pruefe_workflows.py <Dateien>` ausführen. Der Prüfer meldet fehlende Node-Verweise,
   kaputte `{{ }}`, fehlende Einstellungen und entfernte End-Nodes. Danach die Exporte nach `workflows/`
   committen – **der Export aus n8n ist ab dann die maßgebliche Fassung**; `tools/generator/` dient nur
   dem Neuaufbau.
7. **Ausdrucks-Tests (optional, für Entwickler):** `cd tools/tests && npm install --ignore-scripts &&
   node test_workflows.js` prüft die wichtigsten Ausdrücke mit der echten n8n-Engine.

## 7. Häufige Meldungen

| Meldung | Ursache | Lösung |
|---|---|---|
| QA-Bericht: „Renderer nicht erreichbar – Weg ohne Renderer (…ENOTFOUND…)“ | Renderer-Container läuft nicht / anderes Docker-Netz | `docker compose up -d` im Ordner `renderer/`; Netzname prüfen |
| „Dateityp .pptx kann ohne Renderer nicht gelesen werden“ | kein Renderer | Datei als PDF speichern oder Renderer starten |
| „Claude hat keine PowerPoint-Datei geliefert“ | Zeitlimit/Überlast beim Ersatzweg | Lauf wiederholen; Manuskript nutzen; Renderer bevorzugen |
| „Katalog im Renderer (v…) weicht von GitHub (v…) ab“ | Katalog geändert, Renderer nicht neu gebaut | `docker compose up -d --build` |
| „Regelwerk unvollständig …“ | Pflicht-`.md` fehlt/umbenannt im Regel-Ordner | Dateien in `governance/` prüfen |
| ECOMEX 10: Datei „zu groß“ | über `max_mb` | als PDF exportieren oder `max_mb` erhöhen |
