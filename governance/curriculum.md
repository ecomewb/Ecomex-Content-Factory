---
document_id: ecomex.curriculum
title: "ECOMEX | Curriculum und Lernarchitektur"
version: "1.0.0"
status: "working_draft"
last_reviewed: "2026-11-18"
language: "de-DE"
scope: "KI-Coach Professional 2027 / modulare KI-Qualifizierungsfamilie"
owner_role: "ECOMEX Weiterbildungsmanagement / Curriculum-Verantwortung"
change_control: "Menschliche Freigabe bei Änderungen an Wochen, UE, Lernzielen, Pflichtmodulen und Zertifizierung"
depends_on:
  - didaktik.md
  - qa_rules.md
---

# Curriculum: Gesamte Lernreise und Modulverknüpfungen

## 0. Zweck und Leseregeln

Dieses Dokument ist die **programmweite fachlich-didaktische Ausgangsbasis** für Menschen und Content-Engines (einzelne LLMs, spezialisierte Agenten oder automatisierte Pipelines). Es ist **keine fertige Folienvorlage** und kein Prompt für einen bestimmten Anbieter. Aus ihm werden überprüfbare Modul-, Wochen-, Tages- und Folienbriefings abgeleitet.

**Kennzeichnungen:**

- **[PLAN]** = aktueller ECOMEX-Planungsstand, noch keine Aussage über abschließende Zertifizierung.
- **[REGEL]** = vorgeschlagene Produktionsregel für die Content Engine; intern freizugeben, bevor sie verbindlich wird.
- **[REFERENZ]** = vorhandenes Material, das geprüft und gegebenenfalls überarbeitet übernommen werden darf.
- **[OFFEN]** = fachlich/organisatorisch nicht abschließend entschieden; nicht durch das LLM „auflösen“.
- **[PILOT]** = Versuchsmaterial zum Testen einer Content-Produktion, keine Mastervorlage.

Die neun zugelieferten Quelldokumente sind am Ende mit stabilen Kennungen `S01`–`S09` erfasst. Bei Änderungen an dieser Datei müssen die Quellenangaben und Konfliktentscheidungen mitgepflegt werden.

## 1. Gesamtqualifikation

**Arbeitstitel [PLAN]:** KI-Coach Professional – KI anwenden, automatisieren, einführen und vermitteln.  
**Umfang [PLAN]:** 16 Wochen × 41 Unterrichtseinheiten (UE) = **656 UE**, je vierwöchiger Abschnitt 164 UE. Eine UE ist im Zertifizierungskontext nicht automatisch eine Zeitstunde. Finale Dauer, Gruppengröße und Zertifizierungsangaben sind gesondert zu bestätigen. [S01, S03]

**Übergeordnetes Kompetenzziel:** Absolventinnen und Absolventen können KI im Beruf sinnvoll und sicher einsetzen, geeignete Anwendungsfälle begründen, ausgewählte Automatisierungen und Agenten umsetzen, die Einführung von KI-Lösungen planen und andere Menschen bei der Nutzung begleiten. Ein Abschlussprojekt soll diese Fähigkeiten anhand konkreter Arbeitsergebnisse sichtbar machen. [S01–S03]

**Zielgruppe:** Berufserfahrene Erwachsene und qualifizierte Quereinsteigerinnen und -einsteiger mit unterschiedlichen Berufsbiografien, darunter Projekt-, Prozess-, Verwaltungs-, Marketing-, HR-, Beratungs-, Bildungs- und Servicekontexte. Angestrebt wird ein gemeinsames berufliches Kompetenzniveau bei sehr unterschiedlicher KI-Erfahrung.Personen aus nativer IT oder IT-nahen Berufsgruppen sind nicht die primäre Zielgruppe, können vereinzelt aber in Kursen sein. **Keine reguläre Zielsetzung:** Ausbildung zu Software Engineers, Data Scientists oder tief spezialisierten ML-Forschenden. Ausreichende digitale Basiskompetenz ist vorausgesetzt bzw. vorab zu diagnostizieren. [S03, S09]

**Produktlogik:** Der 16-Wochen-Pfad ist ein umfassender Qualifizierungsweg; kürzere, passendere Lernpfade bleiben prinzipiell möglich. Die Inhalte werden als wiederverwendbare Module konzipiert, nicht als starre „16 Wochen für alle“. Ob und welche Zwischenabschlüsse tatsächlich zertifiziert werden, ist offen. [S09]

