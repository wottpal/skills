# Fact Verification Checklist (Mandatory)

Treat every statement as untrusted until confirmed from source files or commands.
Prefer guarded checks so the workflow works across different stacks.

## Verify Paths And Files

```bash
rg --files | rg '(<path-or-file-pattern>)'
test -e <path> && echo "exists"
```

## Verify Variables / Constants / Flags

```bash
rg -n --hidden --glob '!.git' '(<CONST_NAME>|<ENV_VAR>|<flag>)'
```

Check:

- Name is exact (case-sensitive).
- Definition and usage both exist.
- Behavior matches documented meaning.

## Verify Commands

```bash
test -f package.json && rg -n '"scripts"\s*:' package.json
test -f pyproject.toml && rg -n '^\[project\]|^\[tool\.' pyproject.toml
test -f Makefile && rg -n '^[A-Za-z0-9_.-]+:' Makefile
```

Check:

- Command exists in scripts/task runner.
- Command still runs in current repo.
- Output semantics match documentation.

## Verify Dependencies And Versions

JavaScript/TypeScript:

```bash
test -f package.json && rg -n '(<dep-name>|"dependencies"|"devDependencies"|"peerDependencies")' package.json
test -f bun.lockb && command -v bun >/dev/null && bun pm ls <dep-name> || true
test -f pnpm-lock.yaml && command -v pnpm >/dev/null && pnpm why <dep-name> || true
test -f package-lock.json && command -v npm >/dev/null && npm ls <dep-name> --depth=0 || true
test -f yarn.lock && command -v yarn >/dev/null && yarn why <dep-name> || true
```

Python:

```bash
test -f pyproject.toml && rg -n '(<dep-name>|^\[project\]|^\[tool.poetry\])' pyproject.toml
rg -n '(<dep-name>)' requirements*.txt 2>/dev/null || true
command -v uv >/dev/null && uv pip show <dep-name> || true
command -v poetry >/dev/null && poetry show <dep-name> || true
command -v pip >/dev/null && pip show <dep-name> || true
```

Check:

- Dependency is still installed/declared.
- Version range in docs is current.
- Dependency is still actively used.

## Toolchain Detection (Optional Quick Pass)

```bash
test -f bun.lockb && echo "bun"
test -f pnpm-lock.yaml && echo "pnpm"
test -f package-lock.json && echo "npm"
test -f yarn.lock && echo "yarn"
test -f pyproject.toml && echo "python-project"
ls requirements*.txt >/dev/null 2>&1 && echo "requirements-txt"
```

## Verify URLs, Endpoints, And Entry Points

```bash
rg -n '(http|https|/api/|route|endpoint|main|entry)'
```

Check:

- Endpoint/path exists in code.
- Example payload shape matches current implementation.

## Final Anti-Staleness Pass

- Re-run critical searches after editing docs.
- Remove or fix any doc claim you cannot verify quickly.
- Prefer “not documented yet” over stale certainty.
