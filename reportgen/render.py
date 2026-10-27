#!/usr/bin/env python3
"""Render captured terminal sessions to PNG images that imitate real
screenshots (dark background, monospace font, coloured prompts/results).

Used by build_reports.py to embed program-run evidence into the Word reports.
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

# palette (VS Code "Dark+" flavoured)
BG = (30, 30, 30)
FG = (204, 204, 204)
CMD = (78, 201, 176)      # "$ ..." command lines
OK = (134, 219, 61)       # success markers
BAD = (224, 108, 117)     # error / invalid markers
DIM = (128, 128, 128)     # menu banners / separators
PROMPT = (86, 156, 214)   # interactive "> " and "Alegeti" lines

OK_WORDS = ("OK", "True", "CORECT", "VALIDA", "valida", "trecut", "identice")
BAD_WORDS = ("Invalid", "invalid", "GRESIT", "ERROR", "Error", "AssertionError")


def _style(line: str):
    """Pick a colour for a whole line based on simple heuristics."""
    stripped = line.strip()
    if stripped.startswith("$ "):
        return CMD
    if stripped.startswith("> ") or stripped.startswith("Alegeti") or \
       "Alegeti optiunea" in line or stripped.startswith("Optiunea ("):
        return PROMPT
    if any(w in line for w in BAD_WORDS):
        return BAD
    if any(w in line for w in OK_WORDS):
        return OK
    if stripped.startswith("=" * 10) or stripped.startswith("Optiuni:") or \
       stripped.startswith("LUCRAREA") or stripped.startswith("---"):
        return DIM
    return FG


def render_terminal(lines, out_png, max_cols=104, font_size=15,
                    pad=14, line_gap=3, wrap=True, title=None):
    """Render *lines* (a list of strings) into a terminal-looking PNG."""
    font = ImageFont.truetype(FONT_PATH, font_size)
    bold = ImageFont.truetype(FONT_BOLD, font_size)
    # width of a single monospace character
    cw = font.getbbox("M")[2] - font.getbbox("M")[0]
    ch = font.getbbox("Mg")[3] - font.getbbox("Mg")[1]

    # wrap overly long lines so the image stays a sane width
    out = []
    for raw in lines:
        raw = raw.rstrip("\n").replace("\t", "    ")
        if wrap and len(raw) > max_cols:
            while len(raw) > max_cols:
                out.append(raw[:max_cols])
                raw = raw[max_cols:]
            out.append(raw)
        else:
            out.append(raw)
    lines = out

    cols = max((len(l) for l in lines), default=1)
    cols = max(cols, 20)
    img_w = cols * cw + 2 * pad
    img_h = len(lines) * (ch + line_gap) + 2 * pad + (26 if title else 0)
    img = Image.new("RGB", (img_w, img_h), BG)
    draw = ImageDraw.Draw(img)

    y = pad
    if title:
        draw.rectangle([0, 0, img_w, 26], fill=(60, 60, 60))
        # window controls
        for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            cx = pad + i * 18
            draw.ellipse([cx, 8, cx + 10, 18], fill=col)
        draw.text((pad + 60, 6), title, font=font, fill=(220, 220, 220))
        y = 26 + pad

    for line in lines:
        colour = _style(line)
        f = bold if line.strip().startswith("$ ") else font
        if line:
            draw.text((pad, y), line, font=f, fill=colour)
        y += ch + line_gap

    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    img.save(out_png)
    return out_png


def render_excerpt(text, out_png, start=None, end=None, max_lines=None, **kw):
    """Render *text* (a big captured string), optionally slicing from the line
    containing *start* up to (and including) the line containing *end*, and
    optionally capping the result to *max_lines* rows."""
    lines = text.splitlines()
    if start is not None:
        for i, l in enumerate(lines):
            if start in l:
                lines = lines[i:]
                break
    if end is not None:
        for i, l in enumerate(lines):
            if end in l:
                lines = lines[: i + 1]
                break
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines] + ["\u2026 (\u00eencerere trunchiat\u0103 pentru raport)"]
    return render_terminal(lines, out_png, **kw)


if __name__ == "__main__":
    import sys
    src = open(sys.argv[1], encoding="utf-8").read()
    render_terminal(src.splitlines(), sys.argv[2])
    print("wrote", sys.argv[2])
