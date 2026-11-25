from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree as xml
from PIL import Image


HERE = Path(__file__).resolve().parent
PILOT = HERE if (HERE / "cs408-editable-pilot.pptx").is_file() else HERE.parent
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PKG = "{http://schemas.openxmlformats.org/package/2006/relationships}"
EMU = 12700
INK = "17212C"
BLUE = "168BC2"
PURPLE = "98469F"
ORANGE = "DE562D"


def node(parent, tag, **attrs):
    return xml.SubElement(parent, tag, {name: str(value) for name, value in attrs.items()})


def px(number):
    return round(number * EMU)


def geometry(parent, rect, **options):
    x, y, w, h = rect
    transform = node(parent, A + "xfrm", **options)
    node(transform, A + "off", x=px(x), y=px(y))
    node(transform, A + "ext", cx=px(w), cy=px(h))


def fill(parent, color):
    if color:
        node(node(parent, A + "solidFill"), A + "srgbClr", val=color)
    else:
        node(parent, A + "noFill")


def stext(shape, lines, *, size=32, leading=None, font="Arial", color=INK, bold=False,
          align="l", vertical="ctr", margin=0):
    previous = shape.find(P + "txBody")
    if previous is not None:
        shape.remove(previous)
    body = node(shape, P + "txBody")
    props = node(body, A + "bodyPr", wrap="none", anchor=vertical,
                 lIns=px(margin), rIns=px(margin), tIns=px(margin), bIns=px(margin))
    node(props, A + "noAutofit")
    node(body, A + "lstStyle")
    for line in lines:
        para = node(body, A + "p")
        style = node(para, A + "pPr", algn=align)
        if leading is not None:
            node(node(style, A + "lnSpc"), A + "spcPts", val=round(leading * 100))
        run = node(para, A + "r")
        character = node(run, A + "rPr", lang="en-US", sz=round(size * 100), b=int(bold))
        fill(character, color)
        node(character, A + "latin", typeface=font)
        node(run, A + "t").text = line
        node(para, A + "endParaRPr", lang="en-US", sz=round(size * 100))


class Slide:
    def __init__(self, document):
        self.root = document
        self.tree = document.find(f".//{P}spTree")
        self.ids = {
            int(obj.find(f"./*/{P}cNvPr").get("id")): obj for obj in self.tree.iter()
            if obj.find(f"./*/{P}cNvPr") is not None
        }
        self.last_id = max(int(el.get("id")) for el in document.iter(P + "cNvPr"))

    def identity(self, parent, name):
        self.last_id += 1
        node(parent, P + "cNvPr", id=self.last_id, name=name)

    def remove(self, *ids):
        for identity in ids:
            shape = self.ids[identity]
            shape.getparent().remove(shape)

    def move(self, identity, rect):
        shape = self.ids.get(identity)
        if shape is None:
            shape = next(obj for obj in self.tree.iter(P + "sp")
                         if obj.find(f"./{P}nvSpPr/{P}cNvPr").get("id") == str(identity))
        props = shape.find(P + "spPr")
        props.remove(props.find(A + "xfrm"))
        x, y, w, h = rect
        xf = xml.Element(A + "xfrm")
        node(xf, A + "off", x=px(x), y=px(y))
        node(xf, A + "ext", cx=px(w), cy=px(h))
        props.insert(0, xf)
        return shape

    def shape(self, name, rect, *, primitive="rect", color=None, stroke=None,
              width=1, arrow=False, options=None, text_box=False):
        shape = node(self.tree, P + "sp")
        native = node(shape, P + "nvSpPr")
        self.identity(native, name)
        node(native, P + "cNvSpPr", **({"txBox": 1} if text_box else {}))
        node(native, P + "nvPr")
        props = node(shape, P + "spPr")
        geometry(props, rect, **(options or {}))
        node(node(props, A + "prstGeom", prst=primitive), A + "avLst")
        fill(props, color)
        outline = node(props, A + "ln", w=px(width))
        fill(outline, stroke)
        if arrow:
            node(outline, A + "tailEnd", type="triangle", w="med", len="med")
        return shape

    def text(self, name, rect, lines, *, background=None, border=None, **text_style):
        shape = self.shape(name, rect, color=background, stroke=border, width=2,
                           text_box=background is None and border is None)
        stext(shape, lines, **text_style)

    def edge(self, *points, color=ORANGE, width=2.6, arrow=True):
        for i, ((x1, y1), (x2, y2)) in enumerate(zip(points, points[1:])):
            self.shape("Diagram edge", (min(x1, x2), min(y1, y2), abs(x1-x2), abs(y1-y2)),
                       primitive="line", stroke=color, width=width,
                       arrow=arrow and i == len(points) - 2,
                       options={"flipH": int(x1 > x2), "flipV": int(y1 > y2)})

    def graph_nodes(self, coordinates, *, exits=("B5", "B7")):
        for name, (x, y) in coordinates.items():
            shape = self.shape(f"Node {name}", (x, y, 71, 40), color="FFFFFF",
                               stroke=PURPLE, width=5 if name in exits else 3)
            stext(shape, [name], size=23, color="55515A", align="ctr")

    def picture(self, identity):
        picture = node(self.tree, P + "pic")
        native = node(picture, P + "nvPicPr")
        self.identity(native, "Course photo, cropped to the reference")
        node(native, P + "cNvPicPr")
        node(native, P + "nvPr")
        paint = node(picture, P + "blipFill")
        node(paint, A + "blip", **{R + "embed": identity})
        node(node(paint, A + "stretch"), A + "fillRect")
        props = node(picture, P + "spPr")
        geometry(props, (0, 0, 1024, 768))
        node(node(props, A + "prstGeom", prst="rect"), A + "avLst")
        self.tree.remove(picture)
        self.tree.insert(2, picture)


