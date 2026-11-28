"""Ensure every PPTX slide has editable 9 pt speaker notes.

Existing note text is preserved and explicitly styled. Slides without notes
receive a notes page with a single whitespace run so the 9 pt setting has a
real text run to survive Google Slides import. Notes are verified by package
and native text-style readback, not visual inspection.
"""

from __future__ import annotations

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
SLIDE_REL = f"{R}/slide"
NOTES_REL = f"{R}/notesSlide"
NOTES_MASTER_REL = f"{R}/notesMaster"
NOTES_CT = "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"
NS = {"p": P, "a": A, "r": R, "rel": REL, "ct": CT}
NOTES_PART_RE = re.compile(r"ppt/notesSlides/notesSlide(\d+)\.xml$")


def _xml_bytes(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _rels_path(part: str) -> str:
    folder, name = posixpath.split(part)
    return posixpath.join(folder, "_rels", f"{name}.rels")


def _resolve_target(source_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(source_part), target))


def _relative_target(source_part: str, target_part: str) -> str:
    return posixpath.relpath(target_part, posixpath.dirname(source_part))


def _relationships(parts: dict[str, bytes], part: str) -> etree._Element:
    path = _rels_path(part)
    if path not in parts:
        parts[path] = _xml_bytes(etree.Element(f"{{{REL}}}Relationships", nsmap={None: REL}))
    return etree.fromstring(parts[path])


def _add_notes_override(parts: dict[str, bytes], part: str) -> None:
    root = etree.fromstring(parts["[Content_Types].xml"])
    part_name = f"/{part}"
    existing = root.xpath("./ct:Override[@PartName=$name]", namespaces=NS, name=part_name)
    if not existing:
        etree.SubElement(root, f"{{{CT}}}Override", PartName=part_name, ContentType=NOTES_CT)
    parts["[Content_Types].xml"] = _xml_bytes(root)


def _body_shapes(notes_root: etree._Element) -> list[etree._Element]:
    return [
        shape for shape in notes_root.findall(".//p:sp", NS)
        if any(ph.get("type") == "body" for ph in shape.findall(".//p:ph", NS))
    ]


def _blank_paragraph(size: int) -> etree._Element:
    paragraph = etree.Element(f"{{{A}}}p")
    run = etree.SubElement(paragraph, f"{{{A}}}r")
    etree.SubElement(run, f"{{{A}}}rPr", lang="en-US", sz=str(size))
    text = etree.SubElement(run, f"{{{A}}}t")
    text.set(f"{{http://www.w3.org/XML/1998/namespace}}space", "preserve")
    text.text = " "
    etree.SubElement(paragraph, f"{{{A}}}endParaRPr", lang="en-US", sz=str(size))
    return paragraph


def _clear_body(notes_root: etree._Element, size: int) -> None:
    shapes = _body_shapes(notes_root)
    if not shapes:
        raise ValueError("notes slide has no speaker-notes body placeholder")
    for shape in shapes:
        text_body = shape.find("p:txBody", NS)
        if text_body is None:
            raise ValueError("speaker-notes body placeholder has no text body")
        for paragraph in list(text_body.findall("a:p", NS)):
            text_body.remove(paragraph)
        text_body.append(_blank_paragraph(size))


def _style_notes(notes_root: etree._Element, size: int) -> None:
    property_tags = {
        f"{{{A}}}rPr", f"{{{A}}}defRPr", f"{{{A}}}endParaRPr",
    }
    for node in notes_root.iter():
        if node.tag in property_tags:
            node.set("sz", str(size))

    for tag in ("r", "fld"):
        for run in notes_root.findall(f".//a:{tag}", NS):
            run_properties = run.find("a:rPr", NS)
            if run_properties is None:
                run_properties = etree.Element(f"{{{A}}}rPr", lang="en-US")
                run.insert(0, run_properties)
            run_properties.set("sz", str(size))

    shapes = _body_shapes(notes_root)
    if not shapes:
        raise ValueError("notes slide has no speaker-notes body placeholder")
    for shape in shapes:
        text_body = shape.find("p:txBody", NS)
        if text_body is None:
            raise ValueError("speaker-notes body placeholder has no text body")
        text = "".join(text_body.xpath(".//a:t/text()", namespaces=NS))
        if not text.strip():
            for paragraph in list(text_body.findall("a:p", NS)):
                text_body.remove(paragraph)
            text_body.append(_blank_paragraph(size))
        else:
            for paragraph in text_body.findall("a:p", NS):
                end_properties = paragraph.find("a:endParaRPr", NS)
                if end_properties is None:
                    end_properties = etree.SubElement(paragraph, f"{{{A}}}endParaRPr")
                end_properties.set("sz", str(size))


def _next_notes_part(parts: dict[str, bytes]) -> int:
    nums = [int(m.group(1)) for name in parts if (m := NOTES_PART_RE.fullmatch(name))]
    return max(nums, default=0) + 1


