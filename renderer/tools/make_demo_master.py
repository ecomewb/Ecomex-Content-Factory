"""Erzeugt einen neutralen DEMO-Master (16:9, Open Sans), solange der echte ECOMEX-Master fehlt.

Produktiv wird masters/ecomex_master.pptx (euer Originalmaster) verwendet.
Aufruf: python tools/make_demo_master.py masters/demo_master.pptx
"""
import sys
from copy import deepcopy

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, PP_PLACEHOLDER
from pptx.enum.text import PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

COLORS = {"dk1": "1E2430", "lt1": "FFFFFF", "dk2": "16294D", "lt2": "EEF1F6", "accent1": "0F7C8C",
          "accent2": "E0892B", "accent3": "4A5FA8", "accent4": "7B8798", "accent5": "C2493A", "accent6": "3E8E5E",
          "hlink": "0F7C8C", "folHlink": "4A5FA8"}
LAYOUT_NAMES = ["Titelfolie", "Titel und Inhalt", "Abschnittsüberschrift", "Zwei Inhalte", "Vergleich",
                "Nur Titel", "Leer", "Inhalt mit Überschrift", "Bild mit Überschrift", "Titel und vertikaler Text",
                "Vertikaler Titel und Text"]
A = "http://schemas.openxmlformats.org/drawingml/2006/main"


class _Tmp:
    """python-pptx kann auf Master/Layouts keine Formen anlegen -> auf Hilfsfolie bauen und XML verschieben."""
    def __init__(self, prs):
        self.prs = prs
        self.slide = prs.slides.add_slide(prs.slide_layouts[6])
        self.shapes = self.slide.shapes

    def move_to(self, target_shapes, *shapes):
        tree = target_shapes._spTree
        for i, s in enumerate(shapes):
            el = deepcopy(s._element)
            tree.insert(2 + i, el)

    def close(self):
        lst = self.prs.slides._sldIdLst
        sid = lst[-1]
        self.prs.part.drop_rel(sid.rId)
        lst.remove(sid)


def set_theme(prs):
    part = prs.slide_master.part.part_related_by(RT.THEME)
    root = etree.fromstring(part.blob)
    ns = {"a": A}
    cs = root.find(".//a:clrScheme", ns)
    cs.set("name", "ECOMEX Demo")
    for name, val in COLORS.items():
        el = cs.find(f"a:{name}", ns)
        for c in list(el):
            el.remove(c)
        s = etree.SubElement(el, f"{{{A}}}srgbClr")
        s.set("val", val)
    for tag in ("majorFont", "minorFont"):
        lat = root.find(f".//a:fontScheme/a:{tag}/a:latin", ns)
        lat.set("typeface", "Open Sans")
    part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def scale_x(el, f):
    for off in el.iter(qn("a:off")):
        off.set("x", str(int(int(off.get("x")) * f)))
    for ext in el.iter(qn("a:ext")):
        if ext.get("cx"):
            ext.set("cx", str(int(int(ext.get("cx")) * f)))


