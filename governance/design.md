---
document_id: ecomex.design
title: "ECOMEX | Designsystem für Lernmaterialien"
version: "1.0.0"
status: "provisional_until_brand_master_approved"
last_reviewed: "2026-11-18"
language: "de-DE"
applies_to: ["PPTX", "PDF-Export", "Workbooks", "Übungsunterlagen", "Diagramme"]
depends_on: ["didaktik.md", "qa_rules.md"]
---

# Design: ECOMEX-Designsprache und Layoutprinzipien

## 1. Geltungsbereich und Herkunft

Dieses Dokument verbindet **beobachtbare** ECOMEX-Gestaltungsmerkmale mit **vorgeschlagenen verbindlichen Produktionsregeln**. Es ist kein offizielles Corporate-Design-Handbuch.

**Gesichert aus den bereitgestellten Dateien:**

- Die bereitgestellten Präsentationen verwenden **16:9** (technisch 10,0 × 5,625 Zoll) und enthalten einen wiederkehrenden hellen, sachlichen Stil, dunkle Textfarben, Blau/Türkis-Akzente und modulare Übersichts-/Übungsfolien. [S05–S08]
- Die November-2026-PDFs zeigen ECOMEX-Logo, dunkle Titel, farbige Phasenmarkierungen, helle Flächen, deutliche Strukturierung und die Abfolge **USE / BUILD / TRANSFORM / ENABLE**. [S01, S02]
- In S01/S02 ist die sichtbare PDF-Schrift überwiegend **Lato**; in den bestehenden PPTX-Dateien S05–S08 überwiegt **Open Sans**. Die Dateien zeigen damit **mehr als eine Gestaltungsvariante**.
- S08 ist **Pilotmaterial zur automatisierten Content-Erzeugung**, ausdrücklich **kein** festgeschriebener Master für Folientypen, Dichte oder Aufbau.

**Noch zu entscheiden:** Das formell freigegebene ECOMEX-Template (`.potx`/`.pptx` inkl. Masterlayouts), Logo-Assets, Lizenzlage und etwaige zentral definierte Hausschriften/Abstände fehlen in der übergebenen Referenzmenge. **Beim Rendern hat ein künftig freigegebener echter Markenmaster Vorrang vor den hier dokumentierten Näherungswerten.** Keine fiktive „offizielle Design-Guideline“ behaupten.

## 2. Visuelle Haltung

**Professionell, modern, ruhig, klar und gut unterrichtbar.**

- **Didaktische Verständlichkeit vor Dekoration:** Eine visuelle Aussage ist nur gut, wenn sie Verstehen oder Wiedererkennen verbessert.
- **Reduktion ohne Inhaltsverlust:** Komplexe Inhalte dürfen auf mehrere Folien aufgeteilt werden; Fachgenauigkeit bleibt erhalten.
- **Inhalt vor Layout:** Erst wird die fachlich freigegebene `SlideSpec` erarbeitet, dann eine geeignete Visualisierung ausgewählt.
- **Kontrast statt Effekt:** Dunkle Typografie auf hellen Flächen, Akzentfarbe gezielt für Orientierung und didaktische Beziehungen.
- **Wiedererkennung:** gleiche Komponenten und Anordnung bei ähnlichen Lernhandlungen, aber keine monotone Abfolge identischer Textfolien.
- **Native Editierbarkeit:** Flussdiagramme, Tabellen, Pfeile und Beschriftungen nach Möglichkeit als bearbeitbare PPTX-Elemente.

Nicht erwünscht: vollflächige generische KI-Bilder auf jeder Folie; unbegründete Gradients, überladene Icons, winzige Fließtexte, kunstvolle aber unlesbare Grafiken, isolierte „Tool-Folien“ ohne Aussage.

## 3. Vorläufige Design-Tokens – **aus ECOMEX-PDFs abgeleitet**

Diese Hexwerte wurden aus den gelieferten PDF-Grafikelementen ausgelesen. Sie sind **beobachtete Referenzwerte**, keine Freigabe eines verbindlichen CI-Handbuchs.

| Token | Wert | Beobachteter Einsatz / empfohlene Nutzung |
|---|---|---|
| `navy` | `#1E3F63` | dunkle Überschriften, starke Struktur |
| `ink` | `#21364B` | Haupttext auf hellen Flächen |
| `muted_ink` | `#51677A` | sekundäre Angaben |
| `white` | `#FFFFFF` | neutraler Hintergrund / Kontrasttext auf dunkler Fläche |
| `panel` | `#F1F8FC` | helle Informationsfläche |
| `use_blue` | `#49B0E4` | Phase USE / allgemeiner Akzent |
| `build_teal` | `#2A9D8F` | Phase BUILD |
| `transform_gold` | `#DB9D45` | Phase TRANSFORM |
| `enable_coral` | `#E77E64` | Phase ENABLE |

