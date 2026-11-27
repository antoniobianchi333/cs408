# Batch 1 diagnostic: Week 1

**Updated:** 2026-11-27  
**Status:** The Keynote show order and active-slide sequence are decoded.
Introduction has 92 ordered nodes, 62 marked skipped, and 30 active;
Fault/Error has 108 nodes, 29 skipped, and 79 active. Each active sequence
matches its Fall PDF page map and LibreOffice candidate in order. The 111-page
baseline now has a 142-page partial expansion. Seven of 52 build-bearing slides
are classified: three paragraph reveals, one two-state AI-policy subtitle/list
build, one single-chunk All at Once slide with no additional state, one
six-state mixed banner/question build, and one two-state image/headline build.
The 37 states across the six expanded slides passed local review, native Google
readback, and page-by-page PDF inspection. Round 23's local Arial and bullet
repair for page 12 survived Google import without a native correction.
The Round 21 Google import needed a targeted native `DOT` outline update on
its six banner shapes. Round 22 needed a 31 pt native headline plus a 75,000
EMU vertical adjustment after Google import. The full 142-slide WIP deck is
now in the shared Drive root as
[CS408 Batch 1 - WIP - needs fixes](https://docs.google.com/presentation/d/1EYXO-ZvBcLhUg9-JdA0t6C78sSx6Ki-4OGnIeYM9IME/edit);
native outline readback confirmed 142 ordered slides. The user reports a brief
visual check found about 90% of slides looking fine. Full build classification,
remaining repairs, and full-batch Google PDF inspection remain open.
Keep the local PPTX and maps as the reproducible source; use the full native
Google deck as the working surface for iterative visual fixes. Apply confirmed
repairs in that deck, rebuilding locally only when a content or structural
change requires it. See the [route decision](../SLIDE_CONVERSION.md#repair-route-decision-local-first-default-google-first-fallback),
[Round 17 repair pilot](../SLIDE_CONVERSION.md#round-17--introduction-page-17-repair-pilot),
[Round 21 build pilot](../SLIDE_CONVERSION.md#round-21--batch-1-introduction-mixed-bannerquestion-build),
[Round 22 build pilot](../SLIDE_CONVERSION.md#round-22--batch-1-introduction-page-18-imageheadline-build),
and [Round 23 build pilot](../SLIDE_CONVERSION.md#round-23--batch-1-introduction-page-12-ai-policy-build).

**User-owned exception:** Do not edit or repair the Introduction course
schedule slide. The user will correct that slide directly; it is outside the
agent's repair scope and is not a reason to delay the other Batch 1 work.

## Scope and source of truth

Batch 1 follows the current Fall syllabus and keeps both Week 1 topics whole:

1. `01-408st-introduction.key` — Introduction and administrivia.
2. `02-408st-fault-error-failure.key` — Faults, Errors, and Failures.

The matching current Fall references are
[`01-408st-introduction.pdf`](../../../slides/f26-pdfs/01-408st-introduction.pdf)
(30 pages) and
[`02-408st-fault-error-failure.pdf`](../../../slides/f26-pdfs/02-408st-fault-error-failure.pdf)
(79 pages). The source packages' unskipped Keynote nodes match those PDF pages
in order; visual checks remain required to confirm page-level fidelity.
Preserve the newest Fall content and use the source package to resolve content
absent from an older PDF.

## Conversion and alignment evidence

On Linux, LibreOffice converted the two selected `.key` packages to PPTX.
The candidates are ignored work files:

- `out/.build/batch-01/source-pptx/01-408st-introduction.pptx`
- `out/.build/batch-01/source-pptx/02-408st-fault-error-failure.pptx`

The generated PPTX files contain 92 and 108 slides, while the corresponding
current Fall PDFs contain 30 and 79 pages. A structural decoder now reads the
Keynote show tree and `isSkipped` values directly. The 62 skipped Introduction
nodes and 29 skipped Fault/Error nodes account for the count difference; the
remaining 30 and 79 nodes match every PDF page-map candidate in order. This
settles which slide records are in the active show. Animation states still
need a separate review because one active slide can have many build chunks.

[`audit_batch_source_alignment.py`](../audit_batch_source_alignment.py)
produced an ordered text-based page alignment. It proposes 30 Introduction
and 79 Fault/Error candidate slide matches. The four CSVs linked from the
[batch workspace index](README.md) preserve both the page proposals and the
audit of unmatched candidate slides. Alignment scores are triage evidence;
they do not prove visual correctness or source visibility.

Current visual work files, including local PDF renders and side-by-side
contact sheets, are under ignored `out/.build/batch-01/`. They are diagnostic
and must be regenerated if absent. The Fault/Error sheets covering reference
pages 33–79 and contact sheets of every unmatched candidate have now been
generated and inspected. The source-order/skip audit resolves active versus
skipped records; unmatched visual candidates still need comparison with the
current source to decide whether any unique instructional content is retained.

## Decoded Keynote order and build metadata

[`audit_keynote_build_sequences.py`](../audit_keynote_build_sequences.py)
reads the ordered slide tree, each slide node's skip flag, the slide's build
archives, and its build chunks. It uses the system Snappy library through
Python `ctypes`; it does not install a Python package or edit a source file.
The two source packages record Keynote 14.4 and 15.3.1 in their build history.
The audit's relevant type and field numbers match the reverse-engineered
[Keynote archive map and build-order notes](https://docs.rs/iwork/latest/src/iwork/keynote.rs.html).

| Source deck | Ordered Keynote nodes | Skipped | Active | Fall PDF pages | Page-map sequence | Active slides with builds | Active build archives / chunks |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| Introduction | 92 | 62 | 30 | 30 | 30/30 match candidate order | 17 | 74 / 113 |
| Fault/Error/Failure | 108 | 29 | 79 | 79 | 79/79 match candidate order | 35 | 92 / 185 |

The full ordered records are in the [Introduction build-sequence audit](batch-01-introduction-build-sequences.csv)
and [Fault/Error build-sequence audit](batch-01-fault-error-build-sequences.csv).
The page-map check assigns each unskipped source slide to the same-numbered
LibreOffice candidate slide, and the source-order audit confirms every mapped
PDF page. This explains the prior 92/108 versus 30/79 count difference.

**Do not use cached node counters as the build map.** In these packages,
`hasBuilds` remains false even on slides with decoded builds, and cached
`buildEventCount` often differs from the number of chunks. The ordered
`SlideArchive.buildChunks` references are the sequence signal. The audit
records each chunk's build, delivery/effect, order, automatic flag, and source
slide; it does not render the intermediate states or prove that every chunk
changes meaningful instructional content. Review those states and retain
separate slides only for meaningful visible changes.

## Confirmed findings so far

### Introduction

- Candidate slide 1 is marked skipped in the Keynote show tree. The current
  Fall PDF page 1 maps to active candidate slide 2.
- The current 30-page PDF maps in order to all 30 unskipped slides. The other
  62 candidate records are marked skipped; do not carry them over merely
  because LibreOffice rendered them.
- The provisional map flags low-text or image-heavy reference pages 7–9,
  13, 20, and 23 for direct visual/source-package review.
- Initial comparison found empty grading tables where the Fall PDF has values,
  a stale `Two-Step Submission` overlay, a clipped objectives callout, and a
  distorted diagram. Rebuild these as native text, tables, and shapes where
  practical. The course schedule slide is user-owned: leave it unchanged and
  do not count its schedule content as an agent repair or acceptance blocker.
- The current Introduction source page 2 still says `Now - Depths of Winter`
  in both the Keynote-derived slide and the reference PDF. The current syllabus
  identifies Fall 2026; the batch repair replaces that stale seasonal phrase
  with `Fall 2026` and fixes the overlapping WHO/WHERE/WHEN labels, portrait
  collision, and body-text width while keeping the text and photos editable.
  This is an intentional content correction based on the syllabus, not a claim
  that the source PDF already has the repaired wording.
- The editable repair has now been applied to source page 2 and included in a
  provisional batch assembly. Its local LibreOffice page 3 render was checked:
  instructor and TA text fits in the center column, WHERE/WHEN labels and
  values occupy separate aligned rows, and the portraits remain visible. The
  imported 34 pt body text was reduced to 28 pt to fit. A separate one-slide
  Google Pilot confirms the local repair survived import and the Google PDF
  renders all these rows cleanly. The final two-pass native Google repair is
  also readable but renders Fall 2026 in black instead of the local repair's
  orange; see the
  [route decision record](../SLIDE_CONVERSION.md#repair-route-decision-local-first-default-google-first-fallback).
- Source page 17 is now repaired locally with editable text and shapes. The
  blue response banner's text was below the canvas and horizontal; the repair
  positions and rotates it over the existing native blue freeform, uses an
  explicit two-line break, and corrects its dotted outline for the local PDF.
  The question list now uses a visible native bullet, a font size that matches
  the reference wrapping, and measured 112% line spacing. Arial at 91% of the
  imported mixed title sizes closely matches the reference width while keeping
  its separate blue, bold, and regular text runs. The full local candidate's
  output page 18 visually matches reference PDF page 17. The Google pilot was
  first imported before the local title adjustment; native text-size and
  `DOT` outline updates then corrected that pilot. It has one editable slide
  and a one-page 39,981-byte Google PDF. The pilot is
  [in the shared Pilots folder](https://docs.google.com/presentation/d/1Gat0ZLl5w5iSrU4tDtZOgEEwQnvEIANW3pUV2vsqw48/edit).
  This proves the native fallback for the tested title and outline, not that
  the final local title change has survived a full-batch import; verify it in
  the integrated Batch 1 Google PDF.
- One current Fall screenshot/image page is absent or materially different
  in the `.key` conversion. Check the exact source revision and embedded media
  before deciding whether a small image crop is required.

### Faults, Errors, and Failures

- Candidate slide 1 and slides 3–19 are marked skipped in the Keynote show
  tree. Current PDF page 1 aligns to active candidate slide 2; the current PDF
  page sequence then resumes at candidate slide 20.
- The 79 current PDF pages map in order to the 79 unskipped slides. The other
  29 candidate records are skipped slides; active-slide build chunks are
  recorded separately in the sequence audit.
- Pages 33–43 (modeling computations and number-state examples) mostly retain
  their content. Check code/table legibility at full size and preserve any
  meaningful state sequence.
- Reference page 68 (candidate slide 94) has a correct underlying photo, but
  the editable `Testing`/`Debugging` labels wrapped and lost the source
  lettering. A 40 pt local repair still wrapped the final G in `DEBUGGING`.
  Reducing that label to 36 pt produced a Google-exported page with the photo
  visible and both underlined, rotated labels on one line. The corresponding
  Google-first PDF instead has a black field where the photo belongs. Keep the
  36 pt local rule and verify it again in the integrated batch.
- Reference page 65 (candidate slide 90) and pages 73–74 (candidate slides
  101–102) have connector geometry extending far beyond the 1024 pt slide
  canvas, causing arrows to cross diagram text. The local repair replaces only
  each diagram region with a 150 dpi crop from its matching Fall PDF page; the
  titles remain editable. This is a last-resort, diagram-only image fallback
  because the converted connector paths are corrupted. Latest local renders
  visually match the references; verify these crops in Google.
- Reference page 76 (candidate slide 104) and page 77 (candidate slide 105)
  were separate teaching states: the first shows the three input columns and
  asks which combinations are possible; the next adds the `Possible?` answer
  column. Their blank 9-row tables have been restored as native editable table
  cells with the reference Yes/No values and colors. The local renders match
  the PDF; keep both pages and verify Google's table import.
- Reference page 75 (candidate slide 103) is the text-only Bugs-versus-Faults
  definitions page; it has no diagram arrows. Review its typography at full
  size alongside the remaining code/example pages before acceptance.
- Several code/example pages near the end need full-size inspection for text
  collisions and clipping. Adjust text boxes or font sizes before considering
  image fallback.

## Visual triage of unmatched candidates

The reusable
[`render_unmatched_contact_sheets.py`](../render_unmatched_contact_sheets.py)
script generated contact sheets for all 62 unmatched Introduction candidates
and all 29 unmatched Fault/Error candidates. They are in ignored
`out/.build/batch-01/unmatched-review/` and can be regenerated from the local
PDFs and candidate-audit CSVs.

- **Introduction:** candidate 1 is the Fall 2025 title and is obsolete.
  Candidates 18–19 add objective/interactivity content around the selected
  `Who` pages; their relation to current builds is unresolved. Candidates
  34–70 are a mixture of polls, `When to test?`, reliability images,
  duplicate teaching content, and images/text that resemble current reference
  pages. The focused review below shows why they cannot be bulk classified as
  either current builds or stale records. Candidates 71–90 include a prior
  recap and old admin, staffing, policy, and schedule pages. Candidates 91–92 are image-only
  records. Do not bulk-delete these ranges until each potentially current
  build/image state is reconciled with the Keynote slide order and PDF.
- **Fault/Error:** candidates 1 and 3–19 are clearly a Fall 2025 title and
  outdated admin/review material. Candidate 40 (`Defect, incorrect`) and
  candidates 45, 84–86 are alternate/duplicate teaching pages; compare with
  the selected current Fall pages before exclusion. Candidates 92 (`Exercise
  (cont.)`) and 98 (`Finding Faults`) have substantial content overlap with
  current PDF pages 63–64, so they need source/build review rather than
  automatic exclusion. Candidate 87 overlaps the selected crash/failure
  discussion. Candidate 99 is an alternate RIRP diagram. Candidate 108 is an
  unselected summary after the current PDF recap. The selected Fall PDF remains
  the content baseline; preserve only verified current content/build states.

The full numbered inventory and text scores are in the linked candidate-audit
CSVs. An image-only candidate can have a zero text score, and a high text
score can describe an obsolete duplicate; both require visual/source evidence.
The earlier raw-byte `.key` IWA locator found explicit effect markers, including
`apple:bc-appear`, `apple:appear`, `apple:dissolve`, and `apple:dropbuild`; the
Introduction package also contains an `apple:magic-move-implied-motion-path`
marker. In contrast, both generated PPTX files contain zero `<p:timing>` slide
records. LibreOffice therefore does not preserve those Keynote effects in the
current candidates. The [Introduction audit](batch-01-introduction-build-marker-audit.csv)
and [Fault/Error audit](batch-01-fault-error-build-marker-audit.csv) found 32
and 37 slide records with effect markers, respectively. These counts include
transition effects and do **not** equal the number of additional static
slides required. The structural audit now resolves Keynote slide and chunk
order; the raw-marker audits remain useful locators only. Inspect affected
source slides and reconstruct meaningful animation states as separate static
slides in build order. Do not claim the effects were preserved just because
their slide text was converted.

The locator currently links effect-marked records to these reference pages:

- Introduction: 2–6, 12, 14–17, and 25–30.
- Fault/Error: 2, 7, 12, 14, 19–21, 23, 26–27, 30, 32–33, 35, 37, 42, 60,
  64–65, 69–73, 75–77, and 79.

These are **review targets, not an expansion count or a final animation map**.
Some markers describe slide transitions; multiple records can point to the
same page; low lexical scores and image-heavy slides make some matches weak.
Use the new sequence CSVs for active source order and review each chunk's
visible effect before creating cumulative static states.

### Focused Introduction review: reference pages 16–23

The current 30-page Fall PDF maps monotonically to unskipped candidates
2–17 and 20–33. The review below compares skipped candidate records 18–19 and
42–53 with nearby PDF pages. Their skip status is now established by the
Keynote show tree; these whole-slide records are not active build states. Any
additional states must come from the build chunks attached to an active slide.

| Fall PDF page | Provisional candidate | Unmatched records visually checked | Observation and disposition |
| ---: | ---: | --- | --- |
| 16 | 17 | 18 | Candidate 18 combines older learning objectives with the previous class-prompt banner. It is marked skipped in the Keynote show tree and is not a current-page build state. |
| 17 | 20 | 19 | Candidate 19 shows an incomplete poll list under the previous prompt banner and is marked skipped. Candidate 20 is active and matches the reference. Its clipped banner, font substitution, question wrapping, and empty bullet glyphs are repaired locally; output page 18 now matches reference page 17. The Google pilot exposed a wide title and coarse custom border, both corrected with native fallback edits. Verify the integrated local title repair in the final batch import. |
| 18 | 21 | 42–43 | Candidate 42 shows the rocket image with a short claim; candidate 43 shows a separate quote-only state. Both whole-slide records are skipped in the Keynote show tree. Active candidate 21 contains the full image and article excerpt. |
| 19 | 22 | 44 | Candidate 44 repeats the “What if I don’t care about rockets?” question. It is visually redundant with the selected PDF page; do not add it without evidence of a distinct intended teaching state. |
| 20 | 23 | 45 | Candidate 45 is the same satellite image as the image-only PDF page and selected candidate 23; it is a skipped whole-slide record, not an active build state. |
| 21 | 24 | 46–48 | These show an annotated blackout map, a text-led blackout summary, and two satellite maps. Candidate 24 matches the current PDF page. The other whole-slide records are marked skipped. |
| 22 | 25 | 49 | Candidate 49 repeats the “What if I don’t care about the power grid?” question and is visually redundant with the selected page. |
| 23 | 26 | 50–53 | Candidate 50 is blank; 51 is a server-room photo; 52 is a casualty statement; 53 says “Therac-35.” They are marked skipped; the active candidate 26 is the AWS outage article screenshot in the current PDF. |

The active Keynote order confirms the current 30-page reference sequence.
Skipped records are outside the show; active-slide build chunks are the path
for any additional static states. Keep the Introduction image discrepancy
and any page-level differences open for visual/source review. Do not use the
raw 92-slide LibreOffice count as the final output count. Meaningful build
expansion raises the 111-page baseline. Six build expansions and one
no-expansion decision are now classified:

- Introduction PDF page 4 has 11 chunks and 11 cumulative states at output
  pages 5–15. Every local and Google state was reviewed; the final state
  matches reference page 4. The 27.5 pt Arial text and native bullets preserve
  editable emphasis while fixing missing bullets and line fit.
- Introduction PDF page 6, Course Grading, has 7 ordered chunks and 7
  cumulative states at output pages 17–23. Every local and Google state was
  reviewed; the final state matches reference page 6. The repair sets the
  heading/body box sizes and visible native bullets; the long `~24` line stays
  on one line after Google import. Bold/color emphasis and the source's bullet
  hierarchy remain editable.
- Introduction PDF page 12 has two ordered `All at Once` builds: first the
  subtitle “Only when explicitly permitted,” then the AI-policy list. Its two
  cumulative states occupy output pages 29–30. The local repair sets explicit
  Arial sizes and native bullet indentation; both native Google pages retained
  the line breaks and editable text without further correction.
- Introduction PDF page 15, Course Objectives, has 9 ordered chunks and 9
  cumulative states at output pages 33–41. Every local and Google state was
  reviewed; the final state matches reference page 15. Explicit Arial fonts,
  native bullets, and paragraph spacing preserve hierarchy, emphasis, and line
  fit through the Google import.
- Introduction PDF page 16 has one `All at Once` pop chunk. It remains one
  static slide, with no additional output state.
- Introduction PDF page 17, the mixed response-banner and question build, has
  six ordered states at output pages 43–48: banner first, then five cumulative
  question reveals. All local and Google states were reviewed. A native Google
  `DOT` outline update fixes the coarse dashed border that appeared after
  import; text, title, and banner stay as native elements.
- Introduction PDF page 18 has two ordered `All at Once` builds: first the
  scanned article excerpt from `Data/pasted-image-4629.tiff`, then the
  separate editable headline. The page 18 reconstruction script restores the
  Keynote image and editable text rather than flattening both into a PDF crop.
  Both local states and both Google PDF pages passed review. Google required
  a 31 pt headline and a 75,000 EMU upward position adjustment; it remains
  editable and one line, with a small residual glyph-height difference.

The 11-slide page 4, 7-slide page 6, 2-slide page 12, 9-slide page 15,
6-slide page 17, and 2-slide page 18 subsets passed native Google readback and
page-by-page PDF review. The current 142-page expanded candidate remains
unimported as a full batch. The [build-expansion manifest](batch-01-build-expansion.json) records
all six expansions, the page 16 no-expansion decision, and their chunk IDs; the
[`expand_batch_build_states.py`](../expand_batch_build_states.py) creates the
cumulative states, and [`prune_pptx_slides.py`](../prune_pptx_slides.py)
creates compact package-preserving pilot subsets. See the [Round 18](../SLIDE_CONVERSION.md#round-18--batch-1-introduction-paragraph-build-pilot),
[Round 19](../SLIDE_CONVERSION.md#round-19--batch-1-course-grading-paragraph-build-pilot),
 [Round 20](../SLIDE_CONVERSION.md#round-20--batch-1-course-objectives-paragraph-build-pilot),
[Round 21](../SLIDE_CONVERSION.md#round-21--batch-1-introduction-mixed-bannerquestion-build),
[Round 22](../SLIDE_CONVERSION.md#round-22--batch-1-introduction-page-18-imageheadline-build),
and [Round 23](../SLIDE_CONVERSION.md#round-23--batch-1-introduction-page-12-ai-policy-build)
records for the native Google links and PDF renders.

## Next actions for this batch

1. Continue classifying active build chunks into meaningful instructional
   states versus decorative effects; update output mappings for every state
   that should become a separate static slide. Seven build-bearing slides are
   classified; 45 of 52 remain unclassified.
2. Resolve the low-confidence and image-heavy page matches against the source
   package and PDF. Record a final page/build disposition for every candidate.
3. Finalize the ordered source/build map. The 111-page candidate remains the
   baseline: one editable divider plus 30 mapped reference pages for
   Introduction, then one divider plus 79 mapped reference pages for
   Fault/Error. The current 142-page expansion candidate adds ten homework
   states, six Course Grading states, one AI-policy state, eight Course
   Objectives states, five net slides for the six-state page 17 build, and one
   net slide each for the two-state page 12 and page 18 builds; later states
   may increase the count further. Both dividers show the
   exact filename and topic.
4. Repair the confirmed diagrams, tables, text fit, image composition, and
   any further defects. Preserve notes where present and map all static build
   states to their source. The standalone page 17 local fix appears at output
   page 18 and page 68 at output page 100 in the rebuilt local candidate.
   Google has checked isolated pilots for the page 4, 6, 15, and 17 builds,
   plus the standalone page 17 and page 68 label repairs. Verify all integrated
   content, including pages 65,
   73, 74, 76, and 77, in the final batch. Leave the course schedule slide
   untouched for the user to edit.
5. Keep the full-size WIP deck at the shared Drive root and improve that same
   native presentation in place. Export the initial full Google PDF, compare
   all pages with the references, and apply confirmed visual fixes directly in
   Google Slides. Use the local PPTX and maps as the reproducible source; if a
   later build-state change alters structure, update the WIP deck and verify
   its affected order/pages. Rename it as accepted only after the full review.

## Open questions and acceptance blockers

- Which decoded build chunks change meaningful content and therefore need
  separate static slides? The chunk order is available; the visual state
  classification is still open.
- Does each current Fall PDF exactly match its `.key` revision? The Introduction
  image discrepancy requires checking the package revision and embedded media.
- Which notes are present on the selected source slides, and does the planned
  package/assembly path retain them?
- Has every Google-exported page been visually reviewed against the exact
  reference? **Not yet.** The WIP deck is uploaded, but its full Google PDF has
  not yet been exported and inspected. The user's brief visual check found
  about 90% of pages looking fine; that is preliminary feedback, not acceptance.
- The Introduction course schedule slide is not an open agent issue. The user
  will update it directly; continue Batch 1 work without changing its schedule
  text.
