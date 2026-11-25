#!/usr/bin/env python3
"""Build a Fall Project 1 pilot, expanding paragraph builds to static slides.

The input is the Fall Lab 1 source PPTX. Three slides use paragraph timing to
reveal one item at a time; this script expands those states as ordinary slides.
It also maps a consecutive AFL screenshot zoom pair (source slides 35–36),
which has no timing metadata but shares text and adds a full-slide image. The
script preserves note-slide packages and updates stale title/administrative
text from Fall course sources. It uses only the Python standard library and
writes a one-row-per-output-slide source/build map.
"""

from __future__ import annotations

import csv
import posixpath
import re
import sys
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[3]
PILOT_DIR = Path(__file__).resolve().parent
SOURCE = ROOT / "labs/lab1/slides/intro.pptx"
OUTPUT = PILOT_DIR / "cs408-fall-project-1-pilot-round13.pptx"
MAP = PILOT_DIR / "cs408-fall-project-1-pilot-round13-map.csv"

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
}
for prefix, uri in NS.items():
    if prefix != "rel" and prefix != "ct":
        ET.register_namespace(prefix, uri)
ET.register_namespace("", NS["rel"])
ET.register_namespace("", NS["ct"])

SLIDE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
NOTES_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
SLIDE_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
NOTES_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"


