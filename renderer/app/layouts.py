"""Darstellung der Katalog-Layouts als native PowerPoint-Objekte.

Jede Funktion erhält: Canvas, Felder der Folie, Inhaltsbereich (x, y, w, h) in Zoll.
Gestaltungsprinzipien: weißer Grund, ruhige Flächen in Akzent-Tönungen, klare Hierarchie,
große Lesegrößen, keine Dekoration ohne Funktion.
"""
from __future__ import annotations

from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Pt

from .pptxkit import E

PRIMARY = "accent1"
SECOND = "accent2"
THIRD = "accent3"
OK = "accent6"
DARK = "dk2"
TEXT = "dk1"
MUTED = ("dk1", 0.4)
PANEL = ("accent1", 0.9)
PANEL2 = ("dk2", 0.93)

BODY = [22, 20, 18, 17, 16, 15, 14, 13]
BODY_S = [18, 17, 16, 15, 14, 13, 12, 11]
HEAD = [22, 20, 19, 18, 17, 16, 15, 14]


def _list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [x for x in v if x not in (None, "")]
    return [v]


def _s(v):
    return "" if v is None else str(v).strip()


def badge(cv, x, y, text, color=SECOND, txt="lt1", h=0.32):
    w = cv.m.width(text, 11, bold=True) / 72 + 0.34
    shp = cv.rect(x, y, w, h, fill=color, radius=0.5)
    cv.text(0, 0, w, h, text, [11], color=txt, bold=True, align="center", anchor="middle", shape=shp, label="Badge")
    return w


def number_dot(cv, x, y, d, label, fill=PRIMARY, txt="lt1", size=None):
    shp = cv.shape(MSO_SHAPE.OVAL, x, y, d, d, fill=fill)
    cv.text(0, 0, d, d, str(label), [size or max(10, round(d * 26))], color=txt, bold=True, align="center",
            anchor="middle", shape=shp, label="Nummer")
    return shp


def bar_note(cv, x, y, w, h, label, text, fill=PANEL, accent=PRIMARY):
    cv.rect(x, y, w, h, fill=fill, radius=0.12)
    cv.rect(x, y, 0.09, h, fill=accent, radius=None)
    lw = 0
    if label:
        lw = cv.m.width(label, 14, bold=True) / 72 + 0.35
        cv.text(x + 0.2, y, lw, h, label, [14], color=accent, bold=True, anchor="middle", label=label)
    cv.text(x + 0.2 + lw, y, w - 0.35 - lw, h, text, [18, 17, 16, 15, 14, 13], color=DARK, bold=True,
            anchor="middle", label=f"{label or 'Hinweis'}")


# ------------------------------------------------------------------ Layouts

def stichpunkte(cv, f, box):
    x, y, w, h = box
    punkte, fazit = _list(f.get("punkte")), _s(f.get("fazit"))
    bh = h - (0.95 if fazit else 0)
    tw = min(w, 11.2)
    cv.text(x, y + 0.1, tw, bh - 0.1, punkte, BODY + [12], bullets=PRIMARY, lead_bold=True, space=0.6,
            label="Stichpunkte")
    if fazit:
        bar_note(cv, x, y + h - 0.8, w, 0.8, "Fazit", fazit)


def lernziele(cv, f, box):
    x, y, w, h = box
    ziele = _list(f.get("ziele"))[:5]
    n = max(1, len(ziele))
    row = min(1.05, h / n)
    d = min(0.52, row * 0.7)
    # gemeinsame Schriftgröße für alle Zeilen
    size = cv.group_size(ziele, min(w, 11.5) - d - 0.25, row, BODY, label="Lernziele")
    top = y + max(0, (h - row * n) / 2) * 0.4
    for i, z in enumerate(ziele):
        ry = top + i * row
        number_dot(cv, x, ry + (row - d) / 2, d, i + 1)
        cv.text(x + d + 0.25, ry, min(w, 11.5) - d - 0.25, row, z, [size], color=TEXT, anchor="middle",
                lead_bold=True, label=f"Lernziel {i + 1}", check=False)
        if i < n - 1:
            cv.line(x + d + 0.3, ry + row, x + min(w, 11.5), ry + row, color=("dk1", 0.88), width=0.75)


