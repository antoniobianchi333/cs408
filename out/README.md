THE MOST IMPORTANT THING IS THAT I NEVER STOP UNTIL ALL THE SLIDES ARE CONVERTED AND TESTED!!!!!!!!!!!!!

# COMPLETION REQUIREMENT — DO NOT STOP EARLY

**Keep working until all slides in the final reconciled course set—including
every complete older topic absent from Fall and every meaningful animation
state—have been converted to Google Slides and verified against their
sources and Google exports. Do not stop after documentation, planning,
pilots, or partial batches.**

The final delivery target is **16 conceptual batches**, roughly one lecture
week each. Keep every original source deck and topic whole; adjust batch slide
counts to preserve those boundaries.

**Finish batches in order.** Complete Batch 1 end to end—source/build map,
conversion, repairs, local checks, Google import, native readback, Google PDF,
page-by-page review, and documentation—before beginning Batch 2. Apply the
same gate to each following batch. Every full batch deck, including its WIP
working copy, belongs directly in the shared Google Drive folder root, one
level above `Pilots`. Mark unfinished decks `WIP - needs fixes` and rename
them only after acceptance. Use `Pilots` only for small isolated test decks.

**Google file-transfer rule:** Never use `curl` or another shell/network
downloader for Drive files or signed references. Use the connected Drive
stream, authenticated browser download, or paced native thumbnails. Keep Drive
requests paced and cut batches only between complete source decks and topics.
The exact cause and recovery steps are in
[the Drive access guide](combined/GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf).

