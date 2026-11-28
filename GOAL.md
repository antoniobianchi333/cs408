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
- Keep the live `STATUS` Google Doc in the project Drive root current about
  hourly and after major milestones. Its ordered fields are: approvals needed,
  code-usage percentages, current work and near-term plan, the complete
  `out/MANUALLYCONVERT.md`, and the complete `out/PLAN.md`. Before requesting
  any permission, first try to update `STATUS` with the exact blocked action
  and scope. If a real platform approval is still required, use that platform
  approval flow; do not substitute an ordinary chat request.
- Set speaker-note text to 9 pt on every slide in every batch, including slides
  with no authored notes. Preserve existing note text. For an empty note body,
  add one ordinary space as an invisible editable run and explicitly style it
  to 9 pt; this makes the setting survive Google Slides import. Verify note
  text-size metadata by native readback and never inspect notes visually.
- At the beginning of every new session, check which permissions are active.
  Ask only for a missing permission that is needed for the work: connected
  Google Drive access limited to the project folder and session-wide
  `libreoffice --headless` authorization, including conversions beyond PDF
  export. Before requesting any permission, first try to update `STATUS` with
  the exact blocked action and scope; use the actual platform approval flow
  when required, not an ordinary chat request. Do not ask again after the user
  grants it. Do not ask permission to commit or push; the user handles those
  actions.
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

As of 2026-11-28, the same Batch 1 WIP contains 142 ordered slides at native
revision `81I4pqOtZCYd2A`. Its latest slide PDF is the Round 34 Google export:
142 pages, 5,278,199 bytes, SHA256
`f209ce582c79ec0934992b157639c6ead8b53ff237867988ba5e2641cc5f72aa`. Round
24 fixed the two source-deck dividers; Round 25 repaired the Course Grading
tables; Rounds 30–34 repaired selected pages. All 52 build-bearing slides are
classified. The local candidate has 272 mapped slides; 130 candidate rows
remain to integrate at 32 anchors in the existing WIP. Its correspondence map
was corrected in 14 source/build-state matches. Do not treat those map changes
as visual repairs or as a repaired-slide count.

Every WIP slide now has editable 9 pt speaker-note text, including a single
whitespace run on each of the 66 previously empty note pages. Native readback
confirmed 142 slides and 339 note runs, all 9 pt. The updated local builder
and build-state expander also add blank 9 pt notes to slides without source
notes. Speaker notes are checked by metadata only and are not visually
inspected. Batch 1 still needs structural integration, a fresh Google PDF,
full-page review, and the acceptance record. Do not start Batch 2 yet.
