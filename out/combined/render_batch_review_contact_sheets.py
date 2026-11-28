#!/usr/bin/env python3
"""Render mapped source/output comparison sheets for a final batch PDF.

The map must contain ``output_slide``, ``row_type``, ``source_filename``,
``source_pdf_page``, and ``source_build_state`` columns. Pass source PDFs as
``--source 'source.key=reference.pdf'``. Sheets and page renders belong in
ignored ``out/.build``; this script does not alter slide or source files.

Build states are compared to the completed reference page as a content and
layout aid. Earlier states are expected to omit later revealed material.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_sources(values: list[str]) -> dict[str, Path]:
    sources: dict[str, Path] = {}
    for value in values:
        name, sep, raw_path = value.partition("=")
        if not sep or not name or not raw_path:
            raise ValueError(f"source must be SOURCE_FILENAME=PDF_PATH: {value}")
        sources[name] = Path(raw_path).resolve()
    return sources


def render_pdf(renderer: str, pdf: Path, directory: Path, prefix: str, width: int) -> dict[int, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / prefix
    subprocess.run(
        [renderer, "-jpeg", "-scale-to", str(width), "-jpegopt", "quality=88", str(pdf), str(target)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    pages: dict[int, Path] = {}
    for path in directory.glob(f"{prefix}-*.jpg"):
        match = re.search(r"-(\d+)\.jpg$", path.name)
        if match:
            pages[int(match.group(1))] = path
    return pages


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def fit_page(path: Path, width: int, height: int) -> Image.Image:
    with Image.open(path) as source:
        image = source.convert("RGB")
    image.thumbnail((width, height), Image.LANCZOS)
    canvas = Image.new("RGB", (width, height), "white")
    canvas.paste(image, ((width - image.width) // 2, (height - image.height) // 2))
    return canvas


def wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width_chars: int,
            font: ImageFont.ImageFont, fill: str, line_spacing: int = 3) -> int:
    y = xy[1]
    for line in textwrap.wrap(text, width=width_chars) or [""]:
        draw.text((xy[0], y), line, font=font, fill=fill)
        y += font.size + line_spacing if hasattr(font, "size") else 15
    return y


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--candidate-pdf", type=Path, required=True)
    parser.add_argument("--source", action="append", default=[], metavar="KEY=PDF")
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--prefix", default="batch-review")
    parser.add_argument("--pages-per-sheet", type=int, default=8)
    parser.add_argument("--thumb-width", type=int, default=480)
    args = parser.parse_args()

    renderer = shutil.which("pdftoppm")
    if not renderer:
        raise RuntimeError("pdftoppm is required; install Poppler utilities")
    sources = parse_sources(args.source)
    args.outdir.mkdir(parents=True, exist_ok=True)
    renders = args.outdir / "page-renders"
    candidate_pages = render_pdf(
        renderer, args.candidate_pdf.resolve(), renders, "candidate", args.thumb_width
    )
    source_pages: dict[str, dict[int, Path]] = {}
    for number, (key, pdf) in enumerate(sorted(sources.items()), start=1):
        source_pages[key] = render_pdf(
            renderer, pdf, renders, f"source-{number:02d}", args.thumb_width
        )

    with args.map.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    required = {"output_slide", "row_type", "source_filename", "source_pdf_page", "source_build_state"}
    missing = required - set(rows[0] if rows else [])
    if missing:
        raise ValueError(f"map is missing columns: {', '.join(sorted(missing))}")
    if len(rows) != len(candidate_pages):
        raise ValueError(f"map has {len(rows)} rows but candidate PDF rendered {len(candidate_pages)} pages")

    thumb_h = round(args.thumb_width * 0.75)
    panel_w = args.thumb_width + 20
    pair_w = panel_w * 2 + 20
    card_h = thumb_h + 86
    columns = 2
    font = load_font(13)
    small = load_font(12)
    pages_per_sheet = max(1, args.pages_per_sheet)

    for start in range(0, len(rows), pages_per_sheet):
        group = rows[start : start + pages_per_sheet]
        row_count = (len(group) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * pair_w, row_count * card_h), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, row in enumerate(group):
            output_no = int(row["output_slide"])
            row_type = row["row_type"]
            source_name = row["source_filename"]
            source_page = row["source_pdf_page"].strip()
            state = row["source_build_state"].strip()
            x = (offset % columns) * pair_w
            y = (offset // columns) * card_h
            label = f"OUT {output_no:03d} | {row_type}"
            if source_page:
                label += f" | {source_name} p.{source_page}"
            if state:
                label += f" | state {state}"
            draw.text((x + 8, y + 4), label[:130], font=font, fill="black")

            source_x = x + 8
            output_x = x + panel_w + 16
            cap_y = y + 26
            draw.text((source_x, cap_y), "SOURCE PDF", font=small, fill="#333333")
            draw.text((output_x, cap_y), "CANDIDATE OUTPUT", font=small, fill="#333333")
            image_y = cap_y + 20

            if row_type == "source_deck_divider":
                expected = (
                    "Expected editable divider: solid #FFF2CC background; exact source filename "
                    "centered in 24 pt bold Arial; following topic centered in 28 pt regular Arial."
                )
                draw.rectangle((source_x, image_y, source_x + args.thumb_width, image_y + thumb_h), fill="#FFF2CC")
                wrapped(draw, expected, (source_x + 15, image_y + 35), 52, small, "#333333")
            elif source_page:
                source_path = sources.get(source_name)
                page_map = source_pages.get(source_name, {})
                source_image = page_map.get(int(source_page)) if source_path else None
                if source_image:
                    sheet.paste(fit_page(source_image, args.thumb_width, thumb_h), (source_x, image_y))
                else:
                    draw.rectangle((source_x, image_y, source_x + args.thumb_width, image_y + thumb_h), fill="#fff2cc")
                    wrapped(draw, f"Exact PDF unavailable for {source_name}, page {source_page}.",
                            (source_x + 15, image_y + 35), 52, small, "#333333")
            else:
                draw.rectangle((source_x, image_y, source_x + args.thumb_width, image_y + thumb_h), fill="#eeeeee")
                draw.text((source_x + 20, image_y + 35), "Generated slide; inspect against project rules.", font=small, fill="#333333")

            output_image = candidate_pages.get(output_no)
            if output_image is None:
                raise FileNotFoundError(f"candidate PDF page {output_no} was not rendered")
            sheet.paste(fit_page(output_image, args.thumb_width, thumb_h), (output_x, image_y))
            draw.rectangle((source_x, image_y, source_x + args.thumb_width, image_y + thumb_h), outline="#777777", width=1)
            draw.rectangle((output_x, image_y, output_x + args.thumb_width, image_y + thumb_h), outline="#777777", width=1)

        sheet_no = start // pages_per_sheet + 1
        out_path = args.outdir / f"{args.prefix}-{sheet_no:03d}.jpg"
        sheet.save(out_path, quality=90, optimize=True)

    count = len(rows)
    sheets = (count + pages_per_sheet - 1) // pages_per_sheet
    print(f"Rendered {count} mapped candidate pages into {sheets} source/output contact sheets in {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