def main(out):
    prs = Presentation()
    f = 13.333 / 10
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    master = prs.slide_master
    scale_x(master._element.find(qn("p:cSld")), f)
    for lay in master.slide_layouts:
        scale_x(lay._element.find(qn("p:cSld")), f)
    set_theme(prs)
    for lay, name in zip(master.slide_layouts, LAYOUT_NAMES):
        lay.name = name

    # Titelstil: links, fett, dk2
    ts = master._element.find(qn("p:txStyles")).find(qn("p:titleStyle")).find(qn("a:lvl1pPr"))
    ts.set("algn", "l")
    d = ts.find(qn("a:defRPr"))
    d.set("sz", "2800")
    d.set("b", "1")
    for c in list(d):
        if c.tag == qn("a:solidFill"):
            d.remove(c)
    sf = etree.SubElement(d, qn("a:solidFill"))
    etree.SubElement(sf, qn("a:schemeClr")).set("val", "tx2")
    d.insert(0, sf)

    for ph in master.placeholders:
        t = ph.placeholder_format.type
        if t == PP_PLACEHOLDER.TITLE:
            ph.left, ph.top, ph.width, ph.height = Inches(0.6), Inches(0.45), Inches(12.13), Inches(0.95)
            ph.text_frame._bodyPr.set("anchor", "b")
        elif t == PP_PLACEHOLDER.BODY:
            ph.left, ph.top, ph.width, ph.height = Inches(0.6), Inches(1.65), Inches(12.13), Inches(5.0)
        elif t in (PP_PLACEHOLDER.DATE, PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER):
            ph.top = Inches(7.0)
            ph.height = Inches(0.35)

    # Master-Deko: Akzentlinie oben links + Wortmarke oben rechts (erscheint auf allen Folien)
    tmp = _Tmp(prs)
    sp = tmp.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(0.28), Inches(0.75), Inches(0.07))
    sp.fill.solid(); sp.fill.fore_color.rgb = RGBColor.from_string(COLORS["accent1"]); sp.line.fill.background()
    st = sp._element.find(qn("p:style"))
    if st is not None:
        sp._element.remove(st)
    tb = tmp.shapes.add_textbox(Inches(10.4), Inches(0.16), Inches(2.33), Inches(0.3))
    p = tb.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    r = p.add_run(); r.text = "ecomex · DEMO-MASTER"
    r.font.size = Pt(9); r.font.bold = True; r.font.color.rgb = RGBColor.from_string(COLORS["accent4"])
    tmp.move_to(master.shapes, sp, tb)

    # Titelfolie
    tl = master.slide_layouts[0]
    for ph in tl.placeholders:
        t = ph.placeholder_format.type
        if t == PP_PLACEHOLDER.CENTER_TITLE:
            ph.left, ph.top, ph.width, ph.height = Inches(1.0), Inches(2.2), Inches(11.0), Inches(2.0)
            ph.text_frame._bodyPr.set("anchor", "b")
        elif t == PP_PLACEHOLDER.SUBTITLE:
            ph.left, ph.top, ph.width, ph.height = Inches(1.0), Inches(4.45), Inches(11.0), Inches(1.4)
            lst = ph.text_frame._txBody.find(qn("a:lstStyle"))
            lvl = lst.find(qn("a:lvl1pPr")) if lst is not None else None
            if lvl is not None:
                lvl.set("algn", "l")
    band = tmp.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.35), prs.slide_height)
    band.fill.solid(); band.fill.fore_color.rgb = RGBColor.from_string(COLORS["accent1"]); band.line.fill.background()
    st = band._element.find(qn("p:style"))
    if st is not None:
        band._element.remove(st)
    tmp.move_to(tl.shapes, band)

    # Abschnittsüberschrift: Titel groß unten, Text darunter
    sl = master.slide_layouts[2]
    for ph in sl.placeholders:
        t = ph.placeholder_format.type
        if t == PP_PLACEHOLDER.TITLE:
            ph.left, ph.top, ph.width, ph.height = Inches(1.0), Inches(2.3), Inches(11.0), Inches(1.6)
            ph.text_frame._bodyPr.set("anchor", "b")
        elif t == PP_PLACEHOLDER.BODY:
            ph.left, ph.top, ph.width, ph.height = Inches(1.0), Inches(4.05), Inches(10.0), Inches(1.5)
    band2 = tmp.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.35), prs.slide_height)
    band2.fill.solid(); band2.fill.fore_color.rgb = RGBColor.from_string(COLORS["accent1"]); band2.line.fill.background()
    st = band2._element.find(qn("p:style"))
    if st is not None:
        band2._element.remove(st)
    tmp.move_to(sl.shapes, band2)
    tmp.close()

    prs.save(out)
    print("Demo-Master gespeichert:", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "masters/demo_master.pptx")
