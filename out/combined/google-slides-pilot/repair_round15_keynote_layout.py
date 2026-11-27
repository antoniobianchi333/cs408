#!/usr/bin/env python3
"""Repair measured Round 15 Keynote-to-PPTX conversion defects.

This is a source-specific pilot repair, not a collection-wide geometry rule.
It uses the IWA evidence that the testing-question heading belongs to the
three consecutive "What is a program?" pages, and matches the meme overlay to
the available Fall PDF reference while keeping its text and backing editable.
It restores foreground titles and the faded anatomy background on the complete
image-backed title family identified by comparing the Google render with the
Fall reference PDF. It also removes the unsupported slide 1 green gradient,
cleans empty slide 2 bullets, uses a source crop for slide 4's distorted state
diagram while keeping its text editable, fits the slide 26 Observe callout,
repairs the slide 30 percentage and caption, reduces the later 25% callouts,
restores two slide 36 logos with a transparent patch, and removes the white
background from the imported chain logo. Other image-only builds and
intentional photo slides remain unchanged.
"""

from __future__ import annotations

import argparse
import re
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree
from PIL import Image


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
}
QUESTION = "When to stop testing? How much testing is necessary?"
QUESTION_SLIDES = {3, 4, 5}
EMU_PER_POINT = 12_700  # This deck's 1024 x 768 PDF pages use 1 pt per slide point.
SLIDE_WIDTH = 1024 * EMU_PER_POINT
SLIDE_HEIGHT = 768 * EMU_PER_POINT
BACKGROUND_WASH_NAME = "Round16 anatomy background wash"
PERCENT_CALLOUT_SLIDES = {30, 31, 32}
CHAIN_LOGO_PART = "ppt/media/image43.png"
LOGO_PATCH_NAME = "Round16 restored slide 36 logos"
LOGO_PATCH_PART = "ppt/media/round16-slide36-missing-logos.png"
LOGO_PATCH_REL_ID = "rId7"
DIAGRAM_PATCH_NAME = "Round16 slide 4 reference state diagram"
DIAGRAM_PATCH_PART = "ppt/media/round16-slide4-state-diagram.png"
DIAGRAM_PATCH_TARGET = "../media/round16-slide4-state-diagram.png"
DIAGRAM_PATCH_REL_ID = "rId3"
DEFAULT_LOGO_PATCH = (
    Path(__file__).parent
    / "cs408-fall-test-anatomy-round16-review"
    / "slide36-missing-logos.png"
)
DEFAULT_CHAIN_LOGO = (
    Path(__file__).parent
    / "cs408-fall-test-anatomy-round16-review"
    / "slide36-chain-transparent.png"
)
DEFAULT_DIAGRAM_PATCH = (
    Path(__file__).parent
    / "cs408-fall-test-anatomy-round16-review"
    / "slide4-state-diagram.png"
)
BACKGROUND_TITLE_SLIDES = {
    10: "What is a test?",
    11: "What is a test?",
    12: "What is a test?",
    13: "What is a test?",
    14: "Dissect this test",
    15: "Dissect this test",
    16: "Dependencies ⊆ Environment",
    17: "Dissect this test",
    18: "Three setups, Three tests",
    19: "Three setups, Three tests",
    20: "Three setups, Three tests",
    21: "Three setups, Three tests",
    22: "Three setups, Three tests",
    25: "Doubles: The New Hotness",
    26: "Doubles: The New Hotness",
    27: "Integration Testing, Revisited",
    30: "Integration Testing, Revisited",
    31: "Integration Testing, Revisited",
    32: "Integration Testing, Revisited",
    36: "Integration Testing Today",
    37: "Integration Testing, Improved",
}


def set_shape_bounds(shape: etree._Element, *, x: int, y: int, w: int, h: int, rotation: int | None = None) -> None:
    xfrm = shape.find("./p:spPr/a:xfrm", NS)
    if xfrm is None:
        raise ValueError("Expected editable shape transform is missing")
    off = xfrm.find("./a:off", NS)
    ext = xfrm.find("./a:ext", NS)
    if off is None or ext is None:
        raise ValueError("Expected editable shape position or size is missing")
    off.set("x", str(x))
    off.set("y", str(y))
    ext.set("cx", str(w))
    ext.set("cy", str(h))
    if rotation is None:
        xfrm.attrib.pop("rot", None)
    else:
        xfrm.set("rot", str(rotation))


