---
document_id: ecomex.optional_method.ki_kuratierte_projektreise
title: "ECOMEX | Optionale KI-kuratierte Projektreise – Didaktik und Guardrails"
version: "0.2.0"
status: "proposed_for_review_repository_checked"
last_reviewed: "2026-11-19"
language: "de-DE"
method_id: "guided_project_journey"
active_by_default: false
owner_role: "ECOMEX Weiterbildungsmanagement / Content-Verantwortung"
applies_to: ["ausgewählte Modul-/Tagesbriefs", "Projektübungen", "Dozentenhinweise", "didaktische QA"]
depends_on: ["curriculum.md", "didaktik.md", "qa_rules.md", "content_workflow.md", "design.md"]
---

# Optionale KI-kuratierte Projektreise

> **Status und Reichweite:** Ergänzendes didaktisches Muster zur Prüfung und Pilotierung, **keine sechste globale Pflichtnorm** und keine Änderung der bestehenden Curriculums-, Design- oder Qualitätsstandards. Diese Datei wird nur geladen, wenn eine zuständige Person die Methode im konkreten `ModuleBrief`/`DayBrief` aktiviert. Eine Erwähnung von „Agenten“, „Projekten“ oder „Vibe Coding“ aktiviert sie **nicht automatisch**.

## 1. Anlass und Kernidee

