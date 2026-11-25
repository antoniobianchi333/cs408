"""Rebuild the four older delta-debugging supplement pages as editable text.

Uses only the existing Round 4 PPTX package and the locally available lxml
helpers. No presentation-conversion package is installed or required.
"""

from csv import DictWriter
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from rebuild_round2 import A, P, R, Slide, fill, node, px, stext, xml
from rebuild_round2 import serialize


HERE = Path(__file__).resolve().parent
BASE = HERE / "cs408-editable-part-01-round4.pptx"
OUTPUT = HERE / "cs408-tcm-supplement-round12-rev2.pptx"
PAGE_MAP = HERE / "cs408-tcm-supplement-round12-rev2-map.csv"

INK = "17212C"
BLUE = "168BC2"
ORANGE = "DE562D"
GREEN = "30943B"
RED = "C94646"
FONT = "Source Sans Pro"


def rich_text(slide, name, rect, runs, *, size=28, align="l", bold=False,
              italic=False, vertical="ctr"):
    """Add a native editable text box with independently colored text runs."""
    shape = slide.shape(name, rect, text_box=True)
    body = node(shape, P + "txBody")
    props = node(body, A + "bodyPr", wrap="none", anchor=vertical,
                 lIns=0, rIns=0, tIns=0, bIns=0)
    node(props, A + "noAutofit")
    node(body, A + "lstStyle")
    para = node(body, A + "p")
    node(para, A + "pPr", algn=align)
    for run_spec in runs:
        value, color, run_bold, run_italic, *extra = run_spec
        baseline = extra[0] if extra else None
        run_size = extra[1] if len(extra) > 1 else size
        run = node(para, A + "r")
        attributes = {"lang": "en-US", "sz": round(run_size * 100),
                      "b": int(bold or run_bold), "i": int(italic or run_italic)}
        if baseline is not None:
            attributes["baseline"] = baseline
        character = node(run, A + "rPr", **attributes)
        fill(character, color)
        node(character, A + "latin", typeface=FONT)
        node(run, A + "t").text = value
    node(para, A + "endParaRPr", lang="en-US", sz=round(size * 100))
    return shape


def rich_lines(slide, name, rect, lines, *, size=28, align="l", vertical="ctr",
               leading=None):
    """Add editable mixed-style lines, including real DrawingML subscripts."""
    shape = slide.shape(name, rect, text_box=True)
    body = node(shape, P + "txBody")
    props = node(body, A + "bodyPr", wrap="none", anchor=vertical,
                 lIns=0, rIns=0, tIns=0, bIns=0)
    node(props, A + "noAutofit")
    node(body, A + "lstStyle")
    for runs in lines:
        para = node(body, A + "p")
        ppr = node(para, A + "pPr", algn=align)
        if leading is not None:
            node(node(ppr, A + "lnSpc"), A + "spcPts", val=round(leading * 100))
        for run_spec in runs:
            value, color, run_bold, run_italic, *extra = run_spec
            baseline = extra[0] if extra else None
            run_size = extra[1] if len(extra) > 1 else size
            run = node(para, A + "r")
            attributes = {"lang": "en-US", "sz": round(run_size * 100),
                          "b": int(run_bold), "i": int(run_italic)}
            if baseline is not None:
                attributes["baseline"] = baseline
            character = node(run, A + "rPr", **attributes)
            fill(character, color)
            node(character, A + "latin", typeface=FONT)
            node(run, A + "t").text = value
        node(para, A + "endParaRPr", lang="en-US", sz=round(size * 100))
    return shape


def sub(text, color=BLUE, *, size=19):
    """DrawingML subscript run, avoiding unsupported Unicode subscript glyphs."""
    return (text, color, False, False, "-25000", size)


def title(slide, text):
    slide.text("Editable title", (45, 29, 934, 66), [text], font=FONT,
               size=49, color=INK, align="ctr")
    slide.shape("Title underline", (326, 105, 372, 3), color=BLUE)


def bullet(slide, y, lines, *, size=27, x=89, width=860, leading=35):
    slide.shape("Native bullet dot", (54, y + 11, 9, 9), primitive="ellipse",
                color=INK)
    slide.text("Editable bullet text", (x, y, width, 75), lines, font=FONT,
               size=size, color=INK, leading=leading, vertical="t")


