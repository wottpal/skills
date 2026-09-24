# Migrate Legacy Documentation To README/AGENTS

The result is one canonical README, an `AGENTS.md` symlink resolving to it, and no `CLAUDE.md` companion in each selected documentation scope. Preserve valuable content and shared targets throughout the migration.

## Inventory Before Editing

1. Check the working-tree status and preserve existing edits. Identify the scopes the user actually requested.
2. Inspect README, AGENTS, and CLAUDE paths without following links first. Record link targets, including broken links and shared targets outside the directory.
3. Read all valid source files and compare their contents. Map every useful instruction to its destination; check facts before retaining them.
4. Look for consumers of the old layout in docs, CI, setup scripts, templates, imports, and hooks. Search hidden configuration explicitly where relevant.

From the target repository root:

```bash
git status --short
rg -n --hidden -g '!.git/**' -g '!node_modules/**' -g '!.venv/**' \
  'CLAUDE\.md|CLAUDE\.local\.md|set-doc-triplet|check-doc-triplets|@AGENTS\.md|SessionStart' .
```

Search results are candidates for inspection, not deletion instructions. Do not modify unrelated hooks, vendor fixtures, historical examples, personal files, or organization-managed instructions.

## Reconcile Content, Then Change Files

| Existing setup | Migration |
| --- | --- |
| README is canonical; AGENTS and CLAUDE link to it | Keep README and AGENTS; unlink CLAUDE only. |
| CLAUDE is a separate file | Merge verified unique guidance into README, resolve conflicts, then remove CLAUDE. |
| AGENTS is a separate file | Merge useful guidance into README, then replace AGENTS with a relative link to README. |
| README or AGENTS ultimately points to CLAUDE | Preserve the actual content as a real canonical README first, then retarget AGENTS and remove CLAUDE. Never leave a link chain depending on the removed name. |
| All files link to a shared README elsewhere | Keep the shared target and both remaining links if shared scope is justified. Unlink only the obsolete companion. |
| Link is broken, cyclic, or its target is unavailable | Recover or locate the intended content before deleting it; report unresolved targets rather than guessing. |
| CLAUDE only imports or tells the agent to read another file | Verify the referenced instructions are included or explicitly routed from the canonical README before removing the wrapper. |

- Do not blindly concatenate documents. Keep each instruction once, preserve its original scope, and resolve contradictions using the user's stated policy and repository evidence.
- A substantive conflict is a reason to ask a focused question; routine duplicate cleanup is not.
- Stage replacement content before unlinking a canonical source. Replacing a symlink means unlinking the link itself, never overwriting or deleting its target.
- When preserving referenced content, account for relative links and imports whose base directory changes.
- Never copy private local instructions into a tracked README without explicit authorization.

## Use The Helpers After Reconciliation

Resolve `<skill-dir>` to the installed skill directory, and pass the actual selected scope:

```bash
"<skill-dir>/scripts/set-doc-pair.sh" "<scope>"
python3 "<skill-dir>/scripts/check-doc-pairs.py" "<scope>"
```

The setter preflights the entire scope. It only replaces existing companions when their resolved contents exactly match the canonical README. A dangling link, different content, directory, or unsafe dependency on a removed path causes refusal before any changes. After manually merging a file, remove or replace that reviewed file explicitly; the helper cannot prove a semantic merge from differing bytes.

For a shared README, pass its relative path as the second setter argument. The helper flattens link chains ending at a real README. If CLAUDE itself holds the canonical content, first preserve it in a real canonical README before using the helper.

## Remove Obsolete Infrastructure

- Replace triplet setup/check commands with pair helpers in active workflows, then remove unused triplet-only scripts.
- Remove imports and bootstrap instructions whose sole purpose was loading the obsolete companion.
- Remove only the part of a startup hook that duplicates now-loaded instructions; preserve its other actions.
- Update descriptions, diagrams, and templates that still prescribe three files.
- Recheck all selected pairs, shared targets, relative links, and the diff. A clean structural audit does not prove content was preserved.
- Do not run the checker recursively unless every discovered documentation scope is intended to follow the pair contract.

## Claude Code Compatibility

Verified 2026-09-24 against [Claude Code's official memory documentation](https://code.claude.com/docs/en/memory#agentsmd):

- Native AGENTS loading starts at v2.1.277; some provider/session limitations were fixed in v2.1.281.
- Existing `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` in the working directory or its ancestors can suppress default AGENTS loading. Personal and managed instructions are outside this migration's deletion scope.
- Check Project instructions in `/config` and the built-in `agents-md` plugin if loading fails; verify in a fresh session.
- Loading is harness behavior, not a model capability. Update or configure incompatible harnesses; do not recreate a CLAUDE companion automatically.

Recheck the linked documentation when diagnosing compatibility. The README/AGENTS pair remains this skill's default.
