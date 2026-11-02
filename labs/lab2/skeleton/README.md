# CS408 Lab 2: Teaching a Coding Agent to Write Tests

You write *skills*: reusable instructions that a fixed coding agent (mini-swe-agent
with the course model) reads while it writes tests. You compare runs with your
skills against vanilla runs (no skills) on the same tasks. The agent, the model,
the tasks and the run limits are the same for everyone. The course handout gives
the background, the deliverables and the deadlines.

## Tasks

`python -m lab2 tasks` lists them.

| Task | Type | Language | Public checkpoints | The agent must... |
| --- | --- | --- | ---: | --- |
| `garage` | warmup | Python | 15 | extend `test_garage.py` for a parking-garage class (plates, capacity, sessions, charges, passes) from `SPEC.md` |
| `paperless` | test-writing | Python | 12 | test `generate_filename` of paperless-ngx (document type, ASN, tag and date placeholders, path separators) |
| `minio` | test-writing | Go | 8 | test MinIO's `internal/etag` package (parsing, equality, multipart, encryption, S3 formatting) |
| `k6` | test-writing | Go | 9 | test k6 execution segments (sequences from strings, striped offsets, shared properties, new execution tuples) |
| `dateutil` | issue-reproduction | Python | 25 | reproduce RFC 5545 timezone interoperability of `dateutil.rrule` (RDATE TZID/VALUE, timezone-aware `__str__`, iCalendar output, set operations) |
| `psd-tools` | issue-reproduction | Python | 20 | reproduce a typed blend-range ("Blend If") API for layers and its use in compositing |
| `abs` | issue-reproduction | Go | 14 | reproduce stepped slices `value[start:end:step]` for arrays and strings in the ABS language |

- **Test writing** (and the warmup): the supplied implementation is correct. The
  tests must pass on it and catch faulty versions of it.
- **Issue reproduction**: the supplied code lacks a feature or fix described in an
  upstream issue. The tests must fail on the supplied (unfixed) code and pass once
  a correct repair is applied. The agent must not implement the repair.

The six test-writing and issue-reproduction tasks are the benchmark. The warmup
is practice and is not part of the benchmark mean. Each task's prompt is
`tasks/<type>/<id>/prompt.md`. The agent may add test files only in the task's
`test_paths` (`task.yaml`), and may edit only the starter tests listed under
`editable` (only the warmup has one, `test_garage.py`).

## Setup

Run all commands from the root of your repository, in Bash.

```bash
bash setup.sh --check        # report what is installed; changes nothing
bash setup.sh                # install everything under .tools/ and .venvs/ (no sudo)
source scripts/activate.sh   # in every new shell
```

`setup.sh` installs uv and Python 3.12 under `.tools/`, git and basic utilities
when missing, the pinned mini-swe-agent and Harbor (`vendor/`) and the other
requirements into `.venvs/<platform>/`, the udocker engines, and tectonic (a
self-contained LaTeX engine, for the report). It does not touch anything outside
the repository or edit your shell profile.

**Machine.** The six benchmark tasks run in ARM64 container images, so they need
Linux ARM64 (aarch64). On Linux x86_64 only the warmup runs.

**Images.** Download the six image archives (`<id>-arm64.tar.gz`, named in each
`task.yaml` under `environment.archive`) and put them into `images/`. The first
run of a task loads its archive into the udocker image store,
`.cache/udocker/` by default (several GB; set `LAB2_IMAGE_STORE` to another
folder if space is short). Once loaded, the archive is not needed any more.

**API key.** Runs call the Purdue RCAC GenAI API (`https://genai.rcac.purdue.edu/api`,
model `qwen3.8:27b`). The key is read from `PURDUE_RCAC_API_KEY`. Keep it out of
git, skills and reports. The lab2 process makes itself unreadable to the agent's
commands (Linux `prctl`), and credential-like variables (`*KEY*`, `*TOKEN*`,
`*SECRET*`, `*PASSWORD*`) are removed from their environment. A shell that has the
key exported is still readable by processes of your user, so pass it only to
the command:

```bash
PURDUE_RCAC_API_KEY=$(cat ~/.purdue-rcac-key) python -m lab2 run --alias A --tasks garage
```

**Sandboxing.** Image tasks run in rootless udocker containers. The warmup runs
on the host, without a sandbox: the agent's commands run as your user in a
temporary git workspace copied from `tasks/warmup/garage/project/`, and they can
reach your files. Run it on a machine and account where that is acceptable.

## Command line

```
python -m lab2 tasks
python -m lab2 run    --alias A --tasks ID [ID ...] [--skills NAME [NAME ...]] [--redo-existing]
python -m lab2 eval   --alias A --tasks ID [ID ...] [--checkpoints FILE [FILE ...]]
python -m lab2 submit --alias A --type {warmup,test-writing,issue-reproduction} [--resubmit-existing]
python -m lab2 scoreboard
```

