#!/usr/bin/env python3
"""Reconcile Batch 1 native WIP slides with the expanded candidate order.

Input JSON is a compact, notes-free readback from the native Slides text API:
{"revisionId": "...", "slides": [{"slide_number": 1,
"slide_object_id": "p1", "text": "..."}, ...]}. The script matches each
WIP slide only against candidate rows for its already established source deck
and PDF page, then uses ordered dynamic programming to choose candidate build
states. It rewrites the correspondence and insertion-gap CSVs after validating
that the WIP is a unique, ordered subsequence of the complete candidate map.

Use the connected Google Slides text readback to prepare the JSON. Do not add
speaker notes to the input; notes are unrelated to slide correspondence.
"""

from __future__ import annotations

import argparse
import csv
import json
import posixpath
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from zipfile import ZipFile

from lxml import etree


CORRESPONDENCE_FIELDS = [
    "wip_slide_number", "wip_slide_object_id", "candidate_output_slide",
    "row_type", "source_filename", "source_pdf_page", "source_build_state",
    "alignment_score", "alignment_basis",
]
GAP_FIELDS = [
    "candidate_output_slide", "row_type", "source_filename",
    "source_pdf_page", "source_build_state", "source_build_chunk_ids",
    "wip_insert_after_slide", "wip_insert_before_slide",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def tokens(value: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return re.findall(r"\w+", normalized, flags=re.UNICODE)


def similarity(left: str, right: str) -> float:
    a, b = tokens(left), tokens(right)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def candidate_slide_texts(path: Path) -> dict[int, str]:
    """Read candidate text in presentation order, resolving slide relationships."""
    ns = {
        "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    result: dict[int, str] = {}
    with ZipFile(path) as package:
        presentation = etree.fromstring(package.read("ppt/presentation.xml"))
        rels = etree.fromstring(package.read("ppt/_rels/presentation.xml.rels"))
        targets = {rel.get("Id"): rel.get("Target") for rel in rels.findall("rel:Relationship", ns)}
        nodes = presentation.findall("p:sldIdLst/p:sldId", ns)
        for number, node in enumerate(nodes, 1):
            target = targets[node.get(f"{{{ns['r']}}}id")]
            part = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("ppt", target))
            root = etree.fromstring(package.read(part))
            result[number] = "\n".join(root.xpath(".//a:t/text()", namespaces=ns))
    return result


def ordered_assignment(
    wip_rows: list[dict[str, str]], candidate_rows: list[dict[str, str]],
    current_by_wip: dict[int, int], candidate_text: dict[int, str],
) -> tuple[list[tuple[int, float]], list[list[float]]]:
    """Choose a strictly increasing candidate subsequence for one source page."""
    n, m = len(wip_rows), len(candidate_rows)
    if n > m:
        raise ValueError(f"{n} WIP slides cannot map to {m} candidate rows")
    score = [
        [similarity(w.get("text", ""), candidate_text.get(int(c["output_slide"]), ""))
         for c in candidate_rows]
        for w in wip_rows
    ]
    # A tiny tie preference preserves prior map decisions when text is identical
    # across states, while a better content match always wins.
    bonus = [
        [0.00001 if current_by_wip.get(int(w["slide_number"])) == int(c["output_slide"]) else 0.0
         for c in candidate_rows]
        for w in wip_rows
    ]
    dp = [[float("-inf")] * (m + 1) for _ in range(n + 1)]
    take = [[False] * (m + 1) for _ in range(n + 1)]
    for j in range(m + 1):
        dp[0][j] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            skip = dp[i][j - 1]
            match = dp[i - 1][j - 1] + score[i - 1][j - 1] + bonus[i - 1][j - 1]
            if match >= skip:
                dp[i][j] = match
                take[i][j] = True
            else:
                dp[i][j] = skip
    if dp[n][m] == float("-inf"):
        raise ValueError("Could not construct an ordered correspondence")
    chosen: list[tuple[int, float]] = []
    i, j = n, m
    while i:
        if j == 0:
            raise ValueError("Could not backtrack an ordered correspondence")
        if take[i][j]:
            chosen.append((j - 1, score[i - 1][j - 1]))
            i -= 1
            j -= 1
        else:
            j -= 1
    chosen.reverse()
    return chosen, score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wip-text", required=True, type=Path)
    parser.add_argument("--candidate-pptx", required=True, type=Path)
    parser.add_argument("--candidate-map", required=True, type=Path)
    parser.add_argument("--correspondence", required=True, type=Path)
    parser.add_argument("--gaps", required=True, type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.wip_text.read_text(encoding="utf-8"))
    wip = payload["slides"]
    candidate = read_csv(args.candidate_map)
    old_correspondence = read_csv(args.correspondence)
    candidate_text = candidate_slide_texts(args.candidate_pptx)
    candidate_by_page: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in candidate:
        candidate_by_page.setdefault(
            (row["source_filename"], row["source_pdf_page"]), []
        ).append(row)
    current_by_wip = {
        int(row["wip_slide_number"]): int(row["candidate_output_slide"])
        for row in old_correspondence
    }

    # Candidate source/page labels are authoritative for the ordered topics;
    # existing correspondence supplies each WIP slide's source/page group.
    old_by_wip = {int(row["wip_slide_number"]): row for row in old_correspondence}
    wip_by_page: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in wip:
        old = old_by_wip[int(row["slide_number"])]
        page_key = (old["source_filename"], old["source_pdf_page"])
        enriched = {**row, **old}
        wip_by_page.setdefault(page_key, []).append(enriched)

    revised: dict[int, dict[str, str]] = {}
    changed: list[dict[str, object]] = []
    for page_key, group in wip_by_page.items():
        options = candidate_by_page.get(page_key, [])
        if not options:
            raise ValueError(f"No candidate rows for source page {page_key}")
        # Empty/image-only pages have no text signal; retain their existing row.
        if not any(tokens(row.get("text", "")) for row in group):
            for row in group:
                current = current_by_wip[int(row["slide_number"])]
                match_index = next(
                    (i for i, candidate_row in enumerate(options)
                     if int(candidate_row["output_slide"]) == current), None
                )
                if match_index is None:
                    raise ValueError(f"Current image-only mapping {current} is outside {page_key}")
                revised[int(row["slide_number"])] = {
                    **row, "candidate_output_slide": str(current),
                    "alignment_score": "0.000", "alignment_basis": "source_order_image_only",
                }
            continue

        chosen, scores = ordered_assignment(group, options, current_by_wip, candidate_text)
        for local_index, (row, (option_index, picked_score)) in enumerate(zip(group, chosen, strict=True)):
            number = int(row["slide_number"])
            picked = options[option_index]
            current = current_by_wip[number]
            picked_id = int(picked["output_slide"])
            current_index = next(
                (i for i, item in enumerate(options) if int(item["output_slide"]) == current), None
            )
            current_score = scores[local_index][current_index] if current_index is not None else 0.0
            result = {
                **row,
                "candidate_output_slide": str(picked_id),
                "row_type": picked["row_type"],
                "source_filename": picked["source_filename"],
                "source_pdf_page": picked["source_pdf_page"],
                "source_build_state": picked.get("source_build_state", ""),
                "alignment_score": f"{picked_score:.3f}",
                "alignment_basis": "native_text_ordered_same_source_page",
            }
            revised[number] = result
            if current != picked_id:
                def excerpt(value: str) -> str:
                    return " ".join(value.split())[:180]

                changed.append({
                    "wip_slide": number, "source_page": page_key[1],
                    "old_candidate": current, "old_score": round(current_score, 3),
                    "new_candidate": picked_id, "new_score": round(picked_score, 3),
                    "new_state": result["source_build_state"],
                    "wip_excerpt": excerpt(row.get("text", "")),
                    "old_candidate_excerpt": excerpt(candidate_text.get(current, "")),
                    "new_candidate_excerpt": excerpt(candidate_text.get(picked_id, "")),
                })

    ordered = [revised[n] for n in sorted(revised)]
    candidate_numbers = [int(row["candidate_output_slide"]) for row in ordered]
    if len(set(candidate_numbers)) != len(candidate_numbers):
        raise ValueError("Correspondence reuses candidate output rows")
    if candidate_numbers != sorted(candidate_numbers):
        raise ValueError("Correspondence does not follow candidate output order")
    candidate_numbers_all = [int(row["output_slide"]) for row in candidate]
    mapped_set = set(candidate_numbers)
    unmapped = [row for row in candidate if int(row["output_slide"]) not in mapped_set]

    gap_rows: list[dict[str, str]] = []
    for row in unmapped:
        number = int(row["output_slide"])
        previous = next((item for item in reversed(ordered)
                         if int(item["candidate_output_slide"]) < number), None)
        following = next((item for item in ordered
                          if int(item["candidate_output_slide"]) > number), None)
        gap_rows.append({
            "candidate_output_slide": str(number),
            "row_type": row["row_type"],
            "source_filename": row["source_filename"],
            "source_pdf_page": row.get("source_pdf_page", ""),
            "source_build_state": row.get("source_build_state", ""),
            "source_build_chunk_ids": row.get("source_build_chunk_ids", ""),
            "wip_insert_after_slide": str(previous["wip_slide_number"]) if previous else "0",
            "wip_insert_before_slide": str(following["wip_slide_number"]) if following else "",
        })
    if len(mapped_set) + len(unmapped) != len(candidate_numbers_all):
        raise ValueError("Candidate coverage is incomplete")

    if args.write:
        write_csv(args.correspondence, CORRESPONDENCE_FIELDS, ordered)
        write_csv(args.gaps, GAP_FIELDS, gap_rows)
    print(json.dumps({
        "revisionId": payload.get("revisionId"),
        "wipSlides": len(ordered), "candidateRows": len(candidate),
        "mappedRows": len(mapped_set), "gapRows": len(gap_rows),
        "gapAnchors": len({(r["wip_insert_after_slide"], r["wip_insert_before_slide"]) for r in gap_rows}),
        "changedMappings": changed,
        "wipCandidateOrderValid": True,
        "candidateCoverageValid": True,
        "written": args.write,
    }, indent=2))


if __name__ == "__main__":
    main()
