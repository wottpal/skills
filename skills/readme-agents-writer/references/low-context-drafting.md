# Low-Context Drafting Workflow (For Large Docs)

Use this workflow for large restructures or migrations with several conflicting sources. For a small edit, keep a short outline in working context and edit directly.

## Create Temporary Planning Files

Use a unique scratch directory outside the repository:

```bash
doc_plan_dir="$(mktemp -d "${TMPDIR:-/tmp}/readme-doc-plan.XXXXXX")"
```

Recommended files:

- `facts.md`
  - Verified facts only (paths, constants, versions, commands).
- `gaps.md`
  - Unknowns and what must be verified.
- `toc-options.md`
  - 2-3 outline candidates with pros/cons.
- `selected-outline.md`
  - Final section order with rationale.
- `snippets.md`
  - Command blocks and short policy statements to reuse.

## Process

1. Fill `facts.md` from code and config.
2. Generate at least two structure options in `toc-options.md`.
3. Pick one in `selected-outline.md` after comparing tradeoffs.
4. Draft final docs from selected outline.
5. Re-verify facts before finalizing.

## Lifecycle And Cleanup

- Create these files inside the recorded `doc_plan_dir`; no repository ignore-rule changes are needed.
- After applying the docs, remove only the scratch files and directory created for this task. Never clear a pre-existing planning directory or another agent's files.
- Persist planning files only when explicitly requested; move selected artifacts to an intentional tracked path.

## Why This Helps

- Reduces context pressure.
- Avoids early “local optimum” structure choices.
- Makes refactors safer because facts and structure are separated.
