---
document_id: ecomex.didaktik
title: "ECOMEX | Fachliche und didaktische Qualitätsstandards"
version: "1.1.0"
status: "working_draft"
last_reviewed: "2026-11-18"
language: "de-DE"
applies_to: ["Modulplanung", "Tagesplanung", "SlideSpecs", "Übungen", "Workbooks", "Lehrhinweise"]
depends_on: ["curriculum.md", "qa_rules.md"]
---

# Didaktik: Fachliche Substanz und wirksame Erwachsenenbildung

## 1. Qualitätsversprechen

ECOMEX-Kurse sollen fachlich belastbare, unmittelbar nutzbare berufliche Kompetenzen aufbauen, **ohne sie künstlich zu trivialisieren und ohne Menschen mit Theorie, technischen Details oder schnell wechselnden Tools zu überladen**. Der Regelfall ist **praktische Arbeit mit KI-Werkzeugen**: recherchieren, Texte und Dokumente bearbeiten, Präsentationen und Medien gestalten, Lösungen planen, geeignete Tools einsetzen, testen, verbessern und Ergebnisse beurteilen. Nur einzelne Module benötigen einen stärkeren Daten-, Schnittstellen- oder Automatisierungsschwerpunkt. Die Teilnehmenden sollen Zusammenhänge verstehen, sinnvolle Entscheidungen treffen, realistische Aufgaben ausführen und ihre Ergebnisse kritisch prüfen können.

**[REGEL – Schwerpunktsteuerung]** Die Content Engine darf aus gut dokumentierten Daten-/API-Piloten **keinen allgemeinen Kursstil** ableiten. Sie wählt den Inhalt und das Beispiel **vom Lernziel und Modul aus**, nicht von vorhandenen technischen Referenzdecks aus. Fachliche Tiefe bedeutet in nichttechnischen Modulen vor allem durchdachte Anwendung, Qualitätsbewertung, methodische Begründung, Grenzen und reflektierte Verbesserung – **nicht** zusätzliche JSON-, Code-, Architektur- oder Datenmodellfolien. In technischen Modulen bleiben korrekte Mechanismen und dort notwendige Datenbeispiele selbstverständlich verpflichtend.

**Gleichzeitig wahr:**

1. **Fachliche Tiefe:** präzise Begriffe, methodisch und sachlich richtige Zusammenhänge, bei Bedarf korrekte technische Mechanismen, Grenzen, Gegenbeispiele und professionelle Bewertungskriterien.
2. **Zugänglichkeit:** klare Sprache, gut gewählte Analogien, nachvollziehbare konkrete Beispiele und schrittweise Lernunterstützung.
3. **Eigenaktivität:** sinnvolle Übungszeit, begründete Entscheidungen, sichtbare Ergebnisse und überprüfbare Lernfortschritte.
4. **Heterogenität:** dieselben verbindlichen Kernziele, geführte Basispfade und optionale anspruchsvolle Erweiterungen.
5. **Transfer:** konkrete Arbeitsprodukte, berufliche Probleme und übertragbare Lernkompetenzen bilden den roten Faden; Tools sind praktisches Arbeitsmittel, nicht Selbstzweck.
6. **Menschliche Verantwortung:** Quellenprüfung, Datenschutz, Berechtigungen, Qualitätskontrolle und Fach-/Freigabeentscheidungen bleiben sichtbar.

Die Grundrichtung folgt den didaktischen Konsequenzen in S04 und den Qualitätsproblemen/Erkenntnissen aus S05–S08. Einzelne hier präzisierte Kriterien sind **redaktionelle Projektstandards**, keine Behauptung, sie seien bereits von ECOMEX zertifiziert.

## 2. Zielgruppen- und Niveaumodell

**Zielgruppe:** Erwachsene mit beruflicher Erfahrung, oft aus unterschiedlichen Funktionen. Ihre Kenntnisse in KI, Daten, IT, Projektarbeit und Unternehmensstrategie unterscheiden sich erheblich. **Ziel** ist weder ein „Einsteigerkurs für alle“ noch ein Programmier-Bootcamp, sondern eine belastbare gemeinsame Kernkompetenz mit fachlich angemessener Vertiefung. [S03, S04]

**Vor jedem Modul:**

- Vorwissen mit 3–5 kurzen Aufgaben/Fragen erkennen (nicht allein Selbstbewertung).
- Unverzichtbare Voraussetzungen und unmittelbar nötige Toolzugänge prüfen.
- Fachbegriffe vorab auf tatsächlich benötigte Mindestbegriffe begrenzen.
- Basispfad so gestalten, dass er ohne tiefes technisches Vorwissen erreichbar ist.
- Einen **optionalen Plus-Pfad** für schnellere Teilnehmende anbieten, der denselben Fall vertieft und keine unabhängige zweite Unterrichtsklasse erzeugt.
- Verständnishürden und Unterstützungsbedarf als Planungsinformation behandeln, nicht als Defizit der Lernenden.

**Drei Schwierigkeitsstufen als Metadaten – Beispiel aus der alltäglichen Tool-Praxis:**

