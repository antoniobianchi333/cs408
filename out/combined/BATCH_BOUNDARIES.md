# Final 16-batch boundaries

**Updated:** 2026-11-26  
**Status:** High-level boundaries are set. Batch 1 is next; its detailed
source/build map will record exact source revisions, output pages, build
states, and divider slides before conversion.

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
- The user requires one plain divider slide before each original source deck
  in every final batch, including the first deck in that batch. The slide
  names the exact source filename and the topic of the slides that follow.
  Keep it minimal: plain background and editable text, with no decorative
  image. Record it as a generated row in the batch map; do not count it as a
  source slide or animation state.
- Expand meaningful builds into ordered static slides after their source
  deck divider. Map every output slide to its source file, source slide, and
  build state. Do not combine or split a source deck to meet an equal-size or
  file-size target.
- Week labels follow the Fall 2026 syllabus. Week 12 is an exam week without
  a selected current Fall slide deck. The selected deck inventory has no
  verified current slide master for the scheduled Floyd/Dafny lecture; do
  not substitute the distinct older Verified Distributed Systems deck for
  it. Record and reconcile any newly verified exact source evidence before
  that batch is finalized.
- These are 16 contiguous conceptual upload groups, not equal slide-count
  partitions. Batches 12 and 13 keep the Fall concurrency lectures and the
  complete older supplemental topics adjacent without splitting a topic.

## Ordered outline

| Batch | Syllabus placement | Complete topics |
| ---: | --- | --- |
| 01 | Week 1 | Introduction and administrivia; Faults, Errors, and Failures. |
| 02 | Week 2 | Unit/Integration Testing and RIPR; Black-box Test Design and Input Space Partitioning. |
| 03 | Week 3 | Control-Flow Graphs and Program Paths; Graph-Based Coverage. |
| 04 | Week 4 | Data-Flow Coverage; Logic Coverage. |
| 05 | Week 5 | Active Clause Coverage; Mutation Testing. |
| 06 | Week 6 | Test Oracles; Randomized/Property-Based Testing; current Fall Bug Reports and Triage. Repair stale dated announcements in the complete Bug Reports source using current course materials. |
| 07 | Week 7 | Fall Midterm 1 Review. Use the complete Fall review source; the older review remains comparison material under the existing audit. |
| 08 | Week 8 | Introduction to Fuzzing. Use the complete Fall source and preserve meaningful builds. |
| 09 | Week 9 | Greybox Fuzzing; Test-Case Minimization and Delta Debugging. Keep each complete source deck intact. |
| 10 | Week 10 | Symbolic Execution; Concolic and Dynamic Symbolic Execution. Keep both complete topics in syllabus order. |
| 11 | Week 11 | Regression Testing and Test Selection/Prioritization. Use the complete Fall source. |
| 12 | Week 13 | Fall Concurrency: complete Fall source decks on race concepts, happens-before/race detection, and concurrency bugs, in source order. |
| 13 | Week 13 supplemental sequence | Complete older-only units adjacent to the Fall concurrency lectures: Concurrency Testing Lab Introduction; Semantic/Latent Concurrency-Bug Detection; Record and Replay; Deterministic Execution; Verified Distributed Systems. Keep each source deck and topic distinct, complete, and in selected source order. |
| 14 | Week 14 | Fall Static Analysis I/II material, followed by the complete older-only Static Testing Tools survey as its own topic. Repair obsolete admin text in the older deck. |
| 15 | Week 15 | Current Fall Testing AI Systems / Machine Learning sequence. Keep the complete selected Fall deck sequence. |
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
