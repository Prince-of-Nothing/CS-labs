#!/usr/bin/env python3
"""Helpers to build UTM/FCIM-style laboratory reports as .docx files.

Layout follows the documented UTM template requirements:
  * A4 page, Times New Roman 12 pt, line spacing 1.5,
  * margins: left 3 cm, right 1.5 cm, top 2 cm, bottom 2 cm,
  * centred page number in the footer.
"""
from __future__ import annotations

import os

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

FONT = "Times New Roman"
MONO = "Consolas"


def _set_run(run, size=12, bold=False, italic=False, name=FONT, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = RGBColor(*color)
    # make the font apply to East-Asian text too
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:cs"), name)


def new_document():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.left_margin = Cm(3.0)
    sec.right_margin = Cm(1.5)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(12)
    pf = normal.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(0)
    pf.space_before = Pt(0)

    # Section titles must carry real Heading styles, otherwise a TOC field
    # would find no outline level and Word would build an empty index.
    _style_heading(doc, "Heading 1")
    _style_heading(doc, "Heading 2")
    ensure_hyperlink_style(doc)
    doc._toc_entries = []
    return doc


def _style_heading(doc, name):
    """Reskin Word's built-in heading styles as UTM section titles.

    Without this, applying the style would turn every section title into
    the default blue Calibri; the reports must stay Times New Roman 12 pt
    bold and black while still registering as outline level 1/2.
    """
    try:
        st = doc.styles[name]
    except KeyError:
        return
    st.font.name = FONT
    st.font.size = Pt(12)
    st.font.bold = True
    st.font.italic = False
    st.font.color.rgb = RGBColor(0, 0, 0)
    hpf = st.paragraph_format
    hpf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    hpf.space_before = Pt(10)
    hpf.space_after = Pt(6)
    hpf.first_line_indent = Cm(0)
    hpf.keep_with_next = True


def ensure_hyperlink_style(doc):
    """Make sure the character style 'Hyperlink' exists.

    Word expects w:rStyle w:val="Hyperlink" on hyperlink runs; python-docx's
    blank template does not define it, so links would lose their formatting.
    """
    try:
        doc.styles["Hyperlink"]
        return
    except KeyError:
        pass
    st = doc.styles.add_style("Hyperlink", WD_STYLE_TYPE.CHARACTER)
    st.font.color.rgb = RGBColor(0x06, 0x45, 0xAD)
    st.font.underline = True


def _add_page_field(paragraph):
    """Insert a centred PAGE field into the footer."""
    run = paragraph.add_run()
    f1 = OxmlElement("w:fldChar")
    f1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    f2 = OxmlElement("w:fldChar")
    f2.set(qn("w:fldCharType"), "end")
    run._r.append(f1)
    run._r.append(instr)
    run._r.append(f2)
    _set_run(run, size=11)


def add_page_numbers(doc):
    footer = doc.sections[0].footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _add_page_field(p)


def para(doc, text="", size=12, bold=False, italic=False, align="justify",
         first_indent=1.25, space_after=6, name=FONT, color=None):
    p = doc.add_paragraph()
    amap = {
        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }
    p.alignment = amap[align]
    if first_indent is not None:
        p.paragraph_format.first_line_indent = Cm(first_indent)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    if text:
        r = p.add_run(text)
        _set_run(r, size=size, bold=bold, italic=italic, name=name, color=color)
    return p


def heading(doc, text, level=1):
    p = doc.add_paragraph(style="Heading %d" % level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if level > 1 else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    r = p.add_run(text)
    _set_run(r, size=12, bold=True)

    # Bookmark the heading so the TOC entries can link to it, and remember
    # the entry for insert_toc().
    entries = getattr(doc, "_toc_entries", None)
    if entries is None:
        entries = []
        doc._toc_entries = entries
    n = len(entries) + 1
    # Deliberately not named _Toc*: Word creates and owns that namespace when
    # it rebuilds the index, and a clash could break the generated links.
    name = "_Sec%03d" % n
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(n))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(n))
    ppr = p._p.pPr
    p._p.insert(list(p._p).index(ppr) + 1 if ppr is not None else 0, start)
    p._p.append(end)
    entries.append({"level": level, "text": text, "name": name})
    return p


