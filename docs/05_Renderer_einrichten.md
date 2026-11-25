# 05 · Renderer einrichten (für IT / Hetzner-Server)

Der **ECOMEX Folien-Renderer** ist ein kleiner interner Webdienst. n8n schickt ihm die fertigen Folieninhalte,
er baut daraus eine editierbare PowerPoint im echten ECOMEX-Folienmaster, eine PDF-Vorschau und einen
Prüfbericht, und er liest PowerPoint-/Word-/Excel-/PDF-Dateien für die Wissensbasis aus.
Kein KI-Aufruf, keine Datenbank, keine Datenhaltung – jede Anfrage wird im Speicher verarbeitet.

Die Workflows laufen auch ohne Renderer. Mit Renderer werden die Folien aber exakt im Master gesetzt,
automatisch geprüft und visuell kontrolliert – und es entstehen keine Kosten für den Ersatzweg über Claude.

## Was gebraucht wird

| | |
|---|---|
| Ort | derselbe Hetzner-Server/Docker-Host wie n8n |
| Software | Docker mit Compose |
| Ressourcen | 1 vCPU, 1–1,5 GB RAM, ca. 1,2 GB Plattenplatz für das Image |
| Netz | nur intern: gleiches Docker-Netz wie der n8n-Container, **kein** öffentlicher Port |
| Image | `ghcr.io/ecomewb/ecomex-renderer:latest` (enthält den ECOMEX-Master 6.2) |

## Einrichtung (ca. 15 Minuten)

Auf dem Hetzner-Server per SSH. Liegt n8n auf einem anderen Hetzner-Server als der Renderer, statt des
gemeinsamen Docker-Netzes das private Hetzner-Netz (Cloud Network) nutzen und `expose` durch
`ports: ["<private-IP>:8080:8080"]` ersetzen – nie an die öffentliche IP binden; zusätzlich die Hetzner-Firewall
für Port 8080 nur aus dem privaten Netz öffnen. In ECOMEX 0 dann `renderer_url` = `http://<private-IP>:8080`.

1. **Ordner anlegen** auf dem n8n-Server, z. B. `/opt/ecomex-renderer`, und dort ablegen:
   `docker-compose.yml` und `.env.example` aus dem Repo-Ordner `renderer/`.
2. **Netz von n8n ermitteln:** `docker network ls` bzw. `docker inspect <n8n-container> --format '{{json .NetworkSettings.Networks}}'`.
3. **`.env` anlegen** (aus `.env.example`):
   ```
   RENDERER_API_KEY=<Ergebnis von: openssl rand -hex 24>
   N8N_NETZ=<Netzname aus Schritt 2>
   ```
4. **Anmelden bei GitHub Packages** (nur nötig, solange das Image privat ist): Token mit Recht
   `read:packages` von ecomex erhalten, dann
   `echo <TOKEN> | docker login ghcr.io -u <github-benutzer> --password-stdin`.
5. **Starten:** `docker compose pull && docker compose up -d`
6. **Selbsttest:** `docker exec ecomex-renderer python tools/selbsttest.py`
   → erwartet: alle Zeilen `OK`, am Ende „ALLES IN ORDNUNG – der Renderer ist bereit für n8n.“
7. **Aus n8n erreichbar?** `docker exec <n8n-container> wget -qO- http://ecomex-renderer:8080/health`
   → `{"status":"ok", …, "demo_master":false}`
8. **API-Key übergeben** an die n8n-Verantwortlichen (sicherer Kanal, nicht per E-Mail im Klartext).

## In n8n (ECOMEX-Team)

1. Credential **Header Auth „ECOMEX Renderer“**: Name `X-API-Key`, Wert = `RENDERER_API_KEY`.
2. ECOMEX 0 › *Edit Fields* › `renderer_url` = `http://ecomex-renderer:8080` (Standard – nur ändern, wenn der
   Container anders heißt oder außerhalb des n8n-Netzes läuft).
3. **ECOMEX 11 | Systemcheck** ausführen → Zeile *Renderer* muss ✔ zeigen. Ab jetzt nutzen alle Workflows
   automatisch den Renderer.

## Betrieb

| Aufgabe | Befehl |
|---|---|
| Update (neue Renderer-Version oder neuer Master) | `docker compose pull && docker compose up -d` |
| Status | `docker ps --filter name=ecomex-renderer` (Spalte STATUS zeigt `healthy`) |
| Protokoll | `docker logs --tail 100 ecomex-renderer` |
| Stoppen | `docker compose down` – die Workflows laufen dann automatisch ohne Renderer weiter |
| Bestimmte Version festhalten | in `.env`: `RENDERER_VERSION=sha-<7 Zeichen>` (Tags siehe GitHub › Packages) |

## Sicherheit

- Port 8080 nur im Docker-Netz (`expose`, kein `ports`). Jede Anfrage außer `/health` verlangt den API-Key.
- Der Container läuft ohne Root-Rechte, speichert nichts und braucht keinen Internetzugang.
- Das Image enthält den ECOMEX-Folienmaster. Ist das Repository privat, bleibt auch das Image privat.

## Alternative: Azure Container Apps

Wenn der Renderer nicht neben n8n laufen kann: in Azure (Region West Europe) eine Container App aus dem
Image `ghcr.io/ecomewb/ecomex-renderer:latest` anlegen, Port 8080, Umgebungsvariable `RENDERER_API_KEY`,
Ingress *extern* (HTTPS), 1 vCPU / 2 GiB, min. 0–1 Replikat. In ECOMEX 0 dann `renderer_url` =
`https://<app-name>.<region>.azurecontainerapps.io`. Der API-Key schützt den Dienst; trotzdem sollte die
App nur aus dem Netz des n8n-Servers erreichbar sein (IP-Einschränkung im Ingress).

## E-Mail-Vorlage an die IT

> Betreff: Kleiner interner Docker-Dienst neben n8n (ECOMEX Folien-Renderer)
>
> Hallo,
> für die Content Factory in n8n brauchen wir einen kleinen internen Docker-Dienst neben dem n8n-Container:
> das Image `ghcr.io/ecomewb/ecomex-renderer:latest` (1 vCPU, ca. 1–1,5 GB RAM, kein öffentlicher Port,
> gleiches Docker-Netz wie n8n). Die Anleitung mit allen Befehlen und einem Selbsttest liegt im Repo unter
> `docs/05_Renderer_einrichten.md`; die Compose-Datei unter `renderer/docker-compose.yml`.
> Den Zugang zu GitHub Packages und den API-Key stimmen wir separat ab.
> Könnt ihr uns sagen, wann das möglich ist? Danke!
