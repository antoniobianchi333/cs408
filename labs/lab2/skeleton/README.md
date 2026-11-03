# CS408 Lab 2: Teaching a Coding Agent to Write Tests

You write *skills*: short instructions that a fixed coding agent (mini-swe-agent
with the course model) reads while it writes tests. You compare runs with your
skills against vanilla runs (no skills) on the same tasks. The agent, the model,
the tasks and the run limits are the same for everyone. The course handout gives
the background, the deliverables and the deadlines; this guide is the reference
for the lab2 tool. The tool calls an experiment an *alias*, a run a *job*, and a
part (warmup, test writing, issue reproduction) a *type*.

## Tasks

`python -m lab2 tasks` lists them.

| Task | Part (type) | Language | Public checkpoints | The agent must... |
| --- | --- | --- | ---: | --- |
| `garage` | warmup | Python | 15 | extend `test_garage.py` for a parking-garage class (plates, capacity, sessions, charges, passes) from `SPEC.md` |
| `paperless` | test-writing | Python | 12 | test `generate_filename` of paperless-ngx (document type, ASN, tag and date placeholders, path separators) |
| `minio` | test-writing | Go | 8 | test MinIO's `internal/etag` package (parsing, equality, multipart, encryption, S3 formatting) |
| `k6` | test-writing | Go | 9 | test k6 execution segments (sequences from strings, striped offsets, shared properties, new execution tuples) |
| `dateutil` | issue-reproduction | Python | 24 | reproduce RFC 5545 timezone interoperability of `dateutil.rrule` (RDATE TZID/VALUE, timezone-aware `__str__`, iCalendar output, set operations) |
| `psd-tools` | issue-reproduction | Python | 21 | reproduce a typed blend-range ("Blend If") API for layers and its use in compositing |
| `abs` | issue-reproduction | Go | 14 | reproduce stepped slices `value[start:end:step]` for arrays and strings in the ABS language |

- **Warmup and test writing**: the code in the task repository is correct. The
  tests must pass on it and detect faulty versions of it.
- **Issue reproduction**: the task repository holds the *unfixed code*, which lacks
  a behavior that an issue requests. The tests must fail on the unfixed code and
  pass on the correct code (our implementation, `solution.patch`). The agent must
  not implement the behavior.

The six test-writing and issue-reproduction tasks are the benchmark; the warmup
is practice and is in neither mean. Each task's text is
`tasks/<type>/<id>/prompt.md`.

A *test file* is a file named `test_*.py` or `*_test.py` (Python) or `*_test.go`
(Go) in one of the task's `test_paths` (`task.yaml`). The agent may only add test
files and edit the starter tests listed under `editable` (only the warmup has
one, `test_garage.py`). Any other change in the task repository, including files
that the tests write when they run, makes the submission invalid; tests write
temporary files under `/tmp`.

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

**Images.** On the course servers the task images are already there, in a
shared read-only copy (`/tmp/cs408-lab2-shared`). If it is missing an image, the
command pulls it (`environment.image` in `task.yaml`, public on
`ghcr.io/cs408-fall-2026`; needs network, about a minute) into your own store and
deletes it again when the command ends. Your own store,
`/tmp/cs408-lab2-<user>/udocker` (private to you; `<user>` is your login name, or
`LAB2_IMAGE_STORE`), otherwise holds only the containers of running tasks.

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

An **alias** (an experiment in the handout) names a set of runs (`jobs/<alias>/`). It matches
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
  invalid `SKILL.md`, existing jobs, an image that cannot be pulled.

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
- The prompt lists only the name, the description and the path of each skill's
  `SKILL.md`. During the run the selected skills are at `.skills/<name>/` in the
  task repository, and the agent reads their files with bash when it needs them.
- Select skills with `run --skills my-skill other-skill`. A run without
  `--skills` is a **vanilla** run.
- Do not edit a skill after a run has used it: copy it to a new folder
  (e.g. `my-skill-v2/`, with `name: my-skill-v2`) and edit the copy.

