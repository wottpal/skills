#!/usr/bin/env python3
"""
Audit README/AGENTS/CLAUDE triplets and print actionable fix commands.

Allowed patterns per directory that contains README.md:
1) Standard:
   - README.md is a regular file
   - AGENTS.md and CLAUDE.md are symlinks resolving to README.md
2) Shared-doc exception:
   - README.md, AGENTS.md, CLAUDE.md are symlinks that all resolve
     to the same canonical README in another directory.
"""

from __future__ import annotations

import os
import pathlib
import sys

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".next",
    ".turbo",
    ".venv",
    ".pytest_cache",
}


def quote(path: str) -> str:
    return "'" + path.replace("'", "'\"'\"'") + "'"


def print_standard_fix(directory: pathlib.Path) -> None:
    print(f"  cd {quote(str(directory))}")
    print("  ln -snf README.md AGENTS.md")
    print("  ln -snf README.md CLAUDE.md")


def print_shared_fix(directory: pathlib.Path, target: str) -> None:
    print(f"  cd {quote(str(directory))}")
    print(f"  TARGET={quote(target)}")
    print('  ln -snf "$TARGET" README.md')
    print('  ln -snf "$TARGET" AGENTS.md')
    print('  ln -snf "$TARGET" CLAUDE.md')


def print_inferred_shared_or_standard_fix(
    directory: pathlib.Path, readme: pathlib.Path, agents: pathlib.Path, claude: pathlib.Path
) -> None:
    target = infer_shared_target(directory, readme, agents, claude)
    if target is not None:
        print_shared_fix(directory, target)
        return
    print("  # Could not infer a valid shared README target from current symlinks.")
    print("  # Apply standard mode fix, or replace README.md target with a valid canonical README.")
    print_standard_fix(directory)


def resolved(path: pathlib.Path) -> pathlib.Path | None:
    try:
        return path.resolve(strict=True)
    except (FileNotFoundError, OSError, RuntimeError):
        return None


def is_symlink(path: pathlib.Path) -> bool:
    return path.is_symlink()


def infer_shared_target(
    directory: pathlib.Path, readme: pathlib.Path, agents: pathlib.Path, claude: pathlib.Path
) -> str | None:
    candidates: list[pathlib.Path] = []
    for link_path in (readme, agents, claude):
        if not link_path.is_symlink():
            continue
        resolved_target = resolved(link_path)
        if resolved_target is None:
            continue
        if resolved_target.name != "README.md":
            continue
        candidates.append(resolved_target)

    if not candidates:
        return None

    canonical = candidates[0]
    try:
        return os.path.relpath(str(canonical), str(directory))
    except ValueError:
        return str(canonical)


def check_directory(directory: pathlib.Path) -> int:
    errors = 0
    readme = directory / "README.md"
    agents = directory / "AGENTS.md"
    claude = directory / "CLAUDE.md"

    if not readme.exists() and not readme.is_symlink():
        return 0

    missing = [name for name, p in (("AGENTS.md", agents), ("CLAUDE.md", claude)) if not (p.exists() or p.is_symlink())]
    if missing:
        errors += 1
        print(f"[FAIL] {directory}: missing {', '.join(missing)}")
        print("  Fix commands:")
        if readme.is_symlink():
            print_inferred_shared_or_standard_fix(directory, readme, agents, claude)
        else:
            print_standard_fix(directory)
        print()

    if missing:
        return errors

    if readme.is_symlink():
        # Shared-doc exception path: all three must be symlinks to same resolved target.
        if not (is_symlink(agents) and is_symlink(claude)):
            errors += 1
            print(f"[FAIL] {directory}: shared-doc mode requires README/AGENTS/CLAUDE all symlinks")
            print("  Fix commands:")
            print_inferred_shared_or_standard_fix(directory, readme, agents, claude)
            print()
            return errors

        targets = [resolved(readme), resolved(agents), resolved(claude)]
        if any(t is None for t in targets) or len(set(targets)) != 1:
            errors += 1
            print(f"[FAIL] {directory}: README/AGENTS/CLAUDE symlinks must resolve to same target")
            print("  Fix commands:")
            print_inferred_shared_or_standard_fix(directory, readme, agents, claude)
            print()
        return errors

    # Standard mode path: AGENTS and CLAUDE must be symlinks to local README.
    if not is_symlink(agents):
        errors += 1
        print(f"[FAIL] {directory}: AGENTS.md must be a symlink")
        print("  Fix commands:")
        print_standard_fix(directory)
        print()
    if not is_symlink(claude):
        errors += 1
        print(f"[FAIL] {directory}: CLAUDE.md must be a symlink")
        print("  Fix commands:")
        print_standard_fix(directory)
        print()

    if errors:
        return errors

    readme_target = resolved(readme)
    if resolved(agents) != readme_target or resolved(claude) != readme_target:
        errors += 1
        print(f"[FAIL] {directory}: AGENTS.md and CLAUDE.md must resolve to README.md")
        print("  Fix commands:")
        print_standard_fix(directory)
        print()

    return errors


def main() -> int:
    root = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else pathlib.Path.cwd().resolve()

    failures = 0
    checked = 0
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if "README.md" not in filenames:
            continue
        directory = pathlib.Path(current_root)
        checked += 1
        failures += check_directory(directory)

    if failures:
        print(f"Result: {failures} violation(s) across {checked} README directory(ies).")
        return 1

    print(f"Result: OK ({checked} README directory(ies) checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
