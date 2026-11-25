# CS 408 combined slide collection

[Output index](../README.md) · [Conversion runbook](SLIDE_CONVERSION.md) ·
[Google Drive access](GOOGLE_DRIVE_ACCESS.md) ·
[Pilot folder guide](google-slides-pilot/README.md)

The collection contains 2,235 visible slides from 57 decks. The Spring 2026
lecture sequence comes first, followed by additional decks and the lab
tutorial. Distinct decks are retained even when they revisit a topic. For
the newer reading and exercise sequence, see the
[Fall 2026 study guide](../README.md#fall-2026-study-guide).

## Test the editable import first

The [Round 4 PPTX](google-slides-pilot/cs408-editable-part-01-round4.pptx)
is the current full Part 1 comparison baseline. Its
[Google export](google-slides-pilot/cs408-editable-part-01-round4.pdf)
has all 260 pages. Rounds 5–11 tested targeted repairs in smaller native
decks. The latest is [Round 11 revision 4](google-slides-pilot/cs408-conversion-pilot-round11-rev4.pptx),
with its [Google PDF](google-slides-pilot/cs408-conversion-pilot-round11-rev4-google.pdf)
and [three-page map](google-slides-pilot/cs408-conversion-pilot-round11-rev4-map.csv).
It repairs the split `Program Text`, `CFG`, `true`, and `false` labels on
combined slides 115–116 while preserving their original fonts and editable
objects. Slide 114 is an unchanged control and matches the Round 4 Google
export pixel for pixel at 120 dpi. The [native Google deck](https://docs.google.com/presentation/d/1iov7hGZMI1BnyVNWcwwvG-XxcslA4qJCMzatqMORMSA/edit)
has the three mapped slides in order. The
[conversion runbook](SLIDE_CONVERSION.md#round-11--cfg-label-fit-with-original-fonts)
records the revisions, local font-substitution caveat, repair rule, API
readback, and remaining work.

Native text edit/readback has been verified on a disposable Round 10 copy and
on the requested Round 4 deck. A reversible line-position edit/readback also
passed on a disposable copy of Round 11 revision 4; Google's line-style
update was rejected for that imported arrow. These results are object- and
operation-specific. See the Google Drive guide's records for
[text edits](GOOGLE_DRIVE_ACCESS.md#verified-live-text-edits) and
[native vector edits](GOOGLE_DRIVE_ACCESS.md#verified-native-vector-object-edit).

Run the [local pilot audit script](google-slides-pilot/audit_conversion_pilot.py)
after each round. It verifies ZIP relationships, map/order agreement, control
XML, PDF page counts, requested text, and optional baseline pixel equality.
It is local-only; manually inspect every repaired slide in the Google PDF.

The Part 2 scale pilot contains combined slides 261–492 in order. The
[rev3 native Google deck](https://docs.google.com/presentation/d/1OTrLWNKqwFOokESPsZuoBoqWI6Qjm-7IxiSmsa0f50I/edit)
passed 232-slide order readback. Its [Google PDF](google-slides-pilot/cs408-editable-part-02-scale-rev3-google.pdf)
was exported and materialized without curl; page-by-page comparison shows
only the intended repairs on local slides 214 and 216 differ from rev2.
Their editable text shapes now restore the source's translucent white panels.
The [rev3 map](google-slides-pilot/cs408-editable-part-02-scale-rev3-map.csv)
and [visual-diff report](google-slides-pilot/cs408-editable-part-02-scale-rev3-visual-diff.csv)
are preserved with the pilot. See the
[Drive transfer guide](GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf)
for the no-curl method. This and all other pilot decks live in the Drive
`Pilots` subfolder; final batch decks belong at the shared folder root. See
the [pilot folder guide](google-slides-pilot/README.md).

The [first pilot's slide map](google-slides-pilot/slide-map.csv) identifies
the original 16 selected pages and their lecture sources. The runbook
records where the user inserted a slide in Round 1 and the page maps for
later pilots. Round 9's [map](google-slides-pilot/cs408-conversion-pilot-round9-map.csv)
identifies its two controls and four repaired diagrams. Use those maps
whenever the Google export has a different slide range from the collection.
Round 10's original three-page map applies to revision 2; its
[revision 6 map](google-slides-pilot/cs408-conversion-pilot-round10-rev6-map.csv)
adds slide 153 as the unchanged control. Round 11 revision 4's map covers
slides 114–116; earlier revision maps remain beside their diagnostic PPTX and
PDFs. Use the map for the exact revision being inspected.

## Map a slide to its source and artifacts

1. Use the combined slide number as the stable reference. One-based page
   230 of the [combined PDF](cs408-all-slides.pdf) is combined slide 230.
   In a pilot with gaps, look up the combined number in that round's
   ordered page map before comparing renders.
2. Find the row with `first_slide <= number <= last_slide` in
   [sources.csv](sources.csv) or [sources.json](sources.json). The position
   within the visible source deck is `number - first_slide + 1`.
   Use that position to look up the saved build in `visible_indices`
   when present. The corresponding `original_pdf_page_flags` value
   indicates whether the combined page reused the paired PDF's original
   export. Open the matching reference slide to confirm the build,
   especially if the combined PDF already shows an issue.
3. Find the parent batch in the
   [editable manifest](editable-parts-manifest.json). Final batch PowerPoints
   are stored directly in this `combined/` folder. Use the Round 4 PPTX
   for the current full Part 1 work. The original Part 1 in the manifest
   and the locally repaired Round 4 file have the same range. Use the
   runbook to identify which version already contains a repair.

From the repository root, the following lookup returns the original
source and batch for combined slide 230.

```sh
slide=230
jq --argjson slide "$slide" '
  .[] | select(.first_slide <= $slide and $slide <= .last_slide)
  | ($slide - .first_slide) as $offset
  | {source, source_kind, paired_pdf, visible_page: ($offset + 1),
     keynote_index: .visible_indices[$offset],
     reused_original_pdf: .original_pdf_page_flags[$offset]}
' out/combined/sources.json
jq --argjson slide "$slide" '
  .[] | select(.first_slide <= $slide and $slide <= .last_slide)
  | {file, first_slide, last_slide}
' out/combined/editable-parts-manifest.json
```

Keep each pilot's PPTX, available local render, Google PDF, and page map together.
Rounds 5–7 use the stem `cs408-conversion-pilot-roundN` with the PDF
suffixes `-linux.pdf` and `-google.pdf`. Keep older filenames as written
in the logs so their links resolve. Round 8 keeps both the first Google
render, which exposed two repair issues, and the corrected `-rev2` files.
Its [page map](google-slides-pilot/cs408-conversion-pilot-round8-map.csv)
applies to both revisions. Round 9 retains its first failing import and the
revised `-rev4` PPTX and Google PDF. Its page map applies to every revision.
Round 10 keeps maps for its three-page diagnostic and the final four-page
revision because the control selection changed. The
[rebuild script](google-slides-pilot/rebuild_conversion_pilots.py) reproduces
the selected slides and prints their combined numbers in order.
Use the [conversion and comparison instructions](SLIDE_CONVERSION.md)
when adding a new test and the [Drive guide](GOOGLE_DRIVE_ACCESS.md)
to create its native deck and download its Google render.

## Available PowerPoints

- This `combined/` folder contains nine editable PowerPoints in course order,
  split at lecture boundaries. The [manifest](editable-parts-manifest.json)
  maps each file to its original slide range. These are the baseline batches,
  each with at most 275 slides. The Round 3 and Round 4 repairs are in their
  own Part 1 files under `google-slides-pilot/`, alongside the smaller
  tests for Rounds 5–11. Each existing boundary falls after a complete source
  deck; future upload blocks must also keep complete topics together, so the
  final block sizes may differ from these baseline files.
- The [full editable PowerPoint](cs408-all-slides-editable.pptx) contains
  the same 2,235 slides in one file.
  Text and shapes from Keynote are editable. The three PDF-supplied decks use
  page images. The combined file is about 87 MB, but each smaller batch is
  easier to check and retry.
- The image-based [Part 1](cs408-google-slides-part-1.pptx) and
  [Part 2](cs408-google-slides-part-2.pptx) use a single image per slide. Import them
  separately if the task calls for the image-based edition. For editable
  conversion, use the runbook's object-level repair and fallback process.
  [The image-based manifest](import-parts.json) records the ranges and sizes. The
  single image-based `cs408-all-slides.pptx` is about 117 MB, above Google's
  [100 MB conversion limit](https://support.google.com/drive/answer/37603?hl=en).
- The [combined PDF](cs408-all-slides.pdf) is the full visual reference
  with 57 deck bookmarks. The source manifests above record the
  corresponding files and slide ranges.

Google's [PowerPoint-to-Slides guide](https://support.google.com/docs/answer/9310378)
describes importing and converting PowerPoint files.

## Source selection and conversion

Use the newest available version of each topic as the primary source. Keep an
older lecture, slide, homework, or syllabus item only when its useful content
does not appear in the newer version; note its source and why it remains.
Do not duplicate an older version that a newer source has superseded. The
current 2,235-slide map is Spring-centered and has not yet been reconciled
topic by topic against the Fall 2026 material for final source selection.
Complete that crosswalk before freezing the conversion set. Use the
candidate [Fall 2026 crosswalk](source-version-crosswalk.csv) to compare
exports with their current combined-source counterparts. Its mappings are
topic-level candidates; content review and final keep/replace decisions are
still open. The 20 referenced PDFs (956 pages) are present in the base branch
`origin/fall+2026` at `slides/f26-pdfs/`, not in the active branch's checked-out
course tree. They were extracted with `git archive` into the temporary
`out/.build/fall-source/` folder; their validated page counts and metadata are
in [fall-source-metadata.csv](fall-source-metadata.csv). To reproduce the
extraction from the repository root, run:

```sh
git archive --format=tar origin/fall+2026 slides/f26-pdfs | tar -xf - -C out/.build/fall-source
```

Use the slide-level source maps below to preserve provenance, and check the
current syllabus and course order when deciding where unique older material
belongs. Do not switch branches just to inspect Fall PDFs; the archive command
keeps the current working branch intact.

The source files have checkout timestamps, so selection used dates embedded
inside the Keynote archives and PDF metadata, with PDF UTC dates converted to
the local time zone. Modern Keynote slide order and skip flags were read
directly from the IWA archives; the flags match the existing PDF slide counts
for the corresponding unchanged decks.

Within this Spring-centered candidate set, the latest saved Keynote supplies
each deck, except symbolic execution (`17`), whose March 26 PDF is newer and
more complete than its March 18 Keynote.
Test-case minimization (`20`) and the lab tutorial are supplied only as PDFs.
The older 37-page structural-coverage PDF in the top-level directory is
superseded by the later version in `pdfs/` and its current Keynote.

The 398 slides marked skipped in Keynote were excluded from the combined
collection. These include archived material and unused template slides.
The original files are unchanged. A separate editable build-state conversion
may produce more than 2,235 output slides when meaningful animation states are
expanded.

Keynote was converted with LibreOffice, retaining editable text, shapes, and
available speaker notes. Font names were normalized and available open fonts
were used to reduce text wrapping. Original Apple-exported PDF pages were
reused where the corresponding Keynote slide predates that export and its
text, including code operators, matches. Other pages were rendered from the
selected Keynote slides. Third-party conversion can change typography and
some diagram formatting; these files are not a native Apple Keynote export.
The source PDFs and image-based PowerPoint parts flatten animation builds.
For the editable conversion, meaningful instructional build states should
become sequential static slides in original build order, with a map from each
output page to its source slide and build state. Keep the resulting sequence
inside its complete source deck and topic.

The first checked example is combined slides 205–206 from
`06-408st-concurrency.key`: the Round 4 Google PDF preserves the first comic
panel followed by the completed comic. The paired static PDF repeats the
completed comic, so it cannot validate this animation order. See the detailed
[build audit](SLIDE_CONVERSION.md#animationbuild-audit-combined-slides-205206).

The two image-based import parts render the final PDF, using slide images up
to 1,100 pixels wide and extracted slide text in the speaker notes. The lab's
widescreen pages are centered without distortion on the 4:3 PowerPoint canvas.
The PDF retains its original page dimensions and vector text where available.

## Verification

The editable decks now use one notes master per file. The repair preserved all
2,235 slide XML parts, 805 note pages, and 694 images byte for byte. The
image-based decks now declare their existing notes master in the presentation
XML. ZIP integrity, internal relationships, slide order, and the import
sizes were checked after repair.

LibreOffice rendered the 16-slide pilot and the 275-slide third editable batch.
In the pilot, the photo backgrounds and image-only pages rendered, while some
editable titles wrapped differently and some code or diagram elements shifted.
For example, compare pilot slides 7 and 12 with the reference. Linux font
substitution can account for some of these differences. Rounds 1 and 2 kept
all 16 original pilot slides in order. Rounds 3 and 4 each kept all 260
slides in Part 1 in order. Rounds 5–11 completed connector imports and PDF
exports on small, source-mapped test decks. Round 9 revision 4 verified
editable CFG arrows and matched both unchanged controls pixel for pixel.
Round 10 revision 6 verified a font-and-inset repair, moved subset symbols,
and matched its unchanged control pixel for pixel. It also surfaced empty
bullet paragraphs on control slide 153; they are preserved as an open repair
example. Round 11 revision 4 disabled wrapping and removed excess horizontal
insets on the affected CFG labels while retaining their original font sizes.
Its Google PDF control matches the Round 4 export pixel for pixel. A local
LibreOffice render substituted a wider font for Bebas Neue; use Google's PDF
to judge the import and do not reduce a font solely to compensate for that
local substitution. See the runbook for reusable rules and current open work.
