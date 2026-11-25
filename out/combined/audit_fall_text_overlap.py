#!/usr/bin/env python3
"""Build a heuristic Fall-PDF to current-slide text-overlap report.

This is a triage aid, not a source-selection decision or a substitute for
visual/build review. It extracts text from each Fall PDF page with pdftotext,
reads text from the editable PPTX in presentation order and from the current
combined reference PDF, and finds the best lexical match in each candidate
slide range. Comparing both outputs helps distinguish missing content from
content present only as an image in the PPTX.

Example from the repository root:
  python3 out/combined/audit_fall_text_overlap.py \
    --pdf-dir slides/f26-pdfs \
    --pptx out/combined/cs408-all-slides-editable.pptx \
    --reference-pdf out/combined/cs408-all-slides.pdf \
    --crosswalk out/combined/source-version-crosswalk.csv \
    --output out/.build/fall-current-text-overlap.csv \
    --reverse-output out/.build/current-fall-text-overlap.csv \
    --summary-output out/.build/fall-topic-overlap-summary.csv
"""

from __future__ import annotations

import argparse
import csv
import posixpath
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P_NS = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+#-]{2,}")
STOPWORDS = set(
    "the and for are that this with from was were will have has had you your our "
    "but not can may how why what when where which who does did into than then "
    "use using used all any out one two new more some each their they them its "
    "about also just let lets now we is it to of in on as by be or an a at if do so"
    .split()
)


def parse_ranges(value: str) -> list[int]:
    slides: set[int] = set()
    for part in value.split(";"):
        part = part.strip()
        if not part:
            continue
        match = re.fullmatch(r"(\d+)(?:-(\d+))?", part)
        if not match:
            raise ValueError(f"invalid slide range: {part!r}")
        first = int(match.group(1))
        last = int(match.group(2) or first)
        if last < first:
            raise ValueError(f"descending slide range: {part!r}")
        slides.update(range(first, last + 1))
    return sorted(slides)


def tokens(text: str) -> set[str]:
    return {
        token.lower()
        for token in TOKEN_RE.findall(text)
        if token.lower() not in STOPWORDS
    }


def ordered_pptx_text(pptx_path: Path) -> list[str]:
    with zipfile.ZipFile(pptx_path) as package:
        presentation = ET.fromstring(package.read("ppt/presentation.xml"))
        rels_root = ET.fromstring(package.read("ppt/_rels/presentation.xml.rels"))
        rels = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels_root.findall(REL_NS + "Relationship")
        }
        slide_ids = [
            node.attrib[R_NS + "id"]
            for node in presentation.find(P_NS + "sldIdLst")
        ]
        result: list[str] = []
        for rel_id in slide_ids:
            target = rels[rel_id]
            slide_path = (
                target.lstrip("/")
                if target.startswith("/")
                else posixpath.normpath(posixpath.join("ppt", target))
            )
            root = ET.fromstring(package.read(slide_path))
            result.append(" ".join((node.text or "") for node in root.iter(A_NS + "t")))
        return result


def pdf_pages(path: Path) -> list[str]:
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    pages = result.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def first_lines(text: str, count: int = 2, limit: int = 180) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return " / ".join(lines[:count])[:limit]


def overlap(query: set[str], candidate: set[str]) -> tuple[float, float, int]:
    common = len(query & candidate)
    return (
        common / len(query) if query else 0.0,
        common / len(query | candidate) if query | candidate else 0.0,
        common,
    )


