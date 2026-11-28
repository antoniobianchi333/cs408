#!/usr/bin/env python3
"""Assemble ordered, editable PPTX candidates from mapped source PPTX files.

The manifest must list source decks in batch order. Each map CSV must contain
`reference_pdf_page` and `converted_pptx_slide` columns produced by
audit_batch_source_alignment.py. The builder adds a full-slide solid pale-yellow
(`#FFF2CC`) editable divider before each source deck, with centered 24 pt bold
Arial filename text and 28 pt regular Arial topic text. Divider text boxes use
explicit DrawingML rectangle geometry. The builder copies selected slides
and notes, sets speaker-note text to 8 pt, and records every output page. It
deliberately does not expand Keynote animation builds or repair imported
layouts; the output map labels those items as pending.

This package-level copier supports LibreOffice PPTX inputs whose slide
relationships point only to slide layouts, images, and speaker notes. It
requires the source decks to share identical slide master and theme parts.

Example:
  python3 out/combined/build_batch_candidate.py \
    --manifest out/combined/final-batches/batch-01-inputs.json \
    --output out/.build/batch-01/assembled/batch-01-static-candidate.pptx \
    --map-output out/.build/batch-01/assembled/batch-01-candidate-map.csv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import posixpath
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"p": P, "a": A, "r": R, "rel": REL, "ct": CT}
SLIDE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
LAYOUT_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"
MASTER_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster"
PRES_MASTER_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster"
THEME_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"
NOTES_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
NOTES_MASTER_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster"
IMAGE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
SLIDE_CT = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
LAYOUT_CT = "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"
MASTER_CT = "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"
NOTES_CT = "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"


def xml_bytes(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def rels_path(part: str) -> str:
    folder, name = posixpath.split(part)
    return posixpath.join(folder, "_rels", f"{name}.rels")


def resolve_target(source_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(source_part), target))


def relative_target(source_part: str, target_part: str) -> str:
    return posixpath.relpath(target_part, posixpath.dirname(source_part))


def load_zip(path: Path) -> dict[str, bytes]:
    with ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"{path}: corrupt ZIP member {bad}")
        return {item.filename: archive.read(item.filename) for item in archive.infolist()}


def rel_root(parts: dict[str, bytes], part: str) -> etree._Element:
    name = rels_path(part)
    if name not in parts:
        raise ValueError(f"missing relationship part {name}")
    return etree.fromstring(parts[name])


def presentation_slides(parts: dict[str, bytes]) -> tuple[etree._Element, etree._Element, list[tuple[int, etree._Element, str]]]:
    root = etree.fromstring(parts["ppt/presentation.xml"])
    rels = etree.fromstring(parts["ppt/_rels/presentation.xml.rels"])
    relmap = {r.get("Id"): r for r in rels.findall("rel:Relationship", NS)}
    slide_list = root.find("p:sldIdLst", NS)
    if slide_list is None:
        raise ValueError("presentation has no p:sldIdLst")
    result = []
    for position, node in enumerate(slide_list.findall("p:sldId", NS), start=1):
        rel = relmap.get(node.get(f"{{{R}}}id"))
        if rel is None or rel.get("Type") != SLIDE_REL:
            raise ValueError(f"slide {position}: presentation relationship is missing or not a slide")
        result.append((position, node, resolve_target("ppt/presentation.xml", rel.get("Target"))))
    return root, rels, result


def map_rows(path: Path, slide_count: int) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        raise ValueError(f"empty page map: {path}")
    pages = [int(row["reference_pdf_page"]) for row in rows]
    candidates = [int(row["converted_pptx_slide"]) for row in rows]
    if pages != list(range(1, len(rows) + 1)):
        raise ValueError(f"{path}: reference pages must be consecutive from 1")
    if len(candidates) != len(set(candidates)):
        raise ValueError(f"{path}: a candidate PPTX slide is mapped more than once")
    if candidates != sorted(candidates):
        raise ValueError(f"{path}: candidate PPTX slides are not in source order")
    if min(candidates) < 1 or max(candidates) > slide_count:
        raise ValueError(f"{path}: candidate slide number is outside the PPTX")
    return rows


def build_hints(path: Path | None) -> dict[int, tuple[str, str]]:
    if path is None:
        return {}
    grouped: dict[int, dict[str, set[str]]] = {}
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            pages = [int(value) for value in row.get("mapped_reference_pdf_pages", "").split(";") if value]
            for page in pages:
                item = grouped.setdefault(page, {"effects": set(), "groups": set()})
                item["effects"].update(value for value in row.get("effect_markers", "").split(";") if value)
                item["groups"].update(value for value in row.get("build_grouping_hints", "").split(";") if value)
    return {
        page: (";".join(sorted(values["effects"])), ";".join(sorted(values["groups"])))
        for page, values in grouped.items()
    }


def add_override(content_types: etree._Element, part: str, content_type: str) -> None:
    name = "/" + part
    for node in content_types.findall("ct:Override", NS):
        if node.get("PartName") == name:
            node.set("ContentType", content_type)
            return
    etree.SubElement(content_types, f"{{{CT}}}Override", PartName=name, ContentType=content_type)


def add_default_if_needed(output: dict[str, bytes], source: dict[str, bytes], extension: str) -> None:
    root = etree.fromstring(output["[Content_Types].xml"])
    if any(node.get("Extension", "").lower() == extension.lower() for node in root.findall("ct:Default", NS)):
        return
    source_root = etree.fromstring(source["[Content_Types].xml"])
    match = next(
        (node for node in source_root.findall("ct:Default", NS)
         if node.get("Extension", "").lower() == extension.lower()),
        None,
    )
    if match is None:
        raise ValueError(f"no content type is declared for media extension .{extension}")
    root.append(etree.fromstring(etree.tostring(match)))
    output["[Content_Types].xml"] = xml_bytes(root)


def find_single_part(parts: dict[str, bytes], pattern: str, what: str) -> str:
    matches = [name for name in parts if re.fullmatch(pattern, name)]
    if len(matches) != 1:
        raise ValueError(f"expected one {what}, found {len(matches)}")
    return matches[0]


def parts_matching(parts: dict[str, bytes], pattern: str, what: str) -> list[str]:
    matches = sorted(name for name in parts if re.fullmatch(pattern, name))
    if not matches:
        raise ValueError(f"no {what} parts found")
    return matches


def check_shared_design(base: dict[str, bytes], other: dict[str, bytes], label: str) -> None:
    base_themes = parts_matching(base, r"ppt/theme/theme\d+\.xml", "base theme")
    other_themes = parts_matching(other, r"ppt/theme/theme\d+\.xml", f"{label} theme")
    base_theme_hashes = {hashlib.sha256(base[name]).digest() for name in base_themes}
    if any(hashlib.sha256(other[name]).digest() not in base_theme_hashes for name in other_themes):
        raise ValueError(f"{label}: theme differs from the base PPTX; refusing unsafe merge")
    base_root = etree.fromstring(base["ppt/presentation.xml"])
    other_root = etree.fromstring(other["ppt/presentation.xml"])
    base_size = base_root.find("p:sldSz", NS)
    other_size = other_root.find("p:sldSz", NS)
    if base_size is None or other_size is None or (base_size.get("cx"), base_size.get("cy")) != (other_size.get("cx"), other_size.get("cy")):
        raise ValueError(f"{label}: slide dimensions differ from the base PPTX")


def add_presentation_master(pres_root: etree._Element, pres_rels: etree._Element,
                            target_part: str, rel_serial: list[int],
                            master_id_serial: list[int]) -> None:
    master_list = pres_root.find("p:sldMasterIdLst", NS)
    if master_list is None:
        raise ValueError("presentation has no p:sldMasterIdLst")
    rel_serial[0] += 1
    rel_id = f"rId{rel_serial[0]}"
    etree.SubElement(
        pres_rels,
        f"{{{REL}}}Relationship",
        Id=rel_id,
        Type=PRES_MASTER_REL,
        Target=relative_target("ppt/presentation.xml", target_part),
    )
    master_id_serial[0] += 1
    node = etree.SubElement(master_list, f"{{{P}}}sldMasterId", id=str(master_id_serial[0]))
    node.set(f"{{{R}}}id", rel_id)


def next_part_number(parts: dict[str, bytes], regex: str) -> int:
    values = [int(match.group(1)) for name in parts if (match := re.fullmatch(regex, name))]
    return max(values, default=0) + 1


def image_copy(source: dict[str, bytes], output: dict[str, bytes], source_part: str,
               image_cache: dict[str, str], deck_index: int, serial: list[int]) -> str:
    cache_key = f"{deck_index}:{source_part}"
    if cache_key in image_cache:
        return image_cache[cache_key]
    if source_part not in source:
        raise ValueError(f"missing image part {source_part}")
    extension = Path(source_part).suffix.lstrip(".").lower()
    if not extension:
        raise ValueError(f"image part has no extension: {source_part}")
    add_default_if_needed(output, source, extension)
    serial[0] += 1
    target = f"ppt/media/batch{deck_index:02d}-image{serial[0]:04d}.{extension}"
    output[target] = source[source_part]
    image_cache[cache_key] = target
    return target


def copy_layout(source: dict[str, bytes], output: dict[str, bytes], source_part: str,
                layout_cache: dict[str, str], deck_index: int, layout_serial: list[int],
                image_cache: dict[str, str], image_serial: list[int],
                master_cache: dict[str, str], master_serial: list[int],
                master_id_serial: list[int], base_masters_by_hash: dict[bytes, str],
                base_theme: str, pres_root: etree._Element, pres_rels: etree._Element,
                rel_serial: list[int]) -> str:
    cache_key = f"{deck_index}:{source_part}"
    if cache_key in layout_cache:
        return layout_cache[cache_key]
    if source_part not in source:
        raise ValueError(f"missing layout part {source_part}")
    layout_serial[0] += 1
    target_part = f"ppt/slideLayouts/slideLayout{layout_serial[0]}.xml"
    output[target_part] = source[source_part]
    source_rels = rel_root(source, source_part)
    target_rels = etree.Element(f"{{{REL}}}Relationships", nsmap={None: REL})
    for rel in source_rels.findall("rel:Relationship", NS):
        copied = etree.fromstring(etree.tostring(rel))
        rel_type = rel.get("Type")
        source_target = resolve_target(source_part, rel.get("Target"))
        if rel_type == MASTER_REL:
            master_part = copy_master(
                source, output, source_target, master_cache, deck_index, master_serial,
                master_id_serial, layout_cache, layout_serial, image_cache, image_serial,
                base_masters_by_hash, base_theme, pres_root, pres_rels, rel_serial,
            )
            copied.set("Target", relative_target(target_part, master_part))
        elif rel_type == IMAGE_REL:
            image_part = image_copy(source, output, source_target, image_cache, deck_index, image_serial)
            copied.set("Target", relative_target(target_part, image_part))
        else:
            raise ValueError(f"unsupported layout relationship {rel_type} in {source_part}")
        target_rels.append(copied)
    output[rels_path(target_part)] = xml_bytes(target_rels)
    ct_root = etree.fromstring(output["[Content_Types].xml"])
    add_override(ct_root, target_part, LAYOUT_CT)
    output["[Content_Types].xml"] = xml_bytes(ct_root)
    layout_cache[cache_key] = target_part
    return target_part


def copy_master(source: dict[str, bytes], output: dict[str, bytes], source_part: str,
                master_cache: dict[str, str], deck_index: int, master_serial: list[int],
                master_id_serial: list[int], layout_cache: dict[str, str],
                layout_serial: list[int], image_cache: dict[str, str], image_serial: list[int],
                base_masters_by_hash: dict[bytes, str], base_theme: str,
                pres_root: etree._Element, pres_rels: etree._Element,
                rel_serial: list[int]) -> str:
    cache_key = f"{deck_index}:{source_part}"
    if cache_key in master_cache:
        return master_cache[cache_key]
    if source_part not in source:
        raise ValueError(f"missing slide master part {source_part}")
    source_hash = hashlib.sha256(source[source_part]).digest()
    if source_hash in base_masters_by_hash:
        target_part = base_masters_by_hash[source_hash]
        master_cache[cache_key] = target_part
        return target_part

    master_serial[0] += 1
    target_part = f"ppt/slideMasters/slideMaster{master_serial[0]}.xml"
    output[target_part] = source[source_part]
    master_cache[cache_key] = target_part
    target_rels = etree.Element(f"{{{REL}}}Relationships", nsmap={None: REL})
    for rel in rel_root(source, source_part).findall("rel:Relationship", NS):
        copied = etree.fromstring(etree.tostring(rel))
        rel_type = rel.get("Type")
        source_target = resolve_target(source_part, rel.get("Target"))
        if rel_type == THEME_REL:
            copied.set("Target", relative_target(target_part, base_theme))
        elif rel_type == LAYOUT_REL:
            layout_part = copy_layout(
                source, output, source_target, layout_cache, deck_index, layout_serial,
                image_cache, image_serial, master_cache, master_serial, master_id_serial,
                base_masters_by_hash, base_theme, pres_root, pres_rels, rel_serial,
            )
            copied.set("Target", relative_target(target_part, layout_part))
        elif rel_type == IMAGE_REL:
            image_part = image_copy(source, output, source_target, image_cache, deck_index, image_serial)
            copied.set("Target", relative_target(target_part, image_part))
        else:
            raise ValueError(f"unsupported slide-master relationship {rel_type} in {source_part}")
        target_rels.append(copied)
    output[rels_path(target_part)] = xml_bytes(target_rels)
    ct_root = etree.fromstring(output["[Content_Types].xml"])
    add_override(ct_root, target_part, MASTER_CT)
    output["[Content_Types].xml"] = xml_bytes(ct_root)
    add_presentation_master(pres_root, pres_rels, target_part, rel_serial, master_id_serial)
    base_masters_by_hash[source_hash] = target_part
    return target_part


def copy_notes(source: dict[str, bytes], output: dict[str, bytes], source_part: str,
               new_slide_part: str, notes_cache: dict[str, str], notes_serial: list[int],
               image_cache: dict[str, str], image_serial: list[int], deck_index: int,
               base_notes_master: str) -> str:
    cache_key = f"{deck_index}:{source_part}"
    if cache_key in notes_cache:
        return notes_cache[cache_key]
    if source_part not in source:
        raise ValueError(f"missing notes slide part {source_part}")
    notes_serial[0] += 1
    target_part = f"ppt/notesSlides/notesSlide{notes_serial[0]}.xml"
    notes_root = etree.fromstring(source[source_part])
    set_speaker_notes_font_size(notes_root)
    output[target_part] = xml_bytes(notes_root)
    source_rels = rel_root(source, source_part)
    target_rels = etree.Element(f"{{{REL}}}Relationships", nsmap={None: REL})
    for rel in source_rels.findall("rel:Relationship", NS):
        copied = etree.fromstring(etree.tostring(rel))
        rel_type = rel.get("Type")
        source_target = resolve_target(source_part, rel.get("Target"))
        if rel_type == SLIDE_REL:
            copied.set("Target", relative_target(target_part, new_slide_part))
        elif rel_type == NOTES_MASTER_REL:
            copied.set("Target", relative_target(target_part, base_notes_master))
        elif rel_type == IMAGE_REL:
            image_part = image_copy(source, output, source_target, image_cache, deck_index, image_serial)
            copied.set("Target", relative_target(target_part, image_part))
        else:
            raise ValueError(f"unsupported notes relationship {rel_type} in {source_part}")
        target_rels.append(copied)
    output[rels_path(target_part)] = xml_bytes(target_rels)
    ct_root = etree.fromstring(output["[Content_Types].xml"])
    add_override(ct_root, target_part, NOTES_CT)
    output["[Content_Types].xml"] = xml_bytes(ct_root)
    notes_cache[cache_key] = target_part
    return target_part


def set_speaker_notes_font_size(notes_root: etree._Element) -> None:
    """Set every existing speaker-note text run and paragraph default to 8 pt."""
    property_tags = {
        f"{{{A}}}rPr",
        f"{{{A}}}defRPr",
        f"{{{A}}}endParaRPr",
    }
    for node in notes_root.iter():
        if node.tag in property_tags:
            node.set("sz", "800")

    # Some source runs omit explicit properties and inherit a larger size from
    # the notes master. Add a local run property so the 8 pt rule survives import.
    for tag in ("r", "fld"):
        for run in notes_root.findall(f".//a:{tag}", NS):
            run_properties = run.find("a:rPr", NS)
            if run_properties is None:
                run_properties = etree.Element(f"{{{A}}}rPr")
                run.insert(0, run_properties)
            run_properties.set("sz", "800")


def divider_xml(filename: str, topic: str, width: int, height: int) -> bytes:
    slide = etree.Element(f"{{{P}}}sld", nsmap={"a": A, "r": R, "p": P}, showMasterSp="0")
    c_sld = etree.SubElement(slide, f"{{{P}}}cSld", name="Source deck divider")
    bg = etree.SubElement(c_sld, f"{{{P}}}bg")
    bg_pr = etree.SubElement(bg, f"{{{P}}}bgPr")
    solid = etree.SubElement(bg_pr, f"{{{A}}}solidFill")
    etree.SubElement(solid, f"{{{A}}}srgbClr", val="FFF2CC")
    etree.SubElement(bg_pr, f"{{{A}}}effectLst")
    tree = etree.SubElement(c_sld, f"{{{P}}}spTree")
    nv = etree.SubElement(tree, f"{{{P}}}nvGrpSpPr")
    etree.SubElement(nv, f"{{{P}}}cNvPr", id="1", name="")
    etree.SubElement(nv, f"{{{P}}}cNvGrpSpPr")
    etree.SubElement(nv, f"{{{P}}}nvPr")
    group = etree.SubElement(tree, f"{{{P}}}grpSpPr")
    xfrm = etree.SubElement(group, f"{{{A}}}xfrm")
    etree.SubElement(xfrm, f"{{{A}}}off", x="0", y="0")
    etree.SubElement(xfrm, f"{{{A}}}ext", cx="0", cy="0")
    etree.SubElement(xfrm, f"{{{A}}}chOff", x="0", y="0")
    etree.SubElement(xfrm, f"{{{A}}}chExt", cx="0", cy="0")

    def add_textbox(shape_id: int, name: str, text: str, y: int, h: int,
                    size: int, bold: bool) -> None:
        shape = etree.SubElement(tree, f"{{{P}}}sp")
        nv_sp = etree.SubElement(shape, f"{{{P}}}nvSpPr")
        etree.SubElement(nv_sp, f"{{{P}}}cNvPr", id=str(shape_id), name=name)
        etree.SubElement(nv_sp, f"{{{P}}}cNvSpPr", txBox="1")
        etree.SubElement(nv_sp, f"{{{P}}}nvPr")
        sp_pr = etree.SubElement(shape, f"{{{P}}}spPr")
        tx = etree.SubElement(sp_pr, f"{{{A}}}xfrm")
        etree.SubElement(tx, f"{{{A}}}off", x=str(width // 12), y=str(y))
        etree.SubElement(tx, f"{{{A}}}ext", cx=str(width - width // 6), cy=str(h))
        # Use explicit DrawingML geometry. LibreOffice renders a text box
        # without this element, but Google Slides dropped both generated
        # divider text boxes; explicit geometry makes the shape unambiguous
        # for importers, and the two-slide pilot will verify that repair.
        geometry = etree.SubElement(sp_pr, f"{{{A}}}prstGeom", prst="rect")
        etree.SubElement(geometry, f"{{{A}}}avLst")
        etree.SubElement(sp_pr, f"{{{A}}}noFill")
        line = etree.SubElement(sp_pr, f"{{{A}}}ln")
        etree.SubElement(line, f"{{{A}}}noFill")
        body = etree.SubElement(shape, f"{{{P}}}txBody")
        etree.SubElement(body, f"{{{A}}}bodyPr", wrap="square", lIns="0", rIns="0", tIns="0", bIns="0", anchor="ctr")
        etree.SubElement(body, f"{{{A}}}lstStyle")
        para = etree.SubElement(body, f"{{{A}}}p")
        etree.SubElement(para, f"{{{A}}}pPr", algn="ctr")
        run = etree.SubElement(para, f"{{{A}}}r")
        rpr = etree.SubElement(run, f"{{{A}}}rPr", lang="en-US", sz=str(size), dirty="0")
        if bold:
            rpr.set("b", "1")
        color = etree.SubElement(rpr, f"{{{A}}}solidFill")
        etree.SubElement(color, f"{{{A}}}srgbClr", val="333333")
        etree.SubElement(rpr, f"{{{A}}}latin", typeface="Arial")
        etree.SubElement(run, f"{{{A}}}t").text = text
        etree.SubElement(para, f"{{{A}}}endParaRPr", lang="en-US", sz=str(size))

    add_textbox(2, "Exact source filename", filename, int(height * 0.40), int(height * 0.10), 2400, True)
    add_textbox(3, "Following topic", topic, int(height * 0.51), int(height * 0.11), 2800, False)
    etree.SubElement(slide, f"{{{P}}}clrMapOvr").append(etree.Element(f"{{{A}}}masterClrMapping"))
    return xml_bytes(slide)


def add_presentation_rel(rels: etree._Element, rel_id: str, target: str) -> None:
    etree.SubElement(
        rels,
        f"{{{REL}}}Relationship",
        Id=rel_id,
        Type=SLIDE_REL,
        Target=target,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--map-output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    decks = manifest.get("decks", [])
    if not decks:
        raise ValueError("manifest must contain at least one source deck")

    loaded: list[dict] = []
    for item in decks:
        pptx_path = Path(item["candidate_pptx"])
        page_map_path = Path(item["page_map"])
        parts = load_zip(pptx_path)
        _, _, slides = presentation_slides(parts)
        rows = map_rows(page_map_path, len(slides))
        hints_path = Path(item["build_marker_audit"]) if item.get("build_marker_audit") else None
        loaded.append({**item, "parts": parts, "slides": slides, "rows": rows,
                       "build_hints": build_hints(hints_path), "pptx_path": pptx_path})

    output = dict(loaded[0]["parts"])
    base_master_parts = parts_matching(output, r"ppt/slideMasters/slideMaster\d+\.xml", "base slide master")
    base_masters_by_hash = {
        hashlib.sha256(output[name]).digest(): name for name in base_master_parts
    }
    base_theme_parts = parts_matching(output, r"ppt/theme/theme\d+\.xml", "base theme")
    base_theme = base_theme_parts[0]
    base_notes_master = find_single_part(output, r"ppt/notesMasters/notesMaster\d+\.xml", "base notes master")
    pres_root, pres_rels, base_slides = presentation_slides(output)

    base_by_position = {position: (node, part) for position, node, part in base_slides}
    selected_base_positions = {int(row["converted_pptx_slide"]) for row in loaded[0]["rows"]}
    for position in selected_base_positions:
        if position not in base_by_position:
            raise ValueError(f"base candidate slide {position} does not exist")

    # Existing package part names are retained; only selected slides remain in the presentation list.
    existing_sldid_ids = [
        int(node.get("id")) for node in pres_root.findall(".//p:sldId", NS)
        if node.get("id", "").isdigit()
    ]
    keep_rel_ids = {node.get(f"{{{R}}}id") for _, node, _ in base_slides if node in [base_by_position[p][0] for p in selected_base_positions]}
    for rel in list(pres_rels.findall("rel:Relationship", NS)):
        if rel.get("Type") == SLIDE_REL and rel.get("Id") not in keep_rel_ids:
            pres_rels.remove(rel)

    sld_id_lst = pres_root.find("p:sldIdLst", NS)
    preserved_non_slide_children = [child for child in sld_id_lst if child.tag != f"{{{P}}}sldId"]
    for child in list(sld_id_lst):
        sld_id_lst.remove(child)

    # Allocate new slide, relationship, layout, notes, and image part names above existing IDs.
    slide_serial = [next_part_number(output, r"ppt/slides/slide(\d+)\.xml") - 1]
    rel_serial = [max([int(m.group(1)) for r in pres_rels.findall("rel:Relationship", NS)
                       if (m := re.fullmatch(r"rId(\d+)", r.get("Id", "")))] or [0])]
    layout_serial = [next_part_number(output, r"ppt/slideLayouts/slideLayout(\d+)\.xml") - 1]
    master_serial = [next_part_number(output, r"ppt/slideMasters/slideMaster(\d+)\.xml") - 1]
    notes_serial = [next_part_number(output, r"ppt/notesSlides/notesSlide(\d+)\.xml") - 1]
    image_serial = [0]
    layout_cache: dict[str, str] = {}
    master_cache: dict[str, str] = {}
    notes_cache: dict[str, str] = {}
    image_cache: dict[str, str] = {}
    map_records: list[dict[str, str]] = []
    final_slide_count = sum(len(item["rows"]) + 1 for item in loaded)
    sldid_serial = [max(existing_sldid_ids or [255])]
    master_list = pres_root.find("p:sldMasterIdLst", NS)
    master_ids = [
        int(node.get("id")) for node in master_list.findall("p:sldMasterId", NS)
        if node.get("id", "").isdigit()
    ] if master_list is not None else []
    master_id_serial = [max(master_ids or [0])]

    def append_slide(rel_target: str, slide_node: etree._Element | None = None) -> None:
        if slide_node is None:
            rel_serial[0] += 1
            rel_id = f"rId{rel_serial[0]}"
            add_presentation_rel(pres_rels, rel_id, rel_target)
            sldid_serial[0] += 1
            slide_node = etree.Element(f"{{{P}}}sldId", id=str(sldid_serial[0]))
            slide_node.set(f"{{{R}}}id", rel_id)
        sld_id_lst.append(slide_node)

    if len(loaded) > 1:
        for item in loaded[1:]:
            check_shared_design(output, item["parts"], item["source_filename"])

    for deck_index, item in enumerate(loaded, start=1):
        source_filename = item["source_filename"]
        topic = item["topic"]
        parts = item["parts"]
        _, _, source_slides = presentation_slides(parts)
        slide_by_position = {position: (node, part) for position, node, part in source_slides}
        # Add a plain editable divider before every original source deck.
        slide_serial[0] += 1
        divider_part = f"ppt/slides/slide{slide_serial[0]}.xml"
        pres_size = pres_root.find("p:sldSz", NS)
        width, height = int(pres_size.get("cx")), int(pres_size.get("cy"))
        output[divider_part] = divider_xml(source_filename, topic, width, height)
        divider_rels = etree.Element(f"{{{REL}}}Relationships", nsmap={None: REL})
        layout_target = "ppt/slideLayouts/slideLayout1.xml"
        etree.SubElement(divider_rels, f"{{{REL}}}Relationship", Id="rId1", Type=LAYOUT_REL,
                         Target=relative_target(divider_part, layout_target))
        output[rels_path(divider_part)] = xml_bytes(divider_rels)
        ct_root = etree.fromstring(output["[Content_Types].xml"])
        add_override(ct_root, divider_part, SLIDE_CT)
        output["[Content_Types].xml"] = xml_bytes(ct_root)
        append_slide(f"slides/{Path(divider_part).name}")
        map_records.append({
            "output_slide": str(len(map_records) + 1),
            "row_type": "source_deck_divider",
            "source_filename": source_filename,
            "topic": topic,
            "source_pdf_page": "",
            "converted_pptx_slide": "",
            "speaker_notes_in_source": "no",
            "keynote_effect_markers": "",
            "keynote_grouping_hints": "",
            "build_status": "divider; no source page",
            "review_status": "verify exact filename/topic text and plain editable layout",
        })

        for row in item["rows"]:
            position = int(row["converted_pptx_slide"])
            if deck_index == 1:
                node, part = base_by_position[position]
                append_slide("", etree.fromstring(etree.tostring(node)))
                slide_rel_id = node.get(f"{{{R}}}id")
                slide_part = part
                source_note = any(r.get("Type") == NOTES_REL for r in rel_root(output, slide_part).findall("rel:Relationship", NS))
            else:
                _, source_slide_part = slide_by_position[position]
                source_slide_rels = rel_root(parts, source_slide_part)
                slide_serial[0] += 1
                slide_part = f"ppt/slides/slide{slide_serial[0]}.xml"
                output[slide_part] = parts[source_slide_part]
                target_rels = etree.Element(f"{{{REL}}}Relationships", nsmap={None: REL})
                source_note_part = None
                for rel in source_slide_rels.findall("rel:Relationship", NS):
                    copied = etree.fromstring(etree.tostring(rel))
                    rel_type = rel.get("Type")
                    old_target = resolve_target(source_slide_part, rel.get("Target"))
                    if rel_type == LAYOUT_REL:
                        layout_part = copy_layout(parts, output, old_target, layout_cache, deck_index,
                                                  layout_serial, image_cache, image_serial,
                                                  master_cache, master_serial, master_id_serial,
                                                  base_masters_by_hash, base_theme, pres_root,
                                                  pres_rels, rel_serial)
                        copied.set("Target", relative_target(slide_part, layout_part))
                    elif rel_type == IMAGE_REL:
                        image_part = image_copy(parts, output, old_target, image_cache, deck_index, image_serial)
                        copied.set("Target", relative_target(slide_part, image_part))
                    elif rel_type == NOTES_REL:
                        source_note_part = old_target
                        note_part = copy_notes(parts, output, source_note_part, slide_part, notes_cache,
                                               notes_serial, image_cache, image_serial, deck_index,
                                               base_notes_master)
                        copied.set("Target", relative_target(slide_part, note_part))
                    else:
                        raise ValueError(f"unsupported slide relationship {rel_type} in {source_slide_part}")
                    target_rels.append(copied)
                output[rels_path(slide_part)] = xml_bytes(target_rels)
                ct_root = etree.fromstring(output["[Content_Types].xml"])
                add_override(ct_root, slide_part, SLIDE_CT)
                output["[Content_Types].xml"] = xml_bytes(ct_root)
                rel_serial[0] += 1
                rel_id = f"rId{rel_serial[0]}"
                add_presentation_rel(pres_rels, rel_id, relative_target("ppt/presentation.xml", slide_part))
                sldid_serial[0] += 1
                new_node = etree.Element(f"{{{P}}}sldId", id=str(sldid_serial[0]))
                new_node.set(f"{{{R}}}id", rel_id)
                append_slide("", new_node)
                source_note = source_note_part is not None

            effect_markers = row.get("effect_markers", "")
            markers, grouping = item["build_hints"].get(int(row["reference_pdf_page"]), (effect_markers, ""))
            map_records.append({
                "output_slide": str(len(map_records) + 1),
                "row_type": "source_pdf_page_candidate",
                "source_filename": source_filename,
                "topic": topic,
                "source_pdf_page": row["reference_pdf_page"],
                "converted_pptx_slide": str(position),
                "speaker_notes_in_source": "yes" if source_note else "no",
                "keynote_effect_markers": markers,
                "keynote_grouping_hints": grouping,
                "build_status": "not expanded; inspect Keynote build audit",
                "review_status": "provisional text alignment only; repair and Google review pending",
            })

    for child in preserved_non_slide_children:
        sld_id_lst.append(child)
    output["ppt/presentation.xml"] = xml_bytes(pres_root)
    output["ppt/_rels/presentation.xml.rels"] = xml_bytes(pres_rels)

    app_path = "docProps/app.xml"
    if app_path in output:
        app = etree.fromstring(output[app_path])
        slide_count = app.find("{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}Slides")
        if slide_count is not None:
            slide_count.text = str(final_slide_count)
        output[app_path] = xml_bytes(app)

    if len(map_records) != final_slide_count:
        raise ValueError(f"map has {len(map_records)} rows but expected {final_slide_count}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", ZIP_DEFLATED) as archive:
        for name, data in output.items():
            archive.writestr(name, data)
    with ZipFile(args.output) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"output PPTX has corrupt ZIP member {bad}")
        check_root = etree.fromstring(archive.read("ppt/presentation.xml"))
        count = len(check_root.findall("p:sldIdLst/p:sldId", NS))
        if count != final_slide_count:
            raise ValueError(f"output presentation has {count} slides; expected {final_slide_count}")

    args.map_output.parent.mkdir(parents=True, exist_ok=True)
    with args.map_output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=[
                "output_slide", "row_type", "source_filename", "topic",
                "source_pdf_page", "converted_pptx_slide", "speaker_notes_in_source",
                "keynote_effect_markers", "keynote_grouping_hints", "build_status", "review_status",
            ],
        )
        writer.writeheader()
        writer.writerows(map_records)
    print(f"Built {args.output} with {final_slide_count} ordered candidate slides.")
    print(f"Output map: {args.map_output}")
    print("Candidate only: animation expansion and visual repair are still pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
