#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<USAGE
Usage:
  ${0##*/} <1password-account> <secret-reference>
  ${0##*/} --account <1password-account> [--no-newline] <secret-reference>

Reads a 1Password secret reference using a short-lived cached session token.
USAGE
  exit 64
}

account="${OP_ACCOUNT:-}"
reference=""
ttl="${OP_READ_CACHED_TTL:-1500}"
lock_timeout="${OP_READ_CACHED_LOCK_TIMEOUT:-180}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --account)
      [[ $# -ge 2 ]] || usage
      account="$2"
      shift 2
      ;;
    --account=*)
      account="${1#--account=}"
      shift
      ;;
    --no-newline|-n)
      # Always passed to `op read`; accepted for config compatibility.
      shift
      ;;
    --ttl)
      [[ $# -ge 2 ]] || usage
      ttl="$2"
      shift 2
      ;;
    --ttl=*)
      ttl="${1#--ttl=}"
      shift
      ;;
    --help|-h)
      usage
      ;;
    --*)
      printf 'Unsupported option: %s\n' "$1" >&2
      usage
      ;;
    *)
      if [[ -z "$account" && $# -ge 2 ]]; then
        account="$1"
      elif [[ -z "$reference" ]]; then
        reference="$1"
      else
        usage
      fi
      shift
      ;;
  esac
done

[[ -n "$account" && -n "$reference" ]] || usage
[[ "$ttl" =~ ^[0-9]+$ ]] || { printf 'TTL must be seconds.\n' >&2; exit 64; }
command -v op >/dev/null || { printf '1Password CLI `op` not found on PATH.\n' >&2; exit 69; }

cache_root="${XDG_RUNTIME_DIR:-${TMPDIR:-/tmp}}/op-read-cached"
mkdir -p "$cache_root"
chmod 700 "$cache_root" 2>/dev/null || true

safe_account="$(printf '%s' "$account" | tr -c 'A-Za-z0-9_.-' '_')"
cache_file="$cache_root/session-$safe_account"
lock_dir="$cache_root/session-$safe_account.lock"

cleanup_lock() {
  [[ -n "${lock_acquired:-}" ]] && rmdir "$lock_dir" 2>/dev/null || true
}

acquire_lock() {
  local deadline
  deadline="$(($(date +%s) + lock_timeout))"

  while ! mkdir "$lock_dir" 2>/dev/null; do
    if (( $(date +%s) >= deadline )); then
      printf 'Timed out waiting for 1Password session cache lock.\n' >&2
      exit 75
    fi
    sleep 0.2
  done

  lock_acquired=1
  trap cleanup_lock EXIT
}

read_cached_token() {
  [[ -f "$cache_file" ]] || return 1

  local cached_at token
  cached_at="$(sed -n '1p' "$cache_file")"
  token="$(sed -n '2p' "$cache_file")"

  [[ "$cached_at" =~ ^[0-9]+$ ]] || return 1
  [[ -n "$token" ]] || return 1
  (( $(date +%s) - cached_at < ttl )) || return 1

  printf '%s' "$token"
}

read_with_token() {
  local token="$1"
  OP_SESSION="$token" op read --account "$account" --session "$token" --no-newline "$reference"
}

write_cached_token() {
  local token="$1" tmp
  tmp="$(mktemp "$cache_root/session-$safe_account.XXXXXX")"
  chmod 600 "$tmp"
  printf '%s\n%s\n' "$(date +%s)" "$token" > "$tmp"
  mv "$tmp" "$cache_file"
  chmod 600 "$cache_file"
}

if token="$(read_cached_token)"; then
  if read_with_token "$token"; then
    exit 0
  fi
  rm -f "$cache_file"
fi

acquire_lock

if token="$(read_cached_token)"; then
  if read_with_token "$token"; then
    exit 0
  fi
  rm -f "$cache_file"
fi

token="$(op signin --account "$account" --raw)"
write_cached_token "$token"
read_with_token "$token"
