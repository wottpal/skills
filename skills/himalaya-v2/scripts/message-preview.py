#!/usr/bin/env python3
"""Preview parsed Himalaya message JSON without fetching links or attachments."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
import re
import sys
from typing import Any


class BodyHTMLParser(HTMLParser):
    """Render visible HTML text and collect anchor destinations, without IO."""

    BLOCKS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "blockquote", "pre"}
    HIDDEN = {"head", "script", "style", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.chunks: list[str] = []
        self.links: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.HIDDEN:
            self.hidden += 1
        if self.hidden:
            return
        if tag in self.BLOCKS:
            self.chunks.append("\n")
        if tag in {"td", "th"}:
            self.chunks.append(" ")
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value and value.startswith(("https://", "http://")):
                    self.links.append(value)

    def handle_endtag(self, tag):
        if tag in self.HIDDEN and self.hidden:
            self.hidden -= 1
        elif not self.hidden and tag in self.BLOCKS:
            self.chunks.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.chunks.append(data)

    def text(self) -> str:
        text = re.sub(r"[^\S\n]+", " ", "".join(self.chunks))
        text = "\n".join(line.strip() for line in text.splitlines())
        return re.sub(r"\n{3,}", "\n\n", text).strip()


def strip_html(value: str) -> str:
    parser = BodyHTMLParser()
    parser.feed(value)
    parser.close()
    return parser.text()


def extract_bodies(message: Any) -> tuple[list[str], list[str]]:
    """Resolve mail-parser's zero-based body indexes; never walk every MIME part."""
    if not isinstance(message, dict) or not any(k in message for k in ("text_body", "html_body")):
        raise ValueError("Expected parsed message JSON from 'message read --json' without --raw.")
    parts = message.get("parts", [])
    attachments = message.get("attachments", [])
    if not isinstance(parts, list) or not isinstance(attachments, list):
        raise ValueError("Expected parts and attachments arrays.")
    results: dict[str, list[str]] = {"Text": [], "Html": []}
    for field, kind in (("text_body", "Text"), ("html_body", "Html")):
        values = message.get(field, [])
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list):
            raise ValueError(f"Expected {field} to be a string or array.")
        for value in values:
            if type(value) is int:
                if value < 0 or value >= len(parts) or not isinstance(parts[value], dict):
                    raise ValueError(f"Invalid {field} MIME part index: {value}.")
                if value in attachments:
                    continue
                body = parts[value].get("body")
                if not isinstance(body, dict):
                    raise ValueError(f"Missing body for MIME part {value}.")
                # mail-parser may reuse an HTML part as a text-body fallback.
                body_kind = next((k for k in ("Text", "Html") if k in body), None)
                if body_kind is None or not isinstance(body[body_kind], str):
                    raise ValueError(f"Expected Text/Html content for MIME part {value}.")
                results[body_kind].append(body[body_kind])
            elif isinstance(value, str):
                results[kind].append(value)
            else:
                raise ValueError(f"Unsupported value in {field}; expected a part index or string.")
    return (list(dict.fromkeys(results["Text"])), list(dict.fromkeys(results["Html"])))


def body_candidates(message: dict[str, Any]) -> list[str]:
    plain, rich = extract_bodies(message)
    texts = [value.strip() for value in plain if value.strip()]
    if not texts:
        texts = [strip_html(value) for value in rich]
    return list(dict.fromkeys(text for text in texts if text))


def extract_urls(message: dict[str, Any]) -> list[str]:
    plain, rich = extract_bodies(message)
    urls: list[str] = []
    for value in rich:
        parser = BodyHTMLParser()
        parser.feed(value)
        parser.close()
        plain.append(parser.text())
        urls.extend(parser.links)
    for value in plain:
        for url in re.findall(r"https?://[^\s<>\"']+", value):
            url = url.rstrip(".,;!")
            while url.endswith(")") and url.count(")") > url.count("("):
                url = url[:-1]
            urls.append(url)
    return list(dict.fromkeys(urls))


def nonnegative(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("--chars must be nonnegative (0 means unlimited).")
    return number


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chars", type=nonnegative, default=3000, help="Maximum body characters; 0 means unlimited.")
    parser.add_argument("--urls", action="store_true", help="List HTTP(S) links from body text and HTML anchors, even beyond the preview limit.")
    args = parser.parse_args()

    try:
        message = json.load(sys.stdin)
        text = "\n\n".join(body_candidates(message))
        urls = extract_urls(message) if args.urls else []
    except (ValueError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not text:
        print("No readable text or HTML body found.", file=sys.stderr)
        return 1
    if args.chars > 0:
        text = text[: args.chars]

    print(text)

    if urls:
        print("\nURLS:")
        print("\n".join(urls))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
