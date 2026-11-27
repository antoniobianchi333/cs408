#!/usr/bin/env python3
"""Render contact sheets for converted slides not matched to a reference PDF.

This is a visual triage aid for audit_batch_source_alignment.py. Unmatched
slides are not automatically obsolete: inspect their source/build metadata
before excluding them from a final batch.

Example:
  python3 out/combined/render_unmatched_contact_sheets.py \
    --pdf out/.build/batch-01/local-render/02-408st-fault-error-failure.pdf \
    --slide-audit out/.build/batch-01/02-fault-error-slide-audit.csv \
    --outdir out/.build/batch-01/unmatched-review \
    --prefix fault-error

Requires the system `pdftoppm` utility and Python Pillow; installs no packages.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def page_number(path: Path) -> int:
    match = re.search(r"-(\d+)\.png$", path.name)
    if not match:
        raise ValueError(f"unexpected pdftoppm page filename: {path.name}")
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--slide-audit", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--pages-per-sheet", type=int, default=12)
    parser.add_argument("--thumb-width", type=int, default=320)
    args = parser.parse_args()

    renderer = shutil.which("pdftoppm")
    if not renderer:
        raise RuntimeError("pdftoppm is required; install Poppler utilities")
    args.outdir.mkdir(parents=True, exist_ok=True)
    render_prefix = args.outdir / f"{args.prefix}-page"
    subprocess.run(
        [renderer, "-png", "-scale-to", str(args.thumb_width),
         str(args.pdf), str(render_prefix)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    rendered = {
        page_number(path): path
        for path in args.outdir.glob(f"{args.prefix}-page-*.png")
    }

    with args.slide_audit.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    unmatched = [
        row for row in rows
        if row["chosen_by_ordered_alignment"].strip().lower() == "false"
    ]
    if not unmatched:
        print("No unmatched converted slides.")
        return 0

    columns = 3
    cell_w = args.thumb_width + 24
    cell_h = int(args.thumb_width * 0.82) + 62
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    font = (
        ImageFont.truetype(str(font_path), 11)
        if font_path.exists()
        else ImageFont.load_default()
    )
    for start in range(0, len(unmatched), args.pages_per_sheet):
        group = unmatched[start : start + args.pages_per_sheet]
        row_count = (len(group) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * cell_w, row_count * cell_h), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, record in enumerate(group):
            slide_no = int(record["converted_pptx_slide"])
            reference = record["best_reference_pdf_page"]
            score = record["f1_similarity"]
            image_path = rendered.get(slide_no)
            if image_path is None:
                raise FileNotFoundError(
                    f"render for unmatched slide {slide_no} was not produced"
                )
            image = Image.open(image_path).convert("RGB")
            image.thumbnail((args.thumb_width, cell_h - 54))
            x = (offset % columns) * cell_w + 8
            y = (offset // columns) * cell_h
            draw.text(
                (x, y + 3),
                f"Candidate slide {slide_no} | best PDF page {reference} | F1 {score}",
                fill="black",
                font=font,
            )
            sheet.paste(image, (x, y + 22))
            excerpt = record.get("slide_excerpt", "").replace("\n", " ")[:88]
            draw.text((x, y + cell_h - 29), excerpt, fill="#333333", font=font)
        sheet_no = start // args.pages_per_sheet + 1
        output = args.outdir / f"{args.prefix}-unmatched-{sheet_no:02d}.png"
        sheet.save(output, optimize=True)
        print(output)

    print(
        f"Rendered {len(unmatched)} unmatched slides into "
        f"{(len(unmatched) + args.pages_per_sheet - 1) // args.pages_per_sheet} "
        "contact sheets. Inspect source/build metadata before excluding any slide."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
