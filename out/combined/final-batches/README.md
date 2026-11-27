# Final batch workspace

This folder holds the durable, compact maps and acceptance records for the
16 final course batches. The complete batch and topic boundaries are in
[`../BATCH_BOUNDARIES.md`](../BATCH_BOUNDARIES.md). Full-size working PPTX,
rendered PDFs, and disposable images stay in ignored `out/.build/` while a
batch is under construction; the accepted native Google Slides decks belong
in the shared Drive project root above `Pilots`.

## Required batch artifacts

Before a batch is accepted, its record must link to:

1. An ordered source/build map covering every source slide, every meaningful
   animation state, every generated static slide, and every required divider.
2. A final PPTX candidate and its local package/order diagnostics.
3. The final native Google Slides URL and structural readback.
4. The Google-exported PDF and a page-by-page visual review against the best
   available exact-revision source.
5. A concise repair log, open exceptions, and acceptance date.

Every original source deck in a final batch starts with one plain, editable
divider slide. Its text must give the exact source filename and the topic of
the slides that follow. The divider gets its own generated row in the map.
Do not split source decks, topics, or meaningful build sequences at batch
boundaries.

## Batch 1 current state

Batch 1 covers Week 1: Introduction and administrivia, followed by Faults,
Errors, and Failures. Its current maps are provisional alignment proposals,
not final output-page maps. They map each reference PDF page to a candidate
slide in the LibreOffice-generated PPTX. They do not yet decide which
unmatched slides are stale records, hidden Keynote content, or meaningful
animation/build states.

- [Batch 1 diagnostic and visual findings](batch-01-diagnostic.md)
- [Introduction reference-page candidates](batch-01-introduction-provisional-page-map.csv)
- [Introduction converted-slide audit](batch-01-introduction-candidate-audit.csv)
- [Introduction Keynote effect/build-marker audit](batch-01-introduction-build-marker-audit.csv)
- [Fault/Error reference-page candidates](batch-01-fault-error-provisional-page-map.csv)
- [Fault/Error converted-slide audit](batch-01-fault-error-candidate-audit.csv)
- [Fault/Error Keynote effect/build-marker audit](batch-01-fault-error-build-marker-audit.csv)

The corresponding PDFs are `slides/f26-pdfs/01-408st-introduction.pdf` and
`slides/f26-pdfs/02-408st-fault-error-failure.pdf`. Diagnostic PPTX files,
PDFs, and contact sheets are under ignored `out/.build/batch-01/` and must be
regenerated if that directory is cleared. The unmatched candidate contact
sheets are under `out/.build/batch-01/unmatched-review/`; the
[`render_unmatched_contact_sheets.py`](../render_unmatched_contact_sheets.py)
script regenerates them from the local diagnostic PDF and slide-audit CSV.
The Keynote package build-marker scan can be regenerated with
[`audit_keynote_build_markers.py`](../audit_keynote_build_markers.py); it is
only a locator and does not decode complete build order.
Nothing in this folder represents an uploaded or accepted final batch yet.

## Acceptance tracking

Add one record per batch here as it is completed. Do not label a batch
complete based only on a successful import, matching page count, or a text
alignment score. Acceptance requires visual inspection of every exported
Google PDF page and documented resolution of every flagged mismatch.
