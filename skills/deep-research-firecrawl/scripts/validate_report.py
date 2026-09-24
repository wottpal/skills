#!/usr/bin/env python3
"""Offline structure checks for the skill's documented Markdown report format."""

import argparse
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
import re
from urllib.parse import urlsplit


SECTIONS = (
    "Executive Summary", "Method and Scope", "Key Findings",
    "Counterevidence and Risks", "Recommendations", "Bibliography",
)
MODES = {"quick", "standard", "deep", "ultradeep"}
HEADING = re.compile(r"^ {0,3}##[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$", re.M)
CITATION = re.compile(r"(?<![\\!])\[(\d+)\](?![(:])")
ENTRY = re.compile(r"^ {0,3}\[(\d+)\][ \t]+(.+)$", re.M)
METADATA = re.compile(r'^(.+?)\s+\(([^()]+)\)\.\s+"([^"]+)"\.', re.S)


@dataclass
class Source:
    number: int
    text: str
    author: str = ""
    published: str = ""
    title: str = ""
    url: str = ""
    accessed: str = ""


@dataclass
class Report:
    sections: list[tuple[str, str]]
    body: str
    sources: list[Source]
    errors: list[str] = field(default_factory=list)


def prose_only(text: str) -> str:
    """Mask comments and code blocks; deliberately not a general Markdown parser."""
    text = re.sub(r"<!--.*?(?:-->|\Z)", "", text, flags=re.S)
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            lines.append("")
        elif marker:
            fence = marker[1]
            lines.append("")
        elif line.startswith(("    ", "\t")):
            lines.append("")
        else:
            lines.append(line)
    return "\n".join(lines)


def without_inline_code(text: str) -> str:
    return re.sub(r"(`+)(?!`)(.*?)(?<!`)\1(?!`)", "", text, flags=re.S)


def parse_report(text: str) -> Report:
    text = prose_only(text)
    headings = list(HEADING.finditer(text))
    sections = [(m[1].strip(), text[m.end():headings[i + 1].start() if i + 1 < len(headings) else len(text)])
                for i, m in enumerate(headings)]
    body = text[:headings[0].start()] if headings else text
    sources, errors = [], []
    for title, content in sections:
        if title.casefold() != "bibliography":
            body += "\n" + content
            continue
        matches = list(ENTRY.finditer(content))
        if content[:matches[0].start() if matches else len(content)].strip():
            errors.append("Bibliography must contain numbered entries, not introductory prose.")
        for i, match in enumerate(matches):
            raw = content[match.start():matches[i + 1].start() if i + 1 < len(matches) else len(content)]
            raw = re.sub(r"^\s*\[\d+\]\s+", "", raw).strip()
            source = Source(int(match[1]), raw)
            metadata = METADATA.match(raw)
            if metadata:
                source.author, source.published, source.title = (v.strip() for v in metadata.groups())
            url = re.search(r"https?://[^\s<>\"]+", raw)
            source.url = url[0].rstrip(".,;") if url else ""
            accessed = re.search(r"\bAccessed:\s*(\d{4}-\d{2}-\d{2})(?![\dT])", raw)
            source.accessed = accessed[1] if accessed else ""
            sources.append(source)
    return Report(sections, body, sources, errors)


def publication_date(value: str) -> date | None:
    """Accept unknown dates, years, ISO dates, and ISO timestamps (normalize to UTC)."""
    if value == "n.d.":
        return None
    if re.fullmatch(r"\d{4}", value):
        return date(int(value), 1, 1)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return date.fromisoformat(value)
    if not re.match(r"\d{4}-\d{2}-\d{2}T", value):
        raise ValueError("Use an ISO date, timestamp, year, or n.d.")
    timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timestamp.tzinfo:
        timestamp = timestamp.astimezone(timezone.utc)
    return timestamp.date()


def valid_url(url: str) -> bool:
    try:
        parts = urlsplit(url)
        return (parts.scheme in {"http", "https"} and bool(parts.hostname)
                and not parts.username and not parts.password and not re.search(r"\s", url)
                and (parts.port is None or 0 < parts.port < 65536))
    except ValueError:
        return False


def check_sources(report: Report, today: date | None = None) -> tuple[list[str], list[str]]:
    today = today or datetime.now(timezone.utc).date()
    errors, warnings = list(report.errors), []
    counts = Counter(s.number for s in report.sources)
    if not counts:
        errors.append("No bibliography entries found.")
    for number, count in counts.items():
        if count > 1:
            errors.append(f"Duplicate bibliography ID [{number}].")
    for source in report.sources:
        label = f"[{source.number}]"
        if source.number < 1:
            errors.append(f"{label} Citation IDs must be positive integers.")
        if not source.author or not source.title:
            errors.append(f'{label} Expected: Author (date). "Title". <URL> Accessed: YYYY-MM-DD.')
        if not valid_url(source.url):
            errors.append(f"{label} Missing or invalid HTTP(S) source URL.")
        try:
            published = publication_date(source.published)
            if published and published > today:
                warnings.append(f"{label} Publication date is in the future; check forthcoming/version metadata.")
        except ValueError:
            errors.append(f"{label} Invalid publication date; use ISO date/timestamp, year, or n.d.")
        try:
            if date.fromisoformat(source.accessed) > today:
                errors.append(f"{label} Access date cannot be in the future.")
        except ValueError:
            errors.append(f"{label} Missing or invalid Accessed: YYYY-MM-DD date.")
    return errors, warnings


def validate_report(text: str, today: date | None = None) -> tuple[list[str], list[str]]:
    report = parse_report(text)
    errors, warnings = check_sources(report, today)
    titles = Counter(title.casefold() for title, _ in report.sections)
    for title in SECTIONS:
        if titles[title.casefold()] != 1:
            errors.append(f"Expected exactly one level-two '{title}' section.")
    for title, content in report.sections:
        if title.casefold() in {s.casefold() for s in SECTIONS}:
            visible = without_inline_code(content)
            visible = re.sub(r"^\s*(?:#{1,6}\s+.*|[-*_]{3,})\s*$", "", visible, flags=re.M)
            if not re.search(r"\w", visible):
                errors.append(f"Empty section: {title}.")
    body = without_inline_code(report.body)
    modes = re.findall(r"^Mode:\s*(\w+)\s*$", body, re.M | re.I)
    if len(modes) != 1 or modes[0].casefold() not in MODES:
        errors.append("Include exactly one 'Mode: quick|standard|deep|ultradeep' line.")
    cited = {int(n) for n in CITATION.findall(body)}
    listed = {s.number for s in report.sources}
    if not cited:
        errors.append("No numeric citations found in report prose outside the bibliography.")
    for number in sorted(cited - listed):
        errors.append(f"Citation [{number}] has no bibliography entry.")
    for number in sorted(listed - cited):
        errors.append(f"Bibliography entry [{number}] is never cited in report prose.")
    if re.search(r"\{\{[^}]+\}\}", prose_only(text)):
        errors.append("Unfilled template placeholder: {{...}}.")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, nargs="?")
    parser.add_argument("--report", "-r", type=Path, dest="report_option", help="Alias for the positional report path.")
    args = parser.parse_args()
    if (args.report is None) == (args.report_option is None):
        parser.error("Provide one report path, positionally or with --report/-r.")
    report_path = args.report or args.report_option
    try:
        errors, warnings = validate_report(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: Cannot read report: {exc}")
        return 2
    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")
    if not errors:
        print("Structure checks passed. Claim support still requires source review.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
