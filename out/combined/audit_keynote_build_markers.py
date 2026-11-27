#!/usr/bin/env python3
"""Locate Keynote slide records with build/transition effects and map candidates.

The IWA scan is a locator, not a full Keynote build-order decoder. It finds
animation-effect markers, then uses text overlap to suggest the corresponding
reference PDF page and LibreOffice-converted PPTX slide. Inspect the source
record and visual sequence before expanding or excluding any state.

Example:
  python3 out/combined/audit_keynote_build_markers.py \
    --key slides/02-408st-fault-error-failure.key \
    --pptx out/.build/batch-01/source-pptx/02-408st-fault-error-failure.pptx \
    --pdf slides/f26-pdfs/02-408st-fault-error-failure.pdf \
    --page-map out/.build/batch-01/02-fault-error-page-candidates.csv \
    --output out/.build/batch-01/02-fault-error-build-markers.csv

Only Python's standard library and the existing local audit helpers are used.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import zipfile
from pathlib import Path

from audit_batch_source_alignment import similarity
from audit_fall_text_overlap import first_lines, ordered_pptx_text, pdf_pages, tokens


EFFECT_RE = re.compile(rb"apple:[A-Za-z0-9_-]+")
PRINTABLE_RE = re.compile(rb"[ -~]{4,}")


def record_text(data: bytes) -> str:
    return " ".join(part.decode("ascii", "replace") for part in PRINTABLE_RE.findall(data))


def rank_matches(text: str, candidates: list[str], limit: int = 3) -> list[tuple[int, float]]:
    source_tokens = tokens(text)
    ranked = []
    for index, candidate in enumerate(candidates, start=1):
        score = similarity(text, candidate)[0]
        if source_tokens:
            ranked.append((index, score))
    return sorted(ranked, key=lambda item: (-item[1], item[0]))[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--pptx", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--page-map", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    pptx_texts = ordered_pptx_text(args.pptx)
    pdf_texts = pdf_pages(args.pdf)
    mapped_pages: dict[int, list[int]] = {}
    if args.page_map:
        with args.page_map.open(newline="", encoding="utf-8") as source:
            for row in csv.DictReader(source):
                candidate = int(row["converted_pptx_slide"])
                page = int(row["reference_pdf_page"])
                mapped_pages.setdefault(candidate, []).append(page)

    with zipfile.ZipFile(args.key) as package:
        names = sorted(
            name for name in package.namelist()
            if name.startswith("Index/Slide-") and name.endswith(".iwa")
        )
        records = []
        for name in names:
            data = package.read(name)
            markers = sorted(set(marker.decode("ascii") for marker in EFFECT_RE.findall(data)))
            if not markers:
                continue
            text = record_text(data)
            pptx_ranks = rank_matches(text, pptx_texts)
            pdf_ranks = rank_matches(text, pdf_texts)
            best_pptx, pptx_score = pptx_ranks[0] if pptx_ranks else (0, 0.0)
            best_pdf, pdf_score = pdf_ranks[0] if pdf_ranks else (0, 0.0)
            directly_mapped = ";".join(map(str, mapped_pages.get(best_pptx, [])))
            records.append(
                {
                    "keynote_iwa_record": name,
                    "effect_markers": ";".join(markers),
                    "mapped_reference_pdf_pages": directly_mapped,
                    "candidate_pptx_slide": best_pptx,
                    "pptx_text_f1": f"{pptx_score:.4f}",
                    "candidate_pdf_page": best_pdf,
                    "pdf_text_f1": f"{pdf_score:.4f}",
                    "pptx_runner_up_slides": ";".join(
                        f"{slide}:{score:.3f}" for slide, score in pptx_ranks[1:]
                    ),
                    "text_excerpt": first_lines(text, 2, 220),
                    "review_status": "Candidate locator only; verify source order/build and visual state",
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=[
                "keynote_iwa_record",
                "effect_markers",
                "mapped_reference_pdf_pages",
                "candidate_pptx_slide",
                "pptx_text_f1",
                "candidate_pdf_page",
                "pdf_text_f1",
                "pptx_runner_up_slides",
                "text_excerpt",
                "review_status",
            ],
        )
        writer.writeheader()
        writer.writerows(records)

    with zipfile.ZipFile(args.pptx) as package:
        slide_xml = [
            name for name in package.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]
        timing_slides = [
            name for name in slide_xml if b"<p:timing" in package.read(name)
        ]
    print(f"Found {len(records)} Keynote slide records with effect markers.")
    print(f"Converted PPTX: {len(slide_xml)} slides, {len(timing_slides)} with p:timing.")
    print(f"Effect-marker audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
