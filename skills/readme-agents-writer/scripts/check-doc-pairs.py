#!/usr/bin/env python3
"""Read-only audit of selected README/AGENTS pairs and obsolete CLAUDE companions."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

SKIP_DIRS = {
    ".git", "node_modules", ".next", ".turbo", ".venv", "venv",
    ".pytest_cache", "__pycache__", "dist", "build", "vendor",
}
DOC_NAMES = {"README.md", "AGENTS.md", "CLAUDE.md"}


def resolved_file(path: Path) -> Path | None:
    try:
        target = path.resolve(strict=True)
        return target if target.is_file() else None
    except (OSError, RuntimeError):
        return None


def check_directory(directory: Path) -> list[str]:
    if not directory.is_dir():
        return ["scope is not a directory"]
    errors = []
    readme = directory / "README.md"
    agents = directory / "AGENTS.md"
    claude = directory / "CLAUDE.md"
    canonical = resolved_file(readme)

    if canonical is None or canonical.name != "README.md":
        errors.append("README.md must resolve to a regular canonical README.md")
    if not agents.is_symlink():
        errors.append("AGENTS.md must be a symlink; reconcile any standalone content first")
    else:
        target = resolved_file(agents)
        if target is None or canonical is None or target != canonical:
            errors.append("AGENTS.md must resolve to the same canonical README.md")
    if claude.exists() or claude.is_symlink():
        errors.append("legacy CLAUDE.md remains; preserve unique content before removing it")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="*", default=["."], help="Selected scopes (default: current directory)")
    parser.add_argument("--recursive", action="store_true", help="Also audit all documentation scopes below each root")
    args = parser.parse_args()
    scopes: set[Path] = set()
    scan_errors = []
    for name in args.directories:
        try:
            root = Path(name).resolve(strict=True)
        except (OSError, RuntimeError) as error:
            scan_errors.append(f"{name}: {error}")
            continue
        scopes.add(root)
        if args.recursive and root.is_dir():
            for current, dirs, files in os.walk(root, onerror=lambda error: scan_errors.append(str(error))):
                # Do not follow directory aliases into other scopes.
                if DOC_NAMES.intersection(files + dirs):
                    scopes.add(Path(current))
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not (Path(current) / d).is_symlink()]

    failures = len(scan_errors)
    for error in scan_errors:
        print(f"[FAIL] {error}")
    for directory in sorted(scopes):
        errors = check_directory(directory)
        failures += len(errors)
        for error in errors:
            print(f"[FAIL] {directory}: {error}")
    if failures:
        print(f"Result: {failures} violation(s); {len(scopes)} scope(s) checked.")
        return 1
    print(f"Result: OK ({len(scopes)} scope(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