## 2. Vierstufiger Kompetenzpfad

| Phase | Wochen | Leitfrage | Zielkompetenz / Exit-Outcome |
|---|---:|---|---|
| **USE – Anwenden** | 1–4 | Wie setze ich KI sinnvoll und sicher ein und wie funktionieren die Grundlagen? | KI produktiv nutzen, geeignete Use Cases erkennen und einen digitalen Lösungsweg erläutern. |
| **BUILD – Umsetzen** | 5–8 | Wie baue und prüfe ich reale Arbeitsabläufe und Agenten? | Einen dokumentierten n8n-Workflow/Agenten und einen Copilot-Studio-Agenten für begrenzte Aufgaben entwickeln und testen. |
| **TRANSFORM – Einführen und weiterentwickeln** | 9–12 | Welches Problem lösen wir und wie führen wir die Lösung sinnvoll ein? | Strategie und Nutzerbedarf ermitteln, Prototyp bauen, Lösungsalternativen bewerten und iterative Einführung planen. |
| **ENABLE – Befähigen** | 13–16 | Wie lernen andere Menschen den sinnvollen Einsatz? | Schulung, Einführung, Veränderungsbegleitung und ein integriertes Abschlussprojekt gestalten. |

**Lernlogik [REGEL]:** Von *anwenden* über *selbst umsetzen* zu *beurteilen/einführen* und schließlich *befähigen*. Jede Phase benötigt einen eigenständigen beobachtbaren Kompetenzzuwachs und baut auf verwertbaren Arbeitsergebnissen vorheriger Phasen auf. **Keine isolierte Sammlung von Tools.** [S01, S02]

## 3. Modulmatrix: aktuelle Ideallinie [PLAN]

Die 12 Module ergeben insgesamt 656 UE. Die folgenden konkreten Outcomes operationalisieren die Angaben aus S02/S03; ihr Wortlaut ist ein Redaktionsvorschlag, keine neue Zertifizierungszusage.

| ID | Woche | Modul | UE | Kerninhalte | Nachweisbares Ergebnis |
|---|---|---|---:|---|---|
| M01 | 1–2 | KI im Berufsalltag professionell nutzen | 82 | GenAI, ChatGPT/Claude/Gemini/Copilot, Prompting, Recherche, Dokumente, Präsentationen, Medien, Daten, Quellen- und Ergebnisprüfung | Wiederverwendbarer, überprüfter KI-Arbeitsablauf plus Abschlussdemo |
| M02 | 3 | Power Using und KI-Anwendungsfälle | 41 | wiederverwendbare KI-Arbeit, Prozesssicht, Use-Case-Auswahl, Nutzen/Machbarkeit, beruflicher Transfer | Use-Case-Steckbrief mit Problem, Nutzern, Prozess, Nutzen, Risiken, Erfolgskriterium |
| M03 | 4 | Digitale Abläufe und KI-Lösungen verstehen | 41 | Datenwege, Markdown/CSV/JSON, API, Webhook, Workflow, Agent, MCP, Rechte, Kontrolle und KI-Recht im Überblick | verständliches Lösungsbild und Daten-/Kontrollfluss, begründete Einschätzung |
| M04 | 5–6 | KI-Automatisierung mit n8n | 82 | Trigger, Nodes, Integrationen, Datenübergaben, APIs, KI, Tests, Debugging, RAG, Multi-Agenten-Systeme| dokumentierter und getesteter End-to-End-Workflow |
| M05 | 7–8 | KI-Agenten mit Microsoft Copilot Studio | 82 | Agenten, Wissensquellen, Aktionen, M365/SharePoint, Connectoren, Berechtigungen, Test | funktionsfähiger, abgegrenzter Agent mit Testfällen und Betriebsgrenzen |
| M06 | 9 | Design Thinking mit KI | 41 | Nutzerbedarf, Problemdefinition, Ideen, Persona/Nutzerreise, Prototyp, Feedback | validierter Problemrahmen und priorisierte Lösungshypothese |
| M07 | 10 | Vibe Coding / KI-gestütztes Prototyping | 41 | Anforderungen, UI, KI-gestützte Entwicklung, Tests, iterative Verbesserung | demonstrierbarer Prototyp samt Akzeptanzkriterien |
| M08 | 11 | KI-Strategie und Einführung | 41 | Reifegrad, Lösungswahl, Wirtschaftlichkeit, Priorisierung, Governance, KI-Verordnung, Rollout | begründeter Einführungsplan mit Risiken, Verantwortlichkeiten und Erfolgsmessung |
| M09 | 12 | Agile Methoden in KI-Projekten | 41 | Scrum, Kanban, Lean Startup, MVP, Aufgabenplanung, Reviews, Iteration | nachvollziehbarer iterativer Projekt-/Umsetzungsplan |
| M10 | 13 | KI-Kompetenzaufbau und Einführung im Team | 41 | Zielgruppen- und Lernbedarf, Lernformate, Begleitung, Akzeptanz, Wissenstransfer | Schulungs-/Enablement-Konzept mit Transferprüfung |
| M11 | 16 | Abschlussprojekt und Berufstransfer | 41 | Lösung/Prototyp, Strategie, verantwortlicher Betrieb, Dokumentation, Vermittlung, Präsentation | integriertes Praxisportfolio und nachvollziehbare Abschlusspräsentation |
| M12 | 14–15 | Coaching-Grundlagen für KI-Kontexte | 82 | Coaching vs. Beratung/Training, Gesprächsführung, Feedback, Zielklärung, Veränderung | erprobter Gesprächs-/Begleitprozess mit Reflexion |