| Stufe | Zweck | Beispiel: Ein KI-Tool soll aus Besprechungsnotizen einen verwertbaren Ergebnisbericht erstellen |
|---|---|---|
| **KERN** | Alle erreichen das prüfbare Kompetenzziel | Aus fiktiven Stichpunkten mit einem KI-Tool eine gegliederte Zusammenfassung erstellen und Aussagen am Original prüfen |
| **PLUS** | Gleiches Lernziel mit anspruchsvollerem Fall | Zielgruppenabhängige Versionen erstellen, Unterschiede vergleichen und unklare Verantwortlichkeiten kenntlich machen |
| **EXPERT-OPTIONAL** | Transfer/Qualitätsanalyse für Fortgeschrittene | Einen wiederverwendbaren Arbeitsablauf mit Prüfkriterien entwickeln und ihn an einem zweiten Notizsatz testen |

**Modulspezifische Abwandlung:** In Präsentationsmodulen wird eine reale Folie verbessert; in Design Thinking ein Interview ausgewertet; in Copilot Studio eine Agentenantwort getestet; in n8n ein Workflow geprüft; **nur im passenden Datenmodul** beispielsweise ein JSON-Feld gelesen. Die Niveaustufen bilden **Kompetenztiefe innerhalb des jeweiligen Fachthemas**, keine automatische technische Eskalation.

Eine PLUS-Aufgabe darf **nicht heimlich zum Pflichtwissen** für das gesamte Team werden. Die Lernplanung reserviert trotzdem gemeinsame Reflexion.

## 3. Anspruchsvolle Inhalte verständlich machen

**[REGEL] Nicht weniger Substanz, sondern bessere Sequenz.**

Bevor ein **neues Konzept, eine Methode oder eine Tool-Funktion** eingeführt wird, definiert die Redaktion:

1. **Warum ist sie relevant?** Konkrete Arbeitsaufgabe, ein Problem oder beobachtbarer Engpass.
2. **Was muss ich verstehen?** Korrekte Funktionsweise bzw. Methode, notwendige Voraussetzungen und Grenzen – **nur in der für das Lernziel erforderlichen Tiefe**.
3. **Was ist sichtbar?** Ein tatsächlich ausgearbeitetes Arbeitsergebnis, ein realistisch demonstrierter Tool-Schritt, ein Interface, Test oder Vergleich.
4. **Wie probiere ich es aus?** Überschaubare Aufgabe mit überprüfbarem Output.
5. **Woran erkenne ich eine gute Anwendung?** Kriterium, Musterlösung und typischer Fehler.
6. **Wann eignet sich der Ansatz nicht?** Gegenbeispiel, Qualitätsrisiko oder Trade-off.
7. **Wo brauche ich es später?** Anschluss zum nächsten Modul bzw. beruflichen Einsatz.

**Primärbeispiel – produktive KI-Nutzung statt Technikvorlesung:**

- *Praxisfrage:* „Wie wird aus einer unübersichtlichen, fiktiven Besprechungsmitschrift eine verständliche Entscheidungsvorlage?“
- *Demonstration:* Eine vorbereitete Mitschrift wird in ChatGPT oder einem anderen freigegebenen Tool mit einem klaren Arbeitsauftrag verarbeitet; der **tatsächlich erzeugte Erstentwurf** wird gezeigt, nicht nur ein Prompt.
- *Kriterien:* Entscheidungen und offene Punkte bleiben getrennt; Verantwortlichkeiten werden **nicht erfunden**; unklare Informationen werden als offen markiert.
- *Angeleitete Übung:* Die Lernenden verbessern die Ausgabe anhand des Originals und erstellen eine nutzbare Endfassung.
- *Grenze:* Das Modell kann Formulierungen ergänzen oder Sicherheit suggerieren; die Originalnotizen und eine fachliche Endprüfung bleiben maßgeblich.
- *Plus:* Einen zweiten Adressatenkreis bedienen und nachvollziehbar begründen, welche Informationen entfallen oder hinzugefügt wurden.

**Spezialbeispiel – API-Erklärung ausschließlich bei passendem technischem Lernziel:**

- *Praxisfrage:* „Wie bekommt der Antwort-Assistent den aktuellen Status einer Bestellung, wenn die E-Mail diesen nicht enthält?“
- *Mechanik:* Ein Programm sendet eine nach Schnittstellenvertrag zulässige Anfrage an einen Endpunkt; das Zielsystem prüft je nach Dienst den Zugang und liefert Antwortdaten bzw. einen Fehler.
- *Konkretes Beispiel:* `GET /tickets/T-8124` → `{"ticket_id":"T-8124","status":"offen"}`.
- *Prüfpunkt:* `status: "offen"` beschreibt den Ticketstatus, **nicht** den Liefertermin.
- *Grenze:* Eine API kann unterschiedlich authentifiziert sein, gibt nicht immer JSON zurück und garantiert nicht die Richtigkeit aller gelieferten Informationen.
- *Plus:* Lesen vs. Schreiben / minimale Rechte / Fehlerantwort und Berechtigungsproblem unterscheiden.

Das API-Beispiel ist fachlich wichtig, **aber nicht repräsentativ für den gesamten Kurs**. Die technische Tiefe wird im vorgesehenen Modul aufgebaut; in nichttechnischen Tagen darf die Engine daraus keine zusätzliche Unterrichtseinheit generieren.

## 4. Standard-Lernsequenz für neue Konzepte

**Default**, nicht starres sechs-Folien-Format:

`Problem/Kontext → ausgearbeitetes Beispiel → präziser Begriff/Mechanik → angeleitete Anwendung → Besprechung/Lösung → Transfer und Grenze`

