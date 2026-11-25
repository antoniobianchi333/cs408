# CS 408 slide conversion runbook

[Output index](../README.md) · [Combined collection](README.md) ·
[Google Drive access](GOOGLE_DRIVE_ACCESS.md)

Use this file as the handoff for an agent working on editable Google Slides
imports. The goal is a repeatable workflow for any slide in the collection,
including slides the pilots have never covered. Preserve content, order,
dimensions, and meaningful layout while keeping text, code, and ordinary
shapes editable. Update the roundtrip log after each test.

[Round 4](#round-4--checked) is the complete Part 1 comparison baseline.
[Round 11 revision 4](#round-11--cfg-label-fit-with-original-fonts) is the
latest checked pilot. Rounds 5–11 imported through the connector and
exported Google PDFs for local review. Native text editing/readback passed
on a disposable Round 10 copy and the requested Round 4 deck. A reversible
line-position edit/readback passed on a disposable Round 11 copy; a line
style update was rejected for its imported arrow. See the
[Google API records](GOOGLE_DRIVE_ACCESS.md#verified-live-text-edits) and
[vector edit record](GOOGLE_DRIVE_ACCESS.md#verified-native-vector-object-edit).
Use the [current open-work list](#open-work-after-round-11) before extending
repairs across Part 1 or the full collection.

## File-transfer invariant (current)

Never use `curl` or another shell/network client to download a Drive file or
connector-supplied signed URL. The old failure was a materialization gap:
Drive exported the PDF, but the connector handed back a `file_uri` without a
local path. Use the connected Drive streaming fetch, then the authenticated
browser download for local PDF comparison if needed; native slide thumbnails
are the paced fallback when browser transfer is unavailable. For size
limits, make up to 16 ordered blocks, cutting only between complete source
decks and topics. Do not split a deck/topic to meet a byte target. The current
connector result and detailed recovery order are recorded in the
[Drive guide](GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf).

## Convert and verify an unfamiliar slide

1. Find the matching source slide and intended build. Identify the
   content and relationships that must survive, including exact code
   tokens, formula symbols, graph endpoints, crops, and layer order.
   Check links, notes, and reveal sequences where the source uses them.
2. Inspect the editable PPTX and source locally. A Linux render is optional;
   if its typography differs, check font substitution before using it to
   diagnose the deck. Compare the source with the Google export, which is the
   acceptance render. Inspect the PPTX slide and its dependencies when a
   layer is missing, transformed, or covered. Work out whether the
   discrepancy starts in the source reference, the editable PPTX, or Google.
   Record uncertainty when the available sources disagree.
3. Repair the smallest affected object using the rules below. Start with
   the existing editable object, then reconstruct it from the source if
   needed. For unfamiliar objects such as tables, charts, or equations,
   keep their underlying values or symbols and prefer editable
   representations. Use raster fallback only after the editable repair
   sequence below, and record any resulting loss of editability.
4. Check the repaired slide in Google presentation view at normal size.
   Verify content, layout, and meaning against the source. In a disposable
   copy of the native deck, verify that each repaired object type can still
   be edited as intended. Report visual fidelity and live editability
   separately. Check the neighboring builds and confirm page order when
   returning the slide to a batch.

## Turn each round into a reusable rule

- Record the object type and failure symptom, how to recognize it, where
  the failure first appears, the exact repair, the check that proves it
  worked, and any exceptions. Put the rule in this runbook and link to the
  example slides and reference artifacts in the roundtrip log.
- Before applying a rule across the collection, try it on an affected
  slide from another lecture or layout that was outside the pilot used to
  design the repair. Include an unaffected example to check that the rule
  leaves sound content alone. Run those slides through Google. Record
  which kinds of objects and builds passed and where judgment is still
  needed.
- Automate a repair once its applicability can be checked reliably.
  Identify the target from its content, geometry, or relationships. Treat
  slide numbers, fixed shape IDs, and PDF resource names in pilot scripts
  as example-specific. Send ambiguous cases to visual review and record
  any unverified behavior before declaring a batch ready.

## Reusable repair rules learned so far

Apply these as starting points, not blind global substitutions. For each
new layout, verify the repair against its source and Google render. Use a
local render as diagnostic evidence when available, and test the repair on
another example before using it across a batch.

| Failure family | Repeatable approach | Evidence and limits |
| --- | --- | --- |
| A short editable label wraps or clips | Inspect the label's font, shape width, and internal margins. Remove excessive left/right insets first; if needed, reduce only that label's font. Preserve the existing family, weight, color, alignment, and editable text. Do not shrink the whole slide or use auto-fit as a substitute for measured geometry. | On slide 154, the 46 pt `CFG` label wrapped in the source PDF and both Linux and Google imports. Reducing it to 24 pt alone still wrapped; setting its 90,000-EMU side insets to zero let 24 pt fit in both Linux and Google. This shows why insets should be checked before making text much smaller. The setting is local to this text box; other fonts and layouts need their own check. |
| A label splits inside a word even though the original font is available in Google | Check the source geometry, side insets, and wrapping mode before changing font size. Disable wrapping for a short one-line label and remove only unnecessary side insets; reduce font size only if those changes still do not fit. | In Round 11, slides 115–116 kept their original 46 pt Bebas Neue CFG labels and 20 pt branch labels. Disabling wrapping and clearing side insets fixed the splits. This followed Round 10, where its different label still needed a size reduction after the insets were removed. |
| A local LibreOffice render disagrees with Google on font width | Check which font each renderer actually used with `pdffonts` and Fontconfig. Treat LibreOffice as an optional diagnostic; use the Google-generated PDF for acceptance and compare it with the source reference. | In Round 11 rev1, local Fontconfig resolved Bebas Neue to wider DejaVu Sans while the Google PDF embedded Bebas Neue. Shrinking labels to compensate for the local substitution would have damaged the Google result. |
| A relationship symbol overlaps a box or label | Give each relation its own editable symbol in the open space between the related boxes. Preserve the direction, hierarchy, and association; verify every branch and row, not just one example. | Slides 155–156 now use editable `⊆` text boxes placed in the gaps. Their labels, outlines, and symbols survived the Google roundtrip. The positions are specific to these diagrams. |
| A full-page preview appears to omit or hide an object | Check the page at presentation size and crop the relevant region before diagnosing loss. Cross-check extracted PDF text and native object readback. A small or scaled preview alone is insufficient evidence that a diagram or border is absent. | The initial Round 10 full-page preview made the slide 155 diagram look absent. A crop and text extraction confirmed all boxes and labels were present in the Google PDF. |
| A Google repair is visually correct but editability is uncertain | Read back native object types and representative text. For a claim that an object can be edited, separately make one reversible edit on a disposable copy and read it back. | Native text replacement and readback passed on a disposable Round 10 copy and on the requested Round 4 deck. A line-position change and restoration passed on a disposable Round 11 copy; the corresponding line-style update was rejected. See the [text edit record](GOOGLE_DRIVE_ACCESS.md#verified-live-text-edits) and [vector edit record](GOOGLE_DRIVE_ACCESS.md#verified-native-vector-object-edit). |
| A diagram is intrinsically visual or survives no reliable native repair | First try rebuilding the affected lines, labels, or symbols as native editable objects. If that still fails, rasterize only the smallest meaning-bearing region and retain nearby text and labels as editable objects. | Rounds 8–10 recovered arrows and relation labels as native shapes/text. No whole-slide raster fallback was needed in these rounds. |

For scale, group slides by recurring failure family and source layout, then
apply the verified repair by a structural selector such as text, font,
geometry, or relationships. Keep fixed shape IDs in pilot scripts as
diagnostic examples, not as a collection-wide mapping. Review edge cases and
controls after each family-level pass.

## Preserve meaningful animation builds

Static PDF export and image-based conversion flatten Keynote animation
builds. For an instructional reveal, inspect the source build order and notes,
then represent each meaningful teaching state as a separate static slide in
that order. Do not create a page for a purely decorative transition that
does not change the information students need to see. Map each output slide
to its source deck, source slide, and build state; keep the generated sequence
inside that source deck and topic. The output count may exceed the 2,235 input
slides. Verify the sequence and its neighboring slides in Google Slides.

The verified example on combined slides 205–206 is already documented below.
The latest Keynote export and Round 4 Google PDF show the first comic panel,
then the complete comic. Do not spend another round on this sequence; find a
different meaningful animation family during source reconciliation.

## Pick the source and define the scope

1. Confirm which offering and slide range the user wants. This pilot is
   from the 2,235-slide collection built around the Spring 2026 sequence.
   The Fall 2026 study guide in `out/` is a separate artifact. For a Fall
   conversion, read `origin/fall+2026` and use the Fall lecture PDFs to check
   which Keynote revisions match.
2. Use [sources.csv](sources.csv) and [sources.json](sources.json) to map a
   slide in the combined collection to its source deck. Use the combined
   PDF as the current visual baseline. If the baseline itself has a defect
   or differs from an original native export, consult the exact source
   slide and record the difference. Keep slide order and exclude slides
   marked skipped. Speaker notes can explain intended builds or overlays.
   For repeated topics, use the newest available source as authoritative.
   Retain older material only when its useful content is absent from the
   newer version, and record its source/version and reason for inclusion.
   Use the current syllabus and source dates to place unique older material
   with the topic it supports; never keep a superseded duplicate just to
   preserve an older deck's wording.
3. Preserve the original files. Write new tests to
   `out/combined/google-slides-pilot/`. Keep the source reference, input
   PowerPoint, local PDF, Google PDF, and page map separately identifiable.
   Apply widely recurring repairs to import batches only after a Google
   roundtrip confirms the behavior.

## Prepare a reproducible pilot on Linux

Use Poppler for PDF inspection. A LibreOffice Impress render is optional
local diagnostic evidence, not the acceptance render; compare the Google PDF
with the source reference. Check the fonts embedded by each renderer before
attributing a wrapping difference to the imported deck. The pilot scripts
use Python with Pillow, lxml, and pikepdf.
Recovering clipped pictures in Rounds 5–7 also uses `pdftocairo`.
The versioned PPTX, source page map, and paired PDFs are the durable
record. Use a temporary directory for rendered images and raw connector
responses.

Select pages that expose the specific failures you are trying to repair.
Include a control from the same source deck and, when verifying a reusable
repair, a matching symptom from another lecture or layout. Include adjacent
builds when a slide changes the set of displayed edges, labels, or examples.
Save a one-based map from pilot page to combined slide and record each page's
role as a repair or control. For the existing pilots, the rebuild scripts and
roundtrip entries already provide the mapping.

This example rebuilds Round 7 in temporary storage and optionally renders its
PPTX with a separate LibreOffice profile. Run from the repository root.

```sh
pilot_stage=$(mktemp -d "${TMPDIR:-/tmp}/cs408-pilot.XXXXXX")
python3 out/combined/google-slides-pilot/rebuild_conversion_pilots.py 7 \
  --output "$pilot_stage/round7-rebuilt.pptx"
python3 -m zipfile -t "$pilot_stage/round7-rebuilt.pptx"
libreoffice --headless --convert-to pdf \
  "-env:UserInstallation=file://$pilot_stage/lo" \
  --outdir "$pilot_stage" "$pilot_stage/round7-rebuilt.pptx"
pdfinfo "$pilot_stage/round7-rebuilt.pdf"
```

The original Round 7 build has 11 pages on a 4:3 canvas. The record below
gives the exact order. Treat a LibreOffice PDF as optional local diagnostics;
the Google PDF is the import acceptance render. If LibreOffice fails to start in the Codex sandbox,
request approval for the headless PDF render. The existing reusable
approval in this environment uses the prefix
`libreoffice --headless --convert-to pdf`. Give Keynote-to-PowerPoint
conversion its own approval if the environment requires one.

When developing a new repair, keep the selected slide list, input deck
revision, and output filenames with the repair script or the written
procedure. Render the new PPTX locally and inspect the intended changes
before sending it to the shared folder.

## Produce an editable PowerPoint on Linux

1. Use a matching editable Keynote source when available. Export with
   LibreOffice Impress on Linux, or use a native Keynote PowerPoint export
   supplied by the user. A Keynote deck can be exported in Impress with
   `libreoffice --headless --convert-to pptx --outdir <stage> <input.key>`.
   Use a temporary profile and output directory to avoid disturbing any
   LibreOffice session. Compare against the corresponding reference PDF.
   Google Slides import and its PDF determine acceptance; a local render is
   diagnostic and may substitute fonts unavailable on Linux.
   Keep existing good slide XML and assets when a tested editable package
   is available.
2. Keep editable text in text boxes with explicit sizes, paragraph breaks,
   and room for the longest line. Preserve bold, italics, links, and code
   formatting where they carry meaning. Google used Bebas Neue,
   Roboto Condensed, Source Sans 3, Arial, Roboto Mono, and Source Code Pro in
   this pilot. Keep those families when they fit the original. Local
   Fontconfig fallback is a different rendering path. Avoid changing fonts
   across the course based on a Linux-only discrepancy.
3. Use explicit geometry for images. If an implicit background fill changes
   the crop, crop the source photo to the reference framing and insert it as
   a full-slide picture. Keep titles and captions as editable objects above
   it. Avoid applying a new crop to every image. The first cover stretched in
   Google while other photos rendered acceptably.
4. Inspect clipped or overlapping text in presentation view. Replace
   duplicated content from earlier builds with one readable layout. For
   tight boxes, prefer explicit line breaks, a fixed font size, and padding
   over relying on auto-fit. Remove old template shapes only after matching
   them to the visual source and confirming that they are decorative ghosts.
   Keep a record of substantive rewrites.
5. Check arrows against the reference and the lecture semantics. Replace
   drifting imported curves with simple editable lines and arrowheads when
   feasible. Trace each source and destination node. Keep labels editable.
   Record which edges are present in each build, including entry edges,
   loopbacks, and insets. Round 4's lines are independently editable.
   If you move a node, reposition the segments that meet it.
   Treat raster conversion as a last resort. First try rebuilding the
   object in editable form and verify the result in a Google roundtrip.
   If that still fails, rasterize only the smallest affected object and
   keep its surrounding labels and text editable. Use a whole-slide image
   only when the source is a PDF without an editable original, or when
   object-level repair has failed and a whole-slide image is the only
   reliable way to preserve the content. Record the slide, failed
   approaches, and reason for the exception.
6. Maintain one notes master per PowerPoint. Repoint notes slide relationships
   to that master and retain the notes slide XML and notes text. Check
   `ppt/presentation.xml`, its relationships, and every notes slide
   relationship. When splitting a package, preserve the presentation's
   ordered slide list and copy the slide layouts, slide masters, media,
   themes, and notes each selected slide needs. Run a ZIP integrity check,
   parse the XML, and verify all internal relationship targets and slide
   counts.
7. Keep each **original source deck** and each **topic** whole. A batch cut
   is allowed only where a source deck ends and a topic ends. If one topic
   spans several adjacent source decks, keep all of those decks together. If
   one source deck spans multiple topics, keep the deck intact and combine
   those topics with adjacent material as needed. Never split either unit to
   make batches equal or satisfy a guessed size limit. Use the previous
   offering's syllabus and schedule only to guide week groupings after these
   boundaries are established. For meaningful animation builds, map each
   generated slide to its source slide and build state, and keep the whole
   sequence in the same deck/topic group; output count may grow. The existing
   [editable batch manifest](editable-parts-manifest.json) covers all 2,235
   slides in nine files of at most 275 slides and under the Google Slides
   100 MB conversion limit. The batch packages were checked locally, and
   their boundaries align with complete source decks. They are baseline
   packaging units; check topic spans before reusing them as final upload
   blocks. Batch 3 rendered all 275 slides in Impress. A pilot import does
   not establish that the full deck or each batch will import.

### Repair by symptom

| Symptom | What to inspect | Repair and evidence |
| --- | --- | --- |
| Image missing, stretched, or obscuring text | Check the original clip and transformation, the PPTX picture relationship, and the layer order in the shape tree. | Put the original image back at the intended crop. For an irregular clip, isolate the source PDF image draw and graphics state, recover it with transparency, and insert the cropped picture separately. Keep the title and callouts editable above it. Rounds 4 and 5 verify both kinds of recovery. |
| Code or dense text fits in Linux but clips in Google | Inspect the last visible token, long-line wrap, and border in the Google PDF. Compare the extracted code and symbols with the exact source. | Start with a wider or taller box and sufficient padding. Adjust paragraph spacing while preserving font size where possible. Round 7 verified 27–39 points of bottom clearance for six repaired code boxes on the 1,024 × 768 canvas. Measure the margin for each new layout. |
| A short editable label wraps or clips | Check the source geometry, intended wrapping, font availability, and side insets. | If a single line is intended, disable wrapping and remove unnecessary horizontal insets first. Reduce the font only if it still does not fit. Round 11 retained original fonts on slides 115–116 with this method; Round 10's slide 154 needed 24 pt after its 90,000-EMU insets were removed. Google PDF is the acceptance render; LibreOffice may substitute fonts. |
| An arrow drifts, points backwards, or crosses another node | Use the reference, adjacent builds, and the code or definitions to identify each direction and endpoint. | Replace malformed paths with native lines and arrowheads. Reserve space for editable branch labels. Check the presence of entry and return edges on each build. Slides 136 and 147 show how a similar layout can require different topology. |
| A subset or containment symbol covers a box label | Map every symbol to the relation it expresses and inspect all branches. | Move or rebuild each symbol as its own editable object in the gap between related boxes. Verify relation direction and visible spacing on every branch. Round 10 tests this on slides 155–156. |
| List markers wrap or a divider crosses the first row | Inspect the text run, list-marker style, row heights, and underline geometry. | For path identifiers referenced elsewhere on a slide, use dedicated editable label and value positions. Preserve the meaning-bearing path color and keep the rule above the first row. Round 6 verifies this across slides 173–175. |
| Raster and extracted-text checks disagree | Check the image crop, shape stacking, and exact frame boundaries. | Inspect the render and determine whether the content is an intrinsic screenshot, hidden by another shape, or clipped. Use native object readback for structure and a separate edit test for behavior. |
| A detail looks missing in a scaled preview | Inspect the actual Google PDF at presentation size, with a crop around the detail. | Cross-check PDF text and native structure before treating it as lost. Round 10's slide 155 diagram looked absent in a downscaled full-page view but was present in the PDF crop and text extraction. |

## Run and evaluate a Google roundtrip

Use the [paced Google Drive workflow](GOOGLE_DRIVE_ACCESS.md#run-a-low-volume-connector-roundtrip)
to import and export small pilots from Codex. The connector transfers the
deck and Google-rendered PDF. Run the visual and text checks below
regardless of how the PDF arrives.

1. Use a small representative deck covering photos, title wrapping, dense
   body text, code, formulas, arrows, and at least one PDF image slide.
   Export it locally first. Compare that render with the reference to
   identify defects that predate Google.
2. Use the [connector workflow](GOOGLE_DRIVE_ACCESS.md#run-a-low-volume-connector-roundtrip)
   or [browser upload](GOOGLE_DRIVE_ACCESS.md#upload-or-export-in-the-browser).
   Save a separate native deck and Google PDF for each revision. In a
   disposable copy, [test a direct edit](GOOGLE_DRIVE_ACCESS.md#verified-live-text-edits)
   when authorized. Check a title, an editable code line, or a diagram
   object and record the result separately from the PDF audit.
3. Run `pdfinfo <export.pdf>` to check the creator, page count, and canvas.
   Use `pdftotext -layout <export.pdf> -` to locate title anchors or compare
   code and symbols, `pdffonts <export.pdf>` to check embedded fonts, and
   `pdftoppm -scale-to 1024 -png <export.pdf> <stage>/google` to render
   comparison images. Do the same for the reference and the Linux render.
4. Match pages with titles and images before comparing them. Record any
   extra, skipped, reordered, or manually added pages explicitly. Normalize
   the canvas for comparisons while keeping its aspect ratio. Center a 16:9
   reference image on a 4:3 canvas if the PPTX did the same. Image-only
   slides have visual content even when PDF text extraction is empty.
5. Review three images side by side for any flagged page. Verify that
   photos maintain their intended framing, all meaningful words and
   symbols are visible, and arrows end at the right nodes. Extracted text
   can include material hidden behind other shapes and text clipped by the
   slide edge. At presentation size, check the last line, punctuation,
   numbered and lettered labels, and where separators cross lists. Labels
   cited in prose need enough size and contrast to find the matching item.
   Pixel differences can flag pages for review. Similar-looking sequential
   builds need a slide-list and title or content check to confirm order.
   Record the defect, its cause if known, what changed, and whether Google
   verified the fix. After a successful roundtrip, compare every affected
   slide in the first real batch before resuming broader conversion.
6. Compare with the previous Google PDF at the same raster size. Derive the
   planned change set from the ordered PPTX slide XML and from any shared
   images, layouts, or other parts that changed. Render both Google PDFs
   with the same Poppler settings and compare decoded RGB pixels on matched
   pages. Inspect each expected change and investigate any changes on
   untouched pages. Round 4 used `pdftoppm -scale-to 480 -png` for the
   full scan and larger crops for arrow tips, small labels, and clipped code.
   Use the per-slide source flags in `sources.json` when a defect appears
   in the combined reference, too.

### Compare the same slide in all three PDFs

Round 7 pilot page 4 corresponds to combined slide 107. Use the exact
pilot map the same way for each page you review. The commands below
render the source, local conversion, and Google result at one scale.
They also create Google text and bounding-box outputs for the same page.

```sh
pilot_review=$(mktemp -d "${TMPDIR:-/tmp}/cs408-review.XXXXXX")
pilot_prefix=out/combined/google-slides-pilot/cs408-conversion-pilot-round7
pdfinfo "$pilot_prefix-google.pdf"
pdftoppm -f 107 -l 107 -scale-to 1024 -png \
  out/combined/cs408-all-slides.pdf "$pilot_review/source"
pdftoppm -f 4 -l 4 -scale-to 1024 -png \
  "$pilot_prefix-linux.pdf" "$pilot_review/linux"
pdftoppm -f 4 -l 4 -scale-to 1024 -png \
  "$pilot_prefix-google.pdf" "$pilot_review/google"
pdftotext -f 4 -l 4 -layout "$pilot_prefix-google.pdf" "$pilot_review/google.txt"
pdftotext -f 4 -l 4 -bbox "$pilot_prefix-google.pdf" "$pilot_review/google-bbox.html"
```

Use the image comparison for cropping, overlap, contrast, and arrow
endpoints. Use extracted text for code, formulas, and missing labels.
For a suspected clipped last line, locate its last token in the same code
box and compare its bounding-box `yMax` to the frame's lower edge in PDF
points. Confirm the result visually. Compare the control with its previous
Google export at the same scale. Round 7 compared decoded RGB pixels
at a width of 480 pixels for its five controls.

### Record whether the round passed

- **Structure.** The input PPTX opens, its internal relationship targets
  resolve, the selected pages are in order, and the native deck and both
  PDFs have the expected mapped pages. Check the expected canvas or
  documented aspect-ratio treatment.
- **Fidelity.** The intended repair is visible, the slide teaches the
  same content and relationships as its source, and differences on
  controls are explained. Review each small pilot page at presentation
  size and zoom in on dense code and small diagram labels.
- **Editability.** Record separate native object types from structural
  readback. Record a live edit and its readback as a separate check.
  Document any image fallback and the source object it replaced.
- **Handoff.** In the next log entry record the local input and export
  links, native deck URL, page map, tested method, concrete results, and
  remaining defects. If a stage is blocked, record the last successful
  stage and the actual failure. Update the summary and open-work sections
  after the audit.

### Automate the repeatable local checks

Run the [pilot audit script](google-slides-pilot/audit_conversion_pilot.py)
after the local and Google PDFs are saved. It does not call Drive. It checks
PPTX ZIP integrity and internal relationship targets, verifies that the
page map matches the native presentation order, confirms control slide XML
is byte-identical to the baseline, reports changed slide parts, validates
PDF page counts, checks requested extracted text, and can compare mapped
control pages pixel for pixel at a chosen DPI. It checks controls and text;
manually inspect every repaired page at presentation size.

The Round 10 invocation was:

```sh
python3 out/combined/google-slides-pilot/audit_conversion_pilot.py \
  --baseline-pptx out/combined/google-slides-pilot/cs408-editable-part-01-round4.pptx \
  --pilot-pptx out/combined/google-slides-pilot/cs408-conversion-pilot-round10-rev6.pptx \
  --map out/combined/google-slides-pilot/cs408-conversion-pilot-round10-rev6-map.csv \
  --linux-pdf out/combined/google-slides-pilot/cs408-conversion-pilot-round10-rev6-linux.pdf \
  --google-pdf out/combined/google-slides-pilot/cs408-conversion-pilot-round10-rev6-google.pdf \
  --baseline-google-pdf out/combined/google-slides-pilot/cs408-editable-part-01-round4.pdf \
  --dpi 120 \
  --expect-text "1:Game Plan" \
  --expect-text "2:CFG" \
  --expect-text "3:Edge-Pair Coverage" \
  --expect-text "4:Simple Round Trip Coverage"
```

The script requires Python, Pillow, and Poppler's `pdfinfo`, `pdftotext`,
and `pdftoppm`; package and XML checks use Python's standard library. A
successful audit reduces repeated mechanical work but does not certify visual
quality or live object editability by itself.

## Integrate verified repairs into a full batch

Start from the latest full-batch PPTX. For Part 1 that is
[Round 4](google-slides-pilot/cs408-editable-part-01-round4.pptx).
The Part 1 candidate with the merged work from Rounds 5–11 is still open.
Use the newest verified change to each slide. Later control pages
confirm earlier repairs. The table lists where each repair last changed.

| Version to carry forward | Combined slides |
| --- | --- |
| Round 5 | 19, 36, 230, 232, 251 |
| Round 6 | 73, 136, 147, 173–175 |
| Round 7 | 103, 107, 121, 134–135, 253 |
| Round 8 | 77–78 |
| Round 9 | 99–102 |
| Round 10 | 154–156 (153 is an unchanged control) |
| Round 11 | 115–116 (114 is an unchanged control) |

Apply the repair functions to the matching slides in the full package
or copy only the necessary slide edits and related assets. Reuse the
full presentation's ordered slide list and keep its notes and layouts.
For added media, update the target slide's relationships and package
content types. Verify that every relationship still resolves. Copying a
standalone pilot's presentation part would substitute its shorter slide
order for the full batch.

Round 8 adds no media or package relationships. For its two slides, the
current pilot's repaired parts are `ppt/slides/d02_slide64.xml` and
`ppt/slides/d02_slide65.xml`. Preserve the full batch's presentation order,
notes, and other relationships when carrying them forward.

Round 9 adds no media or package relationships. Its repaired source parts
are `ppt/slides/d03_slide29.xml`, `d03_slide31.xml`, `d03_slide33.xml`, and
`d03_slide44.xml`. Their CFG arrow shafts and heads remain separate native
freeforms. Slides 100–102 store diagram elements in groups; when editing a
grouped slide, preserve its group transform and insert a new head beside its
shaft within that same group. The Round 9 controls, 98 and 104, are byte
identical to the Round 4 baseline. Round 10 changes only slides 154–156;
slide 153 remains unchanged and its Google render matches the Round 4 PDF
pixel for pixel at 120 dpi. Round 11 changes only slides 115–116; slide 114's
XML is unchanged and its Google render matches the Round 4 PDF pixel for
pixel at 120 dpi. If animation states are expanded during integration,
update the slide list and page map while keeping the source deck and topic
whole.

Render the assembled candidate locally and check the change set against
the verified fixes. Import it as a new native deck, verify the full count
and page order, and compare one Google PDF with the prior full-batch
export. Inspect every changed slide in the full-size context. Switch to
the new baseline after that audit and carry forward any remaining
issues. Apply the same process to the other batches and establish each
batch's own reference and regression controls.

## Scale the conversion across all 2,235 slides

Do not move from a successful pilot directly to one large upload. First
reconcile source versions, then finish family-level pilots against the
selected sources. Integrate and verify the Part 1 candidate afterward; its
slide count may grow if meaningful build states are expanded. For the
collection, use topic-aligned blocks and keep every
slide in original order:

1. Reconcile the Spring-centered 2,235-slide set topic by topic against the
   Fall 2026 material and any other newer source. Select the newest version
   for each topic; retain older items only when they contain useful content
   absent from newer sources, and record why. Then build an ordered inventory
   from the source map, recording each original source deck's complete slide
   range and topic tags before grouping.
2. Mark permissible cuts only where both conditions hold: the preceding
   original deck is complete, and the preceding topic is complete. When a
   topic spans adjacent decks, keep that run together. When a deck spans
   several topics, keep all of them together and group adjacent topic runs
   around it. Preserve the current collection order; do not move slides to
   manufacture cleaner or equal-sized blocks.
3. Partition those ordered, indivisible groups into four contiguous blocks
   as the first packaging assessment. Do not target 559 slides per block.
   Balance sizes only among the permissible cuts, considering actual PPTX
   bytes, slide count, topic sequence, and validation effort.
4. If measured import size or review effort calls for more divisions, assess
   eight and then up to sixteen blocks. Add a cut only at another permissible
   deck-and-topic boundary. The block count is a capacity choice, not a
   requirement to divide slides or topics evenly. If a single indivisible
   group exceeds a limit, investigate a different import, export, or storage
   path before changing its boundaries.
5. At sixteen blocks, use the previous course's syllabus, lecture order, and
   homework timing to estimate roughly one class week per block. Treat weeks
   as a planning aid: a topic that crosses an estimated week stays whole.
   Place a syllabus, homework, or supplemental item beside the topic it
   supports when the current source order allows it, without splitting a
   source deck or moving material out of order.
6. Make a block manifest with its exact slide range, complete source deck
   IDs, lecture/topic labels, estimated week where useful, PPTX size, slide
   count, and associated homework or syllabus items. The manifest should
   make it possible to verify mechanically that no source deck was divided;
   record the topic-boundary rationale for each cut. Preserve one-based
   combined-slide numbers and exact order in every page map.
7. Verify ZIP integrity, internal relationships, notes, page count, page
   order, and the imported native deck before accepting a block. Export and
   inspect its Google PDF before uploading the next one. For PDFs above the
   standard export limit, use the Drive streaming fetch or authenticated
   browser download. If size still requires smaller units, use up to 16
   ordered blocks at whole source-deck/topic boundaries. Never use a shell
   downloader or split a deck/topic to meet a byte target.

Block sizes are expected to vary. Complete original decks and topics, source
order, and verifiable imports matter more than equal counts. Do not exceed
sixteen blocks without rechecking size and review assumptions with the user.

## Roundtrip log

### Round 1 — checked

The [Google export](google-slides-pilot/cs408-editable-pilot.pdf) contains
17 pages. Original pilot slides 1–3 map directly to Google pages 1–3. Page 4
is the user-added slide. Pilot slides 4–16 map to Google pages 5–17. All 16
originals were found in order. Use the [slide map](google-slides-pilot/slide-map.csv),
[reference PDF](google-slides-pilot/cs408-pilot-reference.pdf), and
[Linux render](google-slides-pilot/cs408-pilot-linux.pdf).

| Pilot slide | Round 1 Google page | Finding |
| --- | ---: | --- |
| 1 | 1 | Google used the requested fonts, but stretched the implicit photo background instead of following the reference crop. The title became smaller and went from two lines to one. |
| 2–3 | 2–3 | Duplicate objectives and part of the coverage title already overlap or clip in the source-derived reference and also do so in Google. |
| 4–6 | 5–7 | The prime-path figures have misplaced arrows. Page 5 also makes the angled callout visible outside its box. The happens-before example overlaps the explanatory text in both the baseline and Google. |
| 7–8 | 8–9 | Google uses the intended headline font, but the layout changes. The bug report slide's last caption line is pushed to the bottom edge and its ending is missing from PDF text extraction. |
| 9–11 | 10–12 | The logic lattice's symbols, symbolic-execution photo slide, and symbolic-execution code survive. The existing flow-graph connectors on slide 11 warrant visual review when that lecture is converted. |
| 12–14 | 13–15 | Google splits the two “information” headings across lines and makes the SMT callout nearly illegible. The sign lattice and path-sensitivity example also have overlaps already visible in the reference. |
| 15–16 | 16–17 | The verification slide reflows but stays legible. The widescreen tutorial is centered and remains an image. |

### Round 2 — checked

The [revised pilot](google-slides-pilot/cs408-editable-pilot-round2.pptx)
produced this [Google export](google-slides-pilot/cs408-pilot-round2-linux_download.pdf).
The PDF reports Google as its creator and identifies the revised pilot in
its title. It has 16 pages in the original pilot order on a 1,024 × 768-point
canvas. The Round 1 user-added page is absent, so Round 2 page numbers match
the [pilot slide map](google-slides-pilot/slide-map.csv) directly.

This pilot makes 11 targeted changes. It crops the course photo explicitly
and separates its editable title, rebuilds the overlapping objectives as a
readable grid, moves the coverage title clear of the stripe, and redraws the
two prime-path diagrams with native shapes. It sets aside a column for the
happens-before definition, removes old titles behind photos on slides 7–8,
and fixes the caption boundaries. It also widens the data structure labels
and the SMT callout, rebuilds the sign lattice, and removes an unrelated
overlapping code box from the path-sensitivity example.

| Pilot slide | Result in the second Google export |
| --- | --- |
| 1–3 | The explicit photo crop holds, the two-line title fits, and the objectives and coverage title are fully visible. |
| 4–5 | The rebuilt arrowheads visibly land on the intended graph nodes. The observation and pseudocode stay inside their boxes. |
| 6 | The definition and the thread boxes are readable. The bottom program box loses its final numbered ellipsis because Google wraps its opening comment. Both thread-start calls remain visible. |
| 7–8 | The headlines fit and the bug report caption is fully visible, including “What’s a dev to do?” |
| 12–13 | Both information headings and the full SMT query and model fit. The sign lattice no longer overlaps its surrounding labels. |
| 14 | The unrelated code overlay is gone. Google wraps the method signature and puts the last brace slightly below the code box. All code and the explanation are visible. |
| 9–11, 15–16 | The five untouched slides render pixel-for-pixel the same as Round 1 at the same raster size. Slide 11 still has the pre-existing misrouted symbolic-execution graph arrows. |

[Round 3](#round-3--batch-import-passed-other-slides-still-need-repair)
carried Round 2's crop, text layout, and native arrow approach into a test
copy of [editable Part 1](cs408-editable-part-01.pptx), on
combined slides 1, 14, 84, 158, 161, and 243. The bottom program box on
243 was expanded to fit five lines even when the comment wraps.

When converting the later batches, rebuild the symbolic graph on combined
slide 705 from the code, with L2 leading to C3, C3 branching to C4 and C10,
and each branch reaching its matching return. Give the code box on
combined slide 982 enough width for the method signature and enough
height for its final brace. Include both in their respective batch checks.
This result verifies the visual rendering of the pilot. The
[Round 4 procedure](#round-4--checked) lists the live editability checks
still to run.

The revised deck passed the ZIP, slide order, media, and speaker-note
checks and rendered all 16 slides in
[LibreOffice](google-slides-pilot/cs408-pilot-round2-linux.pdf). For an exact
rebuild from the first pilot, run this from the repository root with
Python, Pillow, and lxml available:

```sh
python3 out/combined/google-slides-pilot/rebuild_round2.py \
  --output out/combined/google-slides-pilot/round2-rebuilt.pptx
```

The rebuild script is specific to the 16-slide pilot and its original shape
IDs. Use the procedure above to identify equivalent shapes in the full
collection.

### Round 3 — batch import passed, other slides still need repair

The [Google export](google-slides-pilot/cs408-editable-part-01-round3.pdf)
matches the title of the [Part 1 test deck](google-slides-pilot/cs408-editable-part-01-round3.pptx).
It has 260 pages on a 1,024 × 768-point canvas. PDF integrity checks passed.
Page-by-page thumbnail matching against the
[Linux render](google-slides-pilot/cs408-part-01-round3-linux.pdf) and the
seven lecture boundaries found no omitted or reordered pages. Here, a
page number is also its one-based slide number in the combined collection.

Compared at the same raster size, Google pages 1, 14, 84, 158, and 161
match their Round 2 counterparts pixel for pixel. On page 243 both
thread-start calls and the final numbered ellipsis are visible in Google,
which verifies the five-line code box repair. The cover photograph
remains its own picture, and the new text, code, and graph elements in
the PowerPoint are separate objects. The PDF check verifies appearance.
Live Google editing still needs to be tested on a title, a code line,
and a diagram element.

All 260 pages were rendered and scanned. The following are representative
defects found at the end of Round 3 outside the six repaired examples.
Use the [current open-work list](#open-work-after-round-11) for
remaining Part 1 work.

| Slide(s) | Finding | Repair to try |
| --- | --- | --- |
| 24 | The outage article screenshot from the reference is missing. The PPTX slide `ppt/slides/d01_slide33.xml` has an empty shape tree, and both exports are white. This loss happened before Google. | Recover the screenshot's 884 × 723 image and soft mask from the reference PDF or recover the original asset. Insert it as a selectable picture at the source position. The source slide already used an image. |
| 16–17 | Requirements, Design, and Deployment point at the same montage image in the PPTX. The reference uses individual illustrations. Labels also break mid-word. | Restore the separate illustrations from source and fit the labels as native text. Check the build on slide 17 separately. |
| 69–73, 77–78 | Examples include split labels, code and text collisions, and arrows crossing the RIPR and scientific method diagrams. The most serious arrow drift is visible in both Linux and Google. | Match intended endpoints to the reference, rebuild paths with native edges, and give adjacent labels explicit space. |
| 99–107, 115–125, 127–145, 157–181 | Broken CFG and prime-path arrows recur on slides and builds outside the repaired examples. Pages 158 and 161 demonstrate the fixes. Representative failures are 99, 102, 104, 124, 137, 160, and 162. | Reuse validated native node and edge templates across matching graph families. Verify each build's graph, branch labels, and semantics independently. |
| 134–147, 155–156 | Subset symbols land inside coverage boxes on examples including slides 134 and 146, obscuring their relationships. | Give each relation its own native text box between the nodes and verify the sequence against the source. |
| 149, 233 | The photo covers the title on 149. The lock-set photo obscures the title and lecture content on 233. In the PPTX the relevant picture follows the text in each shape tree. | Move the photo behind the editable content, preserve its crop, then check fit and contrast. |
| 230, 232, 242, 244 | The dynamic-analysis diagram is distorted on 230, the labels collide on 232, and the adjacent happens-before builds still overlap on 242 and 244. | Restore the intended picture layers, rebuild diagram arrows as native lines, and adapt slide 243's separate text column to the other builds. |

Five Google pages had no extractable text. Four still show imagery
(21, 25, 205, and 206); slide 24 is the only blank render. Slide 205 shows
only the opening panel while 206 shows the complete comic. Check the
intended reveal against the Keynote source before filling early builds.
Slide 6's empty grading table also appears in the source. These examples
show why a missing text extraction or visual difference alone is not a
defect.

**Batch decision:** The six targeted repairs survive a full-size import.
Part 1 still needs a source-aware repair pass before it is ready to use as
the edited course deck. Prioritize missing or obscured content and wrong
graph edges. Prefer native text, pictures, shapes, and arrows. Use raster
fallback only for individual elements that cannot be restored reliably.

### Round 4 — checked

The [Google export](google-slides-pilot/cs408-editable-part-01-round4.pdf)
reports Google as its creator and matches the title of the
[Round 4 PPTX](google-slides-pilot/cs408-editable-part-01-round4.pptx). It
passed a PDF syntax check and contains all 260 pages in order on a
1,024 × 768-point canvas. Page numbers match combined slide numbers. The
260-page [Linux render](google-slides-pilot/cs408-part-01-round4-linux.pdf)
and the [combined reference](cs408-all-slides.pdf) were used to review
each edited slide and selected defects elsewhere in the batch.

Compared with the Round 3 Google PDF at the same 480-pixel width, exactly
the 47 pages edited in the PPTX changed. The other 213 match pixel for
pixel, including the six Round 3 fixes on 1, 14, 84, 158, 161, and 243.
Slides 21, 24, 25, 205, and 206 have no extractable text. All five show
images, including the recovered screenshot on 24. There are no blank
renders.

The PDF embeds Bebas Neue, Roboto Condensed, Source Sans 3, Arial, Roboto
Mono, Source Code Pro, and other fonts. On 202–203, the check and cross
marks missing in the Linux render are visible in Google. Use the Google
render to decide where glyphs actually need replacement.

| Slide(s) | Verified in the Google PDF | Follow-up |
| --- | --- | --- |
| 16–17, 24 | Separate illustration crops and four one-line labels survived. The four green checks rebuilt as native shapes on 16 are visible. The central overlay on 17 covers the same middle illustrations as the reference. Page 24 shows the original outage article. | Reuse the original picture object, its crop, and its soft mask where present. On 24 the original slide content was a standalone 884 × 723 screenshot. |
| 69 | Testing and debugging each fit on a single line. | Reuse the fixed-size one-line text approach for short photo labels. |
| 103–106, 108, 127–128, 130–132, 157 | The fork and return loop now reach the intended nodes, including the lower graph on 128. Google shows the arrowheads more clearly than the local render. | On 103 the code and hint still crowd each other, and the last code line is near the slide edge. On 128 the inset and standalone B5 box are visually misaligned with the reachability equations. Lay out each answer beside its own equation and verify the intended reveal for `reach_G(7)`. On 130–132 verify the stray “The first” bullet against the native source. It appears in both renders and is absent from the matching original PDF pages. |
| 134–135, 146–147 | The labels fit and every subset symbol is visible in the gap between its boxes. | On 134–135 the examples still touch the code box, and the final brace drops below its border to the page edge. On 147 the smaller fork graph still has misrouted edges. Preserve that graph's topology when adapting the arrow repair. |
| 137–145, 160, 162–175 | The edge-pair and prime-path graphs show the intended branch directions, including C5 → B6 and the B6 → C5 loopback on builds with that edge. Page 160 preserves the stage without the loopback and shows the full question. All eleven pseudocode builds on 162–172 display the final return inside the code box. | The letter and number markers in the path and algorithm lists are small in presentation view. On 173–175 all a–i markers are present at magnification, but the header divider falls between the first and second paths. Place it above the first path and keep the letter markers and their color-coded references readable. |
| 149, 233 | The full coverage title appears over the photo on 149. The lock-set title and all the bullets on 233 are visible, including the final candidate-locks line. The light panel is behind the body text. | Reuse the photo → contrast panel → editable text order where a background obscures content. |
| 242, 244 | The definition is readable in its own column. The two thread labels fit, both thread-start calls and the final ellipsis are visible, and the code stays inside its boxes. | The long diagonal on 244 still runs through or beside the second event column to the bottom edge. It is also in the local and combined reference renders. Check the intended event endpoints in the Keynote build before redrawing it. |

ZIP and ordered slide XML checks found six new image assets and three
updated slide relationship files. Speaker-note parts are byte-identical
to Round 3. The 47 repairs retained ordinary text, lines, and shapes as
PowerPoint objects. No whole-slide render was introduced. For live
editability, use a disposable copy of the native Google deck and test
editing a label on 16, selecting the screenshot on 24, changing code on
243, and selecting an edge and a node independently on 128 or 173. Undo
the test edits before exporting the next verification PDF.

#### Part 1 repair queue after Round 4

Prioritize missing content and misleading graphs. The following findings
were checked against both the Linux render and the combined reference.
Use the original Keynote slide or matching Apple export when the reference
also contains the problem.

| Slide(s) | Finding and next repair |
| --- | --- |
| 19, 36, 230 | Page 19 lost the Ariane 5 report excerpt. Its PPTX contains the background photo as its only picture, while the matching PDF shows the excerpt over it. Recover the excerpt asset and restore its light backing. On 36 the imported portrait has a white rectangle at the left that obscures the heading. Recover the intended crop or silhouette and place it at the right. On 230 the main image is entirely off-canvas in the PPTX and its arrows cross the slide. Restore the separate images from the original export and rebuild the title, labels, and arrows as editable objects. |
| 70, 73, 77–78 | Separate the crash example from the surrounding bullets on 70. Rebuild the RIPR and scientific-method diagrams on 73 and 77–78 from the original endpoint pairs. Widen the RIPR labels and preserve the different test nodes in the two scientific-method builds. |
| 99–102, 107, 115–121, 123–125 | CFGs have misplaced edges and examples of broken `true`/`false` labels. Trace each branch against the visible code. Reuse geometry for matching series such as 107 and 121 after checking each build. Keep separate entry arrows, terminal nodes, and branch labels. |
| 136, 147, 154–156, 159, 176–182, 186 | Check these remaining coverage diagrams and lattices. In particular 136 and 147 need the fork without the C2 loop. The 176–177 example and 178–179 counterexample differ by the self-loop at node 3. Slides 180–182 share another topology. Give each subset relation its own space on 155–156, 178–179, and 186. Preserve both relation direction and meaning. |
| 232, 238, 251, 253 | Separate the two photo labels on 232, give the figure labels on 238 room and contrast, and keep both words and the caption in frame on 251. On 253 the compiler screenshot lost its rotation and was squashed. Keep its aspect ratio, preserve legibility, and respect the intended overlay on the source code. |
| 2, 10, 13, 15, 18, 39, 48, 50, 60, 194, 202–203, 214, 224–225, 245–246, 256–257 | Review these layout and build examples before publishing Part 1. Issues include clipped footer or callout text, title and body overlays, thread and code box crowding, and labels that wrap at the slide edge. Several problems already appear in the combined reference, including the overlays on 10, 39, 214, and 224–225. Confirm which layers belong to each native build before removing duplicates. |
| 205–206 | **Resolved 2026-11-24.** The combined reference PDF repeats the completed comic, but that PDF does not preserve this Keynote build. The latest Keynote export shows the first panel followed by the complete comic; the Round 4 Google PDF shows the same sequence. Keep the two cropped picture objects as separate static build slides; no repair is needed. Details below. |

#### Animation/build audit: combined slides 205–206

The source map assigns these positions to `06-408st-concurrency.key`
(`visible_indices` 18 and 19); the second is explicitly marked as a Keynote
page in `original_pdf_page_flags`. The paired source PDF is a static export and
shows the completed four-panel comic on both corresponding pages, so it is
not a reliable reference for this reveal.

The latest saved Keynote is dated 2026-02-03 13:22. A Linux LibreOffice
export of that `.key` file is retained temporarily at
`out/.build/06-408st-concurrency.pdf`. Its pages 19–20 show (1) the first
comic panel and (2) the completed four-panel comic. The numbered Keynote
indices and PDF export page numbers differ here; identify the states by
their visible contents, not by assuming those numbers are identical.

The Round 4 Google PDF at pages 205–206 reproduces those two states in the
same order: slide 205 has the first panel, slide 206 has all four panels.
The two PPTX slides use distinct crop/placement settings on the same source
image, so they remain picture objects rather than flattened full-slide
screenshots. The 2,235-page combined reference PDF showing the full comic on
both pages is a known static-PDF limitation, not a Google conversion defect.
This check establishes the rule for this family: when the newest Keynote
contains a staged build, use its visible build sequence and verify it in the
Google PDF; do not collapse the sequence to match a static older PDF.

For asset recovery, the image names below refer to the resource dictionary
on the stated page of the combined PDF. Inspect what the page paints and
its transformation and clipping path. The resource dictionary can include
images from other pages of the same source deck.

- On 19, `/Im21` is the report excerpt and `/Im20` is its shadow. Use
  `/Im21` with its soft mask, and put the editable headline above it.
- On 36, `/Im32` is the background and `/Im33` is the portrait. On 230,
  `/Im4` is the background and `/Im6` is the portrait. Both portrait
  bitmaps include a white background. Recover each silhouette using the
  source clip and keep the resulting picture separate from the text.
- On 253, `/Im13` is the 882 × 414 compiler screenshot. The reference
  tilts it by about 12° and keeps its aspect ratio.

**Batch decision.** Use Round 4 as the next repair baseline. Apply the
validated crop, picture layering, spaced relation labels, and explicit
line-and-arrowhead patterns to matching slides. The Part 1 deck needs
another targeted repair and a Google check before wider rollout. Keep
whole-slide raster fallback as the last resort described above.

Rebuild Round 4 from the Round 3 PPTX and combined reference using Python
with pikepdf, Pillow, and lxml installed.

```sh
python3 out/combined/google-slides-pilot/rebuild_round4.py \
  --output out/combined/google-slides-pilot/round4-rebuilt.pptx
```

The script uses slide-specific shape IDs and PDF image resource names. Use
the verified layouts and topology as examples when repairing other pages.

### Round 5 — recovered pictures and text overlays

Imported the [10-slide PPTX](google-slides-pilot/cs408-conversion-pilot-round5.pptx)
into the shared folder as a [native deck](https://docs.google.com/presentation/d/16Xp_ZVazWG6Al8EPX5HHOHFRS9To2lMwnFN5hVhVYIA/edit).
The [Google PDF](google-slides-pilot/cs408-conversion-pilot-round5-google.pdf)
and [Linux PDF](google-slides-pilot/cs408-conversion-pilot-round5-linux.pdf)
each have 10 pages. In export order the combined slide numbers are
16, 19, 24, 36, 149, 230, 232, 233, 251, 253. All four controls, 16, 24,
149, and 233, match Round 4 pixel for pixel at 480 pixels wide.

| Combined slide | Result in Google |
| --- | --- |
| 19 | The Ariane 5 report excerpt is back at the source crop. The title and headline remain editable text over the separate recovered picture. |
| 36 | The clipped portrait silhouette is restored to its source position. The goal statement and three smaller labels are visible. |
| 230 | Both original pictures are present as separate images. The redesigned title and callouts are native text, and the two arrows lead to their respective explanations. |
| 232 and 251 | Explicit line breaks and contrast panels keep both analysis names and the full monkey caption readable. The underlying pictures and their intrinsic captions keep their crops. |
| 253 | The screenshot keeps its aspect ratio beside the editable Rust code. The last brace crosses the code box's lower border in Google despite fitting in Linux. Round 7 retests it with more vertical reserve. |

For a missing or incorrectly clipped picture, find its `Do` operation in
the reference PDF content stream. Isolate that draw and the graphics-state
operations that place and clip it, render it against transparency, crop to
the alpha bounds, and place that cropped image back at those bounds.
Only the original picture is rasterized by this procedure. Verify it on
both rectangular and freeform clips. Slides 19, 36, and 230 passed.
If an image needs no special clip, keep its original aspect ratio and
use a separate editable box or panel for any overlapping instruction.

### Round 6 — arrows, code layout, and path lists

Imported the [13-slide PPTX](google-slides-pilot/cs408-conversion-pilot-round6.pptx)
into the shared folder as a [native deck](https://docs.google.com/presentation/d/1ktrcDqs0WSbptAOs1zYYloQpyTmSkKovQ-MCzv8e81c/edit).
The [Google PDF](google-slides-pilot/cs408-conversion-pilot-round6-google.pdf)
and [Linux PDF](google-slides-pilot/cs408-conversion-pilot-round6-linux.pdf)
each have 13 pages. In export order the combined slide numbers are
69, 73, 103, 128, 134, 135, 136, 147, 162, 173, 174, 175, 243. All four
controls, 69, 128, 162, and 243, match Round 4 pixel for pixel at 480 pixels
wide. Control 128 preserves its known association issue.

| Combined slide(s) | Result in Google |
| --- | --- |
| 73 | All four RIPR arrows meet the intended shapes and the full labels fit. The skill of recovering edge endpoints transfers from CFGs to a diagram of overlapping sets. |
| 103, 134–135 | Prompts and examples no longer collide with the code. On 103 the final statement still crosses the lower border. On 134–135 the closing brace meets the lower border. Round 7 retests both layouts. |
| 136 and 147 | Both forks have legible arrows. Page 136 has no return edge. Page 147 has B4 → C1, matching its example of a graph with a loop. Counting edges and checking code or examples before reusing a template preserves this difference. |
| 173–175 | Nine editable row labels a–i and all nine paths are readable. The rule above the first row stays clear of the text and the original color keys survive. Read the color from the path's text run. The paragraph's automatic list-marker color may differ. |

Both pilots used an ordered subset of the Round 4 PowerPoint and preserved
all selected slides' package dependencies. The native Slides readback
showed distinct objects for the repaired pictures, code, labels, and arrows.
Use an unchanged slide from the same deck to detect unintended changes in
theme, crop, or text layout when making a subset. These pilots did not
replace the 260-slide baseline.

### Round 7 — code clearance and transfer to a new graph

Imported the [11-slide PPTX](google-slides-pilot/cs408-conversion-pilot-round7.pptx)
into the shared folder as a [native deck](https://docs.google.com/presentation/d/1nqcLTekLf4qHB2GYHv7howOfEEi6wvCcx4TBeKs_JQw/edit).
The [Google PDF](google-slides-pilot/cs408-conversion-pilot-round7-google.pdf)
and [Linux PDF](google-slides-pilot/cs408-conversion-pilot-round7-linux.pdf)
each have 11 pages. In export order the combined slide numbers are
19, 73, 103, 107, 121, 134, 135, 147, 175, 230, 253. Native readback and
PDF content checks confirmed the same order. Five control pages matched
their prior Google render pixel for pixel at 480 pixels wide. Slides 19
and 230 matched Round 5, and 73, 147, and 175 matched Round 6.

| Combined slide(s) | Result in Google |
| --- | --- |
| 103 | The hints remain clear of the code. The code box starts higher, with room above the bottom border for the full print statement and its BB5 label. |
| 107 and 121 | The entry and branch edges reach their target nodes, the true and false labels fit, and both example paths still match the code. The separated body and code layouts work in the first lesson and the later review. |
| 134–135 | The final brace is inside the frame on both builds. The test-case inputs and subset relationships are legible. |
| 253 | The Rust snippet and its final brace fit inside the code frame. The diagnostic keeps its aspect ratio beside it. Screenshot detail remains small at presentation size. |

The six repaired code boxes leave 27–39 points between the last token
and the lower border in the 1,024 × 768-point Google PDF. Reserve room
above and below the code and give long lines enough width. Tuning
paragraph spacing or box geometry can preserve the existing font size.
Check the rendered bottom line and measure its PDF bounding box. Round 5
and Round 6 both showed that a line can be present in extracted text
while crossing its frame. This also applies to a closing brace or a
comment at the end of a line.

To reuse a graph repair, match the endpoints to the source code and test
examples, explicit entry and exit arrows, branch labels, and any
loopback. Check for surrounding paragraphs that change their wrapping
in Linux and in Google. Slides 107 and 121 use the same verified branch
structure with different title and text styling.

#### Open-work snapshot after Round 7 (superseded by Round 8)

This is the queue as it stood before Round 8. Slides 77–78 were repaired in
that round; use the [current open-work list](#open-work-after-round-11) for
remaining work.

- Merge the Google-verified repairs from Rounds 5–7 into a new 260-slide
  Part 1 candidate using the [integration table](#integrate-verified-repairs-into-a-full-batch).
  Recheck a full-size import before applying the rules across the remaining
  batches.
- Resolve the association between the inset, B5 box, and equations on
  slide 128. Check the Keynote build for the intended reveal on 205–206
  and the endpoints of the timeline line on 244.
- Repair diagrams still outside these pilots, including 77–78, 99–102,
  115–120, 123–125, and 176–182. The subset diagrams on 155–156, 178–179,
  and 186 still need their symbols repositioned with the correct
  direction. The [Round 4 repair queue](#part-1-repair-queue-after-round-4)
  also lists remaining layout problems, including 70 and 238.
- Recheck the diagnostic on 253 at projected size. For cases where small
  screenshot details carry the lesson, allow a larger frame or preserve
  the full image with an editable excerpt beside it.
- Test one actual Google Slides edit and read it back on a disposable
  copy. Native readback in these three rounds confirmed the object types.
  The export path for PDFs above the 10 MB standard API limit still
  depends on the session being able to materialize a streamed file.

### Round 8 — scientific-method arrows and text

The [first Round 8 deck](https://docs.google.com/presentation/d/1gs5aMoT0LRHL4I1Hqn0zrBJK_7gunseGQqDEntTna-8/edit)
was a three-slide pilot in order 69, 77, 78. The [page map](google-slides-pilot/cs408-conversion-pilot-round8-map.csv)
identifies slide 69 as a control and slides 77–78 as repairs. The first
[Google PDF](google-slides-pilot/cs408-conversion-pilot-round8-google.pdf)
exposed two Google import differences: some arrowheads on freeform lines
were missing, and text inside the blue sets wrapped at different words and
sat too high.

Revision 2 retained the text, nodes, ellipses, and other shapes as separate
editable objects. It rebuilt the seven arrows on slide 77 and eight on 78
from the matching vector paths in the combined reference PDF. Each shaft
and its filled triangle arrowhead is its own editable freeform. Explicit
text lines and a corrected text-box inset and width keep the labels in the
same positions and lines in Google. The one-line “All Final Program Output
States” label also uses a Google-safe font size and family. No diagram was
flattened to an image.

The corrected [PPTX](google-slides-pilot/cs408-conversion-pilot-round8-rev2.pptx)
and [Linux PDF](google-slides-pilot/cs408-conversion-pilot-round8-rev2-linux.pdf)
each have three pages. The [revision 2 native deck](https://docs.google.com/presentation/d/1vtFHD5zVx5Kgqrl6qT8n1GEIHa8_PRmqnKksEin2hgQ/edit)
read back three slides in order and preserved the diagram text as text boxes
alongside custom and ordinary shapes. Its [Google PDF](google-slides-pilot/cs408-conversion-pilot-round8-rev2-google.pdf)
identifies Google as creator, has all three 1,024 × 768 pages, and shows the
arrowheads and explicit line breaks. It is 107,450 bytes. The unchanged
slide 69 control matches Round 4 Google page 69 pixel for pixel at 480 pixels
wide. Google word bounds for the blue-set labels now match the source on
both lines horizontally and on the first line vertically; Google's second
line sits about 9 points lower than the source because of its line metrics,
but remains inside the ellipse and does not collide with another object.

The first and corrected native decks both remain in the shared test folder
so the observed failure and repair can be compared. Drive requests were
serial with 3–4 second pauses between calls. No rate limit occurred. The
round validates this vector-path method for the two scientific-method
slides; Round 9 separately tests its use on CFG diagrams.

### Round 9 — control-flow graphs

The [Round 9 map](google-slides-pilot/cs408-conversion-pilot-round9-map.csv)
keeps slides 98 and 104 as unchanged controls and tests four CFG diagrams on
99–102. The [first PPTX](google-slides-pilot/cs408-conversion-pilot-round9.pptx)
and [first Google PDF](google-slides-pilot/cs408-conversion-pilot-round9-google.pdf)
showed the source arrow connectors crossing nodes or labels after import.
Google also split branch labels across lines. This first deck remains in the
[shared test folder](https://docs.google.com/presentation/d/1T6Va6BZz_BubkjycPFDc_Sb8CmKnA9DvOJ7mXWie9qs/edit)
as the failure example.

Round 9 reused the source-vector method from Round 8. It extracted each
orange shaft and arrowhead from the corresponding source-PDF SVG, then
rebuilt them as separate editable freeforms in the PPTX. The four CFGs use
8, 13, 8, and 10 shafts, respectively, with a matching separate arrowhead
for each. Slides 100–102 store the objects inside PowerPoint groups. The
rebuild code now traverses nested group children and inserts each head next
to its shaft without flattening or removing the group. The group transforms
on these pages are identity transforms, so the source-PDF coordinates map
directly to slide coordinates.

The first repair fixed the graph paths and one-line true/false labels, but
Google's render also clipped the last letters of “Program Text” and “CFG” on
slide 99, clipped white “CFG w/o BBs” and “CFG w/ BBs” labels against blue
arrowheads on slide 100, and placed slide 102's last brace a few points below
its dashed code frame. The final PPTX uses no-wrap text with zero side insets
for short labels, two explicit lines for the white labels on slide 100, and
safe 32-point Arial labels for “Program Text” and “CFG.” It brings those blue
arrow labels to the front. The slide 102 code frame grows by 8 points to
contain the brace while leaving the code text and numbering intact. All of
these remain editable text or shapes; no slide was converted to an image.

The intermediate [revision 3 deck](https://docs.google.com/presentation/d/1RcpJFFAk1Se4I_8iCEwITbYMCp6syx0D4WIvrHMBmxg/edit)
and [Google PDF](google-slides-pilot/cs408-conversion-pilot-round9-rev3-google.pdf)
confirmed the label repairs but exposed an unsuccessful line-spacing change:
setting 26-point leading moved the final brace much farther below its frame.
Measure the rendered text and frame together before changing paragraph
leading. Revision 4 kept the original code spacing and extended the frame
slightly instead.

The final [revision 4 PPTX](google-slides-pilot/cs408-conversion-pilot-round9-rev4.pptx)
and [Linux PDF](google-slides-pilot/cs408-conversion-pilot-round9-rev4-linux.pdf)
contain six pages in map order. Its [native Google deck](https://docs.google.com/presentation/d/1Y2docfCaRugym_wOF2vwq7u3LfXf6fIuK9PDUi93K8o/edit)
read back six slides. The [Google PDF](google-slides-pilot/cs408-conversion-pilot-round9-rev4-google.pdf)
identifies Google as creator, has six 1,024 × 768 pages, and is 144,648
bytes. The arrow paths and arrowheads are in the intended positions; branch
labels stay on one line, and the Program Text, CFG, and blue CFG labels are
fully visible. The final brace is inside its extended frame. At 900 pixels
wide, the unchanged controls on pages 1 and 6 match combined slides 98 and
104 in the Round 4 Google PDF pixel for pixel.

Drive activity was serial: three imports, each followed by one presentation
read, one PDF export, and one PDF fetch, with at least four seconds between
requests. No rate limit occurred. This round validates source-vector
reconstruction on this CFG family, including grouped diagrams. It does not
prove the method for subset diagrams, tables, equations, or every CFG layout.

### Round 10 — coverage diagrams and typography

The final [four-page map](google-slides-pilot/cs408-conversion-pilot-round10-rev6-map.csv)
keeps combined slide 153 as an unchanged control, tests the `CFG` label fit
on 154, and repairs subset-symbol placement on 155–156. The
[final PPTX](google-slides-pilot/cs408-conversion-pilot-round10-rev6.pptx),
[Linux PDF](google-slides-pilot/cs408-conversion-pilot-round10-rev6-linux.pdf),
and [Google PDF](google-slides-pilot/cs408-conversion-pilot-round10-rev6-google.pdf)
are retained with the pilot. The
[native Google deck](https://docs.google.com/presentation/d/1JvHVSP6X4lBrk6EG02cSG-TeDIPwiaDwnpzBI_a-AU4/edit)
read back as four slides in order: 153, 154, 155, and 156.

The first three-page pilot used slide 154 as an unchanged control. Its Google
PDF exposed that the `CFG` label wrapped as `CF` / `G`. This was already
visible in the source PDF, so it is a source-layout issue that needed a
readable editable repair, not a defect introduced only by Google. The original
text shape used 46 pt Bebas Neue and 90,000-EMU left and right insets.
Diagnostic revisions showed:

- 30 pt with the original insets still wrapped.
- 18 pt fit on one line but looked smaller than necessary.
- 24 pt with the original insets still wrapped.
- 24 pt with both horizontal insets set to zero fit on one line in both
  LibreOffice and Google.

The final method preserves the text and font family, reduces only this
label's size, and removes only its excessive side insets. No picture or
whole-slide fallback was needed. The [Round 10 revision 2 map](google-slides-pilot/cs408-conversion-pilot-round10-map.csv)
and [revision 3 map](google-slides-pilot/cs408-conversion-pilot-round10-rev3-map.csv),
[revision 4 map](google-slides-pilot/cs408-conversion-pilot-round10-rev4-map.csv),
and [revision 5 map](google-slides-pilot/cs408-conversion-pilot-round10-rev5-map.csv)
are retained as iteration evidence; only revision 6 passed the full Google
check. The slide 155 and 156 subset symbols are separate editable text shapes,
each placed in its own relation gap. At presentation size, the labels, blue
outlines, branches, and all ten symbols are visible in Google's PDF.

Slide 153 in the final deck is unchanged from Round 4 and matches the full
Round 4 Google PDF pixel for pixel when both are rendered at 120 dpi. The
slide 154 comparison between revision 2 and revision 6 changes only the
`CFG` label region. Page count, native text, and relation-symbol count were
checked by structural readback; PDF text extraction confirmed the one-line
`CFG` label and all coverage labels. A downscaled full-page preview initially
made the slide 155 diagram look absent, but a high-resolution crop and text
extraction confirmed the complete diagram. Inspect crops before diagnosing
missing artwork.

The unchanged slide 153 control visibly retains small bullet markers from
empty list paragraphs; Round 10 does not alter them. Record this as a
separate list-formatting repair example. No live edit/readback was performed
on the Round 10 revision 6 deck itself. Later edit checks used a disposable
copy of that pilot and the separately requested Round 4 deck; see the
[live edit record](GOOGLE_DRIVE_ACCESS.md#verified-live-text-edits).

The final native deck is in the shared folder. Its 281,012-byte Google PDF
has four 1,024 × 768 pages. The connector stream did not provide a local
workspace path, so the documented bounded compatibility transfer was used
for this small export. Round 10 revision 6 used one import, one compact
presentation read, and one PDF fetch, with at least five seconds between
Drive requests. No rate limit occurred. The 10 MB-plus PDF path remains
unverified.

### Round 11 — CFG label fit with original fonts

Round 11 tested the issue the user identified in Round 11 rev3's third pilot
page: labels such as `true`, `false`, and `CFG` split at the edge. The final
[three-page map](google-slides-pilot/cs408-conversion-pilot-round11-rev4-map.csv)
keeps combined slide 114 as a control and repairs slides 115–116. The final
[PPTX](google-slides-pilot/cs408-conversion-pilot-round11-rev4.pptx),
[Google PDF](google-slides-pilot/cs408-conversion-pilot-round11-rev4-google.pdf),
and map are retained with the pilot. The
[native Google deck](https://docs.google.com/presentation/d/1iov7hGZMI1BnyVNWcwwvG-XxcslA4qJCMzatqMORMSA/edit)
read back as three slides in the mapped order: 114, 115, 116. Its current
revision is `0TUO7uma-IfDJA`.

The final repair was local and editable. On slide 115, the `Program Text` and
`CFG` labels retained their original 46 pt Bebas Neue; on slide 116, `CFG`
retained 46 pt and `true`/`false` retained 20 pt. For those one-line labels,
the repair disabled wrapping and removed unnecessary left/right insets. The
eight arrows on each repaired slide were rebuilt as editable vector lines
from the source PDF paths. No image or whole-slide fallback was needed.

The revision sequence taught two separate lessons. Rev2 reduced fonts and
made labels fit, but the labels became too small. Rev3 restored the original
46 pt CFG label on slide 115 and kept the local correction targeted. Rev4
added the corresponding label repair on slide 116. Check wrapping and box
insets before reducing a font; Round 10 slide 154 remains a case where a
local size reduction was necessary.

Round 11 rev1's LibreOffice preview appeared to overflow because Linux did
not have Bebas Neue: Fontconfig matched DejaVu Sans, which is wider. The
Google PDF embedded Bebas Neue. Do not shrink labels to compensate for a
substituted local font. The final rev4 roundtrip did not create a LibreOffice
PDF; the audit accepted the Google PDF without `--linux-pdf`. Its three
1,024 × 768 pages total 242,663 bytes. Package integrity, map/order,
unchanged slide 114 XML, Google PDF text, and control pixels passed; slide
114 matched the Round 4 Google PDF at 120 dpi.

Google readback of slide 115 returned 33 page elements (25 shapes and 8 line
objects). Slide 116 returned 32 (24 shapes and 8 line objects). Text, code,
and arrows were present as native elements; a separate reversible API edit
tested only one arrow's position, as recorded in the
[Google API evidence](GOOGLE_DRIVE_ACCESS.md#verified-native-vector-object-edit).
That test does not establish that every line style or every line object can
be edited.

Google import, structural read, PDF export, and fetch were serialized with
at least 5.5 seconds between calls. One final PDF fetch supplied the bytes
materialized locally in chunks; no duplicate fetch was needed and no rate
limit occurred. A rev2 PDF fetch had been repeated too soon while preserving
its response; avoid that pattern. The pacing and materialization details are
in the [Drive guide](GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf).

## Part 2 scale validation, revision 3

The Part 2 pilot covers combined slides 261–492 (232 slides). Rev2 already
fixed the missing media on slides 296 and 376 and corrected the background
z-order on slides 474 and 476. Its comparison still showed that slides 474
and 476 had lost the source's translucent white panel behind body text.

Rev3 adds a 70% white fill to the editable body text boxes on local slides
214 and 216 (combined slides 474 and 476). The repair is produced by
[`repair_part02_contrast_panels.py`](google-slides-pilot/repair_part02_contrast_panels.py)
from rev2; it does not rasterize text or change slide order. The updated map
is [`cs408-editable-part-02-scale-rev3-map.csv`](google-slides-pilot/cs408-editable-part-02-scale-rev3-map.csv).

- [Rev3 PPTX](google-slides-pilot/cs408-editable-part-02-scale-rev3.pptx)
- [Rev3 native Google deck](https://docs.google.com/presentation/d/1OTrLWNKqwFOokESPsZuoBoqWI6Qjm-7IxiSmsa0f50I/edit)
- [Rev3 Google PDF](google-slides-pilot/cs408-editable-part-02-scale-rev3-google.pdf)
- [Page-by-page visual-diff report](google-slides-pilot/cs408-editable-part-02-scale-rev3-visual-diff.csv)
- Slide 214 [rev2/rev3 comparison](google-slides-pilot/cs408-editable-part-02-scale-rev3-compare-214.jpg)
- Slide 216 [rev2/rev3 comparison](google-slides-pilot/cs408-editable-part-02-scale-rev3-compare-216.jpg)

The native readback returned `p1` through `p232` in order. On `p214`, the
body remains a native text shape (`p214_i313`) with white fill alpha
0.7019608; `p216_i322` has the same editable text and fill. The rev3 Google
PDF is 9,899,270 bytes and has 232 pages. At 854 × 640 pixels, 230 pages
are pixel-identical to rev2; only pages 214 and 216 changed. Both were
visually reviewed against the source: the white text panels are restored and
the text stays readable over the marshmallow photo. Part 2 visual scale
verification is complete; source reconciliation and final-batch approval
remain open.

The PDF was materialized without curl using the Slides export-and-render
helper with `google_drive_fetch` wrapped to request `include_base64: true`.
This returned the bytes through the connector and the helper wrote them
locally in bounded chunks. The helper's first full-deck local render exceeded
its 30-second `exec_command` wait and reported failure even though the local
PDF was valid; rendering continued in the spawned session. We reused that
one PDF, rendered the missing pages, and produced a complete 60-dpi set for
the 232-page diff. For future large renders, poll the returned `session_id`
with `write_stdin` until it exits; do not repeat a Google export because the
local renderer exceeded its first wait.

#### Open-work snapshot after Round 8 (superseded by Round 9)

This queue is preserved as the state before the CFG round. Slide 99–102 arrow
repairs, slide 99 labels, and slide 102's code-frame fit have since been
addressed. Use the [current open-work list](#open-work-after-round-11).

- Merge verified repairs from Rounds 5–8 into a new 260-slide Part 1
  candidate. Round 8 adds no media or relationships. Use the
  [integration table](#integrate-verified-repairs-into-a-full-batch),
  preserve notes and package order, and run one full-size Google check.
- Use Round 9 to test a different diagram family, with an unchanged control
  and adjacent builds. The CFG examples on 99–102 and 115–125 are good
  candidates. Keep the vector-path repair family-specific until it passes
  on a different lecture and layout.
- Resolve slide 128's inset, B5 box, and equation association. Check the
  intended Keynote reveal on 205–206 and the timeline endpoints on 244.
- Repair the other diagram and subset cases: 155–156, 176–182, 186, and
  remaining problems on 70, 178–179, and 238. Recheck the 253 diagnostic
  at projected size.
- Test one actual Google Slides edit and read it back on a disposable copy.
  Round 8's structural read confirms object types but did not test live
  editing.
- The connector path for a native PDF above the standard 10 MB export limit
  still needs a materializable stream or a browser download.
- After the conversion method has passed across the major slide families,
  prepare four ordered upload blocks using only complete original-deck and
  topic boundaries. Increase to eight or sixteen only if measured PPTX size,
  import, export, or review time calls for it. Preserve source order; do not
  target equal slide counts. Verify each block before uploading the next one.

#### Open work after Round 9 (superseded by Round 10)

- Merge the verified repairs from Rounds 5–9 into a new 260-slide Part 1
  candidate. Carry forward the newest repair per slide from the
  [integration table](#integrate-verified-repairs-into-a-full-batch), preserve
  notes and relationships, and check the full-size Google import and PDF.
- Use Round 10 to test a different diagram/layout family with a nearby
  unchanged control. Candidate families include the subset diagrams on
  155–156 and the additional control-flow examples on 115–125. Keep each
  repair rule limited to the family that passed its Google roundtrip.
- Resolve slide 128's inset, B5 box, and equation association. Check the
  intended Keynote reveal on 205–206 and the timeline endpoints on 244.
- Repair remaining diagram and subset cases on 70, 115–125, 155–156,
  176–182, 186, and 238. Recheck the slide 253 diagnostic at
  projected size.
- Test one actual Google Slides edit and read it back on a disposable copy.
  Structural reads confirm object types, but no live edit has been tested.
- Materialize a Google PDF above the standard 10 MB export limit using a
  streamed file or browser download. The small-pilot base64 compatibility
  path is only for exports known to be below that limit.
- After the method has passed across the major slide families, prepare
  upload blocks for all 2,235 slides. Keep every original source deck and
  topic whole, preserve source order, and allow block sizes to vary. Assess
  four blocks first, then eight or sixteen if measured file size, import or
  review effort calls for them. Verify every block's count and Google PDF
  before proceeding to the next one.

#### Open work after Round 10 (superseded by Round 11)

- Merge the verified repairs from Rounds 5–10 into a new 260-slide Part 1
  candidate. Carry forward only the newest verified change per slide from
  the [integration table](#integrate-verified-repairs-into-a-full-batch),
  preserve notes and relationships, and verify the full-size Google import
  and PDF.
- Run another pilot on a different diagram family, such as slides 115–125
  or 176–182, with an unchanged control. Test whether vector reconstruction,
  text-fit inspection, and the new crop-based QA transfer to a distinct
  layout before broad use. Round 11 has since repaired slides 115–116.
- Investigate the empty bullet paragraphs visible on unchanged control
  slide 153. Inspect similar list layouts before applying a general cleanup;
  keep meaningful nested bullets intact.
- Resolve slide 128's inset, B5 box, and equation association. Check the
  intended Keynote reveal on 205–206 and the timeline endpoints on 244.
- Repair the remaining diagram and subset cases on 70, 115–125, 176–182,
  186, and 238. Recheck slide 253 at projected size. Slides 154–156 were
  tested in Round 10 and are no longer in this queue.
- Test edits and readback for diagram shapes, freeform paths, image crops,
  tables, equations, and speaker notes on disposable copies. Basic text
  replacement/readback already passed; see the
  [live text edit record](GOOGLE_DRIVE_ACCESS.md#verified-live-text-edits)
  and [vector edit record](GOOGLE_DRIVE_ACCESS.md#verified-native-vector-object-edit).
  Do not treat text editability as proof that other object types are editable.
- Verify a Google PDF above the standard 10 MB export limit using a
  materialized stream or browser download. The small-pilot compatibility
  route is only for PDFs known to be below that limit.
- Plan the 2,235-slide upload as four ordered blocks first, then eight or up
  to sixteen if measured size or review time requires it. Never split an
  original source deck or topic; create cuts only where both are complete.
  Allow block sizes to vary. For sixteen blocks, use the prior course
  syllabus and schedule to estimate one week per block, while keeping all
  topics and decks whole. Keep related syllabus and homework material with
  its topic where source order permits. Verify a block completely before
  uploading the next one.

#### Open work after Round 11

- Reconcile the Spring-centered slide set topic by topic against Fall 2026
  and other newer course sources. Select the latest version for each topic;
  keep older material only when it adds useful content absent from newer
  sources, and record that reason. Complete this crosswalk before freezing
  the conversion set.
- For any *other* animation family found during source reconciliation, map
  meaningful build states and create Round 12 only if the existing Google
  roundtrip does not already cover the family. The 205–206 concurrency
  sequence is resolved: the latest Keynote export and Round 4 Google PDF
  both show first-panel then full-comic states. Preserve this as the first
  verified build-expansion example; do not spend another import on it.
- Build the Part 1 candidate from selected latest sources. Carry forward the
  repairs in Rounds 5–11 only where their source slide remains current and
  equivalent, using the [integration table](#integrate-verified-repairs-into-a-full-batch).
  Preserve notes, relationships, exact order, and untouched controls. The
  Round 4 260-slide file is a comparison baseline; the selected candidate may
  differ if the crosswalk identifies newer content.
- Continue the visual queue for slides 70, 117–125, 128, 176–182, 186, 238,
  244, and 253. Slides 115–116 now have a verified local repair; validate
  that fit method on another layout before applying it more broadly.
- Inspect the empty bullet paragraphs on control slide 153 and related list
  layouts. Preserve meaningful nested list formatting.
- Continue native API checks on disposable copies. Text replacement and one
  line-position edit/readback are verified. The imported arrow's
  `updateLineProperties` request failed; other shapes, image crops, tables,
  equations, and speaker notes still need separate edit/readback evidence.
- Validate the no-curl transfer for a Google PDF above 10 MB using streamed
  Drive fetch and authenticated browser download when a local file is needed.
  If size requires smaller units, use up to 16 ordered blocks at whole
  deck/topic boundaries. Never use a shell downloader; if local transfer is
  unavailable, use paced native thumbnails and continue independent work
  while recording PDF comparison as open.
- Complete the version-aware inventory and topic-boundary map for the
  selected input slides. Confirm the nine existing batch boundaries at topic
  level; they are known to end at complete source decks. Meaningful animation
  expansion may increase the output count.
- Build variable-sized, contiguous upload blocks from complete deck/topic
  groups. Assess four blocks first, then eight or sixteen only if measured
  import size and review effort require them. Keep each block's exact source,
  topic, build-state, and syllabus/homework mapping in its manifest.

Rebuild the pilots from the Round 4 PPTX and combined
reference. The script requires Python, pikepdf, lxml, Pillow, and
Poppler's `pdftocairo`. It prints the combined slide numbers in export
order. Use a new output path if that round's original PPTX already exists.

```sh
python3 out/combined/google-slides-pilot/rebuild_conversion_pilots.py 9 \
  --output out/combined/google-slides-pilot/round9-rebuilt.pptx
```

The subset keeps slide order and follows package relationships to
preserve the selected pages' notes, layouts, masters, and media.
For a local PDF, the saved approval prefix is
`libreoffice --headless --convert-to pdf`. Put any per-run
`-env:UserInstallation=file:///...` and `--outdir` arguments after
that prefix and use a temporary profile.