def kernaussage(cv, f, box):
    x, y, w, h = box
    aussage, erl = _s(f.get("aussage")), _s(f.get("erlaeuterung"))
    tw = min(w - 0.5, 10.8)
    ah = h * (0.58 if erl else 0.8)
    cv.rect(x, y + 0.25, 0.12, ah - 0.25, fill=PRIMARY, radius=None)
    cv.text(x + 0.4, y + 0.2, tw, ah - 0.15, aussage, [38, 36, 34, 32, 30, 28, 26, 24], color=DARK, bold=True,
            anchor="middle", line_spacing=0.95, label="Kernaussage")
    if erl:
        cv.text(x + 0.4, y + ah + 0.25, tw, h - ah - 0.3, erl, [22, 20, 19, 18, 17, 16, 15], color=MUTED,
                label="Erläuterung")


def leitfrage(cv, f, box):
    x, y, w, h = box
    frage, kontext = _s(f.get("frage")), _s(f.get("kontext"))
    gw = 2.2
    cv.text(x - 0.1, y, gw, h * 0.85, "?", [220, 200, 180], color=("accent1", 0.75), bold=True, anchor="middle",
            align="center", label="Fragezeichen", check=False)
    tw = min(w - gw - 0.2, 9.6)
    fh = h * (0.6 if kontext else 0.85)
    cv.text(x + gw + 0.1, y + 0.15, tw, fh, frage, [36, 34, 32, 30, 28, 26, 24], color=DARK, bold=True,
            anchor="bottom" if kontext else "middle", line_spacing=0.95, label="Leitfrage")
    if kontext:
        cv.text(x + gw + 0.1, y + fh + 0.3, tw, h - fh - 0.35, kontext, [20, 19, 18, 17, 16, 15], color=MUTED,
                label="Kontext")


def zwei_spalten(cv, f, box):
    x, y, w, h = box
    fazit = _s(f.get("fazit"))
    gap = 0.4
    cw = (w - gap) / 2
    ch = h - (1.0 if fazit else 0)
    cols = [(f.get("links") or {}, PRIMARY), (f.get("rechts") or {}, DARK)]
    pts_all = [_list(c.get("punkte")) for c, _ in cols]
    # einheitliche Größe für beide Spalten
    size = cv.group_size(pts_all, cw - 0.4, ch - 0.95, [22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12],
                         label="Vergleich", space=0.55, indent=0.28)
    for i, (c, col) in enumerate(cols):
        cx = x + i * (cw + gap)
        cv.rect(cx, y, cw, ch, fill=PANEL if i == 0 else PANEL2, radius=0.05)
        head = cv.rect(cx, y, cw, 0.62, fill=col, radius=0.18)
        cv.text(0, 0, cw, 0.62, _s(c.get("ueberschrift")) or ("Links" if i == 0 else "Rechts"), HEAD, color="lt1",
                bold=True, anchor="middle", align="center", shape=head, label="Spaltenkopf")
        cv.text(cx + 0.2, y + 0.8, cw - 0.4, ch - 0.95, pts_all[i], [size], bullets=col, lead_bold=True, space=0.55,
                label=f"Spalte {i + 1}", check=False)
    if fazit:
        bar_note(cv, x, y + h - 0.82, w, 0.82, "Fazit", fazit)


