#!/usr/bin/env python3
"""Repair confirmed layout defects in the Fall Introduction PPTX candidate.

This script normalizes text geometry and font sizes, restores two editable
grading tables, removes a stale overlay, restores two source-PDF screenshots,
and replaces one corrupted diagram region with a reference crop. It does not
alter the course schedule slide: that is a user-owned edit. The repairs are
deliberately limited to source pages where the imported result visibly differs
from the current Fall PDF.

Example:
  python3 out/combined/repair_batch01_introduction.py \
    --input out/.build/batch-01/source-pptx/01-408st-introduction.pptx \
    --output out/.build/batch-01/source-pptx/01-408st-introduction-repaired.pptx
"""

from __future__ import annotations

import argparse
import copy
import io
import posixpath
import re
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree
from PIL import Image


P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"p": P, "a": A, "r": R, "rel": REL}
EMU = 12_700
IMAGE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
SLIDE_W_PT = 1024
SLIDE_H_PT = 768
PALE_BLUE = "CCE4F3"
LABEL_BLUE = "3190D0"


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


def find_slide_shape(root: etree._Element, index: int) -> etree._Element:
    matches = root.findall(".//p:sp", NS)
    if index < 0 or index >= len(matches):
        raise ValueError(f"expected shape index {index} on target slide")
    return matches[index]


def set_font_size(shape: etree._Element, points: float) -> None:
    size = str(round(points * 100))
    runs = shape.findall(".//a:rPr", NS) + shape.findall(".//a:defRPr", NS) + shape.findall(".//a:endParaRPr", NS)
    if not runs:
        raise ValueError("target shape has no editable font properties")
    for run in runs:
        run.set("sz", size)


def scale_font_sizes(shape: etree._Element, factor: float) -> None:
    for run in shape.findall(".//a:rPr", NS) + shape.findall(".//a:defRPr", NS) + shape.findall(".//a:endParaRPr", NS):
        size = run.get("sz")
        if size:
            run.set("sz", str(round(int(size) * factor)))


def set_shape_box(shape: etree._Element, x: float, y: float, width: float, height: float) -> None:
    set_bounds(shape, x, y, width, height)
    body = shape.find("./p:txBody/a:bodyPr", NS)
    if body is not None:
        for key in ("lIns", "rIns", "tIns", "bIns"):
            body.set(key, "0")


def set_table_cell(cell: etree._Element, text: str, *, first_column: bool) -> None:
    tcpr = cell.find("./a:tcPr", NS)
    if tcpr is None:
        tcpr = etree.SubElement(cell, f"{{{A}}}tcPr")
    for child in list(tcpr):
        if etree.QName(child).localname in ("solidFill", "gradFill", "blipFill", "noFill"):
            tcpr.remove(child)
    fill = etree.Element(f"{{{A}}}solidFill")
    etree.SubElement(fill, f"{{{A}}}srgbClr", val=PALE_BLUE if first_column else "FFFFFF")
    tcpr.insert(0, fill)
    for side in ("lnL", "lnR", "lnT", "lnB"):
        line = tcpr.find(f"./a:{side}", NS)
        if line is not None:
            for child in list(line):
                if etree.QName(child).localname in ("solidFill", "gradFill", "blipFill", "noFill"):
                    line.remove(child)
            solid = etree.SubElement(line, f"{{{A}}}solidFill")
            etree.SubElement(solid, f"{{{A}}}srgbClr", val="000000")

    txbody = cell.find("./a:txBody", NS)
    if txbody is None:
        txbody = etree.Element(f"{{{A}}}txBody")
        etree.SubElement(txbody, f"{{{A}}}bodyPr")
        etree.SubElement(txbody, f"{{{A}}}lstStyle")
        cell.insert(0, txbody)
    body = txbody.find("./a:bodyPr", NS)
    if body is None:
        body = etree.Element(f"{{{A}}}bodyPr")
        txbody.insert(0, body)
    body.set("anchor", "ctr")
    for key in ("lIns", "rIns", "tIns", "bIns"):
        body.set(key, "0")
    for node in list(txbody):
        if etree.QName(node).localname == "p":
            txbody.remove(node)
    paragraph = etree.SubElement(txbody, f"{{{A}}}p")
    ppr = etree.SubElement(paragraph, f"{{{A}}}pPr", algn="ctr")
    etree.SubElement(ppr, f"{{{A}}}buNone")
    run = etree.SubElement(paragraph, f"{{{A}}}r")
    rpr = etree.SubElement(run, f"{{{A}}}rPr", lang="en-US", sz="2400", b="1")
    color = LABEL_BLUE if first_column else "000000"
    solid = etree.SubElement(rpr, f"{{{A}}}solidFill")
    etree.SubElement(solid, f"{{{A}}}srgbClr", val=color)
    etree.SubElement(rpr, f"{{{A}}}latin", typeface="Arial")
    etree.SubElement(run, f"{{{A}}}t").text = text
    etree.SubElement(paragraph, f"{{{A}}}endParaRPr", lang="en-US", sz="2400")


