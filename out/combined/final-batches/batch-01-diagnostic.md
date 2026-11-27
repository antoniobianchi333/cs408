# Batch 1 diagnostic: Week 1

**Updated:** 2026-11-26  
**Status:** Local source conversion and preliminary PDF alignment exist;
source/build disposition, repairs, final assembly, Google import, and visual
acceptance remain open.

## Scope and source of truth

Batch 1 follows the current Fall syllabus and keeps both Week 1 topics whole:

1. `01-408st-introduction.key` — Introduction and administrivia.
2. `02-408st-fault-error-failure.key` — Faults, Errors, and Failures.

The matching current Fall references are
[`01-408st-introduction.pdf`](../../../slides/f26-pdfs/01-408st-introduction.pdf)
(30 pages) and
[`02-408st-fault-error-failure.pdf`](../../../slides/f26-pdfs/02-408st-fault-error-failure.pdf)
(79 pages). The PDFs are the main visual references, subject to confirming
that each page reflects the selected Keynote revision. Preserve the newest
Fall content and use the source package to resolve content absent from an
older PDF.

## Conversion and alignment evidence

On Linux, LibreOffice converted the two selected `.key` packages to PPTX.
The candidates are ignored work files:

- `out/.build/batch-01/source-pptx/01-408st-introduction.pptx`
- `out/.build/batch-01/source-pptx/02-408st-fault-error-failure.pptx`

The generated PPTX files contain 92 and 108 slides, while the corresponding
current Fall PDFs contain 30 and 79 pages. These counts are not equivalent:
the `.key` packages contain saved/old records and possible build states, and
the PDF may show only one state. Therefore, neither deleting all unmatched
slides nor keeping every LibreOffice page is justified by page counts alone.

[`audit_batch_source_alignment.py`](../audit_batch_source_alignment.py)
produced an ordered text-based page alignment. It proposes 30 Introduction
and 79 Fault/Error candidate slide matches. The four CSVs linked from the
[batch workspace index](README.md) preserve both the page proposals and the
audit of unmatched candidate slides. Alignment scores are triage evidence;
they do not prove visual correctness or source visibility.

Current visual work files, including local PDF renders and side-by-side
contact sheets, are under ignored `out/.build/batch-01/`. They are diagnostic
and must be regenerated if absent. The Fault/Error sheets covering reference
pages 33–79 and contact sheets of every unmatched candidate have now been
generated and inspected. This is first-pass visual triage, not a source/build
disposition; unmatched candidates still need Keynote visibility/build review.

## Confirmed findings so far

### Introduction

- The first converted slide is a stale Fall 2025 title. The current Fall PDF
  title aligns to converted candidate slide 2.
- The current 30-page PDF maps in order to candidate slides, but many other
  converted slides remain unmatched. Do not carry over old administration or
  duplicate pages solely because they are present in the package.
- The provisional map flags low-text or image-heavy reference pages 7–9,
  13, 20, and 23 for direct visual/source-package review.
- Initial comparison found empty grading tables where the Fall PDF has values,
  a stale `Two-Step Submission` overlay, an obsolete schedule, a clipped
  objectives callout, and a distorted diagram. Rebuild these as native text,
  tables, and shapes where practical.
- One current Fall screenshot/image page is absent or materially different
  in the `.key` conversion. Check the exact source revision and embedded media
  before deciding whether a small image crop is required.

### Faults, Errors, and Failures

- Candidate slide 1 is a stale Fall 2025 title. Current PDF page 1 aligns to
  candidate slide 2. Converted slides 3–19 contain old administration and
  review material, but unmatched-page/build inspection is still needed before
  exclusion is final.
- The ordered map proposes current PDF pages 1–79. Several skipped converted
  slides inside that range may be animation/build states; inspect their source
  build records and visual sequence rather than discarding them automatically.
- Pages 33–43 (modeling computations and number-state examples) mostly retain
  their content. Check code/table legibility at full size and preserve any
  meaningful state sequence.
- Reference page 68 has a poor image/video composition in the candidate
  (candidate slide 94); investigate the source crop/build. Keep accompanying
  instructional text editable and use only the smallest necessary image
  replacement.
- Reference page 65 (candidate slide 90) has a distorted RIRP diagram: arrows
  cross labels and shapes. Rebuild its geometry as native shapes/connectors.
- Reference page 74 (candidate slide 102) has scientific-method arrows
  crossing the diagram text; repair the native diagram and verify endpoints.
- Reference page 75 (candidate slide 103) has overlapping/misplaced diagram
  arrows. Repair the diagram natively and compare every connection to the PDF.
- Reference page 76 (candidate slide 104) is missing the colored outcome
  table and has poor text/table layout. Restore the table as native cells or
  shapes and fit the adjacent prompt.
- Reference pages 77–78 (candidate slides 105–106) have blank comparison
  matrices where the references contain colored/labelled values. Restore the
  correct values and color states separately; do not assume the pages are
  duplicates.
