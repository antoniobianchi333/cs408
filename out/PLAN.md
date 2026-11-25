# CS 408 slide conversion plan

**Updated:** 2026-11-25  
**Status:** Round 14 imported the complete 28-slide archived concurrency-
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
Its 20 Fall PDF sources and matching Keynote files are present in the active
checkout. A 956-page text-overlap audit ranks Fall PDF pages against the
current candidate; it is triage, not a content-selection decision. A visual
pass separated older Symbolic Execution ranges into logic/CACC, symbolic,
concolic, and MultiNyx topics. The first-pass deck audit maps all 57 Spring
entries to Fall candidates (44 exact basenames, 12 topic/renumbering aliases,
and the Spring Lab 2 tutorial to Fall Lab 1/fuzzing material). All 57 entries
now have explicit content-selection outcomes. The five final comparisons
resolved on 2026-11-25: select the latest available Final Review deck with
Fall schedule repairs; include complete older Verified Distributed Systems
and Semantic/Latent Concurrency Bug Detection units; exclude the older mixed
Regression/Integration and Fall 2025 Review decks. Slide/build maps and
conversion remain open. The read-only Drive listing
shows the Pilots folder and no final batches in the visible project root.

**Working branch:** `spring+2027+bianchi`, based on the newest available
course branch, `others/fall+2026` at `900304aa` (2026-11-15). Its selected
documentation, scripts, and compact maps are being added; generated slide
decks and PDFs remain local and unadded because of their size.

This is the live plan for converting the 2,235-slide collection into reliable,
editable Google Slides. Update it after each major milestone and about hourly
during active work. Estimates are hands-on time unless noted; revise them as
file sizes, API behavior, and review effort become measurable.

## Goal and fixed decisions

- Use the newest available version of each topic or artifact. Include older
  material only as a complete topic that newer sources do not cover; record
  its source and version in the crosswalk.
- The user's updated selection preference is topic-level: when Fall covers a
  topic, use its complete Fall sequence and avoid cherry-picking isolated old
  slides or anecdotes. Include a complete Spring topic/deck when it is absent
  from Fall, with any older-only source, schedule, homework, and build details
  mapped as a whole. Do not add an older subtopic, example, criterion, or case
  study as a supplement inside a Fall-covered topic. Reconsider older content
  only if it is a complete topic Fall does not cover.
- Preserve original order. **Never split an original source deck or a topic.**
  A block boundary is valid only after a complete source deck and a complete
  topic. Keep adjacent decks together when one topic spans them; keep an
  entire deck together when it covers several topics.
- First identify ordered, indivisible deck/topic groups. Assess four
  contiguous output blocks, then eight or sixteen only if measured import,
  file-size, or review constraints call for them. These are packaging counts,
  not equal-slide targets. Let block sizes vary. Do not cut a deck or topic to
  satisfy a size target.
- Use the current syllabus and course sequence for placement. If sixteen
  blocks are useful, consult the previous course's schedule to estimate
  roughly one class week per block; keep topics and decks whole when a topic
  spans the estimated week boundary.
- Preserve text, code, shapes, diagrams, pictures, and notes as editable
  objects where reliable. For text-fit problems, inspect width, height, and
  insets before reducing font size. Keep an image fallback limited to the
  smallest element that remains unreliable; whole-slide images are a last
  resort.
- Convert meaningful instructional animation or reveal builds into
  sequential static slides in the original build order. Map every generated
  slide to its source slide and build state. Keep the expanded sequence within
  its source deck/topic group; final output count can exceed 2,235.