def cover(slide, archive, member, changes):
    relname = member.replace("/slides/", "/slides/_rels/") + ".rels"
    rels = xml.fromstring(archive.read(relname))
    old = next(rel for rel in rels if rel.get("Id") == "rId1")
    source = "ppt/" + old.get("Target").removeprefix("../")
    # The reference PDF paints the original 1800 × 1200 image at this matrix.
    # Crop the visible region before inserting it into the 4:3 slide.
    sx, sy, tx, ty = 1350.028, 900.028, -163.02, -65.991
    with Image.open(BytesIO(archive.read(source))) as im:
        ratio_x, ratio_y = im.width / sx, im.height / sy
        box = (-tx * ratio_x, (sy + ty - 767.99) * ratio_y,
               (1023.987 - tx) * ratio_x, (sy + ty) * ratio_y)
        crop = im.transform((1366, 1024), Image.EXTENT, box, Image.BICUBIC)
        data = BytesIO()
        crop.convert("RGB").save(data, format="JPEG", quality=96, subsampling=0)
    new_image = "ppt/media/cs408-round2-course-photo.jpg"
    changes[new_image] = data.getvalue()
    old.set("Target", "../media/cs408-round2-course-photo.jpg")
    changes[relname] = serialize(rels)
    contents = slide.root.find(P + "cSld")
    contents.remove(contents.find(P + "bg"))
    slide.picture("rId1")
    slide.move(163, (360, 568, 635, 177))
    stext(slide.ids[163], ["CS 408: SOFTWARE", "TESTING"], font="Bebas Neue",
          size=67, leading=66, color="FAF6EB", align="ctr")