- Several code/example pages near the end need full-size inspection for text
  collisions and clipping. Adjust text boxes or font sizes before considering
  image fallback.

## Visual triage of unmatched candidates

The reusable
[`render_unmatched_contact_sheets.py`](../render_unmatched_contact_sheets.py)
script generated contact sheets for all 62 unmatched Introduction candidates
and all 29 unmatched Fault/Error candidates. They are in ignored
`out/.build/batch-01/unmatched-review/` and can be regenerated from the local
PDFs and candidate-audit CSVs.

- **Introduction:** candidate 1 is the Fall 2025 title and is obsolete.
  Candidates 18–19 add objective/interactivity content around the selected
  `Who` pages; their relation to current builds is unresolved. Candidates
  34–43 include polls, `When to test?`, reliability images, and a space-error
  image/quote sequence. Some are likely older content, but the image/quote
  pages can be related build states because their visual/text content overlaps
  current reference pages. Candidates 44–70 include older duplicate
  testing/failure slides, while 71–90 include a prior recap and old admin,
  staffing, policy, and schedule pages. Candidates 91–92 are image-only
  records. Do not bulk-delete these ranges until each potentially current
  build/image state is reconciled with the Keynote slide order and PDF.
- **Fault/Error:** candidates 1 and 3–19 are clearly a Fall 2025 title and
  outdated admin/review material. Candidate 40 (`Defect, incorrect`) and
  candidates 45, 84–86 are alternate/duplicate teaching pages; compare with
  the selected current Fall pages before exclusion. Candidates 92 (`Exercise
  (cont.)`) and 98 (`Finding Faults`) have substantial content overlap with
  current PDF pages 63–64, so they need source/build review rather than
  automatic exclusion. Candidate 87 overlaps the selected crash/failure
  discussion. Candidate 99 is an alternate RIRP diagram. Candidate 108 is an
  unselected summary after the current PDF recap. The selected Fall PDF remains
  the content baseline; preserve only verified current content/build states.

The full numbered inventory and text scores are in the linked candidate-audit
CSVs. An image-only candidate can have a zero text score, and a high text
score can describe an obsolete duplicate; both require visual/source evidence.
The `.key` IWA records contain explicit effect markers, including
`apple:bc-appear`, `apple:appear`, `apple:dissolve`, and `apple:dropbuild`; the
Introduction package also contains an `apple:magic-move-implied-motion-path`
marker. In contrast, both generated PPTX files contain zero `<p:timing>` slide
records. LibreOffice therefore does not preserve those Keynote effects in the
current candidates. The [Introduction audit](batch-01-introduction-build-marker-audit.csv)
and [Fault/Error audit](batch-01-fault-error-build-marker-audit.csv) found 32
and 37 slide records with effect markers, respectively. These counts include
transition effects and do **not** equal the number of additional static
slides required. Grouping hints such as `By Paragraph`, `By Bullet Group`,
and `By Row`, plus text-based candidate slide/page matches, help locate the
source content but do not decode full Keynote build order. Inspect affected
source slides and reconstruct meaningful animation states as separate static
slides in build order. Do not claim the effects were preserved just because
their slide text was converted.

The locator currently links effect-marked records to these reference pages:

- Introduction: 2–6, 12, 14–17, and 25–30.
- Fault/Error: 2, 7, 12, 14, 19–21, 23, 26–27, 30, 32–33, 35, 37, 42, 60,
  64–65, 69–73, 75–77, and 79.

These are **review targets, not an expansion count or a final animation map**.
Some markers describe slide transitions; multiple records can point to the
same page; low lexical scores and image-heavy slides make some matches weak.
Resolve actual object grouping and sequence from the Keynote records before
creating cumulative static states.

## Next actions for this batch

1. Inspect all unmatched converted slides against Keynote order/build metadata
   to classify current
   pages, meaningful builds, stale slides, and duplicate records.
2. Resolve the low-confidence and image-heavy page matches against the source
   package and PDF. Record a final page/build disposition for every candidate.
3. Build the final ordered source/build map. Add a plain editable divider
   before each of the two source decks; use exact filenames and topic names.
4. Repair the confirmed diagrams, tables, text fit, image composition, and
   any further defects. Preserve notes where present and map all static build
   states to their source.
5. Assemble and audit the local final PPTX; only then import it into the
   shared Drive root. Read back native order/editability, export one paced
   Google PDF, and inspect every page before accepting Batch 1.

## Open questions and acceptance blockers

- Which unmatched converted slides represent meaningful build states, and
  which are stale/hidden Keynote records?
- Does each current Fall PDF exactly match its `.key` revision? The Introduction
  image discrepancy requires checking the package revision and embedded media.
- Which notes are present on the selected source slides, and does the planned
  package/assembly path retain them?
- Has every final Google-exported page been visually reviewed against the
  exact reference? **Not yet.** No final Batch 1 deck has been uploaded.
