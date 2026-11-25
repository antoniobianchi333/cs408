# Pilot files

This folder holds pilot-only artifacts: small conversion rounds, full-size
comparison imports such as Round 4, revisions, local PDFs, Google exports,
slide maps, rebuild scripts, and local audit scripts. Keep the inputs and
evidence for each round together here. Put temporary renders and transfer
scratch files in `out/.build/` instead of this folder.

Final-candidate batch PowerPoints stay directly in `out/combined/`, beside
the full collection PDF and source maps. The batch manifest is
[`../editable-parts-manifest.json`](../editable-parts-manifest.json). Do not
put final batch PowerPoints in this pilot folder.

## Google Drive organization

The user's shared CS408 folder is
[the Drive root for this project](https://drive.google.com/drive/folders/16vTRNocHa1rlPN1bii_w0b8Ce90XrFbn).
Keep pilots and disposable API/edit tests in its [`Pilots` subfolder](https://drive.google.com/drive/folders/1PHuKHahwY2PxviNWTM2f8kYmb7K-37Dj).
Upload final batch decks directly to the shared folder root, not to `Pilots`.
As of November 24, 2026, all 17 presentations previously listed at the shared
root were pilot/test decks and have been moved into `Pilots`; the shared root
is reserved for final batches.

## Future rounds

1. Build and inspect a pilot locally under this folder, with a source page map.
2. Import it into Google Slides with a title that includes the round and
   revision, then keep its native URL and Google PDF evidence in the runbook.
3. Keep disposable live-edit tests in `Pilots` and restore them after testing.
4. Keep API calls serial and paced as described in
   [`GOOGLE_DRIVE_ACCESS.md`](../GOOGLE_DRIVE_ACCESS.md).
5. Do not promote a pilot to a final batch until its source selection,
   slide order, editability, and Google PDF visual review are recorded.

## Round 12 technical pilot: Test Case Minimization supplement

Round 12 revision 2 reconstructs older Test Case Minimization PDF pages 38–41
(combined slides 840–843) as four editable slides. The
[PPTX](cs408-tcm-supplement-round12-rev2.pptx),
[Google PDF](cs408-tcm-supplement-round12-rev2-google.pdf),
[page map](cs408-tcm-supplement-round12-rev2-map.csv), and
[rebuild script](rebuild_tcm_supplement_round12.py) are here; the native
Google Slides result is linked in the
[runbook](../SLIDE_CONVERSION.md#round-12--editable-test-case-minimization-supplement).
Visual review found unsupported Unicode `n` and `j` subscripts in rev1;
rev2 uses DrawingML subscript formatting and passed the four-page Google
render review. The older Spring Keynote is unavailable, so its source
notes/builds are not part of this reconstruction.

## Current scale pilot: Part 2 rev3

The current large pilot is the 232-slide
[`Part 2 rev3 PPTX`](cs408-editable-part-02-scale-rev3.pptx), imported as
[native Google Slides](https://docs.google.com/presentation/d/1OTrLWNKqwFOokESPsZuoBoqWI6Qjm-7IxiSmsa0f50I/edit).
Its [Google PDF](cs408-editable-part-02-scale-rev3-google.pdf),
[page map](cs408-editable-part-02-scale-rev3-map.csv), and
[232-page visual-diff report](cs408-editable-part-02-scale-rev3-visual-diff.csv)
are the acceptance evidence. The 70% white shape fills on slides 214 and 216
restore contrast while leaving body text editable. The corresponding
[repair script](repair_part02_contrast_panels.py) starts from rev2 and emits
rev3 plus its map. Two comparison images are retained for the affected slides.

The verified export helper's no-curl transfer recipe and the Google readback
are in [`GOOGLE_DRIVE_ACCESS.md`](../GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf).
Temporary full-deck page renders stay in `out/.build/`; keep the PDF, PPTX,
source map, diff report, repair script, and reviewed target comparisons here.

## Round 13: Fall Lab 1 fuzzing tutorial

Round 13 is a content-selection and conversion pilot for the Fall 2026 Lab 1
fuzzing tutorial. It imports the complete `labs/lab1/slides/intro.pptx` source
(40 pages) as 62 static Google Slides. Source slides 6, 7, and 8 each contain
sequential paragraph reveal timing; the builder expands them into 8, 6, and
11 cumulative states. Source slides 35–36 form an additional inferred AFL
screenshot zoom sequence: their text is identical, while slide 36 adds a
full-slide image over the thumbnail. No `p:timing` metadata is present for
that pair, so the map explicitly records the inference and preserves both
source pages in order.

- [Editable PPTX](cs408-fall-project-1-pilot-round13.pptx)
- [Native Google Slides deck](https://docs.google.com/presentation/d/1wHRFaaLfwfrOnY_fKJbG69xQf9x0Yql47D6ZFCoZb7g/edit)
- [Google-rendered PDF](cs408-fall-project-1-round13-review/presentation.pdf)
- [62-row source/build map](cs408-fall-project-1-pilot-round13-map.csv)
- [Builder](build_fall_lab1_pilot_round13.py)
- [62-page contact sheets and renders](cs408-fall-project-1-round13-review/)

The package audit confirmed 62 ordered slides, 62 linked note slides, no
residual PowerPoint animation timing, current title/admin updates, and an
exact map row for every output slide. Google readback confirmed 62 ordered
slides, editable text and native objects, and speaker notes on both a static
slide and an expanded build slide. All 62 Google PDF pages were visually
reviewed. Slide 2 follows the Fall handout's Oct 30 deadline, while the current
syllabus table says Nov 3; keep this discrepancy visible for resolution before
final integration. The prior 43-page Spring Lab 2 tutorial is comparison-only
because Fall has the newer complete lab/fuzzing topic.

## Round 14: concurrency-testing lab introduction

Round 14 tests the complete older concurrency-testing lab introduction at
`labs/lab1-archive/slides/lab1_intro.pptx`. It is a separate supplemental
topic retained in the Fall study guide, not the current Fall fuzzing project.
The [native Google deck](https://docs.google.com/presentation/d/1tAObwDTGc_EJ6aD4nXIceRTPjc3vF63hOPDdxFdZ0WE/edit)
has 28 slides in source order. The Google PDF, source PPTX's local diagnostic
PDF, and 28-page contact sheets are in the
[review folder](cs408-concurrency-lab-intro-round14-review/); the
[one-to-one source map](cs408-concurrency-lab-intro-round14-map.csv) records
all slides. No source notes or timed animations were present. This direct PPTX
import showed no repair-worthy layout defect. The source contains February
2026 course-specific GitHub Classroom and assignment details; check these
against the preserved handout and study-guide pages before final integration.
The due date and assignment URL match the Spring 2026 handout, but screenshots
on slides 4–6 still show `CS503 Spring 2021` and old assignment screens. Update
or label those screenshots as archival before final integration.
