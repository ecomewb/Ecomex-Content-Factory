"""Bausteine: Master/Theme auslesen, Layout-Auswahl und native, editierbare Formen.

Alle Farben werden als THEME-Farben gesetzt (accent1, dk2 …). Dadurch übernimmt jedes Deck
automatisch die Farbwelt des eingesetzten ECOMEX-Masters – und folgt ihr, wenn der Master
später angepasst wird. Schriften werden nicht hart gesetzt, sondern aus dem Theme geerbt.
"""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field

from lxml import etree
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE, PP_PLACEHOLDER
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

from .textfit import Measurer

EMU_PER_IN = 914400
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

THEME = {
    "dk1": MSO_THEME_COLOR.TEXT_1, "lt1": MSO_THEME_COLOR.BACKGROUND_1,
    "dk2": MSO_THEME_COLOR.TEXT_2, "lt2": MSO_THEME_COLOR.BACKGROUND_2,
    "accent1": MSO_THEME_COLOR.ACCENT_1, "accent2": MSO_THEME_COLOR.ACCENT_2,
    "accent3": MSO_THEME_COLOR.ACCENT_3, "accent4": MSO_THEME_COLOR.ACCENT_4,
    "accent5": MSO_THEME_COLOR.ACCENT_5, "accent6": MSO_THEME_COLOR.ACCENT_6,
}

FOOTER_TYPES = {PP_PLACEHOLDER.DATE, PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER}
CONTENT_TYPES = {PP_PLACEHOLDER.BODY, PP_PLACEHOLDER.OBJECT, PP_PLACEHOLDER.PICTURE, PP_PLACEHOLDER.TABLE,
                 PP_PLACEHOLDER.CHART, PP_PLACEHOLDER.MEDIA_CLIP, PP_PLACEHOLDER.ORG_CHART,
                 PP_PLACEHOLDER.SUBTITLE, PP_PLACEHOLDER.VERTICAL_BODY, PP_PLACEHOLDER.VERTICAL_OBJECT}


def E(inches: float) -> Emu:
    return Emu(int(round(inches * EMU_PER_IN)))


def inch(emu) -> float:
    return int(emu) / EMU_PER_IN


# --------------------------------------------------------------------------- Theme / Master

@dataclass
class ThemeInfo:
    colors: dict
    major_font: str
    minor_font: str
    title_size: float


def read_theme(prs) -> ThemeInfo:
    master = prs.slide_master
    colors, major, minor = {}, "Open Sans", "Open Sans"
    try:
        theme_part = master.part.part_related_by(RT.THEME)
        root = etree.fromstring(theme_part.blob)
        ns = {"a": A_NS}
        for name in THEME:
            el = root.find(f".//a:clrScheme/a:{name}", ns)
            if el is None:
                continue
            srgb, sysc = el.find("a:srgbClr", ns), el.find("a:sysClr", ns)
            colors[name] = srgb.get("val") if srgb is not None else (sysc.get("lastClr") if sysc is not None else None)
        mj = root.find(".//a:fontScheme/a:majorFont/a:latin", ns)
        mn = root.find(".//a:fontScheme/a:minorFont/a:latin", ns)
        major = mj.get("typeface") if mj is not None else major
        minor = mn.get("typeface") if mn is not None else minor
    except Exception:
        pass
    title_size = 28.0
    try:
        el = master._element.find(qn("p:txStyles") + "/" + qn("p:titleStyle") + "/" + qn("a:lvl1pPr") + "/" + qn("a:defRPr"))
        if el is not None and el.get("sz"):
            title_size = int(el.get("sz")) / 100
    except Exception:
        pass
    return ThemeInfo(colors, major, minor, title_size)


@dataclass
class LayoutInfo:
    layout: object
    name: str
    kind: str
    title_box: tuple | None  # (x, y, w, h) in Zoll
    placeholders: list = field(default_factory=list)


def _ph_list(layout):
    out = []
    for ph in layout.placeholders:
        try:
            out.append({"idx": ph.placeholder_format.idx, "type": ph.placeholder_format.type, "name": ph.name,
                        "box": (inch(ph.left or 0), inch(ph.top or 0), inch(ph.width or 0), inch(ph.height or 0))})
        except Exception:
            continue
    return out


