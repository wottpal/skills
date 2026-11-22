"""Offline regressions for the pair checker's size options."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CHECKER = Path(__file__).resolve().parents[1] / "scripts" / "check-doc-pairs.py"


def make_scope(directory: Path, size: int) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "README.md").write_text("x" * size, encoding="utf-8")
    os.symlink("README.md", directory / "AGENTS.md")


class SizeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_checker(self, *args):
        result = subprocess.run(
            [sys.executable, str(CHECKER), str(self.root), "--recursive", *args],
            capture_output=True, text=True,
        )
        return result.returncode, result.stdout

    def test_passes_docs_at_their_limits(self):
        make_scope(self.root, 100)
        make_scope(self.root / "a", 50)
        code, out = self.run_checker("--max-root-bytes", "100", "--max-nested-chars", "50")
        self.assertEqual(code, 0, out)

    def test_names_the_root_and_a_nested_doc_over_their_limits(self):
        make_scope(self.root, 101)
        make_scope(self.root / "a", 51)
        code, out = self.run_checker("--max-root-bytes", "100", "--max-nested-chars", "50")
        self.assertEqual(code, 1)
        self.assertIn("over the root limit of 100", out)
        self.assertIn("over the nested limit of 50", out)

    def test_a_shared_doc_is_counted_once_under_its_own_path(self):
        make_scope(self.root, 10)
        make_scope(self.root / "a", 60)
        (self.root / "b").mkdir()
        os.symlink("../a/README.md", self.root / "b" / "README.md")
        os.symlink("../a/README.md", self.root / "b" / "AGENTS.md")
        code, out = self.run_checker("--max-nested-chars", "50")
        self.assertEqual(code, 1)
        self.assertEqual(out.count("over the nested limit"), 1, out)

    def test_a_readme_without_an_agents_link_is_not_counted(self):
        make_scope(self.root, 10)
        (self.root / "vendor-like").mkdir()
        (self.root / "vendor-like" / "notes").mkdir()
        (self.root / "vendor-like" / "notes" / "README.md").write_text("x" * 500)
        code, out = self.run_checker("--max-nested-chars", "50")
        self.assertNotIn("over the nested limit", out)

    def test_the_allowlist_only_shrinks(self):
        make_scope(self.root, 10)
        make_scope(self.root / "big", 60)
        make_scope(self.root / "thinned", 20)
        allow = self.root / "oversized.txt"
        allow.write_text("# docs over the limit\nbig/README.md\nthinned/README.md\ngone/README.md\n")
        code, out = self.run_checker("--max-nested-chars", "50", "--allow-oversized", str(allow))
        self.assertEqual(code, 1)
        self.assertNotIn("big/README.md: 60", out)
        self.assertIn("thinned/README.md: now under the nested limit", out)
        self.assertIn("gone/README.md: on the oversized list", out)


if __name__ == "__main__":
    unittest.main()
