#!/usr/bin/env python3
"""Run repeatable local checks on a source-mapped Google Slides pilot.

The script checks package integrity and relationships, map/order agreement,
unchanged control XML, PDF page counts, optional extracted-text expectations,
and pixel equality for controls in a supplied baseline Google PDF. A local
renderer PDF is optional: Google is the authoritative import result, and a
second renderer may substitute fonts or introduce unrelated differences. The
script does not call Google or replace visual review of repaired slides.
"""

from __future__ import annotations

import argparse
import csv
import json
import posixpath
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

from PIL import Image, ImageChops


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


class AuditError(Exception):
    """A check could not be completed or failed."""


def run_text(args: list[str]) -> str:
    result = subprocess.run(args, check=False, capture_output=True, text=True)
    if result.returncode:
        raise AuditError(
            f"Command failed ({result.returncode}): {args[0]}\n"
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout


def read_slide_order(package: zipfile.ZipFile) -> list[str]:
    names = set(package.namelist())
    try:
        presentation = ET.fromstring(package.read("ppt/presentation.xml"))
        relationships = ET.fromstring(package.read("ppt/_rels/presentation.xml.rels"))
    except (KeyError, ET.ParseError) as error:
        raise AuditError(f"Cannot read presentation slide order: {error}") from error

    targets = {
        rel.get("Id"): rel.get("Target")
        for rel in relationships.findall(f"{{{REL_NS}}}Relationship")
        if (rel.get("Type") or "").endswith("/slide")
    }
    slide_ids = presentation.find(f"{{{P_NS}}}sldIdLst")
    if slide_ids is None:
        raise AuditError("Presentation has no ordered slide list")

    ordered = []
    for slide in slide_ids.findall(f"{{{P_NS}}}sldId"):
        relation_id = slide.get(f"{{{R_NS}}}id")
        target = targets.get(relation_id)
        if not target:
            raise AuditError(f"Slide relationship {relation_id!r} is missing")
        if target.startswith("/"):
            part = target.lstrip("/")
        else:
            part = posixpath.normpath(posixpath.join("ppt", target))
        if part not in names:
            raise AuditError(f"Slide part is missing from package: {part}")
        ordered.append(part)
    return ordered


def check_package(path: Path) -> tuple[zipfile.ZipFile, list[str]]:
    package = zipfile.ZipFile(path)
    bad_member = package.testzip()
    if bad_member:
        package.close()
        raise AuditError(f"ZIP integrity failure in {path}: {bad_member}")

    names = set(package.namelist())
    for rels_path in (name for name in names if name.endswith(".rels")):
        try:
            relationships = ET.fromstring(package.read(rels_path))
        except ET.ParseError as error:
            package.close()
            raise AuditError(f"Invalid relationship XML in {rels_path}: {error}") from error

        if rels_path == "_rels/.rels":
            source_part = ""
        else:
            marker = "/_rels/"
            if marker not in rels_path:
                package.close()
                raise AuditError(f"Unexpected relationship path: {rels_path}")
            prefix, name = rels_path.split(marker, 1)
            if not name.endswith(".rels"):
                package.close()
                raise AuditError(f"Unexpected relationship filename: {rels_path}")
            source_part = posixpath.join(prefix, name[:-5])

        for rel in relationships.findall(f"{{{REL_NS}}}Relationship"):
            if rel.get("TargetMode") == "External":
                continue
            target = rel.get("Target")
            if not target:
                package.close()
                raise AuditError(f"Empty target in {rels_path}")
            uri_path = unquote(urlsplit(target).path)
            if uri_path.startswith("/"):
                destination = uri_path.lstrip("/")
            else:
                destination = posixpath.normpath(
                    posixpath.join(posixpath.dirname(source_part), uri_path)
                )
            if destination not in names:
                package.close()
                raise AuditError(
                    f"Unresolved relationship in {rels_path}: {target} -> {destination}"
                )

    return package, read_slide_order(package)


def load_map(path: Path) -> list[dict[str, str | int]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    required = {"pilot_page", "combined_slide", "role"}
    if not rows or not required.issubset(rows[0]):
        raise AuditError(f"Map must include columns: {', '.join(sorted(required))}")

    mapped = []
    for index, row in enumerate(rows, start=1):
        try:
            pilot_page = int(row["pilot_page"])
            combined_slide = int(row["combined_slide"])
        except (TypeError, ValueError) as error:
            raise AuditError(f"Invalid page number in map row {index + 1}") from error
        if pilot_page != index:
            raise AuditError(
                f"Map pilot pages must be contiguous: row {index} says {pilot_page}"
            )
        mapped.append({**row, "pilot_page": pilot_page, "combined_slide": combined_slide})

    combined = [int(row["combined_slide"]) for row in mapped]
    if any(right <= left for left, right in zip(combined, combined[1:])):
        raise AuditError("Map source slides must be unique and in increasing order")
    return mapped


def pdf_info(path: Path) -> dict[str, str | int]:
    output = run_text(["pdfinfo", str(path)])
    info: dict[str, str | int] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if key.strip() == "Pages":
            info["pages"] = int(value)
        elif key.strip() == "Page size":
            info["page_size"] = value
        elif key.strip() == "Creator":
            info["creator"] = value
    if "pages" not in info:
        raise AuditError(f"Could not read page count from {path}")
    return info


def extract_page_text(path: Path, expected_pages: int) -> list[str]:
    output = run_text(["pdftotext", "-layout", str(path), "-"])
    pages = output.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    if len(pages) != expected_pages:
        raise AuditError(
            f"Text extraction found {len(pages)} pages in {path}; expected {expected_pages}"
        )
    return pages


def render_page(pdf: Path, page: int, dpi: int, prefix: Path) -> Path:
    run_text([
        "pdftoppm", "-f", str(page), "-l", str(page), "-singlefile",
        "-png", "-r", str(dpi), str(pdf), str(prefix),
    ])
    image_path = prefix.with_suffix(".png")
    if not image_path.is_file():
        raise AuditError(f"Page renderer did not create {image_path}")
    return image_path


def count_changed_slide_parts(
    baseline: zipfile.ZipFile,
    pilot: zipfile.ZipFile,
    mapped_parts: set[str],
) -> tuple[list[str], list[str]]:
    baseline_names = set(baseline.namelist())
    pilot_names = set(pilot.namelist())
    common_slide_parts = {
        name for name in baseline_names & pilot_names
        if name.startswith("ppt/slides/")
        and name.endswith(".xml")
        and "/_rels/" not in name
    }
    changed = sorted(
        name for name in common_slide_parts
        if baseline.read(name) != pilot.read(name)
    )
    unexpected = sorted(name for name in changed if name not in mapped_parts)
    return changed, unexpected


def parse_expectation(value: str) -> tuple[int, str]:
    page_text, separator, text = value.partition(":")
    if not separator or not text:
        raise argparse.ArgumentTypeError("use PAGE:TEXT, for example 2:CFG")
    try:
        page = int(page_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("PAGE must be an integer") from error
    return page, text


def audit(args: argparse.Namespace) -> dict[str, object]:
    rows = load_map(args.page_map)
    baseline, baseline_order = check_package(args.baseline_pptx)
    pilot, pilot_order = check_package(args.pilot_pptx)
    try:
        if len(pilot_order) != len(rows):
            raise AuditError(
                f"Pilot has {len(pilot_order)} slides but map has {len(rows)} rows"
            )
        expected_parts = []
        for row in rows:
            combined_slide = int(row["combined_slide"])
            if not 1 <= combined_slide <= len(baseline_order):
                raise AuditError(f"Mapped slide {combined_slide} is outside the baseline")
            expected_parts.append(baseline_order[combined_slide - 1])
        if pilot_order != expected_parts:
            raise AuditError(
                "Pilot package order does not match the source-mapped slide order\n"
                f"expected: {expected_parts}\nactual:   {pilot_order}"
            )

        unchanged_controls = []
        for row, part in zip(rows, pilot_order):
            if str(row["role"]).strip().lower() == "control":
                if baseline.read(part) != pilot.read(part):
                    raise AuditError(
                        f"Control slide {row['combined_slide']} XML differs from baseline"
                    )
                unchanged_controls.append(int(row["combined_slide"]))

        changed_parts, unexpected_parts = count_changed_slide_parts(
            baseline, pilot, set(pilot_order)
        )
        if unexpected_parts:
            raise AuditError(
                "Unmapped slide XML changed: " + ", ".join(unexpected_parts)
            )

        linux_info = pdf_info(args.linux_pdf) if args.linux_pdf else None
        google_info = pdf_info(args.google_pdf)
        expected_pages = len(rows)
        if linux_info and linux_info["pages"] != expected_pages:
            raise AuditError(
                f"Linux PDF has {linux_info['pages']} pages; expected {expected_pages}"
            )
        if google_info["pages"] != expected_pages:
            raise AuditError(
                f"Google PDF has {google_info['pages']} pages; expected {expected_pages}"
            )

        google_text = extract_page_text(args.google_pdf, expected_pages)
        text_checks = []
        for page, text in args.expect_text:
            if not 1 <= page <= expected_pages:
                raise AuditError(f"Text expectation page {page} is outside the pilot")
            if text not in google_text[page - 1]:
                raise AuditError(f"Google PDF page {page} is missing expected text {text!r}")
            text_checks.append({"page": page, "contains": text})

        pixel_checks = []
        if args.baseline_google_pdf:
            baseline_pdf_info = pdf_info(args.baseline_google_pdf)
            with tempfile.TemporaryDirectory(prefix="cs408-pilot-audit-") as temp:
                temp_path = Path(temp)
                for row in rows:
                    if str(row["role"]).strip().lower() != "control":
                        continue
                    source_page = int(row["combined_slide"])
                    pilot_page = int(row["pilot_page"])
                    if source_page > int(baseline_pdf_info["pages"]):
                        raise AuditError(
                            f"Control slide {source_page} exceeds baseline Google PDF pages"
                        )
                    left_path = render_page(
                        args.baseline_google_pdf, source_page, args.dpi,
                        temp_path / f"baseline-{source_page}",
                    )
                    right_path = render_page(
                        args.google_pdf, pilot_page, args.dpi,
                        temp_path / f"pilot-{pilot_page}",
                    )
                    with Image.open(left_path) as left_image, Image.open(right_path) as right_image:
                        left = left_image.convert("RGB")
                        right = right_image.convert("RGB")
                        if left.size != right.size:
                            raise AuditError(
                                f"Control page sizes differ: {left.size} vs {right.size}"
                            )
                        diff = ImageChops.difference(left, right)
                        bbox = diff.getbbox()
                        if bbox is not None:
                            changed_pixels = sum(
                                pixel != (0, 0, 0) for pixel in diff.getdata()
                            )
                            raise AuditError(
                                f"Control slide {source_page} differs at {args.dpi} dpi: "
                                f"bbox={bbox}, changed_pixels={changed_pixels}"
                            )
                        pixel_checks.append({
                            "combined_slide": source_page,
                            "pilot_page": pilot_page,
                            "dpi": args.dpi,
                            "exact": True,
                        })

        return {
            "status": "pass",
            "pilot_pages": expected_pages,
            "combined_slide_order": [int(row["combined_slide"]) for row in rows],
            "control_slides_xml_identical": unchanged_controls,
            "changed_mapped_slide_parts": changed_parts,
            "linux_pdf": linux_info,
            "google_pdf": google_info,
            "google_text_checks": text_checks,
            "control_pixel_checks": pixel_checks,
            "notes": "Manual review of every repaired page is still required.",
        }
    finally:
        baseline.close()
        pilot.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-pptx", required=True, type=Path)
    parser.add_argument("--pilot-pptx", required=True, type=Path)
    parser.add_argument("--map", required=True, type=Path, dest="page_map")
    parser.add_argument(
        "--linux-pdf", type=Path,
        help="optional local-renderer PDF for diagnosis; Google PDF remains authoritative",
    )
    parser.add_argument("--google-pdf", required=True, type=Path)
    parser.add_argument("--baseline-google-pdf", type=Path)
    parser.add_argument("--dpi", type=int, default=120)
    parser.add_argument("--expect-text", action="append", type=parse_expectation, default=[])
    args = parser.parse_args()

    for value in (args.baseline_pptx, args.pilot_pptx, args.page_map, args.google_pdf):
        if not value.is_file():
            raise AuditError(f"Input file does not exist: {value}")
    if args.linux_pdf and not args.linux_pdf.is_file():
        raise AuditError(f"Local-renderer PDF does not exist: {args.linux_pdf}")
    if args.baseline_google_pdf and not args.baseline_google_pdf.is_file():
        raise AuditError(f"Baseline Google PDF does not exist: {args.baseline_google_pdf}")
    if not 36 <= args.dpi <= 300:
        raise AuditError("DPI must be between 36 and 300")

    print(json.dumps(audit(args), indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as error:
        print(f"AUDIT FAILED: {error}", file=sys.stderr)
        raise SystemExit(1) from error