Varianten sind zulässig, solange alle sechs Funktionen im Lernarrangement erkennbar sind. Komplexere Themen nutzen eine kürzere *Demonstration → gemeinsames Nachbauen → eigenständige Variation → Feedback*-Schleife. [S04]

**Lehr- und Lernrhythmus:**

- Jede längere Lehrstrecke erhält eine echte Frage, Entscheidung, Sortieraufgabe, Demonstration oder Übungsphase.
- Neue Begriffe und Tool-Funktionen werden direkt mit einer Handlung und einem sichtbaren, fachlich passenden Arbeitsprodukt verknüpft.
- Ein gutes Beispiel wird vollständig **durchgearbeitet**, bevor die nächste Abstraktion kommt.
- Geführte Hilfen werden beim Übergang zur selbständigen Aufgabe schrittweise reduziert.
- Kurze Abruf- und Transferfragen prüfen Verständnis, nicht bloß Wiedererkennen einer Folie.
- Es ist legitim, weniger Themen fundiert zu behandeln als viele nur anzureißen.

**Wirkungslose „Interaktion“ vermeiden:** Bloßes „Was denkt ihr?“ ohne konkretes Arbeitsmaterial, Entscheidungsfrage oder Rückmeldung ist kein Ersatz für eine Übung.

## 5. Lernziele und konstruktive Ausrichtung

Jede Tageseinheit besitzt **3–5 zentrale, beobachtbare Lernziele** (Richtwert; abhängig von Dauer). Ein Lernziel beschreibt:

`Handlung + Gegenstand + Kontext/Anforderung + überprüfbares Ergebnis`

**Geeignet (Regelfall – Tool-Anwendung):** „Die Teilnehmenden können aus bereitgestellten fiktiven Besprechungsnotizen mithilfe eines freigegebenen KI-Tools einen strukturierten Ergebnisbericht erstellen, drei Aussagen am Original gegenprüfen und die Endfassung anhand einer Checkliste überarbeiten.“

**Nicht geeignet:** „Die Teilnehmenden kennen die Möglichkeiten von ChatGPT und können damit produktiver arbeiten.“

**Geeignet (spezifisches Technikmodul):** „Die Teilnehmenden können in einer bereitgestellten einfachen JSON-Antwort die für einen Supportfall entscheidenden Angaben erkennen und fehlende Informationen benennen.“

Verben und erwartete Tiefe an die Phase anpassen:

- **USE:** erläutern, identifizieren, unterscheiden, anwenden, prüfen, skizzieren.
- **BUILD:** konfigurieren, verbinden, umsetzen, testen, debuggen, dokumentieren.
- **TRANSFORM:** untersuchen, priorisieren, begründen, prototypisieren, abwägen, planen.
- **ENABLE:** erklären, anleiten, moderieren, beraten (mit Rollengrenzen), begleiten, evaluieren.

**Traceability-Regel:** Jedes Kernlernziel wird mindestens einem konkreten Übungs-/Prüfergebnis zugeordnet; jede Pflichtübung muss ein Lernziel stützen. Kein Pflichtinhalt ohne erkennbaren Lernwert.

## 6. Lehrmaterial braucht ausgearbeitete Substanz

Eine Folie, ein Beispiel oder eine Übung ist **inhaltlich unvollständig**, wenn sie lediglich erklärt, was man „zeigen könnte“. Bei produktionsreifen Materialien gilt:

- Fachbehauptung und fachlich passendes Gegenbeispiel, wo nützlich.
- **Tatsächlich ausgearbeitete Arbeitsinputs und -outputs**: z. B. fiktives Briefing plus fertiger KI-Text, Ausgangsfolie plus verbesserte Folie, Recherchefrage plus überprüfte Quellen, Workflow plus Testlauf oder – wenn fachlich nötig – Beispieldaten. Keine leeren Platzhalter.
- Tatsächlich erstellte Visualisierung, bearbeitbare Beispielfolie, angeleitete Tool-Demonstration oder konkretes Ergebnis statt „Diagramm/Screenshot hier einfügen“.
- Nachvollziehbare Rechenschritte bei Nutzen-/Kostenbeispielen.
- Sichtbare Kriterien für richtige Entscheidung bzw. Interpretation.
- Lösungsfolie, Lösungsschlüssel oder Dozentenlösung für jede Pflichtübung.
- Innerhalb eines Praxisfalls konsistente Ziele, Ausgangsmaterialien, Aussagen, Rollen, Dateinamen und – soweit vorhanden – Zahlen/Felder.
- Provenienz: Was stammt aus der Quelle, was hat ein System gesetzt, was ist geschätzt/noch unbekannt?

**Beispiele dürfen fiktiv sein**, müssen aber ausdrücklich als solche gekennzeichnet werden. Ein fiktiver API-Endpunkt darf **nicht** als aufrufbare echte API ausgegeben werden.

## 7. Übungsarchitektur: vom sicheren Einstieg zum Transfer

Jede Übung bekommt **passendes Ausgangsmaterial** (Text, Dokument, Bild, Arbeitsbrief, Tool-Projekt, Testfall oder nur bei Bedarf Datensatz) und mindestens:

