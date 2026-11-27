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
- [Batch 1 input manifest](batch-01-inputs.json)

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
The provisional editable package can be assembled with
[`build_batch_candidate.py`](../build_batch_candidate.py), which adds the
required plain dividers, selects mapped reference-page candidates, and records
notes and build-marker hints. It explicitly leaves animation expansion and
remaining visual repair pending. The current ignored local candidate is
`out/.build/batch-01/assembled/batch-01-static-candidate.pptx`; its output map
and a local PDF render are in the same `out/.build/batch-01/` workspace. It has
111 baseline pages before any verified build expansion. The editable repair
for Introduction source page 2 is
[`repair_batch01_introduction.py`](../repair_batch01_introduction.py); it fixes
overlapping labels and the portrait collision and replaces a stale winter
phrase using the Fall 2026 syllabus. Its latest local render has readable body
text, aligned labels and values, and clear space around the portraits. A
separate one-slide Google Pilot confirms this local repair survives import and
renders cleanly. The full 111-page candidate has not been accepted. The
source-specific Fault/Error repair
is [`repair_batch01_fault_error.py`](../repair_batch01_fault_error.py). It
restores two pages of native table cells, repairs two editable video labels,
and uses diagram-only crops from the matching Fall PDF for three corrupted
connector diagrams. The current local 111-page candidate has been rendered;
these repairs match the references locally. The Introduction page 2 local
repair and the Fault/Error page 68, 36 pt label repair have also passed Google
PDF checks. Page 68's local-first import preserves the photo and fits both
labels on one line; the Google-first PDF loses the photo. The route decision
is therefore local-first by default, with native Google Slides repair as a
fallback for a slide family where the local roundtrip fails or performs worse.
See the tested evidence in the
[conversion runbook](../SLIDE_CONVERSION.md#repair-route-decision-local-first-default-google-first-fallback).
The provisional full batch remains unaccepted. The Introduction course schedule slide is user-owned:
leave it unchanged and continue other Batch 1 work; the user will make that
edit directly. It is not an agent repair blocker.
Nothing in this folder represents an uploaded or accepted final batch yet.

## Acceptance tracking

Add one record per batch here as it is completed. Do not label a batch
complete based only on a successful import, matching page count, or a text
alignment score. Acceptance requires visual inspection of every exported
Google PDF page and documented resolution of every flagged mismatch.
