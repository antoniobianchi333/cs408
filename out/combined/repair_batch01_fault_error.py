#!/usr/bin/env python3
"""Repair confirmed Fault/Error slides in the local LibreOffice PPTX.

The script makes editable text/table repairs and uses narrowly scoped image
regions for corrupted Keynote image crops and connector diagrams. Text remains
native where it is part of the source page; only the affected image/diagram
region is replaced. The two outcome tables remain editable native cells.

Example:
  python3 out/combined/repair_batch01_fault_error.py \
    --input out/.build/batch-01/source-pptx/02-408st-fault-error-failure.pptx \
    --reference-pdf slides/f26-pdfs/02-408st-fault-error-failure.pdf \
    --output out/.build/batch-01/source-pptx/02-408st-fault-error-failure-repaired.pptx \
    --crop-dir out/.build/batch-01/source-pdf-diagram-crops

Batch mapping: source PDF pages 65, 73, and 74 align to converted candidate
slides 90, 101, and 102. Source pages 76 and 77 align to candidate slides 104
and 105. Source page 68 aligns to candidate slide 94.
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
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"p": P, "a": A, "r": R, "rel": REL, "ct": CT}
EMU_PER_PT = 12_700
SLIDE_W_PT = 1024
SLIDE_H_PT = 768
DIAGRAM_Y_PT = 160

HEADERS = ["Fault executed", "Error", "Failure"]
CASES = [
    ["No", "No", "No"],
    ["No", "No", "Yes"],
    ["No", "Yes", "No"],
    ["No", "Yes", "Yes"],
    ["Yes", "No", "No"],
    ["Yes", "No", "Yes"],
    ["Yes", "Yes", "No"],
    ["Yes", "Yes", "Yes"],
]
POSSIBLE = ["Yes", "No", "No", "No", "Yes", "No", "Yes", "Yes"]
GREEN = "1DB100"
CORAL = "FF644E"
YELLOW = "F8BA00"
GRAY_A = "EBEBEB"
GRAY_B = "E1E0DA"
GRID = "B8B8B8"


def q(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def emu(points: float) -> str:
    return str(round(points * EMU_PER_PT))


def xml_bytes(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def presentation_order(parts: dict[str, bytes]) -> list[str]:
    pres = etree.fromstring(parts["ppt/presentation.xml"])
    rels = etree.fromstring(parts["ppt/_rels/presentation.xml.rels"])
    targets = {
        rel.get("Id"): rel.get("Target")
        for rel in rels.findall("rel:Relationship", NS)
    }
    order = []
    for node in pres.findall("p:sldIdLst/p:sldId", NS):
        target = targets[node.get(q(R, "id"))]
        order.append(posixpath.normpath(posixpath.join("ppt", target)))
    return order


def render_source_crop(reference_pdf: Path, page: int, crop_dir: Path) -> Path:
    crop_dir.mkdir(parents=True, exist_ok=True)
    rendered = crop_dir / f"page-{page}-150dpi.png"
    prefix = crop_dir / f"page-{page}-source"
    subprocess.run(
        [
            "pdftoppm", "-f", str(page), "-l", str(page), "-r", "150",
            "-png", "-singlefile", str(reference_pdf), str(prefix),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    raw = prefix.with_suffix(".png")
    if not raw.exists():
        raise FileNotFoundError(f"pdftoppm did not create {raw}")
    graph = crop_dir / f"page-{page}-diagram-only.png"
    with Image.open(raw) as source:
        scale = source.width / SLIDE_W_PT
        crop_top = round(DIAGRAM_Y_PT * scale)
        if crop_top <= 0 or crop_top >= source.height:
            raise ValueError(f"invalid crop start for reference page {page}")
        source.crop((0, crop_top, source.width, source.height)).save(graph, optimize=True)
    return graph


def remove_or_set_fill(tcpr: etree._Element, color: str) -> None:
    for node in list(tcpr):
        if etree.QName(node).localname in ("solidFill", "gradFill", "blipFill", "noFill"):
            tcpr.remove(node)
    fill = etree.SubElement(tcpr, q(A, "solidFill"))
    etree.SubElement(fill, q(A, "srgbClr")).set("val", color)


def set_cell_border_colors(tcpr: etree._Element) -> None:
    for edge in ("lnL", "lnR", "lnT", "lnB"):
        line = tcpr.find(f"./a:{edge}", NS)
        if line is None:
            continue
        for node in list(line):
            if etree.QName(node).localname in ("solidFill", "gradFill", "noFill"):
                line.remove(node)
        fill = etree.SubElement(line, q(A, "solidFill"))
        etree.SubElement(fill, q(A, "srgbClr")).set("val", GRID)


def set_cell(cell: etree._Element, text: str, fill: str, *, bold: bool = False) -> None:
    tcpr = cell.find("./a:tcPr", NS)
    if tcpr is None:
        tcpr = etree.SubElement(cell, q(A, "tcPr"))
    tcpr.set("anchor", "ctr")
    for attr in ("marL", "marR", "marT", "marB"):
        tcpr.set(attr, "0")
    remove_or_set_fill(tcpr, fill)
    set_cell_border_colors(tcpr)

    txbody = cell.find("./a:txBody", NS)
    if txbody is None:
        txbody = etree.Element(q(A, "txBody"))
        bodypr = etree.SubElement(txbody, q(A, "bodyPr"))
        bodypr.set("anchor", "ctr")
        etree.SubElement(txbody, q(A, "lstStyle"))
        paragraph = etree.SubElement(txbody, q(A, "p"))
        cell.insert(0, txbody)
    else:
        bodypr = txbody.find("./a:bodyPr", NS)
        if bodypr is None:
            bodypr = etree.Element(q(A, "bodyPr"))
            txbody.insert(0, bodypr)
        bodypr.set("anchor", "ctr")
        paragraph = txbody.find("./a:p", NS)
        if paragraph is None:
            paragraph = etree.SubElement(txbody, q(A, "p"))
        for child in list(paragraph):
            paragraph.remove(child)

    ppr = etree.SubElement(paragraph, q(A, "pPr"))
    ppr.set("algn", "ctr")
    etree.SubElement(ppr, q(A, "buNone"))
    run = etree.SubElement(paragraph, q(A, "r"))
    rpr = etree.SubElement(run, q(A, "rPr"))
    rpr.set("lang", "en-US")
    rpr.set("sz", "1700" if bold else "1800")
    if bold:
        rpr.set("b", "1")
    solid = etree.SubElement(rpr, q(A, "solidFill"))
    etree.SubElement(solid, q(A, "srgbClr")).set("val", "000000")
    latin = etree.SubElement(rpr, q(A, "latin"))
    latin.set("typeface", "Arial")
    t = etree.SubElement(run, q(A, "t"))
    t.text = text
    etree.SubElement(paragraph, q(A, "endParaRPr")).set("lang", "en-US")


def table_from_frame(frame: etree._Element) -> tuple[etree._Element, etree._Element]:
    table = frame.find(".//a:tbl", NS)
    if table is None:
        raise ValueError("expected native table in graphicFrame")
    xfrm = frame.find("./p:xfrm", NS)
    ext = xfrm.find("./a:ext", NS) if xfrm is not None else None
    if ext is None:
        raise ValueError("table graphicFrame has no geometry")
    return table, ext


def shrink_main_table_to_three_columns(frame: etree._Element) -> list[list[etree._Element]]:
    table, ext = table_from_frame(frame)
    grid = table.find("./a:tblGrid", NS)
    rows = table.findall("./a:tr", NS)
    if grid is None or len(grid.findall("./a:gridCol", NS)) != 4 or len(rows) != 9:
        raise ValueError("expected the converted 9-row by 4-column outcome table")
    for row in rows:
        cells = row.findall("./a:tc", NS)
        if len(cells) != 4:
            raise ValueError("outcome table row has an unexpected cell count")
        row.remove(cells[-1])
    cols = grid.findall("./a:gridCol", NS)
    for col in cols[3:]:
        grid.remove(col)
    for col, width in zip(grid.findall("./a:gridCol", NS), (167, 117, 123), strict=True):
        col.set("w", emu(width))
    ext.set("cx", emu(407))
    return [row.findall("./a:tc", NS) for row in rows]


def repair_tables(root_page_76: etree._Element, root_page_77: etree._Element) -> None:
    frames76 = root_page_76.findall(".//p:graphicFrame", NS)
    frames77 = root_page_77.findall(".//p:graphicFrame", NS)
    if len(frames76) != 1 or len(frames77) != 2:
        raise ValueError("unexpected table count on Fall reference pages 76–77")

    for frames in (frames76, frames77):
        rows = shrink_main_table_to_three_columns(frames[0])
        for col, text in enumerate(HEADERS):
            set_cell(rows[0][col], text, GRAY_A)
        for row_index, values in enumerate(CASES, start=1):
            for col, text in enumerate(values):
                fill = GREEN if text == "No" else CORAL
                set_cell(rows[row_index][col], text, fill)

    possible, _ = table_from_frame(frames77[1])
    possible_rows = possible.findall("./a:tr", NS)
    if len(possible_rows) != 9 or any(len(r.findall("./a:tc", NS)) != 1 for r in possible_rows):
        raise ValueError("expected the separate 9-row Possible? table")
    possible_cells = [r.find("./a:tc", NS) for r in possible_rows]
    set_cell(possible_cells[0], "Possible?", GRAY_A, bold=True)
    for index, value in enumerate(POSSIBLE, start=1):
        if value == "Yes":
            fill = YELLOW
        else:
            fill = GRAY_A if index % 2 else GRAY_B
        set_cell(possible_cells[index], value, fill, bold=True)


def set_bounds(shape: etree._Element, x: float, y: float, w: float, h: float) -> None:
    xfrm = shape.find("./p:spPr/a:xfrm", NS)
    if xfrm is None:
        raise ValueError("target text shape has no transform")
    off = xfrm.find("./a:off", NS)
    ext = xfrm.find("./a:ext", NS)
    if off is None or ext is None:
        raise ValueError("target text shape has incomplete geometry")
    off.set("x", emu(x))
    off.set("y", emu(y))
    ext.set("cx", emu(w))
    ext.set("cy", emu(h))


def shape_text(shape: etree._Element) -> str:
    return "".join(shape.xpath(".//a:t/text()", namespaces=NS)).strip()


def repair_video_labels(root: etree._Element) -> None:
    targets = {
        "Testing": ("TESTING", 246, 108, 200, 80),
        "Debugging": ("DEBUGGING", 561, 150, 240, 80),
    }
    for old, (new, x, y, w, h) in targets.items():
        matches = [s for s in root.findall(".//p:sp", NS) if shape_text(s) == old]
        if len(matches) != 1:
            raise ValueError(f"expected one {old} overlay label, found {len(matches)}")
        shape = matches[0]
        set_bounds(shape, x, y, w, h)
        xfrm = shape.find("./p:spPr/a:xfrm", NS)
        xfrm.set("rot", "900000")  # 15 degrees clockwise to follow the signs.
        body = shape.find("./p:txBody/a:bodyPr", NS)
        if body is not None:
            for attr in ("lIns", "rIns", "tIns", "bIns"):
                body.set(attr, "0")
            body.set("anchor", "ctr")
            body.set("wrap", "none")
        paragraph = shape.find("./p:txBody/a:p", NS)
        if paragraph is not None:
            ppr = paragraph.find("./a:pPr", NS)
            if ppr is None:
                ppr = etree.Element(q(A, "pPr"))
                paragraph.insert(0, ppr)
            ppr.set("algn", "ctr")
        runs = shape.findall(".//a:rPr", NS)
        if not runs:
            raise ValueError(f"{old} label has no editable styled text")
        for run in runs:
            # 36 pt keeps the rotated DEBUGGING label on one line after the
            # local PPTX repair is imported and rendered by Google Slides.
            run.set("sz", "3600")
            run.set("b", "1")
            for kind in ("latin", "ea", "cs"):
                font = run.find(f"./a:{kind}", NS)
                if font is None:
                    font = etree.SubElement(run, q(A, kind))
                font.set("typeface", "Arial")
        text_nodes = shape.findall(".//a:t", NS)
        if len(text_nodes) != 1:
            raise ValueError(f"{old} label has unexpected text-run structure")
        text_nodes[0].text = new


def slide_rels_path(slide_part: str) -> str:
    folder, name = posixpath.split(slide_part)
    return posixpath.join(folder, "_rels", f"{name}.rels")


def add_png_relationship(parts: dict[str, bytes], slide_part: str, slide_number: int, png_path: Path, tag: str = "diagram") -> str:
    media_name = f"batch01-slide-{slide_number}-{tag}.png"
    media_part = f"ppt/media/{media_name}"
    if media_part in parts:
        raise ValueError(f"media part already exists: {media_part}")
    rels_part = slide_rels_path(slide_part)
    if rels_part not in parts:
        rels = etree.Element(q(REL, "Relationships"), nsmap={None: REL})
    else:
        rels = etree.fromstring(parts[rels_part])
    used = {rel.get("Id") for rel in rels.findall("rel:Relationship", NS)}
    rid = f"rIdBatch01{tag.title().replace('-', '')}{slide_number}"
    suffix = 2
    while rid in used:
        rid = f"rIdBatch01Diagram{slide_number}_{suffix}"
        suffix += 1
    rel = etree.SubElement(rels, q(REL, "Relationship"))
    rel.set("Id", rid)
    rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel.set("Target", f"../media/{media_name}")
    parts[rels_part] = xml_bytes(rels)
    parts[media_part] = png_path.read_bytes()
    return rid


def add_png_default(parts: dict[str, bytes]) -> None:
    root = etree.fromstring(parts["[Content_Types].xml"])
    if not any(d.get("Extension", "").lower() == "png" for d in root.findall("ct:Default", NS)):
        node = etree.SubElement(root, q(CT, "Default"))
        node.set("Extension", "png")
        node.set("ContentType", "image/png")
    parts["[Content_Types].xml"] = xml_bytes(root)


def add_picture(
    root: etree._Element,
    relationship_id: str,
    page: int,
    bounds: tuple[float, float, float, float] = (0, DIAGRAM_Y_PT, SLIDE_W_PT, SLIDE_H_PT - DIAGRAM_Y_PT),
    label: str | None = None,
) -> None:
    tree = root.find("p:cSld/p:spTree", NS)
    existing_ids = [int(v) for v in root.xpath(".//p:cNvPr/@id", namespaces=NS) if v.isdigit()]
    object_id = max(existing_ids, default=0) + 1
    pic = etree.SubElement(tree, q(P, "pic"))
    nvpic = etree.SubElement(pic, q(P, "nvPicPr"))
    c_nv = etree.SubElement(nvpic, q(P, "cNvPr"))
    c_nv.set("id", str(object_id))
    c_nv.set("name", label or f"Exact Fall PDF crop page {page}")
    c_nv_pic = etree.SubElement(nvpic, q(P, "cNvPicPr"))
    locks = etree.SubElement(c_nv_pic, q(A, "picLocks"))
    locks.set("noChangeAspect", "1")
    etree.SubElement(nvpic, q(P, "nvPr"))
    blip_fill = etree.SubElement(pic, q(P, "blipFill"))
    blip = etree.SubElement(blip_fill, q(A, "blip"))
    blip.set(q(R, "embed"), relationship_id)
    stretch = etree.SubElement(blip_fill, q(A, "stretch"))
    etree.SubElement(stretch, q(A, "fillRect"))
    sppr = etree.SubElement(pic, q(P, "spPr"))
    xfrm = etree.SubElement(sppr, q(A, "xfrm"))
    off = etree.SubElement(xfrm, q(A, "off"))
    x, y, width, height = bounds
    off.set("x", emu(x))
    off.set("y", emu(y))
    ext = etree.SubElement(xfrm, q(A, "ext"))
    ext.set("cx", emu(width))
    ext.set("cy", emu(height))
    geom = etree.SubElement(sppr, q(A, "prstGeom"))
    geom.set("prst", "rect")
    etree.SubElement(geom, q(A, "avLst"))


def replace_diagram_with_exact_crop(
    parts: dict[str, bytes], slide_part: str, slide_number: int,
    title: str, crop_path: Path, source_page: int,
) -> None:
    root = etree.fromstring(parts[slide_part])
    tree = root.find("p:cSld/p:spTree", NS)
    title_matches = [s for s in root.findall(".//p:sp", NS) if shape_text(s) == title]
    if len(title_matches) != 1:
        raise ValueError(f"candidate slide {slide_number}: expected one editable {title!r} title")
    title_shape = title_matches[0]
    for child in list(tree):
        local = etree.QName(child).localname
        if local in ("sp", "pic", "cxnSp", "graphicFrame", "grpSp") and child is not title_shape:
            tree.remove(child)
    rid = add_png_relationship(parts, slide_part, slide_number, crop_path, "diagram")
    add_picture(root, rid, source_page, label=f"Exact Fall PDF diagram crop page {source_page}")
    parts[slide_part] = xml_bytes(root)


def render_reference_region(reference_pdf: Path, page: int, box: tuple[float, float, float, float], crop_dir: Path) -> Path:
    crop_dir.mkdir(parents=True, exist_ok=True)
    prefix = crop_dir / f"page-{page}-region-source"
    subprocess.run(
        ["pdftoppm", "-f", str(page), "-l", str(page), "-scale-to-x", "2048", "-scale-to-y", "1536", "-png", "-singlefile", str(reference_pdf), str(prefix)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    source_path = prefix.with_suffix(".png")
    if not source_path.exists():
        raise FileNotFoundError(f"pdftoppm did not create {source_path}")
    x, y, width, height = box
    result = crop_dir / f"page-{page}-reference-region-{round(x)}-{round(y)}-{round(width)}-{round(height)}.png"
    with Image.open(source_path) as source:
        source.crop((round(x * 2), round(y * 2), round((x + width) * 2), round((y + height) * 2))).save(result, optimize=True)
    return result


def set_text_box(shape: etree._Element, x: float, y: float, width: float, height: float, font_size: float) -> None:
    set_bounds(shape, x, y, width, height)
    for run in shape.findall(".//a:rPr", NS) + shape.findall(".//a:defRPr", NS) + shape.findall(".//a:endParaRPr", NS):
        run.set("sz", str(round(font_size * 100)))
    body = shape.find("./p:txBody/a:bodyPr", NS)
    if body is not None:
        for attr in ("lIns", "rIns", "tIns", "bIns"):
            body.set(attr, "0")


def keep_photo_text_and_replace_region(
    parts: dict[str, bytes],
    slide_part: str,
    slide_number: int,
    reference_page: int,
    crop_path: Path,
    bounds: tuple[float, float, float, float],
    retained_text: dict[str, tuple[float, float, float, float, float]],
) -> None:
    root = etree.fromstring(parts[slide_part])
    tree = root.find("p:cSld/p:spTree", NS)
    keep: list[etree._Element] = []
    for text, box in retained_text.items():
        matches = [shape for shape in root.findall(".//p:sp", NS) if shape_text(shape) == text]
        if len(matches) != 1:
            raise ValueError(f"candidate slide {slide_number}: expected one editable {text!r} shape, found {len(matches)}")
        shape = matches[0]
        set_text_box(shape, *box)
        keep.append(shape)
    for child in list(tree):
        local = etree.QName(child).localname
        if local in ("sp", "pic", "cxnSp", "graphicFrame", "grpSp") and child not in keep:
            tree.remove(child)
    rid = add_png_relationship(parts, slide_part, slide_number, crop_path)
    add_picture(root, rid, reference_page, bounds, label=f"Reference PDF image region page {reference_page}")
    parts[slide_part] = xml_bytes(root)


def remove_stale_torture_content(root: etree._Element, slide_number: int, keep_pictures: bool = True) -> None:
    for shape in list(root.findall(".//p:sp", NS)):
        text = shape_text(shape)
        if text == "failures versus X" or text.startswith("Torture CS students"):
            shape.getparent().remove(shape)
        elif text.startswith("Question: Is a crash always a failure?") and "What if" in text:
            shape.getparent().remove(shape)
    # The duplicate text version is a hidden/old build source. Preserve the
    # movie still picture and the separate editable question card.
    cards = [s for s in root.findall(".//p:sp", NS) if shape_text(s) == "Question:Is a crash always a failure?"]
    if not cards:
        raise ValueError(f"candidate slide {slide_number}: question card is missing")
    def card_y(shape: etree._Element) -> int:
        xfrm = shape.find("./p:spPr/a:xfrm", NS)
        off = xfrm.find("./a:off", NS) if xfrm is not None else None
        return int(off.get("y")) if off is not None else 0
    card = min(cards, key=card_y)
    for duplicate in cards:
        if duplicate is not card:
            duplicate.getparent().remove(duplicate)
    set_text_box(card, 227.9, 55.7, 568.3, 141.4, 40)


def repair(pptx_in: Path, reference_pdf: Path, pptx_out: Path, crop_dir: Path) -> None:
    crops = {page: render_source_crop(reference_pdf, page, crop_dir) for page in (65, 73, 74)}
    photo_regions = {
        11: render_reference_region(reference_pdf, 11, (0, 0, 444, 386), crop_dir),
        13: render_reference_region(reference_pdf, 13, (0, 0, 444, 768), crop_dir),
        22: render_reference_region(reference_pdf, 22, (0, 0, 431, 406), crop_dir),
        25: render_reference_region(reference_pdf, 25, (0, 0, 432, 768), crop_dir),
    }
    analogy_patch = render_reference_region(reference_pdf, 5, (360, 0, 330, 340), crop_dir)
    analogy_bubble_patch = render_reference_region(reference_pdf, 5, (660, 0, 350, 150), crop_dir)
    with ZipFile(pptx_in) as archive:
        parts = {item.filename: archive.read(item.filename) for item in archive.infolist()}
    order = presentation_order(parts)
    if len(order) < 106:
        raise ValueError("Fault/Error source PPTX has fewer than 106 converted slides")

    # Reconstruct source page 68's two editable title overlays. The book and
    # presenter image itself already matches the selected PDF crop.
    slide94 = etree.fromstring(parts[order[93]])
    repair_video_labels(slide94)
    parts[order[93]] = xml_bytes(slide94)

    slide104 = etree.fromstring(parts[order[103]])
    slide105 = etree.fromstring(parts[order[104]])
    repair_tables(slide104, slide105)
    parts[order[103]] = xml_bytes(slide104)
    parts[order[104]] = xml_bytes(slide105)

    # Source page 1: keep the photograph and both title text objects editable,
    # but reduce fallback-font sizes so the intended three-line subtitle and
    # two-line deck title fit their translucent panels.
    cover_part = order[1]
    cover = etree.fromstring(parts[cover_part])
    top_title = next((s for s in cover.findall(".//p:sp", NS) if shape_text(s).startswith("bugs, bugs, everywhere")), None)
    deck_title = next((s for s in cover.findall(".//p:sp", NS) if shape_text(s).startswith("Beyond Bugs:")), None)
    if top_title is None or deck_title is None:
        raise ValueError("Fault/Error cover title text objects could not be identified")
    set_text_box(top_title, 30.5, 0.1, 600, 350, 36)
    set_text_box(deck_title, 216.2, 480, 795.1, 188, 46)
    parts[cover_part] = xml_bytes(cover)

    # Source page 5: the same full-bleed photo is present, but the Lin portrait
    # build was compressed into a narrow white strip. Replace only that small
    # region with its exact PDF appearance; the title and thought bubble stay
    # editable/background objects.
    analogy_part = order[22]
    analogy = etree.fromstring(parts[analogy_part])
    analogy_rels_part = slide_rels_path(analogy_part)
    analogy_rels = etree.fromstring(parts[analogy_rels_part])
    analogy_pictures = analogy.findall(".//p:pic", NS)
    if len(analogy_pictures) != 2:
        raise ValueError(f"Fault/Error slide 23: expected background and portrait pictures, found {len(analogy_pictures)}")
    analogy_pictures[1].getparent().remove(analogy_pictures[1])
    analogy_rid = add_png_relationship(parts, analogy_part, 23, analogy_patch, "portrait")
    add_picture(analogy, analogy_rid, 5, (360, 0, 330, 340), label="Corrected portrait region from Fall reference")
    bubble_rid = add_png_relationship(parts, analogy_part, 23, analogy_bubble_patch, "thought-bubble")
    add_picture(analogy, bubble_rid, 5, (660, 0, 350, 150), label="Thought bubble artwork from Fall reference")
    parts[analogy_part] = xml_bytes(analogy)

    # Source pages 11, 13, 22, and 25 use teaching images with build/crop
    # states. LibreOffice imported the composite media into the wrong crop and
    # exposed stale overlay text. Replace only the left image panels; keep the
    # visible teaching phrases as editable text shapes.
    photo_repairs = (
        (29, 11, (0, 0, 444, 386), {
            "We just found a bug": (461.3, 147.2, 554.4, 130, 52),
        }),
        (31, 13, (0, 0, 444, 768), {
            "We just found a bug": (461.3, 147.2, 554.4, 130, 52),
            "We just found a failure": (461.3, 539.4, 554.4, 156, 52),
        }),
        (41, 22, (0, 0, 431, 406), {
            "We just fixed a failure": (461.3, 147.2, 554.4, 156, 52),
        }),
        (44, 25, (0, 0, 432, 768), {
            "We just fixed a failure": (461.3, 147.2, 554.4, 156, 52),
            "We just repaired a fault": (461.3, 539.4, 554.4, 156, 52),
        }),
    )
    for slide_number, reference_page, bounds, retained in photo_repairs:
        keep_photo_text_and_replace_region(
            parts, order[slide_number - 1], slide_number, reference_page,
            photo_regions[reference_page], bounds, retained,
        )

    # These are the cumulative states of the same question card. The local
    # PPTX had stale title/bullet layers and a duplicate card on the movie
    # still. Remove only those stale text layers; retain the correct question
    # card and the slide 17 movie image.
    for slide_number in (34, 35):
        question_slide = etree.fromstring(parts[order[slide_number - 1]])
        remove_stale_torture_content(question_slide, slide_number)
        parts[order[slide_number - 1]] = xml_bytes(question_slide)

    # The same saved, old state footer was imported onto seven unrelated
    # current pages. The exact Fall PDF contains none of this text, so remove
    # only that editable overlay and leave each page's code/result objects.
    stale_footer = "Fix: “for (int i = 0; i<x.length; i++)”"
    for slide_number in (28, 33, 36, 38, 39, 45, 85):
        slide_part = order[slide_number - 1]
        slide = etree.fromstring(parts[slide_part])
        matches = [s for s in slide.findall(".//p:sp", NS) if shape_text(s).startswith(stale_footer)]
        if len(matches) > 1:
            raise ValueError(f"candidate slide {slide_number}: duplicate stale state overlays ({len(matches)})")
        for shape in matches:
            shape.getparent().remove(shape)
        parts[slide_part] = xml_bytes(slide)

    # Source page 27: keep the full question on one line after font fallback.
    objective_part = order[46]
    objective_slide = etree.fromstring(parts[objective_part])
    why_faults = next((s for s in objective_slide.findall(".//p:sp", NS) if shape_text(s) == "Why do we find faults?"), None)
    if why_faults is None:
        raise ValueError("source page 27 title could not be identified")
    set_text_box(why_faults, 20, 364.3, 984, 120, 60)
    parts[objective_part] = xml_bytes(objective_slide)

    add_png_default(parts)
    for slide_number, page, title in (
        (90, 65, "RIPR model"),
        (101, 73, "Scientific Method"),
        (102, 74, "Scientific Method"),
    ):
        replace_diagram_with_exact_crop(
            parts, order[slide_number - 1], slide_number, title, crops[page], page
        )

    pptx_out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(pptx_out, "w", ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            archive.writestr(name, data)
    with ZipFile(pptx_out) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"repaired PPTX has corrupt ZIP member {bad}")
    print(f"Repaired native tables/text, 4 image panels, video labels, and 3 diagram regions: {pptx_out}")
    print(f"Exact PDF repair regions are under {crop_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--reference-pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--crop-dir", type=Path, required=True)
    args = parser.parse_args()
    repair(args.input, args.reference_pdf, args.output, args.crop_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
