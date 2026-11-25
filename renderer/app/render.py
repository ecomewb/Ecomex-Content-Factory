"""Deck-JSON -> PPTX im Originalmaster (+ Prüfbericht)."""
from __future__ import annotations

import io
import json
import os
import subprocess
import tempfile
import uuid
from collections import Counter
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.util import Pt

from .layouts import RENDERERS, MUTED, PRIMARY, DARK
from .pptxkit import FOOTER_TYPES, Canvas, MasterInfo, clone_title_text, read_theme, remove_placeholder, E, inch
from .textfit import Measurer, _font_file

APP_DIR = Path(__file__).parent
CATALOG_PATH = Path(os.getenv("CATALOG_PATH", APP_DIR / "catalog.json"))
CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
LAYOUT_IDS = {l["id"]: l for l in CATALOG["layouts"]}


class Ctx:
    def __init__(self, measurer, theme, master, brand):
        self.measurer = measurer
        self.theme = theme
        self.master = master
        self.brand = brand
        self.warnings = []

    def warn(self, slide_no, art, text):
        self.warnings.append({"folie": slide_no, "art": art, "text": text})


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _clear_slides(prs):
    lst = prs.slides._sldIdLst
    for sid in list(lst):
        prs.part.drop_rel(sid.rId)
        lst.remove(sid)


def _validate(folie, no, ctx):
    lid = folie.get("layout")
    felder = folie.get("felder") or {}
    if lid not in LAYOUT_IDS:
        ctx.warn(no, "layout_unbekannt", f"Layout '{lid}' existiert nicht – als 'stichpunkte' gesetzt.")
        punkte = []
        for v in felder.values():
            punkte += v if isinstance(v, list) else [v]
        return "stichpunkte", {"titel": folie.get("titel") or felder.get("titel") or "", "punkte": [str(p) for p in punkte if p and not isinstance(p, dict)]}
    spec = LAYOUT_IDS[lid]["felder"]
    if folie.get("titel") and not felder.get("titel"):
        felder["titel"] = folie["titel"]
    for name, fs in spec.items():
        val = felder.get(name)
        if fs.get("pflicht") and (val in (None, "", [], {})):
            ctx.warn(no, "pflichtfeld", f"Pflichtfeld '{name}' fehlt ({lid}).")
        if val is None:
            continue
        mx = fs.get("max")
        if fs.get("typ", "text") == "text" and mx and isinstance(val, str) and len(val) > mx * 1.15:
            ctx.warn(no, "zeichenlimit", f"'{name}' hat {len(val)} statt max. {mx} Zeichen.")
        if isinstance(val, list):
            me = fs.get("max_eintraege")
            if me and len(val) > me:
                ctx.warn(no, "zu_viele_eintraege", f"'{name}': {len(val)} Einträge, max. {me}. Überzählige werden nicht dargestellt: "
                         + "; ".join(str(v)[:60] for v in val[me:]))
                felder[name] = val[:me]
            if mx and fs.get("typ") == "liste":
                for v in val:
                    if isinstance(v, str) and len(v) > mx * 1.15:
                        ctx.warn(no, "zeichenlimit", f"Eintrag in '{name}' hat {len(v)} statt max. {mx} Zeichen.")
    return lid, felder


def _notes_text(folie, meta):
    parts = []
    if folie.get("notizen"):
        parts.append(str(folie["notizen"]).strip())
    info = []
    if folie.get("block"):
        info.append(f"Block: {folie['block']}")
    if folie.get("dauer_min"):
        info.append(f"Zeit: {folie['dauer_min']} Min.")
    if info:
        parts.append(" | ".join(info))
    q = [str(x) for x in (folie.get("quellen") or []) if x]
    if q:
        parts.append("QUELLEN\n" + "\n".join(f"- {x}" for x in q))
    r = [str(x) for x in (folie.get("review_hinweise") or []) if x]
    if r:
        parts.append("OFFEN / BITTE PRÜFEN\n" + "\n".join(f"- {x}" for x in r))
    return "\n\n".join(parts)