def repair_question_heading(root: etree._Element, slide_number: int) -> tuple[int, bool]:
    changed = 0
    for shape in root.findall(".//p:spTree/p:sp", NS):
        text = "".join(shape.xpath(".//a:t/text()", namespaces=NS))
        if QUESTION not in text:
            continue
        parent = shape.getparent()
        if parent is None:
            raise ValueError(f"Slide {slide_number}: heading shape has no parent")
        if slide_number not in QUESTION_SLIDES:
            parent.remove(shape)
            changed += 1
            continue

        # Place the real 16 pt question in a narrow header band above the title.
        set_shape_bounds(
            shape,
            x=38 * EMU_PER_POINT,
            y=5 * EMU_PER_POINT,
            w=948 * EMU_PER_POINT,
            h=30 * EMU_PER_POINT,
        )
        body = shape.find("./p:txBody/a:bodyPr", NS)
        if body is not None:
            for attr in ("lIns", "rIns", "tIns", "bIns"):
                body.set(attr, "0")
            body.set("anchor", "ctr")
        for run_style in shape.findall(".//a:rPr", NS) + shape.findall(".//a:defRPr", NS):
            run_style.set("sz", "1600")
        for end_style in shape.findall(".//a:endParaRPr", NS):
            end_style.set("sz", "1600")
        changed += 1
    return changed, slide_number in QUESTION_SLIDES


def remove_slide1_gradient(root: etree._Element, slide_number: int) -> bool:
    if slide_number != 1:
        return False
    matches = []
    for shape in root.findall(".//p:spTree/p:sp", NS):
        off = shape.find("./p:spPr/a:xfrm/a:off", NS)
        ext = shape.find("./p:spPr/a:xfrm/a:ext", NS)
        gradient = shape.find("./p:spPr/a:gradFill", NS)
        text = "".join(shape.xpath(".//a:t/text()", namespaces=NS)).strip()
        if (
            off is not None
            and ext is not None
            and gradient is not None
            and not text
            and (off.get("x"), off.get("y"), ext.get("cx"), ext.get("cy"))
            == ("5867280", "10440", "1270440", "9753840")
        ):
            matches.append(shape)
    if len(matches) != 1:
        raise ValueError(f"Slide 1: expected one unsupported green gradient, found {len(matches)}")
    matches[0].getparent().remove(matches[0])
    return True


def remove_slide2_empty_bullets(root: etree._Element, slide_number: int) -> int:
    if slide_number != 2:
        return 0
    matches = []
    for shape in root.findall(".//p:spTree/p:sp", NS):
        text = "".join(shape.xpath(".//a:t/text()", namespaces=NS))
        if "Announcements:" in text:
            matches.append(shape)
    if len(matches) != 1:
        raise ValueError(f"Slide 2: expected one announcements text box, found {len(matches)}")
    body = matches[0].find("./p:txBody", NS)
    if body is None:
        raise ValueError("Slide 2: announcements text body is missing")
    removed = 0
    for paragraph in list(body.findall("./a:p", NS)):
        text = "".join(paragraph.xpath(".//a:t/text()", namespaces=NS)).strip()
        if not text:
            body.remove(paragraph)
            removed += 1
    return removed


def repair_slide1_title_banner(root: etree._Element, slide_number: int) -> bool:
    if slide_number != 1:
        return False
    matches = []
    for shape in root.findall(".//p:spTree/p:sp", NS):
        text = "".join(shape.xpath(".//a:t/text()", namespaces=NS)).strip()
        if text == "Anatomy of A Test":
            matches.append(shape)
    if len(matches) != 1:
        raise ValueError(f"Slide 1: expected one anatomy title, found {len(matches)}")
    properties = matches[0].find("./p:spPr", NS)
    if properties is None:
        raise ValueError("Slide 1: anatomy title shape properties are missing")
    for no_fill in properties.findall("./a:noFill", NS):
        properties.remove(no_fill)
    solid_fill = etree.Element(f"{{{NS['a']}}}solidFill")
    color = etree.SubElement(solid_fill, f"{{{NS['a']}}}srgbClr", val="805540")
    etree.SubElement(color, f"{{{NS['a']}}}alpha", val="76000")
    line = properties.find("./a:ln", NS)
    properties.insert(properties.index(line) if line is not None else len(properties), solid_fill)
    return True


def repair_slide2_announcement_fit(root: etree._Element, slide_number: int) -> bool:
    if slide_number != 2:
        return False
    matches = []
    for shape in root.findall(".//p:spTree/p:sp", NS):
        if "Announcements:" in "".join(shape.xpath(".//a:t/text()", namespaces=NS)):
            matches.append(shape)
    if len(matches) != 1:
        raise ValueError(f"Slide 2: expected one announcements text box, found {len(matches)}")
    matching_paragraphs = []
    for paragraph in matches[0].findall("./p:txBody/a:p", NS):
        text = "".join(paragraph.xpath(".//a:t/text()", namespaces=NS)).strip()
        if text.startswith("HW1 will be published on Friday, due at 6p on"):
            matching_paragraphs.append(paragraph)
    if len(matching_paragraphs) != 1:
        raise ValueError(
            f"Slide 2: expected one HW1 announcement paragraph, found {len(matching_paragraphs)}"
        )
    paragraph = matching_paragraphs[0]
    styles = paragraph.findall("./a:pPr/a:defRPr", NS)
    styles.extend(paragraph.findall("./a:r/a:rPr", NS))
    styles.extend(paragraph.findall("./a:endParaRPr", NS))
    for style in styles:
        style.set("sz", "3300")
    return True