**Rules.** A skill teaches *how* to test: a testing method from class and how to
apply it to a kind of code. It must not tell the agent *what* to test in a
particular task, and must not reveal, directly or indirectly, what a faulty
version breaks, an input that breaks it, or how our implementation of an issue
works. The three runs you submit for a part must use the same skills.

`skills/example/` shows the format only; its instructions are not testing advice.

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
- `environment`: image and its git head (warmup: `local`);
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

A task has *checkpoints*: behaviors the tests should check. Each checkpoint has
one or more *faulty versions*: copies of the correct code (patches) in which only
that behavior is broken.

1. **Valid submission.** The submission is the agent's test files (see Tasks). It
   is invalid if there is no test file or if anything else in the task repository
   changed. An invalid submission scores 0 (`valid_submission: false`, with the
   offending files in `unexpected_changes`).
2. **Counted tests.** Warmup and test writing: a test is counted if it passes on
   the correct code. Issue reproduction: if it fails on the unfixed code and passes
   on the correct code. Tests that are not counted are ignored; they never lower
   the score.
3. **Detection.** A faulty version is detected if at least one counted test fails
   on it. A test that gives no result (crash, panic, build or import error,
   timeout) counts as failing.
4. **Task score** = 100 x the mean *checkpoint value* over the checkpoints, all
   weighted equally; a checkpoint's value is the fraction of its faulty versions
   that are detected.

Each version of the code is tested from a reset repository with only the
submission added, with all the agent's tests run together. A run longer than 5
minutes is stopped and its tests count as giving no result (Go: each package also
stops after 2 minutes). All faulty versions of a task together get 2 hours;
faulty versions not reached by then count as not detected.

Tests must check behavior: they call the code under test. A test that reads or
checks source code, file contents or a diff (e.g. whether a line is present) makes
the run invalid; the TAs check this by hand.

**Hidden checkpoints.** In each benchmark task 25-30% of the checkpoints are not
listed. They cover other behaviors the task text asks for and are scored the same
way, but they are used only for the skills competition and are published after
the deadline. The warmup has none. Grading uses the public checkpoints.

**Issue reproduction** uses the correct code `tasks/issue-reproduction/<id>/solution.patch`;
its faulty versions are edits of that code. The agent never sees it or any faulty
version, and your skills must not pass on what you learn from them.

### checkpoints.json

`tasks/<type>/<id>/checkpoints.json` lists the public checkpoints:

```json
{"task": "paperless",
 "checkpoints": [
   {"id": "tag-key-dash", "label": "...", "hidden": false,
    "faulty_versions": [{"id": "dash-not-delimiter", "patch": "diff --git a/... b/...\n..."}]}]}
```

Each `patch` is a unified diff against the correct code (`git apply`); for issue
reproduction, the correct code is the unfixed code with `solution.patch` applied.
To check your tests against faulty versions of your own, write a file in this
format (`task` must be the task id) and pass it with `eval --checkpoints FILE`,
together with the public file if you want both.

## Submission

- `python -m lab2 submit --alias A --type TYPE` copies the jobs of one part into
  `jobs/submission/<type>/`; the tasks of a part must use the same skills. Different
  parts may come from different aliases. The TAs evaluate the submitted test files
  again.
- The report: edit `report/main.tex` (ACL style; its comments say what to write)
  and run `tectonic report/main.tex` from the root of your repository. Commit both
  the sources and `report/main.pdf`. The first build downloads the LaTeX packages
  it needs into `.cache/tectonic/` (needs network).
- Commit every skill a submitted job used in `skills/`, identical to the job's
  snapshot in `jobs/submission/<type>/<id>/skills/`.

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
report/              your report: main.tex (edit), main.pdf (submit; tectonic report/main.tex)
tests/               tests of the lab tools (python -m pytest; no API calls)
vendor/              mini-swe-agent and Harbor (pinned git submodules)
```

Generated and ignored by git: `.tools/`, `.venvs/`, `.cache/tectonic/` and
`jobs/<alias>/` of your own runs.