def _content_box(li, master: MasterInfo):
    sw, sh = master.slide_w, master.slide_h
    tb = li.title_box or (0.6, 0.35, sw - 1.2, 1.0)
    x = max(0.45, tb[0])
    right = min(sw - 0.45, tb[0] + tb[2])
    y0 = tb[1] + tb[3] + 0.22
    y1 = min(master.footer_top, sh - 0.5) - 0.12
    if y1 - y0 < 3.2:
        y0, y1 = min(y0, sh * 0.25), sh - 0.55
    return (x, y0, right - x, y1 - y0)


def _footer(cv, master, meta, folie, brand):
    """Fußzeile links (Modul · Tag · Block) + ENTWURF-Kennzeichnung mittig.
    Die Kennzeichnung heißt 'ECOMEX_ENTWURF' und wird von POST /finalisieren entfernt."""
    if not brand.get("fusszeile", True):
        return
    y = master.slide_h - brand.get("fusszeile_abstand_unten", 0.42)
    kurz = " · ".join(str(v) for v in [meta.get("modul"), meta.get("tag"), folie.get("block")] if v)
    if kurz:
        box = cv.text(brand.get("fusszeile_x", 0.5), y, 4.5, 0.3, kurz, [9], color=("dk1", 0.5), label="Fußzeile",
                      check=False)
        if box is not None:
            box.name = "ECOMEX_FUSSZEILE"
    if meta.get("entwurf", True) and brand.get("entwurf_label", True):
        box = cv.text(master.slide_w / 2 - 1.75, y, 3.5, 0.3, brand.get("entwurf_text", "ENTWURF – nicht freigegeben"),
                      [9], color="accent5", bold=True, align="center", label="Entwurf", check=False)
        if box is not None:
            box.name = "ECOMEX_ENTWURF"


def _title_slide(slide, li, f, ctx, cv):
    title_ph = None
    bodies = []
    for ph in list(slide.placeholders):
        t = ph.placeholder_format.type
        if t in (PP_PLACEHOLDER.CENTER_TITLE, PP_PLACEHOLDER.TITLE) and title_ph is None:
            title_ph = ph
        elif t in (PP_PLACEHOLDER.SUBTITLE, PP_PLACEHOLDER.BODY):
            bodies.append(ph)
        elif t not in FOOTER_TYPES:
            remove_placeholder(ph)
    # größter Textplatzhalter = Untertitel, nächster = Modul/Tag (z. B. ECOMEX-Cover: „Dozent/in“ und „Tag 1“)
    bodies.sort(key=lambda p: -(inch(p.width) * inch(p.height)))
    titel = str(f.get("titel") or "")
    if title_ph is not None:
        clone_title_text(title_ph, titel, max(ctx.theme.title_size + 8, 36), lambda a, t: ctx.warn(cv.no, a, t),
                         ctx.measurer, min_size=24)
    texte = [str(v) for v in [f.get("untertitel"), f.get("meta")] if v]
    # kleiner zweiter Platzhalter (z. B. „Tag 1“) nur für kurze Angaben, sonst beides in den großen
    if len(bodies) >= 2 and len(texte) == 2 and not ctx.measurer.fits([texte[1]], max(0.5, inch(bodies[1].width) - 0.2) * 72,
                                                                        max(0.3, inch(bodies[1].height)) * 72, 14):
        texte = ["\n".join(texte)]
    if len(bodies) >= 2 and len(texte) == 2:
        bodies[0].text_frame.text, bodies[1].text_frame.text = texte[0], texte[1]
        used = 2
    elif bodies and texte:
        bodies[0].text_frame.text = "\n".join(texte)
        used = 1
    else:
        used = 0
        if texte:
            m = ctx.master
            cv.text(0.8, m.slide_h * 0.62, m.slide_w - 1.6, 1.2, texte, [22, 20, 18], color=MUTED, label="Untertitel")
    for ph in bodies[used:]:
        remove_placeholder(ph)


