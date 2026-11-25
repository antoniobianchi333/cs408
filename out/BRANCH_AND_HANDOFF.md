# Branch and restart-kit policy

**Purpose:** keep the Git branch small enough to use and complete enough that a
new agent can restart the conversion work with this repository and access to
the documented Google Drive folder.

## Branch facts

The active branch is `spring+2027+bianchi`. It was created from
`origin/fall+2026` at commit `900304aa07d6b7fd75bdef23e5ef8c3fc7115b60`, dated
November 15, 2026. This is the newest of the four pre-existing branch tips
checked on November 25, 2026. The Fall branch contains the Spring 2026 history,
`new-lab2-dev`, and `project1-ai-policy` as ancestors; the lab and Project 1
branches have been merged into Fall.

Local tracking branches have been created for all source branches so that a
plain `git branch` lists the full set:

| Local branch | Upstream/source | Tip checked on 2026-11-25 | Relationship |
| --- | --- | --- | --- |
| `spring+2027+bianchi` | `origin/fall+2026` at creation | `900304aa` | Active restart-kit branch |
| `fall+2026` | `origin/fall+2026` | `900304aa` | Newest source branch; includes merged changes below |
| `spring+2026` | `origin/spring+2026` | `ea36051` | Ancestor of Fall |
| `new-lab2-dev` | `origin/new-lab2-dev` | `6d030b0` | Merged into Fall |
| `project1-ai-policy` | `origin/project1-ai-policy` | `24c05ab` | Merged into Fall |

Branch-tip timestamps and ancestry are facts from this check, not a rule that
branch names predict freshness. For future work, compare commit tips and
ancestry before choosing a base. The `spring+2027+bianchi` branch is a
working name; it does not assert that the content is a finalized Spring 2027
course offering.

## What belongs in Git

Treat this branch as a **restart kit and reproducible workflow**, not a mirror
of every large source or processed slide binary. Add and keep current:

- Every project README, plan, runbook, Drive guide, and handoff note that
  explains the task, source selection, conversion process, QA, upload layout,
  and remaining work.
- Conversion, repair, audit, and manifest-generation scripts needed to
  reproduce a result. Include their inputs/outputs, dependencies, and exact
  invocations in documentation.
- Compact source and output maps, batch manifests, page-to-source/build maps,
  crosswalks, and small machine-readable reports that preserve provenance or
  explain a repair.
- Small representative evidence only when the result cannot be reconstructed
  from the source and the script. Prefer a concise report or crop over a full
  render set.
- Source material required to reproduce the work when it is not already
  available from the chosen base branch or another documented authoritative
  source.

Do not add large generated PDFs, whole-deck PPTX files, repeated pilot
revisions, page-render directories, temporary extracted PDFs, LibreOffice
profiles, or other rebuildable scratch files merely to make the checkout look
complete. Keep temporary material in `out/.build/` and untracked. Keep large
durable processed artifacts in the Google Drive project folder when their
Drive copies have been verified. Store pilots and disposable tests under the
Drive `Pilots` subfolder; reserve the Drive root for final batch decks.

Do not infer that an untracked local file is safely preserved in Drive. Before
relying on a large artifact as handoff storage, confirm its exact Drive file
name, ID, type, parent folder, and size through the connector, then record the
link and evidence in the relevant README/runbook entry. If no verified Drive
copy exists and the artifact is needed to reproduce or review a result, upload
it to `Pilots` before omitting it from Git. Avoid duplicate uploads; inspect
the folder and metadata first, and pace all Drive operations as described in
[`combined/GOOGLE_DRIVE_ACCESS.md`](combined/GOOGLE_DRIVE_ACCESS.md).

## What a restarting agent must be able to do

With this repository and authorized Google Drive access, a new agent should
be able to:

1. Read [`README.md`](README.md) first and follow its links to the live plan,
   branch policy, collection guide, conversion runbook, and Drive guide.
2. Identify the newest authoritative course source and recover Fall lecture
   PDFs from the base branch when needed. The 20 PDFs are in
   `origin/fall+2026:slides/f26-pdfs/`; the current local extraction is
   temporary under `out/.build/fall-source/`.
3. Rebuild pilot/editable candidates using the tracked scripts and maps, then
   verify source order, content, animation states, package integrity, native
   Google Slides structure, and Google-rendered PDF visuals.
4. Find verified durable pilot artifacts in Drive `Pilots` and distinguish
   them from final decks in the Drive root. Use the Drive guide for account
   setup, low-rate API calls, no-curl transfer, and export limits.
5. Continue source reconciliation and full conversion without treating an
   existing pilot, local generated file, or partially uploaded batch as
   project completion.

The root [`README.md`](README.md) is the navigation hub and must link to every
relevant project Markdown file, script, map, and artifact folder. Update that
hub whenever a new durable project document or script is added. Keep
[`PLAN.md`](PLAN.md) synchronized with actual progress and next steps.

## Selected branch payload

The intended Git payload for `spring+2027+bianchi` is all project Markdown
files (including this one), the Python conversion/repair/audit scripts, the
source crosswalk and maps, batch manifest, pilot page maps, and the compact
Part 2 visual-diff report. The large PDFs, PPTX files, and generated page
images remain unadded. The 20-row Fall PDF metadata audit is tracked as
[`combined/fall-source-metadata.csv`](combined/fall-source-metadata.csv).

This inventory is the policy for selecting files, not evidence that every
large local artifact already has a Drive copy. The Google folder must be
checked before a future agent relies on a particular local/Drive artifact.