```yaml
exercise:
  id: "M01-D05-E02"
  linked_objectives: ["M01-D05-O2"]
  work_mode: "Einzelarbeit mit anschließendem Partnercheck"
  duration_minutes: 30
  input_material: "materials/fiktive_meetingnotizen.md"
  tool_or_method: "freigegebenes KI-Textwerkzeug; alternativ vorbereitete Ausgabe"
  task: "Erstelle eine Zusammenfassung mit Entscheidungen, Aufgaben und offenen Fragen; prüfe sie am Ausgangstext."
  base_path: "Pflichtaufgabe: Ergebnisbericht erstellen und mindestens drei Aussagen prüfen."
  extension_optional: "Bericht für eine zweite Zielgruppe umarbeiten und Änderungen begründen."
  expected_output: "korrigierter Ergebnisbericht mit markierten offenen Punkten"
  sample_solution_ref: "solutions/M01-D05-E02.md"
  hints: ["Prüfe jede behauptete Entscheidung am Originaltext."]
  misconceptions: ["Von der KI ergänzte Verantwortlichkeiten als belegt übernehmen."]
  fallback: "vorbereiteter KI-Erstentwurf plus Arbeitsblatt für Offline-Überarbeitung"
  debrief: "Zwei Belege und eine unzulässige Ergänzung gemeinsam diskutieren."
```

**Zeitregel:** `duration_minutes` bezeichnet den **sichtbaren Übungsblock im Tagesstundenplan** und ist nur `15`, `30`, `45` oder `60`. Eine kurze Reflexion oder Demonstration darf **innerhalb** eines solchen Blocks kleinschrittig getaktet werden; diese Unterteilung erzeugt keine krummen eigenständigen Stundenplan-Einträge.

**Vor der Übung:** Zeit, Sozialform, Auftrag, Material, Output und Pflicht-/Plus-Aufgabe sichtbar machen.  
**Während der Übung:** Unterstützungsanker, testbare Zwischenziele, klare Hilfe bei Zugangsproblemen.  
**Nach der Übung:** Lösung anhand der Kriterien prüfen, Fehlannahmen adressieren und eine Transferfrage stellen.

**Musterlösungen** sind *didaktisch korrekt*, nicht nur formal richtig: Sie erklären mindestens die entscheidende Begründung und typische alternative zulässige Antworten.

## 8. Unterrichtsdramaturgie, **verbindliche Zeiten** und Agenda

**[VERBINDLICHE ECOMEX-RAHMENBEDINGUNG – nicht aus Pilotdecks abgeleitet]** Die Unterrichtszeit ist **Montag bis Donnerstag immer 09:00–15:00 Uhr**, **Freitag immer 09:00–13:00 Uhr**. **Keine Verlängerung** für Übungen, Nachbesprechungen, technische Probleme oder einen verspäteten Kursbeginn. Bei Zeitdruck werden optionale Vertiefungen oder Inhalte innerhalb der bestehenden Zeit reduziert bzw. planvoll umverteilt; Kernziele dürfen nicht stillschweigend entfallen.

**Pausen und Agenda:** Die Kaffeepause liegt üblicherweise bei **10:30–10:45 Uhr (15 Minuten)**; die Mittagspause dauert **45 Minuten** und liegt üblicherweise gegen **12:00 oder 12:30 Uhr**. Die exakten Pausenpositionen können je Tag variieren; **in jeder ausgegebenen Agenda sind die tatsächlichen Uhrzeiten vorab explizit und fest ausgewiesen**. Änderungen der Tagesagenda erfordern Anpassung aller betroffenen Folien, Anleitungen und Zeitprüfungen. **Für Freitag keine Mittagspause automatisch annehmen**: Sie wird nur eingeplant, wenn sie in der konkreten Freitagsagenda vorgesehen ist; der Schlusspunkt 13:00 bleibt ausnahmslos bestehen.

**[VERBINDLICHE TAKTUNG]** Themen-, Unterrichts- und Übungsblöcke im **Stundenplan** erhalten ausschließlich **15, 30, 45 oder 60 Minuten**. Ein 90-Minuten-Themenfenster besteht zum Beispiel aus einem 60- und einem 30-Minuten-Block; **keine 12-, 20-, 25-, 35- oder 50-Minuten-Blöcke** als selbständige Stundenplanposition. Ein 3–5-minütiger Impuls **innerhalb** eines 15-/30-Minuten-Blocks ist zulässig, aber kein separater Agendaposten. Pausen folgen ihren ausgewiesenen Dauern (typisch 15/45 Minuten).

**Maschinenlesbarer Zeitvertrag (anbieterneutral; konkrete Agenda hat Vorrang bei variabler Pausenlage):**

```yaml
schedule_policy:
  timezone: "Europe/Berlin"
  class_days:
    MON: {start: "09:00", end: "15:00"}
    TUE: {start: "09:00", end: "15:00"}
    WED: {start: "09:00", end: "15:00"}
    THU: {start: "09:00", end: "15:00"}
    FRI: {start: "09:00", end: "13:00"}
  allow_overtime: false
  allowed_agenda_block_minutes: [15, 30, 45, 60]
  breaks:
    coffee: {usual_start: "10:30", usual_end: "10:45", duration_minutes: 15}
    lunch: {duration_minutes: 45, usual_start_window: ["12:00", "12:30"], friday: "only_if_explicitly_scheduled"}
  agenda_must_list_exact_break_times: true
  require_contiguous_nonoverlapping_coverage: true
  must_not_infer_certification_ue_from_clock_time: true
```