def karten(cv, f, box):
    x, y, w, h = box
    ks = [k for k in _list(f.get("karten")) if isinstance(k, dict)][:4]
    n = max(1, len(ks))
    grid = n == 4 and any(len(_s(k.get("text"))) > 115 for k in ks) and h > 4.2
    cols, rows = (2, 2) if grid else (n, 1)
    gap = 0.3
    cw = (w - gap * (cols - 1)) / cols
    chh = (h - gap * (rows - 1)) / rows
    if not grid:
        chh = min(chh, 4.6)
    texts = [_s(k.get("text")) for k in ks]
    heads = [_s(k.get("ueberschrift")) for k in ks]
    hsize = cv.group_size(heads, cw - 0.5, 0.85, [22, 20, 19, 18, 17, 16, 15, 14, 13], bold=True,
                          label="Kartenüberschriften")
    hh = (max(cv.m.height([t], hsize, (cw - 0.66) * 72, bold=True) for t in heads) / 72 + 0.12) if heads else 0.5
    size = cv.group_size(texts, cw - 0.5, chh - 0.6 - hh - 0.15, [20, 19, 18, 17, 16, 15, 14, 13, 12, 11],
                         label="Kartentexte")
    for i, k in enumerate(ks):
        r, c = divmod(i, cols)
        cx, cy = x + c * (cw + gap), y + r * (chh + gap)
        cv.rect(cx, cy, cw, chh, fill=PANEL, radius=0.06)
        cv.rect(cx, cy, cw, 0.09, fill=[PRIMARY, SECOND, THIRD, DARK][i % 4], radius=None)
        cv.text(cx + 0.25, cy + 0.25, 1.0, 0.35, f"{i + 1:02d}", [13], color=[PRIMARY, SECOND, THIRD, DARK][i % 4],
                bold=True, label="Kartennummer")
        cv.text(cx + 0.25, cy + 0.55, cw - 0.5, hh, heads[i], [hsize], color=DARK, bold=True, anchor="top",
                label=f"Karte {i + 1} Überschrift", check=False)
        cv.text(cx + 0.25, cy + 0.6 + hh + 0.1, cw - 0.5, chh - 0.6 - hh - 0.15, texts[i], [size], color=TEXT,
                label=f"Karte {i + 1} Text", check=False)


def prozess(cv, f, box):
    x, y, w, h = box
    st = [s for s in _list(f.get("schritte")) if isinstance(s, dict)][:6]
    n = max(1, len(st))
    sw = w / n
    d = 0.7
    cy = y + 0.45
    cv.line(x + sw / 2, cy + d / 2, x + w - sw / 2, cy + d / 2, color=("accent1", 0.6), width=3)
    titles = [_s(s.get("titel")) for s in st]
    texts = [_s(s.get("text")) for s in st]
    tsize = cv.group_size(titles, sw - 0.2, 0.9, [21, 20, 19, 18, 17, 16, 15, 14, 13], bold=True,
                          label="Prozessschritte")
    bsize = cv.group_size(texts, sw - 0.2, h - (cy - y) - d - 1.2, [19, 18, 17, 16, 15, 14, 13, 12, 11],
                          label="Prozesstexte")
    for i in range(n):
        sx = x + i * sw
        number_dot(cv, sx + sw / 2 - d / 2, cy, d, i + 1, fill=PRIMARY if i < n - 1 else DARK)
        cv.text(sx + 0.1, cy + d + 0.25, sw - 0.2, 0.9, titles[i], [tsize], color=DARK, bold=True, align="center",
                label=f"Schritt {i + 1} Titel", check=False)
        cv.text(sx + 0.1, cy + d + 1.15, sw - 0.2, h - (cy - y) - d - 1.2, texts[i], [bsize], color=TEXT,
                align="center", label=f"Schritt {i + 1} Text", check=False)


def _table(cv, x, y, w, h, kopf, zeilen, label="Tabelle"):
    kopf = [_s(k) for k in _list(kopf)][:5]
    rows = [r for r in _list(zeilen) if isinstance(r, list)][:7]
    ncol = max(len(kopf), max((len(r) for r in rows), default=1))
    if not kopf:
        kopf = [""] * ncol
    kopf += [""] * (ncol - len(kopf))
    rows = [([_s(c) for c in r] + [""] * ncol)[:ncol] for r in rows]
    colw = w / ncol
    # Schriftgröße so wählen, dass die geschätzte Tabellenhöhe passt
    chosen, est = cv.sz(11), None
    for s in dict.fromkeys(cv.sz(v) for v in [18, 17, 16, 15, 14, 13, 12, 11]):
        lh = cv.m.line_height(s)
        total = 0
        for r in [kopf] + rows:
            lines = max(cv.m.count_lines(c or " ", s, (colw - 0.2) * 72, bold=(r is kopf)) for c in r)
            total += lines * lh + 0.16 * 72
        if total <= h * 72:
            chosen, est = s, total
            break
    else:
        cv.warn("textueberlauf", f"{label}: Tabelle ist zu umfangreich – Zeilen/Text reduzieren.")
    gt = cv.slide.shapes.add_table(len(rows) + 1, ncol, E(x),
                                   E(y),
                                   E(w),
                                   E(min(h, (est or h * 72) / 72)))
    tbl = gt.table
    tbl.first_row = True
    tbl.horz_banding = False
    for ci in range(ncol):
        tbl.columns[ci].width = E(colw)
    for ri, r in enumerate([kopf] + rows):
        for ci in range(ncol):
            cell = tbl.cell(ri, ci)
            cell.margin_left = cell.margin_right = Pt(7)
            cell.margin_top = cell.margin_bottom = Pt(4)
            cell.fill.solid()
            if ri == 0:
                cv.color(cell.fill.fore_color, DARK)
            else:
                cv.color(cell.fill.fore_color, PANEL if ri % 2 == 1 else ("lt1"))
            tf = cell.text_frame
            tf.word_wrap = True
            tf.text = r[ci]
            for p in tf.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(chosen)
                    run.font.bold = (ri == 0) or (ci == 0 and ncol > 2)
                    cv.color(run.font.color, "lt1" if ri == 0 else TEXT)
    return gt