**Grenzen:** Modulnamen, Wochen und UE sind gegenüber Änderungen gesperrte **Curriculum-Felder**. Ein Content-Agent darf diese nicht selbst verändern; er kann Änderungsanträge erzeugen. Toolbeispiele und einzelne Fallthemen sind dagegen redaktionell austauschbar. [S01–S03]

## 4. Ausgearbeitete USE-Lernreise: Tage 1–20

S04 ist für den **Tageszuschnitt von USE** präziser als die älteren Präsentationen oder das allgemeinere Stammdatenblatt. Die konkrete Zuordnung von Tagen 17/18 in S08 ist ein **Automatisierungsversuch** und wird nicht als Freigabe neuer Pflichtinhalte interpretiert.

| Tag | Tagesfokus | Zentrale Lernhandlungen / Ergebnis | Scope-Grenze |
|---|---|---|---|
| 01 | Generative KI und Werkzeugwahl | gleiche Aufgabe mit 2–3 Werkzeugen vergleichen; Daten- und Quellenrisiken einordnen | kein technischer Architekturkurs |
| 02 | Prompting | Ziel/Kontext/Format klären und einen Prompt iterativ verbessern | kein „Superprompt“-Selbstzweck |
| 03 | Projects, wiederverwendbare Assistenten und Skills | eng abgegrenzten Assistenten konfigurieren, testen, verbessern | keine komplexe Agentenarchitektur |
| 04 | Recherche und Quellen | Informationen recherchieren, Urheber/Datum/Quellen prüfen | nicht allein auf KI-Zitate verlassen |
| 05 | Dokumente und Kommunikation | Dokumentauswertung, adressatengerechte E-Mail, Meeting-Ergebnis | faktische Verlässlichkeit/Vertraulichkeit prüfen |
| 06 | Präsentation und Storyline | aus Material 3–5 aussagekräftige Folien erstellen und verbessern | keine bloße Tool-Galerie |
| 07 | Bild, Design, Mock-ups | Kommunikations-Asset erstellen und iterieren | Lizenz/Rechte nicht auslassen |
| 08 | Audio, Video, multimodale KI | Inhalt in ein zweites Medium übertragen; Grenzen vergleichen | ein Medium vertiefen, andere exemplarisch |
| 09 | Power-User-Werkstatt | zwei oder mehr etablierte KI-Arbeitsweisen verbinden | **keine neuen großen technischen Begriffe** |
| 10 | Abschluss Grundlagenmodul | Praxisdemo, Lernreflexion, persönlicher Transfer | Modulabschluss ohne JSON-/API-Pflicht |
| 11 | Gemeinsamer Einstieg / Use Cases | Problem, Nutzende, Ziel und Passung eines Falls festhalten | kein Wiederholen der ganzen Anfängerwoche |
| 12 | Power Using / wiederverwendbare Arbeitsweisen | komplexere Aufgabe zerlegen, Assistenzablauf testen | nicht einfach Tag 03 kopieren |
| 13 | Use Case → Arbeitsprozess | IST-/SOLL-Prozess, Engpass und Kontrollpunkt visualisieren | keine Unternehmensprozessarchitektur |
| 14 | Nutzen, Machbarkeit und Toolwahl | einzelnen Use Case mithilfe einfacher Kriterien bewerten | **kein ROI/TCO, Make-or-Buy oder Portfolio** |
| 15 | Bewerbung und Berufstransfer | KI-Kompetenzen für Stellensuche, Unterlagen, Interview nutzen | Wochenabschluss |
| 16 | Vom Use Case zum Lösungsbild | Nutzer, Input, System/KI, Output, Mensch unterscheiden | **kein Coding** |
| 17 | Daten, Formate und Schnittstellen verstehen | kleinen Datensatz prüfen/visualisieren; Markdown, CSV, einfaches JSON sowie typische API-Anfrage/-Antwort nachvollziehen | kein JSON-Schema-/HTTP-Programmierkurs |
| 18 | Automatisierung und Agenten verstehen | Trigger, Schritte, Datenübergabe, Agentenentscheidungen, MCP und Freigaben erklären | kein produktiver n8n-/Copilot-Build |
| 19 | Lösung bewerten und strategisch einordnen | Nutzen, Aufwand, Datenlage, Risiken, Kontrollen begründen | KI-OS nur als Orientierungsbild; keine Strategieroadmap |
| 20 | KI-Recht „Lite“ und USE-Abschluss | typische Situationen prüfen, menschliche Kontrolle und Klärbedarf benennen | keine Rechtsberatung/Governance-Vollausbildung |

