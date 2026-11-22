#!/usr/bin/env python3
"""Read-only audit of selected README/AGENTS pairs, obsolete CLAUDE companions and, on request, doc sizes."""

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


def instruction_doc(directory: Path) -> Path | None:
    """The canonical file an agent loads for this scope: what AGENTS.md resolves to, if anything."""
    agents = directory / "AGENTS.md"
    return resolved_file(agents) if agents.exists() else None


def read_allowlist(path: Path) -> set[Path]:
    """Canonical docs allowed over the nested limit, one path per line, relative to the list file."""
    entries = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            entries.add((path.parent / line).resolve())
    return entries


def check_sizes(
    roots: set[Path],
    scopes: set[Path],
    max_root_bytes: int | None,
    max_nested_chars: int | None,
    allowed: set[Path],
) -> list[str]:
    """Size problems, each doc counted once: a root scope's doc against bytes, any other against characters."""
    errors = []
    root_docs = {doc for doc in (instruction_doc(root) for root in roots) if doc}
    nested_docs = {doc for doc in (instruction_doc(scope) for scope in scopes) if doc} - root_docs

    if max_root_bytes is not None:
        for doc in sorted(root_docs):
            size = doc.stat().st_size
            if size > max_root_bytes:
                errors.append(f"{doc}: {size:,} bytes, over the root limit of {max_root_bytes:,}; move detail into the docs that own it")

    if max_nested_chars is not None:
        sizes = {doc: len(doc.read_text(encoding="utf-8")) for doc in nested_docs}
        for doc, chars in sorted(sizes.items()):
            if chars > max_nested_chars and doc not in allowed:
                errors.append(f"{doc}: {chars:,} characters, over the nested limit of {max_nested_chars:,}")
        # The allowlist only shrinks: an entry that no longer needs its exception has to go.
        for doc in sorted(allowed):
            if doc not in sizes:
                errors.append(f"{doc}: on the oversized list, but no checked AGENTS.md resolves to it; remove or update the entry")
            elif sizes[doc] <= max_nested_chars:
                errors.append(f"{doc}: now under the nested limit ({sizes[doc]:,} characters); remove its entry from the oversized list")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="*", default=["."], help="Selected scopes (default: current directory)")
    parser.add_argument("--recursive", action="store_true", help="Also audit all documentation scopes below each root")
    parser.add_argument("--max-root-bytes", type=int, metavar="N", help="Fail when a supplied root's instruction doc is over N bytes")
    parser.add_argument("--max-nested-chars", type=int, metavar="N", help="Fail when any other instruction doc is over N characters")
    parser.add_argument("--allow-oversized", type=Path, metavar="FILE", help="Shrink-only list of docs allowed over --max-nested-chars")
    args = parser.parse_args()
    if args.allow_oversized and args.max_nested_chars is None:
        parser.error("--allow-oversized needs --max-nested-chars")

    roots: set[Path] = set()
    scopes: set[Path] = set()
    scan_errors = []
    for name in args.directories:
        try:
            root = Path(name).resolve(strict=True)
        except (OSError, RuntimeError) as error:
            scan_errors.append(f"{name}: {error}")
            continue
        roots.add(root)
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
    if args.max_root_bytes is not None or args.max_nested_chars is not None:
        allowed = read_allowlist(args.allow_oversized) if args.allow_oversized else set()
        size_errors = check_sizes(roots, scopes, args.max_root_bytes, args.max_nested_chars, allowed)
        failures += len(size_errors)
        for error in size_errors:
            print(f"[FAIL] {error}")
    if failures:
        print(f"Result: {failures} violation(s); {len(scopes)} scope(s) checked.")
        return 1
    print(f"Result: OK ({len(scopes)} scope(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
