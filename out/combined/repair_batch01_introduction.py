#!/usr/bin/env python3
"""Repair measured text-fit/font issues on Fall Introduction candidate slide 2.

The LibreOffice import substitutes the source BebasNeue labels and makes the
Who/Where/When text boxes wrap into overlapping lines. Its instructor block
also extends beneath the right-side portraits. This repair uses standard
Arial text, larger label boxes, and a narrower content box; pictures and all
body text remain editable. It also replaces the inherited "Depths of Winter"
phrase with the verified Fall 2026 term in the current syllabus. The script
fails closed if the expected source text is not
found exactly once.

Example:
  python3 out/combined/repair_batch01_introduction.py \
    --input out/.build/batch-01/source-pptx/01-408st-introduction.pptx \
    --output out/.build/batch-01/source-pptx/01-408st-introduction-repaired.pptx
"""

from __future__ import annotations

import argparse
import posixpath
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"p": P, "a": A, "r": R, "rel": REL}
EMU = 12_700


def presentation_order(parts: dict[str, bytes]) -> list[str]:
    pres = etree.fromstring(parts["ppt/presentation.xml"])
    rels = etree.fromstring(parts["ppt/_rels/presentation.xml.rels"])
    targets = {
        rel.get("Id"): rel.get("Target")
        for rel in rels.findall("rel:Relationship", NS)
    }
    result = []
    for node in pres.findall("p:sldIdLst/p:sldId", NS):
        target = targets[node.get(f"{{{R}}}id")]
        result.append(posixpath.normpath(posixpath.join("ppt", target)))
    return result


def set_bounds(shape: etree._Element, x: float, y: float, width: float, height: float) -> None:
    xfrm = shape.find("./p:spPr/a:xfrm", NS)
    if xfrm is None:
        raise ValueError("target text shape has no transform")
    off = xfrm.find("./a:off", NS)
    ext = xfrm.find("./a:ext", NS)
    if off is None or ext is None:
        raise ValueError("target text shape has incomplete geometry")
    off.set("x", str(round(x * EMU)))
    off.set("y", str(round(y * EMU)))
    ext.set("cx", str(round(width * EMU)))
    ext.set("cy", str(round(height * EMU)))


def find_text_shape(root: etree._Element, predicate, label: str) -> etree._Element:
    matches = []
    for shape in root.findall(".//p:sp", NS):
        # LibreOffice can preserve one visible label as multiple DrawingML runs
        # (for example ``Here`` + `` (+ Brightspace)``). Match the rendered
        # text, not the internal run boundaries.
        text = "".join(shape.xpath(".//a:t/text()", namespaces=NS)).strip()
        if predicate(text):
            matches.append(shape)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {label} text shape; found {len(matches)}")
    return matches[0]


def repair_label(shape: etree._Element, text: str) -> None:
    paragraph = shape.find("./p:txBody/a:p", NS)
    if paragraph is None:
        raise ValueError(f"label {text!r} has no paragraph")
    paragraph_props = paragraph.find("./a:pPr", NS)
    if paragraph_props is None:
        paragraph_props = etree.Element(f"{{{A}}}pPr")
        paragraph.insert(0, paragraph_props)
    paragraph_props.set("algn", "l")
    runs = paragraph.findall("./a:r", NS)
    if not runs:
        raise ValueError(f"label {text!r} has no editable text run")
    first = runs[0]
    text_node = first.find("./a:t", NS)
    if text_node is None:
        raise ValueError(f"label {text!r} has no text node")
    text_node.text = text
    for extra in runs[1:]:
        paragraph.remove(extra)
    rpr = first.find("./a:rPr", NS)
    if rpr is None:
        raise ValueError(f"label {text!r} has no run style")
    rpr.set("sz", "3200")
    rpr.set("b", "1")
    for tag in ("latin", "ea", "cs"):
        font = rpr.find(f"./a:{tag}", NS)
        if font is None:
            font = etree.SubElement(rpr, f"{{{A}}}{tag}")
        font.set("typeface", "Arial")
    end = paragraph.find("./a:endParaRPr", NS)
    if end is not None:
        end.set("sz", "3200")
        end.set("b", "1")
        font = end.find("./a:latin", NS)
        if font is None:
            font = etree.SubElement(end, f"{{{A}}}latin")
        font.set("typeface", "Arial")
    body = shape.find("./p:txBody/a:bodyPr", NS)
    if body is not None:
        for key in ("lIns", "rIns", "tIns", "bIns"):
            body.set(key, "0")
        body.set("anchor", "ctr")