def ensure_speaker_notes(parts: dict[str, bytes], size: int = 900) -> int:
    """Mutate a PPTX package so every presentation slide has a 9 pt note run.

    Returns the number of new notes pages created.
    """
    presentation = etree.fromstring(parts["ppt/presentation.xml"])
    presentation_rels = etree.fromstring(parts["ppt/_rels/presentation.xml.rels"])
    relmap = {rel.get("Id"): rel for rel in presentation_rels.findall("rel:Relationship", NS)}
    slide_list = presentation.find("p:sldIdLst", NS)
    if slide_list is None:
        raise ValueError("presentation has no slide list")

    slide_parts: list[str] = []
    for index, slide_id in enumerate(slide_list.findall("p:sldId", NS), start=1):
        relation = relmap.get(slide_id.get(f"{{{R}}}id"))
        if relation is None or relation.get("Type") != SLIDE_REL:
            raise ValueError(f"slide {index} has no presentation relationship")
        slide_parts.append(_resolve_target("ppt/presentation.xml", relation.get("Target")))

    notes_master_relations = [
        relation for relation in presentation_rels.findall("rel:Relationship", NS)
        if relation.get("Type") == NOTES_MASTER_REL
    ]
    if len(notes_master_relations) != 1:
        raise ValueError(f"expected one notes master relationship, found {len(notes_master_relations)}")
    notes_master = _resolve_target("ppt/presentation.xml", notes_master_relations[0].get("Target"))

    template_part = None
    for name in sorted(parts):
        if not NOTES_PART_RE.fullmatch(name):
            continue
        candidate = etree.fromstring(parts[name])
        if _body_shapes(candidate):
            template_part = name
            break
    if template_part is None:
        raise ValueError("cannot create blank notes: no notes-slide body template exists")

    template_root = etree.fromstring(parts[template_part])
    template_rels = _relationships(parts, template_part)
    master_rel = next(
        (rel for rel in template_rels.findall("rel:Relationship", NS)
         if rel.get("Type") == NOTES_MASTER_REL),
        None,
    )
    if master_rel is None:
        raise ValueError(f"notes template {template_part} has no notes-master relationship")

    serial = _next_notes_part(parts)
    created = 0
    for slide_part in slide_parts:
        slide_rels = _relationships(parts, slide_part)
        note_relations = [
            relation for relation in slide_rels.findall("rel:Relationship", NS)
            if relation.get("Type") == NOTES_REL
        ]
        if len(note_relations) > 1:
            raise ValueError(f"slide {slide_part} has multiple notes relationships")

        if note_relations:
            note_part = _resolve_target(slide_part, note_relations[0].get("Target"))
            if note_part not in parts:
                raise ValueError(f"missing notes part {note_part}")
            notes_root = etree.fromstring(parts[note_part])
            _style_notes(notes_root, size)
            parts[note_part] = _xml_bytes(notes_root)
            continue

        note_part = f"ppt/notesSlides/notesSlide{serial}.xml"
        serial += 1
        notes_root = etree.fromstring(_xml_bytes(template_root))
        _clear_body(notes_root, size)
        _style_notes(notes_root, size)

        note_rels = etree.fromstring(_xml_bytes(template_rels))
        slide_backrefs = [
            relation for relation in note_rels.findall("rel:Relationship", NS)
            if relation.get("Type") == SLIDE_REL
        ]
        master_backrefs = [
            relation for relation in note_rels.findall("rel:Relationship", NS)
            if relation.get("Type") == NOTES_MASTER_REL
        ]
        if len(slide_backrefs) != 1 or len(master_backrefs) != 1:
            raise ValueError(f"notes template {template_part} has unexpected relationships")
        slide_backrefs[0].set("Target", _relative_target(note_part, slide_part))
        master_backrefs[0].set("Target", _relative_target(note_part, notes_master))
        parts[note_part] = _xml_bytes(notes_root)
        parts[_rels_path(note_part)] = _xml_bytes(note_rels)

        ids = [
            int(match.group(1)) for rel in slide_rels.findall("rel:Relationship", NS)
            if (match := re.fullmatch(r"rId(\d+)", rel.get("Id", "")))
        ]
        rel_id = f"rId{max(ids, default=0) + 1}"
        etree.SubElement(
            slide_rels, f"{{{REL}}}Relationship", Id=rel_id, Type=NOTES_REL,
            Target=_relative_target(slide_part, note_part),
        )
        parts[_rels_path(slide_part)] = _xml_bytes(slide_rels)
        _add_notes_override(parts, note_part)
        created += 1

    return created


def repair_pptx_file(path: str, output_path: str | None = None, size: int = 900) -> int:
    """Apply the project note rule to a PPTX file in place or to a new file."""
    with ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"input PPTX has corrupt ZIP member {bad}")
        parts = {item.filename: archive.read(item.filename) for item in archive.infolist()}
    created = ensure_speaker_notes(parts, size)
    destination = output_path or path
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            archive.writestr(name, data)
    with ZipFile(destination) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"output PPTX has corrupt ZIP member {bad}")
    return created

