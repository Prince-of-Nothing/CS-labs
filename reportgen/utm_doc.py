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
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
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
    return doc


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
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if level > 1 else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    r = p.add_run(text)
    _set_run(r, size=12, bold=True)
    return p


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
    r = p.add_run(url)
    _set_run(r, size=12, name=MONO, color=(0x06, 0x45, 0xAD))
