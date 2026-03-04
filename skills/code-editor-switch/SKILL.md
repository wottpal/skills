---
name: code-editor-switch
description: Install and use duti on macOS to switch default code/text/config file handlers to a target editor, including project-driven extension discovery and verification.
---

# code-editor-switch

## Purpose

Use this skill to switch Finder/Open defaults for code, text, and config files to a new editor (for example Zed, VS Code, Cursor) using `duti`.

## When to use

- Migrating from one editor to another on macOS.
- Standardizing file defaults for local repos and team machines.
- Fixing mismatched defaults for dotfiles and config files.

## Non-negotiable rules

- Run this only on macOS.
- Prefer `duti` over direct LaunchServices plist edits.
- Apply both generic UTIs and concrete extensions/names.
- Keep `public.data` opt-in only (`--apply-public-data`).
- Verify with `duti -x` after applying mappings.

## Workflow

### 1) Preflight

- Ensure `duti` exists:
  - `command -v duti >/dev/null || brew install duti`
- Resolve bundle identifier for target editor:
  - `osascript -e 'id of app "Cursor"'`
  - `mdls -name kMDItemCFBundleIdentifier -raw "/Applications/Cursor.app"`

### 2) Apply baseline mappings

- Run:
  - `bash "scripts/switch-code-editor.sh" --editor "Cursor"`
- This applies:
  - Core UTIs (`public.text`, `public.plain-text`, `public.source-code`, etc.)
  - Baseline code/config extensions (`ts`, `tsx`, `js`, `json`, `yaml`, `sql`, `py`, `css`, `toml`, `mdx`, etc.)
  - No-extension names like `Dockerfile`

### 3) Add project-driven coverage (preview first)

- Preview discovered tokens before applying (required):
  - `bash "scripts/discover-project-editor-tokens.sh" "$HOME/Developer/fmd-labs/viral-app"`
  - `bash "scripts/discover-project-editor-tokens.sh" "$HOME/Developer/fmd-labs/viral-app" | sed -n '1,120p'`
- Optional safety check for obvious artifact noise:
  - `bash "scripts/discover-project-editor-tokens.sh" "$HOME/Developer/fmd-labs/viral-app" | rg '^(dep-|build-script-|bin$|a$|d$)'`
- Only after preview/review, apply project scan:
  - `bash "scripts/switch-code-editor.sh" --editor "Cursor" --project "$HOME/Developer/fmd-labs/viral-app"`
- If preview output is noisy, narrow `--project` to a cleaner subdirectory or expand excludes first.

### 4) Verify

- Check representative mappings:
  - `duti -x ts`
  - `duti -x tsx`
  - `duti -x env`
  - `duti -x gitignore`
  - `duti -x Dockerfile`
- If Finder still opens old handlers, log out/in to refresh LaunchServices behavior.

### 5) Optional aggressive mode

- Only if explicitly requested:
  - `bash "scripts/switch-code-editor.sh" --editor "Cursor" --apply-public-data`
- Warning: this can redirect many non-code files.

## Known edge cases

- `.ts` can resolve to a non-code UTI on some systems; extension mapping is required.
- Dotfiles like `.env.local` are often matched by suffix (`local`) plus text UTIs.
- Some apps may reclaim specific extensions after updates/reinstalls.

## Deliverables

When using this skill, always return:

- Target editor and resolved bundle ID.
- Exact script command used.
- Summary of UTI + token mappings applied.
- 3-5 verification checks (`duti -x ...`).

## Progressive disclosure

Load only what is needed:

- `references/coverage-from-viral-app.md` for practical extension gaps.
- `references/sources.md` for source links and version checkpoints.
- `scripts/discover-project-editor-tokens.sh` for token discovery.
- `scripts/switch-code-editor.sh` for the full apply workflow.
