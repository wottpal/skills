# Agent Instruction Best Practices For Unified README/AGENTS

The canonical README serves humans directly and agents through `AGENTS.md`. Its usefulness matters more than its headings or link structure.

## Keep Instructions Specific And Compact

- Keep essential commands, constraints, and non-obvious project facts close to the top.
- Include context that changes how work should be done; omit generic advice and obvious directory inventories.
- Link lengthy architecture explanations, API details, and specialized playbooks. Say when to read each link; a Markdown link does not guarantee automatic loading.
- Keep examples only where they resolve real ambiguity.
- Link the actual linter, formatter, and typechecker configuration instead of transcribing machine-enforced rules. Keep exceptions and conventions those tools do not enforce.
- Document established repository policies. Do not invent approval gates or testing requirements just to fill a section.

## Prefer Trigger/Action Rules

Good (adapt names and commands to the actual repository):

```md
When editing `apps/web/**`, run `pnpm --filter @acme/web test` from the repository root.
If it fails, fix failures caused by the change and report any remaining failures.
```

Weak:

```md
Consider running tests when appropriate.
```

## Separate Requirements From Preferences

Good:

```md
Mandatory: do not edit generated files in `src/generated/`; regenerate them using `pnpm generate`.
Preferred: place new shared utilities in `src/lib/`.
```

Avoid mixing hard constraints and suggestions in one vague sentence. A preference should not silently become a mandatory rule during refactoring.

## Make Commands Executable As Written

State the working directory, prerequisites, command, and useful success criteria. Verify against the repository's scripts and CI configuration. Where supported, document focused file/package checks alongside the conditions requiring broader checks; a narrower command does not replace mandatory checks or necessary integration coverage.

```md
From the repository root, run `pnpm lint`. A zero exit status indicates success.
```

Do not copy this command into a repository that uses a different toolchain. Do not execute deployment, publishing, data deletion, or other state-changing commands merely to verify documentation. Inspect their definitions and report unexecuted checks.

## Preserve Scope And Policy

- State which files or subtree a rule governs.
- Root guidance defines shared defaults; local guidance contains relevant differences.
- Make local exceptions explicit and reconcile contradictions. Harness loading and precedence differ, so do not assume proximity alone resolves conflicts.
- Preserve existing user changes and repository constraints while consolidating files.
- Treat stated requirements as policy, not observations about current compliance. If code violates a policy, report the mismatch rather than silently rewriting the policy to match the code.
- Keep core rules agent-agnostic. Put necessary harness-specific behavior in a short compatibility note.
- Instructions describe intended behavior; they do not replace permissions, CI, or other enforcement mechanisms.

## Suggested Content

Use only the sections that help the selected scope:

- Purpose and ownership boundaries
- Setup and core commands
- Repository-specific constraints and conventions
- Focused verification and failure handling
- Architecture or domain invariants that affect changes
- Links to deeper documentation with a reason to read each

The root needs a broad orientation. A module needs local invariants and focused checks. Neither needs a padded checklist of generic best practices.

## Remove These Anti-Patterns

- Contradictory or duplicated mandates
- Stale names, versions, links, and commands
- Unstated command working directories
- Full reference manuals in always-loaded instructions
- Blanket demands to run every check after every edit
- Model-specific branching in normal repository workflows
- Obsolete instructions to create CLAUDE companions or enforce triplets
- Claims deleted merely because verification was inconvenient; investigate or mark the uncertainty instead

## Final Review

- **Structure:** selected README/AGENTS pairs resolve correctly; legacy companions are reconciled and removed.
- **Specificity:** rules state what to do and when, with explicit scope.
- **Verification:** facts match source; executed checks and limitations are reported accurately.
- **Preservation:** unique instructions and existing authorization boundaries survive migration.
- **Portability:** core instructions do not depend on one harness's import syntax or implicit precedence.
- **Context cost:** every paragraph earns its place; deeper detail is linked rather than repeated.

## Sources

- [AGENTS.md format and usage](https://agents.md/): portable instruction files and scoped guidance. This skill intentionally shares content with README through a symlink rather than maintaining two separate documents.
- [Claude Code memory documentation](https://code.claude.com/docs/en/memory#agentsmd): current loading behavior; consult the migration reference for compatibility checks.
- [Callicrate authoring guidance](https://github.com/Callicrate/skills/blob/main/agents-md/SKILL.md): selective inspiration for proportional edits, policy preservation, and reference audits after moves.
- [Sentry agent documentation guidance](https://github.com/getsentry/skills/blob/main/skills/agents-md/SKILL.md): selective inspiration for focused checks and avoiding duplicated configuration. This skill retains its own unified README/AGENTS layout and content policy.