def repair_meme_overlay(root: etree._Element) -> None:
    backing = None
    code = None
    for shape in root.findall(".//p:spTree/p:sp", NS):
        text = "".join(shape.xpath(".//a:t/text()", namespaces=NS))
        sp_pr = shape.find("./p:spPr", NS)
        if sp_pr is None:
            continue
        if not text and sp_pr.find("./a:custGeom", NS) is not None:
            alpha = sp_pr.find(".//a:alpha", NS)
            if alpha is not None and alpha.get("val") == "37000":
                backing = shape
        if text.startswith("def test_purchase_confirms_order():"):
            code = shape

    if backing is None or code is None:
        raise ValueError("Slide 9 editable code overlay or translucent backing was not found")

    # Measured from the reference page: vertices in PDF points are approximately
    # (488,90), (963,14), (984,182), and (509,229).
    set_shape_bounds(
        backing,
        x=488 * EMU_PER_POINT,
        y=14 * EMU_PER_POINT,
        w=496 * EMU_PER_POINT,
        h=215 * EMU_PER_POINT,
    )
    path = backing.find("./p:spPr/a:custGeom/a:pathLst/a:path", NS)
    if path is None:
        raise ValueError("Slide 9 translucent backing path is missing")
    path.set("w", "25023")
    path.set("h", "10566")
    points = [(0, 3735), (23963, 0), (25023, 8258), (1059, 10566), (0, 3735)]
    path_children = list(path)
    if len(path_children) != len(points) + 1:
        raise ValueError("Unexpected slide 9 custom path; refusing to rewrite it")
    for node, point in zip(path_children, points):
        xy = node.find("./a:pt", NS)
        if xy is None:
            raise ValueError("Unexpected slide 9 path point")
        xy.set("x", str(point[0]))
        xy.set("y", str(point[1]))

    # Rotate the editable code to follow the reference's ~9 degree upward slope.
    set_shape_bounds(
        code,
        x=488 * EMU_PER_POINT,
        y=34 * EMU_PER_POINT,
        w=709 * EMU_PER_POINT,
        h=136 * EMU_PER_POINT,
        rotation=21_060_000,  # 360° - 9° in DrawingML's 1/60,000-degree units.
    )
    for run_style in code.findall(".//a:rPr", NS) + code.findall(".//a:defRPr", NS):
        for script in ("latin", "ea", "cs"):
            font = run_style.find(f"./a:{script}", NS)
            if font is not None:
                font.set("typeface", "Roboto Mono")


def repair_background_title_z_order(root: etree._Element, slide_number: int, expected_title: str) -> None:
    sp_tree = root.find("./p:cSld/p:spTree", NS)
    if sp_tree is None:
        raise ValueError("Slide 10 shape tree is missing")

    matches = []
    for shape in sp_tree.findall("./p:sp", NS):
        text = "".join(shape.xpath(".//a:t/text()", namespaces=NS)).strip()
        if text == expected_title:
            matches.append(shape)
    if len(matches) != 1:
        raise ValueError(
            f"Slide {slide_number}: expected one {expected_title!r} title shape, found {len(matches)}"
        )
    if not sp_tree.findall("./p:pic", NS):
        raise ValueError(f"Slide {slide_number}: background image is missing")

    # Later shape-tree elements render in front of earlier ones. Keep the
    # native title text and move it above the image, as shown in the PDF.
    title = matches[0]
    sp_tree.remove(title)
    extension_list = sp_tree.find("./p:extLst", NS)
    if extension_list is None:
        sp_tree.append(title)
    else:
        sp_tree.insert(sp_tree.index(extension_list), title)

    if slide_number == 37:
        # This heading wraps across its underline at 60 pt after import.
        # The source PDF shows one line; reduce only this title to 48 pt.
        for style in (
            title.findall(".//a:rPr", NS)
            + title.findall(".//a:defRPr", NS)
            + title.findall(".//a:endParaRPr", NS)
        ):
            style.set("sz", "4800")


