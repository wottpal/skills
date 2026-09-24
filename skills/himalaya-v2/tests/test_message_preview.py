"""Offline MIME regressions; fixtures contain only synthetic message content."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts/message-preview.py"
spec = importlib.util.spec_from_file_location("message_preview", SCRIPT)
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)
FIXTURE = SKILL_DIR / "tests/fixtures/multipart.json"


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.message = json.loads(FIXTURE.read_text())

    def test_indexed_mime_prefers_plain_and_excludes_attachments(self):
        bodies = preview.body_candidates(self.message)
        self.assertEqual(len(bodies), 1)
        self.assertIn("Hello <team>, 2 < 3 and 5 > 4.", bodies[0])
        self.assertNotIn("ATTACHMENT", bodies[0])
        self.assertNotIn("Read docs", bodies[0])

    def test_urls_are_not_truncated_at_s_or_extended_across_whitespace(self):
        self.assertEqual(preview.extract_urls(self.message), ["https://docs.example.com/search?q=skills&sort=asc"])

    def test_html_only_uses_visible_text_and_anchor_links(self):
        message = {"html_body": ['<p>First &amp; second</p><p><a href="https://example.com/search?a=1&amp;b=2">Details</a></p><img src="https://tracker.example.com/pixel"><script>ignore</script>']}
        self.assertEqual(preview.body_candidates(message), ["First & second\n\nDetails"])
        self.assertEqual(preview.extract_urls(message), ["https://example.com/search?a=1&b=2"])

    def test_nested_hidden_html_and_comments_are_excluded(self):
        text = '<head><style>secret</style><title>title</title></head><!-- comment --><p>Body</p><template>hidden</template>'
        self.assertEqual(preview.strip_html(text), "Body")

    def test_plain_text_is_not_interpreted_as_html_or_entities(self):
        text = 'Contact <person@example.com>; use <token> &amp; 2 < 3.'
        self.assertEqual(preview.body_candidates({"text_body": text}), [text])

    def test_string_arrays_are_supported_and_deduplicated(self):
        self.assertEqual(preview.body_candidates({"text_body": [" One ", "One", "Two"]}), ["One", "Two"])

    def test_empty_plain_falls_back_to_html(self):
        self.assertEqual(preview.body_candidates({"text_body": ["  "], "html_body": "<p>HTML</p>"}), ["HTML"])

    def test_indexed_html_fallback_preserves_its_type(self):
        message = {"text_body": [0], "html_body": [0], "parts": [{"body": {"Html": "<p>HTML &amp; entities</p>"}}]}
        self.assertEqual(preview.body_candidates(message), ["HTML & entities"])

    def test_attachment_index_cannot_become_body(self):
        self.message["text_body"].append(4)
        self.assertNotIn("ATTACHMENT", " ".join(preview.body_candidates(self.message)))

    def test_unknown_shapes_fail_instead_of_scanning_all_parts(self):
        for message in ([], None, {"error": "auth failed"}, {"message": "raw mail"}, {"parts": [{"body": {"Text": "attachment"}}]}):
            with self.subTest(message=message), self.assertRaises(ValueError):
                preview.body_candidates(message)

    def test_invalid_indexes_and_types_fail_clearly(self):
        for value in (-1, 99, True, {}, None):
            message = {"text_body": [value], "parts": [{"body": {"Text": "body"}}]}
            with self.subTest(value=value), self.assertRaises(ValueError):
                preview.body_candidates(message)

    def test_url_parentheses_and_trailing_punctuation(self):
        message = {"text_body": "See (https://example.com/docs_(test)). Then https://sample.example.org/results please."}
        self.assertEqual(preview.extract_urls(message), ["https://example.com/docs_(test)", "https://sample.example.org/results"])

    def test_headers_and_attachments_do_not_leak_into_urls(self):
        self.message["headers"] = [{"value": "https://header.example.com"}]
        urls = preview.extract_urls(self.message)
        self.assertFalse(any("header" in u or "attachment" in u or "tracker" in u for u in urls))

    def run_cli(self, data, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=data, text=True, capture_output=True, timeout=10)

    def test_cli_character_limit_and_full_body_links(self):
        result = self.run_cli(FIXTURE.read_text(), "--chars", "5", "--urls")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("Hello\n"))
        self.assertIn("https://docs.example.com/search?q=skills&sort=asc", result.stdout)

    def test_cli_unlimited_and_negative_limits(self):
        result = self.run_cli(json.dumps({"text_body": "x" * 4000}), "--chars", "0")
        self.assertEqual(result.stdout.strip(), "x" * 4000)
        self.assertEqual(self.run_cli("{}", "--chars", "-1").returncode, 2)

    def test_cli_empty_body_and_malformed_input_exit_codes(self):
        empty = self.run_cli(json.dumps({"text_body": [], "html_body": [], "parts": []}))
        self.assertEqual(empty.returncode, 1)
        self.assertIn("No readable", empty.stderr)
        for data in ("not json", "[]", '{"message":"raw RFC 5322"}'):
            with self.subTest(data=data):
                result = self.run_cli(data)
                self.assertEqual(result.returncode, 2)
                self.assertIn("ERROR:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
