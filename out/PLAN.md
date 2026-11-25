# CS 408 slide conversion plan

**Updated:** 2026-11-25  
**Status:** Round 11 revision 4 passed its three-slide Google roundtrip; the
205–206 concurrency build sequence is verified in the Round 4 Google PDF.
Part 2 (232 slides) is imported as native Google Slides and structurally
read back with 232 ordered slide objects. Part 2 rev3's 232-page Google PDF
was materialized through the connector helper without curl. All pages were
compared with rev2: 230 are pixel-identical and only the repaired panels on
slides 214 and 216 differ. Both repairs preserve editable text. The Fall/current
source crosswalk remains open; its 20 Fall PDF sources are now confirmed on
`origin/fall+2026` and extracted to `.build` for comparison. Full conversion
verification is not complete.

**Working branch:** `spring+2027+bianchi`, based on the newest available
course branch, `origin/fall+2026` at `900304aa` (2026-11-15). Its selected
documentation, scripts, and compact maps are being added; generated slide
decks and PDFs remain local and unadded because of their size.

This is the live plan for converting the 2,235-slide collection into reliable,
editable Google Slides. Update it after each major milestone and about hourly
during active work. Estimates are hands-on time unless noted; revise them as
file sizes, API behavior, and review effort become measurable.

## Goal and fixed decisions

- Use the newest available version of each topic or artifact. Keep older
  material only when useful content is absent from newer sources; record its
  source, version, and reason for retention.
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
  reconciliation. LibreOffice 7.3.7.2 silently produced no PPTX from either
  `.key` or `.pdf` with `--convert-to pptx`; no output is being treated as a
  conversion. Choose an editable conversion route or retain only demonstrably
  unique content after the Fall/current comparison.
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
  to candidate current sections. It is not a final selection: content-level
  comparison and keep/replace decisions remain open. Several current Keynotes
  have later save dates than the Fall PDF exports.
- On 2026-11-25 the repository was switched to `spring+2027+bianchi`, based
  on the newest source branch, `origin/fall+2026` at `900304aa`. Local tracking
  branches were created for all four pre-existing branches so `git branch`
  lists the full set.
- The 20 Fall source PDFs (19 numbered lectures plus the Integration Testing
  Bad draft, 956 pages total) are stored on `origin/fall+2026` under
  `slides/f26-pdfs/`. They were extracted into `out/.build/fall-source/`
  without changing branches. All actual page counts matched the expected
  counts; the compact audit is
  [fall-source-metadata.csv](combined/fall-source-metadata.csv). Content-level
  comparison and keep/replace decisions remain open.

## Planned work and estimates

These estimates exclude waiting time between API calls and assume each pilot
needs no unexpected repair cycle. Confidence is lower for untested Google
behavior and for full-deck visual review.

