#!/usr/bin/env python3
"""Restore the two editable source objects for Introduction PDF page 18.

The current local candidate has a reference-PDF crop for the article panel,
which flattened the image and the later headline build together. This repair
reuses the scanned article image embedded in the Keynote package, crops it in
the PPTX picture properties, and restores the headline as native text from the
converted source PPTX. The build-state expander can then hide the headline in
the first state and reveal it in the second.

This is a narrowly scoped source reconstruction. It does not modify either
input deck. Pillow is used only to re-encode the embedded TIFF as PNG; no image
pixels are altered.
"""

from __future__ import annotations

import argparse
import copy
import io
import posixpath
import re
import zipfile
from pathlib import Path

from lxml import etree
from PIL import Image


P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
IMAGE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
NS = {"p": P, "a": A, "r": R, "rel": REL, "ct": CT}


def xml_bytes(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def slide_part(parts: dict[str, bytes], position: int) -> str:
    presentation = etree.fromstring(parts["ppt/presentation.xml"])
    relationships = etree.fromstring(parts["ppt/_rels/presentation.xml.rels"])
    relmap = {
        item.get("Id"): item
        for item in relationships.findall("rel:Relationship", NS)
    }
    slides = presentation.find("p:sldIdLst", NS)
    if slides is None or position < 1 or position > len(slides):
        raise ValueError(f"slide position {position} is outside the presentation")
    node = slides[position - 1]
    relation = relmap.get(node.get(f"{{{R}}}id"))
    if relation is None:
        raise ValueError(f"slide position {position} has no relationship")
    target = relation.get("Target", "")
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join("ppt", target))


def read_parts(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"{path} has a corrupt ZIP member: {bad}")
        return {item.filename: archive.read(item.filename) for item in archive.infolist()}