An **alias** names a set of runs (`jobs/<alias>/`). It matches
`[A-Za-z0-9][A-Za-z0-9._-]*`. `submission` and `vanilla` are reserved, in any
letter case: `run` and `submit` refuse them. All arguments are checked before
anything runs. An error prints `error: ...` and exits with status 2. `run` exits with
status 1 if a task ended with an error; that task's `run.json` records it.

**`run`** runs the agent once per task and writes `jobs/<alias>/<id>/`.

- `--tasks`: task ids (`python -m lab2 tasks`).
- `--skills`: folder names under `skills/` (not paths). Omit it for a vanilla run.
- `--redo-existing`: replace existing jobs of this alias. Without it, `run`
  refuses to start if any named task already has a job under the alias.
- The tasks run one after another: each run holds a full container copy, and the
  machine's shared temporary storage serves every student at once.
- `run` and `eval` first remove containers and temporary folders left behind by
  killed runs or evaluations (only those of processes that no longer exist).
- Errors: invalid or reserved alias, unknown task, unknown or duplicate skill,
  invalid `SKILL.md`, existing jobs, an image that is neither loaded nor present
  in `images/`.

Each run goes through Harbor: the agent works in a fresh environment, then the
accepted test files are collected and evaluated in another fresh environment with
the task's public checkpoints (`eval.json`). If a task fails (agent, Harbor or
evaluation error), its `run.json` still records the parameters and the error,
and the other tasks go on. The CLI prints one summary line per task and the
first line of each error.

**`eval`** re-evaluates saved jobs in a fresh environment and rewrites their
`eval.json`.

- `--checkpoints FILE ...`: checkpoints files to use instead of the task's
  public `checkpoints.json`. Several files are concatenated; checkpoint ids must
  be unique.
- `--alias submission` evaluates `jobs/submission/<type>/<id>/`.
- Errors: no job for a task under the alias, `--alias vanilla` (the shipped jobs
  are read-only; copy one to your own alias first), a checkpoints file that does
  not exist, belongs to another task or lacks the required keys, duplicate ids.

**`submit`** copies `jobs/<alias>/<id>/` of every task of one type to
`jobs/submission/<type>/<id>/` and writes `jobs/submission/<type>/submission.json`
(alias, tasks, skills, time). All tasks of the type must have run with the same
skills (identical `skills/` snapshots in their jobs, or no skills).

- `--resubmit-existing`: replace an existing `jobs/submission/<type>/`. Without
  it, `submit` refuses.
- Errors: invalid or reserved alias, a task of that type without a job under the
  alias, jobs of that type that used different skills.

**`scoreboard`** prints the score in `eval.json` of every alias (`jobs/<alias>/`,
vanilla first; not `submission`) on every task, plus `TW mean` (paperless, minio,
k6) and `IR mean` (dateutil, psd-tools, abs), each when all three tasks of that
part have a score. `–` marks a task without a job,
`no eval` a job without `eval.json`, `checks` an `eval.json` without a score.

## Skills

A skill is a folder `skills/<name>/` with a `SKILL.md` and optional supporting files:

```markdown
---
name: my-skill
description: When the skill is useful (shown to the agent at the start).
---

# Instructions the agent reads when it decides the skill is relevant
```

- `name` must equal the folder name: lowercase letters, digits and `-`.
- `description` and the instructions must not be empty. Symbolic links are not allowed.
- The initial prompt lists only the names and descriptions. During the run the
  selected skills are at `.skills/<name>/` in the task's working directory, and the
  agent reads `SKILL.md` and other files with bash when needed.
- Select skills with `run --skills my-skill other-skill`. A run without
  `--skills` is a **vanilla** run.

`skills/example/` shows the format only; it is not a testing strategy.

## Jobs

`jobs/<alias>/<id>/` holds one run:

| File | Contents |
| --- | --- |
| `run.json` | Run parameters and outcome (below) |
| `trajectory.json` | The mini-swe-agent trajectory; `info.lab2` holds a copy of `run.json` |
| `model-requests.jsonl` | One row per model request attempt, with token usage |
| `prompt.md` | The exact task prompt given to the agent |
| `config.yaml` | The agent and model configuration used |
| `skills/` | Snapshot of the selected skills (absent for vanilla) |
| `submission/` | The accepted test files |
| `eval.json` | The evaluation with the public checkpoints |

`run.json` records every parameter of the run, so `run.json`, or a trajectory
alone, shows how it was produced:

- `command` (the exact command line), `alias`, `task`, `type`, `redo_existing`;
- `skills`: name, description and snapshot path of each skill;
- `model` (name, API base, temperature and other settings) and `agent` (step
  limit, wall-time limit, templates excluded), the effective `config.yaml` values;
- `environment`: image tag, archive and image git head (warmup: `local`);
- `versions` (Python, mini-swe-agent, Harbor), `repository` (git commit, dirty flag),
  `host` (name, platform);
- `timestamps` (UTC ISO-8601): `started`, `agent_started`, `agent_finished`,
  `eval_finished`, `finished`;
- outcome: `exit_status`, `model_calls`, `usage` (token totals), `valid_submission`,
  `score`, `errors`.