def tabelle(cv, f, box):
    x, y, w, h = box
    hinweis = _s(f.get("hinweis"))
    th = h - (0.6 if hinweis else 0)
    _table(cv, x, y + 0.05, w, th - 0.05, f.get("kopf"), f.get("zeilen"))
    if hinweis:
        cv.text(x, y + h - 0.5, w, 0.5, hinweis, [14, 13, 12, 11], color=MUTED, italic=True, anchor="bottom",
                label="Tabellenhinweis")


def zitat_definition(cv, f, box):
    x, y, w, h = box
    text, quelle = _s(f.get("text")), _s(f.get("quelle"))
    cv.text(x, y - 0.25, 1.6, 1.8, "“", [140, 120], color=("accent1", 0.55), bold=True, label="Anführungszeichen", check=False)
    tw = min(w - 1.4, 10.4)
    cv.rect(x + 1.25, y + 0.35, tw + 0.3, h - 0.6 - (0.6 if quelle else 0), fill=PANEL, radius=0.04)
    cv.text(x + 1.5, y + 0.45, tw - 0.2, h - 0.8 - (0.6 if quelle else 0), text, [30, 28, 26, 24, 22, 20, 18],
            color=DARK, italic=True, anchor="middle", line_spacing=1.05, label="Zitat/Definition")
    if quelle:
        cv.text(x + 1.5, y + h - 0.65, tw - 0.2, 0.5, "— " + quelle, [15, 14, 13, 12], color=MUTED, align="right",
                label="Quelle")


def zahl_fakt(cv, f, box):
    x, y, w, h = box
    fk = [k for k in _list(f.get("fakten")) if isinstance(k, dict)][:3]
    n = max(1, len(fk))
    cw = w / n
    for i, k in enumerate(fk):
        cx = x + i * cw
        if i > 0:
            cv.line(cx, y + 0.5, cx, y + h - 0.5, color=("dk1", 0.85), width=1)
        cv.text(cx + 0.3, y + 0.4, cw - 0.6, 1.6, _s(k.get("wert")), [72, 66, 60, 54, 48, 42, 36], color=PRIMARY,
                bold=True, anchor="bottom", label=f"Zahl {i + 1}")
        cv.text(cx + 0.3, y + 2.15, cw - 0.6, h - 3.0, _s(k.get("label")), [22, 20, 19, 18, 17, 16, 15, 14],
                color=DARK, label=f"Fakt {i + 1}")
        q = _s(k.get("quelle"))
        if q:
            cv.text(cx + 0.3, y + h - 0.75, cw - 0.6, 0.6, "Quelle: " + q, [12, 11, 10], color=MUTED,
                    anchor="bottom", label=f"Fakt {i + 1} Quelle")
        else:
            cv.warn("quelle_fehlt", f"Zahl/Fakt {i + 1} ohne Quelle.")