**Quellenhinweis:** In S02 sind nahe Farbvarianten sichtbar, z. B. `#2F9CD1`, `#E4AB42`, `#E57E64`. Andere Decks verwenden teilweise `#48AFE3`, `#326395`, `#FF8B6B`. **Diese Werte sind Dokumentvarianten, nicht zehn gleichzeitig zu mischende Primärfarben.** Für eine neue konsistente 2027-Produktserie soll zunächst die Token-Tabelle aus S01 gelten, solange kein Markenmaster gegenteilig entscheidet.

**Semantik:** Blau/Teal/Gold/Koralle werden vorzugsweise als **Phasenfarben** verwendet, nicht willkürlich für „richtig/falsch“ oder Gefahrenstufen umdefiniert. Fehler und Warnungen zusätzlich über Text, Form oder Icon kennzeichnen; niemals nur über Farbe.

### Maschinenlesbarer Startblock (vorläufig)

```yaml
design_tokens:
  version: "1.0.0"
  authority: "provisional_pdf_observation"
  canvas:
    ratio: "16:9"
    width_emu: 9144000
    height_emu: 5143500
  colors:
    navy: "#1E3F63"
    ink: "#21364B"
    muted_ink: "#51677A"
    background: "#FFFFFF"
    panel: "#F1F8FC"
    USE: "#49B0E4"
    BUILD: "#2A9D8F"
    TRANSFORM: "#DB9D45"
    ENABLE: "#E77E64"
  typography:
    deck_reference: "Open Sans"
    handout_reference: "Lato"
    official_master_required: true
  logo:
    source: "approved ECOMEX brand asset"
    reconstruct_from_text: false
```

Der Renderer liest diese Daten als **Fallback-Tokens**. Nach Freigabe ersetzt ein versionskontrolliertes Brand-Token-Set einzelne Werte, **ohne die Unterrichtsinhalte neu zu generieren**.

## 4. Typografie und Lesbarkeit

**Bestehende Dateien:** Open Sans/Open Sans Light/Semibold in PPTX; Lato in den beiden PDFs. Die Entscheidung über eine verbindliche Hausschrift ist offen. Bevorzugte Produktionslogik:

- Verwende die Font-Definitionen eines freigegebenen Masterlayouts; keine willkürlichen Schriftwechsel pro Folie.
- Klarer Typohierarchie: **Folienschwerpunkt > Kernaussage > Beispiel/Diagramm > Quellen/Meta**.
- Normaler Folientext soll aus üblichem Präsentationsabstand lesbar sein. Für neue 16:9-Decks **ca. 18 pt oder größer anstreben**; 16 pt ist eine **zu prüfende untere Warnschwelle**, **keine generelle Rechtfertigung** für dichte Folien.
- Titel typischerweise **24–32 pt oder größer**, abhängig von echtem Master und Raum; kurze verständliche Titel bevorzugen.
- Code/JSON/API-Beispiele so groß und kontrastreich setzen, dass Zeichen, Anführungszeichen, Klammern und Schlüssel/Wert-Zuordnung nachvollziehbar sind.
- Kleingedruckte Quellen/Abbildungscredits ggf. kompakt, aber nicht zum versteckten inhaltlichen Pflichtbestandteil machen.
- **Nie allein durch starkes Verkleinern „passend“ machen**. Wenn etwas nicht lesbar bleibt: reduzieren, auslagern, in zwei Lernschritte teilen oder als Handout bereitstellen.

**Wichtig:** In den alten Foliensätzen sind viele kleine Schriftgrade vorhanden. Sie sind für eine neue Content Engine **kein anzustrebender Qualitätsstandard**.

## 5. Raster, Abstände und Anordnung

Die folgenden Prinzipien sind eine **redaktionelle Regel**, keine ausgemessene offizielle Rasterdatei:

