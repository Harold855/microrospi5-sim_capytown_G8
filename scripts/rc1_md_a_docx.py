#!/usr/bin/env python3
"""rc1_md_a_docx — convierte un .md del grupo en .docx (pandoc) y le da formato legible: márgenes de 2 cm,
tablas con bordes y encabezado sombreado, letra más pequeña en tablas y código.

Uso:   python3 scripts/rc1_md_a_docx.py docs/rc1_g8/funcionamiento_rc1.md
Salida: el mismo nombre con extensión .docx, junto al .md.
Requiere: pandoc y python-docx.
"""
import os
import subprocess
import sys

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


def bordes(tabla):
    tblPr = tabla._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:space"), "0"); e.set(qn("w:color"), "9AA5B1")
        b.append(e)
    tblPr.append(b)


def sombrear(celda, color="DCE9F2"):
    tcPr = celda._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), color)
    tcPr.append(sh)


def main(md):
    docx = os.path.splitext(md)[0] + ".docx"
    subprocess.run(["pandoc", md, "-o", docx, "--resource-path", os.path.dirname(md) or ".",
                    "--standalone"], check=True)
    d = Document(docx)
    for s in d.sections:
        s.left_margin = s.right_margin = Cm(2.0)
        s.top_margin = s.bottom_margin = Cm(2.0)
    for nombre, tam in (("Normal", 10), ("Body Text", 10), ("First Paragraph", 10), ("Compact", 9)):
        try:
            d.styles[nombre].font.size = Pt(tam)
        except KeyError:
            pass
    for t in d.tables:
        bordes(t)
        for i, fila in enumerate(t.rows):
            for c in fila.cells:
                if i == 0:
                    sombrear(c)
                for p in c.paragraphs:
                    for r in p.runs:
                        r.font.size = Pt(8.5)
                        if i == 0:
                            r.font.bold = True
    for p in d.paragraphs:
        if p.style.name in ("Source Code",):
            for r in p.runs:
                r.font.size = Pt(8)
    d.save(docx)
    print(docx)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
