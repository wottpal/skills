#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  set-doc-triplet.sh <directory>
    - Standard mode: requires <directory>/README.md to exist and sets:
      AGENTS.md -> README.md
      CLAUDE.md -> README.md

  set-doc-triplet.sh <directory> <target-readme>
    - Shared-doc mode: sets all three to the same target:
      README.md -> <target-readme>
      AGENTS.md -> <target-readme>
      CLAUDE.md -> <target-readme>
EOF
}

abs_path() {
  local input="$1"
  local dir_part base
  dir_part="$(dirname "$input")"
  base="$(basename "$input")"
  (
    cd "$dir_part" >/dev/null 2>&1
    printf '%s/%s\n' "$(pwd -P)" "$base"
  )
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 1
fi

dir="$1"
target="${2:-README.md}"

mkdir -p "$dir"

(
  cd "$dir"
  if [[ "$target" == "README.md" ]]; then
    if [[ ! -e "README.md" ]]; then
      echo "Error: $dir/README.md does not exist."
      echo "Create README.md first or pass an explicit shared target."
      exit 2
    fi
    ln -snf README.md AGENTS.md
    ln -snf README.md CLAUDE.md
    echo "Set companions in $dir:"
    echo "  AGENTS.md -> README.md"
    echo "  CLAUDE.md -> README.md"
  else
    if [[ ! -e "$target" && ! -L "$target" ]]; then
      echo "Error: target '$target' does not exist from directory '$dir'."
      echo "Pass a valid path to a canonical README.md file."
      exit 3
    fi

    if [[ "$(basename "$target")" != "README.md" ]]; then
      echo "Error: shared target must point to a README.md file. Got '$target'."
      exit 4
    fi

    target_abs="$(abs_path "$target")"
    readme_abs="$(abs_path "README.md")"
    if [[ "$target_abs" == "$readme_abs" ]]; then
      echo "Error: shared target resolves to this directory's README.md ($target)."
      echo "Use standard mode (omit second arg) or pass a different canonical README.md path."
      exit 5
    fi

    ln -snf "$target" README.md
    ln -snf "$target" AGENTS.md
    ln -snf "$target" CLAUDE.md
    echo "Set shared-doc symlinks in $dir:"
    echo "  README.md -> $target"
    echo "  AGENTS.md -> $target"
    echo "  CLAUDE.md -> $target"
  fi
)
