#!/usr/bin/env bash
set -euo pipefail

# Python handles paths and preflight checks without platform-specific readlink flags.
python3 - "$@" <<'PY'
import argparse
import os
from pathlib import Path
import sys


def present(path):
    return path.exists() or path.is_symlink()


def configure(directory, target):
    directory = Path(directory).resolve(strict=True)
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    if Path(target).is_absolute():
        raise ValueError("Use a target relative to the selected directory.")

    readme = directory / "README.md"
    agents = directory / "AGENTS.md"
    claude = directory / "CLAUDE.md"
    canonical = (directory / target).resolve(strict=True)
    if canonical.name != "README.md" or not canonical.is_file():
        raise ValueError("Target must resolve to a regular README.md; preserve legacy content there first.")
    content = canonical.read_bytes()

    # Check every affected path before making any changes. Different prose needs
    # human/agent reconciliation, even if one file appears to contain the other.
    for path in (readme, agents, claude):
        if not present(path):
            continue
        if not path.is_file():
            raise ValueError(f"Unresolved link or non-file at {path}; inspect it before migration.")
        if path.read_bytes() != content:
            raise ValueError(f"Content differs at {path}; merge unique instructions before replacing/removing it.")

    # Point directly at the resolved canonical file, avoiding chains through the
    # legacy companion that will be removed. Keep a local real README untouched.
    relative_target = os.path.relpath(canonical, directory)
    replacements = [agents] if canonical == readme else [readme, agents]
    for path in replacements:
        if path.is_symlink() and os.readlink(path) == relative_target:
            continue
        if present(path):
            path.unlink()
        path.symlink_to(relative_target)
    if present(claude):
        claude.unlink()
    print(f"OK: {directory}: AGENTS.md -> {relative_target}; no CLAUDE.md companion")


parser = argparse.ArgumentParser(
    description="Create a README/AGENTS pair and remove only an identical legacy CLAUDE companion."
)
parser.add_argument("directory", help="Existing documentation scope")
parser.add_argument("target", nargs="?", default="README.md", help="Relative canonical README path")
args = parser.parse_args()
try:
    configure(args.directory, args.target)
except (OSError, RuntimeError, ValueError) as error:
    print(f"Error: {error}", file=sys.stderr)
    sys.exit(1)
PY
