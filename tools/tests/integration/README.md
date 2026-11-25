# Integrationstests (optional, für Entwickler)

Führt **alle 12 ECOMEX-Workflows mit der echten n8n-Engine 2.46** aus – ohne laufendes n8n.
GitHub, Supabase, Anthropic und Azure werden simuliert (nock), der Renderer läuft lokal, KI-Antworten sind vorgegeben.
Geprüft werden Abläufe, Verzweigungen, Datei-Weitergabe, Fehlerwege und Formular-Meldungen (60 Fälle).

```bash
# 1. Renderer lokal starten (eigenes Terminal)
cd renderer && pip install -r requirements.txt
RENDERER_API_KEY=testkey MASTER_PATH=../design/ECOMEX_Masterlayout_6.2.pptx python3 -m uvicorn app.main:app --port 8099

# 2. Testdateien erzeugen und Tests starten
cd tools/tests/integration
python3 vorbereiten.py
npm install --ignore-scripts
node it_all.js
```
