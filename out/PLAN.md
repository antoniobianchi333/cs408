# CS 408 slide conversion plan

**Updated:** 2026-11-27
**Status:** Round 24 fixed the source-deck dividers, and the Round 25 grading
table repair passed a two-slide PPTX-to-Google-Slides import pilot. The full
142-slide Batch 1 WIP remains in the shared Drive root. Its latest Google PDF
export has 142 pages and is 5,233,045 bytes. Contact sheets have been reviewed
across all pages; full-size follow-up on flagged slides and confirmed repairs
remain open, so Batch 1 is not accepted. The user reports that a brief visual
check found about 90% of slides looking fine.

In the current session, I regenerated the local repaired source PPTX files,
rebuilt the 111-page base, restored the page 18 article/headline build, and
expanded the six classified build slides to a 142-slide candidate. The output
map has 142 consecutive rows, including dividers at pages 1 and 63; the PPTX
presentation order resolves to 142 existing slide parts and passes ZIP
integrity checking. Its local diagnostic PDF also has 142 pages (32,564,269
bytes). This local render is not acceptance evidence: Linux substitutes some
source fonts, and the full Google WIP still needs the remaining repairs,
build classifications, and recheck. Seven of 52 build-bearing slides are
classified; 45 remain.

The connected Drive account can list the project folder, and the native
`STATUS` document was created, read, and edited there. The user confirmed that
no separate Drive authorization is needed now. The Google Drive app inherits
the platform's “Allow low-risk actions” mode, so handle an actual per-operation
prompt or denial if one occurs. The session-wide LibreOffice authorization is
active.

The two generated source-deck dividers initially imported blank. The local
builder's editable text boxes lacked explicit DrawingML rectangle geometry;
Arial itself was present. A two-slide Google pilot confirmed that explicit
`a:prstGeom` preserves both text boxes. The same two slides now display the
exact filenames and topics in the WIP, with centered 24 pt bold and 28 pt
regular Arial over a solid pale-yellow `#FFF2CC` background. The generator and
batch instructions now enforce this style.