def _title_box(layout, master):
    for src in (layout, master):
        for ph in src.placeholders:
            if ph.placeholder_format.type in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE):
                if ph.width:
                    return (inch(ph.left), inch(ph.top), inch(ph.width), inch(ph.height))
    return None


def classify_layout(layout, master) -> LayoutInfo:
    phs = _ph_list(layout)
    types = {p["type"] for p in phs}
    name = layout.name or ""
    low = name.lower()
    content = [p for p in phs if p["type"] in CONTENT_TYPES]
    has_title = PP_PLACEHOLDER.TITLE in types or PP_PLACEHOLDER.CENTER_TITLE in types
    if PP_PLACEHOLDER.CENTER_TITLE in types or re.search(r"titelfolie|titelseite|title slide|cover|^titel$", low):
        kind = "title_slide"
    elif re.search(r"abschnitt|section|kapitel|trenner|divider", low):
        kind = "section"
    elif has_title and not content:
        kind = "title_only"
    elif not has_title:
        kind = "blank"
    else:
        kind = "title_content"
    return LayoutInfo(layout, name, kind, _title_box(layout, master), phs)


class MasterInfo:
    """Sucht passende Master-Layouts. Optional übersteuerbar per master_map."""

    def __init__(self, prs, master_map: dict | None = None):
        self.prs = prs
        self.master = prs.slide_master
        self.layouts = [classify_layout(l, self.master) for l in self.master.slide_layouts]
        self.map = master_map or {}
        self.slide_w = inch(prs.slide_width)
        self.slide_h = inch(prs.slide_height)
        self.footer_top = self._footer_top()

    def _footer_top(self):
        tops = []
        for ph in self.master.placeholders:
            if ph.placeholder_format.type in FOOTER_TYPES and ph.top:
                tops.append(inch(ph.top))
        return min(tops) if tops else self.slide_h - 0.55

    def by_name(self, name):
        for li in self.layouts:
            if li.name.strip().lower() == str(name).strip().lower():
                return li
        return None

    def pick(self, catalog_id: str, default_kind: str = "title_only") -> LayoutInfo:
        wanted = self.map.get(catalog_id)
        if wanted:
            li = self.by_name(wanted)
            if li:
                return li
        kind_for = {"titel": "title_slide", "kapitel": "section"}
        kind = kind_for.get(catalog_id, default_kind)
        if catalog_id not in kind_for and self.map.get("default"):
            li = self.by_name(self.map["default"])
            if li:
                return li
        name_hint = {"title_only": r"nur titel|title only", "section": r"abschnitt|section", "title_slide": r"titelfolie|title slide"}
        cands = [l for l in self.layouts if l.kind == kind]
        hint = name_hint.get(kind)
        if hint:
            named = [l for l in cands if re.search(hint, l.name.lower())]
            cands = named or cands
        if cands:
            return cands[0]
        for k in ("title_only", "title_content"):
            c = [l for l in self.layouts if l.kind == k]
            if c:
                return c[0]
        return self.layouts[0]

    def describe(self):
        return [{"name": l.name, "art": l.kind, "titelbox_zoll": [round(v, 2) for v in l.title_box] if l.title_box else None,
                 "platzhalter": [{"idx": p["idx"], "typ": str(p["type"]).split(".")[-1].split(" ")[0], "name": p["name"]} for p in l.placeholders]}
                for l in self.layouts]


# --------------------------------------------------------------------------- Zeichnen

