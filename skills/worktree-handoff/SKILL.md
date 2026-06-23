---
name: worktree-handoff
description: Safely hand off the current source worktree state, including untracked files, onto a local target branch without modifying the source worktree, using an alternate-index snapshot and target-side cherry-pick.
---

# Worktree Handoff

## Mission

Reproduce the current source worktree state onto a local target branch. If the user does not name a target branch, choose the default target from the current worktree context.

The source worktree must look the same before and after the handoff. The handoff only changes the destination branch/worktree.

## When To Use

- User wants current worktree changes moved onto another local branch.
- Untracked files must come along with tracked edits.
- The repo uses multiple worktrees and the target branch may already have one.

## Non-Negotiables

- Default target branch:
  - If the user named a target branch, use it.
  - If no target is named and the current source is a linked worktree, use the current source branch as the canonical destination branch.
  - If no target is named and the source is detached, first check `git worktree list --porcelain` for same-HEAD branch worktrees before falling back to `develop`.
  - Never use `develop` as the detached fallback until same-HEAD branch worktrees have been checked.
- Source worktree state is invariant. Do not clear it, clean it, switch it, reset it, restore it, or stash/pop/apply from it as part of the handoff.
- Do not update the destination branch with `pull`, `merge`, `rebase`, or `reset` as part of the handoff. Apply onto the destination's current local state.
- Do not use destructive git commands.
- Prefer the target branch's existing worktree if one already exists.
- Existing local changes on the target branch are allowed. Minor dirtiness such as lockfile churn is not a blocker; apply on top and let Git report whether a real conflict exists.
- After applying, always inspect for conflicts and report them before resolving anything.
- If a temporary target worktree is created, report its path and leave it in place unless the user asks for cleanup.
- A clean source worktree after handoff is not a success signal. If the source became clean, something went wrong unless the user explicitly asked for cleanup.

## Fast Non-Mutating Workflow

### 1) Preflight

```bash
git status --short --branch
git worktree list --porcelain
```

- Capture the source status first; it must match again after the handoff.
- `git status --short --branch` replaces separate branch and status checks.
- If `HEAD` is detached, use the short commit SHA as the source ref in the report.
- When resolving an implicit target, state which rule selected it before applying anything.
- If there are no source changes, stop and say there is nothing to hand off.

### 2) Resolve the default target branch

Only do this if the user did not specify a target branch.

- Parse `git worktree list --porcelain`; entries are separated by `worktree <path>` lines and may include `HEAD <sha>` and `branch refs/heads/<name>`.
- If the source is not detached, the source path differs from the first/main worktree path, and `git status --short --branch` shows a local branch, default the target to that source branch name. Report: "Source is a linked worktree on `<branch>`, so defaulting target to `<branch>`."
- If the source is detached, get the source `HEAD` SHA and find other worktree entries with the same `HEAD <sha>` and a `branch refs/heads/<name>` line.
- If exactly one same-HEAD branch worktree exists, default the target to that branch. Report: "Source is detached at <sha>, but main/root worktree at the same HEAD is on `<branch>`, so defaulting target to `<branch>`." If the matching branch worktree is not the main/root worktree, name its path instead of "main/root worktree".
- If multiple same-HEAD branch worktrees exist, stop and ask which branch to use. List the candidate branch names and worktree paths.
- If no same-HEAD branch worktree exists, default the target to `develop`. Report: "Source is detached at <sha> and no same-HEAD branch worktree exists, so defaulting target to `develop`."
- Do not default a detached source to `develop` before completing the same-HEAD branch worktree check.

Example Codex linked-worktree case:

```text
worktree /repo
HEAD abc1234
branch refs/heads/feature/foo

worktree /repo/.codex/worktrees/task
HEAD abc1234
detached
```

If the source path is `/repo/.codex/worktrees/task` and no target was specified, default to `feature/foo`, not `develop`, because the main/root worktree is on `feature/foo` at the same HEAD.

### 3) Resolve the target worktree

- If `git worktree list --porcelain` already shows `branch refs/heads/<target-branch>` in a worktree other than the source worktree, use that worktree path.
- Otherwise, create a sibling temporary worktree for the target branch instead of forcing a branch switch in the current worktree.
- If Git refuses because the target branch is already checked out by the source worktree, create the temporary destination with `--force`; never use the source worktree itself as the destination.

```bash
git worktree add "../<repo>-handoff-<target-branch>" "<target-branch>"
# only when Git says the branch is already checked out by the source worktree:
git worktree add --force "../<repo>-handoff-<target-branch>" "<target-branch>"
```

- If the target branch does not exist locally, stop and ask whether it should be created from `origin/<target-branch>` or another base.

### 4) Build a non-mutating snapshot from the source worktree

```bash
tmpdir=$(mktemp -d)
base=$(git rev-parse HEAD)
alt_index="$tmpdir/handoff.index"
cp "$(git rev-parse --git-path index)" "$alt_index"
GIT_INDEX_FILE="$alt_index" git add -A
snapshot_tree=$(GIT_INDEX_FILE="$alt_index" git write-tree)
snapshot_commit=$(printf 'worktree-handoff snapshot\n' | git commit-tree "$snapshot_tree" -p "$base")
```

- This captures tracked, staged, unstaged, and untracked paths without touching the real source index or worktree.
- `snapshot_commit` is temporary and does not update any branch ref.
- This handoff preserves the source worktree contents, not the exact staged/unstaged split. The destination will typically receive the snapshot as staged changes.

### 5) Check the target before applying

```bash
git -C "<target-worktree>" status --short
```

- Existing tracked changes and non-colliding untracked files are fine, including small unrelated dirtiness such as `bun.lock` updates. Do not stop just because the destination is dirty.
- If the target already has colliding untracked paths, report the collision instead of forcing the handoff.

### 6) Apply the handoff onto the target branch

```bash
git -C "<target-worktree>" cherry-pick -n "$snapshot_commit"
```

- This applies the source snapshot only in the target worktree. The source worktree must remain untouched.
- Stop on conflicts and report them. Do not resolve them silently.
- Do not run `git stash push`, `git stash pop`, or `git stash apply` in the source worktree.

### 7) Verify the result

```bash
git status --short --branch
git -C "<target-worktree>" diff --name-only --diff-filter=U
git -C "<target-worktree>" status --short
```

- Confirm the source status matches the preflight snapshot. If it differs, report an unexpected source mutation immediately.
- The target should now contain the handed-off snapshot.

## Reporting Rules

- If the apply succeeds cleanly, report:
  - source ref/worktree
  - target branch/worktree
  - whether the target already had local changes
  - whether the source status matched before/after exactly
  - whether a temporary target worktree was created
  - that the destination received a staged snapshot of the source state
- If there are conflicts, stop after applying and report:
  - conflicted files
  - whether the target branch already had overlapping edits
  - that the source worktree remained unchanged
  - the most likely resolution approach

Even if a conflict looks trivial, do not silently resolve it. Ask how to proceed after summarizing the conflict.

Never describe success as "the source worktree is now clean again". If the user wants the source cleaned after verification, that is a separate explicit follow-up step.