| Order | Work | Estimate | Exit condition |
| ---: | --- | --- | --- |
| 1 | Reconcile the Spring-centered 2,235-slide set against Fall 2026 and other newer course material. Build a topic/source crosswalk, remove superseded material, and mark useful older-only content with its reason. | 2–4 hours for the first pass · medium | Every selected topic has an authoritative newest source; older unique additions are recorded; the sequence and scope are ready for pilots. Re-estimate after the first deck family. |
| 2 | **Complete 2026-11-25.** Resolve the concurrency build around combined slides 205–206 using the latest Keynote export and the existing Round 4 Google PDF. | 45–90 min · medium | Confirmed: Keynote export pages 19–20 and Google PDF pages 205–206 show the first comic panel followed by the complete comic. Two distinct picture/crop objects preserve the ordered build; no new import is needed. See the [build audit](combined/SLIDE_CONVERSION.md#animationbuild-audit-combined-slides-205206). |
| 3 | As the source crosswalk proceeds, identify the next animation/build family not already represented by an accepted Google roundtrip. Create Round 12 only for that family, with an unaffected control and an exact source map. | 45–90 min active · medium | Google readback and PDF show the mapped states in order; the runbook records which source version and build states were used. |
| 4 | Build the Part 1 candidate from the selected latest sources, carrying forward Round 5–11 repairs only where their source slide remains current and equivalent. The Round 4 260-slide file is the comparison baseline; verified build-state expansion may increase the candidate count. | 2–4 hours · medium | Local package and map checks pass; every change is source-mapped; controls remain unchanged; affected pages are reviewed. |
| 5 | Import the integrated Part 1 into Google and measure import, read, PDF export, and review time. | 45–90 min · low | Native readback confirms count and order; one saved Google PDF is reviewed and compared with the baseline. |
| 6 | **Complete 2026-11-25.** Verify Part 2 rev3: 232-slide native readback, Google PDF, and full-page regression comparison against rev2. | 30–90 min · low | 232 slides/pages confirmed. Only the intentional fixes on slides 214 and 216 changed; both rendered panels and editable text were reviewed. Evidence is linked from the [Drive guide](combined/GOOGLE_DRIVE_ACCESS.md#part-2-scale-import-and-pdf-transfer). |
| 7 | Resolve the Fall/current source crosswalk and animation-state map. | 2–4 hours · medium | Every retained slide group has a newest source and all useful older-only additions have a placement and reason. |
| 8 | Validate the no-curl path for a native Google PDF over 10 MB. Prefer topic-safe blocks below the export limit, up to 16 total; use browser transfer only if a single indivisible block remains too large. | 30–90 min · low | Local Google renders are materialized and validated without shell networking; preserve whole source decks and topics. |
| 9 | Convert and upload all reconciled material, beginning with four contiguous blocks and increasing to eight or sixteen only when measured constraints require it. | Roughly 1–3 working days after the gates above · low | Each block has a verified manifest, mapped source/build states, local checks, native readback, and reviewed Google PDF before the next upload. Re-estimate after the first accepted block. |

## Current open issues

- Round 11 fixes slides 115–116, but other CFG layouts and similar labels need
  validation before applying the no-wrap/inset rule broadly. The open queue
  is maintained in the [runbook](combined/SLIDE_CONVERSION.md#open-work-after-round-11).
- Slide 153's unchanged Round 10 control retains visible markers from empty
  bullet paragraphs. Inspect related list layouts before applying a general
  cleanup.
- Other layout work remains on slides 70, 117–125, 128, 176–182, 186,
  238, 244, and 253. The 205–206 concurrency build is verified and removed
  from the open queue; see the [runbook audit](combined/SLIDE_CONVERSION.md#animationbuild-audit-combined-slides-205206).
- Native text replacement and the tested line-position transform are
  verified. Native line-style updates, other diagram types, freeform path
  edits, image crops, tables, equations, and speaker-note edits need separate
  tests on disposable copies.
- The no-curl connector helper path is now verified for a 9.9 MB Google PDF:
  wrapping `google_drive_fetch` to request `include_base64: true` lets the
  export-and-render helper materialize the bytes in chunks without a signed
  URL. A streamed `include_base64: false` response still yields only a
  `file_uri` in this environment. The >10 MB path remains open; use up to 16
  whole-deck/topic blocks sized below the export limit before considering the
  authenticated browser. Never use `curl` or another shell/network downloader.
- The nine existing editable batches each end at a complete source-deck
  boundary, but their topic-boundary alignment has not yet been fully mapped.
  Do not assume those files are final upload blocks.
- The Spring-centered 2,235-slide set has not yet been reconciled topic by
  topic against Fall 2026 material for final source selection. Keep the
  full-scale conversion gate closed until the crosswalk identifies what is
  newer, what is superseded, and which older content remains unique.
- The [Fall source crosswalk](combined/source-version-crosswalk.csv) references
  20 PDFs under `slides/f26-pdfs/`. They are present on
  `origin/fall+2026` (the base of the current branch), not in its checked-out
  tree. All 20 were extracted with `git archive` to `out/.build/fall-source/`;
  their metadata and page counts are recorded in
  [fall-source-metadata.csv](combined/fall-source-metadata.csv). All 956 pages
  matched the expected counts. Content-level keep/replace decisions remain
  open; no individual Fall PDF is missing from the available Git history.
- The Fall `Test Anatomy` PDF has no exact title match in the current source
  map, and `Integration Testing Bad` is marked as a draft. Verify their
  content against current intro/testing material and keep them only where
  they add useful, non-superseded content.
- Part 2 rev3 passed visual scale review: 232-slide order/readback, 232-page
  Google PDF, and page comparison. The fix and evidence are recorded in the
  [runbook](combined/SLIDE_CONVERSION.md#part-2-scale-validation-revision-3).

## Next action

Continue the Fall/current source comparison using the full study guide at
[`out/cs408-study-guide.pdf`](cs408-study-guide.pdf), the extracted PDFs at
`out/.build/fall-source/slides/f26-pdfs/`, and the Spring source decks. Start
with introduction and fault/error/failure, mark exactly which Fall page ranges
are represented, superseded, or unique, and record supporting slide/page
evidence. Then select the next unverified animation family for a small Google
roundtrip; 205–206 is already verified.
