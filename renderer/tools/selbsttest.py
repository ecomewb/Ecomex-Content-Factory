"""Selbsttest des ECOMEX-Renderers – läuft im Container oder gegen eine URL.

Im Container (nach dem Start):     docker exec ecomex-renderer python tools/selbsttest.py
Gegen eine URL:                    python tools/selbsttest.py --url https://renderer.example --key <API-Key>
Ergebnisdateien zusätzlich ablegen: --ausgabe /tmp/selbsttest

Prüft: /health (Originalmaster geladen?), /katalog, /render (Prüfbericht, PPTX, PDF), /extract, /finalisieren.
Exit-Code 0 = alles in Ordnung.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
BEISPIEL = HIER / "tests" / "sample_deck.json"


def anfrage(url, key, methode="GET", daten=None, typ=None, timeout=300):
    kopf = {"X-API-Key": key} if key else {}
    if typ:
        kopf["Content-Type"] = typ
    req = urllib.request.Request(url, data=daten, method=methode, headers=kopf)
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers), time.time() - start
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers), time.time() - start


def multipart(feld, dateiname, inhalt, mime):
    grenze = uuid.uuid4().hex
    teile = (f"--{grenze}\r\nContent-Disposition: form-data; name=\"{feld}\"; filename=\"{dateiname}\"\r\n"
             f"Content-Type: {mime}\r\n\r\n").encode() + inhalt + f"\r\n--{grenze}--\r\n".encode()
    return teile, f"multipart/form-data; boundary={grenze}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8080")
    ap.add_argument("--key", default=os.getenv("RENDERER_API_KEY", ""))
    ap.add_argument("--ausgabe", default="")
    ap.add_argument("--demo-erlaubt", action="store_true", help="Demo-Master nicht als Fehler werten")
    a = ap.parse_args()
    url = a.url.rstrip("/")
    aus = Path(a.ausgabe) if a.ausgabe else None
    if aus:
        aus.mkdir(parents=True, exist_ok=True)
    ergebnisse = []

    def pruefe(name, ok, detail):
        ergebnisse.append((name, ok, detail))
        print(f"{'OK  ' if ok else 'FEHLER'}  {name:<28} {detail}", flush=True)

    # 1. Health (ohne Key) – wartet bis zu 60 s auf den Start
    h = None
    for _ in range(30):
        try:
            s, b, _, _ = anfrage(url + "/health", None, timeout=10)
            if s == 200:
                h = json.loads(b)
                break
        except Exception:
            pass
        time.sleep(2)
    if not h:
        pruefe("Erreichbar (/health)", False, f"keine Antwort von {url}")
        return 1
    master_ok = not h.get("demo_master") or a.demo_erlaubt
    pruefe("Erreichbar (/health)", h.get("status") == "ok", f"Version {h.get('version')}, Katalog v{h.get('katalog_version')}")
    pruefe("Originalmaster geladen", master_ok,
           f"{h.get('master')}" + (" – DEMO-Master! ECOMEX-Master fehlt im Container" if h.get("demo_master") else ""))

    # 2. API-Key wirkt
    s, _, _, _ = anfrage(url + "/katalog", "falscher-schluessel")
    pruefe("API-Key wird verlangt", s == 401 or not a.key, "401 bei falschem Key" if s == 401 else f"HTTP {s} – RENDERER_API_KEY gesetzt?")
    s, b, _, _ = anfrage(url + "/katalog", a.key)
    kat = json.loads(b) if s == 200 else {}
    pruefe("Layoutkatalog (/katalog)", s == 200 and len(kat.get("layouts", [])) >= 10,
           f"{len(kat.get('layouts', []))} Layouts, {len(kat.get('master_layouts', []))} Master-Layouts")

    # 3. Rendern
    deck = BEISPIEL.read_bytes()
    s, b, _, t = anfrage(url + "/render?format=report", a.key, "POST", deck, "application/json")
    rep = json.loads(b) if s == 200 else {}
    pruefe("Prüfbericht (/render report)", s == 200 and rep.get("folien", 0) > 0,
           f"{rep.get('folien')} Folien, {rep.get('warnungen_anzahl')} Hinweise ({rep.get('kritisch')} kritisch), {t:.1f} s")
    s, pptx, _, t = anfrage(url + "/render?format=pptx", a.key, "POST", deck, "application/json")
    pruefe("PowerPoint (/render pptx)", s == 200 and pptx[:2] == b"PK", f"{len(pptx) // 1024} KB, {t:.1f} s")
    s, pdf, _, t = anfrage(url + "/render?format=pdf", a.key, "POST", deck, "application/json", timeout=600)
    pruefe("PDF-Vorschau (/render pdf)", s == 200 and pdf[:4] == b"%PDF", f"{len(pdf) // 1024} KB, {t:.1f} s (LibreOffice)")

    # 4. Text lesen
    if pptx[:2] == b"PK":
        body, typ = multipart("file", "selbsttest.pptx", pptx,
                              "application/vnd.openxmlformats-officedocument.presentationml.presentation")
        s, b, _, t = anfrage(url + "/extract", a.key, "POST", body, typ)
        ex = json.loads(b) if s == 200 else {}
        pruefe("Text lesen (/extract)", s == 200 and len(ex.get("abschnitte", [])) > 0,
               f"{len(ex.get('abschnitte', []))} Folien mit Text, {t:.1f} s")
        s, fin, kopf, _ = anfrage(url + "/finalisieren?version=v0_test&pruefer=Selbsttest", a.key, "POST",
                                  *multipart("file", "selbsttest_ENTWURF.pptx", pptx,
                                             "application/vnd.openxmlformats-officedocument.presentationml.presentation"))
        entfernt = {k.lower(): v for k, v in kopf.items()}.get("x-entwurf-entfernt", "?")
        pruefe("Freigabe (/finalisieren)", s == 200 and fin[:2] == b"PK", f"{entfernt} ENTWURF-Kennzeichnungen entfernt")
        if aus:
            (aus / "selbsttest.pptx").write_bytes(pptx)
            (aus / "selbsttest_FREIGEGEBEN.pptx").write_bytes(fin)
    if aus:
        if pdf[:4] == b"%PDF":
            (aus / "selbsttest.pdf").write_bytes(pdf)
        (aus / "pruefbericht.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")

    fehler = [n for n, ok, _ in ergebnisse if not ok]
    print("\n" + ("ALLES IN ORDNUNG – der Renderer ist bereit für n8n." if not fehler
                  else "NICHT BEREIT: " + ", ".join(fehler)))
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
