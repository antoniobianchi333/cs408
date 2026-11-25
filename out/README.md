THE MOST IMPORTANT THING IS THAT I NEVER STOP UNTIL ALL THE SLIDES ARE CONVERTED AND TESTED!!!!!!!!!!!!!

# COMPLETION REQUIREMENT — DO NOT STOP EARLY

**Keep working until all 2,000+ slides in the final reconciled course set—
including useful older-only material and every meaningful animation
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
- The editable Slides project targets a separate 2,235-slide collection
  built around the Spring 2026 course sequence and selected earlier material.

The conversion goal is to preserve lesson content, slide order, and notes
while keeping text, code, diagrams, and pictures usable as separate objects
in Google Slides. Meaningful instructional animation builds should become
sequential static slides in build order, with each generated slide mapped to
its source slide and build state. The delivered slide count may therefore
exceed the 2,235-slide source count.

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
`origin/fall+2026` commit `900304aa` (November 15, 2026), the newest of the
four pre-existing course branches. `spring+2026`, `new-lab2-dev`, and
`project1-ai-policy` are ancestors of Fall 2026; the latter two changes are
already merged into Fall. Local tracking branches now exist for all four
source branches, so plain `git branch` lists them together with the new
working branch.

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
  and [Fall PDF metadata/page-count audit](combined/fall-source-metadata.csv)
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
  and [local audit script](combined/google-slides-pilot/audit_conversion_pilot.py)
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
- **Latest pilot.** [Round 11 revision 4](combined/SLIDE_CONVERSION.md#round-11--cfg-label-fit-with-original-fonts)
  repairs split labels on combined slides 115–116. Its three-page
  [Google PDF](combined/google-slides-pilot/cs408-conversion-pilot-round11-rev4-google.pdf)
  preserves slide 114 as a pixel-identical control against the Round 4 Google
  PDF. The [native deck](https://docs.google.com/presentation/d/1iov7hGZMI1BnyVNWcwwvG-XxcslA4qJCMzatqMORMSA/edit)
  and exact source map are recorded in the runbook.
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
  the newer Fall 2026 material before fixing the final source selection.
  Keep the newest version when available and retain older material only for
  useful content absent from it. Apply the verified 205–206 build-state rule
  and test other animation/build families when found. Carry forward only
  applicable repairs from Rounds 5–11 and continue validating the no-curl
  PDF transfer workflow, especially for files over 10 MB. If the overall
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
  [current open-work list](combined/SLIDE_CONVERSION.md#open-work-after-round-11).

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
Selected earlier material fills gaps in the Fall exports, including
concurrency, static analysis, verification, and final exam practice.

The main sequence includes all 19 numbered Fall lecture PDF exports, the
syllabus, six numbered homework sets including the Homework 6 draft, 13
quizzes, two lab handouts, and both Fall midterms with their practice versions.
Exercises and readings appear near the corresponding topics.

