# CS408 Lab 2 — Teaching a Coding Agent to Write Tests

This project has three parts: **Warmup**, **Test Writing**, and **Issue Reproduction**.
You write reusable skills. The supplied coding agent uses those skills to write tests.
The agent, model, tasks, and run budgets stay fixed when you compare vanilla and skills.

Read the [course handout](../handout/index.md) for the background and examples.
The handout also has a [standalone HTML edition](../handout/index.html).
All six benchmark tasks are public. There is no separate set of hidden tasks.
TA reference fixes and deliberately faulty implementations are not distributed in this skeleton.

## Set up the environment

Run these commands **from this skeleton directory**:

```bash
bash setup.sh --check          # report status; do not install anything
bash setup.sh                  # install missing tools without sudo or apt
source scripts/activate.sh    # select this machine's Python, gh, and udocker tools
bash setup.sh --check
```

The setup checks Linux architecture, Git, GitHub CLI (`gh`), Python, Python packages,
udocker execution tools, and the presence of `PURDUE_RCAC_API_KEY`. It does not print
secrets. GitHub login is optional for the public source and images. An API key is
required to run the agent, but is not needed to install the environment.

- **Linux ARM64 / aarch64:** runs all seven tasks.
- **Linux x86_64 / amd64:** runs the local Garage Warmup. The current six benchmark
  images are ARM64; setup does not claim that x86 can execute them.
- **Other systems:** use a Linux machine. These scripts do not create a VM or enable
  cross-architecture emulation.

Setup uses an official user-owned `uv` installation and managed Python 3.12. If Git
or required command-line utilities are absent, a user-owned micromamba environment
provides them. No system package manager is used. The GitHub CLI release archive is
checked against its published SHA-256 checksum. Python packages are installed only
in `.venvs/linux-arm64/` or `.venvs/linux-amd64/`.

The project-local `.tools/bin/gh` launcher checks `uname` on **every invocation**.
It selects `.tools/gh/linux-arm64/bin/gh` or `.tools/gh/linux-amd64/bin/gh`.
Setup installs only the current machine's binary. It never replaces
`~/.local/bin/gh`, `~/.local/libexec/gh/`, an existing system `gh`, or the other
architecture's project binary. The shared-home x86 installation remains intact.
Neither setup nor activation edits `.bashrc` or another shell profile.

If the key is not already exported in your shell, set it before a run:

```bash
export PURDUE_RCAC_API_KEY='YOUR_KEY'
```

