# CS 408 combined slide collection

[Output index](../README.md) · [Conversion runbook](SLIDE_CONVERSION.md) ·
[Google Drive access](GOOGLE_DRIVE_ACCESS.md) ·
[Pilot folder guide](google-slides-pilot/README.md)

The source inventory contains 2,235 visible slides from 57 Spring-centered
candidate decks. It is the comparison baseline, not the final selection.
Content selection is closed for all 57 candidates: use Fall's complete source
wherever Fall covers a topic and include older material only as a complete
topic absent from Fall. Keep older material within a Fall-covered topic as
comparison/provenance evidence, not as isolated supplements. Final source/build
maps are being made batch by batch.
Keep durable scripts, manifests, maps, and compact QA reports in this folder.
Generated PPTX/PDF/render files belong under ignored `out/.build/`; older
round logs may record local artifact paths that are not present in a fresh
checkout. Full-batch native Google Slides decks belong in the shared Drive
root, and small live tests belong in `Pilots`.
For the newer reading and exercise sequence, see the
[Fall 2026 study guide](../README.md#fall-2026-study-guide).

Current older-topic decisions and their evidence are recorded in the
[older-topic selection audit](older-topic-selection-audit.csv). The audit
records final whole-topic choices and exclusions. Six older-only slide units
are selected: the concurrency-testing lab introduction, Verified Distributed
Systems, Semantic/Latent Concurrency Bug Detection, Record and Replay,
Deterministic Execution, and Static Testing Tools. Conversion and source/build
mapping remain to be completed in their assigned batches.

## Test the editable import first

The Round 4 PPTX is the historical full Part 1 comparison baseline; its local
PPTX/PDF artifacts may be absent from a fresh checkout. The recorded Google
export had 260 pages. Rounds 5–11 tested targeted repairs in smaller native
decks. Round 11 revision 4 is the latest label-fit repair:
Round 11 PPTX (recorded local artifact: `google-slides-pilot/cs408-conversion-pilot-round11-rev4.pptx`; may be absent from this checkout),
with its Google PDF (recorded local artifact: `google-slides-pilot/cs408-conversion-pilot-round11-rev4-google.pdf`; may be absent from this checkout)
and [three-page map](google-slides-pilot/cs408-conversion-pilot-round11-rev4-map.csv).
It repairs the split `Program Text`, `CFG`, `true`, and `false` labels on
combined slides 115–116 while preserving their original fonts and editable
objects. Slide 114 is an unchanged control and matches the Round 4 Google
export pixel for pixel at 120 dpi. The [native Google deck](https://docs.google.com/presentation/d/1iov7hGZMI1BnyVNWcwwvG-XxcslA4qJCMzatqMORMSA/edit)
has the three mapped slides in order. The
[conversion runbook](SLIDE_CONVERSION.md#round-11--cfg-label-fit-with-original-fonts)
records the revisions, local font-substitution caveat, repair rule, API
readback, and remaining work.

Round 16 completed its diagnostic `.key` repair pilot. Google readback confirms
38 ordered native slides, editable objects, and notes on every page. All 38
pages have close visual review; the final 38-page Google PDF is 5,101,352
bytes and is saved with refreshed contact sheets, the page map, and a slide
25 comparison. Repairs preserve native content except for diagram-only image
patches on slides 4–5. The local audit passes package/order/PDF/text checks
and confirms slide 6 is unchanged against the Round 15 baseline. The September
PDF predates the October Keynote revision; newer content on slides 6 and 21 is
kept. See the
[Round 15 baseline](SLIDE_CONVERSION.md#round-15--fall-test-anatomy-linux-keynote-diagnostic),
[Round 16 review](SLIDE_CONVERSION.md#round-16--test-anatomy-repairs-and-google-review),
and [PDF coverage audit](SLIDE_CONVERSION.md#fall-pdf-coverage-and-keynote-preview-limits).

Round 14 is the latest older-topic conversion pilot: it imports the complete
28-slide archived concurrency-testing lab introduction. The [native deck](https://docs.google.com/presentation/d/1tAObwDTGc_EJ6aD4nXIceRTPjc3vF63hOPDdxFdZ0WE/edit),
[Google PDF and contact sheets](google-slides-pilot/cs408-concurrency-lab-intro-round14-review/),
and [slide map](google-slides-pilot/cs408-concurrency-lab-intro-round14-map.csv)
record the result. Google readback found 28 slides in order; all 28 rendered
pages were visually reviewed against a diagnostic render of the source PPTX.
The source has no speaker-note parts or timed animation. It is an older
supplemental topic, separate from the current Fall fuzzing project. Content
review found the screenshots on slides 4–6 still show a `CS503 Spring 2021`
context; update or clearly label them as archival in the final selected copy.

Round 13 remains the latest Fall source-selection/conversion pilot: it imports the
complete Fall Lab 1 tutorial (40 source slides) into a 62-slide native Google
deck. The [native presentation](https://docs.google.com/presentation/d/1wHRFaaLfwfrOnY_fKJbG69xQf9x0Yql47D6ZFCoZb7g/edit),
PPTX (recorded local artifact: `google-slides-pilot/cs408-fall-project-1-pilot-round13.pptx`; may be absent from this checkout),
62-page Google PDF (recorded local artifact: `google-slides-pilot/cs408-fall-project-1-round13-review/presentation.pdf`; may be absent from this checkout),
[source/build map](google-slides-pilot/cs408-fall-project-1-pilot-round13-map.csv),
and [builder](google-slides-pilot/build_fall_lab1_pilot_round13.py) are kept
in the pilot folder. Native readback confirmed 62 ordered slides. Speaker
notes were cloned in the local package and read back from one static slide and
one expanded-state slide. All 62 Google-rendered pages were inspected. The
map expands 8/6/11 paragraph-reveal states and identifies the separate AFL
screenshot zoom sequence on source slides 35–36. Slide 2 follows the Fall
handout's Oct 30 date; the syllabus table says Nov 3, so retain that conflict
for resolution before final integration.

Round 12 revision 2 remains a technical conversion pilot: it reconstructs
four older Test Case Minimization pages (combined slides 840–843) as editable
text and equations. These pages are not selected for final content because
Fall supplies the complete topic. Its PPTX (recorded local artifact: `google-slides-pilot/cs408-tcm-supplement-round12-rev2.pptx`; may be absent from this checkout),
Google PDF (recorded local artifact: `google-slides-pilot/cs408-tcm-supplement-round12-rev2-google.pdf`; may be absent from this checkout),
[page map](google-slides-pilot/cs408-tcm-supplement-round12-rev2-map.csv),
[builder](google-slides-pilot/rebuild_tcm_supplement_round12.py), and
[native Google deck](https://docs.google.com/presentation/d/1QBFgfPtlkF_UIgBuuiFzmf12lk3Kg3CJ8GheASBtBdM/edit)
are documented in the [Round 12 log](SLIDE_CONVERSION.md#round-12--editable-test-case-minimization-supplement).
Readback confirmed four slides with native shape text and no images. The PDF
review caught and fixed missing Unicode letter subscripts before acceptance.

Native text edit/readback has been verified on a disposable Round 10 copy and
on the requested Round 4 deck. A reversible line-position edit/readback also
passed on a disposable copy of Round 11 revision 4; Google's line-style
update was rejected for that imported arrow. These results are object- and
operation-specific. See the Google Drive guide's records for
[text edits](GOOGLE_DRIVE_ACCESS.md#verified-live-text-edits) and
[native vector edits](GOOGLE_DRIVE_ACCESS.md#verified-native-vector-object-edit).

Run the [local pilot audit script](google-slides-pilot/audit_conversion_pilot.py)
after each round. It verifies ZIP relationships, map/order agreement, control
XML, PDF page counts, requested text, and optional baseline pixel equality.
It is local-only; manually inspect every repaired slide in the Google PDF.

The Part 2 scale pilot contains combined slides 261–492 in order. The
[rev3 native Google deck](https://docs.google.com/presentation/d/1OTrLWNKqwFOokESPsZuoBoqWI6Qjm-7IxiSmsa0f50I/edit)
passed 232-slide order readback. Its Google PDF (recorded local artifact: `google-slides-pilot/cs408-editable-part-02-scale-rev3-google.pdf`; may be absent from this checkout)
was exported and materialized without curl; page-by-page comparison shows
only the intended repairs on local slides 214 and 216 differ from rev2.
Their editable text shapes now restore the source's translucent white panels.
The [rev3 map](google-slides-pilot/cs408-editable-part-02-scale-rev3-map.csv)
and [visual-diff report](google-slides-pilot/cs408-editable-part-02-scale-rev3-visual-diff.csv)
are preserved with the pilot. See the
[Drive transfer guide](GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf)
for the no-curl method. This and all other pilot decks live in the Drive
`Pilots` subfolder; final batch decks belong at the shared folder root. See
the [pilot folder guide](google-slides-pilot/README.md).

The [first pilot's slide map](google-slides-pilot/slide-map.csv) identifies
the original 16 selected pages and their lecture sources. The runbook
records where the user inserted a slide in Round 1 and the page maps for
later pilots. Round 9's [map](google-slides-pilot/cs408-conversion-pilot-round9-map.csv)
identifies its two controls and four repaired diagrams. Use those maps
whenever the Google export has a different slide range from the collection.
Round 10's original three-page map applies to revision 2; its
[revision 6 map](google-slides-pilot/cs408-conversion-pilot-round10-rev6-map.csv)
adds slide 153 as the unchanged control. Round 11 revision 4's map covers
slides 114–116; earlier revision maps remain beside their diagnostic PPTX and
PDFs. Use the map for the exact revision being inspected.

## Map a slide to its source and artifacts

1. Use the combined slide number as the stable reference. One-based page
   230 of the combined PDF (recorded local artifact: `cs408-all-slides.pdf`; may be absent from this checkout) is combined slide 230.
   In a pilot with gaps, look up the combined number in that round's
   ordered page map before comparing renders.
2. Find the row with `first_slide <= number <= last_slide` in
   [sources.csv](sources.csv) or [sources.json](sources.json). The position
   within the visible source deck is `number - first_slide + 1`.
   Use that position to look up the saved build in `visible_indices`
   when present. The corresponding `original_pdf_page_flags` value
   indicates whether the combined page reused the paired PDF's original
   export. Open the matching reference slide to confirm the build,
   especially if the combined PDF already shows an issue.
3. For a legacy combined-slide mapping, find the parent part in the
   [editable manifest](editable-parts-manifest.json). The Round 4 PPTX is the
   old Part 1 comparison baseline; it is not the current Batch 1 candidate.
   For the 16-batch project, use
   [BATCH_BOUNDARIES.md](BATCH_BOUNDARIES.md) and
   [final-batches/README.md](final-batches/README.md). Keep temporary local
   batch PPTX candidates and renders in ignored `out/.build/batch-NN/`;
   persistent scripts, maps, and repair rules belong in Git. The full native
   WIP or accepted batch deck belongs in the shared Google Drive root above
   `Pilots`.

From the repository root, the following lookup returns the original
source and batch for combined slide 230.

```sh
slide=230
jq --argjson slide "$slide" '
  .[] | select(.first_slide <= $slide and $slide <= .last_slide)
  | ($slide - .first_slide) as $offset
  | {source, source_kind, paired_pdf, visible_page: ($offset + 1),
     keynote_index: .visible_indices[$offset],
     reused_original_pdf: .original_pdf_page_flags[$offset]}
' out/combined/sources.json
jq --argjson slide "$slide" '
  .[] | select(.first_slide <= $slide and $slide <= .last_slide)
  | {file, first_slide, last_slide}
' out/combined/editable-parts-manifest.json
```

Keep each pilot's PPTX, available local render, Google PDF, and page map together.
Rounds 5–7 use the stem `cs408-conversion-pilot-roundN` with the PDF
suffixes `-linux.pdf` and `-google.pdf`. Keep older filenames as written
in the logs so their links resolve. Round 8 keeps both the first Google
render, which exposed two repair issues, and the corrected `-rev2` files.
Its [page map](google-slides-pilot/cs408-conversion-pilot-round8-map.csv)
applies to both revisions. Round 9 retains its first failing import and the
revised `-rev4` PPTX and Google PDF. Its page map applies to every revision.
Round 10 keeps maps for its three-page diagnostic and the final four-page
revision because the control selection changed. The
[rebuild script](google-slides-pilot/rebuild_conversion_pilots.py) reproduces
the selected slides and prints their combined numbers in order.
Use the [conversion and comparison instructions](SLIDE_CONVERSION.md)
when adding a new test and the [Drive guide](GOOGLE_DRIVE_ACCESS.md)
to create its native deck and download its Google render.

## Available PowerPoints

- This `combined/` folder contains nine editable PowerPoints in course order,
  split at lecture boundaries. The [manifest](editable-parts-manifest.json)
  maps each file to its original slide range. These are the baseline batches,
  each with at most 275 slides. The Round 3 and Round 4 repairs are in their
  own Part 1 files under `google-slides-pilot/`, alongside the smaller
  tests for Rounds 5–11. Each existing boundary falls after a complete source
  deck; future upload blocks must also keep complete topics together, so the
  final block sizes may differ from these baseline files.
- The full editable PowerPoint (recorded local artifact: `cs408-all-slides-editable.pptx`; may be absent from this checkout) contains
  the same 2,235 slides in one file.
  Text and shapes from Keynote are editable. The three PDF-supplied decks use
  page images. The combined file is about 87 MB, but each smaller batch is
  easier to check and retry.
- The image-based Part 1 (recorded local artifact: `cs408-google-slides-part-1.pptx`; may be absent from this checkout) and
  Part 2 (recorded local artifact: `cs408-google-slides-part-2.pptx`; may be absent from this checkout) use a single image per slide. Import them
  separately if the task calls for the image-based edition. For editable
  conversion, use the runbook's object-level repair and fallback process.
  [The image-based manifest](import-parts.json) records the ranges and sizes. The
  single image-based `cs408-all-slides.pptx` is about 117 MB, above Google's
  [100 MB conversion limit](https://support.google.com/drive/answer/37603?hl=en).
- The combined PDF (recorded local artifact: `cs408-all-slides.pdf`; may be absent from this checkout) is the full visual reference
  with 57 deck bookmarks. The source manifests above record the
  corresponding files and slide ranges.

Google's [PowerPoint-to-Slides guide](https://support.google.com/docs/answer/9310378)
describes importing and converting PowerPoint files.

## Source selection and conversion

Use the newest available version of each topic as the primary source. Apply a
whole-topic rule: use the complete Fall source for every topic Fall covers,
and add a complete older topic only when Fall does not cover it. Do not append
isolated older slides, examples, criteria, or case studies to a Fall-covered
topic. Record older sources in the crosswalk as provenance and comparison
evidence. Content selection is complete; do not redo it. The current 2,235-
slide map is Spring-centered, but the 57-row audit records final use/exclude
decisions. The initial pass maps all 57 candidate deck entries to Fall sources
in the
[source-deck topic audit](source-deck-topic-audit.csv): 44 by exact basename,
12 by topic/renumbering, and the remaining 43-page Spring Lab 2 tutorial to
Fall Lab 1 plus Fall fuzzing sources. The Fall Lab 1 tutorial is now imported
and visually reviewed; its expanded builds, notes, and screenshot zoom are
mapped in the Round 13 source map. Treat the Spring tutorial as superseded and
comparison-only. The older syntax-based-testing decks (combined slides
1222–1318) are now excluded after review: Fall Fuzzing and Mutation Testing
cover their main grammar and program-mutation lessons; older grammar-coverage
criteria are isolated additions. The source-deck audit now records use/exclude
outcomes for all 57 entries. It selects the latest available Final Review
deck with Fall-syllabus repairs; includes full older Verified Distributed
Systems and Semantic/Latent Concurrency Bug Detection units; and excludes the
older mixed Regression/Integration and Fall 2025 Review decks whole. Exact
source/build maps and conversion remain open. The separate
[older-topic selection audit](older-topic-selection-audit.csv) now records
candidate complete older units and their current decisions; Round 14 tested
the concurrency-testing lab introduction as a complete 28-slide import.
Record/replay, deterministic execution, static-testing tools, verified
distributed systems, semantic/latent concurrency-bug detection, and the
archived concurrency lab are selected as complete older-only units. The Fall
Final Review still needs its May 8 and HW3–5 administrative details replaced
using the current syllabus. The mixed Regression/Integration deck and its
17-page `Integration Testing Bad` draft are excluded in favor of the complete
Fall Test Anatomy and Regression Testing sources. The reproducible first-pass mapper is
[audit_source_deck_topics.py](audit_source_deck_topics.py).
The initial pass
identifies Fall-specific changes to Introduction policies, grading, schedule,
and learning objectives. The Spring Keynote source has the incorrect label
“Therac-35,” while its paired PDF page 27 scans Nancy Leveson's Therac-25
article; Fall's complete Introduction contains no Therac example. Omit the
isolated scan and generic casualty transition, keeping the mismatch as
provenance only. Older slides 29–34 are not added to Fall Fault/Error/Failure
or Regression Testing. Fall Test Anatomy is the complete selected source; do
not append the older 1979–1980 overview. Older slides 1831–1838 are JPL
LOC-1–LOC-6 coding-standard excerpts for Mars Science Laboratory flight
software, not Mars Climate Orbiter code; slides 1839–1840 show Clang/cppcheck.
Fall also has a current Static Analysis Keynote. The Fall
`22-408st-static-analysis.key` exists, but its PDF export is absent from the
20-PDF set; three agenda-slide variants still mention April 24 Project 2/HW5
deadlines. Replace them with Fall values (HW6: Dec 4 at 6 PM; Project 2: Dec
6). Export and inspect the complete Fall Static Analysis source; do not append
older examples individually. The candidate audit explicitly excludes row 24,
`03-408st-fault-error-failure`: it is an older Fall 2025 version superseded
by the complete Fall 2026 source in `02-408st-fault-error-failure.key` and
its PDF. See the
[Static Analysis review](SLIDE_CONVERSION.md#static-analysis-and-coding-standards-source-review).
Fault/Error/Failure adds an ordered program-state
modeling sequence in Fall PDF pages 31–62, then updated RIPR/revealability and
other builds through page 78; its older 2025 candidate section mostly repeats
material present in Fall 2026. The selected source decisions are recorded in
the [source-deck audit](source-deck-topic-audit.csv) and
[older-topic audit](older-topic-selection-audit.csv). Use the candidate
[Fall 2026 crosswalk](source-version-crosswalk.csv) for page-level provenance
and source mapping; slide/build reconciliation is still open. The 20
referenced PDFs (956 pages) are present in the current
checkout at `slides/f26-pdfs/`, because this branch is based on Fall 2026. The
matching Keynote decks are under `slides/`; 57 Keynote files are listed in
[fall-keynote-inventory.csv](fall-keynote-inventory.csv). The PDFs' validated
page counts and metadata are in
[fall-source-metadata.csv](fall-source-metadata.csv). If a future checkout
does not contain the source branch files directly, extract only the required
sources from the current Fall base with:

```sh
git archive --format=tar HEAD slides/f26-pdfs slides/01-408st-introduction.key | tar -xf - -C out/.build/fall-source
```

The [branch blob comparison](source-branch-diff-audit.csv), generated by
[audit_source_branch_diffs.py](audit_source_branch_diffs.py), compares each
candidate's recorded Spring source with its mapped Fall source at the two
branch tips. It found 36 byte-identical source pairs and 25 changed pairs
across 61 mapped paths. The four Fall sources mapped to the older Lab 2 PDF
are separate files, and the fuzzing topic maps to two Fall decks. Blob identity
is provenance evidence only: it does not establish topic equivalence, current
course relevance, or a keep/replace decision. Use the content crosswalk and
source review for those decisions.

The Fall Test Case Minimization PDF/Keynote is the primary lesson. A visual
review of all 49 Fall pages against the 52-page older PDF found four
consecutive older slides (source pages 38–41, combined slides 840–843) with a
useful formal model of edits and failing-input construction that Fall omits.
The equations have been visually checked for the conversion pilot. The pages
are not selected as an isolated supplement inside Fall's complete TCM topic.
The Spring branch has no old Keynote, so the pilot mapped each source PDF page
one-to-one to an editable static slide;
the old pages in the combined deck are raster images. Round 12 revision 2
reconstructs only the four selected older pages; it is not the full Fall
lecture conversion. The pilot demonstrated the editable reconstruction in
Google Slides: subscripted labels render legibly and each page is mapped
one-to-one. The older Spring Keynote remains unavailable, so notes and
animation build states cannot be recovered from the older PDF. The rest of
the old deck is superseded or duplicated. See the
[crosswalk](source-version-crosswalk.csv) and
[runbook findings](SLIDE_CONVERSION.md#test-case-minimization-source-review)
and [Round 12 conversion log](SLIDE_CONVERSION.md#round-12--editable-test-case-minimization-supplement).

The older symbolic-execution candidate includes three additional Keynotes
whose combined slides cross topic boundaries. Their 1545–1660 span is not all
symbolic execution: pages 1545–1559 cover logic/CACC, 1560–1589 and 1617–1620
cover symbolic execution, 1590–1616 and 1621–1645 cover concolic execution,
and 1646–1660 contain a MultiNyx hypervisor case study. These ranges have
been corrected in the [crosswalk](source-version-crosswalk.csv). Since Fall
covers both topics, these older candidate sections are comparison/provenance
only and are not selected. See the
[runbook review](SLIDE_CONVERSION.md#symbolic-execution-and-concolic-source-review).

The older ISP material contains Multiple Base Choice Coverage (slides
1889–1890) and an Iterator characteristics/test-generation exercise (slides
1896–1916), but these are isolated additions inside the Fall-covered topic.
They are comparison/provenance only and are not selected. The broad old
range also contains JPL coding-standard and Clang/cppcheck material before ISP
actually begins at 1841. See the
[corrected crosswalk](source-version-crosswalk.csv) and
[detailed review](SLIDE_CONVERSION.md#input-space-partitioning-source-review).

Use the slide-level source maps below to preserve provenance, and check the
current syllabus and course order when placing complete older topics absent
from Fall. Do not switch branches just to inspect Fall sources; the archive
command keeps the working branch intact.

**Source-version rule:** use the complete Fall source wherever Fall covers a
topic. When an exact-revision Fall PDF exists, use it for page-by-page visual
comparison; use the Keynote for editable objects, notes, visibility, and
build order. Not every selected Fall Keynote has a paired PDF, and Test
Anatomy's available PDF predates its latest Keynote revision. Check the
[PDF coverage audit](SLIDE_CONVERSION.md#fall-pdf-coverage-and-keynote-preview-limits)
before assuming a pair is complete or current. Use older PDFs and
Spring-centered Keynote/PPTX sources only as revision-checked reconstruction
references; they must not override newer Fall content. Compare each page and
meaningful build state for source QA, but select older material only as a
complete topic when Fall does not cover it. The 17-page `Integration Testing Bad` draft has been compared and excluded whole:
Fall Test Anatomy pages 32–34 mark the traditional strategies as old/broken,
and pages 35–36 replace them with explicit contracts.

For reproducible page-level triage, see the [Fall-to-current report](fall-current-text-overlap.csv),
the [current-to-Fall report](current-fall-text-overlap.csv), and the
[per-topic summary](fall-topic-overlap-summary.csv), generated by
[audit_fall_text_overlap.py](audit_fall_text_overlap.py). These lexical
matches identify candidates for review; they do not decide whether a page is
equivalent, superseded, unique, or image-only. The [conversion runbook](SLIDE_CONVERSION.md#fall-2026-source-audit-and-first-text-crosswalk)
records the command and current findings.

The Spring-centered candidate's source inventory uses save/export dates
embedded inside the Keynote archives and PDF metadata; PDF UTC dates were
converted to the local time zone. Those dates describe that candidate only
and do not supersede the later Fall 2026 PDF exports. Modern Keynote slide
order and skip flags were read directly from the IWA archives; the flags match
the existing PDF slide counts for the corresponding unchanged decks.

Within this Spring-centered candidate set, the latest saved Keynote supplies
each deck, except symbolic execution (`17`), whose March 26 PDF is newer and
more complete than its March 18 Keynote.
Test-case minimization (`20`) and the lab tutorial are supplied only as PDFs.
The older 37-page structural-coverage PDF in the top-level directory is
superseded by the later version in `pdfs/` and its current Keynote.

The 398 slides marked skipped in Keynote were excluded from the combined
collection. These include archived material and unused template slides.
The original files are unchanged. A separate editable build-state conversion
may produce more than 2,235 output slides when meaningful animation states are
expanded.

Keynote was converted with LibreOffice, retaining editable text, shapes, and
available speaker notes. Font names were normalized and available open fonts
were used to reduce text wrapping. Original Apple-exported PDF pages were
reused where the corresponding Keynote slide predates that export and its
text, including code operators, matches. Other pages were rendered from the
selected Keynote slides. Third-party conversion can change typography and
some diagram formatting; these files are not a native Apple Keynote export.
The source PDFs and image-based PowerPoint parts flatten animation builds.
For the editable conversion, meaningful instructional build states should
become sequential static slides in original build order, with a map from each
output page to its source slide and build state. Keep the resulting sequence
inside its complete source deck and topic.

The first checked example is combined slides 205–206 from
`06-408st-concurrency.key`: the Round 4 Google PDF preserves the first comic
panel followed by the completed comic. The paired static PDF repeats the
completed comic, so it cannot validate this animation order. See the detailed
[build audit](SLIDE_CONVERSION.md#animationbuild-audit-combined-slides-205206).

The two image-based import parts render the final PDF, using slide images up
to 1,100 pixels wide and extracted slide text in the speaker notes. The lab's
widescreen pages are centered without distortion on the 4:3 PowerPoint canvas.
The PDF retains its original page dimensions and vector text where available.

## Current status and batch order

The source-selection gate and 16 conceptual boundaries are complete. Batch 1
is active and not accepted. Its full native WIP is the
[142-slide Google deck](https://docs.google.com/presentation/d/1EYXO-ZvBcLhUg9-JdA0t6C78sSx6Ki-4OGnIeYM9IME/edit)
at the shared Drive root; current native revision `81I4pqOtZCYd2A`. The latest
Google export is the Round 34 PDF with 142 pages, 5,278,199 bytes, and SHA256
`f209ce582c79ec0934992b157639c6ead8b53ff237867988ba5e2641cc5f72aa`. Rounds
29–34 repaired selected pages in that same WIP. Round 40 set all speaker notes
to 9 pt; native readback confirmed 339 runs across all 142 slides, including
whitespace anchors on the 66 formerly empty note pages. Full-size Google
review and structural reconciliation remain open. All 52 build dispositions
are complete: 37 source slides expand into 198 cumulative states and 15 remain
single static slides. Do not repeat content selection or start Batch 2 early.
The detailed boundaries are in [BATCH_BOUNDARIES.md](BATCH_BOUNDARIES.md), and
batch maps and acceptance records are maintained in
[final-batches/](final-batches/).

The current local candidate is in ignored
`out/.build/batch-01/round39-page24-repair/`. Its PPTX has 272 ordered slides
and 272 map rows, resolves all ordered slide references, and passes ZIP
integrity; it is 41,741,711 bytes with SHA256
`3fc340887af03f12bd5669a4dbfe5453f5e4ea06714121e48c376df56f96c164`. Its
272-page diagnostic PDF is 5,228,469 bytes, SHA256
`86b78b494deac683ab634a181623566c16b373859d1ef00da044b716e145cb53`. The
current source/build map is
[`batch-01-round39-expanded-map.csv`](final-batches/batch-01-round39-expanded-map.csv).
Round 39 repaired local Fault/Error pages 24, 61, and 69 (outputs 130, 202,
and 224–225), retaining the page 24 title and page 61 text as editable. The
page 77 progression keeps both tables editable. Linux LibreOffice substitutes
fonts, so use Google rendering for font-sensitive acceptance. Round 28's
eight-slide native pilot verified the page 2–3 and page 27 states against
exact Fall PDFs. The Round 40 package check added 117 blank-note anchors to a
copy and confirmed 272 note pages at 9 pt without changing the slide map or
order. The tracked [speaker-note helper](speaker_notes.py) is used by the
batch builder and expander. This local candidate is not integrated into the
Drive WIP. The user set
the Google Drive plugin to “Allow all tools”; no approval is pending. Project
operations remain limited to the CS 408 folder.

The notes-free native text readback has now been reconciled with the candidate:
all 142 existing WIP slides map in order, and 130 candidate rows remain at 32
insertion anchors. The reconciler corrected 14 provisional build-state
matches; these are map alignments, not visual repairs. A small Slides API pilot
verified duplicate with child-ID mapping, delete, and position operations; it
did not modify the full WIP. The nine-slide test deck is
[in Drive Pilots](https://docs.google.com/presentation/d/1qz2QdqzzT0m5tlSm1iS2LhOUHAKenZ0UonmSPU9z7R0/edit).
See the correspondence and insertion-gap maps in
[final-batches/](final-batches/) and
[reconcile_batch01_wip_candidate.py](reconcile_batch01_wip_candidate.py).

The initial unmatched-slide review sheets can be regenerated with
[render_unmatched_contact_sheets.py](render_unmatched_contact_sheets.py). The
current local Batch 1 repairs are implemented by
[repair_batch01_introduction.py](repair_batch01_introduction.py) and
[repair_batch01_fault_error.py](repair_batch01_fault_error.py); their evidence
and limitations are recorded in the diagnostic and conversion runbook.

For every final batch, add a full-slide solid pale-yellow (`#FFF2CC`) editable
divider before each original source deck. Center the exact filename in 24 pt
bold Arial and the following topic in 28 pt regular Arial; give the generated
text boxes explicit rectangle geometry so Google Slides retains them. Each
divider receives its own source-map row.

Finish the active Batch 1 end to end: complete its source/build map, classify
the remaining meaningful builds, convert and repair its selected material,
validate the local package, and keep one full-size working Google Slides deck
directly in the shared Drive root (the parent folder of `Pilots`). Improve
that same native deck in place, read it back, export the Google PDF, inspect
every page, and document the result. Rename it as the accepted batch only
after all checks pass; start Batch 2 only then. Continue in order. Use
`Pilots` only for small isolated test decks and disposable tests; never put a
full-batch WIP or final deck there.

Aim for each batch PDF to stay below 10 MB when whole-topic boundaries allow.
Do not run a separate large-PDF transfer test. If an actual complete batch
exceeds the direct export limit, use the documented no-curl LRO or
authenticated-browser fallback; never split a deck or topic to fit.

## Verification

The editable decks now use one notes master per file. The repair preserved all
2,235 slide XML parts, 805 note pages, and 694 images byte for byte. The
image-based decks now declare their existing notes master in the presentation
XML. ZIP integrity, internal relationships, slide order, and the import
sizes were checked after repair.

LibreOffice rendered the 16-slide pilot and the 275-slide third editable batch.
In the pilot, the photo backgrounds and image-only pages rendered, while some
editable titles wrapped differently and some code or diagram elements shifted.
For example, compare pilot slides 7 and 12 with the reference. Linux font
substitution can account for some of these differences. Rounds 1 and 2 kept
all 16 original pilot slides in order. Rounds 3 and 4 each kept all 260
slides in Part 1 in order. Rounds 5–11 completed connector imports and PDF
exports on small, source-mapped test decks. Round 9 revision 4 verified
editable CFG arrows and matched both unchanged controls pixel for pixel.
Round 10 revision 6 verified a font-and-inset repair, moved subset symbols,
and matched its unchanged control pixel for pixel. It also surfaced empty
bullet paragraphs on control slide 153; they are preserved as an open repair
example. Round 11 revision 4 disabled wrapping and removed excess horizontal
insets on the affected CFG labels while retaining their original font sizes.
Its Google PDF control matches the Round 4 export pixel for pixel. A local
LibreOffice render substituted a wider font for Bebas Neue; use Google's PDF
to judge the import and do not reduce a font solely to compensate for that
local substitution. See the runbook for reusable rules and current open work.
