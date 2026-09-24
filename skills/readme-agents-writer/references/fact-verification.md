# Fact Verification Checklist

For a small patch, verify affected claims and dependent references; expand the investigation if they reveal uncertainty or contradictions. For new documentation or a full rewrite, verify all factual claims, including retained ones. Existing documentation is evidence to investigate, not proof by itself.

## Facts And Policy

- Descriptive claims (a command exists, a dependency is installed, a directory contains generated files) need current implementation evidence.
- Prescriptive rules (do not edit generated files, use a particular package manager) derive from explicit user or repository policy. Existing violations do not make a rule obsolete.
- When policy and implementation disagree, preserve the policy, correct separable factual details, and report the mismatch. Ask only if completing the task requires resolving a substantive policy conflict.
- Do not promote an observed pattern into a mandatory convention without evidence that the repository intends it as policy.

## Paths And Names

From the target repository root, substitute actual quoted paths and search terms:

```bash
rg --files --hidden -g '!.git/**' -g '!node_modules/**' -g '!.venv/**'
test -e "path/to/file"
test -L "path/to/file"
rg -n --hidden -g '!.git/**' -g '!node_modules/**' -g '!.venv/**' -- 'EXACT_NAME' .
```

- Check spelling, case, definitions, and actual usage.
- `test -e` follows symlinks and fails for a dangling link; `test -L` identifies the link itself.
- Resolve link targets before editing. Read through a valid link only after confirming its target is in scope.
- Discovery may omit ignored paths. Inspect relevant known config directories explicitly rather than scanning dependency trees.
- Future output paths may not exist yet; label them as outputs instead of pretending they are present inputs.

## Commands

- Identify the actual task runner using manifests, lockfiles, configuration, and CI.
- Read command definitions and note the required working directory and environment.
- Prefer supported file- or package-scoped checks when they cover the change. Keep broader checks required by repository policy or CI, or needed for cross-package and integration behavior.
- Verify that a focused invocation still loads the intended configuration and covers its claimed scope. Do not invent file arguments for tools that require project context.
- Execute safe, relevant checks when practical; record their exit status and what they establish.
- Never run deployments, publishing, production migrations, or deletion commands just to check a documentation example. Inspect definitions or use an established non-mutating validation mode instead.
- Report an unavailable environment or skipped command accurately; do not turn missing tools into a successful check with `|| true`.

## Dependencies And Versions

- Use declared manifests and lockfiles for repository versions, not remembered defaults or whatever is globally installed.
- Distinguish a manifest range, a locked version, and an installed version when the difference matters.
- Detect current and older lockfile names (for example, both `bun.lock` and `bun.lockb`) rather than assuming one format.
- Verify runtime usage before describing a dependency's purpose.
- Check current official documentation when making external tool behavior or compatibility claims. Date those claims and link the source.
- Do not upgrade dependencies just to make documentation say "latest." Describe the repository as it exists unless an upgrade is requested.

## Links, Endpoints, And Examples

- Resolve local Markdown links relative to the document; after moving content, fix paths and heading anchors.
- Check shared READMEs from each alias location as well as their canonical location. Prefer a local pair with explicit links if relative links cannot work for all consumers.
- Verify referenced endpoints and payload shapes against implementation.
- Label illustrative examples; do not present invented paths, commands, or environment variables as working project facts.
- Avoid printing secrets when checking environment variable names or configuration.

## After Moves Or Renames

- Search the affected repository for the old file paths, directory names, command names, and link targets, including relevant hidden configuration. Inspect neighboring READMEs, examples, scripts, templates, and CI consumers.
- Update active references within the task's scope and report stale consumers outside it. Keep intentional historical references and migration examples when they are clearly labeled.
- Recheck relative links from each supported alias location and confirm that instructions still apply to the intended subtree. Edit the canonical README once for its AGENTS symlink.
- Record the search terms and any unresolved references in the final update or temporary working notes; do not create a permanent evidence file just for the search.

## Final Pass

- Recheck facts affected by the edit or migration, including consumers of removed filenames.
- Fix incorrect claims. Investigate useful but uncertain claims or mark the gap instead of silently deleting important operational guidance.
- Review the diff for lost instructions, accidental policy changes, unrelated modifications, and broken links.
- Report what was verified, what remains uncertain, and any command that was not run.