def _field_start(p):
    """Begin a complex field: fldChar begin (dirty) + instruction + separate."""
    r = p.add_run()
    f = OxmlElement("w:fldChar")
    f.set(qn("w:fldCharType"), "begin")
    f.set(qn("w:dirty"), "true")   # Word rebuilds the index on open
    r._r.append(f)
    r2 = p.add_run()
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = ' TOC \\o "1-2" \\h \\z \\u '
    r2._r.append(it)
    r3 = p.add_run()
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    r3._r.append(sep)


def _field_end(p):
    r = p.add_run()
    f = OxmlElement("w:fldChar")
    f.set(qn("w:fldCharType"), "end")
    r._r.append(f)


def _hyperlink(p, text, anchor):
    """Append an internal (w:anchor) hyperlink run to a paragraph."""
    link = OxmlElement("w:hyperlink")
    link.set(qn("w:anchor"), anchor)
    link.set(qn("w:history"), "1")
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    rs = OxmlElement("w:rStyle")
    rs.set(qn("w:val"), "Hyperlink")
    rpr.append(rs)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)
    link.append(r)
    p._p.append(link)


def external_hyperlink(doc, p, url, font=None, size=None):
    """Append a clickable external link run to a paragraph.

    font/size keep a URL looking exactly like the styled run it replaces
    (the template prints the repository address in Consolas).
    """
    ensure_hyperlink_style(doc)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), p.part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/"
        "relationships/hyperlink",
        is_external=True))
    link.set(qn("w:history"), "1")
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    rs = OxmlElement("w:rStyle")
    rs.set(qn("w:val"), "Hyperlink")
    rpr.append(rs)
    if font:
        rf = OxmlElement("w:rFonts")
        rf.set(qn("w:ascii"), font)
        rf.set(qn("w:hAnsi"), font)
        rpr.append(rf)
    if size:
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), str(int(size * 2)))   # half-points
        rpr.append(sz)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = url
    r.append(t)
    link.append(r)
    p._p.append(link)


def set_update_fields(doc):
    """Mark the file so Word refreshes fields (TOC and PAGE) when opened."""
    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is not None:
        return
    el = OxmlElement("w:updateFields")
    el.set(qn("w:val"), "true")
    compat = settings.find(qn("w:compat"))
    if compat is not None:
        compat.addprevious(el)   # keeps ECMA-376 element order
    else:
        settings.append(el)


def insert_toc(doc, title="Table of Contents"):
    """Insert a real table of contents in front of the first section title.

    The index is a genuine 'TOC \\o "1-2" \\h \\z \\u' field flagged
    w:dirty, and the file asks Word for w:updateFields, so page numbers are
    written by Word itself instead of being hard-coded here (where they would
    silently go stale). The cached entries carry only the linked section
    titles, so the index is readable and clickable even before Word refreshes
    it - the numbers a PDF renderer shows next to them are page footers.
    """
    entries = list(getattr(doc, "_toc_entries", []))
    target = next((p for p in doc.paragraphs
                   if p.style is not None
                   and p.style.name in ("Heading 1", "Heading 2")), None)
    if not entries or target is None:
        return None

    # Title paragraph: deliberately NOT a heading, so the index cannot list
    # itself.
    tp = doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    tp.paragraph_format.first_line_indent = Cm(0)
    tp.paragraph_format.space_before = Pt(10)
    tp.paragraph_format.space_after = Pt(6)
    tp.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    tp.paragraph_format.keep_with_next = True
    tr = tp.add_run(title)
    _set_run(tr, size=14, bold=True)

    paras = [tp]
    for i, e in enumerate(entries):
        p = doc.add_paragraph()
        epf = p.paragraph_format
        epf.first_line_indent = Cm(0)
        epf.left_indent = Cm(0 if e["level"] == 1 else 0.75)
        epf.space_before = Pt(0)
        epf.space_after = Pt(2)
        epf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        if i == 0:
            _field_start(p)
        _hyperlink(p, e["text"], e["name"])
        if i == len(entries) - 1:
            _field_end(p)
        paras.append(p)

    # The index occupies its own page, as in the reference report: the
    # break sits outside the field so Word keeps it when rebuilding the
    # index, and section 1 starts on a fresh page.
    br = doc.add_paragraph()
    br.paragraph_format.first_line_indent = Cm(0)
    br.paragraph_format.space_after = Pt(0)
    br.add_run().add_break(WD_BREAK.PAGE)
    paras.append(br)

    for p in paras:                      # stack them in front of section 1
        target._p.addprevious(p._p)
    set_update_fields(doc)
    return tp


