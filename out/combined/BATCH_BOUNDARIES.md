# Final 16-batch boundaries

**Updated:** 2026-11-28
**Status:** The 16 conceptual boundaries are fixed. Batch 1 is in progress and
not accepted. Its 142-slide native WIP remains in the shared Drive root at
revision `81I4pqOtZCYd2A`. The fresh Round 34 Google PDF is 5,278,199 bytes,
has 142 pages, and has SHA256
`f209ce582c79ec0934992b157639c6ead8b53ff237867988ba5e2641cc5f72aa`.
Rounds 30–34 repaired selected pages in place; page 42 was compared with exact
Fall Introduction PDF page 16 after the final heading adjustment. The Round
39 local 272-slide candidate passes ZIP/order checks but remains unintegrated;
all 52 build-bearing slides are classified. Thirty-seven source slides expand
into 198 cumulative states and 15 no-expansion decisions retain one static
slide. The candidate includes the Introduction PDF page 26 reveal sequence
(outputs 64–72), local layout repairs on Introduction page 26 and Fault/Error
pages 12 and 69, plus the new Fault/Error page 24 and 61 repairs at outputs
130 and 202. Native readback now confirms 339 note runs at 9 pt across the
142-slide WIP, including whitespace anchors on all 66 formerly empty note
pages. A package check confirmed notes pages and 9 pt runs on all 272 local
candidate slides, including 117 blank-note anchors. The current work log and open pages are in the
[Batch 1 diagnostic](final-batches/batch-01-diagnostic.md); see the
[Round 39 record](SLIDE_CONVERSION.md#round-39--source-page-24-and-page-61-repairs).
The notes-free text reconciler maps all 142 WIP slides to 142 candidate rows
and places the remaining 130 rows at 32 insertion anchors. It corrected 14
provisional build-state matches; the correspondence and gap maps are in
[final-batches/](final-batches/), with the reusable
[reconciler](reconcile_batch01_wip_candidate.py). The WIP still has not been
structurally expanded. Do not start Batch 2 until Batch 1 passes its
acceptance checks. The 14 corrected source/build-state matches are map
alignment fixes, not visual repairs; no defensible repair count is available
until full Google-page review is complete. The notes-only revision left slide
order and the Round 34 visual PDF unchanged.

## Fixed rules

- Follow the completed source-selection decisions in the
  [57-deck audit](source-deck-topic-audit.csv) and
  [older-topic audit](older-topic-selection-audit.csv). Do not repeat the
  full selection analysis.
- Use complete Fall sources wherever Fall covers a topic. Include the six
  selected older-only units as complete units: Concurrency Testing Lab
  Introduction, Verified Distributed Systems, Semantic/Latent
  Concurrency-Bug Detection, Record and Replay, Deterministic Execution, and
  Static Testing Tools.
- Preserve original order inside every source deck and topic. A batch
  boundary may fall only between complete source decks and topics. Counts
  may vary to preserve those boundaries.
- The user requires one divider slide before each original source deck in
  every final batch, including the first deck in that batch. Use a full-slide,
  solid pale-yellow background (`#FFF2CC`), with centered editable Arial text:
  exact source filename at 24 pt bold, then the following topic at 28 pt
  regular. Record it as a generated row in the batch map; do not count it as a
  source slide or animation state. The builder must give generated text boxes
  explicit DrawingML rectangle geometry so Google Slides preserves them on
  import.
- Expand meaningful builds into ordered static slides after their source
  deck divider. Map every output slide to its source file, source slide, and
  build state. Do not combine or split a source deck to meet an equal-size or
  file-size target.
- Set speaker-note text to 9 pt on every slide, including slides without
  authored notes. Preserve existing note wording. The builder adds an
  editable notes page with an ordinary-space run to each empty note body and
  applies 9 pt styling. Confirm by native text readback; do not inspect notes
  visually.
- Week labels follow the actual Fall 2026 syllabus in syllabus/syllabus.tex.
  Week 12 includes a Midterm 2 review, but no selected current Fall slide deck
  for that review was found; the older March review remains comparison-only
  under the existing audit. Week 15 schedules Floyd/Dafny, but the selected
  deck inventory has no verified current slide master for that lecture. Do
  not substitute the distinct older Verified Distributed Systems deck for
  Floyd/Dafny. Record and reconcile any newly verified exact source before
  its sequence is finalized.
- These are 16 contiguous conceptual upload groups, not equal slide-count
  partitions. Batches 13 and 14 keep the Fall concurrency lectures and
  complete older supplemental topics adjacent without splitting a topic.

## Ordered outline

| Batch | Syllabus placement | Complete topics |
| ---: | --- | --- |
| 01 | Week 1 | Introduction and administrivia; Faults, Errors, and Failures. |
| 02 | Week 2 | Unit/Integration Testing and RIPR; Black-box Test Design and Input Space Partitioning. |
| 03 | Week 3 | Control-Flow Graphs and Program Paths; Graph-Based Coverage. |
| 04 | Week 4 | Data-Flow Coverage. |
| 05 | Week 4 | Logic Coverage; Active Clause Coverage. Keep the full topic sequence intact. |
| 06 | Week 5 | Mutation Testing; Randomized/Property-Based Testing. |
| 07 | Week 6 | Test-Case Minimization and Delta Debugging; Introduction to Fuzzing; Greybox Fuzzing. Keep each complete topic and deck in the syllabus sequence. |
| 08 | Week 7 | Greybox Fuzzing II and Fall Midterm 1 Review. Use the complete Fall review source; the older March review is comparison material under the existing audit. |
| 09 | Week 8 | Regression Testing and Test Selection/Prioritization. Use the complete Fall source. |
| 10 | Week 9 | Symbolic Execution; Concolic and Dynamic Symbolic Execution. Keep both complete topics in syllabus order. |
| 11 | Week 10 | Test Oracles. |
| 12 | Week 11 | Current Fall Bug Reports and Triage; Testing AI Systems / Machine Learning. Keep the topics separate with source-deck dividers. Repair stale dated announcements in the complete Bug Reports source using current course materials. |
| 13 | Week 12 | Fall Concurrency I and the adjacent complete older-only units Concurrency Testing Lab Introduction, Semantic/Latent Concurrency-Bug Detection, and Verified Distributed Systems. Keep every topic and deck distinct and complete. |
| 14 | Week 12 | Fall Concurrency II; complete older-only Record and Replay and Deterministic Execution units. Keep each topic and deck whole. |
| 15 | Weeks 13–15 | Fall Static Analysis I/II; the complete older-only Static Testing Tools survey as its own topic. Repair obsolete admin text in the older deck. The syllabus-only Floyd/Dafny lecture has no verified current slide master in the selected inventory. |
| 16 | Week 16 | Latest selected Fall Final Review source. Repair stale Spring exam and homework announcements before final integration. |

This outline follows the existing selection audit; it is not a new content
selection decision. The syllabus-only Week 12 exam and any topic without a
selected slide master do not create empty or invented slide decks. Where a
topic has no matching full-deck PDF, record the actual source and best
available reference in that batch's detailed map before conversion.
MANUALLYCONVERT.md remains the last-resort list for user-created reference
PDFs.

## Batch acceptance record

For each numbered group, record or link its source/build map, final native
Google Slides URL, native readback, Google-rendered PDF, full-page review,
repair record, and acceptance date. A group is not complete until the map
includes every original source deck, every generated divider, every
meaningful build state, and every final output slide, and the Google PDF has
been reviewed page by page against the best available exact-revision source.
