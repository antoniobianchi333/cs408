from argparse import ArgumentParser
from collections import defaultdict
from copy import deepcopy
from io import BytesIO
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile
import re

import pikepdf
from lxml import etree as xml

from rebuild_round2 import A, P, R, PKG, Slide, geometry, node, serialize, stext


PILOT = Path(__file__).resolve().parent
REFERENCE = PILOT.parent / "cs408-all-slides.pdf"
BASE = PILOT / "cs408-editable-part-01-round3.pptx"
TARGET = PILOT / "cs408-editable-part-01-round4.pptx"
FORK_GRAPH = (103, 104, 105, 106, 108, 127, 128, 130, 131, 132, 157)
PRIME_GRAPH = (*range(137, 146), 160, *range(162, 176))
REL_IMAGE = R[1:-1] + "/image"


def slide_paths(archive):
    presentation = xml.fromstring(archive.read("ppt/presentation.xml"))
    relations = xml.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))
    targets = {x.get("Id"): x.get("Target") for x in relations}
    return ["ppt/" + targets[x.get(R + "id")] for x in presentation.find(P + "sldIdLst")]


def relpath(slide_path):
    path = PurePosixPath(slide_path)
    return str(path.parent / "_rels" / (path.name + ".rels"))


def shape_id(shape):
    return int(shape.find(f"./*/{P}cNvPr").get("id"))


def shape_name(shape):
    return shape.find(f"./*/{P}cNvPr").get("name")


def text_of(shape):
    return "".join(t.text or "" for t in shape.iter(A + "t"))


def box(shape):
    transform = shape.find(P + "spPr/" + A + "xfrm")
    return tuple(int(value) / 12700 for child in transform[:2] for value in child.attrib.values())


def draw_picture(slide, relation, name, placement):
    picture = node(slide.tree, P + "pic")
    props = node(picture, P + "nvPicPr")
    slide.identity(props, name)
    node(props, P + "cNvPicPr")
    node(props, P + "nvPr")
    paint = node(picture, P + "blipFill")
    node(paint, A + "blip", **{R + "embed": relation})
    node(node(paint, A + "stretch"), A + "fillRect")
    props = node(picture, P + "spPr")
    geometry(props, placement)
    node(node(props, A + "prstGeom", prst="rect"), A + "avLst")


def png_from_pdf(page, key):
    obj = page.images[key]
    frame = pikepdf.PdfImage(obj).as_pil_image().convert("RGB")
    if "/SMask" in obj:
        mask = pikepdf.PdfImage(obj.SMask).as_pil_image().convert("L")
        frame.putalpha(mask)
    data = BytesIO()
    frame.info.pop("icc_profile", None)
    frame.save(data, "PNG")
    return data.getvalue()


def red_paths(slide):
    result = []
    for shape in slide.tree.findall(P + "sp"):
        props = shape.find(P + "spPr")
        if props.find(A + "custGeom") is None:
            continue
        color = props.find(A + "ln/" + A + "solidFill/" + A + "srgbClr")
        if color is not None and color.get("val").upper() == "DD5F36":
            result.append(shape)
    return result


def graph_nodes(slide, expected, max_bottom, min_top=0):
    choices = defaultdict(list)
    for shape in slide.tree.findall(P + "sp"):
        label = re.sub(r"^BB", "B", "".join(text_of(shape).split()))
        if label in expected:
            rect = box(shape)
            if min_top < rect[1] and rect[1] + rect[3] < max_bottom and 65 < rect[2] < 77 and 35 < rect[3] < 45:
                choices[label].append(rect)
    assert all(len(choices[label]) == 1 for label in expected), choices
    return {label: choices[label][0] for label in expected}


def anchor(rect, side):
    x, y, w, h = rect
    return {
        "left": (x, y + h / 2), "right": (x + w, y + h / 2),
        "top": (x + w / 2, y), "bottom": (x + w / 2, y + h),
    }[side]


def connect(slide, nodes, source, target, exit="right", entry="left", via=()):
    slide.edge(anchor(nodes[source], exit), *via, anchor(nodes[target], entry))


