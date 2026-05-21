#!/usr/bin/env bash
# diff-hashes.sh — Compare git blob hashes against docs/wiki/_hashes.json
# Output: NDJSON with one line per file: {"path":"...","status":"...","doc":"...",...}
# Usage: ./diff-hashes.sh [--manifest <path>] [--scope <glob>...]

set -euo pipefail

MANIFEST="docs/wiki/_hashes.json"
SCOPE=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest) MANIFEST="$2"; shift 2 ;;
    --scope) SCOPE+=("$2"); shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ ! -f "$MANIFEST" ]]; then
  echo '{"error":"manifest not found","path":"'"$MANIFEST"'"}'
  exit 1
fi

# Extract include patterns from manifest config
if [[ ${#SCOPE[@]} -eq 0 ]]; then
  # Read include patterns from manifest; jq must be installed
  while IFS= read -r pattern; do
    SCOPE+=("$pattern")
  done < <(jq -r '.config.include[]' "$MANIFEST" 2>/dev/null || echo "src/**/*")
fi

if [[ ${#SCOPE[@]} -eq 0 ]]; then
  SCOPE=("src/**/*")
fi

# Get current git blob hashes for tracked files matching scope
declare -A git_hashes
while IFS=$'\t' read -r hash path; do
  git_hashes["$path"]="$hash"
done < <(git ls-tree -r HEAD -- "${SCOPE[@]}" 2>/dev/null | while read -r mode type hash path; do echo "$hash	$path"; done)

# Read manifest file→hash→doc mapping
declare -A manifest_hashes
declare -A manifest_docs
while IFS=$'\t' read -r path hash doc; do
  manifest_hashes["$path"]="$hash"
  manifest_docs["$path"]="$doc"
done < <(jq -r '.files // {} | to_entries[] | "\(.key)\t\(.value.hash // "null")\t\(.value.doc // "null")"' "$MANIFEST")

# Check manifest files against git
for path in "${!manifest_hashes[@]}"; do
  manifest_h="${manifest_hashes[$path]}"
  manifest_d="${manifest_docs[$path]}"
  git_h="${git_hashes[$path]:-MISSING}"

  if [[ "$git_h" == "MISSING" ]]; then
    # File in manifest but not in git tree — orphaned
    echo "{\"path\":\"$path\",\"status\":\"orphaned\",\"doc\":\"$manifest_d\"}"
  elif [[ "$manifest_h" == "null" || "$git_h" != "$manifest_h" ]]; then
    if [[ "$manifest_d" == "null" ]]; then
      echo "{\"path\":\"$path\",\"status\":\"undocumented\",\"doc\":null}"
    else
      echo "{\"path\":\"$path\",\"status\":\"stale\",\"doc\":\"$manifest_d\",\"old_hash\":\"$manifest_h\",\"new_hash\":\"$git_h\"}"
    fi
  fi
done

# Check for new git files not in manifest
for path in "${!git_hashes[@]}"; do
  if [[ -z "${manifest_hashes[$path]:-}" ]]; then
    echo "{\"path\":\"$path\",\"status\":\"new\",\"doc\":null,\"hash\":\"${git_hashes[$path]}\"}"
  fi
done