Dieser Vertrag regelt die **Tagesplanung**, nicht automatisch die zertifizierungsrelevante UE-Verteilung. Die genaue Position der Pausen muss **vor Renderung** als konkretes Zeitintervall im DayBrief stehen; `usual_start_window` ist lediglich eine Orientierung, keine bereits beschlossene Uhrzeit.


**Plausible Beispielagenda Montag–Donnerstag (Pausenlage nur ein Planungsbeispiel):**

| Zeit | Minuten | Lernfunktion |
|---|---:|---|
| 09:00–09:30 | 30 | Einstieg, Vorwissen, Tagesziel |
| 09:30–10:30 | 60 | Tool-Demonstration und gemeinsames Erarbeiten |
| 10:30–10:45 | 15 | **Kaffeepause** |
| 10:45–11:30 | 45 | Angeleitete Praxis mit sichtbarem Ergebnis |
| 11:30–12:15 | 45 | Eigenständige Anwendung und Qualitätsprüfung |
| 12:15–13:00 | 45 | **Mittagspause** |
| 13:00–13:45 | 45 | Transfer- oder Projektaufgabe |
| 13:45–14:30 | 45 | Vergleich, Feedback, Verbesserung |
| 14:30–15:00 | 30 | Ergebnissicherung und Ausblick |

Das ergibt **360 Minuten Anwesenheitszeit, davon 60 Minuten Pausen und 300 Minuten geplante Lernzeit**. 300 Minuten sind ein Beispiel für den Regelfall mit 15 + 45 Minuten Pause, kein Ersatz für die Prüfung der **konkret freigegebenen** Tagesagenda.

**Plausible Beispielagenda Freitag (ohne automatisch gesetzte Mittagspause):**

| Zeit | Minuten | Lernfunktion |
|---|---:|---|
| 09:00–09:30 | 30 | Einstieg / Rückblick |
| 09:30–10:30 | 60 | Demonstration und gemeinsames Ausprobieren |
| 10:30–10:45 | 15 | **Kaffeepause** |
| 10:45–11:30 | 45 | Eigenständige Werkzeugpraxis |
| 11:30–12:15 | 45 | Anwendung auf beruflichen Fall |
| 12:15–13:00 | 45 | Ergebnisprüfung und Wochenabschluss |

Das ergibt bei **dieser beispielhaften Pausenplanung** 240 Minuten Anwesenheit und 225 Minuten Lernzeit. Bei zusätzlicher Freitagspause muss diese explizit ausgewiesen und die Lernzeit **innerhalb 09:00–13:00** entsprechend gekürzt werden.

**Pro Tagesplan zwingend ausweisen:** Start, Ende und Wochentag; Beginn/Ende jeder Pause; lückenlose, nicht überlappende Blöcke; Minuten jedes Themen-/Übungsblocks; Netto-Lernzeit aus der tatsächlichen Agenda; Einführungs-, Demonstrations-, Praxis-, Feedback- und Transferphasen; geplanten Tool-Setup-/Fallback-Pfad und Ergebnis jedes Blocks. Ein Zeitpuffer ist **Teil eines passenden 15-/30-/45-/60-Minuten-Blocks**, kein heimlich zusätzliches Zeitfenster.

**UE-Konflikt nicht übergehen:** Der Planungsstand von **41 UE/Woche bzw. 656 UE/16 Wochen** in `curriculum.md` ist **nicht rechnerisch identisch** mit den hier fixierten Live-Zeitfenstern. Die Zertifizierungs-/UE-Zuordnung und ggf. weitere Lernformen sind durch das Weiterbildungsmanagement zu klären. Eine Content Engine darf **keine zusätzlichen Uhrzeiten, Pausenkürzungen oder nicht vereinbarte Selbstlernzeiten erfinden**, um 41 UE zu erfüllen.

**Keine Folienzahl als Qualitätsersatz.** Ob 20, 40 oder 60 Folien entstehen, richtet sich nach Lernziel, tatsächlicher Praxis, Visualisierungsbedarf und Zeit. Produktionssysteme dürfen keine Folien strecken, um eine Stückzahl zu erreichen.

## 9. Fallbeispiele als roter Faden – ohne Zwang zur Konzernfallstudie

Ein konsistenter Fall reduziert kognitive Last. **Er darf das Lernen nicht verengen.** [S04]

**Geeignete Falltypen – nach Lernziel auswählen, nicht stets dieselbe Datenwelt:**

- **Recherche und Kommunikation:** Aussagen prüfen, E-Mails verbessern, Briefings erstellen, Tonalität für Zielgruppen anpassen;
- **Dokument- und Wissensarbeit:** ein langes Dokument auswerten, Quellen abgleichen, einen strukturierten Leitfaden oder eine Entscheidungsvorlage erstellen;
- **Präsentation und Medien:** Ausgangsfolie überarbeiten, eine Storyline entwickeln, Bild-/Video-/Audioentwürfe beurteilen;
- **Copilot und produktive Assistenz:** Wissensantwort, Meeting-Nachbereitung oder eine klar abgegrenzte Agentenaufgabe testen;
- **Design Thinking und Agilität:** Nutzerinterviews, Problemdefinitionen, Storyboards, MVP-Abwägungen und Review-Situationen;
- **KI-Strategie und Enablement:** Use Cases priorisieren, Einführungsgespräche, Schulungs- und Coaching-Situationen;
- **Technische Module:** Workflow-Tests, Datenübergaben, Berechtigungen oder API-Antworten mit fiktiven Datensätzen;
- optional ein durchgehender Unternehmensfall – wenn er die spezifischen Lernziele unterstützt.

