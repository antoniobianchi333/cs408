#!/usr/bin/env python3
"""Repair confirmed Fault/Error slides in the local LibreOffice PPTX.

The script makes two editable repairs and applies a narrowly scoped image
fallback to three diagrams whose imported connector paths are badly corrupted.
The fallback is a crop of the exact selected Fall PDF page below the still
editable title; it replaces only the damaged diagram region, not the whole
slide. The two tables remain native Google-editable table cells.

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
import posixpath
import subprocess
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
            run.set("sz", "4000")
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


def add_png_relationship(parts: dict[str, bytes], slide_part: str, slide_number: int, png_path: Path) -> str:
    media_name = f"batch01-page-{slide_number}-diagram.png"
    media_part = f"ppt/media/{media_name}"
    if media_part in parts:
        raise ValueError(f"media part already exists: {media_part}")
    rels_part = slide_rels_path(slide_part)
    if rels_part not in parts:
        rels = etree.Element(q(REL, "Relationships"), nsmap={None: REL})
    else:
        rels = etree.fromstring(parts[rels_part])
    used = {rel.get("Id") for rel in rels.findall("rel:Relationship", NS)}
    rid = f"rIdBatch01Diagram{slide_number}"
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


def add_picture(root: etree._Element, relationship_id: str, page: int) -> None:
    tree = root.find("p:cSld/p:spTree", NS)
    existing_ids = [int(v) for v in root.xpath(".//p:cNvPr/@id", namespaces=NS) if v.isdigit()]
    object_id = max(existing_ids, default=0) + 1
    pic = etree.SubElement(tree, q(P, "pic"))
    nvpic = etree.SubElement(pic, q(P, "nvPicPr"))
    c_nv = etree.SubElement(nvpic, q(P, "cNvPr"))
    c_nv.set("id", str(object_id))
    c_nv.set("name", f"Exact Fall PDF diagram crop page {page}")
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
    off.set("x", "0")
    off.set("y", emu(DIAGRAM_Y_PT))
    ext = etree.SubElement(xfrm, q(A, "ext"))
    ext.set("cx", emu(SLIDE_W_PT))
    ext.set("cy", emu(SLIDE_H_PT - DIAGRAM_Y_PT))
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
    rid = add_png_relationship(parts, slide_part, slide_number, crop_path)
    add_picture(root, rid, source_page)
    parts[slide_part] = xml_bytes(root)


def repair(pptx_in: Path, reference_pdf: Path, pptx_out: Path, crop_dir: Path) -> None:
    crops = {
        page: render_source_crop(reference_pdf, page, crop_dir)
        for page in (65, 73, 74)
    }
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
    print(f"Repaired native tables/video labels and 3 diagram regions: {pptx_out}")
    print(f"Exact PDF diagram crops are under {crop_dir}")


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
