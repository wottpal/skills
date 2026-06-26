#!/usr/bin/env bash
set -euo pipefail

target_dir="${1:-$HOME/.local/bin}"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source_script="$script_dir/op-read-cached.sh"
target="$target_dir/op-read-cached"

mkdir -p "$target_dir"
cp "$source_script" "$target"
chmod 700 "$target"

printf '%s\n' "$target"
