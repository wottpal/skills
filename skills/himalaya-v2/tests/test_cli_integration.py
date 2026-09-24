"""Opt-in checks against a supplied Himalaya binary, using only a temporary Maildir."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = Path(__file__).resolve().parents[1]
BINARY = os.environ.get("HIMALAYA_TEST_BIN")


@unittest.skipUnless(BINARY, "Set HIMALAYA_TEST_BIN to test an isolated v2.1.0+ Maildir.")
class IsolatedMaildirTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="himalaya-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        mail = self.root / "mail" / "INBOX"
        for part in ("cur", "new", "tmp"):
            (mail / part).mkdir(parents=True)
        self.raw = (SKILL_DIR / "tests/fixtures/multipart.eml").read_text().replace("\n", "\r\n").encode()
        (mail / "cur/fixture:2,").write_bytes(self.raw)
        config = self.root / "config.toml"
        config.write_text('[accounts.fixture]\ndefault = true\nemail = "receiver@example.com"\nmaildir.root = ' + json.dumps(str(self.root / "mail")) + '\nmailbox.alias.inbox = "INBOX"\n')
        self.base = [BINARY, "-c", str(config), "-a", "fixture", "--backend", "maildir"]

    def command(self, *args):
        result = subprocess.run([*self.base, *args], capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        return result.stdout

    def test_real_json_preview_and_read_only_behavior(self):
        before = json.loads(self.command("envelope", "list", "-m", "INBOX", "--json"))
        parsed = self.command("message", "read", "-m", "INBOX", "fixture", "--json")
        data = json.loads(parsed)
        self.assertEqual(data["text_body"], [2])
        self.assertEqual(data["html_body"], [3])
        self.assertEqual(data["attachments"], [4])
        output = subprocess.run([sys.executable, str(SKILL_DIR / "scripts/message-preview.py"), "--urls"], input=parsed, capture_output=True, timeout=10)
        self.assertEqual(output.returncode, 0, output.stderr.decode())
        self.assertIn(b"Hello <team>, 2 < 3 and 5 > 4.", output.stdout)
        self.assertIn(b"https://docs.example.com/search?q=skills&sort=asc", output.stdout)
        self.assertNotIn(b"ATTACHMENT CONTENT", output.stdout)
        after = json.loads(self.command("envelope", "list", "-m", "INBOX", "--json"))
        self.assertEqual(before, after)
        self.assertEqual(before["envelopes"][0]["flags"], [])

    def test_raw_and_json_wrapper_match_original_bytes(self):
        raw = self.command("message", "read", "-m", "INBOX", "fixture", "--raw")
        wrapped = json.loads(self.command("message", "read", "-m", "INBOX", "fixture", "--raw", "--json"))
        self.assertEqual(raw, self.raw)
        self.assertEqual(wrapped["message"].encode(), self.raw)


if __name__ == "__main__":
    unittest.main()
