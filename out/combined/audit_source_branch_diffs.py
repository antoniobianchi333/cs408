#!/usr/bin/env python3
"""Record Git blob comparisons for Spring candidate to Fall source mappings.

This is provenance evidence only. Byte-identical blobs do not prove that a
topic belongs in the course sequence, and changed blobs do not establish
semantic equivalence or supersession. Use the content crosswalk for selection.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources.csv"
TOPIC_AUDIT = HERE / "source-deck-topic-audit.csv"
OUTPUT = HERE / "source-branch-diff-audit.csv"


def git_blob(ref: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        return None
    return result.stdout.strip()


def require_ref(ref: str) -> None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise SystemExit(
            f"Git ref {ref!r} is unavailable; fetch or create it before running "
            "this provenance audit."
        )


def old_repo_path(source: str) -> str:
    if source.startswith(("slides/", "labs/")):
        return source
    # `sources.csv` paths such as `pdfs/...` are relative to the slides tree.
    return f"slides/{source}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-ref", default="spring+2026")
    parser.add_argument("--new-ref", default="fall+2026")
    args = parser.parse_args()
    require_ref(args.old_ref)
    require_ref(args.new_ref)

    with SOURCES.open(newline="", encoding="utf-8") as stream:
        source_rows = {row["deck"]: row for row in csv.DictReader(stream)}
    with TOPIC_AUDIT.open(newline="", encoding="utf-8") as stream:
        topic_rows = list(csv.DictReader(stream))

    fields = [
        "candidate_order",
        "spring_candidate_deck",
        "spring_source_path",
        "spring_ref_blob",
        "fall_source_candidate",
        "fall_ref_blob",
        "blob_relation",
    ]
    counts: Counter[str] = Counter()
    with OUTPUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in topic_rows:
            source = source_rows[row["spring_candidate_deck"]]["source"]
            spring_path = old_repo_path(source)
            spring_blob = git_blob(args.old_ref, spring_path)
            fall_paths = [
                item.strip()
                for item in row["fall_source_candidates"].split(";")
                if item.strip()
            ]
            for fall_path in fall_paths:
                fall_blob = git_blob(args.new_ref, fall_path)
                if spring_blob is None:
                    relation = "source absent at old ref"
                elif fall_blob is None:
                    relation = "candidate absent at new ref"
                elif spring_blob == fall_blob:
                    relation = "identical blob"
                else:
                    relation = "changed blob"
                counts[relation] += 1
                writer.writerow(
                    {
                        "candidate_order": row["candidate_order"],
                        "spring_candidate_deck": row["spring_candidate_deck"],
                        "spring_source_path": spring_path,
                        "spring_ref_blob": spring_blob or "",
                        "fall_source_candidate": fall_path,
                        "fall_ref_blob": fall_blob or "",
                        "blob_relation": relation,
                    }
                )

    print(
        f"Wrote {OUTPUT.name}: {len(topic_rows)} candidate rows; "
        f"{sum(counts.values())} mapped source comparisons; "
        + ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
    )


if __name__ == "__main__":
    main()