def _kapitel(slide, li, f, ctx, cv, box):
    titel = str(f.get("titel") or "")
    nummer = str(f.get("nummer") or "").strip()
    leit, dauer = str(f.get("leitfrage") or ""), str(f.get("dauer") or "")
    if li.kind == "section":
        title_ph = None
        bodies = []
        for ph in list(slide.placeholders):
            t = ph.placeholder_format.type
            if t in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE) and title_ph is None:
                title_ph = ph
            elif t in (PP_PLACEHOLDER.BODY, PP_PLACEHOLDER.OBJECT, PP_PLACEHOLDER.SUBTITLE):
                bodies.append(ph)
            elif t == PP_PLACEHOLDER.PICTURE:
                continue  # leerer Bildplatzhalter bleibt: unsichtbar in der Präsentation, Dozierende können ein Foto einsetzen
            elif t not in FOOTER_TYPES:
                remove_placeholder(ph)
        # Layouts ohne Titel-Platzhalter (z. B. „Kapitelbalken“): oberster Textplatzhalter trägt den Titel
        bodies.sort(key=lambda p: inch(p.top))
        if title_ph is None and bodies:
            title_ph = bodies.pop(0)
        body_ph = bodies.pop(0) if bodies else None
        for ph in bodies:
            remove_placeholder(ph)
        if title_ph is not None:
            clone_title_text(title_ph, (f"{nummer}  " if nummer else "") + titel, ctx.theme.title_size + 4,
                             lambda a, t: ctx.warn(cv.no, a, t), ctx.measurer)
        body = "\n".join(v for v in [leit, (f"Dauer: {dauer}" if dauer else "")] if v)
        if body_ph is not None:
            if body:
                body_ph.text_frame.text = body
            else:
                remove_placeholder(body_ph)
        return
    # eigenes Kapitel-Design auf einem Titel-/Leer-Layout
    for ph in list(slide.placeholders):
        if ph.placeholder_format.type not in FOOTER_TYPES:
            remove_placeholder(ph)
    m = ctx.master
    x, w = 0.9, m.slide_w - 1.8
    cv.rect(0, 0, 0.28, m.slide_h, fill=PRIMARY, radius=None)
    if nummer:
        cv.text(x, m.slide_h * 0.14, 4, 2.0, nummer, [110, 96], color=("accent1", 0.7), bold=True, label="Kapitelnummer")
    cv.text(x, m.slide_h * 0.40, w, 1.6, titel, [44, 40, 36, 32, 28], color=DARK, bold=True, anchor="bottom",
            label="Kapiteltitel")
    if leit:
        cv.text(x, m.slide_h * 0.40 + 1.75, w * 0.8, 1.2, leit, [24, 22, 20, 18], color=MUTED, label="Leitfrage")
    if dauer:
        from .layouts import badge
        badge(cv, x, m.slide_h * 0.40 + 3.05, dauer.upper(), color=PRIMARY)


