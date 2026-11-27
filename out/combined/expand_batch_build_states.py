#!/usr/bin/env python3
"""Expand selected PPTX slides into cumulative static build states.

The input is an assembled batch candidate and its output map. The JSON
expansion manifest identifies an existing output slide and supplies ordered
state operations. Each operation starts from the original slide, then keeps
the requested paragraph prefixes and/or removes the requested shape IDs.
Duplicated slides retain their layout, media relationships, and speaker notes.

This supports paragraph reveals and object-visibility states without adding a
dependency beyond the XML package already used by build_batch_candidate.py.
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
SLIDE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
NOTES_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
SLIDE_CT = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
NOTES_CT = "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"
NS = {"p": P, "a": A, "r": R, "rel": REL, "ct": CT}


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

    for shape_id in operations.get("hidden_shape_ids", []):
        node = shape_node(root, str(shape_id))
        parent = node.getparent()
        if parent is None:
            raise ValueError(f"shape {shape_id} has no parent")
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
            new_rows.append({**row, "output_slide": str(len(new_rows) + 1)})
            new_nodes.append(old_node)
            continue

        source_slide_xml = parts[old_part]
        source_rels_part = rels_path(old_part)
        if source_rels_part not in parts:
            raise ValueError(f"missing relationships for source slide {old_part}")
        source_slide_rels = parts[source_rels_part]
        states = expansion["states"]
        for state_index, state in enumerate(states, start=1):
            transformed = apply_operations(source_slide_xml, state.get("operations", {}))
            if state_index == 1:
                state_part = old_part
                parts[state_part] = transformed
                state_node = old_node
            else:
                slide_serial[0] += 1
                state_part = f"ppt/slides/slide{slide_serial[0]}.xml"
                parts[state_part] = transformed
                clone_slide_relationships(parts, old_part, state_part, notes_serial)
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
    print(f"PPTX: {args.output}")
    print(f"Map: {args.map_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