def add_anatomy_background_wash(root: etree._Element, slide_number: int) -> bool:
    sp_tree = root.find("./p:cSld/p:spTree", NS)
    if sp_tree is None:
        raise ValueError(f"Slide {slide_number} shape tree is missing")
    if any(
        node.get("name") == BACKGROUND_WASH_NAME
        for node in sp_tree.findall(".//p:cNvPr", NS)
    ):
        return False

    pictures = sp_tree.findall("./p:pic", NS)
    if not pictures:
        raise ValueError(f"Slide {slide_number} anatomy image is missing")
    def picture_area(picture: etree._Element) -> int:
        ext = picture.find("./p:spPr/a:xfrm/a:ext", NS)
        if ext is None:
            return 0
        return int(ext.get("cx", "0")) * int(ext.get("cy", "0"))
    background_picture = max(pictures, key=picture_area)
    if picture_area(background_picture) == 0:
        raise ValueError(f"Slide {slide_number} background image bounds are missing")

    shape = etree.Element(f"{{{NS['p']}}}sp")
    nv_sp_pr = etree.SubElement(shape, f"{{{NS['p']}}}nvSpPr")
    max_id = max(
        (int(value) for value in sp_tree.xpath(".//p:cNvPr/@id", namespaces=NS)),
        default=0,
    )
    etree.SubElement(
        nv_sp_pr,
        f"{{{NS['p']}}}cNvPr",
        id=str(max_id + 1),
        name=BACKGROUND_WASH_NAME,
    )
    etree.SubElement(nv_sp_pr, f"{{{NS['p']}}}cNvSpPr")
    etree.SubElement(nv_sp_pr, f"{{{NS['p']}}}nvPr")

    sp_pr = etree.SubElement(shape, f"{{{NS['p']}}}spPr")
    xfrm = etree.SubElement(sp_pr, f"{{{NS['a']}}}xfrm")
    etree.SubElement(xfrm, f"{{{NS['a']}}}off", x="0", y="0")
    etree.SubElement(
        xfrm,
        f"{{{NS['a']}}}ext",
        cx=str(SLIDE_WIDTH),
        cy=str(SLIDE_HEIGHT),
    )
    geometry = etree.SubElement(sp_pr, f"{{{NS['a']}}}prstGeom", prst="rect")
    etree.SubElement(geometry, f"{{{NS['a']}}}avLst")
    fill = etree.SubElement(sp_pr, f"{{{NS['a']}}}solidFill")
    color = etree.SubElement(fill, f"{{{NS['a']}}}srgbClr", val="FFFFFF")
    etree.SubElement(color, f"{{{NS['a']}}}alpha", val="72000")
    line = etree.SubElement(sp_pr, f"{{{NS['a']}}}ln", w="0")
    etree.SubElement(line, f"{{{NS['a']}}}noFill")

    text_body = etree.SubElement(shape, f"{{{NS['p']}}}txBody")
    etree.SubElement(text_body, f"{{{NS['a']}}}bodyPr")
    etree.SubElement(text_body, f"{{{NS['a']}}}lstStyle")
    paragraph = etree.SubElement(text_body, f"{{{NS['a']}}}p")
    etree.SubElement(paragraph, f"{{{NS['a']}}}endParaRPr", lang="en-US")

    # Insert above the anatomy image, then restore the title to the front.
    sp_tree.insert(sp_tree.index(background_picture) + 1, shape)
    return True


def repair_percent_callout_font(root: etree._Element, slide_number: int) -> bool:
    if slide_number not in PERCENT_CALLOUT_SLIDES:
        return False
    matches = []
    for shape in root.findall(".//p:spTree/p:sp", NS):
        text = "".join(shape.xpath(".//a:t/text()", namespaces=NS)).strip()
        if text == "25%":
            matches.append(shape)
    if len(matches) != 1:
        raise ValueError(
            f"Slide {slide_number}: expected one 25% callout, found {len(matches)}"
        )
    # The imported 88 pt text wraps the percent sign below the number in
    # Google's 4:3 rendering. At 50 pt it remains a single editable text run.
    for style in (
        matches[0].findall(".//a:rPr", NS)
        + matches[0].findall(".//a:defRPr", NS)
        + matches[0].findall(".//a:endParaRPr", NS)
    ):
        style.set("sz", "5000")
    return True