def praxisbeispiel(cv, f, box):
    x, y, w, h = box
    parts = [("Ausgangslage", _s(f.get("situation")), THIRD), ("Vorgehen", _s(f.get("vorgehen")), PRIMARY),
             ("Ergebnis", _s(f.get("ergebnis")), OK)]
    gap = 0.55
    cw = (w - 2 * gap) / 3
    size = cv.group_size([t for _, t, _ in parts], cw - 0.5, h - 0.95,
                         [24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11], label="Praxisbeispiel")
    for i, (lab, txt, col) in enumerate(parts):
        cx = x + i * (cw + gap)
        cv.rect(cx, y, cw, h, fill=PANEL if i != 1 else ("accent1", 0.82), radius=0.05)
        badge(cv, cx + 0.25, y + 0.25, lab.upper(), color=col)
        cv.text(cx + 0.25, y + 0.8, cw - 0.5, h - 0.95, txt, [size], color=TEXT, label=lab, check=False)
        if i < 2:
            ar = cv.shape(MSO_SHAPE.RIGHT_ARROW, cx + cw + 0.1, y + h / 2 - 0.22, gap - 0.2, 0.44, fill=("dk1", 0.7))


def prompt_demo(cv, f, box):
    x, y, w, h = box
    prompt, tool, erk = _s(f.get("prompt")), _s(f.get("werkzeug")), _list(f.get("erklaerung"))
    lw = w * (0.6 if erk else 1.0)
    cv.rect(x, y, lw, h, fill=("dk2", 0.94), line=("dk2", 0.75), radius=0.03)
    cv.rect(x, y, lw, 0.5, fill=DARK, radius=None)
    cv.text(x + 0.2, y, lw - 0.4, 0.5, ("Prompt" + (" · " + tool if tool else "")), [14], color="lt1", bold=True,
            anchor="middle", label="Prompt-Kopf")
    cv.text(x + 0.25, y + 0.65, lw - 0.5, h - 0.8, prompt.split("\n"), [18, 17, 16, 15, 14, 13, 12, 11], color=TEXT,
            mono=True, space=0.25, label="Prompt")
    if erk:
        ex = x + lw + 0.4
        cv.text(ex, y, w - lw - 0.4, 0.45, "Worauf es ankommt", [16], color=PRIMARY, bold=True, label="Einordnung")
        cv.text(ex, y + 0.55, w - lw - 0.4, h - 0.6, erk, [19, 18, 17, 16, 15, 14, 13], bullets=PRIMARY,
                lead_bold=True, space=0.6, label="Einordnung")


def _placeholder_visual(cv, x, y, w, h, kind, text):
    cv.rect(x, y, w, h, fill=("dk1", 0.95), line=("dk1", 0.6), radius=0.03, line_w=1.25, dash=True)
    cv.text(x + 0.3, y + h / 2 - 0.9, w - 0.6, 0.45, kind, [14], color=("dk1", 0.35), bold=True, align="center",
            label=kind)
    cv.text(x + 0.3, y + h / 2 - 0.4, w - 0.6, h / 2 + 0.2, text or "Bild manuell einfügen", [16, 15, 14, 13, 12],
            color=("dk1", 0.35), align="center", label=kind)
    cv.warn("manuell", f"{kind} muss manuell ergänzt werden.")


def tool_anleitung(cv, f, box):
    x, y, w, h = box
    schritte, tool, hint = _list(f.get("schritte")), _s(f.get("werkzeug")), _s(f.get("screenshot_hinweis"))
    pw = w * 0.52
    _placeholder_visual(cv, x, y, pw, h, "SCREENSHOT" + (" · " + tool.upper() if tool else ""), hint)
    sx = x + pw + 0.45
    sw = w - pw - 0.45
    n = max(1, len(schritte))
    row = h / n
    d = 0.42
    size = cv.group_size(schritte, sw - d - 0.2, row, [20, 19, 18, 17, 16, 15, 14, 13, 12, 11], label="Anleitung")
    for i, t in enumerate(schritte):
        ry = y + i * row
        number_dot(cv, sx, ry + min(0.08, row / 4), d, i + 1, size=13)
        cv.text(sx + d + 0.2, ry, sw - d - 0.2, row, t, [size], color=TEXT, lead_bold=True, label=f"Schritt {i + 1}", check=False)


def bild_text(cv, f, box):
    x, y, w, h = box
    punkte = _list(f.get("punkte"))
    pw = w * (0.48 if punkte else 1.0)
    _placeholder_visual(cv, x, y, pw, h, "BILDIDEE", _s(f.get("bildidee")))
    if punkte:
        cv.text(x + pw + 0.45, y + 0.1, w - pw - 0.45, h - 0.1, punkte, BODY, bullets=PRIMARY, lead_bold=True,
                space=0.6, label="Punkte")