**Hinweis zu Tag 17/18:** Die Datei `Ecomex_Tage_17_18_Daten_APIs_MCP V3.2.pptx` setzt in einem Testpfad Formate/Markdown/JSON auf Tag 17 und API/Workflow/Agent/MCP auf Tag 18. Sie liefert nützliche Ansätze für einen durchgehenden, **fiktiven** Lieferanfrage-/Supportfall, für die Trennung von Falldaten und FAQ-Wissen sowie für kurze Verständnischecks. Das ist **Testmaterial zur Bewertung einer Automatisierung**, **kein** verbindliches Folienlayout, keine freigegebene Agenda und keine verbindliche Verteilung aller Inhalte. Weicht es von S04 ab, geht die Unterrichtsplanung erst nach menschlicher Entscheidung in die Produktion. [S04, S08]

## 5. Übergaben zwischen Modulen: die inhaltliche Kette

Ein **Transferartefakt** ist ein wiederverwendbares Arbeitsergebnis, nicht bloß eine Schlussfolie. Beispiele können beruflich-individuell sein; ein fiktives Unternehmen ist eine Option, **keine Pflicht**.

| Übergabe | Eingang aus Vorgängermodul | Was wird im Folgemodul neu gelernt? | Artefakt-Weiterentwicklung |
|---|---|---|---|
| M01 → M02 | geprüfte KI-Arbeitsweise | vom Werkzeug zum tatsächlichen Problem und Nutzen | Anwendungsfall-Steckbrief |
| M02 → M03 | Use Case mit Prozess und Erfolgskriterium | Datenfluss, Integration und Kontrollpunkte verstehen | konzeptionelles Lösungsbild |
| M03 → M04 | beschrifteter Daten-/Ablaufplan | technische Schritte in n8n **selbst** implementieren | laufender Workflow + Tests |
| M04 → M05 | Erfahrung mit Triggern, Daten und Freigaben | Wissensquellen, Aktionen und Agenten in einer zweiten Plattform | Copilot-Studio-Agent mit Prüffällen |
| M05 → M06 | vorhandene technische Möglichkeiten | Nutzerbedarf **kritisch hinterfragen**, Probleme neu framen | Problemdefinition/Feedbackprotokoll |
| M06 → M07 | geprüfte Lösungshypothese | interaktiven Prototyp realisieren und testen | getestete UI/App |
| M07 → M08 | Prototyp samt Befunden | Unternehmensnutzen, Governance, Wirtschaftlichkeit, Einführung | strategischer Umsetzungsplan |
| M08 → M09 | strategische Entscheidung | in priorisierte, testbare Iterationen und Teamarbeit übersetzen | Backlog, MVP, Review-Plan |
| M09 → M10 | Einführungs- und Iterationsplan | Menschen zielgruppengerecht schulen und begleiten | Schulungs-/Adoption-Konzept |
| M10 → M11 | Lern- und Veränderungsbedarf | Gesprächsführung, Coachingauftrag, Grenzen professionell üben | Fallreflexion / Gesprächsprotokoll |
| M11 → M12 | technische, fachliche und kommunikative Teilprodukte | integrieren, begründen, demonstrieren und beruflich vermitteln | Abschlussportfolio |