def render_deck(deck: dict, master_path: Path, brand: dict | None = None, master_map: dict | None = None):
    brand = brand or {}
    prs = Presentation(str(master_path))
    _clear_slides(prs)
    theme = read_theme(prs)
    master = MasterInfo(prs, master_map)
    measurer = Measurer(theme.minor_font)
    ctx = Ctx(measurer, theme, master, brand)
    meta = deck.get("meta") or {}
    folien = deck.get("folien") or []
    used = []
    for i, folie in enumerate(folien, start=1):
        lid, f = _validate(dict(folie), i, ctx)
        used.append(lid)
        li = master.pick(lid)
        slide = prs.slides.add_slide(li.layout)
        cv = Canvas(slide, ctx, i)
        box = _content_box(li, master)
        if lid == "titel":
            _title_slide(slide, li, f, ctx, cv)
        elif lid == "kapitel":
            _kapitel(slide, li, f, ctx, cv, box)
        else:
            title_ph = None
            for ph in list(slide.placeholders):
                t = ph.placeholder_format.type
                if t in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE) and title_ph is None:
                    title_ph = ph
                elif t not in FOOTER_TYPES:
                    remove_placeholder(ph)
            titel = str(f.get("titel") or "")
            if title_ph is not None:
                clone_title_text(title_ph, titel, ctx.theme.title_size, lambda a, t: ctx.warn(i, a, t), measurer)
            elif titel:
                cv.text(0.6, 0.4, master.slide_w - 1.2, 1.0, titel, [28, 26, 24, 22], color=DARK, bold=True,
                        label="Titel")
            try:
                RENDERERS[lid](cv, f, box)
            except Exception as e:  # nie stillschweigend: Folie bleibt erhalten, Fehler im Bericht
                ctx.warn(i, "renderfehler", f"{lid}: {e}")
        notes = _notes_text(folie, meta)
        if notes:
            slide.notes_slide.notes_text_frame.text = notes
        elif lid not in ("titel", "tagesablauf", "pause", "kapitel"):
            ctx.warn(i, "notizen_fehlen", "Keine Sprechernotizen.")
        if lid != "titel":
            _footer(cv, master, meta, folie, brand)
    # deterministische Struktur- und Designprüfung
    for j in range(2, len(used)):
        if used[j] == used[j - 1] == used[j - 2] and used[j] not in ("material", "loesung"):
            ctx.warn(j + 1, "monotonie", f"Drei Folien hintereinander im Layout '{used[j]}' – visuell abwechseln.")
    for j, lid in enumerate(used):
        if lid == "uebung" and "loesung" not in used[j + 1:j + 5]:
            ctx.warn(j + 1, "didaktik", "Übung ohne nachfolgende Musterlösung (innerhalb von 4 Folien).")
    font_file = _font_file(theme.minor_font, False, False) or ""
    report = {
        "folien": len(folien),
        "master_layouts_genutzt": Counter(master.pick(l).name for l in used),
        "katalog_layouts": Counter(used),
        "theme": {"farben": theme.colors, "schrift_titel": theme.major_font, "schrift_text": theme.minor_font},
        "schrift_vermessung": os.path.basename(font_file),
        "warnungen": ctx.warnings,
        "warnungen_anzahl": len(ctx.warnings),
        "kritisch": sum(1 for w in ctx.warnings if w["art"] in ("textueberlauf", "titel_zu_lang", "renderfehler",
                                                               "layout_unbekannt", "pflichtfeld")),
    }
    if theme.minor_font.lower().replace(" ", "") not in os.path.basename(font_file).lower().replace(" ", "").replace("-", ""):
        report["hinweis_schrift"] = (f"Schrift '{theme.minor_font}' ist im Renderer nicht installiert – Vermessung mit "
                                     f"'{os.path.basename(font_file)}'. Für exakte Passung TTF in fonts/ ablegen.")
    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue(), report


def to_pdf(pptx_bytes: bytes, timeout=240) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "deck.pptx"
        src.write_bytes(pptx_bytes)
        profile = Path(td) / f"lo_{uuid.uuid4().hex}"
        cmd = ["soffice", f"-env:UserInstallation=file://{profile}", "--headless", "--norestore",
               "--convert-to", "pdf", "--outdir", td, str(src)]
        subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
        out = Path(td) / "deck.pdf"
        if not out.exists():
            raise RuntimeError("PDF-Konvertierung fehlgeschlagen (LibreOffice).")
        return out.read_bytes()


def finalize(pptx_bytes: bytes, version: str = "", pruefer: str = "") -> tuple[bytes, int]:
    """Entfernt alle ENTWURF-Kennzeichnungen und vermerkt Version/Prüfer in den Dateieigenschaften."""
    prs = Presentation(io.BytesIO(pptx_bytes))
    removed = 0
    for slide in prs.slides:
        for shp in list(slide.shapes):
            if shp.name == "ECOMEX_ENTWURF":
                shp._element.getparent().remove(shp._element)
                removed += 1
    cp = prs.core_properties
    if version:
        cp.version = str(version)[:60]
    if pruefer:
        cp.last_modified_by = str(pruefer)[:60]
        cp.comments = f"Freigegeben von {pruefer}" + (f", Version {version}" if version else "")
    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue(), removed
