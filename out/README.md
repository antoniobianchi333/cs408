THE MOST IMPORTANT THING IS THAT I NEVER STOP UNTIL ALL THE SLIDES ARE CONVERTED AND TESTED!!!!!!!!!!!!!

# COMPLETION REQUIREMENT — DO NOT STOP EARLY

**Keep working until all slides in the final reconciled course set—including
every complete older topic absent from Fall and every meaningful animation
state—have been converted to Google Slides and verified against their
sources and Google exports. Do not stop after documentation, planning,
pilots, or partial batches.**

**Google file-transfer rule:** Never use `curl` or another shell/network
downloader for Drive files or signed references. Use the connected Drive
stream, authenticated browser download, or paced native thumbnails. If size
requires smaller work units, use up to 16 ordered blocks, cutting only
between complete source decks and topics. The exact cause and recovery steps
are in [the Drive access guide](combined/GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf).

# CS 408 Software Testing materials

This directory holds two CS 408 resources:

- The Fall 2026 study guide is a reading PDF with lectures, exercises, and
  course maps.
- The editable Slides project starts from a 2,235-slide candidate collection
  built around the Spring 2026 sequence and earlier material. That inventory
  is being reconciled topic by topic against Fall 2026: use Fall's complete
  source wherever it covers a topic, and retain Spring material only for a
  complete topic Fall does not cover. The candidate collection is not the
  final selected slide set.

The conversion goal is to preserve lesson content, slide order, and notes
while keeping text, code, diagrams, and pictures usable as separate objects
in Google Slides. Meaningful instructional animation builds should become
sequential static slides in build order, with each generated slide mapped to
its source slide and build state. The delivered slide count may therefore
exceed the 2,235-slide source count.

