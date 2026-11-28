# Fresh-session prompt — resume the CS 408 slide conversion

You are resuming the CS 408 slide-conversion project in a new session or on a
different machine. The user's goal is in [`GOAL.md`](GOAL.md). Treat that goal
as active work: **keep working until all 16 final batches are converted,
uploaded to Google Drive, and verified. Do not stop at a pilot, plan, or
partial batch.**

## Ask for permissions at the beginning

Before tool actions in this new session, ask the user once—in one concise,
grouped request—to confirm or grant the permissions that may not carry over:

- Google Drive connector access to read and edit the shared CS408 project
  folder. Use the dedicated connected account and make Drive calls only within
  the documented project folder.
- One project-wide authorization for any `libreoffice --headless` command,
  including conversions beyond PDF export. The earlier broad grant may have
  applied only to the previous session or machine. Use the session's approval
  flow if it requires an explicit permission request.

If Drive access is already active or a permission is already granted, do not
ask for it again. Continue independent local and read-only work while a needed
permission is pending. Do not ask permission to stage, commit, or push; the user
handles Git publishing.

## Read first

Read these files before making changes:

1. [`out/README.md`](out/README.md) — project rules, status, and navigation.
2. [`GOAL.md`](GOAL.md) — completion criteria and operating rules.
3. [`out/PLAN.md`](out/PLAN.md) — ordered tasks and estimates.
4. [`out/BRANCH_AND_HANDOFF.md`](out/BRANCH_AND_HANDOFF.md) — Git payload and
   restart policy.
5. [`out/combined/BATCH_BOUNDARIES.md`](out/combined/BATCH_BOUNDARIES.md) — the
   completed 16-batch outline and whole-topic rules.
6. [`out/combined/SLIDE_CONVERSION.md`](out/combined/SLIDE_CONVERSION.md) — conversion
   and repair evidence, especially Rounds 24–25.
7. [`out/combined/GOOGLE_DRIVE_ACCESS.md`](out/combined/GOOGLE_DRIVE_ACCESS.md) — Drive
   access, file organization, pacing, export, and no-curl rules.
8. [`out/combined/final-batches/README.md`](out/combined/final-batches/README.md) and
   [`out/combined/final-batches/batch-01-diagnostic.md`](out/combined/final-batches/batch-01-diagnostic.md)
   — Batch 1 map, status, repairs, and open issues.
9. [`out/combined/repair_batch01_introduction.py`](out/combined/repair_batch01_introduction.py)
   and the linked batch build/repair scripts — reproducible repair entry
   points.

The main `out/README.md` is the navigation hub and must link every relevant project
Markdown file, script, map, and artifact folder. Update it and the PLAN as the
work changes. Refresh PLAN about hourly during sustained work and at each major
milestone.

## Verify this checkout and Drive state

- Check `git branch --show-current`, `git status --short`, and the current Git
  config for information. The intended work branch is `spring+2027+bianchi`.
  Do not change remotes/config. The user handles staging, commits, and pushes;
  **do not commit or push**.
- The user will add and commit the project changes. Ensure all durable scripts,
  maps, manifests, and documentation are tracked or visible as intended. Do not
  add generated full-size PPTX/PDF/render outputs from `.build`.
- The current `out/.build/` directory is ignored scratch space and may be
  missing on this machine. Do not treat local `.build` paths below as durable
  handoff artifacts. Regenerate temporary outputs from tracked scripts and
  authoritative sources as needed.
