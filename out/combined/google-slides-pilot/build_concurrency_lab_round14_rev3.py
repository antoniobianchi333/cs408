#!/usr/bin/env python3
"""Place a visible editable archival label above the title on slides 4–6."""

from __future__ import annotations

import argparse
import csv
import io
import zipfile
from pathlib import Path

from lxml import etree


ROOT = Path(__file__).resolve().parents[3]
PILOT_DIR = Path(__file__).resolve().parent
SOURCE = ROOT / "labs/lab1-archive/slides/lab1_intro.pptx"
OUTPUT = PILOT_DIR / "cs408-concurrency-lab-intro-round14-rev3.pptx"
SOURCE_MAP = PILOT_DIR / "cs408-concurrency-lab-intro-round14-map.csv"
OUTPUT_MAP = PILOT_DIR / "cs408-concurrency-lab-intro-round14-rev3-map.csv"

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"p": P_NS, "a": A_NS}
EMU = 914400


def make_label(shape_id: int) -> etree._Element:
    shape = etree.Element(f"{{{P_NS}}}sp")
    nv = etree.SubElement(shape, f"{{{P_NS}}}nvSpPr")
    c_nv = etree.SubElement(nv, f"{{{P_NS}}}cNvPr")
    c_nv.set("id", str(shape_id))
    c_nv.set("name", "Round 14 archival screenshot label")
    etree.SubElement(nv, f"{{{P_NS}}}cNvSpPr", txBox="1")
    etree.SubElement(nv, f"{{{P_NS}}}nvPr")

    sp_pr = etree.SubElement(shape, f"{{{P_NS}}}spPr")
    xfrm = etree.SubElement(sp_pr, f"{{{A_NS}}}xfrm")
    etree.SubElement(
        xfrm,
        f"{{{A_NS}}}off",
        x=str(round(8.92 * EMU)),
        y=str(round(0.12 * EMU)),
    )
    etree.SubElement(
        xfrm,
        f"{{{A_NS}}}ext",
        cx=str(round(3.49 * EMU)),
        cy=str(round(0.22 * EMU)),
    )
    geometry = etree.SubElement(sp_pr, f"{{{A_NS}}}prstGeom", prst="rect")
    etree.SubElement(geometry, f"{{{A_NS}}}avLst")
    etree.SubElement(sp_pr, f"{{{A_NS}}}noFill")
    line = etree.SubElement(sp_pr, f"{{{A_NS}}}ln")
    etree.SubElement(line, f"{{{A_NS}}}noFill")

    tx = etree.SubElement(shape, f"{{{P_NS}}}txBody")
    etree.SubElement(
        tx,
        f"{{{A_NS}}}bodyPr",
        wrap="none",
        lIns="0",
        rIns="0",
        tIns="0",
        bIns="0",
        anchor="ctr",
    )
    etree.SubElement(tx, f"{{{A_NS}}}lstStyle")
    paragraph = etree.SubElement(tx, f"{{{A_NS}}}p")
    p_pr = etree.SubElement(paragraph, f"{{{A_NS}}}pPr", algn="r")
    etree.SubElement(p_pr, f"{{{A_NS}}}buNone")
    run = etree.SubElement(paragraph, f"{{{A_NS}}}r")
    r_pr = etree.SubElement(run, f"{{{A_NS}}}rPr", lang="en-US", sz="1100", i="1")
    solid = etree.SubElement(r_pr, f"{{{A_NS}}}solidFill")
    etree.SubElement(solid, f"{{{A_NS}}}srgbClr", val="555555")
    etree.SubElement(r_pr, f"{{{A_NS}}}latin", typeface="Arial")
    etree.SubElement(run, f"{{{A_NS}}}t").text = "Archived screenshots: CS503 Spring 2021"
    etree.SubElement(paragraph, f"{{{A_NS}}}endParaRPr", lang="en-US", sz="1100")
    return shape


def add_label(xml_bytes: bytes) -> bytes:
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(xml_bytes, parser)
    tree = root.find("p:cSld/p:spTree", NS)
    if tree is None:
        raise ValueError("slide has no shape tree")
    current_ids = [int(node.get("id")) for node in root.findall(".//p:cNvPr", NS)]
    next_id = max(current_ids, default=0) + 1
    tree.append(make_label(next_id))
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def build(source: Path, output: Path) -> None:
    with zipfile.ZipFile(source, "r") as src, zipfile.ZipFile(output, "w") as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename in {"ppt/slides/slide4.xml", "ppt/slides/slide5.xml", "ppt/slides/slide6.xml"}:
                data = add_label(data)
            dst.writestr(item, data)

    with SOURCE_MAP.open(newline="", encoding="utf-8") as input_file, OUTPUT_MAP.open(
        "w", newline="", encoding="utf-8"
    ) as output_file:
        reader = csv.DictReader(input_file)
        fields = reader.fieldnames
        if fields != ["output_slide", "source_file", "source_slide", "build_state"]:
            raise ValueError("unexpected Round 14 source-map columns")
        writer = csv.DictWriter(output_file, fieldnames=fields)
        writer.writeheader()
        for row in reader:
            if row["source_slide"] in {"4", "5", "6"}:
                row["build_state"] = (
                    "Source slide as authored; editable archival label above title; no timed animation"
                )
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    build(args.source, args.output)
    print(f"Wrote {args.output}")
    print(f"Wrote {OUTPUT_MAP}")


if __name__ == "__main__":
    main()
