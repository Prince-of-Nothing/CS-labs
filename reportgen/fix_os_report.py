#!/usr/bin/env python3
"""Reformat resources/Lab3_PlesuDinu_FAF-241.docx (Operating Systems lab report)
to the documented UTM layout, keeping every word, table and screenshot intact:

  * A4; margins left 3 cm, right 1.5 cm, top/bottom 2 cm,
  * Times New Roman 12 pt body, justified, 1.5 line spacing, 1.25 cm indent,
  * clean heading sizes (H1 14 pt bold, H2 12 pt bold), Consolas 10 pt code,
  * figure captions renumbered Figure 1..N (in-text references stay in sync),
  * centred page number in the footer from page 2; the title page keeps its
    "Chisinau - 2026" footer line.

The script is idempotent: running it twice produces the same document.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
DOCX = ROOT / "resources" / "Lab3_PlesuDinu_FAF-241.docx"
FONT, MONO = "Times New Roman", "Consolas"

CAPTION_RE = re.compile(r"^Figure\s+\d+(?:\.\d+)?\s*[–—-]\s*")
NUMBER_RE = re.compile(r"Figure\s+(\d+(?:\.\d+)?)")


# ---------------------------------------------------------------- helpers
def set_run(run, name=FONT, size=12, bold=None, italic=None):
    """Font/size on a run (ascii + hAnsi + complex script), keep other flags."""
    run.font.name = name
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor(0, 0, 0)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rf.set(qn(attr), name)
    szcs = rpr.find(qn("w:szCs"))
    if szcs is None:
        szcs = OxmlElement("w:szCs")
        rpr.append(szcs)
    szcs.set(qn("w:val"), str(int(size * 2)))


def fmt(p, align, line15, before=0, after=0, first=None, left=None,
        keep_next=False, keep_together=False):
    pf = p.paragraph_format
    p.alignment = align
    pf.line_spacing_rule = (WD_LINE_SPACING.ONE_POINT_FIVE if line15
                            else WD_LINE_SPACING.SINGLE)
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.first_line_indent = Cm(first) if first is not None else Cm(0)
    pf.left_indent = Cm(left) if left is not None else Cm(0)
    pf.keep_with_next = keep_next
    pf.keep_together = keep_together


def has_drawing(p):
    return bool(p._p.findall(".//" + qn("w:drawing"))
                or p._p.findall(".//" + qn("w:pict")))


def is_page_break_para(p):
    if p.text.strip() or has_drawing(p):
        return False
    return any(br.get(qn("w:type")) == "page"
               for br in p._p.findall(".//" + qn("w:br")))


def is_mono(p):
    runs = [r for r in p.runs if r.text.strip()]
    return bool(runs) and all(r.font.name == MONO for r in runs)


def add_page_field(p):
    run = p.add_run()
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end")
    run._r.append(f1); run._r.append(instr); run._r.append(f2)
    set_run(run, size=11)


# ---------------------------------------------------------------- main
def main():
    doc = Document(DOCX)
    paras = doc.paragraphs

    original_texts = [p.text for p in paras]
    n_images = sum(1 for r in doc.part.rels.values() if "image" in r.reltype)

    # -- regions ----------------------------------------------------------
    breaks = [i for i, p in enumerate(paras) if is_page_break_para(p)]
    title_end = breaks[0] if breaks else -1          # paragraphs 0..title_end-1
    contents_head = next((i for i, p in enumerate(paras)
                          if p.text.strip() == "Contents"), None)
    contents_end = breaks[1] if len(breaks) > 1 else title_end

    # -- 1. page geometry -------------------------------------------------
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin, sec.right_margin = Cm(3.0), Cm(1.5)
    sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(2.0)

    # -- 2. styles & defaults --------------------------------------------
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = FONT, Pt(12)
    npf = normal.paragraph_format
    npf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    npf.space_before = Pt(0)
    npf.space_after = Pt(0)
    npf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for lvl, size in [(1, 14)] + [(k, 12) for k in range(2, 10)]:
        st = doc.styles[f"Heading {lvl}"]
        st.font.name, st.font.size = FONT, Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)

    dd = doc.styles.element.find(qn("w:docDefaults"))
    rpr = dd.find(qn("w:rPrDefault")).find(qn("w:rPr"))
    rf = rpr.find(qn("w:rFonts"))
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rf.set(qn(attr), FONT)
    for tag, val in (("w:sz", "24"), ("w:szCs", "24")):
        el = rpr.find(qn(tag))
        if el is None:
            el = OxmlElement(tag); rpr.append(el)
        el.set(qn("w:val"), val)
    ppr = dd.find(qn("w:pPrDefault")).find(qn("w:pPr"))
    sp = ppr.find(qn("w:spacing"))
    for attr, val in (("w:after", "0"), ("w:before", "0"),
                      ("w:line", "360"), ("w:lineRule", "auto")):
        sp.set(qn(attr), val)

    # -- 3. figure captions renumbered 1..N -------------------------------
    caption_idx, mapping, n = [], {}, 0
    for i, p in enumerate(paras):
        t = p.text.strip()
        m = CAPTION_RE.match(t)
        if not m:
            continue
        n += 1
        old_num = NUMBER_RE.match(m.group(0)).group(1)
        rest = t[len(m.group(0)):]
        new_text = f"Figure {n} – {rest}"
        mapping[f"Figure {old_num}"] = f"Figure {n}"
        caption_idx.append(i)
        if p.runs:                      # captions are single-run paragraphs
            p.runs[0].text = new_text
            for r in p.runs[1:]:
                r.text = ""
    print(f"captions renumbered: {n} (Figure 1..{n}); refs: {mapping}")

    # keep in-text references in sync
    for i, p in enumerate(paras):
        if i in caption_idx or "Figure" not in p.text:
            continue
        for r in p.runs:
            if "Figure" in r.text:
                r.text = NUMBER_RE.sub(
                    lambda m: mapping.get(f"Figure {m.group(1)}", m.group(0)),
                    r.text)

    # -- 4. paragraph formatting -----------------------------------------
    for i, p in enumerate(paras):
        text = p.text.strip()
        style = p.style.name if p.style else ""
        img = has_drawing(p)

        # title page
        if i < title_end:
            if img:
                fmt(p, WD_ALIGN_PARAGRAPH.CENTER, False, before=0, after=8)
                continue
            if not text:
                fmt(p, WD_ALIGN_PARAGRAPH.CENTER, False)
                continue
            spec = dict(size=12, bold=None, before=0, after=2)
            if text.startswith(("MINISTRY", "OF THE REPUBLIC")):
                spec.update(bold=True)
            elif text.startswith("Technical University"):
                spec.update(size=14, bold=True)
            elif text.startswith(("Faculty of", "Department of")):
                pass
            elif text.startswith("Report"):            # "Report" + discipline
                fmt(p, WD_ALIGN_PARAGRAPH.CENTER, False, after=4)
                for j, r in enumerate(p.runs):
                    set_run(r, size=(20 if j == 0 else 14),
                            bold=(None if j == 0 else True))
                continue
            elif text.startswith("Laboratory Work"):
                spec.update(size=14, after=4)
            elif text.startswith("Topic:"):
                spec.update(after=20)
            elif text.startswith("Checked by"):
                spec.update(after=2)
            if "FAF-" in text and "Ple" in text:        # student line
                spec.update(bold=True, after=6)
            fmt(p, WD_ALIGN_PARAGRAPH.CENTER, False,
                before=spec["before"], after=spec["after"])
            for r in p.runs:
                set_run(r, size=spec["size"], bold=spec["bold"])
            continue

        # contents block
        if i == contents_head:
            fmt(p, WD_ALIGN_PARAGRAPH.LEFT, True, after=6)
            for r in p.runs:
                set_run(r, size=14, bold=True)
            continue
        if contents_head is not None and title_end < i < contents_end:
            fmt(p, WD_ALIGN_PARAGRAPH.LEFT, True, after=2)
            for r in p.runs:
                set_run(r, size=12)
            continue

        # page-break / empty spacer paragraphs
        if not text and not img:
            fmt(p, WD_ALIGN_PARAGRAPH.LEFT, False)
            continue

        # headings
        if style in [f"Heading {k}" for k in range(1, 10)]:
            size = 14 if style == "Heading 1" else 12
            before, after = (12, 6) if size == 14 else (8, 4)
            fmt(p, WD_ALIGN_PARAGRAPH.LEFT, True, before=before, after=after,
                keep_next=True)
            for r in p.runs:
                set_run(r, size=size, bold=True)
            continue

        # code blocks (Consolas runs)
        if is_mono(p):
            fmt(p, WD_ALIGN_PARAGRAPH.LEFT, False, before=2, after=4, left=0.5,
                keep_next=True, keep_together=True)
            for r in p.runs:
                set_run(r, name=MONO, size=10)
            continue

        # screenshots
        if img:
            fmt(p, WD_ALIGN_PARAGRAPH.CENTER, False, before=6, after=2,
                keep_next=True)
            continue

        # captions
        if i in caption_idx or CAPTION_RE.match(text):
            fmt(p, WD_ALIGN_PARAGRAPH.CENTER, True, before=2, after=10,
                keep_together=True)
            for r in p.runs:
                set_run(r, size=11, italic=True)
            continue

        # ordinary text
        fmt(p, WD_ALIGN_PARAGRAPH.JUSTIFY, True, after=6, first=1.25)
        for r in p.runs:
            set_run(r, size=12)

    # -- 5. the prediction/observation table ------------------------------
    for table in doc.tables:
        grid = table._tbl.find(qn("w:tblGrid"))
        cols = grid.findall(qn("w:gridCol")) if grid is not None else []
        total = sum(int(c.get(qn("w:w"))) for c in cols)
        limit = Cm(16.5).twips
        factor = min(1.0, limit / total) if total else 1.0
        if factor < 1.0:
            for c in cols:
                c.set(qn("w:w"), str(int(int(c.get(qn("w:w"))) * factor)))
            for tr in table._tbl.findall(qn("w:tr")):
                for tc in tr.findall(qn("w:tc")):
                    tcw = tc.find(qn("w:tcPr")).find(qn("w:tcW"))
                    tcw.set(qn("w:w"), str(int(int(tcw.get(qn("w:w"))) * factor)))
        for ri, row in enumerate(table.rows):
            for cell in row.cells:
                for p in cell.paragraphs:
                    fmt(p, WD_ALIGN_PARAGRAPH.LEFT, False, after=2)
                    for r in p.runs:
                        set_run(r, size=10, bold=(True if ri == 0 else None))

    # -- 6. footer: page number from page 2, title page keeps its line ----
    old_footer_text = sec.footer.paragraphs[0].text or "Chi\u0219in\u0103u \u2013 2026"
    sec.different_first_page_header_footer = True

    fp = sec.first_page_footer.paragraphs[0]
    fp.text = ""
    fmt(fp, WD_ALIGN_PARAGRAPH.CENTER, False)
    set_run(fp.add_run(old_footer_text), size=11)

    df = sec.footer.paragraphs[0]
    for r in list(df.runs):
        r._r.getparent().remove(r._r)
    fmt(df, WD_ALIGN_PARAGRAPH.CENTER, False)
    add_page_field(df)

    doc.save(DOCX)
    print(f"saved {DOCX}")

    # -- 7. verification --------------------------------------------------
    d2 = Document(DOCX)
    ok = True

    def check(label, cond, detail=""):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'ok ' if cond else 'FAIL'}] {label}{(' — ' + str(detail)) if detail else ''}")

    s = d2.sections[0]
    check("margins 3/1.5/2/2",
          (round(s.left_margin.cm, 1), round(s.right_margin.cm, 1),
           round(s.top_margin.cm, 1), round(s.bottom_margin.cm, 1)) == (3.0, 1.5, 2.0, 2.0))
    check("page number in footer", "PAGE" in s.footer.paragraphs[0]._p.xml)
    check("title-page footer line", s.first_page_footer.paragraphs[0].text == old_footer_text)
    check("images intact",
          sum(1 for r in d2.part.rels.values() if "image" in r.reltype) == n_images)

    caps = [p.text for p in d2.paragraphs if CAPTION_RE.match(p.text.strip())]
    check("captions numbered 1..N",
          [c.split()[1] for c in caps] == [str(k) for k in range(1, len(caps) + 1)],
          f"{len(caps)} captions")
    check("no stale dotted figure refs",
          not any(re.search(r"Figure\s+\d+\.\d+", p.text) for p in d2.paragraphs))

    # text preservation: only caption renumbering and in-text figure
    # references (following the same mapping) may differ from the original
    def allowed(i, a, b):
        if i in caption_idx:
            return True
        remapped = NUMBER_RE.sub(
            lambda m: mapping.get(f"Figure {m.group(1)}", m.group(0)), a)
        return remapped == b

    diffs = [(i, a[:70], b[:70])
             for i, (a, b) in enumerate(zip(original_texts,
                                            [p.text for p in d2.paragraphs]))
             if a != b and not allowed(i, a, b)]
    check("no unintended text changes", not diffs, diffs)

    # no stray font sizes left
    bad = sorted({r.font.size.pt for p in d2.paragraphs for r in p.runs
                  if r.font.size and r.font.size.pt not in (20, 14, 12, 11, 10)})
    check("font sizes normalized", not bad, bad)

    print("VERIFICATION:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