def fork_graph(slide, number):
    nodes = graph_nodes(slide, ("B1", "C1", "B2", "B3", "B4", "C2", "B5"), 340)
    originals = [shape for shape in red_paths(slide) if box(shape)[1] < 320]
    assert len(originals) in (8, 9), (number, len(originals))
    has_entry = len(originals) == 9
    slide.remove(*(shape_id(shape) for shape in originals))
    draw_fork(slide, nodes, has_entry)
    if number == 128:
        inset = graph_nodes(slide, ("C1", "B2", "B3", "B4", "C2", "B5"), 540, 390)
        edges = [shape for shape in red_paths(slide) if box(shape)[1] > 380]
        assert len(edges) == 7
        slide.remove(*(shape_id(shape) for shape in edges))
        inset_shapes = [shape for shape in slide.tree.findall(P + "sp")
                        if text_of(shape).strip() and box(shape) in inset.values()]
        assert len(inset_shapes) == len(inset)
        for shape in inset_shapes:
            x, y, w, h = box(shape)
            slide.move(shape_id(shape), (x, y + 50, w, h))
        inset = {label: (x, y + 50, w, h) for label, (x, y, w, h) in inset.items()}
        draw_fork(slide, inset)


def draw_fork(slide, nodes, has_entry=False):
    if "B1" in nodes:
        connect(slide, nodes, "B1", "C1")
    for source, target in (("C1", "B3"), ("B3", "B4"), ("B4", "C2"), ("C2", "B5")):
        connect(slide, nodes, source, target)
    connect(slide, nodes, "C1", "B2", exit="top")
    connect(slide, nodes, "B2", "B4", entry="top")
    a = anchor(nodes["C2"], "bottom")
    b = anchor(nodes["C1"], "bottom")
    below = max(a[1], b[1]) + 23
    connect(slide, nodes, "C2", "C1", exit="bottom", entry="bottom",
            via=((a[0], below), (b[0], below)))
    if has_entry:
        x, y = anchor(nodes["B1"], "left")
        slide.edge((x - 43, y), (x, y))


def prime_graph(slide, number):
    nodes = graph_nodes(slide, ("C1", "B2", "C3", "B4", "B7", "C5", "B6"), 325)
    edges = [shape for shape in red_paths(slide) if box(shape)[1] < 375]
    has_entry = any(box(shape)[0] < 177 and box(shape)[3] < 2 for shape in edges)
    has_loop = any(box(shape)[1] > 310 for shape in edges)
    assert len(edges) == 8 + has_entry + has_loop, (number, len(edges), has_entry, has_loop)
    slide.remove(*(shape_id(shape) for shape in edges))
    for source, target in (("C1", "B2"), ("B2", "C3"), ("C3", "B4"), ("B4", "B7")):
        connect(slide, nodes, source, target)
    connect(slide, nodes, "C3", "C5")
    a, b = anchor(nodes["C1"], "top"), anchor(nodes["C3"], "top")
    high = min(a[1], b[1]) - 42
    connect(slide, nodes, "C1", "C3", exit="top", entry="top",
            via=((a[0] + 68, high), (b[0] - 72, high)))
    a, b = anchor(nodes["C5"], "top"), anchor(nodes["B7"], "left")
    connect(slide, nodes, "C5", "B7", exit="top", via=((a[0] + 62, b[1] + 27),))
    a, b = anchor(nodes["C5"], "right"), anchor(nodes["B6"], "left")
    connect(slide, nodes, "C5", "B6", via=(((a[0] + b[0]) / 2, a[1] - 25),))
    if has_loop:
        a, b = anchor(nodes["B6"], "bottom"), anchor(nodes["C5"], "bottom")
        connect(slide, nodes, "B6", "C5", exit="bottom", entry="bottom",
                via=(((a[0] + b[0]) / 2, max(a[1], b[1]) + 22),))
    if has_entry:
        x, y = anchor(nodes["C1"], "left")
        slide.edge((x - 51, y), (x, y))
    if number == 160:
        slide.remove(343, 344)
        slide.text("Prime path question", (608, 675, 384, 68),
                   ["How do we calculate the set", "of prime paths?"],
                   size=21, leading=28, background="F1F7FB", border="168BC2", align="ctr")
    for shape in slide.tree.findall(P + "sp"):
        if text_of(shape).startswith("Algorithm for calculating prime paths:"):
            compact_algorithm(shape)


def compact_algorithm(shape):
    for props in (*shape.iter(A + "rPr"), *shape.iter(A + "endParaRPr")):
        if int(props.get("sz", "0")) > 2000:
            props.set("sz", "2000")
    for para in shape.findall(P + "txBody/" + A + "p"):
        style = para.find(A + "pPr")
        if style is None:
            style = xml.Element(A + "pPr")
            para.insert(0, style)
        for tag in ("lnSpc", "spcBef", "spcAft"):
            current = style.find(A + tag)
            if current is not None:
                style.remove(current)
        leading = xml.Element(A + "lnSpc")
        node(leading, A + "spcPts", val=2450)
        style.insert(0, leading)