def repair(pptx_in: Path, pptx_out: Path) -> None:
    with ZipFile(pptx_in) as archive:
        parts = {item.filename: archive.read(item.filename) for item in archive.infolist()}
    order = presentation_order(parts)
    if len(order) < 3:
        raise ValueError("Introduction candidate has fewer than three slides")
    slide_part = order[2]
    root = etree.fromstring(parts[slide_part])

    content = find_text_shape(root, lambda text: text.startswith("Instructor"), "instructor/admin block")
    set_bounds(content, 285, 247, 475, 365)
    body = content.find("./p:txBody/a:bodyPr", NS)
    if body is not None:
        for key in ("lIns", "rIns"):
            body.set(key, "0")
    # LibreOffice's Bebas Neue substitution makes the original 34 pt body run
    # substantially wider than the reference. At 475 pt, 28 pt keeps the
    # office-hours sentence on one line and prevents the final TA-hours line
    # from spilling into the separate WHERE/WHEN rows.
    for run in content.findall(".//a:rPr", NS) + content.findall(".//a:defRPr", NS) + content.findall(".//a:endParaRPr", NS):
        if int(run.get("sz", "0")) > 2800:
            run.set("sz", "2800")

    labels = [
        ("Who:", "WHO:", (280, 185, 155, 62)),
        ("WhEre:", "WHERE:", (28, 610, 165, 62)),
        ("When:", "WHEN:", (28, 681, 150, 62)),
    ]
    for old, new, bounds in labels:
        shape = find_text_shape(root, lambda text, old=old: text == old, old)
        repair_label(shape, new)
        set_bounds(shape, *bounds)

    for exact, replacement, bounds in (
        ("Here (+ Brightspace)", "Here (+ Brightspace)", (190, 610, 780, 65)),
        ("Now - Depths of Winter", "Fall 2026", (190, 681, 780, 65)),
    ):
        shape = find_text_shape(root, lambda text, exact=exact: text == exact, exact)
        text_nodes = shape.findall(".//a:t", NS)
        if not text_nodes:
            raise ValueError(f"{exact!r} text shape has no editable text")
        text_nodes[0].text = replacement
        for extra in text_nodes[1:]:
            extra.text = ""
        set_bounds(shape, *bounds)
        paragraph = shape.find("./p:txBody/a:p", NS)
        if paragraph is not None:
            paragraph_props = paragraph.find("./a:pPr", NS)
            if paragraph_props is None:
                paragraph_props = etree.Element(f"{{{A}}}pPr")
                paragraph.insert(0, paragraph_props)
            paragraph_props.set("algn", "l")
        for run in shape.findall(".//a:rPr", NS) + shape.findall(".//a:defRPr", NS):
            if int(run.get("sz", "0")) > 3600:
                run.set("sz", "3600")
        for end in shape.findall(".//a:endParaRPr", NS):
            if int(end.get("sz", "0")) > 3600:
                end.set("sz", "3600")

    parts[slide_part] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    pptx_out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(pptx_out, "w", ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            archive.writestr(name, data)
    with ZipFile(pptx_out) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"repaired PPTX has corrupt ZIP member {bad}")
    print(f"Repaired editable text layout on source page 2: {pptx_out}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repair(args.input, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
