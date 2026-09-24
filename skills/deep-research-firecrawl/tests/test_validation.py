"""Offline regressions for report structure, dates, and optional network checks."""

from contextlib import redirect_stdout
from datetime import date, datetime, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from validate_report import (  # noqa: E402
    Source, parse_report, publication_date, validate_report,
)
import verify_citations as citations  # noqa: E402

VALID = (SKILL_DIR / "tests/fixtures/valid_report.md").read_text()
TODAY = date(2026, 9, 24)


class ReportTests(unittest.TestCase):
    def errors(self, text):
        return "\n".join(validate_report(text, TODAY)[0])

    def test_all_modes_accept_a_short_report_with_one_source(self):
        for mode in ("quick", "standard", "deep", "ultradeep"):
            with self.subTest(mode=mode):
                self.assertEqual(validate_report(VALID.replace("Mode: quick", f"Mode: {mode}"), TODAY), ([], []))

    def test_bibliography_is_not_a_body_citation(self):
        text = (SKILL_DIR / "tests/fixtures/invalid_report.md").read_text()
        self.assertIn("No numeric citations", self.errors(text))
        self.assertIn("never cited", self.errors(text))

    def test_unused_missing_and_duplicate_ids(self):
        cases = (
            (VALID.replace("finding [1]", "finding [2]"), "[2] has no bibliography"),
            (VALID + '\n## Bibliography\n[1] Other (2024). "Title". <https://example.com> Accessed: 2024-06-01.', "Duplicate bibliography"),
            (VALID.replace("## Appendix", '[2] Other (2024). "Title". <https://example.com/other> Accessed: 2024-06-01.\n\n## Appendix'), "[2] is never cited"),
        )
        for text, expected in cases:
            with self.subTest(expected=expected):
                self.assertIn(expected, self.errors(text))

    def test_examples_and_links_cannot_supply_body_citations(self):
        bib = VALID.index("## Bibliography")
        uncited = VALID[:bib].replace("[1]", "") + VALID[bib:]
        for example in ("`[1]`", "``[1]``", "```md\n[1]\n```", "~~~\n[1]\n~~~", "    [1]", "<!-- [1] -->", "[1](https://example.com)", "\\[1]", "![1](image.png)"):
            with self.subTest(example=example):
                text = uncited.replace("## Key Findings", example + "\n\n## Key Findings")
                self.assertIn("No numeric citations", self.errors(text))

    def test_headings_in_code_cannot_supply_missing_section(self):
        text = VALID.replace("## Recommendations", "```md\n## Recommendations\n```")
        self.assertIn("'Recommendations' section", self.errors(text))

    def test_empty_duplicate_or_deeper_required_heading_fails(self):
        cases = (
            VALID.replace("## Recommendations", "### Recommendations"),
            VALID + "\n## Recommendations\nExtra section.",
            VALID.replace("Use this fixture only to exercise structural checks.", "<!-- no content -->"),
        )
        for text in cases:
            with self.subTest(text=text[-80:]):
                self.assertTrue(self.errors(text))

    def test_multiline_bibliography_and_appendix_boundaries(self):
        text = VALID.replace('"Synthetic source". <', '"Synthetic source".\n  <')
        text += "\nThe appendix also cites [1].\n"
        report = parse_report(text)
        self.assertEqual(report.sources[0].url, "https://example.com/source")
        self.assertEqual(report.sources[0].accessed, "2024-06-01")
        self.assertNotIn("appendix", report.sources[0].text.lower())
        self.assertEqual(self.errors(text), "")

    def test_bibliography_comment_and_fenced_examples_are_ignored(self):
        text = VALID.replace("## Appendix", "<!-- [99] Fake -->\n```md\n[99] Fake\n```\n## Appendix")
        self.assertEqual(self.errors(text), "")

    def test_unfilled_template_is_rejected(self):
        template = (SKILL_DIR / "templates/report_template.md").read_text()
        self.assertIn("Unfilled template", self.errors(template))

    def test_missing_or_invalid_mode_and_source_fields(self):
        for before, after in (
            ("Mode: quick", "Mode: marathon"),
            ("Mode: quick", "Mode: quick\nMode: deep"),
            ('"Synthetic source"', "Synthetic source"),
            ("2024-05-01", "2024-02-30"),
            ("Accessed: 2024-06-01", "Accessed: unknown"),
            ("https://example.com/source", "file:///tmp/source"),
            ("https://example.com/source", "https://user:password@example.com/source"),
            ("[1]", "[0]"),
        ):
            with self.subTest(before=before, after=after):
                self.assertTrue(self.errors(VALID.replace(before, after)))

    def test_current_year_and_unknown_dates_are_valid(self):
        for published in ("2026", "2026-09-20", "2026-09-20T00:00:00Z", "n.d."):
            with self.subTest(published=published):
                self.assertEqual(validate_report(VALID.replace("2024-05-01", published), TODAY), ([], []))

    def test_default_year_tracks_the_clock(self):
        current = str(datetime.now(timezone.utc).year)
        self.assertEqual(validate_report(VALID.replace("2024-05-01", current)), ([], []))

    def test_timezone_dates_normalize_without_naive_aware_subtraction(self):
        self.assertEqual(publication_date("2026-09-20T00:00:00Z"), date(2026, 9, 20))
        self.assertEqual(publication_date("2026-09-20T00:30:00+02:00"), date(2026, 9, 19))

    def test_future_publication_warns_but_future_access_fails(self):
        errors, warnings = validate_report(VALID.replace("2024-05-01", "2027"), TODAY)
        self.assertEqual(errors, [])
        self.assertIn("future", warnings[0])
        self.assertIn("Access date cannot be in the future", self.errors(VALID.replace("Accessed: 2024-06-01", "Accessed: 2027-01-01")))

    def test_cli_fixture_exit_codes_and_read_error(self):
        for filename, expected in (("valid_report.md", 0), ("invalid_report.md", 1), ("absent.md", 2)):
            with self.subTest(filename=filename):
                result = subprocess.run([sys.executable, str(SKILL_DIR / "scripts/validate_report.py"), str(SKILL_DIR / "tests/fixtures" / filename)], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_cli_preserves_report_flag_and_rejects_ambiguous_input(self):
        path = str(SKILL_DIR / "tests/fixtures/valid_report.md")
        for args, expected in ((["--report", path], 0), (["-r", path], 0), ([], 2), ([path, "--report", path], 2)):
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, str(SKILL_DIR / "scripts/validate_report.py"), *args], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)