**[REGEL] Kein Redundanz-Fehlschluss:** Ein wiederkehrender Begriff ist erlaubt, **wenn** die zweite Begegnung ein neues Kompetenzniveau verlangt. Beispiel: `JSON lesen` (USE) → `JSON auf Nodes abbilden` (BUILD) → `Datenverfügbarkeit beurteilen` (TRANSFORM). Dagegen ist eine zweite Grundlagenvorlesung ohne höhere Handlungstiefe ein Qualitätsfehler.

## 6. Kompetenz-Niveaus und Tiefengrenzen

| Inhalt | USE: erkennen/erklären | BUILD: anwenden/umsetzen | TRANSFORM: bewerten/einführen | ENABLE: vermitteln/begleiten |
|---|---|---|---|---|
| KI-Werkzeuge | vergleichen, produktiv nutzen, prüfen | in Lösungen einbinden | Auswahlkriterien/Organisation | sichere Anwendung erklären |
| Daten und JSON | Felder, Werte, Herkunft, Plausibilität | Mapping, Transformation, Debugging | Datenqualität, Zugriff, Betrieb | typische Datenrisiken vermitteln |
| API / MCP | Zweck, typischer Ablauf und Berechtigungen | funktionierende Verbindung unter Kontrollen | Eignung und Integrationsrisiko | Grenzen gegenüber Teams erklären |
| Workflows / Agenten | abgrenzen, Ablauf skizzieren, Grenzen nennen | erstellen, testen, Fehler untersuchen | Autonomie, Betrieb, Verantwortlichkeiten wählen | geeignete Nutzung anleiten |
| Recht / Governance | Risikosignale und Klärbedarf erkennen | Sicherheit und Berechtigung umsetzen | Verantwortlichkeiten und Regelwerk planen | Regeln verständlich vermitteln, Fälle eskalieren |
| Geschäftsprobleme | einen Einzelfall begründen | konkrete Lösung liefern | mehrere Fälle priorisieren/ausrollen | Akzeptanz und Lerntransfer sichern |

## 7. Verbindlicher Mindestumfang jedes Modulbriefs [REGEL]

Eine Content Engine darf kein Tagesdeck aus einer isolierten Überschrift oder einem Kapitelstichwort herstellen. Mindestens erforderlich:

```yaml
module_brief:
  module_id: "M03"
  phase: "USE"
  curriculum_version: "1.0.0"
  duration_ue: 41
  audience: "heterogene berufserfahrene Erwachsene"
  prerequisites: ["M02-Kompetenzen oder dokumentiertes Äquivalent"]
  outcomes:
    - id: "M03-O1"
      action: "einen einfachen Datenfluss erläutern"
      evidence: "annotiertes Lösungsbild"
  in_scope: ["CSV/Markdown/JSON", "API-Grundverständnis", "Workflow/Agent/MCP"]
  out_of_scope: ["produktionsreife Agenten bauen", "komplexe Softwareentwicklung"]
  transfer_from: ["Use-Case-Steckbrief"]
  transfer_to: ["Daten- und Lösungsbild für BUILD"]
  reference_sources: ["S01", "S02", "S03", "S04"]
  decisions_required: []
```

**Tagesbriefs** ergänzen die **tatsächlich** geplanten Zeiten inklusive Pausen, Lernvoraussetzungen, konkrete Lernnachweise, Fall/Referenzdaten, verfügbare Werkzeuge, Alternativpfad ohne Toolzugriff, fachliche Quellen und Verantwortliche. Produktionsschnittstelle und Review-Schritte stehen in `content_workflow.md`.

## 8. Quellenregister und Konfliktbehandlung

