"""Erzeugt die Testdateien für die Integrationstests (fixtures/). Der Renderer muss laufen:
   cd renderer && RENDERER_API_KEY=testkey MASTER_PATH=../design/ECOMEX_Masterlayout_6.2.pptx uvicorn app.main:app --port 8099"""
import json, os, urllib.request
from pathlib import Path
from openpyxl import Workbook
from PIL import Image, ImageDraw

HIER = Path(__file__).parent
F = HIER / "fixtures"; F.mkdir(exist_ok=True)
URL = os.getenv("RENDERER_TEST_URL", "http://127.0.0.1:8099")
deck = (HIER / "../../../renderer/tests/sample_deck.json").resolve().read_bytes()
for fmt in ("pptx", "pdf"):
    req = urllib.request.Request(f"{URL}/render?format={fmt}", data=deck, method="POST",
                                 headers={"X-API-Key": "testkey", "Content-Type": "application/json"})
    (F / f"deck.{fmt}").write_bytes(urllib.request.urlopen(req, timeout=300).read())
wb = Workbook(); ws = wb.active
ws.append(["Tag", "Block", "Von", "Bis", "Titel", "Art", "Lernziele", "Folien", "Status"])
for i in range(1, 31):
    ws.append(["Tag 12", i, "09:00", "09:30", f"Titel {i}", "input", "Die TN können X", 5, "Freigegeben" if i < 4 else "Entwurf"])
wb.save(F / "tabelle.xlsx")
img = Image.new("RGB", (800, 600), "white"); ImageDraw.Draw(img).text((50, 50), "GESCANNT", fill="black"); img.save(F / "scan.pdf", "PDF")
(F / "notizen.md").write_text("# Einleitung\nDas ist ein Test.\n\n## Teil 2\nNoch mehr Text für die Wissensbasis.\n", encoding="utf-8")
print("Testdateien:", ", ".join(sorted(p.name for p in F.iterdir())))
