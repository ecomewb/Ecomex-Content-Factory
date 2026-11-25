"""ECOMEX Folien-Renderer – kleiner HTTP-Dienst für n8n.

Endpunkte
  GET  /health                      Status, aktiver Master
  GET  /katalog                     Layoutkatalog (für die Agenten) + Master-Layouts
  POST /render?format=pptx|pdf|report   Deck-JSON -> PowerPoint / PDF-Vorschau / Prüfbericht
  POST /extract                     Datei (multipart, Feld 'file') -> Text mit Fundstellen
  POST /inspect                     Master-Layouts und automatische Zuordnung anzeigen
  POST /finalisieren                Freigegebene PPTX: ENTWURF-Kennzeichnung entfernen
Schutz: Header 'X-API-Key' (Umgebungsvariable RENDERER_API_KEY).
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from fastapi import Body, Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse, Response
from pptx import Presentation

from .extract import extract
from .pptxkit import MasterInfo
from .render import CATALOG, finalize, load_json, render_deck, to_pdf

APP_DIR = Path(__file__).parent
BASE = APP_DIR.parent
MASTER_PATH = Path(os.getenv("MASTER_PATH", BASE / "masters" / "ecomex_master.pptx"))
DEMO_MASTER = BASE / "masters" / "demo_master.pptx"
CONFIG_DIR = Path(os.getenv("CONFIG_DIR", BASE / "config"))
API_KEY = os.getenv("RENDERER_API_KEY", "")
EXTRACT_MAX_MB = int(os.getenv("EXTRACT_MAX_MB", "150"))
PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

app = FastAPI(title="ECOMEX Folien-Renderer", version="1.1.0")


def auth(x_api_key: str | None = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="X-API-Key fehlt oder ist falsch.")


def master():
    if MASTER_PATH.exists():
        return MASTER_PATH, False
    return DEMO_MASTER, True


def config():
    return load_json(CONFIG_DIR / "brand.json", {}), load_json(CONFIG_DIR / "master_map.json", {})


def safe_name(name: str, ext: str) -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", name or "ECOMEX_Deck").strip("_") or "ECOMEX_Deck"
    return base[:120] + "." + ext


@app.get("/health")
def health():
    m, demo = master()
    return {"status": "ok", "master": m.name, "demo_master": demo, "katalog_version": CATALOG["version"],
            "extract_max_mb": EXTRACT_MAX_MB, "version": app.version}


@app.get("/katalog", dependencies=[Depends(auth)])
def katalog():
    m, demo = master()
    mi = MasterInfo(Presentation(str(m)), config()[1])
    return {**CATALOG, "master": m.name, "demo_master": demo, "master_layouts": [l.name for l in mi.layouts]}


@app.post("/render", dependencies=[Depends(auth)])
def render(deck: dict = Body(...), format: str = Query("pptx", pattern="^(pptx|pdf|report)$")):
    if "deck" in deck and isinstance(deck["deck"], (dict, str)):
        deck = deck["deck"]
    if isinstance(deck, str):
        deck = json.loads(deck)
    if not isinstance(deck.get("folien"), list) or not deck["folien"]:
        raise HTTPException(status_code=422, detail="Deck enthält keine 'folien'.")
    m, demo = master()
    brand, mmap = config()
    pptx_bytes, report = render_deck(deck, m, brand, mmap)
    report["demo_master"] = demo
    meta = deck.get("meta") or {}
    name = meta.get("dateiname") or f"ECOMEX_{meta.get('modul', '')}_{meta.get('tag', '')}_ENTWURF"
    if format == "report":
        return JSONResponse(report)
    if format == "pdf":
        fn = safe_name(name, "pdf")
        return Response(to_pdf(pptx_bytes), media_type="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="{fn}"'})
    fn = safe_name(name, "pptx")
    return Response(pptx_bytes, media_type=PPTX_MIME, headers={"Content-Disposition": f'attachment; filename="{fn}"',
                                                               "X-Render-Warnings": str(report["warnungen_anzahl"])})


@app.post("/extract", dependencies=[Depends(auth)])
async def extract_file(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > EXTRACT_MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Datei größer als {EXTRACT_MAX_MB} MB. Bitte als PDF exportieren oder EXTRACT_MAX_MB erhöhen.")
    try:
        return extract(file.filename or "datei", data)
    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))


@app.post("/inspect", dependencies=[Depends(auth)])
async def inspect(file: UploadFile | None = File(default=None)):
    import io
    if file is not None:
        prs = Presentation(io.BytesIO(await file.read()))
        name = file.filename
    else:
        m, _ = master()
        prs, name = Presentation(str(m)), m.name
    mi = MasterInfo(prs, config()[1])
    mapping = {l["id"]: mi.pick(l["id"]).name for l in CATALOG["layouts"]}
    return {"master": name, "folienformat_zoll": [round(mi.slide_w, 2), round(mi.slide_h, 2)],
            "layouts": mi.describe(), "zuordnung_katalog_zu_master": mapping,
            "hinweis": "Zuordnung bei Bedarf in config/master_map.json übersteuern, z. B. {\"default\": \"Nur Titel\", \"kapitel\": \"Kapitel\"}."}


@app.post("/finalisieren", dependencies=[Depends(auth)])
async def finalisieren(file: UploadFile = File(...), version: str = Query(""), pruefer: str = Query("")):
    data = await file.read()
    out, removed = finalize(data, version, pruefer)
    base = re.sub(r"_?ENTWURF", "", (file.filename or "ECOMEX_Deck.pptx").rsplit(".", 1)[0])
    fn = safe_name(f"{base}_{version}_FREIGEGEBEN" if version else f"{base}_FREIGEGEBEN", "pptx")
    return Response(out, media_type=PPTX_MIME, headers={"Content-Disposition": f'attachment; filename="{fn}"',
                                                        "X-Entwurf-Entfernt": str(removed)})