def add_slide_contents(slide, index):
    tree = slide.tree
    for child in list(tree)[2:]:
        tree.remove(child)
    slide.root.set("showMasterSp", "0")
    slide.root.set("showMasterPhAnim", "0")
    c_sld = slide.root.find(P + "cSld")
    background = c_sld.find(P + "bg")
    if background is not None:
        c_sld.remove(background)
    background = xml.Element(P + "bg")
    bg_props = node(background, P + "bgPr")
    solid = node(bg_props, A + "solidFill")
    node(solid, A + "srgbClr", val="FFFFFF")
    node(bg_props, A + "effectLst")
    c_sld.insert(0, background)

    if index == 1:
        title(slide, "Delta Debugging")
        bullet(slide, 171, ["Let T denote the set of all possible test inputs"])
        bullet(slide, 238, ["We can go from one input t₁ to another input t₂ by a",
                            "series of edits"])
        bullet(slide, 326, ["An edit δ is a mapping T → T which takes one input",
                            "and changes it to another input"])
        slide.shape("Example bullet", (54, 424, 9, 9), primitive="ellipse",
                    color=INK)
        rich_text(slide, "Example definition", (89, 407, 860, 45), [
            ("Example: ", INK, True, False),
            ("δ₀", BLUE, True, False),
            (' = insert ', INK, False, False),
            ('ME="priori', ORANGE, False, False),
            (" at input position 10", INK, False, False),
        ], size=27)
        rich_text(slide, "Input before edit", (122, 500, 832, 42), [
            ("t₁ = ", INK, False, False),
            ('<SELECT NAty" MULTIPLE SIZE=7>', BLUE, False, False),
        ], size=25)
        rich_text(slide, "Input after edit", (122, 558, 832, 42), [
            ("δ₀(t₁) = ", INK, False, False),
            ("<SELECT NA", BLUE, False, False),
            ('ME="priori', ORANGE, False, False),
            ('ty" MULTIPLE SIZE=7>', BLUE, False, False),
        ], size=25)

    elif index == 2:
        title(slide, "Delta Debugging")
        slide.shape("Edit decomposition bullet", (54, 186, 9, 9),
                    primitive="ellipse", color=INK)
        rich_lines(slide, "Edit decomposition text", (89, 164, 890, 76), [[
            ("An edit δ can be decomposed into a number of", INK, False, False)], [
            ("elementary edits δ₁, δ₂, …, δ", INK, False, False),
            sub("n", INK), (", where", INK, False, False),
        ]], size=27, leading=35, vertical="t")
        rich_lines(slide, "Composition equation", (70, 287, 925, 58), [[
            ("δ = δ₁ ∘ δ₂ ∘ … ∘ δ", BLUE, False, False), sub("n", BLUE),
            ("   and   (δ", BLUE, False, False), sub("i", BLUE),
            (" ∘ δ", BLUE, False, False), sub("j", BLUE),
            (")(r) = δ", BLUE, False, False), sub("j", BLUE),
            ("(δ", BLUE, False, False), sub("i", BLUE), ("(r))", BLUE, False, False),
        ]], size=27, align="ctr")
        bullet(slide, 389, ["Example: deleting a part of an input file can be",
                            "decomposed to deleting characters one by one",
                            "from the file"], size=26, leading=34)
        slide.shape("Sub-bullet dot", (94, 552, 7, 7), primitive="ellipse",
                    color=ORANGE)
        slide.text("Composition explanation", (120, 530, 817, 116), [
            "By composing the deletion of single characters, we can get a",
            "change that deletes part of the input file",
        ], font=FONT, size=25, color=ORANGE, leading=33, vertical="t")

    elif index == 3:
        title(slide, "Decomposing edits")
        rich_text(slide, "Insertion example", (82, 183, 864, 48), [
            ("Example: ", INK, True, False),
            ("δ′", BLUE, True, False),
            (' = insert ', INK, False, False),
            ('ME="priori', ORANGE, False, False),
            (" at input position 10", INK, False, False),
        ], size=27)
        slide.text("Edit decomposition", (100, 263, 824, 55),
                   ["δ′ = δ₁ ∘ δ₂ ∘ … ∘ δ₁₀"], font=FONT, size=30,
                   color=BLUE, align="ctr")
        slide.text("Edit step one", (116, 399, 797, 55),
                   ["δ₁ = insert M at position 10"], font=FONT, size=28,
                   color=INK)
        slide.text("Edit step two", (116, 468, 797, 55),
                   ["δ₂ = insert E at position 11"], font=FONT, size=28,
                   color=INK)
        slide.text("Remaining edit steps", (200, 550, 600, 55), ["…"],
                   font=FONT, size=34, color=BLUE, align="ctr")

    elif index == 4:
        title(slide, "Decomposing edits")
        slide.shape("Passing input bullet", (54, 162, 9, 9),
                    primitive="ellipse", color=INK)
        rich_text(slide, "Passing input", (89, 139, 860, 43), [
            ("We have an input without failure: t", INK, False, False),
            sub("P", INK, size=18),
        ], size=25)
        rich_text(slide, "Failing input", (89, 206, 860, 43), [
            ("We have an input with failure: ", INK, False, False),
            ("t", RED, True, False), sub("F", RED, size=18),
        ], size=25)
        rich_text(slide, "Full edit set", (89, 260, 875, 45), [
            ("We have a set of edits c", INK, False, False),
            sub("F", INK, size=18), (" = {", INK, False, False),
            ("δ₁, δ₂, …, δ", BLUE, False, False), sub("n", BLUE, size=18),
            ("} such that:", INK, False, False),
        ], size=25)
        rich_lines(slide, "Failing input equation", (153, 318, 718, 52), [[
            ("r", BLUE, False, False), sub("F", BLUE, size=21),
            (" = (δ₁ ∘ δ₂ ∘ … ∘ δ", BLUE, False, False), sub("n", BLUE, size=21),
            (")(t", BLUE, False, False), sub("P", BLUE, size=21), (")", BLUE, False, False),
        ]], size=29, align="ctr")
        rich_text(slide, "Subset candidate", (89, 390, 850, 44), [
            ("Each subset t of c", INK, False, False),
            sub("F", INK, size=18), (" produces a candidate ", INK, False, False),
            ("test case", BLUE, True, False),
        ], size=25)
        rich_lines(slide, "Failure preservation goal", (89, 465, 875, 106), [[
            ("Goal: ", BLUE, True, False),
            ("For a subset t, test whether applying its edits to t", INK, False, False),
            sub("P", INK, size=18),
        ], [
            ("produces the same failure as r", INK, False, False),
            sub("F", INK, size=18), (".", INK, False, False),
        ]], size=25, leading=34, vertical="t")
    else:
        raise ValueError(index)


