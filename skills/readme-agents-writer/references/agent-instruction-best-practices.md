# Agent Instruction Best Practices For Unified README/AGENTS/CLAUDE

Use this guide when the canonical `README.md` also powers `AGENTS.md` and `CLAUDE.md` via symlinks.

The goal is strict triplet structure plus high-quality operational instructions.

## Research Basis (Primary Sources)

This guidance aligns with current first-party docs and specs from major agent tooling ecosystems, including:

- Repository instruction-file conventions (`AGENTS.md`, `CLAUDE.md`, and equivalent project rule files)
- Portable `agents.md`-style specification patterns
- IDE-integrated project-instruction systems
- Custom coding-instruction systems in code-hosting platforms

Common signal across sources:

- Local, repo-level instructions must be explicit and actionable.
- Rules should be testable and avoid soft language.
- Scope and precedence should be clear (global vs local rules).
- Instruction files should encode workflows, not just style opinions.

## Hard Rule: Agent-Agnostic Wording

Keep instruction content agent-agnostic by default.

- Allowed: file naming for compatibility (`AGENTS.md`, `CLAUDE.md`, `README.md`)
- Allowed: short compatibility notes in dedicated sections
- Not allowed: core rules that assume one model/tool's private behavior
- Not allowed: "if assistant A does X, assistant B does Y" for core repo workflow

Good:

```md
Before opening a PR, run `pnpm lint` and `pnpm test` from the repo root.
If either command fails, stop and report failing targets with exact output.
```

Bad:

```md
One assistant should run lint first, but another assistant can skip lint for small changes.
```

## Design Principles

### 1) Prefer Trigger/Action Rules Over Advice

Good:

```md
When editing `apps/web/**`, run `pnpm --filter @acme/web test`.
```

Bad:

```md
Consider running tests if you touched web files.
```

### 2) Separate Mandatory Constraints From Preferences

Good:

```md
Mandatory:
- Never run destructive git commands without explicit approval.

Preferred:
- Keep new utility files under `src/lib/`.
```

Bad:

```md
Try not to use git reset --hard and usually put files in src/lib.
```

### 3) Make Commands Executable As Written

Every command should define:

- Working directory
- Exact command
- Expected success criteria (where useful)

Good:

```md
From repo root, run `python3 scripts/check-doc-triplets.py .`.
Success means no "VIOLATION" lines are printed.
```

Bad:

```md
Run the triplet checker and make sure it looks good.
```

### 4) Encode Safety Gates For Risky Actions

Good:

```md
Before changing production config files, stop and request confirmation with a one-line risk summary.
```

Bad:

```md
Be careful with production files.
```

### 5) Require Verification For Factual Claims

Good:

```md
Never document a command/script until its path and invocation are verified with `rg --files` and local execution.
```

Bad:

```md
Document commands based on prior knowledge of the repository.
```

### 6) Define Scope And Ownership Boundaries

State what the doc owns and what it links out to.

Good:

```md
This file owns repository-wide guardrails. Package-specific build details live in `packages/*/README.md`.
```

Bad:

```md
This is the main guide. See other docs for details.
```

### 7) Resolve Conflicts With Explicit Precedence

Good:

```md
If local package docs conflict with root defaults, package docs win for package-internal commands.
```

Bad:

```md
Use your judgment when docs disagree.
```

### 8) Use Concrete Good/Bad Examples For Ambiguous Areas

Most useful for:

- naming rules
- test scope
- file placement
- migration patterns
- destructive operations

## Recommended Section Contract For Canonical README

For unified human+agent docs, include at least:

1. `Overview`
2. `Scope`
3. `Guardrails`
4. `Engineering Playbook` (setup, run, test, lint, build, release)
5. `Conventions` (repo-specific)
6. `Do / Don't Examples`
7. `Verification Checklist`
8. `Escalation Rules`
9. `Related Docs`

If this is root-level, include architecture map and ownership boundaries.
If this is module-level, include local invariants and focused command set.

## Anti-Patterns To Remove

- Soft language (`maybe`, `probably`, `generally`) for mandatory behavior
- Contradictory mandates across sections
- Non-runnable commands or missing cwd assumptions
- Tool/model-specific branching in core workflow
- Over-indexing on file structure while omitting operational playbooks
- Stale version numbers and dependency names
- Broad "best practices" not mapped to repo reality

## Good/Bad Instruction Blocks

### Example: Git Safety

Good:

```md
Never run `git reset --hard` or `git checkout -- <file>` unless explicitly requested by the user.
If a cleanup seems necessary, ask first and include impacted paths.
```

Bad:

```md
Avoid dangerous git commands.
```

### Example: Test Coverage Expectation

Good:

```md
For behavior changes under `packages/api/src/**`, add or update Vitest coverage in `packages/api/test/**`.
If tests are skipped, document why and list exact risk in the final update.
```

Bad:

```md
Add tests when it makes sense.
```

### Example: Documentation Freshness

Good:

```md
Any referenced script path must be validated with `rg --files | rg '<script-name>'` before publish.
Delete claims that cannot be verified quickly.
```

Bad:

```md
Keep docs fresh and accurate.
```

## Pre-Publish Review Rubric

A doc is ready only if all pass:

- `Structure`: Triplet contract and scope layering are correct.
- `Specificity`: Mandatory rules are explicit and deterministic.
- `Executability`: Commands run as written from declared directories.
- `Safety`: Risky operations include confirmation/escalation gates.
- `Verifiability`: Claims about files, names, versions, and commands are checked.
- `Portability`: Core instructions are agent-agnostic and tool-neutral.

If one fails, fix the doc before finalizing symlink enforcement.