def ranked_matches(
    query: set[str], candidates: list[set[str]], slide_numbers: list[int]
) -> list[tuple[float, float, int, int]]:
    ranked = []
    for slide_no in slide_numbers:
        coverage, jaccard, common = overlap(query, candidates[slide_no - 1])
        if common:
            ranked.append((coverage, jaccard, common, slide_no))
    ranked.sort(reverse=True)
    return ranked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", type=Path, required=True)
    parser.add_argument("--pptx", type=Path, required=True)
    parser.add_argument("--reference-pdf", type=Path, required=True)
    parser.add_argument("--crosswalk", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--reverse-output",
        type=Path,
        help=(
            "optional current-slide-to-Fall-page report, useful for finding "
            "older material that may be absent from the newer source"
        ),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        help="optional per-Fall-deck counts derived from the forward report",
    )
    args = parser.parse_args()

    slide_text = ordered_pptx_text(args.pptx)
    slide_tokens = [tokens(text) for text in slide_text]
    reference_pages = pdf_pages(args.reference_pdf)
    reference_tokens = [tokens(text) for text in reference_pages]
    if len(reference_pages) != len(slide_text):
        raise ValueError(
            f"PPTX has {len(slide_text)} slides but reference PDF has "
            f"{len(reference_pages)} pages"
        )
    output_rows: list[dict[str, object]] = []

    with args.crosswalk.open(newline="", encoding="utf-8-sig") as source:
        crosswalk = csv.DictReader(source)
        for mapping in crosswalk:
            pdf_rel = Path(mapping["fall_2026_source"])
            pdf_path = args.pdf_dir / pdf_rel.name
            candidates = parse_ranges(mapping["current_candidate_combined_slides"])
            valid_candidates = [
                slide_no for slide_no in candidates if 1 <= slide_no <= len(slide_text)
            ]
            if not pdf_path.is_file():
                print(f"missing PDF: {pdf_path}", file=sys.stderr)
                continue
            for page_no, text in enumerate(pdf_pages(pdf_path), 1):
                query = tokens(text)
                ranked_pptx = ranked_matches(query, slide_tokens, valid_candidates)
                ranked_pdf = ranked_matches(query, reference_tokens, valid_candidates)
                best_pptx = (
                    ranked_pptx[0] if ranked_pptx else (0.0, 0.0, 0, 0)
                )

                second_pptx = (
                    ranked_pptx[1] if len(ranked_pptx) > 1 else (0.0, 0.0, 0, 0)
                )
                best_pdf = ranked_pdf[0] if ranked_pdf else (0.0, 0.0, 0, 0)
                second_pdf = (
                    ranked_pdf[1] if len(ranked_pdf) > 1 else (0.0, 0.0, 0, 0)
                )
                output_rows.append(
                    {
                        "fall_pdf": mapping["fall_2026_source"],
                        "fall_page": page_no,
                        "fall_heading": first_lines(text),
                        "candidate_slide_ranges": mapping[
                            "current_candidate_combined_slides"
                        ],
                        "best_pptx_slide": best_pptx[3],
                        "pptx_token_coverage": f"{best_pptx[0]:.4f}",
                        "pptx_jaccard": f"{best_pptx[1]:.4f}",
                        "pptx_shared_tokens": best_pptx[2],
                        "second_pptx_slide": second_pptx[3],
                        "second_pptx_coverage": f"{second_pptx[0]:.4f}",
                        "best_reference_pdf_page": best_pdf[3],
                        "reference_pdf_token_coverage": f"{best_pdf[0]:.4f}",
                        "reference_pdf_jaccard": f"{best_pdf[1]:.4f}",
                        "reference_pdf_shared_tokens": best_pdf[2],
                        "second_reference_pdf_page": second_pdf[3],
                        "second_reference_pdf_coverage": f"{second_pdf[0]:.4f}",
                        "fall_text_chars": len(text),
                    }
                )

    reverse_rows: list[dict[str, object]] = []
    if args.reverse_output:
        with args.crosswalk.open(newline="", encoding="utf-8-sig") as source:
            for mapping in csv.DictReader(source):
                pdf_path = args.pdf_dir / Path(mapping["fall_2026_source"]).name
                if not pdf_path.is_file():
                    continue
                fall_pages = pdf_pages(pdf_path)
                fall_tokens = [tokens(text) for text in fall_pages]
                fall_page_numbers = list(range(1, len(fall_pages) + 1))
                slide_numbers = [
                    slide_no
                    for slide_no in parse_ranges(
                        mapping["current_candidate_combined_slides"]
                    )
                    if 1 <= slide_no <= len(slide_text)
                ]
                for slide_no in slide_numbers:
                    pptx_text = slide_text[slide_no - 1]
                    reference_text = reference_pages[slide_no - 1]
                    ranked_pptx = ranked_matches(
                        tokens(pptx_text), fall_tokens, fall_page_numbers
                    )
                    ranked_reference = ranked_matches(
                        tokens(reference_text), fall_tokens, fall_page_numbers
                    )
                    best_pptx = (
                        ranked_pptx[0]
                        if ranked_pptx
                        else (0.0, 0.0, 0, 0)
                    )
                    best_reference = (
                        ranked_reference[0]
                        if ranked_reference
                        else (0.0, 0.0, 0, 0)
                    )
                    reverse_rows.append(
                        {
                            "fall_pdf": mapping["fall_2026_source"],
                            "candidate_slide_ranges": mapping[
                                "current_candidate_combined_slides"
                            ],
                            "current_slide": slide_no,
                            "current_heading": first_lines(reference_text),
                            "best_fall_page_pptx": best_pptx[3],
                            "pptx_token_coverage": f"{best_pptx[0]:.4f}",
                            "pptx_jaccard": f"{best_pptx[1]:.4f}",
                            "pptx_shared_tokens": best_pptx[2],
                            "best_fall_page_reference_pdf": best_reference[3],
                            "reference_pdf_token_coverage": (
                                f"{best_reference[0]:.4f}"
                            ),
                            "reference_pdf_jaccard": (
                                f"{best_reference[1]:.4f}"
                            ),
                            "reference_pdf_shared_tokens": best_reference[2],
                            "current_text_chars": len(reference_text),
                        }
                    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output_rows[0]) if output_rows else []
    with args.output.open("w", newline="", encoding="utf-8") as dest:
        writer = csv.DictWriter(dest, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    if args.reverse_output:
        args.reverse_output.parent.mkdir(parents=True, exist_ok=True)
        reverse_fields = list(reverse_rows[0]) if reverse_rows else []
        with args.reverse_output.open("w", newline="", encoding="utf-8") as dest:
            writer = csv.DictWriter(
                dest, fieldnames=reverse_fields, lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(reverse_rows)

    if args.summary_output:
        grouped: dict[str, dict[str, object]] = {}
        for row in output_rows:
            fall_pdf = str(row["fall_pdf"])
            summary = grouped.setdefault(
                fall_pdf,
                {
                    "fall_pdf": fall_pdf,
                    "fall_pages": 0,
                    "candidate_slide_ranges": row["candidate_slide_ranges"],
                    "strong_pptx_text_matches": 0,
                    "strong_reference_pdf_matches": 0,
                    "zero_pptx_text_overlap": 0,
                    "weak_reference_pdf_matches_lt_0_35": 0,
                },
            )
            summary["fall_pages"] = int(summary["fall_pages"]) + 1
            summary["strong_pptx_text_matches"] = int(
                summary["strong_pptx_text_matches"]
            ) + (float(row["pptx_token_coverage"]) >= 0.70)
            summary["strong_reference_pdf_matches"] = int(
                summary["strong_reference_pdf_matches"]
            ) + (float(row["reference_pdf_token_coverage"]) >= 0.70)
            summary["zero_pptx_text_overlap"] = int(
                summary["zero_pptx_text_overlap"]
            ) + (float(row["pptx_token_coverage"]) == 0.0)
            summary["weak_reference_pdf_matches_lt_0_35"] = int(
                summary["weak_reference_pdf_matches_lt_0_35"]
            ) + (float(row["reference_pdf_token_coverage"]) < 0.35)
        args.summary_output.parent.mkdir(parents=True, exist_ok=True)
        with args.summary_output.open("w", newline="", encoding="utf-8") as dest:
            fields = [
                "fall_pdf",
                "fall_pages",
                "candidate_slide_ranges",
                "strong_pptx_text_matches",
                "strong_reference_pdf_matches",
                "zero_pptx_text_overlap",
                "weak_reference_pdf_matches_lt_0_35",
            ]
            writer = csv.DictWriter(dest, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(grouped.values())

    print(
        f"slides={len(slide_text)} fall_pages={len(output_rows)} "
        f"output={args.output}"
    )
    if args.reverse_output:
        print(f"reverse_rows={len(reverse_rows)} output={args.reverse_output}")
    if args.summary_output:
        print(f"summary_decks={len(grouped)} output={args.summary_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
