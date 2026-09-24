# Report and citation checks

## Supported Markdown contract

Use [the template](../templates/report_template.md) for a saved report. It requires exactly one `Mode: quick|standard|deep|ultradeep` line and exactly one nonempty level-two heading for each of:

- Executive Summary
- Method and Scope
- Key Findings
- Counterevidence and Risks
- Recommendations
- Bibliography

Additional level-two sections may follow the bibliography; their contents are prose, not bibliography entries. ATX headings (`## Heading`) are supported; setext headings, HTML headings, reference-style link definitions, and platform-specific citation syntax are outside this format.

Use individual positive numeric markers (`[1]`, `[2]`) next to claims. Grouped/range forms (`[1,2]`, `[1–3]`) are unsupported. Each marker must resolve to one bibliography entry, and every entry must be cited outside the bibliography. Markers in fenced/indented code, inline code, HTML comments, or numeric inline Markdown links do not count as citations.

Each bibliography entry starts on a new line:

```text
[1] Author or organization (2026-09-20). "Source title". <https://example.com/source> Accessed: 2026-09-24.
```

Replace this illustrative source with one actually consulted. Publication values accept `YYYY`, `YYYY-MM-DD`, an ISO timestamp (timezone-aware timestamps normalize to UTC), or `n.d.`. Future publication dates trigger a review warning rather than an accusation of fabrication; forthcoming and online/print dates need judgment. An access date must be a valid date no later than the current UTC date.

Use straight double quotes around the title, one primary HTTP(S) URL in angle brackets (bare URLs also work), and `Accessed: YYYY-MM-DD`. Do not use Markdown link syntax for bibliography URLs. A DOI source uses its canonical `https://doi.org/...` URL. Continuation lines may use 0–3 leading spaces; four-space indentation denotes a code block. Version, venue, and access limitations can follow the required metadata. `{{...}}` is reserved for unfilled template placeholders.

The checker uses a small parser for this format, not a complete CommonMark implementation. It checks citation/bibliography matching and required fields; it cannot prove every factual claim has an appropriate citation or that a passage supports it. No word-count minimum, source quota, or automatic credibility score is imposed.

## Commands and results

Resolve `<skill-dir>` to this skill's actual directory; report paths may be absolute or relative to your current directory.

```bash
python3 "<skill-dir>/scripts/validate_report.py" "/absolute/path/to/report.md"
python3 "<skill-dir>/scripts/verify_citations.py" --report "/absolute/path/to/report.md" --strict
```

- `validate_report.py`: offline; accepts a positional path or the existing `--report`/`-r` option. Exit 0 means structural checks passed (warnings may remain), 1 means invalid structure or citation metadata, 2 means unreadable input or invalid CLI usage.
- `verify_citations.py`: networked bibliography check; does not check report sections or claim support. Invalid bibliography metadata always exits 1 before requests. With `--strict`, unresolved requests, date warnings, or DOI discrepancies also exit 1. Without `--strict`, those review items are printed but exit 0. Input/usage errors exit 2.
- `--timeout SECONDS` sets a per-request timeout for the citation checker (default 10, maximum 120). Requests are sequential; this is not a total runtime budget. Python's standard HTTP redirect handling applies.

The network checker tests the first source URL with HEAD and falls back to a bounded GET request when HEAD returns 405/501. For canonical DOI URLs it also requests CSL JSON metadata and compares normalized title and issued year. Discrepancies need manual review: online and print years can differ. A reachable URL is labeled reachable, never factually verified. A 403, 429, timeout, or metadata failure is unresolved, never proof of fabrication. Metadata responses are size-limited; page bodies are not downloaded by the reachability check.

Only run the network checker for source URLs appropriate to contact from this environment. It is not a browser or authenticated retriever and may fail on otherwise valid restricted sources. For those, verify through the available authorized retrieval tool and disclose the checker limitation.

## Regression tests

From the skill directory, using Python 3.10+:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "tests" -v
python3 "scripts/validate_report.py" "tests/fixtures/valid_report.md"
python3 "scripts/validate_report.py" "tests/fixtures/invalid_report.md"
```

The suite uses synthetic fixtures, an injected date where needed, and mocked HTTP responses; it makes no network calls. The valid fixture exits 0; the invalid fixture intentionally exits 1. Coverage includes bibliography-only markers, missing/unused/duplicate IDs, code/comment exclusion, multiline metadata, appendix boundaries, current/future/unknown dates, timezone offsets, HEAD fallback, DOI mismatches, malformed responses, timeouts, and CLI exit behavior.

## Workflow evaluations

These are agent behavior checks, separate from Python tests. Exercise them with the intended model and tool surface after a workflow change; record the tools, observed behavior, and any untested live integration. Do not claim a mock walkthrough proves live MCP compatibility.

| Scenario | Expected behavior |
| --- | --- |
| Quick API comparison; only search and scrape exposed | Uses those tools, reads official versioned sources, accepts one canonical source for its own contract, and gives a concise cited answer without a source quota. |
| Firecrawl missing, or a client exposes discovery without page retrieval | Discovers actual schemas; uses and discloses an available fallback. If explicitly Firecrawl-only, reports the access gap instead of inventing calls. |
| Agent returns processing, then completed or failed | Preserves the ID, polls with bounded delays, inspects final data and sources; failed/pending work remains a limitation. No report completion claim on submission. |
| Crawl is partial, paginated, or has per-page errors | Distinguishes MCP internal polling from API pagination, avoids infinite continuation loops, checks missing pages, and reports actual coverage. |
| Deep comparison with conflicting sources and embedded instructions | Ignores source instructions, traces shared origins, retains counterevidence, distinguishes facts/inference, and changes recommendations only when the evidence warrants it. |