class FakeResponse(io.BytesIO):
    def __init__(self, content=b"", status=200):
        super().__init__(content)
        self.status = status


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.source = Source(1, "", "Fixture", "2026", "A study of testing", "https://doi.org/10.5555/test", "2026-09-24")

    def test_head_405_and_501_fall_back_to_get(self):
        for code in (405, 501):
            with self.subTest(code=code), patch.object(citations.request, "urlopen", side_effect=[HTTPError(self.source.url, code, "unsupported", {}, None), FakeResponse(status=206)]) as mocked:
                ok, detail = citations.check_url(self.source.url)
                self.assertTrue(ok)
                self.assertIn("GET", detail)
                self.assertEqual([call.args[0].method for call in mocked.call_args_list], ["HEAD", "GET"])
                self.assertEqual(mocked.call_args.args[0].get_header("Range"), "bytes=0-0")

    def test_access_failures_and_timeouts_remain_unresolved(self):
        for failure in (HTTPError(self.source.url, 403, "restricted", {}, None), HTTPError(self.source.url, 429, "limited", {}, None), URLError("network unavailable"), TimeoutError("timeout")):
            with self.subTest(failure=failure), patch.object(citations.request, "urlopen", side_effect=failure) as mocked:
                ok, _ = citations.check_url(self.source.url)
                self.assertFalse(ok)
                self.assertEqual(mocked.call_count, 1)

    def test_any_successful_2xx_is_reachable_only(self):
        with patch.object(citations.request, "urlopen", return_value=FakeResponse(status=204)):
            ok, detail = citations.check_url(self.source.url)
            self.assertTrue(ok)
            self.assertIn("reachability only", detail)

    def test_realistic_generic_title_is_not_a_fabrication_heuristic(self):
        payload = {"title": "A Study of Testing", "issued": {"date-parts": [[2026]]}}
        with patch.object(citations.request, "urlopen", return_value=FakeResponse(json.dumps(payload).encode())):
            self.assertEqual(citations.check_doi(self.source), ("metadata consistent", []))

    def test_reachable_url_does_not_erase_doi_mismatch(self):
        with patch.object(citations, "check_url", return_value=(True, "HTTP 200")), patch.object(citations.request, "urlopen", return_value=FakeResponse(b'{"title":"Different title","issued":{"date-parts":[[2025]]}}')):
            status, issues = citations.audit_source(self.source)
            self.assertIn("needs review", status)
            self.assertEqual(len(issues), 2)

    def test_malformed_or_incomplete_doi_metadata_does_not_crash(self):
        for payload in (b"not json", b"[]", b'{}', b'{"title":[]}', b'{"title":"A study of testing","issued":null}', b'{"title":"A study of testing","issued":{"date-parts":[[]]}}', b"x" * (citations.METADATA_LIMIT + 1)):
            with self.subTest(payload=payload[:60]), patch.object(citations.request, "urlopen", return_value=FakeResponse(payload)):
                status, issues = citations.check_doi(self.source)
                self.assertNotEqual(status, "metadata consistent")
                self.assertTrue(issues)

    def test_malformed_doi_is_rejected_without_request(self):
        self.source.url = "https://doi.org/not-a-doi"
        with patch.object(citations.request, "urlopen") as mocked:
            self.assertEqual(citations.check_doi(self.source)[0], "unresolved")
            mocked.assert_not_called()

    def test_non_doi_url_skips_metadata_request(self):
        self.source.url = "https://example.com/10.5555/test"
        with patch.object(citations.request, "urlopen") as mocked:
            self.assertEqual(citations.check_doi(self.source), ("not applicable", []))
            mocked.assert_not_called()

    def run_cli(self, text, strict=False, issues=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.md"
            path.write_text(text)
            args = ["--report", str(path)] + (["--strict"] if strict else [])
            with patch.object(citations, "audit_source", return_value=("URL: unresolved", issues or [])) as audit, redirect_stdout(io.StringIO()) as output:
                result = citations.main(args)
            return result, audit.call_count, output.getvalue()

    def test_strict_and_advisory_exit_codes(self):
        self.assertEqual(self.run_cli(VALID, strict=True, issues=["timeout"])[0], 1)
        code, _, output = self.run_cli(VALID, issues=["timeout"])
        self.assertEqual(code, 0)
        self.assertIn("Unresolved checks remain", output)
        self.assertIn("Claim support was not checked", output)
        self.assertEqual(self.run_cli(VALID, strict=True)[0], 0)

    def test_successful_network_audit_preserves_future_date_warning(self):
        future = str(datetime.now(timezone.utc).year + 1)
        self.assertEqual(self.run_cli(VALID.replace("2024-05-01", future), strict=True)[0], 1)

    def test_invalid_bibliography_fails_before_network_even_without_strict(self):
        code, calls, _ = self.run_cli(VALID.replace("Accessed: 2024-06-01", ""))
        self.assertEqual((code, calls), (1, 0))


if __name__ == "__main__":
    unittest.main()
