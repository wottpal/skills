#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Discover code/editor-relevant duti tokens from a project.

Usage:
  discover-project-editor-tokens.sh [PROJECT_PATH]

Notes:
  - Excludes typical generated/vendor folders.
  - Emits one token per line (extension, dotfile suffix, or no-ext filename).
  - No-extension filenames are restricted to a high-signal allowlist.
  - Filters obvious binary/media extensions.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

PROJECT_PATH="${1:-$PWD}"
NO_EXT_ALLOWLIST_LOWER_REGEX='^(dockerfile|containerfile|makefile|gnumakefile|brewfile|gemfile|rakefile|procfile|fastfile|podfile|vagrantfile|jenkinsfile|tiltfile|justfile|taskfile|caddyfile|build|workspace|readme|license)$'

if [[ ! -d "$PROJECT_PATH" ]]; then
  echo "Project path does not exist: $PROJECT_PATH" >&2
  exit 1
fi

find "$PROJECT_PATH" \
  \( \
    -path '*/.git' -o \
    -path '*/node_modules' -o \
    -path '*/vendor' -o \
    -path '*/.next' -o \
    -path '*/.nuxt' -o \
    -path '*/.svelte-kit' -o \
    -path '*/.output' -o \
    -path '*/.venv' -o \
    -path '*/venv' -o \
    -path '*/target' -o \
    -path '*/.turbo' -o \
    -path '*/.cache' -o \
    -path '*/.parcel-cache' -o \
    -path '*/.pytest_cache' -o \
    -path '*/.mypy_cache' -o \
    -path '*/.ruff_cache' -o \
    -path '*/__pycache__' -o \
    -path '*/coverage' -o \
    -path '*/out' -o \
    -path '*/dist' -o \
    -path '*/build' \
  \) -prune -o -type f -print0 \
  | while IFS= read -r -d '' file_path; do
    base_name="$(basename "$file_path")"
    token=""
    token_is_no_ext=0

    if [[ "$base_name" == .* ]]; then
      trimmed="${base_name#.}"
      if [[ "$trimmed" == *.* ]]; then
        token="${trimmed##*.}"
      else
        token="$trimmed"
      fi
    elif [[ "$base_name" == *.* ]]; then
      token="${base_name##*.}"
    else
      token="$base_name"
      token_is_no_ext=1
    fi

    if [[ -z "$token" ]]; then
      continue
    fi

    token_lower="$(printf '%s' "$token" | tr '[:upper:]' '[:lower:]')"

    if [[ "$token_is_no_ext" -eq 1 ]] && [[ ! "$token_lower" =~ $NO_EXT_ALLOWLIST_LOWER_REGEX ]]; then
      continue
    fi

    case "$token_lower" in
      ds_store|swp|swo|tmp|bak|orig|rej)
        continue
        ;;
      cache|nodeids|tag|pkg-info|log|pyc|pyo|gpickle|msgpack|tsbuildinfo)
        continue
        ;;
      png|jpg|jpeg|gif|webp|svg|ico|heic|bmp|tiff|avif|pdf|ps|eps|ai|sketch|fig)
        continue
        ;;
      mp3|mp4|mov|avi|mkv|wav|flac|aiff|ogg|webm)
        continue
        ;;
      zip|gz|tgz|bz2|xz|7z|rar|dmg|pkg|iso|jar|war|class|exe|dll|so|dylib)
        continue
        ;;
      woff|woff2|ttf|otf|eot)
        continue
        ;;
    esac

    printf '%s\n' "$token"
  done \
  | awk 'NF > 0' \
  | LC_ALL=C sort -u
