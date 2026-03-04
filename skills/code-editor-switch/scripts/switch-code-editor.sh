#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Switch default code/text/config handlers to a target editor using duti.

Usage:
  switch-code-editor.sh --editor <APP_NAME|APP_PATH|BUNDLE_ID> [options]

Options:
  --project <path>          Scan project for additional tokens to map.
  --role <role>             duti role: all|viewer|editor|shell|none (default: all).
  --extra-token <token>     Additional token to map. Repeatable.
  --apply-public-data       Also map public.data (aggressive, opt-in).
  --dry-run                 Print commands without applying.
  -h, --help                Show this help.

Examples:
  switch-code-editor.sh --editor "Cursor"
  switch-code-editor.sh --editor "com.microsoft.VSCode" --project "$HOME/Developer/fmd-labs/viral-app"
  switch-code-editor.sh --editor "/Applications/Zed.app" --dry-run
EOF
}

fail() {
  echo "Error: $*" >&2
  exit 1
}

resolve_bundle_id() {
  local input="$1"
  local app_path=""
  local escaped=""
  local app_id=""

  if [[ "$input" == *"/"* ]]; then
    app_path="$input"
    if [[ -d "$app_path" ]]; then
      app_id="$(mdls -name kMDItemCFBundleIdentifier -raw "$app_path" 2>/dev/null || true)"
      if [[ -n "$app_id" && "$app_id" != "(null)" ]]; then
        printf '%s\n' "$app_id"
        return 0
      fi
    fi
  fi

  if [[ "$input" == *.app ]]; then
    app_path="/Applications/$input"
    if [[ -d "$app_path" ]]; then
      app_id="$(mdls -name kMDItemCFBundleIdentifier -raw "$app_path" 2>/dev/null || true)"
      if [[ -n "$app_id" && "$app_id" != "(null)" ]]; then
        printf '%s\n' "$app_id"
        return 0
      fi
    fi
  fi

  escaped="${input//\"/\\\"}"
  app_id="$(osascript -e "id of app \"$escaped\"" 2>/dev/null || true)"
  if [[ -n "$app_id" ]]; then
    printf '%s\n' "$app_id"
    return 0
  fi

  if [[ "$input" == *.* && "$input" != *" "* ]]; then
    printf '%s\n' "$input"
    return 0
  fi

  return 1
}

bundle_id_exists() {
  local bundle_id="$1"
  local escaped_bundle_id=""

  escaped_bundle_id="${bundle_id//\"/\\\"}"

  if osascript -e "id of app id \"$escaped_bundle_id\"" >/dev/null 2>&1; then
    return 0
  fi

  if mdfind "kMDItemCFBundleIdentifier == \"$bundle_id\"" | head -n 1 | grep -q .; then
    return 0
  fi

  return 1
}

