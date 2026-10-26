# Lab 2 handout

- [Read the Markdown edition on GitHub](index.md).
- [Open the standalone HTML edition](index.html) in a local browser, or serve it with GitHub Pages.

`index.md` is the content source. `template.html` and `assets/` provide the light,
responsive layout and three SVG diagrams. The page uses local assets only. It has
no CDN, tracking, web font, or front-end build tool. The small JavaScript file adds
navigation, code copying, and an interactive scoring example. The text and figures
remain available without JavaScript.

From `labs/lab2/skeleton/`, after setup and activation:

```bash
python ../handout/build.py
```

This rebuilds `index.html`, copies the public `baselines.json`, and synchronizes the
selected historical score tables in `index.md` and the skeleton README. It does
not run the agent, regenerate tests, or read TA reference fixes. Edit the Markdown
source for narrative changes. Edit `skeleton/baselines.json` only when intentionally
revising the documented score selection. Its source hashes preserve provenance.

A portable site can be built into a new directory:

```bash
python ../handout/build.py --output /tmp/lab2-pages
python -m http.server 8000 --directory /tmp/lab2-pages
```

Open `http://localhost:8000`. Direct `file://` viewing of `index.html` also works.

## GitHub rendering and publishing

GitHub's repository code browser renders Markdown, but shows HTML as source.
It cannot be made to serve a repository HTML file as a website. The Markdown
edition provides a readable page without configuring hosting.

For the full UI, the prepared `Publish Lab 2 handout` workflow builds a GitHub Pages
artifact containing only `index.html`, local assets, public baseline metadata,
and `.nojekyll`. It does not publish the TA repository or the skeleton's source.

In the publishing repository, choose **Settings → Pages → Source: GitHub Actions**.
Run **Actions → Publish Lab 2 handout → Run workflow** on the branch to publish.
The deployment job provides the URL. The workflow is deliberately manual; adding
or editing course files does not publish them automatically. No Pages settings,
remote commits, or deployments are changed by the local build.

If a semester repository uses another directory layout, update the handout path in
the workflow when generating that repository. Preserve the mini-swe-agent Git
submodule mapping when generating the student skeleton.

The Pages workflow is supplied as `pages-workflow.yml`. To enable publishing, a maintainer with GitHub workflow permissions can copy it to `.github/workflows/lab2-handout.yml`. It is not installed or triggered automatically.
