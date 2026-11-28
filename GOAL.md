# Project goal — complete all selected CS 408 slides

**THE MOST IMPORTANT THING IS TO KEEP WORKING UNTIL ALL 2,000+ SELECTED SLIDES
ARE CONVERTED, UPLOADED, AND TESTED. DO NOT STOP AT PLANNING, DOCUMENTATION,
PILOTS, A PARTIAL BATCH, OR A SUCCESSFUL IMPORT.**

Convert every slide in the final reconciled course set to editable native Google
Slides wherever practical, then verify the uploaded result. The project is
complete only when all 16 conceptual batches are accepted under the checks
below.

## Final content and batch rules

- Use the completed content decisions in
  [`out/combined/source-deck-topic-audit.csv`](out/combined/source-deck-topic-audit.csv)
  and [`out/combined/older-topic-selection-audit.csv`](out/combined/older-topic-selection-audit.csv).
  Use Fall 2026 material wherever Fall covers a topic. Add only the six
  selected complete older-only topics; do not redo the source-selection audit.
- Follow [`out/combined/BATCH_BOUNDARIES.md`](out/combined/BATCH_BOUNDARIES.md).
  Keep every original slide deck, topic, and meaningful animation sequence
  whole and in order. The 16 batches are conceptual lecture-week groups, not
  equal slide counts. Never split a deck or topic to meet a page or file-size
  target.
- Convert meaningful builds into ordered, animation-free static slides and
  map every output slide to its source deck, source slide, and build state.
- Add one editable divider before every original source deck. Use a full-slide
  solid pale-yellow `#FFF2CC` background, the exact source filename centered
  in 24 pt bold Arial, and the following topic centered in 28 pt regular Arial.
  Use explicit DrawingML rectangle geometry for both text boxes and include a
  separate generated row in the map.
- Prefer editable text, shapes, diagrams, and pictures. Fix font size, text-box
  geometry, alignment, and ordering before considering an image fallback.
  Flatten only an individual object or region when no reliable editable repair
  works; image-only repair is the last resort.

## Batch completion gate

Complete Batch 1 before starting Batch 2, then proceed in order through Batch
16. For each batch:

1. Map every source page, generated state, and divider.
2. Convert and repair the full conceptual group; retain editability wherever
   practical and remove animations by expanding meaningful states.
3. Validate local package order and content using the project scripts.
4. Upload the full working deck to the shared Google Drive project root,
   directly above `Pilots`, and name it `WIP - needs fixes` until accepted.
   Keep one working native Google Slides deck per active batch and repair it
   in place. Use Drive `Pilots` only for small isolated test decks.
5. Read back native slide order and relevant objects, export the Google PDF,
   and inspect every page against the best available exact-revision source.
6. Record repairs, remaining exceptions, source/build maps, native deck link,
   PDF evidence, and acceptance date in the batch record and runbook.
7. Rename the WIP as accepted only after every check passes. Then begin the
   next batch.

## Operating rules

- Pace Google Drive calls serially, leaving at least 5.5 seconds between calls.
  Use the connected Drive and Slides tools. **Never use `curl` or another shell
  or network downloader for Drive files or signed references.** Follow the
  no-curl export recipe in
  [`out/combined/GOOGLE_DRIVE_ACCESS.md`](out/combined/GOOGLE_DRIVE_ACCESS.md).
- Use exact source PDFs when available. Missing reference PDFs are a documented
  limitation; [`out/MANUALLYCONVERT.md`](out/MANUALLYCONVERT.md) is a
  last-resort list and is currently empty.
- Keep scripts, maps, manifests, and project documentation in Git. Keep
  rebuildable PPTX, PDFs, render PNGs, and temporary files under ignored
  `out/.build/`. Store large processed Google Slides decks in the shared Drive
  root; store small tests in `Pilots`.
- Keep [`out/PLAN.md`](out/PLAN.md) current with ordered next steps and time estimates;
  refresh it about hourly during sustained work and after major changes. Update
  the main [`out/README.md`](out/README.md) whenever project status or navigation
  changes. The main README must link all relevant project Markdown, scripts,
  maps, and artifact folders.
- At the beginning of every new session, ask the user once for any permissions
  that may not carry over: Google Drive connector access needed to read and edit
  only the project folder, and a session-wide authorization for project
  `libreoffice --headless` conversions (including conversions beyond PDF
  export). A previous LibreOffice authorization may be session-specific. Use
  the platform's permission flow when it is available; do not ask repeatedly
  after the user grants it. Do not ask permission to commit or push; the user
  handles those actions.
- Work on the `spring+2027+bianchi` branch after verifying the actual checkout.
  The user handles staging, commits, and pushes. **Never commit or push unless
  the user explicitly tells you to.** Do not change Git remotes or config.
- Avoid adding dependencies when existing system tools and connected Drive
  tools suffice. A LibreOffice headless grant in an earlier session may not
  carry to another machine or session; follow the active session's permissions.

## Current starting point

The 57-deck content selection and the 16 batch boundaries are complete. Batch
1 is active and **not accepted**. Its 142-slide native Google WIP is at the
shared Drive root:

- [Batch 1 WIP deck](https://docs.google.com/presentation/d/1EYXO-ZvBcLhUg9-JdA0t6C78sSx6Ki-4OGnIeYM9IME/edit)
- [Batch 1 diagnostic](out/combined/final-batches/batch-01-diagnostic.md)
- [Current plan and estimates](out/PLAN.md)
- [Runbook and Round 24–25 evidence](out/combined/SLIDE_CONVERSION.md)
- [Current Drive state and access rules](out/combined/GOOGLE_DRIVE_ACCESS.md)

As of 2026-11-27, the WIP contains 142 ordered slides; its latest Google PDF
has 142 pages and is 5,233,045 bytes. Round 24 fixed the two source-deck
dividers. Round 25 fixed the Course Grading tables on output pages 24–25 and
verified their PPTX import in a two-slide pilot. Full-page follow-up and repair
remain open, and 45 of 52 build-bearing slides still need classification.
Continue with the open work listed in the diagnostic and PLAN; do not start
Batch 2 until Batch 1 passes its completion gate.
