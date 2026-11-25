"""Text-Vermessung mit echten Font-Metriken (Pillow + fontconfig).

Damit wählt der Renderer pro Textfeld die größte Schriftgröße, die in die Box passt,
und meldet echte Überlaufrisiken, statt Text heimlich abzuschneiden.
"""
from __future__ import annotations

import functools
import subprocess

from PIL import ImageFont

SCALE = 8  # Pixel pro Punkt bei der Vermessung (Genauigkeit)


@functools.lru_cache(maxsize=64)
def _font_file(family: str, bold: bool, mono: bool) -> str | None:
    pattern = "DejaVu Sans Mono" if mono else family
    pattern += ":weight=bold" if bold else ":weight=regular"
    try:
        out = subprocess.run(["fc-match", "-f", "%{file}", pattern], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except Exception:
        return None


@functools.lru_cache(maxsize=512)
def _font(family: str, size_pt: float, bold: bool, mono: bool):
    path = _font_file(family, bold, mono)
    try:
        f = ImageFont.truetype(path, int(size_pt * SCALE)) if path else ImageFont.load_default()
        if bold and path:
            try:  # Variable Fonts (z. B. Open Sans[wdth,wght])
                f.set_variation_by_name("Bold")
            except Exception:
                pass
        return f
    except Exception:
        return ImageFont.load_default()


class Measurer:
    def __init__(self, family: str = "Open Sans"):
        self.family = family or "Open Sans"

    def width(self, text: str, size: float, bold=False, mono=False) -> float:
        f = _font(self.family, size, bold, mono)
        try:
            return f.getlength(text) / SCALE
        except Exception:
            return len(text) * size * 0.55

    def line_height(self, size: float, mono=False) -> float:
        f = _font(self.family, size, False, mono)
        try:
            a, d = f.getmetrics()
            return max(1.17 * size, (a + d) / SCALE)
        except Exception:
            return 1.3 * size

    def count_lines(self, text: str, size: float, width_pt: float, bold=False, mono=False) -> int:
        total = 0
        for raw in (text or "").split("\n"):
            words = raw.split(" ")
            if not raw.strip():
                total += 1
                continue
            line = ""
            lines = 1
            for w in words:
                cand = (line + " " + w) if line else w
                if self.width(cand, size, bold, mono) <= width_pt:
                    line = cand
                    continue
                if not line:  # einzelnes, überlanges Wort -> hart umbrechen
                    chunk = ""
                    for ch in w:
                        if self.width(chunk + ch, size, bold, mono) > width_pt and chunk:
                            lines += 1
                            chunk = ch
                        else:
                            chunk += ch
                    line = chunk
                else:
                    lines += 1
                    line = w
                    while self.width(line, size, bold, mono) > width_pt and len(line) > 1:
                        # Wort länger als Zeile
                        cut = len(line)
                        while cut > 1 and self.width(line[:cut], size, bold, mono) > width_pt:
                            cut -= 1
                        line = line[cut:]
                        lines += 1
            total += lines
        return max(total, 1)

    def height(self, paragraphs: list[str], size: float, width_pt: float, bold=False, mono=False,
               space_after: float | None = None, line_spacing: float = 1.0) -> float:
        if space_after is None:
            space_after = size * 0.45
        lh = self.line_height(size, mono) * line_spacing
        h = 0.0
        for i, p in enumerate(paragraphs):
            h += self.count_lines(p, size, width_pt, bold, mono) * lh
            if i < len(paragraphs) - 1:
                h += space_after
        return h

    def longest_word(self, paragraphs, size, bold=False, mono=False) -> float:
        words = [w for p in paragraphs for w in str(p).replace("\n", " ").split(" ") if w]
        return max((self.width(w, size, bold, mono) for w in words), default=0.0)

    def fits(self, paragraphs, width_pt, height_pt, size, bold=False, mono=False, space_factor=0.45,
             line_spacing=1.0) -> bool:
        if not mono and self.longest_word(paragraphs, size, bold) > width_pt:
            return False  # kein Wort darf mitten im Wort umbrechen
        return self.height(paragraphs, size, width_pt, bold, mono, size * space_factor, line_spacing) <= height_pt

    def fit(self, paragraphs: list[str], width_pt: float, height_pt: float, sizes: list[float], bold=False,
            mono=False, space_factor: float = 0.45, line_spacing: float = 1.0):
        """Größte Schriftgröße aus `sizes`, die passt. Rückgabe (size, passt)."""
        for s in sizes:
            if self.fits(paragraphs, width_pt, height_pt, s, bold, mono, space_factor, line_spacing):
                return s, True
        return sizes[-1], False
