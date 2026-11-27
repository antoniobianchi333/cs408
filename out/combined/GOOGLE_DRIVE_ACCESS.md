# Connect Google Drive to Codex for CS 408

[Output index](../README.md) · [Slide conversion runbook](SLIDE_CONVERSION.md)

Use this guide for the part of the conversion that runs in Google. The
local PPTX and the page map identify the exact test input. A native Google
Slides copy and its PDF record what Google imported for that round. The
current import evidence includes Rounds 5–16. Round 16 is the current
Test Anatomy repair pilot; its native structure was read back, but its Google
PDF still needs page-by-page review. Round 12 revision 2 is a technical pilot
for rebuilding four older TCM pages; those pages are not selected for final
content. See the
[readback and visual review](SLIDE_CONVERSION.md#round-12--editable-test-case-minimization-supplement).
The latest diagram-repair pilot is
[Round 11 revision 4](SLIDE_CONVERSION.md#round-11--cfg-label-fit-with-original-fonts).
Native text edit/readback was separately verified on a disposable Round 10
copy and on the requested Round 4 deck. A reversible vector-position edit
was also tested on a disposable Round 11 copy; its line-style update failed.
The evidence and limits are recorded below.

**Current connector check (November 25, 2026):** read-only listing now works
for the exact shared project folder. The folder listing returned its `Pilots`
subfolder; a second paced listing returned the pilot presentations. The
visible project root had no final batch decks in that response. The calls were
serialized with more than five seconds between them. This supersedes the
earlier transport failure below; it was connector-session behavior, not a
Google permission denial or API rate limit. Continue using one Drive call at a
time and keep the same pacing before larger imports, exports, or readbacks.

## Share and connect the folder

1. Use a dedicated Google account for the slide work. In Drive, keep the
   [CS 408 test folder](https://drive.google.com/drive/folders/16vTRNocHa1rlPN1bii_w0b8Ce90XrFbn)
   set to **Restricted** and share it with that account. **Viewer** is enough
   for inspection. Use **Editor** when the account needs to add or change
   test decks. The connector follows the account's Google permissions,
   including any other files the account owns or can open. Keep the
   dedicated account's access limited to the project.
   [Google Drive folder permissions](https://support.google.com/drive/answer/7166529)
2. In ChatGPT, open **Plugins**, find **Google Drive**, and select **Connect**.
   Sign in as the dedicated account in Google's browser authorization flow.
   Complete any consent prompts there and keep passwords and tokens out of
   the conversation and repository.
   [Google Drive setup in ChatGPT](https://help.openai.com/en/articles/10929079)
3. In Codex, paste the exact folder link and ask **“List the files in this
   folder using Google Drive.”** A successful list verifies folder access
   from that session. Check the native deck's outline separately to verify
   that the session can read Slides.

## If a Codex session cannot open the folder

- Open the link in Drive while signed in to the connected Google account.
  If Google denies access, check the folder share for that account.
- If the folder opens in ChatGPT and Codex reports that Drive is
  unavailable, check that the same ChatGPT workspace has the plugin
  installed and enabled. In the Linux CLI, `codex login status` checks
  the sign-in method and `codex plugin list` checks plugin availability.
  If the session started before installation, retry the same prompt in a
  fresh session launched with `codex -C /home/antoniob/git/cs408`.
  [Codex plugin setup](https://learn.chatgpt.com/docs/plugins)
- Use the folder link directly in the prompt if `/apps` or the **Sources**
  menu is absent. After installation, the connector became available in
  the existing CS 408 session and the plain-link test worked. It required
  no second Google sign-in.
- If the file list succeeds and a Slides action fails, record which
  action failed and its error. Folder listing, outline reads, edits,
  imports, and exports can have different permissions or availability.
  For a large deck, use the presentation outline to check the slide
  count and order. The outline worked for Round 4 after the presentation
  read returned an internal error.
  [Google Drive troubleshooting](https://help.openai.com/en/articles/10929079#troubleshoot-google-drive)

## Verified for this project

On November 24, 2026, Codex listed **cs_408_ai_editable** and read the
outline of the native
[Round 4 deck](https://docs.google.com/presentation/d/1RsGbPcJJZucpjhRbT1-K3cIYqyC25hCHmqqqOSDw1A8/edit).
It returned **260 slides**. The [Round 4 PDF audit](SLIDE_CONVERSION.md#round-4--checked)
used the manually downloaded Google PDF. In Rounds 5–9, Codex imported
local PPTX files into the shared folder, read back native objects, and saved
Google's PDFs locally. Round 8 revision 2 read back three slides in order;
its Google PDF was 107,450 bytes and matched the control slide pixel for
pixel against Round 4. Keep the first Round 8 import as evidence of the
missing arrowheads and changed line wrapping that motivated revision 2.
Round 9 revision 4 read back six slides and exported a six-page, 144,648-byte
Google PDF. Its controls on slides 98 and 104 matched the Round 4 Google PDF
pixel for pixel. The [final Round 9 deck](https://docs.google.com/presentation/d/1Y2docfCaRugym_wOF2vwq7u3LfXf6fIuK9PDUi93K8o/edit)
and its earlier revisions remain in the shared project folder as examples
of the iterative check. The first render exposed Google-specific graph and
text defects; the final render verifies their repairs. See the
[Round 9 log](SLIDE_CONVERSION.md#round-9--control-flow-graphs) for the
artifact map and results.
Round 10 revision 6 read back four mapped slides and exported a four-page,
281,012-byte Google PDF. Its unchanged slide 153 control matched the Round 4
Google PDF pixel for pixel at 120 dpi. The
[Round 10 deck](https://docs.google.com/presentation/d/1JvHVSP6X4lBrk6EG02cSG-TeDIPwiaDwnpzBI_a-AU4/edit)
and its local artifacts are recorded in the
[Round 10 log](SLIDE_CONVERSION.md#round-10--coverage-diagrams-and-typography).
The connector stream did not return a local workspace path, so the documented
bounded compatibility transfer was used for this small export. No rate limit
occurred.
A Round 11 rev4 import read back three slides in order and exported a
three-page, 242,663-byte Google PDF. The unchanged slide 114 matched the Round
4 Google PDF at 120 dpi. The
[Round 11 deck](https://docs.google.com/presentation/d/1iov7hGZMI1BnyVNWcwwvG-XxcslA4qJCMzatqMORMSA/edit)
and [Round 11 log](SLIDE_CONVERSION.md#round-11--cfg-label-fit-with-original-fonts)
record the exact map and revisions. Calls were serial with at least 5.5
seconds between operations; there was no rate limit. The PDF bytes were
materialized from one fetch response in local chunks.
A Drive inventory on the connected account also found items outside the
shared course folder. For slide work, use only the exact project folder ID
and deck IDs returned by imports; do not inventory unrelated Drive content.

## Run a low-volume connector roundtrip

1. Build a small local PPTX and check its package, expected count, and
   page map before sending anything to Google. In the current Google Drive
   and Slides skills, use the native PowerPoint import action. Pass the
   absolute workspace path, a unique title such as
   `cs408-conversion-pilot-roundN`, and the shared folder's exact ID
   `16vTRNocHa1rlPN1bii_w0b8Ce90XrFbn` as `parent_folder_id`. Select
   `native_google_slides` if the action exposes the upload mode.
2. Record the returned deck ID and URL. Verify the MIME type
   `application/vnd.google-apps.presentation` and the location by readback.
   Read the native presentation once for the expected slide count, order,
   and representative native text, picture, and line objects. The Slides
   skill can save this readback to a temporary JSON file for reuse.
   Check a deck's outline if the full read fails on a large presentation.
3. Use the [PDF download paths below](#download-the-google-rendered-pdf).
   Request one Google PDF for the entire pilot and render the pages locally
   with Poppler. Save it beside the input and any local render with the suffix
   `-google.pdf`. Confirm the creator, page count, and mapped page order
   before using it as evidence.
4. Send requests serially. Use the local package and visual checks between
   requests. Plan on one import, one structural read, and one PDF export
   per revision, plus a folder read when needed to confirm placement. Leave
   at least five seconds between Drive requests for these small pilots; pause
   longer after any slow response or rate-limit signal. Rounds 10 and 11 used
   this pacing and had no rate limit. Never retry a timed-out write until
   checking whether its uniquely titled deck already exists.
   Use the saved PDF for all thumbnails, crops, and text extraction.
   If Google rate-limits a read, honor `Retry-After` when provided.
   Otherwise increase the wait before the next attempt. If a write times
   out, check the folder for its unique title before retrying to avoid
   duplicate native decks.
   This five-second interval is a conservative project pacing rule based on
   our small pilot rounds; it is not a statement of Google's published quota.
5. Compare the saved Google PDF with the exact source and any local
   diagnostic render using the [roundtrip checks](SLIDE_CONVERSION.md#run-and-evaluate-a-google-roundtrip).
   Record the deck link, local PDF, and any failures or fallbacks in the
   matching roundtrip log entry.

## Download the Google-rendered PDF

**No-curl rule: never use `curl` or another shell/network client to retrieve
Google file references or signed download URLs.** The root cause of the old
fallback was a handoff mismatch: Google/Drive successfully exported the PDF,
but the connector returned a user-scoped `file_uri` (including a short-lived
download reference) rather than a local `workspace_path`. That reference was
mistakenly treated as something the shell had to download. The new streaming
fetch avoids the `files.export` 10 MB response cap; it does not itself promise
that the returned reference is mounted into the local workspace.

### Root cause, separated from size limits

The missing local path is **not caused by a PDF being too large**. The same
`include_base64: false` fetch returned a `file_uri` without `workspace_path`
for both a 74,585-byte Round 12 PDF and a 9,898,674-byte Part 2 PDF. The Drive
tool description says this option streams through `files.download` and returns
a user-scoped file reference without inline bytes. The connector response is
therefore a reference by design; this session does not automatically
materialize every such reference as a local path the renderer can open. The
failure is at the connector-to-workspace handoff, after Drive has produced the
export.

Google's official API docs make two separate guarantees. `files.export` returns
the exported bytes directly and that response is limited to 10 MB. The
`files.download` long-running operation also supports exporting Workspace
documents, including Slides as PDF; it returns an operation and ultimately a
download URI, which the client must retrieve. Google documents polling with
backoff for long-running exports. The connected tool contract specifically
says `include_base64: false` uses `files.download`, that this route is not
subject to the `files.export` 10 MB limit, and that it returns a user-scoped
`file_uri` without inline bytes. Neither Google's API documentation nor the
tool contract promises that this URI will appear as a local `workspace_path`.
So the known cause of the missing path is the transfer/materialization
boundary, not PDF size. The 10 MB cutoff applies to direct `files.export`; the
separate LRO route is the documented option for larger exports. This does not
prove that an LRO export can never fail for another reason. See Google's [export
method](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/export),
[download/export guide](https://developers.google.com/workspace/drive/api/guides/manage-downloads),
[long-running operations guide](https://developers.google.com/workspace/drive/api/guides/long-running-operations),
and [files.download method](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/download).

The connected tool surface exposes `google_drive_fetch` and
`google_drive_export_file`, but no separate `operations.get` or
`file_uri`-to-workspace materialization action. Therefore the API-level path
is documented, while completion of the final local transfer still depends on
the connector/helper or the authenticated browser. Google's long-running
operation guide says both `files.download` and `operations.get` consume normal
Drive API quota and recommends polling with backoff (for example, ten-second
intervals). Save the operation name and poll it; do not start a duplicate
export just to check progress.

Use this no-curl recovery order, with one export/fetch per deck revision:

1. For a PDF known to be below 10 MB, call the export/render helper once and
   wrap only `google_drive_fetch` to set `include_base64: true`. Do not wrap
   `exec_command` with a generic wait/poll function; the helper uses a TTY
   receiver that must return immediately to accept PDF chunks. Example:

   ```js
   const fetchName = "mcp__codex_apps__google_drive_fetch";
   const smallPdfTools = {
     ...tools,
     [fetchName]: (args) => tools[fetchName]({ ...args, include_base64: true }),
   };
   const result = await exportAndRenderSlides({
     presentationId, outputDir, workspaceRoot, skillRoot,
     pdftoppmPath, dpi: 120, tools: smallPdfTools,
   });
   ```

   This uses the authenticated connector response and local chunk receiver;
   it makes no shell/network request. Never print or persist the base64. The
   verified small-PDF use cases are recorded below.
2. For a PDF over 10 MB, use the documented `files.download` long-running
   operation route with `include_base64: false`, polling only a returned
   operation with backoff. The connector may return a `file_uri` without a
   local `workspace_path`; this session has no separate materializer for that
   URI. The over-10-MB local transfer is still unverified. If it cannot be
   materialized through the supported helper, use the authenticated browser
   **File → Download → PDF** path or paced native thumbnails and record the
   limitation. Never use a shell downloader.
3. Do not split a source deck or topic to fit the 10 MB direct-export cap.
   Choose batch boundaries from complete source decks and topics, and measure
   import/review needs separately.

The streamed handoff was rechecked on November 24, 2026 against Part 2 rev2.
A fetch with `include_base64: false` returned a 9,898,674-byte PDF as a
`file_uri`, with no local `workspace_path`; streaming works but does not
always materialize a local file. The no-curl solution was then verified on
rev3: one export-and-render-helper fetch with the wrapper above returned a
9,899,270-byte PDF, which the helper wrote locally and rendered to 232 pages.
Do not retry the stream or issue a second export merely to recover that render.

On November 25, 2026, the same `include_base64: false` path again returned a
file reference without `workspace_path` for the four-slide Round 12 rev2
pilot. This is consistent with the option's contract, not a size failure. A
single explicit bounded compatibility fetch with `include_base64: true`
returned the 74,585-byte PDF; the helper's chunk receiver wrote it locally,
and Poppler rendered four pages. The payload was not printed or persisted.
This confirms the small-file compatibility path only. The official LRO route
for a >10 MB Google Slides PDF is documented but has not been tested through
this connector and local materializer. A separate large-file test is not a
project gate. Aim for batch PDFs below 10 MB where whole-topic boundaries
naturally allow; if an actual complete batch exceeds the direct export limit,
use the LRO or authenticated-browser route for that batch. Keep source
decks/topics whole.

For Round 13 (November 25), the known `include_base64: false` behavior was
avoided rather than triggering a second export: the export/render helper was
wrapped for one `include_base64: true` fetch because the local 1.5 MB PPTX was
a small pilot. It returned a 1,017,750-byte Google PDF; the helper wrote it
through its bounded chunk receiver and rendered 62 pages. Native order
readback also returned 62 slides. No payload was printed, no shell network
client was used, and no retry/export loop occurred. This strengthens the
verified small-PDF path; it does not test the >10 MB LRO handoff.

For Round 14 (November 25), a direct `export_file` call and then a
`include_base64: false` fetch both returned file references without a local
`workspace_path`. Because the PDF was known to be below 10 MB, one explicit
compatibility fetch through the documented helper wrapper with
`include_base64: true` materialized the 942,081-byte PDF locally. The helper
rendered all 28 pages; no shell downloader or retry loop was used. This
reconfirmed the small-file route but also used more Drive calls than necessary
because the first direct export/stream attempt preceded the bounded fallback.
For future PDFs known to be below 10 MB, use one helper fetch with
`include_base64: true` from the start. Reserve `include_base64: false` for the
larger-download route and verify how the connector delivers its result.

Round 15's first local PDF attempt stalled because an `exec_command` wrapper
waited for the helper's TTY receiver session to finish before returning
control. The helper was waiting for that receiver to accept streamed PDF
chunks, so both sides waited. The corrected run removed the generic wait
wrapper and retained only the `google_drive_fetch` base64 option wrapper. It
materialized a 4,916,129-byte Google PDF and rendered 38 pages in about
44 seconds. This demonstrates a helper/TTY handoff issue, not a PDF-size
failure. Do not poll the helper's TTY receiver inside the wrapper; for a
separate non-TTY command that returns a `session_id`, polling with
`write_stdin` remains appropriate.

For Round 16 (November 26), the helper's default `include_base64: false`
fetch again returned a file reference without a local `workspace_path`. The
known small-file route was used once for the final 4,944,273-byte PDF: wrap
only `google_drive_fetch` to set `include_base64: true` and let the helper
write the PDF through its bounded receiver. The export produced a valid
38-page PDF without `curl` or another shell network client.

The same run exposed a separate local-renderer timeout symptom. The helper
reported `pdftoppm failed:` with no diagnostic text after 35 page images had
appeared; the PDF itself was intact, and all 38 images appeared after the
renderer finished. The last pages were also rendered directly from that
saved PDF. The likely cause is that a 38-page 120-dpi render exceeded the
helper's 30-second `exec_command` yield window, so the helper saw no completed
exit code while Poppler continued writing files. This is an inference from
the saved PDF and image set. On this error, check the PDF with `pdfinfo`, count
the existing page images, and render only missing pages locally. Do not make
another Drive export call unless the deck has changed. This renderer behavior
does not require `curl` and is separate from the missing `workspace_path`
issue.

Historical pilot logs mention a bounded base64 transfer for small files.
That is now a supported helper path only below the standard export limit;
never print or persist the encoded payload. See the current
[Google Drive export/download reference](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/export)
and [files.download reference](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/download).

## Upload or export in the browser

1. Open the CS 408 test folder in Drive while signed in to the connected
   account. Upload the local PPTX with **New → File upload**.
2. Open the uploaded file in Google Slides and choose
   **File → Save as Google Slides** to create the native deck. Confirm
   that the new deck is in the intended folder and that its slide count
   and order match the local map. Record the new deck's link.
3. In the native deck, choose **File → Download → PDF Document**. Save
   the file beside the local PPTX and use the round's Google PDF filename.
   Use this same download step if the connector already created the
   native deck and only PDF materialization failed.
   [Google's PowerPoint import guide](https://support.google.com/docs/answer/9310378)

## Verified live text edits

Two separate checks establish that the connected Slides tools can edit native
text and read the result back. This is a narrow capability check: it does not
prove that every object type or visual repair is editable.

### Reversible check on a disposable copy

On November 24, 2026, a disposable copy of the Round 10 pilot was used to
replace one exact sentence with a temporary `[LIVE EDIT TEST]` marker using
the Slides `replaceAllText` request scoped to page object `p2`. The connector
reported one occurrence changed; a read of the same slide found
the marker. The text was then restored with a second exact replacement, and
readback confirmed the original sentence was present once and the marker was
absent. The Round 10 revision 6 deck was not changed by this test.

- [Disposable test copy](https://docs.google.com/presentation/d/1Ug0_a1ZWRf_dV9IpQFy61QKHl7mUHFjjTwRG-KDwxyQ/edit?usp=drivesdk)
- Target was slide object `p2`; the temporary marker was
  `Coverage criteria [LIVE EDIT TEST] define a set of test requirements`.
- The copy was restored to its starting text and left in the shared test
  folder as evidence.

### Requested edit on Round 4

The user then requested a live edit of `cs408-editable-part-01-round4`:
`Instructor: Ben Delaware` → `Instructor: Antonio Bianchi [TODO]`. On
November 24, 2026, the outline placed that text on slide 3, “Administrivia,”
with slide object ID `p2`; outline slide 2 was titled “How” and did not contain
the instructor line. The unique quoted text was used to identify the target.
Only the name substring was replaced using `replaceAllText`, scoped with
`pageObjectIds: ["p2"]`, preserving the adjacent `Instructor:` label. The
update was guarded by `writeControl.requiredRevisionId` set to the fresh
revision `5fo0mb0mhrn8ag`; Google reported `occurrencesChanged: 1` and
returned new revision `NTdMS4sqQbmi2g`. A readback of `p2` at that revision
showed `Instructor: Antonio Bianchi [TODO]` once and `Ben Delaware` zero
times. The user confirmed the edit worked.

- [Round 4 deck](https://docs.google.com/presentation/d/1RsGbPcJJZucpjhRbT1-K3cIYqyC25hCHmqqqOSDw1A8/edit)
- This was an intentional edit to the requested Round 4 deck, not the
  disposable test copy. It was a text-editing test, not a conversion repair.

### Reusable procedure and limits

1. Read the presentation outline and find the target by both content and
   slide position. Do not infer a slide number from a page object ID: the
   Round 4 `p2` object is slide 3, not slide 2. If the stated slide number
   and unique quoted text disagree, report the mismatch and scope the edit
   to the slide containing the exact text.
2. Read the target slide and confirm the exact text, object, and current
   presentation revision. Prefer replacing the smallest unique substring
   when the surrounding text has different styling; scope the request to
   the target slide's `pageObjectId`.
3. Supply `writeControl.requiredRevisionId` from the fresh read so concurrent
   changes fail safely. Stop if `occurrencesChanged` is not exactly one.
4. Read the same slide again and verify the expected new text and absence of
   the old text. Record the new revision. For a conversion experiment, use a
   disposable copy and restore the test edit before handoff.
5. Keep API calls serial, with at least five seconds between calls for this
   project; wait longer after a slow response. Both text-edit tests used this
   pacing and produced no rate-limit errors.

The tested path proves direct text replacement and exact text readback. It
does not establish safe editing/readback of arbitrary geometry, freeform
paths, image crops, tables, equations, speaker notes, or visually complex
text styling. One imported arrow's position was separately tested below.
Continue testing each object and operation separately in disposable copies.
Record visual fidelity and editability as separate results. To carry a repair
forward, encode its equivalent in the local PPTX or rebuild script so it can
be reproduced on the next import.

## Verified native vector object edit

On November 24, 2026, a disposable copy of Round 11 revision 4 was used to
test whether a native imported arrow could be moved and restored through the
connected Slides API. The original Round 11 deck was not edited.

For future request construction, use Google's official references for
[`presentations.batchUpdate`](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/batchUpdate),
[Slides request types](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request),
and [transform operations](https://developers.google.com/workspace/slides/api/samples/transform).
The requests below document what this imported object accepted in this test;
they do not imply that every imported object supports the same updates.

- [Disposable Round 11 copy](https://docs.google.com/presentation/d/11gVpZXWyDeTdO7fX1706q5QMS0NlUwhQraFWIju4h_o/edit?usp=drivesdk)
- Copy ID: `11gVpZXWyDeTdO7fX1706q5QMS0NlUwhQraFWIju4h_o`.
- Target slide object: `p2`; initial read revision: `kYc4KVdsm219nw`.
- The slide read back with 33 page elements: 25 shapes and 8 line elements.
  The first orange arrow was `p2_i239`, with transform
  `scaleX=0.04`, `scaleY=0.04`, `translateX=9640391`,
  `translateY=6578798`, `unit=EMU`, and line color `#DD5F36`.

The exact sequence and result:

1. `updateLineProperties` attempted to change the arrow to magenta with
   `writeControl.requiredRevisionId=kYc4KVdsm219nw`. Google returned HTTP 400
   `INVALID_ARGUMENT`: “The object (p2_i239) is not of type LINE.” No change
   was made. The object appeared as a line in readback, so this failure is
   specific to that imported object's compatibility with this update request;
   it does not establish that all line-style edits fail.
2. `updatePageElementTransform` then translated the arrow's X position by
   12,700 EMU (1 pt), using the current revision. Google accepted the write
   and returned revision `e1sT3Ii-0741og`; readback showed the new X position
   `9653091`.
3. A second `updatePageElementTransform`, guarded by that new revision,
   restored the exact original transform. Google returned revision
   `I_JE2Y1ZB-JetQ`; final readback confirmed the original X/Y transforms and
   orange line style.

The reversible position edit and readback passed. The style update did not.
For future geometry edits, use a disposable copy, read the current object and
presentation revision, preserve the full original transform, guard writes
with the fresh revision ID, and read back after both the change and restore.
Keep API calls serial with at least five seconds between calls; this test
used at least 5.5 seconds and produced no rate-limit response. The copy is
restored and remains in the shared test folder as evidence.

## Part 2 scale import and PDF transfer

On November 24, 2026, the 232-slide editable Part 2 PowerPoint
(`combined slides 261–492`, 16,401,836 bytes) was imported once to the shared
test folder using the native Google Slides conversion flow. The returned
presentation ID is `1CFsmvh6YcpiNkJJye8NR0fP2c_ScFlEAXSc8Mm9Yj3k`:

- [Part 2 scale-validation deck](https://docs.google.com/presentation/d/1CFsmvh6YcpiNkJJye8NR0fP2c_ScFlEAXSc8Mm9Yj3k/edit)

A readback with `presentationId,title,slides(objectId,pageElements(objectId))`
returned 232 slides, object IDs `p1` through `p232`, in order. The slides
contain a range of editable imported objects, not one full-slide picture per
page. This confirms native import and structural count/order only.

The original Google PDF export returned a 9,478,484-byte file reference and
extracted text. Rev2's streamed fetch returned 9,898,674 bytes without a local
path. Rev3 was imported and verified in the same `Pilots` folder:

- [Rev3 native Google deck](https://docs.google.com/presentation/d/1OTrLWNKqwFOokESPsZuoBoqWI6Qjm-7IxiSmsa0f50I/edit)
- [Rev3 Google PDF](google-slides-pilot/cs408-editable-part-02-scale-rev3-google.pdf)
- [Rev3 source map](google-slides-pilot/cs408-editable-part-02-scale-rev3-map.csv)
- [Rev3 page-by-page visual diff](google-slides-pilot/cs408-editable-part-02-scale-rev3-visual-diff.csv)
- [Panel repair script](google-slides-pilot/repair_part02_contrast_panels.py)

The native readback returned exactly 232 ordered slides, `p1`–`p232`, and
confirmed editable body text on local slides 214 and 216 with white fill
alpha 0.7019608. The rev3 Google PDF has 232 pages. Compared with rev2 at
854 × 640 pixels, 230 pages are pixel-identical; pages 214 and 216 are the
only changes. Both were visually reviewed and their translucent panels now
match the source contrast while keeping text editable. Part 2 visual review
is complete; its scale import remains a pilot, not a final course batch.

The import, structural readback, and PDF export were serial; no rate-limit
response occurred. The resulting deck is a scale-validation artifact, not
one of the final course batches. The whole-topic source choices are complete;
the remaining work is the 16-batch boundary outline and sequential batch
conversion, animation-state handling, and page-by-page verification.

## Pilot and final-batch folder organization

Keep local pilots under
[`combined/google-slides-pilot/`](google-slides-pilot/README.md), and local
final-candidate batches directly in `combined/`. The editable batch manifest
is `combined/editable-parts-manifest.json`.

In Google Drive, use the shared CS408 folder
[`16vTRNocHa1rlPN1bii_w0b8Ce90XrFbn`](https://drive.google.com/drive/folders/16vTRNocHa1rlPN1bii_w0b8Ce90XrFbn)
for final batches. Keep pilot imports, revisions, and disposable edit tests in
its [`Pilots` subfolder](https://drive.google.com/drive/folders/1PHuKHahwY2PxviNWTM2f8kYmb7K-37Dj).
On November 24, 2026, all 17 presentations in the shared root were confirmed
to be pilots or test copies; their parent metadata was read before they were
moved into `Pilots`. New pilot rounds follow the same organization; final
batch decks stay at the shared root, one level above `Pilots`. Upload and
complete Batch 1 there before starting Batch 2; continue in order through all
16 batches. Each final batch must pass its native readback and Google PDF
page review before beginning the next. Do not place a completed batch deck in
`Pilots`.