def uebung(cv, f, box):
    x, y, w, h = box
    badge(cv, x, y, "ÜBUNG", color=SECOND)
    basis, vert = _s(f.get("basis")), _s(f.get("vertiefung"))
    lower = 1.0 if (basis or vert) else 0
    top = y + 0.5
    ah = h - 0.5 - lower - (0.2 if lower else 0)
    lw = w * 0.62
    cv.text(x, top, lw - 0.3, 0.4, "Arbeitsauftrag", [15], color=SECOND, bold=True, label="Auftrag-Label")
    cv.text(x, top + 0.45, lw - 0.3, ah - 0.45, _list(f.get("auftrag")), [21, 20, 19, 18, 17, 16, 15, 14, 13],
            numbered=SECOND, bullets=SECOND, lead_bold=True, space=0.55, label="Arbeitsauftrag")
    # Infospalte
    ix, iw = x + lw, w - lw
    cv.rect(ix, top, iw, ah, fill=("accent2", 0.88), radius=0.05)
    info = [("DAUER", _s(f.get("dauer"))), ("SOZIALFORM", _s(f.get("sozialform"))),
            ("MATERIAL", _s(f.get("material"))), ("ERGEBNIS", _s(f.get("ergebnis")))]
    info = [i for i in info if i[1]]
    base = 0.6
    extra = max(0.0, (ah - 0.3) - base * len(info))
    lens = [len(v) for _, v in info]
    rows_h = [base + extra * l / (sum(lens) or 1) for l in lens]
    ry = top + 0.15
    vsize = 12
    for s_ in [18, 17, 16, 15, 14, 13, 12]:
        if all(cv.m.fits([v], (iw - 0.66) * 72, (rh_ - 0.3) * 72, s_) for (_, v), rh_ in zip(info, rows_h)):
            vsize = s_
            break
    else:
        cv.warn("textueberlauf", "Übungsinfo: Text zu lang – bitte kürzen.")
    for (lab, val), rh in zip(info, rows_h):
        cv.text(ix + 0.25, ry, iw - 0.5, 0.3, lab, [11], color=("accent2", -0.35), bold=True, label=lab, check=False)
        if lab == "DAUER":
            cv.text(ix + 0.25, ry + 0.24, iw - 0.5, rh - 0.26, val, [24, 22, 20, 18, vsize], color=DARK, bold=True,
                    label=lab)
        else:
            cv.text(ix + 0.25, ry + 0.24, iw - 0.5, rh - 0.26, val, [vsize], color=DARK, label=lab, check=False)
        ry += rh
    if not _s(f.get("ergebnis")):
        cv.warn("didaktik", "Übung ohne erwartetes Ergebnis.")
    if lower:
        ly = y + h - lower
        bw = (w - 0.3) / 2 if (basis and vert) else w
        col = 0
        lsize = cv.group_size([basis, vert], bw - 0.4, lower - 0.42, [17, 16, 15, 14, 13, 12], label="Basis/Vertiefung")
        for lab, val, c in (("Basis", basis, PRIMARY), ("Vertiefung", vert, DARK)):
            if not val:
                continue
            bx = x + col * (bw + 0.3)
            cv.rect(bx, ly, bw, lower, fill=PANEL if c == PRIMARY else PANEL2, radius=0.08)
            cv.text(bx + 0.2, ly + 0.08, bw - 0.4, 0.3, lab.upper(), [11], color=c, bold=True, label=lab, check=False)
            cv.text(bx + 0.2, ly + 0.38, bw - 0.4, lower - 0.42, val, [lsize], color=TEXT, label=lab, check=False)
            col += 1


