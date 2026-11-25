"""Repair four Google import defects in editable Part 2, preserving order."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import tempfile
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[3]
COMBINED = ROOT / "out/combined"
SOURCE_PDF = COMBINED / "cs408-all-slides.pdf"
INPUT = COMBINED / "cs408-editable-part-02.pptx"
OUTPUT = COMBINED / "google-slides-pilot/cs408-editable-part-02-scale-rev2.pptx"
TEMP_ROOT = ROOT / "out/.build"

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"p": P, "a": A, "r": R}


def q(namespace: str, local: str) -> str:
    return f"{{{namespace}}}{local}"


def register_xml_namespaces(data: bytes) -> None:
    head = data[:4096].decode("utf-8", errors="ignore")
    for prefix, uri in re.findall(r'xmlns(?::([\w.-]+))?="([^"]+)"', head):
        ET.register_namespace(prefix or "", uri)


def serialize(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True,
                       short_empty_elements=True)


def relationship_path(slide_path: str) -> str:
    folder, name = slide_path.rsplit("/", 1)
    return f"{folder}/_rels/{name}.rels"


def add_full_slide_picture(slide_data: bytes, rels_data: bytes,
                           image_target: str, width: int, height: int,
                           name: str) -> tuple[bytes, bytes]:
    register_xml_namespaces(slide_data)
    slide = ET.fromstring(slide_data)
    tree = slide.find(".//p:spTree", NS)
    if tree is None or len(tree) < 2:
        raise ValueError("slide is missing its required group properties")

    for child in list(tree)[2:]:
        tree.remove(child)

    register_xml_namespaces(rels_data)
    rels = ET.fromstring(rels_data)
    for rel in list(rels):
        if rel.attrib.get("Type", "").endswith("/image"):
            rels.remove(rel)
    used = [int(m.group(1)) for rel in rels
            if (m := re.fullmatch(r"rId(\d+)", rel.attrib.get("Id", "")))]
    image_rid = f"rId{max(used, default=0) + 1}"
    ET.SubElement(rels, q(PKG, "Relationship"), {
        "Id": image_rid,
        "Type": f"{R}/image",
        "Target": image_target,
    })

    pic = ET.Element(q(P, "pic"))
    nv = ET.SubElement(pic, q(P, "nvPicPr"))
    ET.SubElement(nv, q(P, "cNvPr"), {"id": "2", "name": name})
    cnv = ET.SubElement(nv, q(P, "cNvPicPr"))
    ET.SubElement(cnv, q(A, "picLocks"), {"noChangeAspect": "1"})
    ET.SubElement(nv, q(P, "nvPr"))
    fill = ET.SubElement(pic, q(P, "blipFill"))
    ET.SubElement(fill, q(A, "blip"), {q(R, "embed"): image_rid})
    stretch = ET.SubElement(fill, q(A, "stretch"))
    ET.SubElement(stretch, q(A, "fillRect"))
    props = ET.SubElement(pic, q(P, "spPr"))
    xfrm = ET.SubElement(props, q(A, "xfrm"))
    ET.SubElement(xfrm, q(A, "off"), {"x": "0", "y": "0"})
    ET.SubElement(xfrm, q(A, "ext"), {"cx": str(width), "cy": str(height)})
    geom = ET.SubElement(props, q(A, "prstGeom"), {"prst": "rect"})
    ET.SubElement(geom, q(A, "avLst"))
    tree.insert(2, pic)
    return serialize(slide), serialize(rels)


def move_picture_behind_text(slide_data: bytes) -> bytes:
    register_xml_namespaces(slide_data)
    slide = ET.fromstring(slide_data)
    tree = slide.find(".//p:spTree", NS)
    if tree is None:
        raise ValueError("slide has no shape tree")
    pictures = [child for child in list(tree) if child.tag == q(P, "pic")]
    if len(pictures) != 1:
        raise ValueError(f"expected one background image; found {len(pictures)}")
    picture = pictures[0]
    tree.remove(picture)
    tree.insert(2, picture)
    return serialize(slide)


def locate_slide_paths(zf: ZipFile) -> list[str]:
    register_xml_namespaces(zf.read("ppt/presentation.xml"))
    rels_root = ET.fromstring(zf.read("ppt/_rels/presentation.xml.rels"))
    targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels_root}
    pres = ET.fromstring(zf.read("ppt/presentation.xml"))
    paths = []
    for slide in pres.findall(".//p:sldId", NS):
        target = targets[slide.attrib[q(R, "id")]].lstrip("/")
        paths.append(target if target.startswith("ppt/") else f"ppt/{target}")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="part02-repair-", dir=TEMP_ROOT) as tmp:
        stage = Path(tmp)
        video_prefix = stage / "video-slide376"
        flyer_prefix = stage / "flyer-slide296"
        subprocess.run([
            "pdfimages", "-f", "376", "-l", "376", "-png",
            str(SOURCE_PDF), str(video_prefix),
        ], check=True)
        video_candidates = sorted(stage.glob("video-slide376-*.png"))
        if len(video_candidates) != 1:
            raise RuntimeError(f"expected one source media frame; found {len(video_candidates)}")
        video_image = video_candidates[0].read_bytes()
        subprocess.run([
            "pdftoppm", "-png", "-r", "144", "-f", "296", "-l", "296",
            "-singlefile", str(SOURCE_PDF), str(flyer_prefix),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        flyer_image = Path(f"{flyer_prefix}.png").read_bytes()

        image_additions = {
            "ppt/media/cs408-part02-combined-296.png": flyer_image,
            "ppt/media/cs408-part02-combined-376.png": video_image,
        }
        with ZipFile(args.input, "r") as source:
            names = set(source.namelist())
            paths = locate_slide_paths(source)
            # Combined slides 296, 376, 474, 476 map to Part 2 pages 36, 116,
            # 214, and 216 respectively.
            changes = {}
            for combined, local, stem, label, size in (
                (296, 36, "cs408-part02-combined-296.png", "Faculty seminar flyer image fallback", (13004800, 9753600)),
                (376, 116, "cs408-part02-combined-376.png", "Video still image fallback", (13004800, 9753600)),
            ):
                slide_path = paths[local - 1]
                rels_path = relationship_path(slide_path)
                changes[slide_path], changes[rels_path] = add_full_slide_picture(
                    source.read(slide_path), source.read(rels_path),
                    f"../media/{stem.rsplit('/', 1)[-1]}", *size,
                    name=f"Combined slide {combined}: {label}",
                )
            for local in (214, 216):
                slide_path = paths[local - 1]
                changes[slide_path] = move_picture_behind_text(source.read(slide_path))

            ctype_data = source.read("[Content_Types].xml")
            register_xml_namespaces(ctype_data)
            ctype = ET.fromstring(ctype_data)
            png_default = any(x.tag == q(CT, "Default") and x.attrib.get("Extension") == "png"
                              for x in ctype)
            if not png_default:
                ET.SubElement(ctype, q(CT, "Default"), {
                    "Extension": "png", "ContentType": "image/png",
                })
                changes["[Content_Types].xml"] = serialize(ctype)

            with ZipFile(args.output, "w", compression=ZIP_DEFLATED, compresslevel=6) as out:
                for info in source.infolist():
                    if info.filename in changes:
                        data = changes.pop(info.filename)
                    else:
                        data = source.read(info.filename)
                    out.writestr(info, data)
                for filename, data in image_additions.items():
                    if filename in names:
                        raise FileExistsError(filename)
                    out.writestr(filename, data, compress_type=ZIP_DEFLATED)
                for filename, data in changes.items():
                    if filename not in names:
                        raise FileNotFoundError(filename)
                    out.writestr(filename, data, compress_type=ZIP_DEFLATED)

    with ZipFile(args.output) as result:
        bad = result.testzip()
        if bad:
            raise RuntimeError(f"corrupt package member: {bad}")
        slide_paths = locate_slide_paths(result)
        if len(slide_paths) != 232:
            raise RuntimeError(f"expected 232 slides, got {len(slide_paths)}")
        for local in (36, 116):
            slide = ET.fromstring(result.read(slide_paths[local - 1]))
            if len(slide.findall(".//p:pic", NS)) != 1:
                raise RuntimeError(f"expected one fallback picture on local slide {local}")
        for local in (214, 216):
            slide = ET.fromstring(result.read(slide_paths[local - 1]))
            tree = slide.find(".//p:spTree", NS)
            contents = list(tree)[2:]
            if not contents or contents[0].tag != q(P, "pic"):
                raise RuntimeError(f"background image is not first on local slide {local}")

    print(f"wrote {args.output} ({args.output.stat().st_size} bytes)")
    print("repaired combined slides 296, 376, 474, and 476; slide count/order unchanged")


if __name__ == "__main__":
    main()