def repair_statistic_phrase(root: etree._Element, slide_number: int) -> bool:
    if slide_number != 30:
        return False
    matches = []
    for shape in root.findall(".//p:spTree/p:sp", NS):
        text = " ".join("".join(shape.xpath(".//a:t/text()", namespaces=NS)).split())
        if text == "of faults are integration-related!":
            matches.append(shape)
    if len(matches) != 1:
        raise ValueError(
            f"Slide 30: expected one integration-fault caption, found {len(matches)}"
        )

    shape = matches[0]
    text_body = shape.find("./p:txBody", NS)
    if text_body is None:
        raise ValueError("Slide 30: integration-fault caption text body is missing")
    set_shape_bounds(
        shape,
        x=488 * EMU_PER_POINT,
        y=563 * EMU_PER_POINT,
        w=283 * EMU_PER_POINT,
        h=75 * EMU_PER_POINT,
    )
    body = text_body.find("./a:bodyPr", NS)
    if body is None:
        raise ValueError("Slide 30: integration-fault caption body properties are missing")
    for attr in ("lIns", "rIns", "tIns", "bIns"):
        body.set(attr, "0")
    body.set("anchor", "ctr")
    for child in list(body):
        if etree.QName(child).localname in {"noAutofit", "normAutofit", "spAutoFit"}:
            body.remove(child)
    etree.SubElement(body, f"{{{NS['a']}}}noAutofit")
    for paragraph in text_body.findall("./a:p", NS):
        text_body.remove(paragraph)

    def add_caption_line(value: str) -> None:
        paragraph = etree.SubElement(text_body, f"{{{NS['a']}}}p")
        etree.SubElement(paragraph, f"{{{NS['a']}}}pPr", algn="l")
        run = etree.SubElement(paragraph, f"{{{NS['a']}}}r")
        style = etree.SubElement(run, f"{{{NS['a']}}}rPr", lang="en-US", sz="2400")
        fill = etree.SubElement(style, f"{{{NS['a']}}}solidFill")
        etree.SubElement(fill, f"{{{NS['a']}}}srgbClr", val="FFFFFF")
        etree.SubElement(style, f"{{{NS['a']}}}latin", typeface="Arial")
        etree.SubElement(run, f"{{{NS['a']}}}t").text = value
        etree.SubElement(paragraph, f"{{{NS['a']}}}endParaRPr", lang="en-US", sz="2400")

    add_caption_line("of faults are")
    add_caption_line("integration-related!")
    return True


def repair_observe_callout(root: etree._Element, slide_number: int) -> bool:
    if slide_number != 26:
        return False
    matches = []
    for shape in root.findall(".//p:spTree/p:sp", NS):
        text = "".join(shape.xpath(".//a:t/text()", namespaces=NS)).strip()
        if text.startswith("Observe: An experiment (or test) is only as good"):
            matches.append(shape)
    if len(matches) != 1:
        raise ValueError(f"Slide 26: expected one Observe callout, found {len(matches)}")
    shape = matches[0]
    text_body = shape.find("./p:txBody", NS)
    if text_body is None:
        raise ValueError("Slide 26: Observe callout paragraph is missing")
    set_shape_bounds(
        shape,
        x=166 * EMU_PER_POINT,
        y=292 * EMU_PER_POINT,
        w=620 * EMU_PER_POINT,
        h=80 * EMU_PER_POINT,
    )
    body = text_body.find("./a:bodyPr", NS)
    if body is None:
        raise ValueError("Slide 26: Observe callout body properties are missing")
    for attr in ("lIns", "rIns", "tIns", "bIns"):
        body.set(attr, "0")
    body.set("anchor", "ctr")
    for paragraph in text_body.findall("./a:p", NS):
        text_body.remove(paragraph)

    def add_run(paragraph: etree._Element, value: str, *, bold: bool = False) -> None:
        run = etree.SubElement(paragraph, f"{{{NS['a']}}}r")
        style = etree.SubElement(
            run,
            f"{{{NS['a']}}}rPr",
            lang="en-US",
            sz="2000",
            **({"b": "1"} if bold else {}),
        )
        fill = etree.SubElement(style, f"{{{NS['a']}}}solidFill")
        etree.SubElement(fill, f"{{{NS['a']}}}srgbClr", val="FFFFFF")
        etree.SubElement(style, f"{{{NS['a']}}}latin", typeface="Arial")
        etree.SubElement(run, f"{{{NS['a']}}}t").text = value

    first = etree.SubElement(text_body, f"{{{NS['a']}}}p")
    add_run(first, "Observe:", bold=True)
    add_run(first, " An experiment (or test) is only")
    etree.SubElement(first, f"{{{NS['a']}}}endParaRPr", lang="en-US", sz="2000")
    second = etree.SubElement(text_body, f"{{{NS['a']}}}p")
    add_run(second, "as good as the assumptions it makes.")
    etree.SubElement(second, f"{{{NS['a']}}}endParaRPr", lang="en-US", sz="2000")
    return True