Keep real keys out of Git, skill files, and reports. The API endpoint is
`https://genai.rcac.purdue.edu/api`. The configured model is `qwen3.8:27b`.
See [Purdue's API documentation](https://docs.rcac.purdue.edu/services/genai/api/).

The official mini-swe-agent is a Git submodule under `vendor/mini-swe-agent`, pinned
to `04d809ceab9df28f9adaed044884180159172930` (2.4.6). Setup initializes it when
needed. If distributing this lab as a new Git repository, preserve the submodule
URL and Git link in that repository's `.gitmodules` as well.

## Part 1 — Warmup: Garage

**Task:** `warmup/garage` · Python · local virtual environment

The supplied `Garage` implementation is correct. Its specification covers vehicle
names, capacity, visits, re-entry, charges, and session history. Read
[`SPEC.md`](tasks/warmup/garage/project/SPEC.md). Extend the starter test file or
add `test_*.py` files. Do not change `garage.py` or the specification.

```bash
python -m lab2 warmup/garage --output outputs/garage-vanilla
python -m lab2 warmup/garage --skills-config skillsets/example.yaml \
  --output outputs/garage-example
```

The second command demonstrates loading the **format example**, not an effective
Garage strategy. Write your own skill and skill-list file for an actual comparison.
No Garage reference skills or reference test suite are provided.

**Practice scoring:** the existing TA Warmup checker runs the suite against the
correct implementation and 21 deliberately faulty versions. The suite must pass
on the correct implementation, and production code must be unchanged. Otherwise
the practice submission is invalid. For a valid suite, its practice score is
`100 × detected faulty versions / 21`. This Warmup feedback is reported separately
and is **not included** in the six-task benchmark mean.

## Part 2 — Test Writing

The supplied implementation is already correct. Add tests that check its behavior.
A test must pass on that implementation and detect a relevant deliberately faulty
version. There is no requirement for a reference repair to turn a failure into a
pass: this is a test-writing task, not a repair-reproduction task.

The following numbers are the **lowest previously scored vanilla test-artifact
scores** selected under the current checkpoint rubric. They are not averages.
See the selection policy below before interpreting them.

<!-- baseline:TW -->
### Maddy — 80.00/100

Write integration tests for sender-based mail routing. Check domains, rejected senders, name normalization, and rule precedence.

**Task:** `test-writing/maddy` · **Checkpoints:** 5 · **Faulty versions:** 5

```bash
python -m lab2 test-writing/maddy
```

<details>
<summary>Detailed selected vanilla score</summary>

| Checkpoint | Max | V | K | Points |
| --- | ---: | ---: | ---: | ---: |
| Route by sender domain | 20.00 | 1 | 1 | 20.00 |
| Normalize qualified sender addresses | 20.00 | 1 | 1 | 20.00 |
| Reject a configured sender | 20.00 | 1 | 1 | 20.00 |
| Apply sender-route precedence | 20.00 | 1 | 1 | 20.00 |
| Normalize unqualified sender names | 20.00 | 0 | 0 | 0.00 |

**Total: 80.00/100.** Each checkpoint is worth exactly `100/5`; displayed values are rounded. The total uses unrounded values.

Selected score record: `results/benchmark-course-skills-v2-r1/vanilla-scores.json`. See `baselines.json` for the evidence hash and other eligible historical scores.

</details>

### MinIO — 68.18/100

Write ETag tests for parsing, equality, multipart aggregation, encrypted tags, and S3 formatting.

**Task:** `test-writing/minio` · **Checkpoints:** 11 · **Faulty versions:** 14

```bash
python -m lab2 test-writing/minio
```

<details>
<summary>Detailed selected vanilla score</summary>

| Checkpoint | Max | V | K | Points |
| --- | ---: | ---: | ---: | ---: |
| Report the accepted multipart count | 9.09 | 1 | 1 | 9.09 |
| Compute the multipart digest | 9.09 | 1 | 1 | 9.09 |
| Exclude ineligible parts from aggregation | 9.09 | 1 | 1 | 9.09 |
| Handle aggregation with no accepted parts | 9.09 | 1 | 1 | 9.09 |
| Recognize encrypted ETags | 9.09 | 1 | 1 | 9.09 |
| Format encrypted ETags for S3 | 9.09 | 1 | 1 | 9.09 |
| Compare equivalent ETags | 9.09 | 0 | 0 | 0.00 |
| Validate multipart part numbers | 9.09 | 1 | 0.5 | 4.55 |
| Validate multipart digest length | 9.09 | 0 | 0 | 0.00 |
| Parse non-strict single-part ETags | 9.09 | 0 | 0 | 0.00 |
| Parse quoted ETags | 9.09 | 1 | 1 | 9.09 |

**Total: 68.18/100.** Each checkpoint is worth exactly `100/11`; displayed values are rounded. The total uses unrounded values.

Selected score record: `results/benchmark-course-skills-v2-r1/vanilla-scores.json`. See `baselines.json` for the evidence hash and other eligible historical scores.

</details>

### k6 — 66.67/100

Write tests for execution segments. Check sequence input, boundaries, striped work allocation, and integer resegmentation.

**Task:** `test-writing/k6` · **Checkpoints:** 12 · **Faulty versions:** 12

```bash
python -m lab2 test-writing/k6
```

<details>
<summary>Detailed selected vanilla score</summary>

| Checkpoint | Max | V | K | Points |
| --- | ---: | ---: | ---: | ---: |
| Format segments consistently | 8.33 | 1 | 1 | 8.33 |
| Handle an empty execution-segment sequence | 8.33 | 1 | 1 | 8.33 |
| Build the correct integer execution tuple | 8.33 | 1 | 1 | 8.33 |
| Compute a shared denominator | 8.33 | 0 | 0 | 0.00 |
| Reject negative segment boundaries | 8.33 | 0 | 0 | 0.00 |
| Parse rational segment values | 8.33 | 0 | 0 | 0.00 |
| Require neighboring segments to meet | 8.33 | 1 | 1 | 8.33 |
| Validate the number of sequence boundaries | 8.33 | 1 | 1 | 8.33 |
| Require increasing boundaries | 8.33 | 0 | 0 | 0.00 |
| Allocate the correct number of striped units | 8.33 | 1 | 1 | 8.33 |
| Compute the striped period | 8.33 | 1 | 1 | 8.33 |
| Compute the striped starting offset | 8.33 | 1 | 1 | 8.33 |

**Total: 66.67/100.** Each checkpoint is worth exactly `100/12`; displayed values are rounded. The total uses unrounded values.

Selected score record: `results/benchmark-course-skills-v2-r1/vanilla-scores.json`. See `baselines.json` for the evidence hash and other eligible historical scores.

</details>

<!-- /baseline:TW -->

## Part 3 — Issue Reproduction

The supplied implementation has a defect or missing feature. The task text states
what should happen. Write tests that fail because of that issue and pass after the
TA's reference repair. You write tests, not the repair. The agent never receives
the reference patch. The upstream issue is quoted as context; any instructions
in it to implement a fix or commit code do not override the tests-only rules.

<!-- baseline:IR -->
### Ansible — 40.00/100

Reproduce archive path traversal during collection extraction. Keep legitimate extraction behavior intact.

**Task:** `issue-reproduction/ansible` · **Checkpoints:** 5 · **Faulty versions:** 5

```bash
python -m lab2 issue-reproduction/ansible
```

<details>
<summary>Detailed selected vanilla score</summary>

| Checkpoint | Max | V | E | K | Points |
| --- | ---: | ---: | ---: | ---: | ---: |
| Preserve checksum validation | 20.00 | 0 | 0 | 0 | 0.00 |
| Keep normalized extraction paths inside the destination | 20.00 | 1 | 1 | 1 | 20.00 |
| Name the offending archive entry in the error | 20.00 | 1 | 1 | 0 | 0.00 |
| Allow a legitimate file directly inside the destination | 20.00 | 1 | 1 | 1 | 20.00 |
| Handle Unicode archive paths | 20.00 | 0 | 0 | 0 | 0.00 |

**Total: 40.00/100.** Each checkpoint is worth exactly `100/5`; displayed values are rounded. The total uses unrounded values.

Selected score record: `results/benchmark-course-skills-v2-r1/vanilla-scores.json`. See `baselines.json` for the evidence hash and other eligible historical scores.

</details>

### psd-tools — 54.52/100

Reproduce the missing typed Blend If API and its effect on stored sliders, layer persistence, and composited pixels.

**Task:** `issue-reproduction/psd-tools` · **Checkpoints:** 28 · **Faulty versions:** 35

```bash
python -m lab2 issue-reproduction/psd-tools
```

<details>
<summary>Detailed selected vanilla score</summary>

| Checkpoint | Max | V | E | K | Points |
| --- | ---: | ---: | ---: | ---: | ---: |
| Apply the black-slider visibility transition | 3.57 | 0 | 0 | 0 | 0.00 |
| Construct a full-range default channel | 3.57 | 0 | 0 | 0 | 0.00 |
| Recognize default channel values | 3.57 | 0.8 | 1 | 1 | 2.86 |
| Describe a channel | 3.57 | 1 | 1 | 0.5 | 1.79 |
| Validate each channel pair count | 3.57 | 1 | 1 | 1 | 3.57 |
| Write color-channel values back to raw storage | 3.57 | 0 | 0 | 0 | 0.00 |
| Validate the composite pair count | 3.57 | 1 | 1 | 1 | 3.57 |
| Write composite values back to raw storage | 3.57 | 0 | 0 | 0 | 0.00 |
| Use source and backdrop in the right order | 3.57 | 0 | 0 | 0 | 0.00 |
| Report the number of color channels | 3.57 | 1 | 1 | 1 | 3.57 |
| Recognize a default container | 3.57 | 0.4 | 1 | 0 | 0.00 |
| Describe a container | 3.57 | 1 | 1 | 0.5 | 1.79 |
| Iterate over all color channels | 3.57 | 1 | 1 | 1 | 3.57 |
| Preserve compositing with default ranges | 3.57 | 1 | 1 | 1 | 3.57 |
| Return full visibility for default ranges | 3.57 | 1 | 1 | 1 | 3.57 |
| Construct a container from explicit channels | 3.57 | 1 | 1 | 1 | 3.57 |
| Construct non-split channels from scalar values | 3.57 | 0 | 0 | 0 | 0.00 |
| Read and persist layer blend-range values | 3.57 | 0.2 | 1 | 0 | 0.00 |
| Produce the correct visibility-mask pixels | 3.57 | 0 | 0 | 0 | 0.00 |
| Support negative channel indices | 3.57 | 1 | 1 | 1 | 3.57 |
| Apply individual color-channel ranges | 3.57 | 0 | 0 | 0 | 0.00 |
| Construct a container from raw range data | 3.57 | 0.6667 | 1 | 1 | 2.38 |
| Decode slider handles from raw integers | 3.57 | 0.8 | 1 | 1 | 2.86 |
| Encode slider handles as raw integers | 3.57 | 1 | 1 | 1 | 3.57 |
| Report whether slider handles are split | 3.57 | 1 | 1 | 1 | 3.57 |
| Expose a typed blend-range property on layers | 3.57 | 1 | 1 | 1 | 3.57 |
| Use backdrop values for underlying-layer sliders | 3.57 | 0 | 0 | 0 | 0.00 |
| Index the first color channel correctly | 3.57 | 1 | 1 | 1 | 3.57 |

**Total: 54.52/100.** Each checkpoint is worth exactly `100/28`; displayed values are rounded. The total uses unrounded values.

Selected score record: `results/benchmark-course-skills-v2-r1/vanilla-scores.json`. See `baselines.json` for the evidence hash and other eligible historical scores.

</details>

### abs — 50.88/100

Reproduce stepped reads and assignments for arrays and strings, including omitted bounds, Unicode, and error handling.

**Task:** `issue-reproduction/abs` · **Checkpoints:** 19 · **Faulty versions:** 19

```bash
python -m lab2 issue-reproduction/abs
```

<details>
<summary>Detailed selected vanilla score</summary>

| Checkpoint | Max | V | E | K | Points |
| --- | ---: | ---: | ---: | ---: | ---: |
| Broadcast one value across selected array positions | 5.26 | 1 | 1 | 1 | 5.26 |
| Assign array values in the selected order | 5.26 | 0.6667 | 1 | 1 | 3.51 |
| Preserve single-index array assignment | 5.26 | 0 | 0 | 0 | 0.00 |
| Report the correct array size-mismatch error | 5.26 | 0 | 0 | 0 | 0.00 |
| Read forward slices using the requested step | 5.26 | 1 | 1 | 1 | 5.26 |
| Preserve an omitted start in the parsed expression | 5.26 | 1 | 1 | 1 | 5.26 |
| Preserve the third slice component in the parsed expression | 5.26 | 1 | 1 | 1 | 5.26 |
| Report non-numeric slice bounds or steps | 5.26 | 1 | 1 | 1 | 5.26 |
| Choose the correct default start for reverse slices | 5.26 | 1 | 1 | 1 | 5.26 |
| Exclude the end position in reverse slices | 5.26 | 0.5 | 1 | 0 | 0.00 |
| Broadcast one character across selected string positions | 5.26 | 1 | 1 | 1 | 5.26 |
| Handle assignment to an empty string range | 5.26 | 0 | 0 | 0 | 0.00 |
| Assign through a negative string index | 5.26 | 0 | 0 | 0 | 0.00 |
| Assign characters in the selected order | 5.26 | 0.3333 | 1 | 1 | 1.75 |
| Require one character for single-index string assignment | 5.26 | 0 | 0 | 0 | 0.00 |
| Preserve negative ends in two-part slices | 5.26 | 0 | 0 | 0 | 0.00 |
| Read Unicode characters rather than bytes | 5.26 | 0.6667 | 1 | 1 | 3.51 |
| Assign Unicode characters rather than bytes | 5.26 | 0 | 0 | 0 | 0.00 |
| Reject step zero with the correct error | 5.26 | 1 | 1 | 1 | 5.26 |

**Total: 50.88/100.** Each checkpoint is worth exactly `100/19`; displayed values are rounded. The total uses unrounded values.

Selected score record: `manual-mutation-scenario-v3.json`. See `baselines.json` for the evidence hash and other eligible historical scores.

</details>

<!-- /baseline:IR -->

## How benchmark scores work

Every benchmark task receives **one score out of 100**. Its behavior is divided
into checkpoints. A checkpoint concerns one behavior, such as rejecting an invalid
path or treating an empty input correctly. All checkpoints within one task have
equal weight. Some checkpoints have more than one deliberately faulty version;
those versions have equal weight within that checkpoint.

| Symbol | Meaning |
| --- | --- |
| `N` | Number of checkpoints for this task. Each is worth `100/N` points. |
| `V` | Fraction of a checkpoint's submitted independent checks that have a correct expected answer and pass on the correct implementation. |
| `E` | IR only: among those correct checks, the fraction that meet the required before/after behavior. |
| `K` | Fraction of that checkpoint's faulty versions detected by eligible correct checks. |

- **TW:** checkpoint points = `(100/N) × V × K`.
- **IR:** checkpoint points = `(100/N) × V × E × K`.
- Add checkpoint points to obtain the task's score. No checks for a checkpoint
  means zero points there. If `V=0`, that checkpoint contributes zero.
- An IR bug check must fail on the supplied code and pass on the corrected code.
  A preclassified check of existing correct behavior must pass on both. A new bug
  check that happens to pass the supplied code is not relabeled as an existing
  behavior check to gain credit.
- A correct independent check can earn credit even if another check in the same
  test function is wrong. The TA may isolate checks for diagnosis without changing
  their inputs, setup, or expected answers. Wrong checks still receive no credit.
- A timeout, missing dependency, collection failure, or unrelated crash is not by
  itself proof that a behavioral requirement was tested correctly. Reference
  tests validate the faulty versions before they are used for scoring.

For example, suppose an IR checkpoint is worth 20 points. Three of four submitted
checks are correct (`V=3/4`). Two of those three satisfy the required before/after
behavior (`E=2/3`). They expose one of two relevant faulty versions (`K=1/2`).
The checkpoint receives `20 × 3/4 × 2/3 × 1/2 = 5` points. For TW, leave out `E`.

The six tasks use **80 checkpoints and 90 approved faulty versions** in total.
The benchmark mean is the arithmetic mean of the six task scores. Warmup is
separate. There is no public/hidden-task weighting. A score of 100 means all
checks in this finite rubric were satisfied; it is not a proof that a test suite
will detect every possible programming mistake.

### Historical vanilla selection policy

Vanilla means skills are disabled, not that an empty skill list is selected.
For each task, the tables above select the minimum among the available previously
scored vanilla artifacts under **scenario-v3**, using the same approved faulty
versions and checkpoint weights. Skill-assisted runs, incomplete candidate-only
outputs, no-test timeout attempts, and superseded scoring formulas are excluded.
The old 30-minute abs run that produced no tests is therefore not reported as a
0-point test suite. Ties prefer the newer score record.

The selected six-task mean is **60.04/100**. This is a set of historical minima,
not one matched six-task run, an expected vanilla score, or evidence of a stable
improvement. Historical runs used different transport/time settings. The current
runner uses two hours and non-streaming requests. Inspect `baselines.json` for
unrounded checkpoint values, candidate scores, the selection rule, and evidence
hashes. Reference fixes, generated test bodies, and faulty source patches are
not included in that file.

The historical psd-tools minimum was accepted by the older file collector, but
its run also changed Git history. That protocol problem was recorded separately;
the frozen test-quality score was not retroactively changed. The current runner
rejects Git-history changes. Historical quality scores do not certify compliance
with every current submission rule.

## Write and select skills

```text
skills/                         # student-authored skill directories
  example/
    skill.yaml                  # format only; no task-specific strategy
    references/format.md
skillsets/
  example.yaml                  # selects ../skills/example
```

Every skill needs `name`, `description`, and `instructions`. The name must be
unique in the selected list. The initial prompt includes only the name,
description, and file location. The agent reads instructions and supporting
files when needed. These files are not executable plugins.

Each skill-list YAML selects directories. Paths are relative to the list file:

```yaml
skills:
  enabled:
    - ../skills/my-skill
    - ../skills/another-skill
```

Create multiple files under `skillsets/` to compare different combinations.
Omitting `--skills-config` disables skills entirely. No vanilla list file is needed.

```bash
python -m lab2 test-writing/minio --output outputs/minio-vanilla
python -m lab2 test-writing/minio --skills-config skillsets/my-list.yaml \
  --output outputs/minio-skills
python -m lab2 issue-reproduction/ansible --skills-config skillsets/my-list.yaml \
  --output outputs/ansible-skills
```

Use a new output directory for every run. The runner refuses to overwrite an old
run. Do not edit the adapter, the official agent, protected source, dependencies,
or Git history to improve a score. Only the Garage starter test is explicitly
editable; benchmark tasks require new test files in their listed directories.

## Runs, records, and submission

Both arms use the same model, temperature 0, 60-call limit, and two-hour agent
time setting. No output-token cap is set by this runner. The provider may impose
its own context/output limits. The official agent checks elapsed time **between**
model calls, so a long active request can exceed the nominal time setting.
Non-streaming transport can also encounter a server-side gateway timeout.
Such a request is recorded as incomplete and is not silently retried.

A run saves:

| Path | Contents |
| --- | --- |
| `submission/` | Automatically collected new or permitted starter test files. No agent-written manifest is required. |
| `trajectory.json` | Agent messages, tool actions, observations, configuration, and exit status. |
| `model-requests.jsonl` | Request attempts and provider-reported usage, including rejected tool responses. |
| `raw-model-responses/` | Original responses saved before tool parsing. |
| `usage-summary.json` | Input, output, reasoning, and reported cache token counts. |
| `result.json` | File-integrity checks, submission status, elapsed time, and usage summary. |
| `skills/` | Snapshot and hashes of enabled skills, if any. |

Input tokens count every request, including repeated conversation history.
Output tokens already include reasoning tokens; do not add reasoning a second
time. Missing token usage is an error, not zero. Missing cache counts remain
unknown. Monetary cost is not calculated for this locally deployed model.
`valid_submission` reports file/protocol acceptance; it does not mean that all
tests are correct or that the task scored 100. Scoring happens on the TA side.

Submit your own skill directories, selected skill-list files, generated test
artifacts, trajectories/usage records, and a short comparison of what improved
and what still failed. Keep vanilla and skill-assisted outputs separate. Report
all attempts you use in the comparison, not only a favorable pair.

## Layout

```text
adapter/        Purdue RCAC model, udocker environment, and skill loading
lab2/           python -m lab2 entry point
vendor/         pinned official mini-swe-agent submodule
scripts/        user-owned setup and architecture-aware activation
skills/         student-authored skills; only a format example is supplied
skillsets/      selectable skill-list YAML files
tasks/          warmup/, test-writing/, issue-reproduction/
baselines.json  historical minimum scores and checkpoint evidence metadata
tests/          adapter and environment checks
```

## Environment references

- [uv installer options](https://docs.astral.sh/uv/reference/installer/)
- [uv Python storage](https://docs.astral.sh/uv/reference/storage/)
- [udocker installation](https://github.com/indigo-dc/udocker/blob/master/docs/installation_manual.md)
- [GitHub CLI releases](https://github.com/cli/cli/releases)
- [mini-swe-agent source](https://github.com/SWE-agent/mini-swe-agent)
