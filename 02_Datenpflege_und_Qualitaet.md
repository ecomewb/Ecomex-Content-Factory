# Datenpflege und Qualitätsregeln

## Grundsatz: eine Quelle der Wahrheit je Objekt

- **Git:** Freigegebene Fassung der Norm- und Promptdateien. Jede Änderung ist ein Review/Commit; in Bearbeitung stehende Normen behalten `working_draft`.
- **SharePoint:** Unveränderter Ursprung und final freigegebene Präsentationsartefakte; nie als eigenmächtig „aktuell“ umdeuten.
- **Supabase:** Suchindex + Herkunftsregister, **keine konkurrierende Kopie** der normativen ECOMEX-MD-Dateien.
- **n8n:** Produktionslauf mit konkreten Versionsnummern und dokumentierten Freigaben.

## Dokumentstatus

`draft` = unvollständig; `reference` = Material, das kontextualisiert/überprüft werden muss; `approved` = für klar definierten Zweck fachlich freigegeben; `archived` = nicht mehr als aktuell verwenden.

`access_class` ist davon getrennt: `public`, `internal`, `restricted`. Freigabe bedeutet NICHT automatisch Weitergabe an externe LLM-Anbieter.

## Ingestion-Prinzip

1. Quellrechte, Lizenz, Datenschutz und Versionsnummer prüfen.
2. Original ausschließlich in genehmigtem Storage belassen.
3. Text, Sprechertexte, Diagrammaussagen und Fundstellen ermitteln (Bild-/Tabelleninhalte notfalls gesondert prüfen).
4. Fachlich sinnvolle Abschnitte bilden; z. B. 1–3 Folien eines Themas statt starrer 500-Zeichen-Chunks.
5. Metadaten setzen: `source_id`, **`embedding_model: text-embedding-3-small`**, `locator`, `module_id`, `content_type`, `chunk_index`, `source_version`, optional `verified_at`. Bei fehlendem/anderem Modellwert darf kein Vektor geschrieben werden.
6. Exakt ein **festgelegtes Embedding-Modell** für den Pilot verwenden. Embeddings verschiedener Modelle nicht vermischen.
7. Erst nach erfolgreichem Suchtest als verwendbar markieren.

## Änderung und Aktualisierung

- **Normänderung:** Git-Commit → Review → neue Version → betroffene Content-Jobs als `NEEDS_REVIEW` markieren.
- **Quellenänderung:** neuen Hash/Version prüfen → betroffene Chunks ersetzen (kein blindes Anhängen) → Embeddings neu berechnen → alte Version dokumentieren.
- **Neue Fachinformation aus dem Web:** Primärquelle und Abrufdatum erfassen → Claim prüfen → erst nach Review in freigegebenen Bestand aufnehmen.
- **LLM-Erzeugnisse:** immer als Entwurf kennzeichnen; nicht automatisch in `approved` überführen.

## Sicherheitsregeln

- Secrets nur in n8n-Credentials/zugelassenen Secret Stores.
- Rollen nach Least Privilege; produktive Schreibzugänge getrennt von Agent-Lesezugängen.
- Tabellen haben RLS. Vor produktivem Rollout getrennte serverseitige Rollen/Endpoints einführen: Read/Search für Agenten, Write/Ingest für kontrollierten Workflow. Der erste Pilot verwendet noch einen administrativen Secret Key auf dem Server – keine direkte Agentenfreigabe.
- Lösch-/Überschreiboperationen erfordern Versionsprüfung und dokumentierten Freigabeprozess.
- DSGVO/Urheberrecht und Rechte zur Nutzung von Dozentenmaterialien gesondert klären.