def add_slide36_logo_picture(root: etree._Element) -> None:
    sp_tree = root.find("./p:cSld/p:spTree", NS)
    if sp_tree is None:
        raise ValueError("Slide 36 shape tree is missing")
    if any(node.get("name") == LOGO_PATCH_NAME for node in sp_tree.findall(".//p:cNvPr", NS)):
        return

    used_ids = [int(value) for value in sp_tree.xpath(".//p:cNvPr/@id", namespaces=NS)]
    picture = etree.Element(f"{{{NS['p']}}}pic")
    nv_pic = etree.SubElement(picture, f"{{{NS['p']}}}nvPicPr")
    etree.SubElement(
        nv_pic,
        f"{{{NS['p']}}}cNvPr",
        id=str(max(used_ids, default=0) + 1),
        name=LOGO_PATCH_NAME,
    )
    etree.SubElement(nv_pic, f"{{{NS['p']}}}cNvPicPr")
    etree.SubElement(nv_pic, f"{{{NS['p']}}}nvPr")

    fill = etree.SubElement(picture, f"{{{NS['p']}}}blipFill")
    etree.SubElement(fill, f"{{{NS['a']}}}blip", {f"{{{NS['r']}}}embed": LOGO_PATCH_REL_ID})
    stretch = etree.SubElement(fill, f"{{{NS['a']}}}stretch")
    etree.SubElement(stretch, f"{{{NS['a']}}}fillRect")

    properties = etree.SubElement(picture, f"{{{NS['p']}}}spPr")
    xfrm = etree.SubElement(properties, f"{{{NS['a']}}}xfrm")
    etree.SubElement(xfrm, f"{{{NS['a']}}}off", x="0", y=str(588 * EMU_PER_POINT))
    etree.SubElement(
        xfrm,
        f"{{{NS['a']}}}ext",
        cx=str(330 * EMU_PER_POINT),
        cy=str(132 * EMU_PER_POINT),
    )
    geometry = etree.SubElement(properties, f"{{{NS['a']}}}prstGeom", prst="rect")
    etree.SubElement(geometry, f"{{{NS['a']}}}avLst")
    extension_list = sp_tree.find("./p:extLst", NS)
    sp_tree.insert(sp_tree.index(extension_list) if extension_list is not None else len(sp_tree), picture)


def add_slide4_diagram_picture(root: etree._Element) -> None:
    """Cover only the converted state diagram with its reference-PDF crop."""
    sp_tree = root.find("./p:cSld/p:spTree", NS)
    if sp_tree is None:
        raise ValueError("Slide 4 shape tree is missing")
    if any(node.get("name") == DIAGRAM_PATCH_NAME for node in sp_tree.findall(".//p:cNvPr", NS)):
        return

    used_ids = [int(value) for value in sp_tree.xpath(".//p:cNvPr/@id", namespaces=NS)]
    picture = etree.Element(f"{{{NS['p']}}}pic")
    nv_pic = etree.SubElement(picture, f"{{{NS['p']}}}nvPicPr")
    etree.SubElement(
        nv_pic,
        f"{{{NS['p']}}}cNvPr",
        id=str(max(used_ids, default=0) + 1),
        name=DIAGRAM_PATCH_NAME,
    )
    etree.SubElement(nv_pic, f"{{{NS['p']}}}cNvPicPr")
    etree.SubElement(nv_pic, f"{{{NS['p']}}}nvPr")

    fill = etree.SubElement(picture, f"{{{NS['p']}}}blipFill")
    etree.SubElement(
        fill,
        f"{{{NS['a']}}}blip",
        {f"{{{NS['r']}}}embed": DIAGRAM_PATCH_REL_ID},
    )
    stretch = etree.SubElement(fill, f"{{{NS['a']}}}stretch")
    etree.SubElement(stretch, f"{{{NS['a']}}}fillRect")

    properties = etree.SubElement(picture, f"{{{NS['p']}}}spPr")
    xfrm = etree.SubElement(properties, f"{{{NS['a']}}}xfrm")
    etree.SubElement(xfrm, f"{{{NS['a']}}}off", x="0", y=str(int(446.4 * EMU_PER_POINT)))
    etree.SubElement(
        xfrm,
        f"{{{NS['a']}}}ext",
        cx=str(SLIDE_WIDTH),
        cy=str(int(321.6 * EMU_PER_POINT)),
    )
    geometry = etree.SubElement(properties, f"{{{NS['a']}}}prstGeom", prst="rect")
    etree.SubElement(geometry, f"{{{NS['a']}}}avLst")
    extension_list = sp_tree.find("./p:extLst", NS)
    sp_tree.insert(sp_tree.index(extension_list) if extension_list is not None else len(sp_tree), picture)