class Canvas:
    """Kapselt eine Folie samt Mess- und Warnlogik."""

    def __init__(self, slide, ctx, slide_no: int):
        self.slide = slide
        self.ctx = ctx
        self.no = slide_no
        self.m: Measurer = ctx.measurer
        # Schriftgrößen sind für 13,33-Zoll-Folien ausgelegt; kleinere Master (z. B. 10 Zoll) proportional verkleinern
        self.k = max(0.6, min(1.0, ctx.master.slide_w / 13.333))

    def sz(self, s):
        return s if self.k >= 0.999 else max(9.0, round(s * self.k * 2) / 2)

    # ---- Farbe
    @staticmethod
    def color(target, spec):
        """spec: 'accent1' | ('accent1', 0.8) | '#RRGGBB'"""
        if spec is None:
            return
        bright = 0.0
        if isinstance(spec, tuple):
            spec, bright = spec
        if isinstance(spec, str) and spec.startswith("#"):
            target.rgb = RGBColor.from_string(spec[1:])
        else:
            target.theme_color = THEME[spec]
            if bright:
                target.brightness = bright

    def warn(self, art, text):
        self.ctx.warn(self.no, art, text)

    def group_size(self, texts, w_in, h_in, sizes, bold=False, label="Text", space=0.45, indent=0.0):
        """Eine gemeinsame Größe für gleichartige Felder (Karten, Spalten …)."""
        texts = [t if isinstance(t, list) else [t] for t in texts if t]
        aw = max(0.2, w_in - 0.16 - indent) * 72
        ah = max(0.1, h_in - 0.08) * 72
        for s in sizes:
            if all(self.m.fits(t, aw, ah, self.sz(s), bold, space_factor=space) for t in texts):
                return s  # unskaliert zurück; text() skaliert genau einmal
        self.warn("textueberlauf", f"{label}: Text zu lang für den verfügbaren Platz – bitte kürzen.")
        return sizes[-1]

    # ---- Formen
    def shape(self, kind, x, y, w, h, fill=None, line=None, radius=None, line_w=1.0, dash=False):
        shp = self.slide.shapes.add_shape(kind, E(x), E(y), E(w), E(h))
        st = shp._element.find(qn("p:style"))
        if st is not None:  # Theme-Effekte (Schatten/Verläufe) entfernen -> ruhiges, sauberes Design
            shp._element.remove(st)
        if fill is None:
            shp.fill.background()
        else:
            shp.fill.solid()
            self.color(shp.fill.fore_color, fill)
        if line is None:
            shp.line.fill.background()
        else:
            shp.line.fill.solid()
            self.color(shp.line.fill.fore_color, line)
            shp.line.width = Pt(line_w)
            if dash:
                from pptx.enum.dml import MSO_LINE
                shp.line.dash_style = MSO_LINE.DASH
        if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
            shp.adjustments[0] = radius
        tf = shp.text_frame
        tf.margin_left = tf.margin_right = E(0.08)
        tf.margin_top = tf.margin_bottom = E(0.04)
        return shp

    def rect(self, x, y, w, h, fill=None, line=None, radius=0.06, **kw):
        kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
        return self.shape(kind, x, y, w, h, fill, line, radius if radius else None, **kw)

    def line(self, x1, y1, x2, y2, color="lt2", width=2.0):
        c = self.slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2))
        c.line.fill.solid()
        self.color(c.line.fill.fore_color, color)
        c.line.width = Pt(width)
        st = c._element.find(qn("p:style"))
        if st is not None:
            c._element.remove(st)
        return c

    # ---- Text
    def text(self, x, y, w, h, paragraphs, sizes, color="dk1", bold=False, italic=False, align="left",
             anchor="top", bullets=None, lead_bold=False, mono=False, space=0.45, label=None, shape=None,
             line_spacing=1.0, numbered=False, check=True):
        """Textfeld mit automatischer Größenwahl. paragraphs: str oder Liste von str."""
        if isinstance(paragraphs, str):
            paragraphs = [paragraphs]
        paragraphs = [str(p) for p in paragraphs if p is not None and str(p).strip() != ""]
        if not paragraphs:
            return None
        if isinstance(sizes, (int, float)):
            sizes = [sizes]
        sizes = list(dict.fromkeys(self.sz(s) for s in sizes))
        ins_lr, ins_tb = 0.08, 0.04
        indent = 0.0
        if bullets or numbered:
            indent = 0.28
        avail_w = max(0.2, (w - 2 * ins_lr - indent)) * 72
        avail_h = max(0.1, (h - 2 * ins_tb)) * 72
        size, fits = self.m.fit(paragraphs, avail_w, avail_h, sizes, bold=bold, mono=mono, space_factor=space,
                                line_spacing=line_spacing)
        if not fits and check:
            self.warn("textueberlauf", f"{label or 'Textfeld'}: Text passt auch in {size:g} pt nicht vollständig – bitte kürzen.")
        if shape is not None:
            box = shape
        else:
            box = self.slide.shapes.add_textbox(E(x), E(y), E(w), E(h))
        tf = box.text_frame
        tf.clear()
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.margin_left = tf.margin_right = E(ins_lr)
        tf.margin_top = tf.margin_bottom = E(ins_tb)
        tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[anchor]
        al = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
        for i, ptext in enumerate(paragraphs):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.alignment = al
            if line_spacing != 1.0:
                para.line_spacing = line_spacing
            if i < len(paragraphs) - 1:
                para.space_after = Pt(round(size * space, 1))
            lead, rest = None, ptext
            if lead_bold:
                mm = re.match(r"^([^:]{2,38}):\s+(.+)$", ptext, flags=re.S)
                if mm:
                    lead, rest = mm.group(1) + ": ", mm.group(2)
            runs = [(lead, True)] if lead else []
            runs.append((rest, bold))
            for rt, rb in runs:
                r = para.add_run()
                r.text = rt
                f = r.font
                f.size = Pt(size)
                f.bold = rb
                f.italic = italic
                if mono:
                    f.name = "Consolas"
                self.color(f.color, color)
            if bullets or numbered:
                _set_bullet(para, indent, bullets, numbered)
        return box


