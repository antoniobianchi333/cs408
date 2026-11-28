# Final batch workspace

This folder holds the durable, compact maps and acceptance records for the
16 final course batches. The complete batch and topic boundaries are in
[`../BATCH_BOUNDARIES.md`](../BATCH_BOUNDARIES.md). Full-size working PPTX,
rendered PDFs, and disposable images stay in ignored `out/.build/` while a
batch is under construction. Every full-size native Google Slides batch deck,
including a WIP deck that still needs fixes, belongs in the shared Drive root
above `Pilots`. Use a title such as `WIP - needs fixes` until acceptance;
reserve `Pilots` for small isolated test decks.

## Required batch artifacts

Before a batch is accepted, its record must link to:

1. An ordered source/build map covering every source slide, every meaningful
   animation state, every generated static slide, and every required divider.
2. A final PPTX candidate and its local package/order diagnostics.
3. The final native Google Slides URL and structural readback.
4. The Google-exported PDF and a page-by-page visual review against the best
   available exact-revision source.
5. A concise repair log, open exceptions, and acceptance date.

Every original source deck in a final batch starts with one full-slide, solid
pale-yellow (`#FFF2CC`) editable divider. Center the exact source filename in
24 pt bold Arial and the following topic in 28 pt regular Arial. Include
explicit rectangle geometry for the generated text boxes so Google Slides
retains them. The divider gets its own generated row in the map.
Do not split source decks, topics, or meaningful build sequences at batch
boundaries.

## Batch 1 current state

Batch 1 covers Week 1: Introduction and administrivia, followed by Faults,
Errors, and Failures. Its current maps are provisional alignment proposals,
not final output-page maps. They map each reference PDF page to a candidate
slide in the LibreOffice-generated PPTX. Keynote order/skip decoding shows the
30 and 79 unskipped slides map one-to-one, in order, to the two reference PDFs
and candidate slides. Other candidates are skipped in the Keynote slide tree.
The active slides' build chunks are decoded. Eleven of 52 build-bearing slides
are classified: Introduction PDF pages 2 and 3 have two and three cumulative
object states; pages 4 and 15 have 11 and 9 paragraph states; page 6 has seven
paragraph states; page 12 has a two-state AI-policy subtitle/list build; page
14 and 16 have one-chunk All at Once builds and need no extra state;
page 17 has a six-state banner-first, five-question build; page 18 has a two-state
article-image then editable-headline build; page 27 has three cumulative
paragraph states. The original 37 states across six slides passed local review,
native Google readback, and page-by-page PDF review. The five states on pages
2–3 and three states on page 27 passed the Round 28 native Google pilot
readback and page-by-page PDF review. Round 29 then repaired and checked output
pages 2 and 64 in the full native WIP. The other 41 build-bearing slides need
classification.

- [Batch 1 diagnostic and visual findings](batch-01-diagnostic.md)
- [Introduction reference-page candidates](batch-01-introduction-provisional-page-map.csv)
- [Introduction converted-slide audit](batch-01-introduction-candidate-audit.csv)
- [Introduction Keynote effect/build-marker audit](batch-01-introduction-build-marker-audit.csv)
- [Introduction Keynote slide/build sequence](batch-01-introduction-build-sequences.csv)
- [Fault/Error reference-page candidates](batch-01-fault-error-provisional-page-map.csv)
- [Fault/Error converted-slide audit](batch-01-fault-error-candidate-audit.csv)
- [Fault/Error Keynote effect/build-marker audit](batch-01-fault-error-build-marker-audit.csv)
- [Fault/Error Keynote slide/build sequence](batch-01-fault-error-build-sequences.csv)
- [Batch 1 input manifest](batch-01-inputs.json)
- [Build-state decisions and chunk map](batch-01-build-expansion.json)
- [Round 28 native Google pilot source/build map](batch-01-round28-google-pilot-map.csv)