def save_parts(path: Path, parts: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in parts.items():
            archive.writestr(name, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--source-pptx", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--candidate-slide-position", type=int, default=19)
    parser.add_argument("--source-slide-position", type=int, default=21)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    candidate = read_parts(args.candidate)
    source_pptx = read_parts(args.source_pptx)
    output_slide = slide_part(candidate, args.candidate_slide_position)
    source_slide = slide_part(source_pptx, args.source_slide_position)
    output_rels = posixpath.join(
        posixpath.dirname(output_slide), "_rels", posixpath.basename(output_slide) + ".rels"
    )
    source_xml = etree.fromstring(source_pptx[source_slide])
    output_xml = etree.fromstring(candidate[output_slide])
    output_relationships = etree.fromstring(candidate[output_rels])

    headline_text = "A space error: $370 million for an integer\u00a0overflow"
    source_shapes = source_xml.xpath(".//p:spTree/p:sp", namespaces=NS)
    headline_shapes = [
        shape
        for shape in source_shapes
        if headline_text in "".join(shape.xpath(".//a:t/text()", namespaces=NS))
    ]
    if len(headline_shapes) != 1:
        raise ValueError(f"expected one source headline shape, found {len(headline_shapes)}")

    pictures = output_xml.xpath(
        ".//p:spTree/p:pic[p:nvPicPr/p:cNvPr[@name='Reference article screenshot']]",
        namespaces=NS,
    )
    if not pictures:
        # The batch assembler can preserve the imported picture while
        # normalizing its nonvisual name to an empty string. On this source
        # slide the screenshot is the only picture, so it remains an
        # unambiguous replacement target.
        all_pictures = output_xml.xpath(".//p:spTree/p:pic", namespaces=NS)
        if len(all_pictures) == 1:
            pictures = all_pictures
    if len(pictures) != 1:
        raise ValueError(f"expected one article-panel fallback picture, found {len(pictures)}")
    picture = pictures[0]

    image_relations = output_relationships.findall("rel:Relationship", NS)
    existing_names = {
        node.get("name")
        for node in output_xml.xpath(".//p:cNvPr", namespaces=NS)
    }
    headline_shape = copy.deepcopy(headline_shapes[0])
    c_nv_pr = headline_shape.find(".//p:cNvPr", NS)
    if c_nv_pr is None:
        raise ValueError("source headline has no non-visual shape properties")
    shape_id = c_nv_pr.get("id")
    used_ids = {
        node.get("id") for node in output_xml.xpath(".//p:cNvPr", namespaces=NS)
    }
    if shape_id in used_ids:
        existing = output_xml.xpath(
            f".//p:sp[p:nvSpPr/p:cNvPr[@id='{shape_id}']]", namespaces=NS
        )
        expected_text = headline_text.replace("\u00a0", " ")
        matches = [
            shape for shape in existing
            if expected_text in " ".join(
                "".join(shape.xpath(".//a:t/text()", namespaces=NS)).replace("\u00a0", " ").split()
            )
        ]
        if len(existing) == 1 and len(matches) == 1:
            # The assembler can retain LibreOffice's editable version of the
            # caption. Replace that same object with the exact source shape
            # rather than duplicating the headline or failing on its ID.
            matches[0].getparent().remove(matches[0])
            used_ids = {
                node.get("id") for node in output_xml.xpath(".//p:cNvPr", namespaces=NS)
            }
        else:
            raise ValueError(f"headline shape ID {shape_id} is already used by a different candidate object")
    c_nv_pr.set("name", "Build 2 article headline")
    if c_nv_pr.get("name") in existing_names:
        raise ValueError("headline shape name unexpectedly already exists")
    body_properties = headline_shape.find(".//a:bodyPr", NS)
    auto_fit = body_properties.find("a:normAutofit", NS) if body_properties is not None else None
    if auto_fit is None:
        raise ValueError("source headline has no normalized auto-fit properties")
    # LibreOffice exports the source 70 pt headline at 43.7 pt high and wraps,
    # despite the source's 50% auto-fit. After font substitution, 27 pt is the
    # largest fixed size that fits the full headline on one line in the source
    # box and closely matches the reference text's width and height.
    body_properties.remove(auto_fit)
    for run_properties in headline_shape.xpath(
        ".//a:rPr|.//a:defRPr|.//a:endParaRPr", namespaces=NS
    ):
        run_properties.set("sz", "2700")
    headline_transform = headline_shape.find(".//a:xfrm", NS)
    headline_offset = headline_transform.find("a:off", NS) if headline_transform is not None else None
    if headline_offset is None:
        raise ValueError("source headline has no position transform")
    # The imported text baseline lands 19.7 pt above the Fall PDF reference.
    # Move the editable box down 250,000 EMU (about 19.7 pt).
    headline_offset.set("y", str(int(headline_offset.get("y")) + 250000))
    picture.getparent().append(headline_shape)

    with zipfile.ZipFile(args.key) as key_package:
        image_tiff = key_package.read("Data/pasted-image-4629.tiff")
    with Image.open(io.BytesIO(image_tiff)) as source_image:
        encoded = io.BytesIO()
        source_image.save(encoded, format="PNG")
    media_part = "ppt/media/cs408-intro-page18-keynote-image.png"
    if media_part in candidate:
        raise ValueError(f"output media path already exists: {media_part}")
    candidate[media_part] = encoded.getvalue()

    used_relation_ids = [
        int(match.group(1))
        for item in image_relations
        if (match := re.fullmatch(r"rId(\d+)", item.get("Id", "")))
    ]
    image_rid = f"rId{max(used_relation_ids, default=0) + 1}"
    etree.SubElement(
        output_relationships,
        f"{{{REL}}}Relationship",
        Id=image_rid,
        Type=IMAGE_REL,
        Target="../media/cs408-intro-page18-keynote-image.png",
    )
    blip = picture.find("p:blipFill/a:blip", NS)
    if blip is None:
        raise ValueError("article-panel picture has no image relationship")
    blip.set(f"{{{R}}}embed", image_rid)
    fill = picture.find("p:blipFill", NS)
    old_crop = fill.find("a:srcRect", NS)
    if old_crop is not None:
        fill.remove(old_crop)
    crop = etree.Element(f"{{{A}}}srcRect", t="20200")
    fill.insert(1, crop)

    content_types = etree.fromstring(candidate["[Content_Types].xml"])
    png_default = content_types.xpath("./ct:Default[@Extension='png']", namespaces=NS)
    if not png_default:
        etree.SubElement(
            content_types,
            f"{{{CT}}}Default",
            Extension="png",
            ContentType="image/png",
        )

    candidate[output_slide] = xml_bytes(output_xml)
    candidate[output_rels] = xml_bytes(output_relationships)
    candidate["[Content_Types].xml"] = xml_bytes(content_types)
    save_parts(args.output, candidate)
    print(f"Prepared candidate slide {args.candidate_slide_position} from {args.candidate}")
    print(f"Restored editable 27 pt headline at the reference vertical position and linked {media_part} with 20.2% top crop")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