def _set_bullet(para, indent_in, color_spec, numbered=False):
    pPr = para._p.get_or_add_pPr()
    pPr.set("marL", str(int(indent_in * EMU_PER_IN)))
    pPr.set("indent", str(int(-indent_in * EMU_PER_IN)))
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum", "a:buClr", "a:buFont"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    if color_spec and isinstance(color_spec, (str, tuple)):
        spec = color_spec[0] if isinstance(color_spec, tuple) else color_spec
        if not str(spec).startswith("#"):
            buClr = etree.SubElement(pPr, qn("a:buClr"))
            sc = etree.SubElement(buClr, qn("a:schemeClr"))
            sc.set("val", {"dk1": "tx1", "lt1": "bg1", "dk2": "tx2", "lt2": "bg2"}.get(spec, spec))
    if numbered:
        bu = etree.SubElement(pPr, qn("a:buAutoNum"))
        bu.set("type", "arabicPeriod")
    else:
        bf = etree.SubElement(pPr, qn("a:buFont"))
        bf.set("typeface", "Arial")
        bu = etree.SubElement(pPr, qn("a:buChar"))
        bu.set("char", "•")
    # Reihenfolge laut Schema: buClr, buFont, buChar/buAutoNum
    order = [qn("a:buClr"), qn("a:buSzPct"), qn("a:buFont"), qn("a:buChar"), qn("a:buAutoNum")]
    kids = [k for k in pPr if k.tag in order]
    for k in kids:
        pPr.remove(k)
    for k in sorted(kids, key=lambda e: order.index(e.tag)):
        pPr.append(k)


def remove_placeholder(ph):
    el = ph._element
    el.getparent().remove(el)


def clone_title_text(ph, text, size_pt, warn_cb, measurer: Measurer, min_size=20):
    """Titel in den Master-Platzhalter schreiben; Größe nur reduzieren, wenn nötig."""
    tf = ph.text_frame
    tf.word_wrap = True
    w = max(1.0, inch(ph.width) - 0.2) * 72
    h = max(0.4, inch(ph.height) - 0.1) * 72
    sizes = [s for s in [size_pt, size_pt - 2, size_pt - 4, size_pt - 6, size_pt - 8] if s >= min_size] or [min_size]
    size, fits = measurer.fit([text], w, h, sizes, bold=True, space_factor=0)
    tf.text = text
    for p in tf.paragraphs:
        for r in p.runs:
            r.font.size = Pt(size)
    if not fits:
        warn_cb("titel_zu_lang", f"Titel passt nicht in den Master-Platzhalter ({len(text)} Zeichen) – bitte kürzen.")