**Regeln für Running Cases:**

1. Reale Probleme und Lernziele bestimmen den Fall – nicht umgekehrt.
2. Dieselben Namen/IDs/Fakten/Feldtypen bleiben über Folien und Material konstant.
3. Alle Abweichungen haben einen inhaltlichen Grund und sind als Änderung dokumentiert.
4. Unterschiedliche Quellen und Arten von Ergebnissen bleiben erkennbar (z. B. Originaldokument ≠ KI-Zusammenfassung; FAQ-Text ≠ Ticketstatus).
5. **Mehrere Quellen**, ungeprüfte KI-Ergänzungen und fehlende Angaben bleiben erkennbar.
6. Transfer auf eigene Fälle wird ermöglicht, ohne vertrauliche Daten in externe Tools hochzuladen.
7. Unterrichtsbeispiele dürfen wirtschaftliche Abteilungen, Rollen und Teamgrößen nicht unnötig voraussetzen.

Der Supportfall aus S08 ist ein **beobachtbares Pilotbeispiel** für Daten- und Rechteverständnis, nicht der verpflichtende Fall jedes 2027-Moduls.

## 10. Fachliche Präzisionsregeln in den zentralen Themen

**[REGEL]** Die folgende Themenliste ist eine Referenz für fachliche Korrektheit, **keine Aufforderung, jedes Thema in jede Kurswoche einzubauen**. Vorrang haben modulbezogene Lernziele und tatsächlich gelehrte Werkzeuge.

**Überwiegend anwendungsorientierte Module – typische Qualitätsgrenzen:**

| Thema | Fachlich richtige Anforderung | Unzulässige Verkürzung |
|---|---|---|
| Prompting / KI-Assistenten | Ziel, Kontext, Material, Ergebnisform und Prüfmaßstab nachvollziehbar steuern; Ergebnisse iterieren | „Es gibt einen universell besten Prompt.“ |
| Recherche | Primärquellen prüfen, Zitate verifizieren, Datum und Perspektive beachten | „Eine Quellenangabe der KI beweist ihre Behauptung.“ |
| Dokumente und Kommunikation | KI-Ausgabe gegen Original prüfen, Ton und Empfängerziel berücksichtigen, Datenschutz beachten | „Eine elegante Zusammenfassung ist automatisch korrekt.“ |
| Präsentationen und Medien | Storyline, fachliche Aussage, Lesbarkeit, Bild-/Nutzungsrechte und reales Endprodukt bewerten | „Gute KI-Folien sind vor allem schöne Bilder.“ |
| Design Thinking | beobachteten Bedarf von Annahmen trennen; Ideen und Tests am Problem ausrichten | „Eine KI-Persona ersetzt echte Nutzerforschung.“ |
| Vibe Coding | Anforderungen, Testfälle, Iterationen und Grenzen eines Prototyps sichtbar machen | „Wenn der Prototyp gut aussieht, ist die Anwendung fertig.“ |
| Agile Methoden | Vorgehen aus Team-/Projektbedarf begründen; inkrementellen Wert und Feedback nutzen | „Scrum, Kanban und Lean Startup sind austauschbare Listen von Ritualen.“ |
| KI-Strategie | Nutzen, Kosten, Umsetzbarkeit, Risiken, Verantwortlichkeiten und Einführung differenziert beurteilen | „Ein Tool-Demo-Erfolg ist eine belastbare Business-Case-Rechnung.“ |
| Schulung und Coaching | Lernbedarf klären, anleiten, Gesprächs- und Rollengrenzen beachten, Transfer prüfen | „Coaching ist synonym mit Tool-Erklärung oder Beratung.“ |

**Technische Module / technische Unterthemen – nur bei ausgewiesenem Scope:**

| Thema | Korrekte Abgrenzung | Typische unzulässige Vereinfachung |
|---|---|---|
| Generative KI / LLM | Modell erzeugt plausible Ergebnisse; Wahrheit muss extern geprüft werden | „Die KI weiß, ob die Aussage stimmt.“ |
| Recherche / RAG | Abruf aus definierten Quellen kann Ergebnisse stützen; Retrieval und Generierung sind getrennte Schritte | „Mit RAG halluziniert KI nicht mehr.“ |
| Markdown | leicht bearbeitbares Auszeichnungs-/Textformat für Inhalte, oft gut für Wissensnotizen | „Markdown ist eine Datenbank oder das Gedächtnis einer KI.“ |
| CSV | tabellarische Struktur; Delimiter, Encoding, Dezimal-/Datumsformat und Header beachten | „CSV hat überall dieselben Kommas und Spalten.“ |
| JSON | strukturierte Werte; Syntaxgültigkeit ≠ semantische Richtigkeit | „Gültiges JSON bedeutet korrekte Information.“ |
| Datentypen | ID kann Zeichenkette sein, `true`/`false` sind Booleans, `"offen"` ist Text | „Jede Bestellnummer ist eine Zahl.“ |
| API | definiertes Interface; Authentifizierung, Antwortformate und Methoden sind dienstabhängig | „Jede API braucht einen API-Key und antwortet in JSON.“ |
| Webhook | typischerweise ein ereignisgetriebener HTTP-Aufruf an einen Empfänger | „Webhook und wiederholte API-Abfrage sind dasselbe.“ |
| Workflow | definierte Steuerung, teils mit KI-Schritten; nicht zwingend „ohne KI“ | „Workflow = nie KI, Agent = immer völlig autonom.“ |
| KI-Agent | System kann innerhalb von Regeln Werkzeug- oder Handlungsentscheidungen treffen; Ausprägungen variieren | „Jeder Agent hat Langzeitgedächtnis und alle Rechte.“ |
| MCP | Standardisierte Verbindung von KI-Anwendungen zu angebotenen Werkzeugen/Ressourcen; kein Ersatz für APIs/Rechte | „MCP gibt der KI automatisch Zugriff auf alle Dateien.“ |
| Automatisierung | fehleranfällig, test- und beobachtungsbedürftig; Berechtigungen begrenzen Aktionen | „Wenn der Workflow einmal lief, ist er zuverlässig.“ |
| Copilot Studio | Wissen, Themen, Aktionen/Tools und Berechtigungen getrennt prüfen | „Quellenzugriff berechtigt automatisch zum Senden/Löschen.“ |
| Datenschutz / AI Act | konkrete Verarbeitung und Rolle prüfen; zuständiges Recht/Fachprüfung beachten | „Alle personenbezogenen Daten sind generell in jedem KI-Tool verboten.“ |
| Strategie / Nutzen | belastbare Annahmen, Alternativen, Kosten und Risiken dokumentieren | „KI spart immer X Prozent Zeit.“ |