def subset_labels(slide):
    names = {"NodeCoverage": "Node", "EdgeCoverage": "Edge", "Edge-PairCoverage": "Edge-Pair",
             "CompletePathCoverage": "Complete Path", "?": "?"}
    covered = [(shape, names[key]) for shape in slide.tree.findall(P + "sp")
               if (key := "".join(text_of(shape).split())) in names]
    blocks = [box(shape) for shape, _ in covered]
    relations = [shape_id(shape) for shape in slide.tree.findall(P + "sp") if text_of(shape).strip() == "⊆"]
    assert len(blocks) == len(relations) + 1, (blocks, relations)
    slide.remove(*relations)
    for shape, title in covered:
        stext(shape, [title] if title == "?" else [title, "Coverage"],
              bold=True, size=22, leading=28, align="ctr")
    blocks.sort()
    for (x, y, w, h), (right, _, _, _) in zip(blocks, blocks[1:]):
        start = x + w
        assert right - start > 23
        slide.text("Subset relation", (start, y, right - start, h), ["⊆"], size=34, align="ctr")


def move_behind(slide, picture_id):
    picture = slide.ids[picture_id]
    assert picture.tag == P + "pic"
    slide.tree.remove(picture)
    slide.tree.insert(2, picture)


def graph_cover(slide):
    move_behind(slide, 197)
    stext(slide.move(196, (15, 457, 498, 270)),
          ["GRAPH-BASED", "COVERAGE CRITERIA", "(ROUND 2)"], font="Bebas Neue",
          size=46, leading=62, color="FAF6EB", align="ctr")


def lockset_slide(slide):
    move_behind(slide, 456)
    panel = slide.shape("Lock-set explanation contrast panel", (69, 197, 886, 501), color="FFFFFF")
    paint = panel.find(P + "spPr/" + A + "solidFill/" + A + "srgbClr")
    node(paint, A + "alpha", val=86000)
    slide.tree.remove(panel)
    slide.tree.insert(slide.tree.index(slide.ids[455]), panel)
    # Keep all original bullets, emphasis, and speaker-note content.
    for props in slide.ids[455].iter(A + "rPr"):
        if int(props.get("sz", "0")) > 3300:
            props.set("sz", "3300")


def quote_labels(slide):
    for shape in slide.tree.findall(P + "sp"):
        if text_of(shape).strip() in {"Testing", "Debugging"}:
            stext(shape, [text_of(shape).strip().upper()], size=37, font="Bebas Neue",
                  color="111111", align="ctr")


def native_checkmarks(slide):
    checks = [(shape_id(shape), box(shape)) for shape in slide.tree.findall(P + "sp")
              if text_of(shape) == "✅"]
    assert len(checks) == 4
    for identity, (x, y, _, _) in checks:
        slide.remove(identity)
        x, y = x + 5, y + 8
        slide.shape("Test stage check", (x, y, 29, 29), primitive="roundRect", color="079918")
        slide.edge((x + 6, y + 15), (x + 12, y + 21), (x + 23, y + 8),
                   color="FFFFFF", width=3, arrow=False)


def timeline_variant(slide, corrected):
    definitions = [shape_id(shape) for shape in slide.tree.findall(P + "sp")
                   if text_of(shape).strip().startswith("Event") and "same thread" in text_of(shape)]
    assert len(definitions) == 1
    slide.remove(*definitions)
    for shape in corrected.tree.findall(P + "sp"):
        if shape_name(shape) not in {"Happens-before definition", "Happens-before conditions", "Partial-order note"}:
            continue
        copy = deepcopy(shape)
        slide.last_id += 1
        copy.find(f"./*/{P}cNvPr").set("id", str(slide.last_id))
        slide.tree.append(copy)
    headings = [shape for shape in slide.tree.iter(P + "sp")
                if "".join(text_of(shape).split()) in {"Thread1", "Thread2"}]
    for shape in headings:
        _, y, _, _ = box(shape)
        title = text_of(shape).strip()
        stext(slide.move(shape_id(shape), (130, y, 148, 38)), [title], size=25, align="ctr")
    for shape in slide.tree.findall(P + "sp"):
        if text_of(shape).strip().startswith("//") and "program under test" in text_of(shape):
            original = corrected.ids[748].find(P + "txBody")
            if text_of(original) == text_of(shape):
                shape.replace(shape.find(P + "txBody"), deepcopy(original))