The Course Grading slides at output pages 24–25 were also repaired in the
Google WIP. Their Fall PDF uses an 80 pt Source Sans Pro title and 66 pt Bebas
Neue table text; the imported cells had been 24 pt Arial and top aligned. The
WIP now uses the source font sizes, middle alignment, and source-matched row
heights on page 24. A two-slide import pilot confirmed that the table font,
size, alignment, and row heights survive a fresh PPTX import. The title face
maps to Arial on that import, so the full WIP keeps a native Source Sans Pro
repair. See [Round 25](combined/SLIDE_CONVERSION.md#round-25--batch-1-course-grading-table-typography).

The 111-page baseline has a 142-page partial candidate after six expansions.
Introduction PDF pages 4, 6, 12, 15, 17, and 18 have 11, 7, 2, 9, 6, and 2
cumulative states. All 37 generated states passed local and Google PDF
review. Page 12's explicit Arial sizes, bullet glyphs, and line breaks
survived import while remaining editable. Page 18's source article image now
precedes its editable headline; Google needed a 31 pt text size and a small
vertical adjustment. Its final line width and baseline closely match the
Fall reference; font substitution leaves it slightly shorter vertically.
The page 6 `~24` line remains unwrapped; page 17's Google-only coarse banner
dash was repaired with a native `DOT` outline update on all six states. Page
16's one-chunk All at Once build stays a single static slide.

The Keynote show trees are now decoded: Introduction has 92 ordered nodes,
62 skipped, and 30 active; Fault/Error has 108 nodes, 29 skipped, and 79
active. Every unskipped slide matches its Fall PDF page and LibreOffice
candidate slide in order. This resolves the earlier count mismatch and active
slide order. The Introduction reveals on PDF pages 4, 6, 12, 15, 17, and 18 have
11, 7, 2, 9, 6, and 2 cumulative states. All 37 states were reviewed locally
and in separate native Google pilots. Their PDFs have 11, 7, 2, 9, 6, and 2
pages; every page was visually checked, and the final states closely match
the Fall references. Page 18 retains a small Google font-substitution height
difference. Its image-first/headline-second progression has passed local and
Google PDF review. Page 17
needed a native Google `DOT` line-style update after import. Page 16's
single-chunk All at Once build adds no static state. The six expansions raise
the partial candidate from 111 to 142 pages. Seven of 52 build-containing
slides are classified; 45 remain unclassified.

Round 16 remains the completed 38-slide diagnostic: native readback confirmed
ordered editable slides and notes on every page; all 38 pages have close
visual review, and the local audit passes package/order/PDF-page/text checks
with slide 6 as the control. Slide 21's newer System test material is retained
although it is absent from the older September PDF. The 16-batch boundary
outline is recorded. Each final batch gets a full-slide solid pale-yellow
(`#FFF2CC`) editable divider before every original source deck, labeled with
its exact filename and following topic; use 24 pt bold Arial for the filename
and 28 pt regular Arial for the topic.

Batch 1 local source repairs cover Introduction pages 2 and 17 and Fault/Error
pages 65, 68, 73, 74, 76, and 77; the three diagram-region crops are documented
last resorts. The uploaded full-batch native Google deck is the live surface
for confirmed visual-only fixes. Keep the local PPTX and maps as the
reproducible source, and rebuild/reconcile them when content, build states,
order, or structure changes, or when a local repair is needed to preserve the
intended result through import.
Introduction page 2's local repair retains the orange Fall 2026 value; its
final two-pass native repair is readable but renders that value black. On
Fault/Error page 68, Google-first loses the source photo, while the local-first
36 pt label repair preserves it and keeps both labels on one line. Keynote IWA
scans found effect markers in 32 Introduction and 37 Fault/Error slide
records; these are locator counts, not animation counts. Structural build
order is decoded; meaningful static expansion remains open. Use local PPTX
repairs by default and native Google Slides edits as a per-family backup when
import-specific defects remain or Google-first evidence is stronger. Page 17
  supports targeted Google-native repair for import-only differences; page 4
  and 6 paragraph pilots confirm local repairs for their editable text-build
  families. For the uploaded full batch, repair visual-only defects in the
  same native WIP and use a local rebuild when content or structure changes.
  Do not repeat the closed
57-deck content-selection analysis. See the
[Round 16 record](combined/SLIDE_CONVERSION.md#round-16--test-anatomy-repairs-and-google-review),
[Round 17 record](combined/SLIDE_CONVERSION.md#round-17--introduction-page-17-repair-pilot),
[Round 18 record](combined/SLIDE_CONVERSION.md#round-18--batch-1-introduction-paragraph-build-pilot),
[Round 19 record](combined/SLIDE_CONVERSION.md#round-19--batch-1-course-grading-paragraph-build-pilot),
[Round 20 record](combined/SLIDE_CONVERSION.md#round-20--batch-1-course-objectives-paragraph-build-pilot),
[Round 21 record](combined/SLIDE_CONVERSION.md#round-21--batch-1-introduction-mixed-bannerquestion-build),
[Round 22 record](combined/SLIDE_CONVERSION.md#round-22--batch-1-introduction-page-18-imageheadline-build),
and [Batch 1 diagnostic](combined/final-batches/batch-01-diagnostic.md).

Round 14 imported the complete 28-slide archived concurrency-
testing lab introduction into native Google Slides. Google readback returned
28 slides in order with native text/slide objects. All 28 Google PDF pages
were visually reviewed against a local diagnostic render of the source PPTX.
The source has no notes parts or timed animations. Its Google PDF is 942,081
bytes; the source map and review PDF/contact sheets are in the pilot folder.
This validates a small direct-PPTX import for an older complete topic; it does
not exercise animation expansion, speaker notes, or `.key` export.

Round 13 imported the complete Fall Lab 1 fuzzing tutorial. Its 40 source
slides became 62 ordered static slides after expanding 8/6/11 paragraph
builds; one AFL screenshot zoom pair is also mapped as sequential states.
Native readback confirmed 62 slides and editable text/native objects; notes
were confirmed on a static slide and an expanded-build slide. All 62 Google
PDF pages were visually reviewed. The Spring Lab 2 tutorial is superseded and
comparison-only. Slide 2 follows the handout's October 30 deadline, while the
syllabus table says November 3; retain that conflict for resolution before
final integration.

Round 13's 1,017,750-byte Google PDF was rendered using one bounded connector
fetch; no `curl` or retry loop was used. Round 12 remains a technical pilot for
older Test Case Minimization pages; Fall is the complete selected TCM source.
The 205–206 concurrency build remains verified in the Round 4 Google PDF.
Part 2 (232 slides) is native Google Slides; its rev3 PDF was compared with
rev2, where 230 pages are pixel-identical and only the repaired panels on
slides 214 and 216 differ. Content selection for all 57 candidates is now
recorded; page/build source mapping remains open.
All 20 files in `slides/f26-pdfs/` and the 57 Keynote packages are present in
the active checkout, but they are not a one-to-one set of exact-revision
pairs. The PDF coverage audit records missing and older references. A
956-page text-overlap audit ranks Fall PDF pages against the current
candidate; it is triage, not a content-selection decision. A visual
pass separated older Symbolic Execution ranges into logic/CACC, symbolic,
concolic, and MultiNyx topics. The first-pass deck audit maps all 57 Spring
entries to Fall candidates (44 exact basenames, 12 topic/renumbering aliases,
and the Spring Lab 2 tutorial to Fall Lab 1/fuzzing material). All 57 entries
now have explicit content-selection outcomes. The five final comparisons
resolved on 2026-11-25: select the latest available Final Review deck with
Fall schedule repairs; include complete older Verified Distributed Systems
and Semantic/Latent Concurrency Bug Detection units; exclude the older mixed
Regression/Integration and Fall 2025 Review decks. Slide/build maps and
conversion remain open. Before the Round 23 full-deck upload, the November 27
read-only Drive root listing returned only `Pilots`. The current 142-slide
WIP deck is now in the root; its placement is documented in the
[Drive guide](combined/GOOGLE_DRIVE_ACCESS.md#pilot-and-final-batch-folder-organization).

## Required live status document

Keep one native Google Doc titled `STATUS` directly in the CS 408 project
Drive folder root (`16vTRNocHa1rlPN1bii_w0b8Ce90XrFbn`), above `Pilots`.
The [live STATUS document](https://docs.google.com/document/d/1TAFn9A9Nkkr8YU8R0Hpfge4Q7MBOvBPT4F7XHiDG9UU/edit)
was created and verified on 2026-11-27; its ID is
`1TAFn9A9Nkkr8YU8R0Hpfge4Q7MBOvBPT4F7XHiDG9UU`, its MIME type is native Google
Docs, and its parent is the designated project folder. Update this same
document about hourly during sustained work and after major milestones. Every
update must put these items in order: permission approvals needed (or none
pending), the current 5-hour and weekly usage percentages from
`codex_usage.py`, current work and near-term plan, the full contents of
`MANUALLYCONVERT.md`, and the full contents of this plan. The status Doc
belongs in the project root and is not a pilot artifact.

**Working branch:** `spring+2027+bianchi`, based on the newest available
course branch, `others/fall+2026` at `900304aa` (2026-11-15). Its selected
documentation, scripts, and compact maps are being added; generated slide
decks and PDFs remain local and unadded because of their size.

This is the live plan for converting the selected Fall-first course material
and complete older-only topics into reliable, editable Google Slides. The
2,235-slide Spring-centered collection is a comparison baseline, not the final
source list. Update this plan after each major milestone and about hourly
during active work. Estimates are hands-on time unless noted; revise them as
batch size, API behavior, and review effort become measurable.

## Goal and fixed decisions

- Use the newest available version of each topic or artifact. Include older
  material only as a complete topic that newer sources do not cover; record
  its source and version in the crosswalk.
- Topic selection is complete for all 57 candidate rows. Do not repeat or
  broaden that analysis. Use the complete Fall source wherever Fall covers a
  topic, and include only complete older-only topics absent from Fall. The six
  selected older-only units are the archived concurrency-testing lab
  introduction, Verified Distributed Systems, Semantic/Latent Concurrency Bug
  Detection, Record and Replay, Deterministic Execution, and Static Testing
  Tools. Their decisions are in the [selection audit](combined/older-topic-selection-audit.csv).
  Do not append isolated older examples or criteria to Fall-covered topics.
- Use existing full-deck PDFs first and verify that they match the selected
  Keynote revision. Manual PDF export by the user is a last resort; the
  [request list](MANUALLYCONVERT.md) currently has no entries.
- Preserve original order. **Never split an original source deck or a topic.**
  A block boundary is valid only after a complete source deck and a complete
  topic. Keep adjacent decks together when one topic spans them; keep an
  entire deck together when it covers several topics.
- First identify ordered, indivisible deck/topic groups. The final upload
  target is **16 conceptual batches**, roughly one lecture week each. Let slide
  counts and file sizes vary to preserve source-deck and topic boundaries.
  Never cut a deck or topic to reach an equal-size target.
- Use the current syllabus and course sequence to place batches. Consult the
  previous course schedule to estimate roughly one class week per batch; keep
  a topic whole when it spans the estimated week boundary.
- The Introduction course schedule slide is user-owned. Do not edit its
  schedule content or let that slide block agent work; the user will make that
  correction directly.
- Preserve text, code, shapes, diagrams, pictures, and notes as editable
  objects where reliable. For text-fit problems, inspect width, height, and
  insets before reducing font size. Keep an image fallback limited to the
  smallest element that remains unreliable; whole-slide images are a last
  resort.
- **Repair route:** build reproducible source repairs in the local PPTX, then
  import and verify the Google PDF. Once the full WIP is uploaded, make
  confirmed visual-only fixes in that same native deck to avoid unnecessary
  full-deck re-imports. Rebuild/reconcile locally for source-content, build,
  order, or structural changes, or when a source-side repair is needed to
  preserve media through import. Paired page 2 and page 68 evidence and the
  full-batch workflow are in the
  [conversion runbook](combined/SLIDE_CONVERSION.md#full-batch-working-deck-workflow).
- Convert meaningful instructional animation or reveal builds into
  sequential static slides in the original build order. Map every generated
  slide to its source slide and build state. Keep the expanded sequence within
  its source deck/topic group; final output count can exceed 2,235.
- Pace Google Drive calls serially. Leave at least five seconds between
  import, structural read, export, and fetch operations, and wait longer after
  slow responses or rate-limit signals. Validate each block before uploading
  the next.
- Set the 16 contiguous conceptual batch boundaries once, using whole source
  decks/topics and the syllabus/homework sequence. Then complete Batch 1 in
  full—map, convert, repair, upload, read back, export, inspect every page,
  and document—before starting Batch 2. Repeat in order through Batch 16.
- Put every full-batch deck, including WIP copies, directly in the shared
  Google Drive folder root, one level above `Pilots`. Mark unfinished decks
  `WIP - needs fixes`; use `Pilots` only for small isolated test sets.
- Aim to keep a batch PDF below 10 MB when its natural conceptual boundaries
  allow it. Do not split a source deck or topic for size. A larger PDF triggers
  the documented no-curl LRO/browser fallback only for that actual batch; a
  standalone >10 MB transfer test is not a project gate.
- Keep this plan, the root [README](README.md), and the runbook aligned with
  verified evidence. The root README must link to every relevant project
  Markdown file, script, and artifact folder.

## Completed and verified

- Round 14 imports `labs/lab1-archive/slides/lab1_intro.pptx` as the native
  Google deck [Concurrency Testing Lab Introduction Pilot Round 14](https://docs.google.com/presentation/d/1tAObwDTGc_EJ6aD4nXIceRTPjc3vF63hOPDdxFdZ0WE/edit)
  in the Drive `Pilots` folder. The source has 28 slides, no `p:timing` parts,
  and no speaker-note parts. Native outline readback returned exactly 28
  sequential slides and editable text; the Google PDF also has 28 pages.
  Every page was inspected in the Google contact sheets and compared with a
  local LibreOffice diagnostic rendering of the original PPTX. No layout or
  clipping issue requiring repair was found. This is an older complete
  concurrency-testing lab topic, not Fall's current fuzzing Lab 1. See the
  [Round 14 runbook record](combined/SLIDE_CONVERSION.md#round-14--older-concurrency-testing-lab-introduction)
  and [older-topic decisions](combined/older-topic-selection-audit.csv).
- Round 4 remains the full 260-slide Part 1 comparison baseline.
- Rounds 5–11 tested image recovery, code and text fit, arrows, CFG diagrams,
  subset relations, and font-fit repairs with small Google imports.
- Round 11 revision 4 covers combined slides 114–116. It keeps slide 114 as
  an unchanged control and repairs the `Program Text`, `CFG`, `true`, and
  `false` labels on slides 115–116. Google's export matches the Round 4
  control at 120 dpi; text and slide order checks passed. The final native
  deck, PDF, and page map are recorded in the
  [Round 11 runbook entry](combined/SLIDE_CONVERSION.md#round-11--cfg-label-fit-with-original-fonts).
- The Round 11 repairs preserve the original label fonts. Removing
  unnecessary horizontal insets and disabling wrapping solved the split
  labels. A local LibreOffice check substituted a wider font because Bebas
  Neue was unavailable, so LibreOffice is an optional diagnostic renderer;
  Google's PDF is the visual acceptance render.
- The local [pilot audit script](combined/google-slides-pilot/audit_conversion_pilot.py)
  passed Round 11 without a Linux PDF. It checked PPTX structure, page map and
  order, unchanged control XML, Google PDF page count and text, and
  pixel-identical control rendering. The audit does not replace visual review.
- Native text replacement and readback passed on a disposable Round 10 copy
  and on the requested Round 4 deck. On a disposable copy of Round 11 rev4,
  `updatePageElementTransform` moved an imported arrow line by 1 pt and
  readback confirmed the move; a second guarded update restored its exact
  original transform. An `updateLineProperties` color change was rejected
  with `INVALID_ARGUMENT` for that imported arrow. This establishes a tested
  position edit for that object and a failure for that style update, not
  general editability of all line objects. See the
  [Google API evidence](combined/GOOGLE_DRIVE_ACCESS.md#verified-native-vector-object-edit).
- The Google API roundtrip used serial calls with at least 5.5 seconds between
  operations. Round 11 had no rate-limit response. Its final Google PDF is
  242,663 bytes and has three 1,024 × 768 pages.
- On November 24, 2026, the existing 232-slide editable Part 2 (slides
  261–492) imported successfully to the shared Drive folder as native Google
  Slides: [Part 2 scale-validation deck](https://docs.google.com/presentation/d/1CFsmvh6YcpiNkJJye8NR0fP2c_ScFlEAXSc8Mm9Yj3k/edit).
  A native structure readback returned exactly 232 slides with IDs `p1`
  through `p232` in order. Google generated one PDF export, 9,478,484 bytes;
  its returned text begins with Data-Flow Coverage Criteria and proceeds to
  Input Space Partitioning and the later source topics. The renderer found no
  local `workspace_path`, so this is a structural/import pass, not a visual
  pass. Do not count Part 2 as fully verified until that PDF is locally
  available and compared page by page. The single export did not produce a
  rate-limit response.
- Round 15 established an explicit LibreOffice `.key`-to-PPTX path on Linux
  and a native Google Slides import, but the Test Anatomy result is diagnostic
  only because of layout defects and one unmapped slide. Its 37-page Fall PDF
  is a useful visual baseline, but predates the latest Keynote member by a
  month. See the [Round 15 record](combined/SLIDE_CONVERSION.md#round-15--fall-test-anatomy-linux-keynote-diagnostic).
- The nine local editable batch PowerPoints now sit directly in
  `out/combined/`, with ranges in `editable-parts-manifest.json`. All 17
  Google presentations formerly at the shared folder root were confirmed by
  metadata as pilots or disposable tests and moved into its `Pilots`
  subfolder. The shared folder root is reserved for final batches. The local
  and Drive locations are described in the
  [pilot folder guide](combined/google-slides-pilot/README.md).
- All project Markdown files, every relevant conversion/repair/audit script,
  source map, manifest, and working folder are linked from the
  [root README](README.md).
- The initial source crosswalk is at
  [source-version-crosswalk.csv](combined/source-version-crosswalk.csv). It
  maps the 19 Fall lecture PDFs and the separate Integration Testing Bad PDF
  to candidate current sections. Use the source-deck and older-topic audits
  for the recorded use/exclude decisions; this crosswalk remains a page-level
  provenance and source-map aid. **Correction from the
  metadata audit:** the Fall PDFs (August–November 2026) postdate the
  Spring-centered Keynote candidates (January–August 2026). Use Fall content
  as the latest source where it covers the same material; page/build-level
  mapping remains open. The older-topic decisions are already recorded in the
  selection audit.
- On 2026-11-25 the repository was switched to `spring+2027+bianchi`, based
  on the newest source branch, `others/fall+2026` at `900304aa`. Local tracking
  branches were created for all four pre-existing branches so `git branch`
  lists the full set.
- The 20 Fall source PDFs (19 numbered lectures plus the Integration Testing
  Bad draft, 956 pages total) are stored on `others/fall+2026` under
  `slides/f26-pdfs/`. They were extracted into `out/.build/fall-source/`
  without changing branches. All actual page counts matched the expected
  counts; the compact audit is
  [fall-source-metadata.csv](combined/fall-source-metadata.csv). All 57
  candidate rows now have recorded use/exclude outcomes; exact source/build
  mapping and conversion remain open.

## Planned work and estimates

These estimates exclude waiting time between API calls and assume each pilot
needs no unexpected repair cycle. Confidence is lower for untested Google
behavior and for full-deck visual review.

| Order | Work | Estimate | Exit condition |
| ---: | --- | --- | --- |
| 1 | **Complete 2026-11-25.** Record content-selection outcomes for all 57 source-deck candidates and the older-only topics. | 2–4 hours · medium | Every candidate has a use/exclude decision. Six complete older-only units are selected: archived Concurrency Testing Lab Introduction, Verified Distributed Systems, Semantic/Latent Concurrency Bug Detection, Record and Replay, Deterministic Execution, and Static Testing Tools. The mixed Regression/Integration and stale Fall 2025 Review decks are excluded whole. Do not repeat selection; exact source/build mapping is a batch conversion task. See the [source-deck audit](combined/source-deck-topic-audit.csv) and [older-topic audit](combined/older-topic-selection-audit.csv). |
| 2 | **Complete 2026-11-25.** Resolve the concurrency build around combined slides 205–206 using the latest Keynote export and the existing Round 4 Google PDF. | 45–90 min · medium | Confirmed: Keynote export pages 19–20 and Google PDF pages 205–206 show the first comic panel followed by the complete comic. Two distinct picture/crop objects preserve the ordered build; no new import is needed. See the [build audit](combined/SLIDE_CONVERSION.md#animationbuild-audit-combined-slides-205206). |
| 3 | **Complete 2026-11-25 (technical pilot only).** Reconstruct four older Test Case Minimization pages to test editable math and Google font rendering. | 45–90 min active · medium | Rev2 readback confirmed four ordered editable slides with no images; all four Google PDF pages were inspected. Round 12 is a conversion-method sample, not final content; Fall is the selected complete TCM source. |
| 4 | **Complete 2026-11-25 (diagnostic only).** Test the explicit Linux LibreOffice `.key`-to-PPTX route using Fall Test Anatomy, then import into Google Slides. | 1–3 hours active · medium | Round 15 identified the repeated question, slide 9 overlay, and valid newer quote/build page; Round 16 applies targeted repairs. See [Round 15](combined/SLIDE_CONVERSION.md#round-15--fall-test-anatomy-linux-keynote-diagnostic). |
| 5 | **Removed as a separate gate.** Do not build and measure an integrated legacy Part 1 before the final batch sequence. Use existing scale evidence and measure the actual Batch 1 workflow instead. | 0 min | No standalone Part 1 import is required to begin Batch 1. |
| 6 | **Complete 2026-11-25.** Verify Part 2 rev3: 232-slide native readback, Google PDF, and full-page regression comparison against rev2. | 30–90 min · low | 232 slides/pages confirmed. Only the intentional fixes on slides 214 and 216 changed; both rendered panels and editable text were reviewed. Evidence is linked from the [Drive guide](combined/GOOGLE_DRIVE_ACCESS.md#part-2-scale-import-and-pdf-transfer). |
| 7 | **Complete 2026-11-25 (source/conversion pilot).** Import the complete Fall Lab 1 tutorial, expand and map its builds, verify native order/notes, and inspect the Google PDF. | 45–90 min active · medium | Complete: 40 source slides became 62 ordered slides; paragraph states 8/6/11 and the AFL screenshot zoom pair are mapped. All 62 Google PDF pages were inspected. Spring Lab 2 tutorial is comparison-only. The Oct 30 handout vs Nov 3 syllabus deadline conflict remains open. See [Round 13](combined/SLIDE_CONVERSION.md#round-13--fall-lab-1-fuzzing-source-and-build-mapping). |
| 8 | **Complete 2026-11-25 (older-topic import pilot).** Import the complete archived concurrency-testing lab introduction, map it, and compare every Google-rendered page with the PPTX source. | 45–90 min active · medium | Complete: 28 ordered slides and 28 Google PDF pages; all pages visually reviewed against the source's local diagnostic PDF. No layout repair needed. The source has no notes or timed animation. See [Round 14](combined/SLIDE_CONVERSION.md#round-14--older-concurrency-testing-lab-introduction). |
| 9 | **Complete 2026-11-26.** Review all 38 pages of the Round 16 Google export against the current Keynote-derived deck and September PDF where applicable; repair verified defects. | Complete · 0 min remaining | All 38 map rows have close review. Repairs cover slide 1's banner, slide 2's empty bullets and line fit, diagram regions on slides 4–5, agenda bullets on 7 and 38, and the blank code row on 25. Google shows `3.` on the restored blank row; source PDF leaves it unnumbered. The audit passes page order/count, requested text, and slide 6's unchanged XML/pixel control. See [Round 16](combined/SLIDE_CONVERSION.md#round-16--test-anatomy-repairs-and-google-review). |
| 10 | **Complete 2026-11-26.** Set the 16 conceptual boundaries from the closed selection audit and Fall syllabus. | Complete · 0 min remaining | [BATCH_BOUNDARIES.md](combined/BATCH_BOUNDARIES.md) records the ordered groups, complete source topics, Week 12 Midterm 2 review and Week 15 Floyd/Dafny source gaps, and six older-only units. Confirm those source gaps before the affected batches; do not substitute an unrelated topic. Every final batch gets a full-slide, solid pale-yellow (`#FFF2CC`) editable divider before each original deck. Center the exact filename in 24 pt bold Arial and the following topic in 28 pt regular Arial; map each divider separately. |
| 11 | **In progress.** Complete Batch 1 end to end: inspect every source/build candidate, finalize the map, expand meaningful states, repair, assemble, iteratively fix the full Google deck, export its PDF, inspect every page, and document acceptance. | Remaining estimate 4–7 working days · low | Two source Keynotes are converted. The decoded show trees confirm 30 active Introduction slides and 79 active Fault/Error slides, each matching their Fall PDF and PPTX candidate in order. The baseline assembly is 111 pages; the current partial expansion is 142 pages after six build expansions for Introduction PDF pages 4, 6, 12, 15, 17, and 18 (11, 7, 2, 9, 6, and 2 states). All 37 generated states passed local review and separate native Google PDF review. Round 23's page 12 fonts, bullets, order, and line breaks survived Google import without a Google-side repair; page 18 still has a small font-substitution height difference after its native font/position adjustment. Page 16 has one All at Once chunk and needs no extra state. Seven of 52 build-containing slides are classified; 45 remain. The decoded sequence logs report 113 Introduction and 185 Fault/Error build chunks across 52 active slides; chunk counts are review leads, not final slide counts. The full 142-slide WIP deck is in the shared Drive root as [CS408 Batch 1 - WIP - needs fixes](https://docs.google.com/presentation/d/1EYXO-ZvBcLhUg9-JdA0t6C78sSx6Ki-4OGnIeYM9IME/edit); native outline readback confirmed slide count and order. The user reports about 90% looked fine in a brief first pass; the latest full Google PDF is 142 pages and 5,233,045 bytes, and contact sheets have been reviewed across all pages. Full-size follow-up and confirmed repairs remain open. The two source-deck dividers were initially blank because generated text boxes lacked explicit preset geometry; a two-slide pilot verified that `a:prstGeom` restores editable labels. The WIP now has solid pale-yellow `#FFF2CC` backgrounds, filename 24 pt bold, and topic 28 pt regular. Round 25 repaired output pages 24–25 with 80 pt Source Sans Pro titles, 66 pt Bebas Neue table cells, MIDDLE alignment, and source-matched row heights; a two-slide import pilot confirmed the table styles, while the title maps to Arial on import. Local repairs cover Introduction pages 2, 6, 12, 15, and 17 plus Fault/Error pages 65, 68, 73, 74, 76, and 77. Use local repairs to build reproducible source content, then make confirmed visual fixes in the same native Google working deck. Page 17's native title and dotted-outline fallback still need full-deck verification. Repairs on pages 65, 73, 74, 76, and 77 still need Google-export checks; diagram crops remain last resorts. The user owns the schedule slide and will edit it. The WIP deck is not accepted; do not start Batch 2 until Batch 1 passes every acceptance check. Re-estimate later batches from measured defect rates. |
| 12 | Complete Batches 2–16 in order, repeating the full Batch 1 workflow; start each only after the previous batch is accepted. | Initial estimate 1–3 working days per batch (15–45 days total) · low; recalibrate after Batch 1 | All 16 final decks are directly in the shared Drive root (above `Pilots`), with complete maps, native readbacks, reviewed Google PDFs, and current documentation. |
| 13 | Use the no-curl large-PDF fallback only if a real batch export exceeds the direct response limit. | Conditional: 30–90 min if needed | Try the documented `files.download` LRO or authenticated browser route for that batch. Do not run a standalone size test and do not split a whole deck/topic just to fit the limit. |

## Current open issues

- Round 16 is accepted as a diagnostic pilot: all 38 pages have close review,
  and the final 5,101,352-byte Google PDF, page map, contact sheets, and
  slide 25 comparison are saved in the review folder. Known conversion rules
  and accepted differences are recorded in the map and runbook. The audit
  passes page order/count and text checks; slide 6 is byte-identical to the
  Round 15 PPTX and pixel-identical to its Google PDF at 120 dpi.
- Selected Fall Keynotes lack full-deck PDFs in `slides/f26-pdfs/` for
  Concurrency 06/07/10, Bug Reports and Triage 13, Static Analysis 22, Final
  Review 23, and Testing AI/ML 28/29/29b/30. Older PDFs exist for some and
  require revision/page-map checks; the AI/ML sources have no complete PDF in
  either local PDF folder. Resolve each reference gap when that source reaches
  the active batch; do not create a global preconversion gate. Manual PDF
  export remains the last resort. See the
  [coverage audit](combined/SLIDE_CONVERSION.md#fall-pdf-coverage-and-keynote-preview-limits).
- Carry forward Round 11's CFG-label repair only when the same object/layout
  appears in a selected batch. Other legacy Part 1 visual issues are not a
  separate pre-batch gate; check relevant layouts during that batch and use
  the [route decision and repair evidence](combined/SLIDE_CONVERSION.md#repair-route-decision-local-source-repairs-in-place-google-wip-edits).
- Before integrating the Round 14 older concurrency-lab unit, update or mark
  the `CS503 Spring 2021` screenshots on slides 4–6 as archival. Its full
  Spring 2026 handout is already in the study guide; the date and Classroom
  link match, so avoid duplicating the handout in slide form.
- Slide 153's unchanged Round 10 control retains visible markers from empty
  bullet paragraphs. Inspect related list layouts before applying a general
  cleanup.
- Other layout work remains on slides 70, 117–125, 128, 176–182, 186,
  238, 244, and 253. The 205–206 concurrency build is verified and removed
  from the open queue; see the [runbook audit](combined/SLIDE_CONVERSION.md#animationbuild-audit-combined-slides-205206).
- Source selection is closed for all 57 candidate rows. The selected older-only
  units are the archived concurrency-testing lab introduction, Verified
  Distributed Systems, Semantic/Latent Concurrency Bug Detection, Record and
  Replay, Deterministic Execution, and Static Testing Tools. Map and convert
  them as complete topics when their sequential batch is reached. Update the
  selected Final Review source's May 8/HW3–5 administration from the Fall
  syllabus during that batch. See the
  [selection audit](combined/older-topic-selection-audit.csv).
- The 31-slide older Regression/Integration deck is excluded because the
  complete Fall Test Anatomy and Regression Testing sources cover its topics.
  The separate 17-page Integration Testing Bad draft is also excluded: Fall
  Test Anatomy labels its older integration strategies as old/broken and
  replaces them with explicit contracts.
- Round 15 established an explicit Linux `.key`-to-PPTX import route; Round 16's
  38-slide diagnostic and review are complete. Round 17 tested one Introduction
  page repair through native Google Slides. No Apple account or separate
  iCloud route is planned.
- Native text replacement, the line-position transform, and a native outline
  dash-style update (`DOT`) are verified on pilots. Other diagram types,
  freeform path edits, image crops, tables, equations, and speaker-note edits
  need separate tests on disposable copies.
- The official Drive docs distinguish direct `files.export` (10 MB response
  cap) from `files.download` (LRO, supports Workspace export including Slides
  PDF). The connected fetch tool says `include_base64: false` uses the LRO
  route and returns a user-scoped `file_uri`; Google returns a download URI,
  and the connector does not promise that it will also appear as a local
  `workspace_path`. That explains the missing local path: it is the connector
  materialization boundary, not PDF size. This path returned a reference for
  both the 74,585-byte Round 12 PDF and the 9.9 MB Part 2 PDF. One bounded
  `include_base64: true` compatibility fetch was materialized and rendered for
  each. A >10 MB LRO through this connector and local materializer remains
  untested, but a standalone test is not required. Aim for small batch PDFs
  when complete-topic boundaries allow; if a real batch exceeds the direct
  limit, use the documented fallback. Never split a whole deck/topic for
  size, and never use `curl` or another shell/network downloader. See the
  [Drive transfer guide](combined/GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf).
- The November 27 read-only listing of the designated Drive folder succeeded
  before the Round 23 full-batch upload: the visible root then contained only
  the `Pilots` subfolder, and the nested listing included the Round 17
  Introduction page 17 pilot. The 142-slide Batch 1 WIP deck is now in the
  shared root. Calls were serialized with more than five seconds between them.
  This supersedes the earlier transient connector failure. See
  the [Drive guide](combined/GOOGLE_DRIVE_ACCESS.md#share-and-connect-the-folder).
- The nine legacy editable files are only comparison material; do not assume
  their boundaries match the new 16 conceptual batches.
- The final source-selection decisions and 16-batch boundary outline are
  recorded. Batch 1's active Keynote order and source/PDF alignment are
  decoded; its final output map is not assembled because meaningful animation
  states, visual repairs, and integrated Google checks remain. Finish Batch 1
  before starting later batches.
- The [Fall source crosswalk](combined/source-version-crosswalk.csv) references
  20 PDFs under `slides/f26-pdfs/`. They are present on
  the current checkout because `spring+2027+bianchi` is based on the Fall
  branch. All 20 PDFs (956 pages) and 57 Keynote decks (824.8 MiB total) are
  directly available under `slides/`; the small Keynote inventory and PDF
  metadata/page-count audit are recorded in
  [fall-keynote-inventory.csv](combined/fall-keynote-inventory.csv) and
  [fall-source-metadata.csv](combined/fall-source-metadata.csv). All 956 pages
  matched the expected counts. The source-deck audit records a use/exclude
  outcome for each of the 57 Spring-centered candidates; page/build mapping
  and conversion remain open. No source PDF or Keynote is missing from the
  active tree.
- An inventory-level audit maps all 57 Spring candidate source-deck entries
  to current Fall source candidates: 44 have exact basenames, 12 use explicit
  topic/renumbering mappings, and the Spring Lab 2 tutorial maps to Fall Lab 1
  plus the current fuzzing lecture sources. Every mapped local path exists.
  The Fall Lab 1 assignment covers the same black-box, grey-box,
  grammar-generation, and AFL workflow described in that 43-page Spring PDF.
  This does not prove slide/build equivalence. The older-topic audit selects
  six complete older additions: concurrency lab introduction, Verified
  Distributed Systems, Semantic/Latent Concurrency Bug Detection, Record and
  Replay, Deterministic Execution, and Static Testing Tools.
  The 97-slide syntax-based-testing unit is now excluded after content review:
  Fall Fuzzing covers grammar-based input generation and invalid-input grammar
  mutation, while Fall Mutation Testing covers program mutants and test-suite
  effectiveness. Its TSC/PDC/DC grammar-coverage criteria are isolated older
  additions within these Fall-covered topics, so they do not justify carrying
  forward the three old decks. Round 14 has tested the separate concurrency-
  lab introduction as a complete native Slides import.
  See the [audit table](combined/source-deck-topic-audit.csv) and its
  [generator](combined/audit_source_deck_topics.py).
- The first-pass audit now marks the Spring candidate's
  `03-408st-fault-error-failure` deck as superseded by the complete Fall 2026
  source. The Spring Lab 2 tutorial is likewise excluded in favor of the
  complete Fall Lab 1/fuzzing sources. Rows 31–33 now exclude the old
  syntax-based-testing decks after comparison with Fall Fuzzing and Mutation
  Testing. The two older bug-reporting decks are now marked comparison-only
  in favor of the October 25 Fall source; its stale February Project 1 and
  March midterm announcements need correction before conversion. The Fall
  Static Analysis deck is selected because it is scheduled in Fall and is
  byte-identical to its mapped Spring candidate. The three Fall concurrency
  decks at rows 6, 7, and 29 are also selected whole; they match their Spring
  blobs and together cover the scheduled Fall concurrency topic. The complete
  Fall Data-Flow source is selected for the two older mapped decks. All 57
  source-deck rows now have explicit use/exclude outcomes. The later Fall
  Final Review source is selected with schedule repairs; the full older
  Verification and Semantic Checker topics are selected as older supplements;
  the mixed Regression/Integration deck and stale 2025 Review deck are
  excluded whole.
  Older ISP source decks at rows 49–50 are excluded whole in favor of Fall's
  complete ISP topic. The concurrency-lab introduction is a separate supplemental source outside
  that 57-deck inventory. See the
  [older-topic audit](combined/older-topic-selection-audit.csv) and the
  [source-deck audit](combined/source-deck-topic-audit.csv).
- A branch-tip blob audit compares the mapped Spring source paths at
  `spring+2026` with the Fall candidate paths at `fall+2026`: 61 mapped path
  pairs comprise 36 byte-identical pairs and 25 changed pairs. The Spring Lab 2
  PDF maps to four separate Fall sources, and the fuzzing topic maps to two
  Fall decks. This is provenance evidence only; byte changes do not prove
  semantic changes, and identical blobs do not prove that a topic was taught
  in Fall. Content review remains the selection authority. See the
  [comparison](combined/source-branch-diff-audit.csv) and
  [generator](combined/audit_source_branch_diffs.py).
- Two preliminary text-overlap reports cover all 956 Fall PDF pages and the
  reverse view of 1,388 candidate current slides. Candidate ranges may overlap,
  so the reverse-row count is not a unique-slide count. The forward report
  compares editable PPTX text and the combined reference PDF; the reverse
  report ranks current candidates against their Fall topic PDFs to surface
  possible older-only content. They confirm that 32 of 49 Fall Test Case
  Minimization pages have strong matches in the existing PDF but no PPTX text
  matches, so the Fall source still needs an editable conversion. Round 12
  tested reconstruction of four older pages but does not select them for the
  final content; Fall is the complete TCM topic source under the updated
  preference. Symbolic execution has strong PDF matches on 34/47 pages
  and partial PPTX text overlap, but no PPTX page reaches the report's strong
  threshold; inspect object types before deciding which pages need rebuilding.
  The [per-topic overlap summary](combined/fall-topic-overlap-summary.csv)
  reports the same coverage counts for all 20 sources and ranks topics for
  follow-up; its thresholds are heuristic, not keep/drop decisions.
- A visual comparison now covers every page of the 49-page Fall Test Case
  Minimization PDF and its 52-page older counterpart. Fall is the complete
  selected topic source. Older PDF pages 38–41 (combined slides 840–843) were
  reconstructed in Round 12 rev2 as a technical conversion pilot, but are not
  selected as an isolated supplement. The Spring branch contains only the
  older PDF, not its Keynote, so there is no original note/build metadata to
  inspect. The rest of the older administration, algorithm, and GCC case
  study is superseded or duplicated. The four-page pilot is not yet merged
  into a final full-course batch.
  Details are in the
  [runbook](combined/SLIDE_CONVERSION.md#test-case-minimization-source-review)
  and [crosswalk](combined/source-version-crosswalk.csv).
- Fall Introduction pages 18–23 use a rocket launch, a power-grid outage, and
  a cloud outage as testing-motivation examples. The Spring Keynote source says
  `Therac-35`, while its paired PDF page 27 scans Nancy Leveson's Therac-25
  article; Fall's PDF and Keynote contain no Therac example. Since this is an
  isolated example inside the Fall-covered Introduction topic, omit it. Keep
  the source mismatch in the crosswalk for provenance only.
- The first visual pass on the older symbolic material corrected a misleading
  1545–1660 mapping: pages 1545–1559 are logic/CACC, 1560–1589 and 1617–1620
  are symbolic execution, 1590–1616 and 1621–1645 are concolic execution, and
  1646–1660 are a MultiNyx hypervisor case study. Fall covers these topics, so
  older sections are comparison/provenance only and are not selected as
  supplements. Preserve each original source deck intact at batch boundaries.
  See the [crosswalk](combined/source-version-crosswalk.csv) and
  [runbook](combined/SLIDE_CONVERSION.md#symbolic-execution-and-concolic-source-review).
- Visual review of all 52 Fall Input Space Partitioning pages and the older
  candidate ranges corrected the 1829–1916 map. Slides 1831–1838 are JPL
  LOC-1–LOC-6 coding standards for Mars Science Laboratory flight software;
  slides 1839–1840 are Clang/cppcheck examples. Both belong to Static Analysis,
  not Test Anatomy or ISP. The current source includes Fall
  `22-408st-static-analysis.key` and the syllabus schedules two lectures.
  There is no matching Fall PDF in `f26-pdfs/`; an older May 4 PDF exists in
  `slides/pdfs/` and needs revision/page mapping before use. The direct
  LibreOffice `.key`-to-PDF attempt produced no PDF. Map the complete Fall
  deck and replace its stale April 24 Project 2/HW5 announcements with Fall
  values (HW6 due Dec 4 at 6 PM; Project 2 due Dec 6). Do not append older
  slides 1831–1840 as isolated supplements.
  ISP starts at 1841 and Fall covers the topic; older slides 1889–1890 and
  1896–1916 are comparison evidence only, not selected content.
  Keep source decks 32 and 33 whole at eventual block boundaries. See the
  [crosswalk](combined/source-version-crosswalk.csv) and
  [runbook](combined/SLIDE_CONVERSION.md#input-space-partitioning-source-review).
  Test Anatomy has weak matches against both and needs direct mapping review;
  its older-source map no longer includes the JPL coding-standard excerpts.
  A visual/text check of Fall PDF pages 26–31 confirms the later lecture has
  detailed integration-testing rationale, contract/representation/protocol/
  error-handling/resource-management fault categories, the Mars Climate
  Orbiter example, and incremental evidence/citation builds. The only clear
  older overlap is a general “Testing in the real-world” / “Integration
  Testing” title and overview at current slides 1979–1980 in
  `36-408st-regression-integration-testing.key`; slides 855–884 are Regression
  Testing and are not Test Anatomy. Do not append the isolated older overview;
  use the complete Fall lesson.
  The Fall Introduction comparison confirms that course-specific values must
  come from Fall: its attendance policy, two grading options, midterm dates,
  and weekly schedule differ from the Spring-centered slides. Fall also adds a
  Coding Agent question and updates the learning objectives. Current Spring
  slide 10's Two-Step Submission instructions are absent from Fall and appear
  obsolete. The older Therac-25 scan and slides 29–34's reliability/failure
  examples remain provenance/comparison evidence; none are selected within
  Fall-covered topics.
  The Fall Fault/Error/Failure PDF contains 79 pages. The visual audit of its
  pages 31–62 shows a substantial ordered analogy and program-state modeling
  sequence, including stepwise execution-state builds that must remain
  separate static slides. The current reference has strong text matches for
  40/79 Fall pages and the editable PPTX for 39/79. Its 2025 candidate section
  around slides 1069–1087 mostly repeats definitions, RIPR, debugging, exercise,
  and recap content now present in Fall 2026; do not append it wholesale.
  Fall pages 63–78 also include the fourth RIPR condition (revealability), a
  staged debugging sequence, the expanded fault/error/failure possibility
  table, and a second exercise. These are part of the selected Fall deck and
  must remain in order; map each reveal/build separately.
  The report is heuristic; human page/build comparison remains required.
- Local LibreOffice exports from the Fall Introduction and Fault/Error/Failure
  Keynotes yielded 92 and 108 pages, versus 30 and 79 pages in the original
  Fall PDFs. The Keynote show tree marks exactly 62 and 29 nodes skipped;
  every unskipped slide maps in order to a current PDF page and the LO
  candidate. LO also rendered skipped material, including an Introduction
  submission slide and old Admin/Teaching Staff pages, plus an Admin/review
  block before Fault/Error/Failure's Game Plan. Do not add skipped records to
  the current show without evidence that a complete selected topic needs them.
  Active build chunks still need review for meaningful static states. LO damaged the schedule and grading tables, so its
  PDF is not acceptance visual evidence. Round 15 later proved an explicit
  `.key`-to-PPTX export can import into Google Slides, but its visible defects
  and unmatched page mean the route remains diagnostic, not accepted.
- The complete Fall `Test Anatomy` source supersedes the older mixed
  Regression/Integration deck's integration portion. The separate 17-page
  `Integration Testing Bad` draft is also excluded after comparison: Fall Test
  Anatomy pages 32–34 label its traditional strategies old/broken and pages
  35–36 teach explicit component contracts.
- Part 2 rev3 passed visual scale review: 232-slide order/readback, 232-page
  Google PDF, and page comparison. The fix and evidence are recorded in the
  [runbook](combined/SLIDE_CONVERSION.md#part-2-scale-validation-revision-3).

## Next action

1. **Complete 2026-11-27.** Create and verify the single `STATUS` Google Doc in
   the project root, populate the current usage/work sections and full source
   contents, and link it from `README.md`. Refresh hourly after reading the
   current sources and usage script.
2. Continue reviewing the remaining Batch 1 build chunks in decoded playback
   order. Introduction PDF pages 4, 6, 12, 15, 17, and 18 have verified
   expansions of 11, 7, 2, 9, 6, and 2 cumulative states; page 16's one-chunk
   All at Once build adds no extra slide. Seven of 52 build-bearing slides are
   classified; 45 remain. The current local 142-slide candidate and its 142-
   page diagnostic PDF have been regenerated and package-checked. Map every
   meaningful state before replacing/reconciling the same Drive WIP.
3. Finalize the complete ordered map, expand meaningful states, resolve the
   remaining page defects, then rebuild and audit the full local PPTX. Keep each
   source deck and topic whole and retain the required editable dividers.
4. The current full-size WIP deck is in the shared Drive root. Its 142-page
   Google PDF has been exported and all pages have had a contact-sheet review.
   Confirm flagged exceptions at full size and make verified visual fixes in
   that same native deck. Keep the local PPTX and maps as the reproducible
   source. If build classification changes the structure, update the working
   deck and verify the affected order and pages. Rename it as accepted only
   after native order/editability, notes, and the full Google PDF pass. Begin
   Batch 2 only after that gate; keep `Pilots` for small test sets.

When a batch needs a visual reference, first use a matching existing PDF or
inspect the Keynote/source package and its builds. The PDF coverage audit
records sources with no exact full-deck PDF. Request a manual export only as
the final fallback, through [`MANUALLYCONVERT.md`](MANUALLYCONVERT.md). Keep
each conceptual batch PDF below 10 MB when natural topic/deck boundaries allow;
use the documented no-curl LRO or authenticated browser path only if an actual
complete batch exceeds the direct export limit. Do not run a separate >10 MB
transfer test or split a deck/topic to meet the limit.

## Suggested `/goal` text

In the Codex app, enter `/goal` and paste this objective in the current
project thread:

```text
Complete the CS 408 slide project described in out/README.md and out/PLAN.md.
Deliver exactly 16 conceptual Google Slides batches covering the audited
Fall-first content plus complete older-only topics. Never split an original
source deck or topic. Convert meaningful animations into ordered static
slides. For every batch, upload to the shared Drive root, verify slide count,
order, editability, and notes, export a Google PDF, and compare every page
with an exact-revision source PDF or the best available verified reference.
Repair defects, record reusable conversion rules, and update the linked
Markdown and maps. Finish Batch 1 completely before starting Batch 2, and
continue in order. Put every full batch deck, including WIP copies, directly
in the shared Drive root, one level above Pilots. Name unfinished decks `WIP -
needs fixes`; keep improving the same native Google Slides deck there and
rename it after acceptance. Use Pilots only for small isolated test decks.
Use existing PDFs first; consult out/MANUALLYCONVERT.md only after other
reference options fail. Aim for batch PDFs below 10 MB when natural
boundaries allow; use the no-curl large-export fallback only if a real batch
exceeds the limit. Keep Drive calls at least five seconds apart; never use a
shell downloader for Drive files. Do not commit or push.
Mark the goal complete only after all 16 batches are uploaded and every batch
has a complete map, native readback, and page-by-page visual review. A pilot,
partial upload, or documentation update is not completion.
```

Goals can continue across turns while active and within budget, but may stop
for user input, interruption, or a budget limit. None of those conditions
means the project is complete. Resume the same goal after required input or
when the thread is available again.
