#!/usr/bin/env bash
set -euo pipefail

remote=bianchi
delay_seconds=${PUSH_DELAY_SECONDS:-10}
dry_run=0

if [[ ${1:-} == --dry-run ]]; then
  dry_run=1
elif [[ $# -gt 0 ]]; then
  printf 'Usage: bash %s [--dry-run]\n' "$0" >&2
  exit 2
fi

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo 'Run this script from inside the repository.' >&2
  exit 2
fi
if ! git remote get-url "$remote" >/dev/null 2>&1; then
  echo "Git remote '$remote' is not configured." >&2
  exit 2
fi
if ! [[ $delay_seconds =~ ^[0-9]+$ ]]; then
  echo 'PUSH_DELAY_SECONDS must be a non-negative integer.' >&2
  exit 2
fi

mapfile -t branches < <(git for-each-ref --format='%(refname:short)' refs/heads)
if ((${#branches[@]} == 0)); then
  echo 'No local branches found.' >&2
  exit 2
fi

declare -A commits_by_branch start_by_branch
total_pushes=0

# Preflight every branch before pushing any of them. If interrupted later,
# rerunning resumes from the last commit published on each remote branch.
for branch in "${branches[@]}"; do
  mapfile -t commits < <(git rev-list --reverse --first-parent "refs/heads/$branch")
  if ((${#commits[@]} == 0)); then
    echo "No commits found for local branch '$branch'." >&2
    exit 2
  fi

  remote_line=$(git ls-remote --heads "$remote" "refs/heads/$branch")
  remote_sha=${remote_line%%$'\t'*}
  start=0

  if [[ -n $remote_sha ]]; then
    found=0
    for i in "${!commits[@]}"; do
      if [[ ${commits[$i]} == "$remote_sha" ]]; then
        start=$((i + 1))
        found=1
        break
      fi
    done
    if ((found == 0)); then
      printf "Remote branch '%s' is not at a commit on its local first-parent history. No branches were pushed.\n" "$branch" >&2
      exit 2
    fi
  fi

  commits_by_branch["$branch"]="${commits[*]}"
  start_by_branch["$branch"]=$start
  remaining=$((${#commits[@]} - start))
  total_pushes=$((total_pushes + remaining))
  printf '%-28s %d commit(s) to push\n' "$branch" "$remaining"
done

if ((dry_run)); then
  printf 'Dry run only; no pushes made. Destination: %s\n' "$(git remote get-url "$remote")"
  exit 0
fi

printf 'Destination: %s\n' "$(git remote get-url "$remote")"
read -r -p "Push all ${#branches[@]} local branches incrementally to '$remote'? [y/N] " answer
if [[ ! $answer =~ ^[Yy]$ ]]; then
  echo 'Cancelled; no pushes made.'
  exit 0
fi

if ((total_pushes == 0)); then
  echo 'All local branch tips are already present on the remote.'
  exit 0
fi

pushed=0
for branch in "${branches[@]}"; do
  read -r -a commits <<< "${commits_by_branch[$branch]}"
  start=${start_by_branch[$branch]}
  for ((i=start; i<${#commits[@]}; i++)); do
    printf "[%d/%d] %s at %s\n" "$((pushed + 1))" "$total_pushes" "$branch" "${commits[$i]}"
    if ! git push "$remote" "${commits[$i]}:refs/heads/$branch"; then
      printf "Push failed on branch '%s'. Rerun this script to resume from the remote tip.\n" "$branch" >&2
      exit 1
    fi
    pushed=$((pushed + 1))
    if ((pushed < total_pushes && delay_seconds > 0)); then
      sleep "$delay_seconds"
    fi
  done
done

echo 'Finished pushing all local branches.'
