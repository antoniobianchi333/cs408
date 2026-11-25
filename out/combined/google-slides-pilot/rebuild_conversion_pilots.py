"""Build small, source-mapped import tests from the verified Round 4 PPTX."""

from argparse import ArgumentParser
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from posixpath import dirname, join, normpath
import re
from string import ascii_lowercase
from subprocess import run
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

import pikepdf
from PIL import Image

from rebuild_round2 import A, P, PKG, R, Slide, node, px, serialize, stext, xml
from rebuild_round4 import (
    PILOT, REFERENCE, REL_IMAGE, box, connect, draw_picture, graph_nodes,
    png_from_pdf, red_paths, relpath, shape_id, slide_paths, text_of,
)


BASE = PILOT / "cs408-editable-part-01-round4.pptx"
SELECTION = {
    5: (16, 19, 24, 36, 149, 230, 232, 233, 251, 253),
    6: (69, 73, 103, 128, 134, 135, 136, 147, 162, 173, 174, 175, 243),
    7: (19, 73, 103, 107, 121, 134, 135, 147, 175, 230, 253),
    8: (69, 77, 78),
    9: (98, 99, 100, 101, 102, 104),
    10: (153, 154, 155, 156),
    11: (114, 115, 116),
}
SCIENTIFIC_METHOD_ARROW_IDS = {
    77: (487, 488, 490, 491, 492, 497, 498),
    78: (506, 507, 510, 511, 512, 517, 518, 519),
}
CFG_ARROW_IDS = {
    99: (400, 401, 402, 403, 404, 405, 414, 416),
    100: (455, 456, 460, 461, 462, 463, 464, 465, 471, 472, 474, 475, 476),
    101: (513, 515, 516, 517, 521, 522, 526, 527),
    102: (725, 727, 728, 729, 733, 734, 738, 741, 743, 745),
    115: (239, 240, 241, 242, 243, 244, 253, 255),
    116: (265, 266, 267, 268, 269, 270, 277, 279),
}
CFG_BRANCH_LABEL_IDS = {
    99: (406, 407, 408, 409),
    100: (466, 477),
    101: (518, 519, 524, 525),
    102: (730, 731, 736, 737, 739, 742),
    115: (245, 246, 247, 248),
    116: (271, 272, 273, 274),
}
SUBSET_RELATION_POSITIONS = {
    155: {
        252: (246, 286, 42, 48),
        253: (246, 436, 42, 48),
        250: (246, 586, 42, 48),
    },
    156: {
        261: (246, 286, 42, 48),
        262: (246, 436, 42, 48),
        259: (246, 586, 42, 48),
        265: (650, 286, 42, 48),
        271: (316, 365, 44, 48),
        268: (742, 436, 42, 48),
        269: (730, 586, 42, 48),
    },
}
CFG_FIT_LABEL_IDS = {115: 250, 116: 275, 154: 238}
PROGRAM_TEXT_LABEL_IDS = {115: 249}
DRAW_IMAGE = {"q", "cm", "ri", "m", "l", "c", "v", "y", "re", "h", "W", "W*", "n"}
SVG_NS = "http://www.w3.org/2000/svg"
SVG_NUMBERS = re.compile(r"[A-Za-z]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def isolated_image(page, key):
    """Use the source PDF transformation and clipping path for one picture."""
    ops = list(pikepdf.parse_content_stream(page))
    matches = [i for i, op in enumerate(ops)
               if str(op.operator) == "Do" and str(op.operands[0]) == key]
    assert len(matches) == 1, key
    end, = matches
    start = end
    while start and str(ops[start - 1].operator) in DRAW_IMAGE:
        start -= 1
    selected = [op for op in ops[start:end + 1] if str(op.operator) != "ri"]
    q_depth = sum(str(op.operator) == "q" for op in selected)
    assert q_depth and any(str(op.operator) == "cm" for op in selected), key
    with TemporaryDirectory(prefix="cs408-picture-") as stage, pikepdf.Pdf.new() as doc:
        doc.pages.append(page)
        doc.pages[0].Contents = doc.make_stream(
            pikepdf.unparse_content_stream(selected) + b"\nQ\n" * q_depth
        )
        source = Path(stage) / "picture.pdf"
        doc.save(source)
        run(["pdftocairo", "-png", "-transp", "-r", "144", "-singlefile",
             str(source), str(source.with_suffix(""))], check=True)
        with Image.open(source.with_suffix(".png")) as raster:
            assert raster.size == (2048, 1536), raster.size
            bounds = raster.getchannel("A").getbbox()
            assert bounds, key
            contents = BytesIO()
            raster.crop(bounds).save(contents, format="PNG")
    x1, y1, x2, y2 = bounds
    return contents.getvalue(), (x1 / 2, y1 / 2, (x2 - x1) / 2, (y2 - y1) / 2)


def place_picture(slide, assets, name, data, bounds, layer=None):
    path = f"cs408-{name}.png"
    assets[path] = data
    draw_picture(slide, name, name, bounds)
    if layer is not None:
        image = slide.tree[-1]
        slide.tree.remove(image)
        slide.tree.insert(layer, image)


def fix_media(slide, page, index, assets, round_number):
    if index == 19:
        excerpt, bounds = isolated_image(page, "/Im21")
        place_picture(slide, assets, "ariane-report-excerpt", excerpt, bounds,
                      layer=slide.tree.index(slide.ids[310]))
        title = text_of(slide.ids[310]).replace("\u00a0", " ")
        stext(slide.move(310, (329, 433, 669, 37)), [title], size=24,
              bold=True, color="17212C")
        slide.remove(311)
        stext(slide.move(312, (325, 60, 421, 94)), ["Why test?"], size=70,
              bold=True, color="17212C")
        paragraph = slide.ids[312].find(f"{P}txBody/{A}p")
        default_run = paragraph.find(A + "r")
        for position, (label, color) in enumerate((("Why", "168BC2"), (" test", "17212C"), ("?", "168BC2"))):
            styled = deepcopy(default_run)
            styled.find(A + "t").text = label
            props = styled.find(A + "rPr")
            props.find(f"{A}solidFill/{A}srgbClr").set("val", color)
            if position == 0:
                props.set("u", "sng")
            paragraph.insert(position + 1, styled)
        paragraph.remove(default_run)
    elif index == 36:
        position = slide.tree.index(slide.ids[368])
        slide.remove(368)
        portrait, bounds = isolated_image(page, "/Im33")
        place_picture(slide, assets, "software-quality-portrait", portrait, bounds, layer=position)
        stext(slide.move(367, (26, 19, 660, 249)),
              ["Our Goal: Produce software that", "is good enough for a given", "context"],
              size=43, leading=65, color="FFFFFF", vertical="t")
        lines = slide.ids[367].findall(f"{P}txBody/{A}p")
        for row, prefix in [(lines[0], "Our Goal:"), (lines[1], "good enough")]:
            run_xml = row.find(A + "r")
            old = run_xml.find(A + "t").text
            before, after = old.split(prefix)
            row.remove(run_xml)
            row.remove(row.find(A + "endParaRPr"))
            for part, bold in [(before, 0), (prefix, 1), (after, 0)]:
                if part:
                    run_part = node(row, A + "r")
                    props = node(run_part, A + "rPr", sz=4300, b=bold)
                    node(node(props, A + "solidFill"), A + "srgbClr", val="FFFFFF")
                    node(props, A + "latin", typeface="Arial")
                    node(run_part, A + "t").text = part
        for identity, (x, y, width) in zip((369, 370, 371), ((50, 398, 340), (130, 470, 365), (357, 542, 295))):
            label = text_of(slide.ids[identity])
            stext(slide.move(identity, (x, y, width, 54)), [label], size=32, color="FFFFFF")
    elif index == 230:
        slide.remove(*slide.ids)
        for key, name in [("/Im4", "dynamic-analysis-background"), ("/Im6", "dynamic-analysis-portrait")]:
            photo, bounds = isolated_image(page, key)
            place_picture(slide, assets, name, photo, bounds)
        slide.text("Answer heading", (267, 42, 490, 86), ["Answer:"], size=60, bold=True,
                   color="FFFFFF", background="25313F", align="ctr")
        slide.text("Instrumentation explanation", (24, 196, 294, 178),
                   ["Instrument program", "to monitor data", "accesses and", "synchronization points"],
                   size=22, leading=32, align="ctr", background="EAF5FC", border="097BB5")
        slide.text("Run-time analysis explanation", (739, 196, 261, 178),
                   ["Analyze data", "gathered from", "run-time executions"],
                   size=22, leading=34, align="ctr", background="FFF3EC", border="AD4E25")
        slide.edge((217, 583), (162, 375), color="097BB5", width=4.5)
        slide.edge((770, 583), (860, 375), color="AD4E25", width=4.5)
        slide.text("Analysis answer", (53, 583, 918, 102), ["White-Box Dynamic Program Analysis"],
                   size=42, color="FFFFFF", background="25313F", bold=True, align="ctr")
    elif index == 232:
        slide.remove(433, 435, 436, 437, 438)
        slide.text("Two approaches", (197, 323, 473, 161),
                   ["1. Lockset Analysis", "2. Happens-Before Analysis"],
                   size=29, leading=49, color="FFFFFF", bold=True, background="19232D", align="ctr")
    elif index == 251:
        stext(slide.move(942, (18, 262, 308, 202)), ["False", "Negatives"],
              size=43, leading=60, color="C14E29", bold=True, align="ctr")
        slide.remove(943)
        slide.text("Photo caption", (409, 630, 340, 98), ["Formal Methods", "Monkey"],
                   size=30, leading=38, color="FFFFFF", background="23313C", align="ctr")
    elif index == 253:
        slide.remove(965, 968)
        stext(slide.move(962, (214, 35, 596, 85)), ["static race detection"],
              size=46, color="151515", align="ctr")
        slide.edge((229, 121), (795, 121), color="168BC2", width=2, arrow=False)
        leading = 21 if round_number == 7 else 24
        fit_text(slide.move(964, (47, 288, 407, 442)), 19, leading, code=True)
        image = page.images["/Im13"]
        width = 548
        place_picture(slide, assets, "rust-compiler-diagnostic", png_from_pdf(page, "/Im13"),
                      (463, 365, width, width * int(image.Height) / int(image.Width)))


def fit_text(shape, size, leading, *, code=False):
    body = shape.find(P + "txBody")
    body_props = body.find(A + "bodyPr")
    for axis in ("l", "r", "t", "b"):
        body_props.set(axis + "Ins", str(px(14)))
    body_props.set("anchor", "t")
    if code:
        body_props.set("wrap", "none")
    for tag in ("noAutofit", "normAutofit", "spAutoFit"):
        current = body_props.find(A + tag)
        if current is not None:
            body_props.remove(current)
    body_props.insert(0, xml.Element(A + "noAutofit"))
    for para in body.findall(A + "p"):
        style = para.find(A + "pPr")
        if style is None:
            style = xml.Element(A + "pPr")
            para.insert(0, style)
        for tag in ("lnSpc", "spcBef", "spcAft"):
            el = style.find(A + tag)
            if el is not None:
                style.remove(el)
        for position, (tag, val) in enumerate((("lnSpc", leading * 100), ("spcBef", 0), ("spcAft", 0))):
            el = xml.Element(A + tag)
            node(el, A + "spcPts", val=val)
            style.insert(position, el)
        if code:
            for bullet in list(style):
                if xml.QName(bullet).localname.startswith("bu"):
                    style.remove(bullet)
            next_style = next((i for i, child in enumerate(style)
                               if child.tag in {A + "tabLst", A + "defRPr", A + "extLst"}), len(style))
            style.insert(next_style, xml.Element(A + "buNone"))
            style.set("marL", "0")
            style.set("indent", "0")
    for tag in ("rPr", "endParaRPr", "defRPr"):
        for props in body.iter(A + tag):
            props.set("sz", str(size * 100))
            if code:
                family = props.find(A + "latin")
                if family is None:
                    family = node(props, A + "latin")
                family.set("typeface", "Roboto Mono")


def ripr(slide):
    slide.remove(454, 455, 456, 460, 462)
    layouts = {
        444: ((91, 183, 149, 100), ["Test"]),
        446: ((68, 358, 195, 138), ["Faulty", "Location"]),
        448: ((29, 550, 275, 149), ["Erroneous", "Program State"]),
        450: ((457, 359, 249, 117), ["Erroneous", "Output State"]),
        452: ((740, 328, 220, 174), ["Observable", "Portion of the", "Output States"]),
        453: ((393, 259, 571, 64), ["All Final Program Output States"]),
        458: ((177, 299, 143, 48), ["Reaches"]),
        459: ((177, 498, 130, 48), ["Infects"]),
        461: ((310, 538, 179, 48), ["Propagates"]),
        464: ((738, 558, 140, 48), ["Reveals"]),
    }
    for identity, (rect, lines) in layouts.items():
        stext(slide.move(identity, rect), lines, size=27, leading=33, align="ctr")
    for start, end in [((166, 284), (166, 357)), ((166, 498), (166, 552)),
                       ((281, 585), (471, 471)), ((720, 463), (720, 617))]:
        slide.edge(start, end, color="171717", width=3)


def coverage_fork(slide, index):
    nodes = graph_nodes(slide, ("B1", "C1", "B2", "B3", "B4", "B5"), 470)
    red = red_paths(slide)
    if index == 147:
        # The original on slide 147 includes a B4-to-C1 return edge.
        assert len(red) == 7, (index, len(red))
    else:
        assert len(red) == 6, (index, len(red))
    slide.remove(*(shape_id(shape) for shape in red))
    for source, target in [("B1", "C1"), ("C1", "B3"), ("B3", "B4"), ("B4", "B5")]:
        connect(slide, nodes, source, target)
    connect(slide, nodes, "C1", "B2", exit="top")
    connect(slide, nodes, "B2", "B4", entry="top")
    if index == 147:
        # This return branch is visible in the original Apple PDF.
        x, y, width, height = nodes["B4"]
        cx, cy, cw, ch = nodes["C1"]
        below = max(y + height, cy + ch) + 22
        connect(slide, nodes, "B4", "C1", exit="bottom", entry="bottom",
                via=((x + width / 2, below), (cx + cw / 2, below)))
    else:
        foot = text_of(slide.ids[823])
        stext(slide.move(823, (605, 709, 372, 40)), [foot], size=19, align="r")


def path_list(slide):
    group, = [shape for shape in slide.tree.findall(P + "grpSp")
              if text_of(shape).startswith("Prime Paths")]
    paragraphs = [[p, text_of(p).strip()] for p in group.iter(A + "p") if text_of(p).strip()]
    assert len(paragraphs) == 10 and paragraphs[0][1] == "Prime Paths"
    slide.tree.remove(group)
    slide.shape("Prime paths panel", (49, 328, 240, 366), color="FFFFFF", stroke="171717", width=2)
    slide.text("Prime paths heading", (59, 335, 220, 46), ["Prime Paths"],
               size=25, bold=True, color="171717", align="ctr")
    slide.edge((64, 385), (274, 385), color="171717", width=1.5, arrow=False)
    for row, ((para, path), letter) in enumerate(zip(paragraphs[1:], ascii_lowercase)):
        color = next(
            run.find(f"{A}rPr/{A}solidFill/{A}srgbClr").get("val")
            for run in para.findall(A + "r")
            if text_of(run).strip()
        )
        y = 395 + row * 30
        slide.text(f"Path {letter} label", (64, y, 29, 26), [f"{letter}."],
                   size=21, color="171717")
        slide.text(f"Path {letter} nodes", (96, y, 180, 26), [path],
                   size=21, color=color, bold=True)


def test_paths_graph(slide):
    labels = ("L2", "L3", "L5", "L7")
    nodes = graph_nodes(slide, labels, 675, 400)
    edges = red_paths(slide)
    assert len(edges) == 5
    slide.remove(*(shape_id(shape) for shape in edges))
    for source, target in (("L2", "L3"), ("L2", "L5"), ("L3", "L7"), ("L5", "L7")):
        connect(slide, nodes, source, target)
    x, y, _, height = nodes["L2"]
    slide.edge((x - 49, y + height / 2), (x, y + height / 2))
    body, = [i for i, shape in slide.ids.items()
             if text_of(shape).startswith("Each test case corresponds")]
    fit_text(slide.move(body, (62, 183, 931, 237)), 30, 36)
    code, = [i for i, shape in slide.ids.items() if text_of(shape).startswith("int bar(int x)")]
    fit_text(slide.move(code, (63, 440, 340, 282)), 21, 25, code=True)
    for title, bounds in (("true", (600, 445, 75, 35)), ("false", (597, 575, 78, 35))):
        identity, = [i for i, shape in slide.ids.items() if text_of(shape).strip() == title]
        stext(slide.move(identity, bounds), [title], size=22, align="ctr")


def fix_structure(slide, index, round_number):
    if index == 73:
        ripr(slide)
    elif index == 103:
        fit_text(slide.move(747, (53, 421, 436, 258)), 29, 39)
        if round_number == 7:
            fit_text(slide.move(763, (505, 375, 490, 363)), 20, 24, code=True)
        else:
            fit_text(slide.move(763, (505, 407, 490, 331)), 20, 26, code=True)
    elif index in (107, 121):
        test_paths_graph(slide)
    elif index in (134, 135):
        code, = [i for i, shape in slide.ids.items() if text_of(shape).startswith("public static int compute")]
        leading = 22 if round_number == 7 else 26
        fit_text(slide.move(code, (516, 430, 479, 311)), 17, leading, code=True)
    elif index in (136, 147):
        coverage_fork(slide, index)
    elif index in (173, 174, 175):
        path_list(slide)


def svg_commands(data):
    tokens = SVG_NUMBERS.findall(data)
    result = []
    i = 0
    while i < len(tokens):
        command = tokens[i]
        i += 1
        if command == "M" or command == "L":
            values = tuple(float(tokens[i + j]) for j in range(2))
            i += 2
        elif command == "C":
            values = tuple(float(tokens[i + j]) for j in range(6))
            i += 6
        elif command in ("Z", "z"):
            values = ()
        else:
            raise ValueError(f"Unsupported SVG path command: {command}")
        result.append((command.upper(), values))
    return result


def svg_translation(path):
    transform = path.get("transform", "")
    if not transform:
        return 0.0, 0.0
    match = re.fullmatch(r"matrix\(([^)]+)\)", transform)
    assert match, transform
    a, b, c, d, x, y = (float(value) for value in match.group(1).split(","))
    assert (a, b, c, d) == (1.0, 0.0, 0.0, 1.0), transform
    return x, y


def source_arrow_paths(index):
    prefix = f"cs408-scientific-method-{index}-"
    with TemporaryDirectory(prefix=prefix) as stage:
        output = Path(stage) / "page-svg"
        run(["pdftocairo", "-f", str(index), "-l", str(index), "-svg",
             str(REFERENCE), str(output)], check=True)
        document = xml.parse(str(output))
    paths = document.xpath(
        ".//svg:g[@id='surface1']/svg:path",
        namespaces={"svg": SVG_NS},
    )
    arrows = []
    for path_index, path in enumerate(paths):
        style = {}
        for item in path.get("style", "").split(";"):
            if ":" in item:
                key, value = item.split(":", 1)
                style[key.strip()] = value.strip()
        if style.get("fill") == "none" and style.get("stroke-width") == "4":
            head = paths[path_index + 1]
            head_style = {}
            for item in head.get("style", "").split(";"):
                if ":" in item:
                    key, value = item.split(":", 1)
                    head_style[key.strip()] = value.strip()
            assert head_style.get("stroke") == "none" and head_style.get("fill") == "rgb(0%,0%,0%)"
            arrows.append((svg_commands(path.get("d", "")), svg_translation(path),
                           svg_commands(head.get("d", "")), svg_translation(head)))
    expected = len(SCIENTIFIC_METHOD_ARROW_IDS[index])
    assert len(arrows) == expected, (index, len(arrows), expected)
    return arrows


def source_cfg_arrow_paths(index):
    prefix = f"cs408-cfg-{index}-"
    with TemporaryDirectory(prefix=prefix) as stage:
        output = Path(stage) / "page-svg"
        run(["pdftocairo", "-f", str(index), "-l", str(index), "-svg",
             str(REFERENCE), str(output)], check=True)
        document = xml.parse(str(output))
    paths = document.xpath(".//svg:path", namespaces={"svg": SVG_NS})
    arrows = []
    for path_index, path in enumerate(paths[:-1]):
        style = {}
        for item in path.get("style", "").split(";"):
            if ":" in item:
                key, value = item.split(":", 1)
                style[key.strip()] = value.strip()
        if (style.get("fill") != "none" or style.get("stroke-width") != "3"
                or not style.get("stroke", "").startswith("rgb(86.666")):
            continue
        head = paths[path_index + 1]
        head_style = {}
        for item in head.get("style", "").split(";"):
            if ":" in item:
                key, value = item.split(":", 1)
                head_style[key.strip()] = value.strip()
        if (head_style.get("stroke") != "none"
                or not head_style.get("fill", "").startswith("rgb(86.666")):
            continue
        arrows.append((svg_commands(path.get("d", "")), svg_translation(path),
                       svg_commands(head.get("d", "")), svg_translation(head)))
    expected = len(CFG_ARROW_IDS[index])
    assert len(arrows) == expected, (index, len(arrows), expected)
    return arrows


def write_custom_geometry(props, commands, translation, *, fill_mode, stroke):
    tx, ty = translation
    # The slide and the combined reference use the same source coordinate units.
    scale = 1.0
    transformed = []
    for command, values in commands:
        points = [(values[i] + tx, values[i + 1] + ty)
                  for i in range(0, len(values), 2)]
        points = [(x * scale, y * scale) for x, y in points]
        transformed.append((command, points))
    xs = [x for _, points in transformed for x, _ in points]
    ys = [y for _, points in transformed for _, y in points]
    left, top, right, bottom = min(xs), min(ys), max(xs), max(ys)
    if right - left < 1:
        left -= (1 - (right - left)) / 2
        right = left + 1
    if bottom - top < 1:
        top -= (1 - (bottom - top)) / 2
        bottom = top + 1
    width, height = px(right - left), px(bottom - top)

    transform = props.find(A + "xfrm")
    if transform is not None:
        props.remove(transform)
    transform = xml.Element(A + "xfrm")
    node(transform, A + "off", x=px(left), y=px(top))
    node(transform, A + "ext", cx=width, cy=height)
    props.insert(0, transform)
    custom = props.find(A + "custGeom")
    if custom is not None:
        props.remove(custom)
    custom = node(props, A + "custGeom")
    for tag in ("avLst", "gdLst", "ahLst", "cxnLst"):
        node(custom, A + tag)
    node(custom, A + "rect", l="0", t="0", r="r", b="b")
    path_list = node(custom, A + "pathLst")
    path = node(path_list, A + "path", w=str(width), h=str(height),
                stroke=str(int(stroke)), fill=fill_mode)
    for command, points in transformed:
        local = [(px(x - left), px(y - top)) for x, y in points]
        if command == "M":
            item = node(path, A + "moveTo")
            node(item, A + "pt", x=local[0][0], y=local[0][1])
        elif command == "L":
            item = node(path, A + "lnTo")
            node(item, A + "pt", x=local[0][0], y=local[0][1])
        elif command == "C":
            item = node(path, A + "cubicBezTo")
            for x, y in local:
                node(item, A + "pt", x=x, y=y)
        elif command == "Z":
            node(path, A + "close")


def replace_arrow_geometry(shape, commands, translation):
    props = shape.find(P + "spPr")
    write_custom_geometry(props, commands, translation, fill_mode="none", stroke=True)
    outline = props.find(A + "ln")
    for tag in ("headEnd", "tailEnd"):
        marker = outline.find(A + tag)
        if marker is not None:
            outline.remove(marker)


def add_arrowhead(slide, shaft, commands, translation, color="000000"):
    shape = xml.Element(P + "sp")
    native = node(shape, P + "nvSpPr")
    slide.identity(native, "Scientific Method arrowhead")
    node(native, P + "cNvSpPr")
    node(native, P + "nvPr")
    props = node(shape, P + "spPr")
    write_custom_geometry(props, commands, translation, fill_mode="norm", stroke=False)
    node(node(props, A + "solidFill"), A + "srgbClr", val=color)
    node(node(props, A + "ln", w=0), A + "noFill")
    parent = shaft.getparent()
    parent.insert(parent.index(shaft) + 1, shape)
    slide.ids[slide.last_id] = shape


def scientific_method(slide, index):
    ids = SCIENTIFIC_METHOD_ARROW_IDS[index]
    arrows = source_arrow_paths(index)
    assert len(ids) == len(arrows)
    for identity, (commands, translation, head, head_translation) in zip(ids, arrows):
        shaft = slide.ids[identity]
        replace_arrow_geometry(shaft, commands, translation)
        add_arrowhead(slide, shaft, head, head_translation)

    label_id = 485 if index == 77 else 504
    label = slide.ids[label_id]
    if index == 78:
        transform = label.find(f"{P}spPr/{A}xfrm")
        extent = transform.find(A + "ext")
        extent.set("cx", str(int(extent.get("cx")) - px(60)))
    lines = ["Conjectured Set of", "Final States"] if index == 77 else ["Conjectured", "Set of Final States"]
    stext(label, lines, size=35, leading=44, font="Source Sans 3", color="000000",
          align="ctr" if index == 77 else "r", vertical="t", margin=7.0866)
    body = label.find(P + "txBody")
    body_props = body.find(A + "bodyPr")
    body_props.set("wrap", "none")
    body_props.set("tIns", str(45000 + px(32)))
    body_props.set("bIns", "45000")

    output_id = 486 if index == 77 else 505
    output_label = slide.ids[output_id]
    output_body = output_label.find(P + "txBody")
    output_props = output_body.find(A + "bodyPr")
    output_props.set("wrap", "none")
    output_props.set("lIns", "0")
    output_props.set("rIns", "0")
    for text_props in output_body.iter():
        if text_props.tag in (A + "rPr", A + "endParaRPr", A + "defRPr"):
            text_props.set("sz", "3200")
            for tag in ("latin", "ea", "cs"):
                font = text_props.find(A + tag)
                if font is None and tag == "latin":
                    font = node(text_props, A + tag)
                if font is not None:
                    font.set("typeface", "Arial")


def control_flow_graph(slide, index):
    ids = CFG_ARROW_IDS[index]
    arrows = source_cfg_arrow_paths(index)
    assert len(ids) == len(arrows)
    for identity, (commands, translation, head, head_translation) in zip(ids, arrows):
        shaft = slide.ids[identity]
        replace_arrow_geometry(shaft, commands, translation)
        add_arrowhead(slide, shaft, head, head_translation, color="DD5F36")

    # Google can wrap these short words inside the narrow source boxes. Keep
    # each branch label on one line while retaining an editable text object.
    for identity in CFG_BRANCH_LABEL_IDS[index]:
        body = slide.ids[identity].find(P + "txBody")
        body_props = body.find(A + "bodyPr")
        body_props.set("wrap", "none")
        body_props.set("lIns", "0")
        body_props.set("rIns", "0")

    if index == 99:
        compact_google_label(slide.ids[410], size=32)
        compact_google_label(slide.ids[411], size=32)
        transform = slide.ids[411].find(f"{P}spPr/{A}xfrm")
        transform.find(A + "off").set("x", str(px(936)))
        transform.find(A + "ext").set("cx", str(px(76)))
    elif index == 100:
        for identity, lines in ((447, ["CFG w/", "BBs"]),
                                (449, ["CFG w/o", "BBs"])):
            label = slide.ids[identity]
            stext(label, lines, size=20, leading=26, font="Arial",
                  color="FFFFFF", align="ctr", vertical="ctr")
            parent = label.getparent()
            parent.remove(label)
            parent.append(label)
    elif index == 102:
        # Google's font metrics place the final brace a few points below the
        # source frame. Extend the editable code frame slightly to contain it.
        extent = slide.ids[720].find(f"{P}spPr/{A}xfrm/{A}ext")
        extent.set("cy", str(int(extent.get("cy")) + px(8)))


def compact_google_label(shape, *, size, font="Arial"):
    body = shape.find(P + "txBody")
    body_props = body.find(A + "bodyPr")
    body_props.set("wrap", "none")
    body_props.set("lIns", "0")
    body_props.set("rIns", "0")
    for tag in ("noAutofit", "normAutofit", "spAutoFit"):
        current = body_props.find(A + tag)
        if current is not None:
            body_props.remove(current)
    node(body_props, A + "noAutofit")
    for tag in ("rPr", "endParaRPr", "defRPr"):
        for props in body.iter(A + tag):
            props.set("sz", str(size * 100))
            for family in ("latin", "ea", "cs"):
                element = props.find(A + family)
                if element is not None:
                    element.set("typeface", font)
                elif family == "latin":
                    node(props, A + family, typeface=font)


def subset_relations(slide, index):
    for identity, (x, y, width, height) in SUBSET_RELATION_POSITIONS[index].items():
        shape = slide.ids[identity]
        transform = shape.find(f"{P}spPr/{A}xfrm")
        off, extent = transform.find(A + "off"), transform.find(A + "ext")
        off.set("x", str(px(x)))
        off.set("y", str(px(y)))
        extent.set("cx", str(px(width)))
        extent.set("cy", str(px(height)))
        stext(shape, ["⊆"], size=40, leading=44, font="Arial",
              align="ctr", vertical="ctr")


def fit_cfg_label(slide, index, *, size=24):
    """Keep CFG editable, remove side insets, and set the measured font size."""
    shape = slide.ids[CFG_FIT_LABEL_IDS[index]]
    body = shape.find(P + "txBody")
    body_props = body.find(A + "bodyPr")
    body_props.set("lIns", "0")
    body_props.set("rIns", "0")
    body_props.set("wrap", "none")
    for tag in (A + "rPr", A + "endParaRPr", A + "defRPr"):
        for props in body.iter(tag):
            props.set("sz", str(size * 100))


def fit_program_text_label(slide, index):
    """Prevent the source's condensed program caption from wrapping in Google."""
    shape = slide.ids[PROGRAM_TEXT_LABEL_IDS[index]]
    body_props = shape.find(f"{P}txBody/{A}bodyPr")
    body_props.set("lIns", "0")
    body_props.set("rIns", "0")
    body_props.set("wrap", "none")


def subset_archive(source, changes, paths, indices):
    presentation_path = "ppt/presentation.xml"
    relations_path = relpath(presentation_path)
    presentation = xml.fromstring(source.read(presentation_path))
    relations = xml.fromstring(source.read(relations_path))
    retained = {paths[i - 1] for i in indices}
    used_ids = {rel.get("Id") for rel in relations
                if normpath(join("ppt", rel.get("Target"))) in retained}
    for slide in list(presentation.find(P + "sldIdLst")):
        if slide.get(R + "id") not in used_ids:
            slide.getparent().remove(slide)
    for rel in list(relations):
        if rel.get("Type").endswith("/slide") and rel.get("Id") not in used_ids:
            relations.remove(rel)
    changes[presentation_path] = serialize(presentation)
    changes[relations_path] = serialize(relations)

    existing = set(source.namelist()) | set(changes)
    selected = {"[Content_Types].xml", "_rels/.rels"}
    pending = [("", "_rels/.rels")]
    while pending:
        part, link_file = pending.pop()
        data = changes[link_file] if link_file in changes else source.read(link_file)
        for rel in xml.fromstring(data):
            if rel.get("TargetMode") == "External":
                continue
            target = rel.get("Target")
            target = target.lstrip("/") if target.startswith("/") else normpath(join(dirname(part), target))
            assert target in existing, (part, target)
            if target in selected:
                continue
            selected.add(target)
            links = relpath(target)
            if links in existing:
                selected.add(links)
                pending.append((target, links))
    types = xml.fromstring(source.read("[Content_Types].xml"))
    for entry in list(types):
        if entry.get("PartName") and entry.get("PartName").lstrip("/") not in selected:
            types.remove(entry)
    changes["[Content_Types].xml"] = serialize(types)
    return selected


def build(round_number, output):
    indices = SELECTION[round_number]
    with ZipFile(BASE) as source, pikepdf.open(REFERENCE) as reference:
        paths = slide_paths(source)
        changes = {}
        for index in indices:
            path = paths[index - 1]
            slide = Slide(xml.fromstring(source.read(path)))
            old = serialize(slide.root)
            pictures = {}
            if round_number in (5, 7):
                fix_media(slide, reference.pages[index - 1], index, pictures, round_number)
            if round_number in (6, 7):
                fix_structure(slide, index, round_number)
            if round_number == 8 and index in SCIENTIFIC_METHOD_ARROW_IDS:
                scientific_method(slide, index)
            if round_number in (9, 11) and index in CFG_ARROW_IDS:
                control_flow_graph(slide, index)
            if round_number == 10 and index in SUBSET_RELATION_POSITIONS:
                subset_relations(slide, index)
            if round_number in (10, 11) and index in CFG_FIT_LABEL_IDS:
                fit_cfg_label(slide, index, size=24 if index == 154 else 46)
            if round_number == 11 and index in PROGRAM_TEXT_LABEL_IDS:
                fit_program_text_label(slide, index)
            new = serialize(slide.root)
            if new != old:
                changes[path] = new
            if pictures:
                rel_file = relpath(path)
                rels = xml.fromstring(source.read(rel_file))
                for filename, data in pictures.items():
                    asset = f"ppt/media/{filename}"
                    assert asset not in source.namelist()
                    changes[asset] = data
                    node(rels, PKG + "Relationship", Id=filename.removeprefix("cs408-").removesuffix(".png"),
                         Type=REL_IMAGE, Target=f"../media/{filename}")
                changes[rel_file] = serialize(rels)
        members = subset_archive(source, changes, paths, indices)
        with ZipFile(output, "x", compression=ZIP_DEFLATED) as pilot:
            for member in sorted(members):
                pilot.writestr(member, changes[member] if member in changes else source.read(member))
    with ZipFile(output) as pilot:
        assert not pilot.testzip()
        assert slide_paths(pilot) == [paths[i - 1] for i in indices]
    print(f"Round {round_number} combined slide order: {', '.join(map(str, indices))}")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("round", type=int, choices=SELECTION)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    build(args.round, args.output or PILOT / f"cs408-conversion-pilot-round{args.round}.pptx")