- Visuell konsistente Ränder und Ausrichtung; sichtbare Elemente halten Abstand zu Folienkanten.
- Ein Titelbereich und ein klarer Inhaltsbereich; Fußbereich nur für notwendige Metadaten.
- Gleichartige Elemente teilen Achsen, Abstände, Breiten, Höhen und Eckformen.
- Gleichmäßige innere Abstände in Boxen; Text kollidiert nie mit Rahmen/Icons.
- Weißraum dient dem Denken und der Orientierung, nicht nur dem ästhetischen Effekt.
- Pfeile und Linien kodieren eine echte Relation: Reihenfolge, Datenfluss, Abhängigkeit oder Entscheidung.
- **Keine falschen Prozessketten:** Parallele Datenquellen nicht als Umwandlungskette darstellen. Eine FAQ als Markdown und ein Ticket als JSON bleiben unterschiedliche Informationsquellen.
- Feste Figuren-/Icon-Sets nicht unmotiviert mischen. Keine Symbole, deren Bedeutung nicht erklärbar ist.
- Dekoration darf niemals notwendige Inhalte oder Bedienelemente überdecken.

## 6. Empfohlene Folientypen als Renderer-Bausteine

| Layout-ID | Typischer Zweck | Inhaltliches Pflichtmerkmal |
|---|---|---|
| `cover` | Modul/Tag eröffnen | Titel, Einordnung, ggf. Dozent und Datum; kein Platzhalter |
| `agenda` | Lernverlauf orientieren | echte Tagesblöcke, Pausen und erwartete Ergebnisse |
| `learning_outcomes` | Erwartungen setzen | messbare Kompetenzen statt vager Begriffe |
| `problem_hook` | Relevanz herstellen | konkretes Problem oder Entscheidungsfrage |
| `concept_visual` | Mechanik erklären | fachlich korrektes Diagramm, eindeutige Relationen |
| `worked_example` | Beispiel vollständig zeigen | Daten, Handlung, Interpretation, Prüfschritt |
| `comparison` | Optionen abgrenzen | identische Vergleichskriterien, keine Scheinalternativen |
| `process_flow` | Vorgang erklären | Start/Ende, Informationswege, Akteure, Kontrollpunkte |
| `annotated_data` | CSV/JSON/API exemplarisch lesen | editierbarer, syntaktisch geprüfter Ausschnitt |
| `exercise` | angeleitete / selbständige Arbeit | Aufgabe, Material, Zeit, Sozialform, Output, Basis/Plus |
| `solution` | Selbstkontrolle / Diskussion | richtige Lösung und Begründung, typische Fehler |
| `reflection_transfer` | Transfer sichern | Was kann ich, wann nutze ich es, was prüfe ich? |
| `chapter_transition` | Orientierung / Rollenwechsel | klarer Rück- und Vorausbezug statt dekorativer Leerseite |
| `source_status` | fachliche Nachvollziehbarkeit | Quellen, Abruf-/Versionsstand, ggf. fiktiver Status |

**Keine Pflicht, alle Folientypen zu verwenden.** Layoutwahl ergibt sich aus Lehrziel und Inhalt, nicht aus einer zu erfüllenden Template-Quote.

## 7. Visualisierungsregeln nach Inhalt

- **Datenformate:** tatsächlicher JSON-/CSV-/Markdown-Ausschnitt, optische Annotationen, Datenquelle und Typunterschiede.
- **API / MCP:** beschriftete Systemgrenzen, Rollen (Host/Client/Server), Daten-/Rechtefluss, mögliche Fehlerstellen.
- **n8n / Copilot Studio:** echte, datierte und zur unterrichteten Version passende UI-Screenshots **oder** abstrahierte, ausdrücklich schematische Schritte; Screenshots nie als unveränderliche Wahrheit.
- **Use-Case-Vergleich:** kompakte Entscheidungsmatrix mit nachvollziehbaren Kriterien statt dekorativer Score-Badges.
- **Strategie:** Trade-offs, Entscheidungslogik, Alternativen und Annahmen sichtbar machen; keine unbelegten Zahlen.
- **Agile Methoden:** konkrete Backlog-Items, MVP/Feedbackschleife und Übergang zu einem realen KI-Projekt, nicht nur eine Framework-Tabelle.
- **Coaching/Enablement:** Gesprächsbeispiele, Moderationssituationen, Rollen- und Verantwortungsgrenzen, Transferfragen.
- **Recht/Governance:** sachliche Fallentscheidung und Eskalationsweg; keine simplifizierende Ampel als alleinige Rechtsbewertung.

**Bilder:** Ein Bild erhält eine didaktische Funktion, eine zulässige Nutzungslizenz, einen Quellen-/Credit-Eintrag und, soweit sinnvoll, Alternativtext. Keine generischen KI-Gehirne als Ersatz für Abbildungen einer konkreten Mechanik.

## 8. Editierbarkeit und PowerPoint-Qualität

**Priorität:** Fachlich nachvollziehbare PPTX, die ECOMEX intern und von externen Dozierenden ohne Bildbearbeitung angepasst werden kann.

