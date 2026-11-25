# ECOMEX Content Factory – Starterpaket 0.1

**Zweck:** Sichere, nachvollziehbare Einrichtung von Git + Supabase als Basis für n8n-gesteuerte Content- und Designagenten.

## Zuerst lesen

1. `docs/01_Einrichtung_fuer_Einsteiger.md` – Schritt für Schritt ohne Terminal
2. `docs/02_Datenpflege_und_Qualitaet.md` – Pflege, Berechtigungen, Freigaben
3. `docs/03_Agenten_und_n8n.md` – Rollen und Datenflüsse
4. `database/001_create_kb.sql` – vorgeschlagene Pilotdatenbank, vor Ausführung prüfen

## Wichtig: Bestehende ECOMEX-Arbeit ist unverändert übernommen

Die fünf Dateien unter `governance/` stammen aus dem vorhandenen Wissensstand. **Es wurde kein Inhalt umgeschrieben**, es wird kein `working_draft` zu `approved` erklärt. Ergänzende KI-kuratierte Methode unter `optional_methods/` bleibt optional.

Der aktuelle Folienmaster `design/ECOMEX_Masterlayout_6.2.pptx` und die technische Layoutbibliothek werden als Designreferenz eingebunden. Die PPTX kann alternativ in SharePoint liegen und nur referenziert werden.

**Hinweis Layoutbibliothek:** Die Dateien `design/ECOMEX_*_v3.json` wurden aus Master 6.1 erzeugt. Master 6.2 enthält zusätzlich u. a. Frage 1–5 sowie Kapitel/Unterkapitel/Inhalt in Farbvarianten; die Bildfolien „05/06 · Bildfolie | Großmotiv“ aus 6.1 fehlen in 6.2. Der Katalog wird im nächsten Schritt an 6.2 angeglichen.

## Nicht enthalten

- Keine aktiven API-Verbindungen oder Credentials.
- Keine vollständige n8n-Agentenautomation.
- Keine bereinigten, indexierten Fachquellen aus Bestandspräsentationen.
- Keine offiziell geprüfte Datenschutz-/Rechtefreigabe.

## Ergebnis von Schritt 1

Nach Einrichtung kannst du (1) Normdateien versioniert bearbeiten, (2) Quellen in Supabase nachvollziehbar registrieren, (3) später gezielt durch RAG abrufen und (4) Content-/Designagenten über definierte Schnittstellen einsetzen.