def add_slide36_logo_relationship(data: bytes) -> bytes:
    root = etree.fromstring(data)
    for rel in root.findall("./rel:Relationship", NS):
        if rel.get("Target") == "../media/round16-slide36-missing-logos.png":
            return data
    used = {rel.get("Id") for rel in root.findall("./rel:Relationship", NS)}
    rel_id = LOGO_PATCH_REL_ID
    while rel_id in used:
        number = int(rel_id.removeprefix("rId")) + 1
        rel_id = f"rId{number}"
    etree.SubElement(
        root,
        f"{{{NS['rel']}}}Relationship",
        Id=rel_id,
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
        Target="../media/round16-slide36-missing-logos.png",
    )
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def add_slide4_diagram_relationship(data: bytes) -> bytes:
    root = etree.fromstring(data)
    for rel in root.findall("./rel:Relationship", NS):
        if rel.get("Target") == DIAGRAM_PATCH_TARGET:
            return data
    used = {rel.get("Id") for rel in root.findall("./rel:Relationship", NS)}
    rel_id = DIAGRAM_PATCH_REL_ID
    while rel_id in used:
        number = int(rel_id.removeprefix("rId")) + 1
        rel_id = f"rId{number}"
    if rel_id != DIAGRAM_PATCH_REL_ID:
        raise ValueError(
            f"Slide 4 image relationship must be {DIAGRAM_PATCH_REL_ID}, got {rel_id}; "
            "update the picture relationship ID to match"
        )
    etree.SubElement(
        root,
        f"{{{NS['rel']}}}Relationship",
        Id=rel_id,
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
        Target=DIAGRAM_PATCH_TARGET,
    )
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def ensure_png_content_type(data: bytes) -> bytes:
    root = etree.fromstring(data)
    if not any(node.get("Extension", "").lower() == "png" for node in root.findall("./ct:Default", NS)):
        etree.SubElement(
            root,
            f"{{{NS['ct']}}}Default",
            Extension="png",
            ContentType="image/png",
        )
        return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    return data


def transparent_chain_logo(data: bytes) -> bytes:
    """Remove the opaque white matte from the source slide's black chain mark."""
    image = Image.open(BytesIO(data)).convert("RGBA")
    if image.size != (340, 340):
        raise ValueError(f"Expected the slide 36 chain logo to be 340x340 px, got {image.size}")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = pixels[x, y]
            if max(red, green, blue) - min(red, green, blue) <= 4:
                gray = (red + green + blue) // 3
                alpha = round(alpha * (255 - gray) / 255)
                pixels[x, y] = (0, 0, 0, alpha)
    result = BytesIO()
    image.save(result, format="PNG", optimize=True)
    return result.getvalue()