- Texte bleiben echte Textobjekte.
- Tabellen, Pfeile, Boxen und einfache Prozessgrafiken bleiben nach Möglichkeit native Shapes.
- Schaubilder dürfen als Bild gerendert werden, wenn technisch nötig, sollen aber dann Quell-Datei/Diagrammspezifikation erhalten.
- Original-Assets und Dateirechte respektieren; keine fremden Logos automatisch nachbauen oder verändern.
- Diagrammwerte, Tabellenzahlen und Quellenverweise müssen redaktionell nachbearbeitbar sein.
- `SlideSpec` und Assetmanifest bleiben unabhängig von PowerPoint erhalten, sodass ein anderer Renderer oder ein anderes LLM dieselbe inhaltliche Grundlage nutzen kann.
- PPTX **und** exportierte Folienbilder/PDF werden visuell geprüft. PowerPoint-Datei allein ist kein QA-Nachweis.

## 9. Entwurfsschwellen für automatische Sichtprüfung

Die Zahlen sind **Review-Schwellen, nicht CI-Normen**. Abweichungen erfordern begründete Prüfung statt blindem Umschreiben.

| Prüfkriterium | Prüfheuristik | Reaktion |
|---|---|---|
| Titellänge | ca. 55 Zeichen als Richtwert | bei Umbruch oder Clipping überprüfen |
| Textmenge | häufig ca. 45–65 Wörter auf normaler Inhaltsfolie | bessere Visualisierung oder Teilung erwägen |
| Normaler Bodytext | Ziel ≥ 18 pt, 16 pt als Warnschwelle | Lesbarkeit im Render prüfen |
| Textüberlauf | kein Abschneiden/Überdecken | **hart blockieren** |
| Kontrast | WCAG-orientierter Kontrast-Check, bei Text i. d. R. 4,5:1 als Ziel | manuell/automatisch prüfen |
| Layout-Konsistenz | Ränder, Abstände, Typogrößen, Phasenfarben | Abweichung begründen |
| Bildqualität | Motiv und Lesbarkeit bei Präsentationsgröße | ersetzen/neu rendern |
| Datendiagramme | Einheiten, Achsen, Quellen, Annahmen lesbar | bei fehlender Aussage blockieren |

Kontrastprüfungen sind ein sinnvolles technisches Prüfwerkzeug, aber nicht jede PPTX kann vollautomatisch auf Zugänglichkeit geprüft werden. Wahrnehmungsprüfung durch Menschen bleibt erforderlich.

## 10. Gestaltung für mehrtägige Lehrgänge

- Konsistenter Deckkopf/Titelhierarchie über **alle Tage**, nicht nur innerhalb eines Tages.
- Am Tagesanfang minimaler Recap und Einordnung; neue Ebene klar markieren.
- Nicht dieselben Intro- und Grundlagendefinitionen jeden Tag erneut.
- Phasenfarben als Wegweiser **über Module hinweg** erhalten.
- Neue UI-Versionen oder neue Beispiele dürfen die Lernzielstruktur nicht zerstören.
- Wochen- oder Modulübergänge mit fachlicher **„Was kann ich jetzt? / Was folgt daraus?“**-Brücke statt beliebiger Kapiteltrenner.
- Eine separate Materialspur für komplexe Datensätze, Arbeitsanweisungen, Musterlösungen und ggf. Dozentenleitfäden.

## 11. Freigabebedarf und Änderungsspielraum

**Human Approval erforderlich:**

1. Welcher originale ECOMEX-PPTX-Master ist freigegeben?
2. Soll `Open Sans` als Folienschrift und `Lato` nur für PDF-/Handout-Referenzen gelten – oder eine einheitliche Hausschrift?
3. Welche Logo-Dateien und Lizenzrechte dürfen automatisiert verwendet werden?
4. Welche Layouts/Abstände sind tatsächlich CI-verbindlich?
5. Wie sollen Quellen, Autor, Kursdatum und Dozentenname auf Folien erscheinen?

**Ohne diese Entscheidung:** Produktionssysteme dürfen nur einen als **vorläufig** gekennzeichneten, dokumenttreuen Entwurf mit den obigen Fallback-Werten liefern; keine ungeprüfte Behauptung „100 % CI-konform“.

## 12. Changelog

| Version | Datum | Änderung |
|---|---|---|
| 1.0.0 | 2026-11-18 | Vorläufiges Designsystem aus November-2026-PDFs und vier vorhandenen PPTX-Decks; feste Trennung von beobachteten Tokens und neuen Produktionsregeln |

Quellenkürzel siehe `curriculum.md`.