The agent has at most 60 model calls and 2 hours (`config.yaml`, temperature 0).
Transient provider errors (timeouts, connection errors, 5xx, rate limits) are
retried; every attempt is a row in `model-requests.jsonl`.

`jobs/vanilla/<id>/` holds our vanilla run of each task (one per task), in the same
format.

Vanilla scores on the public checkpoints (`python -m lab2 scoreboard` shows the same):

| Task | Type | Vanilla score | Public checkpoints |
| --- | --- | ---: | ---: |
| `garage` | warmup | 53.33 | 15 |
| `k6` | test-writing | 77.78 | 9 |
| `minio` | test-writing | 75.00 | 8 |
| `paperless` | test-writing | 83.33 | 12 |
| `abs` | issue-reproduction | 50.00 | 14 |
| `dateutil` | issue-reproduction | 70.83 | 24 |
| `psd-tools` | issue-reproduction | 66.67 | 21 |

TW mean **78.70**, IR mean **62.50** (the warmup is in neither mean).

## Scoring

A task has checkpoints: behaviours the tests should check. Each checkpoint has
one or more *faulty versions*, patches that break that behaviour.

1. **Valid submission.** The submission is the set of new test files in the
   task's test paths, plus edited starter tests listed as editable. It is
   invalid if there is no such file or if anything else changed (production code,
   other files, git history). An invalid submission scores 0.
2. **Eligible tests.** Test writing and warmup: a test is eligible if it passes on
   the correct code. Issue reproduction: if it fails (or does not run) on the
   unfixed code and passes on the reference-repaired code.
3. **K per checkpoint.** A faulty version is detected if at least one eligible
   test fails on it; a test that does not run (crash, panic, build error,
   timeout) counts as failing. K is the fraction of the checkpoint's faulty
   versions that are detected.
4. **Score** = 100 x the mean K over the checkpoints, all weighted equally.

Every test run starts from a reset repository with only the submission added. A
run longer than 300 seconds is stopped and its tests count as not run. All
faulty-version runs of one evaluation together get 2 hours; faulty versions not
reached by then count as not detected.

**Hidden checkpoints.** Each benchmark task also has hidden checkpoints, about
25-30% of its checkpoints. They cover the same features as the listed ones and
are scored the same way, but they are not listed and are used only in the TAs'
evaluation of your submission. The warmup has none.

**Issue reproduction** is scored with the task's reference repair,
`tasks/issue-reproduction/<id>/solution.patch`; its faulty versions are edits of
the repaired code. The repair is there only for evaluation: skills must not
reveal, directly or indirectly, the cause of a bug or how to fix it.

### checkpoints.json

`tasks/<type>/<id>/checkpoints.json` lists the public checkpoints:

```json
{"task": "paperless",
 "checkpoints": [
   {"id": "tag-key-dash", "label": "...", "hidden": false,
    "faulty_versions": [{"id": "dash-not-delimiter", "patch": "diff --git a/... b/...\n..."}]}]}
```

Each `patch` is a unified diff against the correct code (`git apply`); for issue
reproduction, against the reference-repaired code. To check your tests against
your own faulty versions, write a file in this format (`task` must be the task id)
and pass it with `eval --checkpoints FILE`, together with the public file if you
want both.

## Submission

- `python -m lab2 submit --alias A --type TYPE` puts the jobs you choose into
  `jobs/submission/<type>/`; the three tasks of a type must use the same skills.
  The TAs evaluate them with all checkpoints, public and hidden.
- The report: edit `report/main.tex` (ACL style; its comments say what to write),
  from the root of your repository run `tectonic report/main.tex`, and submit
  the output `report/main.pdf`. The first build downloads the LaTeX packages it
  needs into `.cache/tectonic/` (needs network; set by `scripts/activate.sh`).
- Keep the skills you used in `skills/`; each job also has its own snapshot.

## Layout

```
README.md            this guide
setup.sh             installs the tools (scripts/setup.py)
scripts/activate.sh  shell environment: venv, PATH, PYTHONPATH, udocker, tectonic cache
config.yaml          agent and model configuration
pyproject.toml       Python requirements and pinned vendored packages
lab2/                the lab tools (python -m lab2); verify.py is the verifier run in each task environment
tasks/<type>/<id>/   task.yaml, prompt.md, checkpoints.json (issue reproduction: solution.patch; warmup: project/)
skills/<name>/       skills (skills/example: the format)
jobs/vanilla/<id>/   our vanilla run of each task
jobs/submission/     your submitted jobs (written by submit)
jobs/<alias>/<id>/   your runs
images/              downloaded image archives
report/              your report: main.tex (edit), main.pdf (submit; tectonic report/main.tex)
tests/               tests of the lab tools (python -m pytest; no API calls)
vendor/              mini-swe-agent and Harbor (pinned git submodules)
```

Generated and ignored by git: `.tools/`, `.venvs/`, `.cache/udocker/`,
`.cache/tectonic/`, `images/*.tar.gz` and `jobs/<alias>/` of your own runs.
