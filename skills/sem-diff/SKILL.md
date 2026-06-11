---
name: sem-diff
description: Use sem for entity-level semantic Git diffs, blame, dependency impact, logs, entities, and AI-ready code context. Prefer for understanding code changes by functions/classes instead of raw line hunks.
---

# sem-diff

## Purpose

Use `sem` when you need to understand code changes semantically: functions, classes, methods, types, and structured sections instead of raw line hunks.

`sem` is an entity-level layer on top of Git. It uses tree-sitter parsing and AST-normalized structural hashes to distinguish cosmetic edits from structural changes.

## When to use

- Reviewing a diff and needing a concise "what changed" summary.
- Explaining staged, working tree, commit, or range changes to a user.
- Finding who last touched an entity.
- Estimating dependency impact from a changed function/class/method.
- Building AI context around an entity and its related code.

Do not replace tests, typechecks, or domain reasoning with `sem`; use it to focus investigation.

## Install and setup

Check whether it is already available:

```bash
command -v sem && sem --help
```

Install with Homebrew:

```bash
brew install sem-cli
```

Optional Git integration:

```bash
sem setup
```

`sem setup` configures `git diff` to use `sem`. Revert with:

```bash
sem unsetup
```

Build from source when Homebrew is not appropriate:

```bash
git clone https://github.com/Ataraxy-Labs/sem
cd sem/crates
cargo install --path sem-cli
```

## Core workflow

### 1) Start with entity diff

```bash
sem diff
sem diff --staged
sem diff --commit abc1234
sem diff --from HEAD~5 --to HEAD
sem diff file1.ts file2.ts
```

Prefer `sem diff` before raw `git diff` when the user asks what changed. It groups changes by entity and reports added, modified, deleted, moved, renamed, reordered, and cosmetic-vs-structural edits.

Use verbose mode when the entity list is too coarse:

```bash
sem diff -v
```

### 2) Use machine-readable output for agents and scripts

```bash
sem diff --format json
sem diff --format plain
sem diff --format markdown
sem diff --stdin --format json
```

When consuming results programmatically, prefer JSON and summarize the `summary` counts plus the highest-risk `changes` entries.

Some commands also accept `--json`; if `--format json` is rejected, retry with `--json`.

### 3) Trace ownership and impact

```bash
sem blame src/auth.ts --json
sem graph --entity validateToken --format json
sem impact validateToken --json
```

Use `blame` for per-entity ownership, `graph` for calls and callers, and `impact` for transitive dependents.

### 4) Pull focused context

When available in the installed `sem` version, use:

```bash
sem entities src/auth.ts
sem log authenticateUser --json
sem context authenticateUser --json
```

Use `entities` to identify exact names, `log` to inspect how one entity evolved, and `context` to provide a token-budgeted prompt with the target entity plus dependencies and dependents.

## Practical command choices

- Current worktree: `sem diff`
- Staged review: `sem diff --staged --format json`
- One commit: `sem diff --commit <sha> --format json`
- Release/range review: `sem diff --from <base> --to <head> --format json`
- Language-limited scan: `sem diff --file-exts .ts .tsx --format json`
- Dependency check: `sem impact <entity> --json`
- Caller/callee graph: `sem graph --entity <entity> --format json`
- Entity ownership: `sem blame <path> --json`

## Interpreting output

- Treat `modified (logic)` or structural changes as review priorities.
- Treat cosmetic-only edits as lower risk unless they touch generated, formatted, or whitespace-sensitive files.
- Treat deleted, renamed, moved, or reordered public API entities as compatibility risks.
- For impact analysis, inspect directly affected tests and transitive callers before claiming safety.
- Use raw `git diff` only after `sem` has identified the entities that deserve line-level inspection.

## Language coverage

`sem` supports common code and structured data formats including TypeScript, JavaScript, Python, Go, Rust, Java, C/C++, C#, Ruby, PHP, Swift, Kotlin, Elixir, Bash, HCL/Terraform, Vue, Svelte, Dart, Scala, Nix, Zig, JSON, YAML, TOML, CSV, Markdown, and more. Unsupported files fall back to chunk-based diffing.

## Sources

- https://ataraxy-labs.github.io/sem/
- https://ataraxy-labs.github.io/sem/llms.txt
- https://github.com/Ataraxy-Labs/sem
