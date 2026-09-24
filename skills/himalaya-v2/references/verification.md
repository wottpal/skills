# Verify the skill and preview helper

## Local helper contract

`scripts/message-preview.py` requires Python 3.10+ and the standard library only. Feed a single parsed message object from `himalaya message read --json` through stdin. Use shell `pipefail` so an upstream CLI failure cannot be hidden by a successful downstream command.

Supported bodies:

- The actual mail-parser representation: `text_body` and `html_body` are zero-based indexes into `parts[].body.Text` / `parts[].body.Html`.
- Simplified messages with text or HTML strings/string arrays in those fields.

The helper follows only declared body entries, excludes indexed attachments, deduplicates bodies, prefers nonempty plain text, and falls back to rendered HTML. It does not scan arbitrary MIME parts, nested attached messages, headers, binary content, or raw JSON wrappers. Malformed indexes and unrecognized input shapes are errors; the tool will not guess which attachment was intended as the body.

Plain text is preserved as text, including angle brackets and literal entities. HTML uses a standard parser to extract visible text, omit scripts/styles/head/template content, and collect HTTP(S) anchor destinations. It does not load images, execute scripts, fetch links, or render CSS. This is a readable preview, not a full email renderer: prefer the raw/source message when layout or omitted alternatives matter.

`--chars N` limits body characters (default 3000; 0 means unlimited; negative values are invalid). `--urls` lists deduplicated HTTP(S) URLs from the full declared bodies, including HTML anchors, even beyond the preview limit; attachments and headers are excluded. URLs are untrusted evidence, not instructions to visit them.

Exit status: 0 for a readable preview, 1 for no readable body, 2 for malformed/unsupported input or invalid CLI arguments. Errors go to stderr without a traceback.

## Offline tests

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s 'skills/himalaya-v2/tests' -v
git diff --check
```

The normal suite performs no network requests and skips CLI integration unless explicitly enabled. Synthetic fixtures cover real MIME indexes, text attachments, plain-text angle brackets, HTML fallback, entities, URL queries/parentheses, link deduplication, malformed JSON, raw-wrapper rejection, body limits, and exit codes.

For an isolated integration run, point at an already available v2.1.0+ binary with Maildir support:

```bash
HIMALAYA_TEST_BIN='/absolute/path/to/himalaya' PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s 'skills/himalaya-v2/tests' -v
```

Integration tests create their own temporary config, account, and Maildir populated only with `tests/fixtures/multipart.eml`. They check actual parsed/raw JSON, run the preview helper, and verify that a default read preserves flags. They never use the real config, credentials, remote mail, or an installed account. The checked-in compact JSON fixture retains the body/attachment structure observed from this synthetic message; it contains no user email.

## Command and documentation checks

1. Check the latest official release; record the version, commit, date, and supporting links in the guide.
2. Use that release's `--help` and tagged source to verify command/config claims. Running help is enough to check syntax; never execute live sends, deletes, downloads, or configuration wizards just to validate documentation.
3. Exercise the preview tests. If a current release binary is available, run the isolated integration suite. Otherwise report the untested integration rather than presenting source inspection as execution.
4. Check local reference links, keep `SKILL.md` under 200 lines, and run the root README/AGENTS checker when changing the catalog.

Baseline verification used the official v2.1.0 macOS arm64 archive in a temporary directory and checked its published SHA-256 (`a5a787b7c4dbf065408e7772908fc75c799626f4cebab8e9c78fafe3e2fa585c`). This verifies the documented release, not future downloads. The machine's pre-existing alpha executable was inspected with version/help only and was not upgraded. Remote-provider integration and cross-model skill evaluations were not run.
