# Fresh-session prompt — resume the CS 408 slide conversion

You are resuming the CS 408 slide-conversion project in a new session or on a
different machine. The user's goal is in [`GOAL.md`](GOAL.md). Treat that goal
as active work: **keep working until all 16 final batches are converted,
uploaded to Google Drive, and verified. Do not stop at a pilot, plan, or
partial batch. Do not edit `GOAL.md` unless the user explicitly asks.**

## Check permissions at the beginning; update STATUS before any request

At the start of a new session, check which permissions are active. Do not send
an ordinary chat approval question. Request only a permission that is actually
missing and needed before using Drive or running LibreOffice. Before any such
request, first try to update the live `STATUS` Doc with the exact blocked
action and scope; if that update is itself blocked, use the platform's real
approval flow for the blocked operation. The request should cover:

- Google Drive connector access to read and edit the CS 408 project folder
  through the dedicated connected account. Use Drive only within the documented
  project folder, even if the connected account can see other files.
- One session-wide authorization for every project `libreoffice --headless`
  command, including conversions beyond PDF export. Use the platform's
  permission flow when it requires explicit approval; after approval, do not
  ask again during that session.

If a permission is already active, do not request it again. Continue
independent local work while an actual platform approval is pending. Do not ask
permission to stage, commit, or push; the user handles Git publishing. The last
confirmed Google Drive plugin setting is “Allow all tools.” Check whether it
remains active in a new session. Even with that setting, keep project
operations limited to the CS 408 folder.

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
   and repair evidence, especially Rounds 24–40.
7. [`out/combined/GOOGLE_DRIVE_ACCESS.md`](out/combined/GOOGLE_DRIVE_ACCESS.md) — Drive
   access, file organization, pacing, export, and no-curl rules.
8. [`out/combined/final-batches/README.md`](out/combined/final-batches/README.md) and
   [`out/combined/final-batches/batch-01-diagnostic.md`](out/combined/final-batches/batch-01-diagnostic.md)
   — Batch 1 map, status, repairs, and open issues.
9. [`out/combined/repair_batch01_introduction.py`](out/combined/repair_batch01_introduction.py),
   [`out/combined/prepare_intro_page18_build.py`](out/combined/prepare_intro_page18_build.py),
   and the linked batch build/repair scripts — reproducible repair entry
   points, including restoration of the page 18 image omitted by a clean
   reassembly.
10. [`out/combined/speaker_notes.py`](out/combined/speaker_notes.py) — ensures
    every PPTX slide has a 9 pt speaker-note run, including slides with no
    source notes.

The main `out/README.md` is the navigation hub and must link every relevant project
Markdown file, script, map, and artifact folder. Update it and the PLAN as the
work changes. Refresh PLAN about hourly during sustained work and at each major
milestone.

Maintain one native Google Doc titled `STATUS` directly in the CS 408 project
Drive folder root, above `Pilots`. Create it if absent; verify its exact file
metadata before editing. About hourly during sustained work and after major
milestones, refresh that same document in this order: approvals needed (or
none), current 5-hour and weekly usage percentages from the root
[`codex_usage.py`](codex_usage.py) script, current work and near-term plan,
the full contents of `out/MANUALLYCONVERT.md`, and the full contents of
`out/PLAN.md`. Read the local sources for each refresh, and link the verified
Google Doc from `out/README.md`.

