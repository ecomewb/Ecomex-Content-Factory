# ECOMEX Content Factory – Einrichtung für Einsteiger

> Stand: 19.11.2026 · Technischer Entwurf, **nicht produktiv freigegeben**. Reihenfolge ist verbindlich.

## Vorweg: Was wohin gehört?

| Ablage | Inhalt | Wie ändere ich das später? |
|---|---|---|
| **Privates Git-Repository** (GitHub-Weboberfläche oder Azure DevOps Repos) | Fünf normative MD-Dateien, JSON-Schemas, technische Konfiguration, SQL-Skripte | Datei im Browser bearbeiten, Änderung kommentieren, nach Review übernehmen |
| **SharePoint** | Ursprüngliche Dozentenpräsentationen, große PPTX-Dateien, endgültige Decks | Bestehende Microsoft-Oberfläche |
| **Supabase** | Quellenregister, inhaltliche Textabschnitte, Embeddings und Nachweis der Herkunft | Quellenmetadaten über Table Editor, Inhalte vorerst über einen kontrollierten n8n-Ingestion-Prozess |
| **n8n** | Aufnahme, Wissensabruf, Storyboarding, Content- und Designproduktion, QA, Freigabe | Grafische Workflows |

> Ein Claude-Projekt ist ein optionaler Arbeitsraum, **nicht** die maßgebliche Versionsablage. Das LLM darf Normen nicht autonom überschreiben.

## Schritt 1 – Git-Ablage anlegen (ohne Terminal)

1. In der gewählten Plattform anmelden (privates **Unternehmenskonto**, nicht persönliches Experimentalkonto). GitHub ist eine Option; Azure DevOps Repos passt zu Eurer Microsoft-Landschaft.
2. Neues **privates** Repository `ecomex-content-factory` anlegen. Sichtbarkeit vor dem Upload nochmals kontrollieren.
3. ZIP entpacken; zunächst die Ordner `governance/`, `design/` (der beiliegende **Lite-Download enthält keine große PPTX**; diese separat in SharePoint lassen), `database/`, `docs/`, `samples/`, `n8n/` hochladen. Die große Master-PPTX kann in SharePoint liegen; in Git reicht später ein Manifest-/Versionsverweis.
4. `governance/*.md` im Browser öffnen: Fünf Quelldateien sind **unverändert** übernommen und behalten ihren bisherigen `status` (z. B. `working_draft`). Keine automatische Freigabe!
5. Für Änderungen: Datei öffnen → Bearbeiten → präzise Änderung → kurze Commit-Nachricht. Für Normänderungen idealerweise Review durch zweite Person und erst danach Merge.
6. Nur redaktionelle Regeln in Git; keine personenbezogenen Daten, API-Keys oder Kundendokumente hochladen.

**Qualitätsprobe:** Öffne `governance/didaktik.md` und suche nach `09:00–15:00` und den Praxisbeispielen. Die Datei muss vollständig lesbar sein.

## Schritt 2 – Supabase-Projekt anlegen

