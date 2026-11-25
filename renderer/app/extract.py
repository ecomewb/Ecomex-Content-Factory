"""Dateien (DOCX, XLSX, PPTX, PDF, TXT/MD) -> Markdown-Text mit Fundstellen.

Ersetzt die Azure-Document-Intelligence-Polling-Kette für Storyboards und Wissensimport.
Jeder Abschnitt trägt eine Fundstelle (Seite, Folie, Tabellenblatt/Zeile, Überschrift),
damit Agenten Aussagen nachvollziehbar belegen können.
"""
from __future__ import annotations

import io
import re


def _md_table(rows):
    rows = [[("" if c is None else str(c)).replace("\n", " ").replace("|", "/").strip() for c in r] for r in rows]
    rows = [r for r in rows if any(c for c in r)]
    if not rows:
        return ""
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * n]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def _docx(data: bytes):
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    d = docx.Document(io.BytesIO(data))
    sections, current, buf, n_tab = [], "Dokumentanfang", [], 0
    body = d.element.body
    for el in body.iterchildren():
        tag = el.tag.split("}")[-1]
        if tag == "p":
            p = Paragraph(el, d)
            txt = p.text.strip()
            if not txt:
                continue
            style = (p.style.name or "").lower() if p.style is not None else ""
            m = re.match(r"(heading|überschrift)\s*(\d)", style)
            if m or style == "title":
                if buf:
                    sections.append((current, "\n".join(buf)))
                level = int(m.group(2)) if m else 1
                current = txt
                buf = ["#" * level + " " + txt]
            elif "list" in style or "aufzählung" in style:
                buf.append("- " + txt)
            else:
                buf.append(txt)
        elif tag == "tbl":
            n_tab += 1
            t = Table(el, d)
            rows = []
            for r in t.rows:
                cells, seen = [], set()
                for c in r.cells:
                    if id(c._tc) in seen:  # verbundene Zellen nur einmal
                        continue
                    seen.add(id(c._tc))
                    cells.append(c.text)
                rows.append(cells)
            buf.append(f"[Tabelle {n_tab}]\n" + _md_table(rows))
    if buf:
        sections.append((current, "\n".join(buf)))
    return [{"fundstelle": f"Abschnitt {i + 1}: {h}", "text": t} for i, (h, t) in enumerate(sections)]


def _xlsx(data: bytes):
    import openpyxl

    wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True, read_only=True)
    out = []
    for ws in wb.worksheets:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        rows = [r for r in rows if any(v not in (None, "") for v in r)]
        if not rows:
            continue
        header = [str(c) if c is not None else f"Spalte {i + 1}" for i, c in enumerate(rows[0])]
        chunk = []
        for i, r in enumerate(rows[1:], start=2):
            pairs = [f"{header[j] if j < len(header) else f'Spalte {j + 1}'}: {v}" for j, v in enumerate(r)
                     if v not in (None, "")]
            chunk.append(f"Zeile {i} – " + "; ".join(pairs))
            if len(chunk) == 25:
                out.append({"fundstelle": f"Tabellenblatt '{ws.title}', Zeilen {i - 24}–{i}", "text": "\n".join(chunk)})
                chunk = []
        if chunk:
            last = len(rows)
            out.append({"fundstelle": f"Tabellenblatt '{ws.title}', Zeilen {last - len(chunk) + 1}–{last}",
                        "text": f"Spalten: {', '.join(header)}\n" + "\n".join(chunk)})
    return out


def _pptx(data: bytes):
    from pptx import Presentation

    prs = Presentation(io.BytesIO(data))
    out = []
    for i, s in enumerate(prs.slides, start=1):
        parts = []
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                parts.append(sh.text_frame.text.strip())
            elif getattr(sh, "has_table", False) and sh.has_table:
                parts.append(_md_table([[c.text for c in r.cells] for r in sh.table.rows]))
        if s.has_notes_slide:
            nt = s.notes_slide.notes_text_frame.text.strip()
            if nt:
                parts.append("Sprechernotiz: " + nt)
        if parts:
            out.append({"fundstelle": f"Folie {i}", "text": "\n".join(parts)})
    return out


def _pdf(data: bytes):
    import pdfplumber

    out = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for i, p in enumerate(pdf.pages, start=1):
            t = (p.extract_text() or "").strip()
            if t:
                out.append({"fundstelle": f"Seite {i}", "text": t})
    return out


def _text(data: bytes):
    txt = data.decode("utf-8", errors="replace")
    parts = re.split(r"(?m)^(?=#{1,3} )", txt)
    out = []
    for i, p in enumerate([p for p in parts if p.strip()], start=1):
        head = p.strip().splitlines()[0][:80]
        out.append({"fundstelle": f"Abschnitt {i}: {head}", "text": p.strip()})
    return out


def extract(filename: str, data: bytes) -> dict:
    ext = (filename.rsplit(".", 1)[-1] if "." in filename else "").lower()
    fn = {"docx": _docx, "xlsx": _xlsx, "xlsm": _xlsx, "pptx": _pptx, "pdf": _pdf, "txt": _text, "md": _text}.get(ext)
    if fn is None:
        raise ValueError(f"Dateityp '.{ext}' wird nicht unterstützt (erlaubt: docx, xlsx, pptx, pdf, txt, md). "
                         "Alte .doc/.xls/.ppt bitte vorher im neuen Format speichern.")
    abschnitte = fn(data)
    text = "\n\n".join(f"[{a['fundstelle']}]\n{a['text']}" for a in abschnitte)
    return {"dateiname": filename, "typ": ext, "abschnitte_anzahl": len(abschnitte), "zeichen": len(text),
            "text": text, "abschnitte": abschnitte,
            "hinweis": "Bilder, Diagramme und Screenshots werden nicht inhaltlich ausgewertet." if ext in ("pptx", "pdf", "docx") else ""}
