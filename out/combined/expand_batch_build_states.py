#!/usr/bin/env python3
"""Expand selected PPTX slides into cumulative static build states.

The input is an assembled batch candidate and its output map. The JSON
expansion manifest identifies an existing output slide and supplies ordered
state operations. Each operation starts from the original slide, then keeps
requested paragraph or table-row prefixes and/or removes requested shape IDs.
A classified `non_expansions` entry annotates the existing map row with its
final static state and build chunk IDs without duplicating the slide.
Duplicated slides retain their layout, media relationships, and speaker notes;
speaker-note text is set to 9 pt for every slide. Slides without a source note
page receive a blank editable note page with a whitespace run to anchor 9 pt.

This supports paragraph, table-row, object-visibility, and progressive picture
region states. Pillow is already used by the tracked source-repair scripts.
It does not infer whether an effect is instructional; the source/build review
must decide which states belong in the manifest.

Example:
  python3 out/combined/expand_batch_build_states.py \
    --input out/.build/batch-01/assembled/batch-01-static-candidate.pptx \
    --map out/.build/batch-01/assembled/batch-01-candidate-map.csv \
    --manifest out/combined/final-batches/batch-01-build-expansion.json \
    --output out/.build/batch-01/assembled/batch-01-expanded-candidate.pptx \
    --map-output out/.build/batch-01/assembled/batch-01-expanded-map.csv
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import posixpath
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree
from PIL import Image, ImageDraw

from speaker_notes import ensure_speaker_notes


P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
SLIDE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
NOTES_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
SLIDE_CT = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
NOTES_CT = "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"
NS = {"p": P, "a": A, "r": R, "rel": REL, "ct": CT}
NOTES_PART_RE = re.compile(r"ppt/notesSlides/notesSlide\d+\.xml")


def xml_bytes(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def set_speaker_notes_font_size(notes_root: etree._Element) -> None:
    """Set every existing speaker-note text run and paragraph default to 9 pt."""
    property_tags = {
        f"{{{A}}}rPr",
        f"{{{A}}}defRPr",
        f"{{{A}}}endParaRPr",
    }
    for node in notes_root.iter():
        if node.tag in property_tags:
            node.set("sz", "900")
    # Add local run styling when the source relies on a larger notes-master default.
    for tag in ("r", "fld"):
        for run in notes_root.findall(f".//a:{tag}", NS):
            run_properties = run.find("a:rPr", NS)
            if run_properties is None:
                run_properties = etree.Element(f"{{{A}}}rPr")
                run.insert(0, run_properties)
            run_properties.set("sz", "900")


def rels_path(part: str) -> str:
    folder, name = posixpath.split(part)
    return posixpath.join(folder, "_rels", f"{name}.rels")


def resolve_target(source_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(source_part), target))


def relative_target(source_part: str, target_part: str) -> str:
    return posixpath.relpath(target_part, posixpath.dirname(source_part))


def presentation_slides(parts: dict[str, bytes]):
    root = etree.fromstring(parts["ppt/presentation.xml"])
    rels = etree.fromstring(parts["ppt/_rels/presentation.xml.rels"])
    relmap = {r.get("Id"): r for r in rels.findall("rel:Relationship", NS)}
    slide_list = root.find("p:sldIdLst", NS)
    if slide_list is None:
        raise ValueError("presentation has no p:sldIdLst")
    slides = []
    for position, node in enumerate(slide_list.findall("p:sldId", NS), start=1):
        rel = relmap.get(node.get(f"{{{R}}}id"))
        if rel is None or rel.get("Type") != SLIDE_REL:
            raise ValueError(f"slide {position}: missing presentation relationship")
        target = rel.get("Target")
        part = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("ppt", target))
        slides.append((position, node, part))
    return root, rels, slide_list, slides


def next_part_number(parts: dict[str, bytes], pattern: str) -> int:
    found = [int(m.group(1)) for name in parts if (m := re.fullmatch(pattern, name))]
    return max(found, default=0) + 1


def add_override(parts: dict[str, bytes], part: str, content_type: str) -> None:
    root = etree.fromstring(parts["[Content_Types].xml"])
    name = "/" + part
    for node in root.findall("ct:Override", NS):
        if node.get("PartName") == name:
            node.set("ContentType", content_type)
            parts["[Content_Types].xml"] = xml_bytes(root)
            return
    etree.SubElement(root, f"{{{CT}}}Override", PartName=name, ContentType=content_type)
    parts["[Content_Types].xml"] = xml_bytes(root)


def shape_node(root: etree._Element, shape_id: str) -> etree._Element:
    matches = root.xpath(".//p:cNvPr[@id=$sid]", namespaces=NS, sid=str(shape_id))
    if len(matches) != 1:
        raise ValueError(f"expected one shape ID {shape_id}, found {len(matches)}")
    node = matches[0]
    while node.getparent() is not None and node.getparent().tag != f"{{{P}}}spTree":
        node = node.getparent()
    return node


def drawing_object_node(root: etree._Element, object_id: str) -> etree._Element:
    """Return the exact drawing object, including a child inside a group."""
    matches = root.xpath(".//p:cNvPr[@id=$sid]", namespaces=NS, sid=str(object_id))
    if len(matches) != 1:
        raise ValueError(f"expected one drawing-object ID {object_id}, found {len(matches)}")
    node = matches[0]
    object_tags = {
        f"{{{P}}}sp", f"{{{P}}}pic", f"{{{P}}}cxnSp",
        f"{{{P}}}grpSp", f"{{{P}}}graphicFrame",
    }
    while node is not None and node.tag not in object_tags:
        node = node.getparent()
    if node is None:
        raise ValueError(f"drawing-object ID {object_id} has no object element")
    return node


def graphic_frame_node(root: etree._Element, object_id: str) -> etree._Element:
    matches = root.xpath(
        ".//p:graphicFrame[p:nvGraphicFramePr/p:cNvPr[@id=$fid]]",
        namespaces=NS,
        fid=str(object_id),
    )
    if len(matches) != 1:
        raise ValueError(f"expected one graphic-frame ID {object_id}, found {len(matches)}")
    return matches[0]


def apply_operations(slide_xml: bytes, operations: dict) -> bytes:
    root = etree.fromstring(slide_xml)
    for shape_id, keep_count in operations.get("visible_paragraphs", {}).items():
        node = shape_node(root, shape_id)
        text_body = node.find("p:txBody", NS)
        if text_body is None:
            raise ValueError(f"shape {shape_id} has no text body")
        paragraphs = text_body.findall("a:p", NS)
        content_paragraphs = [
            para for para in paragraphs
            if "".join(para.xpath(".//a:t/text()", namespaces=NS)).strip()
        ]
        if int(keep_count) < 0 or int(keep_count) > len(content_paragraphs):
            raise ValueError(
                f"shape {shape_id}: requested {keep_count} visible paragraphs, "
                f"found {len(content_paragraphs)}"
            )
        for para in content_paragraphs[int(keep_count):]:
            text_body.remove(para)

    for frame_id, keep_count in operations.get("visible_table_rows", {}).items():
        frame = graphic_frame_node(root, str(frame_id))
        table = frame.find(".//a:tbl", NS)
        if table is None:
            raise ValueError(f"graphic frame {frame_id} has no table")
        rows = table.findall("a:tr", NS)
        if int(keep_count) < 0 or int(keep_count) > len(rows):
            raise ValueError(
                f"table {frame_id}: requested {keep_count} visible rows, found {len(rows)}"
            )
        retained_rows = rows[:int(keep_count)]
        for row in rows[int(keep_count):]:
            table.remove(row)
        transform = frame.find("p:xfrm", NS)
        extent = transform.find("a:ext", NS) if transform is not None else None
        if extent is not None:
            extent.set("cy", str(sum(int(row.get("h", "0")) for row in retained_rows)))

    for shape_id in operations.get("hidden_shape_ids", []):
        node = shape_node(root, str(shape_id))
        parent = node.getparent()
        if parent is None:
            raise ValueError(f"shape {shape_id} has no parent")
        parent.remove(node)

    for object_id in operations.get("hidden_drawing_object_ids", []):
        node = drawing_object_node(root, str(object_id))
        parent = node.getparent()
        if parent is None:
            raise ValueError(f"drawing object {object_id} has no parent")
        parent.remove(node)
    return xml_bytes(root)


def clone_slide_relationships(parts: dict[str, bytes], source_slide: str,
                              new_slide: str, notes_serial: list[int]) -> None:
    source_rels_path = rels_path(source_slide)
    if source_rels_path not in parts:
        raise ValueError(f"missing slide relationships: {source_rels_path}")
    rels = etree.fromstring(parts[source_rels_path])
    note_relations = [r for r in rels.findall("rel:Relationship", NS) if r.get("Type") == NOTES_REL]
    if len(note_relations) > 1:
        raise ValueError(f"{source_slide} has multiple notes relationships")
    if note_relations:
        note_rel = note_relations[0]
        source_note = resolve_target(source_slide, note_rel.get("Target"))
        source_note_rels_path = rels_path(source_note)
        if source_note not in parts or source_note_rels_path not in parts:
            raise ValueError(f"missing notes part or relationships for {source_slide}")
        notes_serial[0] += 1
        new_note = f"ppt/notesSlides/notesSlide{notes_serial[0]}.xml"
        parts[new_note] = parts[source_note]
        note_rels = etree.fromstring(parts[source_note_rels_path])
        slide_backrefs = [r for r in note_rels.findall("rel:Relationship", NS) if r.get("Type") == SLIDE_REL]
        if len(slide_backrefs) != 1:
            raise ValueError(f"{source_note} has no unique source-slide relationship")
        slide_backrefs[0].set("Target", relative_target(new_note, new_slide))
        parts[rels_path(new_note)] = xml_bytes(note_rels)
        note_rel.set("Target", relative_target(new_slide, new_note))
        add_override(parts, new_note, NOTES_CT)
    parts[rels_path(new_slide)] = xml_bytes(rels)


def apply_picture_region_masks(
    parts: dict[str, bytes], slide_part: str, slide_xml: bytes,
    operations: dict,
) -> None:
    """Clone a picture asset and mask future build-object bounds in it.

    Some previously repaired diagrams are a single source-PDF crop. This
    supports progressive static states without restoring the corrupted
    converted diagram underneath the crop. Bounds are supplied in slide
    points from the Keynote build-object records.
    """
    specs = operations.get("picture_region_masks", [])
    if not specs:
        return
    root = etree.fromstring(slide_xml)
    rels_part = rels_path(slide_part)
    if rels_part not in parts:
        raise ValueError(f"missing relationships for masked-picture slide {slide_part}")
    rels = etree.fromstring(parts[rels_part])
    for spec in specs:
        picture_id = str(spec["picture_shape_id"])
        matches = root.xpath(
            ".//p:pic[p:nvPicPr/p:cNvPr[@id=$sid]]",
            namespaces=NS,
            sid=picture_id,
        )
        if len(matches) != 1:
            raise ValueError(
                f"expected one picture shape {picture_id} on {slide_part}, found {len(matches)}"
            )
        picture = matches[0]
        blip = picture.find(".//a:blip", NS)
        xfrm = picture.find("./p:spPr/a:xfrm", NS)
        off = xfrm.find("./a:off", NS) if xfrm is not None else None
        ext = xfrm.find("./a:ext", NS) if xfrm is not None else None
        if blip is None or off is None or ext is None:
            raise ValueError(f"picture shape {picture_id} has incomplete image geometry")
        embed_id = blip.get(f"{{{R}}}embed")
        image_rel = rels.find(f'rel:Relationship[@Id="{embed_id}"]', NS)
        if image_rel is None or not image_rel.get("Type", "").endswith("/image"):
            raise ValueError(f"picture shape {picture_id} has no image relationship")
        source_media = resolve_target(slide_part, image_rel.get("Target"))
        if source_media not in parts:
            raise ValueError(f"missing picture asset {source_media}")
        with Image.open(io.BytesIO(parts[source_media])) as source:
            image = source.convert("RGBA")
            draw = ImageDraw.Draw(image)
            image_x = int(off.get("x")) / 12700
            image_y = int(off.get("y")) / 12700
            image_w = int(ext.get("cx")) / 12700
            image_h = int(ext.get("cy")) / 12700
            if image_w <= 0 or image_h <= 0:
                raise ValueError(f"picture shape {picture_id} has non-positive dimensions")
            padding = float(spec.get("padding_pt", 1.5))
            for bounds in spec.get("bounds_pt", []):
                x, y, w, h = (float(value) for value in bounds)
                if spec.get("zero_extent_as_square"):
                    if w == 0 and h > 0:
                        x -= h / 2
                        w = h
                    elif h == 0 and w > 0:
                        y -= w / 2
                        h = w
                    elif w == 0 and h == 0:
                        side = float(spec.get("zero_extent_min_side_pt", 8))
                        x -= side / 2
                        y -= side / 2
                        w = h = side
                left = math.floor((x - padding - image_x) * image.width / image_w)
                top = math.floor((y - padding - image_y) * image.height / image_h)
                right = math.ceil((x + max(w, 0) + padding - image_x) * image.width / image_w)
                bottom = math.ceil((y + max(h, 0) + padding - image_y) * image.height / image_h)
                left = max(0, min(image.width, left))
                top = max(0, min(image.height, top))
                right = max(0, min(image.width, right))
                bottom = max(0, min(image.height, bottom))
                if right > left and bottom > top:
                    draw.rectangle((left, top, right - 1, bottom - 1), fill=(255, 255, 255, 255))
            output = io.BytesIO()
            image_format = source.format or "PNG"
            if image_format.upper() in {"JPEG", "JPG"}:
                image.convert("RGB").save(output, format="JPEG", quality=95)
            else:
                image.save(output, format=image_format)

        extension = Path(source_media).suffix
        prefix = "ppt/media/cs408-build-mask-"
        serial = 1 + sum(name.startswith(prefix) for name in parts)
        new_media = f"{prefix}{serial:04d}{extension}"
        parts[new_media] = output.getvalue()
        image_rel.set("Target", relative_target(slide_part, new_media))
    parts[rels_part] = xml_bytes(rels)


def load_map(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not reader.fieldnames:
            raise ValueError(f"map has no header: {path}")
        return rows, list(reader.fieldnames)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--map-output", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    expansions = manifest.get("expansions", [])
    non_expansions = manifest.get("non_expansions", [])
    with ZipFile(args.input) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"input PPTX has a corrupt member: {bad}")
        parts = {item.filename: archive.read(item.filename) for item in archive.infolist()}
    map_rows, map_columns = load_map(args.map)
    slides_root, presentation_rels, slide_list, slides = presentation_slides(parts)
    if len(map_rows) != len(slides):
        raise ValueError(f"map has {len(map_rows)} rows for {len(slides)} slides")
    if [int(row["output_slide"]) for row in map_rows] != list(range(1, len(slides) + 1)):
        raise ValueError("map output_slide values must match presentation order")

    expansions_by_position: dict[int, dict] = {}
    for expansion in expansions:
        position = int(expansion["output_slide"])
        if position < 1 or position > len(slides):
            raise ValueError(f"expansion output slide {position} is outside the presentation")
        if position in expansions_by_position:
            raise ValueError(f"more than one expansion targets output slide {position}")
        states = expansion.get("states")
        if not states:
            raise ValueError(f"output slide {position} has no states")
        expansions_by_position[position] = expansion

    non_expansions_by_position: dict[int, dict] = {}
    for decision in non_expansions:
        source_filename = decision.get("source_filename", "")
        reference_pdf_page = str(decision.get("reference_pdf_page", ""))
        matching_positions = [
            index for index, row in enumerate(map_rows, start=1)
            if row.get("source_filename") == source_filename
            and row.get("source_pdf_page") == reference_pdf_page
        ]
        if len(matching_positions) != 1:
            raise ValueError(
                "classified build source must match exactly one map row by "
                f"filename and PDF page: {source_filename} page {reference_pdf_page}; "
                f"found {len(matching_positions)}"
            )
        position = matching_positions[0]
        if position in expansions_by_position:
            raise ValueError(f"slide {position} is both expanded and classified without expansion")
        if position in non_expansions_by_position:
            raise ValueError(f"more than one non-expansion decision targets slide {position}")
        row = map_rows[position - 1]
        if row.get("converted_pptx_slide") != str(decision.get("converted_pptx_slide")):
            raise ValueError(
                f"non-expansion converted-slide mismatch at map output slide {position}: "
                f"map has {row.get('converted_pptx_slide')!r}, manifest has "
                f"{decision.get('converted_pptx_slide')!r}"
            )
        non_expansions_by_position[position] = decision

    slide_serial = [next_part_number(parts, r"ppt/slides/slide(\d+)\.xml") - 1]
    notes_serial = [next_part_number(parts, r"ppt/notesSlides/notesSlide(\d+)\.xml") - 1]
    sldid_serial = [max((int(node.get("id")) for node in slides_root.findall(".//p:sldId", NS)
                         if (node.get("id") or "").isdigit()), default=255)]
    rel_serial = [max((int(m.group(1)) for rel in presentation_rels.findall("rel:Relationship", NS)
                       if (m := re.fullmatch(r"rId(\d+)", rel.get("Id", "")))), default=0)]

    new_rows: list[dict[str, str]] = []
    new_nodes: list[etree._Element] = []
    for position, old_node, old_part in slides:
        row = map_rows[position - 1]
        expansion = expansions_by_position.get(position)
        if expansion is None:
            output_row = {**row, "output_slide": str(len(new_rows) + 1)}
            decision = non_expansions_by_position.get(position)
            if decision is not None:
                output_row["build_status"] = decision.get(
                    "build_status", "classified single-step build; no additional static state"
                )
                output_row["review_status"] = decision.get(
                    "review_status", "build classification recorded; full-batch visual review pending"
                )
                output_row["source_keynote_slide_order"] = str(
                    decision.get("source_keynote_slide_order", "")
                )
                output_row["source_build_state"] = decision.get(
                    "source_build_state", "single final static state"
                )
                output_row["source_build_chunk_ids"] = ";".join(
                    str(x) for x in decision.get("build_chunk_ids", [])
                )
            new_rows.append(output_row)
            new_nodes.append(old_node)
            continue

        source_slide_xml = parts[old_part]
        source_rels_part = rels_path(old_part)
        if source_rels_part not in parts:
            raise ValueError(f"missing relationships for source slide {old_part}")
        source_slide_rels = parts[source_rels_part]
        states = expansion["states"]
        for state_index, state in enumerate(states, start=1):
            operations = state.get("operations", {})
            transformed = apply_operations(source_slide_xml, operations)
            if state_index == 1:
                state_part = old_part
                state_node = old_node
            else:
                slide_serial[0] += 1
                state_part = f"ppt/slides/slide{slide_serial[0]}.xml"
                current_source_rels = parts[source_rels_part]
                parts[source_rels_part] = source_slide_rels
                clone_slide_relationships(parts, old_part, state_part, notes_serial)
                parts[source_rels_part] = current_source_rels
                add_override(parts, state_part, SLIDE_CT)
                rel_serial[0] += 1
                rel_id = f"rId{rel_serial[0]}"
                etree.SubElement(
                    presentation_rels, f"{{{REL}}}Relationship",
                    Id=rel_id, Type=SLIDE_REL,
                    Target=relative_target("ppt/presentation.xml", state_part),
                )
                sldid_serial[0] += 1
                state_node = etree.Element(f"{{{P}}}sldId", id=str(sldid_serial[0]))
                state_node.set(f"{{{R}}}id", rel_id)
            apply_picture_region_masks(parts, state_part, transformed, operations)
            parts[state_part] = transformed
            new_nodes.append(state_node)
            record = {**row, "output_slide": str(len(new_rows) + 1)}
            record["row_type"] = "source_build_state"
            record["build_status"] = state.get(
                "build_status",
                expansion.get("build_status", f"cumulative static state {state_index}/{len(states)}"),
            )
            record["review_status"] = state.get(
                "review_status",
                expansion.get("review_status", "generated static state; visual review pending"),
            )
            record["source_keynote_slide_order"] = str(expansion.get("source_keynote_slide_order", ""))
            record["source_build_state"] = state.get("label", f"{state_index}/{len(states)}")
            record["source_build_chunk_ids"] = ";".join(str(x) for x in state.get("build_chunk_ids", []))
            new_rows.append(record)

    for child in list(slide_list):
        if child.tag == f"{{{P}}}sldId":
            slide_list.remove(child)
    for node in new_nodes:
        slide_list.append(node)
    parts["ppt/presentation.xml"] = xml_bytes(slides_root)
    parts["ppt/_rels/presentation.xml.rels"] = xml_bytes(presentation_rels)

    app_path = "docProps/app.xml"
    if app_path in parts:
        app = etree.fromstring(parts[app_path])
        slides_count = app.find("{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}Slides")
        if slides_count is not None:
            slides_count.text = str(len(new_rows))
        parts[app_path] = xml_bytes(app)

    # Apply the project-wide speaker-note type size to original and cloned notes.
    for part_name in list(parts):
        if NOTES_PART_RE.fullmatch(part_name):
            note_root = etree.fromstring(parts[part_name])
            set_speaker_notes_font_size(note_root)
            parts[part_name] = xml_bytes(note_root)

    blank_notes_added = ensure_speaker_notes(parts, size=900)

    extra_columns = ["source_keynote_slide_order", "source_build_state", "source_build_chunk_ids"]
    output_columns = map_columns + [c for c in extra_columns if c not in map_columns]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            archive.writestr(name, data)
    with ZipFile(args.output) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"output PPTX has corrupt member {bad}")
        root = etree.fromstring(archive.read("ppt/presentation.xml"))
        actual = len(root.findall("p:sldIdLst/p:sldId", NS))
        if actual != len(new_rows):
            raise ValueError(f"output has {actual} slides but map has {len(new_rows)} rows")

    args.map_output.parent.mkdir(parents=True, exist_ok=True)
    with args.map_output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(new_rows)
    print(f"Expanded {len(expansions)} source slide(s) to {len(new_rows)} ordered static slides.")
    print(f"Ensured 9 pt speaker notes on every slide; added {blank_notes_added} blank notes page(s).")
    print(f"PPTX: {args.output}")
    print(f"Map: {args.map_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