def code_block(doc, lines, size=10):
    """Monospaced, single-spaced, indented code fragment."""
    for i, line in enumerate(lines):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.left_indent = Cm(0.5)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        r = p.add_run(line.rstrip("\n") if line else "")
        _set_run(r, size=size, name=MONO)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run(text)
    _set_run(r, size=11, italic=True)


def add_image(doc, path, width_cm=16.0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(path, width=Cm(width_cm))


_HERE = os.path.dirname(os.path.abspath(__file__))
UTM_LOGO = os.path.join(_HERE, "img", "utm_logo.jpeg")


def title_page(doc, lab_no, topic, group="FAF-241"):
    """Title page laid out like the reference report in resources/:
    UTM logo, two-line ministry header, university / faculty / department,
    the student's name and group in bold, a large 'Report / discipline'
    block, the laboratory number and topic, and the supervisor block."""
    def line(text, size=12, bold=False, align="center", space=2):
        p = doc.add_paragraph()
        p.alignment = {
            "center": WD_ALIGN_PARAGRAPH.CENTER,
            "left": WD_ALIGN_PARAGRAPH.LEFT,
        }[align]
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_after = Pt(space)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        r = p.add_run(text)
        _set_run(r, size=size, bold=bold)
        return p

    # UTM logo, centred at the very top (same size as the reference)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(8)
    p.add_run().add_picture(UTM_LOGO, width=Cm(3.3))

    line("MINISTRY OF EDUCATION, CULTURE AND RESEARCH", 12, True, space=2)
    line("OF THE REPUBLIC OF MOLDOVA", 12, True, space=2)
    line("Technical University of Moldova", 14, True, space=2)
    line("Faculty of Computers, Informatics and Microelectronics", 12, False, space=2)
    line("Department of Computer Science and Information Technologies", 12, False, space=2)

    line("%s   %s" % ("Dinu Plesu", group), 12, True, space=6)

    # Large two-line block: "Report" (20 pt) over the discipline (14 pt bold)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    r = p.add_run("Report\n\t")
    _set_run(r, size=20)
    r = p.add_run("Cryptography and Security")
    _set_run(r, size=14, bold=True)

    line("Laboratory Work No. %d" % lab_no, 14, False, space=4)
    line("Topic: %s" % topic, 12, False, space=20)

    line("Checked by: Maia Zaica", 12, False, space=2)

    # Footer of the title page only (as in the reference report): the place
    # and year are centred at the bottom of page 1, and the PAGE field is
    # suppressed there; numbered pages start from the body of the report.
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    fp = section.first_page_footer
    p = fp.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run("Chi\u0219in\u0103u \u2013 2026")
    _set_run(r, size=12)

    doc.add_page_break()


def references(doc, items):
    heading(doc, "References")
    for i, it in enumerate(items, 1):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.left_indent = Cm(0.5)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        r = p.add_run("%d. %s" % (i, it))
        _set_run(r, size=12)


def source_code(doc, url):
    heading(doc, "Source Code")
    para(doc, "The complete source code of all laboratory works (Go sources for "
              "Labs 1\u20133, Python sources for Labs 4\u20136, together with the "
              "ciphertext and plaintext files used in Lab 2 and Lab 6) is available "
              "in the GitHub repository:", first_indent=1.25)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(6)
    external_hyperlink(doc, p, url, font=MONO, size=12)
