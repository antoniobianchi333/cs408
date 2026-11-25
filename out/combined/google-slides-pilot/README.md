# Pilot files

This folder holds pilot-only artifacts: small conversion rounds, full-size
comparison imports such as Round 4, revisions, local PDFs, Google exports,
slide maps, rebuild scripts, and local audit scripts. Keep the inputs and
evidence for each round together here. Put temporary renders and transfer
scratch files in `out/.build/` instead of this folder.

Final-candidate batch PowerPoints stay directly in `out/combined/`, beside
the full collection PDF and source maps. The batch manifest is
[`../editable-parts-manifest.json`](../editable-parts-manifest.json). Do not
put final batch PowerPoints in this pilot folder.

## Google Drive organization

The user's shared CS408 folder is
[the Drive root for this project](https://drive.google.com/drive/folders/16vTRNocHa1rlPN1bii_w0b8Ce90XrFbn).
Keep pilots and disposable API/edit tests in its [`Pilots` subfolder](https://drive.google.com/drive/folders/1PHuKHahwY2PxviNWTM2f8kYmb7K-37Dj).
Upload final batch decks directly to the shared folder root, not to `Pilots`.
As of November 24, 2026, all 17 presentations previously listed at the shared
root were pilot/test decks and have been moved into `Pilots`; the shared root
is reserved for final batches.

## Future rounds

1. Build and inspect a pilot locally under this folder, with a source page map.
2. Import it into Google Slides with a title that includes the round and
   revision, then keep its native URL and Google PDF evidence in the runbook.
3. Keep disposable live-edit tests in `Pilots` and restore them after testing.
4. Keep API calls serial and paced as described in
   [`GOOGLE_DRIVE_ACCESS.md`](../GOOGLE_DRIVE_ACCESS.md).
5. Do not promote a pilot to a final batch until its source selection,
   slide order, editability, and Google PDF visual review are recorded.

## Current scale pilot: Part 2 rev3

The current large pilot is the 232-slide
[`Part 2 rev3 PPTX`](cs408-editable-part-02-scale-rev3.pptx), imported as
[native Google Slides](https://docs.google.com/presentation/d/1OTrLWNKqwFOokESPsZuoBoqWI6Qjm-7IxiSmsa0f50I/edit).
Its [Google PDF](cs408-editable-part-02-scale-rev3-google.pdf),
[page map](cs408-editable-part-02-scale-rev3-map.csv), and
[232-page visual-diff report](cs408-editable-part-02-scale-rev3-visual-diff.csv)
are the acceptance evidence. The 70% white shape fills on slides 214 and 216
restore contrast while leaving body text editable. The corresponding
[repair script](repair_part02_contrast_panels.py) starts from rev2 and emits
rev3 plus its map. Two comparison images are retained for the affected slides.

The verified export helper's no-curl transfer recipe and the Google readback
are in [`GOOGLE_DRIVE_ACCESS.md`](../GOOGLE_DRIVE_ACCESS.md#download-the-google-rendered-pdf).
Temporary full-deck page renders stay in `out/.build/`; keep the PDF, PPTX,
source map, diff report, repair script, and reviewed target comparisons here.
