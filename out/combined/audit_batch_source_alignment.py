#!/usr/bin/env python3
"""Align a converted Keynote PPTX with its selected full-deck reference PDF.

The report proposes an ordered one-to-one match for every PDF page and lists
converted slides that did not win that match. It is a mapping aid: text-poor
pages, low-scoring matches, and unmatched slides still need visual review and
Keynote visibility/build evidence before they are accepted or excluded.

Example:
  python3 out/combined/audit_batch_source_alignment.py \
    --pptx out/.build/batch-01/source-pptx/01-408st-introduction.pptx \
    --pdf slides/f26-pdfs/01-408st-introduction.pdf \
    --page-map out/.build/batch-01/01-introduction-page-candidates.csv \
    --slide-audit out/.build/batch-01/01-introduction-slide-audit.csv
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

from audit_fall_text_overlap import first_lines, ordered_pptx_text, pdf_pages, tokens


def similarity(pdf_text: str, slide_text: str) -> tuple[float, float, float, int]:
    pdf_tokens = tokens(pdf_text)
    slide_tokens = tokens(slide_text)
    common = len(pdf_tokens & slide_tokens)
    if not pdf_tokens or not slide_tokens or not common:
        return 0.0, 0.0, 0.0, common
    pdf_coverage = common / len(pdf_tokens)
    slide_coverage = common / len(slide_tokens)
    f1 = (
        2 * pdf_coverage * slide_coverage / (pdf_coverage + slide_coverage)
        if pdf_coverage + slide_coverage
        else 0.0
    )
    return f1, pdf_coverage, slide_coverage, common


def ordered_alignment(scores: list[list[float]]) -> list[int]:
    """Return zero-based PPTX slide indices for each PDF page, in order."""
    page_count = len(scores)
    slide_count = len(scores[0]) if page_count else 0
    if page_count > slide_count:
        raise ValueError(
            f"reference has {page_count} pages but converted deck has "
            f"only {slide_count} slides"
        )
    neg_inf = -math.inf
    best = [[neg_inf] * (slide_count + 1) for _ in range(page_count + 1)]
    back: list[list[tuple[int, int, str] | None]] = [
        [None] * (slide_count + 1) for _ in range(page_count + 1)
    ]
    for j in range(slide_count + 1):
        best[0][j] = 0.0
    for i in range(1, page_count + 1):
        for j in range(1, slide_count + 1):
            skip = best[i][j - 1]
            match = best[i - 1][j - 1] + scores[i - 1][j - 1]
            if match >= skip:
                best[i][j] = match
                back[i][j] = (i - 1, j - 1, "match")
            else:
                best[i][j] = skip
                back[i][j] = (i, j - 1, "skip")
    if not math.isfinite(best[page_count][slide_count]):
        raise ValueError("could not construct an ordered alignment")
    result = [-1] * page_count
    i, j = page_count, slide_count
    while i:
        step = back[i][j]
        if step is None:
            raise ValueError("alignment backtrace is incomplete")
        prev_i, prev_j, action = step
        if action == "match":
            result[i - 1] = j - 1
        i, j = prev_i, prev_j
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pptx", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--page-map", type=Path, required=True)
    parser.add_argument("--slide-audit", type=Path, required=True)
    args = parser.parse_args()

    slide_texts = ordered_pptx_text(args.pptx)
    page_texts = pdf_pages(args.pdf)
    if not slide_texts or not page_texts:
        raise ValueError("PPTX and reference PDF must both contain pages")
    score_rows = [
        [similarity(page, slide)[0] for slide in slide_texts]
        for page in page_texts
    ]
    aligned = ordered_alignment(score_rows)
    chosen = set(aligned)
    args.page_map.parent.mkdir(parents=True, exist_ok=True)
    args.slide_audit.parent.mkdir(parents=True, exist_ok=True)

    with args.page_map.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "reference_pdf_page",
                "converted_pptx_slide",
                "f1_similarity",
                "pdf_text_coverage",
                "pptx_text_coverage",
                "common_tokens",
                "match_excerpt",
                "runner_up_pptx_slides",
                "review_status",
            ],
        )
        writer.writeheader()
        for page_index, slide_index in enumerate(aligned):
            f1, pdf_cov, slide_cov, common = similarity(
                page_texts[page_index], slide_texts[slide_index]
            )
            alternatives = sorted(
                (
                    (score_rows[page_index][j], j)
                    for j in range(len(slide_texts))
                    if j != slide_index
                ),
                reverse=True,
            )[:3]
            writer.writerow(
                {
                    "reference_pdf_page": page_index + 1,
                    "converted_pptx_slide": slide_index + 1,
                    "f1_similarity": f"{f1:.4f}",
                    "pdf_text_coverage": f"{pdf_cov:.4f}",
                    "pptx_text_coverage": f"{slide_cov:.4f}",
                    "common_tokens": common,
                    "match_excerpt": first_lines(slide_texts[slide_index], 2, 180),
                    "runner_up_pptx_slides": ";".join(
                        f"{j + 1}:{score:.3f}" for score, j in alternatives
                    ),
                    "review_status": (
                        "Visual review required"
                        if f1 < 0.35 or pdf_cov < 0.35
                        else "Candidate; visual review required"
                    ),
                }
            )

    with args.slide_audit.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "converted_pptx_slide",
                "best_reference_pdf_page",
                "f1_similarity",
                "pdf_text_coverage",
                "pptx_text_coverage",
                "chosen_by_ordered_alignment",
                "slide_excerpt",
                "review_status",
            ],
        )
        writer.writeheader()
        for slide_index, text in enumerate(slide_texts):
            rankings = sorted(
                (
                    (*similarity(page, text), page_index + 1)
                    for page_index, page in enumerate(page_texts)
                ),
                reverse=True,
            )
            f1, pdf_cov, slide_cov, _, page_no = rankings[0]
            chosen_flag = slide_index in chosen
            writer.writerow(
                {
                    "converted_pptx_slide": slide_index + 1,
                    "best_reference_pdf_page": page_no,
                    "f1_similarity": f"{f1:.4f}",
                    "pdf_text_coverage": f"{pdf_cov:.4f}",
                    "pptx_text_coverage": f"{slide_cov:.4f}",
                    "chosen_by_ordered_alignment": str(chosen_flag).lower(),
                    "slide_excerpt": first_lines(text, 2, 180),
                    "review_status": (
                        "Selected page candidate; visually review"
                        if chosen_flag
                        else "Unmatched: inspect Keynote visibility/build before disposition"
                    ),
                }
            )

    print(
        f"Aligned {len(page_texts)} reference pages to {len(slide_texts)} "
        f"converted slides; {len(slide_texts) - len(chosen)} converted slides "
        f"remain unmatched for source/visual review."
    )
    print(f"Page map: {args.page_map}")
    print(f"Slide audit: {args.slide_audit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
