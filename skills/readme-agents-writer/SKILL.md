---
name: readme-agents-writer
description: Build and maintain unified README.md + AGENTS.md documentation with a canonical README and an AGENTS.md symlink. Use for writing or refactoring verified human and agent guidance, repairing documentation pairs, and migrating legacy CLAUDE.md companions without losing instructions.
---

# README/AGENTS Writer

## Mission

Produce documentation that works for both humans and coding agents:

- Make the canonical README useful first: accurate facts, current references, clear ownership, runnable commands, and operational guidance that lets agents and humans act safely.
- Keep instruction quality high enough for autonomous execution (guardrails, conventions, playbooks, do/don't rules, verification steps, and escalation rules).
- Keep one source of truth: a canonical `README.md` with an `AGENTS.md` symlink.
- Remove legacy `CLAUDE.md` companions after preserving useful, unique content.
- Keep guidance agent-agnostic: no model/vendor-specific logic unless a separate compatibility note is unavoidable.

Pair correctness supports the documentation; it is not a substitute for accurate, specific, high-signal content. Because `AGENTS.md` points to `README.md`, the README is the operational source of truth for both humans and agents.

## When To Use

- Creating or updating unified documentation pairs (`README.md`, `AGENTS.md`)
- Consolidating dedicated instruction files into a canonical README
- Cleaning up legacy `CLAUDE.md` files, symlinks, and triplet tooling
- Refactoring large docs while keeping agent guidance accurate, explicit, and current
- Strengthening weak instruction files that are vague, stale, or hard for agents to execute safely

## When Not To Use

- Repos that intentionally keep separate human and agent documentation and have not requested consolidation.
- Environments where symlinks are disallowed by policy/tooling.
- Requests that are only content edits where a different file-ownership policy is intentionally defined elsewhere.

## Non-Negotiables

### 1) Content Priority Policy (Canonical README Must Be Correct And Operational)

The first priority is the content quality of the canonical README:

- Verify project facts from source files, configs, commands, and current references.
- Preserve or add useful domain context, architecture notes, examples, troubleshooting, and cross-links.
- Correct stale claims, sharpen vague guidance, and investigate useful uncertain claims or mark the gap.
- Prefer a correct, scoped doc with clearly marked gaps over a polished structure containing weak facts.

The canonical `README.md` must include scope-appropriate agent-operational guidance:

- Scope and ownership boundaries
- Safety guardrails and non-negotiable constraints
- Conventions and coding standards (repo-specific, not generic)
- Engineering playbook (setup, test/lint/build, release, and troubleshooting)
- Do/Don't rules with concrete examples
- Verification workflow (how to prove claims and detect stale docs)
- Escalation policy for ambiguity, destructive actions, and risky operations

If this depth is missing, the documentation is incomplete even when symlinks are correct.

### 2) File Structure Policy (Pair Contract)

For any directory that owns this documentation unit, use one of these two allowed patterns:

1. Standard pattern
   - `README.md` is the canonical file in that directory.
   - `AGENTS.md -> README.md`

2. Shared-doc exception
   - `README.md` and `AGENTS.md` are symlinks to the same canonical `README.md` in another directory.
   - Use this only when all of these are true:
     - Same owner/team and release cadence.
     - Same audience and operational intent.
     - No directory-specific setup/rules that would diverge.

Never keep a dedicated/non-symlink `AGENTS.md` or a legacy `CLAUDE.md` companion in a migrated scope. Merge unique instructions into the canonical README before replacing or deleting files; never edit through a symlink without checking its target.
Avoid shared-doc mode when docs are expected to evolve independently.

Do not add pairs to every directory merely because it contains a README. Apply this contract to the documentation scopes selected for the task. For existing setups, read [Migration and cleanup](references/migration-and-cleanup.md).

## Required Commands

Default workflow (recommended):

```bash
"<skill-dir>/scripts/set-doc-pair.sh" "<dir>"
"<skill-dir>/scripts/set-doc-pair.sh" "<dir>" "<relative-path-to-canonical-README.md>"
python3 "<skill-dir>/scripts/check-doc-pairs.py" "<dir>"
```

The helpers require Python 3.10+; the setter also requires Bash. Resolve `<skill-dir>` to this skill's directory; scope paths are relative to the caller's working directory. The shared target is relative to `<dir>`. The setter refuses conflicting files and never decides which prose to discard. Resolve reported conflicts using the migration guide, then rerun. The checker accepts multiple scope paths; with no arguments it audits the current directory. `--recursive` explicitly audits every documentation scope below the supplied roots.

Instruction-quality review (always run during doc updates):

```bash
rg -n 'TODO|TBD|FIXME|maybe|probably|should be' "<canonical-README.md>"
python3 "<skill-dir>/scripts/check-doc-pairs.py" "<dir>"
```

Review search matches in context; no matches is normal (`rg` exits 1). The checker is read-only and exits nonzero for violations.

## Workflow

1. Choose scope and edit depth
   - Root doc, workspace/app/package/service doc, or module/feature doc.
   - For a small patch, preserve valid headings, order, and prose; inspect affected claims and their dependencies.
   - Use new outlines/templates only for new docs or an explicit substantial rewrite (load `references/scope-patterns.md`).
2. Build a verified fact inventory
   - Verify new or changed factual claims against live code/config; during a full rewrite, also verify retained facts.
   - Distinguish descriptive facts from repository policy. Preserve intentional constraints even when current code violates them; report the discrepancy.
   - Use `references/fact-verification.md`.
3. Confirm the selected scopes use the unified pair model
   - Honor the user's stated file policy; do not ask again when already specified.
   - Inventory legacy files and preserve unique instructions before migration.
4. For new docs or rewrites, design instruction architecture before prose
   - Separate hard constraints from preferences.
   - Convert vague guidance into trigger/action rules ("When X, do Y").
   - Keep rules agent-agnostic (do not assume one tool's private behavior model).
   - Plan sections for guardrails, conventions, playbooks, and escalation.
   - Link machine-enforced configuration instead of repeating its rules; retain non-obvious exceptions and unenforced conventions.
   - Use `references/agent-instruction-best-practices.md`.
5. For large rewrites, plan with temporary structure files
   - Use a task-specific scratch directory; skip this overhead for small edits.
   - Keep these as bullet/TODO artifacts, not full prose.
   - Use `references/low-context-drafting.md`.
6. Draft at the selected depth
   - For a small patch, edit the affected section without unrelated restructuring.
   - For a rewrite, establish structure, boundaries, rules, and commands first; then remove stale statements and duplication.
7. Migrate and validate the pair
   - Use `scripts/set-doc-pair.sh` after content reconciliation.
   - Remove obsolete CLAUDE companions, imports, hooks, and triplet checks within the selected scope.
   - Use `scripts/check-doc-pairs.py` for a read-only structural audit.
8. Run instruction quality QA
   - Check for ambiguity, contradictory rules, and missing failure-mode guidance.
   - Ensure there are repo-specific examples (good/bad where useful).
   - Prefer supported checks scoped to the affected files or package; retain required broader checks and those needed for integration coverage.
   - Re-check against `references/agent-instruction-best-practices.md`.
9. Final freshness pass
   - After moves or renames, search old paths, names, and commands in docs, examples, scripts, and CI. Fix in-scope consumers and report stale references outside scope.
   - Re-run verification commands for anything changed during writing.
   - Ensure scope-appropriate content (no root-only setup details in small module docs).

## Quality Bar

All of the following are required:

- Content is specific, verifiable, and operational.
- Commands are copy/paste ready and runnable from stated working dirs.
- Paths described as existing inputs resolve; output paths and illustrative examples are clearly labeled.
- Variable names and constants match code exactly and are used as described.
- Versions reflect currently installed/declared dependencies.
- Instructions use explicit trigger/action language, not soft ambiguity.
- Hard constraints are clearly marked as mandatory vs optional guidance.
- Safety-critical operations include confirmation/escalation rules.
- Examples demonstrate both compliant and non-compliant patterns where ambiguity risk is high.
- Wording stays agent-agnostic and portable across tooling.
- Long explanations live in linked docs; keep essential instructions and when to read each link in the canonical README.
- Selected pairs resolve correctly, unique legacy instructions survive, and removed filenames have no active consumers.

## References

- `references/scope-patterns.md`
- `references/fact-verification.md`
- `references/low-context-drafting.md`
- `references/agent-instruction-best-practices.md`
- `references/migration-and-cleanup.md`

## Scripts

- `scripts/set-doc-pair.sh`
- `scripts/check-doc-pairs.py`