- Pace Google Drive calls serially. Leave at least five seconds between
  import, structural read, export, and fetch operations, and wait longer after
  slow responses or rate-limit signals. Validate each block before uploading
  the next.
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
- The Fall `Test Anatomy` PDF and Keynote source were obtained for source
  reconciliation. LibreOffice 7.3.7.2 produced no PPTX from the `.key` or
  `.pdf` input; a new test of the 37-page Fall Test Anatomy PDF explicitly
  returned `no export filter` for PPTX output. No empty output is treated as a
  conversion. A no-install alternative has been identified: export a PPTX
  copy in Apple's Keynote for iCloud browser, then import that into Slides.
  Google Drive can store `.key` files but its documented import formats for
  Slides are PowerPoint and OpenDocument Presentation, not Keynote. This Apple
  browser route remains untested on course material; pilot one deck and verify
  build expansion, notes, editability, and appearance before using it at scale.
  Follow the user's preference to avoid installing an additional Linux
  converter while this route is available. See the
  [runbook](combined/SLIDE_CONVERSION.md#produce-an-editable-powerpoint-on-linux).
- The nine local editable batch PowerPoints now sit directly in
  `out/combined/`, with ranges in `editable-parts-manifest.json`. All 17
  Google presentations formerly at the shared folder root were confirmed by
  metadata as pilots or disposable tests and moved into its `Pilots`
  subfolder. The shared folder root is reserved for final batches. The local
  and Drive locations are described in the
  [pilot folder guide](combined/google-slides-pilot/README.md).
- All five project Markdown files, four Python scripts, source maps, manifests,
  and working folders are linked from the [root README](README.md).
- The initial source crosswalk is at
  [source-version-crosswalk.csv](combined/source-version-crosswalk.csv). It
  maps the 19 Fall lecture PDFs and the separate Integration Testing Bad PDF
  to candidate current sections. Use the source-deck and older-topic audits
  for the recorded use/exclude decisions; this crosswalk remains a page-level
  provenance and source-map aid. **Correction from the
  metadata audit:** the Fall PDFs (August–November 2026) postdate the
  Spring-centered Keynote candidates (January–August 2026). Use Fall content
  as the latest source where it covers the same material; page-level source
  mapping and identification of complete older topics absent from Fall still
  require comparison.
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
| 1 | **Complete 2026-11-25.** Record content-selection outcomes for all 57 source-deck candidates. The older-topic audit now separately includes complete Verified Distributed Systems and Semantic/Latent Concurrency Bug Detection units; the mixed Regression/Integration and stale Fall 2025 Review decks are excluded whole. | 2–4 hours · medium | Each candidate has a recorded use/exclude decision and evidence; source-level build mapping remains a separate conversion task. See the [source-deck audit](combined/source-deck-topic-audit.csv) and [older-topic audit](combined/older-topic-selection-audit.csv). |
| 2 | **Complete 2026-11-25.** Resolve the concurrency build around combined slides 205–206 using the latest Keynote export and the existing Round 4 Google PDF. | 45–90 min · medium | Confirmed: Keynote export pages 19–20 and Google PDF pages 205–206 show the first comic panel followed by the complete comic. Two distinct picture/crop objects preserve the ordered build; no new import is needed. See the [build audit](combined/SLIDE_CONVERSION.md#animationbuild-audit-combined-slides-205206). |
| 3 | **Complete 2026-11-25 (technical pilot only).** Reconstruct four older Test Case Minimization pages to test editable math and Google font rendering. | 45–90 min active · medium | Rev2 readback confirmed four ordered editable slides with no images; all four Google PDF pages were inspected. Round 12 is a conversion-method sample, not a commitment to include these pages in the final content; current selection defaults to the complete Fall TCM topic. |
| 4 | Prove an editable, no-install export route for the latest Fall Keynote source on a small pilot. Use the Aug 31 Fall-branch Final Review deck first; check source/build order, notes, editability, and appearance, and replace its stale May 8/HW3–5 announcements with Fall syllabus values. | 1–3 hours active · low | A PowerPoint made from the Fall `.key` imports into Google Slides with ordered editable objects, mapped build states, and notes; its PDF is visually reviewed. If the Keynote-for-iCloud route is unavailable, stop scale conversion and test another permitted route. |
| 5 | Import the integrated Part 1 into Google and measure import, read, PDF export, and review time. | 45–90 min · low | Native readback confirms count and order; one saved Google PDF is reviewed and compared with the baseline. |
| 6 | **Complete 2026-11-25.** Verify Part 2 rev3: 232-slide native readback, Google PDF, and full-page regression comparison against rev2. | 30–90 min · low | 232 slides/pages confirmed. Only the intentional fixes on slides 214 and 216 changed; both rendered panels and editable text were reviewed. Evidence is linked from the [Drive guide](combined/GOOGLE_DRIVE_ACCESS.md#part-2-scale-import-and-pdf-transfer). |
| 7 | **Complete 2026-11-25 (source/conversion pilot).** Import the complete Fall Lab 1 tutorial, expand and map its builds, verify native order/notes, and inspect the Google PDF. | 45–90 min active · medium | Complete: 40 source slides became 62 ordered slides; paragraph states 8/6/11 and the AFL screenshot zoom pair are mapped. All 62 Google PDF pages were inspected. Spring Lab 2 tutorial is comparison-only. The Oct 30 handout vs Nov 3 syllabus deadline conflict remains open. See [Round 13](combined/SLIDE_CONVERSION.md#round-13--fall-lab-1-fuzzing-source-and-build-mapping). |
| 8 | **Complete 2026-11-25 (older-topic import pilot).** Import the complete archived concurrency-testing lab introduction, map it, and compare every Google-rendered page with the PPTX source. | 45–90 min active · medium | Complete: 28 ordered slides and 28 Google PDF pages; all pages visually reviewed against the source's local diagnostic PDF. No layout repair needed. The source has no notes or timed animation. See [Round 14](combined/SLIDE_CONVERSION.md#round-14--older-concurrency-testing-lab-introduction). |
| 9 | Finish source-level conversion maps for the selected Fall sequence and older-only complete topics, then build the topic-ordered candidate decks. Reconcile each exact `.key` revision against current PDFs, notes, skipped-slide flags, and meaningful build states. | 2–4 working days · low | Every output slide maps to its authoritative source, original slide, notes, and build state; every included topic/deck remains whole; stale course details are corrected from the current syllabus. |
| 10 | Validate the no-curl path for a native Google PDF over 10 MB through Drive `files.download` long-running operation (LRO), then materialize the returned file reference locally. | 30–90 min · low | Google documents the LRO export route for Slides PDFs; the connector's >10 MB materialization remains untested. Do not split topics or decks to meet the separate 10 MB `files.export` response limit. |
| 11 | Convert and upload all reconciled material, beginning with four contiguous blocks and increasing to eight or sixteen only when measured constraints require it. | Roughly 3–6 working days after the gates above · low | Each block has a verified manifest, mapped source/build states, local checks, native readback, and a page-reviewed Google PDF before the next upload. Re-estimate after the first accepted block; API waiting time is additional. |

## Current open issues

- Round 11 fixes slides 115–116, but other CFG layouts and similar labels need
  validation before applying the no-wrap/inset rule broadly. The open queue
  is maintained in the [runbook](combined/SLIDE_CONVERSION.md#open-work-after-round-14).
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
- Content-selection decisions are now recorded for all 57 candidate rows.
  The Fall-branch Final Review deck (commit `32a585f`, Aug 31) is selected,
  but its existing combined map predates that revision and its first slide
  still contains May 8/HW3–5 administration. Two older complete topics
  (Verified Distributed Systems and Semantic/Latent Concurrency Bug Detection)
  are selected whole; both still need source/build maps and conversion pilots.
- The 31-slide older Regression/Integration deck is excluded because the
  complete Fall Test Anatomy and Regression Testing sources cover its topics.
  The separate 17-page Integration Testing Bad draft is also excluded: Fall
  Test Anatomy labels its older integration strategies as old/broken and
  replaces them with explicit contracts.
- A no-install `.key`-to-editable-PowerPoint export for current Fall sources
  is still untested. The candidate Keynote-for-iCloud route must pass a small
  source pilot before the 2,000+ slide conversion proceeds.
- Native text replacement and the tested line-position transform are
  verified. Native line-style updates, other diagram types, freeform path
  edits, image crops, tables, equations, and speaker-note edits need separate
  tests on disposable copies.
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
  untested. Do not split whole topics/decks to meet the direct-export cap;
  split only for measured packaging/import/review constraints. Never use
  `curl` or another shell/network downloader. See the
  [Drive transfer guide](combined/GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf).
- The November 25 read-only listing of the designated Drive folder now
  succeeds: its visible root contains the `Pilots` subfolder, and the nested
  listing returns the pilot presentations. No final batch deck appeared in
  the root listing. Two calls were serialized with more than five seconds
  between them. This supersedes the earlier transient connector failure. See
  the [Drive guide](combined/GOOGLE_DRIVE_ACCESS.md#share-and-connect-the-folder).
- The nine existing editable batches each end at a complete source-deck
  boundary, but their topic-boundary alignment has not yet been fully mapped.
  Do not assume those files are final upload blocks.
- The 2,235-slide Spring-centered set is still only the comparison baseline,
  not the final selected order. All 57 candidate rows now have content
  decisions, but the final Fall/older source sequence, exact source/build
  maps, and converted output have not been assembled. Keep the full-scale
  conversion gate closed until the Keynote export pilot and source maps pass.
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
  This does not prove slide/build equivalence. The older-topic audit identifies
  complete older additions under review: concurrency lab introduction,
  record/replay, deterministic execution, and a static-testing-tools survey.
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
  `22-408st-static-analysis.key` and the syllabus schedules two lectures, but
  no corresponding PDF is present; a diagnostic LibreOffice export produced
  no PDF. Export the complete Fall deck and replace its stale April 24
  Project 2/HW5 announcements with Fall values (HW6 due Dec 4 at 6 PM; Project
  2 due Dec 6). Do not append older slides 1831–1840 as isolated supplements.
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
  Fall PDFs. LO also included material absent from the selected PDFs: an
  Introduction submission slide and extra Admin/Teaching Staff slides, plus
  an Admin/review block before Fault/Error/Failure's Game Plan. Some repeated
  pages may be animation states; confirm using Keynote visibility/build data
  before including them. LO damaged the schedule and grading tables, so its
  PDF is not acceptance visual evidence. Headless `.key` to `.odp` and
  `.pptx` conversions produced no output. Apple's Keynote for iCloud is the
  current no-install conversion candidate; it still needs a controlled pilot
  and Google readback before it can be considered reliable.
- The complete Fall `Test Anatomy` source supersedes the older mixed
  Regression/Integration deck's integration portion. The separate 17-page
  `Integration Testing Bad` draft is also excluded after comparison: Fall Test
  Anatomy pages 32–34 label its traditional strategies old/broken and pages
  35–36 teach explicit component contracts.
- Part 2 rev3 passed visual scale review: 232-slide order/readback, 232-page
  Google PDF, and page comparison. The fix and evidence are recorded in the
  [runbook](combined/SLIDE_CONVERSION.md#part-2-scale-validation-revision-3).

## Next action

The content-selection gate is closed for the 57 candidate rows. The next gate
is a small editable export pilot using the Fall-branch
`23-408st-final-review.key` (commit `32a585f`), followed by source/build maps
for the selected Fall sequence and older-only units. Map meaningful animation
states, speaker notes, and skipped slides against the exact Fall file; do not
reuse a Spring map where the Fall branch blob differs. Keep every included
source deck and topic whole.
The 31-slide Verified Distributed Systems and 18-slide Semantic/Latent
Concurrency Bug Detection units join the already selected Record and Replay,
Deterministic Execution, Static Testing Tools, and archived Concurrency Lab
topics as complete older-only units. Their source decisions are recorded in
the [older-topic audit](combined/older-topic-selection-audit.csv); conversion
has not started. Round 14 confirmed the archived concurrency-lab introduction as a 28-slide
editable Google import with no conversion repair needed. Its slide deadline
and Classroom URL match the Spring 2026 handout, which is already included in
the study guide. The source screenshots on slides 4–6 still show `CS503 Spring
2021`; update or clearly label those old assignment screens before final
integration, then retain the handout as companion reading without duplicating
it as slides.

In parallel, the conversion gate for the current Fall Static Analysis source
remains a browser export of `slides/22-408st-static-analysis.key` through
Keynote for iCloud to PPTX (and PDF for visual comparison). Google Slides
cannot convert `.key` directly, and the installed LibreOffice produced no
output for the Keynote source. No additional Linux converter is required;
allow about 30–60 minutes after a PPTX export is available to map visible
slides/builds and replace the April 24 announcements. Older Static Analysis
pages remain a separate earlier-offering topic, not additions to the Fall
lecture.

Finish the source crosswalk using the whole-topic rule. For overlapping
topics—including Introduction, Fault/Error/Failure, Static Analysis, Test
Case Minimization, ISP, Symbolic Execution, and Concolic Execution—select the
complete Fall source and do not add isolated older examples, criteria, or case
studies. Identify complete Spring topics Fall does not cover and map each
entire source deck, homework, schedule context, and meaningful build states.
Round 12 remains a technical conversion pilot only. Both page-text reports
([Fall to current](combined/fall-current-text-overlap.csv),
[current to Fall](combined/current-fall-text-overlap.csv)) are only triage aids:
compare
official Fall PDF pages, Keynote source builds/notes, current editable objects,
and the Google baseline. Then build an editable Fall Introduction pilot from
its complete Fall source, with a slide map covering every page and build state.
Import and visually validate that pilot
before applying its conversion method to the next deck. Keep LibreOffice
rendering diagnostic only where it distorts the selected Fall appearance;
205–206 is already verified and need not be repeated.