def material(cv, f, box):
    x, y, w, h = box
    badge(cv, x, y, "MATERIAL", color=THIRD)
    text, kopf, zeilen = _s(f.get("text")), f.get("kopf"), f.get("zeilen")
    has_tab = bool(_list(zeilen))
    top = y + 0.5
    if text and has_tab:
        nrows = len(_list(zeilen)) + 1
        th = max((h - 0.5) * 0.35, (h - 0.5) - nrows * 0.5 - 0.3)
    elif text:
        th = h - 0.5
    else:
        th = 0
    if text:
        cv.rect(x, top, w, th, fill=("dk2", 0.95), radius=0.03)
        cv.text(x + 0.25, top + 0.12, w - 0.5, th - 0.24, text.split("\n"), [18, 17, 16, 15, 14, 13, 12, 11],
                color=TEXT, space=0.3, label="Materialtext")
    if has_tab:
        ty = top + th + (0.2 if text else 0)
        _table(cv, x, ty, w, y + h - ty, kopf, zeilen, label="Materialtabelle")
    if not text and not has_tab:
        cv.warn("didaktik", "Material-Folie ohne Inhalt.")


def loesung(cv, f, box):
    x, y, w, h = box
    badge(cv, x, y, "MUSTERLÖSUNG", color=OK)
    hinweis = _s(f.get("hinweis"))
    bh = h - 0.55 - (0.75 if hinweis else 0)
    cv.rect(x, y + 0.5, w, bh, fill=("accent6", 0.88), radius=0.04)
    cv.text(x + 0.3, y + 0.65, min(w - 0.6, 11.4), bh - 0.3, _list(f.get("punkte")), BODY,
            numbered=OK, bullets=OK, lead_bold=True, space=0.55, label="Musterlösung")
    if hinweis:
        cv.text(x, y + h - 0.65, w, 0.6, hinweis, [15, 14, 13, 12], color=MUTED, italic=True, anchor="bottom",
                label="Lösungshinweis")


def reflexion(cv, f, box):
    x, y, w, h = box
    fr = _list(f.get("fragen"))[:4]
    n = max(1, len(fr))
    cols = 2 if n == 4 else n
    rows = 2 if n == 4 else 1
    gap = 0.3
    cw = (w - gap * (cols - 1)) / cols
    chh = min((h - gap * (rows - 1)) / rows, 3.6)
    size = cv.group_size(fr, cw - 1.2, chh - 0.3, [24, 22, 20, 19, 18, 17, 16, 15, 14, 13, 12], bold=True,
                         label="Reflexionsfragen")
    oy = y + max(0, (h - (chh * rows + gap * (rows - 1))) / 2)
    for i, q in enumerate(fr):
        r, c = divmod(i, cols)
        cx, cy = x + c * (cw + gap), oy + r * (chh + gap)
        cv.rect(cx, cy, cw, chh, fill=PANEL, radius=0.06)
        number_dot(cv, cx + 0.25, cy + 0.25, 0.6, "?", fill=SECOND, size=20)
        cv.text(cx + 1.0, cy + 0.15, cw - 1.2, chh - 0.3, q, [size], color=DARK, bold=True, anchor="middle",
                label=f"Frage {i + 1}", check=False)


def zusammenfassung(cv, f, box):
    x, y, w, h = box
    kp, aus = _list(f.get("kernpunkte"))[:5], _s(f.get("ausblick"))
    lh = h - (1.0 if aus else 0)
    n = max(1, len(kp))
    row = min(0.95, lh / n)
    d = 0.42
    tw = min(w, 11.6) - d - 0.3
    size = cv.group_size(kp, tw, row, [22, 20, 19, 18, 17, 16, 15, 14, 13, 12], label="Zusammenfassung")
    for i, t in enumerate(kp):
        ry = y + i * row
        number_dot(cv, x, ry + (row - d) / 2, d, "✓", fill=OK, size=15)
        cv.text(x + d + 0.25, ry, tw, row, t, [size], color=TEXT, anchor="middle", lead_bold=True,
                label=f"Kernpunkt {i + 1}", check=False)
    if aus:
        bar_note(cv, x, y + h - 0.85, w, 0.85, "Ausblick", aus, fill=("accent2", 0.85), accent=SECOND)