def repair(
    input_path: Path,
    output_path: Path,
    logo_patch_path: Path = DEFAULT_LOGO_PATCH,
    chain_logo_path: Path = DEFAULT_CHAIN_LOGO,
    diagram_patch_path: Path = DEFAULT_DIAGRAM_PATCH,
) -> dict[str, int]:
    if not logo_patch_path.is_file():
        raise FileNotFoundError(f"Slide 36 logo patch is missing: {logo_patch_path}")
    logo_patch_bytes = logo_patch_path.read_bytes()
    if not diagram_patch_path.is_file():
        raise FileNotFoundError(f"Slide 4 diagram patch is missing: {diagram_patch_path}")
    diagram_patch_bytes = diagram_patch_path.read_bytes()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    question_edits = 0
    question_retained = 0
    slide_count = 0
    background_washes_added = 0
    percent_callout_repairs = 0
    statistic_caption_repairs = 0
    observe_callout_repairs = 0
    logo_patch_added = 0
    chain_logo_repaired = 0
    slide1_gradient_removed = 0
    slide2_empty_bullets_removed = 0
    slide4_diagram_patch_added = 0
    slide1_title_banner_repaired = 0
    slide2_announcement_fit_repaired = 0

    with ZipFile(input_path) as source, ZipFile(output_path, "w", ZIP_DEFLATED) as target:
        if CHAIN_LOGO_PART not in source.namelist():
            raise FileNotFoundError(f"Slide 36 chain logo image is missing: {CHAIN_LOGO_PART}")
        chain_logo_bytes = transparent_chain_logo(source.read(CHAIN_LOGO_PART))
        chain_logo_path.parent.mkdir(parents=True, exist_ok=True)
        chain_logo_path.write_bytes(chain_logo_bytes)
        for info in source.infolist():
            data = source.read(info.filename)
            match = re.fullmatch(r"ppt/slides/slide([0-9]+)\.xml", info.filename)
            if match:
                slide_number = int(match.group(1))
                slide_count += 1
                root = etree.fromstring(data)
                original_canonical_xml = etree.tostring(root, method="c14n")
                edits, retained = repair_question_heading(root, slide_number)
                question_edits += edits
                question_retained += int(retained and edits > 0)
                slide1_gradient_removed += int(remove_slide1_gradient(root, slide_number))
                slide2_empty_bullets_removed += remove_slide2_empty_bullets(root, slide_number)
                slide1_title_banner_repaired += int(repair_slide1_title_banner(root, slide_number))
                slide2_announcement_fit_repaired += int(
                    repair_slide2_announcement_fit(root, slide_number)
                )
                if slide_number == 9:
                    repair_meme_overlay(root)
                if slide_number in BACKGROUND_TITLE_SLIDES:
                    background_washes_added += int(
                        add_anatomy_background_wash(root, slide_number)
                    )
                    repair_background_title_z_order(
                        root,
                        slide_number,
                        BACKGROUND_TITLE_SLIDES[slide_number],
                    )
                percent_callout_repairs += int(
                    repair_percent_callout_font(root, slide_number)
                )
                statistic_caption_repairs += int(
                    repair_statistic_phrase(root, slide_number)
                )
                observe_callout_repairs += int(
                    repair_observe_callout(root, slide_number)
                )
                if slide_number == 36:
                    add_slide36_logo_picture(root)
                    logo_patch_added = 1
                if slide_number == 4:
                    add_slide4_diagram_picture(root)
                    slide4_diagram_patch_added = 1
                if etree.tostring(root, method="c14n") != original_canonical_xml:
                    data = etree.tostring(
                        root,
                        xml_declaration=True,
                        encoding="UTF-8",
                        standalone=True,
                    )
            elif info.filename == "ppt/slides/_rels/slide4.xml.rels":
                data = add_slide4_diagram_relationship(data)
            elif info.filename == "ppt/slides/_rels/slide36.xml.rels":
                data = add_slide36_logo_relationship(data)
            elif info.filename == CHAIN_LOGO_PART:
                data = chain_logo_bytes
                chain_logo_repaired = 1
            elif info.filename == "[Content_Types].xml":
                data = ensure_png_content_type(data)
            target.writestr(info, data)
        target.writestr(LOGO_PATCH_PART, logo_patch_bytes)
        target.writestr(DIAGRAM_PATCH_PART, diagram_patch_bytes)

    if slide_count != 38:
        output_path.unlink(missing_ok=True)
        raise ValueError(f"Expected 38 source slides, found {slide_count}")
    if question_retained != 3:
        output_path.unlink(missing_ok=True)
        raise ValueError(f"Expected to retain the heading on 3 source slides, retained {question_retained}")
    if chain_logo_repaired != 1:
        output_path.unlink(missing_ok=True)
        raise ValueError("Expected to replace the opaque slide 36 chain logo image")
    if (
        slide1_gradient_removed != 1
        or slide2_empty_bullets_removed != 2
        or slide4_diagram_patch_added != 1
        or slide1_title_banner_repaired != 1
        or slide2_announcement_fit_repaired != 1
    ):
        output_path.unlink(missing_ok=True)
        raise ValueError(
            "Round 16 targeted repairs did not match expectations: "
            f"slide1_gradient={slide1_gradient_removed}, "
            f"slide2_empty_bullets={slide2_empty_bullets_removed}, "
            f"slide4_diagram={slide4_diagram_patch_added}, "
            f"slide1_title_banner={slide1_title_banner_repaired}, "
            f"slide2_announcement_fit={slide2_announcement_fit_repaired}"
        )

    with ZipFile(output_path) as checked:
        bad_member = checked.testzip()
    if bad_member:
        output_path.unlink(missing_ok=True)
        raise ValueError(f"PPTX package integrity check failed at {bad_member}")

    return {
        "source_slides": slide_count,
        "question_shapes_repaired_or_removed": question_edits,
        "question_slides_retained": question_retained,
        "meme_overlay_shapes_repaired": 2,
        "background_title_zorders_repaired": len(BACKGROUND_TITLE_SLIDES),
        "background_washes_added": background_washes_added,
        "percent_callout_font_repairs": percent_callout_repairs,
        "statistic_caption_repairs": statistic_caption_repairs,
        "observe_callout_repairs": observe_callout_repairs,
        "slide36_logo_patch_added": logo_patch_added,
        "slide36_chain_logo_background_removed": chain_logo_repaired,
        "slide1_unsupported_gradient_removed": slide1_gradient_removed,
        "slide2_empty_bullets_removed": slide2_empty_bullets_removed,
        "slide4_diagram_region_patched": slide4_diagram_patch_added,
        "slide1_title_banner_repaired": slide1_title_banner_repaired,
        "slide2_announcement_font_fit": slide2_announcement_fit_repaired,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--slide36-logo-patch", type=Path, default=DEFAULT_LOGO_PATCH)
    parser.add_argument("--slide36-chain-logo", type=Path, default=DEFAULT_CHAIN_LOGO)
    parser.add_argument("--slide4-diagram-patch", type=Path, default=DEFAULT_DIAGRAM_PATCH)
    args = parser.parse_args()
    print(
        repair(
            args.input,
            args.output,
            args.slide36_logo_patch,
            args.slide36_chain_logo,
            args.slide4_diagram_patch,
        )
    )


if __name__ == "__main__":
    main()