**Required separator-slide style:** Put one editable separator before every
original source deck in a final batch. Give it a full-slide, solid pale-yellow
`#FFF2CC` background, a centered exact source filename in 24 pt bold Arial,
and the following topic in centered 28 pt regular Arial. Keep both text boxes
editable and give them explicit rectangle geometry so Google Slides retains
them. This larger, high-contrast style makes deck boundaries easy to spot.
The [batch boundary rules](combined/BATCH_BOUNDARIES.md) and
[conversion runbook](combined/SLIDE_CONVERSION.md#round-24--batch-1-divider-import-and-visual-standard)
record the implementation and import check.

# CS 408 Software Testing materials

This directory holds two CS 408 resources:

- The Fall 2026 study guide is a reading PDF with lectures, exercises, and
  course maps.
- The editable Slides project starts from a 2,235-slide candidate collection
  built around the Spring 2026 sequence and earlier material. Source selection
  is complete: use the full Fall 2026 source wherever it covers a topic, and
  add only complete older topics absent from Fall. The 57-deck decisions and
  six older-only topics are recorded in the [source-deck audit](combined/source-deck-topic-audit.csv)
  and [older-topic audit](combined/older-topic-selection-audit.csv). The
  2,235 slides are a comparison baseline, not the final selected output.

The conversion goal is to preserve lesson content, slide order, and notes
while keeping text, code, diagrams, and pictures usable as separate objects
in Google Slides. Meaningful instructional animation builds should become
sequential static slides in build order, with each generated slide mapped to
its source slide and build state. The delivered slide count may therefore
exceed the 2,235-slide source count.

For `.key` source files on Linux, use a matching full-deck PDF as the main
visual reference wherever one exists. The 57 Keynote packages include a
single-slide `preview.jpg`, not a full-deck PDF; PDFs embedded under `Data/`
are individual placed assets. The 20 files in `slides/f26-pdfs/` include 19
lesson PDFs and the excluded `Integration+Testing+Bad` draft. They do not cover
every selected Fall Keynote, and the Test Anatomy PDF predates the latest
Keynote. The exact gaps and the Round 15–17 diagnostics and repairs are in the
[runbook](combined/SLIDE_CONVERSION.md#fall-pdf-coverage-and-keynote-preview-limits).

## Documentation and workflow

| Step | Instructions | What to keep |
| --- | --- | --- |
| 1. Locate the source | Use the [combined collection guide](combined/README.md) to map a combined slide number to its source deck, saved build, and editable batch. | The matching Keynote or PowerPoint, source PDF, and combined slide numbers. |
| 2. Build and diagnose the current batch | Follow the [conversion runbook](combined/SLIDE_CONVERSION.md). Reuse verified rules; create only small pilots for unfamiliar slide families. Add one full-slide solid pale-yellow (`#FFF2CC`) editable divider before every original source deck. Center the exact source filename in 24 pt bold Arial and the following topic in 28 pt regular Arial. Map each divider separately. Build and repair the reproducible PPTX locally before import. | The current batch PPTX, its ordered source/build map, divider rows, and local diagnostics. |
| 3. Upload and verify in Google | Use the [Google Drive guide](combined/GOOGLE_DRIVE_ACCESS.md) for paced imports, native readback, PDF export, and the browser fallback. Put every full-batch WIP or accepted deck directly in the shared folder root; put only small isolated tests in `Pilots`. | The batch's native deck URL, structural readback, Google PDF, and page-by-page review. |
| 4. Compare and improve | Follow the [roundtrip checks](combined/SLIDE_CONVERSION.md#run-and-evaluate-a-google-roundtrip) and run the [local audit script](combined/google-slides-pilot/audit_conversion_pilot.py). Check page order, content and code, image crops, graph endpoints, and actual editability. Record where each defect first appeared and retest the smallest repair. Periodically delete per-slide PNG renders when the matching PDF can recreate them; keep review contact sheets, active exception images, repair crops, and source media. | The comparison result, a reusable repair rule, any exceptions, and what remains open. |
| 5. Apply verified repairs to the batch | Keep one full-batch WIP deck in the shared Drive root and apply confirmed visual fixes in that same native deck. Keep the local PPTX and maps as the reproducible source; use local rebuilds when a structural or content change requires them, then reconcile the WIP deck and verify the affected order/pages. | A versioned WIP deck, its PDF comparison, and an updated runbook. |

## Project documents

- [Overall completion goal and project rules](../GOAL.md) — read this file, but
  do not edit it unless the user explicitly asks.
- [Copy-ready prompt for a fresh session](../PROMPT.md)
- [Live plan and time estimates](PLAN.md)
- [Last-resort manual Keynote-to-PDF request list](MANUALLYCONVERT.md)
- [Codex usage reader for the live status report](../codex_usage.py)
- [Live Google Drive `STATUS` document](https://docs.google.com/document/d/1TAFn9A9Nkkr8YU8R0Hpfge4Q7MBOvBPT4F7XHiDG9UU/edit)
  — native Google Doc, verified directly in the CS 408 project folder root
  above `Pilots`; refresh it hourly using the ordered fields in
  [the live plan](PLAN.md#required-live-status-document).
- [Branch, restart-kit, and artifact-tracking policy](BRANCH_AND_HANDOFF.md)
- [Combined slide collection and source map](combined/README.md)
- [Final 16-batch boundaries and deck/topic sequence](combined/BATCH_BOUNDARIES.md)
- [Final batch workspace and acceptance records](combined/final-batches/README.md)
- [Batch 1 current diagnostic and unresolved pages](combined/final-batches/batch-01-diagnostic.md)
- [Local and Drive pilot artifact organization](combined/google-slides-pilot/README.md)
- [Batch 1 Keynote order/build decoder](combined/audit_keynote_build_sequences.py),
  with [Introduction sequence audit](combined/final-batches/batch-01-introduction-build-sequences.csv)
  and [Fault/Error sequence audit](combined/final-batches/batch-01-fault-error-build-sequences.csv)
- [Build-state expander](combined/expand_batch_build_states.py),
  [small-pilot PPTX slide/package pruner](combined/prune_pptx_slides.py), and
  [Batch 1 build-state decisions and chunk map](combined/final-batches/batch-01-build-expansion.json)
- [Conversion runbook, pilot logs, and reusable repair rules](combined/SLIDE_CONVERSION.md)
- [Google Drive access and paced upload/export workflow](combined/GOOGLE_DRIVE_ACCESS.md)

## Branch and restart policy

The active working branch is `spring+2027+bianchi`. It starts at
`others/fall+2026` commit `900304aa` (November 15, 2026), the newest of the
four pre-existing course branches. `spring+2026`, `new-lab2-dev`, and
`project1-ai-policy` are ancestors of Fall 2026; the latter two changes are
already merged into Fall. Local tracking branches now exist for all four
source branches, so plain `git branch` lists them together with the new
working branch.

The Git config identifies `others` (`git@github.com:bendy/cs408.git`) as the
source remote and `bianchi` (`git@github.com:antoniobianchi333/cs408.git`) as
the Bianchi remote. **The user handles commits and pushes. Never commit or
push unless the user explicitly instructs it.** Do not push to either remote
without that explicit instruction; when a push is requested, use the Bianchi
remote if that is still what the Git config specifies.

Keep the new branch as a **restart kit**, not a second archive of every large
processed slide file. A future agent with this repository and access to the
documented Google Drive folder should be able to understand the goal, find the
authoritative sources, reproduce repairs, inspect maps and QA evidence, and
continue uploads. Add all current project Markdown, conversion/audit scripts,
source maps, manifests, compact comparison reports, and small evidence needed
to resume the work. Keep generated full-size PDFs, PPTX decks, page renders,
and extracted temporary source copies out of Git when they are large; store
durable processed/pilot decks and review PDFs in the documented Drive
`Pilots` folder, and final batch decks in the Drive root. Do not assume a local
untracked file is already on Drive: verify the Drive file by name, ID, and
metadata before relying on it. The precise inclusion rules and current branch
inventory are in [BRANCH_AND_HANDOFF.md](BRANCH_AND_HANDOFF.md).

## Working artifacts, scripts, and folders

- [Combined collection folder](combined/), [collection guide](combined/README.md),
  [source map CSV](combined/sources.csv), [source map JSON](combined/sources.json),
  [Fall 2026 source-version crosswalk](combined/source-version-crosswalk.csv),
  [Fall PDF metadata/page-count audit](combined/fall-source-metadata.csv), and
  [Fall Keynote source inventory](combined/fall-keynote-inventory.csv),
  [57-deck Fall/Spring topic audit](combined/source-deck-topic-audit.csv), and
  [branch-level source blob comparison](combined/source-branch-diff-audit.csv),
  generated by
  [audit_source_branch_diffs.py](combined/audit_source_branch_diffs.py), plus
  [Fall-page-to-current-slide report](combined/fall-current-text-overlap.csv),
  [current-slide-to-Fall-page report](combined/current-fall-text-overlap.csv),
  and [per-topic overlap summary](combined/fall-topic-overlap-summary.csv)
- [Final batch workspace](combined/final-batches/), including the
  [Batch 1 diagnostic findings](combined/final-batches/batch-01-diagnostic.md),
  Introduction [provisional page map](combined/final-batches/batch-01-introduction-provisional-page-map.csv),
  [candidate audit](combined/final-batches/batch-01-introduction-candidate-audit.csv),
  and [build-marker audit](combined/final-batches/batch-01-introduction-build-marker-audit.csv),
  Fault/Error [provisional page map](combined/final-batches/batch-01-fault-error-provisional-page-map.csv),
  [candidate audit](combined/final-batches/batch-01-fault-error-candidate-audit.csv),
  and [build-marker audit](combined/final-batches/batch-01-fault-error-build-marker-audit.csv),
  durable sequence/build maps, plus the
  [alignment audit script](combined/audit_batch_source_alignment.py) and
  [unmatched-slide contact-sheet script](combined/render_unmatched_contact_sheets.py),
  [Keynote build-marker audit](combined/audit_keynote_build_markers.py), and
  [batch-candidate builder](combined/build_batch_candidate.py) with its
  [Batch 1 input manifest](combined/final-batches/batch-01-inputs.json), plus
  [Batch 1 Introduction text repair](combined/repair_batch01_introduction.py),
  [Batch 1 Fault/Error repairs](combined/repair_batch01_fault_error.py), and
  [page 18 image/build reconstruction](combined/prepare_intro_page18_build.py)
- [Legacy editable batch baselines](combined/) and their
  [batch manifest](combined/editable-parts-manifest.json). The manifest keeps
  the nine-part comparison mapping; generated PPTX/PDF inputs are rebuildable
  artifacts and belong under ignored `.build/` when present. They are not the
  final 16 Google Drive batches.
- [Pilot artifacts folder](combined/google-slides-pilot/), including the
  [pilot folder guide](combined/google-slides-pilot/README.md),
  [Round 2 rebuild](combined/google-slides-pilot/rebuild_round2.py),
  [Round 4 rebuild/helpers](combined/google-slides-pilot/rebuild_round4.py),
  [pilot rebuild script](combined/google-slides-pilot/rebuild_conversion_pilots.py),
  [Part 2 panel repair script](combined/google-slides-pilot/repair_part02_contrast_panels.py),
  [Part 2 media/z-order repair script](combined/google-slides-pilot/repair_part02_media_and_zorder.py),
  [Round 12 editable-supplement builder](combined/google-slides-pilot/rebuild_tcm_supplement_round12.py),
  [Round 13 Fall Lab 1 builder](combined/google-slides-pilot/build_fall_lab1_pilot_round13.py)
  and [Round 13 slide/build map](combined/google-slides-pilot/cs408-fall-project-1-pilot-round13-map.csv),
  [Round 14 older-topic map](combined/google-slides-pilot/cs408-concurrency-lab-intro-round14-map.csv)
  and [Round 14 review folder](combined/google-slides-pilot/cs408-concurrency-lab-intro-round14-review/),
  [Round 14 rev2 builder](combined/google-slides-pilot/build_concurrency_lab_round14_rev2.py),
  and [Round 14 rev3 builder](combined/google-slides-pilot/build_concurrency_lab_round14_rev3.py),
  [Round 15-to-16 repair script](combined/google-slides-pilot/repair_round15_keynote_layout.py)
  and the [Round 16 page map](combined/google-slides-pilot/cs408-fall-test-anatomy-round16-map.csv),
  and [Round 16 review folder](combined/google-slides-pilot/cs408-fall-test-anatomy-round16-review/),
  [Fall text-overlap audit script](combined/audit_fall_text_overlap.py),
  [source-deck topic audit script](combined/audit_source_deck_topics.py), and
  [older-topic selection audit](combined/older-topic-selection-audit.csv), plus
  [local conversion audit script](combined/google-slides-pilot/audit_conversion_pilot.py)
- [Legacy combined-slide manifest and mapping](combined/editable-parts-manifest.json)
  and [image-based part manifest](combined/import-parts.json). The generated
  combined PPTX/PDF files are not in this checkout; keep rebuildable binaries
  in ignored `.build/` rather than `out/combined/`.
- [Google Drive Pilots folder](https://drive.google.com/drive/folders/1PHuKHahwY2PxviNWTM2f8kYmb7K-37Dj)
  contains the historical pilot and disposable decks. The shared Drive
  folder root is reserved for final batch decks.
- [Temporary local render and audit work](.build/). Keep rebuildable PPTX,
  PDF, render, and transfer files here, ignored by Git. Keep durable scripts,
  maps, manifests, and compact reports in `combined/`; keep only small live
  test decks in Drive `Pilots` and full-batch WIP/accepted native decks in the
  shared Drive root.

## Current conversion status

**Required live status document:** keep a single editable Google Doc titled
`STATUS` directly in the CS 408 project Drive folder root, above `Pilots`.
Refresh it about hourly during sustained work and after major milestones. Its
sections must stay in this order: pending permissions; current code-usage
percentages from [`codex_usage.py`](../codex_usage.py); current work and the
near-term plan; the complete [manual conversion list](MANUALLYCONVERT.md); and
the complete [plan](PLAN.md). Use the connected Drive tools only in the
documented CS 408 project folder. The live document is
[STATUS](https://docs.google.com/document/d/1TAFn9A9Nkkr8YU8R0Hpfge4Q7MBOvBPT4F7XHiDG9UU/edit)
(Drive ID `1TAFn9A9Nkkr8YU8R0Hpfge4Q7MBOvBPT4F7XHiDG9UU`); its metadata
confirms the native Google Docs MIME type and project-root parent folder.

- **Batch 1 is active; its full native WIP is the live repair surface in Google Drive.** Keep the local PPTX and maps as the reproducible source. Make confirmed visual-only fixes in the same native WIP; rebuild and reconcile locally when content, build states, order, or structure changes, or when a local repair is needed to preserve the intended result through import. The paired page 2 and page 68 tests support local source repairs for those cases; Round 17 and Round 25 show targeted native Google edits for import-specific differences. See the [documented route decision](combined/SLIDE_CONVERSION.md#full-batch-working-deck-workflow). The current Fall Introduction
  and Fault/Error/Failure Keynote sources convert to 92 and 108 LibreOffice
  PPTX slides, while their reference PDFs contain 30 and 79 pages. A structural
  IWA decoder now confirms 62 Introduction nodes and 29 Fault/Error nodes are
  marked skipped; the remaining 30 and 79 active slides match every reference
  PDF page and candidate slide in order. This resolves the earlier count
  mismatch. Build stages on 17 Introduction slides and 35 Fault/Error slides
  are decoded (74/113 Introduction build archives/chunks and 92/185 for
  Fault/Error). Three paragraph-build families are confirmed on Introduction
  PDF pages 4, 6, and 15; Round 26 also mapped the two-object and three-object
  sequences on pages 2 and 3. The mixed banner/question build on page 17 is
  converted. Introduction PDF page 12's two-step AI-policy build is now
  classified: its subtitle appears first, then its editable policy list. The
  single-chunk All at Once builds on pages 14 and 16 need no extra slide. Eleven
  of 52 build-bearing slides are classified; 41 remain. Round 27 added the
  three paragraph states on Introduction page 27, mapped to local output pages
  62–64. The editable list's missing bullet, geometry, and line spacing were
  repaired from the Fall PDF. Round 28 imported an 8-slide native pilot for
  the page 2–3 and page 27 states. Native readback confirmed ordered editable
  slides; every Google PDF page was compared with exact Fall pages 2, 3, and
  27. See the [Round 28 runbook](combined/SLIDE_CONVERSION.md#round-28--batch-1-google-verification-pilot-for-build-states)
  and the tracked
  [pilot source/build map](combined/final-batches/batch-01-round28-google-pilot-map.csv).
  Linux LibreOffice substitutes Source Sans Pro with Liberation Sans, changing
  some local line wraps; native Google review resolved that preview issue for
  these states.
  The current local candidate is under
  `out/.build/batch-01/round29/rebuild-v2/`. Its map has 147 consecutive rows;
  PPTX order, relationships, slide parts, and ZIP integrity pass. Local
  divider rows are at pages 1 and 68. The PPTX is 39,494,683 bytes, SHA256
  `5e12bceca939cb6dbda4baf7a7ca616e0955786e7ba9afe2359fcc761ce4e9e0`; its
  147-page local diagnostic PDF is 28,501,659 bytes, SHA256
  `06748e758845faf5f28695da2c43d8059e8183dbded3ed2e5e13b3064a1927d4`. Linux
  font substitutions make it diagnostic only. This local candidate has not
  replaced or changed the existing Drive WIP.
  Confirmed repair areas include Introduction tables/text/diagram fit and
  Fault/Error diagrams, video composition, and colored outcome tables. A
  111-page local baseline includes editable source-deck dividers; the current
  expanded candidate has 147 pages after the earlier states and the five new
  object states on pages 2–3 plus page 27's three states. The original 37
  expanded states were inspected locally and in separate native Google pilots.
  The newer page 2–3 and page 27 states passed local review and the Round 28
  native Google pilot. Existing pilot PDFs confirmed ordered
  progression, bullet hierarchy, emphasis, and line fit for their reviewed
  builds. The final
  states closely match their Fall references; page 12's explicit Arial sizes
  and native bullets survived Google import without a Google-side patch, while
  page 18 retains a small Google
  font-substitution height difference. On page 17, the Google-only coarse border dash was repaired
  by a native `DOT` outline update across all six states. The page 6 `~24`
  line stays on one line after
  import. Introduction source pages 2 and 17 have local text/layout repairs
  and were checked in local renders. Page 17's title width, question wrapping,
  bullets, and rotated blue response banner now closely match the reference.
  Fault/Error pages 65, 68,
  73, 74, 76, and 77 also have local repairs; three diagram-only image crops
  are documented last resorts. The 36 pt page 68 label repair has passed a
  Google pilot, and the provisional candidate was rebuilt with that change;
  its output page 100 in the pre-Round27 candidate (now page 102) was reviewed.
  Meaningful builds, other repairs, the final
  remaining build classifications, the final map, and full-batch Google
  verification remain open. The 142-slide [working deck](https://docs.google.com/presentation/d/1EYXO-ZvBcLhUg9-JdA0t6C78sSx6Ki-4OGnIeYM9IME/edit)
  is uploaded at the shared Drive root as `WIP - needs fixes`; native readback
  confirms 142 ordered slides at revision `mEV_c_nCguc_IQ`. The latest Google
  PDF export has 142 pages, is 5,299,986 bytes, and has SHA256
  `fb172ef445e150960d683aa3b01cfcfeba5f627ceb2c0172eefde5168359e2c2`. Round
  29 repaired output pages 2 and 64 in that same deck and checked them against
  the exact Fall cover references. Six of 142 pages are confirmed repaired
  (about 4%); full-size review has not established a reliable count of all
  remaining defects. Contact sheets have been reviewed for all pages, but the
  batch is not accepted. The user set the Google Drive plugin to “Allow all
  tools”; no approval is pending, and project operations remain limited to the
  CS 408 folder. The two source-deck dividers were blank after import because the
  generated DrawingML text boxes lacked explicit preset geometry. A two-slide
  pilot confirmed that adding rectangle geometry preserves the editable text;
  the current WIP now has the source filename and topic labels on both
  dividers, with a solid `#FFF2CC` background, 24 pt bold filenames, and 28 pt
  topics. A one-slide page 17 Drive pilot confirmed the
  editable text and banner/list repairs after import. A native fallback
  corrected the substituted-font title size and the banner's dotted outline;
  its one-page Google PDF was visually checked. That pilot is in `Pilots`.
  Course Grading slides (output pages 24–25) now match their Fall PDF typography
  and centered cells. A two-slide PPTX-import pilot verified 66 pt Bebas Neue
  labels, middle-aligned cells, and row sizing; its title font maps to Arial on
  import, so the full WIP received a direct native Source Sans Pro repair. See
  the [Round 25 runbook](combined/SLIDE_CONVERSION.md#round-25--batch-1-course-grading-table-typography).
  The integrated local page 17 repair still needs final-batch Google verification.
  The separate 11-slide page 4, 7-slide page 6, 2-slide page 12, 9-slide page
  15, 6-slide page 17, and 2-slide page 18 build-state pilots are in
  Drive `Pilots`; their export and repair notes are in the [Round 18](combined/SLIDE_CONVERSION.md#round-18--batch-1-introduction-paragraph-build-pilot)
  [Round 19](combined/SLIDE_CONVERSION.md#round-19--batch-1-course-grading-paragraph-build-pilot),
  [Round 20](combined/SLIDE_CONVERSION.md#round-20--batch-1-course-objectives-paragraph-build-pilot),
  and [Round 21](combined/SLIDE_CONVERSION.md#round-21--batch-1-introduction-mixed-bannerquestion-build)
  logs. Round 23 verifies the AI-policy subtitle/list build and its locally
  repaired editable typography through Google import without a native fix; see
  the [Round 23 record](combined/SLIDE_CONVERSION.md#round-23--batch-1-introduction-page-12-ai-policy-build).
  Round 22 recovers the article scan from the Keynote package, reveals it
  before its editable headline, and records the Google-specific text sizing
  repair; see the [Round 22 record](combined/SLIDE_CONVERSION.md#round-22--batch-1-introduction-page-18-imageheadline-build).
  Before this upload, the November 27 Drive root listing showed only
  `Pilots`. The current WIP deck is now at the root, above `Pilots`, and is
  linked in the [Drive guide](combined/GOOGLE_DRIVE_ACCESS.md#pilot-and-final-batch-folder-organization).
  Earlier one-slide pilots show that both routes can repair
  Introduction page 2: the local-repair Google PDF retains the orange Fall
  2026 styling, while the final two-pass native repair is readable but makes
  that value black. On Fault/Error page 68, the 36 pt local repair
  survives import with the photo visible and both labels on one line; the
  Google-first export has a black field where the photo belongs. This supports
  local source repairs for those specific content/media defects. For the
  uploaded full-batch WIP, make confirmed visual-only fixes in the same native
  Google deck and rebuild locally when content or structure changes.
  See the [conversion route decision and Round 17 record](combined/SLIDE_CONVERSION.md#round-17--introduction-page-17-repair-pilot).
  See the
  [Batch 1 diagnostic](combined/final-batches/batch-01-diagnostic.md),
  [provisional maps](combined/final-batches/README.md), and the ordered
  [build-sequence audits](combined/final-batches/README.md#batch-1-current-state).
  The [static-state expander](combined/expand_batch_build_states.py),
  [pilot package pruner](combined/prune_pptx_slides.py), and
  [page 18 source-asset reconstruction](combined/prepare_intro_page18_build.py),
  [build-expansion decisions](combined/final-batches/batch-01-build-expansion.json)
  document how to reproduce and isolate these reveal conversions.
  The Introduction
  course schedule slide is user-owned: leave its schedule content alone while
  completing other Batch 1 work; the user will edit it.
- **Latest full baseline.** Round 4 Part 1 (recorded local artifact: `combined/google-slides-pilot/cs408-editable-part-01-round4.pptx`; may be absent from this checkout)
  contains combined slides 1–260. The Round 4 Google PDF (recorded local artifact: `combined/google-slides-pilot/cs408-editable-part-01-round4.pdf`; may be absent from this checkout)
  gives the full-batch comparison baseline.
- **Most recent `.key` build-conversion pilot.** [Round 23](combined/SLIDE_CONVERSION.md#round-23--batch-1-introduction-page-12-ai-policy-build)
  tests the AI-policy subtitle/list sequence; locally repaired fonts and
  bullets survived import and remained editable without a Google-side patch.
  [Round 22](combined/SLIDE_CONVERSION.md#round-22--batch-1-introduction-page-18-imageheadline-build)
  tests the scanned article image followed by its editable headline, with a
  targeted Google-native font/position correction after import. [Round 21](combined/SLIDE_CONVERSION.md#round-21--batch-1-introduction-mixed-bannerquestion-build)
  verified a six-state mixed banner/question reveal; its dotted outline needed
  a Google-native property correction. [Round 20](combined/SLIDE_CONVERSION.md#round-20--batch-1-course-objectives-paragraph-build-pilot),
  [Round 19](combined/SLIDE_CONVERSION.md#round-19--batch-1-course-grading-paragraph-build-pilot),
  and [Round 18](combined/SLIDE_CONVERSION.md#round-18--batch-1-introduction-paragraph-build-pilot)
  cover the nine-state Course Objectives, seven-state Course Grading, and
  11-state homework reveals. The most recent single-slide repair
  pilot remains [Round 17](combined/SLIDE_CONVERSION.md#round-17--introduction-page-17-repair-pilot),
  which tested a one-slide Introduction page 17 repair in native Google Slides.
  Its editable list/banner survived import; native title sizing and a `DOT`
  outline update repaired two Google-only differences. The one-page Google PDF
  was visually checked. The integrated local title-size repair still needs
  verification in the full Batch 1 import. [Round 16](combined/SLIDE_CONVERSION.md#round-16--test-anatomy-repairs-and-google-review)
  remains the completed 38-slide diagnostic immediately before it.
  Google native readback confirmed 38 ordered editable slides and notes on
  every page. All 38 pages now have close visual review in the [page map](combined/google-slides-pilot/cs408-fall-test-anatomy-round16-map.csv)
  and [review folder](combined/google-slides-pilot/cs408-fall-test-anatomy-round16-review/).
  The latest Google PDF is 5,101,352 bytes. Repairs preserved native text and
  shapes where possible: slide 1's unsupported gradient was removed and the
  brown banner restored; slide 2's verified empty bullets were removed and
  only the overflowing HW1 line was reduced to 33 pt; slides 4–5 use a
  source-PDF crop only for their distorted state diagrams; slides 7 and 38
  have verified empty agenda bullets removed; and slide 25's missing blank
  code row was restored so the separator no longer crosses `def`. Google
  displays `3.` on that blank row, while the September reference leaves it
  unnumbered. The local audit passes package, order, PDF-page, requested-text,
  and unchanged-control checks; slide 6 is byte-identical to the baseline
  PPTX and pixel-identical to the baseline Google PDF at 120 dpi. The
  September 1 PDF predates the October 6 Keynote revision: slide 6's
  quote/build and slide 21's system-test material are valid newer content.
- **Latest source-selection pilot before Round 15.** [Round 14](combined/SLIDE_CONVERSION.md#round-14--older-concurrency-testing-lab-introduction)
  imports the complete 28-slide archived concurrency-testing lab introduction
  as a native Google deck. Google readback found 28 slides in source order and
  preserved native text and slide objects; all 28 Google-rendered PDF pages
  were reviewed against a local diagnostic render of the original PPTX. The
  source has no speaker-note parts or timed animations. It is a complete older
  supplemental topic absent from the Fall fuzzing assignment, not a replacement
  for Fall Lab 1. Content review flagged stale `CS503 Spring 2021` screenshots
  on slides 4–6 for update or an archival label before final integration. See
  the [native deck](https://docs.google.com/presentation/d/1tAObwDTGc_EJ6aD4nXIceRTPjc3vF63hOPDdxFdZ0WE/edit),
  [Google PDF and contact sheets](combined/google-slides-pilot/cs408-concurrency-lab-intro-round14-review/),
  and [source map](combined/google-slides-pilot/cs408-concurrency-lab-intro-round14-map.csv).
- [Round 13](combined/SLIDE_CONVERSION.md#round-13--fall-lab-1-fuzzing-source-and-build-mapping)
  imports the complete Fall Lab 1 tutorial (40 source slides) as 62 editable
  Google Slides. Three paragraph-timed slides became 25 cumulative static
  states; a two-slide AFL screenshot zoom is also mapped. Native readback
  confirmed 62 ordered slides, editable text/shapes/images, and preserved
  speaker notes. The 62-page Google PDF was visually reviewed. The pilot
  updates stale Spring title/admin text from Fall sources and keeps the
  Spring tutorial out of the selected set as superseded. The explicit Fall
  handout deadline (Oct 30) conflicts with the syllabus table (Nov 3); this
  remains recorded for reconciliation. Its [native deck](https://docs.google.com/presentation/d/1wHRFaaLfwfrOnY_fKJbG69xQf9x0Yql47D6ZFCoZb7g/edit),
  PPTX (recorded local artifact: `combined/google-slides-pilot/cs408-fall-project-1-pilot-round13.pptx`; may be absent from this checkout),
  Google PDF (recorded local artifact: `combined/google-slides-pilot/cs408-fall-project-1-round13-review/presentation.pdf`; may be absent from this checkout),
  [slide/build map](combined/google-slides-pilot/cs408-fall-project-1-pilot-round13-map.csv),
  and [builder](combined/google-slides-pilot/build_fall_lab1_pilot_round13.py)
  are documented in the runbook.
- [Round 12 revision 2](combined/SLIDE_CONVERSION.md#round-12--editable-test-case-minimization-supplement)
  remains a technical conversion pilot for four older Test Case Minimization
  pages; Fall is the complete selected source for that topic, so those pages
  are not carried into final content.
- **Animation/build example verified.** Combined slides 205–206 preserve the
  concurrency comic reveal as two Google slides: first panel, then full comic.
  The latest Keynote export and Round 4 Google PDF (recorded local artifact: `combined/google-slides-pilot/cs408-editable-part-01-round4.pdf`; may be absent from this checkout)
  agree. The older static reference PDF repeats the final comic and is not the
  build-order authority for this case. See the [build audit](combined/SLIDE_CONVERSION.md#animationbuild-audit-combined-slides-205206).
- **Part 2 visual scale check complete.** [Rev3 native Google deck](https://docs.google.com/presentation/d/1OTrLWNKqwFOokESPsZuoBoqWI6Qjm-7IxiSmsa0f50I/edit)
  is in `Pilots`; its 232-page Google PDF (recorded local artifact: `combined/google-slides-pilot/cs408-editable-part-02-scale-rev3-google.pdf`; may be absent from this checkout)
  and [source map](combined/google-slides-pilot/cs408-editable-part-02-scale-rev3-map.csv)
  are saved locally. Native readback confirmed `p1`–`p232` in order. The
  [visual regression report](combined/google-slides-pilot/cs408-editable-part-02-scale-rev3-visual-diff.csv)
  shows only the two intended panel repairs (slides 214 and 216) differ from
  rev2; text remains editable. This pilot does not complete any of the final
  16-batch map, conversion, or review work. The successful no-curl transfer method
  and root cause are in the
  [Drive guide](combined/GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf).
- **Next.** Round 17 is complete as a one-slide repair pilot; its integration
  in Batch 1 remains open. The content-selection gate is closed for all
  57 candidate rows; do not repeat that analysis. Use Fall sources for
  covered topics and include the six complete older-only topics recorded in
  the audit. The ordered 16-batch boundary outline is in
  [BATCH_BOUNDARIES.md](combined/BATCH_BOUNDARIES.md). Put one full-slide,
  solid pale-yellow (`#FFF2CC`) divider before every original source deck in
  each final batch. Center the exact filename in 24 pt bold Arial and the
  following topic in 28 pt regular Arial; keep both editable and map the
  divider separately from source slides and build states. Then map,
  convert, repair, upload, and verify Batch 1 completely before
  starting Batch 2. Resolve source-reference gaps when they affect the batch
  in progress; use existing
  PDFs first and consult `MANUALLYCONVERT.md` only as a last resort. Aim for a
  Google PDF below 10 MB when conceptual boundaries naturally allow it; if a
  complete batch is larger, use the documented no-curl fallback rather than
  splitting a deck or topic. Put every full-batch WIP and accepted native
  deck in the shared Drive root above `Pilots`. Native text edits and a reversible
  native line-position edit/readback have passed; a line-style update was
  rejected for the imported arrow object. Other object types still need
  editability checks as they occur in each batch. See the
  [current Batch 1 open work](combined/final-batches/batch-01-diagnostic.md#next-actions-for-this-batch).

Keep rebuildable local PPTX candidates, PDFs, renders, and temporary files in
ignored `out/.build/`. Keep durable scripts, manifests, maps, repair rules, and
compact QA reports in `out/combined/`. See the [pilot folder guide](combined/google-slides-pilot/README.md)
for historical pilot evidence and current artifact placement. Store small
native test decks in Drive `Pilots`; put each full-batch WIP and accepted
native Slides deck directly in the shared Drive root. After each round, update
its runbook entry, source/build map, open-work list, and this status page.
Update the collection source maps only when source selection or provenance
changes.

## Fall 2026 study guide

The historical study guide has 1,838 pages. Its generated PDF is not in this
checkout and is separate from the active slide-conversion inputs. It opens with a
six-page quick review and linked contents. Nine course maps highlight the
current section and link to its lectures and exercises.

### Recommended four-part split

| Part | Pages in the full guide | Content |
| --- | ---: | --- |
| 1. Foundations and coverage (recorded local artifact: `cs408-study-guide-1.pdf`; may be absent from this checkout) | 1–485 (485 pages) | Quick review, contents, syllabus, test design, input space partitioning, control flow, data flow, and logic coverage. |
| 2. Mutation, oracles, fuzzing, and minimization (recorded local artifact: `cs408-study-guide-2.pdf`; may be absent from this checkout) | 486–974 (489 pages) | Mutation testing, test oracles, property-based testing, Midterm 1 practice, fuzzing, Project 1, and delta debugging. |
| 3. Symbolic execution, regression, and advanced topics (recorded local artifact: `cs408-study-guide-3.pdf`; may be absent from this checkout) | 975–1489 (515 pages) | Symbolic and concolic execution, regression and integration testing, Midterm 2 practice, concurrency, static analysis, verification, and Project 2. |
| 4. Final review and supplemental topics (recorded local artifact: `cs408-study-guide-4.pdf`; may be absent from this checkout) | 1490–1838 (349 pages) | Course review, a practice final with worked solutions, and earlier material on bug reporting, production coverage, concurrency testing, record and replay, deterministic execution, and static testing tools. |

Parts 2–4 begin on existing course maps at natural changes of topic. The first
part builds the vocabulary and coverage criteria. The second pairs automated
test generation with the fuzzing project. The third keeps the remainder of
the main course sequence together. The fourth starts with the final review
and groups the optional older material behind it.

The parts preserve the original page order, course maps, and bookmarks for
their sections. PDF page labels keep the full guide's numbering. Keep the four
files together for links between parts. Some browser PDF viewers block links
to sibling files. The full guide provides continuous navigation in those
viewers.

### Course sources

The branch check at build time found four GitHub branches. The guide uses
`fall+2026` as its primary source. Both development branches,
`new-lab2-dev` and `project1-ai-policy`, were already merged into Fall.
The older Spring-centered collection is a candidate inventory, not a final
selection. Check Fall's complete Keynote inventory before calling any older
topic absent: Fall has Keynotes for concurrency, Static Analysis, verification,
and final review even where a matching PDF export is missing.

The main sequence includes all 19 numbered Fall lecture PDF exports, the
syllabus, six numbered homework sets including the Homework 6 draft, 13
quizzes, two lab handouts, and both Fall midterms with their practice versions.
The Fall lecture PDFs were exported from August through November 2026, later
than the January–August 2026 Spring-centered Keynote candidates. Treat Fall
content as authoritative for every topic it covers; include older material
only as a complete topic Fall does not cover, with its source and rationale
recorded in the [crosswalk](combined/source-version-crosswalk.csv). The
active branch already contains the Fall PDFs and 57 Keynote decks in
`slides/`; see the [PDF audit](combined/fall-source-metadata.csv) and
[Keynote inventory](combined/fall-keynote-inventory.csv).
Exercises and readings appear near the corresponding topics.

The selection rule is topic-level: use the complete Fall source for every
topic Fall covers; add Spring material only for a complete topic absent from
Fall. Do not cherry-pick older slides, examples, or subtopic supplements from
within a Fall-covered topic. Keep older sources in the crosswalk as comparison
and provenance evidence. Fall updates Introduction administration and uses
rocket, power-grid, and cloud-outage examples. The Spring Keynote has the
incorrect label “Therac-35,” while its paired PDF page 27 scans Nancy
Leveson's Therac-25 article; the isolated older page and generic casualty
transition are excluded because Fall supplies the complete Introduction
topic. Older failure examples are not added to Fall Fault/Error/Failure or
Regression Testing. The older integration-testing overview is not appended to
Fall Test Anatomy. The syllabus has no dedicated bug-reporting lecture, but
the Fall branch retains a complete newer Bug Reports and Triage deck updated
October 25, 2026; the two older Spring decks are comparison-only against it.
The newer deck retains February Project 1 and March midterm announcements that
must be corrected before conversion. Older slides 1831–1840 contain JPL coding standards and
Clang/cppcheck examples, while Fall has a current Static Analysis Keynote but
no PDF export in the 20-PDF set. Export and inspect that complete Fall source;
do not append selected older examples to it. See the
[crosswalk](combined/source-version-crosswalk.csv) and [current plan](PLAN.md)
for evidence and remaining checks. The Fall Static Analysis Keynote itself
still contains April 24 Project 2/HW5 announcements in three agenda-slide
variants; replace them with the current syllabus dates (HW6: Dec 4 at 6 PM;
Project 2: Dec 6). See the
[conversion runbook](combined/SLIDE_CONVERSION.md#static-analysis-and-coding-standards-source-review).
The older three-deck syntax-based-testing unit (combined slides 1222–1318) is
excluded: Fall Fuzzing and Mutation Testing cover its main grammar-based
input-generation, invalid-input mutation, and program-mutant lessons. Its
TSC/PDC/DC grammar-coverage criteria are isolated additions within those
Fall-covered topics, so they do not justify bringing the older 97 slides
forward. This content comparison is recorded in the
[older-topic audit](combined/older-topic-selection-audit.csv) and
[source-deck audit](combined/source-deck-topic-audit.csv).
The Fall Fault/Error/Failure deck's pages 31–62 include ordered execution-state
builds, followed by updated RIPR/revealability, a possibility table, and a
second exercise. Its older 2025 candidate section is mostly superseded.
Fall is the complete selected source for Test Case Minimization. Round 12
revision 2 reconstructed four older pages as a technical conversion pilot;
those pages are not selected for final content because they are an isolated
supplement inside a Fall-covered topic. The 49-page Fall lecture still needs
its own editable conversion. See the
[crosswalk](combined/source-version-crosswalk.csv) and
[detailed review](combined/SLIDE_CONVERSION.md#test-case-minimization-source-review).
The first symbolic-execution visual audit also corrected a misleading old
candidate range that mixed logic/CACC, symbolic execution, concolic execution,
and a MultiNyx hypervisor case study; those parts are now mapped to their
respective Fall topics while older-content decisions remain open. See the
[revised crosswalk](combined/source-version-crosswalk.csv) and
[review notes](combined/SLIDE_CONVERSION.md#symbolic-execution-and-concolic-source-review).
The older ISP map was also corrected: source slides 1831–1840 are Mars code
and static-analysis material, not ISP; the topic starts at 1841. Fall is the
selected complete ISP topic; older Multiple Base Choice and Iterator exercise
slides are not added as isolated supplements. See the
[ISP review](combined/SLIDE_CONVERSION.md#input-space-partitioning-source-review).