def xml_bytes(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def parse(data: bytes) -> ET.Element:
    return ET.fromstring(data)


def part_for_target(target: str) -> str:
    # Slide relationship targets are relative to ppt/slides/, e.g.
    # ../notesSlides/notesSlide6.xml. Normalize before looking them up.
    return posixpath.normpath(posixpath.join("ppt/slides", target.replace("\\", "/")))


def slide_number_from_target(target: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", target)
    if not match:
        raise ValueError(f"Unexpected slide target: {target}")
    return int(match.group(1))


def note_target_from_relationships(data: bytes) -> str | None:
    rels = parse(data)
    for rel in rels.findall("rel:Relationship", NS):
        if rel.get("Type") == NOTES_REL:
            return rel.get("Target")
    return None


def find_animated_body(root: ET.Element) -> tuple[str, int] | None:
    timing = root.find("p:timing", NS)
    if timing is None:
        return None
    max_paragraph: dict[str, int] = {}
    for target in timing.findall(".//p:spTgt", NS):
        shape_id = target.get("spid")
        p_range = target.find("p:txEl/p:pRg", NS)
        if not shape_id or p_range is None:
            continue
        end = int(p_range.get("end", "0"))
        max_paragraph[shape_id] = max(max_paragraph.get(shape_id, -1), end)
    matches = []
    for shape in root.findall(".//p:sp", NS):
        props = shape.find("p:nvSpPr/p:cNvPr", NS)
        body = shape.find("p:txBody", NS)
        if props is None or body is None:
            continue
        shape_id = props.get("id")
        if shape_id not in max_paragraph:
            continue
        paragraph_count = len(body.findall("a:p", NS))
        if paragraph_count == max_paragraph[shape_id] + 1:
            matches.append((shape_id, paragraph_count))
    if len(matches) != 1:
        raise ValueError(f"Expected one animated paragraph body; found {matches}")
    return matches[0]


def expand_slide(source_xml: bytes, keep_paragraphs: int | None) -> bytes:
    root = parse(source_xml)
    if keep_paragraphs is not None:
        target = find_animated_body(root)
        if target is None:
            raise ValueError("Requested build state for a slide without timing")
        shape_id, total = target
        if not 1 <= keep_paragraphs <= total:
            raise ValueError(f"Invalid build count {keep_paragraphs}/{total}")
        for shape in root.findall(".//p:sp", NS):
            props = shape.find("p:nvSpPr/p:cNvPr", NS)
            if props is None or props.get("id") != shape_id:
                continue
            body = shape.find("p:txBody", NS)
            paragraphs = body.findall("a:p", NS)
            for paragraph in paragraphs[keep_paragraphs:]:
                body.remove(paragraph)
            break
    timing = root.find("p:timing", NS)
    if timing is not None:
        root.remove(timing)
    return xml_bytes(root)


def apply_fall_updates(xml: bytes, source_slide: int) -> bytes:
    root = parse(xml)
    texts = root.findall(".//a:t", NS)
    if source_slide == 1:
        matches = [t for t in texts if t.text == "CS 408 Lab2 Tutorial"]
        if len(matches) != 1:
            raise ValueError("Could not uniquely locate outdated title on slide 1")
        matches[0].text = "CS 408 Project 1: Fuzzing"
    elif source_slide == 2:
        replacements = {
            "Deadline: Apr. 12": "Deadline: October 30, 2026",
            "Handout is released on Ed": "See the Fall 2026 Project 1 handout",
            "Skeleton code will be released by the end of today":
                "Get your project repository through Classroom 50",
            "Group information can be found on Brightspace":
                "Group formation is announced on Ed Discussion",
        }
        for old, new in replacements.items():
            matches = [t for t in texts if t.text == old]
            if len(matches) != 1:
                raise ValueError(f"Could not uniquely locate slide 2 text: {old!r}")
            matches[0].text = new
    return xml_bytes(root)


def update_slide_relationships(data: bytes, output_slide: int) -> bytes:
    root = parse(data)
    for rel in root.findall("rel:Relationship", NS):
        if rel.get("Type") == NOTES_REL:
            rel.set("Target", f"../notesSlides/notesSlide{output_slide}.xml")
    return xml_bytes(root)


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Source missing: {SOURCE}")
    with zipfile.ZipFile(SOURCE) as zin:
        source_parts = {name: zin.read(name) for name in zin.namelist()}

    presentation = parse(source_parts["ppt/presentation.xml"])
    presentation_rels = parse(source_parts["ppt/_rels/presentation.xml.rels"])
    relation_by_id = {
        rel.get("Id"): rel.get("Target")
        for rel in presentation_rels.findall("rel:Relationship", NS)
    }
    slide_ids = presentation.find("p:sldIdLst", NS)
    ordered_sources = []
    for sld_id in list(slide_ids):
        rel_id = sld_id.get(f"{{{NS['r']}}}id")
        target = relation_by_id[rel_id]
        ordered_sources.append(slide_number_from_target(target))
    if len(ordered_sources) != 40:
        raise ValueError(f"Expected 40 Fall Lab 1 source slides, got {len(ordered_sources)}")

    expansion_counts = {}
    for source_slide in ordered_sources:
        xml = source_parts[f"ppt/slides/slide{source_slide}.xml"]
        root = parse(xml)
        if root.find("p:timing", NS) is not None:
            body = find_animated_body(root)
            expansion_counts[source_slide] = body[1]
    if expansion_counts != {6: 8, 7: 6, 8: 11}:
        raise ValueError(f"Animation audit changed; expected 6/7/8 paragraph builds, found {expansion_counts}")

    # Slides 35–36 are a separate, Keynote-style reveal represented as two
    # ordered source slides rather than PowerPoint timing. Slide 36 retains
    # the same text and adds a full-slide screenshot object over slide 35's
    # thumbnail, so record it as the second static state in that sequence.
    source_35 = parse(source_parts["ppt/slides/slide35.xml"])
    source_36 = parse(source_parts["ppt/slides/slide36.xml"])
    text_35 = "".join(t.text or "" for t in source_35.findall(".//a:t", NS))
    text_36 = "".join(t.text or "" for t in source_36.findall(".//a:t", NS))
    image_counts = (
        len(source_35.findall(".//p:pic", NS)),
        len(source_36.findall(".//p:pic", NS)),
    )
    if text_35 != text_36 or image_counts != (1, 2):
        raise ValueError(
            "AFL screenshot state audit changed: expected identical text and one then two pictures"
        )

    output_map = []
    for source_slide in ordered_sources:
        count = expansion_counts.get(source_slide)
        if count:
            for state in range(1, count + 1):
                output_map.append((source_slide, state, count))
        else:
            output_map.append((source_slide, 0, 1))
    if len(output_map) != 62:
        raise ValueError(f"Expected 62 static output slides, got {len(output_map)}")

    # Prepare the new ordered slide list and relation IDs, preserving all other
    # presentation-level relationships such as masters and themes.
    max_rel = max(
        (int(m.group(1)) for rid in relation_by_id if (m := re.fullmatch(r"rId(\d+)", rid))),
        default=0,
    )
    existing_sld_ids = [int(e.get("id")) for e in list(slide_ids)]
    next_sld_id = max(existing_sld_ids, default=255) + 1
    for child in list(slide_ids):
        slide_ids.remove(child)

    relationship_output = []
    for output_slide, (source_slide, state, total) in enumerate(output_map, 1):
        rel_id = f"rId{max_rel + output_slide}"
        relationship_output.append((rel_id, output_slide))
        sld = ET.Element(f"{{{NS['p']}}}sldId", {
            "id": str(next_sld_id + output_slide - 1),
            f"{{{NS['r']}}}id": rel_id,
        })
        slide_ids.append(sld)

    # Remove the old slide relationships and append the final ordered set.
    for rel in list(presentation_rels.findall("rel:Relationship", NS)):
        if rel.get("Type") == SLIDE_REL:
            presentation_rels.remove(rel)
    for rel_id, output_slide in relationship_output:
        ET.SubElement(presentation_rels, f"{{{NS['rel']}}}Relationship", {
            "Id": rel_id,
            "Type": SLIDE_REL,
            "Target": f"slides/slide{output_slide}.xml",
        })

    content_types = parse(source_parts["[Content_Types].xml"])
    for item in list(content_types):
        name = item.get("PartName", "")
        if re.fullmatch(r"/ppt/slides/slide\d+\.xml", name) or re.fullmatch(
            r"/ppt/notesSlides/notesSlide\d+\.xml", name
        ):
            content_types.remove(item)
    for output_slide in range(1, len(output_map) + 1):
        ET.SubElement(content_types, f"{{{NS['ct']}}}Override", {
            "PartName": f"/ppt/slides/slide{output_slide}.xml",
            "ContentType": SLIDE_CONTENT_TYPE,
        })
        ET.SubElement(content_types, f"{{{NS['ct']}}}Override", {
            "PartName": f"/ppt/notesSlides/notesSlide{output_slide}.xml",
            "ContentType": NOTES_CONTENT_TYPE,
        })

    # Replace the source slide/note parts in final reading order. Each static
    # build state gets its own cloned note slide and slide relationship.
    generated = {
        "ppt/presentation.xml": xml_bytes(presentation),
        "ppt/_rels/presentation.xml.rels": xml_bytes(presentation_rels),
        "[Content_Types].xml": xml_bytes(content_types),
    }
    map_rows = []
    for output_slide, (source_slide, state, total) in enumerate(output_map, 1):
        slide_xml = source_parts[f"ppt/slides/slide{source_slide}.xml"]
        slide_xml = expand_slide(slide_xml, state if state else None)
        slide_xml = apply_fall_updates(slide_xml, source_slide)
        generated[f"ppt/slides/slide{output_slide}.xml"] = slide_xml

        rels_name = f"ppt/slides/_rels/slide{source_slide}.xml.rels"
        rels_data = source_parts[rels_name]
        note_target = note_target_from_relationships(rels_data)
        if note_target:
            note_source_part = part_for_target(note_target)
            generated[f"ppt/notesSlides/notesSlide{output_slide}.xml"] = source_parts[note_source_part]
            note_rels_source = f"ppt/notesSlides/_rels/{Path(note_source_part).name}.rels"
            generated[f"ppt/notesSlides/_rels/notesSlide{output_slide}.xml.rels"] = source_parts[note_rels_source]
            rels_data = update_slide_relationships(rels_data, output_slide)
            notes_status = "source note slide cloned unchanged"
        else:
            notes_status = "no source note slide"
        generated[f"ppt/slides/_rels/slide{output_slide}.xml.rels"] = rels_data

        change = ""
        if source_slide == 1:
            change = "Updated stale Lab 2 title to Fall Project 1/Fuzzing"
        elif source_slide == 2:
            change = (
                "Updated April deadline and obsolete repository/group channels from Fall sources; "
                "used handout due date Oct 30, while syllabus table says Project 1 due Nov 3"
            )
        if state:
            build_state = f"paragraph build {state}/{total}; cumulative visible paragraphs"
        elif source_slide == 35:
            build_state = (
                "sequential image-build state 1/2: AFL bullets with thumbnail; "
                "paired with source slide 36"
            )
        elif source_slide == 36:
            build_state = (
                "sequential image-build state 2/2: same AFL bullets plus "
                "full-slide screenshot overlay; inferred from source sequence, no p:timing"
            )
        else:
            build_state = "static source slide, unchanged build content"
        map_rows.append({
            "output_slide": output_slide,
            "source_file": "labs/lab1/slides/intro.pptx",
            "source_slide": source_slide,
            "build_state": build_state,
            "speaker_notes": notes_status,
            "content_update": change,
        })

    # Carry every unrelated package item forward exactly; replace only the
    # manifest/presentation/slide/note parts generated above.
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in source_parts.items():
            if name in generated:
                continue
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", name):
                continue
            if re.fullmatch(r"ppt/slides/_rels/slide\d+\.xml\.rels", name):
                continue
            if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name):
                continue
            if re.fullmatch(r"ppt/notesSlides/_rels/notesSlide\d+\.xml\.rels", name):
                continue
            zout.writestr(name, data)
        for name, data in generated.items():
            zout.writestr(name, data)

    with MAP.open("w", newline="", encoding="utf-8") as f:
        fields = ["output_slide", "source_file", "source_slide", "build_state", "speaker_notes", "content_update"]
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(map_rows)
    print(f"Built {OUTPUT} with {len(output_map)} slides; expanded source builds {expansion_counts}; map: {MAP}")


if __name__ == "__main__":
    main()
