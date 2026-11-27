#!/usr/bin/env python3
"""Keep selected PPTX slides and prune parts no longer reachable from them.

Slide positions are 1-based positions in the input presentation. Ranges may be
combined, for example ``--keep 17-23`` or ``--keep 1-4,17-23``. Slide order in
the output follows the order supplied to ``--keep``. The package-level method
preserves editable slide XML, layouts, masters, images, notes, and other related
parts while removing unrelated slides and media from pilot decks.
"""

from __future__ import annotations

import argparse
import posixpath
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
APP = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
NS = {"p": P, "r": R, "rel": REL}


def xml_bytes(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def rels_part(source_part: str) -> str:
    if not source_part:
        return "_rels/.rels"
    folder, name = posixpath.split(source_part)
    return posixpath.join(folder, "_rels", f"{name}.rels")


def resolve_target(source_part: str, target: str) -> str:
    target = target.split("#", 1)[0].split("?", 1)[0]
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    return posixpath.normpath(posixpath.join(posixpath.dirname(source_part), target))


def parse_positions(value: str) -> list[int]:
    positions: list[int] = []
    for token in value.split(","):
        token = token.strip()
        match = re.fullmatch(r"(\d+)(?:-(\d+))?", token)
        if not match:
            raise argparse.ArgumentTypeError(f"invalid slide range: {token!r}")
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if start < 1 or end < start:
            raise argparse.ArgumentTypeError(f"invalid slide range: {token!r}")
        positions.extend(range(start, end + 1))
    if not positions or len(set(positions)) != len(positions):
        raise argparse.ArgumentTypeError("slide positions must be nonempty and unique")
    return positions


def package_closure(parts: dict[str, bytes]) -> set[str]:
    """Return all internal relationship targets reachable from package root."""
    pending = [""]
    reached: set[str] = set()
    while pending:
        source = pending.pop()
        if source:
            reached.add(source)
        relationship_part = rels_part(source)
        if relationship_part not in parts:
            if source:
                continue
            raise ValueError("PPTX package is missing _rels/.rels")
        if relationship_part not in reached:
            reached.add(relationship_part)
        root = etree.fromstring(parts[relationship_part])
        for rel in root.findall("rel:Relationship", NS):
            if rel.get("TargetMode") == "External":
                continue
            target = resolve_target(source, rel.get("Target", ""))
            if target not in parts:
                raise ValueError(f"relationship from {source or '[package root]'} points to missing {target}")
            if target not in reached:
                pending.append(target)
    reached.add("[Content_Types].xml")
    return reached


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--keep", type=parse_positions, required=True,
                        help="1-based slide positions/ranges, e.g. 17-23 or 1-4,17-23")
    parser.add_argument("--keep-all-parts", action="store_true",
                        help="retain unused package members for compatibility diagnosis")
    args = parser.parse_args()

    with ZipFile(args.input) as source:
        bad = source.testzip()
        if bad:
            raise ValueError(f"input PPTX has a corrupt member: {bad}")
        parts = {entry.filename: source.read(entry.filename) for entry in source.infolist()}

    presentation = etree.fromstring(parts["ppt/presentation.xml"])
    presentation_rels = etree.fromstring(parts["ppt/_rels/presentation.xml.rels"])
    rel_by_id = {rel.get("Id"): rel for rel in presentation_rels.findall("rel:Relationship", NS)}
    slide_ids = presentation.find("p:sldIdLst", NS)
    if slide_ids is None:
        raise ValueError("PPTX presentation has no slide list")
    all_slides = slide_ids.findall("p:sldId", NS)
    wanted = set(args.keep)
    if max(wanted) > len(all_slides):
        raise ValueError(f"requested slide {max(wanted)} but input has {len(all_slides)} slides")

    kept_nodes = [node for index, node in enumerate(all_slides, start=1) if index in wanted]
    kept_rel_ids = {node.get(f"{{{R}}}id") for node in kept_nodes}
    for node in list(slide_ids):
        if node.tag == f"{{{P}}}sldId":
            slide_ids.remove(node)
    for node in kept_nodes:
        slide_ids.append(node)
    for rel in list(presentation_rels.findall("rel:Relationship", NS)):
        if rel.get("Type", "").endswith("/slide") and rel.get("Id") not in kept_rel_ids:
            presentation_rels.remove(rel)
    parts["ppt/presentation.xml"] = xml_bytes(presentation)
    parts["ppt/_rels/presentation.xml.rels"] = xml_bytes(presentation_rels)

    app_path = "docProps/app.xml"
    if app_path in parts:
        app = etree.fromstring(parts[app_path])
        slide_count = app.find(f"{{{APP}}}Slides")
        if slide_count is not None:
            slide_count.text = str(len(kept_nodes))
        parts[app_path] = xml_bytes(app)

    keep_parts = set(parts) if args.keep_all_parts else package_closure(parts)
    content_types = etree.fromstring(parts["[Content_Types].xml"])
    ct_ns = {"ct": "http://schemas.openxmlformats.org/package/2006/content-types"}
    for override in list(content_types.findall("ct:Override", ct_ns)):
        part_name = override.get("PartName", "").lstrip("/")
        if part_name not in keep_parts:
            content_types.remove(override)
    parts["[Content_Types].xml"] = xml_bytes(content_types)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", ZIP_DEFLATED) as target:
        for name, data in parts.items():
            if name in keep_parts:
                target.writestr(name, data)

    with ZipFile(args.output) as result:
        bad = result.testzip()
        if bad:
            raise ValueError(f"output PPTX has a corrupt member: {bad}")
        final_presentation = etree.fromstring(result.read("ppt/presentation.xml"))
        final_slides = final_presentation.findall("p:sldIdLst/p:sldId", NS)
        if len(final_slides) != len(args.keep):
            raise ValueError(f"output has {len(final_slides)} slides; expected {len(args.keep)}")
        final_parts = set(result.namelist())
        for part in sorted(final_parts):
            if part.endswith(".rels"):
                source = "" if part == "_rels/.rels" else part.rsplit("/_rels/", 1)[0] + "/" + part.rsplit("/", 1)[1][:-5]
                root = etree.fromstring(result.read(part))
                for rel in root.findall("rel:Relationship", NS):
                    if rel.get("TargetMode") == "External":
                        continue
                    resolved = resolve_target(source, rel.get("Target", ""))
                    if resolved not in final_parts:
                        raise ValueError(f"output relationship {part} points to missing {resolved}")

    print(f"Kept {len(args.keep)} slides from positions {args.keep}; package parts {len(parts)} -> {len(keep_parts)}.")
    print(f"Output: {args.output} ({args.output.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
