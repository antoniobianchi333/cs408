# Lab 2 task images (TA only)

How the six ARM64 task images that students download are built. Not distributed.

## Requirements

- An ARM64 Linux host with udocker, and the skeleton environment active:
  `source skeleton/scripts/activate.sh` (run every command from the lab root).
- The local mars-base container `~/.udocker/containers/cs408-mars-arm64`. Every
  build starts from a copy of it; the original is never changed.
- Network access: ghcr.io (SWE-Atlas images), GitHub, go.dev, PyPI, the Debian
  mirrors and the Go module proxy.
- Disk: one build container (~100k inodes) at a time in `--work`, plus the archives.

## Build

```bash
python construction/images/build.py --check [ID ...]    # only check that every source is reachable
python construction/images/build.py [ID ...]            # build all six images, or the given ones
```

Options: `--out DIR` (archives and image store, default `/tmp/cs408-lab2-images`),
`--work DIR` (build containers and downloads, default `/tmp/cs408-lab2-build`),
`--no-validate`.

For each task the build:

1. fills `/app`: for the SWE-Atlas TW tasks (paperless, minio, k6), with the `/app` tree
   of the task's Atlas x86 image; for the DeepSWE tasks (dateutil, psd-tools, abs),
   by cloning the repository at the base commit (`source/Dockerfile`);
2. installs the native ARM64 toolchain and dependencies (the per-task recipe in
   `RECIPES` in `images/build.py`; Python versions pinned by `source/constraints.txt` or
   `source/requirements.txt`);
3. checks that `/app` is at task.yaml `environment.head`, has the recipe's `app_tree`
   and a clean working tree;
4. writes `<out>/<id>-arm64.tar.gz` (tag `cs408-lab2/<id>:arm64`), loads it into
   `<out>/udocker` and runs `validate.py` on it.

The archives are what students download into `skeleton/images/`.

## Validate

```bash
python construction/validate.py [ID ...] [--store DIR]   # images already in a udocker store
```

It prints OK or FAILED per task. The checks are:

- SWE-Atlas TW: the existing tests pass, the reference tests (`reference-tests/`) pass, and
  the Atlas skeleton swap (`source/skeleton_code_swap.patch`) makes them fail.
- DeepSWE: with the official tests (`source/test.patch`), every P2P test passes and every
  F2P test fails on the unfixed code and passes with the task's `solution.patch`
  (`source/config.json`).

`test_file_renaming_missing_permissions` (paperless) fails because udocker runs as root,
so it is listed as a known failure.

## Task files

```
tasks/<type>/<id>/source/            upstream task files used by the build and the validation
tasks/test-writing/<id>/reference-tests/   the Atlas reference test file, at its repository path
```

The Atlas removal of paperless' reference tests also removed the `@override_settings`
decorators from two existing tests. `source/restore-decorators.patch` adds them back
as a separate commit.