The corresponding PDFs are `slides/f26-pdfs/01-408st-introduction.pdf` and
`slides/f26-pdfs/02-408st-fault-error-failure.pdf`. Diagnostic PPTX files,
PDFs, and contact sheets are under ignored `out/.build/batch-01/` and must be
regenerated if that directory is cleared. The reusable
[`expand_batch_build_states.py`](../expand_batch_build_states.py) creates
cumulative paragraph or object-visibility states from the manifest above.
The current ignored 147-page local candidate is
`out/.build/batch-01/round29/rebuild-v2/batch-01-expanded-candidate.pptx`; its
output map is `out/.build/batch-01/round29/rebuild-v2/batch-01-expanded-map.csv`.
It was rebuilt from the repaired source packages and 111-page base, then
expanded with the page 2, page 3, and page 27 sequences. The new states place
the second source-deck divider at local output page 68; the existing WIP still
has it at page 63. The PPTX is 39,494,683 bytes (SHA256
`5e12bceca939cb6dbda4baf7a7ca616e0955786e7ba9afe2359fcc761ce4e9e0`).
The page 18 article image/headline reconstruction was applied before expansion,
using the unrepaired converted Introduction PPTX as the source for its editable
headline; the source-repair package does not retain that separate text shape.
Nine source slides expand to cumulative states; the manifest records every
source slide, state, chunk ID, and visibility operation. Page 27 adds two net
slides to the prior 145-slide candidate. The 147-row output map is consecutive
and the PPTX has 147 ordered slide references, all resolving to existing slide
parts; ZIP integrity passes. Its local diagnostic PDF has 147 pages and is
28,501,659 bytes, SHA256
`06748e758845faf5f28695da2c43d8059e8183dbded3ed2e5e13b3064a1927d4`. Pages
62–64 were inspected against the exact Fall Introduction PDF. The missing bullet
glyph, heading/body sizes, indentation, line spacing, and editable cumulative
progression were checked. Linux LibreOffice substitutes Source Sans Pro with
Liberation Sans and changes some line wraps. The Round 28 native Google PDF
showed the expected three-paragraph progression with editable 36 pt body text.
The full WIP still needs the structural update and complete-batch visual review.
The Google WIP has not been replaced by this regenerated candidate. The full
expanded deck in Drive is the
[142-slide WIP Batch 1 deck](https://docs.google.com/presentation/d/1EYXO-ZvBcLhUg9-JdA0t6C78sSx6Ki-4OGnIeYM9IME/edit).
Native outline readback confirmed 142 ordered slides. The latest Google PDF
export has 142 pages, is 5,299,986 bytes, and has SHA256
`fb172ef445e150960d683aa3b01cfcfeba5f627ceb2c0172eefde5168359e2c2` at native
revision `mEV_c_nCguc_IQ`. Round 29 repaired output pages 2 and 64 in that same
deck. Its fresh PDF was visually checked against the exact Fall cover pages.
Six WIP pages are confirmed repaired (about 4%); full-size review has not
counted all remaining defects. Contact sheets have been reviewed for all
pages, but the deck is not accepted. The user set the Google Drive plugin to
“Allow all tools”; no approval is pending, and project operations remain
limited to the CS 408 folder. The two source-deck dividers were blank on the first import
because their generated DrawingML text boxes lacked explicit rectangle
geometry. A two-slide Google pilot confirmed that adding `a:prstGeom` retains
both editable labels. The WIP now uses a solid pale-yellow `#FFF2CC`
background, 24 pt bold Arial filenames, and 28 pt regular Arial topics.
Output pages 24–25 (Introduction PDF pages 7–8) now use the source's 80 pt
Source Sans Pro title and 66 pt Bebas Neue table text, centered vertically.
Page 24 uses corrected 92/92/77/92/92 pt rows. A two-slide PPTX import pilot
rev2 confirmed the table font, sizes, row heights, and MIDDLE cell alignment;
the title maps to Arial on import, so the full WIP received a native
Source Sans Pro edit. See the [Round 25 log](../SLIDE_CONVERSION.md#round-25--batch-1-course-grading-table-typography).
The latest full Google PDF from Round 25 is saved under
`out/.build/batch-01/round24-grading-cell-style/`; regenerate it from Google
Drive if the ignored `.build` directory is absent. The newly regenerated local
diagnostic PDF is `out/.build/batch-01/assembled/batch-01-expanded-candidate.pdf`.
Pruned
11-slide,
7-slide, 2-slide, 9-slide, 6-slide, and two 2-slide state subsets were imported
as native Google pilots and verified; see the [Round 18](../SLIDE_CONVERSION.md#round-18--batch-1-introduction-paragraph-build-pilot),
[Round 19](../SLIDE_CONVERSION.md#round-19--batch-1-course-grading-paragraph-build-pilot),
[Round 20](../SLIDE_CONVERSION.md#round-20--batch-1-course-objectives-paragraph-build-pilot),
 [Round 21](../SLIDE_CONVERSION.md#round-21--batch-1-introduction-mixed-bannerquestion-build),
[Round 22](../SLIDE_CONVERSION.md#round-22--batch-1-introduction-page-18-imageheadline-build),
and [Round 23](../SLIDE_CONVERSION.md#round-23--batch-1-introduction-page-12-ai-policy-build)
records. The
[`prune_pptx_slides.py`](../prune_pptx_slides.py) utility creates compact
editable pilot packages from selected slide ranges while retaining referenced
layouts, media, notes, and other package relationships.
The page 18 asset reconstruction is reproducible with
[`prepare_intro_page18_build.py`](../prepare_intro_page18_build.py); it uses
the TIFF stored in the Keynote package and restores the headline as editable
text before the two slide states are pruned.
The unmatched candidate contact
sheets are under `out/.build/batch-01/unmatched-review/`; the
[`render_unmatched_contact_sheets.py`](../render_unmatched_contact_sheets.py)
script regenerates them from the local diagnostic PDF and slide-audit CSV.
The raw effect-marker locator can be regenerated with
[`audit_keynote_build_markers.py`](../audit_keynote_build_markers.py); it is
only a locator and does not decode complete build order. The structural slide
order, skip flags, build archives, and playback-ordered build chunks can be
regenerated with
[`audit_keynote_build_sequences.py`](../audit_keynote_build_sequences.py),
using the page maps in ignored `.build/batch-01/` to check sequence alignment.
The provisional editable package can be assembled with
[`build_batch_candidate.py`](../build_batch_candidate.py), which adds the
required pale-yellow editable dividers with explicit text-box geometry,
selects mapped reference-page candidates, and records
notes and build-marker hints. It explicitly leaves animation expansion and
remaining visual repair pending. The current ignored local candidate is
`out/.build/batch-01/assembled/batch-01-static-candidate.pptx`; its output map
and a local PDF render are in the same `out/.build/batch-01/` workspace. It has
111 baseline pages before build expansion. The editable repair
for Introduction source page 2 is
[`repair_batch01_introduction.py`](../repair_batch01_introduction.py); it fixes
overlapping labels and the portrait collision and replaces a stale winter
phrase using the Fall 2026 syllabus. Its latest local render has readable body
text, aligned labels and values, and clear space around the portraits. A
separate one-slide Google Pilot confirms this local repair survives import and
renders cleanly. The same repair script now fixes Introduction source page 17:
the editable poll banner and title, question wrapping, visible bullets, and
line spacing. In the rebuilt candidate, source PDF page 17 is output page 18;
output page 18 was visually compared with the reference and matches closely.
A one-slide Google pilot confirmed the local question list/banner import and
editable text, then native fallback edits corrected the title sizing and the
custom border's dotted style. That pilot's final Google PDF is one page and
39,981 bytes; the integrated local title fix still needs verification in the
full-batch import. The pilot is
[in the shared Pilots folder](https://docs.google.com/presentation/d/1Gat0ZLl5w5iSrU4tDtZOgEEwQnvEIANW3pUV2vsqw48/edit).
The following repair details record local checks on the pre-expansion
111-page baseline; the active full-size Google WIP is the 142-slide deck
summarized above. The source-specific Fault/Error repair
is [`repair_batch01_fault_error.py`](../repair_batch01_fault_error.py). It
restores two pages of native table cells, repairs two editable video labels,
and uses diagram-only crops from the matching Fall PDF for three corrupted
connector diagrams. At that stage, the 111-page pre-expansion baseline was
rendered and these repairs matched the references locally. The Introduction page 2 local
repair and the Fault/Error page 68, 36 pt label repair have also passed Google
PDF checks. Page 68's local import preserves the photo and fits both labels on
one line; the Google-first PDF loses the photo. These paired trials support
local source repairs for these specific content and media defects. The full
native Google WIP is the live surface for confirmed visual-only fixes after
upload; make those fixes in the same presentation. Rebuild and reconcile the
local PPTX when content, media, build states, order, or structure changes, or
when a local repair is needed to preserve the intended result through import.
See the tested evidence in the
[conversion runbook](../SLIDE_CONVERSION.md#repair-route-decision-local-source-repairs-in-place-google-wip-edits).
The 111-page baseline candidate was rebuilt after this 36 pt update, and
its local output page 100 in the pre-Round27 candidate (now page 102) was
reviewed with the photo and both labels visible. Output page 18 (Introduction
page 17) and page 102 have both been checked in the rebuilt local PDF. These
were checks of the reproducible source candidate.
The separate 142-slide WIP has since been uploaded to the shared Drive root
and remains unaccepted.
The Introduction course schedule slide is user-owned:
leave it unchanged and continue other Batch 1 work; the user will make that
edit directly. It is not an agent repair blocker.
There is no accepted final batch yet; Batch 1's full-size WIP is in Drive.

## Acceptance tracking

Add one record per batch here as it is completed. Do not label a batch
complete based only on a successful import, matching page count, or a text
alignment score. Acceptance requires visual inspection of every exported
Google PDF page and documented resolution of every flagged mismatch.