**Technik- und Rechtsquellen:** Aktualisierungen sind in `content_workflow.md` geregelt. Die Tabelle ersetzt keine verifizierte Tool-Dokumentation oder Rechtsprüfung.

## 11. Anspruchsniveau ohne Redundanz

**Spiralförmiges Lernen** ist erwünscht: Eine Idee kehrt zurück, aber mit einer **neuen Operation, einem neuen Risiko oder einer neuen Entscheidung**.

**Praxisbeispiel – die gleiche berufliche Aufgabe auf wachsendem Kompetenzniveau:**

- **USE:** „Kann ich mit einem KI-Tool aus einem fiktiven Briefing einen belastbaren Entwurf erstellen und Fehler korrigieren?“
- **BUILD:** „Kann ich eine klar begrenzte Verarbeitung oder Assistenz für diesen Prozess umsetzen und testen?“
- **TRANSFORM:** „Soll diese Lösung eingesetzt werden, welche Alternative ist sinnvoll, und wie organisiere ich die Einführung?“
- **ENABLE:** „Wie leite ich Kolleginnen und Kollegen an, die Lösung sicher einzusetzen und Ergebnisse selbst zu prüfen?“

**Technisches Spezialbeispiel nur bei Daten-/Automatisierungszielen:** JSON lesen (USE) → Felder in n8n verarbeiten und testen (BUILD) → Datenzugriff und Betrieb bewerten (TRANSFORM) → Berechtigungsgrenzen vermitteln (ENABLE).

**Redundanztest:** Wenn sich zwischen zwei Einheiten weder Handlungskomplexität noch Betrachtungswinkel, Nachweis oder Transfer erhöht, ist mindestens eine Einheit zu kürzen, zu verknüpfen oder zu ersetzen.

## 12. Dozierendenperspektive als Qualitätsmaßstab

Eine fachlich anspruchsvolle Lehrperson muss mit dem Material:

- ohne erratene Zwischenschritte eine verständliche Dramaturgie erkennen;
- wissen, **warum** eine Folie folgt und welches Ergebnis sie vorbereitet;
- fachliche Rückfragen fundiert beantworten können;
- je Übung Material, Zeit, erwarteten Output und Lösung vorfinden;
- bei technischem Ausfall einen praktikablen Ausweichpfad haben;
- zur Gruppe passende Tiefe variieren können, ohne Lernziele zu verlassen;
- irreführende Behauptungen und veraltete Screenshots schnell erkennen;
- genug Raum für professionelle eigene Formulierungen und Kursführung behalten.

**Lehrhinweise:** Der Projektstandard ist eine separate, editierbare Notiz-/Leitfadenspur. Umfang und Entscheidung, ob Sprechernotizen direkt in die PPTX geschrieben werden, sind im `DayBrief` zu steuern. Sprechernotizen dürfen **nicht ohne Auftrag** eine explizite Vorgabe „keine Sprechernotizen“ überschreiben.

## 13. Kritischer Review aus drei Perspektiven

**Teilnehmende:** Kann ich selbst folgen? Habe ich etwas Reales gesehen, getan und überprüft? Verstehe ich den Nutzen? Weiß ich, was ich noch nicht kann?

**Dozierende:** Ist das fachlich korrekt? Stimmt die Reihenfolge? Sind die Aufgaben durchführbar? Muss ich wesentliche Inhalte improvisieren? Wo liegt die zulässige Vertiefung?

**Fachredaktion/Weiterbildungsmanagement:** Erreichen wir messbare Lernziele, erhalten die Folgemodule die richtigen Vorleistungen, sind Themen redundant, ist der Zeitplan realistisch, und was bedarf neuer fachlicher Prüfung?

**[REGEL] Keine positive Gesamtfreigabe, solange eine Perspektive einen kritischen Befund hat.** Die genaue Fehlerklassifikation steht in `qa_rules.md`.

## 14. Qualitätsbeispiel: von zu schwach zu gut

**Nicht produktionsreif (allgemeine Tool-Praxis):**

