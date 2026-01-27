#!/usr/bin/env bash
# ---------------------------------- #
# DO NOT MODIFY THIS FILE            #
# ---------------------------------- #

INPUT_FILE="./.immutablefiles"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: This script must be run inside a Git repository."
    exit 1
fi

#BASE_COMMIT="cfba7c484ac4faf60ec4d9adad921eea265c8949"
BASE_COMMIT=`git rev-list --max-parents=0 HEAD`
MODIFIED=$(git diff --name-only "$BASE_COMMIT")

echo "Following immutable file(s) are modified and have been added to the git:"
while IFS= read -r pattern; do
    # skip empty lines and comments
    [[ -z "$pattern" || "$pattern" =~ ^# ]] && continue

    # Expand glob pattern into actual files
    files=( $pattern )
    total=${#files[@]}
    count=0

    for f in "${files[@]}"; do
        # Ensure relative path to repo root
        rel=$(realpath --relative-to="$(git rev-parse --show-toplevel)" "$f" 2>/dev/null)
        if echo "$MODIFIED" | grep -qx "$rel"; then
            ((count++))
        fi
    done

    if [ "$count" -gt 0 ]; then
        echo "MODIFIED: $pattern"
    fi
done < "$INPUT_FILE"
echo ""

echo "Following immutable file(s) are modified:"
while IFS= read -r path; do
    # Skip empty lines or comments
    [[ -z "$path" || "$path" =~ ^# ]] && continue
    if git status --porcelain -- "$path" | grep -q '^[ MADRCU]'; then
        echo "MODIFIED: $path"
    fi
done < "$INPUT_FILE"
