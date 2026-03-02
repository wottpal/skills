# Low-Context Drafting Workflow (For Large Docs)

When docs are large, do not jump directly to polished prose.

## Create Temporary Planning Files

Use a scratch directory:

```bash
mkdir -p .tmp/readme-doc-plan
```

Recommended files:

- `.tmp/readme-doc-plan/facts.md`
  - Verified facts only (paths, constants, versions, commands).
- `.tmp/readme-doc-plan/gaps.md`
  - Unknowns and what must be verified.
- `.tmp/readme-doc-plan/toc-options.md`
  - 2-3 outline candidates with pros/cons.
- `.tmp/readme-doc-plan/selected-outline.md`
  - Final section order with rationale.
- `.tmp/readme-doc-plan/snippets.md`
  - Command blocks and short policy statements to reuse.

## Process

1. Fill `facts.md` from code and config.
2. Generate at least two structure options in `toc-options.md`.
3. Pick one in `selected-outline.md` after comparing tradeoffs.
4. Draft final docs from selected outline.
5. Re-verify facts before finalizing.

## Lifecycle And Cleanup

- Keep planning artifacts out of version control by default (`.tmp/` in `.gitignore` or local exclude).
- Delete `.tmp/readme-doc-plan/` after the final docs are merged/applied.
- Persist planning files only when explicitly requested; move selected artifacts to an intentional tracked path.

## Why This Helps

- Reduces context pressure.
- Avoids early “local optimum” structure choices.
- Makes refactors safer because facts and structure are separated.
