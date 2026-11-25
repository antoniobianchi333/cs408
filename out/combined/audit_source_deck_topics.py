#!/usr/bin/env python3
"""Build the first-pass topic map from Spring candidate decks to Fall sources.

This is a first-pass topic/source map, with any completed reconciliation
exceptions recorded explicitly below. Exact basename matches and aliases
identify candidate current sources; do not treat an inventory match as
content-equivalence evidence.
"""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources.csv"
FALL_INVENTORY = HERE / "fall-keynote-inventory.csv"
OUTPUT = HERE / "source-deck-topic-audit.csv"

ALIASES = {
    "03-408st-structural-coverage-cfg": (
        "slides/05-408st-cfg.key", "topic-name mapping"
    ),
    "04-408st-structural-coverage-2": (
        "slides/06-408st-structural-coverage.key", "topic-name mapping"
    ),
    "08-408st-data-flow": (
        "slides/07-408st-data-flow.key", "renumbered topic mapping"
    ),
    "09-408st-input-space-partitioning": (
        "slides/04-408st-input-space-partitioning.key", "renumbered topic mapping"
    ),
    "11-408st-mutation-based-randomized-testing": (
        "slides/14-408st-intro-to-fuzzing.key; "
        "slides/15-408st-greybox-fuzzing.key",
        "topic split across Fall decks",
    ),
    "12-408st-mutation-testing": (
        "slides/10-408st-mutation-testing.key", "renumbered topic mapping"
    ),
    "14-408st-midterm-review": (
        "slides/13-408st-midterm-review.key", "renumbered topic mapping"
    ),
    "15-408st-logic-coverage": (
        "slides/f26-pdfs/8-408st-logic-coverage.pdf", "Fall PDF-only source mapping"
    ),
    "16-408st-active-logic-coverage": (
        "slides/09-408st-active-logic-coverage.key", "renumbered topic mapping"
    ),
    "18-408st-concolic-execution": (
        "slides/f26-pdfs/18-408st-concolic-execution.pdf", "Fall PDF-only source mapping"
    ),
    "19-408st-test-oracles": (
        "slides/11-408st-test-oracles.key", "renumbered topic mapping"
    ),
    "20-408st-TestCase-Minimization": (
        "slides/16-408st-TestCase-Minimization.key", "renumbered topic mapping"
    ),
    "intro-lab-2": (
        "labs/lab1/handout/lab1.tex; labs/lab1/slides/intro.pptx; "
        "slides/f26-pdfs/14-408st-intro-to-fuzzing.pdf; "
        "slides/f26-pdfs/15-408st-greybox-fuzzing.pdf",
        "Fall fuzzing lectures and Lab 1 overlap the old tutorial",
    ),
}

# These are retained on the Fall branch for provenance/history but are not the
# selected newest source for the topic. Keep their current branch path in the
# audit so the blob comparison can document that they are unchanged archives.
SUPERSEDED = {
    "03-408st-fault-error-failure": (
        "Older Fall 2025 Fault/Error/Failure version; exclude from the selected "
        "set in favor of complete Fall 2026 slides/02-408st-fault-error-failure.key "
        "and slides/f26-pdfs/02-408st-fault-error-failure.pdf."
    ),
}

FIELDS = [
    "candidate_order",
    "spring_candidate_deck",
    "combined_slide_range",
    "slide_count",
    "spring_source",
    "fall_source_candidates",
    "inventory_match",
    "selection_status",
    "notes",
]


def main() -> None:
    with SOURCES.open(newline="", encoding="utf-8") as f:
        source_rows = list(csv.DictReader(f))
    with FALL_INVENTORY.open(newline="", encoding="utf-8") as f:
        fall_rows = list(csv.DictReader(f))
    fall_stems = {Path(row["path"]).stem for row in fall_rows}

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in source_rows:
            deck = row["deck"]
            if deck in SUPERSEDED and deck in fall_stems:
                candidates = f"slides/{deck}.key"
                match = "same basename; retained older version"
                status = "Exclude superseded Fall 2025 version; select Fall 2026 FEF source"
                notes = SUPERSEDED[deck]
            elif deck in fall_stems:
                candidates = f"slides/{deck}.key"
                match = "same basename"
                status = "Fall complete topic source candidate; page/build comparison pending"
                notes = (
                    "Filename match is inventory evidence only; reconcile every "
                    "slide/build before final source map and conversion."
                )
            elif deck in ALIASES:
                candidates, match = ALIASES[deck]
                if deck == "intro-lab-2":
                    status = "Select complete Fall Lab 1/fuzzing sources; exclude the superseded Spring tutorial"
                    notes = (
                        "The 43-page Spring PDF teaches a fuzzer lab: black-box "
                        "and grey-box fuzzers, grammar-based generation, AFL, "
                        "competition, and submission. Fall's complete Lab 1 "
                        "tutorial (40 source slides) was imported as 62 Google "
                        "slides in Round 13; all 62 Google PDF pages were "
                        "visually reviewed, with paragraph states 8/6/11 and "
                        "the AFL screenshot zoom pair mapped. Select Fall and "
                        "retain the Spring PDF for comparison/provenance only. "
                        "The Fall handout says due October 30; the syllabus "
                        "table says November 3. Round 13 uses the handout date "
                        "and records the conflict for resolution."
                    )
                else:
                    status = "Fall complete topic source candidate; page/build comparison pending"
                    notes = (
                        "Topic/filename mapping is provisional; verify full "
                        "content, source deck order, notes, and meaningful "
                        "builds before final selection."
                    )
            else:
                candidates = ""
                match = "no filename/topic mapping yet"
                status = "unresolved; audit for complete older topic absent from Fall"
                notes = (
                    "No Fall Keynote candidate was assigned by the initial "
                    "inventory pass; compare syllabus, Fall materials, and "
                    "source contents before deciding."
                )

            writer.writerow(
                {
                    "candidate_order": row["section"],
                    "spring_candidate_deck": deck,
                    "combined_slide_range": (
                        f"{row['first_slide']}-{row['last_slide']}"
                    ),
                    "slide_count": row["slide_count"],
                    "spring_source": row["source"],
                    "fall_source_candidates": candidates,
                    "inventory_match": match,
                    "selection_status": status,
                    "notes": notes,
                }
            )

    exact = sum(row["deck"] in fall_stems for row in source_rows)
    topic_aliases = sum(deck != "intro-lab-2" for deck in ALIASES)
    print(
        f"Wrote {OUTPUT} with {len(source_rows)} candidate-deck rows; "
        f"exact basename matches: {exact}; explicit topic/renumbering maps: "
        f"{topic_aliases}; separate Spring Lab 2 mapping: 1"
    )


if __name__ == "__main__":
    main()
