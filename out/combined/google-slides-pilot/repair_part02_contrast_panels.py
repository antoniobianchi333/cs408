"""Restore the source's translucent text panels in Part 2 rev2."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import posixpath
import re
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[3]
PILOTS = ROOT / "out/combined/google-slides-pilot"
DEFAULT_INPUT = PILOTS / "cs408-editable-part-02-scale-rev2.pptx"
DEFAULT_OUTPUT = PILOTS / "cs408-editable-part-02-scale-rev3.pptx"
DEFAULT_MAP = PILOTS / "cs408-editable-part-02-scale-rev2-map.csv"
DEFAULT_OUTPUT_MAP = PILOTS / "cs408-editable-part-02-scale-rev3-map.csv"

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"p": P, "a": A, "r": R}


def q(namespace: str, local: str) -> str:
    return f"{{{namespace}}}{local}"


def register_namespaces(data: bytes) -> None:
    for prefix, uri in re.findall(
        r'xmlns(?::([\w.-]+))?="([^"]+)"',
        data[:4096].decode("utf-8", errors="ignore"),
    ):
        ET.register_namespace(prefix or "", uri)


def serialize(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True,
                       short_empty_elements=True)


def slide_paths(package: ZipFile) -> list[str]:
    register_namespaces(package.read("ppt/presentation.xml"))
    presentation = ET.fromstring(package.read("ppt/presentation.xml"))
    relationships = ET.fromstring(package.read("ppt/_rels/presentation.xml.rels"))
    rels = {rel.attrib["Id"]: rel.attrib["Target"] for rel in relationships}
    paths = []
    for entry in presentation.findall(".//p:sldId", NS):
        target = rels[entry.attrib[q(R, "id")]].lstrip("/")
        paths.append(target if target.startswith("ppt/") else f"ppt/{target}")
    return paths


def restore_panel(data: bytes, target_text: str, alpha: int = 70000) -> bytes:
    register_namespaces(data)
    root = ET.fromstring(data)
    matches = []
    for shape in root.findall(".//p:sp", NS):
        text = "".join((node.text or "") for node in shape.findall(".//a:t", NS))
        if text.startswith(target_text):
            matches.append(shape)
    if len(matches) != 1:
        raise ValueError(f"expected one text shape starting {target_text!r}; found {len(matches)}")

    shape_props = matches[0].find("p:spPr", NS)
    if shape_props is None:
        raise ValueError(f"target text shape {target_text!r} has no p:spPr")
    no_fill = shape_props.find("a:noFill", NS)
    if no_fill is None:
        raise ValueError(f"target text shape {target_text!r} has no empty fill to replace")
    index = list(shape_props).index(no_fill)
    shape_props.remove(no_fill)
    fill = ET.Element(q(A, "solidFill"))
    color = ET.SubElement(fill, q(A, "srgbClr"), {"val": "FFFFFF"})
    ET.SubElement(color, q(A, "alpha"), {"val": str(alpha)})
    shape_props.insert(index, fill)
    return serialize(root)


def write_map(source: Path, output: Path) -> None:
    with source.open(newline="", encoding="utf-8") as inp:
        rows = list(csv.DictReader(inp))
        fields = list(rows[0])
    for row in rows:
        if int(row["combined_slide"]) in (474, 476):
            repair = "Restore editable body-text box with 70% white fill behind text"
            row["repair"] = "; ".join(x for x in (row["repair"], repair) if x)
    with output.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    if len(rows) != 232:
        raise ValueError(f"expected 232 mapped slides; found {len(rows)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--output-map", type=Path, default=DEFAULT_OUTPUT_MAP)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    replacements = {
        214: "A child is offered a choice between",
        216: "Results:",
    }
    with ZipFile(args.input) as source:
        paths = slide_paths(source)
        if len(paths) != 232:
            raise ValueError(f"expected 232 input slides; found {len(paths)}")
        changes = {}
        for number, target_text in replacements.items():
            path = paths[number - 1]
            changes[path] = restore_panel(source.read(path), target_text)

        with ZipFile(args.output, "w", compression=ZIP_DEFLATED, compresslevel=6) as out:
            for info in source.infolist():
                out.writestr(info, changes.pop(info.filename, source.read(info.filename)))
        if changes:
            raise RuntimeError(f"unwritten package parts: {sorted(changes)}")

    with ZipFile(args.output) as result:
        corrupt = result.testzip()
        if corrupt:
            raise RuntimeError(f"corrupt package member: {corrupt}")
        paths = slide_paths(result)
        if len(paths) != 232:
            raise RuntimeError(f"expected 232 output slides; found {len(paths)}")
        for number, target_text in replacements.items():
            slide = ET.fromstring(result.read(paths[number - 1]))
            matches = []
            for shape in slide.findall(".//p:sp", NS):
                text = "".join((node.text or "") for node in shape.findall(".//a:t", NS))
                if text.startswith(target_text):
                    matches.append(shape)
            if len(matches) != 1 or matches[0].find("p:spPr/a:solidFill/a:srgbClr/a:alpha", NS) is None:
                raise RuntimeError(f"editable translucent panel missing on local slide {number}")
    write_map(args.map, args.output_map)
    print(f"wrote {args.output} ({args.output.stat().st_size} bytes)")
    print(f"wrote {args.output_map} (232 mapped slides)")


if __name__ == "__main__":
    main()