def build():
    if OUTPUT.exists():
        OUTPUT.unlink()
    with ZipFile(BASE) as source:
        pres = xml.fromstring(source.read("ppt/presentation.xml"))
        rels_path = "ppt/_rels/presentation.xml.rels"
        rels = xml.fromstring(source.read(rels_path))
        rel_targets = {rel.get("Id"): rel.get("Target") for rel in rels}
        slide_list = pres.find(P + "sldIdLst")
        selected_ids = list(slide_list)[:4]
        selected_rids = {element.get(R + "id") for element in selected_ids}
        ordered_parts = [
            "ppt/" + rel_targets[element.get(R + "id")].removeprefix("../")
            for element in selected_ids
        ]
        selected_parts = set(ordered_parts)
        for element in list(slide_list)[4:]:
            slide_list.remove(element)
        for relationship in list(rels):
            if relationship.get("Type", "").endswith("/slide") and relationship.get("Id") not in selected_rids:
                rels.remove(relationship)

        content_types = xml.fromstring(source.read("[Content_Types].xml"))
        selected_overrides = {"/" + part for part in selected_parts}
        for override in list(content_types):
            if (override.tag.endswith("Override")
                    and override.get("PartName", "").startswith("/ppt/slides/")
                    and override.get("PartName") not in selected_overrides):
                content_types.remove(override)

        changes = {
            "ppt/presentation.xml": serialize(pres),
            rels_path: serialize(rels),
            "[Content_Types].xml": serialize(content_types),
        }
        for index, part in enumerate(ordered_parts, 1):
            document = xml.fromstring(source.read(part))
            slide = Slide(document)
            add_slide_contents(slide, index)
            changes[part] = serialize(document)
            slide_rel = part.replace("ppt/slides/", "ppt/slides/_rels/") + ".rels"
            if slide_rel in source.namelist():
                slide_rels = xml.fromstring(source.read(slide_rel))
                for relation in list(slide_rels):
                    if not relation.get("Type", "").endswith("/slideLayout"):
                        slide_rels.remove(relation)
                changes[slide_rel] = serialize(slide_rels)

        keep_rels = {
            part.replace("ppt/slides/", "ppt/slides/_rels/") + ".rels"
            for part in ordered_parts
        }
        with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED, compresslevel=4) as target:
            for name in source.namelist():
                if name.startswith("ppt/slides/") and name.endswith(".xml"):
                    if name not in ordered_parts and name not in keep_rels:
                        continue
                if name.startswith("ppt/slides/_rels/") and name.endswith(".xml.rels"):
                    if name not in keep_rels:
                        continue
                target.writestr(name, changes.pop(name, source.read(name)))
            for name, data in changes.items():
                target.writestr(name, data)

    with PAGE_MAP.open("w", newline="", encoding="utf-8") as stream:
        writer = DictWriter(stream, fieldnames=[
            "pilot_slide", "source_pdf", "source_pdf_page", "combined_slide",
            "source_status", "content", "reconstruction",
        ])
        writer.writeheader()
        contents = [
            "Input set, edits as transformations, and HTML insertion example",
            "Edit composition/decomposition and single-character deletion example",
            "Character-by-character insertion decomposition",
            "Passing/failing inputs, edit set, and failure-preserving subsets",
        ]
        for slide_number, page in enumerate(range(38, 42), 1):
            writer.writerow({
                "pilot_slide": slide_number,
                "source_pdf": "slides/pdfs/20-408st-TestCase-Minimization.pdf",
                "source_pdf_page": page,
                "combined_slide": 802 + page,
                "source_status": "older PDF only; original Keynote unavailable",
                "content": contents[slide_number - 1],
                "reconstruction": "native editable text and equation text; no slide image",
            })
    print(f"Created {OUTPUT} and {PAGE_MAP}")


if __name__ == "__main__":
    build()