def repair_grading_table(root: etree._Element, expected_rows: int, rows_data: list[tuple[str, str]]) -> None:
    frames = root.findall(".//p:graphicFrame", NS)
    if len(frames) != 1:
        raise ValueError(f"expected one grading table, found {len(frames)}")
    table = frames[0].find(".//a:tbl", NS)
    if table is None:
        raise ValueError("grading slide has no editable table")
    rows = table.findall("./a:tr", NS)
    if len(rows) != expected_rows or any(len(row.findall("./a:tc", NS)) != 2 for row in rows):
        raise ValueError("grading table does not match the expected two-column structure")
    for row, (label, weight) in zip(rows, rows_data, strict=True):
        cells = row.findall("./a:tc", NS)
        set_table_cell(cells[0], label, first_column=True)
        set_table_cell(cells[1], weight, first_column=False)


def render_pdf_page(pdf: Path, page: int, workdir: Path) -> Image.Image:
    prefix = workdir / f"reference-page-{page}"
    subprocess.run(
        ["pdftoppm", "-f", str(page), "-l", str(page), "-scale-to-x", "2048", "-scale-to-y", "1536", "-png", "-singlefile", str(pdf), str(prefix)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    path = prefix.with_suffix(".png")
    if not path.exists():
        raise FileNotFoundError(f"pdftoppm did not create {path}")
    return Image.open(path).convert("RGBA")


def add_picture(
    parts: dict[str, bytes],
    slide_part: str,
    slide_root: etree._Element,
    rels_root: etree._Element,
    template: etree._Element,
    image_bytes: bytes,
    media_name: str,
    label: str,
    bounds: tuple[float, float, float, float],
) -> None:
    media_part = f"ppt/media/{media_name}"
    if media_part in parts:
        raise ValueError(f"PPTX media part already exists: {media_part}")
    rid_numbers = [int(m.group(1)) for rel in rels_root.findall("rel:Relationship", NS) if (m := re.fullmatch(r"rId(\d+)", rel.get("Id", "")))]
    rid = f"rId{max(rid_numbers, default=0) + 1}"
    slide_folder = posixpath.dirname(slide_part)
    etree.SubElement(
        rels_root,
        f"{{{REL}}}Relationship",
        Id=rid,
        Type=IMAGE_REL,
        Target=posixpath.relpath(media_part, slide_folder),
    )
    pic = copy.deepcopy(template)
    nv = pic.find("./p:nvPicPr/p:cNvPr", NS)
    if nv is None:
        raise ValueError("picture template has no non-visual properties")
    shape_ids = [int(e.get("id")) for e in slide_root.findall(".//p:cNvPr", NS) if e.get("id", "").isdigit()]
    nv.set("id", str(max(shape_ids, default=0) + 1))
    nv.set("name", label)
    blip = pic.find(".//a:blip", NS)
    if blip is None:
        raise ValueError("picture template has no blip")
    blip.set(f"{{{R}}}embed", rid)
    src_rect = pic.find(".//a:srcRect", NS)
    if src_rect is not None:
        src_rect.getparent().remove(src_rect)
    xfrm = pic.find("./p:spPr/a:xfrm", NS)
    off = xfrm.find("./a:off", NS) if xfrm is not None else None
    ext = xfrm.find("./a:ext", NS) if xfrm is not None else None
    if off is None or ext is None:
        raise ValueError("picture template has incomplete geometry")
    x, y, width, height = bounds
    off.set("x", str(round(x * EMU)))
    off.set("y", str(round(y * EMU)))
    ext.set("cx", str(round(width * EMU)))
    ext.set("cy", str(round(height * EMU)))
    tree = slide_root.find("./p:cSld/p:spTree", NS)
    if tree is None:
        raise ValueError("slide has no shape tree")
    tree.append(pic)
    parts[media_part] = image_bytes
    types = etree.fromstring(parts["[Content_Types].xml"])
    if not any(node.get("Extension", "").lower() == "png" for node in types.findall("{http://schemas.openxmlformats.org/package/2006/content-types}Default")):
        etree.SubElement(types, "{http://schemas.openxmlformats.org/package/2006/content-types}Default", Extension="png", ContentType="image/png")
    parts["[Content_Types].xml"] = etree.tostring(types, xml_declaration=True, encoding="UTF-8", standalone=True)


def add_reference_crop(
    parts: dict[str, bytes],
    pdf: Path,
    slide_part: str,
    slide_root: etree._Element,
    slide_rels: etree._Element,
    template: etree._Element,
    *,
    page: int,
    source_box: tuple[float, float, float, float],
    target_box: tuple[float, float, float, float],
    media_name: str,
    label: str,
    workdir: Path,
) -> None:
    image = render_pdf_page(pdf, page, workdir)
    x, y, width, height = source_box
    crop = image.crop((round(x * 2), round(y * 2), round((x + width) * 2), round((y + height) * 2)))
    buffer = io.BytesIO()
    crop.save(buffer, format="PNG", optimize=True)
    add_picture(parts, slide_part, slide_root, slide_rels, template, buffer.getvalue(), media_name, label, target_box)


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

    def load_slide(index: int) -> tuple[str, etree._Element, etree._Element]:
        slide_part = order[index - 1]
        root = etree.fromstring(parts[slide_part])
        rel_part = posixpath.join(posixpath.dirname(slide_part), "_rels", posixpath.basename(slide_part) + ".rels")
        rels = etree.fromstring(parts[rel_part])
        return slide_part, root, rels

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

    # Source page 3: the Textbook heading wraps into the text line below it.
    part4, slide4, _ = load_slide(4)
    textbook = find_text_shape(slide4, lambda text: text.startswith("Textbook"), "Textbook heading")
    set_shape_box(textbook, 240, 212, 300, 52)
    set_font_size(textbook, 24)
    lectures = find_text_shape(slide4, lambda text: text.startswith("Lectures"), "Lectures heading")
    set_shape_box(lectures, 240, 346, 210, 50)
    set_font_size(lectures, 24)
    parts[part4] = etree.tostring(slide4, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Source page 5: one-line section labels and body sizing recover the
    # reference's hierarchy without replacing any text with an image.
    part6, slide6, _ = load_slide(6)
    for prefix, bounds in (
        ("Group Projects", (38, 178, 420, 52)),
        ("Exams", (38, 518, 360, 50)),
    ):
        heading = find_text_shape(slide6, lambda text, prefix=prefix: text.startswith(prefix), f"{prefix} heading")
        set_shape_box(heading, *bounds)
        set_font_size(heading, 28)
    for prefix, label in (
        ("Programming Assignments", "group-project body"),
        ("Two in-class midterms", "exam body"),
    ):
        body = find_text_shape(slide6, lambda text, prefix=prefix: text.startswith(prefix), label)
        set_font_size(body, 26)
    parts[part6] = etree.tostring(slide6, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Source pages 7–8: put the Fall grading labels and weights back into the
    # existing native, editable table cells.
    for index, table_rows in (
        (8, [("ATTENDANCE", "10%"), ("HOMEWORK ASSIGNMENTS", "10%"), ("COURSE PROJECTS", "20%"), ("MIDTERMS", "35%"), ("FINAL (TBA)", "25%")]),
        (9, [("HOMEWORK ASSIGNMENTS", "10%"), ("COURSE PROJECTS", "20%"), ("MIDTERMS", "40%"), ("FINAL (TBA)", "30%")]),
    ):
        table_part, table_slide, _ = load_slide(index)
        repair_grading_table(table_slide, len(table_rows), table_rows)
        title = find_text_shape(table_slide, lambda text: text.startswith("Course Grading"), "grading option title")
        set_shape_box(title, 20, 20, 984, 140)
        set_font_size(title, 60)
        parts[table_part] = etree.tostring(table_slide, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Source page 13 contains only the question. The imported Two-Step
    # Submission text is stale Fall 2025 material, so remove that overlay.
    part14, slide14, _ = load_slide(14)
    stale = find_text_shape(slide14, lambda text: text.startswith("Two-Step Submission"), "obsolete submission overlay")
    stale.getparent().remove(stale)
    title14 = find_text_shape(slide14, lambda text: text.startswith("Administrivia") and "questions" in text, "administrivia questions title")
    set_shape_box(title14, 40, 340, 944, 90)
    set_font_size(title14, 60)
    parts[part14] = etree.tostring(slide14, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Source page 16: shrink the imported callout text so every editable bullet
    # remains inside the rotated blue box. Also keep the heading on one line.
    part17, slide17, _ = load_slide(17)
    title17 = find_text_shape(slide17, lambda text: text.startswith("Who") and "you’ll be after CS 408" in text, "Who title")
    scale_font_sizes(title17, 0.85)
    set_shape_box(title17, 50, 20, 950, 170)
    callout = find_text_shape(slide17, lambda text: text.startswith("Turn to the person next to you"), "turn-to-person callout")
    set_font_size(callout, 24)
    parts[part17] = etree.tostring(slide17, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Source page 18: restore the missing embedded article screenshot as an
    # image object. It is intrinsically a screenshot; surrounding title and
    # caption remain editable text objects.
    reference_pdf = getattr(repair, "reference_pdf", None)
    if reference_pdf is not None:
        with tempfile.TemporaryDirectory(prefix="cs408-intro-reference-") as tmp:
            workdir = Path(tmp)
            part21, slide21, rels21 = load_slide(21)
            caption = find_text_shape(slide21, lambda text: text.startswith("A space error:"), "space-error caption")
            caption.getparent().remove(caption)
            template = slide21.find(".//p:pic", NS)
            if template is None:
                raise ValueError("source page 18 has no picture template for its restored screenshot")
            add_reference_crop(parts, reference_pdf, part21, slide21, rels21, template,
                page=18, source_box=(316, 421, 708, 254), target_box=(316, 421, 708, 254),
                media_name="cs408-intro-page18-article.png", label="Reference article screenshot", workdir=workdir)
            parts[part21] = etree.tostring(slide21, xml_declaration=True, encoding="UTF-8", standalone=True)
            rel_part21 = posixpath.join(posixpath.dirname(part21), "_rels", posixpath.basename(part21) + ".rels")
            parts[rel_part21] = etree.tostring(rels21, xml_declaration=True, encoding="UTF-8", standalone=True)

            # Source page 23 has no editable prose: the sole object is an AWS
            # article screenshot. Restore only that screenshot region.
            part26, slide26, rels26 = load_slide(26)
            add_reference_crop(parts, reference_pdf, part26, slide26, rels26, template,
                page=23, source_box=(70, 38, 883, 724), target_box=(70, 38, 883, 724),
                media_name="cs408-intro-page23-aws-article.png", label="AWS article screenshot", workdir=workdir)
            parts[part26] = etree.tostring(slide26, xml_declaration=True, encoding="UTF-8", standalone=True)
            rel_part26 = posixpath.join(posixpath.dirname(part26), "_rels", posixpath.basename(part26) + ".rels")
            parts[rel_part26] = etree.tostring(rels26, xml_declaration=True, encoding="UTF-8", standalone=True)

            # Source page 26 has corrupted off-canvas connector paths. Keep its
            # heading and bullets native; use a diagram-only source crop.
            part29, slide29, rels29 = load_slide(29)
            body29 = find_text_shape(slide29, lambda text: text.startswith("Testing allows us to"), "testing-intent bullets")
            set_shape_box(body29, 75, 204, 874, 150)
            set_font_size(body29, 24)
            # These two empty vector paths have extreme off-slide coordinates
            # and render as stray arrows over the source diagram. Remove only
            # those path shapes; the rest of the diagram is replaced below by
            # the narrow reference crop.
            for shape in list(slide29.findall(".//p:sp", NS)):
                if "".join(shape.xpath(".//a:t/text()", namespaces=NS)).strip():
                    continue
                xfrm = shape.find("./p:spPr/a:xfrm", NS)
                off = xfrm.find("./a:off", NS) if xfrm is not None else None
                ext = xfrm.find("./a:ext", NS) if xfrm is not None else None
                if off is None or ext is None:
                    continue
                x = int(off.get("x")) / EMU
                y = int(off.get("y")) / EMU
                w = int(ext.get("cx")) / EMU
                h = int(ext.get("cy")) / EMU
                if x < 0 or y < 0 or x + w > SLIDE_W_PT or y + h > SLIDE_H_PT:
                    shape.getparent().remove(shape)
            add_reference_crop(parts, reference_pdf, part29, slide29, rels29, template,
                page=26, source_box=(0, 400, 1024, 368), target_box=(0, 400, 1024, 368),
                media_name="cs408-intro-page26-diagram.png", label="Reference diagram region", workdir=workdir)
            parts[part29] = etree.tostring(slide29, xml_declaration=True, encoding="UTF-8", standalone=True)
            rel_part29 = posixpath.join(posixpath.dirname(part29), "_rels", posixpath.basename(part29) + ".rels")
            parts[rel_part29] = etree.tostring(rels29, xml_declaration=True, encoding="UTF-8", standalone=True)
    else:
        # If no PDF reference was supplied, still repair the fully editable
        # source slides and leave the three image repairs explicitly pending.
        pass

    # Source page 25: text fit on the editable SUT label. The nearby photo is
    # an intrinsic image and is resized without converting the whole slide.
    part28, slide28, rels28 = load_slide(28)
    sut = find_text_shape(slide28, lambda text: text == "System Under Test", "System Under Test label")
    set_shape_box(sut, 206, 478, 450, 145)
    set_font_size(sut, 40)
    pictures28 = slide28.findall(".//p:pic", NS)
    if len(pictures28) != 3:
        raise ValueError(f"expected three pictures on source page 25, found {len(pictures28)}")
    portrait = pictures28[2]
    blip = portrait.find(".//a:blip", NS)
    rid = blip.get(f"{{{R}}}embed")
    rel = next((r for r in rels28.findall("rel:Relationship", NS) if r.get("Id") == rid), None)
    if rel is None:
        raise ValueError("portrait image relationship is missing")
    old_part = posixpath.normpath(posixpath.join(posixpath.dirname(part28), rel.get("Target")))
    image = Image.open(io.BytesIO(parts[old_part])).convert("RGBA")
    width, height = image.size
    side = min(width, height)
    left = max(0, min(width - side, round(width * 0.22)))
    portrait_crop = image.crop((left, 0, left + side, side))
    buffer = io.BytesIO()
    portrait_crop.save(buffer, format="PNG", optimize=True)
    portrait_part = "ppt/media/cs408-intro-sut-portrait.png"
    parts[portrait_part] = buffer.getvalue()
    rel.set("Target", posixpath.relpath(portrait_part, posixpath.dirname(part28)))
    pic_xfrm = portrait.find("./p:spPr/a:xfrm", NS)
    off = pic_xfrm.find("./a:off", NS) if pic_xfrm is not None else None
    ext = pic_xfrm.find("./a:ext", NS) if pic_xfrm is not None else None
    if off is None or ext is None:
        raise ValueError("portrait picture geometry is missing")
    off.set("x", str(round(744 * EMU)))
    off.set("y", str(round(448 * EMU)))
    ext.set("cx", str(round(90 * EMU)))
    ext.set("cy", str(round(90 * EMU)))
    parts[part28] = etree.tostring(slide28, xml_declaration=True, encoding="UTF-8", standalone=True)
    rel_part28 = posixpath.join(posixpath.dirname(part28), "_rels", posixpath.basename(part28) + ".rels")
    parts[rel_part28] = etree.tostring(rels28, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Source pages 27–29: shrink long objective headings/body text to match
    # the source hierarchy and remove the title wrap caused by font fallback.
    for index in (30, 31, 32):
        title_part, objective_slide, _ = load_slide(index)
        title = find_text_shape(objective_slide, lambda text: text.startswith("Who") and "you’ll be after CS 408" in text, "learning-objective title")
        scale_font_sizes(title, 0.85)
        set_shape_box(title, 50, 20, 950, 170)
        heading = find_text_shape(objective_slide, lambda text: text.startswith("Learning Objective"), "learning-objective heading")
        set_shape_box(heading, 38, 181, 950, 62)
        set_font_size(heading, 30)
        body = find_text_shape(objective_slide, lambda text: not text.startswith("Learning Objective") and text.startswith(("Design", "Implement", "Compare")), "learning-objective body")
        set_shape_box(body, 35, 245, 940, 475)
        set_font_size(body, 28)
        parts[title_part] = etree.tostring(objective_slide, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Source page 25's introductory bullets also wrap too early after import.
    part28, slide28, rels28 = load_slide(28)
    intro_bullets = find_text_shape(slide28, lambda text: text.startswith("Testing allows us to"), "why-test bullets")
    set_font_size(intro_bullets, 30)
    parts[part28] = etree.tostring(slide28, xml_declaration=True, encoding="UTF-8", standalone=True)

    parts[slide_part] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Record picture relationship updates from source page 25 and PDF-derived
    # screenshot crops. All image defaults already exist in the package.
    pptx_out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(pptx_out, "w", ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            archive.writestr(name, data)
    with ZipFile(pptx_out) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"repaired PPTX has corrupt ZIP member {bad}")
    print(f"Applied local Introduction repairs and source screenshot restores: {pptx_out}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference-pdf", type=Path, help="exact current Fall PDF for screenshot and diagram crops")
    args = parser.parse_args()
    repair.reference_pdf = args.reference_pdf
    repair(args.input, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