def objectives(slide):
    slide.remove(241, 242, 245, 248, 251, 252)
    items = [
        ("01  Become better testers", ["Understand and apply software testing", "techniques and coverage criteria."]),
        ("02  Become better programmers", ["Anticipate defects and write tests", "that catch problems early."]),
        ("03  Become better engineers", ["Build software and test it as part", "of the same development process."]),
        ("04  Become better thinkers", ["Approach software problems logically", "and analyze them systematically."]),
    ]
    for i, (title, lines) in enumerate(items):
        x = 75 + 445 * (i % 2)
        y = 205 + 213 * (i // 2)
        slide.shape(f"Objective {i + 1} panel", (x, y, 419, 177), color="F1F7FB")
        slide.text(f"Objective {i + 1}", (x + 15, y + 14, 391, 45),
                   [title], size=25, bold=True, color="075581")
        slide.text(f"Objective {i + 1} description", (x + 15, y + 67, 391, 76),
                   lines, size=22, leading=32)


def coverage_cover(slide):
    slide.move(238, (570, 435, 430, 296))
    stext(slide.ids[238], ["COVERAGE CRITERIA", "+ CONTROL FLOW", "GRAPHS"],
          font="Bebas Neue", size=39, leading=55, color="FAF6EB", align="ctr")


def prime_paths(slide):
    slide.remove(*range(292, 310))
    coordinates = {"B1": (156, 247), "C1": (284, 247), "B2": (411, 155),
                   "B3": (411, 247), "B4": (539, 247), "C2": (667, 247), "B5": (794, 247)}
    for points in [
        [(117, 267), (156, 267)], [(227, 267), (284, 267)],
        [(319, 247), (349, 175), (411, 175)], [(355, 267), (411, 267)],
        [(482, 175), (528, 175), (575, 247)], [(482, 267), (539, 267)],
        [(610, 267), (667, 267)], [(738, 267), (794, 267)],
        [(702, 287), (702, 319), (319, 319), (319, 287)],
    ]:
        slide.edge(*points)
    slide.graph_nodes(coordinates)
    slide.text("Prime path observation", (675, 530, 322, 105),
               ["A simple path need not", "be a test path."], color="263743",
               background="F1F7FB", border=BLUE, size=23, align="ctr", bold=True)


def prime_coverage(slide):
    slide.remove(*range(346, 362), 363)
    coordinates = {"C1": (214, 226), "B2": (342, 226), "C3": (469, 226),
                   "B4": (574, 168), "B7": (727, 168), "C5": (574, 255), "B6": (739, 255)}
    for points in [
        [(163, 246), (214, 246)], [(285, 246), (342, 246)], [(413, 246), (469, 246)],
        [(248, 226), (326, 183), (402, 183), (501, 226)],
        [(539, 228), (574, 189)], [(540, 255), (574, 274)], [(645, 188), (727, 188)],
        [(616, 255), (673, 215), (728, 205)],
        [(645, 273), (690, 242), (739, 273)], [(772, 295), (707, 319), (616, 295)],
    ]:
        slide.edge(*points)
    slide.graph_nodes(coordinates)
    slide.move(362, (25, 377, 725, 369))


def happens_before(slide):
    slide.remove(736)
    stext(slide.move(742, (130, 392, 148, 38)), ["Thread 2"], size=25, align="ctr")
    stext(slide.move(746, (130, 198, 148, 38)), ["Thread 1"], size=25, align="ctr")
    slide.text("Happens-before definition", (367, 200, 221, 90),
               ["A happens before B", "in either case."], size=22, leading=30, bold=True)
    slide.text("Happens-before conditions", (367, 306, 221, 242),
               ["B follows A in", "the same thread.", "", "Across threads,",
                "a synchronization", "event C orders them:", "A then C then B."],
               size=19, leading=27, vertical="t")
    slide.text("Partial-order note", (407, 565, 180, 116),
               ["This defines a", "partial order on", "events.", "Lamport ’87"],
               size=20, leading=26, color=BLUE)


def randomized(slide):
    slide.remove(168, 169)
    slide.move(171, (62, 560, 550, 195))
    stext(slide.ids[171], ["Writing tests is fine", "if a little tedious", "lets automate it"],
          font="Roboto Condensed", size=43, leading=55, color="FAF6EB", align="ctr")
    stext(slide.ids[172], ["RANDOMIZED", "TESTING"], font="Bebas Neue", size=70,
          leading=73, color="FAF6EB", align="ctr")


def bug_reports(slide):
    slide.remove(168, 169)
    slide.move(171, (24, 571, 510, 176))
    stext(slide.ids[171], ["So many defects", "So little time to fix them", "What’s a dev to do?"],
          font="Roboto Condensed", size=39, leading=47, color="FAF6EB", align="ctr")
    stext(slide.ids[172], ["BUG REPORTS AND TRIAGE"], font="Bebas Neue", size=63,
          leading=67, color="FAF6EB", align="ctr")
    slide.move(173, (596, 702, 378, 43))
    stext(slide.ids[173], ["h/t to Westley Weimer"], font="Roboto Condensed",
          size=25, color="FAF6EB", align="r")


def data_structures(slide):
    slide.remove(1003, 1004, 1006, 1007, 1009, 1016, 1017)
    stext(slide.move(996, (75, 32, 874, 112)), ["Dealing with Data Structures"],
          size=49, align="ctr")
    stext(slide.move(1014, (51, 167, 345, 65)), ["Next Instruction ↦ Done"],
          size=26, align="ctr")
    slide.text("Concrete information label", (460, 204, 178, 87),
               ["CONCRETE", "INFORMATION"], font="Roboto Condensed",
               size=27, leading=34, color="FFFFFF", align="ctr", bold=True)
    slide.text("Symbolic information label", (681, 209, 322, 88),
               ["SYMBOLIC", "INFORMATION"], font="Roboto Condensed",
               size=27, leading=34, color="FFFFFF", align="ctr", bold=True)
    slide.text("Concrete state label", (459, 298, 176, 88), ["concrete", "state:"],
               size=27, leading=34, color="348A20", align="ctr")
    slide.text("Symbolic state label", (676, 298, 154, 88), ["symbolic", "state:"],
               size=26, leading=34, color="6C3481", align="ctr")
    slide.text("Path conditions label", (837, 298, 166, 88), ["path", "conditions:"],
               size=25, leading=34, color="6C3481", align="ctr")
    slide.text("SMT query and model", (165, 618, 730, 125),
               ["SMT query: a > 0 ∧ l ≠ null", "Satisfying model: [a ↦ 3, l ↦ ⟨6, null⟩]"],
               background="FBE5D8", border=ORANGE, font="Source Sans 3",
               size=31, leading=43, color="452211", margin=16)


def sign_lattice(slide):
    slide.remove(412, 447, 448, 449)
    coordinates = {"⊤": (644, 457), "NP": (480, 525), "NZ": (644, 525), "NN": (808, 525),
                   "−": (480, 606), "0": (644, 606), "+": (808, 606), "⊥": (644, 689)}
    edges = [
        ("⊤", "NP"), ("⊤", "NZ"), ("⊤", "NN"), ("NP", "−"), ("NP", "0"),
        ("NZ", "−"), ("NZ", "+"), ("NN", "0"), ("NN", "+"),
        ("−", "⊥"), ("0", "⊥"), ("+", "⊥"),
    ]
    for parent, child in edges:
        x, y = coordinates[parent]
        tx, ty = coordinates[child]
        slide.edge((x, y + 19), (tx, ty - 19), color="526477", width=1.8, arrow=False)
    for name, (x, y) in coordinates.items():
        slide.text(f"Sign lattice node {name}", (x - 33, y - 19, 66, 38), [name],
                   background="F1F7FB", border=BLUE, size=24, bold=True, align="ctr")
    slide.text("Less information label", (865, 448, 155, 32), ["Less information"], size=14, color="294B63")
    slide.text("More information label", (865, 676, 155, 32), ["More information"], size=14, color="294B63")


def path_sensitivity(slide):
    slide.remove(1625, 1630, 1631)
    slide.move(1627, (75, 231, 493, 321))
    slide.move(1628, (607, 255, 367, 250))
    slide.text("Path sensitivity explanation", (75, 598, 899, 135),
               ["The new input state does not track all path conditions at each",
                "program point, so the analysis overgeneralizes."],
               background="FBE5D8", border=ORANGE, size=25, leading=38, margin=18)


FIXES = {
    2: objectives, 3: coverage_cover, 4: prime_paths, 5: prime_coverage, 6: happens_before,
    7: randomized, 8: bug_reports, 12: data_structures, 13: sign_lattice, 14: path_sensitivity,
}


def serialize(element):
    return xml.tostring(element, xml_declaration=True, standalone=True, encoding="UTF-8")


def build(destination):
    with ZipFile(PILOT / "cs408-editable-pilot.pptx") as source:
        write_pilot(source, destination)


def write_pilot(source, destination):
    root = xml.fromstring(source.read("ppt/presentation.xml"))
    relationships = xml.fromstring(source.read("ppt/_rels/presentation.xml.rels"))
    targets = {rel.get("Id"): rel.get("Target") for rel in relationships}
    slides = ["ppt/" + targets[element.get(R + "id")] for element in root.find(P + "sldIdLst")]
    assert len(slides) == 16
    changes = {}
    for i in [1, *FIXES]:
        path = slides[i - 1]
        slide = Slide(xml.fromstring(source.read(path)))
        if i == 1:
            cover(slide, source, path, changes)
        else:
            FIXES[i](slide)
        changes[path] = serialize(slide.root)
    with ZipFile(destination, "x", compression=ZIP_DEFLATED, compresslevel=3) as output:
        for filename in source.namelist():
            output.writestr(filename, changes.pop(filename) if filename in changes else source.read(filename))
        for filename, data in changes.items():
            output.writestr(filename, data)
    print(f"Built {destination.name} with targeted repairs to {len(FIXES)+1} of {len(slides)} slides.")


if __name__ == "__main__":
    parser = ArgumentParser(description="Rebuild the second CS 408 editable pilot.")
    parser.add_argument("--output", type=Path, default=PILOT / "cs408-editable-pilot-round2.pptx")
    build(parser.parse_args().output)