1. Auf [supabase.com/dashboard](https://supabase.com/dashboard) mit dem ECOMEX-Organisationskonto anmelden.
2. **New project** innerhalb der bestehenden Pro-Organisation anlegen; Name z. B. `ecomex-content-factory-dev`, Region nach interner Datenschutz-/IT-Freigabe wählen. **Pro-Organisation heißt nicht zwingend, dass jedes zusätzliche Projekt ohne weitere Kosten ist.**
3. Projekt-URL notieren (keine geheimen Schlüssel in Chats, MD-Dateien oder Git).
4. Prüfen, dass kein bestehendes Kundendatenprojekt als Testumgebung verwendet wird.
5. Unter **SQL Editor** das Skript `database/001_create_kb.sql` öffnen. **Nur im leeren, neuen Projekt** ausführen. Vorher von IT/Datenbankverantwortung prüfen lassen. Es erstellt Tabellen und eine Suchfunktion, löscht keine Daten.
6. Unter **Table Editor** sollten `ecomex_sources` und `ecomex_documents` erscheinen; unter **Database → Extensions** sollte `vector` aktiv sein.
7. Kein `anon`-/öffentlicher Lesezugriff. Der Entwurf aktiviert RLS ohne Freigabepolicies. n8n nutzt später einen geheimen serverseitigen Schlüssel im Credential Store.

**Wichtig zu SQL-Editor:** Für die Pilotphase möglich. Bei langfristiger Entwicklung auf CLI-Migrationen umstellen; SQL-Editor-Änderungen werden nicht automatisch in der offiziellen Migrationshistorie erfasst. Das erste Skript als Baseline archivieren und spätere Änderungen abstimmen.

## Schritt 3 – Erst eine Quelle registrieren, dann Chunks importieren

1. Eine intern verwendbare, nicht vertrauliche Beispielpräsentation in SharePoint wählen.
2. In `ecomex_sources` eine Zeile mit stabiler `source_id`, Titel, SharePoint-Pfad, Version, `review_status='reference'`, `access_class='internal'` anlegen.
3. **Noch keine automatische Inhaltsfreigabe!** Die ursprüngliche Präsentation ist Referenz, nicht verbindlicher Unterrichtsstandard.
4. Der spätere Ingestion-Workflow extrahiert Folien und Notizen, bereinigt personenbezogene Angaben, erzeugt pro Abschnitt `content`, `metadata` mit `source_id` und `embedding_model` sowie `embedding` und schreibt in `ecomex_documents`.
5. Gezielter Test: Frag nach einem tatsächlich im Referenzdeck enthaltenen Sachverhalt. Das Suchergebnis muss `source_id` und Folienlocator zurückgeben. Prüfe es im Original.

## Schritt 4 – n8n nur lesend anbinden

1. In n8n eine **Supabase Credential** für das Entwicklungsprojekt anlegen. URL ohne `/rest/v1`; **secret key nur in Credential-Einstellungen** und nie in Set-/Code-Nodes, Prompts oder Screenshots.
2. Einen einfachen Workflow `KB – Recherchetest` anlegen: Manual Trigger → Frage/Modul → Embedding desselben Modells wie im Index → Supabase Vector Store/geeigneter RPC-Aufruf → Fundstellen anzeigen.
3. Vor dem Agenten erst testen: Welche Quelle wird gefunden? Wird der Status `reference` respektiert? Ist der Auszug wirklich relevant?
4. In der ersten Version **keine autonomen Schreib-/Löschrechte** für Content- und Design-Agenten; die Aufnahme läuft über einen separaten kontrollierten Workflow.

## Schritt 5 – Content- und Design-Agenten verbinden

- **Content-Agent** liest freigegebene normative MD-Versionen + zielgerichtete Quellen aus Supabase + recherchiert neue Fakten aus überprüfbaren Internetquellen (nur wenn zugelassen). Er erzeugt `SourceBrief`, `DayBrief`, `SlidePlan`, Übungen und `SlideSpecs` mit Quellen-/Freigabestatus.
- **Design-Agent** liest `governance/design.md`, den tatsächlich freigegebenen Master und den Layoutkatalog. Er ändert **keine** fachlichen Aussagen und keine ECOMEX-Farben, Schriftfamilien oder Logo-Position; erzeugt Layout-IDs und visuelle Spezifikationen.
- **QA** prüft Quellen, Didaktik, Layout, Datensicherheit und tatsächliche Ausgabe; **menschliche Freigabe** vor Veröffentlichung.
- **n8n** orchestriert die Schritte und übergibt strukturierte Daten. **SharePoint** enthält finale, tatsächlich freigegebene PPTX-Artefakte.

## Was wir absichtlich NOCH NICHT tun

- Kein automatisches „Selbstlernen“ aus KI-Ausgaben ohne fachlichen Review.
- Kein Vollimport aller Originaldecks mit ungeprüften Zugriffsrechten.
- Keine Web-Recherche als ungeprüfter Ersatz für Primärquellen.
- Keine verteilten Agenten mit gemeinsamen Schreibrechten auf Normdateien.
- Keine Produktion ganzer Kurswochen vor dem Pilot eines Unterrichtstags.

## Die ersten drei Abnahmetests

1. **Version:** Änderung an einer MD-Datei ist im Git-Verlauf sichtbar und rücknehmbar.
2. **Provenienz:** Eine Supabase-Suchantwort nennt Quelle und Folie; referenzierter Originaltext ist auffindbar.
3. **Sicherheit:** Ohne explizite Freigabe kann eine unbekannte/noch als `draft` markierte Quelle nicht als autoritative Basis in der Suche erscheinen.