def build(output_path):
    with ZipFile(BASE) as source, pikepdf.Pdf.open(REFERENCE) as reference:
        paths = slide_paths(source)
        assert len(paths) == 260
        changed = {}
        media = {}

        def part(number):
            return Slide(xml.fromstring(source.read(paths[number - 1])))

        def update(number, slide):
            changed[paths[number - 1]] = serialize(slide.root)

        def add_media(number, specs, originals=None):
            slide = part(number)
            original_tree_size = len(slide.tree)
            if originals:
                first_index = min(slide.tree.index(slide.ids[i]) for i in originals)
                slide.remove(*originals)
            else:
                first_index = original_tree_size
            relationships = relpath(paths[number - 1])
            root = xml.fromstring(source.read(relationships))
            existing = {row.get("Id") for row in root}
            last = max(int(k.removeprefix("rId")) for k in existing)
            for name, png, placement in specs:
                file_name = f"cs408-r4-{name}.png"
                asset = f"ppt/media/{file_name}"
                media.setdefault(asset, png)
                last += 1
                rid = f"rId{last}"
                node(root, PKG + "Relationship", Id=rid, Type=REL_IMAGE, Target="../media/" + file_name)
                draw_picture(slide, rid, name, placement)
                picture = slide.tree[-1]
                slide.tree.remove(picture)
                slide.tree.insert(first_index, picture)
                first_index += 1
            if originals:
                for title, x in (("Requirements", 5), ("Design", 263), ("Development", 531), ("Deployment", 773)):
                    slide.text(f"{title} label", (x, 545, 246, 56), [title], size=31, align="ctr")
                    label = slide.tree[-1]
                    slide.tree.remove(label)
                    slide.tree.insert(first_index, label)
                    first_index += 1
            if number == 16:
                native_checkmarks(slide)
            changed[relationships] = serialize(root)
            update(number, slide)

        design = reference.pages[15]
        sources = [
            ("bird-illustration", "/Im11", (32, 246, 188, 142)),
            ("child-illustration", "/Im13", (47, 350, 158, 143)),
            ("airplane-sketch", "/Im12", (273, 276, 225, 169)),
            ("development-photo", "/Im15", (551, 288, 209, 157)),
            ("deployment-photo", "/Im14", (796, 299, 208, 142)),
        ]
        illustrations = [(name, png_from_pdf(design, key), rect) for name, key, rect in sources]
        add_media(16, illustrations, originals=(262, 265, 268, 271))
        add_media(17, illustrations, originals=(279, 282, 285, 288))
        outage = reference.pages[23]
        assert (outage.images["/Im24"].Width, outage.images["/Im24"].Height) == (884, 723)
        assert len(part(24).tree) == 2
        add_media(24, [("outage-screenshot", png_from_pdf(outage, "/Im24"), (70.067, 38.819, 883.867, 722.710))])

        for group, transform in ((FORK_GRAPH, fork_graph), (PRIME_GRAPH, prime_graph)):
            for number in group:
                slide = part(number)
                transform(slide, number)
                update(number, slide)
        for group, transform in [
            ((134, 135, 146, 147), subset_labels),
            ((69,), quote_labels),
            ((149,), graph_cover),
            ((233,), lockset_slide),
            ((242, 244), lambda slide: timeline_variant(slide, part(243))),
        ]:
            for number in group:
                slide = part(number)
                transform(slide)
                update(number, slide)

        assert all(asset not in source.namelist() for asset in media)
        # The base file already declares the PNG media content type.
        types = xml.fromstring(source.read("[Content_Types].xml"))
        assert any(t.get("Extension") == "png" and t.get("ContentType") == "image/png" for t in types)
        with ZipFile(output_path, "x", compression=ZIP_DEFLATED, compresslevel=3) as result:
            for filename in source.namelist():
                result.writestr(filename, changed[filename] if filename in changed else source.read(filename))
            for filename, content in media.items():
                result.writestr(filename, content)
        updated = [n for n, path in enumerate(paths, 1) if path in changed]
        print(f"Repaired {len(updated)} slides, retained all 260 positions: {updated}.")


if __name__ == "__main__":
    parser = ArgumentParser(description="Rebuild the fourth Google Slides import test.")
    parser.add_argument("--output", type=Path, default=TARGET)
    build(parser.parse_args().output)