EDITOR_INPUT=""
PROJECT_PATH=""
ROLE="all"
DRY_RUN=0
APPLY_PUBLIC_DATA=0
EXTRA_TOKENS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --editor)
      [[ $# -ge 2 ]] || fail "--editor requires a value"
      EDITOR_INPUT="$2"
      shift 2
      ;;
    --project)
      [[ $# -ge 2 ]] || fail "--project requires a value"
      PROJECT_PATH="$2"
      shift 2
      ;;
    --role)
      [[ $# -ge 2 ]] || fail "--role requires a value"
      ROLE="$2"
      shift 2
      ;;
    --extra-token)
      [[ $# -ge 2 ]] || fail "--extra-token requires a value"
      EXTRA_TOKENS+=("$2")
      shift 2
      ;;
    --apply-public-data)
      APPLY_PUBLIC_DATA=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown argument: $1"
      ;;
  esac
done

[[ -n "$EDITOR_INPUT" ]] || fail "Missing --editor"
command -v duti >/dev/null 2>&1 || fail "duti is not installed (run: brew install duti)"

case "$ROLE" in
  all|viewer|editor|shell|none)
    ;;
  *)
    fail "Invalid role '$ROLE'. Use all|viewer|editor|shell|none"
    ;;
esac

if [[ -n "$PROJECT_PATH" && ! -d "$PROJECT_PATH" ]]; then
  fail "--project path does not exist: $PROJECT_PATH"
fi

BUNDLE_ID="$(resolve_bundle_id "$EDITOR_INPUT" || true)"
[[ -n "$BUNDLE_ID" ]] || fail "Could not resolve bundle identifier for: $EDITOR_INPUT"
bundle_id_exists "$BUNDLE_ID" || fail "Bundle identifier '$BUNDLE_ID' is not installed/registered in LaunchServices"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DISCOVER_SCRIPT="$SCRIPT_DIR/discover-project-editor-tokens.sh"
[[ -x "$DISCOVER_SCRIPT" ]] || fail "Missing executable helper script: $DISCOVER_SCRIPT"

BASE_UTIS=(
  "public.text"
  "public.plain-text"
  "public.source-code"
  "public.script"
  "public.shell-script"
  "public.python-script"
  "net.daringfireball.markdown"
  "public.json"
  "public.xml"
  "public.yaml"
)

if [[ "$APPLY_PUBLIC_DATA" -eq 1 ]]; then
  BASE_UTIS+=("public.data")
fi

BASE_TOKENS=(
  "txt"
  "md"
  "markdown"
  "mdx"
  "rst"
  "adoc"
  "org"
  "json"
  "jsonc"
  "json5"
  "yaml"
  "yml"
  "toml"
  "xml"
  "ini"
  "conf"
  "cfg"
  "properties"
  "html"
  "htm"
  "css"
  "scss"
  "sass"
  "less"
  "env"
  "local"
  "gitignore"
  "gitattributes"
  "gitmodules"
  "npmrc"
  "nvmrc"
  "editorconfig"
  "dockerignore"
  "Dockerfile"
  "Makefile"
  "ts"
  "tsx"
  "js"
  "jsx"
  "mjs"
  "cjs"
  "mts"
  "cts"
  "py"
  "sh"
  "bash"
  "zsh"
  "fish"
  "rb"
  "php"
  "go"
  "rs"
  "java"
  "kt"
  "swift"
  "c"
  "h"
  "cpp"
  "hpp"
  "cs"
  "scala"
  "sql"
  "graphql"
  "gql"
  "prisma"
  "lock"
)

TMP_TOKENS="$(mktemp)"
trap 'rm -f "$TMP_TOKENS"' EXIT

{
  for token in "${BASE_TOKENS[@]}"; do
    printf '%s\n' "$token"
  done

  for token in "${EXTRA_TOKENS[@]}"; do
    printf '%s\n' "$token"
  done

  if [[ -n "$PROJECT_PATH" ]]; then
    "$DISCOVER_SCRIPT" "$PROJECT_PATH"
  fi
} | awk 'NF > 0' | LC_ALL=C sort -u > "$TMP_TOKENS"

run_mapping() {
  local token="$1"
  local category="$2"
  local error_output=""

  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run] duti -s %q %q %q  # %s\n' "$BUNDLE_ID" "$token" "$ROLE" "$category"
    return 0
  fi

  if error_output="$(duti -s "$BUNDLE_ID" "$token" "$ROLE" 2>&1 >/dev/null)"; then
    return 0
  fi

  error_output="${error_output//$'\n'/ }"
  error_output="${error_output//$'\r'/ }"
  if [[ -z "$error_output" ]]; then
    error_output="no stderr output"
  fi

  FAILED_DETAILS+=("$category '$token': $error_output")
  echo "WARN: failed to apply $category mapping for '$token' ($error_output)" >&2
  return 1
}

success_count=0
fail_count=0
FAILED_DETAILS=()

for uti in "${BASE_UTIS[@]}"; do
  if run_mapping "$uti" "UTI"; then
    success_count=$((success_count + 1))
  else
    fail_count=$((fail_count + 1))
  fi
done

while IFS= read -r token; do
  if run_mapping "$token" "token"; then
    success_count=$((success_count + 1))
  else
    fail_count=$((fail_count + 1))
  fi
done < "$TMP_TOKENS"

echo "Editor input:  $EDITOR_INPUT"
echo "Bundle ID:     $BUNDLE_ID"
echo "Role:          $ROLE"
if [[ -n "$PROJECT_PATH" ]]; then
  echo "Project scan:  $PROJECT_PATH"
fi
echo "Mapped:        $success_count success, $fail_count failed"
if [[ "$fail_count" -gt 0 ]]; then
  max_failed_details=20
  echo "Failed mappings (showing up to $max_failed_details):"
  for failed_detail in "${FAILED_DETAILS[@]:0:$max_failed_details}"; do
    echo "  - $failed_detail"
  done

  if [[ "${#FAILED_DETAILS[@]}" -gt "$max_failed_details" ]]; then
    echo "  - ... and $(( ${#FAILED_DETAILS[@]} - max_failed_details )) more"
  fi
fi

echo "Verification examples:"
echo "  duti -x ts"
echo "  duti -x tsx"
echo "  duti -x env"
echo "  duti -x gitignore"
echo "  duti -x Dockerfile"
