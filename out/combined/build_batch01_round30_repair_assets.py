#!/usr/bin/env python3
"""Build source-based picture assets for Batch 1's Round 30 native repairs.

The page-18 output composes only its two source pictures: the full-slide
decorative Ariane 5 photograph and the cropped report screenshot. The page
title and later headline remain editable Google Slides text. The page-24
output is a crop of that slide's source picture only; its editable caption is
not included.

All generated files belong under ignored ``out/.build``. No source deck or PDF
is modified.
"""

from __future__ import annotations

import argparse
import io
import subprocess
import tempfile
import zipfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
INTRO_PDF = ROOT / "slides/f26-pdfs/01-408st-introduction.pdf"
FAULT_PDF = ROOT / "slides/f26-pdfs/02-408st-fault-error-failure.pdf"
INTRO_KEY = ROOT / "slides/01-408st-introduction.key"
OUTPUT_DIR = ROOT / "out/.build/batch-01/round30-fullsize-review/repair-assets"


def first_pdf_image(pdf: Path, page: int, directory: Path) -> Path:
    prefix = directory / "source"
    subprocess.run(
        ["pdfimages", "-f", str(page), "-l", str(page), "-all", str(pdf), str(prefix)],
        check=True,
    )
    candidates = sorted(directory.glob("source-000.*"))
    if len(candidates) != 1:
        raise RuntimeError(f"expected one first image for {pdf.name} page {page}, got {candidates}")
    return candidates[0]


def page_png(pdf: Path, page: int, directory: Path) -> Path:
    prefix = directory / "page"
    subprocess.run(
        ["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-r", "72", "-singlefile", str(pdf), str(prefix)],
        check=True,
    )
    result = prefix.with_suffix(".png")
    if not result.exists():
        raise RuntimeError(f"missing rendered page: {result}")
    return result


def page18_composite(directory: Path) -> Path:
    with tempfile.TemporaryDirectory(dir=directory) as temp:
        temp_dir = Path(temp)
        photo_path = first_pdf_image(INTRO_PDF, 18, temp_dir)
        with Image.open(photo_path) as image:
            photo = image.convert("RGBA").resize((1187, 780), Image.LANCZOS)
        # These bounds reproduce the picture's source-deck fill-and-crop
        # transform: x=-152.99 pt, y=-5.75 pt, 1187.06 x 779.53 pt.
        canvas = photo.crop((153, 6, 1177, 774))
        with zipfile.ZipFile(INTRO_KEY) as package:
            article_bytes = package.read("Data/pasted-image-4629.tiff")
        with Image.open(io.BytesIO(article_bytes)) as image:
            article = image.convert("RGBA")
            crop_top = round(article.height * 0.202)
            article = article.crop((0, crop_top, article.width, article.height))
            article = article.resize((708, 254), Image.LANCZOS)
        canvas.alpha_composite(article, (316, 421))
        result = OUTPUT_DIR / "batch01-intro-page18-source-pictures.png"
        canvas.save(result)
        return result


def page24_picture(directory: Path) -> Path:
    with tempfile.TemporaryDirectory(dir=directory) as temp:
        source_page = page_png(FAULT_PDF, 24, Path(temp))
        with Image.open(source_page) as image:
            if image.size != (1024, 768):
                raise RuntimeError(f"expected 1024x768 source page, got {image.size}")
            # Reference page 24's photograph occupies this 432 x 408 pt region.
            crop = image.crop((0, 0, 432, 408))
        result = OUTPUT_DIR / "batch01-fault-error-page24-picture.png"
        crop.save(result)
        return result


def main() -> int:
    global OUTPUT_DIR
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    OUTPUT_DIR = args.output_dir.resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(page18_composite(OUTPUT_DIR))
    print(page24_picture(OUTPUT_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