**Anlass:** Besprechungsnotizen zum Vorschlag von Sebastian (19.11.2026, vom Auftraggeber zusammengefasst), ergänzt um eine **Quellensichtung des öffentlich zugänglichen Repositories** [Jukoi/vibe-coding-wizard](https://github.com/Jukoi/vibe-coding-wizard) am 19.11.2026. Der Wizard umfasst einen zentralen Claude-Projektprompt, elf phasenspezifische Prompts und Hilfedateien. Die dokumentierte Journey reicht von Idee, Wireframes, Style Guide und Design über Lovable-Umsetzung und optionale Datenbank/KI-Funktion bis zu Pitch und optionalem GitHub-Export. **Dies ist eine ausgewählte Quellensichtung, kein getesteter End-to-End-Durchlauf.**

**Unser redaktioneller Vorschlag:** Den Ansatz **selektiv** als *begleitete, realitätsnahe Projektarbeit* verwenden. Der Mehrwert liegt in einem nachvollziehbaren beruflichen Arbeitsprozess mit prüfbaren Entscheidungen, nutzbaren Artefakten, Feedback und Transfer – **nicht** darin, dass Teilnehmende einem KI-Agenten möglichst fehlerlos folgen oder immer ein Softwareprodukt erzeugen.

**Verbindliche Schutzthese für Pilotierungen:** KI soll die Entwicklung von Urteil, Methodenkompetenz und Handlungsfähigkeit **unterstützen, nicht ersetzen**. Ein hochwertiges Endprodukt beweist für sich genommen noch keinen Kompetenzgewinn.

## 1a. Repositorybefund: tatsächliche Funktionsweise und ECOMEX-Relevanz

**Aus dem Repository belegbar (Stand 19.11.2026):**

| Baustein | Umsetzung im Original | Didaktische Bewertung für ECOMEX |
|---|---|---|
| Zentrale Projektanweisung | Rolle als Product-/UX-Partner, ein neuer Claude-Chat je Phase, einheitliches Antwortformat, `weiter`/`zurück`/`Hilfe`/`Stand` | Gut reproduzierbare Führung; Chat-Grenze ist eine konkrete Umsetzung, **kein zwingender ECOMEX-Standard** |
| Elf Phasen | 01 Idee, 02 Wireframes, 03 Style Guide, 04 Design, 05 Lovable-Start, 06 Iteration, optional 07 Datenbank, 08 KI-Funktion, 09 Pitch, optional 10–11 GitHub | **App-Entwicklungsspezifischer Pfad**, nicht auf sämtliche ECOMEX-Module übertragbar |
| Übergaben | `STECKBRIEF`, `ÜBERGABE WIREFRAMES`, `STYLE GUIDE`, Projektbuch (max. 2.000 Zeichen), später Datenmodell/KI-Steckbrief | Sehr gut als **Muster für phasenübergreifende Artefaktübergaben**; nicht als neues Pflichtformat im Curriculum |
| Initiative des Wizards | Agent zeigt Vorschläge und Multiple-Choice-Optionen, die erste Option ist standardmäßig empfohlen; `weiter` übernimmt die Empfehlungen | Niedrige Einstiegshürde; **Risiko des unreflektierten Durchklickens** bei Lernenden |
| Vorhandene Eigenleistung | Die Produktidee wird am Lebenskontext entwickelt; Entscheidungen trifft laut Phase 01 der Lernende; in Phase 06 wird ein freiwilliger Lernmodus für selbst formulierte User Stories angeboten | **Nicht behaupten, der Wizard nehme Menschen alle Entscheidungen ab**. ECOMEX sollte die Eigenleistung an ausgewählten Stellen **verbindlich sichtbar machen** |
| Bestehende Qualitäts-/Sicherheitsregeln | Phase 06: testbare Akzeptanzkriterien, sichere Secrets, Änderungsabgrenzung; Phase 07: Datenminimierung, Rollenrechte/RLS und Test mit Beispieldaten | Gute technische Guardrails **anerkennen und nicht doppelt erfinden**; echte Prüfungen sind dennoch erforderlich |
| Pitch | Phase 09 sieht eine feste Erzählfolge und bis zu acht Slides vor; Schätzungen sind zu kennzeichnen | Gut für eine **konkrete App-Pitch-Übung**, aber kein universelles Denk-/Präsentationsschema oder Ersatz für begründete Entscheidung |

**Aus den gesichteten Dateien nicht als verbindlicher Standard erkennbar:** eine abschließende **eigenständige Transferprüfung ohne Wizard-Führung**, eine ausdrücklich erforderliche **Gegenprüfung des vorgeschlagenen Phasenmodells** und eine **gewichtete Kompetenzbewertung**, die Eigenleistung klar von Produktglanz trennt. Dies ist eine **Lücke in der gesichteten Spezifikation**, kein Nachweis, dass Sebastian solche Elemente im Unterricht nicht bereits praktiziert.

**Quellen:** [README und Gesamtübersicht](https://github.com/Jukoi/vibe-coding-wizard), [00 Projektanweisung](https://github.com/Jukoi/vibe-coding-wizard/blob/main/projekt-dateien/00%20-%20Projektanweisung%20(System-Prompt).md), [01 Idee finden](https://raw.githubusercontent.com/Jukoi/vibe-coding-wizard/main/projekt-dateien/Phase%2001%20-%20Idee%20finden.md), [06 Iterieren](https://raw.githubusercontent.com/Jukoi/vibe-coding-wizard/main/projekt-dateien/Phase%2006%20-%20Iterieren.md), [07 Datenbank](https://raw.githubusercontent.com/Jukoi/vibe-coding-wizard/main/projekt-dateien/Phase%2007%20-%20Datenbank.md), [09 Pitch Deck](https://raw.githubusercontent.com/Jukoi/vibe-coding-wizard/main/projekt-dateien/Phase%2009%20-%20Pitch%20Deck.md). Es wurden **nicht alle Dateien unter Live-Unterrichtsbedingungen getestet**.

**Übernahmeentscheidung (Vorschlag, nicht freigegeben):** Als **didaktisches Pattern** übernehmen: kurze Phasen, explizite Übergaben, nachvollziehbares Projektbuch, differenzierte Hilfen, kleine Änderungsaufträge, Testkriterien und Sicherheit. **Nicht als globale Norm übernehmen:** elf Phasen, Claude-Neuchat-Pflicht, Lovable/Stitch/Supabase/GitHub-Kette, feste Pitch-Gliederung, empfehlungsbasierte Multiple-Choice-Bedienung, visuelle Gestaltung aus dem Projekt statt ECOMEX-Design.

## 2. Nicht verhandelbare Bestandsschutzregeln

1. **Curriculum bleibt führend:** `curriculum.md` mit USE → BUILD → TRANSFORM → ENABLE, Modul-Outcomes, Scope-Grenzen und freigegebenen Kompetenzen hat Vorrang. Der Ansatz darf keine zusätzlichen Pflichtmodule, UE, Zertifizierungsziele oder Modulverschiebungen erzeugen.
2. **Didaktik bleibt führend:** `didaktik.md` bestimmt Niveau, fachliche Tiefe, praktische Tool-Anwendung, Kern-/Plus-Differenzierung, vollständige Aufgaben und Zeitrahmen. Keine pauschale Verschiebung in Softwareentwicklung, Daten-/API-Fälle oder technisches Projektmanagement.
3. **Qualität und Freigaben bleiben führend:** `qa_rules.md` und `content_workflow.md` gelten unverändert; diese Ergänzung fügt Prüffragen hinzu, ersetzt keine Prüfung und umgeht keine Gates.
4. **Erscheinungsbild bleibt ECOMEX:** `design.md` und der freigegebene ECOMEX-Folienmaster bestimmen Logo, Schriftarten, Farbpalette, Layoutsystem und visuelle Dramaturgie. Die „Consulting“-Anmutung bezeichnet **analytische Qualität, Entscheidungsklarheit und gute Storyline**, **nicht** einen BCG-Stilwechsel, neue Markenfarben oder zusätzliche Folienkonventionen.
5. **Unterschiedliche berufliche Fälle bleiben zulässig:** Kein verpflichtender Konzern-/Startup-Fall, kein genereller Nordwind-Zwang, kein universelles Pitch Deck/GitHub-Repository. Artefakte folgen dem fachlichen Lernziel.
6. **Unterrichtszeiten bleiben fest:** Montag–Donnerstag 09:00–15:00 Uhr, Freitag 09:00–13:00 Uhr; keine Verlängerung. Pausen explizit im `DayBrief`, Planungsblöcke von 15/30/45/60 Minuten. Kein zusätzlicher Prozessschritt ohne reale Zeitdeckung.

**Konfliktregel:** Bei einer Kollision gilt immer die übergeordnete, aktuell freigegebene Norm. Der Agent erzeugt `needs_decision`, niemals eine stille Überschreibung. Noch nicht freigegebene Planungsregeln bleiben als solche gekennzeichnet.

## 3. Einsatzbereich: wo die Methode sinnvoll ist

**Geeignet, falls ausdrücklich gewählt:**

- **USE, vor allem M02 (Woche 3):** Beruflichen Use Case durchlaufen: Problem → Zielgruppe → Alternativen → überprüfbare Entscheidungsvorlage. **Kein** Vorgriff auf produktive Automatisierungen oder eine vollständige App.
- **M06 Design Thinking:** Nutzungsproblem, Hypothesen, mögliche Lösungswege und Validierung gestalten. KI-Vorschläge ersetzen keine echten Nutzungsbelege.
- **M07 Vibe Coding:** Geeignet für eine kohärente Projektjourney mit Anforderungen, UI, Prototyp, Test, Iteration und begründetem Vorgehen – innerhalb des tatsächlich freigegebenen Unterrichtsumfangs.
- **M08 KI-Strategie:** Optional für Business Case, Optionenvergleich, Risiken, Entscheidungspräsentation. Ein schön gestaltetes Pitch Deck ersetzt keine belastbaren Annahmen.
- **M09 Agile Methoden oder M12 Abschluss:** Als mögliches Verbindungs-/Reflexionsformat, wenn es die **spezifischen** Modulziele ergänzt.

**Nicht pauschal einsetzen:** Als universellen 16-Wochen-Rahmen, als Ersatz für Grundlagenvermittlung, als Standard für jede Tool-Demo, als Zwangssequenz in allen Modulen oder ohne begründeten Kompetenznutzen. Der Einsatz in M03 (Woche 4) darf nicht zur eigenständigen Build-/App-Entwicklung werden; dort steht Verständnis von Lösungs- und Datenwegen im Vordergrund.

**Aktivierung nur, wenn alle Kriterien erfüllt sind:**

- Ein freigegebenes Lernziel erfordert tatsächlich eine mehrstufige Entscheidung oder ein zusammenhängendes Arbeitsprodukt.
- Die erforderlichen Vorkenntnisse, Toolzugänge, Materialien, Lösungen und Alternativpfade sind vorhanden.
- Innerhalb der Netto-Lernzeit bleibt genügend Raum für eigenständiges Denken, Test, Kritik und Transfer.
- Der zusätzliche Aufwand gegenüber einer normalen Praxisübung ist didaktisch begründet.
- Der Verantwortliche hat die Methode ausdrücklich im konkreten Brief aktiviert.

## 4. Didaktischer Mechanismus: Führung reduzieren, Eigenständigkeit erhöhen

**Dies sind Lernfunktionen, kein starres Vier-/Sechs-Phasen-Rezept.** Reihenfolge, Anzahl und Länge werden aus Problem und Lernziel bestimmt. Rücksprünge und alternative Wege sind legitim.

| Lernfunktion | Zunächst zulässige KI-Hilfe | Verlangte Eigenleistung | Beobachtbarer Kompetenznachweis |
|---|---|---|---|
| **Problem klären** | Verständnisfragen und Strukturierungsimpulse | Problem, Nutzer, Erfolgskriterien selbst formulieren | eigener erster Problemrahmen |
| **Optionen entwickeln** | Möglichkeiten, Gegenargumente und blinde Flecken | mindestens eine eigene Alternative vor KI-Empfehlung | kurzer Optionenvergleich |
| **Entscheiden** | Kriterien und Risiken sichtbar machen | Vorgehen begründen, KI-Empfehlung annehmen, ändern oder verwerfen | Decision Log mit Begründung |
| **Umsetzen / testen** | Bei Bedarf Anleitung, Beispiel, Hilfestellung | passendes Ergebnis selbst prüfen und iterieren | überprüftes Arbeitsartefakt/Testbefund |
| **Transfer** | Rückfragen, Feedback und Gegenbeispiele | neuen Fall ohne vorgegebene Schrittfolge strukturieren | kurze unabhängige Transferleistung |

### Drei Unterstützungsmodi

- **A – Geführter Einstieg:** Der Agent erklärt auf Anfrage, zeigt ein vollständig ausgearbeitetes Beispiel und bietet abgestufte Hinweise. Geeignet für unbekannte Methoden und Zugänge.
- **B – Kritische Ko-Kreation:** Die Teilnehmenden machen eigene Vorschläge und vergleichen diese mit Alternativen. Der Agent fragt nach Belegen, Annahmen und Risiken, statt eine Musterlösung vorzugeben.
- **C – Eigenständiger Transfer:** Erst eigene Struktur/Entscheidung, dann KI für begrenzte Recherche, Prüfung oder Verfeinerung. Abschließend eine kurze Begründung **ohne Agentenführung**.

**Scaffolding-Fading:** Hilfen werden gezielt reduziert, wenn die Gruppe bereit ist. Das ist eine didaktische Steuerungsregel, **keine** pauschale Quote und kein Automatismus nach Folienzahl oder Zeit. Notwendige Barrierefreiheit und Basishilfen bleiben verfügbar.

## 5. Guardrails gegen Deskilling, Abhängigkeit und Schema-Denken

| ID | Risiko | Regel für Agent und Unterricht | Nachweis |
|---|---|---|---|
| `KLP-01` | **Deskilling / kognitive Auslagerung** | Vor zentralen KI-Lösungsvorschlägen zumindest eine eigene Hypothese, Skizze oder Entscheidung einfordern; Ausnahmen (z. B. erste Demonstration) bewusst markieren. | eigener Erstentwurf oder kurze mündliche Position |
| `KLP-02` | **KI-Abhängigkeit** | Mindestens eine Transferaufgabe ohne kuratierte Schritt-für-Schritt-Führung vorsehen; KI darf danach zur Prüfung genutzt werden. | unabhängige Strukturierung und Reflexion |
| `KLP-03` | **Starres Schema-Denken** | Phasen dürfen ausgelassen, umgestellt oder wiederholt werden, sofern begründet; mindestens eine alternative Methode oder ein Gegenfall betrachten. | begründete Prozessabweichung/Alternativenprüfung |
| `KLP-04` | **Musterlösungsillusion** | Agentenergebnisse als Vorschläge behandeln; nicht einen einzigen Ablauf als einzig richtige Antwort werten. Musterlösungen erklären zulässige Alternativen. | Bewertung anhand von Kriterien statt Prompt-Identität |
| `KLP-05` | **Schein-Kompetenz durch schöne Artefakte** | Bewertet werden Entscheidung, Richtigkeit, Test, Reflexion und Transfer; Ästhetik allein erfüllt kein Lernziel. | Kompetenzrubrik + kurze Ergebnisverteidigung |
| `KLP-06` | **Methodische Bevormundung** | Agent darf nachfragen, Optionen anbieten und Widersprüche sichtbar machen, aber keine ungesicherte Nutzerabsicht, Lösung oder Methodik als verbindlich festsetzen. | dokumentierte, menschliche Entscheidungen |
| `KLP-07` | **Tool-/Phasen-Overload** | Nur die für das Ziel erforderlichen Werkzeuge und Schritte nutzen; kein verpflichtendes Wireframe, Pitch Deck, Repository oder Coding ohne Modulbezug. | Modul-/DayBrief-Abgleich |
| `KLP-08` | **Falsche Fakten / erfundene Evidenz** | Quellen und Behauptungen separat prüfen; nicht verifizierte Ergebnisse markieren. Produktdemos und Schnittstellen nur nach Zugangstest zeigen. | Quellen-/Testnachweise |
| `KLP-09` | **Unfaire Heterogenität** | KERN-Pfad mit realistischen Hilfen und optionaler PLUS-Aufgabe bereitstellen; Plus ist keine versteckte Pflicht. | zwei differenzierte Pfade, gleiches Kernlernziel |
| `KLP-10` | **Datenschutz / Berechtigungen** | Nur freigegebene Accounts und Daten; fiktive/geeignet anonymisierte Fälle bevorzugen. Keine externen Schreib-/Publikationsaktionen ohne explizite menschliche Freigabe. | Tool-/Rechteprüfung, Freigabevermerk |
| `KLP-11` | **Promptabhängigkeit / Wartungslast** | Agenten in kleine phasenbezogene Anweisungen trennen, versionieren, testen. Kein monolithischer Superprompt als einzige Wissensquelle. | Versions- und Testprotokoll |
| `KLP-12` | **Abhängigkeit von Toolverfügbarkeit** | Für jede Kernaufgabe einen fachlich gleichwertigen Offline-/Demo-Fallback vorsehen; keine Pflichtleistung, die ausschließlich an einem kostenpflichtigen Account scheitert. | Fallback-Material, erprobter Alternativpfad |
| `KLP-13` | **Curriculum- und Markenverwässerung** | Keine Änderung an Kompetenzphasen, Modulzielen, Zeiten oder ECOMEX-Design. Beratungsähnliche Ergebnisqualität ist **keine** neue Corporate Identity. | Norm- und Render-QA |
| `KLP-14` | **Überautomatisierung** | Agent darf nicht selbst die didaktische Eignung seiner Methode oder sein Ergebnis freigeben. Entscheidungen und Release-Gates bleiben bei Menschen. | dokumentierte Gate-Freigaben |

### Repositorybezogene Zusatz-Guardrails (Pilot, nach Freigabe)

| ID | Trigger aus dem Original-Wizard | Zusätzliche ECOMEX-Regel | Prüfnachweis |
|---|---|---|---|
| `KLP-15` | Befehl `weiter` übernimmt standardmäßig Empfehlungen | Bei **fachlich oder methodisch wesentlichen** Entscheidungen keine automatische Annahme durch ein einziges `weiter`. Lernende formulieren vor Freigabe ein eigenes Kriterium oder einen Grund; bei rein organisatorischen Schritten bleibt Schnellfortschritt erlaubt. | Entscheidungsbegründung statt Klickprotokoll |
| `KLP-16` | Phase 06 bietet Eigenformulierung nur als optionalen Lernmodus | An mindestens einem **geeigneten** Entscheidungspunkt je ausgewählter Projektreise ist ein kurzer **Human-first-Versuch** verbindlich; danach darf KI unterstützen. Hilfen bleiben für Basispfad/Barrierefreiheit verfügbar. | eigener Entwurf plus Feedback |
| `KLP-17` | Phasenfolge ist app-spezifisch; Phase 09 verwendet ein Pitch-Framework | Lehrperson muss bei mindestens einer Gelegenheit erklären lassen, **warum** eine Phase oder Darstellungsform gewählt wurde und **welche Alternative** ebenfalls vertretbar wäre. | kurzer Methodenvergleich oder dokumentierte begründete Abweichung |
| `KLP-18` | Die Repository-Spezifikation führt bis zu Pitch/Repository | Bewertungsabschluss enthält eine **neue, kleine Transferaufgabe** ohne vorgelesene Wizard-Schritte. Nicht das fertige Artefakt allein, sondern eigenständige Problemstrukturierung und Begründung zählen. | eigenständiger Transfernachweis, separat vom Pitch |

**Pilotregel:** Diese vier Prüfungen werden nur bei aktiver Methode in das bestehende `qa_rules.md`-Regelsystem eingespeist. Sie sind **zusätzlich**, nicht als Ersetzung für `DID-*`, `CUR-*`, `VIS-*` oder `KLP-01` bis `KLP-14` gedacht. Ein `weiter` ist nicht per se problematisch; relevant ist sein Einsatz zur stillschweigenden Übernahme von inhaltlichen Entscheidungen.

### Verhalten des KI-Lernbegleiters

**Tun:** Rückfragen stellen, einen nächsten sinnvollen Schritt anbieten, Optionen gegenüberstellen, auf Annahmen hinweisen, bei Bedarf konkrete Beispiele erklären, Reflexionsfragen stellen, Kriterien anbieten, widersprüchliche Ergebnisse sichtbar machen.

**Nicht tun:** Bereits zu Beginn die vollständige Musterlösung ausgeben; alle Entscheidungen im Namen der Lernenden treffen; automatisch zu einer nächsten Phase springen; eine Methode als alternativlos darstellen; Texte nur nach äußerer Professionalität bewerten; eigenmächtig Toolrechte erteilen, Daten veröffentlichen oder das Curriculum ändern.

**Bei Blockade:** Erst Hinweis auf das Ziel, dann kleine Hilfestellung, dann ausgearbeitetes Teilbeispiel. Vollständige Lösung nur bei didaktischer Freigabe, beispielsweise in der gemeinsamen Nachbesprechung. Das Lernziel darf trotzdem nicht durch künstliches Zurückhalten notwendiger Barrierefreiheits- oder Basishilfen unerreichbar werden.

## 6. Optionale Artefakte – nicht als allgemeine Pflichtliste

| Artefakt | Geeignet, wenn … | Kein Selbstzweck |
|---|---|---|
| Use-Case-Steckbrief | Problem/Nutzen/Machbarkeit beurteilt werden | nicht für jede einfache Toolübung |
| Problem-/Hypothesenblatt | Nutzendenbedarf erkundet wird | KI-generierte Persona ist keine Nutzervalidierung |
| Kriterienbasierter Optionenvergleich | eine reale Entscheidung ansteht | nicht in jeder Unterrichtseinheit ein Framework |
| Wireframe / UI-Mock-up | Gestaltung oder Interaktion Lerngegenstand ist | nicht in Strategie-/Grundlagenblöcken erzwingen |
| Testprotokoll / Iterationslog | Lösungsqualität überprüft wird | konkrete Testfälle statt hübscher Statusampeln |
| Decision Log | Entscheidungen und Alternativen nachvollziehbar sein sollen | knapp halten; keine zusätzliche Dokumentationsbürokratie |
| Pitch / Management Summary | verständliche Kommunikation und Verteidigung Teil des Ziels ist | kein BCG-Designklon, keine standardisierte Pitch-Show |
| GitHub-Repository | Code/Versionierung fachlich erforderlich und Zugang erlaubt ist | **nicht** pauschaler Abschlussnachweis |

**Minimum für eine Projektreise:** ein zum Lernziel passendes Arbeitsergebnis **und** eine nachvollziehbare eigene Entscheidung bzw. Reflexion. Ein Team darf auch auf ein Präsentations-, Prozess-, Kommunikations- oder Beratungsergebnis hinausarbeiten statt auf Software.

## 7. Betriebslogik für die ECOMEX Content Engine

### Aktivierung im Brief (Beispiel; Zusatzfelder, noch kein verabschiedetes JSON-Schema)

```yaml
learning_method:
  id: "guided_project_journey"
  enabled: true                   # nur nach expliziter Freigabe
  approval_status: "PENDING"     # erst APPROVED schaltet die Engine frei
  activation_reason: "Mehrstufige Lösungsbewertung und praktischer Transfer"
  learning_objective_ids: ["M07-O2"]
  permitted_scope: ["Anforderungen", "UI", "Prototyp", "Tests"]
  not_in_scope: ["produktiver Betrieb", "GitHub-Pflicht"]
  learner_autonomy_target: "eigenständige Wahl und Begründung des Lösungswegs"
  chosen_artifacts: ["entscheidungslog", "prototyp", "testprotokoll"]
  support_modes: ["guided", "critical_cocreation", "independent_transfer"]
  decision_checkpoint_required: true  # KLP-15
  human_first_checkpoint_required: true # KLP-16
  alternative_method_checkpoint_required: true # KLP-17
  transfer_assessment_required: true
  tool_fallback_required: true
  reviewed_by: null
```

`enabled: true` allein genügt **nicht**: Ohne reale Freigabe (`approval_status: APPROVED` und verantwortliche Person im Produktionsdatensatz) bleibt die Methode inaktiv.

### Einbindung entlang der bestehenden Pipeline

- **P0 – Auftrag:** Prüfen, ob die Option aktiviert und genehmigt ist; normative Versionsstände und Rechte fixieren.
- **P1 – SourceBrief:** Relevante Fachquellen und bereits vermittelte Kompetenzen abrufen; keine zusätzlichen Module erfinden.
- **P2 – DayBrief:** Lernziel, geeignete Projektdauer, Modusfolge, konkrete Agenda, Basis-/Plus-Pfad und Fallback festlegen.
- **P3 – SlidePlan / Gate G2:** Fachliche Storyline und notwendige Übungs-/Reflexionsphasen prüfen. **Hier** entscheiden, ob die Methode mehr leistet als eine normale Übung.
- **P4 – SlideSpecs:** Reale Arbeitsmaterialien, Hilfestufen, Musterlösungen, Kriterien und Dozentennotizen ausarbeiten. Der Agentenablauf erscheint nur so weit auf Folien, wie er unterrichtlich sinnvoll ist.
- **P5 – Content-QA / Gate G3:** Prüffragen `KLP-01` bis `KLP-14` ergänzen; keine Pseudonachweise.
- **P6 – PPTX / Gate G4:** Ausschließlich freigegebene ECOMEX-Layouts verwenden. Keine grafische Fremdidentität oder zusätzliches Pflicht-Folienritual.
- **P7 – Dozentenreview / Gate G5:** Unterrichtbarkeit, Eigenleistung und Kompetenztransfer validieren; anschließend Veröffentlichung nach realer menschlicher Freigabe.

**n8n/Supabase:** n8n orchestriert die bestehenden Schritte, Supabase speichert Quellen, gewählte Methode, zugehörige Artefakte/Prüfbefunde und Referenzen. Die Norm selbst bleibt als versionierte `.md`-Datei maßgeblich; ein RAG-Treffer aktiviert die Methode **niemals** eigenständig. Keine zusätzlichen LLM-Runden, wenn die Option nicht verwendet wird.

### Menschliche Rollen

- **Curriculum-/Content-Verantwortung:** entscheidet über Modul-/Tag-Einsatz und Freigabe des Storyboards.
- **Dozent/in:** steuert Hilfentiefe, Tempo und Abweichungen entsprechend realem Lernstand; hinterlegt Feedback.
- **Lernende:** formulieren Hypothesen, wählen und begründen Optionen, testen Ergebnisse und reflektieren ihre Entscheidungen.
- **Agent:** unterstützt und dokumentiert, entscheidet nicht stellvertretend über Lernzielerreichung oder Publikation.

## 8. QA-Zusatz: Freigabekriterien und Fehlergewichtung

Die folgenden Regeln sind **zusätzlich** zu `qa_rules.md`, nicht dessen Ersatz. Für aktivierte Projektreisen gilt:

| Kriterium | Evidenz / Mindestprüfung | Schwere bei Verstoß |
|---|---|---|
| Eigenleistung sichtbar (`KLP-01`, `02`, `16`, `18`) | eigener Ansatz + Transfer ohne Schritt-für-Schritt-Agent | **MAJOR**, bei vollständig fehlendem Kompetenznachweis **BLOCKER** |
| Methodenfreiheit (`KLP-03`, `04`, `06`, `15`, `17`) | zulässige Alternativen und begründete Abweichung möglich | **MAJOR** |
| Kompetenz statt Hochglanz (`KLP-05`) | Bewertung von Begründung, fachlicher Richtigkeit, Test und Reflexion | **MAJOR** |
| Modulspezifischer Scope (`KLP-07`, `13`) | `ModuleBrief`/`DayBrief` und Normversionen eingehalten | **BLOCKER** bei unautorisiertem Curriculum-/Designwechsel |
| Zugänge, Datenschutz, Fallback (`KLP-08`, `10`, `12`) | belegte Quelle/Rechte, geprüfte Zugänge, Alternativpfad | **BLOCKER** bei Daten-/Sicherheitsproblem, sonst **MAJOR** |
| Promptwartung/Freigaben (`KLP-11`, `14`) | Versionen, Tests, reale Approval-Datensätze | **BLOCKER** bei unerlaubter Veröffentlichung, sonst **MAJOR** |

**Drei zwingende Prüffragen im Review:**

1. „Was können die Teilnehmenden **ohne den kuratierten Agenten** eigenständig erklären oder entscheiden?“
2. „Wo wurden tatsächlich **Alternativen oder Annahmen** geprüft, statt nur Schritte abgearbeitet?“
3. „Welcher **Kompetenznachweis** geht über ein optisch überzeugendes Artefakt hinaus?“

Ein `PASS` setzt dokumentierte Evidenz voraus; sonst `FAIL` oder `NOT_RUN`. Ein LLM darf keine selbstbehauptete Freigabe erzeugen.

## 9. Pilot- und Reviewempfehlung

**Schlanker Pilot:** eine geeignete zusammenhängende Unterrichtssequenz im Vibe-Coding-Modul oder eine begrenzte Use-Case-Einheit in M02. Nicht sofort einen vollständigen neuen Kursablauf verpflichtend machen.

**Prüfen:** Kann die Gruppe nach geführter Arbeit einen zweiten, kleinen Fall eigenständig strukturieren? Sind alternative Wege erlaubt? Ist das Ergebnis fachlich belastbar? Wie viel tatsächliche Tool- und Unterrichtszeit wird benötigt? Was sagen anspruchsvolle Dozierende zur Durchführbarkeit?

**Vergleich:** Möglichst mit einer konventionell geführten Übung am selben Lernziel vergleichen. Nicht nur Zufriedenheit, Anzahl fertiger Prototypen oder Designqualität erfassen. Ergebnisse und Grenzen dokumentieren, bevor die Methode ausgeweitet wird.

**Offene Punkte – nicht von der Engine selbst entscheiden:** Eigentum/Lizenz und Version von Sebastians Repository, System-Prompt und Nutzungsrechte; tatsächliche Accounts/Konnektoren/Teamrechte; zulässige Credits/Kosten; technische Durchführung im freigegebenen Modul; Verantwortliche für die Pflege der Lernbegleiter-Prompts.

## 10. Minimaler Integrationshinweis (für die späteren Workflow-Konfigurationen)

> **Nur ergänzen, nicht bestehende Dateien überschreiben:** Beim Erzeugen eines `DayBrief` prüft die Engine das Feld `learning_method`. Wenn die Methode `guided_project_journey` ausdrücklich autorisiert ist, wird diese Datei **zusätzlich zu** den fünf bestehenden Normdateien geladen. Dann gelten die `KLP-*`-Checks. Andernfalls wird sie ignoriert; der normale ECOMEX-Produktionsworkflow bleibt vollständig unverändert.

**Änderungsregel:** Jede zukünftige Anpassung dieser optionalen Methode wird separat versioniert. Änderungen an `curriculum.md`, `didaktik.md`, `design.md`, `qa_rules.md` oder `content_workflow.md` erfordern eine eigene begründete Freigabe; sie erfolgen nicht implizit durch Aufnahme dieser Datei.

---

### Changelog

- **0.1.0 – 2026-11-19:** Optionales didaktisches Muster aus dem besprochenen KI-kuratierten Entwicklungsansatz abgeleitet. Bestandsschutz, Lernendenautonomie, Aktivierungsbedingungen, Guardrails und QA-Prüfungen ergänzt. **Noch nicht als ECOMEX-Standard freigegeben.**

## 11. Änderungsprotokoll v0.2.0

- **Quellenlage korrigiert:** Das Repository ist nun als Primärquelle ausgewertet, statt lediglich aus Besprechungsnotizen rekonstruiert.
- **Vorhandene Stärken anerkannt:** Lernmodus, Eigenentscheidungen, MVP-Begrenzung, Sicherheit, Akzeptanzkriterien, Übergabeartefakte.
- **Zusätzliche Risiken präzisiert:** `weiter` als unreflektiertes Übernehmen, fakultative Eigenformulierung, feste Pitch-/Phasenstruktur, fehlender nachgewiesener Abschluss-Transfer.
- **Ergänzt:** `KLP-15` bis `KLP-18`, ohne die ursprünglichen 14 Guardrails oder die fünf ECOMEX-Grundlagendateien zu verändern.
- **Status:** `proposed_for_review_repository_checked`; weder als verbindliche Norm beschlossen noch in n8n/Git/Supabase aktiviert.