For `.key` source files on Linux, avoid installing a converter while a
browser-based option is available: Apple Keynote for iCloud can export a PPTX
copy, which can then be imported into Google Slides. Google Drive can store a
`.key` file but does not list it among the formats it converts to Slides. This
route still needs a representative pilot; see the
[runbook](combined/SLIDE_CONVERSION.md#produce-an-editable-powerpoint-on-linux).

## Documentation and workflow

| Step | Instructions | What to keep |
| --- | --- | --- |
| 1. Locate the source | Use the [combined collection guide](combined/README.md) to map a combined slide number to its source deck, saved build, and editable batch. | The matching Keynote or PowerPoint, source PDF, and combined slide numbers. |
| 2. Build a small editable test | Follow the [conversion runbook](combined/SLIDE_CONVERSION.md). Start from the latest full batch, add a representative slide from another layout, and include an unaffected control. A local LibreOffice render is optional diagnostic evidence; Google’s PDF is the acceptance render. | A new PPTX, the ordered pilot-to-source page map, and available local and Google PDFs. |
| 3. Upload and export in Google | Use the [Google Drive guide](combined/GOOGLE_DRIVE_ACCESS.md) for connector setup, a paced native import and PDF export, and the browser fallback. Use a separate deck in the shared test folder for each revision. | The verified native deck URL and a Google-generated PDF in the pilot directory. |
| 4. Compare and improve | Follow the [roundtrip checks](combined/SLIDE_CONVERSION.md#run-and-evaluate-a-google-roundtrip) and run the [local audit script](combined/google-slides-pilot/audit_conversion_pilot.py). Check page order, content and code, image crops, graph endpoints, and actual editability. Record where each defect first appeared and retest the smallest repair. | The comparison result, a reusable repair rule, any exceptions, and what remains open. |
| 5. Apply verified repairs to the batch | Use the [integration instructions](combined/SLIDE_CONVERSION.md#integrate-verified-repairs-into-a-full-batch) to assemble a new full-size candidate and verify its Google export. | A versioned full-batch candidate, its PDF comparison, and an updated runbook. |

## Project documents

- [Live plan and time estimates](PLAN.md)
- [Branch, restart-kit, and artifact-tracking policy](BRANCH_AND_HANDOFF.md)
- [Combined slide collection and source map](combined/README.md)
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
- [Final editable batches](combined/) and their
  [batch manifest](combined/editable-parts-manifest.json). Each of the nine
  `cs408-editable-part-*.pptx` files stays directly in `combined/`.
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
  [Fall text-overlap audit script](combined/audit_fall_text_overlap.py),
  [source-deck topic audit script](combined/audit_source_deck_topics.py), and
  [older-topic selection audit](combined/older-topic-selection-audit.csv), plus
  [local conversion audit script](combined/google-slides-pilot/audit_conversion_pilot.py)
- [Full combined slide PDF](combined/cs408-all-slides.pdf),
  [full editable PowerPoint](combined/cs408-all-slides-editable.pptx), and
  [image-based PowerPoint parts](combined/import-parts.json)
- [Google Drive Pilots folder](https://drive.google.com/drive/folders/1PHuKHahwY2PxviNWTM2f8kYmb7K-37Dj)
  contains the historical pilot and disposable decks. The shared Drive
  folder root is reserved for final batch decks.
- [Temporary local render and audit work](.build/). These are diagnostic
  outputs; the versioned pilot artifacts and PDFs are kept in
  `combined/google-slides-pilot/`.

## Current conversion status

- **Latest full baseline.** [Round 4 Part 1](combined/google-slides-pilot/cs408-editable-part-01-round4.pptx)
  contains combined slides 1–260. The [Round 4 Google PDF](combined/google-slides-pilot/cs408-editable-part-01-round4.pdf)
  gives the full-batch comparison baseline.
- **Latest source-selection/Google import pilot.** [Round 14](combined/SLIDE_CONVERSION.md#round-14--older-concurrency-testing-lab-introduction)
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
  [PPTX](combined/google-slides-pilot/cs408-fall-project-1-pilot-round13.pptx),
  [Google PDF](combined/google-slides-pilot/cs408-fall-project-1-round13-review/presentation.pdf),
  [slide/build map](combined/google-slides-pilot/cs408-fall-project-1-pilot-round13-map.csv),
  and [builder](combined/google-slides-pilot/build_fall_lab1_pilot_round13.py)
  are documented in the runbook.
- [Round 12 revision 2](combined/SLIDE_CONVERSION.md#round-12--editable-test-case-minimization-supplement)
  remains a technical conversion pilot for four older Test Case Minimization
  pages; Fall is the complete selected source for that topic, so those pages
  are not carried into final content.
- **Animation/build example verified.** Combined slides 205–206 preserve the
  concurrency comic reveal as two Google slides: first panel, then full comic.
  The latest Keynote export and [Round 4 Google PDF](combined/google-slides-pilot/cs408-editable-part-01-round4.pdf)
  agree. The older static reference PDF repeats the final comic and is not the
  build-order authority for this case. See the [build audit](combined/SLIDE_CONVERSION.md#animationbuild-audit-combined-slides-205206).
- **Part 2 visual scale check complete.** [Rev3 native Google deck](https://docs.google.com/presentation/d/1OTrLWNKqwFOokESPsZuoBoqWI6Qjm-7IxiSmsa0f50I/edit)
  is in `Pilots`; its [232-page Google PDF](combined/google-slides-pilot/cs408-editable-part-02-scale-rev3-google.pdf)
  and [source map](combined/google-slides-pilot/cs408-editable-part-02-scale-rev3-map.csv)
  are saved locally. Native readback confirmed `p1`–`p232` in order. The
  [visual regression report](combined/google-slides-pilot/cs408-editable-part-02-scale-rev3-visual-diff.csv)
  shows only the two intended panel repairs (slides 214 and 216) differ from
  rev2; text remains editable. This pilot does not complete the final source
  reconciliation or full collection. The successful no-curl transfer method
  and root cause are in the
  [Drive guide](combined/GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf).
- **Pending.** Reconcile the Spring-centered slide set topic by topic against
  the newer Fall 2026 material. Use Fall's complete source for topics it
  covers; include complete Spring topics only where Fall has no corresponding
  topic. Do not append older individual slides or examples to covered topics.
  Apply the verified 205–206 build-state rule and test other animation/build
  families when found. Carry forward only applicable repairs from Rounds 5–11;
  Round 12 is a technical pilot, not selected content. Continue validating
  no-curl PDF transfer through Drive's documented `files.download` LRO for
  files over 10 MB; the connector's local materialization remains untested at
  that size. Do not split topics or decks solely to meet the separate 10 MB
  `files.export` response cap. If the overall
  collection needs smaller blocks, use up to 16
  while preserving whole source-deck and topic boundaries. The
  plan starts by assessing four contiguous blocks, then can expand to eight
  or sixteen if measured constraints require it. Block sizes may vary: every
  original source deck and topic must remain whole, and each cut must satisfy
  both boundaries. Use the prior course syllabus and schedule to estimate weeks,
  never to override those boundaries. Native text edits and a reversible
  native line-position edit/readback have passed; a line-style update was
  rejected for the imported arrow object. Other object types still need
  editability tests. See the
  [current open-work list](combined/SLIDE_CONVERSION.md#open-work-after-round-14).

Keep final editable batch PowerPoints directly in `out/combined/`. Keep every
local pilot input, revision, page map, reference render, and Google PDF in
`out/combined/google-slides-pilot/`, following its [folder guide](combined/google-slides-pilot/README.md).
In Drive, put pilots under the shared folder's `Pilots` subfolder; put final
batch decks directly in the shared folder root. After each round, update its
runbook entry, pilot page map, current open-work list, and status on this
page. Update the collection source maps when source selection or provenance
changes.

## Fall 2026 study guide

The [full study guide](cs408-study-guide.pdf) has 1,838 pages. It opens with a
six-page quick review and linked contents. Nine course maps highlight the
current section and link to its lectures and exercises.

### Recommended four-part split

| Part | Pages in the full guide | Content |
| --- | ---: | --- |
| [1. Foundations and coverage](cs408-study-guide-1.pdf) | 1–485 (485 pages) | Quick review, contents, syllabus, test design, input space partitioning, control flow, data flow, and logic coverage. |
| [2. Mutation, oracles, fuzzing, and minimization](cs408-study-guide-2.pdf) | 486–974 (489 pages) | Mutation testing, test oracles, property-based testing, Midterm 1 practice, fuzzing, Project 1, and delta debugging. |
| [3. Symbolic execution, regression, and advanced topics](cs408-study-guide-3.pdf) | 975–1489 (515 pages) | Symbolic and concolic execution, regression and integration testing, Midterm 2 practice, concurrency, static analysis, verification, and Project 2. |
| [4. Final review and supplemental topics](cs408-study-guide-4.pdf) | 1490–1838 (349 pages) | Course review, a practice final with worked solutions, and earlier material on bug reporting, production coverage, concurrency testing, record and replay, deterministic execution, and static testing tools. |

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