def quellen(cv, f, box):
    x, y, w, h = box
    ein = _list(f.get("eintraege"))
    if len(ein) > 5:
        half = (len(ein) + 1) // 2
        cv.text(x, y, w / 2 - 0.2, h, ein[:half], [14, 13, 12, 11, 10], numbered=PRIMARY, bullets=PRIMARY, space=0.5,
                label="Quellen")
        cv.text(x + w / 2 + 0.2, y, w / 2 - 0.2, h, ein[half:], [14, 13, 12, 11, 10], numbered=PRIMARY,
                bullets=PRIMARY, space=0.5, label="Quellen")
    else:
        cv.text(x, y, w, h, ein, [16, 15, 14, 13, 12, 11], numbered=PRIMARY, bullets=PRIMARY, space=0.5,
                label="Quellen")


def pause(cv, f, box):
    x, y, w, h = box
    dauer, text = _s(f.get("dauer")), _s(f.get("text"))
    cv.text(x, y + h * 0.15, w, h * 0.4, dauer or "", [80, 72, 64], color=PRIMARY, bold=True, align="center",
            anchor="bottom", label="Pausendauer")
    if text:
        cv.text(x + 1, y + h * 0.58, w - 2, h * 0.3, text, [22, 20, 18], color=MUTED, align="center",
                label="Pausentext")


ART_COLOR = {"input": PRIMARY, "uebung": SECOND, "pause": ("dk1", 0.55), "reflexion": THIRD, "sonstiges": DARK}
ART_LABEL = {"input": "Input", "uebung": "Übung", "pause": "Pause", "reflexion": "Reflexion", "sonstiges": ""}


def tagesablauf(cv, f, box):
    x, y, w, h = box
    ein = [e for e in _list(f.get("eintraege")) if isinstance(e, dict)][:12]
    n = max(1, len(ein))
    # einspaltig, solange die Zeilen hoch genug sind; zweispaltig nur, wenn jede Spalte breit genug bleibt
    two = h / n < 0.36 and (w - 0.5) / 2 > 4.2
    per = (n + 1) // 2 if two else n
    colw = (w - 0.5) / 2 if two else min(w, 11.4)
    row = min(0.72, h / per)
    chip_w = min(1.65, max(1.05, colw * 0.2))
    tx = chip_w + 0.25
    pad = min(0.18, row * 0.2)
    labs = [ART_LABEL.get(_s(e.get("art")).lower() or "input", "").upper() for e in ein]
    lw = max((cv.m.width(l, 11, bold=True) / 72 for l in labs if l), default=0) + 0.3
    size = cv.group_size([_s(e.get("titel")) for e in ein], colw - tx - lw, row,
                         [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10], label="Tagesablauf")
    for i, e in enumerate(ein):
        c, r = divmod(i, per)
        cx, ry = x + c * (colw + 0.5), y + r * row
        art = _s(e.get("art")).lower() or "input"
        col = ART_COLOR.get(art, DARK)
        chip = cv.rect(cx, ry + pad / 2, chip_w, row - pad, fill=col, radius=0.3)
        cv.text(0, 0, chip_w, row - pad, _s(e.get("zeit")), [14, 13, 12, 11, 10, 9], color="lt1", bold=True,
                align="center", anchor="middle", shape=chip, label="Zeit")
        cv.text(cx + tx, ry, colw - tx - lw, row, _s(e.get("titel")), [size],
                color=TEXT if art != "pause" else MUTED, anchor="middle", label="Agendapunkt", check=False)
        if labs[i]:
            cv.text(cx + colw - lw, ry, lw, row, labs[i], [11, 10, 9], color=col, bold=True, align="right",
                    anchor="middle", label="Art", check=False)
        if r < per - 1 and i < n - 1:
            cv.line(cx + tx, ry + row, cx + colw, ry + row, color=("dk1", 0.9), width=0.75)


RENDERERS = {
    "stichpunkte": stichpunkte, "lernziele": lernziele, "kernaussage": kernaussage, "leitfrage": leitfrage,
    "zwei_spalten": zwei_spalten, "karten": karten, "prozess": prozess, "tabelle": tabelle,
    "zitat_definition": zitat_definition, "zahl_fakt": zahl_fakt, "praxisbeispiel": praxisbeispiel,
    "prompt_demo": prompt_demo, "tool_anleitung": tool_anleitung, "bild_text": bild_text, "uebung": uebung,
    "material": material, "loesung": loesung, "reflexion": reflexion, "zusammenfassung": zusammenfassung,
    "quellen": quellen, "pause": pause, "tagesablauf": tagesablauf,
}
