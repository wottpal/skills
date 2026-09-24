#!/usr/bin/env python3
"""Check bibliography URL reachability and DOI metadata; never verify claim support."""

import argparse
import json
from pathlib import Path
import re
from urllib import error, request
from urllib.parse import quote, unquote, urlsplit

from validate_report import Source, check_sources, parse_report


USER_AGENT = "DeepResearchCitationCheck/1.0"
METADATA_LIMIT = 1_000_000


def check_url(url: str, timeout: float = 10) -> tuple[bool, str]:
    """HEAD first, bounded GET fallback for servers that do not support HEAD."""
    for method in ("HEAD", "GET"):
        headers = {"User-Agent": USER_AGENT}
        if method == "GET":
            headers["Range"] = "bytes=0-0"
        try:
            req = request.Request(url, headers=headers, method=method)
            with request.urlopen(req, timeout=timeout) as response:
                status = response.status
                return 200 <= status < 300, f"HTTP {status} ({method}); reachability only"
        except error.HTTPError as exc:
            code = exc.code
            exc.close()
            if method == "HEAD" and code in {405, 501}:
                continue
            return False, f"HTTP {code}; access failure is not proof of fabrication"
        except (OSError, ValueError) as exc:
            return False, f"Request failed: {exc}"
    return False, "No usable response"


def normalize_title(title: str) -> str:
    return " ".join(re.findall(r"\w+", title.casefold()))


def check_doi(source: Source, timeout: float = 10) -> tuple[str, list[str]]:
    """Resolve canonical DOI URLs and compare metadata; discrepancies need review."""
    parts = urlsplit(source.url)
    if parts.hostname not in {"doi.org", "dx.doi.org"}:
        return "not applicable", []
    doi = unquote(parts.path.lstrip("/"))
    if not re.match(r"^10\.\d{4,9}/\S+$", doi):
        return "unresolved", ["Malformed DOI URL."]
    url = "https://doi.org/" + quote(doi, safe="/")
    req = request.Request(url, headers={
        "User-Agent": USER_AGENT, "Accept": "application/vnd.citationstyles.csl+json",
    })
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read(METADATA_LIMIT + 1)
        if len(raw) > METADATA_LIMIT:
            return "unresolved", ["DOI metadata response exceeded the size limit."]
        data = json.loads(raw)
        if not isinstance(data, dict):
            return "unresolved", ["DOI resolver did not return a metadata object."]
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            return "unresolved", ["DOI metadata has no usable title."]
        issues = []
        if normalize_title(source.title) != normalize_title(title):
            issues.append(f"Title differs from DOI metadata: {title!r}; review manually.")
        issued = data.get("issued")
        dates = issued.get("date-parts") if isinstance(issued, dict) else None
        year = dates[0][0] if isinstance(dates, list) and dates and isinstance(dates[0], list) and dates[0] else None
        if source.published != "n.d.":
            if not isinstance(year, int) or isinstance(year, bool):
                issues.append("DOI metadata has no usable issued year.")
            elif int(source.published[:4]) != year:
                issues.append(f"Issued year differs: report {source.published[:4]}, DOI {year}; review online/print dates.")
        return ("needs review" if issues else "metadata consistent"), issues
    except error.HTTPError as exc:
        code = exc.code
        exc.close()
        return "unresolved", [f"DOI metadata request failed: HTTP {code}."]
    except (OSError, ValueError) as exc:
        return "unresolved", [f"DOI metadata request failed: {exc}"]


def audit_source(source: Source, timeout: float = 10) -> tuple[str, list[str]]:
    reachable, detail = check_url(source.url, timeout)
    metadata, issues = check_doi(source, timeout)
    if not reachable:
        issues.insert(0, detail)
    return f"URL: {'reachable' if reachable else 'unresolved'}; DOI: {metadata}", issues


def positive_timeout(value: str) -> float:
    number = float(value)
    if not 0 < number <= 120:
        raise argparse.ArgumentTypeError("Timeout must be greater than 0 and at most 120 seconds.")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", "-r", required=True, type=Path)
    parser.add_argument("--strict", action="store_true", help="Exit 1 for unresolved links, metadata discrepancies, or date warnings.")
    parser.add_argument("--timeout", type=positive_timeout, default=10, help="Per-request timeout in seconds (default 10).")
    args = parser.parse_args(argv)
    try:
        report = parse_report(args.report.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: Cannot read report: {exc}")
        return 2
    errors, warnings = check_sources(report)
    for message in errors:
        print(f"ERROR: {message}")
    if errors:
        return 1
    for message in warnings:
        print(f"REVIEW: {message}")
    unresolved = bool(warnings)
    for source in report.sources:
        status, issues = audit_source(source, args.timeout)
        print(f"[{source.number}] {status}")
        for issue in issues:
            print(f"  REVIEW: {issue}")
        unresolved = unresolved or bool(issues)
    print("Claim support was not checked. Reachability and metadata cannot establish factual accuracy.")
    if unresolved:
        print("Unresolved checks remain; review the messages above.")
    return 1 if args.strict and unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