| ID | Quelle | Funktion in der Architektur | Autorität im hier beschriebenen Anwendungsfall |
|---|---|---|---|
| S01 | `Ecomex_UBTE_Kursarchitektur_OnePager(1).pdf` | 2027-Makrostruktur, Ziele, 656 UE | aktuelle **Planungsbasis**, nicht finaler Bescheid |
| S02 | `Ecomex_UBTE_Einzelmodule_Themen_Uebersicht(1).pdf` | 12 Module, Woche/Schwerpunkt | aktuelle **Modulübersicht**, vorläufig |
| S03 | `16_Stammdatenblatt_KI-Coach_Professional_3.1.docx` | UE, Zielgruppe, Modulziele, Zertifizierungsentwurf | detaillierter formeller **Entwurf**, noch nicht freigegeben |
| S04 | `Ecomex Lehrplan Woche 1-4.docx` | konkrete Tage 1–20, Lernlogik, Feedback-Konsequenzen | präferierte **USE-Feinplanung** |
| S05 | `Präsentation - ChatGPT und Co. FW 10.11.26.pptx` | bestehende Übungen/Folien und Produktivitätsinhalte | **Bestandsreferenz**, nicht neue Kursarchitektur |
| S06 | `Präsentation - KI-Agenten mit n8n FR 05.11.26.pptx` | didaktische Fachpraxis und realer Werkzeugbezug | **Bestandsreferenz**, nicht 2-Wochen-Freigabe |
| S07 | `KI Strategie Implementierung V5.1.pptx` | Strategie, Wirtschaftlichkeit, Governance, Recht | **Bestandsreferenz**, fachlich einzeln prüfen |
| S08 | `Ecomex_Tage_17_18_Daten_APIs_MCP V3.2.pptx` | erster technischer **Content-Engine-Pilot** | **PILOT – ausdrücklich keine Mastervorlage** |
| S09 | `Ecomex_KI_Coach_2027_Master_Strategy_Claude_Audit(1).docx` | historischer Strategie-/Wirtschaftlichkeitsrahmen, Flagship-Logik | **Kontext**, bei Änderungen nicht vorrangig |

**Dokumentierte [OFFEN]-Punkte (nicht stillschweigend entscheiden):**

1. **Woche-2-Datenumfang:** S03 nennt Markdown/CSV/JSON bereits im zweiten Wochenmodul, S04 verortet die vertiefte strukturierte Daten-/API-Einführung ausdrücklich in Woche 4 und schließt JSON an Tag 10 aus. Für **Deckproduktion** gilt bis zur Entscheidung die Tageslogik von S04; die abweichende Zertifizierungsformulierung muss vor Einreichung abgestimmt werden.
2. **Ältere Modulmatrix:** S09 beschreibt an einer Stelle noch zwei Wochen Vibe Coding und zwei Wochen Strategie; S01/S02/S03 definieren aktuell jeweils **eine** Woche. Kein Agent darf aus S09 zusätzliche Wochen ableiten.
3. **Zeiten/UE:** 656 UE ist als Planungswert dokumentiert. Reale Unterrichts-/Pausenpläne, Selbstlernphasen und Zertifizierungsberechnung getrennt prüfen.
4. **Folienmaster/Branding:** Die PDFs nutzen Lato, vorhandene PowerPoints überwiegend Open Sans; ein rechtsverbindliches Corporate-Design-Handbuch oder freigegebener `.potx`-Master liegt in dieser Quellenmenge nicht vor. Siehe `design.md`.
5. **Rechtliche Zeitabhängigkeit:** KI-Verordnung, Datenschutz und Lizenzbedingungen niemals nur aus älteren Folien übernehmen; vor Veröffentlichung durch zuständige Fachperson und aktuelle Primärquellen prüfen.

## 9. Änderungsprotokoll

| Version | Datum | Änderung | Status |
|---|---|---|---|
| 1.0.0 | 2026-11-18 | Erstfassung der modularen Lernarchitektur aus S01–S09, einschließlich Pilot-Abgrenzung und Konfliktliste | Arbeitsentwurf |

**Änderungsregel:** Jedes neue Modul, verschobene Woche oder veränderte Kompetenzziel erhält einen nachvollziehbaren Änderungsantrag mit Auswirkung auf UE, Zertifizierung, Modulabhängigkeiten, Lehrmaterialien, QA und Produktion. Erst nach menschlicher Freigabe `version` ändern.