> „ChatGPT kann Meetingnotizen zusammenfassen. Probiert das einmal aus und diskutiert eure Ergebnisse.“

Fehlt: Ausgangsmaterial, konkreter Arbeitsauftrag, nachprüfbares Ergebnis, Qualitätskriterium, Zeit, Musterlösung, Hilfe und Transfer. Eine bloße Tool-Erwähnung ist **noch keine Übung**.

**Produktionsreif für USE – 30-Minuten-Übungsblock mit vorbereitetem Material:**

> **Problem:** Aus einer fiktiven, ungeordneten Meetingnotiz soll ein brauchbarer Ergebnisbericht werden.  
> **Input:** Ein bereitgestelltes einseitiges Protokoll enthält zwei nachweisbare Beschlüsse, eine offene Frage und eine nicht zugewiesene Aufgabe.  
> **Tool und Demonstration:** Die Lehrperson zeigt einen ersten KI-Entwurf und legt das Ausgangsmaterial daneben.  
> **Aufgabe (KERN):** Erstellt mit einem freigegebenen KI-Tool eine strukturierte Endfassung; markiert die beiden Beschlüsse und die offene Aufgabe; gleicht diese Stellen mit dem Original ab.  
> **PLUS:** Schreibt eine knappe Version für die Geschäftsleitung und erläutert die zwei wichtigsten Änderungen.  
> **Abgabe:** geprüfter Ergebnisbericht mit einer offen markierten Zuständigkeit.  
> **Musterlösung:** Nur die zwei ausdrücklich protokollierten Entscheidungen dürfen als „beschlossen“ erscheinen. Für die unzugewiesene Aufgabe ist „Verantwortlich: noch offen“ korrekt; eine von der KI erdachte Person ist zu streichen.  
> **Grenze:** Die Zusammenfassung darf nicht als unabhängiger Tatsachenbeleg genutzt werden.  
> **Fallback:** Ein vorbereiteter Erstentwurf wird ohne Live-Tool anhand des Originals verbessert.

**Alternative für TRANSFORM:** Ein fiktives Nutzerinterview zu einem internen KI-Assistenten auswerten; Beobachtungen, Interpretationen und Lösungsannahmen getrennt markieren; zwei überprüfbare Hypothesen formulieren. Eine bloß KI-generierte Persona ohne empirische Grundlage wäre **keine** valide Nutzerforschung.

**Alternative für technische Module:** Eine JSON-Antwort oder MCP-Werkzeugfreigabe mit korrekten Begriffen und Rechtegrenzen prüfen. Technische Fälle sind **gleichwertige, aber modulspezifische Spezialfälle** und keine Standardvorlage für sämtliche Kurswochen.

Keines der Beispiele ist als unveränderlicher Unterrichtsfall vorgeschrieben; die Content Engine muss zu jedem tatsächlich produzierten Beispiel das vollständige Arbeitsmaterial und die überprüfbare Lösung liefern.

## 15. Freigabefragen vor jeder Produktion

1. Ist das Ziel fachlich ambitioniert **und** für die Gruppe erreichbar?
2. Haben neue Begriffe ein korrektes Beispiel und eine sinnvolle Handlung?
3. Sind benötigte Vorkenntnisse, Vorbereitung und Hilfen explizit?
4. Existieren Pflichtaufgabe, optionale Vertiefung, Material und Musterlösung?
5. Ist die neue Kompetenz von benachbarten Modulen unterscheidbar?
6. Sind Quellen, fiktive Angaben, Annahmen und unbekannte Daten getrennt?
7. Liegt der Schwerpunkt **tatsächlich auf der zum Modul gehörenden Werkzeugpraxis** und ist jede technische Vertiefung aus dem Lernziel begründet?
8. Sind **Mo–Do 09:00–15:00 / Fr 09:00–13:00** eingehalten, Pausen in der Agenda ausgewiesen und alle Stundenplan-Blöcke **15/30/45/60 Minuten** lang?
9. Ist der Netto-Zeitbedarf plausibel, sind Toolausfälle innerhalb des Tages kompensierbar und wird nichts „angehängt“?
10. Ist der Übergang zwischen den Unterrichtsblöcken erkennbar?
11. Würde eine kritische Dozentin den roten Faden und die Fachbehauptungen akzeptieren?
12. Kann ein Teilnehmender nach dem Modul **konkret mit einem Tool bzw. einer Methode arbeiten und das Ergebnis prüfen**, statt nur Folien wiederzugeben?

**Rückgabe an den Agenten:** Wenn eine Antwort „nein“ lautet, wird ein konkret verorteter Verbesserungsauftrag erzeugt – nicht ein pauschales „didaktisch optimieren“.

## 16. Pflege

| Version | Datum | Änderung |
|---|---|---|
| 1.0.0 | 2026-11-18 | Erster konsolidierter fachlich-didaktischer Regelentwurf für alle vier Phasen |
| 1.1.0 | 2026-11-18 | Tool-/Berufspraxis als Regelfall; technische Beispiele modulspezifisch; feste Mo–Do-/Fr-Zeiten, explizite Pausen und 15/30/45/60-Minuten-Agendablocks |

Referenzen in diesem Dokument: `S03` Stammdatenblatt, `S04` USE-Lehrplan sowie `S05–S08` Bestands-/Pilotpräsentationen; Definitionen der Kürzel siehe `curriculum.md`.