The current verified `STATUS` Doc is
[`STATUS`](https://docs.google.com/document/d/1TAFn9A9Nkkr8YU8R0Hpfge4Q7MBOvBPT4F7XHiDG9UU/edit),
Drive ID `1TAFn9A9Nkkr8YU8R0Hpfge4Q7MBOvBPT4F7XHiDG9UU`, parent folder
`16vTRNocHa1rlPN1bii_w0b8Ce90XrFbn`.

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
- Read `codex_usage.py` and use it for every `STATUS` refresh. The working
  checkout may show it as untracked; do not overwrite or remove it.
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
- Keep the existing 142-slide Batch 1 WIP in the shared root and repair that
  same native presentation in place. Read its current metadata and revision
  before edits; never create a duplicate full-batch deck or move it into
  `Pilots`. Use `Pilots` for small isolated tests only. Read back changed
  native objects, export one fresh Google PDF after a repair set, and inspect
  affected pages against the matching Fall PDF. For a new batch, upload one
  clearly named `WIP - needs fixes` deck directly to the shared root, then
  rename it only after the full acceptance review.
- Set speaker-note text to 9 pt on every slide, including slides with no
  authored notes. The builder creates a notes page with one ordinary-space
  run on an empty body and explicitly styles every run to 9 pt. Confirm by
  native note-text readback only; do not inspect notes visually.

## Current Batch 1 state (handoff snapshot: 2026-11-28)

The source-selection audit and 16 conceptual boundaries are complete. Use
Fall 2026 sources wherever they cover a topic; include only the six complete
older-only units already selected in the audit. Do not redo content selection
or split original decks/topics.

Batch 1 is the only active final batch and is **not accepted**. The full native
Google Slides WIP is in the shared folder root, not `Pilots`:

- Deck ID: `1EYXO-ZvBcLhUg9-JdA0t6C78sSx6Ki-4OGnIeYM9IME`
- URL: https://docs.google.com/presentation/d/1EYXO-ZvBcLhUg9-JdA0t6C78sSx6Ki-4OGnIeYM9IME/edit
- It has 142 ordered slides at native revision `81I4pqOtZCYd2A`; verify again
  before a write. The 9 pt notes-only change left slide order and visible slide
  content unchanged. Drive metadata confirms native Slides type, project-root
  parent, and 20,356,502 bytes.
- The Round 34 Google PDF has 142 pages, 5,278,199 bytes, and SHA256
  `f209ce582c79ec0934992b157639c6ead8b53ff237867988ba5e2641cc5f72aa`. Its
  local copy is under `out/.build/batch-01/round34-final-review/`; regenerate
  through the connected export helper if absent or if Drive has changed.
- The Drive title still includes `Round 23`; it is the same WIP deck. Do not
  create a second full-batch deck or move it into `Pilots`.

The current local candidate has 272 ordered slides and a 272-row map at
`out/.build/batch-01/round39-page24-repair/`; its PPTX ZIP/order checks pass.
Its diagnostic PDF has 272 pages, is 5,228,469 bytes, and has SHA256
`86b78b494deac683ab634a181623566c16b373859d1ef00da044b716e145cb53`. The
PPTX is 41,741,711 bytes and has SHA256
`3fc340887af03f12bd5669a4dbfe5453f5e4ea06714121e48c376df56f96c164`. Linux
LibreOffice substitutes fonts, so use Google PDF rendering for font-sensitive
review. All 52 build-bearing slides are classified: 37 source slides expand
into 198 cumulative static states, and 15 no-expansion decisions retain one
final static slide. The durable map is
[`batch-01-round39-expanded-map.csv`](out/combined/final-batches/batch-01-round39-expanded-map.csv).
Round 39 added local source repairs for Fault/Error PDF pages 24, 61, and 69
(output pages 130, 202, and 224–225). Round 28's focused 8-slide pilot in
`Pilots` verified the page 2–3 and page 27 states against exact Fall PDFs.
Round 29 repaired output page 2 with
the exact Fall cover crop behind editable title/quote objects and repaired
output page 64's cover panels/title directly in the same full native WIP.
Readback and the latest 142-page Google PDF confirmed both pages against their
exact Fall cover references. Rounds 30–34 then repaired selected pages in the
same WIP, including pages 42–50, 64, 70, 87–90, 123–125, 132, and 139. The
final page 42 heading adjustment was compared with exact Fall Introduction
PDF page 16. Native readback after the notes-only update confirms 142 note
shapes and 339 text runs, all 9 pt. The 66 previously empty placeholders now
have a single ordinary-space run; preserve note content and do not inspect
notes visually. The local builder and expander now apply 9 pt to every slide,
including blank notes. The 272-slide local structure has not yet been
integrated into the WIP. Full-page review has not established a reliable
repaired-page percentage or remaining-defect count.

The latest notes-free native-text reconciliation corrected 14 provisional
WIP-to-candidate state matches. Its correspondence map covers all 142 current
WIP slides; its gap map records 130 remaining candidate rows at 32 insertion
anchors. Continue from these maps and the tracked
[reconciler](out/combined/reconcile_batch01_wip_candidate.py); do not recreate
the earlier unverified alignment. The slides themselves were not altered by
these mapping corrections. The latest correspondence map is based on the
pre-notes revision; slide text and order are unchanged at revision
`81I4pqOtZCYd2A`.

Round 40 verified the Slides API sequence for inserting a missing static
state: `duplicateObject` with a child-ID mapping followed by `deleteObject`
worked in one batch update, and `updateSlidesPosition` placed the clone at the
required insertion index. The nine-slide API pilot is in Drive `Pilots` as
`1qz2QdqzzT0m5tlSm1iS2LhOUHAKenZ0UonmSPU9z7R0`; do not use it as a full-batch
deck. The Round 40 note-format pilot also confirmed that an empty native notes
shape needs a whitespace run before `updateTextStyle` can set it to 9 pt.

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

Before Round 26, the interim local candidate in this session had a 142-row map
and a 142-page diagnostic PDF. Those checks were superseded by the current
147-slide Round 27 candidate described above. The page 18 reconstruction must
read its separate editable headline from the unrepaired converted Introduction
PPTX, then run before the build-state expander. These are ignored scratch files
and may be missing in a later session; regenerate from the tracked scripts and
sources.

## Immediate work — finish Batch 1

1. Read the latest diagnostic and verify the current deck/revision in Drive.
   Continue working in the same native WIP.
2. Review every page in the 272-slide local candidate against exact Fall PDFs
   where available. Include the Introduction page 26 reveal states (outputs
   64–72) and editable text-layout repairs on Introduction page 26 and
   Fault/Error pages 12 and 69. Recheck the existing WIP repairs in the fresh
   Google PDF. Do not edit the user-owned schedule slide at Google page 26 or
   local page 29.
3. Keep output page 3 aligned with the latest Fall content. The user owns the
   course schedule slide: it is output page 26 in the current Google WIP and
   page 29 in the Round 39 local candidate. Do not edit it.
4. Confirm the full-deck status of the page 17 dotted-outline repair and the
   page 18 article image. Check existing local repairs on Introduction pages
   6, 12, 15, 17 and Fault/Error pages 65, 68, 73, 74, 76, 77 against the
   full Google export; Rounds 29–34 applied and checked additional repairs.
5. All 52 build dispositions are complete. Repair defects found by the full
   local review, then integrate the reviewed 272-slide structure into the same
   WIP deck. Re-export and inspect every Google page after integration.
6. Complete the final map, native readback, source comparison, exception log,
   and acceptance record. Begin Batch 2 only after Batch 1 passes every gate.

## Repair route to use

Use local PPTX repairs to create reproducible source content and to fix
content, media, or structural issues that must survive import. After a full
batch is uploaded, treat that same native Google Slides deck as the live
surface for confirmed visual-only fixes; avoid re-importing the whole deck for
each adjustment. Rebuild and reconcile the WIP only when source content, build
states, slide order, or structure changes, or when the evidence shows a local
repair is needed to preserve the intended result through import. The paired
page 2 and page 68 tests are evidence for local source repair in those cases;
page 17 and page 24–25 show where native Google edits address import-specific
differences. Record which route each repair used in the
[Batch 1 diagnostic](out/combined/final-batches/batch-01-diagnostic.md) and
[conversion runbook](out/combined/SLIDE_CONVERSION.md).

Do not stop after this handoff document is read. Continue the conversion work
until the completion criteria in `GOAL.md` are met. Report progress briefly,
update the docs as reality changes, and ask the user only when a genuinely
blocked decision or missing source requires their input.