- Recheck Google Drive through the connected Drive/Slides tools. Use only the
  project folder
  [`16vTRNocHa1rlPN1bii_w0b8Ce90XrFbn`](https://drive.google.com/drive/folders/16vTRNocHa1rlPN1bii_w0b8Ce90XrFbn)
  for full batch decks; small tests belong in its `Pilots` subfolder
  [`1PHuKHahwY2PxviNWTM2f8kYmb7K-37Dj`](https://drive.google.com/drive/folders/1PHuKHahwY2PxviNWTM2f8kYmb7K-37Dj).
  Read the exact current Drive metadata before acting; do not rely on a file
  name alone.
- Keep Drive operations serial, with at least 5.5 seconds between calls. Do
  not enumerate unrelated Drive contents. **Never use `curl` or another shell
  or network downloader** for Drive files or signed references. Follow the
  connected export helper in the Drive guide and its bounded
  `include_base64: true` compatibility path.

## Current Batch 1 state (handoff snapshot: 2026-11-27)

The source-selection audit and 16 conceptual boundaries are complete. Use
Fall 2026 sources wherever they cover a topic; include only the six complete
older-only units already selected in the audit. Do not redo content selection
or split original decks/topics.

Batch 1 is the only active final batch and is **not accepted**. The full native
Google Slides WIP is in the shared folder root, not `Pilots`:

- Deck ID: `1EYXO-ZvBcLhUg9-JdA0t6C78sSx6Ki-4OGnIeYM9IME`
- URL: https://docs.google.com/presentation/d/1EYXO-ZvBcLhUg9-JdA0t6C78sSx6Ki-4OGnIeYM9IME/edit
- It has 142 ordered slides. The latest checked native revision was
  `MDNZfA_IWLdgQg`; verify again before a write.
- Latest full Google PDF: 142 pages, 5,233,045 bytes, SHA256
  `5b9a067f0c27afe19439008a4e8b291d86de6842da6f692309076cb8b0bdf66d`.
  Previous local copy was
  `out/.build/batch-01/round24-grading-cell-style/presentation.pdf`; re-export
  if the ignored file is absent or the Drive deck has changed.
- The Drive title still includes `Round 23`; it is the same WIP deck. Do not
  create a second full-batch deck or move it into `Pilots`.

### Confirmed divider rule — Round 24

The two source-deck divider slides are output pages 1 and 63. Their first
Google import was blank because the generated text shapes lacked explicit
DrawingML rectangle geometry, not because Arial was missing. The reusable
builder now emits `a:prstGeom prst="rect"`. Style every divider with a
full-slide solid pale-yellow `#FFF2CC` background, centered editable exact
filename at 24 pt bold Arial, and centered editable following-topic text at
28 pt regular Arial. The two-slide Google pilot is
[`1K9wKFR8PCSwFg1DOCdTAqFPyNwBLojTJfruFe2Jy6Bs`](https://docs.google.com/presentation/d/1K9wKFR8PCSwFg1DOCdTAqFPyNwBLojTJfruFe2Jy6Bs/edit?usp=drivesdk).
The current full WIP was repaired in place and visually checked in the Google
PDF.

### Confirmed grading-table repair — Round 25

Output pages 24–25 correspond to `slides/f26-pdfs/01-408st-introduction.pdf`,
pages 7–8. The source title is 80 pt Source Sans Pro; table cells use 66 pt
Bebas Neue. The full Google WIP now has those styles and middle-aligned cells.
Page 24 row heights are 92/92/77/92/92 pt; page 25's existing row heights
already matched. The full Google export was visually checked on both pages.

The two-slide PPTX import pilot rev2 is
[`1zpf9oltsH7I2OY9IrnIrTFKPhKpgb4AnMrFpSLM3A-w`](https://docs.google.com/presentation/d/1zpf9oltsH7I2OY9IrnIrTFKPhKpgb4AnMrFpSLM3A-w/edit?usp=drivesdk).
Native readback confirms Bebas Neue 66 pt and MIDDLE alignment. The PPTX
import maps the Source Sans Pro title to Arial 80 pt; the full WIP received a
direct native Source Sans Pro repair. The first pilot lacked `a:tcPr
anchor="ctr"` and read back as TOP; include that cell property in future local
PPTX repairs. See the Round 25 runbook for evidence and the official API
details.

Linux LibreOffice on the previous machine did not have Bebas Neue or Source
Sans Pro (`fc-match` resolved both to DejaVu Sans). Its local PDF wrapped the
labels and is not a reliable visual acceptance result for these fonts. The
Google-import pilot rendered Bebas Neue correctly. Use the exact Google PDF
for acceptance, and document font substitution when it affects local preview.

The reproducible source repair is in tracked
[`out/combined/repair_batch01_introduction.py`](out/combined/repair_batch01_introduction.py).
The previous machine's current local full candidate was
`out/.build/batch-01/assembled/batch-01-expanded-candidate-round24b.pptx`.
It was patched only at physical `slide8.xml` and `slide9.xml` from the repaired
Introduction package, leaving the rest of the 836-part candidate unchanged
and preserving the page 18 image. That candidate is ignored scratch and may
not be available here. A clean reassembly from the manifest previously omitted
the page 18 image; restore that asset with the tracked
`out/combined/prepare_intro_page18_build.py` before replacing the full candidate.

## Immediate work — finish Batch 1

1. Read the latest diagnostic and verify the current deck/revision in Drive.
   Continue working in the same native WIP.
2. Continue full-size follow-up on the flagged pages. Known leads from the
   contact-sheet review: output page 2 cover/panel/title; page 64 second cover;
   pages 42–48 dotted-banner/build states; pages 49–50 article-image/headline;
   page 70 layout; pages 87–90 composites; pages 123–125 error-state diagram
   and callouts; page 132 testing/debugging diagram/code; and pages 139–140
   table/title sizing. Regenerate only the pages needed from the current Google
   PDF; old broad contact sheets predate the divider repair.
3. Keep output page 3 aligned with the latest Fall content. Do not edit the
   course schedule slide (output page 26); the user will fix it.
4. Confirm the full-deck status of the page 17 dotted-outline repair and the
   page 18 article image. Check existing local repairs on Introduction pages
   2, 6, 12, 15, 17 and Fault/Error pages 65, 68, 73, 74, 76, 77 against the
   full Google export.
5. Classify the 45 remaining build-bearing slides. Expand only meaningful
   animation/build states, preserve source order, update the source/build map,
   and integrate structural changes into the same WIP deck.
6. Re-export and inspect all 142+ pages after repairs. Complete the final map,
   native readback, source comparison, exception log, and acceptance record.
   Begin Batch 2 only after Batch 1 passes every gate.

Do not stop after this handoff document is read. Continue the conversion work
until the completion criteria in `GOAL.md` are met. Report progress briefly,
update the docs as reality changes, and ask the user only when a genuinely
blocked decision or missing source requires their input.
